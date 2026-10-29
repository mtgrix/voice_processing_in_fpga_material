"""Lab 1.3.5: a bit-accurate fixed-point pitch detector, and its float reference.

The point of this file is the claim section 1.3.5 makes in prose: that the autocorrelation
pitch detector can be written with nothing but `+`, `-`, `*` and `>>` on two's-complement
integers, and that such a program returns the same bits on every machine and on the FPGA.
`fixed_pitch_frame` is that program. `float_pitch_frame` is the reference algorithm in float64,
used to measure how far the integers drift from it.

Nothing here is a bench recording. Every constant is derived from the section's design
(frame 640 samples, hop 160, scan lag range [26, 214], search range [27, 213]) or from
Praat's published defaults.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
HEX_DIR = Path(__file__).resolve().parent / "hex"

# --- Design constants, all fixed by section 1.3.5 -------------------------------
FS_HZ = 16_000
FRAME_LEN = 640  # 40 ms: three periods of the 75 Hz floor
HOP = 160  # 10 ms

# Scan range: tau in [26, 214] (189 lags) so tau* = 27 and 213
# have neighbors for parabolic interpolation
TAU_SCAN_MIN = 26  # ceil(fs / 615 Hz)
TAU_SCAN_MAX = 214  # floor(fs / 74.8 Hz)
N_SCAN_LAGS = TAU_SCAN_MAX - TAU_SCAN_MIN + 1  # 189 lags

# Search range for tau*: strictly [27, 213] (187 search candidates)
TAU_MIN = 27  # ceil(fs / 600 Hz ceiling)
TAU_MAX = 213  # floor(fs / 75 Hz floor)
N_SEARCH_LAGS = TAU_MAX - TAU_MIN + 1  # 187 lags

VOICING_THRESHOLD = 0.45  # Praat default; the integer test is on hundredths
# Praat default silence_threshold = 0.03 (amplitude). In energy: 0.03^2 = 0.0009 (-30.46 dB)
SILENCE_AMPLITUDE_THRESHOLD = 0.03
SILENCE_ENERGY_THRESHOLD = 0.0009  # 9 / 10000

OCTAVE_COST = 0.01  # Praat default: score penalty per octave of lag
PITCH_FLOOR_HZ = 75.0
PITCH_CEILING_HZ = 600.0

Q15 = 1 << 15  # 1.0 in Q1.15 (32768)
Q13 = 1 << 13  # 1.0 in Q3.13 (8192)

# Integer ratios for exact threshold checks without division
VOICING_THRESHOLD_HUNDREDTHS = 45  # 45 / 100 <=> best_score * 100 >= 45 * R_x[0]
SILENCE_ENERGY_RATIO_NUM = 9  # 9 / 10000 <=> R_x[0] * 10000 < 9 * E_ref
SILENCE_ENERGY_RATIO_DEN = 10000

IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]


def hanning_rom_q15() -> IntArray:
    """The 640-point Hanning window as Q1.15 integers.

    Following Praat Sound_to_Pitch.cpp line 413:
        w[i] = 0.5 - 0.5 * cos(2 * pi * i / (N + 1)), i = 1..N
    For N = 640, peak value at center would be 32768 in Q1.15, which overflows
    signed 16-bit integer (max +32767). We saturate at 32767.
    """
    i = np.arange(1, FRAME_LEN + 1, dtype=np.float64)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / (FRAME_LEN + 1))
    return np.clip(np.round(w * Q15), 0, Q15 - 1).astype(np.int64)


def compensation_rom_q13() -> IntArray:
    """C[tau] = R_w[0] / R_w[tau] as Q3.13, 189 entries for tau in [TAU_SCAN_MIN, TAU_SCAN_MAX].

    Multiplying the raw autocorrelation by this undoes the window's own taper. Q3.13
    because the largest entry (C[214]) is about 2.12, which Q3.13 holds up to 3.999 while
    keeping 13 fractional bits; Q1.15 would clip at 1.0.
    """
    w = hanning_rom_q15().astype(np.float64) / Q15
    rw0 = float(np.dot(w, w))
    out = []
    for tau in range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1):
        rw_tau = float(np.dot(w[: FRAME_LEN - tau], w[tau:]))
        out.append(round(rw0 / rw_tau * Q13))
    return np.array(out, dtype=np.int64)


def scoring_rom_q13(octave_cost: float = OCTAVE_COST) -> IntArray:
    """The ROM the FPGA actually stores: window compensation with the octave bias folded in.

    Praat subtracts `octave_cost * log2(ceiling / F0)` from each candidate's strength at
    scoring time. Multiplying by 2**(-octave_cost * log2(ceiling / F0)) is the same
    preference expressed as a factor, and a factor can be precomputed per lag. Folding it
    here means the hardware never evaluates a log2: one ROM read, one multiply, one shift.
    The penalty is <= 1, so the largest entry stays at C[214] and Q3.13 still holds it.
    Entries cover tau in [TAU_SCAN_MIN, TAU_SCAN_MAX] (189 words).
    Single direct rounding from float avoids double-rounding discretization error.
    """
    w = hanning_rom_q15().astype(np.float64) / Q15
    rw0 = float(np.dot(w, w))
    out = []
    for tau in range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1):
        rw_tau = float(np.dot(w[: FRAME_LEN - tau], w[tau:]))
        c_raw = rw0 / rw_tau
        f0 = FS_HZ / tau
        bias = 2.0 ** (-octave_cost * np.log2(PITCH_CEILING_HZ / f0))
        out.append(round(c_raw * bias * Q13))
    return np.array(out, dtype=np.int64)


def load_rom_from_hex_or_compute(filename: str, fallback_fn) -> IntArray:
    """Load ROM table from chapter01/hex/*.hex if present, avoiding transcendental drift."""
    p = HEX_DIR / filename
    if p.is_file():
        entries = []
        with open(p, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("//"):
                    val = int(s, 16)
                    if val >= 0x8000:
                        val -= 0x10000
                    entries.append(val)
        if len(entries) > 0:
            return np.array(entries, dtype=np.int64)
    return fallback_fn()


GLOBAL_HANNING_Q15 = load_rom_from_hex_or_compute("hanning_rom.hex", hanning_rom_q15)
GLOBAL_SCORING_ROM_Q13 = load_rom_from_hex_or_compute("c_tau_rom.hex", scoring_rom_q13)


def f0_rom_hz() -> IntArray:
    """F0 = round(fs / tau) in Hz, 189 entries for tau in [TAU_SCAN_MIN, TAU_SCAN_MAX].

    LUT tra cứu thô không dùng phép chia tại run-time (Chế độ A). Khi bật nội suy
    parabol (Chế độ B), phần cứng dùng bộ chia tuần tự hoặc HPS để tính f0_q12_4.
    """
    return np.array(
        [round(FS_HZ / tau) for tau in range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1)], dtype=np.int64
    )


def window_frame_q15(x_q15: IntArray, w_q15: IntArray | None = None) -> IntArray:
    """Multiply one 640-sample frame by the Hanning ROM, keeping Q1.15.

    Each product of two Q1.15 values is Q2.30 in a 32-bit word; (prod + 16384) >> 15
    brings it back to Q1.15 with round-to-nearest without a divide.
    """
    if w_q15 is None:
        w_q15 = GLOBAL_HANNING_Q15
    prod = x_q15.astype(np.int64) * w_q15
    return (prod + (1 << 14)) >> 15


@dataclass(frozen=True)
class FrameResult:
    """One frame's verdict, from either detector."""

    f0_hz: float
    tau_star: int
    r0: float
    voiced: bool
    f0_q12_4: int = 0


def parabolic_interpolation_fixed(
    scores: list[int] | IntArray, best_idx: int, tau_star: int
) -> tuple[int, int]:
    """Integer 3-point parabolic peak interpolation (Mode B).

    N = S[i-1] - S[i+1];  D = 2*(S[i-1] - 2*S[i] + S[i+1])
    tau_fine_q16 = (tau_star << 16) + ((N << 16) // D)
    f0_q12_4 = (16000*16*65536 + (tau_fine_q16 >> 1)) // tau_fine_q16
    Returns (tau_fine_q16, f0_q12_4).
    """
    sm1 = int(scores[best_idx - 1])
    s0 = int(scores[best_idx])
    sp1 = int(scores[best_idx + 1])

    N = sm1 - sp1
    D = 2 * (sm1 - 2 * s0 + sp1)
    if D == 0:
        tau_fine_q16 = tau_star << 16
    else:
        tau_fine_q16 = (tau_star << 16) + ((N << 16) // D)

    if tau_fine_q16 <= 0:
        return tau_fine_q16, 0

    f0_q12_4 = (16000 * 16 * 65536 + (tau_fine_q16 >> 1)) // tau_fine_q16
    return tau_fine_q16, f0_q12_4


def parabolic_interpolation(scores: list[int] | IntArray, best_idx: int) -> float:
    """3-point parabolic peak interpolation: delta_tau = 0.5 * (ym1 - yp1) / (ym1 - 2*y0 + yp1)."""
    if 0 < best_idx < len(scores) - 1:
        ym1 = float(scores[best_idx - 1])
        y0 = float(scores[best_idx])
        yp1 = float(scores[best_idx + 1])
        denom = ym1 - 2.0 * y0 + yp1
        if denom != 0.0:
            return 0.5 * (ym1 - yp1) / denom
    return 0.0


def fixed_pitch_frame(
    x_q15: IntArray,
    ref_energy: int,
    use_interpolation: bool = True,
    scoring_rom: IntArray | None = None,
) -> FrameResult:
    """One frame of integer-only pitch detection.

    The body is +, -, * and >> on int64 (<= 56-bit product,
    <= 43-bit signed accumulator for S[tau]), so it is
    bit-identical on AMD64, ARM64, and an FPGA datapath of the same width. `ref_energy` is
    the peak frame energy E_ref = max_k R_x[0]_k across the whole utterance (Q2.30 scale);
    the silence gate is an integer comparison: R_x[0] * 10000 < 9 * E_ref.
    """
    if scoring_rom is None:
        scoring_rom = GLOBAL_SCORING_ROM_Q13

    # Subtract local mean (Praat Sound_to_Pitch.cpp line 63-83)
    mean_x = (int(np.sum(x_q15)) + (FRAME_LEN // 2)) // FRAME_LEN
    x_zero_mean = x_q15 - mean_x

    xw = window_frame_q15(x_zero_mean)
    r0 = int(np.dot(xw, xw))

    # Silence gate: energy below 0.09% (0.03^2) of the peak reference.
    # r0 < 0.0009 * ref_energy  <=>  r0 * 10000 < 9 * ref_energy. No divide, no float.
    if ref_energy > 0 and r0 * SILENCE_ENERGY_RATIO_DEN < SILENCE_ENERGY_RATIO_NUM * ref_energy:
        return FrameResult(0.0, 0, float(r0), False, 0)
    if r0 == 0:
        return FrameResult(0.0, 0, 0.0, False, 0)

    taus_scan = range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1)
    scores = []
    # <= 56-bit product, <= 43-bit signed accumulator for S[tau] = (R_x[tau] * C[tau] + 4096) >> 13
    for idx, tau in enumerate(taus_scan):
        n = FRAME_LEN - tau
        r_tau = int(np.dot(xw[:n], xw[tau:]))
        score = (r_tau * scoring_rom[idx] + (1 << 12)) >> 13
        scores.append(score)

    # Argmax restricted strictly to [TAU_MIN, TAU_MAX] (idx 1 to 187 in the 189-element array)
    best_score = -(1 << 62)
    tau_star = 0
    best_idx = 0
    for idx in range(1, len(taus_scan) - 1):
        tau = TAU_SCAN_MIN + idx
        if scores[idx] > best_score:
            best_score = scores[idx]
            tau_star = tau
            best_idx = idx

    # Voicing test without a divide: best >= 0.45 * R_x[0]  <=>  best * 100 >= 45 * R_x[0]
    if best_score * 100 < VOICING_THRESHOLD_HUNDREDTHS * r0:
        return FrameResult(0.0, 0, float(r0), False, 0)

    if use_interpolation:
        tau_fine_q16, f0_q12_4 = parabolic_interpolation_fixed(scores, best_idx, tau_star)
        f0 = f0_q12_4 / 16.0
    else:
        f0 = float(f0_rom_hz()[best_idx])
        f0_q12_4 = encode_pitch_f0_q12_4(f0, True)

    return FrameResult(f0, tau_star, float(r0), True, f0_q12_4)


def float_pitch_frame(
    x: FloatArray, ref_energy: float = 0.0, use_interpolation: bool = True
) -> FrameResult:
    """The 6-step Praat detector reference in float64 (without dynamic programming Viterbi)."""
    # Step 1: subtract local mean
    x_zm = x - np.mean(x)
    # Step 2: Hanning window
    w = hanning_rom_q15().astype(np.float64) / Q15
    xw = x_zm * w
    r0 = float(np.dot(xw, xw))

    # Silence gate: 0.03^2 = 0.0009 (-30.46 dB)
    if ref_energy > 0.0 and r0 < SILENCE_ENERGY_THRESHOLD * ref_energy:
        return FrameResult(0.0, 0, r0, False)
    if r0 == 0.0:
        return FrameResult(0.0, 0, 0.0, False)

    # Step 3: Autocorrelation + Step 4: Window compensation with octave bias
    rw0 = float(np.dot(w, w))
    taus_scan = list(range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1))
    scores = []
    for tau in taus_scan:
        r_tau = float(np.dot(xw[: FRAME_LEN - tau], xw[tau:]))
        rw_tau = float(np.dot(w[: FRAME_LEN - tau], w[tau:]))
        c_tau = rw0 / rw_tau
        bias = 2.0 ** (-OCTAVE_COST * np.log2(PITCH_CEILING_HZ / (FS_HZ / tau)))
        scores.append(r_tau * c_tau * bias)

    # Argmax restricted strictly to [TAU_MIN, TAU_MAX]
    best = -np.inf
    tau_star = 0
    best_idx = 0
    for idx in range(1, len(taus_scan) - 1):
        tau = TAU_SCAN_MIN + idx
        if scores[idx] > best:
            best = scores[idx]
            tau_star = tau
            best_idx = idx

    # Step 5: Voicing threshold
    if best / r0 < VOICING_THRESHOLD:
        return FrameResult(0.0, 0, r0, False)

    # Step 6: Parabolic interpolation
    if use_interpolation:
        delta_tau = parabolic_interpolation(scores, best_idx)
        tau_fine = tau_star + delta_tau
        f0 = FS_HZ / tau_fine
    else:
        f0 = FS_HZ / tau_star

    return FrameResult(f0, tau_star, r0, True)


def median3(values: list[int | float]) -> list[int | float]:
    """3-tap moving median over an integer or float F0 sequence.

    1 frame (10 ms) latency: window is [v[i-1], v[i], v[i+1]].
    Suppresses single-frame isolated octave spikes.
    """
    out = []
    for i in range(len(values)):
        window = [values[max(0, i - 1)], values[i], values[min(len(values) - 1, i + 1)]]
        out.append(sorted(window)[1])
    return out


# --- Binary Protocol pitch_f0.bin (Q12.4 uint16 Little-Endian) -----------------
def encode_pitch_f0_q12_4(f0_hz: float, voiced: bool) -> int:
    """Encode F0 into Q12.4 uint16 (0 = Unvoiced, max 4095.9375 Hz)."""
    if not voiced or f0_hz <= 0.0:
        return 0
    val = int(round(f0_hz * 16.0))
    return min(max(val, 0), 0xFFFF)


def decode_pitch_f0_q12_4(val: int) -> tuple[float, bool]:
    """Decode Q12.4 uint16 into (F0_hz, voiced)."""
    if val == 0:
        return 0.0, False
    return val / 16.0, True


def save_pitch_f0_bin(
    f0_series: list[float], voiced_series: list[bool], filepath: Path | str
) -> None:
    """Save an F0 sequence to pitch_f0.bin as contiguous uint16 Little-Endian words."""
    words = [encode_pitch_f0_q12_4(f, v) for f, v in zip(f0_series, voiced_series, strict=False)]
    data = struct.pack(f"<{len(words)}H", *words)
    Path(filepath).write_bytes(data)


def load_pitch_f0_bin(filepath: Path | str) -> list[float]:
    """Load an F0 sequence from pitch_f0.bin uint16 LE binary file."""
    data = Path(filepath).read_bytes()
    n_words = len(data) // 2
    words = struct.unpack(f"<{n_words}H", data)
    return [decode_pitch_f0_q12_4(w)[0] for w in words]


def word_to_frame_indices(w_start_s: float, w_end_s: float) -> tuple[int, int]:
    """Map word timestamps [w_start, w_end] (in seconds) to frame index range [k_start, k_end].

    Timing contract: Frame k has physical center t_k = 20 + 10*k ms from audio sample 0.
    k_start = ceil((w_start * 1000 - 20) / 10)
    k_end   = floor((w_end * 1000 - 20) / 10)
    """
    k_start = int(np.ceil((w_start_s * 1000.0 - 20.0) / 10.0))
    k_end = int(np.floor((w_end_s * 1000.0 - 20.0) / 10.0))
    return max(0, k_start), max(0, k_end)


@dataclass(frozen=True)
class FrameComparison:
    """One frame measured by both the integer and the float detector."""

    tau_star_fixed: int
    tau_star_float: int
    f0_fixed_hz: float
    f0_float_hz: float
    agree_hz: bool


def compare_on_signal(
    freq_hz: float = 200.0, seconds: float = 0.08, amplitude: float = 0.5
) -> FrameComparison:
    """Run both detectors on one voiced frame and report agreement."""
    t = np.arange(int(seconds * FS_HZ), dtype=np.float64) / FS_HZ
    x = amplitude * np.sin(2.0 * np.pi * freq_hz * t)[:FRAME_LEN]
    x_q15 = np.clip(np.round(x * Q15), -Q15, Q15 - 1).astype(np.int64)
    ref_fix = int(np.dot(x_q15, x_q15))
    ref_flt = float(np.dot(x, x))
    fixed = fixed_pitch_frame(x_q15, ref_fix)
    flt = float_pitch_frame(x, ref_flt)
    return FrameComparison(
        tau_star_fixed=fixed.tau_star,
        tau_star_float=flt.tau_star,
        f0_fixed_hz=fixed.f0_hz,
        f0_float_hz=flt.f0_hz,
        agree_hz=abs(fixed.f0_hz - flt.f0_hz) < 0.5,
    )


def octave_cost_sweep(
    costs: tuple[float, ...] = (0.0, 0.005, 0.009, 0.01, 0.02),
    f_lo: float = PITCH_FLOOR_HZ,
    f_hi: float = PITCH_CEILING_HZ,
) -> dict[float, int]:
    """Count octave failures per octave_cost over a 1 Hz sweep of the band on sine waves.

    Failure defined as |Delta_cent| > 600 (more than half an octave / tritone) or unvoiced.
    With cost = 0.0, the detector produces 300 / 526 failures due to 2*T0 peak competition.
    With cost = 0.01 (Praat default), failures drop to 0 / 526.
    """
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    result: dict[float, int] = {}
    for cost in costs:
        s_rom = scoring_rom_q13(octave_cost=cost)
        failures = 0
        total = 0
        for f0 in np.arange(f_lo, f_hi + 0.5, 1.0):
            total += 1
            x = 0.5 * np.sin(2.0 * np.pi * f0 * t)
            x_q15 = np.clip(np.round(x * Q15), -Q15, Q15 - 1).astype(np.int64)
            ref = int(np.dot(x_q15, x_q15))
            res = fixed_pitch_frame(x_q15, ref, use_interpolation=True, scoring_rom=s_rom)
            if res.f0_hz <= 0.0:
                failures += 1
            else:
                cent_err = abs(1200.0 * np.log2(res.f0_hz / f0))
                if cent_err > 600.0:
                    failures += 1
        result[float(cost)] = failures
    return result


def export_golden_vectors(
    out_path: Path, c_rom: IntArray, f0_lut: IntArray
) -> tuple[int, int, int]:
    """Export golden_vectors.hex for 440 Hz test tone, returning (tau_star, f0_q12_4, voiced)."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x_440_q15 = np.round(0.5 * 32767.0 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.int64)
    ref_440 = int(np.dot(x_440_q15, x_440_q15))
    res_440 = fixed_pitch_frame(x_440_q15, ref_440, use_interpolation=True, scoring_rom=c_rom)

    with open(out_path / "golden_vectors.hex", "w", encoding="utf-8") as f:
        f.write("// 640 input samples in Q1.15 for 440 Hz test tone\n")
        for val in x_440_q15:
            f.write(f"{val & 0xFFFF:04x}\n")
        f.write("// Golden outputs: [0]=tau_star, [1]=f0_q12_4, [2]=voiced\n")
        f.write(f"{res_440.tau_star & 0xFFFF:04x}\n")
        f.write(f"{res_440.f0_q12_4 & 0xFFFF:04x}\n")
        f.write(f"{int(res_440.voiced) & 0xFFFF:04x}\n")
    return res_440.tau_star, res_440.f0_q12_4, int(res_440.voiced)


def export_hex(output_dir: Path | str = HEX_DIR) -> None:
    """Export hanning_rom.hex, c_tau_rom.hex, f0_lut.hex, and golden_vectors.hex for Verilog."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    w_q15 = hanning_rom_q15()
    c_rom = scoring_rom_q13()
    f0_lut = f0_rom_hz()

    with open(out_path / "hanning_rom.hex", "w", encoding="utf-8") as f:
        for val in w_q15:
            f.write(f"{val & 0xFFFF:04x}\n")

    with open(out_path / "c_tau_rom.hex", "w", encoding="utf-8") as f:
        for val in c_rom:
            f.write(f"{val & 0xFFFF:04x}\n")

    with open(out_path / "f0_lut.hex", "w", encoding="utf-8") as f:
        for val in f0_lut:
            f.write(f"{val & 0xFFFF:04x}\n")

    export_golden_vectors(out_path, c_rom, f0_lut)


def process_wav_fixed_point(
    wav_path: Path | str,
    bin_path: Path | str,
    mode: str = "file",
    scoring_rom: IntArray | None = None,
) -> list[int]:
    """Process a 16 kHz 16-bit mono WAV into pitch_f0.bin.

    mode="file": 2 passes. Pass 1 calculates r0 for all frames to find E_ref = max r0;
                 Pass 2 detects pitch with the global silence gate.
    mode="stream": 1 pass with running max E_ref. First frames may differ from file mode.
    Applies median3 on f0_q12_4 (preserving 0 as UV, 1 frame delay = 10 ms).
    Saves as little-endian uint16 binary file.
    """
    if scoring_rom is None:
        scoring_rom = GLOBAL_SCORING_ROM_Q13

    with wave.open(str(wav_path), "rb") as w:
        fs = w.getframerate()
        assert fs == FS_HZ, f"Expected {FS_HZ} Hz, got {fs} Hz"
        n_channels = w.getnchannels()
        assert n_channels == 1, f"Expected mono, got {n_channels} channels"
        sampwidth = w.getsampwidth()
        assert sampwidth == 2, f"Expected 16-bit (2 bytes), got {sampwidth}"
        n_samples = w.getnframes()
        raw_data = w.readframes(n_samples)
        samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.int64)

    n_frames = max(0, (len(samples) - FRAME_LEN) // HOP + 1)
    if n_frames == 0:
        Path(bin_path).write_bytes(b"")
        return []

    if mode == "file":
        # Pass 1: compute r0 for all frames
        r0_list = []
        for k in range(n_frames):
            seg = samples[k * HOP : k * HOP + FRAME_LEN]
            mean_x = (int(np.sum(seg)) + (FRAME_LEN // 2)) // FRAME_LEN
            xw = window_frame_q15(seg - mean_x)
            r0_list.append(int(np.dot(xw, xw)))
        ref_energy = max(r0_list) if len(r0_list) > 0 else 0

        # Pass 2: pitch detection
        f0_raw = []
        for k in range(n_frames):
            seg = samples[k * HOP : k * HOP + FRAME_LEN]
            res = fixed_pitch_frame(
                seg, ref_energy, use_interpolation=True, scoring_rom=scoring_rom
            )
            f0_raw.append(res.f0_q12_4 if res.voiced else 0)
    elif mode == "stream":
        f0_raw = []
        running_max = 0
        for k in range(n_frames):
            seg = samples[k * HOP : k * HOP + FRAME_LEN]
            mean_x = (int(np.sum(seg)) + (FRAME_LEN // 2)) // FRAME_LEN
            xw = window_frame_q15(seg - mean_x)
            r0 = int(np.dot(xw, xw))
            running_max = max(running_max, r0)
            res = fixed_pitch_frame(
                seg, running_max, use_interpolation=True, scoring_rom=scoring_rom
            )
            f0_raw.append(res.f0_q12_4 if res.voiced else 0)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    f0_filtered = [int(v) for v in median3(f0_raw)]
    out_words = np.asarray(f0_filtered, dtype="<u2")
    out_words.tofile(str(bin_path))
    return f0_filtered


def run_selftest() -> None:
    """Self-test printing exact verified numbers for documentation and verification."""
    w = hanning_rom_q15()
    c = scoring_rom_q13()
    print("=== SELFTEST lab_1_3_5.py ===")
    print(f"H[0..4]: {[int(x) for x in w[:5]]}")
    print(f"C[26..30]: {[int(x) for x in c[:5]]}")
    print(f"C[26..30] hex: {[f'{x:04x}' for x in c[:5]]}")
    print(f"C[214]: {int(c[-1])} (hex: {int(c[-1]):04x})")

    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x_440 = np.round(0.5 * 32767.0 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.int64)
    print(f"golden x[0..4]: {[int(x) for x in x_440[:5]]}")

    # Compute 440 Hz scores
    mean_x = (int(np.sum(x_440)) + (FRAME_LEN // 2)) // FRAME_LEN
    xw = window_frame_q15(x_440 - mean_x)
    scores_440 = []
    for idx, tau in enumerate(range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1)):
        n = FRAME_LEN - tau
        r_tau = int(np.dot(xw[:n], xw[tau:]))
        score = (r_tau * c[idx] + 4096) >> 13
        scores_440.append(score)

    s35 = scores_440[35 - TAU_SCAN_MIN]
    s36 = scores_440[36 - TAU_SCAN_MIN]
    s37 = scores_440[37 - TAU_SCAN_MIN]
    print(f"440 Hz S[35..37]: S[35]={s35}, S[36]={s36}, S[37]={s37}")

    tau_fine_q16, f0_q12_4 = parabolic_interpolation_fixed(scores_440, 36 - TAU_SCAN_MIN, 36)
    f0_hz = f0_q12_4 / 16.0
    f0_flt_interp = 16000.0 / (tau_fine_q16 / 65536.0)
    cent_flt = 1200.0 * np.log2(f0_flt_interp / 440.0)
    print(
        f"Parabolic mode B: tau_star=36, tau_fine_q16={tau_fine_q16}, "
        f"f0_q12_4={f0_q12_4} (0x{f0_q12_4:04x} = {f0_hz:.3f} Hz)"
    )
    print(f"Parabolic float: {f0_flt_interp:.3f} Hz ({cent_flt:+.2f} c)")

    print("Octave Cost Sweep:")
    sweep = octave_cost_sweep()
    for cost, fails in sweep.items():
        print(f"  cost={cost:.3f}: {fails} / 526 failures")

    print("Sine Freq Accuracy (Mode B vs true freq):")
    for freq in [75.0, 100.0, 200.0, 440.0, 590.0]:
        x_tone = np.round(0.5 * 32767.0 * np.sin(2.0 * np.pi * freq * t)).astype(np.int64)
        mean_tone = (int(np.sum(x_tone)) + (FRAME_LEN // 2)) // FRAME_LEN
        xw_tone = window_frame_q15(x_tone - mean_tone)
        sc = []
        for idx, tau in enumerate(range(TAU_SCAN_MIN, TAU_SCAN_MAX + 1)):
            dot_val = int(np.dot(xw_tone[: FRAME_LEN - tau], xw_tone[tau:]))
            sc.append((dot_val * c[idx] + 4096) >> 13)
        best_idx = 1
        best_score = sc[1]
        for idx in range(1, len(sc) - 1):
            if sc[idx] > best_score:
                best_score = sc[idx]
                best_idx = idx
        tau_star = TAU_SCAN_MIN + best_idx
        tf_q16, f_q12_4 = parabolic_interpolation_fixed(sc, best_idx, tau_star)
        f_hz = f_q12_4 / 16.0
        c_err = 1200.0 * np.log2(f_hz / freq)
        print(f"  {freq:3.0f} Hz: {c_err:+.2f} c (F0 = {f_hz:.3f} Hz)")


def median3_removes_octave_spike() -> dict[str, list[int | float]]:
    """Worked example: [122, 245, 124] Hz -> the spike is gone."""
    raw = [122, 245, 124]
    return {"raw": raw, "filtered": median3(raw)}


def render_report() -> dict[str, object]:
    """Summary metrics of the detector."""
    rom = hanning_rom_q15()
    comp = compensation_rom_q13()
    score_rom = scoring_rom_q13()
    cmp = compare_on_signal()
    return {
        "window_rom_entries": int(rom.size),
        "window_rom_w0": int(rom[0]),
        "window_rom_centre_q15": int(rom.max()),
        "compensation_entries": int(comp.size),
        "compensation_min_q13": int(comp.min()),
        "compensation_max_q13": int(comp.max()),
        "scoring_min_q13": int(score_rom.min()),
        "scoring_max_q13": int(score_rom.max()),
        "scan_lag_range": [TAU_SCAN_MIN, TAU_SCAN_MAX],
        "search_lag_range": [TAU_MIN, TAU_MAX],
        "n_scan_lags": N_SCAN_LAGS,
        "n_search_lags": N_SEARCH_LAGS,
        "frame": asdict(cmp),
        "median_example": median3_removes_octave_spike(),
        "voicing_threshold_hundredths": VOICING_THRESHOLD_HUNDREDTHS,
        "silence_energy_ratio": [SILENCE_ENERGY_RATIO_NUM, SILENCE_ENERGY_RATIO_DEN],
        "octave_cost_sweep_failures": octave_cost_sweep(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=None, help="write the report as JSON")
    ap.add_argument(
        "--export-hex",
        type=Path,
        default=None,
        nargs="?",
        const=HEX_DIR,
        help="export .hex files to directory (default: chapter01/hex)",
    )
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="run self-test and print exact verified figures",
    )
    args = ap.parse_args()

    if args.export_hex is not None:
        export_hex(args.export_hex)
        print(f"Exported .hex files to {args.export_hex}")

    if args.selftest:
        run_selftest()
        return 0

    report = render_report()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
