#!/usr/bin/env bash
# verify_v3/run_ch11_iverilog.sh
# Runs iverilog simulations for Chapter 11 (Median-3 replacing Path Finder)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch11_median3.v ]; then
    cd ..
fi

echo "=== [ch11] Compiling tb_ch11_median3 with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch11_median3 \
    tb/v3/tb_ch11_median3.v \
    rtl/v3/ch11_median3.v

echo "=== [ch11] Running simulation vvp sim_ch11_median3 ==="
vvp verify_v3/sim_ch11_median3 > verify_v3/ch11_median3_iverilog.log 2>&1
cat verify_v3/ch11_median3_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch11_median3_iverilog.log; then
    echo "=== [ch11] ERROR: Simulation tb_ch11_median3 detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "\[PASS\] All [0-9]\+ cycles matched bit-for-bit with Python twin\!" verify_v3/ch11_median3_iverilog.log; then
    echo "=== [ch11] ERROR: Expected success banner not found in ch11_median3_iverilog.log! ==="
    exit 1
fi

echo "=== [ch11] tb_ch11_median3 PASSED (0 errors) ==="
rm -f verify_v3/sim_ch11_median3
