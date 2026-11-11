#!/usr/bin/env bash
# verify_v3/run_ch10_iverilog.sh
# Runs iverilog simulations for Chapter 10 (Voicing Decision: Silence / Voiceless / Voiced)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch10_voicing.v ]; then
    cd ..
fi

echo "=== [ch10] Compiling tb_ch10_voicing with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch10_voicing \
    tb/v3/tb_ch10_voicing.v \
    rtl/v3/ch10_voicing.v

echo "=== [ch10] Running simulation vvp sim_ch10_voicing ==="
vvp verify_v3/sim_ch10_voicing > verify_v3/ch10_voicing_iverilog.log 2>&1
cat verify_v3/ch10_voicing_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch10_voicing_iverilog.log; then
    echo "=== [ch10] ERROR: Simulation tb_ch10_voicing detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "\[PASS\] All [0-9]\+ cycles matched bit-for-bit with Python twin\!" verify_v3/ch10_voicing_iverilog.log; then
    echo "=== [ch10] ERROR: Expected success banner not found in ch10_voicing_iverilog.log! ==="
    exit 1
fi

echo "=== [ch10] tb_ch10_voicing PASSED (0 errors) ==="
rm -f verify_v3/sim_ch10_voicing
