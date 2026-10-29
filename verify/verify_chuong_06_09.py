#!/usr/bin/env python3
"""Verify every hand-worked number in chuong_06..09.tex."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

Q15 = 1 << 15
Q13 = 1 << 13
FS = 16_000
N = 640
TAU_MIN, TAU_MAX = 26, 214  # scan inclusive


def sat16(v: int) -> int:
    return max(-32768, min(32767, int(v)))


def q15_mul(a: int, b: int) -> int:
    return sat16((int(a) * int(b) + (1 << 14)) >> 15)


def test_ch06_classical_n8():
    print("=== Ch6 Classical Hanning N=8 (N-1) ===")
    Nc = 8
    expected = {
        0: (0.0, 0),
        1: (0.188255, 6169),
        2: (0.611260, 20029),
        3: (0.950484, 31145),
    }
    for n, (wf, wq_exp) in expected.items():
        w = 0.5 * (1.0 - np.cos(2.0 * np.pi * n / (Nc - 1)))
        # Classical table in text uses round(w*32767) for positive coeffs demo
        wq = int(round(w * 32767))
        print(f"n={n}: w={w:.6f} wq={wq}")
        assert abs(w - wf) < 1e-5
        assert wq == wq_exp
    assert q15_mul(10000, 20029) == 6112
    assert q15_mul(-10000, 20029) == -6112
    assert q15_mul(20000, 31145) == 19009
    assert q15_mul(30000, 0) == 0
    print("mul +/-10000 * 20029 -> +/-6112; 20000*31145->19009; *0->0 OK")


def test_ch06_praat_n8_and_n640():
    print("\n=== Ch6 Praat Hanning (N+1) ===")
    for i, (wf, wq_exp) in {
        1: (0.116978, 3833),
        2: (0.413176, 13539),
        3: (0.750000, 24576),
        4: (0.969846, 31780),
    }.items():
        w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / 9.0)
        wq = int(np.clip(round(w * Q15), 0, Q15 - 1))
        print(f"i={i}: w={w:.6f} wq={wq}")
        assert abs(w - wf) < 1e-5
        assert wq == wq_exp

    i = np.arange(1, N + 1, dtype=np.float64)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / (N + 1))
    wq = np.clip(np.round(w * Q15), 0, Q15 - 1).astype(np.int64)
    assert int(wq[0]) == 1 and int(wq[1]) == 3
    assert int(wq[319]) == 32767 and int(wq[320]) == 32767
    assert int(wq[638]) == 3 and int(wq[639]) == 1
    rw0 = int(np.sum(wq.astype(np.int64) * wq.astype(np.int64)))
    print(f"N=640 markers OK; Rw0_int={rw0}")
    assert rw0 == 258_100_276_868
    assert N * 16 == 10_240  # exactly 1 M10K


def test_ch07_mac_small_and_cos():
    print("\n=== Ch7 MAC small + cos frame ===")
    x = np.array([1, 2, 1, 2], dtype=np.int64)
    R = [int(np.dot(x[: 4 - t], x[t:])) for t in range(4)]
    print("R[0..3]=", R)
    assert R == [10, 6, 5, 2]

    n = np.arange(16)
    xf = np.cos(2.0 * np.pi * n / 8.0)
    xq = np.clip(np.round(xf * Q15), -32768, 32767).astype(np.int64)
    assert list(map(int, xq[:8])) == [32767, 23170, 0, -23170, -32768, -23170, 0, 23170]

    def acf(xx, tau):
        return int(np.dot(xx[: len(xx) - tau], xx[tau:]))

    R0, R8, R4 = acf(xq, 0), acf(xq, 8), acf(xq, 4)
    print(f"R0={R0}, R8={R8}, R4={R4}")
    assert R0 == 8_589_627_426
    assert R8 == 4_294_813_713
    assert R4 == -6_442_220_568
    assert abs(R8 / R0 - 0.5) < 1e-12

    # Budget: naive 189*640 vs exact sum(L-tau)
    n_naive = 189 * 640
    n_exact = sum(N - tau for tau in range(TAU_MIN, TAU_MAX + 1))
    assert n_naive == 120_960 and n_exact == 98_280
    t_exact_ms = n_exact / 50e6 * 1000
    rtf = t_exact_ms / 10.0
    print(f"N_MAC_exact={n_exact}, T={t_exact_ms:.4f} ms, RTF={rtf:.4f}")
    assert abs(t_exact_ms - 1.9656) < 1e-4
    assert abs(rtf - 0.19656) < 1e-5


def test_ch07_bfp():
    print("\n=== Ch7 BFP power 2e ===")
    # After stage overflow: m=[20,-15,5,-2], e=1; bin0 real power
    m, e = 20, 1
    power = (m * m) * (1 << (2 * e))
    assert power == 1600  # equals original 40^2
    # Mantissa y=3, e=2 -> true 3*2^{-2}; square -> 9 * 2^{-4}
    assert (3 * 2 ** (-2)) ** 2 == 9 * 2 ** (-4)
    print("BFP 2e scaling OK")


def test_ch08_C():
    print("\n=== Ch8 C[tau] ===")
    w = np.array([1.0, 2.0, 2.0, 1.0])
    Rw = [float(np.dot(w[: 4 - t], w[t:])) for t in range(4)]
    assert Rw == [10.0, 8.0, 4.0, 1.0]
    C = [Rw[0] / r for r in Rw]
    assert C == [1.0, 1.25, 2.5, 10.0]
    assert int(round(1.25 * Q13)) == 10240
    assert int(round(2.5 * Q13)) == 20480
    assert int(round(1.5 * Q13)) == 12288  # 0x3000

    w2 = np.array([1.0, 2.0, 1.0])
    assert float(np.dot(w2, w2)) / float(np.dot(w2[:1], w2[2:])) == 6.0

    # N=640 pure compensation at endpoints
    from lab_1_3_5 import compensation_rom_q13, scoring_rom_q13

    comp = compensation_rom_q13()
    score = scoring_rom_q13()
    hexc = [int(l.strip(), 16) for l in open(ROOT / "hex" / "c_tau_rom.hex")]
    assert int(comp[0]) == 8281
    assert int(comp[-1]) == 17429
    assert list(map(int, score)) == hexc  # deployed hex folds octave_cost
    print(f"C_pure[26]={int(comp[0])}, C_pure[214]={int(comp[-1])}")
    print(f"C_score[26]={hexc[0]}, C_score[214]={hexc[-1]} (matches hex)")
    assert 189 * 16 == 3024  # < 1 M10K
    assert abs(17070 / 17429 - 0.9794021458488725) < 1e-12  # octave-cost ratio @214


def test_ch09_parabolic_and_div():
    print("\n=== Ch9 parabolic + Q12.4 + divider ===")
    cases = [
        # (ym1, y0, yp1, tau*, delta, f0, q12_4)
        (0.40, 0.50, 0.46, 80, 0.214285714, 199.465705, 3191),
        (0.30, 0.55, 0.50, 100, 1.0 / 3.0, 159.468439, 2551),
        (0.48, 0.50, 0.40, 120, -1.0 / 3.0, 133.704735, 2139),
        (0.20, 0.60, 0.20, 64, 0.0, 250.0, 4000),
        (0.20, 0.60, 0.50, 101, 0.3, 157.946693, 2527),
    ]
    for ym, y0, yp, tstar, d_exp, f0_exp, q_exp in cases:
        delta = 0.5 * (ym - yp) / (ym - 2.0 * y0 + yp)
        tf = tstar + delta
        f0 = FS / tf
        q124 = int(round(f0 * 16))
        print(f"@{tstar}: d={delta:.6f} f0={f0:.4f} Q12.4={q124}")
        assert abs(delta - d_exp) < 1e-8
        assert abs(f0 - f0_exp) < 1e-4
        assert q124 == q_exp

    assert 13 // 3 == 4 and 13 % 3 == 1
    assert 16000 // 80 == 200
    # cycles available per hop
    assert int(50e6 * 0.01) == 500_000
    # Mode-B numerics matching float 0.40/0.50/0.46
    N_m, D_m = 400 - 460, 2 * (400 - 1000 + 460)
    assert N_m == -60 and D_m == -280
    assert abs(0.5 * N_m / (D_m / 2) - 3 / 14) < 1e-12
    # little-endian pack of Q12.4=3191
    q = 3191
    lo, hi = q & 0xFF, (q >> 8) & 0xFF
    assert (lo, hi) == (0x77, 0x0C)
    assert ((lo << 8) | hi) == 0x770C == 30476  # BE mis-read of LE bytes
    # Phase-2 cycle budget sketch (window+MAC+C+peak)
    n_budget = 98_280 + 640 + 189 + 300
    assert n_budget == 99_409
    assert abs(n_budget / 50e6 * 1000 - 1.98818) < 1e-4
    print("divider / Q12.4 / endian / Mode-B OK")


def test_sidelobe_db():
    print("\n=== sidelobe dB (cross-ref Ch0) ===")
    assert abs(10 ** (-13 / 20) - 0.223872) < 1e-5
    assert abs(10 ** (-32 / 20) - 0.025119) < 1e-5


if __name__ == "__main__":
    test_ch06_classical_n8()
    test_ch06_praat_n8_and_n640()
    test_ch07_mac_small_and_cos()
    test_ch07_bfp()
    test_ch08_C()
    test_ch09_parabolic_and_div()
    test_sidelobe_db()
    print("\nALL verify_chuong_06_09 PASSED")
