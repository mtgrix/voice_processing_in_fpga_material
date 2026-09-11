# Research Note R02: FPGA Streaming Dataflow for Continuous Audio Processing

- **Source ID**: `R01-02`, `R01-04`
- **Topic**: FPGA Spatial Computing, Initiation Interval ($II=1$), and Audio Streaming
- **Date**: 2026-09-11

---

## 1. Spatial Computing vs. Temporal Computing

Unlike CPUs and GPUs that execute instructions sequentially on fixed arithmetic logic units over time (**temporal execution**), FPGAs construct dedicated circuits tailored to the exact computational graph of the neural network (**spatial execution**):

- **Dataflow Pipelining**:
  Each layer of the neural network is instantiated as a distinct hardware stage connected via on-chip FIFO streams (e.g. AXI4-Stream).
- **Initiation Interval ($II$)**:
  The number of clock cycles between consecutive input data tokens. With $II=1$, the FPGA can accept a new audio sample or spectral frame every single clock cycle without waiting for downstream layers to finish.

---

## 2. On-Chip SRAM (BRAM/URAM) Residency

For small-to-medium voice models (e.g. Keyword Spotting like MatchboxNet or Speech Enhancement like RNNoise):
- Total model weight parameters can fit entirely within the on-chip SRAM (Block RAM and UltraRAM) of modern FPGAs (e.g., Kria KV260 has 144 BRAMs and 64 URAMs, providing ~4.5 MB on-chip memory).
- **Zero Off-Chip Memory Traffic**:
  When all weights reside in on-chip SRAM, inference eliminates DDR DRAM accesses entirely, drastically slashing dynamic power consumption from watts down to milliwatts.
