# CLAUDE.md — Voice Edge AI: Jetson Orin to FPGA

## Goal

Build this repository as:

1. A high-impact, rigorous **Voice Edge AI learning monograph**, and
2. An empirical, reproducible **research platform for publishing scientific papers** on migrating streaming voice models from Jetson Orin to FPGA kits.

---

## GitHub Workflow

For meaningful work, always follow:

```text
Issue → Branch → Commits → PR → Validate → Merge
```

Rules:
* Do not do planned work directly on `main`.
* Every non-trivial task needs a real GitHub Issue.
* Create a branch from updated `main`.
* One branch = one coherent task.
* Push meaningful checkpoints.
* Open a PR to `main`.
* Never invent Issue/PR/tag/release numbers.
* Verify Git/GitHub state before saying work is pushed, merged, released, or done.

---

## Before Working

Check Git status/history and read:

```text
CLAUDE.md
AGENTS.md
docs/BOOK_STATUS.md
docs/BOOK_PEDAGOGY.md
docs/RESEARCH_METHODOLOGY.md
```

For chapter or paper work, inspect corresponding research notes in `docs/research_notes/` and source registry in `docs/source_index.json`.

---

## Monograph & Paper Rules

* Book prose: Vietnamese (canonical).
* Paper drafts / English edition: English.
* Keep English technical terms on first occurrence.
* Write original explanations, formal proofs, and code; do not copy sources.
* All empirical claims must be traceable to registered sources or captured benchmark logs.
* Follow `docs/BOOK_PEDAGOGY.md`.
* Keep the **Voice Edge Benchmark** model consistent across chapters.

---

## Validation

Before merge or completing a task, run relevant checks:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
python scripts/verify_integrity.py
```

Never report unverified results.
