PYTHON ?= python

.PHONY: help test lint format format-check typecheck verify verify-evidence check-render render-evidence check-registry render-registry gate book book-check book-clean clean

help:
	@echo "Available commands:"
	@echo "  make test              - Run pytest test suite"
	@echo "  make lint              - Run ruff linter"
	@echo "  make format            - Format code with ruff"
	@echo "  make format-check      - Check formatting without rewriting"
	@echo "  make typecheck         - Run mypy static type checking"
	@echo "  make verify            - Run repo integrity and validation scripts"
	@echo "  make verify-evidence   - Audit docs/verification: every quote must be able to produce its value"
	@echo "  make check-render      - Fail if the record .md files drift from claims.json"
	@echo "  make render-evidence   - Regenerate the record .md files from claims.json"
	@echo "  make check-registry    - Fail if docs/source_index.json drifts from its spec and claims.json"
	@echo "  make render-registry   - Regenerate the source registry from its spec and claims.json"
	@echo "  make gate              - Run every check CI runs, in CI's order"
	@echo "  make clean             - Clean temporary cache files"
	@echo "  make book              - Build both monograph PDFs into dist/ (needs Pandoc and LuaLaTeX)"
	@echo "  make book-check        - Run the PASS/FAIL/N-A gate against the built PDFs"
	@echo "  make book-clean        - Remove built PDFs and page previews"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

format-check:
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy .

verify:
	$(PYTHON) scripts/verify_integrity.py

# The evidence checks are deliberately not part of `verify`: docs/verification is a data
# set with its own schema, and a failure there means a citation is wrong rather than that
# a script broke. `gate` runs both.
verify-evidence:
	$(PYTHON) scripts/verification/audit_claims.py

check-render:
	$(PYTHON) scripts/verification/render_claims.py --check

# The registry is a rendering in the same sense the evidence markdown is: half of it is curated and
# half is derived from claims.json, so the derived half cannot be allowed to drift by hand.
# Issue #20. `render-registry` rewrites, this checks.
check-registry:
	$(PYTHON) scripts/verification/build_source_index.py --check

render-registry:
	$(PYTHON) scripts/verification/build_source_index.py --write

render-evidence:
	$(PYTHON) scripts/verification/render_claims.py --write

gate: lint format-check typecheck test verify verify-evidence check-render check-registry

# The book targets are deliberately NOT part of gate, so CI does not run them: the# checks job installs Python only, and a TeX distribution costs hundreds of megabytes# for a job that does not otherwise need one. A green gate therefore does not mean a# buildable book. Run make book-check where Pandoc and LuaLaTeX exist. Issue #29.
book:
	bash scripts/build_book.sh

book-check:
	bash scripts/verify_book_pdf.sh

book-clean:
	rm -rf dist/voice-edge-fpga-book-*.pdf dist/preview dist/.verify

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist
