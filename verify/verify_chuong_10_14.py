#!/usr/bin/env python3
"""Bit-checked hand numbers for Chuong 10--14 (voicing, Avalon, Q12.4, tiers, checklist)."""
from __future__ import annotations

import math
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")


def med3(a: float, b: float, c: float) -> float:
    return max(min(a, b), min(max(a, b), c))


def pack_q124(f0_hz: float, voiced: bool = True, ceiling: int = 9600) -> tuple[int, bytes]:
    if (not voiced) or f0_hz <= 0:
        q = 0
    else:
        q = max(0, min(ceiling, int(round(f0_hz * 16.0))))
    return q, struct.pack("<H", q)


def cent(f_hw: float, f_ref: float) -> float:
    return 1200.0 * math.log2(f_hw / f_ref)


def main() -> None:
    print("=== Chuong 10: median-3 ===")
    seq = [200, 210, 80, 205, 208]
    outs = []
    for i in range(len(seq) - 2):
        a, b, c = seq[i : i + 3]
        m = med3(a, b, c)
        outs.append(m)
        print(f"  window ({a},{b},{c}) -> {m}")
    assert outs == [200, 205, 205]
    assert med3(100, 400, 110) == 110

    print("=== Chuong 10: voicing Q1.14 ===")
    V = math.floor(0.45 * (1 << 14))
    assert V == 7372
    ra, Ploc, Pglob, S = 12000, 3277, 30000, 0.03
    assert (ra >= V) and (Ploc >= S * Pglob)
    assert not ((ra >= V) and (200 >= S * Pglob))

    print("=== Chuong 10: s_UV ===")
    Pl, Pg, S, Vf = 0.02, 1.0, 0.03, 0.45
    den = S / (1.0 + Vf)
    s_uv = Vf + max(0.0, 2.0 - (Pl / Pg) / den)
    assert abs(s_uv - 1.4833333333333332) < 1e-12
    print(f"  s_UV = {s_uv}")
    s_full = Vf + max(0.0, 2.0 - (1.0) / den)
    assert abs(s_full - 0.45) < 1e-12
    print(f"  s_UV(P_local=P_global) = {s_full}")

    print("=== Chuong 10: octave jump + Viterbi 2-frame ===")
    assert abs(0.35 * abs(math.log2(150 / 160)) - 0.03258829153701851) < 1e-12
    assert abs(0.35 * abs(math.log2(150 / 300)) - 0.35) < 1e-12
    d1v, d1u, d2v, d2u = 0.50, 0.40, 0.45, 0.48
    cvv, cvu = 0.05, 0.14
    cum2v = d2v + max(d1v - cvv, d1u - cvu)
    assert abs(cum2v - 0.90) < 1e-12
    print(f"  cum(V2) = {cum2v} (path V1->V2)")
    d1v, d1u, d2v, d2u = 0.50, 0.45, 0.48, 0.45
    jump_vv, jump_vuv = 0.02, 0.14
    cum2v = d2v + max(d1v - jump_vv, d1u - jump_vuv)
    cum2u = d2u + max(d1v - jump_vuv, d1u - 0.0)
    assert abs(cum2v - 0.96) < 1e-12 and abs(cum2u - 0.90) < 1e-12
    print(f"  cum(V2)={cum2v}, cum(UV2)={cum2u}")

    print("=== Chuong 10: P_global IIR a=1/16 ===")
    a = 1.0 / 16.0
    Pg = 0.0
    expected_pg = [6.25, 18.359375, 48.4619140625]
    for i, pl in enumerate([100.0, 200.0, 500.0]):
        Pg = (1.0 - a) * Pg + a * pl
        assert abs(Pg - expected_pg[i]) < 1e-9
        print(f"  step{i}: Pl={pl} Pg={Pg}")

    print("=== Chuong 10: median pipeline delay ===")
    f1 = f2 = f3 = 0
    m_reg = f_out = 0
    raw = [200, 210, 80, 205, 208]
    fout_seq = []
    for v in raw:
        med = max(min(f1, f2), min(max(f1, f2), f3))
        new_m, new_fo = med, m_reg
        f1, f2, f3 = f2, f3, v
        m_reg, f_out = new_m, new_fo
        fout_seq.append(f_out)
    assert fout_seq == [0, 0, 0, 200, 200], fout_seq
    print(f"  f_out sequence = {fout_seq}")

    print("=== Chuong 10: octave cents ===")
    assert abs(1200.0 * math.log2(100 / 200) - (-1200.0)) < 1e-9
    assert abs(1200.0 * math.log2(400 / 200) - 1200.0) < 1e-9

    print("=== Chuong 11: Avalon-ST beat count ===")
    trace = [
        (1, 1, "A"),
        (1, 1, "B"),
        (1, 0, "C"),
        (1, 0, "C"),
        (1, 1, "C"),
        (0, 1, "-"),
        (1, 1, "D"),
    ]
    beats = sum(1 for v, r, _ in trace if v and r)
    assert beats == 4
    print(f"  beats = {beats}")
    L = 640
    assert 0 == 0 and (L - 1) == 639
    ex = [(1, 1, "X"), (1, 0, "Y"), (1, 0, "Y"), (1, 0, "Y"), (1, 1, "Y"), (1, 1, "Z")]
    assert sum(1 for v, r, _ in ex if v and r) == 3
    assert (214 - 26 + 1) == 189
    assert 189 * 640 == 120_960
    assert 50_000_000 * 0.01 == 500_000
    assert abs(120_960 / 500_000 - 0.24192) < 1e-9
    print("  tau=189, MAC budget=120960, RTF≈0.24192")

    print("=== Chuong 12: Q12.4 pack ===")
    expected = {
        0.0: (0, b"\x00\x00"),
        75.0: (1200, bytes.fromhex("b004")),
        150.0625: (2401, bytes.fromhex("6109")),
        199.466: (3191, bytes.fromhex("770c")),
        200.0: (3200, bytes.fromhex("800c")),
        220.0: (3520, bytes.fromhex("c00d")),
        440.0: (7040, bytes.fromhex("801b")),
        600.0: (9600, bytes.fromhex("8025")),
        700.0: (9600, bytes.fromhex("8025")),
        150.25: (2404, bytes.fromhex("6409")),
    }
    for f0, (q_exp, b_exp) in expected.items():
        voiced = f0 > 0
        q, b = pack_q124(f0, voiced=voiced)
        assert q == q_exp and b == b_exp, (f0, q, b.hex(), q_exp, b_exp.hex())
        print(f"  {f0} Hz -> {q} LE={b.hex(' ')}")
    q = 3200
    wrong = struct.unpack(">H", struct.pack("<H", q))[0]
    assert wrong == 32780 and abs(wrong / 16.0 - 2048.75) < 1e-9
    print(f"  endian bug: 200 Hz LE read as BE -> {wrong/16} Hz")
    assert (3200 >> 4) == 200 and (3200 & 15) == 0
    assert (3191 >> 4) == 199 and (3191 & 15) == 7
    assert abs(3191 / 16.0 - 199.4375) < 1e-12
    assert (16000 - 640) // 160 + 1 == 97
    assert 97 * 2 == 194

    print("=== Chuong 13: GPE / VDE / FFE + cent ===")
    assert abs(cent(199.466, 200.0) - (-4.628576814454318)) < 1e-9
    print(f"  cent(199.466, 200) = {cent(199.466, 200.0):.4f}")
    N = 20
    n_gpe = 2
    n_joint_voiced = 14
    gpe = n_gpe / n_joint_voiced
    n_vde = 3
    vde = n_vde / N
    n_ffe = 5
    ffe = n_ffe / N
    print(f"  GPE={gpe:.4f}, VDE={vde:.4f}, FFE={ffe:.4f}")
    assert abs(gpe - 2 / 14) < 1e-12
    assert abs(vde - 0.15) < 1e-12
    assert abs(ffe - 0.25) < 1e-12
    lsb_cent = cent(200.0625, 200.0)
    print(f"  Q12.4 LSB at 200 Hz = {lsb_cent:.4f} cent")
    assert abs(lsb_cent - 0.5409261250275985) < 1e-9

    ref = [200.0, 200.0, 0.0, 180.0, 0.0]
    hw = [199.5, 100.0, 0.0, 0.0, 50.0]
    vv = [k for k in range(5) if ref[k] > 0 and hw[k] > 0]
    gpe_n = sum(1 for k in vv if abs(hw[k] / ref[k] - 1.0) > 0.2)
    vde_n = sum(1 for k in range(5) if (ref[k] > 0) != (hw[k] > 0))
    assert vv == [0, 1] and gpe_n == 1 and vde_n == 2
    print(f"  5-frame GPE={gpe_n}/2, VDE={vde_n}/5")
    assert abs(120_960 * 97 / 50e6 - 0.2346624) < 1e-9

    print("=== Chuong 14: timing budget ===")
    cycles = 50e6 * 0.01
    assert cycles == 500_000
    rtf = 120_960 / 500_000
    print(f"  cycles/hop={cycles:.0f}, RTF_mac≈{rtf:.4f}")
    assert 640 * 16 == 10_240

    print("=== Extra LSB cents @75/@600 ===")
    c75 = cent(75.0625, 75.0)
    c600 = cent(600.0625, 600.0)
    print(f"  LSB cent @75={c75:.4f}, @600={c600:.4f}")
    assert abs(c75 - 1.442094251703702) < 1e-9
    assert abs(c600 - 0.1803274882173265) < 1e-9

    print("ALL verify_chuong_10_14 CHECKS PASSED")


if __name__ == "__main__":
    main()
