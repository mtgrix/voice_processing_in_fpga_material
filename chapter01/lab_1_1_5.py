"""Lab 1.1.5: the microphone mute and the high-pass in front of section 1.2.

The numbers this section prints are derived here, from the INMP441 clock rule and
from the Audio EQ Cookbook high-pass. Nothing in this file is a bench recording.
"""

from __future__ import annotations

import argparse
import json
import platform
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parent.parent

# DS-INMP441-00 rev 1.1. The startup sentence's "218" is 2^18: 2^18 cycles of
# the stated 3.072 MHz clock is 85.33 ms, which the datasheet rounds to 85 ms.
MUTE_CLOCKS = 1 << 18
DATASHEET_SCK_HZ = 3_072_000.0
CLOCKS_PER_FRAME = 64  # "f_SCK = 64 x f_WS", Data Word Length
FS_HZ = 16_000
FC_HZ = 60.0
# Butterworth, so the passband does not peak. The cookbook still needs a Q.
Q_BUTTERWORTH = float(1.0 / np.sqrt(2.0))
# Table 7, digital high-pass at a nominal 48 kHz. Cutoff scales with fs.
INTERNAL_FS_HZ = 48_000.0
INTERNAL_TABLE_HZ = (3.7, 10.4, 21.6)
HOP_SAMPLES = 160
SETTLE_THRESHOLD = 0.01
TONE_HZ = 200.0
OFFSET = 0.2
TONE_AMPLITUDE = 0.3
CONSTRUCTED_SECONDS = 0.08

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Mute:
    """Power-up mute implied by the datasheet clock rule at one sample rate."""

    mute_clocks: int
    clocks_per_frame: int
    fs_hz: int
    sck_hz: float
    mute_s: float
    mute_samples: int
    hops: float
    datasheet_example_ms: float


@dataclass(frozen=True)
class Highpass:
    """Normalized cookbook high-pass and a few probes of it."""

    fs_hz: int
    fc_hz: float
    q: float
    b0: float
    b1: float
    b2: float
    a1: float
    a2: float
    gain_at_dc: float
    db_at_20_hz: float
    db_at_40_hz: float
    db_at_60_hz: float
    db_at_80_hz: float
    db_at_85_hz: float
    db_at_300_hz: float
    settle_samples: int
    settle_ms: float
    constructed_mean_in: float
    constructed_mean_tail: float
    constructed_tone_rms_in: float
    constructed_tone_rms_tail: float


def mute_at(fs_hz: int = FS_HZ) -> Mute:
    """Return the mute duration when each output frame takes 64 bit clocks."""
    sck_hz = float(CLOCKS_PER_FRAME * fs_hz)
    mute_s = MUTE_CLOCKS / sck_hz
    return Mute(
        mute_clocks=MUTE_CLOCKS,
        clocks_per_frame=CLOCKS_PER_FRAME,
        fs_hz=fs_hz,
        sck_hz=sck_hz,
        mute_s=mute_s,
        mute_samples=int(round(mute_s * fs_hz)),
        hops=mute_s * fs_hz / HOP_SAMPLES,
        datasheet_example_ms=MUTE_CLOCKS / DATASHEET_SCK_HZ * 1_000.0,
    )


def scale_internal_hpf(fs_hz: int = FS_HZ) -> tuple[float, float, float]:
    """Scale Table 7 from its 48 kHz nominal rate down to fs_hz."""
    ratio = fs_hz / INTERNAL_FS_HZ
    low, mid, high = INTERNAL_TABLE_HZ
    return (low * ratio, mid * ratio, high * ratio)


def cookbook_highpass(fs_hz: float, fc_hz: float, q: float) -> tuple[FloatArray, FloatArray]:
    """Audio EQ Cookbook high-pass, normalized so a0 = 1.

    H(z) = (b0 + b1 z^{-1} + b2 z^{-2}) / (1 + a1 z^{-1} + a2 z^{-2}).
    """
    w0 = 2.0 * np.pi * fc_hz / fs_hz
    alpha = np.sin(w0) / (2.0 * q)
    cos_w0 = np.cos(w0)
    b0 = (1.0 + cos_w0) / 2.0
    b1 = -(1.0 + cos_w0)
    b2 = (1.0 + cos_w0) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cos_w0
    a2 = 1.0 - alpha
    b = np.array([b0, b1, b2], dtype=np.float64) / a0
    a = np.array([1.0, a1 / a0, a2 / a0], dtype=np.float64)
    return b, a


def linear_gain(b: FloatArray, a: FloatArray, freq_hz: float, fs_hz: float) -> float:
    """Magnitude of H at one frequency. Exact zero at DC returns 0."""
    if freq_hz == 0.0:
        return float(abs(b[0] + b[1] + b[2]) / abs(a[0] + a[1] + a[2]))
    z = np.exp(-1j * 2.0 * np.pi * freq_hz / fs_hz)
    numerator = b[0] + b[1] * z + b[2] * z**2
    denominator = a[0] + a[1] * z + a[2] * z**2
    return float(np.abs(numerator / denominator))


def db(gain: float) -> float:
    """20 log10 of a magnitude. A true zero is reported as a large negative."""
    if gain <= 0.0:
        return -300.0
    return float(20.0 * np.log10(gain))


def apply_biquad(b: FloatArray, a: FloatArray, samples: FloatArray) -> FloatArray:
    """Transposed direct form II. The two delays start at zero."""
    out = np.empty(samples.size, dtype=np.float64)
    z1 = 0.0
    z2 = 0.0
    b0, b1, b2 = float(b[0]), float(b[1]), float(b[2])
    a1, a2 = float(a[1]), float(a[2])
    for index, sample in enumerate(samples.tolist()):
        y = b0 * sample + z1
        z1 = b1 * sample - a1 * y + z2
        z2 = b2 * sample - a2 * y
        out[index] = y
    return out


def step_settle_samples(
    b: FloatArray,
    a: FloatArray,
    threshold: float = SETTLE_THRESHOLD,
    hold: int = HOP_SAMPLES,
    limit: int = FS_HZ,
) -> int:
    """Index of the first sample of a quiet run on a unit step.

    Quiet means |y| stayed under the threshold for one hop. The two delays
    start at zero, which is the state a filter has before the first sample.
    """
    filtered = apply_biquad(b, a, np.ones(limit, dtype=np.float64))
    quiet = 0
    for index, sample in enumerate(filtered.tolist()):
        if abs(float(sample)) < threshold:
            quiet += 1
            if quiet >= hold:
                return index - hold + 1
        else:
            quiet = 0
    raise RuntimeError("unit step did not stay under the threshold for one hop")


def _tail_rms(samples: FloatArray, tone_hz: float, fs_hz: float, start: int) -> float:
    """RMS of the component at tone_hz, on samples[start:]."""
    segment = samples[start:]
    n = np.arange(segment.size, dtype=np.float64)
    phase = 2.0 * np.pi * tone_hz * n / fs_hz
    cosine = float(np.dot(segment, np.cos(phase)) * 2.0 / segment.size)
    sine = float(np.dot(segment, np.sin(phase)) * 2.0 / segment.size)
    return float(np.hypot(cosine, sine) / np.sqrt(2.0))


def analyze_highpass() -> Highpass:
    """Coefficients, probe gains, settling, and one constructed offset-plus-tone."""
    b, a = cookbook_highpass(float(FS_HZ), FC_HZ, Q_BUTTERWORTH)
    probes = {
        freq: db(linear_gain(b, a, float(freq), float(FS_HZ))) for freq in (20, 40, 60, 80, 85, 300)
    }
    settle = step_settle_samples(b, a)
    n = np.arange(int(CONSTRUCTED_SECONDS * FS_HZ), dtype=np.float64)
    raw = OFFSET + TONE_AMPLITUDE * np.sin(2.0 * np.pi * TONE_HZ * n / FS_HZ)
    filtered = apply_biquad(b, a, raw)
    return Highpass(
        fs_hz=FS_HZ,
        fc_hz=FC_HZ,
        q=Q_BUTTERWORTH,
        b0=float(b[0]),
        b1=float(b[1]),
        b2=float(b[2]),
        a1=float(a[1]),
        a2=float(a[2]),
        gain_at_dc=linear_gain(b, a, 0.0, float(FS_HZ)),
        db_at_20_hz=probes[20],
        db_at_40_hz=probes[40],
        db_at_60_hz=probes[60],
        db_at_80_hz=probes[80],
        db_at_85_hz=probes[85],
        db_at_300_hz=probes[300],
        settle_samples=settle,
        settle_ms=settle / FS_HZ * 1_000.0,
        constructed_mean_in=float(np.mean(raw)),
        constructed_mean_tail=float(np.mean(filtered[settle:])),
        constructed_tone_rms_in=_tail_rms(raw, TONE_HZ, float(FS_HZ), settle),
        constructed_tone_rms_tail=_tail_rms(filtered, TONE_HZ, float(FS_HZ), settle),
    )


def render_figure(path: Path, highpass: Highpass) -> None:
    """Magnitude curve and the constructed offset-plus-tone. Units only, no title."""
    b, a = cookbook_highpass(float(FS_HZ), FC_HZ, Q_BUTTERWORTH)
    freqs = np.linspace(5.0, 400.0, 2000)
    gains = np.array([db(linear_gain(b, a, float(freq), float(FS_HZ))) for freq in freqs])

    n = np.arange(int(CONSTRUCTED_SECONDS * FS_HZ), dtype=np.float64)
    raw = OFFSET + TONE_AMPLITUDE * np.sin(2.0 * np.pi * TONE_HZ * n / FS_HZ)
    filtered = apply_biquad(b, a, raw)
    time_ms = n / FS_HZ * 1_000.0

    fig, (ax_mag, ax_time) = plt.subplots(1, 2, figsize=(7.4, 2.8))
    ax_mag.plot(freqs, gains, color="#1a1a1a", linewidth=1.4)
    ax_mag.axvline(60.0, color="#c45c26", linewidth=0.9, linestyle="--")
    ax_mag.axvline(85.0, color="#1f4e79", linewidth=0.9, linestyle="--")
    ax_mag.axvline(300.0, color="#2d6a4f", linewidth=0.9, linestyle="--")
    ax_mag.text(48, -37.5, "60", color="#c45c26", fontsize=7, ha="right")
    ax_mag.text(88, -37.5, "85", color="#1f4e79", fontsize=7, ha="left")
    ax_mag.text(292, -37.5, "300", color="#2d6a4f", fontsize=7, ha="right")
    ax_mag.set_xlim(0.0, 400.0)
    ax_mag.set_ylim(-40.0, 5.0)
    ax_mag.set_xlabel("Hz")
    ax_mag.set_ylabel("dB")
    ax_mag.grid(True, linestyle="--", alpha=0.4)

    ax_time.plot(time_ms, raw, color="#9aa0a6", linewidth=0.8, label="$x$")
    ax_time.plot(time_ms, filtered, color="#1a1a1a", linewidth=1.1, label="$y$")
    ax_time.axvline(highpass.settle_ms, color="#c45c26", linewidth=0.9, linestyle="--")
    ax_time.set_xlim(0.0, CONSTRUCTED_SECONDS * 1_000.0)
    ax_time.set_xlabel("ms")
    ax_time.set_ylabel("amplitude")
    ax_time.grid(True, linestyle="--", alpha=0.4)
    ax_time.legend(frameon=False, fontsize=7)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def report_lines(mute: Mute, highpass: Highpass, scaled: tuple[float, float, float]) -> list[str]:
    """Stable text report. The section quotes these lines, not a hand copy."""
    return [
        f"mute_clocks {mute.mute_clocks}",
        f"clocks_per_frame {mute.clocks_per_frame}",
        f"sck_hz {mute.sck_hz:.1f}",
        f"mute_s {mute.mute_s:.6f}",
        f"mute_samples {mute.mute_samples}",
        f"hops {mute.hops:.4f}",
        f"datasheet_example_ms {mute.datasheet_example_ms:.4f}",
        f"internal_scaled_hz {scaled[0]:.4f} {scaled[1]:.4f} {scaled[2]:.4f}",
        f"q {highpass.q:.6f}",
        f"b0 {highpass.b0:.6f}",
        f"b1 {highpass.b1:.6f}",
        f"b2 {highpass.b2:.6f}",
        f"a1 {highpass.a1:.6f}",
        f"a2 {highpass.a2:.6f}",
        f"gain_at_dc {highpass.gain_at_dc:.3e}",
        f"db_at_20_hz {highpass.db_at_20_hz:.2f}",
        f"db_at_40_hz {highpass.db_at_40_hz:.2f}",
        f"db_at_60_hz {highpass.db_at_60_hz:.2f}",
        f"db_at_80_hz {highpass.db_at_80_hz:.2f}",
        f"db_at_85_hz {highpass.db_at_85_hz:.2f}",
        f"db_at_300_hz {highpass.db_at_300_hz:.2f}",
        f"settle_samples {highpass.settle_samples}",
        f"settle_ms {highpass.settle_ms:.3f}",
        f"constructed_mean_in {highpass.constructed_mean_in:.4f}",
        f"constructed_mean_tail {highpass.constructed_mean_tail:.4f}",
        f"constructed_tone_rms_in {highpass.constructed_tone_rms_in:.4f}",
        f"constructed_tone_rms_tail {highpass.constructed_tone_rms_tail:.4f}",
        "multiplies_per_sample 5",
        f"multiplies_per_second {5 * FS_HZ}",
    ]


def main(argv: list[str] | None = None) -> int:
    """Print the report, write the figure, and optionally capture a result log."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--figure",
        type=Path,
        default=ROOT / "chapter01" / "fig_1_1_5_response.pdf",
    )
    parser.add_argument("--capture-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    mute = mute_at()
    scaled = scale_internal_hpf()
    highpass = analyze_highpass()
    lines = report_lines(mute, highpass, scaled)
    print("\n".join(lines))
    render_figure(args.figure, highpass)
    print(f"figure {args.figure}")

    if args.capture_dir is not None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        out = args.capture_dir / stamp
        out.mkdir(parents=True, exist_ok=True)
        payload = {
            "captured_utc": stamp,
            "environment": {
                "numpy": np.__version__,
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "mute": asdict(mute),
            "internal_scaled_hz": list(scaled),
            "highpass": asdict(highpass),
            "multiplies_per_sample": 5,
            "multiplies_per_second": 5 * FS_HZ,
        }
        (out / "result.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (out / "stdout.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"capture {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
