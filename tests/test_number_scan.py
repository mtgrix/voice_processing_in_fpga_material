"""The numeric cage has to be proved to rattle, not just shown to be quiet.

Issue #59 added scripts/verification/scan_numbers.py, which fails the gate when the manuscript
prints a number that no claim cited by its own section supports. A gate like this one earns its
place only if two opposite things are both demonstrated: that correct prose passes, and that
wrong prose fails. The first is easy to observe on the real manuscript; the second cannot be,
because the correct manuscript by definition contains no numbers to trip it with. So most of
this file manufactures bad manuscripts -- an uncited figure here, an unsourced latency there --
and asserts the tool says so, and says so about the right file, section, and number.

The exemptions get their own tests for the mirror-image reason. Every region rule (fences, math,
headings, cross-references, identifier digits) is a place the scanner chooses NOT to look, and a
choice not to look is exactly where a wrong number can hide. Each one is therefore pinned from
both sides: the rule exempts the shape it claims to, and does not swallow an ordinary prose
number standing next to it.

End to end, the baseline lifecycle is walked the way a contributor will meet it: a number that
fails --check, gets recorded by --write-baseline, passes --check, still fails --strict, and
announces itself as repaid debt once a real citation is added.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "verification"))
import scan_numbers as scan  # noqa: E402


def fake_claims(*pairs: tuple[str, str, str]) -> dict[str, Any]:
    """A registry document with one record per (id, value, unit) triple."""
    return {
        "records": [
            {"id": cid, "value": value, "unit": unit, "status": "verified"}
            for cid, value, unit in pairs
        ]
    }


# ---------------------------------------------------------------- separators --


def test_as_number_accepts_every_separator_in_use() -> None:
    # The registry writes 23616, chapter 1 writes 16,000, tables write 23 616 with a plain
    # space and (defensively) a no-break space. All four must name one quantity, or the same
    # measurement fails the cage depending on who typed it.
    assert scan.as_number("23616") == 23616.0
    assert scan.as_number("16,000") == 16000.0
    assert scan.as_number("23 616") == 23616.0
    assert scan.as_number("23\xa0616") == 23616.0
    assert scan.as_number("1.25") == 1.25
    assert scan.as_number("2,500.5") == 2500.5
    assert scan.as_number("12.") == 12.0  # sentence-final dot survives tokenising
    assert scan.as_number("12x") is None


# ------------------------------------------------------------- region rules --


def test_tokens_in_skips_identifier_digits() -> None:
    # The first version of the tool read 260 out of KV260 and 01 out of exp_01_streaming.
    found = dict((tok, col) for tok, col in scan.tokens_in("the KV260 ran exp_01 twice"))
    assert found == {}
    # ... and still reads a real quantity standing in the same sentence.
    assert [t for t, _ in scan.tokens_in("the KV260 ran for 2 epochs")] == ["2"]


def test_crossrefs_and_math_are_silent_prose_numbers_are_not() -> None:
    line = "See [Figure 8](#fig-kv-ring-buffer) in section 9.4, page 22, Table 23."
    assert scan.tokens_in(scan.strip_regions(line, "prose")) == []
    math = "$P_{\\text{cache}} = 2 \\times L \\times 64$ gives 8 at the end"
    stripped = scan.strip_regions(math, "prose")
    assert [t for t, _ in scan.tokens_in(stripped)] == ["8"]
    # An idiom the book uses constantly: a bracketed label whose number is Pandoc's, and the
    # real quantity right beside it. Only the quantity may be caged.
    both = "[Table 3](#t-sizes) lists 128 KB blocks"
    assert [t for t, _ in scan.tokens_in(scan.strip_regions(both, "prose"))] == ["128"]


def test_inline_code_is_not_stripped() -> None:
    # Citations live inside backticks in this manuscript; stripping code spans would blind
    # the scanner to the very ids that license the numbers around them.
    assert [t for t, _ in scan.tokens_in("`128`")] == ["128"]


def test_fence_content_never_opens_a_section() -> None:
    text = (
        "## 2.1 Sizes\n\nprose\n\n```tikz\n## 9.9 drawn heading, 12345 units\n```\n\n"
        "## 2.2 Next\n\nmore\n"
    )
    sections = scan.split_sections(text)
    keys = [s["heading"] for s in sections]
    assert keys == ["(front matter)", "2.1", "2.2"]
    fence_lines = [ln for _, ln, k in sections[1]["lines"] if k == "fence"]
    assert any("12345" in ln for ln in fence_lines)  # kept, but tagged fence


def test_sub_subsection_headings_do_not_open_sections() -> None:
    # HEADING matches ###, and level 3 is not a citation scope -- its numbers ride under the
    # enclosing ## section.
    sections = scan.split_sections("## 2.1 A\n\n### 2.1.1 B\n\nprose 7\n")
    assert [s["heading"] for s in sections] == ["(front matter)", "2.1"]


# --------------------------------------------------------------- table rows --


ALLOWED = {"V-01-01": {128.0}, "V-01-02": {32.0}}


def test_table_row_scopes_to_its_own_citation(tmp_path: Path) -> None:
    # Book tables carry a "Where it comes from" column, so the row, not the section, is the
    # unit of support. 32 rides on its own row's citation; 64 cites nothing and the section's
    # 128 cannot vouch for it.
    f = tmp_path / "chapter02.md"
    f.write_text(
        "## 2.1 Cache sizes\n\n"
        "The L2 is 128 KB, see `V-01-01`.\n\n"
        "| Part | KB | Source |\n"
        "| --- | --- | --- |\n"
        "| Core | 32 | `V-01-02` |\n"
        "| Tile | 64 | none |\n",
        encoding="utf-8",
    )
    findings, derived = scan.scan_file(f, ALLOWED)
    assert [r["token"] for r in findings] == ["64"]
    assert findings[0]["in_table"] is True
    assert findings[0]["registered_elsewhere"] == []
    assert derived == []


def test_unit_numbers_license_prose() -> None:
    # "BRAM36 blocks" registers 36 through the unit, not the value; a section citing that
    # claim may print 36.
    nums = scan.claim_numbers({"id": "V-01-05", "value": "4.9", "unit": "BRAM36 blocks"})
    assert nums == {4.9, 36.0}


# ------------------------------------------------------------------ derived --


def test_declared_derivation_is_listed_not_caged(tmp_path: Path) -> None:
    # Arithmetic on registered claims (40 ms = 2 x 20 ms) cannot be checked by matching
    # against the registry, and exempting "numbers that look derived" would exempt the exact
    # shape of an invention. The compromise the tool draws: declared derivations leave the
    # cage but never leave the output, and --list-derived exists to keep them in sight.
    f = tmp_path / "chapter09.md"
    f.write_text(
        "## 9.4 Sizing\n\n"
        "The ring is 40 ms -- derived, from `V-05-31`.\n\n"
        "The tail is 57 ms, measured on the kit.\n",
        encoding="utf-8",
    )
    findings, derived = scan.scan_file(f, ALLOWED)
    assert [r["token"] for r in derived] == ["40"]
    assert [r["token"] for r in findings] == ["57"]


# ------------------------------------------------------------- end to end --


@pytest.fixture()
def cage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """A one-file manuscript, a two-record registry, and a baseline path in tmp."""
    manu = tmp_path / "neg.md"
    manu.write_text(
        "## 2.1 Sizes\n\nThe L2 is 128 KB, per `V-01-01`. The SRAM is 2560 KB.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        scan,
        "load_claims",
        lambda path=None: fake_claims(("V-01-01", "128", "KB"), ("V-09-77", "2560", "KB")),
    )
    monkeypatch.setattr(scan, "BASELINE_PATH", tmp_path / "baseline.json")
    return manu, tmp_path


def test_baseline_lifecycle(cage: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    manu, _ = cage
    # 1. Uncited and unbaselined: --check fails and names the number and its class.
    assert scan.main([str(manu), "--check"]) == 1
    out = capsys.readouterr().out
    assert "2560" in out and "registered by V-09-77" in out
    # 2. Recorded as reviewed debt: --write-baseline succeeds and writes the file.
    assert scan.main([str(manu), "--write-baseline"]) == 0
    doc = json.loads(scan.BASELINE_PATH.read_text(encoding="utf-8"))
    assert [e["number"] for e in doc["entries"]] == ["2560"]
    # 3. The debt excuses --check but never --strict.
    assert scan.main([str(manu), "--check"]) == 0
    assert scan.main([str(manu), "--strict"]) == 1
    # 4. A real citation repays it, and the stale entry is announced, not silently dropped.
    manu.write_text(
        "## 2.1 Sizes\n\nThe L2 is 128 KB, per `V-01-01`. The SRAM is 2560 KB, `V-09-77`.\n",
        encoding="utf-8",
    )
    assert scan.main([str(manu), "--check"]) == 0
    assert "no longer needed" in capsys.readouterr().out


def test_real_manuscript_passes_the_committed_baseline() -> None:
    # Pins docs/verification/number_baseline.json against book-en and the real registry: if
    # this fails, either new prose printed an uncited number or the registry lost one.
    assert scan.main(["--check"]) == 0
