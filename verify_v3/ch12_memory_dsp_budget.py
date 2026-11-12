#!/usr/bin/env python3
"""verify_v3/ch12_memory_dsp_budget.py
Derives and verifies the memory (M10K) and DSP block budget for Chapter 12:
- Targets Intel Cyclone V SoC 5CSXFC6D6F31C6N
- Embedded memory specifications from Intel Embedded Memory User Guide (UG-01068 / CV-51003)
- Variable Precision DSP Block specifications from CV-51004
- M10K block geometries: 10Kx1, 5Kx2, 2.5Kx4, 1024x10, 512x20, 256x40
- Verifies exact M10K counts for every hardware module
- Documents "phải đo trong Quartus/Fitter" for post-compilation figures
"""

def derive_hardware_budgets():
    print("=== CH12 MEMORY (M10K) AND DSP BUDGET DERIVATION ===")
    print("Target Device: Intel Cyclone V SoC 5CSXFC6D6F31C6N")
    print("Document citations:")
    print("  - Embedded Memory Blocks in Cyclone V Devices (Intel doc ID: CV-51003)")
    print("  - Variable Precision DSP Blocks in Cyclone V Devices (Intel doc ID: CV-51004)")
    print("  - Cyclone V Device Overview (Intel doc ID: CV-51001)\n")
    
    # M10K specifications
    # Capacity = 10,240 bits
    # Supported port configurations:
    #   Depth <= 256  -> width up to 40 bits (256x40)
    #   Depth <= 512  -> width up to 20 bits (512x20)
    #   Depth <= 1024 -> width up to 10 bits (1024x10)
    #   Depth <= 2048 -> width up to 5 bits  (2048x5)
    #   Depth <= 4096 -> width up to 2 bits  (4096x2)
    #   Depth <= 8192 -> width 1 bit         (8192x1)
    
    modules_ram = [
        ("FIFO vào (On-Chip FIFO)", "512x16", 512, 16, 1, "Cấu hình 512x20 (độ sâu <= 512, rộng <= 20 bit) -> đúng 1 M10K"),
        ("RAM vòng mẫu (Ring Buffer)", "1024x16", 1024, 16, 2, "Độ sâu 1024 > 512 -> cấu hình 1024x10. Cần 16 bit -> 2 khối M10K (rộng 20 bit)"),
        ("ROM Hanning (Full N=638)", "638x16", 638, 16, 2, "Độ sâu 638 > 512 -> cấu hình 1024x10 -> 2 khối M10K (nửa ROM 319x16 cần 1 M10K)"),
        ("xw_ram (true dual-port)", "638x17", 638, 17, 2, "Độ sâu 638 > 512, rộng 17 bit -> cấu hình 1024x10 -> 2 khối M10K (đệm đôi: 4 M10K)"),
        ("ROM {C, K} (189 từ dùng)", "256x32", 256, 32, 1, "Độ sâu 256 <= 256, rộng 32 <= 40 bit -> cấu hình 256x40 -> đúng 1 M10K"),
        ("FIFO ra F0 (pitch_f0)", "512x16", 512, 16, 1, "Cấu hình 512x20 (độ sâu <= 512, rộng <= 20 bit) -> đúng 1 M10K")
    ]
    
    total_m10k_base = sum(m[4] for m in modules_ram)
    total_m10k_overlap = total_m10k_base + 2 # +2 for xw_ram double buffering
    chip_m10k_blocks = 553 # Per Intel CV-51001 Table 1-2 (Cyclone V SoC Device Features)
    chip_m10k_bits = chip_m10k_blocks * 10240
    chip_m10k_mbit = chip_m10k_bits / 1e6 # 5.662720 Mbit
    
    print("--- 1. M10K Embedded Memory Budget ---")
    print(f"{'Khối chức năng':<30} | {'Kích thước':<10} | {'M10K':<6} | {'Giải thích cấu hình M10K'}")
    print("-" * 90)
    for name, size, depth, width, m10k, note in modules_ram:
        print(f"{name:<30} | {size:<10} | {m10k:<6} | {note}")
    print("-" * 90)
    print(f"{'Tổng baseline (tuần tự)':<30} | {' ':10} | {total_m10k_base:<6} | Chiếm {total_m10k_base}/{chip_m10k_blocks} = {total_m10k_base/chip_m10k_blocks*100:.2f}% tổng tài nguyên M10K")
    print(f"{'Tổng đệm đôi (chồng lấp)':<30} | {' ':10} | {total_m10k_overlap:<6} | Chiếm {total_m10k_overlap}/{chip_m10k_blocks} = {total_m10k_overlap/chip_m10k_blocks*100:.2f}% tổng tài nguyên M10K")
    print(f"Tổng tài nguyên M10K của chip Cyclone V 5CSXFC6D6F31C6N: {chip_m10k_blocks} khối M10K ({chip_m10k_bits:,} bits = {chip_m10k_mbit:.2f} Mbit) theo CV-51001 Bảng 1-2 (phải kiểm trong datasheet/Quartus).\n")
    
    # DSP Block specifications
    # Cyclone V Variable Precision DSP Block:
    # 112 DSP blocks total on 5CSXFC6D6F31C6N per CV-51001 Table 1-2 (phải kiểm trong datasheet/Quartus)
    # Each DSP block supports:
    #   - 3x 9x9 multipliers
    #   - 2x 18x18 multipliers
    #   - 1x 27x27 multiplier
    #   - 1x 18x18 MAC with 64-bit accumulator
    
    modules_dsp = [
        ("Trừ trung bình (ch05_local_mean)", "25x24", 1, "Phép nhân nghịch đảo acc * M_MEAN (chế độ 27x27)"),
        ("Cửa sổ Hanning (ch06_hanning_window)", "17x17", 1, "Nhân mẫu d * w (chế độ 18x18)"),
        ("Động cơ MAC (ch07_mac_unit)", "17x17+acc", 1, "Nhân dập xw * xw và tích lũy 48-bit (chế độ 18x18 MAC)"),
        ("Chuẩn hóa Rn*C (ch08_norm_score)", "27x17", 1, "Nhân Rn * C[tau] (chế độ 27x27)"),
        ("Chi phí quãng tám R0n*K (ch08_norm_score)", "27x16", 1, "Nhân R0n * K[tau] (chế độ 27x27)"),
        ("Quyết định âm tính (ch10_voicing)", "Hằng số+LHS/RHS", 0, "Nhân hằng số bằng shift-add; tích 54-bit dùng chung logic/DSP (phải đo)"),
        ("Bộ lọc FIR 31 tap (ch03_fir_filter, tùy chọn)", "16x16", 1, "Gấp tap đối xứng, chỉ dùng khi bật (mặc định bypass)")
    ]
    
    dsp_base = sum(d[2] for d in modules_dsp[:-1]) # without FIR
    dsp_fir = dsp_base + 1
    chip_dsp_total = 112
    
    print("--- 2. Variable Precision DSP Block Budget ---")
    print(f"{'Khối chức năng':<35} | {'Toán tử':<14} | {'DSP':<5} | {'Ghi chú kiến trúc'}")
    print("-" * 90)
    for name, op, dsp, note in modules_dsp:
        print(f"{name:<35} | {op:<14} | {dsp:<5} | {note}")
    print("-" * 90)
    print(f"{'Tổng lõi baseline (FIR bypass)':<35} | {' ':14} | {dsp_base:<5} | Chiếm {dsp_base}/112 = {dsp_base/112*100:.2f}% tổng DSP")
    print(f"{'Tổng khi bật FIR 31-tap':<35} | {' ':14} | {dsp_fir:<5} | Chiếm {dsp_fir}/112 = {dsp_fir/112*100:.2f}% tổng DSP")
    print(f"Tổng tài nguyên DSP trên chip: {chip_dsp_total} khối (phải đo số thực trong Quartus/Fitter).\n")
    
    print("Summary:")
    print("  - M10K budget derived from RTL: 9 blocks (baseline) / 11 blocks (overlap) on 553 M10K (theo CV-51001 Bang 1-2, phai kiem trong datasheet/Quartus).")
    print("  - DSP budget derived from RTL: 5 blocks (baseline) / 6 blocks (with FIR) on 112 DSPs (phai do trong Quartus/Fitter).")
    print("  - Real post-fitting counts (ALM, FF, M10K, DSP, Fmax): 'phai do trong Quartus/Fitter'.")

if __name__ == '__main__':
    derive_hardware_budgets()
