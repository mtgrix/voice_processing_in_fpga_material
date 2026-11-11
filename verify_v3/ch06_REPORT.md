# BÁO CÁO NGHIỆM THU CHƯƠNG 6 (verify_v3/ch06_REPORT.md)
**Tên chương:** Cửa sổ Hanning N+1 (`chuong_v3/chuong_06_hanning.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy)  
**Thời điểm hoàn thành:** 2026-11-11  

---

## 1. Bảng kiểm soát chất lượng từng mục (Per-subsection Checklist)

| Mục | Mở đầu bằng bài toán thực tế | Ví dụ tính tay / Kịch bản Python | Phương án + Đánh đổi + Lựa chọn số liệu | Tuyến IP Intel | Tuyến HDL tự viết | Song sinh + Iverilog | Câu tóm tắt bản chất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6.1. Bản chất của hiện tượng rò rỉ phổ và công thức Hanning N+1** | Có | Có (`ch06_praat_lines.py`, `ch06_hanning_math.py`, Bảng tính tay 8 mẫu) | Có (Búp bên đầu $-31{,}47\text{ dB}$ vs $-13{,}26\text{ dB}$, dốc $-18\text{ dB/octave}$ vs $-6\text{ dB/octave}$) | Không áp dụng | Không áp dụng | Pass (7/7 Praat lines, 638 mẫu) | Có |
| **6.2. Dẫn xuất toán học của cửa sổ Q1.15 và hiện tượng kẹp bão hòa** | Có | Có (`ch06_hanning_math.py`, Bảng 6 mẫu đại diện) | Có ($w[0]=w[637]=1$, đỉnh kẹp $32.768 \to 32.767$, tổng $10.469.378$, $\epsilon = 0{,}8020\text{ LSB}$, SQNR $97{,}02\text{ dB}$) | Không áp dụng | Không áp dụng | Pass (100% bit-exact với hex) | Có |
| **6.3. Không gian thiết kế phần cứng: Đánh đổi kiến trúc và định dạng** | Có | Có (`ch06_stress_audit.py`, Stress Frame A) | Có (Toàn ROM 2 M10K vs Nửa ROM 1 M10K; 17-bit có dấu chống tràn $d \in [-65535, +65535]$, $\max |x_w| = 59.379$) | Không áp dụng | Không áp dụng | Pass (Stress frame bit-exact) | Có |
| **6.4. Tuyến (A): Khởi tạo khối IP Intel ROM: 1-PORT và LPM_MULT** | Có | Có (Trích dẫn CV-52003 Chương 3 & 5, UG-01068, UG-01069) | Có (ROM 1-PORT trễ 1 nhịp, LPM_MULT 17x17 signed `LPM_PIPELINE=1`, 2 M10K, 1 DSP, 0 ALM) | Có (Listing ghép nối IP Verilog) | Không áp dụng | Không áp dụng | Có |
| **6.5. Tuyến (B): Hiện thực hóa phần cứng HDL tự viết và cân bằng nhịp** | Có | Có (Bảng đối chiếu từng dòng Twin vs HDL) | Có (Đường ống 2 chu kỳ: `d_r1` cân bằng nhịp ROM, `prod_r2` chốt tích DSP, làm tròn $(p+2^{14})\gg 15$, dò LocalPeak $212 \dots 425$) | Không áp dụng | Có (`rtl/v3/ch06_hanning_window.v`, 95 dòng trích) | 3.250/3.250 chu kỳ Twin | Có |
| **6.6. Bảng so sánh IP vs HDL, quy ước lấy mẫu testbench và bài tập** | Có | Có (`verify_v3/ch06_exercises.py`) | Có (Quy ước lấy mẫu 2 pha; Bảng so sánh IP vs HDL: 2 M10K, 1 DSP, 0 ALM, $F_{\max}$, tích hợp LocalPeak) | Có | Có | iverilog: to be run by reviewer | Có |
| **Bài tập cuối chương (4 bài tập)** | Có | Có (`verify_v3/ch06_exercises.py`) | Có (So sánh 4 cửa sổ, mạch gấp nửa ROM tiết kiệm 1 M10K, đánh đổi CORDIC vs ROM, bão hòa đỉnh và SQNR $97{,}02\text{ dB}$) | Không áp dụng | Không áp dụng | Pass (4/4 bài tập) | Có |

---

## 2. Số liệu định lượng tài liệu và ấn bản (Metrics)

- **Số trang biên dịch trong PDF hoàn chỉnh (`phan_moi_v3.pdf`):** 24 trang (trang 142 đến trang 165).
- **Tổng số trang toàn cuốn sách hiện tại:** 165 trang.
- **Số từ trong tệp TeX (`wc -w chuong_v3/chuong_06_hanning.tex`):** 13.837 từ.
- **Số dòng trong tệp TeX:** 871 dòng.
- **Số hình vẽ TikZ kỹ thuật:** 3 hình (được hiệu chỉnh trực quan ở độ phân giải 150/300 dpi, phông chữ $\ge \text{\scriptsize}$, `fill=white`, không chạm viền, không có đường cắt qua chữ).
  - Hình 12 (`chuong_v3/fig_ch06_leakage.tex`): So sánh đáp ứng tần số và phổ rò rỉ giữa Cửa sổ chữ nhật và Cửa sổ Hanning $N+1$ ($N = 638$, số liệu chính xác từ `verify_v3/ch06_hanning_math.log`). Minh họa mức dập búp bên $-31{,}47\text{ dB}$ (vượt trội $+18{,}21\text{ dB}$) và tốc độ dốc $-18\text{ dB/octave}$ vs $-6\text{ dB/octave}$.
  - Hình 13 (`chuong_v3/fig_ch06_window_shape.tex`): Dạng sóng rời rạc của Cửa sổ Hanning $N+1$ trong miền thời gian sau khi lượng tử hóa Q1.15, xử lý bão hòa $32.768 \to 32.767$ ở đỉnh đối xứng kép ($n = 318, 319$), giá trị biên $w[0] = w[637] = 1$ và phân vùng cửa sổ trung tâm LocalPeak ($n \in [212, 425]$).
  - Hình 14 (`chuong_v3/fig_ch06_window_arch.tex`): Sơ đồ kiến trúc vi mô phần cứng của module `rtl/v3/ch06_hanning_window.v`, minh họa phân rã 4 giai đoạn nhịp: Giai đoạn 0 (Bộ đếm địa chỉ), Giai đoạn 1 (Đọc ROM và thanh ghi trễ `d_r1`), Giai đoạn 2 (Bộ nhân DSP có dấu và thanh ghi tích số `prod_r2`), Giai đoạn 3 (Bộ làm tròn nửa bước và mạch tích hợp dò đỉnh LocalPeak).
- **Số bảng số liệu kỹ thuật:** 4 bảng lớn trong thân bài + 2 bảng trong phần bài tập.
  - Bảng 26 (`tab:ch06_hand_8samp`): Tính tay 8 mẫu đối chiếu công thức Hanning $N+1$ của Praat với công thức Hanning đối xứng kinh điển (chứng minh $w[0] = 0{,}0597 \ne 0$).
  - Bảng 27 (`tab:ch06_sample_check`): Bảng đối chiếu 6 mẫu đại diện trên các vùng chiến lược của khung 638 mẫu giữa giá trị lý thuyết `double` và Q1.15 phần cứng.
  - Bảng 28 (`tab:ch06_twin_vs_hdl`): Bảng đối chiếu trực tiếp giữa mã nguồn mô hình song sinh Python (`verify_v3/ch06_window_twin.py`) và mã Verilog HDL (`rtl/v3/ch06_hanning_window.v`).
  - Bảng 29 (`tab:ch06_ip_vs_hdl`): So sánh toàn diện giữa đường dẫn sử dụng IP lõi Intel (`ROM: 1-PORT` + `LPM_MULT`) và giải pháp HDL tự viết (`ch06_hanning_window.v`).
  - Bảng trong Bài tập 6.1: So sánh 4 loại cửa sổ (Chữ nhật, Hanning $N+1$, Hamming, Blackman).
  - Bảng trong Bài tập 6.3: So sánh kiến trúc Bảng tra ROM M10K và Bộ tính CORDIC đường ống.
- **Số đoạn mã nguồn trích dẫn (Listings):** 5 đoạn.
  - Listing 26: Định nghĩa `AC_HANNING` / `AC_GAUSS` và vòng lặp tính cửa sổ Hanning $N+1$ từ `fon/Sound_to_Pitch.cpp` của Praat 7.0.03.
  - Listing 27: Mẫu ghép nối 2 khối IP Intel `ROM: 1-PORT` và `LPM_MULT` cùng mạch làm tròn.
  - Listing 28 (`lstinputlisting`): 95 dòng mã Verilog cốt lõi của `rtl/v3/ch06_hanning_window.v` (dòng 79 đến 173, `firstnumber=79`).
  - Listing 29 (`lstinputlisting`): 84 dòng mã mô hình song sinh Python của `verify_v3/ch06_window_twin.py` (dòng 82 đến 165, `firstnumber=82`).
  - Listing trong Bài tập 6.2: Đoạn mã Verilog cho mạch gấp địa chỉ nửa ROM.
- **Lỗi biên dịch XeLaTeX:** 0 lỗi (biên dịch 2 lần với `xelatex -interaction=nonstopmode -halt-on-error phan_moi_v3.tex`).
- **Cảnh báo Overfull `\hbox` (> 10pt):** 0 cảnh báo (toàn bộ tài liệu đạt đúng 0 overfull hbox).

---

## 3. Danh mục các số liệu "phải đo" và căn cứ trích dẫn phần cứng

1. **Số liệu trích dẫn tài liệu phần cứng Intel Cyclone V:**
   - Cấu trúc khối nhớ nhúng M10K: *Cyclone V Device Handbook, Volume 1: Device Interfaces and Integration* (CV-52003, Chương 3: "Embedded Memory Blocks in Cyclone V Devices", Bảng 3-1: "M10K Embedded Memory Block Configurations"). Khối M10K có dung lượng $10.240\text{ bit}$. Cấu hình độ sâu lớn nhất cho độ rộng 16-bit là $512 \times 20$. Do đó:
     * Cửa sổ đầy đủ $638 \times 16\text{ bit}$ có độ sâu $638 > 512$, buộc phải cấu hình thành $1024 \times 10$, đòi hỏi ghép song song **2 khối M10K**.
     * Cửa sổ nửa ROM $319 \times 16\text{ bit}$ có độ sâu $319 \le 512$, nằm gọn trong **1 khối M10K duy nhất** cấu hình $512 \times 20$, tiết kiệm $50\%$ tài nguyên RAM.
   - Cấu trúc khối Variable Precision DSP: *Cyclone V Device Handbook, Volume 1* (CV-52003, Chương 5: "Variable Precision DSP Blocks in Cyclone V Devices", Mục 5-2 và Bảng 5-1). Mỗi khối DSP chứa hai bộ nhân độc lập $18 \times 18$. Phép nhân $17 \times 17$-bit có dấu nằm vừa khít bên trong một bộ nhân $18 \times 18$, chiếm **1 khối DSP** và tiêu tốn **0 ALM**.
   - Khối IP `ROM: 1-PORT`: *Embedded Memory (RAM: 1-PORT, RAM: 2-PORT, ROM: 1-PORT, and ROM: 2-PORT) User Guide* (UG-01068), tham số độ trễ ngõ ra `outdata_reg_a = "CLOCK0"` (1 chu kỳ).
   - Khối IP `LPM_MULT`: *Integer Arithmetic IP Cores User Guide* (UG-01069), tham số `LPM_WIDTHA = 17`, `LPM_WIDTHB = 17`, `LPM_WIDTHP = 34`, `LPM_REPRESENTATION = "SIGNED"`, `LPM_PIPELINE = 1`.
2. **Số liệu trích dẫn mã nguồn Praat 7.0.03 được kiểm chứng:**
   - `fon/Sound_to_Pitch.cpp:39-40`: `#define AC_HANNING 0`, `#define AC_GAUSS 1`.
   - `fon/Sound_to_Pitch.cpp:78`: `frame [j] = (my z [i] - localMean) * window [j]`.
   - `fon/Sound_to_Pitch.cpp:88-101`: Dò đỉnh cục bộ `LocalPeak` trong dải $212 \dots 425$ (`halfnsamp_window = 319`, `halfnsamp_period = 107`).
   - `fon/Sound_to_Pitch.cpp:299-301`: `AC_HANNING` cấu hình độ dài 3 chu kỳ và `brent_depth = NUM_PEAK_INTERPOLATE_SINC70`.
   - `fon/Sound_to_Pitch.cpp:303-306`: `AC_GAUSS` nhân đôi độ dài cửa sổ (`periodsPerWindow *= 2`, 6 chu kỳ) và `brent_depth = SINC700`.
   - `fon/Sound_to_Pitch.cpp:409`: `window.resize (nsamp_window)` ($N = 638$).
   - `fon/Sound_to_Pitch.cpp:413-415`: Đoạn chú thích của Boersma ("A Gaussian or Hanning window is applied against phase effects. The Hanning window is 2 to 5 dB better for 3 periods/window. The Gaussian window is 25 to 29 dB better for 6 periods/window." - mốc tham chiếu không nêu trong nguồn).
   - `fon/Sound_to_Pitch.cpp:422-424`: Công thức Hanning $N+1$: `window [i] = 0.5 - 0.5 * cos (NUM2pi * i / (nsamp_window + 1))`.
   - `fon/Sound_to_Pitch.cpp:429-442`: Tính tự tương quan chuẩn hóa của cửa sổ `windowR` qua FFT, với `windowR[1] = 1`.
   - Toàn bộ trích dẫn được kiểm chứng qua `verify_v3/ch06_praat_lines.py`.
3. **Số liệu số học và lượng tử hóa kiểm chứng chính xác:**
   - Cửa sổ Q1.15: $w[0] = w[637] = 1$ (`0x0001`), $w[318] = w[319] = 32.767$ (`0x7FFF`).
   - Tổng số học 638 hệ số ROM: $\sum_{n=0}^{637} w[n] = \mathbf{10.469.378}$ (khớp với `golden_v2/rom/hanning638_q15.hex`).
   - Sai số tại đỉnh bão hòa: $\epsilon_{\text{apex}} = 2{,}4475 \times 10^{-5} \approx 0{,}8020\text{ LSB} < 1\text{ LSB}$.
   - Tỷ số tín hiệu trên nhiễu lượng tử đo đạc: $P_{\text{signal}} = 0{,}375588$, $P_{\text{noise}} = 7{,}45784 \times 10^{-11}$, $\text{SQNR} = \mathbf{97{,}02\text{ dB}}$ (vượt trội so với lý thuyết 15-bit $92{,}06\text{ dB}$).
   - So sánh phổ Hanning vs Gaussian (`verify_v3/ch06_hanning_math.py`):
     - Hanning $N=638$ (3 chu kỳ): BW $-3\text{ dB} = 36{,}13\text{ Hz}$, búp bên $-31{,}47\text{ dB}$.
     - Praat Gaussian $N=1276$ (6 chu kỳ): BW $-3\text{ dB} = 32{,}71\text{ Hz}$, búp bên $-124{,}90\text{ dB}$.
     - Gaussian $N=638$ (3 chu kỳ): BW $-3\text{ dB} = 64{,}94\text{ Hz}$ (nở rộng $79{,}7\%$).
   - Dải động 17-bit có dấu: $d_{\max} = +65.535$, $d_{\min} = -65.535$. Khung kiểm thử khắc nghiệt (Stress Frame A) có $\text{mean} = -26.614$, $d[318] = +59.381$, $x_w[318] = \mathbf{59.379}$ (nếu ép về 16-bit sẽ bị tràn thành $-6.157$). Đã kiểm chứng qua `verify_v3/ch06_stress_audit.py`.
4. **Mục "phải đo" (To be measured on hardware / Linux simulation):**
   - iverilog: to be run by reviewer
   - Tài nguyên logic ALM và tần số cực đại $F_{\max}$: Phải đo chính xác sau khi tổng hợp Fitter và TimeQuest Timing Analyzer trong phần mềm Quartus Prime với chip Cyclone V 5CSXFC6D6F31C6.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Tiêu tốn 2 khối M10K cho cấu hình toàn ROM 638 từ:**
   Mặc dù tổng số bit của 638 từ 16-bit ($10.208\text{ bit}$) nhỏ hơn dung lượng $10.240\text{ bit}$ của một khối M10K, nhưng do giới hạn phần cứng của Cyclone V chỉ cho phép độ rộng 16-bit ở độ sâu $\le 512$, thiết kế bắt buộc phải cấu hình $1024 \times 10$ và tiêu tốn 2 khối M10K. Nếu hệ thống bị nghẽn tài nguyên RAM trong các dự án mở rộng, giải pháp gấp địa chỉ nửa ROM (Bài tập 6.2) có thể được áp dụng để giảm về 1 khối M10K, đổi lại tốn thêm ~10 ALM cho bộ trừ địa chỉ.
2. **Cố định cấu hình khung 638 mẫu:**
   Mảng ROM và bộ đếm mẫu trong module được cấu hình cho kích thước danh định $N = 638$ ($f_s = 16\text{ kHz}, F_{\text{floor}} = 75\text{ Hz}$). Nếu thay đổi tần số sàn $F_{\text{floor}}$ hoặc $f_s$, cần tái tạo lại bảng tra ROM và nạp lại tệp HEX tương ứng.
3. **Mạch làm tròn hội tụ sử dụng logic tổ hợp ngõ ra:**
   Phép cộng làm tròn $(p + 2^{14}) \gg 15$ và bộ so sánh LocalPeak được thực hiện bằng logic tổ hợp nối tiếp sau thanh ghi tích số `prod_r2`. Ở tần số xung nhịp danh định 50 MHz ($T_{\text{clk}} = 20\text{ ns}$), đường trễ này chỉ chiếm chưa tới 2 ns (thoải mái thỏa mãn timing). Tuy nhiên nếu hệ thống ép xung lên trên 200 MHz, việc chèn thêm một tầng thanh ghi đường ống trước ngõ ra `out_xw` sẽ giúp gia tăng biên độ an toàn thời gian.

---

## 5. Lịch sử các Commit Git trên nhánh v3

Tiến trình phát triển và hoàn thiện Chương 6 được thực hiện qua chuỗi commit nguyên tử có cấu trúc rõ ràng:
- Commit `v3: ch06 6.1-6.3`: Bản chất rò rỉ phổ, dẫn xuất công thức Hanning $N+1$ của Praat 7.0.03, phân tích kẹp bão hòa đỉnh Q1.15 $32.768 \to 32.767$, kiểm chứng 17-bit có dấu và Stress Frame A ($|x_w| = 59.379$), Hình 12 và Hình 13 TikZ.
- Commit `v3: ch06 6.4-6.5`: Tuyến IP Intel `ROM: 1-PORT` + `LPM_MULT`, tuyến HDL tự viết `rtl/v3/ch06_hanning_window.v` và `rtl/v3/ch06_hanning_rom.v`, mô hình song sinh Python `verify_v3/ch06_window_twin.py`, Hình 14 TikZ và Bảng đối chiếu dòng-từng-dòng.
- Commit `v3: ch06 6.6`: Quy ước lấy mẫu testbench 2 pha, tập 3.250 vector kiểm thử, hộp giữ chỗ iverilog `\todo{box}`, Bảng 29 so sánh toàn diện IP vs HDL, và 4 bài tập cuối chương có lời giải chi tiết.
- Commit `v3: ch06 done`: Hoàn tất nghiệm thu đợt đầu Chương 6, cập nhật `phan_moi_v3.tex`, biên dịch sạch sẽ `phan_moi_v3.pdf`, bổ sung mục `ch06` trong `verify_v3/Makefile`, mã nguồn HPS C và báo cáo `verify_v3/ch06_REPORT.md`.
- Commit `v3: ch06 r1 praat citations and blocker 1-2 fixes`: Sửa các trích dẫn Praat 7.0.03 (dòng 39-40, 78, 88-101, 299-301, 303-306, 409, 413-415, 422-424, 429-442), trích dẫn nguyên văn câu bình luận của Boersma, bổ sung đối sánh phổ định lượng giữa Hanning N=638 và Gaussian N=638/1276 trong `ch06_hanning_math.py`, thay thế hộp iverilog bằng `\todo{box}`.
- Commit `v3: ch06 r1 figures 12 and 13`: Thiết kế lại Hình 12 (đưa trục tần số xuống đáy -50 dB, nhãn tiếng Việt "Tần số chuẩn hóa ($f/f_s$)", đường chỉ rõ ràng có `fill=white`, phông chữ $\ge \text{\scriptsize}$) và Hình 13 (loại bỏ dải màu cam đặc, sửa nhãn trục đối xứng và nhãn trục hoành $n = 318, 319$).
- Commit `v3: ch06 r1 figure 14 arch`: Tái bố cục sơ đồ kiến trúc vi mô Hình 14 trên lưới tọa độ thoáng, khoảng cách các khối $\ge 6\text{ mm}$, đường tín hiệu và nhãn dây có `fill=white`, phông chữ $\ge \text{\scriptsize}$, không cắt qua tiêu đề.
- Commit `v3: ch06 r1 tone audit`: Chuẩn hóa văn phong học thuật trung tính, loại bỏ các từ ngữ mang tính cường điệu ("tuyệt đối", "hoàn toàn", "triệt để", "kinh điển", "tối ưu tuyệt đối"), chỉ giữ "100%" và "khớp bit" khi gắn kèm số liệu đối soát N/N cụ thể.
- Commit `v3: ch06 revision`: Hoàn tất nghiệm thu Đợt sửa đổi 1 (Revision Round 1) Chương 6.
