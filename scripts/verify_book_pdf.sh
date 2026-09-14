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
#   6  figure sources, PDF captions and prose references agree in count
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

# --chapter NN checks a single-chapter PDF built by scripts/build_book.sh --chapter NN.
# The constant EXPECTED_TITLES below demands all fourteen front-matter, chapter and
# appendix titles, which a one-chapter document cannot satisfy: that is why Issue #32
# had to add
# this mode instead of using the existing one. In chapter mode the expected headings are
# read out of the single source file being built.
CHAPTER=""
while [ $# -gt 0 ]; do
  case "$1" in
    --chapter|-c)
      [ $# -ge 2 ] || { echo "verify_book_pdf: $1 needs a value" >&2; exit 2; }
      CHAPTER="$2"; shift 2 ;;
    --chapter=*) CHAPTER="${1#--chapter=}"; shift ;;
    *) echo "verify_book_pdf: unknown argument: $1" >&2; exit 2 ;;
  esac
done
if [ -n "$CHAPTER" ]; then
  case "$CHAPTER" in
    ''|*[!0-9]*) echo "verify_book_pdf: --chapter wants a number, got: $CHAPTER" >&2; exit 2 ;;
  esac
  CHAPTER="$(printf '%02d' "$((10#$CHAPTER))")"
fi
DIST="$ROOT/dist"
BOOK_DIR="${BOOK_DIR:-$ROOT/book-en}"
SHARED_DIR="$ROOT/book"

# The book class prints the chapter number, so H1 text carries the title alone
# (see book/metadata.yaml). These are matched as space-free substrings of the
# extracted text: PDF extraction shifts and can drop spaces at some glyph
# boundaries, so a full fixed string is a fragile test.
#
# For a whole-book build the list is the contract: it is what a reader opening the
# volume expects to find, and it does not depend on the manuscript agreeing with
# itself. For --chapter it cannot be used, so headings come out of the one file being
# built, which makes the check "did what I wrote reach the page" and nothing stronger.
# That is a weaker check, and recording that is the reason it may replace the strong one
# in a review build but not in the release build.
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
  "Model Fundamentals: The Forward Pass in Hardware Terms"
  "Open Questions and Open Numbers"
)

MANU="$(basename "$BOOK_DIR")"
OUT_NAME="$(sed -n 's/^[[:space:]]*output_name:[[:space:]]*//p' "$SHARED_DIR/book-manifest.yaml" | head -1)"
[ -n "$OUT_NAME" ] || { echo "verify_book_pdf: manifest has no output_name" >&2; exit 1; }
if [ "$MANU" = "book-en" ]; then OUT_PREFIX="$OUT_NAME"; else OUT_PREFIX="$OUT_NAME-$MANU"; fi

if [ -n "$CHAPTER" ]; then
  CHAPTER_SRC="$BOOK_DIR/chapter$CHAPTER.md"
  [ -f "$CHAPTER_SRC" ] || { echo "verify_book_pdf: no such chapter source: $CHAPTER_SRC" >&2; exit 1; }
  OUT_PREFIX="$OUT_PREFIX-chapter$CHAPTER"
  # H1 and H2 lines, minus the authoring attribute braces that Pandoc consumes and
  # minus inline emphasis, which is what the printed heading actually contains.
  EXPECTED_TITLES=()
  HEADINGS="$(sed -nE 's/^#{1,2} +//p' "$CHAPTER_SRC" | sed -E 's/ *\{[^}]*\}$//; s/[*`]+//g' | sed -E 's/ +$//')"
  while IFS= read -r heading; do
    [ -n "$heading" ] && EXPECTED_TITLES+=("$heading")
  done <<< "$HEADINGS"
  [ "${#EXPECTED_TITLES[@]}" -gt 0 ] || { echo "verify_book_pdf: chapter $CHAPTER has no headings to look for" >&2; exit 1; }
  echo "verify_book_pdf: chapter mode, ${#EXPECTED_TITLES[@]} headings read from $(basename "$CHAPTER_SRC")"
fi
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

# --- 6. figures: counted in, captioned out, referenced from prose ---------
# Both halves of this check were written when the manuscript held no figures, so the
# branch that used to be reachable said only "nothing leaked". That is not the same
# claim as "everything rendered": Pandoc can lose a float between the div and the page
# and leave the text layer clean, because a dropped figure has no fence left to leak.
# So the count of figure sources is compared against the count of numbered captions in
# the PDF. Acceptance 5 of Issue #36 is the other half: the prose has to point at a
# figure rather than repeat its numbers, so every figure id has to appear in a link
# somewhere in the manuscript, which is what the id loop below checks.
#
# A caption is found by its leading "Figure <n>:" because that colon is printed by the
# float and by nothing else in the book -- a reference in prose is followed by a word.
#
# Two quantities are being compared here, and they have to describe the same document.
# The PDF under test is either the whole manuscript or one chapter, decided by
# --chapter; the source count used to be decided by nothing, and always read every
# chapter file. A figureless chapter therefore failed for the book's own figures, and a
# chapter whose count happened to equal the manuscript total passed having checked
# nothing. Both readings were wrong, and only one of them announced itself. Issue #54.
FENCE_A='```mermaid'
FENCE_B='```tikz'
if grep -aqE "${FENCE_A}|${FENCE_B}|begin.tikzpicture" "$WORK/book.txt"; then
  fail "unrendered figure source leaked into the PDF"
else
  if [ -n "$CHAPTER" ]; then
    FENCE_FILES=("$CHAPTER_SRC")
    SCOPE="chapter $CHAPTER"
  else
    FENCE_FILES=("$BOOK_DIR"/*.md)
    SCOPE="the whole $MANU manuscript"
  fi
  NFENCE=$(cat "${FENCE_FILES[@]}" 2>/dev/null | grep -acE '^[[:space:]]*```(tikz|mermaid)')
  # Unreferenced divs are a property of the manuscript, not of the PDF, so this loop stays
  # global in both modes: a prose reference may legitimately sit in a different chapter from
  # the div it points at, and narrowing the loop would report a book that points at nothing.
  UNREF=""
  for id in $(grep -haoE '^::: \{#fig-[A-Za-z0-9_-]+ \.figure\}' "$BOOK_DIR"/*.md | sed 's/.*#//; s/ .*//'); do
    grep -aqF "(#${id})" "$BOOK_DIR"/*.md || UNREF="$UNREF $id"
  done
  if [ -n "$UNREF" ]; then
    fail "figure div(s) that no prose points at:$UNREF"
  elif [ "${NFENCE:-0}" -eq 0 ]; then
    na "figure checks: $SCOPE contains no figure sources"
  else
    CAPS=$(grep -aoE '^Figure [0-9]+:' "$WORK/book.txt" | grep -oE '[0-9]+' | sort -n -u | tr '\n' ' ')
    NCAP=$(echo "$CAPS" | wc -w | tr -d '[:space:]')
    # The expected sequence is 1..N only for a whole-book build. LaTeX numbers floats from 1
    # inside the document it is given, so a chapter-only PDF renumbers its own figures: the
    # prose cites [Figure 8](#fig-kv-ring-buffer) while that document prints "Figure 3:".
    # Asserting a sequence there would compare the chapter's local floats against a claim
    # about the book's ordering, and the book's ordering is not in that file.
    SEQ_CLAIM=1
    [ -n "$CHAPTER" ] && SEQ_CLAIM=0
    WANT=""
    [ "$SEQ_CLAIM" -eq 1 ] && WANT="$(seq -s ' ' 1 "$NFENCE") "
    # WANT stays empty when the sequence claim is off, so the guard below has to test SEQ_CLAIM
    # before comparing: an empty expectation is not the same claim as "no captions", and on the
    # first run of this fix that is exactly how chapter mode came back failing its own figures.
    BAD=""
    if [ "$NCAP" -ne "$NFENCE" ]; then
      BAD="$NFENCE figure source(s) in $SCOPE, $NCAP caption(s) in the PDF"
    elif [ "$SEQ_CLAIM" -eq 1 ] && [ "$CAPS" != "$WANT" ]; then
      BAD="expected caption numbers: $WANT  found in the PDF: ${CAPS}none"
    fi
    if [ -n "$BAD" ]; then
      fail "figure checks: $BAD"
    else
      pass "figure checks: $NFENCE source(s) in $SCOPE rendered as $NCAP caption(s), each referenced from prose"
      if [ "$SEQ_CLAIM" -eq 0 ]; then
        echo "        note: caption numbers above are local to this chapter document; the prose"
        echo "        cites book-wide positions, so the two differ by design. Run the whole-book"
        echo "        build to check the sequence, which is the only claim about figure order."
      fi
    fi
  fi
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
  # Acceptance 1 of Issue #36 is that a figure be visible, which no text-layer check can
  # establish on its own. The pages carrying captions therefore join the quartile
  # samples, rather than leaving it to luck whether the quartiles happened to hit them:
  # Measured on the current 48-page build: the quartile samples are pages 12, 24, 36 and 48,
  # while the nine floats sit on pages 19, 20, 26, 27, 30, 37, 39, 40 and 44. The two sets do
  # not intersect at all, so sampling alone would have rendered none of the figures.
  FIGPAGES=$(awk '/^=== PAGE /{pg=$3} /^Figure [0-9]+:/{print pg}' "$WORK/book.txt" | sort -nu)
  REPR="$REPR $FIGPAGES"
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
#
# Two limits on what a clean log here licenses, both from Issue #54. It is now truncated at the
# start of each build and named after the mode that wrote it, so it describes this document rather
# than the concatenation of every build -- but it only describes this document's *failures*. Pandoc
# forwards the engine's output only when the engine exits non-zero, so a successful build can raise
# a warning here and leave nothing: absence of "Missing character" is not evidence that no glyph was
# dropped. Check 7 of this script is the text-layer half of the same question, and the figure
# legibility eyeball in check 9 is the rest.
BUILD_LOG="$DIST/build.log"
[ -n "$CHAPTER" ] && BUILD_LOG="$DIST/build-chapter$CHAPTER.log"
if [ ! -f "$BUILD_LOG" ]; then
  na "missing-glyph warnings: no $(basename "$BUILD_LOG") in dist/ (build with scripts/build_book.sh)"
else
  NG=$(grep -ac 'Missing character' "$BUILD_LOG" 2>/dev/null)
  NG="${NG:-0}"
  if [ "$NG" -eq 0 ]; then
    pass "no missing-glyph warnings in $(basename "$BUILD_LOG") (both passes of this build)"
  else
    fail "$NG missing-glyph warning(s) in $(basename "$BUILD_LOG"): the PDF drops those characters"
    grep -ao "There is no .\{0,32\}in font" "$BUILD_LOG" 2>/dev/null | sort -u | sed "s/^/        /" | head -5
  fi
fi

# --- 11. authoring syntax that reached print --------------------------------
# Pandoc reads "{.unnumbered}" as a class and "{unnumbered}" as the literal
# word: the first build of this book printed "Preface {unnumbered}" in its own
# table of contents because of the missing dot, and checks 2 above could not see
# it, since a substring match tolerates any suffix. Any brace of this shape in
# the extracted text is markup the writer was supposed to consume.
# The HTML comment markers joined the pattern for the chapter build: every stub in this
# manuscript sits under a drafting note in that form, Pandoc drops such comments on the
# way to LaTeX, and a marker that reaches the page therefore means the notes are being
# printed as prose.
LEAK=$(grep -aoE '\{(unnumbered|[.][a-z-]+|[#][A-Za-z0-9_.-]+)\}|<!--|-->' "$WORK/book.txt" | sort -u | tr '\n' ' ')
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
