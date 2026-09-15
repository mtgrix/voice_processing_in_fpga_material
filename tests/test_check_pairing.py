"""The pairing reviewer has to rattle on a mis-attribution, not just sit quiet on good prose.

Issue #56 records the two defects this tool was written for and check_pairing caught during
assembly while every other gate passed them: a draft that cited a record its own sentence did not
use, and a paragraph that attributed a 14-million-parameter count to a record whose value is a
word-error rate. Both are the MISM class -- a number standing beside a citation that does not
carry it. A reviewer whose hard findings have been tuned down to zero on the real manuscript is
only trustworthy if the zero is measured against prose that really is clean, so this file
manufactures each defect in isolation and asserts the tool says FAIL about the right number on the
right line, and then asserts the exemptions (baseline debt, section-wide citations, comments, axis
ticks, declared derivations) excuse their shape and nothing wider.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "verification"))
import check_pairing as cp  # noqa: E402


def registry(*pairs: tuple[str, str, str]) -> dict[str, dict[str, Any]]:
    """A record set keyed by id: (id, quantity, value)."""
    return {cid: {"id": cid, "quantity": q, "value": v, "unit": ""} for cid, q, v in pairs}


def grade(
    tmp_path: Path, text: str, by: dict[str, dict[str, Any]], excused: set[Any] | None = None
) -> tuple[int, int, list[str]]:
    """Run one manuscript through grade_file, returning (hard, notes, finding lines)."""
    path = tmp_path / "chapter08.md"
    path.write_text(text, encoding="utf-8")
    strong, weak = cp.field_forms(by)
    lines: list[str] = []

    class Capture:
        def __init__(self) -> None:
            self.stdout = sys.stdout

        def write(self, s: str) -> None:
            lines.extend(ln for ln in s.split("\n") if ln.startswith("  "))

        def flush(self) -> None:
            pass

    saved = sys.stdout
    sys.stdout = Capture()
    try:
        hard, notes, _ = cp.grade_file(path, by, strong, weak, excused or set())
    finally:
        sys.stdout = saved
    return hard, notes, lines


def test_misattributed_number_is_a_hard_mism(tmp_path: Path) -> None:
    """The #56 defect itself: a parameter count printed beside a WER record."""
    by = registry(
        ("V-05-01", "wer_percent", "4.9"),
        ("V-05-02", "parameter_count", "14 million"),
    )
    text = "## 8.1 Section\n\nThe model ships at `V-05-01` and holds 14 million parameters.\n"
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 1
    assert any("MISM" in ln and "14" in ln for ln in lines)


def test_correct_attribution_is_quiet(tmp_path: Path) -> None:
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = "## 8.1 Section\n\nThe model scores 4.9 per cent error (`V-05-01`).\n"
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 0


def test_citation_of_a_nonexistent_record_is_hard(tmp_path: Path) -> None:
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = "## 8.1 Section\n\nAs `V-99-99` prints, the margin is 4.9 per cent.\n"
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 1
    assert any("FAIL" in ln and "V-99-99" in ln for ln in lines)


def test_uncited_unsourced_number_is_a_hard_orphan(tmp_path: Path) -> None:
    """Invention is scan_numbers' claim, but a number no record anywhere carries stays hard here."""
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = "## 8.1 Section\n\nThe queue depth is 73 frames.\n"
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 1
    assert any("orphan" in ln and "73" in ln for ln in lines)


def test_section_wide_citation_softens_drift_not_invention(tmp_path: Path) -> None:
    """A number a section cites elsewhere softens to a note; one carried nowhere is hard."""
    by = registry(
        ("V-05-01", "wer_percent", "4.9"),
        ("V-05-02", "frame_ms", "40"),
    )
    drifted = (
        "## 8.1 Section\n\nThe hop is 40 ms (`V-05-02`).\n\n"
        "Later prose says the hop is 40 ms without repeating the id.\n"
    )
    hard, notes, lines = grade(tmp_path, drifted, by)
    assert hard == 0
    assert any("note" in ln and "40" in ln for ln in lines)

    invented = "## 8.1 Section\n\nThe hop is 40 ms (`V-05-02`).\n\nNothing here says 77.\n"
    hard, notes, lines = grade(tmp_path, invented, by)
    assert hard == 1
    assert any("orphan" in ln and "77" in ln for ln in lines)


def test_baseline_debt_is_excused(tmp_path: Path) -> None:
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = "## 8.1 Section\n\nThe queue is 73 frames deep.\n"
    hard, _, _ = grade(tmp_path, text, by, excused={("chapter08.md", "8.1", "73")})
    assert hard == 0


def test_authoring_comments_are_not_claims(tmp_path: Path) -> None:
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = (
        "## 8.1 Section\n\n<!-- reviewed against Issue #59, gate 22 -->\n\n"
        "The model scores 4.9 per cent error (`V-05-01`).\n"
    )
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 0


def test_axis_ticks_are_geometry_but_labelled_figure_numbers_are_claims(tmp_path: Path) -> None:
    by = registry(("V-05-01", "wer_percent", "4.9"))
    text = (
        "## 8.1 Section\n\nThe model scores 4.9 per cent error (`V-05-01`).\n\n"
        "```tikz\n"
        "\\node[below] at (1,0) {1000};\n"
        "\\node[below] at (2,0) {9999};\n"
        "```\n"
    )
    hard, notes, lines = grade(tmp_path, text, by)
    # 1000 is a bare tick: invisible. 9999 is also bare: invisible. No fence number is hard.
    assert hard == 0


def test_declared_derivation_is_a_note_not_a_mismatch(tmp_path: Path) -> None:
    by = registry(("V-05-02", "frame_ms", "40"), ("V-05-03", "hop_ms", "20"))
    text = (
        "## 8.1 Section\n\nThe overlap is 20 ms, derived from `V-05-02` and `V-05-03` "
        "as half the frame, printing 60 per cent coverage.\n"
    )
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 0
    assert any("note" in ln and "60" in ln for ln in lines)


def test_id_digits_are_never_graded_as_measurements(tmp_path: Path) -> None:
    """`V-01-09` must not contribute tokens 01 and 09 for the reviewer to chase."""
    by = registry(("V-01-09", "dsp_slices", "1,248"))
    text = "## 8.1 Section\n\n| `V-01-09` | the fabric's 1,248 multiply-accumulate slices |\n"
    hard, notes, lines = grade(tmp_path, text, by)
    assert hard == 0


@pytest.mark.parametrize("tool", ["check_pairing", "check_figures", "compile_tikz"])
def test_promoted_scripts_import_cleanly(tool: str) -> None:
    mod = __import__(tool)
    assert hasattr(mod, "main")
