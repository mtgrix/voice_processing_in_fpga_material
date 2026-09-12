"""Shared loading and field definitions for the docs/verification evidence set.

The evidence set has one machine-readable source of truth, docs/verification/claims.json.
The per-topic markdown files beside it are generated from it. These helpers exist so that
the auditor and the renderer cannot disagree about what a record is supposed to look like.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs" / "verification"
CLAIMS_PATH = EVIDENCE_DIR / "claims.json"

#: Fields every record must carry, in the order the renderer prints them. `id` is the
#: twelfth plus one: it is the record key, and it leads each rendered block.
RECORD_FIELDS: tuple[str, ...] = (
    "status",
    "quantity",
    "value",
    "unit",
    "conditions",
    "source_tier",
    "doc_id",
    "title",
    "url",
    "locator",
    "quote",
    "retrieved_utc",
    "access",
    "corroborating_url",
    "notes",
)

STATUSES = ("verified", "unresolved", "conflict")
TIERS = ("T1", "T2", "T3", "T4", "T5")

#: Matches a declared arithmetic clause in a locator, e.g.
#: "p.22 Table 23; arithmetic: 144 * 36 Kb + 64 * 288 Kb = 23,616 Kb".
#: The colon is required so that prose titles containing the word arithmetic, such as
#: Jacob et al. section 2.2 "Integer-arithmetic-only matrix multiplication", are not
#: mistaken for a declaration.
ARITHMETIC_MARKER = re.compile(r"\barithmetic(?:\s+derivation)?:\s*(?P<body>.+)$", re.IGNORECASE)

#: A number with optional thousands separators or decimal point.
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")

#: Words that make a value numeric-looking without being a measured quantity.
CITATION_UNIT = "citation"


def load_claims(path: Path | None = None) -> dict[str, Any]:
    """Read claims.json and return the parsed document."""
    target = path or CLAIMS_PATH
    doc: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
    return doc


def records(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the record list from a parsed claims document."""
    recs: list[dict[str, Any]] = doc["records"]
    return recs


def numeric_tokens(value: Any) -> set[str]:
    """Every number appearing in a value, normalised so 23,616 and 23616 compare equal.

    Tokens shorter than two characters are dropped: a lone "2" matches inside almost any
    sentence, so requiring it would make the traceability test meaningless.
    """
    out: set[str] = set()
    for raw in NUMBER.findall(str(value if value is not None else "")):
        stripped = raw.strip(".,")
        if not stripped:
            continue
        normalised = stripped.replace(",", "")
        out.add(normalised)
        out.add(stripped)
    return {t for t in out if len(t) >= 2}


def arithmetic_clause(locator: Any) -> str | None:
    """Return the text of a declared arithmetic clause, or None if the locator has none."""
    match = ARITHMETIC_MARKER.search(str(locator or ""))
    return match.group("body") if match else None


def file_of(record_id: str) -> str:
    """The two-digit file group a record belongs to, taken from its id."""
    return record_id.split("-")[1]


def parse_record_id(record_id: str) -> tuple[str, int]:
    """Split "V-01-11" into ("V-01", 11). Raises ValueError when an id is malformed."""
    parts = record_id.split("-")
    if len(parts) != 3 or parts[0] != "V" or not parts[2].isdigit():
        msg = f"malformed record id {record_id!r}, expected V-<file>-<seq>"
        raise ValueError(msg)
    return f"{parts[0]}-{parts[1]}", int(parts[2])
