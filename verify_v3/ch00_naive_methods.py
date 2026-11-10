#!/usr/bin/env python3
"""verify_v3/ch00_naive_methods.py
Demonstrate why naive pitch estimation methods fail:
1. Zero-crossing counting on a signal with strong 2nd harmonic.
2. FFT peak picking frequency resolution and cent errors.
3. Miniature integer autocorrelation example.
"""

import math
import numpy as np

def test_zero_crossing():
    print("=== 1. Zero-Crossing Failure ===")
    fs = 16000
    f0 = 100.0
    # Period in samples = 160.
    # Signal with fundamental + strong 2nd harmonic
    # x(t) = sin(2*pi*f0*t) - 0.75 * sin(4*pi*f0*t)
    # Let's inspect 1 period (160 samples) and 3 periods (480 samples)
    t = np.arange(480) / fs
    x = np.sin(2 * np.pi * f0 * t) - 0.75 * np.sin(4 * np.pi * f0 * t)
    
    # Count zero crossings: sign changes
    # A zero-crossing occurs between n and n+1 if x[n]*x[n+1] < 0
    crossings = []
    for i in range(len(x) - 1):
        if (x[i] >= 0 and x[i+1] < 0) or (x[i] < 0 and x[i+1] >= 0):
            crossings.append(i)
            
    print(f"Signal duration: {len(x)} samples ({len(x)/fs*1000:.1f} ms, 3 full periods of 100 Hz).")
    print(f"Total zero-crossings counted: {len(crossings)} in 3 periods.")
    print(f"Crossings per period: {len(crossings) / 3:.1f} (expected 2 for pure sine, got 4!).")
    f_est = (len(crossings) / 2.0) / (len(x) / fs)
    print(f"Estimated frequency by zero-crossing: {f_est:.1f} Hz (true f0 = {f0:.1f} Hz).")
    print(f"First period zero-crossing sample indices: {[c for c in crossings if c < 160]}")
    
    # A small discrete hand example of 16 samples (1 period of 1000 Hz at 16 kHz):
    print("\nMiniature 16-sample hand example (1 period):")
    n16 = np.arange(16)
    x16 = np.round(100 * (np.sin(2 * np.pi * n16 / 16) - 0.8 * np.sin(4 * np.pi * n16 / 16))).astype(int)
    print("n:   ", " ".join(f"{n:4d}" for n in n16))
    print("x[n]:", " ".join(f"{v:4d}" for v in x16))
    zc16 = [i for i in range(15) if (x16[i] >= 0 and x16[i+1] < 0) or (x16[i] < 0 and x16[i+1] >= 0)]
    print(f"Zero crossings in 16 samples: indices {zc16} -> count = {len(zc16)} (should be 2, is {len(zc16)})")

def test_fft_resolution():
    print("\n=== 2. FFT Peak-Picking Resolution Failure ===")
    fs = 16000
    N_640 = 640
    df_640 = fs / N_640
    N_638 = 638
    df_638 = fs / N_638
    print(f"fs = {fs} Hz")
    print(f"N = 640: bin spacing df = {fs}/{N_640} = {df_640:.2f} Hz")
    print(f"N = 638: bin spacing df = {fs}/{N_638} = {df_638:.4f} Hz (Praat 638-sample window)")
    
    # Error for target f0 = 100 Hz, 112.5 Hz, 200 Hz, 400 Hz
    targets = [
        (100.0, 112.5), # half-bin offset at 100 Hz
        (200.0, 212.5), # half-bin offset at 200 Hz
        (400.0, 412.5), # half-bin offset at 400 Hz
    ]
    for f_nom, f_true in targets:
        # If true frequency is f_true and FFT picks closest bin:
        closest_bin = round(f_true / df_640)
        f_picked = closest_bin * df_640
        err_hz = abs(f_true - f_picked)
        cents = 1200 * math.log2(f_true / f_picked)
        print(f"Target f_true = {f_true:.1f} Hz: closest bin {closest_bin} ({f_picked:.1f} Hz), err = {err_hz:.1f} Hz, cents = {cents:.2f} cent (|cents| = {abs(cents):.2f})")

def test_autocorr_motivation():
    print("\n=== 3. Miniature Integer Autocorrelation Example ===")
    # Periodic pattern of period P = 3
    # x = [3, -1, -2, 3, -1, -2, 3, -1, -2] (sum per period = 0)
    x = [3, -1, -2, 3, -1, -2, 3, -1, -2]
    N = len(x)
    print(f"x = {x}, length N = {N}, fundamental period P = 3")
    R = {}
    for tau in range(6):
        r = sum(x[n] * x[n + tau] for n in range(N - tau))
        R[tau] = r
        pairs = [f"{x[n]}*{x[n+tau]}" for n in range(N - tau)]
        print(f"tau = {tau}: R[{tau}] = " + " + ".join(pairs) + f" = {r}")
    
    # Normalized by overlap length (N - tau) to see pure correlation:
    print("\nUnbiased average R[tau]/(N-tau):")
    for tau in range(6):
        avg = R[tau] / (N - tau)
        print(f"tau = {tau}: R[{tau}]/({N}-{tau}) = {R[tau]}/{N-tau} = {avg:.2f}")

if __name__ == '__main__':
    test_zero_crossing()
    test_fft_resolution()
    test_autocorr_motivation()
