Tag: v0.1.1-ch1.1.5
Source commit: ae7fd6558e2aa27224bf114f28b2d4e037bca8f9 on feat/ch01-sec-1-1-5-preconditioning (issue 129, pull request 130), based on develop_content b08e81a.
SHA256 (en): 9217316284ae1f42d82378128200dc0346259cb2916eae5df676e6b2b2e5ec56
SHA256 (vi): 085a9d8f1c012725ad6f70c969425500c3db5ed1d55b19f6b4db857496d4d15d
Lab log: results/lab115/20261020T175727Z
Residual & Scope: Section 1.1.5 only, English and Vietnamese. The mute length is derived from the INMP441 datasheet at a 64-times bit clock and 16 kHz (0.256 s, 4096 samples). The high-pass is the Audio EQ Cookbook biquad at 60 Hz with Q = 1/sqrt(2). The October 2026 bench decibel figures are not printed in this section.
Integration: pull request 130 is not merged. make gate already fails on develop_content in chapter01/lab_1_3.py and chapter08/dtw_baseline.py, and this section does not change those files.

---

Tag: v0.1.2-ch1.3.5
Source commit: 8b24735 (issue 134, pull request 135) on main at 55b7787.
SHA256 (vi): 6405be9c4f4fc599d26b094ae4d320ebe7c30fd78936b4a5e7a0cfec576a0b6d
Source SHA256: sec_1_3_5_vi.tex 41cd052c8896b85b9e07340e54aaae62b53c5ca67ba6589b712707185c3c1109; sec_1_3_5_vi.md 48a85f92d4a7d1a1110341cb5595ec5a89454fdbae4c0b2ac789748f69daeab4; fig_1_3_5b_vi.tex 635e7fdf5c7b6b2df07aaa29fbb4215c26d84c1d8acdca14f3d4f0ca0afb09d7
Residual & Scope: Section 1.3.5 only, Vietnamese. The rewritten sections 2 and 3 and Figure 1.3.5b use the F0 = 200 Hz example (T0 = 80 samples); its peak values 0,42 and 0,23 rising to about 0,47 and 0,35 are worked examples for the teaching narrative, not benchmark measurements. No empirical claim is made from them.
Integration: pull request 135 is merged. make gate: ruff check and ruff format pass; integrity, claims, scan_numbers, prose_cage and figure_numbers pass; mypy reports the same 148 errors as on a clean main tree; pytest cannot collect tests/test_audio_pipeline.py because the import capstone.voice_edge_benchmark resolves to a site-packages capstone instead of the repository directory (same on main).

---

Tag: v0.1.4-ch1.3.5
Source commit: feat/ch01-1-3-5-architecture-fixedpoint.
SHA256 (vi): e8e4ddd570385d45d9d795c8223d3a0565388c7b12adb6ec0f9a44a85e47b36f
Source SHA256: sec_1_3_5_vi.tex 57ef6dc538e421f1cd231d6ee5485734c4cd6de9de664a36dcff8ea4c8d6b92f; sec_1_3_5_vi.md 53d2c5bde8a46fdc2b009791e3daf131f266c1ad51f0c6fed44ab81cd2d3e7ce; lab_1_3_5.py cb525b16b4358da61d85a0fc89e4918853a3264a5aa1a5c7a21e09db24cb8b1c
Residual & Scope: Section 1.3.5 and Appendix 1.3.5-A, Vietnamese. Complete pedagogical overhaul to v5 (39 pages). Architecture fully grounded: FPGA edge node (60 Hz HPF + Q12.4 uint16 pitch_f0.bin @ 100 fps) <-> Shared Folder <-> Server (Whisper Log-Mel + scoring). Praat algorithmic foundation (§3.0 6-step pipeline from C++ source, N=638 vs FPGA 640 derivation, Table of 5 deliberate differences). Q-format specification table (§4.0) with exact rounding, 42-bit signed accumulator Q12.30, and integer quadratic silence gate (Rx[0]*10000 < 9*E_ref). Bit-accurate fixed-point implementation (lab_1_3_5.py), 3-tier verification (verify_tiers.py) across 10 canonical vectors, exported Quartus ROM hex files (chapter01/hex/*.hex). All numbers derived from theory or verified execution in run_log_v5.txt.
Integration: ruff check and ruff format pass; pytest passes 15/15 unit tests in chapter01/test_lab_1_3_5.py. LuaLaTeX compiles sec_1_3_5_vi.tex to 39-page publication-quality PDF with 0 errors, 0 missing references, and 0 overfull hboxes.


