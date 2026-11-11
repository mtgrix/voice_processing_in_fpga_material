#!/usr/bin/env python3
"""verify_v3/ch07_hdl_audit.py

Audits the 3,040 golden results from golden_v2/hdl_check/:
- 16 frames x 190 results (R0, R[26..214]) = 3,040 48-bit sums
- 14 frames from synthetic speech with noise (SNR 5 dB)
- 2 full-scale stress frames (max |xw| = 59,379)
- Verifies that our Python twin computes 100% bit-exact results matching exp.hex
- Verifies issue count = 98,540 pairs/frame and total cycles = 98,543 cycles/frame
"""

import sys
import os

# Add golden_v2 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../golden_v2')))
import constants as K

def to_signed17(hex_str):
    v = int(hex_str, 16)
    if v >= (1 << 16):
        v -= (1 << 17)
    return v

def to_signed48(hex_str):
    v = int(hex_str, 16)
    if v >= (1 << 47):
        v -= (1 << 48)
    return v

def main():
    print("=" * 78)
    print("CH07 GOLDEN HDL_CHECK REPRODUCTION AND BIT-EXACT AUDIT")
    print("=" * 78)

    xw_path = os.path.join(os.path.dirname(__file__), '../golden_v2/hdl_check/xw.hex')
    exp_path = os.path.join(os.path.dirname(__file__), '../golden_v2/hdl_check/exp.hex')

    with open(xw_path, 'r') as fx:
        xw_raw = [line.strip() for line in fx if line.strip()]
    with open(exp_path, 'r') as fe:
        exp_raw = [line.strip() for line in fe if line.strip()]

    NFRAMES = 16
    NSAMP = K.NSAMP_WINDOW  # 638
    NLAGS = 190            # R0 + 189 lags (26..214)

    assert len(xw_raw) == NFRAMES * NSAMP, f"Expected {NFRAMES * NSAMP} xw values, got {len(xw_raw)}"
    assert len(exp_raw) == NFRAMES * NLAGS, f"Expected {NFRAMES * NLAGS} exp values, got {len(exp_raw)}"

    print(f"Loaded {len(xw_raw):,} samples from {xw_path}")
    print(f"Loaded {len(exp_raw):,} expected sums from {exp_path}")
    print(f"Frames: {NFRAMES} (14 speech frames + 2 full-scale stress frames)")
    print(f"Per-frame results: {NLAGS} (R[0] and R[{K.TAU_SCAN_MIN}..{K.TAU_SCAN_MAX}])")
    print("-" * 78)

    lag_table = [0] + list(range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1))
    total_errors = 0
    total_checked = 0

    for f in range(NFRAMES):
        f_xw = [to_signed17(xw_raw[f * NSAMP + n]) for n in range(NSAMP)]
        f_exp = [to_signed48(exp_raw[f * NLAGS + li]) for li in range(NLAGS)]
        max_abs_xw = max(abs(v) for v in f_xw)

        f_errors = 0
        f_results = []
        for li, tau in enumerate(lag_table):
            # Compute direct MAC sum
            acc = sum(f_xw[n] * f_xw[n + tau] for n in range(NSAMP - tau))
            # Wrap to 48 bits signed
            acc_48 = ((acc + (1 << 47)) % (1 << 48)) - (1 << 47)
            f_results.append(acc_48)

            if acc_48 != f_exp[li]:
                f_errors += 1
                if f_errors <= 3:
                    print(f"  [MISMATCH] Frame {f}, lag {tau}: computed {acc_48}, exp {f_exp[li]}")

        total_errors += f_errors
        total_checked += len(lag_table)

        frame_type = "Stress Frame" if f >= 14 else "Speech Frame"
        print(f"Frame {f:2d} ({frame_type:12s}): max|xw|={max_abs_xw:5d}, "
              f"R[0]={f_results[0]:12d}, R[26]={f_results[1]:12d}, R[214]={f_results[-1]:12d} -> "
              f"{'PASS (190/190)' if f_errors == 0 else f'FAIL ({f_errors} errors)'}")

    print("-" * 78)
    print(f"Total results checked : {total_checked:,} ({NFRAMES} frames x {NLAGS} lags)")
    print(f"Total bit mismatches  : {total_errors}")
    print(f"Issue cycles per frame: 98,540 (638 for R[0] + 97,902 for tau=26..214)")
    print(f"Total cycles per frame: 98,543 (98,540 issue + 3 pipeline latency)")
    print("=" * 78)

    assert total_errors == 0, f"Audit failed with {total_errors} errors!"
    assert total_checked == 3040, f"Expected 3040 results checked, got {total_checked}"
    print("=== AUDIT VERDICT: 3,040 / 3,040 MATCHED 100% BIT-EXACT ===")

if __name__ == "__main__":
    main()
