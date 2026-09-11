# Thí nghiệm 9.1: Luồng Dữ liệu DMA & Tích hợp SoC PYNQ (PYNQ DMA Audio Streaming)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_09_pynq_dma_audio_streaming`
- **Chương liên kết**: Chương 09 — Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng / Phần mềm
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Hiện thực hóa luồng truyền nhận dữ liệu âm thanh thời gian thực giữa CPU ARM và FPGA fabric qua giao diện AXI DMA sử dụng thư viện PYNQ trên Petalinux.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Nắm vững cơ chế đồng thiết kế phần cứng/phần mềm trên nền tảng Zynq MPSoC, kiểm soát độ trễ giao tiếp CPU-FPGA.

## 3. Mục tiêu Phần cứng
- AMD Xilinx Kria KV260 (chạy Petalinux 2022.2/2023.1 + PYNQ).

## 4. Dẫn xuất Toán học & Thuật toán
- Phân tích độ trễ DMA: $T_{\text{DMA}} = T_{\text{setup}} + \frac{\text{Bytes}}{\text{Bandwidth}}$.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Dòng âm thanh liên tục lấy mẫu 16 kHz từ cổng microphone hoặc tệp WAV.

## 6. Lệnh Thực thi
```bash
python chapter09/exp_09_pynq_dma_audio_streaming/pynq_runner.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Thời gian trễ truyền nhận DMA $< 50\mu\text{s}$ cho mỗi khung 10ms.

## 8. Phương pháp Đo lường
- Đo thời gian Python `time.perf_counter_ns()` và bộ đếm AXI Timer phần cứng.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ nạp bitstream lên bo mạch Kria KV260]

## 10. Đánh đổi Phần cứng - Phần mềm
- Sử dụng DMA Zero-Copy giúp CPU rảnh tay cho các tác vụ giải mã CTC và kết nối mạng.

## 11. Giới hạn & Giả định
- Yêu cầu cấu hình đúng Clock Domain Crossing (CDC) giữa bus CPU và logic PL.

## 12. Bài học Sư phạm Rút ra
- Phần cứng chỉ phát huy tối đa sức mạnh khi lớp giao tiếp phần mềm và trình điều khiển (driver) được tối ưu hóa mượt mà.

## 13. Nguồn Trích dẫn
- `R01-04`: AMD Xilinx Kria KV260 User Guide.
