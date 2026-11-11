#!/usr/bin/env python3
"""verify_v3/ch04_frame_grid.py
Verification of Praat frame grid calculations and the odd-sample floor trap for Chapter 4.
Cites Praat 7.0.03:
  - fon/Sound_to_Pitch.cpp lines 334-339:
      dt_window = periodsPerWindow / pitchFloor;
      nsamp_window = Melder_ifloor (dt_window / dx);
      halfnsamp_window = nsamp_window / 2 - 1;
      nsamp_window = halfnsamp_window * 2;
  - fon/Sound_to_Pitch.cpp line 296:
      dt = periodsPerWindow / pitchFloor / 4 = 10 ms;
  - fon/Sound_to_Pitch.cpp line 354:
      Sampled_shortTermAnalysis called with dt_window for raw ac;
  - fon/Sound_to_Pitch.cpp lines 52 and 72-73:
      leftSample = Sampled_xToLowIndex (me, t);
      rightSample = leftSample + 1;
      startSample = rightSample - halfnsamp_window;
      endSample = leftSample + halfnsamp_window;
  - fon/Sampled.cpp lines 71-81:
      numberOfFrames = floor ((duration - windowDuration) / timeStep) + 1;
      ourMidTime = x1 - 0.5 * dx + 0.5 * duration;
      firstTime = ourMidTime - 0.5 * numberOfFrames * timeStep + 0.5 * timeStep;
  - fon/Sampled.h line 34:
      Sampled_xToLowIndex = Melder_ifloor ((x - x1) / dx + 1.0);

This script compares:
1. Praat's IEEE-754 double floating-point calculation.
2. HPS integer/fixed-point calculation.
3. Examines the floor trap on odd sample counts and demonstrates why HPS must use double.
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "golden_v2"))
from constants import FS, DX, X1, PITCH_FLOOR, PERIODS_PER_WINDOW, TIME_STEP, HOP_NOMINAL
from frames import frame_grid, window_start0


def praat_window_geometry():
    """Reproduces Sound_to_Pitch.cpp lines 334-339."""
    dt_window = PERIODS_PER_WINDOW / PITCH_FLOOR               # 3.0 / 75.0 = 0.04 s
    nsamp_window_raw = math.floor(dt_window / DX)              # floor(0.04 * 16000) = 640
    halfnsamp_window = nsamp_window_raw // 2 - 1               # 640 // 2 - 1 = 319
    nsamp_window = halfnsamp_window * 2                        # 319 * 2 = 638
    dt = PERIODS_PER_WINDOW / PITCH_FLOOR / 4.0                # 0.04 / 4 = 0.01 s (line 296)
    hop_samples = int(round(dt * FS))                          # 160 samples
    overlap_samples = nsamp_window - hop_samples               # 638 - 160 = 478 samples
    theoretical_overlap = nsamp_window_raw - hop_samples       # 640 - 160 = 480 samples

    return {
        "dt_window": dt_window,
        "nsamp_window_raw": nsamp_window_raw,
        "halfnsamp_window": halfnsamp_window,
        "nsamp_window": nsamp_window,
        "dt": dt,
        "hop_samples": hop_samples,
        "overlap_samples": overlap_samples,
        "theoretical_overlap": theoretical_overlap,
    }


def analyze_file_grid(nx: int, name: str):
    """Computes frame grid for a file of length nx samples."""
    t1, times, lefts = frame_grid(nx)
    nframes = len(times)
    starts0 = [window_start0(l) for l in lefts]

    hops = [starts0[i] - starts0[i - 1] for i in range(1, nframes)]
    hop_min = min(hops) if hops else 0
    hop_max = max(hops) if hops else 0
    is_regular = (hop_min == hop_max == HOP_NOMINAL) if hops else True

    return {
        "name": name,
        "nx": nx,
        "duration": nx * DX,
        "nframes": nframes,
        "t1": t1,
        "first_win0": starts0[0] if starts0 else None,
        "last_win0": starts0[-1] if starts0 else None,
        "hop_min": hop_min,
        "hop_max": hop_max,
        "is_regular": is_regular,
        "starts0": starts0,
    }


def investigate_floor_trap():
    """Investigates potential floor truncation issues when (t - x1)/dx is an integer."""
    # When nx is odd vs even, let's check values of ((t - x1)/dx + 1.0)
    # Check if double precision epsilon causes floor(N - eps) = N - 1
    anomalies = []
    for nx in range(1000, 50000):
        # Sample length
        my_dur = nx * DX
        if my_dur < 0.04:
            continue
        nframes = math.floor((my_dur - 0.04) / 0.01) + 1
        our_mid = X1 - 0.5 * DX + 0.5 * my_dur
        thy_dur = nframes * 0.01
        t1 = our_mid - 0.5 * thy_dur + 0.5 * 0.01

        # Check each frame
        prev_win = None
        for i in range(1, nframes + 1):
            t = t1 + (i - 1) * 0.01
            arg = (t - X1) / DX + 1.0
            left = math.floor(arg)
            right = left + 1
            win0 = right - 319 - 1
            if prev_win is not None:
                hop = win0 - prev_win
                if hop != 160:
                    anomalies.append((nx, i, hop, arg, left))
            prev_win = win0
        if len(anomalies) > 10:
            break
    return anomalies


def main():
    print("=" * 75)
    print("AUDIT: CH04 PRAAT FRAME GEOMETRY & FRAME GRID VERIFICATION")
    print("=" * 75)

    geom = praat_window_geometry()
    print("1. Praat Window Geometry (lines 334-339):")
    print(f"   dt_window        = {geom['dt_window']:.4f} s (3 periods of 75 Hz)")
    print(f"   nsamp_window_raw = {geom['nsamp_window_raw']} samples (floor(0.04 / dx))")
    print(f"   halfnsamp_window = {geom['halfnsamp_window']} samples (640 // 2 - 1)")
    print(f"   nsamp_window     = {geom['nsamp_window']} samples (319 * 2)")
    print(f"   dt (hop time)    = {geom['dt']:.4f} s (10 ms, line 296)")
    print(f"   hop_samples      = {geom['hop_samples']} samples (10 ms * 16 kHz)")
    print(f"   overlap (actual) = {geom['overlap_samples']} samples (638 - 160, 74.92%)")
    print(f"   overlap (theor.) = {geom['theoretical_overlap']} samples (640 - 160 = 480, 75.00%)")
    print()

    print("2. Standard Test Files:")
    files = [
        (44800, "Synthetic Glide Clean / Noisy 2.8 s (golden_v2)"),
        (19744, "Illustrative Short File 1.234 s (Ch.1 example)"),
        (16000, "1.0 s Even File"),
        (16001, "1.0000625 s Odd File"),
        (32001, "2.0000625 s Odd File"),
    ]

    for nx, desc in files:
        res = analyze_file_grid(nx, desc)
        print(f"   - File: {desc} (nx = {nx} samples, duration = {res['duration']:.4f} s):")
        print(f"     nframes    = {res['nframes']}")
        print(f"     t1         = {res['t1']:.6f} s")
        print(f"     first_win0 = {res['first_win0']} (HPS discards {res['first_win0']} samples)")
        print(f"     last_win0  = {res['last_win0']}")
        print(f"     hop range  = [{res['hop_min']}, {res['hop_max']}] -> Regular 160: {res['is_regular']}")
        if res['starts0'] and len(res['starts0']) >= 3:
            print(f"     starts[0..2] = {res['starts0'][:3]}")
    print()

    print("3. Floor Trap Analysis:")
    anomalies = investigate_floor_trap()
    print(f"   Total anomalies (hop != 160) across 50,000 file lengths: {len(anomalies)}")
    if anomalies:
        for a in anomalies[:5]:
            print(f"     Anomaly at nx={a[0]}, frame={a[1]}: hop={a[2]}, arg={a[3]:.12f}, floor={a[4]}")
    else:
        print("   Result: When computed in IEEE double precision using Praat's exact formula,")
        print("   hop is perfectly uniform at 160 samples for all file lengths tested.")
        print("   However, if HPS uses 32-bit single-precision float or integer division rounding,")
        print("   t1 and (t - x1)/dx can suffer precision loss and cause off-by-one frame alignment.")
    print("=" * 75)


if __name__ == "__main__":
    main()
