"""Tests for chapter01/lab_1_3.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from chapter01.exp_01_streaming_audio_pipeline import AudioConfig, create_mel_filterbank
from chapter01.lab_1_3 import (
    ROOT,
    classify_filterbank_rows,
    detect_window_sidelobes,
    log_compress,
    mel_edges,
    probe_sums,
    render_report,
    stft_power,
    window_frame,
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


def test_window_sidelobe_detector() -> None:
    """Window detector measures rectangular and Hamming nulls and first sidelobes."""
    w_rect = np.ones(400, dtype=np.float32)
    w_ham = np.hamming(400).astype(np.float32)

    r_null, r_n2n, r_side_hz, r_side_db = detect_window_sidelobes(w_rect, n_scan=65536, fs=16000)
    h_null, h_n2n, h_side_hz, h_side_db = detect_window_sidelobes(w_ham, n_scan=65536, fs=16000)

    # Rectangular asserts: null 40 Hz +- 1 Hz, sidelobe 57.6 Hz +- 1 Hz, level -13.27 dB +- 0.2 dB
    assert r_null == pytest.approx(40.0, abs=1.0)
    assert r_n2n == pytest.approx(80.0, abs=2.0)
    assert r_side_hz == pytest.approx(57.6, abs=1.0)
    assert r_side_db == pytest.approx(-13.27, abs=0.2)

    # Hamming asserts: null 80 Hz +- 1 Hz, sidelobe 88.9 Hz +- 1.5 Hz, level -44.45 dB +- 0.3 dB
    assert h_null == pytest.approx(80.0, abs=1.0)
    assert h_n2n == pytest.approx(160.0, abs=2.0)
    assert h_side_hz == pytest.approx(88.9, abs=1.5)
    assert h_side_db == pytest.approx(-44.45, abs=0.3)
    assert h_side_hz < 120.0


def test_power_spectrum_operation_counts() -> None:
    """Power spectrum over 257 bins requires 514 squares, 257 adds, total 771 real operations."""
    n_bins = 257
    squares = n_bins * 2
    adds = n_bins * 1
    total = squares + adds
    assert squares == 514
    assert adds == 257
    assert total == 771


def test_phase_shift_ratios_and_sums() -> None:
    """Quarter-cycle shift drops cosine probe sum while Pythagorean sum remains invariant."""
    tone_path = ROOT / "datasets" / "sample_tone440.wav"
    from chapter01.lab_1_3 import load_wav

    audio, _ = load_wav(tone_path)
    f0, _ = window_frame(audio, start_idx=0, win_length=400)
    f9, _ = window_frame(audio, start_idx=9, win_length=400)

    c0, s0 = probe_sums(f0, k=14, n_fft=512)
    c9, s9 = probe_sums(f9, k=14, n_fft=512)

    p0 = c0**2 + s0**2
    p9 = c9**2 + s9**2

    assert c0 == pytest.approx(105.34, abs=0.1)
    assert s0 == pytest.approx(20.89, abs=0.1)
    assert c9 == pytest.approx(-19.27, abs=0.1)
    assert s9 == pytest.approx(105.74, abs=0.1)

    mag_ratio = abs(c9) / abs(c0)
    energy_ratio = (c9**2) / (c0**2)
    power_rel_change = abs(p9 - p0) / p0

    assert 0.18 <= mag_ratio <= 0.19
    assert 0.03 <= energy_ratio <= 0.04
    assert power_rel_change < 0.005


def test_mel_filterbank_row_classification() -> None:
    """Classifies 80 filter rows into 1 dead, 18 one-tap, and 61 multi-tap."""
    config = AudioConfig()
    fb = create_mel_filterbank(config)
    dead_rows, onetap_rows, multitap_rows = classify_filterbank_rows(fb)

    assert len(dead_rows) == 1
    assert dead_rows == [2]
    assert len(onetap_rows) == 18
    assert onetap_rows == [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 22]
    assert len(multitap_rows) == 61
    assert len(dead_rows) + len(onetap_rows) + len(multitap_rows) == 80

    assert float(np.max(fb[2])) == 0.0
    assert int(np.where(fb[15] > 0)[0][0]) == 14
    assert float(fb[15, 14]) == 1.0


def test_sec_1_3_vi_forbidden_strings() -> None:
    """sec_1_3_vi.tex must not contain any forbidden, deprecated, or misleading strings."""
    tex_path = ROOT / "chapter01" / "sec_1_3_vi.tex"
    if not tex_path.is_file():
        pytest.skip("sec_1_3_vi.tex not found")
    content = tex_path.read_text(encoding="utf-8")

    forbidden = [
        "209",
        "179,7",
        "179.7",
        "3,18",
        "3.18",
        "Chương 2",
        "tổng cộng 514",
        "xác nhận chính xác",
        r"4\pi",
        "Gabor",
    ]
    for term in forbidden:
        assert term not in content, f"Forbidden term found in sec_1_3_vi.tex: {term!r}"
