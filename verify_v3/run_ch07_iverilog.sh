#!/usr/bin/env bash
# verify_v3/run_ch07_iverilog.sh
# Runs iverilog simulations for Chapter 7 (Autocorrelation by MAC)
# Exits non-zero if any [FAIL] appears or compilation fails

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

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
    echo "=== [ch07] ERROR: Simulation detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "ALL [0-9]\+ VECTORS MATCHED SUCCESSFULLY" verify_v3/ch07_iverilog.log; then
    echo "=== [ch07] ERROR: Expected success banner not found in log! ==="
    exit 1
fi

echo "=== [ch07] tb_ch07_mac PASSED (0 errors) ==="
rm -f verify_v3/sim_ch07_mac
exit 0
