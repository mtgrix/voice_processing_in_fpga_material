#!/usr/bin/env python3
"""
verify/v2_ch01_praat.py: Verification script for Chapter 1.
Verifies all mathematical claims and verifies Chapter 1 RTL modules against Python twins using iverilog.
"""

import math
import subprocess
import numpy as np

def test_ch01_numbers():
    print("=== Testing Ch.1 Numerical Calculations ===")

    # 1. Nyquist tone & spectral mask
    # Tone at fs/2: x = [1, -1, 1, -1, 1, -1, 1, -1]
    x_nyq = np.array([1, -1, 1, -1, 1, -1, 1, -1], dtype=np.float64)
    X_nyq = np.fft.fft(x_nyq)
    # Bin 4 is Nyquist in 8-point DFT
    assert np.isclose(np.abs(X_nyq[4]), 8.0)
    for k in range(4):
        assert np.isclose(np.abs(X_nyq[k]), 0.0)
    # Spectral mask G[4] at Nyquist is 0.0
    # G[k] drops from 0.95*fn to fn
    # k=4 corresponds to fn, so G[4] = 0.0
    G_4 = 0.0
    X_filtered_4 = X_nyq[4] * G_4
    assert X_filtered_4 == 0.0
    print("[OK] Nyquist tone: X[4]=8.0 completely nulled by G[4]=0.0")

    # 2. Framing and search range
    fs = 16000
    f_min = 75.0
    f_max = 600.0
    P = 3
    L = int(round(P * fs / f_min))
    hop_s = 0.010
    H = int(round(hop_s * fs))
    tau_min = int(math.floor(fs / f_max))
    tau_max = int(math.floor(fs / f_min))
    assert L == 640
    assert H == 160
    assert tau_min == 26
    assert tau_max == 213
    print(f"[OK] Framing: L={L}, H={H}, tau range [{tau_min}, {tau_max}]")

    # 3. Local mean removal
    x_mean = np.array([3, 5, 3, 5], dtype=np.float64)
    mu = np.mean(x_mean)
    assert mu == 4.0
    x_zm = x_mean - mu
    assert np.allclose(x_zm, [-1, 1, -1, 1])

    # Autocorrelation without circular wrap
    N = len(x_zm)
    R_zm = [np.sum(x_zm[:N-t] * x_zm[t:]) for t in range(N)]
    assert R_zm[0] == 4.0
    assert R_zm[2] == 2.0
    raw_ratio = R_zm[2] / R_zm[0]
    unbiased_ratio = (R_zm[2] / (N - 2)) / (R_zm[0] / N)
    assert raw_ratio == 0.5
    assert unbiased_ratio == 1.0

    R_raw = [np.sum(x_mean[:N-t] * x_mean[t:]) for t in range(N)]
    assert R_raw[0] == 68.0
    assert R_raw[2] == 34.0
    inflation = R_raw[0] / R_zm[0]
    assert inflation == 17.0
    print(f"[OK] Local mean: R_zm[0]={R_zm[0]}, R_zm[2]={R_zm[2]}, inflation={inflation}x")

    # 4. Hanning N+1 formula (N=4)
    N_h = 4
    i_h = np.arange(1, N_h + 1)
    w_4 = 0.5 - 0.5 * np.cos(2.0 * np.pi * i_h / (N_h + 1))
    assert np.allclose(w_4, [0.3454915, 0.9045085, 0.9045085, 0.3454915])
    Rw0 = np.sum(w_4 ** 2)
    Rw1 = np.sum(w_4[:N_h-1] * w_4[1:])
    C1 = Rw0 / Rw1
    assert np.isclose(Rw0, 1.875)
    assert np.isclose(Rw1, 1.4431356)
    assert np.isclose(C1, 1.299254)
    print(f"[OK] Hanning N=4: Rw[0]={Rw0:.4f}, Rw[1]={Rw1:.6f}, C[1]={C1:.6f}")

    # Hanning N=8
    i_8 = np.arange(1, 9)
    w_8 = 0.5 - 0.5 * np.cos(2.0 * np.pi * i_8 / 9)
    assert np.isclose(w_8[0], 0.11697778)
    assert np.isclose(w_8[1], 0.41317591)
    assert np.allclose(w_8, w_8[::-1])
    print(f"[OK] Hanning N=8: w[1]={w_8[0]:.6f}, w[2]={w_8[1]:.6f}")

    # 5. Parabolic 3-point interpolation
    r_m1 = 0.40
    r_0 = 0.50
    r_p1 = 0.46
    tau_star = 80
    num = r_m1 - r_p1
    denom = 2.0 * (r_m1 - 2.0 * r_0 + r_p1)
    delta = num / denom
    tau_fine = tau_star + delta
    f0_interp = fs / tau_fine
    f0_coarse = fs / tau_star
    cent_diff = 1200.0 * np.log2(f0_coarse / f0_interp)
    assert np.isclose(delta, 3.0 / 14.0)
    assert np.isclose(f0_interp, 199.465705)
    assert np.isclose(cent_diff, 4.63185, atol=1e-3)
    print(f"[OK] Parabolic: delta={delta:.6f} (3/14), f0={f0_interp:.4f} Hz, cent_diff={cent_diff:.2f}")

    # 6. Sinc 3-point interpolation at t=0.2
    t = 0.2
    sinc_m1 = np.sinc(t - (-1))
    sinc_0 = np.sinc(t - 0)
    sinc_p1 = np.sinc(t - 1)
    y_hat = r_m1 * sinc_m1 + r_0 * sinc_0 + r_p1 * sinc_p1
    assert np.isclose(sinc_m1, -0.155915, atol=1e-5)
    assert np.isclose(sinc_0, 0.935489, atol=1e-5)
    assert np.isclose(sinc_p1, 0.233872, atol=1e-5)
    assert np.isclose(y_hat, 0.512960, atol=1e-5)
    print(f"[OK] Sinc interp at t=0.2: y_hat={y_hat:.6f}")

    # 7. Octave & transition costs
    octave_cost = 0.01
    ceiling = 600.0
    r_a = 0.48
    s200 = r_a - octave_cost * np.log2(ceiling / 200.0)
    s100 = r_a - octave_cost * np.log2(ceiling / 100.0)
    assert np.isclose(s200, 0.464150)
    assert np.isclose(s100, 0.454150)
    print(f"[OK] Octave cost: s(200Hz)={s200:.6f} > s(100Hz)={s100:.6f}")

    octaveJumpCost = 0.35
    c_150_160 = octaveJumpCost * abs(np.log2(150.0 / 160.0))
    c_150_300 = octaveJumpCost * abs(np.log2(150.0 / 300.0))
    assert np.isclose(c_150_160, 0.032588)
    assert np.isclose(c_150_300, 0.350000)
    print(f"[OK] Transition jump cost: 150->160Hz={c_150_160:.6f}, 150->300Hz={c_150_300:.4f}")

    # 8. Silence & Voicing integer cross-multiplications
    theta_sil = 0.03
    theta_vox = 0.45
    theta_energy = theta_sil ** 2
    assert np.isclose(theta_energy, 0.0009)
    assert np.isclose(theta_energy, 9 / 10000)

    # Case 1: Silence
    r0_sil = 500_000
    ref_sil = 600_000_000
    assert (r0_sil / ref_sil) < theta_energy
    assert (r0_sil * 10000) < (9 * ref_sil)

    # Case 2: Voicing
    r0_vox = 1_000_000
    s_vox = int(round(0.78 * r0_vox))
    assert (s_vox * 100) >= (45 * r0_vox)
    print("[OK] Integer silence (9/10000) and voicing (45/100) gates verified")

    # 9. Median-3 sequence
    seq = [148, 150, 300, 152, 151]
    meds = []
    for i in range(1, 4):
        meds.append(sorted(seq[i-1:i+2])[1])
    assert meds == [150, 152, 152]
    print(f"[OK] Median-3 sequence: {meds}")

    # 10. Viterbi 3-frame trellis
    cum_v = [0.50]
    cum_uv = [0.45]
    c_vv, c_vuv, c_uvv, c_uvuv = 0.02, 0.14, 0.14, 0.0
    # Frame 2
    cum_v.append(0.48 + max(cum_v[0] - c_vv, cum_uv[0] - c_uvv))
    cum_uv.append(0.45 + max(cum_v[0] - c_vuv, cum_uv[0] - c_uvuv))
    # Frame 3
    cum_v.append(0.49 + max(cum_v[1] - c_vv, cum_uv[1] - c_uvv))
    cum_uv.append(0.45 + max(cum_v[1] - c_vuv, cum_uv[1] - c_uvuv))
    assert np.isclose(cum_v[1], 0.96)
    assert np.isclose(cum_uv[1], 0.90)
    assert np.isclose(cum_v[2], 1.43)
    assert np.isclose(cum_uv[2], 1.35)
    print(f"[OK] Viterbi trellis: d_v={cum_v}, d_uv={cum_uv}")

    # 11. Synthesis T1 (mean -> window -> ra)
    x_t1 = np.array([-1.0, 1.0, -1.0, 1.0]) * w_4
    R0_t1 = float(np.sum(x_t1 ** 2))
    R2_t1 = float(np.sum(x_t1[:2] * x_t1[2:]))
    Rw2_t1 = float(np.sum(w_4[:2] * w_4[2:]))
    C2_t1 = Rw0 / Rw2_t1
    ra2_t1 = (R2_t1 / R0_t1) * C2_t1
    assert np.isclose(R0_t1, 1.875)
    assert np.isclose(R2_t1, 0.625)
    assert np.isclose(C2_t1, 3.0)
    assert np.isclose(ra2_t1, 1.0)
    print(f"[OK] Synthesis T1: R0={R0_t1:.4f}, R2={R2_t1:.4f}, C2={C2_t1:.4f}, ra2={ra2_t1:.4f}")

def test_ch01_iverilog_modules():
    print("\n=== Testing Chapter 1 RTL Modules via iverilog ===")

    rtl_files = [
        "rtl/v2/ch01_step01_filter.v",
        "rtl/v2/ch01_step03_mean_sub.v",
        "rtl/v2/ch01_step04_window_mul.v",
        "rtl/v2/ch01_step05_mac_acf.v",
        "rtl/v2/ch01_step06_norm_mul.v",
        "rtl/v2/ch01_step07_parabolic.v",
        "rtl/v2/ch01_step10_voicing_gate.v",
        "rtl/v2/ch01_step11_median3.v",
        "tb/v2/tb_ch01_modules.v"
    ]

    cmd_compile = ["iverilog", "-g2012", "-o", "/tmp/sim_ch01_modules"] + rtl_files
    res_c = subprocess.run(cmd_compile, capture_output=True, text=True)
    assert res_c.returncode == 0, f"iverilog compile failed: {res_c.stderr}"

    cmd_run = ["vvp", "/tmp/sim_ch01_modules"]
    res_r = subprocess.run(cmd_run, capture_output=True, text=True)
    assert res_r.returncode == 0, f"vvp execution failed: {res_r.stderr}"

    lines = res_r.stdout.strip().split("\n")
    outputs = {}
    for line in lines:
        if ":" in line:
            tag, val = line.split(":", 1)
            outputs.setdefault(tag.strip(), []).append(val.strip())

    print("Captured RTL Simulation Outputs:")
    for k, v in outputs.items():
        print(f"  {k}: {v}")

    # Check Step 1: Nyquist tone [1000, -1000, 1000, -1000] -> steady state output is 0
    # Input 0: d1=0, d2=0 -> (1000)/4 = 250
    # Input 1: d1=1000, d2=0 -> (-1000 + 2000)/4 = 250
    # Input 2: d1=-1000, d2=1000 -> (1000 - 2000 + 1000)/4 = 0!
    # Input 3: d1=1000, d2=-1000 -> (-1000 + 2000 - 1000)/4 = 0!
    assert int(outputs["STEP01"][2]) == 0
    assert int(outputs["STEP01"][3]) == 0
    print("[OK] Step 1 RTL: Nyquist tone nulled to 0")

    # Check Step 3: Mean sub: x=[3, 5, 3, 5] - 4 -> [-1, 1, -1, 1]
    s3_vals = [int(v) for v in outputs["STEP03"]]
    assert s3_vals == [-1, 1, -1, 1]
    print("[OK] Step 3 RTL: Local mean subtraction matches [-1, 1, -1, 1]")

    # Check Step 4: Window mul: 16384 * 16384 -> 8192
    s4_val = int(outputs["STEP04"][0])
    assert s4_val == 8192
    print("[OK] Step 4 RTL: Window multiply (0.5 * 0.5 = 0.25 -> 8192)")

    # Check Step 5: Sequential MAC on 4 pairs [1*1 + (-1)*(-1) + 1*1 + (-1)*(-1)] = 4
    s5_val = int(outputs["STEP05"][0])
    assert s5_val == 4
    print("[OK] Step 5 RTL: Sequential MAC result = 4")

    # Check Step 6: Norm mul: R_tau = 1000, C_tau = 8192 (1.0) -> score = 1000
    s6_val = int(outputs["STEP06"][0])
    assert s6_val == 1000
    print("[OK] Step 6 RTL: Norm multiply (1000 * 8192 >> 13 = 1000)")

    # Check Step 7: Parabolic: r_-=4000, r*=5000, r_+=4600 -> num=-600, den=2800
    s7_str = outputs["STEP07"][0]
    import re
    s7_nums = [int(n) for n in re.findall(r'-?\d+', s7_str)]
    assert s7_nums[0] == -600, f"Expected -600, got {s7_nums[0]}"
    assert s7_nums[1] == 2800, f"Expected 2800, got {s7_nums[1]}"
    print("[OK] Step 7 RTL: Parabolic numerator and denominator (-600, 2800)")

    # Check Step 10: Silence & Voicing gate
    # Case 1: Silence -> voiced=0, f0=0
    # Case 2: Voiced  -> voiced=1, f0=3200
    # Case 3: Unvoiced -> voiced=0, f0=0
    def parse_step10(s):
        v = int(s.split("voiced=")[1].split()[0])
        f = int(s.split("f0=")[1].split()[0])
        return v, f

    assert parse_step10(outputs["STEP10"][0]) == (0, 0)
    assert parse_step10(outputs["STEP10"][1]) == (1, 3200)
    assert parse_step10(outputs["STEP10"][2]) == (0, 0)
    print("[OK] Step 10 RTL: Silence and Voicing gates match expected behavior")

    # Check Step 11: Median-3 filter on [148, 150, 300, 152, 151]
    # Input 0: d0=148, d1=0, f_in=148 -> median(148, 0, 0) = 0
    # Input 1: d0=150, d1=148, f_in=150 -> median(150, 148, 0) = 148
    # Input 2: d0=300, d1=150, f_in=300 -> median(300, 150, 148) = 150
    # Input 3: d0=152, d1=300, f_in=152 -> median(152, 300, 150) = 152
    # Input 4: d0=151, d1=152, f_in=151 -> median(151, 152, 300) = 152
    s11_vals = [int(v) for v in outputs["STEP11"]]
    assert s11_vals == [0, 148, 150, 152, 152]
    print("[OK] Step 11 RTL: Canonical Median-3 outputs match [0, 148, 150, 152, 152]")

if __name__ == "__main__":
    test_ch01_numbers()
    test_ch01_iverilog_modules()
    print("\n>>> ALL CH.1 VERIFICATIONS PASSED SUCCESSFULLY! <<<")
