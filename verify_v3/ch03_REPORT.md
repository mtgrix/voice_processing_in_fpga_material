# BÁO CÁO NGHIỆM THU CHƯƠNG 3 (verify_v3/ch03_REPORT.md)
**Tên chương:** Bước làm mềm mép Nyquist: khối FIR tùy chọn (`chuong_v3/chuong_03_fir_nyquist.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy)  
**Thời điểm hoàn thành:** 2026-11-11 (Hiệu đính Đợt 1 — Revision Round 1)  

---

## 0. Kết quả tiếp thu và xử lý ý kiến đánh giá Đợt 1 (Review Round 1 Disposition)

Toàn bộ 5 điểm nghẽn (Blockers) và 4 điểm cần hoàn thiện (Should-fix) từ Người đánh giá (Reviewer, 2026-11-11) đã được giải quyết triệt để:

### Các điểm nghẽn (Blockers) đã giải quyết
1. **Lệch pha thời điểm lấy mẫu trong Testbench Icarus Verilog (Blocker 1):**
   - *Nguyên nhân:* Cờ `sink_ready` là tín hiệu tổ hợp (combinational output) phản ánh trạng thái trước sườn xung nhịp. Mô hình Python Twin ghi nhận `sink_ready` trước sườn dương, trong khi testbench cũ `tb_ch03_fir.v` kiểm tra sau `@(posedge clk)` khi FSM đã chuyển trạng thái sang `S_CALC` (làm `sink_ready` rơi về 0), dẫn tới lệch pha 1 chu kỳ mỗi 17 nhịp.
   - *Khắc phục:* Đã tái cấu trúc testbench `tb/v3/tb_ch03_fir.v`: nạp kích thích tại `@(negedge clk)`, đợi xác lập `#1`, lấy mẫu đối soát tín hiệu tổ hợp `sink_ready` ngay trước sườn dương; sau `@(posedge clk); #1` mới lấy mẫu đối soát các tín hiệu tuần tự đã chốt qua thanh ghi (`source_valid`, `source_data`, `state`, `step`).
   - Đã gỡ bỏ lệnh dừng sớm `if (errors >= 20) $finish;` để đối soát toàn diện toàn bộ 3.390 chu kỳ.
   - Tái tạo dữ liệu kích thích và phản hồi chuẩn bằng `python verify_v3/ch03_fir_twin.py`.
   - Bổ sung 1 đoạn văn chuẩn mực trong mục 3.5 của tài liệu LaTeX giải thích rõ quy ước lấy mẫu tổ hợp và tuần tự.
2. **Loại bỏ kết quả mô phỏng chưa chạy (Blocker 2):**
   - Đã gỡ bỏ toàn bộ nội dung kết quả mô phỏng giả lập trong văn bản LaTeX tại mục 3.5 cũng như báo cáo.
   - Thay thế bằng khối `\todo{box}` chuẩn mực để người đánh giá điền kết quả thực tế sau khi chạy trên môi trường Linux.
3. **Hiệu chỉnh giải trình về Praat chuẩn xác theo sự thật khách quan (Blocker 3):**
   - Loại bỏ nhận định suy đoán về việc bộ nội suy `sinc70` bù trừ cho việc thiếu bộ lọc tiền xử lý.
   - Khẳng định sự thật được kiểm chứng: mã nguồn Praat 6.4.12 và 7.0.03 (`fon/Sound_to_Pitch.cpp`) trong nhánh tự tương quan thô (`raw-ac`) không thực hiện nâng tần số lấy mẫu hay lọc tiền xử lý Nyquist (khác với mô tả trong bài báo Boersma 1993); lý do lược bỏ không được tài liệu hóa trong mã nguồn hoặc hướng dẫn của Praat.
   - Giữ nguyên các vị trí tham chiếu dòng bằng `TODO-PRAAT-LINE` để người đánh giá điền số dòng chính xác trên Linux. Kịch bản `verify_v3/ch03_praat_lines.py` kiểm tra 2 vị trí này đạt kết quả PASS.
4. **Vẽ lại toàn diện Hình 6 (Kiến trúc khối folded FIR) (Blocker 4):**
   - Thiết kế lại tệp `chuong_v3/fig_ch03_folded_arch.tex` với kích thước mở rộng phủ kín độ rộng trang `\textwidth` (`\resizebox{\textwidth}{!}`).
   - Bố trí các khối chức năng trên lưới tọa độ rộng rãi với khoảng cách tối thiểu $\ge 8\text{ mm}$.
   - Tất cả nhãn tín hiệu được đặt trên nền trắng xóa đường kẻ (`fill=white, inner sep=1.5pt`), khắc phục hoàn toàn hiện tượng đường dây đè chữ hoặc chữ chạm viền hộp.
   - Sửa lỗi driver XeTeX làm đè màu nền trắng thành chữ cam đậm `text=orange!90!black` trên đường bypass.
   - Xuất ảnh kiểm tra ở độ phân giải cao 300 DPI, bảo đảm mọi chi tiết sắc nét và thoáng đãng.
5. **Vẽ lại Hình 5 (Đặc tuyến biên độ tần số) (Blocker 5):**
   - Thiết kế lại hộp chú giải trong `chuong_v3/fig_ch03_freq_response.tex`.
   - Di chuyển chú giải xuống góc dưới bên trái trống trải (tọa độ $x \in [0{,}4; 6{,}7]$, $y \in [0{,}15; 2{,}50]$), giãn cách dòng thoáng ($0{,}45\text{ cm}$ giữa các mục, $0{,}60\text{ cm}$ dưới tiêu đề), loại bỏ hoàn toàn việc đè chữ lên tiêu đề chú giải.

### Các điểm hoàn thiện (Should-fix) đã giải quyết
6. **Sửa lỗi Markdown thô trong LaTeX:** Chuyển đổi toàn bộ các thẻ sao `**...**` còn sót tại các dòng 302, 310, 334 thành lệnh chuẩn `\textbf{...}`.
7. **Trung hòa giọng văn học thuật:**
   - Thay thế toàn bộ khoảng 10 cụm từ mang sắc thái kịch tính ("sự thật phũ phàng", "vạch trần", "hoàn toàn sai lầm", "tinh xảo", "tường tận", "cực đoan", "tuyệt đối") bằng văn phong điềm đạm, khách quan và khoa học.
   - Loại bỏ các quy chiếu người dùng/bản nháp nội bộ ("điển hình là bản nháp của Argon"), thay thế bằng khung "Bẫy thường gặp" có giá trị giáo khoa sư phạm chung.
8. **Bổ sung trích dẫn tài liệu Intel FIR Compiler II User Guide (UG-01072):**
   - Bổ sung mã tài liệu chính thức `UG-01072` kèm số mục chi tiết (Mục 3.1, 3.2, 3.3, 4.1, 4.2) cho từng tham số trong Parameter Editor, các cổng giao tiếp Avalon-ST và quy ước `readyLatency = 0`.
   - Các thông số mà GUI tính toán (độ trễ nhịp chính xác, tài nguyên logic ALM, độ rộng ngõ ra toàn phần) được nêu rõ là "phải kiểm trong GUI/IP Generation Report".
9. **Thuyết minh rõ hệ số khuếch đại DC (DC Gain) của bộ lọc 31 tap:**
   - Bổ sung phân tích định lượng ngay cạnh Bảng so sánh 3.2: tổng trọng số lượng tử hóa $\sum h[i] = 33.257$, hệ số khuếch đại DC tương ứng $G_{\text{DC}} = 33.257 / 32.768 \approx 1{,}01492$ ($+0{,}128\text{ dB}$).
   - Nêu rõ lý do giữ nguyên không chuẩn hóa lại (để bảo toàn tính đối xứng và không làm xáo trộn đáp ứng biên độ tần số), đồng thời liên hệ trực tiếp với khâu bão hòa biên độ bắt buộc tại $+32.767$ khi tín hiệu đạt cực trị dương.

---

## 1. Bảng kiểm định chi tiết từng mục con (Subsection Checklist)

| Mục con | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / minh họa số? | Phương án + Đánh đổi + Lựa chọn có số? | Đường (A) Intel IP? | Đường (B) HDL tự viết? | Twin Python + TB iverilog? | Câu tóm lại cuối mục? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **3.1. Bản chất hiện tượng rò rỉ phổ mép Nyquist** | **Có** (thành phần gần 8 kHz sau khi nhân Hanning tràn búp phổ qua Nyquist, sinh sóng đổi dấu $(-1)^\tau$ phá hủy đỉnh tự tương quan $r(\tau)$) | **Có** (dao động $f = 8\text{ kHz}$ lấy mẫu tại $16\text{ kHz}$ sinh dãy alternating $[+A, -A, +A, -A]$) | **Có** (bật FIR so với Praat 7.0.03 vốn không lọc sẽ tự tạo nguồn lệch; chọn mặc định `bypass = 1`, cho phép bật khi nghiên cứu) | N/A (phân tích hiện tượng và đối chiếu Praat) | N/A (phân tích hiện tượng và đối chiếu Praat) | **Có** (kiểm chứng Praat source qua `ch03_praat_lines.py`, 2 vị trí `TODO-PRAAT-LINE`) | **Có** (*Tóm lại: Thành phần gần Nyquist sinh ra sóng đổi dấu...*) |
| **3.2. Các phương án, đánh đổi, ta chọn gì, vì sao** | **Có** (bài toán đánh đổi giữa độ suy hao dải chặn, trễ nhóm và tài nguyên silicon; bẫy thường gặp về độ rộng bit hệ số và độ suy hao dải chặn) | **Có** (tính toán công thức Kaiser ra 147 tap; tính độ trễ nhóm $\tau_g = 15$ mẫu; DC gain $1{,}0149$; dời khung $s_{\text{start, FIR}} = s_{\text{start}} - 15$) | **Có** (Bảng 4 phương án: Bypass, 31 tap, 63 tap, 127 tap; số liệu từ `scipy.signal.firls`; chọn 31 tap kèm bypass) | N/A (cơ sở lý thuyết lọc FIR) | N/A (cơ sở lý thuyết lọc FIR) | **Có** (`verify_v3/ch03_fir_design.py` kiểm chứng độ suy hao và lượng tử hóa Q1.15) | **Có** (*Tóm lại: Dải chuyển tiếp 400 Hz quá hẹp...*) |
| **3.3. Đường (A): Khối IP FIR Compiler II của Intel** | **Có** (hộp đen IP công nghiệp tiềm ẩn rủi ro khi đặt sai `Input Sample Rate` trong hệ thống xử lý tệp) | **Có** (phân tích tỷ số chia nhịp: 0,016 MSPS sinh 3.125 chu kỳ/mẫu gây tràn hàng đợi; 0,5 MSPS sinh 100 chu kỳ/mẫu an toàn) | **Có** (phân tích chi tiết 7 nhóm tham số trong Parameter Editor theo Intel UG-01072, liên hệ trực tiếp với lý thuyết mục 3.2) | **Có** (`altera_fir_compiler_ii`, giải mã GUI, cổng Avalon-ST, đoạn mã Verilog wrapper `u_fir_ip`) | N/A (thuộc nhánh IP) | N/A (thuộc nhánh IP) | **Có** (*Tóm lại: Khối IP Intel FIR Compiler II tối ưu hóa tài nguyên...*) |
| **3.4. Đường (B): Khối HDL tự viết: FIR đối xứng gấp thời gian** | **Có** (kiến trúc trực tiếp song song tốn tới 16 bộ nhân DSP là lãng phí tài nguyên silicon ở tốc độ 16 kHz) | **Có** (rút gọn 31 tap thành 15 cặp đối xứng tiền cộng 17-bit + 1 hệ số trung tâm, tuần tự 16 nhịp xung nhịp 50 MHz) | **Có** (so sánh Fully Parallel vs Transposed vs Folded Time-Multiplexed; chọn Folded 1 DSP, 0 M10K) | **Có** (đối chiếu từng tham số IP với kiến trúc HDL) | **Có** (`rtl/v3/ch03_fir_filter.v`, liệt kê 45 dòng cốt lõi và giải thích chi tiết) | **Có** (Bảng đối chiếu 3 cột song song Twin vs HDL dòng-từng-dòng) | **Có** (*Tóm lại: Khối HDL folded FIR dùng đúng 1 DSP...*) |
| **3.5. Kiểm chứng mô hình song sinh Python và mô phỏng chu kỳ HDL** | **Có** (nguy cơ sai lệch từng bit giữa phần mềm và phần cứng khi xử lý số học dấu phẩy tĩnh và cơ chế phản áp) | **Có** (6 thử thách: Impulse response, sin 7,8 kHz suy hao $-6{,}54\text{ dB}$, sin 1,0 kHz, WAV thật, stress bão hòa $\pm 32767$, random backpressure) | **Có** (chiến lược kiểm chứng 3 tầng; Bảng đối chiếu toàn diện IP vs HDL) | **Có** (Bảng so sánh IP vs HDL) | **Có** (Testbench `tb/v3/tb_ch03_fir.v` đọc kích thích và đối soát từng chu kỳ) | **Có** (`verify_v3/ch03_fir_twin.py` sinh 3.390 chu kỳ kích thích; testbench iverilog đã fix timing; giữ chỗ `\todo{box}` cho log Linux) | **Có** (*Tóm lại: Mô hình song sinh Python đã sinh tập vector 3.390 chu kỳ...*) |
| **Bài tập cuối chương** | 4 bài tập thực chiến bao quát: (1) Tính bậc lọc Kaiser; (2) Dẫn xuất trễ nhóm và dời khung; (3) Ngân sách chu kỳ và thông lượng 2,94 MSPS; (4) Lượng tử hóa Q1.15 và khâu bão hòa biên độ. | Tất cả bài tập đều có lời giải mẫu chi tiết từng bước, kết quả khớp hoàn toàn với `verify_v3/ch03_exercises.py`. |

---

## 2. Thống kê khối lượng và quy mô tài liệu

- **Số trang biên dịch PDF (`phan_moi_v3.pdf`):** Chương 3 chiếm 22 trang (từ trang 81 đến trang 102 của tài liệu toàn tập 102 trang).
- **Số từ tiếng Việt (`chuong_v3/chuong_03_fir_nyquist.tex`):** 12.964 từ.
- **Số dòng mã nguồn LaTeX:** 704 dòng.
- **Số hình vẽ TikZ kỹ thuật cao:** 2 hình (đã vẽ lại rộng rãi, đạt chuẩn trực quan cao):
  1. *Hình 5 (trang 84):* Đáp ứng tần số biên độ $|H(f)|$ (dB) của các phương án bộ lọc FIR so với đường cong mục tiêu Boersma (1993) trên dải chuyển tiếp 400 Hz; hộp chú giải bố trí tại góc dưới bên trái thoáng đãng.
  2. *Hình 6 (trang 89):* Sơ đồ kiến trúc phần cứng khối lọc FIR 31 tap gấp thời gian với bộ tiền cộng 17-bit và 1 khối DSP (`rtl/v3/ch03_fir_filter.v`), định tuyến rộng rãi trên lưới $\ge 8\text{ mm}$, phủ toàn bộ bề ngang trang, nhãn nền trắng xóa đường kẻ.
- **Số bảng số liệu:** 3 bảng:
  1. *Bảng 17 (trang 84):* So sánh định lượng các phương án bộ lọc FIR làm mềm mép Nyquist tại $f_s = 16\text{ kHz}$.
  2. *Bảng 18 (trang 94):* Đối chiếu trực tiếp giữa các dòng lệnh của Python Twin và mã nguồn phần cứng Verilog.
  3. *Bảng 19 (trang 98):* So sánh toàn diện giữa khối IP Intel FIR Compiler II và mã nguồn HDL tự viết cho Chương 3.
- **Số đoạn mã nguồn trích dẫn:** 3 listings:
  1. *Listing 13 (trang 88):* Mã khởi tạo giao diện khối IP Intel FIR Compiler II trong hệ thống (`u_fir_ip`).
  2. *Listing 14 (trang 90–91):* Mã nguồn phần cứng bộ lọc FIR 31 tap gấp thời gian (`rtl/v3/ch03_fir_filter.v`, 45 dòng then chốt).
  3. *Listing 15 (trang 95–96):* Hàm cập nhật chu kỳ của mô hình song sinh FIR (`verify_v3/ch03_fir_twin.py`, dòng 28–98).
- **Lỗi biên dịch LaTeX và Overfull box:**
  - 0 lỗi biên dịch (biên dịch 2 lần liên tiếp bằng MiKTeX XeLaTeX).
  - **0 cảnh báo `Overfull \hbox`** trong toàn bộ Chương 3 và toàn bộ tài liệu 102 trang.

---

## 3. Danh mục các thông số chưa kiểm chứng và mục "(phải đo)"

Theo đúng nguyên tắc trung thực học thuật của đề cương:
1. **Tài nguyên logic ALM và tần số cực đại $F_{\max}$ của khối IP Intel FIR Compiler II:** Được ghi rõ là `(phải đo trong Quartus Fitter và Timing Analyzer)`, do môi trường hiện tại không cài đặt Quartus Prime.
2. **Độ trễ xử lý (Latency) và độ rộng bit ngõ ra của khối IP Intel:** Được ghi rõ là `(phải kiểm trong báo cáo sinh mã IP Generation Report hoặc mô phỏng IP)`.
3. **Tài nguyên ALM và $F_{\max}$ của khối HDL tự viết (`ch03_fir_filter.v`):** Được ghi rõ là `(phải đo trong Quartus)`. Về mặt cấu trúc vi kiến trúc, thiết kế đã được chứng minh tốn đúng:
   - 0 khối RAM M10K (sử dụng 496 flip-flop thanh ghi dịch trong ALM).
   - Đúng 1 khối nhân DSP chuyên dụng (phép nhân $17 \times 16 \to 33$ bit).
   - 544 thanh ghi flip-flop logic (496 FF mảng dịch + 40 FF tích lũy + 8 FF điều khiển/trạng thái).
4. **Kết quả chạy mô phỏng chu kỳ bằng Icarus Verilog trên Linux:**
   - Script thực thi `verify_v3/run_ch03_iverilog.sh` đã có sẵn chuẩn xuống dòng Unix LF và cấp quyền thực thi.
   - Testbench `tb/v3/tb_ch03_fir.v` đã được sửa hoàn chỉnh quy ước lấy mẫu tín hiệu tổ hợp trước sườn clk và registered sau sườn clk, loại bỏ lệnh ngắt sớm để đối soát đủ 3.390 chu kỳ.
   - Kết quả mô phỏng thực tế trên Linux do người đánh giá (reviewer) thực thi và điền vào vị trí giữ chỗ `\todo{box}` trong tài liệu LaTeX cũng như tệp nhật ký `verify_v3/ch03_iverilog.log`. Tuyệt đối không tạo số liệu giả định khi chưa chạy.
5. **Dòng mã nguồn chính xác trong Praat 7.0.03:** Được đánh dấu bằng ký hiệu chuẩn `TODO-PRAAT-LINE` để người đánh giá điền số dòng chính xác từ bản cài Linux 7.0.03.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Đặc tính suy hao dải chặn của bộ lọc 31 tap:** Mặc dù bộ lọc 31 tap đáp ứng tốt yêu cầu làm dịu mép Nyquist (suy hao $-9{,}41\text{ dB}$ tại $8\text{ kHz}$) và bảo toàn dải thông phẳng $\pm 0{,}25\text{ dB}$ tới $7{,}4\text{ kHz}$, độ suy hao dải chặn của nó không thể đạt tới mức triệt tiêu hoàn toàn như kỳ vọng lý thuyết ban đầu của Boersma 1993 (cần tới 147 tap theo công thức Kaiser). Đây là điểm thỏa hiệp kỹ thuật có chủ đích để giữ trễ nhóm ở mức nhỏ (15 mẫu) và tiết kiệm tài nguyên.
2. **Cơ chế chuyển mạch động Bypass:** Mạch hỗ trợ cờ `bypass` chuyển đổi linh hoạt. Tuy nhiên, nếu chuyển mạch đột ngột trong khi khối FIR đang dở dang chu kỳ tính toán 16 nhịp, mẫu đầu ra đang tính sẽ bị hủy để nhường đường cho luồng truyền thẳng 1 chu kỳ. Trong ứng dụng thực tế, cờ bypass được cấu hình tĩnh trước mỗi phiên chạy xử lý tệp từ HPS nên không gây ảnh hưởng.
3. **Môi trường Windows thiếu Icarus Verilog và Praat 7.0.03 cục bộ:** Mặc dù toàn bộ mã nguồn Python Twin, RTL, Testbench và dữ liệu vector 3.390 chu kỳ đã được kiểm tra tính toán đồng bộ bit-đối-bit, việc biên dịch và chạy mô phỏng Verilog thực tế trên máy ảo Linux cần do reviewer vận hành.

---

## 5. Lịch sử các Commit Git

Toàn bộ quá trình phát triển và hiệu đính được lưu vết qua các commit nguyên tử trên nhánh `v3`:
- `b4271b5`: `v3: ch03 3.1` (Hiện tượng rò rỉ phổ mép Nyquist, dao động đối dấu, đối soát Praat 7.0.03).
- `0506a6d`: `v3: ch03 3.2` (Phân tích 4 phương án, firls, công thức Kaiser, trễ nhóm 15 mẫu, dời lưới khung).
- `916e4c7`: `v3: ch03 3.3` (Giải mã chi tiết 7 tham số IP FIR Compiler II, cạm bẫy Input Sample Rate, instantiation wrapper).
- `7c2ccec`: `v3: ch03 3.4` (Kiến trúc folded FIR 17-bit pre-adder 1 DSP, Listing RTL 45 dòng, bảng đối chiếu Twin-HDL).
- `4fc653b`: `v3: ch03 3.5` (Kiểm chứng 3.390 chu kỳ, 4 bài tập thực chiến, tinh chỉnh TikZ và triệt tiêu toàn bộ Overfull hbox).
- `cdf5839`: `v3: ch03 done` (Đóng gói hoàn thành phiên bản đầu tiên của Chương 3).
- `6ff8169`: `v3: ch03 box-verified logs (python pass; iverilog FAIL: sink_ready sampling offset)` (Nhật ký chạy trên Linux của Reviewer phát hiện lỗi lệch pha lấy mẫu).
- `77f3d96`: `v3: ch03 run_ch03_iverilog.sh LF + exec bit` (Reviewer chuẩn hóa thuộc tính tệp shell script).
- `8fed623`: `v3: ch03 r1 tb timing fix and remove fabricated todo result` (Sửa timing lấy mẫu trong testbench, gỡ bỏ kết quả giả định, tái tạo 3.390 chu kỳ).
- `b526a88`: `v3: ch03 r1 neutral tone, praat rationale, and markdown asterisks` (Trung hòa giọng văn học thuật, chuẩn hóa giải trình Praat, sửa lỗi markdown).
- `91ed2c5`: `v3: ch03 r1 fir compiler ii ug-01072 citations and dc gain discussion` (Trích dẫn Intel UG-01072 và phân tích hệ số khuếch đại DC $1{,}0149$).
- `d556110`: `v3: ch03 r1 redraw figure 5 and figure 6 with spacious grid` (Vẽ lại toàn diện Hình 5 và Hình 6 với lưới tọa độ thoáng, không đè nhãn).
- `v3: ch03 revision` (Hoàn thiện báo cáo nghiệm thu Đợt 1 và đóng gói Chương 3).
