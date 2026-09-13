# The Streaming Bottleneck: Why Batch=1 Stalls a GPU

> *Objective: Analyze the root architectural causes behind GPU power inefficiency, memory bandwidth saturation, and latency jitter under continuous streaming audio.*

---

## 3.1 The Mismatch Between Streaming Audio and SIMT Architecture
## 3.2 Kernel Launch Overheads, Preemption, and Tail Jitter
## 3.3 Roofline Analysis: Why Voice at Batch=1 is Memory-Bound
## 3.4 Motivation for Spatial Hardware Computing on FPGAs
