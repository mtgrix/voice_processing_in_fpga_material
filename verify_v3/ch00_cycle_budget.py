#!/usr/bin/env python3
"""verify_v3/ch00_cycle_budget.py
Derive and verify the exact cycle budget for Chapter 0:
- 50 MHz clock -> 20 ns
- fs = 16 kHz -> 3125 cycles/sample
- hop = 160 samples (10 ms) -> 500,000 cycles/hop
- N = 638, tau in 26..214 (189 lags)
- sum(638 - tau) arithmetic series
- MAC cycles with R[0] and latency
- RTF calculation
"""

def run():
    f_clk = 50_000_000
    fs = 16000
    cycles_per_sample = f_clk // fs
    hop = 160
    cycles_per_hop = hop * cycles_per_sample
    
    print("=== Cycle Budget from First Principles ===")
    print(f"Clock frequency: {f_clk / 1e6:.1f} MHz (T_clk = {1e9/f_clk:.1f} ns)")
    print(f"Audio sampling rate: {fs} Hz (T_s = {1e6/fs:.2f} us)")
    print(f"Cycles available per audio sample: {f_clk} / {fs} = {cycles_per_sample} cycles")
    print(f"Hop size: {hop} samples ({hop / fs * 1000:.1f} ms)")
    print(f"Cycles available per hop (real-time budget): {hop} * {cycles_per_sample} = {cycles_per_hop} cycles")
    
    N = 638
    tau_min = 26
    tau_max = 214
    num_lags = tau_max - tau_min + 1
    
    print("\n=== MAC Count Derivation ===")
    print(f"Window length: N = {N}")
    print(f"Lags: tau = {tau_min} .. {tau_max} ({num_lags} lags)")
    
    # Arithmetic series derivation:
    # sum_{tau=26}^{214} (N - tau) = num_lags * N - sum_{tau=26}^{214} tau
    sum_tau = num_lags * (tau_min + tau_max) // 2
    sum_N = num_lags * N
    mac_lags = sum_N - sum_tau
    
    # Verify with direct sum:
    mac_lags_direct = sum(N - tau for tau in range(tau_min, tau_max + 1))
    assert mac_lags == mac_lags_direct
    
    print(f"sum(tau) for tau in {tau_min}..{tau_max} = {num_lags} * ({tau_min} + {tau_max}) / 2 = {num_lags} * {tau_min + tau_max} / 2 = {sum_tau}")
    print(f"{num_lags} * {N} = {sum_N}")
    print(f"MACs for lags 26..214: {sum_N} - {sum_tau} = {mac_lags} MACs")
    
    mac_r0 = N
    total_mac_pairs = mac_lags + mac_r0
    print(f"Energy R[0] MACs: {mac_r0} MACs")
    print(f"Total MAC pairs issued per frame: {mac_lags} + {mac_r0} = {total_mac_pairs} pairs")
    
    # Pipeline latency of MAC DSP block:
    # 1 cycle input register + 1 cycle multiply/accumulate + 1 cycle output register = 3 cycles
    pipeline_latency = 3
    mac_total_cycles = total_mac_pairs + pipeline_latency
    print(f"MAC pipeline latency: {pipeline_latency} cycles")
    print(f"Total cycles from first pair issued to final R[214] valid: {total_mac_pairs} + {pipeline_latency} = {mac_total_cycles} cycles")
    
    rtf_mac = mac_total_cycles / cycles_per_hop
    print(f"MAC Real-Time Factor (RTF): {mac_total_cycles} / {cycles_per_hop} = {rtf_mac:.6f} (approx {rtf_mac:.3f})")
    
    # Full core estimate (from Agenda 12.2):
    # - Local mean (426 samples): 426 + 3 = 429 cycles
    # - Subtract mean, Hanning window, localPeak LP (638 samples): 638 + 3 = 641 cycles
    # - MAC (R0 + 189 lags): 98,543 cycles
    # - C, K ROM scaling and peak finding: overlaps MAC, tail ~ 20 cycles
    # - Parabolic interpolation and division: ~ 40-60 cycles
    # - Voicing decision and median-3: ~ 10 cycles
    # Total core cycles ~ 99,700 cycles
    core_total_cycles = 99700
    rtf_core = core_total_cycles / cycles_per_hop
    print(f"\nEstimated total core cycles: {core_total_cycles} cycles")
    print(f"Core RTF: {core_total_cycles} / {cycles_per_hop} = {rtf_core:.6f} (approx {rtf_core:.3f})")

if __name__ == '__main__':
    run()
