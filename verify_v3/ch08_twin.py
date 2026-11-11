#!/usr/bin/env python3
"""verify_v3/ch08_twin.py

Bit-exact, cycle-accurate Python twin of rtl/v3/ch08_norm_score.v.
Generates test stimuli and expected vectors for tb/v3/tb_ch08_norm.v.

Pipeline Structure (3 cycles latency from R[tau] to U[tau]/Sc[tau]):
  Stage 0 (Latch R0):
    sh = max(0, bitlen(R0) - 26)
    R0n = R0 >> sh
  Stage 1 (ROM address & shift):
    rom_addr = in_tau - 26
    rn_pipe1 = in_R >> sh (signed arithmetic shift)
  Stage 2 (Dual DSP Multiplications):
    prod_c = rn_pipe1 * C[tau] (signed 27x17)
    prod_k = R0n * K[tau] (signed 27x16)
  Stage 3 (Rounding & Output):
    U = (prod_c + 8192) >> 14
    term_k = (prod_k + 524288) >> 20
    Sc = U - term_k
"""

import os
import sys
import math
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, os.path.join(REPO_DIR, 'golden_v2'))

import constants as K
from gen_roms import hanning_q15, c_table, k_table
from fixed_twin import analyse_fixed
from praat_float_ref import read_wav_float

# Load canonical C and K tables
W_CANON = hanning_q15()
C_CANON = c_table(W_CANON)
K_CANON = k_table()

class NormScoreTwin:
    def __init__(self, init_file=None):
        self.C = dict(C_CANON)
        self.K = dict(K_CANON)
        self.reset()

    def reset(self):
        # Latch registers for R0
        self.sh_reg = 0
        self.r0n_reg = 0

        # Stage 1 registers
        self.v_pipe1 = 0
        self.tau_pipe1 = 0
        self.rn_pipe1 = 0
        self.r0n_pipe1 = 0

        # Stage 2 registers
        self.v_pipe2 = 0
        self.tau_pipe2 = 0
        self.prod_c_pipe2 = 0
        self.prod_k_pipe2 = 0
        self.r0n_pipe2 = 0

        # Stage 3 registers (outputs)
        self.out_valid = 0
        self.out_tau = 0
        self.out_U = 0
        self.out_Sc = 0
        self.out_R0n = 0
        self.out_sh = 0
        self.out_last = 0

    @staticmethod
    def calc_bitlen(val):
        if val <= 0:
            return 0
        return val.bit_length()

    def step(self, rst_n, in_valid, in_tau, in_R):
        """Cycle-accurate step function.
        Simulates hardware registered behavior:
        1. Capture current registered outputs.
        2. Compute next internal state.
        3. Advance internal registers on posedge clk.
        """
        if not rst_n:
            self.reset()
            return {
                'out_valid': 0, 'out_tau': 0, 'out_U': 0,
                'out_Sc': 0, 'out_R0n': 0, 'out_sh': 0, 'out_last': 0
            }

        # Current outputs reflecting Stage 3 registers
        curr_out = {
            'out_valid': int(self.out_valid),
            'out_tau': int(self.out_tau),
            'out_U': int(self.out_U),
            'out_Sc': int(self.out_Sc),
            'out_R0n': int(self.out_R0n),
            'out_sh': int(self.out_sh),
            'out_last': int(self.out_last)
        }

        # ---------------------------------------------------------------------
        # Next state computation for Stage 3 (Outputs)
        # ---------------------------------------------------------------------
        if self.v_pipe2:
            next_out_valid = 1
            next_out_tau = self.tau_pipe2
            next_out_R0n = self.r0n_pipe2
            next_out_sh = self.sh_reg
            next_out_last = 1 if self.tau_pipe2 == K.TAU_SCAN_MAX else 0

            # Rounding and shifts
            u_div = (self.prod_c_pipe2 + 8192) >> 14
            k_div = (self.prod_k_pipe2 + 524288) >> 20
            sc_diff = u_div - k_div

            # Clamp to 28-bit signed integer range for bit-exact HDL matching
            # Signed 28-bit range: [-134217728, 134217727]
            next_out_U = ((u_div + (1 << 27)) % (1 << 28)) - (1 << 27)
            next_out_Sc = ((sc_diff + (1 << 27)) % (1 << 28)) - (1 << 27)
        else:
            next_out_valid = 0
            next_out_tau = 0
            next_out_U = 0
            next_out_Sc = 0
            next_out_R0n = self.r0n_pipe2
            next_out_sh = self.sh_reg
            next_out_last = 0

        # ---------------------------------------------------------------------
        # Next state computation for Stage 2 (Multiplication)
        # ---------------------------------------------------------------------
        if self.v_pipe1:
            next_v_pipe2 = 1
            next_tau_pipe2 = self.tau_pipe1
            next_r0n_pipe2 = self.r0n_pipe1
            tau = self.tau_pipe1
            c_coeff = self.C[tau]
            k_coeff = self.K[tau]
            next_prod_c = self.rn_pipe1 * c_coeff
            next_prod_k = self.r0n_pipe1 * k_coeff
        else:
            next_v_pipe2 = 0
            next_tau_pipe2 = 0
            next_r0n_pipe2 = 0
            next_prod_c = 0
            next_prod_k = 0

        # ---------------------------------------------------------------------
        # Next state computation for Stage 1 (ROM Address & Shift)
        # ---------------------------------------------------------------------
        if in_valid and (K.TAU_SCAN_MIN <= in_tau <= K.TAU_SCAN_MAX):
            next_v_pipe1 = 1
            next_tau_pipe1 = in_tau
            next_rn_pipe1 = in_R >> self.sh_reg
            next_r0n_pipe1 = self.r0n_reg
        else:
            next_v_pipe1 = 0
            next_tau_pipe1 = 0
            next_rn_pipe1 = 0
            next_r0n_pipe1 = 0

        # ---------------------------------------------------------------------
        # Latch R0 when in_tau == 0
        # ---------------------------------------------------------------------
        if in_valid and (in_tau == 0):
            r0_val = max(0, in_R)
            r0_bitlen = self.calc_bitlen(r0_val)
            sh_val = max(0, r0_bitlen - 26)
            self.sh_reg = sh_val
            self.r0n_reg = r0_val >> sh_val

        # ---------------------------------------------------------------------
        # Clock edge: advance registers
        # ---------------------------------------------------------------------
        self.v_pipe1 = next_v_pipe1
        self.tau_pipe1 = next_tau_pipe1
        self.rn_pipe1 = next_rn_pipe1
        self.r0n_pipe1 = next_r0n_pipe1

        self.v_pipe2 = next_v_pipe2
        self.tau_pipe2 = next_tau_pipe2
        self.prod_c_pipe2 = next_prod_c
        self.prod_k_pipe2 = next_prod_k
        self.r0n_pipe2 = next_r0n_pipe2

        self.out_valid = next_out_valid
        self.out_tau = next_out_tau
        self.out_U = next_out_U
        self.out_Sc = next_out_Sc
        self.out_R0n = next_out_R0n
        self.out_sh = next_out_sh
        self.out_last = next_out_last

        return curr_out


def generate_verification_vectors():
    print("=" * 80)
    print("GENERATING VERIFICATION VECTORS FOR CH08 NORMALIZATION & OCTAVE SCORING")
    print("=" * 80)

    stim_file = os.path.join(BASE_DIR, "tb_ch08_norm_stim.txt")
    exp_file = os.path.join(BASE_DIR, "tb_ch08_norm_expected.txt")

    twin = NormScoreTwin()
    stim_records = []

    # 1. Initial reset sequence (5 cycles)
    for _ in range(5):
        stim_records.append((0, 0, 0, 0))

    # Helper function to append frame stimulus
    def append_frame_stimulus(r0, r_dict, insert_bubbles=False):
        # 1 idle cycle before R0
        stim_records.append((1, 0, 0, 0))
        # R0 at in_tau = 0
        stim_records.append((1, 1, 0, r0))
        # 2 idle cycles after R0
        stim_records.append((1, 0, 0, 0))
        stim_records.append((1, 0, 0, 0))

        # Stream lags tau = 26..214
        for tau in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1):
            r_val = r_dict[tau]
            stim_records.append((1, 1, tau, r_val))
            if insert_bubbles and (tau % 17 == 0):
                # occasional bubble / stall cycle
                stim_records.append((1, 0, 0, 0))

        # 5 drain cycles after frame
        for _ in range(5):
            stim_records.append((1, 0, 0, 0))

    # Frame 1 & 2: Clean speech frames from golden_v2
    wav_clean = os.path.join(REPO_DIR, 'golden_v2', 'synth_glide_vuv_16k.wav')
    if os.path.exists(wav_clean):
        xi, _ = read_wav_float(wav_clean)
        res_clean = analyse_fixed(xi, trace=True)
        # Select frame 40 (glide active) and frame 240 (vibrato active)
        for f_idx in [40, 240]:
            fr = res_clean['frames'][f_idx]
            append_frame_stimulus(fr['r0'], fr['R'], insert_bubbles=False)

    # Frame 3: Noisy speech frame (SNR 5 dB) with bubble stalls
    wav_noisy = os.path.join(REPO_DIR, 'golden_v2', 'synth_glide_vuv_16k_snr5.wav')
    if os.path.exists(wav_noisy):
        xi, _ = read_wav_float(wav_noisy)
        res_noisy = analyse_fixed(xi, trace=True)
        fr_noisy = res_noisy['frames'][60]
        append_frame_stimulus(fr_noisy['r0'], fr_noisy['R'], insert_bubbles=True)

    # Frame 4: Stress Frame Full-Scale (Maximum dynamic range R0 ~ 2^42)
    # xw alternating full-scale +/- 59379
    xw_stress = [59379 if j % 2 == 0 else -59379 for j in range(638)]
    r0_stress = sum(v * v for v in xw_stress)
    r_stress = {t: sum(xw_stress[j] * xw_stress[j + t] for j in range(638 - t))
                for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1)}
    append_frame_stimulus(r0_stress, r_stress, insert_bubbles=False)

    # Frame 5: Small amplitude frame (R0 small, bitlen <= 26, sh = 0)
    xw_small = [15 if j % 2 == 0 else -15 for j in range(638)]
    r0_small = sum(v * v for v in xw_small)
    r_small = {t: sum(xw_small[j] * xw_small[j + t] for j in range(638 - t))
               for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1)}
    append_frame_stimulus(r0_small, r_small, insert_bubbles=False)

    # Frame 6: Silence Frame (R0 = 0, R[tau] = 0)
    r0_zero = 0
    r_zero = {t: 0 for t in range(K.TAU_SCAN_MIN, K.TAU_SCAN_MAX + 1)}
    append_frame_stimulus(r0_zero, r_zero, insert_bubbles=False)

    # Additional drain cycles at the end
    for _ in range(10):
        stim_records.append((1, 0, 0, 0))

    total_cycles = len(stim_records)
    print(f"Total simulation cycles generated: {total_cycles} cycles (>= 200 required)")

    # Execute twin cycle-by-cycle to produce expected vectors
    exp_records = []
    twin.reset()
    for stim in stim_records:
        rst_n, in_vld, in_t, in_r = stim
        out = twin.step(rst_n, in_vld, in_t, in_r)
        exp_records.append(out)

    # Write stimulus file
    with open(stim_file, "w", newline="\n") as f_stim:
        for rst_n, in_vld, in_t, in_r in stim_records:
            f_stim.write(f"{int(rst_n)} {int(in_vld)} {int(in_t)} {int(in_r)}\n")

    # Write expected output file
    with open(exp_file, "w", newline="\n") as f_exp:
        for out in exp_records:
            f_exp.write(f"{int(out['out_valid'])} {int(out['out_tau'])} {int(out['out_U'])} "
                        f"{int(out['out_Sc'])} {int(out['out_R0n'])} {int(out['out_sh'])} "
                        f"{int(out['out_last'])}\n")

    print(f"Wrote stimulus to : {stim_file}")
    print(f"Wrote expected to : {exp_file}")
    print("=" * 80)
    return total_cycles

if __name__ == "__main__":
    generate_verification_vectors()
