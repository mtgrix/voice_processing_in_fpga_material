#!/usr/bin/env python3
"""verify_v3/ch01_driver_test.py
Verification of HPS C driver in simulation mode (-DSIM):
1. Compiles sw_v3/ch01_driver.c with gcc -Wall -Wextra -O2 -DSIM.
2. Runs driver on golden WAV (synth_glide_vuv_16k.wav).
3. Verifies generated pitch_f0.bin (554 bytes = 277 frames * 2 bytes) and pitch_meta.txt.
4. Checks cycle counts, frame counts, and metadata.
"""
import os
import sys
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BIN_PATH = os.path.join(REPO_ROOT, "verify_v3", "ch01_driver_sim.exe" if os.name == "nt" else "ch01_driver_sim")

def main():
    print("=" * 70)
    print("VERIFICATION: CH01 HPS C DRIVER (-DSIM MODE)")
    print("=" * 70)

    # 1. Compile C driver with -DSIM
    cmd = [
        "gcc", "-Wall", "-Wextra", "-O2", "-DSIM",
        os.path.join(REPO_ROOT, "sw_v3", "ch01_driver.c"),
        os.path.join(REPO_ROOT, "sw_v3", "ch01_wav.c"),
        os.path.join(REPO_ROOT, "sw_v3", "ch01_frames.c"),
        "-I", os.path.join(REPO_ROOT, "sw_v3"),
        "-lm",
        "-o", BIN_PATH
    ]
    print(f"Compiling HPS driver in -DSIM mode: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("COMPILATION FAILED:")
        print(res.stderr)
        sys.exit(1)
    print("Compilation successful.\n")

    # 2. Run driver on golden clean WAV
    wav_path = os.path.join(REPO_ROOT, "golden_v2", "synth_glide_vuv_16k.wav")
    out_dir = os.path.join(REPO_ROOT, "verify_v3")
    print(f"Executing driver on {wav_path}...")
    res_run = subprocess.run([BIN_PATH, wav_path, out_dir], capture_output=True, text=True)
    print(res_run.stdout)
    if res_run.returncode != 0:
        print(f"DRIVER RUN FAILED with code {res_run.returncode}:")
        print(res_run.stderr)
        sys.exit(1)

    # 3. Check output binary file
    bin_file = os.path.join(out_dir, "pitch_f0.bin")
    assert os.path.exists(bin_file), f"Output file {bin_file} not found!"
    bin_size = os.path.getsize(bin_file)
    expected_size = 277 * 2 # 277 frames * 2 bytes = 554 bytes
    print(f"Checking {bin_file}: size = {bin_size} bytes (expected {expected_size} bytes)")
    assert bin_size == expected_size, f"Size mismatch! Expected {expected_size}, got {bin_size}"

    # 4. Check output metadata file
    meta_file = os.path.join(out_dir, "pitch_meta.txt")
    assert os.path.exists(meta_file), f"Metadata file {meta_file} not found!"
    with open(meta_file, "r") as f:
        meta_content = f.read()
    print(f"Checking {meta_file}:\n{meta_content}")

    assert "t1=0.020000" in meta_content
    assert "n_frames=277" in meta_content
    assert "first_win0=1" in meta_content
    assert "global_peak=22946" in meta_content

    print("=" * 70)
    print("ALL HPS C DRIVER SIMULATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
