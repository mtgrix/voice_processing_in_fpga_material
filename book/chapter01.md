# Chương 1: Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực

> *Mục tiêu: Nắm vững bản chất chuỗi xử lý tín hiệu âm thanh liên tục (streaming audio), các ràng buộc độ trễ vật lý (latency constraints) và lý do bài toán xử lý giọng nói tại biên luôn chạy ở chế độ kích thước lô bằng một ($batch=1$).*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Biến đổi Fourier Rời rạc (DFT)**: Phân tích phổ tín hiệu từ miền thời gian sang miền tần số.
> - **Nguyên lý bất định thời gian - tần số (Heisenberg-Gabor)**: Sự đánh đổi giữa độ phân giải thời gian và độ phân giải tần số của hàm cửa sổ.
> - **Thang đo Mel phi tuyến**: Mô hình hóa độ nhạy tần số của thính giác người.

---

## 1.1 Trực giác: Sự Khác biệt Cốt lõi giữa Xử lý Thị giác và Xử lý Giọng nói
<!-- 
TODO (Nội dung cần viết):
- Phân tích sự khác biệt giữa ảnh tĩnh 2D (batching dễ, kích thước tensor cố định) và sóng âm 1D (dòng dữ liệu liên tục thời gian thực).
- Khái niệm kích thước lô bằng một (batch=1) và áp lực phản hồi tức thời (<10ms đối với KWS, <100ms đối với ASR).
- Tại sao GPU truyền thống không được thiết kế tối ưu cho dòng dữ liệu nhỏ giọt liên tục này.
-->

## 1.2 Chuỗi Tiền Xử lý Tín hiệu Âm thanh (Audio Preprocessing Pipeline)
<!-- 
TODO (Nội dung cần viết):
- Sơ đồ chuỗi biến đổi: Waveform x[n] -> Cửa sổ trượt (Sliding Window) -> Hamming Window -> STFT/FFT -> Power Spectrum -> Mel Filterbank -> Log Compression.
- Các tham số kỹ thuật chuẩn mực: Tần số lấy mẫu fs=16kHz, độ dài khung N=400 (25ms), bước nhảy H=160 (10ms).
-->

## 1.3 Cơ chế Toán học: STFT và Ngân hàng Lọc Mel
<!-- 
TODO (Nội dung cần viết):
- Công thức giải tích của STFT và biểu diễn số phức Re + j*Im.
- Cách xây dựng ma trận bộ lọc tam giác Mel Filterbank.
- Công thức nén Log-Mel và ý nghĩa khử tương quan năng lượng.
-->

## 1.4 Ứng dụng & Thách thức Phần cứng
<!-- 
TODO (Nội dung cần viết):
- Phân tích yêu cầu bộ nhớ đệm xoay vòng (ring buffer) trên phần cứng.
- Đánh đổi giữa việc tính toán tiền xử lý trên CPU Host vs. tăng tốc bằng IP Core chuyên dụng trên FPGA.
-->

---

## Thực nghiệm Liên kết (Hands-on Experiment)
- Xem mã nguồn thí nghiệm và kịch bản thực thi tại [`chapter01/`](../chapter01/).

## Tài liệu Tham khảo
- Tham chiếu nguồn: `R01-03` (Conformer), `R01-05` (MatchboxNet) trong [`docs/SOURCES.md`](../docs/SOURCES.md).
