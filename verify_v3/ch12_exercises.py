#!/usr/bin/env python3
"""verify_v3/ch12_exercises.py
Computes and verifies exact numerical results for Chapter 12 exercises:
- Exercise 1: RTF scaling with clock frequency (25 MHz, 50 MHz, 100 MHz)
- Exercise 2: Double-buffering trade-offs as hop size scales (hop 160, 80, 40)
- Exercise 3: M10K block bit utilization efficiency
- Exercise 4: Cycle counter 32-bit overflow threshold and rollover duration at 50 MHz
"""

def solve_exercises():
    print("=== CH12 EXERCISES NUMERICAL VERIFICATION ===")
    
    # Exercise 1: Clock Frequency and RTF
    # Hop = 160 samples (10 ms at fs = 16 kHz)
    # Measured cycles per frame = 99,663 cycles
    measured_cycles = 99663
    clocks = [25_000_000, 50_000_000, 100_000_000]
    print("\n--- Exercise 1: RTF vs Clock Frequency (Hop 160, 10 ms deadline) ---")
    for f_clk in clocks:
        cycles_per_hop = int((f_clk / 16000) * 160)
        time_per_frame_ms = (measured_cycles / f_clk) * 1000.0
        rtf = measured_cycles / cycles_per_hop
        print(f"  f_clk = {f_clk/1e6:5.1f} MHz: Available = {cycles_per_hop:7d} ck | Frame time = {time_per_frame_ms:.3f} ms | RTF = {rtf:.4f} (Margin = {1.0/rtf:.2f}x)")

    # Exercise 2: Double-buffering impact with varying hop
    # Non-overlap: P1 (429) + P2 (641) + P3 (98,543) + P4-6 (43) + overhead (7) = 99,663 cycles
    # Overlap: P3 (98,543) + P4-6 (43) + overhead (3) = 98,589 cycles
    # Overhead saved = 1,074 cycles per frame
    hops = [160, 80, 40]
    f_clk = 50_000_000
    print("\n--- Exercise 2: Double-buffering Savings vs Hop Size at 50 MHz ---")
    for h in hops:
        hop_deadline_ck = int((f_clk / 16000) * h)
        rtf_non = 99663 / hop_deadline_ck
        rtf_ovl = 98589 / hop_deadline_ck
        speedup_pct = (1074 / 99663) * 100.0
        print(f"  Hop {h:3d} ({h/16:.1f} ms, {hop_deadline_ck:6d} ck): RTF non-overlap = {rtf_non:.4f} | RTF overlap = {rtf_ovl:.4f} | Speedup = {speedup_pct:.2f}%")

    # Exercise 3: M10K bit utilization
    # M10K = 10,240 bits
    m10k_capacity = 10240
    rams = [
        ("FIFO Vào (512x16)", 512 * 16, 1),
        ("RAM Vòng (1024x16)", 1024 * 16, 2),
        ("ROM Hanning (638x16)", 638 * 16, 2),
        ("xw_ram (638x17)", 638 * 17, 2),
        ("ROM {C,K} (189x32)", 189 * 32, 1),
        ("FIFO Ra (512x16)", 512 * 16, 1)
    ]
    print("\n--- Exercise 3: M10K Bit Utilization Efficiency ---")
    total_used_bits = 0
    total_allocated_bits = 0
    for name, used_bits, num_m10k in rams:
        allocated = num_m10k * m10k_capacity
        util = (used_bits / allocated) * 100.0
        total_used_bits += used_bits
        total_allocated_bits += allocated
        print(f"  {name:<25}: Used {used_bits:5d} bits / Allocated {allocated:5d} bits ({num_m10k} M10K) -> {util:5.1f}%")
    print(f"  Total system: Used {total_used_bits} bits / Allocated {total_allocated_bits} bits (9 M10K) -> {total_used_bits/total_allocated_bits*100:.2f}%")

    # Exercise 4: 32-bit Cycle Counter Overflow at 50 MHz
    max_count = (1 << 32) - 1
    t_rollover_s = max_count / f_clk
    t_rollover_min = t_rollover_s / 60.0
    print("\n--- Exercise 4: 32-bit Cycle Counter Rollover at 50 MHz ---")
    print(f"  Max count = 2^32 - 1 = {max_count} cycles")
    print(f"  Rollover duration: {max_count} / {f_clk} = {t_rollover_s:.3f} seconds ({t_rollover_min:.2f} minutes)")
    print(f"  Audio duration at RTF 0.199: {t_rollover_s / 0.199326:.1f} seconds ({t_rollover_s / 0.199326 / 60:.2f} minutes of speech)")

if __name__ == '__main__':
    solve_exercises()
