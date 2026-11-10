#!/usr/bin/env python3
"""verify_v3/ch00_norm_sine.py
Demonstrate Boersma's window normalization:
Pure sine wave through an 8-sample Praat Hanning window (N=8, N+1 form).
Compute r(tau) before and after dividing by R_w(tau).
"""

import math
import numpy as np

def run():
    N = 8
    # Praat Hanning formula: w[i] = 0.5 - 0.5 * cos(2*pi*i / (N+1)), i = 1..N
    # In 0-based indexing n = 0..7, so i = n + 1
    w = np.array([0.5 - 0.5 * math.cos(2 * math.pi * (n + 1) / (N + 1)) for n in range(N)])
    
    # Pure sine of period P = 4: x[n] = sin(2*pi*n / 4) = [0, 1, 0, -1, 0, 1, 0, -1]
    n = np.arange(N)
    x = np.sin(2 * np.pi * n / 4)
    # Windowed signal
    xw = x * w
    
    print("=== Praat 8-sample Hanning Window ===")
    for i, val in enumerate(w):
        print(f"w[{i}] (i={i+1}): {val:.6f}")
        
    print("\n=== Signal and Windowed Signal ===")
    for i in range(N):
        print(f"n={i}: x[{i}] = {x[i]:6.3f}, w[{i}] = {w[i]:.4f}, xw[{i}] = {xw[i]:.4f}")
        
    # Autocorrelation of windowed signal Rxw(tau) and window Rw(tau)
    lags = [0, 1, 2, 3, 4]
    Rxw = []
    Rw = []
    for tau in lags:
        rxw_val = sum(xw[k] * xw[k + tau] for k in range(N - tau))
        rw_val = sum(w[k] * w[k + tau] for k in range(N - tau))
        Rxw.append(rxw_val)
        Rw.append(rw_val)
        
    Rxw = np.array(Rxw)
    Rw = np.array(Rw)
    
    # Normalized without dividing by Rw(tau): just Rxw(tau) / Rxw(0)
    r_unnorm = Rxw / Rxw[0]
    
    # Boersma normalization: r(tau) = Rxw(tau) / Rw(tau)
    # Since Rw(0) = sum w^2, and Rxw(0) = sum xw^2 = 0.5 * Rw(0) for a pure sine,
    # r_Boersma(tau) = [Rxw(tau) / Rw(tau)] / [Rxw(0) / Rw(0)]
    # Or simply comparing Rxw(tau)/Rw(tau) relative to Rxw(0)/Rw(0).
    # In Praat: r(tau) = (Rxw(tau) / Rw(tau)) / (Rxw(0) / Rw(0))
    r_Boersma = (Rxw / Rw) / (Rxw[0] / Rw[0])
    
    print("\n=== Autocorrelation Results ===")
    print("tau |    Rw(tau)   |   Rxw(tau)   | Unnorm r(tau) | Boersma r(tau)")
    print("----+--------------+--------------+---------------+---------------")
    for i, tau in enumerate(lags):
        print(f" {tau:2d} | {Rw[i]:12.6f} | {Rxw[i]:12.6f} | {r_unnorm[i]:13.6f} | {r_Boersma[i]:13.6f}")

    print("\nExplanation:")
    print(f"At fundamental period tau = 4:")
    print(f"Without window normalization: r_unnorm(4) = {r_unnorm[4]:.4f} (severely attenuated due to window taper!)")
    print(f"With Boersma normalization:   r_Boersma(4) = {r_Boersma[4]:.4f} (almost exactly 1.0, restoring true periodicity!)")

if __name__ == '__main__':
    run()
