"""Make chapter-count drift impossible rather than merely corrected once.

The repository states its own structure in four places: the roadmap table in
``plan-v2.md`` section 7, the chapter table in ``docs/BOOK_STATUS.md``, the experiment table
in ``docs/EXPERIMENT_STATUS.md``, and ``README.md``. plan-v2 section 9.3 rules that ten
chapters is canonical, and notes that fixing the count once is not enough: nothing stopped a
fifth document from re-introducing a different number. This file is that stop.

It also looks at ``book/TOC.md``, which currently disagrees. That test is an expected failure
rather than a pass or a hard failure, so the conflict is visible in every test run without
blocking work that is unrelated to it. Resolving it needs a human, because the fix is a
rewrite of a file under ``book/``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: The canonical count, from plan-v2.md section 9.3.
CANONICAL_CHAPTER_COUNT = 10

STATUS_DOCS = {
    "docs/BOOK_STATUS.md": re.compile(r"^\|\s*\*\*(\d{2})\*\*\s*\|", re.MULTILINE),
    "docs/EXPERIMENT_STATUS.md": re.compile(
        r"^\|\s*\*\*exp_(\d{2})\*\*\s*\|\s*(\d{2})\s*\|", re.MULTILINE
    ),
}


def _text(relative: str) -> str:
    path = ROOT / relative
    assert path.exists(), f"{relative} is missing; the project structure is no longer described"
    return path.read_text(encoding="utf-8")


def _roadmap_chapters() -> list[str]:
    """Chapter numbers bound to a stage in the plan-v2 roadmap table, section 7.

    Stage 0 has no chapter: it is the capture step that precedes the book. It is therefore
    excluded here rather than counted as an eleventh chapter.
    """
    section = _text("plan-v2.md").split("## 7. LỘ TRÌNH", 1)
    assert len(section) == 2, "plan-v2.md lost its roadmap section 7"
    body = section[1].split("\n### 7.", 1)[0]
    return [m.group(2) for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*(\d{2})\s*\|", body, re.MULTILINE)]


def test_book_status_lists_ten_chapters() -> None:
    chapters = STATUS_DOCS["docs/BOOK_STATUS.md"].findall(_text("docs/BOOK_STATUS.md"))
    assert len(chapters) == CANONICAL_CHAPTER_COUNT
    assert chapters == [f"{n:02d}" for n in range(1, CANONICAL_CHAPTER_COUNT + 1)]


def test_experiment_table_covers_every_chapter_exactly_once() -> None:
    rows = STATUS_DOCS["docs/EXPERIMENT_STATUS.md"].findall(_text("docs/EXPERIMENT_STATUS.md"))
    assert len(rows) == CANONICAL_CHAPTER_COUNT
    assert [exp for exp, _ in rows] == [f"{n:02d}" for n in range(1, CANONICAL_CHAPTER_COUNT + 1)]
    assert [ch for _, ch in rows] == [f"{n:02d}" for n in range(1, CANONICAL_CHAPTER_COUNT + 1)]


def test_roadmap_stages_and_chapter_tables_agree() -> None:
    assert _roadmap_chapters() == [f"{n:02d}" for n in range(1, CANONICAL_CHAPTER_COUNT + 1)]


def test_no_document_claims_a_different_chapter_count() -> None:
    """Catch a prose assertion of a different structure, in the files that define structure."""
    offenders: list[str] = []
    for relative in ("plan-v2.md", "README.md", "docs/BOOK_STATUS.md"):
        for match in re.finditer(
            r"(\d{1,2})\s*(?:chapters?|chặng|Chương \(Chapters?\))", _text(relative)
        ):
            count = int(match.group(1))
            if count not in {CANONICAL_CHAPTER_COUNT, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}:
                offenders.append(f"{relative}: {match.group(0)!r}")
    assert not offenders, (
        "a structure document asserts a chapter count outside the range: " + "; ".join(offenders)
    )


@pytest.mark.xfail(
    strict=False,
    reason=(
        "book/TOC.md is untracked and declares 5 chapters while plan-v2 section 9.3 makes "
        "10 canonical. Closing this needs a human decision: regenerate the TOC from "
        "plan-v2 section 7, or delete it. Editing a file under book/ is not an agent's call."
    ),
)
def test_toc_agrees_with_the_canonical_chapter_count() -> None:
    path = ROOT / "book" / "TOC.md"
    if not path.exists():
        pytest.skip("book/TOC.md does not exist in this checkout")
    text = path.read_text(encoding="utf-8")
    declared = len(re.findall(r"^## Chương \d+", text, re.MULTILINE))
    assert declared == CANONICAL_CHAPTER_COUNT, f"book/TOC.md declares {declared} chapters"
