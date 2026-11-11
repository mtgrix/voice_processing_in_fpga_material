#!/usr/bin/env python3
"""verify_v3/ch10_twin.py

Cycle-accurate, bit-exact Python twin of rtl/v3/ch10_voicing.v (Praat-Consistent Voicing Unit).
Simulates the 3-stage pipeline:
- Stage 1: Shift-and-add linear combinations, ramp calculation, and silence detection
- Stage 2: 54-bit products (LHS = term1 * 3*GP, RHS = 100*R0n * ramp_pos)
- Stage 3: Strict comparator (LHS > RHS), silence gating, and Q12.4 F0 output multiplexer

Generates stimulus and expected files for tb/v3/tb_ch10_voicing.v:
- verify_v3/tb_ch10_voicing_stim.txt
- verify_v3/tb_ch10_voicing_expected.txt

Follows all project lessons:
- Every boolean cast to int() for $fscanf compatibility
- Newline='\n' on all vector writes
- Sampling convention: inputs driven at negedge clk, registered outputs checked at posedge clk + #1
"""

import os
import sys
import random
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASE_DIR)
GOLDEN_DIR = os.path.join(REPO_DIR, 'golden_v2')
sys.path.insert(0, GOLDEN_DIR)

import constants as K
import fixed_twin
from praat_float_ref import read_wav_float

# -----------------------------------------------------------------------------
# 1. Functional Model (Pure Combinational Reference)
# -----------------------------------------------------------------------------
def decide_voicing_pure(f0_raw, sc, r0n, cand_found, lp, gp):
    """Bit-exact functional model of the integer voicing condition."""
    silence_trap = (r0n == 0) or (lp == 0) or (gp == 0) or (not cand_found)
    term1 = 100 * sc - 45 * r0n
    mult3_gp = 3 * gp
    lhs = term1 * mult3_gp

    ramp = 6 * gp - 145 * lp
    ramp_pos = max(0, ramp)
    term_100_r0n = 100 * r0n
    rhs = term_100_r0n * ramp_pos

    is_voiced = (not silence_trap) and (lhs > rhs)
    f0_out = f0_raw if is_voiced else 0
    return {
        'voiced': int(is_voiced),
        'f0': f0_out,
        'lhs': lhs,
        'rhs': rhs,
        'silence_trap': int(silence_trap)
    }

# -----------------------------------------------------------------------------
# 2. Cycle-Accurate 3-Stage Pipeline Twin
# -----------------------------------------------------------------------------
class VoicingTwin:
    def __init__(self):
        self.reset()

    def reset(self):
        # Stage 1 registers
        self.s1_term1 = 0
        self.s1_mult3_gp = 0
        self.s1_100_r0n = 0
        self.s1_ramp_pos = 0
        self.s1_f0_raw = 0
        self.s1_silence_trap = 1
        self.s1_valid = 0

        # Stage 2 registers
        self.s2_lhs = 0
        self.s2_rhs = 0
        self.s2_f0_raw = 0
        self.s2_silence_trap = 1
        self.s2_valid = 0

        # Stage 3 registers (DUT outputs)
        self.out_valid = 0
        self.out_f0 = 0
        self.out_voiced = 0
        self.out_lhs = 0
        self.out_rhs = 0

    def clock(self, rst_n, in_valid, in_f0_raw, in_sc, in_r0n, in_cand_found, in_lp, in_gp):
        """Advances the 3-stage pipeline by exactly one clock cycle."""
        if not rst_n:
            self.reset()
            return {
                'out_valid': 0,
                'out_f0': 0,
                'out_voiced': 0,
                'out_lhs': 0,
                'out_rhs': 0
            }

        # ---------------------------------------------------------------------
        # Stage 3 Update (reads old Stage 2 registers)
        # ---------------------------------------------------------------------
        comb_is_voiced = (not self.s2_silence_trap) and (self.s2_lhs > self.s2_rhs)
        next_out_valid = self.s2_valid
        next_out_voiced = int(comb_is_voiced)
        next_out_f0 = self.s2_f0_raw if comb_is_voiced else 0
        next_out_lhs = self.s2_lhs
        next_out_rhs = self.s2_rhs

        # ---------------------------------------------------------------------
        # Stage 2 Update (reads old Stage 1 registers)
        # ---------------------------------------------------------------------
        # 54-bit signed multiplications
        comb_lhs = self.s1_term1 * self.s1_mult3_gp
        comb_rhs = self.s1_100_r0n * self.s1_ramp_pos

        next_s2_lhs = comb_lhs
        next_s2_rhs = comb_rhs
        next_s2_f0_raw = self.s1_f0_raw
        next_s2_silence_trap = self.s1_silence_trap
        next_s2_valid = self.s1_valid

        # ---------------------------------------------------------------------
        # Stage 1 Update (reads inputs)
        # ---------------------------------------------------------------------
        # Shift-adds:
        term_100_sc = (in_sc << 6) + (in_sc << 5) + (in_sc << 2)
        term_45_r0n = (in_r0n << 5) + (in_r0n << 3) + (in_r0n << 2) + in_r0n
        comb_term1 = term_100_sc - term_45_r0n

        comb_mult3_gp = (in_gp << 1) + in_gp
        comb_100_r0n = (in_r0n << 6) + (in_r0n << 5) + (in_r0n << 2)

        comb_mult6_gp = (in_gp << 2) + (in_gp << 1)
        comb_mult145_lp = (in_lp << 7) + (in_lp << 4) + in_lp

        comb_ramp_diff = comb_mult6_gp - comb_mult145_lp
        comb_ramp_pos = comb_ramp_diff if comb_ramp_diff > 0 else 0

        comb_silence_trap = (in_r0n == 0) or (in_lp == 0) or (in_gp == 0) or (not in_cand_found)

        # Latch new values
        self.out_valid = next_out_valid
        self.out_voiced = next_out_voiced
        self.out_f0 = next_out_f0
        self.out_lhs = next_out_lhs
        self.out_rhs = next_out_rhs

        self.s2_lhs = next_s2_lhs
        self.s2_rhs = next_s2_rhs
        self.s2_f0_raw = next_s2_f0_raw
        self.s2_silence_trap = next_s2_silence_trap
        self.s2_valid = next_s2_valid

        self.s1_term1 = comb_term1
        self.s1_mult3_gp = comb_mult3_gp
        self.s1_100_r0n = comb_100_r0n
        self.s1_ramp_pos = comb_ramp_pos
        self.s1_f0_raw = in_f0_raw
        self.s1_silence_trap = int(comb_silence_trap)
        self.s1_valid = in_valid

        return {
            'out_valid': self.out_valid,
            'out_f0': self.out_f0,
            'out_voiced': self.out_voiced,
            'out_lhs': self.out_lhs,
            'out_rhs': self.out_rhs
        }

# -----------------------------------------------------------------------------
# 3. Vector Generation and Testbench Validation
# -----------------------------------------------------------------------------
def build_test_stimuli():
    """Builds a comprehensive set of >= 200 test cases with diverse properties."""
    cases = []

    # 1. The 10 canonical hand-calculation cases from ch10_math_audit.py
    canonical = [
        ("Ex1: Voiced Speech", 2560, 800000, 1000000, 1, 2000, 20000),
        ("Ex2: Flat Voiceless", 2560, 350000, 1000000, 1, 2000, 20000),
        ("Ex3: Strict Silence", 2560, 700000, 1000000, 1, 400, 20000),
        ("Ex4: Ramp Zone Voiced", 2560, 700000, 1000000, 1, 760, 20000),
        ("Ex5: Ramp Zone Voiceless", 2560, 600000, 1000000, 1, 700, 20000),
        ("Ex6: Near-threshold 0.4499", 2560, 449900, 1000000, 1, 2000, 20000),
        ("Ex7: Near-threshold 0.4501", 2560, 450100, 1000000, 1, 2000, 20000),
        ("Ex8: Silence shortcut LP=0", 2560, 800000, 1000000, 1, 0, 20000),
        ("Ex9: Silence shortcut GP=0", 2560, 800000, 1000000, 1, 2000, 0),
        ("Ex10: Silence shortcut R0=0", 2560, 800000, 0, 1, 2000, 20000),
        ("Ex11: No candidate found", 2560, 800000, 1000000, 0, 2000, 20000),
        ("Ex12: Max dynamic range stress", 4000, (1 << 27) - 1, (1 << 27) - 1, 1, 59379, 32768),
    ]
    for desc, f0_raw, sc, r0n, found, lp, gp in canonical:
        cases.append((f0_raw, sc, r0n, found, lp, gp))

    # 2. Dense near-threshold scan around 0.45 (ratios 0.4490 to 0.4510 in steps of 0.0001)
    for step in range(-10, 11):
        ratio = 0.45 + step * 0.0001
        r0n = 1000000
        sc = int(round(ratio * r0n))
        gp = 20000
        lp = 2000  # I = 0.10 (active flat region)
        cases.append((2500, sc, r0n, 1, lp, gp))

    # 3. Dense ramp region scan: I in [0.030, 0.042] in steps of 0.0005
    for i_step in range(300, 421, 5):
        i_val = i_step / 10000.0
        gp = 20000
        lp = int(round(i_val * gp))
        r0n = 1000000
        # Test both above and below voicing threshold
        cases.append((3000, int(0.70 * r0n), r0n, 1, lp, gp))
        cases.append((3000, int(0.40 * r0n), r0n, 1, lp, gp))

    # 4. Silence shortcut combinations (permutations of zeros)
    cases.append((1000, 500000, 0, 1, 0, 0))
    cases.append((1000, 500000, 1000000, 0, 0, 20000))
    cases.append((1000, 500000, 1000000, 1, 0, 20000))
    cases.append((1000, 500000, 1000000, 1, 1000, 0))

    # 5. Golden WAV real frames: synth_glide_vuv_16k.wav (277 frames)
    wav1 = os.path.join(GOLDEN_DIR, "synth_glide_vuv_16k.wav")
    if os.path.exists(wav1):
        xi1, _ = read_wav_float(wav1)
        gp1 = fixed_twin.global_peak(xi1)
        res1 = fixed_twin.analyse_fixed(xi1)
        for f, f0q in zip(res1['frames'], res1['f0q']):
            sh = f['sh']
            r0n = f['r0'] >> sh if f['r0'] > 0 else 0
            found = 1 if f['best'] > 0 else 0
            f0_raw = f['f0q_raw'] if 'f0q_raw' in f else f0q
            cases.append((min(f0_raw, 65535), f['sc'], r0n, found, f['lp'], gp1))

    # 6. Golden WAV real frames: synth_glide_vuv_16k_snr5.wav (277 frames)
    wav2 = os.path.join(GOLDEN_DIR, "synth_glide_vuv_16k_snr5.wav")
    if os.path.exists(wav2):
        xi2, _ = read_wav_float(wav2)
        gp2 = fixed_twin.global_peak(xi2)
        res2 = fixed_twin.analyse_fixed(xi2)
        for f, f0q in zip(res2['frames'], res2['f0q']):
            sh = f['sh']
            r0n = f['r0'] >> sh if f['r0'] > 0 else 0
            found = 1 if f['best'] > 0 else 0
            f0_raw = f['f0q_raw'] if 'f0q_raw' in f else f0q
            cases.append((min(f0_raw, 65535), f['sc'], r0n, found, f['lp'], gp2))

    return cases

def generate_cycle_vectors():
    print("=" * 70)
    print("GENERATING CYCLE-ACCURATE VECTORS FOR CH10 VOICING UNIT")
    print("=" * 70)

    cases = build_test_stimuli()
    print(f"Total test frame cases collected: {len(cases)}")
    assert len(cases) >= 200, f"Expected >= 200 test cases, got {len(cases)}!"

    twin = VoicingTwin()
    stim_lines = []
    exp_lines = []

    # Cycle 0-2: Reset sequence
    for _ in range(3):
        out = twin.clock(0, 0, 0, 0, 0, 0, 0, 0)
        stim_lines.append("0 0 0 0 0 0 0 0\n")
        exp_lines.append(f"{int(out['out_valid'])} {out['out_f0']} {int(out['out_voiced'])} {out['out_lhs']} {out['out_rhs']}\n")

    # Play test cases with variable gaps to test pipeline throughput and isolation
    random.seed(42)
    processed_count = 0

    for idx, (f0_raw, sc, r0n, found, lp, gp) in enumerate(cases):
        # 1. Drive valid transaction for 1 cycle
        out = twin.clock(1, 1, f0_raw, sc, r0n, found, lp, gp)
        stim_lines.append(f"1 1 {f0_raw} {sc} {r0n} {int(found)} {lp} {gp}\n")
        exp_lines.append(f"{int(out['out_valid'])} {out['out_f0']} {int(out['out_voiced'])} {out['out_lhs']} {out['out_rhs']}\n")
        processed_count += 1

        # 2. Insert pseudo-random idle gap (0 to 4 cycles) between transactions
        gap_len = random.choice([0, 0, 1, 2, 3])
        for _ in range(gap_len):
            out = twin.clock(1, 0, 0, 0, 0, 0, 0, 0)
            stim_lines.append("1 0 0 0 0 0 0 0\n")
            exp_lines.append(f"{int(out['out_valid'])} {out['out_f0']} {int(out['out_voiced'])} {out['out_lhs']} {out['out_rhs']}\n")

    # Flush pipeline (at least 5 cycles after last transaction)
    for _ in range(6):
        out = twin.clock(1, 0, 0, 0, 0, 0, 0, 0)
        stim_lines.append("1 0 0 0 0 0 0 0\n")
        exp_lines.append(f"{int(out['out_valid'])} {out['out_f0']} {int(out['out_voiced'])} {out['out_lhs']} {out['out_rhs']}\n")

    total_cycles = len(stim_lines)
    print(f"Total cycles simulated: {total_cycles}")
    print(f"Total test vectors issued: {processed_count}")

    stim_file = os.path.join(BASE_DIR, "tb_ch10_voicing_stim.txt")
    exp_file = os.path.join(BASE_DIR, "tb_ch10_voicing_expected.txt")

    with open(stim_file, "w", newline="\n") as f:
        f.writelines(stim_lines)

    with open(exp_file, "w", newline="\n") as f:
        f.writelines(exp_lines)

    print(f"Wrote stimulus to: {stim_file} ({os.path.getsize(stim_file)} bytes)")
    print(f"Wrote expected to: {exp_file} ({os.path.getsize(exp_file)} bytes)")
    print("[+] Vector generation completed successfully.")

if __name__ == '__main__':
    generate_cycle_vectors()
