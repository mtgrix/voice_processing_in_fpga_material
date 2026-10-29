#!/usr/bin/env python3
"""
verify_chuong_00_01.py: Verification script for all numerical calculations
in chuong_00_mo_dau.tex and chuong_01_praat.tex.
Runs stand-alone and asserts/prints exact values.
"""

import numpy as np

def test_decibel_and_nyquist():
    print("=== 1. Decibel & Nyquist ===")
    fs = 16000
    fn = fs / 2
    f_in = 9000
    f_alias = abs(fs - f_in)
    print(f"fs = {fs} Hz, Nyquist fn = {fn} Hz")
    print(f"Input tone = {f_in} Hz -> Aliased tone = {f_alias} Hz")
    assert f_alias == 7000

    db_hanning = -32.0
    amp_hanning = 10.0 ** (db_hanning / 20.0)
    print(f"-32 dB amplitude ratio = {amp_hanning:.6f} (approx 1/{1/amp_hanning:.2f})")

    db_rect = -13.0
    amp_rect = 10.0 ** (db_rect / 20.0)
    print(f"-13 dB amplitude ratio = {amp_rect:.6f} (approx 1/{1/amp_rect:.2f})")

def test_local_mean_removal():
    print("\n=== 2. Local Mean Removal ===")
    x = np.array([3, 5, 3, 5], dtype=np.float64)
    mu = np.mean(x)
    x_zm = x - mu
    print(f"x = {x}, mean = {mu}, x_zm = {x_zm}")
    assert mu == 4.0
    assert np.allclose(x_zm, [-1, 1, -1, 1])

    # Unbiased / Non-circular ACF:
    # R[tau] = sum_{n=0}^{N-1-tau} x[n] x[n+tau]
    N = len(x)
    R_zm = [np.sum(x_zm[:N-tau] * x_zm[tau:]) for tau in range(N)]
    print(f"R_zm[0] = {R_zm[0]}, R_zm[2] = {R_zm[2]}")
    assert R_zm[0] == 4.0
    assert R_zm[2] == 2.0

    raw_ratio_zm = R_zm[2] / R_zm[0]
    unbiased_ratio_zm = (R_zm[2] / (N - 2)) / (R_zm[0] / N)
    print(f"Raw ratio R_zm[2]/R_zm[0] = {raw_ratio_zm}")
    print(f"Unbiased ratio = {unbiased_ratio_zm}")
    assert raw_ratio_zm == 0.5
    assert unbiased_ratio_zm == 1.0

    # Without mean removal:
    R_x = [np.sum(x[:N-tau] * x[tau:]) for tau in range(N)]
    print(f"R_x[0] = {R_x[0]}, R_x[2] = {R_x[2]}")
    assert R_x[0] == 68.0
    assert R_x[2] == 34.0
    amplification = R_x[0] / R_zm[0]
    print(f"R_x[0] / R_zm[0] amplification = {amplification}")
    assert amplification == 17.0

def test_hanning_praat_n4():
    print("\n=== 3. Praat Hanning N=4 (N+1 formula) ===")
    N = 4
    i = np.arange(1, N + 1)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / (N + 1))
    print(f"w = {w}")
    # Verify symmetry
    assert np.allclose(w, [0.3454915, 0.9045085, 0.9045085, 0.3454915])

    Rw0 = np.sum(w ** 2)
    Rw1 = np.sum(w[:N-1] * w[1:])
    C1 = Rw0 / Rw1
    print(f"Rw[0] = {Rw0:.6f}")
    print(f"Rw[1] = {Rw1:.6f}")
    print(f"C[1] = Rw[0]/Rw[1] = {C1:.6f}")
    assert np.isclose(Rw0, 1.875)
    assert np.isclose(Rw1, 1.4431356)
    assert np.isclose(C1, 1.299254)

def test_dft_8_manual():
    print("\n=== 4. DFT 8-point manual step-by-step ===")
    # Signal: x = [1, 1, 1, 1, 0, 0, 0, 0] (rectangular pulse of 4 samples)
    x = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=np.float64)
    N = 8
    X = np.fft.fft(x)
    print("k | Re X[k] | Im X[k] | |X[k]|^2")
    for k in range(N):
        re = np.real(X[k])
        im = np.imag(X[k])
        pwr = np.abs(X[k])**2
        print(f"{k} | {re:8.4f} | {im:8.4f} | {pwr:8.4f}")

    # Theoretical values for x=[1,1,1,1,0,0,0,0]:
    # k=0: sum = 4, im = 0, pwr = 16
    # k=1: Re = 1 + cos(pi/4) + cos(pi/2) + cos(3pi/4) = 1 + sqrt(2)/2 + 0 - sqrt(2)/2 = 1.0
    #      Im = -(sin(pi/4) + sin(pi/2) + sin(3pi/4)) = -(sqrt(2)/2 + 1 + sqrt(2)/2) = -(1 + sqrt(2)) = -2.41421356
    #      |X[1]|^2 = 1^2 + (1 + sqrt(2))^2 = 1 + (1 + 2sqrt(2) + 2) = 4 + 2sqrt(2) approx 6.828427
    # k=2: Re = 1 + cos(pi/2) + cos(pi) + cos(3pi/2) = 1 + 0 - 1 + 0 = 0.0
    #      Im = -(sin(pi/2) + sin(pi) + sin(3pi/2)) = -(1 + 0 - 1) = 0.0
    #      |X[2]|^2 = 0.0
    # k=3: Re = 1 + cos(3pi/4) + cos(3pi/2) + cos(9pi/4) = 1 - sqrt(2)/2 + 0 + sqrt(2)/2 = 1.0
    #      Im = -(sin(3pi/4) + sin(3pi/2) + sin(9pi/4)) = -(sqrt(2)/2 - 1 + sqrt(2)/2) = -(sqrt(2) - 1) = 1 - sqrt(2) approx -0.41421356
    #      |X[3]|^2 = 1^2 + (sqrt(2)-1)^2 = 1 + (2 - 2sqrt(2) + 1) = 4 - 2sqrt(2) approx 1.171573
    # k=4: Re = 1 - 1 + 1 - 1 = 0.0, Im = 0.0, |X[4]|^2 = 0.0
    # Parseval: sum(|x|^2) = 4. 1/8 * sum(|X|^2) = 1/8 * (16 + 2*(4+2sqrt(2)) + 0 + 2*(4-2sqrt(2)) + 0)
    #           = 1/8 * (16 + 8 + 4sqrt(2) + 8 - 4sqrt(2)) = 1/8 * 32 = 4.0!
    sum_x2 = np.sum(x**2)
    sum_X2_div_N = np.sum(np.abs(X)**2) / N
    print(f"Parseval check: sum(|x|^2) = {sum_x2}, (1/N)*sum(|X|^2) = {sum_X2_div_N}")
    assert np.isclose(sum_x2, sum_X2_div_N)
    assert np.isclose(np.real(X[1]), 1.0)
    assert np.isclose(np.imag(X[1]), -(1 + np.sqrt(2)))
    assert np.isclose(np.abs(X[2])**2, 0.0)

def test_parabolic_and_sinc():
    print("\n=== 5. Parabolic & Sinc Interpolation ===")
    tau_star = 80
    ym1 = 0.40
    y0 = 0.50
    yp1 = 0.46

    # Parabolic delta
    num = ym1 - yp1
    denom = 2.0 * (ym1 - 2.0 * y0 + yp1)
    delta = num / denom
    tau_fine = tau_star + delta
    fs = 16000
    f0 = fs / tau_fine
    f0_raw = fs / tau_star
    cent_diff = 1200.0 * np.log2(f0_raw / f0)
    print(f"num = {num:.4f}, denom = {denom:.4f}, delta = {delta:.6f}")
    print(f"tau_fine = {tau_fine:.6f}, f0 = {f0:.4f} Hz, f0_raw = {f0_raw:.4f} Hz")
    print(f"Difference in cent = {cent_diff:.2f} cent")
    assert np.isclose(delta, 3.0 / 14.0)
    assert np.isclose(tau_fine, 80 + 3.0/14.0)
    assert np.isclose(f0, 199.465705)

    # Sinc 3-point approximation at t = 0.2:
    # y(t) = sum_{k=-1}^1 y_k * sinc(t - k)
    t = 0.2
    sinc_m1 = np.sinc(t - (-1))  # np.sinc(x) is sin(pi*x)/(pi*x)
    sinc_0  = np.sinc(t - 0)
    sinc_p1 = np.sinc(t - 1)
    y_hat = ym1 * sinc_m1 + y0 * sinc_0 + yp1 * sinc_p1
    print(f"sinc(1.2) = {sinc_m1:.6f}, sinc(0.2) = {sinc_0:.6f}, sinc(-0.8) = {sinc_p1:.6f}")
    print(f"y_hat(0.2) = {y_hat:.6f}")
    assert np.isclose(sinc_m1, -0.15591488)
    assert np.isclose(sinc_0, 0.93548928)
    assert np.isclose(sinc_p1, 0.23387232)
    assert np.isclose(y_hat, 0.512960)

def test_octave_and_transition_costs():
    print("\n=== 6. Octave & Transition Costs ===")
    octave_cost = 0.01
    ceiling = 600.0
    r_a = 0.48

    # Octave cost
    # s = r_a - octave_cost * log2(ceiling / f0)
    s200 = r_a - octave_cost * np.log2(ceiling / 200.0)
    s100 = r_a - octave_cost * np.log2(ceiling / 100.0)
    s500 = r_a - octave_cost * np.log2(ceiling / 500.0)
    s600 = r_a - octave_cost * np.log2(ceiling / 600.0)
    print(f"s(200 Hz) = {s200:.6f}")
    print(f"s(100 Hz) = {s100:.6f}")
    print(f"s(500 Hz) = {s500:.6f}")
    print(f"s(600 Hz) = {s600:.6f}")
    assert np.isclose(s200, 0.464150)
    assert np.isclose(s100, 0.454150)

    # Transition cost
    octaveJumpCost = 0.35
    vuvCost = 0.14
    c_150_160 = octaveJumpCost * abs(np.log2(150.0 / 160.0))
    c_150_300 = octaveJumpCost * abs(np.log2(150.0 / 300.0))
    print(f"Jump 150->160 Hz cost = {c_150_160:.6f}")
    print(f"Jump 150->300 Hz cost = {c_150_300:.6f}")
    assert np.isclose(c_150_160, 0.032588)
    assert np.isclose(c_150_300, 0.35)

def test_silence_and_voicing():
    print("\n=== 7. Silence & Voicing Thresholds ===")
    silence_threshold = 0.03
    voicing_threshold = 0.45
    denom = silence_threshold / (1.0 + voicing_threshold)
    print(f"Threshold denom = {denom:.6f}")

    # Case 1: local/global = 0.02
    ratio1 = 0.02 / denom
    s_uv1 = voicing_threshold + max(0.0, 2.0 - ratio1)
    print(f"Case 1 (local=0.02): ratio = {ratio1:.6f}, s_uv = {s_uv1:.6f}")
    assert np.isclose(s_uv1, 1.483333)

    # Case 2: local/global = 0.8
    ratio2 = 0.8 / denom
    s_uv2 = voicing_threshold + max(0.0, 2.0 - ratio2)
    print(f"Case 2 (local=0.8): ratio = {ratio2:.6f}, s_uv = {s_uv2:.6f}")
    assert np.isclose(s_uv2, 0.45)

def test_viterbi_trellis():
    print("\n=== 8. Viterbi 3-frame Trellis ===")
    delta_v = [0.50, 0.48, 0.49]
    delta_uv = [0.45, 0.45, 0.45]
    c_vv = 0.02
    c_uv_v = 0.14
    c_v_uv = 0.14
    c_uv_uv = 0.0

    cum_v = [0.0]*3
    cum_uv = [0.0]*3
    bp_v = [None]*3
    bp_uv = [None]*3

    # Frame 1
    cum_v[0] = delta_v[0]
    cum_uv[0] = delta_uv[0]

    # Frame 2
    from_v_to_v = cum_v[0] - c_vv
    from_uv_to_v = cum_uv[0] - c_uv_v
    if from_v_to_v >= from_uv_to_v:
        cum_v[1] = delta_v[1] + from_v_to_v
        bp_v[1] = 'V'
    else:
        cum_v[1] = delta_v[1] + from_uv_to_v
        bp_v[1] = 'UV'

    from_v_to_uv = cum_v[0] - c_v_uv
    from_uv_to_uv = cum_uv[0] - c_uv_uv
    if from_v_to_uv >= from_uv_to_uv:
        cum_uv[1] = delta_uv[1] + from_v_to_uv
        bp_uv[1] = 'V'
    else:
        cum_uv[1] = delta_uv[1] + from_uv_to_uv
        bp_uv[1] = 'UV'

    # Frame 3
    from_v_to_v = cum_v[1] - c_vv
    from_uv_to_v = cum_uv[1] - c_uv_v
    if from_v_to_v >= from_uv_to_v:
        cum_v[2] = delta_v[2] + from_v_to_v
        bp_v[2] = 'V'
    else:
        cum_v[2] = delta_v[2] + from_uv_to_v
        bp_v[2] = 'UV'

    from_v_to_uv = cum_v[1] - c_v_uv
    from_uv_to_uv = cum_uv[1] - c_uv_uv
    if from_v_to_uv >= from_uv_to_uv:
        cum_uv[2] = delta_uv[2] + from_v_to_uv
        bp_uv[2] = 'V'
    else:
        cum_uv[2] = delta_uv[2] + from_uv_to_uv
        bp_uv[2] = 'UV'

    print(f"t=1: cum(V)={cum_v[0]:.2f}, cum(UV)={cum_uv[0]:.2f}")
    print(f"t=2: cum(V)={cum_v[1]:.2f} (bp={bp_v[1]}), cum(UV)={cum_uv[1]:.2f} (bp={bp_uv[1]})")
    print(f"t=3: cum(V)={cum_v[2]:.2f} (bp={bp_v[2]}), cum(UV)={cum_uv[2]:.2f} (bp={bp_uv[2]})")

    assert np.isclose(cum_v[1], 0.96)
    assert np.isclose(cum_uv[1], 0.90)
    assert np.isclose(cum_v[2], 1.43)
    assert np.isclose(cum_uv[2], 1.35)

def test_hardware_budget():
    print("\n=== 9. Hardware Budgets & Timing ===")
    fs = 16000
    f_min = 75.0
    f_max = 600.0
    n_periods = 3
    L = int(round(n_periods * fs / f_min))
    hop_time_s = 0.010
    H = int(round(hop_time_s * fs))
    overlap = (L - H) / L
    tau_scan_min = 26
    tau_scan_max = 214
    n_scan_lags = tau_scan_max - tau_scan_min + 1
    tau_min = 27
    tau_max = 213
    n_search_lags = tau_max - tau_min + 1

    print(f"L = {L}, H = {H}, overlap = {overlap*100:.1f}%")
    print(f"Scan lags: [{tau_scan_min}, {tau_scan_max}] ({n_scan_lags} lags)")
    print(f"Search lags: [{tau_min}, {tau_max}] ({n_search_lags} lags)")
    assert L == 640
    assert H == 160
    assert overlap == 0.75
    assert n_scan_lags == 189
    assert n_search_lags == 187

    # Memory budget:
    frame_bits = L * 16
    m10k_capacity = 10240
    print(f"Frame memory: {L} x 16 bit = {frame_bits} bits = {frame_bits / m10k_capacity:.2f} M10K block")
    assert frame_bits == m10k_capacity

    c_tau_bits = n_scan_lags * 16
    print(f"C[tau] ROM: {n_scan_lags} x 16 bit = {c_tau_bits} bits")

    # Timing and RTF:
    f_clk_50 = 50e6
    cycles_in_hop_50 = hop_time_s * f_clk_50
    mac_cycles = L * n_scan_lags
    time_mac_50_s = mac_cycles / f_clk_50
    rtf_50 = time_mac_50_s / hop_time_s
    print(f"Clock 50 MHz: {cycles_in_hop_50:.0f} cycles in 10 ms hop")
    print(f"MAC operations: {mac_cycles} multiplications")
    print(f"Time for MAC at 50 MHz: {time_mac_50_s*1000:.2f} ms")
    print(f"RTF at 50 MHz: {rtf_50:.4f}")
    assert cycles_in_hop_50 == 500000
    assert mac_cycles == 120960
    assert np.isclose(time_mac_50_s * 1000, 2.4192)
    assert np.isclose(rtf_50, 0.24192)


def test_ch01_synthesis_T1():
    print("\n=== 10. Ch.1 Synthesis T1 (mean -> window -> ra) ===")
    N = 4
    i = np.arange(1, N + 1)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / (N + 1))
    x_zm = np.array([-1.0, 1.0, -1.0, 1.0])
    xt = x_zm * w
    R0 = float(np.sum(xt ** 2))
    R2 = float(np.sum(xt[: N - 2] * xt[2:]))
    Rw0 = float(np.sum(w ** 2))
    Rw2 = float(np.sum(w[: N - 2] * w[2:]))
    C2 = Rw0 / Rw2
    ra2 = (R2 / R0) * C2
    print(f"R0={R0:.6f}, R2={R2:.6f}, C2={C2:.6f}, ra2={ra2:.6f}")
    assert np.isclose(R0, 1.875)
    assert np.isclose(R2, 0.625)
    assert np.isclose(C2, 3.0)
    assert np.isclose(ra2, 1.0)


def test_ch01_hanning_n8_edges():
    print("\n=== 11. Ch.1 Hanning N=8 edges ===")
    N = 8
    i = np.arange(1, N + 1)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / (N + 1))
    print(f"w[1]={w[0]:.6f}, w[2]={w[1]:.6f}")
    assert np.isclose(w[0], 0.116977778440511)
    assert np.isclose(w[1], 0.4131759111665348)
    assert np.allclose(w, w[::-1])


def test_soft_upsample_nyquist_tone():
    print("\n=== 12. Soft upsample Nyquist-grid tone DFT ===")
    x = np.array([1, 0, -1, 0, 1, 0, -1, 0], dtype=np.float64)
    X = np.fft.fft(x)
    assert np.isclose(np.abs(X[2]) ** 2, 16.0)
    assert np.isclose(np.abs(X[4]) ** 2, 0.0)
    print("k=2 |X|^2 = 16; k=4 Nyquist |X|^2 = 0 --- OK")



def test_viterbi_perturbed_exercise():
    print("\n=== 13. Viterbi exercise s2(V)=0.20 ===")
    s_v = [0.50, 0.20, 0.49]
    s_uv = [0.45, 0.45, 0.45]
    c_vv, c_vuv, c_uvv, c_uvuv = 0.02, 0.14, 0.14, 0.0
    d_v = [s_v[0]]
    d_uv = [s_uv[0]]
    d_v.append(s_v[1] + max(d_v[0] - c_vv, d_uv[0] - c_uvv))
    d_uv.append(s_uv[1] + max(d_v[0] - c_vuv, d_uv[0] - c_uvuv))
    d_v.append(s_v[2] + max(d_v[1] - c_vv, d_uv[1] - c_uvv))
    d_uv.append(s_uv[2] + max(d_v[1] - c_vuv, d_uv[1] - c_uvuv))
    print(f"d_v={d_v}, d_uv={d_uv}")
    assert np.isclose(d_v[1], 0.68)
    assert np.isclose(d_uv[1], 0.90)
    assert np.isclose(d_v[2], 1.25)
    assert np.isclose(d_uv[2], 1.35)



def test_integer_silence_voicing_gates():
    """Derive Silence/Voicing integer compares from float rules (Ch.1 §1.10)."""
    print("\n=== 16. Integer Silence / Voicing gates from float ===")
    theta_sil = 0.03
    theta_energy = theta_sil ** 2
    assert np.isclose(theta_energy, 0.0009)
    assert np.isclose(9 / 10000, theta_energy)

    # Silence: R0/Eref < 0.0009 <=> R0*10000 < 9*Eref
    R0, Eref = 500_000, 600_000_000
    assert (R0 / Eref) < theta_energy
    assert R0 * 10000 < 9 * Eref
    R0_loud = int(0.8 * Eref)
    assert not (R0_loud * 10000 < 9 * Eref)

    # Voicing: best_score is S = r_a * R0 (C-compensated energy), NOT dimensionless r_a
    theta_vox = 0.45
    R0 = 1_000_000
    S_voiced = int(round(0.78 * R0))
    S_unvoiced = int(round(0.30 * R0))
    assert S_voiced * 100 >= 45 * R0
    assert S_unvoiced * 100 < 45 * R0
    # exact boundary
    assert 4500 * 100 == 45 * 10_000
    # trap: dimensionless r_a must not enter the integer test
    assert not (0.78 * 100 >= 45 * R0)
    print("silence 9/10000 and voicing 45/100 gates OK; scale trap confirmed")


def test_silence_energy_db():
    print("\n=== 14. Silence energy threshold dB ===")
    theta = 0.03 ** 2
    db = 10.0 * np.log10(theta)
    print(f"theta={theta}, dB={db:.6f}")
    assert np.isclose(theta, 0.0009)
    assert np.isclose(db, -30.457575, atol=1e-3)


def test_median3_exercise():
    print("\n=== 15. Median-3 exercise ===")
    seq = [148, 150, 300, 152, 151]
    meds = []
    for i in range(1, 4):
        w = sorted(seq[i - 1 : i + 2])
        meds.append(w[1])
    print("meds", meds)
    assert meds == [150, 152, 152]


if __name__ == "__main__":
    test_decibel_and_nyquist()
    test_local_mean_removal()
    test_hanning_praat_n4()
    test_dft_8_manual()
    test_parabolic_and_sinc()
    test_octave_and_transition_costs()
    test_silence_and_voicing()
    test_viterbi_trellis()
    test_hardware_budget()
    test_ch01_synthesis_T1()
    test_ch01_hanning_n8_edges()
    test_soft_upsample_nyquist_tone()
    test_viterbi_perturbed_exercise()
    test_silence_energy_db()
    test_integer_silence_voicing_gates()
    test_median3_exercise()
    print("\nALL NUMERICAL TESTS PASSED SUCCESSFULLY!")
