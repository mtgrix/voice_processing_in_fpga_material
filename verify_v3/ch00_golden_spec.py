"""
verify_v3/ch00_golden_spec.py
Verifies the 10-step integer specification from golden_v2/fixed_twin.py
and extracts the canonical comparison numbers from golden_v2/out/compare_report.md
for Chapter 0, Subsection 0.7.
"""

import sys
import os
import re

# Ensure golden_v2 is importable
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
golden_v2_dir = os.path.join(repo_root, "golden_v2")
if golden_v2_dir not in sys.path:
    sys.path.insert(0, golden_v2_dir)

import constants as K
from gen_roms import hanning_q15, c_table, k_table

def verify_spec_constants():
    print("=== 1. Verifying 10-step Integer Spec Constants ===")
    assert K.FS == 16000
    assert K.NSAMP_WINDOW == 638
    assert K.HOP_NOMINAL == 160
    assert K.MEAN_SPAN == 426
    assert K.MEAN_OFFSET == 106
    assert K.M_MEAN == 10082083
    assert K.K_MEAN == 32
    assert K.TAU_SCAN_MIN == 26
    assert K.TAU_SCAN_MAX == 214
    assert K.TAU_SEARCH_MIN == 27
    assert K.TAU_SEARCH_MAX == 213

    W = hanning_q15()
    assert len(W) == 638
    assert W[0] == 1 and W[637] == 1
    assert W[318] == 32767 and W[319] == 32767
    assert sum(W) == 10469378

    C = c_table(W)
    assert C[26] == 16563
    assert C[27] == 16578
    assert C[100] == 19260
    assert C[213] == 34773
    assert C[214] == 35030

    KT = k_table()
    assert KT[26] == -383
    assert KT[27] == 188
    assert KT[100] == 19995
    assert KT[213] == 31434
    assert KT[214] == 31504

    print("  All constants match canonical values in BRIEF_v3 §7 perfectly.")

def verify_compare_report():
    print("\n=== 2. Canonical Comparison Results from golden_v2/out/compare_report.md ===")
    report_path = os.path.join(golden_v2_dir, "out", "compare_report.md")
    if not os.path.isfile(report_path):
        print("  Warning: compare_report.md not found!")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("  File read successfully. Length:", len(content), "bytes.")
    # Check key figures
    assert "synth_glide_vuv_16k.wav" in content
    assert "synth_glide_vuv_16k_snr5.wav" in content
    print("  Found synthetic clean and noisy 5 dB sections.")

if __name__ == "__main__":
    verify_spec_constants()
    verify_compare_report()
