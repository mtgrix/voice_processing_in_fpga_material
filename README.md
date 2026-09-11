# Voice Edge AI: From Jetson Orin to FPGA

<h4 align="center">Từ Jetson Orin đến FPGA: Tăng tốc Phần cứng Mô hình Giọng nói — An Open-Source Bilingual Monograph & Research Platform</h4>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0--or--later-blue" alt="license: GPL-3.0-or-later"></a>
  <a href="#editions"><img src="https://img.shields.io/badge/Vietnamese-Canonical-green" alt="Vietnamese"></a>
  <a href="#editions"><img src="https://img.shields.io/badge/English-Paper%20Drafts-blue" alt="English"></a>
  <a href="#testing"><img src="https://img.shields.io/badge/python-%3E%3D3.12-informational" alt="python: >=3.12"></a>
  <a href="#testing"><img src="https://img.shields.io/badge/hardware-Jetson%20Orin%20%7C%20FPGA%20Kria-orange" alt="hardware: Jetson Orin | FPGA"></a>
</p>

> An open-source, executable monograph and scientific research framework on Edge Voice AI hardware acceleration — from first principles of acoustic signal processing to deep hardware mapping on NVIDIA Jetson Orin and AMD Xilinx FPGAs.

---

## The Two Mental Models

```text
Model 1 (Execution Model)
  Voice Edge System  =  Streaming Audio Pipeline  +  Neural Acoustic/Spectral Graph  +  Hardware Microarchitecture
  (Hệ thống Thoại Biên  =  Chuỗi Âm thanh Liên tục  +  Đồ thị Mạng Nơ-ron Âm học  +  Vi kiến trúc Phần cứng)

Model 2 (Research & Migration Lifecycle)
  Hardware Migration  =  Profiling & Bottlenecks  →  Hardware-Aware Quantization  →  Spatial Architecture Mapping  →  Pareto Verification
  (Vòng đời Di chuyển  =  Định lượng Điểm nghẽn  →  Lượng tử hóa Thích ứng  →  Ánh xạ Kiến trúc Không gian  →  Đánh giá Biên tối ưu Pareto)
```

These are **engineering learning models** designed to demystify edge AI acceleration. They clearly separate acoustic signal processing principles, neural network graph representations, and digital hardware microarchitecture.

---

## Chapters & Research Curriculum

| # | Title | Vietnamese Title | Core Research Question |
|:-:|-------|------------------|------------------------|
| 1 | **From Acoustic Waves to Edge Inference** | Từ Sóng Âm đến Suy diễn Biên | How does streaming audio differ fundamentally from computer vision in edge compute? |
| 2 | **Jetson Orin: Edge Baseline & Limits** | Jetson Orin: Kiến trúc Điểm chuẩn & Giới hạn Vật lý | How do Ampere Tensor Cores and unified LPDDR5 perform under strict $batch=1$ streaming audio? |
| 3 | **The Streaming Bottleneck on GPUs** | Khoảng cách Thực tế: Điểm nghẽn Streaming trên Edge GPU | Why do GPUs suffer from power waste and latency jitter during fine-grained audio frame processing? |
| 4 | **FPGA Microarchitecture for Edge AI** | Vi kiến trúc FPGA cho Trí tuệ Nhân tạo Biên | How do LUTs, DSP slices, BRAM/URAM, and AXI-Stream enable true spatial dataflow pipelining? |
| 5 | **Acceleration Methodologies** | Phương pháp luận Tăng tốc: HLS, DPU và FINN | How do Vitis AI DPU, FINN Streaming Dataflow, and Custom HLS engines compare in voice workloads? |
| 6 | **Audio Front-End Hardware Acceleration** | Tăng tốc Tầng Tiền xử lý Âm thanh | How do we build bit-exact fixed-point FFT/STFT and direct I2S/PDM hardware interfaces? |
| 7 | **Hardware-Aware Quantization Science** | Khoa học Lượng tử hóa Thích ứng Phần cứng | How do PTQ and QAT achieve INT8/INT4 precision without degrading WER or PESQ? |
| 8 | **Accelerating Attention & Conformer** | Tăng tốc Cơ chế Attention & Conformer trên FPGA | How do we implement non-linear Softmax approximation and depthwise convs on FPGA fabric? |
| 9 | **SoC Integration & Hardware-Software Co-Design** | Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng/Phần mềm | How do ARM host and programmable logic interact efficiently via DMA and AXI interconnects? |
| 10 | **Research Methodology & Paper Publication** | Phương pháp Luận Nghiên cứu Khoa học & Bài báo | How do we construct a rigorous Pareto frontier (WER vs. Latency vs. Joules) for top-tier publication? |

---

## Theoretical & Empirical Pillars

| Pillar | Focus | Key Metrics & Formalisms |
|--------|-------|--------------------------|
| **Acoustic Front-End** | Time-Frequency Analysis | $O(N \log N)$ FFT complexity, Fixed-point dynamic range, Mel-scale triangular filterbanks |
| **GPU Microarchitecture** | NVIDIA Jetson Orin | SM warp scheduling, Tensor Core tile sizes, Unified Memory page migration, Latency jitter |
| **FPGA Spatial Dataflow** | AMD Xilinx UltraScale+ | Initiation Interval ($II=1$), Pipeline depth, DSP48E2 utilization, BRAM dual-port banking |
| **Quantization Theory** | Information Preservation | MSE-optimal scaling, KL-divergence calibration, Hessian-weighted sensitivity, WER/PESQ degradation bounds |
| **Pareto Frontier & Energy** | Edge AI Evaluation | Real-Time Factor (RTF), Energy-Delay Product (EDP), $\text{Joules}/\text{inference frame}$, $\text{TOPS}/\text{W}$ |

---

## Repository Structure

```text
voice_jetson_to_fpga_learning-journey/
├── book/                   # Canonical Vietnamese manuscript
├── book-en/                # English manuscript & Paper draft chapters
├── chapter01–02/           # Runnable Python & simulation experiments + unit tests
├── capstone/               # Voice Edge Benchmark (Jetson vs. FPGA comparative suite)
├── docs/                   # Pedagogy policy, research methodology, sources, notes
├── scripts/                # Verification and automated build scripts
└── tests/                  # Repository, pedagogy, and numerical integrity tests
```

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- Recommended: `uv` package manager (`python -m pip install uv`)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/MinhTuan76800310/voice_jetson_to_fpga_learning-journey.git
cd voice_jetson_to_fpga_learning-journey

# Run tests
python -m pytest

# Run linting
python -m ruff check .
```

### Running Experiments

```bash
# Chapter 1: Streaming Audio Pipeline Simulation
python chapter01/exp_01_streaming_audio_pipeline.py

# Chapter 2: Jetson Orin Latency & Energy Profiler
python chapter02/exp_02_jetson_orin_profiler.py
```

---

## Research Paper Citation

```bibtex
@book{nguyen2026voiceedge,
  title     = {Voice Edge AI: From Jetson Orin to FPGA},
  author    = {Nguyen, Minh Tuan},
  year      = {2026},
  publisher = {Open Source Monograph \& Research Framework},
  url       = {https://github.com/MinhTuan76800310/voice_jetson_to_fpga_learning-journey}
}
```

**License:** [GPL-3.0-or-later](LICENSE)
