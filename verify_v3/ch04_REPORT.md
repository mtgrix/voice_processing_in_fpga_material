# BÁO CÁO NGHIỆM THU CHƯƠNG 4 (verify_v3/ch04_REPORT.md)
**Tên chương:** Chia khung và RAM vòng (`chuong_v3/chuong_04_chia_khung_ram_vong.tex`)  
**Nhánh git:** `v3`  
**Nền tảng thực thi:** Windows 11 (MiKTeX XeLaTeX, Python 3.12, NumPy, SciPy)  
**Thời điểm hoàn thành:** 2026-11-11  

---

## 1. Bảng kiểm soát chất lượng từng mục (Per-subsection Checklist)

| Mục | Mở đầu bằng bài toán thực tế | Ví dụ tính tay / Kịch bản Python | Phương án + Đánh đổi + Lựa chọn số liệu | Tuyến IP Intel | Tuyến HDL tự viết | Song sinh + Iverilog | Câu tóm tắt bản chất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4.1. Vì sao 3 chu kỳ, vì sao 10 ms** | Có | Có (`ch04_frame_grid.py`) | Có ($N=1, 2, 3, 5$ chu kỳ, $40\text{ ms}$, hop $10\text{ ms}$) | Không áp dụng | Không áp dụng | Khớp 100% Python | Có |
| **4.2. Căn lưới khung giống Praat và bẫy số lẻ** | Có | Có (`ch04_frame_grid.py`, `ch04_praat_lines.py`) | Có (Căn lưới $t_1$, bỏ $1$ vs $33$ mẫu, bẫy $159/161$) | Không áp dụng | Không áp dụng | Khớp 100% Python | Có |
| **4.3. Phân tích các phương án phần lưu đệm** | Có | Có (Bảng so sánh 3 phương án phần cứng) | Có (10.208 FF vs 800 từ + ALM vs 1024 từ 2 M10K) | Không áp dụng | Không áp dụng | Không áp dụng | Có |
| **4.4. Tuyến (A): Khối IP Intel RAM: 2-PORT** | Có | Có (Giải mã 7 tham số, CV-52003, UG-01068) | Có (Latency 1 vs 2, Old Data vs Don't Care) | Có (Mẫu khai báo và timing IP) | Không áp dụng | Không áp dụng | Có |
| **4.5. Tuyến (B): Mã nguồn HDL suy diễn M10K** | Có | Có (Dãy `rd_base` 0..960..96, logic 10-bit) | Có (Atomic sample count, `REGISTERED_OUTPUT`) | Không áp dụng | Có (`rtl/v3/ch04_ring_buffer.v`, 45 dòng) | Khớp 100% Twin | Có |
| **4.6. Kiểm chứng song sinh, Testbench và Bài tập** | Có | Có (Bảng đối chiếu 6 khối, quy ước lấy mẫu) | Có (3.500 chu kỳ, 5 góc biên, phản áp) | Có (Bảng so sánh IP vs HDL) | Có (`tb/v3/tb_ch04_ring_buffer.v`) | 3.500/3.500 vector Twin; Iverilog `\todo{box}` | Có |
| **Bài tập thực hành (4 bài tập)** | Có | Có (`verify_v3/ch04_exercises.py`) | Có (Định lượng dung lượng, FPU-free, modulo, flush) | Không áp dụng | Không áp dụng | Khớp 100% Python | Có |

---

## 2. Số liệu định lượng tài liệu và ấn bản (Metrics)

- **Số trang biên dịch trong PDF hoàn chỉnh (`phan_moi_v3.pdf`):** 16 trang (trang 102 đến trang 117).
- **Tổng số trang toàn sách:** 118 trang.
- **Số từ trong tệp TeX (`wc -w chuong_v3/chuong_04_chia_khung_ram_vong.tex`):** 9.566 từ.
- **Số dòng trong tệp TeX:** 647 dòng.
- **Số hình vẽ TikZ kỹ thuật:** 2 hình.
  - Hình 7 (`chuong_v3/fig_ch04_frame_grid.tex`): Lưới căn khung thời gian Praat, bước nhảy hop 160 mẫu, vùng chồng lấp 478 mẫu, độ trễ bỏ qua mẫu đầu `lead_discard`.
  - Hình 8 (`chuong_v3/fig_ch04_ring_buffer.tex`): Sơ đồ kiến trúc phần cứng khối RAM vòng 1024 từ, giao diện Avalon-ST Sink, Cổng A ghi, Cổng B đọc, con trỏ ghi `wr_ptr`, con trỏ gốc `rd_base`, bộ đếm mẫu tồn `sample_count` và các cờ bắt tay.
- **Số bảng số liệu kỹ thuật:** 3 bảng.
  - Bảng 10 (`tab:ch04_buffer_options`): So sánh định lượng 3 phương án phần cứng lưu đệm chia khung ($N=638, \text{hop}=160$).
  - Bảng 11 (`tab:ch04_twin_vs_hdl`): Bảng đối chiếu từng dòng giữa mô hình song sinh Python (`verify_v3/ch04_ring_buffer_twin.py`) và mã Verilog HDL (`rtl/v3/ch04_ring_buffer.v`).
  - Bảng 12 (`tab:ch04_ip_vs_hdl`): So sánh toàn diện giữa IP Intel RAM: 2-PORT và mã nguồn HDL tự viết suy diễn M10K.
- **Số đoạn mã nguồn trích dẫn (Listings):** 4 đoạn.
  - Đoạn 1: Mã nguồn C trích từ Praat 7.0.03 (`Sound_to_Pitch.cpp:334-339`) về quy tắc làm tròn kích thước cửa sổ.
  - Đoạn 2: Mẫu khởi tạo khối IP Intel `RAM: 2-PORT`.
  - Đoạn 3 (`lstinputlisting`): 48 dòng then chốt của `rtl/v3/ch04_ring_buffer.v` (dòng 70 đến 117).
  - Đoạn 4 (`lstinputlisting`): 44 dòng then chốt trong hàm `clock_edge` của `verify_v3/ch04_ring_buffer_twin.py` (dòng 71 đến 114).
- **Lỗi biên dịch XeLaTeX:** 0 lỗi.
- **Cảnh báo Overfull `\hbox` (> 10pt):** 0 cảnh báo.

---

## 3. Danh mục các số liệu "phải đo" và căn cứ trích dẫn phần cứng

1. **Số liệu trích dẫn từ tài liệu phần cứng Intel Cyclone V:**
   - Cấu hình khối M10K: *Cyclone V Device Handbook, Volume 1: Device Interfaces and Integration* (CV-52003, Bảng 3-1: "M10K Block Configurations"). Dung lượng 10.240 bit; khi chạy ở độ rộng 16-bit, cấu hình sâu nhất của 1 khối M10K là $512 \times 16$ hoặc $512 \times 20$. Do đó, bộ nhớ 1024 từ $\times$ 16-bit bắt buộc sử dụng đúng 2 khối M10K ($1024 \times 8 \times 2$); bộ nhớ 800 từ $\times$ 16-bit cũng tiêu tốn đúng 2 khối M10K.
   - Tham số IP RAM: *Embedded Memory (RAM: 1-PORT, RAM: 2-PORT, ROM: 1-PORT, and ROM: 2-PORT) User Guide* (UG-01068). Giải thích chính xác các tham số `operation_mode = DUAL_PORT`, `read_during_write_mode_mixed_ports = DONT_CARE`, `outdata_reg_b = CLOCK0` (Latency = 2).
2. **Số liệu trích dẫn mã nguồn Praat 7.0.03 được kiểm chứng:**
   - `fon/Sound_to_Pitch.cpp:334-339`: `halfnsamp_window = nsamp_window/2 - 1` $\implies$ $640 \to 319 \to 638$ mẫu tại $f_s = 16\text{ kHz}$.
   - `fon/Sound_to_Pitch.cpp:296`: `dt = periodsPerWindow / pitchFloor / 4 = 10 ms = 160 mẫu`.
   - `fon/Sound_to_Pitch.cpp:354`: Gọi `Sampled_shortTermAnalysis` với `dt_window`.
   - `fon/Sound_to_Pitch.cpp:52, 72-73`: `leftSample = Sampled_xToLowIndex(me,t)`, `rightSample = leftSample + 1`, `startSample = rightSample - halfnsamp_window`.
   - `fon/Sampled.cpp:71-81`: `Sampled_shortTermAnalysis` tính `numberOfFrames = floor((duration - windowDuration)/timeStep) + 1` và `firstTime`.
   - `fon/Sampled.h:34`: `Sampled_xToLowIndex = Melder_ifloor((x - x1)/dx + 1.0)`.
   - Toàn bộ 6 trích dẫn được kiểm chứng đạt 6/6 PASS qua `verify_v3/ch04_praat_lines.py`.
3. **Mục "phải đo" (To be measured on hardware / Linux simulation):**
   - Kết quả chạy thực tế Icarus Verilog: Đã đóng gói trong script `verify_v3/run_ch04_iverilog.sh` (LF, chế độ 100755). Trong văn bản LaTeX, kết quả được đánh dấu trung thực bằng khối `\todo{box}` để người đánh giá điền kết quả chính thức từ máy chủ Linux.
   - Tài nguyên logic ALM và tần số hoạt động tối đa $F_{max}$: Phải đo chính xác sau khi biên dịch Place & Route (Fitter) trong phần mềm Quartus Prime với thiết bị 5CSXFC6D6F31C6.

---

## 4. Những điểm yếu còn tồn tại và đánh giá kỹ thuật khách quan

1. **Xử lý khung cuối cùng (Tail Frame Flushing):** Khối RAM vòng hiện tại dừng nhận dữ liệu khi tệp âm thanh kết thúc và chỉ xuất khung khi cờ `frame_ready` bật ($\ge 638$ mẫu). Nếu phần đuôi của tệp âm thanh còn thừa ít hơn 638 mẫu mà HPS muốn phân tích khung áp chót/cuối cùng, HPS phải chủ động đệm thêm các mẫu 0 (Zero-padding) vào luồng nạp FIFO trước khi kết thúc phiên. Logic chèn đệm tự động chưa được tích hợp trong phần cứng RTL mà đang được đề xuất ở Bài tập 4.
2. **Độ trễ đọc cố định ở ngõ ra:** Thiết kế mặc định sử dụng `REGISTERED_OUTPUT = 1` tạo độ trễ ổn định 2 chu kỳ xung nhịp để bảo đảm thời gian định thời trên FPGA Cyclone V. Nếu khối tính tự tương quan (ACF Engine ở Chương 5) yêu cầu truy xuất trực tiếp với độ trễ 1 chu kỳ, người thiết kế cần gán tham số này về 0, khi đó dữ liệu xuất trực tiếp từ cổng ra không thanh ghi của khối nhớ M10K.
3. **Phụ thuộc môi trường kiểm thử:** Testbench đã được chuẩn hóa theo quy ước kích thích sườn âm, kiểm tra tổ hợp trước sườn dương và kiểm tra tuần tự sau sườn dương; tập vector 3.500 chu kỳ bao quát toàn diện các góc biên. Tuy nhiên, việc thực thi công cụ Icarus Verilog cục bộ trên Windows chưa có sẵn nên cần chạy qua kịch bản shell trên Linux của reviewer.

---

## 5. Lịch sử các Commit Git trên nhánh v3

Toàn bộ tiến trình phát triển và kiểm chứng Chương 4 được lưu vết qua các commit nguyên tử trên nhánh `v3`:
- `0a563ff`: `v3: ch04 4.1-4.2 praat frame grid and floor trap` (Lý thuyết 3 chu kỳ, hình vẽ lưới khung TikZ, kiểm chứng Praat 7.0.03, giải thuật căn lưới và bẫy làm tròn số lẻ).
- `faaa42d`: `v3: ch04 4.3-4.5 ring buffer rtl twin and tb` (Thiết kế RTL RAM vòng 1024 từ suy diễn M10K, mô hình song sinh bit-exact Python 3.500 chu kỳ, testbench chuẩn hóa quy ước lấy mẫu tổ hợp/tuần tự, hình vẽ kiến trúc TikZ).
- `3a738a2`: `v3: ch04 4.6 verification and exercises` (Tích hợp chương vào phan_moi_v3.tex, biên dịch XeLaTeX 0 lỗi 0 overfull hbox, 4 bài tập thực chiến có giải bằng số liệu từ ch04_exercises.py, cập nhật Makefile).
- `1d367fb`: `v3: ch04 done` (Đóng gói báo cáo nghiệm thu hoàn chỉnh ch04_REPORT.md).
