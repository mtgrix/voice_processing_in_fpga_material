#!/usr/bin/env python3
"""verify_v3/ch10_golden_audit.py

Audits the golden_v2 dataset for Chapter 10:
1. Loads the two synthetic 16 kHz WAV files:
   - synth_glide_vuv_16k.wav (clean)
   - synth_glide_vuv_16k_snr5.wav (noisy SNR 5 dB)
2. Runs fixed_twin.py and praat_float_ref.py (R2 mode: octave-jump = 0, V/UV = 0).
3. Verifies VDE (Voicing Decision Error):
   - On clean file: VDE = 0 / 277 frames (0.0000%)
   - On noisy file: VDE = 0 / 277 frames (0.0000%)
4. Verifies frame-by-frame equivalence between the cross-multiplied integer inequality
   and the floating-point inequality:
   (100*Sc - 45*R0n) * 3 * GP > 100 * R0n * max(0, 6*GP - 145*LP)
   vs
   (Sc / R0n) > 0.45 + max(0, 2 - (LP/GP) * 145 / 3)
5. Reports globalPeak (GP), min/max localPeak (LP), number of voiced/unvoiced frames.
"""

import sys
import os
import wave
import numpy as np

# Add golden_v2 to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN_DIR = os.path.join(os.path.dirname(BASE_DIR), "golden_v2")
sys.path.insert(0, GOLDEN_DIR)

import constants as K
import fixed_twin
from praat_float_ref import PraatRawAc, read_wav_float
import frames

def audit_file(filename):
    filepath = os.path.join(GOLDEN_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}")
        return

    print("=" * 75)
    print(f"AUDITING FILE: {filename}")
    print("=" * 75)

    xi, z = read_wav_float(filepath)
    fs = K.FS
    n_samples = len(xi)
    duration = n_samples / fs
    print(f"Samples: {n_samples}, Duration: {duration:.4f} s, FS: {fs} Hz")

    # 1. HPS globalPeak calculation
    gp_int = fixed_twin.global_peak(xi)
    # Praat float globalPeak
    mean_val = float(np.mean(xi))
    gp_float = float(np.max(np.abs(xi - mean_val)))
    print(f"GlobalPeak: integer GP = {gp_int}, float GP = {gp_float:.4f}")

    # 2. Frame grid
    t_mid, times, lefts = frames.frame_grid(n_samples)
    n_frames = len(times)
    starts = [frames.window_start0(l) for l in lefts]
    print(f"Total frames: {n_frames}, First window start: {starts[0]}, Hop: 160")

    # 3. Analyze with fixed_twin
    res_fixed = fixed_twin.analyse_fixed(xi, trace=True)
    f0q_fixed = res_fixed['f0q']
    voiced_fixed = [1 if v > 0 else 0 for v in f0q_fixed]

    # 4. Analyze with praat_float_ref (R2 mode)
    # R2 mode: octave_jump = 0.0, vuv = 0.0
    _, f2_float, _ = PraatRawAc(octave_jump=0.0, vuv=0.0).analyse(z)
    voiced_r2 = [1 if f0 > 0.0 else 0 for f0 in f2_float]

    # 5. Calculate VDE
    vde_count = sum(1 for vf, vr in zip(voiced_fixed, voiced_r2) if vf != vr)
    vde_rate = vde_count / n_frames
    n_voiced_fixed = sum(voiced_fixed)
    n_voiced_r2 = sum(voiced_r2)

    print(f"\nVoicing Decision Summary:")
    print(f"    Total frames: {n_frames}")
    print(f"    Voiced frames (Fixed): {n_voiced_fixed}")
    print(f"    Voiced frames (Praat R2): {n_voiced_r2}")
    print(f"    VDE count: {vde_count} / {n_frames}")
    print(f"    VDE rate: {vde_rate * 100:.4f} %")

    # 6. Verify cross-multiplied formula vs floating-point formula frame by frame
    mismatches = 0
    lp_values = []
    ramp_frames = 0
    silence_frames = 0
    active_frames = 0

    for idx, f in enumerate(res_fixed['frames']):
        lp = f['lp']
        lp_values.append(lp)
        r0 = f['r0']
        sh = f['sh']
        r0n = r0 >> sh if r0 > 0 else 0
        sc = f['sc']
        cand_found = (f['best'] > 0)

        # Cross-multiplication evaluation
        if r0 == 0 or lp == 0 or gp_int == 0 or not cand_found:
            ineq_fixed = False
        else:
            term1 = (100 * sc - 45 * r0n) * 3 * gp_int
            term2 = 100 * r0n * max(0, 6 * gp_int - 145 * lp)
            ineq_fixed = (term1 > term2)

        # Float evaluation
        if gp_int > 0 and r0n > 0 and lp > 0 and cand_found:
            I = lp / gp_int
            r_unv = 0.45 + max(0.0, 2.0 - I * 145.0 / 3.0)
            ineq_float = ((sc / r0n) > r_unv)
        else:
            I = 0.0
            ineq_float = False

        if I < 0.03:
            silence_frames += 1
        elif I < 6.0 / 145.0:
            ramp_frames += 1
        else:
            active_frames += 1

        if ineq_fixed != ineq_float:
            mismatches += 1
            print(f"    [!] Mismatch at frame {idx}: fixed={ineq_fixed}, float={ineq_float}")

    print(f"\nFormula Equivalence Verification:")
    print(f"    Frames in strict silence (I < 0.03): {silence_frames}")
    print(f"    Frames in ramp region (0.03 <= I < 0.0414): {ramp_frames}")
    print(f"    Frames in active region (I >= 0.0414): {active_frames}")
    print(f"    LP range: min={min(lp_values)}, max={max(lp_values)}")
    print(f"    Cross-multiplication vs Float mismatches: {mismatches} / {n_frames}")

    assert vde_count == 0, f"Expected VDE == 0, got {vde_count}!"
    assert mismatches == 0, f"Expected 0 mismatches, got {mismatches}!"
    print(f"[+] VDE == 0 and integer inequality equivalence verified successfully!\n")

def main():
    print("=" * 75)
    print("GOLDEN V2 VOICING AUDIT (CHAPTER 10)")
    print("=" * 75)
    audit_file("synth_glide_vuv_16k.wav")
    audit_file("synth_glide_vuv_16k_snr5.wav")

if __name__ == '__main__':
    main()
