# Thí nghiệm 8.1: Tăng tốc Phần cứng cho Attention và Softmax (Voice Attention Accelerator)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_08_voice_attention_accelerator`
- **Chương liên kết**: Chương 08 — Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Hiện thực hóa bộ tăng tốc phần cứng cho cơ chế Attention rút gọn và xấp xỉ hàm Softmax cơ số 2 trên FPGA.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Giải quyết bài toán tính toán phi tuyến tính tốn tài nguyên nhất trong các mô hình ASR hiện đại (Conformer/Transformer).

## 3. Mục tiêu Phần cứng
- AMD Xilinx Kria KV260 Starter Kit.

## 4. Dẫn xuất Toán học & Thuật toán
- $\text{Softmax}(z)_i \approx 2^{z_i - z_{\max}} / \sum 2^{z_j - z_{\max}}$.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Ma trận $Q, K, V$ kích thước $T \times d_k$ với $T=64, d_k=64$.

## 6. Lệnh Thực thi
```bash
python chapter08/exp_08_voice_attention_accelerator/run_hls.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Sai số đầu ra Softmax so với PyTorch FP32 $< 1\%$.

## 8. Phương pháp Đo lường
- HLS C/RTL Cosimulation waveform.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ hoàn thành mô phỏng]

## 10. Đánh đổi Phần cứng - Phần mềm
- Xấp xỉ hàm lũy thừa cơ số 2 tiết kiệm hàng ngàn LUTs so với tính hàm $e^x$ dấu phẩy động.

## 11. Giới hạn & Giả định
- Áp dụng cho mô hình cơ chế Attention phân khối (Chunk/Local Attention).

## 12. Bài học Sư phạm Rút ra
- Kỹ thuật biến đổi toán học tương đương là chìa khóa để triển khai các mô hình AI hiện đại lên phần cứng chuyên dụng.

## 13. Nguồn Trích dẫn
- `R01-03`: Conformer Interspeech 2020.
