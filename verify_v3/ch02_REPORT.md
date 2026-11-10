# Báo cáo nghiệm thu Chương 2 — Avalon-ST, Ngân sách chu kỳ, Mã hóa FSM (v3)

Theo quy định hợp đồng kỹ thuật tại **Mục 12 của BRIEF_v3.md** và đề cương kỹ thuật **Ch.2 của agenda_chot_v2_2026-11-10.md**, dưới đây là báo cáo kiểm chứng toàn diện cho Chương 2: `chuong_v3/chuong_02_avalon_st_fsm.tex`.

---

## 1. Bảng đánh giá chi tiết theo từng tiểu mục (Subsection Checklist)

| Tiểu mục | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / minh họa số? | Phương án + đánh đổi + lựa chọn có số? | Đường IP (A)? | Đường HDL (B)? | Twin Python & Testbench | Câu tóm lại (*Tóm lại: ...*)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2.1. Chuẩn giao tiếp Avalon-ST và cơ chế bắt tay readyLatency** | Có (nguy cơ mất gói tin hoặc đóng băng đường ống do lệch readyLatency giữa hai khối kết nối) | Có (bảng vết chu kỳ CK0..CK8, trễ phản áp tại CK5 dẫn tới mất mẫu 12 tại CK6 khi sender RL=1, receiver RL=0) | Có (phân tích so sánh readyLatency=0 đáp ứng tức thời vs readyLatency=1 trễ 1 chu kỳ) | Có (chuẩn giao diện Avalon-ST Intel Specification) | Có (quy ước tín hiệu `valid`/`ready`/`data` đồng bộ sườn dương) | 9 chu kỳ trace toán học (`ch02_avalon_st_trace.py`) | Có (`\textit{Tóm lại: Trong toàn bộ kiến trúc ước lượng F0...}`) |
| **2.2. Ngân sách chu kỳ khi đầu vào là tệp dữ liệu** | Có (ngộ nhận tai hại rằng xung nhịp lấy mẫu âm thanh 16 kHz áp đặt nhịp độ xử lý của mạch FPGA) | Có (dẫn xuất từ nguyên lý đầu tiên: 50 MHz $\to$ 500.000 chu kỳ/khung; MAC: 638 + 97.902 = 98.540 phép tính; tổng 98.543 chu kỳ/khung; 616 chu kỳ/mẫu; RTF 0,197) | Có (Bảng 11 phân tích chi tiết ngân sách chu kỳ; bóc tách lỗi triệt tiêu kép của tài liệu v1) | N/A (đây là ngân sách thuật toán và kiến trúc lõi) | Đối chiếu với thiết kế bộ đếm cặp `rtl/v3/ch00_pair_counter.v` và MAC Ch.7 | 100% khớp số học giải tích (`ch02_cycle_budget.py`) | Có (`\textit{Tóm lại: Khi xử lý tín hiệu từ tệp dữ liệu...}`) |
| **2.3. Mã hóa máy trạng thái hữu hạn (FSM)** | Có (nguy cơ lỗi chuyển trạng thái và suy giảm Fmax do logic tổ hợp giải mã ngõ ra phức tạp) | Có (FSM 5 trạng thái: IDLE, LOAD, CALC, NORM, DONE; phân tích 166.036 flip-flop của Cyclone V; chứng minh toán học mã Gray $n \oplus (n \gg 1)$ bằng chuỗi bit 1 tận cùng) | Có (Bảng 12 so sánh 6 chế độ mã hóa: Auto, One-Hot, Minimal Bits, Gray, Johnson, User-Encoded với số FF và hàm logic) | Có (chế độ State Machine Processing của trình biên dịch Quartus Prime) | Có (hai hiện thực song song: `rtl/v3/ch02_fsm_binary.v` và `rtl/v3/ch02_fsm_onehot.v`) | 500 chu kỳ so sánh nhịp-cho-nhịp (`ch02_fsm_twin.py`, `tb/v3/tb_ch02_fsm_equiv.v`) | Có (`\textit{Tóm lại: Trên kiến trúc Cyclone V SoC giàu thanh ghi...}`) |
| **2.4. Khối đệm trượt (Skid Buffer)** | Có (chuỗi lan truyền phản áp tổ hợp ngược dòng làm giảm Fmax trầm trọng khi readyLatency=0) | Có (vết hoạt động 2 chu kỳ nạp/xả đệm trượt trong Bảng 13; sơ đồ kiến trúc TikZ Hình 4) | Có (so sánh FIFO 2 phần tử vs Skid Buffer chuyên dụng; chi phí 1 thanh ghi đệm phụ vs bảo toàn 100% thông lượng) | Đối chiếu Avalon-ST Pipeline Bridge IP | Có (mã nguồn hoàn chỉnh `rtl/v3/ch02_skid_buffer.v`) | 600 chu kỳ kích thích ngẫu nhiên (`ch02_skid_twin.py`, `tb/v3/tb_ch02_skid_buffer.v`) | Có (`\textit{Tóm lại: Khối đệm trượt là một mẫu thiết kế không thể thiếu...}`) |
| **2.5. Kiểm chứng ba tầng và bài tập thực hành** | Có (khoảng cách giữa mô hình toán học Python, mô phỏng RTL và ánh xạ vật lý trên FPGA) | Có (Bảng 14 đối chiếu IP vs HDL; quy trình kiểm chứng ba tầng; 4 bài tập thực hành có lời giải mẫu chi tiết) | Có (đối chiếu tài nguyên, độ trễ và khả năng di động giữa Intel IP và HDL độc lập) | Phân tích Intel Avalon-ST Pipeline Bridge | Phân tích Skid Buffer tự phát triển | Bộ kích thích và tệp kỳ vọng đồng bộ chu kỳ | Có (`\textit{Tóm lại: Chiến lược kiểm chứng ba tầng...}`) |

---

## 2. Thống kê khối lượng tài liệu và ấn phẩm

- **Số trang văn bản:** 17 trang (từ trang 59 đến trang 75 trong `phan_moi_v3.pdf`).
- **Số từ (Word count):** 12.005 từ (769 dòng mã LaTeX trong `chuong_v3/chuong_02_avalon_st_fsm.tex`).
- **Hình vẽ TikZ:** 2 hình chính được biên dịch kiểm tra trực quan ở độ phân giải cao:
  1. `fig:ch02_readylatency` (trang 60): Giản đồ xung so sánh cơ chế bắt tay Avalon-ST giữa readyLatency = 0 và readyLatency = 1, làm nổi bật chu kỳ thất thoát mẫu.
  2. `fig:ch02_skid_buffer` (trang 69): Sơ đồ kiến trúc vi mô của khối đệm trượt Skid Buffer, phân định rõ mạch chốt thuận (forward register) và mạch chốt nghịch (backward skid register).
  - *Kiểm tra chất lượng đồ họa:* Đã xuất hình ảnh qua `pdftoppm -r 300`, xác nhận không có chữ chạm viền hộp và không có đường kẻ cắt ngang chữ.
- **Bảng số liệu tổng hợp:** 5 bảng kỹ thuật chi tiết:
  1. Bảng 10: Vết chu kỳ bắt tay Avalon-ST và lỗi lệch readyLatency (CK0 đến CK8).
  2. Bảng 11: Bảng phân tích ngân sách chu kỳ xử lý từ tệp dữ liệu trên FPGA Cyclone V (tần số 50 MHz).
  3. Bảng 12: So sánh 6 phương thức mã hóa FSM của Quartus Prime trên FPGA Cyclone V SoC.
  4. Bảng 13: Vết chu kỳ hoạt động chi tiết của Skid Buffer trong tình huống nghẽn hạ nguồn 2 chu kỳ.
  5. Bảng 14: So sánh toàn diện giữa Intel Avalon-ST Pipeline Bridge IP và Skid Buffer tự phát triển.
- **Đoạn mã nguồn trích dẫn:** 2 khối mã nguồn chính:
  1. Module Verilog hoàn chỉnh của khối đệm trượt `ch02_skid_buffer.v`.
  2. Hàm xử lý chu kỳ nhịp-cho-nhịp của mô hình đôi song sinh Python `SkidBufferTwin.step`.
- **Hộp bài tập thực hành cuối chương:** 4 bài tập chuyên sâu kèm lời giải mẫu từng bước:
  1. Bài tập 1: Đánh giá độ trễ và thông lượng khi ghép tầng Skid Buffer.
  2. Bài tập 2: Tính toán đường tới hạn của chuỗi phản áp tổ hợp khi không dùng Skid Buffer.
  3. Bài tập 3: Dẫn xuất mã Gray 4-bit và kiểm chứng chuỗi bit 1 tận cùng (trailing-ones).
  4. Bài tập 4: Đánh giá chi phí phần cứng của FSM điều khiển tự tương quan.
- **Trạng thái biên dịch XeLaTeX:**
  - Biên dịch 2 lượt với MiKTeX XeLaTeX trên `phan_moi_v3.tex`.
  - Kết quả: **0 lỗi LaTeX**, **0 Overfull `\hbox`** trên toàn bộ tài liệu 75 trang.

---

## 3. Danh mục các số liệu kỹ thuật, số liệu kiểm chứng và hạng mục "Phải đo"

### 3.1. Các số liệu suy diễn từ nguyên lý đầu tiên (Derived Numbers)
- **Tần số hệ thống:** $f_{\text{clk}} = 50\text{ MHz} \implies T_{\text{clk}} = 20\text{ ns}$.
- **Tần số âm thanh tiêu chuẩn:** $f_s = 16\text{ kHz} \implies T_s = 62{,}5\ \mu\text{s}$.
- **Thước đo thời gian thực:** $50\text{ MHz} / 16\text{ kHz} = 3.125$ chu kỳ/mẫu.
- **Bước nhảy khung (hop size):** $\Delta t = 10\text{ ms} \implies H = 160$ mẫu âm thanh mới.
- **Ngân sách thời gian thực cho một bước nhảy:** $10\text{ ms} \times 50\text{ MHz} = 500.000$ chu kỳ xung nhịp.
- **Chiều dài cửa sổ phân tích:** $N = 638$ mẫu.
- **Phạm vi độ trễ tự tương quan:** $\tau_{\min} = 26$, $\tau_{\max} = 214$ mẫu (189 giá trị $\tau$).
- **Tổng số phép nhân-cộng (MAC) tính toán tự tương quan:**
  $$R[0] = 638 \quad \text{phép tính}$$
  $$\sum_{\tau=26}^{214} (638 - \tau) = 189 \times 638 - \frac{189 \times (26 + 214)}{2} = 120.582 - 22.680 = 97.902 \quad \text{phép tính}$$
  $$\text{Tổng số MAC} = 638 + 97.902 = 98.540 \quad \text{phép tính}$$
- **Tổng chu kỳ thực thi khối MAC (với 3 chu kỳ trễ đường ống):** $98.540 + 3 = 98.543$ chu kỳ/khung.
- **Số chu kỳ trung bình cho mỗi mẫu âm thanh:** $98.543 / 160 = 615{,}89375 \approx 616$ chu kỳ/mẫu.
- **Hệ số thời gian thực (Real-Time Factor):**
  $$\text{RTF}_{\text{MAC}} = \frac{98.543}{500.000} \approx 0{,}197086 \approx 0{,}197$$
- **Số lượng thanh ghi logic trên chip Cyclone V 5CSXFC6D6F31C6N:**
  $$41.910\ \text{ALMs} \times 4\ \text{thanh ghi/ALM} = 166.036\ \text{thanh ghi}$$
  *(Đính chính sai lệch của tài liệu v1 vốn ghi nhầm thành 68.000 thanh ghi).*

### 3.2. Các số liệu đã kiểm chứng bằng kịch bản Python (Script-Verified Numbers)
1. `verify_v3/ch02_avalon_st_trace.py`:
   - Xác nhận bảng vết 9 chu kỳ (CK0..CK8) của giao thức Avalon-ST.
   - Khi Master phát theo chuẩn readyLatency = 1 còn Slave tiếp nhận theo chuẩn readyLatency = 0, việc hạ tín hiệu `ready = 0` tại CK5 dẫn tới thất thoát chính xác mẫu số 12 tại chu kỳ CK6.
2. `verify_v3/ch02_cycle_budget.py`:
   - Xác minh toàn bộ các giá trị tích lũy số học, số chu kỳ/mẫu 615,89, RTF 0,197086.
   - Bóc tách bản chất lỗi triệt tiêu kép của tài liệu v1 (ngân sách 1.250.000 chu kỳ do nhầm bước nhảy 25 ms và 246.000 chu kỳ MAC do nhầm cửa sổ 640 mẫu, vô tình tạo ra tỷ số $246.000 / 1.250.000 = 0{,}1968 \approx 0{,}197$).
3. `verify_v3/ch02_gray_code.py`:
   - Kiểm chứng toán học công thức $G(n) = n \oplus (n \gg 1)$ trên toàn bộ không gian số nguyên từ 1 đến 65.535 ($2^{16}-1$). Xác nhận với mọi bước nhảy $n \to n+1$, hàm khoảng cách Hamming $\text{popcount}(G(n) \oplus G(n+1)) = 1$ tuyệt đối.
   - Chứng minh giải tích dựa trên cấu trúc chuỗi bit 1 tận cùng (trailing ones).
4. `verify_v3/ch02_skid_twin.py`:
   - Tạo bộ kích thích ngẫu nhiên 600 chu kỳ bao gồm các chuỗi phản áp liên tục và gián đoạn.
   - Kiểm chứng mô hình đôi song sinh Python: 0 thất thoát dữ liệu, 0 trùng lặp, bảo toàn 100% thứ tự gói tin, xuất tệp kỳ vọng `tb_ch02_skid_expected.txt`.
5. `verify_v3/ch02_fsm_twin.py`:
   - Tạo bộ kích thích 500 chu kỳ cho máy trạng thái FSM điều khiển tự tương quan.
   - Kiểm chứng tương đương chu kỳ-cho-chu kỳ giữa hiện thực mã hóa nhị phân (Binary) và một-nóng (One-Hot), xuất tệp kỳ vọng `tb_ch02_fsm_expected.txt`.
6. `verify_v3/ch02_praat_lines.py`:
   - Kiểm tra các vị trí tham chiếu mã nguồn Praat 7.0.03, bảo đảm đánh dấu `TODO-PRAAT-LINE` và mã bảo vệ token cho khâu nghiệm thu Linux.

### 3.3. Các hạng mục vật lý "Phải đo" (To be measured on hardware / Quartus)
1. **Tần số xung nhịp cực đại $F_{\max}$ sau đóng gói vật lý:**
   - Ước lượng lý thuyết: Mạch Skid Buffer ngắt hoàn toàn cả đường đi tới và đường đi lui bằng thanh ghi, do đó đường tới hạn chỉ gồm 1 cổng logic MUX và 1 cổng AND/OR, bảo đảm $F_{\max} > 200\text{ MHz}$ trên Cyclone V cấp tốc độ -6.
   - *Hạng mục phải đo:* Tần số $F_{\max}$ thực tế và độ trễ Slack tại nhiệt độ $85^\circ\text{C}$ (Slow 1100mV 85C Model) phải được trích xuất từ báo cáo Timing Analyzer (`.sta.rpt`) của Quartus Prime sau khi biên dịch toàn bộ hệ thống.
2. **Tài nguyên logic thực tế (ALMs và phân bổ thanh ghi bên trong LAB):**
   - *Hạng mục phải đo:* Mức độ chia sẻ tài nguyên LAB (Logic Array Block) giữa thanh ghi đệm chính (`m_data`) và thanh ghi đệm trượt (`skid_data`) phải được đọc từ báo cáo Fitter Resource Section của Quartus.
3. **Báo cáo lựa chọn mã hóa FSM của Quartus (State Machine Report):**
   - Khi đặt thiết lập `State Machine Processing = Auto`, Quartus Prime sẽ phân tích số lượng trạng thái, độ phức tạp của logic kích hoạt và tài nguyên của chip để tự động chuyển đổi FSM sang One-Hot hoặc Minimal Bits.
   - *Hạng mục phải đo:* Phải kiểm tra bảng *State Machine - Processing Style* trong báo cáo tổng hợp Quartus (`.map.rpt`) để xác nhận kiểu mã hóa mà trình biên dịch đã áp dụng thực tế.
4. **Thời gian truyền dữ liệu thực tế qua Lightweight HPS-to-FPGA Bridge:**
   - Ước lượng lý thuyết: Giới hạn trên thời gian ghi một từ 32-bit là xấp xỉ $1\ \mu\text{s}$, dẫn tới thông lượng truyền tải $32\text{ KB/s}$ chỉ chiếm $\text{RTF}_{\text{transfer}} \le 0{,}008$.
   - *Hạng mục phải đo:* Thời gian trễ thực tế của từng thao tác ghi từ không gian người dùng (Linux User Space) qua con trỏ bộ nhớ ảo của `mmap` phải được đo bằng hàm chuẩn `clock_gettime(CLOCK_MONOTONIC, ...)` trực tiếp trên bo mạch DE10-Standard đang chạy hệ điều hành Linux.

---

## 4. Các điểm hạn chế còn tồn đọng (Honest Remaining Weaknesses)

1. **Môi trường chạy mô phỏng Verilog (`iverilog`/`vvp`):**
   - Do môi trường máy trạm Windows của implementer không có sẵn công cụ biên dịch mã nguồn mở `iverilog`/`vvp`, việc mô phỏng nhịp-cho-nhịp 600 chu kỳ của Skid Buffer và 500 chu kỳ của Dual FSM mới chỉ được thực hiện trên mô hình toán học đôi song sinh Python (`ch02_skid_twin.py` và `ch02_fsm_twin.py`).
   - Toàn bộ mã nguồn RTL (`rtl/v3/ch02_*.v`), mã nguồn Testbench (`tb/v3/tb_ch02_*.v`), kịch bản chạy tự động chuẩn hóa Unix LF (`verify_v3/run_ch02_iverilog.sh`) và các tệp vector kích thích/kỳ vọng đã được chuẩn bị đầy đủ và sẵn sàng để Reviewer chạy trực tiếp trên máy trạm Linux.
2. **Số dòng mã nguồn Praat 7.0.03:**
   - Bộ mã nguồn Praat trên máy trạm Windows hiện tại là bản phát hành cũ hơn 7.0.03. Do đó, các vị trí trích dẫn số dòng chi tiết trong chương được đánh dấu bằng mã giữ chỗ `TODO-PRAAT-LINE`. Kịch bản `verify_v3/ch02_praat_lines.py` đã thiết lập sẵn các chuỗi ký tự nhận diện token chuẩn để Reviewer tự động kiểm tra và điền số dòng chính xác trên bản nguồn 7.0.03 của Linux.
3. **Thử nghiệm trên phần cứng thật (Physical FPGA Deployment):**
   - Các số liệu tài nguyên ALM, số lượng thanh ghi tiêu thụ và tần số hoạt động cực đại $F_{\max}$ trong tài liệu hiện dựa trên datasheet của Intel Cyclone V SoC (5CSXFC6D6F31C6N) và tính toán lý thuyết vi kiến trúc. Việc đo đạc vật lý thực tế cần có sự hỗ trợ của phần mềm Quartus Prime Fitter trên máy trạm hoàn chỉnh.

---

## 5. Lịch sử các Commit trên Git (Commit History)

Toàn bộ quá trình phát triển Chương 2 tuân thủ nghiêm ngặt quy tắc cam kết lũy tiến từng tiểu mục (incremental commits) trên nhánh `v3`:

- **Commit 1:** `a289e28` — `v3: ch02 2.1` (Khởi tạo tài liệu Chương 2, hoàn thiện tiểu mục 2.1 về Avalon-ST readyLatency, giản đồ xung TikZ, RTL Skid Buffer & FSM, mô hình Python Twin, testbench Verilog, kịch bản shell và Makefile).
- **Commit 2:** `e1670e2` — `v3: ch02 2.2` (Bổ sung tiểu mục 2.2: Dẫn xuất ngân sách chu kỳ từ nguyên lý đầu tiên cho đầu vào tệp dữ liệu, phân tích 500.000 chu kỳ/khung, 98.543 chu kỳ MAC, 616 chu kỳ/mẫu, RTF 0,197, Bảng 11 và đính chính lỗi sai lệch của tài liệu v1).
- **Commit 3:** `aa3cccb` — `v3: ch02 2.3` (Bổ sung tiểu mục 2.3: Mã hóa máy trạng thái FSM, so sánh 6 tùy chọn Quartus, Bảng 12, phân tích 166.036 thanh ghi của Cyclone V, dẫn xuất giải tích mã Gray và kiểm chứng toán học tính chất lật 1 bit bằng chuỗi bit 1 tận cùng).
- **Commit 4:** `cae9cfb` — `v3: ch02 2.4` (Bổ sung tiểu mục 2.4: Phân tích kiến trúc vi mô Skid Buffer, vết chu kỳ 2 nhịp nạp/xả bộ đệm trong Bảng 13, sơ đồ phần cứng TikZ Hình 4, trích đoạn mã RTL Verilog và logic đôi song sinh Python).
- **Commit 5:** `6118fdb` — `v3: ch02 2.5` (Bổ sung tiểu mục 2.5: Chiến lược kiểm chứng ba tầng, Bảng 14 so sánh Intel IP vs HDL tự viết, 4 bài tập thực hành cuối chương có lời giải chi tiết, chuẩn hóa 0 lỗi biên dịch XeLaTeX và 0 Overfull hbox).
- **Commit 6:** `739a57f` — `v3: ch02 report` (Bổ sung tài liệu nghiệm thu kỹ thuật `verify_v3/ch02_REPORT.md` theo Mục 12 của BRIEF_v3.md và chuẩn hóa quyền thực thi 100755 cho `verify_v3/run_ch02_iverilog.sh`).
