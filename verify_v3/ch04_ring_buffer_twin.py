#!/usr/bin/env python3
"""verify_v3/ch04_ring_buffer_twin.py
Python bit- and cycle-exact twin for ch04_ring_buffer.
Models the 1024x16 circular ring buffer, frame slicing (638 samples),
hop stepping (160 samples), and overlap management (478 samples).

Generates:
  - verify_v3/tb_ch04_ring_buffer_stim.txt
  - verify_v3/tb_ch04_ring_buffer_expected.txt
"""

import sys
import os
import random

FRAME_LEN = 638
HOP_LEN = 160
ADDR_WIDTH = 10
BUFFER_DEPTH = 1 << ADDR_WIDTH  # 1024
SAFE_LIMIT = BUFFER_DEPTH - 4   # 1020


class RingBufferTwin:
    def __init__(self, registered_output=True):
        self.registered_output = registered_output
        self.ram = [0] * BUFFER_DEPTH
        self.wr_ptr = 0
        self.rd_base = 0
        self.sample_count = 0
        self.frame_idx = 0

        # Port B read pipeline
        self.ram_q = 0
        self.rd_en_d1 = False
        self.rd_valid_r = False
        self.rd_data_r = 0

    def get_combinational_outputs(self):
        sink_ready = 1 if self.sample_count < SAFE_LIMIT else 0
        frame_ready = 1 if self.sample_count >= FRAME_LEN else 0
        return sink_ready, frame_ready

    def get_registered_outputs(self):
        if self.registered_output:
            rd_valid = 1 if self.rd_valid_r else 0
            rd_data = self.rd_data_r
        else:
            rd_valid = 1 if self.rd_en_d1 else 0
            rd_data = self.ram_q

        return (
            self.frame_idx & 0xFFFF,
            self.rd_base & 0x3FF,
            self.sample_count & 0x7FF,
            rd_valid,
            rd_data & 0xFFFF,  # 16-bit unsigned hex representation for comparison
        )

    def clock_edge(self, rst_n, clr, sink_valid, sink_data, frame_step, rd_en, rd_sample_idx):
        if not rst_n or clr:
            self.wr_ptr = 0
            self.rd_base = 0
            self.sample_count = 0
            self.frame_idx = 0
            self.ram_q = 0
            self.rd_en_d1 = False
            self.rd_valid_r = False
            self.rd_data_r = 0
            return

        sink_ready, frame_ready = self.get_combinational_outputs()
        write_fire = (sink_valid == 1) and (sink_ready == 1)
        step_fire = (frame_step == 1) and (frame_ready == 1)

        # Port A write
        if write_fire:
            # Mask to signed 16-bit
            s16 = ((sink_data + 32768) % 65536) - 32768
            self.ram[self.wr_ptr] = s16

        # Port B read
        rd_phys_addr = (self.rd_base + rd_sample_idx) & 0x3FF
        next_ram_q = self.ram[rd_phys_addr] if rd_en else self.ram_q

        # Read output registers
        next_rd_en_d1 = (rd_en == 1)
        next_rd_valid_r = self.rd_en_d1
        next_rd_data_r = self.ram_q if self.rd_en_d1 else self.rd_data_r

        # Pointer and counter updates
        next_wr_ptr = (self.wr_ptr + 1) & 0x3FF if write_fire else self.wr_ptr
        next_rd_base = (self.rd_base + HOP_LEN) & 0x3FF if step_fire else self.rd_base
        next_frame_idx = (self.frame_idx + 1) & 0xFFFF if step_fire else self.frame_idx

        # Atomic sample count update
        if write_fire and step_fire:
            next_sample_count = self.sample_count + 1 - HOP_LEN
        elif write_fire:
            next_sample_count = self.sample_count + 1
        elif step_fire:
            next_sample_count = self.sample_count - HOP_LEN
        else:
            next_sample_count = self.sample_count

        # Latch new state
        self.wr_ptr = next_wr_ptr
        self.rd_base = next_rd_base
        self.frame_idx = next_frame_idx
        self.sample_count = next_sample_count
        self.ram_q = next_ram_q
        self.rd_en_d1 = next_rd_en_d1
        self.rd_valid_r = next_rd_valid_r
        self.rd_data_r = next_rd_data_r


def generate_vectors(num_cycles=3500, seed=42):
    random.seed(seed)
    twin = RingBufferTwin(registered_output=True)

    stim_lines = []
    exp_lines = []

    # Current sample value generator
    sample_val = 100
    current_read_idx = 0
    reading_frame = False

    for cyc in range(num_cycles):
        if cyc < 5:
            # Active reset
            rst_n = 0
            clr = 0
            sink_valid = 0
            sink_data = 0
            frame_step = 0
            rd_en = 0
            rd_sample_idx = 0
        elif cyc == 5:
            # Release reset
            rst_n = 1
            clr = 0
            sink_valid = 0
            sink_data = 0
            frame_step = 0
            rd_en = 0
            rd_sample_idx = 0
        else:
            rst_n = 1
            clr = 0

            # Sink valid with occasional bubbles (85% valid)
            sink_valid = 1 if random.random() < 0.85 else 0
            sink_data = sample_val if sink_valid else 0
            if sink_valid and (twin.sample_count < SAFE_LIMIT):
                # Update next sample with interesting patterns (sawtooth / sine-like)
                sample_val = (sample_val + 37) % 32000 - 16000

            # Frame read state machine
            c_sink_ready, c_frame_ready = twin.get_combinational_outputs()

            if c_frame_ready and not reading_frame:
                # Start reading new frame
                reading_frame = True
                current_read_idx = 0

            if reading_frame:
                rd_en = 1 if random.random() < 0.90 else 0
                rd_sample_idx = current_read_idx
                if rd_en:
                    current_read_idx += 1
                    if current_read_idx >= FRAME_LEN:
                        # Finished reading all 638 samples of frame
                        reading_frame = False
                        frame_step = 1
                    else:
                        frame_step = 0
                else:
                    frame_step = 0
            else:
                rd_en = 0
                rd_sample_idx = 0
                frame_step = 0

        # 1. Evaluate combinational outputs before posedge
        c_sink_ready, c_frame_ready = twin.get_combinational_outputs()

        # Format stim line:
        # rst_n clr sink_valid sink_data frame_step rd_en rd_sample_idx
        s_data_u16 = sink_data & 0xFFFF
        stim_line = f"{rst_n} {clr} {sink_valid} {s_data_u16:04X} {frame_step} {rd_en} {rd_sample_idx:03X}"
        stim_lines.append(stim_line)

        # 2. Advance clock edge
        twin.clock_edge(rst_n, clr, sink_valid, sink_data, frame_step, rd_en, rd_sample_idx)

        # 3. Evaluate registered outputs after posedge
        f_idx, r_base, s_count, r_valid, r_data_u16 = twin.get_registered_outputs()

        # Format exp line:
        # c_sink_ready c_frame_ready f_idx r_base s_count r_valid r_data
        exp_line = f"{c_sink_ready} {c_frame_ready} {f_idx:04X} {r_base:03X} {s_count:03X} {r_valid} {r_data_u16:04X}"
        exp_lines.append(exp_line)

    return stim_lines, exp_lines


def main():
    print("=" * 70)
    print("CH04 RING BUFFER TWIN: VECTOR GENERATION")
    print("=" * 70)

    stim_lines, exp_lines = generate_vectors(num_cycles=3500, seed=12345)

    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    stim_path = os.path.join(repo_dir, "verify_v3", "tb_ch04_ring_buffer_stim.txt")
    exp_path = os.path.join(repo_dir, "verify_v3", "tb_ch04_ring_buffer_expected.txt")

    with open(stim_path, "w", newline="\n") as f:
        f.write("\n".join(stim_lines) + "\n")

    with open(exp_path, "w", newline="\n") as f:
        f.write("\n".join(exp_lines) + "\n")

    print(f"Generated {len(stim_lines)} stimulus vectors -> {stim_path}")
    print(f"Generated {len(exp_lines)} expected vectors -> {exp_path}")

    # Inspect first few lines
    print("\nStimulus Header (first 5 lines):")
    for l in stim_lines[:5]:
        print("  " + l)

    print("\nExpected Header (first 5 lines):")
    for l in exp_lines[:5]:
        print("  " + l)

    # Inspect lines around frame 0 ready (around cycle 750)
    print("\nTrace around Frame 0 completion (cycles 750..755):")
    for i in range(750, 756):
        print(f"  Cycle {i:4d}: STIM=[{stim_lines[i]}] EXP=[{exp_lines[i]}]")

    print("=" * 70)
    print("Status: SUCCESS - Vectors ready for Icarus Verilog testbench.")
    print("=" * 70)


if __name__ == "__main__":
    main()
