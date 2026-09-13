# Keyword Spotting on the Board: From Microphone to Decision

> **Scope note (Issue #29).** This chapter now carries the keyword-spotting end-to-end build from `plan-v2.md` section 7. The section stubs below were written for the earlier mapping, where chapter 8 held shared model primitives. They are not wrong, and they are not yet in the right order. The prose pass will re-cut them; `book/TOC.md` holds both readings until it does.


> *Objective: Architect custom hardware circuits for non-standard neural primitives: Depthwise Separable Convolutions, Multi-Head Self-Attention, and non-linear approximations.*

---

## 8.1 Hardware Challenges in Modern Acoustic Architectures
## 8.2 Pipelined 1D Depthwise Separable Convolutions on FPGA
## 8.3 Streaming Chunk-Level Self-Attention Engines
## 8.4 Hardware Approximations for Non-Linearities: Base-2 Softmax and LayerNorm
