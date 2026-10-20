# 1.6 Từ nhận dạng đến đánh giá: Báo cáo của nhóm nằm ở đâu, đã làm được gì, và những vấn đề còn mở

> **MỤC TIÊU HỌC TẬP**  
> Thay vì chỉ tiếp cận bài toán nhận dạng tiếng nói đơn thuần như việc chuyển tự âm thanh thành chuỗi văn bản, mục này nghiên cứu phương thức một hệ sinh thái xử lý tiếng nói tại biên chấm điểm phát âm bài đọc thành tiếng của người học. Chúng tôi đặt báo cáo kỹ thuật nội bộ của nhóm nghiên cứu (`BAO_CAO_492026.pdf`, gồm 32 slide trải qua bốn cuộc họp học thuật trong tháng 9/2026: 04/09, 11/09, 18/09, 23/09) vào đúng chuỗi quy trình đánh giá hoàn chỉnh, phục dựng tường minh hợp đồng toán học và hình học được thiết lập xuyên suốt các slide, làm rõ những giá trị kỹ thuật cốt lõi mà hợp đồng này đã đạt được, phân tích có hệ thống bốn ca biên mở độc lập, định hình các ứng viên kiến trúc khả dĩ trên một hệ trục đánh giá thống nhất, và chuẩn bị một trang quyết định hành động cho buổi thảo luận nhóm mà không áp đặt chủ quan lựa chọn của tập thể.

---

## 1.6.0 Báo cáo nằm ở đâu trong chấm đọc thành tiếng

Chấm điểm phát âm tự động trong công nghệ giáo dục có bản chất hoàn toàn khác biệt so với nhận dạng tiếng nói tự động (ASR). Một bộ nhận dạng ASR ánh xạ dạng sóng âm thanh liên tục thành các token chữ viết rời rạc nhằm tối đa hóa độ chính xác chuyển tự thống kê. Trong bài toán đó, mô hình ngôn ngữ tận dụng xác suất tiên nghiệm $P(W)$ để "bỏ qua" hoặc "tha thứ" cho các khiếm khuyết phát âm của người nói miễn là đoán trúng từ vựng. Ngược lại, hệ thống đánh giá phát âm tự động phải chấm điểm một người học đang đọc to một câu văn mẫu đã biết trước. Trong kịch bản này, văn bản chữ viết đã được xác định hoàn toàn; mục tiêu kỹ thuật duy nhất là đo lường người học phát âm chuỗi âm vị mục tiêu đó chuẩn xác đến mức nào, tự nhiên ra sao và sai lệch ở đâu. Hệ thống đánh giá hoạt động như một tấm gương âm học khắt khe, đo đạc trung thực từng độ lệch vật lý so với mẫu chuẩn.

Quy trình chấm một bài đọc thành tiếng đòi hỏi năm tầng xử lý độc lập:
1. **Tầng 1: Thu âm và Xử lý âm học thô (Audio Capture and Acoustic Conditioning):** Số hóa tín hiệu micro thô, khử trôi mức một chiều (DC offset), chuẩn hóa năng lượng nhằm bù đắp biến thiên khoảng cách từ miệng tới micro, và thực thi bộ tách hoạt tính giọng nói (Voice Activity Detection — VAD) để cắt bỏ khoảng lặng không lời ở đầu và cuối bản thu.
2. **Tầng 2: Căn biên từ (Forced Alignment — Định vị ranh giới từ):** Phân đoạn luồng âm thanh liên tục thành các khoảng từ rời rạc thông qua việc tính toán các mốc thời gian âm học $[t_{\text{start}}, t_{\text{end}}]$ cho từng token từ vựng trong câu văn mẫu.
3. **Tầng 3: Kiểm chứng độ đúng âm vị (Phonetic Correctness Verification — Chấm chất lượng âm phổ):** Đánh giá xem hiện thực phổ tần của từng phân đoạn có khớp với các âm vị mục tiêu hay không (chẳng hạn: kiểm chứng quỹ đạo formant $F_1, F_2, F_3$, tính tỷ số log-likelihood độ chuẩn âm vị Goodness of Pronunciation [GOP], hoặc phát hiện các lỗi thay thế, nuốt âm, hay chèn âm vị).
4. **Tầng 4: So khớp giai điệu và ngữ điệu với âm thanh mẫu (Melodic and Prosodic Comparison Against Reference Audio):** Trích xuất các đường bao ngữ điệu—chủ yếu là tần số cơ bản ($F_0$), trường độ âm tiết và động lực năng lượng—rồi so sánh quỹ đạo động học của chúng với một bản thu âm chuẩn mẫu.
5. **Tầng 5: Gán nhãn và Hiệu chỉnh điểm số (Labeling and Score Calibration):** Tổng hợp các số đo âm học và ngữ điệu thành phản hồi sư phạm, ánh xạ điểm số số học liên tục thành mã màu đạt/hỏng ở cấp độ từng từ, phản hồi chẩn đoán chi tiết, hoặc quy đổi sang các thang điểm đánh giá chuẩn hóa.

### Vị trí của báo cáo nhóm

Toàn bộ 32 slide trong tài liệu `BAO_CAO_492026.pdf` nằm trọn trong **Tầng 4** (So sánh giai điệu và ngữ điệu thông qua hệ số tương quan Pearson trên cao độ $F_0$) cùng một quy tắc heuristic ban đầu hướng tới **Tầng 5** (gán nhãn đạt/hỏng ở cấp độ từ bằng cơ chế phân ngưỡng cửa sổ trượt). Báo cáo không hiện thực hóa Tầng 1, 2, hay 3, mà thiết lập các giả định vận hành đặc thù cho từng tầng:
- **Tầng 1 được xem là đã giải quyết xong:** Tại Slide 25, quy trình vận hành trực tiếp trên một bản thu mẫu đã qua tiền xử lý và cắt gọt khoảng lặng sạch sẽ. Việc phát hiện khoảng lặng, khử trôi DC và cắt tỉa biên được giả định là đã hoàn tất ngoại tuyến trước khi thuật toán bắt đầu.
- **Tầng 2 được xem là không cần thiết:** Thay vì triển khai một mô hình âm học căn biên cưỡng bức (forced alignment) để tìm chính xác mốc thời gian $[t_{\text{start}}, t_{\text{end}}]$ của từng từ, báo cáo xây dựng một mô hình cửa sổ trượt giải tích (Slide 19–23) chia câu thành $K+1$ phân đoạn hình học gối nhau chỉ dựa trên số lượng từ $K$ và tổng độ dài câu $N$.
- **Tầng 3 được giả định tự động kéo theo từ tương quan cao độ:** Báo cáo xem độ tương quan của tần số cơ bản ($F_0$) là thước đo trực tiếp để biết người học đọc đúng hay sai ("kiểm tra xem người dùng có đọc giống mẫu không", Slide 2), với ngầm định rằng một người học có đường bao ngữ điệu bám khít mẫu thì cũng sẽ phát âm chuẩn xác các âm vị cốt lõi bên dưới.

### Sarah là một thước đo mẫu chuẩn, không phải chân lý ngôn ngữ học tuyệt đối

Xuyên suốt các buổi báo cáo, bản ghi âm đối sánh chuẩn luôn được gọi tên là "Sarah" (Slide 5, 12, 25, 32). Trong đường cơ sở kỹ thuật của nhóm, Sarah là một bản thu âm cụ thể của một người bản xứ đóng vai trò chiếc thước đo so sánh. Cần nhận thức rõ ràng rằng Sarah đại diện cho một mẫu đối sánh cụ thể chứ không phải chân lý ngôn ngữ học tuyệt đối. Trong tiếng nói con người, hai người bản xứ cùng đọc một câu hoàn toàn chuẩn xác vẫn sở hữu âm vực nền tự nhiên khác nhau (giọng trầm nam so với giọng thanh nữ), biên độ lướt cao độ khác nhau, và nhịp độ co giãn thời gian tự nhiên giữa các âm tiết cũng khác nhau.

Bằng việc chọn file âm thanh của Sarah làm cái đích duy nhất, quy trình đã áp dụng một sự đơn giản hóa kỹ thuật: đo lường đường bao ngữ điệu của học viên dựa trên một lần phát âm cố định. Việc nhận diện chính xác vị trí của báo cáo trong cấu trúc năm tầng giúp một thành viên mới trong nhóm nghiên cứu hiểu rõ nhóm đã chủ động cô lập điều gì, đã xây dựng được gì, và những câu hỏi then chốt nào vẫn đang mở cần tập thể quyết định.

---

## 1.6.1 Hợp đồng đánh giá đúng như slide đã ghi

Để bảo toàn tính trung thực học thuật, chúng tôi dựng lại trọn vẹn hợp đồng toán học và hình học chính xác theo các slide trình bày trong bốn cuộc họp tháng 9/2026.

### Cuộc họp ngày 04/09/2026: Lựa chọn tương quan Pearson làm độ đo ngữ điệu (Slide 1–9)

Buổi trình bày đầu tiên thiết lập mục tiêu kỹ thuật: *"so sánh xem user đọc có giống mẫu không"* (Slide 2). Nhóm lựa chọn hệ số tương quan tuyến tính Pearson ($r$) làm độ đo cốt lõi. Trên Slide 5, công thức Pearson được đưa ra dưới dạng tường minh:

$$r = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2 \sum_{i=1}^n (y_i - \bar{y})^2}}$$

Slide định nghĩa rõ ràng các biến số:
- $n$: *"tổng thời gian của một từ"* (tổng thời lượng hoặc số lượng điểm mẫu rời rạc đại diện cho từ).
- $X = \{x_1, x_2, \dots, x_n\}$: *"mảng pitch của một từ bên User"* (mảng cao độ rời rạc của người học).
- $Y = \{y_1, y_2, \dots, y_n\}$: *"mảng pitch của một từ bên Sarah"* (mảng cao độ rời rạc của bản thu chuẩn mẫu).
- $\bar{x}, \bar{y}$: *"trung bình cộng pitch"* (giá trị trung bình cộng cao độ của User và Sarah).

**Cơ sở toán học từ các slide:** Các tính chất suy diễn của hệ số tương quan Pearson được phân tích qua Slide 6–8:
1. **Đo lường tính đồng hướng của xu hướng (Tử số):** Tích $(x_i - \bar{x})(y_i - \bar{y})$ kiểm tra tính biến thiên cùng chiều. Nếu cao độ của người học tăng khi Sarah tăng (cùng nằm trên giá trị trung bình tương ứng), hoặc cùng giảm khi Sarah giảm, tích số sẽ mang dấu dương (*"Cùng xu hướng"*, Slide 7). Ngược lại, nếu người học lên giọng trong khi Sarah xuống giọng, tích số sẽ mang dấu âm (*"Ngược xu hướng"*, Slide 7).
2. **Bất biến với âm vực và biên độ dao động (Mẫu số):** Việc chuẩn hóa bằng $\sigma_X \sigma_Y$ đưa giá trị hiệp phương sai về chặt chẽ trong khoảng $[-1, +1]$ (Slide 8). Phép tính này triệt tiêu hoàn toàn độ lệch cao độ tuyệt đối (*"loại bỏ khác biệt về độ cao giọng"*, Slide 6), cho phép so sánh trực tiếp giữa giọng nam trầm và giọng nữ cao, đồng thời chuẩn hóa luôn cả biên độ lướt giọng (*"triệt tiêu độ chênh lệch biên độ lượn sóng"*, Slide 8).

Slide 9 cung cấp một đường dẫn tài liệu tham khảo cho phép dẫn xuất thống kê này: `https://www.statisticssolutions.com/free-resources/directory-of-statistical-analyses/pearsons-correlation-coefficient/`.

### Cuộc họp ngày 11/09/2026: Tiền xử lý nội suy và Mô hình cửa sổ trượt (Slide 10–23)

Bài báo cáo ngày 11/09/2026 giải quyết hai đòi hỏi trung tâm: đồng nhất độ dài mảng dữ liệu và định vị đánh giá dọc theo câu nhiều từ dưới tiêu đề *"SLIDING WINDOW PEARSON"* (Slide 10).

**Phần 1: Tiền xử lý nội suy tuyến tính (Slide 11–18).** Công thức Pearson đòi hỏi hai mảng $X$ và $Y$ phải có cùng số lượng phần tử $n$. Do tốc độ nói của mỗi người là khác nhau, mảng pitch thô trích xuất từ người học và Sarah chắc chắn lệch nhau về độ dài. Slide 11 định nghĩa hợp đồng tiền xử lý: *"Resize length cho user bằng Sarah (Pearson yêu cầu 2 mảng cùng chiều dài: dùng linear interpolation)"*.

Để minh họa bước này, Slide 12–18 trình bày một ví dụ tính toán số học trực quan ("VD1"):
- Mảng đầu vào của User: $\text{User} = [40, 90, 100, 60, 120, 145]$ ($6$ điểm).
- Mảng đích của Sarah: $\text{Sarah} = [30, 100, 60, 80]$ ($4$ điểm).

Mục tiêu là co mảng 6 điểm của User xuống còn 4 điểm để khớp với Sarah. Ánh xạ cả hai chuỗi lên trục tọa độ chuẩn hóa liên tục $x \in [0, 1]$:
- 6 điểm của User nằm tại các tọa độ đều $x \in \{0{,}0;\, 0{,}2;\, 0{,}4;\, 0{,}6;\, 0{,}8;\, 1{,}0\}$.
- 4 điểm đích của Sarah nằm tại các tọa độ $x \in \{0{,}0;\, 0{,}33;\, 0{,}67;\, 1{,}0\}$.

Slide 14–17 in rõ phép tính số học cụ thể cho từng vị trí đích:
1. **Tại $x = 0{,}0$ (Slide 14):** $\text{User}[0] = 40$.
2. **Tại $x = 0{,}33$ (Slide 15):** Tọa độ đích $0{,}33$ rơi vào khoảng $[0{,}2;\, 0{,}4]$ giữa $\text{User}(0{,}2) = 90$ và $\text{User}(0{,}4) = 100$. Tỷ lệ khoảng cách trong đoạn là $\alpha = \frac{0{,}33 - 0{,}20}{0{,}40 - 0{,}20} = \frac{0{,}13}{0{,}20} = 0{,}65$. Giá trị nội suy tương ứng là:
   $$\text{User}[1] = 90 + 0{,}65 \times (100 - 90) = 90 + 6{,}5 = 96{,}5$$
3. **Tại $x = 0{,}67$ (Slide 16):** Tọa độ đích $0{,}67$ rơi vào khoảng $[0{,}6;\, 0{,}8]$ giữa $\text{User}(0{,}6) = 60$ và $\text{User}(0{,}8) = 120$. Tỷ lệ khoảng cách trong đoạn là $\alpha = \frac{0{,}67 - 0{,}60}{0{,}80 - 0{,}60} = \frac{0{,}07}{0{,}20} = 0{,}35$. Giá trị nội suy tương ứng là:
   $$\text{User}[2] = 60 + 0{,}35 \times (120 - 60) = 60 + 21{,}0 = 81{,}0$$
4. **Tại $x = 1{,}0$ (Slide 17):** Điểm cuối cùng được gán trực tiếp: $\text{User}[4] = 145$ (trên Slide 17 ghi nhãn là $\text{User}[4]$, đại diện cho mẫu biên cuối).

Tại Slide 18, mảng kết quả sau khi co dãn được in toàn văn:
$$\text{User}_{\text{resized}} = [40, 96{,}5, 81, 145]$$

*Ghi chú quy ước về VD1:* Slide đưa thẳng các hệ số nội suy $0{,}65$ và $0{,}35$. Mặc dù quy ước biên trong mã nguồn Python (như tham số của `np.interp` so với việc làm tròn tọa độ rời rạc) chưa được mô tả chi tiết bằng mã lệnh trên slide, các con số in ra hoàn toàn trùng khớp với phép nội suy tuyến tính tại các tọa độ chuẩn hóa $x = 0{,}33$ và $x = 0{,}67$. Slide 18 kết lại bằng một ghi chú vận hành chân thực: *"Hỏi chatbot giải thích cho dễ hiểu"*.

**Phần 2: Mô hình cửa sổ trượt (Slide 19–23).** Thay vì tính một hệ số Pearson toàn cục duy nhất cho cả câu, nhóm đề xuất một mô hình cửa sổ trượt giải tích (Slide 19–22) nhằm định vị đánh giá theo từng vùng thời gian. Mô hình xác lập bốn tham số:
- $N$: tổng độ dài câu (tính theo số mẫu hoặc số khung).
- $K$: số lượng từ trong câu văn bản mẫu.
- $W$: độ rộng cửa sổ phân tích (tính theo số mẫu hoặc số khung).
- $S$: bước trượt của cửa sổ (stride).

Trên Slide 20–22, nhóm thống nhất tham số hóa: *"Giả sử $S = W / 2$, ta trượt $K + 1$ lần (đề xuất của thầy)"*. Thiết lập bước trượt gối đầu $50\%$ ($S = W/2$), để phủ kín toàn bộ độ dài câu $N$ qua đúng $K+1$ cửa sổ trượt, phương trình hình học xác lập:
$$N = W + K \times S \iff N = W + K \times \left(\frac{W}{2}\right) = W \left(1 + \frac{K}{2}\right) = W \left(\frac{K+2}{2}\right)$$
Giải phương trình đại số để tìm độ rộng cửa sổ $W$:
$$W = \frac{2N}{K+2}, \qquad S = \frac{W}{2} = \frac{N}{K+2}$$

**Quy tắc kết án của nhóm:** Tại Slide 23, nhóm ghép mô hình hình học này với một quy tắc ra quyết định chấm điểm rõ ràng:
> *"Nếu có bất kỳ cửa sổ nào có $r < 0{,}3$, thì tất cả các từ rơi vào cửa sổ đó đều bị tính là sai, kể cả khi từ đó cũng rơi vào một cửa sổ khác có $r \ge 0{,}3$."*

Theo quy tắc này, ngưỡng $r = 0{,}3$ đóng vai trò lằn ranh phân cách giữa ngữ điệu đạt chuẩn và lỗi sai. Điểm cốt lõi là quy tắc mang tính bất đối xứng và kết án triệt để: nếu một từ nằm đè lên nhiều cửa sổ gối nhau, chỉ cần một cửa sổ duy nhất tụt dưới $0{,}3$, toàn bộ các từ nằm trong cửa sổ đó đều bị đánh hỏng vĩnh viễn, bất chấp việc chúng có thể đạt điểm tương quan rất cao ở các cửa sổ lân cận.

### Cuộc họp ngày 18/09/2026: Tính đều đặn của lưới cao độ và Kiểm chứng cơ chế căn tâm Praat (Slide 24–30)

Cuộc họp thứ ba đi sâu khảo sát tính đều đặn theo thời gian của lưới trích xuất cao độ dưới tiêu đề: *"MẢNG PITCH CÁCH ĐỀU NHAU 0.01s: Đảm bảo áp dụng linear interpolation hợp lý"* (Slide 24).

Slide 25 đặt ra một câu hỏi thực nghiệm xuất phát từ một tệp âm thanh kiểm thử thực tế:
> *"Chứng minh các giá trị pitch do Praat ghi nhận cách đều nhau 0.01s (Có thể thắc mắc tại sao khoảng cách 0.01s, độ dài audio 1.450667s thì phải có 145 điểm pitch bắt đầu từ 0.01, 0.02, 0.03...)..."*

Khi xử lý tệp âm thanh mẫu có độ dài $T_{\text{audio}} = 1{,}450667\text{ s}$ (Slide 25), Praat trích xuất chính xác $142$ điểm cao độ, cách đều nhau từng bước $0{,}01\text{ s}$.

**Tra cứu tài liệu hướng dẫn của Praat:** Slide 26 dẫn chiếu tài liệu chính thức của Praat (`Intro_4_2__Configuring_the_pitch_contour.html`) và thư viện Parselmouth. Mở tài liệu Praat làm sáng tỏ công thức định cỡ khung:
> *"Nếu sàn cao độ (pitch floor) là 50 Hz, phương pháp phân tích cao độ đòi hỏi một cửa sổ phân tích dài 60 mili giây; nghĩa là để đo F0 tại thời điểm 0.850 giây, Praat cần xem xét đoạn âm thanh chạy từ 0.820 đến 0.880 giây. 60 mili giây này tương ứng với đúng 3 chu kỳ cao độ cực đại (3/50 = 0.060)."*

Tài liệu quy định:
$$\text{Độ dài cửa sổ phân tích} = \frac{3}{\text{pitch\_floor}}$$
Với ngưỡng sàn cao độ mặc định của nhóm là $75\text{ Hz}$, độ rộng cửa sổ phân tích là:
$$T_{\text{window}} = \frac{3}{75} = 0{,}040\text{ s} = 40\text{ ms}$$

*Ghi chú lỗi in ấn trên Slide 27:* Slide 27 viết: *"Pitch floor = 75Hz => T = 1 / 75 = 0.04s (chiều dài cửa sổ phân tích)"*. Rõ ràng $1 / 75 \approx 0{,}013333\dots\text{ s} \ne 0{,}04\text{ s}$. Biểu thức in trên Slide 27 bị nhầm lẫn ở tử số ($1/75$ thay vì $3/75$), nhưng con số thời lượng tính ra $0{,}04\text{ s}$ hoàn toàn trùng khớp với định thức 3 chu kỳ chuẩn mực của tài liệu Praat ($3/75 = 0{,}04\text{ s}$).

Thêm vào đó, tài liệu Praat cho hàm lệnh `Sound: To Pitch...` xác định bước thời gian nhảy mặc định (hop size):
$$\Delta t = \frac{0{,}75}{\text{pitch\_floor}} = \frac{0{,}75}{75} = 0{,}010\text{ s} = 10\text{ ms}$$

**Tái hiện phép tính 142 điểm và độ lệch căn tâm:** Slide 28–30 truy vết các bước tính toán số học:
1. **Khoảng thời gian nội vi cho các cửa sổ trọn vẹn (Slide 28):** Để một cửa sổ phân tích dài $0{,}04\text{ s}$ nằm hoàn toàn bên trong biên bản thu $[0;\, 1{,}450667\text{ s}]$, khoảng không gian khả dụng cho tâm cửa sổ di chuyển là:
   $$T_{\text{interior}} = 1{,}450667\text{ s} - 0{,}040000\text{ s} = 1{,}410667\text{ s}$$
2. **Số bước trượt và Tổng số điểm mẫu (Slide 29):** Với bước nhảy $\Delta t = 0{,}01\text{ s}$, số bước nhảy nguyên vẹn là:
   $$\text{Số bước trượt} = \left\lfloor \frac{1{,}410667}{0{,}01} \right\rfloor = 141 \implies \text{Tổng số điểm} = 141 + 1 = 142\text{ điểm}$$
3. **Độ lệch căn tâm (Slide 30):** 141 bước trượt này bao phủ một khoảng $141 \times 0{,}01 = 1{,}410000\text{ s}$, để lại một khoảng dôi dư:
   $$T_{\text{residual}} = 1{,}410667\text{ s} - 1{,}410000\text{ s} = 0{,}000667\text{ s}$$
   Cơ chế căn tâm của Praat chia đều phần dôi dư này cho điểm bắt đầu và điểm kết thúc của tệp (Slide 30):
   $$\text{Độ lệch căn tâm} = \frac{0{,}000667\text{ s}}{2} = 0{,}00033\text{ s}$$
   Tâm của cửa sổ phân tích đầu tiên nằm tại vị trí một nửa chiều dài cửa sổ cộng thêm độ lệch căn tâm này:
   $$t_1 = \frac{T_{\text{window}}}{2} + \text{Độ lệch căn tâm} = \frac{0{,}04}{2} + 0{,}00033 = 0{,}02033\text{ s}$$
   Điều này giải thích chính xác tại sao lưới trích xuất cao độ bắt đầu tại $t_1 \approx 0{,}02033\text{ s}$ chứ không phải $0{,}01\text{ s}$, làm sáng tỏ hoàn toàn cơ chế phân khung được phân tích trên Slide 25–30.

### Cuộc họp ngày 23/09/2026: Ngân sách sai số làm tròn và Ứng xử tại biên (Slide 31–32)

Báo cáo cuối cùng xem xét hiệu ứng biên trong tính toán số học dưới tiêu đề: *"CÁC VẤN ĐỀ NẢY SINH (PHẦN NÀY ĐỂ Ý KHI VIẾT BÁO CÁO; TRONG CODE PYTHON TỰ ĐỘNG XỬ LÝ CẮT BỎ)"* (Slide 31).

Slide 32 khảo sát một kịch bản số học cụ thể:
- Âm thanh chuẩn (Sarah): $T_1 = 1{,}42\text{ s}$, trích xuất được $n_1 = 139$ điểm cao độ.
- Âm thanh học viên (User): $T_2 = 2{,}00\text{ s}$, với số điểm được ghi nhãn trên slide là `n1 = 196`.

*Ghi chú lỗi in ấn trên Slide 32:* Slide in *"T2 = 2s, n1 = 196"*, lặp lại tên biến $n_1$ thay vì định danh số điểm của User là $n_2 = 196$.

Slide sau đó tính toán một bước thời gian co dãn hiệu dụng:
$$\theta = \frac{T_1}{n_2} = \frac{1{,}42\text{ s}}{196} = 0{,}0072448979\dots\text{ s} \approx 0{,}007\text{ s}$$
(Lưu ý: trên slide in ký hiệu công thức là $\theta = \frac{T_2}{n_1} = 0{,}00724489\text{s}$, hoán đổi chỉ số biến trong công thức nhưng giá trị số học được tính toán chính xác từ phép chia $1{,}42 / 196$).

**Ngân sách sai số làm tròn:** Slide 32 đánh giá điều gì sẽ xảy ra nếu $\theta$ bị làm tròn hoặc cắt ngắn còn ba chữ số thập phân ($0{,}007\text{ s}$):
1. Thời lượng được tái tạo lại trên 196 mẫu:
   $$T_{\text{reconstructed}} = 196 \times 0{,}007\text{ s} = 1{,}372\text{ s}$$
2. Độ chênh lệch thời gian giữa âm thanh gốc của Sarah và chuỗi biểu diễn sau khi co dãn:
   $$\Delta T = 1{,}420\text{ s} - 1{,}372\text{ s} = 0{,}048\text{ s}$$
3. Quy đổi độ lệch thời gian sang số khung cao độ chuẩn $0{,}01\text{ s}$:
   $$\text{Số khung bị lệch} = \frac{1{,}420\text{ s} - 1{,}372\text{ s}}{0{,}01\text{ s}} = \frac{0{,}048\text{ s}}{0{,}01\text{ s}} = 4{,}8\text{ điểm}$$

Slide 32 kết luận: *"Bị hụt khoảng $(1{,}42 - 1{,}372) / 0{,}01 = 4$ đến $5$ điểm pitch $\implies$ Do đó tính xấp xỉ sẽ bị thiếu hoặc thừa điểm. Ta xem đây là sai số cho phép."*

**Phép tính kiểm chứng phòng thí nghiệm cho độ dài $2{,}00\text{ s}$:** Nhằm đối chiếu hành vi tạo khung trên một đoạn âm thanh $2{,}00\text{ s}$ theo đúng cấu hình Praat đã kiểm chứng ngày 18/09 (sàn cao độ $75\text{ Hz}$, cửa sổ $0{,}04\text{ s}$, bước nhảy $0{,}01\text{ s}$):
$$T_{\text{interior}} = 2{,}000000\text{ s} - 0{,}040000\text{ s} = 1{,}960000\text{ s}$$
Số bước nhảy tương ứng là:
$$\text{Số bước trượt} = \frac{1{,}960000}{0{,}01} = 196 \implies \text{Tổng số điểm} = 196 + 1 = 197\text{ điểm}$$

Cần nhấn mạnh rằng con số $n_2 = 196$ trên Slide 32 và con số $197$ tính trong phòng thí nghiệm đại diện cho hai cấu trúc hoàn toàn độc lập. Con số $196$ trên Slide 32 là một tham số kịch bản giả định được nhóm chọn để minh họa tác động số học khi cắt ngắn bước thời gian còn ba chữ số thập phân ($\theta \approx 0{,}007\text{ s}$). Ngược lại, $197$ là số lượng điểm mẫu thu được khi áp dụng nghiêm ngặt độ rộng cửa sổ ($0{,}04\text{ s}$) và bước nhảy chuẩn ($\lfloor 1{,}96 / 0{,}01 \rfloor + 1$) lên tệp âm thanh $2{,}00\text{ s}$.

---

## 1.6.2 Hợp đồng đó đã mua được gì

Trách nhiệm quan trọng của bất kỳ nhà nghiên cứu nào khi tiếp nhận một dự án đang phát triển là phải hiểu rõ thiết kế hiện tại đã mang lại những lợi ích thực tế gì trước khi phân tích các góc cạnh chưa xử lý. Một người đọc nếu chỉ nhìn vào các ca mở rất dễ nảy sinh định kiến sai lầm rằng hệ thống trước đó được xây dựng tùy tiện hay thiếu sót. Trên thực tế, hợp đồng kỹ thuật được thiết lập xuyên suốt các slide tháng 9/2026 đã mang lại những ưu thế kỹ thuật rất rõ ràng:

1. **Tối thiểu hóa độ phức tạp tính toán (Slide 5, 11):** Việc thực thi phép nội suy tuyến tính (`np.interp`) và công thức Pearson chỉ đòi hỏi tích lũy vô hướng một chiều, các phép nhân-cộng (MAC) dạng đóng, và một phép căn bậc hai duy nhất. Cấu trúc số học dạng đóng này hoàn toàn không cần đến thuật toán tối ưu lặp, không cần ma trận quy hoạch động phức tạp, và không đòi hỏi các bộ đệm bộ nhớ lớn, giúp vận hành với chi phí tài nguyên tính toán tối thiểu trên phần cứng biên.
2. **Bất biến với âm vực giọng nói và biên độ lướt âm (Slide 6, 8):** Bằng cách trừ giá trị trung bình ($\bar{x}, \bar{y}$) và chia cho độ lệch chuẩn ($\sigma_X, \sigma_Y$), thước đo này tách biệt hoàn toàn việc đánh giá ngữ điệu khỏi độ cao tuyệt đối và độ rộng dao động cao độ (Slide 6, 8). Đúng như các slide đã nhấn mạnh, việc trừ trung bình giúp triệt tiêu sự chênh lệch cao độ nền giữa giọng nam trầm và giọng nữ cao (Slide 6), trong khi chia cho độ lệch chuẩn giúp chuẩn hóa biên độ lượn sóng ngữ điệu (Slide 8), cho phép so sánh trực tiếp giữa các âm vực khác nhau.
3. **Không cần quy trình huấn luyện và không tốn bộ nhớ lưu trọng số (Slide 2, 10):** Khác với các mô hình âm học nơ-ron đòi hỏi hàng gigabyte dữ liệu huấn luyện, các phép căn chỉnh CTC phức tạp và hàng megabyte bộ nhớ lưu trữ trọng số trên chip, thuật toán cửa sổ trượt Pearson hoạt động hoàn toàn như một thuật toán xác định dạng đóng. Nó không đòi hỏi epoch huấn luyện nào, không tốn bộ nhớ lưu trữ tham số, và không gây nghẽn băng thông truy xuất bộ nhớ.
4. **Tự định vị từ mà không cần bộ căn biên cưỡng bức ngoài (Slide 19–23):** Việc triển khai một bộ forced aligner ngoài (như quy trình Kaldi hay Montreal Forced Aligner) sẽ kéo theo từ điển phát âm cồng kềnh, các bộ chuyển tự G2P, và các mô hình Markov ẩn âm học phức tạp. Công thức giải tích của nhóm ($W = 2N/(K+2)$ với bước $S = W/2$) cung cấp một giải pháp hình học thanh thoát, phân bổ điểm số dọc theo dòng thời gian câu nói chỉ dựa vào số lượng từ $K$.
5. **Hạ tầng phân khung âm thanh được kiểm chứng thực nghiệm vững chắc (Slide 24–30):** Nhóm nghiên cứu đã tiến hành kiểm chứng ở cấp độ tín hiệu cơ chế tạo khung của Praat, xác thực độ dài cửa sổ phân tích ($40\text{ ms}$), bước nhảy thời gian ($10\text{ ms}$), và độ lệch căn tâm dưới mili-giây ($0{,}00033\text{ s}$). Tinh thần kỷ luật thực nghiệm này tạo nên một điểm tựa vững vàng cho mọi bước phát triển xử lý tín hiệu tiếp theo.

---

## 1.6.3 Bốn ca mở, độc lập

Sau khi đã xác định rõ những điểm mạnh cốt lõi của hợp đồng, chúng ta chuyển sang phân tích các ca mở nơi động lực vật lý của tiếng nói phân kỳ khỏi các giả định vận hành trên slide.

**Tính độc lập tương hỗ của các ca mở.** Cần nhận thức sâu sắc rằng bốn ca mở chi tiết dưới đây là **hoàn toàn độc lập với nhau**. Chúng không bắt nguồn từ một lỗi lập trình chung; trái lại, mỗi ca đại diện cho một chiều kích vật lý riêng biệt của tín hiệu tiếng nói. Xử lý triệt để các khung vô thanh (Ca 3) không thể giải quyết được sự biến thiên nhịp điệu phi tuyến (Ca 2); định vị chính xác ranh giới từ âm học (Ca 4) cũng không thể kiểm chứng được liệu người học có phát âm đúng các formant nguyên âm hay không (Ca 1). Mỗi ca mở cần được xem xét độc lập dựa trên cơ sở toán học và vật lý của chính nó.

Trong mục này, chúng tôi tuyệt đối không đề xuất thuật toán uốn nắn thời gian động (DTW) như một giải pháp mặc định hay định đoạt trước lựa chọn kiến trúc của nhóm; chúng tôi ghi nhận trung thực giả định trên slide, thực tế vật lý chưa được bao quát, hệ quả của quy tắc hiện tại, câu hỏi định hướng cho buổi họp nhóm, và gán một trong hai nhãn kỹ thuật: **vá dòng** (patch this line) hoặc **thay dòng** (replace this line).

### Ca mở 1: Đại lượng đo là xu hướng cao độ, không phải danh tính âm vị

1. **Giả định trên slide (Slide 2, 5):** Quy trình giả định rằng việc tính toán hệ số tương quan Pearson trên tần số cơ bản ($F_0$) theo thời gian là đủ để xác thực người học có đọc đúng câu văn mẫu hay không (*"kiểm tra xem người dùng có đọc giống mẫu không"*, Slide 2).
2. **Thực tế vật lý chưa được giả định bao quát:** Âm học tiếng nói con người phân tách rành mạch giữa nguồn âm thanh (tần số cơ bản $F_0$, sinh ra do sự rung động của các nếp gấp thanh quản) và bộ lọc thanh đạo (các cộng hưởng formant $F_1, F_2, F_3, \dots$, được định hình bởi hình học của lưỡi, hàm và môi). Hệ số tương quan Pearson trên cao độ chỉ đo xem dây thanh quản của người nói có căng và chùng nhịp nhàng cùng hướng với mẫu hay không. Nó hoàn toàn mù đối với đường bao phổ của các formant.  
   Do đó, giả định này không thể xử lý hai hành vi thực tế của người học:
   - *Bẫy ngân nga (Humming Exploit):* Một học viên có thể ngậm chặt miệng và ngân nga điệu bổng trầm của câu nói mà không phát ra bất kỳ một phụ âm hay nguyên âm nào.
   - *Đọc sai âm vị nhưng đúng ngữ điệu:* Một học viên đọc một câu văn hoàn toàn sai lệch (chẳng hạn đọc *"I hate that dog"* thay vì câu mẫu *"I love this cat"*) nhưng giữ nguyên đường đi cao độ trần thuật sẽ tạo ra một chuỗi cao độ $X$ gần như trùng khớp với mẫu.
3. **Hậu quả của quy tắc hiện tại:** Do quỹ đạo cao độ bám sát xu hướng ngữ điệu của Sarah, tử số $\sum (x_i - \bar{x})(y_i - \bar{y})$ vẫn mang giá trị dương rất lớn, dẫn tới $r \ge 0{,}3$ (trong các ví dụ ngân nga minh họa, hệ số tương quan thực nghiệm có thể đạt tới $r \approx 0{,}98$). Quy tắc hiện tại sẽ chấm "Đạt" cho một đoạn âm thanh ngậm miệng hoặc đọc sai toàn bộ từ vựng.
4. **Câu hỏi cho buổi họp nhóm:** Nhóm nghiên cứu có dự định dùng tương quan Pearson trên $F_0$ làm bộ chấm điểm phát âm độc lập duy nhất, hay xem đây là một điểm số ngữ điệu phụ trợ được xếp lớp bên trên một bộ nhận dạng âm học âm vị độc lập?
5. **Nhãn kỹ thuật:** **thay dòng** (replace this line). Tương quan cao độ không thể xác thực danh tính âm vị; việc đánh giá xem học viên có thực sự phát âm đúng câu mẫu hay không bắt buộc phải sử dụng độ đo phổ âm học (như khoảng cách phổ hoặc tỷ số hợp lý xác suất âm vị).

### Ca mở 2: Cùng chỉ số sau co dãn tuyến tính không phải là cùng vị trí trong câu

1. **Giả định trên slide (Slide 11):** Quy trình giả định rằng việc áp dụng phép nội suy tuyến tính toàn cục (`np.interp`) để co dãn mảng pitch của người học cho bằng độ dài của Sarah sẽ căn khớp được các thời điểm âm học tương ứng xuyên suốt câu nói.
2. **Thực tế vật lý chưa được giả định bao quát:** Tốc độ nói của con người có tính biến thiên cục bộ phi tuyến sâu sắc. Khi một học viên ngập ngừng, kéo dài một nguyên âm khó, hoặc ngắc ngứ trước một từ vựng chưa quen, sự dãn nở thời gian diễn ra cục bộ tại đúng âm vị đó, trong khi các phần còn lại của câu vẫn được nói ở tốc độ bình thường.  
   Ví dụ: xét trường hợp một học viên đọc *"Gooood... morning"* ($1{,}8\text{ s}$) trong đó nguyên âm $/u/$ trong từ "Good" bị ngân dài chiếm tới $60\%$ tổng thời lượng câu, so với một người bản xứ đọc *"Good morning"* ($1{,}0\text{ s}$) trong đó từ "Good" chỉ chiếm $35\%$ thời lượng.
3. **Hậu quả của quy tắc hiện tại:** Phép nội suy tuyến tính toàn cục sẽ co dãn mọi khoảng thời gian đồng đều như nhau. Do từ đầu tiên của học viên bị kéo dài, phép nén mẫu đều đặn sẽ ép phần đuôi của từ thứ nhất bên phía học viên rơi vào đúng khung thời gian của từ thứ hai bên phía Sarah.  
   Tại khung chuẩn hóa $k = 45$, học viên vẫn đang kết thúc ngữ điệu đi lên của từ "Good" ($\Delta x > 0$), trong khi Sarah đã chuyển sang giai đoạn hạ giọng ở âm tiết không nhấn của từ "morning" ($\Delta y < 0$). Tích số của hai độ dốc ngược hướng này mang dấu âm:
   $$(x_{45} - \bar{x})(y_{45} - \bar{y}) < 0$$
   Sự lệch pha này kéo giá trị hiệp phương sai chuyển sang âm ($r < 0$). Mặc dù học viên phát âm cả hai từ với ngữ điệu chuẩn mực của người bản xứ, chiếc thước đo tuyến tính cứng nhắc vẫn tạo ra một kết quả đánh hỏng oan uổng (âm tính giả trầm trọng).
4. **Câu hỏi cho buổi họp nhóm:** Quy trình nên làm thế nào để tách rời sự biến thiên tốc độ nói cục bộ khỏi việc đánh giá ngữ điệu? Cơ chế căn chỉnh có nên cho phép tính đàn hồi thời gian phi tuyến để hấp thụ hiện tượng kéo dài nguyên âm trước khi tính toán tương quan ngữ điệu hay không?
5. **Nhãn kỹ thuật:** **thay dòng** (replace this line). Phép nội suy tuyến tính đồng đều về mặt cấu trúc không thể ánh xạ các trục thời gian âm học bị biến dạng phi tuyến khớp vào nhau.

### Ca mở 3: Trạng thái số học của các khung vô thanh

1. **Giả định trên slide (Slide 5):** Công thức Pearson giả định rằng $X = \{x_1, \dots, x_n\}$ và $Y = \{y_1, \dots, y_n\}$ là các vector số thực liên tục, dày đặc và có giá trị xác định trên mọi khung $i \in \{1, \dots, n\}$.
2. **Thực tế vật lý chưa được giả định bao quát:** Tiếng nói con người không phải là một dao động tuần hoàn liên tục. Các phụ âm xát vô thanh (/s/, /sh/, /f/), các pha đóng và bật của âm tắc vô thanh (/p/, /t/, /k/), cùng các khoảng lặng ngắt nghỉ giữa các từ hoàn toàn không có sự rung động của dây thanh âm. Trong suốt các khoảng thời gian này, tần số cơ bản $F_0$ không tồn tại về mặt vật lý.
3. **Hậu quả của quy tắc hiện tại:** Bộ slide không công bố rõ mã nguồn Python của nhóm xử lý các khung vô thanh như thế nào. Mở tài liệu của Praat cho thấy Praat đánh dấu các khung vô thanh là không xác định (undefined). Trong tính toán số học, điều này dẫn đến ba nguy cơ đổ vỡ:
   - *Nếu các khung vô thanh được lưu dưới dạng `NaN`:* Bất kỳ phép cộng $\sum (x_i - \bar{x})$ nào gặp phải `NaN` sẽ lây nhiễm toàn bộ bộ tích lũy, dẫn tới $r = \texttt{NaN}$ và làm sập bộ so sánh phía sau.
   - *Nếu các khung vô thanh được gán bằng $0{,}0\text{ Hz}$:* Một bước nhảy từ $0{,}0\text{ Hz}$ lên cao độ hữu thanh $150\text{ Hz}$ tạo ra một bước nhảy nhân tạo cực lớn $\Delta = 150\text{ Hz}$. Các biến thiên nhân tạo khổng lồ này sẽ chiếm lĩnh hoàn toàn tổng phương sai $\sum (x_i - \bar{x})^2$, làm biến dạng hệ số tương quan Pearson thành một thước đo so khớp khoảng lặng thay vì so sánh xu hướng ngữ điệu.
   - *Nếu xóa bỏ các khung vô thanh:* Việc xóa các khung vô thanh sẽ phá vỡ lưới thời gian đều đặn $0{,}01\text{ s}$, khiến phép nội suy tuyến tính hình học mất đi tính hợp lệ về mặt toán học.
4. **Câu hỏi cho buổi họp nhóm:** Đặc tả hình thức cho các khung vô thanh trong mã nguồn Python của nhóm là gì? Khi Praat đánh dấu một khung là không xác định hoặc vô thanh, thuật toán nên loại bỏ các khung khuyết, gán một giá trị lính canh, hay bỏ qua toàn bộ cửa sổ?
5. **Nhãn kỹ thuật:** **vá dòng** (patch this line). Đây là một bản vá vì các slide hiện để ngỏ hành vi xử lý khung vô thanh; giải pháp chỉ đơn thuần là viết bổ sung quy tắc xử lý khung vô thanh vào mã Python mà không làm thay đổi kiến trúc tổng thể của quy trình.

### Ca mở 4: Vết loang kết án của cửa sổ và phần dư làm tròn

1. **Giả định trên slide (Slide 20–23, 32):** Công thức cửa sổ trượt $W = 2N/(K+2)$ với bước trượt $50\%$ ($S = W/2$) có khả năng cô lập chính xác lỗi ở cấp độ từng từ, và độ lệch 4 đến 5 khung được chỉ ra trên Slide 32 là sai số kỹ thuật cho phép (*"sai số cho phép"*).
2. **Thực tế vật lý chưa được giả định bao quát:**
   - *Vết loang cửa sổ âm học:* Các cửa sổ hình học được định cỡ thuần túy dựa trên tổng độ dài câu $N$ và số lượng từ $K$ đã ngầm định rằng tất cả các từ trong câu có thời lượng bằng nhau. Trong thực tế ngôn ngữ, các từ tiếng Anh có độ dài chênh lệch rất lớn: các từ chức năng đơn âm tiết ngắn ("a", "in", "the") tương phản sâu sắc với các từ nội dung đa âm tiết kéo dài ("pronunciation", "extraordinary"). Các cửa sổ hình học cố định chắc chắn sẽ cắt ngang các ranh giới từ âm học. Một lỗi ngữ điệu xảy ra trọn vẹn trong Từ 2 sẽ tràn sang cả Cửa sổ 2 lẫn Cửa sổ 3.
   - *Phần dư làm tròn:* Việc cắt ngắn bước thời gian hiệu dụng $\theta$ còn ba chữ số thập phân ($0{,}007\text{ s}$) tích lũy độ trôi $4\text{ đến }5\text{ khung}$ ($40\text{ đến }50\text{ ms}$) xuyên suốt câu nói (Slide 32), làm dịch chuyển các mốc biên cửa sổ một cách ngẫu nhiên so với các âm vị thực tế.
3. **Hậu quả của quy tắc hiện tại:** Chiếu theo Quy tắc kết án của nhóm (Slide 23):
   > *"Nếu có bất kỳ cửa sổ nào có $r < 0{,}3$, thì tất cả các từ rơi vào cửa sổ đó đều bị tính là sai, kể cả khi từ đó cũng rơi vào một cửa sổ khác có $r \ge 0{,}3$."*  
   Vì Cửa sổ 2 tụt dưới $0{,}3$, cả Từ 1 và Từ 2 đều bị đánh sai. Vì Cửa sổ 3 cũng tụt dưới $0{,}3$, cả Từ 2 và Từ 3 tiếp tục bị đánh sai. Như vậy, chỉ một lỗi ngữ điệu cục bộ tại Từ 2 đã làm loang kết án và đánh hỏng toàn bộ cả ba từ trong câu. Trầm trọng hơn, độ lệch làm tròn 4 đến 5 khung được ghi nhận trên Slide 32 có thể dịch chuyển điểm cắt nhân tạo một khoảng bằng tới nửa chiều dài của một từ chức năng ngắn.
4. **Câu hỏi cho buổi họp nhóm:**
   - *Về hiện tượng loang cửa sổ:* Nhóm có nên thay thế công thức cửa sổ hình học nhân tạo bằng các ranh giới từ âm học thu được từ một bộ forced aligner, và có nên nới lỏng quy tắc kết án nhị phân thành điểm số tích lũy theo tỷ lệ gối đầu hay không?
   - *Về phần dư làm tròn:* Mã lệnh số học trong Python có nên giữ nguyên độ chính xác dấu phẩy động cho bước thời gian thay vì cắt cụt $\theta$ còn ba chữ số thập phân hay không?
5. **Nhãn kỹ thuật:**
   - **Hiện tượng loang cửa sổ:** **thay dòng** (replace this line). Việc định cỡ cửa sổ bằng công thức hình học nhân tạo không thể thích ứng với độ dài từ vựng biến thiên; việc thay thế dòng này bằng một bộ forced aligner sẽ đưa vào ranh giới từ thực tế, đại diện cho một sự thay thế kiến trúc chứ không thể vá cục bộ.
   - **Phần dư làm tròn:** **vá dòng** (patch this line). Việc giữ nguyên độ chính xác dấu phẩy động cho bước thời gian $\theta$ thay vì cắt cụt còn ba chữ số thập phân ($0{,}007\text{ s}$) là một bản vá số học cục bộ giúp bảo toàn cấu trúc phân khung hiện tại mà không làm thay đổi kiến trúc hệ thống.

---

## 1.6.4 Tầng báo cáo không có, và bốn ứng viên chưa chọn

### Các tầng quy trình không có trong báo cáo

Rà soát lại kiến trúc năm tầng được thiết lập tại Mục 1.6.0 xác nhận rằng báo cáo kỹ thuật của nhóm tập trung chuyên biệt vào Tầng 4 và một quy tắc ban đầu ở Tầng 5. Quy trình hoàn toàn không chứa các tầng vận hành sau:
1. **Tầng 1: Xử lý âm học tiền nguồn và VAD động.** Các slide vận hành trên một tệp ghi âm mẫu tĩnh đã cắt sẵn khoảng lặng (Slide 25). Báo cáo không có bộ tách hoạt tính giọng nói (VAD) theo thời gian thực để cắt bỏ khoảng lặng của người học, không có bộ lọc khử trôi DC, và không có cơ chế chuẩn hóa năng lượng tự động để xử lý micro USB giá rẻ tại biên.
2. **Tầng 2: Nhận biết ranh giới từ âm học thực tế.** Báo cáo không chứa mô hình căn biên cưỡng bức (forced alignment). Nhóm sử dụng công thức cửa sổ trượt hình học thuần túy giải tích để phân chia ranh giới giả định thay vì đo lường mốc thời gian thực của các từ.
3. **Tầng 3: Đo lường chất lượng âm phổ của âm vị.** Báo cáo không chứa bất kỳ tầng trích xuất đặc trưng phổ nào (như phổ Mel, chuỗi formant, hay xác suất hậu nghiệm âm học) để xác thực xem người học có thực sự phát âm đúng các phụ âm và nguyên âm mục tiêu hay không.

### Bốn ứng viên kiến trúc độc lập

Nhằm hỗ trợ định hướng kỹ thuật cho nhóm, chúng tôi hệ thống hóa bốn ứng viên kiến trúc khả dĩ. Bốn ứng viên này được đánh giá một cách khách quan trên cùng bốn trục tiêu chí thống nhất:
- *Trục 1 (Ý tưởng nhóm bảo tồn):* Mức độ gìn giữ cấu trúc thuật toán hiện tại của nhóm.
- *Trục 2 (Ca mở được xử lý):* Các ca biên vật lý trong Mục 1.6.3 được giải quyết.
- *Trục 3 (Độ mịn đầu ra):* Mức độ chi tiết của điểm số phản hồi (cấp cửa sổ, cấp từ, hay cấp âm vị).
- *Trục 4 (Độ phức tạp tính toán và Cấu hình FPGA):* Chi phí tài nguyên tính toán và khả năng hiện thực hóa trên phần cứng.

#### Ứng viên A: Giữ nguyên hợp đồng trên slide (Keep Contract)
- *Trục 1 (Ý tưởng nhóm bảo tồn):* Bảo tồn trọn vẹn 100% hợp đồng trên slide: giữ nguyên phép nội suy tuyến tính toàn cục (`np.interp`), công thức cửa sổ trượt $W = 2N/(K+2)$, và quy tắc kết án ngưỡng $r < 0{,}3$.
- *Trục 2 (Ca mở được xử lý):* Không xử lý thêm ca mở nào; chấp nhận độ lệch 4–5 khung như sai số cho phép.
- *Trục 3 (Độ mịn đầu ra):* Độ mịn thô ở cấp độ cửa sổ hình học (gán nhãn đạt/hỏng từng cửa sổ).
- *Trục 4 (Độ phức tạp tính toán và Cấu hình FPGA):* Cực kỳ nhẹ. Chỉ gồm các phép nhân-cộng MAC dạng đóng và một phép căn bậc hai duy nhất. Trên FPGA, thuật toán ánh xạ hoàn hảo vào một mạch số học gọn nhẹ, không cần bộ nhớ ngoài. Gánh nặng kỹ thuật bằng không do mã nguồn đã hoàn thiện.
- *Đánh giá hai mặt:* Điểm được là kiến trúc cực kỳ tinh gọn, không tốn bộ nhớ và sẵn sàng vận hành ngay lập tức nếu người học tuân thủ nhịp điệu đọc cố định. Điểm mất là chấp nhận toàn bộ các lỗ hổng âm tính giả do lệch pha nhịp điệu và dương tính giả do bẫy ngân nga.

#### Ứng viên B: Thêm biên từ rồi Pearson từng từ (Add Word Edges)
- *Trục 1 (Ý tưởng nhóm bảo tồn):* Giữ nguyên phép đo tương quan Pearson trên cao độ và việc dùng Sarah làm thước đo mẫu; chỉ thay thế việc chia cửa sổ hình học bằng các mốc biên từ âm học thực tế.
- *Trục 2 (Ca mở được xử lý):* Giải quyết triệt để hiện tượng loang kết án trong Ca mở 4 (loại bỏ hoàn toàn việc một từ sai làm lây hỏng các từ bên cạnh).
- *Trục 3 (Độ mịn đầu ra):* Điểm số chuẩn xác ở cấp độ từ thật ($K$ điểm số tương quan vô hướng độc lập cho $K$ từ).
- *Trục 4 (Độ phức tạp tính toán và Cấu hình FPGA):* Tính toán vừa phải. Đòi hỏi một lượt chạy mô hình forced alignment phía trước để trích xuất các mốc thời gian biên từ, sau đó thực thi $K$ lần gọi Pearson đoạn ngắn. Trên FPGA, các mốc thời gian biên từ cần được truyền theo luồng từ bộ xử lý chủ hoặc mô hình thượng nguồn. Gánh nặng kỹ thuật là tích hợp mô hình căn biên ngoài (như Kaldi hay MFA) hoặc bộ phân đoạn VAD.
- *Đánh giá hai mặt:* Điểm được là chấm điểm chính xác từng từ mà không bị loang kết án sang các từ lân cận. Điểm mất là đòi hỏi phải tích hợp thêm một hệ thống forced alignment phức tạp phía trước để trích xuất ranh giới thời gian.

#### Ứng viên C: Căn chỉnh đàn hồi, rồi Pearson trên đường uốn (Elastic Alignment)
- *Trục 1 (Ý tưởng nhóm bảo tồn):* Bảo tồn việc so sánh ngữ điệu với mẫu chuẩn Sarah và phép đo Pearson; chỉ thay thế dòng lệnh nội suy tuyến tính toàn cục (`np.interp`) bằng thuật toán uốn nắn thời gian phi tuyến (Dynamic Time Warping) dọc theo đường uốn tối ưu $\mathcal{P}$.
- *Công thức thuật toán:* Với chuỗi người học $X$ dài $N$ và chuỗi Sarah $Y$ dài $M$, khoảng cách cục bộ là khoảng cách Euclid $d(i, j) = \|x_i - y_j\|$. Ma trận chi phí tích lũy tuân theo công thức đệ quy quy hoạch động chuẩn tắc:
  $$D(i, j) = d(i, j) + \min\big(D(i-1, j),\, D(i, j-1),\, D(i-1, j-1)\big)$$
  Truy vết đường đi tối ưu $\mathcal{P} = ((i_1, j_1), \dots, (i_L, j_L))$ từ $(1, 1)$ đến $(N, M)$ giúp căn chỉnh đàn hồi các sự kiện âm học tương ứng. Hệ số tương quan Pearson sau đó được tính toán trực tiếp trên các cặp mẫu đã được tái chỉ mục dọc theo đường uốn $\mathcal{P}$.
- *Trục 2 (Ca mở được xử lý):* Xử lý triệt để Ca mở 2 (Cùng chỉ số sau co dãn tuyến tính) bằng cách hấp thụ hoàn toàn hiện tượng kéo dài nguyên âm và ngập ngừng cục bộ, ngăn ngừa tuyệt đối lỗi âm tính giả do lệch pha ($r < 0$). Khi kết hợp với mặt nạ khung hữu thanh, nó cô lập được Ca mở 3. Tuy nhiên, nó không xử lý được Ca mở 1 trừ khi các đặc trưng phổ đa chiều được đưa vào khoảng cách cục bộ $d(i, j)$.
- *Trục 3 (Độ mịn đầu ra):* Đường uốn ở cấp độ khung được ánh xạ quy về điểm số cửa sổ hoặc điểm số từ.
- *Trục 4 (Độ phức tạp tính toán và Cấu hình FPGA):* Tính toán vừa phải. Cần tính toán lưới quy hoạch động kích thước $N \times M$ (khoảng $250.000\text{ ô}$ cho một câu 5 giây). Trên FPGA, thuật toán ánh xạ tốt vào đường ống quy hoạch động dạng luồng mà không cần bộ nhớ ngoài. Gánh nặng kỹ thuật là hiện thực hóa bảng đệ quy DP 2D và lựa chọn hàm khoảng cách cục bộ.
- *Đánh giá hai mặt:* Điểm được là triệt tiêu hoàn toàn lỗi âm tính giả do lệch pha tốc độ nói cục bộ của học viên. Điểm mất là gia tăng độ phức tạp tính toán từ $O(N)$ lên $O(N \cdot M)$ và đòi hỏi thiết kế đường ống quản lý bộ nhớ đệm ma trận quy hoạch động.

#### Ứng viên D: Thay đại lượng đo (Goodness of Pronunciation hoặc Embedding âm học)
- *Trục 1 (Ý tưởng nhóm bảo tồn):* Giữ nguyên mục tiêu tối hậu là đánh giá phát âm tiếng Anh tự động; thay thế toàn bộ phép đo tương quan cao độ bằng xác suất hậu nghiệm từ mô hình âm học (GOP) hoặc các vector biểu diễn tiếng nói tự giám sát (như mô hình wav2vec 2.0 hoặc Conformer).
- *Trục 2 (Ca mở được xử lý):* Xử lý triệt để Ca mở 1 (Đúng âm vị) thông qua việc đánh giá trực tiếp tỷ số log-likelihood phổ âm học, xử lý tự nhiên Ca mở 3 (mô hình âm học nơ-ron xử lý bản chất cả khung hữu thanh lẫn vô thanh), và cung cấp khả năng tự căn biên âm vị nội tại.
- *Trục 3 (Độ mịn đầu ra):* Điểm số xác suất hậu nghiệm mịn ở cấp độ từng âm vị, âm tiết và từ.
- *Trục 4 (Độ phức tạp tính toán và Cấu hình FPGA):* Tính toán rất lớn. Đòi hỏi suy luận lan truyền tiến toàn bộ mạng nơ-ron, bộ nhớ lưu trữ tham số hàng megabyte và lượng lớn các phép nhân ma trận (GEMM). Trên FPGA, nó đòi hỏi một lõi tăng tốc mạng nơ-ron học sâu chuyên dụng cùng gánh nặng kỹ thuật lớn để huấn luyện, cắt tỉa và lượng tử hóa mô hình.
- *Đánh giá hai mặt:* Điểm được là đo lường trực tiếp độ chính xác của từng âm vị và phụ âm, giải quyết triệt để vấn đề âm học ngôn ngữ. Điểm mất là đòi hỏi tài nguyên phần cứng lớn gấp nhiều lần, cùng gánh nặng kỹ thuật khổng lồ để huấn luyện, cắt tỉa và lượng tử hóa mô hình âm học.

**Ghi chú trung lập rõ ràng:** Chúng tôi nhấn mạnh rằng Ứng viên C không hề được tuyên bố là giải pháp mặc định chiến thắng, và Ứng viên A cũng không hề bị loại bỏ như một phương án sai lầm. Nếu ngân sách tính toán của dự án bị thắt chặt tối đa và học viên được hướng dẫn đọc theo một nhịp gõ cố định, Ứng viên A cung cấp một đường cơ sở cực kỳ nhẹ nhàng. Nếu việc xác thực độ chuẩn xác của từng âm vị là yêu cầu sống còn, Ứng viên D là bắt buộc bất chấp dung lượng mô hình lớn. Quyết định lựa chọn giữa bốn ứng viên này hoàn toàn thuộc về tập thể nhóm nghiên cứu.

---

## 1.6.5 Trang họp nhóm và Bảng ma trận quyết định

Nhằm hỗ trợ buổi thảo luận hiệu quả trong cuộc họp nhóm sắp tới, Bảng ma trận quyết định tổng hợp các mối đánh đổi kỹ thuật giữa bốn ứng viên kiến trúc. Để bảo đảm tính khách quan, cột cuối cùng được để trống hoàn toàn cho quyết định chung của nhóm.

| Ứng viên | Ý tưởng nhóm bảo tồn | Ca mở được xử lý | Độ mịn đầu ra | Độ phức tạp tính toán | Cấu hình FPGA | Gánh nặng kỹ thuật | Nhóm lựa chọn |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A: Giữ hợp đồng** | Trọn vẹn hợp đồng slide (co dãn tuyến tính, cửa sổ trượt, luật $r<0{,}3$). | Không ca nào (coi phần dư 4–5 khung là sai số cho phép). | Thô (đạt/hỏng theo cửa sổ). | Phép tính MAC dạng đóng, 1 căn bậc hai. | Mạch số học gọn nhẹ. | Không thêm phần mềm mới; mã nguồn đã hoàn chỉnh. | |
| **B: Thêm biên từ** | Giữ Pearson cao độ và mẫu Sarah; thay thế cửa sổ hình học. | Vết loang Ca 4 (triệt tiêu việc loang kết án giữa các từ). | Cấp độ từ ($K$ điểm số vô hướng). | 1 lượt chạy aligner, $K$ lần gọi Pearson ngắn. | Thời điểm biên từ nhận từ luồng ngoài. | Tích hợp forced aligner (MFA/Kaldi) hoặc phân đoạn VAD. | |
| **C: Căn chỉnh đàn hồi** | Giữ Pearson trên đường uốn $\mathcal{P}$; thay phép co dãn đều. | Ca 2 (hấp thụ nhịp điệu nguyên âm), cô lập Ca 3. | Đường uốn $\to$ quy về từ hoặc cửa sổ. | Lưới quy hoạch động $N \times M$ ($2{,}5\times 10^5$ ô). | Đường ống quy hoạch động luồng. | Hiện thực hóa bảng đệ quy DP 2D; định nghĩa độ đo khoảng cách. | |
| **D: Thay đại lượng đo** | Giữ mục tiêu đánh giá tổng thể; thay thế tương quan cao độ. | Ca 1 (âm vị), Ca 3 (vô thanh), tự căn biên nội tại. | Mịn ở cấp xác suất hậu nghiệm âm vị. | Suy luận mạng nơ-ron tiến (GEMMs). | Bộ tăng tốc mạng nơ-ron chuyên dụng. | Huấn luyện, cắt tỉa và lượng tử hóa mô hình âm học (GOP/Conformer). | |

### Bốn câu hỏi hành động cho buổi họp nhóm

Ma trận quyết định phản ánh bốn ngã rẽ kiến trúc cụ thể. Chúng tôi đề xuất bốn câu hỏi dưới đây, được rút ra trực tiếp từ các ca mở được phân tích trong Mục 1.6.3, để định hướng nội dung thảo luận của nhóm:

1. **Về phạm vi kiểm chứng âm vị (Ca mở 1):** Hệ thống hiện tại có bắt buộc phải tự mình phát hiện các từ đọc sai âm vị hoặc từ bị đọc sót hay không, hay thiết bị xử lý giọng nói tại biên được thiết kế theo cấu trúc hai tầng, trong đó một tầng nhận dạng âm học phía trước sẽ kiểm chứng tính chuẩn xác của âm vị trước khi chuyển vector cao độ sang tầng này?
2. **Về cơ chế căn chỉnh thời gian (Ca mở 2):** Nhóm muốn giữ nguyên phép nội suy tuyến tính toàn cục bằng cách yêu cầu người học đọc theo nhịp gõ cố định (Ứng viên A), phân đoạn câu nói theo ranh giới từ âm học (Ứng viên B), hay áp dụng thuật toán uốn nắn thời gian phi tuyến đàn hồi (Ứng viên C) để hấp thụ biến thiên trường độ tự nhiên của nguyên âm?
3. **Về đặc tả số học cho khung vô thanh (Ca mở 3):** Quy tắc toán học chính thức nào sẽ được cam kết trong mã nguồn Python cho các khung vô thanh ($F_0 = 0$ hoặc không xác định)? Thuật toán sẽ áp dụng mặt nạ chỉ tính trên các khung cùng hữu thanh, nội suy tuyến tính lấp đầy các khoảng vô thanh, hay áp dụng một hình phạt điểm số rõ ràng?
4. **Về chuẩn hóa luật chấm điểm (Ca mở 4):** Nhóm nên tinh chỉnh Quy tắc kết án nhóm như thế nào? Quy tắc loại trừ nhị phân ($r < 0{,}3$ đánh hỏng toàn bộ các từ nằm đè) có nên được thay thế bằng một cơ chế tính điểm theo tỷ lệ phần trăm diện tích gối đầu giữa ranh giới âm học của từ và các cửa sổ trượt hay không?