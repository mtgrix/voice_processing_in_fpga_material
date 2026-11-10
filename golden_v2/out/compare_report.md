# golden_v2 vs Praat 7.0.03 — synthetic 16 kHz signals


## synth_glide_vuv_16k.wav

frames 277, t1 = 0.020000 s, first window start (0-based) 1, hop values [160], GP = 22946

| comparison | VDE frames | GPE frames | FFE | mean abs cents | p95 cents | max cents (non-gross) |
|---|---|---|---|---|---|---|
| float_R2 vs praat_R2 | 0/277 | 0/208 | 0.0000 | 5.698e-06 | 5.586e-05 | 6.815e-05 |
| float_R1 vs praat_R1 | 0/277 | 0/208 | 0.0000 | 5.698e-06 | 5.586e-05 | 6.815e-05 |
| praat_R1 vs praat_R2 (path-finder effect) | 0/277 | 0/208 | 0.0000 | 0 | 0 | 0 |
| fixed_raw vs praat_R2 | 0/277 | 0/208 | 0.0000 | 0.2102 | 0.4834 | 1.08 |
| fixed_raw vs float_R2 | 0/277 | 0/208 | 0.0000 | 0.2102 | 0.4834 | 1.08 |
| fixed_med3 vs float_R2+med3 | 0/277 | 0/208 | 0.0000 | 0.2048 | 0.4674 | 0.6939 |
| fixed_med3 vs praat_R2 | 0/277 | 0/208 | 0.0000 | 0.3734 | 0.6363 | 12.96 |
| fixed_med3 vs praat_R1 | 0/277 | 0/208 | 0.0000 | 0.3734 | 0.6363 | 12.96 |
| praat_R1 vs truth | 4/277 | 0/207 | 0.0144 | 0.2993 | 0.8303 | 7.906 |
| praat_R2 vs truth | 4/277 | 0/207 | 0.0144 | 0.2993 | 0.8303 | 7.906 |
| fixed_raw vs truth | 4/277 | 0/207 | 0.0144 | 0.3962 | 0.9976 | 7.819 |
| fixed_med3 vs truth | 4/277 | 0/207 | 0.0144 | 0.5279 | 1.047 | 14.28 |

## synth_glide_vuv_16k_snr5.wav

frames 277, t1 = 0.020000 s, first window start (0-based) 1, hop values [160], GP = 22937

| comparison | VDE frames | GPE frames | FFE | mean abs cents | p95 cents | max cents (non-gross) |
|---|---|---|---|---|---|---|
| float_R2 vs praat_R2 | 0/277 | 0/207 | 0.0000 | 9.361e-06 | 5.976e-05 | 0.0001521 |
| float_R1 vs praat_R1 | 0/277 | 0/207 | 0.0000 | 1.004e-05 | 6.188e-05 | 0.0001521 |
| praat_R1 vs praat_R2 (path-finder effect) | 0/277 | 19/207 | 0.0686 | 117.4 | 1191 | 37.28 |
| fixed_raw vs praat_R2 | 0/277 | 3/207 | 0.0108 | 20.37 | 10.56 | 32.91 |
| fixed_raw vs float_R2 | 0/277 | 3/207 | 0.0108 | 20.37 | 10.56 | 32.91 |
| fixed_med3 vs float_R2+med3 | 0/277 | 3/207 | 0.0108 | 20.31 | 11.24 | 44.66 |
| fixed_med3 vs praat_R2 | 0/277 | 18/207 | 0.0650 | 114.8 | 1181 | 48.41 |
| fixed_med3 vs praat_R1 | 0/277 | 15/207 | 0.0542 | 91.24 | 1182 | 48.41 |
| praat_R1 vs truth | 3/277 | 0/207 | 0.0108 | 10.56 | 21.8 | 29.32 |
| praat_R2 vs truth | 3/277 | 19/207 | 0.0794 | 126.4 | 1199 | 28.48 |
| fixed_raw vs truth | 3/277 | 22/207 | 0.0903 | 142.3 | 1199 | 25.85 |
| fixed_med3 vs truth | 3/277 | 15/207 | 0.0650 | 94.99 | 1179 | 32.68 |
