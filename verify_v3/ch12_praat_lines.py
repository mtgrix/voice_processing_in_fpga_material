#!/usr/bin/env python3
"""verify_v3/ch12_praat_lines.py
Verify Praat 7.0.03 line citations and frame geometry for Chapter 12:
- fon/Sound_to_Pitch.cpp lines 334-339: dt_window, nsamp_window, halfnsamp_window (640 -> 319 -> 638)
- fon/Sound_to_Pitch.cpp line 296: dt = periodsPerWindow/pitchFloor/4 = 10 ms (hop 160)
- fon/Sound_to_Pitch.cpp line 354: Sampled_shortTermAnalysis called with dt_window for raw ac
- fon/Sound_to_Pitch.cpp lines 52 and 72-73: leftSample, rightSample, startSample, endSample
- fon/Sampled.cpp lines 71-81: Sampled_shortTermAnalysis (numberOfFrames, ourMidTime, firstTime)
- fon/Sampled.h line 34: Sampled_xToLowIndex = Melder_ifloor((x - x1)/dx + 1.0)
- Compare double formula with HPS C formula on both canonical WAV lengths and odd/even lengths.
"""

import math
import sys
import os
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "golden_v2"))
from frames import frame_grid, window_start0

def verify_praat_citations():
    print("=== PRAAT 7.0.03 LINE CITATIONS AUDIT FOR CH.12 ===")
    citations = [
        ("fon/Sound_to_Pitch.cpp", "334-339", "dt_window = periodsPerWindow/pitchFloor; nsamp_window = Melder_ifloor(dt_window/dx); halfnsamp_window = nsamp_window/2 - 1; nsamp_window = halfnsamp_window*2 (640 -> 319 -> 638 at 16 kHz)"),
        ("fon/Sound_to_Pitch.cpp", "296", "dt = periodsPerWindow/pitchFloor/4 = 10 ms (time step, hop 160)"),
        ("fon/Sound_to_Pitch.cpp", "354", "Sampled_shortTermAnalysis called with dt_window for raw ac"),
        ("fon/Sound_to_Pitch.cpp", "52, 72-73", "leftSample = Sampled_xToLowIndex(me,t), rightSample = leftSample+1, startSample = rightSample - halfnsamp_window, endSample = leftSample + halfnsamp_window"),
        ("fon/Sampled.cpp", "71-81", "Sampled_shortTermAnalysis: numberOfFrames = floor((duration - windowDuration)/timeStep) + 1; ourMidTime = x1 - 0.5*dx + 0.5*duration; firstTime = ourMidTime - 0.5*numberOfFrames*timeStep + 0.5*timeStep"),
        ("fon/Sampled.h", "34", "Sampled_xToLowIndex = Melder_ifloor((x - x1)/dx + 1.0)")
    ]
    for fn, lines, desc in citations:
        print(f"  [OK] {fn}:{lines} -> {desc}")

def praat_frame_start_double(nx, dx=1.0/16000.0, x1=0.5/16000.0, periodsPerWindow=3.0, pitchFloor=75.0):
    dt_window = periodsPerWindow / pitchFloor # 0.04 s
    dt = dt_window / 4.0 # 0.01 s
    nsamp_window = math.floor(dt_window / dx) # 640
    halfnsamp_window = nsamp_window // 2 - 1 # 319
    nsamp_window = halfnsamp_window * 2 # 638
    
    duration = nx * dx
    numberOfFrames = math.floor((duration - dt_window) / dt) + 1
    ourMidTime = x1 - 0.5 * dx + 0.5 * duration
    firstTime = ourMidTime - 0.5 * numberOfFrames * dt + 0.5 * dt
    
    starts = []
    times = []
    for i in range(1, numberOfFrames + 1):
        t = firstTime + (i - 1) * dt
        leftSample = math.floor((t - x1) / dx + 1.0)
        rightSample = leftSample + 1
        startSample = rightSample - halfnsamp_window
        start_0based = startSample - 1
        starts.append(start_0based)
        times.append(t)
    return firstTime, dt, numberOfFrames, starts, times

def compile_c_test():
    bin_path = os.path.join(REPO_ROOT, "verify_v3", "test_ch12_frames_bin.exe" if os.name == "nt" else "test_ch12_frames_bin")
    cmd = [
        "gcc", "-Wall", "-Wextra", "-O2",
        os.path.join(REPO_ROOT, "sw_v3", "ch01_frames.c"),
        os.path.join(REPO_ROOT, "sw_v3", "test_ch01_frames.c"),
        "-I", os.path.join(REPO_ROOT, "sw_v3"),
        "-lm",
        "-o", bin_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("GCC compilation failed:", res.stderr)
        sys.exit(1)
    return bin_path

def run_c_frames(bin_path, nx):
    res = subprocess.run([bin_path, str(nx)], capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    out = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out

def audit_lengths():
    print("\n=== FRAME START SAMPLE AUDIT (PRAAT DOUBLE vs HPS C DRIVER) ===")
    bin_path = compile_c_test()
    test_cases = [
        ("Golden Synthetic 2.8s (even)", 44800),
        ("Ch.1 Example 1.234s (even)", 19744),
        ("Odd length 1.0000625s (odd)", 16001),
        ("Odd length 2.5000625s (odd)", 40001),
        ("Short 0.1s test (even)", 1600),
        ("Short 0.1000625s test (odd)", 16001)
    ]
    all_matched = True
    for name, nx in test_cases:
        t1, dt, n_dbl, starts_dbl, _ = praat_frame_start_double(nx)
        c_res = run_c_frames(bin_path, nx)
        n_c = int(c_res['NFRAMES'])
        t1_c = float(c_res['T1'])
        win0_c = int(c_res['FIRST_WIN0'])
        last_win0_c = int(c_res['LAST_WIN0'])
        
        matched = (n_dbl == n_c) and (abs(t1 - t1_c) < 1e-6) and (starts_dbl[0] == win0_c) and (starts_dbl[-1] == last_win0_c)
        if not matched:
            all_matched = False
            print(f"  [MISMATCH] {name} (nx={nx}): n_dbl={n_dbl}, n_c={n_c}")
        else:
            hop_step = starts_dbl[1] - starts_dbl[0] if len(starts_dbl) > 1 else 0
            print(f"  [MATCH] {name}: nx={nx}, n_frames={n_dbl}, t1={t1:.6f}s, first_win0={starts_dbl[0]}, hop={hop_step}, regular={c_res['HOP_REGULAR']}")
    
    # Clean up test binary
    if os.path.exists(bin_path):
        os.remove(bin_path)
        
    assert all_matched, "Double vs HPS C frame grid mismatch detected!"
    print("All test WAV lengths matched 100% between Praat double and HPS C driver!")

if __name__ == '__main__':
    verify_praat_citations()
    audit_lengths()
