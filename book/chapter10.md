# Chương 10: Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo Khoa học

> *Mục tiêu: Xây dựng phương pháp luận đo kiểm thực nghiệm công bằng giữa NVIDIA Jetson Orin và FPGA Kit, phân tích không gian đánh đổi đa mục tiêu Pareto Frontier, và đóng gói thành công trình bài báo khoa học hoàn chỉnh.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Biên tối ưu Pareto (Pareto Frontier)**: Tập hợp các điểm thiết kế mà không thể cải thiện bất kỳ chỉ số nào (ví dụ độ trễ) mà không làm suy giảm chỉ số khác (năng lượng hoặc độ chính xác).
> - **Energy-Delay Product (EDP)**: $\text{EDP} = \text{Energy} \times \text{Delay}$ ($\text{J}\cdot\text{s}$), chỉ số đánh giá toàn diện tốc độ và độ tiết kiệm điện.
> - **Tỷ lệ Lỗi Từ (Word Error Rate — WER)**: $\text{WER} = \frac{S + D + I}{N} \times 100\%$.

---

## 10.1 Trực giác: Thế nào là một Bài So sánh Phần cứng Thuyết phục Học thuật?
<!-- 
TODO:
- Tránh bẫy so sánh khập khiễng: Không so sánh mô hình FP32 chưa tối ưu trên GPU với mô hình INT4 tối ưu trên FPGA.
- Nguyên tắc so sánh công bằng: Cùng công suất nhiệt (TDP matched), cùng điều kiện đầu vào luồng, GPU chạy TensorRT bản mới nhất, FPGA chạy bản tối ưu tương đương.
-->

## 10.2 Ma trận Chỉ số Đo lường Đa chiều (Multi-Dimensional Metric Matrix)
<!-- 
TODO:
- Trục 1: Chất lượng âm học (WER, CER, PESQ, STOI).
- Trục 2: Thời gian đáp ứng (Mean Latency, P90, P99 Tail Latency, RTF, Jitter).
- Trục 3: Năng lượng (Active Power W, Energy per Frame mJ, TOPS/W, EDP).
- Trục 4: Chi phí phần cứng (BOM cost, Silicon Area, LUT/DSP/BRAM utilization).
-->

## 10.3 Vẽ Đồ thị và Phân tích Biên Tối ưu Pareto Frontier
<!-- 
TODO:
- Dựng biểu đồ Pareto 2D và 3D: Trục X (Latency), Trục Y (Energy per Frame), Kích thước điểm (Tỷ lệ lỗi WER/PESQ).
- Xác định rõ vùng ưu thế áp đảo của FPGA (vùng thời gian thực streaming dưới 10ms, công suất dưới 5W).
-->

## 10.4 Cấu trúc Bài báo Khoa học Chuẩn IEEE/ACM
<!-- 
TODO:
- Cách viết Abstract cô đọng, nêu bật đóng góp định lượng (Speedup X lần, Tiết kiệm năng lượng Y lần).
- Viết phần Introduction, Related Work, Proposed Architecture, Experimental Evaluation, và Conclusion.
- Lựa chọn hội nghị phù hợp (FCCM, FPGA, FPT, ICASSP, Interspeech, ESL).
-->

---

## Thực nghiệm Liên kết (Capstone Benchmark)
- Xem toàn bộ kịch bản đo kiểm tại [`capstone/voice_edge_benchmark/`](../capstone/voice_edge_benchmark/).
