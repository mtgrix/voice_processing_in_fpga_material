# Chương 1: Từ Sóng Âm đến Suy diễn Biên (From Acoustic Waves to Edge Inference)

> *"Âm thanh là dòng thời gian liên tục; xử lý âm thanh tại biên là cuộc chiến giữa độ trễ vật lý và giới hạn năng lượng silicon."*

---

## 1.1 Trực giác: Sự Khác biệt Cốt lõi giữa Thị giác và Tiếng nói

Trong xử lý dữ liệu biên (edge computing), thị giác máy tính (computer vision) và tiếng nói (voice AI) đặt ra hai mô hình tính toán hoàn toàn trái ngược nhau:

Một khung hình camera đến theo từng nhịp tĩnh (ví dụ: $30\text{ fps} \approx 33.3\text{ ms}$ mỗi ảnh). Khi đến, toàn bộ ma trận điểm ảnh hai chiều kích thước $1920 \times 1080 \times 3$ đã nằm sẵn trong bộ nhớ. Bộ xử lý có thể gom nhiều ảnh thành một lô (batching) để tận dụng tối đa hàng ngàn nhân tính toán song song của bộ xử lý đồ họa (GPU — Graphics Processing Unit).

Ngược lại, sóng âm thanh là **luồng tín hiệu liên tục 1 chiều biến thiên theo thời gian** $x(t)$. Con người nói liên tục với tốc độ lấy mẫu tiêu chuẩn $16\text{ kHz}$ ($16.000$ mẫu biên độ mỗi giây). Người dùng không thể chờ hệ thống gom đủ 1 giây âm thanh rồi mới xử lý; một hệ thống nhận dạng giọng nói hoặc lọc nhiễu tương tác yêu cầu phản hồi gần như tức thì với độ trễ từ đầu đến cuối dưới $100\text{ ms}$, thậm chí dưới $10\text{ ms}$ trong các bài toán phát hiện từ khóa đánh thức (Keyword Spotting — KWS).

Hệ quả là: **Xử lý tiếng nói tại biên luôn vận hành ở chế độ kích thước lô bằng một ($batch=1$) với các khung trượt liên tục.** Đây chính là nguyên nhân sâu xa dẫn đến sự lãng phí tài nguyên to lớn khi chạy các mô hình âm thanh trên kiến trúc GPU truyền thống và mở ra cơ hội đột phá cho phần cứng mạch tích hợp khả trình (FPGA — Field-Programmable Gate Array).

---

> ### 📘 Toán học Tối thiểu cho Chương này
> 
> Để làm chủ trọn vẹn chương này, bạn chỉ cần nắm vững 3 khái niệm toán học:
> 1. **Biến đổi Fourier Rời rạc (DFT — Discrete Fourier Transform)**: Phân rã một chuỗi tín hiệu thời gian thành tổng các sóng hình sin và cosin ở các tần số khác nhau.
> 2. **Phép tích chập 1 chiều (1D Convolution)**: Trượt một bộ lọc trọng số qua chuỗi dữ liệu thời gian để trích xuất đặc trưng cục bộ.
> 3. **Thang đo Logarit (Logarithmic Decibel Scale)**: Nén dải động cực lớn của năng lượng sóng âm phù hợp với đường cong đáp ứng phi tuyến tính của thính giác người.

---

## 1.2 Chuỗi Tiền Xử lý Tín hiệu Âm thanh (Audio Preprocessing Pipeline)

Trước khi một mạng nơ-ron sâu có thể "nghe" và phân loại âm thanh, sóng âm áp suất cơ học từ micrô phải trải qua chuỗi biến đổi toán học để chuyển từ miền thời gian sang biểu diễn phổ tần (Time-Frequency Representation).

```text
Sóng âm thanh x[n] (16 kHz)
   │
   ▼
[ Đệm Cửa sổ Trượt (Sliding Window Buffer) ] ──── Chiều dài khung: N=400 (25 ms), Bước nhảy: H=160 (10 ms)
   │
   ▼
[ Cửa sổ hóa Hamming (Hamming Windowing) ] ──── Giảm thiểu rò rỉ phổ (spectral leakage)
   │
   ▼
[ Biến đổi Fourier Thời gian Ngắn (STFT) ] ──── Thuật toán FFT O(N log N)
   │
   ▼
[ Phổ Công suất (Power Spectrogram) ] ──── |X(k)|^2 = Re^2 + Im^2
   │
   ▼
[ Bộ Ngân hàng Lọc Mel (Mel Filterbank) ] ──── Nhân ma trận M x (N/2 + 1) với M=80 bộ lọc tam giác
   │
   ▼
[ Nén Logarit (Log-Mel Features) ] ──── S[m] = ln(max(E[m], ε)) ── Phù hợp đưa vào Mạng Nơ-ron
```

### Cơ chế Toán học: Biến đổi Fourier Thời gian Ngắn (STFT)

Cho tín hiệu số rời rạc $x[n]$ được trích xuất qua một hàm cửa sổ thời gian $w[n]$ có độ dài $N$ (thường là cửa sổ Hamming hoặc Hanning). Tại khung thời gian thứ $m$ với bước nhảy (hop length) $H$:

$$X[m, k] = \sum_{n=0}^{N-1} x[m \cdot H + n] \cdot w[n] \cdot e^{-j \frac{2\pi}{N} k n}$$

Trong đó:
- $m \in \mathbb{Z}$: Chỉ số khung thời gian (time-frame index).
- $k \in \{0, 1, \dots, N/2\}$: Chỉ số vạch tần số rời rạc (frequency bin).
- $N$: Độ dài cửa sổ lấy mẫu (ví dụ: $N=400$ mẫu tương ứng $25\text{ ms}$ tại $16\text{ kHz}$).
- $H$: Khoảng cách bước nhảy giữa hai khung liên tiếp (ví dụ: $H=160$ mẫu tương ứng $10\text{ ms}$).
- $w[n] = 0.54 - 0.46 \cos\left(\frac{2\pi n}{N-1}\right)$: Trọng số cửa sổ Hamming nhằm làm triệt tiêu gián đoạn biên ở hai đầu khung.

**Hệ quả kỹ thuật:**
- Đầu ra của STFT là một ma trận số phức $X[m, k] \in \mathbb{C}$.
- Năng lượng phổ được tính bằng bình phương độ lớn: $P[m, k] = |X[m, k]|^2 = \text{Re}(X)^2 + \text{Im}(X)^2$.
- Trên phần cứng, tính toán STFT đòi hỏi thực hiện phép Biến đổi Fourier Nhanh (FFT — Fast Fourier Transform) với độ phức tạp $O(N \log_2 N)$ phép tính nhân-cộng phức sau mỗi $H$ mẫu mới.

**Điều KHÔNG suy ra được:**
- STFT không tạo ra thêm thông tin mới; nó chỉ chiếu tín hiệu từ miền thời gian sang miền tần số. Độ phân giải thời gian và tần số bị ràng buộc bởi nguyên lý bất định Heisenberg-Gabor: tăng độ dài $N$ giúp nhìn rõ tần số hơn nhưng làm nhòe mốc thời gian xuất hiện của âm thanh.

---

## 1.3 Ngân hàng Lọc Mel và Trích xuất Đặc trưng Phổ (Mel Filterbank)

Tai người không cảm nhận cao độ âm thanh theo hàm tuyến tính. Chúng ta phân biệt rất nhạy ở các tần số thấp (tiếng nói từ $100\text{ Hz}$ đến $1000\text{ Hz}$), nhưng rất kém nhạy khi tần số vượt trên vài ngàn Hertz. Thang đo Mel (Mel scale) được phát minh để mô phỏng chính xác đặc tính sinh học này:

$$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$

Trong đó $f$ là tần số vật lý tính bằng Hertz ($\text{Hz}$), còn $m$ là tần số theo cảm nhận thính giác tính bằng Mel.

Ta ánh xạ năng lượng $N/2 + 1$ vạch tần số từ STFT vào $M$ dải lọc tam giác chồng lấn (thường chọn $M = 40$ đến $80$ dải lọc):

$$E[m, b] = \sum_{k=0}^{N/2} P[m, k] \cdot H_b[k]$$

Trong đó $H_b[k]$ là đáp ứng xung của bộ lọc tam giác thứ $b \in \{0, \dots, M-1\}$. Sau đó, áp dụng hàm nén logarit:

$$S[m, b] = \ln\left(\max(E[m, b], \epsilon)\right)$$

Ma trận kết quả $S \in \mathbb{R}^{T \times M}$ được gọi là **Log-Mel Spectrogram**, chính là đầu vào chuẩn mực của hầu hết các mô hình nhận dạng giọng nói hiện đại như Conformer, Whisper, hay MatchboxNet.

---

## 1.4 Thí nghiệm Thực thi: Pipeline Tiền Xử lý Âm thanh Trực tuyến

Trong thư mục [`chapter01/`](../chapter01/), chúng ta cung cấp thí nghiệm thực thi `exp_01_streaming_audio_pipeline.py`. Thí nghiệm này chứng minh cơ chế quản lý đệm xoay vòng (ring buffer) mô phỏng dòng âm thanh micrô theo thời gian thực và đo lường sự sai khác số học giữa tính toán theo mẻ (batch) và tính toán theo luồng (streaming).

Bạn có thể chạy thử nghiệm ngay:

```bash
python chapter01/exp_01_streaming_audio_pipeline.py
```

Kết quả đo đạc sẽ khẳng định sai số năng lượng phổ đạt tỷ số tín hiệu trên nhiễu lượng tử (SQNR — Signal-to-Quantization-Noise Ratio) vượt trên $60\text{ dB}$, bảo đảm tính toàn vẹn số học tuyệt đối trước khi truyền dữ liệu vào các lớp nơ-ron tiếp theo.
