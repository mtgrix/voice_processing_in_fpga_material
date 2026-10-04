"""Tests for chapter01/lab_1_3.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from chapter01.exp_01_streaming_audio_pipeline import AudioConfig
from chapter01.lab_1_3 import (
    ROOT,
    log_compress,
    mel_edges,
    render_report,
    stft_power,
)


def test_missing_wav_makes_lab_exit_nonzero(tmp_path: Path) -> None:
    """Missing required audio files causes lab_1_3.py to exit with non-zero status."""
    nonexistent = tmp_path / "does_not_exist.wav"
    cmd = [
        sys.executable,
        str(ROOT / "chapter01" / "lab_1_3.py"),
        "--speech-a-path",
        str(nonexistent),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "does not exist" in result.stderr or result.returncode == 1


def test_tone_peak_bin_is_14() -> None:
    """A 440 Hz tone sampled at 16 kHz with N=512 yields a peak spectral bin at k=14."""
    fs = 16000
    n = np.arange(400)
    tone = np.cos(2.0 * np.pi * 440.0 * n / fs).astype(np.float32)
    w = np.hamming(400).astype(np.float32)
    _, P = stft_power(tone * w, n_fft=512)
    peak_bin = int(np.argmax(P))
    assert peak_bin == 14
    # Frequency corresponding to bin 14 is 14 * 31.25 = 437.5 Hz
    freq = peak_bin * (fs / 512)
    assert freq == pytest.approx(437.5, abs=0.1)


def test_filter0_edges_and_collapsed_count() -> None:
    """Filter 0 has bin edges [0, 0, 1] and exactly 3 filters collapse in the 80-mel bank."""
    config = AudioConfig()
    _, bin_points, collapsed_count, mel_8000, step_mel = mel_edges(config)
    filter0 = [int(bin_points[0]), int(bin_points[1]), int(bin_points[2])]
    assert filter0 == [0, 0, 1]
    assert collapsed_count == 3
    assert mel_8000 == pytest.approx(2840.02, abs=0.05)
    assert step_mel == pytest.approx(35.062, abs=0.01)


def test_energy_below_floor_clamps_in_log_compress() -> None:
    """Energies below 1e-6 are clamped to exactly ln(1e-6) in log_compress."""
    expected_clamped = float(np.log(1e-6))
    assert log_compress(1e-8) == pytest.approx(expected_clamped, rel=1e-5)
    assert log_compress(0.0) == pytest.approx(expected_clamped, rel=1e-5)
    assert log_compress(1e-6) == pytest.approx(expected_clamped, rel=1e-5)
    # Above threshold, values should equal natural logarithm
    assert log_compress(1.0) == pytest.approx(0.0, abs=1e-6)
    assert log_compress(np.e) == pytest.approx(1.0, abs=1e-6)


def test_report_butterfly_and_direct_counts() -> None:
    """The lab report verifies direct DFT products = 262144 and radix-2 butterflies = 2304."""
    tone_path = ROOT / "datasets" / "sample_tone440.wav"
    speech_a = ROOT / "datasets" / "sample_speech_a.wav"
    speech_b = ROOT / "datasets" / "sample_speech_b.wav"
    report = render_report(tone_path, speech_a, speech_b)
    assert report["direct_dft_products"] == 262144
    assert report["radix2_butterflies"] == 2304
    assert report["argmax_bin"] == 14
