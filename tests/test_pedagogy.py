"""Automated tests for pedagogical policy and structural integrity."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_all_10_chapters_presence() -> None:
    """Check that all 10 chapters exist in both Vietnamese and English editions."""
    for i in range(1, 11):
        ch_num = f"{i:02d}"
        vi_path = ROOT / "book" / f"chapter{ch_num}.md"
        en_path = ROOT / "book-en" / f"chapter{ch_num}.md"
        assert vi_path.exists(), f"Missing Vietnamese chapter {vi_path}"
        assert en_path.exists(), f"Missing English chapter {en_path}"


def test_chapter_pedagogical_sidebars() -> None:
    """Verify all chapters contain the Minimal Math / Concepts sidebar."""
    for i in range(1, 11):
        ch_num = f"{i:02d}"
        ch_vi = (ROOT / "book" / f"chapter{ch_num}.md").read_text(encoding="utf-8")
        assert f"# Chương {i}:" in ch_vi
        assert "Toán học / Khái niệm Tối thiểu" in ch_vi or "Toán học Tối thiểu" in ch_vi


def test_experiment_template_and_readmes() -> None:
    """Verify that the official experiment template exists and contains all 13 sections."""
    template_path = ROOT / "experiments_template" / "README.md"
    assert template_path.exists(), "Missing experiments_template/README.md"
    content = template_path.read_text(encoding="utf-8")
    for sec_num in range(1, 14):
        assert f"## {sec_num}." in content, f"Missing section {sec_num} in experiment template"
