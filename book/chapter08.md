# Chương 8: Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại

> *Mục tiêu: Thiết kế vi kiến trúc phần cứng tối ưu cho các phép toán đặc trưng trong mô hình giọng nói: Depthwise Separable Convolutions, Multi-Head Self-Attention, và xấp xỉ hàm phi tuyến (Softmax, LayerNorm).*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Tích chập Tách biệt Chiều thời gian - Kênh (Depthwise Separable 1D Conv)**: Giảm $K \times C_{\text{in}} \times C_{\text{out}}$ xuống còn $K \times C_{\text{in}} + C_{\text{in}} \times C_{\text{out}}$ phép tính.
> - **Cơ chế Tự chú ý (Scaled Dot-Product Attention)**: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$.
> - **Xấp xỉ hàm Softmax cơ số 2**: $\text{Softmax}(z)_i \approx \frac{2^{z_i - z_{\max}}}{\sum 2^{z_j - z_{\max}}}$.

---

## 8.1 Trực giác: Các Khối Tính toán Khắc nghiệt đối với Phần cứng FPGA
<!-- 
TODO:
- Tích chập chuẩn rất thân thiện với DSP; tuy nhiên hai model đích của sách — MatchboxNet cho KWS và **NVIDIA NeMo streaming Conformer-Transducer `small`** cho ASR (`plan-v2.md` §4.2, chốt 2026-09-12) — dùng Depthwise Separable Convolutions và Self-Attention.
- Whisper KHÔNG thuộc danh sách này, dù nó là câu trả lời nhiều người sẽ đoán: cửa sổ 30 giây không nhân quả là một *lớp model* khác và sẽ phá đường cong accuracy-vs-latency mà chương này dạy. Lý do loại được ghi ở §4.2 để không ai âm thầm đưa nó quay lại.
- Hàm Softmax yêu cầu lũy thừa $e^x$ và phép chia tổng $1/\sum$, rất tốn kém tài nguyên logic nếu không xấp xỉ khéo léo.
-->

## 8.2 Tăng tốc Tích chập 1D Tách biệt Kênh trên FPGA
<!-- 
TODO:
- Kỹ thuật unrolling ma trận bộ lọc thời gian và quản lý trượt cửa sổ nơ-ron (Line Buffer / Shift Register).
- Tận dụng cấu trúc nhân-cộng DSP cascade mà không cần qua routing logic.
-->

## 8.3 Xử lý Cơ chế Attention Trực tuyến (Streaming Chunk-Level Attention)
<!-- 
TODO:
- Giới hạn độ dài ngữ cảnh bằng cửa sổ chú ý cục bộ (Local / Chunk Attention) để cố định kích thước bộ nhớ đệm BRAM.
- Triển khai thuật toán FlashAttention phần cứng rút gọn: tính Softmax theo khối mà không cần lưu toàn bộ ma trận $T \times T$.
-->

## 8.4 Hiện thực hóa Hàm Phi tuyến Softmax và Chuẩn hóa Lớp (LayerNorm)
<!-- 
TODO:
- Kỹ thuật đổi cơ số tự nhiên $e$ sang cơ số $2$ để thay phép nhân lũy thừa bằng phép dịch bit phần cứng.
- Tính toán căn bậc hai nghịch đảo ($1/\sqrt{\sigma^2 + \epsilon}$) trong LayerNorm bằng thuật toán Fast Inverse Square Root hoặc Newton-Raphson.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter08/`](../chapter08/).
