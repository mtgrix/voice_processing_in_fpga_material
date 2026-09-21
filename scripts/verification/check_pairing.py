#!/usr/bin/env python3
"""check_pairing.py -- does each number on a line sit beside the record that actually carries it?

Why this exists and what scan_numbers.py does not catch. scripts/verification/scan_numbers.py asks
"is this number anywhere in the records this section cites", which is the right question for
invention and the wrong question for mis-attribution. A draft that prints 17 and cites `V-05-12`
(whose value is 16) passes that budget, because 17 is in the section's allowance from some other
record it also cites. Both defects were live in section 9.1 during assembly: it cited only the
parameter record for a model whose width, depth, heads and taps are all registered, and wrote that
the family keeps 31 taps while the record registers 9 for the variant. Every gate in the tree
passed that paragraph. scan_numbers is the cage; this is the reviewer.

Grades, because a single yes/no would either flood the report or hide the interesting cases:

  strong  the token appears in the cited record's own quantity, value or unit
  weak    it appears only in that record's conditions, locator, quote or notes -- fine for a figure
          a record states as context, still worth a look
  MISM    the token is in neither, beside a citation: the number is attributed to the wrong record
  orphan  the token has no citation in its paragraph and is not excused by the baseline
  FAIL    the line cites a record id that does not exist in the registry

The sanctioned set is docs/verification/number_baseline.json, not a dict in this file. A number
that legitimately derives from cited records (40 ms = 0.01 s x 4) is already recorded there by
scan_numbers --check and reviewed by a human, so this tool excuses exactly what the committed
baseline excuses and nothing more. That keeps the two honest to each other: a number waved through
here is a number a person already signed off on, and repaying the debt (adding the real citation)
clears it from both at once.

No small-number exemption. Sixteen, seventeen, twelve, four, eight and nine are exactly the numbers
this book must not mis-attribute, and a filter that skipped "trivial" integers under twenty would
hide the encoder-depth class of error while removing nothing important.

What this script does NOT license: inline math is dropped, because `$[0.5,1)$` is an interval and
`$2^k$` is a symbol, and BOOK_PEDAGOGY section 6 asks for worked expressions. An unregistered number
smuggled into math still reaches scan_numbers, which is the gate; this file grades attribution in
prose and figure node text only.

usage:
  python scripts/verification/check_pairing.py book-en/chapter08.md [more files]
  python scripts/verification/check_pairing.py --check   # every chapter and the appendix
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims_lib import NUMBER, load_claims, records  # noqa: E402
from figure_numbers import sources  # noqa: E402  (manifest reading order)
from scan_numbers import (
    CLAIM_ID,
    COMMENT,
    DERIVED,
    split_sections,
    strip_regions,
    tokens_in,
)  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CLAIMS = ROOT / "docs" / "verification" / "claims.json"
BASELINE = ROOT / "docs" / "verification" / "number_baseline.json"

STRONG_FIELDS = ("quantity", "value", "unit")
WEAK_FIELDS = ("conditions", "locator", "quote", "notes")
INLINE_MATH = re.compile(r"\$[^$]*\$")
#: A definition of a unit or a tile is not a claim about this project: "Block RAM
#: (BRAM -- 36-kilobit storage tiles)" is naming the object, and 36 is registered
#: elsewhere as V-01-23. Reported as a note rather than silenced, because the same
#: shape can hide a real number.
UNIT_DEFINITION = re.compile(
    r"\b\d+(?:\.\d+)?[- ]?(?:kilobit|megabit|kilobyte|KiB|MiB|kb|Mb)\b", re.I
)
#: Text drawn inside a tikz node, which a reader sees on the page and no prose scanner reads.
NODE_TEXT = re.compile(r"\\node\s*(?:\[[^\]]*\])?\s*(?:at\s*\([^)]*\))?\s*\{([^{}]*)\}")
#: A node whose whole text is a number is an axis tick, not a labelled claim. The roofline figure
#: prints 1000 and 10000 as powers of ten on a log axis; those are geometry, and scan_numbers never
#: sees them because it strips fences. A node with words in it ("1,248 DSP slices") is a claim and
#: stays in scope.
BARE_NUMBER = re.compile(r"^\s*[\d,.]+\s*$")


def field_forms(by: dict[str, dict[str, Any]]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """(strong, weak) number sets per record id, from the registry's own fields.

    Split out of main() so a test can build a fake registry and drive grade_file directly, the way
    tests/test_number_scan.py drives scan_file.
    """
    strong = {
        rid: forms(" ".join(str(r.get(k, "")) for k in STRONG_FIELDS)) for rid, r in by.items()
    }
    weak = {rid: forms(" ".join(str(r.get(k, "")) for k in WEAK_FIELDS)) for rid, r in by.items()}
    return strong, weak


def forms(text: str) -> set[str]:
    out: set[str] = set()
    for raw in NUMBER.findall(text):
        out.add(raw)
        out.add(raw.replace(",", ""))
    return out


def quantities(text: str) -> tuple[set[str], set[str]]:
    """(numbers to check, numbers seen only inside a unit definition)."""
    stripped = strip_regions(text, "prose")
    # The citation's own digits are not a measurement. Without this, `V-01-09` contributes 01 and
    # 09 as tokens to grade, and a table that cites twelve records reports twelve fake mismatches.
    # scan_numbers.sub()s the ids out for exactly this reason; the reviewer has to agree.
    stripped = CLAIM_ID.sub(" ", stripped)
    m = UNIT_DEFINITION.search(stripped)
    defs = forms(m.group(0)) if m else set()
    stripped = INLINE_MATH.sub(" ", stripped)
    return {t for t, _ in tokens_in(stripped)} - defs, defs


def baseline_keys() -> set[tuple[str, str, str]]:
    """(file, section, number) triples a human already recorded as reviewed debt."""
    if not BASELINE.exists():
        return set()
    doc = json.loads(BASELINE.read_text(encoding="utf-8"))
    return {(e["file"], str(e["section"]), str(e["number"])) for e in doc.get("entries", [])}


def paragraphs(lines: list[str]) -> list[str]:
    """The paragraph each line belongs to, for citation-scoping.

    A section that names `V-05-15` once and then spends four sentences on what 31 taps costs is
    writing normally. Requiring the backtick on every line would train the chapter into stamping
    the same citation four times, which is worse prose for no extra evidence.
    """
    out: list[str] = []
    buf: list[str] = []
    for line in lines:
        buf.append(line)
        if line.strip() == "":
            out.extend([" ".join(buf)] * len(buf))
            buf = []
    out.extend([" ".join(buf)] * len(buf))
    return out


def grade_file(
    path: Path,
    by: dict[str, dict[str, Any]],
    strong: dict[str, set[str]],
    weak: dict[str, set[str]],
    excused: set[tuple[str, str, str]],
) -> tuple[int, int, set[str]]:
    """Review one manuscript file. Returns (hard findings, notes, ids cited).

    Sections come from scan_numbers.split_sections, deliberately: the baseline this tool excuses
    against is keyed by that function's section names, and a reviewer that cut sections its own
    way would disagree with the gate about which numbers are reviewed debt for reasons that look
    like bugs from the outside.

    The hard/soft line is the no-double-gate rule from Issue #56. An invented number is
    scan_numbers' claim: prose it lets through is recorded in the baseline, so a number with no
    citation anywhere the gate could see it is excused here too, and what stays hard is the defect
    only this tool can see -- a number standing beside a citation that does not carry it (MISM),
    a citation to a record that does not exist (FAIL), and a number in prose that neither the
    paragraph, the section, the baseline, nor a declared derivation supports (orphan). Figure node
    text is notes-only: scan_numbers strips fences, so the baseline can never cover a picture, and
    a reviewer that hard-fails on geometry the gate cannot excuse would just be wrong.
    """
    # Comments are blanked before anything else, exactly as scan_numbers does it: an authoring note
    # like "the gate of Issue #59" is prose for the next editor, not a reader-facing claim, and its
    # digits would otherwise be graded as measurements. Newlines are preserved so line numbers stay
    # the ones a reader finds in the file. Claim ids, however, are read from the raw (pre-blanking)
    # lines, the same channel scan_numbers allows: an id may ride inside an HTML comment at the
    # start of a Source-cell row so the PDF hides it but the row keeps its citation. Numbers inside
    # comments stay blanked and are never graded here.
    raw = path.read_text(encoding="utf-8")
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), raw)
    raw_lines = raw.split("\n")
    hard = 0
    notes = 0
    cited_all: set[str] = set()
    print(f"=== {path.name}")
    for sec in split_sections(text):
        section = str(sec["heading"])
        body = "\n".join(raw_lines[lineno - 1] for lineno, _, _ in sec["lines"])
        sec_ids = {m.group(0) for m in CLAIM_ID.finditer(body)}
        cited_all |= sec_ids
        lines = sec["lines"]
        paras = paragraphs([raw_lines[lineno - 1] for lineno, _, _ in lines])
        for idx, (lineno, line, kind) in enumerate(lines):
            if kind == "heading":
                continue  # a heading's number is a position in the book, not a measurement
            in_fence = kind == "fence"
            para = paras[idx] if idx < len(paras) else line
            pids = {m.group(0) for m in CLAIM_ID.finditer(para)}
            declares_derivation = bool(DERIVED.search(line))
            texts = NODE_TEXT.findall(line) if in_fence else [line]
            for text_bit in texts:
                if in_fence and BARE_NUMBER.match(text_bit):
                    continue  # an axis tick is geometry, not a labelled claim
                # A citation is graded where it is printed, not by the paragraph's inheritance:
                # pids exists so a number on an uncited line borrows its paragraph's records, but
                # a dangling id reported that way would fire once per line in the paragraph.
                # The line's ids come from the raw line: a Source cell may hide its id inside an
                # HTML comment, and that id scopes the row exactly as a visible backtick id did.
                line_ids = {m.group(0) for m in CLAIM_ID.finditer(raw_lines[lineno - 1])}
                for rid in sorted(line_ids):
                    if rid not in by:
                        print(f"  FAIL  {path.name}:{lineno} [{section}] cites {rid}, not a record")
                        hard += 1
                ids = line_ids or pids
                if ids and not (ids & set(by)):
                    continue  # every citation here is unknown; the FAIL is the finding already
                toks, defs = quantities(text_bit)
                for tok in sorted(toks):
                    base = tok.rstrip(",")
                    cands = {tok, base, base.replace(",", "")}
                    excused_here = any((path.name, section, c) in excused for c in cands)
                    grade = "none"
                    for rid in ids:
                        if rid not in by:
                            continue
                        if cands & strong[rid]:
                            grade = "strong"
                            break
                        if cands & weak[rid]:
                            grade = "weak"
                    if grade == "none" and not ids:
                        # No citation beside the number. The section's records are the next court:
                        # a match there is attribution that drifted from its backtick (task #24's
                        # job to move), not an invention.
                        far = {
                            rid
                            for rid in sec_ids
                            if rid in by and cands & (strong[rid] | weak[rid])
                        }
                        if far:
                            print(
                                f"  note  {path.name}:{lineno} [{section}] {tok} carried by "
                                f"{sorted(far)}, cited elsewhere in the section"
                            )
                            notes += 1
                        elif excused_here:
                            pass  # reviewed debt already recorded by scan_numbers
                        elif in_fence or declares_derivation:
                            print(
                                f"  note  {path.name}:{lineno} [{section}] {tok} in "
                                f"{'figure text' if in_fence else 'a declared derivation'}, "
                                f"unattributed | {text_bit.strip()[:70]}"
                            )
                            notes += 1
                        else:
                            print(
                                f"  orphan {path.name}:{lineno} [{section}] {tok} has no citation "
                                f"and no section record carries it | {text_bit.strip()[:88]}"
                            )
                            hard += 1
                    elif grade == "none" and excused_here:
                        print(
                            f"  note  {path.name}:{lineno} [{section}] {tok} sanctioned by the "
                            f"baseline, not by {sorted(ids)}"
                        )
                        notes += 1
                    elif grade == "none" and declares_derivation:
                        print(
                            f"  note  {path.name}:{lineno} [{section}] {tok} declared derived "
                            f"from {sorted(ids)}, value not in them"
                        )
                        notes += 1
                    elif grade == "none" and any(
                        rid in by and cands & (strong[rid] | weak[rid]) for rid in sec_ids
                    ):
                        # The line cites a record that does not carry the number, but another record
                        # the same section cites does. That is attribution that drifted from its
                        # backtick -- the sentence should name the right id, and task #24 will move
                        # it into a table -- not a number attributed to a source that never printed
                        # it. The hard MISM is reserved for the sharper case below: no record in the
                        # whole section carries the figure the sentence is printing.
                        print(
                            f"  note  {path.name}:{lineno} [{section}] {tok} not in {sorted(ids)} "
                            f"but carried by another record the section cites"
                        )
                        notes += 1
                    elif grade == "none":
                        vals = " ".join(
                            sorted(str(by[rid].get("value", ""))[:20] for rid in ids if rid in by)
                        )
                        print(
                            f"  MISM  {path.name}:{lineno} [{section}] {tok} is in neither value "
                            f"nor context of {sorted(ids)} (values: {vals}) "
                            f"| {text_bit.strip()[:80]}"
                        )
                        hard += 1
                    elif grade == "weak":
                        print(
                            f"  note  {path.name}:{lineno} [{section}] {tok} only in the context "
                            f"fields of {sorted(ids)}"
                        )
                        notes += 1
                if defs and ids:
                    print(
                        f"  note  {path.name}:{lineno} [{section}] unit-definition digits "
                        f"{sorted(defs)} beside {sorted(ids)}"
                    )
                    notes += 1
    return hard, notes, cited_all


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="manuscript files to review")
    ap.add_argument("--check", action="store_true", help="review every chapter and the appendix")
    args = ap.parse_args(argv)
    if not CLAIMS.is_file():
        sys.exit(f"check_pairing: no registry at {CLAIMS}")
    doc = load_claims(CLAIMS)
    by = {str(r["id"]): r for r in records(doc)}
    strong, weak = field_forms(by)
    excused = baseline_keys()
    if args.check:
        # The same scope rule as scan_numbers --check: how-to-use and open-questions are
        # meta-documents about the book, and a reader-facing attribution review of them grades
        # prose nobody will cite as a claim.
        skip = ("how-to-use.md", "open-questions.md")
        paths = [ROOT / "book-en" / s for s in sources() if s not in skip]
    else:
        paths = [Path(f) for f in args.files]
    hard = 0
    notes = 0
    cited_ids: set[str] = set()
    for path in paths:
        h, n, c = grade_file(path, by, strong, weak, excused)
        hard += h
        notes += n
        cited_ids |= c
    print(f"hard: {hard}, notes: {notes}, ids cited: {len(cited_ids)}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
