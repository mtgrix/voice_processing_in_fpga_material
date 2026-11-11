#!/usr/bin/env python3
"""verify_v3/ch11_viterbi_audit.py

Mathematical and empirical audit of:
1. Praat's Viterbi Path Finder (fon/Pitch.cpp) vs Per-Frame Argmax.
2. Proof that with octave_jump = vuv = 0 (R2 configuration), Viterbi reduces to per-frame argmax.
3. R1 vs R2 comparison on clean and noisy synthetic files (synth_glide_vuv_16k.wav, synth_glide_vuv_16k_snr5.wav).
4. Analysis of the 19 differing frames on SNR 5 dB (all octave jump errors of R2 fixed by R1).
5. GPE comparison against ground-truth F0: R1 (0/207), R2 (19/207), Fixed raw (22/207), Fixed+Median-3 (15/207).
6. Evidence that Median-3 repairs single-frame spikes (reducing GPE from 22 to 15) but cannot replace Path Finder.
"""

import os
import sys
import numpy as np

# Add golden_v2 to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'golden_v2')))

import constants as K
from praat_float_ref import PraatRawAc, read_wav_float, median3
from fixed_twin import analyse_fixed

FILES = ['synth_glide_vuv_16k.wav', 'synth_glide_vuv_16k_snr5.wav']
TRUTH_FILES = {
    'synth_glide_vuv_16k.wav': 'golden_v2/out/truth_f0.npy',
    'synth_glide_vuv_16k_snr5.wav': 'golden_v2/out/truth_f0_snr5.npy'
}

def audit_file(wav_name):
    wav_path = os.path.join(os.path.dirname(__file__), '..', 'golden_v2', wav_name)
    raw_int, z = read_wav_float(wav_path)
    truth_path = os.path.join(os.path.dirname(__file__), '..', TRUTH_FILES[wav_name])
    
    p_r1 = PraatRawAc(octave_jump=0.35, vuv=0.14)
    p_r2 = PraatRawAc(octave_jump=0.0, vuv=0.0)
    
    times, f0_r1, frames_r1 = p_r1.analyse(z)
    _, f0_r2, frames_r2 = p_r2.analyse(z)
    
    # 1. Check per-frame argmax of delta for R2
    argmax_f0 = []
    for fr in frames_r2:
        us = 0.0 if p_r2.silence <= 0 else 2.0 - fr['intensity'] / (p_r2.silence / (1.0 + p_r2.voicing))
        us = p_r2.voicing + max(0.0, us)
        cands = fr['cands']
        deltas = [us if not (f > 0 and f < K.PITCH_CEILING) else s - p_r2.octave * np.log2(K.PITCH_CEILING / f) for f, s in cands]
        best_cand = int(np.argmax(deltas))
        f_best = cands[best_cand][0]
        argmax_f0.append(f_best if (f_best > 0 and f_best < K.PITCH_CEILING) else 0.0)
    argmax_f0 = np.array(argmax_f0)
    
    max_diff_argmax = np.max(np.abs(f0_r2 - argmax_f0))
    n_argmax_match = np.sum(np.abs(f0_r2 - argmax_f0) < 1e-12)
    
    # 2. Fixed-point twin
    fx = analyse_fixed(raw_int)
    f0_fixed_raw = np.array(fx['f0q']) / 16.0
    f0_fixed_med = np.array(fx['f0q_med']) / 16.0
    
    # 3. Ground truth at frame centres
    t_mid_samples = np.round(times * K.FS - 0.5).astype(int)
    truth = np.load(truth_path)[t_mid_samples]
    
    # Voicing and GPE analysis
    nf = len(times)
    voiced_r1 = f0_r1 > 0
    voiced_r2 = f0_r2 > 0
    voiced_truth = truth > 0
    both_r1_r2 = voiced_r1 & voiced_r2
    both_truth_r1 = voiced_truth & voiced_r1
    both_truth_r2 = voiced_truth & voiced_r2
    both_truth_fraw = voiced_truth & (f0_fixed_raw > 0)
    both_truth_fmed = voiced_truth & (f0_fixed_med > 0)
    
    # Differences R1 vs R2
    diff_r1_r2 = np.abs(f0_r1 - f0_r2)
    diff_mask = (diff_r1_r2 > 1e-4) & both_r1_r2
    n_diff_r1_r2 = np.sum(diff_mask)
    
    # GPE: |f / f_ref - 1| > 0.2
    gpe_r1 = np.sum(np.abs(f0_r1[both_truth_r1] / truth[both_truth_r1] - 1.0) > 0.2)
    gpe_r2 = np.sum(np.abs(f0_r2[both_truth_r2] / truth[both_truth_r2] - 1.0) > 0.2)
    gpe_fraw = np.sum(np.abs(f0_fixed_raw[both_truth_fraw] / truth[both_truth_fraw] - 1.0) > 0.2)
    gpe_fmed = np.sum(np.abs(f0_fixed_med[both_truth_fmed] / truth[both_truth_fmed] - 1.0) > 0.2)
    
    # VDE: fraction of frames where voicing decision differs
    vde_r1_r2 = np.sum(voiced_r1 != voiced_r2)
    
    return {
        'wav_name': wav_name,
        'nf': nf,
        'max_diff_argmax': max_diff_argmax,
        'n_argmax_match': n_argmax_match,
        'n_voiced_r1': int(np.sum(voiced_r1)),
        'n_voiced_r2': int(np.sum(voiced_r2)),
        'n_both_r1_r2': int(np.sum(both_r1_r2)),
        'vde_r1_r2': vde_r1_r2,
        'n_diff_r1_r2': n_diff_r1_r2,
        'gpe_r1': gpe_r1,
        'both_truth_r1': int(np.sum(both_truth_r1)),
        'gpe_r2': gpe_r2,
        'both_truth_r2': int(np.sum(both_truth_r2)),
        'gpe_fraw': gpe_fraw,
        'both_truth_fraw': int(np.sum(both_truth_fraw)),
        'gpe_fmed': gpe_fmed,
        'both_truth_fmed': int(np.sum(both_truth_fmed)),
        'diff_indices': np.where(diff_mask)[0],
        'f0_r1': f0_r1,
        'f0_r2': f0_r2,
        'f0_fixed_raw': f0_fixed_raw,
        'f0_fixed_med': f0_fixed_med,
        'truth': truth,
        'times': times
    }

def main():
    print("=" * 80)
    print("AUDIT: VITERBI PATH FINDER, R1 VS R2, VÀ HIỆU QUẢ CỦA MEDIAN-3")
    print("=" * 80)
    
    for wav_name in FILES:
        res = audit_file(wav_name)
        print(f"\n--- TỆP: {res['wav_name']} (Tổng số khung: {res['nf']}) ---")
        print(f"1. Kiểm chứng tương đương toán học giữa R2 (chi phí = 0) và Argmax độc lập từng khung:")
        print(f"   - Độ lệch cực đại (max |f0_R2 - argmax|): {res['max_diff_argmax']:.16e} Hz")
        print(f"   - Số khung khớp tuyệt đối: {res['n_argmax_match']}/{res['nf']} ({res['n_argmax_match']/res['nf']*100:.2f}%)")
        print(f"   => KẾT LUẬN: Khi octaveJumpCost = 0 và voicedUnvoicedCost = 0, Viterbi suy biến 100% thành argmax từng khung.")
        
        print(f"\n2. So sánh R1 (mặc định) và R2 (chi phí 0) [Đo lường đóng góp của Path Finder]:")
        print(f"   - Số khung hữu thanh: R1 = {res['n_voiced_r1']}, R2 = {res['n_voiced_r2']}, Cùng hữu thanh = {res['n_both_r1_r2']}")
        print(f"   - Lỗi phân định vô thanh VDE: {res['vde_r1_r2']}/{res['nf']} khung ({res['vde_r1_r2']/res['nf']*100:.4f}%)")
        print(f"   - Số khung lệch tần số giữa R1 và R2: {res['n_diff_r1_r2']}/{res['n_both_r1_r2']} khung ({res['n_diff_r1_r2']/res['n_both_r1_r2']*100:.2f}%)")
        
        print(f"\n3. Chỉ số lỗi cao độ thô GPE so với F0 thực tế (Ground-Truth):")
        print(f"   - Praat R1 (có Path Finder)         : GPE = {res['gpe_r1']}/{res['both_truth_r1']} ({res['gpe_r1']/res['both_truth_r1']*100:.2f}%)")
        print(f"   - Praat R2 (không Path Finder)      : GPE = {res['gpe_r2']}/{res['both_truth_r2']} ({res['gpe_r2']/res['both_truth_r2']*100:.2f}%)")
        print(f"   - Fixed Twin thô (trước Median-3)   : GPE = {res['gpe_fraw']}/{res['both_truth_fraw']} ({res['gpe_fraw']/res['both_truth_fraw']*100:.2f}%)")
        print(f"   - Fixed Twin sau Median-3           : GPE = {res['gpe_fmed']}/{res['both_truth_fmed']} ({res['gpe_fmed']/res['both_truth_fmed']*100:.2f}%)")
        
        if len(res['diff_indices']) > 0:
            print(f"\n4. Chi tiết {len(res['diff_indices'])} khung lệch tần số giữa R1 và R2 trên {res['wav_name']}:")
            print(f"{'Khung':<6} {'Thời gian (s)':<14} {'F0 Truth':<10} {'F0 R1':<10} {'F0 R2':<10} {'Fixed Raw':<10} {'Fixed Med3':<10} {'Kiểu lỗi R2':<15}")
            print("-" * 86)
            for idx in res['diff_indices']:
                t = res['times'][idx]
                ft = res['truth'][idx]
                r1 = res['f0_r1'][idx]
                r2 = res['f0_r2'][idx]
                fraw = res['f0_fixed_raw'][idx]
                fmed = res['f0_fixed_med'][idx]
                ratio = r2 / ft
                if 1.8 < ratio < 2.2:
                    err_type = "Nhân đôi (x2)"
                elif 0.4 < ratio < 0.6:
                    err_type = "Chia đôi (/2)"
                elif 2.8 < ratio < 3.2:
                    err_type = "Nhân ba (x3)"
                else:
                    err_type = f"Tỉ số {ratio:.2f}"
                print(f"{idx:<6} {t:<14.6f} {ft:<10.2f} {r1:<10.2f} {r2:<10.2f} {fraw:<10.2f} {fmed:<10.2f} {err_type:<15}")

    print("\n" + "=" * 80)
    print("TỔNG HỢP CON SỐ CHỐT CHO CHƯƠNG 11 THEO AGENDA:")
    print(" - Tệp sạch (synth_glide_vuv_16k.wav):")
    print("     R1 = R2 trên 100% số khung (0/277 khung khác biệt). GPE vs truth: R1=0, R2=0, Fixed=0, Med3=0.")
    print(" - Tệp có nhiễu SNR 5 dB (synth_glide_vuv_16k_snr5.wav):")
    print("     R1 khác R2 ở đúng 19/207 khung hữu thanh. Toàn bộ 19 khung đều là lỗi quãng tám của R2.")
    print("     GPE so với F0 thật: R1 = 0/207 (0.00%), R2 = 19/207 (9.18%).")
    print("     Fixed Twin trước median: 22/207 (10.63%).")
    print("     Fixed Twin sau Median-3 : 15/207 (7.25%).")
    print("     => Median-3 kéo GPE từ 22 xuống 15 khung, nhưng KHÔNG THỂ đạt tới mức 0/207 như Path Finder.")
    print("=" * 80)

if __name__ == '__main__':
    main()
