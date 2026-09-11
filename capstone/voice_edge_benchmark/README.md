# Capstone: Voice Edge AI Benchmark Suite (Jetson Orin vs. FPGA)

## 1. Tổng quan & Mục tiêu Học thuật
Đây là hệ thống đánh giá thực nghiệm trung tâm (central benchmark harness) của toàn bộ dự án. Mục đích chính là cung cấp bảng số liệu thực nghiệm toàn diện phục vụ việc viết bài báo khoa học (research paper) so sánh trực diện giữa:
- **NVIDIA Jetson Orin** (chạy TensorRT FP16 và INT8)
- **AMD Xilinx Kria KV260 / FPGA Kit** (chạy Vitis AI DPU và FINN Streaming Dataflow)

## 2. Các Trục Đo lường Pareto Frontier
Bảng đánh giá trích xuất 6 chiều không gian tối ưu:
1. **Độ trễ trung bình (Mean Latency)** và **Độ trễ cực đoan (P99 Tail Latency)** tính bằng mili-giây.
2. **Hệ số Thời gian Thực (RTF — Real-Time Factor)**: $\text{RTF} = \text{Latency} / 10\text{ ms}$.
3. **Công suất thực tế (Active Board Power)** đo bằng Watts.
4. **Năng lượng trên từng khung (Energy per Frame)** đo bằng $\text{mJ/frame}$.
5. **Độ chính xác âm học**: Word Error Rate (WER) hoặc Accuracy (%).
6. **Hiệu suất năng lượng**: $\text{frames/sec/Watt}$.

## 3. Lệnh Thực thi & Xuất Bảng
```bash
python capstone/voice_edge_benchmark/benchmark_runner.py
```
