#!/usr/bin/env python3
"""verify_v3/ch10_exercises.py

End-of-chapter exercises and numeric verification for Chapter 10:
Exercise 10.1: Mathematical derivation of transition boundaries and cross-multiplication
Exercise 10.2: Hand calculation walkthrough for a concrete frame in the ramp zone
Exercise 10.3: Dynamic range and 54-bit signed representation bounds proof
Exercise 10.4: Edge cases, silence traps (R0=0, LP=0, GP=0), and near-threshold sensitivity
"""

import math

def ex10_1():
    print("=" * 70)
    print("BÀI TẬP 10.1: DẪN XUẤT TOÁN HỌC VÙNG DỐC VÀ BẤT ĐẲNG THỨC NHÂN CHÉO")
    print("=" * 70)
    silence_thresh = 0.03
    voicing_thresh = 0.45
    factor = (1.0 + voicing_thresh) / silence_thresh  # 1.45 / 0.03 = 145 / 3

    print(f"(a) Hệ số dốc: (1 + {voicing_thresh}) / {silence_thresh} = 1.45 / 0.03 = 145 / 3 = {factor:.6f}")
    # Ramp ends when 2 - I * (145/3) = 0 => I = 6 / 145
    I_end = 6.0 / 145.0
    print(f"    Điểm kết thúc vùng dốc: I_end = 6 / 145 = {I_end:.8f} (xấp xỉ 0.0414)")
    print(f"    Sai số làm tròn so với số 0.0414 trong giáo trình: {abs(I_end - 0.0414):.8f}")

    # (b) Tại I < 0.03
    I_test = 0.03
    r_unv_003 = voicing_thresh + max(0.0, 2.0 - I_test * factor)
    print(f"(b) Tại ngưỡng im lặng I = 0.03: R_unvoiced = {voicing_thresh} + (2 - {I_test} * 145/3) = {voicing_thresh} + {2 - I_test * factor:.4f} = {r_unv_003:.4f}")
    print(f"    Với I < 0.03, R_unvoiced > 1.00. Do hệ số tự tương quan chuẩn hóa r(tau) <= 1.0 và octave cost > 0,")
    print(f"    độ mạnh cực đại của ứng viên hữu thanh Sc/R0n luôn < 1.0, do đó khung chắc chắn vô thanh.")

    # (c) Bất đẳng thức nhân chéo
    print("(c) Nhân chéo hai vế với 300 * R0n * GP > 0:")
    print("    Sc / R0n - 45/100 > max(0, 2 - (145*LP)/(3*GP))")
    print("    <=> (100*Sc - 45*R0n)/(100*R0n) > max(0, (6*GP - 145*LP)/(3*GP))")
    print("    <=> (100*Sc - 45*R0n) * 3 * GP > 100 * R0n * max(0, 6*GP - 145*LP)")
    print("    Dấu > chặt là bắt buộc vì ứng viên 1 (vô thanh) đứng đầu danh sách, khi hòa điểm vô thanh thắng.")
    print("[+] Bài tập 10.1 xác minh thành công.\n")

def ex10_2():
    print("=" * 70)
    print("BÀI TẬP 10.2: TÍNH TOÁN THỦ CÔNG THU NHỎ TRONG VÙNG DỐC")
    print("=" * 70)
    GP = 20000
    LP = 760
    R0n = 1000000
    Sc = 700000

    # (a) Cường độ I
    I = LP / GP
    print(f"(a) Cường độ tương đối: I = LP / GP = {LP} / {GP} = {I:.4f}")
    in_ramp = (0.03 <= I <= 6.0/145.0)
    print(f"    Kiểm tra vùng: 0.03 <= {I:.4f} <= {6.0/145.0:.4f} => Khung nằm trong vùng DỐC CHUYỂN TIẾP: {in_ramp}")

    # (b) Float R_unvoiced
    r_unv = 0.45 + max(0.0, 2.0 - I * 145.0 / 3.0)
    strength = Sc / R0n
    float_voiced = (strength > r_unv)
    print(f"(b) Công thức Praat dấu phẩy động:")
    print(f"    R_unvoiced = 0.45 + (2.0 - {I:.4f} * 145 / 3) = 0.45 + {2.0 - I * 145.0 / 3.0:.6f} = {r_unv:.6f}")
    print(f"    Strength hữu thanh = Sc / R0n = {Sc} / {R0n} = {strength:.6f}")
    print(f"    So sánh: {strength:.6f} > {r_unv:.6f} => Hữu thanh (Voiced) = {float_voiced}")

    # (c) Fixed inequality
    term1 = 100 * Sc - 45 * R0n
    mult3_GP = 3 * GP
    LHS = term1 * mult3_GP

    term_ramp = 6 * GP - 145 * LP
    ramp_pos = max(0, term_ramp)
    RHS = 100 * R0n * ramp_pos
    fixed_voiced = (LHS > RHS)

    print(f"(c) Công thức nhân chéo số nguyên:")
    print(f"    term1 = 100 * {Sc} - 45 * {R0n} = {100*Sc} - {45*R0n} = {term1}")
    print(f"    3 * GP = 3 * {GP} = {mult3_GP}")
    print(f"    LHS = {term1} * {mult3_GP} = {LHS}")
    print(f"    6 * GP - 145 * LP = 6 * {GP} - 145 * {LP} = {6*GP} - {145*LP} = {term_ramp}")
    print(f"    ramp_pos = max(0, {term_ramp}) = {ramp_pos}")
    print(f"    100 * R0n = 100 * {R0n} = {100*R0n}")
    print(f"    RHS = {100*R0n} * {ramp_pos} = {RHS}")
    print(f"    LHS > RHS: {LHS} > {RHS} => {LHS > RHS} => Hữu thanh (Voiced) = {fixed_voiced}")
    print(f"    Độ chênh lệch: LHS - RHS = {LHS - RHS}")
    assert float_voiced == fixed_voiced
    print("[+] Bài tập 10.2 xác minh thành công.\n")

def ex10_3():
    print("=" * 70)
    print("BÀI TẬP 10.3: PHÂN TÍCH ĐỘ RỘNG BIT VÀ TRÀN SỐ PHẦN CỨNG")
    print("=" * 70)
    max_Sc = (1 << 27) - 1
    max_R0n = (1 << 27) - 1
    max_GP = 32768
    max_LP = 59379

    # LHS worst case positive
    term1_max = 100 * max_Sc
    term1_min = -45 * max_R0n
    mult3_GP_max = 3 * max_GP
    lhs_max = term1_max * mult3_GP_max
    lhs_min = term1_min * mult3_GP_max

    # RHS worst case
    rhs_max = 100 * max_R0n * (6 * max_GP)

    print(f"(a) Giá trị biên cực trị:")
    print(f"    Max term1 = 100 * (2^27 - 1) = {term1_max} (< 2^34)")
    print(f"    Min term1 = -45 * (2^27 - 1) = {term1_min} (> -2^33)")
    print(f"    Max 3*GP = 3 * 32768 = {mult3_GP_max} (< 2^17)")
    print(f"    LHS max = {lhs_max} < 2^51 (2^51 = {1 << 51})")
    print(f"    LHS min = {lhs_min} > -2^50 (-2^50 = {- (1 << 50)})")
    print(f"    RHS max = 100 * (2^27 - 1) * 196608 = {rhs_max} < 2^52 (2^52 = {1 << 52})")

    # (b) Bounds proof
    bound_54 = 1 << 53
    print(f"(b) Giới hạn của số nguyên có dấu 54 bit: [-2^53, 2^53 - 1]")
    print(f"    2^53 = {bound_54}")
    print(f"    LHS max < 2^53: {lhs_max < bound_54}")
    print(f"    LHS min >= -2^53: {lhs_min >= -bound_54}")
    print(f"    RHS max < 2^53: {rhs_max < bound_54}")
    print(f"    Kết luận: Định dạng 54-bit có dấu hoàn toàn không bao giờ tràn số.")

    # (c) Silicon analysis
    print(f"(c) So sánh phần cứng: Bộ so sánh 54-bit chỉ tốn khoảng 54 LE/ALM (chuỗi carry chain cứng),")
    print(f"    hoạt động trong 1 chu kỳ tại 50 MHz. Ngược lại, bộ chia dấu phẩy động chuẩn IEEE-754 tốn")
    print(f"    hàng trăm ALM và độ trễ 10-20 chu kỳ.")
    print("[+] Bài tập 10.3 xác minh thành công.\n")

def ex10_4():
    print("=" * 70)
    print("BÀI TẬP 10.4: CÁC CA BIÊN, BẪY IM LẶNG VÀ ĐỘ NHẠY SÁT NGƯỠNG")
    print("=" * 70)
    # (a) Bẫy im lặng khi R0n = 0
    R0n = 0
    GP = 20000
    LP = 1000
    Sc = 500000
    LHS_no_gate = (100 * Sc - 45 * R0n) * 3 * GP
    RHS_no_gate = 100 * R0n * max(0, 6 * GP - 145 * LP)
    print(f"(a) Trường hợp bẫy im lặng R0n = 0, Sc = {Sc}, GP = {GP}, LP = {LP}:")
    print(f"    Nếu KHÔNG có cờ kiểm tra R0n == 0:")
    print(f"        LHS = (100 * {Sc} - 0) * 3 * {GP} = {LHS_no_gate}")
    print(f"        RHS = 100 * 0 * max(...) = {RHS_no_gate}")
    print(f"        LHS > RHS: {LHS_no_gate > RHS_no_gate} => Mạch sẽ phán đoán SAI LẦM là HỮU THANH!")
    print(f"    Do đó, điều kiện tiên quyết 'if (R0 == 0 || LP == 0 || GP == 0) voiced = 0' là bắt buộc tuyệt đối!")

    # (b) Sát ngưỡng 0.4499 và 0.4501 trong vùng phẳng (I >= 0.0414)
    GP_norm = 20000
    LP_norm = 2000  # I = 0.10 >= 0.0414 => ramp = 0, RHS = 0
    R0n_norm = 1000000
    Sc_below = 449900  # Sc / R0n = 0.4499
    Sc_above = 450100  # Sc / R0n = 0.4501

    LHS_below = (100 * Sc_below - 45 * R0n_norm) * 3 * GP_norm
    LHS_above = (100 * Sc_above - 45 * R0n_norm) * 3 * GP_norm
    RHS_flat = 0

    print(f"\n(b) Khảo sát sát ngưỡng trong vùng phẳng (I = {LP_norm/GP_norm:.2f} >= 0.0414):")
    print(f"    RHS = 0")
    print(f"    - Với Sc = {Sc_below} (tương ứng ratio = {Sc_below/R0n_norm:.4f} < 0.45):")
    print(f"        term1 = 100 * {Sc_below} - 45 * {R0n_norm} = {100*Sc_below - 45*R0n_norm}")
    print(f"        LHS = {LHS_below} => LHS > 0: {LHS_below > 0} => Vô thanh (Voiceless)")
    print(f"    - Với Sc = {Sc_above} (tương ứng ratio = {Sc_above/R0n_norm:.4f} > 0.45):")
    print(f"        term1 = 100 * {Sc_above} - 45 * {R0n_norm} = {100*Sc_above - 45*R0n_norm}")
    print(f"        LHS = {LHS_above} => LHS > 0: {LHS_above > 0} => Hữu thanh (Voiced)")
    print(f"    Độ phân giải số nguyên cực kỳ nhạy: bước chênh lệch 100 đơn vị Sc làm đảo chiều dấu của LHS rõ ràng.")
    print("[+] Bài tập 10.4 xác minh thành công.\n")

def main():
    ex10_1()
    ex10_2()
    ex10_3()
    ex10_4()

if __name__ == '__main__':
    main()
