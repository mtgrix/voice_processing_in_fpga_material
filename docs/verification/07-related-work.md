# Verification Records: 07 Related Work

### V-07-01 · Roofline Model Primary Citation

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `roofline_model_primary_citation` |
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

### V-07-06 · Dram Vs Alu Energy

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dram_vs_alu_energy` |
| value | `640 / 3.7 / 1.1` |
| unit | `pJ` |
| conditions | `32-bit DRAM read, 32-bit floating-point add, 32-bit SRAM read; Sze et al. Table 1 / Section V-A` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | Memory accesses are significantly more energy-consuming than arithmetic operations. Accessing off-chip DRAM consumes about 200x more energy than an ALU operation (e.g., 32-bit DRAM read consumes ~640 pJ versus ~3.7 pJ for 32-bit floating-point add, and ~1.1 pJ for 32-bit SRAM read). |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Tracked via research note R04, which transcribes Sze et al. Table 1 / Section V-A verbatim. The three figures are the numbers chapter 3's dataflow section teaches. |

### V-07-07 · Dram Vs Alu Energy Ratio

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dram_vs_alu_energy_ratio` |
| value | `200` |
| unit | `multiplier` |
| conditions | `DRAM access vs ALU operation; Sze et al. Section V-A` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | Accessing off-chip DRAM consumes about 200x more energy than an ALU operation (e.g., 32-bit DRAM read consumes ~640 pJ versus ~3.7 pJ for 32-bit floating-point add, and ~1.1 pJ for 32-bit SRAM read). |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The ~200x headline ratio chapter 3 keeps returning to. |

### V-07-08 · Weight Stationary Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `weight_stationary_dataflow` |
| value | `Weight-Stationary` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | The goal of the weight stationary (WS) dataflow is to minimize the energy consumption of reading weights. In a WS dataflow, weights are read from DRAM or the global buffer into the register file (RF) of each processing element (PE) and kept there for as many MAC operations as possible. Input activations and partial sums must move through the spatial array and global buffer. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Verbatim quote via R04. The survey itself prints the taxonomy as WS / OS / No-Local-Reuse / Row-Stationary; the book teaches the WS/IS/OS triad R04 transcribes. |

### V-07-09 · Input Stationary Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `input_stationary_dataflow` |
| value | `Input-Stationary` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | The goal of the input stationary (IS) dataflow is to minimize the energy consumption of reading input activations from memory. In an IS dataflow, input activations are kept in the RF of each PE, while weights and partial sums are moved through the PEs. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Verbatim quote via R04. |

### V-07-10 · Output Stationary Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `output_stationary_dataflow` |
| value | `Output-Stationary` |
| unit | `architecture` |
| conditions | `Sze et al. Section V-B dataflow taxonomy` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | The goal of the output stationary (OS) dataflow is to minimize the energy consumption of reading and writing partial sums. Accumulation is performed locally within the RF of each PE until the final output activation is calculated. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Verbatim quote via R04. |

### V-07-11 · Softmax Base2 Reformulation

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `softmax_base2_reformulation` |
| value | `exp(x) = 2^(x * log2(e))` |
| unit | `string` |
| conditions | `I-BERT Section 3.2, base-2 exponent reformulation for integer-only softmax` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Calculating the exponential function $e^x$ directly with integer arithmetic is notoriously difficult due to overflow and precision loss. We reformulate $e^x$ by converting the natural base $e$ into base 2: exp(x) = 2^(x * log2(e)) |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | First step of the integer-only softmax path chapter 7 teaches. |

### V-07-12 · Exponent Integer Fraction Decomposition

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `exponent_integer_fraction_decomposition` |
| value | `z = q + p with q = floor(z), p = z - q` |
| unit | `string` |
| conditions | `I-BERT Section 3.2, decomposition of z = x * log2(e) into integer and fractional parts` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Let z = x * log2(e). We decompose z into its integer component q and fractional component p in [0, 1): z = q + p, where q = floor(z), p = z - q |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Second step: the integer part feeds the bit shift, the fraction feeds the polynomial. |

### V-07-13 · Bit Shift Exponent

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `bit_shift_exponent` |
| value | `2^q = 1 << q` |
| unit | `string` |
| conditions | `I-BERT Section 3.2, hardware bit-shift for the integer part of the exponent` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | Here, 2^q can be computed exactly using a simple hardware bit-shift operation: 1 << q. The term 2^p for p in [0, 1) is approximated with a second-order polynomial using integer multiplication and addition |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The bit-shift is the zero-DSP path: a barrel shifter built from LUTs. |

### V-07-14 · Polynomial Fraction Coefficients

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `polynomial_fraction_coefficients` |
| value | `0.6958 / 0.2250` |
| unit | `string` |
| conditions | `I-BERT Section 3.2, second-order polynomial approximating 2^p` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | The term 2^p for p in [0, 1) is approximated with a second-order polynomial using integer multiplication and addition: 2^p approx 1 + 0.6958 p + 0.2250 p^2 |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The two coefficients are the numbers the equation card in chapter 7 tabulates. |

### V-07-15 · Integer Only Softmax Claim

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `integer_only_softmax_claim` |
| value | `transcendental FP replaced by integer arithmetic and bit-shifts, no large lookup tables` |
| unit | `string` |
| conditions | `I-BERT Section 3.2, summary claim of the integer-only approximation` |
| source_tier | `T3` |
| doc_id | `ICML 2021 / arXiv:2101.01321` |
| title | I-BERT: Integer-only BERT Quantization |
| url | https://arxiv.org/abs/2101.01321 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 2.3 |
| quote | This replaces transcendental floating-point computation with integer arithmetic and bit-shifts, without requiring large lookup tables. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The payoff sentence chapter 7's mechanism section ends on. |

### V-07-16 · Confasr Process Node

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_process_node` |
| value | `22` |
| unit | `nm` |
| conditions | `ConfASR silicon, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Primary Hardware Specifications and Silicon Figures (Table 1 / Results): Process Technology: 22 nm FDSOI |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | All ConfASR numbers are quoted verbatim from research note R04 section 3.2, which transcribes the paper's Table 1 / Results section. |

### V-07-17 · Confasr Clock Frequency

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_clock_frequency` |
| value | `250` |
| unit | `MHz` |
| conditions | `ConfASR silicon, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Primary Hardware Specifications and Silicon Figures (Table 1 / Results): Clock Frequency: 250 MHz |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-07-18 · Confasr Operating Power

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_operating_power` |
| value | `359` |
| unit | `mW` |
| conditions | `ConfASR silicon, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Primary Hardware Specifications and Silicon Figures (Table 1 / Results): Operating Power: 359 mW |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-07-19 · Confasr Core Die Area

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_core_die_area` |
| value | `1.19` |
| unit | `mm2` |
| conditions | `ConfASR silicon, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Primary Hardware Specifications and Silicon Figures (Table 1 / Results): Core Die Area: 1.19 mm2 |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The unit is transcribed as ASCII mm2 because the record vocabulary forbids the superscript-two spelling, which is still to be registered; callers read the quote for the printed form. |

### V-07-20 · Confasr Streaming Throughput

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_streaming_throughput` |
| value | `900` |
| unit | `multiplier` |
| conditions | `ConfASR streaming throughput vs real-time requirement, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Streaming Throughput: greater than 900x faster than required for real-time streaming |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-07-21 · Confasr Latency Reduction

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_latency_reduction` |
| value | `4` |
| unit | `multiplier` |
| conditions | `ConfASR latency vs previous streaming ASR hardware, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Latency Reduction: greater than 4x lower latency compared to previous streaming ASR hardware solutions |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-07-22 · Confasr Power Reduction

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_power_reduction` |
| value | `16` |
| unit | `multiplier` |
| conditions | `ConfASR power vs existing edge platforms, real-time streaming mode, ASP-DAC 2026` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Power Reduction: 16x power reduction in real-time streaming mode compared to existing edge platforms |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes |  |

### V-07-23 · Confasr Unified Mac Dataflow

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_unified_mac_dataflow` |
| value | `unified MAC dataflow array with on-chip activation residency` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism 1` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | A unified Multiply-Accumulate (MAC) dataflow array maintaining intermediate activation residency on-chip, minimizing external DRAM traffic. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Mechanism 1 wires ConfASR to Sze's dataflow vocabulary: this is the IS family's goal, realised in silicon. |

### V-07-24 · Confasr Hw Normalization

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_hw_normalization` |
| value | `hardware-friendly normalization with shared scaling factors` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism 2` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Hardware-friendly normalization and shared scaling factors for non-linear operations, eliminating floating-point transcendental overheads. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Mechanism 2 is the silicon-level counterpart of chapter 7's integer-only non-linear approximations. |

### V-07-25 · Confasr Chunk Causal Buffering

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `confasr_chunk_causal_buffering` |
| value | `chunk-based causal attention left-context caching on dedicated hardware` |
| unit | `string` |
| conditions | `ConfASR architectural mechanism 3` |
| source_tier | `T3` |
| doc_id | `ASP-DAC 2026 (ConfASR)` |
| title | ConfASR: A Dedicated Conformer Block Accelerator for Streaming Automatic Speech Recognition |
| url | https://doi.org/10.18154/RWTH-2026-01243 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 3.2 |
| quote | Dedicated hardware buffering for chunk-based causal attention left-context caching. |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Mechanism 3 maps directly onto the left-context K/V ring buffer of chapter 9 section 9.4. |

### V-07-26 · Sze Energy Ladder Bit Width

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `sze_energy_ladder_bit_width` |
| value | `32-bit` |
| unit | `string` |
| conditions | `The example words in the Sze et al. Table 1 / Section V-A energy ladder are all 32-bit` |
| source_tier | `T3` |
| doc_id | `Proceedings of the IEEE 105(12) / arXiv:1703.09039` |
| title | Efficient Processing of Deep Neural Networks: A Tutorial and Survey |
| url | https://ieeexplore.ieee.org/document/8114708 |
| locator | docs/research_notes/R04_sota_speech_hardware_acceleration.md, section 1.3 |
| quote | Memory accesses are significantly more energy-consuming than arithmetic operations. Accessing off-chip DRAM consumes about 200x more energy than an ALU operation (e.g., 32-bit DRAM read consumes ~640 pJ versus ~3.7 pJ for 32-bit floating-point add, and ~1.1 pJ for 32-bit SRAM read). |
| retrieved_utc | `2026-09-17T06:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered so chapter 3's dataflow section can print the 32-bit width of the Sze example words; the width is part of the verbatim quote and no earlier record carries it. |
