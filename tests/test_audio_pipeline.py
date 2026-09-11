"""Integration test verifying end-to-end audio pipeline and benchmark harness."""

from __future__ import annotations

from capstone.voice_edge_benchmark.benchmark_runner import build_default_benchmark_suite
from chapter01.exp_01_streaming_audio_pipeline import run_experiment as run_exp_01
from chapter02.exp_02_jetson_orin_profiler import run_experiment as run_exp_02


def test_full_pipeline_smoke_run() -> None:
    """Run all foundational experiments and verify output validity."""
    exp1_res = run_exp_01()
    assert exp1_res["sqnr_db"] > 50.0

    exp2_res = run_exp_02()
    assert exp2_res.real_time_factor < 1.0

    harness = build_default_benchmark_suite()
    assert len(harness.results) >= 4
    pareto_table = harness.generate_pareto_table()
    assert "NVIDIA Jetson Orin" in pareto_table
    assert "AMD Xilinx Kria KV260" in pareto_table
