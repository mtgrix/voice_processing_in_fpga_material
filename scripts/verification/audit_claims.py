"""Audit the docs/verification evidence set. Exit code 0 means every check passed.

This is the check that catches the defect class the evidence set exists to avoid: a
correct-looking value sitting next to a quote that cannot possibly produce it. It is
deliberately stricter than the manual review that repaired the records.

Checks
    1. structure    claims.json parses, ids are well formed, unique and ordered, every
                    record carries all fifteen fields, status and tier are in vocabulary.
    2. traceability every number in a verified value is printed in the quote, the locator,
                    or the document identity, or is covered by an arithmetic clause it declares.
    3. arithmetic   declared arithmetic clauses are evaluated rather than admired.
                    Equations must compute to their stated result and inequalities must
                    actually hold.
    4. sourcing     a verified record needs a URL, a T1/T2 record needs a locator, and a
                    record hosted on a third-party mirror must say so in its notes.
    5. consistency  README summary counts match the JSON, and each record has exactly one
    6. units        every record's unit is a registered term, and the registry holds:
                    a canonical has a kind, and none folds kilobits in with kilobytes.
                    heading among the markdown files.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from typing import Any

# The helpers beside this file are imported by module name, so that the script runs
# from the repository root without an installed package or a PYTHONPATH assignment.
if __package__ in (None, ""):
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims_lib import (
    CITATION_UNIT,
    CLAIMS_PATH,
    EVIDENCE_DIR,
    RECORD_FIELDS,
    STATUSES,
    TIERS,
    UNIT_KINDS,
    UNIT_TERMS,
    arithmetic_clause,
    file_of,
    load_claims,
    memory_side,
    numeric_tokens,
    parse_record_id,
    records,
    spellings_for,
    unit_canonical,
)

#: Hosts that are not the publisher of the document they serve. Pointing at one is
#: acceptable for a PDF that is otherwise hard to fetch, but the record must admit it.
MIRROR_HOSTS = (
    "connecttech.com",
    "waveshare.com",
    "generation-robots.com",
    "hthreads.github.io",
)

#: Hosts that are canonical for the content they serve. Kept so that the mirror list can
#: be widened without ever swallowing one of these.
#: NVIDIA's Jetson datasheets are served from developer.nvidia.com, not docs.nvidia.com, and
#: the download host redirects there. Both are canonical for the documents they carry.
VENDOR_HOSTS = (
    "docs.nvidia.com",
    "developer.nvidia.com",
    "developer.download.nvidia.com",
    "docs.amd.com",
    "docs.pytorch.org",
    "arxiv.org",
)

UNIT_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_./+-]*")
COMPARISON = re.compile(r"^(?P<lhs>[^=<>]*?)\s*(?P<op>>=|<=|==|>|<)\s*(?P<rhs>[^=<>]+)$")
EQUATION = re.compile(r"^(?P<lhs>[^=]+?)=\s*(?P<rhs>[^=]+)$")
SAFE_EXPR = re.compile(r"^[0-9.+\-*/()=<> \t]+$")
NUMBER_TEXT = re.compile(r"\d[\d,]*(?:\.\d+)?")


def prepare(statement: str) -> str:
    """Strip unit words from a clause fragment, leaving digits and operators.

    Unit tokens are removed whole, including the slash inside them, so that
    "50,000 GOP/s / 102 GB/s" becomes "50000 / 102" rather than "50000 / / 102".
    """
    without_units = UNIT_TOKEN.sub(" ", statement)
    without_separators = re.sub(r",(?=\d{3}\b)", "", without_units)
    collapsed = re.sub(r"[ \t]+", " ", without_separators)
    return collapsed.strip()


def evaluate(fragment: str) -> float | bool | None:
    """Evaluate a numeric expression or a comparison. None when it is not evaluable."""
    cleaned = prepare(fragment)
    if not cleaned or not SAFE_EXPR.match(cleaned):
        return None
    try:
        result: Any = eval(cleaned, {"__builtins__": {}}, {})  # noqa: S307
    except Exception:
        return None
    if isinstance(result, (bool, int, float)):
        return (
            float(result)
            if isinstance(result, (int, float)) and not isinstance(result, bool)
            else result
        )
    return None


def tolerance(stated: float) -> float:
    """Half a unit in the last decimal place the record chose to write."""
    text = repr(stated)
    decimals = len(text.split(".")[1]) if "." in text else 0
    quantum: float = max(0.5 * 10.0 ** (-float(decimals)), 1e-9)
    return quantum * 1.001


def check_structure(recs: list[dict[str, Any]], fails: list[str]) -> None:
    """Ids, fields, and vocabularies."""
    seen: set[str] = set()
    for rec in recs:
        rid = str(rec.get("id", ""))
        try:
            parse_record_id(rid)
        except ValueError as exc:
            fails.append(f"structure: {exc}")
        if rid in seen:
            fails.append(f"structure: duplicate id {rid}")
        seen.add(rid)
        missing = [field for field in RECORD_FIELDS if field not in rec]
        if missing:
            fails.append(f"structure: {rid} missing fields {missing}")
        if rec.get("status") not in STATUSES:
            fails.append(f"structure: {rid} status {rec.get('status')!r} is not a known status")
        if rec.get("source_tier") not in TIERS:
            fails.append(
                f"structure: {rid} source_tier {rec.get('source_tier')!r} is not a known tier"
            )
    ids = [str(r.get("id")) for r in recs]
    ordered = sorted(ids, key=lambda i: (file_of(i), int(i.rsplit("-", 1)[1])))
    if ids != ordered:
        fails.append("structure: records are not in id order")


def check_sourcing(recs: list[dict[str, Any]], fails: list[str]) -> list[str]:
    """URLs, locators, and mirror acknowledgement. Returns the mirror-using ids."""
    mirrors: list[str] = []
    for rec in recs:
        rid = str(rec.get("id"))
        url = str(rec.get("url") or "")
        notes = str(rec.get("notes") or "").lower()
        locator = str(rec.get("locator") or "")
        if rec.get("status") == "verified" and not url:
            fails.append(f"sourcing: {rid} is verified but carries no url")
        if rec.get("source_tier") in ("T1", "T2") and not locator.strip():
            fails.append(f"sourcing: {rid} is {rec.get('source_tier')} but carries no locator")
        if any(host in url for host in VENDOR_HOSTS):
            continue
        if any(host in url for host in MIRROR_HOSTS):
            mirrors.append(rid)
            if "mirror" not in notes:
                fails.append(
                    f"sourcing: {rid} cites a third-party mirror without saying so in notes"
                )
        if re.search(r"routify|file-proxy|\.aliyuncs\.com", url):
            fails.append(f"sourcing: {rid} cites a fetch proxy rather than a real document host")
    return mirrors


def check_traceability(recs: list[dict[str, Any]], fails: list[str]) -> int:
    """Every number in a verified value must be printed, or derived in the open.

    A record whose locator declares an arithmetic clause is exempt from the printed test,
    because the clause is its derivation. That exemption is only as good as check
    _arithmetic, which recomputes every such clause and fails the run when one lies.
    """
    derived_count = 0
    for rec in recs:
        rid = str(rec.get("id"))
        if rec.get("status") != "verified":
            continue
        clause = arithmetic_clause(rec.get("locator"))
        if clause:
            derived_count += 1
        # doc_id counts as evidence: for a citation record the year is part of the
        # source's identity, and a bibliography entry has no prose quote to carry it.
        evidence = " ".join(str(rec.get(field) or "") for field in ("quote", "locator", "doc_id"))
        plain = evidence.replace(",", "")
        for token in numeric_tokens(rec.get("value")):
            if token in evidence or token in plain:
                continue
            if rec.get("unit") == CITATION_UNIT and re.search(r"\b(19|20)\d{2}\b", evidence):
                continue
            if clause:
                continue
            fails.append(
                f"traceability: {rid} value {token!r} appears in neither quote, locator, nor doc_id"
            )
    return derived_count


def check_arithmetic(recs: list[dict[str, Any]], fails: list[str]) -> int:
    """Recompute every declared arithmetic clause, statement by statement."""
    statements = 0
    for rec in recs:
        rid = str(rec.get("id"))
        clause = arithmetic_clause(rec.get("locator"))
        if not clause:
            continue
        for fragment in clause.split(";"):
            piece = fragment.strip()
            if not piece:
                continue
            statements += 1
            if COMPARISON.match(piece):
                if evaluate(piece) is not True:
                    fails.append(
                        f"arithmetic: {rid} states a comparison that does not hold: {piece!r}"
                    )
                continue
            equation = EQUATION.match(piece)
            if equation is None:
                fails.append(
                    f"arithmetic: {rid} declares a clause that is neither an equation nor a "
                    f"comparison: {piece!r}"
                )
                continue
            lhs = evaluate(equation.group("lhs"))
            rhs_numbers = [
                float(n.replace(",", "")) for n in NUMBER_TEXT.findall(equation.group("rhs"))
            ]
            if lhs is None or not rhs_numbers:
                fails.append(f"arithmetic: {rid} clause cannot be evaluated: {piece!r}")
                continue
            if isinstance(lhs, bool):
                fails.append(
                    f"arithmetic: {rid} left side of an equation is a comparison: {piece!r}"
                )
                continue
            rhs = rhs_numbers[-1]
            if abs(lhs - rhs) > tolerance(rhs):
                fails.append(
                    f"arithmetic: {rid} clause does not compute: {piece!r} left side is {lhs}, "
                    f"right side claims {rhs}"
                )
    return statements


def check_readme(recs: list[dict[str, Any]], fails: list[str]) -> None:
    """The README summary must agree with the JSON it describes."""
    path = EVIDENCE_DIR / "README.md"
    if not path.exists():
        fails.append("consistency: docs/verification/README.md is missing")
        return
    text = path.read_text(encoding="utf-8")
    counts: Counter[str] = Counter(str(r.get("status")) for r in recs)
    wanted = {
        "Total Records": len(recs),
        "Verified": counts["verified"],
        "Unresolved": counts["unresolved"],
        "Conflict (records in `status: conflict`)": counts["conflict"],
    }
    for label, actual in wanted.items():
        match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(\d+)", text)
        if match is None:
            fails.append(f"consistency: README has no count labelled {label!r}")
        elif int(match.group(1)) != actual:
            fails.append(f"consistency: README {label!r} says {match.group(1)}, JSON says {actual}")


def check_headings(recs: list[dict[str, Any]], fails: list[str]) -> None:
    """Each record has exactly one heading somewhere, and no heading is orphaned."""
    on_disk: list[str] = []
    for rec_file in sorted(EVIDENCE_DIR.glob("0*.md")):
        on_disk += re.findall(
            r"^### (V-\d+-\d+)", rec_file.read_text(encoding="utf-8"), re.MULTILINE
        )
    in_json = [str(r.get("id")) for r in recs]
    for orphan in sorted(set(on_disk) - set(in_json)):
        fails.append(f"consistency: heading {orphan} has no record in claims.json")
    for absent in sorted(set(in_json) - set(on_disk)):
        fails.append(f"consistency: record {absent} has no heading in any markdown file")
    for dup, how_many in sorted(Counter(on_disk).items()):
        if how_many > 1:
            fails.append(f"consistency: heading {dup} appears {how_many} times")


def check_units(recs: list[dict[str, Any]], fails: list[str]) -> int:
    """Every record's unit must be a registered term, and the registry must not lie.

    The first rule is the one Issue #25 exists for. Until now the unit field was free text
    that no check read, so a wrong label sitting beside right arithmetic passed every gate
    in the repository; relabelling V-01-13 from GB/s to banana changed nothing. The rest of
    the function keeps the vocabulary itself honest, because a registry that drifts from the
    data is a second unsourced list rather than a fix: canonicals need kinds, kinds need to
    be one of the two named values, no canonical may fold a bit term together with a byte
    term, and no term may stay registered once the last record using it is gone.

    Returns the number of canonical terms actually in use.
    """
    used: set[str] = set()
    seen: set[str] = set()
    for rec in recs:
        rid = str(rec.get("id"))
        unit = str(rec.get("unit") or "")
        seen.add(unit)
        canonical = unit_canonical(unit)
        if canonical is None:
            lookalikes = sorted(u for u in UNIT_TERMS if u.lower() == unit.lower())
            hint = f"; this name is registered as {lookalikes}" if lookalikes else ""
            fails.append(
                f"units: {rid} carries the unregistered unit {unit!r}{hint} -- add it to "
                f"claims_lib.UNIT_TERMS with a canonical and a kind, or correct the record"
            )
            continue
        used.add(canonical)
    for spelling, canonical in sorted(UNIT_TERMS.items()):
        if canonical not in UNIT_KINDS:
            fails.append(
                f"units: {spelling!r} folds to {canonical!r}, which has no kind -- a term whose"
                f" dimension is unstated cannot be compared against anything, which is the gap"
                f" this check exists to close"
            )
    for canonical in sorted(UNIT_KINDS):
        kind = UNIT_KINDS[canonical]
        if kind not in ("dimension", "descriptor"):
            fails.append(
                f"units: canonical {canonical!r} has kind {kind!r}, which is neither "
                f"dimension nor descriptor"
            )
        spellings = spellings_for(canonical)
        if not spellings:
            fails.append(
                f"units: canonical {canonical!r} is registered but no spelling folds to it"
            )
            continue
        sides = {s for s in (memory_side(u) for u in spellings) if s is not None}
        if len(sides) > 1:
            fails.append(
                f"units: canonical {canonical!r} folds the spellings {spellings} together "
                f"across {sorted(sides)} -- bits and bytes are a factor of eight apart and "
                f"may not share a term"
            )
    for spelling in sorted(UNIT_TERMS):
        if spelling not in seen:
            fails.append(
                f"units: {spelling!r} is registered but no record uses it -- a term nobody "
                f"depends on cannot be checked, and it lets a future wrong label pass"
            )
    return len(used)


def main() -> int:
    """Run every check and report."""
    if not CLAIMS_PATH.exists():
        print(f"FAIL: {CLAIMS_PATH} not found", file=sys.stderr)
        return 1
    recs = records(load_claims())
    fails: list[str] = []

    check_structure(recs, fails)
    mirrors = check_sourcing(recs, fails)
    derived = check_traceability(recs, fails)
    statements = check_arithmetic(recs, fails)
    unit_terms = check_units(recs, fails)
    check_readme(recs, fails)
    check_headings(recs, fails)

    statuses: Counter[str] = Counter(str(r.get("status")) for r in recs)
    tiers: Counter[str] = Counter(str(r.get("source_tier")) for r in recs)
    print(
        f"records                 {len(recs)}  ("
        + ", ".join(f"{statuses.get(status, 0)} {status}" for status in STATUSES)
        + ")"
    )
    print(
        "source tiers            "
        + ", ".join(f"{tiers.get(tier, 0)} {tier}" for tier in TIERS if tiers.get(tier))
    )
    print(f"third-party mirrors     {len(mirrors)}")
    print(f"declared arithmetic     {derived} records, {statements} statements recomputed")
    print(
        f"unit vocabulary         {len(UNIT_TERMS)} spellings, " + f"{unit_terms} canonicals in use"
    )
    if fails:
        print(f"\nFAIL: {len(fails)} problem(s)", file=sys.stderr)
        for line in fails:
            print(f"  {line}", file=sys.stderr)
        return 1
    print("\nPASS: evidence set is internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
