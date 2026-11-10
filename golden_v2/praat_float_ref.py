"""Float64 port of Praat 7.0.03 'To Pitch (raw autocorrelation)' (method AC_HANNING).

Ported line-by-line from fon/Sound_to_Pitch.cpp (Sound_into_PitchFrame, Sound_to_Pitch_any),
fon/Pitch.cpp (Pitch_pathFinder), melder/NUMinterpol.cpp (NUM_interpolate_sinc,
NUMimproveExtremum) and dwsys/NUM2.cpp (NUMminimize_brent).

Only intentional difference from Praat: the autocorrelation of the frame and of the window is
computed by direct summation instead of a 1024-point FFT (identical up to ~1e-15 rounding).

Modes
  path='R1'  : full Viterbi path finder with Praat defaults (octave-jump 0.35, V/UV 0.14)
  path='R2'  : same path finder with octave-jump = V/UV = 0 -> per-frame argmax of local cost
               (this is what our FPGA does, before the median-3 post filter)
Run as a script:  python3 praat_float_ref.py file.wav [R1|R2]
"""
import math
import sys
import numpy as np

import constants as K
from frames import frame_grid, window_start0, mean_start0

GOLDEN = 1.0 - 0.6180339887498948482045868343656381177203
SQRT_EPS = math.sqrt(np.finfo(float).eps)


# ---------------------------------------------------------------- NUM_interpolate_sinc
def interpolate_sinc(y, x, max_depth):
    """y is a 1-based sequence given as python list with y[0] unused; size = len(y)-1."""
    size = len(y) - 1
    midleft = math.floor(x)
    midright = midleft + 1
    if x < 1:
        return y[1]
    if x > size:
        return y[size]
    if x == midleft:
        return y[midleft]
    if max_depth > midright - 1:
        max_depth = midright - 1
    if max_depth > size - midleft:
        max_depth = size - midleft
    if max_depth <= 0:          # NUM_VALUE_INTERPOLATE_NEAREST
        return y[int(math.floor(x + 0.5))]
    if max_depth == 1:          # LINEAR
        return y[midleft] + (x - midleft) * (y[midright] - y[midleft])
    if max_depth == 2:          # CUBIC
        yl, yr = y[midleft], y[midright]
        dyl = 0.5 * (yr - y[midleft - 1])
        dyr = 0.5 * (y[midright + 1] - yl)
        fil = x - midleft
        fir = midright - x
        return yl * fir + yr * fil - fil * fir * (0.5 * (dyr - dyl) + (fil - 0.5) * (dyl + dyr - 2 * (yr - yl)))
    left = midright - max_depth
    right = midleft + max_depth
    depth = max_depth + 0.5
    result = 0.0
    # left half, recurrence exactly as in Praat
    a = math.pi * (x - midleft)
    halfsina = 0.5 * math.sin(a)
    aa = a / depth
    cosaa = math.cos(aa)
    sinaa = math.sin(aa)
    daa = math.pi / depth
    cosdaa = math.cos(daa)
    sindaa = math.sin(daa)
    for ix in range(midleft, left - 1, -1):
        d = halfsina / a * (1.0 + cosaa)
        result += y[ix] * d
        a += math.pi
        cosaa, sinaa = cosaa * cosdaa - sinaa * sindaa, sinaa * cosdaa + cosaa * sindaa
        halfsina = - halfsina
    a = math.pi * (midright - x)
    halfsina = 0.5 * math.sin(a)
    aa = a / depth
    cosaa = math.cos(aa)
    sinaa = math.sin(aa)
    for ix in range(midright, right + 1):
        d = halfsina / a * (1.0 + cosaa)
        result += y[ix] * d
        a += math.pi
        cosaa, sinaa = cosaa * cosdaa - sinaa * sindaa, sinaa * cosdaa + cosaa * sindaa
        halfsina = - halfsina
    return result


# ---------------------------------------------------------------- NUMminimize_brent
def minimize_brent(f, a, b, tol=1e-10):
    v = a + GOLDEN * (b - a)
    fv = f(v)
    x = w = v
    fx = fw = fv
    for _ in range(60):
        middle = (a + b) / 2.0
        tol_act = SQRT_EPS * abs(x) + tol / 3.0
        rng = b - a
        if abs(x - middle) + rng / 2.0 <= 2.0 * tol_act:
            return x, fx
        new_step = GOLDEN * (b - x if x < middle else a - x)
        if abs(x - w) >= tol_act:
            t = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * t
            q = 2.0 * (q - t)
            if q > 0.0:
                p = -p
            else:
                q = -q
            if abs(p) < abs(new_step * q) and p > q * (a - x + 2.0 * tol_act) and p < q * (b - x - 2.0 * tol_act):
                new_step = p / q
        if abs(new_step) < tol_act:
            new_step = tol_act if new_step > 0.0 else -tol_act
        t = x + new_step
        ft = f(t)
        if ft <= fx:
            if t < x:
                b = x
            else:
                a = x
            v, w, x = w, x, t
            fv, fw, fx = fw, fx, ft
        else:
            if t < x:
                a = t
            else:
                b = t
            if ft <= fw or w == x:
                v, w = w, t
                fv, fw = fw, ft
            elif ft <= fv or v == x or v == w:
                v, fv = t, ft
    return x, fx


def improve_maximum(y, ixmid, value_depth):
    size = len(y) - 1
    if ixmid <= 1:
        return 1.0, y[1]
    if ixmid >= size:
        return float(size), y[size]
    xr, fr = minimize_brent(lambda xx: -interpolate_sinc(y, xx, value_depth), ixmid - 1, ixmid + 1, 1e-10)
    return xr, -fr


# ---------------------------------------------------------------- per-frame analysis
def hanning_window():
    n = K.NSAMP_WINDOW
    i = np.arange(1, n + 1, dtype=float)
    return 0.5 - 0.5 * np.cos(2 * np.pi * i / (n + 1))


def lin_autocorr(v, maxlag):
    n = len(v)
    return np.array([np.dot(v[: n - k], v[k:]) for k in range(maxlag + 1)])


class PraatRawAc:
    def __init__(self, max_candidates=K.MAX_CANDIDATES, silence=K.SILENCE_THRESHOLD,
                 voicing=K.VOICING_THRESHOLD, octave=K.OCTAVE_COST,
                 octave_jump=K.OCTAVE_JUMP_COST, vuv=K.VOICED_UNVOICED_COST):
        self.maxn = max(max_candidates, math.floor(K.PITCH_CEILING / K.PITCH_FLOOR))
        self.silence, self.voicing, self.octave = silence, voicing, octave
        self.octave_jump, self.vuv = octave_jump, vuv
        self.window = hanning_window()
        wr = lin_autocorr(self.window, K.BRENT_IXMAX)
        self.windowR = wr / wr[0]

    def frame(self, z, left, global_peak):
        """z: float samples (0-based numpy). left: Praat 1-based leftSample. Returns dict."""
        n, h = K.NSAMP_WINDOW, K.HALFNSAMP_WINDOW
        m0 = mean_start0(left)
        local_mean = 0.0
        for i in range(m0, m0 + K.MEAN_SPAN):      # sequential sum, same order as Praat
            local_mean += z[i]
        local_mean /= K.MEAN_SPAN
        s0 = window_start0(left)
        fr = (z[s0: s0 + n] - local_mean) * self.window
        local_peak = float(np.max(np.abs(fr[K.LP_FIRST: K.LP_LAST + 1])))
        intensity = 1.0 if local_peak > global_peak else local_peak / global_peak
        cands = [[0.0, 0.0]]          # [frequency, strength]; candidate 1 = voiceless
        imax = [0]
        out = dict(intensity=intensity, local_peak=local_peak, local_mean=local_mean)
        if local_peak == 0.0:
            out['cands'] = cands
            return out
        ac = lin_autocorr(fr, K.BRENT_IXMAX)
        rpos = ac / (ac[0] * self.windowR)
        rpos[0] = 1.0
        # r[-319..319] as 1-based vector of size 639: rv[k] = r[k-320]
        offset = -K.BRENT_IXMAX - 1
        rv = [0.0] * (2 * K.BRENT_IXMAX + 2)
        for k in range(1, 2 * K.BRENT_IXMAX + 2):
            lag = k + offset
            rv[k] = rpos[abs(lag)]
        r = rpos
        fs = 1.0 / K.DX
        i = 2
        while i < K.MAXIMUM_LAG and i < K.BRENT_IXMAX:
            if r[i] > 0.5 * self.voicing and r[i] > r[i - 1] and r[i] >= r[i + 1]:
                place = 0
                dr = 0.5 * (r[i + 1] - r[i - 1])
                d2r = (r[i] - r[i - 1]) + (r[i] - r[i + 1])
                fmax = 1.0 / K.DX / (i + dr / d2r)
                smax = interpolate_sinc(rv, 1.0 / K.DX / fmax - offset, 30)
                if smax > 1.0:
                    smax = 1.0 / smax
                if len(cands) < self.maxn:
                    cands.append([0.0, 0.0]); imax.append(0)
                    place = len(cands)
                else:
                    weakest = 2.0
                    for iw in range(2, self.maxn + 1):
                        c = cands[iw - 1]
                        ls = c[1] - self.octave * math.log2(K.PITCH_FLOOR / c[0])
                        if ls < weakest:
                            weakest, place = ls, iw
                    if smax - self.octave * math.log2(K.PITCH_FLOOR / fmax) <= weakest:
                        place = 0
                if place:
                    cands[place - 1] = [fmax, smax]
                    imax[place - 1] = i
            i += 1
        # second pass
        for ic in range(2, len(cands) + 1):
            c = cands[ic - 1]
            depth = 700 if c[0] > 0.3 / K.DX else 70
            xmid, ymid = improve_maximum(rv, imax[ic - 1] - offset, depth)
            xmid += offset
            c[0] = 1.0 / K.DX / xmid
            if ymid > 1.0:
                ymid = 1.0 / ymid
            c[1] = ymid
        out['cands'] = cands
        out['r'] = r
        return out

    def path_finder(self, frames, dt):
        ceiling = K.PITCH_CEILING
        tsc = 0.01 / dt
        ojc, vuv = self.octave_jump * tsc, self.vuv * tsc
        nf = len(frames)
        voiced = lambda f: f > 0.0 and f < ceiling
        delta, psi = [], []
        for fr in frames:
            us = 0.0 if self.silence <= 0 else 2.0 - fr['intensity'] / (self.silence / (1.0 + self.voicing))
            us = self.voicing + max(0.0, us)
            delta.append([us if not voiced(f) else s - self.octave * math.log2(ceiling / f) for f, s in fr['cands']])
            psi.append([0] * len(fr['cands']))
        for it in range(1, nf):
            prev, cur = frames[it - 1]['cands'], frames[it]['cands']
            pd = delta[it - 1]
            newd = []
            for i2, (f2, _) in enumerate(cur):
                maximum, place = -1e30, 0
                for i1, (f1, _) in enumerate(prev):
                    pv, cv = not voiced(f1), not voiced(f2)
                    if cv:
                        tc = 0.0 if pv else vuv
                    else:
                        tc = vuv if pv else ojc * abs(math.log2(f1 / f2))
                    value = pd[i1] - tc + delta[it][i2]
                    if value > maximum:
                        maximum, place = value, i1
                newd.append(maximum)
                psi[it][i2] = place
            delta[it] = newd
        place = 0
        maximum = delta[-1][0]
        for ic in range(1, len(delta[-1])):
            if delta[-1][ic] > maximum:
                place, maximum = ic, delta[-1][ic]
        best = [0] * nf
        for it in range(nf - 1, -1, -1):
            best[it] = place
            place = psi[it][place]
        f0 = []
        for it in range(nf):
            f, s = frames[it]['cands'][best[it]]
            f0.append(f if voiced(f) else 0.0)
        return np.array(f0)

    def analyse(self, z):
        """z: float samples (Praat units, int16/32768). Returns times, f0 (0 = unvoiced), frames."""
        z = np.asarray(z, dtype=float)
        mean = float(np.mean(z))            # NUMmean uses pairwise sum; differences ~1e-17
        gp = float(np.max(np.abs(z - mean)))
        t1, times, lefts = frame_grid(len(z))
        if gp == 0.0:
            return np.array(times), np.zeros(len(times)), []
        frames = [self.frame(z, l, gp) for l in lefts]
        f0 = self.path_finder(frames, K.TIME_STEP)
        return np.array(times), f0, frames


def median3(f):
    """Centred 3-point median with edge replicate, applied to the sequence as-is (0 = unvoiced)."""
    f = np.asarray(f)
    p = np.concatenate([f[:1], f, f[-1:]])
    return np.median(np.stack([p[:-2], p[1:-1], p[2:]]), axis=0)


def read_wav_float(path):
    import wave
    with wave.open(path, 'rb') as w:
        assert w.getframerate() == K.FS and w.getnchannels() == 1 and w.getsampwidth() == 2
        raw = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2')
    return raw.astype(np.int64), raw.astype(float) / 32768.0


if __name__ == '__main__':
    _, z = read_wav_float(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else 'R2'
    p = PraatRawAc() if mode == 'R1' else PraatRawAc(octave_jump=0.0, vuv=0.0)
    t, f0, _ = p.analyse(z)
    for ti, fi in zip(t, f0):
        print(f"{ti:.6f}\t{fi:.6f}")
