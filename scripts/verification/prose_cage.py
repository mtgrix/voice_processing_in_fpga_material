"""Enforce invisible scaffolding in the manuscript's prose. Exit code 0 means clean.

Why this exists
    docs/BOOK_PEDAGOGY.md section 8 promises that traceability lives in a table, never in a
    sentence, and the pedagogy harness (RULE 1) extends that promise to the whole voice of
    the book: no evidence codes in prose, no audit meta-language, no measured quantities
    spelled out as words. scan_numbers.py guards the *content* (every number has a claim),
    not the *form* (how the number and the evidence trail are printed). A sentence like "one
    thousand two hundred and forty-eight hardened multiply-accumulate slices (V-01-05)" is
    perfectly numbered and perfectly unreadable: the number is spelled out to escape the
    numeric cage, and the record id cuts the clause a reader is following. Each defect is
    invisible to every other gate, because each other gate looks at the shape of the
    evidence set, not at the shape of the sentence.

The three cages, all over prose lines only
    Tables are the sanctioned home of traceability (BOOK_PEDAGOGY section 8), and fences
    hold geometry, math and headings hold structure -- so every rule applies to lines the
    section splitter calls prose, and nothing else.
      - prose-v: a `V-xx-yy` id on a prose line, backticks included. The fix is a row in the
        section's end-of-section Traceability table, never an inline code span.
      - word-number: a spelled-out cardinal or fractional quantity on a prose line. The
        parser resolves English cardinals ("one thousand two hundred and forty-eight" =
        1248, "twenty-three thousand six hundred and sixteen" = 23616, "one-hundred-and-
        sixty" = 160, "eleven point three five" = 11.35, "one one-hundredth" = 0.01) and
        reports the phrase when it is a measured quantity: any value 13 or above, any
        fraction, any decimal. 12 and below stay words by English convention ("the four
        paths", "eight-bit"). Plurals are deliberately not number words, so the rhetorical
        "thousands of design decisions" passes and the exact "two thousand" fails.
      - audit-language: a curated set of multi-word phrases ("the records say", "registered
        gap", "which reading", "no record in this registry") that talk about the evidence
        machinery instead of about the signal path. Every phrase is long enough that a
        legitimate hardware use of "record" or "register" survives.

The baseline
    Measured over the current manuscript, the three cages find a pile of violations, and the
    pile is exactly the debt Issue #99 exists to pay down. As with scan_numbers.py, the
    current state is recorded in docs/verification/prose_baseline.json, --check fails on a
    violation the baseline does not hold, --strict ignores the baseline entirely and is what
    a chapter must pass before it can be called done, and stale baseline entries are reported
    so a chapter that gets cleaned cannot quietly leave a hole behind. The debt is named and
    counted, not excused.

How this stays consistent with scan_numbers
    The section model (what a section is, what a table row is, what a fence is) is the same
    one scan_numbers.py uses: it is imported from there, not reimplemented, so the two cages
    can never disagree about where prose ends and a table begins.

usage
    python scripts/verification/prose_cage.py                        # report everything, exit 0
    python scripts/verification/prose_cage.py --check                # gate: fail on NEW violations
    python scripts/verification/prose_cage.py --strict               # ignore the baseline
    python scripts/verification/prose_cage.py --check book-en/chapter05.md
    python scripts/verification/prose_cage.py --write-baseline       # rerecord current debt
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scan_numbers import CLAIM_ID, COMMENT, split_sections, strip_regions  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
#: Which prose violations the manuscript holds today. Reviewed, committed, and the only thing
#: standing between this check and a wall of failures nobody reads.
BASELINE_PATH = ROOT / "docs" / "verification" / "prose_baseline.json"

#: Files whose subject matter is the evidence system itself. how-to-use.md explains what a
#: V-xx-yy reference *is*; the id format is the lesson, so a prose line there cannot be an
#: infraction. scan_numbers.py skips exactly this file for the same reason.
SKIP = ("how-to-use.md",)

# ------------------------------------------------------------ cardinals --


_UNIT: dict[str, float] = {
    "zero": 0.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "eleven": 11.0,
    "twelve": 12.0,
    "thirteen": 13.0,
    "fourteen": 14.0,
    "fifteen": 15.0,
    "sixteen": 16.0,
    "seventeen": 17.0,
    "eighteen": 18.0,
    "nineteen": 19.0,
}
_TENS: dict[str, float] = {
    "twenty": 20.0,
    "thirty": 30.0,
    "forty": 40.0,
    "fifty": 50.0,
    "sixty": 60.0,
    "seventy": 70.0,
    "eighty": 80.0,
    "ninety": 90.0,
}
_SCALES: dict[str, float] = {
    "hundred": 100.0,
    "thousand": 1000.0,
    "million": 1e6,
    "billion": 1e9,
}
#: Fraction words end a quantity: "one one-hundredth of a second" is 0.01 s. Their presence
#: alone makes the phrase a violation, because a fraction in words is always a quantity
#: waiting for its digits.
_FRACTIONS: dict[str, float] = {
    # Plural forms are number words too: "three hundredths of a second" is the same
    # fraction as "one hundredth", and without the plural keys the parser stops before
    # the fraction word and reads only "three" -- 3, under the 13 threshold, so a real
    # spelled-out fraction would ride through the cage.
    "tenth": 0.1,
    "tenths": 0.1,
    "hundredth": 0.01,
    "hundredths": 0.01,
    "thousandth": 0.001,
    "thousandths": 0.001,
    "millionth": 1e-6,
    "millionths": 1e-6,
}
_DIGITS: dict[str, float] = {
    "zero": 0.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
}
_CONNECTORS = frozenset({"and", "point"})
_NUM_WORDS = frozenset({*_UNIT, *_TENS, *_SCALES, *_FRACTIONS, *_CONNECTORS})

#: Every word, hyphen-split implicitly: a hyphen is punctuation between words, so
#: "one-hundred-and-sixty-sample-hop" parses on "one hundred and sixty" exactly as the
#: space-separated sentence does.
WORD = re.compile(r"[A-Za-z]+")


def parse_cardinal_run(run: list[str]) -> tuple[list[str], float]:
    """Consume the longest cardinal `run`'s head forms; return (words consumed, value).

    The parser mirrors schoolbook English: hundreds multiply what has been counted so far,
    thousand/million add a completed chunk, "and" is a connector only after a scale has been
    seen, and "point" switches to decimal digits. A fraction word ends the phrase, carrying
    the value built so far -- "one one-hundredth" is 1 x 0.01, and a bare "hundredth" is
    1 x 0.01 as well.
    """
    consumed: list[str] = []
    total = 0.0
    current = 0.0
    saw_scale = False
    for idx, w in enumerate(run):
        if w in _FRACTIONS:
            consumed.append(w)
            if len(consumed) >= 3 and consumed[-3] in _UNIT and consumed[-2] == "one":
                # "one one-hundredth" is the article "a" plus the fraction "one-hundredth",
                # both 1: the singular fraction cannot be reached by any other doubling
                # ("two one-hundredths" is plural and never enters this branch), so the
                # numerator is 1 no matter what the article said.
                base = _UNIT["one"]
            else:
                base = total + current if (total or current) else 1.0
            return consumed, base * _FRACTIONS[w]
        if w in _UNIT or w in _TENS:
            consumed.append(w)
            current += _UNIT[w] if w in _UNIT else _TENS[w]
        elif w == "hundred":
            consumed.append(w)
            saw_scale = True
            current = (current if current else 1.0) * 100.0
        elif w in _SCALES:
            consumed.append(w)
            saw_scale = True
            total += (current if current else 1.0) * _SCALES[w]
            current = 0.0
        elif w == "and":
            if not saw_scale and not total:
                break
            consumed.append(w)
        elif w == "point":
            if not any(d in _DIGITS for d in run[idx + 1 :]):
                break
            digits = [d for d in run[idx + 1 :] if d in _DIGITS]
            consumed.append(w)
            consumed.extend(digits)
            frac = 0.0
            for d in digits:
                frac = frac * 10.0 + _DIGITS[d]
            return consumed, total + current + frac * (10.0 ** -len(digits))
    return consumed, total + current


def cardinal_phrases(line: str) -> list[tuple[str, float, int, int]]:
    """Every spelled-out cardinal in `line`: (canonical words, value, start, end column)."""
    out: list[tuple[str, float, int, int]] = []
    toks = [(m.group(0).lower(), m.start(), m.end()) for m in WORD.finditer(line)]
    i = 0
    n = len(toks)
    while i < n:
        w = toks[i][0]
        if w not in _NUM_WORDS or w in _CONNECTORS:
            i += 1
            continue
        # A scale word directly after an Arabic digit is a unit, not a spelled cardinal:
        # "2.056 million per second" and "about 14 million parameters" carry their quantity in
        # the digit, and "million" there is the multiplier the digit already names.
        if line[: toks[i][1]].rstrip().endswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            i += 1
            continue
        run = [w]
        j = i + 1
        while j < n and toks[j][0] in _NUM_WORDS:
            run.append(toks[j][0])
            j += 1
        consumed, value = parse_cardinal_run(run)
        phrase = " ".join(consumed)
        out.append((phrase, value, toks[i][1], toks[i + len(consumed) - 1][2]))
        i += max(1, len(consumed))
    return out


def phrase_is_measured(phrase: str, value: float) -> bool:
    """A spelled-out quantity is a violation when digits would read better.

    Only a phrase that names a digit (a unit word like "six", a tens word like "sixty"), a
    fraction, or a decimal counts as a measured quantity. A *bare* scale word -- "a few
    thousand", "a thousand or a million", "hundred" in "a hundred times" -- is either a unit
    riding on a digit that was checked upstream, or an approximation English keeps as words
    ("the thousands of design decisions"), so it passes. 13 and up are always digits in this
    book; 12 and below are words by the same convention, so "the four paths" and "eight-bit"
    pass.
    """
    words = phrase.split()
    if "point" in words or any(w in _FRACTIONS for w in words):
        return True
    if not any(w in _UNIT or w in _TENS for w in words):
        return False
    return value >= 13.0


# ------------------------------------------------------ audit vocabulary --


#: Meta-language that talks about the evidence machinery instead of about the signal path.
#: Every phrase is deliberately multi-word: "registered gap" is audit-speak while "the
#: firmware registers" is not, and "record the latencies" is honest prose that "the records
#: say" would have caught. All of them survive on a line without a V-id and with a real
#: number, which is what makes them invisible to scan_numbers.
AUDIT_PHRASES: tuple[tuple[str, str], ...] = (
    ("the records say", "the evidence machinery is talking; say what it shows"),
    ("the records state", "the evidence machinery is talking; say what it shows"),
    ("the record says", "the evidence machinery is talking; say what it shows"),
    ("the record states", "the evidence machinery is talking; say what it shows"),
    ("which record says", "the evidence machinery is talking; say what it shows"),
    ("what the record says", "the evidence machinery is talking; say what it shows"),
    ("which reading", "compare readings in reader terms, not by pointing at the machinery"),
    ("registered gap", "a gap is a gap; do not grant it rank in the record system"),
    ("registered by", "traceability belongs in the end-of-section table, not this sentence"),
    ("registered figure", "a number in prose does not need its provenance as an adjective"),
    ("unregistered figure", "a number in prose does not need its provenance as an adjective"),
    ("unresolved record", "say what is unknown about the hardware, not about the records"),
    (
        "no record in this registry",
        "a gap in evidence is a sentence about the subject, not about the registry",
    ),
    ("this registry", "the reader is studying the signal path, not the evidence files"),
    ("records column", "point readers at the table if it helps; do not narrate its columns"),
    ("not cited here", "citation placement is machinery; it never belongs in the sentence"),
    ("registered elsewhere", "citation placement is machinery; it never belongs in the sentence"),
    ("the trail stops", "say what the evidence fails to say, in one plain sentence"),
    ("the citation trail", "say what the evidence fails to say, in one plain sentence"),
    ("unsourced", "say what the evidence fails to say, in one plain sentence"),
)


# ------------------------------------------------------------ scanning --


def scan_file(path: Path) -> list[dict[str, Any]]:
    """One finding per prose violation in `path`, tagged with its kind and its match."""
    text = path.read_text(encoding="utf-8")
    # Comments are blanked rather than deleted, so a line number reported here is the line a
    # reader finds in the file. scan_numbers.py does the same for its scans.
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    findings: list[dict[str, Any]] = []
    for sec in split_sections(text):
        for lineno, line, kind in sec["lines"]:
            if kind != "prose":
                continue
            for m in CLAIM_ID.finditer(line):
                findings.append(
                    {
                        "file": path.name,
                        "section": str(sec["heading"]),
                        "line": lineno,
                        "kind": "prose-v",
                        "match": m.group(0),
                        "value": None,
                        "hint": "record ids belong in this section's Traceability table,"
                        " never in a sentence",
                    }
                )
            low = strip_regions(line, kind).lower()
            for phrase, hint in AUDIT_PHRASES:
                if phrase in low:
                    findings.append(
                        {
                            "file": path.name,
                            "section": str(sec["heading"]),
                            "line": lineno,
                            "kind": "audit-language",
                            "match": phrase,
                            "value": None,
                            "hint": hint,
                        }
                    )
            for phrase, value, _start, _end in cardinal_phrases(strip_regions(line, kind)):
                if not phrase_is_measured(phrase, value):
                    continue
                findings.append(
                    {
                        "file": path.name,
                        "section": str(sec["heading"]),
                        "line": lineno,
                        "kind": "word-number",
                        "match": phrase,
                        "value": value,
                        "hint": f'"{phrase}" is {value:g}; write the quantity as digits',
                    }
                )
    return findings


def key_of(rec: dict[str, Any]) -> tuple[str, str, str]:
    """What a baseline entry keys on: this violation, in this section, of this file.

    Deliberately not the line number -- a paragraph rewritten two lines up shifts every line
    below it, and a baseline that breaks on reflow is a baseline someone regenerates without
    reading. The kind prefix keeps the three cages from colliding on identical strings.
    """
    return (rec["file"], str(rec["section"]), f"{rec['kind']}:{rec['match']}")


def load_baseline() -> dict[tuple[str, str, str], dict[str, Any]]:
    if not BASELINE_PATH.exists():
        return {}
    doc = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {(e["file"], e["section"], e["key"]): e for e in doc.get("entries", [])}


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
                "key": f"{rec['kind']}:{rec['match']}",
                "kind": rec["kind"],
                "match": rec["match"],
                "value": rec["value"],
                "hint": rec["hint"],
            },
        )
    ordered = sorted(entries.values(), key=lambda e: (e["file"], e["section"], e["key"]))
    doc = {
        "version": "1.0.0",
        "note": (
            "Prose violations in the manuscript held the day the prose cage went live: V-xx-yy"
            " ids in sentences, measured quantities spelled out as words, and audit"
            " meta-language. This is debt, not permission -- see"
            " scripts/verification/prose_cage.py for what --check and --strict do with it."
            " A chapter that fixes its prose shrinks this file; run --write-baseline only"
            " after the fix, never to make the debt disappear."
        ),
        "entries": ordered,
    }
    BASELINE_PATH.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    return len(ordered)


KIND_LABEL = {"prose-v": "PROSE-V", "word-number": "WORDNUM", "audit-language": "AUDIT-LANG"}


# --------------------------------------------------------------- main --


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("files", nargs="*", help="markdown files to scan (default: the manuscript)")
    ap.add_argument(
        "--check", action="store_true", help="exit 1 on any violation the baseline lacks"
    )
    ap.add_argument("--strict", action="store_true", help="ignore the baseline and fail on all")
    ap.add_argument("--write-baseline", action="store_true", help="record today's debt and exit 0")
    ap.add_argument("--manuscript", default="book-en", help="book | book-en (default book-en)")
    args = ap.parse_args(argv)

    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        targets = sorted(p for p in (ROOT / args.manuscript).glob("*.md") if p.name not in SKIP)

    findings: list[dict[str, Any]] = []
    for path in targets:
        findings += scan_file(path)

    if args.write_baseline:
        n = write_baseline(findings)
        print(f"baseline: {n} distinct violation(s) recorded, from {len(findings)} occurrence(s)")
        return 0

    baseline = {} if args.strict else load_baseline()
    fresh = [r for r in findings if key_of(r) not in baseline]
    seen = {key_of(r) for r in findings}
    stale = [k for k in baseline if k not in seen]

    print(
        f"prose_cage: {len(targets)} file(s), {len(findings)} violation(s) in "
        f"{len(seen)} distinct kind/section pair(s); baseline holds {len(baseline)}"
    )
    shown = fresh if args.check and not args.strict else findings
    for rec in shown:
        val = f"  = {rec['value']:g}" if rec["value"] is not None else ""
        print(
            f"  {KIND_LABEL[rec['kind']]}  {rec['file']}:{rec['line']}  section {rec['section']}"
            f"  {rec['match']}{val}  -- {rec['hint']}"
        )
    if args.check or args.strict:
        print(f"prose violations not excused by the baseline: {len(fresh)}")
    if stale:
        print(
            f"baseline entries no longer needed -- debt repaid, regenerate to record it: "
            f"{len(stale)}"
        )
        for k in sorted(stale)[:10]:
            print("  " + "  ".join(k))

    if (args.check or args.strict) and fresh:
        print("FAIL: prose carries evidence codes, spelled-out quantities, or audit language")
        return 1
    if args.check or args.strict:
        print(
            "PASS: prose lines are free of evidence codes, spelled-out quantities"
            " and audit language"
        )
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
