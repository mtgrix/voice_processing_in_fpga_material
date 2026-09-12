PYTHON ?= python

.PHONY: help test lint format format-check typecheck verify verify-evidence check-render render-evidence gate clean

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
	@echo "  make gate              - Run every check CI runs, in CI's order"
	@echo "  make clean             - Clean temporary cache files"

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

render-evidence:
	$(PYTHON) scripts/verification/render_claims.py --write

gate: lint format-check typecheck test verify verify-evidence check-render

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist
