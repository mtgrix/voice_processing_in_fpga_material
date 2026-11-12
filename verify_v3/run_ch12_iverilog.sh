#!/usr/bin/env bash
# verify_v3/run_ch12_iverilog.sh
# Runs iverilog simulations for Chapter 12 (Top-Level System Integration)
# Exits non-zero if compilation fails or any [FAIL] appears.

set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch12_top.v ]; then
    cd ..
fi

echo "=== [ch12] Compiling tb_ch12_top with iverilog -g2012 -Wall ==="
iverilog -g2012 -Wall -I rtl/v3 \
    -o verify_v3/sim_ch12_top \
    tb/v3/tb_ch12_top.v \
    rtl/v3/ch12_top.v \
    rtl/v3/ch01_avalon_fifo.v \
    rtl/v3/ch01_fifo_out.v \
    rtl/v3/ch03_fir_filter.v \
    rtl/v3/ch04_ring_buffer.v \
    rtl/v3/ch05_local_mean.v \
    rtl/v3/ch06_hanning_window.v \
    rtl/v3/ch06_hanning_rom.v \
    rtl/v3/ch07_mac_engine.v \
    rtl/v3/ch07_mac_unit.v \
    rtl/v3/ch07_xw_ram.v \
    rtl/v3/ch08_norm_score.v \
    rtl/v3/ch08_ck_rom.v \
    rtl/v3/ch09_f0_calc.v \
    rtl/v3/ch09_peak_finder.v \
    rtl/v3/ch09_radix2_div.v \
    rtl/v3/ch10_voicing.v \
    rtl/v3/ch11_median3.v

echo "=== [ch12] Running simulation vvp sim_ch12_top ==="
vvp verify_v3/sim_ch12_top > verify_v3/ch12_top_iverilog.log 2>&1
cat verify_v3/ch12_top_iverilog.log

# Check for failure tokens
if grep -q "\[FAIL\]" verify_v3/ch12_top_iverilog.log; then
    echo "=== [ch12] ERROR: Simulation tb_ch12_top detected [FAIL] conditions! ==="
    exit 1
fi

if ! grep -q "\[PASS\] All [0-9]\+ cycles matched bit-for-bit with Python twin\!" verify_v3/ch12_top_iverilog.log; then
    echo "=== [ch12] ERROR: Expected success banner not found in ch12_top_iverilog.log! ==="
    exit 1
fi

echo "=== [ch12] tb_ch12_top PASSED (0 errors) ==="
rm -f verify_v3/sim_ch12_top
