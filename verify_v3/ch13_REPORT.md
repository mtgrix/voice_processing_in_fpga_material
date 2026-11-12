# BÁO CÁO NGHIỆM THU CHƯƠNG 13 (BRIEF SECTION 12)
**Đề tài**: Ước lượng tần số cơ bản $F_0$ theo giải thuật Praat trên FPGA Cyclone V (DE10-Standard)  
**Tập tin chương**: `chuong_v3/chuong_13_kiem_chung.tex`  
**Nhánh Git**: `v3`  
**Ngày hoàn thành**: 12/11/2026  

---

## 1. Bảng đánh giá chi tiết theo từng tiểu mục (Per-subsection Table)

| Tiểu mục | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / Minh họa số học? | Đánh đổi phương án kèm số liệu? | Tuyến IP Intel? | Tuyến HDL tự viết? | Mô hình Twin + iverilog (Khớp/Lỗi)? | Câu tóm tắt bản chất kỹ thuật? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **13.1** Ba tầng kiểm chứng hệ thống: Từ mô hình phần mềm đến silicon thực tế | Có (Nguy cơ ngụy biện hệ thống nhúng: lỗi triệt tiêu, không truy vết được lỗi, bất đồng mô phỏng vs silicon) | Có (Khảo sát 13 testbench và log từ Ch01 đến Ch12) | Có (Bit-exact Twin-RTL vs Bit-exact Hardware vs Statistical Acoustic Praat) | Có (Khối IP: FIFO, MULT_ADD, LPM_DIVIDE) | Có (HDL tự viết Verilog-2001) | Khớp 13/13 testbench, 0 lỗi (`verify_v3/run_ch13_iverilog.sh`) | Có ("Tóm lại: Ba tầng kiểm chứng tạo nên một chu trình khép kín...") |
| **13.2** Hai mốc Praat tham chiếu và phân rã các nguồn sai số | Có (So sánh trực diện với Praat mặc định là khập khiễng do Viterbi nhìn toàn cục đa khung vs Pipeline nhân quả) | Có (Bảng 50 đối chuẩn chi tiết trên tệp sạch và tệp nhiễu SNR 5 dB; `ch13_metrics_audit.py`) | Có (Praat R1 mặc định vs Praat R2 gỡ chi phí chuyển trạng thái; phân rã 4 chặng sai số) | Có (Nội suy Parabol vs sinc70 + Brent đợt 2) | Có (Bảng 51 ánh xạ từng dòng `praat_float_ref.py` sang RTL) | Khớp 277/277 khung trên cả hai tệp âm thanh chuẩn | Có ("Tóm lại: Cấu hình R2 gỡ bỏ chi phí chuyển trạng thái quy Viterbi...") |
| **13.3** Căn khung theo thời gian và bộ bốn chỉ số đo lường | Có (Cái bẫy chết người khi so sánh theo chỉ số khung: lệch pha `first_win0`, trễ nhóm FIR 15 mẫu, bẫy làm tròn IEEE-754) | Có (Bảng 52 ví dụ tính tay 10 khung đầy đủ 4 trạng thái; `ch13_hand_example.py`) | Có (Ngưỡng 20% = +315.64 cent vs -386.31 cent, lệch 70.67 cent; loại trừ GPE khi tính cent mịn) | Có (Độ phân giải Q12.4: 1.08 cent @ 100 Hz vs 0.22 cent @ 500 Hz) | Có (`sw_v3/ch01_frames.c` và `golden_v2/frames.py` chuẩn Praat float64) | Khớp 277/277 khung trên 5 cấu hình độ dài chẵn/lẻ (`ch13_frame_alignment.log`) | Có ("Tóm lại: Căn khung theo thời gian vật lý là nguyên tắc sống còn...") |
| **13.4** Đo lường hiệu năng thời gian thực và hệ số RTF | Có (Nguy cơ ngụy biện hiệu năng: so sánh 50 MHz vs 3.5 GHz CPU mà không chuẩn hóa RTF và cô lập thời gian chạy) | Có (Bài tập 3 tính tay: 5.0 s audio, 497 khung: FPGA RTF 0.1981, HPS RTF 0.1989, Praat Linux RTF 0.000395) | Có (Bảng 53 so sánh hiệu năng 3 phía: FPGA Cycle Counter 552.20 ms vs HPS phải đo vs Praat Linux 1.106 ms) | Có (Độ trễ pipeline cố định tuyệt đối 99.671 chu kỳ/khung) | Có (Trình điều khiển HPS 3 giai đoạn: `sw_v3/ch13_hps_timer.c`) | Khớp 27 608 945 chu kỳ / 277 khung = 99 671.3 chu kỳ/khung | Có ("Tóm lại: Lõi FPGA ở 50 MHz đạt RTF = 0,197 (nhanh gấp 5,07 lần thời gian thực)...") |
| **13.5** Bảng tài nguyên IP so với HDL từ Fitter và Timing Analyzer | Có (Đánh đổi kinh tế kỹ thuật giữa khối IP và mã nguồn HDL tự viết: silicon hard IP vs cycle control vs vendor lock-in) | Có (4 bài tập chuyên sâu cuối chương kèm lời giải số học chi tiết; `ch13_exercises.py`) | Có (Bảng 54 chi tiết từng khối: 9 M10K = 1.63%, 5-6 DSP = 4.46-5.36% trên chip Cyclone V) | Có (Tuyến A: MegaCore IP của Intel) | Có (Tuyến B: HDL Verilog-2001 tự viết) | Khớp toàn tuyến, 0 lỗi | Có ("Tóm lại: Toàn bộ hệ thống chỉ chiếm 1,63% khối RAM M10K và chưa tới 5,4% khối DSP...") |

---

## 2. Thống kê định lượng chương (Quantitative Statistics)

- **Số trang văn bản**: 19 trang (từ trang 283 đến trang 301 trong tài liệu tổng hợp `phan_moi_v3.pdf`, tổng 302 trang).
- **Số từ**: 15.907 từ (1.096 dòng mã nguồn LaTeX tại `chuong_v3/chuong_13_kiem_chung.tex`).
- **Số hình vẽ TikZ**: 3 hình chuyên sâu (đã kết xuất và kiểm tra visual ở 300 DPI, 0 lỗi đè chữ, 0 đường cắt chữ):
  1. Hình 32 (`fig_ch13_three_tiers.tex`): Sơ đồ kiến trúc ba tầng kiểm chứng hệ thống.
  2. Hình 33 (`fig_ch13_error_decomp.tex`): Sơ đồ phân rã các nguồn sai số giữa Praat và hệ thống FPGA.
  3. Hình 34 (`fig_ch13_frame_align.tex`): Nguyên lý căn chỉnh khung phân tích theo trục thời gian vật lý liên tục so với chỉ số mẫu rời rạc.
- **Số bảng số liệu**: 5 bảng chuyên sâu:
  1. Bảng 50 (`tab:ch13_benchmark_golden`): Bảng kết quả đối chuẩn đa tầng trên hai tệp âm thanh chuẩn (sạch và SNR 5 dB).
  2. Bảng 51 (`tab:ch13_float_vs_hdl_mapping`): Bảng ánh xạ giải thuật giữa bản port float `praat_float_ref.py` và kiến trúc RTL `ch12_top.v`.
  3. Bảng 52 (`tab:ch13_hand_example`): Bảng tính tay chi tiết bộ bốn chỉ số đo lường âm học trên tập mẫu 10 khung.
  4. Bảng 53 (`tab:ch13_timing_comparison`): Bảng so sánh hiệu năng thời gian và hệ số thời gian thực (RTF) ba phía giữa FPGA, HPS và Praat trên máy Linux (box).
  5. Bảng 54 (`tab:ch13_ip_vs_hdl_resources`): Bảng tổng hợp tài nguyên silicon giữa Đường (A) Intel IP và Đường (B) HDL tự viết trên chip Cyclone V SoC.
- **Số đoạn trích dẫn mã nguồn (Listings)**: 1 listing trích đoạn cốt lõi thuật toán Praat float ref (`golden_v2/praat_float_ref.py`, dòng 197–232, 36 dòng).
- **Số bài tập cuối chương**: 4 bài tập chuyên sâu kèm lời giải số học chi tiết (Bài tập 1: Phân rã sai số ba tầng và hiệu quả Median-3; Bài tập 2: Quy đổi ngưỡng GPE 20% và tính bất đối xứng của cent; Bài tập 3: Tính toán ngân sách chu kỳ và RTF; Bài tập 4: Bẫy làm tròn mẫu trên tệp độ dài lẻ và phân tích số học nhị phân IEEE-754).

---

## 3. Các hạng mục đánh dấu "phải đo" và lý do khách quan

Tuân thủ nghiêm ngặt quy chuẩn của Brief và các bài học từ Ch01-Ch12, mọi thông số phần cứng phụ thuộc vào silicon thực tế hoặc công cụ EDA chưa khả dụng trên máy trạm Windows cục bộ đều được đánh dấu minh bạch dạng `[TODO: box]` hoặc ghi chú `phải đo`:
1. **Kiểm chứng Tầng 2 trên bo mạch vật lý DE10-Standard**: So sánh từng byte (`cmp -l pitch_f0_board.bin pitch_f0_sim.bin`) giữa kết quả HPS DDR3 và mô phỏng RTL. Đánh dấu `(phải đo trên bo mạch thực tế)` do máy trạm không kết nối bo mạch vật lý. Tính đúng đắn của luồng dữ liệu đã được bảo chứng bằng `sw_v3/test_ch12_driver.c` (khớp đúng 277/277 khung).
2. **Báo cáo Fitter và Timing Analyzer**: Các ô ALM, thanh ghi Flip-Flop, đường tới hạn và tần số xung nhịp cực đại $F_{\max}$ trong Bảng 54 được ghi chú `phải đo trong Quartus Prime` (do máy trạm không cài đặt Quartus Prime). Các con số về khối cứng M10K ($9\text{ khối} = 1{,}63\%$) và DSP ($5\text{--}6\text{ khối} = 4{,}46\%\text{--}5{,}36\%$) được xác định chính xác từ kiến trúc. Mẫu số chip được trích dẫn chuẩn xác theo Intel Cyclone V Device Handbook (doc ID CV-51001) và Agenda: $41.910\text{ ALM}$, $166.036\text{ thanh ghi}$, $553\text{--}557\text{ M10K}$, $112\text{ DSP}$.
3. **Đo đạc thời gian Praat 7.0.03 trên Linux (box)**: Đo đạc thực nghiệm từ kịch bản `verify_v3/ch13_benchmark.praat` trên máy chủ Linux box (CPU Intel(R) Xeon(R) Processor, 8 vCPU, 15 GB RAM), ghi nhận tại nhật ký `verify_v3/ch13_praat_bench_R1.log` và `ch13_praat_bench_R2.log`: cấu hình R1 đạt thời gian trung vị $1{,}106\text{ ms}$, $\text{RTF}_{\text{praat}} = 0{,}000395$ (nhanh gấp $\approx 2.531{,}6\text{ lần}$ thời gian thực); cấu hình R2 đạt $1{,}161\text{ ms}$, $\text{RTF} = 0{,}000414$ (nhanh gấp $\approx 2.415{,}5\text{ lần}$ thời gian thực).
4. **Thời gian toàn tuyến trên HPS thực tế**: Chương trình đo đạc thời gian phân giải cao POSIX `clock_gettime(CLOCK_MONOTONIC)` đã được cài đặt tại `sw_v3/ch13_hps_timer.c` và kiểm thử thành công qua `sw_v3/test_ch13_hps_timer.c` (0 lỗi). Trên bo mạch Linux nhúng thực tế, các thông số thời gian 3 giai đoạn và RTF toàn tuyến được giữ minh bạch dưới dạng "phải đo trên bo mạch thực tế", không đưa số liệu ước đoán theo đúng quy tắc hợp đồng.

---

## 4. Các điểm hạn chế còn tồn tại (Honest Remaining Weaknesses)

1. **Bộ lọc trung vị Median-3 thay thế Viterbi**: Median-3 hoạt động hiệu quả khi sửa được 7 trong số 22 khung lỗi GPE trên tệp nhiễu SNR 5 dB (hạ tỷ lệ lỗi xuống 15 khung), nhưng vẫn còn tồn tại 15 khung lỗi quãng tám do giải thuật không lưu vết chuỗi trạng thái toàn cục đa khung như quy hoạch động Viterbi của Praat.
2. **Sai số lượng tử hóa số nguyên Q12.4**: Định dạng Q12.4 với bước lượng tử $1/16\text{ Hz}$ tạo ra sai số làm tròn lý thuyết khoảng $1{,}08\text{ cent}$ tại $100\text{ Hz}$ và $0{,}22\text{ cent}$ tại $500\text{ Hz}$. Mặc dù hoàn toàn đáp ứng ngưỡng cảm nhận âm học của tai người ($< 5\text{ cent}$), nó vẫn là một nguồn sai lệch vi mô so với bản tính dấu phẩy động 64-bit IEEE-754 của Praat.
3. **Xếp hạng ứng viên trên lưới lag nguyên**: FPGA xếp hạng điểm số tự tương quan $Sc[\tau]$ tại các vị trí trễ nguyên $\tau \in [27, 213]$ trước khi nội suy parabol, trong khi Praat tính toán độ mạnh sau khi đã nội suy sinc liên tục. Trên tín hiệu nhiễu nặng, sự khác biệt này khiến FPGA chọn nhầm ứng viên bậc hài tại $3/207\text{ khung}$.

---

## 5. Danh sách vết băm Git Commit thực tế (Git Log Commit Hashes)

Các vết băm commit thực tế được ghi nhận trong lịch sử Git của nhánh `v3`:
- `fb7c5ff`: `v3: ch13 13.1 ba tang kiem chung`
- `9badc51`: `v3: ch13 13.2 hai praat tham chieu va phan ra sai so`
- `faff32a`: `v3: ch13 13.3 can khung theo thoi gian va bo bon chi so`
- `38f08c2`: `v3: ch13 13.4 do luong hieu nang thoi gian va he so rtf`
- `89280b3`: `v3: ch13 13.5 bang tai nguyen ip vs hdl va bai tap`
- `e887e7c`: `v3: ch13 WIP polish (agy 503 exit)`
- *(Commit hoàn tất hiện tại)*: `v3: ch13 done`
