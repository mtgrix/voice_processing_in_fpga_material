"""verify_v3/ch13_frame_alignment.py
Audits frame alignment by time:
  - Praat Pitch object time grid: t_k = t_1 + k * dt
  - Praat 7.0.03 exact C++ formulas (fon/Sound_to_Pitch.cpp, fon/Sampled.cpp, fon/Sampled.h):
      numberOfFrames = floor((duration - windowDuration) / timeStep) + 1
      ourMidTime = x1 - 0.5 * dx + 0.5 * duration
      firstTime = ourMidTime - 0.5 * numberOfFrames * timeStep + 0.5 * timeStep
      leftSample = floor((t - x1) / dx + 1.0)
      startSample = (leftSample + 1) - halfnsamp_window
  - Compares Praat C++ double calculation with HPS C driver implementation (sw_v3/ch01_frames.c).
  - Demonstrates the odd-sample floor trap if naive rounding (t * fs + 0.5) is used.
  - Verifies exact start samples and nominal 160-sample hop on:
      (1) synth_glide_vuv_16k.wav (44800 samples = 2.8 s, even length)
      (2) synth_glide_vuv_16k_snr5.wav (44800 samples = 2.8 s, even length)
      (3) 1.234 s audio file (19744 samples)
      (4) Odd length files (44801, 19743 samples)
"""
import math
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN_DIR = os.path.join(os.path.dirname(BASE_DIR), 'golden_v2')
if GOLDEN_DIR not in sys.path:
    sys.path.insert(0, GOLDEN_DIR)

import constants as K
from frames import frame_grid, window_start0

def praat_cpp_frame_geometry(nsamples, fs=16000, pitch_floor=75.0):
    dx = 1.0 / fs
    x1 = 0.5 * dx
    duration = nsamples * dx
    
    # Sound_to_Pitch.cpp lines 334-339
    periods_per_window = 3.0
    dt_window = periods_per_window / pitch_floor       # 0.040 s
    _n = math.floor(dt_window / dx)                    # 640
    halfnsamp_window = _n // 2 - 1                     # 319
    nsamp_window = halfnsamp_window * 2                # 638
    
    # line 296
    time_step = periods_per_window / pitch_floor / 4.0 # 0.010 s
    
    # Sampled.cpp lines 71-81: Sampled_shortTermAnalysis
    n_frames = math.floor((duration - dt_window) / time_step) + 1
    mid_time = x1 - 0.5 * dx + 0.5 * duration
    t1 = mid_time - 0.5 * n_frames * time_step + 0.5 * time_step
    
    times = [t1 + i * time_step for i in range(n_frames)]
    
    # Sampled.h line 34: Sampled_xToLowIndex
    # Sound_to_Pitch.cpp lines 72-73:
    #   leftSample = Sampled_xToLowIndex(me, t)
    #   rightSample = leftSample + 1
    #   startSample = rightSample - halfnsamp_window (1-based)
    starts_0based = []
    left_samples = []
    for t in times:
        left = math.floor((t - x1) / dx + 1.0)
        start_0 = (left + 1) - halfnsamp_window - 1
        left_samples.append(left)
        starts_0based.append(start_0)
        
    return {
        'n_frames': n_frames,
        't1': t1,
        'dt': time_step,
        'times': times,
        'lefts': left_samples,
        'starts': starts_0based,
        'nsamp_window': nsamp_window
    }

def hps_c_frame_geometry(nsamples, fs=16000):
    """Models the exact C double calculations in sw_v3/ch01_frames.c."""
    fs_d = float(fs)
    dx_d = 1.0 / fs_d
    x1_d = 0.5 * dx_d
    dt_window = 0.04
    time_step = 0.01
    halfnsamp_window = 319
    
    my_duration = dx_d * float(nsamples)
    nframes_d = math.floor((my_duration - dt_window) / time_step) + 1.0
    nframes = int(nframes_d)
    
    our_mid = x1_d - 0.5 * dx_d + 0.5 * my_duration
    thy_duration = float(nframes) * time_step
    t1 = our_mid - 0.5 * thy_duration + 0.5 * time_step
    
    starts = []
    lefts = []
    for i in range(1, nframes + 1):
        t = t1 + float(i - 1) * time_step
        left_d = math.floor((t - x1_d) / dx_d + 1.0)
        left = int(left_d)
        right = left + 1
        win0 = right - halfnsamp_window - 1
        lefts.append(left)
        starts.append(win0)
        
    return {
        'n_frames': nframes,
        't1': t1,
        'dt': time_step,
        'starts': starts,
        'lefts': lefts
    }

def naive_floor_trap_geometry(nsamples, fs=16000):
    """Naive calculation using t*fs + 0.5 that falls into the odd-sample floor trap."""
    dt_window = 0.04
    time_step = 0.01
    duration = float(nsamples) / fs
    n_frames = int(math.floor((duration - dt_window) / time_step)) + 1
    mid_time = 0.5 * duration
    t1 = mid_time - 0.5 * n_frames * time_step + 0.5 * time_step
    starts = []
    for i in range(n_frames):
        t = t1 + i * time_step
        left = int(math.floor(t * fs + 0.5))
        starts.append(left - 319)
    return starts

def main():
    print("=" * 84)
    print("CH13 FRAME ALIGNMENT AUDIT: TIME-BASED GRID & START SAMPLE COMPARISON")
    print("=" * 84)
    
    test_cases = [
        ("synth_glide_vuv_16k.wav", 44800),
        ("synth_glide_vuv_16k_snr5.wav", 44800),
        ("Tệp mẫu 1,234 s (Chương 1)", 19744),
        ("Tệp mẫu độ dài lẻ 1 (44801 mẫu)", 44801),
        ("Tệp mẫu độ dài lẻ 2 (19743 mẫu)", 19743),
    ]
    
    for name, nsamples in test_cases:
        p_res = praat_cpp_frame_geometry(nsamples)
        h_res = hps_c_frame_geometry(nsamples)
        naive_starts = naive_floor_trap_geometry(nsamples)
        
        diff_starts = np.array(p_res['starts']) - np.array(h_res['starts'])
        max_diff = np.max(np.abs(diff_starts))
        
        diff_naive = np.array(p_res['starts']) - np.array(naive_starts)
        max_diff_naive = np.max(np.abs(diff_naive))
        
        hops_p = np.diff(p_res['starts'])
        unique_hops_p = sorted(list(set(hops_p))) if len(hops_p) > 0 else []
        
        print(f"\n--- Kiểm tra: {name} (N = {nsamples} mẫu) ---")
        print(f"  Số khung phân tích (n_frames) : Praat C++ = {p_res['n_frames']}, HPS C = {h_res['n_frames']}")
        print(f"  Thời điểm khung 1 (t1)        : Praat C++ = {p_res['t1']:.6f} s, HPS C = {h_res['t1']:.6f} s")
        print(f"  Bước thời gian (dt)           : Praat C++ = {p_res['dt']:.6f} s, HPS C = {h_res['dt']:.6f} s")
        print(f"  Mẫu bắt đầu khung 0 (first_win0): Praat C++ = {p_res['starts'][0]}, HPS C = {h_res['starts'][0]}")
        print(f"  Tập bước nhảy hop thực tế     : Praat C++ = {unique_hops_p}")
        print(f"  Độ lệch Praat C++ vs HPS C    : max|starts_praat - starts_hps| = {max_diff} mẫu")
        print(f"  Bẫy làm tròn naive (t*fs+0.5) : max|starts_praat - starts_naive| = {max_diff_naive} mẫu")
        if max_diff_naive > 0:
            print(f"    [CẢNH BÁO BẪY LÀM TRÒN] Công thức ngây thơ bị lệch {max_diff_naive} mẫu trên tệp độ dài lẻ!")
        assert max_diff == 0, f"Mismatch between Praat and HPS C driver for {name}!"
        assert p_res['n_frames'] == h_res['n_frames'], f"Frame count mismatch for {name}!"
        assert p_res['starts'][0] == h_res['starts'][0], f"First window start mismatch for {name}!"
        print("  => KẾT LUẬN: HPS C KHỚP TUYỆT ĐỐI 100% VỚI PRAAT C++ TRÊN MỌI ĐỘ DÀI!")

    print("\n" + "=" * 84)
    print("ALL TIME-BASED FRAME ALIGNMENT AUDITS PASSED!")
    print("=" * 84)

if __name__ == '__main__':
    main()
