# Research Note R01: NVIDIA Jetson Orin Architecture & Edge Audio Profiling

- **Source ID**: `R01-01`, `R01-04`
- **Topic**: NVIDIA Jetson Orin GPU Microarchitecture vs. Edge FPGA Baseline
- **Date**: 2026-09-11

---

## 1. Jetson Orin Microarchitectural Fundamentals

The NVIDIA Jetson Orin family (Nano, NX, AGX) is built on the **Ampere GPU architecture**:
- **Streaming Multiprocessors (SMs)**: Each SM contains 128 CUDA cores and 4 3rd-Generation Tensor Cores.
- **Unified Memory Architecture**: CPU and GPU share the same physical LPDDR5 DRAM bus (e.g. 128-bit wide, ~102 GB/s on Orin NX, ~68 GB/s on Orin Nano).
- **Deep Learning Accelerator (DLA 2.0)**: Dedicated fixed-function hardware engine for CNNs, offloading the GPU to save power.

---

## 2. The Audio Streaming Challenge on Jetson Orin

While Jetson Orin excels at large batch throughput (e.g., vision pipelines with $batch \ge 8$ achieving 20–100+ FP16/INT8 TOPS), **real-time audio processing** exposes architectural friction:

1. **Strict $batch = 1$ Penalty**:
   Audio streams frame-by-frame (e.g. 25ms window, 10ms stride = 100 inferences per second per channel). GPU SMs remain largely underutilized due to insufficient parallelism within a single audio frame.

2. **Kernel Launch Overhead & Jitter**:
   Invoking CUDA kernels via the OS driver incurs $5\mu\text{s} - 20\mu\text{s}$ overhead per kernel. When an audio graph has many small operations (STFT, LayerNorm, small convolutions), kernel launch overhead can dominate total inference time.

3. **Power Inefficiency at Low Duty Cycle**:
   Even at low clock frequencies, the baseline SoC idle power of Jetson Orin ranges from 3W to 7W. For continuous always-on voice listening (KWS/VAD), this results in unacceptable energy consumption compared to dedicated hardware.
