#!/usr/bin/env python3
"""verify_v3/ch05_mean_twin.py
Cycle-accurate, bit-exact Python twin and vector generator for Chapter 5:
  1. LocalMeanTwin: models rtl/v3/ch05_local_mean.v cycle by cycle.
     - Generates tb_ch05_mean_stim.txt and tb_ch05_mean_expected.txt.
     - Covers >= 200 frame transactions, including clean/noisy golden audio,
       full-scale positive (+32767), full-scale negative (-32768), alternating extremes,
       and subtraction verification (d = x - mean, 17-bit signed).
  2. DCBlockerTwin: models rtl/v3/ch05_dc_blocker.v cycle by cycle.
     - Generates tb_ch05_dc_blocker_stim.txt and tb_ch05_dc_blocker_expected.txt.
     - Covers >= 500 cycles with random backpressure, bypass toggling, and DC steps.
"""
import sys
import os
import math
import numpy as np

# Add golden_v2 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'golden_v2'))
import constants as K
import scipy.io.wavfile as wav
from frames import frame_grid, window_start0, mean_start0


class LocalMeanTwin:
    """Cycle-accurate model of rtl/v3/ch05_local_mean.v."""
    def __init__(self):
        self.state = 0 # 0: IDLE, 1: ISSUE, 2: WAIT_RD, 3: MULT1, 4: MULT2, 5: DONE
        self.busy = 0
        self.mean_valid = 0
        self.mean_out = 0
        self.rd_en = 0
        self.rd_sample_idx = 0
        self.diff_valid_out = 0
        self.diff_data_out = 0

        # Internal registers
        self.issue_cnt = 0
        self.collect_cnt = 0
        self.acc = 213
        self.mult_a_r = 0
        self.mult_b_r = 0
        self.mult_prod_r = 0

    def step(self, start, rd_valid, rd_data, sub_valid_in, sub_data_in):
        # 1. Combinational / Registered Subtraction update
        if sub_valid_in:
            diff = sub_data_in - self.mean_out
            next_diff_valid = 1
            next_diff_data = diff
        else:
            next_diff_valid = 0
            next_diff_data = 0

        # 2. Sequential FSM state update
        next_state = self.state
        next_busy = self.busy
        next_mean_valid = 0
        next_mean_out = self.mean_out
        next_rd_en = 0
        next_rd_sample_idx = self.rd_sample_idx
        next_issue_cnt = self.issue_cnt
        next_collect_cnt = self.collect_cnt
        next_acc = self.acc
        next_mult_a_r = self.mult_a_r
        next_mult_b_r = self.mult_b_r
        next_mult_prod_r = self.mult_prod_r

        if self.state == 0:  # STATE_IDLE
            next_busy = 0
            next_rd_en = 0
            if start:
                next_busy = 1
                next_mean_valid = 0
                next_issue_cnt = 0
                next_collect_cnt = 0
                next_acc = 213
                next_rd_en = 1
                next_rd_sample_idx = K.MEAN_OFFSET  # 106
                next_state = 1  # STATE_ISSUE

        elif self.state == 1:  # STATE_ISSUE
            if self.issue_cnt < K.MEAN_SPAN - 1:
                next_issue_cnt = self.issue_cnt + 1
                next_rd_sample_idx = K.MEAN_OFFSET + next_issue_cnt
                next_rd_en = 1
            else:
                next_rd_en = 0

            if rd_valid:
                u16_sample = (rd_data & 0xFFFF) ^ 0x8000
                next_acc = self.acc + u16_sample
                next_collect_cnt = self.collect_cnt + 1
                if self.collect_cnt == K.MEAN_SPAN - 1:
                    next_state = 3  # STATE_MULT1
            elif self.issue_cnt == K.MEAN_SPAN - 1:
                next_state = 2  # STATE_WAIT_RD

        elif self.state == 2:  # STATE_WAIT_RD
            next_rd_en = 0
            if rd_valid:
                u16_sample = (rd_data & 0xFFFF) ^ 0x8000
                next_acc = self.acc + u16_sample
                next_collect_cnt = self.collect_cnt + 1
                if self.collect_cnt == K.MEAN_SPAN - 1:
                    next_state = 3  # STATE_MULT1

        elif self.state == 3:  # STATE_MULT1
            next_mult_a_r = self.acc
            next_mult_b_r = K.M_MEAN
            next_state = 4  # STATE_MULT2

        elif self.state == 4:  # STATE_MULT2
            next_mult_prod_r = self.mult_a_r * self.mult_b_r
            next_state = 5  # STATE_DONE

        elif self.state == 5:  # STATE_DONE
            # Mean extraction
            q_biased = (self.mult_prod_r >> 32) & 0xFFFF
            # Subtract 32768 to restore signed int16
            mean_signed = q_biased - 32768
            next_mean_out = mean_signed
            next_mean_valid = 1
            next_busy = 0
            next_state = 0  # STATE_IDLE

        # Latch registered state
        self.state = next_state
        self.busy = next_busy
        self.mean_valid = next_mean_valid
        self.mean_out = next_mean_out
        self.rd_en = next_rd_en
        self.rd_sample_idx = next_rd_sample_idx
        self.issue_cnt = next_issue_cnt
        self.collect_cnt = next_collect_cnt
        self.acc = next_acc
        self.mult_a_r = next_mult_a_r
        self.mult_b_r = next_mult_b_r
        self.mult_prod_r = next_mult_prod_r
        self.diff_valid_out = next_diff_valid
        self.diff_data_out = next_diff_data

        return (self.busy, self.mean_valid, self.mean_out,
                self.rd_en, self.rd_sample_idx,
                self.diff_valid_out, self.diff_data_out)


class DCBlockerTwin:
    """Cycle-accurate model of rtl/v3/ch05_dc_blocker.v."""
    def __init__(self):
        self.x_prev = 0
        self.w_acc = 0  # 36-bit signed Q20.16
        self.source_valid = 0
        self.source_data = 0

    def step(self, bypass, sink_valid, sink_data, source_ready):
        sink_ready = source_ready or not self.source_valid
        next_source_valid = self.source_valid
        next_source_data = self.source_data

        if sink_ready:
            if sink_valid:
                next_source_valid = 1
                if bypass:
                    next_source_data = sink_data
                else:
                    dx = sink_data - self.x_prev
                    self.x_prev = sink_data
                    # Arithmetic shift right by 8
                    w_feedback = self.w_acc - (self.w_acc >> 8)
                    dx_scaled = dx << 16
                    self.w_acc = w_feedback + dx_scaled
                    # Round and saturate
                    w_rounded = self.w_acc + 0x8000
                    y_cand = w_rounded >> 16
                    if y_cand > 32767:
                        next_source_data = 32767
                    elif y_cand < -32768:
                        next_source_data = -32768
                    else:
                        next_source_data = y_cand
            else:
                next_source_valid = 0

        self.source_valid = next_source_valid
        self.source_data = next_source_data
        return sink_ready, self.source_valid, self.source_data


def generate_local_mean_vectors():
    print("Generating Local Mean vectors (ch05_local_mean)...")
    golden_dir = os.path.join(os.path.dirname(__file__), '..', 'golden_v2')
    wav_path = os.path.join(golden_dir, 'synth_glide_vuv_16k.wav')
    fs, data = wav.read(wav_path)
    t1, times, lefts = frame_grid(len(data))

    # Test frames to run:
    # 1. 200 real frames from synthetic audio
    # 2. Stress frame: all +32767
    # 3. Stress frame: all -32768
    # 4. Stress frame: alternating +32767, -32768
    # 5. Stress frame: silence all 0
    # 6. Stress frame: DC 1000 square wave
    frames = []
    for left in lefts[:200]:
        w_start = window_start0(left)
        m_start = mean_start0(left)
        # Ring buffer simulation array for this frame (length 638)
        frame_samples = data[w_start : w_start + K.NSAMP_WINDOW].tolist()
        frames.append(frame_samples)

    # Add corner cases
    frames.append([32767] * K.NSAMP_WINDOW)
    frames.append([-32768] * K.NSAMP_WINDOW)
    frames.append([32767 if i % 2 == 0 else -32768 for i in range(K.NSAMP_WINDOW)])
    frames.append([0] * K.NSAMP_WINDOW)
    frames.append([2000 if (i // 4) % 2 == 0 else 0 for i in range(K.NSAMP_WINDOW)])

    print(f"Total test frames to simulate: {len(frames)}")

    twin = LocalMeanTwin()
    stim_lines = []
    exp_lines = []

    # Simple ring buffer model with 1 cycle read latency
    rb_ram = [0] * K.NSAMP_WINDOW
    rd_en_d1 = 0
    rd_idx_d1 = 0

    total_cycles = 0

    for f_idx, frame in enumerate(frames):
        rb_ram = list(frame)
        # Frame start pulse
        # Cycle 0: start = 1
        for cyc in range(K.MEAN_SPAN + 10):
            start = 1 if cyc == 0 else 0
            
            # RAM read response (1 cycle latency from previous cycle's rd_en)
            if rd_en_d1:
                rd_valid = 1
                rd_data = rb_ram[rd_idx_d1]
            else:
                rd_valid = 0
                rd_data = 0

            # Subtraction stimulus (feed 2 samples during DONE or IDLE)
            if twin.mean_valid or twin.state == 0:
                sub_valid_in = 1 if cyc >= K.MEAN_SPAN + 4 else 0
                sub_data_in = rb_ram[(cyc * 17) % K.NSAMP_WINDOW] if sub_valid_in else 0
            else:
                sub_valid_in = 0
                sub_data_in = 0

            # Step twin
            (busy, mean_valid, mean_out,
             rd_en, rd_sample_idx,
             diff_valid_out, diff_data_out) = twin.step(start, rd_valid, rd_data, sub_valid_in, sub_data_in)

            # Update RAM delay registers
            rd_en_d1 = rd_en
            rd_idx_d1 = rd_sample_idx

            # Record stimulus:
            # rst_n start rd_valid rd_data sub_valid_in sub_data_in
            # Format: %d %d %d %04x %d %04x
            stim_lines.append(f"1 {start} {rd_valid} {rd_data & 0xFFFF:04X} {sub_valid_in} {sub_data_in & 0xFFFF:04X}\n")

            # Record expected:
            # busy mean_valid mean_out rd_en rd_sample_idx diff_valid_out diff_data_out
            # Format: %d %d %04x %d %04x %d %05x
            exp_lines.append(f"{busy} {mean_valid} {mean_out & 0xFFFF:04X} {rd_en} {rd_sample_idx & 0x3FF:03X} {diff_valid_out} {diff_data_out & 0x1FFFF:05X}\n")

            total_cycles += 1

            if cyc > K.MEAN_SPAN + 6 and not busy:
                # Check bit-exactness of computed mean with golden_v2 formula
                expected_mean = (sum(rb_ram[K.MEAN_OFFSET : K.MEAN_OFFSET + K.MEAN_SPAN]) + 213) // K.MEAN_SPAN
                assert mean_out == expected_mean, f"Frame {f_idx}: mean {mean_out} != expected {expected_mean}"
                break

    stim_path = os.path.join(os.path.dirname(__file__), 'tb_ch05_mean_stim.txt')
    exp_path = os.path.join(os.path.dirname(__file__), 'tb_ch05_mean_expected.txt')

    with open(stim_path, 'w') as f:
        f.writelines(stim_lines)
    with open(exp_path, 'w') as f:
        f.writelines(exp_lines)

    print(f"Generated {len(stim_lines)} stimulus cycles for {len(frames)} frames -> {stim_path}")
    print(f"Generated {len(exp_lines)} expected cycles -> {exp_path}")


def generate_dc_blocker_vectors():
    print("\nGenerating DC-Blocker vectors (ch05_dc_blocker)...")
    np.random.seed(12345)
    N_CYCLES = 1000

    twin = DCBlockerTwin()
    stim_lines = []
    exp_lines = []

    # Create interesting stimuli:
    # 0..99: DC step of +2000
    # 100..299: Sine wave (150 Hz) + DC 1500
    # 300..499: Extreme jumps (+32767 to -32768)
    # 500..699: Bypass mode active
    # 700..999: White noise
    t = np.arange(N_CYCLES) / 16000.0
    sine = (10000 * np.sin(2 * np.pi * 150 * t)).astype(int)

    for cyc in range(N_CYCLES):
        if cyc < 100:
            bypass = 0
            sink_data = 2000
        elif cyc < 300:
            bypass = 0
            sink_data = int(sine[cyc] + 1500)
        elif cyc < 500:
            bypass = 0
            sink_data = 32767 if (cyc // 10) % 2 == 0 else -32768
        elif cyc < 700:
            bypass = 1  # Testing bypass mode
            sink_data = int(sine[cyc])
        else:
            bypass = 0
            sink_data = int(np.random.randint(-15000, 15000))

        # Random handshake
        sink_valid = 1 if np.random.rand() > 0.15 else 0
        source_ready = 1 if np.random.rand() > 0.20 else 0

        # Step twin
        sink_ready, source_valid, source_data = twin.step(bypass, sink_valid, sink_data, source_ready)

        # Stimulus format: rst_n bypass sink_valid sink_data source_ready
        stim_lines.append(f"1 {bypass} {sink_valid} {sink_data & 0xFFFF:04X} {source_ready}\n")

        # Expected format: sink_ready source_valid source_data
        exp_lines.append(f"{sink_ready} {source_valid} {source_data & 0xFFFF:04X}\n")

    stim_path = os.path.join(os.path.dirname(__file__), 'tb_ch05_dc_blocker_stim.txt')
    exp_path = os.path.join(os.path.dirname(__file__), 'tb_ch05_dc_blocker_expected.txt')

    with open(stim_path, 'w') as f:
        f.writelines(stim_lines)
    with open(exp_path, 'w') as f:
        f.writelines(exp_lines)

    print(f"Generated {len(stim_lines)} DC-blocker stimulus cycles -> {stim_path}")
    print(f"Generated {len(exp_lines)} DC-blocker expected cycles -> {exp_path}")


def main():
    generate_local_mean_vectors()
    generate_dc_blocker_vectors()
    print("\nAll Chapter 5 stimulus and expected vector files generated successfully!")


if __name__ == "__main__":
    main()
