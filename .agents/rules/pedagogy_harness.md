# Pedagogy Harness — how a voice-edge chapter tells its story

This harness is the *voice* layer of authoring. `docs/BOOK_PEDAGOGY.md` is the *structure*
layer (local sufficiency, three-level introduction, equation card, traceability, pipeline,
figures). This file says how the prose must feel: the reader should never be able to see the
evidence machinery underneath, and should *always* be able to see the physics.

A chapter that obeys every structural rule can still fail this harness. Both must pass.

---

## Why these rules exist

The book is driven by cognitive science, not by convention.

* **Cognitive Load Theory.** Remove extraneous load (evidence codes, audit meta-language,
  spelled-out numbers) so working memory spends itself on the intrinsic load (the signal-path
  idea) and germane load (building the mental model).
* **Dual Coding & Mental Models.** A concept arrives twice: as a picture (TikZ figure) and as
  a sentence. The sentence must be the picture's spoken version, not a transcription of a
  spreadsheet.
* **Feynman's ladder.** Explain first-principles intuition → mechanism → formalism. Every
  formula in this book walks a reader up that ladder; none of them is the summit by itself.

The narrative arc of a good section is: **tension → naive attempt → collision → breakthrough
→ price**. A melody without friction is a statistic. The *collision* (what makes a GPU
approach wrong for this hardware) is where the reader learns.

---

## RULE 1 — Invisible Scaffolding (Giàn giáo ẩn)

The reader never sees the evidence machinery. Concretely, in **prose**:

* **No `V-xx-yy` ids.** Not parenthesized, not inline, not in backticks on a prose line. The
  id is a pointer to an evidence file; inside a sentence it cuts the clause the reader is
  following. Traceability lives **only** in the end-of-section table (BOOK_PEDAGOGY §8).
* **No audit meta-language.** No "the records say", "no record in this registry", "a
  registered figure", "which record says", "the trail stops here", "this is a registered gap
  rather than an omission". If a sentence is about the evidence system rather than about the
  signal path, it is the wrong sentence.
* **No numbers written as words** for quantities: write `1,248 DSP slices`, not "one thousand
  two hundred and forty-eight hardened multiply-accumulate slices"; write `16 kHz`, not
  "sixteen kilohertz". Numbers below 13 stay as words by English convention ("the four
  paths", "eight-bit"), but a measured quantity at or above 13 is always digits.

The checks: `scripts/verification/prose_cage.py` fails the gate on all three, with the
present debt recorded in `docs/verification/prose_baseline.json`. A chapter that must shrink
that baseline before it is called done.

---

## RULE 2 — Four-beat pedagogical cadence (Nhịp 4 nhịp)

Every teachable idea gets exactly these four beats, in order:

1. **Physical Intuition & Friction.** What is it, physically, and what hurts? Why does the
   GPU version pay the price this chapter is about (latency, energy, memory traffic)?
2. **Microarchitectural Mechanism.** The hardware that answers it: dataflow diagram,
   pipeline structure, what a DSP slice or a BRAM tile actually does here.
3. **Human-Centric Mathematics.** The few formulas that make the mechanism precise. Variables
   are introduced by what they are, with units, before they appear in an expression.
4. **Hardware Trade-off & Reality.** What it costs in silicon, what breaks, and what the
   measured or registered numbers say about the real part.

A section that jumps straight to beat 3 has no reader. A section that stays in beat 1 has no
substance.

---

## RULE 3 — Accessible mathematics

* Intuition before formula, always: name what the quantity *is* before writing it.
* Every variable is bound to a physical entity and a unit at first use (the equation card in
  BOOK_PEDAGOGY §7).
* Use dimensional analysis to make the mechanism obvious ("samples per second times seconds
  per hop leaves samples, which is what a hop holds").
* The math explains the hardware mechanism; it never exists to impress. If a formula does not
  change what the reader expects from the silicon, cut it.

---

## RULE 4 — Cognitive empathy and tone

* Voice: an NVIDIA chief architect or an MIT professor explaining, from memory, why their own
  earlier design was half right. Confident, concrete, first-person-plural, zero defensiveness.
* Anticipate the misconception and name it: *"A very common mistake engineers make when moving
  from GPU to FPGA is thinking that …"* — then show the collision.
* A claim's strength matches its evidence. Where the registry is silent, say so with an honest
  gap ("we do not have a measured figure for X") — one plain sentence — never with verdicts
  about the record system.
* Never outsource a judgment to the reader's trust in the author. Every number is argued, not
  just printed.

---

## Pre-merge self-check (five questions)

Before any chapter PR merges, answer all five honestly:

1. Is there a single `V-xx-yy` id anywhere in prose (backticks included)?
2. Is there any audit meta-language sentence ("the records say", "registered gap", …)?
3. Is any measured quantity spelled out in words instead of digits?
4. Is the section locally sufficient for a good FPGA-new engineer who read only up to here?
5. Does the math explain a hardware mechanism, or is it decoration?

A "yes" to 1-3 or a "no" to 4-5 is a review-blocker.
