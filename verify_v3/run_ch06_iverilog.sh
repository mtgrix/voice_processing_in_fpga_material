#!/usr/bin/env bash
# verify_v3/run_ch06_iverilog.sh
# Runs Chapter 6 Hanning window testbench with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch06_hanning.v ]; then
    cd ..
fi

echo '=== Compiling and running tb_ch06_hanning ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch06_hanning \
    tb/v3/tb_ch06_hanning.v \
    rtl/v3/ch06_hanning_window.v \
    rtl/v3/ch06_hanning_rom.v

vvp sim_ch06_hanning > sim_ch06_hanning.log 2>&1 || true
cat sim_ch06_hanning.log

if grep -q "\[FAIL\]" sim_ch06_hanning.log; then
    echo "ERROR: tb_ch06_hanning reported FAIL!" >&2
    rm -f sim_ch06_hanning sim_ch06_hanning.log
    exit 1
fi
rm -f sim_ch06_hanning sim_ch06_hanning.log

echo '=== All Chapter 6 iverilog testbenches passed successfully! ==='
