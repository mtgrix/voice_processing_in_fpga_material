"""Compare golden_v2 against Praat 7.0.03 (R1 = defaults, R2 = octave-jump = V/UV cost = 0).

Usage: python3 compare.py [praat_binary]   (default /workspace/tools/praat7003/praat_barren)
Writes out/compare_report.md and out/compare_summary.json.
Metrics (reference = first argument of each row):
  VDE  = fraction of frames whose voicing decision differs
  GPE  = among frames voiced in both, fraction with |f/fref - 1| > 0.2
  FFE  = (voicing errors + gross pitch errors) / all frames
  cents = 1200 log2(f / fref) over frames voiced in both (|.| mean, p95, max)
"""
import json
import subprocess
import sys
import numpy as np

import constants as K
from praat_float_ref import PraatRawAc, read_wav_float, median3
from fixed_twin import analyse_fixed

PRAAT = sys.argv[1] if len(sys.argv) > 1 else '/workspace/tools/praat7003/praat_barren'
FILES = ['synth_glide_vuv_16k.wav', 'synth_glide_vuv_16k_snr5.wav']
TRUTH = {'synth_glide_vuv_16k.wav': 'out/truth_f0.npy', 'synth_glide_vuv_16k_snr5.wav': 'out/truth_f0_snr5.npy'}


def run_praat(wav, jump, vuv):
    out = subprocess.run([PRAAT, '--run', 'praat_pitch.praat', wav, str(jump), str(vuv)],
                         check=True, capture_output=True, text=True).stdout
    a = np.array([[float(v) for v in line.split('\t')] for line in out.strip().splitlines()])
    return a[:, 0], a[:, 1]


def metrics(ref, f):
    ref, f = np.asarray(ref, float), np.asarray(f, float)
    vr, vf = ref > 0, f > 0
    both = vr & vf
    n = len(ref)
    vde = int(np.sum(vr != vf))
    c = 1200 * np.log2(f[both] / ref[both]) if both.any() else np.zeros(1)
    gpe = int(np.sum(np.abs(f[both] / ref[both] - 1) > 0.2))
    ac = np.abs(c)
    return dict(frames=n, voiced_ref=int(vr.sum()), voiced_test=int(vf.sum()), both=int(both.sum()),
                vde_frames=vde, VDE=vde / n, gpe_frames=gpe, GPE=gpe / max(1, both.sum()), FFE=(vde + gpe) / n,
                cents_mean_abs=float(ac.mean()), cents_mean=float(c.mean()), cents_p95=float(np.percentile(ac, 95)),
                cents_max=float(ac.max()),
                cents_max_nongross=float(ac[ac < 1200 * np.log2(1.2)].max()) if (ac < 315.6).any() else 0.0)


def main():
    summary, lines = {}, ['# golden_v2 vs Praat 7.0.03 — synthetic 16 kHz signals\n']
    for wav in FILES:
        xi, z = read_wav_float(wav)
        t1, p1 = run_praat(wav, 0.35, 0.14)
        t2, p2 = run_praat(wav, 0.0, 0.0)
        tf, f1, _ = PraatRawAc().analyse(z)
        _, f2, _ = PraatRawAc(octave_jump=0.0, vuv=0.0).analyse(z)
        fx = analyse_fixed(xi)
        assert np.array_equal(t1, np.round(tf, 9)) or np.max(np.abs(t1 - tf)) < 1e-8
        hops = np.diff(fx['starts'])
        raw = np.array(fx['f0q']) / 16.0
        med = np.array(fx['f0q_med']) / 16.0
        f2med = median3(f2)
        truth = np.load(TRUTH[wav])[np.round(t1 * K.FS - 0.5).astype(int)]   # true F0 at frame centre
        rows = {
            'float_R2 vs praat_R2': metrics(p2, f2),
            'float_R1 vs praat_R1': metrics(p1, f1),
            'praat_R1 vs praat_R2 (path-finder effect)': metrics(p2, p1),
            'fixed_raw vs praat_R2': metrics(p2, raw),
            'fixed_raw vs float_R2': metrics(f2, raw),
            'fixed_med3 vs float_R2+med3': metrics(f2med, med),
            'fixed_med3 vs praat_R2': metrics(p2, med),
            'fixed_med3 vs praat_R1': metrics(p1, med),
            'praat_R1 vs truth': metrics(truth, p1),
            'praat_R2 vs truth': metrics(truth, p2),
            'fixed_raw vs truth': metrics(truth, raw),
            'fixed_med3 vs truth': metrics(truth, med),
        }
        summary[wav] = dict(nframes=len(t1), t1=float(t1[0]), gp=fx['gp'],
                            hop_values=sorted(set(int(h) for h in hops)), first_window_start0=fx['starts'][0],
                            rows=rows)
        lines.append(f"\n## {wav}\n\nframes {len(t1)}, t1 = {t1[0]:.6f} s, first window start (0-based) "
                     f"{fx['starts'][0]}, hop values {sorted(set(int(h) for h in hops))}, GP = {fx['gp']}\n")
        lines.append('| comparison | VDE frames | GPE frames | FFE | mean abs cents | p95 cents | max cents (non-gross) |')
        lines.append('|---|---|---|---|---|---|---|')
        for k, m in rows.items():
            lines.append(f"| {k} | {m['vde_frames']}/{m['frames']} | {m['gpe_frames']}/{m['both']} | {m['FFE']:.4f} | "
                         f"{m['cents_mean_abs']:.4g} | {m['cents_p95']:.4g} | {m['cents_max_nongross']:.4g} |")
    open('out/compare_report.md', 'w').write('\n'.join(lines) + '\n')
    json.dump(summary, open('out/compare_summary.json', 'w'), indent=1)
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
