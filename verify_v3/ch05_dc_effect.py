#!/usr/bin/env python3
"""verify_v3/ch05_dc_effect.py
Mathematical derivation and numerical verification of DC offset effects on Autocorrelation
and DC-Blocker IIR filter characteristics for Chapter 5:
  1. Hand calculation: 8-sample square wave + DC 1000 (both Rectangular and Hanning windows).
     Verifies that normalized autocorrelation is shifted up by exactly c^2 = 1,000,000 for all lags.
  2. Voicing threshold failure demonstration:
     Unvoiced noise frame corrupted by DC offset falsely exceeding VOICING_THRESHOLD (0.45).
  3. Frequency and time domain analysis of the 1st-order IIR DC-blocker:
     H(z) = (1 - z^-1) / (1 - alpha * z^-1), alpha = 1 - 2^-8 = 0.99609375.
     Exact -3 dB cutoff frequency, response at 75 Hz (pitch floor), and step response decay.
"""
import math
import numpy as np


def run_hand_calculation():
    print("=" * 75)
    print("1. HAND CALCULATION: 8-SAMPLE SIGNAL WITH DC OFFSET (+1000)")
    print("=" * 75)
    # Signal s: zero-mean square wave with amplitude 1000, period 4 samples
    s = np.array([-1000, -1000, 1000, 1000, -1000, -1000, 1000, 1000], dtype=float)
    c = 1000.0  # DC offset
    x = s + c   # [0, 0, 2000, 2000, 0, 0, 2000, 2000]

    print("Signal samples:")
    print(f"  s[n] (zero-mean) = {s.astype(int).tolist()}")
    print(f"  DC offset c      = {int(c)}")
    print(f"  x[n] = s[n] + c  = {x.astype(int).tolist()}")
    print()

    # Praat Hanning window for N=8: w[i] = 0.5 - 0.5*cos(2*pi*i / (N+1)), i=1..8
    i_idx = np.arange(1, 9)
    w_hanning = 0.5 - 0.5 * np.cos(2 * np.pi * i_idx / 9.0)
    w_rect = np.ones(8)

    for w_name, w in [("Rectangular (w[n] = 1)", w_rect), ("Praat Hanning-8 (N+1)", w_hanning)]:
        print(f"--- Window: {w_name} ---")
        sw = s * w
        xw = x * w

        Rw = np.array([np.sum(w[:8-t] * w[t:]) for t in range(5)])
        R_s = np.array([np.sum(sw[:8-t] * sw[t:]) for t in range(5)])
        R_x = np.array([np.sum(xw[:8-t] * xw[t:]) for t in range(5)])
        r_s = R_s / Rw
        r_x = R_x / Rw

        print(f"{'tau':>3} | {'R_s[tau]':>12} | {'R_x[tau]':>12} | {'Rw[tau]':>10} | {'r_s = R_s/Rw':>14} | {'r_x = R_x/Rw':>14} | {'r_x - r_s':>12}")
        print("-" * 88)
        for t in range(5):
            diff = r_x[t] - r_s[t]
            print(f"{t:3d} | {R_s[t]:12.1f} | {R_x[t]:12.1f} | {Rw[t]:10.4f} | {r_s[t]:14.2f} | {r_x[t]:14.2f} | {diff:12.2f}")
            assert abs(diff - c**2) < 1e-4, f"Mismatch in diff: {diff} != {c**2}"

        print(f">>> Result: r_x[tau] - r_s[tau] = exactly c^2 = {c**2:.1f} across ALL lags tau!")
        print()


def run_voicing_failure_demo():
    print("=" * 75)
    print("2. VOICING THRESHOLD CORRUPTION DUE TO UNREMOVED DC")
    print("=" * 75)
    # Simulate an unvoiced noise frame (white noise, sigma = 1000)
    np.random.seed(42)
    noise_sigma = 1000.0
    N = 638
    noise = np.random.normal(0, noise_sigma, N)
    w = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(1, N + 1) / (N + 1))
    
    # Without DC
    nw = noise * w
    Rw0 = np.sum(w * w)
    R0_clean = np.sum(nw * nw)
    r0_clean = R0_clean / Rw0

    # Max non-zero lag autocorrelation for noise
    lags = np.arange(26, 215)
    r_clean_max = 0.0
    for t in lags:
        R_tau = np.sum(nw[:N-t] * nw[t:])
        Rw_tau = np.sum(w[:N-t] * w[t:])
        r_tau = R_tau / Rw_tau
        norm_r = r_tau / r0_clean
        if norm_r > r_clean_max:
            r_clean_max = norm_r

    # Add DC offset c = 1000 (equal to 1 sigma of noise)
    c = 1000.0
    noise_dc = noise + c
    ndcw = noise_dc * w
    R0_dc = np.sum(ndcw * ndcw)
    r0_dc = R0_dc / Rw0

    r_dc_max = 0.0
    for t in lags:
        R_tau = np.sum(ndcw[:N-t] * ndcw[t:])
        Rw_tau = np.sum(w[:N-t] * w[t:])
        r_tau = R_tau / Rw_tau
        norm_r = r_tau / r0_dc
        if norm_r > r_dc_max:
            r_dc_max = norm_r

    print(f"Noise Frame (sigma = {noise_sigma:.1f}, N = {N} samples):")
    print(f"  WITHOUT DC: Peak normalized r(tau)/r(0) in scan range [26, 214] = {r_clean_max:.4f}")
    print(f"              Praat VOICING_THRESHOLD = 0.4500")
    print(f"              Status: {'UNVOICED (Correct)' if r_clean_max < 0.45 else 'VOICED (Wrong)'}")
    print(f"  WITH DC c = {c:.1f}:")
    print(f"              Peak normalized r(tau)/r(0) in scan range [26, 214] = {r_dc_max:.4f}")
    print(f"              Status: {'UNVOICED (Wrong)' if r_dc_max < 0.45 else 'VOICED (FATAL ERROR - False Alarm)'}")
    print(">>> Conclusion: Without local mean subtraction, DC offset elevates noise autocorrelation")
    print("    above 0.45, turning whisper and background noise into false voiced pitch frames!")
    print("-" * 75)


def run_dc_blocker_analysis():
    print("\n" + "=" * 75)
    print("3. OPTIONAL 1ST-ORDER IIR DC-BLOCKER ANALYSIS")
    print("=" * 75)
    fs = 16000.0
    alpha = 1.0 - 2**(-8)  # 255 / 256 = 0.99609375

    # Exact -3 dB cutoff frequency:
    # cos(wc) = (3 - alpha^2) / (2 * (2 - alpha))
    cos_wc = (3.0 - alpha**2) / (2.0 * (2.0 - alpha))
    wc = math.acos(cos_wc)
    fc_exact = wc * fs / (2.0 * math.pi)
    fc_approx = (1.0 - alpha) * fs / (2.0 * math.pi)

    print(f"Filter Transfer Function: H(z) = (1 - z^-1) / (1 - alpha * z^-1)")
    print(f"  alpha = 1 - 2^-8 = 255/256 = {alpha:.8f}")
    print(f"  Exact -3 dB cutoff frequency fc:  {fc_exact:.4f} Hz")
    print(f"  First-order approximation (1-alpha)*fs/(2*pi): {fc_approx:.4f} Hz")
    print(f"  Nyquist frequency fs/2: {fs/2:.1f} Hz")
    print()

    # Frequency response at key frequencies:
    test_freqs = [0.0, 1.0, 5.0, fc_exact, 20.0, 75.0, 150.0, 300.0, 1000.0, 4000.0, 8000.0]
    print(f"{'Freq (Hz)':>10} | {'|H(f)|':>10} | {'Gain (dB)':>12} | {'Phase (deg)':>12}")
    print("-" * 52)
    for f in test_freqs:
        if f == 0.0:
            gain = 0.0
            gain_db = -math.inf
            phase_deg = 90.0
        else:
            w = 2.0 * math.pi * f / fs
            ejw = np.exp(-1j * w)
            H = (1.0 - ejw) / (1.0 - alpha * ejw)
            gain = abs(H)
            gain_db = 20.0 * math.log10(gain)
            phase_deg = math.degrees(np.angle(H))

        print(f"{f:10.2f} | {gain:10.6f} | {gain_db:12.4f} | {phase_deg:12.4f}")

    print()
    # Step response:
    step_input = 1000.0
    y = 0.0
    x_prev = 0.0
    print("DC Step Response (input x[n] = 1000 for n >= 0):")
    milestones = [0, 1, 2, 5, 10, 50, 100, 256, 500, 1000, 2000]
    y_values = {}
    for n in range(max(milestones) + 1):
        x = step_input
        # y[n] = x[n] - x[n-1] + alpha * y[n-1]
        y = (x - x_prev) + alpha * y
        x_prev = x
        if n in milestones:
            y_values[n] = y

    print(f"{'n (sample)':>12} | {'Time (ms)':>10} | {'y[n] Output':>14} | {'Theoretical alpha^n * 1000':>26}")
    print("-" * 68)
    for n in milestones:
        t_ms = n * 1000.0 / fs
        theo = (alpha**n) * step_input
        print(f"{n:12d} | {t_ms:10.3f} | {y_values[n]:14.4f} | {theo:26.4f}")

    print("=" * 75)
    print(">>> Summary: At 75 Hz (lowest F0), attenuation is only -0.0590 dB (gain = 0.9932).")
    print("    DC (0 Hz) is 100% blocked (gain = 0.0). Step response decays by 1/e in ~256 samples (16 ms).")
    print("=" * 75)


def main():
    run_hand_calculation()
    run_voicing_failure_demo()
    run_dc_blocker_analysis()


if __name__ == "__main__":
    main()
