# Thí nghiệm 1.1: Chuỗi Xử lý Âm thanh Trực tuyến (Streaming Audio Pipeline)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_01_streaming_audio_pipeline`
- **Chương liên kết**: Chương 01 — Từ Sóng Âm đến Suy diễn Biên
- **Trạng thái**: ✅ Hoàn thành và vượt qua toàn bộ kiểm thử
- **Mục đích**: Hiện thực hóa và kiểm chứng tính toàn vẹn số học của chuỗi trích xuất đặc trưng âm thanh trực tuyến theo từng khung (sliding ring buffer → STFT → Mel filterbank → Log-Mel).

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
Trong xử lý âm thanh thời gian thực, dữ liệu không thể nạp theo lô lớn mà phải xử lý trượt liên tục theo từng bước nhảy $H$ mẫu ($10\text{ ms}$). Thí nghiệm minh chứng cơ chế đệm vòng lặp và đối chiếu sai số với phương pháp xử lý mẻ truyền thống.

## 3. Mục tiêu Phần cứng
- Host CPU / Python Simulation (sẽ được chuyển đổi thành AXI-Stream Hardware IP Core trên FPGA trong Chương 6).

## 4. Dẫn xuất Toán học & Thuật toán
- Phép biến đổi STFT với độ dài cửa sổ $N=400$, bước nhảy $H=160$, FFT kích thước $512$.
- Ma trận chuyển đổi Mel $M \times (N/2 + 1)$ với $M=80$.
- Hàm nén: $S[m] = \ln(\max(E[m], 10^{-6}))$.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Sóng âm tổng hợp 1 chiều lấy mẫu tại $16\text{ kHz}$ gồm các thành phần đa âm điều hòa ($440\text{ Hz}, 1200\text{ Hz}, 3200\text{ Hz}$).

## 6. Lệnh Thực thi
```bash
python chapter01/exp_01_streaming_audio_pipeline.py
pytest chapter01/test_exp_01.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Sai số tuyệt đối trung bình (MAE) $< 10^{-4}$.
- Tỷ số tín hiệu trên nhiễu lượng tử (SQNR) $> 50\text{ dB}$.

## 8. Phương pháp Đo lường
- So sánh đối chiếu trực tiếp ma trận điểm nổi giữa hàm tính toán streaming và hàm tính toán batch của NumPy.

## 9. Kết quả Thực nghiệm & Bằng chứng
- MAE đạt $0.000000\text{e}+00$ (hoàn toàn trùng khớp).
- SQNR đạt $> 60\text{ dB}$.

## 10. Đánh đổi Phần cứng - Phần mềm
- Xử lý streaming giúp giảm độ trễ từ $1000\text{ ms}$ (chờ cả file) xuống chỉ còn $10\text{ ms}$ (độ trễ 1 khung), với chi phí quản lý đệm trạng thái vòng xoay (ring-buffer state).

## 11. Giới hạn & Giả định
- Hiện tại sử dụng số thực dấu phẩy động 32-bit (FP32). Chương 6 sẽ chuyển đổi sang số dấu phẩy tĩnh (Fixed-Point Q8.8 / Q16.16) để tổng hợp trên phần cứng FPGA.

## 12. Bài học Sư phạm Rút ra
- Hiểu rõ cơ chế cửa sổ trượt và lý do tại sao bộ nhớ đệm trạng thái (stateful buffer) là thành phần cốt lõi trong mọi kiến trúc tăng tốc âm thanh trên phần cứng.

## 13. Nguồn Trích dẫn
- `R01-03`: Gulati et al., *Conformer: Convolution-augmented Transformer for Speech Recognition*, Interspeech 2020.
- `R01-05`: Majumdar et al., *MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network*, Interspeech 2020.
