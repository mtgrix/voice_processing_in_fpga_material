#!/usr/bin/env python3
"""verify_v3/ch11_twin.py

Bit-exact and cycle-exact Python Twin of the Median-3 FPGA hardware module (rtl/v3/ch11_median3.v).

Hardware architecture:
- Registers: f0_z0 (new sample), f0_z1 (center sample), f0_z2 (past sample), f0_med (output).
- 3-element sorting network (3 comparators): determines median in 1 cycle of combinational logic.
- FSM control states:
  - S_IDLE: wait for frame 0 (in_valid && in_first).
  - S_STREAM: receive frame k, emit frame k-1, shift pipeline registers.
  - S_FLUSH: automatic flush beat upon in_last, duplicate last sample f0_z1, emit frame N-1.

Outputs generated:
- verify_v3/tb_ch11_median3_stim.txt
- verify_v3/tb_ch11_median3_expected.txt
"""

import os
import sys
import random
import numpy as np

# Add golden_v2 to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'golden_v2')))
from praat_float_ref import read_wav_float
from fixed_twin import analyse_fixed

S_IDLE   = 0
S_STREAM = 1
S_FLUSH  = 2

def median3_logic(a, b, c):
    """M  ph ng m ng 3 b  so s nh trong Verilog."""
    cmp_ab = (a <= b)
    cmp_bc = (b <= c)
    cmp_ac = (a <= c)
    if cmp_ab:
        if cmp_bc:
            return b
        elif cmp_ac:
            return c
        else:
            return a
    else:
        if cmp_ac:
            return a
        elif cmp_bc:
            return c
        else:
            return b

class Median3Twin:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.state = S_IDLE
        self.f0_z0 = 0
        self.f0_z1 = 0
        self.f0_z2 = 0
        self.f0_med = 0
        self.out_valid = 0
        self.out_last = 0
        
    def clock(self, in_valid, in_first, in_last, in_f0):
        """Simulate one posedge clk cycle of ch11_median3.v."""
        # Temporary variables for next cycle outputs
        next_state = self.state
        next_z0 = self.f0_z0
        next_z1 = self.f0_z1
        next_z2 = self.f0_z2
        next_med = self.f0_med
        next_out_valid = 0
        next_out_last = 0
        
        in_valid = int(in_valid)
        in_first = int(in_first)
        in_last  = int(in_last)
        in_f0    = int(in_f0) & 0xFFFF
        
        if self.state == S_IDLE:
            if in_valid and in_first:
                # Load frame 0: duplicate into z0, z1, z2
                next_z0 = in_f0
                next_z1 = in_f0
                next_z2 = in_f0
                next_out_valid = 0
                next_out_last = 0
                if in_last:
                    # Edge case: single-frame file (N = 1)
                    next_state = S_FLUSH
                else:
                    next_state = S_STREAM
            else:
                next_out_valid = 0
                next_out_last = 0
                
        elif self.state == S_STREAM:
            if in_valid:
                # Next frame x[k] arrives
                med_val = median3_logic(self.f0_z2, self.f0_z1, in_f0)
                next_med = med_val
                next_out_valid = 1
                next_out_last = 0
                
                # Update shift registers
                next_z2 = self.f0_z1
                next_z1 = in_f0
                next_z0 = in_f0
                
                if in_last:
                    # Last frame x[N-1] arrived: transition to flush beat
                    next_state = S_FLUSH
                else:
                    next_state = S_STREAM
            else:
                # No valid data: hold registers, deassert out_valid
                next_out_valid = 0
                next_out_last = 0
                
        elif self.state == S_FLUSH:
            # Flush beat: duplicate last sample x[N-1] (stored in f0_z1)
            med_val = median3_logic(self.f0_z2, self.f0_z1, self.f0_z1)
            next_med = med_val
            next_out_valid = 1
            next_out_last = 1
            
            next_z0 = self.f0_z1
            next_state = S_IDLE
            
        # Update internal state
        self.state = next_state
        self.f0_z0 = next_z0
        self.f0_z1 = next_z1
        self.f0_z2 = next_z2
        self.f0_med = next_med
        self.out_valid = next_out_valid
        self.out_last = next_out_last
        
        return self.out_valid, self.out_last, self.f0_med

def generate_stream_vectors(twin, seq, stall_prob=0.0):
    """T o chu i vector cho 1 t p  m thanh (g m N khung f0), c  th  ch n chu k  r i."""
    stim_list = []
    expected_list = []
    
    N = len(seq)
    if N == 0:
        return stim_list, expected_list
        
    for k in range(N):
        # C  th  ch n m t s  chu k  idle tr  c khi   a khung k
        if stall_prob > 0.0:
            n_stalls = random.choices([0, 1, 2, 3], weights=[0.6, 0.2, 0.1, 0.1])[0]
            for _ in range(n_stalls):
                ov, ol, omed = twin.clock(0, 0, 0, 0)
                stim_list.append((0, 0, 0, 0))
                expected_list.append((ov, ol, omed))
                
        in_first = 1 if (k == 0) else 0
        in_last  = 1 if (k == N - 1) else 0
        in_f0    = int(seq[k])
        
        ov, ol, omed = twin.clock(1, in_first, in_last, in_f0)
        stim_list.append((1, in_first, in_last, in_f0))
        expected_list.append((ov, ol, omed))
        
    # Chu k  x  (Flush cycle)
    ov, ol, omed = twin.clock(0, 0, 0, 0)
    stim_list.append((0, 0, 0, 0))
    expected_list.append((ov, ol, omed))
    
    # 2 chu k  r i sau khi x 
    for _ in range(2):
        ov, ol, omed = twin.clock(0, 0, 0, 0)
        stim_list.append((0, 0, 0, 0))
        expected_list.append((ov, ol, omed))
        
    return stim_list, expected_list

def main():
    random.seed(42)
    twin = Median3Twin()
    
    all_stim = []
    all_expected = []
    
    print("=== SINH VECT  KI M TH  CHO MODULE CH11_MEDIAN3 ===")
    
    # T p 1: V  d  t nh tay    c  ng [120, 122, 244, 121, 0, 0] (li n m ch)
    s1, e1 = generate_stream_vectors(twin, [120, 122, 244, 121, 0, 0], stall_prob=0.0)
    all_stim.extend(s1); all_expected.extend(e1)
    
    # T p 2: V  d  t nh tay    c  ng c  ng t qu ng (idle stalls)
    s2, e2 = generate_stream_vectors(twin, [120, 122, 244, 121, 0, 0], stall_prob=0.4)
    all_stim.extend(s2); all_expected.extend(e2)
    
    # T p 3: Bi n 1 khung duy nh t N = 1
    s3, e3 = generate_stream_vectors(twin, [2500], stall_prob=0.0)
    all_stim.extend(s3); all_expected.extend(e3)
    
    # T p 4: Bi n 2 khung N = 2
    s4, e4 = generate_stream_vectors(twin, [2000, 3200], stall_prob=0.0)
    all_stim.extend(s4); all_expected.extend(e4)
    
    # T p 5: C c ca gai   n l  (Single spikes - Octave doubling & halving)
    s5, e5 = generate_stream_vectors(twin, [1600, 1600, 3200, 1600, 1600, 800, 1600, 1600], stall_prob=0.2)
    all_stim.extend(s5); all_expected.extend(e5)
    
    # T p 6: C c ca gai k p (Double spikes - k o d i 2 khung li n ti p)
    s6, e6 = generate_stream_vectors(twin, [1800, 1800, 3600, 3600, 1800, 1800, 900, 900, 1800], stall_prob=0.2)
    all_stim.extend(s6); all_expected.extend(e6)
    
    # T p 7: Chu i s  0 (unvoiced runs) v    m s ng gi  / m t ti ng
    s7, e7 = generate_stream_vectors(twin, [0, 0, 0, 2200, 0, 0, 2200, 2200, 0, 2200, 2200, 0, 0], stall_prob=0.2)
    all_stim.extend(s7); all_expected.extend(e7)
    
    # T p 8: Chuy n ti p h u thanh / v  thanh
    s8, e8 = generate_stream_vectors(twin, [0, 0, 0, 1500, 1510, 1520, 1530, 0, 0, 0], stall_prob=0.0)
    all_stim.extend(s8); all_expected.extend(e8)
    
    # T p 9: D  li u th c t  t p s ch synth_glide_vuv_16k.wav (277 khung)
    wav_clean = os.path.join(os.path.dirname(__file__), '..', 'golden_v2', 'synth_glide_vuv_16k.wav')
    raw_clean, _ = read_wav_float(wav_clean)
    fx_clean = analyse_fixed(raw_clean)
    s9, e9 = generate_stream_vectors(twin, fx_clean['f0q'], stall_prob=0.1)
    all_stim.extend(s9); all_expected.extend(e9)
    
    # T p 10: D  li u th c t  t p c  nhi u synth_glide_vuv_16k_snr5.wav (277 khung)
    wav_snr5 = os.path.join(os.path.dirname(__file__), '..', 'golden_v2', 'synth_glide_vuv_16k_snr5.wav')
    raw_snr5, _ = read_wav_float(wav_snr5)
    fx_snr5 = analyse_fixed(raw_snr5)
    s10, e10 = generate_stream_vectors(twin, fx_snr5['f0q'], stall_prob=0.1)
    all_stim.extend(s10); all_expected.extend(e10)
    
    stim_path = os.path.join(os.path.dirname(__file__), 'tb_ch11_median3_stim.txt')
    expected_path = os.path.join(os.path.dirname(__file__), 'tb_ch11_median3_expected.txt')
    
    with open(stim_path, 'w', newline='\n') as f_stim, open(expected_path, 'w', newline='\n') as f_exp:
        for (v, first, last, f0), (ov, ol, omed) in zip(all_stim, all_expected):
            f_stim.write(f"{int(v)} {int(first)} {int(last)} {int(f0)}\n")
            f_exp.write(f"{int(ov)} {int(ol)} {int(omed)}\n")
            
    print(f"T ng s  chu k  m  ph ng    sinh: {len(all_stim)} chu k .")
    n_valid_out = sum(1 for _, (ov, _, _) in zip(all_stim, all_expected) if ov == 1)
    print(f"S  k t qu  ng  ra ho n ch nh (out_valid=1): {n_valid_out}.")
    print(f"   ghi: {stim_path}")
    print(f"   ghi: {expected_path}")

if __name__ == '__main__':
    main()
