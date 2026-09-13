"""Per-row correspondence between a claimed result and its raw log (Issue #18).

The rule this repository already specifies, at plan-v2 section 9.2 item 5: no row may
carry the done marker unless results/ holds a matching raw log with a checksum. The rule
the gate used to implement is narrower in two ways at once -- it asked whether results/
was empty as a whole, so one unrelated file vouched for every claim, and it only looked
at rows beginning with a bold id.

Neither flaw was observable, because no row in either status table carries a checkmark:
the only one in the repository sits in the legend line that defines the symbol. So the
gate has never had anything to check, and these tests supply the rows it will one day
have to refuse. They load the real script rather than restating its rules -- see
tests/test_repo_integrity.py, which copies the forbidden-marker list and can therefore
only ever prove the copy agrees with itself.

ASCII throughout, markers spelled as \\N{...} escapes: a checkmark in a fixture must never
be the reason a lint step goes red.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

NL = chr(10)
CHECK = "\N{WHITE HEAVY CHECK MARK}"
PENDING = "\N{CONSTRUCTION SIGN}"

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify_integrity.py"
STATUS_DOC = "docs/EXPERIMENT_STATUS.md"
BOOK_DOC = "docs/BOOK_STATUS.md"


def load_gate(name: str) -> ModuleType:
    """The real scripts/verify_integrity.py, as a fresh module object."""
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Gate pointed at a scratch tree, so ROOT is the only thing a test controls."""
    module = load_gate("verify_integrity_under_test")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    return module


@pytest.fixture
def real_gate() -> ModuleType:
    """Gate pointed at the repository, to record what is true today.

    exec_module does not register the module in sys.modules, which is why this cannot be
    obtained by reloading the scratch fixture above.
    """
    return load_gate("verify_integrity_of_real_repo")


def write_status(tmp_path: Path, rows: list[str]) -> None:
    """Write the experiment table under test, plus a chapter table claiming nothing.

    The gate visits docs/BOOK_STATUS.md too and reports an absent file as an error, so a
    scratch tree that omits it fails for the wrong reason: the assertion below would then
    be evidence about the fixture rather than about the gate.
    """
    doc = tmp_path / STATUS_DOC
    doc.parent.mkdir(parents=True, exist_ok=True)
    header = ["| Ma Thi nghiem | Chuyen | Ten | Trang thai |", "|:---:|:---:|---|:---:|"]
    doc.write_text(NL.join(header + rows) + NL, encoding="utf-8")
    book = ["| Chuyen | Ten | Trang thai |", "|:---:|---|:---:|"]
    book += ["| **01** | Pipeline | drafting |", "| **02** | Profiling | drafting |"]
    (tmp_path / BOOK_DOC).write_text(NL.join(book) + NL, encoding="utf-8")


def make_log(tmp_path: Path, name: str, body: str = "raw counters" + NL) -> Path:
    """Create a log under results/, accepting a slash-separated relative layout."""
    log = tmp_path.joinpath("results", *name.split("/"))
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(body, encoding="utf-8")
    return log


def write_manifest(tmp_path: Path, *logs: Path) -> Path:
    """results/SHA256SUMS, in the format sha256sum itself emits."""
    lines = []
    for log in logs:
        digest = hashlib.sha256(log.read_bytes()).hexdigest()
        lines.append(f"{digest}  {log.relative_to(tmp_path).as_posix()}")
    manifest = tmp_path / "results" / "SHA256SUMS"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(NL.join(lines) + NL, encoding="utf-8")
    return manifest


ROW_01 = f"| **exp_01** | 01 | streaming_audio_pipeline | {CHECK} |"
ROW_01_DOING = f"| **exp_01** | 01 | streaming_audio_pipeline | {PENDING} |"
ROW_03_PLAIN = f"| exp_03 | 03 | batch_one_gpu_bottleneck | {CHECK} |"


class TestNothingClaimedIsQuiet:
    """A promise is not a measurement. Unfinished rows must never be blocked on."""

    def test_pending_row_needs_no_log(self, gate: ModuleType, tmp_path: Path) -> None:
        write_status(tmp_path, [ROW_01_DOING])
        assert gate.check_result_markers_have_logs() == []

    def test_missing_status_document_fails_rather_than_passes(
        self, gate: ModuleType, tmp_path: Path
    ) -> None:
        """A status table that vanished must not read as nothing to check."""
        (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
        assert gate.check_result_markers_have_logs() != []


class TestCorrespondenceIsPerRow:
    def test_claimed_row_with_no_logs_fails(self, gate: ModuleType, tmp_path: Path) -> None:
        write_status(tmp_path, [ROW_01])
        errors = gate.check_result_markers_have_logs()
        assert errors, "a row claiming a finished result with no log must be an error"

    def test_an_unrelated_log_does_not_vouch_for_a_claimed_row(
        self, gate: ModuleType, tmp_path: Path
    ) -> None:
        """The regression Issue #18 is about.

        exp_01 claims a result while the only file in results/ belongs to exp_02. A test
        for directory emptiness sees a non-empty directory and stays silent.
        """
        write_status(tmp_path, [ROW_01])
        make_log(tmp_path, "exp_02_run.json")
        errors = gate.check_result_markers_have_logs()
        assert errors, "a log for a different row must not vouch for this one"
        assert any("exp_01" in e for e in errors), errors

    def test_claim_outside_the_bold_id_shape_is_still_read(
        self, gate: ModuleType, tmp_path: Path
    ) -> None:
        """The point of the marker is the claim it carries, not whether the id is bold."""
        write_status(tmp_path, [ROW_03_PLAIN])
        errors = gate.check_result_markers_have_logs()
        assert errors and any("exp_03" in e for e in errors), errors

    def test_timestamped_layout_from_plan_matches_its_row(
        self, gate: ModuleType, tmp_path: Path
    ) -> None:
        """plan-v2 fixes the layout as results/expNN/<timestamp>/, while rows read exp_NN.

        A gate requiring the row id verbatim would reject the layout its own plan
        prescribes, which is how a correct log ends up looking like a missing one.
        """
        write_status(tmp_path, [ROW_01])
        log = make_log(tmp_path, "exp01/20260913T020000Z/run.json")
        write_manifest(tmp_path, log)
        assert gate.check_result_markers_have_logs() == []


class TestChecksumBinding:
    def test_matching_log_and_digest_pass(self, gate: ModuleType, tmp_path: Path) -> None:
        write_status(tmp_path, [ROW_01])
        log = make_log(tmp_path, "exp_01_run.json")
        write_manifest(tmp_path, log)
        assert gate.check_result_markers_have_logs() == []

    def test_log_absent_from_manifest_fails(self, gate: ModuleType, tmp_path: Path) -> None:
        write_status(tmp_path, [ROW_01])
        make_log(tmp_path, "exp_01_run.json")
        errors = gate.check_result_markers_have_logs()
        assert errors and any("SHA256SUMS" in e for e in errors), errors

    def test_log_edited_after_checksum_fails(self, gate: ModuleType, tmp_path: Path) -> None:
        """Silently revising a captured log is the failure a checksum exists to catch."""
        write_status(tmp_path, [ROW_01])
        log = make_log(tmp_path, "exp_01_run.json")
        write_manifest(tmp_path, log)
        log.write_text("raw counters" + NL + "regretted rounding" + NL, encoding="utf-8")
        errors = gate.check_result_markers_have_logs()
        assert errors and any("exp_01_run.json" in e for e in errors), errors

    def test_manifest_entry_for_wrong_digest_fails(self, gate: ModuleType, tmp_path: Path) -> None:
        write_status(tmp_path, [ROW_01])
        log = make_log(tmp_path, "exp_01_run.json")
        manifest = write_manifest(tmp_path, log)
        manifest.write_text("0" * 64 + "  results/exp_01_run.json" + NL, encoding="utf-8")
        assert gate.check_result_markers_have_logs() != []


class TestRealRepositoryState:
    """Two records of what is true today, so a future change cannot be silent."""

    def test_no_row_claims_a_result_yet(self, real_gate: ModuleType) -> None:
        """The gate is green because nothing has been claimed, not because all is well.

        The day a row is marked done, this stays green only if a checksummed log exists.
        If it goes red, the answer is to run the experiment, not to relax the assertion.
        """
        assert real_gate.check_result_markers_have_logs() == []

    def test_every_log_under_results_is_checksummed(self) -> None:
        """Replaces the snapshot "results/ holds nothing", which could only ever be true once.

        Chapter 1's experiment was run on 2026-09-13, so the directory is no longer empty and
        the old assertion was spent. What replaces it is permanent and stricter: every file
        under results/ must be named by SHA256SUMS. That fails on an unchecksummed log even
        while no row claims it, which the empty-directory test could never do.
        """
        log_dir = REPO_ROOT / "results"
        manifest = log_dir / "SHA256SUMS"
        assert manifest.is_file(), "results/SHA256SUMS is the index; without it no log is evidence"
        listed = {
            line.split("  ", 1)[1].strip()
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if "  " in line
        }
        present = {
            f.relative_to(REPO_ROOT).as_posix()
            for f in sorted(log_dir.rglob("*"))
            if f.is_file() and f != manifest
        }
        assert present, "results/ holds no log, so no row anywhere may carry the marker"
        unlisted = sorted(present - listed)
        assert not unlisted, f"logs with no digest recorded: {unlisted}"

    def test_marker_rows_are_exactly_the_measured_ones(self) -> None:
        """Replaces "no row carries the marker", which is now false.

        Two invariants survive it. The number of claimed rows equals the number of rows with
        captured evidence, stated as a count rather than left to the gate. And BOOK_STATUS
        holds none at all, which turns the gate's documented limit into a test: correspondence
        is by folded substring, so a two-digit chapter id is matched by any path holding those
        digits, a timestamp among them. A checkmark in that table could be vouched for by an
        unrelated log. Mark measurements, not chapters.
        """
        exp_rows = [
            line
            for line in (REPO_ROOT / STATUS_DOC).read_text(encoding="utf-8").splitlines()
            if CHECK in line and line.lstrip().startswith("|")
        ]
        book_rows = [
            line
            for line in (REPO_ROOT / BOOK_DOC).read_text(encoding="utf-8").splitlines()
            if CHECK in line and line.lstrip().startswith("|")
        ]
        assert not book_rows, f"BOOK_STATUS rows carry the marker: {book_rows}"
        assert len(exp_rows) == 1, f"expected exactly one claimed experiment row, got {exp_rows}"
        assert "exp_01" in exp_rows[0]
