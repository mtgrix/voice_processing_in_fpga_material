#!/bin/bash
# usage: run_agy_v2.sh <tag> "<files>" [feedback_file]
cd /workspace/writing_material/uoc_luong_f0_praat_fpga_quartus
tag=$1; grp=$2; fb=$3
P="You are the implementer in this repo (a Vietnamese LaTeX study document). Read STYLE_BRIEF_v2.md fully and follow it exactly (it supersedes STYLE_BRIEF.md). Also read /workspace/writing_material/audit_phan_moi_2026-11-10.md (esp. section 6 model rewrites and the findings for your chapters) and cases #15-#22 / principles 30-41 in /workspace/writing_material/bai-hoc-viet-tai-lieu.md, and sec_1_3_5_vi_v10.tex as the prose quality bar. Your assignment: rewrite ONLY these files under chuong/: $grp (plus new files you create under verify/, tb/v2/, rtl/v2/, and figure files prefixed with your chapter number). Core rules: Feynman + first-principles 6 points in every section; no telegraphic prose (no label:value lines, arrow chains, bullet stubs); keep ALL existing technical content (counts of words/figures/tables/listings must not drop; fix only what the audit marks wrong); at the end of EACH part a Python twin + Verilog HDL block explained line by line, HDL self-written and bit/cycle-exact with any Intel IP used, with the IP instantiation shown and a prose explanation why it matches; verify each HDL block with iverilog (installed) against the twin and every number with a Python script saved under verify/. Do not edit the main tex before \\input{chuong/chuong_00...}. Commit after each finished section (git add -A; git commit -m 'v2: ...'); DO NOT push. Compile with xelatex -interaction=nonstopmode -output-directory=/tmp/build_v2_$tag uoc_luong_f0_praat_fpga_quartus_vi.tex (twice), fix errors, render your pages with pdftoppm -r 60 and inspect them. Finish with the report described in STYLE_BRIEF_v2.md section 8. Environment: xelatex (TeX Live), iverilog/vvp, pdftoppm, python3+numpy+scipy are ALREADY installed and working; do NOT run apt or change system config; if a tool is missing, write it in your report and continue."
if [ -n "$fb" ] && [ -f "$fb" ]; then P="$P

REVIEWER FEEDBACK FROM THE PREVIOUS ROUND (must all be fixed; this is a follow-up round on the same files, keep the good parts):
$(cat $fb)"; fi
log=/workspace/writing_material/agy_log_v2_${tag}.txt
[ -n "$fb" ] && log=/workspace/writing_material/agy_log_v2_${tag}_$(basename $fb .txt).txt
echo "START $(date)" > $log
agy -p "$P" --dangerously-skip-permissions --effort high >> $log 2>&1
echo "EXIT $? $(date)" >> $log
