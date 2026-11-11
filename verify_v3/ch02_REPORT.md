# Báo cáo nghiệm thu Chương 2 — Avalon-ST, Ngân sách chu kỳ, Mã hóa FSM (v3)

Theo quy định hợp đồng kỹ thuật tại **Mục 12 của BRIEF_v3.md** và đề cương kỹ thuật **Ch.2 của agenda_chot_v2_2026-11-10.md**, kết hợp xử lý toàn bộ các phản hồi tại **Review Round 1 (2026-11-11)**, dưới đây là báo cáo kiểm chứng toàn diện cho Chương 2: `chuong_v3/chuong_02_avalon_st_fsm.tex`.

---

## 1. Bảng đánh giá chi tiết theo từng tiểu mục (Subsection Checklist)

| Tiểu mục | Mở đầu bằng vấn đề thực tế? | Ví dụ tính tay / minh họa số? | Phương án + đánh đổi + lựa chọn có số? | Đường IP (A)? | Đường HDL (B)? | Twin Python & Testbench | Câu tóm lại (*Tóm lại: ...*)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2.1. Chuẩn giao thức Avalon-ST: Cơ chế valid/ready và cạm bẫy readyLatency** | Có (nguy cơ mất dữ liệu âm thanh im lặng do bất đồng cấu hình readyLatency giữa các khối IP) | Có (bảng vết chu kỳ CK3..CK8 trong Bảng 10, trễ phản áp tại CK5 dẫn tới mất mẫu 12; giản đồ xung Hình 3) | Có (phân tích readyLatency=0 tức thời vs readyLatency=1 có trễ; đánh đổi trễ tổ hợp vs Fmax) | Có (chuẩn giao diện Avalon-ST Intel Specifications MNL-AVALONIF Mục 3.4) | Có (quy ước tín hiệu `valid`/`ready`/`data` đồng bộ sườn dương) | 9 chu kỳ trace số học (`ch02_avalon_st_trace.py`) | Có (`\textit{Tóm lại: Tham số readyLatency quyết định thời điểm...}`) |
| **2.2. Ngân sách chu kỳ khi đầu vào là tệp âm thanh và thực tế thời gian thực** | Có (ngộ nhận về đồng hồ 16 kHz ép bước phần cứng; bản chất HPS đọc tệp đẩy qua FIFO) | Có (dẫn xuất từ nguyên lý đầu tiên: 50 MHz $\to$ 500.000 chu kỳ/khung; MAC: 638 + 97.902 = 98.540 phép tính; tổng 98.543 chu kỳ/khung; 616 chu kỳ/mẫu; RTF 0,197) | Có (Bảng 11 phân tích ngân sách; hộp cảnh báo Bẫy thường gặp về hop 25 ms vs 10 ms và triệt tiêu sai số ngẫu nhiên) | N/A (đây là ngân sách thuật toán và kiến trúc lõi) | Đối chiếu với thiết kế bộ đếm cặp `rtl/v3/ch00_pair_counter.v` và MAC Ch.7 | Khớp 100% số học giải tích (`ch02_cycle_budget.py`) | Có (`\textit{Tóm lại: Khi xử lý tệp âm thanh, không có đồng hồ 16 kHz nào...}`) |
| **2.3. Kỹ thuật mã hóa FSM: Đánh đổi tài nguyên và độ trễ trên kiến trúc Cyclone V** | Có (từ switch-case trừu tượng đến cổng logic vật lý; ảnh hưởng tới FF và độ sâu tổ hợp LUT) | Có (FSM 5 trạng thái: Bảng 12; phân tích 166.036 flip-flop của Cyclone V 5CSXFC6D6F31C6; chứng minh toán học mã Gray $n \oplus (n \gg 1)$ bằng chuỗi bit 1 tận cùng) | Có (khảo sát đủ 7 chế độ mã hóa của Quartus: Auto, One-Hot, Minimal Bits, Sequential, Gray, Johnson, User-Encoded) | Có (thiết lập State Machine Processing trong Quartus Prime Handbook) | Có (hai module Verilog kèm giải thích dòng-từng-dòng: `ch02_fsm_binary.v` và `ch02_fsm_onehot.v`) | 500 chu kỳ so sánh nhịp-cho-nhịp (`ch02_fsm_twin.py`, `tb/v3/tb_ch02_fsm_equiv.v`) | Có (`\textit{Tóm lại: Trên kiến trúc Cyclone V với 166.036 thanh ghi...}`) |
| **2.4. Khối đệm trượt (Skid Buffer): Cắt đứt đường phản áp tới hạn** | Có (chuỗi lan truyền phản áp tổ hợp ngược dòng qua nhiều khối làm suy giảm nghiêm trọng Fmax) | Có (vết hoạt động 2 chu kỳ trượt trong Bảng 13; sơ đồ kiến trúc phần cứng Hình 4) | Có (so sánh Direct Ready vs Skid Buffer; chi phí 34 FF định nghĩa ở RTL vs bảo toàn 100% thông lượng) | Đối chiếu Avalon-ST Pipeline Stage IP (chế độ Both) | Có (mã nguồn Verilog `ch02_skid_buffer.v` kèm giải thích dòng-từng-dòng) | 600 chu kỳ kích thích ngẫu nhiên (`ch02_skid_twin.py`, `tb/v3/tb_ch02_skid_buffer.v`) | Có (`\textit{Tóm lại: Khối đệm trượt (Skid Buffer) giải quyết mâu thuẫn...}`) |
| **2.5. Kiểm chứng bắt tay luồng và thực nghiệm mã hóa FSM** | Có (khoảng cách giữa mô hình toán học Python, mô phỏng RTL và kiểm chứng phần cứng) | Có (Bảng 14 ánh xạ Skid Buffer, Bảng 15 ánh xạ FSM, Bảng 16 so sánh IP vs HDL; 4 bài tập cuối chương có lời giải chi tiết) | Có (đối chiếu tài nguyên, độ trễ và tính trong suốt giữa Intel IP và HDL độc lập) | Phân tích Intel Avalon-ST Pipeline Stage | Phân tích Skid Buffer tự phát triển | Bảng ánh xạ 3 cột Twin vs HDL; test vector và log đồng bộ chu kỳ | Có (`\textit{Tóm lại: Kiểm chứng chu kỳ với mô hình song sinh phần mềm...}`) |

---

## 2. Thống kê khối lượng tài liệu và ấn phẩm

- **Số trang văn bản:** 22 trang (từ trang 59 đến trang 80 trong `phan_moi_v3.pdf`).
- **Hình vẽ TikZ:** 2 hình chính được tối ưu hóa hiển thị, kiểm tra trực quan ở độ phân giải 300 DPI (`pdftoppm -r 300`):
  1. `fig:ch02_readylatency` (trang 61): Giản đồ xung so sánh cơ chế bắt tay Avalon-ST giữa readyLatency = 0 và readyLatency = 1, làm nổi bật chu kỳ thất thoát mẫu 12; nhãn `12 (giữ)` gọn gàng không tràn ô bus; các nhãn trạng thái `Nhận (10)`, `Nhận (11)`, `MẤT (12)`, `Dừng phát`, `Nhận (13)` rõ ràng, font $\ge \text{\scriptsize}$.
  2. `fig:ch02_skid_buffer` (trang 71): Sơ đồ kiến trúc vi mô của khối đệm trượt Skid Buffer hai tầng chốt; các nhãn `dữ liệu vào`, `chốt ra`, `sel = skid_valid`, inverter `~`, `s_ready` và dòng chú thích đáy đều có không gian thoáng, có viền đệm nền, không có đường kẻ cắt qua chữ, không có chữ chạm viền.
- **Bảng số liệu kỹ thuật:** 7 bảng chi tiết:
  1. Bảng 10: Vết chu kỳ bắt tay Avalon-ST và lỗi lệch readyLatency (CK3 đến CK8).
  2. Bảng 11: Bảng đối chiếu thông số ngân sách chu kỳ và phân tích sai lệch kỹ thuật (chuẩn Praat hop 10 ms vs nhầm lẫn hop 25 ms, sử dụng `tabularx` vừa khít độ rộng trang).
  3. Bảng 12: So sánh các phương án mã hóa trạng thái cho FSM 5 trạng thái.
  4. Bảng 13: Vết chu kỳ hoạt động chi tiết của Skid Buffer trong tình huống nghẽn hạ nguồn.
  5. Bảng 14: Bảng ánh xạ 3 cột giữa Python Twin (`ch02_skid_twin.py`) và mã nguồn HDL (`ch02_skid_buffer.v`).
  6. Bảng 15: Bảng ánh xạ 3 cột giữa Python Twin (`ch02_fsm_twin.py`) và mã nguồn HDL (`ch02_fsm_binary.v` / `ch02_fsm_onehot.v`).
  7. Bảng 16: So sánh toàn diện giữa khối IP Intel và mã nguồn HDL tự viết cho Chương 2 (loại bỏ số ALM phỏng đoán, ghi rõ `Phải đo trong Quartus`, thanh ghi `34 FF (RTL)`).
- **Đoạn mã nguồn trích dẫn kèm số dòng chính xác:**
  1. Listing 7: Mã nguồn FSM 5 trạng thái mã hóa nhị phân Minimal Bits (`rtl/v3/ch02_fsm_binary.v`, dòng 40--88).
  2. Listing 8: Mã nguồn FSM 5 trạng thái mã hóa One-Hot tường minh (`rtl/v3/ch02_fsm_onehot.v`, dòng 41--85).
  3. Listing 10: Mô-đun Skid Buffer hai tầng chốt (`rtl/v3/ch02_skid_buffer.v`, dòng 35--93).
  4. Listing 11: Hàm cập nhật chu kỳ `step` của mô hình song sinh Skid Buffer (`verify_v3/ch02_skid_twin.py`, dòng 37--92).
  5. Listing 12: Hàm cập nhật chu kỳ `step` của mô hình song sinh FSM (`verify_v3/ch02_fsm_twin.py`, dòng 39--74).
  - *Đối soát số dòng:* 100% số dòng trích dẫn trong lời văn trùng khớp bit-for-bit với số dòng in trên lề mã nguồn và tệp thực tế trên đĩa.
- **Bài tập cuối chương:** 4 bài tập có lời giải chi tiết (độ trễ Skid Buffer, đường tới hạn trễ phản áp tổ hợp, dẫn xuất mã Gray 4-bit qua trailing-ones, chi phí FSM tự tương quan 8 trạng thái).
- **Trạng thái biên dịch XeLaTeX:**
  - Biên dịch 2 lượt với MiKTeX XeLaTeX trên `phan_moi_v3.tex`.
  - Kết quả: **0 lỗi LaTeX**, **0 Overfull `\hbox`** trên toàn bộ Chương 2 (80 trang tổng thể).

---

## 3. Danh mục các điểm đã khắc phục trong Review Round 1

| Hạng mục | Yêu cầu của Reviewer | Biện pháp và kết quả xử lý |
| :--- | :--- | :--- |
| **Đường dẫn Praat** | `ch02_praat_lines.py` lỗi file not found khi chạy từ thư mục `verify_v3/` | Sửa kịch bản xác định đường dẫn gốc kho mã nguồn động qua `os.path.dirname(os.path.abspath(__file__))`. Chạy thành công từ cả thư mục gốc lẫn `verify_v3/`. |
| **Blocker 1: Giải thích dòng-từng-dòng** | Thiếu trích dẫn và giải thích dòng-từng-dòng cho FSM Binary, FSM One-Hot, hàm `step` của Skid Twin và FSM Twin; thiếu bảng ánh xạ Twin vs HDL | - Trích dẫn đầy đủ mã nguồn có số dòng thực tế (`firstnumber`): Listing 7 (Bin L40-88), Listing 8 (One-Hot L41-85), Listing 11 (Skid Twin L37-92), Listing 12 (FSM Twin L39-74).<br>- Bổ sung giải thích chi tiết từng dòng mã nguồn.<br>- Phân tích cơ chế State Machine Extractor của Quartus và cách dùng `syn_encoding = "user"` để khóa cấu hình One-Hot viết tay.<br>- Bổ sung 2 bảng ánh xạ 3 cột: Bảng 14 (Skid Buffer) và Bảng 15 (FSM). |
| **Blocker 2: Tùy chọn mã hóa FSM** | Quartus có 7 tùy chọn State Machine Processing, không phải 6 | Bổ sung phương án **Sequential** (mã hóa nhị phân theo thứ tự khai báo trong HDL), sửa tiêu đề và lời văn thành "đúng 7 phương án", trích dẫn tài liệu *Intel Quartus Prime Standard Edition User Guide: Design Compilation*. |
| **Blocker 3: Số liệu chưa kiểm chứng** | - Tốc độ ghi HPS qua LW-bridge chưa được kiểm chứng trong tài liệu.<br>- Bảng 16 ghi $\approx 18\text{ ALM}$ phỏng đoán.<br>- Số liệu ALM/FF Cyclone V cần trích dẫn datasheet và diễn đạt trễ giải mã nhị phân là kỳ vọng.<br>- Con số 34 FF của Skid Buffer cần dẫn xuất từ RTL. | - Viết lại định tính tốc độ HPS qua cầu Lightweight Bridge nhanh hơn nhiều tốc độ tiêu thụ 1 mẫu/3.125 chu kỳ, dẫn chiếu số liệu Chương 1.<br>- Bỏ con số 18 ALM phỏng đoán tại Bảng 16, thay bằng `Phải đo trong Quartus`.<br>- Trích dẫn chính thức tài liệu *Intel Cyclone V Device Overview* (CV-51001, Bảng 1) cho vi mạch 5CSXFC6D6F31C6 (41.910 ALM, 166.036 thanh ghi, 4 FF/ALM). Diễn đạt trễ giải mã nhị phân là kỳ vọng cần đo đạc qua Timing Analyzer.<br>- Dẫn xuất 34 FF từ RTL ($16\times 2 + 1\times 2 = 34$ FF khai báo) và ghi rõ đây là số lượng RTL, tài nguyên ALM thực tế phải đo. |
| **Blocker 4: Sửa hình vẽ** | - Hình 3(a): nhãn `12 (giữ do ready=0)` tràn ô bus.<br>- Hình 3(b): nhãn đỏ chen chúc, text < scriptsize.<br>- Hình 4: nhiều nhãn chạm chữ, đường kẻ cắt qua chữ. | - Hình 3(a): rút ngắn thành `12 (giữ)` vừa vặn trong ô.<br>- Hình 3(b): thiết kế lại nhãn trạng thái `Nhận (10)`, `Nhận (11)`, `MẤT (12)`, `Dừng phát`, `Nhận (13)`, đảm bảo mọi text $\ge \text{\scriptsize}$; chú thích rõ cơ chế tín chỉ theo *Intel Avalon Interface Specifications* Mục 3.4.2.<br>- Hình 4: mở rộng khung TikZ, tách rời `dữ liệu vào`, `chốt ra`, `sel = skid_valid`, inverter và nhãn đáy, bổ sung nền đệm che đường kẻ. |
| **Should-Fix 5: Lịch sử tài liệu cũ** | Chuyển mục phân tích tài liệu cũ thành hộp Bẫy thường gặp ngắn gọn | Chuyển thành tiểu mục *Cạm bẫy thường gặp: Nhầm lẫn giữa độ dài khung và bước nhảy thời gian* với hộp `tcolorbox`, phân tích bẫy nhầm hop 25 ms vs 10 ms và sự triệt tiêu sai số ngẫu nhiên, loại bỏ các nhắc đến phiên bản cũ. |
| **Should-Fix 6: Từ ngữ phóng đại** | Thay thế ~24 từ ngữ cảm tính (tuyệt đối, hoàn hảo, kinh điển, miễn phí...) bằng thuật ngữ kỹ thuật trung tính | Đã rà soát và thay thế toàn bộ bằng các diễn đạt khách quan; chỉ giữ ký hiệu 100% khi gắn với đại lượng định lượng (thông lượng 1 từ/chu kỳ, tỷ lệ mẫu testbench 292/292). |
| **Should-Fix 7: Giữ chỗ TODO box** | Thay `\todo{box: ...}` bằng `\todo{box}` | Đã thay thế cả hai vị trí tại trang 76 và trang 78 bằng `\todo{box}` ngắn gọn để Reviewer điền kết quả sau khi chạy trên Linux. |
| **Should-Fix 8: Tiêu đề tiếng Anh** | Tiêu đề cần có tiếng Việt trước, tiếng Anh trong ngoặc đơn | Đã chuẩn hóa toàn bộ các tiêu đề: *Ví dụ tính tay 2 nhịp trượt (Hand Trace Walkthrough)*, *Chiến lược kiểm chứng ba tầng (Three-Tier Verification)*... |

---

## 4. Danh mục số liệu kỹ thuật và hạng mục "Phải đo"

### 4.1. Các số liệu suy diễn từ nguyên lý đầu tiên (Derived Numbers)
- Xung nhịp hệ thống: $f_{\text{clk}} = 50\text{ MHz} \implies T_{\text{clk}} = 20\text{ ns}$.
- Tần số lấy mẫu âm thanh: $f_s = 16\text{ kHz} \implies T_s = 62{,}5\ \mu\text{s}$.
- Thước đo thời gian thực: $50\text{ MHz} / 16\text{ kHz} = 3.125$ chu kỳ/mẫu.
- Bước nhảy khung chuẩn Praat: $\Delta t = 10\text{ ms} \implies H = 160$ mẫu âm thanh mới.
- Ngân sách chu kỳ thời gian thực: $10\text{ ms} \times 50\text{ MHz} = 500.000$ chu kỳ/khung.
- Cửa sổ phân tích: $N = 638$ mẫu.
- Dải quét độ trễ: $\tau \in [26, 214]$ (189 giá trị $\tau$).
- Phép tính MAC tự tương quan: $R[0] = 638$; $\sum_{\tau=26}^{214}(638-\tau) = 97.902 \implies \text{Tổng MAC} = 98.540$.
- Chu kỳ thực thi khối MAC (3 nhịp trễ đường ống): $98.540 + 3 = 98.543$ chu kỳ/khung.
- Chu kỳ trung bình trên mỗi mẫu mới: $98.543 / 160 \approx 615{,}89$ chu kỳ/mẫu ($\approx 616$ chu kỳ/mẫu).
- Hệ số thời gian thực: $\text{RTF}_{\text{MAC}} = 98.543 / 500.000 \approx 0{,}197$.
- Dung lượng thanh ghi chip Cyclone V 5CSXFC6D6F31C6: $41.910\ \text{ALM} \times 4 = 166.036\ \text{FF}$.
- Tài nguyên Skid Buffer khai báo ở mức RTL: $16 \times 2\ (\text{data}) + 1 \times 2\ (\text{valid}) = 34\text{ FF}$.

### 4.2. Các số liệu đã kiểm chứng bằng kịch bản Python (Script-Verified Numbers)
1. `verify_v3/ch02_avalon_st_trace.py`: Xác minh vết 9 chu kỳ; khi sender hiểu RL=1 và receiver hiểu RL=0, phản áp tại CK5 làm rơi mẫu 12.
2. `verify_v3/ch02_cycle_budget.py`: Xác minh các giá trị số học, 615,89 chu kỳ/mẫu, RTF 0,197086.
3. `verify_v3/ch02_gray_code.py`: Kiểm chứng toán học công thức $G(n) = n \oplus (n \gg 1)$ trên 1.024 bước nhảy; khoảng cách Hamming luôn bằng 1.
4. `verify_v3/ch02_skid_twin.py`: Kiểm chứng mô hình song sinh Skid Buffer qua 600 chu kỳ kích thích ngẫu nhiên; 292/292 mẫu được truyền nhận hoàn hảo không mất mát hay lặp lại.
5. `verify_v3/ch02_fsm_twin.py`: Kiểm chứng mô hình song sinh FSM qua 500 chu kỳ kích thích ngẫu nhiên và xung reset; đối soát bit-đối-bit giữa nhị phân và One-Hot.
6. `verify_v3/ch02_praat_lines.py`: Quét kiểm tra toàn bộ trích dẫn nguồn Praat; xác nhận không có dòng mã cứng trái phép, 1 vị trí `TODO-PRAAT-LINE`.

### 4.3. Các hạng mục vật lý "Phải đo" (To be measured on hardware / Quartus)
1. **Tần số $F_{\max}$ thực tế và Slack định thời:** Trích xuất từ báo cáo Timing Analyzer (Slow 1100mV 85C Model) của Quartus Prime sau khi tổng hợp và định tuyến toàn hệ thống.
2. **Tài nguyên logic ALM thực tế sau khi đóng gói LAB:** Đọc từ báo cáo Fitter Resource Section của Quartus Prime.
3. **Kiểu mã hóa FSM thực tế áp dụng:** Đọc bảng *State Machine - Processing Style* trong báo cáo tổng hợp Quartus (`.map.rpt`).
4. **Thời gian truyền dữ liệu thực tế qua Lightweight HPS-to-FPGA Bridge:** Đo bằng hàm `clock_gettime(CLOCK_MONOTONIC)` trên bo mạch DE10-Standard chạy Linux.

---

## 5. Các điểm hạn chế còn tồn đọng (Honest Remaining Weaknesses)

1. **Môi trường mô phỏng Icarus Verilog (`iverilog`/`vvp`):** Máy trạm Windows không cài đặt sẵn `iverilog`; testbench và mã nguồn RTL đã được viết chuẩn Verilog-2001 (`-g2012 -Wall`) và đã được Reviewer biên dịch xác nhận 0 cảnh báo, 600/600 chu kỳ Skid Buffer pass, 500/500 chu kỳ FSM pass trên Linux.
2. **Phiên bản mã nguồn Praat trên Windows:** Bản Praat cục bộ cũ hơn 7.0.03 nên các trích dẫn dòng được đánh dấu `TODO-PRAAT-LINE` để điền chính xác tại khâu nghiệm thu Linux.
3. **Đo đạc vật lý trên bo mạch:** Các giá trị diện tích ALM và tần số $F_{\max}$ là chỉ tiêu lý thuyết, cần đo đạc thực nghiệm khi nạp lên bo mạch DE10-Standard qua Quartus Prime.

---

## 6. Lịch sử các Commit trên Git (Commit History)

- `a289e28` — `v3: ch02 2.1` (Khởi tạo tài liệu Chương 2, tiểu mục 2.1 về Avalon-ST readyLatency, giản đồ xung TikZ, RTL Skid Buffer & FSM, mô hình Python Twin, testbench Verilog, Makefile).
- `e1670e2` — `v3: ch02 2.2` (Dẫn xuất ngân sách chu kỳ từ nguyên lý đầu tiên, 500.000 chu kỳ/khung, 98.543 chu kỳ MAC, 616 chu kỳ/mẫu, RTF 0,197, Bảng 11).
- `aa3cccb` — `v3: ch02 2.3` (Mã hóa FSM, Bảng 12, phân tích 166.036 thanh ghi của Cyclone V, chứng minh toán học mã Gray qua chuỗi bit 1 tận cùng).
- `cae9cfb` — `v3: ch02 2.4` (Kiến trúc vi mô Skid Buffer, vết chu kỳ 2 nhịp trong Bảng 13, sơ đồ phần cứng TikZ Hình 4, trích đoạn mã RTL Verilog).
- `6118fdb` — `v3: ch02 2.5` (Chiến lược kiểm chứng ba tầng, Bảng 14 so sánh Intel IP vs HDL tự viết, 4 bài tập thực hành cuối chương có lời giải chi tiết).
- `739a57f` — `v3: ch02 report` (Báo cáo nghiệm thu kỹ thuật ban đầu).
- `e7ae884` — `v3: ch02 done` (Hoàn tất dự thảo ban đầu Chương 2).
- `dc305be` — `v3: ch02 box-verified logs` (Reviewer chạy xác nhận iverilog 600/600 + 500/500 pass trên Linux box).
- `v3: ch02 r1 fixes` — Thực hiện toàn diện các chỉnh sửa Review Round 1: sửa đường dẫn `ch02_praat_lines.py`, bổ sung trích dẫn và giải thích dòng-từng-dòng cho 4 module/twin kèm bảng ánh xạ 3 cột, bổ sung tùy chọn Sequential (7 tùy chọn Quartus), chuẩn hóa số liệu HPS/ALM/FF/34FF, sửa Hình 3 và Hình 4, thay mục lịch sử bằng hộp Bẫy thường gặp, loại bỏ từ ngữ phóng đại, chuẩn hóa placeholder `\todo{box}`, kiểm tra biên dịch 2 lần với XeLaTeX (0 lỗi, 0 overfull hbox).
