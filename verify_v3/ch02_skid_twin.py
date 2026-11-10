#!/usr/bin/env python3
"""
verify_v3/ch02_skid_twin.py

Cycle-accurate Python twin and test vector generator for rtl/v3/ch02_skid_buffer.v:
- Models two-stage registered decoupling:
  * Forward path (data & valid) fully registered.
  * Backward path (ready) driven by local state (no combinational loop).
- Maintains 100% throughput (1 word/cycle when not stalled).
- Absorbs up to 1 word of in-flight data when downstream stalls.
- Returns output signals observed AFTER posedge clk, matching Verilog testbench.
- Generates >= 500 test cycles covering:
  1. Empty to full throughput burst.
  2. Single-cycle stall, multi-cycle stall.
  3. Back-to-back stalls and releases.
  4. Pseudo-random valid and ready backpressure.
- Writes:
  * verify_v3/tb_ch02_skid_stim.txt (rst_n, s_valid, s_data, m_ready)
  * verify_v3/tb_ch02_skid_expected.txt (c, rst_n, s_valid, s_data, m_ready, s_ready, m_valid, m_data, skid_valid)
"""

import os
import random

class SkidBufferTwin:
    def __init__(self, data_width=16):
        self.width = data_width
        self.mask = (1 << data_width) - 1
        self.reset()
        
    def reset(self):
        self.main_data = 0
        self.main_valid = 0
        self.skid_data = 0
        self.skid_valid = 0
        
    def step(self, rst_n, s_valid, s_data, m_ready):
        """
        Simulate one clock edge of rtl/v3/ch02_skid_buffer.v.
        Returns (s_ready, m_valid, m_data, skid_valid) observed AFTER posedge clk.
        """
        if not rst_n:
            self.reset()
            # In reset: main_valid=0, skid_valid=0 -> s_ready=1
            return (1, 0, 0, 0)
            
        s_data = s_data & self.mask
        
        # State before clock edge determines handshakes
        s_ready_before = 1 if (self.skid_valid == 0) else 0
        m_valid_before = self.main_valid
        
        s_handshake = (s_valid == 1) and (s_ready_before == 1)
        m_handshake = (m_valid_before == 1) and (m_ready == 1)
        
        next_main_data = self.main_data
        next_main_valid = self.main_valid
        next_skid_data = self.skid_data
        next_skid_valid = self.skid_valid
        
        if m_handshake:
            if self.skid_valid:
                next_main_data = self.skid_data
                next_main_valid = 1
                next_skid_valid = 0
            elif s_handshake:
                next_main_data = s_data
                next_main_valid = 1
            else:
                next_main_valid = 0
        else:
            if s_handshake:
                if self.main_valid:
                    next_skid_data = s_data
                    next_skid_valid = 1
                else:
                    next_main_data = s_data
                    next_main_valid = 1
                    
        # Register update on clock edge
        self.main_data = next_main_data
        self.main_valid = next_main_valid
        self.skid_data = next_skid_data
        self.skid_valid = next_skid_valid
        
        # Output signals after clock edge
        s_ready_after = 1 if (self.skid_valid == 0) else 0
        m_valid_after = self.main_valid
        m_data_after = self.main_data
        skid_valid_after = self.skid_valid
        
        return (s_ready_after, m_valid_after, m_data_after, skid_valid_after)

def run_simulation(num_cycles=600, seed=42):
    random.seed(seed)
    twin = SkidBufferTwin(data_width=16)
    
    stim_lines = []
    exp_lines = []
    
    sent_stream = []
    received_stream = []
    
    sample_counter = 1
    
    for c in range(num_cycles):
        if c < 5:
            rst_n = 0
            s_valid = 0
            s_data = 0
            m_ready = 0
        elif c < 40:
            rst_n = 1
            s_valid = 1
            s_data = sample_counter
            m_ready = 1
        elif c < 100:
            rst_n = 1
            s_valid = 1
            s_data = sample_counter
            m_ready = 0 if (c % 3 == 0) else 1
        elif c < 180:
            rst_n = 1
            s_valid = 1 if (c % 2 == 0) else 0
            s_data = sample_counter
            m_ready = 0 if (120 <= c <= 135 or 150 <= c <= 165) else 1
        elif c < 550:
            rst_n = 1
            s_valid = 1 if (random.random() > 0.3) else 0
            s_data = sample_counter
            m_ready = 1 if (random.random() > 0.4) else 0
        else:
            rst_n = 1
            s_valid = 0
            s_data = 0
            m_ready = 1
            
        # Handshakes in this cycle before the edge
        s_rdy_before = 1 if (twin.skid_valid == 0) else 0
        m_vld_before = twin.main_valid
        m_dat_before = twin.main_data
        
        if rst_n and s_valid and s_rdy_before:
            sent_stream.append(s_data)
            sample_counter = (sample_counter + 1) & 0xFFFF
            if sample_counter == 0:
                sample_counter = 1
                
        if rst_n and m_vld_before and m_ready:
            received_stream.append(m_dat_before)
            
        s_rdy, m_vld, m_dat, sk_vld = twin.step(rst_n, s_valid, s_data, m_ready)
            
        stim_lines.append(f"{rst_n} {s_valid} {s_data:04x} {m_ready}\n")
        exp_lines.append(f"{c} {rst_n} {s_valid} {s_data:04x} {m_ready} {s_rdy} {m_vld} {m_dat:04x} {sk_vld}\n")
        
    print(f"Simulation completed {num_cycles} cycles.")
    print(f"Total samples sent by upstream: {len(sent_stream)}")
    print(f"Total samples received by downstream: {len(received_stream)}")
    
    assert sent_stream == received_stream, (
        f"Stream mismatch! Sent {len(sent_stream)}, received {len(received_stream)}\n"
        f"First diff: {[ (i, s, r) for i, (s, r) in enumerate(zip(sent_stream, received_stream)) if s != r ][:5]}"
    )
    print("PASS: Sent stream exactly equals received stream (0 loss, 0 duplication, 100% order preserved).")
    
    out_dir = "." if os.path.basename(os.getcwd()) == "verify_v3" else "verify_v3"
    os.makedirs(out_dir, exist_ok=True)
    stim_path = os.path.join(out_dir, "tb_ch02_skid_stim.txt")
    exp_path = os.path.join(out_dir, "tb_ch02_skid_expected.txt")
    
    with open(stim_path, "w", newline="\n") as f:
        f.writelines(stim_lines)
    with open(exp_path, "w", newline="\n") as f:
        f.writelines(exp_lines)
    print(f"Wrote {stim_path} and {exp_path} successfully.")

if __name__ == "__main__":
    run_simulation()
