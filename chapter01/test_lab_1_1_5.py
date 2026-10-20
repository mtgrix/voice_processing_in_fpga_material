"""Tests for the mute duration and the cookbook high-pass of section 1.1.5."""

from __future__ import annotations

import numpy as np
import pytest

from chapter01.lab_1_1_5 import (
    CLOCKS_PER_FRAME,
    FC_HZ,
    FS_HZ,
    MUTE_CLOCKS,
    Q_BUTTERWORTH,
    analyze_highpass,
    apply_biquad,
    cookbook_highpass,
    linear_gain,
    mute_at,
    scale_internal_hpf,
    step_settle_samples,
)


def test_mute_at_16_khz_is_256_ms_and_4096_samples() -> None:
    """2^18 bit clocks of a 64-clock frame at 16 kHz is exactly 256 ms."""
    mute = mute_at(16_000)
    assert mute.mute_clocks == 262_144
    assert mute.sck_hz == pytest.approx(1_024_000.0)
    assert mute.mute_s == pytest.approx(0.256)
    assert mute.mute_samples == 4096
    assert mute.hops == pytest.approx(25.6)
    # The datasheet's parenthetical 85 ms is this quotient rounded.
    assert mute.datasheet_example_ms == pytest.approx(85.333, abs=0.001)


def test_internal_highpass_scales_by_the_sample_rate() -> None:
    """Table 7 is stated at 48 kHz and scales with the sampling rate."""
    low, mid, high = scale_internal_hpf(16_000)
    assert low == pytest.approx(3.7 * 16_000 / 48_000)
    assert mid == pytest.approx(10.4 * 16_000 / 48_000)
    assert high == pytest.approx(21.6 * 16_000 / 48_000)
    assert low == pytest.approx(1.2333, abs=0.001)
    assert high == pytest.approx(7.2)


def test_dc_gain_is_zero_and_cutoff_is_near_minus_3_db() -> None:
    """The cookbook high-pass has a zero at z = 1, and Butterworth sits near -3 dB at fc."""
    b, a = cookbook_highpass(float(FS_HZ), FC_HZ, Q_BUTTERWORTH)
    assert linear_gain(b, a, 0.0, float(FS_HZ)) == pytest.approx(0.0, abs=1e-12)
    assert 20.0 * np.log10(linear_gain(b, a, FC_HZ, float(FS_HZ))) == pytest.approx(-3.01, abs=0.05)
    assert 20.0 * np.log10(linear_gain(b, a, 300.0, float(FS_HZ))) == pytest.approx(0.0, abs=0.05)
    # 85 Hz, the lowest pitch section 1.2 teaches, stays in the passband.
    assert 20.0 * np.log10(linear_gain(b, a, 85.0, float(FS_HZ))) > -2.0


def test_rest_state_and_settling() -> None:
    """With both delays at rest the first output is b0, and the step then falls under 1 percent."""
    b, a = cookbook_highpass(float(FS_HZ), FC_HZ, Q_BUTTERWORTH)
    step = np.ones(2_000, dtype=np.float64)
    filtered = apply_biquad(b, a, step)
    assert float(filtered[0]) == pytest.approx(float(b[0]))
    settle = step_settle_samples(b, a)
    assert settle == 219
    assert abs(float(filtered[settle])) < 0.01
    assert float(np.max(np.abs(filtered[settle : settle + 160]))) < 0.01


def test_clock_rule_is_the_datasheet_rule() -> None:
    """Guard the two integers the duration is built from."""
    assert MUTE_CLOCKS == 1 << 18
    assert CLOCKS_PER_FRAME == 64


def test_analyze_reports_a_dead_offset_and_a_surviving_tone() -> None:
    """On the constructed signal the mean collapses and the 200 Hz tone does not."""
    highpass = analyze_highpass()
    assert highpass.gain_at_dc < 1e-9
    assert abs(highpass.constructed_mean_tail) < 0.01
    assert highpass.constructed_tone_rms_tail == pytest.approx(
        highpass.constructed_tone_rms_in, rel=0.05
    )
    assert highpass.db_at_20_hz < highpass.db_at_60_hz < highpass.db_at_300_hz
