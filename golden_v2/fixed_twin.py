"""Bit-exact integer twin of the golden_v2 FPGA core (the spec the HDL and IP paths must match).

Everything here is integer arithmetic. '>>' is Python's arithmetic (floor) shift, identical to
Verilog '>>>' on signed operands. Per frame (inputs: 638 raw int16 samples x[0..637] starting at
the Praat window start, plus the file constant GP from the HPS):

 1  mean   S = sum x[106..531] (426 samples, Praat's local-mean span)
           mean = (((S + 213 + 426*2^15) * 10_082_083) >> 32) - 2^15      == floor((S+213)/426)
 2  window d = x - mean (17 bit signed); xw = (d * w[j] + 2^14) >> 15      w = Hanning638 Q1.15 ROM
 3  peak   LP = max |xw[j]|, j = 212..425
 4  MAC    R0 = sum xw^2 ; R[tau] = sum_{j=0}^{637-tau} xw[j] xw[j+tau], tau = 26..214
 5  norm   sh = max(0, bitlen(R0) - 26); R0n = R0 >> sh; Rn = R >> sh      (27-bit operands)
 6  score  U[tau] = (Rn*C[tau] + 2^13) >> 14             (~ r(tau) * R0n, Praat's normalised ac)
           Sc[tau] = U[tau] - ((R0n*K[tau] + 2^19) >> 20)  (~ (r - 0.01 log2(600/f)) * R0n)
 7  cand   tau in 27..213 with U[tau] > U[tau-1], U[tau] >= U[tau+1], 1000 U[tau] > 225 R0n
           best = first argmax of Sc over candidates
 8  voice  voiced iff (100 Sc[best] - 45 R0n) * 3 GP > 100 R0n * max(0, 6 GP - 145 LP)
           (Praat: strength - octaveCost*log2(ceiling/f) > 0.45 + max(0, 2 - I/(0.03/1.45)), I = LP/GP)
 9  F0     num = U[b+1]-U[b-1]; den = 2U[b]-U[b-1]-U[b+1]; s2 = max(0, bitlen(den)-24)
           numn = num >> s2; denn = den >> s2; D = 2*denn*b + numn
           F0q = (512000*denn + D//2) // D        (Q12.4 Hz, = 16 * 16000 / (b + num/(2 den)))
10  out    F0q if voiced else 0; then median-3 across frames (centred, edge replicate).
Silence shortcuts: R0 == 0, LP == 0 or GP == 0 -> unvoiced.
"""
import sys
import numpy as np
import constants as K
from frames import frame_grid, window_start0
from gen_roms import hanning_q15, c_table, k_table

W = hanning_q15()
C = c_table(W)
KT = k_table()


def global_peak(x):
    n = len(x)
    s = int(np.sum(x))
    gpn = max(abs(n * int(v) - s) for v in (int(np.max(x)), int(np.min(x))))
    return (gpn + n // 2) // n


def frame_fixed(xf, gp, trace=False):
    xf = [int(v) for v in xf]
    assert len(xf) == K.NSAMP_WINDOW
    s = sum(xf[K.MEAN_OFFSET: K.MEAN_OFFSET + K.MEAN_SPAN])
    mean = (((s + K.MEAN_SPAN // 2 + K.MEAN_BIAS) * K.M_MEAN) >> K.K_MEAN) - (1 << 15)
    assert mean == (s + K.MEAN_SPAN // 2) // K.MEAN_SPAN
    xw = []
    for j, v in enumerate(xf):
        d = v - mean
        assert -(1 << 16) <= d < (1 << 16)
        xw.append((d * W[j] + (1 << 14)) >> 15)
    lp = max(abs(v) for v in xw[K.LP_FIRST: K.LP_LAST + 1])
    n = K.NSAMP_WINDOW
    r0 = sum(v * v for v in xw)
    R = {t: sum(xw[j] * xw[j + t] for j in range(n - t)) for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1)}
    out = dict(mean=mean, lp=lp, r0=r0, voiced=0, best=0, f0q=0, sc=0, sh=0)
    if trace:
        out['xw'] = xw
        out['R'] = R
    if r0 == 0 or lp == 0 or gp == 0:
        return out
    sh = max(0, r0.bit_length() - 26)
    r0n = r0 >> sh
    U, Sc = {}, {}
    for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1):
        rn = R[t] >> sh
        U[t] = (rn * C[t] + (1 << 13)) >> 14
        Sc[t] = U[t] - ((r0n * KT[t] + (1 << 19)) >> 20)
    best, bsc = 0, None
    for t in range(K.TAU_SEARCH_MIN, K.TAU_SEARCH_MAX + 1):
        if U[t] > U[t - 1] and U[t] >= U[t + 1] and 1000 * U[t] > 225 * r0n:
            if bsc is None or Sc[t] > bsc:
                best, bsc = t, Sc[t]
    out.update(sh=sh, r0n=r0n)
    if trace:
        out['U'], out['Sc'] = U, Sc
    if best == 0:
        return out
    um, u0, up = U[best - 1], U[best], U[best + 1]
    num = up - um
    den = 2 * u0 - um - up
    assert den > 0
    s2 = max(0, den.bit_length() - 24)
    numn, denn = num >> s2, den >> s2
    D = 2 * denn * best + numn
    f0q = (512000 * denn + D // 2) // D
    voiced = (100 * bsc - 45 * r0n) * 3 * gp > 100 * r0n * max(0, 6 * gp - 145 * lp)
    out.update(best=best, sc=bsc, f0q=min(f0q, 65535) if voiced else 0, voiced=int(voiced), f0q_raw=f0q)
    return out


def median3_int(seq):
    p = [seq[0]] + list(seq) + [seq[-1]]
    return [sorted(p[i:i + 3])[1] for i in range(len(seq))]


def analyse_fixed(x, trace=False):
    x = np.asarray(x, dtype=np.int64)
    gp = global_peak(x)
    _, times, lefts = frame_grid(len(x))
    starts = [window_start0(l) for l in lefts]
    frames = [frame_fixed(x[s: s + K.NSAMP_WINDOW], gp, trace) for s in starts]
    raw = [f['f0q'] for f in frames]
    return dict(times=np.array(times), starts=starts, gp=gp, frames=frames, f0q=raw, f0q_med=median3_int(raw))


if __name__ == '__main__':
    from praat_float_ref import read_wav_float
    xi, _ = read_wav_float(sys.argv[1])
    res = analyse_fixed(xi)
    for t, a, b in zip(res['times'], res['f0q'], res['f0q_med']):
        print(f"{t:.6f}\t{a / 16:.4f}\t{b / 16:.4f}")
