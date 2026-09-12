# Agent Fetch Brief — 2026-09-12 (post-decision package)

A **fetch brief** for an agent to execute in a separate session, possibly on a different model. It
narrows the standing backlog in [`WEB_SEARCH_PROTOCOL.md`](WEB_SEARCH_PROTOCOL.md) §4 to the four
things that became answerable, and newly blocking, when the repository owner made these decisions on
2026-09-12:

* protocol rule 7 (the ban on editing `plan.md`, `plan-v2.md`, `book/`) was retired;
* conflict **C-07** closed to the **`MAXN`** operating point;
* the ASR model became a **named checkpoint** (NeMo Conformer-Transducer `small`, streaming) instead
  of a model class;
* the KV260 audio path became **I2S/PDM through a carrier card into the PL**, so a carrier card is
  now a required BOM line rather than an "if needed".

`WEB_SEARCH_PROTOCOL.md` §4 was written before those decisions. Its items **T1-D**, **T2-A** and
**T3-B** are the same questions asked in the abstract. This brief asks them concretely, and it is
this brief, not §4, that you should work from today.

**You are not the integrator.** Produce records. Do not edit `plan-v2.md`, `book/`, or any chapter —
the owner retired the *protocol* rule that used to forbid it, and the division of labour still stands
because the main session owns how evidence lands in prose. This is a working convention, not a rule;
protocol rules 1, 2, 6 and 8 are rules and still bind you.

---

## 1. Read first, in this order

1. `docs/WEB_SEARCH_PROTOCOL.md` §1 (hard rules), §2 (source tiers), §3.1 (record format), §3.2
   (`claims.json`), §5 (disambiguation traps), §6 (contradictions).
2. `docs/verification/README.md` — the "Conflicts" section, and the current record counts.
3. This file.

The four rules that stop fabrication, restated because they are the ones that will trip you up:

* **Rule 1** — never state a number you did not read in a document you fetched. Your priors about
  what a Conformer's `d_model` is are worth nothing here. If your tooling cannot open a PDF, say so
  in your report; do not substitute memory for a fetch and label it a fetch.
* **Rule 2** — a blog, forum post, vendor marketing page, or AI-generated summary is corroborating
  only. The §2 tier table decides admissibility; T4 cannot carry a record alone.
* **Rule 6** — never overwrite a contradicting record. Add the second record and raise a `C-<nn>` in
  `docs/verification/README.md`.
* **Rule 8** — do not mark anything ✅, "done", or "verified by measurement". There is no board.

---

## 2. Known traps already measured in this repo

Save yourself the rounds these cost:

| Trap | What happens | Do instead |
|---|---|---|
| `docs.amd.com` | Any path, valid or invented, returns **HTTP 200 with an identical JavaScript shell** and no document text. A 200 proves nothing. | Fetch the PDF endpoint or judge the response by whether the expected text is actually present, not by status code. |
| NVIDIA download links | `cdn.qoriz`/`developer.nvidia.com` redirects carry **expiring tokens**. A citation to them dies. | Cite the stable `.../jetson-download/...` or landing-page URL that resolves today, and say which one you used. |
| Orin Nano / AGX datasheets | The vendor path exists and answers **302 → `/login`**. Four plausible AGX slug candidates **404**. | Do not spend the budget guessing slugs. Try the *Developer Guide* and *Design Resources* pages, which are often open where the datasheet is not. If it stays gated, record the measurement as `unresolved` with `access: login_required` and move on. An authenticated download is the owner's action, not yours. |
| `connecttech.com` mirror | 403s. | Not a mirror of record. Skip. |
| Model cards on NGC | Give you WER and the checkpoint name. Architecture fields on a model card are T4. | Get architecture numbers from the model's own config (the `model_config.yaml` inside the checkpoint, or the NeMo source that defines the `conformer_transducer_small` variant) or from the Conformer paper. That is a T2/T3 statement of the same fact. |
| `MAXN` vs `MAXN_SUPER` | Datasheet `DS-10712-001_v1.7` prints **two columns**. Reading the wrong one is the C-07 conflict itself. | Every Orin figure you record must name its column in `conditions`. `MAXN_SUPER` numbers are already in `V-02-37 … V-02-41`; do not re-add them, and do not "correct" them. |

---

## 3. Work items, in priority order

Stop when your budget runs out and report what is left. P1 blocks the most downstream writing.

### P1 — Architecture and memory footprint of the named ASR checkpoint (narrows §4 item T3-B)

Target: **NVIDIA NeMo Conformer-Transducer `small`, streaming variant**, with an open checkpoint.

| ID | Question | Where to look | Fills |
|---|---|---|---|
| **P1-A** | Identify the exact checkpoint: NGC model name, `small` variant, streaming or chunked-inference mode, and the NeMo version that publishes it. | NGC model card; NeMo `docs/user-guide/asr` Conformer section | `plan-v2.md` §4.2 |
| **P1-B** | Architecture: encoder **layers**, `d_model`, attention **heads**, conv **kernel size**, decoder/embedding dims, total **parameter count**. | The checkpoint's `model_config.yaml`; NeMo source `nemo/collections/asr/parts/submodules`; Conformer paper `arXiv:2005.08100`; NeMo `conformer_transducer_small` recipe config | §4.2, §6.1 |
| **P1-C** | Compute per acoustic frame: **MACs/frame** (or the multiply-add count the config implies) and **weight bytes at INT8**. | Prefer a published figure. Otherwise record the inputs as separate records and let `plan-v2.md` §6.1's arithmetic derive it — see "arithmetic" below. | §6.1 roofline |
| **P1-D** | **Activation bytes per frame** at a stated batch and precision, and the weight-streaming rate that implies. | NeMo streaming inference docs; the paper's memory analysis; else derive and declare it. | §6.1, §7 chặng 8–10 |
| **P1-E** | Published **WER** on LibriSpeech test-clean/test-other *under streaming*, plus the **right-context in milliseconds** that the streaming variant uses. | Model card + paper + NeMo results table. Note which is causal and which is offline two-pass — the accuracy-versus-latency curve in §4.4 is meaningless if you mix them. | §4.2, §4.4, §5.3 |

**Arithmetic note.** `plan-v2.md` §4.2 demands these numbers *computed, not estimated*. A derived
value is admissible only if you record it as declared arithmetic over fetched inputs, in the form
`audit_claims.py` already checks: the inputs each get their own record, and the derived record names
them. Do not publish a derived number without the records underneath it.

**Done when:** P1-B has every field filled from a fetched document or is explicitly `unresolved`, and
P1-E states the streaming condition. If only the *config* numbers come back, that is still the single
most useful delivery — the WER can trail.

### P2 — The `MAXN` column, per candidate SKU (narrows §4 item T1-D, now scoped by C-07)

C-07 closed to `MAXN`, so the book's roofline runs on the default profile. **The SKU is still the
owner's choice** — `plan-v2.md` §3.1's "Board baseline" row is deliberately unfilled, and T1-E says
SKU selection is a decision, not a search. Fetch the matrix for the four candidates so the choice can
be made on facts: Orin Nano 4GB, Orin Nano 8GB, Orin **Nano Super**, Orin **NX 16GB**, AGX Orin
32GB/64GB.

| ID | Question | Notes |
|---|---|---|
| **P2-A** | For each candidate: does a mode named **`MAXN`** exist, and at what module power? | `MAXN_SUPER` needs 40W and an 8V rail; `MAXN` figures are what the book now needs. NX 16GB is already covered by `V-02-12 … V-02-19` — check before duplicating, and never overwrite. |
| **P2-B** | **Memory bandwidth in GB/s** per candidate, and the bus width it comes from. | This is the roofline's denominator. Orin Nano Super's 102 GB/s is in the repo; 8GB Nano differs. |
| **P2-C** | INT8 **dense** and **sparse** TOPS at `MAXN` per candidate. | The 50 / 100 pair is NX 16GB at `MAXN_SUPER`-adjacent marketing. Always capture *which* column. |
| **P2-D** | DLA count and TOPS per candidate at `MAXN`. | `V-02-17` was already repaired once for presenting a derived per-engine number as a datasheet reading. There is no per-engine figure in v1.7; do not re-create one. |

**Landmine for the ridge point.** `V-07-02`'s 490.2 OP/byte is `50 dense TOPS / 102 GB/s`. Any new
bandwidth or TOPS record for a *different* SKU changes which ridge point the book teaches, so record
the SKU in `conditions` on pain of producing an unusable number.

### P3 — Does the chosen carrier path actually exist? (narrows §4 item T2-A, now load-bearing)

This is the item most likely to return bad news, and the reason it is P3 rather than P5 is that the
decision it tests was just made. `plan-v2.md` §8.2 now lists a carrier card as required, on the
assumption that a KV260 carrier can bring I2S or PDM to the PL.

| ID | Question | Where to look |
|---|---|---|
| **P3-A** | Does the **Kria KV260 UBB** expose I2S or PDM on any header, and on which pins? | `UG1089` (Kria KV260 carrier card / user guide), pin tables and the expansion sections. Also `DS891`/`DS890` for the SoC side. |
| **P3-B** | If **not**: what official or first-party option does bring a mic bitstream into the PL on KV260 — a different carrier, a Pmod (e.g. Pmod I2S2), a mic array board? Exact part numbers. | AMD/PetaLinux docs, official accessory lists. Note: a Pmod needs a working **PMOD/I2S controller** — record whether that is the PL, and say so. |
| **P3-C** | Price, distributor, lead time for the winning option and for the mic. | Distributor product pages are **T4** — corroborating only. A price is not a technical claim, but record it in `notes`, not as a `verified` quantity, unless you can name a T1/T2 page that prints it. |
| **P3-D** | Is there any **documented** PDM or I2S capture example for KV260, and does it go through the PL or terminate in the PS? | PetaLinux/UG1089 examples, Xilinx app notes. This decides whether §4.1's CIC-decimation content is a real port or an invention. |
| **P3-E** | Is the KV260 still **sold**, and at what price? `plan-v2.md` §8.2's "còn được bán?" row is open. | Distributor stock pages, again T4. |
| **P3-F** | On the **PMOD J2** connector specifically (the connector `V-03-02` documents the Digilent 410-379 codec plugging into), do the I2S lines reach the **PL fabric** as programmable pins, or do they terminate in the **PS** hard IP? Name the table or schematic page. | `UG1089` KV260 carrier card user guide — the PMOD/J2 pin tables and the block diagram showing what J2 drives. Corroborate against `DP197`/`PG216`-class I2S subsystem docs if the IP is PS-side. **This is the item that decides whether section 4.1's CIC/fabric audio content is a real port or an invention.** A record that says "I2S available" without saying to which domain is not an answer; report which page you looked at even if it does not say. |
| **P3-G** | Does any **PDM MEMS microphone array** option exist for KV260 that delivers a PDM bitstream into the PL? Exact part numbers, or an explicit negative from the official accessory list. | AMD/Xilinx KV260 accessory and carrier lists, UG1089 expansion sections. Needed because `book/TOC.md` calls CIC decimation **mandatory** and `plan-v2.md` section 8.2 requires an "I2S or PDM" microphone, while `V-03-03` documents a **CS5343 multi-bit ADC whose output is PCM/I2S words** — a CIC decimator has no PDM bitstream to decimate on that path. If no PDM-to-PL option exists, the book must teach the I2S/PCM route and present PDM+CIC as the architecture for a board that does. |

**Report the negative.** If UBB has no I2S/PDM, that *is* the finding: record it, and the repo will
either name P3-B's replacement or reopen the audio-path decision. Do not soften it into "partially
supported".

### P4 — Toolchain support for the newly chosen path (narrows §4 item T2-B)

| ID | Question |
|---|---|
| **P4-A** | Which Vivado/Vitis/Vitis AI/PetaLinux release officially supports KV260 **and** carries the I2S/PDM or audio example from P3-D. A toolchain that supports the board but not the peripheral is not the answer. |
| **P4-B** | Does Vivado **Community Edition** suffice for `xczu5ev` at the required speed grade? Disk footprint. |
| **P4-C** | Which Vitis AI quantizer precisions and per-tensor/per-channel modes are supported, since §6.2's rounding-mismatch teaching depends on the actual tool behaviour, not on PyTorch's. |

---

## 4. Explicitly out of scope — do not spend budget here

* **`V-04-13`, the DPU core configuration actually shipped on a KV260.** It needs
  `dpu-sysfs resource_info` read from a running board. **No search answers it.** It stays
  `unresolved` and gets taught as a measurement procedure with an empty result. A confident-sounding
  DPU arch version from a tutorial is exactly the failure mode rule 1 exists to stop.
* **Any measured latency, power, WER, or utilization figure for this project.** Nothing has run. There
  is no board. The book's tables keep visibly empty result cells, and that is the design.
* **SKU selection, and any other owner decision.** Present the matrix; choose nothing.
* **Book prose.** Different branch, later.

---

## 5. Deliverable

Add records to the **existing** per-file markdown and `claims.json`, following §3.1's field list
exactly. The mechanics that CI enforces, in the order that works:

1. **`docs/verification/claims.json` is the single source of truth** for record fields. Edit it; do
   not hand-edit `01-…`, `02-…`, `03-…`, `04-…`, `07-…` — `render_claims.py` generates those. After
   editing JSON, run `python scripts/verification/render_claims.py` **without** `--check` to
   regenerate, then `--check` to confirm.
2. **`docs/verification/README.md` is hand-written** and is *not* rendered. Your edits there are safe
   and required: bump the summary counts, because `audit_claims.py` **fails when a README count
   label disagrees with `claims.json`**. Also: exactly one heading per record, no orphans, no
   duplicates.
3. New records take the next free `V-<file>-<seq>` id, unique across the folder. Keep the file-number
   aligned to the subject (`01` FPGA/KV260, `02` Jetson Orin, `03` KV260 audio, `04` toolchain,
   `05` models/datasets, `06` quantization, `07` related work).
4. Register each **new document** in `docs/source_index.json` with a global `S<NNN>` id and a
   `claims_supported` list naming the records it carries. `verify_integrity.py` errors on a
   `claims_supported` id that does not exist. `R01-NN` ids are legacy; do not mint new ones.
5. Bump `claims.json` `version` (minor) and set `generated_utc`.
6. Run everything CI runs, before you open the PR:
   `python -m pytest`, `python -m ruff check .`, `python -m ruff format --check .`,
   `python -m mypy .`, `python scripts/verify_integrity.py`,
   `python scripts/verification/audit_claims.py`,
   `python scripts/verification/render_claims.py --check`.
   There is no `make` binary on every machine; `make gate` is these seven commands.

**Environment notes** that have already cost this repo time: use `python`, not `python3`; export
`PYTHONIOENCODING=utf-8` or the Vietnamese text raises `UnicodeEncodeError` mid-run; the PDF library
is `pymupdf`, imported as `fitz` in some examples and not the same thing as a package named `fitz`.

**Report back** in your PR description: per work item, the record ids produced, the documents
actually opened with their access status, and — most usefully — a plain list of what you could not
reach and what you observed when you tried. A `null` with a measurement attached beats a plausible
number. If you edit `plan-v2.md` or a chapter despite the instruction at the top of this file, say so
in the first line of the report.
