# 1.3 Mô Hình Hóa Toán Học: STFT và Ngân Hàng Bộ Lọc Mel

> **MỤC TIÊU HỌC TẬP**
>
> 1. Tính toán tích số bất định Gabor-Heisenberg $\Delta t \cdot \Delta f = 1$ để thấy rõ sự đánh đổi vật lý không thể tránh khỏi giữa độ phân giải thời gian và tần số khi chọn chiều dài khung.
> 2. Phân tích cơ chế máy thu vuông pha (quadrature receiver) hai sóng dò $\cos$ và $-\sin$ để triệt tiêu sự mù pha, và lý giải nghịch lý kiến trúc: tại sao phần cứng buộc phải dùng hai nhánh dò trực giao chỉ để đo năng lượng rồi vứt bỏ góc pha ở ngay toán tử liền sau.
> 3. Chứng minh vì sao lưới FFT thô ($\Delta f = 31{,}25\text{ Hz}$) làm sụp đổ hình học 3 bộ lọc Mel đầu tiên ($m=0, 1, 2$), giải thích giá trị trọng số $g_{15}[14] = 1{,}00$ của dải âm 440 Hz, và tính toán chính xác số phép tính thực thi trên từng khung 10 ms.

---

## 0. Bản Hợp Đồng của Khung Âm Thanh: Năm Tham Số Tự Nhiên

Đường ống tiền xử lý âm thanh trong hệ thống không tự ý chọn các con số ngẫu nhiên. Mọi tham số đều bị trói chặt bởi các ràng buộc âm học và phần cứng:

| Tham số | Ký hiệu | Giá trị thực | Cơ sở vật lý & Ràng buộc phần cứng | Phương án bị bác bỏ |
| :--- | :---: | :---: | :--- | :--- |
| **Tần số lấy mẫu** | $f_s$ | $16.000\text{ Hz}$ | Định lý Nyquist ($f_{\max} = 8\text{ kHz}$) bao trọn dải tần tiếng nói con người ($300\text{--}3.400\text{ Hz}$). | $8\text{ kHz}$ (mất âm xát cao tần); $44{,}1\text{ kHz}$ (lãng phí $2{,}76\times$ băng thông DSP vô ích). |
| **Chiều dài khung** | $L$ | $400\text{ mẫu}$ ($25\text{ ms}$) | Khoảng thời gian âm học tiếng nói được coi là tĩnh dừng (quasi-stationary). | $10\text{ ms}$ (búp tần số quá bè, mất formant); $100\text{ ms}$ (vi phạm tính dừng, nhòe phụ âm ngắn). |
| **Bước nhảy** | $H$ | $160\text{ mẫu}$ ($10\text{ ms}$) | Độ trễ lan truyền dòng $10\text{ ms}$; gối đầu $60\%$ bù đắp suy hao năng lượng ở hai biên cửa sổ. | $25\text{ ms}$ (không gối đầu, bỏ sót biến cố âm học tức thời); $1\text{ ms}$ (quá tải tính toán $10\times$). |
| **Kích thước FFT** | $N$ | $512\text{ điểm}$ | Lũy thừa của 2 ($2^9$) cho thuật toán FFT Cooley-Tukey; đệm 112 số 0 sau 400 mẫu vật lý. | $400$ điểm (phần cứng không thể chạy FFT cơ số 2 đơn giản, buộc dùng DFT chậm hoặc thuật toán phức tạp). |
| **Số dải Mel** | $M$ | $80\text{ dải}$ | Chuẩn nén sinh học mô phỏng ốc tai người, giảm số chiều từ 257 bin FFT xuống 80 giá trị. | $20\text{ dải}$ (quá thô cho mô hình nhận dạng giọng nói ASR); $257\text{ bin}$ (quá nặng cho mô hình âm học). |

### Phép Tính Bất Định Gabor-Heisenberg Trên Khung Âm Thanh

Một tín hiệu không thể đồng thời có thời lượng vô cùng ngắn và độ rộng dải tần vô cùng hẹp. Tích số bất định thời gian - tần số luôn bị chặn dưới:

$$\Delta t \cdot \Delta f \ge 1$$

Với chiều dài khung $L = 400$ mẫu tại $f_s = 16.000\text{ Hz}$, độ mở thời gian là:

$$\Delta t = \frac{L}{f_s} = \frac{400}{16.000} = 0{,}025\text{ s} = 25\text{ ms}$$

Độ phân giải tần số vật lý tối thiểu bị khóa cứng ở mức:

$$\Delta f = \frac{1}{\Delta t} = \frac{1}{0{,}025\text{ s}} = 40\text{ Hz}$$

Tích số bất định đạt đúng cận biên:

$$\Delta t \cdot \Delta f = 25\text{ ms} \times 40\text{ Hz} = 0{,}025 \times 40 = 1{,}00$$

Mọi nỗ lực tinh chỉnh toán học phía sau (như đệm thêm số không lên 512 điểm) chỉ là phép nội suy hình thức trên lưới rời rạc; không một giải thuật nào có thể vượt qua giới hạn vật lý $40\text{ Hz}$ đã bị ấn định bởi độ dài khung $25\text{ ms}$.

---

## 1. Cửa Sổ Hamming (Hamming Window)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Sau khi Mục 1.2 cắt dòng âm thanh liên tục thành từng khung $L = 400$ mẫu, hai mép ranh giới của khung bị cắt đứt đột ngột. Làm sao để phân tích phổ mà không sinh ra các họa âm giả mạo do các bước nhảy biên nhân tạo này tạo ra?

### 2. Phương pháp thô sơ bị bác bỏ: Cửa sổ chữ nhật và thảm họa rò rỉ phổ
Nếu lấy trực tiếp 400 mẫu mà không làm mượt (tương đương nhân với cửa sổ chữ nhật $w[n]=1$), tín hiệu bị nhân với một xung vuông trong miền thời gian, tương ứng với phép cuộn với hàm $\text{sinc}$ trong miền tần số. Búp phụ đầu tiên của cửa sổ chữ nhật chỉ suy giảm $-13{,}27\text{ dB}$ so với búp chính. Năng lượng từ các tần số trầm cực mạnh sẽ rò rỉ sang các dải lân cận, làm lu mờ hoàn toàn các formant âm thanh tinh tế ở dải cao.

### 3. Công thức hiển thị
Hệ thống sử dụng cửa sổ Hamming đối xứng bậc $L = 400$:

$$w[n] = 0{,}54 - 0{,}46 \cos\left(\frac{2\pi n}{L - 1}\right), \qquad n = 0, 1, \dots, L - 1$$

Khung tín hiệu sau khi áp cửa sổ được đệm thêm 112 số không để đạt kích thước $N = 512$:

$$x_\ell[n] = \begin{cases} x[n_0 + \ell H + n] \cdot w[n], & 0 \le n < L \\ 0, & L \le n < N \end{cases}$$

Bảng đo đạc thực nghiệm 4 điểm ranh giới và đối xứng của cửa sổ Hamming ($L=400$):

| Chỉ số mẫu $n$ | Vị trí mẫu | Giá trị $w[n]$ đo được | Ý nghĩa vật lý ranh giới |
| :---: | :---: | :---: | :--- |
| $n = 0$ | Mép trái | $0{,}080000$ | Triệt tiêu bước nhảy biên đột ngột xuống $8\%$. |
| $n = 1$ | Kế mép trái | $0{,}080057$ | Đạo hàm mượt mà, ngăn ngừa rò rỉ phổ tần số cao. |
| $n = 199$ | Giữa khung | $0{,}999997$ | Bảo toàn nguyên vẹn năng lượng âm học ở tâm khung. |
| $n = 399$ | Mép phải | $0{,}080000$ | Khép kín tính đối xứng hoàn hảo ($w[399] = w[0]$). |

> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ: Thỏa Hiệp Bất Định và Rò Rỉ Phổ**
>
> So sánh phản ứng phổ giữa Cửa sổ Chữ nhật và Cửa sổ Hamming:
> - **Cửa sổ Chữ nhật:** Búp chính $\Delta f = 80\text{ Hz}$ ($2f_s/L$), búp phụ đầu tiên $-13{,}27\text{ dB}$ (tại $57{,}6\text{ Hz}$).
> - **Cửa sổ Hamming:** Búp chính $\Delta f = 160\text{ Hz}$ ($4f_s/L$), búp phụ đầu tiên $-42{,}67\text{ dB}$ (tại $134{,}4\text{ Hz}$).
> - **Mức triệt tiêu cải thiện:** Thêm $+29{,}40\text{ dB}$ suy hao búp phụ, đổi lại độ rộng búp chính tăng gấp đôi. Năng lượng rò rỉ bị khóa chặt dưới sàn $-40\text{ dB}$, bảo vệ toàn bộ các formant cao tần.

### 4. Cái giá phần cứng và điều bị phá hủy
- **Phần cứng tiêu tốn:** 400 phép nhân số thực trên mỗi khung $10\text{ ms}$ ($40.000\text{ nhân/giây}$). Các hệ số đối xứng $w[n]$ được lưu tĩnh trong ROM/LUT (chỉ cần lưu 200 giá trị nhờ tính đối xứng).
- **Điều bị phá hủy:** Phép nhân cửa sổ phá hủy hoàn toàn biên độ gốc của các mẫu ở hai mép khung ($w[0] = 0{,}08$). Để bù đắp điểm mù này, hệ thống bắt buộc phải gối đầu khung sâu $60\%$ ($H = 160$ mẫu, chia sẻ lại 240 mẫu với khung trước).

---

## 2. Thẩm Tra Sóng Bằng Hai Sóng Dò Vuông Pha (Quadrature Probe Waves)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Khung âm thanh $x_\ell[n]$ sau cửa sổ là một chuỗi 400 con số thực. Làm sao kiểm tra xem trong chuỗi này có tồn tại dao động ở một tần số cụ thể $f_k$ hay không?

### 2. Sóng dò đơn lẻ và hiện tượng mù pha (Phase Blindness)
Phương pháp tự nhiên nhất là nhân tín hiệu đầu vào với một sóng dò chuẩn $\cos\left(\frac{2\pi k n}{N}\right)$ rồi cộng dồn lại:

$$\text{Tích lũy} = \sum_{n=0}^{N-1} x[n] \cos\left(\frac{2\pi k n}{N}\right)$$

Nếu $x[n]$ chứa sóng đồng pha $\cos$, tích phân sẽ tích lũy thành một giá trị dương rất lớn. Nhưng nếu sóng đầu vào bị trễ một phần tư chu kỳ ($\pi/2$, tức là sóng $\sin$), tích phân của $\sin \times \cos$ trên một chu kỳ nguyên vẹn bằng đúng 0:

$$\sum_{n=0}^{N-1} \sin\left(\frac{2\pi k n}{N}\right) \cos\left(\frac{2\pi k n}{N}\right) = 0$$

Máy đo hoàn toàn mù trước tín hiệu dù âm thanh đang gầm vang ở đúng tần số đó.

### Hai sóng dò trực giao và đẳng thức Euler
Để triệt tiêu hiện tượng mù pha, ta phải dùng **hai sóng dò trực giao lệch pha $90^\circ$**: sóng đồng pha $\cos\left(\frac{2\pi k n}{N}\right)$ (nhánh Thực) và sóng vuông pha $-\sin\left(\frac{2\pi k n}{N}\right)$ (nhánh Ảo). Theo định lý Pythagoras, biên độ sóng được phục hồi bất biến trước pha xuất hiện:

$$|X[k]| = \sqrt{\text{Re}^2 + \text{Im}^2}$$

Đẳng thức Euler $e^{-j\theta} = \cos\theta - j\sin\theta$ chính là công thức toán học đại diện cho máy thu vuông pha phần cứng hai kênh này.

### Đo Lường Thực Nghiệm: Tính Bất Biến Pha Của Máy Thu Vuông Pha
Kiểm chứng từ `chapter01/lab_1_3.py` trên khung sóng $440\text{ Hz}$ ($k=14$):
- **Trường hợp gốc (Góc pha ban đầu $\theta \approx 0$):**
  $$\text{Re} = +105{,}34, \quad \text{Im} = +20{,}89 \implies |X|^2 = (105{,}34)^2 + (20{,}89)^2 = 11.532{,}71$$
- **Trường hợp dịch trễ 1/4 chu kỳ (+9 mẫu, $\Delta\theta \approx 90^\circ$):**
  $$\text{Re}' = -19{,}27, \quad \text{Im}' = +105{,}74 \implies |X'|^2 = (-19{,}27)^2 + (105{,}74)^2 = 11.552{,}08$$
- **Sai số năng lượng giữa hai pha xuất hiện:** chỉ $0{,}17\%$, chứng minh tính bất biến pha tuyệt đối.

> **$\bigstar$ PHÁT HIỆN THEN CHỐT: Máy Thu Vuông Pha Phần Cứng**
>
> Một bin phổ phức $X[k]$ là một máy thu vuông pha hai kênh: nhánh $\cos$ đo phần thực $\text{Re}$, nhánh $-\sin$ đo phần ảo $\text{Im}$. Năng lượng tín hiệu $|X[k]|^2 = \text{Re}^2 + \text{Im}^2$ hoàn toàn không phụ thuộc vào thời điểm sóng âm ập đến micro.

### Nghịch Lý Kiến Trúc Lớn Nhất Của Đường Ống
Để đo đúng năng lượng sóng mà không bị mù pha, phần cứng bắt buộc phải nhân đôi tài nguyên: 2 bộ nhân, 2 bộ tích lũy, sinh ra số phức gồm 2 thành phần $(\text{Re}, \text{Im})$. Thế nhưng, ngay ở toán tử tiếp theo, hệ thống tính $|X|^2 = \text{Re}^2 + \text{Im}^2$ và **thản nhiên vứt bỏ hoàn toàn góc pha $\theta = \arctan(\text{Im}/\text{Re})$ đi mãi mãi**!

Sự vứt bỏ này không phải là sai sót, mà là một quyết định kiến trúc: não bộ và mạng nơ-ron nhận dạng nguyên âm dựa trên vị trí các đỉnh formant chứ không dựa vào pha sóng âm. Vứt bỏ pha giúp nén dữ liệu và giải phóng áp lực băng thông cho mô hình nhận dạng hạ nguồn.

---

## 3. Biến Đổi Fourier Thời Gian Ngắn (STFT)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Máy thu vuông pha ở Mục 2 mới chỉ kiểm tra một tần số đơn lẻ $k$. Làm sao quét đồng thời toàn bộ dải phổ âm thanh từ $0$ đến $8.000\text{ Hz}$?

### 2. Dự đoán bin đỉnh trước công thức
Lưới tần số STFT với $N = 512$ điểm ở $f_s = 16.000\text{ Hz}$ có bước nhảy bin:

$$\Delta f = \frac{f_s}{N} = \frac{16.000}{512} = 31{,}25\text{ Hz}$$

Âm thanh đơn tần $440\text{ Hz}$ rơi vào chỉ số phân đoạn:

$$k = \frac{440}{31{,}25} = 14{,}08$$

Vì $14{,}08$ nằm gần số nguyên 14 nhất ($14 \times 31{,}25 = 437{,}5\text{ Hz}$ so với bin 15 là $468{,}75\text{ Hz}$), người đọc có thể **dự đoán chắc chắn bin đỉnh công suất phải là bin 14**. Kết quả thực nghiệm từ `chapter01/lab_1_3.py` xác nhận: `argmax bin: 14 (437.5 Hz)`.

### 3. Công thức hiển thị
$$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n] \, e^{-j \frac{2\pi k n}{N}}, \qquad k = 0, 1, \dots, N-1$$

Do tính đối xứng liên hợp của tín hiệu thực ($X_\ell[N-k] = X_\ell^*[k]$), phần cứng chỉ cần giữ lại $N/2 + 1 = 257$ bin đầu tiên ($0\text{--}8.000\text{ Hz}$) là bảo toàn toàn bộ năng lượng phổ.

### 4. Cái giá phần cứng và điều bị phá hủy
- **DFT trực tiếp:** Để tính đủ $N = 512$ bin, mỗi bin cần $N$ tích phức:
  $$N^2 = 512^2 = 262.144\text{ phép nhân phức mỗi khung } 10\text{ ms}$$
- **FFT cơ số 2 (Cooley-Tukey):** Tái sử dụng các hệ số quay tuần hoàn, giảm khối lượng xuống:
  $$\frac{N}{2} \log_2 N = \frac{512}{2} \times 9 = 2.304\text{ bướm tính toán (butterflies) mỗi khung}$$
- Cần nhấn mạnh: **một bướm tính toán không phải là một phép nhân phức đơn lẻ**. Một bướm radix-2 bao gồm một phép nhân phức với hệ số quay $W_N^k$ và hai phép cộng/trừ phức. Tỷ số giảm tải hơn 100 lần giữa 262.144 và 2.304 chính là lý do các kiến trúc phần cứng chuyên dụng bắt buộc phải triển khai FFT thay vì ma trận DFT nhân thẳng.

*Bản chất của đệm số không (Zero-padding):* Việc thêm 112 số không vào sau 400 mẫu khung không tạo thêm thông tin vật lý mới. Nó chỉ làm lưới nội suy phổ dày hơn (chia từ bước $40\text{ Hz}$ của khung 400 điểm thành bước $31{,}25\text{ Hz}$ của lưới 512 điểm). Búp chính của tín hiệu vẫn giữ nguyên độ rộng vật lý do $L = 400$ ấn định.

### Đo Lường Thực Nghiệm: Lưới 400 Điểm So Với Lưới 512 Điểm Trên Sóng 440 Hz
Bảng số liệu đo từ `chapter01/lab_1_3.py`:

| Lưới lấy mẫu | Độ phân giải bin | Bin đỉnh | Tần số bin đỉnh | Công suất đo được $|X|^2$ |
| :--- | :---: | :---: | :---: | :---: |
| Lưới 400 điểm (không đệm số 0) | $\Delta f = 40{,}00\text{ Hz}$ | $k = 11$ | $440{,}0\text{ Hz}$ (trùng khít) | $11.613{,}77$ |
| Lưới 512 điểm (đệm 112 số 0) | $\Delta f = 31{,}25\text{ Hz}$ | $k = 14$ | $437{,}5\text{ Hz}$ (lệch $2{,}5\text{ Hz}$) | $11.532{,}71$ |

Đo đạc minh chứng rõ nét: đệm số 0 chỉ lấy mẫu dày hơn trên đường cong DTFT có sẵn, không làm hẹp búp chính vật lý của tín hiệu.

---

## 4. Toán Tử Công Suất (Power Spectrum Operator)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Đầu ra của STFT là một mảng $257$ số phức $X_\ell[k] = \text{Re} + j\text{Im}$. Làm sao biến đổi mảng này thành mật độ năng lượng thực để đưa vào các tầng nhận diện tiếp theo?

### 2. Cơ chế vật lý: Vứt bỏ góc pha và bảo tồn biên độ Pythagoras
Phổ công suất tính bình phương biên độ của từng số phức:

$$P_\ell[k] = |X_\ell[k]|^2 = \text{Re}(X_\ell[k])^2 + \text{Im}(X_\ell[k])^2$$

Góc pha $\theta = \arctan(\text{Im}/\text{Re})$ chính thức bị triệt tiêu hoàn toàn. Năng lượng âm học được nén từ 2 dòng dữ liệu thực/ảo thành một dòng số thực không âm duy nhất.

### 3. Công thức hiển thị
$$P_\ell[k] = X_{\text{re}}^2[\ell, k] + X_{\text{im}}^2[\ell, k], \qquad k = 0, 1, \dots, 256$$

### 4. Cái giá phần cứng và điều bị phá hủy
- **Phần cứng tiêu tốn:** $257 \times 2 = 514$ phép nhân thực và $257$ phép cộng thực trên mỗi khung $10\text{ ms}$ ($51.400\text{ nhân/giây}$). Đây là một thao tác cực kỳ nhẹ, hoàn toàn song song hóa trên FPGA.
- **Điều bị phá hủy:** Mất vĩnh viễn thông tin pha. Không thể tái tạo lại dạng sóng âm thanh gốc từ $P_\ell[k]$ nếu không dùng các giải thuật ước lượng pha lặp (như Griffin-Lim) hoặc mô hình mạng nơ-ron sinh âm (vocoder).

---

## 5. Ngân Hàng Bộ Lọc Mel (Mel Filterbank)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Tai người không cảm nhận tần số theo thang tuyến tính Hertz. Một khoảng cách $100\text{ Hz}$ ở dải trầm ($200\text{--}300\text{ Hz}$) tạo ra sự khác biệt cao độ rất lớn, nhưng ở dải cao ($5.000\text{--}5.100\text{ Hz}$) tai người hầu như không phân biệt được. Làm sao nén $257$ bin tuyến tính thành một vector cảm nhận sinh học?

### 2. Bộ lọc thực tế mã nguồn xây dựng và hiện tượng sụp đổ (Filter Collapse)
Hàm `create_mel_filterbank(num_filters=80, n_fft=512, fs=16000)` ánh xạ dải $0\text{--}8.000\text{ Hz}$ sang thang Mel. Mảng ranh giới gồm 82 điểm:

$$\text{bin\_points} = \left\lfloor \frac{(N + 1) \cdot f_{\text{mel}}}{f_s} \right\rfloor$$

Khi phân tích chi tiết mảng ranh giới từ `chapter01/lab_1_3.py`, một hiện tượng phần cứng bất ngờ lộ diện: **3 bộ lọc đầu tiên bị sụp đổ (Filter Collapse)** do lưới FFT quá thô:
- **Bộ lọc 0 ($m = 0$):** Ranh giới bin là `[0, 0, 1]`. Điểm mép trái và đỉnh tâm trùng nhau tại bin 0! Bộ lọc này không còn là hình tam giác, mà bị sụp đổ cạnh trái, chỉ còn một cạnh dốc từ bin 0 lên bin 1.
- **Bộ lọc 1 ($m = 1$):** Ranh giới bin là `[0, 1, 2]`. Giữ được hình tam giác tối thiểu 3 điểm.
- **Bộ lọc 2 ($m = 2$):** Ranh giới bin là `[1, 2, 2]`. Bị sụp đổ cạnh phải (đỉnh và mép phải trùng tại bin 2).
- **Bộ lọc 3 ($m = 3$):** Ranh giới bin là `[2, 2, 3]`. Bị sụp đổ cạnh trái (mép trái và đỉnh trùng tại bin 2).

Tổng cộng có đúng **3 bộ lọc bị sụp đổ** ($m=0, 2, 3$). Đây là phát hiện quan trọng: kỹ sư phần cứng không được mặc định mọi bộ lọc đều là hình tam giác đối xứng hoàn hảo!

Ở dải âm $440\text{ Hz}$, Bộ lọc 15 có ranh giới `[13, 14, 15]`. Đỉnh của bộ lọc nằm tại chính xác bin 14 ($437{,}5\text{ Hz}$) với trọng số tuyệt đối:

$$g_{15}[14] = 1{,}00$$

Ở dải tần số cao, Bộ lọc 79 trải rộng từ bin 239 đến bin 256 ($7.475\text{--}8.000\text{ Hz}$), phủ qua 17 bin FFT liên tiếp, phản ánh rõ đặc tính làm nhòe tần số ở dải cao của ốc tai.

### 3. Công thức ánh xạ Mel
$$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right) = 1127 \ln\left(1 + \frac{f}{700}\right)$$

### 4. Trọng số tam giác và nhân ma trận thưa
Mỗi bộ lọc $m$ có dạng tam giác được xác định bởi 3 điểm bin $[f_{m-1}, f_m, f_{m+1}]$:

$$H_m[k] = \begin{cases} 0, & k < f_{m-1} \\ \frac{k - f_{m-1}}{f_m - f_{m-1}}, & f_{m-1} \le k \le f_m \\ \frac{f_{m+1} - k}{f_{m+1} - f_m}, & f_m \le k \le f_{m+1} \\ 0, & k > f_{m+1} \end{cases}$$

Năng lượng dải Mel là tổng có trọng số:

$$E_\ell[m] = \sum_{k=0}^{N/2} P_\ell[k] \, H_m[k], \qquad m = 0, 1, \dots, M-1$$

### 5. Cái giá phần cứng và điều bị phá hủy
- **Phần cứng tiêu tốn:** Về mặt lý thuyết, phép nhân ma trận $[80 \times 257]$ đòi hỏi $80 \times 257 = 20.560$ phép nhân. Nhưng vì ma trận $H$ cực kỳ thưa (mỗi bin $k$ chỉ thuộc tối đa 2 bộ lọc tam giác kề nhau), số phép nhân thực tế chỉ là $2 \times 257 \approx 514$ phép tính trên mỗi khung $10\text{ ms}$.
- **Điều bị phá hủy:** Toàn bộ cấu trúc họa âm sắc nét ở dải cao bị nung chảy thành năng lượng trung bình của các dải rộng.

---

## 6. Nén Logarit (Logarithmic Compression)

### 1. Câu hỏi giai đoạn trước không thể trả lời
Năng lượng $E_\ell[m]$ giữa các dải Mel có thể chênh lệch nhau hàng triệu lần. Nếu đưa thẳng vào mạng nơ-ron, dải âm lượng lớn nhất sẽ chi phối hoàn toàn hàm mất mát và gradient.

### 2. Phương pháp thô sơ và độ to cảm nhận
Độ to mà con người cảm nhận tỷ lệ thuận với logarit của năng lượng âm thanh vật lý (Định luật Weber-Fechner). Hơn nữa, sự thay đổi khoảng cách micro hoặc độ lợi khuếch đại (gain) $g$ sẽ nhân toàn bộ năng lượng âm thanh với hệ số $g^2$. Khi đi qua hàm logarit:

$$\ln(g^2 \cdot E) = \ln(E) + 2\ln(g)$$

Yếu tố khuếch đại có tính chất nhân bị biến đổi thành một **độ lệch cộng tính cố định** $2\ln(g)$ trên toàn bộ các khung. Đây chính là nền tảng toán học giúp kỹ thuật chuẩn hóa trừ trung bình theo thời gian (Cepstral Mean Normalization -- CMN) triệt tiêu hoàn toàn ảnh hưởng của độ nhạy micro!

Ba giá trị đo thực nghiệm từ phòng thí nghiệm Lab 1.3:
- **Năng lượng lớn (dải 15 từ âm 440 Hz):** $E = 11.532{,}71 \implies \ln(11.532{,}71) = \mathbf{9{,}3529}$.
- **Năng lượng đơn vị:** $E = 1{,}0 \implies \ln(1{,}0) = \mathbf{0{,}0000}$.
- **Năng lượng cực tiểu dưới ngưỡng sàn ($10^{-8} < 10^{-6}$):** Bị kẹp sàn tại $10^{-6} \implies \ln(10^{-6}) = \mathbf{-13{,}8155}$.

### 3. Công thức hiển thị
$$S_\ell[m] = \ln(\max(E_\ell[m], 10^{-6})), \qquad m = 0, 1, \dots, M-1$$

### 4. Cái giá phần cứng và điều bị phá hủy
- **Phần cứng tiêu tốn:** Đúng **80 phép tính logarit tự nhiên trên mỗi khung 10 ms**. Trên phần cứng FPGA, hàm logarit không được tính bằng chuỗi Taylor dấu phẩy động chậm chạp mà được xấp xỉ bằng bảng tra kết hợp đa thức bậc một từng đoạn (piecewise linear approximation).
- **Điều bị phá hủy:** Đạo hàm $\frac{d}{dx} \ln(x) = \frac{1}{x}$ tiến tới vô hạn khi $x \to 0$. Ngưỡng chặn sàn $10^{-6}$ ngăn chặn lỗi số học $-\infty$ khi gặp khoảng lặng tuyệt đối, nhưng đồng thời cũng san phẳng mọi biến thiên âm học vi mô nằm dưới mức năng lượng $10^{-6}$.

---

## 7. Bảng Sổ Cái Kỹ Thuật (Pipeline Ledger)

Bảng sổ cái dưới đây tổng hợp trọn vẹn năm giai đoạn toán tử được đo đạc và xác thực trực tiếp từ mã nguồn phòng thí nghiệm `chapter01/lab_1_3.py`:

| Toán tử | Câu hỏi vật lý được trả lời | Kích thước vào $\to$ ra | Khối lượng số học / 10 ms | Điều bị phá hủy |
| :--- | :--- | :---: | :--- | :--- |
| **1. Cửa sổ** | Cắt hữu hạn mà không sinh rò rỉ phổ rác? | $[400] \to [512]$ (đệm 112 số 0) | 400 phép nhân thực | Biên khung bị đè về 0,08; buộc phải gối 60%. |
| **2. STFT** | Nhận diện tần số cộng hưởng không mù pha? | $[512] \to [257]$ số phức | 2.304 bướm FFT radix-2 ($262.144$ tích ở DFT thẳng) | Giả định tuần hoàn; độ phân giải chặn bởi $L = 400$. |
| **3. Công suất** | Trích xuất năng lượng âm học bỏ qua góc pha? | $[257] \to [257]$ số thực | 514 phép tính thực ($257$ bình phương + $257$ cộng) | Mất vĩnh viễn góc pha; không thể nghe lại dạng sóng. |
| **4. Mel** | Uốn phổ theo tai người và giảm chiều mô hình? | $[257] \to [80]$ dải | Nhân ma trận thưa (tối đa 2 tích/bin tích cực) | Phổ dải cao bị nung chảy; 3 bộ lọc thấp bị sụp đổ. |
| **5. Log** | Nén dải động và biến độ lợi micro thành độ lệch? | $[80] \to [80]$ log-Mel | 80 phép tính logarit tự nhiên (bảng tra đa thức) | Mất chi tiết dưới sàn $10^{-6}$; độ dốc phân kỳ gần 0. |

---

## 8. Ba Câu Hỏi Tự Đánh Giá Năng Lực Sư Phạm

Để bảo đảm người học không chỉ ghi nhớ công thức thụ động mà thấu suốt cơ chế vật lý bên dưới, hãy tự trả lời ba câu hỏi phản biện kiến trúc sau đây:

1. **Về định vị bin và đệm số không:** Một âm thanh đơn tần $1.000\text{ Hz}$ được lấy mẫu ở $16.000\text{ Hz}$ và đưa vào khung STFT $N = 512$ điểm. Tín hiệu này sẽ rơi vào chính xác bin tần số số mấy? Việc đệm thêm 112 số không vào sau 400 mẫu của khung có làm cho búp đỉnh nhọn hơn và sắc nét hơn về mặt vật lý hay không?
   - *Trả lời:* Bước nhảy mỗi bin là $\Delta f = 16.000 / 512 = 31{,}25\text{ Hz}$. Chỉ số bin là $k = 1.000 / 31{,}25 = 32$. Tín hiệu rơi chính xác vào **bin 32**. Việc đệm 112 số không **hoàn toàn không làm thu hẹp búp đỉnh vật lý**; nó chỉ lấy mẫu dày hơn trên đường cong DTFT vốn có độ rộng búp chính bị khóa chặt bởi chiều dài cửa sổ vật lý $L = 400$ mẫu ($\Delta t = 25\text{ ms}$).

2. **Về hiện tượng mù pha và sự vứt bỏ góc pha:** Tại sao một sóng dò $\cos$ đơn lẻ lại báo năng lượng xấp xỉ bằng không khi gặp một sóng $\sin$ có cùng tần số? Nếu hai sóng dò trực giao ($\cos$ và $-\sin$) là bắt buộc để đo đúng năng lượng sóng, tại sao ở toán tử liền sau chúng ta lại thản nhiên vứt bỏ góc pha đi?
   - *Trả lời:* Sóng $\sin$ lệch pha $90^\circ$ so với sóng $\cos$. Tích phân hai hàm trực giao trên một chu kỳ nguyên vẹn triệt tiêu hoàn toàn về không, tạo ra sự mù pha. Cần hai nhánh trực giao để theo định lý Pythagoras tính được biên độ $A = \sqrt{\text{Re}^2 + \text{Im}^2}$ bất biến trước thời điểm xuất hiện của sóng. Sau khi biên độ đã được bảo toàn trong công suất thực $P[k] = \text{Re}^2 + \text{Im}^2$, góc pha âm học không còn mang thông tin nhận dạng ngữ âm (não bộ và mạng nơ-ron nhận diện nguyên âm dựa trên vị trí đỉnh formant chứ không dựa vào pha sóng đến micro), nên việc loại bỏ pha giúp giải phóng bộ nhớ và giảm độ phức tạp cho mô hình hạ nguồn.

3. **Về hình học ngân hàng bộ lọc Mel:** Bộ lọc số 0 ($m = 0$) trong cấu hình 80 dải Mel của hệ thống có còn giữ được hình dạng tam giác cân đối hay không? Hãy chỉ ra nguyên nhân toán học dẫn đến hình dạng đó.
   - *Trả lời:* **Không, Bộ lọc 0 không còn là hình tam giác**. Nó bị sụp đổ cạnh trái vì cả mép trái và đỉnh tâm đều bị làm tròn về cùng bin 0 ($[0, 0, 1]$). Nguyên nhân là ở dải tần số cực thấp ($0\text{--}22\text{ Hz}$), khoảng cách giữa các tần số tâm Mel liên tục hẹp hơn độ phân giải rời rạc của lưới FFT ($\Delta f = 31{,}25\text{ Hz}$), khiến phép làm tròn sàn số nguyên $\lfloor (N+1)f/f_s \rfloor$ ép hai điểm ranh giới trùng vào một bin duy nhất.

---

## 9. Khởi Chạy và Tái Hiện Thực Nghiệm

Mọi con số, đường cong và bảng biểu trong mục này được sinh ra và kiểm chứng bằng lệnh duy nhất:

```bash
python chapter01/lab_1_3.py
```

và bộ kiểm thử tự động toàn diện:

```bash
python -m pytest chapter01/test_lab_1_3.py
```

Ba dòng kết quả then chốt từ đầu ra chuẩn của chương trình khớp tuyệt đối từng chữ số với các hình minh họa:
1. **Khớp Hình 1.3a & Mục 3:**
   `argmax bin: 14 (437.5 Hz), Re = 105.3388, Im = 20.8916, Power = 11532.71`
2. **Khớp Hình 1.3b & Mục 5:**
   `filter-0 edges: [0, 0, 1], filter-79 edges: [239, 247, 256], collapsed count: 3`
3. **Khớp Hình 1.3_speech & Mục 7:**
   `speech a (sample_speech_a.wav): peak frame 66, top 3: Band 13 (3.26), Band 14 (3.15), Band 10 (2.16)`
