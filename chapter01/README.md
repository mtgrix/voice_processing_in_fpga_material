# Thí nghiệm 1.1: Chuỗi Tiền Xử lý Âm thanh Trực tuyến (Streaming Audio Pipeline)

## 1. Metadata & Mục đích Thí nghiệm
- **Mã thí nghiệm**: `exp_01_streaming_audio_pipeline`
- **Chương liên kết**: Chương 01 — Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực
- **Trạng thái**: 🚧 Đang xây dựng khung sườn (Scaffolded)
- **Mục đích**: Hiện thực hóa và kiểm chứng tính toàn vẹn số học của chuỗi trích xuất đặc trưng âm thanh trực tuyến theo từng khung (sliding ring buffer → STFT → Mel filterbank → Log-Mel).

## 2. Bối cảnh Lý thuyết & Mục tiêu Sư phạm
Trong xử lý âm thanh thời gian thực, dữ liệu không thể nạp theo lô lớn mà phải xử lý trượt liên tục theo từng bước nhảy $H$ mẫu ($10\text{ ms}$). Thí nghiệm minh chứng cơ chế đệm vòng lặp và đối chiếu sai số với phương pháp xử lý mẻ truyền thống.

## 3. Mục tiêu Phần cứng
- Host CPU / Python Simulation (sẽ chuyển đổi thành AXI-Stream Hardware IP Core trên FPGA trong Chương 6).

## 4. Dẫn xuất Toán học & Thuật toán
- Phép biến đổi STFT: độ dài cửa sổ $L=400$ mẫu, bước nhảy $H=160$ mẫu, độ dài FFT $N=512$ (đệm 112 số không).
- Ma trận chuyển đổi Mel $M \times (N/2 + 1) = 80 \times 257$ với $M=80$.
- Hiệu đính ký hiệu: bản trước dùng $N=400$ cho cả cửa sổ lẫn FFT, nên công thức $M \times (N/2+1)$ cho ra 201 cột, trong khi mã thực thi tạo 257 cột. $N$ trong tài liệu này luôn là độ dài FFT.
- Hàm nén: $S[m] = \ln(\max(E[m], 10^{-6}))$.

## 5. Tín hiệu Đầu vào & Đặc tả Dữ liệu
- Sóng âm tổng hợp 1 chiều lấy mẫu tại $16\text{ kHz}$ gồm các thành phần đa âm điều hòa ($440\text{ Hz}, 1200\text{ Hz}, 3200\text{ Hz}$).

## 6. Lệnh Thực thi
```bash
python chapter01/exp_01_streaming_audio_pipeline.py
pytest chapter01/test_exp_01.py
```

## 7. Kết quả Số học Dự kiến & Dung sai
- Sai số tuyệt đối trung bình (MAE) $< 10^{-4}$.
- Tỷ số tín hiệu trên nhiễu lượng tử (SQNR) $> 50\text{ dB}$.

## 8. Phương pháp Đo lường
- So sánh đối chiếu trực tiếp ma trận điểm nổi giữa hàm tính toán streaming và hàm tính toán batch của NumPy.

## 9. Kết quả Thực nghiệm & Bằng chứng
Executed 2026-09-13 on a host (Python 3.12.10, NumPy 2.5.2, Windows 11). Raw output is at
`results/exp01/20260913T020406Z/` — `stdout.log` plus `result.json`, both listed in
`results/SHA256SUMS`. `scripts/capture_result.py` ran the script and wrote the files, so no
number below was transcribed by hand.

| Metric | Expected (§7) | Measured | Reading |
| --- | --- | --- | --- |
| Frames | — | 98 | One second of audio at $L=400$, $H=160$ |
| MAE | $< 10^{-4}$ | $0.0$ | Bound satisfied |
| SQNR | $> 50\text{ dB}$ | 134.48 dB | **Not a noise measurement** |
| Element comparison | — | 0 of 7,840 differ | Streaming and batch arrays are bitwise identical |

The SQNR figure is an artifact of a guard term, not a margin. The script computes
$10\log_{10}\bigl(P_\text{signal}/(P_\text{error}+10^{-12})\bigr)$, and $P_\text{error}$ is
exactly zero because the two arrays are identical, so the reported value equals
$10\log_{10}(28.04136848449707/10^{-12})$ and reproduces to the last printed digit. A run that
differed from its reference would report a different number for that reason alone. The $> 50$ dB
expectation in §7 is therefore not tested by this run, and the honest statement is that the error
was zero rather than small.

What the run does establish is narrower: the ring-buffer path returns the same FP32 values as the
batch path on this input. It says nothing about fixed point (§11, and chapter 6), and nothing
about recognition accuracy, which needs a model and a dataset.

## 10. Đánh đổi Phần cứng - Phần mềm
- Độ trễ không giảm từ $1000\text{ ms}$ xuống $10\text{ ms}$, như bản trước viết. Khung đầu tiên cần $25\text{ ms}$ âm thanh đi qua ($L/f_s = 400/16000$); sau đó một khung mới xuất hiện mỗi $10\text{ ms}$ ($H/f_s = 160/16000$). Con số $1000\text{ ms}$ là thời gian chờ hết một file dài một giây, nên nó phụ thuộc độ dài file chứ không phải một hằng số của phương pháp. Chi phí phải trả là bộ nhớ đệm trạng thái vòng xoay (ring-buffer state).

## 11. Giới hạn & Giả định
- Sử dụng số thực dấu phẩy động 32-bit (FP32). Chương 6 sẽ chuyển đổi sang số dấu phẩy tĩnh (Fixed-Point) để tổng hợp phần cứng.

## 12. Bài học Sư phạm Rút ra
- Hiểu rõ cơ chế cửa sổ trượt và lý do tại sao bộ nhớ đệm trạng thái (stateful buffer) là thành phần cốt lõi trong mọi kiến trúc tăng tốc âm thanh trên phần cứng.

## 13. Nguồn Trích dẫn
- `R01-03`: Gulati et al., *Conformer: Convolution-augmented Transformer for Speech Recognition*, Interspeech 2020.
- `R01-05`: Majumdar et al., *MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network*, Interspeech 2020.
