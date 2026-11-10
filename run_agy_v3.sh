#!/bin/bash
# usage: run_agy_v3.sh <chXX> "<chapter title>" [feedback_file]   — foreground, one chapter per run
cd /workspace/writing_material/uoc_luong_f0_praat_fpga_quartus
ch=$1; title=$2; fb=$3
P="You are the implementer in this repo (a Vietnamese LaTeX study document on Praat-style F0 estimation on a DE10-Standard FPGA). You are on git branch v3; stay on it. Read /workspace/writing_material/brief/BRIEF_v3.md completely and follow it exactly: it is the contract, and a reviewer will reject the chapter if it breaks any rule there. Then read the sources it lists in section 1 (agenda_chot_v2 first, then golden_v2/, then the style files). Your assignment in this run: write ${title} (file name per BRIEF_v3 section 9, chapter-specific instructions in BRIEF_v3 section 13 and agenda section 3), including its verify_v3/${ch}_* scripts and logs, rtl/v3/${ch}_*.v, tb/v3/tb_${ch}_*.v, sw_v3/${ch}_* (if any) and a verify_v3/Makefile target ${ch}. Run every script and testbench yourself; only print numbers your scripts produced. Compile phan_moi_v3.tex twice with xelatex as in BRIEF_v3 section 11, fix errors and overfull boxes, render and look at every page of your chapter. Commit after each finished subsection (git add -A; git commit -m 'v3: ${ch} <subsection>'), never push. Finish with the report of BRIEF_v3 section 12 (also saved to verify_v3/${ch}_REPORT.md) and a final commit 'v3: ${ch} done'. Environment: xelatex, iverilog/vvp, gcc, pdftoppm, python3+numpy+scipy and Praat 7.0.03 (/workspace/tools/praat7003/praat_barren) are installed; Quartus is not; do NOT run apt/pip or change system config."
if [ -n "$fb" ] && [ -f "$fb" ]; then P="$P

THIS IS A REVISION ROUND on the same chapter. Keep everything good that is already committed, and fix every point in the reviewer feedback below. When done, update verify_v3/${ch}_REPORT.md with a section 'Revision round' listing each feedback point and what you changed, then commit 'v3: ${ch} revision'.

REVIEWER FEEDBACK:
$(cat $fb)"; fi
log=/workspace/writing_material/agy_log_v3_${ch}.txt
[ -n "$fb" ] && log=/workspace/writing_material/agy_log_v3_${ch}_$(basename $fb .txt).txt
echo "START $(date)" > $log
/home/box/.local/bin/agy -p "$P" --dangerously-skip-permissions ${AGY_MODEL:+--model $AGY_MODEL} ${AGY_MODEL:---effort high} >> $log 2>&1
echo "EXIT $? $(date)" >> $log
