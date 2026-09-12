# Verification Evidence Index

This directory contains primary-source evidence collected per `docs/WEB_SEARCH_PROTOCOL.md` to resolve hardware and model parameter questions in `plan-v2.md`.

The initial pass ran on 2026-09-12 and wrote 71 records. A second review re-read every
`verified` record against its own `quote` field and corrected 28 of them, added 7, and raised a
fourth conflict. See [Audit of 2026-09-12](#audit-of-2026-09-12) for what was wrong and how it was
checked. **No record here is marked done or final; nothing in this directory has been applied to
`plan.md`, `plan-v2.md`, or `book/`.**

## Summary

- **Total Records:** 78
- **Verified:** 72
- **Unresolved:** 4
- **Conflict (records in `status: conflict`):** 2
- **Conflicts registered:** 4 (C-01 … C-04; two of them are against repository text and carry no
  `status: conflict` record — see [Conflicts](#conflicts))
- **Machine-readable claims:** [`claims.json`](claims.json) (`version` 1.1.0, `generated_utc` 2026-09-12T07:18:00Z, includes an `audit` block)

## Record Files

1. [`01-fpga-kv260-zu5ev.md`](01-fpga-kv260-zu5ev.md) — 17 records. Exact hardware resource counts for Kria KV260 (XCK26 / ZU5EV), clocking, on-chip SRAM capacity (BRAM, URAM, LUTRAM, PS OCM), and the DDR4 subsystem.
2. [`02-jetson-orin-skus.md`](02-jetson-orin-skus.md) — 28 records. Jetson Orin per-SKU specification matrix (Orin Nano 4GB/8GB/Super, Orin NX 8GB/16GB, AGX Orin 32GB/64GB, nvpmodel power modes).
3. [`03-kv260-audio-path.md`](03-kv260-audio-path.md) — 5 records. Audio input evaluation for the KV260 carrier card (PMOD I2S2 Digilent SKU 410-379 vs USB Audio).
4. [`04-toolchain-versions.md`](04-toolchain-versions.md) — 9 records. Vivado ML Standard device support, disk footprint, Vitis AI DPU overlay architecture (DPUCZDX8G) and its measured footprint on KV260-class silicon, and XPE accuracy caveats.
5. [`05-models-and-datasets.md`](05-models-and-datasets.md) — 9 records. Model architectures (MatchboxNet vs Streaming Conformer), licenses (Speech Commands v2, LibriSpeech CC BY 4.0), streaming chunk latency, and speaker-independent splits.
6. [`06-quantization-sources.md`](06-quantization-sources.md) — 5 records. Primary mathematical source for affine zero-point quantization (Jacob et al. CVPR 2018), integer multiply-shift requantization, the rounding operator Brevitas actually defaults to, FINN framework scope clarification.
7. [`07-related-work.md`](07-related-work.md) — 5 records. Roofline model formulation (Williams et al. CACM 2009), Orin vs KV260 ridge points, and IEEE FCCM 2025 artifact evaluation requirements.

---

## Conflicts

### C-01 · On-Chip SRAM Capacity on Kria KV260
- Existing claim A: "chỉ khoảng 4 MB trên Kria KV260" — `plan.md:55` — value 4 MB
- Existing claim B: "144 BRAMs and 64 URAMs, providing ~4.5 MB on-chip memory" — `docs/research_notes/R02_fpga_audio_streaming.md:23` — value ~4.5 MB
- Computed from verified block counts: 144 BRAM36 (5,184 Kb) + 64 URAM288 (18,432 Kb) = 23,616 Kb = 2,952 KB ≈ 2.8828 MiB (or 3.13 MiB if 256 KB PS OCM is included).
- New verified source: V-01-05, V-01-07, V-01-11 (DS890 v4.10 p.22 Table 23, DS891 v1.9 p.8 Table 5, DS986 v1.3 Product Details)
- Resolution proposed: Replace all references to 4 MB or 4.5 MB with 2.88 MiB (23,616 Kb) fabric SRAM. Acknowledge that neither 4 MB nor 4.5 MB has any silicon basis.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: V-01-11

### C-02 · Affine / Asymmetric Quantization Theoretical Foundation
- Existing claim: Cites FINN [R01-02] for affine quantization theory `r = S(q - Z)` — `plan.md:58`
- New verified source: V-06-01, V-06-02 (Jacob et al., CVPR 2018, arXiv:1712.05877 p.3 Equation 1) and V-06-03 (Umuroglu et al., ACM FPGA 2017, arXiv:1612.07119)
- Analysis: FINN is a framework for Binarized Neural Networks (1-bit XNOR-popcount) and sub-8-bit streaming dataflow. The affine asymmetric zero-point mapping `r = S(q - Z)` and integer-only multiply-shift requantization were formulated by Jacob et al. (CVPR 2018).
- Resolution proposed: Re-anchor affine quantization citations in the book and plan to Jacob et al. (CVPR 2018), and retain FINN strictly for streaming spatial dataflow principles.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: none. The conflicting text lives in `plan.md` / `docs/research_notes/`, which protocol rule 7 forbids this directory from editing, so no record here carries a contradicting value.

### C-03 · MatchboxNet Benchmark Metric
- Existing text: Mentions WER in the context of MatchboxNet evaluation — `plan.md`
- New verified source: V-05-01, V-05-02 (Majumdar et al., Interspeech 2020, arXiv:2004.08531)
- Analysis: MatchboxNet is an isolated keyword spotter / speech command classifier evaluated on Google Speech Commands (12 or 35 classes), reporting top-1 classification accuracy (97.21% - 97.48%). It does not output token sequences and has no Word Error Rate (WER).
- Resolution proposed: Separate metrics cleanly in the plan: Top-1 Classification Accuracy (%) for KWS (MatchboxNet), and Word Error Rate (WER %) strictly for continuous streaming ASR (Conformer).
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: none, for the same reason as C-02.

### C-04 · DPUCZDX8G B4096 Resource Footprint on KV260-Class Silicon
- Existing claim (now withdrawn as evidence): V-04-04 recorded 37,266 LUT / 92,630 FF / 642 DSP / 249.5 BRAM for DPUCZDX8G B4096, attributed to "PG338 Table 11".
- Why withdrawn: PG338 v4.1 (Release_Date 2023-01-23) contains no Table 11 and no `Resources for Different DSP Usage` caption, and none of 37266 / 92630 / 642 / 249.5 appears anywhere in the document. The numbers cannot be reproduced from the cited revision.
- Replacement evidence: V-04-07 (PG338 v4.1 Table 1, B4096 on ZCU102: 52161 LUT / 98249 FF / **255 BRAM** / 710 DSP) and V-04-08 (Table 2, UltraRAM variant on ZCU104: 51843 LUT / 98567 FF / 0 BRAM / **68 URAM** / 710 DSP).
- Feasibility consequence (V-04-09): the B4096 as tabulated **does not fit** ZU5EV / XCK26. 255 BRAM exceeds the 144 available, and 68 URAM exceeds the 64 available; DSP is the only resource with headroom (710 of 1,248).
- Unresolved sub-question: **which DPU core configuration the KV260 overlay actually ships is established by no record in this directory.** V-04-03 evidences the IP name `DPUCZDX8G`, not the shipped arithmetic configuration. Read it off the running overlay (`dpu-sysfs` resource info, or the DPU XSA used by the PetaLinux rootfs) before any capacity claim in the plan is written as fact.
- Resolution proposed: strike the V-04-04 figures from any planning arithmetic; treat B4096 as unavailable on KV260 until the shipped configuration is measured; if a specific core count is needed for the book, measure it on hardware.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: V-04-04 (kept in place rather than deleted, per protocol rule 6)

---

## Unresolved Items

1. **V-02-28 · Project Selected Orin SKU**
   - Question: Which Jetson Orin SKU will be the experimental baseline?
   - Candidates: Orin Nano 8GB (low cost / edge), Orin NX 16GB (balanced 100 TOPS, 2x DLA), or AGX Orin 64GB (flagship 275 TOPS).
   - Reason unresolved: Requires project hardware decision by authors based on lab kit availability.

2. **V-03-04 · Digilent PMOD I2S2 Retail Price**
   - Recorded value: none (previously 19.99–24.99 USD, withdrawn — see audit class 5).
   - Reason unresolved: The quote in the record contained no price, and a re-fetch of the Digilent product page on 2026-09-12 returned HTTP 403. A vendor product page is tier T4, which protocol rule 2 does not admit as a sole source for a volatile retail figure.
   - To resolve: capture a DigiKey or Mouser order-page quote with its date, or reclassify price as a BOM decision rather than a verification record. The PMOD I2S2 part identity itself remains evidenced by V-03-02 and V-03-03.

3. **V-06-05 · torch.round Tie-Breaking Mode**
   - Recorded value: none.
   - Reason unresolved: The PyTorch page formerly relied upon (`torch.ao.quantization.quantize_per_tensor`) returned HTTP 404 in this session, and no live PyTorch text was captured, so no tie-breaking rule is asserted here.
   - To resolve: read the rule from a live PyTorch page or from ATen's rounding implementation. This is not academic: bit-exact parity between the QAT software path (Brevitas `RoundSte`, evidenced in V-06-04) and an RTL fixed-point pipeline depends on the software tie rule matching whatever `+ (1 << (shift-1))` or truncation the RTL implements.

4. **V-07-05 · Published FPGA KWS Comparative Table**
   - Question: Unified comparative numbers (latency, power, energy/frame, LUT/DSP) across published FPGA speech accelerators on Google Speech Commands.
   - Reason unresolved: Deferred pending systematic survey across MLPerf Tiny and ACM FPGA/FCCM papers with matching benchmark conditions.

---

## Audit of 2026-09-12

### What the method was

Every `verified` record was re-tested with one question: **could the text in `quote` produce the
number in `value`?** A record fails when its value is arithmetic, a recollection, or a number from a
different row of the same table. 17 records failed that test; the ones flagged below as false
positives failed only because their value is legitimately derived or is a citation year.

Where a record failed, the underlying document was fetched again and read directly, in this session:

- `DS890 (v4.10)`, `DS-11105-001`, `DS-10712-001_v1.0`, `DS-10662-001v1.8` — downloaded as PDFs and
  parsed locally with PyMuPDF, so every quoted sentence was read out of the file rather than recalled.
- `DS986 (v1.3)` Product Details and `PG338 (v4.1)` Resource Utilization — live AMD deep links
  (`docs.amd.com/r/en-US/<slug>/<Section>`; the plain landing pages return only a JS shell).
- Brevitas `master` — read through the GitHub contents API (`raw.githubusercontent.com` 404s on this repo).

Whole-document search was used to prove absence, not just presence: `930.75` and `1301` occur nowhere
in the 56-page AGX Orin datasheet, and PG338 v4.1 has no Table 11.

### Defect classes found

1. **Arithmetic presented as a datasheet reading** — V-02-02, V-02-06, V-02-14, V-02-18. Bus width ×
   data rate was computed (34.1 / 68.2 / 102.4 GB/s) and recorded against a p.1 quote that prints no
   bandwidth. All four datasheets state the figure outright: 34, 68, 102, and "up to" 204.8 GB/s.
2. **Values from the wrong row of a family table** — V-02-21. "92–98 TOPS" spanned three different
   products: 92 is JAOi, 98 is JAO 32GB, 105 is JAO 64GB.
3. **Numbers that do not exist in the cited document** — V-02-20 (930.75 MHz), V-02-24 (1301 MHz),
   V-04-04 (all four figures). Corrected to 939 MHz and 1.3 GHz from p.7; V-04-04 is C-04.
4. **Wrong locator for a correct value** — V-02-20, V-02-24 pointed at p.10–11, where the GPU table
   lists only GPC/TPC and TOPS; core counts are on p.7.
5. **A value with no source inside the record** — V-03-04 (retail price), now `unresolved`.
6. **A correct value with a partial quote** — V-02-11 (quote widened to show the 15W mode, not only
   the 25W default), V-05-06 (both WERs now visible in one excerpt).
7. **A fabricated derived quantity** — V-05-05 carried a "0ms rightaway / future context" token that
   appears in no fetched document. Removed; 640 ms is now labelled as arithmetic on the published
   chunk size, and right-away latency in milliseconds stays unverified.
8. **A claim resting on a quote that supports less than the value** — V-01-02 asserted the exact part
   `XCZU5EV` from a quote naming only "an AMD Zynq UltraScale+ MPSoC based silicon device". Re-scoped
   to the family; the part-level identification is now V-01-15, stated as an inference.
9. **An unsourced library behaviour attributed to a tool** — V-06-04 asserted "Round-half-to-even
   (PyTorch/Brevitas)" on the strength of a `torch.round` page that says nothing about what a QAT
   library uses. Now evidenced from Brevitas itself; the inherited tie rule is separated out as V-06-05.
10. **Doc revisions named inaccurately** — V-01-03 … V-01-09 cited "DS890 (v4.9)"; the PDF is v4.10
    (21 May 2026). Re-read from v4.10; no value changed.
11. **Markdown broken by the evidence itself** — 26 records contained raw `|` inside `quote`, which
    split their own table rows mid-sentence. Now escaped at render time.

### Resources the original pass missed

- **V-01-16** — Distributed RAM (LUTRAM): 3.5 Mb = 448 KiB. Not part of the 23,616 Kb budget in
  V-01-11, and it costs LUTs rather than being free.
- **V-01-17** — PS On-Chip Memory: 256 KB with ECC. Reachable from the PL over AXI, but not fabric
  SRAM and not in the DPU address space; keep it out of the weight budget.
- **V-01-15** — the XCK26 ↔ ZU5EV identification, made explicit as an inference instead of a fact.
- **V-04-07 / V-04-08 / V-04-09** — the DPU footprint that actually fits on KV260-class silicon,
  which the B4096 as published does not.

### Open defect: mirror URLs, not vendor URLs

26 records point at third-party mirrors of vendor documents rather than at the vendor host:
`connecttech.com` (8), `files.waveshare.com` (9), `static.generation-robots.com` (8),
`hthreads.github.io` (1). **Only 10 of the 26 carry a note saying so.** The 16 that do not are all
NVIDIA records — V-02-01, V-02-03, V-02-04, V-02-05, V-02-07, V-02-08, V-02-12, V-02-13, V-02-15,
V-02-16, V-02-17, V-02-19, V-02-23, V-02-25, V-02-27, and V-07-02 — so a reader of those records
alone cannot tell that the URL is not NVIDIA's own. Replace all 26 with `docs.nvidia.com` /
`docs.amd.com` URLs before any of this is cited in the book. Writing the caveat note into those 16
records is deliberately left undone here: it touches records whose evidence is otherwise sound, and
the approved scope of this pass was to correct evidence that was wrong, not to relabel evidence that
is merely awkwardly hosted. Three Orin records already point at `docs.nvidia.com` directly. Four
records point at `raw.githubusercontent.com`, which is canonical for repository content and is fine.

### What this audit deliberately did not do

Per protocol rule 7, nothing was changed in `plan.md`, `plan-v2.md`, or `book/`. Every resolution
above is `needs-human-decision`. Note that `plan-v2.md` §3.3 currently writes the fabric SRAM figure
as "3.02 MB", which is the same quantity as 2.8828 MiB in decimal megabytes — the table is not wrong,
but the unit is ambiguous and C-01 is where that gets settled.
