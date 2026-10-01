# 1.3 Mô Hình Hóa Toán Học: STFT và Ngân Hàng Bộ Lọc Mel

Mục 1.2 đã xây dựng đường truyền dữ liệu (datapath) vật lý đóng gói áp suất không khí dạng dòng thành các khung rời rạc. Mục 1.3 là chiếc kính hiển vi toán học đặt lên một gói dữ liệu đơn lẻ, suy diễn từng toán tử biến đổi phổ từ hiện tượng giao thoa sóng và cơ chế cảm nhận thính giác.

Sáu biểu thức biến dòng mẫu thành 80 con số trên mỗi khung:
1. Khung sau áp cửa sổ (The Windowed Frame)
2. Biến đổi Fourier thời gian ngắn (Short-Time Fourier Transform -- STFT)
3. Phổ công suất (The Power Spectrum)
4. Ánh xạ tần số Mel (Mel-Frequency Mapping)
5. Ngân hàng bộ lọc Mel là tổng có trọng số (Mel Filterbank as a Weighted Sum)
6. Nén logarit (Logarithmic Compression)

Mỗi phép toán được giải phẫu qua năm nhịp cố định: công thức, ký hiệu, ý nghĩa vật lý, giá phần cứng, và điều công thức giấu.

Các thông số thiết kế chuẩn:
Tần số lấy mẫu $f_s = 16.000\text{ Hz}$, chiều dài khung $L = 400$ mẫu ($25\text{ ms}$), bước nhảy $H = 160$ mẫu ($10\text{ ms}$), kích thước biến đổi $N = 512$ điểm, số lượng kênh bộ lọc $M = 80$ dải, dải tần phân tích từ $f_{\min} = 0\text{ Hz}$ đến $f_{\max} = 8.000\text{ Hz}$.

---

## Sóng Dò, Trước Công Thức

Trước khi viết ra phép lấy tổng Fourier, hãy xem xét bài toán thẩm tra vật lý. Một gói âm thanh chưa biết ập vào cảm biến dưới dạng chuỗi dịch chuyển áp suất không khí rời rạc $x_\ell[n]$. Làm sao một mạch số biết được gói âm thanh này có dao động ở một tần số cụ thể $f_k$ hay không?

Trong vật lý cổ điển, hiện tượng cộng hưởng được phát hiện bằng cách thăm dò: ta đưa một dao động ngoại vi đã biết tần số $\omega_k$ vào tiếp xúc với hệ thống để quan sát sự truyền năng lượng ở trạng thái xác lập. Trong tính toán số, ta tạo ra một âm sóng dò tham chiếu nội bộ và đánh giá sự giao thoa tăng cường hay triệt tiêu thông qua tích vô hướng với tín hiệu đầu vào:

$$\int_0^T x(t) \cos(\omega_k t) \, dt$$

Nếu $x(t)$ chứa dao động tại $\omega_k$ cùng pha ($\cos(\omega_k t)$), tích số trở thành $\cos^2(\omega_k t) = \frac{1 + \cos(2\omega_k t)}{2}$. Tích phân qua một số nguyên chu kỳ $T$, thành phần tần số cao $2\omega_k$ triệt tiêu về 0, để lại phần tích lũy DC dương bằng $\frac{T}{2}$. Nếu $x(t)$ dao động tại bất kỳ họa âm nào khác $\omega_m$ ($m \ne k$), tích phân chéo triệt tiêu hoàn toàn về 0. Sóng dò chỉ cộng hưởng duy nhất với đúng tần số của nó.

Bây giờ, hãy vạch trần tử huyệt của một sóng dò đơn lẻ: **sự mù pha** (phase blindness).

Giả sử gói âm thanh đầu vào chứa một âm thuần tại $\omega_k$, nhưng lại đến trễ một phần tư chu kỳ (độ lệch pha bằng $\pi/2$, biến đầu vào thành sóng sin thuần $\sin(\omega_k t)$). Tích số mà sóng dò cosin đánh giá lúc này là $\sin(\omega_k t)\cos(\omega_k t) = \frac{1}{2}\sin(2\omega_k t)$. Trên khoảng tích phân $T$, sóng này cho kết quả tích phân bằng đúng 0:

$$\int_0^T \sin(\omega_k t) \cos(\omega_k t) \, dt = 0$$

Sóng dò đơn lẻ báo về mức năng lượng bằng 0. Một âm thanh thuần khiết đang gầm vang qua bộ chuyển đổi vật lý, nhưng vì đến lệch pha $90^\circ$, bộ tách sóng toán học của chúng ta hoàn toàn điếc trước nó.

Để xóa bỏ sự mù pha, ta phải thẩm tra sóng âm bằng **hai sóng dò trực giao vuông pha** (quadrature): sóng dò đồng pha (in-phase) dao động theo $\cos(\omega_k t)$ và sóng dò vuông pha dao động theo $-\sin(\omega_k t)$ (trễ pha $90^\circ$). Khi một tín hiệu bất kỳ $x(t) = A \cos(\omega_k t + \theta)$ đập vào bộ tách sóng hai nhánh này, nhánh cosin đo được $A \cos\theta$ và nhánh sin đo được $A \sin\theta$. Theo định lý Pythagoras, biên độ toàn phần của tín hiệu được khôi phục với sự miễn nhiễm pha tuyệt đối:

$$A = \sqrt{(A\cos\theta)^2 + (A\sin\theta)^2}$$

Đồng nhất thức Euler, $e^{-j\theta} = \cos\theta - j\sin\theta$, chính là chiếc vỏ bọc đại số của máy thu vuông pha phần cứng hai kênh này.

```
                  +---> [ * cos(2 pi k n / N) ] ---> [ Bộ tích lũy ] ---> Re(X[k]) ---+
                  |                                                                     |---> X[k] = Re + j Im
x[n] (Khung) -----+                                                                     |
                  |                                                                     |
                  +---> [ * -sin(2 pi k n / N) ] --> [ Bộ tích lũy ] ---> Im(X[k]) ---+
```

> [!TIP]
> **$\bigstar$ PHÁT HIỆN THEN CHỐT**
>
> Một bin phổ phức là một máy thu vuông pha phần cứng hai kênh: hai bộ dao động chuẩn trực giao ($\cos$ và $-\sin$) đập nhịp cùng sóng áp suất đầu vào, trả về hai điểm số tương đồng giúp khôi phục biên độ tín hiệu bất biến trước pha xuất hiện.

---

## 1. Khung Sau Áp Cửa Sổ

Để loại bỏ các bước nhảy biên nhân tạo tại ranh giới khung, đoạn âm thanh hữu hạn phải được thuôn mượt về 0 trước khi giải tích phổ.

### Giải Phẫu 5 Nhịp: Khung Sau Áp Cửa Sổ

**Nhịp 1: Công Thức**
$$x_\ell[n] = x[n_0 + \ell H + n] \, w[n], \qquad n = 0, 1, \dots, L-1$$
tiếp nối bởi bước đệm thêm số 0 lên chiều dài biến đổi $N = 512$:
$$x_\ell[n] = 0, \qquad L \le n < N$$

**Nhịp 2: Ký Hiệu**
- $x_\ell[n]$: khung sau áp cửa sổ $\ell$, gồm $L = 400$ mẫu ($25\text{ ms}$ ở $f_s = 16.000\text{ Hz}$).
- $x$: dòng âm thanh liên tục đầu vào.
- $H$: bước nhảy, $160$ mẫu ($10\text{ ms}$).
- $L$: chiều dài khung vật lý, $400$ mẫu ($25\text{ ms}$).
- $w[n]$: cửa sổ đối xứng Hamming, thuôn dần hai mép ranh giới về $w[0] = w[L-1] = 0{,}08$ và đạt đỉnh $1{,}00$ ở chính giữa.

**Nhịp 3: Ý Nghĩa Vật Lý**
Việc cắt phẳng một tín hiệu liên tục bằng nhát cắt chữ nhật tương đương với nhân với một cửa sổ chữ nhật, cuộn phổ gốc với hàm sinc trong miền tần số. Các búp phụ của cửa sổ chữ nhật suy hao rất chậm, búp phụ đầu tiên nhô cao tới $-13\text{ dB}$ so với búp chính. Cấu hình cosin nâng thuôn mượt của cửa sổ Hamming ghìm hai ranh giới xuống $0{,}08$, nén búp phụ đầu tiên xuống $-44\text{ dB}$---giảm rò rỉ phổ giả mạo tới $31\text{ dB}$.

```
Hình 6: Phản ứng phổ của Cửa sổ Chữ nhật so với Cửa sổ Hamming
-----------------------------------------------------------------------------------------
Cửa sổ chữ nhật:  Bề rộng búp chính = 2 f_s / L = 80 Hz    Búp phụ đầu = -13 dB
Cửa sổ Hamming:   Bề rộng búp chính = 4 f_s / L = 160 Hz   Búp phụ đầu = -44 dB
Hiệu quả suy hao: Triệt tiêu thêm 31 dB búp phụ, đổi lại bề rộng búp chính tăng gấp đôi.
```

> [!NOTE]
> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ**
>
> Áp cửa sổ là một thỏa hiệp bắt buộc với nguyên lý bất định: ta chấp nhận tăng gấp đôi độ rộng búp chính (từ $80\text{ Hz}$ lên $160\text{ Hz}$) để đổi lấy $31\text{ dB}$ triệt tiêu búp phụ. Nếu không triệt tiêu rò rỉ phổ, năng lượng khổng lồ từ các họa âm cơ bản trầm sẽ làm lu mờ hoàn toàn các formant cao tần tinh tế trên toàn phổ.

**Nhịp 4: Giá Phần Cứng**
Tiêu tốn $L = 400$ phép nhân số thực trên mỗi khung $10\text{ ms}$. Các hệ số cửa sổ đối xứng được lưu sẵn trong bảng tra trên chip. Các bộ nhân tạo đường ống hoàn tất tầng này dễ dàng trong nhịp khung. Số lát cắt phần cứng chính xác được phân tích ở Mục 1.4 / Chương 6.

**Nhịp 5: Điều Công Thức Giấu**
Cửa sổ thuôn triệt tiêu năng lượng âm học ở hai đầu mút khung, ép các mẫu biên về gần 0. Để không tạo ra điểm mù khiến các biến cố âm học tức thời biến mất không dấu vết, các khung kế tiếp bắt buộc phải gối đầu sâu: bước nhảy $H = 160$ mẫu chỉ tiến thêm $40\%$ chiều dài cửa sổ, để lại vùng gối đầu $60\%$ ($L - H = 240$ mẫu chia sẻ) bảo đảm năng lượng âm thanh được bao phủ liên tục, đồng đều dọc theo trục thời gian.

---

## 2. Biến Đổi Fourier Thời Gian Ngắn (STFT)

Sau khi áp cửa sổ và đệm số 0, ta thiết lập ma trận phổ phụ thuộc thời gian để ánh xạ các bước chuyển ngữ âm khi chúng biến thiên theo thời gian.

### Giải Phẫu 5 Nhịp: Biến Đổi Fourier Thời Gian Ngắn

**Nhịp 1: Công Thức**
$$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n] \, e^{-j \frac{2\pi k n}{N}}, \qquad k = 0, 1, \dots, N-1$$

**Nhịp 2: Ký Hiệu**
- $k \in \{0, 1, \dots, N-1\}$: chỉ số bin tần số rời rạc, ánh xạ về tần số vật lý $f_k = k \frac{f_s}{N} = k \times \frac{16.000}{512} = k \times 31{,}25\text{ Hz}$.
- $n \in \{0, 1, \dots, N-1\}$: chỉ số mẫu thời gian trong khung phân tích đệm $N$ điểm.
- $x_\ell[n]$: tín hiệu sau khi áp cửa sổ, được đệm thêm $N - L = 512 - 400 = 112$ số 0 lên chiều dài $N = 512$.
- $X_\ell[k]$: hệ số phổ phức. Vì tín hiệu đầu vào hoàn toàn là số thực, nửa trên của phổ có tính đối xứng liên hợp ($X_\ell[N-k] = X_\ell^*[k]$), cho phép giữ lại duy nhất $N/2 + 1 = 257$ bin tần số độc lập ($0\text{ Hz}$ đến $8.000\text{ Hz}$).

**Nhịp 3: Ý Nghĩa Vật Lý**
STFT chiếu tín hiệu thời gian 1D sang không gian tọa độ thời gian - tần số phức 2D, cân bằng sự đánh đổi cốt lõi giữa định vị thời gian và độ phân giải tần số. Cửa sổ $25\text{ ms}$ cách ly các lát cắt âm thanh có tính dừng thời gian, đồng thời đem lại độ chi tiết tần số vừa đủ ($\Delta f = 31{,}25\text{ Hz}$) để phân tách các đỉnh cộng hưởng formant cơ bản.

**Nhịp 4: Giá Phần Cứng**
Tính toán trực tiếp tiêu tốn $N$ bin $\times N$ phép nhân - cộng phức mỗi khung $10\text{ ms}$. Thuật toán FFT cơ số 2 giúp người thiết kế không bị kẹt ở $N^2$, giảm khối lượng số học xuống $\frac{N}{2} \log_2 N$ bướm tính toán mỗi khung. Số lát cắt phần cứng chính xác được phân tích ở Mục 1.4 / Chương 6.

**Nhịp 5: Điều Công Thức Giấu**
Phép lấy tổng trên $n \in [0, N-1]$ mặc định rằng tín hiệu lặp lại tuần hoàn với chu kỳ $N$. Hơn nữa, việc đệm thêm 112 số 0 từ $L = 400$ lên $N = 512$ chỉ làm lưới đánh giá phổ dày hơn qua phép nội suy; nó hoàn toàn không làm tăng độ phân giải tần số vật lý của cảm biến âm học---đại lượng bị giới hạn chặt chẽ bởi chiều dài cửa sổ vật lý $L$.

---

## 3. Phổ Công Suất

Các mô hình âm học hạ nguồn không tiếp nhận trực tiếp tọa độ phức. Ta phải chuyển đổi các bin phổ phức thành năng lượng âm học thực.

### Giải Phẫu 5 Nhịp: Phổ Công Suất

**Nhịp 1: Công Thức**
$$P_\ell[k] = |X_\ell[k]|^2 = \text{Re}(X_\ell[k])^2 + \text{Im}(X_\ell[k])^2, \qquad k = 0, 1, \dots, \frac{N}{2}$$

**Nhịp 2: Ký Hiệu**
- $P_\ell[k] \in \mathbb{R}_{\ge 0}$: mật độ phổ công suất tại khung $\ell$ và bin tần số $k$, biểu diễn năng lượng thực trên $257$ bin tần số.
- $\text{Re}(X_\ell[k]), \text{Im}(X_\ell[k])$: điểm số chiếu đồng pha và vuông pha từ STFT.

**Nhịp 3: Ý Nghĩa Vật Lý**
Mô hình nhận dạng giọng nói cần sự phân bổ năng lượng âm học theo tần số thay vì góc pha xuất hiện. Bình phương độ lớn số phức loại bỏ hoàn toàn góc pha trong khi chuyển đổi $257$ tọa độ phức thành $257$ giá trị năng lượng thực không âm phản ánh cấu trúc formant ngữ âm.

**Nhịp 4: Giá Phần Cứng**
Tiêu tốn 2 phép bình phương và 1 phép cộng cho mỗi bin trên $257$ bin trong mỗi khung $10\text{ ms}$. Tính công suất ($|X|^2$) thay vì biên độ ($|X|$) triệt tiêu hoàn toàn khối logic tính căn bậc hai phần cứng đắt đỏ. Số lát cắt phần cứng chính xác được phân tích ở Mục 1.4 / Chương 6.

**Nhịp 5: Điều Công Thức Giấu**
Loại bỏ pha là một phép biến đổi một chiều không thể đảo ngược. Dù trích xuất được bao năng lượng formant trong trẻo cho mô hình nhận dạng, việc tái tạo lại dạng sóng âm thanh trong miền thời gian là bất khả thi nếu không có thuật toán ước lượng pha.

---

## 4. Ánh Xạ Tần Số Mel

Các bin tần số tuyến tính đối xử với mọi dải tần với cùng một tầm quan trọng số học. Tuy nhiên, thính giác con người cảm nhận cao độ theo quy luật phi tuyến.

### Giải Phẫu 5 Nhịp: Ánh Xạ Tần Số Mel

**Nhịp 1: Công Thức**
$$\mathrm{mel}(f) = 2595 \log_{10}\!\left(1 + \frac{f}{700}\right)$$

**Nhịp 2: Ký Hiệu**
- $f$: tần số vật lý liên tục tính bằng Hertz ($0 \le f \le 8.000\text{ Hz}$).
- $\mathrm{mel}(f)$: cao độ cảm nhận chủ quan tính bằng đơn vị Mel.

**Nhịp 3: Ý Nghĩa Vật Lý**
Độ phân giải tần số của ốc tai người có tính phi tuyến: cực kỳ nhạy cảm với các biến đổi cao độ nhỏ ở dải tần thấp (formant nguyên âm), nhưng thô ráp dần ở dải tần cao (nhiễu phụ âm xát). Thang đo Mel mô hình hóa sự uốn cong sinh học này: mỗi bước cảm nhận bằng nhau $355\text{ mel}$ (tương ứng $1/8$ toàn dải $2.840\text{ mel}$) chỉ trải $259\text{ Hz}$ ở dải thấp ($0\text{--}259\text{ Hz}$ qua phép nghịch đảo $700 \times (10^{355/2595} - 1)$), nhưng dãn rộng tới $2.351\text{ Hz}$ ở dải cao nhất ($5.649\text{--}8.000\text{ Hz}$ với $\Delta f = 8.000 - 5.649\text{ Hz}$)---dãn nở tới chín lần về băng thông vật lý cho cùng một bước cảm nhận âm học.

**Nhịp 4: Giá Phần Cứng**
Tiêu tốn 0 logic thời gian chạy. Hàm uốn Mel được tính toán ngoại tuyến vào thời điểm thiết kế hệ thống để xác định các tần số tâm và trọng số bộ lọc lưu cố định trong bộ nhớ trên chip.

**Nhịp 5: Điều Công Thức Giấu**
Đường cong toán học liên tục buộc phải ánh xạ lên một lưới bin FFT rời rạc. Ở dải tần thấp, băng thông của các bộ lọc cảm nhận có thể trở nên hẹp hơn khoảng cách giữa hai bin số $\Delta f = 31{,}25\text{ Hz}$ ($16000/512$), tạo ra nguy cơ sai lệch rời rạc hóa bin.

---

## 5. Ngân Hàng Bộ Lọc Mel Là Tổng Có Trọng Số

Để nén các bin tuyến tính thành các kênh cảm nhận, các bộ lọc tam giác tích phân năng lượng qua các dải không đồng đều.

### Giải Phẫu 5 Nhịp: Ngân Hàng Bộ Lọc Mel

**Nhịp 1: Công Thức**
$$E_\ell[m] = \sum_{k=0}^{256} g_m[k] \, P_\ell[k], \qquad m = 0, 1, \dots, M-1$$
với $g_m[k]$ là các hàm trọng số hình tam giác gối chồng:
$$g_m[k] = \begin{cases}
\dfrac{k - k_{m-1}}{k_m - k_{m-1}}, & k_{m-1} \le k \le k_m \\[6pt]
\dfrac{k_{m+1} - k}{k_{m+1} - k_m}, & k_m < k \le k_{m+1} \\[6pt]
0, & \text{khác}
\end{cases}$$

**Nhịp 2: Ký Hiệu**
- $m \in \{0, 1, \dots, M-1\}$: chỉ số dải Mel ($M = 80$).
- $k_m$: chỉ số bin FFT rời rạc của tần số tâm bộ lọc $m$.
- $g_m[k]$: trọng số lọc tam giác cho bin $k$ trong bộ lọc $m$.
- $E_\ell[m]$: vector năng lượng phổ Mel tích hợp (kích thước $[1, 80]$).

**Nhịp 3: Ý Nghĩa Vật Lý**
80 bộ lọc tam giác gối chồng nén $257$ bin công suất tuyến tính thành $80$ kênh năng lượng cảm nhận. Từng bộ lọc tích phân năng lượng trong dải, bảo toàn chi tiết phổ tinh vi ở vùng nguyên âm tần thấp trong khi gom các dải năng lượng rộng ở vùng phụ âm ồn tần cao.

> [!NOTE]
> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ**
>
> Ngân hàng bộ lọc Mel là một cỗ máy tập trung thông tin bất đối xứng. Ở dải tần thấp ($0\text{--}1\text{ kHz}$) nơi cư trú của cao độ và formant nguyên âm cốt lõi, mỗi dải chỉ tích hợp một vài bin FFT, bảo tồn chi tiết họa âm tinh vi. Ở dải tần cao ($6\text{--}8\text{ kHz}$) nơi phụ âm xát tạo ra tiếng ồn khuếch tán, mỗi dải gom hàng chục bin, giữ lại đường bao năng lượng tổng thể trong khi gạt bỏ cấu trúc vi mô không cần thiết.

**Nhịp 4: Giá Phần Cứng**
Phép nhân ma trận thưa với vector trên mỗi khung. Vì mỗi bin FFT tuyến tính $k$ chỉ rơi vào tối đa hai bộ lọc tam giác kề nhau, ma trận chủ yếu chứa các số 0. Phần cứng chỉ tốn các phép nhân - cộng trên các nhịp bin tích cực; số lát cắt phần cứng chính xác được phân tích ở Mục 1.4 / Chương 6.

**Nhịp 5: Điều Công Thức Giấu**
Bẫy rời rạc hóa: Khi tần số tâm liên tục được ánh xạ sang chỉ số bin nguyên, các bộ lọc tần thấp kế cận có thể bị làm tròn về cùng một bin nếu khoảng cách hẹp hơn $\Delta f = 31{,}25\text{ Hz}$ ($16000/512$). Bộ lọc có đỉnh và hai mép sụp về một điểm sẽ có độ rộng bằng 0 và cho ra năng lượng chết. Phần cứng phải bảo đảm mỗi dải phủ ít nhất một bin duy nhất.

---

## 6. Nén Logarit

Phép biến đổi cuối cùng nén các biến thiên năng lượng vật lý rộng lớn vào một không gian đặc trưng chuẩn hóa, phù hợp cho các tầng mạng nơ-ron.

### Giải Phẫu 5 Nhịp: Nén Logarit

**Nhịp 1: Công Thức**
$$S_\ell[m] = \ln\bigl(\max(E_\ell[m], 10^{-6})\bigr), \qquad m = 0, 1, \dots, M-1$$

**Nhịp 2: Ký Hiệu**
- $S_\ell[m]$: vector đặc trưng log-Mel năng lượng (kích thước $[1, 80]$) phát cho mô hình âm học.
- $E_\ell[m]$: năng lượng dải Mel thô từ Phép 5.
- $10^{-6}$: ngưỡng chặn dưới ngăn thảm họa $\ln(0) \to -\infty$ khi gặp khoảng lặng.

**Nhịp 3: Ý Nghĩa Vật Lý**
Cảm nhận độ to của con người tỷ lệ logarit với công suất âm thanh. Trong môi trường thực tế, áp suất âm thanh dao động từ tiếng thì thầm khẽ ($10^{-5}\text{ Pa}$) đến tiếng thét lớn ($10\text{ Pa}$)---chênh lệch năng lượng tới $10^{10}$, tương đương $100\text{ dB}$. Nén logarit điều hòa dải động khổng lồ này về một phân phối số học gọn gàng. Hơn nữa, phép logarit biến các hiệu ứng kênh có tính chất nhân (như khoảng cách micro hay âm học phòng) thành các độ lệch cộng tính đơn giản.

**Nhịp 4: Giá Phần Cứng**
Tiêu tốn 80 phép tính logarit trên mỗi khung $10\text{ ms}$. Trên phần cứng, logarit được đánh giá bằng bảng tra hoặc xấp xỉ đa thức từng đoạn. Số lát cắt phần cứng chính xác được phân tích ở Mục 1.4 / Chương 6.

**Nhịp 5: Điều Công Thức Giấu**
Đạo hàm của logarit tự nhiên, $\frac{d}{dx}\ln(x) = \frac{1}{x}$, phân kỳ về vô hạn khi $x \to 0$. Dù ngưỡng chặn $10^{-6}$ ngăn được âm vô cùng, những dao động nhiễu siêu nhỏ quanh ngưỡng sàn vẫn tạo ra các biến động lớn trong không gian đặc trưng, đòi hỏi xử lý số học cẩn trọng trong quá trình lượng tử hóa dấu phẩy tĩnh.

---

## Thực Tế Silicon: Cầu Nối Sang Mục 1.4

Các dẫn xuất toán học của STFT và ngân hàng bộ lọc Mel trong mục này giả định số học vô hạn độ chính xác, truy xuất bộ nhớ trễ bằng 0 và thực thi tức thời. Trên máy tính phát triển, những phương trình này chạy mượt mà trong môi trường khoa học Python, nơi bộ nhớ dồi dào và phần cứng dấu phẩy động che giấu hạn chót xử lý $10\text{ ms}$ cùng ngân sách nhiệt.

Khi chuỗi toán học này được đẩy xuống silicon biên vật lý vận hành dưới trần công suất ngặt nghèo ($< 15\text{ W}$) với hạn chót cứng $10\text{ ms}$ cho mỗi khung, các công thức trừu tượng va chạm trực diện với các ràng buộc phần cứng vật lý. Liệu một GPU biên hay một cấu trúc không gian FPGA có thể thỏa mãn các hạn chót âm thanh dạng dòng này hay không chính là câu hỏi kiến trúc được khám phá tiếp theo.
