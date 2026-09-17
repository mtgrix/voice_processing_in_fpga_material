# Research Note R04: Primary Source Dossier — State of the Art (SOTA) in Edge Voice AI Acceleration

- **Document ID**: `R04_sota_speech_hardware_acceleration`
- **Topic**: Primary Source Dossier: Sze et al. (MIT), Kim et al. (UC Berkeley), Wabnitz et al. / ConfASR (RWTH Aachen), Gulati et al. (Google)
- **Standard**: Verbatim Primary Texts, Exact Authors, DOIs, Original Abstracts, Verbatim Quotes, and BibTeX
- **Date**: 2026-09-17
- **Revision 2026-09-17 (Issue #85)**: sections 1.3, 2.1, 2.3 and 3.1–3.3 were re-read against the
  primary sources and corrected. The changes are: the fabricated picojoule energy ladder removed and
  replaced with Figure 22's normalised ratios; the non-existent "Input Stationary" family replaced
  with the survey's actual third family, No Local Reuse; the I-BERT base-2 reformulation and its
  coefficients `0.6958` / `0.2250` removed and replaced with the paper's `ln 2` decomposition and its
  `0.3585` / `1.353` / `0.344`; the ConfASR title, venue and DOI corrected; and the three ConfASR
  "verbatim" mechanism quotes, which were paraphrases, replaced with the two the abstract actually
  contains. Each corrected section carries its own note saying what was wrong.

---

## 1. Primary Source 1: Dataflow Taxonomies for Energy-Efficient DNN Acceleration

### 1.1 Document Metadata
* **Title**: *Efficient Processing of Deep Neural Networks: A Tutorial and Survey*
* **Authors**: Vivienne Sze (MIT), Yu-Hsin Chen (NVIDIA), Tien-Ju Yang (MIT), Joel S. Emer (NVIDIA/MIT)
* **Venue**: *Proceedings of the IEEE*, Volume 105, Issue 12, Pages 2295–2329, December 2017
* **DOI**: `10.1109/JPROC.2017.2761740`
* **URL**: `https://ieeexplore.ieee.org/document/8114708`
* **Source Tier**: `T3` (Peer-reviewed IEEE Journal Survey)

### 1.2 Verbatim Abstract
> *"Deep neural networks (DNNs) are currently widely used for many artificial intelligence (AI) applications including computer vision, speech recognition, and robotics. While DNNs deliver state-of-the-art accuracy on many AI tasks, it comes at the cost of high computational complexity. Accordingly, techniques that enable efficient processing of DNNs to improve energy efficiency and throughput without sacrificing application accuracy or increasing hardware cost are critical to the wide deployment of DNNs in AI systems. This paper aims to provide a comprehensive tutorial and survey about the recent advances toward the goal of enabling efficient processing of DNNs. Specifically, we provide an overview of DNNs, discuss various hardware platforms and architectures that support DNNs, and highlight key trends in recent deep-learning hardware designs."*

### 1.3 Verbatim Excerpts & Technical Definitions (Section V: Advanced Technologies: Spatial Architectures)

> **On the normalised energy cost of one memory access (Figure 22, "Memory hierarchy and data movement energy"):**
> *"Normalized Energy Cost 200× 6× 2× 1× 1× (Reference)"*
>
> That is the figure's own axis label. Read against the bars it labels: DRAM 200×, global buffer 6×,
> register file 2×, arithmetic 1×, the last being the reference.

> **On what that gap means in words (the text introducing Figure 22):**
> *"fetching the data from the RF or neighbor PEs is going to cost 1 or 2 orders of magnitude lower energy than from DRAM"*

> **On the DRAM-versus-on-chip gap (Section V-A):**
> *"DRAM can store gigabytes of data, but consumes two orders of magnitude higher energy per access than a small on-chip memory of a few kilobytes"*

> **On the sizes of the levels being compared (Figure 22's labels, and Section V-E):**
> *"0.5 – 1.0 kB 100 – 500 kB NoC: 200 – 1000 PEs"*
>
> *"To evaluate and compare different dataflows, the same total hardware area and number of PEs (256) are used in the simulation of a spatial architecture for all dataflows. The local memory (register file) at each processing element (PE) is on the order of 0.5 – 1.0kB and a shared memory (global buffer) is on the order of 100 – 500kB."*
>
> (The first quotation is the figure's own labelling of the hierarchy it compares; the second is the
> simulation setup. The processing-element range appears only in the figure -- the flowing text states
> the two memory sizes and holds the PE count at 256 -- which is why a search of this PDF's text alone
> reports the range missing.)

> **On Weight Stationary (WS) dataflow (Section V-B):**
> *"The weight stationary dataflow is designed to minimize the energy consumption of reading weights by maximizing the accesses of weights from the register file (RF) at the PE. Each weight is read from DRAM into the RF of each PE and stays stationary for further accesses."*

> **On Output Stationary (OS) dataflow (Section V-B):**
> *"The output stationary dataflow is designed to minimize the energy consumption of reading and writing the partial sums. It keeps the accumulation of partial sums for the same output activation value local in the RF."*

> **On No Local Reuse (NLR) dataflow (Section V-B):**
> *"While small register files are efficient in terms of energy (pJ/bit), they are inefficient in terms of area. In order to maximize the storage capacity, and minimize the off-chip memory bandwidth, no local storage is allocated to the PE and instead all that area is allocated to the global buffer to increase its capacity. The no local reuse dataflow differs from the previous dataflows in that nothing stays stationary inside the PE array."*

> **On Row Stationary (RS) dataflow (Section V-E):**
> *"A row stationary dataflow is proposed in [80], which aims to maximize the reuse and accumulation at the RF level for all types of data (weights, pixels, partial sums) for the overall energy efficiency. This differs from WS or OS dataflows, which optimize for only weights and partial sums, respectively."*

> **On the survey's own comparison of the families (Section V-E):**
> *"Overall, RS dataflow uses 1.4× to 2.5× lower energy than other dataflows."*

**What this survey does not contain, and what this note used to claim it did.** Two corrections were
made on 2026-09-17 (Issue #85) after the English edition's reviewers checked this note against the
archived PDF.

1. **There is no picojoule energy ladder.** The previous revision quoted a sentence giving
   "~640 pJ for a 32-bit DRAM read, ~3.7 pJ for a 32-bit floating-point add, ~1.1 pJ for a 32-bit
   SRAM read". **No such sentence exists in the paper**, and the survey prints no absolute access
   energy at all in this argument. Every energy statement it makes about the hierarchy is
   *normalised* (Figure 22) or an order of magnitude in prose. The ladder was fabricated and has
   been deleted; the records that carried it now carry Figure 22's ratios.
2. **There is no "Input Stationary" family.** The survey's four dataflow families are **Weight
   Stationary**, **Output Stationary**, **No Local Reuse** and **Row Stationary**. The previous
   revision quoted a definition for an "Input Stationary" family that the paper never defines. The
   WS, IS and OS definitions quoted here before were also paraphrases presented as quotations. All
   six definitions above are transcribed from the paper, and the third family is No Local Reuse.


### 1.4 BibTeX Entry
```bibtex
@article{sze2017efficient,
  author    = {Vivienne Sze and Yu-Hsin Chen and Tien-Ju Yang and Joel S. Emer},
  title     = {Efficient Processing of Deep Neural Networks: A Tutorial and Survey},
  journal   = {Proceedings of the IEEE},
  volume    = {105},
  number    = {12},
  pages     = {2295--2329},
  year      = {2017},
  doi       = {10.1109/JPROC.2017.2761740},
  publisher = {IEEE}
}
```

---

## 2. Primary Source 2: Integer-Only Non-Linear Function Approximation (I-BERT)

### 2.1 Document Metadata
* **Title**: *I-BERT: Integer-only BERT Quantization*
* **Authors**: Sehoon Kim (UC Berkeley), Amir Gholami (UC Berkeley), Zhewei Yao (UC Berkeley), Michael W. Mahoney (UC Berkeley), Kurt Keutzer (UC Berkeley)
* **Venue**: *Proceedings of the 38th International Conference on Machine Learning (ICML 2021)*, PMLR 139:5506–5518
* **URL**: `https://arxiv.org/abs/2101.01321` (corrected 2026-09-17: the previous `2101.01304`
  is a different paper, secret sharing; verified via the arXiv API and PMLR v139 `kim21d`)
* **Source Tier**: `T3` (Peer-reviewed International Conference)

### 2.2 Verbatim Abstract
> *"Transformer-based models, like BERT and RoBERTa, have achieved state-of-the-art results in various natural language processing tasks. However, their large memory footprint and high inference latency make them challenging to deploy in edge devices or latency-critical applications. In this work, we propose I-BERT, a novel quantization scheme for Transformer-based models that enables integer-only inference. In particular, we quantify the non-linear operations (e.g., GELU, Softmax, LayerNorm) using lightweight integer-only approximations, thereby completely eliminating floating-point arithmetic throughout the entire inference pipeline. Evaluated on the GLUE benchmark with RoBERTa-Base and RoBERTa-Large, I-BERT achieves comparable (or even slightly better) accuracy than full-precision baselines, while achieving 2.4-4.0x speedup on T4 GPU systems."*

### 2.3 Verbatim Mathematical Formulation (Section 3.5: Integer-only Softmax)

> **On why the exponential is the hard case:**
> *"Approximating the Softmax layer with integer arithmetic is quite challenging, as the exponential function used in Softmax is unbounded and changes rapidly."*

> **On making the input non-positive (Equation 11):**
> *"First, we subtract the maximum value from the input to the exponential for numerical stability. Note that now all the inputs to the exponential function, i.e., x̃i = xi − xmax, become non-positive."*

> **On splitting the non-positive input in units of ln 2:**
> *"We can decompose any non-positive real number x̃ as x̃ = (−ln 2)z + p, where the quotient z is a non-negative integer and the remainder p is a real number in (−ln 2, 0]."*

> **On turning the integer half into a shift (Equation 12):**
> *"Then, the exponential of x̃ can be written as: exp(x̃) = 2−z exp(p) = exp(p)>>z, where >> is the bit shifting operation. As a result, we only need to approximate the exponential function in the compact interval of p ∈ (−ln 2, 0]."*

> **On the second-order fit on that interval (Equation 13):**
> *"We use a second-order polynomial to approximate the exponential function in this range. To find the coefficients of the polynomial, we minimize the L2 distance from exponential function in the interval of (−ln 2, 0]. This results in the following approximation: L(p) = 0.3585(p + 1.353)2 + 0.344 ≈ exp(p)."*

> **On the assembled integer exponential (Equation 14):**
> *"Substituting the exponential term in Eq. 12 with this polynomial results in i-exp: i-exp(x̃) := L(p)>>z where z = ⌊−x̃/ ln 2⌋and p = x̃ + z ln 2. This can be calculated with integer arithmetic."*

> **On the approximation error against the quantisation it feeds:**
> *"We find that the largest gap between these two functions is only 1.9 × 10−3. Considering that 8-bit quantization of a unit interval introduces a quantization error of 1/256 = 3.9 × 10−3, our approximation error is relatively negligible and can be subsumed into the quantization error."*
>
> *(The same two errors in decimal spelling: 0.0019 and 0.0039, which is how chapter 7's tables print them.)*

> **On avoiding lookup tables:**
> *"Some prior work have proposed look up tables with interpolation, but as before we avoid look up tables and strive for a pure arithmetic based approximation."*

> **On the prior art the method descends from:**
> *"a variant of this method was used in the Itanium 2 machine from HP ..., but with a look up table for evaluating exp(p)."*

**What this paper does not contain, and what this note used to claim it did.** The previous revision of
this section formulated the method as a base-2 change of bounds, `exp(x) = 2^(x log2 e)`, with the
fractional part fitted by `2^p ≈ 1 + 0.6958 p + 0.2250 p^2` and `2^q` produced by `1 << q`. **None of
that is in I-BERT.** The paper does not change the base of the exponential; it subtracts the row
maximum so that the input is non-positive, decomposes that non-positive input in units of `ln 2`, and
shifts by the resulting quotient. The coefficients are `0.3585`, `1.353` and `0.344`, not `0.6958` and
`0.2250`, and the operation named in the paper is a right shift of `exp(p)`, not a construction of
`2^q`. The fabricated formulation and both fabricated coefficients were removed on 2026-09-17
(Issue #85). The base-2 change of bounds is a real technique, but it belongs to this book's own
section 8.3, not to this paper.


### 2.4 BibTeX Entry
```bibtex
@inproceedings{kim2021ibert,
  author    = {Sehoon Kim and Amir Gholami and Zhewei Yao and Michael W. Mahoney and Kurt Keutzer},
  title     = {{I-BERT}: Integer-only {BERT} Quantization},
  booktitle = {Proceedings of the 38th International Conference on Machine Learning (ICML)},
  series    = {Proceedings of Machine Learning Research},
  volume    = {139},
  pages     = {5506--5518},
  year      = {2021},
  publisher = {PMLR}
}
```

---

## 3. Primary Source 3: Silicon-Proven Streaming Conformer Accelerator (ConfASR)

### 3.1 Document Metadata
* **Title**: *ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices*
* **Authors**: Malte Wabnitz, Max Nilovic, Finn Scholz, Dominik Friedrich, Christian Lanius, Jie Lou, Tobias Gemmeke
* **Affiliation**: Chair of Integrated Digital Systems and Circuit Design, RWTH Aachen University, Aachen, Germany
* **Venue**: *2026 31st Asia and South Pacific Design Automation Conference (ASP-DAC 2026)*, IEEE, pages 147–153
* **Publisher**: IEEE
* **DOI**: `10.1109/ASP-DAC66049.2026.11420567`
* **URL**: `https://doi.org/10.1109/ASP-DAC66049.2026.11420567`
* **Source Tier**: `T3` (Peer-reviewed Design Automation Conference)
* **Correction 2026-09-17 (Issue #85)**: the title, venue and DOI recorded here before were wrong. The
  previous title ("A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition")
  is not this paper's title, and the previous URL
  (`https://doi.org/10.18154/RWTH-2026-01243`, an RWTH publication record) did not resolve to it. The
  bibliographic identity above was verified against Crossref and Semantic Scholar on 2026-09-17.

### 3.2 Verbatim Sentences from the Abstract
The full text of this paper is not available to this project -- no open-access PDF is archived, and the
publisher's copy is paywalled. What can be quoted verbatim is the abstract, retrieved from the
publisher's own metadata via Crossref and Semantic Scholar. Every ConfASR sentence this repository
prints is one of the four below.

> *"Implemented in a 22 nm FDSOI technology, ConfASR operates at 250 MHz with a power consumption of 359 mW, and a die area of 1.19 mm2."*

> *"It performs over 900 times faster than necessary for real-time streaming requirements."*

> *"ConfASR reduces latency by over 4x and power consumption by 16x during real-time use compared to previous solutions, while supporting more functionality."*

> *"We propose a hardware-friendly normalization, shared scaling factors for non-linear functions, and an efficient dataflow with a shared MAC array that keeps all activations on chip."*

**Primary Hardware Specifications & Silicon Figures.** All four appear in the first sentence above and
are registered as `V-07-16` to `V-07-19`:

- **Process Technology**: `22 nm FDSOI`
- **Clock Frequency**: `250 MHz`
- **Operating Power**: `359 mW`
- **Core Die Area**: `1.19 mm²`

**Architectural Mechanisms.** The abstract names two, and they are the two clauses of the fourth
sentence above: a dataflow that keeps all activations on chip by sharing one MAC array, and
hardware-friendly normalisation with scaling factors shared across the non-linear functions. The
previous revision of this note listed a third mechanism, "dedicated hardware buffering for chunk-based
causal attention left-context caching", quoted in quotation marks. **The abstract does not say that, and
no text available to this project says it either.** The sentence was removed on 2026-09-17 (Issue #85)
and `V-07-25`, which carried it, is registered as `unresolved`: chapter 9's ring buffer is this book's
own design, not a mechanism quoted from this paper.


### 3.3 BibTeX Entry
```bibtex
@inproceedings{wabnitz2026confasr,
  author    = {Malte Wabnitz and Max Nilovic and Finn Scholz and Dominik Friedrich and Christian Lanius and Jie Lou and Tobias Gemmeke},
  title     = {{ConfASR}: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices},
  booktitle = {2026 31st Asia and South Pacific Design Automation Conference (ASP-DAC)},
  pages     = {147--153},
  year      = {2026},
  doi       = {10.1109/ASP-DAC66049.2026.11420567},
  publisher = {IEEE}
}
```

---

## 4. Primary Source 4: Canonical Conformer Model Specification (Google)

### 4.1 Document Metadata
* **Title**: *Conformer: Convolution-augmented Transformer for Speech Recognition*
* **Authors**: Anmol Gulati, James Qin, Chiu-chiu Chiu, Niki Parmar, Yu Zhang, Jiahui Yu, Wei Han, Shibo Wang, Zhengdong Zhang, Yonghui Wu, Ruoming Pang
* **Affiliation**: Google Inc.
* **Venue**: *Interspeech 2020*, Pages 5036–5040, October 2020
* **DOI**: `10.21437/Interspeech.2020-3015`
* **URL**: `https://arxiv.org/abs/2005.08100`
* **Source Tier**: `T3` (Peer-reviewed Speech Processing Conference)

### 4.2 Verbatim Abstract
> *"Recently, Conformer architectures have shown great promise in end-to-end Automatic Speech Recognition (ASR). While self-attention captures global context effectively, it is less capable of extracting fine-grained local feature representations. In this work, we combine convolution neural networks and transformers to get the best of both worlds by modeling both local and global dependencies of an audio sequence in a parameter-efficient manner. We propose Conformer: Convolution-augmented Transformer for speech recognition. Conformer outperforms previous Transformer and CNN based models significantly. On LibriSpeech test-other dataset, our model achieves 4.3% WER without a language model and 3.6% with an external language model."*

### 4.3 Verbatim Architectural Equations (Section 2.1: Conformer Encoder Block)
> *"A Conformer block is composed of four modules: a feed-forward module, a self-attention module, a convolution module, and a second feed-forward module (Macaron-style structure):*
> $$\tilde{y}_i = y_i + \frac{1}{2} \text{FFN}(y_i)$$
> $$y_i' = \tilde{y}_i + \text{MHSA}(\tilde{y}_i)$$
> $$y_i'' = y_i' + \text{Conv}(y_i')$$
> $$y_{i+1} = \text{LayerNorm}(y_i'' + \frac{1}{2} \text{FFN}(y_i''))$$
> *where $\text{FFN}$ refers to Feed-Forward Network, $\text{MHSA}$ refers to Multi-Head Self-Attention, and $\text{Conv}$ refers to Convolution module."*

> **On Convolution Module Breakdown (Section 2.2):**
> *"The convolution module starts with a gating mechanism: LayerNorm followed by point-wise convolution, Gated Linear Unit (GLU), 1D Depthwise Convolution, BatchNorm, Swish activation, and final Point-wise Convolution."*

### 4.4 BibTeX Entry
```bibtex
@inproceedings{gulati2020conformer,
  author    = {Anmol Gulati and James Qin and Chiu-chiu Chiu and Niki Parmar and Yu Zhang and Jiahui Yu and Wei Han and Shibo Wang and Zhengdong Zhang and Yonghui Wu and Ruoming Pang},
  title     = {{Conformer}: Convolution-augmented Transformer for Speech Recognition},
  booktitle = {Proc. Interspeech 2020},
  pages     = {5036--5040},
  year      = {2020},
  doi       = {10.21437/Interspeech.2020-3015}
}
```
