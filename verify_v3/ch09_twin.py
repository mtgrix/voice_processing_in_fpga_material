#!/usr/bin/env python3
"""verify_v3/ch09_twin.py

Cycle-accurate, bit-exact Python twin of:
1. rtl/v3/ch09_radix2_div.v (Sequential Radix-2 Restoring Divider)
2. rtl/v3/ch09_peak_finder.v (Streaming Candidate Peak Finder)
3. rtl/v3/ch09_f0_calc.v (Top-Level F0 Parabolic Interpolation and Divider Unit)

Generates test vectors for:
- tb/v3/tb_ch09_div.v (>= 200 triples: negative num, small den, large den, tau=27, tau=213)
- tb/v3/tb_ch09_calc.v (frame-level verification against golden_v2 fixed_twin.py)
"""

import os
import sys
import random
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, os.path.join(REPO_DIR, 'golden_v2'))

import constants as K
from fixed_twin import analyse_fixed
from praat_float_ref import read_wav_float

# -----------------------------------------------------------------------------
# 1. Pure Functional Model (matches golden_v2/fixed_twin.py lines 71-88)
# -----------------------------------------------------------------------------
def calc_parabola_div(um, u0, up, tau_p):
    """Computes exact parabolic interpolation parameters and single division F0_Q12.4."""
    num = up - um
    den = 2 * u0 - um - up
    assert den > 0, f"den must be positive, got {den} (um={um}, u0={u0}, up={up})"
    s2 = max(0, den.bit_length() - 24)
    numn = num >> s2
    denn = den >> s2
    D = 2 * denn * tau_p + numn
    assert D > 0, f"D must be positive, got {D}"
    prod_512k = 512000 * denn
    N = prod_512k + D // 2
    quotient = N // D
    remain = N % D
    f0q = min(quotient, 65535)
    return {
        'num': num, 'den': den, 's2': s2,
        'numn': numn, 'denn': denn,
        'D': D, 'N': N,
        'quotient': quotient, 'remain': remain,
        'f0q': f0q
    }

# -----------------------------------------------------------------------------
# 2. Cycle-Accurate Model of ch09_radix2_div.v
# -----------------------------------------------------------------------------
class Radix2DivTwin:
    def __init__(self, widthn=44, widthd=34):
        self.widthn = widthn
        self.widthd = widthd
        self.reset()

    def reset(self):
        self.state = 0 # 0: IDLE, 1: CALC, 2: DONE
        self.count = 0
        self.quo_reg = 0
        self.rem_reg = 0
        self.div_reg = 0
        self.busy = 0
        self.done = 0
        self.quotient = 0
        self.remain = 0

    def step(self, rst_n, start, numer, denom):
        if not rst_n:
            self.reset()
            return {'busy': 0, 'done': 0, 'quotient': 0, 'remain': 0}

        self.done = 0
        if self.state == 0: # S_IDLE
            self.busy = 0
            if start:
                self.busy = 1
                self.count = self.widthn
                self.quo_reg = numer & ((1 << self.widthn) - 1)
                self.rem_reg = 0
                self.div_reg = denom & ((1 << self.widthd) - 1)
                self.state = 1 # S_CALC
        elif self.state == 1: # S_CALC
            # 1 restoring step
            next_rem = ((self.rem_reg << 1) | ((self.quo_reg >> (self.widthn - 1)) & 1))
            ext_div = self.div_reg
            if next_rem >= ext_div:
                self.rem_reg = (next_rem - ext_div) & ((1 << self.widthn) - 1)
                self.quo_reg = ((self.quo_reg << 1) | 1) & ((1 << self.widthn) - 1)
            else:
                self.rem_reg = next_rem & ((1 << self.widthn) - 1)
                self.quo_reg = (self.quo_reg << 1) & ((1 << self.widthn) - 1)

            self.count -= 1
            if self.count == 0:
                self.state = 2 # S_DONE
        elif self.state == 2: # S_DONE
            self.busy = 0
            self.done = 1
            self.quotient = self.quo_reg
            self.remain = self.rem_reg & ((1 << self.widthd) - 1)
            self.state = 0 # S_IDLE

        return {
            'busy': int(self.busy),
            'done': int(self.done),
            'quotient': int(self.quotient),
            'remain': int(self.remain)
        }

# -----------------------------------------------------------------------------
# 3. Vector Generation for tb_ch09_div.v
# -----------------------------------------------------------------------------
def generate_div_vectors(stim_path, exp_path):
    print("Generating divider test vectors (tb_ch09_div)...")
    triples = []

    # 1. Hand calculation example
    triples.append((8000, 10000, 9000, 100)) # delta = +1/6, F0 = 159.73 Hz, Q12.4 = 2556

    # 2. Exercise 2 example (negative num)
    triples.append((9500, 10000, 8500, 80)) # delta = -0.25, Q12.4 = 3210

    # 3. Boundary lag tau = 27 (minimum candidate lag)
    triples.append((12000, 15000, 13000, 27))
    triples.append((14000, 15000, 12000, 27))
    triples.append((13000, 15000, 13000, 27)) # symmetrical num = 0

    # 4. Boundary lag tau = 213 (maximum candidate lag)
    triples.append((5000, 8000, 6000, 213))
    triples.append((7000, 8000, 5000, 213))
    triples.append((6000, 8000, 6000, 213))

    # 5. Small den values (den = 1, 2, 3, 4, 5, 10, 20)
    # y = (100, 101, 101): den = 202 - 100 - 101 = 1, num = 1
    triples.append((100, 101, 101, 100))
    # y = (100, 101, 100): den = 202 - 100 - 100 = 2, num = 0
    triples.append((100, 101, 100, 100))
    # y = (99, 101, 100): den = 202 - 99 - 100 = 3, num = 1
    triples.append((99, 101, 100, 100))

    # 6. Large den values triggering s2 normalization (s2 = 1, 2, 3, 4, 5)
    # s2 = 1: den > 2^24 ~ 16,777,216
    u0_s2_1 = 20000000
    triples.append((u0_s2_1 - 9000000, u0_s2_1, u0_s2_1 - 8000000, 120))
    # s2 = 2: den > 2^25 ~ 33,554,432
    u0_s2_2 = 35000000
    triples.append((u0_s2_2 - 18000000, u0_s2_2, u0_s2_2 - 16000000, 150))
    # s2 = 3: den > 2^26 ~ 67,108,864
    u0_s2_3 = 70000000
    triples.append((u0_s2_3 - 35000000, u0_s2_3, u0_s2_3 - 34000000, 180))
    # s2 = 4: den > 2^27 ~ 134,217,728
    u0_s2_4 = 134000000
    triples.append((u0_s2_4 - 68000000, u0_s2_4, u0_s2_4 - 67000000, 90))

    # 7. Randomized triples across full parameter space (>= 250 vectors)
    rng = random.Random(42)
    for _ in range(250):
        t_p = rng.randint(27, 213)
        u0 = rng.randint(1000, 60000000)
        # Choose um, up such that u0 > um and u0 >= up
        d_m = rng.randint(1, min(u0, 20000000))
        d_p = rng.randint(0, min(u0, 20000000))
        um = u0 - d_m
        up = u0 - d_p
        triples.append((um, u0, up, t_p))

    print(f"Total test triples: {len(triples)}")

    # Run cycle-accurate simulation for tb_ch09_div
    div_twin = Radix2DivTwin(widthn=44, widthd=34)
    stim_lines = []
    exp_lines = []

    # Cycle 0: reset
    stim_lines.append("0 0 0 0\n") # rst_n, start, numer, denom
    exp = div_twin.step(0, 0, 0, 0)
    exp_lines.append(f"{exp['busy']} {exp['done']} {exp['quotient']} {exp['remain']}\n")

    # Run each triple
    for um, u0, up, tau_p in triples:
        res = calc_parabola_div(um, u0, up, tau_p)
        N = res['N']
        D = res['D']

        # Assert start for 1 cycle
        stim_lines.append(f"1 1 {N} {D}\n")
        exp = div_twin.step(1, 1, N, D)
        exp_lines.append(f"{exp['busy']} {exp['done']} {exp['quotient']} {exp['remain']}\n")

        # Wait during division (44 cycles)
        while True:
            stim_lines.append(f"1 0 {N} {D}\n")
            exp = div_twin.step(1, 0, N, D)
            exp_lines.append(f"{exp['busy']} {exp['done']} {exp['quotient']} {exp['remain']}\n")
            if exp['done'] == 1:
                assert exp['quotient'] == res['quotient'], f"Quotient mismatch: {exp['quotient']} != {res['quotient']}"
                assert exp['remain'] == res['remain'], f"Remain mismatch: {exp['remain']} != {res['remain']}"
                break

        # 1 idle cycle between divisions
        stim_lines.append("1 0 0 0\n")
        exp = div_twin.step(1, 0, 0, 0)
        exp_lines.append(f"{exp['busy']} {exp['done']} {exp['quotient']} {exp['remain']}\n")

    with open(stim_path, 'w', newline='\n') as f:
        f.writelines(stim_lines)
    with open(exp_path, 'w', newline='\n') as f:
        f.writelines(exp_lines)

    def fmt_p(p):
        return p.replace(REPO_DIR, '/workspace/writing_material/uoc_luong_f0_praat_fpga_quartus').replace('\\', '/')

    print(f"Wrote {len(stim_lines)} stimulus cycles to {fmt_p(stim_path)}")
    print(f"Wrote {len(exp_lines)} expected cycles to {fmt_p(exp_path)}")

# -----------------------------------------------------------------------------
# 4. Vector Generation for tb_ch09_calc.v (Frame-Level Verification)
# -----------------------------------------------------------------------------
def generate_calc_vectors(stim_path, exp_path):
    print("\nGenerating full-core test vectors (tb_ch09_calc)...")
    # Load golden synthetic frames
    wav_path = os.path.join(REPO_DIR, 'golden_v2', 'synth_glide_vuv_16k.wav')
    x, _ = read_wav_float(wav_path)
    res = analyse_fixed(x, trace=True)
    frames = res['frames']

    # Select representative frames: voiced, unvoiced, glide transitions
    # Frame 0 is unvoiced/silent, Frame 5 is unvoiced, Frame 10 is voiced (glide onset), etc.
    selected_indices = [0, 1, 2, 5, 10, 20, 50, 100, 150, 200, 250, 276]

    stim_lines = []
    exp_lines = []

    # Cycle 0: reset
    stim_lines.append("0 0 0 0 0 0 0\n") # rst_n, in_valid, in_tau, in_U, in_Sc, in_R0n, in_last
    exp_lines.append("0 0 0 0 0 0\n")    # out_valid, out_f0_raw, out_best_tau, out_sc, out_r0n, out_found

    # Helper function for calc step
    for ifr in selected_indices:
        fr = frames[ifr]
        if 'U' not in fr:
            continue

        U = fr['U']
        Sc = fr['Sc']
        r0n = fr['r0n']
        expected_best = fr['best']
        expected_sc = fr['sc'] if expected_best > 0 else 0
        expected_f0q = fr['f0q_raw'] if expected_best > 0 else 0
        expected_found = 1 if expected_best > 0 else 0

        # Feed 189 lags: tau = 26..214
        for t in range(26, 215):
            in_last = 1 if t == 214 else 0
            u_val = U[t]
            sc_val = Sc[t]
            stim_lines.append(f"1 1 {t} {u_val} {sc_val} {r0n} {in_last}\n")
            exp_lines.append("0 0 0 0 0 0\n")

        # Total latency from in_last (tau=214) to out_valid:
        # If a candidate peak is found (expected_found == 1):
        #   - 1 cycle for peak_finder to assert peak_valid
        #   - 1 cycle in S_IDLE to sample peak_valid and enter S_PREP (latching num, den)
        #   - 1 cycle in S_PREP to compute N, D combinatorially and assert div_start
        #   - 1 cycle in ch09_radix2_div to sample start in S_IDLE and load operands
        #   - 44 cycles in ch09_radix2_div S_CALC (restoring division steps)
        #   - 1 cycle in ch09_radix2_div S_DONE where div_done is asserted
        #   - 1 cycle in ch09_f0_calc S_DIV to sample div_done and register out_valid
        #   Total latency = 1 + 1 + 1 + 1 + 44 + 1 = 49 cycles from in_last to out_valid.
        # If no candidate peak found (expected_found == 0):
        #   - 1 cycle for peak_finder to assert peak_valid
        #   - 1 cycle in S_IDLE to sample peak_valid and register out_valid (div_cycles = 1)
        div_cycles = 49 if expected_found == 1 else 1

        for c in range(div_cycles):
            stim_lines.append("1 0 0 0 0 0 0\n")
            if c == div_cycles - 1:
                # Out valid cycle
                exp_lines.append(f"1 {expected_f0q} {expected_best} {expected_sc} {r0n} {expected_found}\n")
            else:
                exp_lines.append("0 0 0 0 0 0\n")

        # 2 idle cycles
        for _ in range(2):
            stim_lines.append("1 0 0 0 0 0 0\n")
            exp_lines.append("0 0 0 0 0 0\n")

    with open(stim_path, 'w', newline='\n') as f:
        f.writelines(stim_lines)
    with open(exp_path, 'w', newline='\n') as f:
        f.writelines(exp_lines)

    def fmt_p(p):
        return p.replace(REPO_DIR, '/workspace/writing_material/uoc_luong_f0_praat_fpga_quartus').replace('\\', '/')

    print(f"Wrote {len(stim_lines)} stimulus cycles to {fmt_p(stim_path)}")
    print(f"Wrote {len(exp_lines)} expected cycles to {fmt_p(exp_path)}")

def main():
    print("=== [ch09_twin] Generating Chapter 9 Stimulus and Expected Vectors ===")
    div_stim = os.path.join(BASE_DIR, 'tb_ch09_div_stim.txt')
    div_exp = os.path.join(BASE_DIR, 'tb_ch09_div_expected.txt')
    calc_stim = os.path.join(BASE_DIR, 'tb_ch09_calc_stim.txt')
    calc_exp = os.path.join(BASE_DIR, 'tb_ch09_calc_expected.txt')

    generate_div_vectors(div_stim, div_exp)
    generate_calc_vectors(calc_stim, calc_exp)
    print("=== [ch09_twin] Vector Generation Complete ===")

if __name__ == '__main__':
    main()
