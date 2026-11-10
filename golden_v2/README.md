# golden_v2 — Praat-faithful golden model (Praat 7.0.03, raw autocorrelation, 16 kHz)

Replaces nothing: `golden/lab_1_3_5.py` (v1) is untouched. This folder follows Tú's 2026-11-10 decisions:
window 638, local mean over 426 samples, Praat's amplitude silence gate (localPeak/globalPeak),
subtractive octave cost, reference Praat 7.0.03 with R1 = defaults and R2 = octave-jump = V/UV cost = 0.

| file | what |
|---|---|
| `constants.py` | every number derived from `Sound_to_Pitch.cpp` (638/319/213/107/26/214/319/426 …) |
| `frames.py` | Praat frame grid in IEEE double (`Sampled_shortTermAnalysis`, `Sampled_xToLowIndex`) |
| `praat_float_ref.py` | float64 port of Praat 7.0.03 raw-ac: 15 candidates, sinc30 strength, sinc70 + Brent refinement, path finder (R1) / zero-cost path (R2), `median3` |
| `fixed_twin.py` | **bit-exact integer spec of the FPGA core** (docstring = the spec), median-3 |
| `gen_roms.py` | `rom/hanning638_q15.{hex,mif}` (638×16), `rom/ck_rom.{hex,mif}` (256×32, 189 used), `rom/constants.vh` |
| `make_synth.py` | `synth_glide_vuv_16k.wav` (glide 80→400 Hz, noise, silence, 140 Hz vibrato) and `…_snr5.wav` (+white noise 5 dB SNR) |
| `praat_pitch.praat` | runs Praat 7.0.03 `To Pitch (raw autocorrelation)` and prints time/F0 per frame |
| `compare.py` | VDE / GPE / FFE / cents tables → `out/compare_report.md`, `out/compare_summary.json` |
| `gen_vectors.py` | `out/golden_frames_*.tsv` (all per-frame twin results) and `hdl_check/{xw,exp}.hex` |
| `hdl_check/` | `mac_dsp_unit17.v` + `tb_mac638.v`: 17-bit MAC, 638-sample frames, 16 frames × 190 sums |

Reproduce:
```
python3 gen_roms.py && python3 make_synth.py && python3 compare.py && python3 gen_vectors.py 16
cd hdl_check && iverilog -g2005 -o sim tb_mac638.v mac_dsp_unit17.v && vvp -n sim
```

## Results (2026-11-10)

* Float port vs Praat 7.0.03: identical voicing on all 554 frames, max |ΔF0| = 1.5e-4 cent (R1 and R2,
  both files). The path-finder port is validated too: on the noisy file Praat R1 ≠ R2 in 19 frames, and the
  port reproduces both.
* Fixed twin (pre-median) vs Praat R2: clean file VDE 0/277, GPE 0/208, mean |Δ| 0.21 cent, max 1.08 cent.
  Noisy file VDE 0/277, GPE 3/207 (octave near-ties: Praat's two best local costs differ by 0.0005–0.007),
  non-gross max 33 cent (parabolic vs sinc+Brent on noisy, adjacent split peaks).
* MAC iverilog: 3040/3040 sums exact, 98,543 cycles per frame (98,540 issue + 3 latency), incl. 2 full-scale
  stress frames (|xw| up to 59,379 > 2^15 → 17-bit datapath required).
* Praat frame grid on both files: t1 = 0.020 s, first window starts at sample 1 (0-based), hop exactly 160.

## Known deviations of the fixed twin from Praat (by design, all documented)
1. parabolic interpolation on the grid instead of sinc70 + Brent; 2. candidate ranking and voicing on the grid
score instead of the sinc-refined strength; 3. one best candidate instead of 15 + path; 4. integer local mean
(floor((S+213)/426)) and Q1.15 window; 5. strength > 1 is not reflected (rare, short-lag only); 6. lag 26 is
scanned but never a candidate (Praat can still pick lags 2..26, but they map to ≥ 600 Hz = unvoiced);
7. normalisation of R to 27 bits (relative error ≤ 1.5e-8). F0 output Q12.4: ±1/32 Hz rounding = ±0.68 cent at 80 Hz.
