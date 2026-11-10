#!/usr/bin/env bash
# verify_v3/run_ch01_iverilog.sh
# Runs both Chapter 1 testbenches with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch01_fifo.v ]; then
    cd ..
fi

echo '=== [1/2] Compiling and running tb_ch01_fifo ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch01_fifo tb/v3/tb_ch01_fifo.v rtl/v3/ch01_avalon_fifo.v
vvp sim_ch01_fifo > sim_fifo.log 2>&1 || true
cat sim_fifo.log
if grep -q "\[FAIL\]" sim_fifo.log; then
    echo "ERROR: tb_ch01_fifo reported FAIL!" >&2
    rm -f sim_ch01_fifo sim_fifo.log
    exit 1
fi
rm -f sim_ch01_fifo sim_fifo.log

echo '=== [2/2] Compiling and running tb_ch01_fifo_out ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch01_fifo_out tb/v3/tb_ch01_fifo_out.v rtl/v3/ch01_fifo_out.v
vvp sim_ch01_fifo_out > sim_fifo_out.log 2>&1 || true
cat sim_fifo_out.log
if grep -q "\[FAIL\]" sim_fifo_out.log; then
    echo "ERROR: tb_ch01_fifo_out reported FAIL!" >&2
    rm -f sim_ch01_fifo_out sim_fifo_out.log
    exit 1
fi
rm -f sim_ch01_fifo_out sim_fifo_out.log

rm -f sim_ch01_fifo sim_ch01_fifo_out
echo '=== All Chapter 1 iverilog testbenches passed successfully! ==='
