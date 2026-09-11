# Chương 3: Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU

> *Mục tiêu: Phân tích tường tận nguyên nhân gốc rễ (root cause) khiến kiến trúc GPU bị lãng phí năng lượng và gặp vấn đề độ trễ không tất định khi xử lý âm thanh luồng kích thước lô bằng một.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Chi phí khởi chạy lệnh gọi nhân (CUDA Kernel Launch Overhead)**: Độ trễ cố định ($5\mu\text{s} - 20\mu\text{s}$) khi CPU phát lệnh cho GPU qua driver.
> - **Mô hình Roofline**: Đồ thị xác định giới hạn hiệu năng bị chặn bởi tính toán (Arithmetic Intensity) hay bởi băng thông bộ nhớ (Memory Bandwidth).
> - **Tỷ lệ chiếm dụng nhân (SM Occupancy)**: Tỷ số giữa số warp hoạt động thực tế so với số warp tối đa phần cứng hỗ trợ.

---

## 3.1 Trực giác: Sự Không Tương thích giữa Âm thanh Luồng và Kiến trúc SIMT
<!-- 
TODO:
- GPU sinh ra để xử lý các khối dữ liệu song song khổng lồ (hàng triệu pixel cùng lúc).
- Khi âm thanh chỉ đưa vào 80 giá trị đặc trưng Mel mỗi 10ms, hàng ngàn nhân CUDA phải chờ đợi dữ liệu hoặc chạy lãng phí.
-->

## 3.2 Cơ chế: Kernel Launch Overhead, Context Switching và Jitter
<!-- 
TODO:
- Phân tích chi phí khi một mô hình âm thanh có hàng chục lớp nhỏ: STFT -> Conv1D -> LayerNorm -> Attention -> Linear.
- Hiện tượng Jitter: Ngắt CPU của hệ điều hành Linux và tranh chấp bus PCIe/LPDDR5 gây ra độ trễ cực đoan P99.
-->

## 3.3 Phân tích Roofline: Giới hạn Băng thông Bộ nhớ LPDDR5
<!-- 
TODO:
- Tính toán Arithmetic Intensity (FLOPs/byte) của mô hình thoại tại batch=1.
- Chứng minh điểm hoạt động rơi vào sườn dốc (memory-bound) của đồ thị Roofline.
-->

## 3.4 Động lực Chuyển dịch Sang Kiến trúc FPGA
<!-- 
TODO:
- Tóm tắt 3 lý do cốt lõi buộc phải tìm kiếm giải pháp thay thế: Tiêu thụ năng lượng tĩnh cao, Jitter độ trễ, và Hiệu suất sử dụng silicon thấp.
-->

---

## Thực nghiệm Liên kết (Hands-on Experiment)
- Xem mã nguồn thực nghiệm tại [`chapter03/`](../chapter03/).
