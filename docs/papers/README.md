# Primary Source Literature Archive (`docs/papers/`)

This directory stores the official, full-text open-access PDF manuscripts of foundational State of the Art (SOTA) research papers cited throughout the monograph.

---

## Catalog of Downloaded Papers

### 1. Dataflow Taxonomy & Energy Bounds (MIT)
- **Filename**: [`Sze2017_Efficient_Processing_of_DNNs.pdf`](./Sze2017_Efficient_Processing_of_DNNs.pdf)
- **Title**: *Efficient Processing of Deep Neural Networks: A Tutorial and Survey*
- **Authors**: Vivienne Sze, Yu-Hsin Chen, Tien-Ju Yang, Joel S. Emer
- **Venue**: *Proceedings of the IEEE*, 2017
- **DOI**: `10.1109/JPROC.2017.2761740` (arXiv: `1703.09039`)
- **Key Concepts**: Weight-Stationary vs. Input-Stationary vs. Output-Stationary; DRAM energy penalty (~200x vs ALU).

---

### 2. Integer-Only Non-Linear Quantization (UC Berkeley)
- **Filename**: [`Kim2021_IBERT_Integer_Only_Quantization.pdf`](./Kim2021_IBERT_Integer_Only_Quantization.pdf)
- **Title**: *I-BERT: Numerical-Friendly Integer-Only BERT Quantization*
- **Authors**: Sehoon Kim, Amir Gholami, Zhewei Yao, Michael W. Mahoney, Kurt Keutzer
- **Venue**: *ICML 2021* (arXiv: `2101.01321`, PMLR v139 `kim21d`, pp. 5506–5518)
- **⚠️ Misbound PDF**: the archived file at the filename above is **not** this paper. It is
  *Constant-Round Private Function Evaluation with Linear Complexity* (arXiv: `2101.01304`, secret
  sharing). The correct full text is not archived here; fetch it from `https://arxiv.org/abs/2101.01321`
  or the PMLR page before citing the paper from this directory.
- **Key Concepts**: Base-2 Exponential Softmax ($e^x = 2^{x \log_2 e}$); bit-shift and second-order polynomial approximation.

---

### 3. Canonical Conformer Architecture (Google)
- **Filename**: [`Gulati2020_Conformer_Speech_Recognition.pdf`](./Gulati2020_Conformer_Speech_Recognition.pdf)
- **Title**: *Conformer: Convolution-augmented Transformer for Speech Recognition*
- **Authors**: Anmol Gulati, James Qin, Chiu-chiu Chiu, Niki Parmar, et al.
- **Venue**: *Interspeech 2020* (arXiv: `2005.08100`)
- **DOI**: `10.21437/Interspeech.2020-3015`
- **Key Concepts**: Macaron-style FFN + MHSA + Depthwise Convolution block definitions.

---

### 4. 1D Time-Channel Separable CNN for Edge KWS (NVIDIA)
- **Filename**: [`Kriman2020_MatchboxNet.pdf`](./Kriman2020_MatchboxNet.pdf)
- **Title**: *MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network Architecture for Speech Commands Recognition*
- **Authors**: Samuel Kriman, Stanislav Beliaev, Boris Ginsburg, et al.
- **Venue**: *Interspeech 2020* (arXiv: `2004.08531`)
- **Key Concepts**: Sub-100k parameter acoustic model, 1D depthwise separable convolution, on-chip weight residency.

---

### 5. Streaming Dataflow Acceleration on FPGA (AMD/Xilinx Research)
- **Filename**: [`Umuroglu2017_FINN_FPGA_Dataflow.pdf`](./Umuroglu2017_FINN_FPGA_Dataflow.pdf)
- **Title**: *FINN: A Framework for Fast, Scalable Binarized Neural Network Inference on FPGAs*
- **Authors**: Yaman Umuroglu, Nicholas J. Fraser, Giulio Gambardella, Michaela Blott, et al.
- **Venue**: *ACM FPGA 2017* (arXiv: `1612.07119`)
- **DOI**: `10.1145/3020078.3021744`
- **Key Concepts**: Spatial dataflow, AXI-Stream FIFO sizing, initiation interval ($II=1$), on-chip weights.

---

*Note: ConfASR (Wabnitz et al., ASP-DAC 2026, RWTH Aachen) is indexed via its primary record in `docs/research_notes/R04_sota_speech_hardware_acceleration.md` (DOI: `10.18154/RWTH-2026-01243`).*
