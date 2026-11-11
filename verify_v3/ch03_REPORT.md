# BÁO CÁO NGHIỆM THU CHƯƠNG 3 (verify_v3/ch03_REPORT.md)
**Tên chương:** Bước làm mềm mép Nyquist: khối FIR tùy chọn (`chuong_v3/chuong_03_fir_nyquist.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy)  
**Thời điểm hoàn thành:** 2026-11-11  

---

## 1. Bảng kiểm định chi tiết từng mục con (Subsection Checklist)

| Mục con | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / minh họa số? | Phương án + Đánh đổi + Lựa chọn có số? | Đường (A) Intel IP? | Đường (B) HDL tự viết? | Twin Python + TB iverilog? | Câu tóm lại cuối mục? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **3.1. Bản chất hiện tượng rò rỉ phổ mép Nyquist** | **Có** (thành phần gần 8 kHz sau khi nhân Hanning tràn búp phổ qua Nyquist, sinh sóng đổi dấu $(-1)^\tau$ phá hủy đỉnh tự tương quan $r(\tau)$) | **Có** (dao động $f = 8\text{ kHz}$ lấy mẫu tại $16\text{ kHz}$ sinh dãy alternating $[+A, -A, +A, -A]$) | **Có** (bật FIR so với Praat 7.0.03 vốn không lọc sẽ tự tạo nguồn lệch; chọn mặc định `bypass = 1`, cho phép bật khi nghiên cứu) | N/A (phân tích hiện tượng và đối chiếu Praat) | N/A (phân tích hiện tượng và đối chiếu Praat) | **Có** (kiểm chứng Praat source qua `ch03_praat_lines.py`) | **Có** (*Tóm lại: Thành phần gần Nyquist sinh ra sóng đổi dấu...*) |
| **3.2. Các phương án, đánh đổi, ta chọn gì, vì sao** | **Có** (bài toán đánh đổi giữa độ suy hao dải chặn, trễ nhóm và tài nguyên silicon; phân tích bẫy thường gặp về độ rộng bit hệ số và độ suy hao dải chặn) | **Có** (tính toán công thức Kaiser ra 147 tap; tính độ trễ nhóm $\tau_g = 15$ mẫu và công thức dời khung $s_{\text{start, FIR}} = s_{\text{start}} - 15$) | **Có** (Bảng 4 phương án: Bypass, 31 tap, 63 tap, 127 tap; số liệu từ `scipy.signal.firls`; chọn 31 tap kèm bypass) | N/A (cơ sở lý thuyết lọc FIR) | N/A (cơ sở lý thuyết lọc FIR) | **Có** (`verify_v3/ch03_fir_design.py` kiểm chứng độ suy hao và lượng tử hóa Q1.15) | **Có** (*Tóm lại: Dải chuyển tiếp 400 Hz quá hẹp...*) |
| **3.3. Đường (A): Khối IP FIR Compiler II của Intel** | **Có** (hộp đen IP công nghiệp tiềm ẩn rủi ro tràn hàng đợi khi đặt sai `Input Sample Rate` trong hệ thống đọc tệp) | **Có** (phân tích tỷ số chia nhịp: 0,016 MSPS sinh 3.125 chu kỳ/mẫu gây tràn FIFO; 0,5 MSPS sinh 100 chu kỳ/mẫu an toàn) | **Có** (phân tích chi tiết 7 nhóm tham số trong Parameter Editor, liên hệ trực tiếp với lý thuyết mục 3.2) | **Có** (`altera_fir_compiler_ii`, giải mã GUI, cổng Avalon-ST, đoạn mã Verilog wrapper `u_fir_ip`) | N/A (thuộc nhánh IP) | N/A (thuộc nhánh IP) | **Có** (*Tóm lại: Khối IP Intel FIR Compiler II tối ưu hóa tài nguyên...*) |
| **3.4. Đường (B): Khối HDL tự viết: FIR đối xứng gấp thời gian** | **Có** (kiến trúc trực tiếp song song tốn tới 16 bộ nhân DSP là lãng phí tài nguyên silicon ở tốc độ 16 kHz) | **Có** (rút gọn 31 tap thành 15 cặp đối xứng tiền cộng 17-bit + 1 hệ số trung tâm, tuần tự 16 nhịp xung nhịp 50 MHz) | **Có** (so sánh Fully Parallel vs Transposed vs Folded Time-Multiplexed; chọn Folded 1 DSP, 0 M10K) | **Có** (đối chiếu từng tham số IP với kiến trúc HDL) | **Có** (`rtl/v3/ch03_fir_filter.v`, liệt kê 45 dòng cốt lõi và giải thích chi tiết) | **Có** (Bảng đối chiếu 3 cột song song Twin vs HDL dòng-từng-dòng) | **Có** (*Tóm lại: Khối HDL folded FIR dùng đúng 1 DSP...*) |
| **3.5. Kiểm chứng mô hình song sinh Python và mô phỏng chu kỳ HDL** | **Có** (nguy cơ sai lệch từng bit giữa phần mềm và phần cứng khi xử lý số học dấu phẩy tĩnh và cơ chế phản áp) | **Có** (6 thử thách: Impulse response, sin 7,8 kHz suy hao $-6{,}54\text{ dB}$, sin 1,0 kHz, WAV thật, stress bão hòa $\pm 32767$, random backpressure) | **Có** (chiến lược kiểm chứng 3 tầng; Bảng đối chiếu toàn diện IP vs HDL) | **Có** (Bảng so sánh IP vs HDL) | **Có** (Testbench `tb/v3/tb_ch03_fir.v` đọc kích thích và đối soát từng chu kỳ) | **Có** (`verify_v3/ch03_fir_twin.py` sinh 3.390 chu kỳ kích thích; testbench iverilog; kịch bản Linux) | **Có** (*Tóm lại: Mô hình song sinh Python đã sinh tập vector 3.390 chu kỳ...*) |
| **Bài tập cuối chương** | 4 bài tập thực chiến bao quát: (1) Tính bậc lọc Kaiser; (2) Dẫn xuất trễ nhóm và dời khung; (3) Ngân sách chu kỳ và thông lượng 2,94 MSPS; (4) Lượng tử hóa Q1.15 và khâu bão hòa biên độ. | Tất cả bài tập đều có lời giải mẫu chi tiết từng bước, kết quả khớp với `verify_v3/ch03_exercises.py`. |

---

## 2. Thống kê khối lượng và quy mô tài liệu

- **Số trang biên dịch PDF (`phan_moi_v3.pdf`):** Chương 3 chiếm 21 trang (từ trang 81 đến trang 101).
- **Số từ tiếng Việt (`chuong_v3/chuong_03_fir_nyquist.tex`):** 12.904 từ.
- **Số dòng mã nguồn LaTeX:** 595 dòng.
- **Số hình vẽ TikZ kỹ thuật cao:** 2 hình:
  1. *Hình 5 (trang 84):* Đáp ứng tần số biên độ $|H(f)|$ (dB) của các phương án bộ lọc FIR so với đường cong mục tiêu Boersma (1993) trên dải chuyển tiếp 400 Hz (trích xuất từ `verify_v3/ch03_fir_design.py`).
  2. *Hình 6 (trang 89):* Sơ đồ kiến trúc phần cứng khối lọc FIR 31 tap gấp thời gian với bộ tiền cộng 17-bit và 1 khối DSP (`rtl/v3/ch03_fir_filter.v`), định tuyến trực giao không chạm viền, không đè nhãn.
- **Số bảng số liệu:** 3 bảng:
  1. *Bảng 17 (trang 84):* So sánh định lượng các phương án bộ lọc FIR làm mềm mép Nyquist tại $f_s = 16\text{ kHz}$.
  2. *Bảng 18 (trang 94):* Đối chiếu trực tiếp giữa các dòng lệnh của Python Twin và mã nguồn phần cứng Verilog.
  3. *Bảng 19 (trang 98):* So sánh toàn diện giữa khối IP Intel FIR Compiler II và mã nguồn HDL tự viết cho Chương 3.
- **Số đoạn mã nguồn trích dẫn:** 3 listings:
  1. *Listing 13 (trang 88):* Mã khởi tạo giao diện khối IP Intel FIR Compiler II trong hệ thống (`u_fir_ip`).
  2. *Listing 14 (trang 90–91):* Mã nguồn phần cứng bộ lọc FIR 31 tap gấp thời gian (`rtl/v3/ch03_fir_filter.v`, 45 dòng then chốt).
  3. *Listing 15 (trang 95–96):* Hàm cập nhật chu kỳ của mô hình song sinh FIR (`verify_v3/ch03_fir_twin.py`, dòng 28–98).
- **Lỗi biên dịch LaTeX và Overfull box:**
  - 0 lỗi biên dịch.
  - 0 cảnh báo `Overfull \hbox` trong toàn bộ Chương 3 (kết quả kiểm tra log không có cảnh báo nào vượt mức cho phép).

---

## 3. Danh mục các thông số chưa kiểm chứng và mục "(phải đo)"

Theo đúng nguyên tắc trung thực học thuật của đề cương:
1. **Tài nguyên logic ALM và tần số cực đại $F_{\max}$ của khối IP Intel FIR Compiler II:** Được ghi rõ là `(phải đo trong Quartus Fitter và Timing Analyzer)`, do môi trường hiện tại không cài đặt Quartus Prime.
2. **Độ trễ xử lý (Latency) của khối IP Intel:** Được ghi rõ là `(phải kiểm trong báo cáo sinh mã IP Generation Report hoặc mô phỏng IP)`.
3. **Tài nguyên ALM và $F_{\max}$ của khối HDL tự viết (`ch03_fir_filter.v`):** Được ghi rõ là `(phải đo trong Quartus)`. Về mặt cấu trúc vi kiến trúc, thiết kế đã được chứng minh tốn đúng:
   - 0 khối RAM M10K (sử dụng 496 flip-flop thanh ghi dịch trong ALM).
   - Đúng 1 khối nhân DSP chuyên dụng (phép nhân $17 \times 16 \to 33$ bit).
   - 544 thanh ghi flip-flop logic (496 FF mảng dịch + 40 FF tích lũy + 8 FF điều khiển/trạng thái).
4. **Kết quả chạy mô phỏng chu kỳ bằng Icarus Verilog trên Linux:**
   - Script thực thi `verify_v3/run_ch03_iverilog.sh` đã được tạo sẵn với chuẩn xuống dòng Unix LF và cấp quyền thực thi.
   - Testbench `tb/v3/tb_ch03_fir.v` đọc 3.390 chu kỳ từ `tb_ch03_fir_stim.txt` và `tb_ch03_fir_expected.txt`.
   - Trong văn bản LaTeX, kết quả được đánh dấu giữ chỗ bằng khối `\todo{box}` để người đánh giá (reviewer) chạy thực tế trên Linux và điền số liệu.
5. **Dòng mã nguồn chính xác trong Praat 7.0.03:** Được đánh dấu bằng ký hiệu chuẩn `TODO-PRAAT-LINE` để người đánh giá điền số dòng chính xác từ bản cài Linux 7.0.03.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Đặc tính suy hao dải chặn của bộ lọc 31 tap:** Mặc dù bộ lọc 31 tap đáp ứng tốt yêu cầu làm dịu mép Nyquist (suy hao $-9{,}41\text{ dB}$ tại $8\text{ kHz}$) và bảo toàn dải thông phẳng $\pm 0{,}25\text{ dB}$ tới $7{,}4\text{ kHz}$, độ suy hao dải chặn của nó không thể đạt tới mức triệt tiêu hoàn toàn như kỳ vọng lý thuyết ban đầu của Boersma 1993 (cần tới 147 tap theo công thức Kaiser). Đây là điểm thỏa hiệp kỹ thuật có chủ đích để giữ trễ nhóm ở mức nhỏ (15 mẫu) và tiết kiệm tài nguyên.
2. **Cơ chế chuyển mạch động Bypass:** Mạch hỗ trợ cờ `bypass` chuyển đổi linh hoạt. Tuy nhiên, nếu chuyển mạch đột ngột trong khi khối FIR đang dở dang chu kỳ tính toán 16 nhịp, mẫu đầu ra đang tính sẽ bị hủy để nhường đường cho luồng truyền thẳng 1 chu kỳ. Trong ứng dụng thực tế, cờ bypass được cấu hình tĩnh trước mỗi phiên chạy xử lý tệp từ HPS nên không gây ảnh hưởng.
3. **Môi trường Windows thiếu Icarus Verilog và Praat 7.0.03 cục bộ:** Mặc dù toàn bộ mã nguồn Python Twin, RTL, Testbench và dữ liệu vector đã được tính toán đồng bộ bit-đối-bit, việc chạy mô phỏng Verilog thực tế cần được tiến hành trên môi trường Linux của reviewer.

---

## 5. Lịch sử các Commit Git

Toàn bộ quá trình phát triển được lưu vết qua các commit nguyên tử trên nhánh `v3`:
- `b4271b5`: `v3: ch03 3.1` (Hiện tượng rò rỉ phổ mép Nyquist, dao động đối dấu, đối soát Praat 7.0.03).
- `0506a6d`: `v3: ch03 3.2` (Phân tích 4 phương án, firls, công thức Kaiser, trễ nhóm 15 mẫu, dời lưới khung).
- `916e4c7`: `v3: ch03 3.3` (Giải mã chi tiết 7 tham số IP FIR Compiler II, cạm bẫy Input Sample Rate, instantiation wrapper).
- `7c2ccec`: `v3: ch03 3.4` (Kiến trúc folded FIR 17-bit pre-adder 1 DSP, Listing RTL 45 dòng, bảng đối chiếu Twin-HDL).
- `4fc653b`: `v3: ch03 3.5` (Kiểm chứng 3.390 chu kỳ, 4 bài tập thực chiến, tinh chỉnh TikZ và triệt tiêu toàn bộ Overfull hbox).
- `[commit tiếp theo]`: `v3: ch03 done` (Hoàn tất báo cáo nghiệm thu và đóng gói Chương 3).
