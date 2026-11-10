"""Golden vectors from the fixed-point twin.

  out/golden_frames_<wav>.tsv : one line per frame (all frames) with every per-frame result
  hdl_check/xw.hex, exp.hex   : NF-2 real frames + 2 full-scale stress frames, each (xw[0..637] 17-bit) and NF x 190 expected 48-bit sums
                                (R0, R[26..214]) for the MAC iverilog check (tb_mac638.v)
"""
import sys
import numpy as np
import constants as K
from praat_float_ref import read_wav_float
from fixed_twin import analyse_fixed, frame_fixed

NF = int(sys.argv[1]) if len(sys.argv) > 1 else 16


def stress_frames():
    """Two full-scale frames that push |x - mean| beyond 16 bits (needs the 17-bit datapath)."""
    a = np.full(K.NSAMP_WINDOW, -32768); a[300:340] = 32767
    b = np.where((np.arange(K.NSAMP_WINDOW) // 27) % 2 == 0, 32767, -32768); b[100:300] = -32768
    return [frame_fixed(v, 32767, trace=True) for v in (a, b)]


def main():
    for wav in ['synth_glide_vuv_16k.wav', 'synth_glide_vuv_16k_snr5.wav']:
        xi, _ = read_wav_float(wav)
        res = analyse_fixed(xi, trace=True)
        with open(f'out/golden_frames_{wav[:-4]}.tsv', 'w') as f:
            f.write('frame\ttime\tstart0\tmean\tLP\tR0\tsh\tbest_tau\tSc\tvoiced\tf0q\tf0q_med3\n')
            for i, (t, s, fr, m) in enumerate(zip(res['times'], res['starts'], res['frames'], res['f0q_med'])):
                f.write(f"{i+1}\t{t:.6f}\t{s}\t{fr['mean']}\t{fr['lp']}\t{fr['r0']}\t{fr['sh']}\t{fr['best']}\t"
                        f"{fr['sc']}\t{fr['voiced']}\t{fr['f0q']}\t{m}\n")
        if wav == 'synth_glide_vuv_16k_snr5.wav':        # noisy frames: full dynamic range, all lags busy
            idx = np.linspace(0, len(res['frames']) - 1, NF - 2).astype(int)
            frames = [res['frames'][i] for i in idx] + stress_frames()
            with open('hdl_check/xw.hex', 'w') as fx, open('hdl_check/exp.hex', 'w') as fe:
                for fr in frames:
                    for v in fr['xw']:
                        fx.write(f'{v & 0x1FFFF:05X}\n')
                    for v in [fr['r0']] + [fr['R'][t] for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1)]:
                        fe.write(f'{v & ((1 << 48) - 1):012X}\n')
            mx = max(max(abs(v) for v in fr['xw']) for fr in frames)
            print('hdl vectors: frames', [int(i) for i in idx], '+ 2 stress frames, max|xw|', mx)


if __name__ == '__main__':
    main()
