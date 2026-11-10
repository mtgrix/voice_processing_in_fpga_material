#!/usr/bin/env bash
# verify_v3/run_ch02_iverilog.sh
# Runs both Chapter 2 testbenches with iverilog -g2012 -Wall
set -e

# Change to repository root if run from verify_v3/
if [ -f ../tb/v3/tb_ch02_skid_buffer.v ]; then
    cd ..
fi

echo '=== [1/2] Compiling and running tb_ch02_skid_buffer ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch02_skid tb/v3/tb_ch02_skid_buffer.v rtl/v3/ch02_skid_buffer.v
vvp sim_ch02_skid > sim_skid.log 2>&1 || true
cat sim_skid.log
if grep -q "\[FAIL\]" sim_skid.log; then
    echo "ERROR: tb_ch02_skid_buffer reported FAIL!" >&2
    rm -f sim_ch02_skid sim_skid.log
    exit 1
fi
rm -f sim_ch02_skid sim_skid.log

echo '=== [2/2] Compiling and running tb_ch02_fsm_equiv ==='
iverilog -g2012 -Wall -I rtl/v3 -o sim_ch02_fsm tb/v3/tb_ch02_fsm_equiv.v rtl/v3/ch02_fsm_binary.v rtl/v3/ch02_fsm_onehot.v
vvp sim_ch02_fsm > sim_fsm.log 2>&1 || true
cat sim_fsm.log
if grep -q "\[FAIL\]" sim_fsm.log; then
    echo "ERROR: tb_ch02_fsm_equiv reported FAIL!" >&2
    rm -f sim_ch02_fsm sim_fsm.log
    exit 1
fi
rm -f sim_ch02_fsm sim_fsm.log

rm -f sim_ch02_skid sim_ch02_fsm
echo '=== All Chapter 2 iverilog testbenches passed successfully! ==='
