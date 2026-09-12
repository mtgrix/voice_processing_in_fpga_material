# Tiến độ Soạn thảo & Nghiên cứu — Voice Edge AI (Book Status)

> **Theo dõi tiến độ 10 chương chuyên khảo và các mục của bài báo khoa học.**
> Cập nhật lần cuối: 2026-09-13

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

## 1.1 Trạng thái nội dung: khung sườn ĐÃ được sửa cho đúng đề cương

Hai trạng thái khác nhau phải phân biệt rõ: chương **chưa viết** (các khối `TODO (Nội dung cần viết)`) và chương **đã viết sai đề cương**. Từ 2026-09-13, nhóm lỗi thứ hai đã được xử lý:

- `book/TOC.md` giờ là xương sống 10 chương chiếu từ `plan-v2.md` §7 và đã được track. Trước đó nó là bản 5 chương thừa hưởng từ `plan.md`, và `tests/test_plan_consistency.py` phải để nó ở dạng xfail.
- Số liệu nhớ on-chip ở Chương 04 đã thay bằng giá trị có trang datasheet (`V-01-11`); "4.5 MB" là số của `plan.md`.
- Whisper đã bị rút khỏi Chương 08; model đích là NeMo streaming Conformer-Transducer `small`.
- WER không còn là metric toàn dụng ở Chương 02, 07, 10 và ở `docs/BOOK_PEDAGOGY.md` (§5.3 cấm dùng lẫn).
- Chương 05 thôi tuyên bố FINN/HLS là "vũ khí tối thượng"; gate chặng 5 đòi log tổng hợp thật.
- Chương 06 dạy rõ đường âm thanh vào PL qua carrier, vì KV260 không có mic.

**Chưa chốt, cần chủ repo:** `plan-v2.md` §7 gán artefact chặng 8–9 (KWS SoC trên board; Conformer overlay) khác với tiêu đề chương 08–09 hiện tại. Ghi chi tiết ở `book/TOC.md`, mục "Lệch ánh xạ chưa chốt".

**Chưa làm:** toàn bộ văn xuôi của 10 chương, và bản tiếng Anh tương ứng. Không một ô số liệu nào trong bảng chương được đóng dấu hoàn thành — không có phần cứng để đo.

---

## 2. Kế hoạch Bài báo Khoa học (Paper Roadmap)

- **Mục tiêu Hội nghị / Tạp chí**: IEEE/ACM FCCM, FPGA, ICASSP, Interspeech, hoặc IEEE ESL.
- **Tiêu đề Dự kiến**: *Spatial Dataflow vs. SIMT for Continuous Edge Voice AI: A Comprehensive Pareto Analysis from Jetson Orin to FPGA*.
- **Đóng góp Dự kiến**:
  1. Phân tích định lượng sâu sắc về hiện tượng suy giảm hiệu suất SIMT khi xử lý âm thanh luồng ($batch=1$).
  2. Kiến trúc luồng dữ liệu tùy biến trên FPGA tích hợp trực tiếp tầng tiền xử lý I2S/STFT và tầng nơ-ron.
  3. Đo kiểm thực nghiệm Pareto Frontier: Đối sánh đa chiều giữa TensorRT (FP16/INT8) trên Orin và FPGA overlay.
