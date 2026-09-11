# Agents Guide — voice-edge-jetson-to-fpga

This repository is designed for AI-assisted development and scientific research. Follow these rules when working on this project.

## Language Policy

- **Book content** (`book/`, chapter READMEs, experiment READMEs): Write in **Vietnamese**. Keep technical terms in English on first occurrence: "lượng tử hóa thích ứng phần cứng (hardware-aware quantization)", "luồng dữ liệu không gian (spatial dataflow)".
- **English monograph / Paper drafts** (`book-en/`): Write in **English**.
- **Code, tests, configs, docs/**: Write in **English**.
- **Commit messages**: English, conventional commits format (`feat:`, `fix:`, `docs:`, `test:`, `perf:`).

## Before Writing Chapter Content or Research Papers

1. Read `docs/BOOK_PEDAGOGY.md` — the canonical authoring policy for concept introduction, forward references, and reader-friction review.
2. Read `docs/RESEARCH_METHODOLOGY.md` — guidelines on scientific rigor, benchmarking setup, and paper structure.
3. Read `docs/SOURCES.md` and `docs/source_index.json` to identify authoritative sources for the topic (NVIDIA, AMD/Xilinx, IEEE, ACM, NeurIPS).
4. Never copy text from external sources. Research, understand, derive originally, and cite.

## Experiment Standards

Every experiment MUST have a `README.md` with all required sections:
1. Experiment Metadata & Purpose
2. Theoretical Context & Pedagogical Goal
3. Hardware Target (Jetson Orin vs FPGA Kit)
4. Mathematical Derivation / Algorithm
5. Input Signal & Dataset Specs
6. Execution Command
7. Expected Numerical Output / Tolerances
8. Profiling & Measurement Methodology (Latency, Power, Memory)
9. Empirical Results & Artifacts
10. Hardware-Software Trade-offs
11. Limitations & Assumptions
12. Pedagogical Takeaways
13. Source Citations

Status markers mean:
- ✅ = Actually executed successfully with captured evidence
- 📖 = Requires external hardware kit or manual reproduction
- 🚧 = Design/research exercise, not yet implemented

Never mark ✅ without running the experiment and capturing real output.

## Code Quality

```bash
python -m ruff check .        # Lint
python -m ruff format .       # Format
python -m pytest              # Test
python -m mypy .              # Type check (when configured)
```

All checks must pass before declaring work complete.

## Capstone Domain

The recurring capstone is the **Voice Edge Benchmark** under `capstone/voice_edge_benchmark/`. All chapters should contribute modular kernels, acoustic front-ends, or quantization layers that build toward this benchmark comparing NVIDIA Jetson Orin with an FPGA kit (e.g. AMD Xilinx Kria KV260 / ZCU104).

## Key Mental Models

Always frame content through these two models:

1. **Voice Edge System = Streaming Audio Pipeline + Neural Acoustic/Spectral Graph + Hardware Microarchitecture**
2. **Hardware Migration = Profiling & Bottlenecks → Hardware-Aware Quantization → Architecture Mapping → Pareto Verification**

State explicitly that Model 1 and Model 2 are engineering learning and research models, not universal formal definitions.

## Autonomous Execution (YOLO Mode)

- Full autonomy is enabled for this project: terminal commands, file edits/reads, and testing run proactively without unnecessary confirmations.
- Proactively verify changes using tests and linters before reporting back.
