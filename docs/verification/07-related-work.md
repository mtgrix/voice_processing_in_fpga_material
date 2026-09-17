# Verification Records: 07 Related Work

### V-07-01 · V-07-01

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `` |
| value | `Williams, Waterman, Patterson, CACM April 2009` |
| unit | `citation` |
| conditions | `Communications of the ACM, Vol. 52, No. 4, pp. 65-76, DOI: 10.1145/1498765.1498785` |
| source_tier | `T3` |
| doc_id | `CACM April 2009` |
| title | Roofline: An Insightful Visual Performance Model for Multicore Architectures |
| url | https://dl.acm.org/doi/10.1145/1498765.1498785 |
| locator | p.65-76; p.2 in preprint |
| quote | Note that the ridge point, where the diagonal and horizontal roofs meet, offers interesting insight into the computer. The x-coordinate of the ridge point is the minimum operational intensity required to achieve peak performance. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://users.cs.duke.edu/~lkw34/papers/roofline-cacm2008.pdf |
| notes | Defines arithmetic/operational intensity (FLOP/byte or OP/byte) and memory vs compute bound regimes. |

### V-07-02 · Jetson Orin Ridge Point

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `jetson_orin_ridge_point` |
| value | `490.2 (Dense INT8) / 980.4 (Sparse INT8)` |
| unit | `OP/byte` |
| conditions | `Jetson Orin NX 16GB at the MAXN profile: 50 TOPS dense / 100 TOPS sparse, 102 GB/s memory bandwidth` |
| source_tier | `T2` |
| doc_id | `Derived from DS-10712-001_v1.7 (V-02-16, V-02-18)` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | Arithmetic derivation: 50,000 GOP/s / 102 GB/s = 490.2 OP/byte; 100,000 GOP/s / 102 GB/s = 980.4 OP/byte |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. ... Jetson Orin NX (ONX)16GB \| Number of Operations (up to) \| Sparse \| 100 INT8 TOPs \| 157 INT8 TOPs \| Dense \| 50 INT8 TOPs \| 78 INT8 TOPs |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Very high ridge point means edge GPU is heavily memory bandwidth bound for streaming batch=1 speech processing with low arithmetic intensity. Recomputed 2026-09-12 using the 102 GB/s the datasheet actually prints, replacing 102.4. Previous values 488.3 / 976.6 are superseded; the conclusion (Orin is heavily bandwidth-bound for batch=1 streaming speech) is unchanged. TIER CORRECTED 2026-09-12: was T1. The value is arithmetic on printed figures and is never printed itself, so it is tiered T2 like V-02-36, V-04-09 and V-04-12. Tier describes the evidence, not the quality of the source it was derived from. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Recomputed 2026-09-12 against the vendor v1.7 copy; 490.2 and 980.4 are unchanged because the inputs print in v1.7 as in v1.0. The MAXN_SUPER operating point moves the ridge point, which is C-07. |

### V-07-03 · Kria Kv260 Fpga Ridge Point

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kria_kv260_fpga_ridge_point` |
| value | `39.0 - 78.0` |
| unit | `OP/byte` |
| conditions | `KV260 (1248 DSP48E2 @ 300 MHz): 748.8 GOP/s (1 MAC/DSP) or 1497.6 GOP/s (packed INT8), 19.2 GB/s DDR4` |
| source_tier | `T2` |
| doc_id | `Derived from DS890 (V-01-09) and DS987 (V-01-13)` |
| title | UltraScale Architecture Overview & Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | Arithmetic derivation: 748.8 GOP/s / 19.2 GB/s = 39.0 OP/byte; 1497.6 / 19.2 = 78.0 |
| quote | DSP Slices: 1,248 ... 4 GB 64-bit wide, 2400 Mb/s memory |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Ridge point is 6.2x to 12.5x lower than Orin NX, illustrating FPGA's advantage in streaming low-arithmetic-intensity workloads. TIER CORRECTED 2026-09-12: was T1. The value is arithmetic on printed figures and is never printed itself, so it is tiered T2 like V-02-36, V-04-09 and V-04-12. Tier describes the evidence, not the quality of the source it was derived from. CLOCK ASSUMPTION, recorded 2026-09-13 (Issue #16): the 300 MHz in conditions is a design assumption with no source record in this directory. An achievable fabric clock is not a datasheet figure -- it is whatever a specific synthesized design closes at on a specific part at a specific voltage -- so it cannot be fetched. V-01-10 establishes only that XCK26-SFVC784-2LV is a -2 speed grade at VCCINT = 0.72 V, which bounds the question rather than answering it. Every other input is traceable: 1,248 DSP slices from V-01-09, 19.2 GB/s from V-01-13, and the 1 MAC = 2 OP convention is the same one V-07-02 uses, so the two ridge points stay comparable. The result is proportional to the clock: at 500 MHz the pair becomes 65.0 and 130.0 OP/byte, narrowing the gap to Orin's 490.2 from 12.6x to 7.5x. The value and conditions above stand unchanged; this note is the honesty layer, and its effect is to mark the FPGA side of the comparison as a projection while the Orin side is a printed peak. Do not replace 300 MHz with a vendor "up to" frequency from a blog or an overview page: under protocol rule 2 such a page is corroborating at best, and under rule 1 it would launder an assumption into a sourced figure. The only other 300 MHz in this directory's evidence is a third-party DPU clock cited under V-04-13 (README Unresolved Items 1), tier T5, corroborating only, and the clock of a different block; it is not a source for this assumption and must not be used to close it. |

### V-07-04 · Fccm Artifact Evaluation Badging Policy

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `fccm_artifact_evaluation_badging_policy` |
| value | `Code/Dataset Available, Evaluated (Functional), Reproducible` |
| unit | `IEEE badges` |
| conditions | `IEEE FCCM 2025 Artifact Evaluation Guidelines` |
| source_tier | `T2` |
| doc_id | `FCCM 2025 Artifact Evaluation Guidelines` |
| title | Artifact Evaluation 2025 - The 33rd IEEE International Symposium on Field-Programmable Custom Computing Machines |
| url | https://www.fccm.org/artifact-evaluation-2025/ |
| locator | Sections 'ARTIFACT REVIEW BADGES' and 'FAQ' |
| quote | The artifact evaluation process for FCCM 2025 will consider awarding the following IEEE reproducibility badges: Code/Dataset Available, Code/Dataset Evaluated (Functional), Code/Dataset Reproducible. ... Q: Does the artifact submission link need to be anonymous? A: No, it should not be anonymous and thus should not be included in the submitted paper. Any information about the artifacts should only be submitted via the Artifact Evaluation form. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Artifacts evaluated only post-acceptance; non-anonymous repository link submitted through dedicated form. |

### V-07-05 · Published Fpga Kws Comparative Table

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `published_fpga_kws_comparative_table` |
| value | `` |
| unit | `table` |
| conditions | `Published FPGA KWS accelerators (latency, power, energy/frame, LUT/DSP)` |
| source_tier | `T3` |
| doc_id | `n/a` |
| title | n/a |
| url |  |
| locator | plan-v2.md §5.5 |
| quote |  |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Search deferred: pending comprehensive survey of MLPerf Tiny / IEEE FPT / FCCM literature for standardized comparative baselines across identical Speech Commands test split. |

### V-07-06 · Sze Memory Hierarchy Normalized Energy

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `sze_memory_hierarchy_normalized_energy` |
| value | `200 / 6 / 2 / 1` |
| unit | `multiplier` |
| conditions | `Sze et al. Fig. 22 'Memory hierarchy and data movement energy': the normalised cost of one access at each level of the hierarchy, with the ALU as the 1x reference -- DRAM 200x, Global Buffer 6x, RF 2x` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | Figure 22, its axis label and the text introducing it; docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | Normalized Energy Cost 200× 6× 2× 1× 1× (Reference) [...] fetching the data from the RF or neighbor PEs is going to cost 1 or 2 orders of magnitude lower energy than from DRAM |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): this record carried 640 / 3.7 / 1.1 pJ, from a sentence that appears nowhere in the paper. The survey prints no absolute access energy at all: its Figure 22 is normalised to the ALU, and the only energy statements in the surrounding prose are order-of-magnitude ones. The pJ ladder was a fabrication of the previous pass. The quote now leads with Figure 22's own axis label, so the ratios in the value field are quoted rather than inferred. Chapter 3 teaches these as the ratios they are. |

### V-07-07 · Dram Vs Onchip Memory Energy Orders

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dram_vs_onchip_memory_energy_orders` |
| value | `two orders of magnitude` |
| unit | `multiplier` |
| conditions | `DRAM access against a small on-chip memory of a few kilobytes, as the survey's own prose states it. Figure 22 prints the same gap as the ratio 200x against the ALU, which is V-07-06's value; this record exists to keep the survey's wording, not to restate the ratio.` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | Section V-A, the text introducing Figure 22; docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | DRAM can store gigabytes of data, but consumes two orders of magnitude higher energy per access than a small on-chip memory of a few kilobytes |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the quote was replaced with a sentence the paper actually contains, and the value was corrected to match it. The previous value of 200 rested on Figure 22's ALU-normalised ratio, which this sentence does not print; V-07-06 carries that ratio from the figure itself. |

### V-07-08 · Weight Stationary Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `weight_stationary_dataflow` |
| value | `Weight-Stationary` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy, family 1 (Fig. 25(a))` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | The weight stationary dataflow is designed to minimize the energy consumption of reading weights by maximizing the accesses of weights from the register file (RF) at the PE. Each weight is read from DRAM into the RF of each PE and stays stationary for further accesses. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): quote replaced with the paper's own wording; the previous one was a paraphrase that read as a definition. |

### V-07-09 · No Local Reuse Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `no_local_reuse_dataflow` |
| value | `No-Local-Reuse (NLR)` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy, family 3 (Fig. 25(c))` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | While small register files are efficient in terms of energy (pJ/bit), they are inefficient in terms of area. In order to maximize the storage capacity, and minimize the off-chip memory bandwidth, no local storage is allocated to the PE and instead all that area is allocated to the global buffer to increase its capacity. The no local reuse dataflow differs from the previous dataflows in that nothing stays stationary inside the PE array. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the survey has no Input-Stationary family. This record was renamed from input_stationary_dataflow and now carries the third family the paper defines. Fig. 25 illustrates WS / OS / NLR; the fourth family, Row-Stationary, is V-07-28. |

### V-07-10 · Output Stationary Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `output_stationary_dataflow` |
| value | `Output-Stationary` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy, family 2 (Fig. 25(b))` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | The output stationary dataflow is designed to minimize the energy consumption of reading and writing the partial sums. It keeps the accumulation of partial sums for the same output activation value local in the RF. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): quote replaced with the paper's own wording; the previous one was a paraphrase. |

### V-07-11 · Softmax Max Subtraction And Ln2 Decomposition

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `softmax_max_subtraction_and_ln2_decomposition` |
| value | `x̃ = (−ln 2)z + p` |
| unit | `string` |
| conditions | `I-BERT Section 3.5: Eq. 11 subtracts the row maximum, then the non-positive remainder is decomposed in units of ln 2` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Approximating the Softmax layer with integer arithmetic is quite challenging, as the exponential function used in Softmax is unbounded and changes rapidly. [...] First, we subtract the maximum value from the input to the exponential for numerical stability. Note that now all the inputs to the exponential function, i.e., x̃i = xi − xmax, become non-positive. We can decompose any non-positive real number x̃ as x̃ = (−ln 2)z + p, where the quotient z is a non-negative integer and the remainder p is a real number in (−ln 2, 0]. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the previous record carried a change-of-base reformulation 'exp(x) = 2^(x * log2(e))' that appears nowhere in I-BERT. The paper's actual route subtracts the row maximum and decomposes the non-positive remainder in units of ln 2, which is what turns the exponent into a power of two. |

### V-07-12 · Exponential Shift Identity

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `exponential_shift_identity` |
| value | `exp(x̃) = 2^(−z) exp(p) = exp(p) >> z, with p confined to (−ln 2, 0]` |
| unit | `string` |
| conditions | `I-BERT Section 3.5, Eq. 12` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Then, the exponential of x̃ can be written as: exp(x̃) = 2−z exp(p) = exp(p)>>z, where >> is the bit shifting operation. As a result, we only need to approximate the exponential function in the compact interval of p ∈ (−ln 2, 0]. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): this record carried a floor-of-z split 'z = q + p' from the same fabricated formulation. The real identity shifts right by z, which is the exact part of the path; only exp(p) on (−ln 2, 0] is approximated. |

### V-07-13 · Polynomial Fit On Ln2 Interval

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `polynomial_fit_on_ln2_interval` |
| value | `L(p) = 0.3585(p + 1.353)^2 + 0.344` |
| unit | `string` |
| conditions | `I-BERT Section 3.5, Eq. 13: second-order polynomial fitted by L2 minimisation on (−ln 2, 0]` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | We use a second-order polynomial to approximate the exponential function in this range. To find the coefficients of the polynomial, we minimize the L2 distance from exponential function in the interval of (−ln 2, 0]. This results in the following approximation: L(p) = 0.3585(p + 1.353)2 + 0.344 ≈ exp(p). |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): this record carried the fabricated coefficients 0.6958 / 0.2250. The real ones are 0.3585, 1.353 and 0.344, and the polynomial is fitted on (−ln 2, 0] rather than on [0, 1). |

### V-07-14 · I Exp Definition

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `i_exp_definition` |
| value | `i-exp(x̃) := L(p) >> z, where z = ⌊−x̃/ln 2⌋ and p = x̃ + z ln 2` |
| unit | `string` |
| conditions | `I-BERT Section 3.5, Eq. 14, with z = ⌊−x̃/ln 2⌋ and p = x̃ + z ln 2` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Substituting the exponential term in Eq. 12 with this polynomial results in i-exp: i-exp(x̃) := L(p)>>z where z = ⌊−x̃/ ln 2⌋and p = x̃ + z ln 2. This can be calculated with integer arithmetic. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the coefficients this record used to carry were fabricated; they are now registered by V-07-13. The shift by z is what makes the whole layer integer-only. |

### V-07-15 · Integer Only Softmax No Lookup

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `integer_only_softmax_no_lookup` |
| value | `pure arithmetic based approximation, no look up tables` |
| unit | `string` |
| conditions | `I-BERT Section 3.5: the design constraint that rules out table-based exponentials` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Some prior work have proposed look up tables with interpolation, but as before we avoid look up tables and strive for a pure arithmetic based approximation. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the previous quote did not exist in the paper. The paper also names the contrast it is drawing: a variant of this method was used in the Itanium 2, but with a look up table for evaluating exp(p). |

### V-07-16 · Confasr Process Node

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_process_node` |
| value | `22` |
| unit | `nm` |
| conditions | `ConfASR silicon, ASP-DAC 2026, pp. 147-153 (22 nm FDSOI process)` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Implemented in a 22 nm FDSOI technology, ConfASR operates at 250 MHz with a power consumption of 359 mW, and a die area of 1.19 mm2. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. Silicon figure verified against the paper's abstract. |

### V-07-17 · Confasr Clock Frequency

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_clock_frequency` |
| value | `250` |
| unit | `MHz` |
| conditions | `ConfASR silicon, ASP-DAC 2026, pp. 147-153 (250 MHz clock)` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Implemented in a 22 nm FDSOI technology, ConfASR operates at 250 MHz with a power consumption of 359 mW, and a die area of 1.19 mm2. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-18 · Confasr Operating Power

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_operating_power` |
| value | `359` |
| unit | `mW` |
| conditions | `ConfASR silicon, ASP-DAC 2026, pp. 147-153 (359 mW power)` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Implemented in a 22 nm FDSOI technology, ConfASR operates at 250 MHz with a power consumption of 359 mW, and a die area of 1.19 mm2. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-19 · Confasr Core Die Area

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_core_die_area` |
| value | `1.19` |
| unit | `mm2` |
| conditions | `ConfASR silicon, ASP-DAC 2026, pp. 147-153 (1.19 mm2 die area)` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Implemented in a 22 nm FDSOI technology, ConfASR operates at 250 MHz with a power consumption of 359 mW, and a die area of 1.19 mm2. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-20 · Confasr Streaming Throughput

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_streaming_throughput` |
| value | `900` |
| unit | `multiplier` |
| conditions | `ConfASR streaming throughput vs the real-time requirement, ASP-DAC 2026, pp. 147-153` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | It performs over 900 times faster than necessary for real-time streaming requirements. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-21 · Confasr Latency Reduction

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_latency_reduction` |
| value | `4` |
| unit | `multiplier` |
| conditions | `ConfASR latency vs previous streaming ASR hardware, ASP-DAC 2026, pp. 147-153` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | ConfASR reduces latency by over 4x and power consumption by 16x during real-time use compared to previous solutions, while supporting more functionality. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-22 · Confasr Power Reduction

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_power_reduction` |
| value | `16` |
| unit | `multiplier` |
| conditions | `ConfASR power vs previous solutions in real-time use, ASP-DAC 2026, pp. 147-153` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | ConfASR reduces latency by over 4x and power consumption by 16x during real-time use compared to previous solutions, while supporting more functionality. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): title, DOI and quote replaced. |

### V-07-23 · Confasr Shared Mac Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_shared_mac_dataflow` |
| value | `shared MAC array keeping all activations on chip` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism, stated as one clause of the abstract's proposal` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | We propose a hardware-friendly normalization, shared scaling factors for non-linear functions, and an efficient dataflow with a shared MAC array that keeps all activations on chip. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): quote replaced with the abstract's own sentence, quoted in full so the reader sees the mechanism as one clause of a three-part proposal rather than as a standalone claim. The earlier paraphrase is not in the paper. |

### V-07-24 · Confasr Hw Normalization

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_hw_normalization` |
| value | `hardware-friendly normalization, shared scaling factors for non-linear functions` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism, stated as one clause of the abstract's proposal` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | We propose a hardware-friendly normalization, shared scaling factors for non-linear functions, and an efficient dataflow with a shared MAC array that keeps all activations on chip. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): quote replaced with the abstract's own sentence. |

### V-07-25 · Confasr Chunk Causal Buffering

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `confasr_chunk_causal_buffering` |
| value | `` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism 3 -- NOT VERIFIED. The abstract names only the dataflow, the normalisation and the shared scaling factors.` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge Devices |
| url | https://doi.org/10.1109/ASP-DAC66049.2026.11420567 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote |  |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-17 (Issue #85): the previous quote was a paraphrase, and the left-context caching mechanism it described does not appear in the paper's abstract at all. The full text sits behind IEEE's subscription wall and could not be retrieved, so this record is unresolved and chapter 9 no longer attributes a buffering mechanism to this paper. The book's own left-context ring buffer stands on its own derivation in section 9.4. The RWTH publication record cited earlier (10.18154/RWTH-2026-01243) does not exist; the registered DOI is 10.1109/ASP-DAC66049.2026.11420567. |

### V-07-26 · Sze Memory Hierarchy Sizes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `sze_memory_hierarchy_sizes` |
| value | `0.5 - 1.0 / 100 - 500 / 200 - 1000` |
| unit | `KB` |
| conditions | `Sze et al. Fig. 22 labels the memory hierarchy it compares: register file 0.5-1.0 kB per PE, global buffer 100-500 kB, NoC 200-1000 PEs. The simulation setup in Section V-E holds the total area and the PE count at 256 for all dataflows instead of using those ranges` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | Figure 22's own labels next to the levels they size, and Section V-E; docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | 0.5 – 1.0 kB 100 – 500 kB NoC: 200 – 1000 PEs [...] To evaluate and compare different dataflows, the same total hardware area and number of PEs (256) are used in the simulation of a spatial architecture for all dataflows. The local memory (register file) at each processing element (PE) is on the order of 0.5 – 1.0kB and a shared memory (global buffer) is on the order of 100 – 500kB. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | REPURPOSED 2026-09-17 (Issue #85): this record registered the 32-bit width of the pJ ladder, which does not exist in the paper, so the width is no longer registered. It now carries the hierarchy sizes Fig. 22 prints, which chapter 3 needs. The 200-1000 PE count in the value is the NoC size from the same figure. RE-READ LATER THE SAME DAY: the quote now leads with Figure 22's own labels, because a text-only extraction of this PDF reported the NoC count missing and this record was nearly re-filed as fabricated with it. The figure prints 'NoC: 200 - 1000 PEs' and the flowing text never repeats the range; this paper carries numbers in its figures that its sentences do not. The same sweep does confirm the ladder this record used to carry: the string '640' occurs zero times in the whole document, and 'pJ' occurs once, in the no-local-reuse definition, as a unit with no number attached to it. |

### V-07-27 · I Exp Approximation Error

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `i_exp_approximation_error` |
| value | `0.0019 / 0.0039 / 256` |
| unit | `multiplier` |
| conditions | `Largest gap between L(p) and exp(p) on (−ln 2, 0], expressed as a fraction of the unit interval, against the quantisation error 8 bits introduce on that interval; I-BERT Section 3.5` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3; the paper prints the two errors as 1.9 x 10-3 and 3.9 x 10-3, which chapter 7 prints as 0.0019 and 0.0039 |
| quote | We find that the largest gap between these two functions is only 1.9 × 10−3. Considering that 8-bit quantization of a unit interval introduces a quantization error of 1/256 = 3.9 × 10−3, our approximation error is relatively negligible and can be subsumed into the quantization error. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered 2026-09-17 (Issue #85). The previous chapter 7 text told the reader no record registered the polynomial's error; the paper does register it, and the approximation's worst case is smaller than the quantisation error it is compared against. |

### V-07-28 · Row Stationary Energy Comparison

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `row_stationary_energy_comparison` |
| value | `1.4 - 2.5` |
| unit | `multiplier` |
| conditions | `Row-Stationary vs the other dataflows, AlexNet CONV layers at batch 16, same total area and PE count; Sze et al. Section V-E` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | Section V-E; docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | Overall, RS dataflow uses 1.4× to 2.5× lower energy than other dataflows. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered 2026-09-17 (Issue #85) so chapter 3 can state the survey's own winner. The book's output-stationary lean is a workload argument for streaming batch one, not a claim that OS wins this evaluation. |

### V-07-29 · Row Stationary Definition

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `row_stationary_definition` |
| value | `the row stationary definition, and the survey's attribution of that design to an earlier work` |
| unit | `string` |
| conditions | `Sze et al. Section V-E, the definition of the fourth dataflow family` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | Section V-E; docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | A row stationary dataflow is proposed in [80], which aims to maximize the reuse and accumulation at the RF level for all types of data (weights, pixels, partial sums) for the overall energy efficiency. This differs from WS or OS dataflows, which optimize for only weights and partial sums, respectively. |
| retrieved_utc | `2026-09-17T09:30:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered 2026-09-17 (Issue #85) so that the fourth dataflow definition has a record of its own, as the three the survey's other families get in V-07-08 to V-07-10. The numeral inside the quotation is the survey's reference marker; chapter 3 elides it and names the work instead. That work is Eyeriss, a spatial architecture for energy-efficient dataflow (Chen, Emer and Sze, ISCA 2016), named on the survey's own reference list and not held by this repository, so the book names the design rather than citing a source it cannot hand the reader. |
