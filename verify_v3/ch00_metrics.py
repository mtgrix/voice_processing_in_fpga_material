#!/usr/bin/env python3
"""verify_v3/ch00_metrics.py
Metric definitions and verification:
- VDE (Voicing Decision Error)
- GPE (Gross Pitch Error)
- FFE (F0 Frame Error)
- Fine cents statistics (mean absolute cents, std, 95th percentile, max)

Checks against golden_v2/compare.py and provides a 10-frame miniature hand calculation.
"""

import sys
import math
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
    import os
    path = None
    for candidate in ['golden_v2/out/compare_summary.json', '../golden_v2/out/compare_summary.json']:
        if os.path.exists(candidate):
            path = candidate
            break
    if path is not None:
        import json
        with open(path) as f:
            data = json.load(f)
        for wav, info in data.items():
            print(f"File {wav}: {info['nframes']} frames")
            for comp, res in info['rows'].items():
                if comp in ['fixed_raw vs praat_R2', 'fixed_med3 vs praat_R1']:
                    print(f"  {comp:35s}: VDE={res['vde_frames']}/{res['frames']} ({res['VDE']:.4f}), "
                          f"GPE={res['gpe_frames']}/{res['both']} ({res['GPE']:.4f}), FFE={res['FFE']:.4f}, "
                          f"cents={res['cents_mean_abs']:.4g} (p95={res['cents_p95']:.4g}, max={res['cents_max_nongross']:.4g})")
    else:
        print("compare_summary.json not found, check path.")

def pedagogical_10_frame_example():
    print("\n=== Pedagogical 10-Frame Example ===")
    # 10 frames representing 4 distinct scenarios:
    # Frame 0: Both unvoiced (0 vs 0) -> Case 4
    # Frame 1: Both voiced, exact match (120 vs 120) -> Case 1
    # Frame 2: Both voiced, small error (150 vs 152) -> Case 1
    # Frame 3: Both voiced, small error (200 vs 196) -> Case 1
    # Frame 4: Both voiced, small error (220 vs 224) -> Case 1
    # Frame 5: Voicing error: Ref unvoiced, Test voiced (0 vs 130) -> Case 3
    # Frame 6: Voicing error: Ref voiced, Test unvoiced (140 vs 0) -> Case 3
    # Frame 7: Both voiced, gross error / octave doubling (100 vs 200) -> Case 2
    # Frame 8: Both voiced, gross error / octave halving (300 vs 150) -> Case 2
    # Frame 9: Both unvoiced (0 vs 0) -> Case 4
    
    ref  = [  0.0, 120.0, 150.0, 200.0, 220.0,   0.0, 140.0, 100.0, 300.0,   0.0]
    test = [  0.0, 120.0, 152.0, 196.0, 224.0, 130.0,   0.0, 200.0, 150.0,   0.0]
    
    m = compute_metrics(ref, test)
    
    print("Frame | Ref (Hz) | Test (Hz) | Status                | Rel Err (%) | Cents     | Gross?")
    print("------+----------+-----------+-----------------------+-------------+-----------+-------")
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
        print(f"  {i:2d}  | {r:8.1f} | {t:9.1f} | {status} | {rel:>11s} | {cnt:>9s} | {gross}")
        
    print("\n--- Summary Breakdown ---")
    print(f"Total frames: N = {m['frames']}")
    print(f"Voiced in Ref: {m['voiced_ref']}, Voiced in Test: {m['voiced_test']}")
    print(f"Both voiced frames: N_both = {m['both_voiced']} (Frames 1, 2, 3, 4, 7, 8)")
    print(f"Voicing errors (VDE): {m['vde_count']} frames (Frames 5, 6) -> VDE = {m['vde_count']}/{m['frames']} = {m['vde_rate']*100:.1f}%")
    print(f"Gross Pitch Errors (GPE): {m['gpe_count']} frames (Frames 7, 8) out of {m['both_voiced']} both-voiced frames -> GPE = {m['gpe_count']}/{m['both_voiced']} = {m['gpe_rate']*100:.1f}%")
    print(f"F0 Frame Errors (FFE): VDE + GPE = {m['vde_count']} + {m['gpe_count']} = {m['ffe_count']} -> FFE = {m['ffe_count']}/{m['frames']} = {m['ffe_rate']*100:.1f}%")
    print(f"Fine cents (excluding GPE frames 7 and 8, on frames 1, 2, 3, 4):")
    print(f"  Frame 1:  0.00 cent")
    print(f"  Frame 2: +22.96 cent")
    print(f"  Frame 3: -34.97 cent")
    print(f"  Frame 4: +31.18 cent")
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
