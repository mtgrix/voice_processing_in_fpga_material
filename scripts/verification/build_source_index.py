#!/usr/bin/env python3
"""Regenerate docs/source_index.json from its curated spec plus claims.json.

The registry has two halves. Which documents exist, what they are called, who publishes them,
what licence their content carries and what a reader should be warned about: that is curated, and
it lives in SPEC below. Which verification records rest on each document: that is derived, from
the doc_id field of every record in claims.json, and it must never be typed by hand -- a hand-kept
list of 103 records across 30 documents rots the first time a chapter adds one.

So this file is the curated half in full, and every row of docs/source_index.json is built from
it. The five legacy R01-NN rows are in SPEC too, which is what makes that sentence true: until
Issue #42 they were lifted off the file being rendered and written back, so the registry was
partly hand-maintained and an edit to one of those five rows showed no drift.

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

Curated and derived columns are different kinds of thing. Curated here: type, publisher, title,
url, year, authors, authors_bibtex, pages, venue, bibtex_entry, licence, topics,
research_note_path, notes. Derived from claims.json: doc_ids, claims_supported, access,
tiers_observed. The rendering writes them in one fixed order, the order the S rows have always
used, so that adding a column moves five rows in the diff rather than thirty. A title or url written
in SPEC overrides the citing record's own field, and the five legacy rows do so deliberately --
their curated spellings differ from what their records name (a different docs.amd.com form, an arXiv
abstract rather than the same paper's pdf). Reconciling those pairs is Issue #40's work, not this
file's.
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
REGISTRY_VERSION = "1.3.0"

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

    #: The doc_id label this row answers, plus any others in `aliases`.
    doc_id: str
    #: What kind of document this is, from the vocabulary the tier protocol uses. Not a free field:
    #: build_bibliography.py maps these to BibTeX entry types and refuses an unknown spelling.
    type: str
    #: Who issued it. None for a paper whose registry row names people instead, which is the case
    #: for the two legacy rows that predate the publisher column.
    publisher: str | None = None
    #: The registry id, in S<NNN> form. A row carrying `legacy_id` keeps its old id and leaves this
    #: None, so the two are alternatives rather than a pair.
    id: str | None = None
    aliases: tuple[str, ...] = ()
    #: Overrides the title on the citing record. Left None wherever the record's own title is right.
    title: str | None = None
    url: str | None = None
    #: For a reader: the abbreviated author line a citation shows.
    authors: str | None = None
    #: For book/references.bib: the author field in BibTeX syntax, where "and" separates people and
    #: double braces hold up a corporate name. Separate from `authors` because citeproc shortens a
    #: ten-name list for print and a .bib that lost four of those names would be wrong.
    authors_bibtex: str | None = None
    year: int | None = None
    licence: str | None = None
    #: The page range, in BibTeX's en-dash form (65--74).
    pages: str | None = None
    #: Where the work appeared -- a journal, a proceedings, or an issuing body. What the .bib calls
    #: that field depends on the entry type, so one column feeds journal, booktitle and
    #: organization rather than three columns that must be kept consistent by hand.
    venue: str | None = None
    #: The BibTeX entry type where it should not be inferred from `type`. Set on the five legacy
    #: rows, three of which the ported project cited as articles and one as a manual.
    bibtex_entry: str | None = None
    #: Subject labels. A claim about what a document covers, which is why no record can supply it.
    topics: tuple[str, ...] = ()
    #: The research note this document was worked through in. verify_integrity.py checks the file
    #: exists; whether the note is about this document is Issue #40.
    research_note_path: str | None = None
    legacy_id: str | None = None
    notes: str | None = None


#: The documents the evidence set cites. Ordering is by id and fixes the S0NN numbering, so it is
#: not an arbitrary list: a number that moves between runs would make every diff unreadable.
#: Where records disagree about the same work, the notes say so instead of the generator
#: averaging the disagreement away.
SPEC: list[Entry] = [
    # The five rows that came from the ported project's R01-NN registry, and the only five whose
    # registry id is not an S number. Their titles, urls and author lines are transcribed from
    # docs/source_index.json and book/references.bib as they stood; their `type` is the one the
    # other 25 rows use, which is the single value this patch re-decides.
    Entry(
        doc_id="R01-01",
        legacy_id="R01-01",
        type="vendor-whitepaper",
        title="NVIDIA Jetson AGX Orin Architecture Whitepaper",
        url="https://developer.nvidia.com/embedded/learn/jetson-agx-orin-architecture-whitepaper",
        authors="NVIDIA Corporation",
        authors_bibtex="{{NVIDIA Corporation}}",
        venue="NVIDIA Technical Whitepapers",
        bibtex_entry="article",
        year=2022,
        research_note_path="docs/research_notes/R01_jetson_orin_arch.md",
        topics=(
            "Jetson Orin",
            "Ampere GPU",
            "Tensor Cores",
            "DLA",
            "LPDDR5",
            "nvpmodel",
        ),
        notes="Registered and uncited: no verification record names this whitepaper. The empty "
        "doc_ids and claims_supported lists are that finding, not an omission.",
    ),
    Entry(
        doc_id="ACM FPGA 2017 / arXiv:1612.07119",
        legacy_id="R01-02",
        type="conference-paper",
        publisher="ACM",
        title="FINN: A Framework for Fast, Scalable Binarized Neural Network Inference on FPGAs",
        url="https://doi.org/10.1145/3020078.3021744",
        authors="Yaman Umuroglu et al.",
        authors_bibtex="Umuroglu, Yaman and Rasnayake, Nicholas J and Suda, Naveen and "
        "Preusser, Thomas B and Fraser, Nicholas and Gambardella, Giulio and O'Brien, Matthew "
        "and Liang, Yu and Leong, Philip HW and Blott, Michaela",
        venue="Proceedings of the 2017 ACM/SIGDA International Symposium on Field-Programmable "
        "Gate Arrays (FPGA)",
        pages="65--74",
        bibtex_entry="inproceedings",
        year=2017,
        research_note_path="docs/research_notes/R02_fpga_audio_streaming.md",
        topics=(
            "FINN",
            "FPGA",
            "Streaming Dataflow",
            "Quantized Neural Networks",
            "Initiation Interval",
        ),
        notes="Same work as the legacy FINN entry, which book/chapter01.md cites by its R01-02 id. "
        "The legacy id is kept and this row adds the doc_id alias that lets a record resolve "
        "to it.",
    ),
    Entry(
        doc_id="R01-03",
        legacy_id="R01-03",
        type="conference-paper",
        title="Conformer: Convolution-augmented Transformer for Speech Recognition",
        url="https://arxiv.org/abs/2005.08100",
        authors="Anmol Gulati et al.",
        authors_bibtex="Gulati, Anmol and Qin, James and Chiu, Chung-Cheng and Parmar, Niki and "
        "Zhang, Yu and Yu, Jiahui and Han, Wei and Wang, Shibo and Zhang, Zhengdong and Wu, "
        "Yonghui and others",
        venue="Proc. Interspeech 2020",
        pages="5036--5040",
        bibtex_entry="article",
        year=2020,
        research_note_path="docs/research_notes/R03_quantization_for_speech.md",
        topics=(
            "Conformer",
            "Speech Recognition",
            "Self-Attention",
            "Depthwise Separable Convolution",
            "Streaming ASR",
        ),
        notes="Registered and uncited: chapter 1 explains the Conformer from its architecture, and "
        "no record yet quotes this paper for it.",
    ),
    Entry(
        doc_id="UG1089 (v1.4)",
        legacy_id="R01-04",
        type="vendor-guide",
        publisher="Advanced Micro Devices, Inc.",
        title="AMD Xilinx Kria KV260 Vision AI Starter Kit User Guide",
        url="https://docs.amd.com/v/u/en-US/ug1089-kv260-starter-kit",
        authors="Advanced Micro Devices, Inc.",
        authors_bibtex="{{Advanced Micro Devices, Inc.}}",
        venue="AMD Xilinx",
        bibtex_entry="manual",
        year=2023,
        research_note_path="docs/research_notes/R02_fpga_audio_streaming.md",
        topics=("Kria KV260", "Zynq UltraScale+", "DPU", "AXI-Stream", "PYNQ"),
        notes="Same work as the legacy KV260 user-guide entry, which carries the publication year.",
    ),
    Entry(
        doc_id="Interspeech 2020 / arXiv:2004.08531",
        legacy_id="R01-05",
        type="conference-paper",
        publisher="ISCA",
        title="MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network for Speech "
        "Command Recognition",
        url="https://arxiv.org/abs/2004.08531",
        authors="Somshubra Majumdar et al.",
        authors_bibtex="Majumdar, Somshubra and Ginsburg, Boris",
        venue="Proc. Interspeech 2020",
        pages="3356--3360",
        bibtex_entry="article",
        year=2020,
        research_note_path="docs/research_notes/R03_quantization_for_speech.md",
        topics=(
            "Keyword Spotting",
            "1D Convolution",
            "Time-Channel Separable",
            "Edge Voice",
            "Low Footprint",
        ),
        notes="Same work as the legacy MatchboxNet entry. The doc_id names both the venue and the "
        "preprint, which is one work with two urls and not two sources.",
    ),
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
        doc_id="NeMo Conformer-Transducer Recipe Config",
        id="S026",
        type="source-code",
        publisher="NVIDIA Corporation",
        topics=("Conformer", "Transducer", "ASR recipe", "streaming"),
        notes="The training recipe, and the only place the four size variants of the model family "
        "are tabulated together. Cited at a pinned commit, because a recipe file moves and a "
        "record quoting line 11 of a moving file is true of one day's tree only. Its variant table "
        "overrides five fields and line 6 says so, which is what lets a Small model be read off "
        "the table plus the body.",
    ),
    Entry(
        doc_id="NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config",
        id="S027",
        type="source-code",
        publisher="NVIDIA Corporation",
        topics=("Conformer", "Transducer", "cache-aware streaming", "ASR recipe"),
        notes="The streaming recipe, where the left and right context pair and the look-ahead "
        "formula are written down. The architecture fields of a streaming model are not the "
        "offline model's with a flag turned on: this file sets conv_norm_type to layer_norm where "
        "the offline recipe sets batch_norm, so the two are separate documents and separate "
        "registry rows.",
    ),
    Entry(
        doc_id="NeMo Cache-Aware Streaming FastConformer-Transducer Recipe Config",
        id="S028",
        type="source-code",
        publisher="NVIDIA Corporation",
        topics=("FastConformer", "Transducer", "cache-aware streaming", "ASR recipe"),
        notes="The other streaming recipe in the family, and the one whose checkpoints carry a "
        "published accuracy-against-latency curve. Subsampling 8 rather than 4 and a 9-tap "
        "convolution module rather than 31 are what make its per-frame cost differ from S027's at "
        "equal width.",
    ),
    Entry(
        doc_id="NeMo Conformer English Score Table",
        id="S029",
        type="repository-documentation",
        publisher="NVIDIA Corporation",
        topics=("LibriSpeech", "word error rate", "ASR results"),
        notes="A project's own results table states what that project achieved, so it corroborates "
        "and does not establish, which is the rule the WeNet README row already records. Its value "
        "here is that it names the checkpoints and their look-ahead in milliseconds independently "
        "of the config files, so the look-ahead formula and the catalogue check each other.",
    ),
    Entry(
        doc_id="CUDA Programming Guide v13.4, Advanced Kernel Programming",
        id="S030",
        type="vendor-tool-guide",
        publisher="NVIDIA Corporation",
        url="https://docs.nvidia.com/cuda/cuda-programming-guide/03-advanced/advanced-kernel-programming.html",
        year=2026,
        topics=("CUDA", "SIMT", "warp", "streaming multiprocessor", "memory latency"),
        notes="The current CUDA Programming Guide, which replaced the legacy "
        "cuda-c-programming-guide that NVIDIA's own page says stopped being updated at CUDA 13.0. "
        "Five records sit on it, and all five are about the execution model rather than about the "
        "Orin: the width of a warp, what a divergent branch costs, what switching between warps "
        "costs, what bounds how many warps are resident, and what hides memory latency. That bound "
        "is deferred to the guide's Compute Capabilities tables and is not registered here, so "
        "chapter 3 reasons about lanes without naming a capacity.",
    ),
    Entry(
        doc_id="CUDA Programming Guide v13.4, CUDA Graphs",
        id="S031",
        type="vendor-tool-guide",
        publisher="NVIDIA Corporation",
        url="https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/cuda-graphs.html",
        year=2026,
        topics=("CUDA", "CUDA Graphs", "kernel launch", "host overhead"),
        notes="Read for one sentence: the host driver performs a setup sequence for every kernel "
        "it "
        "issues, and that cost can be a significant fraction of end-to-end time for a short "
        "kernel. "
        "The microsecond cost of a launch on the Orin is in no record here, and chapter 3.2 says "
        "so "
        "rather than repeating the figure that circulates in secondary notes. Both this page and "
        "S030 carry the navbar version v13.4 and the stamp 'Last updated on Sep 09, 2026', which "
        "is "
        "what the doc_id pins: a chapter quoted from a moving online guide is true of one version "
        "of it.",
    ),
    Entry(
        doc_id="PyTorch Tutorials 2.14, Convolution/Batch Norm fuser",
        id="S032",
        type="software-documentation",
        publisher="PyTorch Foundation",
        url="https://docs.pytorch.org/tutorials/intermediate/torch_compile_conv_bn_fuser.html",
        topics=("PyTorch", "operator fusion", "batch normalisation", "torch.compile", "inference"),
        notes="Read for chapter 5's account of what a compiler does to a graph before hardware "
        "sees "
        "it. Three records sit on it: that folding a convolution and a batch norm needs no new "
        "operator and deletes the norm, that the pattern is reachable only because compilation "
        "captures the graph, and that the fold is legal in inference mode alone. The page carries "
        "no "
        "date of its own, so the doc_id pins the version its title prints, 2.14.0, the same "
        "version "
        "string the round-half-to-even record already relies on. The page is a worked example that "
        "says its code is copied from the repository, which is why V-06-09 cites the repository "
        "file for the arithmetic rather than trusting this prose.",
    ),
    Entry(
        doc_id="PyTorch v2.10.0 source, torch/nn/utils/fusion.py",
        id="S033",
        type="source-code",
        publisher="PyTorch Foundation",
        url="https://raw.githubusercontent.com/pytorch/pytorch/v2.10.0/torch/nn/utils/fusion.py",
        topics=("PyTorch", "operator fusion", "batch normalisation", "source code"),
        notes="The implementation behind the tutorial's prose, pinned to a release tag. The pin "
        "matters and is recorded rather than assumed: at this tag the eval-mode guard is an assert "
        "statement, while the development branch has rewritten the same check as a raise, with the "
        "identical message string. A chapter quoting the behaviour is safe across that rewrite; "
        "one "
        "quoting the statement form would not be.",
    ),
    Entry(
        doc_id="Vitis AI Quantizer (vai_q_pytorch) documentation",
        id="S034",
        type="repository-documentation",
        publisher="Xilinx, Inc.",
        url="https://raw.githubusercontent.com/Xilinx/Vitis-AI/77cb9e6ad6749de55cf6de8d4959b1cb4b27020e/src/vai_quantizer/vai_q_pytorch/doc/Quant_Config.md",
        topics=("Vitis AI", "quantization", "calibration", "DPU", "configuration"),
        notes="The configuration document of the quantizer that produces the DPU's integer graphs, "
        "read from the vendor repository at a commit rather than a branch. Three records come from "
        "it: the documented estimators for a scale, the option combinations the tool refuses "
        "outright, and the instruction that layer names can only be chosen after calibration has "
        "run. T2 for the reason docs/WEB_SEARCH_PROTOCOL.md section 2 gives for the other Vitis AI "
        "material: a tool reference, not a datasheet. The repository still publishes under the "
        "Xilinx organisation name, so that is the publisher recorded here even though the "
        "documents "
        "now carry AMD branding.",
    ),
    Entry(
        doc_id="Proceedings of the IEEE 105(12) / arXiv:1703.09039",
        id="S035",
        type="journal-article",
        publisher="IEEE",
        url="https://ieeexplore.ieee.org/document/8114708",
        authors="Vivienne Sze et al.",
        authors_bibtex="Sze, Vivienne and Chen, Yu-Hsin and Yang, Tien-Ju and Emer, Joel",
        venue="Proceedings of the IEEE",
        pages="2295--2329",
        bibtex_entry="article",
        year=2017,
        research_note_path="docs/research_notes/R04_sota_speech_hardware_acceleration.md",
        topics=("DNN accelerator", "dataflow", "weight stationary", "row stationary", "energy"),
        notes="Sze, Chen, Yang and Emer, Efficient Processing of Deep Neural Networks: A Tutorial "
        "and Survey. Chapter 3's dataflow taxonomy and its energy ladder are this paper's, so the "
        "doc_id carries both the journal issue and the arXiv stamp. The R04 transcription prints "
        "the taxonomy as WS / IS / OS; the survey itself tabulates WS / OS / No-Local-Reuse / "
        "Row-Stationary, and the book keeps the claim to the triad R04 actually quotes.",
    ),
    Entry(
        doc_id="ICML 2021 / arXiv:2101.01321",
        id="S036",
        type="conference-paper",
        publisher="PMLR",
        url="https://arxiv.org/abs/2101.01321",
        authors="Sehoon Kim et al.",
        authors_bibtex="Kim, Sehoon and Gholami, Amir and Yao, Zhewei and Mahoney, Michael W and "
        "Keutzer, Kurt",
        venue="Proceedings of the 38th International Conference on Machine Learning",
        pages="5506--5518",
        bibtex_entry="inproceedings",
        year=2021,
        research_note_path="docs/research_notes/R04_sota_speech_hardware_acceleration.md",
        topics=("BERT", "integer arithmetic", "softmax", "transformer", "quantization"),
        notes="I-BERT: Integer-only BERT Quantization. The arXiv id 2101.01321 was verified via "
        "the arXiv API against the title; the archive's copy in docs/papers is a different "
        "paper (arXiv 2101.01304, secret sharing) and is superseded. The PMLR record is "
        "pages 5506-5518 in volume 139, confirmed by extracting every kim21x entry from the "
        "volume page. Chapter 7's integer-only softmax path is this paper's.",
    ),
    Entry(
        doc_id="ASP-DAC 2026 (ConfASR)",
        id="S037",
        type="conference-paper",
        publisher="IEEE",
        url="https://doi.org/10.1109/ASP-DAC66049.2026.11420567",
        venue="2026 31st Asia and South Pacific Design Automation Conference (ASP-DAC)",
        bibtex_entry="inproceedings",
        year=2026,
        authors="Malte Wabnitz and Max Nilovic and Finn Scholz and Dominik Friedrich and "
        "Christian Lanius and Jie Lou and Tobias Gemmeke",
        pages="147--153",
        research_note_path="docs/research_notes/R04_sota_speech_hardware_acceleration.md",
        topics=("Conformer", "streaming ASR", "silicon", "FDSOI", "ring buffer"),
        notes="ConfASR: A Conformer Block Accelerator for Speech Recognition Optimized for Edge "
        "Devices. No open-access full text exists: the title, venue, page range and DOI above were "
        "verified against Crossref and Semantic Scholar on 2026-09-17 (Issue #85), which corrected "
        "a title, a venue and a DOI that did not belong to this paper. Every ConfASR sentence "
        "chapter 9 quotes is a sentence of the abstract, retrieved from the publisher's metadata, "
        "and is transcribed in full in research note R04 section 3.2. One record on this label, "
        "V-07-25, is unresolved: a claim about dedicated left-context buffering that the previous "
        "pass attributed to this paper could not be found in any available text, so chapter 9 now "
        "presents the ring buffer as this book's own design.",
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


def render(doc: dict[str, Any]) -> Report:
    groups = group_by_doc_id(doc)
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

    for entry in SPEC:
        #: A row for a registered-but-uncited document puts its registry id in doc_id, as it has
        #: no doc_id label of its own: no record quotes the document, so nothing named it. Treating
        #: that id as a label would make STALE fire on a row whose whole point is that it is unused.
        uncited = bool(entry.legacy_id) and entry.doc_id == entry.legacy_id
        labels = entry.aliases if uncited else (entry.doc_id, *entry.aliases)
        key = entry.legacy_id or entry.doc_id
        ids: list[str] = []
        tiers: list[str] = []
        accesses: list[str] = []
        title = ""
        url = ""
        for did in labels:
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
        url = entry.url or url
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

        row_id = entry.id or entry.legacy_id
        wanted = NEW_ID_PATTERN if entry.id else LEGACY_ID_PATTERN
        if not row_id or not wanted.match(row_id):
            raise ValueError(
                f"spec row for {entry.doc_id!r} needs an id matching {wanted.pattern!r}, "
                f"got {row_id!r}"
            )
        row: dict[str, Any] = {
            "id": row_id,
            "doc_ids": list(labels),
            "title": entry.title or title or entry.doc_id,
            "url": url,
            "access": accesses[0] if len(set(accesses)) == 1 else sorted(set(accesses)),
            "type": entry.type,
        }
        # Key order is the one the S rows have always been written in, with the five new columns
        # placed beside their relatives rather than appended. A rendering that reordered the
        # existing rows would put 25 unchanged sources in the diff, and the five rows that did
        # change would be impossible to pick out of it.
        if entry.publisher is not None:
            row["publisher"] = entry.publisher
        row["tiers_observed"] = observed
        for name in (
            "year",
            "authors",
            "authors_bibtex",
            "licence",
            "pages",
            "venue",
            "bibtex_entry",
            "research_note_path",
        ):
            value = getattr(entry, name)
            if value is not None:
                row[name] = value
        if entry.topics:
            row["topics"] = list(entry.topics)
        row["claims_supported"] = supported
        if entry.notes:
            row["notes"] = entry.notes
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
    out = render(doc)
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
