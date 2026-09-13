#!/usr/bin/env python3
"""capture_result.py -- run one experiment and commit its raw log.

plan-v2 section 5.1 requires that a result's raw log be committed under
``results/expNN/<timestamp>/`` and that every claimed row resolve to a log whose digest
``results/SHA256SUMS`` lists. ``scripts/verify_integrity.py`` enforces the second half.
This script produces the first, so that a number in the book names a file a script
wrote rather than a file a person typed.

Nothing here computes a metric. It imports the experiment, calls its own
``run_experiment()``, and records what that call returned and printed. The value of the
exercise is that the log is the program's output, so a bug in the program is a bug in
the record and cannot be hidden by a transcription.

Usage:
    python scripts/capture_result.py exp_01 chapter01/exp_01_streaming_audio_pipeline.py
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("row_id", help="row id the log vouches for, e.g. exp_01")
    ap.add_argument("script", help="path of the experiment script, relative to the repo root")
    ap.add_argument("--label", default="", help="free-text label recorded beside the run")
    args = ap.parse_args()

    script = (ROOT / args.script).resolve()
    if not script.is_file():
        print(f"capture_result: no such script: {script}", file=sys.stderr)
        return 2

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    # The directory name carries the folded row id: verify_integrity matches a claim to
    # its log by folded substring, and plan-v2 prescribes results/expNN/<timestamp>/.
    out_dir = ROOT / "results" / args.row_id.replace("_", "") / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = importlib.util.spec_from_file_location("captured_experiment", script)
    if spec is None or spec.loader is None:
        print(f"capture_result: cannot load {script}", file=sys.stderr)
        return 2
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: @dataclass resolves annotations through sys.modules, so a
    # module that is loaded but not registered fails inside the standard library.
    sys.modules["captured_experiment"] = module
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        spec.loader.exec_module(module)
        if not hasattr(module, "run_experiment"):
            print("capture_result: the script defines no run_experiment()", file=sys.stderr)
            return 2
        returned = module.run_experiment()
    printed = stream.getvalue()

    (out_dir / "stdout.log").write_text(printed, encoding="utf-8", newline="\n")
    record = {
        "row_id": args.row_id,
        "script": script.relative_to(ROOT).as_posix(),
        "label": args.label,
        "captured_utc": stamp,
        "returned_metrics": returned,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": __import__("numpy").__version__,
        },
    }
    (out_dir / "result.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )

    manifest = ROOT / "results" / "SHA256SUMS"
    existing = ""
    if manifest.is_file():
        existing = manifest.read_text(encoding="utf-8")
    with manifest.open("a", encoding="utf-8", newline="\n") as fh:
        for path in sorted(out_dir.iterdir()):
            rel = path.relative_to(ROOT).as_posix()
            if f" {rel}\n" in existing:
                continue
            fh.write(f"{sha256(path)}  {rel}\n")

    print(f"capture_result: wrote {out_dir.relative_to(ROOT).as_posix()}/")
    for path in sorted(out_dir.iterdir()):
        print(f"  {sha256(path)[:16]}...  {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
