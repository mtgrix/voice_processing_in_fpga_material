"""Unit tests for Chapter 02 Jetson Orin profiler."""

from __future__ import annotations

import numpy as np

from chapter02.exp_02_jetson_orin_profiler import (
    JetsonOrinProfiler,
    run_experiment,
)


def test_profiler_rtf_and_energy_math() -> None:
    """Verify exact formula calculation for RTF and energy per frame."""
    profiler = JetsonOrinProfiler(audio_frame_duration_ms=10.0)
    # 10 frames with constant 2.0 ms latency and 10.0 W power
    latencies = np.full(10, 2.0)
    gpu_power = np.full(10, 4.0)
    board_power = np.full(10, 10.0)

    metrics = profiler.analyze_benchmark(latencies, gpu_power, board_power)

    # RTF = 2.0 ms / 10.0 ms = 0.2
    assert abs(metrics.real_time_factor - 0.2) < 1e-6
    # Energy = 10.0 W * 0.002 s * 1000 = 20.0 mJ
    assert abs(metrics.energy_per_frame_mj - 20.0) < 1e-6
    # FPS = 1000 / 2 = 500 fps; FPS/Watt = 500 / 10 = 50.0
    assert abs(metrics.frames_per_sec_per_watt - 50.0) < 1e-6
    # Jitter of constant latency must be 0
    assert abs(metrics.jitter_std_ms - 0.0) < 1e-6


def test_simulated_benchmark_thresholds() -> None:
    """Verify statistical properties of simulated Jetson Orin traces."""
    metrics = run_experiment()
    assert metrics.total_frames == 1000
    assert metrics.real_time_factor < 0.5  # Must easily achieve real-time
    assert metrics.p99_latency_ms > metrics.p50_latency_ms  # Monotonic percentiles
    assert metrics.avg_board_power_w > 5.0
    assert metrics.energy_per_frame_mj > 0.0
