# Verification Records: 04 Toolchain Versions

### V-04-01 · Vivado Ml Standard Zu5Ev Support

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `vivado_ml_standard_zu5ev_support` |
| value | `Supported (No license required)` |
| unit | `boolean` |
| conditions | `Vivado ML Standard / WebPACK edition, XCZU5EV device` |
| source_tier | `T1` |
| doc_id | `UG973 (v2019.1 / v2022.2)` |
| title | Vivado Design Suite User Guide: Release Notes, Installation, and Licensing |
| url | https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_2/ug973-vivado-release-notes-install-license.pdf |
| locator | p.8-9, Chapter 2 'Requirements and Setup', Table 1 'Architecture Support', Zynq UltraScale+ MPSoC |
| quote | UltraScale+ MPSoC: XCZU2EG, XCZU2CG, XCZU3EG, XCZU3CG, XCZU4EG, XCZU4CG, XCZU4EV, XCZU5EG, XCZU5CG, XCZU5EV, XCZU7EV, XCZU7EG, and XCZU7CG |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/2025.1-English/ug973-vivado-release-notes-install-license/Supported-Devices |
| notes | XCZU5EV (and therefore the K26 SOM) is fully supported in the free Vivado ML Standard edition. |

### V-04-02 · Vivado Disk Footprint Gb

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `vivado_disk_footprint_gb` |
| value | `48.6 - 95.9` |
| unit | `GB` |
| conditions | `Vivado ML Standard 2024.1 (Zynq UltraScale+ selected): 18.08 GB download, 95.9 GB required during install, 48.62 GB final installed footprint` |
| source_tier | `T2` |
| doc_id | `VivadoGuide2024_1` |
| title | Vivado 2024.1: Installation Guide |
| url | https://hthreads.github.io/classes/embedded-systems/labs/assets/guides/VivadoGuide2024_1.pdf |
| locator | p.2, Disk requirements summary |
| quote | Download: 18.08 GB \| Required: 95.9 GB \| Final: 48.62 GB |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ug973-vivado-release-notes-install-license |
| notes | Full Unified Vitis installer with multiple architectures requires >150-200 GB. URL is a university course mirror (hthreads.github.io) of a Xilinx document; replace with a docs.amd.com URL. |

### V-04-03 · Kv260 Dpu Architecture

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_dpu_architecture` |
| value | `DPUCZDX8G` |
| unit | `string` |
| conditions | `Zynq UltraScale+ MPSoC, Vitis AI 3.0` |
| source_tier | `T1` |
| doc_id | `PG338 (v4.1)` |
| title | DPU for Convolutional Neural Network IP Product Guide |
| url | https://docs.amd.com/r/en-US/pg338-dpu |
| locator | Title page and Chapter 1 |
| quote | DPUCZDX8G for Zynq UltraScale+ MPSoCs Product Guide (PG338) |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://github.com/zeasa/nvdla-compiler/blob/master/document/pdf/pg338-dpu.pdf |
| notes | Hardware CNN processing engine overlay for Kria KV260. Quote identifies the IP name only; it does not establish which core configuration the KV260 actually ships with. See V-04-07, V-04-08, V-04-09 and conflict C-04. |

### V-04-04 · Dpuczdx8G B4096 Resource Footprint

| Field | Value |
|---|---|
| status | `conflict` |
| quantity | `dpuczdx8g_b4096_resource_footprint` |
| value | `37266 LUTs, 92630 FFs, 642 DSPs, 249.5 BRAMs (or URAM replaced)` |
| unit | `resources` |
| conditions | `High DSP usage, 1 DPU core, without depthwise/average pooling additions` |
| source_tier | `T1` |
| doc_id | `PG338 (v3.0)` |
| title | DPU for Convolutional Neural Network IP Product Guide |
| url | https://docs.amd.com/r/en-US/pg338-dpu |
| locator | p.27, Table 11 'Resources for Different DSP Usage', row 'B4096 High DSP Usage' |
| quote | B4096 \| LUT: 37266 \| Register: 92630 \| BRAM: 249.5 \| DSP: 642 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | WITHDRAWN AS EVIDENCE 2026-09-12 -> see C-04. PG338 v4.1 (2023-01-23) contains no Table 11 and no 'Resources for Different DSP Usage' caption, and none of 37266 / 92630 / 642 / 249.5 appear in the document. The numbers cannot be reproduced from the cited revision, so this record cannot support a resource-budget claim. Replacement evidence: V-04-07 and V-04-08. Kept rather than deleted, per protocol rule 6: never overwrite a contradicting record. |

### V-04-05 · Xpe Estimation Accuracy Nature

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `xpe_estimation_accuracy_nature` |
| value | `Pre-implementation estimation tool` |
| unit | `n/a` |
| conditions | `Pre-design and pre-RTL estimation, spreadsheet model` |
| source_tier | `T2` |
| doc_id | `UG440 (v2022.1)` |
| title | Xilinx Power Estimator User Guide |
| url | https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_1/ug440-xilinx-power-estimator.pdf |
| locator | p.4, Chapter 1 Introduction; p.10 Device Model Accuracy |
| quote | The Xilinx® Power Estimator (XPE) spreadsheet is a power estimation tool typically used in the pre-design and pre-implementation phases of a project. ... The device models are extracted from measurements, simulation, and/or extrapolation. ... Advance specifications are based on simulations only and are subject to change. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | XPE does not provide measured post-implementation silicon power; post-implementation requires Vivado Report Power or physical rail measurements. |

### V-04-06 · Vivado Utilization Report Command

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `vivado_utilization_report_command` |
| value | `report_utilization -file <filename>` |
| unit | `Tcl command` |
| conditions | `Post-synthesis or post-implementation in Vivado` |
| source_tier | `T2` |
| doc_id | `UG906 (v2022.2)` |
| title | Vivado Design Suite User Guide: Design Analysis and Closure Techniques |
| url | https://docs.amd.com/r/en-US/ug906-vivado-design-analysis/Report-Utilization |
| locator | Section 'Report Utilization' |
| quote | report_utilization -file utilization.rpt |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Outputs exact site breakdowns for CLB LUTs, CLB Registers, Block RAM Tile (RAMB36/RAMB18), UltraRAM (URAM288), and DSPs (DSP48E2). |

### V-04-07 · Dpuczdx8G B4096 Zcu102 Low Ram Footprint

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dpuczdx8g_b4096_zcu102_low_ram_footprint` |
| value | `52161 LUT, 98249 Register, 255 Block RAM, 710 DSP` |
| unit | `resources` |
| conditions | `DPUCZDX8G B4096 single core on the ZCU102 platform, low RAM usage, channel augmentation, alu parallel = PP/2, conv leaky ReLU + ReLU6, alu ReLU6 features, high DSP usage, Argmax enabled` |
| source_tier | `T2` |
| doc_id | `PG338 (v4.1)` |
| title | DPU for Convolutional Neural Network IP Product Guide |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Resource Utilization, Table 1 'Resources of Different DPUCZDX8G Architectures', row B4096 |
| quote | Table 1. Resources of Different DPUCZDX8G Architectures \| DPUCZDX8G Architecture \| LUT \| Register \| Block RAM \| DSP \| B4096 \| 52161 \| 98249 \| 255 \| 710 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Supersedes V-04-04 (see C-04). The board sentence reads: 'The data is based on the ZCU102 platform with low RAM usage, channel augmentation, alu parallel = PP/2, conv: leaky ReLU + ReLU6, alu: ReLU6 features, high DSP usage, and Argmax enabled.' This is a ZCU102 reference-design figure, NOT a KV260 measurement, and 255 Block RAM already exceeds the 144 available on ZU5EV / XCK26. |

### V-04-08 · Dpuczdx8G B4096 Uram Footprint

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dpuczdx8g_b4096_uram_footprint` |
| value | `51843 LUT, 98567 Register, 0 Block RAM, 68 UltraRAM, 710 DSP` |
| unit | `resources` |
| conditions | `DPUCZDX8G B4096 single-core project on the ZCU104 platform, BRAM mapped into UltraRAM` |
| source_tier | `T2` |
| doc_id | `PG338 (v4.1)` |
| title | DPU for Convolutional Neural Network IP Product Guide |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Resource Utilization, Table 2 'Resources of DPUCZDX8G using UltraRAM', row B4096 |
| quote | Table 2. Resources of DPUCZDX8G using UltraRAM \| DPUCZDX8G Architecture \| LUT \| Register \| Block RAM \| UltraRAM \| DSP \| B4096 \| 51843 \| 98567 \| 0 \| 68 \| 710 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Supersedes V-04-04 (see C-04). The board sentence reads: 'Another example of a DPUCZDX8G single core project is based on the ZCU104 platform.' ZCU104 is a ZU7EV board with 96 URAM, which is why 68 URAM fits there; ZU5EV / XCK26 has 64, so this configuration does not fit KV260 either. |

### V-04-09 · B4096 Fits Zu5Ev

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `b4096_fits_zu5ev` |
| value | `No, as tabulated` |
| unit | `boolean` |
| conditions | `Compares the PG338 v4.1 Table 1 and Table 2 B4096 rows against the DS890 v4.10 ZU5EV totals` |
| source_tier | `T1` |
| doc_id | `Derived from V-04-07, V-04-08, V-01-05, V-01-07` |
| title | Derived feasibility check |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Arithmetic: 255 Block RAM > 144 available; 68 UltraRAM > 64 available; 710 DSP <= 1,248 |
| quote | B4096 \| 52161 \| 98249 \| 255 \| 710 vs Block RAM Blocks 144 ; B4096 \| 51843 \| 98567 \| 0 \| 68 \| 710 vs UltraRAM Blocks 64 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| notes | DSP is the one resource with headroom (710 of 1,248). Both memory variants of B4096 exceed ZU5EV. Therefore the DPU that actually runs on a KV260 overlay cannot be the full B4096 as tabulated in PG338: it is a smaller range (B1024 / B2048), a reduced or ranged-core build, or a design that trades LUTRAM. Which core configuration KV260 ships is NOT established by any record in this directory and must be read off the running overlay before any capacity claim in the plan is written as fact. |
