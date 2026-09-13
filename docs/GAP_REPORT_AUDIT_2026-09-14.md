# Audit of an External AI Gap Report — 2026-09-14

**Date:** 2026-09-14
**Subject:** A report written by an AI assistant in a conversation outside this repository. It re-ranks
six learning gaps, states architecture numbers for the target model, names the manuscript sections to
fill, proposes a verification flow, and lists missing tooling. The repository owner asked whether it is
correct and, if it is, to fold it in and generate the material.
**Verdict:** Partly, and the split is clean. Everything the report says about **what the manuscript is
missing** holds, and holds strongly. Every number it supplies **for the model** is either contradicted
by a registered record or has no record behind it at all, and the ranking it re-orders does not exist
anywhere in this repository. So the report can be used as a list of questions and cannot be used as a
source of answers.
**Companion:** [`PLAN_GAP_ANALYSIS.md`](PLAN_GAP_ANALYSIS.md) — the same treatment applied to `plan.md`.

> **Why an outside AI report cannot carry a number here.** `docs/WEB_SEARCH_PROTOCOL.md` rule 1 forbids
> stating a number that has not been read in a fetched document, and rule 2 forbids a model-generated
> summary as the sole source of anything. The report is a model-generated summary, so it is not a
> tier-1 to tier-4 source in any reading of the table in that protocol. This is not a judgement about
> whether its numbers happen to be right. A right number with no record underneath it still cannot be
> traced, and untraceable numbers are the failure mode this repository has been repeatedly repaired
> for: `docs/PLAN_GAP_ANALYSIS.md` BLOCKER-1 is a benchmark table the same way.

---

## 1. Verdict table

Twenty claims, each with the file, line, or record that decides it. "Holds" means the repository
agrees. "Contradicts" means a registered record says otherwise. "No evidence" means neither. Rows 17 to 19
joined after the first draft: three attention claims this session had left out of the table, read in by the
adversarial panel described in section 6. Rows 15 and 18 were then re-judged and row 20 added, once
the panel's model-structure verdict arrived and this session re-read the registered config line by line: the
evidence for the model's shape is better than "no evidence", and the normalization claim is the one the
hardware primitives turn on.

| # | The report states | Verdict | Decided by |
|---|---|---|---|
| 1 | Chapter 8 has four section headers and zero content | **Holds** | `book-en/chapter08.md` is 13 lines: an H1, a scope note, an objective line, a rule, and four `## 8.x` headings with no body |
| 2 | "The book has ZERO content" on attention | **Holds** | Two occurrences of the word in the whole English manuscript, both in `book-en/chapter08.md` (line 6 objective, line 12 heading) |
| 3 | No V&V tooling: cocotb, golden model, `.hex` vectors, bit-exact comparison, SVA, ILA | **Holds, and the repo already knew** | Measured here: zero tracked files with a `.v`, `.sv`, `.vhdl`, `.vhd`, `.xdc` or `.tcl` extension. The only matches of `golden`, `bit.exact` or `hex` in any `.py` file are three `hexdigest()` lines, `scripts/capture_result.py:36`, `scripts/verify_integrity.py:210` and `tests/test_result_log_gate.py:94` — checksum code, not a golden model. `pyproject.toml` declares numpy, scipy, matplotlib, rich, pydantic plus dev, audio, ml and book extras, and no `cocotb`, `brevitas` or `verilator`. `plan-v2.md` §6.3 already prescribes the whole ladder and ends "phải thêm, nếu không thì cả mục này là văn" |
| 4 | PyTorch rounds half-to-even: 0.5→0, 1.5→2, 2.5→2, 3.5→4 | **Holds, and is evidenced here** | `V-06-05` quotes the PyTorch page: "This function implements the 'round half to even' to break ties"; `V-06-04` records Brevitas defaulting to `RoundSte`, which wraps it |
| 5 | "your FPGA's BRAM budget (2.88 MiB)" | **Right size, wrong memory** | 2.88 MiB is fabric SRAM, BRAM and URAM together: `V-01-11` gives 23 616 Kb and `V-01-22` prints the chain 23 616 Kb = 2 952 KiB = 3 022 848 B = 2.8828 MiB under the condition "144 BRAM36 tiles + 64 URAM288 tiles". BRAM alone is `V-01-06`, 5.1 Mb = 648 KiB = 0.63 MiB. The report writes BRAM at the formula and again in its deliverable list, so a reader sizing a buffer from it believes there is 4.5 times the memory that exists, in the memory it named |
| 6 | Ring buffer = `T_left` × `d_head` × `n_heads` × 2 × bytes, with "chunk e.g. 16 frames" | **Holds, minus two things the plan states and the report drops** | `plan-v2.md` §6.7 gives six factors: `n_chunks_kept × chunk_len × d_head × n_head × 2 × bytes`. Collapsing the first two into `T_left` loses a unit. One chunk is 16 *feature* frames at 40 ms each (`V-05-05`), so a reader who counts raw 10 ms frames over-counts by 4. And "chunk e.g. 16 frames" fixes `n_chunks_kept` at 1, which is the chunk being computed, not left context. Neither side multiplies by the block count, though every block keeps its own keys and values. See §4.4 |
| 7 | Acceptance for the on-board build is a continuous run of at least one hour | **Holds** | `plan-v2.md` §7, stage 8: "Chạy liên tục ≥1 giờ không treo; P99 đo trên board khớp sim ±10 %" |
| 8 | "16 Conformer blocks", "4 or 8 heads" | **Contradicts**, **amended the same day to true of another model** — see §7 | `V-05-04` registers `d_model=256`, 12 encoder blocks, 4 heads, `linear_units=2048`, `cnn_kernel=15`; and `plan-v2.md` §4.2 forbids writing any of these numbers before a fetch registers them. The fetch ran the same day and the verdict moved: see §7 |
| 9 | A six-topic ranking exists at positions 1–6 and is being re-ordered | **Contradicts** | No six-topic list exists in any tracked file. The only authority-stated order is the ten-stage spine in `plan-v2.md` §7 mirrored by `book/TOC.md`, which puts measurement before architecture |
| 10 | Sections 8.3 and 8.4 "are the two most critical sections for your job, and they're blank" | **Wrong procedure** | `book/TOC.md` lines 139–166 records the owner settling chapters 8 and 9 on the `plan-v2.md` §7 artefacts, and says the stubs under them "were left in place on purpose" pending prose work |
| 11 | "You're comparing your FPGA implementation of 30 unfused layers against Orin's 12 fused kernels" | **No evidence** | No record in `docs/verification/claims.json` counts layers or kernels for either side |
| 12 | Rounding mismatches eat "80 % of debugging time" | **No evidence** | No record, no log in `results/`, and this project has not debugged anything yet |
| 13 | After 64-plus rounding operations "the final output can differ by several percent" | **No evidence, and against the method** | `plan-v2.md` §6.2 states the qualitative risk and no magnitude; §6.3 makes the gate "0 mismatch trên toàn bộ vector" measured **per stage**, which is a procedure for preventing accumulation rather than quantifying it |
| 14 | TensorRT fusion makes the chapter 3 roofline comparison unfair | **Category error** | `book-en/chapter03.md` lines 30–33: the figure plots machine ridge points, and the workload is deliberately left off the plot. Fusion changes a workload's memory traffic, not a machine's corner |
| 15 | The Conformer block is FFN–attention–convolution–FFN with a half-scale residual on the two feed-forward halves | **Right for the class, unregistered here** | The order and the half-scale check out against a fetched source: NeMo's `nemo/collections/asr/parts/submodules/conformer_modules.py` builds feed_forward1, self-attention, the convolution module, feed_forward2, scales the two feed-forward residuals by `fc_factor = 0.5`, and expands the convolution module as pointwise, GLU, depthwise, norm, Swish, pointwise. That source is not in this repository's registry, and the registry holds nothing on block structure at all: `docs/source_index.json` line 87 records of the Conformer paper that it is "Registered and uncited: chapter 1 explains the Conformer from its architecture, and no record yet quotes this paper for it", and its `claims_supported` is an empty list. So the claim is the first draft of a passage the book still has to write, with a citation the book does not yet have. The count and the norm belong to rows 8 and 20, not here |
| 16 | Deliverable: a one-page "Model Reference Card" for the target model | **Good idea, blocked on a fetch** | `docs/AGENT_FETCH_BRIEF_2026-09-12.md` item P1, opened 2026-09-12 and never delivered, is exactly the card's input list. Filed as #47 |
| 17 | "In streaming mode, frame i must NOT attend to future frames j>i. In hardware, this is a mask that forces certain attention scores to zero. You implement this as a comparator + mux in RTL." | **Contradicts, and it would break the book's own results** | `plan.md:75` says exactly this and `plan-v2.md:200` orders the sentence corrected, because the Conformer "vốn **có** future context". Chunked streaming forbids reading past the current *chunk*, not past the current *frame*: inside a chunk frames see each other both ways, and that look-ahead is the right context the project chose this model for (`plan-v2.md:159`) and means to plot against accuracy (`plan-v2.md:197`). On `V-05-05`'s numbers a 16-frame chunk gives its first frame 15 frames of right context, 600 ms. Masking `j>i` deletes it, and the 3.80 and 4.54 WERs of `V-05-06` would stop describing the device being built. The one `causal` in the evidence set is `causal: true` inside `V-05-04`, which flags the convolution. A mask is also not zeros: scores are summed, so an out-of-window key is absent from the buffer or given a large negative value before the softmax |
| 18 | "The Conformer uses Transformer-XL style relative position ... Each term is a separate multiply-accumulate path in hardware" | **Confirmed by the record, and unrecorded** | The repository's own registered config answers this, and neither the report nor this session had read it: line 17 of `S016`'s file sets `pos_enc_layer_type: 'rel_pos'` and line 18 sets `selfattention_layer_type: 'rel_selfattn'`, which is the relative-shifted attention of Transformer-XL by name. Those two lines sit inside the "Lines 4-18" range `V-05-04`'s locator claims and are absent from its quote, so the evidence was one fetch away and unregistered (#50). The hardware consequence the report draws is also real: relative position means an extra shift term per head and a second dot product per pair, not one QK path. What remains missing is the four-term decomposition itself, which belongs to the Conformer paper (`R01-03`), still uncited |
| 19 | "your FPGA pipeline STALLS at softmax. You need to design around this — double-buffering, or the base-2 approximation (Ch.8.4)" | **Partly correct, and the named remedy answers a different problem** | The order rule holds: a row's denominator, and here its running maximum too, must finish before any value in that row is final. A reduction is not a stall, though — the accumulator is occupied once per element for the whole sum. The repository's own list of where idle cycles come from is `plan-v2.md` §6.6: FIFO sizing, who holds TREADY, measured II. And the block-wise answer the report presents as news is already the plan: `book/chapter08.md:34` asks for softmax "theo khối mà không cần lưu toàn bộ ma trận T x T". Base-2 piecewise conversion reduces the cost of the exponential, not the dependency on the sum |
| 20 | The convolution module "BatchNorm → Swish", "why BN not LN here", and "LayerNorm vs. BatchNorm ... LN normalizes per-frame, BN normalizes per-channel. LN needs rsqrt." | **The distinction holds; the choice is wrong for the recorded model** | Per-frame against per-channel is a fair way to separate the two norms, and a reciprocal square root really is the expensive part of LayerNorm in fabric. The premise is not. The one Conformer configuration this repository registers sets `cnn_module_norm: 'layer_norm'`, with the recipe's own comment "using nn.LayerNorm makes model converge faster", at line 21 of `S016`'s file; `V-05-04`'s quote stops at line 20, so the record that decides the question does not contain its answer (#50). BatchNorm is what NeMo's convolution module defaults to, and no NeMo record exists (§4.1). Two consequences, both in the book's favour: a LayerNorm is data-dependent, so it folds into no neighbouring convolution and must be computed as itself, which is the unit `book-en/chapter08.md` already promises in section 8.4; and a BatchNorm, were one ever registered, would fold backwards into the causal depthwise taps as a per-channel affine, deleting a stage rather than adding one |

## 2. What the report contributes

Three things in the report are worth keeping, and none of them is a number.

**It reads the manuscript honestly.** The claim that chapters 8 and 9 are empty is true, and the count
is worse than the report says: measured as non-heading, non-comment lines, `book-en/` holds 329 content
lines in chapter 1 and 233 in chapter 3, and between one and seven in each of the other eight chapters.
Two chapters carry a book's argument; eight carry headings.

**It names the right trap.** `plan-v2.md` §6.2 already wrote that a rounding convention shared between
the quantizer and the RTL is where bit-exactness dies, and it left the choice open with three candidates
named. The report's table is the same trap seen from the software side, and the three registered records
`V-06-04`, `V-06-05` plus the note that RTL adding `1 << (shift - 1)` rounds half away from zero make it
concrete: three tie behaviours live in one toolchain.

**It asks for a deliverable the repository does not have.** A model reference card is the natural home
for the fields `plan-v2.md` §4.2 demands be computed rather than estimated.

What it does not contribute is any new question. Every gap it lists for verification and tooling is
already written down in `plan-v2.md` §6.3 and §8.4, and every gap it lists for hardware primitives is
already a section heading with a question behind it.

## 3. The one claim that would have cost the most

Claim 8. The report puts "16 Conformer blocks" into an arithmetic ("16 blocks × 4 sub-layers × multiple
requantization steps = 64+ rounding operations") and then uses that arithmetic to size a risk. Each step
of it looks reasonable, so the number survives a reader's first glance, and that is the whole
mechanism by which a fabricated figure becomes load-bearing.

Against it: `V-05-04` is the only registered architecture in this repository and it reads 12 encoder
blocks with 4 heads, quoted from the config that ships the recipe the record is about. And
`plan-v2.md` §4.2, in the past tense and with a list, already rules the entire class out:

> **Những con số chưa được phép viết thành số.** Số layer, `d_model`, số head, số tham số, MACs mỗi
> frame, byte trọng số ở INT8, byte activation mỗi frame — tất cả **phải fetch và ghi thành record**
> trước khi xuất hiện ở bất kỳ đâu.

So the report's number is not merely unsourced. It is unsourced about the one quantity the project has
explicitly fenced.

**Amended the same day.** Two sentences above are now false and are left standing rather than edited, per `WEB_SEARCH_PROTOCOL.md` rule 6. `V-05-04` *was* the only registered architecture in this repository when this section was written; it is no longer, because `V-05-12 … V-05-15` register a second one, and the number that one prints is 16. What §3 concludes about the method — an unsourced figure that reads as reasonable becomes load-bearing — survives that finding intact, and §7 states where the two now differ.

## 4. What the report cannot know about this repository

Six defects, none of which the report sees, all of which sit underneath the material it proposes to
write.

**4.1 The spine and the registry name different models** (filed as #47).** `plan-v2.md` §4.2 and `book/TOC.md` line 25 fix
the ASR target as a **NVIDIA NeMo streaming Conformer-Transducer `small`** checkpoint. The evidence set
contains nothing about that checkpoint: `V-05-03` registers a **WeNet** U2++ Conformer as the open
checkpoint, and `V-05-04` to `V-05-06` give its hyperparameters, chunk latency and published WER. The
fetch brief opened on 2026-09-12 to close this — item P1, five fields — has never been executed. Any
chapter written from either reading is arithmetic on an unregistered model.

**Amended the same day, and the sentence aged better than it looks.** P1 was executed hours after
this paragraph was written (§7). Its answer to the checkpoint named above is that no source this
directory can reach publishes it — `V-05-56` records the search, not a gap in it — so "the evidence
set contains nothing about that checkpoint" changed meaning from *nobody looked* to *there is nothing
there to look at*, which is a stronger finding and the one Issue #46 now has to decide against. The
same pass also falsifies this paragraph's last clause in the other direction: NeMo records now exist,
46 of them, and row 20's "no NeMo record exists" should be read as of the morning it was written.

**4.2 "The Voice Edge Benchmark" is one thing in the rules and two in the plan** (filed as #46).** `CLAUDE.md` requires
the **Voice Edge Benchmark** model to stay consistent across chapters, in the singular. `plan-v2.md`
§4.2 assigns two different models to two different tasks: keyword spotting with MatchboxNet or
SpeechCommands1 v2 at stages 4–6, streaming ASR with the NeMo Conformer at stages 8–10. The capstone
harness, `capstone/voice_edge_benchmark/README.md`, defines six measurement axes and names no model at
all. `book-en/chapter03.md` line 32 then asks for "a measured arithmetic intensity for the Voice Edge
Benchmark", which is a question with one answer only if the benchmark is one workload. It is not, so
chapter 3's missing number has to be split before it can be filled, and chapter 8's end-to-end
acceptance is a keyword-spotting build on a spine whose ASR model arrives at chapter 9.

**4.3 The structure gates count, they do not read.** `tests/test_plan_consistency.py` holds the spine
together by comparing chapter *numbers* across `plan-v2.md` §7, `docs/BOOK_STATUS.md`,
`docs/EXPERIMENT_STATUS.md` and `README.md`. It never compares titles, which is how `docs/BOOK_STATUS.md`
row 08 can still read "Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại" while
`book-en/chapter08.md` reads "Keyword Spotting on the Board: From Microphone to Decision" and
`scripts/verify_book_pdf.sh` expects the second. `book/TOC.md` line 17 states that chapter titles are
copied verbatim from `docs/BOOK_STATUS.md` so that no fifth source is created, and the build gate names
the other reading. A green gate is therefore not evidence that the spine agrees with itself. Report this
as a gate gap, not as a content error: it is the same class as `docs/PLAN_GAP_ANALYSIS.md` PROCESS-1.

**4.4 The plan's own buffer formula omits the block multiplier** (filed as #48).** `plan-v2.md` §6.7 rewrites `plan.md`'s
borrowed term "KV-Cache" as "Left-Context K/V Ring Buffer", gives the capacity as six factors, and closes
"tính ra con số". Every one of those factors is per attention block, and each encoder block holds its own
keys and its own values, so the capacity is that product times the number of blocks. At `V-05-04`'s twelve
blocks the omission is a factor of twelve, and the section written to stop a reader sizing memory from an
LLM analogy under-counts the same memory. The report inherited this rather than catching it, and any
diagram that prints the buffer from §6.7 as written will be wrong by that factor.

**4.5 The evidence set labels one tie rule the wrong way** (filed as #49).** `docs/verification/README.md:86` tabulates the
hardware side of the rounding trap as "round half away from zero (`+ (1 << (shift-1))`)". Run the idiom on
negatives, as §6 does: at `shift = 1` it sends `-0.5` to `0`, which is toward positive infinity. Away from
zero would send `-0.5` to `-1`. Both readings agree on the positive half, which is why a table that only
shows `0.5` and `1.5` can carry the error unnoticed, and this is the row the whole quantization chapter is
built on: an unsigned accumulator and a signed arithmetic right shift differ on negatives only. The same
words are in three places: `docs/verification/claims.json` inside `V-06-05`'s `notes` (line 1767 at
`main`), its render at `docs/verification/06-quantization-sources.md:103`, and `README.md:86`. The first two
are one edit plus a re-render, which is what `make render-evidence` is for. Filed as its own issue: a label
is a claim, and a rendered file is a mirror, so fixing the markdown alone would put the render out of step
with its own source.

**4.6 The record that decides the model's shape bundles five quantities, and its quote walks past its own
locator** (filed as #50). `V-05-04` carries five numbers in one field: its `value` reads
`d_model=256, 12 encoder blocks, 4 heads, linear_units=2048, cnn_kernel=15` and its `unit` is the literal
word `string`. `docs/WEB_SEARCH_PROTOCOL.md` rule 5 is "One record per quantity. Do not batch several
numbers into one prose paragraph." A bundle cannot be re-checked field by field, cannot be contradicted in
part, and cannot be looked up by one of its numbers. The locator is the other half of the defect. It says
"Lines 4-18, encoder_conf". Read against the file at the registered URL, the quote contains `causal: true`
and `use_dynamic_chunk: true`, which are lines 19 and 20, and it skips `activation_type: 'swish'`,
`pos_enc_layer_type: 'rel_pos'` and `selfattention_layer_type: 'rel_selfattn'`, which are lines 16, 17 and
18 and inside the stated range. A reader who cannot fetch decides what a record covers from its locator, so
a quote that leaves its range makes the locator false in both directions at once: it claims ground the quote
does not cover, and disclaims ground the quote does cover. Line 21, `cnn_module_norm: 'layer_norm'`, sits
just outside and is the line rows 15, 18 and 20 turn on. The fix is to split `V-05-04` into per-quantity
records with exact locators, quote the streaming and normalization lines, raise the version and re-render.
The split supersedes a bundle that three rows of this table and `plan-v2.md` cite by number, so the old id
has to stay resolvable rather than be edited into something else.

---

## 5. What happens next

Three branches, in this order, each with its own issue.

1. **This file.** Record the verdicts, so that the next session does not re-litigate them. The five
   defects in §4 that need their own fix are filed: **#47** for the model the spine names against the model
   the registry holds, **#46** for the benchmark that is singular in the rules and double in the plan,
   **#48** for the missing per-block multiplier, **#49** for the tie-direction label, **#50** for the
   bundled record and its out-of-range quote. §4.3 is a gate gap and stays in this file until it is
   written into a chapter.
2. **The fetch** — #47. Execute P1: identify the NeMo streaming Conformer-Transducer `small` checkpoint,
   then
   register layer count, `d_model`, heads, kernel size, parameter count, MACs per frame, INT8 weight
   bytes and activation bytes per frame as records with a quotation each. Where the registry's WeNet
   numbers disagree, `WEB_SEARCH_PROTOCOL.md` rule 6 applies: add the second record and raise a conflict,
   do not overwrite `V-05-04`.
   → Executed the same day: 46 records registered (`V-05-12 … V-05-57`) and C-08 raised. Its first sentence turned out to name a checkpoint no source publishes, and its last two quantities still have no number. §7.
3. **The prose and the pictures.** Re-cut the chapter 8 and 9 stubs to the resolved spine, then write
   them. The material is diagram-led by the owner's stated preference, and the book already has the
   machinery: a fenced div plus a `tikz` block becomes a numbered float through
   `scripts/filters/tikz_figures.lua`, and check 6 of `scripts/verify_book_pdf.sh` refuses a figure that
   no caption reached and prose that no figure answers. Four pictures are planned: the Conformer block
   as a dataflow with the tensor shape written on every edge; a chunked streaming step whose boundary is the
   chunk and not the frame, so the window inside the chunk has to be drawn bidirectional or the picture
   teaches claim 17; the softmax and LayerNorm pipelines side by side, showing a row waiting on its own
   reduction while the accumulator stays busy; and the requantization decision as a number line with the
   three tie behaviours drawn on it, negatives included, because that is where §4.5 lives. The buffer
   picture multiplies out per block and then by the block count, which is what keeps §4.4 from being
   drawn again. The convolution module is drawn with a LayerNorm because the registered config sets
   `cnn_module_norm: 'layer_norm'` at line 21 of `S016`'s file (#50), not because the report said
   BatchNorm; and if the fetch returns a NeMo checkpoint that does default to BatchNorm, row 20's
   fold-backwards note is what decides whether that stage exists in hardware at all.

Fields the fetch does not deliver stay visibly empty in the prose, the way chapter 3's figures label what
no record carries. A placeholder that admits it is a placeholder is the difference between an open number
and a fabricated one.

## 6. Method

Read-only against `main` at `4d5b887`, on 2026-09-14.

- `wc -l` and a line classifier over `book-en/chapter*.md` for the content counts in §2.
- `grep -rniE "attention" book-en/*.md` for claim 2. For the ranking, `git grep -ilE` over tracked `.md`,
  `.json`, `.yaml` and `.yml`, one term at a time: "MLOps", "HW-NAS", "architecture search",
  "ML Fundamentals", "Attention Theory". **Zero files for all five.** The same shape of search for
  "relative attention", "Transformer-XL" and "macaron" over tracked markdown and JSON returns nothing
  either, which is claim 18.
- Tooling, three ways. `git ls-files` filtered on `.v`, `.sv`, `.svh`, `.vhdl`, `.vhd`, `.xdc`, `.tcl`,
  `.ucf`: **0 tracked files**. `grep -rniE "golden|bit.exact|hex" --include="*.py" .`: three files, and
  every hit is a `hexdigest()` line. `pyproject.toml` read in full.
- Two arithmetic runs, one to check the report and one to check this repository. NumPy 2.5.2 gives
  `np.round([0.5, 1.5, 2.5, 3.5])` equal to `[0.0, 2.0, 2.0, 4.0]` and the negatives equal to
  `[-0.0, -2.0, -2.0, -4.0]`, which reproduces row 4. The fixed-point idiom `(v + (1 << (shift - 1))) >> s`
  at `shift = 1` maps `-3` to `-1`, `-1` to `0`, `1` to `1` and `3` to `2`: ties toward positive infinity,
  not away from zero, which is §4.5.
- Record-by-record reads of `V-01-06`, `V-01-11`, `V-01-22`, `V-05-01` to `V-05-09`, `V-06-04`, `V-06-05` out of
  `docs/verification/claims.json` (version 1.7.0, 103 records: 96 `verified`, 4 `unresolved`,
  3 `conflict`).
- Direct reads of `plan-v2.md` §4.2, §6.2, §6.3, §6.7, §7 and §8.4; `book/TOC.md` in full;
  `docs/BOOK_STATUS.md`; `docs/AGENT_FETCH_BRIEF_2026-09-12.md` §3; `docs/PLAN_GAP_ANALYSIS.md`;
  `docs/WEB_SEARCH_PROTOCOL.md`; `capstone/voice_edge_benchmark/README.md`;
  `tests/test_plan_consistency.py`; `scripts/verify_book_pdf.sh`.

**Not checked.** The report's account of the owner's job and of what his work involves, which is outside
the repository. The origin of the six-topic ranking, which is a conversation this repository has no copy
of; that is why claim 9 is judged against what the repo *does* order rather than against a baseline that
cannot be shown. Whether some NeMo recipe does in fact publish 16 encoder blocks — the report's number
may have a real provenance in a different model variant, and the fetch in step 2 is what will say. **Answered the same day: it does — §7.** And
the four-term decomposition of relative self-attention, which needs the Conformer paper quoted rather than
an audit; and the NeMo checkpoint's own field values, which no document in this repository has ever
carried.

**Provenance of this audit, stated plainly.** Two passes, independently. Pass one is the commands above,
run in this session. Pass two is an adversarial panel, workflow run `wf_13cfa314-af5`: eight agents each
assigned one load-bearing claim and told to refute it, with repository file and line citations required,
plus five fetch angles and a refutation pass over anything a fetch returned. All eight audit verdicts are
reflected above. `causal-mask`, `placement`, `ranking` and `roofline-fusion` came back wrong,
`rounding-accumulate`, `buffer-formula` and `softmax-stall` came back partly correct, and
`model-structure` came back a split judgement, all eight at confidence `high`. Rows 17, 19 and §4.4 exist
because of the panel; rows 15, 18 and 20 and §4.6 exist because its last verdict made this session open the
registered config and read it line by line. Two places where the panel and this session part company, recorded rather than
smoothed. The ranking agent wrote that attention "lives in Chapter 8", which is the stub reading; the
spine the owner resolved on 2026-09-13 puts the streaming Conformer overlay in chapter 9
(`book/TOC.md:139-166`), and row 10 and §5 follow the file. The model-structure agent also reported that
`V-05-04`'s quote "truncates away" `cnn_module_norm` "although its locator claims Lines 4-18". Measured,
that line is 21, so nothing was truncated from inside the stated range: the agent reached the right defect by
the wrong route. The defect is not the missing line but a quote that reaches past its locator to lines 19
and 20 while skipping lines 16 to 18, which is §4.6 and #50. The buffer agent also read `V-01-11` as the
2.88 MiB row and `V-01-22` as its unit chain; both are true, and row 5 cites both because `V-01-11` carries
status `conflict` while `V-01-22` carries the printed conversions. One infrastructure fact worth recording: the subagent model alias the owner maintains, `subagent`,
fails at the transport with `API Error: 400 unknown provider for model subagent`, measured again here on
2026-09-14 after the same result on 2026-09-13, so the panel ran under the `sonnet` spelling and the wire
label its proxy returned was `qwen3.8-flash`. The panel's agents are not Claude models in that run, and
their verdicts were accepted only where a file said so.

---

## 7. Amendment: what the fetch said back

Step 2 of §5 ran on 2026-09-14, on the branch `docs/nemo-target-spec`, and it changed an answer rather
than confirming one. Five things it settled, one number it left unregistered, and one checkpoint it
could not find.

**The report's 16 is right about a model this repository had never registered.** Row 8 read
**Contradicts** because `V-05-04` — WeNet's streaming Conformer recipe, 12 blocks, `d_model=256`, 4
heads, 15 taps — was the only architecture with a quotation behind it. It is still true, and still
WeNet's. Line 11 of NVIDIA's own Conformer-Transducer recipe prints a variant table whose Small (14M)
column reads 176 units, 4 heads, **16 blocks**, 31 taps, registered as `V-05-12 … V-05-16`, and whose
Large column reads 512 units, 8 heads, 17 blocks (`V-05-17 … V-05-19`). So the report's number and this
repository's number were never competing accounts of one thing; they are two networks. Row 8's verdict
moves from *contradicts the evidence* to *true of another model*, which for the book's purposes is the
same outcome — the chapter may not print it until the model it belongs to is chosen — and a different
outcome for the report's credibility, which is why the distinction is recorded rather than smoothed.

**"4 or 8 heads" is the same table read the same way:** 4 for Small, 8 for Large (`V-05-14`,
`V-05-19`). Both of the numbers row 8 named are therefore right about NeMo's family, and neither was
cited — an unsourced figure that happens to match a document is not a sourced figure, and §3's argument
about the mechanism is untouched.

**The third number in that arithmetic is still not registered, and it is not the 4 that now is.** The
report multiplies its block count by "4 sub-layers" to reach "64+ rounding operations", and no record in
this directory counts the sub-layers of a Conformer block: §6 already noted that "macaron" returns
nothing in any tracked file, and the fetch did not change that. What the streaming recipe does print at
`V-05-36` is `ff_expansion_factor: 4`, a width multiplier on the feed-forward inner layer. The two 4s
measure different things — one is a count of stages through which a frame passes, the other a ratio
between a layer's input and its intermediate width — and a later reader who confuses them will size the
rounding chain wrong by a factor of four while quoting a record.

**The convolution module's norm is LayerNorm, from the vendor.** §5 step 3 said the module would be
drawn with a LayerNorm because WeNet's config sets `cnn_module_norm: 'layer_norm'`, and asked what
would change if a NeMo checkpoint defaulted to BatchNorm instead. Both streaming NeMo recipes print
`layer_norm` (`V-05-26`, `V-05-41`); `batch_norm` appears only in the offline recipe (`V-05-20`). That
is the first-party answer to row 20's "why BN not LN here", and it narrows that row's other half. Row 20
wrote "BatchNorm is what NeMo's convolution module defaults to, and no NeMo record exists" — the
default is true of the framework and of the offline recipe, and it is not what either streaming recipe
prints. So the fold-backwards note is not the branch a streaming target takes: the normalisation whose
statistics come from the tensor in hand stays in the datapath, and the one that could be folded into the
convolution taps is the offline model's.

**Relative position is in the target.** `rel_pos` is printed by the offline recipe and by the streaming
Conformer (`V-05-21`, `V-05-27`), and the streaming recipe's own comment names the Transformer-XL
layers that option selects. Row 8's arithmetic may still be wrong about block counts, but the
positional term it leans on is real, and chapter 9 has to implement it.

**Right context, which no record carried before this.** The streaming Conformer prints `[140, 27]` with
subsampling 4 (`V-05-29`, `V-05-30`, `V-05-32`) and the streaming FastConformer `[70, 13]` with
subsampling 8 (`V-05-43`, `V-05-44`, `V-05-42`), each with the look-ahead formula written beside it in
the file — 1,080 ms and 1,040 ms respectively (`V-05-34`, `V-05-47`). The checkpoint catalogue states
the same look-ahead in its model names, so the formula and the catalogue check each other without
either being derived from the other. And the accuracy-versus-latency curve `plan-v2.md` §4.4 promises
turned out to be published already, for exactly one family: 7.0, 6.4, 5.7 and 5.4 % test-other WER at
0, 80, 480 and 1,040 ms of look-ahead (`V-05-52 … V-05-55`). Chapter 8's latency figure can therefore
be drawn from records instead of waiting on a run.

**What the fetch could not deliver, and why that is a decision.** Its first instruction was to identify
the NeMo *streaming* Conformer-Transducer `small` checkpoint. No source this directory reached
publishes one: the English score table's 27 rows contain no streaming Small, the recipe tree has no
streaming Small config, and the one route that could have settled it independently — the HuggingFace
catalogue — answers HTTP 401 to an anonymous request, so absence there proves nothing either way. That
is `V-05-56`, kept `unresolved` under rule 8 rather than written as a negative. The same fetch left
MACs per frame, INT8 weight bytes and activation bytes per frame without a number, because no publisher
prints them and computing them needs the checkpoint itself or a golden-model run — `V-05-57`. Between
them sit the two halves of C-08: the model the spine names does not exist as a published checkpoint,
and the streaming models that do print about 120 million and about 115 million parameters
(`V-05-33`, `V-05-46`) against the roughly 14 million the Small column prints (`V-05-16`). Choosing
between them is the owner's call, it is the same call Issue #46 asks about, and this directory has now
registered both options rather than picking one.
