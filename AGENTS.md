# Agents Guide — voice-edge-jetson-to-fpga

This repository is designed for AI-assisted research and monograph authoring. Follow these rules when working on this project.

## Project Scope

The topic of this repository is **Edge Voice AI Hardware Acceleration**: migrating voice processing models (e.g. Keyword Spotting, Speech Enhancement, Streaming ASR/Conformer) from **NVIDIA Jetson Orin** (Edge GPU) to an **FPGA kit** (AMD Xilinx Kria / Zynq UltraScale+).

**Do NOT conflate with other topics (such as Knowledge Graphs).**

## Language Policy

- **Book drafts** (`book/`, chapter skeletons, experiment READMEs): Write in English level b2
- **English monograph / Paper drafts** (`book-en/`): Write in **English**.
- **Code, tests, configs, docs/**: Write in **English**.
- **Commit messages**: English, conventional commits format (`feat:`, `fix:`, `docs:`, `test:`, `perf:`).

## Pedagogy & Authoring Policy

1. Follow `docs/BOOK_PEDAGOGY.md` for chapter structure:
   - Local Sufficiency Principle.
   - Defer Depth, Never Required Understanding.
   - Three-Level Concept Introduction: Intuition → Mechanism → Application.
   - Minimal Mathematics Sidebar requirement for chapters with math.
2. Follow `docs/RESEARCH_METHODOLOGY.md` for academic rigor and benchmarking standards.
3. Every claim or hardware metric must reference an authoritative source registered in `docs/source_index.json`.

## Experiment Standards

Every experiment directory MUST have a `README.md` conforming to the 13-section template:
1. Experiment Metadata & Purpose
2. Theoretical Context & Pedagogical Goal
3. Hardware Target (Jetson Orin vs. FPGA)
4. Mathematical Derivation / Algorithm
5. Input Signal & Dataset Specs
6. Execution Command
7. Expected Numerical Output / Tolerances
8. Profiling & Measurement Methodology
9. Empirical Results & Artifacts
10. Hardware-Software Trade-offs
11. Limitations & Assumptions
12. Pedagogical Takeaways
13. Source Citations

Status markers:
- 🚧 = Design phase / Scaffolded
- 📖 = Hardware-in-the-loop / Manual execution required
- ✅ = Executed successfully with verified output and captured logs

Do NOT mark ✅ or fabricate benchmark data unless actual code runs and outputs real evidence.

## Key Mental Models

1. **Voice Edge System = Audio Preprocessing / DSP + Neural Acoustic Model + Hardware Microarchitecture**
2. **Hardware Migration = Profiling & Bottlenecks (GPU) → Hardware-Aware Quantization → Spatial Architecture Mapping (FPGA) → Pareto Verification**

## Code Quality

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

## Cognitive & Reasoning Harness (Pro-Emulation Protocol)

When processing instructions, the agent MUST strictly adhere to the 5-phase cognitive framework defined in [.agents/rules/thinking_harness.md](.agents/rules/thinking_harness.md):
1. **Intent Decoding & Problem Deconstruction**: Identify core vs. implicit goals, inventory hardware/system constraints, enforce the anti-rushing rule.
2. **First-Principles & Architectural Grounding**: Anchor problems into Key Mental Models (DSP + Acoustic Model + Microarchitecture).
3. **Multi-Hypothesis & Stress-Testing**: Brainstorm at least two viable approaches, failure modes, and trade-offs before deciding.
4. **Pre-Execution Verification Protocol**: Explicitly define verification tests, lint checks, and numerical tolerances before modifying code.
5. **Structured Execution & Self-Correction**: Atomic steps with root-cause critique on errors instead of guessing.

## Autonomous Execution (YOLO Mode)

- Full autonomy is enabled for this project: terminal commands, file edits/reads, and testing run proactively without unnecessary confirmations.
- Proactively verify changes using tests and linters before reporting back.


## Pedagogy Harness

When writing or revising book prose (`book-en/`, `book/`), follow [.agents/rules/pedagogy_harness.md](.agents/rules/pedagogy_harness.md) in addition to the structure rules in `docs/BOOK_PEDAGOGY.md`. The harness rules are the voice layer: invisible scaffolding (no `V-xx-yy` or audit meta-language in prose, no numbers spelled out), the four-beat cadence, accessible mathematics, and the pre-merge five-question checklist. `make check-prose` enforces the mechanical parts.
