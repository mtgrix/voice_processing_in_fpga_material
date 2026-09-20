PYTHON ?= python

.PHONY: help test lint format format-check typecheck verify verify-evidence check-render render-evidence check-registry render-registry check-bib render-bib check-numbers render-numbers check-prose render-prose check-figures render-figures check-figure-divs check-pairing gate book book-check book-figsize book-figcompile book-clean clean

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
	@echo "  make check-bib         - Fail if book/references.bib drifts from the registry"
	@echo "  make render-bib        - Regenerate the bibliography from the registry"
	@echo "  make check-numbers     - Fail on a number no cited claim supports (see number_baseline.json)"
	@echo "  make render-numbers    - Re-record the accepted numbers that lack a citation"
	@echo "  make check-prose       - Fail on a V-code, audit phrase, or spelled-out quantity in prose (see prose_baseline.json)"
	@echo "  make render-prose      - Re-record today's prose violations as reviewed debt"
	@echo "  make check-figures     - Fail if a prose Figure N disagrees with the number its float gets"
	@echo "  make render-figures    - Rewrite prose figure numbers to the build order"
	@echo "  make check-figure-divs - Fail on a malformed or unclosed TikZ figure div"
	@echo "  make check-pairing     - Fail on a number beside a record that does not carry it"
	@echo "  make gate              - Run every check CI runs, in CI's order"
	@echo "  make clean             - Clean temporary cache files"
	@echo "  make book              - Build both monograph PDFs into dist/ (needs Pandoc and LuaLaTeX)"
	@echo "  make book-check        - Run the PASS/FAIL/N-A gate against the built PDFs"
	@echo "  make book-figcompile   - Compile each TikZ figure alone; name the broken one"
	@echo "  make book-figsize      - Compile every TikZ figure alone; fail if one overflows the text block"
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

# The bibliography is derived from the registry, which is itself half derived from
# claims.json, so one citation path runs from an evidence quote to a printed reference
# line. Keys are registry ids. Issue #42.
check-bib:
	$(PYTHON) scripts/verification/build_bibliography.py --check

render-bib:
	$(PYTHON) scripts/verification/build_bibliography.py --write

# Every quantity the manuscript prints has to be reachable from a claim the same section cites.
# Today's gaps are recorded in docs/verification/number_baseline.json, so this fails on a NEW unsourced
# number instead of on the pile already in the book: the debt is named and counted, not excused. Use
# --strict when finishing a chapter, which ignores the baseline. Issue #59.
check-numbers:
	$(PYTHON) scripts/verification/scan_numbers.py --check

render-numbers:
	$(PYTHON) scripts/verification/scan_numbers.py --write-baseline

# BOOK_PEDAGOGY §8 bans V-codes, audit phrases, and spelled-out quantities from prose. The
# prose cage checks that ban; today's violations are recorded in
# docs/verification/prose_baseline.json, so the gate fails on a NEW infraction instead of on the
# pile already in the book. --strict ignores the baseline when finishing a chapter. Issue #99.
check-prose:
	$(PYTHON) scripts/verification/prose_cage.py --check

render-prose:
	$(PYTHON) scripts/verification/prose_cage.py --write-baseline

# A prose citation has to print the number its float actually gets. That number is a function of
# book-manifest.yaml order plus how many figure divs each file holds, so adding one diagram to the
# preface silently invalidates every citation after it -- the defect verify_book_pdf.sh cannot see,
# because a link with a wrong number still lands on the right figure. Pure text, so CI runs it.
# Issue #62.
check-figures:
	$(PYTHON) scripts/verification/figure_numbers.py

render-figures:
	$(PYTHON) scripts/verification/figure_numbers.py --fix

# The figure divs have to hold exactly one outer picture, a caption, and the house three-colon form
# that verify_book_pdf.sh check 6 greps for -- all claims the PDF verifier makes too, but only after
# a two-minute build that names the assembled TeX line, not the chapter. These are the milliseconds
# that make the minutes unnecessary. Pure text, so CI runs it. Issue #56.
check-figure-divs:
	$(PYTHON) scripts/verification/check_figures.py --check

# scan_numbers asks whether a number is anywhere in the section's records; that budget is the right
# answer for invention and the wrong one for mis-attribution -- 17 beside V-05-12 (value 16) passes
# if 17 sits in any other record the section cites. This grades each number against the record
# actually cited beside it, with the reviewed baseline as the sanctioned set. Pure text. Issue #56.
check-pairing:
	$(PYTHON) scripts/verification/check_pairing.py --check

gate: lint format-check typecheck test verify verify-evidence check-render check-registry check-bib check-numbers check-prose check-figures check-figure-divs check-pairing

# The book targets are deliberately NOT part of gate, so CI does not run them: the
# checks job installs Python only, and a TeX distribution costs hundreds of megabytes
# for a job that does not otherwise need one. A green gate therefore does not mean a
# buildable book. Run make book-check where Pandoc and LuaLaTeX exist. Issue #29.
book:
	bash scripts/build_book.sh

book-check:
	bash scripts/verify_book_pdf.sh

# The build never asks whether a TikZ float is wider than the text block, and an over-wide one
# prints no error: header.tex sets hfuzz=2pt, which only mutes small overfull warnings. This
# compiles each figure alone against the page the build really uses. Needs LuaLaTeX, so it is
# not in gate -- run it before `make book`, whose full pass costs minutes.
book-figsize:
	$(PYTHON) scripts/verification/figprobe.py --all

# Which figure is broken, in seconds, instead of an `l.1140` in a pandoc-assembled file: each
# fence compiles alone against the book's real preamble. It reports compile only -- fit is
# book-figsize above, and neither one says whether a picture depicts its caption. Issue #56.
book-figcompile:
	$(PYTHON) scripts/verification/compile_tikz.py --check

book-clean:
	rm -rf dist/voice-edge-fpga-book-*.pdf dist/preview dist/.verify

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist
