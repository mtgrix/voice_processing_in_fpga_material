# Authoritative Sources & Literature Matrix — Voice Edge AI

This document catalogs the authoritative literature, technical specifications, and academic standards underpinning the monograph and research paper.

Every entry links to a unique source ID registered in [`docs/source_index.json`](source_index.json).

---

## 1. Edge GPU & NVIDIA Jetson Orin Architecture

| ID | Reference | Type | Core Concept / Hardware Metric |
|:---:|---|:---:|---|
| **R01-01** | NVIDIA Corp., *Jetson AGX Orin Architecture Whitepaper*, 2022. | Whitepaper | Ampere architecture, 3rd Gen Tensor Cores, DLA 2.0, unified LPDDR5, power profiles (7W–60W). |

---

## 2. FPGA Architecture & Edge Acceleration Frameworks

| ID | Reference | Type | Core Concept / Hardware Metric |
|:---:|---|:---:|---|
| **R01-02** | Umuroglu et al., *FINN: A Framework for Fast, Scalable Binarized Neural Network Inference on FPGAs*, ACM FPGA 2017. | Conference | Streaming dataflow architecture, custom precision (1-bit to 8-bit), Initiation Interval ($II=1$), on-chip BRAM FIFO buffers. |
| **R01-04** | AMD Xilinx, *Kria KV260 Vision AI Starter Kit User Guide*, UG1089, 2023. | User Guide | Zynq UltraScale+ MPSoC (XCZU5EV), quad ARM Cortex-A53, dual Cortex-R5F, 256K LUTs, 1.2K DSP slices, AXI HP/HPC ports. |

---

## 3. Voice Models & Acoustic Representations

| ID | Reference | Type | Core Concept / Hardware Metric |
|:---:|---|:---:|---|
| **R01-03** | Gulati et al., *Conformer: Convolution-augmented Transformer for Speech Recognition*, Interspeech 2020. | Conference | Combination of multi-head self-attention and depthwise separable convolutions for acoustic modeling; $O(T^2)$ computational complexity. |
| **R01-05** | Majumdar et al., *MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network for Speech Command Recognition*, Interspeech 2020. | Conference | Ultra-compact keyword spotting model; high accuracy with small parameter count ($<100\text{k}$ parameters), ideal for FPGA on-chip SRAM residency. |
