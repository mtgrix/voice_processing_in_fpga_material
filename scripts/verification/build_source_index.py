#!/usr/bin/env python3
"""Regenerate docs/source_index.json from its curated spec plus claims.json.

The registry has two halves. Which documents exist, what they are called, who publishes them,
what licence their content carries and what a reader should be warned about: that is curated, and
it lives in SPEC below. Which verification records rest on each document: that is derived, from
the doc_id field of every record in claims.json, and it must never be typed by hand -- a hand-kept
list of 103 records across 30 documents rots the first time a chapter adds one.

So this script merges. It takes the five legacy R01-NN dictionaries out of the file on disk and
keeps them verbatim apart from the derived doc_ids and claims_supported, and it rebuilds every
S0NN entry from SPEC.

    --write   rewrite docs/source_index.json in place
    --check   exit non-zero if the file on disk differs from the rendering (default)

Issue #20. Run 'make render-registry' after adding or editing any record. What makes the registry
a gate rather than a list is that this script can refuse to emit one, on four counts: a doc_id the
records cite that nothing registers (UNMAPPED); a registered label no record uses any more (STALE);
a document with no url holding up a claim that is not itself unresolved (NO-URL); and an exempt
label sitting on a record that asserts a value (EXEMPT). 'make check-registry' runs this file with
--check and fails on any of those, or on drift between docs/source_index.json and this rendering.
scripts/verify_integrity.py asks this script the same question instead of answering it twice, so the
join has one derivation in the repository.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

if __package__ in (None, ""):
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claims_lib import (
    CLAIMS_PATH,
    EXACT_EXEMPT,
    EXEMPT_PREFIXES,
    ROOT,
    is_exempt,
    load_claims,
    records,
)

INDEX_PATH = ROOT / "docs" / "source_index.json"

#: The two accepted id forms, so that the carry-forward loop below can tell an entry it must
#: leave alone from an entry this script owns. Mirrors SOURCE_ID_PATTERN in verify_integrity.py.
LEGACY_ID_PATTERN = re.compile(r"^R\d{2}-\d{2}$")
NEW_ID_PATTERN = re.compile(r"^S\d{3}$")

#: The schema this script emits. A new field is a new version, because the field is what tells a
#: reader whether a citation resolves.
REGISTRY_VERSION = "1.2.0"

#: Moved out of the JSON and into the script for the same reason the records moved into
#: claims.json: a rendering that reads its own prose off disk cannot detect that prose being
#: edited by hand. The text is the one the file carried before Issue #20.
ID_SCHEME = (
    "New sources: global S<NNN>, never carrying a chapter number, because a chapter is an "
    "attribute of a source and not its identity. The five legacy R01-NN ids are retained: "
    "book/chapter01.md and book/chapter02.md cite them by name and docs/SOURCES.md lists them, so "
    "renumbering is a human edit to prose, not a mechanical one. scripts/verify_integrity.py "
    "accepts exactly these two forms. Every entry lists the doc_id labels it answers, in doc_ids."
)

DOC_ID_NOTE = (
    "doc_ids holds the doc_id strings that records in docs/verification/claims.json use to cite "
    "this work, and it is the join between the evidence set and the registry. One document may be "
    "cited by several labels, because a label is a spelling and not a source; the aliases are "
    "listed here rather than renamed in the records, so that no record lost its own history. "
    "The labels that name arithmetic or an absence are exempt, defined once by "
    "claims_lib.is_exempt and pinned by tests/test_source_registry.py."
)


@dataclass
class Entry:
    """One curated registry row: a document, and the labels claims.json uses for it.

    One row per document, not per label. ``aliases`` holds the other spellings records use for the
    same work, which is how the registry was reconciled without renaming a single record.

    ``legacy_id`` names an existing R01-NN entry to attach this row to instead of minting an S0NN
    id, which is how the three documents that predate the reconciliation keep the identifier
    book/chapter01.md already cites them by.
    """

    doc_id: str
    type: str
    publisher: str
    id: str | None = None
    aliases: tuple[str, ...] = ()
    title: str | None = None
    authors: str | None = None
    year: int | None = None
    licence: str | None = None
    legacy_id: str | None = None
    notes: str | None = None


#: The documents the evidence set cites. Ordering is by id and fixes the S0NN numbering, so it is
#: not an arbitrary list: a number that moves between runs would make every diff unreadable.
#: Where records disagree about the same work, the notes say so instead of the generator
#: averaging the disagreement away.
SPEC: list[Entry] = [
    Entry(
        doc_id="UG440 (v2022.1)",
        id="S001",
        type="vendor-tool-guide",
        publisher="Xilinx, Inc.",
        notes="Xilinx Power Estimator user guide. T2 under docs/WEB_SEARCH_PROTOCOL.md section 2:"
        " a tool reference, which describes what an estimate means rather than what a chip "
        "contains.",
    ),
    Entry(
        doc_id="UG906 (v2022.2)",
        id="S002",
        type="vendor-tool-guide",
        publisher="Xilinx, Inc.",
        notes="Vivado Design Analysis and Closure Techniques. The page read is Report Utilization, "
        "where a synthesis report's terms are defined.",
    ),
    Entry(
        doc_id="UG973 (v2019.1 / v2022.2)",
        id="S003",
        type="vendor-tool-guide",
        publisher="Xilinx, Inc.",
        notes="One label spanning two revisions; each record's locator names the revision it was "
        "read from. The Vivado ML Standard support table in V-04-01 is a statement about the tool "
        "licence a designer needs, not a licence of this document, so no licence field appears "
        "here.",
    ),
    Entry(
        doc_id="VivadoGuide2024_1",
        id="S004",
        type="vendor-tool-guide",
        publisher="Xilinx, Inc.",
        notes="Not vendor-hosted. The recorded url is a university course mirror "
        "(hthreads.github.io) of the Xilinx installation guide, which is why the doc_id is a file "
        "name rather than a document number. The tier holds for the content, which is the vendor's "
        "own text; the copy is not authoritative, so a revision check has to go to the vendor.",
    ),
    Entry(
        doc_id="DS890 (v4.10)",
        id="S005",
        aliases=("DS890 (v4.10) & DS891 (v1.9)", "DS890 (v4.10) & DS986 (v1.3)"),
        type="vendor-datasheet",
        publisher="Advanced Micro Devices, Inc.",
        notes="UltraScale Architecture Overview. The two compound labels each name a second "
        "datasheet, but in every one of those records the title, url and locator are DS890's, so "
        "DS891 was never read as a source of its own and is registered nowhere. That is a gap in "
        "the evidence set, and it is not papered over by an entry with no quote in it.",
    ),
    Entry(
        doc_id="DS986 (v1.3)",
        id="S006",
        aliases=("DS986 (v1.1)",),
        type="vendor-datasheet",
        publisher="Advanced Micro Devices, Inc.",
        notes="Two revisions of the KV260 datasheet, both read: V-03-05 quotes v1.1 and the others "
        "quote v1.3. One document, because a revision is an attribute rather than a second "
        "work. Read as HTML on docs.amd.com while sibling datasheets at the same host are recorded "
        "T1, so this entry keeps tiers_observed at T2 and the disagreement is reported rather than "
        "silently unified.",
    ),
    Entry(
        doc_id="DS987 (v1.2)",
        id="S007",
        type="vendor-datasheet",
        publisher="Advanced Micro Devices, Inc.",
        notes="Kria K26 System-on-Module datasheet: the silicon under the KV260 carrier board.",
    ),
    Entry(
        doc_id="PG338 (v4.1)",
        id="S008",
        aliases=("PG338 (v3.0)",),
        type="vendor-ip-guide",
        publisher="Advanced Micro Devices, Inc.",
        title="DPUCZDX8G for Zynq UltraScale+ MPSoCs Product Guide (PG338)",
        notes="The title printed on the guide's own title page, which V-04-03 quotes. The "
        "docs.amd.com names the same document 'DPU for Convolutional Neural Network IP Product "
        "Guide' and four records carry that spelling instead. The revision alias carries weight: "
        "V-04-04 quotes a Table 11 that exists in v3.0 and not in v4.1, and was withdrawn as "
        "evidence on that fact (conflict C-04) rather than merged quietly into this entry.",
    ),
    Entry(
        doc_id="DS-10662-001v1.8",
        id="S009",
        type="vendor-datasheet",
        publisher="NVIDIA Corporation",
        notes="Jetson AGX Orin Series module datasheet, read from a third-party distributor mirror "
        "(generation-robots.com) rather than the vendor's own download.",
    ),
    Entry(
        doc_id="DS-10712-001_v1.7",
        id="S010",
        type="vendor-datasheet",
        publisher="NVIDIA Corporation",
        notes="Jetson Orin NX Series module datasheet, vendor-hosted.",
    ),
    Entry(
        doc_id="DS-11105-001_v1.1",
        id="S011",
        aliases=("DS-11105-001",),
        type="vendor-datasheet",
        publisher="NVIDIA Corporation",
        notes="Jetson Orin Nano Series module datasheet, read via a connecttech.com mirror. Two "
        "doc_id spellings are one PDF: V-02-06 records that it carries no revision number "
        "on its cover, so the v1.1 suffix is a reader's label and not a property of the file. "
        "Merged by alias rather than by renaming records, because renaming would destroy the note "
        "that says exactly that.",
    ),
    Entry(
        doc_id="Jetson Linux Developer Guide (r36.4.4)",
        id="S012",
        type="vendor-guide",
        publisher="NVIDIA Corporation",
        notes="Platform Power and Performance page, where nvpmodel and the power-mode labels are "
        "defined.",
    ),
    Entry(
        doc_id="Jetson Orin Nano DevKit User Guide (2025-2026)",
        id="S013",
        type="vendor-guide",
        publisher="NVIDIA Corporation",
        notes="The date range in the doc_id is the guide's own title-page stamp.",
    ),
    Entry(
        doc_id="Brevitas master, read 2026-09-12",
        id="S014",
        type="source-code",
        publisher="Xilinx, Inc.",
        notes="Not a published document: two module files in a repo at its master branch as of "
        "the date in the doc_id. The date is load-bearing because master moves, so one quoting "
        "this work is true of that day's tree and of no other.",
    ),
    Entry(
        doc_id="WeNet LibriSpeech README",
        id="S015",
        type="repository-documentation",
        publisher="The WeNet project",
        notes="A project's own README states what that project achieved, which is a claim by the "
        "party with an interest in it, so it corroborates and does not establish.",
    ),
    Entry(
        doc_id="WeNet LibriSpeech Recipe Config",
        id="S016",
        type="source-code",
        publisher="The WeNet project",
        notes="The recipe's YAML config, where the frontend values of a published model are "
        "actually written down, as opposed to described.",
    ),
    Entry(
        doc_id="WeNet Pretrained Models & Tutorial",
        id="S017",
        type="repository-documentation",
        publisher="The WeNet project",
    ),
    Entry(
        doc_id="PyTorch 2.14 documentation",
        id="S018",
        type="software-documentation",
        publisher="PyTorch Foundation",
        notes="torch.round, which is the round-half-to-even rule chapter 6's quantizer inherits.",
    ),
    Entry(
        doc_id="CVPR 2018 / arXiv:1712.05877",
        id="S019",
        type="conference-paper",
        publisher="IEEE / CVF",
        year=2018,
        notes="Jacob et al., Quantization and Training of Neural Networks for Efficient "
        "Integer-Arithmetic-Only Inference. Venue and year come from the doc_id label rather than "
        "from a quote, so they are recorded as an attribute of the work and not as evidence.",
    ),
    Entry(
        doc_id="CACM April 2009",
        id="S020",
        type="journal-article",
        publisher="Association for Computing Machinery",
        year=2009,
        notes="Williams, Waterman and Patterson, Roofline: An Insightful Visual Performance Model "
        "for Multicore Architectures. The figure chapter 3 draws is this paper's device. Venue and "
        "date are stated in the doc_id label rather than read off the fetched page.",
    ),
    Entry(
        doc_id="arXiv:1804.03209",
        id="S021",
        type="preprint",
        publisher="arXiv",
        year=2018,
        notes="Warden, Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition. The "
        "year is read from the document's own arXiv stamp, which V-05-11 quotes. No authors field "
        "appears, because no recorded quote includes the author line. Both records carry licence "
        "statements, and both are about data rather than about this paper: V-05-07 says the Speech "
        "Commands corpus is CC BY 4.0, V-05-09 says LibriSpeech is too. The second is this paper "
        "describing somebody else's corpus, which is why this registry's licence field sits on "
        "the OpenSLR entry and not on this one.",
    ),
    Entry(
        doc_id="OpenSLR 12",
        id="S022",
        type="corpus-page",
        publisher="OpenSLR",
        licence="CC BY 4.0",
        notes="The distribution page for LibriSpeech. T4: corroboration only, because "
        "a page that hands out a dataset is not a description of it. Its recorded quote names the "
        "16 kHz storage rate and the preparers and says nothing about a licence, so the licence "
        "field above rests on V-05-09, a peer-reviewed paper about a third party's corpus, and "
        "not on this page. That makes it a second-hand licence attribution; the corpus's own terms "
        "page would replace it.",
    ),
    Entry(
        doc_id="FCCM 2025 Artifact Evaluation Guidelines",
        id="S023",
        type="conference-webpage",
        publisher="IEEE CS TPDS / FCCM",
        year=2025,
        notes="What a reusable artifact has to contain, which is the standard chapter 10 writes "
        "against.",
    ),
    Entry(
        doc_id="Digilent Product Catalog",
        id="S024",
        type="product-catalogue",
        publisher="Digilent, Inc.",
        notes="No url is recorded, because V-03-04 is unresolved and its notes say a price page is "
        "corroborating only and never becomes a verified quantity. Registered so that the citation "
        "resolves and the absence stays visible: the entry rule in scripts/verify_integrity.py "
        "fails any registry entry with an empty url that supports a verified record, so an "
        "unlocatable source cannot quietly accumulate evidence.",
    ),
    Entry(
        doc_id="Pmod I2S2 Reference Manual",
        id="S025",
        type="vendor-guide",
        publisher="Digilent, Inc.",
        notes="Read from a distributor mirror (media.digikey.com) of the Digilent manual.",
    ),
    Entry(
        doc_id="ACM FPGA 2017 / arXiv:1612.07119",
        legacy_id="R01-02",
        type="conference-paper",
        publisher="ACM",
        year=2017,
        notes="Same work as the legacy FINN entry, which book/chapter01.md cites by its R01-02 id. "
        "The legacy id is kept and this row adds the doc_id alias that lets a record resolve to "
        "it.",
    ),
    Entry(
        doc_id="UG1089 (v1.4)",
        legacy_id="R01-04",
        type="vendor-guide",
        publisher="Advanced Micro Devices, Inc.",
        year=2023,
        notes="Same work as the legacy KV260 user-guide entry, which carries the publication year.",
    ),
    Entry(
        doc_id="Interspeech 2020 / arXiv:2004.08531",
        legacy_id="R01-05",
        type="conference-paper",
        publisher="ISCA",
        year=2020,
        notes="Same work as the legacy MatchboxNet entry. The doc_id names both the venue and the "
        "preprint, which is one work with two urls and not two sources.",
    ),
]


@dataclass
class Report:
    """The rendered registry plus its verdict on whether it covers the evidence set."""

    document: dict[str, Any]
    labels: int = 0
    exempt: int = 0
    unmapped: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    tier_split: list[str] = field(default_factory=list)
    no_url: list[str] = field(default_factory=list)
    bad_exempt: list[str] = field(default_factory=list)


def group_by_doc_id(doc: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for rec in records(doc):
        groups.setdefault(str(rec.get("doc_id", "")), []).append(rec)
    return groups


def first_title_or_url(groups: dict[str, list[dict[str, Any]]], doc_id: str, key: str) -> str:
    """The value of key on the earliest record citing doc_id, or an empty string.

    Deliberately first rather than most-common: a document whose records disagree about its own
    title is a finding, and a generator that averaged it away would hide the disagreement.
    """
    for rec in groups.get(doc_id, []):
        value = rec.get(key)
        if value:
            return str(value)
    return ""


def render(legacy: dict[str, Any], doc: dict[str, Any]) -> Report:
    groups = group_by_doc_id(doc)
    legacy_by_id = {str(s.get("id")): s for s in legacy.get("sources", [])}
    status_of = {str(r["id"]): str(r.get("status")) for r in records(doc)}
    out = Report(document={})
    out.labels = len(groups)
    out.exempt = len([d for d in groups if is_exempt(d)])

    #: An exempt label is a claim about why no document is cited, so it can be read back off the
    #: record that makes it. 'Derived from' asserts that the inputs sit elsewhere in this file,
    #: which is worth nothing on a record with no value to have been derived from them. 'n/a' and
    #: 'no primary source found' both assert that there is no answer yet, which a record carrying
    #: a value contradicts by existing. Without this, the exemption is a way to opt out of the
    #: registry by choosing a particular string, which is the loophole Issue #20 is about.
    for rec in records(doc):
        rid = str(rec.get("id"))
        did = str(rec.get("doc_id", ""))
        status = str(rec.get("status"))
        value = str(rec.get("value", "")).strip()
        if did.startswith(EXEMPT_PREFIXES) and not value:
            out.bad_exempt.append(
                f"{rid}: doc_id {did!r} claims a derivation, and the record carries no value to "
                "have been derived"
            )
        elif did in EXACT_EXEMPT and (status != "unresolved" or value):
            out.bad_exempt.append(
                f"{rid}: doc_id {did!r} states that no source exists, yet the record is "
                f"{status!r} with value {value!r}. A number with no source is a finding about the "
                "search, not an exemption from the registry"
            )

    sources: list[dict[str, Any]] = []
    claimed_ids: set[str] = set()
    used_legacy: set[str] = set()

    for entry in SPEC:
        key = entry.legacy_id or entry.doc_id
        ids: list[str] = []
        tiers: list[str] = []
        accesses: list[str] = []
        title = ""
        url = ""
        for did in (entry.doc_id, *entry.aliases):
            recs = groups.get(did)
            if not recs:
                out.stale.append(f"{key}: spec cites doc_id {did!r}, which no record uses any more")
                continue
            claimed_ids.add(did)
            ids.extend(str(r["id"]) for r in recs)
            tiers.extend(str(r.get("source_tier")) for r in recs)
            accesses.extend(str(r["access"]) for r in recs if r.get("access"))
            title = title or first_title_or_url(groups, did, "title")
            url = url or first_title_or_url(groups, did, "url")
        supported = sorted(set(ids))
        observed = sorted(set(tiers))
        if len(observed) > 1:
            out.tier_split.append(
                f"{key}: {len(supported)} records spread over tiers {observed}; the tier is a "
                f"property of the claim being made, so check before comparing two of them"
            )
        if not url:
            statuses = sorted({status_of[i] for i in supported})
            if statuses and statuses != ["unresolved"]:
                out.no_url.append(
                    f"{key}: registered without a url yet supports statuses {statuses}"
                )

        if entry.legacy_id:
            base = dict(legacy_by_id.get(entry.legacy_id) or {})
            base["doc_ids"] = [entry.doc_id, *entry.aliases]
            base["claims_supported"] = supported
            if entry.notes:
                base["notes"] = entry.notes
            used_legacy.add(entry.legacy_id)
            sources.append(base)
            continue

        if not entry.id or not NEW_ID_PATTERN.match(entry.id):
            raise ValueError(
                f"spec row for {entry.doc_id!r} needs an id in the S<NNN> form, got {entry.id!r}"
            )
        row: dict[str, Any] = {
            "id": entry.id,
            "doc_ids": [entry.doc_id, *entry.aliases],
            "title": entry.title or title or entry.doc_id,
            "url": url,
            "access": accesses[0] if len(set(accesses)) == 1 else sorted(set(accesses)),
            "type": entry.type,
            "publisher": entry.publisher,
            "tiers_observed": observed,
        }
        if entry.year is not None:
            row["year"] = entry.year
        if entry.authors is not None:
            row["authors"] = entry.authors
        if entry.licence is not None:
            row["licence"] = entry.licence
        row["claims_supported"] = supported
        if entry.notes:
            row["notes"] = entry.notes
        sources.append(row)

    # Legacy entries no record cites keep their shape, with an explicit empty doc_ids so that
    # "checked, nothing cites it" is distinguishable from "not checked".
    for sid, base in legacy_by_id.items():
        if sid in used_legacy or not LEGACY_ID_PATTERN.match(sid):
            continue
        row = dict(base)
        row["doc_ids"] = []
        row.setdefault("claims_supported", [])
        sources.append(row)

    sources.sort(key=lambda s: str(s.get("id")))
    cited = {d for d in groups if not is_exempt(d)}
    out.unmapped = sorted(cited - claimed_ids)
    out.document = {
        "version": REGISTRY_VERSION,
        "last_updated": str(doc.get("generated_utc", ""))[:10],
        "id_scheme": ID_SCHEME,
        "doc_id_note": DOC_ID_NOTE,
        "sources": sources,
    }
    return out


def serialise(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str]) -> int:
    args = list(argv)
    write = "--write" in args
    for flag in ("--write", "--check"):
        while flag in args:
            args.remove(flag)
    if args:
        print(f"build_source_index: unknown argument: {args[0]}", file=sys.stderr)
        return 2

    doc = load_claims(CLAIMS_PATH)
    legacy = json.loads(INDEX_PATH.read_text(encoding="utf-8")) if INDEX_PATH.exists() else {}
    out = render(legacy, doc)
    text = serialise(out.document)
    entries = len(out.document["sources"])

    on_disk = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
    if write:
        INDEX_PATH.write_text(text, encoding="utf-8", newline="\n")
        state = "wrote"
    else:
        state = "clean" if on_disk == text else "DRIFT"

    print(
        f"{state}  docs/source_index.json  {entries} entries; {out.labels} doc_id labels in "
        f"{len(records(doc))} records, {out.exempt} of them arithmetic or absence labels"
    )
    for line in out.unmapped:
        print(f"  UNMAPPED  cited by a record, registered nowhere: {line!r}")
    for line in out.stale:
        print(f"  STALE     {line}")
    for line in out.no_url:
        print(f"  NO-URL    {line}")
    for line in out.tier_split:
        print(f"  TIERS     {line}")
    for line in out.bad_exempt:
        print(f"  EXEMPT    {line}")

    if state == "DRIFT":
        diff = [
            line
            for line in difflib.unified_diff(
                on_disk.splitlines(), text.splitlines(), lineterm="", n=0
            )
            if line[:1] in "+-" and not line.startswith(("---", "+++"))
        ]
        print(f"FAIL: docs/source_index.json differs from its spec in {len(diff)} line(s)")
        for line in diff[:8]:
            print("   ", line[:160])
        print("    run: make render-registry")
        return 1
    if out.unmapped or out.stale or out.no_url or out.bad_exempt:
        print("FAIL: the registry does not cover the evidence set; see the lines above")
        return 1
    print("PASS: every cited document is registered, and every registered label is cited")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
