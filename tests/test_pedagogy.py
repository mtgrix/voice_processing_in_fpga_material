"""Automated tests for pedagogical policy and structural integrity."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_manuscript_chapter_presence() -> None:
    """Check that Chapter 1 and Chapter 2 exist in both Vietnamese and English editions."""
    assert (ROOT / "book" / "chapter01.md").exists()
    assert (ROOT / "book" / "chapter02.md").exists()
    assert (ROOT / "book-en" / "chapter01.md").exists()
    assert (ROOT / "book-en" / "chapter02.md").exists()


def test_vietnamese_chapter01_pedagogical_structure() -> None:
    """Verify Chapter 01 adheres to pedagogical conventions (Sidebar, Headings)."""
    ch1_vi = (ROOT / "book" / "chapter01.md").read_text(encoding="utf-8")
    assert "# Chương 1:" in ch1_vi
    # Verify Minimal Math Sidebar is present
    assert "Toán học Tối thiểu cho Chương này" in ch1_vi
    # Verify STFT and Mel equations are present
    assert "STFT" in ch1_vi
    assert "Mel" in ch1_vi


def test_vietnamese_chapter02_pedagogical_structure() -> None:
    """Verify Chapter 02 includes the Minimal Math Sidebar and key hardware concepts."""
    ch2_vi = (ROOT / "book" / "chapter02.md").read_text(encoding="utf-8")
    assert "# Chương 2:" in ch2_vi
    assert "Toán học Tối thiểu cho Chương này" in ch2_vi
    assert "TensorRT" in ch2_vi
    assert "tegrastats" in ch2_vi
    assert "RTF" in ch2_vi
