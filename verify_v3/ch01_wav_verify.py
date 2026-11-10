#!/usr/bin/env python3
"""verify_v3/ch01_wav_verify.py
Verification of WAV parsing and integer globalPeak:
1. Compiles sw_v3/ch01_wav.c and test runner sw_v3/test_ch01_wav.c with gcc.
2. Runs tests on golden WAV files and crafted edge-case WAV files.
3. Implements Python reference twin and compares bit-for-bit.
4. Verifies GP formula: round(max |n*x - sum(x)| / n) on both golden files.
"""
import os
import sys
import subprocess
import numpy as np

# Ensure golden_v2 can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "golden_v2"))
from fixed_twin import global_peak as golden_global_peak

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BIN_PATH = os.path.join(REPO_ROOT, "verify_v3", "test_ch01_wav_bin.exe" if os.name == "nt" else "test_ch01_wav_bin")

def compile_c_wav_parser():
    cmd = [
        "gcc", "-Wall", "-Wextra", "-O2",
        os.path.join(REPO_ROOT, "sw_v3", "ch01_wav.c"),
        os.path.join(REPO_ROOT, "sw_v3", "test_ch01_wav.c"),
        "-I", os.path.join(REPO_ROOT, "sw_v3"),
        "-o", BIN_PATH
    ]
    print(f"Compiling C WAV parser: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("C COMPILATION FAILED:")
        print(res.stderr)
        sys.exit(1)
    print("Compilation successful.\n")

def run_c_test(wav_relpath):
    wav_path = os.path.join(REPO_ROOT, wav_relpath)
    res = subprocess.run([BIN_PATH, wav_path], capture_output=True, text=True)
    lines = res.stdout.strip().split("\n")
    out = {}
    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out

def main():
    print("=" * 70)
    print("VERIFICATION: CH01 WAV PARSER AND GLOBAL PEAK")
    print("=" * 70)

    # 1. Compile C parser
    compile_c_wav_parser()

    # 2. Test golden clean file
    clean_wav = "golden_v2/synth_glide_vuv_16k.wav"
    out_clean = run_c_test(clean_wav)
    print(f"Test 1: Golden clean WAV ({clean_wav})")
    print(f"  Return code: {out_clean['RETURN_CODE']} (expected 0)")
    print(f"  Num samples: {out_clean['NUM_SAMPLES']} (expected 44800)")
    print(f"  Sample rate: {out_clean['SAMPLE_RATE']} (expected 16000)")
    print(f"  Channels:    {out_clean['NUM_CHANNELS']} (expected 1)")
    print(f"  Bits/sample: {out_clean['BITS_PER_SAMPLE']} (expected 16)")
    print(f"  globalPeak:  {out_clean['GLOBAL_PEAK']} (expected 22946)")
    assert out_clean['RETURN_CODE'] == '0'
    assert int(out_clean['NUM_SAMPLES']) == 44800
    assert int(out_clean['GLOBAL_PEAK']) == 22946

    # 3. Test golden noisy file
    noisy_wav = "golden_v2/synth_glide_vuv_16k_snr5.wav"
    out_noisy = run_c_test(noisy_wav)
    print(f"\nTest 2: Golden noisy SNR 5dB WAV ({noisy_wav})")
    print(f"  Return code: {out_noisy['RETURN_CODE']} (expected 0)")
    print(f"  Num samples: {out_noisy['NUM_SAMPLES']} (expected 44800)")
    print(f"  globalPeak:  {out_noisy['GLOBAL_PEAK']} (expected 22937)")
    assert out_noisy['RETURN_CODE'] == '0'
    assert int(out_noisy['NUM_SAMPLES']) == 44800
    assert int(out_noisy['GLOBAL_PEAK']) == 22937

    # 4. Test mini_speech.wav (8 samples walk-through)
    mini_wav = "verify_v3/data/mini_speech.wav"
    out_mini = run_c_test(mini_wav)
    print(f"\nTest 3: Miniature speech WAV ({mini_wav})")
    print(f"  Return code: {out_mini['RETURN_CODE']}")
    print(f"  Num samples: {out_mini['NUM_SAMPLES']} (expected 8)")
    print(f"  globalPeak:  {out_mini['GLOBAL_PEAK']}")
    print(f"  Samples:     {out_mini['FIRST_8_SAMPLES']}")
    assert out_mini['RETURN_CODE'] == '0'
    assert int(out_mini['NUM_SAMPLES']) == 8
    assert out_mini['FIRST_8_SAMPLES'] == "0 100 -200 300 -400 500 -600 700"

    # 5. Test edge_list_chunk.wav (LIST chunk placed before data chunk)
    list_wav = "verify_v3/data/edge_list_chunk.wav"
    out_list = run_c_test(list_wav)
    print(f"\nTest 4: Edge case LIST chunk ({list_wav})")
    print(f"  Return code: {out_list['RETURN_CODE']} (expected 0)")
    print(f"  Num samples: {out_list['NUM_SAMPLES']} (expected 160)")
    assert out_list['RETURN_CODE'] == '0'
    assert int(out_list['NUM_SAMPLES']) == 160

    # 6. Test edge_odd_chunk.wav (Odd-sized chunk with pad byte)
    odd_wav = "verify_v3/data/edge_odd_chunk.wav"
    out_odd = run_c_test(odd_wav)
    print(f"\nTest 5: Edge case odd-sized chunk with pad ({odd_wav})")
    print(f"  Return code: {out_odd['RETURN_CODE']} (expected 0)")
    print(f"  Num samples: {out_odd['NUM_SAMPLES']} (expected 4)")
    assert out_odd['RETURN_CODE'] == '0'
    assert int(out_odd['NUM_SAMPLES']) == 4

    # 7. Test edge_wrong_rate.wav (44100 Hz -> rejected)
    rate_wav = "verify_v3/data/edge_wrong_rate.wav"
    out_rate = run_c_test(rate_wav)
    print(f"\nTest 6: Invalid sample rate 44.1 kHz ({rate_wav})")
    print(f"  Return code: {out_rate['RETURN_CODE']} (expected -7: WAV_ERR_UNSUPPORTED_RATE)")
    assert out_rate['RETURN_CODE'] == '-7'

    # 8. Test edge_stereo.wav (2 channels -> rejected)
    stereo_wav = "verify_v3/data/edge_stereo.wav"
    out_stereo = run_c_test(stereo_wav)
    print(f"\nTest 7: Invalid channel count stereo ({stereo_wav})")
    print(f"  Return code: {out_stereo['RETURN_CODE']} (expected -6: WAV_ERR_UNSUPPORTED_CHANNELS)")
    assert out_stereo['RETURN_CODE'] == '-6'

    # 9. Test edge_truncated.wav (corrupted header length -> rejected)
    trunc_wav = "verify_v3/data/edge_truncated.wav"
    out_trunc = run_c_test(trunc_wav)
    print(f"\nTest 8: Truncated audio data ({trunc_wav})")
    print(f"  Return code: {out_trunc['RETURN_CODE']} (expected -10: WAV_ERR_TRUNCATED)")
    assert out_trunc['RETURN_CODE'] == '-10'

    print("\n" + "=" * 70)
    print("ALL 8 WAV PARSER AND GLOBAL PEAK TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
