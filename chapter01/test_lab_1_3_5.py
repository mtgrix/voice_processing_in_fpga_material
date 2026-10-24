"""Tests for chapter01/lab_1_3_5.py.

These pin the claims the section makes about its own code: that the integer path is
bit-exact and reproducible, that the parabolic interpolation refines pitch to sub-cent precision,
and that the octave-cost sweep matches the simulation results.
"""

from __future__ import annotations

import numpy as np
import pytest

from chapter01.lab_1_3_5 import (
    FRAME_LEN,
    FS_HZ,
    N_SCAN_LAGS,
    Q15,
    compare_on_signal,
    compensation_rom_q13,
    export_hex,
    fixed_pitch_frame,
    hanning_rom_q15,
    load_pitch_f0_bin,
    median3,
    median3_removes_octave_spike,
    octave_cost_sweep,
    save_pitch_f0_bin,
    scoring_rom_q13,
    window_frame_q15,
    word_to_frame_indices,
)


def test_window_rom_is_full_length_and_bounded() -> None:
    """The 640-point Hanning window satisfies Praat formula and saturates at 32767."""
    rom = hanning_rom_q15()
    assert rom.size == FRAME_LEN
    assert rom[0] > 0  # i=1 gives small positive value
    assert int(rom.max()) == Q15 - 1  # 32767 saturation to prevent int16 overflow


def test_window_multiply_keeps_q15_scale() -> None:
    """Multiplying by the window and rounding with + (1<<14) >> 15 leaves the signal in Q1.15."""
    x = np.full(FRAME_LEN, Q15 // 2, dtype=np.int64)
    y = window_frame_q15(x)
    # Near center the window is ~1.0, so the sample is preserved
    assert abs(int(y[FRAME_LEN // 2]) - Q15 // 2) <= 1
    # At edge, window is small
    assert int(y[0]) < 10


def test_compensation_table_is_monotone_and_fits_q3_13() -> None:
    """C[tau] rises with lag and never exceeds what Q3.13 can hold."""
    comp = compensation_rom_q13()
    assert comp.size == N_SCAN_LAGS
    assert np.all(np.diff(comp) > 0), "window taper must grow with lag"
    assert int(comp.max()) < (1 << 15), "Q3.13 cannot represent 4.0 or more"


def test_scoring_rom_is_compensation_times_a_penalty_at_most_one() -> None:
    """Folding octave_cost in can only lower a score, never raise it, for all tau >= TAU_MIN."""
    comp = compensation_rom_q13()
    score = scoring_rom_q13()
    # At index 0 (tau=26, 615 Hz > 600 Hz ceiling), bias is slightly > 1 (+2 LSB).
    # For all valid search candidates tau in [27, 213] (index 1..187), penalty <= 1.
    assert np.all(score[1:] <= comp[1:] + 1), "bias factor must be <= 1 for all valid candidates"


def test_integer_detector_matches_float_on_worked_example() -> None:
    """At 200 Hz (T0 = 80 samples) both detectors must name the same lag."""
    cmp = compare_on_signal(freq_hz=200.0)
    assert cmp.tau_star_fixed == 80
    assert cmp.tau_star_float == 80
    assert cmp.f0_fixed_hz == pytest.approx(200.0, abs=0.5)
    assert cmp.agree_hz


def test_parabolic_interpolation_sub_cent_accuracy() -> None:
    """On 440 Hz tone, lag 36 gives 444.4 Hz (+17 cent); parabolic gives < 1 cent."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x = 0.5 * np.sin(2.0 * np.pi * 440.0 * t)
    x_q15 = np.clip(np.round(x * Q15), -Q15, Q15 - 1).astype(np.int64)
    ref = int(np.dot(x_q15, x_q15))

    coarse = fixed_pitch_frame(x_q15, ref, use_interpolation=False)
    assert coarse.tau_star == 36
    assert coarse.f0_hz == pytest.approx(444.44, abs=0.5)
    coarse_cent = abs(1200 * np.log2(coarse.f0_hz / 440.0))
    assert coarse_cent > 15.0  # ~17.4 cent error

    fine = fixed_pitch_frame(x_q15, ref, use_interpolation=True)
    assert fine.tau_star == 36
    fine_cent = abs(1200 * np.log2(fine.f0_hz / 440.0))
    assert fine_cent < 1.0  # < 1 cent error (+0.35 cent)


def test_boundary_interpolation_590hz_and_75hz() -> None:
    """Boundary frequencies 590 Hz (tau=27) and 75 Hz (tau=213) have valid neighbors."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ

    # 590 Hz: lag 27 with left neighbor 26
    x_590 = 0.5 * np.sin(2.0 * np.pi * 590.0 * t)
    x_590_q15 = np.clip(np.round(x_590 * Q15), -Q15, Q15 - 1).astype(np.int64)
    ref_590 = int(np.dot(x_590_q15, x_590_q15))
    res_590 = fixed_pitch_frame(x_590_q15, ref_590, use_interpolation=True)
    assert res_590.tau_star == 27
    err_590 = abs(1200 * np.log2(res_590.f0_hz / 590.0))
    assert err_590 < 1.0  # < 1 cent error (~0.39 cent)

    # 75 Hz: lag 213 with right neighbor 214
    x_75 = 0.5 * np.sin(2.0 * np.pi * 75.0 * t)
    x_75_q15 = np.clip(np.round(x_75 * Q15), -Q15, Q15 - 1).astype(np.int64)
    ref_75 = int(np.dot(x_75_q15, x_75_q15))
    res_75 = fixed_pitch_frame(x_75_q15, ref_75, use_interpolation=True)
    assert res_75.tau_star == 213
    err_75 = abs(1200 * np.log2(res_75.f0_hz / 75.0))
    assert err_75 < 2.0  # < 2 cent error (~1.37 cent)


def test_integer_detector_is_deterministic_across_repeated_runs() -> None:
    """Same input, same bits, every time."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x_q15 = np.clip(np.round(0.5 * np.sin(2.0 * np.pi * 220.0 * t) * Q15), -Q15, Q15 - 1).astype(
        np.int64
    )
    ref = int(np.dot(x_q15, x_q15))
    first = fixed_pitch_frame(x_q15, ref)
    for _ in range(5):
        assert fixed_pitch_frame(x_q15, ref) == first


def test_silence_is_unvoiced() -> None:
    """A frame with no energy is reported unvoiced."""
    x_q15 = np.zeros(FRAME_LEN, dtype=np.int64)
    result = fixed_pitch_frame(x_q15, ref_energy=0)
    assert not result.voiced
    assert result.f0_hz == 0.0


def test_silence_gate_rejects_quiet_frame() -> None:
    """Energy under 0.09% of peak reference is unvoiced."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    quiet = np.clip(np.round(0.001 * np.sin(2.0 * np.pi * 200.0 * t) * Q15), -Q15, Q15 - 1).astype(
        np.int64
    )
    loud_ref = int(Q15 * Q15)
    assert not fixed_pitch_frame(quiet, ref_energy=loud_ref).voiced


def test_median3_removes_a_single_frame_octave_spike() -> None:
    """[122, 245, 124] Hz -> the 245 spike is suppressed."""
    result = median3_removes_octave_spike()
    assert result["raw"] == [122, 245, 124]
    assert result["filtered"] == [122, 124, 124]
    assert 245 not in result["filtered"]


def test_median3_preserves_monotone_run() -> None:
    assert median3([100, 110, 120]) == [100, 110, 120]


def test_octave_cost_sweep_matches_simulation() -> None:
    """Zero cost fails 300 times on sine grid; 0.01 cost eliminates octave jump failures."""
    sweep = octave_cost_sweep()
    assert sweep[0.0] == 300
    assert sweep[0.005] == 21
    assert sweep[0.009] == 0
    assert sweep[0.01] == 0
    assert sweep[0.02] == 0


def test_export_hex_creates_valid_files(tmp_path) -> None:
    """export_hex produces valid 4-digit hex files with exact line counts."""
    export_hex(tmp_path)
    hanning_file = tmp_path / "hanning_rom.hex"
    c_tau_file = tmp_path / "c_tau_rom.hex"
    f0_lut_file = tmp_path / "f0_lut.hex"
    golden_file = tmp_path / "golden_vectors.hex"

    assert hanning_file.exists()
    assert c_tau_file.exists()
    assert f0_lut_file.exists()
    assert golden_file.exists()

    h_lines = [line for line in hanning_file.read_text().strip().split("\n") if line.strip()]
    c_lines = [line for line in c_tau_file.read_text().strip().split("\n") if line.strip()]
    f_lines = [line for line in f0_lut_file.read_text().strip().split("\n") if line.strip()]
    g_lines = [
        line
        for line in golden_file.read_text().strip().split("\n")
        if line.strip() and not line.strip().startswith("//")
    ]

    assert len(h_lines) == 640
    assert len(c_lines) == 189
    assert len(f_lines) == 189
    assert len(g_lines) == 643  # 640 samples + 3 output words

    # Center of Hanning should be 7fff (32767)
    assert h_lines[319] == "7fff" or h_lines[320] == "7fff"


def test_pitch_f0_q12_4_protocol(tmp_path) -> None:
    """Test Q12.4 uint16 binary serialization and word-to-frame index mapping."""
    f0_in = [0.0, 440.125, 200.0, 0.0]
    voiced_in = [False, True, True, False]

    bin_path = tmp_path / "pitch_f0.bin"
    save_pitch_f0_bin(f0_in, voiced_in, bin_path)
    assert bin_path.stat().st_size == 4 * 2  # 4 frames * 2 bytes = 8 bytes

    f0_out = load_pitch_f0_bin(bin_path)
    assert f0_out[0] == 0.0
    assert abs(f0_out[1] - 440.125) < 0.001
    assert abs(f0_out[2] - 200.0) < 0.001
    assert f0_out[3] == 0.0

    # Timing contract: frame center tk = 20 + 10k ms
    # Word from 0.050s to 0.120s (50 ms to 120 ms)
    # k_start = ceil((50 - 20)/10) = 3
    # k_end = floor((120 - 20)/10) = 10
    k_start, k_end = word_to_frame_indices(0.050, 0.120)
    assert k_start == 3
    assert k_end == 10
