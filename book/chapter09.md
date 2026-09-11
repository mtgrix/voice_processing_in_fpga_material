# Chương 9: Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng / Phần mềm

> *Mục tiêu: Làm chủ quy trình tích hợp toàn diện trên chip SoC (Zynq UltraScale+ / Kria KV260): thiết kế phân tầng xử lý giữa ARM Host (CPU) và Programmable Logic (FPGA), tối ưu hóa truyền nhận dữ liệu DMA và kiểm soát nhiệt độ.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Giao thức AXI4**: Giao diện kết nối bus chuẩn công nghiệp giữa Processing System (PS) và Programmable Logic (PL).
> - **Direct Memory Access (DMA)**: Truyền dữ liệu trực tiếp giữa bộ nhớ ngoài và logic khả trình mà không tiêu tốn chu kỳ CPU.
> - **Chỉ số Hiệu năng trên Công suất (TOPS/Watt)**: Thước đo hiệu quả sử dụng năng lượng vật lý của toàn hệ thống.

---

## 9.1 Trực giác: Sự Phân chia Công việc Tối ưu giữa Host CPU và FPGA Fabric
<!-- 
TODO:
- CPU ARM rất giỏi xử lý logic rẽ nhánh, quản lý mạng, giao thức OS (Linux/Petalinux) và giải mã chuỗi đầu ra (CTC decode / Beam Search).
- FPGA Fabric vượt trội ở việc tính toán song song ma trận số học luồng với độ trễ cố định.
-->

## 9.2 Kiến trúc Hệ thống SoC: Processing System (PS) và Programmable Logic (PL)
<!-- 
TODO:
- Sơ đồ tích hợp trên Kria KV260: Quad Cortex-A53 + AXI HP/HPC Ports + AXI DMA + Custom IP Overlay.
- Quản lý bộ nhớ đệm liên kết (Cache Coherency) và cơ chế Zero-Copy Buffer.
-->

## 9.3 Tích hợp Phần mềm: PYNQ, Vitis AI Runtime (VART) và Trình điều khiển Linux
<!-- 
TODO:
- Xây dựng lớp giao tiếp Python/C++ sử dụng thư viện PYNQ hoặc Vitis AI C++ API.
- Đo đạc độ trễ round-trip truyền nhận qua DMA và so sánh với kernel launch của CUDA trên Jetson Orin.
-->

## 9.4 Quản lý Năng lượng & Phân tán Nhiệt (Thermal & Power Management)
<!-- 
TODO:
- Phân tích công suất tĩnh vs công suất động trên FPGA.
- Kỹ thuật Clock Gating và Power Domains trên dòng UltraScale+.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter09/`](../chapter09/).
