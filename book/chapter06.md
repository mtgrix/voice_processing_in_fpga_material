# Chương 6: Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh

> *Mục tiêu: Thiết kế và hiện thực hóa lõi phần cứng (Hardware IP Core) tính toán FFT/STFT và Mel Filterbank sử dụng số dấu phẩy tĩnh (Fixed-Point), kết nối trực tiếp với giao diện micrô I2S/PDM.*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Biểu diễn Dấu phẩy Tĩnh (Fixed-Point Arithmetic - Qm.n)**: Định dạng số nguyên tỷ lệ với $m$ bit nguyên và $n$ bit thập phân.
> - **Hệ số quay Fourier (Twiddle Factors)**: Các hằng số phức $W_N^k = e^{-j \frac{2\pi k}{N}}$ lưu trước trong bảng tra BRAM.
> - **Tỷ số Tín hiệu trên Nhiễu Lượng tử Hóa (SQNR)**: $\text{SQNR} \approx 6.02 \cdot b + 1.76\text{ dB}$ (với $b$ bit biểu diễn).

---

## 6.1 Trực giác: Loại bỏ Nút cổ chai Chuyển giao CPU-FPGA
<!-- 
TODO:
- Thay vì để ARM CPU tính STFT bằng float32 rồi chuyển qua DMA, mạch FPGA nhận trực tiếp luồng bit từ micro.
-->

## 6.2 Thiết kế Lõi FFT Dấu phẩy Tĩnh (Fixed-Point Radix-2 / Radix-4 FFT Engine)
<!-- 
TODO:
- Dẫn xuất thuật toán Cooley-Tukey FFT tối ưu hóa phần cứng.
- Cấu trúc Bướm (Butterfly Unit) sử dụng nhân DSP48E2.
- Phân tích hiện tượng tràn số (overflow) và kỹ thuật dịch bit thích nghi (block floating point).
-->

## 6.3 Hiện thực hóa Ngân hàng Lọc Mel và Nén Logarit trên Phần cứng
<!-- 
TODO:
- Tối ưu hóa lưu trữ ma trận thưa Mel Filterbank trong ROM/BRAM.
- Xấp xỉ hàm logarit tự nhiên $\ln(x)$ bằng phương pháp Piecewise Linear Approximation hoặc thuật toán CORDIC.
-->

## 6.4 Giao diện Thu nhận Âm thanh Phần cứng: I2S và PDM Decimation Filter
<!-- 
TODO:
- Giao tiếp micro kỹ thuật số MEMS qua I2S bus.
- Bộ lọc giải điều chế PDM (CIC Decimation Filter) tích hợp trực tiếp trên FPGA fabric.
-->

---

## Thực nghiệm Liên kết
- Xem chi tiết tại [`chapter06/`](../chapter06/).
