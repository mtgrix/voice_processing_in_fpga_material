"""The prose cage has to be proved to rattle, not just shown to be quiet.

Issue #99 added scripts/verification/prose_cage.py, which fails the gate when manuscript prose
carries an evidence code (V-xx-yy), an audit phrase ("the records say", "registered gap"), or a
measured quantity written out as words ("one thousand six hundred" for 1,600). BOOK_PEDAGOGY §8
banned all three in prose; before this tool nothing checked that the ban held. A gate like this
one earns its place only if two opposite things are both demonstrated: that clean prose passes,
and that auditor prose fails -- and fails about the right file, section, kind, and match.

The exemptions get their own tests for the mirror-image reason. Prose cage lines are classified
by split_sections (the same classifier scan_numbers.py uses, so the two cages agree on what a
prose line is): table rows, fenced code, and headings are each a place the cage chooses NOT to
look, and a choice not to look is where a violation can hide. Each exemption is pinned from both
sides -- the shape is exempt, and a violation standing in real prose next to it is still caught.

The word-number parser is the subtle part. Real manuscript prose mixes measured quantities
("over one thousand six hundred muxes"), rhetorical uses ("a few thousand", "a thousand or a
million"), and scale words riding on an Arabic digit that was already checked by scan_numbers
("2.056 million per second", "about 14 million parameters"). The tests below pin all three
classes so the cage leashes what it should and lets what it should pass.

End to end, the baseline lifecycle is walked the way a contributor will meet it: prose that
fails --check, gets recorded by --write-baseline, passes --check, still fails --strict, and
announces itself as repaid debt once the prose is cleaned up.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "verification"))
import prose_cage as cage  # noqa: E402


def kinds(findings: list[dict[str, Any]]) -> list[str]:
    """The violation kinds of a scan, in order."""
    return [r["kind"] for r in findings]


def matches(findings: list[dict[str, Any]], kind: str) -> list[Any]:
    """The match texts of one kind, in order."""
    return [r["match"] for r in findings if r["kind"] == kind]


# ----------------------------------------------------------------- misuse --


def test_inline_code_v_id_is_an_infraction(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text("## 2.1 Sizes\n\nThe L2 is 128 KB (`V-01-01`).\n", encoding="utf-8")
    findings = cage.scan_file(f)
    assert kinds(findings) == ["prose-v"]
    assert findings[0]["match"] == "V-01-01"
    assert findings[0]["section"] == "2.1"  # headings are keyed by their number, like scan_numbers


def test_audit_language_without_v_id_is_an_infraction(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes\n\nThe latency is 40 ms; the records say the rest.\n", encoding="utf-8"
    )
    findings = cage.scan_file(f)
    assert kinds(findings) == ["audit-language"]
    assert findings[0]["match"] == "the records say"


def test_bare_cardinal_two_digit_is_an_infraction(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text("## 2.1 Sizes\n\nThe DSP slices are sixty-four wide.\n", encoding="utf-8")
    findings = cage.scan_file(f)
    assert kinds(findings) == ["word-number"]
    assert findings[0]["match"] == "sixty four"  # canonical, space-joined form
    assert findings[0]["value"] == 64.0


def test_hyphenated_cardinal_is_an_infraction(tmp_path: Path) -> None:
    # Sixteen-bit and forty-two are written with a hyphen for the compound adjective; the
    # word parser splits the hyphen the way a typewriter reader does, and the match is the
    # canonical space-joined phrase.
    f = tmp_path / "chapter04.md"
    f.write_text(
        "## 4.2 Front end\n\nThe sixteen-bit stream feeds forty-two filters.\n", encoding="utf-8"
    )
    findings = cage.scan_file(f)
    assert matches(findings, "word-number") == ["sixteen", "forty two"]


# ------------------------------------------------------------- parser --


def test_parse_cardinal_full_compound() -> None:
    assert cage.parse_cardinal_run("one thousand two hundred and forty eight".split())[1] == 1248.0


def test_parse_cardinal_scaled() -> None:
    assert cage.parse_cardinal_run("two million".split())[1] == 2_000_000.0
    assert cage.parse_cardinal_run("one thousand".split())[1] == 1000.0
    assert cage.parse_cardinal_run("five hundred".split())[1] == 500.0


def test_parse_fraction_article_special_case() -> None:
    # "one one-hundredth" is the article "a" plus the fraction, both ones: the value is
    # 0.01, not 0.02. A bare "one hundredth" is the same 0.01 by the "no digits" rule, and
    # the plural forms are the same fraction as their singulars -- "three hundredths" is
    # 3 x 0.01, not the integer 3.
    assert cage.parse_cardinal_run("one one hundredth".split())[1] == 0.01
    assert cage.parse_cardinal_run("one hundredth".split())[1] == 0.01
    assert cage.parse_cardinal_run("three hundredths".split())[1] == 0.03
    assert cage.parse_cardinal_run("five tenths".split())[1] == 0.5
    assert cage.parse_cardinal_run("twenty thousandths".split())[1] == 0.02


def test_parse_cardinal_point_decimal() -> None:
    assert cage.parse_cardinal_run("one point five".split())[1] == 1.5
    assert cage.parse_cardinal_run("one point five seven".split())[1] == 1.57


def test_parse_cardinal_undershoot_consumed_head() -> None:
    # A run stops at the first word that is not a number word; the tail is untouched.
    words, value = cage.parse_cardinal_run("sixteen stream feeds".split())
    assert words == ["sixteen"]
    assert value == 16.0


def test_cardinal_phrases_ignores_digit_licensed_scale() -> None:
    # "2.056 million" and "14 million" carry their quantity in the Arabic digit, which
    # scan_numbers already cages; "million" there is the unit, not a spelled cardinal.
    phrases = cage.cardinal_phrases("The rate is 2.056 million voices per second.")
    assert phrases == []
    phrases = cage.cardinal_phrases("It costs about 14 million parameters.")
    assert phrases == []


def test_cardinal_phrases_leaves_rhetorical_scales_alone(tmp_path: Path) -> None:
    # A bare scale word -- "a few thousand", "a thousand or a million" -- carries no digit:
    # English keeps these approximations as words, and the measured filter lets them pass.
    # The parser still extracts "thousand" from the first; the filter is what releases it.
    phrases = cage.cardinal_phrases("It takes a few thousand gates.")
    assert [p for p, _, _, _ in phrases] == ["thousand"]
    assert cage.phrase_is_measured("thousand", 1000.0) is False
    phrases = cage.cardinal_phrases("A thousand or a million might do.")
    assert [p for p, _, _, _ in phrases] == ["thousand", "million"]
    assert all(cage.phrase_is_measured(p, v) is False for p, v, _, _ in phrases)
    f = tmp_path / "chapter02.md"
    f.write_text("## 2.1 Sizes\n\nIt takes a few thousand gates.\n", encoding="utf-8")
    assert cage.scan_file(f) == []


def test_phrase_is_measured_rules() -> None:
    assert cage.phrase_is_measured("sixteen", 16.0) is True
    assert cage.phrase_is_measured("sixty four", 64.0) is True
    assert cage.phrase_is_measured("one", 1.0) is False  # convention: words under 13
    assert cage.phrase_is_measured("eighty", 80.0) is True
    assert cage.phrase_is_measured("two", 2.0) is False
    assert cage.phrase_is_measured("thousandth", 0.001) is True  # a fraction is always measured
    assert cage.phrase_is_measured("one point five", 1.5) is True


# -------------------------------------------------------------- content --


def test_patterns_used_in_manuscript() -> None:
    f = Path(ROOT / "book-en" / "preface.md")
    findings = cage.scan_file(f)
    assert "seventy" in matches(findings, "word-number")
    assert "eighty" in matches(findings, "word-number")


def test_third_party_passive_voice_is_not_audit_speak(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes\n\nThe latency is 40 ms and the results were registered in the paper.\n",
        encoding="utf-8",
    )
    assert cage.scan_file(f) == []  # "registered" as a verb is honest prose


# -------------------------------------------------------------- regions --


def test_heading_v_ids_are_not_prose(tmp_path: Path) -> None:
    # A heading is where a citation becomes a legal aid, not evidence-talk: a section whose
    # own heading announces its source leaves the prose clean.
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes (`V-01-01`)\n\n"
        "The L2 is 128 KB, per the table below.\n\n"
        "| Part | KB | Source |\n"
        "| --- | --- | --- |\n"
        "| L2 | 128 | `V-01-01` |\n",
        encoding="utf-8",
    )
    assert cage.scan_file(f) == []


def test_table_rows_are_not_prose(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes\n\nThe L2 is 128 KB.\n\n"
        "| Part | KB | Source |\n"
        "| --- | --- | --- |\n"
        "| L2 | 128 | `V-01-01` |\n",
        encoding="utf-8",
    )
    findings = cage.scan_file(f)
    assert findings == []  # the row's V-id and the real quantity live in the table


def test_fenced_code_is_not_prose(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes\n\nprose\n\n```tikz\n% sixty-four lanes, V-01-01\n```\n\nprose\n",
        encoding="utf-8",
    )
    findings = cage.scan_file(f)
    assert findings == []  # the fence holds labels and geometry, neither of them prose


def test_math_expression_is_stripped_but_tail_is_not(tmp_path: Path) -> None:
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Sizes\n\nThe model declares $W = 64$ sixty-four lanes wide.\n",
        encoding="utf-8",
    )
    findings = cage.scan_file(f)
    assert matches(findings, "word-number") == ["sixty four"]
    assert findings[0]["value"] == 64.0


# ------------------------------------------------------------------ files --


def test_how_to_use_is_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # how-to-use.md teaches the mechanics of the V-id and the traceability table, so its
    # prose lines are the subject matter itself. The skip is enforced where the manuscript
    # is assembled -- main() refuses the filename before any line is scanned -- just as
    # scan_numbers.py skips the same file for the same reason.
    manu = tmp_path / "book-en"
    manu.mkdir()
    (manu / "how-to-use.md").write_text(
        "# How to use\n\nA record reference, such as `V-07-02`, belongs in the table.\n",
        encoding="utf-8",
    )
    (manu / "chapter02.md").write_text("## 2.1 Sizes\n\nThe L2 is 128 KB.\n", encoding="utf-8")
    monkeypatch.setattr(cage, "ROOT", tmp_path)
    monkeypatch.setattr(cage, "BASELINE_PATH", tmp_path / "baseline.json")
    assert cage.main(["--check"]) == 0


# ---------------------------------------------------------- end to end --


@pytest.fixture()
def cage_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A one-file manuscript with every disease, and a baseline path in tmp."""
    manu = tmp_path / "neg.md"
    manu.write_text(
        "## 2.1 Sizes\n\n"
        "The L2 is 128 KB (`V-01-01`). "
        "The records say the SRAM is one hundred sixty kilobytes wide.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cage, "BASELINE_PATH", tmp_path / "baseline.json")
    return manu


def test_baseline_lifecycle(
    cage_fixture: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    manu = cage_fixture

    # 1. Dirty prose, no baseline yet: --check fails and names each violation's kind, match,
    #    file, and section.
    assert cage.main([str(manu), "--check"]) == 1
    out = capsys.readouterr().out
    assert "V-01-01" in out and "the records say" in out and "hundred" in out

    # 2. Recorded as reviewed debt: --write-baseline succeeds and writes the file.
    assert cage.main([str(manu), "--write-baseline"]) == 0
    doc = json.loads(cage.BASELINE_PATH.read_text(encoding="utf-8"))
    assert {e["kind"] for e in doc["entries"]} == {"prose-v", "audit-language", "word-number"}

    # 3. The debt excuses --check but never --strict.
    assert cage.main([str(manu), "--check"]) == 0
    assert cage.main([str(manu), "--strict"]) == 1

    # 4. Cleaning the prose repays the debt, and the stale entry is announced.
    manu.write_text(
        "## 2.1 Sizes\n\nThe L2 is 128 KB (see the table). "
        "The SRAM is 160 KB wide, per the table.\n",
        encoding="utf-8",
    )
    assert cage.main([str(manu), "--check"]) == 0
    assert "no longer needed" in capsys.readouterr().out


def test_real_manuscript_passes_the_committed_baseline() -> None:
    # Pins docs/verification/prose_baseline.json against book-en. If this fails, either new
    # prose carries a V-id, an audit phrase, or a spelled-out quantity, or the baseline lost
    # an entry it needs. --manuscript book-en is the gate's invocation on CI.
    assert cage.main(["--manuscript", "book-en", "--check"]) == 0
