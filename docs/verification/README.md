# Verification Evidence Index

This directory contains primary-source evidence collected per `docs/WEB_SEARCH_PROTOCOL.md` to resolve
hardware and model parameter questions in `plan-v2.md`.

Five passes ran on 2026-09-12. The initial pass wrote 71 records. The first review re-read every
`verified` record against its own `quote` field and corrected 28, added 7, and raised a fourth conflict.
The second pass went the other way: it re-read the underlying documents to settle what the first review
had left asserted rather than evidenced, added 18 records, and raised a fifth conflict. The third pass
audited provenance fields instead of values: it tiered three derived quantities as derived, titled three
records that had no title, and raised a sixth conflict about which revision of one NVIDIA datasheet ten
records actually cite. The fourth pass tested whether the vendor hosts those documents at all;
for the Orin NX datasheet it does, and re-pointing eleven records at NVIDIA's own copy moved
nine quotations, two page locators and two values. See
[Audit of 2026-09-12](#audit-of-2026-09-12).

**No record here is marked done or final; nothing in this directory has been applied to `plan.md`,
`plan-v2.md`, or `book/`.**

## Summary

- **Total Records:** 101
- **Verified:** 94
- **Unresolved:** 4
- **Conflict (records in `status: conflict`):** 3
- **Conflicts registered:** 7 (C-01 … C-07; three of them concern repository text or record provenance
  rather than a contested value, so they carry no `status: conflict` record — see
  [Conflicts](#conflicts)). One is now closed: the owner decided C-07 on 2026-09-12 in favour
  of `MAXN`. Closing it changed which operating point the book teaches, not what either record
  says, so no record was deleted or re-typed.
- **Machine-readable claims:** [`claims.json`](claims.json) (`version` 1.5.0, `generated_utc`
  2026-09-12T15:55:00Z, includes an `audit` block describing the two value-level passes, the two
  provenance passes and the decision package that closed C-07)
- **Checks:** `make verify-evidence` runs the auditor over this directory;
  `make render-evidence` regenerates the seven record files from `claims.json`.

## Record Files

1. [`01-fpga-kv260-zu5ev.md`](01-fpga-kv260-zu5ev.md) — 23 records. Exact hardware resource counts for
   Kria KV260 (XCK26 / ZU5EV), clocking, on-chip SRAM capacity (BRAM, URAM, LUTRAM, PS OCM) and the tile
   sizes behind them, the DDR4 subsystem, and the GTH transceiver rate as it differs between device and
   package.
2. [`02-jetson-orin-skus.md`](02-jetson-orin-skus.md) — 41 records. Jetson Orin per-SKU specification
   matrix (Orin Nano 4GB/8GB/Super, Orin NX 8GB/16GB, AGX Orin 32GB/64GB, nvpmodel power modes), the
   sparse-versus-dense TOPS pair for every SKU, the memory-clock convention, and how a module TOPS
   figure decomposes into GPU plus DLA.
3. [`03-kv260-audio-path.md`](03-kv260-audio-path.md) — 5 records. Audio input evaluation for the KV260
   carrier card (PMOD I2S2 Digilent SKU 410-379 vs USB Audio).
4. [`04-toolchain-versions.md`](04-toolchain-versions.md) — 13 records. Vivado ML Standard device
   support, disk footprint, Vitis AI DPU overlay architecture (DPUCZDX8G), the full PG338 resource
   ladders for both the Block RAM and UltraRAM variants, what of those ladders fits ZU5EV, and XPE
   accuracy caveats.
5. [`05-models-and-datasets.md`](05-models-and-datasets.md) — 9 records. Model architectures (MatchboxNet
   vs Streaming Conformer), licenses (Speech Commands v2, LibriSpeech CC BY 4.0), streaming chunk
   latency, and speaker-independent splits.
6. [`06-quantization-sources.md`](06-quantization-sources.md) — 5 records. Primary mathematical source
   for affine zero-point quantization (Jacob et al. CVPR 2018), integer multiply-shift requantization,
   the rounding operator Brevitas actually defaults to, the tie rule `torch.round` documents, and FINN
   framework scope clarification.
7. [`07-related-work.md`](07-related-work.md) — 5 records. Roofline model formulation (Williams et al.
   CACM 2009), Orin vs KV260 ridge points, and IEEE FCCM 2025 artifact evaluation requirements.

---

## Ambiguous Quantities — Both Readings

Some numbers below are not wrong; they are ambiguous, and a record that stores a single value silently
picks one reading. Each of these is recorded with **both** values and an explanation of when each
applies, because choosing between them changes downstream arithmetic.

| Quantity | Reading A | Reading B | Which governs, and why | Record |
|---|---|---|---|---|
| KV260 GTH transceiver rate | 16.3 Gb/s | 12.5 Gb/s | Both are printed on the same DS890 page. 16.3 is what the silicon's 16 GTH transceivers can do; 12.5 is what the SFVC784 package the SOM uses bonds out, and it bonds out 4 of them. A link budget for this board uses 12.5. | V-01-20, V-01-21 |
| KV260 fabric SRAM size | 2.8828 MiB | 3.02 MB | Same bytes. 23,616 Kb = 2,952 KB; divide by 1024 for binary MiB, by 1,000,000 bytes for decimal MB. `plan-v2.md` §3.3 writes "3.02 MB", which is correct only if MB means 10⁶. Neither 4 MB nor 4.5 MB is either reading — see C-01. | V-01-22 |
| …including the PS OCM or not | 2.8828 MiB (fabric only) | 3.13 MiB (fabric + 256 KB OCM) | The OCM is reachable from the PL over AXI but is not fabric SRAM and is not in the DPU address space. Keep it out of a weight budget; mention it only for a total on-chip figure. | V-01-22, V-01-17 |
| DS890 `Block RAM (Mb)` column basis | 1000-based | 1024-based | Solved rather than assumed: 144 tiles × 36 Kb ÷ 1024 = 5.0625, printed as 5.1, and the KU19P control row gives 288 × 288 ÷ 1024 = 81.0 exactly. The column is 1024-based. One row (ZU3TEG) does not reconcile and nothing here depends on it. | V-01-23 |
| NVIDIA datasheet "MHz" for LPDDR5 | memory clock (CK), so data rate = 2 × MHz | data rate, single-pumped | The clock reading reproduces all four printed bandwidth figures; the single-pump reading reproduces none and assigns the 4 GB Nano's bandwidth to the 8 GB module. Printed MHz is the clock on every Orin datasheet here. Contrast K26, where DS987's "2400 Mb/s" is already a data rate and no doubling applies. | V-02-34, V-02-35, V-01-13 |
| Orin INT8 TOPS | sparse | dense | Differ by exactly 2× on every SKU, which is NVIDIA's own factor: the Ampere whitepaper states structured sparsity "doubles throughput". Marketing headlines and this project's plan always quote sparse, so a network that is not 2:4 pruned should be planned against the dense number. | V-02-29, V-02-30, V-02-31 |
| KV260 resource counts | 256K / 1.2K (DS986 marketing) | 256,200 / 1,248 (DS890 exact) | The rounded vector understates DSP by 4%, which is the one rounding that matters for a roofline. Use DS890's exact column for capacity, DS986's rounded figures for prose. | V-01-15, V-01-18, V-01-19 |
| Orin NX 16 GB "100 TOPS" | 100 as a module figure | 60 GPU + 40 DLA | The datasheet prints 100 and 20-per-engine-DLA but never 60. The split is derived (T2), and it matters because a roofline that lets the GPU claim use all 100 double-counts up to 40% of the module. | V-02-36 |
| PG338 `Block RAM` / `UltraRAM` columns | count of tiles | volume | PG338 never defines the unit, which is why "255 Block RAM" reads as smaller than ZU5EV's "144" until you know both are tile counts of 36 Kb and 288 Kb tiles respectively. | V-04-10, V-04-11, V-01-23 |
| Rounding a tie (x.5) | round half to even (`round(2.5)` → 2) | round half away from zero (`+ (1 << (shift-1))`) | PyTorch documents the first, Brevitas defaults to `RoundSte`, and an RTL fixed-point pipeline usually implements the second. Three tie behaviours across one toolchain is a bit-exactness trap, not a style choice. | V-06-05, V-06-04 |
| AGX Orin 32 GB DLA TOPS | 92 | 98 | Same datasheet, three pages, two answers, and only 92 makes the module total add up. Recorded as a conflict rather than resolved by preference — see C-05. | V-02-33 |

Two of these became conflicts with a `needs-human-decision` resolution (C-01 and C-05). The rest are
recorded as settled readings with the rejected reading kept visible, because a reader who meets the
other number in a vendor page should be able to see why it differs.

---

## Conflicts

### C-01 · On-Chip SRAM Capacity on Kria KV260
- Existing claim A: "chỉ khoảng 4 MB trên Kria KV260" — `plan.md:55` — value 4 MB
- Existing claim B: "144 BRAMs and 64 URAMs, providing ~4.5 MB on-chip memory" —
  `docs/research_notes/R02_fpga_audio_streaming.md:23` — value ~4.5 MB
- Computed from verified block counts: 144 BRAM36 (5,184 Kb) + 64 URAM288 (18,432 Kb) = 23,616 Kb =
  2,952 KB ≈ 2.8828 MiB (or 3.13 MiB if 256 KB PS OCM is included). The tile sizes that make that
  addition legal are now established by V-01-23 rather than assumed.
- New verified source: V-01-05, V-01-07, V-01-11 (DS890 v4.10 p.22 Table 23, DS891 v1.9 p.8 Table 5,
  DS986 v1.3 Product Details); unit readings enumerated in V-01-22.
- Resolution proposed: Replace all references to 4 MB or 4.5 MB with 2.88 MiB (23,616 Kb) fabric SRAM.
  Acknowledge that neither 4 MB nor 4.5 MB has any silicon basis.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: V-01-11

### C-02 · Affine / Asymmetric Quantization Theoretical Foundation
- Existing claim: Cites FINN [R01-02] for affine quantization theory `r = S(q - Z)` — `plan.md:58`
- New verified source: V-06-01, V-06-02 (Jacob et al., CVPR 2018, arXiv:1712.05877 p.3 Equation 1) and
  V-06-03 (Umuroglu et al., ACM FPGA 2017, arXiv:1612.07119)
- Analysis: FINN is a framework for Binarized Neural Networks (1-bit XNOR-popcount) and sub-8-bit
  streaming dataflow. The affine asymmetric zero-point mapping `r = S(q - Z)` and integer-only
  multiply-shift requantization were formulated by Jacob et al. (CVPR 2018).
- Resolution proposed: Re-anchor affine quantization citations in the book and plan to Jacob et al.
  (CVPR 2018), and retain FINN strictly for streaming spatial dataflow principles.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: none. The conflicting text lives in `plan.md` /
  `docs/research_notes/`, which protocol rule 7 forbade this directory from editing until it was
  retired on 2026-09-12, so at the time of writing no record here
  carries a contradicting value.

### C-03 · MatchboxNet Benchmark Metric
- Existing text: Mentions WER in the context of MatchboxNet evaluation — `plan.md`
- New verified source: V-05-01, V-05-02 (Majumdar et al., Interspeech 2020, arXiv:2004.08531)
- Analysis: MatchboxNet is an isolated keyword spotter / speech command classifier evaluated on Google
  Speech Commands (12 or 35 classes), reporting top-1 classification accuracy (97.21% - 97.48%). It
  does not output token sequences and has no Word Error Rate (WER).
- Resolution proposed: Separate metrics cleanly in the plan: Top-1 Classification Accuracy (%) for KWS
  (MatchboxNet), and Word Error Rate (WER %) strictly for continuous streaming ASR (Conformer).
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: none, for the same reason as C-02.

### C-04 · DPUCZDX8G B4096 Resource Footprint on KV260-Class Silicon
- Existing claim (now withdrawn as evidence): V-04-04 recorded 37,266 LUT / 92,630 FF / 642 DSP / 249.5
  BRAM for DPUCZDX8G B4096, attributed to "PG338 Table 11".
- Why withdrawn: PG338 v4.1 (Release_Date 2023-01-23) contains no Table 11 and no `Resources for
  Different DSP Usage` caption, and none of 37266 / 92630 / 642 / 249.5 appears anywhere in the
  document. The numbers cannot be reproduced from the cited revision.
- Replacement evidence: the full ladders are now transcribed rather than sampled — V-04-10 (Table 1,
  Block RAM variant, ZCU102, eight architectures) and V-04-11 (Table 2, UltraRAM variant, ZCU104, eight
  architectures). The B4096 rows specifically are V-04-07 and V-04-08.
- Feasibility consequence (V-04-09, re-tiered to T2 on the second pass because a comparison of two
  records is derived evidence): the B4096 as tabulated **does not fit** ZU5EV / XCK26. 255 Block RAM
  tiles exceed the 144 available and 68 URAM tiles exceed the 64 available; DSP is the only resource
  with headroom (710 of 1,248). The largest core of each variant that does fit is B1600 (126 of 144
  BRAM) and B3136 (64 of 64 URAM, exactly full, so B2304 at 60 is the largest with headroom) — V-04-12.
- Unresolved sub-question: now its own record. **V-04-13** carries
  `kv260_shipped_dpu_core_architecture` as `unresolved`, with the primary-source attempts that failed
  and the mutually inconsistent tier-T5 evidence that remains. V-04-03 evidences the IP name
  `DPUCZDX8G`, not the shipped arithmetic configuration.
- Resolution proposed: strike the V-04-04 figures from any planning arithmetic; treat B4096 as
  unavailable on KV260 until the shipped configuration is measured; if a specific core count is needed
  for the book, measure it on hardware.
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: V-04-04 (kept in place rather than deleted, per protocol rule 6)

### C-05 · Jetson AGX Orin 32 GB DLA TOPS
- Reading A (92): DS-10662-001v1.8 p.8 states "JAO 32GB: Maximum Operating Frequency: 1.4 GHz | 46 TOPs
  each (Sparse INT8)" for a 2× NVDLA 2.0 configuration, so 2 × 46 = 92; p.10 states 92 outright.
- Reading B (98): the same document, p.12, states "JAO 32GB: Up to 98 INT8 Sparse TOPS (Deep Learning
  Inference)". This is the row V-02-21 quotes.
- Discriminating evidence: p.7 prints the module total as "Up to 200 Sparse TOPs (INT8)" and the GPU
  figure as 108. V-02-32 demonstrates for two other SKUs that the module total is the sum of the printed
  GPU and DLA figures (156 + 92 = 248, 170 + 105 = 275). That additivity holds for the 32 GB SKU under
  reading A only: 108 + 92 = 200, which is the printed total, while 108 + 98 = 206 appears nowhere in
  the document.
- Position of this directory: reading A is better supported and 98 is most likely an editorial slip on
  p.12 — but the value is **not adopted**, because that would be this directory choosing over a
  datasheet. Both readings are carried in V-02-33.
- Also corrected here: the first-pass note on V-02-21 asserted "92 is JAOi" as though that disposed of
  the 32 GB SKU. It does not. 92 is printed for the 32 GB SKU too, on p.10 and per-engine on p.8. The
  note has been amended to say so.
- Resolution proposed: measure DLA throughput on hardware for a 2:4-pruned network at 1.4 GHz, or ask
  NVIDIA which page is current. Meanwhile quote "92 (datasheet also prints 98 on p.12)".
- Resolution status: `needs-human-decision`
- Record in `status: conflict`: V-02-33

### C-06 · Which Revision of DS-11105-001 Backs Ten Records
- Identity A: eight records cite `DS-11105-001_v1.1` — V-02-01, V-02-03, V-02-04, V-02-05, V-02-07,
  V-02-08, V-02-29, V-02-34 — read from the mirror copy at 2026-09-12T04:25Z and 12:00Z.
- Identity B: two records cite `DS-11105-001` with no revision — V-02-02 and V-02-06, read at 07:18Z —
  and their own notes state the reason: "DS-11105-001 carries no revision number on its cover and is
  stamped 'SUBJECT TO CHANGE | PRELIMINARY - ADVANCE INFORMATION'".
- Same URL in all ten: `https://connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf`. One file
  cannot be both revision 1.1 and an unnumbered preliminary, so either the distributor replaced the PDF
  between the two retrievals or one group recorded the revision wrong.
- Why this directory cannot settle it: on 2026-09-12 a direct fetch of that URL returned HTTP 403 with a
  5,547-byte HTML body — no PDF at all. Those ten records are not merely mirrored, they are currently
  unreachable, so the quoted text cannot be re-read from anything this directory holds.
- What is at stake is not a rounding difference. The two contested records are the Orin Nano memory
  bandwidths, 34 GB/s and 68 GB/s, which are the denominator of every roofline in chapter 7, and V-02-29
  and V-02-34 carry the TOPS ladder and the 2133 MHz unit reading.
- Position of this directory: both identities are kept, per protocol rule 6. Retiring one is a
  substitution, not a correction, and no record may be edited to make a provenance question disappear.
- Resolution proposed: fetch DS-11105-001 from its vendor host, read its cover, and set all ten
  records to the revision NVIDIA prints. **Measured 2026-09-12, and the route is not open:** the
  vendor equivalent of this document is
  `https://developer.nvidia.com/downloads/jetson-orin-nano-series-data-sheet`, which answers 302
  to `/login` — the host is `developer.nvidia.com`, not the `docs.nvidia.com` this section first
  assumed, and settling C-06 now needs an authenticated fetch or someone with NVIDIA access. If the vendor cover carries a revision, Identity B's note becomes wrong
  about the vendor document and must be amended to say it was true only of the mirror copy.
- Resolution status: `needs-human-decision`, though a vendor fetch rather than a judgement unblocks it —
  once the NVIDIA copy is readable the choice is mechanical.

### C-07 · Which Operating Point of the Orin NX the Book May Assume
- What the mirror (DS-10712-001_v1.0) printed, and what every one of these records was built on: the
  8 GB GPU tops out at 765 MHz and the 16 GB at 918 MHz; AI performance is 100 sparse / 50 dense INT8
  TOPS (16 GB) and 70 / 35 (8 GB); the mode lists are 10W, 15W, 20W and 10W, 15W, 25W.
- What the vendor (DS-10712-001_v1.7) prints: **all of those numbers, unchanged**, in a first column.
  Beside it stands a second column headed `MAXN_SUPER`, which prints 1,173 MHz on the Ampere GPU for
  both SKUs, 1,229 MHz on the DLA (80 TOPS on 16 GB, 40 TOPS on 8 GB), 157 sparse / 78 dense INT8 TOPS
  for the 16 GB and 117 / 58 for the 8 GB, and a fourth module mode of 40W. `MAXN_SUPER` additionally
  requires an 8V-20V supply where the module otherwise accepts 5V-20V.
- Why this is a conflict rather than an addition: the contested word is *maximum*. V-02-12 and V-02-16
  are records of a maximum operating frequency, and V-02-15 and V-02-19 of a power-mode list. Each was
  complete for the document it cited and each is incomplete for the module. Two records that cannot
  both be true of the hardware are being kept, per protocol rule 6.
- What is at stake for this project is the roofline, not a footnote. `plan-v2.md` takes 100 sparse INT8
  TOPS as the Orin NX ceiling, and V-07-02 divides 50 dense TOPS by 102 GB/s to get a ridge point of
  490.2 OP/byte. Under `MAXN_SUPER` the same division takes 78 TOPS over 102 GB/s, which is 764.7
  OP/byte. A chapter that tells a reader "Orin becomes compute-bound above roughly 490 OP/byte" is
  wrong by half for a profile it never names, and the port's whole premise — that a batch-of-one voice
  pipeline sits far below the ridge point — is stated in those units.
- Position of this directory: nothing is chosen. The eleven records that moved to the vendor keep their
  values and now name their profile in `conditions`; the five `MAXN_SUPER` figures are recorded as
  **V-02-37 … V-02-41** rather than substituted for anything.
- Resolution proposed: a human picks the operating point the book's arithmetic uses. `MAXN` is the
  defensible default for a portable voice product, because 40W and an 8V rail are exactly what a
  battery-powered carrier cannot promise, and because nvpmodel as read in the r36.4.4 guide names modes
  only up to 20W and 25W. Whichever is picked, `plan-v2.md` and the chapter 7 arithmetic must then be
  restated against it.
- **Resolution, 2026-09-12:** the repository owner chose **`MAXN`**. The book and `plan-v2.md`
  compute from the default operating point: 918 MHz on the 16GB GPU, 765 MHz on the 8GB, 100
  sparse / 50 dense INT8 TOPS on the 16GB, and module modes up to 25W. The ridge point the book
  teaches is therefore 490.2 OP/byte (V-07-02) and not 764.7.
  Three things follow from that choice and are recorded rather than assumed. The
  `MAXN_SUPER` records V-02-37 … V-02-41 stay in this directory unchanged, because rule 6
  outlaws overwriting a contradicting record and because they are true of the module: they
  describe what a carrier that can supply 40W and an 8V rail gets. A chapter may cite them as
  the upper profile, and must then name it. And `MAXN` is now an assumption that any measured
  Orin number has to be taken under, which is why `plan-v2.md` §3.1 writes it into the row for
  the power mode of measurement.
- Resolution status: `resolved-by-owner`, 2026-09-12
- Records involved: V-02-12, V-02-13, V-02-15, V-02-16, V-02-17, V-02-19, V-02-30, V-02-36, V-07-02,
  V-02-37, V-02-38, V-02-39, V-02-40, V-02-41


---

## Unresolved Items

1. **V-04-13 · KV260 shipped DPU core architecture**
   - Question: which DPUCZDX8G rung the KV260 factory PetaLinux image actually loads.
   - Reason unresolved: the AMD software-manual deep link
     `docs.amd.com/r/en-US/ug230-kv260-vision-software-manual/DPU` returns HTTP 404; code search across
     `org:Xilinx` for DPUCZDX8G returns compiler targets and examples rather than a KV260 designation;
     PG338 v4.1 names no Kria board. Third-party KV260 files disagree with each other (fingerprint
     `0x101000056010407` whose tail matches B4096, versus `DPUCZDX8G_ISA1_B3136` at 300 MHz, versus
     `_B4096` at 325 MHz), all tier T5 and therefore corroborating only under protocol rule 2 — and B4096
     as tabulated does not fit this device at all (V-04-09), so a B4096 fingerprint needs explaining
     rather than repeating.
   - To resolve: read `dpu-sysfs` `resource_info` and the fingerprint on a KV260 running the factory
     image, or open the DPU XSA the PetaLinux rootfs was built from. This is the one capacity question in
     the plan that documents cannot settle.

2. **V-02-28 · Project Selected Orin SKU**
   - Question: Which Jetson Orin SKU will be the experimental baseline?
   - Candidates: Orin Nano 8GB (low cost / edge), Orin NX 16GB (balanced 100 TOPS sparse / 50 dense, 2×
     DLA), or AGX Orin 64GB (flagship 275 TOPS sparse).
   - Reason unresolved: Requires project hardware decision by authors based on lab kit availability.

3. **V-03-04 · Digilent PMOD I2S2 Retail Price**
   - Recorded value: none (previously 19.99–24.99 USD, withdrawn — see audit class 5).
   - Reason unresolved: The quote in the record contained no price, and a re-fetch of the Digilent
     product page on 2026-09-12 returned HTTP 403. A vendor product page is tier T4, which protocol rule 2
     does not admit as a sole source for a volatile retail figure.
   - To resolve: capture a DigiKey or Mouser order-page quote with its date, or reclassify price as a BOM
     decision rather than a verification record. The PMOD I2S2 part identity itself remains evidenced by
     V-03-02 and V-03-03.

4. **V-07-05 · Published FPGA KWS Comparative Table**
   - Question: Unified comparative numbers (latency, power, energy/frame, LUT/DSP) across published FPGA
     speech accelerators on Google Speech Commands.
   - Reason unresolved: Deferred pending systematic survey across MLPerf Tiny and ACM FPGA/FCCM papers
     with matching benchmark conditions.

Resolved by the second pass and removed from this list: **V-06-05 · `torch.round` tie-breaking mode**,
now `verified` against the versioned PyTorch 2.14 URL. The first pass could not re-reach the page and so
asserted nothing; see the audit note on that record for the redirect-shell problem that caused it.

---

## Audit of 2026-09-12

### What the method was (first review)

Every `verified` record was re-tested with one question: **could the text in `quote` produce the number
in `value`?** A record fails when its value is arithmetic, a recollection, or a number from a different
row of the same table. 17 records failed that test; the ones flagged below as false positives failed only
because their value is legitimately derived or is a citation year.

Where a record failed, the underlying document was fetched again and read directly, in this session:

- `DS890 (v4.10)`, `DS-11105-001`, `DS-10712-001_v1.0`, `DS-10662-001v1.8` — downloaded as PDFs and
  parsed locally with PyMuPDF, so every quoted sentence was read out of the file rather than recalled.
- `DS986 (v1.3)` Product Details and `PG338 (v4.1)` Resource Utilization — live AMD deep links
  (`docs.amd.com/r/en-US/<slug>/<Section>`; the plain landing pages return only a JS shell).
- Brevitas `master` — read through the GitHub contents API (`raw.githubusercontent.com` 404s on this
  repo).

Whole-document search was used to prove absence, not just presence: `930.75` and `1301` occur nowhere in
the 56-page AGX Orin datasheet, and PG338 v4.1 has no Table 11.

### Defect classes found (first review)

1. **Arithmetic presented as a datasheet reading** — V-02-02, V-02-06, V-02-14, V-02-18. Bus width ×
   data rate was computed (34.1 / 68.2 / 102.4 GB/s) and recorded against a p.1 quote that prints no
   bandwidth. All four datasheets state the figure outright: 34, 68, 102, and "up to" 204.8 GB/s.
2. **Values from the wrong row of a family table** — V-02-21. "92–98 TOPS" spanned three different
   products: 92 is JAOi, 98 is JAO 32GB, 105 is JAO 64GB.
3. **Numbers that do not exist in the cited document** — V-02-20 (930.75 MHz), V-02-24 (1301 MHz),
   V-04-04 (all four figures). Corrected to 939 MHz and 1.3 GHz from p.7; V-04-04 is C-04.
4. **Wrong locator for a correct value** — V-02-20, V-02-24 pointed at p.10–11, where the GPU table lists
   only GPC/TPC and TOPS; core counts are on p.7.
5. **A value with no source inside the record** — V-03-04 (retail price), now `unresolved`.
6. **A correct value with a partial quote** — V-02-11 (quote widened to show the 15W mode, not only the
   25W default), V-05-06 (both WERs now visible in one excerpt).
7. **A fabricated derived quantity** — V-05-05 carried a "0ms rightaway / future context" token that
   appears in no fetched document. Removed; 640 ms is now labelled as arithmetic on the published chunk
   size, and right-away latency in milliseconds stays unverified.
8. **A claim resting on a quote that supports less than the value** — V-01-02 asserted the exact part
   `XCZU5EV` from a quote naming only "an AMD Zynq UltraScale+ MPSoC based silicon device". Re-scoped to
   the family; the part-level identification is now V-01-15, stated as an inference.
9. **An unsourced library behaviour attributed to a tool** — V-06-04 asserted "Round-half-to-even
   (PyTorch/Brevitas)" on the strength of a `torch.round` page that says nothing about what a QAT library
   uses. Now evidenced from Brevitas itself; the inherited tie rule is separated out as V-06-05.
10. **Doc revisions named inaccurately** — V-01-03 … V-01-09 cited "DS890 (v4.9)"; the PDF is v4.10 (21
    May 2026). Re-read from v4.10; no value changed.
11. **Markdown broken by the evidence itself** — 26 records contained raw `|` inside `quote`, which split
    their own table rows mid-sentence. Now escaped at render time.

### Resources the first pass missed

- **V-01-16** — Distributed RAM (LUTRAM): 3.5 Mb = 448 KiB. Not part of the 23,616 Kb budget in V-01-11,
  and it costs LUTs rather than being free.
- **V-01-17** — PS On-Chip Memory: 256 KB with ECC. Reachable from the PL over AXI, but not fabric SRAM
  and not in the DPU address space; keep it out of the weight budget.
- **V-01-15** — the XCK26 ↔ ZU5EV identification, made explicit as an inference instead of a fact.
- **V-04-07 / V-04-08 / V-04-09** — the DPU footprint that actually fits on KV260-class silicon, which
  the B4096 as published does not.

### Second pass (same day)

The first review asked whether a quote could produce its value. The second asked the harder question:
**where the first review had asserted a convention or a unit, could the document be read to prove it?**
Four things were settled by reading rather than reasoning, and one of the four overturned the first
review's own correction.

- DS890 v4.10 p.22 Table 23 and p.23 Table 24 re-read, including a package table whose 13 columns
  interleave unreliably in extracted linear text and had to be located by coordinate extraction.
- DS-10662-001v1.8 reconciled page by page (p.7 module totals, p.8 DLA engines, p.10 and p.12 tables),
  which is what turned a suspected typo into C-05.
- PG338 v4.1 Tables 1 and 2 transcribed in full rather than sampled, giving both variant ladders.
- `torch.round` re-fetched from the versioned `docs/2.14/` URL after the `/docs/stable/` URL returned only
  a "Redirecting…" shell — a trap worth knowing: a checker reading the stable URL sees no claim to check.

**What the second pass corrected:** V-01-11, V-01-13, V-01-15, V-02-17, V-02-21, V-04-09, V-05-05,
V-06-05, V-07-03.

1. **A value assembled from two documents, one of them mis-quoted** — V-01-15 carried DS986's marketing
   line as its quote while stating DS890's exact numbers (256,200 and 1,248) as its value. The value was
   right, the quote could not produce it, and the first review missed it because both pages print a
   number. Split into three records: exact column (V-01-15), marketing vector (V-01-18), and the
   difference between them (V-01-19).
2. **A convention asserted instead of solved** — V-01-23 establishes the 36 Kb / 288 Kb tile sizes and
   the 1024-based Mb column by making two printed numbers come out right, with the KU19P row of DS890
   Table 9 as a control. V-01-11's note pointed at it instead of resting on the assumption.
3. **Arithmetic that was real but undeclared** — V-01-13, V-02-17, V-05-05, V-07-03 now carry `arithmetic`
   clauses in `locator`, which the auditor evaluates rather than admires. Declaring a clause is the only
   way a record can be exempt from the printed-digit test, so an undeclared derivation looks identical to
   an unsourced one.
4. **A derived comparison filed as a datasheet fact** — V-04-09 lowered from T1 to T2. The comparison is
   unchanged and still holds; the tier was wrong because T1 means a datasheet says it.
5. **A correction that was itself wrong** — V-02-21's first-pass note asserted "92 is JAOi" and thereby
   dismissed the 98 it had just recorded for the 32 GB SKU. p.8 and p.10 print 92 for that SKU, and 92 is
   the only figure that makes the datasheet's own module total work. Both readings now live in V-02-33;
   the note on V-02-21 is amended. This is the defect the audit method cannot catch about itself: a
   reviewer who replaces one wrong page with another wrong page.
6. **Silent mirrors** — the 16 records that pointed at third-party hosts without saying so, plus the 8
   new records that would have inherited the same silence, are now self-declared. See below.

**What the second pass added:** 18 records — V-01-18 … V-01-23, V-02-29 … V-02-36, V-04-10 … V-04-13.

### Open defect: Mirror URLs, not vendor URLs

23 records point at third-party mirrors of vendor documents rather than at the vendor host:
`static.generation-robots.com` (12), `connecttech.com` (10), `hthreads.github.io` (1). Eleven
that cited `files.waveshare.com` for the Orin NX datasheet moved to NVIDIA's own copy on
2026-09-12; see [the fifth pass](#fifth-pass-the-orin-nx-records-moved-to-the-vendor-same-day). Every one of them now says so in its `notes` field, which was the second
acceptance criterion for this pass: a reader can no longer mistake the URL for NVIDIA's own.

**That is acknowledgement, not a fix.** The remaining work is to substitute `developer.nvidia.com`
URLs, and it is still open because a mirror is a copy of a document this directory cannot verify against the
original host — the quoted text was read out of the mirror copy, and only a re-fetch from NVIDIA can
confirm the mirror is unaltered.

The mirrors are not all still there. `connecttech.com/ftp/pdf/nvidia_jetson_orin_datasheet.pdf`, which
ten records cite, returned HTTP 403 to a direct fetch on 2026-09-12, so those ten are unreachable from
any host this directory trusts, and the ambiguity over which revision they hold is C-06.

**Substituting a vendor URL is not always possible, and that is now measured rather than assumed.**
V-04-02 cites the Vivado installation disk table for **2024.1**. The revision-pinned vendor path
`xilinx.com/support/documents/sw_manuals/xilinx2024_1/ug973-vivado-release-notes-install-license.pdf`
answers HTTP 404, while the same pattern for `xilinx2022_2` serves a 2,885,302-byte PDF — so the path
convention is right and AMD simply no longer publishes that revision there. `docs.amd.com` resolves the
guide only to UG973 **2026.1**, and `adaptivesupport.amd.com` requires a login. A 2024.1 figure pointed at
a 2026.1 URL would look vendor-backed and not be, so the mirror stays with its reason written into the
record.

**A trap for whoever finishes this list:** `docs.amd.com` returns HTTP 200 with the same 2,575-byte
JavaScript shell for every path, including paths that name no document at all. A 200 from that host proves
nothing about whether a page exists. Content has to be confirmed as rendered text, which is how the DS986
and PG338 deep links in this directory were read, and a bare status code must never be recorded as a
successful fetch. Four records point at `raw.githubusercontent.com`, which is canonical
for repository content and is fine. Several already point at `docs.nvidia.com` or `docs.amd.com`
directly. `make verify-evidence` fails if any mirror record loses its acknowledgement.
### Fifth pass: the Orin NX records moved to the vendor (same day)

The mirror defect kept asking a question nobody had tested: does NVIDIA host these PDFs where this
directory can reach them? For the Orin NX datasheet the answer turned out to be yes, and testing it
changed the records rather than just their URLs.

- **The fetch.** `https://developer.nvidia.com/downloads/jetson-orin-nx-module-series-data-sheet`
  answers 302 to a token-bearing URL on `developer.download.nvidia.com`, which serves HTTP 200,
  `application/pdf`, 753,138 bytes, 56 pages, cover stamped `DS-10712-001_v1.7 | February 2026`. The
  signed URL expires, so all eleven records cite the `developer.nvidia.com` form. Note that the
  original instruction for this defect named `docs.nvidia.com`, which is not where this document
  lives: `VENDOR_HOSTS` in `audit_claims.py` now lists `developer.nvidia.com` and
  `developer.download.nvidia.com` beside it.
- **Three of the eleven quotations did not survive the move**, and not because the values were wrong.
  Nine of the eleven v1.0 quotations do not appear as text in v1.7 at all. V-02-12 for instance
  "quoted" `ONX 8GB: Maximum Operating Frequency: 765 MHz`, which is a reconstruction of a table row:
  the vendor table prints the label `Maximum Operating Frequency (up to):` on one line and the bare
  cell `765 MHz` several lines away, with the SKU name in a third place. Every quote now in these
  records was checked cell by cell against the vendor text layer, and each printed page in each
  locator is the page that cell actually appears on (the PDF page is the printed page plus six).
- **Two locator defects and one value defect were found by that check.** The power-mode list is printed
  on p.3, not p.1 (V-02-15, V-02-19). The DLA table moved from p.1 to p.2 between revisions (V-02-13,
  V-02-17). V-02-17 had been read as printing "20 TOPS each"; v1.7 prints 40 TOPS for the `2x NVDLA`
  configuration and no per-engine figure anywhere, so the per-engine number is now declared arithmetic
  (`40 / 2 = 20`) instead of presented as a datasheet reading.
- **Two values changed.** Both mode lists gained a fourth entry, 40W (`MAXN_SUPER`). That is the
  visible half of C-07.
- **The document does not explain itself.** v1.7's Revision History table stops at v1.1, December 8
  2023. Nothing in the PDF says what arrived in v1.2 through v1.7, so the only way to learn what the
  vendor added was to diff it, which is what this pass did for the pages these records cite.
- **A convention made explicit, because it was implicit and that cost nine quotes.** Prose quotations
  are verbatim substrings. Table quotations join cells with `" | "`, because a PDF text layer emits one
  cell per line and a table row can therefore never be a substring of extracted text. The check has to
  be per cell, and a single substring test over a whole table quote is not evidence of anything.
- **A near-miss, stated plainly because it is a hole in the suite.** The script that moved these
  records first left nine of them naming `DS-10712-001_v1.0` in `doc_id` while pointing at NVIDIA's
  v1.7 file: a record reading as though the older revision backs a newer quotation.
  `make verify-evidence` passed it, and it cannot do otherwise. `doc_id` is free text, the URL is now
  a vendor host so the mirror rule is satisfied, and every value token still appears in the quote. The
  mismatch surfaced only by reading the rendered table. This is the same gap the third pass recorded as
  the `doc_id` loophole, and it argues for the same fix: a structured revision field that the locator,
  the URL and a check can all agree on.

- **What did not move, and why the count is 23 rather than 0.** The Orin Nano vendor path
  `.../downloads/jetson-orin-nano-series-data-sheet` resolves but answers 302 to `/login`, so the ten
  `connecttech.com` records cannot be re-read anonymously. For DS-10662-001v1.8 no download slug could
  be derived: four `developer.nvidia.com` candidates answer 404 while the NX and Nano slugs resolve.
  Recording a guess's 404 as "NVIDIA does not publish this" would be a fabrication, so the twelve
  `generation-robots.com` records stay mirrored with the measurement in their notes, and
  `hthreads.github.io` (V-04-02) stays as settled in the third pass. All 23 still say they are mirrors;
  `make verify-evidence` fails if one stops saying so.


### Third pass: provenance hygiene (same day)

The first two passes asked whether a value matches its quote. This one asked whether the *fields
describing the value* mean what they claim, across the 96 records as they now stand.

- **Three derived quantities were tiered T1.** V-01-13 (19.2 GB/s), V-07-02 (490.2 and 980.4 OP/byte)
  and V-07-03 (39.0 to 78.0 OP/byte) are arithmetic on printed figures and appear nowhere printed.
  V-02-36's note already states the rule — a derived value is T2 because the document never prints it —
  and V-04-09 and V-04-12 follow it. Now all six agree. Tiers went from 58 T1 / 26 T2 to 55 T1 / 29 T2.
  No value changed, so no chapter loses support; three claims lose datasheet authority.
- **Three records had an empty `title`.** V-02-36, V-04-12 and V-04-13 rendered a heading with nothing
  but a document number to identify the source. Filled, and V-04-12's title now says it is a derivation.
- **One document-identity conflict raised: C-06.** Ten records cite one URL under two revisions.
  (The fifth pass raised C-07 and took the T1 count from 55 to 60 by adding five records, so the
  tier figures in the bullets above are as of this pass, not as of the final file.)
- **A convention this pass chose not to change:** six records carry prose in `doc_id`
  (`"Derived from DS987 (v1.2)"`, `"Derived from V-04-10, V-04-11, ..."`). `audit_claims.py` reads
  `doc_id` as evidence text when hunting for a printed number, so a record id sitting in that field
  counts as a place a value's digits may appear. That is a loophole worth closing, but closing it means
  a separate field for derivation provenance, and a schema change is not a hygiene fix. Recorded here so
  it is not mistaken for tidy formatting.

### What these audits deliberately did not do

Rule 7 as it then stood kept these audit passes out of `plan.md`, `plan-v2.md`, and `book/`, and
every resolution above was left `needs-human-decision`. That is history, not the current state:
the owner retired rule 7 on 2026-09-12 and the same package closed C-07 and named the ASR model
in `plan-v2.md`. `book/` still holds no new prose, because chapter drafting is a separate branch
and nothing has been written into it yet. Note that `plan-v2.md` §3.3 currently writes the fabric SRAM figure as "3.02 MB",
which is the same quantity as 2.8828 MiB in decimal megabytes — the table is not wrong, but the unit is
ambiguous and C-01 is where that gets settled.
