#!/usr/bin/env python3
"""compile_tikz.py -- compile every tikz fence on its own, and name the figure id that failed.

Why this exists. A whole-book build reports ``l.1140`` in a TeX file that pandoc assembled out of
fourteen markdown sources, so the first job of any figure failure is archaeology: which picture is
broken, and under which section. This script removes that step. Each ```tikz fence is wrapped in
the same preamble the book uses -- book/header.tex, so a figure cannot pass here by leaning on a
package some other chapter happens to load -- and compiled alone in a paper large enough that a
wide figure warns instead of failing. Seconds per figure instead of minutes per book.

Two traps this harness has to get right, both learned from being wrong:

  * documentclass, not article. book/header.tex renews \\chapter, and an undefined one is a fatal
    preamble error that reports as a failure of every figure in the file. The harness must share
    the book class or it is not a harness.
  * lualatex halts at the first error, so in a whole build one broken coordinate masks every
    defect below it. Compiling figures separately is also what makes the queue visible.

What this script does NOT license: it says nothing about fit. A figure that overflows the text
block compiles happily here, because overfull boxes are not errors -- that claim belongs to
figprobe.py, which measures the box against the page the build really uses. And it says nothing
about whether a picture depicts its caption; only a rendered page and a reader can check that.

usage:
  python scripts/verification/compile_tikz.py book-en/chapter09.md [more files]
  python scripts/verification/compile_tikz.py --check    # every figure in the manifest
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from figure_numbers import sources  # noqa: E402  (manifest reading order, parsed once)

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "book" / "header.tex"
BOOK_DIR = ROOT / "book-en"

#: A figure div, its id, and the fence inside it. The div form is asserted by check_figures.py;
#: this reads the same shape so the two tools cannot disagree about what a figure is.
DIV = re.compile(
    r"^:::\s*\{#(fig-[A-Za-z0-9_-]+)\s+\.figure\}\s*$\n^```tikz\s*$\n(.*?)^```\s*$",
    re.S | re.M,
)
#: Which section a div sits under, so a failure names the fragment to edit rather than a line.
SEC = re.compile(r"^## (\d+\.\d+)", re.M)
LATEX_ERR = re.compile(r"^! (.*)$", re.M)
PGF_LINE = re.compile(r"^l\.(\d+) (.*)$", re.M)


def shell(body: str, header: str) -> str:
    return (
        "\\documentclass[10pt]{book}\n"
        "\\usepackage[margin=6cm]{geometry}\n"
        + header
        + "\n\\begin{document}\n"
        + body
        + "\n\\end{document}\n"
    )


def compile_one(tex: str, fid: str, out_dir: str) -> tuple[int, str]:
    """Typeset one figure alone. Returns (exit code, log text)."""
    job = os.path.join(out_dir, fid)
    os.makedirs(job, exist_ok=True)
    Path(job, "pic.tex").write_text(tex, encoding="utf-8", newline="\n")
    proc = subprocess.run(
        ["lualatex", "-interaction=nonstopmode", "-halt-on-error", "pic.tex"],
        cwd=job,
        capture_output=True,
        text=True,
    )
    log_path = Path(job, "pic.log")
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    return proc.returncode, log


def compile_file(path: Path, header: str, out_dir: str) -> tuple[int, int]:
    """Compile every figure in one manuscript file. Returns (checked, failed)."""
    text = path.read_text(encoding="utf-8")
    marks = [(m.start(), m.group(1)) for m in SEC.finditer(text)]
    checked = failed = 0
    for m in DIV.finditer(text):
        fid, body = m.group(1), m.group(2)
        sec = next((s for pos, s in reversed(marks) if pos < m.start()), "?")
        checked += 1
        rc, log = compile_one(shell(body, header), fid, out_dir)
        errs = LATEX_ERR.findall(log)
        if rc == 0 and not errs:
            print(f"  PASS  {fid:<32} ({sec})")
            continue
        failed += 1
        print(f"  FAIL  {fid:<32} ({sec})  rc={rc}")
        seen: set[str] = set()
        for i, e in enumerate(errs):
            where = PGF_LINE.findall(log)
            ctx = where[i][0] if i < len(where) else "?"
            src = where[i][1][:60] if i < len(where) else ""
            # lualatex repeats one broken key for every subsequent path command, so a log with
            # forty ! lines can carry two real defects. Dedup on the message.
            if e[:58] in seen:
                continue
            seen.add(e[:58])
            print(f"        l.{ctx}  {e[:110]}")
            print(f"              >> {src}")
    return checked, failed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="manuscript files holding the figures")
    ap.add_argument(
        "--check", action="store_true", help="compile every figure in the manifest's sources"
    )
    args = ap.parse_args(argv)
    if not HEADER.is_file():
        sys.exit(f"compile_tikz: no preamble at {HEADER}; the harness would compile nothing real")
    header = HEADER.read_text(encoding="utf-8")
    if args.check:
        paths = [BOOK_DIR / s for s in sources()]
    elif args.files:
        paths = [Path(f) for f in args.files]
    else:
        sys.exit("compile_tikz: give it files to check, or --check for the whole book")
    total = fails = 0
    with tempfile.TemporaryDirectory(prefix="tikzcompile-") as out_dir:
        for path in paths:
            print(f"=== {path.name}")
            checked, failed = compile_file(path, header, out_dir)
            total += checked
            fails += failed
    print(f"compile_tikz: {total} figure(s), {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
