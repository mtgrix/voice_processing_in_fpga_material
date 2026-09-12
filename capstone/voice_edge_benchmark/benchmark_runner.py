"""Capstone: Voice Edge AI comparative benchmark harness (Jetson Orin vs. FPGA).

PROVENANCE IS PART OF THE DATA. A row that was measured and a row that was written by
hand look identical in a markdown table, and that is how a placeholder becomes a citation.
Every result therefore carries a ``provenance`` field, every export labels each row with it,
and a table containing any synthetic row says so in its own header line.

The numbers currently in this file are SYNTHETIC PLACEHOLDERS. They were written by hand to
give the harness a shape while no hardware had been run. They are not measurements, they do
not come from any publication, and they must never be cited. See docs/plan-v2 gap analysis
section 9.2, which called this the most serious blocker in the project.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Literal

#: Where a number came from. "measured" is reserved for rows produced from a raw log in
#: results/, which the integrity gate requires before any chapter may claim a result.
Provenance = Literal["synthetic", "measured"]

PROVENANCE_LABEL: dict[str, str] = {"synthetic": "SYNTHETIC", "measured": "MEASURED"}

SYNTHETIC_BANNER = (
    "SYNTHETIC PLACEHOLDER DATA, not measured. Never cite these numbers, and never print "
    "this table under a benchmark or results heading."
)


@dataclass
class HardwareBenchmarkResult:
    target_device: str
    backend: str
    precision: str
    model_name: str
    mean_latency_ms: float
    p99_latency_ms: float
    rtf: float
    active_power_w: float
    energy_per_frame_mj: float
    accuracy_metric_name: str
    accuracy_score: float  # e.g., Accuracy % or PESQ
    efficiency_fps_per_watt: float
    provenance: Provenance = "synthetic"


class VoiceEdgeBenchmarkHarness:
    """Benchmark harness comparing Jetson Orin and FPGA edge implementations."""

    def __init__(self) -> None:
        self.results: list[HardwareBenchmarkResult] = []

    def register_result(self, result: HardwareBenchmarkResult) -> None:
        self.results.append(result)

    def generate_pareto_table(self) -> str:
        """Produce a markdown table of all metrics, with every row labelled by provenance."""
        lines: list[str] = []
        if any(r.provenance == "synthetic" for r in self.results):
            lines.append(f"> **{SYNTHETIC_BANNER}**")
            lines.append("")
        header = (
            "| Target Device | Backend | Precision | Provenance | Latency (ms) | P99 (ms) | "
            "RTF | Power (W) | Energy (mJ/fr) | Accuracy | FPS/Watt |"
        )
        sep = "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
        lines += [header, sep]
        for r in self.results:
            acc_str = f"{r.accuracy_score:.2f} ({r.accuracy_metric_name})"
            row = (
                f"| **{r.target_device}** | {r.backend} | {r.precision} | "
                f"`{PROVENANCE_LABEL[r.provenance]}` | "
                f"{r.mean_latency_ms:.2f} | {r.p99_latency_ms:.2f} | "
                f"{r.rtf:.4f} | {r.active_power_w:.1f}W | {r.energy_per_frame_mj:.2f} | "
                f"{acc_str} | {r.efficiency_fps_per_watt:.1f} |"
            )
            lines.append(row)
        return "\n".join(lines)

    def export_json(self, filepath: str) -> None:
        """Write the rows as JSON. Each row carries its own provenance field."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.results], f, indent=2)


def synthetic_demo_fixture() -> VoiceEdgeBenchmarkHarness:
    """SYNTHETIC PLACEHOLDER, not measured, never cite.

    Four hand-written rows that give the harness something to format before any hardware has
    been run. The device names and model name are real; every latency, power, energy and
    accuracy figure below is invented. Do not describe this function as reference data, as
    empirical data, or as a published comparison, in this docstring or anywhere else.
    """
    harness = VoiceEdgeBenchmarkHarness()

    # 1. Jetson Orin Nano (FP16 TensorRT)
    harness.register_result(
        HardwareBenchmarkResult(
            target_device="NVIDIA Jetson Orin Nano",
            backend="TensorRT FP16",
            precision="FP16",
            model_name="MatchboxNet-3x1x64",
            mean_latency_ms=2.15,
            p99_latency_ms=2.90,
            rtf=0.215,
            active_power_w=8.8,
            energy_per_frame_mj=18.92,
            accuracy_metric_name="Acc",
            accuracy_score=97.4,
            efficiency_fps_per_watt=52.8,
        )
    )

    # 2. Jetson Orin Nano (INT8 TensorRT QAT)
    harness.register_result(
        HardwareBenchmarkResult(
            target_device="NVIDIA Jetson Orin Nano",
            backend="TensorRT INT8",
            precision="INT8",
            model_name="MatchboxNet-3x1x64",
            mean_latency_ms=1.45,
            p99_latency_ms=2.10,
            rtf=0.145,
            active_power_w=8.2,
            energy_per_frame_mj=11.89,
            accuracy_metric_name="Acc",
            accuracy_score=97.2,
            efficiency_fps_per_watt=84.1,
        )
    )

    # 3. AMD Kria KV260 (Vitis AI DPU)
    harness.register_result(
        HardwareBenchmarkResult(
            target_device="AMD Xilinx Kria KV260",
            backend="Vitis AI DPUCZDX8G",
            precision="INT8",
            model_name="MatchboxNet-3x1x64",
            mean_latency_ms=1.10,
            p99_latency_ms=1.25,
            rtf=0.110,
            active_power_w=4.8,
            energy_per_frame_mj=5.28,
            accuracy_metric_name="Acc",
            accuracy_score=97.1,
            efficiency_fps_per_watt=189.4,
        )
    )

    # 4. AMD Kria KV260 (FINN Custom Streaming Dataflow)
    harness.register_result(
        HardwareBenchmarkResult(
            target_device="AMD Xilinx Kria KV260",
            backend="FINN Dataflow AXI-Stream",
            precision="INT4/INT8",
            model_name="MatchboxNet-3x1x64",
            mean_latency_ms=0.48,
            p99_latency_ms=0.51,
            rtf=0.048,
            active_power_w=3.9,
            energy_per_frame_mj=1.87,
            accuracy_metric_name="Acc",
            accuracy_score=96.9,
            efficiency_fps_per_watt=534.2,
        )
    )

    return harness


if __name__ == "__main__":
    suite = synthetic_demo_fixture()
    print(SYNTHETIC_BANNER)
    print()
    print("Voice Edge AI benchmark harness, demo fixture (Jetson Orin vs. FPGA)")
    print(suite.generate_pareto_table())
