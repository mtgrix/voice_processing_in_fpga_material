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
| notes | Dense INT8 TOPS = 10, Sparse INT8 TOPS = 20.URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | CORRECTED 2026-09-12: previous value 34.1 GB/s was bus-width arithmetic presented as a datasheet reading, with a p.1 quote that prints no bandwidth. The datasheet itself states 34 GB/s. DS-11105-001 carries no revision number on its cover and is stamped 'SUBJECT TO CHANGE \| PRELIMINARY - ADVANCE INFORMATION'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 the vendor equivalent was measured: `https://developer.nvidia.com/downloads/jetson-orin-nano-series-data-sheet` answers HTTP 302 to /login, so NVIDIA does host this document but it cannot be re-read anonymously. The substitution is blocked on an authenticated fetch, not on effort. |

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
| notes | DLA is not present on any Orin Nano SKU.URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | Default mode is Mode 0 (10W).URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | Dense INT8 TOPS = 20, Sparse INT8 TOPS = 40.URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | CORRECTED 2026-09-12: previous value 68.2 GB/s was arithmetic; the datasheet states 68 GB/s. Use 68 GB/s in roofline arithmetic for consistency with the source. DS-11105-001 carries no revision number on its cover and is stamped 'SUBJECT TO CHANGE \| PRELIMINARY - ADVANCE INFORMATION'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 the vendor equivalent was measured: `https://developer.nvidia.com/downloads/jetson-orin-nano-series-data-sheet` answers HTTP 302 to /login, so NVIDIA does host this document but it cannot be re-read anonymously. The substitution is blocked on an authenticated fetch, not on effort. |

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
| notes | No DLA engines on Orin Nano 8GB.URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | Default mode is Mode 0 (15W).URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| conditions | `Orin NX 8GB, Ampere GPU, MAXN profile (765 MHz). The same table prints 1,173 MHz under MAXN_SUPER; see V-02-37.` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, Ampere GPU table |
| quote | Jetson Orin NX (ONX) 8GB \| Maximum Operating Frequency (up to): \| 1024 NVIDIA® CUDA® cores \| 32 Tensor cores: \| 765 MHz \| 1,173 MHz |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Dense INT8 TOPS = 35, Sparse INT8 TOPS = 70. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12: the core counts and 765 MHz print unchanged from v1.0. v1.7 additionally prints a MAXN_SUPER column. |

### V-02-13 · Orin Nx 8Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_dla_specs` |
| value | `1x NVDLA, 610 MHz, 20 TOPS (Sparse INT8)` |
| unit | `string` |
| conditions | `Orin NX 8GB, MAXN profile; v1.7 prints 1229 MHz / 40 TOPS under MAXN_SUPER (V-02-38)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.2, Deep Learning Accelerator (DLA) table |
| quote | Jetson Orin NX (ONX) 8GB: 1x NVDLA \| Maximum Operating Frequency (up to) \| Sparse INT8 Operations (up to) \| 610 MHz \| 20 TOPS \| 1229 MHz \| 40 TOPS |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 1 DLA engine enabled. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12. v1.0 put this table on p.1; v1.7 prints it on p.2, so the locator changed without the value changing. |

### V-02-14 · Orin Nx 8Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_memory_bandwidth` |
| value | `102` |
| unit | `GB/s` |
| conditions | `Jetson Orin NX 8GB: 8GB LPDDR5, max frequency 3200 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.9, 'Memory' paragraph |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 102.4 GB/s was arithmetic; the datasheet prints 102 GB/s for the series. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12: the sentence prints verbatim, including 3200 MHz and 102 GB/s. The memory subsystem table on p.2 prints the same two figures. |

### V-02-15 · Orin Nx 8Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_power_modes` |
| value | `10W, 15W, 20W, 40W (MAXN_SUPER)` |
| unit | `Watts` |
| conditions | `Orin NX 8GB, nvpmodel Mode 0 (MAXN), Mode 1 (10W), Mode 2 (15W default), Mode 3 (20W)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.3, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 932 |
| quote | Jetson Orin NX 8GB Modes: 10W \| 15W \| 20W \| 40W (MAXN_SUPER) |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (15W). Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. CORRECTED 2026-09-12 against the vendor v1.7: the v1.0 mirror listed 10W, 15W and 20W, and v1.7 adds a fourth mode, 40W (MAXN_SUPER). The nvpmodel numbering in conditions was read from the r36.4.4 developer guide and names no mode for 40W, so the datasheet mode list and the software mode list are not the same length. |

### V-02-16 · Orin Nx 16Gb Gpu Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_gpu_specs` |
| value | `1024 CUDA cores, 32 Tensor Cores, 918 MHz` |
| unit | `string` |
| conditions | `Orin NX 16GB, Ampere GPU, MAXN profile (918 MHz). The same table prints 1,173 MHz under MAXN_SUPER; see V-02-37.` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, Ampere GPU table |
| quote | Jetson Orin NX (ONX) 16GB \| Maximum Operating Frequency (up to): \| 1024 NVIDIA® CUDA® cores \| 32 Tensor cores: \| 918 MHz \| 1,173 MHz |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Dense INT8 TOPS = 50, Sparse INT8 TOPS = 100. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12: the core counts and 918 MHz print unchanged from v1.0. v1.7 additionally prints a MAXN_SUPER column. |

### V-02-17 · Orin Nx 16Gb Dla Specs

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_dla_specs` |
| value | `2x NVDLA, 614 MHz, 40 TOPS (Sparse INT8); 20 TOPS per engine is arithmetic` |
| unit | `string` |
| conditions | `Orin NX 16GB, MAXN profile; v1.7 prints 1229 MHz / 80 TOPS under MAXN_SUPER (V-02-38)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.2, Deep Learning Accelerator (DLA) table; arithmetic: 40 / 2 = 20 |
| quote | Jetson Orin NX (ONX)16GB: 2x NVDLA \| Maximum Operating Frequency (up to) \| Sparse INT8 Operations (up to) \| 614 MHz \| 40 TOPS \| 1229 MHz \| 80 TOPS |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 2 DLA engines enabled. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. DEFECT CORRECTED 2026-09-12: v1.0 was read as printing "20 TOPS each". The vendor v1.7 prints 40 TOPS for the 2x NVDLA configuration and never prints a per-engine figure, so the per-engine number is now declared as arithmetic (40 / 2 = 20) rather than as a datasheet reading. The total is unchanged. |

### V-02-18 · Orin Nx 16Gb Memory Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_memory_bandwidth` |
| value | `102` |
| unit | `GB/s` |
| conditions | `Jetson Orin NX 16GB: 16 GB 128-bit LPDDR5, max frequency 3200 MHz` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.9, 'Memory' paragraph |
| quote | The Jetson Orin NX 16GB integrates 16 GB 128-bit LPDDR5 DRAM, and Jetson Orin NX 8GB integrates 8GB LPDDR5 DRAM. The maximum frequency of Jetson Orin NX is 3200 MHz, and has a theoretical peak memory bandwidth of 102 GB/s. |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | CORRECTED 2026-09-12: previous value 102.4 GB/s was arithmetic. The datasheet gives one bandwidth figure for the whole Orin NX series, so 8GB and 16GB share it. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12: the sentence prints verbatim. Both SKUs share it, and the p.2 memory subsystem table prints 3200 MHz / 102 GB/s once for the series. |

### V-02-19 · Orin Nx 16Gb Power Modes

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_power_modes` |
| value | `10W, 15W, 25W, 40W (MAXN_SUPER)` |
| unit | `Watts` |
| conditions | `Orin NX 16GB, nvpmodel Mode 0 (MAXN), Mode 1 (10W), Mode 2 (15W default), Mode 3 (25W)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.3, Operating Requirements; Jetson Linux Dev Guide r36.4.4 line 1106 |
| quote | Jetson Orin NX 16GB Modes: 10W \| 15W \| 25W \| 40W (MAXN_SUPER) |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url | https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html |
| notes | Default mode is Mode 2 (15W). Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. CORRECTED 2026-09-12 against the vendor v1.7: the v1.0 mirror listed 10W, 15W and 25W, and v1.7 adds 40W (MAXN_SUPER). This doubles the ceiling a reader would plan a thermal envelope from, so it is recorded as C-07 rather than settled here. |

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
| notes | CORRECTED 2026-09-12: the previous frequency 930.75 MHz does not appear anywhere in DS-10662-001v1.8 (whole-document search) and is withdrawn; the datasheet prints 939 MHz. The core counts were right but the old locator pointed at p.10-11, where the GPU table lists only GPC/TPC and TOPS. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 no vendor download slug for DS-10662-001 could be derived: four candidate paths under `developer.nvidia.com/downloads/` answer HTTP 404, while the Orin NX and Orin Nano slugs resolve. The Orin NX document is openly downloadable, so this is a slug problem rather than a policy conclusion, and it will not be settled by guessing. |

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
| notes | CORRECTED 2026-09-12: the previous value '92-98 TOPS' spanned three different products - 92 is JAOi, 98 is JAO 32GB, 105 is JAO 64GB. Per disambiguation trap 8 (a table column is a part, not the family), the JAO 32GB figure is 98. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 no vendor download slug for DS-10662-001 could be derived: four candidate paths under `developer.nvidia.com/downloads/` answer HTTP 404, while the Orin NX and Orin Nano slugs resolve. The Orin NX document is openly downloadable, so this is a slug problem rather than a policy conclusion, and it will not be settled by guessing.AMENDED by the second pass: the note here once asserted '92 is JAOi' as though that settled the 32GB SKU, but 92 is also printed for JAO 32GB, on p.10, and follows from p.8's 46 TOPS per engine. The 98 in this record is p.12's figure and it is the odd one out. Both readings and the additivity argument are in V-02-33 (C-05). |

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
| notes | 256-bit bus width. Quote confirmed verbatim against the v1.8 PDF; note the datasheet wording is 'up to'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 no vendor download slug for DS-10662-001 could be derived: four candidate paths under `developer.nvidia.com/downloads/` answer HTTP 404, while the Orin NX and Orin Nano slugs resolve. The Orin NX document is openly downloadable, so this is a slug problem rather than a policy conclusion, and it will not be settled by guessing. |

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
| notes | Default mode is Mode 2 (30W).URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | CORRECTED 2026-09-12: the previous frequency 1301 MHz does not appear anywhere in DS-10662-001v1.8 (whole-document search) and is withdrawn; the datasheet prints 1.3 GHz. JAOi (industrial) is a separate row at 1.185 GHz and 156 Sparse TOPS. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 no vendor download slug for DS-10662-001 could be derived: four candidate paths under `developer.nvidia.com/downloads/` answer HTTP 404, while the Orin NX and Orin Nano slugs resolve. The Orin NX document is openly downloadable, so this is a slug problem rather than a policy conclusion, and it will not be settled by guessing. |

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
| notes | Total module AI compute = 275 Sparse INT8 TOPS (170 GPU + 105 DLA).URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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
| notes | 256-bit bus width. Quote confirmed verbatim against the v1.8 PDF; note the datasheet wording is 'up to'. URL is a third-party mirror of the NVIDIA PDF, not a NVIDIA-hosted document; on 2026-09-12 no vendor download slug for DS-10662-001 could be derived: four candidate paths under `developer.nvidia.com/downloads/` answer HTTP 404, while the Orin NX and Orin Nano slugs resolve. The Orin NX document is openly downloadable, so this is a slug problem rather than a policy conclusion, and it will not be settled by guessing. |

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
| notes | Default mode is Mode 2 (30W).URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

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

### V-02-29 · Orin Nano Sparse Versus Dense Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_sparse_versus_dense_tops` |
| value | `8GB: up to 40 sparse / 20 dense INT8 TOPS; 4GB: up to 20 sparse / 10 dense INT8 TOPS` |
| unit | `INT8 TOPS` |
| conditions | `Jetson Orin Nano at 625 MHz GPU; no DLA on either SKU` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.1, 'AI Performance' block; restated p.4 in the Jetson Orin Nano introduction; arithmetic: 40 / 2 = 20; 20 / 2 = 10 |
| quote | Jetson Orin Nano 8GB: Up to 40 (Sparse) INT8 TOPs and 20 (Dense) INT8 TOPs; Jetson Orin Nano 4GB: Up to 20 (Sparse) INT8 TOPs and 10 (Dense) INT8 TOPs |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The datasheet prints both numbers for both SKUs, so the factor of two is NVIDIA's own rather than a reading. Headline figures in marketing, and in this repository's plan, consistently use the sparse number; a model that is not 2:4 pruned will not reach it. URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-30 · Orin Nx Sparse Versus Dense Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_sparse_versus_dense_tops` |
| value | `16GB: up to 100 sparse / 50 dense INT8 TOPS; 8GB: up to 70 sparse / 35 dense INT8 TOPS` |
| unit | `INT8 TOPS` |
| conditions | `Jetson Orin NX at the MAXN profile: 918 MHz (16GB) or 765 MHz (8GB) GPU. The same block prints 157/78 and 117/58 TOPS under MAXN_SUPER; see V-02-39, V-02-40.` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, 'AI Performance' block; arithmetic: 100 / 2 = 50; 70 / 2 = 35 |
| quote | Jetson Orin NX (ONX)16GB \| Number of Operations (up to) \| Sparse \| 100 INT8 TOPs \| 157 INT8 TOPs \| Dense \| 50 INT8 TOPs \| 78 INT8 TOPs ... Jetson Orin NX (ONX) 8GB \| Number of Operations (up to) \| Sparse \| 70 INT8 TOPs \| 117 INT8 TOPs \| Dense \| 35 INT8 TOPs \| 58 INT8 TOPs |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Recorded alongside the sparse figure because '100 TOPS' is the number this project's plan uses for the NX, and it is the number a 2:4-pruned network would have to earn. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-read from the vendor v1.7 on 2026-09-12: 100/50 and 70/35 print unchanged. v1.7 adds a MAXN_SUPER column with higher figures, which is why this record now names the profile it belongs to. |

### V-02-31 · Ampere Structured Sparsity Speedup

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ampere_structured_sparsity_speedup` |
| value | `2x (structured sparsity doubles throughput; up to 2x higher inference performance)` |
| unit | `multiplier` |
| conditions | `NVIDIA Ampere GPU Tensor Cores, 2:4 structured sparsity only` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.18, Ampere GPU enhancements, first bullet; p.19, structured-sparsity paragraph |
| quote | Sparsity: fine grained structured sparsity doubles throughput and reduces memory usage. ... Ampere adds support for structured sparsity. ... The Tensor Cores in Ampere can provide up to 2x higher performance for inference of sparse models. |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | This is the primary justification for reading any Orin sparse TOPS figure as twice its dense figure, and for the reverse division. Note 'up to': 2x needs the network actually pruned to 2:4. Unstructured sparsity is a different feature on the same page (Compute Data Compression). URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-32 · Agx Module Tops Equals Gpu Plus Dla

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_module_tops_equals_gpu_plus_dla` |
| value | `JAOi 156 + 92 = 248; JAO 64GB 170 + 105 = 275` |
| unit | `sparse INT8 TOPS` |
| conditions | `module totals on p.7 reconciled against GPU rows on p.7/p.10 and DLA rows on p.10/p.12` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.7 'AI Performance' and 'Ampere GPU'; p.10 'GPU' and 'Vision and DNN accelerators'; p.12 'Vision and DNN Accelerators'; arithmetic: 156 + 92 = 248; 170 + 105 = 275 |
| quote | JAOi: Up to 248 TOPs (INT8) ; JAO 64GB: Up to 275 Sparse TOPS (INT8) ; JAOi: 156 Sparse TOPS ; JAO 64GB: 170 Sparse TOPS ; JAOi: Up to 92 INT8 TOPS (Sparse, Deep Learning Inference) ; JAO 64GB: Up to 105 INT8 TOPS (Sparse, Deep Learning Inference) |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Establishes that the printed module figure is the sum of the printed GPU and DLA figures, which is what makes V-02-33's failure to sum a finding rather than a rounding fuss. It also settles that JAOi's unqualified '248 TOPs (INT8)' on p.7 is a sparse figure, since both of its components are printed as sparse. URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-33 · Agx Orin 32Gb Dla Tops

| Field | Value |
|---|---|
| status | `conflict` |
| quantity | `agx_orin_32gb_dla_tops` |
| value | `92 (p.8 per-engine x 2, and p.10) or 98 (p.12)` |
| unit | `sparse INT8 TOPS` |
| conditions | `Jetson AGX Orin 32GB DLA throughput; same document, three pages, two answers` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.8 'DL Accelerator' ('JAO 32GB: Maximum Operating Frequency: 1.4 GHz \| 46 TOPs each (Sparse INT8)'); p.10 'Vision and DNN accelerators' ('JAO 32GB: Up to 92'); p.12 'Vision and DNN Accelerators' ('JAO 32GB: Up to 98'); arithmetic: 2 * 46 = 92; 108 + 92 = 200; 108 + 98 = 206; 206 > 200 |
| quote | JAOi/JAO: 2x NVDLA 2.0 Engines ... JAO 32GB: Maximum Operating Frequency: 1.4 GHz \| 46 TOPs each (Sparse INT8) ; JAO 32GB: Up to 92 INT8 TOPS (Sparse, Deep Learning Inference) ; JAO 32GB:  Up to 98 INT8 Sparse TOPS (Deep Learning Inference) ; JAO 32GB: Up to 200 Sparse TOPs (INT8) ; JAO 32GB: 108 Sparse TOPS |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | C-05. WHY BOTH ARE RECORDED: 92 and 98 are each printed verbatim in DS-10662-001v1.8 for the same SKU, and protocol rule 6 forbids overwriting a record to hide a contradiction. READING 1 (92): two engines at 46 TOPS each on p.8 gives 92, p.10 states 92 outright, and only 92 makes the datasheet's own module total work, since the p.7 figure 200 equals 108 GPU + 92 DLA. READING 2 (98): p.12 states 98 outright - the row V-02-21 quotes - and it is the only page that disagrees; with 98 the module total would have to be 206, which appears nowhere in the document. WEIGHING: the additivity V-02-32 demonstrates for JAOi and JAO 64GB holds for the 32GB SKU only under reading 1, so 92 is the better supported figure and 98 is most likely an editorial slip on p.12. NOT ADOPTED as the value, because that would be this directory choosing over the datasheet. This also amends the first-pass note on V-02-21, which asserted '92 is JAOi' as though 92 were not also printed for the 32GB SKU: it is, on p.10 and per-engine on p.8. ACTION: measure on hardware, or ask NVIDIA. URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-34 · Orin Nano Lpddr5 Clock Versus Data Rate

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nano_lpddr5_clock_versus_data_rate` |
| value | `2133 MHz printed as the memory clock is 4266 MT/s as a data rate` |
| unit | `MHz / MT/s` |
| conditions | `LPDDR5 on Jetson Orin Nano; the datasheet's MHz figure is CK, not data rate` |
| source_tier | `T1` |
| doc_id | `DS-11105-001_v1.1` |
| title | NVIDIA Jetson Orin Nano Series Data Sheet |
| url | https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf |
| locator | p.7, 'Memory' paragraph; arithmetic: 2133 * 2 = 4266; 4266 * 16 / 1000 = 68.3; 4266 * 8 / 1000 = 34.1; 2133 * 16 / 1000 = 34.1 |
| quote | Maximum frequency of Jetson Orin Nano Memory is 2133 MHz. The theoretical peak memory bandwidth on Orin Nano 8GB is 68 GB/s, and on Orin Nano 4GB is 34 GB/s. |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | TWO READINGS OF THE SAME '2133 MHz', differing by a factor of two: taken as a data rate it predicts 34 GB/s on a 128-bit bus, taken as the memory clock - DDR being double data rate, so 4266 MT/s - it predicts 68.3 against a printed 68. The datasheet prints 68 for the 8GB and 34 for the 4GB, so the clock reading reproduces both numbers and the single-pump reading quietly assigns the 4GB module's bandwidth to the 8GB module. The same convention reconciles Orin NX 3200 MHz to 102 GB/s (V-02-18) and AGX 3200 MHz to 204.8 GB/s (V-02-35). Contrast K26, where DS987 prints 2400 Mb/s already as a data rate and no doubling applies (V-01-13). URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-35 · Agx Orin Memory Bandwidth Derivation

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `agx_orin_memory_bandwidth_derivation` |
| value | `204.8 GB/s from 3200 MHz x 2 x 32 bytes` |
| unit | `GB/s` |
| conditions | `256-bit LPDDR5 bus; the datasheet words it as '(up to) 204.8 GB/s'` |
| source_tier | `T1` |
| doc_id | `DS-10662-001v1.8` |
| title | NVIDIA Jetson AGX Orin Series Modules Data Sheet |
| url | https://static.generation-robots.com/media/Jetson-AGX-Orin-Data-Sheet.pdf |
| locator | p.12 'Memory Subsystem' (256-bit LPDDR5, '(up to) 204.8 GB/s'); p.29 section 4.10 (memory clock 3200 MHz); arithmetic: 3200 * 2 = 6400; 6400 * 32 = 204800; 204800 / 1000 = 204.8 |
| quote | Memory Subsystem \| Memory Type 256-bit LPDDR5 \| Maximum Memory Bus Bandwidth (up to) 204.8 GB/s |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The derivation is recorded so a reader can see why the datasheet writes 'up to': 204.8 GB/s is the peak at the maximum supported clock, and the clock is DVFS-scaled, so measured bandwidth is always lower. With V-02-34 this is the third SKU whose printed MHz reconciles to its printed GB/s under the 2x convention and fails under the 1x reading, which is what makes the convention a finding rather than an assumption. URL is a third-party mirror of the NVIDIA PDF rather than a vendor-hosted document; the quoted text was read out of that mirror copy on 2026-09-12. See 'Mirror URLs' in this directory's README. |

### V-02-36 · Orin Nx 16Gb Gpu Share Of Sparse Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_gpu_share_of_sparse_tops` |
| value | `60 (derived: 100 module sparse total minus 40 DLA sparse)` |
| unit | `sparse INT8 TOPS` |
| conditions | `Jetson Orin NX 16GB at the MAXN profile; no page of DS-10712-001_v1.7 prints a GPU-only TOPS figure` |
| source_tier | `T2` |
| doc_id | `Derived from DS-10712-001_v1.7 (V-02-16, V-02-17, V-02-30)` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1 'AI Performance' and p.2 'Deep Learning Accelerator (DLA)'; arithmetic: 100 - 40 = 60 |
| quote | Jetson Orin NX (ONX)16GB \| Number of Operations (up to) \| Sparse \| 100 INT8 TOPs \| 157 INT8 TOPs \| Dense \| 50 INT8 TOPs \| 78 INT8 TOPs ... Jetson Orin NX (ONX)16GB: 2x NVDLA \| Maximum Operating Frequency (up to) \| Sparse INT8 Operations (up to) \| 614 MHz \| 40 TOPS \| 1229 MHz \| 80 TOPS |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Labelled derived and tiered T2 for that reason: the datasheet prints 100, 20 and '2x', but never 60. The subtraction assumes the module total is GPU plus DLA, which V-02-32 demonstrates on the same vendor's AGX datasheet but which this datasheet never states. A roofline that double-counts the DLA overstates Orin NX headroom by up to 40%, so the split matters even though the total is printed. Source is NVIDIA's own copy of the datasheet, fetched anonymously from developer.nvidia.com on 2026-09-12 (HTTP 200, application/pdf, 753,138 bytes, 56 pages, cover prints "DS-10712-001_v1.7 \| February 2026"). The citable URL 302-redirects to a token-bearing file URL on developer.download.nvidia.com that expires, so quote the developer.nvidia.com link, not the redirect target. Table rows are quoted with cells joined by " \| ", the convention this directory already uses for tabular evidence. Re-derived against the vendor v1.7 on 2026-09-12; 60 is unchanged because both inputs (100 and 40) print in v1.7 as they did in v1.0. Under MAXN_SUPER the same subtraction gives 157 - 80 = 77, which is why the profile is now named. |

### V-02-37 · Orin Nx Gpu Maxn Super Frequency

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_gpu_maxn_super_frequency` |
| value | `1173` |
| unit | `MHz` |
| conditions | `Jetson Orin NX 16GB and 8GB, Ampere GPU, MAXN_SUPER profile. Both SKUs print the same 1,173 MHz.` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, Ampere GPU table, MAXN_SUPER column |
| quote | Jetson Orin NX (ONX) 16GB \| Maximum Operating Frequency (up to): \| 1024 NVIDIA® CUDA® cores \| 32 Tensor cores: \| 918 MHz \| 1,173 MHz ... Jetson Orin NX (ONX) 8GB \| Maximum Operating Frequency (up to): \| 1024 NVIDIA® CUDA® cores \| 32 Tensor cores: \| 765 MHz \| 1,173 MHz |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | New fact that the v1.0 mirror does not contain. The second column of the overview tables is headed "MAXN_SUPER", and the CUDA Core Performance row under it prints 2.40 FP32 / 4.80 FP16 TFLOPs for both SKUs, which is consistent with 1,173 MHz on 1024 cores. |

### V-02-38 · Orin Nx Dla Maxn Super

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_dla_maxn_super` |
| value | `1229 MHz; 16GB 80 TOPS, 8GB 40 TOPS (Sparse INT8)` |
| unit | `mixed` |
| conditions | `Jetson Orin NX at the MAXN_SUPER profile` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.2, Deep Learning Accelerator (DLA) table, MAXN_SUPER column |
| quote | Jetson Orin NX (ONX)16GB: 2x NVDLA \| Maximum Operating Frequency (up to) \| Sparse INT8 Operations (up to) \| 614 MHz \| 40 TOPS \| 1229 MHz \| 80 TOPS ... Jetson Orin NX (ONX) 8GB: 1x NVDLA \| Maximum Operating Frequency (up to) \| Sparse INT8 Operations (up to) \| 610 MHz \| 20 TOPS \| 1229 MHz \| 40 TOPS |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | New fact from the vendor v1.7. Read beside V-02-13 and V-02-17, which carry the MAXN column the older mirror showed only. |

### V-02-39 · Orin Nx 16Gb Maxn Super Ai Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_16gb_maxn_super_ai_tops` |
| value | `157 sparse / 78 dense` |
| unit | `INT8 TOPS` |
| conditions | `Jetson Orin NX 16GB at the MAXN_SUPER profile; 40W module mode (V-02-19)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, 'AI Performance' block, MAXN_SUPER column |
| quote | Jetson Orin NX (ONX)16GB \| Number of Operations (up to) \| Sparse \| 100 INT8 TOPs \| 157 INT8 TOPs \| Dense \| 50 INT8 TOPs \| 78 INT8 TOPs |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | New fact from the vendor v1.7. This is the number that supersedes 100 in any ceiling calculation that assumes MAXN_SUPER, and it is not what the project plan currently uses. Registered as C-07. |

### V-02-40 · Orin Nx 8Gb Maxn Super Ai Tops

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_8gb_maxn_super_ai_tops` |
| value | `117 sparse / 58 dense` |
| unit | `INT8 TOPS` |
| conditions | `Jetson Orin NX 8GB at the MAXN_SUPER profile; 40W module mode (V-02-15)` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.1, 'AI Performance' block, MAXN_SUPER column |
| quote | Jetson Orin NX (ONX) 8GB \| Number of Operations (up to) \| Sparse \| 70 INT8 TOPs \| 117 INT8 TOPs \| Dense \| 35 INT8 TOPs \| 58 INT8 TOPs |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | New fact from the vendor v1.7, the 8GB counterpart of V-02-39. |

### V-02-41 · Orin Nx Maxn Super Supply Voltage Floor

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `orin_nx_maxn_super_supply_voltage_floor` |
| value | `8` |
| unit | `V` |
| conditions | `Jetson Orin NX, any SKU, MAXN_SUPER operation` |
| source_tier | `T1` |
| doc_id | `DS-10712-001_v1.7` |
| title | NVIDIA Jetson Orin NX Series Data Sheet |
| url | https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet |
| locator | p.3, Operating Requirements |
| quote | Supported Power Input: 5V-20V (8V-20V for MAXN_SUPER) |
| retrieved_utc | `2026-09-12T16:10:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | New fact from the vendor v1.7 and the reason MAXN_SUPER is not free: a carrier that supplies 5V cannot reach the profile that makes the 157 TOPS figure of V-02-39 true. Relevant here because the plan's budget arithmetic assumes the module can be run at its datasheet ceiling. |
