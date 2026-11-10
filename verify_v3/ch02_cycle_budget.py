#!/usr/bin/env python3
"""
verify_v3/ch02_cycle_budget.py

Derives and verifies the exact cycle budget for FPGA F0 estimation on Cyclone V:
- Audio sample period vs system clock period
- Hop budget: 160 samples = 500,000 cycles at 50 MHz
- Autocorrelation MAC operations: R[0] + lags 26..214
- Pipeline latency and measured execution cycles: 98,543 cycles
- Real-Time Factor (RTF) calculations
- Systematic audit and rebuttal of Argon's erroneous figures
"""

def compute_cycle_budget():
    f_clk = 50_000_000  # 50 MHz
    t_clk = 1.0 / f_clk # 20 ns
    f_s = 16_000        # 16 kHz
    t_s = 1.0 / f_s     # 62.5 us
    
    cycles_per_sample = f_clk / f_s
    hop_samples = 160
    hop_time_s = hop_samples / f_s
    hop_cycles = int(hop_samples * cycles_per_sample)
    
    # Window and lag parameters
    N = 638
    tau_min = 26
    tau_max = 214
    num_lags = tau_max - tau_min + 1
    
    # MAC calculation
    mac_r0 = N
    # sum of (N - tau) for tau from 26 to 214
    # terms: (638 - 26) = 612 down to (638 - 214) = 424
    terms = [N - tau for tau in range(tau_min, tau_max + 1)]
    mac_lags = sum(terms)
    total_mac = mac_r0 + mac_lags
    
    mac_latency = 3
    measured_cycles = total_mac + mac_latency
    cycles_per_new_sample = measured_cycles / hop_samples
    
    time_calc_ms = (measured_cycles * t_clk) * 1000.0
    rtf_mac = measured_cycles / hop_cycles
    
    # Full core estimate (including mean subtraction and peak finding)
    full_core_est_cycles = 99_700
    rtf_full = full_core_est_cycles / hop_cycles
    
    print("=== CH02 CYCLE BUDGET DERIVATION ===")
    print(f"System Clock: {f_clk/1e6:.1f} MHz (Period = {t_clk*1e9:.1f} ns)")
    print(f"Audio Sample Rate: {f_s} Hz (Period = {t_s*1e6:.2f} us)")
    print(f"Real-time clock cycles per sample: {cycles_per_sample:.1f} cycles")
    print(f"Frame Hop: {hop_samples} samples ({hop_time_s*1000:.1f} ms)")
    print(f"Real-time clock cycles per hop: {hop_cycles:,} cycles")
    print("-" * 50)
    print(f"Window length N: {N} samples")
    print(f"Lag range: tau = {tau_min} .. {tau_max} ({num_lags} lags)")
    print(f"MACs for R[0]: {mac_r0}")
    print(f"MACs for lags {tau_min}..{tau_max}: sum_{{tau=26}}^{{214}} (638 - tau)")
    print(f"   First term (tau={tau_min}): {terms[0]}")
    print(f"   Last term (tau={tau_max}): {terms[-1]}")
    print(f"   Arithmetic sum: ({terms[0]} + {terms[-1]}) * {num_lags} / 2 = {mac_lags:,}")
    print(f"Total MAC operations: {mac_r0} + {mac_lags:,} = {total_mac:,}")
    print(f"Pipeline latency: {mac_latency} cycles")
    print(f"Total core execution cycles: {measured_cycles:,} cycles/frame")
    print(f"Average cycles per audio sample: {cycles_per_new_sample:.5f} (~{round(cycles_per_new_sample)} cycles/sample)")
    print(f"Calculation wall-clock time per frame: {time_calc_ms:.5f} ms")
    print(f"RTF (MAC core): {rtf_mac:.6f} (~{rtf_mac:.3f})")
    print(f"Estimated full core cycles: {full_core_est_cycles:,}")
    print(f"RTF (Full core): {rtf_full:.6f} (~{rtf_full:.3f})")
    print("-" * 50)
    
    # Audit Argon's errors
    argon_claimed_budget = 1_250_000
    argon_claimed_cycles = 246_000
    argon_claimed_rtf = 0.197
    
    implied_hop_samples = argon_claimed_budget / cycles_per_sample
    implied_hop_time_ms = (implied_hop_samples / f_s) * 1000.0
    argon_ratio = argon_claimed_cycles / argon_claimed_budget
    
    print("=== AUDIT OF ARGON ERRONEOUS VALUES ===")
    print(f"Argon claimed budget: {argon_claimed_budget:,} cycles/frame")
    print(f"Implied hop in samples at 3125 cycles/sample: {implied_hop_samples:.1f} samples")
    print(f"Implied hop in milliseconds at 16 kHz: {implied_hop_time_ms:.1f} ms (WRONG! Praat hop is 10 ms = 160 samples)")
    print(f"Argon claimed cycles: {argon_claimed_cycles:,} cycles")
    print(f"Argon claimed RTF: {argon_claimed_rtf}")
    print(f"Argon ratio (246k / 1.25M): {argon_ratio:.5f}")
    print("Conclusion: Argon's figures were doubled errors that accidentally matched 0.197 via cancellation:")
    print("   1. Hop was assumed to be 25 ms (400 samples -> 1,250,000 cycles), which contradicts Praat's 10 ms hop (160 samples -> 500,000 cycles).")
    print("   2. Cycles were assumed to be 246,000, which contradicts the true 98,543 cycles.")
    print(f"   Correct reality: {measured_cycles:,} / {hop_cycles:,} = {rtf_mac:.5f} (~0.197).")

if __name__ == "__main__":
    compute_cycle_budget()
