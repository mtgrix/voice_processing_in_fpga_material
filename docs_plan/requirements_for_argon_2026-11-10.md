# Yêu cầu tài liệu "Ước lượng F0 theo Praat trên FPGA DE10-Standard" (bản gửi Argon để thống nhất đề cương)

## 1. Mục tiêu của Tú
1. **Đầu vào là file WAV 16 kHz có sẵn**, không dùng micro hay codec.
   - HPS (ARM, Linux) trên DE10-Standard đọc WAV từ thẻ SD.
   - PCM được đẩy sang pipeline FPGA qua cầu HPS–FPGA (mSGDMA, hoặc Avalon-MM vào FIFO, rồi Avalon-ST).
   - FPGA tính F0 từng khung rồi trả về HPS dưới dạng `pitch_f0.bin` (Q12.4).
2. **So sánh với Praat chạy trên laptop**, cùng WAV và cùng tham số `To Pitch (ac)`.
   - Độ chính xác: GPE, VDE, FFE và sai số cent theo từng khung.
   - Thời gian:
     - số chu kỳ FPGA (cycle counter), cho từng khung và cả file;
     - thời gian end-to-end trên HPS, tính cả đọc file và truyền;
     - wall time của Praat trên laptop.
   - Tính RTF = thời gian xử lý ÷ thời lượng audio cho cả ba.
3. **Hiểu từng thành phần của Praat**: bản chất, vì sao Boersma làm vậy (bỏ đi thì hỏng gì), và cách hiện thực trên FPGA.

**Quyết định đã chốt:**
- WAV là 16 kHz, nên luồng chính không resample. Bước 1 chỉ còn lọc mềm mép Nyquist gần 8 kHz bằng FIR: (A) FIR Compiler II và (B) HDL.
- Resample 48 → 16 kHz và 44,1 → 16 kHz là chương TÙY CHỌN.
  - 48 → 16 là tỉ số 1/3: ↓3 trực tiếp, hoặc half-band 48→24 rồi polyphase 2/3 tap chẵn/lẻ.
  - 44,1 → 16 là tỉ số 160/441: dùng polyphase hữu tỉ hoặc Farrow, không coi là 2/3.
- Tự tương quan chỉ dùng MAC (bỏ đường FFT).
- Không có Viterbi: median-3 là bộ làm trơn; Viterbi chỉ được nhắc để giải thích vì sao bỏ.
- DC-blocker là khối tùy chọn.

## 2. Mỗi chương bắt buộc có
- **Feynman và first-principles, 6 điểm:**
  1. mở bằng vấn đề thật hoặc một sự thật phũ;
  2. xây từ sự kiện gốc, không nhảy bước, không có công thức nào trước câu dẫn của nó;
  3. ví dụ đời thường cùng "Ví dụ tính tay" có số kiểm bằng script;
  4. đoán trước chỗ người đọc sẽ vướng;
  5. sau cùng mới ánh xạ sang phần cứng;
  6. kết bằng một câu tóm tắt.
- **Mức kể chuyện của Ch.0 (bản cũ) là sàn tối thiểu.** Kết quả chỉ được xuất hiện sau khi người đọc đã được dẫn tới nó theo thứ tự: vấn đề → vì sao cách ngây thơ hỏng → suy dẫn từng bước có câu nối → ví dụ tính tay → con số.
- **Hai đường hiện thực đặt cạnh nhau cho mọi thành phần:**
  - (A) dùng IP Intel;
  - (B) HDL tự viết, khớp (A) từng bit và từng chu kỳ, kèm giải thích vì sao khớp.
  - Cả hai đều so với twin Python. Thành phần nào không có IP hợp lý (median-3, so sánh voicing) thì nói rõ điều đó và giải thích vì sao chỉ dùng HDL.
- **Với mỗi IP:**
  1. Giải thích từng tham số trong Parameter Editor (ví dụ LPM_MULT: độ rộng, signed, LPM_PIPELINE, DSP hay logic; altsyncram: mode, độ rộng/độ sâu, outdata_reg, read-during-write, init file; LPM_DIVIDE: độ rộng, LPM_PIPELINE, LPM_REMAINDERPOSITIVE; FIR Compiler II: độ rộng hệ số, đối xứng, hệ số nội suy/hạ mẫu, tỉ số clock/sample tức folding). Mỗi tham số nói ý nghĩa và vì sao chọn giá trị đó.
  2. Nêu những gì IP sinh ra: port, latency, báo cáo tài nguyên (DSP/M10K/ALM), độ rộng và thang của ngõ ra.
  3. Nối mỗi tham số ngược về lý thuyết: độ rộng hệ số ↔ suy hao dải chặn, đối xứng ↔ pha tuyến tính và một nửa số bộ nhân, folding ↔ ngân sách 3125 chu kỳ.
- **Với HDL**, chỉ ra cách viết RTL để tạo ra từng đánh đổi đó: tầng thanh ghi nào ứng với LPM_PIPELINE, cách viết phép nhân có dấu để suy ra khối DSP, cách có hành vi Old Data, cách gấp tap qua pre-adder. Cho thấy đổi một lựa chọn RTL thì Fmax, latency và tài nguyên dịch đi thế nào.
- **Cấu trúc "các phương án → đánh đổi → ta chọn gì → vì sao, có số"** cho mọi khối.
  - Ví dụ bộ nhân:
    - Phương án tổ hợp: ra kết quả cùng chu kỳ, đường tới hạn dài, Fmax thấp.
    - Phương án có thanh ghi/pipeline: LPM_PIPELINE = N, Fmax cao hơn, trễ N chu kỳ mà FSM phải tính đến.
    - Ta chọn pipeline. Lý do có số: clock 50 MHz, ngân sách 3125 chu kỳ cho mỗi mẫu nên latency gần như không tốn gì, thanh ghi trong khối DSP là miễn phí, và cách này khớp với cấu hình IP.
  - Áp tương tự cho: kiểu đọc bộ nhớ, bộ chia (tổ hợp / pipeline / lặp), loại FIFO, mã hóa FSM.
- **Cuối mỗi phần** có twin Python và HDL, cả hai giải thích từng dòng, kèm iverilog chạy ≥ 200 vector khớp 100%.

## 3. Bản hiện tại sai ở đâu
- **Cộc lốc, kiểu đổ từ khóa** từ Ch.1 trở đi.
  - tr.81 §3.2: "Đáp ứng tần số gần DC: |H(e^{jω})| tăng gần tuyến tính với ω khi ω nhỏ; hằng thời gian xấp xỉ 1/(1−α) mẫu."
  - tr.92: "RTL thay thế. Khi không gọi IP: systolic MAC + coeff ROM, folding tay nếu N ≤ 32."
  - tr.120: "Lệch một chu kỳ gắn F0 khung trước vào khung sau — lỗi thời gian, không phải lỗi toán."
  - tr.56: "MAC mặc định: 1 DSP, accumulator 48-bit, 120960 chu kỳ/khung @ 50 MHz ⇒ 2,42 ms".
- **Sai hướng:** cả tài liệu giả định micro, WM8731, I²S, PLL/MCLK. Toàn bộ Ch.2 và phần lớn khung của Ch.0, 3, 4, 11, 14 xoay quanh giả định này.
- **Mục con "b/c" gắn thêm vào mà không có câu nối:** 3.3b, 3.4b, 4.1b, 4.3b, 4.4b, 5.1b–5.3b, 8.4b/c, 8.5b, 9.4b/c, 9.5b, 11.3b, 11.4b, 11.5b/c, 12.7b–d, 13.4b–13.7c, 14.2b–14.4d. Riêng 11.5c lặp lại nguyên logic RTL của 11.5.
- **Mâu thuẫn giữa các chương:**
  - Hanning: N+1 đủ 640 từ (Ch.1, Ch.6) nhưng Ch.14 ghi "N−1, nửa bảng".
  - Số MAC: 120 960 so với 98 280.
  - Cổng voicing: nhân chéo nguyên (Ch.1.10) so với phép chia (Ch.10).
  - median-3: Ch.10 có thêm m_reg mà Ch.1 không có.
  - Cực DC-blocker: 0,995 so với 0,99609375.
- **Sai kiến thức:**
  - Polyphase 2/3 chia nhánh mod 3 kiểu "E2 không xuất", và câu "tiết kiệm 66%".
  - "Zero-padding dọn mép Nyquist".
  - "640×16 vừa 1 M10K" (thực tế cần 2 khối).
  - Ch.14 nói quên C[τ] thì thiên về τ lớn (thực ra là τ nhỏ).
- **RTL dở dang:** `mac_autocorr` có thân rỗng; `i2s_rx` bị comment một nửa; `window_hanning` đọc ROM tổ hợp; sliding RAM thiếu chốt `rd_base`.
- **Chữ meta rò rỉ ra trang:** "Giữ nguyên v10 pp.1–38", "Chính sách DIFF", và "ALTDIV_TENT không tồn tại" lặp 4 lần.
- **Thiếu giải thích IP:** không có tham số nào được giải thích, không có báo cáo tài nguyên nào.
- **Đoạn mẫu tốt** (chuẩn cần đạt): "Sự thật phũ trước: từ 24 kHz xuống 16 kHz không thể 'giữ 2 mẫu, bỏ 1'. Mẫu 24 kHz nằm ở 0; 41,67; 83,33; 125 µs…, còn lưới 16 kHz cần 0; 62,5; 125 µs…. Mẫu ở 62,5 µs chưa từng tồn tại, nên nó phải được tính ra…"

## 4. Đề cương nháp (lõi theo thứ tự Sound_to_Pitch)
- **Ch.0.** Mục tiêu, hệ thống WAV → HPS → FPGA → HPS, các chỉ số so sánh.
- **Ch.1.** WAV I/O trên HPS và truyền HPS–FPGA.
  - IP: mSGDMA, FIFO.
  - HDL: Avalon-MM slave + FIFO.
  - Cần bàn: DMA hay PIO, độ sâu FIFO.
- **Ch.2.** Avalon-ST và FSM đỉnh. Chỉ HDL; bàn kiểu mã hóa FSM.
- **Ch.3.** Bước 1, FIR mềm mép Nyquist ở 16 kHz.
  - IP: FIR Compiler II.
  - HDL: FIR gấp tap đối xứng qua pre-adder.
  - Cần bàn: số tap và độ rộng hệ số.
- **Ch.3b (tùy chọn).** Resample về 16 kHz.
  - 48 → 16: ↓3 trực tiếp, hoặc half-band 48→24 rồi polyphase 2/3 tap chẵn/lẻ.
  - 44,1 → 16 (160/441): polyphase hữu tỉ hoặc Farrow.
- **Ch.4.** Bước 2, phân khung và RAM trượt.
  - IP: altsyncram.
  - HDL: RAM suy diễn, Old Data, 2 khối M10K.
- **Ch.5.** Bước 3, trừ trung bình (cộng DC-blocker tùy chọn).
  - IP: LPM_MULT.
  - HDL: bộ tích lũy + nhân hằng 1/L.
- **Ch.6.** Bước 4, ROM Hanning N+1 nhân mẫu.
  - IP: ROM + LPM_MULT.
  - Cần bàn: bộ nhân tổ hợp hay pipeline.
- **Ch.7.** Bước 5, tự tương quan MAC (98 280 phép nhân).
  - IP: DSP ở chế độ nhân–cộng dồn.
  - HDL: FSM MAC 48 bit.
- **Ch.8.** Bước 6, ROM C[τ]. IP là ROM + LPM_MULT; cần bàn: nhân ROM hay chia ở mỗi τ.
- **Ch.9.** Bước 7, đỉnh, parabolic, F0 = fs/τ; giải thích vì sao không dùng sinc/Brent.
  - IP: LPM_DIVIDE.
  - HDL: bộ chia lặp / non-restoring.
- **Ch.10.** Bước 9, octave cost gộp vào ROM. Bàn: dạng nhân hay dạng trừ.
- **Ch.11.** Bước 10, voicing/silence. Không có IP; HDL là bộ so sánh nhân chéo nguyên.
- **Ch.12.** Bước 11, median-3; giải thích vì sao bỏ Viterbi. Không có IP.
- **Ch.13.** Ngõ ra Q12.4 về HPS, file `pitch_f0.bin`.
- **Ch.14.** Kiểm chứng và so sánh với Praat: độ chính xác + thời gian, RTF, cycle counter.
- **Ch.15.** Checklist.
- **Mỗi chương lõi giao:** twin Python, HDL (B), đoạn khởi tạo IP (A), testbench iverilog, bảng so sánh IP và HDL (tài nguyên, latency, độ linh hoạt).

## 5. Quy tắc văn phong (ví dụ trước/sau)
- **Trước:** "Đáp ứng tần số gần DC: |H| tăng gần tuyến tính với ω."
- **Sau:** "Câu hỏi đầu tiên: làm sao hai phép cộng trừ 'biết' đâu là 0 Hz? Đưa vào một kim đồng hồ dài 1, x[n] = e^{jωn}. Mẫu trễ một nhịp là e^{jωn}·e^{−jω}, độ dài vẫn 1, góc lùi ω, nên trễ 1 mẫu chính là nhân z^{−1}… Thay z = 1 vào thì H(1) = 0. *Tóm lại:* zero đặt tại z = 1 vì z = 1 chính là 0 Hz."
- **Cấm:**
  - dòng "nhãn: giá trị" và chuỗi mũi tên thay cho câu văn;
  - gạch đầu dòng cụt;
  - kết quả đưa ra mà không có suy dẫn;
  - đoạn văn chủ yếu là thuật ngữ cộng con số.

## 6. Bẫy cần giữ và câu hỏi mở
**Bẫy cần giữ:**
- Polyphase ↑2↓3 (trong chương resample tùy chọn) dùng tap chẵn/lẻ: khoảng N/2 phép nhân cho mỗi mẫu ra, 3 so với 18, tức tiết kiệm 83%. Không chia nhánh mod 3. Còn 160/441 không phải 2/3.
- Hanning dùng N+1 với đủ 640 từ.
- Số MAC là Σ(640−τ) = 98 280, RTF ≈ 0,197.
- Voicing dùng nhân chéo nguyên `best·100 ≥ 45·R0` và `R0·10000 < 9·E_ref` (đây là xấp xỉ theo năng lượng của tỉ số biên độ trong Praat).
- Octave cost gộp ROM: 17429 → 17070 tại τ = 214.
- 640×16 cần 2 khối M10K.

**Câu hỏi còn mở:**
1. Truyền bằng DMA (mSGDMA) hay PIO?
2. Lấy phiên bản Praat và bộ tham số nào làm chuẩn?
3. Golden đang ghi τ_max = 213 / 187 lag trong khi tài liệu dùng 214 / 189: thống nhất theo bên nào?
