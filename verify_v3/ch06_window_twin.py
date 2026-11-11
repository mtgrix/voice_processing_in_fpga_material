#!/usr/bin/env python3
"""verify_v3/ch06_window_twin.py

Cycle-accurate bit-exact Python twin for Chapter 6 module: ch06_hanning_window.v
Generates stimulus (tb_ch06_hanning_stim.txt) and expected outputs
(tb_ch06_hanning_expected.txt) for iverilog testbench tb_ch06_hanning.v.

Rules followed:
- Cast every boolean to int() to prevent $fscanf parsing issues (Lesson m.1)
- Write vector files with newline='\n'
- Test >= 200 vectors including clean frames, noisy frames, and 2 full-scale stress frames
- Track register stages cycle-by-cycle in exact agreement with RTL
"""

import math
import os
import sys
import numpy as np

# Ensure golden_v2 is accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN_V2_DIR = os.path.join(CURRENT_DIR, "..", "golden_v2")
sys.path.insert(0, GOLDEN_V2_DIR)

import constants as K
import gen_vectors
from fixed_twin import frame_fixed, analyse_fixed, W
from praat_float_ref import read_wav_float


class HanningWindowTwin:
    """Cycle-accurate model of ch06_hanning_window.v."""

    def __init__(self, rom_data=None):
        self.rom = rom_data if rom_data is not None else list(W)
        self.reset()

    def reset(self):
        self.busy = 0
        self.sample_cnt = 0
        self.rom_addr = 0
        self.w_q = 0

        # Stage 1 registers
        self.d_r1 = 0
        self.v_r1 = 0
        self.idx_r1 = 0

        # Stage 2 registers
        self.prod_r2 = 0
        self.v_r2 = 0
        self.idx_r2 = 0

        # Stage 3 registers
        self.out_valid = 0
        self.out_xw = 0
        self.out_done = 0
        self.out_lp = 0
        self.lp_reg = 0

    def step(self, rst_n, start, in_valid, in_d):
        """Execute one clock cycle.
        
        Sampling convention:
        - Inputs driven before posedge
        - Combinational logic evaluates based on current state
        - Registered outputs update on posedge
        """
        if not rst_n:
            self.reset()
            return dict(
                out_valid=int(self.out_valid),
                out_xw=int(self.out_xw),
                out_done=int(self.out_done),
                out_lp=int(self.out_lp),
                busy=int(self.busy)
            )

        # ---------------------------------------------------------------------
        # Next-state computation (combinational logic evaluating current regs)
        # ---------------------------------------------------------------------
        # Stage 3: Rounding adder and output evaluation
        next_out_valid = int(self.v_r2)
        next_out_done = 0
        next_out_xw = self.out_xw
        next_out_lp = self.out_lp
        next_lp_reg = self.lp_reg

        if start:
            next_lp_reg = 0

        if self.v_r2:
            # Rounding adder: (p + 2^14) >> 15
            p_round = self.prod_r2 + 16384
            xw_res = p_round >> 15
            next_out_xw = xw_res

            abs_xw = abs(xw_res)
            if K.LP_FIRST <= self.idx_r2 <= K.LP_LAST:
                if abs_xw > next_lp_reg:
                    next_lp_reg = abs_xw

            if self.idx_r2 == K.NSAMP_WINDOW - 1:
                next_out_done = 1
                next_out_lp = next_lp_reg

        # Stage 2: Multiplier product
        # w_q is unsigned Q1.15 in [0, 32767]
        prod_comb = self.d_r1 * self.w_q
        next_prod_r2 = prod_comb
        next_v_r2 = int(self.v_r1)
        next_idx_r2 = self.idx_r1

        # Stage 1: ROM synchronous read and sample delay matching
        curr_sample_cnt = 0 if start else self.sample_cnt
        valid_sample = in_valid and (self.busy or start)

        next_w_q = self.rom[curr_sample_cnt] if valid_sample else 0
        next_d_r1 = in_d if valid_sample else 0
        next_v_r1 = 1 if valid_sample else 0
        next_idx_r1 = curr_sample_cnt if valid_sample else 0

        next_sample_cnt = self.sample_cnt
        next_busy = self.busy

        if start:
            next_busy = 1

        if valid_sample:
            if curr_sample_cnt == K.NSAMP_WINDOW - 1:
                next_sample_cnt = 0
            else:
                next_sample_cnt = curr_sample_cnt + 1

        if next_out_done:
            next_busy = 0

        # ---------------------------------------------------------------------
        # Register update on posedge clk
        # ---------------------------------------------------------------------
        self.busy = next_busy
        self.sample_cnt = next_sample_cnt
        self.w_q = next_w_q

        self.d_r1 = next_d_r1
        self.v_r1 = next_v_r1
        self.idx_r1 = next_idx_r1

        self.prod_r2 = next_prod_r2
        self.v_r2 = next_v_r2
        self.idx_r2 = next_idx_r2

        self.out_valid = next_out_valid
        self.out_xw = next_out_xw
        self.out_done = next_out_done
        self.out_lp = next_out_lp
        self.lp_reg = next_lp_reg

        return dict(
            out_valid=int(self.out_valid),
            out_xw=int(self.out_xw),
            out_done=int(self.out_done),
            out_lp=int(self.out_lp),
            busy=int(self.busy)
        )


def build_test_stimuli():
    """Generates stimuli for clean, noisy, stress, and edge-case frames."""
    frames = []

    # Frame 0: Clean frame (frame 100 from synthetic glide)
    wav_clean = os.path.join(GOLDEN_V2_DIR, "synth_glide_vuv_16k.wav")
    if os.path.exists(wav_clean):
        x_clean, _ = read_wav_float(wav_clean)
        res_clean = analyse_fixed(x_clean, trace=True)
        fr_clean = res_clean['frames'][100]
        # Calculate d = x - mean
        start0 = res_clean['starts'][100]
        x_seg = [int(v) for v in x_clean[start0 : start0 + K.NSAMP_WINDOW]]
        d_clean = [v - fr_clean['mean'] for v in x_seg]
        frames.append(("Clean Frame 100", d_clean, fr_clean['lp'], fr_clean['xw']))

    # Frame 1: Noisy frame (frame 100 from synthetic glide snr5)
    wav_noisy = os.path.join(GOLDEN_V2_DIR, "synth_glide_vuv_16k_snr5.wav")
    if os.path.exists(wav_noisy):
        x_noisy, _ = read_wav_float(wav_noisy)
        res_noisy = analyse_fixed(x_noisy, trace=True)
        fr_noisy = res_noisy['frames'][100]
        start0 = res_noisy['starts'][100]
        x_seg = [int(v) for v in x_noisy[start0 : start0 + K.NSAMP_WINDOW]]
        d_noisy = [v - fr_noisy['mean'] for v in x_seg]
        frames.append(("Noisy Frame 100 (SNR 5dB)", d_noisy, fr_noisy['lp'], fr_noisy['xw']))

    # Frame 2: Stress Frame A (pulse +32767 on background -32768)
    raw_a = np.full(K.NSAMP_WINDOW, -32768, dtype=np.int64)
    raw_a[300:340] = 32767
    fa = frame_fixed(raw_a, 32767, trace=True)
    d_stress_a = [int(v - fa['mean']) for v in raw_a]
    frames.append(("Stress Frame A (Pulse)", d_stress_a, fa['lp'], fa['xw']))

    # Frame 3: Stress Frame B (alternating full-scale square wave)
    raw_b = np.where((np.arange(K.NSAMP_WINDOW) // 27) % 2 == 0, 32767, -32768).astype(np.int64)
    raw_b[100:300] = -32768
    fb = frame_fixed(raw_b, 32767, trace=True)
    d_stress_b = [int(v - fb['mean']) for v in raw_b]
    frames.append(("Stress Frame B (Square)", d_stress_b, fb['lp'], fb['xw']))

    # Frame 4: Silence frame (all 0)
    raw_zero = np.zeros(K.NSAMP_WINDOW, dtype=np.int64)
    fz = frame_fixed(raw_zero, 1, trace=True)
    d_zero = [int(v - fz['mean']) for v in raw_zero]
    frames.append(("Silence Frame (Zero)", d_zero, fz['lp'], fz['xw']))

    return frames


def main():
    print("=" * 78)
    print("GENERATING VERIFICATION VECTORS FOR CH06 HANNING WINDOW")
    print("=" * 78)

    twin = HanningWindowTwin()
    frames = build_test_stimuli()
    print(f"Loaded {len(frames)} test frames for stimulus vector generation.")

    stim_records = []
    exp_records = []

    # Cycle 0-3: Reset sequence
    for _ in range(4):
        stim_records.append((0, 0, 0, 0))  # rst_n=0, start=0, in_valid=0, in_d=0
        out = twin.step(rst_n=0, start=0, in_valid=0, in_d=0)
        exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))

    # Idle cycle
    stim_records.append((1, 0, 0, 0))
    out = twin.step(rst_n=1, start=0, in_valid=0, in_d=0)
    exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))

    total_samples_checked = 0

    for f_idx, (name, d_vec, exp_lp, exp_xw) in enumerate(frames):
        print(f"Processing {name} ({len(d_vec)} samples)...")
        collected_xw = []
        final_lp = 0

        # Cycle: Pulse start
        # Sample 0 is presented at the start cycle or next cycle
        stim_records.append((1, 1, 1, d_vec[0]))
        out = twin.step(rst_n=1, start=1, in_valid=1, in_d=d_vec[0])
        exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))
        if out['out_valid']:
            collected_xw.append(out['out_xw'])

        # Stream samples 1..637
        for n in range(1, K.NSAMP_WINDOW):
            # Inject occasional 1-cycle bubble (in_valid=0) every 100 samples to verify handshake
            if n % 107 == 0:
                stim_records.append((1, 0, 0, 0))
                out = twin.step(rst_n=1, start=0, in_valid=0, in_d=0)
                exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))
                if out['out_valid']:
                    collected_xw.append(out['out_xw'])

            stim_records.append((1, 0, 1, d_vec[n]))
            out = twin.step(rst_n=1, start=0, in_valid=1, in_d=d_vec[n])
            exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))
            if out['out_valid']:
                collected_xw.append(out['out_xw'])

        # Flush pipeline (need at least 3 cycles for last sample to emerge)
        for _ in range(6):
            stim_records.append((1, 0, 0, 0))
            out = twin.step(rst_n=1, start=0, in_valid=0, in_d=0)
            exp_records.append((out['out_valid'], out['out_xw'], out['out_done'], out['out_lp']))
            if out['out_valid']:
                collected_xw.append(out['out_xw'])
            if out['out_done']:
                final_lp = out['out_lp']

        # Verify bit-exact match against golden_v2 for this frame
        assert collected_xw == exp_xw, f"Frame {f_idx} xw mismatch with golden_v2!"
        assert final_lp == exp_lp, f"Frame {f_idx} LP mismatch: got {final_lp}, exp {exp_lp}!"
        total_samples_checked += len(collected_xw)
        print(f"  -> Verified {len(collected_xw)} xw samples and LP = {final_lp} (100% bit-exact).")

    # Write stimulus and expected text files for iverilog
    stim_file = os.path.join(CURRENT_DIR, "tb_ch06_hanning_stim.txt")
    exp_file = os.path.join(CURRENT_DIR, "tb_ch06_hanning_expected.txt")

    with open(stim_file, "w", newline="\n") as f_stim, open(exp_file, "w", newline="\n") as f_exp:
        for rst_n, start, in_valid, in_d in stim_records:
            f_stim.write(f"{int(rst_n)} {int(start)} {int(in_valid)} {int(in_d)}\n")

        for out_valid, out_xw, out_done, out_lp in exp_records:
            f_exp.write(f"{int(out_valid)} {int(out_xw)} {int(out_done)} {int(out_lp)}\n")

    num_cycles = len(stim_records)
    print(f"\nSuccessfully wrote {num_cycles} clock cycle vectors to:")
    print(f"  Stimulus : {stim_file}")
    print(f"  Expected : {exp_file}")
    print(f"Total windowed samples verified : {total_samples_checked}")
    print("=" * 78)


if __name__ == "__main__":
    main()
