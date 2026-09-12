# Web Search Protocol — Evidence Collection for `plan-v2.md`

**Purpose.** A model or human with web access executes this document to fill the verification gaps
that [`plan-v2.md`](../plan-v2.md) opened. It is written to be run **standalone**, with no other
conversation context. Hand it to a search-capable model together with the target repository path.

**Why it exists.** `plan-v2.md` §3 and Appendix B list hardware and model quantities that the
repository currently states three different ways, or not at all. Those cells must be filled from
primary documents, not from a model's memory. This file specifies **what to search, how to search
it, and exactly how to record the answer** so the result is admissible as a source.

**Language.** Output records are in **English** (`docs/` is English per `AGENTS.md`).

---

## 1. Hard rules

1. **Never state a number you have not read in a fetched document.** If a search fails, record the
   gap as `unresolved`. An `unresolved` row is a valid and useful result; a remembered number is not.
2. **Never cite a blog, forum post, vendor marketing page, or model-generated summary as the sole
   source** for a hardware quantity. Those may appear as `corroborating_url` only.
3. **Record the conditions with the value.** Datasheet numbers depend on speed grade, voltage,
   temperature, and clock. A number without its conditions is unusable and will be discarded.
4. **Quote the sentence or table cell you read**, verbatim, in the `quote` field. This is what lets a
   later reader check the claim without re-searching.
5. **One record per quantity.** Do not batch several numbers into one prose paragraph.
6. **Never overwrite an existing record to resolve a contradiction.** Add the second record and
   raise a `CONFLICT` entry (§6). Contradictions are findings, not mess.
7. **Retired 2026-09-12 by the repository owner.** The rule read: "Do not edit `plan.md`,
   `plan-v2.md`, or any `book/` file. This task produces evidence only. A human decides which
   claims to rewrite afterwards." The owner lifted it so that planning text and book prose can
   be revised against verified evidence, on the ground that the project's deliverable is the
   knowledge, and no board is available to measure on.

   The number 7 is kept rather than renumbering the list, because `docs/verification/` cites
   rules 1, 2, 6 and 8 by number and a renumber would silently misdirect them.

   **What this did not lift:** rules 1, 2, 6 and 8 still bind, and they are the ones that stop
   fabrication rather than the ones that assign territory. No number that was not read in a
   fetched document. No blog, forum, marketing page or model-generated summary as a sole source.
   Never overwrite a contradicting record. Nothing is marked ✅ without executed code and
   captured logs, which an owner's decision about scope does not manufacture. Editing `book/` is
   now permitted; inventing a measurement in it is not.
8. **Do not mark anything ✅.** Per `AGENTS.md`, ✅ requires executed code and captured logs, which
   web search cannot produce.

---

## 2. Source trust hierarchy

| Tier | Type | Admissible alone? | Examples |
|---|---|---|---|
| **T1** | Manufacturer datasheet / architecture document, PDF, with a document ID | **Yes** | AMD `DS890`, `DS891`; NVIDIA Jetson Design Guidelines |
| **T2** | Manufacturer user guide, tool reference, official spec / whitepaper | **Yes** | AMD `UG1089` (KV260), `UG906` (Vitis AI), FINN paper, Jacob et al. 2018 |
| **T3** | Peer-reviewed paper | **Yes**, for algorithm and model claims | Conformer, MatchboxNet, FINN, FPGA-ASR literature |
| **T4** | Official product page / official repo README | No — corroborating only | nvidia.com embedded module pages, GitHub READMEs |
| **T5** | Forum, blog, Medium, Reddit, StackOverflow, AI summary | **No** | note only if it points at a T1–T3 document |

Prefer the **PDF** over the HTML rendering of the same document, and record the PDF page number.
Where AMD documents are behind a login, say so in the record and mark `access: login_required`.

---

## 3. Output location and record schema

Create this structure (do not restructure anything else):

```text
docs/verification/
  README.md              # index: what was searched, what is still unresolved
  claims.json            # machine-readable, one object per record
  01-fpga-kv260-zu5ev.md
  02-jetson-orin-skus.md
  03-kv260-audio-path.md
  04-toolchain-versions.md
  05-models-and-datasets.md
  06-quantization-sources.md
  07-related-work.md
```

### 3.1 Record format (markdown, one block per quantity)

```markdown
### V-<tier>-<nn> · <short name of the quantity>

| Field | Value |
|---|---|
| status | `verified` \| `unresolved` \| `conflict` |
| quantity | e.g. `on_chip_bram_total` |
| value | e.g. `144` |
| unit | e.g. `BRAM36 blocks` (write `n/a` if dimensionless) |
| conditions | e.g. `speed grade -2, 1.0V, 85C junction` (`n/a` if not applicable) |
| source_tier | `T1` |
| doc_id | e.g. `DS891 (v1.12)` |
| title | full document title |
| url | exact URL fetched |
| locator | page / table / section, e.g. `p.4 Table 1-1 "ZU5EG/ev DC and AC Switching Characteristics"` |
| quote | verbatim sentence or table row that yields the value |
| retrieved_utc | ISO 8601, e.g. `2026-09-12T04:30:00Z` |
| access | `open` \| `login_required` \| `paywalled` |
| corroborating_url | optional, may be empty |
| notes | caveats, e.g. "figure is for ZU5EG not ZU5EV; EV adds no fabric logic" |
```

Rules for the fields:

- `locator` must be specific enough that a reader finds the number in under a minute.
- `quote` is the single most important field. Never paraphrase inside it.
- If `status` is `unresolved`, still fill `quantity`, `notes` (what you searched, what failed), and
  `retrieved_utc`. Leave `value` empty rather than guessing.
- If the document gives a range or several speed grades, create one record **per variant** and name
  the variant in `conditions`.

### 3.2 `claims.json`

Same data, machine-readable, so it can be checked rather than read. Today `scripts/verification/audit_claims.py` checks the file against itself: field shape, id order, that every number in a `verified` value is printed in its own `quote`/`locator`/`doc_id` or derived by an `arithmetic:` clause it declares, that mirror citations admit it, and that every `unit` spelling is a registered term -- the vocabulary lives in `claims_lib.UNIT_TERMS`, and a record that needs a new unit must add it there so the canonical and the kind are stated rather than assumed. Checking each record against `docs/source_index.json` is still not implemented, and so is any check that a registered unit is the right dimension for its value: 39 of the 64 dimensional records hold prose values, so that gate needs a schema split first (Issue #25).

```json
{
  "version": "1.0.0",
  "generated_utc": "2026-09-12T05:00:00Z",
  "records": [
    {
      "id": "V-01-03",
      "status": "verified",
      "quantity": "on_chip_bram36_count",
      "value": "144",
      "unit": "blocks",
      "conditions": "xczu5ev, speed grade -2",
      "source_tier": "T1",
      "doc_id": "DS891 v1.12",
      "title": "Zynq UltraScale+ MPSoC Data Sheet: DC and AC Switching Characteristics",
      "url": "https://docs.amd.com/v/u/en-US/ds891-zynq-ultrascale-plus-mpsoc-dc-ac",
      "locator": "p.4, Table 1-1, row 'Block RAM'",
      "quote": "...",
      "retrieved_utc": "2026-09-12T04:31:00Z",
      "access": "open",
      "corroborating_url": "",
      "notes": ""
    }
  ]
}
```

Every record needs a stable `id` of the form `V-<file-number>-<seq>`, unique across the folder.

---

## 4. Search backlog, in priority order

Work top to bottom. Stop when the time budget is exhausted and report what is left. Tier 1 items
block the most downstream work.

**Partly superseded 2026-09-12.** The owner's decision package named the ASR checkpoint, closed
C-07 to `MAXN`, and made a carrier card a required BOM line. Items T1-D, T2-A and T3-B below are
those same questions asked in the abstract; they were narrowed to concrete targets, and joined
by new ones, in [`AGENT_FETCH_BRIEF_2026-09-12.md`](AGENT_FETCH_BRIEF_2026-09-12.md). An agent
fetching today works from that brief. Everything else here stays valid.

### Tier 1 — blocks every later number

| ID | Question to answer | Suggested queries | Fills |
|---|---|---|---|
| **T1-A** | Exact fabric resource counts for the FPGA on Kria KV260: LUT, FF, **BRAM36 count**, **URAM288 count**, **DSP48E2 count**, and the **speed grade**. | `DS891 Zynq UltraScale+ MPSoC DC AC switching characteristics PDF` · `xczu5ev LUT FF DSP48E2 BRAM URAM site count` · `DS890 Zynq UltraScale+ architecture datasheet PDF` | `plan-v2.md` §3.2, §3.3 |
| **T1-B** | Resolve the memory contradiction: compute total on-chip SRAM from the verified block counts and compare against the three existing claims. | no search — arithmetic on T1-A, then write a `conflict` record | `plan-v2.md` §3.3 |
| **T1-C** | DDR on KV260: type, bus width, data rate, theoretical bandwidth, and whether the PL shares it with the PS. | `KV260 DDR4 16-bit bandwidth UG1089` · `ZU5EV PS DDR4 controller bandwidth DS891` | `plan-v2.md` §3.2, §6.1 |
| **T1-D** | Jetson Orin **per-SKU** matrix: SM count, CUDA cores, Tensor Cores, **DLA count and TOPS**, LPDDR5 bus width and **bandwidth GB/s**, configurable power range, `nvpmodel` mode list. Cover: Orin Nano 4GB, Orin Nano 8GB, Orin Nano Super, Orin NX 16GB, AGX Orin 32GB, AGX Orin 64GB. | `Jetson Orin Nano NX series datasheet NVIDIA PDF` · `Jetson AGX Orin developer guide nvpmodel power modes` · `Orin LPDDR5 102.4 GB/s memory bandwidth` · `Jetson Orin DLA 2 TOPS NVDLA version` | `plan-v2.md` §3.1 |
| **T1-E** | Which Orin SKU the project will actually use, and confirm the module's **exact** part suffix. | no search — this is a decision; record it as `unresolved` with the candidate list from T1-D | `plan-v2.md` §3.1 |

> **T1-B is the highest-value single item in this document.** The repository currently claims
> "~4.5 MB" and "4 MB" while its own block counts add to ~3.02 MB. Confirming the true counts either
> way changes whether the streaming-Conformer half of the project is feasible at all.

### Tier 2 — blocks the audio path and the toolchain

| ID | Question to answer | Suggested queries | Fills |
|---|---|---|---|
| **T2-A** | Does KV260 have **any** onboard audio input? If not, what official carrier/UBB card provides I2S or PDM, and what is its exact name, price, and availability? | `Kria KV260 audio input microphone UG1089` · `Kria carrier card audio I2S PDM AMD` · `KV260 UBB pins I2S available` | `plan-v2.md` §4.1, §8.2 |
| **T2-B** | Which Vivado/Vitis/Vitis AI/PetaLinux versions officially support KV260, and does the **Community** edition suffice for ZU5EV? Disk footprint. | `Vitis AI KV260 supported Vivado version UG1414` · `Vivado Community edition Zynq UltraScale+ supported devices` · `KV260 PetaLinux version compatibility` | `plan-v2.md` §3.2, §8.1, §8.4 |
| **T2-C** | Fixed overlay DPU on KV260: which AIE/DPU arch version, which layer types it supports, and its resource footprint. | `KV260 DPU B4096 arch 3.2 supported operators UG1414` · `Vitis AI model zoo KV260 DPU core configuration` | `plan-v2.md` §7 chặng 5 |
| **T2-D** | Xilinx Power Estimator: confirm it is an **estimation** tool, and get the document that says so plus its stated accuracy caveats. | `Xilinx Power Estimator accuracy measured versus estimated UG440` | `plan-v2.md` §8.3 |
| **T2-E** | Timing/report commands and what a real `report_utilization` looks like for ZU5EV, to know which cells to fill. | `report_utilization Vivado UG912 BRAM DSP48E2` | `plan-v2.md` §6.5 |

### Tier 3 — blocks the model, data, and metric decisions

| ID | Question to answer | Suggested queries | Fills |
|---|---|---|---|
| **T3-A** | MatchboxNet exact parameter count, layer config, and its published accuracy on Speech Commands. Confirm it is a **command classifier**, not ASR, and therefore has **no WER**. | `MatchboxNet 1D Time-Channel Separable CNN Interspeech 2020 parameters` · `NGC MatchboxNet 35 class 12 class model size` | `plan-v2.md` §4.2, §5.3 |
| **T3-B** | A **named** streaming Conformer with an open checkpoint: parameter count, `d_model`, layers, heads, published WER, and its rightaway / future-context in **milliseconds**. | `streaming Conformer open checkpoint LibriSpeech WER rightaway future context` · `online Conformer ASR chunk size latency ms NVIDIA NeMo` · `parametric streaming Conformer low latency WER` | `plan-v2.md` §4.2, §4.4 |
| **T3-C** | Datasets and their **licences**: Google Speech Commands v2, LibriSpeech, and any KWS benchmark split. Speaker-independent split availability. | `Speech Commands v2 dataset license CC BY` · `LibriSpeech license attribution` · `speaker independent KWS evaluation split` | `plan-v2.md` §5.1 |
| **T3-D** | Primary source for **affine / asymmetric** quantization with zero-point, and for the integer multiply-plus-shift requantization. The repo currently cites FINN for this, which is wrong. | `Jacob 2018 Quantization Deployment Deep Neural Networks Microcontrollers affine zero-point` · `TensorFlow model quantization spec integer multiply shift requantization` · `quantization handbook fixed point requantization rounding` | `plan-v2.md` §9.1 |
| **T3-E** | What FINN actually is and is not, to justify removing it as the quantization source. | `FINN framework binarized quantized neural network FPGA Umuroglu scope` | `plan-v2.md` §9.1 |
| **T3-F** | Rounding-mode conventions: what PyTorch / TensorRT / Brevitas each use for requantization, and the known mismatch when porting to RTL. | `Brevitas quantization aware training rounding mode` · `PyTorch quantize per tensor rounding half even` · `TensorRT INT8 calibration entropy percentile` | `plan-v2.md` §6.2 |

### Tier 4 — blocks the paper

| ID | Question to answer | Suggested queries | Fills |
|---|---|---|---|
| **T4-A** | Related work: published FPGA speech accelerators with **latency, power, energy-per-frame, and resource** numbers, to build the positioning table. | `FPGA keyword spotting accelerator energy per frame` · `FPGA speech recognition accelerator latency power comparison Jetson` · `FINN KWS FPGA measured power` · `MLPerf Tiny FPGA` | `plan-v2.md` §5.5 |
| **T4-B** | Artifact evaluation requirements for FCCM / ACM FPGA / ICASSP: what must ship, anonymity rules, page limits. | `FCCM artifact evaluation requirements` · `ACM FPGA conference reproducibility appendix` · `ICASSP page limit reproducibility checklist` | `plan-v2.md` §11 |
| **T4-C** | Roofline methodology citation and the correct Orin ridge point once T1-D is done. | `Roofline model Williams CACM arithmetic intensity` | `plan-v2.md` §6.1 |

---

## 5. Disambiguation traps to check on every record

These are the specific ways this topic produces a wrong-but-plausible number.

1. **EG vs EV vs CG vs I vs E suffixes** on Zynq UltraScale+ parts change price and sometimes
   available fabric. Record the **full** part string.
2. **Speed grade** changes Fmax and therefore what "peak TOPS" means. Never record a frequency
   without its grade.
3. **"Jetson Orin" is not a chip.** A bandwidth figure for Orin NX is wrong for Orin Nano. Every
   Orin record must name the SKU in `conditions`.
4. **Marketing TOPS are sparse INT8.** Dense INT8, FP16, and sparse numbers differ by up to 4×.
   Always record which one, and prefer the non-sparse figure.
5. **Module power ≠ system power.** Carrier board, peripherals, and storage add watts. Record whether
   the figure is module-only.
6. **Idle power is included or excluded** differently across documents. Record which.
7. **BRAM and URAM are different memories** with different clocking and different usable fraction.
   Never merge them into one "SRAM" number without stating both counts.
8. **A datasheet table may be for the family, not the part.** Check the column header for the exact
   device.
9. **URAM availability is not guaranteed** for every design — some are reserved or unusable at the
   target clock. Note any such caveat you find.
10. **Papers report batch>1.** A throughput number at batch 8 is not comparable to a streaming
    `batch=1` claim. Record the batch.
11. **Conference version vs arXiv version** of a paper can differ in numbers. Record which you read.
12. **A "user guide" may describe a reference design, not the silicon.** Distinguish device facts
    from board-level facts.

---

## 6. Handling contradictions

When a new record disagrees with something already in the repository:

1. Add the new record normally, with `status: conflict`.
2. Append an entry to `docs/verification/README.md` under `## Conflicts`, in this form:

```markdown
### C-<nn> · <quantity>
- Existing claim A: "<quote>" — `plan.md:55` — value 4 MB
- Existing claim B: "<quote>" — `docs/research_notes/R02_fpga_audio_streaming.md` — value ~4.5 MB
- Computed from verified block counts: 3.02 MB
- New verified source: V-01-03 (DS891 p.4 Table 1-1)
- Resolution proposed: <one line>
- Resolution status: `needs-human-decision`
```

3. **Do not edit the contradicting files.** Proposing the resolution is in scope; applying it is not.

---

## 7. Definition of done

Report back with a short table, and only then stop.

| Check | Pass condition |
|---|---|
| Tier 1 complete | T1-A…T1-D each have a `verified` record, or are `unresolved` with what was tried |
| Memory question settled | T1-B exists and states the computed total plus which existing claim is wrong |
| Audio path settled | T2-A states either a working input route or that none exists at reasonable cost |
| Every record has `quote` + `locator` + `retrieved_utc` | no exceptions |
| `claims.json` parses | `python -c "import json;json.load(open('docs/verification/claims.json'))"` |
| Conflicts logged, none silently resolved | `## Conflicts` section present |
| Nothing outside `docs/verification/` modified | `git status` shows only new files in that folder |

### 7.1 Hand-back summary format

Produce this as the final output so the next step can act on it without re-reading everything:

```markdown
## Search report — <date>
Records written: <n> (verified <a>, unresolved <b>, conflict <c>)
Files: docs/verification/...

### Answers that change the plan
- <one line each, with the record id>

### Still unresolved, and why
- <quantity> — <what failed: login wall / not published / ambiguous>

### Conflicts needing a human decision
- C-01 ...
```

---

## 8. Suggested execution

Give the searching model this file plus the repository path. A workable prompt:

```text
Read docs/WEB_SEARCH_PROTOCOL.md in this repository and execute it.
Work Tier 1 first, then 2, 3, 4, until your budget is exhausted.
Write records only under docs/verification/. Do not modify any other file.
Never state a number you did not read in a fetched document; record 'unresolved' instead.
Finish with the §7.1 hand-back summary.
```

If the model has no web access, it should say so immediately rather than answering from memory. That
answer would be worse than no answer, because it would look like evidence.
