"""Experiment 1.1: Streaming Audio Preprocessing Pipeline.

This experiment implements and verifies an online, frame-by-frame acoustic feature
extraction pipeline (Sliding Ring Buffer -> STFT -> Mel Filterbank -> Log-Mel Features),
comparing streaming execution against full-batch offline execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast, overload

import numpy as np


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    n_fft: int = 512
    win_length: int = 400  # 25 ms at 16 kHz
    hop_length: int = 160  # 10 ms at 16 kHz
    n_mels: int = 80
    f_min: float = 0.0
    f_max: float = 8000.0


@overload
def hz_to_mel(hz: float) -> float: ...


@overload
def hz_to_mel(hz: np.ndarray) -> np.ndarray: ...


def hz_to_mel(hz: float | np.ndarray) -> float | np.ndarray:
    """Convert Hz frequency to Mel scale. Accepts a scalar or an array of frequencies."""
    return 2595.0 * np.log10(1.0 + hz / 700.0)


@overload
def mel_to_hz(mel: float) -> float: ...


@overload
def mel_to_hz(mel: np.ndarray) -> np.ndarray: ...


def mel_to_hz(mel: float | np.ndarray) -> float | np.ndarray:
    """Convert Mel scale frequency to Hz. Accepts a scalar or an array of mel values."""
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


def create_mel_filterbank(config: AudioConfig) -> np.ndarray:
    """Create a triangular Mel filterbank matrix of shape (n_mels, n_fft // 2 + 1)."""
    n_bins = config.n_fft // 2 + 1
    mel_min = hz_to_mel(config.f_min)
    mel_max = hz_to_mel(config.f_max if config.f_max is not None else config.sample_rate / 2.0)
    mel_points = np.linspace(mel_min, mel_max, config.n_mels + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((config.n_fft + 1) * hz_points / config.sample_rate).astype(int)

    filterbank = np.zeros((config.n_mels, n_bins), dtype=np.float32)
    for m in range(config.n_mels):
        left = bin_points[m]
        center = bin_points[m + 1]
        right = bin_points[m + 2]

        for k in range(left, center):
            if center > left:
                filterbank[m, k] = (k - left) / (center - left)
        for k in range(center, right):
            if right > center:
                filterbank[m, k] = (right - k) / (right - center)

    return filterbank


class StreamingAudioPreprocessor:
    """Online streaming preprocessor maintaining a sliding buffer for continuous audio frames."""

    def __init__(self, config: AudioConfig) -> None:
        self.config = config
        self.buffer = np.zeros(config.win_length, dtype=np.float32)
        self.window = np.hamming(config.win_length).astype(np.float32)
        self.mel_fb = create_mel_filterbank(config)

    def compute_current_features(self) -> np.ndarray:
        """Compute log-mel features on the current buffer contents."""
        windowed = self.buffer * self.window
        fft_complex = np.fft.rfft(windowed, n=self.config.n_fft)
        power_spectrum = np.abs(fft_complex) ** 2
        mel_energy = np.dot(self.mel_fb, power_spectrum)
        # np.dot returns Any under the installed NumPy stubs.
        return cast("np.ndarray", np.log(np.maximum(mel_energy, 1e-6)))

    def feed_and_compute(self, hop_samples: np.ndarray) -> np.ndarray:
        """Slide buffer by hop_length, insert new hop samples, and compute log-mel features."""
        assert len(hop_samples) == self.config.hop_length, (
            f"Expected {self.config.hop_length} samples, got {len(hop_samples)}"
        )
        shift = self.config.hop_length
        self.buffer[:-shift] = self.buffer[shift:]
        self.buffer[-shift:] = hop_samples
        return self.compute_current_features()


def compute_batch_stft_mel(waveform: np.ndarray, config: AudioConfig) -> np.ndarray:
    """Compute offline batch log-mel spectrogram for reference comparison."""
    window = np.hamming(config.win_length).astype(np.float32)
    mel_fb = create_mel_filterbank(config)

    num_frames = (len(waveform) - config.win_length) // config.hop_length + 1
    spectrogram = []

    for i in range(num_frames):
        start = i * config.hop_length
        end = start + config.win_length
        chunk = waveform[start:end] * window
        fft_complex = np.fft.rfft(chunk, n=config.n_fft)
        power = np.abs(fft_complex) ** 2
        mel = np.dot(mel_fb, power)
        log_mel = np.log(np.maximum(mel, 1e-6))
        spectrogram.append(log_mel)

    return np.array(spectrogram, dtype=np.float32)


def run_experiment() -> dict[str, float]:
    """Execute the experiment verifying streaming vs. batched numerical agreement."""
    config = AudioConfig()
    duration_sec = 1.0
    num_samples = int(duration_sec * config.sample_rate)

    # Generate synthetic speech chirp + multi-tone signal
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    synthetic_speech = (
        0.5 * np.sin(2 * np.pi * 440 * t)
        + 0.3 * np.sin(2 * np.pi * 1200 * t)
        + 0.2 * np.sin(2 * np.pi * 3200 * t)
    ).astype(np.float32)

    # 1. Offline reference calculation
    offline_features = compute_batch_stft_mel(synthetic_speech, config)

    # 2. Streaming execution frame by frame
    streamer = StreamingAudioPreprocessor(config)
    # Pre-fill initial buffer with the first window (frame 0)
    streamer.buffer[:] = synthetic_speech[: config.win_length]

    streaming_features = [streamer.compute_current_features()]
    for i in range(
        config.win_length,
        len(synthetic_speech) - config.hop_length + 1,
        config.hop_length,
    ):
        hop = synthetic_speech[i : i + config.hop_length]
        log_mel = streamer.feed_and_compute(hop)
        streaming_features.append(log_mel)

    streaming_array = np.array(streaming_features[: len(offline_features)], dtype=np.float32)
    reference_array = offline_features[: len(streaming_array)]

    # Metrics: Mean Absolute Error and Signal-to-Quantization-Noise Ratio (SQNR)
    mae = float(np.mean(np.abs(streaming_array - reference_array)))
    signal_power = np.mean(reference_array**2)
    noise_power = np.mean((streaming_array - reference_array) ** 2)
    sqnr_db = float(10 * np.log10(signal_power / (noise_power + 1e-12)))

    print("=" * 60)
    print("Experiment 1.1: Streaming Audio Pipeline Results")
    print(f"Total Frames Processed : {len(streaming_array)}")
    print(f"Mean Absolute Error     : {mae:.6e}")
    print(f"Signal-to-Noise (SQNR)  : {sqnr_db:.2f} dB")
    print("=" * 60)

    return {"mae": mae, "sqnr_db": sqnr_db, "num_frames": float(len(streaming_array))}


if __name__ == "__main__":
    run_experiment()
