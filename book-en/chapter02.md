# Chapter 2: Jetson Orin Microarchitecture & Profiling Baseline

> *Objective: Dissect the NVIDIA Jetson Orin SoC architecture (Ampere GPU, Tensor Cores, LPDDR5, DLA) and establish rigorous baseline measurement protocols (TensorRT, tegrastats).*

---

> ### 📘 Minimal Mathematics / Prerequisites for this Chapter
> 
> - **Energy per Frame**: $E_{\text{frame}} = P_{\text{avg}} \times \Delta t_{\text{latency}}$ ($\text{Joules}$ or $\text{mJ}$).
> - **Real-Time Factor (RTF)**: $\text{RTF} = T_{\text{compute}} / T_{\text{audio}}$.
> - **Tail Latency (P99)**: 99th percentile processing latency across thousands of consecutive streaming frames.

---

## 2.1 Intuition: The Power and Paradox of NVIDIA Jetson Orin
<!-- High peak TOPS vs low compute efficiency under fine-grained streaming audio -->

## 2.2 SoC Architecture: ARM Cores, Ampere SM, and LPDDR5 Memory Subsystem
<!-- Hardware block diagram and SIMT warp scheduling limits -->

## 2.3 Benchmarking Methodology: TensorRT and Hardware Power Sensors
<!-- Compilation with TensorRT, INA3221 shunt reading via tegrastats -->

## 2.4 The Baseline Scorecard
<!-- Latency distribution, RTF, power, and energy consumption metrics -->

---

## Associated Experiment
- Refer to [`chapter02/`](../chapter02/).
