#!/usr/bin/env bash
# verify_v3/run_ch08_iverilog.sh
# Runs iverilog simulations for Chapter 8 (Window Normalization C[tau] and Octave Cost)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch08_norm.v ]; then
    cd ..
fi

echo "=== [ch08] Compiling tb_ch08_norm with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch08_norm \
    tb/v3/tb_ch08_norm.v \
    rtl/v3/ch08_norm_score.v \
    rtl/v3/ch08_ck_rom.v

echo "=== [ch08] Running simulation vvp sim_ch08_norm ==="
vvp verify_v3/sim_ch08_norm > verify_v3/ch08_iverilog.log 2>&1
cat verify_v3/ch08_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch08_iverilog.log; then
    echo "=== [ch08] ERROR: Unit simulation detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ VECTORS MATCHED SUCCESSFULLY" verify_v3/ch08_iverilog.log; then
    echo "=== [ch08] ERROR: Expected unit success banner not found in log! ==="
    exit 1
fi

echo "=== [ch08] tb_ch08_norm PASSED (0 errors) ==="
rm -f verify_v3/sim_ch08_norm

echo "=== [ch08] All Chapter 8 iverilog simulations completed successfully ==="
