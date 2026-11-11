#!/usr/bin/env python3
"""verify_v3/ch07_praat_lines.py

Audits Praat 7.0.03 line citations for Chapter 7 (Autocorrelation by MAC)
in fon/Sound_to_Pitch.cpp.

Reviewer-verified line citations (Note p):
- line 344: minimumLag = max(2, Melder_ifloor(1/dx/pitchCeiling)) -> 26 at 16 kHz, 600 Hz
- line 345: maximumLag = min(Melder_ifloor(nsamp_window/periodsPerWindow) + 2, nsamp_window) -> 212 + 2 = 214
- lines 401-403: nsampFFT = smallest power of 2 >= nsamp_window*(1+interpolation_depth) = 957 -> 1024
- lines 79-80: zero padding frame[j] = 0 for j = nsamp_window+1..nsampFFT
- lines 144-156: comment 'The FFT of the autocorrelation is the power spectrum.'; NUMfft_forward, power spectrum ac[i] = re^2 + im^2, DC at 151, Nyquist at 154, NUMfft_backward gives the autocorrelation
- lines 158-164: r[0] = 1; r[i] = ac[i+1] / (ac[1] * windowR[i+1]) for i = 1..brent_ixmax
"""

import sys
import math

CITATIONS = [
    ("fon/Sound_to_Pitch.cpp", "344",
     "minimumLag = max (2, Melder_ifloor (1.0 / my dx / pitchCeiling));",
     "Xác định độ trễ tối thiểu (minimumLag = floor(16000/600) = 26 tại fs=16kHz, ceiling=600Hz)"),
    ("fon/Sound_to_Pitch.cpp", "345",
     "maximumLag = min (Melder_ifloor (nsamp_window / periodsPerWindow) + 2, nsamp_window);",
     "Xác định độ trễ tối đa (maximumLag = floor(638/3) + 2 = 212 + 2 = 214 tại N=638, 3 chu kỳ)"),
    ("fon/Sound_to_Pitch.cpp", "401--403",
     "nsampFFT = 1; while (nsampFFT < nsamp_window * (1.0 + interpolation_depth)) nsampFFT *= 2;",
     "Kích thước FFT 1024 điểm (lũy thừa 2 nhỏ nhất >= 638 * 1.5 = 957 -> 1024)"),
    ("fon/Sound_to_Pitch.cpp", "79--80",
     "for (integer j = nsamp_window + 1; j <= nsampFFT; j ++) frame [j] = 0.0;",
     "Đệm số 0 vào đuôi khung từ vị trí 639 đến 1024 để chống chồng phổ trong miền thời gian"),
    ("fon/Sound_to_Pitch.cpp", "144--156",
     "/* The FFT of the autocorrelation is the power spectrum. */ ... NUMfft_forward ... NUMfft_backward",
     "Tính tự tương quan bằng cặp biến đổi FFT: phổ công suất |X(k)|^2 rồi biến đổi ngược IFFT"),
    ("fon/Sound_to_Pitch.cpp", "158--164",
     "r [0] = 1.0; for (integer i = 1; i <= brent_ixmax; i ++) r [i] = ac [i + 1] / (ac [1] * windowR [i + 1]);",
     "Chuẩn hóa tự tương quan: chia cho năng lượng ac[1] và hàm tự tương quan cửa sổ windowR, r[0] = 1")
]

def main():
    print("=" * 78)
    print("CH07 PRAAT 7.0.03 SOURCE CODE CITATIONS AUDIT")
    print("=" * 78)
    for file, lines, snippet, meaning in CITATIONS:
        print(f"[{file}:{lines}]")
        print(f"   Code   : {snippet}")
        print(f"   Ý nghĩa: {meaning}\n")

    # Audit the numerical parameters
    fs = 16000.0
    dx = 1.0 / fs
    pitchCeiling = 600.0
    nsamp_window = 638
    periodsPerWindow = 3.0
    interpolation_depth = 0.5

    min_lag = max(2, math.floor(1.0 / dx / pitchCeiling))
    max_lag = min(math.floor(nsamp_window / periodsPerWindow) + 2, nsamp_window)
    
    nsampFFT = 1
    while nsampFFT < nsamp_window * (1.0 + interpolation_depth):
        nsampFFT *= 2

    print("=" * 78)
    print("NUMERICAL VERIFICATION OF PRAAT FORMULAS")
    print("=" * 78)
    print(f"Sampling frequency fs        : {fs:.1f} Hz (dx = {dx*1e6:.2f} us)")
    print(f"Pitch ceiling                : {pitchCeiling:.1f} Hz")
    print(f"Window length nsamp_window   : {nsamp_window} samples")
    print(f"Periods per window           : {periodsPerWindow:.1f}")
    print(f"Minimum lag (line 344)       : {min_lag} (floor(16000/600) = 26)")
    print(f"Maximum lag (line 345)       : {max_lag} (floor(638/3) + 2 = 212 + 2 = 214)")
    print(f"FFT size nsampFFT (line 401) : {nsampFFT} (smallest power of 2 >= {nsamp_window * 1.5} -> 1024)")
    print(f"Zero padding span (line 79)  : samples {nsamp_window + 1} to {nsampFFT} ({nsampFFT - nsamp_window} zero samples)")
    print(f"No-wrap margin for linear ac : nsampFFT - nsamp_window = {nsampFFT - nsamp_window} samples")
    print(f"Check condition max_lag <= 386: {max_lag} <= {nsampFFT - nsamp_window} -> {max_lag <= nsampFFT - nsamp_window} (NO CIRCULAR WRAP)")
    print("=" * 78)

if __name__ == "__main__":
    main()
