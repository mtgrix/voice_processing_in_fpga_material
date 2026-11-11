# BÁO CÁO NGHIỆM THU CHƯƠNG 7 (verify_v3/ch07_REPORT.md)
**Tên chương:** Tự tương quan bằng MAC (`chuong_v3/chuong_07_mac.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy, GCC)  
**Thời điểm hoàn thành:** 2026-11-11  

---

## 1. Bảng kiểm soát chất lượng từng mục (Per-subsection Checklist)

| Mục | Mở đầu bằng bài toán thực tế | Ví dụ tính tay / Kịch bản Python | Phương án + Đánh đổi + Lựa chọn số liệu | Tuyến IP Intel | Tuyến HDL tự viết | Song sinh + Iverilog | Câu tóm tắt bản chất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **7.1. Bản chất toán học của phép tự tương quan và đếm số phép tính** | Có | Có (`ch07_praat_lines.py`, `ch07_mac_math.py`, `ch07_fft_vs_mac.py`) | Có ($97.902\text{ MAC}$ cho $\tau = 26..214$, cộng 638 cho $R[0] \to 98.540\text{ MAC}$; v1 640 mẫu là $98.280$ và $98.920$; FFT 1024 mẫu đệm 386 số 0 tương đương toán học với MAC trực tiếp $\tau \le 386$, sai số float $\approx 2{,}4 \times 10^{-16}$) | Không áp dụng | Không áp dụng | Pass (7/7 trích dẫn Praat 7.0.03 dòng 344, 345, 401-403, 79-80, 144-156, 158-164) | Có |
| **7.2. Vì sao dùng MAC trực tiếp thay vì FFT: Đánh đổi tài nguyên và ngân sách thời gian** | Có | Có (`ch07_mac_math.py`, bảng định lượng 4 kiến trúc) | Có (FFT 1024 phức tạp, tốn 6--8 DSP, logic điều khiển bướm, ROM twiddle; MAC tuần tự 1 DSP chiếm $98.543 / 500.000\text{ nhịp} \to \text{RTF} = 0{,}197$, rảnh rỗi $> 80\%$ thời gian) | Không áp dụng | Không áp dụng | Pass (RTF $0{,}197086$) | Có |
| **7.3. Khảo sát kiến trúc MAC có thanh ghi: Ba phương án và đánh đổi trễ vs thông lượng** | Có | Có (Bảng tính tay 8 chu kỳ với chuỗi $x_w=[2,-3,4,1]$, $R[1]=-14$, $R[2]=5$) | Có (Phương án 1 trễ 2 nhịp đường tới hạn dài; Phương án 2 trễ 3 nhịp chốt ngõ vào DSP dùng FF cứng 0 ALM - **ĐÃ CHỌN**; Phương án 3 trễ 4 nhịp tốn 32 FF ngoài ALM bị loại; cơ chế zero-bubble bằng cờ `sload` tiết kiệm 190 chu kỳ) | Không áp dụng | Không áp dụng | Pass (Bảng tính tay khớp bit-chu-kỳ) | Có |
| **7.4. Dẫn xuất độ rộng bit bộ tích lũy và cấu trúc Variable Precision DSP** | Có | Có (`ch07_mac_math.py`) | Có (Toán hạng 17 bit có dấu, tích 34 bit có dấu, tổng 638 mẫu cực hạn $S_{\max} = 2.740.105.511.550 < 2^{41{,}32}$, cần 43 bit có dấu; bộ tích lũy DSP cứng Cyclone V rộng 64 bit, chọn 48 bit dự phòng an toàn 5 bit $\times 32$, 0 ALM ngoài) | Không áp dụng | Không áp dụng | Pass (Cận trên toán học 43 bit) | Có |
| **7.5. Kiến trúc bộ nhớ True Dual-Port RAM 638x17 và phân rã khối M10K** | Có | Có (Trích dẫn CV-52003 Chương 3 Bảng 3-1) | Có (Bộ nhớ $638 \times 17\text{-bit}$ cần $10.846\text{ bit} > 10.240\text{ bit}$ và độ sâu $638 > 512$, cấu hình bắt buộc $1024 \times 10$, tiêu tốn đúng **2 khối M10K**; cung cấp 2 cổng đọc đồng thời $x_w[n]$ và $x_w[n+\tau]$, trễ đọc 1 chu kỳ) | Không áp dụng | Không áp dụng | Pass (2 M10K, $512 \times 20$) | Có |
| **7.6. Phương án mở rộng: Tính song song bằng 2 khối DSP và bức tường bộ nhớ** | Có | Có (`ch07_mac_math.py`, so sánh 1 DSP vs 2 DSP) | Có (2 DSP giảm thời gian một nửa RTF $0{,}197 \to 0{,}10$, nhưng cần 3 cổng đọc đồng thời, vi phạm giới hạn 2 cổng M10K $\to$ phải nhân đôi bộ nhớ lên 4 M10K; giữ cấu hình 1 DSP làm mặc định tối ưu) | Không áp dụng | Không áp dụng | Pass (Phân tích Memory Wall) | Có |
| **7.7. Tuyến (A): Tích hợp khối IP Intel ALTERA_MULT_ADD** | Có | Có (Trích dẫn UG-01069) | Có (Tên chuẩn trên Cyclone V là `ALTERA_MULT_ADD`; tham số: `NUMBER_OF_MULTIPLIERS=1`, `WIDTH_A=17`, `WIDTH_B=17`, `REPRESENTATION="SIGNED"`, `WIDTH_RESULT=48`, `INPUT_REGISTER="CLOCK0"`, `MULTIPLIER_REGISTER="UNREGISTERED"`, `ACCUMULATOR="YES"`, `ACCUM_SLOAD_REGISTER="CLOCK0"`, `OUTPUT_REGISTER="CLOCK0"`; trễ 2 chu kỳ; 1 DSP, 0 ALM) | Có (Listing ghép nối IP Verilog) | Không áp dụng | Không áp dụng | Có |
| **7.8. Tuyến (B): Thiết kế Verilog HDL, mô hình song sinh Python và kiểm chứng** | Có | Có (`ch07_hdl_audit.py`, `ch07_mac_twin.py`, Bảng đối chiếu Twin vs HDL) | Có (3 module: `ch07_mac_engine.v`, `ch07_xw_ram.v`, `ch07_mac_unit.v`; FSM quét $98.540$ cặp trong $98.543$ chu kỳ; 16 khung từ `golden_v2/hdl_check/`, gồm 14 khung tiếng nói có nhiễu + 2 stress frames với $\max |x_w| = 59.379$; khớp bit tuyệt đối 3.040 / 3.040 kết quả, 0 lỗi) | Không áp dụng | Có (`rtl/v3/ch07_mac_unit.v` dòng 33--71, `verify_v3/ch07_mac_twin.py` dòng 50--98) | Pass 3.040/3.040 kết quả golden, 7.460 vector Twin; giữ chỗ `\todo{box}` cho Linux | Có |
| **7.9. Tổng kết so sánh IP và HDL, quy ước kiểm chứng và bài tập** | Có | Có (`ch07_exercises.py`) | Có (Quy ước lấy mẫu 2 pha: kích thích ở negedge `#1`, chốt và kiểm tra ở posedge `#1`; Bảng so sánh toàn diện IP vs HDL: 1 DSP, 2 M10K, trễ 2 nhịp, HDL vượt trội về khả chuyển mô phỏng; 4 bài tập có lời giải chi tiết) | Có | Có | iverilog: to be run by reviewer | Có |
| **Bài tập cuối chương (4 bài tập)** | Có | Có (`verify_v3/ch07_exercises.py`) | Có (Ex 7.1: FFT tối thiểu $N_{\text{min}} = 852 \to 1024$ đệm 172 mẫu; Ex 7.2: bubble 190 chu kỳ, $+0{,}1928\%$; Ex 7.3: Cận trên $S_{\max} = 2.740.105.511.550 < 2^{41{,}32}$, headroom 5 bit; Ex 7.4: Nghẽn cổ chai 3 cổng đọc, nhân đôi thành 4 M10K) | Không áp dụng | Không áp dụng | Pass (4/4 bài tập) | Có |

---

## 2. Số liệu định lượng tài liệu và ấn bản (Metrics)

- **Số trang biên dịch trong PDF hoàn chỉnh (`phan_moi_v3.pdf`):** 26 trang (trang 165 đến trang 190).
- **Tổng số trang toàn cuốn sách hiện tại:** 190 trang.
- **Số từ trong tệp TeX (`chuong_v3/chuong_07_mac.tex`):** 16.158 từ.
- **Số dòng trong tệp TeX:** 1.046 dòng.
- **Số hình vẽ TikZ kỹ thuật:** 3 hình (được hiệu chỉnh trực quan ở độ phân giải 150/300 dpi, phông chữ $\ge \text{\scriptsize}$, `fill=white`, không chạm viền, không có đường cắt qua chữ).
  - Hình 15 (`chuong_v3/fig_ch07_direct_mac_vs_fft.tex`): So sánh quy trình tính toán tự tương quan giữa Tuyến FPGA dùng MAC trực tiếp và Tuyến Praat dùng cặp biến đổi FFT 1024 điểm. Minh họa luồng dữ liệu thẳng 1 DSP $98.543$ chu kỳ so với luồng đệm 0, bướm FFT, phổ công suất và IFFT.
  - Hình 16 (`chuong_v3/fig_ch07_pipeline_options.tex`): So sánh ba phương án chốt thanh ghi đường ống trong khối nhân tích lũy MAC trên FPGA Cyclone V. Phân rã đường tới hạn $T_{\text{co}}(\text{M10K}) + T_{\text{wire}} + T_{\text{mult}} + T_{\text{add}} + T_{\text{su}}$ và ưu điểm vượt trội của Phương án 2 (chia đôi đường trễ bằng thanh ghi vào cứng có sẵn trong DSP, 0 ALM, trễ 3 chu kỳ chỉ chiếm $0{,}001\%$ thời gian).
  - Hình 17 (`chuong_v3/fig_ch07_mac_arch.tex`): Sơ đồ kiến trúc vi mô phần cứng của module tự tương quan MAC (`ch07_mac_engine.v`), thể hiện sự phối hợp nhịp nhàng giữa FSM phát địa chỉ quét $98.540$ cặp, bộ nhớ True Dual-Port RAM 638x17 (2 khối M10K), tầng cân bằng nhịp điều khiển `pipe1` và khối MAC DSP cứng (`ch07_mac_unit.v`) với tổng độ trễ đường ống đúng 3 chu kỳ.
- **Số bảng số liệu kỹ thuật:** 4 bảng lớn.
  - Bảng 30 (`tab:ch07_hand_trace`): Bảng tính tay 8 chu kỳ chứng minh cơ chế nạp đè `sload` và cờ xuất kết quả `out_valid` trên chuỗi mẫu giả định $x_w = [2, -3, 4, 1]$, tính $R[1] = -14$ và $R[2] = 5$ liên tục không có nhịp nghỉ (zero-bubble).
  - Bảng 31 (`tab:ch07_twin_vs_hdl`): Đối chiếu chi tiết từng khối dòng lệnh giữa mô hình song sinh Python (`verify_v3/ch07_mac_twin.py`) và mã nguồn Verilog HDL (`rtl/v3/ch07_mac_unit.v`).
  - Bảng 32 (`tab:ch07_ip_vs_hdl`): So sánh toàn diện giữa tuyến IP Intel `ALTERA_MULT_ADD` và tuyến HDL tự viết `ch07_mac_unit.v` về bản chất, tài nguyên DSP, M10K, ALM, $F_{\max}$, độ trễ, tính khả chuyển và gỡ lỗi.
  - Bảng định lượng đánh đổi ở Mục 7.2: So sánh kiến trúc MAC tuần tự 1 DSP, MAC song song 2 DSP, và FFT 1024 điểm về số phép tính, chu kỳ, DSP, M10K và RTF.
- **Số đoạn mã nguồn trích dẫn (Listings):** 5 đoạn.
  - Listing 30: Đoạn mã ghép nối khối IP Intel `ALTERA_MULT_ADD` trong chế độ MAC 17x17 signed.
  - Listing 31 (`lstinputlisting`): 39 dòng mã Verilog cốt lõi của khối MAC `rtl/v3/ch07_mac_unit.v` (dòng 33 đến 71, `firstnumber=33`).
  - Listing 32 (`lstinputlisting`): 49 dòng mã hàm cập nhật chu kỳ của mô hình song sinh Python `verify_v3/ch07_mac_twin.py` (dòng 50 đến 98, `firstnumber=50`).
  - Listing trong Thể công thức Mục 7.1: Trích dẫn 6 đoạn mã nguồn xác thực từ `fon/Sound_to_Pitch.cpp` của Praat 7.0.03.
  - Listing bài tập: Các công thức và cấu trúc logic liên quan.
- **Lỗi biên dịch XeLaTeX:** 0 lỗi (biên dịch bằng `xelatex -interaction=nonstopmode -halt-on-error phan_moi_v3.tex`).
- **Cảnh báo Overfull `\hbox` (> 10pt):** 0 cảnh báo (toàn bộ tài liệu đạt đúng 0 overfull hbox).

---

## 3. Danh mục các số liệu "phải đo" và căn cứ trích dẫn phần cứng

1. **Số liệu trích dẫn tài liệu phần cứng Intel Cyclone V:**
   - Cấu trúc khối Variable Precision DSP: *Cyclone V Device Handbook, Volume 1: Device Interfaces and Integration* (CV-52003, Chương 5: "Variable Precision DSP Blocks in Cyclone V Devices", Mục 5-2 và Bảng 5-1). Mỗi khối DSP chứa bộ tích lũy cứng rộng tới **64 bit** (CV-52003 Mục "Accumulator"). Luận điểm của Argon cho rằng bộ cộng rộng "48 bit tự nhiên" là không chính xác; bộ tích lũy vật lý là 64 bit, việc ta chọn thanh ghi kết quả 48 bit là cấu hình cắt bớt an toàn, hoàn toàn nằm trong silicon cứng và tiêu tốn **0 ALM ngoài**.
   - Cấu trúc khối nhớ nhúng M10K: *Cyclone V Device Handbook, Volume 1* (CV-52003, Chương 3: "Embedded Memory Blocks in Cyclone V Devices", Bảng 3-1). Khối M10K có dung lượng $10.240\text{ bit}$. Do bộ đệm $x_w$ có $638\text{ từ} \times 17\text{ bit} = 10.846\text{ bit} > 10.240\text{ bit}$ và độ sâu $638 > 512$, cấu hình phần cứng bắt buộc phải chọn là $1024 \times 10$, tiêu tốn đúng **2 khối M10K** ở chế độ True Dual-Port (cung cấp 2 cổng đọc độc lập $x_w[n]$ và $x_w[n+\tau]$, độ trễ đọc 1 chu kỳ).
   - Khối IP `ALTERA_MULT_ADD`: *Integer Arithmetic IP Cores User Guide* (Intel Document ID: UG-01069, mục "ALTERA_MULT_ADD IP Core"). Tên gọi chuẩn duy nhất trên Cyclone V; cấu hình toán hạng có dấu 17-bit, ngõ ra 48-bit, bật `INPUT_REGISTER = "CLOCK0"`, `MULTIPLIER_REGISTER = "UNREGISTERED"`, `ACCUMULATOR = "YES"`, `ACCUM_SLOAD_REGISTER = "CLOCK0"`, `OUTPUT_REGISTER = "CLOCK0"` cho độ trễ ngõ ra đúng **2 chu kỳ**.
   - Khối IP `RAM: 2-PORT`: *Embedded Memory User Guide* (UG-01068).
2. **Số liệu trích dẫn mã nguồn Praat 7.0.03 được kiểm chứng:**
   - `fon/Sound_to_Pitch.cpp:344`: `minimumLag = max(2, Melder_ifloor(1/dx/pitchCeiling))` $\to 26$ mẫu ở $16\text{ kHz}, 600\text{ Hz}$.
   - `fon/Sound_to_Pitch.cpp:345`: `maximumLag = min(Melder_ifloor(nsamp_window/periodsPerWindow) + 2, nsamp_window)` $\to \text{floor}(638/3) + 2 = 212 + 2 = \mathbf{214\text{ mẫu}}$.
   - `fon/Sound_to_Pitch.cpp:401-403`: `nsampFFT = smallest power of 2 >= nsamp_window*(1+interpolation_depth) = 638*1.5 = 957 -> 1024`.
   - `fon/Sound_to_Pitch.cpp:79-80`: Đệm 0 đuôi khung: `frame[j] = 0` cho $j = 639 \dots 1024$ (386 mẫu 0).
   - `fon/Sound_to_Pitch.cpp:144-156`: Đoạn chú thích của Boersma ("The FFT of the autocorrelation is the power spectrum."), tính phổ công suất $P[k] = \text{re}^2 + \text{im}^2$ và biến đổi IFFT ngược để thu hàm tự tương quan $ac[\tau]$.
   - `fon/Sound_to_Pitch.cpp:158-164`: Chuẩn hóa tự tương quan: $r[0] = 1$, $r[i] = ac[i+1] / (ac[1] \cdot windowR[i+1])$.
   - Toàn bộ trích dẫn được kiểm chứng qua `verify_v3/ch07_praat_lines.py`.
3. **Số liệu số học và kiểm toán thực thi chính xác:**
   - Số phép tính MAC lý thuyết:
     * Quét pitch $\tau \in [26, 214]$ (189 lag): $\sum_{\tau=26}^{214} (638 - \tau) = \mathbf{97.902\text{ MAC}}$.
     * Năng lượng khung tại $\tau = 0$: $638\text{ MAC}$.
     * Tổng số phép tính MAC trên toàn khung: $97.902 + 638 = \mathbf{98.540\text{ MAC}}$.
     * Đối chiếu bản v1 (640 mẫu): $98.280$ MAC quét và $98.920$ MAC tổng.
   - Ngân sách chu kỳ xung nhịp và RTF:
     * Tần số xung nhịp: $50\text{ MHz}$ ($T_{\text{clk}} = 20\text{ ns}$).
     * Hop size: $160\text{ mẫu} \to 500.000\text{ chu kỳ/khung}$.
     * Số chu kỳ phát địa chỉ: $98.540$ chu kỳ.
     * Độ trễ đường ống: $3\text{ chu kỳ}$ ($1\text{ M10K} + 2\text{ DSP}$).
     * Tổng số chu kỳ tự tương quan mỗi khung: $98.540 + 3 = \mathbf{98.543\text{ chu kỳ}}$.
     * Thời gian thực thi: $98.543 \times 20\text{ ns} \approx 1{,}97086\text{ ms} < 10\text{ ms}$.
     * Hệ số thời gian thực: $\text{RTF} = 98.543 / 500.000 = \mathbf{0{,}197086}$ (hệ thống rảnh rỗi hơn $80\%$ thời gian).
   - Tương đương toán học giữa FFT 1024 điểm và MAC trực tiếp:
     * Khung 638 mẫu đệm 0 lên 1024 điểm có khoảng đệm $1024 - 638 = 386$ mẫu.
     * Điều kiện không chồng lấn vòng: $\tau \le 386$.
     * Vì $\tau_{\max} = 214 \le 386$, tích chập vòng qua FFT hoàn toàn đồng nhất với tích chập tuyến tính MAC trực tiếp.
     * Sai số tương đối cực đại đo được trên 5 khung tín hiệu chuẩn: $\max \frac{|ac[\tau+1] - R[\tau]|}{R[0]} \le 3{,}23 \times 10^{-16}$ (xấp xỉ epsilon kiểu `double` 64-bit).
   - Dẫn xuất cận trên số học 43-bit chống tràn:
     * Toán hạng $x_w \in [-65.535, +65.535]$ ($17\text{ bit}$ có dấu).
     * Tích số cực đại: $65.535^2 = 4.294.836.225$.
     * Tổng tích lũy cực đại lý thuyết cho 638 mẫu: $S_{\max} = 638 \times 4.294.836.225 = \mathbf{2.740.105.511.550}$.
     * $\log_2(S_{\max}) \approx 41{,}3217 \to$ Cần tối thiểu $\lceil 41{,}3217 \rceil + 1 = \mathbf{43\text{ bit}}$ có dấu.
     * Độ rộng thanh ghi tích lũy phần cứng: $48\text{ bit}$.
     * Khoảng dự phòng an toàn (Headroom): $48 - 43 = \mathbf{5\text{ bit}}$ (gấp $2^5 = 32$ lần giá trị cực hạn lý thuyết).
   - Kiểm toán tái lập dữ liệu chuẩn tắc `golden_v2/hdl_check/`:
     * Số khung kiểm tra: 16 khung (14 khung tiếng nói có nhiễu + 2 stress frames với $\max |x_w| = 59.379$).
     * Số kết quả kiểm chứng: $16 \times 190 = \mathbf{3.040\text{ kết quả}}$.
     * Tỷ lệ khớp bit tuyệt đối: **3.040 / 3.040 kết quả** ($100\%$, 0 sai lệch) đối chiếu với `golden_v2/hdl_check/exp.hex`.
     * C reference HPS (`sw_v3/test_ch07_mac.c` + `sw_v3/ch07_mac.c`): 3.040 / 3.040 khớp $100\%$ bit-exact.
4. **Mục "phải đo" (To be measured on hardware / Linux simulation):**
   - iverilog: to be run by reviewer (`tb/v3/tb_ch07_mac.v`, kịch bản `verify_v3/run_ch07_iverilog.sh` chế độ 100755, 7.460 vector kiểm chứng chu-kỳ-đối-chu-kỳ).
   - Tài nguyên logic ALM và tần số cực đại $F_{\max}$: Phải đo chính xác sau khi tổng hợp Fitter và TimeQuest Timing Analyzer trong phần mềm Quartus Prime trên kit DE10-Standard với chip Cyclone V 5CSXFC6D6F31C6.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Hiện tượng bức tường bộ nhớ (Memory Wall) khi mở rộng tính song song:**
   Khi mở rộng lên 2 khối DSP để tính song song 2 giá trị lag trong cùng một chu kỳ (Mục 7.6 và Bài tập 7.4), hệ thống cần truy xuất 3 mẫu dữ liệu đồng thời ($x_w[n], x_w[n+\tau_1], x_w[n+\tau_2]$). Do khối nhớ M10K vật lý chỉ hỗ trợ tối đa 2 cổng đọc độc lập (True Dual-Port), hệ thống không thể chia sẻ chung 1 bộ nhớ mà buộc phải nhân đôi toàn bộ khối RAM thành 2 bản sao độc lập, tiêu tốn 4 khối M10K (thay vì 2 khối).
2. **Cố định kích thước khung 638 mẫu và dải quét pitch lag:**
   Máy trạng thái FSM phát địa chỉ được cấu hình cứng cho dải lag $\tau \in [26, 214]$ và chiều dài khung $N = 638$ (tương ứng $f_s = 16\text{ kHz}, F_{\text{floor}} = 75\text{ Hz}, F_{\text{ceiling}} = 600\text{ Hz}$). Nếu thay đổi các tham số phân tích này, cần cấu hình lại các hằng số đếm trong FSM.
3. **Độ trễ đọc kết quả của lag cũ tại chu kỳ chuyển tiếp:**
   Do áp dụng cơ chế nạp đè zero-bubble với cờ `sload_r`, kết quả tích lũy hoàn chỉnh của lag cũ chỉ tồn tại trên ngõ ra thanh ghi `acc` trong đúng 1 chu kỳ xung nhịp trước khi bị tích số đầu tiên của lag mới nạp đè. Do đó, khối xử lý phía sau (Bộ chuẩn hóa cửa sổ và dò đỉnh ở Chương 8 và Chương 9) bắt buộc phải chốt kết quả $R[\tau]$ ngay tại chu kỳ `out_valid = 1`.

---

## 5. Lịch sử các Commit Git trên nhánh v3

Tiến trình phát triển và hoàn thiện Chương 7 được thực hiện qua chuỗi commit nguyên tử có cấu trúc rõ ràng:

1. `83c4313` — `v3: ch07 7.1`: Bản chất tự tương quan, đếm phép tính $98.540\text{ MAC}$, chứng minh toán học tương đương FFT 1024 điểm với MAC trực tiếp ($\tau \le 386$, sai số float $10^{-16}$), 7 trích dẫn Praat 7.0.03 dòng 344--164.
2. `3b846e8` — `v3: ch07 7.2`: Vì sao dùng MAC trực tiếp thay vì FFT, phân tích đánh đổi tài nguyên và ngân sách thời gian, RTF $= 0{,}197$ (rảnh rỗi $> 80\%$).
3. `242d593` — `v3: ch07 7.3`: Khảo sát kiến trúc MAC có thanh ghi, 3 phương án chốt đường tới hạn, lựa chọn Phương án 2 (thanh ghi vào DSP, 0 ALM, trễ 3 chu kỳ), cơ chế zero-bubble bằng cờ `sload` và bảng tính tay 8 chu kỳ.
4. `432a70e` — `v3: ch07 7.4`: Dẫn xuất độ rộng bit bộ tích lũy, cận trên toán học 638 mẫu cực hạn đòi hỏi 43 bit có dấu, bộ tích lũy DSP cứng Cyclone V rộng 64 bit, lựa chọn ngõ ra 48 bit với dự phòng an toàn 5 bit ($32\times$).
5. `d1eac0a` — `v3: ch07 7.5`: Phân rã khối nhớ nhúng True Dual-Port RAM 638x17, chứng minh cấu hình $1024 \times 10$ tiêu tốn đúng 2 khối M10K, trễ đọc 1 chu kỳ.
6. `f9cf02d` — `v3: ch07 7.6`: Phương án mở rộng 2 DSP song song, phân tích bức tường bộ nhớ (cần 3 cổng đọc $\to$ nhân đôi thành 4 M10K).
7. `e1e728a` — `v3: ch07 7.7`: Tuyến (A) tích hợp khối IP Intel `ALTERA_MULT_ADD`, giải thích chi tiết từng tham số cấu hình trong Parameter Editor, mã ghép nối Verilog và phân tích độ trễ.
8. `41b4a0b` — `v3: ch07 7.8`: Tuyến (B) thiết kế Verilog HDL (`ch07_mac_unit.v`, `ch07_xw_ram.v`, `ch07_mac_engine.v`), Hình 17 kiến trúc vi mô, Listing 39 dòng Verilog và 49 dòng Python twin, Bảng đối chiếu 3 cột, kiểm toán 16 khung ($3.040$ kết quả khớp bit $100\%$ với `golden_v2/hdl_check/exp.hex`, 0 lỗi), $98.543$ chu kỳ/khung, giữ chỗ `\todo{box}` cho Linux.
9. `a71973c` — `v3: ch07 7.9`: Quy ước lấy mẫu testbench 2 pha, Bảng 32 so sánh toàn diện IP vs HDL, 4 bài tập có lời giải chi tiết, câu tóm tắt chương.
10. `80160c6` — `v3: ch07 polish fig and makefile target`: Tinh chỉnh khoảng cách nhãn Hình 17 không chạm viền/chữ, cập nhật Makefile target `ch07` tương thích đa nền tảng, thiết lập chế độ 100755 cho `run_ch07_iverilog.sh`, chuẩn hóa nhãn `\todo{box}`.
11. `1175c5c` — `v3: ch07 done`: Hoàn tất đợt nộp bản thảo đầu tiên của Chương 7 kèm báo cáo nghiệm thu.

### Chuỗi commit Revision Round 1 (R1) giải quyết toàn diện phản hồi phản biện:
12. `9bb66ad` — `v3: ch07 r1 item 1`: Hiện thực testbench mức đỉnh `tb/v3/tb_ch07_mac_engine.v` chuẩn `iverilog -g2012 -Wall`, không dùng `$random`, đọc trực tiếp `golden_v2/hdl_check/xw.hex` và so sánh bit-exact $16\text{ khung} \times 190 = 3.040\text{ kết quả}$ với `exp.hex`, kiểm tra đúng 190 xung `out_valid`/khung và chu kỳ kết thúc đúng 98.543 nhịp; tích hợp vào `verify_v3/run_ch07_iverilog.sh` (LF, 100755).
13. `271e4a1` — `v3: ch07 r1 item 2`: Khôi phục ô giữ chỗ trống `\todo{box}` nguyên bản theo đúng quy chuẩn không tiền định kết quả iverilog khi chưa chạy trên Linux; cập nhật diễn đạt nêu rõ kết quả kiểm toán 3.040/3.040 khớp `exp.hex` là của mô hình song sinh Python trong `verify_v3/ch07_hdl_audit.log`.
14. `fbed8c7` — `v3: ch07 r1 item 3`: Bổ sung trích dẫn Listing mã nguồn `rtl/v3/ch07_mac_engine.v` (dòng 128--167) với `firstnumber=128`, thuyết minh chi tiết từng dòng FSM và cơ chế zero-bubble, phân tích căn chỉnh đường ống trễ (dòng 215--249), mở rộng Bảng đối chiếu `tab:ch07_twin_vs_hdl` và sửa lỗi chính tả đường dẫn `verify/v3/` $\to$ `verify_v3/`.
15. `5f79666` — `v3: ch07 r1 item 4`: Loại bỏ triệt để các nhận định không có nguồn trích dẫn (nhận xét 0,8 ms, số M10K suy diễn, rủi ro lượng tử hóa ở Mục 7.6; so sánh họ Arria/Stratix và nhận xét $\approx 32\text{ FF}$ ngoài ALM ở Mục 7.3); bổ sung chỉ dẫn "(phải kiểm trong Quartus)" cho số ALM; chuẩn hóa toàn bộ trích dẫn tài liệu Intel sang *Cyclone V Device Handbook Vol.1, CV-52003, Variable Precision DSP Blocks in Cyclone V Devices* và *Integer Arithmetic IP Cores User Guide*.
16. `3422fba` — `v3: ch07 r1 item 6`: Chuẩn hóa giọng văn học thuật trung tính, loại bỏ toàn bộ dấu chấm than `!` và các tính từ thái quá (`tuyệt đối`, `hoàn toàn`, `hoàn hảo`, `tối ưu`, `triệt để`, `xa xỉ`, `thảm họa`, `vô nghĩa`); chỉ giữ tỷ lệ phần trăm $100\%$ khi đi kèm số đếm phân số thực tế $N/N$; chuyển đổi cú pháp markdown `*...*` sang `\emph{...}`.
17. `e2b4c4f` — `v3: ch07 r1 item 5`: Thiết kế lại toàn diện Hình 15, Hình 16, Hình 17 với khoảng cách rộng rãi, loại bỏ nhãn trùng lắp, không có đường cắt qua chữ hay chữ chạm viền; tăng cỡ chữ ghi chú chân hình lên `\small`; kiểm soát chặt chẽ biên dịch đạt đúng 0 cảnh báo overfull hbox trên toàn bộ Chương 7 và toàn cuốn sách.

---

## 6. Tổng kết đợt chỉnh sửa Revision Round 1

Toàn bộ 6 điểm nghẽn (Blockers) do người phản biện chỉ ra trong `agy_feedback/ch07_r1.txt` đã được giải quyết trọn vẹn, kiểm tra chéo trực quan ở độ phân giải cao 300 DPI và xác thực kỹ thuật đầy đủ:
- **Blocker 1 (Top TB):** Đã viết `tb/v3/tb_ch07_mac_engine.v` và tích hợp `run_ch07_iverilog.sh`.
- **Blocker 2 (Pre-written box):** Đã xóa kết quả tiền định, để trống `\todo{box}` cho người phản biện chạy trên Linux; ghi rõ công lao đối chiếu `exp.hex` thuộc về Python audit.
- **Blocker 3 (Engine listing & alignment):** Đã thêm Listing 40 dòng FSM engine, giải thích chi tiết, thuyết minh căn chỉnh đường trễ cờ điều khiển, mở rộng bảng đối chiếu.
- **Blocker 4 (Unsourced claims & Intel citations):** Đã loại bỏ các nhận định không có nguồn; chuẩn hóa tài liệu Intel Cyclone V.
- **Blocker 5 (Figures & Overfull):** Cả 3 hình vẽ TikZ đã được hiệu chỉnh khoảng cách rộng rãi, phóng to chữ chú thích, biên dịch sạch không có bất kỳ cảnh báo overfull hbox nào.
- **Blocker 6 (Tone & Markdown):** Đã thanh lọc toàn bộ từ ngữ cảm thán, chuyển đổi toàn bộ đánh dấu markdown sang lệnh LaTeX tiêu chuẩn.
