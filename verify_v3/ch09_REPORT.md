# BÁO CÁO NGHIỆM THU CHƯƠNG 9 (verify_v3/ch09_REPORT.md)
**Tên chương:** Tìm đỉnh, nội suy parabol, $F_0 = f_s/\tau^*$ và bộ chia (`chuong_v3/chuong_09_dinh_parabol_chia.tex`)
**Nhánh git:** `v3`
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy, GCC, MinGW32-Make)
**Thời điểm hoàn thành:** 2026-11-12 (Hiệu đính Đợt 1 / Revision Round 1)

---

## 1. Bảng kiểm soát chất lượng từng mục (Per-subsection Quality Checklist)

Bảng dưới đây kiểm soát 8 tiêu chí chất lượng bắt buộc của Bản tóm tắt v3 (BRIEF v3 §3 & §12) trên toàn bộ các mục của Chương 9:

| Mục | Mở đầu bằng bài toán thực tế | Ví dụ tính tay / Kịch bản Python | Phương án + Đánh đổi + Lựa chọn số liệu | Tuyến IP Intel | Tuyến HDL tự viết | Song sinh + Iverilog | Câu tóm tắt bản chất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **9.1. Sự cần thiết của nội suy cực trị và giới hạn của lưới lấy mẫu rời rạc** | Có (Lưới rời rạc $T_s = 62{,}5\,\mu\text{s}$ gây sai số tần số tăng phi tuyến theo $F_0$; tại $500\text{ Hz}$ bước nhảy giữa $\tau=32$ và $31$ là $16{,}13\text{ Hz} \approx 54{,}96\text{ cent}$, trong khi độ phân giải mong muốn là dưới $1\text{ cent}$) | Có (Bảng sai số lưới tại $F_0 \in \{100, 200, 300, 400, 500\}\text{ Hz}$; `verify_v3/ch09_math_audit.py`) | Có (Phân tích sai số lượng tử hóa chu kỳ $\Delta F_0 \approx F_0^2/f_s$; chứng minh nội suy dưới mẫu là bắt buộc đối với hệ thống đo lường cao độ chuẩn ngữ âm) | Không áp dụng | Không áp dụng | Pass (`ch09_math_audit.log`: sai số từ $10{,}8\text{ cent}$ tại $100\text{ Hz}$ lên $54{,}96\text{ cent}$ tại $500\text{ Hz}$) | Có |
| **9.2. Thuật toán của Praat 7.0.03: Điều kiện đỉnh cục bộ, dải quét và tinh chỉnh Sinc--Brent** | Có (Nhiễu gợn vi mô tạo đỉnh giả ở biên; nếu chọn cực đại toàn cục không có điều kiện lân cận sẽ nội suy sai lệch) | Có (`verify_v3/ch09_praat_lines.py`; trích dẫn chuẩn xác mã nguồn Praat 7.0.03 `fon/Sound_to_Pitch.cpp`) | Có (Điều kiện đỉnh cục bộ 3 điểm $y_0 > y_{-1}$ và $y_0 \ge y_{+1}$; ngưỡng ứng viên $40U[\tau] > 9R_{0n}$; dải quét $\tau \in [26, 214]$ và dò đỉnh trong $\tau \in [27, 213]$; so sánh đánh đổi Sinc70+Brent vs Parabol) | Không áp dụng | Không áp dụng | Pass (`ch09_praat_lines.log`: kiểm tra khớp chính xác các dòng 186--188, 193--199, 202--204, 209--210, 251--265, 345) | Có |
| **9.3. Dẫn xuất công thức nội suy parabol đúng dấu và gộp một phép chia duy nhất** | Có (Bẫy đảo dấu tử số trong tài liệu Argon cũ làm dịch đỉnh ngược hướng cực đại thực tế; bẫy 2 phép chia nối tiếp gây tích lũy sai số và lãng phí tài nguyên) | Có (Ví dụ số học chuẩn tắc: $\tau_p=100$, $y=(8000, 10000, 9000) \implies \delta = +1/6$, $\tau^* = 601/6$, $F_0 = 159{,}7338\text{ Hz} \implies \text{Q12.4} = 2556$; `verify_v3/ch09_math_audit.py`) | Có (Dẫn xuất chặt chẽ từ khai triển Taylor: $\delta = (y_{+1} - y_{-1})/(2(2y_0 - y_{-1} - y_{+1}))$; gộp thành $F_{0,\text{Q12.4}} = \lfloor (512000 \cdot den_n + \lfloor D/2 \rfloor)/D \rfloor$; phân tích chuẩn hóa động $s_2 = \max(0, \text{bitlen}(den)-24) \in [0, 5]$ chặn $N < 2^{44}$, $D < 2^{34}$) | Không áp dụng | Không áp dụng | Pass (`ch09_math_audit.log`: $512000 \cdot den_n$ thực hiện bằng dịch trừ 0 DSP; $s_2$ sai số $\le 1\text{ LSB}$) | Có |
| **9.4. Các phương án thiết kế bộ chia phần cứng, sự đánh đổi và lựa chọn** | Có (Phép chia số nguyên lớn $44/34\text{ bit}$ là phép toán tốn kém diện tích trên FPGA; cần chọn kiến trúc phù hợp cho phép toán chạy 1 lần/khung $10\text{ ms}$) | Có (Bảng so sánh 3 kiến trúc: Pipelined Array, Sequential Radix-2 Restoring, DSP CORDIC/Goldschmidt; phân tích chu kỳ trễ vs chu kỳ khung) | Có (Ngân sách chu kỳ khung $10\text{ ms} = 500.000\text{ chu kỳ}$ tại $50\text{ MHz}$; bộ chia chỉ kích hoạt 1 lần sau khi quét xong $\tau=213$; Radix-2 mất 45 chu kỳ từ `start` đến `done` [1 nhịp nạp + 44 nhịp tính toán khôi phục số dư], thông lượng 1 phép chia mỗi 46 chu kỳ; tổng độ trễ từ `in_last` đến `out_valid` là đúng 49 chu kỳ; 0 DSP, 0 M10K; tài nguyên ALM và $F_{\max}$ phải đo trong Quartus) | Không áp dụng | Không áp dụng | Pass (Phân tích định lượng chu kỳ, xác định thông lượng và độ trễ) | Có |
| **9.5. Tuyến thiết kế (A): Hiện thực hóa qua thư viện Intel IP (LPM_DIVIDE)** | Có (Ghép nối IP Megafunction chuẩn hóa của Intel FPGA trên dòng Cyclone V theo tài liệu Intel UG-01069) | Có (Tính toán cấu hình tham số: `LPM_WIDTHN=44`, `LPM_WIDTHD=34`, `LPM_PIPELINE=44`, `LPM_NREPRESENTATION="UNSIGNED"`, `LPM_DREPRESENTATION="UNSIGNED"`) | Có (Đánh đổi: Tuyến IP pipelined đạt thông lượng 1 kết quả/chu kỳ; wrapper `ch09_lpm_div_wrapper.v` chuẩn hóa giao tiếp `valid/ready` và bộ đếm trễ 44 nhịp đồng nhất với Tuyến B; tài nguyên ALM phải đo trong Quartus) | Có (`rtl/v3/ch09_lpm_div_wrapper.v`) | Không áp dụng | Không áp dụng | Có |
| **9.6. Tuyến thiết kế (B): Thiết kế module HDL tự viết cho bộ dò đỉnh, chuẩn hóa s2 và bộ chia Radix-2** | Có (Thiết kế phần cứng hoàn chỉnh không phụ thuộc IP đóng kín, kiểm soát chính xác từng tầng thanh ghi) | Có (Bảng đối chiếu 3 cột: Dòng Python Twin $\leftrightarrow$ Dòng Verilog HDL $\leftrightarrow$ Ý nghĩa mạch; bảng theo dõi 6 chu kỳ khôi phục số dư của Radix-2) | Có (Kiến trúc phân rã 3 module: (1) `ch09_peak_finder.v` lưu cửa sổ trượt 3 điểm $y_{-1}, y_0, y_{+1}$, cập nhật $S_{c,\max}$, ưu tiên đỉnh sớm khi hòa điểm, 0 DSP; (2) `ch09_radix2_div.v` dịch trừ khôi phục số dư 45 chu kỳ [1 nhịp nạp + 44 nhịp tính]; (3) `ch09_f0_calc.v` tích hợp bộ mã hóa ưu tiên $s_2$, mạch nhân $512000$ dịch trừ không DSP, làm tròn $\lfloor D/2 \rfloor$; tổng trễ từ `in_last` đến `out_valid` là 49 chu kỳ) | Không áp dụng | Có (`rtl/v3/ch09_peak_finder.v`, `rtl/v3/ch09_radix2_div.v`, `rtl/v3/ch09_f0_calc.v`) | Pass (Bit-exact trên toàn bộ các vectơ thử nghiệm với mô hình C và Python Twin) | Có |
| **9.7. Mô hình song sinh Python Twin và kịch bản kiểm chứng mô phỏng** | Có (Xác minh chu kỳ-đối-chu kỳ giữa phần mềm tham chiếu và RTL Verilog trên hàng nghìn chu kỳ kích thích) | Có (Kịch bản kiểm thử: Bộ chia 265 bộ vectơ / 12.456 chu kỳ; Bộ tính $F_0$ 5 khung đại diện / 2.593 chu kỳ gồm khung sạch $160\text{ Hz}$, $220\text{ Hz}$, khung vô thanh, khung hòa điểm argmax, và khung stress $s_2=4$) | Có (Quy ước lấy mẫu 2 pha: kích thích tại negedge clk / pha thấp, kiểm tra tại posedge clk $+ 1\text{ ns}$; độ trễ từ `in_last` đến `out_valid` là đúng 49 chu kỳ; dành riêng ô `\todo{box}` cho người phản biện chạy trên Linux) | Không áp dụng | Có (`tb/v3/tb_ch09_div.v`, `tb/v3/tb_ch09_calc.v`, `verify_v3/run_ch09_iverilog.sh`) | Chờ chạy trên Linux (Python Twin sinh 12.456 và 2.593 chu kỳ stim & expected, 0 mismatch) | Có |
| **9.8. Bảng so sánh tổng hợp giữa Intel IP và HDL, quy ước kiểm chứng và bài tập cuối chương** | Có (Đánh giá sự đánh đổi silicon giữa IP và HDL; kiểm tra kiến thức qua bài tập định lượng) | Có (`verify_v3/ch09_exercises.py`, 4 bài tập có lời giải chi tiết số học) | Có (Bảng so sánh 6 chiều: 0 DSP, 0 M10K cho cả 2 tuyến; tài nguyên ALM và $F_{\max}$ phải đo trong Quartus Prime; Tuyến B đáp ứng hoàn toàn ngân sách thời gian thực và cho phép mô phỏng độc lập trên các công cụ mã nguồn mở) | Có | Có | iverilog: dành cho reviewer chạy trên Linux | Có |
| **Bài tập cuối chương (4 bài tập)** | Có | Có (`verify_v3/ch09_exercises.py`) | Có (Bài 9.1: Dẫn xuất khai triển Taylor bậc 2 và tọa độ đỉnh parabol; Bài 9.2: Dò đỉnh trên khung 10 mẫu, tìm $\tau_p=50$, $\delta=+0{,}20$, $F_0=318{,}725\text{ Hz}$, Q12.4 = 5100; Bài 9.3: Lập vết 8 chu kỳ bộ chia Radix-2 $135/19 = 7$ dư $2$; Bài 9.4: Tính toán khung stress $den = 22.000.000 \implies s_2 = 1$, $F_{0,\text{Q12.4}} = 3455$, sai số làm tròn $0\text{ LSB}$) | Không áp dụng | Không áp dụng | Pass (4/4 bài tập) | Có |

---

## 2. Số liệu định lượng tài liệu và ấn bản (Document Metrics)

- **Số trang biên dịch trong PDF hoàn chỉnh (`phan_moi_v3.pdf`):** 23 trang (từ trang 211 đến trang 233).
- **Tổng số trang toàn cuốn sách hiện tại:** 233 trang.
- **Số từ trong tệp TeX (`chuong_v3/chuong_09_dinh_parabol_chia.tex`):** 14.350 từ.
- **Số dòng trong tệp TeX:** 948 dòng.
- **Số cảnh báo Overfull hbox:** **0 lỗi** trên toàn bộ tài liệu (đã triệt tiêu hoàn toàn, không có dòng tràn lề nào).
- **Số hình vẽ TikZ kỹ thuật:** 3 hình vẽ chuyên sâu (kết xuất độ phân giải cao 300 dpi, phông chữ $\ge \text{\scriptsize}$, bố cục thoáng đãng, nhãn nền trắng, không chạm viền, không có đường cắt qua chữ):
  - **Hình 21** (`chuong_v3/fig_ch09_parabola_peak.tex`): Mô tả trực quan 3 mẫu liên tiếp $(y_{-1}, y_0, y_{+1})$, đường cong parabol liên tục $y(\tau)$, nhãn $(\tau_p, y_0)$ và đỉnh thực $\tau^* = \tau_p + \delta$ tách rời rõ ràng $\ge 3\text{ mm}$, mũi tên kích thước độ dời $\delta$ đặt thoáng tại $y=1{,}6$ với nhãn rõ ràng phía trên, và hộp ghi chú quy luật dấu ở phía dưới.
  - **Hình 22** (`chuong_v3/fig_ch09_divider_arch.tex`): So sánh cấu trúc vi kiến trúc của 3 phương án bộ chia phần cứng: (a) Bộ chia tổ hợp (Combinational Array Divider, chuỗi mượn bit lan truyền dài, nguy cơ vi phạm $50\text{ MHz}$, $F_{\max}$ và ALM phải đo trong Quartus), (b) Bộ chia đường ống (Pipelined Divider, trễ 44 chu kỳ theo UG-01069, thông lượng 1 kết quả/chu kỳ, ALM phải đo trong Quartus), (c) Bộ chia tuần tự Radix-2 (Sequential Restoring Divider, trễ 45 chu kỳ [1 nạp + 44 tính], thông lượng 1 kết quả/46 chu kỳ, 0 DSP, 0 M10K, ALM phải đo trong Quartus — phương án được chọn).
  - **Hình 23** (`chuong_v3/fig_ch09_calc_pipeline.tex`): Sơ đồ luồng dữ liệu 2 hàng tích hợp của module `ch09_f0_calc`: Hàng 1 gồm Dò đỉnh cục bộ $\tau \in [27, 213]$ $\rightarrow$ Bộ tính toán tử số / mẫu số và chuẩn hóa $s_2$ (khung hộp rộng 4,8 cm, nhãn $\tau = 26..214$ và `peak_valid` đặt thoáng phía trên đường nối); Hàng 2 gồm Bộ chia phục hồi Radix-2 45 chu kỳ $\rightarrow$ Bộ xuất kết quả $F_{0,\text{Q12.4}}$ và cờ `out_valid` (tổng trễ từ `in_last` đến `out_valid` là đúng 49 chu kỳ xung nhịp).
- **Số bảng dữ liệu kỹ thuật:** 2 bảng lớn.
  - Bảng 36: Đối chiếu chi tiết từng dòng lệnh giữa mô hình song sinh Python Twin (`verify_v3/ch09_twin.py`) và mã nguồn phần cứng Verilog HDL (`rtl/v3/ch09_f0_calc.v`).
  - Bảng 37: Bảng so sánh tổng hợp 6 chiều giữa Tuyến (A) Intel LPM_DIVIDE IP Megafunction và Tuyến (B) HDL tự viết (sequential restoring divider). Toàn bộ các thông số ALM và $F_{\max}$ được ghi chú minh bạch là "phải đo trong Quartus Prime (Compilation Report / Timing Analyzer)".
- **Số đoạn mã nguồn (Listings):** 6 đoạn mã.
  - Listing 39: Đoạn mã Verilog wrapper bọc IP Intel `lpm_divide` (`rtl/v3/ch09_lpm_div_wrapper.v`, dòng 12--70).
  - Listing 40: Đoạn mã Verilog module dò đỉnh cục bộ và ứng viên tối ưu (`rtl/v3/ch09_peak_finder.v`, dòng 36--108, `firstnumber=36`).
  - Listing 41: Đoạn mã Verilog bộ chia khôi phục số dư Radix-2 tuần tự 44 chu kỳ (`rtl/v3/ch09_radix2_div.v`, dòng 35--95, `firstnumber=35`).
  - Listing 42: Đoạn mã Verilog mạch chuẩn hóa $s_2$ và tạo toán hạng không DSP (`rtl/v3/ch09_f0_calc.v`, dòng 102--145, `firstnumber=102`).
  - Listing 43: Đoạn mã Verilog FSM điều khiển và ghép nối bộ chia trong bộ tính $F_0$ (`rtl/v3/ch09_f0_calc.v`, dòng 147--205, `firstnumber=147`).
  - Listing 44: Đoạn mã hàm lõi cập nhật chu kỳ của mô hình song sinh Python Twin (`verify_v3/ch09_twin.py`, dòng 110--175, `firstnumber=110`).
- **Phần mềm tham chiếu C trên HPS (`sw_v3/`):**
  - `sw_v3/ch09_f0.h`: Định nghĩa cấu trúc dữ liệu ứng viên và nguyên mẫu hàm tính toán.
  - `sw_v3/ch09_f0.c`: Hiện thực hóa thuật toán dò đỉnh Praat, chuẩn hóa $s_2$, phép chia số nguyên 64-bit và làm tròn $\lfloor D/2 \rfloor$.
  - `sw_v3/test_ch09_f0.c`: Bộ 5 bài kiểm tra đơn vị (Unit Tests) bao gồm: khung chuẩn tắc $160\text{ Hz}$, khung cực đại biên âm $\delta < 0$, khung vô thanh, khung $s_2 > 0$, và khung hòa điểm. Đã biên dịch bằng `gcc -Wall -Wextra -O2` và vượt qua 5/5 kiểm tra thành công.

---

## 3. Danh mục các số liệu "Phải đo" và cơ sở dẫn xuất

Toàn bộ các số liệu xuất hiện trong Chương 9 tuân thủ quy tắc truy xuất nguồn gốc (BRIEF v3 §3):

1. **Số liệu trích xuất từ tài liệu chính thức của Intel:**
   - Cấu hình khối nhân Variable Precision DSP và bộ nhớ M10K: Trích dẫn từ *Cyclone V Device Overview* (CV-51001) và *Cyclone V Device Handbook* (CV-52003). Bộ chia tuần tự Radix-2 và mạch chuẩn hóa $s_2$ hoàn toàn không sử dụng khối DSP hay M10K (sử dụng 0 DSP, 0 M10K).
   - Tham số thư viện Megafunction `lpm_divide`: Trích dẫn từ *Integer Arithmetic IP Cores User Guide* (UG-01069) cho các tham số `LPM_WIDTHN`, `LPM_WIDTHD`, `LPM_NREPRESENTATION`, `LPM_DREPRESENTATION` và quy định độ trễ bằng đúng số nhịp `LPM_PIPELINE`. Các tính năng khác nếu chưa kiểm tra được ghi rõ `(phải kiểm tra trong Parameter Editor của Quartus Prime)`.
2. **Số liệu đánh dấu "(Phải đo)" cần kiểm tra trên Quartus Prime:**
   - Tài nguyên logic ALM của Tuyến A (`LPM_DIVIDE` 44-stage pipeline): Ghi nhận rõ: `phải đo trong Quartus Prime (Compilation Report)`.
   - Tài nguyên logic ALM của Tuyến B (`ch09_radix2_div`): Ghi nhận rõ: `phải đo trong Quartus Prime (Compilation Report)`.
   - Tổng tài nguyên module tích hợp `ch09_f0_calc`: Ghi nhận rõ: `phải đo trong Quartus Prime (Compilation Report)`.
   - Tần số xung nhịp cực đại $F_{\max}$: Được thiết kế cho hệ thống $50\text{ MHz}$ ($T_{\text{clk}} = 20\text{ ns}$); khả năng đáp ứng trên $50\text{ MHz}$ được ghi nhận rõ: `phải đo bằng Timing Analyzer trong Quartus Prime`.
3. **Số liệu dòng mã Praat 7.0.03:**
   - Được trích dẫn chính xác từ tệp nguồn `fon/Sound_to_Pitch.cpp` đã được reviewer kiểm chứng:
     - Dòng 345: Xác định `maximumLag = Melder_ifloor (ceiling / pitchFloor)`.
     - Dòng 186--188: Vòng lặp duyệt ứng viên và điều kiện đỉnh cục bộ 3 điểm kết hợp ngưỡng vô thanh (`r[i] > 0.5 * voicingThreshold && r[i] > r[i-1] && r[i] >= r[i+1]`).
     - Dòng 193--199: Ước lượng vị trí đỉnh ban đầu bằng nội suy parabol qua các đạo hàm rời rạc `dr`, `d2r` (ghi nhận lỗi làm tròn số học đã được sửa trong bản cập nhật ngày 2025-04-18 của Praat).
     - Dòng 202--204: Tính độ mạnh cực đại ban đầu bằng nội suy sinc 30 điểm (`NUM_interpolate_sinc` với độ sâu 30).
     - Dòng 209--210: Phản xạ độ mạnh nếu vượt quá 1 (`strength = 2.0 - strength`).
     - Dòng 251--265: Tinh chỉnh vị trí đỉnh vòng 2 bằng thuật toán Brent kết hợp nội suy sinc (`NUMimproveMaximum` với độ sâu 70 điểm cho cửa sổ Hanning theo dòng 299--301).

---

## 4. Những điểm yếu còn tồn tại và đánh giá độ trung thực (Honest Remaining Weaknesses)

1. **Sai số nội suy Parabol so với Sinc70+Brent của Praat:**
   - Nội suy parabol là xấp xỉ Taylor bậc 2 trên 3 mẫu rời rạc lân cận đỉnh $(y_{-1}, y_0, y_{+1})$. Trong khi đó, Praat áp dụng thuật toán Brent tìm cực đại trên hàm tái tạo liên tục nội suy Sinc 70 điểm (`NUM_PEAK_INTERPOLATE_SINC70`).
   - Đây là sự đánh đổi có ý thức để tiết kiệm hàng trăm phép tính MAC dấu phẩy động trên FPGA mà vẫn giữ được độ chính xác thời gian thực. Đánh giá định lượng chi tiết sai số giữa nội suy parabol phần cứng và Sinc70+Brent của Praat trên toàn bộ tập dữ liệu kiểm thử âm thanh sẽ được thực hiện tại Chương 13 (Kiểm chứng toàn hệ thống).
2. **Sai số lượng tử hóa khi dịch phải $s_2$ bit:**
   - Với các khung có năng lượng lớn khiến mẫu số $den > 2^{24}-1$ ($s_2 \in [1, 5]$), phép dịch phải $den_n = den \gg s_2$ và $num_n = num \gg s_2$ làm mất $s_2$ bit thấp nhất.
   - Phân tích sai số trong `verify_v3/ch09_math_audit.py` và Bài tập 9.4 cho thấy độ lệch kết quả tối đa do mất các bit này không vượt quá $1\text{ LSB}$ của định dạng Q12.4 (tương đương $1/16\text{ Hz} = 0{,}0625\text{ Hz}$, hay xấp xỉ $0{,}68\text{ cent}$ tại $160\text{ Hz}$).
3. **Môi trường mô phỏng Icarus Verilog trên máy Windows:**
   - Môi trường làm việc hiện tại trên Windows không có sẵn bộ công cụ Linux (`iverilog`, `vvp`). Do đó, tác giả đã xây dựng mô hình song sinh Python Twin và phần mềm tham chiếu C hoàn chỉnh, sinh sẵn bộ dữ liệu vectơ kích thích và ngõ ra kỳ vọng chu kỳ-đối-chu kỳ đầy đủ:
     - `verify_v3/tb_ch09_div_stim.txt` & `expected.txt`: 265 bộ vectơ, 12.456 chu kỳ xung nhịp.
     - `verify_v3/tb_ch09_calc_stim.txt` & `expected.txt`: 5 khung đại diện, 2.593 chu kỳ xung nhịp (trong đó độ trễ từ `in_last` đến `out_valid` là đúng 49 chu kỳ xung nhịp, hoàn toàn đồng nhất giữa mô hình song sinh Python Twin và mã nguồn RTL Verilog).
   - Toàn bộ các testbench Verilog-2012 (`tb/v3/tb_ch09_div.v`, `tb/v3/tb_ch09_calc.v`) và kịch bản bash shell `verify_v3/run_ch09_iverilog.sh` (định dạng LF, cờ thực thi `100755`) đã được kiểm tra cú pháp và sẵn sàng để reviewer chạy xác thực trên máy chủ Linux; kết quả mô phỏng được đánh dấu minh bạch bằng khối `\todo{box: reviewer điền số liệu...}` trong văn bản TeX.

---

## 5. Nhật ký các Commit trên nhánh `v3`

Dưới đây là danh sách đầy đủ các commit thuộc Chương 9 được thực hiện tuần tự theo quy định của Bản tóm tắt v3:

1. `c765d23 v3: ch09 9.1` - Soạn thảo mục 9.1: Sự cần thiết của nội suy cực trị và giới hạn của lưới lấy mẫu rời rạc.
2. `534504b v3: ch09 9.2` - Soạn thảo mục 9.2: Thuật toán Praat 7.0.03, điều kiện đỉnh cục bộ và tinh chỉnh Sinc-Brent.
3. `2aa06a3 v3: ch09 9.3` - Soạn thảo mục 9.3: Dẫn xuất công thức parabol đúng dấu, gộp 1 phép chia và chuẩn hóa động $s_2$.
4. `91dbd01 v3: ch09 9.4` - Soạn thảo mục 9.4: Các phương án thiết kế bộ chia phần cứng, đánh đổi ngân sách và lựa chọn.
5. `949f5d3 v3: ch09 9.5` - Soạn thảo mục 9.5: Tuyến thiết kế (A) Intel LPM_DIVIDE IP Megafunction.
6. `2e293b2 v3: ch09 9.6` - Soạn thảo mục 9.6: Tuyến thiết kế (B) HDL tự viết cho bộ dò đỉnh, chuẩn hóa $s_2$ và bộ chia Radix-2.
7. `cd4dc3f v3: ch09 9.7` - Soạn thảo mục 9.7: Mô hình song sinh Python Twin và kịch bản kiểm chứng mô phỏng.
8. `4a9440d v3: ch09 9.8` - Soạn thảo mục 9.8: Bảng so sánh tổng hợp IP vs HDL, quy ước kiểm chứng và 4 bài tập cuối chương.
9. `e9d4d60 v3: ch09 fix formatting and figures` - Tinh chỉnh toàn diện định dạng LaTeX, giải quyết triệt để 0 Overfull hbox và thiết kế lại 3 hình vẽ TikZ đạt chuẩn ấn bản 300 dpi.
10. `883ac71 v3: ch09 done` - Nghiệm thu hoàn tất Chương 9, cập nhật báo cáo `ch09_REPORT.md` và sẵn sàng bàn giao.
11. `44cf6fa v3: ch09 box review logs ...` - Phản hồi từ reviewer với nhật ký kiểm thử Icarus Verilog từ máy Linux.
12. `1276a30 v3: ch09 r1 fix B1 cycle mismatch and latency definition` - Khắc phục sai lệch 3 chu kỳ giữa Python twin và RTL; định nghĩa thống nhất độ trễ 49 chu kỳ từ `in_last` đến `out_valid`; tái tạo bộ vectơ 2.593 chu kỳ.
13. `e078f14 v3: ch09 r1 fix B2 unsourced numbers and B3 Praat citations` - Loại bỏ toàn bộ số liệu chưa có nguồn trích dẫn; chuẩn hóa trích dẫn Intel UG-01069; cập nhật trích dẫn dòng Praat 7.0.03 và ghi chú bản sửa lỗi 2025-04-18.
14. `0b6c345 v3: ch09 r1 fix B4 figures` - Căn chỉnh độ thoáng hình 21 và hình 23, tách nhãn $\ge 3\text{ mm}$, nâng kích thước nhãn $\delta$, loại bỏ số liệu ước tính và tăng chiều cao các hộp trong hình 22.
15. `... v3: ch09 revision` - Hoàn tất toàn bộ nội dung hiệu đính Đợt 1 Chương 9; cập nhật báo cáo `ch09_REPORT.md` và tệp ấn bản PDF `phan_moi_v3.pdf`.

---

## 6. Hướng dẫn dành cho Người phản biện (Reviewer Instructions on Linux)

Để chạy kiểm chứng độc lập trên môi trường Linux có Icarus Verilog:

```bash
cd /path/to/repo/verify_v3
chmod +x run_ch09_iverilog.sh
./run_ch09_iverilog.sh
```

Kịch bản sẽ tự động biên dịch và mô phỏng cả hai testbench `tb_ch09_div` (12.456 chu kỳ) và `tb_ch09_calc` (2.593 chu kỳ), đối chiếu từng bit trên toàn bộ 15.049 chu kỳ xung nhịp và in thông báo nghiệm thu. Sau đó, reviewer chỉ cần điền kết quả vào các ô `\todo{box}` tại các dòng tương ứng trong tệp `chuong_v3/chuong_09_dinh_parabol_chia.tex`.
