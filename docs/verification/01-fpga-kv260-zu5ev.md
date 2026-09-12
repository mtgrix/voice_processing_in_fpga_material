# Verification Records: 01 Fpga Kv260 Zu5Ev

### V-01-01 · Som Device Part Marking

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `som_device_part_marking` |
| value | `XCK26-SFVC784-2LV-C/I` |
| unit | `string` |
| conditions | `K26 SOM, commercial (C) or industrial (I) temperature grade` |
| source_tier | `T1` |
| doc_id | `DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.2, Functional Overview and Block Diagram, paragraph 1; p.11 Supported I/O Standards |
| quote | The K26 SOM leverages the XCK26-SFVC784-2LV-C/I, a custom-built Zynq UltraScale+ MPSoC that runs optimally (and exclusively) on the SOM. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit |
| notes | KV260 starter kit ordering SKU SK-KV260-G uses the commercial grade device XCK26-C. |

### V-01-02 · Som Base Device Family

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `som_base_device_family` |
| value | `AMD Zynq UltraScale+ MPSoC (EV sub-family)` |
| unit | `string` |
| conditions | `K26 SOM base silicon, family level only` |
| source_tier | `T2` |
| doc_id | `DS986 (v1.3)` |
| title | Kria KV260 Vision AI Starter Kit Data Sheet |
| url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| locator | Kria KV260 Vision AI Starter Kit > Product Details |
| quote | System logic cells 256K \| Block RAM blocks 144 \| UltraRAM blocks 64 \| DSP slices 1.2K |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| notes | CORRECTED 2026-09-12: this record previously asserted the exact part 'XCZU5EV' from a quote that names only 'an AMD Zynq(TM) UltraScale+(TM) MPSoC based silicon device', so the quote could not generate the value. Re-scoped to the family, which the quote does support. Part-level identification is recorded separately as V-01-15. |

### V-01-03 · Clb Lut Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `clb_lut_count` |
| value | `117120` |
| unit | `CLB LUTs` |
| conditions | `xczu5ev / XCK26` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'CLB LUTs' |
| quote | CLB LUTs: 117,120 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-overview |
| notes | Verified identical across DS890 Table 23 (p.22) and DS891 Table 5 (p.8). Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-04 · Clb Ff Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `clb_ff_count` |
| value | `234240` |
| unit | `CLB Flip-Flops` |
| conditions | `xczu5ev / XCK26` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'CLB Flip-Flops' |
| quote | CLB Flip-Flops: 234,240 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-overview |
| notes | Verified identical in DS891 Table 5 (p.8). Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-05 · On Chip Bram36 Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `on_chip_bram36_count` |
| value | `144` |
| unit | `BRAM36 blocks` |
| conditions | `xczu5ev / XCK26` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'Block RAM Blocks' |
| quote | Block RAM Blocks: 144 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| notes | Each BRAM block is 36 Kb, configurable as dual independent 18 Kb RAMs. Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-06 · On Chip Bram Capacity Mb

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `on_chip_bram_capacity_mb` |
| value | `5.1` |
| unit | `Mb` |
| conditions | `xczu5ev / XCK26 (144 blocks * 36 Kb = 5184 Kb)` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'Block RAM (Mb)' |
| quote | Block RAM (Mb): 5.1 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-overview |
| notes | 5184 Kb = 648 KB = 0.6328 MiB. Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-07 · On Chip Uram288 Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `on_chip_uram288_count` |
| value | `64` |
| unit | `URAM288 blocks` |
| conditions | `xczu5ev / XCK26` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'UltraRAM Blocks' |
| quote | UltraRAM Blocks: 64 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| notes | Each UltraRAM block is 288 Kb (72 bits x 4096 depth). Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-08 · On Chip Uram Capacity Mb

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `on_chip_uram_capacity_mb` |
| value | `18.0` |
| unit | `Mb` |
| conditions | `xczu5ev / XCK26 (64 blocks * 288 Kb = 18432 Kb)` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'UltraRAM (Mb)' |
| quote | UltraRAM (Mb): 18.0 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-overview |
| notes | 18432 Kb = 2304 KB = 2.25 MiB. Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-09 · Dsp48E2 Slice Count

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `dsp48e2_slice_count` |
| value | `1248` |
| unit | `DSP48E2 slices` |
| conditions | `xczu5ev / XCK26` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'DSP Slices' |
| quote | DSP Slices: 1,248 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| notes | Listed as '1.2K' in high-level marketing overview tables. Doc revision corrected v4.9 -> v4.10; row re-read from the v4.10 PDF p.22 Table 23 this session. |

### V-01-10 · Fpga Speed Grade Voltage

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `fpga_speed_grade_voltage` |
| value | `-2LV / 0.72V` |
| unit | `speed grade / Volts` |
| conditions | `XCK26-SFVC784-2LV, VCCINT = 0.72V, Commercial temp 0C to 85C MPSoC Tj` |
| source_tier | `T1` |
| doc_id | `DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.11, Supported I/O Standards, paragraph 3 |
| quote | The K26 SOM is built with the XCK26-SFVC784-2LV device; which has a -2 speed grade and is an LV device (operates at VCCINT = 0.72V). |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-overview |
| notes | Low voltage (LV) operation reduces dynamic power dissipation compared to standard 0.85V parts. |

### V-01-11 · Total On Chip Sram Capacity

| Field | Value |
|---|---|
| status | `conflict` |
| quantity | `total_on_chip_sram_capacity` |
| value | `23616` |
| unit | `Kb` |
| conditions | `Fabric SRAM only (144 BRAM36 + 64 URAM288 = 5184 Kb + 18432 Kb = 23616 Kb = 2952 KB = 2.8828 MiB)` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10) & DS891 (v1.9)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22 Table 23; arithmetic: 144 * 36 Kb + 64 * 288 Kb = 23,616 Kb |
| quote | Block RAM (Mb): 5.1 ... UltraRAM (Mb): 18.0 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Conflicts with plan.md:55 ('chỉ khoảng 4 MB') and R02_fpga_audio_streaming.md:23 ('providing ~4.5 MB'). True fabric SRAM is 2.88 MiB (2.95 MB decimal). Adding 256 KB PS OCM gives 3.13 MiB total on-chip SRAM. DS890 re-parsed from the v4.10 (21 May 2026) PDF: Table 23 ZU5EV values unchanged. Distributed RAM (V-01-16) and PS OCM (V-01-17) are additional on-chip storage and do not alter the BRAM+URAM figure of 23,616 Kb. |

### V-01-12 · Ddr Capacity And Bus Width

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ddr_capacity_and_bus_width` |
| value | `4 GB, 64-bit wide, 2400 Mb/s` |
| unit | `string` |
| conditions | `4x 1GB DDR4 devices, non-ECC on KV260 Starter Kit` |
| source_tier | `T1` |
| doc_id | `DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.2, Functional Overview and Block Diagram, bullet 2; DS986 p.5 Table |
| quote | • 4 GB 64-bit wide, 2400 Mb/s memory |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit |
| notes | DS986 p.5 states '4 GB (4 x 512 Mb x 16 bit) [non-ECC] DDR4' (where '512 Mb' is a typo in DS986 for 512M x 16 bit = 1 GB per chip, clarified in DS987 as 4x 1 GB = 4 GB total). |

### V-01-13 · Ddr Theoretical Bandwidth

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ddr_theoretical_bandwidth` |
| value | `19.2` |
| unit | `GB/s` |
| conditions | `64-bit bus at 2400 MT/s: 64 bits * 2400 MT/s / 8 bits/byte = 19,200 MB/s` |
| source_tier | `T1` |
| doc_id | `Derived from DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.2, Functional Overview, bullet 2 |
| quote | • 4 GB 64-bit wide, 2400 Mb/s memory |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Theoretical peak bandwidth is 19.2 GB/s. Actual achievable bandwidth depends on AXI port width, burst length, and DDRC scheduling. Value is arithmetic on the quoted bus width and data rate, not a printed datasheet figure. |

### V-01-14 · Ddr Pl Ps Interconnect

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ddr_pl_ps_interconnect` |
| value | `Shared PS DDRC` |
| unit | `n/a` |
| conditions | `MIO Bank 504 on PS, PL connects via PS-PL AXI HP/HPC ports` |
| source_tier | `T1` |
| doc_id | `DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.5, Processing System overview; Table 3 MIO Banks p.6 |
| quote | • Dynamic memory controller (DDRC): DDR4 memory controller with configurable quality-of-service configuration capabilities. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ug1091-carrier-card-design |
| notes | There are no dedicated memory pins from the PL fabric to external DRAM on the K26 SOM. All PL access to DDR4 must route through the PS AXI slave ports. |

### V-01-15 · Kv260 Fabric Resources Equal Zu5Ev Column

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_fabric_resources_equal_zu5ev_column` |
| value | `256,200 logic cells / 144 BRAM / 64 URAM / 1,248 DSP` |
| unit | `resources` |
| conditions | `K26 SOM fabric compared against the ZU5EV column of DS890 Table 23; ZU4EV and ZU7EV columns both differ` |
| source_tier | `T2` |
| doc_id | `DS986 (v1.3)` |
| title | Kria KV260 Vision AI Starter Kit Data Sheet - Product Details |
| url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| locator | Product Details rows 'System logic cells', 'Block RAM blocks', 'UltraRAM blocks', 'DSP slices'; compared to DS890 (v4.10) p.22 Table 23 ZU5EV column |
| quote | System logic cells 256K \| Block RAM blocks 144 \| UltraRAM blocks 64 \| DSP slices 1.2K |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| notes | The KV260's published fabric numbers match DS890's ZU5EV column exactly on all four quantities and match neither ZU4EV (192,150 cells / 128 BRAM / 48 URAM / 728 DSP) nor ZU7EV (504,000 / 312 / 96 / 1,728). That is a strong identification of the fabric generation, but it remains an INFERENCE: no fetched document states 'XCK26 is an XCZU5EV'. Treat XCK26 and XCZU5EV as resource-equivalent for planning, and do not substitute an XCZU5EV timing or power figure for the K26 without checking the -2LV 0.72 V corner (V-01-10). Replaces the unsupported part-level assertion formerly carried by V-01-02. |

### V-01-16 · Distributed Ram Capacity Mb

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `distributed_ram_capacity_mb` |
| value | `3.5` |
| unit | `Mb` |
| conditions | `xczu5ev / XCK26 fabric LUTRAM; ZU5EV is the middle column (ZU4EV 2.6, ZU7EV 6.2)` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', row 'Distributed RAM (Mb)' |
| quote | Distributed RAM (Mb) \| 2.6 \| 3.5 \| 6.2 |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 3.5 Mb = 448 KiB of LUTRAM. Missed by the 2026-09-12 search pass. LUTRAM is good for small, low-latency on-chip storage but it consumes logic and is not initialised by the bitstream the way BRAM is, so it does not add to the 23,616 Kb BRAM+URAM budget of V-01-11 unless the design deliberately spends LUTs on it. |

### V-01-17 · Ps On Chip Memory Kb

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ps_on_chip_memory_kb` |
| value | `256` |
| unit | `KB` |
| conditions | `PS-side OCM with ECC; the row is a merged cell spanning ZU4EV/ZU5EV/ZU7EV, so it is a family-level statement, not ZU5EV-specific` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23, row 'Embedded and External Memory' |
| quote | Embedded and External Memory \| 256 KB On-Chip Memory w/ECC; External DDR4; DDR3; DDR3L; LPDDR4; LPDDR3; External Quad-SPI; NAND; eMMC |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | 256 KB = 0.25 MiB on the PS side, reachable from the PL over AXI. Missed by the 2026-09-12 search pass. It is not fabric SRAM and is not in the DPU's address space, so keep it out of the V-01-11 weight budget; it is worth about 64k INT8 weights for latency-critical scratch, not for model storage. |
