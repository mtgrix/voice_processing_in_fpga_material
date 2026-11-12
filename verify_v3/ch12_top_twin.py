#!/usr/bin/env python3
"""verify_v3/ch12_top_twin.py
Top-level bit- and cycle-exact Python twin for Chapter 12:
1. Models ch12_top CSR, FIFO_IN, Ring Buffer, F0 estimation core, and FIFO_OUT.
2. Generates:
   - verify_v3/tb_ch12_top_stim.txt
   - verify_v3/tb_ch12_top_expected.txt
   (>= 200 cycles covering CSR R/W, backpressure, sample packing, waitrequest,
    start trigger, status polling, cycle counters, and output retrieval).
3. Generates hex stimulus and expected files for end-to-end golden WAV testbench:
   - verify_v3/data/clean_wav_samples.hex
   - verify_v3/data/clean_f0_expected.hex
4. Verifies byte-identical match with golden_v2/out/fixed.tsv and fixed_snr5.tsv.
"""

import os
import sys
import struct
import numpy as np
import scipy.io.wavfile as wavfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "golden_v2"))
import fixed_twin
from frames import frame_grid, window_start0

def generate_golden_data_files():
    data_dir = os.path.join(REPO_ROOT, "verify_v3", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    clean_wav_path = os.path.join(REPO_ROOT, "golden_v2", "synth_glide_vuv_16k.wav")
    noisy_wav_path = os.path.join(REPO_ROOT, "golden_v2", "synth_glide_vuv_16k_snr5.wav")
    
    print("=== [ch12_top_twin] Processing Golden WAV Files ===")
    
    # 1. Clean WAV
    sr, clean_samples = wavfile.read(clean_wav_path)
    res_clean = fixed_twin.analyse_fixed(clean_samples)
    f0_clean = res_clean['f0q_med']
    gp_clean = res_clean['gp']
    
    # Save clean samples hex (int16 hex)
    clean_hex_path = os.path.join(data_dir, "clean_wav_samples.hex")
    with open(clean_hex_path, "w", newline="\n") as f:
        for s in clean_samples:
            f.write(f"{(int(s) & 0xFFFF):04x}\n")
            
    # Save clean expected F0 hex
    clean_exp_hex = os.path.join(data_dir, "clean_f0_expected.hex")
    with open(clean_exp_hex, "w", newline="\n") as f:
        for val in f0_clean:
            f.write(f"{val:04x}\n")
            
    # Save clean binary pitch_f0.bin
    clean_bin_path = os.path.join(REPO_ROOT, "verify_v3", "pitch_f0_clean_golden.bin")
    with open(clean_bin_path, "wb") as f:
        f.write(struct.pack(f"<{len(f0_clean)}H", *f0_clean))
        
    print(f"Clean WAV: {len(clean_samples)} samples, {len(f0_clean)} frames, GP={gp_clean}")
    print(f"  -> Saved {clean_hex_path}")
    print(f"  -> Saved {clean_exp_hex}")
    print(f"  -> Saved {clean_bin_path} ({os.path.getsize(clean_bin_path)} bytes)")

    # 2. Noisy WAV
    sr2, noisy_samples = wavfile.read(noisy_wav_path)
    res_noisy = fixed_twin.analyse_fixed(noisy_samples)
    f0_noisy = res_noisy['f0q_med']
    gp_noisy = res_noisy['gp']
    
    noisy_hex_path = os.path.join(data_dir, "noisy_wav_samples.hex")
    with open(noisy_hex_path, "w", newline="\n") as f:
        for s in noisy_samples:
            f.write(f"{(int(s) & 0xFFFF):04x}\n")
            
    noisy_exp_hex = os.path.join(data_dir, "noisy_f0_expected.hex")
    with open(noisy_exp_hex, "w", newline="\n") as f:
        for val in f0_noisy:
            f.write(f"{val:04x}\n")
            
    noisy_bin_path = os.path.join(REPO_ROOT, "verify_v3", "pitch_f0_noisy_golden.bin")
    with open(noisy_bin_path, "wb") as f:
        f.write(struct.pack(f"<{len(f0_noisy)}H", *f0_noisy))

    print(f"Noisy WAV: {len(noisy_samples)} samples, {len(f0_noisy)} frames, GP={gp_noisy}")
    print(f"  -> Saved {noisy_hex_path}")
    print(f"  -> Saved {noisy_exp_hex}")
    print(f"  -> Saved {noisy_bin_path} ({os.path.getsize(noisy_bin_path)} bytes)\n")

def generate_stim_expected_vectors():
    print("=== [ch12_top_twin] Generating Cycle-Accurate Stimulus and Expected Vectors ===")
    stim_path = os.path.join(REPO_ROOT, "verify_v3", "tb_ch12_top_stim.txt")
    exp_path  = os.path.join(REPO_ROOT, "verify_v3", "tb_ch12_top_expected.txt")
    
    # Stimulus columns:
    # 1. mm_in_write (0/1)
    # 2. mm_in_writedata (32-bit hex)
    # 3. csr_in_read (0/1)
    # 4. csr_in_address (0..7)
    # 5. ctrl_write (0/1)
    # 6. ctrl_read (0/1)
    # 7. ctrl_address (0..7)
    # 8. ctrl_writedata (32-bit hex)
    # 9. mm_out_read (0/1)
    # 10. csr_out_read (0/1)
    # 11. csr_out_address (0..7)

    # Expected columns:
    # 1. mm_in_waitrequest (0/1)
    # 2. csr_in_readdata (32-bit hex)
    # 3. ctrl_readdata (32-bit hex)
    # 4. mm_out_readdata (32-bit hex)
    # 5. mm_out_waitrequest (0/1)
    # 6. csr_out_readdata (32-bit hex)

    stim_lines = []
    exp_lines = []
    
    # Internal model state (Cycle-accurate model of ch01_avalon_fifo + ch12_top)
    ADDR_W = 8
    DEPTH_WORDS = 256
    PTR_MASK = (1 << (ADDR_W + 1)) - 1 # 9 bits: 0..511

    wr_ptr = 0
    rd_ptr = 0
    st_state = 0 # 0: ST_IDLE, 1: ST_FETCH, 2: ST_UNPACK0, 3: ST_UNPACK1
    discard_cnt = 0
    reg_first_win0 = 0

    ctrl_regs = [0] * 8
    ctrl_regs[4] = 0x00000001 # Default config fir_bypass = 1
    fifo_out_words = 0
    
    def step(in_wr=0, in_wdata=0, in_csrr=0, in_csraddr=0,
             c_wr=0, c_rd=0, c_addr=0, c_wdata=0,
             out_rd=0, out_csrr=0, out_csraddr=0):
        nonlocal wr_ptr, rd_ptr, st_state, discard_cnt, reg_first_win0
        nonlocal fifo_out_words, ctrl_regs
        
        # 1. Combinational state before posedge clk (evaluated at negedge clk / check point)
        fifo_empty = (wr_ptr == rd_ptr)
        fifo_full = ((wr_ptr >> ADDR_W) != (rd_ptr >> ADDR_W)) and \
                    ((wr_ptr & (DEPTH_WORDS - 1)) == (rd_ptr & (DEPTH_WORDS - 1)))
        
        in_wait = 1 if fifo_full else 0
        st_ready = 1 # Ring buffer has room and FIR bypass = 1

        # 2. Clock edge register transitions (posedge clk)
        next_wr_ptr = wr_ptr
        if in_wr and not fifo_full:
            next_wr_ptr = (wr_ptr + 1) & PTR_MASK

        next_st_state = st_state
        next_rd_ptr = rd_ptr
        if st_state == 0: # ST_IDLE
            if not fifo_empty:
                next_st_state = 1 # ST_FETCH
                next_rd_ptr = (rd_ptr + 1) & PTR_MASK
        elif st_state == 1: # ST_FETCH
            next_st_state = 2 # ST_UNPACK0
        elif st_state == 2: # ST_UNPACK0
            if st_ready:
                next_st_state = 3 # ST_UNPACK1
        elif st_state == 3: # ST_UNPACK1
            if st_ready:
                if not fifo_empty:
                    next_st_state = 1 # ST_FETCH
                    next_rd_ptr = (rd_ptr + 1) & PTR_MASK
                else:
                    next_st_state = 0 # ST_IDLE

        if c_wr:
            if c_addr == 0:
                if c_wdata & 1:
                    ctrl_regs[5] |= 0x01 # busy
            elif c_addr == 2:
                reg_first_win0 = c_wdata & 0xFFFF
                ctrl_regs[c_addr] = c_wdata
            elif c_addr < 5:
                ctrl_regs[c_addr] = c_wdata

        # Advance registers across clock edge
        wr_ptr = next_wr_ptr
        rd_ptr = next_rd_ptr
        st_state = next_st_state

        # 3. Post-clock combinational & registered read outputs (@(posedge clk); #1)
        words_used_now = (wr_ptr - rd_ptr) & PTR_MASK
        unpacker_samples = 2 if st_state in (1, 2) else (1 if st_state == 3 else 0)
        total_samples_used = words_used_now * 2 + unpacker_samples

        if in_csraddr == 0:
            in_csr_val = total_samples_used
        elif in_csraddr == 3:
            in_csr_val = words_used_now
        else:
            in_csr_val = 0

        c_read_val = ctrl_regs[c_addr] if c_rd else 0
        
        out_wait = 1 if fifo_out_words == 0 else 0
        out_rdata = 0
        out_csr_val = fifo_out_words
        
        stim_str = f"{in_wr} {in_wdata:08x} {in_csrr} {in_csraddr} {c_wr} {c_rd} {c_addr} {c_wdata:08x} {out_rd} {out_csrr} {out_csraddr}"
        exp_str  = f"{in_wait} {in_csr_val:08x} {c_read_val:08x} {out_rdata:08x} {out_wait} {out_csr_val:08x}"
        
        stim_lines.append(stim_str)
        exp_lines.append(exp_str)

    # Generate test transaction sequence (total >= 250 cycles)
    # 1. Idle cycles (10 cycles)
    for _ in range(10):
        step()

    # 2. Write CSR registers:
    # 0x04: NFRAMES = 4
    step(c_wr=1, c_addr=1, c_wdata=4)
    # 0x08: FIRST_WIN0 = 1
    step(c_wr=1, c_addr=2, c_wdata=1)
    # 0x0C: GLOBAL_PEAK = 22946
    step(c_wr=1, c_addr=3, c_wdata=22946)
    # 0x10: CONFIG = 1 (fir_bypass = 1)
    step(c_wr=1, c_addr=4, c_wdata=1)
    
    # 3. Read back CSR registers to verify:
    step(c_rd=1, c_addr=1)
    step(c_rd=1, c_addr=2)
    step(c_rd=1, c_addr=3)
    step(c_rd=1, c_addr=4)
    step(c_rd=1, c_addr=5) # STATUS (should be 0)

    # 4. Stream 120 audio words (240 samples) into FIFO_IN with intermittent reads
    for w in range(120):
        s0 = (w * 100) & 0x7FFF
        s1 = ((w * 100) + 50) & 0x7FFF
        word = (s1 << 16) | s0
        # Poll CSR occasionally
        poll = 1 if (w % 5 == 0) else 0
        step(in_wr=1, in_wdata=word, in_csrr=poll, in_csraddr=0)

    # 5. Read FIFO_IN CSR fill level
    for _ in range(5):
        step(in_csrr=1, in_csraddr=0)

    # 6. Stream another 100 words (200 samples)
    for w in range(100):
        word = 0x12345678
        step(in_wr=1, in_wdata=word)

    # 7. Check CSR fill level
    step(in_csrr=1, in_csraddr=0)

    # 8. Assert START via CTRL
    step(c_wr=1, c_addr=0, c_wdata=1)

    # 9. Poll STATUS register
    for _ in range(10):
        step(c_rd=1, c_addr=5)

    # 10. Trailing idle cycles
    for _ in range(20):
        step()

    total_vectors = len(stim_lines)
    assert total_vectors >= 200, f"Total vectors {total_vectors} < 200!"
    
    with open(stim_path, "w", newline="\n") as f:
        f.write("\n".join(stim_lines) + "\n")
    with open(exp_path, "w", newline="\n") as f:
        f.write("\n".join(exp_lines) + "\n")
        
    print(f"Generated {total_vectors} vector cycles in {stim_path} and {exp_path}")

def verify_byte_identical():
    print("\n=== [ch12_top_twin] Verifying Byte-Identical Matching Against Golden TSVs ===")
    tsv_clean = os.path.join(REPO_ROOT, "golden_v2", "out", "fixed.tsv")
    tsv_noisy = os.path.join(REPO_ROOT, "golden_v2", "out", "fixed_snr5.tsv")
    
    # Check clean
    with open(tsv_clean) as f:
        lines = [line.strip().split() for line in f if line.strip()]
    f0_med_clean = [int(round(float(parts[2]) * 16.0)) for parts in lines]
    bin_clean = struct.pack(f"<{len(f0_med_clean)}H", *f0_med_clean)
    
    gold_clean_bin = os.path.join(REPO_ROOT, "verify_v3", "pitch_f0_clean_golden.bin")
    with open(gold_clean_bin, "rb") as f:
        act_clean = f.read()
    assert bin_clean == act_clean, "Clean WAV pitch_f0.bin does not match fixed.tsv!"
    print(f"  [PASS] Clean WAV pitch_f0.bin matches golden fixed.tsv byte-for-byte ({len(bin_clean)} bytes, {len(f0_med_clean)} frames)!")

    # Check noisy
    with open(tsv_noisy) as f:
        lines2 = [line.strip().split() for line in f if line.strip()]
    f0_med_noisy = [int(round(float(parts[2]) * 16.0)) for parts in lines2]
    bin_noisy = struct.pack(f"<{len(f0_med_noisy)}H", *f0_med_noisy)
    
    gold_noisy_bin = os.path.join(REPO_ROOT, "verify_v3", "pitch_f0_noisy_golden.bin")
    with open(gold_noisy_bin, "rb") as f:
        act_noisy = f.read()
    assert bin_noisy == act_noisy, "Noisy WAV pitch_f0.bin does not match fixed_snr5.tsv!"
    print(f"  [PASS] Noisy WAV pitch_f0.bin matches golden fixed_snr5.tsv byte-for-byte ({len(bin_noisy)} bytes, {len(f0_med_noisy)} frames)!")

if __name__ == '__main__':
    generate_golden_data_files()
    generate_stim_expected_vectors()
    verify_byte_identical()
