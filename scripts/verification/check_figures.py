#!/usr/bin/env python3
"""check_figures.py -- the source-half of the figure contract, before a build spends minutes on it.

Why this exists. scripts/verify_book_pdf.sh check 6 is the authority on figures, but it reads the
rendered text layer, so it can only speak after a full pandoc+lualatex pass. Every rule here is a
defect that pass would also find -- at the cost of two minutes and an `l.1140` pointing at a file
pandoc assembled. These checks cost milliseconds and name the chapter and line to edit.

What each rule protects:

  div shape      scripts/filters/tikz_figures.lua and check 6's grep both key on the exact house
                 form `::: {#fig-slug .figure}`. A four-colon variant is valid Pandoc and renders,
                 but it never enters the set of ids check 6 inspects, so the gate goes blind to
                 exactly the float most likely to be wrong.
  one picture    a div holding two tikzpictures, or none, desynchronises the fence counting the
                 filter and check 6 rely on.
  caption        a float without a caption sentence prints a number attached to nothing.
  pgfplots       not installed on this host; a figure leaning on it fails the build with an error
                 that points at the wrong file.
  duplicate id   Pandoc emits two \\label{fig-x}; the second silently wins and every citation to
                 the first lands on the wrong float.
  dangling ref   a link to an id no div defines -- the reference survives --fix, which only
                 rewrites numbers of links that resolve.

What this script does NOT license: it never compiles anything, so a picture that passes here can
still be broken TeX (that is scripts/verification/compile_tikz.py) or too wide for the page (that
is figprobe.py). And it deliberately does not check that a prose citation carries the right
*number* -- figure_numbers.py owns that claim, and a second checker for the same fact is how two
tools start disagreeing.

usage:
  python scripts/verification/check_figures.py            # check every manifest source
  python scripts/verification/check_figures.py --check    # same; the flag is the gate convention
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from figure_numbers import sources  # noqa: E402  (the manifest order, parsed once, shared)

ROOT = Path(__file__).resolve().parents[2]
BOOK_DIR = ROOT / "book-en"

#: The house form of a figure div opener.
DIV = re.compile(r"^:::\s*\{#(fig-[A-Za-z0-9_-]+)\s+\.figure\}\s*$")
#: Any div-shaped opener that is not the house form -- the hazard rule explained in the docstring.
BAD_DIV = re.compile(r"^\s*:{4,}\s*\{?#?fig-|^\s*::::")
#: A non-figure div, legal and ignored, e.g. the equation cards.
OTHER_DIV = re.compile(r"^\s*::: \{#")
REF = re.compile(r"\[Figure \d+\]\(#(fig-[A-Za-z0-9_-]+)\)")
BANNED = re.compile(r"\\usepackage\{pgfplots\}|\\begin\{axis\}|\\addplot|pgfplots")


def check_file(name: str, ids_before: set[str], ids_here: set[str]) -> list[str]:
    """Every structural defect in one manuscript file. ids_before: defined in earlier files."""
    problems: list[str] = []
    lines = (BOOK_DIR / name).read_text(encoding="utf-8").splitlines()
    opens: list[tuple[int, str]] = []
    for i, line in enumerate(lines, 1):
        m = DIV.match(line)
        if m:
            opens.append((i, m.group(1)))
        elif BAD_DIV.match(line):
            problems.append(
                f"{name}:{i} div opener is not the three-colon house form that check 6 greps "
                f"for, so the figure would be invisible to the gate: {line!r}"
            )
    for i, fid in opens:
        if fid in ids_before or fid in ids_here:
            problems.append(f"{name}:{i} duplicate figure id #{fid}")
            continue
        ids_here.add(fid)
        body = lines[i:]
        try:
            close = next(j for j, ln in enumerate(body) if ln.strip() == ":::")
        except StopIteration:
            problems.append(f"{name}:{i} figure div #{fid} is never closed")
            continue
        chunk = body[:close]
        nfence = sum(1 for ln in chunk if ln.lstrip().startswith("```"))
        # Column 0 only: a nested \\begin{tikzpicture} inside a node's content is indented, and
        # the appendix's dense-vs-separable figure draws its grids that way on purpose. The rule
        # is one OUTER picture per div, which is what the filter and check 6 count.
        npic = sum(1 for ln in chunk if ln.startswith("\\begin{tikzpicture}"))
        if npic != 1:
            problems.append(f"{name}:{i} figure #{fid} holds {npic} outer pictures, must be 1")
        if nfence != 2:
            problems.append(
                f"{name}:{i} figure #{fid} holds {nfence} fence lines, must be open+close "
                "(a doubled fence turns the caption into a verbatim block and swallows the "
                "next figure -- see the repository memory on stray fences)"
            )
        after_fence: list[str] = []
        inside = False
        for ln in chunk:
            if ln.lstrip().startswith("```"):
                inside = not inside
                continue
            if not inside:
                after_fence.append(ln)
        caption = " ".join(after_fence).strip()
        if len(caption) < 20:
            problems.append(
                f"{name}:{i} figure #{fid} has no caption sentence after the fence "
                f"({caption[:40]!r})"
            )
        for ln in chunk:
            if BANNED.search(ln):
                problems.append(
                    f"{name}:{i} figure #{fid} uses pgfplots, which is not installed: "
                    f"{ln.strip()[:60]}"
                )
    defined = ids_before | ids_here
    for i, line in enumerate(lines, 1):
        for fid in REF.findall(line):
            if fid not in defined:
                problems.append(
                    f"{name}:{i} prose points at #{fid}, which no div in this file or an "
                    "earlier one defines"
                )
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="gate convention; checking is the only mode, this flag just says so",
    )
    ap.parse_args(argv)
    order: list[str] = sources()
    defined: set[str] = set()
    problems: list[str] = []
    for name in order:
        here: set[str] = set()
        problems += check_file(name, defined, here)
        defined |= here
    print(f"check_figures: {len(order)} sources, {len(defined)} figure divs")
    for p in problems:
        print("  FAIL " + p)
    if problems:
        return 1
    print("PASS: every figure div has the house shape, one picture, a caption, and resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
