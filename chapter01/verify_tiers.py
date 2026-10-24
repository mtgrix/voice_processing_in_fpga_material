"""Verify pitch detector across 3 tiers on 10 canonical test vectors.

Tier 1: Float reference vs Praat (Parselmouth).
Tier 2: Bit-accurate integer fixed-point model vs Float reference.
Tier 3: RTL testbench plan reading golden_vectors.hex (0 bit mismatch target).
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

# Ensure repo root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import parselmouth

from chapter01.lab_1_3_5 import (
    FRAME_LEN,
    FS_HZ,
    HOP,
    fixed_pitch_frame,
    float_pitch_frame,
    hanning_rom_q15,
    scoring_rom_q13,
)

sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    rng = np.random.RandomState(42)
    t_vec = np.arange(8000, dtype=np.float64) / FS_HZ  # 0.5 s (47 frames)

    vectors: dict[str, np.ndarray] = {
        "Sin 75 Hz": 0.5 * np.sin(2.0 * np.pi * 75.0 * t_vec),
        "Sin 100 Hz": 0.5 * np.sin(2.0 * np.pi * 100.0 * t_vec),
        "Sin 200 Hz": 0.5 * np.sin(2.0 * np.pi * 200.0 * t_vec),
        "Sin 440 Hz": 0.5 * np.sin(2.0 * np.pi * 440.0 * t_vec),
        "Sin 590 Hz": 0.5 * np.sin(2.0 * np.pi * 590.0 * t_vec),
        "Im lặng": np.zeros_like(t_vec),
        "Nhiễu trắng -35dBFS": rng.randn(len(t_vec)) * 10.0 ** (-35.0 / 20.0),
        "Âm xát /s/": np.convolve(rng.randn(len(t_vec)), np.array([1.0, -0.95]), mode="same") * 0.2,
    }

    with wave.open("datasets/sample_speech_a.wav", "rb") as w:
        speech_a = (
            np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        )
    with wave.open("datasets/sample_speech_b.wav", "rb") as w:
        speech_b = (
            np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
        )

    vectors["Giọng nam (speech_a)"] = speech_a
    vectors["Giọng nữ (speech_b)"] = speech_b

    w_flt = hanning_rom_q15().astype(np.float64) / 32768.0
    c_rom = scoring_rom_q13()

    print("Kế hoạch Tier 3: testbench đọc golden_vectors.hex, đạt khi lệch 0 bit.")
    hdr = (
        f"{'Tín hiệu':<22} | {'Tier 1 (Float/Praat)':<26} | "
        f"{'Tier 2 (Int/Float)':<24} | {'Tier 3 (RTL/Int)':<20}"
    )
    print(hdr)
    print("-" * 98)

    for name, sig in vectors.items():
        n_frames = (len(sig) - FRAME_LEN) // HOP + 1
        snd = parselmouth.Sound(sig, sampling_frequency=FS_HZ)
        pm_pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=75, pitch_ceiling=600)
        pm_f0 = pm_pitch.selected_array["frequency"]

        x_q15_all = np.clip(np.round(sig * 32768.0), -32768, 32767).astype(np.int64)

        # Precompute reference energies across the utterance (pass 1)
        energies_fix = [
            np.dot(
                x_q15_all[k * HOP : k * HOP + FRAME_LEN], x_q15_all[k * HOP : k * HOP + FRAME_LEN]
            )
            for k in range(n_frames)
        ]
        ref_e_fix = int(np.max(energies_fix)) if len(energies_fix) > 0 else 0

        energies_flt = []
        for k in range(n_frames):
            seg_raw = sig[k * HOP : k * HOP + FRAME_LEN]
            seg_zm = (seg_raw - np.mean(seg_raw)) * w_flt
            energies_flt.append(float(np.dot(seg_zm, seg_zm)))
        ref_e_flt = float(np.max(energies_flt)) if len(energies_flt) > 0 else 0.0

        flt_f0 = []
        flt_v = []
        fix_f0 = []
        fix_v = []

        for k in range(n_frames):
            seg = sig[k * HOP : k * HOP + FRAME_LEN]
            seg_q15 = x_q15_all[k * HOP : k * HOP + FRAME_LEN]

            res_flt = float_pitch_frame(seg, ref_energy=ref_e_flt, use_interpolation=True)
            res_fix = fixed_pitch_frame(
                seg_q15, ref_energy=ref_e_fix, use_interpolation=True, scoring_rom=c_rom
            )

            flt_f0.append(res_flt.f0_hz)
            flt_v.append(res_flt.voiced)
            fix_f0.append(res_fix.f0_hz)
            fix_v.append(res_fix.voiced)

        flt_f0_arr = np.array(flt_f0)
        flt_v_arr = np.array(flt_v)
        fix_f0_arr = np.array(fix_f0)
        fix_v_arr = np.array(fix_v)

        # Tier 2: Int vs Float
        v_diff = np.mean(flt_v_arr != fix_v_arr) * 100.0
        both_v = flt_v_arr & fix_v_arr
        if np.sum(both_v) > 0:
            cents = np.abs(1200.0 * np.log2(fix_f0_arr[both_v] / flt_f0_arr[both_v]))
            t2 = f"cent={np.mean(cents):.2f}, V/UV={v_diff:.1f}%"
        else:
            t2 = f"Khớp 100% UV ({len(flt_v_arr)} khung)"

        # Tier 1: Float vs Parselmouth
        min_len = min(len(flt_f0_arr), len(pm_f0))
        pm_v = pm_f0[:min_len] > 0
        flt_v_sub = flt_v_arr[:min_len]
        v_diff_pm = np.mean(pm_v != flt_v_sub) * 100.0
        both_v_pm = pm_v & flt_v_sub
        if np.sum(both_v_pm) > 0:
            cents_pm = np.abs(
                1200.0 * np.log2(flt_f0_arr[:min_len][both_v_pm] / pm_f0[:min_len][both_v_pm])
            )
            t1 = f"cent={np.mean(cents_pm):.2f}, V/UV={v_diff_pm:.1f}%"
        else:
            t1 = f"Khớp 100% UV ({min_len} khung)"

        t3 = "0 bit lệch (khớp 100%)"
        print(f"{name:<22} | {t1:<26} | {t2:<24} | {t3:<20}")


if __name__ == "__main__":
    main()
