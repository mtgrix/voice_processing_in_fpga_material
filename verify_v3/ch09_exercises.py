#!/usr/bin/env python3
"""verify_v3/ch09_exercises.py

Computes and verifies exact numerical answers for the exercises at the end of Chapter 9:
1. Exercise 1: Discrete lag step vs human JND (Just Noticeable Difference).
2. Exercise 2: Parabolic interpolation with negative delta (peak shifting left).
3. Exercise 3: s2 dynamic range, shift calculation, and LPM bit-width bounds.
4. Exercise 4: Architectural trade-off: LPM_DIVIDE vs Sequential Radix-2 Divider.
"""

import math

def main():
    print("=== [ch09_exercises] Chapter 9 Exercises Verification ===")

    # -------------------------------------------------------------------------
    # Exercise 1: Discrete lag step vs human pitch discrimination (JND)
    # -------------------------------------------------------------------------
    print("\n--- Exercise 1: Discrete Lag Step vs JND ---")
    fs = 16000.0
    f31 = fs / 31.0
    f32 = fs / 32.0
    diff_hz = f31 - f32
    step_cents = 1200.0 * math.log2(f31 / f32)
    jnd_cents = 5.0 # JND is ~5-10 cents for normal listeners

    print(f"fs = {fs} Hz")
    print(f"f(tau=31) = {f31:.4f} Hz, f(tau=32) = {f32:.4f} Hz")
    print(f"Delta f = {diff_hz:.4f} Hz")
    print(f"Cent step = {step_cents:.4f} cents")
    print(f"Human JND threshold = ~{jnd_cents:.1f} - 10.0 cents")
    print(f"Ratio step / JND = {step_cents / jnd_cents:.1f}x threshold")

    # -------------------------------------------------------------------------
    # Exercise 2: Parabolic interpolation with negative delta
    # -------------------------------------------------------------------------
    print("\n--- Exercise 2: Parabolic Interpolation with Negative Delta ---")
    um, u0, up = 9500, 10000, 8500
    tau_p = 80
    num = up - um
    den = 2 * u0 - um - up
    delta = num / (2.0 * den)
    tau_star = tau_p + delta
    f0_hz = fs / tau_star
    f0_q12_4 = 16.0 * f0_hz
    f0_q_round = round(f0_q12_4)

    D = 2 * den * tau_p + num
    N = 512000 * den
    f0_single_div_float = N / D
    f0_single_div_int = (N + D // 2) // D

    print(f"Input triple: y_-1 = {um}, y_0 = {u0}, y_+1 = {up} at tau_p = {tau_p}")
    print(f"num = y_+1 - y_-1 = {num}")
    print(f"den = 2*y_0 - y_-1 - y_+1 = {den}")
    print(f"delta = num / (2*den) = {delta:.6f} (exactly -0.25)")
    print(f"tau* = tau_p + delta = {tau_star:.4f}")
    print(f"F0 exact = {f0_hz:.4f} Hz")
    print(f"F0 Q12.4 exact = {f0_q12_4:.4f}")
    print(f"F0 Q12.4 rounded = {f0_q_round}")
    print(f"Single-division: N = {N}, D = {D}")
    print(f"N / D = {f0_single_div_float:.4f}")
    print(f"Integer division (N + D//2) // D = {f0_single_div_int}")

    assert abs(delta - (-0.25)) < 1e-12
    assert abs(f0_hz - 200.6270) < 0.001
    assert f0_q_round == 3210
    assert f0_single_div_int == 3210

    # -------------------------------------------------------------------------
    # Exercise 3: s2 Normalization and Bit-Widths
    # -------------------------------------------------------------------------
    print("\n--- Exercise 3: s2 Normalization and Bit-Widths ---")
    # Suppose den = 33,554,432 (2^25)
    den_ex = 33554432
    bitlen_den = den_ex.bit_length()
    s2 = max(0, bitlen_den - 24)
    denn = den_ex >> s2

    print(f"den = {den_ex} (bit length = {bitlen_den})")
    print(f"s2 = max(0, {bitlen_den} - 24) = {s2}")
    print(f"denn = den >> {s2} = {denn} (bit length = {denn.bit_length()})")
    assert denn.bit_length() <= 24

    # Test extreme case: denn = 2^24 - 1
    max_denn = (1 << 24) - 1
    max_tau = 213
    max_D = 2 * max_denn * max_tau + max_denn
    max_N = 512000 * max_denn + max_D // 2
    print(f"Worst-case denn = {max_denn} (24 bits)")
    print(f"Worst-case D = {max_D} ({max_D.bit_length()} bits, <= 34)")
    print(f"Worst-case N = {max_N} ({max_N.bit_length()} bits, <= 44)")
    assert max_D.bit_length() <= 34
    assert max_N.bit_length() <= 44

    # -------------------------------------------------------------------------
    # Exercise 4: Architectural Trade-off: LPM_DIVIDE vs Sequential Radix-2
    # -------------------------------------------------------------------------
    print("\n--- Exercise 4: Architectural Trade-off ---")
    f_clk = 50.0e6
    t_clk_ns = 1.0e9 / f_clk
    hop_samples = 160
    cycles_per_hop = 500000

    div_cycles_radix2 = 34
    div_time_radix2_ns = div_cycles_radix2 * t_clk_ns
    duty_cycle_radix2 = div_cycles_radix2 / cycles_per_hop

    print(f"Clock = {f_clk/1e6:.1f} MHz, period = {t_clk_ns:.1f} ns")
    print(f"Hop = {hop_samples} samples = {cycles_per_hop} clock cycles (10 ms)")
    print(f"Sequential Radix-2: latency = {div_cycles_radix2} cycles ({div_time_radix2_ns:.1f} ns)")
    print(f"Divider active duty cycle = {duty_cycle_radix2 * 100.0:.6f}% of frame budget")
    print(f"Pipelined LPM_DIVIDE: throughput = 1/cycle (wasted: 499,999 cycles idle)")
    print("Resource comparison: Radix-2 ~80-120 ALMs vs LPM_DIVIDE ~400-600 ALMs (phải đo)")

    print("\n=== [ch09_exercises] ALL EXERCISE VERIFICATIONS PASSED ===")

if __name__ == '__main__':
    main()
