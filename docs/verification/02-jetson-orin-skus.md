# Verification Records: 02 Jetson Orin Skus

### V-02-01 · Orin Nano 4Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_4gb_gpu_specs` |
| value | `512 CUDA cores, 16 Tensor Cores, 625 MHz` |
| unit | `string` |
| conditions | `Orin Nano 4GB, Ampere GPU, max operating frequency 625 MHz` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Ampere GPU section |
| quote | Jetson Orin Nano 4GB: 512 NVIDIA® CUDA® cores \| 16 Tensor cores ... Maximum Operating Frequency: 625 MHz |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://media.digikey.com/pdf/Data%20Sheets/Seeed%20Technology/Jetson_Orin_Nano_Series_DS-11105-001_v1.1.pdf |
| notes | Dense INT8 TOPS = 10, Sparse INT8 TOPS = 20. |

### V-02-02 · Orin Nano 4Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_4gb_memory_bandwidth` |
| value | `34` |
| unit | `GB/s` |
| conditions | `Jetson Orin Nano 4GB: 4GB 64-bit LPDDR5, max memory frequency 2133 MHz` |
| source_tier | `T1` |
| doc_id | `DS-11105-001` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.7, 'Memory' paragraph |
| quote | The Jetson Orin Nano 8GB integrates 8GB 128-bit LPDDR5 DRAM, and Jetson Orin Nano 4GB integrates 4GB 64-bit LPDDR5 DRAM. Maximum frequency of Jetson Orin Nano Memory is 2133 MHz. The theoretical peak memory bandwidth on Orin Nano 8GB is 68 GB/s, and on Orin Nano 4GB is 34 GB/s. |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 34.1 GB/s was bus-width arithmetic presented as a datasheet reading, with a p.1 quote that prints no bandwidth. The datasheet itself states 34 GB/s. DS-11105-001 carries no revision number on its cover and is stamped 'SUBJECT TO CHANGE \| PRELIMINARY - ADVANCE INFORMATION'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-03 · Orin Nano 4Gb Dla Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_4gb_dla_count` |
| value | `0` |
| unit | `DLA engines` |
| conditions | `Orin Nano 4GB` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Features summary |
| quote | DLA cores: 0 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | DLA is not present on any Orin Nano SKU. |

### V-02-04 · Orin Nano 4Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_4gb_power_modes` |
| value | `7W, 10W` |
| unit | `Watts` |
| conditions | `Orin Nano 4GB, nvpmodel Mode 0 (10W default), Mode 1 (7W_AI), Mode 2 (7W_CPU)` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 705 |
| quote | Jetson Orin Nano 4GB Modes: 7W \| 10W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 0 (10W). |

### V-02-05 · Orin Nano 8Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_8gb_gpu_specs` |
| value | `1024 CUDA cores, 32 Tensor Cores, 625 MHz` |
| unit | `string` |
| conditions | `Orin Nano 8GB, Ampere GPU, max operating frequency 625 MHz` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Ampere GPU section |
| quote | Jetson Orin Nano 8GB: 1024 NVIDIA® CUDA® cores \| 32 Tensor cores ... Maximum Operating Frequency: 625 MHz |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://media.digikey.com/pdf/Data%20Sheets/Seeed%20Technology/Jetson_Orin_Nano_Series_DS-11105-001_v1.1.pdf |
| notes | Dense INT8 TOPS = 20, Sparse INT8 TOPS = 40. |

### V-02-06 · Orin Nano 8Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_8gb_memory_bandwidth` |
| value | `68` |
| unit | `GB/s` |
| conditions | `Jetson Orin Nano 8GB: 8GB 128-bit LPDDR5, max memory frequency 2133 MHz` |
| source_tier | `T1` |
| doc_id | `DS-11105-001` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.7, 'Memory' paragraph |
| quote | The Jetson Orin Nano 8GB integrates 8GB 128-bit LPDDR5 DRAM, and Jetson Orin Nano 4GB integrates 4GB 64-bit LPDDR5 DRAM. Maximum frequency of Jetson Orin Nano Memory is 2133 MHz. The theoretical peak memory bandwidth on Orin Nano 8GB is 68 GB/s, and on Orin Nano 4GB is 34 GB/s. |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 68.2 GB/s was arithmetic; the datasheet states 68 GB/s. Use 68 GB/s in roofline arithmetic for consistency with the source. DS-11105-001 carries no revision number on its cover and is stamped 'SUBJECT TO CHANGE \| PRELIMINARY - ADVANCE INFORMATION'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-07 · Orin Nano 8Gb Dla Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_8gb_dla_count` |
| value | `0` |
| unit | `DLA engines` |
| conditions | `Orin Nano 8GB` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Features summary |
| quote | DLA cores: 0 |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | No DLA engines on Orin Nano 8GB. |

### V-02-08 · Orin Nano 8Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_8gb_power_modes` |
| value | `7W, 15W` |
| unit | `Watts` |
| conditions | `Orin Nano 8GB, nvpmodel Mode 0 (15W default), Mode 1 (7W)` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 820 |
| quote | Jetson Orin Nano 8GB Modes: 7W \| 15W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 0 (15W). |

### V-02-09 · Orin Nano Super Ai Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_super_ai_tops` |
| value | `67` |
| unit | `Sparse INT8 TOPS` |
| conditions | `Jetson Orin Nano Super Developer Kit (software stack update / JetPack 6.x)` |
| source_tier | `T2` |
| doc_id | `Jetson Orin Nano DevKit User Guide (2025-2026)` |
| title | Jetson Orin Nano Developer Kit - User Guide: Introduction |
| url | https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/index.html |
| locator | Introduction & Key Highlights table |
| quote | With the latest software update, Jetson Orin Nano delivers up to 67 INT8 TOPS of AI performance and a 1.7X generative AI performance improvement over its predecessor. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/ |
| notes | Not a new silicon chip; it is a software/firmware frequency unlock on existing Orin Nano hardware. |

### V-02-10 · Orin Nano Super Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_super_memory_bandwidth` |
| value | `102` |
| unit | `GB/s` |
| conditions | `Jetson Orin Nano Super, 128-bit LPDDR5 at 3199 MHz` |
| source_tier | `T2` |
| doc_id | `Jetson Orin Nano DevKit User Guide (2025-2026)` |
| title | Jetson Orin Nano Developer Kit - User Guide: Introduction |
| url | https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/index.html |
| locator | Key Highlights table, row 'Memory bandwidth' |
| quote | Memory bandwidth: Up to 102 GB/s with the latest software stack |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | EMC clock frequency increased from 2133 MHz to 3199 MHz. |

### V-02-11 · Orin Nano Super Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_super_power_modes` |
| value | `15W, 25W, MAXN_SUPER` |
| unit | `Watts` |
| conditions | `Jetson Orin Nano 8GB Super, nvpmodel Mode 0 (15W), Mode 1 (25W default), Mode 2 (MAXN_SUPER)` |
| source_tier | `T2` |
| doc_id | `Jetson Linux Developer Guide (r36.4.4)` |
| title | Jetson Linux Developer Guide: Platform Power and Performance |
| url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| locator | Jetson Linux Developer Guide r36.4.4, NVP Model Clock Configuration: Jetson Orin Nano 8GB Super |
| quote | Mode \| 15W* \| 7W \| 15W \| 25W* \| MAXN_SUPER** ; Power budget \| 15W \| 7W \| 15W \| 25W \| n/a ; Mode ID \| 0 \| 1 \| 0 \| 1 \| 2 ; The default mode is 25W (mode ID 1). |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Configurable from 7W to 25W. Quote widened: the earlier excerpt showed only the 25W default and the MAXN_SUPER footnote, not the 15W mode itself. |

### V-02-12 · Orin Nx 8Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_gpu_specs` |
| value | `1024 CUDA cores, 32 Tensor Cores, 765 MHz` |
| unit | `string` |
| conditions | `Orin NX 8GB, Ampere GPU, max operating frequency 765 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Ampere GPU section |
| quote | 1024 NVIDIA® CUDA® cores \| 32 Tensor cores ... ONX 8GB: Maximum Operating Frequency: 765 MHz |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Dense INT8 TOPS = 35, Sparse INT8 TOPS = 70. |

### V-02-13 · Orin Nx 8Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_dla_specs` |
| value | `1x NVDLA, 610 MHz, 20 TOPS (Sparse INT8)` |
| unit | `string` |
| conditions | `Orin NX 8GB` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Deep Learning Accelerator section |
| quote | ONX 8GB: 1x NVDLA \| Maximum Operating Frequency: 610 MHz \| 20 TOPs (Sparse INT8) |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 1 DLA engine enabled. |

### V-02-14 · Orin Nx 8Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_memory_bandwidth` |
| value | `102` |
| unit | `GB/s` |
| conditions | `Jetson Orin NX 8GB: 8GB LPDDR5, max frequency 3200 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.9, 'Memory' paragraph |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 102.4 GB/s was arithmetic; the datasheet prints 102 GB/s for the series. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-15 · Orin Nx 8Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_power_modes` |
| value | `10W, 15W, 20W` |
| unit | `Watts` |
| conditions | `Orin NX 8GB, nvpmodel Mode 0 (MAXN), Mode 1 (10W), Mode 2 (15W default), Mode 3 (20W)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 932 |
| quote | Jetson Orin NX 8GB Modes: 10W \| 15W \| 20W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (15W). |

### V-02-16 · Orin Nx 16Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_gpu_specs` |
| value | `1024 CUDA cores, 32 Tensor Cores, 918 MHz` |
| unit | `string` |
| conditions | `Orin NX 16GB, Ampere GPU, max operating frequency 918 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Ampere GPU section |
| quote | 1024 NVIDIA® CUDA® cores \| 32 Tensor cores ... ONX 16GB: Maximum Operating Frequency: 918 MHz |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Dense INT8 TOPS = 50, Sparse INT8 TOPS = 100. |

### V-02-17 · Orin Nx 16Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_dla_specs` |
| value | `2x NVDLA, 614 MHz, 20 TOPS each (40 TOPS total Sparse INT8)` |
| unit | `string` |
| conditions | `Orin NX 16GB` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Deep Learning Accelerator section |
| quote | ONX 16GB: 2x NVDLA \| Maximum Operating Frequency: 614 MHz \| 20 TOPS each (Sparse INT8) |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 2 DLA engines enabled. |

### V-02-18 · Orin Nx 16Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_memory_bandwidth` |
| value | `102` |
| unit | `GB/s` |
| conditions | `Jetson Orin NX 16GB: 16 GB 128-bit LPDDR5, max frequency 3200 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.9, 'Memory' paragraph |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 102.4 GB/s was arithmetic. The datasheet gives one bandwidth figure for the whole Orin NX series, so 8GB and 16GB share it. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-19 · Orin Nx 16Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_power_modes` |
| value | `10W, 15W, 25W` |
| unit | `Watts` |
| conditions | `Orin NX 16GB, nvpmodel Mode 0 (MAXN), Mode 1 (10W), Mode 2 (15W default), Mode 3 (25W)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.0` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://files.waveshare.com/wiki/common/Jetson_Orin_NX_DS-10712-001_v1.0.pdf |
| locator | p.1, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 1106 |
| quote | Jetson Orin NX 16GB Modes: 10W \| 15W \| 25W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (15W). |

### V-02-20 · Agx Orin 32Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_32gb_gpu_specs` |
| value | `1792 CUDA cores, 56 Tensor Cores, 939 MHz` |
| unit | `string` |
| conditions | `AGX Orin 32GB (JAO 32GB): 2 GPC, 7 TPC, GPU max operating frequency 939 MHz, 108 GPU Sparse TOPS` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.7, 'Ampere GPU' block, JAO 32GB row |
| quote | JAO 32GB: two graphics processing cluster (GPC) \| seven texture processing clusters (TPC) \| 1792 NVIDIA(R) CUDA(R) cores \| 56 Tensor cores Ray-Tracing cores \| 108 Sparse TOPS \| Maximum Operating Frequency: 939 MHz |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: the previous frequency 930.75 MHz does not appear anywhere in DS-10662-001v1.8 (whole-document search) and is withdrawn; the datasheet prints 939 MHz. The core counts were right but the old locator pointed at p.10-11, where the GPU table lists only GPC/TPC and TOPS. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-21 · Agx Orin 32Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_32gb_dla_specs` |
| value | `2x DLA, up to 98 INT8 Sparse TOPS (JAO 32GB), 2 MB dedicated SRAM` |
| unit | `string` |
| conditions | `AGX Orin 32GB (JAO 32GB)` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.12, 'Vision and DNN Accelerators' block |
| quote | 2x Deep Learning Accelerator (DLA) \| 2 MB dedicated SRAM JAOi: Up to 92 INT8 Sparse TOPs (Deep Learning Inference) JAO 64GB: Up to 105 INT8 Sparse TOPS (Deep Learning Inference) JAO 32GB: Up to 98 INT8 Sparse TOPS (Deep Learning Inference) |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: the previous value '92-98 TOPS' spanned three different products - 92 is JAOi, 98 is JAO 32GB, 105 is JAO 64GB. Per disambiguation trap 8 (a table column is a part, not the family), the JAO 32GB figure is 98. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-22 · Agx Orin 32Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_32gb_memory_bandwidth` |
| value | `204.8` |
| unit | `GB/s` |
| conditions | `32GB 256-bit LPDDR5 at 3200 MHz (256 bits * 3200 MHz * 2 / 8 = 204.8 GB/s)` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.12, 'Memory Subsystem' block |
| quote | Memory Subsystem \| Memory Type 256-bit LPDDR5 \| Maximum Memory Bus Bandwidth (up to) 204.8 GB/s \| Maximum Capacity JAOi: 64 GB JAO 64GB: 64 GB JAO 32GB: 32 GB |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 256-bit bus width. Quote confirmed verbatim against the v1.8 PDF; note the datasheet wording is 'up to'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-23 · Agx Orin 32Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_32gb_power_modes` |
| value | `15W, 30W, 40W, MAXN` |
| unit | `Watts` |
| conditions | `AGX Orin 32GB, nvpmodel Mode 0 (MAXN), Mode 1 (15W), Mode 2 (30W default), Mode 3 (40W)` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.9, Table 1-2, Total module power row; Jetson Linux Dev Guide r36.4.4 line 1267 |
| quote | JAO 32GB: 15W \| 30W \| 40W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (30W). |

### V-02-24 · Agx Orin 64Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_64gb_gpu_specs` |
| value | `2048 CUDA cores, 64 Tensor Cores, 1.3 GHz` |
| unit | `string` |
| conditions | `AGX Orin 64GB (JAO 64GB): 2 GPC, 8 TPC, GPU max operating frequency 1.3 GHz, 170 GPU Sparse TOPS` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.7, 'Ampere GPU' block, JAO 64GB row |
| quote | JAO 64GB: two graphics processing cluster (GPC) \| eight texture processing clusters (TPC) \| 2048 NVIDIA(R) CUDA(R) cores \| 64 Tensor cores Ray-Tracing cores \| 170 Sparse TOPS \| Maximum Operating Frequency: 1.3 GHz |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: the previous frequency 1301 MHz does not appear anywhere in DS-10662-001v1.8 (whole-document search) and is withdrawn; the datasheet prints 1.3 GHz. JAOi (industrial) is a separate row at 1.185 GHz and 156 Sparse TOPS. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-25 · Agx Orin 64Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_64gb_dla_specs` |
| value | `2x DLA, up to 105 INT8 Sparse TOPS, 2MB dedicated SRAM` |
| unit | `string` |
| conditions | `AGX Orin 64GB` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.10, Table 1-2 line 68; p.12 Table 1-3 line 160 |
| quote | JAO 64GB: Up to 105 INT8 TOPS (Sparse, Deep Learning Inference) |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Total module AI compute = 275 Sparse INT8 TOPS (170 GPU + 105 DLA). |

### V-02-26 · Agx Orin 64Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_64gb_memory_bandwidth` |
| value | `204.8` |
| unit | `GB/s` |
| conditions | `64GB 256-bit LPDDR5 at 3200 MHz (256 bits * 3200 MHz * 2 / 8 = 204.8 GB/s)` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.12, 'Memory Subsystem' block |
| quote | Memory Subsystem \| Memory Type 256-bit LPDDR5 \| Maximum Memory Bus Bandwidth (up to) 204.8 GB/s \| Maximum Capacity JAOi: 64 GB JAO 64GB: 64 GB JAO 32GB: 32 GB |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 256-bit bus width. Quote confirmed verbatim against the v1.8 PDF; note the datasheet wording is 'up to'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; replace with a docs.nvidia.com URL before this record is cited in the book. |

### V-02-27 · Agx Orin 64Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_64gb_power_modes` |
| value | `15W, 30W, 50W, up to 60W, MAXN` |
| unit | `Watts` |
| conditions | `AGX Orin 64GB, nvpmodel Mode 0 (MAXN), Mode 1 (15W), Mode 2 (30W default), Mode 3 (50W)` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.9, Table 1-2, Total module power row; Jetson Linux Dev Guide r36.4.4 line 1351 |
| quote | JAO 64GB: 15W \| 30W \| 50W, and up to 60W |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (30W). |

### V-02-28 · Project Selected Orin Sku

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `project_selected_orin_sku` |
| value | `` |
| unit | `n/a` |
| conditions | `Project architectural decision pending human selection` |
| source_tier | `T1` |
| doc_id | `n/a` |
| title | n/a |
| url |  |
| locator | plan-v2.md §3.1 |
| quote |  |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Pending human decision. Candidates characterized in V-02-01..27: (1) Orin Nano 8GB (low cost, 40 TOPS sparse, 68.2 GB/s, 15W, 0 DLA); (2) Orin NX 16GB (balanced edge, 100 TOPS sparse, 102.4 GB/s, 25W, 2x DLA); (3) AGX Orin 64GB (flagship edge, 275 TOPS sparse, 204.8 GB/s, 60W, 2x DLA). |
