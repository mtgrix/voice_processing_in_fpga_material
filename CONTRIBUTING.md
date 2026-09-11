# Contributing Guidelines — Voice Edge AI (Jetson Orin to FPGA)

Welcome to the **Voice Edge AI: From Jetson Orin to FPGA** learning journey and research monograph project.

We welcome contributions in the form of empirical experiments, mathematical derivations, hardware benchmarks, and manuscript improvements.

## Guiding Principles

1. **Empirical Reproducibility**:
   Every claim regarding speedup, energy efficiency (mJ/frame or TOPS/W), or accuracy (WER/PESQ) must be reproducible with a corresponding experiment in `chapterXX/` or `capstone/`.

2. **Pedagogical Governance**:
   All book chapters and pedagogical materials must strictly adhere to [`docs/BOOK_PEDAGOGY.md`](docs/BOOK_PEDAGOGY.md).
   - Local Sufficiency Principle
   - Three-Level Concept Introduction (Intuition → Mechanism → Application)
   - Acronym first-use rule

3. **Language Policy**:
   - Monograph chapters (`book/`): Vietnamese (canonical).
   - English edition / Paper drafts (`book-en/`): English.
   - Code, docstrings, tests, and research notes (`docs/`): English.

4. **Standards & Source Citations**:
   - Every hardware architecture or algorithmic claim must reference a registered source in `docs/source_index.json`.
   - Never copy external textbook prose directly. Synthesize, formalize, and cite.

## Contribution Workflow

We follow the standard GitHub workflow:
```text
Issue → Branch → Commits → PR → Automated Validation → Merge
```

- Run `make lint` and `make test` before opening a PR.
- Ensure all repository integrity tests pass.
