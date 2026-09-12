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
| source_tier | `T2` |
| doc_id | `Derived from V-04-07, V-04-08, V-01-05, V-01-07` |
| title | Derived feasibility check |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Arithmetic: 255 Block RAM > 144 available; 68 UltraRAM > 64 available; 710 DSP <= 1,248 |
| quote | B4096 \| 52161 \| 98249 \| 255 \| 710 vs Block RAM Blocks 144 ; B4096 \| 51843 \| 98567 \| 0 \| 68 \| 710 vs UltraRAM Blocks 64 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| notes | DSP is the one resource with headroom (710 of 1,248). Both memory variants of B4096 exceed ZU5EV. Therefore the DPU that actually runs on a KV260 overlay cannot be the full B4096 as tabulated in PG338: it is a smaller range (B1024 / B2048), a reduced or ranged-core build, or a design that trades LUTRAM. Which core configuration KV260 ships is NOT established by any record in this directory and must be read off the running overlay before any capacity claim in the plan is written as fact.Tier lowered from T1 to T2 on the second pass: a record whose value comes from comparing two other records is derived evidence however certain the comparison, and T1 means a datasheet says it. The comparison itself is unchanged and still holds. See V-04-12 for the largest core of each variant that does fit, and V-04-13 for the shipped configuration, which stays unresolved. |

### V-04-10 · Dpuczdx8G Bram Variant Ladder

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dpuczdx8g_bram_variant_ladder` |
| value | `B512 72 / B800 90 / B1024 104 / B1152 121 / B1600 126 / B2304 165 / B3136 208 / B4096 255 Block RAM` |
| unit | `Block RAM` |
| conditions | `PG338 v4.1 Table 1, ZCU102 platform, low RAM usage option, standalone single core` |
| source_tier | `T2` |
| doc_id | `PG338 (v4.1)` |
| title | DPUCZDX8G for Zynq UltraScale+ MPSoCs Product Guide (PG338) |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Resource Utilization, Table 1 'Resources of Different DPUCZDX8G Architectures' |
| quote | Table 1. Resources of Different DPUCZDX8G Architectures \| DPUCZDX8G Architecture \| LUT \| Register \| Block RAM \| DSP \| B512 \| 26922 \| 34543 \| 72 \| 118 \| B800 \| 29721 \| 41147 \| 90 \| 166 \| B1024 \| 34074 \| 48057 \| 104 \| 230 \| B1152 \| 32169 \| 47374 \| 121 \| 222 \| B1600 \| 38418 \| 58831 \| 126 \| 326 \| B2304 \| 42127 \| 68829 \| 165 \| 438 \| B3136 \| 46714 \| 79710 \| 208 \| 566 \| B4096 \| 52161 \| 98249 \| 255 \| 710 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url | https://github.com/Xilinx/Vitis-AI/tree/master/src/vai_runtime/target_factory/targets |
| notes | The whole ladder rather than one row, so any capacity question can be answered without re-fetching. Two limits: the table is measured on ZCU102 with a specific option set ('low RAM usage, channel augmentation, alu parallel = PP/2, conv: leaky ReLU + ReLU6, alu: ReLU6'), and it is a standalone single-core footprint, so a design carrying a video pipeline as well costs more than these numbers. PG338 never defines the unit: 'Block RAM' is a count of 36 Kb tiles, which is what makes 255 exceed ZU5EV's 144 rather than being a comparison of sizes. Vitis-AI ships one prototxt per rung with matching feature codes (B512 0x000056010200 through B4096 0x000056010407), corroborating the ladder's shape from a different AMD artifact. |

### V-04-11 · Dpuczdx8G Uram Variant Ladder

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dpuczdx8g_uram_variant_ladder` |
| value | `B512 18 / B800 40 / B1024 26 / B1152 44 / B1600 56 / B2304 60 / B3136 64 / B4096 68 UltraRAM, 0 Block RAM` |
| unit | `UltraRAM` |
| conditions | `PG338 v4.1 Table 2, ZCU104 platform, image and weights buffered in UltraRAM` |
| source_tier | `T2` |
| doc_id | `PG338 (v4.1)` |
| title | DPUCZDX8G for Zynq UltraScale+ MPSoCs Product Guide (PG338) |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | Resource Utilization, Table 2 'Resources of DPUCZDX8G using UltraRAM' |
| quote | Table 2. Resources of DPUCZDX8G using UltraRAM \| DPUCZDX8G Architecture \| LUT \| Register \| Block RAM \| UltraRAM \| DSP \| B512 \| 26767 \| 34538 \| 0 \| 18 \| 118 \| B800 \| 29563 \| 41129 \| 0 \| 40 \| 166 \| B1024 \| 33973 \| 48036 \| 0 \| 26 \| 230 \| B1152 \| 32064 \| 47357 \| 0 \| 44 \| 222 \| B1600 \| 38325 \| 58809 \| 0 \| 56 \| 326 \| B2304 \| 42060 \| 68808 \| 0 \| 60 \| 438 \| B3136 \| 46260 \| 80079 \| 0 \| 64 \| 566 \| B4096 \| 51843 \| 98567 \| 0 \| 68 \| 710 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The UltraRAM column is not monotonic with the architecture name - B1024 uses 26 where B800 uses 40 - so it is not a budget you can interpolate between rungs. Each rung must be read from this table or measured. Same standalone-single-core caveat as V-04-10, and the same undefined unit; per V-01-23 the URAM tile is 288 Kb, so these are tile counts. |

### V-04-12 · Largest Pg338 Core Fitting Zu5Ev

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `largest_pg338_core_fitting_zu5ev` |
| value | `B1600 for the Block RAM variant (126 of 144); B3136 for the UltraRAM variant (64 of 64, exactly full)` |
| unit | `architecture` |
| conditions | `Standalone single core against ZU5EV/XCK26 totals from V-01-05 and V-01-07; no video pipeline` |
| source_tier | `T2` |
| doc_id | `Derived from V-04-10, V-04-11, V-01-05, V-01-07` |
| title |  |
| url | https://docs.amd.com/r/en-US/pg338-dpu/Resource-Utilization |
| locator | PG338 v4.1 Tables 1-2 against DS890 v4.10 p.22 Table 23; arithmetic: 126 <= 144; 165 > 144; 64 <= 64; 68 > 64; 208 > 144; 60 <= 64 |
| quote | B1600 \| 38418 \| 58831 \| 126 \| 326 ; B2304 \| 42127 \| 68829 \| 165 \| 438 ; B3136 \| 46260 \| 80079 \| 0 \| 64 \| 566 ; B4096 \| 51843 \| 98567 \| 0 \| 68 \| 710 ; Block RAM Blocks \| 128 \| 144 \| 312 ; UltraRAM Blocks \| 48 \| 64 \| 96 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | DERIVED, and stated as such: PG338 never mentions KV260, ZU5EV, ZU9EG or XCK26 anywhere, so no row of either table is a vendor statement about this board. The Block RAM ceiling is firm - the next rung needs 165 tiles against 144. The UltraRAM ceiling at B3136 is arithmetical only: it consumes exactly 64 of 64 tiles, leaving nothing for the rest of the design, so in practice B2304 (60 tiles) is the largest UltraRAM core with any headroom, which is the 60 <= 64 statement above. LUT cost matters too: B1600 takes 38,418 of ZU5EV's 117,120 LUTs, about a third of the device for one core. |

### V-04-13 · Kv260 Shipped Dpu Core Architecture

| Field | Value |
|---|---|
| status | `unresolved` |
| quantity | `kv260_shipped_dpu_core_architecture` |
| value | `` |
| unit | `architecture` |
| conditions | `Which DPUCZDX8G rung the KV260 factory PetaLinux image actually loads` |
| source_tier | `T5` |
| doc_id | `no primary source found` |
| title |  |
| url |  |
| locator |  |
| quote |  |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | STILL UNRESOLVED after the second pass, and now recorded explicitly rather than left implicit in C-04. WHAT WAS TRIED: the AMD software-manual deep link docs.amd.com/r/en-US/ug230-kv260-vision-software-manual/DPU returns HTTP 404; a code search for DPUCZDX8G across org:Xilinx returns compiler targets and examples, not a KV260 core designation; searches restricted to device-tree arch directories return nothing; and PG338 v4.1 names no Kria board (V-04-10). WHY THE COMMUNITY ANSWER WAS NOT ADOPTED: third-party KV260 files disagree with each other - one board.env records DPU fingerprint 0x101000056010407, whose tail matches B4096 in PG338's ladder, while other KV260 files name DPUCZDX8G_ISA1_B3136 at 300 MHz and yet others _B4096 at 325 MHz. Those are tier T5, corroborating only under protocol rule 2, and mutually inconsistent. B4096 as tabulated does not fit this device at all (V-04-09), so a fingerprint read as B4096 needs explaining rather than repeating. TO RESOLVE: read dpu-sysfs resource_info and the fingerprint on a KV260 running the factory image, or open the DPU XSA the PetaLinux rootfs was built from. This is the one capacity question in the plan that documents cannot settle. |
