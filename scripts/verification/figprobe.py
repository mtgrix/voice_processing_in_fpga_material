#!/usr/bin/env python3
"""figprobe.py -- compile one TikZ figure, or the whole book's worth, and print its size.

Why this exists. scripts/verify_book_pdf.sh counts figure fences against PDF captions and checks the
build log for missing glyphs, but it never asks whether a picture that compiled is wider than the
text block it was dropped into. A TikZ float that overflows prints no error and fails no check:
the `hfuzz=2pt` in book/header.tex only silences small overfull warnings, so a picture too wide
for the column reaches the page bleeding into the margin, and the way to find it is to look at
the page. This script looks at the number instead, before the whole-book build.

Fidelity is the whole point of this script, and it is why the preamble below is derived rather
than written. A first draft of this probe used a bare book class and three packages of its own
invention. It then reported four of the book's eleven figures as too wide for a 345pt column,
and a fifth as a compile error because `\\vert` was undefined in text mode. Both results were
artifacts of the probe. The real build asks Pandoc for 11pt and an a4 page with 32mm and 22mm
side margins, which makes the text block 442pt wide, and its header loads unicode-math, which
is what defines `\\vert` in text mode. A probe that disagrees with the build about the page or
the packages produces confident false findings, which is worse than no probe. So the class
options, the geometry and the header are read from scripts/build_book.sh and book/header.tex at
run time, and the script refuses to guess if either disappears.

Two limits, each found by being wrong rather than by thinking. The first: the probe measures a
figure against the page, and never one part of a figure against another, so a chapter label that
grew into the dashed box drawn around it passed every number this script prints and was only
visible in a rendered picture. The second: it once reported a verdict read out of the previous
run's leftover PDF, because the existence of an artifact was taken as proof that this run had
compiled. A log's modification time is now compared against the run, and both the height and the
depth of the box are reported, since a savebox splits its content at the baseline. Neither fix
changes the rule above: a probe that disagrees with the build is worse than no probe, and a probe
that cannot see a defect should say so rather than imply that it looked.

usage: python scripts/verification/figprobe.py book-en/chapter09.md fig-kv-ring-buffer
       python scripts/verification/figprobe.py --all
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD_SH = os.path.join(ROOT, "scripts", "build_book.sh")
HEADER_TEX = os.path.join(ROOT, "book", "header.tex")
BOOK_DIR = os.path.join(ROOT, "book-en")

#: `::: {#fig-slug .figure}` -- the authoring form scripts/filters/tikz_figures.lua expects.
DIV = re.compile(r"^:::\s*\{#(fig-[A-Za-z0-9_-]+)\s+\.figure\}\s*$", re.M)

#: The figure goes into the savebox directly, not inside a minipage: a minipage is a parbox of the
#: width it is given, so wrapping one would make the measurement read \\textwidth no matter how
#: wide the figure is. \\noindent matters for the same reason -- the class indents a new paragraph,
#: and that indent would read as an Overfull line blaming the figure for the paragraph's own
#: geometry.
TEMPLATE = r"""\documentclass[%CLASSOPTS%]{book}
\usepackage[%GEO%]{geometry}
%HEADER%
\newsavebox{\figbox}
\begin{document}
\typeout{PROBETEXTWIDTH\the\textwidth}
\typeout{PROBETEXTHEIGHT\the\textheight}
\begin{lrbox}{\figbox}%
%FIGURE%
\end{lrbox}
\typeout{PROBEWIDTH\the\wd\figbox}
\typeout{PROBEHEIGHT\the\ht\figbox}
\typeout{PROBEDEPTH\the\dp\figbox}
\noindent\usebox{\figbox}
\end{document}
"""


def tmp_dir() -> str:
    out_dir = os.environ.get("CLAUDE_JOB_DIR", tempfile.gettempdir()) + "/tmp"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def pt(value: str) -> float:
    """Parse a TeX dimension like '442.26pt' into points, or return -1 if it is not one."""
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)pt\s*$", value)
    return float(m.group(1)) if m else -1.0


def preamble() -> tuple[str, str]:
    """Return (class options, geometry options) exactly as scripts/build_book.sh passes them."""
    try:
        build = open(BUILD_SH, encoding="utf-8").read()
    except OSError as exc:
        sys.exit(f"figprobe: cannot read {BUILD_SH}: {exc}")
    # Pandoc accepts a variable as either `-V key=value` or `-V key:value`, and build_book.sh uses
    # both forms, so the separator has to be a character class rather than a literal.
    fontsize = re.search(r"-V\s+fontsize[:=](\S+)", build)
    geo = re.findall(r"-V\s+geometry[:=](\S+)", build)
    if not fontsize or not geo:
        sys.exit(
            "figprobe: scripts/build_book.sh no longer passes -V fontsize / -V geometry, so the\n"
            "probe cannot claim to measure a figure against the page the book really uses.\n"
            "Update this script to read whatever replaced those flags before trusting its verdict."
        )
    # Both pandoc passes share one COMMON_ARGS array, so these six flags appear exactly once in the
    # file. A future second, different geometry set would be joined into one invalid option list,
    # which lualatex then rejects: a loud failure rather than a silently wrong page width.
    return fontsize.group(1), ",".join(geo)


def extract(path: str, slug: str) -> str:
    """Return the tikz fence belonging to the `::: {#fig-slug .figure}` div, or exit."""
    text = open(path, encoding="utf-8").read()
    spans = [(m.group(1), m.start()) for m in DIV.finditer(text)]
    if slug not in [s for s, _ in spans]:
        avail = ", ".join(s for s, _ in spans) or "none"
        sys.exit(f"figprobe: no figure #{slug} in {path} (this file has: {avail})")
    start = next(p for s, p in spans if s == slug)
    fence = re.search(r"^```tikz\s*\n(.*?)^```\s*$", text[start:], re.S | re.M)
    if not fence:
        sys.exit(f"figprobe: #{slug} is a .figure div with no ```tikz fence inside it")
    return fence.group(1)


def all_figures() -> list[tuple[str, str]]:
    """Every (file, slug) pair in book-en/, so --all can sweep the whole book."""
    out: list[tuple[str, str]] = []
    for fn in sorted(os.listdir(BOOK_DIR)):
        if fn.endswith(".md"):
            text = open(os.path.join(BOOK_DIR, fn), encoding="utf-8").read()
            out += [(fn, slug) for slug in DIV.findall(text)]
    if not out:
        sys.exit("figprobe: --all found no figure div in book-en/, so it checked nothing")
    return out


def compile_figure(tex: str, stem: str) -> tuple[int, str, bool, bool]:
    """Typeset one probe document.

    Returns (exit code, log text, whether a PDF appeared, whether the log is from this run).

    The fourth value exists because lualatex is not the only thing that can leave a PDF on disk.
    A previous run of the same figure, or of a different figure sharing the stem, leaves both a
    PDF and a log behind, and a probe that asks only whether they exist will happily report the
    size of a document it never compiled. That is the exact failure this script was written to
    prevent, arriving from inside it: the numbers come back plausible, the verdict comes back
    PASS, and what was actually measured is an older picture. So the run's start time is recorded
    and a log older than it is treated as no log at all.
    """
    out_dir = tmp_dir()
    started = time.time()
    open(stem + ".tex", "w", encoding="utf-8", newline="\n").write(tex)
    proc = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory",
            out_dir,
            stem + ".tex",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    # lualatex writes <jobname>.log beside the output directory, and the jobname is the file's
    # basename, so a stem holding a directory must not be reused to name the log.
    log_path = os.path.join(out_dir, os.path.basename(stem) + ".log")
    # Freshness, not existence. A log left by an earlier run answers every question this probe
    # asks and looks exactly like an answer from this one, so the modification time is compared
    # against the moment lualatex was invoked, and an older log is discarded rather than read.
    fresh = os.path.exists(log_path) and os.path.getmtime(log_path) >= started
    log = ""
    if fresh:
        log = open(log_path, encoding="utf-8", errors="replace").read()
    made_pdf = os.path.exists(os.path.join(out_dir, os.path.basename(stem) + ".pdf"))
    return proc.returncode, log, made_pdf, fresh


def probe(
    path: str, slug: str, header: str, classopts: str, geo: str, stem: str
) -> tuple[int, str]:
    """Measure one figure and print its verdict. Returns (exit code, one-line summary)."""
    tex = (
        TEMPLATE.replace("%CLASSOPTS%", classopts)
        .replace("%GEO%", geo)
        .replace("%HEADER%", header)
        .replace("%FIGURE%", extract(path, slug))
    )
    rc, log, made_pdf, fresh = compile_figure(tex, stem)

    def grab(key: str) -> str:
        m = re.search(rf"{key}(.*?)\s*$", log, re.M)
        return m.group(1).strip() if m else ""

    width, height, depth, text_width, text_height = (
        pt(grab("PROBEWIDTH")),
        pt(grab("PROBEHEIGHT")),
        pt(grab("PROBEDEPTH")),
        pt(grab("PROBETEXTWIDTH")),
        pt(grab("PROBETEXTHEIGHT")),
    )
    overfull = [ln for ln in log.splitlines() if ln.startswith("Overfull")][:6]
    undef = [ln for ln in log.splitlines() if "Undefined control sequence" in ln][:4]
    errors = [ln for ln in log.splitlines() if ln.startswith("!")][:6]

    print(f"figure   : #{slug} from {path}")
    print(f"preamble : documentclass book [{classopts}], geometry [{geo}]")
    print(f"lualatex : exit {rc}; pdf written: {made_pdf}; log from this run: {fresh}")

    if width < 0 or text_width < 0:
        print("size     : never measured -- the compile stopped before the figure was boxed")
        for ln in errors:
            print(f"log      : {ln}")
        return 1, f"{slug:<32} FAIL   compile stopped before the figure was boxed"

    # Height and depth are reported apart and judged together, because a savebox splits its content
    # at the baseline and either half can be the tall one. Before this, the probe compared width to
    # textwidth and never looked at the vertical dimension at all, so a figure could outgrow the
    # page in the one direction a book cannot reflow.
    #
    # What the probe still cannot see, and this is the limit worth remembering: it measures a figure
    # against the page, never one part of a figure against another. A chapter map label that grew
    # into the dashed box drawn around it passed every number here -- width unchanged, height
    # unchanged, no overfull, page nowhere near full. Only the rendered picture showed it. Use
    # --all to catch size, and look at a page render to catch layout inside a figure.
    slack = text_width - width
    total = height + depth
    vslack = text_height - total if text_height > 0 else float("inf")
    reasons = []
    if not fresh:
        reasons.append("no log from this run")
    if slack < 0:
        reasons.append(f"over the text block by {-slack:.1f}pt")
    if vslack < 0:
        reasons.append(f"taller than the text block by {-vslack:.1f}pt")
    if rc != 0 or undef or overfull:
        reasons.append("compile or overfull reported")
    fails = bool(reasons)
    print(f"size     : width {width:.1f}pt  tall {height:.1f}pt + {depth:.1f}pt = {total:.1f}pt")
    print(
        f"available: textwidth {text_width:.1f}pt  slack {slack:+.1f}pt   "
        f"textheight {text_height:.1f}pt  vslack {vslack:+.1f}pt"
    )
    for ln in overfull + undef:
        print(f"log      : {ln}")
    verdict = f"FAIL   {'; '.join(reasons)}" if fails else "PASS"
    return (1 if fails else 0), (
        f"{slug:<32} {verdict:<28} width {width:6.1f}pt  slack {slack:+6.1f}pt  "
        f"tall {total:6.1f}pt  vslack {vslack:+6.1f}pt"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="manuscript file holding the figure")
    ap.add_argument("slug", nargs="?", help="figure id without the leading #")
    ap.add_argument("--all", action="store_true", help="probe every figure div in book-en/")
    args = ap.parse_args()
    if not args.all and not (args.path and args.slug):
        ap.error("give a path and a slug, or --all")

    try:
        header = open(HEADER_TEX, encoding="utf-8").read()
    except OSError as exc:
        sys.exit(f"figprobe: cannot read {HEADER_TEX}: {exc}")
    classopts, geo = preamble()

    if args.all:
        # One job name per figure: reusing a stem lets a crashed run's leftover log answer for a
        # later figure, which would report a verdict for a document that was never compiled.
        figures = all_figures()
        bad = 0
        for fn, slug in figures:
            stem = os.path.join(tmp_dir(), "figprobe-" + slug.removeprefix("fig-"))
            rc, line = probe(os.path.join(BOOK_DIR, fn), slug, header, classopts, geo, stem)
            print(f"{line}   {fn}")
            bad += rc
        print(
            f"-- {bad} of {len(figures)} figure(s) FAIL"
            if bad
            else f"-- {len(figures)} figure(s) PASS"
        )
        return 1 if bad else 0

    # The same stem as --all, for the same reason: a stem that names no figure lets the artifact of
    # whatever was probed last answer for the figure being probed now, and the PDF it leaves behind
    # is then a thing a reader can open and be confidently wrong about.
    stem = os.path.join(tmp_dir(), "figprobe-" + args.slug.removeprefix("fig-"))
    rc, line = probe(args.path, args.slug, header, classopts, geo, stem)
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
