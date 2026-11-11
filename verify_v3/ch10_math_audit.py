#!/usr/bin/env python3
"""
verify_v3/ch10_math_audit.py

Mathematical audit for Chapter 10:
1. Praat unvoiced candidate strength formula:
   R_unvoiced = voicingThreshold + max(0, 2 - I * (1 + voicingThreshold) / silenceThreshold)
   With defaults silenceThreshold = 0.03, voicingThreshold = 0.45:
   R_unvoiced = 0.45 + max(0, 2 - I * 145 / 3)
2. Ramp boundary derivation:
   2 - I * 145 / 3 = 0  =>  I = 6 / 145 = 0.041379310344827586... approx 0.0414
   I <= 0.03  =>  R_unvoiced >= 0.45 + (2 - 0.03 * 145 / 3) = 0.45 + 0.55 = 1.00
3. Derivation of the sample range for localPeak:
   halfnsamp_window = 319
   nsamp_period = floor(1 / (1/16000) / 75) = 213
   halfnsamp_period = 213 // 2 + 1 = 107
   1-based: startSample = 319 + 1 - 107 = 213; endSample = 319 + 107 = 426
   0-based: j in [212, 425] -> 425 - 212 + 1 = 214 samples.
4. Cross-multiplication derivation:
   Sc / R0n > 0.45 + max(0, 2 - (145 * LP) / (3 * GP))
   <=> (100*Sc - 45*R0n) / (100*R0n) > max(0, (6*GP - 145*LP) / (3*GP))
   Multiply by 300 * R0n * GP > 0:
   (100*Sc - 45*R0n) * 3 * GP > 100 * R0n * max(0, 6*GP - 145*LP)
5. Bit-width and dynamic range bounds:
   Sc < 2^27, R0n < 2^27, GP <= 32768, LP <= 59379.
   Show that LHS < 2^52 and RHS < 2^53, so 54-bit signed representation is exact and never overflows.
6. Hand-calculation trace examples:
   - Case 1: Active speech, high correlation (voiced)
   - Case 2: Active speech, low correlation (unvoiced, near 0.45)
   - Case 3: Silence region (I < 0.03, unvoiced)
   - Case 4: Ramp region (0.03 <= I <= 0.0414)
   - Edge case: Near-threshold 0.4499 vs 0.4500
"""

import math
import sys
import os

def main():
    print("=" * 70)
    print("CH10 MATHEMATICAL AUDIT: VOICING DECISION & CROSS-MULTIPLICATION")
    print("=" * 70)

    # 1. Praat default constants
    silence_thresh = 0.03
    voicing_thresh = 0.45
    factor = (1.0 + voicing_thresh) / silence_thresh
    print(f"\n[1] Praat constants:")
    print(f"    silenceThreshold = {silence_thresh}")
    print(f"    voicingThreshold = {voicing_thresh}")
    print(f"    (1 + voicingThreshold) / silenceThreshold = {factor:.8f} = 1.45 / 0.03 = 145 / 3 = {145/3:.8f}")

    # 2. Ramp boundaries
    I_silence = silence_thresh
    I_ramp_end = 2.0 / factor
    print(f"\n[2] Transition boundaries:")
    print(f"    Strict silence threshold (I_silence) = {I_silence}")
    print(f"    R_unvoiced at I = 0.03: {voicing_thresh + max(0.0, 2.0 - I_silence * factor):.6f}")
    print(f"    Ramp end threshold: 2 / (145/3) = 6/145 = {I_ramp_end:.8f}")
    print(f"    Agenda value: 0.0414, Difference: {abs(I_ramp_end - 0.0414):.8f}")
    print(f"    R_unvoiced at I = 6/145: {voicing_thresh + max(0.0, 2.0 - I_ramp_end * factor):.6f}")
    print(f"    R_unvoiced at I >= 6/145: {voicing_thresh:.6f} (constant flat)")

    # 3. Local peak window range
    fs = 16000
    pitch_floor = 75.0
    dx = 1.0 / fs
    dt_window = 3.0 / pitch_floor
    nsamp_window_raw = math.floor(dt_window / dx) # 640
    halfnsamp_window = nsamp_window_raw // 2 - 1   # 319
    nsamp_window = halfnsamp_window * 2            # 638
    nsamp_period = math.floor(1.0 / dx / pitch_floor) # 213
    halfnsamp_period = nsamp_period // 2 + 1       # 107

    start_sample_1based = halfnsamp_window + 1 - halfnsamp_period # 319 + 1 - 107 = 213
    end_sample_1based = halfnsamp_window + halfnsamp_period       # 319 + 107 = 426
    start_sample_0based = start_sample_1based - 1                 # 212
    end_sample_0based = end_sample_1based - 1                     # 425
    span_len = end_sample_0based - start_sample_0based + 1        # 214

    print(f"\n[3] LocalPeak geometry (Sound_to_Pitch.cpp lines 87-102):")
    print(f"    halfnsamp_window = {halfnsamp_window}")
    print(f"    nsamp_period = {nsamp_period}")
    print(f"    halfnsamp_period = {halfnsamp_period}")
    print(f"    startSample (1-based) = {start_sample_1based}, endSample (1-based) = {end_sample_1based}")
    print(f"    0-based index range: j = {start_sample_0based} .. {end_sample_0based}")
    print(f"    Total samples in local peak scan = {span_len}")

    # 4. Bit width and dynamic range analysis
    # Max values
    max_Sc = (1 << 27) - 1      # 134,217,727
    max_R0n = (1 << 27) - 1     # 134,217,727
    max_GP = 32768
    max_LP = 59379              # Stress frame |xw| max from ch06

    # LHS: (100 * Sc - 45 * R0n) * 3 * GP
    # Worst-case positive term1: Sc = max_Sc, R0n = 0
    term1_max = 100 * max_Sc
    term1_min = -45 * max_R0n
    mult3_GP_max = 3 * max_GP   # 3 * 32768 = 98304
    lhs_max = term1_max * mult3_GP_max
    lhs_min = term1_min * mult3_GP_max

    # RHS: 100 * R0n * max(0, 6*GP - 145*LP)
    ramp_term_max = 6 * max_GP  # 196608 (when LP = 0, though LP=0 is voiceless)
    term_100_R0n_max = 100 * max_R0n
    rhs_max = term_100_R0n_max * ramp_term_max

    print(f"\n[4] Bit-width & Dynamic Range Bounds:")
    print(f"    term1 (100*Sc - 45*R0n): min = {term1_min} ({term1_min.bit_length()} bits signed), max = {term1_max} ({term1_max.bit_length()} bits)")
    print(f"    3*GP: max = {mult3_GP_max} ({mult3_GP_max.bit_length()} bits unsigned)")
    print(f"    LHS max = {lhs_max} (approx {lhs_max:.3e}, bit_length = {lhs_max.bit_length()})")
    print(f"    LHS min = {lhs_min} (approx {lhs_min:.3e}, bit_length = {lhs_min.bit_length()})")
    print(f"    max(0, 6*GP - 145*LP): max = {ramp_term_max} ({ramp_term_max.bit_length()} bits unsigned)")
    print(f"    100*R0n: max = {term_100_R0n_max} ({term_100_R0n_max.bit_length()} bits unsigned)")
    print(f"    RHS max = {rhs_max} (approx {rhs_max:.3e}, bit_length = {rhs_max.bit_length()})")
    print(f"    Bound 2^51 = {1 << 51}")
    print(f"    Bound 2^52 = {1 << 52}")
    print(f"    Bound 2^53 = {1 << 53}")
    print(f"    LHS < 2^52: {abs(lhs_max) < (1 << 52) and abs(lhs_min) < (1 << 52)}")
    print(f"    RHS < 2^53: {rhs_max < (1 << 53)}")
    print(f"    54-bit signed range: [{- (1 << 53)}, {(1 << 53) - 1}]")
    print(f"    Conclusion: 54-bit signed representation is completely safe against overflow.")

    # 5. Hand-calculation trace examples
    print(f"\n[5] Hand-calculation trace examples:")
    examples = [
        # Name, Sc, R0n, GP, LP, cand_found
        ("Ex1: Voiced Speech (I=0.10, Sc/R0n=0.80)", 800000, 1000000, 20000, 2000, True),
        ("Ex2: Flat Voiceless (I=0.10, Sc/R0n=0.35)", 350000, 1000000, 20000, 2000, True),
        ("Ex3: Strict Silence (I=0.02 < 0.03)", 700000, 1000000, 20000, 400, True),
        ("Ex4: Ramp Zone Voiced (I=0.038, Sc/R0n=0.70)", 700000, 1000000, 20000, 760, True),
        ("Ex5: Ramp Zone Voiceless (I=0.035, Sc/R0n=0.60)", 600000, 1000000, 20000, 700, True),
        ("Ex6: Near-threshold 0.4499", int(0.4499 * 1000000), 1000000, 20000, 2000, True),
        ("Ex7: Near-threshold 0.4501", int(0.4501 * 1000000), 1000000, 20000, 2000, True),
        ("Ex8: Silence shortcut LP=0", 800000, 1000000, 20000, 0, True),
        ("Ex9: Silence shortcut GP=0", 800000, 1000000, 0, 2000, True),
        ("Ex10: Silence shortcut R0=0", 800000, 0, 20000, 2000, True),
    ]

    for name, sc, r0n, gp, lp, found in examples:
        # Float evaluation
        if gp > 0 and r0n > 0 and lp > 0 and found:
            I = lp / gp
            r_unv = 0.45 + max(0.0, 2.0 - I * 145.0 / 3.0)
            strength = sc / r0n
            float_voiced = (strength > r_unv)
        else:
            I = (lp / gp) if gp > 0 else 0.0
            r_unv = 0.45 + max(0.0, 2.0 - I * 145.0 / 3.0) if gp > 0 else 0.0
            strength = (sc / r0n) if r0n > 0 else 0.0
            float_voiced = False

        # Fixed evaluation
        if r0n == 0 or lp == 0 or gp == 0 or not found:
            fixed_voiced = False
            lhs = (100 * sc - 45 * r0n) * 3 * gp
            rhs = 100 * r0n * max(0, 6 * gp - 145 * lp)
        else:
            term1 = 100 * sc - 45 * r0n
            lhs = term1 * 3 * gp
            ramp = 6 * gp - 145 * lp
            ramp_pos = max(0, ramp)
            rhs = 100 * r0n * ramp_pos
            fixed_voiced = (lhs > rhs)

        match = (float_voiced == fixed_voiced)
        print(f"\n  --- {name} ---")
        print(f"      Sc={sc}, R0n={r0n}, GP={gp}, LP={lp}")
        print(f"      Float: I={I:.4f}, Strength={strength:.4f}, R_unv={r_unv:.4f} => Voiced={float_voiced}")
        print(f"      Fixed: LHS={lhs}, RHS={rhs}, LHS > RHS={lhs > rhs} => Voiced={fixed_voiced}")
        print(f"      Bit-exact equivalence: {match}")
        assert match, f"Mismatch in {name}!"

    print("\n[+] All mathematical checks PASSED successfully.")

if __name__ == '__main__':
    main()
