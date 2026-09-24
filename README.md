# Voice Edge AI: From Jetson Orin to FPGA

<h3 align="center">Hardware Acceleration for Real-Time Streaming Audio, DSP & Neural Acoustic Models</h3>

<p align="center">
  <em>An open-source research framework, reproducible benchmark suite, and executable monograph for migrating voice AI models from NVIDIA Jetson Orin (Edge GPU) to AMD Xilinx Kria / Zynq UltraScale+ (FPGA).</em>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg" alt="License: GPL-3.0-or-later"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Python-%3E%3D3.12-informational.svg" alt="Python: >=3.12"></a>
  <a href="#hardware-targets--toolchains"><img src="https://img.shields.io/badge/Hardware-Jetson%20Orin%20%7C%20AMD%20Xilinx%20FPGA-orange.svg" alt="Hardware Target"></a>
  <a href="#scientific-rigor--verification-standards"><img src="https://img.shields.io/badge/CI%20Gate-Passing-success.svg" alt="CI Gate"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Code%20Style-Ruff-000000.svg" alt="Code Style: Ruff"></a>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Types-Mypy%20Strict-blue.svg" alt="Type Check: Mypy Strict"></a>
  <a href="#project-editions--monograph"><img src="https://img.shields.io/badge/Edition-English%20%7C%20Ti%E1%BA%BFng%20Vi%E1%BB%87t-brightgreen.svg" alt="Editions"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

---

## Table of Contents

- [About the Project](#about-the-project)
- [The Architectural Dilemma: Edge GPU vs. FPGA](#the-architectural-dilemma-edge-gpu-vs-fpga)
- [The Two Core Mental Models](#the-two-core-mental-models)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [10-Chapter Curriculum & Roadmap](#10-chapter-curriculum--roadmap)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Hardware Targets & Toolchains](#hardware-targets--toolchains)
- [Scientific Rigor & Verification Standards](#scientific-rigor--verification-standards)
- [Project Editions & Monograph](#project-editions--monograph)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

---

## About the Project

Voice processing at the physical edge powers ambient computing—ranging from always-on **Keyword Spotting (KWS)** and low-latency **Speech Enhancement (SE)** to streaming **Automatic Speech Recognition (ASR)** via Conformer and Transformer architectures.

While edge GPUs such as the **NVIDIA Jetson Orin** deliver remarkable raw tensor compute for batched offline tasks, real-time voice applications operate under strict frame-by-frame deadlines ($\le 10–25\text{ ms}$), batch sizes of one ($\text{batch}=1$), and strict power constraints ($<10\text{ W}$). Under these streaming dynamics, GPU architectures suffer from kernel launch overheads, underutilized SIMT cores, DRAM latency walls, and high latency jitter.

**Voice Edge AI: From Jetson Orin to FPGA** is an open-source, executable research initiative and monograph that details the end-to-end migration of streaming voice processing systems from NVIDIA Jetson Orin to AMD Xilinx FPGA kits (Kria KV260, Zynq UltraScale+). By transforming linear execution into spatial dataflow pipelines, this project demonstrates how dedicated FPGA fabrics achieve sub-millisecond deterministic latency, bit-exact DSP front-ends, and order-of-magnitude energy efficiency ($\text{mJ/frame}$).

---

## The Architectural Dilemma: Edge GPU vs. FPGA

| Dimension | NVIDIA Jetson Orin (Edge GPU) | AMD Xilinx Kria / Zynq UltraScale+ (FPGA) |
|---|---|---|
| **Execution Paradigm** | Temporal SIMT (Single Instruction, Multiple Threads) | Spatial Dataflow Pipeline (Custom Hardware Fabric) |
| **Streaming Performance ($\text{batch}=1$)** | Low compute efficiency; thousands of cores idle | Maximum efficiency; fully unrolled hardware pipelines |
| **Initiation Interval ($II$)** | Coarse-grained kernel launch ($II \gg 1$) | Cycle-deterministic pipeline rate ($II = 1$) |
| **Latency Jitter** | High (OS scheduler, memory contention, DVFS) | Near-zero (Clock-cycle deterministic dataflow) |
| **DSP Preprocessing** | Host memory $\leftrightarrow$ Device CUDA copies | Direct I2S/PDM pin ingestion $\to$ On-chip streaming STFT |
| **Quantization Support** | Power-of-2 fixed points (FP32, FP16, INT8) | Arbitrary precision (INT8, INT4, non-uniform, Ternary) |
| **Energy Profile** | Dynamic power spikes ($>8–15\text{ W}$ baseline) | Ultra-low steady-state power ($<3–5\text{ W}$ per pipeline) |

---

## The Two Core Mental Models

This project is grounded in two fundamental abstractions that anchor signal processing, neural network architecture, and silicon hardware mapping:

### Mental Model 1: Edge Voice System Decomposition
$$\text{Voice Edge System} = \text{Audio Preprocessing / DSP} + \text{Neural Acoustic Model} + \text{Hardware Microarchitecture}$$

A voice edge accelerator cannot be analyzed as an isolated neural network. The physical audio pipeline (microphones, PDM/I2S, sliding ring buffer, STFT, and Mel filterbanks) dictates feature dimensionality, frame-rate timing, and memory footprints. The acoustic model transforms audio frames into acoustic tokens, while the hardware microarchitecture determines pipeline throughput, arithmetic mapping, and memory hierarchy.

### Mental Model 2: Hardware Migration Lifecycle
$$\text{Hardware Migration} = \text{Profiling \& Bottlenecks (GPU)} \longrightarrow \text{Hardware-Aware Quantization} \longrightarrow \text{Spatial Architecture Mapping (FPGA)} \longrightarrow \text{Pareto Verification}$$

Hardware migration is a multi-stage engineering progression:
1. **Profiling & Bottlenecks**: Quantify latency, kernel execution timelines, and memory-bandwidth bottlenecks on Jetson Orin.
2. **Hardware-Aware Quantization**: Emulate fixed-point arithmetic (PTQ/QAT) and guard task-specific accuracy metrics (EER, WER, PESQ/STOI).
3. **Spatial Architecture Mapping**: Map compute graphs to spatial dataflow engines (FINN, Vitis AI DPU, Vivado HLS, Custom RTL).
4. **Pareto Verification**: Construct multi-objective Pareto frontiers comparing accuracy, Real-Time Factor (RTF), latency jitter, energy per frame ($\text{mJ/frame}$), and hardware resource utilization.

---

## System Architecture

```text
                  PHYSICAL ACOUSTIC DOMAIN
           (Microphones / MEMS Sensors: 16 kHz, 16-bit PCM)
                            │
                            ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. AUDIO PREPROCESSING & STREAMING DSP FRONT-END                       │
│    • Frame Ingestion: Circular Ring Buffer (25 ms Frame, 10 ms Step)   │
│    • Pre-Emphasis & Windowing (Hamming / Hann)                         │
│    • Real-Time Fast Fourier Transform (Radix-2 / Radix-4 Streaming FFT) │
│    • Mel-Scale Triangular Filterbanks (80 Mel channels, Log Energy)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Log-Mel Energy Vectors
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. NEURAL ACOUSTIC MODEL BACKBONE                                      │
│    • Keyword Spotting (KWS): ResNet-18, Depthwise-Separable CNN (DS-CNN)│
│    • Speech Enhancement (SE): Conv-TasNet, Dual-Path RNN, UNet-Denoise  │
│    • Streaming ASR: Chunked Streaming Conformer / Emformer             │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
    (Edge GPU Path) │                                │ (FPGA Spatial Path)
                    ▼                                ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│ 3A. NVIDIA JETSON ORIN BACKEND       │  │ 3B. AMD XILINX FPGA FABRIC   │
│ • Ampere Streaming Multiprocessors   │  │ • Spatial Streaming Dataflow │
│ • TensorRT FP16 / INT8 Precision     │  │ • Pipelined DSP48/58 Slices  │
│ • Unified LPDDR5 Memory Subsystem    │  │ • On-Chip BRAM / URAM Lines  │
│ • Host-Device Memory Transfers       │  │ • Zero-Copy AXI-Stream Engine│
└───────────────────┬──────────────────┘  └──────────────┬───────────────┘
                    │                                    │
                    └─────────────────┬──────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. MULTI-OBJECTIVE PARETO VERIFICATION & METRICS                       │
│    • Quality: Accuracy / EER (KWS), PESQ / STOI (SE), WER / CER (ASR)  │
│    • Latency: Mean Frame Latency, P99 Tail Latency, Jitter, RTF (<1.0) │
│    • Efficiency: Energy per Frame (mJ/frame), Board Power (W), TOPS/W  │
│    • Hardware Utilization: LUTs, Flip-Flops, DSP Slices, BRAM/URAM     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Executable Monograph Format**: Every chapter pairs academic exposition with runnable Python simulation, hardware profiling scripts, and automated test cases.
- **Bit-Exact Streaming DSP**: Online frame-by-frame STFT and Mel filterbanks verified to exceed $>130\text{ dB}$ Signal-to-Quantization-Noise Ratio (SQNR) against offline FP32 baselines.
- **Dual-Target Empirical Benchmarks**: Direct comparative profiling between NVIDIA Jetson Orin (TensorRT, `tegrastats`) and AMD Xilinx Kria KV260 / Zynq UltraScale+.
- **Domain-Specific Quantization Science**: Rigorous PTQ and QAT workflows for INT8/INT4/non-uniform quantization, safeguarding task-specific metrics (EER, WER, PESQ, STOI).
- **Four FPGA Acceleration Paradigms**: In-depth trade-off analysis across AMD Vitis AI DPU, FINN Streaming Dataflow, Vivado HLS C/C++, and Custom Register-Transfer Level (RTL) designs.
- **Academic Citation & Evidence Integrity**: Automated CI gates linking every hardware metric and algorithmic assertion to primary literature indexed in `docs/source_index.json`.

---

## 10-Chapter Curriculum & Roadmap

The project and monograph are organized into four sequential parts comprising 10 chapters:

| Part | Chapter | Chapter Title | Core Research & Engineering Focus |
|:---:|:---:|---|---|
| **I. Foundations & GPU Baselines** | **01** | **Streaming Voice Pipeline Architecture & Real-Time Constraints** | Streaming audio mechanics, frame latency deadlines ($\le 10–25\text{ ms}$), batch-1 execution constraints, and feature extraction. |
| | **02** | **NVIDIA Jetson Orin Microarchitecture & Baseline Profiling** | Ampere GPU architecture, Tensor Cores, unified LPDDR5 memory, TensorRT compilation, and `tegrastats` power/latency profiling. |
| | **03** | **Streaming Bottlenecks on Edge GPU Architectures** | Root-cause analysis of GPU inefficiencies at $\text{batch}=1$: kernel launch overheads, underutilized SIMT lanes, and power jitter. |
| **II. FPGA Microarchitecture & Acceleration** | **04** | **FPGA Microarchitecture: Logic Slices, DSPs, BRAM/URAM & Dataflow** | Spatial computing fundamentals, feedforward pipelining, distributed memory hierarchies, and achieving initiation interval $II=1$. |
| | **05** | **Comparative Acceleration Methodologies on FPGA** | Architectural comparison of 4 design flows: AMD Vitis AI DPU, FINN Streaming Dataflow, Vivado HLS C/C++, and Custom RTL. |
| | **06** | **Hardware Acceleration for Audio Preprocessing & DSP** | Fixed-point bit-exact STFT/FFT engine, Mel filterbank generation, and direct on-chip I2S/PDM digital microphone interfacing. |
| **III. Model Compression & Quantization** | **07** | **Hardware-Aware Quantization Science for Voice Models** | Non-uniform, INT8, and INT4 Post-Training Quantization (PTQ) and Quantization-Aware Training (QAT) bound to EER, WER, and PESQ/STOI. |
| | **08** | **Accelerating Core Voice Model Compute Blocks** | Hardware mapping for multi-head self-attention, non-linear Softmax/LayerNorm approximations, and depthwise separable convolutions. |
| **IV. System Integration & Monograph Synthesis** | **09** | **SoC System Integration & Hardware/Software Co-Design** | Heterogeneous ARM Host + FPGA fabric communication via AXI-Stream, DMA transfers, PYNQ runtime, and shared DDR management. |
| | **10** | **Experimental Benchmarking, Pareto Analysis & Monograph Synthesis** | Systematic empirical benchmark setup, multi-objective Pareto frontier plotting (Quality vs. Latency vs. mJ/frame), and monograph write-up. |

---

## Repository Structure

```text
voice_jetson_to_fpga_learning-journey/
├── book-en/                # English monograph & academic paper drafts
├── book/                   # Vietnamese canonical monograph manuscript
├── chapter01/              # Ch 01: Streaming Audio Pipeline & Online STFT/Mel (exp_01)
├── chapter02/              # Ch 02: Jetson Orin Latency, Jitter & Energy Profiler (exp_02)
├── chapter03–10/           # Ch 03 through Ch 10 experiments, tests, and hardware models
├── capstone/               # Voice Edge Benchmark: Comparative harness (Orin vs. FPGA)
│   └── voice_edge_benchmark/
│       ├── benchmark_runner.py  # Unified benchmark execution and Pareto export
│       └── README.md            # Methodology & hardware execution instructions
├── docs/                   # Standards, verification records, and research bibliography
│   ├── BOOK_PEDAGOGY.md    # Pedagogical standards (Local Sufficiency, 3-level intro)
│   ├── RESEARCH_METHODOLOGY.md # IEEE/ACM academic rigor & empirical protocols
│   ├── source_index.json   # Machine-readable authoritative bibliography registry
│   ├── BOOK_STATUS.md      # Chapter manuscript drafting progress tracking
│   ├── EXPERIMENT_STATUS.md# Hardware-in-the-loop experiment tracking table
│   └── verification/       # Formal claims, measurement records & baseline gates
├── results/                # Raw benchmark logs, profiles, and SHA256SUMS manifest
├── scripts/                # Integrity verification, LaTeX compilation, and build tools
│   ├── verify_integrity.py # Master verification gate script
│   └── verification/       # Specialized AST and citation verification modules
├── tests/                  # Pytest test suite covering pipelines, schemas, and gates
├── Makefile                # Unified developer commands and CI gate entrypoints
└── pyproject.toml          # Python project specification and tool configuration
```

---

## Quick Start

### 1. Prerequisites
- **Python**: Version $\ge 3.12$
- **Package Manager**: `uv` (recommended) or `pip`
- **Optional Tools**: `pandoc` and `lualatex` (for building monograph PDF editions)

### 2. Installation
Clone the repository and install the development environment:

```bash
git clone https://github.com/mtgrix/voice_processing_in_fpga_material.git
cd voice_processing_in_fpga_material

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package with development, audio, and ML extras
pip install -e .[dev,audio,ml]
```

### 3. Verify Repository Integrity & Run Test Suite
Ensure code quality, typing, and academic citation linkages pass:

```bash
# Run pytest test suite (139+ tests)
python -m pytest

# Run Ruff linter and format checker
python -m ruff check .
python -m ruff format --check .

# Run Mypy static type verification
python -m mypy .

# Run master integrity and evidence verification gate
python scripts/verify_integrity.py
```

Or execute the complete continuous integration gate via `make`:
```bash
make gate
```

### 4. Running Sample Experiments

#### Experiment 1.1: Streaming Audio Preprocessing Pipeline
Demonstrates frame-by-frame streaming STFT and Mel filterbank feature extraction with circular buffering:
```bash
python chapter01/exp_01_streaming_audio_pipeline.py
```
*Expected Output:*
```text
============================================================
Experiment 1.1: Streaming Audio Pipeline Results
Total Frames Processed : 98
Mean Absolute Error     : 0.000000e+00
Signal-to-Noise (SQNR)  : 134.48 dB
============================================================
```

#### Experiment 2.1: NVIDIA Jetson Orin Baseline Profiler
Simulates and evaluates streaming audio inference latency, tail jitter (P99), Real-Time Factor (RTF), and energy per frame:
```bash
python chapter02/exp_02_jetson_orin_profiler.py
```
*Expected Output:*
```text
============================================================
Experiment 2.1: NVIDIA Jetson Orin Baseline Profile Report
Total Frames Analyzed : 1000
Mean Frame Latency    : 2.21 ms
P50 Latency           : 2.20 ms
P90 Latency           : 2.33 ms
P99 Latency (Tail)    : 2.45 ms
Latency Jitter (Std)  : 0.09 ms
Real-Time Factor (RTF): 0.2208 (< 1.0 Real-time)
Average Board Power   : 8.61 W
Energy per Frame      : 19.02 mJ
Efficiency            : 52.57 frames/sec/Watt
============================================================
```

#### Capstone: Comparative Voice Edge Benchmark Harness
Executes the unified comparative benchmarking suite across platforms:
```bash
python capstone/voice_edge_benchmark/benchmark_runner.py
```

---

## Hardware Targets & Toolchains

### Edge GPU Target: NVIDIA Jetson Platform
- **Supported Boards**: NVIDIA Jetson Orin Nano (4GB / 8GB), Jetson Orin NX (8GB / 16GB)
- **Architecture**: NVIDIA Ampere Architecture with Tensor Cores, ARM Cortex-A78AE CPU
- **Software Stack**: JetPack 5.1+ / 6.0+, CUDA 12.x, TensorRT 8.6+, `tegrastats` profiling daemon

### Edge FPGA Target: AMD Xilinx Platform
- **Supported Boards**: AMD Xilinx Kria KV260 Vision AI Starter Kit, Zynq UltraScale+ MPSoC (XCZU5EV / ZU3EG)
- **Architecture**: Quad-core ARM Cortex-A53, Dual-core Cortex-R5F, UltraScale+ Programmable Logic (PL)
- **Software Stack**: AMD Vivado Design Suite 2022.2+, Vitis HLS, Vitis AI 3.0+ DPU, FINN Compiler, PYNQ v3.0+

---

## Scientific Rigor & Verification Standards

To prevent ungrounded claims, this repository enforces strict empirical verification:

1. **The 13-Section Experiment Template**: Every experiment directory (`chapterXX/README.md`) follows a formal structure containing mathematical derivations, measurement methodology, hardware trade-offs, and empirical findings.
2. **Status Markers**:
   - 🚧 **Scaffolded**: Architectural design and software model ready; hardware pending.
   - 📖 **Hardware-in-the-Loop**: Hardware execution required; run logs captured manually.
   - ✅ **Verified Result**: Execution validated with checksummed raw logs in `results/SHA256SUMS`.
3. **Traceability Registry**: Hardware architecture parameters, latency figures, and energy claims must resolve to primary citations indexed in `docs/source_index.json` and validated by `scripts/verify_integrity.py`.

---

## Project Editions & Monograph

This repository hosts two companion editions of the research monograph:

- **English Monograph & Paper Drafts** (`book-en/`): Formatted for academic paper submissions and international reference.
- **Vietnamese Canonical Manuscript** (`book/`): The canonical monograph edition written with clear pedagogical scaffolding.

To compile both monograph editions into high-quality PDFs (requires `pandoc` and `lualatex`):
```bash
make book
```

---

## Contributing

Contributions are warmly welcomed! Whether you are implementing hardware HLS kernels, measuring physical power on Jetson/FPGA boards, optimizing streaming models, or refining pedagogical explanations:

1. Check open issues or start a discussion.
2. Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`docs/BOOK_PEDAGOGY.md`](docs/BOOK_PEDAGOGY.md).
3. Ensure all pull requests adhere to conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `perf:`).
4. Verify that `make gate` passes cleanly before submitting.

---

## Citation

If you use this research framework, code, or monograph in your research or hardware designs, please cite:

```bibtex
@book{voice_jetson_to_fpga_journey,
  title     = {Voice Edge AI: From Jetson Orin to FPGA},
  author    = {Nguyen, Minh Tuan and Voice Edge AI Contributors},
  year      = {2026},
  publisher = {Open Source Monograph \& Research Framework},
  url       = {https://github.com/mtgrix/voice_processing_in_fpga_material}
}
```

---

## License

This project is licensed under the [GNU General Public License v3.0 or later (GPL-3.0-or-later)](LICENSE).
