"""Lab 1.3.5: a bit-accurate fixed-point pitch detector, and its float reference.

The point of this file is the claim section 1.3.5 makes in prose: that the autocorrelation
pitch detector can be written with nothing but `+`, `-`, `*` and `>>` on two's-complement
integers, and that such a program returns the same bits on every machine and on the FPGA.
`fixed_pitch_frame` is that program. `float_pitch_frame` is the same algorithm in float64,
used only to measure how far the integers drift from it.

Nothing here is a bench recording. Every constant is derived from the section's design
(frame 640 samples, hop 160, lag range [27, 213]) or from Praat's published defaults.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parent.parent

# --- Design constants, all fixed by section 1.3.5 -------------------------------
FS_HZ = 16_000
FRAME_LEN = 640  # 40 ms: three periods of the 75 Hz floor
HOP = 160  # 10 ms
TAU_MIN = 27  # ceil(fs / 600 Hz ceiling)
TAU_MAX = 213  # floor(fs / 75 Hz floor)
VOICING_THRESHOLD = 0.45  # Praat default; the integer test is on hundredths
SILENCE_THRESHOLD = 0.03  # Praat default; frame energy floor, also in hundredths
OCTAVE_COST = 0.01  # Praat default: score penalty per octave of lag
PITCH_FLOOR_HZ = 75.0
PITCH_CEILING_HZ = 600.0

Q15 = 1 << 15  # 1.0 in Q1.15
Q13 = 1 << 13  # 1.0 in Q3.13
WINDOW_ROM = 320  # Hanning is symmetric: 640 points fold into 320 entries

# 45 and 3 as exact integers, so the two threshold comparisons never divide.
VOICING_THRESHOLD_HUNDREDTHS = int(round(VOICING_THRESHOLD * 100))
SILENCE_THRESHOLD_HUNDREDTHS = int(round(SILENCE_THRESHOLD * 100))

IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]


def hanning_rom_q15() -> IntArray:
    """The 320-entry symmetric Hanning window as Q1.15 integers.

    Praat builds its window as 0.5 - 0.5*cos(2*pi*i/(N+1)); the section's ROM folds that
    to half length because w[i] == w[N-1-i]. Rounding to nearest means the table is the
    closest integer to the real coefficient, which is what a synthesisable ROM holds.
    """
    n = np.arange(WINDOW_ROM, dtype=np.float64)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * n / (FRAME_LEN - 1))
    return np.round(w * Q15).astype(np.int64)


def full_hanning_q15() -> IntArray:
    """The 640-point window reconstructed from the folded 320-entry ROM."""
    half = hanning_rom_q15()
    return np.concatenate([half, half[::-1]])


def compensation_rom_q13() -> IntArray:
    """C[tau] = R_w[0] / R_w[tau] as Q3.13, one entry per lag in [TAU_MIN, TAU_MAX].

    Multiplying the raw autocorrelation by this undoes the window's own taper. Q3.13
    because the largest entry (C[213]) is about 2.12, which Q3.13 holds up to 4.0 while
    keeping 13 fractional bits; Q1.15 would clip at 1.0.
    """
    w = full_hanning_q15().astype(np.float64) / Q15
    rw0 = float(np.dot(w, w))
    out = []
    for tau in range(TAU_MIN, TAU_MAX + 1):
        rw_tau = float(np.dot(w[: FRAME_LEN - tau], w[tau:]))
        out.append(round(rw0 / rw_tau * Q13))
    return np.array(out, dtype=np.int64)


def scoring_rom_q13(octave_cost: float = OCTAVE_COST) -> IntArray:
    """The ROM the FPGA actually stores: window compensation with the octave bias folded in.

    Praat subtracts `octave_cost * log2(ceiling / F0)` from each candidate's strength at
    scoring time. Multiplying by 2**(-octave_cost * log2(ceiling / F0)) is the same
    preference expressed as a factor, and a factor can be precomputed per lag. Folding it
    here means the hardware never evaluates a log2: one ROM read, one multiply, one shift.
    The penalty is <= 1, so the largest entry stays at C[213] and Q3.13 still holds it.
    """
    base = compensation_rom_q13().astype(np.float64) / Q13
    out = []
    for idx, tau in enumerate(range(TAU_MIN, TAU_MAX + 1)):
        f0 = FS_HZ / tau
        out.append(round(base[idx] * 2.0 ** (-octave_cost * np.log2(PITCH_CEILING_HZ / f0)) * Q13))
    return np.array(out, dtype=np.int64)


def f0_rom_hz() -> IntArray:
    """F0 = round(fs / tau) in Hz, one entry per lag in [TAU_MIN, TAU_MAX].

    This is the divider replaced by a table: when the peak search returns tau*, the
    address tau* - TAU_MIN indexes straight to a frequency, no division at run time.
    """
    return np.array([round(FS_HZ / tau) for tau in range(TAU_MIN, TAU_MAX + 1)], dtype=np.int64)


def window_frame_q15(x_q15: IntArray) -> IntArray:
    """Multiply one 640-sample frame by the Hanning ROM, keeping Q1.15.

    Each product of two Q1.15 values is Q2.30 in a 32-bit word; >> 15 brings it back to
    Q1.15 without a divide. This is the only place the window is applied, which is the
    correction Figure 1.3.5e makes against the naive pipeline.
    """
    prod = x_q15.astype(np.int64) * full_hanning_q15()
    return prod >> 15


@dataclass(frozen=True)
class FrameResult:
    """One frame's verdict, from either detector."""

    f0_hz: float
    tau_star: int
    r0: float
    voiced: bool


def fixed_pitch_frame(x_q15: IntArray, ref_energy: int) -> FrameResult:
    """One frame of integer-only pitch detection.

    The body is +, -, * and >> on int64, so it is bit-identical on AMD64, ARM64, and an
    FPGA datapath of the same width. `ref_energy` is the peak frame energy seen so far,
    in the same Q2.30 scale as R_x[0]; the silence gate is a comparison against it and
    introduces no float.
    """
    xw = window_frame_q15(x_q15)
    r0 = int(np.dot(xw, xw))

    # Silence gate: energy below 3% of the running reference. As integers,
    # r0 < 0.03 * ref  <=>  r0 * 100 < 3 * ref. No divide, no float.
    if ref_energy > 0 and r0 * 100 < SILENCE_THRESHOLD_HUNDREDTHS * ref_energy:
        return FrameResult(0.0, 0, float(r0), False)
    if r0 == 0:
        return FrameResult(0.0, 0, 0.0, False)

    comp = scoring_rom_q13()
    best_score = -(1 << 62)
    tau_star = 0
    for idx, tau in enumerate(range(TAU_MIN, TAU_MAX + 1)):
        n = FRAME_LEN - tau
        r_tau = int(np.dot(xw[:n], xw[tau:]))
        # score = R_x[tau] * C[tau]; >> 13 restores scale after the Q3.13 multiply.
        score = (r_tau * comp[idx]) >> 13
        if score > best_score:
            best_score = score
            tau_star = tau

    # Voicing test without a divide: best >= 0.45 * R_x[0]  <=>  best * 100 >= 45 * R_x[0]
    if best_score * 100 < VOICING_THRESHOLD_HUNDREDTHS * r0:
        return FrameResult(0.0, 0, float(r0), False)

    f0 = float(f0_rom_hz()[tau_star - TAU_MIN])
    return FrameResult(f0, tau_star, float(r0), True)


def float_pitch_frame(x: FloatArray) -> FrameResult:
    """The same detector in float64, as the reference to measure integer drift against."""
    w = full_hanning_q15().astype(np.float64) / Q15
    xw = x * w
    r0 = float(np.dot(xw, xw))
    if r0 == 0.0:
        return FrameResult(0.0, 0, 0.0, False)
    rw0 = float(np.dot(w, w))
    best = -np.inf
    tau_star = 0
    for tau in range(TAU_MIN, TAU_MAX + 1):
        r_tau = float(np.dot(xw[: FRAME_LEN - tau], xw[tau:]))
        rw_tau = float(np.dot(w[: FRAME_LEN - tau], w[tau:]))
        score = r_tau * (rw0 / rw_tau)
        if score > best:
            best = score
            tau_star = tau
    if best / r0 < VOICING_THRESHOLD:
        return FrameResult(0.0, 0, r0, False)
    return FrameResult(FS_HZ / tau_star, tau_star, r0, True)


def median3(values: list[int]) -> list[int]:
    """3-tap moving median over an integer F0 sequence.

    This is the FPGA replacement for Viterbi: three registers and two compares, one frame
    of latency, and a single-frame octave spike cannot survive it. A median is not a mean,
    so a spike that lasts one sample is removed rather than averaged into its neighbours.
    """
    out = []
    for i in range(len(values)):
        window = [values[max(0, i - 1)], values[i], values[min(len(values) - 1, i + 1)]]
        out.append(sorted(window)[1])
    return out


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
    """Run both detectors on one voiced frame and report whether they agree.

    A 200 Hz tone is the section's worked example: T0 = 80 samples, comfortably inside
    [27, 213], so a disagreement here is arithmetic and not a design decision.
    """
    t = np.arange(int(seconds * FS_HZ), dtype=np.float64) / FS_HZ
    x = amplitude * np.sin(2.0 * np.pi * freq_hz * t)[:FRAME_LEN]
    x_q15 = np.round(x * Q15).astype(np.int64)
    ref = int(np.dot(x_q15, x_q15))
    fixed = fixed_pitch_frame(x_q15, ref)
    flt = float_pitch_frame(x)
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
    """Count Lagrange octave failures per octave_cost over a 1 Hz sweep of the band.

    A failure is a frame whose winning lag is more than half an octave away from the
    true period. This is the measurement behind the claim that Praat's 0.01 is neither
    arbitrary nor generous: it is the smallest value on a practical grid that clears the
    band, and the sweep reports how much room is left above it.
    """
    w = full_hanning_q15().astype(np.float64) / Q15
    rw0 = float(np.dot(w, w))
    taus = np.arange(TAU_MIN, TAU_MAX + 1)
    c_base = np.array([rw0 / float(np.dot(w[: FRAME_LEN - t], w[t:])) for t in taus])
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    result: dict[float, int] = {}
    for cost in costs:
        bias = 2.0 ** (-cost * np.log2(PITCH_CEILING_HZ / (FS_HZ / taus)))
        failures = 0
        for f0 in np.arange(f_lo, f_hi + 0.5, 1.0):
            xw = 0.5 * np.sin(2.0 * np.pi * f0 * t) * w
            r0 = float(np.dot(xw, xw))
            scores = (
                np.array(
                    [
                        float(np.dot(xw[: FRAME_LEN - tau], xw[tau:])) * c_base[i] / r0
                        for i, tau in enumerate(taus)
                    ]
                )
                * bias
            )
            if abs(taus[int(np.argmax(scores))] - FS_HZ / f0) > 0.5 * FS_HZ / f0:
                failures += 1
        result[float(cost)] = failures
    return result


def median3_removes_octave_spike() -> dict[str, list[int]]:
    """The section's worked example: [122, 245, 124] Hz -> the spike is gone."""
    raw = [122, 245, 124]
    return {"raw": raw, "filtered": median3(raw)}


def render_report() -> dict[str, object]:
    """Everything the section prints, computed rather than asserted."""
    rom = hanning_rom_q15()
    comp = compensation_rom_q13()
    cmp = compare_on_signal()
    return {
        "window_rom_entries": int(rom.size),
        "window_rom_w0": int(rom[0]),
        "window_rom_centre_q15": int(rom.max()),
        "compensation_entries": int(comp.size),
        "compensation_min_q13": int(comp.min()),
        "compensation_max_q13": int(comp.max()),
        "lag_range": [TAU_MIN, TAU_MAX],
        "n_lags": TAU_MAX - TAU_MIN + 1,
        "frame": asdict(cmp),
        "median_example": median3_removes_octave_spike(),
        "voicing_threshold_hundredths": VOICING_THRESHOLD_HUNDREDTHS,
        "octave_cost_sweep_failures": octave_cost_sweep(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=None, help="write the report as JSON")
    args = ap.parse_args()
    report = render_report()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
