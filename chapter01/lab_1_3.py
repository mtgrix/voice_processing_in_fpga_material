"""Lab 1.3: Mathematical Modeling of Streaming STFT and Mel Filterbank.

Demonstrates and verifies each stage of acoustic feature extraction on:
1. A reference 440 Hz tone (datasets/sample_tone440.wav)
2. Speech utterances from Speech Commands (datasets/sample_speech_a.wav, sample_speech_b.wav)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chapter01.exp_01_streaming_audio_pipeline import (  # noqa: E402
    AudioConfig,
    create_mel_filterbank,
    hz_to_mel,
    mel_to_hz,
)


def sha256_file(path: Path | str) -> str:
    """Compute SHA256 digest of a file on disk."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ensure_tone_file(path: Path) -> None:
    """Ensure datasets/sample_tone440.wav exists on disk; synthesize if absent."""
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fs = 16000
    duration = 1.0
    n = np.arange(int(fs * duration))
    # 1.0 s tone: cos(2*pi*440*n/16000), 16000 Hz, mono, int16
    tone_int16 = np.round(np.cos(2.0 * np.pi * 440.0 * n / fs) * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(tone_int16.tobytes())


def load_wav(path: Path | str) -> tuple[np.ndarray, int]:
    """Load a 16 kHz mono WAV file, returning normalized float32 samples in [-1.0, 1.0]."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Missing WAV file: {p}")
    with wave.open(str(p), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if n_channels != 1:
        raise ValueError(f"Expected mono audio, got {n_channels} channels")
    if sampwidth != 2:
        raise ValueError(f"Expected 16-bit PCM, got {sampwidth * 8}-bit")
    if framerate != 16000:
        raise ValueError(f"Expected 16000 Hz sample rate, got {framerate} Hz")

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return samples, framerate


def window_frame(
    signal: np.ndarray, start_idx: int = 0, win_length: int = 400
) -> tuple[np.ndarray, np.ndarray]:
    """Extract and window a frame using a Hamming window."""
    if len(signal) < start_idx + win_length:
        raise ValueError(f"Signal length {len(signal)} is shorter than required frame range")
    raw_frame = signal[start_idx : start_idx + win_length]
    w = np.hamming(win_length).astype(np.float32)
    return raw_frame * w, w


def probe_sums(frame: np.ndarray, k: int = 14, n_fft: int = 512) -> tuple[float, float]:
    """Compute discrete cosine and sine probe sums for frequency bin k."""
    n = np.arange(len(frame))
    cos_probe = np.cos(2.0 * np.pi * k * n / n_fft)
    sin_probe = -np.sin(2.0 * np.pi * k * n / n_fft)
    cos_sum = float(np.sum(frame * cos_probe))
    sin_sum = float(np.sum(frame * sin_probe))
    return cos_sum, sin_sum


def stft_power(frame: np.ndarray, n_fft: int = 512) -> tuple[np.ndarray, np.ndarray]:
    """Compute one-sided STFT complex bins and power spectrum with zero-padding."""
    padded = np.zeros(n_fft, dtype=np.float32)
    padded[: len(frame)] = frame
    X = np.fft.rfft(padded, n=n_fft)
    P = (np.abs(X) ** 2).astype(np.float32)
    return X, P


def mel_edges(config: AudioConfig) -> tuple[np.ndarray, np.ndarray, int, float, float]:
    """Compute Mel filterbank matrix, bin edges, collapsed count, mel(8000), and mel step."""
    mel_min = float(hz_to_mel(config.f_min))
    mel_max = float(hz_to_mel(config.f_max if config.f_max is not None else 8000.0))
    mel_points = np.linspace(mel_min, mel_max, config.n_mels + 2)
    step_mel = float(mel_points[1] - mel_points[0])
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((config.n_fft + 1) * hz_points / config.sample_rate).astype(int)

    filterbank = create_mel_filterbank(config)

    collapsed_count = 0
    for m in range(config.n_mels):
        left, center, right = bin_points[m], bin_points[m + 1], bin_points[m + 2]
        if left == center or center == right:
            collapsed_count += 1

    return filterbank, bin_points, collapsed_count, mel_max, step_mel


def log_compress(energy: np.ndarray | float, floor: float = 1e-6) -> np.ndarray | float:
    """Apply natural logarithm with lower-bound clamping at floor."""
    if isinstance(energy, (int, float, np.floating)):
        return float(np.log(max(float(energy), floor)))
    return np.log(np.maximum(energy, floor))


def analyze_speech_file(
    path: Path, config: AudioConfig, fb: np.ndarray
) -> tuple[int, list[dict[str, float | int]]]:
    """Extract frames, locate peak energy frame, and return its three loudest Mel bands."""
    audio, _ = load_wav(path)
    w = np.hamming(config.win_length).astype(np.float32)
    n_frames = (len(audio) - config.win_length) // config.hop_length + 1

    mel_max = float(hz_to_mel(config.f_max))
    mel_points = np.linspace(0.0, mel_max, config.n_mels + 2)
    hz_centers = mel_to_hz(mel_points[1:-1])

    powers = []
    log_mels = []
    for i in range(n_frames):
        start = i * config.hop_length
        frame = audio[start : start + config.win_length] * w
        _, P = stft_power(frame, n_fft=config.n_fft)
        powers.append(P)
        E = np.dot(fb, P)
        log_mels.append(log_compress(E))

    frame_energies = [float(np.sum(p)) for p in powers]
    peak_frame_idx = int(np.argmax(frame_energies))
    peak_log_mel = log_mels[peak_frame_idx]

    top3_indices = np.argsort(peak_log_mel)[::-1][:3]
    top3_bands = []
    for rank, b in enumerate(top3_indices, 1):
        top3_bands.append(
            {
                "rank": rank,
                "band_index": int(b),
                "log_mel": float(peak_log_mel[b]),
                "center_hz": float(hz_centers[b]),
            }
        )

    return peak_frame_idx, top3_bands


def render_report(
    tone_path: Path, speech_a_path: Path, speech_b_path: Path
) -> dict[str, str | int | float | list]:
    """Run end-to-end lab measurements and print formatted report."""
    ensure_tone_file(tone_path)

    tone_sha = sha256_file(tone_path)
    tone_audio, _ = load_wav(tone_path)

    config = AudioConfig()
    win_length = config.win_length  # 400
    n_fft = config.n_fft  # 512

    # 1. Window
    frame0_windowed, w = window_frame(tone_audio, start_idx=0, win_length=win_length)
    w_0 = float(w[0])
    w_200 = float(w[200])
    w_399 = float(w[399])

    # 2. Probe sums at bin 14
    cos_sum_0, sin_sum_0 = probe_sums(frame0_windowed, k=14, n_fft=n_fft)

    # Quarter-cycle shift (shift by 9 samples ~ 1/4 cycle of 440 Hz at 16 kHz)
    frame_quarter, _ = window_frame(tone_audio, start_idx=9, win_length=win_length)
    cos_sum_quarter, sin_sum_quarter = probe_sums(frame_quarter, k=14, n_fft=n_fft)

    # 3. STFT & Power
    X, P = stft_power(frame0_windowed, n_fft=n_fft)
    argmax_bin = int(np.argmax(P))
    argmax_hz = float(argmax_bin * config.sample_rate / n_fft)
    re_14 = float(X[14].real)
    im_14 = float(X[14].imag)
    power_14 = float(P[14])

    direct_dft_products = n_fft * n_fft  # 262144
    radix2_butterflies = (n_fft // 2) * int(np.log2(n_fft))  # 2304

    # 4. Mel filterbank
    fb, bin_points, collapsed_count, mel_8000, step_mel = mel_edges(config)
    filter0_edges = [int(bin_points[0]), int(bin_points[1]), int(bin_points[2])]
    filter79_edges = [int(bin_points[79]), int(bin_points[80]), int(bin_points[81])]

    # Owning filter for bin 14
    g_14 = float(fb[15, 14])

    # 5. Log compression probes
    log_moderate = float(log_compress(power_14))
    log_unit = float(log_compress(1.0))
    log_clamped = float(log_compress(1e-8))

    # 6. Speech files analysis
    speech_a_peak_idx, speech_a_top3 = analyze_speech_file(speech_a_path, config, fb)
    speech_b_peak_idx, speech_b_top3 = analyze_speech_file(speech_b_path, config, fb)

    report_data = {
        "tone_file_sha256": tone_sha,
        "w_0": round(w_0, 6),
        "w_200": round(w_200, 6),
        "w_399": round(w_399, 6),
        "cosine_probe_sum_0": round(cos_sum_0, 4),
        "sine_probe_sum_0": round(sin_sum_0, 4),
        "cosine_probe_sum_quarter": round(cos_sum_quarter, 4),
        "sine_probe_sum_quarter": round(sin_sum_quarter, 4),
        "argmax_bin": argmax_bin,
        "argmax_hz": argmax_hz,
        "re_bin14": round(re_14, 4),
        "im_bin14": round(im_14, 4),
        "power_bin14": round(power_14, 2),
        "direct_dft_products": direct_dft_products,
        "radix2_butterflies": radix2_butterflies,
        "mel_8000": round(mel_8000, 2),
        "step_mel": round(step_mel, 3),
        "filter0_edges": filter0_edges,
        "filter79_edges": filter79_edges,
        "collapsed_count": collapsed_count,
        "bin14_filter": 15,
        "bin14_weight": g_14,
        "log_moderate": round(log_moderate, 4),
        "log_unit": round(log_unit, 4),
        "log_clamped": round(log_clamped, 4),
        "speech_a_file": str(speech_a_path.as_posix()),
        "speech_a_peak_frame": speech_a_peak_idx,
        "speech_a_top3_bands": speech_a_top3,
        "speech_b_file": str(speech_b_path.as_posix()),
        "speech_b_peak_frame": speech_b_peak_idx,
        "speech_b_top3_bands": speech_b_top3,
    }

    # Print fixed report as required
    print("=" * 80)
    print("LAB 1.3 TEACHING LAB REPORT: MEASURED ACOUSTIC VALUES")
    print("=" * 80)
    print(f"tone file sha256: {report_data['tone_file_sha256']}")
    print(
        f"w[0]: {report_data['w_0']:.6f}, w[200]: {report_data['w_200']:.6f}, "
        f"w[399]: {report_data['w_399']:.6f}"
    )
    print(
        f"cosine-probe sum (zero shift): {report_data['cosine_probe_sum_0']:.4f}, "
        f"sine-probe sum: {report_data['sine_probe_sum_0']:.4f}"
    )
    print(
        f"cosine-probe sum (quarter-cycle shift): {report_data['cosine_probe_sum_quarter']:.4f}, "
        f"sine-probe sum: {report_data['sine_probe_sum_quarter']:.4f}"
    )
    print(f"argmax bin: {report_data['argmax_bin']} ({report_data['argmax_hz']:.1f} Hz)")
    print(
        f"bin 14: Re = {report_data['re_bin14']:.4f}, "
        f"Im = {report_data['im_bin14']:.4f}, "
        f"Power = {report_data['power_bin14']:.2f}"
    )
    print(
        f"direct-DFT product count: {report_data['direct_dft_products']}, "
        f"radix-2 butterfly count: {report_data['radix2_butterflies']}"
    )
    print(
        f"mel(8000): {report_data['mel_8000']:.2f}, step_mel: {report_data['step_mel']:.3f}, "
        f"filter-0 edges: {report_data['filter0_edges']}, "
        f"filter-79 edges: {report_data['filter79_edges']}"
    )
    print(f"collapsed count: {report_data['collapsed_count']}")
    print(f"g for bin 14 (Filter {report_data['bin14_filter']}): {report_data['bin14_weight']:.4f}")
    print(
        f"log energies: ln(P[14]) = {report_data['log_moderate']:.4f}, "
        f"ln(1.0) = {report_data['log_unit']:.4f}, "
        f"ln(1e-8 clamped) = {report_data['log_clamped']:.4f}"
    )
    speech_a_str = ", ".join(
        f"Band {b['band_index']} ({b['center_hz']:.1f} Hz: {b['log_mel']:.2f})"
        for b in speech_a_top3
    )
    print(
        f"speech a ({speech_a_path.name}): peak frame {report_data['speech_a_peak_frame']}, "
        f"top 3 bands: {speech_a_str}"
    )
    speech_b_str = ", ".join(
        f"Band {b['band_index']} ({b['center_hz']:.1f} Hz: {b['log_mel']:.2f})"
        for b in speech_b_top3
    )
    print(
        f"speech b ({speech_b_path.name}): peak frame {report_data['speech_b_peak_frame']}, "
        f"top 3 bands: {speech_b_str}"
    )
    print("=" * 80)

    return report_data


def run_experiment() -> dict[str, str | int | float | list]:
    """Entry point for capture_result.py."""
    tone_path = ROOT / "datasets" / "sample_tone440.wav"
    speech_a_path = ROOT / "datasets" / "sample_speech_a.wav"
    speech_b_path = ROOT / "datasets" / "sample_speech_b.wav"
    return render_report(tone_path, speech_a_path, speech_b_path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tone-path",
        type=Path,
        default=ROOT / "datasets" / "sample_tone440.wav",
        help="Path to 440 Hz tone WAV",
    )
    ap.add_argument(
        "--speech-a-path",
        type=Path,
        default=ROOT / "datasets" / "sample_speech_a.wav",
        help="Path to speech sample A WAV",
    )
    ap.add_argument(
        "--speech-b-path",
        type=Path,
        default=ROOT / "datasets" / "sample_speech_b.wav",
        help="Path to speech sample B WAV",
    )
    args = ap.parse_args()

    # If any file is missing, exit non-zero
    for p in [args.speech_a_path, args.speech_b_path]:
        if not p.is_file():
            print(f"Error: Required audio file does not exist: {p}", file=sys.stderr)
            return 1

    try:
        render_report(args.tone_path, args.speech_a_path, args.speech_b_path)
    except Exception as exc:
        print(f"Error executing lab_1_3: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
