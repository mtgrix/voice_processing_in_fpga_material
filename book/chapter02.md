# Chương 2: Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin

> *Mục tiêu: Giải phẫu kiến trúc SoC NVIDIA Jetson Orin (Ampere GPU, Tensor Cores, bộ nhớ LPDDR5, DLA), thiết lập phương pháp đo đạc độ trễ và công suất chuẩn mực (TensorRT, tegrastats) làm đường cơ sở (baseline) so sánh.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Năng lượng trên khung (Energy per Frame)**: $E_{\text{frame}} = P_{\text{avg}} \times \Delta t_{\text{latency}}$ ($\text{Joules}$ hoặc $\text{mJ}$).
> - **Hệ số Thời gian Thực (Real-Time Factor — RTF)**: $\text{RTF} = T_{\text{compute}} / T_{\text{audio}}$.
> - **Độ trễ cực đoan (Tail Latency P99)**: Phân vị 99% thời gian xử lý qua hàng ngàn khung liên tiếp.

---

## 2.1 Trực giác: Sức mạnh và Nghịch lý của NVIDIA Jetson Orin
<!-- 
TODO (Nội dung cần viết):
- Khả năng xử lý FP16/INT8 TOPS cực cao của Orin trên thị giác máy tính.
- Nghịch lý khi chạy mô hình giọng nói: GPU compute utilization rớt xuống <15%, công suất tĩnh SoC cao.
-->

## 2.2 Vi Kiến trúc SoC Jetson Orin: Từ Lõi ARM đến Ampere Tensor Cores
<!-- 
TODO (Nội dung cần viết):
- Sơ đồ khối SoC: ARM Cortex-A78AE, Ampere SM, DLA 2.0, Unified Memory Bus LPDDR5 128-bit.
- Nguyên lý thực thi SIMT (Warp 32 luồng) và kích thước khối ma trận (tile size) tối thiểu của Tensor Cores.
- Tại sao xử lý âm thanh batch=1 chuyển đổi bài toán từ GEMM (compute-bound) sang GEMV (memory-bandwidth bound).
-->

## 2.3 Phương pháp Luận Đo kiểm: TensorRT và Cảm biến Phần cứng `tegrastats`
<!-- 
TODO (Nội dung cần viết):
- Tối ưu hóa mô hình với NVIDIA TensorRT (FP16 và INT8 calibration).
- Cách đọc chính xác các kênh cảm biến dòng/áp INA3221 qua `tegrastats`: VDD_GPU_SOC, VDD_CPU_CV, VIN_SYS_5V0.
- Cách thiết lập profiling P50, P90, P99 để phát hiện hiện tượng jitter.
-->

## 2.4 Bảng Chỉ số Điểm chuẩn Cơ sở (The Baseline Scorecard)
<!-- 
TODO (Nội dung cần viết):
- Xây dựng bảng chuẩn: Độ trễ (ms), RTF, Công suất (W), Năng lượng (mJ/frame), Tỷ lệ lỗi (WER/PESQ).
-->

---

## Thực nghiệm Liên kết (Hands-on Experiment)
- Xem mã nguồn đo kiểm tại [`chapter02/`](../chapter02/).

## Tài liệu Tham khảo
- Tham chiếu nguồn: `R01-01` (NVIDIA Jetson Orin Whitepaper) trong [`docs/SOURCES.md`](../docs/SOURCES.md).
