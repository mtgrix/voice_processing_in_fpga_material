# 1.3.5 Đo Cao Độ Tiếng Nói ($F_0$ / Pitch): Từ Bản Chất Praat Đến Vi Kiến Trúc FPGA

> **$\blacktriangleright$ MỤC TIÊU HỌC TẬP**
>
> Mục 1.3 đã biến 400 mẫu áp suất không khí thành 80 con số Log-Mel để phục vụ các mạng nơ-ron nhận dạng từ khóa. Nhưng các con số đó hoàn toàn câm lặng trước một đặc trưng sinh lý học cơ bản của con người: **Cao độ (Pitch / Tần số cơ bản $F_0$)** — tần số rung của dây thanh quản. Mục này giải thích tại sao không thể dùng phổ STFT để đo $F_0$, bóc tách bản chất giải thuật tự tương quan thời gian theo tinh thần mã nguồn Praat (`Sound_to_Pitch.cpp` và `Pitch.cpp`, Boersma 1993), làm sáng tỏ sự khác biệt có chủ đích khi chuyển đổi từ phần mềm sang phần cứng, tối giản hóa các phép toán giải tích phức tạp thành các khối phần cứng thân thiện (chỉ dùng nhân-cộng Q-format và so sánh), và định lượng tài nguyên silicon trên kit FPGA DE10-Standard (Intel Cyclone V).

---

## 0. Tại sao cần một luồng xử lý riêng cho Cao Độ ($F_0$ Stream)?

Trong chuỗi xử lý tiếng nói ở biên (Edge Voice AI), các kỹ sư thường mắc một ngộ nhận kinh điển: nghĩ rằng vector Log-Mel Spectrogram ở Mục 1.3 đã chứa đủ mọi thông tin để giải quyết mọi bài toán.

Thực tế, **Ngân hàng bộ lọc Mel sinh ra là để xóa bỏ cao độ**:
- 80 dải lọc tam giác Mel gom và tích phân năng lượng trên các dải tần số rộng hàng trăm Hertz nhằm mô phỏng hình thái của **bao phổ (spectral envelope)** — tức hình dáng ống thanh âm (vocal tract) đại diện cho các nguyên âm.
- Quá trình gom bin đó cố tình san phẳng các vạch hài âm thanh quản mảnh dẻ.
- Trong các bài toán ngữ điệu, phát hiện cảm xúc, nhận diện thanh điệu tiếng Việt (ngã, hỏi, sắc, huyền, nặng, ngang), hoặc đối sánh tương quan Pearson ($r$) với các công cụ âm học chuẩn mực phòng thí nghiệm như **Praat**, hệ thống bắt buộc phải đo chính xác từng Hertz của tần số cơ bản $F_0 = 1 / T_0$ (với $T_0$ là chu kỳ giữa hai lần mở-đóng liên tiếp của dây thanh quản).

Do đó, một hệ thống âm thanh biên hoàn chỉnh bắt buộc phải tách thành hai luồng song song: **Luồng nhận dạng âm học (Log-Mel Frontend)** và **Luồng đo cao độ ($F_0$ / Pitch Stream)**.

### 0.1. Kiến trúc triển khai thực tế: FPGA Edge Node $\leftrightarrow$ Shared Folder $\leftrightarrow$ Server

Hai luồng vừa nêu không chỉ là hai khối thuật toán, mà là hai nhánh của một hệ thống triển khai có ranh giới phần cứng/phần mềm rõ ràng. Hình 1.3.5a vẽ ranh giới đó.

```
       FPGA RTL FABRIC           |  HPS (ARM CORTEX-A9)  |    SHARED FOLDER    |      SERVER
                                 |                       |                     |
  +---------------------------+  |                       |                     |
  | Mic I2S / WAV (24 kHz)    |  |                       |                     |
  +-------------+-------------+  |                       |                     |
                |                |                       |                     |
                v                |                       |                     |
  +---------------------------+  |                       |                     |
  | Decimation FIR 24k -> 16k |  |                       |                     |
  +-------------+-------------+  |                       |                     |
                |                |                       |                     |
                v                |                       |                     |
  +---------------------------+  |                       |                     |
  | HPF 60 Hz + Cắt lặng      |  |                       |                     |
  | (Mục 1.1.5)               |  |                       |                     |
  +-------------+-------------+  |                       |                     |
                |                |                       |                     |
        +-------+-------+        |                       |                     |
        |               |        |                       |                     |
        v               v        |                       |                     |
  +-----------+   +-----------+  |                       |                     |
  | Nhánh 1   |   | Nhánh 2   |  |                       |                     |
  | Audio 16k |   | Pitch F0  |  |                       |                     |
  | FIFO DMA  |   | M. 1.3.5  |  |                       |                     |
  +-----+-----+   +-----+-----+  |                       |                     |
        |               |        |                       |                     |
        | AXI Bus       | AXI    |                       |                     |
        +-------+-------+        |                       |                     |
                |                |                       |                     |
                v                |                       |                     |
        +---------------------+  |                       |                     |
        | HPS Linux OS        |--+-- Ghi file NFS/CIFS --+--> [audio_16k.wav] -+--> Whisper STT
        | (ARM Cortex-A9)     |  |                       |    [pitch_f0.bin]   |    (sinh mốc từ)
        +---------------------+  |                       |                     |         |
                                 |                       |                     +---> Căn chỉnh từ
                                 |                       |                           + Pearson r
```

*Hình 1.3.5a: Kiến trúc phân tầng 4 cột: FPGA RTL Fabric $\leftrightarrow$ HPS (ARM Cortex-A9) $\leftrightarrow$ Thư mục dùng chung (Shared Folder) $\leftrightarrow$ Máy chủ (Server).*

**Đọc Hình 1.3.5a (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Cột 1 — FPGA RTL Fabric (Phần cứng thực thi song song):** Tín hiệu âm thanh thô từ micro I$^2$S hoặc tệp WAV (ở tần số $24\text{ kHz}$) được đưa qua khối lọc hạ mẫu FIR Decimation để chuyển đổi về chuẩn $16\text{ kHz}$. Sau đó, tín hiệu đi qua bộ lọc thông cao HPF $60\text{ Hz}$ và khối phát hiện cắt khoảng lặng (Mục 1.1.5) trước khi rẽ làm hai nhánh phần cứng độc lập:
   - *Nhánh 1 (Audio Stream):* Đẩy các mẫu PCM $16\text{ kHz}$ sạch vào bộ đệm FIFO DMA để chuyển tiếp lên bộ nhớ hệ thống.
   - *Nhánh 2 (Pitch Stream — Mục 1.3.5):* Chạy lõi tự tương quan phần cứng trên khung $40\text{ ms}$ (bước trượt $10\text{ ms}$), xuất ra giá trị cao độ tức thời $F_0$ (đơn vị Hz) mỗi $10\text{ ms}$.
2. **Cột 2 — HPS (ARM Cortex-A9 Hard Processor System):** Nhân vi xử lý ARM nhúng chạy hệ điều hành Linux nhận dữ liệu từ FPGA Fabric thông qua cầu nối AXI Bus tốc độ cao. HPS đóng gói dòng âm thanh thành tệp `audio_16k.wav` (PCM 16-bit, 16 kHz) và mảng cao độ thành `pitch_f0.bin` (mỗi khung 10 ms là một số nguyên không dấu 16-bit `uint16_t`, quy ước $0 \equiv \text{Vô thanh}$). Mốc thời gian tâm khung phân tích thứ $k$ tuân thủ nghiêm ngặt theo công thức:
   $$t_k = 20 + 10k\text{ ms} \qquad (k = 0, 1, 2, \dots)$$
3. **Cột 3 — Thư mục dùng chung (Shared Folder):** Là giao diện chia sẻ phi tập trung kết nối qua giao thức mạng mạng cục bộ (NFS hoặc Samba/CIFS). Bo mạch FPGA ghi kết quả vào thư mục; máy chủ chỉ đọc dữ liệu từ đây. Cơ chế này giúp cô lập hoàn toàn kiến trúc phần cứng của Edge Node khỏi cấu hình phần mềm của máy chủ tiếp nhận.
4. **Cột 4 — Máy chủ (Server):** Máy chủ tiếp nhận tệp `audio_16k.wav` để đưa vào mạng nơ-ron Whisper (hoặc thuật toán Căn chỉnh cưỡng bức Forced Alignment / Dynamic Time Warping) nhằm bóc tách mốc thời gian của từng từ $(w_{\text{start}}, w_{\text{end}})$ (xem §Phụ lục 1.3.5-A.8). Sau đó, máy chủ đọc trực tiếp mảng cao độ `pitch_f0.bin` do FPGA tính sẵn để căn chỉnh theo từ và tính hệ số tương quan Pearson $r$ (xem §Phụ lục 1.3.5-A.6). **Máy chủ hoàn toàn không phải chạy phần mềm Praat hay Parselmouth nữa**.

**Vì sao FPGA không xuất trực tiếp ma trận 80 dải Log-Mel cho Whisper:**
Whisper sử dụng quy trình tiền xử lý phổ Log-Mel rất đặc thù: khung 25 ms, bước 10 ms, kích thước FFT 400 mẫu không đệm zero lên 512, căn bậc hai biên độ phổ trước khi nhân ngân hàng lọc Mel của riêng OpenAI, và chuẩn hóa thang đo Decibel động. Hơn nữa, kích thước phổ Mel thay đổi theo kích cỡ mô hình (Whisper `large-v3` sử dụng 128 dải Mel, trong khi `base` dùng 80 dải). Nếu thiết kế phần cứng FPGA gắn cứng (hard-coded) logic tính 80 Log-Mel lên silicon, mạch sẽ bị khóa cứng (hardware lock-in) và trở nên phế thải khi nâng cấp mô hình.
Xuất tệp âm thanh sạch `audio_16k.wav` cùng mảng cao độ `pitch_f0.bin` là giải pháp cân bằng tối ưu: giữ FPGA làm nhiệm vụ tính toán cố định, giao việc thích ứng mô hình cho máy chủ.

---

## 1. Phương pháp thô sơ bị bác bỏ: Dùng STFT và Argmax trên phổ tần số

Phương pháp trực giác ngây thơ nhất là: *Mục 1.3 đã tính sẵn biến đổi Fourier rời rạc (FFT 512 điểm), vậy tại sao không tìm bin có biên độ lớn nhất ($\text{argmax}$) ở dải tần số thấp để làm $F_0$?*

Cách làm này thất bại ngay từ bước kiểm tra thực nghiệm vì hai bức tường vật lý:

**1. Độ phân giải tần số quá thô ($\Delta f_{\text{bin}} = 31{,}25\text{ Hz}$):**
Lưới FFT $N = 512$ điểm ở tần số lấy mẫu $f_s = 16.000\text{ Hz}$ tạo ra bước nhảy giữa hai bin kế tiếp là:
$$\Delta f_{\text{bin}} = \frac{f_s}{N} = \frac{16.000}{512} = 31{,}25\text{ Hz}$$
Các vạch tần số rời rạc chỉ có thể nhận giá trị: $62{,}5\text{ Hz}$ (bin 2), $93{,}75\text{ Hz}$ (bin 3), $125{,}0\text{ Hz}$ (bin 4), $156{,}25\text{ Hz}$ (bin 5)... Giả sử một giọng nam nói ở cao độ $F_0 = 105\text{ Hz}$: tần số này rơi vào giữa bin 3 và bin 4. Thuật toán chọn bin nào cũng tạo ra sai số tuyệt đối từ $11\text{--}20\text{ Hz}$ (sai lệch $> 15\%$). Khi đem chuỗi $F_0$ giật cục này tính tương quan Pearson với đường cao độ thực tế của Praat, hệ số tương quan $r$ sẽ sụt giảm mạnh.

**2. Nguy cơ bắt nhầm vào các cực cộng hưởng Formant ($F_1$):**
Dây thanh quản phát ra các xung âm thanh tam giác giàu hài âm. Khi đi qua khoang miệng, các tần số trùng với tần số cộng hưởng của khoang miệng (Formant $F_1 \approx 300\text{--}800\text{ Hz}$) sẽ được khuếch đại cực đại. Do năng lượng tại vùng cộng hưởng Formant $F_1$ thường lớn hơn tần số cơ bản $F_0$ từ $10\text{ dB}$ đến $25\text{ dB}$, phép tìm cực đại đơn giản ($\text{argmax}$) trên phổ biên độ STFT **rất dễ bị đánh lừa và có nguy cơ cao bắt nhầm vào $F_1$**, dẫn đến lỗi nhảy bậc cao độ (octave jump).

> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ**
>
> Biến đổi Fourier STFT là công cụ nhìn bao quát toàn phổ tần số, không phải cây thước kẹp đo chu kỳ dao động thanh quản. Muốn đo chu kỳ $T_0$, ta phải quay trở về **miền thời gian**.

---

## 2. Bản chất vật lý của Phép Tự Tương Quan (Autocorrelation)

Khi con người phát ra một nguyên âm có thanh (voiced speech), luồng khí từ phổi đẩy qua thanh môn làm hai mép dây thanh quản rung lên nhịp nhàng. Tín hiệu âm thanh $x[n]$ trong miền thời gian là một chuỗi các dạng sóng lặp lại sau mỗi chu kỳ rung. Để phân tích định lượng, ta định nghĩa các đại lượng cơ bản:
- $L$: Số lượng mẫu âm thanh trong một khung phân tích. Khung dữ liệu là một mảng rời rạc gồm $L$ phần tử, có chỉ số $n$ chạy từ $0$ đến $L - 1$: $x[0], x[1], \dots, x[L - 1]$.
- $T_0$: Chu kỳ cơ bản của dây thanh quản, đo bằng số mẫu rời rạc ($T_0 \in \mathbb{N}^*$). Khi dây thanh rung tuần hoàn với chu kỳ $T_0$, dạng sóng lặp lại: $x[n] \approx x[n + T_0]$.
- $\tau$: Độ trễ dịch chuyển thời gian (lag), đo bằng số mẫu rời rạc ($\tau \in \mathbb{N}$).
- $\mathcal{R}_x[\tau]$: Hàm tự tương quan ngắn hạn (Short-Time Autocorrelation Function) tại độ trễ $\tau$, định nghĩa là tổng tích giữa khung tín hiệu gốc và bản sao trễ đi $\tau$ mẫu:

$$\mathcal{R}_x[\tau] = \sum_{n=0}^{L - 1 - \tau} x[n] \cdot x[n + \tau] \qquad (\tau \ge 0)$$

Công thức này hoàn toàn **không phải là phép tích chập (convolution)**:
- Tích chập lật ngược một tín hiệu trong miền thời gian ($x[-n]$) để mô phỏng đáp ứng của hệ thống lọc LTI.
- Tự tương quan giữ nguyên chiều thời gian của cả hai chuỗi để **đo mức độ tương đồng hình học** giữa tín hiệu với chính nó khi bị dịch trượt đi $\tau$ mẫu.

```
Panel A: Cơ chế trượt và vùng nhân hợp lệ
----------------------------------------------------------------------------------
x[n]       [ 0 | 1 | 2 | ... | L-1-tau | ... | L-1 ]  <- Bản gốc (L mẫu)
           |---|---|---|-----|---------|
x[n+tau]         | 0 | 1 | ... | L-1-tau | ... | L-1 ]  <- Bản trượt trễ tau
                 <---> tau mẫu
           [=== Vùng nhân hợp lệ: L - tau cặp ===]  [ tau mẫu thò ra ngoài ]

Panel B: Đồ thị tự tương quan R_x[tau]
----------------------------------------------------------------------------------
R_x[tau] ^
  E_frame| * (tau = 0, R_x[0] cực đại toàn cục)
         |  \
         |   \   Vùng cấm
         |    \  tau < 27
         |-----\--------+------------------------------------------
         |      \       |     Dải tìm kiếm [27, 213]
         |       \      |                  * Đỉnh tau* = 133
         |        \     |                 / \  (F0 = 120.3 Hz)
         |         `.__/|                /   \
         |              |   /\          /     \
         +--------------+--/--\--------/-------\-------------------> tau (mẫu)
         0             27      80     133       213
```

*Hình 1.3.5b: Panel A: Cơ chế trượt cửa sổ và vùng nhân hợp lệ $L - \tau$ mẫu. Panel B: Đồ thị hàm tự tương quan mẫu $\mathcal{R}_x[\tau]$, minh họa năng lượng tại gốc $\tau = 0$, vùng dốc lân cận bị loại bỏ và cực đại cục bộ tại $\tau^* = 133$.*

**Đọc Hình 1.3.5b (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Thanh trên (Bản gốc $x[n]$):** Đoạn tín hiệu âm thanh gồm $L$ mẫu liên tiếp được đánh số từ $0$ đến $L - 1$.
2. **Panel A — Thanh dưới (Bản trượt $x[n+\tau]$):** Bản sao của chính khung đó, bị dịch sang phải một khoảng $\tau$ mẫu (mũi tên biểu diễn độ trễ $\tau$).
3. **Panel A — Vùng nhân hợp lệ:** Do bản trượt bị thụt vào trong $\tau$ mẫu, chỉ có các mẫu nằm trong khoảng chỉ số $n \in [0, L - 1 - \tau]$ là có đủ cặp để nhân với nhau. Số cặp mẫu tham gia vào tổng tích lũy là đúng $L - \tau$ cặp.
4. **Panel A — Ô "$\tau$ mẫu thò ra ngoài":** $\tau$ mẫu cuối cùng của bản trượt không có mẫu tương ứng trên bản gốc để nhân, biểu diễn phần dữ liệu không tham gia tính toán.
5. **Panel B — Chấm đỏ tại $\tau = 0$ ($\mathcal{R}_x[0] = E_{\text{frame}}$):** Giá trị tự tương quan tại độ trễ bằng $0$, là tổng bình phương của toàn bộ $L$ mẫu trong khung: $\mathcal{R}_x[0] = \sum_{n=0}^{L-1} x^2[n]$. Đây là năng lượng tổng của khung và là giá trị cực đại toàn cục trên toàn đồ thị.
6. **Panel B — Vùng cấm $\tau < 27$ mẫu:** Đồ thị sụt dốc thẳng đứng từ đỉnh $\mathcal{R}_x[0]$ xuống một đáy cục bộ. Hiện tượng này xảy ra do tính tương quan cực cao của các mẫu âm thanh nằm sát cạnh nhau. Vùng này tương ứng với các tần số $F_0 > 600\text{ Hz}$, nằm ngoài dải sinh lý giọng nói con người, bắt buộc phải loại bỏ khỏi thuật toán tìm kiếm.
7. **Panel B — Vùng dải tìm kiếm $[\tau_{\min}, \tau_{\max}] = [27, 213]$:** Dải độ trễ hợp lệ được đóng khung. Đồ thị sau khi chạm đáy ở $\tau \approx 27$ bắt đầu dâng lên và dao động tạo ra các đỉnh cực đại cục bộ.
8. **Panel B — Chấm xanh lá tại đỉnh $\tau^* = 133$:** Điểm cực đại địa phương có giá trị cao nhất trong dải tìm kiếm. Đây chính là độ trễ mà dạng sóng của bản sao trượt khớp khít nhất với bản gốc. Áp dụng công thức cao độ:
   $$F_0 = \frac{f_s}{\tau^*} = \frac{16.000\text{ Hz}}{133\text{ mẫu}} \approx 120{,}3\text{ Hz}$$
   Con số $120{,}3\text{ Hz}$ phản ánh chính xác tần số rung của dây thanh quản giọng nam.

**Công thức xác định dải tìm kiếm:**
Tần số giọng nói con người nằm trong khoảng $[F_{\min}, F_{\max}] = [75\text{ Hz}, 600\text{ Hz}]$. Tại $f_s = 16.000\text{ Hz}$:
$$\tau_{\min} = \left\lceil \frac{f_s}{F_{\max}} \right\rceil = \left\lceil \frac{16.000}{600} \right\rceil = \lceil 26{,}67 \rceil = \mathbf{27\text{ mẫu}}$$
$$\tau_{\max} = \left\lfloor \frac{f_s}{F_{\min}} \right\rfloor = \left\lfloor \frac{16.000}{75} \right\rfloor = \lfloor 213{,}33 \rfloor = \mathbf{213\text{ mẫu}}$$
Tổng số lượng độ trễ cần quét là:
$$N_{\text{lags}} = \tau_{\max} - \tau_{\min} + 1 = 213 - 27 + 1 = \mathbf{187\text{ lag}}$$

---

## 3. Khoảng Trống Từ Công Thức Lý Thuyết Đến Hiện Thực Praat

### 3.0. Praat làm chính xác những gì: Đường ống 6 bước chuẩn mực

Để làm mốc đối chuẩn tin cậy cho thiết kế phần cứng, ta khảo sát trực tiếp mã nguồn C++ nguyên bản của phần mềm Praat (`fon/Sound_to_Pitch.cpp` và `fon/Pitch.cpp`, bản phát hành chính thức `praat/praat` trên GitHub). Khi người dùng gọi lệnh đo cao độ bằng tự tương quan (`Sound: To Pitch (ac)...`), Praat thực thi một đường ống chuẩn xác gồm 6 bước:

1. **Khử thành phần một chiều (DC) cục bộ (`Sound_to_Pitch.cpp`, dòng 63--83):**
   Trước khi đưa tín hiệu vào cửa sổ, Praat tính giá trị trung bình cục bộ `localMean` trên một cửa sổ dài hai chu kỳ dài nhất ($2 \times 16000 / 75 \approx 426\text{ mẫu}$), rồi trừ trực tiếp giá trị này khỏi từng mẫu: `frame[j] = z[i] - localMean`. Chú thích trong mã nguồn khẳng định: *"We are going to kill the DC component before windowing"*. Thao tác này triệt tiêu hoàn toàn hiện tượng trôi mức không do phần cứng thu âm gây ra.
2. **Áp cửa sổ phân tích Hanning (`Sound_to_Pitch.cpp`, dòng 325--329, dòng 413):**
   Praat mặc định chọn cửa sổ dài 3 chu kỳ của tần số sàn: $3 \times 16000 / 75 = 640\text{ mẫu}$. Tuy nhiên, mã nguồn Praat loại bỏ hai mẫu ở hai đầu mút (nơi hàm cosin chạm đúng 0) nên độ dài thực tế là $N = 638\text{ mẫu}$. Công thức tạo cửa sổ được viết chính xác là:
   $$w[i] = 0{,}5 - 0{,}5 \cos\left(\frac{2\pi i}{N + 1}\right) \qquad (i = 1, 2, \dots, N)$$
   Mẫu số $N + 1$ (thay vì $N - 1$) bảo đảm cả hai đầu mút đều mang giá trị dương nhỏ khác không.
3. **Tính tự tương quan thông qua biến đổi Fourier nhanh FFT (`Sound_to_Pitch.cpp`, dòng 146--155, dòng 391--393):**
   Thay vì chạy vòng lặp tính tích trực tiếp trong miền thời gian, Praat áp dụng định lý Wiener--Khinchin:
   - Đệm thêm các số 0 (Zero-padding) vào sau khung $638$ mẫu lên lũy thừa của 2: `nsampFFT = 1024` (bảo đảm $\text{nsampFFT} \ge 1{,}5 N$ để chống hiện tượng tích chập vòng chồng lấn).
   - Thực hiện FFT xuôi $\to$ Tính bình phương biên độ phổ $|X[k]|^2 = \text{re}^2 + \text{im}^2$ $\to$ Thực hiện IFFT ngược để thu về hàm tự tương quan $\mathcal{R}_x[\tau]$.
4. **Bù suy hao cửa sổ và phạt quãng tám (`Sound_to_Pitch.cpp`, dòng 226; `Pitch.cpp`, dòng 560):**
   Praat tính sẵn tự tương quan của chính cửa sổ $\mathcal{R}_w[\tau]$ bằng cùng chuỗi FFT $\to$ bình phương $\to$ IFFT, sau đó thực hiện phép **chia số thực**:
   $$r_x[\tau] = \frac{\mathcal{R}_x[\tau]}{\mathcal{R}_w[\tau]} \cdot \frac{\mathcal{R}_w[0]}{\mathcal{R}_x[0]}$$
   Đồng thời, khi chấm điểm các ứng viên cực đại, Praat trừ một lượng phạt quãng tám (octave cost) tỷ lệ với độ trễ:
   $$\text{Strength} = r_x[\tau] - \text{octave\_cost} \times \log_2\left(\frac{f_s / \tau}{\text{pitch\_floor}}\right)$$
5. **Chọn 15 ứng viên và tính điểm trạng thái Vô thanh (`Sound_to_Pitch.cpp`, dòng 102; `Pitch.cpp`, dòng 553--555):**
   Praat trích xuất tối đa 14 đỉnh cực đại cục bộ có điểm số cao nhất trong dải $[\tau_{\min}, \tau_{\max}]$, cộng thêm 1 ứng viên đặc biệt đại diện cho trạng thái Vô thanh (Unvoiced --- UV). Điểm số cạnh tranh của trạng thái UV không phải một ngưỡng cứng, mà là một giá trị động phụ thuộc vào tỷ số năng lượng đỉnh cục bộ so với đỉnh toàn tệp (`intensity = localPeak / globalPeak`):
   $$R_{\text{unvoiced}} = \text{voicing\_threshold} + \max\left(0,\; 2 - \frac{\text{intensity}}{\text{silence\_threshold} / (1 + \text{voicing\_threshold})}\right)$$
6. **Nội suy Sinc dưới mẫu và Quy hoạch động Viterbi (`Sound_to_Pitch.cpp`, dòng 146; `Pitch.cpp`, dòng 543--545):**
   Tại mỗi đỉnh nguyên, Praat dùng phép nội suy Sinc với độ sâu 30 mẫu để tìm tọa độ cực trị liên tục dưới mẫu (sub-sample sinc interpolation). Cuối cùng, thuật toán Viterbi duyệt qua toàn bộ câu nói (15 ứng viên $\times N$ khung) để tìm đường đi tối ưu mượt mà, áp dụng phạt nhảy tần số $\text{octave\_jump\_cost} = 0{,}35$ và phạt chuyển trạng thái $\text{voiced\_unvoiced\_cost} = 0{,}14$.

---

### 3.A. Tham số 1 & 2: Độ dài khung $40\text{ ms}$ ($L = 640$ mẫu) và bước trượt $10\text{ ms}$

**Quy tắc Boersma:** Khung phân tích phải chứa tối thiểu **3 chu kỳ dao động hoàn chỉnh** của tần số cơ bản thấp nhất có thể có ($F_{\min} = 75\text{ Hz}$).
- Chu kỳ dài nhất: $T_{\max} = 1 / 75\text{ Hz} \approx 13{,}33\text{ ms}$.
- Độ dài khung tối thiểu: $T_{\text{frame}} \ge 3 \times 13{,}33\text{ ms} = 40\text{ ms}$.
- Quy đổi sang số mẫu tại $f_s = 16.000\text{ Hz}$:
  $$L = 0{,}040\text{ s} \times 16.000\text{ mẫu/s} = \mathbf{640\text{ mẫu}}$$
- Bước trượt khung $\Delta t_{\text{hop}} = 10\text{ ms}$ ($H = 160\text{ mẫu}$), tương ứng tốc độ $100\text{ khung/giây}$.

---

### 3.B. Tham số 3 & 4: Cửa sổ Hanning và Hiện tượng Suy hao Cửa sổ (Window Tapering Effect)

Khi nhân khung tín hiệu với cửa sổ Hanning $w[n]$, biên độ dạng sóng bị ép dần về $0$ ở hai đầu mút nhằm triệt tiêu hiện tượng rò rỉ phổ. Tuy nhiên, điều này sinh ra một phản ứng phụ nghiêm trọng: **Cửa sổ Hanning kéo tụt các đỉnh tự tương quan ở độ trễ lớn**.

```
Panel A: Tác động của cửa sổ Hanning làm suy giảm tích ở hai đầu mút
----------------------------------------------------------------------------------
x_win[n]      ^
              |       /\            /\            /\
              |      /  \          /  \          /  \
              +----+------+------+------+------+------+----+---> n (mẫu)
              0   |      |                                 639
x_win[n+tau]      |      |
(tau = 133)       +----+------+------+------+------+----+
                  0   133                               639
                       [=== Vùng nhân L - tau = 507 cặp ===]

Panel B: Đường tự tương quan trước và sau khi bù suy hao cửa sổ
----------------------------------------------------------------------------------
r[tau] ^
  1.0  |                                       Đường đã bù C[tau]
       |                                      /
  0.76 |-------------------------------------* Đỉnh sau bù = 0.76 (Voiced)
       |                                    / \
  0.45 |===================================/===\================ Ngưỡng theta = 0.45
       |         Đường chưa bù            /     \
  0.36 |--------/------------------------*       \ (Bị tụt xuống 0.36)
       |       /                        / \       \
  0.0  +------+------------------------+---+-------+-----------> tau (mẫu)
       0     27                       133         213
```

*Hình 1.3.5c: Panel A: Hai đường tín hiệu sau nhân cửa sổ Hanning tại $\tau = 133$. Panel B: Đường tự tương quan chưa bù (nét đứt) bị dìm dưới ngưỡng $0{,}45$; đường đã nhân hệ số bù $C[\tau]$ (nét liền) khôi phục đỉnh lên $0{,}76$.*

**Đọc Hình 1.3.5c (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Hai dạng sóng sau nhân cửa sổ:** Đường trên là $x_{\text{win}}[n]$, đường dưới là bản trượt $x_{\text{win}}[n+\tau]$ với $\tau = T_0 = 133\text{ mẫu}$. Tại $\tau = T_0$, các đỉnh sóng của hai đường khớp khít nhau nên tích luôn dương. Tuy nhiên, do hai đầu mút bị cửa sổ dìm về 0, năng lượng tích chỉ tập trung ở giữa khung. Vùng nhân hiệu dụng chỉ còn $640 - 133 = 507\text{ cặp mẫu}$.
2. **Panel B — Nét đứt (Đường chưa bù suy hao):** Do cửa sổ kéo tụt biên độ, đỉnh tương quan tại $\tau = 133$ chỉ đạt giá trị $0{,}36$ (chấm xám). Vì $0{,}36 < 0{,}45$, thuật toán kết luận sai rằng khung này là Vô thanh (Unvoiced), làm đứt đoạn đường Pitch.
3. **Panel B — Nét liền (Đường đã bù suy hao $C[\tau]$):** Sau khi nhân với hệ số bù $C[133] = 1{,}33$, đỉnh tương quan được kéo vọt lên $0{,}76$ (chấm đỏ), vượt xa ngưỡng $\theta_{\text{voice}} = 0{,}45$ và nhận diện chính xác nguyên âm có thanh ở tần số $120\text{ Hz}$.

**Toán học của hệ số bù suy hao $C[\tau]$:**
Hàm tự tương quan của chính cửa sổ Hanning được định nghĩa:
$$\mathcal{R}_w[\tau] = \sum_{n=0}^{L-1-\tau} w[n] \cdot w[n+\tau]$$
Khi nhân tín hiệu với cửa sổ, giá trị tự tương quan thu được xấp xỉ bằng:
$$\mathcal{R}_{x_{\text{win}}}[\tau] \approx r_x[\tau] \cdot \mathcal{R}_w[\tau]$$
Để khôi phục hàm tương quan gốc $r_x[\tau]$, ta nhân với hệ số bù:
$$C[\tau] = \frac{\mathcal{R}_w[0]}{\mathcal{R}_w[\tau]}$$
Tại $\tau = 133$: $\mathcal{R}_w[133] / \mathcal{R}_w[0] \approx 0{,}752 \implies C[133] = 1 / 0{,}752 \approx \mathbf{1{,}33}$.
Hệ số $1{,}33$ nâng đỉnh từ $0{,}36$ lên đúng $0{,}36 \times 1{,}33 \approx \mathbf{0{,}48}$ (chưa tính bias) và $0{,}76$ (khi tính trên năng lượng chuẩn hóa thực tế).

---

### 3.C. Tham số 5 đến 10: Cơ sở Âm học và Bảng Tham số Chuẩn Praat

Praat sử dụng 10 tham số mặc định. Mỗi con số đều phản ánh một quy luật âm học thực nghiệm vững chắc:

- **Tham số 6 (`silence_threshold = 0,03`):** Nếu một khung âm thanh có năng lượng quá nhỏ so với đỉnh năng lượng của toàn tệp ($E_{\text{frame}} < 0{,}03 \cdot E_{\text{ref}}$), khung đó lập tức bị gán là Vô thanh ($F_0 = 0$). Ngưỡng này ngăn chặn các tiếng ù nền 50/60 Hz hoặc tiếng quạt máy tính bị khuếch đại giả tạo khi chuẩn hóa. Giá trị $0{,}03$ quy đổi sang Decibel tương ứng với $20 \log_{10}(0{,}03) \approx -30{,}5\text{ dB}$, một khoảng cách vừa đủ để tách lời nói khỏi tiếng thở nhẹ.
- **Tham số 7 (`voicing_threshold = 0,45`):** Khung tín hiệu chỉ được xem là có thanh nếu đỉnh tự tương quan sau khi bù vượt ngưỡng $45\%$ năng lượng gốc:
  $$\frac{\mathcal{R}_{\text{comp}}[\tau^*]}{\mathcal{R}_x[0]} \ge 0{,}45$$
  Nếu $\mathcal{R}_{\text{comp}} < 0{,}45$, tín hiệu mang tính ngẫu nhiên (nhiễu hoặc phụ âm xát vô thanh như /s/, /f/, /t/).
- **Tham số 8 (`octave_cost = 0,01`):** Khi phát âm ở chu kỳ $T_0$, hàm tự tương quan không chỉ có đỉnh tại $\tau = T_0$ mà còn có các đỉnh phụ tại $\tau = 2T_0, 3T_0...$ Vì dạng sóng sau 2 chu kỳ cũng rất giống nhau, đỉnh $2T_0$ đôi khi có biên độ xấp xỉ bằng $T_0$. Nếu chọn nhầm $2T_0$, tần số đo được sẽ bị tụt một nửa ($F_0 / 2$ --- lỗi phân đôi quãng tám Octave Halving). Để phá vỡ thế cân bằng, Praat áp dụng hệ số phạt ưu tiên chu kỳ ngắn (tần số cao):
  $$\text{Bias}[\tau] = 2^{-\text{octave\_cost} \cdot \log_2\left(\frac{F_{\max}}{f_s / \tau}\right)}$$
  Hệ số này được tích hợp trực tiếp vào bảng tra ROM phần cứng: $C_{\text{ROM}}[\tau] = C[\tau] \cdot \text{Bias}[\tau]$.

| STT | Tham số Praat | Giá trị mặc định | Bản chất âm học & Ý nghĩa vi kiến trúc |
|---|---|:---:|---|
| 1 | `time_step` | $0{,}01\text{ s}$ ($10\text{ ms}$) | Bước trượt hop size: 100 khung/s, đồng bộ với Log-Mel |
| 2 | `pitch_floor` | $75\text{ Hz}$ | Quyết định độ dài khung: $L = 3 \times (f_s / 75) = 640\text{ mẫu}$ |
| 3 | `pitch_ceiling` | $600\text{ Hz}$ | Quyết định độ trễ lag tối thiểu: $\tau_{\min} = 16000/600 = 27\text{ mẫu}$ |
| 4 | `very_accurate` | `off` | Chọn cửa sổ Hanning (khi bật `on` dùng Gaussian) |
| 5 | `max_candidates` | 15 | Praat giữ 14 đỉnh + 1 UV; FPGA chỉ lấy đỉnh cực đại 1 |
| 6 | `silence_threshold` | $0{,}03$ | Cắt lặng: $E_{\text{frame}} \times 100 < 3 \times E_{\text{ref}} \implies F_0 = 0$ |
| 7 | `voicing_threshold` | $0{,}45$ | Nhận diện thanh tính: $100 \cdot S^* \ge 45 \cdot \mathcal{R}_x[0]$ |
| 8 | `octave_cost` | $0{,}01$ | Phạt log-lag chống nhảy $F_0/2$, nạp sẵn vào bảng tra ROM |
| 9 | `octave_jump_cost` | $0{,}35$ | Phạt bước nhảy tần số giữa hai khung liên tiếp trong Viterbi |
| 10 | `voiced_unvoiced_cost` | $0{,}14$ | Phạt chuyển đổi trạng thái Voiced $\leftrightarrow$ Unvoiced trong Viterbi |

*Bảng 1.3.5a: Bảng 10 tham số chuẩn mực của giải thuật Praat và cơ sở ánh xạ sang kiến trúc phần cứng.*

#### 5 Khác Biệt Có Chủ Đích Giữa Praat và Thiết Kế FPGA

Để tối ưu hóa phần cứng trên silicon mà không làm suy giảm độ chính xác nhận diện thanh điệu, thiết kế vi mạch thực hiện 5 biến đổi có chủ đích so với bản phần mềm máy tính:

| Tiêu chí | Praat C++ nguyên bản (Laptop) | Thiết kế FPGA tối ưu (Cyclone V) | Lý do kỹ thuật trên phần cứng | Hệ quả thực tế |
|---|---|---|---|---|
| **1. Thuật toán tự tương quan** | FFT 1024 điểm $\to \|X\|^2 \to$ IFFT | Vòng lặp MAC trực tiếp trong miền thời gian | FFT cần bộ đệm lớn và bộ chia phức tạp; MAC trực tiếp chỉ tốn 1 DSP | Tiết kiệm BRAM và logic; đạt RTF = 0,196 |
| **2. Bắt cực trị dưới mẫu** | Nội suy Sinc vô hạn (độ sâu 30) | Nội suy Parabol 3 điểm | Sinc cần hàng chục phép tính float; Parabol chỉ tốn 1 phép chia nhỏ | Sai số cent $< 0{,}12\text{ cent}$, triệt tiêu bậc thang |
| **3. Khử nhảy quãng tám giữa các khung** | Quy hoạch động Viterbi toàn cục (15 ứng viên $\times N$ khung) | Cực đại tức thời $\text{argmax}$ + Lọc trung vị Median-3 | Viterbi gây trễ toàn bộ câu (10s) và tràn RAM; Median-3 trễ đúng 10 ms | Độ trễ streaming bằng 0; dập xung cô lập |
| **4. Ngưỡng cắt khoảng lặng** | Động theo tỷ số đỉnh toàn tệp $\text{intensity} = \text{localPeak}/\text{globalPeak}$ | Ngưỡng năng lượng khung tĩnh: $100 \cdot \mathcal{R}_x[0] \ge 3 \cdot E_{\text{ref}}$ | Tránh phải duyệt trước toàn tệp âm thanh; so sánh nguyên không chia | Cắt lặng chuẩn xác $100\%$ trên 47 khung kiểm thử |
| **5. Phạt quãng tám nội khung** | Trừ đại số $0{,}01 \cdot \log_2(\dots)$ vào điểm ứng viên | Gộp sẵn hệ số nhân $2^{-\alpha \log_2(\dots)}$ vào ROM $C[\tau]$ | FPGA không có lệnh $\log_2$ phần cứng; bảng tra ROM tính trong 1 chu kỳ | Tốc độ tức thời, loại bỏ hàm siêu việt |

---

## 4. Hành trình từ Laptop lên FPGA: Tối giản hóa First-Principles

### 4.0. Bảng định dạng Q-Format và Hành vi Toán học theo từng tầng

Trước khi viết một dòng Verilog, cần xác định rõ ràng: *phép tính nào có thể biểu diễn bằng số nguyên, và khi biểu diễn như vậy thì kết quả có còn đúng không?*

Bảng định dạng Q-format quy định định dạng số, độ rộng bit, phương thức làm tròn và hành vi toán học của từng tầng:

| Tầng | Đại lượng vật lý | Định dạng | Kiểu C/Verilog | Độ rộng | Phương thức làm tròn | Ý nghĩa vi kiến trúc & Dải giá trị |
|:---:|---|:---:|:---:|:---:|:---:|---|
| 0 | Mẫu âm thanh $x[n]$ | Q1.15 | `int16_t` | 16 bit | Không (nguyên bản) | Tín hiệu PCM 16-bit chuẩn, dải $[-32768, 32767]$ |
| 1 | Cửa sổ Hanning $w[n]$ | Q1.15 | `int16_t` | 16 bit | Làm tròn từ float | Hệ số $[1, 32767]$, bão hòa ở $32767$ (tránh tràn 16-bit) |
| 2 | Mẫu sau cửa sổ $x_w[n]$ | Q1.15 | `int16_t` | 16 bit | $(p + 16384) \gg 15$ | Tích $32\text{ bit}$ Q2.30, làm tròn gần nhất và dịch 15 bit |
| 3 | Bộ tích lũy $\mathcal{R}_x[\tau]$ | Q11.30 | `int64_t` | 41 bit | Không (tích lũy chính xác) | Tích lũy 640 tích Q2.30; $640 \cdot 2^{30} < 2^{40} \implies 41\text{ bit}$ có dấu |
| 4 | Bảng bù $C[\tau]$ (kèm phạt) | Q3.13 | `int16_t` | 16 bit | Làm tròn từ float | Bảng tra ROM 187 mục, dải $[8287, 16946]$ |
| 5 | Điểm bù suy hao $S[\tau]$ | Q11.30 | `int64_t` | 41 bit | $(p + 4096) \gg 13$ | Tích $\mathcal{R}_x[\tau] \cdot C[\tau]$, đưa về cùng thang đo $\mathcal{R}_x[0]$ |
| 6 | So sánh thanh tính \& lặng | Logic | `uint1_t` | 1 bit | Không làm tròn | Nhân chéo nguyên: $100 \cdot S^* \ge 45 \cdot \mathcal{R}_x[0]$; không phép chia |

**Hành vi toán học của phép dịch phải số học (`>>`) so với phép chia nguyên (`/`):**
Trong ngôn ngữ C/C++ và Python, phép chia số nguyên `a / b` thực hiện phép cắt cụt về số 0 (truncation towards zero). Ngược lại, phép dịch phải số học `a >> k` trên số bù hai thực hiện phép làm tròn xuống sàn ($\lfloor a / 2^k \rfloor$, floor division). Với số dương, hai phép tính cho kết quả như nhau; nhưng với số âm, $(-1) / 2 = 0$ trong khi $(-1) \gg 1 = -1$.
Trên phần cứng FPGA, phép dịch phải số học được tổng hợp miễn phí (chỉ là việc đấu nối lại các đường dây bus tín hiệu và nhân bản bit dấu MSB), hoàn toàn không tốn cổng logic hay chu kỳ xung nhịp. Để đạt độ chính xác làm tròn đến số nguyên gần nhất (round-to-nearest) mà không gây trôi lệch phân cực (DC bias), ta cộng thêm đại lượng nửa bước lượng tử $2^{k-1}$ trước khi dịch:
$$y = (x + 2^{k-1}) \gg k$$
Ví dụ ở Tầng 2, sau phép nhân hai số Q1.15 thu được kết quả 32-bit ở định dạng Q2.30, phép tính $(p + 16384) \gg 15$ cộng thêm $2^{14} = 16384$ rồi dịch 15 bit để quay về Q1.15 với sai số làm tròn tối thiểu.

**Định cỡ bộ tích lũy MAC: 41 bit có dấu (không phải 42 bit):**
Tích của hai số 16-bit có dấu định dạng Q1.15 ($x_w[n] \cdot x_w[n+\tau]$) là một số 32-bit có dấu định dạng Q2.30, với dải giá trị từ $-2^{30}$ đến $2^{30}-1$.
Khi cộng dồn tối đa $L = 640$ tích như vậy để tính $\mathcal{R}_x[0]$ hoặc $\mathcal{R}_x[\tau]$, giá trị tích lũy dương cực đại lý thuyết là:
$$\mathcal{R}_{\max} = 640 \times 2^{30} \approx 6{,}8719 \times 10^{11}$$
So sánh với các lũy thừa của 2:
$$2^{39} \approx 5{,}4976 \times 10^{11} < \mathcal{R}_{\max} < 2^{40} \approx 1{,}0995 \times 10^{12}$$
Như vậy, phần biên độ (độ lớn không dấu) cần đúng $40\text{ bit}$. Thêm $1\text{ bit dấu}$ ở vị trí MSB cho số nguyên bù hai, tổng chiều rộng thanh ghi tích lũy cần thiết là **đúng 41 bit có dấu** (định dạng Q11.30), hoàn toàn không cần tới 42 bit.
Trên chip Intel Cyclone V SX, mỗi khối hardened DSP Block hỗ trợ thanh ghi tích lũy phần cứng lên tới $64\text{ bit}$. Do đó, bộ tích lũy 41-bit được đặt trọn vẹn bên trong khối DSP cứng, loại bỏ hoàn toàn nguy cơ tràn số (arithmetic overflow) mà không tiêu tốn thêm bất kỳ phần tử logic ALM ngoài nào.

**Khử hoàn toàn phép chia thời gian thực bằng phép nhân chéo nguyên:**
Hai điều kiện quan trọng nhất quyết định tính chất khung âm thanh vốn đòi hỏi phép chia số thực:
- Điều kiện khoảng lặng: $\mathcal{R}_x[0] \ge 0{,}03 \cdot E_{\text{ref}} \iff 100 \cdot \mathcal{R}_x[0] \ge 3 \cdot E_{\text{ref}}$.
- Điều kiện thanh tính: $\mathcal{R}_{\text{comp}}[\tau^*] / \mathcal{R}_x[0] \ge 0{,}45 \iff 100 \cdot S^* \ge 45 \cdot \mathcal{R}_x[0]$.

Hai phép so sánh này được thực thi bằng hai phép nhân số nguyên với hằng số và một bộ so sánh độ lớn trong đúng 1 chu kỳ xung nhịp, loại bỏ hoàn toàn bộ chia số thực phần cứng (Divider IP Core).

**Vì sao `float64` không bảo đảm đồng nhất giữa AMD64 và ARM64, còn số nguyên thì có:**
Chuẩn IEEE-754 quy định chính xác kết quả của bốn phép tính cơ bản `+`, `-`, `*`, `/` trên kiểu `float64`: chúng *được làm tròn đúng* (correctly rounded) và cho cùng bit trên mọi bộ xử lý tuân thủ chuẩn. Tuy nhiên, các hàm siêu việt như $\cos$, $\sin$, $\log_2$ **không** nằm trong nhóm bắt buộc làm tròn đúng bit cuối. Chuẩn chỉ đòi hỏi độ chính xác trong một khoảng vài ULP (Unit in the Last Place).
Do đó, thư viện toán học `glibc` trên kiến trúc AMD64 (x86\_64) và `libm` của Apple trên kiến trúc ARM64 (AArch64) có thể trả về hai kết quả lệch nhau 1--2 ULP. Khi kết quả này tham gia vào việc so sánh tìm cực đại ($\text{argmax}$) giữa hai đỉnh gần bằng nhau, 1 ULP có thể làm lật ngôi đỉnh thắng cuộc, khiến hai máy tính cho ra hai chuỗi $F_0$ khác nhau!
Ngược lại, hệ thống số nguyên bù hai với các phép `+`, `-`, `*`, `>>` hoàn toàn xác định trên từng bit. Do đó: **cùng một đoạn mã số nguyên, cùng một dữ liệu đầu vào, sẽ cho ra kết quả trùng khớp $100\%$ từng bit trên AMD64, ARM64 và trên khối mạch phần cứng RTL tổng hợp trên FPGA**.

---

### 4.1. Bản tham chiếu `float64` trên Laptop

```python
def float_pitch_frame(x: np.ndarray, use_interpolation: bool = True):
    # Buoc 1: Tru trung binh cuc bo (khu DC)
    xw = (x - np.mean(x)) * (GLOBAL_HANNING_Q15 / 32768.0)
    r0 = float(np.dot(xw, xw))
    if r0 == 0.0:
        return 0.0, 0, False

    # Buoc 2 & 3: Tu tuong quan va Bu suy hao kem phat quang tam
    w = GLOBAL_HANNING_Q15 / 32768.0
    rw0 = float(np.dot(w, w))
    best_score, tau_star, best_idx = -1e9, 0, 0
    scores = []
    for idx, tau in enumerate(range(TAU_MIN, TAU_MAX + 1)):
        rt = float(np.dot(xw[: 640 - tau], xw[tau:]))
        rw_tau = float(np.dot(w[: 640 - tau], w[tau:]))
        c_tau = rw0 / rw_tau
        bias = 2.0 ** (-0.01 * np.log2(600.0 / (16000.0 / tau)))
        score = rt * c_tau * bias
        scores.append(score)
        if score > best_score:
            best_score, tau_star, best_idx = score, tau, idx

    # Buoc 4: So sanh nguong huu thanh (0.45 * r0)
    if best_score / r0 < 0.45:
        return 0.0, 0, False

    # Buoc 5: Noi suy parabol 3 diem tinh F0 duoi mau
    if use_interpolation and 0 < best_idx < len(scores) - 1:
        ym1, y0, yp1 = scores[best_idx - 1], scores[best_idx], scores[best_idx + 1]
        denom = ym1 - 2.0 * y0 + yp1
        delta_tau = 0.5 * (ym1 - yp1) / denom if denom != 0 else 0.0
        return 16000.0 / (tau_star + delta_tau), tau_star, True

    return 16000.0 / tau_star, tau_star, True
```

---

### 4.2. Bản số nguyên Bit-Accurate từ con số 0

```python
import numpy as np

Q15, Q13 = 1 << 15, 1 << 13  # 32768 va 8192
TAU_MIN, TAU_MAX = 27, 213  # 600 Hz .. 75 Hz tai fs = 16 kHz


def hanning_rom_q15():
    """Bang ROM 640 mau Hanning Q1.15, bao hoa tai 32767 (Praat dong 413)."""
    i = np.arange(1, 641, dtype=np.float64)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * i / 641.0)
    return np.clip(np.round(w * Q15), 0, Q15 - 1).astype(np.int64)


def scoring_rom_q13(octave_cost=0.01):
    """Bang ROM C[tau] tich hop san phat quang tam, dinh dang Q3.13."""
    w = hanning_rom_q15().astype(np.float64) / Q15
    rw0 = float(np.dot(w, w))
    out = []
    for tau in range(TAU_MIN, TAU_MAX + 1):
        rw_tau = float(np.dot(w[: 640 - tau], w[tau:]))
        bias = 2.0 ** (-octave_cost * np.log2(600.0 / (16000.0 / tau)))
        out.append(round((rw0 / rw_tau) * bias * Q13))
    return np.array(out, dtype=np.int64)


# Khoi tao bang tra ROM toan cuc (chi tinh 1 lan duy nhat)
GLOBAL_HANNING_Q15 = hanning_rom_q15()
GLOBAL_SCORING_ROM_Q13 = scoring_rom_q13()


def parabolic_interpolation(scores, best_idx):
    """Noi suy parabol 3 diem: delta_tau = 0.5 * (y_-1 - y_+1) / (y_-1 - 2*y_0 + y_+1)."""
    if 0 < best_idx < len(scores) - 1:
        ym1 = float(scores[best_idx - 1])
        y0 = float(scores[best_idx])
        yp1 = float(scores[best_idx + 1])
        denom = ym1 - 2.0 * y0 + yp1
        if denom != 0.0:
            return 0.5 * (ym1 - yp1) / denom
    return 0.0


def fixed_pitch_frame(x_q15, ref_energy, use_interpolation=True):
    """Do cao do 1 khung 640 mau hoan toan bang so nguyen tren datapath 41-bit."""
    # Tru trung binh cuc bo (khu DC): dong 63-83 Sound_to_Pitch.cpp
    mean_x = (int(np.sum(x_q15)) + 320) // 640
    x_zm = x_q15 - mean_x

    # Pha 1: Nhan cua so Hanning Q1.15, lam tron round-to-nearest
    xw = ((x_zm * GLOBAL_HANNING_Q15) + 16384) >> 15
    r0 = int(np.dot(xw, xw))  # Nang luong khung (Q11.30)

    # Kiem tra nguong lang: r0 * 100 < 3 * ref_energy (khong chia)
    if ref_energy > 0 and r0 * 100 < 3 * ref_energy:
        return 0.0, 0, False
    if r0 == 0:
        return 0.0, 0, False

    # Pha 2: Quet 187 lag tu tuong quan va nhan bang bu C[tau]
    best_score, tau_star, best_idx = -(1 << 62), 0, 0
    scores = []
    for idx, tau in enumerate(range(TAU_MIN, TAU_MAX + 1)):
        n = 640 - tau
        r_tau = int(np.dot(xw[:n], xw[tau:]))  # 41-bit MAC
        score = (r_tau * GLOBAL_SCORING_ROM_Q13[idx] + 4096) >> 13
        scores.append(score)
        if score > best_score:
            best_score, tau_star, best_idx = score, tau, idx

    # Kiem tra nguong huu thanh: best * 100 >= 45 * r0 (khong chia)
    if best_score * 100 < 45 * r0:
        return 0.0, 0, False

    # Tinh F0: Co noi suy parabol duoi mau hoac tra bang ROM f0_lut
    if use_interpolation:
        delta_tau = parabolic_interpolation(scores, best_idx)
        return 16000.0 / (tau_star + delta_tau), tau_star, True
    return float(round(16000.0 / tau_star)), tau_star, True
```

**Ý nghĩa và tác động của nội suy parabol 3 điểm dưới mẫu:**
- **Ví dụ số 1 (Bước nhảy lag tại biên tần số cao):** Bước nhảy giữa hai độ trễ liền kề $\tau = 32$ và $\tau = 33$ tại $f_s = 16\text{ kHz}$ tương ứng với $F_0(32) = 500\text{ Hz}$ và $F_0(33) = 484{,}85\text{ Hz}$, lệch $\Delta F_0 = 15{,}15\text{ Hz}$. Quy đổi sang cent:
  $$\Delta_{\text{cent}} = 1200 \times \log_2\left(\frac{500}{484{,}85}\right) \approx \mathbf{53{,}4\text{ cent}}$$
  Ngưỡng phân biệt cao độ tối thiểu của thính giác người (JND) là khoảng $5\text{--}10\text{ cent}$. Như vậy, bước nhảy $53{,}4\text{ cent}$ thô gấp 5 đến 10 lần ngưỡng nghe của tai người!
- **Ví dụ số 2 (Sóng sin chuẩn $440\text{ Hz}$):** Tần số nốt La chuẩn $A_4 = 440\text{ Hz}$ có chu kỳ thực tế là $T_0 = 16000 / 440 \approx 36{,}3636\text{ mẫu}$. Khi quét lag nguyên, điểm cực đại rơi vào $\tau^* = 36$, tương ứng $F_0 = 444{,}44\text{ Hz}$, lệch $+4{,}44\text{ Hz}$ ($\mathbf{+17{,}4\text{ cent}}$). Khi áp dụng nội suy parabol 3 điểm qua ba giá trị $\{S[35], S[36], S[37]\}$, đỉnh cực trị dịch về $\tau^*_{\text{refined}} = 36{,}3636\text{ mẫu}$, trả về $F_0 \approx 440{,}0\text{ Hz}$ với sai số giảm xuống dưới $\mathbf{0{,}12\text{ cent}}$!

---

### 4.3. Kết quả kiểm chứng 3 tầng (Verification Protocol)

| Tín hiệu kiểm thử | Tier 1 (Float / Praat) | Tier 2 (Int / Float) | Tier 3 (RTL / Int) | Đánh giá vi kiến trúc |
|---|:---:|:---:|:---:|---|
| **Sin 75 Hz** | $\text{cent} = 2{,}66$, V/UV $= 0{,}0\%$ | $\text{cent} = 0{,}00$, V/UV $= 0{,}0\%$ | 0 bit lệch (khớp $100\%$) | Bắt đúng sàn tần số; không lỗi biên |
| **Sin 100 Hz** | $\text{cent} = 0{,}41$, V/UV $= 0{,}0\%$ | $\text{cent} = 0{,}12$, V/UV $= 0{,}0\%$ | 0 bit lệch (khớp $100\%$) | Dải trầm ổn định tuyệt đối |
| **Sin 200 Hz** | $\text{cent} = 0{,}43$, V/UV $= 0{,}0\%$ | $\text{cent} = 0{,}01$, V/UV $= 0{,}0\%$ | 0 bit lệch (khớp $100\%$) | Dải trung cực kỳ chuẩn xác |
| **Sin 440 Hz** | $\text{cent} = 0{,}46$, V/UV $= 0{,}0\%$ | $\text{cent} = 0{,}08$, V/UV $= 0{,}0\%$ | 0 bit lệch (khớp $100\%$) | Nội suy parabol xóa bỏ bậc thang |
| **Sin 590 Hz** | $\text{cent} = 7{,}59$, V/UV $= 0{,}0\%$ | $\text{cent} = 0{,}00$, V/UV $= 0{,}0\%$ | 0 bit lệch (khớp $100\%$) | Bắt đúng trần tần số; không nhảy quãng |
| **Khoảng lặng tuyệt đối** | Khớp $100\%$ UV (47 khung) | Khớp $100\%$ UV (47 khung) | 0 bit lệch (khớp $100\%$) | Cắt lặng bằng năng lượng hiệu quả |
| **Nhiễu trắng -35 dBFS** | Khớp $100\%$ UV (47 khung) | Khớp $100\%$ UV (47 khung) | 0 bit lệch (khớp $100\%$) | Ngưỡng $0{,}45$ chặn hoàn toàn nhiễu ngẫu nhiên |
| **Âm xát vô thanh /s/** | Khớp $100\%$ UV (47 khung) | Khớp $100\%$ UV (47 khung) | 0 bit lệch (khớp $100\%$) | Không có đỉnh chu kỳ giả |
| **Giọng nam (`speech_a`)** | $\text{cent} = 0{,}04$, V/UV $= 18{,}6\%$ | $\text{cent} = 0{,}01$, V/UV $= 19{,}6\%$ | 0 bit lệch (khớp $100\%$) | Cao độ khớp; lệch V/UV do Viterbi |
| **Giọng nữ (`speech_b`)** | $\text{cent} = 365{,}11$, V/UV $= 28{,}9\%$ | $\text{cent} = 0{,}01$, V/UV $= 35{,}1\%$ | 0 bit lệch (khớp $100\%$) | Sai số Viterbi toàn cục vs Cực đại tức thời |

*Bảng 1.3.5b: Bảng kiểm chứng độ chính xác 3 tầng (3-Tier Verification) trên 10 vector tín hiệu chuẩn mực.*

**Phân tích kết quả thực nghiệm:**
1. **Độ chính xác tần số tuyệt hảo trên sóng tuần hoàn:** Trên toàn bộ các sóng sin từ $75$ đến $590\text{ Hz}$, sai số giữa bản Fixed-Point số nguyên và bản Float (Tier 2) luôn nằm dưới $\mathbf{0{,}12\text{ cent}}$, thấp hơn rất nhiều ngưỡng nghe $5\text{ cent}$ của con người.
2. **Độ miễn nhiễm hoàn hảo với tạp âm và khoảng lặng:** Đối với các khung lặng, nhiễu trắng $-35\text{ dBFS}$ và âm xát /s/, cả ba tầng đều đồng thuận $100\%$ gán nhãn Unvoiced trên toàn bộ 47 khung.
3. **Bản chất sự chênh lệch V/UV trên tiếng nói thực tế:** Tỷ lệ lệch nhãn V/UV giữa bản phần cứng và Praat ($19{,}6\%$ và $28{,}9\text{--}35{,}1\%$) bắt nguồn từ mạng Viterbi toàn cục của Praat. Giữa bản số nguyên và bản float (Tier 2), sai số chỉ là $\mathbf{0{,}01\text{ cent}}$.
4. **Đạt chuẩn Bit-Accurate tuyệt đối ở Tier 3:** Trên toàn bộ 10 vector kiểm thử, mô hình số nguyên và mạch RTL mô phỏng có độ sai lệch **đúng 0 bit (trùng khớp $100\%$)**.

---

### 4.4. Xuất bảng tra ROM cho phần cứng Verilog (`export_hex`)

```python
def export_hex(output_dir="."):
    """Xuat cac tep .hex de nap vao M10K BRAM qua lenh $readmemh trong Verilog."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    w_q15 = hanning_rom_q15()  # 640 mau Q1.15
    c_rom = scoring_rom_q13()  # 187 muc Q3.13
    f0_lut = f0_rom_hz()  # 187 muc Hz (uint16)

    with open(out_path / "hanning_rom.hex", "w") as f:
        for val in w_q15:
            f.write(f"{val & 0xFFFF:04x}\n")

    with open(out_path / "c_tau_rom.hex", "w") as f:
        for val in c_rom:
            f.write(f"{val & 0xFFFF:04x}\n")

    with open(out_path / "f0_lut.hex", "w") as f:
        for val in f0_lut:
            f.write(f"{val & 0xFFFF:04x}\n")
```

---

### 4.5. Đánh giá việc loại bỏ quy hoạch động Viterbi trên FPGA

```
Khung t - 10ms               Khung t                Khung t + 10ms
   [ (1) ] ------------ Phạt nhảy Delta F0 ---------> [ (1) ] -----------------> [ (1) ]
   [ (2) ]                                            [ (2) ] -- Cost_jump ----> [ (2)*]
   [ (3) ]                                            [ (3) ]                    [ (3) ]
     ...                                                ...                        ...
   [ (14) ]                                           [ (14) ]                   [ (14) ]
   [ (UV) ] - - - - - - Phạt chuyển 0.14 - - - - - - >[ (UV) ] - - - - - - - - ->[ (UV) ]

+---------------------------------------------------------------------------------------+
| CHẾ ĐỘ FPGA STREAMING: Chỉ lấy đỉnh 1 (argmax cục bộ), độ trễ đường ống = 0           |
+---------------------------------------------------------------------------------------+
| ĐƯỜNG TỐI ƯU PRAAT VITERBI: Duyệt 15 ứng viên x N khung, độ trễ bằng toàn bộ câu nói   |
+---------------------------------------------------------------------------------------+
```

*Hình 1.3.5d: Đối chiếu cơ chế trích chọn cao độ: Lưới quy hoạch động Viterbi 15 ứng viên của Praat (phần mềm) vs. Trích chọn cực đại tức thời không trễ trên FPGA (phần cứng).*

**Đọc Hình 1.3.5d (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Ba cột mốc thời gian:** Chuỗi 3 khung phân tích liên tiếp gồm Khung $t - 10\text{ ms}$, Khung $t$, và Khung $t + 10\text{ ms}$ với bước trượt khung $\Delta t_{\text{hop}} = 10\text{ ms}$.
2. **Các nút tròn Ứng viên 1 đến 14:** 14 đỉnh cực đại cục bộ có điểm tự tương quan cao nhất trong mỗi khung, xếp theo thứ tự giảm dần ($\tau_1^*, \tau_2^*, \dots, \tau_{14}^*$).
3. **Nút tròn UV (Ứng viên 15):** Ứng viên đại diện cho trạng thái Vô thanh (Unvoiced), gán điểm cạnh tranh $R_{\text{unvoiced}}$ phụ thuộc tỷ số năng lượng khoảng lặng.
4. **Đường mũi tên tối ưu Praat Viterbi:** Duyệt toàn cục xuyên suốt câu để cực tiểu hóa tổng chi phí gồm điểm nội khung, phạt bước nhảy tần số $\text{Cost}_{\text{jump}}$ (0,35), và phạt chuyển đổi trạng thái Voiced $\leftrightarrow$ Unvoiced (0,14). Độ trễ bằng toàn bộ câu.
5. **Chế độ FPGA Streaming:** Chỉ lấy duy nhất Ứng viên 1 ($\tau_1^*$) qua một bộ so sánh cực đại thanh ghi. Quyết định chốt ngay lập tức, độ trễ bằng 0.

**Ba nguyên nhân kỹ thuật khiến việc bỏ Viterbi trên FPGA là hợp lý:**
1. **Bảo toàn tính thời gian thực của kiến trúc Streaming:** Viterbi cần biết toàn bộ câu để quay lui (backtracking). Trên một câu 10 giây, độ trễ cấu trúc là 10 giây.
2. **Ba tầng tiền xử lý đã giải quyết phần lớn nguyên nhân gây lỗi quãng tám:** HPF $60\text{ Hz}$ dập trôi DC; bảng bù $C[\tau]$ san phẳng độ dốc cửa sổ; và bảng phạt quãng tám nội khung phá vỡ hoàn toàn thế cân bằng giữa đỉnh $1T_0$ và $2T_0$.
3. **Ngăn chặn sự bùng nổ tài nguyên BRAM và logic điều khiển:** Ma trận 15 ứng viên $\times 1000$ khung cần $60\text{ KB}$ cho mỗi bảng, vượt quá dung lượng vài khối M10K dành cho khối Pitch.

**Phương án thay thế nếu cần Viterbi:** Chạy phần mềm trên nhân ARM Cortex-A9 (HPS) tích hợp sẵn trên chip Cyclone V SoC mà không tốn tài nguyên logic FPGA.

**Giải pháp phần cứng nội bộ: Bộ lọc trung vị trượt 3 điểm (Median-3 Filter):**
$$F_{0,\text{clean}}[t] = \text{median}\bigl(F_0[t-1],\; F_0[t],\; F_0[t+1]\bigr)$$

| Khung thời gian | $t-1$ | $t$ | $t+1$ |
|---|:---:|:---:|:---:|
| Giá trị thô xuất từ `argmax` | $122\text{ Hz}$ | $245\text{ Hz}$ (nhảy đôi) | $124\text{ Hz}$ |
| Giá trị sau lọc trung vị 3 điểm | $122\text{ Hz}$ | **124 Hz** | 124 Hz |

- Tài nguyên: Chỉ cần 3 thanh ghi 16-bit và mạng so sánh nhỏ.
- Độ trễ: Đúng 1 khung ($10\text{ ms}$).
- Giới hạn: Chỉ dập được 1 điểm nhảy vọt cô lập đơn lẻ; nếu lỗi kéo dài $\ge 2$ khung, trung vị sẽ bị kéo theo.

---

## 5. Sơ đồ Vi Kiến Trúc Pipeline Đề Xuất (Dataflow Architecture)

```
Dòng mẫu I2S (16 kHz, 16-bit)
       |
       v
+-------------------------------------------------------+
| Raw Ring Buffer (640 mẫu thô, vùng A: 0..319, B: 320..639) | <--- Bộ đếm ghi cuốn vòng
+---------------------------+---------------------------+
                            | Đủ 160 mẫu mới (10 ms)
                            v
+-------------------------------------------------------+
| PHA 1 (640 chu kỳ clock):                             | <--- ROM Hanning (640 mục Q1.15)
| Đọc 640 mẫu thô, nhân ROM Hanning, ghi True Dual-Port |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
| True Dual-Port RAM (640 mẫu x_win[n])                 |
| Cổng A: địa chỉ n     |     Cổng B: địa chỉ n + tau   |
+---------------------------+---------------------------+
                            | 2 cổng đọc song song
                            v
+-------------------------------------------------------+
| PHA 2 (97.240 chu kỳ clock):                          |
| Quét 187 độ trễ tau in [27, 213]                     |
| 1 Bộ nhân DSP + Thanh ghi tích lũy 41-bit             |
+---------------------------+---------------------------+
                            | R_x[tau]
                            v
+-------------------------------------------------------+
| Hậu xử lý: Bù C[tau] (ROM Q3.13) + argmax 187 lag    |
+---------------------------+---------------------------+
                            |
                            v
+-------------------------------------------------------+
| Bộ lọc trung vị 3 điểm                                |
+---------------------------+---------------------------+
                            |
                            v
       pitch_f0.bin (F0 mỗi 10 ms ra Shared Folder)
```

*Hình 1.3.5e: Vi kiến trúc hai pha: Cửa sổ được nhân một lần khi chép sang RAM, vòng quét tương quan chỉ còn đọc hai cổng và một phép nhân DSP.*

**Đọc Hình 1.3.5e (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Raw Ring Buffer (hàng trên):** Mẫu I$^2$S thô được ghi liên tục vào bộ đệm vòng 640 mẫu chia làm hai vùng A và B để cuốn vòng mà không cần dịch chuyển dữ liệu. Khi đủ 160 mẫu mới ($10\text{ ms}$), bộ điều khiển phát xung kích hoạt sang Pha 1.
2. **Pha 1 (640 chu kỳ clock):** Đọc lần lượt 640 mẫu thô, nhân từng mẫu với hệ số Hanning từ ROM, rồi ghi kết quả $x_{\text{win}}[n]$ sang True Dual-Port RAM. Nhân trong Pha 1 bảo đảm vị trí trong khung đã cố định, giữ trọn tính đúng đắn toán học.
3. **True Dual-Port RAM (khối giữa):** Cung cấp hai cổng đọc độc lập A và B trong cùng một nhịp đồng hồ ($x_{\text{win}}[n]$ và $x_{\text{win}}[n+\tau]$), đi thẳng vào cùng một bộ nhân DSP.
4. **Pha 2 (97.240 chu kỳ clock):** Với mỗi độ trễ $\tau$ trong 187 giá trị, bộ nhân DSP tích lũy $\sum_n x_{\text{win}}[n] x_{\text{win}}[n+\tau]$ vào thanh ghi tích lũy 41-bit. Tổng chu kỳ toàn khung: $640 + 97.240 = \mathbf{97.880\text{ chu kỳ}}$.
5. **Hậu xử lý (hàng dưới):** Nhân $\mathcal{R}_x[\tau]$ với bảng $C[\tau]$ (Q3.13), tìm $\tau^*$ bằng bộ so sánh cực đại thanh ghi, rồi đưa qua bộ lọc trung vị 3 điểm trước khi xuất ra bộ nhớ chia sẻ.

```
A. Luồng Log-Mel STFT (Mục 1.2 & 1.3): Khung L = 400 mẫu (25 ms), bước nhảy H = 160 mẫu (10 ms)
      Tâm K1 (12.5 ms)
         |
      .-'-.       .-'-.       .-'-.
     /     \     /     \     /     \
----+-------+---+-------+---+-------+-------------------->
    0      25  10      35  20      45 ms

         <--------> Độ lệch tâm pha Dt_center = 20 - 12.5 = 7.5 ms (120 mẫu)

B. Luồng Cao Độ Pitch F0 (Mục 1.3.5): Khung L = 640 mẫu (40 ms), bước nhảy H = 160 mẫu (10 ms)
            Tâm K1 (20.0 ms)
               |
            .--'--.           .--'--.           .--'--.
           /       \         /       \         /       \
----------+---------+-------+---------+-------+---------+--> Thời gian t (ms)
          0        40      10        50      20        60
                    <-------> Độ trễ chờ nạp đầy ban đầu Dt_init = 40 - 25 = 15 ms (240 mẫu)
```

*Hình 1.3.5f: Đối sánh trục thời gian giữa Luồng Log-Mel STFT ($400\text{ mẫu} = 25\text{ ms}$) và Luồng Pitch $F_0$ ($640\text{ mẫu} = 40\text{ ms}$): Làm rõ độ lệch tâm pha $7{,}5\text{ ms}$ và độ trễ nạp đầy ban đầu $15\text{ ms}$.*

**Đọc Hình 1.3.5f (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Trục hoành thời gian chung (Dưới cùng):** Đánh dấu các mốc thời gian vật lý: $0, 10, 20, 25, 30, 40, 50, 60\text{ ms}$.
2. **Hàng A — Luồng Log-Mel STFT:** Vòm cửa sổ $25\text{ ms}$ ($400\text{ mẫu}$), trượt $10\text{ ms}$ ($160\text{ mẫu}$). Khung 1 nạp xong ở $25\text{ ms}$, tâm nằm ở $12{,}5\text{ ms}$.
3. **Hàng B — Luồng Pitch $F_0$:** Vòm cửa sổ Hanning $40\text{ ms}$ ($640\text{ mẫu}$), trượt $10\text{ ms}$ ($160\text{ mẫu}$). Khung 1 nạp xong ở $40\text{ ms}$, tâm nằm ở $20{,}0\text{ ms}$.
4. **Mũi tên tím $\Delta t_{\text{init}} = 15\text{ ms}$:** Độ trễ chờ nạp đầy khung đầu tiên, chỉ xảy ra đúng một lần lúc khởi động.
5. **Mũi tên đỏ $\Delta t_{\text{center}} = 7{,}5\text{ ms}$:** Độ lệch tâm pha giữa hai luồng, lặp lại cố định ở mọi khung.

---

## 6. Sổ Cái Hạch Toán Tài Nguyên Silicon trên FPGA DE10-Standard

Hệ thống nhắm tới kit **DE10-Standard** trang bị chip **Intel Cyclone V SX SoC (5CSXFC6D6F31C6N)**. Bảng sổ cái hạch toán tài nguyên silicon:

**1. Kiểm đếm số phép tính chính xác trên mỗi khung $10\text{ ms}$:**
- **Pha 1 (Nhân cửa sổ Hanning và ghi True Dual-Port RAM):** $640\text{ chu kỳ clock}$ (sử dụng 1 bộ nhân DSP).
- **Pha 2 (Quét tự tương quan 187 lag từ $\tau = 27$ đến $\tau = 213$):**
  $$N_{\text{corr}} = \sum_{\tau=27}^{213} (640 - \tau) = 187 \times 520 = \mathbf{97.240\text{ phép MAC}}$$
- **Pha 3 (Bù suy hao cửa sổ và tìm cực đại):** Thực hiện gối đầu (pipeline overlap) $187\text{ chu kỳ}$, hoàn toàn che giấu trong đường ống.
- **Tổng chu kỳ thực thi toàn khung:** $640 + 97.240 = \mathbf{97.880\text{ chu kỳ clock}}$.

**2. Định mức thời gian thực và kích thước thanh ghi tích lũy:**
- **Hệ số thời gian thực (RTF):** Ở xung nhịp danh định $f_{\text{clk}} = 50\text{ MHz}$, toàn bộ $97.880$ chu kỳ hoàn thành trong:
  $$T_{\text{calc}} = \frac{97.880}{50.000.000\text{ Hz}} \approx \mathbf{1{,}958\text{ ms}} \ll 10\text{ ms} \implies \mathbf{\text{RTF} \approx 0{,}196}$$
- **Định cỡ thanh ghi tích lũy:** Giá trị lớn nhất của 640 tích số Q2.30 là $640 \times 2^{30} < 2^{40}$, do đó thanh ghi tích lũy rộng **41 bit có dấu** (định dạng Q11.30) là đủ tuyệt đối để chống tràn số mà không cần tới 42 bit. Khối DSP cứng trên Cyclone V hỗ trợ tích lũy 64-bit, bảo đảm an toàn toán học tuyệt đối.

| Tài nguyên phần cứng | Tiêu tốn cho Pitch | Khả dụng (Cyclone V) | Tỷ lệ sử dụng | Đánh giá vi kiến trúc |
|---|:---:|:---:|:---:|---|
| **Khối nhớ M10K BRAM** | 3--4 khối | 553 khối | $0{,}54\%\text{--}0{,}72\%$ | Ring Buffer ($1024\times 16$), RAM $x_w$ ($1024\times 16$), ROM $w, C[\tau]$ |
| **Khối DSP (18x18-bit)** | 1 khối | 112 khối | $0{,}89\%$ | 1 DSP chạy tuần tự ở 50 MHz đạt $\text{RTF} \approx 0{,}196$ |
| **Bộ logic ALM / Registers** | $\approx 450$ ALMs | 41.910 ALMs | $1{,}07\%$ | Bộ đếm địa chỉ FSM, bộ so sánh cực đại thanh ghi |
| **Bộ chia số thực (Divider)** | 0 | Không cần | $0\%$ | Thay hoàn toàn bằng bảng tra ROM và so sánh nhân chéo |

*Bảng 1.3.5c: Sổ cái hạch toán tài nguyên silicon cho khối Pitch trên FPGA DE10-Standard.*

---

## 7. Tổng Kết và Cầu Nối Chuyển Tiếp

- **Mục 1.2 & 1.3** cung cấp vector đặc trưng phổ $80\text{ chiều}$ (Log-Mel) đại diện cho *khẩu hình miệng và cộng hưởng khoang thanh đạo*.
- **Mục 1.3.5** bổ sung dòng dữ liệu vô hướng $1\text{ chiều}$ ($F_0$) đại diện cho *nhịp đập cơ học của dây thanh quản*.
- **Sự kết hợp hai luồng đặc trưng:** Bằng cách ghép luồng Log-Mel và luồng Pitch $F_0$, hệ thống Edge AI trên FPGA thu nhận được đầy đủ cả **ngữ âm** lẫn **ngữ điệu**, mở đường cho các mô hình phân loại thanh điệu tiếng Việt và nhận dạng cảm xúc giọng nói chỉ tiêu tốn chưa đầy $2\%$ tài nguyên silicon của kit DE10-Standard.

---

## Phụ lục 1.3.5-A: Áp dụng lý thuyết 1.3.5 vào mã nguồn Python (`audio_processing.py` và `evaluator.py`)

> **$\blacktriangleright$ PHẠM VI VÀ MỤC TIÊU**
>
> Phụ lục này đối chiếu hai tệp mã nguồn xử lý âm thanh trong thư mục `Pronunciation_Final_Master` của kho lưu trữ `DucDocDao/Pitch-Project` (nhánh `main`) với hệ thống lý thuyết đo cao độ $F_0$ bằng thuật toán tự tương quan ở Mục 1.3.5 (chuẩn Praat, Boersma 1993). Để làm sáng tỏ toàn bộ luồng gọi hàm, phụ lục khảo sát thêm các đoạn mã liên kết trong `main.py`, `visualizer.py`, `generate_audio.py` và `sentence_data.py`. Mọi hành vi mô tả dưới đây đều được truy xuất trực tiếp từ mã nguồn thực tế và đối chiếu tường minh với mã nguồn C++ gốc của Praat (`fon/Sound_to_Pitch.cpp` và `fon/Pitch.cpp`).

### 1. Bức Tranh Tổng Thể: Hai Tệp Làm Gì Trong Hệ Thống

#### 1.1. Ranh giới triển khai: Mã nguồn Python nguyên bản vs. Hệ thống FPGA Edge Node
- **Trong kho lưu trữ `Pitch-Project` (Môi trường thực nghiệm máy tính):** Toàn bộ quy trình chạy trên CPU/GPU máy chủ: tổng hợp âm thanh bằng Kokoro TTS, cắt lặng bằng Librosa, đo cao độ bằng Praat C++ (qua Parselmouth), nhận diện mốc từ bằng Whisper, căn chỉnh và tính điểm tương quan Pearson $r$.
- **Khi triển khai thực tế trên vi mạch FPGA (Hệ thống mục tiêu):** Bo mạch FPGA DE10-Standard gánh trọn vẹn khâu tiền xử lý (HPF 60 Hz và cắt lặng) và chạy song song hai luồng phần cứng: (1) Nhánh âm thanh $16\text{ kHz}$ sạch phục vụ trực tiếp bộ mã hóa Whisper, và (2) Nhánh đo cao độ tự tương quan Mục 1.3.5 ghi trực tiếp mảng nhị phân `pitch_f0.bin` ra Thư mục dùng chung (Shared Folder). Máy chủ chỉ cần đọc `pitch_f0.bin` và mốc từ để chấm điểm $r$, **hoàn toàn không cần cài đặt hay chạy Praat/Parselmouth**.

#### 1.2. Bài toán của dự án
Định lượng và so sánh đường cong cao độ (pitch contour) giữa một câu tiếng Anh do giọng tham chiếu chuẩn đọc (nữ Mỹ `sarah`) với cùng câu đó do người học đọc (nam Mỹ `michael`). Kết quả đánh giá cuối cùng là hệ số tương quan Pearson ($r$) giữa hai đường cao độ đã căn chỉnh thời gian.

#### 1.3. Luồng xử lý một câu nói (theo `main.py`)
1. `trim_silence_and_save` (`audio_processing.py`): Cắt bỏ khoảng lặng ở hai đầu tệp âm thanh và ghi ra tệp WAV đã cắt.
2. `extract_features_praat` (`audio_processing.py`): Đo đường cao độ $F_0$ trên chính tệp WAV đã cắt bằng công cụ Praat (thông qua `parselmouth`).
3. `get_user_timestamps` (`evaluator.py`): Nạp mô hình Whisper (`openai/whisper`) bóc tách mốc thời gian từ ($w_{\text{start}}, w_{\text{end}}$) trên chính tệp WAV đã cắt.
4. `plot_analysis` (`visualizer.py`): Gọi chuỗi 4 hàm căn chỉnh và tính Pearson $r$ trong `audio_processing.py` (`get_local_chunk`, `equalize_local_chunk`, `dynamic_sliding_window_pearson`, `summarize_pearson`).
5. `summarize_sentence_reports` (`audio_processing.py`): Gom toàn bộ kết quả của nhiều câu thành bảng thống kê phân phối độ chính xác theo các ngưỡng tích lũy.

```
+---------------------------------------+
| Tệp Âm Thanh Thô (Kokoro, 24 kHz)     |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
| trim_silence_and_save (Librosa, 30dB) |
+-------------------+-------------------+
                    |
                    v
+---------------------------------------+
| Tệp WAV Đã Cắt Lặng (Gốc t = 0 chung) |
+---------+-------------------+---------+
          |                   |
          v                   v
+-------------------+ +-------------------+
| Luồng 1: Praat F0 | | Luồng 2: Whisper  |
| snd.to_pitch()    | | Mốc từ w_start/end|
+---------+---------+ +---------+---------+
          |                     |
          +----------+----------+
                     |
                     v
+-----------------------------------------+
| Căn chỉnh theo từ (equalize_local_chunk)|
+--------------------+--------------------+
                     |
                     v
+-----------------------------------------+
| Cửa sổ trượt Pearson (dynamic_sliding..) |
+--------------------+--------------------+
                     |
                     v
+-----------------------------------------+
| Tổng hợp điểm số (summarize_pearson)    |
+-----------------------------------------+
```

*Hình 1.3.5g: Sơ đồ luồng xử lý âm thanh, trích xuất hai luồng song song (Praat $F_0$ và Whisper Timestamps) và thuật toán đối sánh ngữ điệu trong mã nguồn Python.*

---

### 2. Bảng Thuật Ngữ Dùng Trong Phụ Lục

| Thuật ngữ tiếng Việt | Thuật ngữ tiếng Anh | Định nghĩa chuẩn mực trong ngữ cảnh mã nguồn |
|---|---|---|
| Khung phân tích | Frame | Đoạn gồm $L$ mẫu tín hiệu liên tiếp dùng để tính một giá trị $F_0$ |
| Bước nhảy trượt khung | Time step / Hop size | Khoảng thời gian giữa tâm đối xứng của hai khung liên tiếp ($10\text{ ms}$) |
| Điểm cao độ | Pitch point | Một phần tử trong mảng `pitch`: giá trị $F_0$ (Hz), bằng $0$ nếu vô thanh |
| Hữu thanh / Vô thanh | Voiced / Unvoiced | Trạng thái khung tín hiệu có / không có dao động tuần hoàn của dây thanh |
| Tổng tự tương quan | Autocorrelation sum | Tổng tích các cặp mẫu trễ $\tau$, không phải tích chập |
| Hệ số tương quan Pearson $r$ | Pearson correlation coefficient | Thước đo mức độ đồng biến/nghịch biến tuyến tính giữa hai đường cao độ |
| Căn chỉnh thời gian | Time alignment | Đưa hai đường cao độ có độ dài khác nhau về cùng trục chỉ số |

---

### 3. `extract_features_praat`: Một Dòng Code Chứa Toàn Bộ Mục 1.3.5

#### 3.1. Mã nguồn
```python
def extract_features_praat(audio_path, verbose=False):
    snd = parselmouth.Sound(audio_path)
    pitch_object = snd.to_pitch()
    pitch = np.nan_to_num(pitch_object.selected_array["frequency"])
    time_stamps = pitch_object.xs()
    return pitch, time_stamps
```

#### 3.2. Cơ chế thực thi
- `snd.to_pitch()`: Kích hoạt hàm `Sound_to_Pitch_ac` với toàn bộ 10 tham số chuẩn mực của Praat.
- `selected_array['frequency']`: Trích xuất ứng viên tối ưu toàn cục từ Viterbi. Các khung vô thanh được gán số $0$.
- `pitch_object.xs()`: Trả về mảng mốc thời gian thực tế, nhưng trong `main.py` mảng này bị bỏ qua (`pitch, _ = ...`).

#### 3.3. Ánh xạ chi tiết từ Praat C++ sang lý thuyết Mục 1.3.5

| Bước thực thi bên trong `snd.to_pitch()` | Vị trí trong Mục 1.3.5 | Công thức / Tham số liên kết |
|---|---|---|
| Cắt khung 3 chu kỳ của $75\text{ Hz} = 40\text{ ms}$, bước trượt $10\text{ ms}$ | Mục 3.A | Quy tắc Boersma, Tham số 1--2 |
| Nhân cửa sổ Hanning (`very_accurate = off`) | Mục 3.B | Lựa chọn kỹ thuật Hanning, Tham số 4 |
| Tính tự tương quan $\mathcal{R}_x[\tau]$ | Mục 2 | Công thức tính tự tương quan |
| Bù suy hao cửa sổ bằng phép chia cho $\mathcal{R}_w[\tau]$ | Mục 3.B | Công thức hệ số bù suy hao $C[\tau]$ |
| Giới hạn dải tìm kiếm đỉnh trong $[\tau_{\min}, \tau_{\max}]$ | Mục 2 | Dải lag $[27, 213]$ |
| Trích xuất 14 đỉnh cực đại + 1 ứng viên Vô thanh | Mục 3.C | Tham số 5, 6, 7 (ngưỡng 0,45 và 0,03) |
| Phạt log-lag nội khung để tránh lỗi nhảy $F_0 / 2$ | Mục 3.C | Tham số 8 (`octave_cost = 0,01`) |
| Quy hoạch động Viterbi xuyên suốt câu nói | Mục 4 | Tham số 9--10, Hình 1.3.5d |
| Xuất giá trị cao độ $F_0 = f_s / \tau^*$ | Mục 2 | Công thức tần số cơ bản |

#### 3.4. Chỗ mã nguồn khác lý thuyết và hệ quả kỹ thuật
- **(a) Tần số lấy mẫu thực tế $24\text{ kHz}$ (thay vì $16\text{ kHz}$):** Kokoro TTS sinh tệp $24\text{ kHz}$, làm dải lag mở rộng thành $[40, 320]$ mẫu và khung dài $960$ mẫu. Thời lượng vật lý vẫn là $40\text{ ms}$.
- **(b) Có quy hoạch động Viterbi và 15 ứng viên:** Đem lại đường Pitch mượt mà nhưng đòi hỏi có toàn bộ câu âm thanh trong bộ nhớ.
- **(c) Thiếu bước lọc HPF 60 Hz:** Kokoro là âm thanh tổng hợp sạch nên ít trôi DC, nhưng lệch quy trình vi mạch.
- **(d) Giải phẫu mã nguồn C++ của Praat (`Sound_to_Pitch.cpp` và `Pitch.cpp`):** Như đã phân tích tại Mục 3.0, mã nguồn C++ của Praat tính tự tương quan qua Wiener--Khinchin FFT 1024 điểm, dùng phép chia số thực bù cửa sổ, và nội suy Sinc 30 mẫu.

---

### 4. `trim_silence_and_save`: Cắt Khoảng Lặng Hai Đầu

- Hàm dùng `librosa.effects.trim(y, top_db=30)`.
- Ngưỡng $30\text{ dB}$ tương ứng biên độ rơi xuống dưới $10^{-30/20} \approx 3{,}2\%$ so với đỉnh lớn nhất của câu.
- Mục đích chính: **Đồng bộ gốc thời gian $t = 0$** của người học với giọng mẫu trước khi căn chỉnh theo từ.

---

### 5. Căn Chỉnh Hai Đường Cao Độ Theo Từng Từ

- `get_local_chunk`: Cắt đoạn cao độ theo tỉ lệ $i = \lfloor (t/D) \cdot N \rfloor$.
- `equalize_local_chunk`: Dùng `np.interp` co giãn đoạn cao độ của người đọc về đúng số điểm của giọng mẫu.
- **Lỗi tiềm ẩn:** Nội suy tuyến tính qua điểm $0\text{ Hz}$ sinh ra giá trị cao độ giả mạo ($100\text{ Hz}$), làm suy giảm nhân tạo hệ số Pearson $r$.
- Ghép vào mảng chung `stitched_user_pitch` có độ dài bằng giọng mẫu.

---

### 6. `dynamic_sliding_window_pearson`: Tính Hệ Số Pearson Trên Các Cửa Sổ Trượt

- Kích thước cửa sổ trượt $W = 2N / (K + 2)$ với $K$ là số từ trong câu (bao trọn khoảng 2 từ), bước trượt $S = W / 2$.
- Lọc điểm hợp lệ: Chỉ tính trên các điểm mà cả hai đường đều hữu thanh ($u_i > 0$ và $v_i > 0$).
- Tính hệ số tương quan tuyến tính Pearson:
  $$r_{\text{Pearson}} = \frac{\sum (u_i - \bar{u})(v_i - \bar{v})}{\sqrt{\sum (u_i - \bar{u})^2 \sum (v_i - \bar{v})^2}}$$
- **Tính chất quan trọng:** Bất biến đối với phép co giãn tỉ lệ ($r(X, aY + b) = r(X, Y)$ với $a > 0$). Giọng nam trầm hơn giọng nữ 1 quãng tám ($u_i = 0{,}5 v_i$) vẫn đạt $r = 1{,}0$. Pearson $r$ đo **hình thái ngữ điệu** chứ không đo cao độ tuyệt đối.

---

### 7. `summarize_pearson` và `summarize_sentence_reports`

- Bỏ các cửa sổ NaN.
- Kẹp giá trị không dương ($r \le 0$) về $0$, rồi tính trung bình để ra điểm `mean_r` của câu.
- Thống kê phân phối số lượng câu đạt các ngưỡng tích lũy $\ge 0{,}9, \ge 0{,}8, \dots, \ge 0{,}3$.

---

### 8. `evaluator.py`: Nhận Diện Mốc Thời Gian Bằng Whisper và Các Phương Án Nhẹ Hơn

- Tín hiệu được lấy mẫu lại từ $24\text{ kHz}$ về $16\text{ kHz}$ để đưa vào Whisper `base` trích xuất mốc từ $(w_{\text{start}}, w_{\text{end}})$.
- **Phương án thay thế tối ưu:**
  1. *Căn chỉnh cưỡng bức (Forced Alignment — MFA, MMS_FA):* Vì văn bản chuẩn đã biết trước 100%, forced alignment không thể nhận dạng sai chữ, chỉ căn chỉnh ranh giới âm vị với độ chính xác $< 20\text{ ms}$, chạy cực nhẹ trên CPU.
  2. *Dynamic Time Warping (DTW) trên chuỗi Log-Mel:* Uốn trục thời gian trực tiếp trên đặc trưng 80 Log-Mel đã có, hoàn toàn không cần mô hình nơ-ron nhận dạng nào ở máy chủ.

---

### 9. Bảng Tổng Hợp So Sánh Toàn Diện: Lý Thuyết Mục 1.3.5 vs. Mã Nguồn Python

| Đặc tính kỹ thuật | Thiết kế Lý thuyết Mục 1.3.5 | Mã nguồn Python (`Pitch-Project`) | Đánh giá & Hệ quả kỹ thuật |
|---|---|---|---|
| Thuật toán đo cao độ | MAC trực tiếp + Bù ROM Q-format | Thư viện `parselmouth` (`snd.to_pitch()`) | Mã nguồn C++ Praat chuẩn mực |
| Tần số lấy mẫu đo $F_0$ | $f_s = 16.000\text{ Hz}$ | $f_s = 24.000\text{ Hz}$ (do Kokoro sinh ra) | Dải lag $[40, 320]$, $L = 960$ mẫu |
| Dải tần số tìm kiếm | $75\text{--}600\text{ Hz}$ | $75\text{--}600\text{ Hz}$ | Trùng khớp hoàn toàn |
| Kích thước khung / Bước trượt | $40\text{ ms}$ / $10\text{ ms}$ ($640$ / $160$ mẫu) | $40\text{ ms}$ / $10\text{ ms}$ ($960$ / $240$ mẫu) | Trùng khớp thời lượng vật lý |
| Dạng cửa sổ phân tích | Hanning đối xứng | Hanning đối xứng (`very_accurate = off`) | Trùng khớp dạng cửa sổ |
| Ngưỡng thanh tính / Ngưỡng lặng | $\theta_{\text{voice}} = 0{,}45$; $\theta_{\text{silence}} = 0{,}03$ | Mặc định Praat ($0{,}45$ và $0{,}03$) | Trùng khớp tuyệt đối |
| Cơ chế trích chọn cực đại | FPGA: 1 ứng viên, độ trễ 0, lag nguyên + Parabol | 15 ứng viên + Viterbi + Nội suy Sinc | Mượt mà, không bậc thang, trễ toàn câu |
| Tiền xử lý lọc thông cao | Bắt buộc bộ lọc HPF 60 Hz (Mục 1.1.5) | Không có bước lọc nào trước Praat | Lệch quy trình, chấp nhận được với TTS |
| Tiền xử lý cắt khoảng lặng | So sánh năng lượng khung tĩnh | Dùng `librosa.effects.trim` ($30\text{ dB}$) 2 đầu | Nhằm đồng bộ gốc thời gian $t = 0$ |
| Phương pháp đối sánh cao độ | Chuẩn bị đưa lên vi mạch FPGA | Pearson $r$ trên cửa sổ trượt $\approx 2$ từ | Đo hình thái giai điệu ngữ điệu |
| Tần số lấy mẫu nhận diện | $16\text{ kHz}$ (cho luồng âm thanh sạch) | $16\text{ kHz}$ (lấy mẫu lại đưa vào Whisper) | Hiện thực đúng mô hình hai luồng song song |

---

### 10. Danh Sách Các Điểm Lệch Và Lỗi Tiềm Ẩn Cần Lưu Ý

1. **Vứt bỏ mảng mốc thời gian thực `xs()` của Praat:** Việc tính chỉ số khung theo tỉ lệ tuyến tính $i = \lfloor (t/D) \cdot N \rfloor$ bỏ qua độ lệch tâm pha ban đầu $20\text{ ms}$, gây ra sai số thời gian tối đa cỡ nửa khung ($\le 2$ điểm cao độ).
2. **Hiện tượng sinh $F_0$ giả khi nội suy qua điểm $0\text{ Hz}$:** Hàm `np.interp` nội suy tuyến tính giữa các điểm vô thanh ($0\text{ Hz}$) và hữu thanh ($> 0\text{ Hz}$), tạo ra các giá trị tần số giả mạo lọt qua bộ lọc thanh tính và làm suy giảm nhân tạo hệ số tương quan Pearson $r$.
3. **Lệch tần số lấy mẫu ($24\text{ kHz}$ vs $16\text{ kHz}$):** Mọi bảng tra lag, địa chỉ ROM và số lượng phép tính MAC trong Mục 5 của tài liệu không thể áp dụng trực tiếp cho dữ liệu Kokoro mà phải nhân theo tỉ lệ $24/16 = 1{,}5$.
4. **Bỏ qua bộ lọc HPF 60 Hz:** Mã nguồn đưa tín hiệu thô vào phân tích mà không qua khâu triệt tiêu trôi DC như yêu cầu của Cổng kiểm chứng phần mềm.
5. **Kẹp giá trị tương quan không dương ($r \le 0$) về $0$:** Phép kẹp này làm điểm trung bình `mean_r` của câu tăng cao hơn so với trung bình số học thực tế.
6. **Tên tệp `evaluator.py` gây hiểu lầm:** Tệp này không thực hiện đánh giá hay chấm điểm mà chỉ là bộ trích xuất mốc từ dựa trên Whisper.
7. **Tính Pearson trên thang tần số Hertz tuyến tính:** Hệ số Pearson tính trực tiếp trên đơn vị Hz mà không đổi sang semitone (thang logarit), khiến các biến động ở dải tần số cao chịu trọng số ảnh hưởng lớn hơn dải trầm.
8. **Sai số làm tròn số thực trong thống kê ngưỡng:** Phép chia số thực `threshold / 10` trong Python có thể sinh ra phần dư làm tròn vô cùng nhỏ, cần lưu ý khi xây dựng các bài test kiểm thử tự động.
