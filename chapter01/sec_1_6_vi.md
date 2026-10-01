# 1.6 Từ nhận dạng đến đánh giá: Hai bài toán, hai thuật toán khác biệt

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì xem đánh giá phát âm là một sản phẩm phụ gắn sau mô hình nhận dạng giọng nói (ASR), mục này mổ xẻ sự phân kỳ bản chất giữa phiên âm xác suất và đo đạc âm học thực tế. Bằng cách chẩn đoán các cơ chế gãy đổ của đường cơ sở tương quan cao độ trên tiếng nói thực tế, chúng ta mở ra không gian lựa chọn kiến trúc để đánh giá ngữ điệu và âm vị ở rìa phần cứng.

---

### Cầu nối tự nhiên từ Mục 1.5: Frontend log-Mel chưa thể tự chấm điểm

Trong Mục 1.5, chúng ta đã chứng minh rằng tầng tiền xử lý dòng ánh xạ gọn gàng và xuất ra đều đặn một vector năng lượng 80 dải log-Mel sau mỗi nhịp bước $10\text{ ms}$. Tuy nhiên, bản thân 80 con số này mới chỉ là biểu diễn phổ tức thời; chúng hoàn toàn **chưa thể tự chấm điểm phát âm được**.

Trong các hệ thống nhận dạng giọng nói tự động (ASR) thông thường, chuỗi vector đặc trưng này được cấp vào một mô hình âm học nơ-ron và bộ giải mã thống kê để tìm chuỗi văn bản tối ưu:
$$\hat{W} = \arg\max_W P(W \mid \mathbf{X}) \propto P(\mathbf{X} \mid W) \cdot P(W)$$

Trong đó, mô hình ngôn ngữ tiên nghiệm $P(W)$ được thiết kế có chủ đích để **tha thứ cho lỗi người nói**: nếu một người phát âm ngọng hoặc biến dạng một nguyên âm, mô hình ngôn ngữ sẽ tính toán rằng chuỗi âm sai đó không có nghĩa trong từ điển, từ đó âm thầm tự sửa lỗi và phiên âm ra từ vựng đúng ngữ pháp có khả năng cao nhất. Trong bài toán nhận dạng văn bản, tha thứ lỗi phát âm là một ưu điểm thiết kế sống còn.

Ngược lại, trong bài toán **đánh giá phát âm (Pronunciation Assessment)**, cơ chế tha thứ này trở thành một lỗ hổng tai hại. Mục tiêu của hệ thống đánh giá không phải là đoán xem người dùng muốn nói gì, bởi vì câu mẫu chuẩn đã được biết trước 100%. Nhiệm vụ là so sánh khắt khe một lần đọc thực tế với mẫu chuẩn có sẵn để đo đạc xem người học phát âm *như thế nào*. Nếu sử dụng bộ giải mã ASR, mô hình ngôn ngữ sẽ tự vá lỗi và chấm điểm đạt cho những từ bị phát âm sai lệch. Đánh giá phát âm đòi hỏi một lớp thuật toán hoàn toàn khác: **đo đạc và xác thực quỹ đạo âm học thực tế**, đóng vai trò như một tấm gương âm học không khoan nhượng.

---

### Hộp 1: Đường cơ sở nhóm: Báo cáo 492026

Để giải quyết bài toán so khớp ngữ điệu trên thiết bị nhúng, nhóm nghiên cứu đã xây dựng một đường cơ sở thực nghiệm (ghi nhận trong tài liệu *Báo cáo 492026*, tháng 9/2026 bởi Đức Nguyễn Tiến) gồm các bước xử lý:

1. **Trích xuất quỹ đạo $F_0$ bằng Praat:** Hệ thống sử dụng thuật toán tự tương quan Praat để rút ra chuỗi tần số cơ bản $F_0$ của cả giọng người học (User) và giọng mẫu chuẩn (Sarah, trong tệp `sarah_trimmed.wav`).
2. **Bộ tham số thực nghiệm của Praat:** Với tệp âm thanh mẫu Sarah có thời lượng $T = 1{,}450667\text{ s}$, sàn tần số cơ bản $\text{pitch floor} = 75\text{ Hz}$, bước thời gian $0{,}01\text{ s}$ ($10\text{ ms}$), Praat trích xuất ra đúng $142\text{ điểm}$ cao độ.
3. **Nguồn gốc toán học của 142 điểm và độ lệch căn tâm:** Sàn $75\text{ Hz}$ đòi hỏi cửa sổ phân tích dài đúng ba chu kỳ cực đại:
   $$T_{\text{win}} = \frac{3}{75} = 0{,}040\text{ s} = 40\text{ ms}$$
   Khoảng thời gian khả dụng để tâm cửa sổ nằm trọn vẹn trong tệp âm thanh là:
   $$T_{\text{interior}} = 1{,}450667\text{ s} - 0{,}040000\text{ s} = 1{,}410667\text{ s}$$
   Với bước nhảy $\Delta t = 0{,}01\text{ s}$, số bước nguyên là $\lfloor 1{,}410667 / 0{,}01 \rfloor = 141\text{ bước}$, tạo ra tổng cộng $141 + 1 = 142\text{ điểm}$. Độ dài 141 bước chiếm $1{,}410000\text{ s}$, để lại phần dư $T_{\text{residual}} = 0{,}000667\text{ s}$. Cơ chế căn tâm của Praat chia đều phần dư này cho hai đầu, tạo ra độ lệch căn tâm $0{,}000667 / 2 = 0{,}00033\text{ s}$. Do đó, nhãn thời gian của điểm đầu tiên bắt đầu chính xác tại $t_1 = 0{,}04 / 2 + 0{,}00033 = 0{,}02033\text{ s}$.
4. **Co giãn nội suy tuyến tính (Linear Resampling):** Do người học đọc với tốc độ khác Sarah ($N_{\text{User}} \ne N_{\text{Sarah}}$), hệ thống dùng phép nội suy tuyến tính (`np.interp`) để co giãn chuỗi $F_0$ của người học về cùng độ dài $n$ với Sarah trên trục thời gian chuẩn hóa $[0, 1]$.
5. **Mô hình cửa sổ trượt (Sliding Window Pearson):** Nhóm chia câu $N$ mẫu thành $K+1$ cửa sổ trượt gối đầu $50\%$ ($S = W/2$, với $K$ là số từ trong câu). Chiều rộng mỗi cửa sổ được giải đại số từ đẳng thức phủ kín $N = W + K(W/2)$:
   $$W = \frac{2N}{K+2}, \qquad S = \frac{W}{2} = \frac{N}{K+2}$$
6. **Hệ số tương quan và Quy tắc kết án nhóm:** Trong từng cửa sổ, tương quan Pearson $r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sigma_X \sigma_Y}$ được tính để đo mức độ đồng điệu ngữ điệu. Nhóm chọn ngưỡng $r < 0{,}3$ làm điều kiện phát hiện lỗi với quy tắc kết án nghiêm ngặt: *nếu bất kỳ cửa sổ nào rơi xuống dưới 0,3, tất cả các từ gối lên cửa sổ đó đều bị đánh dấu là phát âm sai*, bất kể các cửa sổ lân cận có $r \ge 0{,}3$.

> ⚠️ **LƯU Ý XÁC ĐỊNH BẢN CHẤT**  
> Đây là đường cơ sở thực nghiệm ban đầu mà nhóm đã thực hiện trong báo cáo kỹ thuật, không phải là thuật toán cuối cùng của cuốn sách.

---

### Hộp 2: Chỗ Pearson tuyến tính gãy

Khi đưa đường cơ sở tuyến tính vào thử nghiệm trên tiếng nói con người thực tế, hai cơ chế gãy đổ vật lý sâu sắc lập tức bộc lộ, phá hủy tính đúng đắn của phép chấm điểm:

1. **Tempo cục bộ và hiện tượng đảo pha tương quan:**  
   Tốc độ phát âm của con người biến thiên phi tuyến tính cao độ. Khi một người học ngập ngừng, kéo dài một nguyên âm khó (chẳng hạn đọc kéo dài từ *“Gooood...”* chiếm $60\%$ thời lượng câu, trong khi cô giáo Sarah đọc lướt qua từ *“Good”* chỉ chiếm $35\%$), phép co giãn tuyến tính đồng đều sẽ nén dãn sai lệch toàn bộ trục thời gian. Phần đuôi nguyên âm của người học bị ép tràn sang khung thời gian ứng với từ tiếp theo của mẫu chuẩn.

2. **Một điểm tính $r$ tại khung lệch:**  
   Xét tại một khung thời gian chuẩn hóa $k$ sau khi co giãn tuyến tính: người học vẫn đang ngân cao độ nguyên âm của từ thứ nhất ($\Delta x_k = x_k - \bar{x} > 0$), trong khi mẫu chuẩn Sarah đã chuyển sang âm tiết không nhấn của từ thứ hai và đang hạ giọng ($\Delta y_k = y_k - \bar{y} < 0$). Tích số nhân chéo tại điểm này lập tức đổi dấu âm:
   $$(x_k - \bar{x})(y_k - \bar{y}) < 0$$
   Tích số âm này kéo tụt toàn bộ tử số hiệp phương sai, khiến hệ số tương quan tụt dốc thành số âm ($r < 0 < 0{,}3$). Hệ thống lập tức đánh trượt oan người học và kết án sai hàng loạt từ lân cận do quy tắc gối đầu, dù ngữ điệu của người học hoàn toàn tự nhiên và chuẩn xác.

3. **Bẫy ngân nga (The Humming Trap: $F_0$ mù formant âm vị):**  
   Định luật âm học phân tách độc lập nguồn phát âm (dao động dây thanh tạo ra tần số cơ bản $F_0$) và bộ lọc thanh đạo (các cộng hưởng formant $F_1, F_2, F_3$ tạo nên bởi vị trí của lưỡi, môi và ngạc mềm). Hệ số tương quan Pearson trên cao độ chỉ đo đạc sự căng chùng cùng hướng của dây thanh, hoàn toàn mù tịt trước đường bao formant phổ.  
   Nếu một người học **ngậm chặt miệng và ngân nga** (*humming*) theo giai điệu lên xuống của câu mà không mở miệng phát âm, hoặc đọc một câu sai hoàn toàn âm vị nhưng có cùng ngữ điệu trần thuật, quỹ đạo $F_0$ vẫn bám khít mẫu chuẩn và đạt hệ số tương quan rất cao (ví dụ minh họa: $r \approx 0{,}98$ trong trường hợp ngân nga khớp giai điệu, lưu ý đây là ví dụ minh họa toán học, không phải số đo thực nghiệm của Sarah). Thuật toán đường cơ sở sẽ cấp điểm đạt tuyệt đối cho một câu nói hoàn toàn không chứa bất kỳ âm vị tiếng Anh hợp lệ nào.

> 💡 **NHÌN THẤY VẬT LÝ**  
> Co giãn thời gian tuyến tính giả định ngây thơ rằng con người nói chuyện như một máy hát đĩa quay đều. Đánh giá phát âm chỉ dựa vào $F_0$ mắc kẹt trong ảo ảnh của nguồn âm thanh, mù trước bộ lọc thanh đạo và biến một tiếng ngậm miệng ngân nga thành một bài đọc hoàn hảo.

---

### Hộp 3: Không gian lựa chọn: Ba hướng kiến trúc (Không tuyên bố thắng)

Trước những giới hạn vật lý của đường cơ sở tuyến tính, nhóm nghiên cứu đứng trước ba hướng đi kiến trúc với những bài toán đánh đổi rõ rệt; chúng ta phân tích khách quan cả ba hướng mà không tuyên bố phương án nào thắng cuộc:

- **Hướng 1: Pearson pitch như nhóm (Đường cơ sở co giãn tuyến tính)**
  - *Được:* Chi phí tính toán cực kỳ nhỏ, chỉ gồm vài phép nhân cộng vô hướng và không đòi hỏi bất kỳ bộ nhớ nào để lưu trữ trọng số mô hình.
  - *Mất:* Rất dễ sụp đổ trước sự biến thiên nhịp điệu cục bộ của người học và hoàn toàn bất lực trong việc phát hiện các lỗi phát âm sai âm vị.

- **Hướng 2: DTW trên riêng $F_0$ (Co giãn thời gian phi tuyến trên chuỗi cao độ)**
  - *Được:* Hấp thụ trọn vẹn hiện tượng kéo dài nguyên âm cục bộ bằng cách nén dãn đàn hồi để khớp đúng các đỉnh cao độ tương ứng giữa hai tín hiệu.
  - *Mất:* Vẫn hoàn toàn mù trước cấu trúc formant âm học và gặp bế tắc toán học tại các khoảng thời gian vô thanh nơi cao độ không tồn tại.

- **Hướng 3: DTW trên 80 dải log-Mel để khóa biên âm, rồi tính Pearson pitch dọc đường co giãn**
  - *Được:* Tận dụng trực tiếp 80 dải năng lượng Mel từ tầng tiền xử lý để căn chỉnh chính xác từng ranh giới âm vị và phụ âm, sau đó so khớp cao độ dọc theo đúng quỹ đạo đàn hồi.
  - *Mất:* Đòi hỏi khối lượng tính toán ma trận quy hoạch động hai chiều lớn hơn và cần thiết kế kiến trúc đường ống xử lý dữ liệu phức tạp hơn trên phần cứng.

**Nguyên tắc trung lập:** Cả ba hướng tiếp cận đều đại diện cho các phương án kỹ thuật thực tế với những đánh đổi xác định; không có phương án nào là hoàn hảo tuyệt đối mà không có sự đánh đổi phần cứng, và chúng ta không gọi Hướng 3 là kiến trúc đã chốt của sách. Quyết định lựa chọn thuộc về sự cân nhắc tập thể của nhóm nghiên cứu dựa trên ngân sách tài nguyên và mục tiêu sản phẩm.

| Đặc tính đánh giá | Hướng 1: Tuyến tính nhóm | Hướng 2: DTW trên $F_0$ | Hướng 3: DTW Mel + Pitch |
| :--- | :--- | :--- | :--- |
| **Bảo tồn ý tưởng cơ sở** | Giữ nguyên $100\%$ đường cơ sở | Giữ nguyên $75\%$ (thay phép co) | Giữ nguyên $50\%$ (kết hợp phổ) |
| **Hấp thụ lệch nhịp cục bộ** | Kém (dễ đảo pha âm $r < 0$) | Tốt (nén dãn đàn hồi theo $F_0$) | Xuất sắc (khóa theo ranh giới âm vị) |
| **Khả năng bắt bẫy ngân nga** | Mù hoàn toàn ($F_0$ không formant) | Mù hoàn toàn ($F_0$ không formant) | Bắt được (dựa trên 80 dải log-Mel) |
| **Xử lý đoạn vô thanh** | Khó khăn ($F_0 = 0$ làm sai lệch) | Cần mặt nạ hữu thanh bổ trợ | Xử lý tự nhiên qua đặc trưng phổ |
| **Gánh nặng tính toán** | Cực nhẹ (phép toán vô hướng) | Trung bình (ma trận DTW 1D) | Cao hơn (ma trận quy hoạch động 2D) |

> 💡 **PHÁT HIỆN THEN CHỐT**  
> Đánh giá phát âm là bài toán căn chỉnh âm học thực nghiệm, không phải suy luận phiên âm xác suất. Ranh giới giữa một bài đọc đạt chuẩn và một tiếng ngậm miệng ngân nga chỉ có thể được phân định khi hệ thống tích hợp cả năng lượng phổ Mel để khóa ranh giới âm vị lẫn quỹ đạo cao độ đàn hồi để đo đạc ngữ điệu.

---

### Cầu nối sang chương sau

Đường co giãn đàn hồi phi tuyến này chính là đối tượng tính toán sẽ được ánh xạ lên mạch phần cứng ở các chương tiếp theo, việc thiết kế vi kiến trúc phần cứng chưa thực hiện tại đây.
