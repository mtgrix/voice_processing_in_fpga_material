"""Generate the per-topic markdown files in docs/verification from claims.json.

claims.json is the single source of truth; the markdown files are a rendering of it.
Without that rule the two drift apart, which is how 26 records ended up with raw pipes
inside quotes that split their own table rows mid-sentence.

    --write   rewrite the markdown files in place
    --check   exit non-zero if anything on disk differs from the rendering (default)

The renderer is pure: given claims.json it reproduces every file byte for byte, deriving
both the H1 title and the per-record heading from the data rather than reading them off
disk. A generator that absorbed existing headings could not detect a renamed or dropped
heading, so it does not.
"""

from __future__ import annotations

import difflib
import re
import sys
from typing import Any

# The helpers beside this file are imported by module name, so that the script runs
# from the repository root without an installed package or a PYTHONPATH assignment.
if __package__ in (None, ""):
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims_lib import EVIDENCE_DIR, RECORD_FIELDS, file_of, load_claims, records

#: Fields rendered inside backticks, which is every field except the human-readable ones.
BACKTICK = {
    "status",
    "quantity",
    "value",
    "unit",
    "conditions",
    "source_tier",
    "doc_id",
    "retrieved_utc",
    "access",
}


def cell(field: str, value: Any) -> str:
    """Render one field value as a markdown table cell."""
    text = "" if value is None else str(value)
    if field in BACKTICK:
        text = "`" + text + "`"
    return text.replace("|", "\\|")


def heading_for(rec: dict[str, Any]) -> str:
    """The title of a record block, derived from its quantity name."""
    quantity = str(rec.get("quantity") or rec.get("id"))
    return quantity.replace("_", " ").title()


def title_for(filename: str) -> str:
    """The H1 of a record file, derived from its own name."""
    stem = filename[:-3] if filename.endswith(".md") else filename
    # The NN- prefix is part of the topic name, not scaffolding: the files are read in
    # numeric order and the title should match the filename a reader opened.
    topic = stem.replace("-", " ").title()
    return "# Verification Records: " + topic


def render(rec: dict[str, Any]) -> str:
    """Render one record as a heading plus a field table."""
    lines = [
        "### " + str(rec["id"]) + " · " + heading_for(rec),
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for field in RECORD_FIELDS:
        lines.append("| " + field + " | " + cell(field, rec.get(field, "")) + " |")
    return "\n".join(lines) + "\n"


def grouped() -> dict[str, list[dict[str, Any]]]:
    """Records bucketed by their two-digit file group, in id order."""
    buckets: dict[str, list[dict[str, Any]]] = {}
    for rec in records(load_claims()):
        buckets.setdefault(file_of(str(rec["id"])), []).append(rec)
    for bucket in buckets.values():
        bucket.sort(key=lambda r: int(str(r["id"]).rsplit("-", 1)[1]))
    return buckets


def path_for(group: str) -> str:
    """The markdown file on disk that carries a given record group."""
    matches = sorted(EVIDENCE_DIR.glob(group + "-*.md"))
    if not matches:
        raise SystemExit(f"render: no file on disk starts with {group}-")
    return matches[0].name


def build(group: str, recs: list[dict[str, Any]]) -> tuple[str, str]:
    """Return (filename, full intended contents) for one record group."""
    filename = path_for(group)
    body = "\n".join(render(rec) for rec in recs)
    return filename, title_for(filename) + "\n\n" + body


def main(argv: list[str]) -> int:
    """Render every group and either write it or diff it."""
    write = "--write" in argv
    problems = 0
    total_rows = 0
    for group, recs in sorted(grouped().items()):
        filename, new = build(group, recs)
        full = EVIDENCE_DIR / filename
        rows = len([ln for ln in new.split("\n") if re.match(r"^\|.*\|$", ln)])
        total_rows += rows
        original = full.read_text(encoding="utf-8") if full.exists() else ""
        if write:
            if original != new:
                full.write_text(new, encoding="utf-8", newline="\n")
                print(f"wrote {filename}")
            else:
                print(f"unchanged {filename}")
            continue
        diff = [
            line
            for line in difflib.unified_diff(
                original.splitlines(), new.splitlines(), lineterm="", n=0
            )
            if line[:1] in "+-" and not line.startswith(("---", "+++"))
        ]
        if diff:
            problems += 1
            print(f"DRIFT {filename}: {len(diff)} lines differ from claims.json")
            for line in diff[:6]:
                print("   ", line[:160])
        else:
            print(f"clean   {filename}  ({len(recs)} records, {rows} table rows)")
    if not write:
        print(f"\ntotal table rows {total_rows}")
        if problems:
            print(
                f"FAIL: {problems} file(s) drift from claims.json; run make render-evidence",
                file=sys.stderr,
            )
            return 1
        print("PASS: every markdown file renders byte-exact from claims.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
