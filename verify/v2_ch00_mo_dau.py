#!/usr/bin/env python3
"""
verify/v2_ch00_mo_dau.py: Verification script for Chapter 0.
Checks all numerical claims and verifies q15_saturate HDL against Python twin with 256 vectors.
"""

import math
import subprocess
import numpy as np

def test_ch00_numbers():
    print("=== Testing Ch.0 Numerical Values ===")
    fs = 16000
    fn = fs / 2
    f_noise = 9000
    f_alias = abs(fs - f_noise)
    assert f_alias == 7000, f"Expected 7000, got {f_alias}"
    print(f"[OK] Aliasing: {f_noise} Hz at fs={fs} Hz -> {f_alias} Hz")

    t_period_samples = fs / f_alias
    assert np.isclose(t_period_samples, 16000 / 7000)
    print(f"[OK] 7000 Hz period in samples: {t_period_samples:.4f} samples")

    # Decibels and suppression
    amp_rect = 10.0 ** (-13.0 / 20.0)
    amp_hann = 10.0 ** (-32.0 / 20.0)
    energy_rect = amp_rect ** 2
    energy_hann = amp_hann ** 2
    suppression_ratio = energy_rect / energy_hann
    print(f"[OK] -13 dB amp: {amp_rect:.6f} (~22.39%), energy: {energy_rect:.6f}")
    print(f"[OK] -32 dB amp: {amp_hann:.6f} (~2.51%), energy: {energy_hann:.6f}")
    print(f"[OK] Energy suppression ratio: {suppression_ratio:.2f}x (~79.4x)")
    assert np.isclose(amp_rect, 0.223872, atol=1e-5)
    assert np.isclose(amp_hann, 0.025119, atol=1e-5)
    assert np.isclose(suppression_ratio, 79.43, atol=0.1)

    # Framing and overlap
    f_min = 75.0
    P = 3
    L = int(round(P * fs / f_min))
    hop_s = 0.010
    H = int(round(hop_s * fs))
    overlap = (L - H) / L
    assert L == 640
    assert H == 160
    assert overlap == 0.75
    print(f"[OK] Framing: L={L}, H={H}, overlap={overlap*100:.1f}%")

    # Lags
    tau_scan_min = 26
    tau_scan_max = 214
    n_lags = tau_scan_max - tau_scan_min + 1
    assert n_lags == 189
    print(f"[OK] Lags range [{tau_scan_min}, {tau_scan_max}], count={n_lags}")

    # MAC operations: Exact vs Upper bound
    exact_mac = sum(L - tau for tau in range(tau_scan_min, tau_scan_max + 1))
    upper_bound_mac = n_lags * L
    assert exact_mac == 98280, f"Expected 98280, got {exact_mac}"
    assert upper_bound_mac == 120960, f"Expected 120960, got {upper_bound_mac}"
    print(f"[OK] MAC operations: exact={exact_mac}, upper_bound={upper_bound_mac}")

    # RTF at 50 MHz
    f_clk = 50e6
    cycles_hop = hop_s * f_clk
    assert cycles_hop == 500000
    t_exact_ms = (exact_mac / f_clk) * 1000.0
    rtf_exact = t_exact_ms / (hop_s * 1000.0)
    t_ub_ms = (upper_bound_mac / f_clk) * 1000.0
    rtf_ub = t_ub_ms / (hop_s * 1000.0)
    print(f"[OK] 50 MHz hop cycles: {cycles_hop:.0f}")
    print(f"[OK] Exact MAC compute time: {t_exact_ms:.4f} ms -> RTF = {rtf_exact:.5f} (~0.197)")
    print(f"[OK] Upper bound compute time: {t_ub_ms:.4f} ms -> RTF = {rtf_ub:.5f} (~0.242)")
    assert np.isclose(t_exact_ms, 1.9656)
    assert np.isclose(rtf_exact, 0.19656)
    assert np.isclose(t_ub_ms, 2.4192)
    assert np.isclose(rtf_ub, 0.24192)

    # DC blocker alpha and cutoff
    alpha = 1.0 - 2.0**(-8)
    assert alpha == 0.99609375
    fc = (2.0**(-8) / (2.0 * math.pi)) * fs
    print(f"[OK] DC blocker alpha = {alpha}, fc = {fc:.4f} Hz")
    assert np.isclose(fc, 9.94718)

    # M10K geometry
    m10k_depth_x16 = 512
    blocks_for_640 = math.ceil(L / m10k_depth_x16)
    assert blocks_for_640 == 2
    print(f"[OK] M10K 640x16 requires ceil(640/512) = {blocks_for_640} blocks")

def python_q15_saturate_twin(val_32: int) -> int:
    """Python twin for q15_saturate RTL: round bit 14, clamp to [-32768, 32767]."""
    # 33-bit addition with round half LSB (+16384)
    rounded = val_32 + 16384
    shifted = rounded >> 15
    if shifted > 32767:
        return 32767
    elif shifted < -32768:
        return -32768
    else:
        return shifted

def test_q15_saturate_iverilog():
    print("\n=== Testing q15_saturate RTL vs Python Twin with 256 Vectors ===")
    np.random.seed(42)
    edge_cases = [
        0,
        1073709056,
        2000000000,
        -2000000000,
        16384,
        16383,
        -16384,
        -16385,
        -536870912,
        1073730000,
        32767 * 32767,
        -32768 * -32768,
        -32768 * 32767,
        2147483647,
        -2147483648,
        32767,
        -32768
    ]
    n_rand = 256 - len(edge_cases)
    random_vectors = np.random.randint(-2147483648, 2147483647, size=n_rand, dtype=np.int64).tolist()
    test_vectors = edge_cases + [int(x) for x in random_vectors]
    assert len(test_vectors) == 256

    expected_outputs = [python_q15_saturate_twin(v) for v in test_vectors]

    # Write hex files for Verilog $readmemh
    with open("tb/v2/q15_vec_in.hex", "w") as fin, open("tb/v2/q15_vec_exp.hex", "w") as fexp:
        for v, exp in zip(test_vectors, expected_outputs):
            # 32-bit unsigned hex representation
            u32 = v & 0xFFFFFFFF
            u16 = exp & 0xFFFF
            fin.write(f"{u32:08x}\n")
            fexp.write(f"{u16:04x}\n")

    # Compile with iverilog
    cmd_compile = [
        "iverilog", "-g2012",
        "-o", "/tmp/sim_q15_saturate",
        "rtl/v2/q15_saturate.v",
        "tb/v2/tb_q15_saturate.v"
    ]
    res_c = subprocess.run(cmd_compile, capture_output=True, text=True)
    assert res_c.returncode == 0, f"iverilog compile failed: {res_c.stderr}"

    # Run simulation with vvp
    cmd_run = ["vvp", "/tmp/sim_q15_saturate"]
    res_r = subprocess.run(cmd_run, capture_output=True, text=True)
    assert res_r.returncode == 0, f"vvp execution failed: {res_r.stderr}"
    assert "PASS_ALL_256_VECTORS" in res_r.stdout, f"RTL testbench failed:\n{res_r.stdout}"

    print(f"[OK] iverilog simulation passed: 256 vectors matched 100% bit-exact with Python twin!")

if __name__ == "__main__":
    test_ch00_numbers()
    test_q15_saturate_iverilog()
    print("\n>>> ALL CH.0 VERIFICATIONS PASSED SUCCESSFULLY! <<<")
