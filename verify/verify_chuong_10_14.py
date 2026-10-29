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
    assert med3(100, 400, 110) == 110  # sorted 100,110,400 — kills spike 400

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
    # local==global: silence term does not fire
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

    # 3-frame Praat-like (phan_b numbers)
    d1v, d1u, d2v, d2u = 0.50, 0.45, 0.48, 0.45
    jump_vv, jump_vuv = 0.02, 0.14
    cum2v = d2v + max(d1v - jump_vv, d1u - jump_vuv)
    cum2u = d2u + max(d1v - jump_vuv, d1u - 0.0)
    assert abs(cum2v - 0.96) < 1e-12 and abs(cum2u - 0.90) < 1e-12
    print(f"  cum(V2)={cum2v}, cum(UV2)={cum2u}")

    print("=== Chuong 11: Avalon-ST beat count ===")
    # cycles: (valid, ready, data_held_after)
    # After correct backpressure: 4 beats for {A,B,C,D}
    trace = [
        (1, 1, "A"),  # beat A
        (1, 1, "B"),  # beat B
        (1, 0, "C"),  # hold C
        (1, 0, "C"),  # hold C
        (1, 1, "C"),  # beat C
        (0, 1, "-"),  # source gap
        (1, 1, "D"),  # beat D
    ]
    beats = sum(1 for v, r, _ in trace if v and r)
    assert beats == 4
    print(f"  beats = {beats}")

    # SOP/EOP: packet of L=640 samples
    L = 640
    sop_idx, eop_idx = 0, L - 1
    assert sop_idx == 0 and eop_idx == 639
    print(f"  SOP @ beat {sop_idx}, EOP @ beat {eop_idx}")

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
        700.0: (9600, bytes.fromhex("8025")),  # sat
        150.25: (2404, bytes.fromhex("6409")),
    }
    for f0, (q_exp, b_exp) in expected.items():
        voiced = f0 > 0
        q, b = pack_q124(f0, voiced=voiced)
        assert q == q_exp and b == b_exp, (f0, q, b.hex(), q_exp, b_exp.hex())
        print(f"  {f0} Hz -> {q} LE={b.hex(' ')}")
    # endian mistake
    q = 3200
    wrong = struct.unpack(">H", struct.pack("<H", q))[0]
    assert wrong == 32780 and abs(wrong / 16.0 - 2048.75) < 1e-9
    print(f"  endian bug: 200 Hz LE read as BE -> {wrong/16} Hz")

    print("=== Chuong 13: GPE / VDE / FFE + cent ===")
    assert abs(cent(199.466, 200.0) - (-4.628576814454318)) < 1e-9
    print(f"  cent(199.466, 200) = {cent(199.466, 200.0):.4f}")
    # Toy confusion: 20 frames
    # ref voiced: 16, unvoiced: 4
    # hw: 2 octave errors among voiced-voiced, 1 false voiced, 2 false unvoiced
    N = 20
    n_gpe = 2  # |Fhw/Fref - 1| > 0.2 among jointly voiced
    n_joint_voiced = 14
    gpe = n_gpe / n_joint_voiced
    n_vde = 3  # voicing decision mismatches
    vde = n_vde / N
    # FFE often = fraction of frames with either VDE or GPE
    n_ffe = 5  # 3 VDE + 2 GPE (disjoint in this toy)
    ffe = n_ffe / N
    print(f"  GPE={gpe:.4f}, VDE={vde:.4f}, FFE={ffe:.4f}")
    assert abs(gpe - 2 / 14) < 1e-12
    assert abs(vde - 0.15) < 1e-12
    assert abs(ffe - 0.25) < 1e-12

    lsb_cent = cent(200.0625, 200.0)
    print(f"  Q12.4 LSB at 200 Hz = {lsb_cent:.4f} cent")
    assert abs(lsb_cent - 0.5409261250275985) < 1e-9

    print("=== Chuong 14: timing budget ===")
    cycles = 50e6 * 0.01
    assert cycles == 500_000
    rtf = 120_960 / 500_000
    print(f"  cycles/hop={cycles:.0f}, RTF_mac≈{rtf:.4f}")

    print("ALL verify_chuong_10_14 CHECKS PASSED")


if __name__ == "__main__":
    main()
