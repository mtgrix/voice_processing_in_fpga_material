"""Automated repository integrity and source consistency tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestSourceIndexIntegrity:
    """Verify docs/source_index.json is well-formed, valid, and references existing notes."""

    def test_source_index_exists_and_parses(self) -> None:
        idx_path = ROOT / "docs" / "source_index.json"
        assert idx_path.exists(), "docs/source_index.json must exist"
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        assert "sources" in data
        assert len(data["sources"]) > 0

    def test_source_ids_are_unique(self) -> None:
        idx_path = ROOT / "docs" / "source_index.json"
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        ids = [s["id"] for s in data["sources"]]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"

    def test_research_note_paths_exist(self) -> None:
        idx_path = ROOT / "docs" / "source_index.json"
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        missing = []
        for s in data["sources"]:
            note_path = s.get("research_note_path", "")
            if note_path and not (ROOT / note_path).exists():
                missing.append(note_path)
        assert not missing, f"Missing research note files: {missing}"


class TestForbiddenPromptArtifacts:
    """Ensure no prompt wrapper markers leak into repository files."""

    FORBIDDEN = [
        "</content>",
        "</parameter>",
        "<content>",
        "<parameter",
        "assistant to=",
    ]

    SKIP_FILES = {
        Path("scripts/verify_integrity.py"),
        Path("tests/test_repo_integrity.py"),
    }

    def test_no_forbidden_markers_in_code_or_docs(self) -> None:
        violations = []
        for ext in ["*.md", "*.py", "*.json"]:
            for file in ROOT.rglob(ext):
                rel = file.relative_to(ROOT)
                if rel in self.SKIP_FILES or any(
                    p in rel.parts for p in [".git", ".pytest_cache", ".ruff_cache"]
                ):
                    continue
                content = file.read_text(encoding="utf-8", errors="ignore")
                for m in self.FORBIDDEN:
                    if m in content:
                        violations.append(f"{rel} contains '{m}'")
        assert not violations, f"Forbidden markers detected: {violations}"
