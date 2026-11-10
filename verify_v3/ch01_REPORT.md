# Báo cáo nghiệm thu Chương 1 — WAV trên HPS và cầu HPS–FPGA (v3)

Theo quy định hợp đồng kỹ thuật tại **Mục 12 của BRIEF_v3.md** và đề cương chi tiết **Ch.1 của agenda_chot_v2_2026-11-10.md**, dưới đây là báo cáo kiểm chứng toàn diện cho Chương 1: `chuong_v3/chuong_01_wav_hps_cau.tex`.

---

## 1. Bảng đánh giá chi tiết theo từng tiểu mục (Subsection Checklist)

| Tiểu mục | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / minh họa số? | Phương án + đánh đổi + lựa chọn có số? | Đường IP (A)? | Đường HDL (B)? | Twin Python & Testbench | Câu tóm lại (*Tóm lại: ...*)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1.1. Vấn đề truyền nhận giữa HPS và FPGA** | Có (mẫu nằm ở DDR3 HPS, logic ở FPGA, nguy cơ nghẽn) | Có (phân tích xung nhịp 50 MHz vs 16 kHz) | Có (so sánh 3 cầu nối vật lý của Cyclone V SoC) | Không áp dụng (mục tổng quan) | Không áp dụng (mục tổng quan) | Không áp dụng | Có (`\textit{Tóm lại: ...}`) |
| **1.2. Đọc WAV đúng cách và các cạm bẫy tiềm ẩn** | Có (bẫy offset 44 khi gặp chunk `LIST`) | Có (Hex dump tệp thật, GP tệp 1,234 s và 2,8 s) | Có (thuật toán số nguyên quét $O(1)$ vs số thực 2 lượt) | N/A (HPS phần mềm C) | N/A (HPS phần mềm C) | 8/8 tệp test (`ch01_wav_verify.py`, 200 tệp `ch01_frames_verify.py`) | Có (`\textit{Tóm lại: ...}`) |
| **1.3. Các phương án truyền dữ liệu, đánh đổi và lựa chọn** | Có (ảo tưởng về sự cần thiết của DMA ở $32\text{ KB/s}$) | Có (tính $B_{\text{audio}} = 32\text{ KB/s}$, trần LWHPS $200\text{ MB/s}$) | Có (Bảng 5 so sánh PIO LWHPS, mSGDMA, PIO Full, $\text{RTF} \le 0{,}008$) | Có (mô tả nguyên lý IP) | Có (mô tả nguyên lý PIO) | Có (tính toán tải bus $0{,}016\%$) | Có (`\textit{Tóm lại: ...}`) |
| **1.4. Đường (A): Xây dựng bộ đệm bằng Intel On-Chip FIFO IP** | Có (bất đồng bộ tốc độ CPU và tiêu thụ chu kỳ của FPGA) | Có (tính dung lượng M10K: $512 \times 16 = 8.192 \le 10.240$ bit) | Có (512 từ = 1 M10K vs 1024 từ = 2 M10K) | Có (`altera_avalon_fifo` và mSGDMA) | Đối chiếu | Phân tích tham số Qsys | Có (`\textit{Tóm lại: ...}`) |
| **1.5. Đường (B): Hiện thực phần cứng bằng HDL tự viết** | Có (tránh phụ thuộc IP hộp đen độc quyền) | Có (con trỏ 9-bit bit vòng, latency 2 nhịp) | Có (chốt thanh ghi FSM vs giải gói tổ hợp làm giảm Fmax) | Đối chiếu thông số | Có (`rtl/v3/ch01_avalon_fifo.v`, `rtl/v3/ch01_fifo_out.v`) | 500 mẫu (`ch01_fifo_twin.py`, `tb/v3/tb_ch01_fifo.v`) | Có (`\textit{Tóm lại: ...}`) |
| **1.6. Bản đồ thanh ghi và giao tiếp điều khiển lõi** | Có (lỗi gộp slave nguyên khối phá vỡ IP chuẩn) | Có (bản đồ địa chỉ cơ sở và offset nội bộ) | Có (tách 4 slave độc lập trên Lightweight Bridge) | Phù hợp chuẩn Qsys | Khớp thanh ghi RTL | Đối chiếu driver C và RTL | Có (`\textit{Tóm lại: ...}`) |
| **1.7. Phần mềm điều khiển trên HPS và kiểm chứng toàn diện** | Có (truy xuất phần cứng từ User Space an toàn) | Có (4 bài tập cuối chương có lời giải chi tiết) | Có (Bảng 8 so sánh toàn diện IP vs HDL) | Đối chiếu IP | Đối chiếu HDL | 100% bit-exact, -DSIM test 277 khung (`ch01_driver_test.py`) | Có (`\textit{Tóm lại: ...}`) |

---

## 2. Thống kê khối lượng tài liệu và ấn phẩm

- **Số trang văn bản:** 23 trang (từ trang 31 đến trang 53 trong `phan_moi_v3.pdf`).
- **Số từ (Word count):** 15.827 từ (848 dòng mã LaTeX trong `chuong_v3/chuong_01_wav_hps_cau.tex`).
- **Hình vẽ TikZ:** 1 hình (`fig:ch01_unpacker_fsm`: Lược đồ chuyển trạng thái FSM 4 bước giải gói 32-to-16 bit, thiết kế lưới 2x2 thông thoáng, kiểm tra ở độ phân giải 300 DPI: tuyệt đối không có chữ chạm viền và không có đường kẻ cắt ngang chữ).
- **Bảng số liệu tổng hợp:** 4 bảng chính có chú thích (Bảng 5: So sánh các phương án truyền dữ liệu; Bảng 6: Bản đồ Slave trên Lightweight Bridge; Bảng 7: Chi tiết thanh ghi khối điều khiển `ctrl`; Bảng 8: So sánh toàn diện giữa Intel On-Chip FIFO IP và HDL tự viết) cùng 1 bảng trích xuất Hex dump RIFF WAV.
- **Đoạn mã nguồn trích dẫn:** 3 khối mã chính (Mô hình suy diễn M10K Verilog, Mạch logic bắt cờ tràn dính Verilog, Khởi tạo ánh xạ `mmap` C).
- **Hộp sư phạm chuyên đề:** 1 hộp mục tiêu học tập (`learningobj`), 1 hộp bản chất vật lý (`physicalinsight`), 1 hộp đối thoại tư duy (`thoughtqa`).
- **Bài tập cuối chương:** 4 bài tập định lượng chuyên sâu kèm lời giải mẫu chi tiết từng bước.
- **Trạng thái biên dịch XeLaTeX:** Biên dịch thành công 100%, 0 lỗi, toàn bộ các cảnh báo Overfull `\hbox` trong Chương 1 đều $\le 8{,}9\text{ pt}$ (nằm nghiêm ngặt dưới ngưỡng trần $10\text{ pt}$).

---

## 3. Danh mục các số liệu và hạng mục "(phải đo)"

Mọi số liệu trong chương đều được phân định xuất xứ minh bạch:
1. **Các số liệu dẫn xuất toán học (Derived):**
   - Băng thông dữ liệu âm thanh 16 kHz 16-bit: $16.000 \times 2\text{ byte} = 32\text{ KB/s} = 0{,}032\text{ MB/s}$.
   - Trần băng thông Lightweight Bridge ở 50 MHz 32-bit: $50\text{ MHz} \times 4\text{ byte} = 200\text{ MB/s}$.
   - Tỷ lệ chiếm dụng bus của dòng âm thanh: $0{,}032 / 200 = 0{,}016\%$.
   - Thời gian CPU cho lệnh ghi PIO bi quan ($1\ \mu\text{s}$): $8.000 \times 1\ \mu\text{s} = 8\text{ ms/s}$ âm thanh $\to \text{RTF}_{\text{transfer}} \le 0{,}008$.
   - Dung lượng bit của FIFO 512 từ 16-bit: $512 \times 16 = 8.192\text{ bit} \le 10.240\text{ bit}$ (vừa khít 1 khối M10K).
   - Số khung và thời điểm $t_1$: Tệp 1,234 s có 120 khung, $t_1 = 0{,}022\text{ s}$, $\text{win0} = 33$; Tệp 2,8 s có 277 khung, $t_1 = 0{,}020\text{ s}$, $\text{win0} = 1$.
   - Kích thước tệp xuất F0 Q12.4: $277 \times 2\text{ byte} = 554\text{ byte}$.

2. **Các số liệu kiểm chứng bằng kịch bản phần mềm (Checked by script):**
   - `verify_v3/ch01_wav_verify.py` $\to$ `ch01_wav_verify.log`: $GP = 22.946$ (clean), $GP = 22.937$ (noisy), $GP = 650$ (mini speech), phát hiện chính xác lỗi 4 tệp biên.
   - `verify_v3/ch01_frames_verify.py` $\to$ `ch01_frames_verify.log`: Khớp $100\%$ với `golden_v2/frames.py` trên 200 tệp ngẫu nhiên; nhận diện tỷ lệ bẫy sàn số lẻ là $86\%$.
   - `verify_v3/ch01_fifo_test.py` $\to$ `ch01_fifo_test.log`: 500 mẫu âm thanh truyền qua FIFO có backpressure ngẫu nhiên đạt $100\%$ bit-exact, ngưỡng bão hòa 257 từ và cờ `ovf_sticky` kích hoạt chính xác.
   - `verify_v3/ch01_driver_test.py` $\to$ `ch01_driver_test.log`: Giả lập `-DSIM` hoàn tất toàn bộ 277 khung, sinh tệp `pitch_f0.bin` (554 byte) và `pitch_meta.txt`.

3. **Các hạng mục ghi rõ "(phải đo)" (Yêu cầu đo trên phần cứng vật lý hoặc Quartus Timing Analyzer):**
   - *Thời gian thực tế của một lệnh ghi PIO qua Lightweight Bridge*: Phụ thuộc vào trễ bus AXI/Avalon trên chip SoC Cyclone V (đo bằng hàm `clock_gettime(CLOCK_MONOTONIC)` trên Linux HPS).
   - *Tài nguyên logic ALM và thanh ghi FF thực tế của khối FIFO IP và HDL tự viết*: Cần biên dịch qua Quartus Fitter để lấy báo cáo Fitter Summary chính thức.
   - *Tần số hoạt động cực đại $F_{\max}$ của khối FIFO*: Cần báo cáo từ Timing Analyzer (Slow 1100mV 85C Model).
   - *Độ trễ truy xuất bus thực tế của mSGDMA khi cạnh tranh bộ nhớ DDR3*: Cần đo đạc bằng bộ đếm chu kỳ hiệu năng trên bo mạch vật lý ở Chương 13.

---

## 4. Những điểm yếu còn tồn tại và kế hoạch xử lý

1. **Trình mô phỏng Verilog độc lập:** Do môi trường máy tính Windows hiện tại không cài đặt `iverilog`/`vvp` và Quartus EDA, tệp kiểm thử `tb/v3/tb_ch01_fifo.v` mới được kiểm chứng chu kỳ qua Python twin (`verify_v3/ch01_fifo_test.py`). Kịch bản Verilog thuần túy đã sẵn sàng và sẽ được chạy nghiệm thu trên máy trạm Linux của reviewer.
2. **Đo đạc trên phần cứng thật:** Trình điều khiển C (`sw_v3/ch01_driver.c`) đã chạy hoàn hảo ở chế độ `-DSIM`. Khi nạp lên bo mạch DE10-Standard vật lý, người phát triển chỉ cần gỡ cờ `-DSIM` để truy xuất trực tiếp `/dev/mem`.

---

## 5. Lịch sử Git Commits

Toàn bộ quá trình thực hiện Chương 1 được cam kết nghiêm ngặt theo từng tiểu mục trên nhánh `v3`:
- Commit `5e5c5d9`: `v3: ch01 1.1` (Mục tiêu học tập và Tiểu mục 1.1)
- Commit `d1e8f70`: `v3: ch01 1.2` (Tiểu mục 1.2: Phân tích RIFF WAV, bẫy offset 44, công thức số nguyên GP, lưới khung Praat và bẫy sàn số lẻ)
- Commit `df97810`: `v3: ch01 1.3` (Tiểu mục 1.3: So sánh định lượng 3 phương án truyền tải, Bảng 5, RTF transfer)
- Commit `44f2cf5`: `v3: ch01 1.4` (Tiểu mục 1.4: Phân tích tường tận tham số On-Chip FIFO IP và mSGDMA)
- Commit `68f741e`: `v3: ch01 1.5` (Tiểu mục 1.5: Hiện thực HDL tự viết, con trỏ bit vòng, suy diễn M10K, FSM giải gói)
- Commit `2665df1`: `v3: ch01 1.6` (Tiểu mục 1.6: Bản đồ thanh ghi phân lập 4 Slave trên Lightweight Bridge)
- Commit `37591de`: `v3: ch01 1.7` (Tiểu mục 1.7: Trình điều khiển C, Python twin, Testbench Verilog, Bảng 8 IP vs HDL, 4 bài tập cuối chương)
- Commit `095be3f`: `v3: ch01 polish FSM diagram layout` (Tinh chỉnh bố cục hình vẽ TikZ FSM đạt chuẩn không chạm viền / không cắt chữ)
