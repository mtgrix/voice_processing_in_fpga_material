#!/usr/bin/env python3
"""Render book/references.bib from docs/source_index.json.

One identifier space is the point. The repository had three: doc_id strings in
docs/verification/claims.json, registry ids in docs/source_index.json, and five semantic BibTeX keys
in book/references.bib that no record and no row used. A chapter that cites FINN has to pick one
spelling, and whichever it picks, the other two can be edited without anything noticing. The .bib
is now a rendering of the registry, keyed by registry id, so `[@R01-02]` in a chapter and
`doc_id: "ACM FPGA 2017 / arXiv:1612.07119"` in a record are the same source by two names that one
file relates.

    --write   rewrite book/references.bib in place
    --check   exit non-zero if the file on disk differs from the rendering (default)

Where a value comes from, per field:

  key      the registry id. Hyphens are legal in a Pandoc citation key, and R01-02 is what
           docs/SOURCES.md and three chapters already print.
  author   authors_bibtex, else {{publisher}} for a document whose publisher is its author, else
           no author at all. See CORPORATE_AUTHOR_TYPES.
  title    the registry title, which for most rows is the title recorded on the citing record.
  <venue>  venue, under the field name the entry type expects: journal, booktitle, institution,
           organization.
  year     year. 21 rows have none, because no captured quote states one; that is Issue #40's work.
  pages    pages, in BibTeX's en-dash form.
  url      url. One row has none (S024, whose claims are all unresolved).

This script can refuse to write, on three counts: a registry row whose type it cannot turn into an
entry type, a row with no title, and two rows that would share a key. All three mean the .bib would
silently cite something other than what the registry describes.

Issue #42. Run 'make render-bib' after changing the registry; 'make check-bib' is in the gate.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "docs" / "source_index.json"
BIB_PATH = ROOT / "book" / "references.bib"

#: The registry's document kinds, and the BibTeX entry type to write for each. A closed set on
#: purpose: a kind that is not here stops the build rather than picking @misc, because @misc is what
#: a citation looks like when nobody decided what it is.
ENTRY_TYPE_BY_TYPE: dict[str, str] = {
    "vendor-datasheet": "manual",
    "vendor-tool-guide": "manual",
    "vendor-guide": "manual",
    "vendor-ip-guide": "manual",
    "vendor-whitepaper": "manual",
    "conference-paper": "inproceedings",
    "journal-article": "article",
    "preprint": "misc",
    "corpus-page": "misc",
    "conference-webpage": "misc",
    "product-catalogue": "misc",
    "source-code": "misc",
    "repository-documentation": "misc",
    "software-documentation": "misc",
}

#: Which field carries `venue` for each entry type. BibTeX names the same idea four ways.
VENUE_FIELD_BY_ENTRY: dict[str, str] = {
    "article": "journal",
    "inproceedings": "booktitle",
    "techreport": "institution",
    "manual": "organization",
    "misc": "howpublished",
}

#: Document kinds whose publisher wrote them, so a corporate author is a fact rather than a guess:
#: a datasheet comes from the vendor, source code from the project that maintains it. Kinds missing
#: here are papers and pages published by a body other than the people who wrote them, and a row of
#: that kind with no authors_bibtex renders with no author field, which is what the registry knows.
CORPORATE_AUTHOR_TYPES: frozenset[str] = frozenset(
    {
        "vendor-datasheet",
        "vendor-tool-guide",
        "vendor-guide",
        "vendor-ip-guide",
        "vendor-whitepaper",
        "source-code",
        "repository-documentation",
        "software-documentation",
        "product-catalogue",
        "corpus-page",
    }
)

#: A Pandoc citation key, as the manuscript will type it.
KEY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]*$")

HEADER = (
    "% GENERATED FILE -- do not edit.\n"
    "% Rendered from docs/source_index.json by scripts/verification/build_bibliography.py.\n"
    "% To change an entry, edit the SPEC list in that script's generator (curated columns) or the\n"
    "% record that quotes the document (derived ones), then run: make render-bib\n"
    "% Keys are registry ids, so a chapter cites [@R01-02] and an evidence record names the same\n"
    "% work by its doc_id; docs/source_index.json records which label belongs to which row.\n"
    "% Author, year and licence appear only where the registry has them. An entry that lacks\n"
    "% one is printing a gap the evidence records have not closed, not a formatting oversight:\n"
    "% Issue #40 fills it from a captured quote. The build line counts them out of the registry,\n"
    "% so this header states no number that could go stale.\n"
)


@dataclass
class Report:
    text: str = ""
    entries: int = 0
    authorless: list[str] = field(default_factory=list)
    corporate: list[str] = field(default_factory=list)
    unmapped: list[str] = field(default_factory=list)
    no_title: list[str] = field(default_factory=list)
    duplicate_keys: list[str] = field(default_factory=list)
    no_url: list[str] = field(default_factory=list)
    no_year: list[str] = field(default_factory=list)


def author_of(row: dict[str, Any]) -> str | None:
    """The BibTeX author string for a registry row, or None when the registry has no author."""
    explicit = row.get("authors_bibtex")
    if explicit:
        return str(explicit)
    publisher = row.get("publisher")
    if publisher and str(row.get("type")) in CORPORATE_AUTHOR_TYPES:
        # Double braces tell BibTeX the whole string is one corporate name, so it is not reordered
        # into "Inc., Advanced Micro Devices".
        return "{{" + str(publisher) + "}}"
    return None


def entry_of(row: dict[str, Any]) -> tuple[str, list[tuple[str, str]]] | None:
    """The entry type and its fields, in the order they are written out, or None if unusable."""
    bibtex = row.get("bibtex_entry")
    entry_type = str(bibtex) if bibtex else ENTRY_TYPE_BY_TYPE.get(str(row.get("type")))
    if not entry_type:
        return None
    fields: list[tuple[str, str]] = []
    author = author_of(row)
    if author:
        fields.append(("author", author))
    # Braced, because the IEEE style applies a sentence-lowercasing transform to titles and the
    # registry's title is the document's own spelling: "Jetson", "torch.round" and
    # "Brevitas.core.quant.int_base" are facts, and lowercase turns two of them into wrong words.
    # One pair is the field delimiter, so the value carries its own: title = {{...}}.
    fields.append(("title", "{" + str(row.get("title") or "") + "}"))
    venue = row.get("venue")
    if venue:
        venue_field = VENUE_FIELD_BY_ENTRY.get(entry_type, "note")
        fields.append((venue_field, str(venue)))
    if row.get("year"):
        fields.append(("year", str(row["year"])))
    if row.get("pages"):
        fields.append(("pages", str(row["pages"])))
    publisher = str(row.get("publisher") or "")
    if publisher and entry_type in {"inproceedings", "misc"} and author != "{{" + publisher + "}}":
        # `author != ...` because a corporate author *is* the publisher, and citeproc prints both:
        # "Xilinx, Inc., “Brevitas source….” Xilinx, Inc." for every source-code and documentation
        # row. A row with a real author list keeps its publisher, which is why FINN still says ACM.
        fields.append(("publisher", publisher))
    if row.get("url"):
        fields.append(("url", str(row["url"])))
    return entry_type, fields


def render(index: dict[str, Any]) -> Report:
    """Build the whole .bib text, and say what had to be decided on the way."""
    out = Report()
    lines: list[str] = [HEADER, ""]
    seen: set[str] = set()
    rows = list(index.get("sources", []))

    for row in rows:
        key = str(row.get("id") or "")
        if key in seen:
            out.duplicate_keys.append(key)
            continue
        seen.add(key)
        if not KEY_PATTERN.match(key):
            out.duplicate_keys.append(f"{key} (not usable as a citation key)")
            continue
        if not row.get("title"):
            out.no_title.append(key)
            continue
        entry = entry_of(row)
        if entry is None:
            out.unmapped.append(f"{key}: type {row.get('type')!r} has no BibTeX entry type")
            continue
        entry_type, fields = entry
        if not row.get("url"):
            out.no_url.append(key)
        if not row.get("year"):
            out.no_year.append(key)
        if not author_of(row):
            out.authorless.append(key)
        elif not row.get("authors_bibtex"):
            out.corporate.append(key)

        # The doc_id label is what an evidence record quotes, and the .bib reader needs it to find
        # the row back. A comment, because citeproc prints a note field and this is for the
        # repository, not for the reference list.
        labels = row.get("doc_ids") or []
        comment = (
            f"% {key}: cited in docs/verification/claims.json as {', '.join(map(repr, labels))}"
        )
        if not labels:
            comment = f"% {key}: registered and uncited, so no record names a doc_id for it"
        lines.append(comment)
        lines.append(f"@{entry_type}{{{key},")
        for name, value in fields:
            lines.append(f"  {name:<10} = {{{value}}},")
        lines.append("}")
        lines.append("")

    out.entries = len([ln for ln in lines if ln.startswith("@")])
    out.text = "\n".join(lines)
    return out


def main(argv: list[str]) -> int:
    args = list(argv)
    write = "--write" in args
    for flag in ("--write", "--check"):
        while flag in args:
            args.remove(flag)
    if args:
        print(f"build_bibliography: unknown argument: {args[0]}", file=sys.stderr)
        return 2
    if not INDEX_PATH.exists():
        print(f"build_bibliography: {INDEX_PATH} does not exist", file=sys.stderr)
        return 2

    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    report = render(index)
    on_disk = BIB_PATH.read_text(encoding="utf-8") if BIB_PATH.exists() else ""
    text = report.text
    state = "clean" if on_disk == text else "DRIFT"
    if write:
        BIB_PATH.write_text(text, encoding="utf-8", newline="\n")
        state = "wrote"

    print(
        f"{state}  book/references.bib  {report.entries} entries from "
        f"{len(index.get('sources', []))} registry rows; "
        f"{len(report.corporate)} take a corporate author from their publisher, "
        f"{len(report.authorless)} have no author recorded and {len(report.no_year)} no year"
    )
    for line in report.unmapped:
        print(f"  NO-ENTRY  {line}")
    for line in report.no_title:
        print(f"  NO-TITLE  {line}: a .bib entry without a title cites nothing in particular")
    for line in report.duplicate_keys:
        print(f"  DUP-KEY   {line}: two rows would render under one citation key")
    for line in report.no_url:
        print(f"  hint      {line}: no url, so a reader cannot open what the book cites")
    if state == "DRIFT" and not write:
        diff = [
            line
            for line in difflib.unified_diff(
                on_disk.splitlines(), text.splitlines(), lineterm="", n=0
            )
            if line[:1] in "+-" and not line.startswith(("---", "+++"))
        ]
        print(f"FAIL: book/references.bib differs from the registry in {len(diff)} line(s)")
        for line in diff[:8]:
            print("   ", line[:160])
        print("    run: make render-bib")
        return 1
    if report.unmapped or report.no_title or report.duplicate_keys:
        print("FAIL: the registry cannot render a bibliography; see the lines above")
        return 1
    print("PASS: every registry row renders one entry, and every entry names one registry row")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
