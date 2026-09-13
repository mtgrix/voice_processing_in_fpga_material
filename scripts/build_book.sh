#!/usr/bin/env bash
# build_book.sh — assemble the Voice Edge AI monograph PDFs with Pandoc.
#
# Pipeline: manuscript Markdown -> Pandoc + citeproc -> LuaLaTeX -> PDF.
#
# Outputs, into dist/ (gitignored):
#   <name>-print.pdf   A4, twoside, black borderless links, no syntax colour
#   <name>-screen.pdf  same layout, clickable coloured links
#
# Usage:
#   bash scripts/build_book.sh
#   BOOK_DIR=book bash scripts/build_book.sh     build the legacy Vietnamese manuscript
#
# Why BOOK_DIR and not a LANG switch: AGENTS.md makes English B2 canonical, so the
# default manuscript is book-en/. The old book/ tree is Vietnamese and will be
# rewritten, not translated on demand, so what changes here is the directory.
#
# No Mermaid or TikZ pre-render step: the manuscript contains no figures, so there
# is nothing for those stages to do. See Issue #29 before adding them back.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD="$ROOT/build"
DIST="$ROOT/dist"
BOOK_DIR="${BOOK_DIR:-$ROOT/book-en}"
SHARED_DIR="$ROOT/book"          # metadata.yaml, header.tex, references.bib, ieee.csl
MANIFEST="$SHARED_DIR/book-manifest.yaml"
# Pandoc writes the TeX and LuaLaTeX writes the PDF, and both talk on stderr. A
# glyph the chosen fonts do not contain is reported only there, and the PDF still
# comes out, so the log is kept for check 10 of scripts/verify_book_pdf.sh.
LOG_FILE="$DIST/build.log"


for tool in pandoc lualatex pdfinfo; do
  command -v "$tool" >/dev/null 2>&1 || { echo "build_book: missing required tool: $tool" >&2; exit 1; }
done
[ -d "$BOOK_DIR" ] || { echo "build_book: no such manuscript dir: $BOOK_DIR" >&2; exit 1; }
[ -f "$MANIFEST" ] || { echo "build_book: missing $MANIFEST" >&2; exit 1; }

mkdir -p "$DIST" "$BUILD"

OUT_NAME="$(sed -n 's/^[[:space:]]*output_name:[[:space:]]*//p' "$MANIFEST" | head -1)"
[ -n "$OUT_NAME" ] || { echo "build_book: manifest has no output_name" >&2; exit 1; }
# The legacy tree keeps its own suffix so a Vietnamese build never overwrites the
# canonical one by accident.
if [ "$(basename "$BOOK_DIR")" = "book-en" ]; then OUT_PREFIX="$OUT_NAME"; else OUT_PREFIX="$OUT_NAME-$(basename "$BOOK_DIR")"; fi

# Read the ordered source list. Missing files are fatal: a silently skipped
# chapter would produce a thinner PDF and still exit 0.
SOURCES=()
while IFS= read -r src; do
  [ -n "$src" ] || continue
  [ -f "$BOOK_DIR/$src" ] || { echo "build_book: manifest names a file that does not exist: $BOOK_DIR/$src" >&2; exit 1; }
  SOURCES+=("$src")
done < <(sed -n '/^sources:/,/^[^ ]/p' "$MANIFEST" | grep -oE '[A-Za-z0-9_.-]+[.]md$')
[ "${#SOURCES[@]}" -gt 0 ] || { echo "build_book: manifest listed no sources" >&2; exit 1; }
echo "build_book: manuscript dir  $BOOK_DIR"
echo "build_book: ${#SOURCES[@]} sources, in order: ${SOURCES[*]}"

# Generated figure PDFs, if any exist, must sit under the Pandoc working dir so
# relative image paths in the chapters resolve.
mkdir -p "$BUILD/figures/generated"
if compgen -G "$BOOK_DIR/figures/generated/*.pdf" >/dev/null; then
  echo "build_book: copying generated figures"
  cp "$BOOK_DIR"/figures/generated/*.pdf "$BUILD/figures/generated/"
fi

COMMON_ARGS=(
  --standalone
  --metadata-file "$SHARED_DIR/metadata.yaml"
  --include-in-header "$SHARED_DIR/header.tex"
  --pdf-engine=lualatex
  --citeproc
  --bibliography "$SHARED_DIR/references.bib"
  --csl "$SHARED_DIR/ieee.csl"
  --toc
  --resource-path "$BUILD:$BOOK_DIR"
  -V fontsize=11pt
  -V geometry:a4paper
  -V geometry:twoside
  -V geometry:inner=32mm
  -V geometry:outer=22mm
  -V geometry:top=25mm
  -V geometry:bottom=28mm
)

# Run from build/ so relative figure paths resolve against $BUILD.
echo "build_book: rendering print PDF"
: "$LOG_FILE"   # start each build with an empty log, then append both passes
( cd "$BUILD" && pandoc "${SOURCES[@]/#/$BOOK_DIR/}" \
    "${COMMON_ARGS[@]}" \
    --syntax-highlighting=none \
    -o "$DIST/$OUT_PREFIX-print.pdf" ) 2>> "$LOG_FILE"

echo "build_book: rendering screen PDF"
# -V colorlinks is passed only here. Any non-empty value makes the Pandoc template
# enable coloured links, which is wanted on screen and not wanted for print.
( cd "$BUILD" && pandoc "${SOURCES[@]/#/$BOOK_DIR/}" \
    "${COMMON_ARGS[@]}" \
    -V colorlinks \
    -o "$DIST/$OUT_PREFIX-screen.pdf" ) 2>> "$LOG_FILE"

echo "build_book: OK"
for pdf in "$DIST/$OUT_PREFIX-print.pdf" "$DIST/$OUT_PREFIX-screen.pdf"; do
  pdfinfo "$pdf" | sed -n 's/^Pages:/  pages:/p;s/^Page size:/  size:/p'
done
