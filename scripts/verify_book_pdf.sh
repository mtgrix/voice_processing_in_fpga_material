#!/usr/bin/env bash
# verify_book_pdf.sh — verification gate for the built monograph PDFs.
#
# Three outcomes, not two:
#   PASS  the check ran and held
#   FAIL  the check ran and did not hold
#   N/A   the thing this check looks at does not exist in the manuscript yet
#
# N/A exists because a gate with only PASS and FAIL reports success for checks it
# never ran. That is the defect class Issue #25 just closed in the evidence
# auditor: a check declared in prose that the code could not reach. The summary
# line prints how many checks were applicable, so a thin manuscript cannot read as
# a finished book. Exit status is unaffected by N/A: an absence of evidence is not
# a pass, and the count says so out loud.
#
# Checks:
#   1  both PDFs exist and pdfinfo succeeds; page count reported
#   2  every expected chapter and front/back-matter title appears in extracted text
#   3  a table of contents is present
#   4  bibliography section and numeric entries (N/A while nothing is cited)
#   5  no unresolved Pandoc citation markers like [@key]
#   6  no leftover figure fences (N/A while there are no figures)
#   7  no U+FFFD replacement characters, which would mean a missing glyph
#   8  no agent-wrapper artifacts leaked into the text
#   9  representative pages render to PNG for eyeballing
#  10  no missing-glyph warnings in the build log (the PDF hides these)
#  11  no Pandoc authoring syntax leaked into the printed text
#  12  no duplicated table-of-contents lines
#
# Exit 0 only when no check failed. Usage: bash scripts/verify_book_pdf.sh
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
BOOK_DIR="${BOOK_DIR:-$ROOT/book-en}"
SHARED_DIR="$ROOT/book"

# The book class prints the chapter number, so H1 text carries the title alone
# (see book/metadata.yaml). These are matched as space-free substrings of the
# extracted text: PDF extraction shifts and can drop spaces at some glyph
# boundaries, so a full fixed string is a fragile test.
EXPECTED_TITLES=(
  "Preface"
  "How to Use This Book"
  "Voice Processing Pipelines"
  "The Jetson Orin Baseline"
  "The Streaming Bottleneck"
  "FPGA Microarchitecture for Edge AI"
  "Four Ways to Accelerate on an FPGA"
  "Audio Preprocessing in Hardware"
  "Quantization That Respects the Hardware"
  "Keyword Spotting on the Board"
  "A Streaming Conformer Overlay"
  "Benchmarking, the Pareto Frontier"
  "Open Questions and Open Numbers"
)

MANU="$(basename "$BOOK_DIR")"
OUT_NAME="$(sed -n 's/^[[:space:]]*output_name:[[:space:]]*//p' "$SHARED_DIR/book-manifest.yaml" | head -1)"
[ -n "$OUT_NAME" ] || { echo "verify_book_pdf: manifest has no output_name" >&2; exit 1; }
if [ "$MANU" = "book-en" ]; then OUT_PREFIX="$OUT_NAME"; else OUT_PREFIX="$OUT_NAME-$MANU"; fi

PRINT="$DIST/$OUT_PREFIX-print.pdf"
SCREEN="$DIST/$OUT_PREFIX-screen.pdf"
WORK="$DIST/.verify"
PREVIEW="$DIST/preview"
mkdir -p "$WORK" "$PREVIEW"

FAIL=0; PASSN=0; FAILN=0; SKIPN=0
pass() { echo "  PASS: $1"; PASSN=$((PASSN+1)); }
fail() { echo "  FAIL: $1"; FAILN=$((FAILN+1)); FAIL=1; }
na()   { echo "  N/A : $1"; SKIPN=$((SKIPN+1)); }
# Octal escape rather than a Unicode literal, so the byte sequence does not
# depend on the locale grep is running under.
REPL=$(printf '\357\277\275')

echo "verify_book_pdf: gate start (manuscript $MANU)"

# --- 1. existence ---------------------------------------------------------
PAGES=0
for pdf in "$PRINT" "$SCREEN"; do
  base="$(basename "$pdf")"
  if [ ! -f "$pdf" ]; then fail "missing PDF: $pdf (run scripts/build_book.sh first)"; continue; fi
  if pdfinfo "$pdf" > "$WORK/pdfinfo.$base.txt" 2>/dev/null; then
    p="$(sed -n 's/^Pages:[[:space:]]*//p' "$WORK/pdfinfo.$base.txt" | tr -d '[:space:]')"
    pass "$base: pdfinfo OK, $p pages"
    [ "$base" = "$OUT_PREFIX-print.pdf" ] && PAGES="$p"
  else
    fail "$base: pdfinfo failed"
  fi
done
if [ "$FAIL" -eq 1 ]; then echo "verify_book_pdf: GATE FAILED"; exit 1; fi

# --- extract text ---------------------------------------------------------
# PyMuPDF through scripts/extract_pdf_text.py, not pdftotext: the reference
# project found pdftotext can drop glyphs depending on the embedded font's
# ToUnicode map, which would make this gate lie in both directions.
if ! python "$ROOT/scripts/extract_pdf_text.py" "$PRINT" "$WORK/book.txt"; then
  fail "PDF text extraction failed"
  echo "verify_book_pdf: GATE FAILED"; exit 1
fi
tr -d '[:space:]' < "$WORK/book.txt" > "$WORK/book.norm.txt"

# --- 2. titles ------------------------------------------------------------
for title in "${EXPECTED_TITLES[@]}"; do
  probe="${title//[[:space:]]/}"
  if grep -aqF "$probe" "$WORK/book.norm.txt"; then pass "title present: $title"
  else fail "title missing from the PDF: $title"; fi
done

# --- 3. table of contents -------------------------------------------------
# Case-insensitive: the book class prints "Contents", some classes print
# uppercase, and the heading is the thing under test, not its capitalisation.
if grep -aqiF "contents" "$WORK/book.norm.txt"; then pass "table of contents present"
else fail "no table of contents heading found"; fi

# --- 4 and 5. citations and bibliography ----------------------------------
CITED_IN_SOURCE="$(grep -rhoE '\[@[A-Za-z0-9_-]+\]' "$BOOK_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
BIB_KEYS="$(grep -cE '^@' "$SHARED_DIR/references.bib" 2>/dev/null || echo 0)"
if [ "${CITED_IN_SOURCE:-0}" -eq 0 ]; then
  na "bibliography section: nothing is cited (0 [@key] markers in the manuscript, $BIB_KEYS entries in references.bib)"
  na "numeric bibliography entries: nothing is cited"
else
  if grep -aqF "References" "$WORK/book.txt"; then pass "bibliography section present"
  else fail "bibliography section References missing while the manuscript cites $CITED_IN_SOURCE times"; fi
  if grep -aqE '^\[[0-9]+\]' "$WORK/book.txt"; then pass "numeric bibliography entries rendered"
  else fail "no numeric entries rendered though the manuscript cites"; fi
fi
if grep -anE '\[@[A-Za-z0-9_-]+\]' "$WORK/book.txt"; then fail "unresolved [@key] citation markers in the PDF"
else pass "no unresolved [@key] markers in the PDF"; fi

# --- 6. figure leftovers --------------------------------------------------
FENCE_A='```mermaid'
FENCE_B='```tikz'
if grep -aqE "${FENCE_A}|${FENCE_B}|begin.tikzpicture" "$WORK/book.txt"; then
  fail "unrendered figure source leaked into the PDF"
elif grep -aqE "${FENCE_A}|${FENCE_B}" "$BOOK_DIR"/*.md 2>/dev/null; then
  pass "figure sources exist in the manuscript and none leaked as fences"
else
  na "figure checks: the manuscript contains no figures"
fi

# --- 7. glyphs ------------------------------------------------------------
if grep -aqF "$REPL" "$WORK/book.txt"; then fail "U+FFFD found: a glyph is missing from the fonts"
else pass "no U+FFFD replacement characters"; fi

# --- 8. wrapper artifacts -------------------------------------------------
if grep -anE '</(content|parameter|tool_use|invoke|function_calls)' "$WORK/book.txt"; then
  fail "agent wrapper artifacts leaked into the PDF"
else pass "no wrapper artifacts"; fi

# --- 9. page renders ------------------------------------------------------
if ! command -v pdftoppm >/dev/null 2>&1; then
  na "page renders: pdftoppm is not installed"
elif [ "$PAGES" -eq 0 ]; then
  na "page renders: no page count to sample"
else
  REPR=""
  for frac in 25 50 75 100; do
    p=$(( (PAGES * frac + 99) / 100 )); [ "$p" -lt 1 ] && p=1
    REPR="$REPR $p"
  done
  REPR="$(echo "$REPR" | tr ' ' '\n' | sort -nu)"
  for p in $REPR; do
    rm -f "$WORK"/pp-*.png
    if pdftoppm -png -r 100 -f "$p" -l "$p" "$PRINT" "$WORK/pp" 2>/dev/null \
       && [ -n "$(ls "$WORK"/pp-*.png 2>/dev/null | head -1)" ]; then
      cp "$WORK"/pp-*.png "$PREVIEW/page-$p.png" 2>/dev/null
      pass "page $p rendered -> dist/preview/page-$p.png"
    else
      fail "page $p produced no image"
    fi
  done
fi

# --- 10. glyphs the fonts do not contain --------------------------------
# This one exists because of a hole found while building: a missing glyph is
# a WARNING from LuaLaTeX, the character is dropped, and the text layer keeps
# no trace of it, so check 7 stays green over a page with a hole in it. The
# build log is the only place the fact survives. N/A when there is no log,
# which is what a hand-run pandoc leaves behind.
BUILD_LOG="$DIST/build.log"
if [ ! -f "$BUILD_LOG" ]; then
  na "missing-glyph warnings: no dist/build.log (build with scripts/build_book.sh)"
else
  NG=$(grep -ac 'Missing character' "$BUILD_LOG" 2>/dev/null)
  NG="${NG:-0}"
  if [ "$NG" -eq 0 ]; then
    pass "no missing-glyph warnings in the build log (both passes)"
  else
    fail "$NG missing-glyph warning(s) in dist/build.log: the PDF drops those characters"
    grep -ao "There is no .\{0,32\}in font" "$BUILD_LOG" 2>/dev/null | sort -u | sed "s/^/        /" | head -5
  fi
fi

# --- 11. authoring syntax that reached print --------------------------------
# Pandoc reads "{.unnumbered}" as a class and "{unnumbered}" as the literal
# word: the first build of this book printed "Preface {unnumbered}" in its own
# table of contents because of the missing dot, and checks 2 above could not see
# it, since a substring match tolerates any suffix. Any brace of this shape in
# the extracted text is markup the writer was supposed to consume.
LEAK=$(grep -aoE '\{(unnumbered|[.][a-z-]+|[#][A-Za-z0-9_.-]+)\}' "$WORK/book.txt" | sort -u | tr '\n' ' ')
if [ -n "$LEAK" ]; then fail "authoring attribute syntax leaked into the PDF: $LEAK"
else pass "no authoring attribute syntax leaked into the PDF"; fi

# --- 12. duplicated contents lines ------------------------------------------
# A front-matter title appeared twice in the contents because Pandoc adds the
# contents line for an unnumbered heading itself while book/header.tex added a
# second. The signature is the same title, a page number, the same title, a page
# number, four adjacent extracted lines. A chapter heading is never followed by a
# bare number, so this cannot fire on the body; measured against the duplicated
# build it named exactly the three front-matter titles and nothing else.
DUP=$(awk '
  { line[NR] = $0 }
  END {
    for (i = 1; i + 3 <= NR; i++)
      if (line[i] == line[i+2] && line[i] ~ /[A-Za-z]/ \
          && line[i+1] ~ /^[0-9]+$/ && line[i+3] ~ /^[0-9]+$/)
        print line[i]
  }' "$WORK/book.txt" | sort -u | tr '\n' ';')
if [ -n "$DUP" ]; then fail "duplicated contents entries: $DUP"
else pass "no duplicated contents entries"; fi

APPLIED=$((PASSN+FAILN))
echo
echo "verify_book_pdf: $PASSN passed, $FAILN failed, $SKIPN not applicable"
echo "verify_book_pdf: $APPLIED of $((APPLIED+SKIPN)) checks could run against this manuscript"
if [ "$FAIL" -eq 0 ] && [ "$APPLIED" -lt 8 ]; then
  echo "verify_book_pdf: note: only $APPLIED checks were applicable. A passing gate over a thin manuscript is not a verified book."
fi
if [ "$FAIL" -eq 0 ]; then
  echo "verify_book_pdf: GATE PASSED (${PAGES} pages, previews in dist/preview/)"
  exit 0
else
  echo "verify_book_pdf: GATE FAILED"
  exit 1
fi
