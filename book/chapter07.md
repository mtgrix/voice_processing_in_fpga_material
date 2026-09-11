# Chương 7: Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại

> *Mục tiêu: Nắm vững lý thuyết lượng tử hóa thích ứng phần cứng (Hardware-Aware Quantization), kỹ thuật PTQ và QAT (INT8, INT4, Non-uniform) nhằm bảo toàn tỷ lệ lỗi từ (WER) và chất lượng thoại (PESQ).*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Lượng tử hóa Đối xứng Đồng nhất (Uniform Symmetric Quantization)**: $q = \text{clamp}(\lfloor x/S \rceil, -2^{b-1}, 2^{b-1}-1)$.
> - **Khoảng cách Kullback-Leibler (KL Divergence)**: Đo lường sự mất mát phân phối thông tin khi cắt cụt dải động (clipping threshold).
> - **Straight-Through Estimator (STE)**: Kỹ thuật xấp xỉ đạo hàm của hàm bậc thang lượng tử hóa trong quá trình lan truyền ngược.

---

## 7.1 Trực giác: Sự Nhạy cảm Đặc thù của Mô hình Âm thanh với Lượng tử hóa
<!-- 
TODO:
- Khác với thị giác máy tính (ảnh có thể chịu được lượng tử hóa thô), âm thanh chứa các sóng hài năng lượng nhỏ nhưng mang thông tin ngữ âm quyết định (ví dụ các âm xát, phụ âm vô thanh).
- Sai số lượng tử hóa có thể biến đổi ngữ âm gây tăng vọt WER hoặc méo tiếng trong lọc nhiễu.
-->

## 7.2 Lượng tử hóa Sau Huấn luyện (PTQ — Post-Training Quantization)
<!-- 
TODO:
- Phương pháp hiệu chỉnh Calibrator: MinMax, Entropy (KL-Divergence), Percentile.
- Phân tích ranh giới giới hạn khi áp dụng PTQ trực tiếp cho mô hình ASR.
-->

## 7.3 Huấn luyện Nhận thức Lượng tử hóa (QAT — Quantization-Aware Training)
<!-- 
TODO:
- Cơ chế chèn nốt giả lượng tử (FakeQuantize) trong PyTorch/Brevitas.
- Huấn luyện với STE để trọng số thích nghi dần với lưới số nguyên.
- Kết quả thực nghiệm: Hạ từ FP32 xuống INT8/INT4 mà không suy hao chất lượng.
-->

## 7.4 Lượng tử hóa Hỗn hợp Chính xác (Mixed-Precision Quantization)
<!-- 
TODO:
- Xác định tầng nhạy cảm: giữ FP16 hoặc INT8 cho tầng Attention Softmax, ép INT4 cho các tầng tích chập trung gian.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter07/`](../chapter07/).
