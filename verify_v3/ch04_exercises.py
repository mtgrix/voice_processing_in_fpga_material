#!/usr/bin/env python3
"""verify_v3/ch04_exercises.py
Computes and verifies exact numerical results for the exercises in Chapter 4:
  1. Minimum circular buffer capacity and headroom analysis.
  2. Sequence and periodicity of rd_base modulo 1024.
  3. Cyclone V M10K embedded memory block mapping and geometry.
  4. Frame grid alignment and odd-sample floor trap demonstration.
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "golden_v2"))
from constants import FS, DX, X1, PITCH_FLOOR, PERIODS_PER_WINDOW, TIME_STEP, HOP_NOMINAL
from frames import frame_grid, window_start0


def ex1_buffer_capacity():
    N = 638
    hop = 160
    min_capacity = N + hop  # 798
    actual_capacity = 1024
    headroom = actual_capacity - min_capacity  # 226
    m10k_single_depth_x16 = 512
    deficit_512 = min_capacity - m10k_single_depth_x16  # 286

    return {
        "N": N,
        "hop": hop,
        "min_capacity": min_capacity,
        "actual_capacity": actual_capacity,
        "headroom": headroom,
        "deficit_512": deficit_512,
    }


def ex2_rd_base_periodicity():
    hop = 160
    depth = 1024
    gcd_val = math.gcd(hop, depth)  # 32
    lcm_val = (hop * depth) // gcd_val  # 5120
    period_frames = depth // gcd_val  # 32
    period_samples = period_frames * hop  # 5120
    period_ms = (period_samples / FS) * 1000.0  # 320.0 ms

    sequence = [(k * hop) % depth for k in range(16)]

    return {
        "hop": hop,
        "depth": depth,
        "gcd": gcd_val,
        "lcm": lcm_val,
        "period_frames": period_frames,
        "period_samples": period_samples,
        "period_ms": period_ms,
        "first_16": sequence,
    }


def ex3_m10k_geometry():
    m10k_total_bits = 10240
    user_depth = 1024
    user_width = 16
    total_user_bits = user_depth * user_width  # 16384

    # Permitted M10K configurations in Cyclone V (CV-52003 Table 3-1):
    # 8Kx1, 4Kx2, 2Kx4, 1Kx8, 1Kx10, 512x16, 512x20, 256x32, 256x40
    max_depth_at_16bit = 512
    max_width_at_1024depth = 10  # 1Kx10 or 1Kx8

    # To build 1024x16: need 2 M10K blocks configured as 1024x8 each in parallel
    blocks_1024x16 = 2
    # To build 638x16: depth 638 > 512, so still exceeds 512x16, requires 2 M10K blocks
    blocks_638x16 = 2

    return {
        "m10k_total_bits": m10k_total_bits,
        "total_user_bits": total_user_bits,
        "max_depth_at_16bit": max_depth_at_16bit,
        "max_width_at_1024depth": max_width_at_1024depth,
        "blocks_1024x16": blocks_1024x16,
        "blocks_638x16": blocks_638x16,
    }


def ex4_odd_sample_trap():
    nx = 32001
    my_dur = nx * DX
    dt_win = 0.04
    dt = 0.01

    nframes = math.floor((my_dur - dt_win) / dt) + 1  # 197
    our_mid = X1 - 0.5 * DX + 0.5 * my_dur
    thy_dur = nframes * dt
    t1 = our_mid - 0.5 * thy_dur + 0.5 * dt

    starts0 = []
    irregular_hops = []
    prev = None

    for i in range(1, nframes + 1):
        t = t1 + (i - 1) * dt
        arg = (t - X1) / DX + 1.0
        left = math.floor(arg)
        right = left + 1
        win0 = right - 319 - 1
        starts0.append(win0)
        if prev is not None:
            h = win0 - prev
            if h != 160:
                irregular_hops.append((i - 1, i, h, t, arg, left))
        prev = win0

    return {
        "nx": nx,
        "my_dur": my_dur,
        "nframes": nframes,
        "t1": t1,
        "first_win0": starts0[0],
        "last_win0": starts0[-1],
        "irregular_count": len(irregular_hops),
        "irregular_hops": irregular_hops,
    }


def main():
    print("=" * 75)
    print("VERIFICATION: CH04 CHAPTER EXERCISES (EXACT NUMERICAL DERIVATIONS)")
    print("=" * 75)

    e1 = ex1_buffer_capacity()
    print("Exercise 1: Circular Buffer Capacity and Headroom")
    print(f"  Frame length N       = {e1['N']} samples")
    print(f"  Hop length           = {e1['hop']} samples")
    print(f"  Minimum capacity     = {e1['min_capacity']} words (638 + 160)")
    print(f"  Actual capacity      = {e1['actual_capacity']} words (2^10)")
    print(f"  Safety headroom      = {e1['headroom']} words (1024 - 798)")
    print(f"  Deficit of 512 words = {e1['deficit_512']} words (798 - 512)")
    print()

    e2 = ex2_rd_base_periodicity()
    print("Exercise 2: rd_base Modulo 1024 Trajectory and Periodicity")
    print(f"  GCD(160, 1024)       = {e2['gcd']}")
    print(f"  LCM(160, 1024)       = {e2['lcm']} samples")
    print(f"  Periodicity in frames= {e2['period_frames']} frames")
    print(f"  Periodicity in time  = {e2['period_ms']:.1f} ms")
    print("  First 16 values of rd_base:")
    for k in range(0, 16, 4):
        print(f"    k={k:2d}..{k+3:2d}: {e2['first_16'][k:k+4]}")
    print()

    e3 = ex3_m10k_geometry()
    print("Exercise 3: Cyclone V M10K Memory Geometry")
    print(f"  Total bits in 1 M10K = {e3['m10k_total_bits']} bits")
    print(f"  User capacity 1024x16= {e3['total_user_bits']} bits")
    print(f"  Max depth for x16 cfg= {e3['max_depth_at_16bit']} words (512x16 or 512x20)")
    print(f"  Max width for 1K depth= {e3['max_width_at_1024depth']} bits (1Kx8 or 1Kx10)")
    print(f"  M10K blocks (1024x16)= {e3['blocks_1024x16']} blocks (2x 1024x8 parallel)")
    print(f"  M10K blocks (638x16) = {e3['blocks_638x16']} blocks (still exceeds 512)")
    print()

    e4 = ex4_odd_sample_trap()
    print("Exercise 4: Odd-Length File Grid Alignment and Floor Trap")
    print(f"  Audio samples nx     = {e4['nx']} ({e4['my_dur']:.7f} s)")
    print(f"  Number of frames     = {e4['nframes']}")
    print(f"  Center time t1       = {e4['t1']:.8f} s")
    print(f"  First window start0  = {e4['first_win0']}")
    print(f"  Last window start0   = {e4['last_win0']}")
    print(f"  Irregular hop count  = {e4['irregular_count']}")
    if e4['irregular_hops']:
        for h in e4['irregular_hops'][:5]:
            print(f"    Frame {h[0]}->{h[1]}: hop={h[2]}, t={h[3]:.6f} s, arg={h[4]:.12f}, left={h[5]}")
    print("=" * 75)


if __name__ == "__main__":
    main()
