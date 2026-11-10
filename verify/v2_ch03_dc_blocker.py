#!/usr/bin/env python3
"""
verify/v2_ch03_dc_blocker.py: Verification script for Chapter 3.
Verifies all numerical claims and runs iverilog simulation against Python twin:
- Phasor clock hand at 100 Hz (speech killing without pole)
- Exact |H(f)| table at 1, 5, 10, 20, 75, 200 Hz (-3 dB at ~9.95 Hz)
- Nyquist magnitude 2 / (1 + alpha) = 1.00196 at z = -1
- Time constant alpha^256 = 0.36716 vs 1/e = 0.36788
- Step decay: sample 1280 has 109 LSB; first drops below 50 LSB at sample 1480 (49 LSB)
- Deadband on 16-bit accumulator (stuck at 255) vs clean decay on 32-bit accumulator
- Limit-cycle oscillation (+/- 4)
- Bit-exact and cycle-accurate verification of dc_block_iir.v with iverilog (1603 samples).
"""

import math
import subprocess
import numpy as np

def test_ch03_numbers():
    print("=== 1. Testing Chapter 3 Numerical Values ===")

    alpha = 1.0 - 2.0**(-8)
    assert alpha == 0.99609375
    print(f"[OK] Alpha = {alpha} (1 - 2^-8)")

    # 1. Phasor clock hand at 100 Hz with fs = 16 kHz
    fs = 16000.0
    f_test = 100.0
    omega_100 = 2.0 * math.pi * f_test / fs
    assert abs(omega_100 - 0.039269908169872414) < 1e-12
    # Magnitude of 1 - z^-1 alone: |1 - e^{-j omega}| = 2 * sin(omega / 2)
    mag_no_pole = 2.0 * math.sin(omega_100 / 2.0)
    assert abs(mag_no_pole - 0.0392673849212566) < 1e-12
    print(f"[OK] 100 Hz phasor: omega={omega_100:.5f} rad, |1 - e^(-jw)|={mag_no_pole:.5f} (~3.9% amplitude without pole)")

    # 2. Table of |H(f)| at 1, 5, 10, 20, 75, 200 Hz
    def H_mag(f, fs_val=16000.0, a=alpha):
        w = 2.0 * math.pi * f / fs_val
        z_inv = np.exp(-1j * w)
        h = (1.0 - z_inv) / (1.0 - a * z_inv)
        return abs(h), 20.0 * np.log10(abs(h))

    freqs = [1.0, 5.0, 10.0, 20.0, 75.0, 200.0]
    expected_mags = [0.10003, 0.44929, 0.70967, 0.89678, 0.99323, 1.00072]
    expected_dbs  = [-20.00,  -6.95,   -2.98,   -0.95,   -0.059,  +0.006]

    print("\n--- |H(f)| Frequency Response Table at fs=16 kHz ---")
    for f, exp_m, exp_db in zip(freqs, expected_mags, expected_dbs):
        m, db = H_mag(f)
        print(f"f = {f:3.0f} Hz: |H| = {m:.5f} ({db:+.3f} dB)")
        assert abs(m - exp_m) < 2e-4, f"Mismatch at {f} Hz: {m} vs {exp_m}"
        assert abs(db - exp_db) < 0.02, f"dB mismatch at {f} Hz: {db} vs {exp_db}"
    print("[OK] All frequency response table values verified!")

    # 3. Nyquist magnitude at z = -1 (f = fs/2 = 8000 Hz)
    mag_nyq, db_nyq = H_mag(8000.0)
    ideal_nyq = 2.0 / (1.0 + alpha)
    assert abs(ideal_nyq - 1.0019569471624265) < 1e-12
    assert abs(mag_nyq - ideal_nyq) < 1e-12
    print(f"[OK] Nyquist (z = -1): |H| = 2 / (1 + alpha) = {mag_nyq:.5f} ({db_nyq:+.4f} dB)")

    # 4. Time constant: alpha^256 vs 1/e
    alpha_256 = alpha ** 256
    inv_e = 1.0 / math.e
    assert abs(alpha_256 - 0.36715975489153624) < 1e-12
    assert abs(inv_e - 0.36787944117144233) < 1e-12
    print(f"[OK] Time constant: alpha^256 = {alpha_256:.5f} vs 1/e = {inv_e:.5f} (diff < 0.2%)")

    # 5. Cutoff frequency fc
    fc16 = (1.0 - alpha) * 16000.0 / (2.0 * math.pi)
    fc48 = (1.0 - alpha) * 48000.0 / (2.0 * math.pi)
    assert abs(fc16 - 9.94718394324346) < 1e-12
    assert abs(fc48 - 29.841551829730378) < 1e-12
    print(f"[OK] Cutoff frequencies: fc(16k) = {fc16:.3f} Hz (~9.95 Hz), fc(48k) = {fc48:.3f} Hz (~29.84 Hz)")

    # 6. Deadband on 16-bit accumulator
    def deadband_16bit(y0=255, steps=5):
        y = y0
        hist = [y]
        for _ in range(steps):
            y = y - (y >> 8)
            hist.append(y)
        return hist

    db_hist = deadband_16bit(255)
    assert db_hist == [255, 255, 255, 255, 255, 255]
    print(f"[OK] 16-bit deadband: starting at 255 stays {db_hist}")

    # 7. Bipolar limit-cycle
    def bip_limit(a=0.875, start=5.0, steps=6):
        y = float(start)
        hist = [y]
        for _ in range(steps):
            y = float(-np.round(a * y))
            hist.append(y)
        return hist

    bip_hist = bip_limit()
    assert bip_hist == [5.0, -4.0, 4.0, -4.0, 4.0, -4.0, 4.0]
    print(f"[OK] Bipolar limit cycle: starting at 5 -> {bip_hist[1:]}")

def python_dc_blocker_twin(x, alpha_shift=8):
    """Bit-exact Python twin matching RTL dc_block_iir."""
    y_acc = np.int32(0)
    x_z1  = np.int32(0)
    out   = np.empty(len(x), dtype=np.int16)
    accs  = []
    for i, xi in enumerate(np.asarray(x, dtype=np.int32)):
        dx = np.int32((xi << 15) - (x_z1 << 15))
        y_next = np.int32(y_acc + dx - (y_acc >> alpha_shift))
        y_acc = y_next
        x_z1 = xi
        y_shift = int(y_acc >> 15)
        out[i] = int(np.clip(y_shift, -32768, 32767))
        accs.append(int(y_acc))
    return out, accs

def test_ch03_step_decay():
    print("\n=== 2. Testing Step Decay & Audit Finding ===")
    x_step = np.array([0, 0, 0] + [16384] * 1600, dtype=np.int16)
    y, accs = python_dc_blocker_twin(x_step)

    # Cycle-exact table n=3..8
    expected_y = [16384, 16320, 16256, 16192, 16129, 16066]
    expected_accs = [536870912, 534773760, 532684800, 530604000, 528531329, 526466754]
    for n in range(3, 9):
        assert y[n] == expected_y[n-3], f"n={n}: y={y[n]} != {expected_y[n-3]}"
        assert accs[n] == expected_accs[n-3], f"n={n}: acc={accs[n]} != {expected_accs[n-3]}"
    print(f"[OK] Cycle-exact step response n=3..8 verified: y[3:9]={y[3:9].tolist()}")

    # Audit check: at sample 1280 (5 * 256), y is 109 LSB (not < 50)
    # The step starts at index 3, so sample 1280 of step is index 3 + 1280 = 1283
    y_1280 = y[3 + 1280]
    assert y_1280 == 109, f"Sample 1280 expected 109 LSB, got {y_1280}"
    print(f"[OK] Audit confirmed: at 1280 samples after step (5*256), y = {y_1280} LSB (NOT < 50)")

    # Find first sample dropping below 50 LSB
    sample_first_below_50 = None
    for idx in range(3, len(y)):
        if y[idx] < 50:
            sample_first_below_50 = idx - 3
            break
    assert sample_first_below_50 == 1480, f"Expected sample 1480, got {sample_first_below_50}"
    assert y[3 + 1480] == 49
    print(f"[OK] First sample dropping below 50 LSB: sample {sample_first_below_50} (y = {y[3 + 1480]} LSB)")

def test_iverilog_dc_block_iir():
    print("\n=== 3. Testing dc_block_iir HDL vs Python Twin with iverilog ===")
    x_test = [0, 0, 0] + [16384] * 1600
    expected_y, _ = python_dc_blocker_twin(x_test)

    cmd_compile = [
        "iverilog", "-g2012",
        "-o", "/tmp/sim_dc_block_iir",
        "rtl/v2/dc_block_iir.v",
        "tb/v2/tb_dc_block_iir.v"
    ]
    res_c = subprocess.run(cmd_compile, capture_output=True, text=True)
    assert res_c.returncode == 0, f"Compilation failed: {res_c.stderr}"

    res_r = subprocess.run(["vvp", "/tmp/sim_dc_block_iir"], capture_output=True, text=True)
    assert res_r.returncode == 0, f"Simulation failed: {res_r.stderr}"

    rtl_outputs = []
    for line in res_r.stdout.strip().split("\n"):
        if line.startswith("OUT_SAMPLE:"):
            parts = line.split(":")
            rtl_outputs.append(int(parts[2].strip()))

    print(f"Total samples collected from RTL: {len(rtl_outputs)}")
    assert len(rtl_outputs) == len(expected_y), f"Count mismatch: {len(rtl_outputs)} vs {len(expected_y)}"

    for i in range(len(expected_y)):
        assert rtl_outputs[i] == expected_y[i], f"Mismatch at sample {i}: RTL={rtl_outputs[i]} != Twin={expected_y[i]}"

    print(f"[OK] dc_block_iir simulation passed: {len(expected_y)} samples matched 100% bit-exact with Python twin!")

if __name__ == "__main__":
    test_ch03_numbers()
    test_ch03_step_decay()
    test_iverilog_dc_block_iir()
    print("\n>>> ALL CHAPTER 3 VERIFICATIONS PASSED (100% MATCH) <<<")
