"""Tests for chapter01/lab_1_3_5.py.

These pin the two claims the section makes about its own code: that the integer path is
bit-exact and reproducible, and that the octave-cost sweep really does show what the
prose says it shows. A test that only checked "it runs" would let the prose drift away
from the code, which is the failure this section exists to prevent.
"""

from __future__ import annotations

import numpy as np
import pytest

from chapter01.lab_1_3_5 import (
    FRAME_LEN,
    FS_HZ,
    Q15,
    TAU_MAX,
    TAU_MIN,
    VOICING_THRESHOLD_HUNDREDTHS,
    compare_on_signal,
    compensation_rom_q13,
    fixed_pitch_frame,
    float_pitch_frame,
    full_hanning_q15,
    hanning_rom_q15,
    median3,
    median3_removes_octave_spike,
    octave_cost_sweep,
    scoring_rom_q13,
    window_frame_q15,
)


def test_window_rom_is_half_length_and_symmetric() -> None:
    """The 640-point window folds into a 320-entry ROM with no loss."""
    rom = hanning_rom_q15()
    assert rom.size == 320
    assert rom[0] == 0  # Hanning touches zero at the edge
    assert int(rom.max()) == Q15  # and reaches 1.0 at the centre
    full = full_hanning_q15()
    assert full.size == FRAME_LEN
    np.testing.assert_array_equal(full, full[::-1])


def test_window_multiply_keeps_q15_scale() -> None:
    """Multiplying by the window and shifting >>15 leaves the signal in Q1.15."""
    x = np.full(FRAME_LEN, Q15 // 2, dtype=np.int64)
    y = window_frame_q15(x)
    # At the centre the window is 1.0, so the sample survives unchanged.
    assert int(y[FRAME_LEN // 2]) == Q15 // 2
    # At the edges the window is 0, so the sample is annihilated.
    assert int(y[0]) == 0


def test_compensation_table_is_monotone_and_fits_q3_13() -> None:
    """C[tau] rises with lag and never exceeds what Q3.13 can hold."""
    comp = compensation_rom_q13()
    assert comp.size == TAU_MAX - TAU_MIN + 1
    assert np.all(np.diff(comp) > 0), "window taper must grow with lag"
    assert int(comp.max()) < (1 << 15), "Q3.13 cannot represent 4.0 or more"


def test_scoring_rom_is_compensation_times_a_penalty_at_most_one() -> None:
    """Folding octave_cost in can only lower a score, never raise it."""
    comp = compensation_rom_q13()
    score = scoring_rom_q13()
    assert np.all(score <= comp + 1), "bias factor must be <= 1 per entry"


def test_integer_detector_matches_float_on_the_sections_worked_example() -> None:
    """At 200 Hz (T0 = 80 samples) both detectors must name the same lag.

    This is the test that catches the octave error. Before the octave cost was folded
    into the scoring ROM, the integer path picked tau = 160 (100 Hz) while the float path
    picked tau = 80 (200 Hz); the two peaks tie at 1.000 after window compensation alone.
    """
    cmp = compare_on_signal(freq_hz=200.0)
    assert cmp.tau_star_fixed == 80
    assert cmp.tau_star_float == 80
    assert cmp.f0_fixed_hz == pytest.approx(200.0)
    assert cmp.agree_hz


def test_integer_detector_is_deterministic_across_repeated_runs() -> None:
    """Same input, same bits, every time: the property the FPGA relies on."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x_q15 = np.round(0.5 * np.sin(2.0 * np.pi * 220.0 * t) * Q15).astype(np.int64)
    ref = int(np.dot(x_q15, x_q15))
    first = fixed_pitch_frame(x_q15, ref)
    for _ in range(5):
        assert fixed_pitch_frame(x_q15, ref) == first


def test_silence_is_unvoiced() -> None:
    """A frame with no energy is reported unvoiced rather than given a bogus F0."""
    x_q15 = np.zeros(FRAME_LEN, dtype=np.int64)
    result = fixed_pitch_frame(x_q15, ref_energy=0)
    assert not result.voiced
    assert result.f0_hz == 0.0


def test_silence_gate_rejects_a_frame_far_below_the_reference() -> None:
    """Energy under 3% of the running reference is silence, not a quiet vowel."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    quiet = np.round(0.001 * np.sin(2.0 * np.pi * 200.0 * t) * Q15).astype(np.int64)
    loud_ref = int(Q15 * Q15)  # a full-scale reference
    assert not fixed_pitch_frame(quiet, ref_energy=loud_ref).voiced


def test_median3_removes_a_single_frame_octave_spike() -> None:
    """The section's worked example, checked as a value and not as a picture."""
    result = median3_removes_octave_spike()
    assert result["raw"] == [122, 245, 124]
    assert result["filtered"] == [122, 124, 124]
    assert 245 not in result["filtered"]


def test_median3_preserves_a_monotone_run() -> None:
    """A median must not smooth away real movement, unlike a moving average."""
    assert median3([100, 110, 120]) == [100, 110, 120]


def test_median3_keeps_a_spike_that_lasts_more_than_one_frame() -> None:
    """Two consecutive high frames survive a 3-tap median; the filter is not a cure-all."""
    assert median3([120, 240, 240, 120]) == [120, 240, 240, 120]


def test_octave_cost_sweep_matches_the_sections_claim() -> None:
    """Zero cost fails; 0.01 clears the band; that is why the parameter exists."""
    sweep = octave_cost_sweep()
    assert sweep[0.0] > 0, "without a bias, some frequency in the band picks a wrong lag"
    assert sweep[0.01] == 0, "Praat's default must clear the band"
    assert sweep[0.005] > 0, "and the default must not be slack enough to pass at half"


def test_voicing_threshold_is_an_exact_integer_percentage() -> None:
    """The comparison is integer-only, so 0.45 must land on exactly 45."""
    assert VOICING_THRESHOLD_HUNDREDTHS == 45


def test_float_reference_finds_the_planted_period() -> None:
    """Guard the reference itself: a broken reference would make drift look like zero."""
    t = np.arange(FRAME_LEN, dtype=np.float64) / FS_HZ
    x = 0.5 * np.sin(2.0 * np.pi * 250.0 * t)
    result = float_pitch_frame(x)
    assert result.voiced
    assert result.f0_hz == pytest.approx(250.0, abs=1.0)
