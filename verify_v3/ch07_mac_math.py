#!/usr/bin/env python3
"""verify_v3/ch07_mac_math.py

Audits all mathematical counts and bounds for Chapter 7:
1. MAC operations:
   - tau = 26..214: sum_{tau=26}^{214} (638 - tau) = 97,902
   - With R[0]: 97,902 + 638 = 98,540
   - v1 comparison (N = 640): sum = 98,280; with R[0] = 98,920
2. Cycle count and latency:
   - 98,540 issue pairs + 3 pipeline stages = 98,543 cycles/frame
   - 50 MHz clock budget: 500,000 cycles/hop
   - MAC RTF = 98,543 / 500,000 = 0.197086 (~19.7% of budget)
3. Bit-width bounds:
   - xw in [-65535, 65535] (17-bit signed)
   - Max product = 65535^2 = 4,294,836,225 (< 2^32)
   - Max sum of 638 products = 2,740,105,511,550 (< 2^41.32)
   - Needs 43-bit signed (magnitude < 2^42 = 4,398,046,511,104)
   - Cyclone V DSP hard accumulator: 64-bit wide; we retain 48-bit signed
4. Hand calculation trace:
   - xw = [2, -3, 4, 1], R[1] = -14, R[2] = 5
"""

import sys
import math

def main():
    print("=" * 78)
    print("CH07 MAC OPERATIONS AND CYCLE BUDGET AUDIT")
    print("=" * 78)

    # 1. MAC Counts
    N_v2 = 638
    tau_min, tau_max = 26, 214
    n_lags = tau_max - tau_min + 1

    mac_scan_v2 = sum(N_v2 - tau for tau in range(tau_min, tau_max + 1))
    mac_total_v2 = mac_scan_v2 + N_v2

    N_v1 = 640
    mac_scan_v1 = sum(N_v1 - tau for tau in range(tau_min, tau_max + 1))
    mac_total_v1 = mac_scan_v1 + N_v1

    print(f"Window length N (v2)        : {N_v2} samples")
    print(f"Lag range                   : {tau_min}..{tau_max} ({n_lags} lags)")
    print(f"MACs for tau=26..214 (v2)   : {mac_scan_v2} (formula: {n_lags} * ({N_v2 - tau_min} + {N_v2 - tau_max}) / 2 = {n_lags * (N_v2 - tau_min + N_v2 - tau_max) // 2})")
    print(f"Total MACs with R[0] (v2)   : {mac_total_v2} (97902 + 638 = 98540)")
    print(f"MACs for tau=26..214 (v1)   : {mac_scan_v1} (N=640)")
    print(f"Total MACs with R[0] (v1)   : {mac_total_v1} (98280 + 640 = 98920)")
    print(f"Difference (v1 - v2 scan)   : {mac_scan_v1 - mac_scan_v2} MACs")
    print(f"Difference (v1 - v2 total)  : {mac_total_v1 - mac_total_v2} MACs")

    assert mac_scan_v2 == 97902
    assert mac_total_v2 == 98540
    assert mac_scan_v1 == 98280
    assert mac_total_v1 == 98920

    # 2. Cycle Counts and Real-Time Budget
    pipeline_latency = 3  # 1 M10K read + 1 DSP input reg + 1 DSP accum reg
    total_cycles_v2 = mac_total_v2 + pipeline_latency
    f_clk = 50_000_000
    fs = 16_000
    hop = 160
    cycles_per_sample = f_clk // fs
    cycles_per_hop = hop * cycles_per_sample
    rtf_mac = total_cycles_v2 / cycles_per_hop

    print("\n" + "=" * 78)
    print("REAL-TIME BUDGET AND LATENCY ANALYSIS (50 MHz, hop 160)")
    print("=" * 78)
    print(f"Clock frequency f_clk       : {f_clk:,} Hz (period T_clk = {1e9/f_clk:.1f} ns)")
    print(f"Sampling frequency fs       : {fs:,} Hz")
    print(f"Cycles per audio sample     : {cycles_per_sample} cycles")
    print(f"Cycles per hop (160 samples): {cycles_per_hop:,} cycles")
    print(f"Pipeline latency            : {pipeline_latency} cycles")
    print(f"Total cycles per frame      : {total_cycles_v2:,} cycles ({mac_total_v2:,} issue + {pipeline_latency} latency)")
    print(f"MAC Core RTF                : {rtf_mac:.6f} ({rtf_mac * 100:.2f}% of real-time budget)")
    print(f"Remaining budget for system : {100.0 - rtf_mac * 100:.2f}% ({cycles_per_hop - total_cycles_v2:,} cycles)")

    assert total_cycles_v2 == 98543

    # 3. Bit-width Bound Derivation
    max_xw = 65535  # 17-bit signed magnitude limit
    max_prod = max_xw * max_xw
    max_sum_638 = 638 * max_prod
    bits_mag = math.log2(max_sum_638)
    bits_signed = bits_mag + 1

    print("\n" + "=" * 78)
    print("BIT-WIDTH BOUND AND ACCUMULATOR SIZING DERIVATION")
    print("=" * 78)
    print(f"Maximum |xw|                : {max_xw:,} (17-bit signed)")
    print(f"Maximum product |p|         : {max_prod:,} (< 2^32 = {1 << 32:,})")
    print(f"Product bit-width           : 34 bits signed")
    print(f"Maximum 638-term sum        : {max_sum_638:,}")
    print(f"log2(max_sum_638)           : {bits_mag:.4f} magnitude bits")
    print(f"Minimum signed width needed : ceil({bits_signed:.4f}) = {math.ceil(bits_signed)} bits (43 bits)")
    print(f"2^42 (bound for 43-bit)     : {1 << 42:,}")
    print(f"Safety margin (2^42 / max)  : {(1 << 42) / max_sum_638:.2f}x (guaranteed no overflow)")
    print(f"Cyclone V DSP accumulator   : 64 bits hardwired")
    print(f"Output width chosen         : 48 bits (holds 43 bits with 5 guard bits, 0 extra ALMs)")

    assert math.ceil(bits_signed) == 43

    # 4. Hand calculation 4 samples
    xw = [2, -3, 4, 1]
    # R[1] = 2*(-3) + (-3)*4 + 4*1 = -6 - 12 + 4 = -14
    # R[2] = 2*4 + (-3)*1 = 8 - 3 = 5
    r1 = xw[0]*xw[1] + xw[1]*xw[2] + xw[2]*xw[3]
    r2 = xw[0]*xw[2] + xw[1]*xw[3]
    print("\n" + "=" * 78)
    print("HAND CALCULATION TRACE (xw = [2, -3, 4, 1])")
    print("=" * 78)
    print(f"R[1] = 2*(-3) + (-3)*4 + 4*1 = {r1}")
    print(f"R[2] = 2*4 + (-3)*1          = {r2}")
    assert r1 == -14
    assert r2 == 5

    # Trace table simulation of the 8 cycles (agenda 4.3)
    print("\nDetailed cycle-by-cycle trace:")
    print("Cycle | Addr (sload,last) | RAM data | DSP in (sload_r) | Prod p | Accum acc | out_valid")
    print("-" * 78)
    # Pipeline stages:
    # addr -> RAM out -> DSP reg -> Accum
    trace_data = [
        # cyc, addr, ram, dsp_in, p, acc, out_vld
        (0, "(0,1) sload=1 last=0", "-", "-", "-", "-", 0),
        (1, "(1,2) sload=0 last=0", "2, -3", "-", "-", "-", 0),
        (2, "(2,3) sload=0 last=1", "-3, 4", "2, -3 (sload=1)", "-6", "-", 0),
        (3, "(0,2) sload=1 last=0", "4, 1", "-3, 4 (sload=0)", "-12", "-6", 0),
        (4, "(1,3) sload=0 last=1", "2, 4", "4, 1 (sload=0)", "4", "-18", 0),
        (5, "-", "-3, 1", "2, 4 (sload=1)", "8", "-14 [R1]", 1),
        (6, "-", "-", "-3, 1 (sload=0)", "-3", "8", 0),
        (7, "-", "-", "-", "-", "5 [R2]", 1)
    ]
    for row in trace_data:
        print(f"  {row[0]:2d}  | {row[1]:20s} | {row[2]:8s} | {row[3]:17s} | {row[4]:6s} | {row[5]:10s} | {row[6]:9d}")
    print("=" * 78)

if __name__ == "__main__":
    main()
