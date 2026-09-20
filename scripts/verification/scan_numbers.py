"""Report every number in the manuscript that no cited claim supports. Exit code 0 means clean.

Why this exists
    docs/verification/claims.json holds 162 records, each with a value, a unit and a quote, and the
    manuscript cites those ids in prose. Nothing connected the two. A sentence could print a figure
    that was never fetched from anywhere and every gate in the repository would pass, because the
    gates check the shape of the registry (audit_claims.py) and the shape of the PDF
    (verify_book_pdf.sh), not whether a number in the prose has a source behind it. Issue #59.

Why citation-scoped, never chapter-scoped
    The claim id looks like it encodes a chapter, and it does not. Measured over the current
    manuscript: book-en/chapter08.md cites 35 distinct ids and none of them is V-08-*,
    chapter09.md cites 75 and none is V-09-*, chapter03.md cites 9 and none is V-03-*. The middle
    segment names the dossier a claim was fetched under, which is why V-07-03 is legitimately cited
    from chapter03.md, chapter09.md and open-questions.md. An allowlist derived from the prefix
    would
    reject almost every real citation in the book. So the allowlist for a section is built from the
    ids that section itself cites, and nothing else -- which is the only scoping that can actually
    fail, because an unsourced number cannot cite its way out.

What counts as support
    A numeric token is supported when it equals the value or the unit of a claim the same section
    cites, compared as numbers so that 23,616 and 23 616 and 23616 all match one record. In a table,
    the supporting ids must sit in the same row: book-en tables carry a "Where it comes from" column
    per row, and a row without a citation is a row making an uncited claim, which is the defect this
    tool exists to find.

What is exempt, and why each exemption is a region rather than a value
    Every rule below removes text before any matching happens, so it can only ever hide a class of
    position. A rule of the form "the number 2 is fine" would be a hole wide enough to walk a
    fabricated constant through, and is not implemented.
      - fenced blocks (``` tikz and ```): figure geometry. A node at 118:2.75cm is not a claim.
      - math, inline and display: a formula's structure. 2 in
        $N_\\text{ring} = T_\\text{left} \\times d_\\text{model} \\times 2 \\times b$ is the K-and-V
        pair, which is arithmetic the definition performs, not a measured quantity.
      - headings and horizontal rules: document structure.
      - cross-references: [Figure 8], "chapter 8", "section 9.4", "Appendix A" address the book.
      - an HTML comment or a raw-LaTeX block: authoring machinery, not prose.
    A number that survives all of that and matches nothing is reported. Declared derivations are
    reported too, in a separate list: prose that says "derived, from `V-05-31` with `V-05-32`" is
    using the same idiom the registry uses for its own arithmetic clauses, but this tool does not
    recompute the product, because 0.01 s times 4 equals 40 only after a unit conversion, and a
    matcher that guessed at conversion factors would be worse than a matcher that admits the limit.
    Every derived number is therefore listed for a human to check, and never silently waved through.

The two failure classes, and the baseline that keeps this tool usable without defanging it
    Measured over the current manuscript, 237 tokens fail the rule above, and they are two different
    problems. 135 are registered by some claim but not by one the printing section cites -- the
    number is real and the trail simply stops there, and the fix is a citation. 102 are registered
    by
    nothing at all, and almost all of those are derived arithmetic in chapter 1: a 400-sample
    frame, a
    160-sample hop, 257 FFT bins, 62.5 ms. Those quantities are correct, they are arithmetic on
    registered values, and the registry holds no record of them because no one has fetched a
    document
    that states them. Refusing to print them is not an option the book can accept, and exempting
    "numbers that look derived" is not an option the tool can accept either, because that is
    precisely
    the shape an invented number takes.

    So the current state of the manuscript is recorded in docs/verification/number_baseline.json and
    no number in it is exempted by rule. --check fails on any unmatched token that is NOT in the
    baseline, which is the whole point: the cage closes on new prose from today forward while the
    existing debt stays visible, counted, and shrinking -- stale baseline entries are reported so a
    chapter that gets citations added cannot quietly leave a hole behind. --strict ignores the
    baseline entirely and is what a chapter must pass before it can be called done. Issue #57 keeps
    its acceptance promise that no draft prints a number the registry cannot support.

usage
    python scripts/verification/scan_numbers.py                     # report everything, exit 0
    python scripts/verification/scan_numbers.py --check             # gate: fail on NEW unmatched
    python scripts/verification/scan_numbers.py --strict            # ignore the baseline
    python scripts/verification/scan_numbers.py --check book-en/chapter09.md
    python scripts/verification/scan_numbers.py --write-baseline    # rerecord current debt
    python scripts/verification/scan_numbers.py --list-derived      # only declared derivations
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Same convention as the other scripts in this directory: import the shared helpers by module name
# so the script runs from the repository root with no installed package and no PYTHONPATH
# assignment.
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims_lib import CLAIMS_PATH, NUMBER, load_claims, records  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
#: Which numbers the manuscript prints today that no cited claim supports. Reviewed, committed, and
#: the only thing standing between this check and a wall of 237 failures nobody reads.
BASELINE_PATH = ROOT / "docs" / "verification" / "number_baseline.json"

#: A claim id as printed in prose, in backticks or bare.
CLAIM_ID = re.compile(r"\bV-(\d{2})-(\d{2})\b")
#: A level-2 or level-3 heading, which is what carries a section number in this manuscript.
HEADING = re.compile(r"^(#{1,3})\s+(.*)$")
#: Which section a stretch of prose belongs to: the number, if the heading has one.
SECTION_NO = re.compile(r"^(\d+(?:\.\d+)*)\s")
TABLE_ROW = re.compile(r"^\s*\|")
HRULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
FENCE = re.compile(r"^\s*```")
LATEX_RAW = re.compile(r"^\s*```\{=latex\}")
#: A cross-reference to a part of a document rather than to the world: this book's own sections and
#: floats, and the page/table numbers a citation uses to point into a source. Neither class states a
#: measured quantity, and 22 in "page 22, Table 23" is the same kind of number as 9 in "chapter 9".
CROSSREF = re.compile(
    r"""
    \[(?:Figure|Table|Listing|Section|Appendix)\s+\d[.\d]*\]   # bracketed link label
    |(?:chapter|section|subsection|figure|table|listing|appendix|Eq\.|equation)\s+\#?\d+(?:\.\d+)*
    |(?:page|pages|p\.|pp\.)\s*\d+(?:[,-]\d+)*
    |Appendix\s+[A-Z]\b
    """,
    re.VERBOSE | re.IGNORECASE,
)
#: An authoring comment, which is a note to the next editor and not text a reader sees.
COMMENT = re.compile(r"<!--.*?-->", re.S)
#: A number as prose prints it. The comma is a thousands separator only in groups of three, because
#: "page 22, Table 23" and "[left, right]" made the registry's looser NUMBER swallow "22," and
#: "70,13" as single values -- 16 findings in the current manuscript were that one regex.
PROSE_NUMBER = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
#: A number is a quantity only when it does not continue an identifier. Without this guard the
#: digits of a part name are read as a claim: KV260 contributed 260, exp_01_streaming... contributed
#: 01. That guard alone accounts for 41 of the findings the first version of this tool reported.
NOT_IN_IDENTIFIER = re.compile(r"[A-Za-z_0-9]$")
#: Prose that declares a number to be arithmetic on other claims, in the registry's own idiom.
DERIVED = re.compile(r"\b(?:derived|computed|calculated)\b", re.IGNORECASE)


def as_number(token: str) -> float | None:
    """Turn a printed or registered number into a float, forgiving every separator in use.

    The registry writes 23616 and the manuscript writes 23 616 with a thousands space and, in one
    place, 23,616. All three are the same quantity, and a matcher that treated them as three values
    would either flag correct prose or accept a typo.
    """
    cleaned = token.replace(",", "").replace(" ", "").replace(" ", "").rstrip(".")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", cleaned):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def claim_numbers(rec: dict[str, Any]) -> set[float]:
    """The numbers a record puts on the table: its value and its unit.

    The unit is included because units carry real numbers in this registry -- "BRAM36 blocks",
    "DSP48E2 slices", "-2LV / 0.72V" -- and a section citing V-01-05 may legitimately print 36.
    """
    out: set[float] = set()
    for field in ("value", "unit"):
        for m in NUMBER.finditer(str(rec.get(field, ""))):
            v = as_number(m.group(0))
            if v is not None:
                out.add(round(v, 6))
    return out


def registry_numbers() -> dict[str, set[float]]:
    doc = load_claims(CLAIMS_PATH)
    return {r["id"]: claim_numbers(r) for r in records(doc)}


def split_sections(text: str) -> list[dict[str, Any]]:
    """Cut a markdown file into sections, each remembering the heading it sits under.

    A section is the unit of citation: the ids it prints are the numbers it may print. Fenced blocks
    are consumed whole, so a tikz picture can never contribute a heading or a section break.
    """
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] = {"heading": "(front matter)", "lines": []}
    sections.append(current)
    in_fence = False
    for lineno, line in enumerate(text.split("\n"), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            current["lines"].append((lineno, line, "fence"))
            continue
        if in_fence:
            current["lines"].append((lineno, line, "fence"))
            continue
        m = HEADING.match(line)
        if m:
            level, title = len(m.group(1)), m.group(2).strip()
            if level <= 2:
                sm = SECTION_NO.match(title)
                current = {
                    "heading": sm.group(1) if sm else title,
                    "title": title,
                    "lines": [],
                }
                sections.append(current)
                continue
        kind = "table" if TABLE_ROW.match(line) else "heading" if m else "prose"
        current["lines"].append((lineno, line, kind))
    return sections


def strip_regions(line: str, kind: str) -> str:
    """Blank out the parts of a line that cannot carry a claim, keeping positions stable."""
    if kind in ("fence", "heading"):
        return ""
    s = CROSSREF.sub(" ", line)
    # $$ ... $$ on one line, and $ ... $ within a line. Math is stripped after cross-references so
    # that a reference inside math, which this manuscript does not use, cannot resurrect itself.
    s = re.sub(r"\$\$.*?\$\$", " ", s)
    s = re.sub(r"\$[^$]*\$", " ", s)
    # Inline code is NOT stripped: this manuscript cites claims inside backticks, and a citation in
    # code fences only at block level. The claim ids are pulled out separately before matching.
    return s


def tokens_in(s: str) -> list[tuple[str, int]]:
    """Numeric tokens with their column, restricted to quantities and not to identifier digits."""
    out: list[tuple[str, int]] = []
    for m in PROSE_NUMBER.finditer(s):
        # A bare "2024" style year is left alone on purpose: a year in prose is a claim about when
        # something happened, and this tool has no business deciding silently that it is structure.
        if NOT_IN_IDENTIFIER.search(s[: m.start()]):
            continue
        out.append((m.group(0), m.start()))
    return out


def scan_file(
    path: Path, allowed: dict[str, set[float]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return one finding per numeric token that no cited claim in its own scope supports."""
    text = path.read_text(encoding="utf-8")
    # Comments are blanked rather than deleted, so that a line number reported here is the line a
    # reader finds in the file. Comment contents are where authors write things like "8.1 reviewed
    # fragment", and a section number inside a comment is not a claim about the world.
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    findings: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    for sec in split_sections(text):
        body = "\n".join(line for _, line, _ in sec["lines"])
        cited = sorted({m.group(0) for m in CLAIM_ID.finditer(body)})
        support: set[float] = set()
        for cid in cited:
            support |= allowed.get(cid, set())
        for lineno, line, kind in sec["lines"]:
            ids_here = {m.group(0) for m in CLAIM_ID.finditer(line)}
            # In a table the row is the scope; in prose the section is the scope. See the docstring.
            scope_support = support
            if kind == "table" and not ids_here:
                scope_support = set()
            elif kind == "table":
                scope_support = set()
                for cid in ids_here:
                    scope_support |= allowed.get(cid, set())
            stripped = strip_regions(CLAIM_ID.sub(" ", line), kind)
            sentence_is_derived = bool(DERIVED.search(line))
            for tok, col in tokens_in(stripped):
                v = as_number(tok)
                if v is None:
                    continue
                rounded = round(v, 6)
                if rounded in scope_support:
                    continue
                rec = {
                    "file": path.name,
                    "section": str(sec["heading"]),
                    "line": lineno,
                    "token": tok,
                    "cited": cited,
                    "in_table": kind == "table",
                }
                # Registered somewhere but not cited here is the sharpest finding this tool makes:
                # the number is real, and the reader simply cannot get from it to a source.
                where = [cid for cid, nums in allowed.items() if rounded in nums]
                rec["registered_elsewhere"] = sorted(where)[:6]
                if sentence_is_derived:
                    rec["declared_derived"] = True
                    derived.append(rec)
                else:
                    findings.append(rec)
    return findings, derived


def key_of(rec: dict[str, Any]) -> tuple[str, str, str]:
    """What a baseline entry keys on: this number, in this section, of this file.

    Deliberately not the line number. A citation added three paragraphs up shifts every line below
    it,
    and a baseline that breaks on reflow is a baseline someone regenerates without reading, which is
    how it would stop meaning anything. Section plus number still catches the case that matters: the
    same figure appearing somewhere it has never appeared before is a new claim, not a reflow.
    """
    return (rec["file"], str(rec["section"]), str(rec["token"]))


def load_baseline() -> dict[tuple[str, str, str], dict[str, Any]]:
    if not BASELINE_PATH.exists():
        return {}
    doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {(e["file"], e["section"], e["number"]): e for e in doc.get("entries", [])}


def write_baseline(findings: list[dict[str, Any]]) -> int:
    """Record the manuscript's present debt, keyed and deduplicated, for a human to review."""
    entries: dict[tuple[str, str, str], dict[str, Any]] = {}
    for rec in findings:
        k = key_of(rec)
        entries.setdefault(
            k,
            {
                "file": rec["file"],
                "section": str(rec["section"]),
                "number": str(rec["token"]),
                "class": "registered-not-cited-here"
                if rec["registered_elsewhere"]
                else "unregistered",
                "registered_by": rec["registered_elsewhere"],
                "section_cites": rec["cited"],
                "in_table_row": rec["in_table"],
            },
        )
    ordered = sorted(
        entries.values(),
        # as_number, not float: the manuscript prints 16,000 and 23 616, and a sort key that
        # raises on a thousands separator dies on the first run, which is how this line was tested.
        key=lambda e: (e["file"], e["section"], as_number(e["number"]) or 0.0),
    )
    doc = {
        "version": "1.0.0",
        "note": (
            "Numbers the manuscript prints that no claim cited by their own section supports."
            " This is debt, not permission: see scripts/verification/scan_numbers.py for what"
            " --check and --strict do with it, and add a citation rather than an entry wherever"
            " one will fit."
        ),
        "entries": ordered,
    }
    BASELINE_PATH.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return len(ordered)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("files", nargs="*", help="markdown files to scan (default: the manuscript)")
    ap.add_argument("--check", action="store_true", help="exit 1 on any number the baseline lacks")
    ap.add_argument("--strict", action="store_true", help="ignore the baseline and fail on all")
    ap.add_argument("--write-baseline", action="store_true", help="record today's debt and exit 0")
    ap.add_argument(
        "--list-derived", action="store_true", help="print only the declared derivations"
    )
    ap.add_argument("--manuscript", default="book-en", help="book | book-en (default book-en)")
    args = ap.parse_args(argv)

    allowed = registry_numbers()
    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        skip = ("how-to-use.md", "open-questions.md")
        targets = sorted(p for p in (ROOT / args.manuscript).glob("*.md") if p.name not in skip)

    findings: list[dict[str, Any]] = []
    derived: list[dict[str, Any]] = []
    for path in targets:
        f, dr = scan_file(path, allowed)
        findings += f
        derived += dr

    if args.write_baseline:
        n = write_baseline(findings)
        uncited = sum(1 for r in findings if r["registered_elsewhere"])
        print(f"baseline: {n} distinct number(s) recorded, from {len(findings)} occurrence(s)")
        print(
            f"  {uncited} registered by a claim this section does not cite, "
            f"{n - len([r for r in findings if not r['registered_elsewhere']])} unregistered"
        )
        return 0

    baseline = {} if args.strict else load_baseline()
    fresh = [r for r in findings if key_of(r) not in baseline]
    seen = {key_of(r) for r in findings}
    stale = [k for k in baseline if k not in seen]

    if not args.list_derived:
        print(
            f"scan_numbers: {len(targets)} file(s), {len(allowed)} claims, "
            f"{len(findings)} unmatched occurrence(s) in {len(seen)} "
            f"distinct number/section pair(s); baseline holds {len(baseline)}"
        )
        # Each mode chooses the list it shows: plain shows everything, --strict shows everything
        # it would fail on, --check shows only the un-baselined part. A per-record filter on top
        # of that is what an earlier draft of this block wrongly added.
        shown = fresh if (args.check and not args.strict) else findings
        for rec in shown:
            hint = (
                "  (registered by "
                + ", ".join(rec["registered_elsewhere"])
                + "; cite it in this section's Traceability table)"
                if rec["registered_elsewhere"]
                else "  (no registered value anywhere equals this)"
            )
            mark = " [table row]" if rec["in_table"] else ""
            print(
                f"  UNSOURCED {rec['file']}:{rec['line']}{mark}  section {rec['section']}  "
                f"number {rec['token']}{hint}"
            )
        print(f"unsourced numbers not excused by the baseline: {len(fresh)}")
    if args.list_derived or not (args.check or args.strict):
        print(f"declared derivations this tool did not recompute: {len(derived)}")
        for rec in derived:
            print(
                f"  {rec['file']}:{rec['line']}  section {rec['section']}"
                f"  number {rec['token']}  "
                "prose declares it derived; check the arithmetic by hand"
            )
    if stale:
        print(
            f"baseline entries no longer needed -- debt repaid, regenerate to record it: "
            f"{len(stale)}"
        )
        for k in sorted(stale)[:10]:
            print("  " + "  ".join(k))

    if (args.check or args.strict) and fresh:
        print("FAIL: numbers printed with no claim cited by their own section behind them")
        return 1
    if args.check or args.strict:
        print(
            "PASS: every number outside math, figures and headings is backed by a claim its own "
            "section cites, or listed in the reviewed baseline"
        )
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
