"""verify_v3/ch03_exercises.py
Verifies numerical calculations for the end-of-chapter exercises in Chapter 3.
"""
import numpy as np
import scipy.signal as signal

def verify_exercises():
    print("=== CH03 EXERCISES NUMERICAL VERIFICATION ===")
    
    # Exercise 1: Kaiser tap estimate for As = 50 dB, delta_f = 500 Hz, fs = 16 kHz
    fs = 16000.0
    As = 50.0
    delta_f = 500.0
    kaiser_formula = (As - 7.95) / (14.36 * (delta_f / fs))
    taps_kaiserord, beta = signal.kaiserord(As, delta_f / (fs / 2.0))
    print("\n--- Exercise 1: Kaiser Tap Estimation ---")
    print(f"Target As = {As} dB, delta_f = {delta_f} Hz, fs = {fs} Hz")
    print(f"Kaiser formula (As - 7.95)/(14.36 * df/fs): {kaiser_formula:.2f} -> {int(np.ceil(kaiser_formula))} taps")
    print(f"scipy kaiserord: {taps_kaiserord} taps, beta = {beta:.4f}")
    
    # Exercise 2: Group delay and frame alignment
    n_taps_31 = 31
    tau_g_31 = (n_taps_31 - 1) // 2
    n_taps_63 = 63
    tau_g_63 = (n_taps_63 - 1) // 2
    s_start = 100
    hop = 160
    s_start_fir_k0 = s_start - tau_g_31
    s_start_fir_k1 = s_start + hop - tau_g_31
    print("\n--- Exercise 2: Group Delay and Grid Alignment ---")
    print(f"N = 31: Group delay = {tau_g_31} samples ({tau_g_31 / fs * 1000:.3f} ms)")
    print(f"N = 63: Group delay = {tau_g_63} samples ({tau_g_63 / fs * 1000:.3f} ms)")
    print(f"Frame 0 start original = {s_start}, with FIR alignment = {s_start_fir_k0}")
    print(f"Frame 1 start original = {s_start + hop}, with FIR alignment = {s_start_fir_k1}")
    
    # Exercise 3: Folded FIR throughput and budget
    f_clk = 50.0e6  # 50 MHz
    cycles_per_sample = 17  # 16 computation + 1 latch
    throughput_msps = (f_clk / cycles_per_sample) / 1.0e6
    time_per_sample_ns = cycles_per_sample * (1.0 / f_clk) * 1.0e9
    audio_rate = 16000.0
    realtime_budget_cycles = f_clk / audio_rate
    dsp_duty_cycle_realtime = (cycles_per_sample / realtime_budget_cycles) * 100.0
    mac_cycles_per_sample = 98543.0 / 160.0  # ~615.89 cycles/sample
    speedup_vs_mac = mac_cycles_per_sample / cycles_per_sample
    print("\n--- Exercise 3: Throughput and Budget ---")
    print(f"Clock: {f_clk/1e6:.1f} MHz, Cycles per sample: {cycles_per_sample}")
    print(f"Throughput: {throughput_msps:.3f} MSPS (Mega-samples/s)")
    print(f"Processing time per sample: {time_per_sample_ns:.1f} ns")
    print(f"Real-time audio budget at 16 kHz: {realtime_budget_cycles:.0f} cycles")
    print(f"DSP duty cycle at 16 kHz real-time: {dsp_duty_cycle_realtime:.3f}%")
    print(f"MAC bottleneck cycles/sample: {mac_cycles_per_sample:.2f} cycles")
    print(f"FIR speedup relative to MAC bottleneck: {speedup_vs_mac:.2f}x faster")
    
    # Exercise 4: Q1.15 Quantization and DC gain
    h15_float = 0.975000
    h15_q15 = int(np.round(h15_float * 32768.0))
    h15_reconstructed = h15_q15 / 32768.0
    abs_err = abs(h15_reconstructed - h15_float)
    rel_err_pct = (abs_err / h15_float) * 100.0
    
    # 31-tap Q1.15 sum
    H16 = [504, -538, 571, -604, 635, -664, 692, -717, 740, -760, 778, -793, 804, -812, 818, 31949]
    coeffs_31 = H16[:15] + [H16[15]] + H16[:15][::-1]
    sum_q15 = sum(coeffs_31)
    dc_gain = sum_q15 / 32768.0
    
    # Max DC input: x[n] = 32767
    x_dc = 32767
    acc_dc = sum(x_dc * c for c in coeffs_31)
    rounded_dc = (acc_dc + 16384) >> 15
    sat_dc = max(-32768, min(32767, rounded_dc))
    print("\n--- Exercise 4: Q1.15 Quantization and Arithmetic ---")
    print(f"h[15] float = {h15_float:.6f}, Q1.15 int = {h15_q15} (0x{h15_q15:04x})")
    print(f"Reconstructed = {h15_reconstructed:.6f}, Abs error = {abs_err:.2e}, Rel error = {rel_err_pct:.4f}%")
    print(f"Sum of 31 coefficients: {sum_q15} (DC gain = {dc_gain:.6f} or +{20*np.log10(dc_gain):.3f} dB)")
    print(f"DC test x = {x_dc}: acc = {acc_dc}")
    print(f"Rounded: {rounded_dc}, Saturated output: {sat_dc}")
    print(f"Overshoot past 32767: {rounded_dc - 32767} LSB (properly saturated to 32767: {sat_dc == 32767})")

if __name__ == '__main__':
    verify_exercises()
