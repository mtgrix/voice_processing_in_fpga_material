# BÁO CÁO NGHIỆM THU CHƯƠNG 11 (Ch.11 Acceptance Report)
**Chương 11: Bộ lọc trung vị Median-3 thay cho bộ dò đường Path Finder**
*Dự án: Ước lượng F0 theo thuật toán Praat trên FPGA Cyclone V SoC (DE10-Standard)*
*Ngày hoàn thành: 12/11/2026*

---

## 1. Bảng đánh giá tiêu chí chất lượng từng tiểu mục (BRIEF §12 Item 1)

| Tiểu mục | Mở đầu bằng vấn đề thực tế (y/n) | Ví dụ tính tay + Script kiểm chứng (y/n) | Lựa chọn + Đánh đổi + Số liệu (y/n) | Tuyến Intel IP (y/n) | Tuyến HDL tự viết (y/n) | Twin + Testbench (N/N) | Câu tóm tắt kết chương (y/n) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **11.1. Bộ dò đường Path Finder của Praat 7.0.03 và nguyên nhân loại bỏ Viterbi trên FPGA** | **y** (Lỗi nhảy quãng tám đơn khung khi ghép nối độc lập các giá trị $F_0$; Praat dùng quy hoạch động toàn cục) | **y** (`ch11_praat_lines.py`: 9 trích dẫn xác thực; tính toán ma trận $\delta, \psi$ kích thước $N \times 15$) | **y** (Viterbi toàn cục [tốn $\ge 60\text{ KB}$ SRAM, trễ toàn file, thuật toán logarit phi tuyến] vs Lọc trung vị cục bộ Median-3 [0 RAM M10K, trễ 1 khung, 0 DSP]) | **y** (Nêu rõ không có IP cho Viterbi F0) | N/A (Lý thuyết giải thuật) | N/A (Lý thuyết cơ sở) | **y** (Dòng 193--196) |
| **11.2. Hai cấu hình đối chuẩn R1, R2 và vai trò chuẩn ngang hàng của R2** | **y** (Cần thiết lập một mốc đối chuẩn công bằng giữa phần mềm máy tính và phần cứng FPGA trước bộ lọc trung vị) | **y** (`ch11_viterbi_audit.py`: chứng minh định lý suy biến; max diff $|F_{0,\text{R2}} - F_{0,\text{argmax}}| = 0{,}0\text{ Hz}$ trên 277/277 khung cả tệp sạch và tệp nhiễu 5 dB) | **y** (R1 [Praat mặc định, jump=0,35, vuv=0,14] vs R2 [jump=0,0, vuv=0,0]; phân tích Bảng 41: R1=R2 ở 100% tệp sạch, R1 sửa 19/207 khung nhảy quãng tám của R2 ở tệp nhiễu 5 dB; Median-3 kéo GPE từ 22 xuống 15 khung) | **y** (Phân tích phương pháp luận đối chuẩn) | N/A (Phương pháp luận) | **y** (`ch11_viterbi_audit.log`: 277/277 khung khớp bit-for-bit) | **y** (Dòng 319--322) |
| **11.3. Bản chất toán học của bộ lọc Median-3: Những gì sửa được, không sửa được và tác động tới VDE** | **y** (Vì sao không dùng bộ lọc trung bình tuyến tính trượt 3 điểm: làm nhòe lỗi và sai lệch tần số; bản chất phi tuyến của trung vị) | **y** (`ch11_median_math.py`: 13 trường hợp hoán vị và hòa điểm; ví dụ đề cương $[120, 122, 244, 121, 0, 0] \to [120, 122, 122, 121, 0, 0]$; sửa gai đơn 1 khung vs giữ nguyên gai kép 2 khung; tác động VDE qua số 0) | **y** (Lọc trung bình [nhòe lỗi] vs Median-3 [xóa sạch gai 10 ms, bảo toàn bậc nhảy thật]; phân tích giới hạn không sửa được lỗi $\ge 2$ khung) | N/A (Toán học xử lý tín hiệu) | **y** (Cây quyết định 6 nhánh rút gọn MUX 3 ngõ vào) | **y** (Mô hình toán học kiểm chứng qua script) | **y** (Dòng 438--441) |
| **11.4. Căn khung nhân quả phần cứng, xử lý biên lặp mẫu và nhịp xả (Flush beat)** | **y** (Bộ lọc trung vị căn giữa đòi hỏi mẫu tương lai $x[k+1]$, vi phạm tính nhân quả của dòng chảy thời gian thực) | **y** (`ch11_median_math.py`: bảng vết chu kỳ T1..T7; chu kỳ T1 nạp lặp biên $z_1=z_2=120$; chu kỳ T7 là nhịp xả Flush Beat xuất khung 5 kèm cờ `out_last=1`) | **y** (Trễ 1 khung [$10\text{ ms}$] xuất khung $k-1$ tại chu kỳ $k$; $N$ khung vào cần đúng $N+1$ chu kỳ để xử lý trọn vẹn) | N/A (Định thời phần cứng) | **y** (Sơ đồ FSM 3 trạng thái S_IDLE, S_STREAM, S_FLUSH) | **y** (Giản đồ định thời Hình 27 và Bảng vết 42 khớp 100% từng chu kỳ) | **y** (Dòng 535--538) |
| **11.5. Tuyến thiết kế vi kiến trúc HDL ch11_median3.v và lý do không dùng Intel IP** | **y** (Khảo sát thư viện Intel Megafunction IP và kết luận không có IP cho lọc trung vị; ghép 3 khối LPM_COMPARE gây lãng phí logic keo) | **y** (Mã nguồn Verilog `ch11_median3.v` dưới 150 dòng; kỹ thuật chia sẻ mạng so sánh cho nhịp xả; 0 DSP, 0 M10K) | **y** (Tuyến A: Intel IP [ghép nhiều LPM, phụ thuộc 220model] vs Tuyến B: HDL tự viết [độc lập, tối ưu 100% diện tích, mô phỏng tự do]) | **y** (Phân tích cặn kẽ vì sao không dùng Intel IP) | **y** (`rtl/v3/ch11_median3.v`, tổng hợp 0 DSP, 0 M10K, thông lượng 1 khung/chu kỳ) | **y** (Listing 47 dòng 40--160, phân tích từng khối chức năng) | **y** (Dòng 590--593) |
| **11.6. Mô hình song sinh Python Twin và kịch bản kiểm chứng mô phỏng** | **y** (Nguy cơ race conditions khi mô phỏng RTL và kiểm chứng bit-exact với phần mềm) | **y** (1.065 chu kỳ mô phỏng, 609 ngõ ra hoàn chỉnh; bao phủ góc biên N=1, N=2, gai đơn, gai kép, chuỗi vô thanh, tệp sạch và tệp nhiễu 5 dB) | **y** (Quy ước lấy mẫu hai pha negedge-drive / posedge-sample loại trừ hoàn toàn lệch nhịp) | **y** (Bảng 44 so sánh tổng hợp Intel IP vs HDL) | **y** (Bảng 43 đối chiếu từng dòng mã nguồn Python Twin vs HDL) | **y** (Mô hình song sinh `ch11_twin.py`: sinh vectơ stim/expected; HPS C `test_ch11_median3.c`: 4/4 suite pass; iverilog placeholder `\todo{box: ...}`) | **y** (Dòng 693--696) |
| **11.7. Bài tập cuối chương có lời giải chi tiết** | **y** (Củng cố kiến thức từ suy biến toán học Viterbi, tính toán thủ công trên dãy 10 khung, phân tích định thời phần cứng đến so sánh độ phức tạp với Bubble Sort) | **y** (4 bài tập cuối chương 11.1--11.4 có lời giải chi tiết, script `ch11_exercises.py` đối chiếu độc lập) | **y** (So sánh độ phức tạp: Mạng so sánh 3 phần tử [1 tầng logic, 0 thanh ghi trung gian] vs Bubble Sort [tối đa 3 chu kỳ hoán đổi]; so sánh tài nguyên Cyclone V: Median-3 [0 DSP, 0 M10K] vs Viterbi [$\ge 60\text{ KB}$ SRAM]) | N/A (Bài tập và lời giải) | N/A (Bài tập và lời giải) | **y** (`verify_v3/ch11_exercises.log` xác nhận khớp 100% từng số liệu) | **y** (Dòng 829--831) |

---

## 2. Số liệu thống kê tài liệu (BRIEF §12 Item 2)

- **Số trang PDF:** 17 trang (từ trang 250 đến trang 266 trong `phan_moi_v3.pdf`, tổng dung lượng sách hiện tại là 266 trang).
- **Số từ tiếng Việt kỹ thuật:** 11.636 từ (đếm qua `chuong_v3/chuong_11_median3.tex`).
- **Hình vẽ (TikZ):** 3 hình chất lượng cao:
  - *Hình 26:* Đồ hình Trellis của giải thuật quy hoạch động Viterbi trong Praat Path Finder, minh họa 15 trạng thái ứng viên cạnh tranh mỗi khung, đường đi tối ưu toàn cục (màu đỏ) và bước truy vết ngược ($N \to 1$) (`chuong_v3/fig_ch11_viterbi_trellis.tex`).
  - *Hình 27:* Giản đồ định thời nhân quả của module `ch11_median3.v` cho chuỗi 6 khung $[120, 122, 244, 121, 0, 0]$, thể hiện rõ nhịp nạp lặp biên T1 và nhịp xả Flush Beat T7 (`chuong_v3/fig_ch11_median_timing.tex`).
  - *Hình 28:* Sơ đồ vi kiến trúc phần cứng của module `ch11_median3.v`, phân định rõ ràng giữa đường truyền dữ liệu (chuỗi thanh ghi trễ $\texttt{f0\_z0} \to \texttt{f0\_z1} \to \texttt{f0\_z2}$, mạng 3 bộ so sánh nhị phân, MUX chọn trung vị, thanh ghi chốt $\texttt{f0\_med}$) và khối điều khiển FSM (`chuong_v3/fig_ch11_median3_arch.tex`).
  - *Tiêu chuẩn đồ họa:* Kiểm tra hình ảnh kết xuất ở độ phân giải cao; không có chữ tràn ra ngoài hộp, không có nét vẽ đè lên chữ, font chữ đồng bộ $\ge \text{\scriptsize}$, các nhãn đều có nền trắng `fill=white`.
- **Bảng số liệu:** 4 bảng:
  - *Bảng 41:* Bảng đối chiếu định lượng giữa Praat R1, Praat R2 và lõi phần cứng FPGA trên hai tệp kiểm chứng tổng hợp 277 khung (`tab:ch11_r1_vs_r2`).
  - *Bảng 42:* Bảng vết thanh ghi từng chu kỳ của module `ch11_median3.v` trên dãy 6 khung $[120, 122, 244, 121, 0, 0]$ (`tab:ch11_trace`).
  - *Bảng 43:* Bảng đối chiếu từng dòng giữa Python Twin (`verify_v3/ch11_twin.py`) và Verilog HDL (`rtl/v3/ch11_median3.v`) (`tab:ch11_twin_vs_hdl`).
  - *Bảng 44:* Bảng so sánh tổng hợp giữa Tuyến Intel IP (giả định) và Tuyến HDL tự viết (`tab:ch11_ip_vs_hdl`).
- **Đoạn mã nguồn (Listings):** 2 đoạn mã nạp trực tiếp qua `\lstinputlisting`:
  - *Listing 47:* Mã nguồn Verilog `rtl/v3/ch11_median3.v` (dòng 40--160, `label={lst:ch11_median3_v}`).
  - *Listing 48:* Mã nguồn Python Twin `verify_v3/ch11_twin.py` (dòng 66--141, `label={lst:ch11_twin_py}`).

---

## 3. Nguồn gốc số liệu và tính minh bạch (BRIEF §12 Item 3)

Mọi số liệu trong Chương 11 đều được phân loại minh bạch theo 3 nhóm quy định:

### A. Số liệu dẫn xuất toán học từ tiên đề (Derived)
1. **Định lý suy biến Viterbi:** Khi $\text{octaveJumpCost} = 0$ và $\text{voicedUnvoicedCost} = 0$, $\text{transitionCost}(i_1 \to i_2) \equiv 0$. Khi đó phương trình tích lũy chi phí tách rời thành $\delta[t][i_2] = (\max_{i_1} \delta[t-1][i_1]) + \text{local\_cost}[t][i_2]$. Con trỏ $\psi[t][i_2]$ trở thành hằng số đối với mọi $i_2$, dẫn đến bước truy vết ngược suy biến thành $\text{place}_t \equiv \arg\max_i \text{local\_cost}[t][i]$ độc lập trên từng khung.
2. **Quy tắc đệm biên đối xứng:** Với dãy $N$ mẫu $x[0..N-1]$, đệm lặp mẫu biên tạo chuỗi $x_{\text{pad}} = [x_0,\, x_0,\, x_1,\, \dots,\, x_{N-1},\, x_{N-1}]$ có độ dài $N+2$, cho phép tính trung vị căn giữa tại cả 2 đầu mút mà không bị lệch tần số.
3. **Độ trễ nhân quả và nhịp xả Flush Beat:** Khung $k-1$ được xuất tại chu kỳ nhận khung $k$ (độ trễ 1 khung thời gian $10\text{ ms}$). Toàn bộ tệp gồm $N$ khung ngõ vào đòi hỏi đúng $N+1$ chu kỳ xung nhịp để xử lý và xả hết ra ngoài.
4. **Mạng so sánh 3 phần tử (Sorting Network):** Cần đúng 3 bộ so sánh nhị phân ($a \le b$, $b \le c$, $a \le c$) với độ trễ 1 tầng logic tổ hợp, điều khiển MUX 3 nhánh chọn trung vị.

### B. Số liệu kiểm chứng bằng kịch bản phần mềm (Script-verified)
1. `verify_v3/ch11_praat_lines.py` $\to$ `verify_v3/ch11_praat_lines.log`: Kiểm tra tính toàn vẹn của 9 trích dẫn dòng Praat 7.0.03 được người phản biện xác thực (`Sound_to_Pitch.cpp` dòng 489--491, 170--179; `Pitch.cpp` dòng 524--652, 548--549, 563--567, 574--605, 608--616, 630--639, 641--652).
2. `verify_v3/ch11_viterbi_audit.py` $\to$ `verify_v3/ch11_viterbi_audit.log`:
   - Kiểm chứng định lý suy biến: Max diff $|F_{0,\text{R2}} - F_{0,\text{argmax}}| = 0{,}000000\text{ Hz}$ trên cả 277 khung tệp sạch và 277 khung tệp nhiễu 5 dB (277/277 khớp tuyệt đối).
   - So sánh R1 vs R2:
     - Tệp sạch: $0/277$ khung khác biệt ($0{,}00\%$), VDE = $0/277$, GPE = $0/207$.
     - Tệp nhiễu 5 dB: Khác nhau ở đúng $19/207$ khung hữu thanh ($9{,}18\%$). Tất cả 19 khung này đều là lỗi nhảy quãng tám của R2 mà R1 sửa được nhờ hàm phạt Viterbi ($\text{GPE}_{\text{R1}} = 0/207$, $\text{GPE}_{\text{R2}} = 19/207$).
   - Đánh giá lõi FPGA thô và Median-3 trên tệp nhiễu 5 dB:
     - FPGA thô: $\text{GPE} = 22 / 207$ ($10{,}63\%$).
     - FPGA sau Median-3: $\text{GPE} = 15 / 207$ ($7{,}25\%$). Median-3 triệt tiêu được đúng 7 khung lỗi gai đơn lẻ, nhưng giữ nguyên 15 khung lỗi kéo dài từ 2 khung liên tiếp trở lên.
3. `verify_v3/ch11_median_math.py` $\to$ `verify_v3/ch11_median_math.log`:
   - Kiểm chứng 13 trường hợp hoán vị và hòa điểm của mạng 3 bộ so sánh.
   - Kiểm chứng ví dụ tính tay đề cương: $[120, 122, 244, 121, 0, 0] \to [120, 122, 122, 121, 0, 0]$.
   - Kiểm chứng triệt tiêu gai đơn lẻ 1 khung ($1600 \to 3200 \to 1600 \implies 1600$) và tính bền vững của gai kép 2 khung ($1800 \to 3600 \to 3600 \to 1800 \implies$ giữ nguyên 3600).
   - Kiểm chứng tác động VDE qua số 0: triệt tiêu đốm sáng giả $[0, 0, 150, 0, 0] \to 0$ và hàn gắn mất tiếng đơn khung $[150, 150, 0, 150, 150] \to 150$.
   - Bảng vết chu kỳ T1..T7 xác nhận mạch phần cứng hoàn thành đúng 7 chu kỳ.
4. `verify_v3/ch11_exercises.py` $\to$ `verify_v3/ch11_exercises.log`: Kiểm chứng độc lập lời giải định lượng của cả 4 bài tập cuối chương 11.1--11.4.
5. `verify_v3/ch11_twin.py` $\to$ `verify_v3/ch11_twin.log`: Sinh 1.065 chu kỳ mô phỏng, 609 ngõ ra hoàn chỉnh, ghi stimulus và expected bao phủ toàn diện các kịch bản thử nghiệm.
6. `sw_v3/test_ch11_median3.c`: 4/4 bài kiểm tra đơn vị đạt chuẩn (13 ca hoán vị, ví dụ tính tay, trường hợp biên N=1 và N=2, gai đơn/gai kép/mất tiếng), biên dịch bằng `gcc -Wall -Wextra -O2`.

### C. Số liệu phần cứng cần đo thực tế (Phải đo)
1. Số lượng phần tử logic ALM cụ thể của khối `ch11_median3.v` khi tổng hợp trong Quartus Prime.
2. Tần số cực đại hoạt động thực tế $F_{\max}$ sau bước Fitter và TimeQuest Timing Analyzer trên chip Cyclone V 5CSXFC6D6F31C6N.

---

## 4. Những điểm yếu còn tồn tại và giới hạn kỹ thuật (BRIEF §12 Item 4)

1. **Môi trường Icarus Verilog chưa cài đặt trên máy trạm:** Do máy trạm Windows này không có sẵn công cụ `iverilog`/`vvp`, kết quả mô phỏng phần cứng được lưu giữ dưới dạng placeholder `\todo{box: ...}` đúng quy định hướng dẫn. Toàn bộ mã nguồn RTL, Testbench hai pha và kịch bản thực thi tự động `verify_v3/run_ch11_iverilog.sh` đã được hoàn thiện với định dạng Unix LF và quyền thực thi `100755`, sẵn sàng để người phản biện chạy trên máy chủ Linux.
2. **Giới hạn tự nhiên của bộ lọc trung vị 3 điểm:** Median-3 chỉ có khả năng loại bỏ các xung lỗi cục bộ kéo dài đúng 1 khung phân tích ($10\text{ ms}$). Khi hiện tượng nhảy quãng tám hoặc nhiễu làm biến dạng hàm tự tương quan kéo dài từ 2 khung liên tiếp trở lên (chiếm đa số trong cửa sổ quan sát 3 điểm), bộ lọc trung vị hoàn toàn bất lực và giữ nguyên giá trị lỗi (minh chứng qua 15 khung lỗi còn lại trên tệp nhiễu 5 dB). Do đó, Median-3 không thể thay thế toàn diện năng lực tối ưu hóa toàn cục của thuật toán Viterbi Path Finder.
3. **Độ trễ xử lý 1 khung thời gian:** Do bản chất căn giữa của bộ lọc trung vị, ngõ ra bị trễ đúng 1 khung ($10\text{ ms}$) so với luồng dữ liệu thời gian thực và đòi hỏi thêm một nhịp xả tự động (Flush beat) tại khung cuối cùng.
4. **Bộ dữ liệu kiểm định:** Các số liệu kiểm chứng hiện tại được thực hiện trên 2 tệp âm thanh chuẩn `synth_glide_vuv_16k.wav` và `synth_glide_vuv_16k_snr5.wav` của bộ `golden_v2`. Khi có bộ dữ liệu ghi âm tiếng Việt đầy đủ của tác giả Tú, kịch bản so sánh sẽ được chạy lại để kiểm chứng trên ngữ liệu giọng nói tự nhiên.

---

## 5. Lịch sử các Commit Git (BRIEF §12 Item 5)

- `0dc9464`: `v3: ch11 median-3 thay cho path finder` (Hoàn thành toàn bộ Chương 11: cơ sở toán học Viterbi, định lý suy biến R2, bản chất phi tuyến Median-3, giản đồ định thời căn khung nhân quả, RTL `ch11_median3.v`, TB `tb_ch11_median3.v`, runner `run_ch11_iverilog.sh`, HPS C `ch11_median3.c`, Makefile target `ch11`, 3 hình vẽ TikZ, 4 bảng biểu, 2 listings, 4 bài tập cuối chương có lời giải chi tiết, biên dịch xelatex 0 lỗi 0 overfull > 10pt).
- `ef56425`: `v3: ch11 done` (Nghiệm thu toàn bộ Chương 11 và chốt báo cáo nghiệm thu).
