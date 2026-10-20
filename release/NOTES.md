Tag: v0.1.1-ch1.1.5
Source commit: ae7fd6558e2aa27224bf114f28b2d4e037bca8f9 on feat/ch01-sec-1-1-5-preconditioning (issue 129, pull request 130), based on develop_content b08e81a.
SHA256 (en): 9217316284ae1f42d82378128200dc0346259cb2916eae5df676e6b2b2e5ec56
SHA256 (vi): 085a9d8f1c012725ad6f70c969425500c3db5ed1d55b19f6b4db857496d4d15d
Lab log: results/lab115/20261020T175727Z
Residual & Scope: Section 1.1.5 only, English and Vietnamese. The mute length is derived from the INMP441 datasheet at a 64-times bit clock and 16 kHz (0.256 s, 4096 samples). The high-pass is the Audio EQ Cookbook biquad at 60 Hz with Q = 1/sqrt(2). The October 2026 bench decibel figures are not printed in this section.
Integration: pull request 130 is not merged. make gate already fails on develop_content in chapter01/lab_1_3.py and chapter08/dtw_baseline.py, and this section does not change those files.
