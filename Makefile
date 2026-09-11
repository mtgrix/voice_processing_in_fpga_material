.PHONY: help test lint format typecheck verify clean

help:
	@echo "Available commands:"
	@echo "  make test       - Run pytest test suite"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with ruff"
	@echo "  make typecheck  - Run mypy static type checking"
	@echo "  make verify     - Run repo integrity and validation scripts"
	@echo "  make clean      - Clean temporary cache files"

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

typecheck:
	python -m mypy .

verify:
	python scripts/verify_integrity.py

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist
