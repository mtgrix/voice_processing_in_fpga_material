"""Repository Integrity and Academic Consistency Verification Script."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_source_index() -> list[str]:
    errors = []
    idx_path = ROOT / "docs" / "source_index.json"
    if not idx_path.exists():
        return ["docs/source_index.json does not exist"]

    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        sources = data.get("sources", [])
        if not sources:
            errors.append("No sources registered in docs/source_index.json")

        seen_ids = set()
        for s in sources:
            sid = s.get("id")
            if not sid:
                errors.append("Source missing 'id' field")
            elif sid in seen_ids:
                errors.append(f"Duplicate source ID: {sid}")
            seen_ids.add(sid)

            note_path = s.get("research_note_path")
            if note_path and not (ROOT / note_path).exists():
                errors.append(f"Research note file not found: {note_path}")
    except Exception as e:
        errors.append(f"Failed to parse docs/source_index.json: {e}")

    return errors


def check_forbidden_markers() -> list[str]:
    errors = []
    forbidden = [
        "</content>",
        "</parameter>",
        "<content>",
        "<parameter",
        "assistant to=",
    ]
    skip_files = {
        Path("scripts/verify_integrity.py"),
        Path("tests/test_repo_integrity.py"),
    }
    for ext in ["*.md", "*.py", "*.json"]:
        for file in ROOT.rglob(ext):
            rel = file.relative_to(ROOT)
            if rel in skip_files or any(
                p in rel.parts for p in [".git", ".pytest_cache", ".ruff_cache"]
            ):
                continue
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
                for marker in forbidden:
                    if marker in content:
                        errors.append(f"Forbidden marker '{marker}' found in {rel}")
            except Exception:
                pass
    return errors


def main() -> int:
    print("Verifying Voice Edge AI repository integrity...")
    all_errors = []
    all_errors.extend(check_source_index())
    all_errors.extend(check_forbidden_markers())

    if all_errors:
        print("FAIL: Integrity errors detected:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("PASS: Repository integrity and citations fully verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
