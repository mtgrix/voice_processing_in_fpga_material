#!/usr/bin/env python3
"""figure_numbers.py -- keep every prose "Figure N" equal to the number the float actually gets.

Why this exists. scripts/verify_book_pdf.sh check 6 compares two counts: N figure sources must
render as captions 1..N, and every div id must be pointed at by a link somewhere. It never
compares the *number a reader reads in a sentence* against the number the anchor in that same
sentence prints on the page. That gap is not theoretical. The number a float gets is a function
of the order files appear in `book/book-manifest.yaml` and of how many figures each file holds,
so adding one figure to the preface renumbers all eleven floats that follow it and makes every
prose citation of them wrong. A wrong number is the one figure defect a reader cannot catch and
a link cannot hide: a citation that points at the right anchor with the wrong number still
lands on the right figure, so only the text lies.

So the canonical order is computed here and never maintained by hand: sources in manifest order,
and within a file, figure divs in file order. `--fix` rewrites the linked numbers to that order,
which is what makes adding a diagram cheap: add the div, run the fix, and the book's citations
agree again.

An unanchored mention -- "as Figure 5 shows" with no link -- is reported as a finding rather than
guessed at, because nothing in the manuscript says which figure the author meant, and a stale number
in that sentence is invisible to every gate in the repository. Either link it or name the figure
without a number.

usage:
  python scripts/verification/figure_numbers.py             # check; exit 1 on any finding
  python scripts/verification/figure_numbers.py --fix       # rewrite linked numbers in place
  python scripts/verification/figure_numbers.py --list      # print the slug -> number table
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "book", "book-manifest.yaml")
BOOK_DIR = os.path.join(ROOT, "book-en")

#: `::: {#fig-slug .figure}` -- the authoring form scripts/filters/tikz_figures.lua expects.
DIV = re.compile(r"^:::\s*\{#(fig-[A-Za-z0-9_-]+)\s+\.figure\}\s*$", re.M)
#: `[Figure 12](#fig-kv-ring-buffer)` -- a citation this script can verify and rewrite.
LINKED = re.compile(r"\[Figure (\d+)\]\(#(fig-[A-Za-z0-9_-]+)\)")
#: "Figure 12" that is not part of a link. Deliberately case-insensitive: a sentence mid-paragraph
#: reads "as figure 4 shows" just as easily, and a stale number is equally wrong either way.
BARE = re.compile(r"(?<!\[)[Ff]igure (\d+)(?!\]\()")


def sources() -> list[str]:
    """Return the manuscript's reading order, which is also its float numbering."""
    if not os.path.isfile(MANIFEST):
        sys.exit(f"figure_numbers: no manifest at {MANIFEST}")
    out: list[str] = []
    inside = False
    for line in open(MANIFEST, encoding="utf-8"):
        if re.match(r"^sources:\s*$", line):
            inside = True
            continue
        if inside:
            m = re.match(r"^\s*-\s*(\S+\.md)\s*$", line)
            if m:
                out.append(m.group(1))
            elif line.strip() and not line.lstrip().startswith("#"):
                break  # the list ended; the next key is not a source
    if not out:
        sys.exit("figure_numbers: the manifest's sources: list came back empty")
    missing = [s for s in out if not os.path.isfile(os.path.join(BOOK_DIR, s))]
    if missing:
        # A source the build cannot find means the numbering computed here is not the numbering the
        # PDF will get, so continuing would produce a table of confident wrong numbers.
        sys.exit(f"figure_numbers: manifest lists sources absent from book-en/: {missing}")
    return out


def canonical(order: list[str]) -> dict[str, int]:
    """slug -> the number its float gets, counting divs in reading order from 1."""
    table: dict[str, int] = {}
    for src in order:
        text = open(os.path.join(BOOK_DIR, src), encoding="utf-8").read()
        for slug in DIV.findall(text):
            if slug in table:
                sys.exit(f"figure_numbers: duplicate figure id #{slug}")
            table[slug] = len(table) + 1
    return table


def findings(order: list[str], table: dict[str, int]) -> list[str]:
    """Every citation that disagrees with the computed number, and every unverifiable mention."""
    out: list[str] = []
    for fn in sorted(os.listdir(BOOK_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(BOOK_DIR, fn)
        in_manifest = fn in order
        for lineno, line in enumerate(open(path, encoding="utf-8"), start=1):
            for num, slug in LINKED.findall(line):
                if not in_manifest:
                    out.append(
                        f"{fn}:{lineno}: link to #{slug} from a file the build does not read"
                    )
                    continue
                want = table.get(slug)
                if want is None:
                    out.append(f"{fn}:{lineno}: [Figure {num}](#{slug}) points at no figure div")
                elif int(num) != want:
                    out.append(f"{fn}:{lineno}: #{slug} is Figure {want}, but the prose says {num}")
            for num in BARE.findall(line):
                out.append(
                    f"{fn}:{lineno}: 'Figure {num}' has no anchor, so its number cannot be checked"
                )
    return out


def fix(order: list[str], table: dict[str, int]) -> int:
    """Rewrite linked numbers to the computed order. Returns how many citations changed."""
    changed = 0
    for src in order:
        path = os.path.join(BOOK_DIR, src)
        text = open(path, encoding="utf-8").read()

        def sub(m: re.Match[str]) -> str:
            nonlocal changed
            want = table[m.group(2)]
            if int(m.group(1)) == want:
                return m.group(0)
            changed += 1
            return f"[Figure {want}](#{m.group(2)})"

        new = LINKED.sub(sub, text)
        if new != text:
            open(path, "w", encoding="utf-8", newline="\n").write(new)
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fix", action="store_true", help="rewrite prose figure numbers to the build order"
    )
    ap.add_argument("--list", action="store_true", help="print slug -> figure number and exit")
    args = ap.parse_args()

    order = sources()
    table = canonical(order)

    if args.list:
        for slug, n in sorted(table.items(), key=lambda kv: kv[1]):
            print(f"Figure {n:<3} #{slug}")
        print(f"-- {len(table)} figure(s), numbered in book/book-manifest.yaml order")
        return 0

    if args.fix:
        n = fix(order, table)
        print(f"figure_numbers: rewrote {n} citation(s) to the build order")

    bad = findings(order, table)
    for line in bad:
        print(f"figure_numbers: {line}")
    if bad:
        bare = sum(1 for b in bad if "no anchor" in b)
        print(
            f"-- {len(bad)} finding(s): {len(bad) - bare} wrong or dangling number(s), "
            f"{bare} unanchored mention(s)"
        )
        return 1
    print(
        f"figure_numbers: PASS -- {len(table)} figure(s), every anchored citation matches its float"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
