#!/usr/bin/env bash
# verify_v3/run_ch09_iverilog.sh
# Runs iverilog simulations for Chapter 9 (Peak finding, parabolic interpolation, F0 and divider)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch09_div.v ]; then
    cd ..
fi

echo "=== [ch09] Compiling tb_ch09_div with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch09_div \
    tb/v3/tb_ch09_div.v \
    rtl/v3/ch09_radix2_div.v

echo "=== [ch09] Running simulation vvp sim_ch09_div ==="
vvp verify_v3/sim_ch09_div > verify_v3/ch09_div_iverilog.log 2>&1
cat verify_v3/ch09_div_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch09_div_iverilog.log; then
    echo "=== [ch09] ERROR: Unit simulation tb_ch09_div detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ VECTORS MATCHED SUCCESSFULLY" verify_v3/ch09_div_iverilog.log; then
    echo "=== [ch09] ERROR: Expected success banner not found in ch09_div_iverilog.log! ==="
    exit 1
fi

echo "=== [ch09] tb_ch09_div PASSED (0 errors) ==="
rm -f verify_v3/sim_ch09_div

echo "=== [ch09] Compiling tb_ch09_calc with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch09_calc \
    tb/v3/tb_ch09_calc.v \
    rtl/v3/ch09_f0_calc.v \
    rtl/v3/ch09_peak_finder.v \
    rtl/v3/ch09_radix2_div.v

echo "=== [ch09] Running simulation vvp sim_ch09_calc ==="
vvp verify_v3/sim_ch09_calc > verify_v3/ch09_calc_iverilog.log 2>&1
cat verify_v3/ch09_calc_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch09_calc_iverilog.log; then
    echo "=== [ch09] ERROR: Full-core simulation tb_ch09_calc detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ VECTORS MATCHED SUCCESSFULLY" verify_v3/ch09_calc_iverilog.log; then
    echo "=== [ch09] ERROR: Expected success banner not found in ch09_calc_iverilog.log! ==="
    exit 1
fi

echo "=== [ch09] tb_ch09_calc PASSED (0 errors) ==="
rm -f verify_v3/sim_ch09_calc

echo "=== [ch09] All Chapter 9 iverilog simulations completed successfully ==="
