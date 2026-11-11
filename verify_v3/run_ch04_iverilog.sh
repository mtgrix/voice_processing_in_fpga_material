#!/usr/bin/env bash
# verify_v3/run_ch04_iverilog.sh
# Runs Chapter 4 testbench with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch04_ring_buffer.v ]; then
    cd ..
fi

echo '=== Compiling and running tb_ch04_ring_buffer ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch04_ring_buffer tb/v3/tb_ch04_ring_buffer.v rtl/v3/ch04_ring_buffer.v
vvp sim_ch04_ring_buffer > sim_ch04_ring_buffer.log 2>&1 || true
cat sim_ch04_ring_buffer.log
if grep -q "\[FAIL\]" sim_ch04_ring_buffer.log; then
    echo "ERROR: tb_ch04_ring_buffer reported FAIL!" >&2
    rm -f sim_ch04_ring_buffer sim_ch04_ring_buffer.log
    exit 1
fi
rm -f sim_ch04_ring_buffer sim_ch04_ring_buffer.log

echo '=== All Chapter 4 iverilog testbenches passed successfully! ==='
