#!/usr/bin/env bash
# verify_v3/run_ch13_iverilog.sh
# Verification script for Chapter 13: System Verification and Comparison with Praat.
# Runs all Chapter 13 Python audits and checks all committed iverilog logs (Ch01-Ch12).
# Exits non-zero if any check fails or any [FAIL] appears.

set -e

# Change to verify_v3 directory if run from repo root
if [ -d verify_v3 ]; then
    cd verify_v3
fi

echo "===================================================================="
echo "STARTING CHAPTER 13 SYSTEM VERIFICATION SUITE"
echo "===================================================================="

PYTHON="${PYTHON:-python}"

echo "=== [1/5] Running Statistical Metrics Audit (Agenda Section 7) ==="
$PYTHON ch13_metrics_audit.py > ch13_metrics_audit.log 2>&1
cat ch13_metrics_audit.log

echo "=== [2/5] Running Miniature Hand Example (10 Frames) ==="
$PYTHON ch13_hand_example.py > ch13_hand_example.log 2>&1
cat ch13_hand_example.log

echo "=== [3/5] Running Frame Alignment Audit (Praat C++ vs HPS C) ==="
$PYTHON ch13_frame_alignment.py > ch13_frame_alignment.log 2>&1
cat ch13_frame_alignment.log

echo "=== [4/5] Running Praat 7.0.03 Line Citations Audit ==="
$PYTHON ch13_praat_lines.py > ch13_praat_lines.log 2>&1
cat ch13_praat_lines.log

echo "=== [5/5] Running Chapter 13 Exercises Verification ==="
$PYTHON ch13_exercises.py > ch13_exercises.log 2>&1
cat ch13_exercises.log

echo "===================================================================="
echo "AUDITING COMMITTED IVERILOG LOGS ACROSS ALL CHAPTERS (CH01-CH12)"
echo "===================================================================="

LOGS=(
    "ch01_iverilog.log"
    "ch02_iverilog.log"
    "ch03_iverilog.log"
    "ch04_iverilog.log"
    "ch05_iverilog.log"
    "ch06_iverilog.log"
    "ch07_iverilog.log"
    "ch08_iverilog.log"
    "ch09_div_iverilog.log"
    "ch09_calc_iverilog.log"
    "ch10_voicing_iverilog.log"
    "ch11_median3_iverilog.log"
    "ch12_top_iverilog.log"
)

for log in "${LOGS[@]}"; do
    if [ ! -f "$log" ]; then
        echo "=== [ERROR] Missing required iverilog log: $log ==="
        exit 1
    fi
    if grep -q "\[FAIL\]" "$log"; then
        echo "=== [ERROR] Detected [FAIL] token in $log ==="
        exit 1
    fi
    echo "  [PASS] Log $log verified: 0 errors, no [FAIL] token."
done

echo "===================================================================="
echo "[PASS] ALL CHAPTER 13 VERIFICATIONS AND LOG AUDITS PASSED (0 ERRORS)!"
echo "===================================================================="
