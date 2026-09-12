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
| notes | Conflicts with plan.md:55 ('chỉ khoảng 4 MB') and R02_fpga_audio_streaming.md:23 ('providing ~4.5 MB'). True fabric SRAM is 2.88 MiB (2.95 MB decimal). Adding 256 KB PS OCM gives 3.13 MiB total on-chip SRAM. DS890 re-parsed from the v4.10 (21 May 2026) PDF: Table 23 ZU5EV values unchanged. Distributed RAM (V-01-16) and PS OCM (V-01-17) are additional on-chip storage and do not alter the BRAM+URAM figure of 23,616 Kb.; Unit readings of the same quantity are enumerated in V-01-22; the tile sizes behind the sum are established in V-01-23. |

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
| source_tier | `T2` |
| doc_id | `Derived from DS987 (v1.2)` |
| title | Kria K26 SOM Data Sheet |
| url | https://docs.amd.com/r/en-US/ds987-k26-som |
| locator | p.2, Functional Overview, bullet 2; arithmetic: 64 * 2400 / 8 = 19200; 19200 / 1000 = 19.2 |
| quote | • 4 GB 64-bit wide, 2400 Mb/s memory |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Theoretical peak bandwidth is 19.2 GB/s. Actual achievable bandwidth depends on AXI port width, burst length, and DDRC scheduling. Value is arithmetic on the quoted bus width and data rate, not a printed datasheet figure.The 2400 Mb/s in DS987 is already the data rate (MT/s), so no factor of two applies here. That is the opposite of the NVIDIA LPDDR5 datasheets, which print the memory clock: see V-02-34. TIER CORRECTED 2026-09-12: was T1. The value is arithmetic on printed figures and is never printed itself, so it is tiered T2 like V-02-36, V-04-09 and V-04-12. Tier describes the evidence, not the quality of the source it was derived from. |

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

### V-01-15 · Zu5Ev Exact Fabric Column

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `zu5ev_exact_fabric_column` |
| value | `256,200 system logic cells / 117,120 CLB LUTs / 144 Block RAM blocks / 64 UltraRAM blocks / 1,248 DSP slices` |
| unit | `resources` |
| conditions | `ZU5EV column of DS890 Table 23, the column the K26 SOM's published vector matches` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23 'Zynq UltraScale+ MPSoC: EV Device Feature Summary', ZU5EV column (middle of ZU4EV \| ZU5EV \| ZU7EV) |
| quote | System Logic Cells \| 192,150 \| 256,200 \| 504,000 ; CLB LUTs \| 87,840 \| 117,120 \| 230,400 ; Block RAM Blocks \| 128 \| 144 \| 312 ; UltraRAM Blocks \| 48 \| 64 \| 96 ; DSP Slices \| 728 \| 1,248 \| 1,728 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| notes | CORRECTED 2026-09-12 (second pass): this record previously mixed two sources in one value - it carried DS986's marketing vector as its quote while its value stated 256,200 and 1,248, which only appear in DS890's Table 23. Re-pointed at DS890, which prints every number in the value. The exact system-logic-cell count 256,200 is confirmed printed in the ZU5EV column, so it is not arithmetic. The KV260's own published (rounded) vector is recorded separately as V-01-18, and the difference between the two is V-01-19. |

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

### V-01-18 · Kv260 Published Fabric Vector Marketing

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_published_fabric_vector_marketing` |
| value | `256K system logic cells / 144 Block RAM blocks / 64 UltraRAM blocks / 1.2K DSP slices` |
| unit | `resources` |
| conditions | `as published by AMD for the KV260, rounded to K units` |
| source_tier | `T2` |
| doc_id | `DS986 (v1.3)` |
| title | Kria KV260 Vision AI Starter Kit Data Sheet |
| url | https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details |
| locator | Product Details, rows 'System logic cells', 'Block RAM blocks', 'UltraRAM blocks', 'DSP slices' |
| quote | System logic cells 256K \| Block RAM blocks 144 \| UltraRAM blocks 64 \| DSP slices 1.2K |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| notes | Split out of the old V-01-15, which used this line as its quote while stating DS890's unrounded numbers as its value. This vector matches DS890's ZU5EV column (V-01-15) on all four quantities, which is the identification argument; the match itself is a comparison of two records, not a fact printed on this page. |

### V-01-19 · Marketing Rounding Error On Resource Counts

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `marketing_rounding_error_on_resource_counts` |
| value | `1.2K reads as 1,200 where the exact count is 1,248 (4% low); 256K reads as 256,000 where the exact count is 256,200 (0.08% low)` |
| unit | `percent` |
| conditions | `when a rounded marketing figure is used as if it were a design budget` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10) & DS986 (v1.3)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | DS986 Product Details ('256K', '1.2K') against DS890 p.22 Table 23 ZU5EV (256,200 and 1,248); arithmetic: 1248 / 1200 = 1.04; 256200 / 256000 = 1.0008 |
| quote | System logic cells 256K \| DSP slices 1.2K ; System Logic Cells \| 192,150 \| 256,200 \| 504,000 ; DSP Slices \| 728 \| 1,248 \| 1,728 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Both readings are recorded because they lead to different downstream arithmetic. Only the DSP one matters: a roofline built on 1,200 DSP is 4% optimistic against 1,248. Use DS890's exact column for any capacity claim and DS986's rounded vector only for prose. |

### V-01-20 · Gth Transceiver Max Rate

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `gth_transceiver_max_rate` |
| value | `16.3 Gb/s device-level; 12.5 Gb/s in the SFVC784 and SFVE784 packages` |
| unit | `Gb/s per lane` |
| conditions | `ZU5EV GTH transceivers; the KV260 SOM's device is marked SFVC784 (V-01-01)` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.22, Table 23, row 'GTH Transceiver 16.3 Gb/s(3)' and note (3) to that table |
| quote | GTH Transceiver 16.3 Gb/s(3) \| 16 \| 16 \| 24 ... 3. GTH transceivers in the SFVC784 and SFVE784 packages support data rates up to 12.5 Gb/s. See Table 24. |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | TWO READINGS, both printed on the same page, and they do not contradict each other: 16.3 Gb/s is the capability of the 16 GTH transceivers the silicon contains, 12.5 Gb/s is what the 784-ball packages route out. For KV260 planning the governing number is 12.5 Gb/s, because the SOM's device is marked SFVC784. A link budget built on 16.3 Gb/s describes a package this board does not have. |

### V-01-21 · Kv260 Package Gth Bondout

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `kv260_package_gth_bondout` |
| value | `4 GTH, 0 GTY in SFVC784` |
| unit | `transceivers` |
| conditions | `ZU5EV-class device in the SFVC784 package, at up to 12.5 Gb/s` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | p.23, Table 24 'EV Device-Package Combinations and Maximum I/Os', SFVC784 row, ZU5EV column, 'GTH, GTY' sub-column (value '4, 0'); note (5) to that table |
| quote | SFVC784(5) ... GTH, GTY ... 4, 0 ... 5. GTH transceivers in the SFVC784 and SFVE784 packages support data rates up to 12.5 Gb/s. |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Table 24 is a 13-column table whose values interleave unreliably in extracted linear text, so this cell was located by coordinate extraction: the header 'ZU5EV' sits at x=353 and the pair '4, 0' at x=360, between ZU4EV (x=216) and ZU7EV (x=491). Read with V-01-20: the device contains 16 GTH transceivers, this package bonds out 4, each capped at 12.5 Gb/s. |

### V-01-22 · On Chip Fabric Sram In Each Unit

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `on_chip_fabric_sram_in_each_unit` |
| value | `23,616 Kb = 2,952 KB = 2.8828 MiB = 3.02 MB decimal; 3.13 MiB if the 256 KB PS OCM is included` |
| unit | `bytes` |
| conditions | `144 BRAM36 tiles + 64 URAM288 tiles; the unit collision is the point` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10) & DS891 (v1.9)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | DS890 p.22 Table 23 block counts and DS891 v1.9 p.8 Table 5 sizes; arithmetic: 23616 / 8 = 2952; 2952 / 1024 = 2.8828; 2952 * 1024 / 1000000 = 3.02; (2952 + 256) / 1024 = 3.13 |
| quote | Block RAM Blocks 144 ; UltraRAM Blocks 64 ; 144 * 36 Kb + 64 * 288 Kb = 23,616 Kb ; 256 KB On-Chip Memory w/ECC |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | This record exists because '4 MB' and '4.5 MB' were each defensible under some unit reading and neither survives arithmetic (C-01). 3.02 MB decimal and 2.8828 MiB are the same bytes; plan-v2 SS3.3 writes 3.02 MB, which is right only if MB is read as 1,000,000. The 256 KB PS OCM term is a family-wide merged cell (V-01-17), not ZU5EV-specific, and it is not in the DPU address space. |

### V-01-23 · Bram And Uram Tile Size

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `bram_and_uram_tile_size` |
| value | `BRAM tile 36 Kb, URAM tile 288 Kb; the Mb columns are 1024-based` |
| unit | `Kb per tile` |
| conditions | `solved from DS891's printed total sizes against DS890's printed block counts` |
| source_tier | `T1` |
| doc_id | `DS890 (v4.10) & DS891 (v1.9)` |
| title | UltraScale Architecture and Product Data Sheet: Overview |
| url | https://docs.amd.com/v/u/en-US/ds890-ultrascale-overview |
| locator | DS891 v1.9 p.8 Table 5 (XCZU5EV total Block RAM 5,184 KB, total UltraRAM 18,432 KB) against DS890 p.22 Table 23 block counts; arithmetic: 5184 / 144 = 36; 18432 / 64 = 288; 144 * 36 / 1024 = 5.0625; 64 * 288 / 1024 = 18.0; 288 * 288 / 1024 = 81.0 |
| quote | Block RAM (Mb) \| 4.5 \| 5.1 \| 11.0 ; UltraRAM (Mb) \| 13.5 \| 18.0 \| 27.0 |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | WHY THIS IS A DERIVATION AND NOT AN ASSUMPTION: 144 blocks x 36 Kb / 1024 = 5.0625, which DS890 prints rounded to 5.1, and 64 x 288 / 1024 = 18.0 exactly. The last statement is the control group: the KU19P row of DS890 Table 9 prints 288 URAM blocks and 81.0 Mb, and 288 x 288 / 1024 is exactly 81.0, which fixes the column as 1024-based rather than 1000-based. One row across the family does not reconcile: ZU3TEG's 48 URAM blocks against its printed 14.0 Mb would imply a 298 Kb tile. It is a lone exception among the rows tested and no record here depends on it. |
