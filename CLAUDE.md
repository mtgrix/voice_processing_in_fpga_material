# CLAUDE.md — Voice Edge AI: Jetson Orin to FPGA

## Goal

Build this repository as:

1. A high-impact, rigorous **Voice Edge AI learning monograph**, and
2. An empirical, reproducible **research platform for publishing scientific papers** on migrating streaming voice models from Jetson Orin to FPGA kits.

---

## GitHub Workflow

For meaningful work, always follow:

```text
Issue → Create new Branch → Commits on new branch → PR → Validate → Merge -> delete merged branch
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

* Book prose: English level b2 (canonical).
* Paper drafts / English edition: English.
* Keep English technical terms on first occurrence and explan when first meet in simple English.
* Write original explanations, formal proofs, and code; do not copy sources.
* All empirical claims must be traceable to registered sources or captured benchmark logs.
* Follow `docs/BOOK_PEDAGOGY.md`.
* Keep the **Voice Edge Benchmark** model consistent across chapters.

---

## Validation

Before merge or completing a task, run the checks relevant to what you changed. `make gate`
runs all of them, which is exactly what CI runs, so a green `make gate` locally means a green
CI. There is no make binary on every machine; the `gate` target in `Makefile` lists the
individual commands, and they are repeated below -- the target is authoritative if the
two ever disagree.

```bash
make gate                                  # everything, in one command
python -m pytest                           # unit and book-code tests
python -m ruff check .                     # lint
python -m ruff format --check .            # formatting
python -m mypy .                           # type hints
python scripts/verify_integrity.py         # source registry and chapter claims
python scripts/verification/audit_claims.py   # docs/verification evidence checks
python scripts/verification/render_claims.py --check  # markdown matches claims.json
python scripts/verification/build_source_index.py --check  # registry matches its spec
python scripts/verification/build_bibliography.py --check  # .bib matches the registry
python scripts/verification/scan_numbers.py --check  # every printed number traces to a claim its section cites
python scripts/verification/figure_numbers.py  # every prose "Figure N" is the number that float gets
```

Never report unverified results.

# workflow & subagent spawn
Always use ANTHROPIC_DEFAULT_SONNET_MODEL model for subagent.
