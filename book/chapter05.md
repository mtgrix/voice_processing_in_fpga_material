# Chương 5: So sánh Các Phương pháp luận Tăng tốc trên FPGA

> *Mục tiêu: Xây dựng **thủ tục** so sánh 4 hướng tiếp cận phát triển mô hình AI trên FPGA — AMD Vitis AI DPU, FINN Streaming Dataflow, Vivado HLS và Custom RTL — trên cùng một model. Chương này dạy cách so sánh; nó không kết luận hộ số liệu, vì gate nghiệm thu của chặng 5 (`plan-v2.md` §7) đòi bốn hàng mà mỗi hàng phải có log tổng hợp thật.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Mảng tâm thu (Systolic Array)**: Mạng lưới các phần tử xử lý kết nối trực tiếp, dữ liệu nhịp nhàng dịch chuyển đồng bộ.
> - **Độ chính xác tùy biến (Arbitrary Precision)**: Khả năng cấu hình độ dài từ bit bất kỳ (1-bit, 2-bit, 4-bit, 8-bit).
> - **Chỉ thị biên dịch tổng hợp (HLS Pragmas)**: `#pragma HLS PIPELINE`, `#pragma HLS UNROLL`, `#pragma HLS ARRAY_PARTITION`.

---

## 5.1 Bốn Hướng Tiếp cận Kiến trúc Tăng tốc AI trên FPGA
<!-- 
TODO:
- Hướng 1: DPU (Deep Processing Unit - Overlay dựa trên tập lệnh nơ-ron).
- Hướng 2: FINN (Khung luồng dữ liệu streaming cho mô hình lượng tử hóa sâu, gốc là binarized NN inference). Cảnh báo nguồn: `R01-02` đăng ký FINN không phải là nguồn của lý thuyết lượng tử hoá affine — `plan-v2.md` §9.1 chỉ ra `plan.md` đã gán sai như vậy.
- Hướng 3: High-Level Synthesis (C/C++ sang Verilog).
- Hướng 4: Custom RTL (Thiết kế trực tiếp Verilog/SystemVerilog tối ưu hóa từng cổng logic).
-->

## 5.2 Phân tích Đánh đổi (Trade-off Matrix)
<!-- 
TODO:
- Bảng so sánh 4 chiều: Thời gian phát triển (Productivity), Tính linh hoạt (Flexibility), Hiệu năng độ trễ (Latency/Throughput), và Tối ưu hóa tài nguyên phần cứng.
-->

## 5.3 Lựa chọn Kiến trúc Phù hợp cho Bài toán Thoại
<!-- 
TODO:
- Tại sao DPU phù hợp cho mô hình lớn có DDR access (ví dụ Conformer).
- Bốn hàng so sánh dựng sẵn, mỗi ô chờ số từ log tổng hợp thật. Không được tuyên bố FINN/HLS thắng trước khi có số: `plan-v2.md` §9.2 đã lần ra nguồn gốc của mấy con số "FINN nhanh nhất" — chúng là fixture viết tay, không phải phép đo.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter05/`](../chapter05/).
