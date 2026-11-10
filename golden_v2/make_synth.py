"""Synthetic 16 kHz test signal for golden_v2 (deterministic, seed 2026).

Segments (seconds):
  0.00-0.10  silence (tiny dither)
  0.10-1.60  voiced, exponential glide 80 -> 400 Hz, 12 harmonics with 1/k^1.2 roll-off
  1.60-1.90  unvoiced: white noise, -20 dB re voiced peak
  1.90-2.10  silence (dither)
  2.10-2.70  voiced 140 Hz with 5 Hz / +-3 % vibrato
  2.70-2.80  silence
Every voiced segment has 10 ms raised-cosine onset/offset. Writes synth_glide_vuv_16k.wav and the
true F0 track (per sample) as truth_f0.npy.
A second 'hard' file synth_glide_vuv_16k_snr5.wav adds white noise at 5 dB SNR (re voiced RMS)
so that the path finder (R1) and the zero-cost baseline (R2) actually differ.
"""
import wave
import numpy as np

FS = 16000


def harmonic(f_inst, nharm=12):
    phase = 2 * np.pi * np.cumsum(f_inst) / FS
    y = np.zeros_like(phase)
    for k in range(1, nharm + 1):
        ok = (k * f_inst) < 0.45 * FS
        y += ok * np.sin(k * phase) / k ** 1.2
    return y


def ramp(n, nr=160):
    e = np.ones(n)
    r = 0.5 - 0.5 * np.cos(np.pi * np.arange(nr) / nr)
    e[:nr] = r
    e[-nr:] = r[::-1]
    return e


def main(path='synth_glide_vuv_16k.wav', snr_db=None, truth_name='truth_f0.npy'):
    rng = np.random.default_rng(2026)
    seg = lambda s: int(round(s * FS))
    parts, truth = [], []
    parts.append(np.zeros(seg(0.10))); truth.append(np.zeros(seg(0.10)))
    n = seg(1.50)
    f = 80.0 * (400.0 / 80.0) ** (np.arange(n) / n)
    parts.append(harmonic(f) * ramp(n)); truth.append(f)
    n = seg(0.30)
    parts.append(0.1 * rng.standard_normal(n) * ramp(n)); truth.append(np.zeros(n))
    parts.append(np.zeros(seg(0.20))); truth.append(np.zeros(seg(0.20)))
    n = seg(0.60)
    f = 140.0 * (1 + 0.03 * np.sin(2 * np.pi * 5 * np.arange(n) / FS))
    parts.append(harmonic(f) * ramp(n)); truth.append(f)
    parts.append(np.zeros(seg(0.10))); truth.append(np.zeros(seg(0.10)))
    y = np.concatenate(parts)
    y = y / np.max(np.abs(y)) * 0.7
    y = y + 2e-5 * rng.standard_normal(len(y))          # dither so 'silence' is not exactly 0
    if snr_db is not None:                               # 'hard' variant: white noise everywhere
        vrms = np.sqrt(np.mean(y[np.concatenate(truth) > 0] ** 2))
        y = y + vrms * 10 ** (-snr_db / 20) * rng.standard_normal(len(y))
        y = y / np.max(np.abs(y)) * 0.7
    x = np.clip(np.round(y * 32768), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(FS)
        w.writeframes(x.tobytes())
    np.save('out/' + truth_name, np.concatenate(truth))
    print(path, len(x), 'samples')


if __name__ == '__main__':
    main()
    main('synth_glide_vuv_16k_snr5.wav', snr_db=5.0, truth_name='truth_f0_snr5.npy')
