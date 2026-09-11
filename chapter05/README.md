# Thí nghiệm 5.1: Đối sánh Phương pháp Tăng tốc: DPU vs. FINN Dataflow

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_05_dpu_vs_finn_benchmark`
- **Chương liên kết**: Chương 05 — So sánh Các Phương pháp luận Tăng tốc trên FPGA
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Đo đạc độ trễ và mức tiêu thụ công suất thực tế giữa kiến trúc Vitis AI DPU (Overlay dựa trên tập lệnh) và FINN (Luồng dữ liệu Dataflow chuyên dụng).

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Cung cấp cái nhìn thực chứng về điểm mạnh và hạn chế của từng phương pháp tiếp cận khi tăng tốc mô hình xử lý thoại trên FPGA.

## 3. Mục tiêu Phần cứng
- AMD Xilinx Kria KV260 Starter Kit.

## 4. Dẫn xuất Toán học & Thuật toán
- So sánh chu kỳ khởi tạo ($II$) và độ trễ từ đầu vào đến đầu ra (latency cycles).

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Tập dữ liệu Google Speech Commands v2 (12 nhãn từ khóa đánh thức).

## 6. Lệnh Thực thi
```bash
python chapter05/exp_05_dpu_vs_finn_benchmark/compare.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- FINN Dataflow đạt độ trễ $< 1\text{ ms}$; DPU đạt độ trễ $< 2\text{ ms}$.

## 8. Phương pháp Đo lường
- Đồng hồ bấm giờ phần cứng AXI Timer trên Programmable Logic.

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ thực nghiệm trên bo mạch Kria KV260]

## 10. Đánh đổi Phần cứng - Phần mềm
- DPU dễ biên dịch từ ONNX nhưng độ trễ cao hơn; FINN cần lượng tử hóa sâu nhưng cho hiệu năng tối ưu nhất.

## 11. Giới hạn & Giả định
- FINN áp dụng cho mô hình INT4/INT8; DPU áp dụng cho INT8 chuẩn.

## 12. Bài học Sư phạm Rút ra
- Không có công cụ vạn năng; lựa chọn công cụ phụ thuộc vào yêu cầu độ trễ và thời gian phát triển dự án.

## 13. Nguồn Trích dẫn
- `R01-02`: FINN: A Framework for Fast, Scalable Binarized Neural Networks on FPGAs.
