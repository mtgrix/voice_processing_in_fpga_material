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
| conditions | `Jetson Orin NX 16GB: 50 TOPS dense / 100 TOPS sparse, 102 GB/s memory bandwidth` |
| source_tier | `T1` |
| doc_id | `Derived from DS-10712-001_v1.0 (V-02-16, V-02-18)` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | Arithmetic derivation: 50,000 GOP/s / 102 GB/s = 490.2 OP/byte; 100,000 GOP/s / 102 GB/s = 980.4 OP/byte |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. ... Jetson Orin NX 16GB: Up to 100 (Sparse) INT8 TOPs and 50 (Dense) INT8 TOPs |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Very high ridge point means edge GPU is heavily memory bandwidth bound for streaming batch=1 speech processing with low arithmetic intensity. Recomputed 2026-09-12 using the 102 GB/s the datasheet actually prints, replacing 102.4. Previous values 488.3 / 976.6 are superseded; the conclusion (Orin is heavily bandwidth-bound for batch=1 streaming speech) is unchanged. |

### V-07-03 · Kria Kv260 Fpga Ridge Point

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kria_kv260_fpga_ridge_point` |
| value | `39.0 - 78.0` |
| unit | `OP/byte` |
| conditions | `KV260 (1248 DSP48E2 @ 300 MHz): 748.8 GOP/s (1 MAC/DSP) or 1497.6 GOP/s (packed INT8), 19.2 GB/s DDR4` |
| source_tier | `T1` |
| doc_id | `Derived from DS890 (V-01-09) and DS987 (V-01-13)` |
| title | UltraScale Architecture Overview & Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | Arithmetic derivation: 748.8 GOP/s / 19.2 GB/s = 39.0 OP/byte |
| quote | DSP Slices: 1,248 ... 4 GB 64-bit wide, 2400 Mb/s memory |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Ridge point is 6.2x to 12.5x lower than Orin NX, illustrating FPGA's advantage in streaming low-arithmetic-intensity workloads. |

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
