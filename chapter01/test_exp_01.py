"""Unit tests for Chapter 01 streaming audio preprocessor."""

from __future__ import annotations

import numpy as np
import pytest

from chapter01.exp_01_streaming_audio_pipeline import (
    AudioConfig,
    create_mel_filterbank,
    hz_to_mel,
    mel_to_hz,
    run_experiment,
)


def test_mel_conversion_inversion() -> None:
    """Test that Hz to Mel and Mel to Hz are exact mathematical inverses."""
    freqs = [100.0, 440.0, 1000.0, 4000.0, 8000.0]
    for f in freqs:
        mel = hz_to_mel(f)
        recovered = mel_to_hz(mel)
        assert pytest.approx(f, rel=1e-4) == recovered


def test_mel_filterbank_shape_and_range() -> None:
    """Verify filterbank dimensions and non-negative triangular weights."""
    config = AudioConfig(n_fft=512, n_mels=80)
    fb = create_mel_filterbank(config)
    assert fb.shape == (80, 257)
    assert np.all(fb >= 0.0)
    assert np.all(fb <= 1.0)


def test_streaming_vs_batch_fidelity() -> None:
    """Ensure streaming sliding buffer produces identical features to batch STFT."""
    results = run_experiment()
    assert results["mae"] < 1e-4, f"MAE too high: {results['mae']}"
    assert results["sqnr_db"] > 50.0, f"SQNR too low: {results['sqnr_db']} dB"
    assert results["num_frames"] > 50
