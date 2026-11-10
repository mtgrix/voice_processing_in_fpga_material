# Audit hướng đi: từ "micro/codec thời gian thực" sang "file WAV qua HPS, so với Praat trên laptop" — 2026-11-10

Nguồn: đọc toàn bộ PDF cũ (117 trang, tr. in 40–156) và các chương v2 đã viết lại. Số từ: trước v2 / sau v2 (nếu có). Tỉ lệ dành cho giả định micro là ước lượng khi đọc.

## 1. Những chỗ giả định micro / WM8731 / I²S / PLL-MCLK / thu âm thời gian thực

| Chỗ | Giả định | Khối lượng |
|---|---|---|
| Ch.0 (tr.40–49): Hình 7, §0.1, các ô Feynman 0.4 (PLL, MCLK, I²S, DCFIFO/Gray), Feynman 9–12, Bài 0.1, bảng ngân sách | Sơ đồ khối bắt đầu từ "Audio Codec WM8731 ADC 24-bit @48 kHz", rồi PLL+I²S, DC-blocker, FIR 48→24→16; "thời gian thực" được định nghĩa theo micro | ~25–30% Ch.0 (7.3k → 10.2k từ) |
| Ch.1: Bước 1, §1.13, bài tập | "Bước 1 được thay bằng lọc analog trong codec WM8731 + FIR 2/3", "streaming, không chờ hết câu" | ~5% |
| **Ch.2 PLL/MCLK/I²S/CDC (tr.72–79)** | Toàn bộ: thạch anh → PLL 12,288 MHz, I²S RX, DCFIFO giữa miền 12,288 MHz và 50 MHz | **100%** (4.1k → 10.4k từ, v2 đã merge) |
| Ch.3 DC-blocker | Trôi DC được quy cho micro/codec; khối đặt sau CDC ở 48 kHz | ~20% phần dẫn dắt; bản thân bộ lọc vẫn đúng |
| Ch.4 FIR 48→24→16 | Tần số vào 48 kHz là tần số của codec | Tỉ số phụ thuộc hoàn toàn vào codec; lý thuyết polyphase/half-band vẫn dùng được |
| Ch.5 RAM trượt | Mẫu 16 kHz đến theo thời gian thực | ~15% |
| Ch.11 FSM/Avalon-ST | Nguồn dữ liệu là DCFIFO từ I²S | ~30% |
| Ch.13 | Testbench lấy luồng I²S/DCFIFO; Signal Tap trên codec | ~15% |
| Ch.14 | Các mục checklist về MCLK, khóa PLL, I²S, tần số codec | ~20% |
| STYLE_BRIEF_v2.md | Các mục Ch.2 (PLL, I²S RX, DCFIFO), §4 "24k→16k", vị trí Ch.3 | Nhiều mục |
| audit_phan_moi_2026-11-10.md | A16, danh sách B cho Ch.2, D5 (Hình 7) | Ít |

## 2. Quyết định của Tú (2026-11-10 tối)
- **WAV là 16 kHz.** Luồng chính KHÔNG resample. Bước 1 chỉ còn xử lý mép Nyquist: lọc thông thấp mềm gần 8 kHz bằng FIR, (A) dùng IP FIR Compiler II và (B) HDL tự viết.
- **Chương TÙY CHỌN: resample về 16 kHz.**
  - 48 → 16 kHz là tỉ số 1/3: ↓3 trực tiếp, hoặc half-band 48→24 rồi polyphase 2/3 tap chẵn/lẻ.
  - 44,1 → 16 kHz là tỉ số 160/441: cần polyphase hữu tỉ hoặc Farrow. KHÔNG được coi là 2/3.
- **Tự tương quan chỉ dùng MAC.** Bỏ hẳn đường FFT.
- **Không có Viterbi.** Median-3 là bộ làm trơn; Viterbi chỉ được nhắc để giải thích vì sao bỏ.
- **DC-blocker là khối tùy chọn.** Praat không có khối này; Bước 3 (trừ trung bình cục bộ) đã khử DC trong từng khung.

## 3. Số phận từng chương
- **Bỏ:** Ch.2 PLL/I²S/CDC. Chỉ giữ một phụ lục ngắn "nếu dùng micro". Phần CDC/Gray có thể tái dùng cho miền clock của cầu HPS–FPGA nếu cần.
- **Thu nhỏ hoặc đổi vai:**
  - Ch.3 DC-blocker thành khối tùy chọn.
  - Ch.4 tách đôi: Bước 1 (FIR mép Nyquist ở 16 kHz) vào luồng chính; resample 48/44,1 → 16 thành chương tùy chọn.
  - Bỏ đường FFT trong Ch.7.
  - Bỏ Viterbi trong Ch.1 và Ch.10, chỉ giữ phần giải thích vì sao bỏ.
- **Đã khớp mục tiêu mới:**
  - Ch.12: Q12.4 và `pitch_f0.bin`.
  - Ch.13: kiểm chứng ba tầng float/fixed/RTL, GPE/VDE/FFE, cent. Chỉ cần thêm phần đo thời gian.
  - Ch.10 / §1.10–1.11: voicing nhân chéo nguyên và median-3.

## 4. Hệ thống đề xuất
WAV 16 kHz trên thẻ SD → HPS Linux đọc file và parse header (kiểm tra 16 kHz, mono, 16-bit) → đẩy PCM sang FPGA qua cầu HPS–FPGA (mSGDMA, hoặc PIO Avalon-MM vào FIFO on-chip, rồi Avalon-ST) → pipeline cao độ → F0 Q12.4 cho từng khung → trả về HPS → `pitch_f0.bin`.
Trên laptop: chạy Praat `To Pitch (ac)` cùng tham số, cùng WAV (script Praat hoặc Parselmouth), xuất F0 từng khung.

**So sánh:**
- **Độ chính xác:** GPE, VDE, FFE và sai số cent theo từng khung so với Praat.
- **Thời gian:**
  - số chu kỳ FPGA (cycle counter start/done cho từng khung và cả file);
  - wall time end-to-end trên HPS (`clock_gettime`, gồm đọc file và truyền);
  - wall time của Praat trên laptop.
- RTF cho cả ba, tính bằng thời gian xử lý ÷ thời lượng audio.

## 5. Đề cương chương đề xuất (lõi theo thứ tự Sound_to_Pitch)

| # | Chương | Đường IP (A) | Đường HDL (B) | Lựa chọn cần bàn |
|---|---|---|---|---|
| 0 | Mục tiêu, hệ thống, chỉ số so sánh | – | – | – |
| 1 | WAV trên HPS + truyền HPS–FPGA | mSGDMA, On-Chip FIFO | Avalon-MM slave + FIFO tự viết | DMA hay PIO; độ sâu FIFO; miền clock |
| 2 | Avalon-ST + FSM đỉnh | Không có IP hợp lý | FSM | Mã hóa one-hot hay binary |
| 3 | Bước 1: FIR mép Nyquist ở 16 kHz | FIR Compiler II (single rate, đối xứng) | FIR gấp đôi tap qua pre-adder | Số tap, độ rộng hệ số ↔ suy hao dải chặn; folding ↔ ngân sách 3125 chu kỳ |
| 3b (tùy chọn) | Resample 48→16 (1/3, hoặc 48→24→16) và 44,1→16 (160/441) | FIR Compiler II decimation/fractional | Polyphase (chẵn/lẻ cho 2/3); Farrow hoặc hữu tỉ cho 160/441 | Có cần chương này không |
| 4 | Bước 2: phân khung + RAM trượt | altsyncram 2-PORT | RAM suy diễn, Old Data, 2×M10K | Đọc có/không thanh ghi; Old Data hay Don't Care |
| 5 | Bước 3: trừ trung bình (+ DC-blocker tùy chọn) | LPM_MULT (×1/L) | Bộ tích lũy + nhân hằng | Nhân hằng hay chia |
| 6 | Bước 4: ROM Hanning N+1 × mẫu | ROM 1-PORT + LPM_MULT | ROM suy diễn + nhân có dấu | Bộ nhân tổ hợp hay pipeline (LPM_PIPELINE) |
| 7 | Bước 5: tự tương quan MAC | DSP ở chế độ nhân–cộng dồn | FSM MAC 48-bit | Độ rộng bộ tích lũy; 1 hay 2 DSP |
| 8 | Bước 6: chuẩn hóa C[τ] | ROM + LPM_MULT | ROM suy diễn + nhân | Nhân ROM hay chia ở mỗi τ |
| 9 | Bước 7: đỉnh, parabolic, F0 = fs/τ (vì sao không dùng sinc/Brent) | LPM_DIVIDE | Bộ chia lặp / non-restoring | Chia tổ hợp, pipeline hay lặp |
| 10 | Bước 9: octave cost gộp vào ROM | ROM | – | Dạng nhân hay dạng trừ |
| 11 | Bước 10: voicing/silence | Không có IP hợp lý | So sánh nhân chéo nguyên | Ngưỡng năng lượng hay biên độ |
| 12 | Bước 11: median-3 (vì sao bỏ Viterbi) | Không có IP hợp lý | median3 | – |
| 13 | Ngõ ra Q12.4 → HPS, `pitch_f0.bin` | mSGDMA | Avalon-MM | – |
| 14 | Kiểm chứng + so sánh với Praat (độ chính xác + thời gian, RTF) | – | Testbench + cycle counter | Chọn bộ WAV thử |
| 15 | Checklist | – | – | – |

Mỗi chương lõi đi theo cùng một trình tự:
1. Bản chất của thành phần.
2. Vì sao Boersma làm vậy, bỏ đi thì hỏng gì.
3. Các phương án, đánh đổi, ta chọn gì, vì sao (có số).
4. Đường IP: giải thích từng tham số, những gì IP sinh ra, nối ngược về lý thuyết.
5. Đường HDL khớp IP từng bit và từng chu kỳ, kèm giải thích vì sao khớp.
6. Twin Python + HDL giải thích từng dòng, kèm vector đã chạy iverilog.
7. Bảng so sánh IP và HDL: tài nguyên, latency, độ linh hoạt.

## 6. Câu hỏi còn mở cho Tú
1. Truyền bằng DMA (mSGDMA) hay PIO?
2. Lấy phiên bản Praat và bộ tham số nào làm chuẩn?
3. τ_max = 213 (golden `lab_1_3_5.py`, 187 lag) hay 214 (các chương, 189 lag)?
