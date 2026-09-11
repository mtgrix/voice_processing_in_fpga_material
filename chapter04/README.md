# Thí nghiệm 4.1: Ước lượng & Ánh xạ Tài nguyên FPGA (FPGA Resource Mapping)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_04_fpga_dsp_bram_mapping`
- **Chương liên kết**: Chương 04 — Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Ước lượng và lập mô hình sử dụng tài nguyên phần cứng (LUTs, Flip-Flops, DSP48E2, BRAM, UltraRAM) cho mô hình nhận diện giọng nói khi đưa lên FPGA.

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
- Giúp người học nắm vững cách tính toán ngân sách phần cứng (Resource Budgeting) trước khi tổng hợp mạch.

## 3. Mục tiêu Phần cứng
- AMD Xilinx Kria KV260 (Zynq UltraScale+ XCZU5EV).

## 4. Dẫn xuất Toán học & Thuật toán
- Công thức tính số lượng DSP cần thiết theo hệ số song song $P$: $N_{\text{DSP}} = P \times \text{MACs\_per\_cycle}$.
- Dung lượng bộ nhớ trên chip: $C_{\text{SRAM}} = N_{\text{weights}} \times \frac{b}{8} + C_{\text{line\_buffer}}$.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Kiến trúc mạng KWS (ví dụ MatchboxNet hoặc TC-ResNet).

## 6. Lệnh Thực thi
```bash
python chapter04/exp_04_fpga_dsp_bram_mapping/estimate.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Tỷ lệ chiếm dụng tài nguyên $< 80\%$ để đảm bảo khả năng đi dây (Routability).

## 8. Phương pháp Đo lường
- Vivado Synthesis & Implementation Resource Utilization Reports (`report_utilization`).

## 9. Kết quả Thực nghiệm & Bằng chứng
- [Chờ tổng hợp Vivado]

## 10. Đánh đổi Phần cứng - Phần mềm
- Unroll vòng lặp càng nhiều thì độ trễ càng thấp nhưng tiêu tốn thêm LUT và DSP.

## 11. Giới hạn & Giả định
- Chưa xét đến chi phí logic phụ trợ của AXI bus.

## 12. Bài học Sư phạm Rút ra
- Không gian silicon là hữu hạn; thiết kế FPGA luôn là bài toán cân đối giữa thông lượng và diện tích mạch.

## 13. Nguồn Trích dẫn
- `R01-04`: AMD Xilinx Kria KV260 User Guide.
