#!/usr/bin/env python3
"""verify_v3/ch00_metrics.py
Metric definitions and verification:
- VDE (Voicing Decision Error)
- GPE (Gross Pitch Error)
- FFE (F0 Frame Error)
- Fine cents statistics (mean absolute cents, std, 95th percentile, max)

Checks against golden_v2/out/*.tsv and compare_summary.json, and provides a 10-frame miniature hand calculation.
"""

import os
import sys
import math
import json
import numpy as np

def compute_metrics(ref, test):
    """Compute VDE, GPE, FFE, and cents metrics between ref and test sequences.
    0 means unvoiced; > 0 means voiced frequency in Hz.
    """
    ref = np.asarray(ref, dtype=float)
    test = np.asarray(test, dtype=float)
    assert len(ref) == len(test), "Sequences must have the same length"
    n = len(ref)
    
    vr = ref > 0
    vt = test > 0
    both = vr & vt
    
    # 1. VDE: fraction of frames where voicing decision differs
    vde_diff = vr != vt
    vde_count = int(np.sum(vde_diff))
    vde_rate = vde_count / n
    
    # 2. GPE: among frames voiced in BOTH, fraction where |test/ref - 1| > 0.20
    both_count = int(np.sum(both))
    if both_count > 0:
        rel_err = np.abs(test[both] / ref[both] - 1.0)
        gross_mask = rel_err > 0.20
        gpe_count = int(np.sum(gross_mask))
        gpe_rate = gpe_count / both_count
        
        # 3. Fine cents on non-gross frames (where rel_err <= 0.20)
        cents = 1200.0 * np.log2(test[both] / ref[both])
        abs_cents = np.abs(cents)
        
        # Non-gross mask
        fine_mask = ~gross_mask
        fine_count = int(np.sum(fine_mask))
        if fine_count > 0:
            fine_abs_cents = abs_cents[fine_mask]
            fine_cents = cents[fine_mask]
            cents_mean_abs = float(np.mean(fine_abs_cents))
            cents_std = float(np.std(fine_cents))
            cents_p95 = float(np.percentile(fine_abs_cents, 95))
            cents_max = float(np.max(fine_abs_cents))
        else:
            cents_mean_abs = cents_std = cents_p95 = cents_max = 0.0
            
        all_cents_mean_abs = float(np.mean(abs_cents))
        all_cents_p95 = float(np.percentile(abs_cents, 95))
        all_cents_max = float(np.max(abs_cents))
    else:
        gpe_count = 0
        gpe_rate = 0.0
        cents_mean_abs = cents_std = cents_p95 = cents_max = 0.0
        all_cents_mean_abs = all_cents_p95 = all_cents_max = 0.0
        
    # 4. FFE: (vde_count + gpe_count) / n
    ffe_rate = (vde_count + gpe_count) / n
    
    return {
        'frames': n,
        'voiced_ref': int(np.sum(vr)),
        'voiced_test': int(np.sum(vt)),
        'both_voiced': both_count,
        'vde_count': vde_count,
        'vde_rate': vde_rate,
        'gpe_count': gpe_count,
        'gpe_rate': gpe_rate,
        'ffe_count': vde_count + gpe_count,
        'ffe_rate': ffe_rate,
        'fine_mean_abs_cents': cents_mean_abs,
        'fine_std_cents': cents_std,
        'fine_p95_cents': cents_p95,
        'fine_max_cents': cents_max,
        'all_mean_abs_cents': all_cents_mean_abs,
        'all_p95_cents': all_cents_p95,
        'all_max_cents': all_cents_max,
    }

def verify_against_golden():
    print("=== Verifying against golden_v2 compare results ===")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    golden_dir = os.path.join(base_dir, '..', 'golden_v2', 'out')
    json_path = os.path.join(golden_dir, 'compare_summary.json')

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path) as f:
        js_data = json.load(f)

    # Helper loaders
    def load_2col(name):
        d = np.loadtxt(os.path.join(golden_dir, name))
        return d[:, 0], d[:, 1]

    def load_3col(name):
        d = np.loadtxt(os.path.join(golden_dir, name))
        return d[:, 0], d[:, 1], d[:, 2]

    # Clean file
    t_clean, p1_clean = load_2col('praat_R1.tsv')
    _, p2_clean = load_2col('praat_R2.tsv')
    _, f1_clean = load_2col('float_R1.tsv')
    _, f2_clean = load_2col('float_R2.tsv')
    _, raw_clean, med_clean = load_3col('fixed.tsv')
    truth_clean = np.load(os.path.join(golden_dir, 'truth_f0.npy'))[np.round(t_clean * 16000 - 0.5).astype(int)]

    # SNR 5 dB file
    t_snr5, p1_snr5 = load_2col('praat_snr5_R1.tsv')
    _, p2_snr5 = load_2col('praat_snr5_R2.tsv')
    _, f1_snr5 = load_2col('float_snr5_R1.tsv')
    _, f2_snr5 = load_2col('float_snr5_R2.tsv')
    _, raw_snr5, med_snr5 = load_3col('fixed_snr5.tsv')
    truth_snr5 = np.load(os.path.join(golden_dir, 'truth_f0_snr5.npy'))[np.round(t_snr5 * 16000 - 0.5).astype(int)]

    files_map = {
        'synth_glide_vuv_16k.wav': {
            'float_R2 vs praat_R2': (p2_clean, f2_clean),
            'float_R1 vs praat_R1': (p1_clean, f1_clean),
            'praat_R1 vs praat_R2 (path-finder effect)': (p2_clean, p1_clean),
            'fixed_raw vs praat_R2': (p2_clean, raw_clean),
            'fixed_raw vs float_R2': (f2_clean, raw_clean),
            'fixed_med3 vs praat_R1': (p1_clean, med_clean),
            'praat_R1 vs truth': (truth_clean, p1_clean),
        },
        'synth_glide_vuv_16k_snr5.wav': {
            'float_R2 vs praat_R2': (p2_snr5, f2_snr5),
            'float_R1 vs praat_R1': (p1_snr5, f1_snr5),
            'praat_R1 vs praat_R2 (path-finder effect)': (p2_snr5, p1_snr5),
            'fixed_raw vs praat_R2': (p2_snr5, raw_snr5),
            'fixed_raw vs float_R2': (f2_snr5, raw_snr5),
            'fixed_med3 vs praat_R1': (p1_snr5, med_snr5),
            'praat_R1 vs truth': (truth_snr5, p1_snr5),
            'praat_R2 vs truth': (truth_snr5, p2_snr5),
            'fixed_raw vs truth': (truth_snr5, raw_snr5),
            'fixed_med3 vs truth': (truth_snr5, med_snr5),
        }
    }

    print("Running compute_metrics() on golden TSV files and asserting against compare_summary.json:")
    print("Note: compare.py's cents_mean_abs and cents_p95 include gross pitch error frames,")
    print("while compute_metrics() fine-cent metrics exclude gross frames by design (Section 0.5).\n")

    for wav, rows in files_map.items():
        print(f"File {wav}:")
        js_rows = js_data[wav]['rows']
        for row_name, (ref, test) in rows.items():
            res = compute_metrics(ref, test)
            jres = js_rows[row_name]

            # Assert VDE count, GPE count, FFE rate, and max non-gross cents
            assert res['vde_count'] == jres['vde_frames'], f"VDE mismatch for {row_name}: {res['vde_count']} != {jres['vde_frames']}"
            assert res['gpe_count'] == jres['gpe_frames'], f"GPE mismatch for {row_name}: {res['gpe_count']} != {jres['gpe_frames']}"
            assert abs(res['ffe_rate'] - jres['FFE']) < 1e-6, f"FFE mismatch for {row_name}: {res['ffe_rate']} != {jres['FFE']}"
            assert abs(res['fine_max_cents'] - jres['cents_max_nongross']) < 1e-4, f"Max cents mismatch for {row_name}: {res['fine_max_cents']} != {jres['cents_max_nongross']}"

            print(f"  [PASS] {row_name:38s}: VDE={res['vde_count']}/{res['frames']}, GPE={res['gpe_count']}/{res['both_voiced']}, FFE={res['ffe_rate']:.4f}, fine_max={res['fine_max_cents']:.4g} (JSON max={jres['cents_max_nongross']:.4g})")
            if res['gpe_count'] > 0:
                print(f"         (gross frames present: fine_mean={res['fine_mean_abs_cents']:.2f} vs report gross-included mean={jres['cents_mean_abs']:.2f})")

def pedagogical_10_frame_example():
    print("\n=== Pedagogical 10-Frame Example ===")
    ref  = [  0.0, 120.0, 150.0, 200.0, 220.0,   0.0, 140.0, 100.0, 300.0,   0.0]
    test = [  0.0, 120.0, 152.0, 196.0, 224.0, 130.0,   0.0, 200.0, 150.0,   0.0]
    
    m = compute_metrics(ref, test)
    
    print("Frame | Ref (Hz) | Test (Hz) | Status                | Rel Err (%) | Cents     | Gross?")
    print("------+----------+-----------+-----------------------+-------------+-----------+-------")
    computed_cents = {}
    for i in range(10):
        r, t = ref[i], test[i]
        vr, vt = r > 0, t > 0
        if not vr and not vt:
            status = "Both unvoiced (UV)   "
            rel = "-"
            cnt = "-"
            gross = "No"
        elif vr != vt:
            status = "Voicing error (V/UV) "
            rel = "-"
            cnt = "-"
            gross = "VDE"
        else: # both voiced
            err = abs(t / r - 1.0)
            c = 1200.0 * math.log2(t / r)
            is_g = err > 0.20
            status = "Both voiced (V)      "
            rel = f"{err*100:6.2f}%"
            cnt = f"{c:+8.2f}"
            gross = "YES (GPE)" if is_g else "No (fine)"
            computed_cents[i] = c
        print(f"  {i:2d}  | {r:8.1f} | {t:9.1f} | {status} | {rel:>11s} | {cnt:>9s} | {gross}")
        
    print("\n--- Summary Breakdown ---")
    print(f"Total frames: N = {m['frames']}")
    print(f"Voiced in Ref: {m['voiced_ref']}, Voiced in Test: {m['voiced_test']}")
    print(f"Both voiced frames: N_both = {m['both_voiced']} (Frames 1, 2, 3, 4, 7, 8)")
    print(f"Voicing errors (VDE): {m['vde_count']} frames (Frames 5, 6) -> VDE = {m['vde_count']}/{m['frames']} = {m['vde_rate']*100:.1f}%")
    print(f"Gross Pitch Errors (GPE): {m['gpe_count']} frames (Frames 7, 8) out of {m['both_voiced']} both-voiced frames -> GPE = {m['gpe_count']}/{m['both_voiced']} = {m['gpe_rate']*100:.1f}%")
    print(f"F0 Frame Errors (FFE): VDE + GPE = {m['vde_count']} + {m['gpe_count']} = {m['ffe_count']} -> FFE = {m['ffe_count']}/{m['frames']} = {m['ffe_rate']*100:.1f}%")
    print(f"Fine cents (excluding GPE frames 7 and 8, on frames 1, 2, 3, 4):")
    print(f"  Frame 1: {computed_cents[1]:+6.2f} cent")
    print(f"  Frame 2: {computed_cents[2]:+6.2f} cent")
    print(f"  Frame 3: {computed_cents[3]:+6.2f} cent")
    print(f"  Frame 4: {computed_cents[4]:+6.2f} cent")
    print(f"  Mean absolute cents: {m['fine_mean_abs_cents']:.2f} cent")
    print(f"  Std of cents: {m['fine_std_cents']:.2f} cent")
    print(f"  95th percentile: {m['fine_p95_cents']:.2f} cent")
    print(f"  Max fine cent error: {m['fine_max_cents']:.2f} cent")
    
    print("\nExplanation of 20% threshold:")
    cent_20_pct = 1200 * math.log2(1.20)
    semitones = 12 * math.log2(1.20)
    print(f"20% frequency ratio: 1200 * log2(1.20) = {cent_20_pct:.2f} cents = {semitones:.2f} semitones.")
    print("Why exclude gross errors from fine-cent statistics?")
    print("An octave error (2x) is 1200 cents! If included, a single octave error would distort the mean cent error from 22 cents to hundreds of cents, hiding the true precision of the fine interpolation algorithm.")

if __name__ == '__main__':
    verify_against_golden()
    pedagogical_10_frame_example()
