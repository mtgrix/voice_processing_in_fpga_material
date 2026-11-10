# Báo cáo Nghiệm thu Chương 0 (verify_v3/ch00_REPORT.md)

**Chương 0: Bài toán, mục tiêu so sánh, và Praat thật sự làm gì**  
**Tập tin chương:** `chuong_v3/chuong_00_bai_toan.tex`  
**Nhánh Git:** `v3`  
**Ngày hoàn thành đợt sửa đổi (Revision Round 1):** 11/11/2026  

---

## 1. Bảng đánh giá theo từng mục con (Per-subsection Evaluation)

| Mục con | Mở đầu bằng vấn đề thực tế (y/n) | Ví dụ tính tay (y/n, script) | Phân tích phương án + đánh đổi + lựa chọn (có số) (y/n) | Tuyến IP Catalog (y/n) | Tuyến HDL tự viết (y/n) | Twin + mô phỏng (N/N) | Câu tóm tắt in nghiêng (y/n) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0.1 Một file, hai câu trả lời** | y | y (`ch00_naive_methods.py`) | y (Zero-crossing vs FFT vs Autocorr) | n/a | n/a | n/a | y |
| **0.2 Ý tưởng của Boersma** | y | y (`ch00_norm_sine.py`) | y (Unnormalized vs Boersma $R_w$) | n/a | n/a | n/a | y |
| **0.3 Tám bước của Praat & thiết kế phần cứng** | y | y (10 tham số & công thức C++) | y (Bảng so sánh 5 lựa chọn kiến trúc) | y | y | n/a | y |
| **0.4 Kiến trúc hệ thống & bản đồ các chương** | y | y (Phân tích luồng dữ liệu Hình 1) | y (PIO vs mSGDMA: 32 KB/s, 8.000 từ/s, RTF $\approx 0{,}008$; FIFO 512 vs 1024) | y | y | n/a | y |
| **0.5 Các phép đo: GPE, VDE, FFE và cent** | y | y (`ch00_metrics.py`) | y (4 tình huống khung, ngưỡng 20%) | n/a | n/a | n/a | y |
| **0.6 Ngân sách chu kỳ, RTF và mạch pair counter** | y | y (`ch00_cycle_budget.py`) | y (1 MAC vs $P$ MAC: $98.540/P + 3$, 1 vs $P$ DSP, $2P$ cổng đọc M10K, RTF 0,197) | y | y | 201/201 (`ch00_test_pair_counter.py`) | y |
| **0.7 Bản đồ kiểm chứng 3 tầng & golden v2** | y | y (`ch00_golden_spec.py`, `ch00_table_golden.py`) | y (Parabol vs sinc70, Median vs Viterbi) | y | y | n/a | y |
| **Bài tập cuối chương (5 bài tập)** | y | y (`ch00_exercises.py`) | y (Đề bài và lời giải toán học chi tiết) | n/a | n/a | n/a | y |

---

## 2. Thống kê quy mô tài liệu và hiện vật (Metrics Summary)

- **Số trang PDF (`phan_moi_v3.pdf`):** 31 trang (Mục lục pp. 1--2, toàn bộ Chương 0 chiếm 29 trang, từ trang 3 đến trang 31).
- **Số từ trong tệp `.tex` (`chuong_v3/chuong_00_bai_toan.tex`):** 20.047 từ (1.155 dòng, 114.341 ký tự).
- **Số hình vẽ (Figures):** 1 hình TikZ kiến trúc hệ thống toàn tuyến (`chuong_v3/fig_ch00_system.tex`, `Hình 1`), đã được căn chỉnh khoảng cách các khối, không còn va chạm văn bản, nhãn nằm tách bạch trên nền trắng.
- **Số bảng dữ liệu (Tables):** 5 bảng:
  1. `Bảng 1`: Tính tay 16 mẫu hiện tượng đếm điểm qua không thất bại với sóng có hài bậc hai ($N=16, f_s=16\text{ kHz}$).
  2. `Bảng 2`: Tính tay 8 mẫu bù suy giảm cửa sổ Hanning theo nguyên lý Boersma ($N=8, P=4$).
  3. `Bảng 3`: Bảng đối chiếu 5 lựa chọn thiết kế: Praat làm gì vs Phần cứng làm gì vs Lý do & Ảnh hưởng.
  4. `Bảng 4`: Bảng tính tay 10 khung mô phạm các độ đo VDE, GPE, FFE và sai số cent.
  5. `Bảng 5`: Kết quả đối chiếu toàn tuyến bộ công cụ golden v2 với Praat 7.0.03 trên tín hiệu tổng hợp chuẩn (sạch và ồn SNR 5 dB), tính theo định nghĩa sai số cent mịn (fine-cent, loại bỏ khung lỗi thô GPE theo đúng Mục 0.5) từ `verify_v3/ch00_table_golden.py`.
- **Số đoạn mã nguồn (Listings):** 2 đoạn mã:
  1. `Listing 1`: Mã nguồn Verilog mạch phát cặp mẫu liên tục `rtl/v3/ch00_pair_counter.v` (78 dòng, giải thích chi tiết từng dòng).
  2. `Listing 2`: Mô hình tương đương Python bit-exact `verify_v3/ch00_pair_counter_twin.py` (giải thích cấu trúc và đối chiếu).
- **Kết quả biên dịch XeLaTeX:** Hoàn thành 2 lượt biên dịch với **0 lỗi**, **0 nhãn chưa định nghĩa (??)**, và **0 cảnh báo Overfull `\hbox`** (hoàn toàn triệt tiêu).
- **Kết quả kiểm tra mã nguồn Praat:** Kịch bản `verify_v3/ch00_praat_lines.py` kiểm tra đối chiếu trực tiếp toàn bộ 15 trích dẫn số dòng của Praat 7.0.03, kết quả 100% chính xác.

---

## 3. Các con số chưa thể đo và danh mục "phải đo" (Measured Items)

Toàn bộ các số liệu thuật toán trong chương đã được kiểm chứng bằng kịch bản Python độc lập và khớp với `golden_v2`. Tuy nhiên, một số chỉ số vật lý gắn liền với phần cứng thực tế và môi trường máy tính người dùng được gắn nhãn **"phải đo"** như sau:
1. **Thời gian chạy của phần mềm Praat gốc trên máy tính:** Phải đo bằng lệnh ghi thời gian trong script Praat `golden_v2/praat_pitch.praat` trên laptop của người dùng (loại trừ thời gian khởi động giao diện GUI và ghi nhận số luồng CPU đang chạy).
2. **Thời gian ghi PIO thực tế từ HPS sang FPGA qua cầu Lightweight:** Ước lượng bi quan trong sách là $1\,\mu\text{s}$/lần ghi (tương ứng $\text{RTF}_{\text{transfer}} \approx 0{,}008$). Thời gian thực tế phải đo trên bo mạch DE10-Standard bằng hàm `clock_gettime(CLOCK_MONOTONIC)` bọc quanh vòng lặp ghi $N$ từ 32-bit (Chương 13 -- phải đo).
3. **Tần số xung nhịp tối đa $F_{\max}$, số lượng ALM, và số khối DSP thực tế:** Giả định tính toán 100 MHz trong Bài tập 5 là giả định thiết kế; thông số thực tế phải đo từ báo cáo Fitter của Intel Quartus Prime sau khi hoàn thành tích hợp toàn bộ hệ thống ở Chương 12 (phải đo).
4. **Bộ file WAV giọng nói thực tế của anh Tú:** Tại thời điểm xuất bản Chương 0, bộ tệp WAV này chưa có sẵn; toàn bộ số liệu đo kiểm thống kê được thực hiện trên tập tín hiệu tổng hợp chuẩn 2,8 s (277 khung); kịch bản `golden_v2/compare.py` đã sẵn sàng để tự động tái chạy ngay khi có dữ liệu.

---

## 4. Phân tích trung thực các điểm yếu còn tồn tại (Honest Remaining Weaknesses)

1. **Nội suy parabol 3 điểm so với sinc70 + Brent của Praat:** Trên tín hiệu sạch, parabol cho sai số cực nhỏ ($< 1{,}1$ cent). Nhưng khi có tạp âm mạnh (SNR 5 dB), đỉnh tự tương quan bị biến dạng hoặc chẻ đôi, khiến xấp xỉ parabol lệch tới 32,9 cent.
2. **Xếp hạng ứng viên bằng điểm số nguyên trên lưới rời rạc:** Việc tính $S_c[\tau]$ trên các tọa độ nguyên $\tau$ trước khi nội suy (thay vì tính tại tọa độ thực nội suy như Praat) có thể dẫn tới hiện tượng lật thứ tự ưu tiên khi hai đỉnh quãng tám có điểm số chênh lệch cực nhỏ (chênh $0{,}0005$ đến $0{,}007$), gây ra sai khác ở 3/207 khung trên file ồn 5 dB (các khung 63, 64, 172). Đây là hiện tượng cạnh tranh sít sao giữa hai đỉnh quãng tám (near-ties), không phải do sai số lượng tử hóa số nguyên.
3. **Bộ lọc trung vị median-3 thay cho bộ dò đường quy hoạch động Viterbi:** Do phần cứng xử lý luồng theo từng khung để đạt thời gian thực và tiết kiệm bộ nhớ, median-3 chỉ quan sát 3 khung cục bộ nên chỉ sửa được lỗi nhảy quãng tám đơn lẻ (1 khung), không thể sửa được các chuỗi nhảy quãng tám kéo dài từ 2 khung trở lên.

---

## 5. Báo cáo Chi tiết Vòng Sửa đổi (Revision Round 1)

Dưới đây là bảng tổng hợp chi tiết việc khắc phục toàn bộ 20 điểm góp ý của phản biện (Reviewer Feedback Round 1):

### 5.1. Nhóm lỗi nghiêm trọng (Blockers 1--5)

1. **[Blocker 1 - Bảng 4 kết quả golden & định nghĩa cent]:**
   - *Vấn đề:* Số liệu hàng "Twin (trước median) vs Praat R2" và "Twin + median-3 vs Praat R1" bị trộn lẫn giữa báo cáo `compare_report.md` (vốn tính gộp cả khung lỗi thô gross) và định nghĩa sai số cent mịn (non-gross) ở Mục 0.5.
   - *Khắc phục:* Viết kịch bản `verify_v3/ch00_table_golden.py` nạp trực tiếp toàn bộ 16 tệp `.tsv` từ `golden_v2/out/` và tính toán lại thống nhất toàn bộ các hàng theo định nghĩa cent mịn chuẩn (loại bỏ khung GPE). Kết quả được ghi nhận vào `verify_v3/ch00_table_golden.log`. Sao chép chính xác số liệu vào Bảng 4 trong tài liệu:
     - Twin vs Praat R2 (SNR 5 dB): Mean cent = 3,07, p95 = 9,78, Max = 32,91 cent.
     - Twin + median-3 vs Praat R1 (SNR 5 dB): Mean cent = 5,58, p95 = 20,62, Max = 48,41 cent.
   - Bổ sung ghi chú rõ ràng ở đầu bảng và cập nhật các đoạn văn phân tích ở Mục 0.7 và Bảng 2 hàng 5 để hoàn toàn đồng nhất.

2. **[Blocker 2 - Hình 1 kiến trúc hệ thống TikZ]:**
   - *Vấn đề:* Các hộp Ch.3--Ch.6 bị chạm nhau và đè chữ ("31-tap mép Nyquis", "426 mẫu quanh tâm"); đường đứt nét gạch ngang qua nhãn đối sánh Ch.13; nhãn Lightweight đè lên hộp FIFO; đường mũi tên cam đè qua tiêu đề phân vùng FPGA; hàng dưới chạm hàng trên.
   - *Khắc phục:* Viết lại hoàn toàn tệp `chuong_v3/fig_ch00_system.tex`: mở rộng bề rộng tổng thể lên 14.5 cm, tăng khoảng cách giữa các khối lên 2.8 cm, đặt các nhãn xe bus với `fill=white`, căn tách biệt hàng trên và hàng dưới cách nhau 1.5 cm, đưa đường truyền dữ liệu HPS-FPGA vòng ra mép ngoài không cắt qua bất kỳ khối nào. Đã xuất ảnh và kiểm tra trực quan tại 80 dpi và 150 dpi xác nhận hình vẽ hiển thị hoàn hảo.

3. **[Blocker 3 - Phạm vi quét ứng viên của Praat]:**
   - *Vấn đề:* Văn bản trước đây ghi Praat chỉ quét trong dải [27, 213]. Thực tế mã nguồn Praat (`Sound_to_Pitch.cpp` dòng 186) quét toàn bộ $i \in [2, \text{maximumLag}-1]$ (tức 2..213).
   - *Khắc phục:* Sửa lại chính xác ở Bước 7 (trang 8) và Bảng 2 hàng 6: Nêu rõ Praat quét $i = 2 \dots 213$, các lag $2 \dots 26$ vẫn có thể sinh đỉnh nhưng tương ứng tần số $\ge 600\text{ Hz}$ nên bộ dò đường Viterbi coi là vô thanh (`Pitch.cpp` dòng 558, `Pitch_util_frequencyIsVoiced`). Giải thích vì sao trên phần cứng FPGA ta quét trực tiếp $[27, 213]$ (với lag 26 và 214 làm hàng xóm biên cho nội suy parabol 3 điểm) là hoàn toàn tương đương (`golden_v2/README` độ lệch 6).

4. **[Blocker 4 - Trích dẫn số dòng mã nguồn Praat 7.0.03]:**
   - *Vấn đề:* Một số số dòng trích dẫn trong Bước 2, Bước 5, Bước 6, Bước 7 bị lệch so với mã nguồn thực tế của Praat 7.0.03.
   - *Khắc phục:* Viết kịch bản `verify_v3/ch00_praat_lines.py` kiểm tra tự động và đối chiếu từng tệp mã nguồn:
     - Bước 2: `Sampled.cpp` dòng 56--70 (`Sampled_getWindowSamples`/`Sampled_xToLowIndex`) và dòng 71--82 (`Sampled_shortTermAnalysis`).
     - Bước 3: `Sound_to_Pitch.cpp` dòng 56--66 (tính trung bình cục bộ 426 mẫu) và dòng 68--84 (sao chép khung, trừ trung bình và nhân cửa sổ).
     - Bước 5: `Sound_to_Pitch.cpp` dòng 87--102 (tìm `localPeak` trên span $\pm 107$ mẫu, gán `intensity` kẹp về 1 ở dòng 102).
     - Bước 6: `Sound_to_Pitch.cpp` dòng 145--160 (FFT 1024 điểm khung tín hiệu qua `NUMfft_forward`), dòng 422--435 (FFT và tự tương quan cửa sổ `windowR`), dòng 162--164 (chuẩn hóa Boersma).
     - Bước 7: `Sound_to_Pitch.cpp` dòng 185--200 (quét đỉnh và ước lượng parabol ban đầu), dòng 250--260 (`NUMimproveMaximum`, tinh chỉnh sinc70 + Brent).
   - Toàn bộ trích dẫn đã được cập nhật chính xác vào văn bản và kịch bản khẳng định thành công (log lưu tại `verify_v3/ch00_praat_lines.log`).

5. **[Blocker 5 - Kiểm chứng ch00_metrics.py với golden_v2]:**
   - *Vấn đề:* Kịch bản `ch00_metrics.py` trước đây chỉ đọc tệp JSON mà chưa thực sự nạp các tệp `.tsv` và chạy hàm `compute_metrics()`.
   - *Khắc phục:* Cập nhật hàm `verify_against_golden()` trong `verify_v3/ch00_metrics.py` để nạp toàn bộ 16 tệp `.tsv`, thực thi `compute_metrics()`, và khẳng định bằng `assert` rằng số lượng khung VDE, GPE, FFE và sai số cent cực đại trùng khớp 100% với `golden_v2/out/compare_summary.json`. Ghi nhận sự khác biệt có chủ ý về thống kê trung bình/p95 giữa cent thô và cent mịn. Viết lại câu văn ở Mục 0.5 để phản ánh đúng thực tế kiểm chứng.

---

### 5.2. Nhóm vấn đề lớn (Majors 6--12)

6. **[Major 6 - Độ bao phủ kiểm thử HDL tb_ch00_pair_counter.v]:**
   - *Khắc phục:*
     - Bổ sung cơ chế xuất tệp vết chu kỳ đối chu kỳ (`tb_ch00_dump_small.txt`) cho các cấu hình nhỏ $N \le 40$ và so sánh khớp từng dòng (line-by-line diff) với mô hình Python twin.
     - Bổ sung lệnh `assert` kiểm tra mã băm kiểm tra chuẩn `canonical_crc == 32'h26518cf3` cho cấu hình chuẩn Praat.
     - Khẳng định tính chất chu kỳ đối chu kỳ không bóng bóng trên toàn bộ 200 cấu hình ngẫu nhiên bằng lệnh `assert(total_cycles == exp_pairs)` với $\text{exp\_pairs} = N + \sum_{\tau=\tau_{\min}}^{\tau_{\max}} (N - \tau)$.
     - Cập nhật `verify_v3/ch00_test_pair_counter.py` và nhật ký kiểm thử.

7. **[Major 7 - Giải thích chi tiết mã nguồn Verilog Listing 1 & Python Twin]:**
   - *Khắc phục:*
     - Cập nhật lại toàn bộ số dòng tham chiếu khớp chính xác với Listing 1: `STATE_IDLE` (dòng 30--41), `STATE_RUN` (dòng 42--70), nhánh kết thúc các lag (dòng 65--68).
     - Bổ sung giải thích kỹ thuật cho từng chi tiết quan trọng: tại sao `max_n` là mạch tổ hợp (đánh giá tức thời điều kiện chạm đỉnh mà không trễ nhịp), tại sao `addr_b` dùng `n_cnt + 1` (kỹ thuật định địa chỉ nhìn trước cho RAM M10K), tại sao cờ `last` tính sớm 1 chu kỳ, tại sao `total_cycles` và `pair_count` khởi tạo từ 1, cơ chế chuyển tiếp 0 nhịp nghỉ $R[0] \to \tau_{\min}$, cơ chế fallback khi `cfg_n == 0`, và xử lý trường hợp biên $N - 1 - \tau = 0$.
     - Bổ sung mục giải thích chi tiết cấu trúc 2 vòng lặp của lớp `PairCounterTwin` trong Listing 2.

8. **[Major 8 - Bổ sung phân tích phương án / đánh đổi / lựa chọn có số]:**
   - *Khắc phục:*
     - Mục 0.4: Thêm tiểu mục phân tích PIO qua Lightweight Bridge so với mSGDMA qua Full Bridge. Đưa ra các con số định lượng cụ thể: lưu lượng 16 kHz 16-bit là $32\text{ KB/s}$; ghép 2 mẫu/từ tương ứng $8.000$ thao tác ghi/giây; thời gian ghi bi quan $1\,\mu\text{s}$ cho ra $\text{RTF}_{\text{transfer}} \approx 0{,}008$ (ghi chú là thông số "phải đo"); phân tích kích thước FIFO $512 \times 16$ (1 khối M10K chứa được 3,2 bước nhảy) so với $1024 \times 16$ (2 khối M10K).
     - Mục 0.6: Thêm tiểu mục phân tích kiến trúc MAC tuần tự 1 DSP so với song song $P$ DSP. Nêu rõ số chu kỳ $\approx 98.540/P + 3$, tiêu tốn $P$ bộ nhân DSP, đòi hỏi $2P$ cổng đọc RAM M10K (cần phân băng hoặc nhân bản bộ nhớ), trong khi kiến trúc 1 DSP đã đạt $\text{RTF} \approx 0{,}197$ ở 50 MHz (vượt xa thời gian thực).

9. **[Major 9 - Đính chính nguyên nhân sai khác 3/207 khung ở SNR 5 dB]:**
   - *Khắc phục:* Sửa đổi cách giải thích ở Mục 0.7 và phần điểm yếu còn tồn tại: 3 khung bị lỗi thô GPE (khung 63, 64, 172) là do hiện tượng cạnh tranh sít sao giữa hai đỉnh quãng tám (near-ties) với chênh lệch điểm số cực nhỏ từ $0{,}0005$ đến $0{,}007$ giữa điểm số lưới nguyên và nội suy sinc70, hoàn toàn không phải do sai số lượng tử hóa số nguyên hay làm tròn số học.

10. **[Major 10 - Đính chính sai số trong Bảng 2 hàng 3]:**
    - *Khắc phục:* Sửa lại câu văn: giá trị $< 10^{-4}$ cent là của bản chuyển mã dấu phẩy động (float port vs Praat), trong khi mô hình số nguyên twin so với Praat R2 đạt trung bình 0,21 cent (p95 = 0,48 cent, max = 1,08 cent) trên tín hiệu sạch và trung bình 3,07 cent trên tín hiệu ồn SNR 5 dB (loại bỏ lỗi thô).

11. **[Major 11 - Chuẩn hóa công thức tín hiệu (1) và giảm giọng văn quá đà]:**
    - *Khắc phục:*
      - Sửa công thức liên tục thành: $x(t) = \sin(2\pi \cdot 100 t) - 0{,}75 \sin(2\pi \cdot 200 t)$ (dấu trừ ở thành phần hài).
      - Bổ sung công thức rời rạc tường minh: $x_{16}[n] = \sin(2\pi \cdot 100 n / 16.000) - 0{,}75 \sin(2\pi \cdot 200 n / 16.000)$.
      - Rà soát toàn bộ tài liệu và loại bỏ các từ ngữ ca ngợi quá mức ("cực kỳ tinh tế", "vi diệu", "đẳng cấp", "ảo diệu"), thay thế bằng giọng văn trung tính, học thuật, chính xác.

12. **[Major 12 - Giải thích hệ số timeStepCorrection trong Praat]:**
    - *Khắc phục:* Bổ sung ở Bước 8 công thức và giải thích về hệ số $\text{timeStepCorrection} = 0{,}01 / \Delta t$ áp dụng cho hai chi phí chuyển tiếp: chi phí nhảy quãng tám ($0{,}35 \cdot (0{,}01/\Delta t)$) và chi phí chuyển đổi có thanh/vô thanh ($0{,}14 \cdot (0{,}01/\Delta t)$) trong `Pitch.cpp` dòng 543--545.

---

### 5.3. Nhóm tiểu tiết và định dạng (Minors 13--20)

13. **[Minor 13 - Độ lệch cent ở Mục 0.1]:**
    - *Khắc phục:* Viết lại chính xác: "204 cent ở 112,5 Hz (khi làm tròn về bin 100 Hz)".

14. **[Minor 14 - Lược bỏ chi tiết tự sự về các thất bại quá khứ]:**
    - *Khắc phục:* Loại bỏ đoạn văn tự sự "Các phiên bản thử nghiệm trước đây của dự án đã từng vấp ngã..." ở Bước 3; tập trung trực diện vào kỹ thuật: trung bình được tính trên 426 mẫu quanh tâm khung ($106 \dots 531$).

15. **[Minor 15 - Thống kê 10 khung mô phạm Mục 0.5]:**
    - *Khắc phục:* Đồng nhất định dạng 2 chữ số thập phân cho toàn bộ các giá trị cent trong bảng tính tay 10 khung: $0{,}00, 22{,}93, 34{,}98, 31{,}19$, giá trị trung bình là $22{,}28$ cent.

16. **[Minor 16 - Thống nhất ngưỡng JND giữa Mục 0.5 và Bài tập 2]:**
    - *Khắc phục:* Thống nhất định nghĩa JND (Just Noticeable Difference): $5 \dots 10$ cent đối với sóng sin thuần và người nghe được đào tạo, $10 \dots 25$ cent đối với nguyên âm tiếng nói tự nhiên phức tạp.

17. **[Minor 17 - Định nghĩa ngưỡng im lặng silence threshold]:**
    - *Khắc phục:* Nêu rõ `silence threshold` (mặc định 0,03) là tỉ số biên độ đỉnh tuyệt đối cục bộ so với đỉnh toàn cục ($\text{localPeak}/\text{globalPeak}$), hoàn toàn không phải đo bằng năng lượng hiệu dụng RMS.

18. **[Minor 18 - Chuẩn hóa tiêu đề mục con 0.7 và Bài tập cuối chương]:**
    - *Khắc phục:* Sửa tiêu đề các mục con trong 0.7 thành `\subsection*{0.7...}`, `\subsubsection*{0.7.1...}` đến `0.7.4`. Chuyển tiêu đề Bài tập cuối chương thành `\subsection*{Bài tập cuối chương}` không đánh số để mục lục phẳng và nhất quán.

19. **[Minor 19 - Tính không tuần hoàn của dãy trong Bài tập 3]:**
    - *Khắc phục:* Bổ sung giải thích tường minh: dãy số $x = [0, 1, 0, -1, 0, 2, 0, -1]$ không tuần hoàn vì các giá trị đỉnh 0 và 2 không lặp lại; phép tính toán nhằm minh họa việc chuẩn hóa Boersma triệt tiêu định kiến suy giảm cửa sổ ngay cả khi tín hiệu biến thiên tự nhiên.

20. **[Minor 20 - Gắn nhãn "(phải đo)" cho giả định $F_{\max}$ trong Bài tập 5]:**
    - *Khắc phục:* Đã bổ sung ghi chú rõ ràng rằng giả định $F_{\max} = 100\text{ MHz}$ chỉ là tham số thiết kế để ước tính ngân sách chu kỳ; tần số hoạt động thực tế trên FPGA DE10-Standard phải được đo đạc từ báo cáo của Quartus TimeQuest Timing Analyzer (phải đo).

---

## 6. Báo cáo Chi tiết Vòng Sửa đổi 2 (Revision Round 2)

**Ngày hoàn thành đợt sửa đổi 2:** 11/11/2026  
Khắc phục triệt để 3 điểm tồn đọng duy nhất từ phản biện (Reviewer Feedback Round 2) cùng 2 điểm cải thiện phi chặn:

### 6.1. Khắc phục lỗi Hình 1 (chuong_v3/fig_ch00_system.tex)
1. **Khoảng cách và chống va chạm các hộp HPS (Mục 1.a):**
   - Đặt lại tọa độ tâm 4 khối HPS thành $x = 3{,}5; 6{,}5; 9{,}5; 12{,}5$ cm (bước cách $3{,}0$ cm), bề rộng mỗi khối cố định $2{,}2$ cm, tạo ra khoảng hở thực tế giữa mọi cặp khối kề nhau là **$0{,}80$ cm** (vượt xa yêu cầu $\ge 0{,}4$ cm).
   - Rút gọn văn bản trong từng khối để đảm bảo đệm an toàn tuyệt đối, không chạm viền:
     - Khối `WAV Parser`: `Kiểm tra RIFF / Bỏ qua LIST`.
     - Khối `globalPeak`: `Đỉnh biên độ GP / max |x - xbar| (16-bit)`.
     - Khối `Lưới khung`: `Căn giữa tệp / t1, hop 160 mẫu`.
     - Khối `C Driver`: `PIO, 2 mẫu/từ / Ghi 32-bit MM`.
   - Mở rộng khung nét đứt HPS bao bọc từ $x=2{,}1$ đến $x=14{,}0$ cm; mũi tên liên kết `(grid) -> (drv)` có độ dài $0{,}80$ cm hiển thị rõ ràng, không còn va chạm viền hay đè chữ.
2. **Đường truyền dữ liệu C Driver $\to$ FIFO và nhãn cầu nối (Mục 1.b):**
   - Định tuyến đường bus cam từ `C Driver` đi thẳng vào góc trên bên trái của khối `On-Chip FIFO` (`(drv.south) -- (fifo_in.north -| drv.south)`) tại tọa độ $x = 12{,}5$ cm.
   - Bố trí nhãn `Cầu nối HPS--FPGA \\ (Lightweight)` tại $x = 12{,}7$ cm với `anchor=west, fill=white, inner sep=1.5pt` (nằm lệch về bên phải đường bus cam $0{,}2$ cm).
   - Ngắt nhãn thành 2 dòng giúp bề ngang nhãn chỉ còn $\approx 2{,}2$ cm, vừa vặn hoàn hảo bên trong khung viền cam cầu nối $[11{,}0; 15{,}4]$ cm. Đường mũi tên bus cam tuyệt đối không cắt qua nhãn chữ; nhãn không tràn ra ngoài viền khung.
   - Kiểm tra trực quan bằng `pdftoppm` ở độ phân giải 300 DPI xác nhận 100% các cạnh hộp, nhãn và đường liên kết đều cách biệt, sắc nét và đạt chuẩn xuất bản.

### 6.2. Hiệu chỉnh số dòng trích dẫn theo đúng bản Praat 7.0.03 (commit 6a9874e)
1. Cập nhật toàn bộ các mốc số dòng trong `chuong_v3/chuong_00_bai_toan.tex`:
   - `globalPeak`: `Sound_to_Pitch.cpp` dòng 375--385 (dòng 375: `globalPeak = 0.0;`, hàm `NUMmean`).
   - Làm tròn cửa sổ 638 mẫu: `Sound_to_Pitch.cpp` dòng 335--339 (`halfnsamp_window = nsamp_window / 2 - 1`).
   - Công thức cửa sổ Hanning $N+1$: `Sound_to_Pitch.cpp` dòng 422--425 (`0.5 - 0.5 * cos`).
   - FFT cửa sổ, `windowR`, chuẩn hóa và `brent_ixmax`: `Sound_to_Pitch.cpp` dòng 430--445.
   - FFT khung tín hiệu: `Sound_to_Pitch.cpp` dòng 147--157 (`NUMfft_forward` tại dòng 150).
   - Chuẩn hóa Boersma $r[\tau]$: `Sound_to_Pitch.cpp` dòng 163--165.
   - Dò ứng viên và tinh chỉnh: quét đỉnh dòng 185--200; nội suy sinc70 + Brent dòng 254--270 (`NUMimproveMaximum` tại dòng 258).
   - Lưới khung thời gian: `Sampled_getWindowSamples` bắt đầu từ `Sampled.cpp` dòng 53; hàm nội tuyến `Sampled_xToLowIndex` trong `Sampled.h` dòng 34; `Sampled_shortTermAnalysis` dòng 71--82.
   - Giữ nguyên các trích dẫn đã chính xác: dòng 56--66, 68--84, 87--102, 102, và `Pitch.cpp` dòng 543--545, 550--565, 558.
2. Cập nhật kịch bản `verify_v3/ch00_praat_lines.py`:
   - Đặt đường dẫn `/workspace/tools/praat_src` lên đầu tiên trong `SEARCH_PATHS`.
   - Bổ sung cơ chế kiểm tra tính hợp lệ của cây mã nguồn Praat: tự động từ chối cây mã nguồn nếu dòng 375 của `Sound_to_Pitch.cpp` không chứa `globalPeak = 0.0;` (ngăn chặn nhầm lẫn với các cây mã nguồn cũ).
   - Tích hợp các đoạn trích dẫn chuẩn của Praat 7.0.03 commit 6a9874e làm fallback khi chạy trên máy chưa gắn thư mục `/workspace/tools/praat_src`.
   - Kết quả kiểm chứng đạt **17/17 trích dẫn PASS 100%**, in ra thông báo `ALL PRAAT 7.0.03 CITATIONS VERIFIED SUCCESSFULLY.` (nhật ký lưu tại `verify_v3/ch00_praat_lines.log`).

### 6.3. Sửa định nghĩa ngưỡng im lặng Silence Threshold
- Viết lại câu mô tả tại trang 9 (dòng 275 trong `.tex`): Praat không bao giờ hạ độ mạnh của ứng viên có thanh bằng ngưỡng này. Thực tế, khi cường độ $\text{intensity}$ giảm xuống dưới ngưỡng, Praat kích hoạt vùng dốc phi tuyến nhằm **nâng cao độ mạnh của ứng viên vô thanh** qua công thức $0{,}45 + \max(0, \; 2 - \text{intensity}/(0{,}03/1{,}45))$ (`Pitch.cpp` dòng 553--555), giúp ứng viên vô thanh giành thắng thế trong các khung thì thầm hoặc yên lặng.

### 6.4. Các hiệu chỉnh bổ sung (Non-blockers)
- Lược bỏ câu văn tán dương "Đây chính là linh hồn toán học giải thích vì sao phần mềm Praat đạt được độ tin cậy và danh tiếng vượt trội..." tại dòng 199 để văn phong thuần túy kỹ thuật và khách quan.
- Chỉnh sửa dòng 3 trong Bảng 2 từ "tích lũy 48-bit" thành "cần 43 bit, dùng 48 bit" để phản ánh chính xác kết quả phân tích độ rộng bit ở Chương 7.

---

## 7. Lịch sử các Commit Git trên nhánh v3

```text
3dd693e v3: ch00 r2 fixes
7398d87 v3: ch00 r1 box-verified logs
0d0819d v3: ch00 revision
0eae97d v3: ch00 box-verified logs
17a6fcd v3: restore LF / exec bit on run_agy*.sh (Windows mode change)
8ca267f v3: ch00 done
5ecd2ce v3: ch00 format fixes and verified scripts
e91a19d v3: ch00 bài tập cuối chương
06fd6fe v3: ch00 0.7 bản đồ kiểm chứng ba tầng và bộ golden v2
be9e12a v3: ch00 0.6 ngân sách chu kỳ rtf và mạch pair counter
4d1687f v3: ch00 0.5 các phép đo đánh giá GPE VDE FFE và cent
10a11d3 v3: ch00 0.4 kiến trúc hệ thống và bản đồ các chương
961174a v3: ch00 0.3 tám bước praat và lựa chọn thiết kế
fbf57fa v3: ch00 0.2 ý tưởng của Boersma
6812dd9 v3: ch00 0.1 một file hai câu trả lời
```
