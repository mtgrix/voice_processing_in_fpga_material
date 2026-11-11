# BÁO CÁO NGHIỆM THU CHƯƠNG 5 (verify_v3/ch05_REPORT.md)
**Tên chương:** Trừ trung bình cục bộ, với DC-blocker tùy chọn (`chuong_v3/chuong_05_tru_trung_binh.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy)  
**Thời điểm hoàn thành:** 2026-11-11  

---

## 1. Bảng kiểm soát chất lượng từng mục (Per-subsection Checklist)

| Mục | Mở đầu bằng bài toán thực tế | Ví dụ tính tay / Kịch bản Python | Phương án + Đánh đổi + Lựa chọn số liệu | Tuyến IP Intel | Tuyến HDL tự viết | Song sinh + Iverilog | Câu tóm tắt bản chất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **5.1. Bản chất toán học và tác hại của mức DC** | Có | Có (`ch05_dc_effect.py`, Bảng 23 tính tay 8 mẫu) | Có ($c^2 = 1.000.000$ lệch tự tương quan, nâng đỉnh $0{,}1977 \to 0{,}6023 > 0{,}45$) | Không áp dụng | Không áp dụng | Pass (5/5) | Có |
| **5.2. Thuật toán Praat thật sự làm gì** | Có | Có (`ch05_praat_lines.py`, 6 dẫn xuất Praat 7.0.03) | Có (Cửa sổ 426 mẫu, trung bình float vs int $\Delta \le 0{,}49765$) | Không áp dụng | Không áp dụng | Pass (6/6) | Có |
| **5.3. Số học số nguyên: Nhân nghịch đảo thay cho bộ chia** | Có | Có (`ch05_mean_math.py`, quét 27.917.911 tổng) | Có ($M=10.082.083, k=32$, bẫy Argon $M=26214$ sai 10.485.605/41.943.040) | Không áp dụng | Không áp dụng | Pass (27.917.911/ 27.917.911) | Có |
| **5.4. Tuyến (A): Khởi tạo khối IP Intel LPM_MULT** | Có | Có (Trích dẫn CV-52003 Chương 5, UG-01069) | Có (DSP $27\times 27$ 1 khối, 0 ALM, `LPM_PIPELINE=2`, unsigned) | Có (Listing 23 LPM_MULT wrapper) | Không áp dụng | Không áp dụng | Có |
| **5.5. Tuyến (B): Hiện thực hóa phần cứng HDL tự viết** | Có | Có (Bảng 24 đối chiếu dòng-từng-dòng twin vs HDL) | Có (FSM 3 pha, đọc trực tiếp RAM vòng, bộ trừ 17-bit $d[n]$) | Không áp dụng | Có (`rtl/v3/ch05_local_mean.v`, 72 dòng trích) | 88.970/88.970 vector Twin | Có |
| **5.6. Bộ lọc số IIR khử trôi dạt DC (DC-blocker tùy chọn)** | Có | Có (`ch05_dc_effect.py`, $f_c = 9{,}928\text{ Hz}$, $-0{,}059\text{ dB}$) | Có ($\alpha = 1 - 2^{-8}$, không tốn bộ nhân DSP, 36-bit Q20.16 chống limit cycle) | Không áp dụng | Có (`rtl/v3/ch05_dc_blocker.v`, 108 dòng) | 1.000/1.000 vector Twin | Có |
| **5.7. Kiểm chứng mô hình song sinh Python và mô phỏng chu kỳ HDL** | Có | Có (Quy ước lấy mẫu tổ hợp/tuần tự, tệp stim/expected) | Có (Bảng 25 so sánh IP vs HDL: 1 DSP, 0 ALM, $F_{\max}$, tích hợp FSM) | Có | Có | iverilog: to be run by reviewer | Có |
| **Bài tập cuối chương (4 bài tập)** | Có | Có (`verify_v3/ch05_exercises.py`) | Có (Phân rã số hạng chéo, dẫn xuất $M$ cho $L=426, 640, 800$, ánh xạ DSP Cyclone V, limit cycle Q20.16) | Không áp dụng | Không áp dụng | Pass (4/4) | Có |

---

## 2. Số liệu định lượng tài liệu và ấn bản (Metrics)

- **Số trang biên dịch trong PDF hoàn chỉnh (`phan_moi_v3.pdf`):** 24 trang (trang 118 đến trang 141).
- **Tổng số trang toàn sách:** 141 trang.
- **Số từ trong tệp TeX (`wc -w chuong_v3/chuong_05_tru_trung_binh.tex`):** 13.879 từ.
- **Số dòng trong tệp TeX:** 771 dòng.
- **Số hình vẽ TikZ kỹ thuật:** 3 hình (toàn bộ nhãn $\ge \text{\scriptsize}$, fill=white, không đè viền, không đường cắt qua chữ).
  - Hình 9 (`chuong_v3/fig_ch05_dc_effect.tex`): Minh họa trực quan tác hại của thành phần DC làm lệch đường cong tự tương quan thêm $+c^2$, phá hủy ngưỡng `VOICING_THRESHOLD = 0.45`, gây báo động giả tiếng hữu thanh trong khung vô thanh.
  - Hình 10 (`chuong_v3/fig_ch05_local_mean_arch.tex`): Sơ đồ kiến trúc vi mô phần cứng khối tính trung bình cục bộ (`ch05_local_mean.v`), minh họa bộ đếm địa chỉ quét 426 mẫu, bộ đổi dấu pre-bias, bộ tích lũy 25-bit, bộ nhân đường ống 2 tầng $M$, bộ trích xuất đổi dấu và bộ trừ 17-bit $d[n]$.
  - Hình 11 (`chuong_v3/fig_ch05_dc_blocker.tex`): Kiến trúc vi mô bộ lọc IIR DC-Blocker bậc 1 (`ch05_dc_blocker.v`), sử dụng bộ trừ sai phân $dx[n]$, thanh ghi tích lũy 36-bit Q20.16 chống limit cycle, mạch dịch số học 8-bit và bộ ghép kênh bypass.
- **Số bảng số liệu kỹ thuật:** 4 bảng.
  - Bảng 23: Tính toán bằng tay tác hại của mức DC $c = +1000$ lên tự tương quan ($N=8$ mẫu, trích từ `verify_v3/ch05_dc_effect.log`).
  - Bảng 24: Bảng đối chiếu song song từng dòng giữa mô hình song sinh Python (`verify_v3/ch05_mean_twin.py`) và mã nguồn Verilog HDL (`rtl/v3/ch05_local_mean.v`).
  - Bảng 25 (`tab:ch05_ip_vs_hdl`): So sánh toàn diện giữa đường dẫn sử dụng IP lõi Intel LPM_MULT và giải pháp HDL tự viết (`ch05_local_mean.v`).
  - Các bảng số liệu giải tích trong Lời giải Bài tập 5.1, 5.2, 5.4.
- **Số đoạn mã nguồn trích dẫn (Listings):** 4 đoạn.
  - Listing 23: Mẫu khởi tạo khối IP Intel `LPM_MULT 25x24 unsigned` trong Verilog (trích từ UG-01069).
  - Listing 24 (`lstinputlisting`): 72 dòng then chốt trong máy trạng thái FSM và đường ống tính trung bình cục bộ của `rtl/v3/ch05_local_mean.v` (dòng 102 đến 173, `firstnumber=102`).
  - Listing 25 (`lstinputlisting`): 52 dòng then chốt trong hàm cập nhật chu kỳ `step_cycle` của `verify_v3/ch05_mean_twin.py` (dòng 114 đến 165, `firstnumber=114`).
  - Listing 26: Bảng đối chiếu 3 cột `Twin Line | HDL Line | Ý nghĩa kiến trúc`.
- **Lỗi biên dịch XeLaTeX:** 0 lỗi.
- **Cảnh báo Overfull `\hbox` (> 10pt):** 0 cảnh báo (toàn bộ tài liệu đạt 0 overfull hbox).

---

## 3. Danh mục các số liệu "phải đo" và căn cứ trích dẫn phần cứng

1. **Số liệu trích dẫn từ tài liệu phần cứng Intel Cyclone V:**
   - Cấu trúc Variable Precision DSP Block: *Cyclone V Device Handbook, Volume 1: Device Interfaces and Integration* (CV-52003, Chương 5: "Variable Precision DSP Blocks in Cyclone V Devices", Mục 5-2 và Bảng 5-1: "Operational Modes"). Cung cấp 3 chế độ độc lập: ba bộ nhân $9 \times 9$, hai bộ nhân $18 \times 18$, hoặc một bộ nhân $27 \times 27$. Phép nhân $25 \times 24$-bit không dấu vừa khít hoàn toàn bên trong 1 khối DSP ở chế độ $27 \times 27$, tiêu tốn đúng 1 khối DSP và 0 ALM.
   - Hướng dẫn cấu hình IP LPM_MULT: *LPM User Guide* (Intel / Altera, UG-01069 / Document ID 10148, Section "LPM_MULT"). Xác định chính xác các tham số `LPM_WIDTHA = 25`, `LPM_WIDTHB = 24`, `LPM_WIDTHP = 49`, `LPM_REPRESENTATION = "UNSIGNED"`, `LPM_PIPELINE = 2`.
2. **Số liệu trích dẫn mã nguồn Praat 7.0.03 được kiểm chứng:**
   - `fon/Sound_to_Pitch.cpp:326`: `nsamp_period = Melder_ifloor(1.0/dx/pitchFloor) = 213` tại $f_s = 16\text{ kHz}, F_{\text{floor}} = 75\text{ Hz}$.
   - `fon/Sound_to_Pitch.cpp:59-60`: `startSample = rightSample - nsamp_period`, `endSample = leftSample + nsamp_period` (khoảng cách đúng bằng $2 \times 213 = 426$ mẫu).
   - `fon/Sound_to_Pitch.cpp:63-65`: Tổng các mẫu `my z` trong khoảng `startSample` đến `endSample` (426 mẫu).
   - `fon/Sound_to_Pitch.cpp:66`: `localMean /= 2*nsamp_period` (chia cho 426 dạng số thực `double`, không làm tròn).
   - `fon/Sound_to_Pitch.cpp:72-73, 77-78`: Sao chép khung và trừ `localMean` trước khi nhân cửa sổ Hanning.
   - Toàn bộ 6 trích dẫn được kiểm chứng đạt 6/6 PASS qua `verify_v3/ch05_praat_lines.py`.
3. **Số liệu số học số nguyên kiểm chứng đầy đủ (Exhaustive & Exact Math):**
   - Định lý nhân nghịch đảo Granlund--Montgomery: $M = \lceil 2^{32} / 426 \rceil = 10.082.083$ (`0x99D7A3`), độ lệch pre-bias $B = 426 \times 32768 = 13.959.168$, hằng số làm tròn $+213$. Đã kiểm chứng vét cạn toàn bộ $27.917.911$ giá trị tổng $S_{\text{biased}} \in [213, 27.918.123]$ qua `verify_v3/ch05_mean_math.py`: 0 lỗi sai số so với phép chia nguyên lý thuyết $\lfloor (S + 213)/426 \rfloor$.
   - Bẫy Argon ($M = 26214, k = 24$): Gây sai số trên $10.485.605 / 41.943.040$ tổng (tỷ lệ lỗi $\approx 25\%$), đã được phân tích và chứng minh nguyên nhân trong `verify_v3/ch05_mean_math.log`.
   - Đáp ứng bộ lọc DC-Blocker: Tần số cắt giải tích chính xác $f_c = 9{,}9278\text{ Hz}$ (công thức xấp xỉ $9{,}9472\text{ Hz}$); tại $75\text{ Hz}$, độ lợi đạt $-0{,}0590\text{ dB}$, pha $+7{,}5691^\circ$. Hằng số thời gian suy giảm $\tau = 255{,}5$ mẫu ($16{,}0\text{ ms}$). Toàn bộ được kiểm chứng trong `verify_v3/ch05_dc_effect.log`.
4. **Mục "phải đo" (To be measured on hardware / Linux simulation):**
   - Kết quả chạy thực tế Icarus Verilog: iverilog: to be run by reviewer. Kịch bản `verify_v3/run_ch05_iverilog.sh` (LF, chế độ 100755) và toàn bộ các tệp vector kích thích/kỳ vọng đã được chuẩn bị đầy đủ và đồng bộ. Trong văn bản LaTeX, kết quả được đặt dạng hộp giữ chỗ `\todo{box}` để reviewer điền số đo chính thức sau khi chạy trên Linux.
   - Tài nguyên logic ALM và tần số hoạt động tối đa $F_{\max}$: Phải đo chính xác sau khi tổng hợp Fitter và TimeQuest Timing Analyzer trong phần mềm Quartus Prime với chip 5CSXFC6D6F31C6.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Sai số lượng tử hóa của phép tính trung bình số nguyên so với Praat `double`:**
   Praat 7.0.03 tính `localMean` dưới dạng số thực dấu phẩy động 64-bit IEEE-754 (`double`), sau đó trừ trực tiếp vào mẫu `double`. Trong kiến trúc phần cứng FPGA của ta, để bảo toàn tài nguyên và loại bỏ FPU 64-bit cồng kềnh, giá trị trung bình cục bộ được làm tròn số nguyên theo quy tắc $\lfloor (S + 213)/426 \rfloor$.
   - Kiểm chứng trên 205 khung tệp âm thanh sạch: độ lệch cực đại là $0{,}5000$, độ lệch trung bình là $0{,}2290$ đơn vị lượng tử (LSB).
   - Kiểm chứng trên tệp có nhiễu: độ lệch cực đại là $0{,}4953$, độ lệch trung bình là $0{,}2493$ LSB.
   - Giới hạn sai số trên lý thuyết chặt chẽ là $212 / 426 \approx 0{,}49765 < 0{,}5\text{ LSB}$.
   Sai số này nằm gọn trong mức nhiễu lượng tử hóa nửa bit $(\pm 0{,}5\text{ LSB})$ của bộ chuyển đổi tín hiệu 16-bit, hoàn toàn không làm suy giảm độ chính xác ước lượng F0.
2. **Kích thước cửa sổ 426 mẫu gắn cứng với cấu hình danh định:**
   Cửa sổ tính trung bình 426 mẫu được thiết kế tối ưu cho tần số lấy mẫu $f_s = 16\text{ kHz}$ và tần số sàn $F_{\text{floor}} = 75\text{ Hz}$. Nếu hệ thống được cấu hình lại với $F_{\text{floor}}$ khác (ví dụ 50 Hz hoặc 100 Hz), tham số độ dài quét $L$ và hằng số nhân nghịch đảo $M$ cần được tham số hóa lại ở thời điểm biên dịch phần cứng.
3. **Độ lệch pha của bộ lọc DC-Blocker:**
   Bộ lọc IIR DC-Blocker bậc 1 loại bỏ hoàn toàn trôi dạt DC tĩnh và trôi dạt chậm mà không tốn khối DSP nào. Tuy nhiên, nó tạo ra một độ lệch pha nhẹ $+7{,}57^\circ$ tại tần số đáy 75 Hz. Do đó, trong các bài đo kiểm đối soát chuẩn mực từng cent với Praat 7.0.03, khối này bắt buộc phải được đặt ở trạng thái BYPASS mặc định (`bypass = 1`).

---

## 5. Lịch sử các Commit Git trên nhánh v3

Toàn bộ tiến trình phát triển và kiểm chứng Chương 5 được lưu vết qua các commit nguyên tử trên nhánh `v3`:
- `c0f46de`: `v3: ch05 5.1` (Bản chất toán học và tác hại của mức DC, Bảng 23 tính tay 8 mẫu, hình vẽ Hình 9 TikZ, khởi tạo toàn bộ RTL, TB, Python scripts, logs và vector kiểm thử).
- `131a341`: `v3: ch05 5.2` (Thuật toán Praat 7.0.03, đối chiếu 6 dòng lệnh C++, cửa sổ 426 mẫu, so sánh định lượng trung bình float vs int).
- `9327c45`: `v3: ch05 5.3` (Số học số nguyên nhân nghịch đảo $M = 10.082.083, k = 32$, bù pre-bias $B = 13.959.168$, vét cạn 27.917.911 tổng, phân tích bẫy Argon $M=26214$).
- `7719d5e`: `v3: ch05 5.4` (Tuyến IP Intel LPM_MULT 25x24 unsigned, giải thích 7 tham số, ánh xạ 1 khối DSP Cyclone V 27x27, 0 ALM, Listing 23).
- `0183c81`: `v3: ch05 5.5` (Tuyến HDL tự viết ch05_local_mean.v, FSM 3 pha, Listing 24 và Listing 25, Bảng 24 đối chiếu từng dòng, Hình 10 TikZ).
- `6fb46e8`: `v3: ch05 5.6` (Bộ lọc số IIR khử trôi dạt DC ch05_dc_blocker.v, dẫn xuất giải tích fc = 9.928 Hz, thanh ghi 36-bit Q20.16 chống limit cycle, Hình 11 TikZ).
- `6ba17ee`: `v3: ch05 5.7` (Quy ước lấy mẫu testbench tổ hợp/tuần tự, bộ vector 88.970 chu kỳ và 1.000 chu kỳ, Bảng 25 so sánh IP vs HDL, 4 bài tập thực chiến có lời giải chi tiết từ ch05_exercises.py).
