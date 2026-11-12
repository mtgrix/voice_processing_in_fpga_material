"""verify_v3/ch13_hand_example.py
Calculates the 10-frame miniature hand calculation for Chapter 13.
Demonstrates:
  - 4 physical cases:
    1. Both voiced, small pitch difference (|f/fref - 1| <= 0.2)
    2. Both voiced, gross pitch error (|f/fref - 1| > 0.2, octave jump)
    3. Voicing mismatch: ref voiced, test unvoiced (VDE)
    4. Voicing mismatch: ref unvoiced, test voiced (VDE)
    5. Both unvoiced (silent / background noise)
  - VDE, GPE, FFE, and Fine Cent calculations.
"""
import numpy as np

def run_hand_example():
    # 10 frames of reference and test F0
    ref  = np.array([120.0, 125.0, 130.0, 135.0, 140.0, 150.0,   0.0,   0.0,   0.0,   0.0])
    test = np.array([120.5, 124.2, 130.8, 134.1, 280.0,   0.0, 160.0,   0.0,   0.0,   0.0])
    
    n = len(ref)
    vr = ref > 0.0
    vt = test > 0.0
    both = vr & vt
    vde_mask = vr != vt
    
    print("=" * 84)
    print("CH13 MINIATURE HAND CALCULATION: 10 FRAMES")
    print("=" * 84)
    print(f"{'Khung':<6}{'F0_ref (Hz)':<14}{'F0_test (Hz)':<14}{'Trạng thái':<22}{'Tỷ số f/fref':<16}{'Sai số cent':<12}")
    print("-" * 84)
    
    cents_list = []
    nongross_cents = []
    gpe_count = 0
    
    for k in range(n):
        r = ref[k]
        t = test[k]
        if r > 0 and t > 0:
            ratio = t / r
            c = 1200.0 * np.log2(ratio)
            cents_list.append(abs(c))
            if abs(ratio - 1.0) > 0.2:
                gpe_count += 1
                status = "Cùng hữu thanh (GPE)"
                ratio_str = f"{ratio:.4f} (> 1.20)"
                c_str = f"{c:+.2f}*"
            else:
                nongross_cents.append(abs(c))
                status = "Cùng hữu thanh (Khớp)"
                ratio_str = f"{ratio:.4f}"
                c_str = f"{c:+.2f}"
        elif r > 0 and t == 0:
            status = "Lệch âm tính (VDE: H->V)"
            ratio_str = "-"
            c_str = "-"
        elif r == 0 and t > 0:
            status = "Lệch âm tính (VDE: V->H)"
            ratio_str = "-"
            c_str = "-"
        else:
            status = "Cùng vô thanh"
            ratio_str = "-"
            c_str = "-"
            
        print(f"{k:<6}{r:<14.1f}{t:<14.1f}{status:<22}{ratio_str:<16}{c_str:<12}")
        
    print("-" * 84)
    
    vde_count = int(np.sum(vde_mask))
    both_count = int(np.sum(both))
    vde_rate = vde_count / n
    gpe_rate = gpe_count / both_count if both_count > 0 else 0.0
    ffe_rate = (vde_count + gpe_count) / n
    
    mean_abs_all = np.mean(cents_list) if cents_list else 0.0
    mean_abs_nongross = np.mean(nongross_cents) if nongross_cents else 0.0
    max_nongross = np.max(nongross_cents) if nongross_cents else 0.0
    
    print("\nTỔNG KẾT CÁC CHỈ SỐ:")
    print(f"  1. Tổng số khung phân tích (N)         : {n}")
    print(f"  2. Số khung hữu thanh mẫu (ref)        : {int(np.sum(vr))}")
    print(f"  3. Số khung hữu thanh thử nghiệm (test): {int(np.sum(vt))}")
    print(f"  4. Số khung cùng hữu thanh (both)      : {both_count}")
    print(f"  5. Số khung lệch âm tính (VDE)         : {vde_count}/{n} ({vde_rate*100:.1f}%)")
    print(f"  6. Số khung lỗi cao độ thô (GPE > 20%) : {gpe_count}/{both_count} ({gpe_rate*100:.1f}%)")
    print(f"  7. Tỷ lệ lỗi toàn diện khung (FFE)     : ({vde_count} + {gpe_count})/{n} = {ffe_rate*100:.1f}%")
    print(f"  8. Sai số cent mịn trung bình (bỏ GPE) : {mean_abs_nongross:.2f} cent")
    print(f"  9. Sai số cent mịn cực đại (bỏ GPE)    : {max_nongross:.2f} cent")
    print(f" 10. Sai số cent trung bình có GPE       : {mean_abs_all:.2f} cent (bị chi phối bởi 1200 cent của khung 4!)")
    print("=" * 84)

if __name__ == '__main__':
    run_hand_example()
