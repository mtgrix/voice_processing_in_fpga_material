"""The accepted-unit vocabulary, and what it refuses (Issue #25).

The evidence set has always carried a `unit` field, and the auditor has always read it
exactly once -- at the exemption that lets a citation record carry a year in `doc_id`
instead of a quote. Nothing anywhere asked whether a spelling meant anything, so
relabelling V-01-13 from `GB/s` to `banana` leaves every gate green: the arithmetic still
recomputes, because no check compares the label to a thing.

These tests load the real modules rather than restating their rules, and they assert both
directions -- the vocabulary must accept all 53 spellings the evidence set now uses,
and it must refuse one it has never seen. A registry that only ever accepts is a list.

The interesting refusal is the one a normaliser would have caused. Folding case turns
`sparse INT8 TOPS` and `Sparse INT8 TOPS` into one term, which is right, and turns `Kb`
(kilobits, V-01-11) and `KB` (kilobytes, V-01-17) into one term, which is a factor of
eight. So the guard is tested by mutating the table to fold them and demanding that the
audit say so.

ASCII throughout: a non-ASCII byte here would be a lint failure, not evidence.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parent.parent
VERIFICATION = ROOT / "scripts" / "verification"

# audit_claims imports claims_lib by module name, so the directory must be importable
# before either file is executed. The script arranges that for itself at run time; a test
# loading it by path has to do the same first.
if str(VERIFICATION) not in sys.path:
    sys.path.insert(0, str(VERIFICATION))


def load_module(name: str, path: Path) -> ModuleType:
    """A real script, as a module object, by path."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load_module("audit_claims_under_test", VERIFICATION / "audit_claims.py")
# Loading claims_lib a second time by path would hand this test a vocabulary to mutate
# that the gate never reads: audit_claims does `from claims_lib import ...`, which binds
# the module registered under its own name. Taking it from sys.modules is the only way to
# be certain the dict under test is the dict under audit.
claims_lib = sys.modules["claims_lib"]


def record(rid: str, unit: str) -> dict[str, str]:
    """The two fields check_units reads. The rest are the other checks' business."""
    return {"id": rid, "unit": unit}


def run(recs: list[dict[str, str]]) -> tuple[int, list[str]]:
    fails: list[str] = []
    used = audit.check_units(recs, fails)
    return used, fails


def evidence_records() -> list[dict[str, str]]:
    recs: list[dict[str, str]] = [
        {"id": str(r.get("id")), "unit": str(r.get("unit") or "")}
        for r in claims_lib.records(claims_lib.load_claims())
    ]
    return recs


class TestRegistryMatchesTheEvidenceSet:
    def test_every_record_unit_is_registered(self) -> None:
        used, fails = run(evidence_records())
        assert fails == [], fails
        assert used > 0

    def test_the_observed_vocabulary_is_53_spellings(self) -> None:
        """A ratchet needs a number in it, or a future deletion reads as tidying.

        54 spellings over 53 canonicals as of 2026-09-14, when Issue #57 registered the CUDA
        execution model for chapter 3 and needed a term for it: a warp is 32 *threads*, which is
        none of the counts already in the set -- `attention heads` and `encoder blocks` count a
        network, `DLA engines` and `transceivers` count silicon. Before that, 53 over 52 from the
        same day, when Issue #47 registered the NeMo ASR recipes and the count terms they needed:
        the set carried `BRAM36 blocks` and `URAM288 blocks` for hardware cells, but no spelling
        for a block of a *network*, and no term at all for a duration in seconds, only in
        milliseconds. Before that, 46 over 45 from 2026-09-13, when V-05-10 and V-05-11 needed
        kilohertz and `MHz` is not a spelling of it. The alias pair that makes the two counts
        differ by one is still `Sparse INT8 TOPS` / `sparse INT8 TOPS`, tested below.
        """
        assert len(claims_lib.UNIT_TERMS) == 54
        assert len({c for c in claims_lib.UNIT_TERMS.values()}) == 53

    def test_every_canonical_has_a_kind(self) -> None:
        assert set(claims_lib.UNIT_TERMS.values()) <= set(claims_lib.UNIT_KINDS)

    def test_kinds_are_only_the_two_named_ones(self) -> None:
        assert set(claims_lib.UNIT_KINDS.values()) == {"dimension", "descriptor"}


class TestBitAndByteGuard:
    def test_kilobits_and_kilobytes_are_different_terms(self) -> None:
        assert claims_lib.UNIT_TERMS["Kb"] == "kilobit"
        assert claims_lib.UNIT_TERMS["KB"] == "kilobyte"

    def test_no_canonical_folds_both_sides(self) -> None:
        for canonical in set(claims_lib.UNIT_TERMS.values()):
            sides = {claims_lib.memory_side(u) for u in claims_lib.spellings_for(canonical)}
            assert len(sides - {None}) <= 1, canonical

    def test_memory_side_reads_the_case_that_carries_the_meaning(self) -> None:
        side = claims_lib.memory_side
        assert side("Kb") == "bit"
        assert side("Mb") == "bit"
        assert side("KB") == "byte"
        assert side("GB/s") == "byte"
        assert side("Watts") is None
        assert side("citation") is None

    def test_a_fold_across_the_boundary_is_refused(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The mutation a case-insensitive normaliser would have shipped silently."""
        monkeypatch.setitem(claims_lib.UNIT_TERMS, "KB", "kilobit")
        _used, fails = run(evidence_records())
        assert any("factor of eight" in f for f in fails), fails


class TestFoldingCaseIsIntentional:
    def test_the_two_sparse_tops_spellings_are_one_quantity(self) -> None:
        canonical = "sparse-int8-tops"
        assert claims_lib.UNIT_TERMS["Sparse INT8 TOPS"] == canonical
        assert claims_lib.UNIT_TERMS["sparse INT8 TOPS"] == canonical

    def test_that_alias_group_is_the_only_one(self) -> None:
        """A second deliberate alias turns this red and forces the choice to be stated."""
        groups: dict[str, list[str]] = {}
        for spelling, canonical in claims_lib.UNIT_TERMS.items():
            groups.setdefault(canonical, []).append(spelling)
        assert sorted(k for k, v in groups.items() if len(v) > 1) == ["sparse-int8-tops"]


class TestRefusals:
    def test_an_unregistered_unit_is_refused(self) -> None:
        used, fails = run([record("V-01-13", "banana")])
        assert used == 0
        assert any("unregistered unit 'banana'" in f for f in fails), fails

    def test_the_same_record_passes_with_its_registered_unit(self) -> None:
        """Same id, same helper, one honest spelling -- so the red above is about the label."""
        _used, fails = run([record("V-01-13", "GB/s"), record("V-01-11", "Kb")])
        assert [f for f in fails if "unregistered" in f] == []

    def test_a_case_variant_is_pointed_at_the_registered_spelling(self) -> None:
        _used, fails = run([record("V-01-13", "gb/s")])
        assert any("this name is registered as" in f for f in fails), fails

    def test_a_registered_term_no_record_uses_is_refused(self) -> None:
        """Otherwise the list becomes a graveyard, and a graveyard lets wrong labels pass."""
        _used, fails = run([record("V-01-13", "GB/s")])
        # One failure per unused *spelling*, not per canonical. Of the 54 spellings the
        # vocabulary now holds, GB/s accounts for the single used one, so 53 go unclaimed.
        assert len([f for f in fails if "registered but no record uses it" in f]) == 53

    def test_a_canonical_without_a_kind_is_refused(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delitem(claims_lib.UNIT_KINDS, "watts")
        _used, fails = run(evidence_records())
        assert any("which has no kind" in f for f in fails), fails

    def test_a_kind_outside_the_two_is_refused(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(claims_lib.UNIT_KINDS, "watts", "powerful")
        _used, fails = run(evidence_records())
        assert any("neither dimension nor descriptor" in f for f in fails), fails


class TestKindsAreEditorialNotMeasured:
    def test_descriptor_marks_prose_and_dimension_marks_a_measurement(self) -> None:
        assert claims_lib.unit_kind("string") == "descriptor"
        assert claims_lib.unit_kind("citation") == "descriptor"
        assert claims_lib.unit_kind("Tcl command") == "descriptor"
        assert claims_lib.unit_kind("GB/s") == "dimension"

    def test_an_unregistered_term_has_no_kind(self) -> None:
        assert claims_lib.unit_kind("banana") is None
        assert claims_lib.unit_canonical("banana") is None
