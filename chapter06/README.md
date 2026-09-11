# Thí nghiệm 6.1: Bộ Tiền Xử lý STFT/Mel Dấu phẩy Tĩnh trên Phần cứng (Hardware Fixed-Point FFT/Mel)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_06_hardware_fixed_point_fft`
- **Chương liên kết**: Chương 06 — Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Hiện thực hóa và kiểm tra độ chính xác của lõi phần cứng FFT/Mel sử dụng số dấu phẩy tĩnh (Fixed-Point Q8.8 hoặc Q16.16) so với chuẩn tham chiếu FP32.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Nắm vững kỹ thuật chuyển đổi từ giải thuật toán học liên tục sang phần cứng số dấu phẩy tĩnh mà không gây tràn số hay méo phổ.

## 3. Mục tiêu Phần cứng
- Vivado HLS / SystemVerilog RTL mô phỏng trên Vivado XSIM.

## 4. Dẫn xuất Toán học & Thuật toán
- Thuật toán Radix-2 FFT và ma trận chuyển đổi Mel dấu phẩy tĩnh.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Tín hiệu âm thanh 16-bit PCM lấy mẫu tại 16 kHz.

## 6. Lệnh Thực thi
```bash
python chapter06/exp_06_hardware_fixed_point_fft/sim.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Tỷ số tín hiệu trên nhiễu lượng tử SQNR $> 45\text{ dB}$.

## 8. Phương pháp Đo lường
- So sánh từng mẫu đầu ra của mô phỏng C++/RTL với NumPy/Librosa FP32.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ mô phỏng HLS C-Cosimulation]

## 10. Đánh đổi Phần cứng - Phần mềm
- Giảm số bit giúp tiết kiệm DSP và BRAM nhưng làm giảm SQNR.

## 11. Giới hạn & Giả định
- Kích thước FFT cố định $512$ điểm.

## 12. Bài học Sư phạm Rút ra
- Hiểu sâu sắc cách kiểm soát dải động và dịch bit (scaling) trong các thuật toán xử lý tín hiệu số phần cứng.

## 13. Nguồn Trích dẫn
- `R01-03`, `R01-05` trong `docs/SOURCES.md`.
