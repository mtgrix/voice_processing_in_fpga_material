#!/usr/bin/env bash
# verify_v3/run_ch07_iverilog.sh
# Runs iverilog simulations for Chapter 7 (Autocorrelation by MAC)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch07_mac.v ]; then
    cd ..
fi

echo "=== [ch07] Compiling tb_ch07_mac with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch07_mac \
    tb/v3/tb_ch07_mac.v \
    rtl/v3/ch07_mac_unit.v

echo "=== [ch07] Running simulation vvp sim_ch07_mac ==="
vvp verify_v3/sim_ch07_mac > verify_v3/ch07_iverilog.log 2>&1
cat verify_v3/ch07_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch07_iverilog.log; then
    echo "=== [ch07] ERROR: Unit simulation detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ VECTORS MATCHED SUCCESSFULLY" verify_v3/ch07_iverilog.log; then
    echo "=== [ch07] ERROR: Expected unit success banner not found in log! ==="
    exit 1
fi

echo "=== [ch07] tb_ch07_mac PASSED (0 errors) ==="
rm -f verify_v3/sim_ch07_mac

echo "=== [ch07] Compiling tb_ch07_mac_engine with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch07_mac_engine \
    tb/v3/tb_ch07_mac_engine.v \
    rtl/v3/ch07_mac_engine.v \
    rtl/v3/ch07_xw_ram.v \
    rtl/v3/ch07_mac_unit.v

echo "=== [ch07] Running simulation vvp sim_ch07_mac_engine ==="
vvp verify_v3/sim_ch07_mac_engine > verify_v3/ch07_engine_iverilog.log 2>&1
cat verify_v3/ch07_engine_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch07_engine_iverilog.log; then
    echo "=== [ch07] ERROR: Engine simulation detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ RESULTS MATCHED SUCCESSFULLY" verify_v3/ch07_engine_iverilog.log; then
    echo "=== [ch07] ERROR: Expected engine success banner not found in log! ==="
    exit 1
fi

echo "=== [ch07] tb_ch07_mac_engine PASSED (0 errors) ==="
rm -f verify_v3/sim_ch07_mac_engine

echo "=== [ch07] All Chapter 7 iverilog testbenches passed successfully! ==="
exit 0
