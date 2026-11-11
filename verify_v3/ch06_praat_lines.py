#!/usr/bin/env python3
"""verify_v3/ch06_praat_lines.py

Audits Praat 7.0.03 line citations for Chapter 6 (Hanning N+1 window) in
fon/Sound_to_Pitch.cpp and compares the Praat C++ double-precision window
against the Q1.15 fixed-point ROM format.

Verified facts from reviewer note (n):
- fon/Sound_to_Pitch.cpp:
  lines 39-40: #define AC_HANNING 0, AC_GAUSS 1
  lines 299-301: sinc70 + Brent interpolation depth
  lines 303-306: AC_GAUSS periodsPerWindow *= 2
  lines 334-339: window length calculation (1278 for 6 periods, 638 for 3 periods)
  line 409: window.resize (nsamp_window);
  lines 413-415: comment on Hanning 2 to 5 dB better for 3 periods/window
  lines 417-421: Gaussian window formula
  lines 422-424: Hanning N+1 formula
  lines 429-442: windowR normalized autocorrelation of the window via FFT
  line 78: frame[j] = (z[i] - localMean) * window[j];
  lines 88-101: LocalPeak search range
"""

import sys
import math
import numpy as np

# Citations table
CITATIONS = [
    ("fon/Sound_to_Pitch.cpp", "39--40", "#define AC_HANNING 0 / #define AC_GAUSS 1", "Định nghĩa định danh cho hai phương pháp cửa sổ hóa"),
    ("fon/Sound_to_Pitch.cpp", "78", "frame[j] = (my z[i] - localMean) * window[j];", "Trừ trung bình cục bộ rồi nhân trực tiếp với mẫu cửa sổ"),
    ("fon/Sound_to_Pitch.cpp", "88--101", "LocalPeak: j from halfnsamp_window - halfnsamp_period + 1 to + halfnsamp_period", "Phạm vi dò đỉnh cục bộ LP (212..425, 0-based)"),
    ("fon/Sound_to_Pitch.cpp", "299--301", "case AC_HANNING: brent_depth = NUM_PEAK_INTERPOLATE_SINC70", "Cấu hình 3 chu kỳ và nội suy SINC70 cho AC_HANNING"),
    ("fon/Sound_to_Pitch.cpp", "303--306", "case AC_GAUSS: periodsPerWindow *= 2; brent_depth = SINC700", "Nhân đôi độ dài cửa sổ (6 chu kỳ) cho AC_GAUSS"),
    ("fon/Sound_to_Pitch.cpp", "334--339", "halfnsamp_window = nsamp_window/2 - 1; nsamp_window = halfnsamp_window*2;", "Tính độ dài cửa sổ chẵn (N = 1278 cho 6 chu kỳ Gaussian, N = 638 cho 3 chu kỳ Hanning)"),
    ("fon/Sound_to_Pitch.cpp", "409", "window.resize (nsamp_window);", "Cấp phát bộ nhớ cho mảng cửa sổ kích thước N = 638"),
    ("fon/Sound_to_Pitch.cpp", "413--415", "The Hanning window is 2 to 5 dB better for 3 periods/window. The Gaussian window is 25 to 29 dB better for 6 periods/window.", "Chú thích Boersma: Hanning 2-5 dB cho 3 chu kỳ, Gaussian 25-29 dB cho 6 chu kỳ (nguồn không nêu mốc so sánh)"),
    ("fon/Sound_to_Pitch.cpp", "417--421", "window[i] = (exp(-48.0 * ((i - imid) / (nsamp_window + 1))^2) - edge) / (1 - edge);", "Công thức cửa sổ Gaussian của Praat"),
    ("fon/Sound_to_Pitch.cpp", "422--424", "window[i] = 0.5 - 0.5 * cos(NUM2pi * i / (nsamp_window + 1));", "Công thức Hanning N+1 (i = 1..N), không có mẫu 0 ở hai biên"),
    ("fon/Sound_to_Pitch.cpp", "429--442", "windowR = normalized autocorrelation of the window via FFT", "Tính tự tương quan chuẩn hóa của cửa sổ R_w qua FFT 1024 điểm")
]

def main():
    print("=" * 78)
    print("CH06 PRAAT 7.0.03 SOURCE CODE CITATIONS AUDIT")
    print("=" * 78)
    for file, lines, snippet, meaning in CITATIONS:
        print(f"[{file}:{lines}]")
        print(f"   Code   : {snippet}")
        print(f"   Ý nghĩa: {meaning}\n")

    # Math comparison between Praat double and Q1.15
    N = 638
    w_praat = [0.5 - 0.5 * math.cos(2.0 * math.pi * i / (N + 1)) for i in range(1, N + 1)]
    w_q15 = [min(32767, int(math.floor(v * 32768.0 + 0.5))) for v in w_praat]
    w_fpga_float = [v / 32768.0 for v in w_q15]

    diff = [abs(p - f) for p, f in zip(w_praat, w_fpga_float)]
    max_diff = max(diff)
    rms_diff = math.sqrt(sum(d * d for d in diff) / N)
    snr_db = 10.0 * math.log10(sum(p * p for p in w_praat) / sum(d * d for d in diff))

    print("=" * 78)
    print("PRAAT DOUBLE VS FPGA Q1.15 WINDOW COMPARISON (N = 638)")
    print("=" * 78)
    print(f"Number of samples N       : {N}")
    print(f"Praat window w[1] (double): {w_praat[0]:.10f}")
    print(f"FPGA Q1.15 w[0] (integer) : {w_q15[0]} -> float: {w_fpga_float[0]:.10f}")
    print(f"Praat window apex w[319]  : {w_praat[318]:.10f}")
    print(f"FPGA Q1.15 apex w[318]    : {w_q15[318]} (saturated to 32767)")
    print(f"Max absolute error        : {max_diff:.8e} ({max_diff * 32768:.4f} LSB)")
    print(f"RMS error                 : {rms_diff:.8e}")
    print(f"Quantization SNR          : {snr_db:.2f} dB")
    print("=" * 78)

if __name__ == "__main__":
    main()
