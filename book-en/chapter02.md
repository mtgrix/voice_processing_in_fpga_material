# Chapter 2: Jetson Orin: Edge Baseline & Limits

> *"A system-on-chip capable of hundreds of tera-operations per second (TOPS) does not inherently provide instantaneous latency for a continuous 10-millisecond audio frame."*

---

## 2.1 Intuition: The Power and Paradox of NVIDIA Jetson Orin

The NVIDIA Jetson Orin family (Nano, NX, AGX) represents the established industry baseline for edge AI computing. Featuring NVIDIA's Ampere GPU architecture, 3rd-generation Tensor Cores, and dedicated Deep Learning Accelerators (DLA 2.0), it delivers unmatched floating-point and integer performance across computer vision workloads.

However, streaming voice AI applications reveal a performance paradox:
1. **Low Compute Utilization**: GPU SM utilization regularly drops below $15\%$ because fine-grained audio frames cannot saturate large SIMT thread arrays.
2. **High Static Idle Power**: Baseline SoC idle power consumes $3\text{W} - 6\text{W}$, which is prohibitive for always-on battery-powered voice trigger devices.
3. **Latency Jitter**: Kernel launch overheads ($5\mu\text{s} - 20\mu\text{s}$) and operating system thread scheduling induce non-deterministic tail latencies.

---

## 2.2 Microarchitecture: From CUDA Cores to Tensor Cores

Within Jetson Orin, execution resources reside within Streaming Multiprocessors (SMs):
- **Matrix-Vector vs Matrix-Matrix Operations**: Under $batch=1$, neural linear layers degrade from compute-bound General Matrix Multiplication (GEMM) to memory-bandwidth-bound General Matrix-Vector Multiplication (GEMV).
- **LPDDR5 Bottleneck**: The GPU spends excessive cycles idling while awaiting weight transfers from unified DRAM rather than executing arithmetic MAC operations.

---

## 2.3 Benchmarking Methodology: TensorRT and Tegrastats

To establish an unassailable empirical baseline for academic publication:
- Models are compiled with NVIDIA TensorRT using FP16 and INT8 engine profiles.
- Tail latencies are measured across 10,000 continuous streaming frames, extracting P50, P90, and P99 latency percentiles.
- Active SoC and board power are captured in real-time via hardware INA3221 shunt sensors using `tegrastats`.

---

## 2.4 Executable Experiment: Jetson Orin Profiler

Under [`chapter02/`](../chapter02/), `exp_02_jetson_orin_profiler.py` provides a formal profiling analyzer computing Real-Time Factor (RTF), Joules per audio frame, and energy efficiency metrics.
