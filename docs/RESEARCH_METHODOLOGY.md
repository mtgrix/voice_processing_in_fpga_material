# Research Methodology Guide — Voice Edge AI: Jetson Orin to FPGA

> **Academic and Empirical Research Manual.** This document governs experimental design, metric collection, and scientific rigor for publishing research papers comparing NVIDIA Jetson Orin with FPGA edge accelerators.

---

## 1. The Research Objective & Paper Scope

The central problem of this research journey is:
> *How does spatial dataflow acceleration on FPGA kits compare against parallel SIMT execution on NVIDIA Jetson Orin for continuous, streaming, low-latency voice AI workloads under constrained thermal/power envelopes?*

### Target Publication Venues
- **Top Hardware Acceleration & Systems Conferences:**
  - IEEE/ACM International Symposium on Field-Programmable Custom Computing Machines (**FCCM**)
  - ACM/SIGDA International Symposium on Field-Programmable Gate Arrays (**FPGA**)
  - International Conference on Field-Programmable Technology (**FPT**)
  - Design, Automation and Test in Europe (**DATE**) / International Conference on Computer-Aided Design (**ICCAD**)
- **Speech & Signal Processing Venues:**
  - IEEE International Conference on Acoustics, Speech and Signal Processing (**ICASSP**)
  - Annual Conference of the International Speech Communication Association (**Interspeech**)
- **Journals:**
  - IEEE Embedded Systems Letters (**ESL**)
  - IEEE Transactions on Very Large Scale Integration (**TVLSI**) Systems
  - ACM Transactions on Reconfigurable Technology and Systems (**TRETS**)

---

## 2. Fair & Controlled Benchmarking Methodology

To be acceptable in peer-reviewed scientific literature, comparison between GPU and FPGA edge devices must follow strict controls:

### A. Equivalent Power Envelopes
- NVIDIA Jetson Orin Nano / Orin NX operate under configurable TDP modes (e.g. 7W, 10W, 15W, 25W via `nvpmodel`).
- FPGA SoCs (e.g. AMD Kria KV260 with Zynq UltraScale+ XCZU5EV) typically dissipate 5W–12W under active neural workload.
- Comparisons must benchmark at matched power budgets (e.g. Jetson Orin 10W mode vs. Kria KV260 full board power).

### B. Streaming Latency vs. Throughput Distinction
- Vision models commonly report batch throughput (frames per second with $batch \ge 8$ or $16$).
- **Voice AI is fundamentally streaming**: audio arrives continuously in windows (e.g., 20ms or 40ms frames with 10ms hop).
- The metric of primary interest is **P99 Frame Latency** and **Real-Time Factor (RTF)** under $batch=1$:
  $$\text{RTF} = \frac{\text{Processing Time for Audio Segment}}{\text{Duration of Audio Segment}}$$
  An $\text{RTF} < 1.0$ is required for real-time operation. Edge targets require $\text{RTF} \le 0.1$ to leave headroom for multi-tasking.

### C. Standardized Measurement Metrics

| Metric Dimension | Jetson Orin Measurement | FPGA Measurement | Unit |
|---|---|---|---|
| **Acoustic Accuracy** | Word Error Rate (WER) / PESQ | Word Error Rate (WER) / PESQ | %, MOS score |
| **Compute Latency** | TensorRT event timer / CUDA Events | Cycle counter in hardware logic / AXI timer | Milliseconds ($\text{ms}$) |
| **Latency Jitter** | Kernel launch variation over $10^4$ frames | Clock cycle deterministic execution | $\sigma_{\text{latency}}$ ($\mu\text{s}$) |
| **Active Power** | Integrated INA3221 voltage/current sensors (`tegrastats`) | Board power shunt monitor / Xilinx Power Estimator (XPE) | Watts ($\text{W}$) |
| **Energy Efficiency** | $\text{Joules per Frame} = P_{\text{avg}} \times \Delta t_{\text{frame}}$ | $\text{Joules per Frame} = P_{\text{avg}} \times \Delta t_{\text{frame}}$ | Millijoules ($\text{mJ}$) |
| **Silicon Area / Cost** | Standard die area & BOM price ($/unit) | LUT, FF, DSP48, BRAM, URAM utilization | % and dollar cost |

---

## 3. Structure of the Scientific Paper

A standard manuscript originating from this research framework must contain:

1. **Abstract**: Problem statement (GPU streaming latency/power overhead in voice), proposed FPGA acceleration architecture, key empirical results (e.g., "$2.8\times$ lower energy per frame, $0.15\times$ deterministic latency with $<0.2\%$ WER drop").
2. **Introduction & Motivation**: Why edge voice requires continuous inference, the limitations of SIMT GPUs at $batch=1$, and the opportunity of custom spatial pipelines.
3. **Background & Related Work**: Acoustic front-end (STFT, Mel), baseline model architecture (KWS / Conformer / RNNoise), existing GPU & FPGA implementations.
4. **Hardware-Aware Model Compression**: Quantization-Aware Training (QAT), fixed-point error analysis, sensitive layer protection.
5. **Proposed FPGA Accelerator Microarchitecture**:
   - Streaming Audio Preprocessor (FFT/Mel AXI-Stream core)
   - Neural Compute Engine (Dataflow pipeline or DPU custom overlay)
   - Memory Subsystem (ping-pong BRAM buffers, zero DRAM stall streaming)
6. **Experimental Evaluation**:
   - Experimental setup & hardware specification
   - Accuracy validation (WER / PESQ)
   - Latency distribution & jitter analysis (Orin vs. FPGA)
   - Power & Energy consumption breakdown
   - Pareto Frontier: Accuracy vs. Latency vs. Joules
7. **Discussion & Lessons Learned**: Thermal dissipation, programming effort (CUDA vs HLS/RTL), adaptability to new model topologies.
8. **Conclusion & Future Directions**.
