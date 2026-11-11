#!/usr/bin/env python3
"""verify_v3/ch06_stress_audit.py

Detailed mathematical and dynamic range audit of the 17-bit signed datapath
for Chapter 6:
- Derives the theoretical extremes of d = x - mean: [-65535, +65535]
- Demonstrates catastrophic overflow of 16-bit datapath on full-scale stress frames
- Reproduces exact stress frame results from golden_v2/hdl_check/ (max |xw| = 59379)
- Analyzes hand-calculated values for sample n = 318 in stress frame a
"""

import math
import os
import sys
import numpy as np

# Ensure golden_v2 is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN_V2_DIR = os.path.join(CURRENT_DIR, "..", "golden_v2")
sys.path.insert(0, GOLDEN_V2_DIR)

import constants as K
import gen_vectors
from fixed_twin import frame_fixed, W


def audit_stress_frames():
    print("=" * 78)
    print("CH06 STRESS FRAME AUDIT: 17-BIT SIGNED DATAPATH JUSTIFICATION")
    print("=" * 78)

    # 1. Theoretical bounds of d = x - mean
    # x in [-32768, 32767], mean in [-32768, 32767]
    d_max = 32767 - (-32768)  # +65535
    d_min = -32768 - 32767    # -65535
    print(f"Theoretical maximum d = x - mean : +{d_max} (0x{d_max:04X})")
    print(f"Theoretical minimum d = x - mean : {d_min} (-0x{abs(d_min):04X})")
    print(f"16-bit signed integer range       : [-32768, +32767]")
    print(f"17-bit signed integer range       : [-65536, +65535]")
    print(f"Bit-width requirement for d       : 17 bits signed (Q16.0s)\n")

    # 2. Reproduce stress frames from golden_v2
    # Stress frame a: full-scale pulse in center, background -32768
    raw_a = np.full(K.NSAMP_WINDOW, -32768, dtype=np.int64)
    raw_a[300:340] = 32767  # 40 positive samples

    # Stress frame b: alternating square wave
    raw_b = np.where((np.arange(K.NSAMP_WINDOW) // 27) % 2 == 0, 32767, -32768).astype(np.int64)
    raw_b[100:300] = -32768

    fa = frame_fixed(raw_a, 32767, trace=True)
    fb = frame_fixed(raw_b, 32767, trace=True)

    print("Stress Frame A Evaluation:")
    print(f"  Mean span indices             : {K.MEAN_OFFSET} .. {K.MEAN_OFFSET + K.MEAN_SPAN - 1} (426 samples)")
    print(f"  Computed local mean           : {fa['mean']} (Agenda verified: -26614)")
    max_d_a = max(v - fa['mean'] for v in raw_a)
    min_d_a = min(v - fa['mean'] for v in raw_a)
    max_xw_a = max(fa['xw'])
    min_xw_a = min(fa['xw'])
    abs_max_xw_a = max(abs(v) for v in fa['xw'])
    print(f"  Difference range d = x - mean : [{min_d_a}, {max_d_a}]")
    print(f"  Windowed xw range             : [{min_xw_a}, {max_xw_a}]")
    print(f"  Max absolute |xw|             : {abs_max_xw_a} (Agenda verified: 59379)")
    assert abs_max_xw_a == 59379, f"Stress frame max |xw| mismatch: {abs_max_xw_a} != 59379"

    print("\nStress Frame B Evaluation:")
    print(f"  Computed local mean           : {fb['mean']}")
    max_d_b = max(v - fb['mean'] for v in raw_b)
    min_d_b = min(v - fb['mean'] for v in raw_b)
    abs_max_xw_b = max(abs(v) for v in fb['xw'])
    print(f"  Difference range d = x - mean : [{min_d_b}, {max_d_b}]")
    print(f"  Max absolute |xw|             : {abs_max_xw_b}")

    # 3. Detailed trace of sample n = 318 in Stress Frame A
    n = 318
    x_val = raw_a[n]
    mean_val = fa['mean']
    d_val = x_val - mean_val
    w_val = W[n]
    p_full = d_val * w_val
    xw_val = (p_full + 16384) >> 15

    print("\n" + "-" * 78)
    print(f"DETAILED WALKTHROUGH FOR SAMPLE n = {n} IN STRESS FRAME A:")
    print("-" * 78)
    print(f"  Raw audio sample x[{n}]       : {x_val} (0x{x_val & 0xFFFF:04X})")
    print(f"  Local mean                   : {mean_val} (0x{mean_val & 0xFFFF:04X})")
    print(f"  Difference d = x - mean      : {d_val} (0x{d_val & 0x1FFFF:05X}, 17 bits)")
    print(f"  16-bit truncated d           : {(d_val + 32768) % 65536 - 32768} (FATAL OVERFLOW to NEGATIVE!)")
    print(f"  Hanning window w[{n}]        : {w_val} (0x{w_val:04X}, Q1.15)")
    print(f"  Full product p = d * w       : {p_full} (0x{p_full & 0x3FFFFFFFF:09X}, 34 bits)")
    print(f"  Rounded (p + 2^14) >> 15     : {xw_val} (Agenda verified: 59379)")
    print(f"  16-bit truncated xw          : {(xw_val + 32768) % 65536 - 32768} (FATAL OVERFLOW to NEGATIVE!)")
    print("-" * 78)
    print("Conclusion: 17-bit signed representation is MATHEMATICALLY MANDATORY.")
    print("=" * 78)


if __name__ == "__main__":
    audit_stress_frames()
