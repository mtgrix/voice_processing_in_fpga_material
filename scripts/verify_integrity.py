"""Repository Integrity and Academic Consistency Verification Script."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: The registry generator and the evidence helpers are modules, not a package, so the directory
#: holding them goes on the search path the same way every other script here does it. mypy already
#: knows about the directory (mypy_path in pyproject.toml); this is for run time.
sys.path.insert(0, str(ROOT / "scripts" / "verification"))

from build_source_index import INDEX_PATH, render, serialise  # noqa: E402
from claims_lib import CLAIMS_PATH, load_claims  # noqa: E402


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


#: Legacy chapter-scoped ids are grandfathered: book/chapter01.md and book/chapter02.md cite
#: R01-03, R01-05 and R01-01 by that name. They stayed unreworded because the evidence protocol
#: of the time forbade an agent from editing book/; that rule was retired on 2026-09-12, but the
#: grandfathering stands, because the registry itself still uses the R-prefixed ids. New sources
#: therefore take the global S<NNN> form, and both are accepted so that the registry can grow
#: without a rewrite that a human has not approved yet.
SOURCE_ID_PATTERN = re.compile(r"^(?:R\d{2}-\d{2}|S\d{3})$")

#: Rows in a status table that claim a result. A legend line defining a symbol is not a claim,
#: which is why only table rows are scanned.
RESULT_MARKER = "✅"


def check_source_claim_linkage() -> tuple[list[str], list[str]]:
    """Every source id is well formed and its claims_supported entries are real records.

    Returns errors plus warnings. plan-v2 section 9.4 asks for the strict rule that each source
    support at least one claim; that is a warning today, because the whitepaper, FINN and
    Conformer entries describe material no record has cited yet. Tightening it is a later step
    once those records exist, not a reason to leave the link unchecked now.

    Read this as one half of a pair, with check_registry_coverage() below as the other. Everything
    here is a property of the file as committed: whether an id is shaped correctly, whether a
    listed record exists. Whether the registry reaches every document the records cite is derived
    by the generator that owns that join.
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        sources = json.loads((ROOT / "docs" / "source_index.json").read_text(encoding="utf-8"))[
            "sources"
        ]
    except Exception as e:
        return [f"Failed to parse docs/source_index.json: {e}"], warnings
    try:
        claims = json.loads(
            (ROOT / "docs" / "verification" / "claims.json").read_text(encoding="utf-8")
        )["records"]
    except Exception as e:
        return [f"Failed to parse docs/verification/claims.json: {e}"], warnings
    claim_ids = {str(c.get("id")) for c in claims}
    for s in sources:
        sid = str(s.get("id"))
        if not SOURCE_ID_PATTERN.match(sid):
            errors.append(
                f"Source id {sid!r} is neither a grandfathered legacy id (R01-NN) nor the "
                "global S<NNN> form reserved for new sources"
            )
        supported = s.get("claims_supported")
        if supported is None:
            errors.append(f"Source {sid} has no claims_supported field; link it or set it to []")
            continue
        if not isinstance(supported, list):
            errors.append(f"Source {sid} claims_supported is not a list")
            continue
        dangling = [c for c in supported if c not in claim_ids]
        if dangling:
            errors.append(f"Source {sid} claims_supported points at missing records {dangling}")
        if not supported:
            warnings.append(f"Source {sid} supports no verification record yet")
    return errors, warnings


def check_registry_coverage() -> tuple[list[str], list[str]]:
    """Ask the registry generator whether its rendering covers the evidence set.

    Issue #20 step 3 asked for this script to fail on a doc_id that resolves to no registry entry,
    because the two files used to be checked independently and neither knew the other's identifier
    space. It does fail, and the join is still derived exactly once: build_source_index.py is the
    only code that knows how a registry is built out of claims.json, so this function calls that
    code and reports its verdict. Re-matching the labels here would put two answers in the
    repository able to disagree, which is the failure the issue was written about.

    What this adds over 'make check-registry' is the committed file rather than the rendering:
    serialise(render(...)) has to equal the bytes on disk, so a registry edited by hand fails here
    even when its own numbers add up. Both run in the gate, so neither is load-bearing alone.

    Returns errors plus warnings. The warning is one document whose records sit at different tiers,
    which is legitimate -- the tier belongs to the claim being made, not to the paper -- but which
    must not be compared across records without reading why.
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        doc = load_claims(CLAIMS_PATH)
        on_disk = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        report = render(doc)
    except Exception as e:
        return [f"Registry coverage could not be computed: {e}"], warnings

    for line in report.unmapped:
        errors.append(f"A cited document resolves to no registry entry: {line}")
    for line in report.stale:
        errors.append(f"The registry answers a label no record uses: {line}")
    for line in report.no_url:
        errors.append(f"An unlocatable source holds up a claim: {line}")
    for line in report.bad_exempt:
        errors.append(f"An exempt doc_id does not match the record carrying it: {line}")
    for line in report.tier_split:
        warnings.append(f"Source {line}")
    if serialise(report.document) != on_disk:
        errors.append(
            "docs/source_index.json is not what its spec renders, so it was probably edited by "
            "hand; run: make render-registry"
        )

    print(
        f"  registry coverage: {report.labels - report.exempt} of {report.labels} cited doc_id "
        f"labels resolve to an entry; {report.exempt} name arithmetic or an absence and must not"
    )
    return errors, warnings


#: Separator folding, so a row id and a log path can be matched without the gate knowing
#: every spelling of every id: plan-v2 prescribes results/expNN/<timestamp>/ while the
#: status tables name the same experiment exp_NN.
ID_FOLD = re.compile("[^a-z0-9]")

#: sha256sum writes "<digest>  <path>", with a leading "*" on the path in binary mode.
DIGEST_FIELDS = 2


def _fold(text: str) -> str:
    """Lowercase and strip everything that is not a letter or a digit."""
    return ID_FOLD.sub("", text.lower())


def _claimed_rows(path: Path) -> list[tuple[int, str]]:
    """Rows asserting a finished result, as (line number, row id from the first cell).

    Any table row counts, not only rows whose id is bold -- the claim is the marker, not
    the emphasis. A legend line that defines the symbol starts with a quote instead of a
    pipe, which is what keeps the definition from reading as a claim.
    """
    found: list[tuple[int, str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if RESULT_MARKER not in stripped or not stripped.startswith("|"):
            continue
        cells = [cell.strip().strip("*").strip() for cell in stripped.strip("|").split("|")]
        found.append((number, cells[0] if cells else ""))
    return found


def _digests(manifest: Path) -> dict[str, str]:
    """Parse a checksum manifest into {slash-relative path: digest}; empty if absent."""
    table: dict[str, str] = {}
    if not manifest.is_file():
        return table
    for line in manifest.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == DIGEST_FIELDS:
            table[parts[1].lstrip("*")] = parts[0]
    return table


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_result_markers_have_logs() -> list[str]:
    """No row may claim a finished result without its own checksummed raw log.

    plan-v2 section 9.2 item 5, and Issue #18. Three distinct failures are caught: a
    claim with no log, a claim vouched for by a log belonging to a different row, and a
    claim whose log no longer matches the digest recorded for it. The middle one is what
    the previous whole-directory test could not see -- one file anywhere in results/
    satisfied it for every row at once -- and the third is what makes a checksum worth
    computing rather than merely present.

    Known limit, stated rather than hidden: correspondence is by folded substring, so a row
    id of two digits -- a chapter number in BOOK_STATUS -- is matched by any path holding
    those digits, a timestamp among them. Experiment ids are long enough for the fold to be
    discriminating; bare chapter numbers are not. No such row carries the marker today, so
    the limit is unexercised, and the way to keep it unexercised is to mark measurements,
    not chapters.
    """
    errors: list[str] = []
    log_dir = ROOT / "results"
    manifest = log_dir / "SHA256SUMS"
    logs: list[Path] = []
    if log_dir.is_dir():
        logs = [p for p in sorted(log_dir.rglob("*")) if p.is_file() and p != manifest]
    digests = _digests(manifest)

    for relative in ("docs/BOOK_STATUS.md", "docs/EXPERIMENT_STATUS.md"):
        path = ROOT / relative
        if not path.exists():
            errors.append(f"{relative} does not exist")
            continue
        for number, row_id in _claimed_rows(path):
            if not row_id:
                errors.append(f"{relative}:{number} carries {RESULT_MARKER} but names no row id")
                continue
            folded = _fold(row_id)
            vouching = [log for log in logs if folded in _fold(log.relative_to(ROOT).as_posix())]
            if not vouching:
                errors.append(
                    f"{relative}:{number} claims {RESULT_MARKER} for {row_id}, but results/ "
                    "holds no log naming that row"
                )
                continue
            for log in vouching:
                rel = log.relative_to(ROOT).as_posix()
                if rel not in digests:
                    errors.append(
                        f"{relative}:{number} vouches on {rel}, which results/SHA256SUMS does "
                        "not list; an unchecksummed log is a claim, not evidence"
                    )
                elif digests[rel] != _sha256(log):
                    errors.append(
                        f"{relative}:{number} vouches on {rel}, whose bytes no longer match "
                        "the digest in results/SHA256SUMS"
                    )
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
    linkage_errors, linkage_warnings = check_source_claim_linkage()
    all_errors.extend(linkage_errors)
    coverage_errors, coverage_warnings = check_registry_coverage()
    all_errors.extend(coverage_errors)
    all_errors.extend(check_result_markers_have_logs())
    all_errors.extend(check_forbidden_markers())

    for warning in linkage_warnings + coverage_warnings:
        print(f"  note: {warning}")

    if all_errors:
        print("FAIL: Integrity errors detected:")
        for err in all_errors:
            print(f"  - {err}")
        return 1

    print("PASS: Repository integrity and citations fully verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
