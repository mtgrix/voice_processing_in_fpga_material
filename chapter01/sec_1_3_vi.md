# 1.3 Mô Hình Hóa Toán Học: STFT và Ngân Hàng Bộ Lọc Mel

Mục 1.2 đã xây dựng đường truyền dữ liệu (datapath) vật lý đóng gói áp suất không khí dạng dòng thành các khung rời rạc. Mục 1.3 là chiếc kính hiển vi toán học đặt lên một gói dữ liệu đơn lẻ, suy diễn từng toán tử biến đổi phổ từ hiện tượng giao thoa sóng và cơ chế cảm nhận thính giác.

> **$\blacktriangleright$ MỤC TIÊU HỌC TẬP**
>
> 1. **Tiêu chuẩn phân giải Rayleigh:** Phân tích tích số $\Delta t \cdot \Delta f = 1$ để thấy rõ sự đánh đổi vật lý không thể tránh khỏi giữa độ phân giải thời gian và tần số khi chọn chiều dài khung $\Delta t = 25\text{ ms}$, ấn định độ phân giải tối thiểu $\Delta f = 40\text{ Hz}$.
> 2. **Cơ chế máy thu vuông pha và tính bất biến pha:** Đối chiếu sự sụt giảm biên độ của nhánh cosin ($+105{,}34 \to -19{,}27$) với tính bất biến của tổng Pythagoras ($\approx 11.533$), và lý giải nghịch lý kiến trúc: phần cứng buộc phải dùng hai nhánh dò trực giao chỉ để đo năng lượng rồi vứt bỏ góc pha ở ngay toán tử liền sau.
> 3. **Cấu trúc thực tế 80 dải Mel:** Khảo sát hiện tượng suy biến trên lưới FFT thô ($\Delta f = 31{,}25\text{ Hz}$) với 18 hàng 1-tap (dây nối phần cứng), 1 hàng chết (Bộ lọc 2 luôn phát mức 0), và chứng minh vì sao $E_{15} = P_{14}$ là một hằng đẳng thức cấu trúc trên mọi phổ chứ không phụ thuộc vào âm 440 Hz.

---

## 0. Bản Hợp Đồng của Khung Âm Thanh: Năm Tham Số Tự Nhiên

Đường ống tiền xử lý âm thanh trong hệ thống không tự ý chọn các con số ngẫu nhiên. Mọi tham số đều bị trói chặt bởi các ràng buộc âm học và phần cứng:

| Tham số | Ký hiệu | Giá trị thực | Cơ sở vật lý & Ràng buộc phần cứng | Phương án bị bác bỏ |
| :--- | :---: | :---: | :--- | :--- |
| **Tần số lấy mẫu** | $f_s$ | $16.000\text{ Hz}$ | Định lý Nyquist ($f_{\max} = 8\text{ kHz}$) bao trọn dải tần tiếng nói con người ($300\text{--}3.400\text{ Hz}$). | $8\text{ kHz}$ (mất âm xát cao tần); $44{,}1\text{ kHz}$ (lãng phí $2{,}76\times$ băng thông DSP). |
| **Chiều dài khung** | $L$ | $400\text{ mẫu}$ ($25\text{ ms}$) | Khoảng thời gian âm học tiếng nói được coi là tĩnh dừng (quasi-stationary). | $10\text{ ms}$ (búp tần số quá bè, mất formant); $100\text{ ms}$ (nhòe phụ âm ngắn). |
| **Bước nhảy** | $H$ | $160\text{ mẫu}$ ($10\text{ ms}$) | Hạn chót lan truyền dòng $10\text{ ms}$; gối đầu $60\%$ bù đắp suy hao năng lượng ở hai biên cửa sổ. | $25\text{ ms}$ (không gối đầu, bỏ sót biến cố âm học); $1\text{ ms}$ (quá tải tính toán $10\times$). |
| **Kích thước FFT** | $N$ | $512\text{ điểm}$ | Lũy thừa của 2 ($2^9$) cho thuật toán FFT Cooley-Tukey; đệm 112 số 0 sau 400 mẫu vật lý. | $400$ điểm (phần cứng không thể chạy FFT cơ số 2 đơn giản, buộc dùng DFT chậm). |
| **Số dải Mel** | $M$ | $80\text{ dải}$ | Chuẩn nén sinh học mô phỏng ốc tai người, giảm số chiều từ 257 bin FFT xuống 80 giá trị. | $20\text{ dải}$ (quá thô cho nhận dạng giọng nói); $257\text{ bin}$ (quá nặng cho mô hình âm học). |

### Phép Tính Bất Định Theo Chuẩn Phân Giải Rayleigh

Một tín hiệu không thể đồng thời có thời lượng vô cùng ngắn và độ rộng dải tần vô cùng hẹp. Với chiều dài khung $L = 400$ mẫu tại $f_s = 16.000\text{ Hz}$, độ mở thời gian là:

$$\Delta t = \frac{L}{f_s} = \frac{400}{16.000} = 0{,}025\text{ s} = 25\text{ ms}$$

Theo tiêu chuẩn phân giải Rayleigh, khoảng cách tần số tối thiểu để phân biệt hai vạch phổ là nghịch đảo của chiều dài khung thời gian:

$$\Delta f = \frac{1}{\Delta t} = \frac{1}{0{,}025\text{ s}} = 40\text{ Hz}$$

Tích số thời gian - tần số bằng đúng đơn vị:

$$\Delta t \cdot \Delta f = 0{,}025\text{ s} \times 40\text{ Hz} = 1{,}00$$

Đẳng thức $\Delta t \cdot \Delta f = 1$ đúng vì $\Delta f$ được định nghĩa bằng $1/\Delta t$ theo chuẩn phân giải Rayleigh. Khi chuyển sang lưới FFT $N = 512$ điểm, bước nhảy bin là $\Delta f_{\text{bin}} = 16.000 / 512 = 31{,}25\text{ Hz}$. Bước nhảy bin $31{,}25\text{ Hz}$ này mịn hơn bề rộng phân giải vật lý $40\text{ Hz}$ của khung; việc đệm thêm 112 số không chỉ lấy mẫu dày hơn trên đường cong liên tục chứ hoàn toàn không làm thay đổi giới hạn phân giải $40\text{ Hz}$ do chiều dài $L = 400$ ấn định.

---

## 1. Cửa Sổ Hamming (Hamming Window)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Sau khi Mục 1.2 cắt dòng âm thanh liên tục thành từng khung $L = 400$ mẫu, hai mép ranh giới của khung bị cắt đứt đột ngột. Làm sao để phân tích phổ mà không sinh ra các họa âm giả mạo do các bước nhảy biên nhân tạo này tạo ra?

**2. Phương pháp thô sơ bị bác bỏ: Cửa sổ chữ nhật và thảm họa rò rỉ phổ.** Nếu lấy trực tiếp 400 mẫu mà không làm mượt (nhân với cửa sổ chữ nhật $w[n]=1$), tín hiệu bị nhân với một xung vuông trong miền thời gian, tương ứng với phép cuộn với hàm $\text{sinc}$ trong miền tần số. Điểm triệt tiêu đầu tiên (first null) của cửa sổ chữ nhật nằm tại $f_s/L = 16.000 / 400 = 40\text{ Hz}$, tạo ra bề rộng null-to-null là:

$$\Delta f_{\text{null, rect}} = 2 \times \frac{f_s}{L} = 2 \times 40\text{ Hz} = 80\text{ Hz}$$

Búp phụ đầu tiên nhô cao tới $-13{,}26\text{ dB}$ tại tần số lệch $57{,}13\text{ Hz}$. Năng lượng từ các tần số trầm cực mạnh sẽ rò rỉ sang các dải lân cận, làm lu mờ hoàn toàn các formant âm thanh tinh tế ở dải cao.

**3. Công thức hiển thị:** Hệ thống sử dụng cửa sổ Hamming đối xứng bậc $L = 400$:

$$w[n] = 0{,}54 - 0{,}46 \cos\left(\frac{2\pi n}{L - 1}\right), \qquad n = 0, 1, \dots, L - 1$$

Điểm triệt tiêu đầu tiên của cửa sổ Hamming dời ra tần số $2f_s/L = 80\text{ Hz}$, thiết lập bề rộng null-to-null:

$$\Delta f_{\text{null, ham}} = 4 \times \frac{f_s}{L} = 4 \times 40\text{ Hz} = 160\text{ Hz}$$

Búp phụ đầu tiên của Hamming nằm tại tần số lệch $88{,}87\text{ Hz}$ với mức suy giảm đạt $\mathbf{-44{,}45\text{ dB}}$. Một biến đổi FFT $N=512$ điểm với bước bin $31{,}25\text{ Hz}$ là quá thô để phát hiện chính xác tọa độ búp phụ này; do đó phòng thí nghiệm sử dụng lưới đệm dài $65.536$ điểm độc lập để giải tích đặc tính cửa sổ.

> **$\blacktriangleright$ NHÌN THẤY VẬT LÝ**
>
> Áp cửa sổ là một thỏa hiệp bắt buộc: ta chấp nhận trả giá bằng việc nới rộng búp chính gấp đôi (từ bề rộng null-to-null $80\text{ Hz}$ lên $160\text{ Hz}$) để đổi lấy búp phụ đầu tiên rơi sâu từ $-13{,}26\text{ dB}$ xuống $-44{,}45\text{ dB}$ (tăng thêm $31{,}19\text{ dB}$ suy hao búp phụ). Năng lượng rò rỉ giả mạo bị ghìm chặt dưới sàn, bảo vệ toàn bộ các formant cao tần.

**4. Cái giá phần cứng và điều bị phá hủy:** Tiêu tốn đúng 400 phép nhân số thực trên mỗi khung $10\text{ ms}$ (tương ứng $40.000\text{ phép nhân/s}$). Hệ số đối xứng được lưu trong bảng tra ROM trên chip. *Điều bị phá hủy:* Biên độ ở hai đầu mút khung bị triệt tiêu về $w[0] = w[399] = 0{,}08$. Để bù đắp điểm mù này, hệ thống bắt buộc phải gối đầu khung sâu $60\%$ ($H = 160$ mẫu, tái sử dụng 240 mẫu với khung trước).

---

## 2. Thẩm Tra Sóng Bằng Hai Sóng Dò Vuông Pha (Quadrature Probe Waves)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Khung âm thanh $x_\ell[n]$ sau cửa sổ là một chuỗi 400 con số thực. Làm sao kiểm tra xem trong chuỗi này có tồn tại dao động ở một tần số cụ thể $f_k$ hay không?

**2. Sóng dò đơn lẻ và hiện tượng mù pha (Phase Blindness):** Phương pháp trực giác là nhân tín hiệu với một sóng dò chuẩn $\cos\left(\frac{2\pi k n}{N}\right)$ rồi cộng dồn lại:

$$\text{Tích lũy} = \sum_{n=0}^{N-1} x[n] \cos\left(\frac{2\pi k n}{N}\right)$$

Về mặt giải tích lý tưởng, nếu tín hiệu đến bị trễ một phần tư chu kỳ ($\pi/2$, tức là sóng $\sin$), tích phân của $\sin(\omega t) \cos(\omega t)$ trên các chu kỳ nguyên vẹn triệt tiêu hoàn toàn về 0:

$$\int_0^T \sin(\omega t) \cos(\omega t) \, dt = 0$$

Để kiểm chứng trên phần cứng, phòng thí nghiệm sử dụng tín hiệu kiểm chuẩn đơn tần tổng hợp `datasets/sample_tone440.wav` (các file sóng âm tiếng nói thực được phân tích riêng ở Mục 7). Sóng dò được đặt tại bin 14 ($437{,}5\text{ Hz}$), lệch $2{,}5\text{ Hz}$ so với tần số sóng $440\text{ Hz}$, và khung được áp cửa sổ Hamming. Khi dịch tín hiệu đi 9 mẫu (tương đương $\approx 1/4$ chu kỳ sóng $440\text{ Hz}$ tại $f_s = 16.000\text{ Hz}$):

- **Khung gốc (dịch 0 mẫu):** $\text{Cos}_0 = +105{,}3388, \quad \text{Sin}_0 = +20{,}8916 \implies |X_0|^2 = 11.532{,}71$.
- **Khung dịch 9 mẫu ($\approx 90^\circ$):** $\text{Cos}_9 = -19{,}2665, \quad \text{Sin}_9 = +105{,}7369 \implies |X_9|^2 = 11.551{,}50$.

Số đo thực tế không về số 0 tuyệt đối: nhánh cosin rơi từ $+105{,}34$ xuống $-19{,}27$. Tỷ số biên độ sau dịch chuyển là $0{,}1829$ (suy giảm $81{,}71\%$), và tỷ số năng lượng nhánh cosin rơi xuống $0{,}0335$ (mất tới $96{,}65\%$ năng lượng nhánh). Phần dư $-19{,}27$ chính là rò rỉ phổ do độ lệch $2{,}5\text{ Hz}$ và việc cửa sổ không chứa số nguyên chu kỳ. Nhánh sin vuông pha vọt lên $+105{,}74$, bù đắp hoàn hảo để tổng công suất $|X|^2$ duy trì ổn định với độ lệch tương đối chỉ $0{,}001629$ ($0{,}16\%$).

> **$\bigstar$ PHÁT HIỆN THEN CHỐT**
>
> Một bin phổ phức $X[k]$ là một máy thu vuông pha phần cứng: nhánh $\cos$ đo phần thực $\text{Re}$, nhánh $-\sin$ đo phần ảo $\text{Im}$. Năng lượng tín hiệu $|X[k]|^2 = \text{Re}^2 + \text{Im}^2$ hoàn toàn không phụ thuộc vào thời điểm sóng âm ập đến micro.

**Nghịch lý kiến trúc:** Để đo đúng năng lượng sóng mà không bị mù pha, phần cứng bắt buộc phải nhân đôi tài nguyên (2 bộ nhân, 2 bộ tích lũy, 2 dòng dữ liệu thực/ảo). Thế nhưng, ngay ở toán tử tiếp theo, hệ thống tính $|X|^2 = \text{Re}^2 + \text{Im}^2$ và **thản nhiên vứt bỏ hoàn toàn góc pha đi mãi mãi**! Sự vứt bỏ này xuất phát từ bản chất âm học: não bộ và mạng nơ-ron nhận dạng nguyên âm dựa trên vị trí các đỉnh formant chứ không dựa vào pha sóng đến micro.

---

## 3. Biến Đổi Fourier Thời Gian Ngắn (STFT)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Máy thu vuông pha ở Mục 2 mới chỉ kiểm tra một tần số đơn lẻ $k$. Làm sao quét đồng thời toàn bộ dải phổ âm thanh từ $0$ đến $8.000\text{ Hz}$?

**2. Dự đoán bin đỉnh trước công thức:** Lưới tần số STFT với $N = 512$ điểm ở $f_s = 16.000\text{ Hz}$ có bước nhảy bin:

$$\Delta f = \frac{f_s}{N} = \frac{16.000}{512} = 31{,}25\text{ Hz}$$

Âm thanh đơn tần $440\text{ Hz}$ rơi vào chỉ số phân đoạn:

$$k = \frac{440}{31{,}25} = 14{,}08$$

Vì $14{,}08$ nằm gần số nguyên 14 nhất ($14 \times 31{,}25 = 437{,}5\text{ Hz}$ so với bin 15 là $468{,}75\text{ Hz}$), người học có thể **dự đoán chắc chắn bin đỉnh công suất phải là bin 14**. Kết quả thực nghiệm từ `chapter01/lab_1_3.py` xác nhận: `argmax bin: 14 (437.5 Hz)`.

**3. Công thức hiển thị:**

$$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n] e^{-j \frac{2\pi k n}{N}}, \qquad k = 0, 1, \dots, N-1$$

Do tính đối xứng liên hợp của tín hiệu thực ($X_\ell[N - k] = X_\ell^*[k]$), phần cứng chỉ cần giữ lại $N/2 + 1 = 257$ bin đầu tiên ($0\text{--}8.000\text{ Hz}$) là bảo toàn toàn bộ năng lượng phổ.

**4. Cái giá phần cứng và điều bị phá hủy:**

- **DFT trực tiếp:** Để tính đủ $N = 512$ bin, mỗi bin cần $N$ tích phức:

  $$N^2 = 512^2 = 262.144\text{ phép nhân phức mỗi khung } 10\text{ ms}$$

- **FFT cơ số 2 (Cooley-Tukey):** Tái sử dụng các hệ số quay tuần hoàn, giảm khối lượng xuống:

  $$\frac{N}{2} \log_2 N = \frac{512}{2} \times 9 = 2.304\text{ bướm tính toán (butterflies) mỗi khung}$$

Cần nhấn mạnh: **một bướm tính toán không phải là một phép nhân phức đơn lẻ**. Một bướm radix-2 bao gồm một phép nhân phức với hệ số quay $W_N^k$ và hai phép cộng/trừ phức. Tỷ số giảm tải hơn 100 lần giữa 262.144 và 2.304 chính là lý do các kiến trúc phần cứng chuyên dụng bắt buộc phải triển khai FFT thay vì ma trận DFT nhân thẳng.

*Bản chất của đệm số không (Zero-padding):* Việc thêm 112 số không vào sau 400 mẫu khung không tạo thêm thông tin vật lý mới. Nó chỉ làm lưới nội suy phổ dày hơn (chia từ bước $40\text{ Hz}$ của khung 400 điểm thành bước $31{,}25\text{ Hz}$ của lưới 512 điểm). Búp chính của tín hiệu vẫn giữ nguyên độ rộng vật lý do $L = 400$ ấn định.

---

## 4. Toán Tử Công Suất (Power Spectrum Operator)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Đầu ra của STFT là một mảng 257 số phức $X_\ell[k] = \text{Re} + j\text{Im}$. Làm sao biến đổi mảng này thành mật độ năng lượng thực để đưa vào các tầng nhận diện tiếp theo?

**2. Cơ chế vật lý: Vứt bỏ góc pha và bảo tồn biên độ Pythagoras.** Phổ công suất tính bình phương biên độ của từng số phức:

$$P_\ell[k] = |X_\ell[k]|^2 = \text{Re}(X_\ell[k])^2 + \text{Im}(X_\ell[k])^2$$

Góc pha $\theta = \arctan(\text{Im}/\text{Re})$ chính thức bị triệt tiêu hoàn toàn. Năng lượng âm học được nén từ 2 dòng dữ liệu thực/ảo thành một dòng số thực không âm duy nhất.

**3. Công thức hiển thị:**

$$P_\ell[k] = X_{\text{re}}^2[\ell, k] + X_{\text{im}}^2[\ell, k], \qquad k = 0, 1, \dots, 256$$

**4. Cái giá phần cứng và điều bị phá hủy:** Trên mỗi khung $10\text{ ms}$, với 257 bin tần số, toán tử đòi hỏi chính xác:

$$257 \times 2 = 514\text{ phép bình phương và } 257 \times 1 = 257\text{ phép cộng, cộng lại } \mathbf{771\text{ phép tính thực}}$$

Đây là thao tác cực kỳ nhẹ, hoàn toàn song song hóa trên FPGA. *Điều bị phá hủy:* Mất vĩnh viễn thông tin pha. Không thể tái tạo lại dạng sóng âm thanh gốc từ $P_\ell[k]$ nếu không dùng các giải thuật ước lượng pha lặp hoặc mô hình mạng nơ-ron sinh âm (vocoder).

---

## 5. Ngân Hàng Bộ Lọc Mel (Mel Filterbank)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Tai người không cảm nhận tần số theo thang tuyến tính Hertz. Một khoảng cách $100\text{ Hz}$ ở dải trầm ($200\text{--}300\text{ Hz}$) tạo ra sự khác biệt cao độ rất lớn, nhưng ở dải cao ($5.000\text{--}5.100\text{ Hz}$) tai người hầu như không phân biệt được. Làm sao nén 257 bin tuyến tính thành một vector cảm nhận sinh học?

**2. Cấu trúc thực tế 80 dải Mel và phân loại hàng:** Hàm `create_mel_filterbank` ánh xạ dải $0\text{--}8.000\text{ Hz}$ sang thang Mel với mảng ranh giới 82 điểm:

$$\text{bin\_points} = \left\lfloor \frac{(N + 1) \cdot f_{\text{mel}}}{f_s} \right\rfloor$$

Khi khảo sát từng hàng trong ma trận trọng số $80 \times 257$, phòng thí nghiệm phân loại chính xác:

- **1 hàng chết (Dead row):** Bộ lọc $m = 2$ có ranh giới $[1, 2, 2]$. Đỉnh tâm và mép phải trùng nhau tại bin 2, khiến toàn bộ trọng số trên hàng này bằng đúng 0 (giá trị cực đại $= 0{,}0000$). Kênh Mel này luôn phát ra mức năng lượng 0 trên mọi phổ.
- **18 hàng 1-tap (Dây nối phần cứng):** Có đúng 1 trọng số khác 0 và trọng số đó bằng $1{,}00$ (gồm các bộ lọc $m \in \{0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 22\}$).
- **61 hàng đa bin:** Các bộ lọc dải cao có từ 2 trọng số khác 0 trở lên.

Đặc biệt, Bộ lọc 15 có ranh giới $[13, 14, 15]$. Vì các bin $k$ là số nguyên rời rạc, bên trong đoạn $[13, 15]$ chỉ tồn tại duy nhất một điểm nguyên là $k=14$. Tại hai mép $k=13$ và $k=15$, trọng số tam giác bằng 0. Do đó, đẳng thức:

$$E_{15} = P_{14}$$

**đúng trên mọi phổ âm thanh**, không phải do âm 440 Hz rơi trúng đỉnh. Về mặt phần cứng, một hàng 1-tap là một dây nối thuần túy (không tốn bộ nhân hay bộ cộng); một hàng chết luôn bằng 0; chỉ có 61 hàng còn lại mới đòi hỏi các phép nhân-cộng thực sự.

---

## 6. Nén Logarit (Logarithmic Compression)

**1. Câu hỏi giai đoạn trước không thể trả lời:** Năng lượng $E_\ell[m]$ giữa các dải Mel có thể chênh lệch nhau hàng triệu lần. Nếu đưa thẳng vào mạng nơ-ron, dải âm lượng lớn nhất sẽ chi phối hoàn toàn hàm mất mát và gradient.

**2. Phương pháp thô sơ và độ to cảm nhận:** Độ to mà con người cảm nhận tỷ lệ thuận với logarit của năng lượng âm thanh vật lý (Định luật Weber-Fechner). Hơn nữa, sự thay đổi khoảng cách micro hoặc độ lợi khuếch đại (gain) $g$ sẽ nhân toàn bộ năng lượng âm thanh với hệ số $g^2$. Khi đi qua hàm logarit:

$$\ln(g^2 \cdot E) = \ln(E) + 2\ln(g)$$

Độ lợi micro có tính chất nhân bị biến đổi thành một **độ lệch cộng tính cố định** $2\ln(g)$ trên toàn bộ các khung. Đây chính là nền tảng đại số giúp các kỹ thuật chuẩn hóa đặc trưng tiếng nói loại bỏ ảnh hưởng của độ nhạy micro.

Ba giá trị đo thực nghiệm từ phòng thí nghiệm Lab 1.3:
- **Năng lượng lớn (dải 15 từ âm 440 Hz):** $E = 11.532{,}71 \implies \ln(11.532{,}71) = \mathbf{9{,}3529}$.
- **Năng lượng đơn vị:** $E = 1{,}0 \implies \ln(1{,}0) = \mathbf{0{,}0000}$.
- **Năng lượng cực tiểu dưới ngưỡng sàn ($10^{-8} < 10^{-6}$):** Bị kẹp sàn tại $10^{-6} \implies \ln(10^{-6}) = \mathbf{-13{,}8155}$.

**3. Công thức hiển thị:**

$$S_\ell[m] = \ln(\max(E_\ell[m], 10^{-6})), \qquad m = 0, 1, \dots, M-1$$

**4. Cái giá phần cứng và điều bị phá hủy:** Tiêu tốn đúng **80 phép tính logarit tự nhiên trên mỗi khung 10 ms**. Trên phần cứng FPGA, hàm logarit được xấp xỉ bằng bảng tra kết hợp đa thức bậc một từng đoạn. *Điều bị phá hủy:* Đạo hàm $\frac{d}{dx} \ln(x) = \frac{1}{x}$ tiến tới vô hạn khi $x \to 0$. Ngưỡng chặn sàn $10^{-6}$ ngăn chặn lỗi số học $-\infty$ khi gặp khoảng lặng, nhưng đồng thời cũng san phẳng mọi biến thiên âm học vi mô nằm dưới mức năng lượng $10^{-6}$.

---

## 7. Bảng Sổ Cái Kỹ Thuật (Pipeline Ledger)

Bảng sổ cái dưới đây tổng hợp trọn vẹn năm giai đoạn toán tử được đo đạc và xác thực trực tiếp từ mã nguồn phòng thí nghiệm `chapter01/lab_1_3.py`:

| Toán tử | Câu hỏi vật lý được trả lời | Kích thước vào $\to$ ra | Khối lượng số học / 10 ms | Điều bị phá hủy |
| :--- | :--- | :---: | :--- | :--- |
| **1. Cửa sổ** | Cắt hữu hạn mà không sinh rò rỉ phổ rác? | $[400] \to [512]$ (đệm 112 số 0) | 400 phép nhân thực | Biên khung bị đè về 0,08; buộc phải gối 60\%. |
| **2. STFT** | Nhận diện tần số cộng hưởng không mù pha? | $[512] \to [257]$ số phức | 2.304 bướm FFT radix-2 (262.144 tích ở DFT thẳng) | Giả định tuần hoàn; độ phân giải chặn bởi $L = 400$. |
| **3. Công suất** | Trích xuất năng lượng âm học bỏ qua góc pha? | $[257] \to [257]$ số thực | 514 phép bình phương và 257 phép cộng, cộng lại 771 phép tính thực | Mất vĩnh viễn góc pha; không thể nghe lại dạng sóng. |
| **4. Mel** | Uốn phổ theo tai người và giảm chiều mô hình? | $[257] \to [80]$ dải | Nhân ma trận thưa (18 hàng 1-tap, 1 hàng chết, 61 hàng đa bin) | Phổ dải cao bị nung chảy; Bộ lọc 2 bị chết. |
| **5. Log** | Nén dải động và biến độ lợi micro thành độ lệch? | $[80] \to [80]$ log-Mel | 80 phép tính logarit tự nhiên (bảng tra đa thức) | Mất chi tiết dưới sàn $10^{-6}$; độ dốc phân kỳ gần 0. |

---

## 8. Ba Câu Hỏi Tự Đánh Giá Năng Lực Sư Phạm

Để bảo đảm người học không chỉ ghi nhớ công thức thụ động mà thấu suốt cơ chế vật lý bên dưới, hãy tự trả lời ba câu hỏi phản biện kiến trúc sau đây:

1. **Về định vị bin và đệm số không:** Một âm thanh đơn tần $1.000\text{ Hz}$ được lấy mẫu ở $16.000\text{ Hz}$ và đưa vào khung STFT $N = 512$ điểm. Tín hiệu này sẽ rơi vào chính xác bin tần số số mấy? Việc đệm thêm 112 số không vào sau 400 mẫu của khung có làm cho búp đỉnh nhọn hơn và sắc nét hơn về mặt vật lý hay không?

   *Trả lời:* Bước nhảy mỗi bin là $\Delta f = 16.000 / 512 = 31{,}25\text{ Hz}$. Chỉ số bin là $k = 1.000 / 31{,}25 = 32$. Tín hiệu rơi chính xác vào **bin 32**. Việc đệm 112 số không **hoàn toàn không làm thu hẹp búp đỉnh vật lý**; nó chỉ lấy mẫu dày hơn trên đường cong DTFT vốn có độ rộng búp chính bị khóa chặt bởi chiều dài cửa sổ vật lý $L = 400$ mẫu ($\Delta t = 25\text{ ms}$).

2. **Về hiện tượng mù pha và sự vứt bỏ góc pha:** Tại sao một sóng dò $\cos$ đơn lẻ lại sụt giảm mạnh biên độ khi gặp một sóng bị lệch pha? Nếu hai sóng dò trực giao ($\cos$ và $-\sin$) là bắt buộc để đo đúng năng lượng sóng, tại sao ở toán tử liền sau chúng ta lại thản nhiên vứt bỏ góc pha đi?

   *Trả lời:* Sóng lệch pha $90^\circ$ làm triệt tiêu phần lớn năng lượng trên sóng dò cosin (biên độ sụt giảm $81{,}71\%$, năng lượng nhánh cosin mất $96{,}65\%$). Cần hai nhánh trực giao để theo định lý Pythagoras tính được biên độ $A = \sqrt{\text{Re}^2 + \text{Im}^2}$ bất biến trước thời điểm xuất hiện của sóng. Sau khi biên độ đã được bảo toàn trong công suất thực $P[k] = \text{Re}^2 + \text{Im}^2$, góc pha âm học không còn mang thông tin nhận dạng ngữ âm (não bộ và mạng nơ-ron nhận diện nguyên âm dựa trên vị trí đỉnh formant chứ không dựa vào pha sóng đến micro), nên việc loại bỏ pha giúp giải phóng bộ nhớ và giảm độ phức tạp cho mô hình hạ nguồn.

3. **Về cấu trúc ma trận Mel:** Hãy giải thích vì sao Bộ lọc 15 chỉ có đúng một trọng số khác 0 và tính chất $E_{15} = P_{14}$ có phụ thuộc vào việc âm thanh thử nghiệm là sóng 440 Hz hay không.

   *Trả lời:* Bộ lọc 15 có ranh giới bin $[13, 14, 15]$. Vì chỉ số bin $k$ là các số nguyên rời rạc, giữa bin 13 và bin 15 chỉ tồn tại duy nhất một bin nguyên bên trong là $k = 14$. Tại hai mép ranh giới $k=13$ và $k=15$, trọng số tam giác suy biến về 0. Do đó, hàng thứ 15 của ma trận chỉ có đúng một trọng số khác không: $g_{15}[14] = 1{,}00$. Tính chất $E_{15} = P_{14}$ là một **hằng đẳng thức cấu trúc đúng trên mọi phổ âm thanh**, biến kênh Mel này thành một dây nối trực tiếp không tiêu tốn bộ nhân DSP.

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

Các kết quả then chốt từ tệp nhật ký thực nghiệm `results/lab13/20261005T154553Z/stdout.log` khớp tuyệt đối từng chữ số với các hình minh họa:

1. **Khớp Hình 1.3_window & Mục 1:**  
   `rect: null = 40.04 Hz, sidelobe = 57.13 Hz (-13.26 dB); ham: null = 80.32 Hz, sidelobe = 88.87 Hz (-44.45 dB)`
2. **Khớp Hình 1.3_probe & Mục 2:**  
   `c0 = +105.3388, s0 = +20.8916; c9 = -19.2665, s9 = +105.7369; mag ratio = 0.1829, rel change = 0.001629`
3. **Khớp Hình 1.3_grid, Mục 3 & Mục 4:**  
   `argmax bin: 14 (437.5 Hz), Power = 11532.71; power ops: 514 squares + 257 adds = 771 ops`
4. **Khớp Hình 1.3b & Mục 5:**  
   `dead count: 1 ([2]), one-tap count: 18, multi-bin count: 61; filter 15 nonzero: bin 14 (weight 1.0000)`
5. **Khớp Hình 1.3_speech & Mục 7:**  
   `speech a: peak frame 66, top 3: Band 13 (3.26), Band 14 (3.15), Band 10 (2.16)`
