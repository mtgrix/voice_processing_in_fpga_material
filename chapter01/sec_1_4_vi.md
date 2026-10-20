# 1.4 Hệ quả phần cứng và giới hạn trễ xử lý

#### Cầu nối tự nhiên từ Mục 1.3: Ánh xạ phương trình lên các bóng bán dẫn vật lý

Trong Mục 1.3, chúng ta đã hoàn thành việc quan sát dưới kính hiển vi toán học toàn bộ chuỗi xử lý DSP đầu vào, chuyển hóa 400 mẫu áp suất liên tục thành 80 giá trị phổ Log-Mel. Tuy nhiên, một thuật toán trên trang giấy luôn giả định bộ nhớ vô hạn và thời gian thực thi bằng không. Trong mục này, chúng ta buộc các phương trình trừu tượng đó phải va chạm trực tiếp với silicon vật lý: đánh giá cách các tham số toán học chuyển dịch thành dấu chân bộ nhớ và hạn chót xử lý giữa một GPU biên (Edge GPU) và fabric phần cứng không gian (Spatial FPGA fabric trên AMD Xilinx Kria KV260).

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì xem độ trễ phần cứng là một khoảng trì hoãn tính toán tùy tiện, mục này neo chặt thời gian xử lý vào quá trình tích lũy âm học vật lý, đối chiếu sự phân bổ Block RAM trên chip với băng thông bộ nhớ ngoài, và làm sáng tỏ tại sao việc chuyển đổi tầng tiền xử lý âm thanh sang logic FPGA lại bắt nguồn từ khả năng thực thi tất định và cách ly phần cứng không rung pha, chứ không phải vì thông lượng số học thô.

---

### Trạng thái 1: Sàn trễ vật lý

Độ trễ trong một hệ thống âm thanh dòng (streaming audio) sở hữu một giới hạn chặn dưới vật lý tuyệt đối được ấn định bởi thời gian gom mẫu trên màng mic trước khi bất kỳ con chip bán dẫn nào được cấp nguồn. Ba đại lượng thời gian được khóa chặt vĩnh viễn bởi đặc tả âm học của tầng đầu vào:

| Tham số | Giá trị số | Nguồn gốc toán học & Định nghĩa vật lý |
| :--- | :--- | :--- |
| Sàn tích lũy khung đầu tiên | $25\text{ ms}$ | $L / f_s = 400 / 16.000$ (Thời gian màng micro hứng áp suất âm thanh vật lý) |
| Nhịp bước giữa các khung | $10\text{ ms}$ | $H / f_s = 160 / 16.000$ (Khoảng phát định kỳ sang mô hình nơ-ron kế tiếp) |
| Tỷ lệ gối đầu giữa các khung | $60\%$ | $(L - H) / L = 240 / 400$ (Ngữ cảnh lịch sử chung giữ liền mạch năng lượng biên) |

Thực tế âm học này thiết lập một sàn trễ tuyệt đối không thể phá vỡ: **Khung 0 về mặt vật lý hoàn toàn không thể tồn tại** trước khi màng rung của micro hứng đủ $25\text{ ms}$ dao động sóng áp suất không khí liên tục. Ngay cả một bộ xử lý lý thuyết cực nhanh với thời gian tính toán tiệm cận 0 nano giây ($t_{\text{xử lý}} \to 0$) cũng không thể phát ra vector đặc trưng đầu tiên trước thời điểm $t = 25\text{ ms}$, bởi vì mẫu âm thanh thứ 400 đơn giản là chưa hề xảy ra trong thực tại vật lý.

```
+-----------------------------------------------------------------------------+
| Hình 1.4a: Sàn trễ âm học vật lý                                             |
| Khung 0 bắt buộc phải tích lũy đủ 25 ms (400 mẫu) dao động áp suất trên      |
| màng rung micro trước khi bất kỳ bộ xử lý nào có thể phát ra vector đặc      |
| trưng đầu tiên.                                                             |
| Callout: Khung 0 không tồn tại trước 25 ms vì mẫu 400 chưa tới.             |
+-----------------------------------------------------------------------------+
```

Một khi sàn tích lũy $25\text{ ms}$ ban đầu được thỏa mãn, hệ thống bước vào chế độ vận hành ổn định (steady-state). Kể từ đây, cứ sau mỗi $10\text{ ms}$, micro lại cung cấp thêm một khối mới gồm đúng $H = 160\text{ mẫu}$ âm thanh. Khoảng thời gian $10\text{ ms}$ này chính là **hạn chót thời gian thực cứng (hard real-time deadline)**: toàn bộ các bước tính toán tiếp theo—áp cửa sổ Hamming, biến đổi 512-điểm FFT, tính phổ công suất, lọc 80 kênh Mel, nén logarit, và suy luận mô hình nơ-ron—phải hoàn tất xong xuôi trong vòng $10\text{ ms}$. Một bộ xử lý nhanh hơn không hề thu nhỏ được sàn vật lý $25\text{ ms}$; nó chỉ đơn thuần ngăn không cho độ trễ tính toán bị chồng chất thêm lên trên sàn âm học đó.

---

### Trạng thái 2: Dấu chân bộ nhớ trên silicon vật lý

Để đánh giá tính khả thi vật lý, chúng ta đối chiếu nhu cầu bộ nhớ của tầng tiền xử lý với tài nguyên bộ nhớ nội bộ Block RAM trên chip của MPSoC Zynq UltraScale+ `XCK26` (bo mạch AMD Kria KV260).

Bây giờ hãy đối chiếu tài nguyên này với hai cấu trúc trạng thái cốt lõi mà tầng tiền xử lý DSP dòng phải duy trì ở định dạng dấu phẩy động 32-bit (FP32):

1. **Bộ đệm vòng âm thanh ($400\text{ mẫu}$)**: Với $4\text{ byte}$ mỗi mẫu, việc lưu trữ lịch sử âm học đang chạy đòi hỏi $400 \times 4\text{ B} = 1.600\text{ byte} = 1.600\text{ B}$. Một khối Block RAM $36\text{-kbit}$ duy nhất cung cấp tới $4.608\text{ byte}$ dung lượng hai cổng (dual-port). Do đó, toàn bộ trạng thái miền thời gian chỉ chiếm đúng **$34{,}7\%$ dung lượng của một khối BRAM** ($0{,}2\%$ tổng BRAM trên chip).
2. **Ma trận trọng số bộ lọc Mel ($80 \times 257$)**: Việc lưu trữ ma trận trọng số tam giác ở dạng dày đặc đòi hỏi $80 \times 257 \times 4\text{ B} = 82.240\text{ byte} = 80{,}3\text{ KiB}$. Toàn bộ ma trận hệ số này cần $18$ khối Block RAM, chiếm đúng **$12{,}4\%$ tổng BRAM trên chip**.
3. **Khoảng trống bộ nhớ cho mô hình nơ-ron ($87{,}4\%$)**: Hai khối trên chỉ chiếm tổng cộng $12{,}6\%$ BRAM trên chip ($81{,}9\text{ KiB}$). Do đó, phần cứng còn nguyên **$87{,}4\%$ Block RAM** ($566{,}1\text{ KiB}$) hoàn toàn tự do dành riêng cho các trọng số của mô hình mạng nơ-ron âm học.

> 💡 **NHÌN THẤY VẬT LÝ**  
> Bởi vì tổng dấu chân bộ nhớ của trạng thái đầu vào và ma trận Mel ($80{,}3\text{ KiB} + 1{,}6\text{ KiB} = 81{,}9\text{ KiB}$) chiếm chưa đầy $13\%$ Block RAM trên chip, toàn bộ pipeline DSP nằm gọn hoàn toàn bên trong bộ nhớ SRAM nội bộ của FPGA. Do đó, bộ đệm và ma trận Mel không cần DDR, triệt tiêu hoàn toàn sự tranh chấp bus, hiện tượng nghẽn do chu kỳ làm tươi DRAM (refresh stall), và tiêu hao năng lượng truyền dẫn qua bus ngoài.

---

### Trạng thái 3: Ảo tưởng số học — Thông lượng so với Cách ly tất định

Việc tính toán bộ lọc Mel 80 kênh đòi hỏi nhân 257 bin phổ công suất với 80 vector trọng số tam giác:
$$\text{Khối lượng mỗi khung} = 80 \times 257 = 20.560\ \text{phép tính nhân-tích lũy (MAC)}$$

Tại nhịp bước $10\text{ ms}$ ($H/f_s = 160 / 16.000$), tầng tiền xử lý tạo ra $100\text{ khung/giây}$ ($1 / 0{,}01\text{ s}$), dẫn đến thông lượng tính toán gộp:
$$\text{Thông lượng} = 20.560\ \text{MAC/khung} \times 100\ \text{khung/giây} = 2.056.000\ \text{MAC/giây} \approx 2{,}06\ \text{MMAC/s}$$

```
+-----------------------------------------------------------------------------+
| Hình 1.4b: Phân bổ bộ nhớ BRAM trên KV260 và tính tất định đường truyền      |
| Panel (a): Phân bổ BRAM trên chip với 3 con số:                              |
|   - 1.600 byte: Bộ đệm vòng âm thanh (400 mẫu FP32)                         |
|   - 80,3 KiB: Ma trận trọng số Mel (80 x 257 FP32)                           |
|   - 87,4%: Phần BRAM còn lại cho mô hình nơ-ron                              |
| Panel (b): Đường thực thi GPU biên so với FPGA:                              |
|   - Đường GPU biên: Bị ngắt HĐH & hàng đợi driver -> rung pha trễ Δt > 0     |
|   - Đường FPGA: Đường dây silicon chuyên dụng không bị ngắt -> tất định Δt=0 |
+-----------------------------------------------------------------------------+
```

So với năng lực của các bộ gia tốc biên hiện đại như Edge GPU, con số $2{,}06\text{ MMAC/s}$ là cực kỳ khiêm tốn. Các bộ xử lý GPU biên sở hữu năng lực xử lý dấu phẩy động khổng lồ, vượt trội hơn rất nhiều lần so với nhu cầu tính toán của chuỗi phép tính này.

Sự chênh lệch này vạch trần một chân lý kiến trúc cốt lõi: **chuyển tầng tiền xử lý âm thanh lên logic FPGA không bao giờ bắt nguồn từ nhu cầu thông lượng số học thô**. Động lực thực sự của việc chuyển đổi hoàn toàn nằm ở **tính tất định thời gian và sự cách ly phần cứng hoàn toàn (deterministic hardware isolation)**:

- **Bẫy phần mềm dùng chung (Edge GPU)**: Trên hệ thống CPU/GPU biên, tầng tiền xử lý âm thanh phải chia sẻ cửa sổ $10\text{ ms}$ với nhân hệ điều hành Linux, các ngắt driver DMA thu âm từ micro, các tiến trình mạng nền và hàng đợi khởi chạy kernel tính toán. Sự tranh chấp tài nguyên và chuyển đổi ngữ cảnh ngẫu nhiên giữa các lớp phần mềm bất đồng bộ khiến độ trễ luôn chịu sự rung pha thời gian ($\Delta t_{\text{rung pha}} > 0$).
- **Fabric không gian chuyên dụng (FPGA)**: Trên FPGA, pipeline DSP được thiết kế hoàn toàn bằng các đường dây silicon và thanh ghi chuyên dụng, được cách ly vật lý tuyệt đối. Phần cứng không dùng chung xung nhịp hay đường ống thực thi với bất kỳ hệ điều hành nào. Tầng tiền xử lý hoàn tất mỗi khung âm thanh trong đúng một số chu kỳ xung nhịp cố định ($N_{\text{clk}}$), bảo đảm độ rung pha thời gian bằng đúng 0 nano giây ($\Delta t = 0\text{ ns}$).

> 💡 **PHÁT HIỆN THEN CHỐT**  
> FPGA không đánh bại GPU biên về thông lượng số học thô; nó vượt trội hoàn toàn về khả năng cách ly tất định. Các đường dây silicon chuyên dụng bảo đảm thời gian thực thi không trôi pha trong hạn chót cứng 10 ms của mỗi nhịp bước, hoàn toàn độc lập với sự chiếm quyền của hệ điều hành và sự tranh chấp tài nguyên bộ nhớ.

---

### Cầu nối tự nhiên sang Mục 1.5: Thử nghiệm ứng suất tại ranh giới phần cứng

Chúng ta đã chứng minh rằng pipeline tiền xử lý dòng ánh xạ cực kỳ hiệu quả lên tài nguyên vật lý của FPGA—chiếm dụng dung lượng Block RAM khiêm tốn ($12{,}6\%$) và bảo đảm tính tất định trễ tuyệt đối.

Tuy nhiên, các công thức toán học luôn tiềm ẩn những điểm gãy đổ thảm khốc khi bị ép vượt qua giới hạn hoạt động danh định. Điều gì xảy ra nếu người thiết kế cố giảm độ trễ bằng cách cắt ngắn độ dài cửa sổ? Điều gì xảy ra nếu tín hiệu âm thanh được lấy mẫu ở chuẩn phòng thu ($48\text{ kHz}$)? Điều gì xảy ra nếu hệ thống lưu ma trận dày đặc thay vì nén thưa? Trong Mục 1.5, chúng ta sẽ đưa các mô hình lý thuyết vào bốn kịch bản thử nghiệm ứng suất nghiêm ngặt, trực tiếp khảo sát nơi mà silicon biên bị bẻ gãy khi chạm tới giới hạn vật lý.
