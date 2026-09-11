# Plan Audit — `plan.md` Gap Analysis

**Date:** 2026-09-12
**Scope:** Is `plan.md` sufficient to *learn* and *execute* migrating a streaming voice model from
NVIDIA Jetson Orin onto an FPGA board, to a standard that would survive NVIDIA / MIT-level review?
**Verdict:** **No.** See §1.
**Companion document:** [`plan-v2.md`](../plan-v2.md) — the rewrite. This file records the evidence.

> **Provenance of this audit (stated plainly).** Two multi-agent review panels were attempted and
> **both failed for infrastructure reasons, not because of the subject matter.** Panel 1
> (`wf_8c4d9590-53a`) stalled on 5 of 8 agents after ~108 minutes and 2.8 M subagent tokens; two
> complete reports survived (research-rigor, fpga-rtl-toolchain) and are folded in below. Panel 2
> (`wf_3c468567-034`, leaner, `plan.md` inlined, tool calls capped) had all 10 agent attempts
> interrupted at their **first** API call — 0 tool uses, 0 assistant messages, final journal record
> `[Request interrupted by user]`. Root cause is subagent launch, not prompt design: the prompt was
> 10.6 KB while each agent also received ~40 KB of injected context (17 KB of it a skill listing).
> **Everything below is therefore either (a) verified by command in this session, (b) arithmetic on
> the repository's own stated figures, or (c) from the two surviving panel-1 reports.** No claim here
> rests on a panel that did not complete.

---

## 1. Verdict

`plan.md` is a competent **architecture essay**. It is not a learning plan and not a research
protocol. It explains *why spatial dataflow is a reasonable idea* and never states *what the learner
does first, what they produce, and how anyone checks it*.

Three structural properties make it insufficient rather than merely incomplete:

1. **It cannot be executed.** It never names a Jetson SKU, an FPGA part number, a model, a dataset,
   a task, or a metric. Every downstream number is therefore unanchored.
2. **It cannot be falsified.** Its four quantitative claims have no derivation and no source that
   supports them. A claim that cannot be wrong cannot be defended at peer review.
3. **Its ordering is inverted.** Milestone 1 is "design the RTL"; milestone 2 is "measure the
   baseline". The architecture is asserted before the measurement that is supposed to justify it.

The repository's own validation suite is **green** while this is true: `pytest` 13 passed, `ruff`
clean, `verify_integrity.py` PASS. That is the most important finding in this document — see §4.

---

## 2. Keyword absence census (verified by `grep` over `plan.md`)

Each of the following appears **zero** times in `plan.md`:

| Absent concept | Why it is load-bearing |
|---|---|
| prerequisite / tiên quyết | The plan silently assumes 4 independent skills |
| dataset / SpeechCommands / LibriSpeech | No data ⇒ no reproducible accuracy number |
| microphone / I2S / PDM | The audio input path does not exist in the document |
| BOM / cost | No board has been bought |
| tool version / JetPack / Vivado | Nothing is pinned ⇒ nothing is reproducible |
| schedule / tuần / giờ | No time budget for a multi-month project |
| exercise / rubric | Nothing for a learner to *do*, nothing to grade |
| related work | Automatic reject at FCCM/FPGA |
| null hypothesis | The central claim is never testable |
| seed / repetition / stddev / confidence | Single-run numbers are not results |
| CTC / beam / decode | The output stage is missing entirely |

Verified by: `grep -c` over `plan.md` for each term family.

---

## 3. Findings by severity

### BLOCKER-1 — Fabricated benchmark data, asserted on by the test suite

`capstone/voice_edge_benchmark/benchmark_runner.py::build_default_benchmark_suite()` returns four
hand-written result rows, with the docstring *"Instantiate reference comparative data reflecting
empirical publications"*, and `__main__` prints them under the heading **"Academic Benchmark
Matrix"**. `tests/test_audio_pipeline.py` asserts against them.

| Row (as written in code) | Latency | Power | mJ/frame | "accuracy" | FPS/W |
|---|---|---|---|---|---|
| Orin Nano FP16 | 2.15 ms | 8.8 W | 18.92 | 97.4 % | 52.8 |
| Orin Nano INT8 | 1.45 ms | 8.2 W | 11.89 | 97.2 % | 84.1 |
| KV260 DPU | 1.10 ms | 4.8 W | 5.28 | 97.1 % | 189.4 |
| KV260 FINN | 0.48 ms | 3.9 W | 1.87 | 96.9 % | 534.2 |

None of these is measured. They directly contradict the repository's own rule
(`AGENTS.md`: *"Do NOT mark ✅ or fabricate benchmark data unless actual code runs and outputs real
evidence"*) and its traceability rule (`CLAUDE.md`: *"All empirical claims must be traceable to
registered sources or captured benchmark logs"*).

**Why it is the top item:** it is the single fastest way to destroy both the publication goal and
the author's credibility, and CI currently certifies it. A reviewer who runs `make test` sees green
and may reasonably assume the numbers are validated.

**Fix:** `plan-v2.md` §9.2 (rename to `synthetic_demo_fixture()`, add a `provenance` field, make
tests assert structure only, add an integrity gate that refuses ✅ without a raw log).

### BLOCKER-2 — No device selection on either side of the comparison

"Jetson Orin" is a **product family** (Nano / Nano Super / NX / AGX 32 GB / AGX 64 GB) differing in
SM count, LPDDR5 bandwidth, DLA presence, and power envelope. "Kria KV260" implies a part
(`xczu5ev`) and a speed grade that are never stated. Without both pinned, the entire Pareto
comparison has no axes.

**Fix:** `plan-v2.md` §3.1–3.2, plus `docs/DATASHEET_VERIFICATION.md`.

### BLOCKER-3 — No verification methodology

`plan.md` describes the *function* of hardware blocks (Line Buffer, Requantizer, Ring Buffer) and
never their *specification*. Absent: golden model, vector generation, cocotb/Verilator, assertions,
coverage, bit-exact gate, ILA on-board correlation. There is no Q-format, no accumulator width, and
no rounding mode anywhere in the document.

Rounding-mode mismatch between the quantizer library and the RTL is the canonical multi-week bug in
this class of project; a plan that never fixes a rounding convention will produce RTL that passes a
testbench written to match it and fails reality.

**Fix:** `plan-v2.md` §6.2–6.3. Note `pyproject.toml` currently has **no** `cocotb` and no RTL
simulator dependency, so the fix also requires dependency changes (§8.4).

### BLOCKER-4 — No clocking, constraints, or timing closure

Zero occurrences of clock domain, CDC, XDC, `create_clock`, or WNS. A design that never closes
timing does not exist on a board.

**Fix:** `plan-v2.md` §6.4.

### BLOCKER-5 — The on-chip memory figure is wrong, and the plan budgets against it

Three values for one quantity:

| Location | Claim |
|---|---|
| `plan.md:55` | "chỉ khoảng **4 MB** trên Kria KV260" |
| `docs/research_notes/R02_fpga_audio_streaming.md` | "144 BRAMs and 64 URAMs, providing **~4.5 MB**" |
| Arithmetic on R02's own block counts | 144×36 Kb + 64×288 Kb = 23 616 Kb ≈ **3.02 MB** |

The refutation of 4.5 MB requires **no datasheet** — it is addition over the block counts the note
itself states. `docs/SOURCES.md` gives "256K LUTs, 1.2K DSP slices" and no memory figure, so none of
the three values is sourced.

Consequence for `plan.md` §3, which uses "4 MB" as the denominator justifying a BRAM partition for
its KV-Cache, against a model it says is "10–30 M parameters":

| Model | INT16 | INT8 | INT4 |
|---|---|---|---|
| 10 M params | 20 MB — 6.6× over | 10 MB — 3.3× | 5 MB — 1.7× |
| 30 M params | 60 MB — 19.8× | 30 MB — 9.9× | 15 MB — 5.0× |

Even at INT4 the model does not fit. The "zero off-chip memory traffic" argument in `R02` holds only
for small KWS-class networks. **The plan's central memory premise is arithmetically false as
written**, and the fix is not a corrected number but splitting the work into two programs
(`plan-v2.md` §4.2, §7 chặng 4 vs 9).

### MAJOR-1 — Underived quantitative claims, one with a misattributed source

`plan.md` makes four percentage claims (lines 32, 36, 58, 64): "80–90 % DSP", "100 % integer",
"75–87 % DRAM bandwidth", "50 % DRAM bandwidth". **Zero have a derivation.**

`[R01-02]` (FINN, a *binarized* NN framework) is cited three times for three different things:
spatial dataflow (line 25, defensible), **affine quantization theory** (line 58, wrong — FINN is not
the source of affine quantization), and HLS/FINN (line 85, duplicate).

Deeper: `plan.md` §1.4 invokes *affine* quantization `r = S(q − Z)` and claims it is anchored in
`source_index.json`, but the registered note for it — `R03_quantization_for_speech.md` §2 — is
titled "Mathematical Uniform **Symmetric** Quantization Contract" and derives
`S = x_max / (2^(b−1) − 1)`, i.e. the **zero-point-free** case. The theory cited is not in the
source registered.

**Fix:** `plan-v2.md` §9.1.

### MAJOR-2 — Milestone ordering inverts the empirical logic

Milestone 1 = RTL design; milestone 2 = baseline measurement. It also contradicts
`docs/BOOK_STATUS.md`, where chapters 1–3 are foundations and measurement and FPGA work starts at
chapter 4. A learner following `plan.md` commits to a microarchitecture before knowing what the
bottleneck is.

**Fix:** `plan-v2.md` §7 — measure at chặng 2–3, with an explicit H0-A gate that can redirect the
project.

### MAJOR-3 — No learner model at all

No prerequisites, no self-diagnostic, no hours, no schedule, no exercises, no rubric, no exit
criteria, no failure budget, no early win. The first tangible success in `plan.md` is a working RTL
convolution core, months in. For a self-learner that is where the project dies.

**Fix:** `plan-v2.md` §2 (prerequisites + E0 early win), §7 (per-stage entry/artefact/gate,
36–58 week estimate), §7.1 (failure budget).

### MAJOR-4 — No audio input path, no decoder, no latency budget

The plan starts at "waveform" and never says where audio comes from; and it designs an encoder while
omitting the decode stage, whose CPU and memory cost on edge is frequently larger than the encoder's.
"Chunk-based attention" is named without defining rightaway/future-context or an end-to-end latency
budget — which is precisely the axis speech reviewers demand.

**Fix:** `plan-v2.md` §4.1, §4.3, §4.4.

### MAJOR-5 — Task/model confusion

`plan.md` §1 frames the problem as "Streaming ASR" but cites MatchboxNet `[R01-05]`, a **12–35 class
command classifier**, as the architectural basis. MatchboxNet has **no WER**. Any metric table mixing
the two is ill-defined. The plan also never names a concrete model, layer count, `d_model`, head
count, or parameter count it actually intends to build.

**Fix:** `plan-v2.md` §4.2, §5.3.

### MAJOR-6 — No research protocol

No related work, no null hypothesis, no seeds/repetitions/confidence intervals, no ablation plan, no
threats to validity, no artifact evaluation. `docs/RESEARCH_METHODOLOGY.md` already contains a metric
matrix, the matched-power rule, and an 8-section paper structure — **and `plan.md` never references
it.** The material exists; the plan just does not use it.

**Fix:** `plan-v2.md` §5, which cites `RESEARCH_METHODOLOGY.md` explicitly rather than restating it.

### MAJOR-7 — "Hardware KV-Cache" borrows an LLM term that does not apply

Streaming Conformer state is a bounded left-context window over K/V per chunk, not an autoregressive
cache that grows with token count. Using the LLM name makes reviewers misread the design and leads
the learner to size the memory wrongly.

**Fix:** `plan-v2.md` §6.7 — rename to "Left-Context K/V Ring Buffer" with an explicit capacity
formula.

### MAJOR-8 — No model-update story

Nothing in the plan answers "how do I ship a new model without rewriting RTL?" This is practitioners'
first objection to FPGA deployments and the difference between a system and a one-off demo.

**Fix:** `plan-v2.md` §7.2.

### MINOR-1 — Heading numbering collides

`## 1. BÀI TOÁN GỐC`, then an **unnumbered** `## CƠ SỞ LÝ THUYẾT` containing its own `### 1.`–`### 4.`,
then `## 2.`–`## 5.`, then unnumbered `## TỔNG KẾT` and `## TÀI LIỆU THAM KHẢO`. Two headings read as
"1" at two levels.

### MINOR-2 — Inflated naming violates the repo's own pedagogy doc

"Định lý Tính toán Không gian" and "Lý thuyết … chứng minh rằng giảm 80–90 %" are neither a theorem
nor a proof, contradicting `docs/BOOK_PEDAGOGY.md` §6 (mathematics must explain a mechanism, and must
state what cannot be inferred). Acronym first-use rule (§5) is also broken for II, HLS, QAT, MAC,
FSM, DSP, DPU, STFT, ASR, KWS, WER.

### MINOR-3 — Source ID scheme cannot scale

Every id in `docs/source_index.json` carries the chapter-scoped prefix `R01-` (`R01-01`…`R01-05`), so
adding a source for chapter 2 breaks the scheme. The source→note mapping is also crossed:
`R01-04` (AMD Kria user guide) points at `R01_jetson_orin_arch.md`, an NVIDIA note, and `R01-03`
(Conformer, an attention architecture) points at `R03_quantization_for_speech.md`.

**Fix:** `plan-v2.md` §9.4 — global `S<NNN>` ids plus a `claims_supported` field so the linkage can be
checked in both directions.

---

## 4. Process findings (these are about the repository, not the prose)

### PROCESS-1 — CI certifies shape, not substance

Verified state: `pytest` **13 passed**, `ruff check` clean, `ruff format --check` clean,
`scripts/verify_integrity.py` **PASS**. Alongside that:

- `book/` contains **2046 words** outside HTML comments; every `## X.Y` body is a `<!-- TODO -->`.
- `pyproject.toml` sets `testpaths = ["tests", "chapter01", "chapter02"]` — **chapters 03–10 have no
  code at all**.
- `verify_integrity.py` checks only: JSON parses, ids unique, note files exist, no prompt-marker
  leakage. It does **not** check that any claim links to any source.
- `tests/test_pedagogy.py` checks only file existence, one sidebar string, and 13 numbered headings.
- `tests/test_repo_integrity.py` checks the same two things as `verify_integrity.py`.

A green suite is therefore not evidence of progress here, and the fabricated-data rows in BLOCKER-1
pass through it unchallenged.

### PROCESS-2 — `plan.md` and `book/TOC.md` are untracked and referenced by nothing

`git status`: `?? plan.md`, `?? book/TOC.md`, `?? .agents/`, `M AGENTS.md`. A repo-wide `grep` across
`*.md`, `*.py`, `*.json`, and `Makefile` finds **no reference** to `plan.md` or `TOC.md`. Consequence:
the 5-vs-10 chapter drift between these two files and `README.md` / `docs/BOOK_STATUS.md` /
`docs/EXPERIMENT_STATUS.md` / `tests/test_pedagogy.py` is **undetectable by any existing test**, and
`plan.md` is unrecoverable if overwritten — which is why this audit writes `plan-v2.md` and leaves
`plan.md` untouched.

### PROCESS-3 — The GitHub process has never run

`CLAUDE.md` mandates `Issue → Branch → Commits → PR → Validate → Merge`. Verified state:

| Check | Result |
|---|---|
| `git ls-remote origin` | **empty** — zero refs, nothing ever pushed |
| `gh api repos/mtgrix/voice_processing_in_fpga_material` | `size: 0`, `empty: true`, private, created 2026-09-11T16:10:34Z |
| Issues on origin | **0** |
| Branches | local `main` only; 2 local commits, no remote branch |
| `gh auth status` | logged in as **`MinhTuan76800310`** |
| `origin` owner | **`mtgrix`** — a different account |
| README BibTeX `url` | `github.com/MinhTuan76800310/voice_jetson_to_fpga_learning-journey` → **HTTP 404, does not exist** |
| `.github/workflows/` | **absent** — there is no place for "Validate" to run |

Two commits exist locally and have never been pushed. The account that `gh` is authenticated as is
not the account that owns the configured remote, and the URL the README cites as the project's own
canonical location returns 404. **This must be resolved by the owner; it is not something to work
around silently**, because pushing or opening issues would act as one account against another
account's private repository.

---

## 5. What `plan.md` gets right

Kept in `plan-v2.md` unchanged in substance:

- The `batch=1` framing is the correct root cause for why streaming voice behaves differently from
  vision on a GPU.
- Line buffer / shift-register over static-SRAM copying is the right mechanism, and the reasoning
  (avoiding array-shift cost) is sound.
- Depthwise-separable factorisation as the DSP-count lever is correct — it just needs the derivation
  and a measured number instead of "80–90 %".
- Requantization as integer-multiply-plus-shift, with clamping, is the correct hardware formulation —
  it needs a fixed rounding convention and a bit-exact test to be actionable.
- Verilog-for-the-core → HLS/FINN-for-scale is the right scalability argument.
- The three-level Intuition → Mechanism → Application pedagogy is genuinely good and is preserved.

---

## 6. Recommended order of work

| # | Action | Blocking? |
|---|---|---|
| 1 | Resolve the Git identity/remote/404 question (§4 PROCESS-3) | **Yes** — nothing can be "done" per `CLAUDE.md` until this is |
| 2 | Quarantine the synthetic benchmark fixture; add `provenance`; fix the tests | **Yes** — BLOCKER-1 |
| 3 | `git add plan.md`; delete or regenerate `book/TOC.md`; add `test_plan_consistency.py` + `make gate` | Prevents recurrence |
| 4 | Create `docs/DATASHEET_VERIFICATION.md`; fill the memory/LUT/DSP/bandwidth cells from real PDFs | Gates every later number |
| 5 | Adopt `plan-v2.md`; rewrite `plan.md` claims that survive into sourced or derived form | |
| 6 | Add `.github/workflows/ci.yml` running `make gate` | |
| 7 | Add `brevitas`, `cocotb`, coverage tooling to `pyproject.toml` with pinned versions | |
| 8 | Execute `plan-v2.md` chặng 0 → 3 before writing any RTL | The H0-A gate may change the project |

---

## 7. Method

Evidence gathered by command in this session: `git status`/`branch -a`/`log`/`ls-remote`;
`gh auth status`; `gh api` against the remote repo and its issue list; `pytest`; `ruff check`;
`ruff format --check`; `python scripts/verify_integrity.py`; `grep` censuses over `plan.md` for
quantitative claims, citation positions, heading tree, and absent-keyword families; full reads of
`plan.md`, `book/TOC.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `Makefile`, `pyproject.toml`,
`docs/BOOK_STATUS.md`, `docs/EXPERIMENT_STATUS.md`, `docs/RESEARCH_METHODOLOGY.md`,
`docs/BOOK_PEDAGOGY.md`, `docs/SOURCES.md`, `docs/source_index.json`, all three
`docs/research_notes/*.md`, `tests/test_audio_pipeline.py`, `tests/test_pedagogy.py`,
`tests/test_repo_integrity.py`, `scripts/verify_integrity.py`, `capstone/voice_edge_benchmark/benchmark_runner.py`,
`chapter01/exp_01_streaming_audio_pipeline.py`, `chapter02/exp_02_jetson_orin_profiler.py`;
and arithmetic on the repository's own stated block counts and parameter ranges.

No hardware datasheet was consulted and no datasheet figure is asserted in this document. Where a
number is needed that could not be verified from a file in this repository, the finding asks for a
verification step instead of supplying a value.
