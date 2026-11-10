#!/usr/bin/env python3
"""verify_v3/ch00_table_golden.py
Loads golden_v2/out/*.tsv and computes VDE, GPE, FFE, and fine-cent metrics
(non-gross, i.e. excluding gross pitch errors |f/f_ref - 1| > 0.20, matching
the definition in Section 0.5) using verify_v3/ch00_metrics.py.

Also compares against the gross-included metrics reported in golden_v2/out/compare_report.md
to document the exact relationship.
"""

import os
import sys
import numpy as np

# Ensure verify_v3 is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch00_metrics import compute_metrics

def load_2col(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1]

def load_3col(path):
    data = np.loadtxt(path)
    return data[:, 0], data[:, 1], data[:, 2]

def run_table():
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    out_dir = os.path.join(base_dir, 'golden_v2', 'out')

    # Files for clean
    t_clean, p1_clean = load_2col(os.path.join(out_dir, 'praat_R1.tsv'))
    _, p2_clean = load_2col(os.path.join(out_dir, 'praat_R2.tsv'))
    _, f1_clean = load_2col(os.path.join(out_dir, 'float_R1.tsv'))
    _, f2_clean = load_2col(os.path.join(out_dir, 'float_R2.tsv'))
    _, raw_clean, med_clean = load_3col(os.path.join(out_dir, 'fixed.tsv'))
    truth_clean_all = np.load(os.path.join(out_dir, 'truth_f0.npy'))
    truth_clean = truth_clean_all[np.round(t_clean * 16000 - 0.5).astype(int)]

    # Files for SNR 5 dB
    t_snr5, p1_snr5 = load_2col(os.path.join(out_dir, 'praat_snr5_R1.tsv'))
    _, p2_snr5 = load_2col(os.path.join(out_dir, 'praat_snr5_R2.tsv'))
    _, f1_snr5 = load_2col(os.path.join(out_dir, 'float_snr5_R1.tsv'))
    _, f2_snr5 = load_2col(os.path.join(out_dir, 'float_snr5_R2.tsv'))
    _, raw_snr5, med_snr5 = load_3col(os.path.join(out_dir, 'fixed_snr5.tsv'))
    truth_snr5_all = np.load(os.path.join(out_dir, 'truth_f0_snr5.npy'))
    truth_snr5 = truth_snr5_all[np.round(t_snr5 * 16000 - 0.5).astype(int)]

    clean_comparisons = [
        ('Port float vs Praat R2', p2_clean, f2_clean),
        ('Port float vs Praat R1', p1_clean, f1_clean),
        ('Praat R1 vs Praat R2', p2_clean, p1_clean),
        ('Twin (trước median) vs Praat R2', p2_clean, raw_clean),
        ('Twin + median-3 vs Praat R1', p1_clean, med_clean),
        ('Praat R1 vs Ground-Truth', truth_clean, p1_clean),
        ('Twin + median-3 vs Ground-Truth', truth_clean, med_clean),
    ]

    snr5_comparisons = [
        ('Port float vs Praat R2', p2_snr5, f2_snr5),
        ('Port float vs Praat R1', p1_snr5, f1_snr5),
        ('Praat R1 vs Praat R2 (Viterbi)', p2_snr5, p1_snr5),
        ('Twin (trước median) vs Praat R2', p2_snr5, raw_snr5),
        ('Twin + median-3 vs Praat R1', p1_snr5, med_snr5),
        ('Praat R1 vs Ground-Truth', truth_snr5, p1_snr5),
        ('Praat R2 vs Ground-Truth', truth_snr5, p2_snr5),
        ('Twin (trước median) vs Ground-Truth', truth_snr5, raw_snr5),
        ('Twin + median-3 vs Ground-Truth', truth_snr5, med_snr5),
    ]

    print("==========================================================================================")
    print("GOLDEN V2 RESULTS RECOMPUTED WITH FINE CENTS (NON-GROSS)")
    print("Note: compare_report.md's 'mean abs/p95' columns include gross frames (>20% / ~316 cents).")
    print("This table uses FINE cents (excluding gross frames), matching the Section 0.5 definition.")
    print("==========================================================================================")

    for title, comps in [("Tín hiệu sạch (Clean synth, 208 khung cùng hữu thanh)", clean_comparisons),
                         ("Tín hiệu có ồn SNR 5 dB (207 khung cùng hữu thanh)", snr5_comparisons)]:
        print(f"\n--- {title} ---")
        print(f"{'Phép so sánh':38s} | {'VDE':7s} | {'GPE':7s} | {'FFE':6s} | {'Fine TB':8s} | {'Fine p95':8s} | {'Fine Max':8s} | {'All TB':8s} | {'All p95':8s}")
        print("-" * 115)
        for name, ref, test in comps:
            res = compute_metrics(ref, test)
            vde_str = f"{res['vde_count']}/{res['frames']}"
            gpe_str = f"{res['gpe_count']}/{res['both_voiced']}"
            ffe_str = f"{res['ffe_rate']:.4f}"
            
            # Formatting fine cents
            if res['fine_max_cents'] < 1e-3 and res['fine_max_cents'] > 0:
                ftb = f"{res['fine_mean_abs_cents']:.1e}"
                fp95 = f"{res['fine_p95_cents']:.1e}"
                fmax = f"{res['fine_max_cents']:.1e}"
            else:
                ftb = f"{res['fine_mean_abs_cents']:.2f}"
                fp95 = f"{res['fine_p95_cents']:.2f}"
                fmax = f"{res['fine_max_cents']:.2f}"

            all_tb = f"{res['all_mean_abs_cents']:.2f}"
            all_p95 = f"{res['all_p95_cents']:.2f}"

            print(f"{name:38s} | {vde_str:7s} | {gpe_str:7s} | {ffe_str:6s} | {ftb:8s} | {fp95:8s} | {fmax:8s} | {all_tb:8s} | {all_p95:8s}")

if __name__ == '__main__':
    run_table()
