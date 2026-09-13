#!/usr/bin/env python
"""Extract the full text of a PDF to a UTF-8 file, one page per block.

Used by scripts/verify_book_pdf.sh. PyMuPDF rather than pdftotext: the reference
project in learning_journey/knowledge_graph_learning-journey found that
``pdftotext`` can silently drop precomposed glyphs depending on the ToUnicode
map the font embedder produced, so a correct-looking PDF fails a text check.
PyMuPDF reads the same text layer and keeps the characters. The module is
imported as ``pymupdf``, its canonical name since release 1.24; the old ``fitz``
alias now prints a deprecation warning on stderr, which would land in the build
log the glyph check reads.

Usage: python scripts/extract_pdf_text.py <in.pdf> <out.txt>
"""

from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, dst = argv[1], argv[2]
    try:
        import pymupdf
    except ImportError:
        print(
            "extract_pdf_text: PyMuPDF is not installed (pip install pymupdf, or the book extra)",
            file=sys.stderr,
        )
        return 1
    try:
        doc = pymupdf.open(src)
    except Exception as exc:  # noqa: BLE001 - report, do not traceback in a gate
        print(f"extract_pdf_text: cannot open {src}: {exc}", file=sys.stderr)
        return 1
    with open(dst, "w", encoding="utf-8", newline="\n") as out:
        for page_no in range(doc.page_count):
            page = doc.load_page(page_no)
            out.write(f"\n=== PAGE {page_no + 1} ===\n")
            out.write(page.get_text())
    print(f"extract_pdf_text: {doc.page_count} pages -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
