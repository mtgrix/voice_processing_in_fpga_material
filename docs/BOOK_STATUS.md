# Tiến độ Soạn thảo & Nghiên cứu — Voice Edge AI (Book Status)

> **Theo dõi tiến độ 10 chương chuyên khảo và các mục của bài báo khoa học.**
> Cập nhật lần cuối: 2026-09-11

---

## 1. Bảng Trạng thái 10 Chương

| Chương | Tên Chương | Bản thảo Tiếng Việt | Bản thảo Tiếng Anh | Thí nghiệm | Trạng thái |
|:---:|---|:---:|:---:|:---:|:---:|
| **01** | Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_01 | Đã tạo khung |
| **02** | Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_02 | Đã tạo khung |
| **03** | Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_03 | Đã tạo khung |
| **04** | Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_04 | Đã tạo khung |
| **05** | So sánh Các Phương pháp luận Tăng tốc trên FPGA: DPU, HLS, FINN & RTL | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_05 | Đã tạo khung |
| **06** | Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_06 | Đã tạo khung |
| **07** | Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_07 | Đã tạo khung |
| **08** | Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_08 | Đã tạo khung |
| **09** | Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng / Phần mềm | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_09 | Đã tạo khung |
| **10** | Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo Khoa học | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_10 | Đã tạo khung |

---

## 2. Kế hoạch Bài báo Khoa học (Paper Roadmap)

- **Mục tiêu Hội nghị / Tạp chí**: IEEE/ACM FCCM, FPGA, ICASSP, Interspeech, hoặc IEEE ESL.
- **Tiêu đề Dự kiến**: *Spatial Dataflow vs. SIMT for Continuous Edge Voice AI: A Comprehensive Pareto Analysis from Jetson Orin to FPGA*.
- **Đóng góp Dự kiến**:
  1. Phân tích định lượng sâu sắc về hiện tượng suy giảm hiệu suất SIMT khi xử lý âm thanh luồng ($batch=1$).
  2. Kiến trúc luồng dữ liệu tùy biến trên FPGA tích hợp trực tiếp tầng tiền xử lý I2S/STFT và tầng nơ-ron.
  3. Đo kiểm thực nghiệm Pareto Frontier: Đối sánh đa chiều giữa TensorRT (FP16/INT8) trên Orin và FPGA overlay.
