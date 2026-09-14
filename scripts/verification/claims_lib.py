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

#: Which doc_id values name no document, so they can have no registry entry.
#:
#: This lives here rather than in the script that writes the registry because three readers need
#: one answer: build_source_index.py, which must not demand an entry for them; the check beside it
#: that pins what a record using one of these labels is allowed to assert; and
#: tests/test_source_registry.py. A rule this narrow, duplicated across files, is where two halves
#: of a check start disagreeing.
#:
#: Each pattern is a statement about the evidence set, not an escape hatch. They are listed in
#: docs/verification/claims.json as of 2026-09-13, and what each one means is a fact about the
#: records that carry it:
#:
#: Measured on the evidence set as it stands, eight of its forty-one doc_id labels are exempt, and
#: they come from nine records:
#:
#:   'Derived from ...'         arithmetic. Six records, 2 through 4 labels each carrying one
#:                              record. Every one verified, and every one naming the records or
#:                              the datasheet figures it divided, multiplied or tabulated out of,
#:                              so the citations exist two fields away. A computation is not a
#:                              work somebody fetched.
#:   'n/a'                      no value yet. Two records, V-02-28 and V-07-05, both unresolved
#:                              with an empty value field. There is no document behind a question
#:                              the project has not answered.
#:   'no primary source found' searched, nothing found. One record, V-04-13, same shape. The
#:                              absence is the finding, and it is what keeps the claim at T5.
#:
#: tests/test_source_registry.py pins all nine record ids, so a tenth exempt record is a
#: deliberate edit to that list rather than a silent one.
#:
#: The three patterns are disjoint by construction, and build_source_index.py refuses to emit a
#: registry over an evidence set where an exempt label sits on a record that carries a value.
EXEMPT_PREFIXES = ("Derived from ",)
EXACT_EXEMPT = ("n/a", "no primary source found")


def is_exempt(doc_id: str) -> bool:
    """True for a doc_id that names arithmetic or an absence rather than a document."""
    return doc_id.startswith(EXEMPT_PREFIXES) or doc_id in EXACT_EXEMPT


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

#: The unit field was a vocabulary with no vocabulary list: audit_claims.py read it exactly
#: once, only to exempt citation records from the traceability test, and nothing anywhere
#: asked whether a spelling meant anything. That is how `GB/s` could be relabelled `banana`
#: and leave every gate green (Issue #25). Membership here is the fix, and it is a ratchet,
#: not a proof: this dict was generated from the 45 spellings the evidence set used on
#: 2026-09-13, so it accepts all of them by construction and refuses anything else. A record
#: that genuinely needs a new unit adds a line, and one whose last record was deleted takes
#: one away -- check_units enforces both directions so the list cannot rot into a graveyard
#: of ghosts, which is how a wrong label starts passing again.
#:
#: Two spellings share a canonical where the difference is decoration: `Sparse INT8 TOPS`
#: and `sparse INT8 TOPS` are one NVIDIA quantity written two ways (V-02-09 and V-02-32,
#: -33, -36). Where the difference is semantics, folding would itself be the defect: `KB`
#: is kilobytes (V-01-17, PS on-chip memory, 256) and `Kb` is kilobits (V-01-11, the
#: 144 x 36 + 64 x 288 sum, 23,616), eight times apart. That is why this table is explicit
#: rather than a lowercase-and-strip function, and why check_units re-derives the two sides
#: from the table on every run -- a future edit that merges a bit term with a byte term
#: fails the audit instead of quietly passing it.
UNIT_TERMS: dict[str, str] = {
    "Accuracy %": "accuracy",
    "architecture": "architecture",
    "attention heads": "attention-heads",
    "attention steps": "attention-steps",
    "Block RAM": "block-ram",
    "boolean": "boolean",
    "BRAM36 blocks": "bram36-blocks",
    "bytes": "bytes",
    "citation": "citation",
    "CLB Flip-Flops": "clb-flip-flops",
    "CLB LUTs": "clb-luts",
    "convolution taps": "convolution-taps",
    "DLA engines": "dla-engines",
    "DSP48E2 slices": "dsp48e2-slices",
    "encoder blocks": "encoder-blocks",
    "GB": "gb",
    "GB/s": "gb-s",
    "Gb/s per lane": "gb-s-per-lane",
    "hidden units": "hidden-units",
    "IEEE badges": "ieee-badges",
    "INT8 TOPS": "int8-tops",
    "Kb": "kilobit",
    "KB": "kilobyte",
    "Kb per tile": "kb-per-tile",
    "kHz": "khz",
    "license": "license",
    "Mb": "mb",
    "mel bands": "mel-bands",
    "MHz": "mhz",
    "MHz / MT/s": "mhz-mt-s",
    "milliseconds": "milliseconds",
    "mixed": "mixed",
    "multiplier": "multiplier",
    "n/a": "n-a",
    "OP/byte": "op-byte",
    "operator": "operator",
    "parameters": "parameters",
    "percent": "percent",
    "ports": "ports",
    "resources": "resources",
    "seconds": "seconds",
    "Sparse INT8 TOPS": "sparse-int8-tops",
    "sparse INT8 TOPS": "sparse-int8-tops",
    "speed grade / Volts": "speed-grade-volts",
    "string": "string",
    "table": "table",
    "Tcl command": "tcl-command",
    "threads per warp": "threads-per-warp",
    "transceivers": "transceivers",
    "UltraRAM": "ultraram",
    "URAM288 blocks": "uram288-blocks",
    "V": "v",
    "Watts": "watts",
    "WER %": "wer",
}

#: What each canonical names. `descriptor` marks a record whose value is not a measurement
#: of anything at all -- a licence string, a boolean, a Tcl command, a set of badge names --
#: and `dimension` marks one that is. This split is editorial, not derived: it was assigned
#: by reading the values beside each canonical, and today it gates nothing except its own
#: internal consistency. Do not read `descriptor` as a claim that a record is soft, or
#: `dimension` as a claim that its value is parseable: 39 of the 64 dimensional records
#: carry prose values, and V-01-22 reads
#: `23,616 Kb = 2,952 KiB = 3,022,848 B = 2.8828 MiB = 3.02 MB decimal`.
UNIT_KINDS: dict[str, str] = {
    "accuracy": "dimension",
    "architecture": "descriptor",
    "attention-heads": "dimension",
    "attention-steps": "dimension",
    "block-ram": "dimension",
    "boolean": "descriptor",
    "bram36-blocks": "dimension",
    "bytes": "dimension",
    "citation": "descriptor",
    "clb-flip-flops": "dimension",
    "clb-luts": "dimension",
    "convolution-taps": "dimension",
    "dla-engines": "dimension",
    "dsp48e2-slices": "dimension",
    "encoder-blocks": "dimension",
    "gb": "dimension",
    "gb-s": "dimension",
    "gb-s-per-lane": "dimension",
    "hidden-units": "dimension",
    "ieee-badges": "descriptor",
    "int8-tops": "dimension",
    "kb-per-tile": "dimension",
    "khz": "dimension",
    "kilobit": "dimension",
    "kilobyte": "dimension",
    "license": "descriptor",
    "mb": "dimension",
    "mel-bands": "dimension",
    "mhz": "dimension",
    "mhz-mt-s": "dimension",
    "milliseconds": "dimension",
    "mixed": "descriptor",
    "multiplier": "dimension",
    "n-a": "descriptor",
    "op-byte": "dimension",
    "operator": "descriptor",
    "parameters": "dimension",
    "percent": "dimension",
    "ports": "dimension",
    "resources": "dimension",
    "seconds": "dimension",
    "sparse-int8-tops": "dimension",
    "speed-grade-volts": "dimension",
    "string": "descriptor",
    "table": "descriptor",
    "tcl-command": "descriptor",
    "threads-per-warp": "dimension",
    "transceivers": "dimension",
    "ultraram": "dimension",
    "uram288-blocks": "dimension",
    "v": "dimension",
    "watts": "dimension",
    "wer": "dimension",
}

_MEMORY_SYMBOL = re.compile(r"(?<![A-Za-z])[KMG]i?([Bb])(?![A-Za-z])")


def memory_side(term: str) -> str | None:
    """`bit`, `byte`, or None for a term that names no storage quantity.

    A single lower-case b against B is a factor of eight. It is the one distinction in the
    unit vocabulary that is not a style choice, so it gets a function of its own that both
    the registry generator and the audit can call.
    """
    match = _MEMORY_SYMBOL.search(term)
    if match is None:
        return None
    return "bit" if match.group(1) == "b" else "byte"


def unit_canonical(term: str) -> str | None:
    """The registered canonical for a spelling, or None when it is unregistered."""
    return UNIT_TERMS.get(term)


def unit_kind(term: str) -> str | None:
    """`dimension` or `descriptor` for a registered spelling; None when unregistered."""
    canonical = UNIT_TERMS.get(term)
    return None if canonical is None else UNIT_KINDS.get(canonical)


def spellings_for(canonical: str) -> list[str]:
    """Every registered spelling that folds to one canonical, sorted."""
    return sorted(u for u, c in UNIT_TERMS.items() if c == canonical)


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
