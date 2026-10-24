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

Tag: v0.1.3-ch1.3.5
Source commit: feat/ch01-1-3-5-architecture-fixedpoint.
SHA256 (vi): 8fa1eed999194eca023443c06f9cf63eeb648a0c03e61ef5ab90edbaa17d70db
Source SHA256: sec_1_3_5_vi.tex 0f799cd5d92f6fde729d5f69301aacdaed9e442717c0235e6144567ff6c9987a; sec_1_3_5_vi.md 3defbc713446f2bac18420350ccb17232f9efa79d4a2f1ef5a76841065e5162e
Residual & Scope: Section 1.3.5 and Appendix 1.3.5-A, Vietnamese. Comprehensive overhaul adding system architecture (FPGA Edge Node <-> Shared Folder <-> Server), acoustic theory for Praat parameters #6 to #10 (silence threshold 0.03 / 30 dB SNR, voicing threshold 0.45 / HNR -0.87 dB, octave cost 0.01 breaking 1T0/2T0 tie, octave jump cost 0.35 & voiced/unvoiced cost 0.14 from Sundberg 1979 biomechanical laryngeal inertia), bit-accurate fixed-point integer model (AMD64 vs ARM64 ULP determinism, lab_1_3_5.py), 3-tap median filter replacing Viterbi, stopwatch timing analogy (15 ms initial buffering vs 7.5 ms frame center phase offset), two-phase BRAM architecture, Praat C++ Wiener-Khinchin FFT dissection, and lighter alternatives to Whisper (Forced Alignment & DTW on 80 Log-Mel).
Integration: ruff check and ruff format pass; pytest passes 14/14 tests in chapter01/test_lab_1_3_5.py and 10/10 tests in chapter01/test_lab_1_3.py. LuaLaTeX compiles sec_1_3_5_vi.tex to 33-page publication-quality PDF with 0 errors and 0 missing references.

