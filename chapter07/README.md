# Thí nghiệm 7.1: Lượng tử hóa Nhận thức Phần cứng cho Mô hình Thoại (Voice QAT)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_07_voice_qat_calibration`
- **Chương liên kết**: Chương 07 — Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Áp dụng kỹ thuật QAT trên PyTorch/Brevitas để lượng tử hóa mô hình thoại từ FP32 xuống INT8/INT4 và kiểm chứng tỷ lệ suy giảm chất lượng nhận dạng.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Nắm vững quy trình nén mô hình thích ứng phần cứng và hiểu tại sao QAT vượt trội hơn PTQ thuần túy trên miền âm thanh.

## 3. Mục tiêu Phần cứng
- GPU để huấn luyện QAT; mô hình sau đó xuất sang ONNX lượng tử hóa nạp vào FPGA.

## 4. Dẫn xuất Toán học & Thuật toán
- Straight-Through Estimator (STE) và Scale factor calibration.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Bộ dữ liệu SpeechCommands v2 hoặc LibriSpeech test-clean.

## 6. Lệnh Thực thi
```bash
python chapter07/exp_07_voice_qat_calibration/train_qat.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Tỷ lệ suy giảm chính xác $< 0.3\%$ so với bản FP32 gốc.

## 8. Phương pháp Đo lường
- Tính toán ma trận nhầm lẫn (Confusion Matrix) và tỷ lệ nhận diện chính xác Top-1.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ hoàn thành huấn luyện QAT]

## 10. Đánh đổi Phần cứng - Phần mềm
- Huấn luyện QAT tốn thời gian hơn nhưng cứu vãn được tỷ lệ lỗi khi chạy trên phần cứng FPGA INT8/INT4.

## 11. Giới hạn & Giả định
- Giả định hàm phân phối trọng số xấp xỉ phân phối chuẩn (Gaussian).

## 12. Bài học Sư phạm Rút ra
- Không thể mang mô hình FP32 nguyên bản xuống FPGA; nén thích ứng phần cứng là bước sống còn.

## 13. Nguồn Trích dẫn
- `R01-05`: MatchboxNet; `R01-02`: FINN.
