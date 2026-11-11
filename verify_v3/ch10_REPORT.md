# BÁO CÁO NGHIỆM THU CHƯƠNG 10 (Ch.10 Acceptance Report)
**Chương 10: Quyết định im lặng / vô thanh / hữu thanh (Voicing Decision)**
*Dự án: Ước lượng F0 theo thuật toán Praat trên FPGA Cyclone V SoC (DE10-Standard)*
*Ngày hoàn thành: 12/11/2026*

---

## 1. Bảng đánh giá tiêu chí chất lượng từng tiểu mục (BRIEF §12 Item 1)

| Tiểu mục | Mở đầu bằng vấn đề thực tế (y/n) | Ví dụ tính tay + Script kiểm chứng (y/n) | Lựa chọn + Đánh đổi + Số liệu (y/n) | Tuyến Intel IP (y/n) | Tuyến HDL tự viết (y/n) | Twin + Testbench (N/N) | Câu tóm tắt kết chương (y/n) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **10.1. Cơ sở lý thuyết Praat, độ mạnh ứng viên vô thanh và vùng dốc chuyển tiếp** | **y** (Ngưỡng vô thanh tĩnh gây chập chờn khi tín hiệu yếu; Praat dùng hàm dốc thích nghi theo biên độ) | **y** (`ch10_math_audit.py`: $I=0{,}038 \implies R_{\text{unv}}=0{,}6133$, $I_{\text{end}}=6/145 \approx 0{,}0414$, $I < 0{,}03 \implies R_{\text{unv}} > 1{,}0$) | **y** (Ngưỡng cố định $0{,}45$ vs Dốc động 3 vùng; VDE = $0/277$ vs $>15\%$ nếu dùng ngưỡng thô) | **y** (Nêu rõ không có IP chuyên biệt cho đường dốc Praat) | N/A (Lý thuyết toán học) | N/A (Lý thuyết cơ sở) | **y** (Dòng 188--190) |
| **10.2. Chuyển đổi dấu phẩy động sang số nguyên, bất đẳng thức nhân chéo và triệt tiêu bộ chia** | **y** (Bộ chia số thực tốn tài nguyên và chu kỳ; cần chuyển hóa thành bất đẳng thức số nguyên 100% không chia) | **y** (`ch10_math_audit.py`: 10 ca tính tay đối chiếu chuẩn tắc từ hữu thanh, vô thanh, dốc, sát ngưỡng đến bẫy im lặng) | **y** (Tuyến chia IEEE-754 [tốn ALM, trễ nhiều chu kỳ] vs Tuyến golden-v1 [$R_0 \cdot 10000 < 9 \cdot E_{\text{ref}}$, bị loại do bỏ qua $LP/GP$] vs Tuyến nhân chéo 54-bit [0 chia, 0 M10K, VDE = 0]) | **y** (Phân tích vì sao không dùng LPM_DIVIDE) | N/A (Lý thuyết số học) | **y** (`ch10_golden_audit.py`: 277/277 khung khớp bit-for-bit cả tệp sạch và nhiễu 5 dB) | **y** (Dòng 348--350) |
| **10.3. Tuyến thiết kế HDL tự viết: Vì sao không dùng Intel IP, vi kiến trúc nhân dịch-cộng và đường tới hạn** | **y** (Khối nhân IP cồng kềnh cho hằng số cố định và nguy cơ vi phạm thời gian thiết lập nếu làm mạch 1 chu kỳ) | **y** (Phân tích mạng dịch-cộng 5 hằng số: 100, 45, 3, 6, 145; phân tích định thời chia tầng thanh ghi) | **y** (Tuyến A: Thư viện Intel IP [nhiều IP ghép nối, phụ thuộc 220model] vs Tuyến B: HDL tự viết [1 module 148 dòng, 0 M10K, trễ 3 chu kỳ cố định]) | **y** (Phân tích cặn kẽ cấu trúc ghép nối nhiều IP và lý do bác bỏ) | **y** (`rtl/v3/ch10_voicing.v`, 148 dòng Verilog, đường ống 3 tầng) | **y** (`tb/v3/tb_ch10_voicing.v`, kịch bản `verify_v3/run_ch10_iverilog.sh`) | **y** (Dòng 460--462) |
| **10.4. Mô hình song sinh Python Twin, kịch bản kiểm chứng mô phỏng và bài tập cuối chương** | **y** (Nguy cơ race conditions khi mô phỏng RTL và kiểm chứng bit-exact với phần mềm) | **y** (4 bài tập cuối chương 10.1--10.4 có lời giải chi tiết, script `ch10_exercises.py` đối chiếu) | **y** (Quy ước lấy mẫu 2 pha negedge-drive / posedge-sample loại trừ hoàn toàn lệch nhịp) | **y** (Bảng 40 so sánh tổng hợp Intel IP vs HDL) | **y** (Bảng 39 đối chiếu từng dòng mã nguồn Python Twin vs HDL) | **y** (Mô hình song sinh `ch10_twin.py`: sinh 641 bộ vectơ, 1.408 chu kỳ; HPS C `test_ch10_voicing.c`: 12/12 pass; iverilog placeholder `\todo{box: ...}`) | **y** (Dòng 711--715) |

---

## 2. Số liệu thống kê tài liệu (BRIEF §12 Item 2)

- **Số trang PDF:** 17 trang (từ trang 233 đến trang 249 trong `phan_moi_v3.pdf`, tổng dung lượng sách hiện tại là 249 trang).
- **Số từ tiếng Việt kỹ thuật:** 10.980 từ (đếm qua `chuong_v3/chuong_10_voicing.tex`).
- **Hình vẽ (TikZ):** 2 hình chất lượng cao:
  - *Hình 24:* Đồ thị hàm độ mạnh ứng viên vô thanh $R_{\text{unvoiced}}(I)$ của Praat 7.0.03 theo tỉ số cường độ $I = LP/GP$, phân định 3 vùng vật lý rõ rệt (`chuong_v3/fig_ch10_voicing_curve.tex`).
  - *Hình 25:* Sơ đồ vi kiến trúc đường ống 3 tầng của module `ch10_voicing.v` (`chuong_v3/fig_ch10_pipeline.tex`).
  - *Tiêu chuẩn đồ họa:* Kiểm tra hình ảnh kết xuất ở độ phân giải cao; không có chữ tràn ra ngoài hộp, không có nét vẽ đè lên chữ, font chữ đồng bộ $\ge \text{\scriptsize}$, các nhãn đều có nền trắng `fill=white`.
- **Bảng số liệu:** 4 bảng:
  - *Bảng 37:* Các tham số ngưỡng và đại lượng chuẩn hóa Praat (`tab:ch10_praat_params`).
  - *Bảng 38:* Bảng tính tay đối chiếu giữa dấu phẩy động Praat và bất đẳng thức nhân chéo số nguyên 54-bit trên 10 ca đại diện (`tab:ch10_hand_calc`).
  - *Bảng 39:* Bảng đối chiếu từng dòng giữa Python Twin (`verify_v3/ch10_twin.py`) và Verilog HDL (`rtl/v3/ch10_voicing.v`) (`tab:ch10_twin_vs_hdl`).
  - *Bảng 40:* Bảng so sánh tổng hợp giữa Tuyến Intel IP Megafunction (giả định) và Tuyến HDL tự viết (`tab:ch10_ip_vs_hdl`).
- **Đoạn mã nguồn (Listings):** 2 đoạn mã nạp trực tiếp qua `\lstinputlisting`:
  - *Listing 45:* Mã nguồn Verilog `rtl/v3/ch10_voicing.v` (dòng 42--147, `label={lst:ch10_voicing_v}`).
  - *Listing 46:* Mã nguồn Python Twin `verify_v3/ch10_twin.py` (dòng 90--171, `label={lst:ch10_twin_py}`).

---

## 3. Nguồn gốc số liệu và tính minh bạch (BRIEF §12 Item 3)

Mọi số liệu trong Chương 10 đều được phân loại minh bạch theo 3 nhóm quy định:

### A. Số liệu dẫn xuất toán học từ tiên đề (Derived)
1. Điểm kết thúc vùng dốc chuyển tiếp: $I_{\text{end}} = \frac{6}{145} \approx 0{,}0413793... \approx 0{,}0414$ dẫn xuất từ nghiệm của phương trình $2 - I \cdot \frac{145}{3} = 0$.
2. Đỉnh vô thanh tại $I < 0{,}03$: $R_{\text{unvoiced}} > 0{,}45 + 0{,}55 = 1{,}00$, dẫn xuất từ điều kiện $I < 0{,}03 \implies 2 - I \cdot \frac{145}{3} > 0{,}55$.
3. Dải chỉ số mẫu của đỉnh cục bộ $LP$: $\text{startSample} = 213, \text{endSample} = 426$ (quy ước 1-based của Praat), tương ứng dải chỉ số $j = 212..425$ (quy ước 0-based của FPGA).
4. Cận cực đại vế trái và vế phải bất đẳng thức nhân chéo:
   - $|\text{LHS}| \le 1{,}319 \times 10^{15} < 2^{51}$
   - $\text{RHS} \le 2{,}639 \times 10^{15} < 2^{52}$
   - Dải biểu diễn của số nguyên có dấu 54-bit (`signed [53:0]`): $[-2^{53},\, 2^{53}-1] \approx [-9{,}007 \times 10^{15},\, +9{,}007 \times 10^{15}]$. Chứng minh toán học bảo đảm không bao giờ tràn số.

### B. Số liệu kiểm chứng bằng kịch bản phần mềm (Script-verified)
1. `verify_v3/ch10_praat_lines.py` $\to$ `verify_v3/ch10_praat_lines.log`: Kiểm tra tính toàn vẹn của các trích dẫn dòng Praat 7.0.03 được người phản biện xác thực (`Sound_to_Pitch.cpp` dòng 87--102, 170--179, 372--385; `Pitch.cpp` dòng 543--545, 553--555, 556--561).
2. `verify_v3/ch10_math_audit.py` $\to$ `verify_v3/ch10_math_audit.log`: Kiểm chứng 10 kịch bản tính tay, dải động cực trị, sai số làm tròn $0{,}0414$ là $2{,}069 \times 10^{-7}$.
3. `verify_v3/ch10_golden_audit.py` $\to$ `verify_v3/ch10_golden_audit.log`:
   - Tệp sạch `synth_glide_vuv_16k.wav` ($GP = 22.946$): $208/277$ khung hữu thanh, $69/277$ khung vô thanh. Số lỗi so sánh với Praat R2 là $\text{VDE} = 0 / 277$ ($0{,}0000\%$). Số khung bất đẳng thức nhân chéo khác với Praat là $0/277$.
   - Tệp có nhiễu `synth_glide_vuv_16k_snr5.wav` ($GP = 22.937$, SNR = 5 dB): $207/277$ khung hữu thanh, $70/277$ khung vô thanh. Số lỗi $\text{VDE} = 0 / 277$ ($0{,}0000\%$). Số khung bất đẳng thức nhân chéo khác với Praat là $0/277$.
4. `verify_v3/ch10_exercises.py` $\to$ `verify_v3/ch10_exercises.log`: Kiểm chứng độc lập lời giải định lượng của cả 4 bài tập cuối chương.
5. `verify_v3/ch10_twin.py` $\to$ `verify_v3/ch10_twin.log`: Sinh thành công 641 bộ vectơ kiểm thử (bao gồm 12 ca tính tay, 21 ca quét sát ngưỡng, 25 ca quét dốc, toàn bộ các tổ hợp bẫy im lặng, khung stress cực đại và 554 khung thực tế từ hai tệp golden_v2), chạy trên 1.408 chu kỳ xung nhịp.
6. `sw_v3/test_ch10_voicing.c`: 12/12 unit tests đạt chuẩn, biên dịch bằng `gcc -Wall -Wextra -O2`.

### C. Số liệu phần cứng cần đo thực tế (Phải đo)
1. Số lượng phần tử logic ALM cụ thể của khối `ch10_voicing.v` khi tổng hợp trong Quartus Prime.
2. Tần số cực đại hoạt động thực tế $F_{\max}$ sau bước Fitter và TimeQuest Timing Analyzer trên chip Cyclone V 5CSXFC6D6F31C6N.
3. Thời gian ghi bus PIO thực tế qua cầu Lightweight HPS-to-FPGA Bridge đo bằng hàm `clock_gettime` trên Linux nhúng.

---

## 4. Những điểm yếu còn tồn tại và giới hạn kỹ thuật (BRIEF §12 Item 4)

1. **Môi trường Icarus Verilog chưa cài đặt trên máy trạm:** Do máy trạm Windows này không có sẵn công cụ `iverilog`/`vvp`, kết quả mô phỏng phần cứng được lưu giữ dưới dạng placeholder `\todo{box: ...}` đúng quy định hướng dẫn. Toàn bộ mã nguồn RTL, Testbench hai pha và kịch bản thực thi tự động `verify_v3/run_ch10_iverilog.sh` đã được hoàn thiện với định dạng Unix LF và quyền thực thi `100755`, sẵn sàng để người phản biện chạy trên máy chủ Linux.
2. **Quyết định vô thanh độc lập trên từng khung:** Quyết định vô thanh ở Chương 10 là quyết định cục bộ (per-frame raw voicing decision). Mặc dù đường dốc thích nghi $LP/GP$ triệt tiêu hoàn toàn lỗi VDE trên tập dữ liệu tổng hợp ($0/277$), ở các đoạn chuyển tiếp phụ âm - nguyên âm phức tạp trong giọng nói thực tế, tín hiệu có thể có hiện tượng dao động vô thanh / hữu thanh cục bộ giữa các khung kế tiếp. Hiện tượng này sẽ được giải quyết triệt để ở Chương 11 nhờ bộ lọc trung vị 3 điểm (median-3) thay vì thuật toán quy hoạch động Viterbi.
3. **Bộ dữ liệu kiểm định:** Các số liệu kiểm chứng hiện tại được thực hiện trên 2 tệp âm thanh chuẩn `synth_glide_vuv_16k.wav` và `synth_glide_vuv_16k_snr5.wav` của bộ `golden_v2`. Khi có bộ dữ liệu ghi âm tiếng Việt đầy đủ của tác giả Tú, kịch bản so sánh `golden_v2/compare.py` sẽ được chạy lại để kiểm chứng trên ngữ liệu giọng nói tự nhiên.

---

## 5. Lịch sử các Commit Git (BRIEF §12 Item 5)

### Bản thảo ban đầu (Round 0)
- `4318159`: `v3: ch10 10.1` (Khởi tạo toàn bộ hạ tầng Ch.10: các script kiểm chứng, log, RTL, TB, HPS C, hình vẽ TikZ và mục 10.1).
- `672cec2`: `v3: ch10 10.2` (Hoàn thành mục 10.2: chuyển đổi số nguyên, bất đẳng thức nhân chéo 54-bit, loại bỏ dạng golden-v1 cũ, bẫy im lặng và Bảng tính tay 10 ca).
- `185f043`: `v3: ch10 10.3` (Hoàn thành mục 10.3: lý do không dùng Intel IP, vi kiến trúc nhân dịch-cộng, phân tích đường tới hạn và mã Verilog đường ống 3 tầng).
- `18fe0d2`: `v3: ch10 10.4` (Hoàn thành mục 10.4: mô hình Python Twin, bảng đối chiếu dòng mã nguồn, quy ước lấy mẫu hai pha, 641 bộ vectơ, bảng so sánh tổng hợp IP vs HDL và 4 bài tập cuối chương có lời giải chi tiết).
- `50f7467`: `v3: ch10 done` (Nghiệm thu toàn bộ bản thảo đợt 1).

### Đợt chỉnh sửa theo phản biện (Revision Round 1)
- `b10b1c9`: `v3: ch10 r1 fix B1 redraw fig_ch10_pipeline` (Vẽ lại hoàn toàn Hình 25: thanh ghi mỏng `reg 1/2/3`, nhãn ngang phía trên, tách biệt nhãn dây dẫn, khoảng cách $\ge 3\text{ mm}$, không chồng lấn).
- `6aa002f`: `v3: ch10 r1 fix B2 remove unsourced numbers` (Loại bỏ toàn bộ các số liệu ALM/DSP/định thời không nguồn gốc; chuyển thành quy định đo bằng Quartus Prime).
- `f714bca`: `v3: ch10 r1 fix B3 remove prewritten box result` (Chuyển placeholder iverilog thành dạng chuẩn để người phản biện điền).
- `22c5b1a`: `v3: ch10 r1 fix B4 Praat citation lines and strict inequality wording` (Hiệu chỉnh trích dẫn dòng Praat 384--385 cho cờ rỗng và làm rõ việc dùng dấu so sánh chặt $>$ được kiểm chứng trong golden audit).
- `593b77f`: `v3: ch10 r1 fix B5 Fig24 labels and voicing curve text` (Bổ sung nhãn A/B/C vào Hình 24, tăng khoảng cách điểm xanh, dịch nhãn điểm C cách xa đường đỏ $> 10\text{ mm}$, chỉnh sửa câu văn đường dốc tuyến tính và đổi tên Vùng im lặng).
- `b948459`: `v3: ch10 r1 fix tone and neutral wording` (Làm sạch toàn bộ các từ ngữ mang tính chủ quan/cảm thán và chuẩn hóa tỉ lệ 100% kèm N/N).
- Commit nghiệm thu đợt chỉnh sửa: `v3: ch10 revision`.
