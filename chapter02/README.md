# Thí nghiệm 2.1: Bộ Đo lường & Phân tích Hiệu năng Jetson Orin (Jetson Orin Profiler)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_02_jetson_orin_profiler`
- **Chương liên kết**: Chương 02 — Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Xây dựng công cụ phân tích phân phối độ trễ (latency distribution), độ biến thiên (jitter), hệ số thời gian thực (RTF) và mức tiêu thụ năng lượng trên từng khung âm thanh dựa trên dữ liệu nhật ký của TensorRT và `tegrastats`.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
Để chứng minh đóng góp khoa học trong bài báo, việc so sánh không thể chỉ dừng lại ở thời gian trung bình (mean time). Thí nghiệm này chuẩn hóa phương pháp thu thập và tính toán các phân vị độ trễ P50, P90, P99 và chỉ số năng lượng chính xác ($\text{mJ/frame}$).

## 3. Mục tiêu Phần cứng
- NVIDIA Jetson Orin Nano / Orin NX (Bộ giả lập mô hình hóa thông số kỹ thuật thực tế).

## 4. Dẫn xuất Toán học & Thuật toán
- $\text{RTF} = \frac{\Delta t_{\text{latency}}}{T_{\text{frame\_duration}}}$
- $E_{\text{frame}} = P_{\text{board}} \times \Delta t_{\text{latency}}$
- $\text{Efficiency} = \frac{1}{\Delta t_{\text{latency}} \times P_{\text{board}}}$ ($\text{frames/s/Watt}$).

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Dữ liệu vết đo độ trễ liên tục từ TensorRT kết hợp với nhật ký công suất từ cảm biến INA3221 (`tegrastats`).

## 6. Lệnh Thực thi
```bash
python chapter02/exp_02_jetson_orin_profiler.py
pytest chapter02/test_exp_02.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- $\text{RTF} < 0.5$ (đạt yêu cầu thời gian thực).
- Độ trễ P99 $> \text{P50}$.

## 8. Phương pháp Đo lường
- Đọc vết đo điện áp và dòng điện từ cảm biến INA3221 kết hợp với bộ đếm thời gian phân giải micro-giây (`cudaEvent_t`).

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ nạp dữ liệu log thực tế từ kit Jetson Orin]

## 10. Đánh đổi Phần cứng - Phần mềm
- Jetson Orin đạt thông lượng tốt nhưng công suất tĩnh cao ($>5\text{W}$), dẫn đến năng lượng tiêu thụ trên từng khung âm thanh cao hơn đáng kể so với kiến trúc FPGA chuyên dụng.

## 11. Giới hạn & Giả định
- Dữ liệu thô cần được xuất từ thiết bị vật lý qua lệnh `tegrastats --interval 10 --logfile tegrastats.log`.

## 12. Bài học Sư phạm Rút ra
- Hiểu rõ tại sao độ trễ cực đoan P99 quan trọng hơn độ trễ trung bình trong các hệ thống âm thanh trực tuyến để tránh rớt khung tiếng (audio dropouts).

## 13. Nguồn Trích dẫn
- `R01-01`: NVIDIA Corporation, *Jetson AGX Orin Architecture Whitepaper*, 2022.
- `R01-04`: AMD Xilinx, *Kria KV260 Vision AI Starter Kit User Guide*, 2023.
