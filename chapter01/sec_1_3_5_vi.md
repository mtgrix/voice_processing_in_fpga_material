# 1.3.5 Đo Cao Độ Tiếng Nói ($F_0$ / Pitch): Từ Bản Chất Praat Đến Vi Kiến Trúc FPGA

> **$\blacktriangleright$ MỤC TIÊU HỌC TẬP**
>
> Mục 1.3 đã biến 400 mẫu áp suất không khí thành 80 con số Log-Mel để phục vụ các mạng nơ-ron nhận dạng từ khóa. Nhưng các con số đó hoàn toàn câm lặng trước một đặc trưng sinh lý học cơ bản của con người: **Cao độ (Pitch / Tần số cơ bản $F_0$)** — tần số rung của dây thanh quản. Mục này giải thích tại sao không thể dùng phổ STFT để đo $F_0$, bóc tách bản chất giải thuật tự tương quan thời gian theo tinh thần mã nguồn Praat (`Sound_to_Pitch.cpp`, Boersma 1993), tối giản hóa các phép toán giải tích phức tạp thành các khối phần cứng thân thiện (chỉ dùng nhân-cộng và so sánh), và định lượng tài nguyên silicon trên kit FPGA DE10-Standard (Intel Cyclone V).

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
       PHẦN CỨNG (FPGA DE10-Standard)           |       BIÊN        |       PHẦN MỀM MÁY CHỦ (SERVER)
                                                |                   |
  +---------------------------------------+     |                   |
  | Tệp WAV hoặc luồng I2S từ mic (16 kHz)|     |                   |
  +-------------------+-------------------+     |                   |
                      |                         |                   |
                      v                         |                   |
  +---------------------------------------+     |                   |
  |     HPF 60 Hz + Cắt khoảng lặng       |     |                   |
  |             (Mục 1.1.5)               |     |                   |
  +-------------------+-------------------+     |                   |
                      |                         |                   |
                      v                         |                   |
  +---------------------------------------+     |                   |
  |       Rẽ hai nhánh song song          |     |                   |
  +---------+-------------------+---------+     |                   |
            |                   |               |                   |
            v                   v               |                   |
  +-------------------+ +---------------+       |                   |
  |Nhánh 1: Mục 1.3   | |Nhánh 2: M.1.3.5|      |                   |
  |STFT 80 dải Log-Mel| |Tự tương quan  |      |                   |
  |Khung 25ms, b.10ms | |F0, 40ms/10ms  |      |                   |
  +---------+---------+ +-------+-------+       |                   |
            |                   |               |                   |
            v                   v               |                   |
     Ma trận Mel           Mảng cao độ          |   Shared Folder   |
     mel_80.bin           pitch_f0.bin          | (mỗi tệp 1 câu,   |
    (80 x N khung)      (1 giá trị/10ms)  ----->|  chung mốc t = 0) |---> Căn chỉnh từ + Pearson r
            |                   |               |                   |      (không chạy Praat)
            +-------------------+               |                   |             ^
            |                                   |                   |             |
            +------------------------------------------------------------> Whisper / Forced Align / DTW
                                                |                   |      trên nhánh Mel
                                                |                   |      => mốc từ (w_start, w_end)
```

*Hình 1.3.5a: Kiến trúc triển khai tổng thể: FPGA Edge Node tính cả hai nhánh đặc trưng và ghi ra thư mục dùng chung; máy chủ chỉ còn nhiệm vụ nhận dạng, căn chỉnh và chấm điểm.*

**Đọc Hình 1.3.5a (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Cột trái — Phần cứng (FPGA DE10-Standard):** Mọi phép biến đổi tín hiệu đều nằm ở đây. Tệp WAV hoặc luồng I$^2$S đi qua HPF 60 Hz và bộ cắt lặng của Mục 1.1.5 trước khi được rẽ vào hai nhánh chạy song song trên cùng một chip. Hai nhánh không tranh chấp tài nguyên vì nhánh Mel dùng bộ nhân FFT còn nhánh Pitch dùng một bộ MAC đơn, như đã hạch toán ở Mục 5.
2. **Nhánh 1 (Mục 1.3):** Sinh ma trận 80 dải Log-Mel với cửa sổ 25 ms và bước 10 ms. Đầu ra này là **đầu vào sẵn sàng** cho bộ mã hóa Whisper, hoặc được ghi ngược thành tệp WAV 16 kHz đã lọc sạch để gọi API Whisper từ xa.
3. **Nhánh 2 (Mục 1.3.5):** Sinh mảng cao độ một giá trị mỗi 10 ms (`pitch_f0.bin`). Đây là toàn bộ những gì máy chủ cần cho ngữ điệu, và nó đã được tính xong **trước khi** dữ liệu rời khỏi bo mạch.
4. **Cột giữa — Thư mục dùng chung (Shared Folder):** Là ranh giới hợp đồng giữa hai thế giới. FPGA chỉ ghi, máy chủ chỉ đọc, nên không bên nào phải biết định dạng bộ nhớ của bên kia. Mỗi câu một cặp tệp, kèm quy ước chung rằng mốc $t = 0$ là mẫu đầu tiên sau khi cắt lặng.
5. **Cột phải — Máy chủ:** Chạy mô hình nhận dạng hoặc căn chỉnh trên nhánh Mel để lấy mốc thời gian từng từ, rồi ghép trực tiếp mảng `pitch_f0.bin` vào các mốc đó để tính Pearson $r$. **Máy chủ không chạy Praat**, vì phép đo cao độ đã hoàn tất trên FPGA.

**Vì sao ranh giới lại đặt ở đây:** Có một lý do kỹ thuật chứ không phải thẩm mỹ. Phép đo cao độ là phép tính **cố định** về mặt cấu trúc: cùng một khung 640 mẫu luôn cho cùng một kết quả, không phụ thuộc mô hình ngôn ngữ, không cần cập nhật khi đổi phiên bản Whisper. Phép nhận dạng thì ngược lại: nó thay đổi mỗi lần có mô hình mới. Đặt phép tính bất biến lên silicon và phép tính hay thay đổi lên máy chủ nghĩa là nâng cấp mô hình không phải đụng đến bitstream, và một kit FPGA rẻ có thể phục vụ nhiều phiên bản mô hình khác nhau theo thời gian. Đây cũng là lý do đường biên trong hình được vẽ bằng nét đứt: nó là ranh giới **hợp đồng dữ liệu**, không phải ranh giới vật lý của một sản phẩm cụ thể.

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

> **$\blacktriangleright$ HỎI – ĐÁP TƯ DUY: Khi đang nói, làm sao dây thanh biết trước tương lai để lặp lại mẫu $x[n + T_0]$?**
>
> Nếu đọc $x[n] \approx x[n + T_0]$ như "mẫu hiện tại bằng mẫu tương lai", trực giác sẽ vấp ngay: người nói đâu có biết trước mẫu tiếp theo để bắt buộc nó lặp lại. **Cơ thể hoàn toàn không cần biết tương lai.** Câu đúng là dạng nhân quả: **$x[n] \approx x[n - T_0]$** — mẫu lúc này giống mẫu đúng một chu kỳ trước. Phép tự tương quan chỉ **đo** mức lặp lại đó; nó không bắt tín hiệu phải lặp lại. Hai lý do vật lý giải thích vì sao sự lặp lại xảy ra mà không cần tương lai:
>
> 1. **Dây thanh là một dao động cơ tự kích.** Luồng không khí từ phổi làm áp suất vùng thanh môn tụt xuống (hiệu ứng Bernoulli), kéo hai mép dây thanh hút vào nhau, cắt dòng khí rồi lại bung ra. Mỗi lần bung là một xung, và dao động này có khối lượng – độ đàn hồi riêng nên tự giữ một nhịp đều, giống dây đàn gảy xong vẫn rung theo tần số của chính nó. Xung vừa phát ra **đã định sẵn** xung kế tiếp; không có tương lai nào phải biết trước.
> 2. **Bộ máy phát âm thay đổi rất chậm so với nhịp rung.** Lưỡi, môi, hàm cần khoảng $50\text{--}100\text{ ms}$ mới đổi được một âm tiết; trong một khung $40\text{ ms}$ ($640$ mẫu) hình dạng ống cộng hưởng gần như đứng yên. Vì thế hai chu kỳ liền nhau đi qua **cùng một bộ lọc**, nên cùng bị bóp méo giống nhau và trông giống nhau.
>
> **Khi nào giả thiết này sụp đổ?** (a) Âm vô thanh như /s/, /f/: không có dây thanh rung, tín hiệu gần như nhiễu ngẫu nhiên, không có chu kỳ. (b) Chuyển âm nhanh: đầu khung là một nguyên âm, cuối khung đã sang nguyên âm khác, bộ lọc không còn đứng yên nữa. Đó là lý do Praat đo cao độ theo từng khung ngắn và ghép lại bằng đường bao trơn, chứ không đo một lần cho cả câu.

- $\tau$ (tau): Độ trễ (lag), là số mẫu mà ta dịch trượt bản sao tín hiệu so với bản gốc, với $\tau$ là số nguyên không âm ($\tau \ge 0$).
- $F_0$: Tần số cơ bản (Pitch / Cao độ), xác định qua hệ thức: $F_0 = f_s / T_0$ (với $f_s$ là tần số lấy mẫu).

Nguyên lý của phép tự tương quan rất trực quan: **Tạo ra một bản sao của khung tín hiệu, trượt bản sao đi một khoảng trễ $\tau$ mẫu, sau đó nhân từng cặp mẫu tương ứng và tính tổng dồn lại.** Biểu thức toán học này được gọi là **tổng tự tương quan** (hoặc **tổng tích các cặp mẫu**):

$$\mathcal{R}_x[\tau] = \sum_{n=0}^{L - 1 - \tau} x[n] \cdot x[n + \tau]$$

**Nguồn gốc cận trên $L - 1 - \tau$ và số lượng cặp mẫu:** Trong công thức trên, bản gốc lấy mẫu tại chỉ số $n$, còn bản trượt lấy mẫu tại chỉ số $n + \tau$. Do khung dữ liệu trong bộ nhớ chỉ lưu trữ các phần tử từ chỉ số $0$ đến $L - 1$, mẫu của bản trượt muốn hợp lệ (không truy xuất tràn mảng) thì chỉ số phải thỏa mãn điều kiện biên:

$$n + \tau \le L - 1 \iff n \le L - 1 - \tau$$

Do đó, chỉ số $n$ chỉ có thể chạy từ $0$ đến $L - 1 - \tau$. Từ điều kiện này rút ra các ý nghĩa bản chất:
1. Số lượng cặp mẫu được nhân với nhau là: $(L - 1 - \tau) - 0 + 1 = \mathbf{L - \tau\text{ cặp}}$.
2. Con số "$-1$" xuất phát từ việc mảng đánh số từ 0 (phần tử cuối cùng là $L - 1$, không phải $L$).
3. Đại lượng "$-\tau$" xuất hiện do khi trượt đi $\tau$ mẫu, đúng $\tau$ mẫu ở đuôi của bản trượt bị thò ra ngoài phạm vi lưu trữ của khung $L$ mẫu (Hình 1.3.5b, Panel A).
4. Cận trên $L - 1 - \tau$ hoàn toàn là điều kiện biên kỹ thuật của khung dữ liệu hữu hạn, **đây KHÔNG phải là phép trừ phần đối xứng**.

**Cơ chế theo dấu của tổng tự tương quan trong 3 trường hợp:** Dấu và độ lớn của tổng tự tương quan $\mathcal{R}_x[\tau]$ được quyết định bởi tính đồng pha giữa bản gốc và bản trượt:
1. **Khi $\tau = 0$ (Trùng khớp):** Bản sao nằm trùng khít lên bản gốc ($x[n]$ nhân với chính nó). Từng tích cặp mẫu trở thành bình phương: $x[n] \cdot x[n] = x^2[n] \ge 0$. Mọi số hạng đều không âm, cộng dồn tạo thành:
   $$\mathcal{R}_x[0] = \sum_{n=0}^{L-1} x^2[n] = E_{\text{frame}}$$
   chính là tổng năng lượng tức thời của toàn khung $L$ mẫu. Đây là giá trị **cực đại toàn cục** của hàm tự tương quan.
2. **Khi $0 < \tau < T_0$ (Lệch pha):** Bản sao bị lệch pha so với bản gốc. Các đỉnh sóng dương ($+$) của bản này rơi vào sườn sóng hoặc đáy sóng âm ($-$) của bản kia. Phép nhân giữa mẫu dương và mẫu âm sinh ra tích âm: $(+) \cdot (-) < 0$. Khi cộng dồn, các tích âm và dương triệt tiêu lẫn nhau, khiến tổng tự tương quan sụt giảm rõ rệt.
3. **Khi $\tau = T_0$ (Đúng một chu kỳ cơ bản):** Sóng âm tuần hoàn lặp lại đúng một chu kỳ. Đỉnh dương của bản sao trượt đúng vào đỉnh dương của bản gốc: $(+) \cdot (+) > 0$. Đáy âm của bản sao cũng trượt đúng vào đáy âm của bản gốc: $(-) \cdot (-) > 0$. Hầu hết các cặp mẫu đều cho tích dương, khiến tổng tự tương quan vọt lên tạo thành một **đỉnh cực đại cục bộ thứ nhất** tại $\tau^* = T_0$ (Hình 1.3.5b, Panel B).

*Tự tương quan đo tính tuần hoàn (lặp lại theo chu kỳ), không đo tính đối xứng; sóng tiếng nói không đối xứng nhưng tuần hoàn.*

**Vì sao phải bỏ qua $\tau = 0$ và thiết lập dải tìm kiếm $[\tau_{\text{min}}, \tau_{\text{max}}]$:** Mặc dù $\mathcal{R}_x[0]$ luôn đạt giá trị lớn nhất, ta bắt buộc phải loại bỏ $\tau = 0$ và vùng lân cận khi tìm kiếm cao độ. Do tính liên tục của sóng âm thanh (quán tính của không khí và dây thanh), các mẫu liền kề nhau có độ tương quan rất cao, tạo thành một sườn dốc đi xuống rất dốc từ $\mathcal{R}_x[0]$. Nếu quét $\text{argmax}$ từ $\tau = 0$, thuật toán sẽ luôn chọn nhầm $\tau = 0$ hoặc $\tau = 1$.

Dải tần số cơ bản của giọng nói con người (từ giọng nam trầm nhất đến giọng nữ cao và trẻ em) nằm trong khoảng $F_0 \in [75\text{ Hz}, 600\text{ Hz}]$. Tại tần số lấy mẫu chuẩn $f_s = 16.000\text{ Hz}$, ta đổi dải tần số này sang dải độ trễ mẫu $\tau$:

$$\tau_{\text{min}} = \left\lceil \frac{f_s}{F_{\text{ceiling}}} \right\rceil = \left\lceil \frac{16.000}{600} \right\rceil = \lceil 26{,}67 \rceil = \mathbf{27\text{ mẫu}}$$

$$\tau_{\text{max}} = \left\lfloor \frac{f_s}{F_{\text{floor}}} \right\rfloor = \left\lfloor \frac{16.000}{75} \right\rfloor = \lfloor 213{,}33 \rfloor = \mathbf{213\text{ mẫu}}$$

Vì vậy, không gian tìm kiếm cực đại chỉ quét trong dải hợp lệ $\tau \in [27, 213]$ gồm đúng $213 - 27 + 1 = \mathbf{187\text{ giá trị lag}}$.

**Ví dụ số nguyên chuỗi tính toán:** Giả sử hệ thống xử lý tín hiệu tại $f_s = 16.000\text{ Hz}$:
- Nếu thuật toán tìm được đỉnh cực đại tại $\tau^* = 160\text{ mẫu} \implies F_0 = \frac{16.000}{160} = \mathbf{100\text{ Hz}}$ (giọng nam trầm).
- Nếu thuật toán tìm được đỉnh cực đại tại $\tau^* = 133\text{ mẫu} \implies F_0 = \frac{16.000}{133} \approx \mathbf{120{,}3\text{ Hz}}$ (giọng nam trung).

```
Panel A: Cơ chế chỉ số mảng: Bản gốc x[n] và Bản trượt x[n + tau] (cận trên L - 1 - tau)
Bản gốc x[n]:   | 0 | 1 | 2 | ... | L - 1 - tau | ... | L - 1 |
Bản trượt x[n+tau]:         | 0 | ... | L - 1 - 2tau| ... | L - 1 - tau | [ tau mẫu thò ra ngoài ]
                            <------------------------------------------->
                               Vùng nhân hợp lệ: n in [0, L - 1 - tau] (L - tau cặp)

Panel B: Đồ thị hàm tự tương quan thô R_x[tau] và dải quét [27, 213] mẫu
R_x[tau]
   ^
R[0]| * (Cực đại toàn cục: Năng lượng khung)
    |  \
    |   \ (Sườn dốc quán tính âm học: bỏ qua vùng tau < 27)
    |    \
    |     \_______      * tau* = 133 mẫu (F0 = 120.3 Hz)
    |             \    / \
    |              \__/   \______
    +-----+---------+---------------+------------------------> tau (mẫu)
    0     |         27             213
          0        tau_min        tau_max
                   <-------------->
                     Dải tìm kiếm hợp lệ (187 lag)
```

*Hình 1.3.5b: Cơ chế chỉ số mảng giới hạn khung $(L - 1 - \tau)$ và đồ thị hàm tự tương quan thô $\mathcal{R}_x[\tau]$ trong dải quét $[27, 213]$ mẫu.*

**Đọc Hình 1.3.5b (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Bản gốc $x[n]$ (Thanh phía trên):** Thể hiện mảng dữ liệu mẫu âm thanh của khung $L = 640$ mẫu được lưu tuần tự trong bộ nhớ, có chỉ số $n$ chạy từ $0$ đến $L - 1$ ($0$ đến $639$). Đoạn chỉ số $n \in [0, L - 1 - \tau]$ có thể bắt cặp.
2. **Panel A — Bản trượt $x[n+\tau]$ (Thanh phía dưới):** Thể hiện bản sao tín hiệu bị dịch trượt sang phải một khoảng trễ $\tau$ mẫu. Mẫu đầu tiên của bản trượt bắt đầu tại chỉ số $\tau$, và mẫu có chỉ số $L - 1$ của bản gốc lúc này đối diện với chỉ số $L - 1 - \tau$ của bản trượt.
3. **Panel A — Độ trễ $\tau$ mẫu:** Đo khoảng cách dịch chuyển giữa điểm gốc $0$ của bản gốc và điểm bắt đầu của bản trượt.
4. **Panel A — Khối nét đứt ($\tau$ mẫu thò ra ngoài):** Khi dịch trượt sang phải một khoảng $\tau$, đúng $\tau$ mẫu ở phần đuôi của bản trượt bị tràn ra ngoài phạm vi lưu trữ của khung $L$ mẫu. Các mẫu này không có mẫu tương ứng của bản gốc để nhân.
5. **Panel A — Vùng nhân hợp lệ:** Giới hạn trong khoảng chỉ số $n \in [0, L - 1 - \tau]$, tương ứng với đúng $L - \tau$ cặp mẫu có đủ cả hai thành phần $x[n]$ và $x[n+\tau]$ nằm trọn vẹn trong bộ nhớ khung. Điều này minh chứng trực quan cho điều kiện biên $n + \tau \le L - 1 \iff n \le L - 1 - \tau$ và giải thích vì sao cận trên của tổng tự tương quan dừng lại ở $L - 1 - \tau$.
6. **Panel B — Chấm tại $\tau = 0$ ($\mathcal{R}_x[0] = E_{\text{frame}}$):** Biểu diễn cực đại toàn cục của hàm tự tương quan, tương ứng với năng lượng tức thời của toàn bộ khung $L$ mẫu (khi hai bản trùng khít hoàn toàn, mọi tích cặp đều là bình phương không âm $x^2[n] \ge 0$).
7. **Panel B — Vùng $\tau < 27$ (Sườn dốc quán tính âm học):** Đoạn đồ thị sụt dốc rất dốc ngay sau điểm $\tau = 0$. Sự sụt dốc này phản ánh tính tương quan rất cao giữa các mẫu âm thanh liền kề do quán tính chuyển động của dây thanh quản và cột không khí. Vùng này bị thuật toán loại bỏ triệt để để không bao giờ chọn nhầm đỉnh tại $\tau = 0$ hay $\tau = 1$.
8. **Panel B — Đáy suy giảm gần $\tau_{\min}$:** Vùng trũng của đồ thị ngay trước mốc $\tau_{\min} = 27$ mẫu, nơi tương quan quán tính âm học đã tắt hẳn và bắt đầu chuyển sang vùng tìm kiếm tính tuần hoàn của giọng nói.
9. **Panel B — Đỉnh tại $\tau^* = 133$ mẫu (Cực đại cục bộ thứ nhất):** Vị trí bản trượt dịch đúng bằng chu kỳ rung cơ bản $T_0$ của dây thanh quản. Tại đây các đỉnh sóng dương và đáy sóng âm trùng pha nhau, làm tổng tích dồn vọt lên đỉnh cực đại cục bộ trong dải quét. Tần số cơ bản được tính chính xác bằng $F_0 = f_s / \tau^* = 16.000 / 133 \approx 120{,}3\text{ Hz}$ (giọng nam trung).
10. **Panel B — Dải quét $\tau \in [27, 213]$ (Dải tìm kiếm hợp lệ):** Không gian quét gồm đúng 187 giá trị lag, được giới hạn bởi $\tau_{\min} = 27$ mẫu ($F_{\text{ceiling}} = 600\text{ Hz}$) và $\tau_{\max} = 213$ mẫu ($F_{\text{floor}} = 75\text{ Hz}$).

---

## 3. Cắt Khung, Chuẩn Hóa Cửa Sổ và Giải Phẫu 10 Tham Số Praat

### A. Vì sao đổi sang cửa sổ Hanning và độ dài $L = 640$ mẫu?
Ở Mục 1.2 và 1.3, chuỗi tiền xử lý dùng khung $L = 400$ mẫu ($25\text{ ms}$) kết hợp cửa sổ Hamming. Thời lượng $25\text{ ms}$ là tiêu chuẩn vàng để trích xuất 80 dải Log-Mel vì đặc tính âm học của khẩu hình miệng giữ trạng thái bán dừng (quasi-stationary) trong khoảng 20--30 ms. Tuy nhiên, khi bước sang bài toán đo cao độ $F_0$, ta bắt buộc phải thay đổi cả độ dài khung lẫn dạng cửa sổ:
1. **Độ dài khung $L = 640$ mẫu ($40\text{ ms}$):** Theo quy tắc của Boersma (1993) trong Praat, khung phân tích cao độ phải chứa **tối thiểu 3 chu kỳ** của tần số thấp nhất cần đo ($\text{pitch\_floor} = 75\text{ Hz}$). Chu kỳ dài nhất là $T_{\text{max}} = 16.000 / 75 \approx 213{,}33\text{ mẫu}$ ($13{,}33\text{ ms}$). Khung phải dài ít nhất:
   $$T_{\text{frame}} \ge 3 \times T_{\text{max}} = 3 \times 13{,}33\text{ ms} = 40\text{ ms} \implies L = 16.000 \times 0{,}040 = \mathbf{640\text{ mẫu}}$$
   Nếu dùng khung $25\text{ ms}$ ($400$ mẫu) như STFT, một giọng nam trầm $75\text{ Hz}$ chỉ kịp lặp lại chưa đầy 2 chu kỳ. Tại độ trễ lớn $\tau \approx 213$, số cặp mẫu còn lại trong khung chỉ là $400 - 213 = 187$ mẫu — quá ít để triệt tiêu các dao động ngẫu nhiên, khiến đỉnh tương quan bị chìm hoàn toàn trong nhiễu.
2. **Cửa sổ Hanning thay vì Hamming:** Cửa sổ Hamming có hai đầu mút nâng cao nhân tạo ($w[0] = w[L-1] = 0{,}08$), gây ra sự gián đoạn bước nhảy biên độ nhỏ ở hai biên khung. Ngược lại, cửa sổ Hanning triệt tiêu hoàn toàn về $0$ ở hai đầu biên:
   $$w[n] = 0{,}5 - 0{,}5 \cos\left(\frac{2\pi n}{L - 1}\right), \quad n = 0, 1, \dots, L - 1$$
   giúp triệt tiêu dứt điểm hiệu ứng rò rỉ phổ và triệt tiêu năng lượng tại các biên trượt.

### B. Bản chất suy hao do cửa sổ Hanning và cơ chế bù $C[\tau]$
Khi áp dụng cửa sổ Hanning lên khung tín hiệu $x[n]$, ta thu được tín hiệu sau khi nhân cửa sổ: $x_{\text{win}}[n] = x[n] \cdot w[n]$. Tổng tự tương quan trên tín hiệu này thực chất là:

$$\mathcal{R}_x[\tau] = \sum_{n=0}^{L-1-\tau} \big(x[n]\,x[n+\tau]\big)\big(w[n]\,w[n+\tau]\big)$$

và vì $w[n]\,w[n+\tau] \approx \mathcal{R}_w[\tau]/L$ theo nghĩa trung bình trên toàn khung, ta ghi gọn mức đo được của âm thanh thật là:

$$r_{\text{thật}}[\tau] = \frac{\mathcal{R}_x[\tau]}{\mathcal{R}_w[\tau]}$$

**Bù lại cái khuôn: nhân với một hằng số lấy từ ROM.** Ở $\tau = 0$ cái khuôn còn nguyên, nên mức đo được đúng bằng mức thật. Ở độ trễ lớn, cái khuôn chỉ còn một phần, khiến mức đo bị dìm xuống. Muốn lấy lại mức thật, ta chia cho phần khuôn còn lại. Phần khuôn còn lại đã được đo sẵn, chỉ phụ thuộc vào $\tau$ và cửa sổ, **không phụ thuộc vào tín hiệu**. Vì vậy ta tính trước một **hệ số phóng đại** và nạp vào ROM:

$$C[\tau] = \frac{\mathcal{R}_w[0]}{\mathcal{R}_w[\tau]} \quad (\ge 1,\ \text{tăng dần theo } \tau)$$

Giá trị bù thực tế dùng để ra quyết định là:

$$\mathcal{R}_{\text{comp}}[\tau] = \mathcal{R}_x[\tau] \cdot C[\tau]$$

và chia cho năng lượng khung để so với ngưỡng thanh tính:

$$\frac{\mathcal{R}_{\text{comp}}[\tau^*]}{\mathcal{R}_x[0]} \ge \theta_{\text{voice}} = 0{,}45 \iff \mathcal{R}_{\text{comp}}[\tau^*] \ge 0{,}45 \cdot \mathcal{R}_x[0]$$

Trên FPGA, phép so sánh này chỉ cần **một phép nhân** với hệ số lấy từ bảng tra và **một phép so sánh số nguyên**; không cần bộ chia.

> **$\blacktriangleright$ BẢNG DỊCH NHANH: 4 KÝ HIỆU CỐT LÕI SANG HÌNH ẢNH QUẢ NÚI**
>
> | Ký hiệu | Nó là gì trong hình ảnh quả núi | Ví dụ số tại $\tau = 133$ |
> |---|---|---|
> | $\mathcal{R}_w[\tau]$ | Diện tích chồng nhau của **hai vỏ núi rỗng** (chỉ có cửa sổ, không có âm thanh). $\tau = 0$ là chồng khít, $\tau$ lớn thì chồng hẹp và thấp. | $0{,}40$ — vỏ còn $40\%$ ($\approx 60\%$ đã hụt) |
> | $\mathcal{R}_x[\tau]$ | Tự tương quan của **âm thanh thật** đã bị cái khuôn đè lên. Mức đo thô bị dìm theo đúng phần vỏ còn lại. | $0{,}90 \times 0{,}40 = 0{,}36$ |
> | $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ | **Hệ số phóng đại** lấy từ ROM: chia cho phần vỏ còn lại để lấy lại mức thật. | $1{,}0 / 0{,}40 = 2{,}5$ |
> | $\mathcal{R}_{\text{comp}}[\tau] = \mathcal{R}_x[\tau] \cdot C[\tau]$ | Mức thật sau khi kéo vỏ núi về đủ chiều cao, đem so với ngưỡng. | $0{,}36 \times 2{,}5 = 0{,}90$ |
>
> Đọc bảng theo một chiều: vỏ hụt → mức đo hụt theo đúng tỷ lệ đó → nhân với nghịch đảo của tỷ lệ → mức thật trở lại.

> **$\blacktriangleright$ HỎI – ĐÁP TƯ DUY: NGHỊCH LÝ NHÂN NGHỊCH ĐẢO — vì sao $\mathcal{R}_x[\tau] \cdot C[\tau]$ không bằng $1$?**
>
> **Câu hỏi:** Hệ số bù là $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$, còn tín hiệu là $\mathcal{R}_x[\tau]$. Nhân hai thứ "nghịch đảo" với nhau, sao kết quả không ra $1$?
>
> **Trả lời:** Hai đại lượng này **không phải nghịch đảo của nhau**. Mẫu số của $C[\tau]$ là tự tương quan của **cửa sổ**, còn $\mathcal{R}_x[\tau]$ là tự tương quan của **tín hiệu âm thanh đã nhân cửa sổ**. Thực chất:
>
> $$\mathcal{R}_x[\tau] \approx (\text{mức giống thật của giọng tại }\tau) \times \mathcal{R}_w[\tau]$$
>
> Tức là $\mathcal{R}_x[\tau]$ **đã mang sẵn** phần vỏ bên trong nó. Nhân thêm $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ là **rút** phần vỏ đó ra, còn lại mức giống thật nhân với $\mathcal{R}_w[0]$ (một hằng số).
>
> **Tính từng bước với một khung giọng nam $120\text{ Hz}$ ($\tau = 133$ mẫu), ngưỡng $\theta_{\text{voice}} = 0{,}45$:**
> 1. Vỏ núi còn: $\mathcal{R}_w[133] / \mathcal{R}_w[0] = 0{,}40$. Ở độ trễ này cái khuôn đã hụt $60\%$.
> 2. Mức đo thô: giọng thật giống nhau $0{,}90$ ở một chu kỳ, nên $\mathcal{R}_x[133] / \mathcal{R}_x[0] = 0{,}90 \times 0{,}40 = 0{,}36$.
> 3. So thẳng với ngưỡng: $0{,}36 < 0{,}45$ ⇒ thuật toán **nhầm là vô thanh**, mất cao độ. Đây chính là lỗi nghịch lý: giọng rất đều nhưng vẫn bị bỏ.
> 4. Phóng đại: $C[133] = 1{,}0 / 0{,}40 = 2{,}5$.
> 5. Sau bù: $0{,}36 \times 2{,}5 = 0{,}90$, vượt ngưỡng $0{,}45$ rõ ràng ⇒ bắt đúng $F_0$.

```
Panel A: Cửa sổ Hanning (quả núi) và bản sao trượt tau mẫu
w[n]       /\                  w[n+tau]     /\
          /  \                             /  \
_________/____\_________          ________/____\________
      Khung gốc L=640                 Trượt sang phải tau mẫu
                                      Đuôi thò ra ngoài khung: tau mẫu

Panel B: Vùng tích các cặp mẫu giảm dần theo độ trễ
tau = 0:   640 cặp mẫu hữu hiệu
tau = 80:  560 cặp mẫu hữu hiệu
tau = 160: 480 cặp mẫu hữu hiệu

Panel C: Khung 200 Hz (T0 = 80 mẫu): Đỉnh 1T0 và 2T0 trước và sau khi bù C[tau]
R / R_x[0]
 1.0 +
     |
 0.8 +
     |                  * 1T0 (0.47) [Đã bù C[tau], vượt ngưỡng]
 0.6 +                   \
     |                    \          * 2T0 (0.35) [Đã bù C[tau]]
 0.45+ - - - - - - - - - - \ - - - -/ - - - - - - - -  Ngưỡng thanh tính 0.45
     |          * 1T0 (0.42)\      /
 0.3 +           (chưa bù)   \    /  * 2T0 (0.23) (chưa bù)
     |                        \__/
 0.0 +------+--------+--------------+--------------> tau
     0     27       80             160          213
                    1T0            2T0
```

*Hình 1.3.5c: Hiện tượng co hẹp vùng tích các cặp mẫu và vai trò của hệ số bù suy hao cửa sổ $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ theo Boersma (1993).*

**Đọc Hình 1.3.5c (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Quả núi thứ nhất:** Khung $L = 640$ mẫu sau khi nhân cửa sổ Hanning có dạng một quả núi: hai chân chạm $0$, đỉnh ở giữa.
2. **Panel A — Quả núi thứ hai:** Bản sao của quả núi thứ nhất, trượt sang phải đúng $\tau$ mẫu.
3. **Panel A — "Phần thò ra":** $\tau$ mẫu ở đuôi quả thứ hai nằm ngoài cửa sổ, không có mẫu nào của quả thứ nhất đối diện để nhân. Cùng lúc, phần chồng nhau hẹp lại còn $L - \tau$ cặp và diện tích chồng nhau chính là $\mathcal{R}_w[\tau]$.
4. **Panel B — Số cặp giảm:** $\tau = 0$: $640$ cặp; $\tau = 80$: $560$ cặp; $\tau = 160$: $480$ cặp. Con số $L - \tau$ này là nguyên nhân hình học đầu tiên khiến tổng tương quan thô sụt theo $\tau$.
5. **Panel C — Trục tung $R/R_x[0]$ và ngưỡng $0{,}45$:** Khung $F_0 = 200\text{ Hz}$ ($T_0 = 80$ mẫu). Đường nét đứt ngang là ngưỡng thanh tính; trục hoành đánh dấu bốn mốc $27$, $80$, $160$, $213$.
6. **Panel C — Đường chưa bù:** Hai đỉnh $1T_0$ ($\tau = 80$) và $2T_0$ ($\tau = 160$) chỉ đạt $0{,}42$ và $0{,}23$; cả hai đều **dưới** ngưỡng $0{,}45$, nên khung bị gán vô thanh.
7. **Panel C — Đường đã bù $C[\tau]$:** Nhân với $C[80] = 1{,}11$ và $C[160] = 1{,}52$, hai đỉnh lên khoảng $0{,}47$ và $0{,}35$; cả hai đều **vượt** ngưỡng.
8. **Panel C — Thêm `octave_cost = 0,01`:** Đỉnh $1T_0$ (80 mẫu) thắng an toàn đỉnh $2T_0$ (160 mẫu).

### B'. Hai đỉnh $1T_0$ và $2T_0$: vì sao bù hệ số lại đẩy đỉnh xa lên, và `octave_cost` dọn nốt tàn dư

Một giọng có chu kỳ $T_0$ sẽ lặp lại không chỉ sau một chu kỳ mà còn sau $2T_0$, $3T_0$… nên hàm tự tương quan có **nhiều đỉnh**. Chọn nhầm đỉnh $2T_0$ là đọc cao độ thành $F_0/2$: giọng $200\text{ Hz}$ bị ghi thành $100\text{ Hz}$, tức **rơi đúng một quãng tám** (octave error).

- **Vì sao sau khi bù, hệ số lại đẩy đỉnh xa lên mạnh hơn:** $C[\tau]$ tăng dần theo $\tau$; đỉnh ở $2T_0$ nằm xa hơn nên có $C[2T_0] > C[T_0]$. Hệ số bù vì vậy **nâng đỉnh $2T_0$ nhiều hơn** đỉnh $T_0$ và có thể kéo hai đỉnh về ngang nhau, tạo nguy cơ lỗi quãng tám thật sự.
- **Praat chặn nguy cơ đó bằng `octave_cost = 0,01`:** Với mỗi bậc độ trễ tăng gấp đôi, Praat **trừ đi $0{,}01$** khỏi điểm của đỉnh. Đỉnh $2T_0$ bị trừ một lần $0{,}01$ so với đỉnh $T_0$, nên đỉnh $1T_0$ luôn **thắng an toàn** khi hai đỉnh xấp xỉ nhau.

### C. Giải phẫu 10 tham số chuẩn của Praat dưới góc nhìn mã nguồn (`Sound_to_Pitch.cpp`)

Mã nguồn mở C++ của Praat do Paul Boersma xây dựng chứa đựng triết lý thiết kế chuẩn mực đã qua hơn 30 năm kiểm chứng. Dưới đây là giải phẫu chi tiết 10 tham số đầu vào của hàm `Sound_to_Pitch_ac`:

1. **`time_step = 0,01 s` ($10\text{ ms} = 160\text{ mẫu}$):** Bước nhảy trượt khung ($\Delta t_{\text{hop}}$). Trong Praat, nếu người dùng truyền `time_step = 0.0` (Auto), mã nguồn tự động gán $\Delta t_{\text{hop}} = \frac{0{,}75}{\text{pitch\_floor}} = \frac{0{,}75}{75} = 0{,}01\text{ s}$ (ứng với 4 khung phân tích gối lên nhau trên mỗi độ dài 3 chu kỳ). Ta khóa cứng tường minh $0{,}01\text{ s}$ để giữ tốc độ 100 khung/s đồng bộ với luồng Log-Mel.
2. **`pitch_floor = 75 Hz`:** Giới hạn đáy cao độ. Quyết định hai đại lượng phần cứng cốt lõi: (a) Độ trễ quét tối đa $\tau_{\text{max}} = \lfloor f_s / 75 \rfloor = 213\text{ mẫu}$; (b) Độ dài cửa sổ phân tích tối thiểu $L = \frac{3}{\text{pitch\_floor}} \times f_s = 0{,}04\text{ s} \times 16.000 = 640\text{ mẫu}$.
3. **`pitch_ceiling = 600 Hz`:** Giới hạn trần cao độ (bao phủ trọn vẹn cả giọng nữ cao và trẻ em). Quyết định độ trễ quét tối thiểu $\tau_{\text{min}} = \lceil f_s / 600 \rceil = 27\text{ mẫu}$. Mọi đỉnh tương quan ở $\tau < 27$ đều bị loại bỏ ngay lập tức như nhiễu tần số cao hoặc cực Formant.
4. **`very_accurate = off (False)`:** Cờ boolean quyết định loại cửa sổ và độ dài phân tích:
   - Khi `off` (Mặc định): Praat dùng cửa sổ **Hanning** dài **3 chu kỳ** ($3/\text{pitch\_floor} = 40\text{ ms} = 640\text{ mẫu}$).
   - Khi `on`: Praat chuyển sang cửa sổ **Gaussian** dài **6 chu kỳ** ($80\text{ ms} = 1.280\text{ mẫu}$) để dìm búp phụ xuống $-120\text{ dB}$. Chọn `very_accurate = off` trên FPGA là hoàn toàn phù hợp với thiết kế cửa sổ Hanning 640 mẫu, giúp giảm một nửa dung lượng BRAM và số phép tính MAC!
5. **`max_number_of_candidates = 15`:** Trong mỗi khung 10 ms, Praat không chỉ chọn 1 đỉnh cao nhất mà trích xuất tối đa **14 đỉnh cực đại cục bộ** của $r_x[\tau]$ cộng với **1 ứng viên Vô thanh (Unvoiced candidate)** (tổng $N_{\text{cand}} = 15$) để chuyển sang mạng lưới quy hoạch động Viterbi. *(Trên FPGA streaming: rút gọn về `max_candidates = 1`, tức dùng bộ so sánh lấy đỉnh cao nhất duy nhất cục bộ).*
6. **`silence_threshold = 0,03`:** Ngưỡng biên độ khoảng lặng so với biên độ đỉnh toàn cục của file ($I_{\text{local}} / I_{\text{max\_global}}$). Nếu một khung có năng lượng quá nhỏ ($< 3\%$ đỉnh toàn cục), khung đó bị nghi ngờ là khoảng lặng hoặc tiếng ồn nền phòng thu.
7. **`voicing_threshold = 0,45`:** Ngưỡng độ mạnh chu kỳ (Harmonicity). Trong code Boersma (Công thức 23), ứng viên Vô thanh (Unvoiced) được gán một điểm số cạnh tranh:
   $$R_{\text{unvoiced}} = \text{voicing\_threshold} + \max\left(0,\, 2 - \frac{I_{\text{local}} / I_{\text{max\_global}}}{\text{silence\_threshold} / (1 + \text{voicing\_threshold})}\right)$$
   Khi âm thanh đủ to, số hạng thứ hai bằng $0 \implies R_{\text{unvoiced}} = 0{,}45$. Một đỉnh hữu thanh muốn chiến thắng phải có tương quan chuẩn hóa $\ge 0{,}45$. Khi âm thanh rơi vào vùng khoảng lặng, $R_{\text{unvoiced}}$ vọt lên 2,45, ép khung đó nhận nhãn Unvoiced ($F_0 = 0$) bất chấp nhiễu nền tuần hoàn giả tạo!
8. **`octave_cost = 0,01` (trên mỗi quãng tám):** Hệ số thiên vị tần số cao nội khung (Local pitch-lag bias). Vì tín hiệu tuần hoàn ở $T_0$ cũng tuần hoàn ở $2T_0$ (tần số nửa $F_0/2$ — lỗi nhảy xuống quãng tám dưới), Praat trừ một khoản phạt tỉ lệ với logarit độ trễ:
   $$R_{\text{voiced}}[\tau] = r_x[\tau] - \text{octave\_cost} \times \log_2\left(\frac{\text{pitch\_ceiling}}{f_s / \tau}\right)$$
   Ở lag càng lớn ($\tau$ lớn, tức $F_0$ càng thấp), lượng trừ càng lớn, giúp đỉnh cơ bản thật $\tau = T_0$ thắng đỉnh bội số $\tau = 2T_0$. Trên FPGA, lượng phạt này được cộng trừ sẵn vào bảng tra ROM $C[\tau]$ mà không tốn mạch tính $\log_2$!
9. **`octave_jump_cost = 0,35`:** Trọng số phạt trong thuật toán Viterbi khi đường cao độ giữa hai khung liên tiếp bị nhảy vọt tần số:
   $$\text{Cost}_{\text{jump}}(F_{0, t-1} \to F_{0, t}) = \text{octave\_jump\_cost} \times \left|\log_2\left(\frac{F_{0, t}}{F_{0, t-1}}\right)\right| \times \left(\frac{0{,}01}{\Delta t_{\text{hop}}}\right)$$
   Nhờ mức phạt 0,35 cho mỗi quãng tám, Viterbi ưu tiên chọn chuỗi ứng viên tạo ra đường cong cao độ mượt mà.
10. **`voiced_unvoiced_cost = 0,14`:** Trọng số phạt trong Viterbi khi trạng thái chuyển từ Hữu thanh sang Vô thanh ($\text{Voiced} \leftrightarrow \text{Unvoiced}$), giúp ngăn hiện tượng đường Pitch bị đứt gãy chớp nháy ở ranh giới âm yếu.

### C'. Vì sao mỗi con số tham số lại là con số đó: cơ sở âm học của Tham số 6--10

**Tham số 6 — `silence_threshold = 0,03`: ngưỡng để nhiễu nền không tự khuếch đại chính nó.**
Khi một khung là khoảng lặng, năng lượng $\mathcal{R}_x[0]$ rất nhỏ. Nhưng phép chuẩn hóa lại chia cho chính năng lượng nhỏ đó: $r_x[\tau] = \mathcal{R}_x[\tau] / \mathcal{R}_x[0]$. Một tạp âm nền tuần hoàn rất yếu vẫn có thể đạt tỷ số $r_x[\tau] > 0{,}45$ sau khi chia, không phải vì nó mạnh, mà vì mẫu số đã bé tí.
Ngưỡng 0,03 chính là một mức SNR quy ra decibel:
$$20 \log_{10}(0{,}03) \approx -30{,}46\text{ dB}$$
Con số này trùng khớp với khoảng cách điển hình giữa giọng nói bình thường (khoảng $65\text{ dB SPL}$) và nền phòng yên tĩnh (khoảng $35\text{ dB SPL}$), tức đúng $30\text{ dB}$. Đó cũng là lý do `top_db = 30` của Librosa ở Phụ lục cho ra cùng một ngưỡng biên độ: $10^{-30/20} \approx 0{,}0316$.

**Tham số 7 — `voicing_threshold = 0,45`: mốc cân bằng giữa tuần hoàn và nhiễu.**
Khi phát âm /s/ hay /f/, biên độ rất lớn nhưng là nhiễu khí hỗn loạn. Thước đo chuẩn là Tỷ số Hài trên Nhiễu (Harmonics-to-Noise Ratio, HNR). Boersma (1993) nối HNR với hệ số tự tương quan chuẩn hóa $r$ bằng:
$$\text{HNR (dB)} = 10 \log_{10}\!\left(\frac{r}{1-r}\right)$$
Điểm cân bằng vật lý — năng lượng tuần hoàn đúng bằng năng lượng nhiễu ($\text{HNR} = 0\text{ dB}$) — ứng với $r = 0{,}50$. Praat chọn $r = 0{,}45$, tương ứng:
$$10 \log_{10}\!\left(\frac{0{,}45}{0{,}55}\right) \approx -0{,}87\text{ dB}$$
tức chấp nhận một khung mà nhiễu nhiều hơn phần tuần hoàn khoảng $0{,}9\text{ dB}$. Dung sai này giữ được các nguyên âm hơi khàn ở cuối câu mà không mở cửa cho phụ âm xát.

**Tham số 8 — `octave_cost = 0,01`: mức phạt nhỏ nhất còn đủ để phá thế hòa.**
Tín hiệu tuần hoàn ở $T_0$ cũng tuần hoàn ở $2T_0$, nên sau khi bù cửa sổ, hai đỉnh có thể hòa nhau. Quét toàn dải $75\text{--}600\text{ Hz}$ trên lưới 1 Hz (526 tần số) cho thấy:
- `octave_cost = 0`: $273 / 526$ tần số bị sai quãng tám (quá nửa dải sai do hai đỉnh hòa nhau).
- `octave_cost = 0.005`: $20 / 526$ còn sai ở vùng cao.
- `octave_cost = 0.01`: **0 / 526 sai (mặc định Praat, sạch hoàn toàn)**.
Con số 1% này cùng bậc với độ bất ổn chu kỳ tự nhiên của dây thanh (jitter điển hình cỡ 0,5--1% ở giọng bình thường).

**Tham số 9 và 10 — `octave_jump_cost = 0,35` và `voiced_unvoiced_cost = 0,14`: quán tính cơ học của thanh quản.**
Cao độ do độ căng của cơ nhẫn giáp (cricothyroid) và cơ giáp phễu (thyroarytenoid) trong thanh quản quyết định. Nghiên cứu cơ sinh học phát âm kinh điển của **Sundberg (1979)** chỉ ra rằng thanh quản người cần ít nhất $80\text{--}100\text{ ms}$ để co duỗi thay đổi độ căng qua một quãng tám ($F_0$ gấp đôi). Trong một bước nhảy trượt chỉ vỏn vẹn $10\text{ ms}$ ($\Delta t_{\text{hop}}$), việc cao độ đột ngột nhảy vọt một quãng tám là điều bất khả thi về mặt sinh học. Với $\Delta t_{\text{hop}} = 10\text{ ms}$:
- Nhảy đúng một quãng tám bị phạt $0{,}35 \times \log_2(2) = 0{,}35$.
- Nhảy một nửa cung (semitone) chỉ bị phạt $0{,}35 \times \frac{1}{12} \approx 0{,}029$.
Tỷ lệ chênh lệch hơn 10 lần này giúp Viterbi uốn lượn tự nhiên trong phạm vi nửa cung nhưng phạt rất nặng lỗi nhảy quãng tám giữa hai khung kế tiếp.

| Tham số Praat | Ký hiệu | Giá trị chuẩn | Ý nghĩa thuật toán & Mã nguồn (Boersma 1993) | Hiện thực trên FPGA DE10-Standard |
| :--- | :---: | :---: | :--- | :--- |
| `time_step` | $\Delta t_{\text{hop}}$ | $0{,}01\text{ s}$ | Bước nhảy trượt khung (160 mẫu tại 16 kHz) | Khóa cứng 10 ms (100 khung/s) đồng bộ luồng Mel |
| `pitch_floor` | $F_{\text{floor}}$ | $75\text{ Hz}$ | Giới hạn đáy cao độ $\implies \tau_{\text{max}} = 213\text{ mẫu}$, $L = 640\text{ mẫu}$ | Cửa sổ 640 mẫu lưu trong 1 khối M10K BRAM |
| `pitch_ceiling` | $F_{\text{ceiling}}$ | $600\text{ Hz}$ | Giới hạn trần cao độ $\implies \tau_{\text{min}} = 27\text{ mẫu}$ (187 lag) | Quét 187 độ trễ $\tau \in [27, 213]$, bỏ qua $\tau < 27$ |
| `very_accurate` | — | `off` | Cửa sổ Hanning 3 chu kỳ (640 mẫu) vs Gaussian 6 chu kỳ | Dùng Hanning 640 mẫu; tiết kiệm 50% BRAM và MAC |
| `max_candidates` | $N_{\text{cand}}$ | $15$ | 14 đỉnh cực đại cục bộ + 1 ứng viên Vô thanh cho Viterbi | Rút gọn về 1 ứng viên (bộ so sánh argmax cực đại) |
| `silence_threshold`| $\theta_{\text{silence}}$| $0{,}03$ | Ngưỡng biên độ khoảng lặng so với đỉnh file (3%) | Ngưỡng năng lượng tĩnh $E_{\text{frame}} > E_{\text{silence}}$ trước khi đo |
| `voicing_threshold`| $\theta_{\text{voice}}$ | $0{,}45$ | Ngưỡng tỷ số tự tương quan chuẩn hóa nhận diện hữu thanh | Điều kiện $\mathcal{R}_{\text{comp}}[\tau^*] \ge 0{,}45 \cdot \mathcal{R}_x[0]$ |
| `octave_cost` | — | $0{,}01$ | Phạt thiên vị log-lag nội khung để tránh nhảy xuống $F_0/2$ | Gộp sẵn lượng bù vào hệ số bảng tra ROM $C[\tau]$ |
| `octave_jump_cost` | — | $0{,}35$ | Phạt nhảy quãng tám giữa hai khung liên tiếp trong Viterbi | Bỏ qua trên streaming pipeline; lọc trung vị nhẹ ở sau |
| `voiced_unvoiced_cost`| — | $0{,}14$ | Phạt chuyển đổi $\text{Voiced} \leftrightarrow \text{Unvoiced}$ giữa hai khung | Bỏ qua; xử lý trực tiếp trên từng khung độc lập |

*Bảng 1.3.5a: Giải phẫu 10 tham số chuẩn mực đo cao độ của Praat và ánh xạ vi kiến trúc lên FPGA DE10-Standard.*

---

> **Thẻ công thức**
>
> **Công thức.**
> $$\mathcal{R}_x[\tau] = \sum_{n=0}^{L - 1 - \tau} x_{\text{win}}[n] \cdot x_{\text{win}}[n+\tau], \qquad \mathcal{R}_{\text{comp}}[\tau] = \mathcal{R}_x[\tau] \cdot C[\tau]$$
> $$F_0 = \begin{cases} \dfrac{f_s}{\tau^*}, & \text{nếu } (E_{\text{frame}} > E_{\text{silence}}) \text{ và } \dfrac{\mathcal{R}_{\text{comp}}[\tau^*]}{\mathcal{R}_x[0]} \ge \theta_{\text{voice}} \\[3mm] 0\text{ (Unvoiced)}, & \text{ngược lại} \end{cases}$$
> $$\text{với } \tau^* = \arg\max_{\tau \in [27, 213]} \mathcal{R}_{\text{comp}}[\tau].$$
>
> **Các biến.**
> - $\tau$ — độ trễ tương quan, là số nguyên quét trong dải $[27, 213]$ mẫu (187 độ trễ).
> - $x_{\text{win}}[n] = x[n] \cdot w[n]$ — mẫu âm thanh sau khi nhân cửa sổ Hanning 640 điểm.
> - $C[\tau] = 1/\mathcal{R}_w[\tau]$ — hệ số bù độ dốc cửa sổ lưu trong bảng tra ROM 187 phần tử.
> - $\mathcal{R}_x[0]$ — năng lượng tại lag 0, dùng làm mốc so sánh thanh tính (Voicing Threshold).
> - $\theta_{\text{voice}} = 0{,}45$ — ngưỡng quyết định có thanh; nếu không vượt qua, gán $F_0 = 0$.
>
> **Ý nghĩa.** Tách bạch bài toán cao độ thành hai pha: (1) Kiểm tra tính chu kỳ và khoảng lặng; (2) Nếu có chu kỳ, trích xuất độ trễ lag chuẩn xác theo đơn vị mẫu rời rạc.
>
> **Giá trên silicon.** Hoàn toàn chỉ dùng các bộ nhân-tích lũy (MAC) và bộ so sánh thanh ghi. Không cần bộ chia số học hay biến đổi ma trận.
>
> **Điều công thức không nói.** Ở tần số cao, khoảng cách giữa hai giá trị lag nguyên kế tiếp thô hơn ở tần số thấp do quan hệ nghịch đảo $F_0 = f_s/\tau$.

---

## 4. Hành trình từ Laptop lên FPGA: Tối giản hóa First-Principles

> **$\blacktriangleright$ CỔNG KIỂM CHỨNG PHẦN MỀM (SOFTWARE VERIFICATION GATE)**
>
> Trước khi đưa thiết kế lên FPGA, bắt buộc phải dựng một mô hình Python tối giản (Bit-accurate Fixed-Point Model) mô phỏng đúng khung 640 mẫu, cửa sổ Hanning và 187 lag số nguyên. Đem mô hình này chạy trên tập dữ liệu âm thanh đã lọc tiền xử lý (HPF 60 Hz ở Mục 1.1.5) để đối sánh trực tiếp với đường Pitch chuẩn của Praat (đo sai số lệch chuẩn Hz và hệ số tương quan Pearson $r$). Chỉ khi phiên bản Python tối giản này chứng minh được độ suy giảm chất lượng nằm trong ngưỡng chấp nhận được của bài toán nhận diện thanh điệu/ngữ điệu, các con số hạch toán phần cứng bên dưới mới có giá trị thực tiễn.

### A. Bản chất *bit-accurate fixed-point*: từ `float64` trên laptop đến thanh ghi số nguyên trên FPGA

**Ba tầng số, và tầng nào thực sự đến được silicon:**
1. **`float64` (dấu phẩy động, 64-bit):** dùng trên laptop. Mỗi số gồm dấu, phần mũ và phần định trị. Cái giá là các hàm siêu việt như $\cos$, $\log_2$ được cài bằng xấp xỉ đa thức khác nhau trên từng kiến trúc CPU.
2. **Q1.15 (fixed-point, 16-bit):** số nguyên 16-bit có dấu, 1 bit dấu, 15 bit lẻ. Dải biểu diễn $[-1, +0{,}99997]$. Định dạng tự nhiên cho mẫu âm thanh và hệ số cửa sổ.
3. **Q2.30 và thanh ghi tích lũy 42-bit:** tích của hai số Q1.15 là số 32-bit (Q2.30). Cộng dồn 640 tích cần thêm $\lceil \log_2 640 \rceil = 10$ bit, nên thanh ghi tích lũy phải rộng ít nhất $32 + 10 = 42$ bit.

**Vì sao `float64` không bảo đảm giống nhau giữa AMD64 và ARM64, còn số nguyên thì có:**
Chuẩn IEEE-754 quy định chính xác kết quả của `+`, `-`, `*`, `/` trên `float64`. Nhưng `cos`, `log2`, `sin` **không** nằm trong nhóm đó. Chuẩn chỉ đòi hỏi độ chính xác trong một khoảng ULP (Unit in the Last Place). Vì vậy glibc trên AMD64 và thư viện Apple trên ARM64 có thể trả về hai kết quả lệch nhau một vài ULP. Với một phép $\log_2$ nằm trong bộ so sánh "đỉnh nào cao hơn", hai ULP đủ để lật ngôi một đỉnh — làm hai máy cho hai chuỗi $F_0$ khác nhau!

Số nguyên bù hai không có vấn đề này. Với `int16`, `int32`, `int64` và bốn phép `+`, `-`, `*`, `>>`:
- Không có khái niệm làm tròn: kết quả là số nguyên chính xác.
- Tràn trong bù hai là hành vi xác định: quay vòng theo modulo $2^N$.
- Dịch phải số học `>>` trên số có dấu cũng xác định (mở rộng bit dấu).
Nghĩa là: **cùng một chuỗi lệnh số nguyên, cùng một đầu vào, cho đúng cùng một dãy bit trên AMD64, trên ARM64, và trên mạch RTL tổng hợp từ cùng biểu thức đó**. Đó chính là định nghĩa của *bit-accurate*.

**Mã nguồn thuật toán từ con số 0 (`chapter01/lab_1_3_5.py`):**

```python
import numpy as np

Q15, Q13 = 1 << 15, 1 << 13  # 1.0 in Q1.15 and Q3.13
TAU_MIN, TAU_MAX = 27, 213  # lag range for 600 Hz .. 75 Hz at 16 kHz


def hanning_rom_q15():
    # 320-entry symmetric Hanning window, Q1.15.
    n = np.arange(320, dtype=np.float64)
    w = 0.5 - 0.5 * np.cos(2.0 * np.pi * n / 639)
    return np.round(w * Q15).astype(np.int64)


def full_window():
    # 640-point window rebuilt from the folded ROM.
    h = hanning_rom_q15()
    return np.concatenate([h, h[::-1]])


def scoring_rom_q13(octave_cost=0.01):
    # C[tau] = R_w[0]/R_w[tau], with octave bias folded in. Q3.13.
    w = full_window() / Q15
    rw0 = float(np.dot(w, w))
    out = []
    for tau in range(TAU_MIN, TAU_MAX + 1):
        rw_tau = float(np.dot(w[: 640 - tau], w[tau:]))
        f0 = 16000.0 / tau
        bias = 2.0 ** (-octave_cost * np.log2(600.0 / f0))
        out.append(round(rw0 / rw_tau * bias * Q13))
    return np.array(out, dtype=np.int64)


def fixed_pitch_frame(x_q15, ref_energy):
    # Integer-only pitch detection for one 640-sample frame.
    xw = (x_q15 * full_window()) >> 15  # window multiply, stays Q1.15
    r0 = int(np.dot(xw, xw))  # frame energy, int64

    # Silence gate: r0 < 0.03 * ref  <=>  r0*100 < 3*ref. No divide.
    if ref_energy > 0 and r0 * 100 < 3 * ref_energy:
        return 0.0, 0

    rom = scoring_rom_q13()
    best, tau_star = -(1 << 62), 0
    for i, tau in enumerate(range(TAU_MIN, TAU_MAX + 1)):
        n = 640 - tau
        r_tau = int(np.dot(xw[:n], xw[tau:]))
        score = (r_tau * rom[i]) >> 13  # Q3.13 multiply
        if score > best:
            best, tau_star = score, tau

    # Voicing: best >= 0.45 * r0  <=>  best*100 >= 45*r0. No divide.
    if best * 100 < 45 * r0:
        return 0.0, 0
    return float(round(16000 / tau_star)), tau_star
```

**Ba chỗ chuyển đổi then chốt từ đại số sang phần cứng:**
1. **Phép chia bị loại bỏ bằng cách nhân chéo:** Điều kiện $\mathcal{R}_{\max} \ge 0{,}45\,\mathcal{R}_x[0]$ nhân chéo hai vế với 100 thành $100\,\mathcal{R}_{\max} \ge 45\,\mathcal{R}_x[0]$, chỉ còn nhân và so sánh.
2. **Hàm siêu việt bị loại bỏ bằng bảng tra:** $\log_2$ và phép chia $f_s / \tau^*$ được tính trước lúc biên dịch rồi nạp vào ROM.
3. **Cửa sổ chỉ nhân một lần cho mỗi khung:** Thực hiện trong Pha 1 trước khi quét tương quan.

**Kết quả kiểm chứng thực tế (`python chapter01/lab_1_3_5.py`):**

| Đại lượng | Bản số nguyên | Bản `float64` |
|---|:---:|:---:|
| Lag thắng $\tau^*$ | 80 | 80 |
| $F_0$ đọc được | 200 Hz | 200 Hz |
| Mã cửa sổ Hanning (320 mục, Q1.15) | đỉnh = 32768 | — |
| Bảng bù $C[\tau]$ (187 mục, Q3.13) | $8289 \dots 17387$ | — |

```
Khung t - 10 ms          Khung t              Khung t + 10 ms
  (1) -----------------> (1) ----------------> (1)     [Chế độ FPGA Streaming:
   | \                  / | \                 / |       Chỉ lấy 1 đỉnh argmax cục bộ,
   |  \   Phạt nhảy DF0/  |  \   Costjump    /  |       Không cần bộ nhớ quay lui]
  (2)  \              /  (2)  \             /  (2)
   |    \            /    |    \           /    |
  (3)    \          /    (3)    \         /    (3)     [Đường tối ưu Praat Viterbi:
   :      \        /      :      \       /      :       Duyệt toàn cục 15 ứng viên x N khung,
  (14)     \      /      (14)     \     /      (14)     Độ trễ bằng cả câu nói]
   |        \    /        |        \   /        |
  (UV)       \  /        (UV)       \ /        (UV)
              v                      v
        Phạt chuyển 0.14       Phạt chuyển 0.14
```

*Hình 1.3.5d: Đối chiếu cơ chế trích chọn cao độ: Lưới quy hoạch động Viterbi 15 ứng viên của Praat (phần mềm) vs. Trích chọn cực đại tức thời không trễ trên FPGA (phần cứng).*

**Đọc Hình 1.3.5d (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Ba cột mốc thời gian:** Chuỗi 3 khung phân tích liên tiếp gồm Khung $t - 10\text{ ms}$, Khung $t$, và Khung $t + 10\text{ ms}$ với bước trượt khung $\Delta t_{\text{hop}} = 10\text{ ms}$.
2. **Các nút tròn Ứng viên 1 đến 14:** 14 đỉnh cực đại cục bộ có điểm tự tương quan cao nhất trong mỗi khung.
3. **Nút tròn UV (Ứng viên 15):** Ứng viên đại diện cho trạng thái Vô thanh (Unvoiced), gán điểm cạnh tranh $R_{\text{unvoiced}}$ phụ thuộc tỷ số năng lượng khoảng lặng.
4. **Đường mũi tên tối ưu Praat Viterbi:** Duyệt toàn cục xuyên suốt câu để cực tiểu hóa tổng chi phí gồm điểm nội khung, phạt bước nhảy tần số $\text{Cost}_{\text{jump}}$ (0,35), và phạt chuyển đổi trạng thái Voiced $\leftrightarrow$ Unvoiced (0,14). Độ trễ bằng toàn bộ câu.
5. **Chế độ FPGA Streaming:** Chỉ lấy duy nhất Ứng viên 1 ($\tau_1^*$) qua một bộ so sánh cực đại thanh ghi. Quyết định chốt ngay lập tức, độ trễ bằng 0.

### B. Bỏ Viterbi trên FPGA: có hợp lý không, và lấy gì thay thế

**Ba lý do bỏ Viterbi là hợp lý:**
1. **Viterbi phá vỡ tính thời gian thực của streaming:** Quy hoạch động cần biết toàn bộ chuỗi khung trước khi quay lui (backtracking). Trên một câu 10 giây, độ trễ cấu trúc là 10 giây.
2. **Ba tầng tiền xử lý đã xử lý phần lớn nguyên nhân gây lỗi quãng tám:** HPF 60 Hz dập nhiễu nền tần thấp; bảng bù $C[\tau]$ san phẳng độ dốc cửa sổ; và `octave_cost = 0,01` phá thế hòa giữa hai đỉnh.
3. **Bộ nhớ trạng thái của Viterbi không hợp với datapath nhỏ:** 15 ứng viên $\times 1000$ khung cần hàng chục nghìn ô nhớ cho ma trận chi phí và con trỏ quay lui, vượt quá vài khối M10K dành cho khối Pitch.

**Giải pháp phần cứng: bộ lọc trung vị trượt 3 điểm:**
Để loại bỏ các điểm nhảy vọt cô lập (isolated octave spike) mà không gây trễ lớn, ta đặt một bộ lọc trung vị 3 điểm ngay sau đầu ra $F_0$:

| Khung | $t-1$ | $t$ | $t+1$ |
|---|:---:|:---:|:---:|
| Giá trị thô | 122 Hz | 245 Hz | 124 Hz |
| Sau lọc trung vị | 122 Hz | **124 Hz** | 124 Hz |

Giá trị $245\text{ Hz}$ là điểm nhảy vọt (gần gấp đôi). Trung vị của $\{122, 245, 124\}$ là $124\text{ Hz}$, loại bỏ điểm nhảy vọt mà không bịa ra giá trị trung bình giả ($163{,}7\text{ Hz}$).
- Phần cứng cần: 3 thanh ghi 16-bit, 2 bộ so sánh và mạch chọn.
- Độ trễ chỉ đúng 1 khung ($10\text{ ms}$).

---

## 5. Sổ Cái Hạch Toán Tài Nguyên Silicon trên FPGA DE10-Standard

Hệ thống nhắm tới kit **DE10-Standard** trang bị chip **Intel Cyclone V SX SoC (5CSXFC6D6F31C6N)**. Hãy lập bảng sổ cái hạch toán tài nguyên silicon:

**1. Kiểm đếm số phép tính chính xác trên mỗi khung $10\text{ ms}$ (với $\text{pitch\_ceiling} = 600\text{ Hz}$):**
- Pha 1 (Nhân cửa sổ Hanning khi ghi mẫu): $640\text{ phép nhân}$.
- Pha 2 (Tính năng lượng gốc $\mathcal{R}_x[0]$ tại $\tau = 0$ và kiểm tra ngưỡng khoảng lặng): $640\text{ phép MAC}$.
- Pha 3 (Quét 187 độ trễ từ $\tau = 27$ đến $\tau = 213$):
  $$N_{\text{corr}} = \sum_{\tau=27}^{213} (640 - \tau) = 187 \times \frac{613 + 427}{2} = 187 \times 520 = \mathbf{97.240\text{ phép MAC}}$$
- Pha 4 (Bù hệ số suy hao cửa sổ bằng bảng tra $C[\tau]$ cho 187 lag): $187\text{ phép nhân}$.
- **Tổng cộng toàn khung:** $640 + 640 + 97.240 + 187 = \mathbf{98.707\text{ phép tính/khung}}$.

**2. Định mức thời gian thực và kích thước thanh ghi tích lũy:**
- Ở xung nhịp $f_{\text{clk}} = 50\text{ MHz}$, một bộ nhân DSP thực thi tuần tự hoàn thành $98.707$ phép tính trong:
  $$T_{\text{calc}} = \frac{98.707}{50.000.000\text{ Hz}} \approx \mathbf{1{,}974\text{ ms}} \ll 10\text{ ms} \implies \mathbf{\text{RTF} \approx 0{,}197}$$
- **Định cỡ thanh ghi tích lũy (Bit-width):** Mẫu âm thanh đầu vào 16-bit có dấu định dạng `Q1.15`. Tích của hai số 16-bit là số 32-bit (`Q2.30`). Khi cộng dồn tối đa $640$ mẫu ($\lceil \log_2(640) \rceil = 10\text{ bit}$ tăng trưởng), thanh ghi tích lũy cần chiều rộng tối thiểu $32 + 10 = \mathbf{42\text{ bit}}$. Khối DSP Block trên Intel Cyclone V tích hợp sẵn bộ cộng tích lũy phần cứng lên tới **64-bit**, do đó thanh ghi 42-bit nằm trọn bên trong phần cứng hardened DSP, hoàn toàn miễn nhiễm với tràn số (no arithmetic overflow).

| Tài nguyên phần cứng | Tiêu tốn cho Pitch | Khả dụng (Cyclone V) | Tỷ lệ sử dụng | Đánh giá vi kiến trúc |
| :--- | :---: | :---: | :---: | :--- |
| **Khối nhớ M10K BRAM** | 2 khối | 553 khối | $0{,}36\%$ | 1 khối lưu $x_{\text{win}}[n]$, 1 khối lưu bảng tra ROM |
| **Khối DSP (18x18-bit)** | 1 khối | 112 khối | $0{,}89\%$ | Chạy tuần tự ở 50 MHz đạt $\text{RTF} \approx 0{,}197$ |
| **Bộ logic ALM / Registers** | $\approx 450$ ALMs$^*$ | 41.910 ALMs | $1{,}07\%$ | Bộ đếm địa chỉ, bộ so sánh cực đại thanh ghi |
| **Bộ chia số thực (Divider)** | 0 | Không cần | $0\%$ | Thay hoàn toàn bằng bảng tra ROM 187 mục |

*Bảng 1.3.5b: Sổ cái hạch toán tài nguyên silicon cho khối Pitch trên FPGA DE10-Standard. ($^*$Ước lượng sơ bộ cho riêng lõi tính toán datapath, chưa bao gồm overhead của FSM điều khiển, bộ sinh địa chỉ Dual-Port và giao tiếp hệ thống).*

> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ**
>
> **Cái giá phải trả và điều bị phá hủy:**
> 1. **Độ trễ ban đầu và tâm cửa sổ (Hình 1.3.5e):** Để bao trọn khung $40\text{ ms}$ thay vì $25\text{ ms}$, bộ đệm luồng Pitch cần thời gian nạp đầy ban đầu (initial buffering latency) lâu hơn $15\text{ ms}$, đồng thời tâm pha của cửa sổ phân tích (frame center) nằm lùi về quá khứ xa hơn $7{,}5\text{ ms}$ so với tâm cửa sổ STFT.
> 2. **Phi tuyến lượng tử hóa ở cao tần:** Do $F_0 = f_s/\tau$, bước nhảy 1 mẫu ở vùng âm trầm ($\tau = 160 \implies 100\text{ Hz}$) chỉ làm lệch $\Delta F_0 = 0{,}62\text{ Hz}$ (rất mịn); nhưng ở vùng âm cao ($\tau = 27 \implies 592{,}6\text{ Hz}$), nhảy 1 mẫu làm lệch tới $\Delta F_0 = 22\text{ Hz}$ (khá thô). Đây là sự đánh đổi cố hữu của phương pháp tự tương quan số nguyên: **Rất nhạy ở âm trầm, nhưng bị bậc thang hóa ở âm cao.**

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

*Hình 1.3.5e: Đối sánh trục thời gian giữa Luồng Log-Mel STFT ($400\text{ mẫu} = 25\text{ ms}$) và Luồng Pitch $F_0$ ($640\text{ mẫu} = 40\text{ ms}$): Làm rõ độ lệch tâm pha $7{,}5\text{ ms}$ và độ trễ nạp đầy ban đầu $15\text{ ms}$.*

**Đọc Hình 1.3.5e (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Trục hoành thời gian chung (Dưới cùng):** Đánh dấu các mốc thời gian vật lý tính bằng mili-giây: $0, 10, 20, 25, 30, 40, 50, 60\text{ ms}$.
2. **Hàng A — Luồng Log-Mel STFT:** Biểu diễn các vòm cửa sổ dài $25\text{ ms}$ ($400\text{ mẫu}$ tại $16\text{ kHz}$), trượt với bước nhảy $10\text{ ms}$ ($160\text{ mẫu}$). Khung đầu tiên hoàn tất nạp mẫu tại $t = 25\text{ ms}$; tâm đối xứng của cửa sổ Khung 1 nằm tại $t = 12{,}5\text{ ms}$.
3. **Hàng B — Luồng Pitch $F_0$:** Biểu diễn các vòm cửa sổ Hanning dài $40\text{ ms}$ ($640\text{ mẫu}$), trượt với cùng bước nhảy $10\text{ ms}$ ($160\text{ mẫu}$). Khung đầu tiên hoàn tất nạp mẫu tại $t = 40\text{ ms}$; tâm đối xứng của cửa sổ Khung 1 nằm tại $t = 20{,}0\text{ ms}$.
4. **Mũi tên hai chiều $\Delta t_{\text{init}} = 15\text{ ms}$:** Độ trễ chờ nạp đầy khung đầu tiên, và **chỉ xảy ra đúng một lần**.
5. **Mũi tên hai chiều $\Delta t_{\text{center}} = 7{,}5\text{ ms}$:** Độ lệch tâm pha, **lặp lại ở mọi khung**.

**Hai con số thời gian dễ bị lẫn, và cách phân biệt chúng (Ẩn dụ hai công nhân bấm đồng hồ):**
Hãy tưởng tượng hai người công nhân cùng bấm đồng hồ từ $t = 0\text{ ms}$, mỗi người phụ trách một luồng:
- **Độ trễ nạp đầy khung đầu tiên ($\Delta t_{\text{init}} = 40 - 25 = 15\text{ ms}$):** Người phụ trách luồng Pitch cần 640 mẫu mới có khung đầu tiên, tức phải chờ đến $t = 40\text{ ms}$. Người phụ trách luồng STFT chỉ cần 400 mẫu, nên xong ở $t = 25\text{ ms}$. Người thứ nhất về đích chậm hơn 15 ms. **Đây là chuyện của lần đầu tiên duy nhất**. Từ khung thứ hai trở đi, cả hai luồng đều đã có sẵn dữ liệu cũ trong bộ đệm, nên cứ mỗi 10 ms cả hai cùng xuất một kết quả.
- **Độ lệch tâm pha ($\Delta t_{\text{center}} = 20 - 12{,}5 = 7{,}5\text{ ms}$):** Một khung 40 ms bắt đầu ở 0 thì có tâm ở 20 ms; một khung 25 ms bắt đầu ở 0 thì có tâm ở 12,5 ms. Khi cả hai cùng mang chỉ số "khung 1", giá trị Pitch mô tả thời điểm 20 ms, còn giá trị Mel mô tả thời điểm 12,5 ms — lệch nhau 7,5 ms. **Đây là sai lệch thường trực, lặp lại ở mọi khung**.
- **Vì sao phải tách bạch:** Khi ghép hai luồng để tính Pearson ở Phụ lục, $\Delta t_{\text{center}}$ được xử lý bằng cách dịch chỉ số, còn $\Delta t_{\text{init}}$ được xử lý bằng cách bỏ qua các khung chưa có dữ liệu ở đầu câu.

---

## 6. Sơ đồ Vi Kiến Trúc Pipeline Đề Xuất (Dataflow Architecture)

Sơ đồ khối chia khối Pitch thành **hai pha tách biệt**. Cửa sổ Hanning được nhân đúng một lần khi chuyển dữ liệu sang True Dual-Port RAM; vòng quét tương quan chỉ còn đọc hai cổng của cùng một bộ nhớ:

```
  Dòng mẫu I2S (16 kHz, 16-bit)
               |
               v
  +---------------------------------------+      +-----------------------+
  |    Raw Ring Buffer (640 mẫu thô)      |      |   Bộ đếm ghi cuốn vòng|
  |  vùng A: 0..319 | vùng B: 320..639    |----->|                       |
  +-------------------+-------------------+      +-----------------------+
                      | (khi đủ 160 mẫu mới)
                      v
  +---------------------------------------+      +-----------------------+
  |    PHA 1 — 640 chu kỳ clock           |<-----| ROM Hanning           |
  | Đọc 640 mẫu thô, nhân ROM, ghi sang RAM|      | 320 mục Q1.15         |
  +-------------------+-------------------+      +-----------------------+
                      | (ghi x_win[n])
                      v
  +---------------------------------------+
  |      True Dual-Port RAM (640 mẫu)     |
  | Cổng A: địa chỉ n | Cổng B: đ.chỉ n + tau |
  +-------------------+-------------------+
                      | (2 cổng đọc song song)
                      v
  +---------------------------------------+      +-----------------------+
  |    PHA 2 — 97.240 chu kỳ clock        |----->| 1 bộ nhân DSP         |
  | Quét 187 độ trễ tau in [27, 213]      |      | + tích lũy >= 42-bit  |
  +---------------------------------------+      +-----------+-----------+
                                                             | R_x[tau]
                                                             v
  +-----------------------+                      +-----------+-----------+
  | Lọc trung vị 3 điểm   |<---------------------| Bù C[tau] (ROM Q3.13) |
  +-----------+-----------+                      | + argmax 187 lag      |
              |                                  +-----------------------+
              v
     F0 mỗi 10 ms (pitch_f0.bin)
```

*Hình 1.3.5f: Vi kiến trúc hai pha: cửa sổ được nhân một lần khi chép sang RAM, nên vòng quét tương quan chỉ còn đọc hai cổng và một phép nhân.*

**Đọc Hình 1.3.5f (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Raw Ring Buffer (Hàng trên):** Mẫu I$^2$S thô được ghi liên tục vào bộ đệm vòng 640 mẫu (chia hai vùng A và B). Khi đã tích lũy đủ 160 mẫu mới (đúng một bước nhảy 10 ms), khối điều khiển phát xung kích hoạt sang Pha 1.
2. **Pha 1 (640 chu kỳ clock):** Đọc lần lượt 640 mẫu thô, nhân từng mẫu với hệ số Hanning lấy từ ROM 320 mục, rồi ghi kết quả $x_{\text{win}}[n]$ sang True Dual-Port RAM. **Đây là điểm sửa lỗi quan trọng so với phiên bản trước:** không nhân cửa sổ khi mẫu vừa chảy vào bộ đệm trượt vì khi khung trượt đi 160 mẫu, mẫu cũ nằm ở vị trí $n$ mới trong khung tương ứng hệ số $w[n]$ khác. Nhân trong Pha 1 bảo đảm luôn đúng vị trí.
3. **True Dual-Port RAM (Khối giữa):** RAM có hai cửa đọc độc lập A và B mở đồng thời trong 1 nhịp đồng hồ. Cửa A xuất $x_{\text{win}}[n]$, cửa B xuất $x_{\text{win}}[n+\tau]$, cả hai đi thẳng vào **cùng một** bộ nhân DSP.
4. **Pha 2 (97.240 chu kỳ clock):** Với mỗi độ trễ $\tau$ trong 187 giá trị, bộ nhân-cộng dồn tích lũy vào thanh ghi 42-bit.
5. **Hậu xử lý:** Nhân $\mathcal{R}_x[\tau]$ với bảng $C[\tau]$ (Q3.13, đã gộp `octave_cost`), tìm $\tau^*$ bằng `argmax`, rồi đưa qua bộ lọc trung vị 3 điểm trước khi xuất `pitch_f0.bin`.

---

## 7. Tổng Kết và Cầu Nối Chuyển Tiếp

- **Mục 1.2 & 1.3** cung cấp vector đặc trưng phổ 80 chiều (Log-Mel) đại diện cho *khẩu hình miệng*.
- **Mục 1.3.5** bổ sung dòng dữ liệu vô hướng 1 chiều ($F_0$) đại diện cho *nhịp đập dây thanh quản*.
- **Sự kết hợp hai luồng đặc trưng:** Bằng cách ghép luồng Log-Mel và luồng Pitch $F_0$, hệ thống Edge AI trên FPGA thu nhận được đầy đủ cả **ngữ âm** lẫn **ngữ điệu**, mở đường cho các mô hình phân loại thanh điệu tiếng Việt và nhận dạng cảm xúc đạt độ chính xác tương đương các siêu máy tính máy trạm mà chỉ tiêu tốn chưa đầy $2\%$ tài nguyên silicon của kit DE10-Standard.

---

# Phụ lục 1.3.5-A. Áp dụng lý thuyết 1.3.5 vào mã nguồn Python (`audio_processing.py` và `evaluator.py`)

> **Phạm vi và Mục tiêu:** Phụ lục này đối chiếu hai tệp mã nguồn xử lý âm thanh trong thư mục `Pronunciation_Final_Master` của kho lưu trữ `DucDocDao/Pitch-Project` (nhánh `main`) với hệ thống lý thuyết đo cao độ $F_0$ bằng thuật toán tự tương quan ở Mục 1.3.5 (chuẩn Praat, Boersma 1993). Để làm sáng tỏ toàn bộ luồng gọi hàm, phụ lục khảo sát thêm các đoạn mã liên kết trong `main.py`, `visualizer.py`, `generate_audio.py` và `sentence_data.py`. Mọi hành vi mô tả dưới đây đều được truy xuất trực tiếp từ mã nguồn thực tế.

---

## 1. Bức Tranh Tổng Thể: Hai Tệp Làm Gì Trong Hệ Thống?

### 1.1. Ranh giới triển khai: Mã nguồn Python nguyên bản vs. Hệ thống FPGA Edge Node
Trước khi đi sâu vào mã nguồn của từng hàm, cần định vị dự án `Pitch-Project` trong bức tranh kiến trúc tổng thể **FPGA Edge Node $\leftrightarrow$ Shared Folder $\leftrightarrow$ Server** đã thiết lập tại Hình 1.3.5a (Mục 0.1):
- **Trong kho lưu trữ `Pitch-Project` (Môi trường thực nghiệm máy tính):** Toàn bộ quy trình chạy trên CPU/GPU máy chủ: tổng hợp âm thanh bằng Kokoro TTS, cắt lặng bằng Librosa, đo cao độ bằng Praat C++ (qua Parselmouth), nhận diện mốc từ bằng Whisper, căn chỉnh và tính điểm tương quan Pearson $r$.
- **Khi triển khai thực tế trên vi mạch FPGA (Hệ thống mục tiêu):** Bo mạch FPGA DE10-Standard gánh trọn vẹn khâu tiền xử lý (HPF 60 Hz và cắt lặng) và chạy song song hai luồng phần cứng: (1) Nhánh STFT Log-Mel phục vụ trực tiếp bộ mã hóa Whisper (hoặc trích xuất WAV sạch), và (2) Nhánh đo cao độ tự tương quan Mục 1.3.5 ghi trực tiếp mảng nhị phân `pitch_f0.bin` ra Thư mục dùng chung (Shared Folder). Máy chủ chỉ cần đọc `pitch_f0.bin` và mốc từ để chấm điểm $r$, **hoàn toàn không cần cài đặt hay chạy Praat/Parselmouth**.

### 1.2. Bài toán của dự án
Dự án giải quyết bài toán định lượng và so sánh **đường cong cao độ (pitch contour)** — tức chuỗi giá trị tần số cơ bản $F_0$ biến thiên theo thời gian — giữa một câu tiếng Anh do giọng tham chiếu chuẩn đọc (giọng tổng hợp nữ Mỹ `sarah`) với cùng câu đó do một người học hoặc giọng đọc khác đọc (các giọng nam Mỹ, ví dụ `michael`). Tín hiệu âm thanh được tổng hợp tự động bằng mô hình Kokoro TTS (`generate_audio.py`). Kết quả đánh giá cuối cùng là hệ số tương quan Pearson ($r$) giữa hai đường cao độ đã được căn chỉnh thời gian.

### 1.3. Luồng xử lý một câu (theo `main.py`)
1. `trim_silence_and_save` (`audio_processing.py`): Cắt bỏ khoảng lặng ở hai đầu tệp âm thanh và ghi ra tệp WAV đã cắt.
2. `extract_features_praat` (`audio_processing.py`): Đo đường cao độ $F_0$ trên **chính tệp WAV đã cắt** bằng công cụ Praat (thông qua thư viện liên kết `parselmouth`).
3. `get_user_timestamps` (`evaluator.py`): Nạp mô hình nhận dạng tiếng nói tự động Whisper (`openai/whisper`) bóc tách mốc thời gian từ ($w_{\text{start}}, w_{\text{end}}$) trên **chính tệp WAV đã cắt**.
4. `plot_analysis` (`visualizer.py`): Gọi chuỗi 4 hàm trong `audio_processing.py` (`get_local_chunk`, `equalize_local_chunk`, `dynamic_sliding_window_pearson`, `summarize_pearson`) để căn chỉnh hai đường cao độ và tính Pearson $r$.
5. `summarize_sentence_reports` (`audio_processing.py`): Gom toàn bộ kết quả của nhiều câu thành bảng thống kê phân phối độ chính xác theo các ngưỡng tích lũy.

```
+------------------------------------+       +------------------------------------+       +------------------------------------+
|        Tệp Âm Thanh Thô            | ----> |       trim_silence_and_save        | ----> |      Tệp WAV Đã Cắt Lặng           |
| (Kokoro TTS, WAV, fs = 24 kHz)     |       | (librosa.effects.trim, top_db=30dB)|       | (fs = 24 kHz, đã đồng bộ gốc t=0)  |
+------------------------------------+       +------------------------------------+       +-----------------+------------------+
                                                                                                            |
                                              +-------------------------------------------------------------+
                                              |                             |
                                              v                             v
                       +------------------------------------+        +------------------------------------+
                       |     Luồng 1: Đo Cao Độ             |        |    Luồng 2: Nhận Diện Mốc Từ       |
                       |  (extract_features_praat)          |        |          (evaluator.py)            |
                       | snd.to_pitch() (Praat, fs = 24 kHz)|        | Lấy mẫu lại về 16 kHz -> Whisper   |
                       | Khung 40 ms, bước 10 ms, 15 u.viên |        | Trích xuất mốc từ (w_start, w_end) |
                       +-----------------+------------------+        +-----------------+------------------+
                                         | Mảng F0 (0 Hz = Unvoiced)                   | Mốc từ (w_start, w_end)
                                         +------------------------------+--------------+
                                                                        |
                                                                        v
                                              +---------------------------------------------------+
                                              |      Căn chỉnh theo từ (audio_processing.py)      |
                                              | 1. get_local_chunk: Cắt đoạn i = floor((t/D)*N)   |
                                              | 2. equalize_local_chunk: Nội suy np.interp        |
                                              | 3. Ghép vào mảng cao độ stitched_user_pitch       |
                                              +-------------------------+-------------------------+
                                                                        |
                                                                        v
                                              +---------------------------------------------------+
                                              |    Cửa sổ trượt Pearson (audio_processing.py)     |
                                              | Kích thước W = 2N/(K+2) (~2 từ), bước S = W/2     |
                                              | Lọc hữu thanh: (u_i > 0) & (v_i > 0) -> Pearson r |
                                              +-------------------------+-------------------------+
                                                                        | Chuỗi Pearson r
                                                                        v
                                              +---------------------------------------------------+
                                              |       Tổng hợp điểm số (audio_processing.py)      |
                                              | Bỏ NaN, kẹp r <= 0 về 0 -> mean_r in [0, 1]       |
                                              | Thống kê tích lũy câu: >= 0.9, >= 0.8, ..., >= 0.3|
                                              +---------------------------------------------------+
```

*Hình 1.3.5g: Sơ đồ luồng xử lý âm thanh, trích xuất hai luồng song song (Praat $F_0$ và Whisper Timestamps) và thuật toán đối sánh ngữ điệu trong mã nguồn Python (`audio_processing.py` và `evaluator.py`).*

**Đọc Hình 1.3.5g (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Khối Tệp Âm Thanh Thô và Khối Tiền xử lý cắt lặng (Hàng 1):** Tệp âm thanh do Kokoro TTS sinh ra ở tần số 24 kHz được đưa qua hàm `trim_silence_and_save` (dùng `librosa.effects.trim`, $\text{top\_db} = 30\text{ dB}$, biên độ $3{,}2\%$) để cắt bỏ khoảng lặng hai đầu, thiết lập gốc thời gian chuẩn $t = 0$.
2. **Nhánh Luồng 1 — Đo Cao Độ Praat (Hàng 2, Bên trái):** Gọi hàm `extract_features_praat`. Lệnh `snd.to_pitch()` chạy mã C++ Praat trên tín hiệu 24 kHz, dùng cửa sổ Hanning 40 ms (960 mẫu), bước nhảy 10 ms (240 mẫu), tự tương quan bù suy hao và Viterbi 15 ứng viên. Kết quả trả về mảng `pitch` ($0\text{ Hz}$ là vô thanh).
3. **Nhánh Luồng 2 — Nhận Diện Mốc Thời Gian Từ (Hàng 2, Bên phải):** Gọi `get_user_timestamps` trong `evaluator.py`. Tín hiệu lấy mẫu lại về 16 kHz đưa vào Whisper `base` để xuất mốc từ ($w_{\text{start}}, w_{\text{end}}$).
4. **Khối Căn Chỉnh Theo Từ (Hàng 3):** Kết hợp kết quả từ hai nhánh: cắt đoạn, nội suy `np.interp` về cùng độ dài từ chuẩn, rồi dán vào `stitched_user_pitch`.
5. **Khối Cửa Sổ Trượt Pearson (Hàng 4):** Tạo cửa sổ trượt $W = 2N/(K+2)$ ($\approx 2$ từ), bước $S = W/2$, lọc các điểm cùng hữu thanh ($u_i > 0$ và $v_i > 0$) để tính Pearson $r$.
6. **Khối Tổng Hợp Điểm Số (Hàng 5):** Bỏ NaN, kẹp $r \le 0$ về 0, tính trung bình `mean_r`, và thống kê tích lũy câu theo các ngưỡng $\ge 0{,}9 \dots \ge 0{,}3$.

### 1.4. Hiểu lầm cần tránh ngay từ đầu
- **`evaluator.py` không thực hiện việc chấm điểm:** Tệp này chỉ nạp Whisper và trả về mốc thời gian từ. Toàn bộ logic so khớp, căn chỉnh và tính điểm tương quan ($r$) đều nằm trọn trong `audio_processing.py`.
- **Không có dòng mã Python nào tự tính tổng tự tương quan:** Công thức tự tương quan $\mathcal{R}_x[\tau]$, cửa sổ Hanning, phép chia bù suy hao và bảng tra đều được đóng gói bên trong lệnh gọi thư viện `snd.to_pitch()`.

---

## 2. Bảng Thuật Ngữ Dùng Trong Phụ Lục

| Thuật ngữ tiếng Việt | Thuật ngữ tiếng Anh | Định nghĩa chuẩn mực trong ngữ cảnh mã nguồn |
| :--- | :--- | :--- |
| Khung phân tích | Frame | Đoạn gồm $L$ mẫu liên tiếp để tính một giá trị $F_0$. |
| Bước nhảy trượt khung | Time step / Hop size ($\Delta t_{\text{hop}}$) | Khoảng thời gian giữa tâm hai khung liên tiếp ($10\text{ ms}$). |
| Điểm cao độ | Pitch point | Một phần tử trong mảng `pitch`: giá trị $F_0$ (Hz); bằng 0 nếu là vô thanh. |
| Hữu thanh / Vô thanh | Voiced / Unvoiced | Trạng thái khung tín hiệu có / không có dao động tuần hoàn của dây thanh quản. |
| Tổng tự tương quan $\mathcal{R}_x[\tau]$ | Autocorrelation sum | Tổng tích các cặp mẫu trễ $\tau$, không phải tích chập. |
| Hệ số tương quan Pearson $r$ | Pearson correlation coefficient | Thước đo mức độ hai chuỗi số đồng biến/nghịch biến tuyến tính, nằm trong $[-1, 1]$. |
| Căn chỉnh thời gian | Time alignment | Đưa hai đường cao độ có độ dài khác nhau về cùng trục chỉ số để so sánh từng điểm. |

*Bảng 1.3.5c: Bảng thuật ngữ chuyên dụng trong mã nguồn và đối sánh lý thuyết.*

> **Cảnh báo nghiêm ngặt về hiện tượng trùng ký hiệu:**
> Ký hiệu $r_x[\tau]$ ở Mục 1.3.5 là **hàm tự tương quan chuẩn hóa theo độ trễ $\tau$** (đo một khung tương đồng với chính nó khi trượt đi $\tau$ mẫu). Biến `r`, `mean_r` trong mã nguồn Python là **hệ số tương quan tuyến tính Pearson** giữa hai đường cong cao độ $F_0$ của hai người nói khác nhau. Hai đại lượng này hoàn toàn khác nhau.

---

## 3. `extract_features_praat`: Một Dòng Code Chứa Toàn Bộ Mục 1.3.5

### 3.1. Mã nguồn
```python
def extract_features_praat(audio_path, verbose=False):
    snd = parselmouth.Sound(audio_path)
    pitch_object = snd.to_pitch()
    pitch = np.nan_to_num(pitch_object.selected_array["frequency"])
    time_stamps = pitch_object.xs()
    return pitch, time_stamps
```

### 3.2. Cơ chế thực thi của từng dòng lệnh
1. `parselmouth.Sound(audio_path)`: Nạp tệp WAV thành đối tượng âm thanh trong bộ nhớ C++ của Praat.
2. `pitch_object = snd.to_pitch()`: Kích hoạt hàm C++ `Sound_to_Pitch_ac` với **toàn bộ 10 tham số mặc định** (Bảng 1.3.5a): `time_step = 0.01s`, `pitch_floor = 75Hz`, `pitch_ceiling = 600Hz`, `very_accurate = off`, `max_candidates = 15`, `silence_threshold = 0.03`, `voicing_threshold = 0.45`, `octave_cost = 0.01`, `octave_jump_cost = 0.35`, `voiced_unvoiced_cost = 0.14`.
3. `selected_array['frequency']`: Trích xuất ứng viên tối ưu toàn cục mà thuật toán Viterbi đã chọn cho từng khung. Khung vô thanh được gán 0. `np.nan_to_num` bảo đảm $0\text{ Hz} \equiv \text{Vô thanh}$.
4. `pitch_object.xs()`: Trả về mảng mốc thời gian vật lý tại tâm đối xứng của từng khung. Trong `main.py`, mảng này bị bỏ qua (`pitch, _ = extract_features_praat(...)`).

### 3.3. Ánh xạ chi tiết từ Praat C++ sang lý thuyết Mục 1.3.5

| Bước thực thi bên trong `snd.to_pitch()` | Vị trí trong Mục 1.3.5 | Công thức / Tham số liên kết |
| :--- | :--- | :--- |
| Cắt khung 3 chu kỳ của $75\text{ Hz} = 40\text{ ms}$, bước $10\text{ ms}$ | Mục 3.A | Quy tắc Boersma, Tham số 1–2 |
| Nhân cửa sổ Hanning (do `very_accurate = off`) | Mục 3.B | Lựa chọn kỹ thuật Hanning, Tham số 4 |
| Tính tự tương quan $\mathcal{R}_x[\tau]$ | Mục 2 | Công thức tính tổng tự tương quan |
| Bù suy hao cửa sổ bằng phép chia cho $\mathcal{R}_w[\tau]$ | Mục 3.B | Công thức hệ số bù $C[\tau]$ |
| Giới hạn dải tìm kiếm đỉnh trong $[\tau_{\min}, \tau_{\max}]$ | Mục 2 | Dải quét $[27, 213]$ mẫu |
| Trích xuất 14 đỉnh cực đại + 1 ứng viên Vô thanh | Mục 3.C | Tham số 5, 6, 7 (ngưỡng 0,45 và 0,03) |
| Phạt log-lag nội khung để tránh nhảy xuống $F_0/2$ | Mục 3.C | Tham số 8 (`octave_cost = 0.01`) |
| Quy hoạch động Viterbi xuyên suốt câu nói | Mục 4 | Tham số 9–10, Hình 1.3.5d (nhánh Praat) |
| Xuất giá trị cao độ $F_0 = f_s / \tau^*$ | Mục 2 | Công thức thẻ tóm tắt |

*Bảng 1.3.5d: Đối chiếu chi tiết giữa lệnh gọi `snd.to_pitch()` và các công thức của Mục 1.3.5.*

### 3.4. Chỗ mã nguồn khác lý thuyết và hệ quả kỹ thuật

**(a) Tần số lấy mẫu thực tế là $24\text{ kHz}$ thay vì $16\text{ kHz}$:**
Kokoro TTS sinh tệp âm thanh ở $f_s = 24.000\text{ Hz}$. Do đó dải lag mẫu thực tế trong Praat là:
$$\tau_{\min} = \lceil 24.000 / 600 \rceil = \mathbf{40\text{ mẫu}}, \qquad \tau_{\max} = \lfloor 24.000 / 75 \rfloor = \mathbf{320\text{ mẫu}}$$
$$L = 0{,}040 \times 24.000 = \mathbf{960\text{ mẫu}}, \qquad \Delta t_{\text{hop}} = 0{,}01 \times 24.000 = \mathbf{240\text{ mẫu}}$$
Dải lag mở rộng từ $[27, 213]$ (187 lag) lên $[40, 320]$ (281 lag). Thời lượng vật lý (40 ms, 10 ms) và dải tần số (75–600 Hz) hoàn toàn không đổi.

**(b) Có quy hoạch động Viterbi và 15 ứng viên:**
Praat trên máy trạm duyệt toàn bộ câu nói qua ma trận 15 ứng viên, trong khi FPGA streaming rút gọn lấy 1 ứng viên cực đại tức thời kết hợp bộ lọc trung vị 3 điểm.

**(c) Thiếu bước lọc thông cao (HPF) 60 Hz:**
Mã Python đưa thẳng tín hiệu tổng hợp vào Praat mà không lọc. Chấp nhận được vì giọng Kokoro rất sạch, nhưng khi lên FPGA với micro thật bắt buộc phải có HPF 60 Hz.

**(d) Giải phẫu chính xác cơ chế tính toán trong mã nguồn C++ của Praat (`fon/Sound_to_Pitch.cpp`):**
- **Praat không tự lấy mẫu lại:** Hàm `Sound_to_Pitch_any` đọc trực tiếp mảng mẫu và dùng nghịch đảo tần số gốc `dx`. Tại 24 kHz, cửa sổ là 960 mẫu.
- **Praat tính tự tương quan bằng FFT theo định lý Wiener–Khinchin:**
  1. Trừ trung bình cục bộ (`localMean`) trước khi nhân cửa sổ để khử DC.
  2. Nhân cửa sổ Hanning: `0.5 - 0.5 * cos(2*pi*i/(nsamp_window+1))`.
  3. Đệm số 0 lên lũy thừa của 2: với 638 mẫu và độ sâu nội suy 0,5, ngưỡng là 957, nên Praat đệm lên `nsampFFT = 1024` ("To avoid edge effects, we have to append zeroes to the window").
  4. Thực hiện chuỗi: Forward FFT $\to$ tính bình phương biên độ $|X[k]|^2 = \text{re}^2 + \text{im}^2 \to$ Backward IFFT. Kết quả `ac` chính là hàm tự tương quan.
  5. Bù suy hao bằng phép chia cho `windowR` (tự tương quan của cửa sổ): `r[i] = ac[i+1] / (ac[1] * windowR[i+1])`.
  6. Nội suy Sinc dưới mẫu (sinc interpolation) tìm cực trị liên tục.
- **Tính tương đương toán học:** Phương pháp FFT với zero-padding đủ lớn ($\ge L + \tau_{\max}$) và phương pháp tổng trực tiếp trong miền thời gian $\sum x_{\text{win}}[n] x_{\text{win}}[n+\tau]$ trên FPGA **hoàn toàn tương đương về mặt toán học** (sai lệch $< 10^{-14}$). Sai lệch thực tế chỉ đến từ nội suy sinc và Viterbi.

### 3.5. Bản chất trục thời gian của mảng `pitch`
Tâm đối xứng của khung phân tích đầu tiên lùi về sau khoảng nửa khung ($\approx 20\text{ ms}$). Đây chính là hiện tượng "độ lệch tâm pha" đã phân tích ở Hình 1.3.5e.

---

## 4. `trim_silence_and_save`: Cắt Khoảng Lặng Hai Đầu

### 4.1. Mã nguồn
```python
y, sr = librosa.load(audio_path, sr=None)
y_trimmed, _ = librosa.effects.trim(y, top_db=top_db)  # top_db = 30
if not len(y_trimmed) or not np.any(y_trimmed):
    raise ValueError(...)
sf.write(trimmed_path, y_trimmed, sr)
```

### 4.2. Cơ chế vật lý
Hàm `librosa.effects.trim` chia tín hiệu thành các khung ngắn (2048 mẫu, bước 512 mẫu), tính năng lượng RMS và đổi sang dB quy chiếu theo khung lớn nhất. Khung nào thấp hơn đỉnh quá $\text{top\_db} = 30\text{ dB}$ bị cắt bỏ ở hai đầu.
$$10^{-30/20} = 10^{-1{,}5} \approx \mathbf{0{,}0316} \implies \mathbf{3{,}2\%}$$

### 4.3. Đối chiếu giữa `top_db = 30` của Librosa và `silence_threshold = 0,03` của Praat

| Đặc tính so sánh | Cắt khoảng lặng bằng Librosa (`top_db = 30`) | Ngưỡng khoảng lặng Praat (`silence_threshold = 0.03`) |
| :--- | :--- | :--- |
| **Bản chất toán học** | Tỷ số decibel: $20 \log_{10}(A / A_{\max}) = -30\text{ dB}$ | Tỷ số biên độ tuyến tính: $I / I_{\max} = 0{,}03$ |
| **Giá trị quy đổi** | Biên độ rơi xuống dưới $3{,}16\%$ đỉnh file | Biên độ rơi xuống dưới $3{,}00\%$ đỉnh file |
| **Phạm vi tác động** | Chỉ cắt bỏ phần lặng ở **đầu và đuôi tệp** | Đánh giá độc lập trên **từng khung $10\text{ ms}$** |
| **Mục đích thiết kế** | Đồng bộ gốc thời gian $t = 0$ cho Whisper và Praat | Ngăn chặn việc dò cao độ giả trên nhiễu nền phòng |

*Bảng 1.3.5e: So sánh bản chất giữa việc cắt lặng bằng Librosa và ngưỡng lặng của Praat.*

---

## 5. `get_local_chunk` và `equalize_local_chunk`: Cắt Đoạn và Co Giãn Thời Gian

### 5.1. `get_local_chunk`: Cắt đoạn cao độ theo mốc từ
```python
i = int((t / D) * N)
```
- $t$: Mốc thời gian của từ (giây) do Whisper cung cấp.
- $D$: Tổng thời lượng của tệp âm thanh (giây).
- $N$: Tổng số điểm cao độ trong mảng `pitch`.
- Sai lệch tiềm ẩn: Công thức tuyến tính này bỏ qua độ lệch tâm pha ban đầu $20\text{ ms}$, gây lệch tối đa khoảng nửa khung ($\le 2$ điểm cao độ).

### 5.2. `equalize_local_chunk`: Co giãn thời gian bằng nội suy tuyến tính
```python
interp_indices = np.linspace(0, len(chunk) - 1, target_len)
equalized = np.interp(interp_indices, np.arange(len(chunk)), chunk)
```
Co giãn đoạn cao độ của người đọc về đúng số điểm của từ tương ứng trong giọng tham chiếu để so sánh từng điểm.

### 5.3. Nguy cơ tiềm ẩn: Sinh $F_0$ giả mạo khi nội suy qua ranh giới vô thanh ($0\text{ Hz}$)
Hàm `np.interp` không biết số $0$ là "Vô thanh". Giữa hai điểm $[0, 200]\text{ Hz}$, phép nội suy sinh ra điểm $100\text{ Hz}$ — một tần số giả mạo không có thật trong giọng nói, lọt qua bộ lọc thanh tính và làm suy giảm nhân tạo hệ số Pearson $r$.

---

## 6. `dynamic_sliding_window_pearson`: Đo Ngữ Điệu Bằng Cửa Sổ Trượt

### 6.1. Mã nguồn
```python
def dynamic_sliding_window_pearson(user_p, sarah_p, word_count):
    N = len(user_p)
    K = max(1, word_count)
    window_size = max(4, int((2 * N) / (K + 2)))
    step_size = max(1, window_size // 2)
    ...
```

### 6.2. Kích thước cửa sổ động theo số từ
Kích thước cửa sổ $W = \frac{2N}{K+2}$ bảo đảm mỗi cửa sổ bao trọn khoảng **2 từ** liên tiếp, và bước trượt $S = W/2$ tạo độ gối chồng 50%.

### 6.3. Bộ lọc điểm hữu thanh
```python
mask = (u > 0) & (v > 0)
```
Chỉ tính Pearson khi cả hai giọng cùng phát ra âm hữu thanh. Nếu số điểm hữu thanh $< 3$ hoặc phương sai bằng 0, gán `np.nan`.

### 6.4. Ý nghĩa vật lý của Pearson $r$
Pearson $r$ **bất biến đối với phép biến đổi afin dương** ($r(X, aY + b) = r(X, Y)$ với mọi $a > 0$). Giọng nam trầm hơn giọng nữ 1 quãng tám ($F_{0, \text{nam}} = 0{,}5 F_{0, \text{nữ}}$) vẫn đạt $r = 1{,}0$ nếu ngữ điệu cùng lên bổng xuống trầm. Pearson $r$ đo **hình thái ngữ điệu**, không đo độ cao tuyệt đối.

---

## 7. `summarize_pearson` và `summarize_sentence_reports`: Từ Cửa Sổ Đến Điểm Số

### 7.1. Tổng hợp điểm số cho một câu
```python
valid = values[np.isfinite(values)]
mean_r = float(np.maximum(valid, 0).mean())
```
1. Loại bỏ các cửa sổ NaN.
2. Kẹp toàn bộ các giá trị tương quan âm hoặc bằng 0 về mức 0 (`np.maximum(valid, 0)`): xem tương quan âm là sai ngữ điệu, không phạt âm thêm.
3. Tính trung bình cộng sinh ra điểm số `mean_r` nằm trong $[0, 1]$.

*Ví dụ số:* Dãy $[0{,}9;\ 0{,}8;\ \text{NaN};\ -0{,}4;\ 0{,}7;\ 0{,}6;\ \text{NaN};\ 0{,}85;\ 0{,}75]$.
- Bỏ 2 NaN $\implies$ còn 7 giá trị.
- Kẹp $-0{,}4 \to 0$.
- Tổng: $0{,}9 + 0{,}8 + 0 + 0{,}7 + 0{,}6 + 0{,}85 + 0{,}75 = 4{,}6$.
- Điểm: $\text{mean\_r} = 4{,}6 / 7 \approx \mathbf{0{,}657}$.

### 7.2. Thống kê tích lũy nhiều câu (`summarize_sentence_reports`)
Đếm số lượng câu đạt điểm $\ge 0{,}9; \ge 0{,}8; \dots; \ge 0{,}3$.

---

## 8. `evaluator.py`: Nhận Diện Mốc Thời Gian Bằng Whisper và Các Phương Án Nhẹ Hơn

### 8.1. Mã nguồn chính
```python
def load_stt_model(model_name="base"):
    torch.set_num_threads(min(4, torch.get_num_threads()))
    return whisper.load_model(model_name)


def get_user_timestamps(audio_path, model):
    audio, sr = sf.read(audio_path, dtype="float32")
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    result = model.transcribe(audio, word_timestamps=True, fp16=False, language="en")
    return [
        dict(word=normalize_word(w["word"]), start=w["start"], end=w["end"])
        for s in result.get("segments", [])
        for w in s.get("words", [])
    ]
```

### 8.2. Kiến trúc song song hai luồng (Log-Mel Frontend vs. Pitch Stream)
- `evaluator.py` nạp tệp âm thanh 24 kHz, lấy mẫu lại về **16 kHz** để cấp cho Whisper. Whisper biến đổi thành **Log-Mel Spectrogram** (Mục 1.3) để nhận dạng từ và trích xuất mốc thời gian ($w_{\text{start}}, w_{\text{end}}$).
- Luồng đo cao độ Praat giữ nguyên tín hiệu 24 kHz để bảo toàn độ phân giải chu kỳ thanh quản.
- Đây chính là sự hiện thực hóa rõ nét của **mô hình hai luồng xử lý song song** ở Mục 0.

### 8.3. Có thể thay Whisper bằng thuật toán nhẹ hơn không?

**Vì sao câu hỏi này đáng hỏi:**
Trong bài toán chấm điểm phát âm, **văn bản chuẩn đã biết trước 100%**. Việc chạy một mô hình nhận dạng tiếng nói lớn (hàng trăm triệu tham số như Whisper) chỉ để đoán lại chữ và lấy mốc thời gian gián tiếp là sự lệch pha giữa công cụ và nhiệm vụ. Có hai phương án nhẹ hơn và chính xác hơn:

**Phương án 1 — Căn chỉnh cưỡng bức (Forced Alignment):**
Thay vì hỏi "người này nói gì", hỏi thẳng "câu đã biết này khớp vào đoạn âm thanh này ở đâu":
- **Montreal Forced Aligner (MFA):** dùng mô hình âm học GMM-HMM hoặc nơ-ron nhỏ cộng từ điển phát âm. Độ chính xác ranh giới từ $< 20\text{ ms}$.
- **Kaldi / Vosk:** nhẹ, chạy mượt trên CPU.
- **`torchaudio.pipelines.MMS_FA`:** mô hình wav2vec2 căn chỉnh chuyên dụng, chạy vài chục mili-giây trên CPU.
*Ưu điểm:* Vì đã biết văn bản, thuật toán **không thể nhận dạng sai chữ** — sai số chỉ nằm ở trục thời gian.

**Phương án 2 — Dynamic Time Warping (DTW) trên chuỗi 80 Log-Mel:**
Bỏ luôn bước nhận dạng chữ. Ta đã có sẵn ma trận 80 dải Log-Mel của câu mẫu và của người học (tính trên FPGA từ Mục 1.3). DTW tìm đường đi tối ưu uốn cong trục thời gian giữa hai chuỗi vector đặc trưng:
$$D[i][j] = \lVert a_i - b_j \rVert^2 + \min\bigl(D[i-1][j],\; D[i][j-1],\; D[i-1][j-1]\bigr)$$
*Ưu điểm:* **Hoàn toàn không cần mô hình nhận dạng nào**, tận dụng trực tiếp ma trận 80 Log-Mel do FPGA tính sẵn!

| Tiêu chí | Whisper (hiện tại) | Forced Alignment | DTW trên Mel |
|---|:---:|:---:|:---:|
| Cần mô hình nhận dạng | Có (lớn) | Không | Không |
| Cần văn bản chuẩn | Không | Có | Không (chỉ cần câu mẫu) |
| Sai số ranh giới từ | Phụ thuộc nhận dạng | $< 20\text{ ms}$ | Phụ thuộc độ dài câu |
| Chạy được trên CPU | Chậm | Nhanh | Rất nhanh |
| Rủi ro chính | Nhận dạng sai chữ | Cần từ điển phát âm | Lệch khi đọc sai từ |

---

## 9. Bảng Tổng Hợp Đối Sánh Toàn Diện: Lý Thuyết Mục 1.3.5 vs. Mã Nguồn Python

| Tiêu chí kỹ thuật | Lý thuyết Mục 1.3.5 (Đích đến FPGA) | Hiện thực trong mã nguồn Python | Đánh giá và Hệ quả kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Công cụ đo cao độ** | Tự thiết kế lõi phần cứng RTL (MAC, ROM) | Thư viện liên kết `parselmouth` (Praat C++) | Bản Python dùng nguyên bản thuật toán Praat máy trạm |
| **Tần số lấy mẫu $f_s$** | Chuẩn hóa $16.000\text{ Hz}$ | $24.000\text{ Hz}$ (do Kokoro TTS sinh ra) | Dải lag đổi thành $\tau \in [40, 320]$, khung $L = 960$ |
| **Dải đo cao độ $F_0$** | $75\text{ Hz} \le F_0 \le 600\text{ Hz}$ | $75\text{ Hz} \le F_0 \le 600\text{ Hz}$ (mặc định) | Trùng khớp hoàn toàn về dải tần số vật lý |
| **Thời lượng khung / Bước** | $40\text{ ms}$ ($640$ mẫu) / $10\text{ ms}$ ($160$ mẫu) | $40\text{ ms}$ ($960$ mẫu) / $10\text{ ms}$ ($240$ mẫu) | Trùng khớp về mặt thời lượng vật lý |
| **Loại cửa sổ phân tích** | Cửa sổ Hanning đối xứng bậc 640 | Hanning (`very_accurate = False`) | Trùng khớp về bản chất giải tích |
| **Bù suy hao cửa sổ** | Bảng tra ROM $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ | Praat tự động chia $r_x[\tau] = \mathcal{R}_x[\tau]/\mathcal{R}_w[\tau]$ | Trùng khớp về mặt bản chất giải thuật |
| **Cơ chế chọn đỉnh** | Chọn cực đại tức thời cục bộ (1 ứng viên) + Lọc trung vị 3 điểm | 15 ứng viên + Viterbi + Nội suy cực trị | Bản Python mượt hơn, bản FPGA tối ưu độ trễ bằng 0 |
| **Lọc thông cao HPF 60 Hz**| Bắt buộc có ở tầng tiền xử lý | Không xuất hiện trong mã nguồn | Chấp nhận được vì âm thanh Kokoro tổng hợp rất sạch |
| **Khử khoảng lặng** | Ngưỡng năng lượng khung tức thời tĩnh | Thêm `librosa.trim` $30\text{ dB}$ ở hai đầu | Bước cắt của Python nhằm mục đích đồng bộ trục thời gian |
| **Phương pháp đối sánh** | Phân loại thanh điệu hoặc Pearson $r$ | Cửa sổ trượt Pearson $r$ theo kích thước động | Khẳng định Pearson đo hình thái, không đo tần số tuyệt đối |
| **Tần số lấy mẫu STT** | $16\text{ kHz}$ (chuẩn Log-Mel STFT) | $16\text{ kHz}$ (Whisper resample) | Tách bạch hoàn hảo hai luồng Mel và Pitch |

*Bảng 1.3.5f: Bảng tổng hợp đối chiếu toàn diện giữa thiết kế lý thuyết Mục 1.3.5 và mã nguồn thực tế.*

---

## 10. Danh Sách 8 Điểm Vênh Kỹ Thuật và Bài Học Thiết Kế Hệ Thống

1. **Bỏ rơi mảng mốc thời gian thực `xs()`:** Việc quy đổi mốc từ sang chỉ số khung qua tỉ lệ $i = \lfloor (t/D) \cdot N \rfloor$ tạo ra sai lệch tối đa khoảng nửa khung ($\le 2$ điểm cao độ) do bỏ qua độ lệch tâm pha ban đầu $20\text{ ms}$.
2. **Nguy cơ sinh tần số $F_0$ giả mạo khi nội suy:** Phép gọi `np.interp` qua các ranh giới vô thanh ($0\text{ Hz}$) sinh ra các giá trị tần số nhân tạo nằm giữa 0 và tần số thật, làm méo mó hệ số Pearson $r$.
3. **Độ lệch tần số lấy mẫu ($24\text{ kHz}$ vs. $16\text{ kHz}$):** Không được áp dụng trực tiếp bảng tra ROM hoặc dải lag $[27, 213]$ của tài liệu vào dữ liệu âm thanh $24\text{ kHz}$ của dự án mà phải tính lại bảng tra theo $[40, 320]$.
4. **Vắng bóng bộ lọc thông cao HPF 60 Hz:** Khi chuyển sang xử lý giọng nói người thật thu qua micrô ở môi trường thực địa trên FPGA, bắt buộc phải khôi phục khối HPF 60 Hz của Mục 1.1.5 để bảo vệ thuật toán khỏi nhiễu tần số thấp.
5. **Hiệu ứng kẹp điểm không âm ($r \le 0 \to 0$):** Làm tăng điểm trung bình `mean_r` của câu so với trung bình số học thực tế, đồng thời làm mất khả năng phân biệt giữa các mức độ đọc sai ngữ điệu trầm trọng.
6. **Vai trò thực tế của `evaluator.py`:** Không thực hiện chức năng đánh giá ngữ điệu mà chỉ đóng vai trò trích xuất mốc thời gian từ bằng mô hình Whisper.
7. **Pearson tính trên Hertz tuyến tính:** Việc tính tương quan trực tiếp trên thang đo Hz thay vì thang đo bán âm (semitones / thang log) tạo ra trọng số thiên vị lớn hơn cho các đoạn luyến ở vùng âm vực cao.
8. **Sai số dấu phẩy động ở ngưỡng tích lũy:** Biểu thức `threshold / 10` trong Python gặp sai số dấu phẩy động rất nhỏ của chuẩn IEEE-754 ($0{,}30000000000000004$), cần lưu ý khi xây dựng logic so sánh cứng trên phần cứng RTL.
