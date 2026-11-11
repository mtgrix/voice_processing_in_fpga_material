#!/usr/bin/env bash
# verify_v3/run_ch05_iverilog.sh
# Runs Chapter 5 testbenches with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch05_local_mean.v ]; then
    cd ..
fi

echo '=== Compiling and running tb_ch05_local_mean ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch05_local_mean tb/v3/tb_ch05_local_mean.v rtl/v3/ch05_local_mean.v
vvp sim_ch05_local_mean > sim_ch05_local_mean.log 2>&1 || true
cat sim_ch05_local_mean.log
if grep -q "\[FAIL\]" sim_ch05_local_mean.log; then
    echo "ERROR: tb_ch05_local_mean reported FAIL!" >&2
    rm -f sim_ch05_local_mean sim_ch05_local_mean.log
    exit 1
fi
rm -f sim_ch05_local_mean sim_ch05_local_mean.log

echo '=== Compiling and running tb_ch05_dc_blocker ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch05_dc_blocker tb/v3/tb_ch05_dc_blocker.v rtl/v3/ch05_dc_blocker.v
vvp sim_ch05_dc_blocker > sim_ch05_dc_blocker.log 2>&1 || true
cat sim_ch05_dc_blocker.log
if grep -q "\[FAIL\]" sim_ch05_dc_blocker.log; then
    echo "ERROR: tb_ch05_dc_blocker reported FAIL!" >&2
    rm -f sim_ch05_dc_blocker sim_ch05_dc_blocker.log
    exit 1
fi
rm -f sim_ch05_dc_blocker sim_ch05_dc_blocker.log

echo '=== All Chapter 5 iverilog testbenches passed successfully! ==='
