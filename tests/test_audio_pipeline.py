"""Smoke tests for the audio pipeline, the Orin profiler and the benchmark harness.

These assert that the machinery runs, that its output has the right shape, and that every
row states where it came from. They deliberately do not assert measurement values. A test
that pins 2.15 ms turns a hand-written placeholder into a contract that later work must not
break, which is the failure mode plan-v2 section 9.2 exists to close.
"""

from __future__ import annotations

from pathlib import Path

from capstone.voice_edge_benchmark.benchmark_runner import (
    SYNTHETIC_BANNER,
    HardwareBenchmarkResult,
    synthetic_demo_fixture,
)
from chapter01.exp_01_streaming_audio_pipeline import run_experiment as run_exp_01
from chapter02.exp_02_jetson_orin_profiler import run_experiment as run_exp_02


def test_foundational_experiments_run() -> None:
    """The two host-runnable experiments produce output of the right kind."""
    exp1_res = run_exp_01()
    assert exp1_res["sqnr_db"] > 50.0

    exp2_res = run_exp_02()
    assert exp2_res.real_time_factor < 1.0


def test_demo_fixture_rows_are_all_labelled_synthetic() -> None:
    """Every row of the demo fixture admits it was not measured."""
    rows = synthetic_demo_fixture().results
    assert len(rows) >= 4
    assert all(isinstance(r, HardwareBenchmarkResult) for r in rows)
    assert [r.provenance for r in rows] == ["synthetic"] * len(rows)


def test_pareto_table_announces_its_own_provenance() -> None:
    """The rendered table cannot be lifted out of this file without its warning."""
    table = synthetic_demo_fixture().generate_pareto_table()
    assert SYNTHETIC_BANNER in table
    assert "Provenance" in table
    assert table.count("`SYNTHETIC`") == len(table.splitlines()) - 4


def test_measurement_sounding_language_is_gone() -> None:
    """Regression guard: the phrasing that made placeholders citable must not return."""
    import capstone.voice_edge_benchmark.benchmark_runner as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "Academic Benchmark Matrix" not in source
    assert "empirical publications" not in source
    assert "build_default_benchmark_suite" not in source
