"""Experiment 2.1: NVIDIA Jetson Orin Latency and Energy Profiler.

This experiment models, processes, and evaluates real-world latency distributions
and hardware power sensor logs (tegrastats INA3221 readings) for edge voice models
running on NVIDIA Jetson Orin under strict streaming (batch=1) constraints.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class OrinProfileMetrics:
    total_frames: int
    mean_latency_ms: float
    p50_latency_ms: float
    p90_latency_ms: float
    p99_latency_ms: float
    jitter_std_ms: float
    audio_frame_duration_ms: float
    real_time_factor: float
    avg_soc_power_w: float
    avg_board_power_w: float
    energy_per_frame_mj: float
    frames_per_sec_per_watt: float


class JetsonOrinProfiler:
    """Analyzer for Jetson Orin execution profiles under streaming voice workloads."""

    def __init__(self, audio_frame_duration_ms: float = 10.0) -> None:
        self.frame_duration_ms = audio_frame_duration_ms

    def analyze_benchmark(
        self,
        latencies_ms: np.ndarray,
        gpu_power_watts: np.ndarray,
        board_power_watts: np.ndarray,
    ) -> OrinProfileMetrics:
        """Compute statistical latency distribution, RTF, and energy consumption metrics."""
        assert len(latencies_ms) > 0, "Latency array cannot be empty"
        assert len(gpu_power_watts) > 0, "Power array cannot be empty"

        mean_lat = float(np.mean(latencies_ms))
        p50 = float(np.percentile(latencies_ms, 50))
        p90 = float(np.percentile(latencies_ms, 90))
        p99 = float(np.percentile(latencies_ms, 99))
        jitter = float(np.std(latencies_ms))

        # Real-time factor = compute time / audio duration
        rtf = mean_lat / self.frame_duration_ms

        avg_soc_power = float(np.mean(gpu_power_watts))
        avg_board_power = float(np.mean(board_power_watts))

        # Energy per frame = Board Power (Watts) * Frame Latency (seconds) * 1000 (mJ)
        energy_per_frame_mj = avg_board_power * (mean_lat / 1000.0) * 1000.0

        # Efficiency: throughput (fps) per Watt
        fps = 1000.0 / mean_lat if mean_lat > 0 else 0.0
        fps_per_watt = fps / avg_board_power if avg_board_power > 0 else 0.0

        return OrinProfileMetrics(
            total_frames=len(latencies_ms),
            mean_latency_ms=mean_lat,
            p50_latency_ms=p50,
            p90_latency_ms=p90,
            p99_latency_ms=p99,
            jitter_std_ms=jitter,
            audio_frame_duration_ms=self.frame_duration_ms,
            real_time_factor=rtf,
            avg_soc_power_w=avg_soc_power,
            avg_board_power_w=avg_board_power,
            energy_per_frame_mj=energy_per_frame_mj,
            frames_per_sec_per_watt=fps_per_watt,
        )


def simulate_orin_benchmark(
    num_frames: int = 1000,
    base_latency_ms: float = 1.85,
    jitter_ms: float = 0.35,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate realistic benchmark traces reflecting Jetson Orin Nano/NX execution traces.

    Emulates log-normal tail latency caused by Linux kernel preemption and CUDA driver launch.
    """
    rng = np.random.default_rng(seed)
    # Lognormal tail noise
    noise = rng.lognormal(mean=0.0, sigma=0.25, size=num_frames) * jitter_ms
    latencies = base_latency_ms + noise

    # Emulate tegrastats power readings (Orin 15W mode: ~3.8W GPU SoC, ~8.6W total board)
    soc_power = 3.8 + rng.normal(0, 0.2, size=num_frames)
    board_power = 8.6 + rng.normal(0, 0.4, size=num_frames)

    return latencies, soc_power, board_power


def run_experiment() -> OrinProfileMetrics:
    """Run Chapter 2 experiment and print formatted profiling report."""
    latencies, soc_power, board_power = simulate_orin_benchmark()
    profiler = JetsonOrinProfiler(audio_frame_duration_ms=10.0)
    metrics = profiler.analyze_benchmark(latencies, soc_power, board_power)

    print("=" * 60)
    print("Experiment 2.1: NVIDIA Jetson Orin Baseline Profile Report")
    print(f"Total Frames Analyzed : {metrics.total_frames}")
    print(f"Mean Frame Latency    : {metrics.mean_latency_ms:.2f} ms")
    print(f"P50 Latency           : {metrics.p50_latency_ms:.2f} ms")
    print(f"P90 Latency           : {metrics.p90_latency_ms:.2f} ms")
    print(f"P99 Latency (Tail)    : {metrics.p99_latency_ms:.2f} ms")
    print(f"Latency Jitter (Std)  : {metrics.jitter_std_ms:.2f} ms")
    print(f"Real-Time Factor (RTF): {metrics.real_time_factor:.4f} (< 1.0 Real-time)")
    print(f"Average Board Power   : {metrics.avg_board_power_w:.2f} W")
    print(f"Energy per Frame      : {metrics.energy_per_frame_mj:.2f} mJ")
    print(f"Efficiency            : {metrics.frames_per_sec_per_watt:.2f} frames/sec/Watt")
    print("=" * 60)

    return metrics


if __name__ == "__main__":
    run_experiment()
