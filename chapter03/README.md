# Thí nghiệm 3.1: Định lượng Điểm nghẽn Xử lý Luồng trên GPU (GPU Streaming Bottleneck)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_03_batch_one_gpu_bottleneck`
- **Chương liên kết**: Chương 03 — Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Đo đạc độ chiếm dụng nhân SM (SM Occupancy), thời gian trễ do phát lệnh gọi nhân (Kernel Launch Overhead) và độ trễ đuôi (Tail Latency P99) trên Jetson Orin khi kích thước lô bằng một ($batch=1$).

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Cung cấp bằng chứng định lượng về sự suy giảm hiệu suất và lãng phí năng lượng của kiến trúc SIMT GPU khi không thể gom lô dữ liệu âm thanh.

## 3. Mục tiêu Phần cứng
- NVIDIA Jetson Orin (Nano / NX).

## 4. Dẫn xuất Toán học & Thuật toán
- Phân tích mô hình Roofline: Tính toán cường độ số học (Arithmetic Intensity = FLOPs / Memory Byte).

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- 10,000 khung âm thanh kích thước $1 \times 80$ Mel features đưa vào tuần tự cách nhau $10\text{ ms}$.

## 6. Lệnh Thực thi
```bash
python chapter03/exp_03_batch_one_gpu_bottleneck/run.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- SM Occupancy $< 20\%$.
- Kernel launch overhead chiếm $> 30\%$ tổng thời gian trễ.

## 8. Phương pháp Đo lường
- NVIDIA Nsight Systems (`nsys profile`) và NVIDIA Nsight Compute (`ncu`).

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ ghi nhận từ thiết bị thực tế]

## 10. Đánh đổi Phần cứng - Phần mềm
- GPU linh hoạt cho nhiều bài toán nhưng lãng phí điện năng khi chạy các tác vụ luồng kích thước nhỏ.

## 11. Giới hạn & Giả định
- Đo kiểm tại các chế độ nguồn 7W, 15W, 25W (`nvpmodel`).

## 12. Bài học Sư phạm Rút ra
- Hiểu rõ ranh giới giữa Memory-Bound và Compute-Bound trong xử lý âm thanh tại biên.

## 13. Nguồn Trích dẫn
- `R01-01`: NVIDIA Jetson Orin Architecture Whitepaper.
