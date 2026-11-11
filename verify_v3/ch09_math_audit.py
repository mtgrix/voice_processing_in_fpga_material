#!/usr/bin/env python3
"""verify_v3/ch09_math_audit.py

Verifies all mathematical derivations, bit-widths, dynamic ranges,
and numerical examples for Chapter 9:
- Discrete lag step at tau=31, 32: 16.13 Hz, 54.96 cent (~55 cent)
- Q12.4 resolution (1/16 Hz = 0.0625 Hz): 1.08 cent @ 100 Hz, 0.22 cent @ 500 Hz
- Hand calculation: y=(8000, 10000, 9000), tau_p=100 -> delta=+1/6, F0=159.73 Hz,
  Q12.4=2556, single-division 512000*3000/601000 = 2555.74 -> 2556
- Comparison with v1 formula (256000*den/(tau_p*den + num)) giving 2551
- Bit-width audit for s2 normalization:
  den <= 2^28, s2 = max(0, bitlen(den) - 24), denn <= 2^24 - 1
  Numerator N = 512000*denn + D//2 < 2^44 -> LPM_WIDTHN = 44
  Denominator D = 2*denn*tau_p + numn < 2^34 -> LPM_WIDTHD = 34
- Verification across all frames of golden_v2 synthetic WAV files
"""

import os
import sys
import math
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, os.path.join(REPO_DIR, 'golden_v2'))

import constants as K
from fixed_twin import analyse_fixed
from praat_float_ref import read_wav_float

def main():
    print("=== [ch09_math_audit] Chapter 9 Mathematical and Numerical Audit ===")

    # -------------------------------------------------------------------------
    # 1. Discrete lag step between tau=31 and tau=32
    # -------------------------------------------------------------------------
    fs = 16000.0
    f31 = fs / 31.0
    f32 = fs / 32.0
    delta_f_31_32 = f31 - f32
    cents_31_32 = 1200.0 * math.log2(f31 / f32)

    print("\n--- 1. Discrete Lag Discretization Error ---")
    print(f"fs = {fs} Hz")
    print(f"tau = 31: F0 = {f31:.4f} Hz")
    print(f"tau = 32: F0 = {f32:.4f} Hz")
    print(f"Delta F0 = {delta_f_31_32:.4f} Hz (Agenda: 16,13 Hz)")
    print(f"Cents step = {cents_31_32:.4f} cent (Agenda: 55 cent)")
    assert abs(delta_f_31_32 - 16.1290) < 0.001
    assert abs(cents_31_32 - 54.9644) < 0.01

    # -------------------------------------------------------------------------
    # 2. Q12.4 resolution (1/16 Hz = 0.0625 Hz)
    # -------------------------------------------------------------------------
    res_hz = 1.0 / 16.0
    cents_at_100 = 1200.0 * math.log2((100.0 + res_hz) / 100.0)
    cents_at_500 = 1200.0 * math.log2((500.0 + res_hz) / 500.0)

    print("\n--- 2. Q12.4 Fixed-Point Resolution ---")
    print(f"Q12.4 LSB = {res_hz} Hz")
    print(f"At 100 Hz: 1 LSB = {cents_at_100:.4f} cent (Agenda: 1,08 cent)")
    print(f"At 500 Hz: 1 LSB = {cents_at_500:.4f} cent (Agenda: 0,22 cent)")
    assert abs(cents_at_100 - 1.0817) < 0.001
    assert abs(cents_at_500 - 0.2164) < 0.001

    # -------------------------------------------------------------------------
    # 3. Hand Calculation Example
    # -------------------------------------------------------------------------
    print("\n--- 3. Hand Calculation Example: y=(8000, 10000, 9000), tau_p=100 ---")
    um, u0, up = 8000, 10000, 9000
    tau_p = 100

    # Parabola parameters
    num = up - um
    den = 2 * u0 - um - up
    delta = num / (2.0 * den)
    tau_star = tau_p + delta
    f0_exact = fs / tau_star
    f0_q12_4_exact = 16.0 * f0_exact
    f0_q12_4_rounded = round(f0_q12_4_exact)

    # Single-divide formula:
    # F0_Q12.4 = round( 512000 * den / (2 * den * tau_p + num) )
    D = 2 * den * tau_p + num
    N = 512000 * den
    f0_single_div_float = N / D
    f0_single_div_int = (N + D // 2) // D

    # Old v1 formula: 256000 * den / (tau_p * den + num)
    D_v1 = tau_p * den + num
    N_v1 = 256000 * den
    f0_v1_float = N_v1 / D_v1
    f0_v1_rounded = round(f0_v1_float)

    print(f"y_-1 = {um}, y_0 = {u0}, y_+1 = {up}, tau_p = {tau_p}")
    print(f"num = y_+1 - y_-1 = {num}")
    print(f"den = 2*y_0 - y_-1 - y_+1 = {den}")
    print(f"delta = num / (2*den) = {delta:.6f} (+1/6 = {1.0/6.0:.6f})")
    print(f"tau* = tau_p + delta = {tau_star:.6f}")
    print(f"F0 exact = fs / tau* = {f0_exact:.4f} Hz (Agenda: 159,73 Hz)")
    print(f"F0 Q12.4 exact = {f0_q12_4_exact:.4f}")
    print(f"F0 Q12.4 rounded = {f0_q12_4_rounded} (Agenda: 2556)")
    print(f"Single-division: 512000*{den} / (2*{den}*{tau_p} + {num}) = {N}/{D} = {f0_single_div_float:.4f}")
    print(f"Single-division integer with +D//2 = {f0_single_div_int}")
    print(f"v1 formula: 256000*{den} / ({tau_p}*{den} + {num}) = {N_v1}/{D_v1} = {f0_v1_float:.4f} -> {f0_v1_rounded} (Agenda: 2551)")

    assert abs(delta - 1.0/6.0) < 1e-12
    assert abs(f0_exact - 159.7338) < 0.001
    assert f0_q12_4_rounded == 2556
    assert f0_single_div_int == 2556
    assert f0_v1_rounded == 2551

    # -------------------------------------------------------------------------
    # 4. Bit-Width and Dynamic Range Audit for s2 Normalization
    # -------------------------------------------------------------------------
    print("\n--- 4. Bit-Width and Dynamic Range Audit for s2 Normalization ---")
    # Worst-case mathematical bounds:
    # R0n < 2^27, U[t] < 2^27.
    # den = 2*u0 - um - up. Maximum den when u0 ~ 2^27 - 1, um = up = 0 -> den ~ 2^28.
    # s2 = max(0, bitlen(den) - 24).
    # Then denn = den >> s2 <= 2^24 - 1.
    max_denn = (1 << 24) - 1
    max_tau = 213
    # numn in [-denn, denn]
    max_D = 2 * max_denn * max_tau + max_denn
    min_D_cand = 2 * max_denn * 27 - max_denn # for tau=27, numn = -denn
    max_N = 512000 * max_denn + max_D // 2

    print(f"Max denn = {max_denn} (bits: {max_denn.bit_length()})")
    print(f"Max D = 2 * denn * 213 + numn = {max_D} (bits: {max_D.bit_length()})")
    print(f"Max N = 512000 * denn + D//2 = {max_N} (bits: {max_N.bit_length()})")
    print(f"LPM_WIDTHN requirement: >= {max_N.bit_length()} bits -> Choose 44 bits")
    print(f"LPM_WIDTHD requirement: >= {max_D.bit_length()} bits -> Choose 34 bits")
    assert max_N.bit_length() <= 44
    assert max_D.bit_length() <= 34

    # -------------------------------------------------------------------------
    # 5. Verification on Golden Synthetic Files
    # -------------------------------------------------------------------------
    print("\n--- 5. Golden Synthetic Files Frame-by-Frame Audit ---")
    files = [
        os.path.join(REPO_DIR, 'golden_v2', 'synth_glide_vuv_16k.wav'),
        os.path.join(REPO_DIR, 'golden_v2', 'synth_glide_vuv_16k_snr5.wav')
    ]

    total_frames = 0
    total_voiced = 0
    max_den_seen = 0
    max_s2_seen = 0
    max_N_seen = 0
    max_D_seen = 0

    for wav_file in files:
        base_name = os.path.basename(wav_file)
        x, _ = read_wav_float(wav_file)
        res = analyse_fixed(x, trace=True)
        frames = res['frames']
        print(f"Auditing {base_name}: {len(frames)} frames...")
        for ifr, fr in enumerate(frames):
            total_frames += 1
            if fr['best'] == 0:
                continue
            best = fr['best']
            U = fr['U']
            um, u0, up = U[best - 1], U[best], U[best + 1]
            num = up - um
            den = 2 * u0 - um - up
            assert den > 0, f"Frame {ifr}: den <= 0!"
            s2 = max(0, den.bit_length() - 24)
            numn, denn = num >> s2, den >> s2
            D_val = 2 * denn * best + numn
            assert D_val > 0, f"Frame {ifr}: D <= 0!"
            N_val = 512000 * denn + D_val // 2
            f0q = N_val // D_val
            assert f0q == fr['f0q_raw'], f"Frame {ifr}: f0q {f0q} != golden {fr['f0q_raw']}"

            if fr['voiced']:
                total_voiced += 1

            if den > max_den_seen:
                max_den_seen = den
            if s2 > max_s2_seen:
                max_s2_seen = s2
            if N_val > max_N_seen:
                max_N_seen = N_val
            if D_val > max_D_seen:
                max_D_seen = D_val

    print(f"Total frames audited: {total_frames}")
    print(f"Total voiced frames: {total_voiced}")
    print(f"Max den observed: {max_den_seen} ({max_den_seen.bit_length()} bits)")
    print(f"Max s2 observed: {max_s2_seen}")
    print(f"Max N observed: {max_N_seen} ({max_N_seen.bit_length()} bits, fits in 44 bits)")
    print(f"Max D observed: {max_D_seen} ({max_D_seen.bit_length()} bits, fits in 34 bits)")
    print("=== [ch09_math_audit] ALL CHAPTER 9 AUDITS PASSED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
