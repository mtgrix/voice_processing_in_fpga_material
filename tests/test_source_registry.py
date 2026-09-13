"""The join between the evidence set and the source registry, and what an exempt doc_id may claim.

docs/source_index.json and docs/verification/claims.json were until Issue #20 two disjoint
identifier spaces: 41 free-text `doc_id` values on one side, five `R01-NN` ids on the other, and
nothing recording which side a citation belonged to. The reconciliation made the relation explicit
-- every registry entry now lists the doc_id labels it answers -- and put its derivation in exactly
one place, scripts/verification/build_source_index.py.

These tests are a second reader of that one derivation rather than a second derivation of it. They
call the generator and assert its verdict is clean, which is what earns them a place here: a record
citing a new document fails at `pytest tests/test_source_registry.py` with a file name attached,
instead of only inside a full gate run.

The exemption tests matter more than the coverage tests. A record whose `doc_id` is 'n/a' is opting
itself out of the registry, so an exemption is a way to become uncheckable. What keeps it honest is
that only a record with no value to source may claim it, and that is pinned here family by family
and record by record -- so a tenth exempt record means editing a set below, in a diff, on purpose.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
VERIFICATION = ROOT / "scripts" / "verification"

# build_source_index imports claims_lib by module name, so the directory has to be importable
# before it runs. The script arranges that for itself at run time; a test importing it by name has
# to do the same first.
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))

import build_source_index as registry  # noqa: E402
from claims_lib import (  # noqa: E402
    CLAIMS_PATH,
    EXACT_EXEMPT,
    EXEMPT_PREFIXES,
    is_exempt,
    load_claims,
    records,
)

DOC = load_claims(CLAIMS_PATH)
RECORDS: list[dict[str, Any]] = records(DOC)
ON_DISK = registry.INDEX_PATH.read_text(encoding="utf-8")
COMMITTED: dict[str, Any] = json.loads(ON_DISK)
SOURCES: list[dict[str, Any]] = COMMITTED["sources"]
REPORT = registry.render(DOC)

#: The ten records that cite no document, split by the reason each one gives. Counted on
#: docs/verification/claims.json at version 1.8.0, 2026-09-14, after Issue #47. There were
#: nine at 1.7.0; the tenth is V-05-57, whose three quantities no publisher prints, so it joins
#: the searched-and-found-nothing family rather than the no-value-ones.
DERIVATION_RECORDS = {"V-01-13", "V-02-36", "V-04-09", "V-04-12", "V-07-02", "V-07-03"}
NO_VALUE_RECORDS = {"V-02-28", "V-07-05"}
SEARCHED_EMPTY_RECORDS = {"V-04-13", "V-05-57"}

#: Legacy entries that were checked and found uncited. An empty doc_ids list here means "no record
#: uses this document", which is a finding. A missing doc_ids key would mean nobody looked, and the
#: generator writes the key for every row precisely so those two states read differently.
UNCITED_LEGACY_ENTRIES = {"R01-01", "R01-03"}


def registered_labels() -> set[str]:
    """Every doc_id label some registry entry claims to answer."""
    return {str(label) for src in SOURCES for label in src["doc_ids"]}


def cited_labels() -> set[str]:
    """Every doc_id label some record actually uses."""
    return {str(rec.get("doc_id", "")) for rec in RECORDS}


class TestCoverage:
    """Every citation resolves, and every registered label is actually cited."""

    def test_no_cited_document_is_unregistered(self) -> None:
        assert REPORT.unmapped == [], f"documents cited but never registered: {REPORT.unmapped}"

    def test_no_registry_entry_answers_an_unused_label(self) -> None:
        assert REPORT.stale == [], f"registry answers labels no record uses: {REPORT.stale}"

    def test_no_url_source_holds_only_unresolved_claims(self) -> None:
        assert REPORT.no_url == [], f"unlocatable sources holding up claims: {REPORT.no_url}"

    def test_one_entry_per_label(self) -> None:
        owners: dict[str, list[str]] = {}
        for src in SOURCES:
            for label in src["doc_ids"]:
                owners.setdefault(str(label), []).append(str(src["id"]))
        doubled = {label: ids for label, ids in owners.items() if len(ids) > 1}
        assert not doubled, f"a doc_id naming two documents cannot resolve to one: {doubled}"

    def test_committed_registry_is_the_rendering(self) -> None:
        assert registry.serialise(REPORT.document) == ON_DISK, (
            "docs/source_index.json was edited by hand; run make render-registry"
        )

    def test_uncited_entries_are_the_known_ones(self) -> None:
        empty = {str(src["id"]) for src in SOURCES if not src["doc_ids"]}
        assert empty == UNCITED_LEGACY_ENTRIES, f"the set of uncited entries changed: {empty}"
        for src in SOURCES:
            if str(src["id"]).startswith("S"):
                assert src["doc_ids"], f"{src['id']} is registered and answers nothing"

    def test_label_sets_match_the_derivation(self) -> None:
        assert registered_labels() == cited_labels() - {
            label for label in cited_labels() if is_exempt(label)
        }


class TestExemption:
    """The exempt labels stay few, and stay attached to records that need no source."""

    def test_exempt_label_count_is_pinned(self) -> None:
        assert REPORT.exempt == 8, f"the registry now has {REPORT.exempt} exempt labels, not 8"

    def test_families_are_the_three_described(self) -> None:
        derived = {
            str(rec["id"])
            for rec in RECORDS
            if str(rec.get("doc_id", "")).startswith(EXEMPT_PREFIXES)
        }
        exact = {str(rec["id"]) for rec in RECORDS if str(rec.get("doc_id")) in EXACT_EXEMPT}
        assert derived == DERIVATION_RECORDS
        assert exact == NO_VALUE_RECORDS | SEARCHED_EMPTY_RECORDS

    def test_patterns_do_not_overlap(self) -> None:
        for label in EXACT_EXEMPT:
            assert not label.startswith(EXEMPT_PREFIXES), f"{label!r} matches two rules at once"

    def test_derivation_records_assert_a_value_and_name_their_inputs(self) -> None:
        for rec in RECORDS:
            doc_id = str(rec.get("doc_id", ""))
            if not doc_id.startswith(EXEMPT_PREFIXES):
                continue
            assert str(rec["status"]) == "verified", f"{rec['id']} derives a value it never reached"
            assert str(rec.get("value", "")).strip(), f"{rec['id']} derives nothing at all"
            assert doc_id.removeprefix(EXEMPT_PREFIXES[0]).strip(), (
                f"{rec['id']} is derived from an unnamed input"
            )

    def test_absence_records_carry_no_value(self) -> None:
        for rec in RECORDS:
            if str(rec.get("doc_id")) not in EXACT_EXEMPT:
                continue
            assert str(rec["status"]) == "unresolved", (
                f"{rec['id']} reports an absence and still resolves to {rec['status']!r}"
            )
            assert not str(rec.get("value", "")).strip(), (
                f"{rec['id']} states a value and cites no document for it"
            )

    def test_is_exempt_agrees_with_the_families(self) -> None:
        for label in cited_labels():
            expected = label.startswith(EXEMPT_PREFIXES) or label in EXACT_EXEMPT
            assert is_exempt(label) is expected, f"{label!r} matches no exemption rule"
        assert not registered_labels() & {label for label in cited_labels() if is_exempt(label)}, (
            "an exempt label gained a registry entry, which turns an absence into a source"
        )


class TestNoRecordDodges:
    """Nothing carrying a number may step outside the registry by choosing a particular string."""

    def test_bad_exempt_is_empty(self) -> None:
        assert REPORT.bad_exempt == [], (
            f"exempt labels contradicting their own records: {REPORT.bad_exempt}"
        )

    def test_value_bearing_records_are_registered_or_derived(self) -> None:
        registered = registered_labels()
        for rec in RECORDS:
            if not str(rec.get("value", "")).strip():
                continue
            doc_id = str(rec.get("doc_id", ""))
            assert doc_id in registered or doc_id.startswith(EXEMPT_PREFIXES), (
                f"{rec['id']} states {rec['value']!r} and cites no registered document"
            )
