"""
verify_v3/ch00_exercises.py
Computes and verifies all numerical results for the exercises at the end of Chapter 0.
"""

import numpy as np

def exercise_1():
    print("=== Exercise 1: Zero-crossing failure with strong 2nd harmonic ===")
    fs = 16000
    f0 = 120
    T0 = 1.0 / f0
    T_obs = 0.05
    n_periods = T_obs / T0
    print(f"  Fundamental period T0 = {T0*1000:.2f} ms")
    print(f"  Observation window T_obs = {T_obs*1000:.1f} ms -> {n_periods:.1f} periods")
    # Equation: sin(w0 t) * (1 + 1.6 cos(w0 t)) = 0
    # Roots in [0, 2pi):
    # sin(theta) = 0 -> theta = 0, pi (2 roots)
    # cos(theta) = -1/1.6 = -0.625 -> theta = acos(-0.625) and 2pi - acos(-0.625)
    theta1 = np.arccos(-0.625)
    theta2 = 2 * np.pi - theta1
    roots = [0.0, float(theta1), np.pi, float(theta2)]
    print(f"  Roots in one period (rad): 0, {theta1:.4f}, {np.pi:.4f}, {theta2:.4f} -> {len(roots)} crossings/period")
    total_crossings = int(n_periods * len(roots))
    f_est = total_crossings / (2.0 * T_obs)
    print(f"  Total zero crossings in {T_obs}s: {total_crossings}")
    print(f"  Estimated frequency: {f_est:.1f} Hz (double the true F0 = 120 Hz!)")

def exercise_2():
    print("\n=== Exercise 2: FFT resolution and cent error ===")
    fs = 16000
    N = 640
    df = fs / N
    print(f"  FFT bin spacing df = {fs} / {N} = {df:.1f} Hz")
    f_true = 162.5
    f_bin6 = 6 * df # 150 Hz
    f_bin7 = 7 * df # 175 Hz
    delta_f_max = df / 2.0
    cent_err_high = 1200 * np.log2(f_bin7 / f_true)
    cent_err_low = 1200 * np.log2(f_true / f_bin6)
    print(f"  True frequency: {f_true} Hz, midway between bin 6 ({f_bin6} Hz) and bin 7 ({f_bin7} Hz)")
    print(f"  Max frequency error: {delta_f_max:.1f} Hz")
    print(f"  Cent error vs bin 7: {cent_err_high:.2f} cents")
    print(f"  Cent error vs bin 6: {cent_err_low:.2f} cents")

def exercise_3():
    print("\n=== Exercise 3: Window normalization on small vector ===")
    x = np.array([2, 4, 6, 6, 4, 2], dtype=float)
    w = np.array([0.25, 0.5, 1.0, 1.0, 0.5, 0.25], dtype=float)
    xw = x * w
    rxw0 = np.sum(xw**2)
    rxw2 = np.sum(xw[:4] * xw[2:])
    rw0 = np.sum(w**2)
    rw2 = np.sum(w[:4] * w[2:])
    r_unnorm = rxw2 / rxw0
    r_norm = (rxw2 / rw2) / (rxw0 / rw0)
    print(f"  xw = {xw}")
    print(f"  R_xw(0) = {rxw0:.3f}, R_xw(2) = {rxw2:.3f}")
    print(f"  R_w(0) = {rw0:.4f}, R_w(2) = {rw2:.4f}")
    print(f"  r_unnorm(2) = {r_unnorm:.4f}")
    print(f"  r_norm(2) = {r_norm:.4f}")

def exercise_4():
    print("\n=== Exercise 4: Metrics (VDE, GPE, FFE, cents) ===")
    f_ref = [120.0, 0.0, 180.0, 100.0, 220.0, 0.0]
    f_test = [121.0, 150.0, 0.0, 200.0, 225.0, 0.0]
    n_frames = len(f_ref)

    # VDE: frames where (ref > 0) != (test > 0)
    vde_frames = [i for i in range(n_frames) if (f_ref[i] > 0) != (f_test[i] > 0)]
    vde = len(vde_frames) / n_frames

    # Both voiced
    both_v = [i for i in range(n_frames) if f_ref[i] > 0 and f_test[i] > 0]
    # GPE: relative error > 20%
    gpe_frames = [i for i in both_v if abs(f_test[i] - f_ref[i]) / f_ref[i] >= 0.20]
    gpe = len(gpe_frames) / len(both_v)

    # FFE: total error frames
    ffe_frames = set(vde_frames).union(set(gpe_frames))
    ffe = len(ffe_frames) / n_frames

    # Fine cents
    fine_v = [i for i in both_v if i not in gpe_frames]
    cents = [1200 * np.log2(f_test[i] / f_ref[i]) for i in fine_v]
    mean_abs_cents = np.mean(np.abs(cents))

    print(f"  Total frames: {n_frames}")
    print(f"  VDE frames: {vde_frames} -> VDE = {len(vde_frames)}/{n_frames} = {vde*100:.2f}%")
    print(f"  Both voiced frames: {both_v}")
    print(f"  GPE frames: {gpe_frames} -> GPE = {len(gpe_frames)}/{len(both_v)} = {gpe*100:.2f}%")
    print(f"  FFE frames: {list(ffe_frames)} -> FFE = {len(ffe_frames)}/{n_frames} = {ffe*100:.2f}%")
    for idx, c in zip(fine_v, cents):
        print(f"    Frame {idx+1}: {c:+.2f} cents")
    print(f"  Mean absolute fine cents: {mean_abs_cents:.2f} cents")

def exercise_5():
    print("\n=== Exercise 5: Cycle budget and RTF at 25 MHz and 100 MHz ===")
    hop_sec = 0.010
    mac_cycles = 98543
    core_cycles = 99700

    for freq_mhz in [25, 100]:
        f_hz = freq_mhz * 1e6
        budget = int(f_hz * hop_sec)
        rtf_mac = mac_cycles / budget
        rtf_core = core_cycles / budget
        print(f"  At {freq_mhz} MHz:")
        print(f"    Budget per 10 ms hop = {budget} cycles")
        print(f"    RTF_mac = {mac_cycles}/{budget} = {rtf_mac:.4f}")
        print(f"    RTF_core = {core_cycles}/{budget} = {rtf_core:.4f}")

    # 8-channel multiplexing
    channels = 8
    total_cycles_needed = channels * core_cycles
    min_freq_hz = total_cycles_needed / hop_sec
    print(f"  8-channel multiplexing total cycles per 10 ms = {total_cycles_needed}")
    print(f"  Minimum clock frequency = {min_freq_hz / 1e6:.2f} MHz")

if __name__ == "__main__":
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    exercise_5()
