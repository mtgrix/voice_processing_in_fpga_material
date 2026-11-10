#!/bin/bash
# usage: run_agy_v2_wt.sh <tag> "<files>" [feedback_file]  — runs in git worktree /workspace/writing_material/wt_<tag> on branch v2_<tag>
base=/workspace/writing_material/uoc_luong_f0_praat_fpga_quartus
tag=$1; grp=$2; fb=$3; wt=/workspace/writing_material/wt_$tag
cd $base
[ -d $wt ] || git worktree add -q -b v2_$tag $wt HEAD
sed -e "s|cd /workspace/writing_material/uoc_luong_f0_praat_fpga_quartus|cd $wt|" -e "s|You are the implementer in this repo|You are the implementer in this repo. Your working copy is the git worktree $wt (branch v2_$tag): read, edit, build and commit ONLY there, never in /workspace/writing_material/uoc_luong_f0_praat_fpga_quartus|" $base/run_agy_v2.sh > /tmp/run_agy_v2_$tag.sh
chmod +x /tmp/run_agy_v2_$tag.sh
cd $wt && /tmp/run_agy_v2_$tag.sh "$tag" "$grp" "$fb"
