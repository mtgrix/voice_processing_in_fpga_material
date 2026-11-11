#!/usr/bin/env bash
# verify_v3/run_ch03_iverilog.sh
# Runs Chapter 3 testbench with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch03_fir.v ]; then
    cd ..
fi

echo '=== Compiling and running tb_ch03_fir ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch03_fir tb/v3/tb_ch03_fir.v rtl/v3/ch03_fir_filter.v
vvp sim_ch03_fir > sim_ch03_fir.log 2>&1 || true
cat sim_ch03_fir.log
if grep -q "\[FAIL\]" sim_ch03_fir.log; then
    echo "ERROR: tb_ch03_fir reported FAIL!" >&2
    rm -f sim_ch03_fir sim_ch03_fir.log
    exit 1
fi
rm -f sim_ch03_fir sim_ch03_fir.log

echo '=== All Chapter 3 iverilog testbenches passed successfully! ==='
