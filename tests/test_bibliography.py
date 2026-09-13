"""The bibliography is a rendering, and every citation key in the manuscript has to name a row.

Issue #42 replaced five hand-written entries in `book/references.bib` with thirty generated ones,
so two things need holding down that nobody had to hold before.

The first is drift. The .bib is derived from docs/source_index.json, which is itself half derived
from docs/verification/claims.json, so a hand edit anywhere in that chain makes the printed
reference list disagree with the evidence behind the claim it documents.

The second is the citation path itself. A chapter names a source with a Pandoc marker, `[@S009]`,
and Pandoc resolves that against the .bib when it builds the PDF -- which CI never does, because
the checks job installs Python and no TeX distribution (Issue #29). So the only thing standing
between a mistyped key and a reference list that silently omits a source is a Python check, and this
file is where that check is proved. Most of it is proved with fabricated manuscripts rather than the
real one: `check_citation_keys_resolve()` returns nothing today because the manuscript holds no
markers at all, and a check that has only ever seen good input is not known to work, only known to
be quiet.

The .bib is parsed here by regex, not by a BibTeX library. A library would test the renderer against
itself -- the same parse, the same assumptions -- while a reader written to the shape Pandoc needs
checks what a reader actually sees: that braces balance, that a key is where a key goes, that a
field name is one citeproc will read.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "scripts" / "verification"

# The renderer sits on mypy_path in pyproject.toml, so it imports by name. The integrity script
# does not: it lives one directory up in scripts/, where mypy would resolve it under a module name
# nothing else in the repository uses. importlib is how tests/test_result_log_gate.py reaches the
# same file, for the reason given there -- a plain import mypy cannot see is a type error, not a
# shortcut.
sys.path.insert(0, str(VERIFICATION))
import build_bibliography as bibliography  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "verify_integrity_under_test", ROOT / "scripts" / "verify_integrity.py"
)
assert _spec is not None and _spec.loader is not None
verify_integrity: ModuleType = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verify_integrity)

INDEX: dict[str, Any] = json.loads(bibliography.INDEX_PATH.read_text(encoding="utf-8"))
SOURCES: list[dict[str, Any]] = INDEX["sources"]
BY_ID: dict[str, dict[str, Any]] = {str(row["id"]): row for row in SOURCES}
IDS: set[str] = set(BY_ID)
TEXT: str = bibliography.BIB_PATH.read_text(encoding="utf-8")

#: One entry: its type, its key, and its field lines. Body lines are indented by the renderer, and
#: the closing brace is never indented, which is what lets a body be matched without a parser.
ENTRY_PATTERN = re.compile(r"^@(\w+)\{([^,]+),\n((?: .*\n)*)\}", re.MULTILINE)
FIELD_PATTERN = re.compile(r"^  (\w+) += +(.+),$", re.MULTILINE)

#: The four rows whose documents the evidence set quotes with no author in any captured quote.
#: Pinned as a set, like the registry pins its exemptions: a fifth authorless row means either a new
#: source was registered without an author, or a quote started naming people. Either is a decision.
AUTHORLESS = {"S019", "S020", "S021", "S023"}


def entries() -> list[tuple[str, str, dict[str, str]]]:
    """(entry type, key, raw field values) for every entry in the committed file."""
    out = []
    for entry_type, key, body in ENTRY_PATTERN.findall(TEXT):
        fields = dict(FIELD_PATTERN.findall(body))
        out.append((entry_type, key, fields))
    return out


def value_of(fields: dict[str, str], name: str) -> str:
    """A field's value with its delimiting brace pair removed, which is what a reader sees."""
    raw = fields[name]
    assert raw.startswith("{") and raw.endswith("}"), f"{name} is not braced: {raw!r}"
    return raw[1:-1]


def manuscript(tmp_path: Path, body: str) -> list[Path]:
    """A one-file manuscript in a temporary directory, for driving the key check."""
    (tmp_path / "chapter99.md").write_text(body, encoding="utf-8")
    return [tmp_path]


class TestTheBibliographyIsTheRendering:
    def test_committed_file_matches_the_registry(self) -> None:
        assert bibliography.render(INDEX).text == TEXT, (
            "book/references.bib was edited by hand; run make render-bib"
        )

    def test_every_row_has_exactly_one_entry(self) -> None:
        keys = [key for _, key, _ in entries()]
        assert len(keys) == len(SOURCES), f"{len(keys)} entries for {len(SOURCES)} rows"
        assert len(set(keys)) == len(keys), "two entries share a key, so one cites the wrong work"
        assert set(keys) == IDS, "the bibliography and the registry name different sources"

    def test_entry_precedes_its_doc_id_comment(self) -> None:
        """The comment above an entry is how a reader gets from a printed reference back to a quote.

        It is a comment rather than a note field because citeproc prints notes into the reference
        list, and this join belongs to the repository, not to the book.
        """
        lines = TEXT.splitlines()
        for index, line in enumerate(lines):
            if not line.startswith("@"):
                continue
            key = line[1:].split("{")[1].rstrip(",")
            comment = lines[index - 1]
            assert comment.startswith(f"% {key}:"), f"{key} is not preceded by its own comment"
            row = BY_ID[key]
            if row["doc_ids"]:
                for label in row["doc_ids"]:
                    assert repr(label) in comment, f"{key}'s comment lost the label {label!r}"
            else:
                assert "uncited" in comment, f"{key} is uncited and its comment does not say so"


class TestEntryShape:
    def test_types_are_ones_citeproc_reads(self) -> None:
        allowed = set(bibliography.ENTRY_TYPE_BY_TYPE.values())
        allowed |= {str(row.get("bibtex_entry")) for row in SOURCES if row.get("bibtex_entry")}
        assert {t for t, _, _ in entries()} <= allowed, "an entry type nobody mapped produced this"

    def test_braces_balance_in_every_field(self) -> None:
        for _, key, fields in entries():
            for name, raw in fields.items():
                assert raw.count("{") == raw.count("}"), (
                    f"{key}.{name} has unbalanced braces: {raw}"
                )

    def test_no_field_is_empty(self) -> None:
        for _, key, fields in entries():
            for name, raw in fields.items():
                assert value_of(fields, name).strip(), f"{key}.{name} renders as nothing"

    def test_venues_use_the_field_the_type_expects(self) -> None:
        for entry_type, key, fields in entries():
            row = BY_ID[key]
            if not row.get("venue"):
                continue
            expected = bibliography.VENUE_FIELD_BY_ENTRY[entry_type]
            assert expected in fields, f"{key} is @{entry_type} and dropped its venue"
            assert value_of(fields, expected) == str(row["venue"])

    def test_urls_are_the_registry_urls(self) -> None:
        for _, key, fields in entries():
            if BY_ID[key].get("url"):
                assert value_of(fields, "url") == str(BY_ID[key]["url"])


class TestTitlesAreProtectedFromTheStyle:
    """The IEEE CSL lowercases the title variable, which is wrong for a product or a module name.

    An unprotected title turned "NVIDIA Jetson AGX Orin Architecture Whitepaper" into "NVIDIA jetson
    AGX orin architecture whitepaper" and "torch.round" into "Torch.round". Verified against pandoc
    and book/ieee.csl, not reasoned about.
    """

    def test_every_title_carries_its_own_brace_pair(self) -> None:
        for _, key, fields in entries():
            raw = fields["title"]
            assert raw.startswith("{{") and raw.endswith("}}"), f"{key} title is not braced: {raw}"
            assert value_of(fields, "title") == "{" + str(BY_ID[key]["title"]) + "}"


class TestAuthorDerivation:
    def test_authorless_rows_are_the_known_four(self) -> None:
        missing = {key for _, key, fields in entries() if "author" not in fields}
        assert missing == AUTHORLESS, f"the set of authorless entries changed: {missing}"

    def test_corporate_authors_are_not_reordered(self) -> None:
        """A corporate name needs its own brace pair, or BibTeX reads "Xilinx, Inc." as a person."""
        for _, key, fields in entries():
            row = BY_ID[key]
            author = fields.get("author")
            if author is None or row.get("authors_bibtex"):
                continue
            assert author == "{{{" + str(row["publisher"]) + "}}}", (
                f"{key} derived its author from the publisher; check the braces"
            )

    def test_a_publisher_that_is_the_author_is_printed_once(self) -> None:
        for _, key, fields in entries():
            author, publisher = fields.get("author"), fields.get("publisher")
            if author and publisher:
                assert author != "{{" + value_of(fields, "publisher") + "}}", (
                    f"{key} prints the same body as author and publisher"
                )

    def test_a_row_with_people_keeps_their_full_list(self) -> None:
        for _, key, fields in entries():
            explicit = BY_ID[key].get("authors_bibtex")
            if explicit:
                assert value_of(fields, "author") == str(explicit)


class TestTheFiveMigratedWorksKeptTheirCitationData:
    """The values the hand-written bibliography carried, asserted against the generated one.

    These five rows are the reason Issue #42 started with a refactor: they held the book's only real
    author lists, page ranges and venues, and they were the only rows the registry generator did not
    own. Rendering a bibliography on top of that would have meant one hand-maintained file feeding
    another, so the hand-maintenance moved into the generator's SPEC first. This test is the check
    that nothing was lost in the move.

    Titles are deliberately not asserted. The registry records a document's own title and the old
    file used a shortened or sentence-cased variant in places; whose spelling wins is Issue #40.
    """

    #: Transcribed from `git show HEAD:book/references.bib`, the last hand-written version, read
    #: rather than remembered. The old keys are named too, because a reader wondering whether
    #: umuroglu2017finn survived should find that answered here rather than in git log. These are
    #: the values that had to survive, not a full diff: the registry also gave FINN a publisher and
    #: a doi the hand-written entry never carried.
    MIGRATED: dict[str, dict[str, object]] = {
        "R01-01": {
            "was": "nvidia2022orin",
            "author": "{{NVIDIA Corporation}}",
            "journal": "NVIDIA Technical Whitepapers",
            "year": "2022",
        },
        "R01-02": {
            "was": "umuroglu2017finn",
            "booktitle": (
                "Proceedings of the 2017 ACM/SIGDA International Symposium on "
                "Field-Programmable Gate Arrays (FPGA)"
            ),
            "pages": "65--74",
            "year": "2017",
        },
        "R01-03": {
            "was": "gulati2020conformer",
            "journal": "Proc. Interspeech 2020",
            "pages": "5036--5040",
            "year": "2020",
        },
        "R01-04": {
            "was": "xilinx2023kv260",
            "author": "{{Advanced Micro Devices, Inc.}}",
            "organization": "AMD Xilinx",
            "year": "2023",
        },
        "R01-05": {
            "was": "majumdar2020matchboxnet",
            "journal": "Proc. Interspeech 2020",
            "pages": "3356--3360",
            "year": "2020",
        },
    }

    def test_field_values_survived_the_migration(self) -> None:
        by_key = {key: fields for _, key, fields in entries()}
        for registry_id, expected in self.MIGRATED.items():
            fields = by_key[registry_id]
            for name, want in expected.items():
                if name == "was":
                    continue
                assert value_of(fields, name) == str(want), f"{registry_id}.{name} changed"

    def test_the_two_long_author_lists_are_still_long(self) -> None:
        """A citeproc display name shortens to "et al."; a .bib that lost names would do the same.""

        Quietly, in both cases: the style is what decides how many names a reader ever sees.
        """
        by_key = {key: fields for _, key, fields in entries()}
        finn = value_of(by_key["R01-02"], "author").split(" and ")
        conformer = value_of(by_key["R01-03"], "author").split(" and ")
        assert len(finn) == 10, f"FINN's author list is {len(finn)} names, not 10"
        assert finn[0] == "Umuroglu, Yaman" and finn[-1] == "Blott, Michaela"
        assert len(conformer) == 11, f"Conformer's list is {len(conformer)} entries, not 11"
        assert conformer[-1] == "others", "the et-al marker is part of the author line, not styling"


class TestManuscriptKeysResolve:
    def test_the_real_manuscript_is_clean(self) -> None:
        assert verify_integrity.check_citation_keys_resolve() == []

    def test_the_manuscript_dirs_exist_to_be_checked(self) -> None:
        """Guards the vacuous pass above: no directory, no markers, no errors, and no meaning."""
        for name in ("book-en", "book"):
            assert list((ROOT / name).glob("*.md")), f"{name} holds no manuscript files any more"

    def test_a_key_that_names_a_row_is_accepted(self, tmp_path: Path) -> None:
        body = "Orin delivers 275 TOPS [@S009] and the K26 module 20 GB/s [@S007].\n"
        assert verify_integrity.check_citation_keys_resolve(manuscript(tmp_path, body)) == []

    def test_an_invented_key_is_refused_with_its_line(self, tmp_path: Path) -> None:
        body = "First line.\nFINN streams dataflow [@umuroglu2017finn].\n"
        errors = verify_integrity.check_citation_keys_resolve(manuscript(tmp_path, body))
        assert len(errors) == 1, errors
        assert "chapter99.md:2" in errors[0], "the message must name the line a reader has to fix"
        assert "umuroglu2017finn" in errors[0]

    def test_a_doc_id_written_where_a_key_belongs_is_refused(self, tmp_path: Path) -> None:
        """The likely mistake, since doc_id is the label the evidence records already use."""
        body = "Utilisation is read from the report [@UG440 (v2022.1)].\n"
        errors = verify_integrity.check_citation_keys_resolve(manuscript(tmp_path, body))
        assert len(errors) == 1, errors
        assert "[@UG440" in errors[0]

    def test_a_marker_with_no_key_in_it_is_refused(self, tmp_path: Path) -> None:
        errors = verify_integrity.check_citation_keys_resolve(manuscript(tmp_path, "See [ @ ].\n"))
        assert errors == [], "a spaced marker is not a citation, and pandoc leaves it as text"
        errors = verify_integrity.check_citation_keys_resolve(manuscript(tmp_path, "See [@].\n"))
        assert len(errors) == 1 and "no key in it" in errors[0]

    def test_the_marker_grammar_matches_pandocs(self) -> None:
        """The regexes are the check's real logic, so they are pinned directly."""
        find = verify_integrity.CITATION_KEY.findall
        assert find("[@S019, p. 4]") == ["S019"]
        assert find("[@S009; @S012]") == ["S009", "S012"]
        assert find("[@UG440 (v2022.1)]") == ["UG440"]
        assert find("[@R01-02]") == ["R01-02"], "a hyphen in a key must survive, the ids have one"
        assert verify_integrity.CITATION_MARKER.findall("see [S009] not a citation") == []

    def test_every_hyphenated_registry_id_is_a_usable_key(self) -> None:
        bad = [key for key in IDS if not bibliography.KEY_PATTERN.match(key)]
        assert not bad, f"{bad} cannot be typed into a chapter as a citation"
