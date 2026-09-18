# Tiến độ Soạn thảo & Nghiên cứu — Voice Edge AI (Book Status)

> **Theo dõi tiến độ 10 chương chuyên khảo và các mục của bài báo khoa học.**
> Cập nhật lần cuối: 2026-09-18

---

## 1. Bảng Trạng thái 10 Chương

| Chương | Tên Chương | Bản thảo Tiếng Việt | Bản thảo Tiếng Anh | Thí nghiệm | Trạng thái |
|:---:|---|:---:|:---:|:---:|:---:|
| **01** | Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực | 🚧 Khung sườn | Đã viết (11 trang PDF) | exp_01 đã chạy, có log | Đã soạn bản tiếng Anh |
| **02** | Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_02 | Đã tạo khung |
| **03** | Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU | 🚧 Khung sườn | Đã soạn 3.1–3.3; 3.4 còn trống | 🚧 exp_03 | Đã viết bản tiếng Anh, chưa đo |
| **04** | Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_04 | Đã tạo khung |
| **05** | So sánh Các Phương pháp luận Tăng tốc trên FPGA: DPU, HLS, FINN & RTL | 🚧 Khung sườn | Đã soạn đủ 5.1–5.3, 5.5, 5.6; giữ nguyên 5.4 | 🚧 exp_05 | Đã viết bản tiếng Anh, chưa đo |
| **06** | Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh | 🚧 Khung sườn | Đã soạn (16 trang PDF) | 🚧 exp_06 | Đã viết bản tiếng Anh, chưa đo |
| **07** | Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại | 🚧 Khung sườn | Đã soạn đủ 7.1–7.4, 7.6; giữ nguyên 7.5 | 🚧 exp_07 | Đã viết bản tiếng Anh, chưa đo |
| **08** | Kiến trúc Pipeline keyword-spotting trên board: từ micro đến quyết định | 🚧 Khung sườn | Đã soạn (10 trang PDF) | 🚧 exp_08 | Đã viết bản tiếng Anh, chưa đo |
| **09** | Streaming Conformer overlay + Left-Context Ring Buffer | 🚧 Khung sườn | Đã soạn (14 trang PDF) | 🚧 exp_09 | Đã viết bản tiếng Anh, chưa đo |
| **10** | Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo Khoa học | 🚧 Khung sườn | 🚧 Khung sườn | 🚧 exp_10 | Đã tạo khung |
| **A** | Model Fundamentals: The Forward Pass in Hardware Terms (phụ lục, không gắn chặng thí nghiệm) | — | Đã soạn đủ A.1–A.6 | — | Đã viết bản tiếng Anh, chưa đo |

---

## 1.1 Trạng thái nội dung: khung sườn ĐÃ được sửa cho đúng đề cương

Hai trạng thái khác nhau phải phân biệt rõ: chương **chưa viết** (các khối `TODO (Nội dung cần viết)`) và chương **đã viết sai đề cương**. Từ 2026-09-13, nhóm lỗi thứ hai đã được xử lý:

- `book/TOC.md` giờ là xương sống 10 chương chiếu từ `plan-v2.md` §7 và đã được track. Trước đó nó là bản 5 chương thừa hưởng từ `plan.md`, và `tests/test_plan_consistency.py` phải để nó ở dạng xfail.
- Số liệu nhớ on-chip ở Chương 04 đã thay bằng giá trị có trang datasheet (`V-01-11`); "4.5 MB" là số của `plan.md`.
- Whisper đã bị rút khỏi Chương 08; model đích là NeMo streaming Conformer-Transducer `small`.
- WER không còn là metric toàn dụng ở Chương 02, 07, 10 và ở `docs/BOOK_PEDAGOGY.md` (§5.3 cấm dùng lẫn).
- Chương 05 thôi tuyên bố FINN/HLS là "vũ khí tối thượng"; gate chặng 5 đòi log tổng hợp thật.
- Chương 06 dạy rõ đường âm thanh vào PL qua carrier, vì KV260 không có mic.
- Từ 2026-09-14 (Issue #57): mọi mục khái niệm viết mới hoặc viết lại phải xếp đủ ba lớp theo đúng thứ
  tự — **Intuition** (không ký hiệu), **Mechanism** (số học forward pass), **Hardware application**
  (byte, băng thông, BRAM/URAM, DSP slice, stall trên Orin hoặc KV260). Traceability chuyển vào
  blockquote có lead-in đậm, không bỏ record nào, và một mục viết lại phải cite siêu tập V-id của mục nó
  thay. Lý do ghi ở đây chứ không chỉ ở commit: người đọc của sách là kỹ sư phần cứng, không phải kỹ sư
  học máy — xem mục "Phụ lục A" trong `book/TOC.md`.

**Chưa chốt, cần chủ repo:** `plan-v2.md` §7 gán artefact chặng 8–9 (KWS SoC trên board; Conformer overlay) khác với tiêu đề chương 08–09 hiện tại. Ghi chi tiết ở `book/TOC.md`, mục "Lệch ánh xạ chưa chốt".

**Chưa làm:** văn xuôi tiếng Việt của cả mười chương. Bản tiếng Anh tính đến 2026-09-18: chương 1 và chương 9 có văn xuôi ở mọi mục; Phụ lục A có đủ sáu mục A.1–A.6; chương 3 thiếu 3.4; chương 5 đã soạn đủ 5.1–5.6; chương 8 có 8.4 mỏng; chương 6 đã soạn 16 trang; chương 7 đã soạn đủ 7.1–7.6; chương 2, 4 và 10 vẫn là tiêu đề rỗng. Không một ô nào trong bảng chương được đóng dấu ✅: theo `scripts/verify_integrity.py`, dấu ✅ chỉ được đặt ở dòng có mã thí nghiệm đủ dài để khớp với log, còn mã chương hai chữ số thì không phân biệt được — nên tiến độ chương ghi bằng chữ, không ghi bằng dấu.

---

## 2. Kế hoạch Bài báo Khoa học (Paper Roadmap)

- **Mục tiêu Hội nghị / Tạp chí**: IEEE/ACM FCCM, FPGA, ICASSP, Interspeech, hoặc IEEE ESL.
- **Tiêu đề Dự kiến**: *Spatial Dataflow vs. SIMT for Continuous Edge Voice AI: A Comprehensive Pareto Analysis from Jetson Orin to FPGA*.
- **Đóng góp Dự kiến**:
  1. Phân tích định lượng sâu sắc về hiện tượng suy giảm hiệu suất SIMT khi xử lý âm thanh luồng ($batch=1$).
  2. Kiến trúc luồng dữ liệu tùy biến trên FPGA tích hợp trực tiếp tầng tiền xử lý I2S/STFT và tầng nơ-ron.
  3. Đo kiểm thực nghiệm Pareto Frontier: Đối sánh đa chiều giữa TensorRT (FP16/INT8) trên Orin và FPGA overlay.
