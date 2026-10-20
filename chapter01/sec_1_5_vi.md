# 1.5 Các chế độ lỗi chẩn đoán: Thử nghiệm ứng suất tại ranh giới silicon và âm học

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì coi chồng thông số 16 kHz / 25 ms / N=512 / Mel dày đặc là những quy ước bất khả xâm phạm, mục này sẽ bẻ gãy từng nút vặn cấu hình để chỉ ra chính xác nơi mà các định luật vật lý tiếng nói và silicon vi kiến trúc từ chối tuân theo.

---

### Cầu nối tự nhiên từ Mục 1.4: Thử thách giới hạn vật lý tại ranh giới phần cứng

Trong Mục 1.4, chúng ta đã chứng minh rằng tầng tiền xử lý DSP dòng ánh xạ gọn gàng lên tài nguyên silicon vật lý: bộ đệm vòng miền thời gian chiếm đúng $1.600\text{ byte}$ ($34{,}7\%$ một khối BRAM), và ma trận trọng số bộ lọc Mel không nén chiếm $82.240\text{ byte}$ ($18\text{ khối BRAM}$). Tổng cộng hai cấu trúc trạng thái này chỉ tiêu tốn khoảng $12{,}6\%$ dung lượng Block RAM trên chip, cho phép toàn bộ chuỗi tính toán vận hành hoàn toàn khép kín trong bộ nhớ SRAM nội bộ. Nhờ sự cô lập phần cứng độc quyền này, hệ thống triệt tiêu hoàn toàn sự rung pha độ trễ và luôn đáp ứng hạn chót thời gian thực $10\text{ ms}$ của mỗi bước nhảy.

Tuy nhiên, một thuật toán vận hành êm ả dưới các tham số danh định thường che giấu những ranh giới gãy đổ toán học và vật lý rất sắc nhọn. Khi một kỹ sư hệ thống cố tình tối ưu hóa hiệu năng bằng cách xoay các nút vặn kiến trúc—chẳng hạn như tăng gấp ba tần số lấy mẫu để tìm kiếm độ trung thực cao hơn, cắt ngắn độ dài cửa sổ để ép giảm độ trễ, bỏ qua phần đệm số không để giảm số điểm FFT, hay lưu trữ ma trận lọc ở dạng dấu phẩy động dày đặc—các quy luật vật lý về truyền sóng âm và vi kiến trúc silicon không gian sẽ lập tức phản kháng dữ dội. Bốn kịch bản chẩn đoán dưới đây mổ xẻ chi tiết các điều kiện biên đó.

---

### Kịch bản chẩn đoán 1: Ảo ảnh tần số lấy mẫu 48 kHz

#### Giả thuyết ngây thơ
Một kỹ sư hệ thống đề xuất nâng cấp tầng thu nhận âm thanh từ chuẩn $f_s = 16\text{ kHz}$ lên chuẩn phòng thu chuyên nghiệp $f_s = 48\text{ kHz}$. Lý do kỹ thuật được đưa ra là việc tăng gấp ba tốc độ lấy mẫu theo thời gian sẽ thu giữ được các sắc thái âm thanh tần số cao tinh tế hơn, ức chế nhiễu lượng tử hóa và tăng độ chính xác nhận dạng từ khóa, trong khi vẫn duy trì độ dài khung cửa sổ ở mức $25\text{ ms}$ và nhịp bước ở mức $10\text{ ms}$.

#### Phép tính toán học
1. **Số lượng mẫu mỗi khung ($L_{48}$) và nhịp bước ($H_{48}$):**  
   Ở tần số $f_s = 48\text{ kHz}$, chu kỳ lấy mẫu co lại còn $T_s = 1 / 48.000\text{ s} \approx 20{,}833\ \mu\text{s}$. Để giữ nguyên độ dài thời gian vật lý của khung là $25\text{ ms}$ và nhịp bước định kỳ $10\text{ ms}$, số lượng mẫu bắt buộc phải tăng tỷ lệ thuận:
   $$\begin{aligned}
   L_{48} &= 48.000\text{ mẫu/giây} \times 0{,}025\text{ s} = 1.200\text{ mẫu} \\
   H_{48} &= 48.000\text{ mẫu/giây} \times 0{,}010\text{ s} = 480\text{ mẫu}
   \end{aligned}$$
   Cả hai đại lượng đều tăng vọt gấp đúng ba lần so với mốc danh định $16\text{ kHz}$ ($L = 400\text{ mẫu}$, $H = 160\text{ mẫu}$).

2. **Dấu chân bộ nhớ trên chip:**  
   Nếu biểu diễn bằng định dạng dấu phẩy động 32-bit (FP32, $4\text{ byte/mẫu}$), việc lưu trữ khung âm thanh $1.200\text{ mẫu}$ trong bộ đệm vòng đòi hỏi:
   $$\text{Dung lượng đệm}_{48} = 1.200 \times 4\text{ B} = 4.800\text{ byte}$$
   Một khối Block RAM $36\text{-kbit}$ vật lý (RAMB36E2) trên chip AMD XCK26 cung cấp tối đa $36.864\text{ bit} = 4.608\text{ byte}$ dung lượng. Vì $4.800\text{ byte} > 4.608\text{ byte}$, bộ đệm vòng bị tràn khỏi ranh giới của một khối BRAM đơn lẻ. Trình tổng hợp buộc phải cấp phát **hai khối Block RAM $36\text{-kbit}$ riêng biệt**, làm tăng gấp đôi diện tích silicon cho bộ nhớ miền thời gian.

#### Vì sao vật lý và silicon từ chối
Theo định lý lấy mẫu Nyquist–Shannon, tần số $f_s = 48\text{ kHz}$ mở rộng dải thông âm học lên tới $f_{\text{max}} = f_s / 2 = 24\text{ kHz}$. Tuy nhiên, toàn bộ các cộng hưởng thanh đạo tạo nên tiếng nói con người—tần số cơ bản ($F_0 \approx 85\text{--}255\text{ Hz}$), các formant nguyên âm ($F_1\text{--}F_4$ trải dài từ $250\text{--}4.500\text{ Hz}$), cho đến các âm xát phụ âm (sibilant fricatives như $/s/, /\int/$ đạt đỉnh ở $4.000\text{--}7.500\text{ Hz}$)—đều nằm hoàn toàn dưới $8\text{ kHz}$.

Quãng tần số mở rộng từ $8\text{--}24\text{ kHz}$ không hề chứa bất kỳ thông tin ngữ âm nào; nó chỉ thu nhận thêm tiếng xì nhiệt môi trường (thermal hiss), nhiễu đóng ngắt mạch điện tử và các tạp âm siêu âm vô nghĩa. Hơn nữa, việc xử lý $1.200\text{ mẫu}$ buộc biến đổi FFT phía sau phải mở rộng lên ít nhất $N = 2.048\text{ điểm}$, làm tăng khối lượng tính toán bướm lên hơn bốn lần. Hệ thống phải trả giá đắt với dung lượng bộ nhớ tăng gấp đôi, thông lượng I/O tăng gấp ba và khối lượng tính toán tăng vọt, trong khi độ chính xác ngữ âm nhận lại hoàn toàn bằng không.

> 💡 **NHÌN THẤU VẬT LÝ**  
> Tăng tần số lấy mẫu từ $16\text{ kHz}$ lên $48\text{ kHz}$ làm tràn ranh giới $4.608\text{ byte}$ của một khối Block RAM 36-kbit và tăng khối lượng tính toán phía sau hơn bốn lần, lãng phí diện tích silicon và năng lượng động chỉ để thu nhận các tần số siêu âm nằm ngoài giới hạn cơ sinh học của thanh đới con người.

---

### Kịch bản chẩn đoán 2: Hình phạt Gabor–Heisenberg ở 5 ms

#### Giả thuyết ngây thơ
Để triệt tiêu độ trễ xử lý giọng nói trong một trợ lý ảo siêu phản ứng, một kỹ sư nhúng muốn cắt giảm mạnh mẽ sàn tích lũy khung vật lý. Thay vì đợi $25\text{ ms}$ để gom đủ $400\text{ mẫu}$ âm thanh, kỹ sư cắt ngắn độ dài cửa sổ phân tích xuống còn $L = 80\text{ mẫu}$ ($\Delta t = 5\text{ ms}$) ở $16\text{ kHz}$, với lập luận rằng các mạng nơ-ron sâu hiện đại vẫn có thể trích xuất đặc trưng âm học từ các lát cắt thời gian cực ngắn.

#### Phép tính toán học
1. **Độ rộng búp chính phổ theo nguyên lý bất định:**  
   Nguyên lý bất định Gabor–Heisenberg chi phối sự định xứ thời gian - tần số trong mọi phép biến đổi tuyến tính: độ định xứ thời gian ($\Delta t$) và độ phân giải tần số ($\Delta f$) bị ràng buộc bởi $\Delta t \cdot \Delta f \ge 1 / (4\pi)$. Với một cửa sổ có thời lượng $\Delta t$, độ rộng hiệu dụng của búp phổ chính tỷ lệ nghịch với thời gian cửa sổ:
   $$\begin{aligned}
   \text{Tại } \Delta t &= 25\text{ ms } (L = 400\text{ mẫu}): \quad \Delta f \approx \frac{1}{0{,}025\text{ s}} = 40\text{ Hz} \quad (\text{độ rộng điểm 0 búp chính Hamming}: \approx 80\text{ Hz}) \\
   \text{Tại } \Delta t &= 5\text{ ms } (L = 80\text{ mẫu}): \quad \Delta f \approx \frac{1}{0{,}005\text{ s}} = 200\text{ Hz} \quad (\text{độ rộng điểm 0 búp chính Hamming}: \approx 400\text{ Hz})
   \end{aligned}$$

2. **Sự nhòe formant và sụp đổ ngữ âm:**  
   Trong bộ máy phát âm của con người, các tần số formant đại diện cho các cực cộng hưởng âm học của thanh đạo. Các formant liền kề—đặc biệt là hai formant đầu tiên ($F_1$ và $F_2$), vốn mang tính quyết định để nhận diện nguyên âm—thường chỉ cách nhau khoảng $150\text{--}200\text{ Hz}$.  
   Khi búp chính của bộ lọc bị phình rộng thành $\Delta f \approx 200\text{ Hz}$ (với vùng triệt tiêu búp phụ trải dài $400\text{ Hz}$), bộ phân tích phổ không thể phân giải hai đỉnh phổ cách nhau $180\text{ Hz}$. Hai formant phân biệt bị hòa lẫn vào nhau thành một khối phổ nhòe nhoẹt. Sự phân biệt ngữ âm giữa các nguyên âm cơ bản sụp đổ hoàn toàn—ví dụ nguyên âm đóng trước $/i/$ (với $F_2$ cao, $F_1$ thấp) bị nhòe thành một khối không thể phân biệt với nguyên âm đóng sau $/u/$ (với $F_1, F_2$ thấp và sát nhau), xóa sạch biểu diễn ngữ âm cần thiết cho mô hình phía sau.

#### Vì sao vật lý và silicon từ chối
Bộ máy phát âm của con người bị ràng buộc bởi quán tính cơ sinh học: lưỡi, ngạc mềm, hàm và các cơ họng không thể biến đổi trạng thái nhanh hơn $20\text{--}30\text{ ms}$. Nghiêm trọng hơn, $5\text{ ms}$ ngắn hơn đáng kể so với chu kỳ cao độ cơ bản ($T_0$) của giọng nam trầm thông thường ($1 / 85\text{ Hz} \approx 11{,}8\text{ ms}$). Cửa sổ $5\text{ ms}$ chỉ bắt được một phần dang dở của một chu kỳ thanh môn duy nhất. Tùy thuộc vào việc cửa sổ $5\text{ ms}$ rơi trúng pha mở hay pha đóng của thanh môn, năng lượng phổ trích xuất được sẽ dao động hỗn loạn hàng chục decibel giữa các khung liên tiếp, phá hủy tính ổn định của đặc trưng đầu vào.

> 💡 **NHÌN THẤU VẬT LÝ**  
> Cắt ngắn cửa sổ xuống dưới $20\text{ ms}$ không tạo ra một hệ thống độ trễ siêu thấp; nó tạo ra một vệt nhòe phổ có độ phân giải kém. Độ trễ thời gian không thể bị ép vượt qua quán tính cơ sinh học của thanh đạo con người mà không vi phạm giới hạn Gabor--Heisenberg và làm dính liền các tần số formant sống còn.

---

### Kịch bản chẩn đoán 3: Bẫy biến đổi rời rạc trực tiếp

#### Giả thuyết ngây thơ
Một kiến trúc sư phần cứng khi quan sát luồng STFT nhận thấy rằng sau khi áp cửa sổ, khung âm thanh có đúng $L = 400\text{ mẫu}$. Thay vì chèn thêm $112$ số 0 nhân tạo để đạt kích thước lũy thừa của hai ($N = 512$), kiến trúc sư lập luận rằng FPGA nên tính trực tiếp Biến đổi Fourier rời rạc 400 điểm (Direct 400-point DFT), nhằm tránh chi phí bộ nhớ lưu các số 0 và loại bỏ điều mà họ cho là các phép tính thừa thãi.

#### Phép tính toán học
1. **Độ phức tạp số học của DFT trực tiếp:**  
   Để tạo ra phổ công suất một phía lên tới giới hạn Nyquist, DFT trực tiếp phải tính $K = L/2 + 1 = 400/2 + 1 = 201$ bin tần số độc lập theo phương trình biến đổi trực tiếp:
   $$X[k] = \sum_{n=0}^{L-1} x[n] e^{-j 2\pi k n / L}, \quad k = 0, 1, \dots, 200$$
   Mỗi bin đòi hỏi đúng $L = 400$ phép nhân-tích lũy số phức (complex MAC). Trên toàn bộ 201 bin, DFT trực tiếp đòi hỏi:
   $$\text{Khối lượng}_{\text{DFT}} = 201 \times 400 = 80.400\text{ phép MAC phức/khung}$$

2. **Độ phức tạp số học của FFT cơ số 2 Cooley–Tukey:**  
   Bằng cách chèn thêm $112$ số 0 vào đuôi để tạo thành vector độ dài $N = 512$ ($N = 2^9$), chuỗi xử lý mở khóa thuật toán FFT cơ số 2 đệ quy Cooley–Tukey. Khối lượng tính toán của FFT chia đôi theo thời gian được giới hạn bởi $(N/2) \log_2 N$ phép tính bướm (butterfly operations):
   $$\text{Khối lượng}_{\text{FFT}} = \frac{512}{2} \log_2(512) = 256 \times 9 = 2.304\text{ phép tính bướm/khung}$$

3. **So sánh chi phí phần cứng silicon:**  
   Đối chiếu hai khối lượng tính toán cho thấy sự phân kỳ số học rõ rệt:
   $$\text{Tỷ lệ cắt giảm} = \frac{80.400\text{ phép MAC phức}}{2.304\text{ phép tính bướm}} \approx 34{,}9\times$$

#### Vì sao vật lý và silicon từ chối
Trên FPGA, một kiến trúc DFT trực tiếp bậc $\mathcal{O}(L^2)$ buộc phải hoàn tất trong hạn chót $10\text{ ms}$ của mỗi bước nhảy. Điều này đòi hỏi hoặc phải phân bổ ồ ạt hàng loạt bộ nhân chạy song song làm cạn kiệt các kênh định tuyến silicon và tăng vọt công suất tiêu thụ, hoặc phải ép xung bộ nhân tuần tự lên tần số cực cao. Ngược lại, FFT cơ số 2 ánh xạ tuyệt đẹp thành một đường ống tính toán tầng gọn gàng, tiêu tốn rất ít tài nguyên tính toán và bộ nhớ. Đáng chú ý, $112$ số 0 đệm thêm tốn đúng **0 phép nhân**, không hề làm méo mó tín hiệu nhân tạo, mà lại mở khóa tính đối xứng đệ quy giúp tiết kiệm tới $34{,}9\times$ chi phí tính toán.

> 💡 **NHÌN THẤU VẬT LÝ**  
> Đệm số 0 không phải là sự lãng phí tính toán; đó là một chất xúc tác kiến trúc. Các số 0 đệm tốn đúng 0 phép nhân-tích lũy nhưng lại mở khóa tính đối xứng đệ quy lũy thừa của hai, cắt giảm tới $34{,}9\times$ khối lượng tính toán trên silicon.

---

### Kịch bản chẩn đoán 4: Nút thắt cổ chai ma trận dày

#### Giả thuyết ngây thơ
Một kỹ sư quen với phần mềm khi ánh xạ tầng lọc Mel lên FPGA đã xem ma trận trọng số bộ lọc như một ma trận dày đặc tiêu chuẩn. Tầng này nhân $K = 257$ bin năng lượng phổ với $M = 80$ vector bộ lọc tam giác:
$$E_\ell[m] = \sum_{k=0}^{256} g_m[k] P_\ell[k], \quad m = 0, 1, \dots, 79$$
Lưu trữ phép biến đổi này dưới dạng ma trận FP32 dày đặc đòi hỏi $80 \times 257 \times 4\text{ B} = 82.240\text{ byte} = 80{,}3\text{ KiB}$. Trên bo mạch Kria KV260, cấu trúc dày này chiếm $82.240 / 4.608 \approx 18\text{ khối Block RAM } 36\text{-kbit}$ ($12{,}4\%$ tổng BRAM trên chip).

#### Phép tính toán học
1. **Khai thác tính thưa của dải lọc Mel:**  
   Vì mỗi bộ lọc Mel $g_m[k]$ là một hình tam giác gọn gàng, chỉ nhận giá trị khác không trong dải tần giới hạn $[k_{m-1}, k_{m+1}]$, các bộ lọc liền kề gối đầu lên nhau đúng $50\%$. Mỗi bin tần số $k$ chỉ bị bao phủ bởi tối đa hai bộ lọc tam giác.  
   Hệ quả là trong tổng số $80 \times 257 = 20.560$ phần tử của ma trận, chỉ có một phần rất nhỏ thực sự mang giá trị khác không:
   $$\text{Số trọng số khác không} \approx 2 \times 257 \approx 514\text{ trọng số} \quad (\text{hoặc } 80 \times 6{,}4 \approx 512\text{ trọng số active})$$
   Hơn $97{,}5\%$ dung lượng của ma trận dày đặc chỉ chứa toàn các số 0 cấu trúc vô nghĩa.

2. **Biểu diễn lưu trữ nén thưa:**  
   Thay vì lưu trữ hàng nghìn số 0 cấu trúc ở định dạng FP32, kiến trúc sư phần cứng nén từng bộ lọc thành:
   - Các trọng số lượng tử hóa số nguyên 16-bit (INT16, $2\text{ byte}$ mỗi trọng số khác không): $514 \times 2 = 1.028\text{ byte}$.
   - Một phần tiêu đề siêu dữ liệu gọn nhẹ cho 80 dải lọc lưu chỉ số bin bắt đầu $k_{\text{min}}$ ($1\text{ byte}$) và độ dài dải $K_m$ ($1\text{ byte}$): $80 \times 2\text{ B} = 160\text{ byte}$.
   
   Tổng dung lượng bộ nhớ nén cần thiết chỉ còn:
   $$\text{Bộ nhớ nén} = 1.028\text{ B} + 160\text{ B} = 1.188\text{ byte}$$

3. **Tác động tới tài nguyên silicon và băng thông đọc:**  
   So sánh ma trận dày FP32 với biểu diễn nén thưa INT16 cho thấy:
   $$\begin{aligned}
   \text{Chiếm dụng BRAM} &= \frac{1.188\text{ byte}}{4.608\text{ byte/BRAM}} \approx 25{,}8\% \text{ của MỘT khối Block RAM duy nhất} \\
   \text{Tỷ lệ thu nhỏ bộ nhớ} &= \frac{82.240\text{ byte}}{1.188\text{ byte}} \approx 69{,}2\times
   \end{aligned}$$

#### Vì sao vật lý và silicon từ chối
Nén thưa thu hẹp dấu chân bộ nhớ của dải lọc Mel từ 18 khối BRAM xuống còn chưa đầy một phần ba ($25{,}8\%$) của một khối BRAM duy nhất, lập tức giải phóng 17 khối BRAM vật lý quý giá cho các trọng số của mô hình mạng nơ-ron âm học. Hơn nữa, băng thông đọc bộ nhớ giảm sụp đổ từ $20.560$ lượt đọc xuống đúng $514$ lượt đọc mỗi khung—**cắt giảm tới $40\times$ số thao tác truy xuất bộ nhớ**.

> 💡 **NHÌN THẤU VẬT LÝ**  
> Lưu trữ các số 0 cấu trúc trong bộ nhớ vật lý là hành vi tự sát kiến trúc. Nén tam giác thưa thu gọn dấu chân dải lọc Mel tới $69{,}2\times$, ép 18 khối Block RAM vào một phần tư của một khối duy nhất và cắt giảm tới $40\times$ băng thông đọc bộ nhớ.

---

### Bảng tổng kết: Bảng tổn thương bốn nút vặn cấu hình

Bốn chế độ lỗi chẩn đoán chứng minh rằng các tham số chuẩn mực của chuỗi xử lý tiếng nói dòng ($f_s = 16\text{ kHz}, L = 400, N = 512, \text{Mel thưa}$) không phải là những quy ước tùy tiện; chúng chính là giao điểm tối ưu Pareto chính xác giữa các quy luật vật lý tiếng nói con người và các ràng buộc vi kiến trúc của silicon biên.

| Nút vặn cấu hình | Biến đổi ngây thơ | Cơ chế gãy đổ vật lý | Hệ quả trên phần cứng silicon |
| :--- | :--- | :--- | :--- |
| **Tần số lấy mẫu ($f_s$)** | $16\text{ kHz} \to 48\text{ kHz}$ | Dải Nyquist mở rộng $24\text{ kHz}$; thu tạp âm siêu âm vô nghĩa | Bộ đệm phình to $4.800\text{ B} > 4.608\text{ B}$; tràn sang **2 BRAM**; tính toán FFT tăng hơn $4\times$ |
| **Độ dài cửa sổ ($L$)** | $25\text{ ms} \to 5\text{ ms}$ | Bất định Gabor nới rộng búp chính lên $\Delta f \approx 200\text{ Hz}$; dính liền formant $F_1/F_2$ | Phá hủy tính tách biệt ngữ âm (/i/ so với /u/); bất ổn định pha thanh môn |
| **Kích thước biến đổi ($N$)** | $N = 400\text{ (DFT trực tiếp)}$ | Bỏ qua đệm số 0; ép tính toán ma trận trực tiếp bậc $\mathcal{O}(L^2)$ | DFT trực tiếp đòi hỏi **$80.400$ phép MAC phức** (tệ hơn $34{,}9\times$ so với $2.304$ phép bướm FFT) |
| **Lưu trữ bộ lọc Mel** | Ma trận FP32 dày đặc | Lưu trữ $97{,}5\%$ số 0 cấu trúc; lãng phí SRAM nội bộ | Chiếm **18 khối Block RAM** ($12{,}4\%$ BRAM trên chip) và đòi hỏi $20.560$ lượt đọc/khung |

> 💡 **PHÁT HIỆN THEN CHỐT**  
> Các tham số chuẩn mực của chuỗi xử lý tiếng nói dòng—lấy mẫu $16\text{ kHz}$, cửa sổ $25\text{ ms}$, đệm số 0 $N=512$, và nén thưa Mel INT16—không phải là những quy ước phần mềm ngẫu nhiên. Chúng đại diện cho một ranh giới Pareto bất dịch nơi mà cơ sinh học thanh đạo người, giới hạn bất định âm học và các khối nguyên thủy bộ nhớ FPGA đạt tới sự hòa hợp silicon tối ưu.

---

### Cầu nối tự nhiên sang Mục 1.6: Từ nhận dạng sang đánh giá phát âm

Với chuỗi thông số tiền xử lý đã được bảo vệ vững chắc qua các thử nghiệm ứng suất, hệ thống sẵn sàng chuyển giao các vector phổ sang các tầng thuật toán tiếp theo để đo đạc quỹ đạo âm học thực tế mà không bị sai lệch bởi xu hướng tự sửa lỗi của các mô hình ngôn ngữ.
