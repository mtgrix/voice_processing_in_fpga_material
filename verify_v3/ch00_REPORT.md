# Báo cáo Nghiệm thu Chương 0 (verify_v3/ch00_REPORT.md)

**Chương 0: Bài toán, mục tiêu so sánh, và Praat thật sự làm gì**  
**Tập tin chương:** `chuong_v3/chuong_00_bai_toan.tex`  
**Nhánh Git:** `v3`  
**Ngày hoàn thành:** 11/11/2026  

---

## 1. Bảng đánh giá theo từng mục con (Per-subsection Evaluation)

| Mục con | Mở đầu bằng vấn đề thực tế (y/n) | Ví dụ tính tay (y/n, script) | Phân tích phương án + đánh đổi + lựa chọn (y/n) | Tuyến IP Catalog (y/n) | Tuyến HDL tự viết (y/n) | Twin + mô phỏng (N/N) | Câu tóm tắt in nghiêng (y/n) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0.1 Một file, hai câu trả lời** | y | y (`ch00_naive_methods.py`) | y (Zero-crossing vs FFT vs Autocorr) | n/a | n/a | n/a | y |
| **0.2 Ý tưởng của Boersma** | y | y (`ch00_norm_sine.py`) | y (Unnormalized vs Boersma $R_w$) | n/a | n/a | n/a | y |
| **0.3 Tám bước của Praat & thiết kế phần cứng** | y | y (10 tham số & công thức C++) | y (Bảng so sánh 5 lựa chọn kiến trúc) | y | y | n/a | y |
| **0.4 Kiến trúc hệ thống & bản đồ các chương** | y | y (Phân tích luồng dữ liệu Hình 1) | y (PIO vs DMA, FIFO, HPS-FPGA) | y | y | n/a | y |
| **0.5 Các phép đo: GPE, VDE, FFE và cent** | y | y (`ch00_metrics.py`) | y (4 tình huống khung, ngưỡng 20%) | n/a | n/a | n/a | y |
| **0.6 Ngân sách chu kỳ, RTF và mạch pair counter** | y | y (`ch00_cycle_budget.py`) | y (Tuần tự 1 DSP vs Song song nhiều DSP) | y | y | 201/201 (`ch00_test_pair_counter.py`) | y |
| **0.7 Bản đồ kiểm chứng 3 tầng & golden v2** | y | y (`ch00_golden_spec.py`) | y (Parabol vs sinc70, Median vs Viterbi) | y | y | n/a | y |
| **Bài tập cuối chương (5 bài tập)** | y | y (`ch00_exercises.py`) | y (Đề bài và lời giải toán học chi tiết) | n/a | n/a | n/a | y |

---

## 2. Thống kê quy mô tài liệu và hiện vật (Metrics Summary)

- **Số trang PDF (`phan_moi_v3.pdf`):** 27 trang (toàn bộ Chương 0 chiếm 25 trang, từ trang 3 đến trang 27).
- **Số từ trong tệp `.tex` (`chuong_v3/chuong_00_bai_toan.tex`):** 17.463 từ (1.075 dòng, 99.668 ký tự).
- **Số hình vẽ (Figures):** 1 hình TikZ kiến trúc hệ thống toàn tuyến (`chuong_v3/fig_ch00_system.tex`, `Hình 1`).
- **Số bảng dữ liệu (Tables):** 5 bảng:
  1. `Bảng 1`: Tính tay 16 mẫu hiện tượng đếm điểm qua không thất bại với sóng có hài bậc hai.
  2. `Bảng 2`: Tính tay 8 mẫu bù suy giảm cửa sổ Hanning theo nguyên lý Boersma.
  3. `Bảng 3`: Bảng đối chiếu 5 lựa chọn thiết kế: Praat làm gì vs Phần cứng làm gì vs Lý do & Ảnh hưởng.
  4. `Bảng 4`: Bảng tính tay 10 khung mô phạm các độ đo VDE, GPE, FFE và sai số cent.
  5. `Bảng 5`: Kết quả đối chiếu toàn tuyến bộ công cụ golden v2 với Praat 7.0.03 trên tín hiệu tổng hợp chuẩn (sạch và ồn SNR 5 dB).
- **Số đoạn mã nguồn (Listings):** 2 đoạn mã:
  1. `Listing 1`: Mã nguồn Verilog mạch phát cặp mẫu liên tục `rtl/v3/ch00_pair_counter.v`.
  2. `Listing 2`: Mô hình tương đương Python bit-exact `verify_v3/ch00_pair_counter_twin.py`.
- **Kết quả biên dịch XeLaTeX:** Hoàn thành 2 lượt biên dịch với **0 lỗi**, **0 nhãn chưa định nghĩa (??)**, và toàn bộ cảnh báo Overfull `\hbox` đều strictly $< 7\text{ pt}$ (nằm sâu dưới giới hạn cho phép $10\text{ pt}$).

---

## 3. Các con số chưa thể đo và danh mục "phải đo" (Measured Items)

Toàn bộ các số liệu thuật toán trong chương đã được kiểm chứng bằng kịch bản Python độc lập và khớp với `golden_v2`. Tuy nhiên, một số chỉ số vật lý gắn liền với phần cứng thực tế và môi trường laptop của người dùng được gắn nhãn **"phải đo"** như sau:
1. **Thời gian chạy của phần mềm Praat gốc trên máy tính:** Phải đo bằng lệnh ghi thời gian trong script Praat `golden_v2/praat_pitch.praat` trên laptop của người dùng (loại trừ thời gian khởi động giao diện GUI và ghi nhận số luồng CPU đang chạy).
2. **Thời gian ghi PIO thực tế từ HPS sang FPGA qua cầu Lightweight:** Ước lượng bi quan trong sách là $1\,\mu\text{s}$/lần ghi (tương ứng $\text{RTF}_{\text{transfer}} \approx 0{,}008$). Thời gian thực tế phải đo trên bo mạch DE10-Standard bằng hàm `clock_gettime(CLOCK_MONOTONIC)` bọc quanh vòng lặp ghi $N$ từ 32-bit.
3. **Tần số xung nhịp tối đa $F_{\max}$, số lượng ALM, và số khối DSP thực tế:** Phải đo từ báo cáo Fitter của Intel Quartus Prime sau khi hoàn thành tích hợp toàn bộ hệ thống ở Chương 12.
4. **Bộ file WAV giọng nói thực tế của anh Tú:** Tại thời điểm xuất bản Chương 0, bộ tệp WAV này chưa có sẵn; toàn bộ số liệu đo kiểm thống kê được thực hiện trên tập tín hiệu tổng hợp chuẩn 2,8 s (277 khung); kịch bản `golden_v2/compare.py` đã sẵn sàng để tự động tái chạy ngay khi có dữ liệu.

---

## 4. Phân tích trung thực các điểm yếu còn tồn tại (Honest Remaining Weaknesses)

1. **Nội suy parabol 3 điểm so với sinc70 + Brent của Praat:** Trên tín hiệu sạch, parabol cho sai số cực nhỏ ($< 1{,}1$ cent). Nhưng khi có tạp âm mạnh (SNR 5 dB), đỉnh tự tương quan bị biến dạng hoặc chẻ đôi, khiến xấp xỉ parabol lệch tới 32,9 cent.
2. **Xếp hạng ứng viên bằng điểm số nguyên trên lưới rời rạc:** Việc tính $S_c[\tau]$ trên các tọa độ nguyên $\tau$ trước khi nội suy (thay vì tính tại tọa độ thực nội suy như Praat) có thể dẫn tới hiện tượng lật thứ tự ưu tiên khi hai đỉnh quãng tám có điểm số chênh lệch cực nhỏ (chênh $0{,}0005$ đến $0{,}007$), gây ra sai khác ở 3/207 khung trên file ồn 5 dB.
3. **Bộ lọc trung vị median-3 thay cho bộ dò đường quy hoạch động Viterbi:** Do phần cứng xử lý luồng theo từng khung để đạt thời gian thực và tiết kiệm bộ nhớ, median-3 chỉ quan sát 3 khung cục bộ nên chỉ sửa được lỗi nhảy quãng tám đơn lẻ (1 khung), không thể sửa được các chuỗi nhảy quãng tám kéo dài từ 2 khung trở lên.

---

## 5. Lịch sử các Commit Git trên nhánh v3 (Commit Hashes)

```text
5ecd2ce v3: ch00 format fixes and verified scripts
e91a19d v3: ch00 bài tập cuối chương
06fd6fe v3: ch00 0.7 bản đồ kiểm chứng ba tầng và bộ golden v2
be9e12a v3: ch00 0.6 ngân sách chu kỳ rtf và mạch pair counter
4d1687f v3: ch00 0.5 các phép đo đánh giá GPE VDE FFE và cent
10a11d3 v3: ch00 0.4 kiến trúc hệ thống và bản đồ các chương
961174a v3: ch00 0.3 tám bước praat và lựa chọn thiết kế
fbf57fa v3: ch00 0.2 ý tưởng của Boersma
6812dd9 v3: ch00 0.1 một file hai câu trả lời
```
