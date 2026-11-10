# Audit phan_moi_fpga_quartus_ch0_14_vi.pdf — 2026-11-10

**Phạm vi:** bản `/workspace/uploads/phan_moi_fpga_quartus_ch0_14_vi.pdf`, 117 trang, tương ứng trang 40–156 của `uoc_luong_f0_praat_fpga_quartus_vi.pdf`. Số trang ghi trong audit là **số in ở chân trang**. Nguồn LaTeX nằm ở `uoc_luong_f0_praat_fpga_quartus/chuong/chuong_XX_*.tex`.
**Đối chiếu với:** toàn bộ nguyên tắc 1–41 và các ca #1–#22 trong `bai-hoc-viet-tai-lieu.md`.
**Script kiểm số:** `verify/audit_phan_moi/check_numbers.py` (tính lại mọi số liệu đáng ngờ) và `verify/audit_phan_moi/terseness_metrics.sh` (đo mức "cộc lốc").

## Tóm tắt

Trục chính là **văn phong cộc lốc**, tức không theo tinh thần Feynman/first-principles. Tài liệu đúng phần lớn số liệu, nhưng đọc như một tờ ghi chú: dòng "nhãn: giá trị", chuỗi mũi tên, hộp chi phí toàn gạch đầu dòng, công thức thả xuống không có câu dẫn. Mức nặng nhất ở Ch.14, 13, 2, 9, 8, 12, 11, 1 (các mục Bước 1–9).

| Mức | Số lượng |
|---|---|
| A. Sai kiến thức / sai số liệu | 17 |
| B. Trên trời rơi xuống / thiếu cầu nối / xếp chồng chủ đề | 16 (12 + 4 từ Argon, đã xác minh) |
| C. Cộc lốc / thuật ngữ chưa giải thích | 15 nhóm (mọi chương) |
| D. Trình bày (hình, chữ "toy", cảm thán, ví dụ bỏ dở, meta-prompt rò rỉ, nhãn hình chồng) | 11 (7 + 4 từ Argon) |
| Thiếu twin Python + HDL cuối mỗi phần (quy tắc mới 39) | hầu hết các phần. Chỉ Ch.3, 6, 11, 12 có cả hai, nhưng ở mức chương chứ không ở mức từng phần |

## 1. Bản đồ trang ↔ file

| Trang in | Chương | File |
|---|---|---|
| 40–49 | 0 | chuong_00_mo_dau.tex |
| 50–71 | 1 | chuong_01_praat.tex |
| 72–79 | 2 | chuong_02_pll_i2s.tex |
| 80–87 | 3 | chuong_03_dc_blocker.tex |
| 88–94 | 4 | chuong_04_fir_23.tex |
| 95–100 | 5 | chuong_05_sliding_ram.tex |
| 101–106 | 6 | chuong_06_window.tex |
| 107–111 | 7 | chuong_07_ac_mac_fft.tex |
| 112–117 | 8 | chuong_08_norm_rom.tex |
| 118–123 | 9 | chuong_09_peak_div.tex |
| 124–130 | 10 | chuong_10_voicing.tex |
| 131–137 | 11 | chuong_11_fsm_avalon.tex |
| 138–144 | 12 | chuong_12_q124.tex |
| 145–151 | 13 | chuong_13_verification.tex |
| 152–156 | 14 | chuong_14_checklist.tex (tr.156 bắt đầu Phụ lục A, thuộc phần cũ) |

## 2. Trục chính: chấm mức cộc lốc từng chương

Thang điểm 1–5, trong đó 5 là cộc lốc nhất. Cột "Feynman": mỗi mục có mở bằng vấn đề thật, xây từ sự thật gốc, có ví dụ đời thường cùng ví dụ tính tay, đoán trước chỗ vướng, và đóng bằng một câu tóm tắt hay không. Cột "Twin+HDL/phần": cuối mỗi phần có cả Python và Verilog giải thích từng dòng hay không.

| Ch. | Từ | \item/1000 từ | Mũi tên | Cộc lốc | Feynman | Twin+HDL/phần | Ví dụ cụ thể |
|---|---|---|---|---|---|---|---|
| 0 | 7348 | 5,0 | 6 | 3 | Một phần: các ô Feynman là đoạn văn, nhưng nhồi định nghĩa; không có câu tóm tắt | Không | tr.43 Feynman 4: "Bước 1 của Praat sử dụng tổ hợp FFT cả câu nói → nhân mặt nạ … → zero-padding để upsample ×2 mềm, dọn sạch mép Nyquist." |
| 1 | 11523 | 7,4 | 47 | 4 (Bước 1–9), 2 (Bước 10–12) | Bước 10–12 tốt; Bước 1–9 kiểu tóm tắt | Không (chỉ Bước 10 và 11 có Verilog) | tr.52 "• Quên dọn Nyquist: tone ∼7…8 kHz giả thành chu kỳ dài…"; tr.69 bảng 10 tham số "Ý nghĩa … một câu" toàn mảnh câu; tr.71 lời giải T3 dạng "xóa → parabolic: lệch vài cent…" |
| 2 | 4067 | 13,0 | 21 | 4 | Có phần "Nhìn thấy vật lý" tốt, nhưng cost box và bài tập cụt | PLL không có HDL tương đương (đúng: PLL là analog nên phải nói rõ lý do); I²S chỉ là đoạn RTL rút gọn bằng comment | tr.73 "• Fmax (…): không phải nút thắt"; tr.74 "FSM Idle→WaitWS→Skip1→Shift16→Push" |
| 3 | 3408 | 2,6 | 2 | 3 (riêng §3.2 là 5) | §3.1 tốt; §3.2 thả cả loạt khái niệm | Có RTL và twin ở mức chương | tr.81 "Đáp ứng tần số gần DC: \|H(e^{jω})\| tăng gần tuyến tính với ω khi ω nhỏ; hằng thời gian xấp xỉ 1/(1−α) mẫu." |
| 4 | 3510 | 3,7 | 21 | 4 (§4.3/4.3b là 5) | §4.1 tốt; §4.3 trên trời rơi xuống | Không có RTL FIR, chỉ 3 dòng comment twin | tr.90 "Noble identity: sau khi hạ mẫu ↓M, các nhánh E_r chạy ở tốc độ thấp hơn…"; tr.92 "RTL thay thế. Khi không gọi IP: systolic MAC + coeff ROM, folding tay nếu N ≤ 32." |
| 5 | 3092 | 3,9 | 4 | 3 | Khá, có ví dụ hộp đen máy bay | RTL và twin có | tr.97 "Latency đọc — điểm dễ lệch khung. • RTL inferred dout <= mem[rd_ptr]: latency 1…" |
| 6 | 3070 | 5,9 | 4 | 2 | Tốt nhất phần mới (§6.1) | Có | tr.106 bài tập 6.1–6.5 đặt câu hỏi liền một khối, lời giải dạng gạch |
| 7 | 2862 | 6,6 | 4 | 3 | §7.1 tốt | MAC chỉ là module stub với comment, không phải RTL thật | tr.109 "module mac_autocorr … // FSM: IDLE -> RUN … -> DONE" |
| 8 | 2847 | 9,8 | 1 | 4 | §8.1 tốt; §8.4 rời rạc | ROM có; LPM_DIVIDE không có RTL tương đương | tr.114 "IP "ALTDIV_TENT" không tồn tại." (câu trơ trọi); tr.115 bảng LPM toàn mảnh câu |
| 9 | 2888 | 10,0 | 12 | 4 | §9.1 khá | Không có RTL non-restoring thật, chỉ wrapper LPM_DIVIDE | tr.120 "Lệch một chu kỳ gắn F0 khung trước vào khung sau — lỗi thời gian, không phải lỗi toán."; tr.121 "Không tồn tại IP ALTDIV_TENT. Chỉ LPM_DIVIDE hoặc RTL non-restoring."; tr.120 ví dụ 13÷3 đầy "…" |
| 10 | 3421 | 6,1 | 12 | 3 | Khá | Có, nhưng twin lệch RTL (xem A13) | tr.127 "• nhân timeStepCorrection= 0,01/∆t nếu đổi hop." |
| 11 | 3007 | 8,6 | 12 | 3 | §11.1 tốt (ống nước có van) | Có | tr.133 danh sách vai trò trạng thái "• IDLE: chờ SOP…" |
| 12 | 2854 | 9,5 | 24 | 3 | §12.1 tốt (thước kẻ) | Có | tr.138 "1. Nhân F0 … 2. Làm tròn … 5. Tách byte" |
| 13 | 3034 | 13,2 | 20 | 4 | §13.1 khá; phần còn lại là danh sách | Chỉ có đoạn assert | tr.148 "• octaveCost / octaveJumpCost: twin float lab tắt pathFinder thì không so được…"; tr.149 testbench toàn gạch |
| 14 | 2618 | 20,2 | 12 | 5 | Checklist, gần như toàn danh sách | Không | tr.152–153 cả chuỗi "• Lý do: …"; tr.155 bảng triệu chứng |

**Mô thức cộc lốc lặp lại**, mỗi kiểu kèm ví dụ thật:
1. **Dòng "nhãn: giá trị" thay câu văn.** Ví dụ "Fmax (maximum frequency — …): dễ > 200 MHz trên tốc độ 6." (tr.85), "Twin: cùng bảng hex C[τ] với ROM phần cứng" (tr.57). Kiểu này có trong mọi hộp CHI PHÍ.
2. **Chuỗi mũi tên thay câu.** Ví dụ "thạch anh → PLL → MCLK/SCLK → I²S RX → DCFIFO → Avalon-ST 50 MHz" (tr.77), "FILL đủ L mẫu → WINDOW → MAC → PEAK/DIV → VOICE/median3 → PACK" (tr.133), "Bước 8: … xóa → parabolic" (tr.71).
3. **Công thức thả xuống không có câu dẫn.** Ví dụ H(z) = Σ z^-r E_r(z^M) (tr.90), "nsampFFT = 2^⌈log2(N(1+depth))⌉" (tr.55), mặt nạ G[k] (tr.51), "Đáp ứng tần số gần DC…" (tr.81).
4. **Câu khẳng định trơ trọi không giải thích.** Ví dụ "Không tồn tại IP ALTDIV_TENT" (tr.114, 116, 121, 153), "Lệch một chu kỳ gắn F0 khung trước vào khung sau" (tr.120), "CIC … méo sinc^N và cần bù — loại khỏi lộ trình này" (tr.88).
5. **Mục xếp chồng chủ đề không có câu chuyển.** Ví dụ §4.3b (tr.91), §1.5 (tr.55–56, DFT + butterfly + Parseval + BFP trong một trang), §3.4 (tr.85, năm đoạn "Đạo hàm cutoff / Vị trí / Tràn 32-bit / So sánh" nối nhau mà không dẫn).
6. **Ví dụ tính tay bỏ dở hoặc không chứng minh điều nó nói.** Ví dụ bảng 13÷3 đầy "…" (tr.120), ví dụ "tín hiệu Nyquist" lại nằm ở bin fs/4 (tr.51), ví dụ alias 9 kHz ở tr.88 không có con số nào.
7. **Thuật ngữ dùng trước khi giải thích.** Noble identity, commutator (tr.90), Brent (tr.58), delta-sigma, oversampling (tr.45), Variable Precision (tr.91), systolic, Distributed Arithmetic (tr.91–92), X-propagation (tr.149, được giải thích muộn), ramstyle (tr.98), Avalon-MM (tr.142).

**Thiếu theo khung Feynman (áp cho hầu hết các mục):** không mở bằng câu hỏi hay sự thật phũ, không có câu tóm tắt bản chất ở cuối, không trả lời trước những chỗ người đọc chắc chắn sẽ vướng (anh Tú đã vướng thật ở tr.43, 47, 81, 89, 90, 91).

## 3. Mức A — Sai kiến thức / sai số liệu

Mọi số trong mục này đã được tính lại trong `check_numbers.py`.

**A1. Polyphase 2/3 chia nhánh mod 3, "E2 không xuất"** (tr.90 §4.3, Hình 25; tr.91 §4.3b; tr.92 §4.4; tr.93 bài tập 4.2; tr.45 Feynman 9 "tiết kiệm đến 66%"; tr.92 "tiết kiệm tới ∼66% nhân").
- Trích: "E0 = [h0, h3], E1 = [h1, h4], E2 = [h2, h5] … chỉ E0, E1 xuất theo lịch 2/3"; "nhánh E2 không xuất nên 0 nhân".
- Sai ở đâu: với ↑2 rồi ↓3, mẫu ra là y[m] = Σ h[k]·x_up[3m−k] và chỉ dùng tap k ≡ m (mod 2). Script xác nhận cách tính trực tiếp khớp polyphase với tap {0,2,4} khi m chẵn và {1,3,5} khi m lẻ. Mỗi mẫu ra tốn 3 phép nhân so với 18 theo cách ngây thơ, tức tiết kiệm 6 lần (83%), không phải 66%.
- Bài học liên quan: #19, #20.
- Cách sửa: viết lại §4.3 theo khuôn #16 và #19. Sửa Hình 25 thành hai nhánh E0 (tap chẵn) và E1 (tap lẻ) dùng luân phiên. Sửa bài 4.2, câu 66% ở tr.45 và tr.92.

**A2. "Giữ 2 trong 3" coi như đúng nếu đã lọc** (tr.88 "Nếu chỉ 'lấy 2 mẫu bỏ 1' mà không lọc, tỷ lệ 2/3 vẫn đúng về số mẫu nhưng sai về phổ"; tr.90 "Lịch 2/3 giữ 2 trong mỗi 3 chỉ số ra sau khi lọc"; tr.93 twin `decimate_2_over_3` giữ i mod 3 ∈ {0,1}; tr.45 "Hạ mẫu là … loại bỏ bớt các mẫu thừa (ví dụ từ 24 kHz xuống 16 kHz)").
- Sai ở đâu: giữ mẫu 0, 1, 3, 4 ở 24 kHz cho các thời điểm 0; 41,67; 125; 166,67 µs, trong khi lưới 16 kHz là 0; 62,5; 125; 187,5 µs. Khoảng cách không đều, tức rung pha, dù đã lọc hay chưa lọc.
- Bài học liên quan: #16.
- Cách sửa: thay twin bằng ↑2 (chèn 0), lọc, ↓3, hoặc bằng polyphase chẵn/lẻ.

**A3. Zero padding được gán là "dọn mép Nyquist"** (tr.43 Feynman 4; tr.50 tiêu đề §1.1 "Soft upsampling: dọn mép Nyquist"; tr.50 "upsample 'mềm' ×2 đồng thời đã dọn sạch mép Nyquist"; tr.71 "Bước 1: Bảo vệ khỏi rò phổ mép Nyquist").
- Sai ở đâu: chỉ mặt nạ G[k] làm giảm năng lượng gần f_N. Padding trong miền tần số chỉ nội suy ×2 và không thêm thông tin.
- Bài học liên quan: #15, #17.
- Cách sửa: tách hai câu riêng cho mặt nạ và cho padding. Đổi tiêu đề §1.1. Thêm câu chặn hiểu nhầm "zero padding không làm giảm rò phổ, không thêm thông tin".

**A4. Zero-pad cho tự tương quan tuyến tính "ít nhất thêm L số 0", "thường lên N_FFT = 2048"** (tr.108 §7.2; tr.110).
- Sai ở đâu: chỉ cần N_FFT ≥ L + τmax = 640 + 214 = 854, nên 1024 là đủ. Chính tr.55–56 cũng nói Praat dùng 1024, nên tài liệu tự mâu thuẫn.
- Bài học liên quan: #15 và nguyên tắc 3 (nói rõ cái gì giới hạn cái gì).
- Cách sửa: nêu điều kiện N ≥ L + τmax và giải thích vì sao.

**A5. Ví dụ "tín hiệu đúng tại Nyquist"** (tr.51).
- Trích: "x = [1,0,−1,0,…] … đúng tại tần số Nyquist của lưới 8 điểm".
- Sai ở đâu: tín hiệu có chu kỳ 4, năng lượng nằm ở bin 2 (fs/4). G[2] = 1 vì 2/8 = 0,25 < 0,475, nên ví dụ không minh họa được tác dụng của mặt nạ.
- Cách sửa: dùng x = [1,−1,1,−1,…] (bin 4) hoặc một tone ở bin 3,9 trên N lớn hơn, rồi tính G[k] cụ thể.

**A6. Số MAC mỗi khung không thống nhất** (120 960 ở tr.46, 48, 53, 56, 71, 133, 148, 154, 155; 98 280 ở tr.107–111).
- Sai ở đâu: tổng không vòng là Σ(640−τ) = 98 280 (đã kiểm). 189 × 640 = 120 960 chỉ là cận trên. Bài 0.2 viết "mỗi giá trị trễ tích lũy L = 640 tích mẫu", trái với định nghĩa L−τ cặp.
- Bài học liên quan: #6, nguyên tắc 18 (nhất quán thông số).
- Cách sửa: định nghĩa con số một lần ở Ch.7, nói rõ "120 960 là cận trên", RTF thật ≈ 0,197.

**A7. 640 × 16 bit "vừa khít 1 M10K"** (tr.53, 55, 95, 98, 103, 135, 155; bảng ngân sách tr.41 "4 khối M10K").
- Sai ở đâu: M10K có 10 240 bit nhưng các cấu hình rộng/sâu là 8K×1, …, 1K×10, 512×20 (hay 512×16), 256×40. Với độ rộng 16 bit thì độ sâu tối đa là 512, nên 640 từ cần 2 khối.
- Mức chắc chắn: rất có thể đúng là lỗi, **cần kiểm tra** bằng báo cáo Fitter.
- Cách sửa: nói rõ hình dạng khối; giải pháp là 2 M10K, hoặc khung 512, hoặc lưu nửa bảng cửa sổ (320 từ). Cập nhật bảng ngân sách.

**A8. Silence gate cứng theo năng lượng Rx[0]/E_ref trong Ch.1** (tr.61–64 §1.10; mâu thuẫn với Ch.10 tr.125 dùng P_local/P_global biên độ).
- Sai ở đâu: theo case #6 trong log (đối chiếu source Praat), silenceThreshold so localPeak/globalPeak theo biên độ và chỉ là chi phí mềm trong ứng viên UV. Praat không có cổng "abort sớm". Việc bình phương thành 0,0009 là sản phẩm tự gán.
- Bài học liên quan: #6, nguyên tắc 25 và 28.
- Cách sửa: dùng đúng công thức Praat (đỉnh biên độ). Nếu FPGA cố ý dùng một cổng cứng theo năng lượng thì gọi đó là lựa chọn thiết kế xấp xỉ, có lý do, và thống nhất với Ch.10.

**A9. Chiều thiên lệch khi quên C[τ] bị viết ngược** (tr.152 mục 6 "Không bù dốc cửa sổ ⇒ thiên vị τ lớn ⇒ octave xuống"; tr.154/155 "Ra ≈ 100 Hz thay vì 200: thường quên nhân C[τ] (đỉnh 2T0 thắng)").
- Sai ở đâu: Ch.8 (tr.112) nói đúng: thiếu C[τ] thì đỉnh τ lớn bị đạp xuống, thuật toán thiên về τ nhỏ, tức cao độ cao giả. Ch.14 nói ngược lại.
- Cách sửa: sửa Ch.14. Triệu chứng F0/2 nên quy cho octave cost hoặc ngưỡng, không quy cho việc quên C.

**A10. Cửa sổ Hanning "dạng cổ điển N−1, nửa bảng" trong checklist** (tr.152 mục 4; tr.153 "đúng mẫu số N−1").
- Sai ở đâu: Ch.1 và Ch.6 chốt Praat N+1, ROM đủ 640 từ. Hai chỗ mâu thuẫn nhau.
- Cách sửa: thống nhất dùng N+1.

**A11. Octave cost "hệ số < 1 nhân thêm"** (tr.115 §8.4c), trong khi Ch.1 (tr.59) ghi đúng là trừ octaveCost·log2(ceiling/F0).
- Mức chắc chắn: cách gộp phép trừ vào ROM nhân là một xấp xỉ, **cần kiểm tra** trong golden `scoring_rom_q13`.
- Cách sửa: nói rõ đây là xấp xỉ nhân thay cho phép trừ và đúng trong điều kiện nào.

**A12. "LPM_DIVIDE … thêm 189×16 chu kỳ nếu tuần tự — phá RTF"** (tr.116).
- Sai ở đâu: 189 × 16 = 3024 chu kỳ, chỉ bằng 0,6% của 500 000, không phá RTF.
- Cách sửa: lý do thật để không chia ở mỗi τ là độ khó khớp bit và tài nguyên, không phải RTF.

**A13. Twin median-3 không khớp RTL; độ trễ "đúng 1 hop" sai** (tr.127–130).
- Trích: RTL cho f_out = {0,0,0,200,200}, script tái hiện đúng. Nhưng twin `median3_stream` cho {0,200,210,200,205}.
- Sai ở đâu: twin không bit-exact với RTL. Đầu ra ở nhịp 4 là trung vị của khung 1–3 (tâm là khung 2), nên độ trễ là 2 hop so với khung tâm, không phải 1.
- Bài học liên quan: #7, #10.
- Cách sửa: viết twin mô phỏng đúng các thanh ghi, hoặc bỏ một tầng thanh ghi. Sửa câu về độ trễ ở tr.46, 65, 126, 129.

**A14. DC-blocker: "Sau khoảng 5·256 mẫu, đầu ra tụt dưới 50 LSB"** (tr.82).
- Sai ở đâu: script cho ra 109 LSB sau 1280 mẫu. Lần đầu dưới 50 LSB là ở mẫu thứ 1480 sau bước. Chỗ tr.85 ghi "1600 mẫu thì |y| < 50" là đúng (31 LSB).
- Cách sửa: sửa thành khoảng 1480 mẫu (≈ 5,8 hằng thời gian).

**A15. Cực DC-blocker "z = 0,995"** (tr.46 Feynman 12) so với α = 0,99609375 (Ch.3). Thông số không thống nhất (nguyên tắc 18).

**A16. Ngân sách DSP mâu thuẫn**: tr.52 "FIR Compiler II — vài chục khối DSP"; tr.41 "3 khối DSP" cho cả luồng; tr.92 bảng ví dụ 4 DSP chỉ riêng cho FIR. Cần một con số và lý do.

**A17. Bài tập 0.1b** (tr.47).
- Trích: "thành phần 7 kHz này sẽ tiếp tục gập qua các ranh giới Nyquist kế tiếp và đổ thẳng vào dải vài trăm Hertz".
- Sai ở đâu: sau 16 kHz không còn bước hạ mẫu nào. Đây là bài giả định mà lời giải không nói rõ.
- Bài học liên quan: #17.
- Cách sửa: theo case #17, giải thích trên hai mặt trận (tần số và tự tương quan; 7 kHz có chu kỳ ≈ 2,29 mẫu).

**Cần kiểm tra (độ tin thấp):**
- tr.110 BFP: −5 dịch phải 1 bit ghi là −2. Dịch số học cho −3; cách cắt về 0 mới cho −2. Phải nói rõ quy ước.
- tr.117 bài 8.3: "Floor thay round lệch tối đa 0,5 LSB". Hai cách khác nhau tối đa 1 LSB nguyên.
- tr.49 bài 0.4b: lý giải "rò phổ formant tạo gợn chu kỳ ngắn đè lên tự tương quan" chưa được chứng minh.
- tr.68 "Viterbi … làm trễ tín hiệu hàng giây" mâu thuẫn với lý do ở Ch.10.
- Số ALM của median-3: 22–28 (tr.66), 25 (tr.68), < 200 (tr.71), 60–100 (tr.129). Không nhất quán.

**Số đã kiểm và ĐÚNG** (giữ nguyên khi viết lại): ví dụ dB 0,224/0,0251 và tỉ lệ ×79,4; PLL 1507/73/84 → 12,28799739 MHz, −0,212 ppm; trôi 48 mẫu; Gray; bảng y_acc tr.82; fc 9,947 Hz và 29,84 Hz; folding 27; h_q tổng 32769; full conv [1,4,10,…,36]; R_w[0] = 258 100 276 868; bảng C[τ] 8281/9078/12412/17429; cosine R[0], R[4], R[8]; parabolic 3/14, 199,466 Hz, Q12.4 3191 và bảng quét; sinc 0,51296; octave cost; Viterbi 3 khung và bài 1.12; s_UV 1,48333; Q12.4 bytes; cent 0,541/1,443/0,180; GPE/VDE/FFE.

## 4. Mức B — Trên trời rơi xuống / thiếu cầu nối

| # | Trang, mục | Trích | Thiếu gì | Cách sửa |
|---|---|---|---|---|
| B1 | tr.81 §3.2 | "Zero … tại z = 1 — đúng tần số 0 Hz … Đáp ứng tần số gần DC: \|H\| tăng gần tuyến tính…" | Không dẫn vì sao trễ 1 mẫu = z^-1 và vì sao z = e^{jω}; không có hình học khoảng cách; không nói hằng thời gian là gì; fc là −3 dB; không có bảng \|H\| | Làm đủ 6 câu hỏi của case #21 (bản mẫu ở mục 6.1) |
| B2 | tr.90 §4.3 | "Viết k = mM + r … H(z) = Σ z^-r E_r(z^M) … Noble identity" | Không đi từ chỗ lãng phí của cách ngây thơ; dùng sai M | Case #19 (bản mẫu 6.2) |
| B3 | tr.91 §4.3b | ba chuyện liền nhau | Thiếu câu chuyển | Case #20 |
| B4 | tr.89 §4.2 | "Khi thiết kế pha tuyến tính … hệ số đối xứng" | Không tách x với h; không nói vì sao h đối xứng (sinc chẵn); thiếu bit thêm cho (a + d) | Case #18 |
| B5 | tr.51 §1.1 | mặt nạ G[k] và IFFT_2N pad | Không có câu dẫn hay ví dụ số đúng | Dẫn từ vấn đề (tr.50), rồi tính G ở 3 bin |
| B6 | tr.55 §1.5 | nsampFFT = 2^⌈log2(N(1+depth))⌉ | "depth" chưa định nghĩa; không nói vì sao 1,5 | Giải thích depth = phần pad cho lag, nối với A4 |
| B7 | tr.55–56 §1.5 | DFT 8 điểm + butterfly + Parseval + BFP trên một trang | Xếp chồng | Tách thành mảnh, có câu chuyển |
| B8 | tr.58 §1.8 | "NUMimproveMaximum … SINC70 … Brent" | Brent chưa định nghĩa | Giải thích tìm cực trị Brent bằng một câu và một ví dụ |
| B9 | tr.85 §3.4 | năm đoạn kỹ thuật nối nhau | Không có câu chuyển | Tách mục con, có câu dẫn |
| B10 | tr.120 §9.4 | "Golden Mode B: f0 = (16000·16·65536 + …)//…" | Không giải thích vì sao 65536, vì sao cộng nửa mẫu số | Dẫn Q16 rồi Q12.4 từng bước bằng số |
| B11 | tr.127 §10.5 | "nhân timeStepCorrection= 0,01/∆t" | Không có lý do | Giải thích chuẩn hóa theo hop |
| B12 | tr.145 §13.2 | GPE "Ngưỡng 20% roughly một quãng gần" | Mảnh câu nửa Anh nửa Việt | Viết lại: 20% ≈ 3,2 bán cung, vì sao chọn |

## 5. Mức C/D — Thuật ngữ và trình bày

- **C1. Thuật ngữ chưa giải thích lúc gặp lần đầu:** delta-sigma, oversampling (tr.45, 72); Noble identity, commutator (tr.90); Variable Precision DSP, systolic, Distributed Arithmetic, Mult-add (tr.91–92); Brent (tr.58); ramstyle (tr.98); readyLatency (tr.131 đã giải thích, đạt); X-propagation (tr.148 dùng, tr.149 mới giải thích); Avalon-MM (tr.142); "Mode B" (tr.118, không nói Mode A là gì); "unbiased" (tr.53).
- **C2. Câu trơ trọi về IP bịa:** "ALTDIV_TENT" lặp 4 lần (tr.114, 116, 121, 153). Người đọc không biết tên này từ đâu ra. Nên bỏ hẳn, hoặc viết một câu: "một số tài liệu trên mạng nhắc tên ALTDIV_TENT, nhưng IP này không có trong Quartus; phép chia dùng LPM_DIVIDE".
- **D1.** Chữ "toy" ở tr.83 ("mô hình toy") vi phạm brief.
- **D2.** Cảm thán vô nghĩa (nguyên tắc 11): "cực kỳ thanh lịch" (tr.65), "yêu cầu sinh tử" (tr.47), "khuôn vàng thước ngọc" (tr.41), "sống còn" (tr.48).
- **D3.** Ví dụ bỏ dở: bảng 13÷3 (tr.120).
- **D4.** Hình 9 (tr.50) có chú thích "Ô xanh dương nhạt … bước 1–2 bị xóa hoặc thay", trong khi bước 2 vẫn giữ.
- **D5.** Hình 7 (tr.40): chữ bị dính, ví dụ "I2 S serialChương 2: PLL + I 48 kHz PCM" khi trích xuất. **Cần kiểm tra** bằng mắt trên ảnh render.
- **D6.** Listing 2 (tr.63): caption bị lặp hoặc vỡ "]Silence + Voicing Gate…".
- **D7.** Thiếu "Đọc hình" (nguyên tắc 19) cho đa số hình từ Hình 7 đến Hình 62.

## 6. Bản mẫu viết lại (minh họa văn phong đúng)

### 6.1 §3.2 (tr.81), đoạn đầu: từ phương trình sai phân đến "z = 1 là 0 Hz"

> Câu hỏi đầu tiên là: làm sao một bộ lọc chỉ có hai phép cộng trừ lại "biết" đâu là tần số 0 Hz? Hãy bắt đầu từ việc bộ lọc thật sự làm với từng mẫu. Phương trình sai phân $y[n]=x[n]-x[n-1]+\alpha\,y[n-1]$ nói rằng mẫu ra bằng hiệu giữa mẫu vào hiện tại và mẫu vào trước đó, cộng thêm một phần $\alpha$ của mẫu ra trước đó. Phần hiệu $x[n]-x[n-1]$ là cái máy giết DC: nếu tín hiệu đứng yên, ví dụ $x=[5,5,5,5]$, thì mọi hiệu đều bằng 0.
>
> Để biết bộ lọc làm gì với từng tần số, ta đưa vào một "kim đồng hồ" dài đúng 1 đơn vị: $x[n]=e^{j\omega n}=\cos(\omega n)+j\sin(\omega n)$. Mỗi mẫu, kim quay thêm $\omega$ radian. Mẫu trễ một nhịp, $x[n-1]$, là vị trí của kim một tích tắc trước đó, tức $e^{j\omega n}\cdot e^{-j\omega}$. Độ dài vẫn là 1 và góc lùi lại $\omega$. Vì vậy "trễ 1 mẫu" luôn tương đương "nhân với $e^{-j\omega}$", và người ta viết gọn $z=e^{j\omega}$, tức trễ 1 mẫu là nhân với $z^{-1}$. Thay vào phương trình rồi chia hai vế cho $x[n]$, ta được $H(z)=\dfrac{1-z^{-1}}{1-\alpha z^{-1}}$. $H$ cho biết sóng tần số $\omega$ đi ra bị phóng to hay thu nhỏ bao nhiêu (độ lớn $|H|$) và bị trễ pha bao nhiêu (góc của $H$).
>
> Tín hiệu đứng yên là kim không quay: $\omega=0$, nên $z=e^{0}=1$. Thay vào, $H(1)=\dfrac{1-1}{1-\alpha}=0$. Đây chính là câu "hiệu hai mẫu của một hằng số bằng 0", chỉ viết bằng ngôn ngữ $z$. Nhưng nếu chỉ có phần hiệu thì ở 100 Hz (tại $f_s$ = 16 kHz, $\omega\approx0{,}039$), $|1-e^{-j\omega}|\approx0{,}039$: giọng nói cũng bị bóp còn khoảng 4%. Vì thế cần thêm cực $\alpha$ để bù lại, như phần tiếp theo sẽ trình bày bằng hình học khoảng cách.
>
> *Tóm lại:* zero đặt tại z = 1 vì z = 1 chính là 0 Hz, và cực đặt ngay sát bên trong để mọi tần số khác gần như đi qua nguyên vẹn.

### 6.2 §4.3 (tr.90), mở đầu polyphase 2/3

> Sự thật phũ trước: từ 24 kHz xuống 16 kHz không thể "giữ 2 mẫu, bỏ 1". Mẫu 24 kHz nằm ở 0; 41,67; 83,33; 125 µs…, còn lưới 16 kHz cần 0; 62,5; 125 µs…. Mẫu ở 62,5 µs chưa từng tồn tại, nên nó phải được tính ra. Cách đúng trên giấy gồm ba bước: chèn một số 0 giữa mỗi hai mẫu để lên 48 kHz (lưới chung, vì 48 là bội chung nhỏ nhất của 24 và 16), lọc thông thấp 8 kHz để nội suy các ô 0 thành giá trị thật, rồi giữ 1 trong 3 mẫu.
>
> Làm thật đúng như vậy thì rất phí. Lấy bộ lọc 6 tap $h=[h_0,\dots,h_5]$. Mỗi mẫu ra ở 48 kHz tốn 6 phép nhân, và cứ 3 mẫu thì vứt 2, nên mỗi mẫu 16 kHz giữ lại "tốn" 18 phép nhân. Hơn nữa một nửa số đó là nhân với các số 0 do chính ta chèn vào. Hãy viết tường minh mẫu ra thứ $m$: $y[m]=\sum_k h[k]\,x_{up}[3m-k]$. Vì $x_{up}$ chỉ khác 0 ở vị trí chẵn, chỉ các tap có $k$ cùng chẵn lẻ với $m$ là đóng góp. Với $m=0$ thì $y[0]=h_0x[0]$ (cộng thêm các mẫu quá khứ qua $h_2,h_4$). Với $m=1$, $3m-k$ chẵn khi $k\in\{1,3,5\}$, nên $y[1]=h_1x[1]+h_3x[0]+h_5x[-1]$. Như vậy chỉ có hai "rổ" hệ số: $E_0=[h_0,h_2,h_4]$ dùng cho mẫu ra chẵn và $E_1=[h_1,h_3,h_5]$ dùng cho mẫu ra lẻ. Mỗi mẫu ra chỉ tốn 3 phép nhân thay vì 18.
>
> Chỉ đến lúc này công thức tổng quát $H(z)=\sum_{r=0}^{L-1}z^{-r}E_r(z^L)$ với $L=2$ mới xuất hiện, như một cách viết gọn hai rổ vừa tìm ra. "Commutator" chỉ là bộ đếm luân phiên 0, 1, 0, 1 chọn rổ nào nạp vào bộ nhân. *Tóm lại:* polyphase 2/3 là chọn đúng nửa số hệ số không gặp số 0 và chỉ tính những mẫu sẽ được giữ.

### 6.3 §9.4 (tr.120–121), câu "Lệch một chu kỳ gắn F0 khung trước vào khung sau" và "Không tồn tại IP ALTDIV_TENT"

> LPM_DIVIDE không trả kết quả ngay. Với LPM_PIPELINE = 8, thương của phép chia bắt đầu ở chu kỳ 0 chỉ xuất hiện ở ngõ ra sau đúng 8 cạnh đồng hồ. Trong 8 chu kỳ đó, ngõ ra vẫn giữ thương của lần chia trước, tức F0 của khung trước. Nếu FSM đọc ở chu kỳ 7, nó nhận đúng con số đó và gắn vào khung hiện tại. Ví dụ khung k−1 có F0 = 200 Hz, khung k có 199,47 Hz: đọc sớm một nhịp sẽ ghi 200 Hz cho khung k. Đường F0 trông vẫn mượt nhưng trễ đều một hop so với twin, nên sai số cent dao động theo thời gian chứ không theo biên độ. Đây là lỗi thời gian, công thức chia vẫn đúng. Vì vậy FSM phải đếm đúng L cạnh đồng hồ, hoặc tốt hơn là đi kèm một tín hiệu valid được trễ qua L thanh ghi song song với IP. Một ghi chú về tên IP: một số ghi chép trên mạng nhắc tới "ALTDIV_TENT", nhưng Quartus không có IP này. Phép chia số nguyên chỉ có LPM_DIVIDE hoặc bộ chia tự viết.

### 6.4 Hộp chi phí Bước 1 (tr.52)

> Bước 1 của Praat không tốn gì trên fabric, vì FPGA không làm nó. Muốn FFT cả một câu nói, ta phải đợi người nói xong và giữ toàn bộ câu trong RAM, mà luồng streaming không thể chờ như vậy. Vai trò "chặn năng lượng gần Nyquist" được giao cho hai chỗ khác: bộ lọc analog trong codec trước ADC, và các bộ lọc FIR khi hạ mẫu ở Chương 4. Chi phí của hai bộ này tính ở Chương 4 (mục tiêu toàn luồng là khoảng 3 DSP), không tính ở đây. Khi muốn so khớp với Praat đầy đủ, twin chạy Bước 1 offline trên Python, ngoài thời gian thực. Nếu bỏ mất cả hai lớp lọc, một tiếng rít 9 kHz sẽ trở thành tone 7 kHz trong dữ liệu 16 kHz. Tone này có chu kỳ chỉ ≈ 2,29 mẫu, nên tạo gợn khắp dải τ = 26–214 của hàm tự tương quan. Khối MAC vẫn tính đúng công thức, nhưng F0 thì sai.

## 7. Danh sách phát hiện theo chương (để giao cho người viết lại)

- **Ch.0:** A3 (tr.43), A6 (tr.46, 48), A15, A17, D2. Feynman 4 viết lại theo #15. Feynman 9 viết lại theo khuôn #16. Bài 0.1b theo #17. Thiếu câu tóm tắt cho từng ô.
- **Ch.1:** A3, A5, A6, A8, A16, B5–B8, bảng 10 tham số (tr.69) và lời giải T3 (tr.71) viết lại thành câu; số ALM median không nhất quán; các Bước 1–9 thiếu Verilog.
- **Ch.2:** cộc lốc mức 4; các cost box; chuỗi FSM dạng mũi tên; I²S RTL chỉ có comment; PLL phải giải thích vì sao không có HDL tương đương (analog VCO), nhưng phần bộ chia SCLK có RTL thì cần twin.
- **Ch.3:** B1 (§3.2, 6 câu hỏi của case #21), A14, B9, D1 ("toy").
- **Ch.4:** A1, A2, A16, B2, B3, B4; thiếu RTL FIR polyphase tự viết khớp FIR Compiler II.
- **Ch.5:** A7 (hình dạng M10K); latency 1/2 viết thành văn.
- **Ch.6:** khá; bài tập dồn một khối; A7 (ROM 640 từ x16).
- **Ch.7:** A4, A6; MAC RTL chỉ là stub; BFP (cần kiểm tra quy ước dịch).
- **Ch.8:** A11, A12, C2; LPM_DIVIDE cần RTL tương đương.
- **Ch.9:** C2, D3, B10; RTL non-restoring thật, khớp LPM_DIVIDE.
- **Ch.10:** A13 (twin và RTL lệch, độ trễ), B11.
- **Ch.11:** khá; danh sách vai trò trạng thái viết thành văn; A6 (tr.133).
- **Ch.12:** khá; các bước 1–5 ở tr.138 viết thành văn.
- **Ch.13:** cộc lốc mức 4; B12; A6 (tr.148).
- **Ch.14:** cộc lốc mức 5; A9, A10, A6; mỗi mục checklist phải thành một đoạn nhân quả.

## 8. Đối chiếu audit của Argon (Gemini), file `gemini/argon_audit_phan_moi_2026-11-10.md`

Từng ý của Argon đã được kiểm lại bằng cách tìm trong text PDF và trong tex, chạy script, và xem ảnh render (pdftoppm). Script: `verify/audit_phan_moi/check_numbers.py`; công thức octave lấy từ `golden/lab_1_3_5.py::scoring_rom_q13`.

| # | Ý của Argon | Kết luận | Bằng chứng / ghi chú |
|---|---|---|---|
| R1 | Hanning N+1 đủ 640 từ ở Ch.1, Ch.6 nhưng Ch.14 ghi "cổ điển N−1, nửa bảng" | **Argon, đã xác minh** (trùng A10) | tr.152–153 |
| R2 | 120 960 / 2,42 ms / RTF 0,242 so với 98 280 / RTF 0,19656 | **Argon, đã xác minh** (trùng A6) | Σ_{τ=26}^{214}(640−τ) = 98 280 (script) |
| R3 | Cổng silence/voicing: Ch.1.10 dùng nhân chéo nguyên (R0·10000 < 9·E_ref; best·100 ≥ 45·R0), Ch.10 dùng biên độ và ra_q14 ≥ 7372 (cần chia) | **Argon, đã xác minh** (mâu thuẫn có thật, tr.62–63 và tr.124–125) | Quyết định thống nhất: dùng phương pháp nhân chéo nguyên của Ch.1.10 cho cả Ch.10, không chia. Phải nói rõ đây là xấp xỉ theo năng lượng (0,03² = 0,0009) của chi phí mềm localPeak/globalPeak (biên độ) trong Praat. Golden `lab_1_3_5.py` cũng dùng 0,0009. (A8 chỉnh theo hướng này.) |
| R4 | median3: Listing 3 ở Ch.1 không có m_reg, Ch.10 có thêm m_reg | **Argon, đã xác minh** (trùng A13) | tr.65–66 so với tr.127–129. Thống nhất thành một module duy nhất `f_out <= med(f_in_gated, d0, d1)`, không có m_reg. Trễ nhóm 1 khung là cố hữu. Twin phải khớp bit với RTL. |
| R5a | Ví dụ DFT tr.51 in thiếu dấu trừ: "[1,0,1,0,1,0,−1,0]" | **Argon, sai** | Ảnh render và text đều in đúng [1,0,−1,0,1,0,−1,0] |
| R5b | Vector đó nằm ở fs/4 (bin 2, 6), không phải Nyquist; Nyquist là [1,−1,…] với X[4] = 8, bị G[4] = 0 triệt | **Argon, đã xác minh** (trùng A5) | Script: \|X\|² = 16 ở bin 2 và 6 |
| R6 | z-domain nhảy bước (Ch.3 tr.81, Ch.4 tr.90); đạo hàm fc chôn trong hộp chi phí tr.85 | **Argon, đã xác minh** (trùng B1, B2) | Đưa fc về §3.2 |
| R7 | Văn điện tín ở các mục 3.4b, 4.3b, 5.3b, 8.4b, 9.4b; "ALTDIV_TENT" lặp lại; meta-prompt rò rỉ ("Giữ nguyên v10 pp.1-38", "Chính sách DIFF") | **Argon, đã xác minh** | ALTDIV_TENT xuất hiện ở tr.114, 116, 121, 152; meta ở tr.152 mục 13–14 ("Giữ nguyên v10…", "Chính sách DIFF") và tr.153 ("Giữ DIFF và v10. Chính sách gói tài liệu…"); "ghi chú DIFF" ở tr.149. **Mục mới D8: xóa toàn bộ chữ meta/prompt nội bộ.** |
| R8 | Thiếu cầu nối đặt DC (z = +1, notch < 10 Hz) và Nyquist (z = −1, FIR 48 tap) trên cùng vòng đơn vị | **Argon, đã xác minh** (bổ sung cho câu hỏi 6 của case #21) | |
| R9 | Fig 7 (tr.40): nhãn mũi tên chồng lên hộp | **Argon, đã xác minh** | Ảnh render: các nhãn "I²S serial", "48 kHz PCM", "16 kHz Q1.15", "x_w[n]", "r_a[τ]"… đè lên viền hộp |
| R10 | Feynman 12: cực 0,995 phải là 1−2⁻⁸ | **Argon, đã xác minh** (trùng A15) | |
| R11 | Chuyển phần đại số parabolic (x = −1, 0, 1 → a, b → 2ax + b = 0) từ Ch.9 lên tr.58 | **Argon, đã xác minh** (thiếu cầu nối) | tr.58 chỉ đưa công thức |
| R12 | RTL i2s_rx (tr.74–75) bị comment một nửa | **Argon, đã xác minh** | chuong_02 dòng 156: `// reg [4:0] bit_cnt; reg [15:0] shreg;` |
| R13 | Mã Gray: thiếu lý do vì sao n^(n>>1) chỉ đổi đúng 1 bit | **Argon, đã xác minh** | tr.76 chỉ đưa ví dụ G(3), G(4) |
| R14 | §3.3: vì sao dịch <<15 vào 32 bit (Q2.30), 15 LSB là "bể dư" để >>>8 không gây deadband | **Argon, đã xác minh** (thiếu lý do) | |
| R15 | §4.3 polyphase: Argon đề nghị giải thích bằng cách nhóm mod 3 | **Argon, sai** với ↑2↓3 | Giữ case #19: E0 = tap chẵn, E1 = tap lẻ, ~N/2 nhân mỗi mẫu ra (script: 3 so với 18). Nhóm mod 3 chỉ được nêu như bước đệm "nếu chỉ ↓3 thuần", có ghi nhãn rõ. |
| R16 | Fig 26 (tr.91): chữ chú thích chồng | **Argon, xác minh một phần** | Chữ trong hình rất nhỏ (~5 pt) và sát nhau nhưng không chồng rõ. Vẫn phải tăng cỡ chữ. |
| R17 | RTL tr.97: rd_ptr chạy tự do; tr.98 nói latch rd_base = n_w khi frame_req nhưng RTL không có | **Argon, đã xác minh** | chuong_05 dòng 140–149 không có rd_base |
| R18 | Fig 30 (tr.104): nhãn vỡ/chồng; window_hanning đọc ROM tổ hợp, có comment tự thừa nhận | **Argon, đã xác minh** | Ảnh render: "w_q[0]", "chốt y_q[0] chỉ từ ck 1" đè lên nét; chuong_06 dòng 219–221 `wire w_q = rom[n]` |
| R19 | mac_autocorr (tr.109) thân trống | **Argon, đã xác minh** | chuong_07 dòng 141–151: chỉ có port và 3 dòng comment |
| R20 | Octave cost gộp ROM 17429 → 17070 nhưng không đưa công thức | **Argon, đã xác minh** | Công thức trong golden: C_q = round(C[τ]·2^{−0,01·log2(600/F0)}·8192); tại τ = 214, F0 = 74,766 Hz, hệ số 0,979390, ra 17070 (script). Phải ghi rõ đây là dạng nhân xấp xỉ phép trừ của Praat (A11). |
| R21 | Mode B: giải thích dấu (D < 0 tại đỉnh; đổi dấu cả N và D để bộ chia thấy mẫu số dương) | **Argon, đã xác minh** (thiếu) | chuong_09 dòng 211–233: có "bắt buộc D < 0" nhưng không nói cách xử lý dấu với LPM_DIVIDE |
| R22 | 11.5c là bản lặp 100% của 11.5 | **Argon, đã xác minh** (logic giống hệt, chỉ khác comment) | diff khối verbatim chỉ khác ở comment. Gộp thành một mục RTL giải thích từng dòng. |
| R23 | Fig 56 (tr.147) chữ tràn | **Argon, sai vị trí** | Fig 56 ổn. Hình bị chồng là **Fig 57**: nhãn "GPE/VDE" đè lên hộp "float twin". |
| R24 | Xóa đoạn "Giữ nguyên v10… Chính sách DIFF…" ở Ch.14 | **Argon, đã xác minh** (= D8) | |

**Cập nhật bảng tổng:** mức A giữ nguyên 17 mục (R3, R4 đã nằm trong A8, A13). Mức B thêm 4 mục (R8, R11, R13, R14). Mức D thêm 4 mục (D8 meta-prompt; hình 7, 30, 57 chồng nhãn; R22 trùng lặp; R16 chữ quá nhỏ). Nhóm RTL dở dang (R12, R17, R18, R19) được tính vào quy tắc 39 (twin+HDL).
