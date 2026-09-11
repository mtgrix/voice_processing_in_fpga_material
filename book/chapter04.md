# Chương 4: Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu

> *Mục tiêu: Nắm vững vi kiến trúc cơ bản của FPGA (LUT, FF, DSP48E2, BRAM, UltraRAM, AXI-Stream) và nguyên lý tính toán không gian (spatial dataflow computing) cho xử lý luồng.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Bảng tra cứu (Lookup Table — LUT)**: Mạch phần cứng khả trình thực hiện hàm logic boolean tùy ý.
> - **Chu kỳ khởi tạo (Initiation Interval — II)**: Số chu kỳ xung nhịp giữa hai lần nhận mẫu dữ liệu liên tiếp ($II=1$ là lý tưởng).
> - **Độ sâu đường ống (Pipeline Depth / Latency)**: Tổng số chu kỳ xung nhịp từ khi dữ liệu vào tầng đầu tiên đến khi kết quả xuất hiện ở tầng cuối cùng.

---

## 4.1 Trực giác: Tính toán Không gian (Spatial) vs. Tính toán Thời gian (Temporal)
<!-- 
TODO:
- CPU/GPU thực thi lệnh tuần tự theo thời gian trên một tập phần cứng cố định.
- FPGA "đúc" mạch phần cứng chuyên dụng trải rộng trên không gian silicon khớp chính xác với đồ thị tính toán.
-->

## 4.2 Các Khối Phần cứng Cơ bản trên FPGA
<!-- 
TODO:
- Configurable Logic Blocks (CLB): LUT6 và Flip-Flops (FF).
- Khối DSP Slices (DSP48E2): Phép nhân 27x18 bit và cộng tích lũy (MAC) tốc độ cao.
- Bộ nhớ SRAM trên chip: Block RAM (36Kb mỗi khối, dual-port) và UltraRAM (288Kb mỗi khối, dung lượng cao).
-->

## 4.3 Chuẩn Giao tiếp Dòng Dữ liệu AXI4-Stream
<!-- 
TODO:
- Cơ chế bắt tay phần cứng: TDATA, TVALID, TREADY.
- Không cần quản lý địa chỉ bộ nhớ; dữ liệu chảy liên tục từ bộ chuyển đổi tương tự-số (ADC) qua các khối tiền xử lý và mạng nơ-ron.
-->

## 4.4 Khả năng Lưu trữ Trọng số Hoàn toàn trên Chip (On-Chip Weight Residency)
<!-- 
TODO:
- Khảo sát dung lượng BRAM/URAM trên các kit phổ biến (Kria KV260: ~4.5MB SRAM).
- Lợi ích triệt tiêu việc truy cập DDR DRAM: giảm điện năng từ Watts xuống milliwatts và đạt độ trễ chu kỳ xung nhịp tất định.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter04/`](../chapter04/).
