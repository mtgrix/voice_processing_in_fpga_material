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

---

## 1. Phương pháp thô sơ bị bác bỏ: Dùng STFT và Argmax trên phổ tần số

Phương pháp trực giác ngây thơ nhất là: *Mục 1.3 đã tính sẵn biến đổi Fourier rời rạc (FFT 512 điểm), vậy tại sao không tìm bin có biên độ lớn nhất ($\text{argmax}$) ở dải tần số thấp để làm $F_0$?*

Cách làm này thất bại ngay từ bước kiểm tra thực nghiệm vì hai bức tường vật lý:

**1. Độ phân giải tần số quá thô ($\Delta f_{\text{bin}} = 31{,}25\text{ Hz}$):**
Lưới FFT $N = 512$ điểm ở tần số lấy mẫu $f_s = 16.000\text{ Hz}$ tạo ra bước nhảy giữa hai bin kế tiếp là:

$$\Delta f_{\text{bin}} = \frac{f_s}{N} = \frac{16.000}{512} = 31{,}25\text{ Hz}$$

Các vạch tần số rời rạc chỉ có thể nhận giá trị: $62{,}5\text{ Hz}$ (bin 2), $93{,}75\text{ Hz}$ (bin 3), $125{,}0\text{ Hz}$ (bin 4), $156{,}25\text{ Hz}$ (bin 5)... Giả sử một giọng nam nói ở cao độ $F_0 = 105\text{ Hz}$: tần số này rơi vào giữa bin 3 và bin 4. Thuật toán chọn bin nào cũng tạo ra sai số tuyệt đối từ $11\text{--}20\text{ Hz}$ (sai lệch $> 15\%$). Khi đem chuỗi $F_0$ giật cục này tính tương quan Pearson với đường cao độ thực tế của Praat, hệ số tương quan $r$ sẽ sụt giảm mạnh (không đạt ngưỡng tin cậy).

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
3. Đại lượng "$-\tau$" xuất hiện do khi trượt đi $\tau$ mẫu, đúng $\tau$ mẫu ở đuôi của bản trượt bị thò ra ngoài phạm vi lưu trữ của khung $L$ mẫu (Hình 1.3.5aA).
4. Cận trên $L - 1 - \tau$ hoàn toàn là điều kiện biên kỹ thuật của khung dữ liệu hữu hạn, **đây KHÔNG phải là phép trừ phần đối xứng**.

**Cơ chế theo dấu của tổng tự tương quan trong 3 trường hợp:** Dấu và độ lớn của tổng tự tương quan $\mathcal{R}_x[\tau]$ được quyết định bởi tính đồng pha giữa bản gốc và bản trượt:
1. **Khi $\tau = 0$ (Trùng khớp):** Bản sao nằm trùng khít lên bản gốc ($x[n]$ nhân với chính nó). Từng tích cặp mẫu trở thành bình phương: $x[n] \cdot x[n] = x^2[n] \ge 0$. Mọi số hạng đều không âm, cộng dồn tạo thành:
   $$\mathcal{R}_x[0] = \sum_{n=0}^{L-1} x^2[n] = E_{\text{frame}}$$
   chính là tổng năng lượng tức thời của toàn khung $L$ mẫu. Đây là giá trị **cực đại toàn cục** của hàm tự tương quan.
2. **Khi $0 < \tau < T_0$ (Lệch pha):** Bản sao bị lệch pha so với bản gốc. Các đỉnh sóng dương ($+$) của bản này rơi vào sườn sóng hoặc đáy sóng âm ($-$) của bản kia. Phép nhân giữa mẫu dương và mẫu âm sinh ra tích âm: $(+) \cdot (-) < 0$. Khi cộng dồn, các tích âm và dương triệt tiêu lẫn nhau, khiến tổng tự tương quan sụt giảm rõ rệt.
3. **Khi $\tau = T_0$ (Đúng một chu kỳ cơ bản):** Sóng âm tuần hoàn lặp lại đúng một chu kỳ. Đỉnh dương của bản sao trượt đúng vào đỉnh dương của bản gốc: $(+) \cdot (+) > 0$. Đáy âm của bản sao cũng trượt đúng vào đáy âm của bản gốc: $(-) \cdot (-) > 0$. Hầu hết các cặp mẫu đều cho tích dương, khiến tổng tự tương quan vọt lên tạo thành một **đỉnh cực đại cục bộ thứ nhất** tại $\tau^* = T_0$ (Hình 1.3.5aB).

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
                |<--- Độ trễ tau --->|
Bản trượt x[n+tau]:                  | tau | tau+1 | ... | L - 1 | [tau mẫu thò ra ngoài]
                |<------------------->|
                 Vùng nhân hợp lệ: n in [0, L - 1 - tau] ==> L - tau cặp mẫu

Panel B: Đồ thị hàm tự tương quan thô R_x[tau] và Dải tìm kiếm [tau_min, tau_max]
R_x[tau]
   ^
   |  R_x[0] = E_frame
   *  \
   |   \  Dải tìm kiếm hợp lệ: tau in [27, 213] (75--600 Hz)
   |    \
   |     \             Đỉnh tau* = 133 (F_0 ~ 120.3 Hz)
   |  Bỏ  \                  *
   |  qua  \                / \
   | tau<27 \              /   \
---+---------+------------+-----+------------------------------------> tau (mẫu)
   0      tau_min=27   tau*=133  \                      tau_max=213   L=640
                                  \-------------------/
```

*Hình 1.3.5a: Cơ chế chỉ số mảng giới hạn khung $(L - 1 - \tau)$ và đồ thị hàm tự tương quan thô $\mathcal{R}_x[\tau]$ trong dải quét $[27, 213]$ mẫu.*

**Đọc Hình 1.3.5a (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Bản gốc $x[n]$ (Thanh màu xanh nhạt phía trên):** Thể hiện mảng dữ liệu mẫu âm thanh của khung $L = 640$ mẫu được lưu tuần tự trong bộ nhớ, có chỉ số $n$ chạy từ 0 đến $L - 1$ (0 đến 639). Vùng tô xanh đậm hơn là đoạn chỉ số $n \in [0, L - 1 - \tau]$ có thể bắt cặp.
2. **Panel A — Bản trượt $x[n + \tau]$ (Thanh màu cam phía dưới):** Thể hiện bản sao tín hiệu bị dịch trượt sang phải một khoảng trễ $\tau$ mẫu. Mẫu đầu tiên của bản trượt bắt đầu tại chỉ số $\tau$, và mẫu có chỉ số $L - 1$ của bản gốc lúc này đối diện với chỉ số $L - 1 - \tau$ của bản trượt.
3. **Panel A — Mũi tên hai chiều màu cam (Độ trễ $\tau$ mẫu):** Đo khoảng cách dịch chuyển giữa điểm gốc 0 của bản gốc và điểm bắt đầu của bản trượt.
4. **Panel A — Khối nét đứt màu đỏ nhạt ($\tau$ mẫu thò ra ngoài):** Khi dịch trượt sang phải một khoảng $\tau$, đúng $\tau$ mẫu ở phần đuôi của bản trượt bị tràn ra ngoài phạm vi lưu trữ của khung $L$ mẫu. Các mẫu này không có mẫu tương ứng của bản gốc để nhân.
5. **Panel A — Mũi tên hai chiều màu xanh lam (Vùng nhân hợp lệ):** Nằm ở đáy Panel A, đánh dấu đoạn chỉ số $n \in [0, L - 1 - \tau]$ gồm đúng $L - \tau$ cặp mẫu tương ứng mà cả bản gốc và bản trượt đều nằm trong phạm vi lưu trữ hợp lệ của khung. Đây chính là xuất xứ trực quan của cận trên $L - 1 - \tau$ trong Công thức (1).
6. **Panel B — Trục tung $\mathcal{R}_x[\tau]$ và Trục hoành $\tau$ (mẫu):** Trục tọa độ biểu diễn giá trị của hàm tự tương quan thô theo độ trễ $\tau$.
7. **Panel B — Điểm chấm tròn màu đỏ $\mathcal{R}_x[0] = E_{\text{frame}}$:** Nằm tại $\tau = 0$ trên trục tung, đại diện cho năng lượng tức thời của toàn khung khi tín hiệu nhân với chính nó. Đây là đỉnh cực đại toàn cục.
8. **Panel B — Vùng màu đỏ nhạt (Bỏ qua $\tau < 27$):** Trải từ $\tau = 0$ đến $\tau = 26$. Đây là sườn dốc quán tính âm thanh đi xuống từ $\mathcal{R}_x[0]$. Vùng này bị loại bỏ để tránh việc thuật toán bắt nhầm các độ trễ nhỏ cạnh 0 làm sai lệch kết quả đo.
9. **Panel B — Vùng màu xanh lá nhạt (Dải tìm kiếm hợp lệ):** Trải từ $\tau_{\text{min}} = 27$ đến $\tau_{\text{max}} = 213$ mẫu (tương ứng dải tần $75\text{--}600\text{ Hz}$). Đây là không gian duy nhất mà thuật toán quét để tìm cực đại, bao gồm đúng 187 giá trị lag nguyên theo Công thức (3) và (4).
10. **Panel B — Điểm chấm tròn màu xanh lam $\tau^* = 133$:** Đỉnh cực đại cục bộ thứ nhất rơi trúng vào dải hợp lệ, ứng với chu kỳ tuần hoàn dây thanh $T_0 = 133\text{ mẫu}$, xác định cao độ giọng nói $F_0 \approx 120{,}3\text{ Hz}$.

---

## 3. Cắt Khung, Chuẩn Hóa Cửa Sổ và Giải Phẫu 10 Tham Số Praat

**Chuyển tiếp từ Mục 1.3: Vì sao đổi sang cửa sổ Hanning và độ dài $L = 640$ mẫu?**
Ở Mục 1.2 và 1.3, chuỗi tiền xử lý dùng khung $L = 400$ mẫu ($25\text{ ms}$) kết hợp cửa sổ Hamming. Thời lượng $25\text{ ms}$ là tiêu chuẩn vàng để trích xuất 80 dải Log-Mel vì đặc tính âm học của khẩu hình miệng giữ trạng thái bán dừng (quasi-stationary) trong khoảng 20--30 ms. Tuy nhiên, khi bước sang bài toán đo cao độ $F_0$, ta bắt buộc phải thay đổi cả độ dài khung lẫn dạng cửa sổ:
1. **Độ dài khung $L = 640$ mẫu ($40\text{ ms}$):** Theo quy tắc của Boersma (1993) trong Praat, khung phân tích cao độ phải chứa **tối thiểu 3 chu kỳ** của tần số thấp nhất cần đo (`pitch_floor = 75 Hz`). Chu kỳ dài nhất là $T_{\text{max}} = 16.000 / 75 \approx 213{,}33\text{ mẫu}$ ($13{,}33\text{ ms}$). Khung phải dài ít nhất:
   $$T_{\text{frame}} \ge 3 \times T_{\text{max}} = 3 \times 13{,}33\text{ ms} = 40\text{ ms} \implies L = 16.000 \times 0{,}040 = \mathbf{640\text{ mẫu}}$$
   Khung 400 mẫu (25 ms) của STFT chỉ chứa được 1,8 chu kỳ của giọng nam 75 Hz, hoàn toàn không đủ độ dài để bản trượt $x[n + \tau]$ bao trọn chu kỳ lặp lại thứ hai!
2. **Vì sao chọn Hanning thay vì Hamming:** Cửa sổ Hamming không triệt tiêu về 0 ở hai đầu biên ($w[0] = w[L-1] = 0{,}08$), gây ra bước nhảy gián đoạn biên khi tính tích trượt giữa hai bản tín hiệu. Ngược lại, cửa sổ Hanning vuốt mượt về đúng 0 ở cả hai đầu ($w[0] = w[L-1] = 0$), giúp hàm tự tương quan của cửa sổ $\mathcal{R}_w[\tau]$ triệt tiêu êm dịu mà không sinh ra các gợn sóng biên giả tạo. Đồng thời, hàm Hanning đối xứng bậc 640 dễ dàng nén một nửa vào bảng tra ROM 320 phần tử trên FPGA, tiết kiệm tài nguyên silicon.

### A. Độ dài khung $L = 640$ mẫu: Giá trị thiết kế cho dải trầm $75\text{ Hz}$

Con số $L = 640$ mẫu ($40\text{ ms}$ tại $f_s = 16.000\text{ Hz}$) là **giá trị thiết kế kỹ thuật điển hình** được quy chuẩn hóa khi ấn định giới hạn đáy cao độ `pitch_floor = 75 Hz` theo quy tắc 3 chu kỳ ở trên.

### B. Cửa sổ Hanning vs. Gaussian và Hệ số chuẩn hóa $\mathcal{R}_w[\tau]$ (Boersma, 1993)

Trong thực tế, Praat ưu tiên sử dụng cửa sổ **Gaussian** vì đặc tính dập tắt búp phụ vượt trội trong miền tần số. Tuy nhiên, việc lựa chọn **cửa sổ Hanning đối xứng bậc 640** ở đây là một **lựa chọn kỹ thuật đơn giản hóa có chủ đích (deliberate engineering trade-off)**: Hanning dễ dàng sinh từ hàm cosin, đối xứng chặt chẽ, dễ nén một nửa vào ROM bảng tra, tiết kiệm tài nguyên FPGA mà vẫn đảm bảo độ mịn biên.

Tuy nhiên, việc nhân cửa sổ làm xuất hiện hiện tượng sụt dốc tự nhiên của đồ thị tự tương quan theo độ trễ $\tau$ do **hai nguyên nhân vật lý độc lập**:
1. **Nguyên nhân hình học (Số cặp mẫu giảm):** Như đã chỉ ra ở Mục 2, số cặp mẫu tham gia vào tổng tự tương quan giảm tuyến tính từ $L$ cặp (tại $\tau = 0$) xuống còn $L - \tau$ cặp (tại độ trễ $\tau$). Ít số hạng cộng dồn hơn khiến tổng số học đương nhiên bị suy giảm (Hình 1.3.5bA).
2. **Nguyên nhân trọng số cửa sổ (Vuốt biên):** Cửa sổ Hanning vuốt hai đầu về 0. Khi trượt bản sao đi một khoảng $\tau$, tích của hai trọng số cửa sổ $w[n] \cdot w[n + \tau]$ suy giảm phi tuyến theo $\tau$.

Hàm tự tương quan của chính cửa sổ phân tích:

$$\mathcal{R}_w[\tau] = \sum_{n=0}^{L - 1 - \tau} w[n] \cdot w[n + \tau]$$

**gói trọn cả hai nguyên nhân nói trên** (vừa phản ánh sự co hẹp của cận lấy tổng từ 0 đến $L - 1 - \tau$, vừa tích hợp sự suy giảm của tích các trọng số cửa sổ).

**Trực giác trước khi viết công thức: hai quả núi Hanning trượt lên nhau.**

**Bước 1 — Vì sao phải vuốt khung thành "quả núi"?** Nếu cắt khung $L$ mẫu bằng một nhát kéo thẳng (cửa sổ chữ nhật), hai đầu khung kết thúc đột ngột giữa một dao động đang chạy. Chỗ gãy ấy giống như bấm tắt loa giữa chừng: nó sinh ra các thành phần tần số cao không có trong giọng nói thật (edge discontinuity). Cửa sổ Hanning thay nhát kéo bằng một đường dốc đứng từ $0$ lên đỉnh rồi xuống $0$: khung có dạng một quả núi, hai chân núi chạm đất nên không còn chỗ gãy.

**Bước 2 — Trượt hai quả núi lên nhau.** Bản sao là quả núi thứ hai, trượt sang phải đúng $\tau$ mẫu. Khi $\tau = 0$, hai quả núi chồng khít và mép núi cao nhất vẫn nguyên. Khi $\tau$ lớn dần, đỉnh quả thứ hai rời khỏi đỉnh quả thứ nhất, và $\tau$ mẫu ở đuôi quả thứ hai thò ra ngoài cửa sổ, không còn mẫu nào của quả thứ nhất đối diện để nhân. Phần chồng nhau vừa **hẹp lại** (số cặp giảm từ $L$ xuống $L - \tau$), vừa **thấp dần** ở hai bên vì hai chân núi chỉ còn gặp nhau ở cùng một độ cao nhỏ. Diện tích chồng nhau chính là $\mathcal{R}_w[\tau]$ — tự tương quan của **chính cửa sổ**.

**Phân đôi tín hiệu thành hai lớp: "âm thanh thật" và "cái khuôn".** Ở mỗi độ trễ, mỗi cặp mẫu cho ta hai thông tin tách biệt:
- Mẫu âm thanh $x[n]$ và $x[n + \tau]$ liền nhau bao nhiêu — phản ánh **tính tuần hoàn thật** của giọng.
- Hai trọng số cửa sổ $w[n]$ và $w[n + \tau]$ còn cao bao nhiêu — phản ánh **cái khuôn** mà ta đã ép lên tín hiệu.

Vì phép nhân là tuyến tính, hai lớp này nhân vào nhau:

$$\text{tích từng cặp} = \underbrace{x[n]\,x[n+\tau]}_{\text{âm thanh thật}} \cdot \underbrace{w[n]\,w[n+\tau]}_{\text{cái khuôn}}$$

Cộng dồn mọi cặp:

$$\mathcal{R}_x[\tau] = \sum_{n=0}^{L-1-\tau} \big(x[n]\,x[n+\tau]\big)\big(w[n]\,w[n+\tau]\big)$$

và vì $w[n]\,w[n+\tau] \approx \mathcal{R}_w[\tau]/L$ theo nghĩa trung bình trên toàn khung, ta ghi gọn mức đo được của âm thanh thật là

$$r_{\text{thật}}[\tau] = \frac{\mathcal{R}_x[\tau]}{\mathcal{R}_w[\tau]}$$

Hai đại lượng trung gian $r_x[\tau]$ và $\tilde{r}_x[\tau]$ mà tài liệu Praat hay dùng không cần đến nữa: ta chuyển thẳng từ $\mathcal{R}_x[\tau]$ sang đại lượng bù.

**Bù lại cái khuôn: nhân với một hằng số lấy từ ROM.** Ở $\tau = 0$ cái khuôn còn nguyên, nên mức đo được đúng bằng mức thật. Ở độ trễ lớn, cái khuôn chỉ còn một phần, khiến mức đo bị dìm xuống. Muốn lấy lại mức thật, ta chia cho phần khuôn còn lại. Phần khuôn còn lại đã được đo sẵn, chỉ phụ thuộc vào $\tau$ và cửa sổ, **không phụ thuộc vào tín hiệu**. Vì vậy ta tính trước một **hệ số phóng đại** và nạp vào ROM:

$$C[\tau] = \frac{\mathcal{R}_w[0]}{\mathcal{R}_w[\tau]} \quad (\ge 1,\ \text{tăng dần theo } \tau)$$

Giá trị bù thực tế dùng để ra quyết định là

$$\mathcal{R}_{\text{bù}}[\tau] = \mathcal{R}_x[\tau] \cdot C[\tau]$$

và chia cho năng lượng khung để so với ngưỡng:

$$\frac{\mathcal{R}_{\text{bù}}[\tau^*]}{\mathcal{R}_x[0]} \ge \theta_{\text{voice}} = 0{,}45 \iff \mathcal{R}_{\text{bù}}[\tau^*] \ge 0{,}45 \cdot \mathcal{R}_x[0]$$

Trên FPGA, phép so sánh này chỉ cần **một phép nhân** với hệ số lấy từ bảng tra và **một phép so sánh số nguyên**; không cần bộ chia.

> **$\blacktriangleright$ BẢNG DỊCH NHANH: 4 KÝ HIỆU CỐT LÕI SANG HÌNH ẢNH QUẢ NÚI**
>
> | Ký hiệu | Nó là gì trong hình ảnh quả núi | Ví dụ số tại $\tau = 133$ |
> |---|---|---|
> | $\mathcal{R}_w[\tau]$ | Diện tích chồng nhau của **hai vỏ núi rỗng** (chỉ có cửa sổ, không có âm thanh). $\tau = 0$ là chồng khít, $\tau$ lớn thì chồng hẹp và thấp. | $0{,}40$ — vỏ còn $40\%$ ($\approx 60\%$ đã hụt) |
> | $\mathcal{R}_x[\tau]$ | Tự tương quan của **âm thanh thật** đã bị cái khuôn đè lên. Mức đo thô bị dìm theo đúng phần vỏ còn lại. | $0{,}90 \times 0{,}40 = 0{,}36$ |
> | $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ | **Hệ số phóng đại** lấy từ ROM: chia cho phần vỏ còn lại để lấy lại mức thật. | $1{,}0 / 0{,}40 = 2{,}5$ |
> | $\mathcal{R}_{\text{bù}}[\tau] = \mathcal{R}_x[\tau] \cdot C[\tau]$ | Mức thật sau khi kéo vỏ núi về đủ chiều cao, đem so với ngưỡng. | $0{,}36 \times 2{,}5 = 0{,}90$ |
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
> Tức là $\mathcal{R}_x[\tau]$ **đã mang sẵn** phần vỏ bên trong nó. Nhân thêm $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ là **rút** phần vỏ đó ra, còn lại mức giống thật nhân với $\mathcal{R}_w[0]$ (một hằng số). Nếu chia cho $1$ thay vì nhân với $C[\tau]$, ta sẽ giữ nguyên phần vỏ bị hụt và đọc sai.
>
> **Tính từng bước với một khung giọng nam $120\text{ Hz}$ ($\tau = 133$ mẫu), ngưỡng $\theta_{\text{voice}} = 0{,}45$:**
> 1. Vỏ núi còn: $\mathcal{R}_w[133] / \mathcal{R}_w[0] = 0{,}40$. Ở độ trễ này cái khuôn đã hụt $60\%$.
> 2. Mức đo thô: giọng thật giống nhau $0{,}90$ ở một chu kỳ, nên $\mathcal{R}_x[133] / \mathcal{R}_x[0] = 0{,}90 \times 0{,}40 = 0{,}36$.
> 3. So thẳng với ngưỡng: $0{,}36 < 0{,}45$ ⇒ thuật toán **nhầm là vô thanh**, mất cao độ. Đây chính là lỗi nghịch lý: giọng rất đều nhưng vẫn bị bỏ.
> 4. Phóng đại: $C[133] = 1{,}0 / 0{,}40 = 2{,}5$.
> 5. Sau bù: $0{,}36 \times 2{,}5 = 0{,}90$, vượt ngưỡng $0{,}45$ rõ ràng ⇒ bắt đúng $F_0$.
>
> **Liên hệ với `octave_cost = 0,01`:** Hệ số $C[\tau]$ chỉ đo lại đúng phần vỏ đã hụt, nên **không thiên vị** đỉnh nào về mặt tần số. Việc chọn giữa đỉnh $1T_0$ và $2T_0$ lại là câu chuyện khác, được xử lý trong mục tiếp theo.

**Phân biệt rõ ràng hai kiểu lỗi suy diễn cao độ:**
1. **Lỗi phán nhầm Vô thanh (Voiced $\to$ Unvoiced Error):** Khi không bù suy hao cửa sổ, đỉnh tương quan ở lag lớn (ví dụ giọng nam $120\text{ Hz}$ tại $\tau^* = 133$) bị dìm tụt xuống mức $0{,}36$. Vì $0{,}36 < \theta_{\text{voice}} = 0{,}45$ (ngưỡng thanh tính mặc định), thuật toán phán đoán nhầm khung này là âm vô thanh hoặc khoảng lặng và gán $F_0 = 0$, làm mất cao độ (Hình 1.3.5bC).
2. **Lỗi nhảy quãng tám (Octave Jump):** Xảy ra khi thuật toán chọn nhầm đỉnh tại chu kỳ kép $\tau = 2T_0$ (nhảy xuống quãng tám dưới $F_0/2$) hoặc đỉnh tại $\tau = T_0/2$ (nhảy lên quãng tám trên $2F_0$). Lỗi này được xử lý độc lập bởi cơ chế phạt log-lag `octave_cost = 0,01` trong Praat, chứ không phải do việc đỉnh rơi xuống dưới ngưỡng thanh tính.

<!-- FIG:ACF_COMPENSATION -->

*Hình 1.3.5b: Hiện tượng co hẹp vùng tích các cặp mẫu và vai trò của hệ số bù suy hao cửa sổ $C[	au] = \mathcal{R}_w[0]/\mathcal{R}_w[	au]$ theo Boersma (1993). Panel A: cửa sổ Hanning là một quả núi, bản sao trượt sang phải $	au$ mẫu nên đuôi bản sao thò ra ngoài khung $L = 640$ mẫu. Panel B: mỗi cặp là hai mảnh núi kẹp vào nhau, số cặp giảm từ $640$ xuống $640 - 	au$. Panel C: khung $F_0 = 200	ext{ Hz}$ ($T_0 = 80$ mẫu), trục tung $R/R_x[0]$; đỉnh $1T_0$ ($	au = 80$) và $2T_0$ ($	au = 160$) lần lượt đi từ $0{,}42$ và $0{,}23$ (chưa bù, đường xám nét đứt) lên khoảng $0{,}47$ và $0{,}35$ (đã bù $C[	au]$, đường xanh), còn đường cam thêm `octave_cost = 0,01`. Ngưỡng thanh tính là $0{,}45$.*

**Đọc Hình 1.3.5b (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Quả núi thứ nhất (đường xanh đậm, vùng tô xanh nhạt):** Khung $L = 640$ mẫu sau khi nhân cửa sổ Hanning, có dạng một quả núi: hai chân chạm $0$, đỉnh ở giữa. Cửa sổ chữ nhật sẽ để hai đầu khung gãy đột ngột; quả núi thì không.
2. **Panel A — Quả núi thứ hai (đường cam):** Bản sao của quả núi thứ nhất, trượt sang phải đúng $	au$ mẫu. Mũi tên hai chiều ở đáy đo đúng khoảng trượt $	au$ này.
3. **Panel A — "Phần thò ra":** $	au$ mẫu ở đuôi quả thứ hai nằm ngoài cửa sổ, không có mẫu nào của quả thứ nhất đối diện để nhân. Mũi tên đỏ chỉ vào chỗ đó. Cùng lúc, phần chồng nhau hẹp lại còn $L - 	au$ cặp và hai chân núi chỉ còn gặp nhau ở độ cao nhỏ, nên phần chồng vừa hẹp vừa thấp. Diện tích chồng nhau chính là $\mathcal{R}_w[	au]$.
4. **Panel B — Bốn cột mẫu:** Mỗi cột là một độ trễ $	au = 0, 80, 160$ và một cột nữa xa hơn. Cột xanh là mảnh núi "bên trái", cột cam là mảnh "bên phải"; mũi tên "kẹp" chỉ cặp mảnh đang dán vào nhau. Từ trên xuống dưới, mảnh cam thấp dần, cho thấy mỗi trọng số tự rơi về $0$.
5. **Panel B — Số cặp giảm:** Nhãn dưới cột ghi $	au = 0$: $640$ cặp; $	au = 80$: $560$ cặp; $	au = 160$: $480$ cặp. Con số $L - 	au$ này là nguyên nhân hình học đầu tiên khiến tổng tương quan thô sụt theo $	au$.
6. **Panel C — Trục tung $R/R_x[0]$ và ngưỡng $0{,}45$:** Khung $F_0 = 200	ext{ Hz}$ ($T_0 = 80$ mẫu). Đường đỏ nét đứt ngang là ngưỡng thanh tính; trục hoành đánh dấu bốn mốc $27$, $80$, $160$, $213$.
7. **Panel C — Đường xám nét đứt (chưa bù):** Hai đỉnh $1T_0$ ($	au = 80$) và $2T_0$ ($	au = 160$) chỉ đạt $0{,}42$ và $0{,}23$; cả hai đều **dưới** ngưỡng $0{,}45$, nên khung bị gán vô thanh.
8. **Panel C — Đường xanh đậm (đã bù $C[	au]$):** Nhân với $C[80] = 1{,}11$ và $C[160] = 1{,}52$, hai đỉnh lên khoảng $0{,}47$ và $0{,}35$; cả hai đều **vượt** ngưỡng. Mũi tên đỏ giữa chấm xám và chấm xanh cho thấy đúng mức nâng bù tại mỗi đỉnh.
9. **Panel C — Đường cam (thêm `octave_cost = 0,01`):** Đường cam gần như trùng đường xanh, chỉ hơi thấp hơn ở đỉnh. Mức phạt nhỏ này đủ để đỉnh $1T_0$ đứng trên đỉnh $2T_0$ khi hai đỉnh xấp xỉ nhau, nhưng không lật ngược một đỉnh vốn đã thua rõ.
10. **Panel C — Dòng chữ xanh đậm ở đáy:** Tóm một câu: đỉnh $1T_0$ (80 mẫu) thắng đỉnh $2T_0$ (160 mẫu) nhờ `octave_cost = 0,01`.

### B'. Hai đỉnh $1T_0$ và $2T_0$: vì sao bù hệ số lại đẩy đỉnh xa lên, và `octave_cost` dọn nốt tàn dư

Một giọng có chu kỳ $T_0$ sẽ lặp lại không chỉ sau một chu kỳ mà còn sau $2T_0$, $3T_0$… nên hàm tự tương quan có **nhiều đỉnh**. Chọn nhầm đỉnh $2T_0$ là đọc cao độ thành $F_0/2$: giọng $200\text{ Hz}$ bị ghi thành $100\text{ Hz}$, tức **rơi đúng một quãng tám** (octave error). Đây là lỗi nguy hiểm nhất của bộ bắt cao độ tự tương quan.

**Vì sao trước khi bù, đỉnh $2T_0$ thấp hơn.** Ở $\tau = 2T_0$, vỏ núi đã hụt nhiều hơn ở $\tau = T_0$, nên mức đo thô bị dìm nhiều hơn, dù "độ giống thật" của giọng ở hai độ trễ này gần như bằng nhau.

**Vì sao sau khi bù, hệ số lại đẩy đỉnh xa lên mạnh hơn.** $C[\tau]$ tăng dần theo $\tau$; đỉnh ở $2T_0$ nằm xa hơn nên có $C[2T_0] > C[T_0]$. Hệ số bù vì vậy **nâng đỉnh $2T_0$ nhiều hơn** đỉnh $T_0$ và có thể kéo hai đỉnh về ngang nhau, tạo nguy cơ lỗi quãng tám thật sự.

**Praat chặn nguy cơ đó bằng `octave_cost = 0,01`.** Với mỗi bậc độ trễ tăng gấp đôi, Praat **trừ đi $0{,}01$** khỏi điểm của đỉnh. Đỉnh $2T_0$ bị trừ một lần $0{,}01$ so với đỉnh $T_0$, nên đỉnh $1T_0$ luôn **thắng an toàn** khi hai đỉnh xấp xỉ nhau. Vì mức phạt chỉ $0{,}01$ trên thang $[0, 1]$, nó đủ để phá thế ngang bằng nhưng **không đủ để lật ngược** một đỉnh $1T_0$ đã thực sự yếu hơn nhiều — nhờ vậy giọng trầm (đỉnh $1T_0$ nằm ở lag lớn) vẫn sống sót sau khi đã được $C[\tau]$ bù.

**Ví dụ số, khung $F_0 = 200\text{ Hz}$ ($T_0 = 80$ mẫu).** Ở khung này cả $1T_0 = 80$ lẫn $2T_0 = 160$ đều nằm trong dải quét $[27, 213]$:
1. Chưa bù: đỉnh $1T_0$ đạt $0{,}42$, đỉnh $2T_0$ đạt $0{,}23$ — cả hai đều dưới ngưỡng $0{,}45$, khung bị gán vô thanh.
2. Nhân hệ số bù: $C[80] = 1{,}11$ và $C[160] = 1{,}52$. Đỉnh $1T_0$ lên $0{,}42 \times 1{,}11 \approx 0{,}47$; đỉnh $2T_0$ lên $0{,}23 \times 1{,}52 \approx 0{,}35$.
3. Thêm `octave_cost`: $0{,}47 \times 2^{-0{,}01} \approx 0{,}47$ và $0{,}35 \times 2^{-0{,}01} \approx 0{,}35$. Cả hai đều tụt một chút, nhưng **tỷ lệ giữa hai đỉnh** chính là thứ quyết định, và đỉnh $1T_0$ đang cao hơn hẳn — lỗi quãng tám bị chặn.
4. Trường hợp nguy hiểm là khi hai đỉnh gần ngang nhau: nếu sau bù $2T_0$ đạt $0{,}90$ và $1T_0$ đạt $0{,}62$, thì phạt $0{,}01$ **không đủ** để lật; vì vậy Praat còn thêm cơ chế Viterbi trên cả chuỗi khung để giữ quỹ đạo cao độ liên tục.

Hình 1.3.5b (Panel C) vẽ đúng ba đường của ví dụ trên: đường xám nét đứt (chưa bù) nằm dưới ngưỡng, đường xanh đậm (đã bù $C[\tau]$) vượt ngưỡng, và đường cam (thêm `octave_cost`) chỉ nhích nhẹ nhưng đủ để đỉnh $1T_0$ đứng trên đỉnh $2T_0$.

### C. Giải phẫu 10 tham số chuẩn của Praat dưới góc nhìn mã nguồn (Sound_to_Pitch.cpp)

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
8. **`octave_cost = 0,01` (trên mỗi quãng tám):** Hệ số thiên vị tần số cao nội khung (Local pitch-lag bias). Vì tín hiệu tuần hoàn ở $T_0$ cũng tuần hoàn ở $2T_0$ (tần số nửa $F_0/2$ — lỗi nhảy xuống quãng tám dưới), Praat trừ một khoản phạt tỉ lệ với logarit độ trễ (Công thức 24 Boersma):
   $$R_{\text{voiced}}[\tau] = r_x[\tau] - \text{octave\_cost} \times \log_2\left(\text{pitch\_floor} \cdot \frac{\tau}{f_s}\right)$$
   Ở lag càng lớn ($\tau$ lớn), điểm số bị trừ nhẹ (0,01 mỗi octave), giúp đỉnh cơ bản thật $\tau = T_0$ luôn thắng đỉnh bội số $\tau = 2T_0$. Trên FPGA, lượng phạt này được cộng trừ sẵn vào bảng tra ROM $C[\tau]$ mà không tốn mạch tính $\log_2$!
9. **`octave_jump_cost = 0,35`:** Trọng số phạt trong thuật toán Viterbi khi đường cao độ giữa hai khung liên tiếp bị nhảy vọt tần số:
   $$\text{Cost}_{\text{jump}}(F_{0, t-1} \to F_{0, t}) = \text{octave\_jump\_cost} \times \left|\log_2\left(\frac{F_{0, t}}{F_{0, t-1}}\right)\right| \times \left(\frac{0{,}01}{\Delta t_{\text{hop}}}\right)$$
   Nhờ mức phạt 0,35 cho mỗi quãng tám, Viterbi ưu tiên chọn chuỗi ứng viên tạo ra đường cong cao độ mượt mà.
10. **`voiced_unvoiced_cost = 0,14`:** Trọng số phạt trong Viterbi khi trạng thái chuyển từ Hữu thanh sang Vô thanh ($\text{Voiced} \leftrightarrow \text{Unvoiced}$), giúp ngăn hiện tượng đường Pitch bị đứt gãy chớp nháy ở ranh giới âm yếu.

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

Để chuyển đổi thuật toán Praat trên laptop sang phần cứng FPGA DE10-Standard, ta vứt bỏ các phép tính xa xỉ không thể tổng hợp:
1. *Bỏ nội suy Sinc vô hạn:* Praat dùng nội suy Sinc để bắt đỉnh dưới mẫu (sub-sample). Trên FPGA, ta giữ nguyên đỉnh số nguyên $\tau^* \in [27, 213]$ để tránh hàng chục nghìn phép tính dấu phẩy động.
2. *Bỏ quy hoạch động Viterbi toàn cục (Hình 1.3.5c):* Thay vì lưu trữ toàn bộ câu nói qua ma trận 15 ứng viên $\times N$ khung để tìm đường đi mượt mà, FPGA quyết định trực tiếp cục bộ trên từng khung 10 ms (streaming pipeline), giữ độ trễ lan truyền bằng 0.
3. *Bỏ bộ chia số học $16.000/\tau^*$:* Toàn bộ 187 giá trị cao độ tương ứng với 187 lag được nạp sẵn vào bảng tra ROM $F_0$. Khi bộ so sánh tìm được $\tau^*$, địa chỉ này kích hoạt ROM xuất thẳng giá trị $F_0$ ra bus đầu ra trong đúng 1 chu kỳ xung nhịp.

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

*Hình 1.3.5c: Đối chiếu cơ chế trích chọn cao độ: Lưới quy hoạch động Viterbi 15 ứng viên của Praat (phần mềm) vs. Trích chọn cực đại tức thời không trễ trên FPGA (phần cứng).*

**Đọc Hình 1.3.5c (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Các nút tròn màu trắng (1) đến (14) và (UV):** Thể hiện tập hợp 15 ứng viên cao độ mà Praat trích xuất tại mỗi khung phân tích thời gian $t$, gồm 14 đỉnh cực đại cục bộ có biên độ cao nhất và 1 ứng viên vô thanh (UV — Unvoiced).
2. **Đường nét đứt màu đỏ chạy ngang qua các nút (1):** Biểu diễn cơ chế của chế độ FPGA Streaming. Trên phần cứng, hệ thống không lưu vết toàn bộ câu mà chỉ giữ lại đúng 1 ứng viên có biên độ cực đại lớn nhất sau khi so sánh cục bộ tại khung hiện tại. Phép quyết định hoàn tất ngay lập tức, độ trễ bằng 0.
3. **Đường nét liền màu xanh lam đậm uốn lượn qua các khung:** Biểu diễn đường đi tối ưu toàn cục do giải thuật quy hoạch động Viterbi của Praat tìm ra sau khi duyệt qua toàn bộ ma trận ứng viên của cả câu nói.
4. **Các mũi tên màu tím hướng xiên giữa các nút ($Cost_{\text{jump}}$):** Đại diện cho hàm chi phí phạt bước nhảy tần số giữa hai khung liên tiếp khi đường cao độ bị thay đổi đột ngột qua các quãng tám.
5. **Các mũi tên màu cam hướng xuống nút (UV) (Phạt chuyển 0,14):** Đại diện cho chi phí phạt chuyển đổi trạng thái giữa có thanh và vô thanh nhằm ngăn chặn hiện tượng đường Pitch bị đứt gãy chớp nháy ở ranh giới các âm thanh yếu.

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
> 1. **Độ trễ ban đầu và tâm cửa sổ (Hình 1.3.5d):** Để bao trọn khung $40\text{ ms}$ thay vì $25\text{ ms}$, bộ đệm luồng Pitch cần thời gian nạp đầy ban đầu (initial buffering latency) lâu hơn $15\text{ ms}$, đồng thời tâm pha của cửa sổ phân tích (frame center) nằm lùi về quá khứ xa hơn $7{,}5\text{ ms}$ so với tâm cửa sổ STFT.
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

*Hình 1.3.5d: Đối sánh trục thời gian giữa Luồng Log-Mel STFT ($400\text{ mẫu} = 25\text{ ms}$) và Luồng Pitch $F_0$ ($640\text{ mẫu} = 40\text{ ms}$): Làm rõ độ lệch tâm pha $7{,}5\text{ ms}$ và độ trễ nạp đầy ban đầu $15\text{ ms}$.*

**Đọc Hình 1.3.5d (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Panel A — Các đường cong màu xanh lam (Luồng Log-Mel STFT):** Biểu diễn các cửa sổ phân tích STFT ngắn $L = 400\text{ mẫu}$ ($25\text{ ms}$). Bước nhảy giữa hai tâm cửa sổ liên tiếp là $H = 160\text{ mẫu}$ ($10\text{ ms}$).
2. **Panel A — Đường dóng nét đứt màu xanh lam (Tâm Khung 1):** Nằm tại thời điểm $t = 12{,}5\text{ ms}$ (mẫu thứ 200), là trọng tâm đối xứng của cửa sổ STFT đầu tiên.
3. **Panel B — Các đường cong màu cam (Luồng Cao Độ Pitch $F_0$):** Biểu diễn các cửa sổ phân tích cao độ dài $L = 640\text{ mẫu}$ ($40\text{ ms}$) theo tiêu chuẩn Praat để chứa trọn 3 chu kỳ âm trầm $75\text{ Hz}$. Bước nhảy giữa các khung vẫn giữ nguyên $H = 160\text{ mẫu}$ ($10\text{ ms}$).
4. **Mũi tên hai chiều màu đỏ ở giữa ($\Delta t_{\text{center}} = 7{,}5\text{ ms}$):** Đo độ lệch tâm pha giữa tâm cửa sổ Pitch ($20\text{ ms}$) và tâm cửa sổ STFT ($12{,}5\text{ ms}$). Mặc dù hai luồng cùng xuất ra kết quả với tốc độ 100 khung/s, luồng Pitch nhìn về quá khứ sâu hơn luồng STFT đúng 120 mẫu.
5. **Mũi tên hai chiều màu tím ở đáy ($\Delta t_{\text{init}} = 15\text{ ms}$):** Đo độ trễ chờ nạp đầy bộ đệm ban đầu. Khối Pitch cần nhận đủ 640 mẫu ($40\text{ ms}$) âm thanh mới bắt đầu tính toán được khung đầu tiên, trễ hơn 240 mẫu so với khối STFT (chỉ cần 400 mẫu = $25\text{ ms}$).

---

## 6. Sơ đồ Vi Kiến Trúc Pipeline Đề Xuất (Dataflow Architecture)

Sơ đồ khối vi kiến trúc tối ưu đưa khối nhân cửa sổ lên **trước** bộ đệm True Dual-Port RAM nhằm tối ưu hóa chu kỳ đọc:

```
+--------------------------+
|  Dòng mẫu I2S (16 kHz)   |
|         (16-bit)         |
+------------+-------------+
             |
             v
+------------+-------------+        +--------------------------+
|   Khối Nhân Cửa Sổ       |<-------| ROM Cửa Sổ Hanning       |
|    (Hanning Mult)        |        | (320 giá trị đối xứng)   |
+------------+-------------+        +--------------------------+
             | x_win[n]
             v
+------------+-------------+
|   True Dual-Port RAM     |
|   640 mẫu x_win[n]       |
|   (1 Khối M10K BRAM)     |
+------------+-------------+
             | Port A, B (n, n + tau)
             v
+------------+-------------+
|   Mảng Nhân - Tích Lũy   |
|   (MAC Engine, 1 DSP)    |
|   Tích lũy >= 42-bit     |
+------------+-------------+
             | R_x[tau]
             v
+------------+-------------+        +--------------------------+
|   Bù Suy Hao Cửa Sổ      |<-------| ROM Hệ Số C[tau]         |
| R_comp[tau] = R_x . C    |        | (187 mục 16-bit)         |
+------------+-------------+        +--------------------------+
             | R_comp[tau]
             v
+------------+-------------+
| Bộ Dò Đỉnh & Thanh Tính  |
| R_max = max(R_comp[tau]) |
| E_frame > E_silence      |
| và R_max >= 0.45 . R_x[0]|
+------+--------------+----+
       | CÓ (tau*)    | KHÔNG
       v              v
+------+------+  +----+--------+
| ROM Tra F0  |  | Cờ Unvoiced |
| 16000 / tau*|  | F0 = 0 Hz   |
|  (187 mục)  |  |             |
+------+------+  +----+--------+
       |              |
       +-------+------+
               |
               v
+--------------+---------------+
| Đầu ra Cao độ Pitch F0       |
| (100 Hz frame rate, 10 ms)   |
| Đồng bộ với luồng Log-Mel    |
+------------------------------+
```

*Hình 1.3.5e: Sơ đồ dòng dữ liệu (Dataflow) vi kiến trúc đo cao độ $F_0$ thời gian thực trên FPGA Intel Cyclone V.*

**Đọc Hình 1.3.5e (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Khối Đầu Vào Âm Thanh và Khối Nhân Cửa Sổ Hanning (Đỉnh sơ đồ):** Tín hiệu 16-bit từ giao tiếp I2S (16 kHz) được nhân trực tiếp với trọng số cửa sổ lấy từ ROM Hanning (chứa 320 giá trị đối xứng) ngay trên đường nạp vào, tạo ra mẫu $x_{\text{win}}[n]$ mà không tốn thêm chu kỳ đọc lại sau này.
2. **Khối True Dual-Port BRAM 640 Mẫu (Màu cam):** Lưu trữ trọn vẹn 640 mẫu $x_{\text{win}}[n]$ của khung phân tích trong đúng 1 khối M10K BRAM. Hai cổng Port A và Port B cho phép đọc đồng thời hai mẫu $x[n]$ và $x[n+\tau]$ trong cùng một chu kỳ xung nhịp.
3. **Khối Nhân - Tích Lũy MAC Engine (Màu xanh dương đậm):** Sử dụng 1 khối DSP Block phần cứng thực thi phép nhân 16-bit và tích lũy vào thanh ghi 42-bit để tính tổng tự tương quan thô $\mathcal{R}_x[\tau]$ cho từng độ trễ $\tau$.
4. **Khối Bù Suy Hao Cửa Sổ và ROM Hệ Số $C[\tau]$ (Màu xanh lá):** Sau khi tính xong tổng $\mathcal{R}_x[\tau]$, giá trị này được nhân với hệ số bù $C[\tau] = \mathcal{R}_w[0]/\mathcal{R}_w[\tau]$ lưu trong ROM 187 mục 16-bit để sinh ra tổng đã bù suy hao $\mathcal{R}_{\text{comp}}[\tau]$ mà không cần bộ chia số học.
5. **Khối Bộ Dò Đỉnh & Thanh Tính (Màu tím):** Tìm giá trị cực đại $\mathcal{R}_{\text{comp}}[\tau^*]$ trong dải $\tau \in [27, 213]$, đồng thời kiểm tra đồng thời hai điều kiện: năng lượng khung vượt ngưỡng khoảng lặng ($E_{\text{frame}} > E_{\text{silence}}$) và tương quan chuẩn hóa đạt ngưỡng thanh tính ($\mathcal{R}_{\text{comp}}[\tau^*] \ge 0{,}45 \cdot \mathcal{R}_x[0]$).
6. **Nhánh Rẽ Quyết Định (Có thanh vs. Vô thanh):** Nếu thỏa mãn cả hai điều kiện, giá trị độ trễ tối ưu $\tau^*$ được dùng làm địa chỉ tra cứu ROM $F_0$ (chứa sẵn 187 giá trị $16.000/\tau^*$) để xuất ra tần số cơ bản chính xác; nếu không thỏa mãn, hệ thống bật cờ vô thanh và gán $F_0 = 0\text{ Hz}$.
7. **Khối Đầu Ra Cao Độ Pitch $F_0$ (Đáy sơ đồ):** Cung cấp dòng dữ liệu cao độ với tốc độ 100 khung/s (mỗi 10 ms một giá trị), hoàn toàn đồng bộ với nhịp khung của luồng đặc trưng Log-Mel Spectrogram.

---

## 7. Tổng Kết và Cầu Nối Chuyển Tiếp

- **Mục 1.2 & 1.3** cung cấp vector đặc trưng phổ 80 chiều (Log-Mel) đại diện cho *khẩu hình miệng*.
- **Mục 1.3.5** bổ sung dòng dữ liệu vô hướng 1 chiều ($F_0$) đại diện cho *nhịp đập dây thanh quản*.
- **Sự kết hợp hai luồng đặc trưng:** Bằng cách ghép luồng Log-Mel và luồng Pitch $F_0$, hệ thống Edge AI trên FPGA thu nhận được đầy đủ cả **ngữ âm** lẫn **ngữ điệu**, mở đường cho các mô hình phân loại thanh điệu tiếng Việt và nhận dạng cảm xúc đạt độ chính xác tương đương các siêu máy tính máy trạm mà chỉ tiêu tốn chưa đầy $2\%$ tài nguyên silicon của kit DE10-Standard.

---

# Phụ lục 1.3.5-A. Áp dụng lý thuyết 1.3.5 vào mã nguồn Python (`audio_processing.py` và `evaluator.py`)

> **Phạm vi và Mục tiêu:** Phụ lục này đối chiếu hai tệp mã nguồn xử lý âm thanh trong thư mục `Pronunciation_Final_Master` của kho lưu trữ `DucDocDao/Pitch-Project` (nhánh `main`) với lý thuyết đo cao độ $F_0$ bằng tự tương quan ở Mục 1.3.5 (Praat, Boersma 1993). Để hiểu trọn vẹn luồng gọi hàm, phụ lục tham chiếu thêm `main.py`, `visualizer.py`, `generate_audio.py` và `sentence_data.py`. Mọi phân tích dưới đây đều dựa trên mã nguồn thực tế; các vị trí mã nguồn không hiển thị rõ hành vi nội tại đều được ghi chú là *chưa kiểm chứng*.

---

## 1. Bức Tranh Tổng Thể: Hai Tệp Làm Gì Trong Hệ Thống?

### 1.1. Bài toán của dự án
Dự án giải quyết bài toán so sánh **đường bao cao độ** (pitch contour — chuỗi tần số cơ bản $F_0$ theo thời gian) của một câu tiếng Anh do giọng chuẩn tham chiếu đọc (giọng tổng hợp nữ `sarah`) với câu do người học hoặc giọng khác đọc (các giọng nam Mỹ, ví dụ `michael`). Âm thanh chuẩn được sinh bằng mô hình tổng hợp tiếng nói Kokoro (`generate_audio.py`). Kết quả cuối cùng là hệ số tương quan Pearson $r$ giữa hai đường cao độ, hiện thực hóa mục tiêu đã nêu tại phần 0 của Mục 1.3.5: *"đối sánh tương quan Pearson ($r$) với các công cụ âm học chuẩn mực phòng thí nghiệm như Praat"*.

### 1.2. Luồng xử lý một câu (theo `main.py`)
1. `trim_silence_and_save` (`audio_processing.py`): Cắt bỏ khoảng lặng ở hai đầu tệp âm thanh và ghi ra tệp WAV đã cắt.
2. `extract_features_praat` (`audio_processing.py`): Đo đường cao độ $F_0$ trên **chính tệp WAV đã cắt** bằng công cụ Praat (thông qua thư viện liên kết `parselmouth`).
3. `get_user_timestamps` (`evaluator.py`): Nạp mô hình nhận dạng tiếng nói tự động Whisper (`openai/whisper`) bóc tách mốc thời gian từ ($w_{\text{start}}, w_{\text{end}}$) trên **chính tệp WAV đã cắt**.
4. `plot_analysis` (`visualizer.py`): Gọi chuỗi 4 hàm trong `audio_processing.py` (`get_local_chunk`, `equalize_local_chunk`, `dynamic_sliding_window_pearson`, `summarize_pearson`) để căn chỉnh hai đường cao độ và tính Pearson $r$.
5. `summarize_sentence_reports` (`audio_processing.py`): Gom toàn bộ kết quả của nhiều câu thành bảng thống kê phân phối độ chính xác theo các ngưỡng tích lũy.

Ghi chú quan trọng trong `main.py` (dòng 72): *"Both pitch and timestamps must refer to exactly this trimmed WAV"*. Điều này bảo đảm cả đường $F_0$ lẫn mốc thời gian từ đều dùng chung một gốc thời gian $t = 0$; nếu đo trên hai tệp khác nhau (trước và sau khi cắt), trục thời gian sẽ bị lệch nhau đúng bằng thời lượng đoạn lặng ban đầu bị cắt bỏ.

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
                                         v                                             v
                       +----------------------------------------------------------------------------------+
                       |           Căn chỉnh theo từ (visualizer.py & audio_processing.py)                |
                       | 1. get_local_chunk: Cắt đoạn theo tỉ lệ i = |_ (t/D) . N _|                      |
                       | 2. equalize_local_chunk: Nội suy np.interp về cùng độ dài từ chuẩn               |
                       | 3. Ghép vào mảng cao độ chung stitched_user_pitch                                |
                       +-----------------------------------------+----------------------------------------+
                                                                 |
                                                                 v
                       +----------------------------------------------------------------------------------+
                       |           Cửa sổ trượt Pearson (dynamic_sliding_window_pearson)                  |
                       | Kích thước W = 2N/(K+2) (chứa ~ 2 từ), bước trượt S = W/2                        |
                       | Lọc điểm hữu thanh: (u_i > 0) & (v_i > 0) ==> Tính hệ số Pearson r               |
                       +-----------------------------------------+----------------------------------------+
                                                                 | Chuỗi Pearson r
                                                                 v
                       +----------------------------------------------------------------------------------+
                       |         Tổng hợp điểm số (summarize_pearson & summarize_sentence_reports)        |
                       | Bỏ NaN, kẹp r <= 0 về 0 ==> mean_r in [0, 1]                                     |
                       | Thống kê tích lũy câu theo các ngưỡng >= 0.9; >= 0.8; ...; >= 0.3                |
                       +----------------------------------------------------------------------------------+
```

*Hình 1.3.5f: Sơ đồ luồng xử lý âm thanh, trích xuất hai luồng song song (Praat $F_0$ và Whisper Timestamps) và thuật toán đối sánh ngữ điệu trong mã nguồn Python (`audio_processing.py` và `evaluator.py`).*

**Đọc Hình 1.3.5f (Hướng dẫn chi tiết từng thành phần trực quan):**
1. **Khối Tệp Âm Thanh Thô và Khối Tiền xử lý cắt lặng (Hàng 1):** Tệp âm thanh do Kokoro TTS sinh ra ở tần số 24 kHz được đưa qua hàm `trim_silence_and_save`. Hàm này dùng `librosa.effects.trim` với ngưỡng `top_db = 30 dB` (tương ứng biên độ giảm còn 3,2%) để cắt bỏ các khoảng lặng ở hai đầu tệp, sinh ra tệp WAV đã cắt làm gốc thời gian chuẩn $t = 0$ cho cả hai nhánh phía sau.
2. **Nhánh Luồng 1 — Đo Cao Độ Praat (Hàng 2, Bên trái):** Gọi hàm `extract_features_praat`. Lệnh `snd.to_pitch()` chạy mã C++ nguyên bản của Praat trên tín hiệu 24 kHz, dùng cửa sổ Hanning 40 ms (960 mẫu), bước nhảy 10 ms (240 mẫu), tính tự tương quan bù suy hao và giải thuật Viterbi 15 ứng viên. Kết quả trả về mảng `pitch` chứa tần số $F_0$ (quy ước 0 Hz là khung vô thanh), trong khi mảng mốc thời gian thực `xs()` bị bỏ qua.
3. **Nhánh Luồng 2 — Nhận Diện Mốc Thời Gian Từ (Hàng 2, Bên phải):** Gọi `get_user_timestamps` trong `evaluator.py`. Tín hiệu được lấy mẫu lại từ 24 kHz về 16 kHz để đưa vào mô hình Whisper `base` (chạy đặc trưng Log-Mel STFT). Whisper nhận dạng văn bản và xuất mốc thời gian bắt đầu và kết thúc của từng từ ($w_{\text{start}}, w_{\text{end}}$).
4. **Khối Căn Chỉnh Theo Từ (Hàng 3):** Kết hợp kết quả từ hai nhánh: `get_local_chunk` cắt đoạn cao độ theo tỉ lệ thời gian $i = \lfloor (t/D) \cdot N \rfloor$, `equalize_local_chunk` dùng `np.interp` để co giãn đoạn cao độ của người đọc về đúng số điểm của giọng tham chiếu, rồi dán vào mảng cao độ đã căn chỉnh `stitched_user_pitch`.
5. **Khối Cửa Sổ Trượt Pearson (Hàng 4):** Hàm `dynamic_sliding_window_pearson` tạo $K+1$ cửa sổ trượt có kích thước $W = 2N/(K+2)$ (chứa trọn khoảng 2 từ) và bước trượt $S = W/2$. Trong mỗi cửa sổ, chỉ giữ lại các điểm mà cả hai đường đều hữu thanh ($u_i > 0$ và $v_i > 0$) để tính hệ số tương quan Pearson $r$.
6. **Khối Tổng Hợp Điểm Số (Hàng 5):** Hàm `summarize_pearson` loại bỏ các cửa sổ NaN, kẹp các giá trị tương quan không dương ($r \le 0$) về $0$, rồi tính trung bình để sinh ra điểm số `mean_r` của câu. Hàm `summarize_sentence_reports` thống kê số lượng câu đạt các ngưỡng tích lũy từ $\ge 0{,}9$ đến $\ge 0{,}3$.

### 1.3. Hiểu lầm cần tránh ngay từ đầu
- **`evaluator.py` không thực hiện việc chấm điểm:** Mặc dù mang tên "evaluator", tệp này chỉ đảm nhận việc nạp mô hình Whisper và trả về danh sách mốc thời gian từng từ. Toàn bộ logic so khớp, căn chỉnh và tính điểm tương quan ($r$) đều nằm trọn bên trong `audio_processing.py` và được điều phối bởi `visualizer.py`.
- **Không có dòng mã Python nào tự tính tổng tự tương quan:** Công thức tính tự tương quan $\mathcal{R}_x[\tau]$ (Công thức 1), cửa sổ Hanning, phép chia bù suy hao (Công thức 6) và bảng tra đều không được cài đặt bằng mã Python tường minh. Toàn bộ các bước này được đóng gói bên trong lệnh gọi thư viện `snd.to_pitch()`.

---

## 2. Bảng Thuật Ngữ Dùng Trong Phụ Lục

| Thuật ngữ tiếng Việt | Thuật ngữ tiếng Anh | Định nghĩa chuẩn mực trong ngữ cảnh mã nguồn |
| :--- | :--- | :--- |
| Khung phân tích | Frame | Đoạn gồm $L$ mẫu tín hiệu liên tiếp dùng để tính một giá trị $F_0$ (Mục 1.3.5, phần 2). |
| Bước nhảy trượt khung | Time step / Hop size ($\Delta t_{\text{hop}}$) | Khoảng thời gian giữa tâm đối xứng của hai khung phân tích liên tiếp (10 ms). |
| Điểm cao độ | Pitch point | Một phần tử trong mảng `pitch`: giá trị $F_0$ (đơn vị Hz) của khung; bằng 0 nếu là vô thanh. |
| Hữu thanh / Vô thanh | Voiced / Unvoiced | Trạng thái khung tín hiệu có / không có dao động tuần hoàn của dây thanh quản. |
| Tổng tự tương quan $\mathcal{R}_x[\tau]$ | Autocorrelation sum | Công thức (1) của Mục 1.3.5: tổng tích các cặp mẫu trễ $\tau$, **không phải là tích chập**. |
| Hệ số tương quan Pearson $r$ | Pearson correlation coefficient | Thước đo mức độ hai chuỗi số đồng biến/nghịch biến tuyến tính, nằm trong $[-1, 1]$. |
| Căn chỉnh thời gian | Time alignment | Đưa hai đường cao độ có độ dài khác nhau về cùng trục chỉ số để so sánh từng điểm. |

> **Cảnh báo nghiêm ngặt về hiện tượng trùng ký hiệu:**
> Tài liệu Mục 1.3.5 dùng ký hiệu $r_x[\tau]$ cho **hàm tự tương quan chuẩn hóa theo độ trễ $\tau$** (Công thức 6), trong khi mã nguồn Python dùng biến `r`, `mean_r` để chỉ **hệ số tương quan tuyến tính Pearson** giữa hai đường cao độ. Hai đại lượng này hoàn toàn khác nhau về bản chất toán học:
> - $r_x[\tau]$ đo mức độ một khung tín hiệu tương đồng với **chính nó** khi dịch trượt đi $\tau$ mẫu trong miền thời gian.
> - Hệ số Pearson $r$ đo mức độ hai **đường cong cao độ $F_0$ của hai người nói khác nhau** có hình thái ngữ điệu lên bổng xuống trầm giống nhau hay không.
> Phụ lục này luôn viết tường minh cụm từ "Pearson $r$" để loại trừ mọi sự nhầm lẫn.

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

### 3.2. Bảng ánh xạ tham số chuẩn Praat
Lệnh `snd.to_pitch()` gọi hàm C++ `Sound_to_Pitch_ac` trong mã nguồn Praat với đầy đủ 10 tham số mặc định:

| Bước giải thuật bên trong `snd.to_pitch()` (Praat C++) | Tham số tương ứng | Vị trí trong lý thuyết Mục 1.3.5 |
| :--- | :--- | :--- |
| Cắt khung phân tích độ dài 3 chu kỳ của $75\text{ Hz}$ ($40\text{ ms}$) | `pitch_floor = 75.0` | Mục 3.A (Quy tắc 3 chu kỳ) |
| Bước nhảy trượt khung $\Delta t_{\text{hop}} = 0{,}75 / 75 = 0{,}01\text{ s}$ ($10\text{ ms}$) | `time_step = 0.0` (Auto) | Mục 3.C (Tham số 1) |
| Áp cửa sổ Hanning (vuốt êm hai đầu mút về 0) | `very_accurate = False` | Mục 3.B và Mục 3.C (Tham số 4) |
| Tính tổng tự tương quan rời rạc $\mathcal{R}_x[\tau]$ | — | Công thức (1) |
| Bù suy hao cửa sổ bằng phép chia $r_x[\tau] = \mathcal{R}_x[\tau] / \mathcal{R}_w[\tau]$ | — | Công thức (6) và (7) |
| Giới hạn không gian tìm kiếm cực đại trong $[\tau_{\text{min}}, \tau_{\text{max}}]$ | `pitch_ceiling = 600.0` | Công thức (3) và (4) |
| Trích xuất 14 đỉnh cực đại cục bộ + 1 ứng viên Vô thanh | `max_number_of_candidates = 15` | Mục 3.C (Tham số 5) |
| Phạt khoảng lặng $\theta_{\text{silence}} = 0{,}03$ và ngưỡng thanh tính $\theta_{\text{voice}} = 0{,}45$ | `silence_threshold`, `voicing_threshold` | Mục 3.C (Tham số 6, 7) |
| Áp mức phạt thiên vị log-lag nội khung để chống nhảy xuống $F_0/2$ | `octave_cost = 0.01` | Mục 3.C (Tham số 8) |
| Giải thuật quy hoạch động Viterbi tìm đường đi mượt mà toàn câu | `octave_jump_cost = 0.35`, `voiced_unvoiced_cost = 0.14` | Mục 3.C (Tham số 9, 10), Hình 1.3.5c |
| Xuất tần số cơ bản của khung: $F_0 = f_s / \tau^*$ | — | Mục 2 |

### 3.3. Đi sâu vào các hệ quả toán học

**(a) Tần số lấy mẫu thực tế là $24\text{ kHz}$ thay vì $16\text{ kHz}$:**
Mô hình tổng hợp giọng nói Kokoro trong `generate_audio.py` ghi tệp âm thanh ở tần số lấy mẫu $f_s = 24.000\text{ Hz}$ (`sf.write(..., 24000)`). Hàm `trim_silence_and_save` nạp tệp với `sr=None` (giữ nguyên tần số lấy mẫu gốc) rồi ghi đè lại cùng tần số. Vì vậy, Praat thực hiện đo đạc $F_0$ trên tín hiệu $f_s = 24.000\text{ Hz}$. Các con số tính toán chuyển đổi:

$$\tau_{\text{min}} = \left\lceil \frac{24.000}{600} \right\rceil = \mathbf{40\text{ mẫu}}, \qquad \tau_{\text{max}} = \left\lfloor \frac{24.000}{75} \right\rfloor = \mathbf{320\text{ mẫu}}$$

$$L = 0{,}040 \times 24.000 = \mathbf{960\text{ mẫu}}, \qquad \Delta t_{\text{hop}} = 0{,}01 \times 24.000 = \mathbf{240\text{ mẫu}}$$

- Dải quét độ trễ mở rộng từ $[27, 213]$ ($187\text{ lag}$ ở $16\text{ kHz}$) lên $[40, 320]$ ($281\text{ lag}$ ở $24\text{ kHz}$).
- Độ dài khung phân tích tăng từ $640\text{ mẫu}$ lên $960\text{ mẫu}$.
- **Thời lượng vật lý** của khung ($40\text{ ms}$) và dải **tần số vật lý** ($75\text{--}600\text{ Hz}$) hoàn toàn không đổi.

*Cảnh báo ứng dụng số học:* Một đỉnh tương quan tại $\tau^* = 200\text{ mẫu}$ trong mã nguồn này tương ứng với $F_0 = 24.000 / 200 = 120\text{ Hz}$. Nếu áp nhầm công thức $16\text{ kHz}$ của Mục 1.3.5 vào dữ liệu này, kết quả sẽ bị sai lệch nghiêm trọng: $16.000 / 200 = 80\text{ Hz}$!

**(b) Về độ phân giải và bậc thang hóa:**
Ở $f_s = 24\text{ kHz}$, bước nhảy 1 mẫu trễ ở cận trần cao độ tạo sai số $\Delta F_0 = \frac{24.000}{40} - \frac{24.000}{41} \approx 14{,}6\text{ Hz}$, mịn hơn đáng kể so với mức $22\text{ Hz}$ ở $16\text{ kHz}$. Đặc biệt, Praat sử dụng phép nội suy parabol/sinc bậc cao quanh đỉnh để tìm cực trị dưới mức mẫu rời rạc (sub-sample interpolation), nên đường cao độ thu được trong Python không bị lỗi bậc thang hóa như thiết kế phần cứng FPGA số nguyên.

**(c) Thuật toán Viterbi và 15 ứng viên:**
Mã Python sử dụng toàn bộ sức mạnh quy hoạch động Viterbi toàn cục (nhánh Praat trong Hình 1.3.5c). Nhờ có toàn bộ câu thoại trong bộ nhớ, đường $F_0$ của Praat loại bỏ triệt để các bước nhảy octave giả tạo.

**(d) Không có bộ lọc High-Pass (HPF) 60 Hz:**
Trong mã nguồn Python, tín hiệu không được đưa qua bộ lọc thông cao HPF 60 Hz như yêu cầu nghiêm ngặt tại Mục 1.1.5 và Mục 4. Tuy nhiên, vì âm thanh đầu vào là âm thanh tổng hợp nhân tạo (Kokoro TTS), tín hiệu hoàn toàn sạch nhiễu cơ học tần số cực thấp (tiếng rung mặt bàn, tiếng gió micrô), nên sự thiếu vắng HPF không gây tác hại nghiêm trọng trong môi trường thử nghiệm này.

**(e) Bỏ rơi mảng mốc thời gian thực `xs()`:**
Praat trả về mảng thời điểm tâm khung `pitch_object.xs()`. Tuy nhiên, trong `main.py` dòng 77:
```python
user_pitch, _ = extract_features_praat(user_wav_path)
```
Mảng thời gian thực này bị bỏ qua bằng biến `_`, dẫn đến việc các hàm phía sau phải dùng phép suy diễn thời gian xấp xỉ tuyến tính (xem Mục 5.1).

---

## 4. `trim_silence_and_save`: Điểm Xuất Phát Của Dòng Thời Gian

### 4.1. Mã nguồn
```python
def trim_silence_and_save(audio_path, trimmed_path, top_db=30):
    y, sr = librosa.load(audio_path, sr=None)
    y_trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    if not len(y_trimmed) or not np.any(y_trimmed):
        raise ValueError(f"File {audio_path} is completely silent.")
    sf.write(trimmed_path, y_trimmed, sr)
```

### 4.2. Cơ chế và ý nghĩa của ngưỡng 30 dB
Hàm `librosa.effects.trim` chia tín hiệu thành các khung ngắn (mặc định $2.048\text{ mẫu}$, bước nhảy $512\text{ mẫu}$), tính năng lượng hiệu dụng RMS của từng khung và đổi sang đơn vị Decibel tương đối so với khung có năng lượng lớn nhất câu ($0\text{ dBFS}$). Mọi khung ở hai đầu tệp có mức năng lượng thấp hơn đỉnh quá $\text{top\_db} = 30\text{ dB}$ đều bị loại bỏ:

$$\text{Tỉ số biên độ} = 10^{-\frac{30}{20}} \approx \mathbf{0{,}0316} \implies \mathbf{3{,}2\%}$$

Hàm chỉ cắt bỏ các đoạn lặng ở phần đầu (lead-in) và phần đuôi (lead-out), **tuyệt đối không cắt khoảng lặng giữa câu**. Mục đích cốt lõi là thiết lập gốc thời gian $t = 0$ đồng bộ giữa hai giọng đọc có thói quen dừng nghỉ ban đầu khác nhau.

### 4.3. Phân biệt `top_db = 30` (librosa) và `silence_threshold = 0,03` (Praat)

| Tiêu chí so sánh | `top_db = 30` (`librosa.effects.trim`) | `silence_threshold = 0,03` (Praat, Tham số 6) |
| :--- | :--- | :--- |
| **Bản chất tác động** | Cắt bỏ hoàn toàn các mẫu dữ liệu khỏi tệp WAV | Giữ nguyên tệp; chỉ gán nhãn $F_0 = 0$ cho khung yếu |
| **Phạm vi xử lý** | Duy nhất hai đầu mút của tệp âm thanh | Toàn bộ mọi khung trên khắp chiều dài câu nói |
| **Thước đo toán học** | Năng lượng RMS khung so với RMS cực đại (dB) | Biên độ đỉnh tức thời khung so với đỉnh toàn tệp |
| **Mục đích thiết kế** | Đồng bộ hóa gốc thời gian chuẩn $t = 0$ cho hai người | Chống bắt nhầm nhiễu nền tuần hoàn thành âm hữu thanh |

---

## 5. Căn Chỉnh Hai Đường Cao Độ Theo Từng Từ

### 5.1. `get_local_chunk`: Cắt đoạn cao độ của một từ
```python
def get_local_chunk(raw_array, w_start, w_end, total_dur):
    N = len(raw_array)
    i1 = int((w_start / total_dur) * N)
    i2 = int((w_end / total_dur) * N)
    return raw_array[i1:i2]
```
Chuyển đổi mốc thời gian giây ($w_{\text{start}}, w_{\text{end}}$) nhận từ Whisper thành chỉ số khung mảng theo quy tắc tỉ lệ:

$$i = \left\lfloor \frac{t}{D} \cdot N \right\rfloor$$

*Đánh giá sai số:* Phép tính tỉ lệ giả định các khung phân bố đều từ $t = 0$ đến $t = D$. Trong thực tế của Praat, tâm khung đầu tiên nằm lùi vào khoảng nửa khung ($t_1 \approx 20\text{ ms}$ — hiện tượng lệch tâm pha ở Hình 1.3.5d). Sai số tối đa do bỏ rơi mảng `xs()` là khoảng nửa khung ($\le 20\text{ ms}$, tương đương $\le 2$ điểm cao độ). Vì cả giọng mẫu lẫn giọng người đọc đều chịu chung sai số này, chúng phần lớn triệt tiêu lẫn nhau khi so sánh.

### 5.2. `equalize_local_chunk`: Co giãn thời gian tuyến tính
```python
def equalize_local_chunk(user_chunk, ref_chunk):
    if len(user_chunk) == 0 or len(ref_chunk) == 0:
        return np.zeros(len(ref_chunk))
    x_ref = np.linspace(0, 1, len(ref_chunk))
    x_user = np.linspace(0, 1, len(user_chunk))
    return np.interp(x_ref, x_user, user_chunk)
```
Hàm chuẩn hóa trục thời gian của từ về đoạn $[0, 1]$, sau đó dùng hàm nội suy 1D `np.interp` để co giãn đoạn cao độ của người đọc về đúng số điểm của giọng tham chiếu. Đây là phép co giãn thời gian tuyến tính (Linear Time Warping) cục bộ theo từng từ.

### 5.3. Nguy cơ tiềm ẩn: Sinh tần số $F_0$ giả mạo khi nội suy qua điểm vô thanh
Hàm `np.interp` coi mảng đầu vào là các con số liên tục, không nhận biết quy ước $0\text{ Hz} = \text{Vô thanh}$. Nếu một từ chuyển trạng thái từ vô thanh sang hữu thanh qua hai điểm kế tiếp $[0\text{ Hz}, 200\text{ Hz}]$, phép nội suy tại điểm giữa sẽ tạo ra giá trị $100\text{ Hz}$. Đây là một **giá trị $F_0$ giả tạo** (dây thanh quản không bao giờ rung ở tần số 100 Hz tại thời điểm đó). Vì $100 > 0$, điểm giả này lọt qua bộ lọc hữu thanh ở khâu sau và có thể làm suy giảm hệ số tương quan Pearson $r$.

### 5.4. Ghép nối mảng cao độ chung (`stitched_user_pitch`)
Hàm `plot_analysis` khởi tạo mảng `stitched_user_pitch` toàn số 0 có độ dài đúng bằng đường tham chiếu ($N_{\text{ref}}$). Các từ nhận diện đúng được dán vào đúng các vị trí chỉ số tương ứng. Các từ bị đọc sai hoặc khoảng lặng giữa các từ vẫn giữ giá trị 0 và sẽ bị bộ lọc hữu thanh loại bỏ.

---

## 6. `dynamic_sliding_window_pearson`: Đo Hình Thái Ngữ Điệu Thay Vì Giá Trị Tuyệt Đối

### 6.1. Mã nguồn
```python
def dynamic_sliding_window_pearson(u_curve, r_curve, num_words):
    N = len(r_curve)
    W = max(6, int((2 * N) / (num_words + 2)))
    if W % 2 != 0:
        W -= 1
    S = max(1, W // 2)
    num_slides = num_words + 1

    r_list = []
    for i in range(num_slides):
        start = i * S
        end = min(start + W, N)
        if i == num_slides - 1:
            end = N
        u_win = u_curve[start:end]
        r_win = r_curve[start:end]
        valid = (u_win > 0) & (r_win > 0)
        if np.sum(valid) >= 3 and np.std(u_win[valid]) > 0 and np.std(r_win[valid]) > 0:
            r = np.corrcoef(u_win[valid], r_win[valid])[0, 1]
        else:
            r = np.nan
        r_list.append(r)
    return r_list
```

### 6.2. Nguồn gốc công thức kích thước cửa sổ động
Gọi $K = \text{num\_words}$ (số từ của câu chuẩn), $N$ là tổng số điểm cao độ. Thuật toán tạo ra $K+1$ cửa sổ trượt có kích thước $W$, bước trượt $S = W/2$. Tổng chiều dài bao phủ:

$$\text{Tổng phủ} = K \cdot S + W = K \frac{W}{2} + W = \frac{(K + 2)W}{2}$$

Đặt tổng chiều dài bằng đúng độ dài câu $N$:

$$\frac{(K + 2)W}{2} = N \implies W = \frac{2N}{K + 2}$$

Công thức này bảo đảm:
- Kích thước mỗi cửa sổ luôn tương đương với **thời lượng trung bình của khoảng 2 từ**.
- Mỗi cửa sổ chứa đủ thông tin ngữ điệu của một cụm từ ngắn.
- Các cửa sổ gối nhau $50\%$ giúp quét mượt mà khắp câu mà không bỏ sót các điểm chuyển tiếp.

### 6.3. Bản chất toán học của hệ số tương quan Pearson
Trong mỗi cửa sổ, chỉ xét tập hợp $M$ điểm mà cả hai đường đều hữu thanh ($u_i > 0$ và $v_i > 0$). Công thức Pearson:

$$r = \frac{\sum_{i=1}^M (u_i - \bar{u})(v_i - \bar{v})}{\sqrt{\sum_{i=1}^M (u_i - \bar{u})^2} \sqrt{\sum_{i=1}^M (v_i - \bar{v})^2}}$$

### 6.4. Tính bất biến Affine và ý nghĩa âm học
Hệ số Pearson $r$ có tính chất bất biến trước các phép biến đổi affine đồng dạng ($u_i = a \cdot v_i + b$ với $a > 0$). Nếu giọng nam `michael` nói trầm hơn giọng nữ `sarah` đúng một quãng tám ($u_i = 0{,}5 \cdot v_i$) nhưng có đường nét luyến láy lên bổng xuống trầm giống hệt nhau, hệ số tương quan vẫn đạt mức tối đa:

$$r = \mathbf{1{,}0}$$

Điều này chứng minh hệ số Pearson $r$ **chỉ đo hình thái đường cong ngữ điệu**, hoàn toàn không bị ảnh hưởng bởi sự chênh lệch cao độ bẩm sinh giữa nam và nữ.

---

## 7. `summarize_pearson` và `summarize_sentence_reports`: Từ Cửa Sổ Đến Điểm Số

### 7.1. Điểm số của một câu (`mean_r`)
```python
def summarize_pearson(r_list):
    arr = np.array(r_list, dtype=float)
    valid = arr[np.isfinite(arr)]
    if len(valid) == 0:
        return {"mean_r": 0.0, "valid_r_count": 0, "missing_r_count": len(arr)}
    mean_r = float(np.maximum(valid, 0).mean())
    return {"mean_r": mean_r, "valid_r_count": len(valid), "missing_r_count": len(arr) - len(valid)}
```
1. Loại bỏ các cửa sổ NaN (không đủ 3 điểm hữu thanh hoặc phương sai bằng 0).
2. Kẹp toàn bộ các giá trị tương quan âm hoặc bằng 0 về mức 0 (`np.maximum(valid, 0)`): coi tương quan âm là không đạt chuẩn ngữ điệu, không phạt thêm điểm âm.
3. Tính trung bình số học sinh ra điểm số `mean_r` nằm trong đoạn $[0, 1]$.

### 7.2. Thống kê tích lũy nhiều câu (`summarize_sentence_reports`)
Hàm quét qua các câu đã xử lý thành công và đếm số lượng câu đạt điểm vượt qua các ngưỡng tích lũy từ $\ge 0{,}9$ đến $\ge 0{,}3$.

---

## 8. `evaluator.py`: Vai Trò Thực Sự và Kiến Trúc Song Song Hai Luồng

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
- `evaluator.py` nạp tệp âm thanh $24\text{ kHz}$, lấy mẫu lại về **$16\text{ kHz}$** để cấp cho mô hình Whisper.
- Whisper sử dụng đặc trưng **Log-Mel Spectrogram** (Mục 1.3) để nhận dạng văn bản và trích xuất mốc thời gian từ ($w_{\text{start}}, w_{\text{end}}$). Whisper hoàn toàn không quan tâm đến tần số cơ bản $F_0$.
- Đồng thời, `extract_features_praat` chạy độc lập trên tín hiệu $24\text{ kHz}$ để trích xuất đường cao độ $F_0$.
- Đây chính là sự hiện thực hóa hoàn hảo của **kiến trúc song song hai luồng** được đề xuất tại phần 0 của Mục 1.3.5: Luồng Mel nhận diện từ, Luồng Pitch đo thanh tính và ngữ điệu!

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
| **Cơ chế chọn đỉnh** | Chọn cực đại tức thời cục bộ (1 ứng viên) | 15 ứng viên + Viterbi + Nội suy cực trị | Bản Python mượt hơn, bản FPGA tối ưu độ trễ bằng 0 |
| **Lọc thông cao HPF 60 Hz**| Bắt buộc có ở tầng tiền xử lý | Không xuất hiện trong mã nguồn | Chấp nhận được vì âm thanh Kokoro tổng hợp rất sạch |
| **Khử khoảng lặng** | Ngưỡng năng lượng khung tức thời tĩnh | Thêm `librosa.trim` $30\text{ dB}$ ở hai đầu | Bước cắt của Python nhằm mục đích đồng bộ trục thời gian |
| **Phương pháp đối sánh** | Phân loại thanh điệu hoặc Pearson $r$ | Cửa sổ trượt Pearson $r$ theo kích thước động | Khẳng định Pearson đo hình thái, không đo tần số tuyệt đối |
| **Tần số lấy mẫu STT** | $16\text{ kHz}$ (chuẩn Log-Mel STFT) | $16\text{ kHz}$ (Whisper resample) | Tách bạch hoàn hảo hai luồng Mel và Pitch |

---

## 10. Danh Sách 8 Điểm Vênh Kỹ Thuật và Bài Học Thiết Kế Hệ Thống

1. **Bỏ rơi mảng mốc thời gian thực `xs()`:** Việc quy đổi mốc từ sang chỉ số khung qua tỉ lệ $i = \lfloor (t/D) \cdot N \rfloor$ tạo ra sai lệch tối đa khoảng nửa khung ($\approx 20\text{ ms}$) do bỏ qua độ lệch tâm pha ban đầu.
2. **Nguy cơ sinh tần số $F_0$ giả mạo khi nội suy:** Phép gọi `np.interp` qua các ranh giới vô thanh ($0\text{ Hz}$) sinh ra các giá trị tần số nhân tạo nằm giữa 0 và tần số thật, làm méo mó hệ số Pearson $r$.
3. **Độ lệch tần số lấy mẫu ($24\text{ kHz}$ vs. $16\text{ kHz}$):** Không được áp dụng trực tiếp bảng tra ROM hoặc dải lag $[27, 213]$ của tài liệu vào dữ liệu âm thanh $24\text{ kHz}$ của dự án mà phải tính lại bảng tra theo $[40, 320]$.
4. **Vắng bóng bộ lọc thông cao HPF 60 Hz:** Khi chuyển sang xử lý giọng nói người thật thu qua micrô ở môi trường thực địa trên FPGA, bắt buộc phải khôi phục khối HPF 60 Hz của Mục 1.1.5 để bảo vệ thuật toán khỏi nhiễu tần số thấp.
5. **Hiệu ứng kẹp điểm không âm ($r \le 0 \to 0$):** Làm tăng điểm trung bình `mean_r` của câu so với trung bình số học thực tế, đồng thời làm mất khả năng phân biệt giữa các mức độ đọc sai ngữ điệu trầm trọng.
6. **Vai trò thực tế của `evaluator.py`:** Không thực hiện chức năng đánh giá ngữ điệu mà chỉ đóng vai trò trích xuất mốc thời gian từ bằng mô hình Whisper.
7. **Pearson tính trên Hertz tuyến tính:** Việc tính tương quan trực tiếp trên thang đo Hz thay vì thang đo bán âm (semitones / thang log) tạo ra trọng số thiên vị lớn hơn cho các đoạn luyến ở vùng âm vực cao.
8. **Sai số dấu phẩy động ở ngưỡng tích lũy:** Biểu thức `threshold / 10` trong Python gặp sai số dấu phẩy động rất nhỏ của chuẩn IEEE-754 ($0{,}30000000000000004$), cần lưu ý khi xây dựng logic so sánh cứng trên phần cứng RTL.

