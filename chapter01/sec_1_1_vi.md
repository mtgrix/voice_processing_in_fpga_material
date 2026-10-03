## 1.1 Trực Giác: Sự Khác Biệt Cốt Lõi Giữa Thị Giác Máy Tính và AI Giọng Nói Biên

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì xem xử lý âm thanh như một chuỗi ma trận số học trong hộp đen, mục này dẫn dắt bạn đi qua cơ chế vật lý và cơ học của sóng âm. Chúng ta sẽ suy diễn vì sao xử lý giọng nói phân kỳ căn bản so với thị giác máy tính, lý do độ trễ biên bắt buộc kích thước lô thực thi phải bằng một ($batch=1$), và cách quán tính sinh học của các cơ quan phát âm định hình ranh giới khung thời gian thực cho mọi kiến trúc silicon được phát triển trong cuốn sách này.

### Bức Ảnh Trong Phòng Trưng Bày và Màng Rung Của Micro

Một bức ảnh là một thực thể đã hoàn thành. Một âm thanh là một quá trình vật lý chưa kết thúc.

Sự phân biệt duy nhất này chi phối gần như mọi đánh đổi kiến trúc trong toàn bộ cuốn sách. Trong thị giác máy tính, một bức ảnh số truyền đến bộ xử lý dưới dạng một ma trận không gian nguyên vẹn, có giới hạn rõ ràng. Các điểm ảnh ở mép dưới tồn tại tại cùng một thời điểm chính xác như các điểm ảnh ở mép trên. Xử lý bức ảnh thứ hai không làm thay đổi thực tại không gian của bức ảnh thứ nhất; bạn có thể xếp chồng tám bức ảnh lại với nhau thành một lô duy nhất và đưa chúng đồng thời qua mạng nơ-ron.

Việc nhóm các đầu vào độc lập theo cách này được gọi là **gom lô** (batching), và số lượng mẫu được nhóm lại đại diện cho **kích thước lô** ($B$ – batch size). Một bộ xử lý đồ họa (GPU) — được xây dựng từ hàng nghìn luồng thực thi số học nhẹ vận hành đồng bộ — thực hiện một phép nhân ma trận lớn hiệu quả hơn rất nhiều so với khi phải thực hiện tám phép nhân nhỏ rời rạc. Trên GPU máy tính để bàn hoặc đám mây, việc gom lô mang lại lợi thế thông lượng to lớn gần như miễn phí. Cái giá duy nhất phải đánh đổi là sự kiên nhẫn — và một bức ảnh tĩnh nằm yên trong bộ nhớ không hề có một thời hạn đếm ngược nào.

Tín hiệu giọng nói dạng dòng (streaming) mang một thực tại vật lý hoàn toàn trái ngược. Dữ liệu âm học không xuất hiện như một khung vẽ hai chiều hoàn chỉnh; nó truyền đến dưới dạng một dòng mẫu áp suất không khí liên tục được đo bởi màng rung dao động của micro. Để tập hợp một lô gồm tám khung âm thanh, hệ thống xử lý không thể tự tạo ra các mẫu tương lai từ hư không. Nó bị buộc về mặt vật lý phải giữ khung âm thanh đầu tiên nằm chờ trong hàng đợi cho đến khi khung thứ tám hoàn tất việc dao động qua không khí và đi qua bộ chuyển đổi tương tự – số.

::: {#fig-1-1a-cv-vs-voice .figure}
```tikz
\input{chapter01/fig_1_1a_vi.tex}
```
Hình 1.1a: Sự phân kỳ vật lý và hình học giữa thị giác máy tính không gian và AI giọng nói biên dạng dòng cho thấy dữ liệu âm thanh diễn tiến tuần tự theo thời gian khiến việc gom lô bắt buộc phải trả giá bằng việc giữ khung âm thanh nằm chờ.
:::

**Độ trễ** ($\tau$) — khoảng thời gian vật lý trôi qua từ thời điểm sóng áp suất âm thanh chạm vào micro đến thời điểm bộ xử lý biên đưa ra quyết định ngôn ngữ khả thi — không phải là một chỉ số đo lường trừu tượng của phần mềm. Trong một hệ thống dòng tương tác, việc gom lô không bao giờ miễn phí: mỗi phần tử bổ sung vào lô đều được đánh đổi trực tiếp bằng sự hy sinh độ trễ của người dùng.

---

### Hành Trình Suy Diễn: Thiết Lập Bài Toán Song Đề Gom Lô

Để hiểu vì sao kiến trúc giọng nói biên vận hành khác biệt so với các hệ thống thị giác, hãy xem xét hai giả thuyết đối lập mà một kỹ sư có thể đặt ra khi định cỡ bộ đệm đầu vào:

* **Giả thuyết A (Ngộ nhận thông lượng hàng loạt của GPU):** Việc gom lô được cho là mang lại gia tốc "miễn phí". Trong môi trường máy chủ hoặc xử lý ảnh tĩnh, việc nhóm tám đầu vào không tốn thêm thời gian chờ đợi nào vì mọi dữ liệu đều đã được nạp sẵn vào bộ nhớ hệ thống. Dưới giả định này, một kỹ sư có thể kỳ vọng rằng việc gom tám khung âm thanh trên bộ xử lý biên sẽ cải thiện hiệu suất tính toán mà không phải trả giá.
* **Giả thuyết B (Thực tại vật lý dạng dòng):** Âm thanh không nằm chờ sẵn trong bộ nhớ; nó được tạo ra bởi một người nói bằng xương bằng thịt diễn tiến liên tục theo thời gian. Để xử lý một lô gồm tám khung, phần cứng phải tạm dừng về mặt vật lý và chờ người nói phát ra các sóng âm tương lai.

Lời giải đáp xuất hiện ngay lập tức: Giả thuyết A sụp đổ vì nó nhầm lẫn giữa dữ liệu tồn tại trong không gian với dữ liệu mở ra theo thời gian. Trong âm thanh dạng dòng, gom lô không phải là hiệu năng miễn phí — nó được đánh đổi trực tiếp bằng độ trễ $\tau$.

Chúng ta có thể lượng hóa hình phạt vật lý này thành hai trạng thái cụ thể:

* **Trạng thái 1 — Hình phạt xếp hàng đầu vào:**  
  Giả sử tầng tiền xử lý âm học tạo ra một khung phân tích sau mỗi $T_h$ giây, trong đó $T_h$ đại diện cho **chu kỳ bước nhảy** (khoảng cách thời gian giữa hai cửa sổ phân tích liên tiếp). Nếu bộ máy suy diễn từ chối tính toán cho đến khi tập hợp đủ một lô gồm $B$ khung, thì khung đầu tiên được thu nhận sẽ phải nằm chờ hoàn toàn vô công trong bộ nhớ trong khi các khung $2, 3, \dots, B$ đang được ghi lại:
  
  $$\Delta t_{\text{wait}} = (B - 1) \, T_h$$
  
  Trong công thức này, $(B-1)$ đại diện cho số khoảng khung thời gian tiếp theo buộc phải trôi qua trong thế giới vật lý trước khi bộ đệm lô được tuyên bố là đã đầy.

* **Trạng thái 2 — Hình phạt độ trễ tại $B = 8$:**  
  Xuyên suốt cuốn sách này, quy trình xử lý tiếng nói biên tiêu chuẩn cố định chu kỳ bước nhảy tại $T_h = 10\text{ ms}$ (một tốc độ mà nguồn gốc sinh học của nó sẽ được suy dẫn ngay bên dưới). Nếu một nhà thiết kế hệ thống cố gắng vận hành bộ tăng tốc biên ở kích thước lô khiêm tốn là $B = 8$ để tăng hiệu quả sử dụng các luồng số học:
  
  $$\Delta t_{\text{wait}} = (8 - 1) \times 10\text{ ms} = 70\text{ ms}$$
  
  Hãy chú ý điều gì đã diễn ra: **$70\text{ ms}$ độ trễ thuần túy đã bị cộng thêm vào hệ thống trước khi một phép nhân đơn lẻ nào kịp bắt đầu.**  
  
  Hình phạt $70\text{ ms}$ này là hệ quả số học bất biến của chính sách gom lô, không phải là khuyết tật của chất lượng mã nguồn hay băng thông bus. Trong một bộ nhận dạng từ khóa thức tỉnh (Keyword Spotting – KWS) mang tính tương tác, $70\text{ ms}$ chính là ranh giới phân định giữa cảm giác tức thì và cảm giác giật cục, trì trệ.

::: {#fig-1-1b-batch-tax .figure}
```tikz
\input{chapter01/fig_1_1b_vi.tex}
```
Hình 1.1b: Hình phạt độ trễ số học do chính sách gom lô áp đặt lên dòng âm thanh cho thấy Khung 1 buộc phải nằm chờ vô công $(B-1)T_h = 70\text{ ms}$ trong bộ đệm đầu vào hoàn toàn độc lập với xung nhịp xử lý hay thông lượng tính toán.
:::

> 🎯 **PHÁT HIỆN THEN CHỐT**  
> Một giao diện giọng nói biên vận hành trước sự hiện diện vật lý của một người đang nói không thể tích lũy các đầu vào theo thời gian; để bảo toàn tính tương tác thời gian thực, hệ thống bị khóa chặt vào:
> 
> $$batch = 1$$
> 
> Câu hỏi thiết kế cốt lõi đối với kỹ sư kiến trúc phần cứng biên không phải là: *"Làm thế nào để tính toán một lô ma trận khổng lồ với thông lượng tối đa?"*  
> Mà là: *"Làm thế nào để thực thi MỘT khung đơn lẻ, gọn nhẹ đến khi hoàn tất trọn vẹn trong ngân sách mười mili giây, mang tính tất định, lặp lại liên tục mà không bao giờ bị tụt lại sau xung nhịp thời gian?"*

---

### Ba Phân Kỳ Vật Lý: Các Ràng Buộc Cơ Học Của Âm Thanh

Từ thực tế duy nhất rằng âm thanh truyền đến tuần tự trong chế độ $batch = 1$, ba hệ quả vật lý tất yếu xuất hiện; mỗi ràng buộc trực tiếp định hình một yêu cầu phần cứng trong các chương tiếp theo.

#### 1. Âm Thanh Không Có Ranh Giới Tự Nhiên (Mệnh Lệnh Trạng Thái Bộ Nhớ)
Một bức ảnh số bị giới hạn cứng nhắc bởi chiều cao $H$ và chiều rộng $W$ tính theo điểm ảnh hữu hạn. Một dạng sóng âm thanh dạng dòng không có cả hai: tiếng nói con người tiếp diễn liên tục vào tương lai, và bộ xử lý biên không thể quan sát toàn bộ tín hiệu trước khi bắt đầu công việc của mình.

Bởi vì bộ xử lý không thể nhìn trước tương lai, nó phải bắc cầu tính liên tục theo thời gian bằng cách lưu giữ ngữ cảnh quá khứ trong **trạng thái** (state) — một vùng bộ nhớ chuyên dụng, giới hạn chặt chẽ trên chip chứa những gì mà khung tiếp theo sẽ cần. 
* *Cầu nối phần cứng tới Chương 4:* Yêu cầu này thay đổi căn bản cách chúng ta định cỡ tài nguyên bán dẫn; khi triển khai các mô hình dạng dòng, câu hỏi *"Con chip sở hữu bao nhiêu đơn vị nhân tích lũy (MAC)?"* chỉ là thứ yếu so với câu hỏi kiến trúc sắc bén hơn nhiều: *"Cần bao nhiêu kilobit RAM khối (BRAM) hoặc UltraRAM (URAM) trên chip để duy trì trạng thái ngữ cảnh trái mà không bị đình trệ do truy xuất DRAM ngoài?"*

#### 2. Quán Tính Sinh Học Chi Phối Vùng Gối Khung (Mệnh Lệnh Bộ Đệm Vòng Trượt)
Vì sao các chuỗi xử lý âm học tiêu chuẩn luôn áp dụng bước nhảy khung $10\text{ ms}$? Câu trả lời nằm ở cơ sinh học của con người.

Đường phát âm của con người — bao gồm lưỡi, môi, vòm mềm, hầu họng và xương hàm dưới — là một tập hợp các mô sinh học có khối lượng vật lý. Bởi vì các cơ quan phát âm này mang quán tính cơ học, chúng không thể thay đổi hình học vật lý của mình một cách tức thời. Do đó, tiếng nói con người duy trì tính chất **chuẩn dừng** (quasi-stationary, tức ổn định về mặt thống kê trong bao hình phổ) trong các khoảng thời gian ngắn từ $20\text{ đến }30\text{ ms}$.

Để chụp lại một ảnh phổ tĩnh đáng tin cậy về mặt thống kê, tầng tiền xử lý số phải quan sát một cửa sổ thời gian dài $25\text{ ms}$ ($400\text{ mẫu}$ ở tần số lấy mẫu chuẩn $f_s = 16\text{ kHz}$). Tuy nhiên, để theo dõi chính xác các biến chuyển ngữ âm nhanh giữa các âm tắc, âm xát và nguyên âm, cửa sổ phân tích phải tịnh tiến theo các bước nhảy nhỏ $T_h = 10\text{ ms}$ ($160\text{ mẫu}$).

Thực tế sinh học này tạo ra một hệ quả cơ học trực tiếp: **hai khung liên tiếp gối chồng sâu lên nhau**. Trong số 400 mẫu cấu thành khung phân tích hiện tại:

$$400 - 160 = 240\text{ mẫu}$$

đã được thu nhận, đệm và phân tích trong khung liền trước.

> 💡 **NHÌN THẤY VẬT LÝ**  
> Vùng gối chồng 240 mẫu giữa hai khung liên tiếp không phải là gánh nặng dư thừa; đó là một cơ hội kiến trúc mang tính cấu trúc. Trong phần mềm thông thường, việc trượt một mảng thường kích hoạt các thao tác sao chép bộ nhớ tốn kém (`memmove`). Trên FPGA, các khối RAM (BRAM) chuyên dụng trên chip cho phép các con trỏ địa chỉ đọc và ghi tịnh tiến tuần hoàn quanh một bộ đệm vòng cố định, cung cấp khung gối chồng cho chuỗi DSP mà không tốn công sao chép dữ liệu và không gây tắc nghẽn bus (được hình thức hóa ở Mục 1.2 và kiểm chứng trên silicon ở Chương 4 và 9).

#### 3. Đồng Hồ Của Tự Nhiên Không Thể Thương Lượng (Khủng Hoảng Mất Mẫu)
Màng rung cơ học của micro không bao giờ ngừng dao động chỉ vì một nhân CPU ở hạ nguồn đang bận phục vụ ngắt hệ điều hành hay gặp hiện tượng trượt bộ nhớ đệm (cache miss).

Trong thị giác máy tính, một hàng đợi xử lý bị nghẽn chỉ đơn thuần làm chậm thời điểm hoàn thành một khung ảnh tĩnh thêm vài mili giây; các điểm ảnh vẫn nằm nguyên vẹn trong bộ nhớ. Trong âm thanh dạng dòng, một hàng đợi không được phục vụ kịp thời sẽ khiến bộ đệm đầu vào bị tràn, dẫn đến hiện tượng **mất mẫu** (dropped samples). Bởi vì dạng sóng âm học là một chuỗi thời gian liên tục và không thể đảo ngược, một mẫu âm thanh bị rơi sẽ vĩnh viễn biến mất; nó không bao giờ có thể lấy lại hay tính toán bù. Trên một đường ống giọng nói biên, ngân sách khung $10\text{ ms}$ không phải là một mục tiêu tối ưu hóa tùy chọn; đó là một thời hạn vật lý bất khả thương lượng.

---

### Định Nghĩa Lại "Tốc Độ": Thông Lượng so với Độ Trễ Khung Tất Định

Ba ràng buộc cơ học này thúc đẩy một sự chuyển dịch sâu sắc trong cách một kỹ sư định nghĩa tốc độ tính toán.

Một bộ tăng tốc thị giác máy tính được đánh giá bằng **thông lượng** — tổng số lượng ảnh được xử lý mỗi giây dưới tải gom lô cao. Trái lại, một bộ tăng tốc giọng nói biên thời gian thực được đánh giá trước hết và trên hết bởi **độ trễ thực thi tất định**: liệu cỗ máy xử lý có bảo đảm rằng mỗi khung đơn lẻ đều hoàn thành toàn bộ chuỗi trích xuất và phân loại nằm gọn trong hạn định vật lý $10\text{ ms}$, từ chu kỳ này sang chu kỳ khác với độ biến thiên bằng không hay không. Chỉ sau khi giao ước thời gian này được đảm bảo, thiết kế mới tối ưu hóa cho **hiệu quả năng lượng trên từng khung** ($\text{mJ/khung}$).

Lý do chính khiến GPU truyền thống không phải là cỗ máy tự nhiên cho giọng nói biên thời gian thực không nằm ở sự thiếu hụt sức mạnh số học thô. Thay vào đó, diện tích silicon của nó được tối ưu hóa cho một chỉ số — thông lượng song song khối lớn qua các lô rộng — mà một hệ thống dạng dòng tương tác ($batch = 1$) bị cấm sử dụng về mặt vật lý. Chương 3 phát triển lập luận này với các phép đo lường về những gì xảy ra với một bộ xử lý Đơn lệnh Nhiều luồng (SIMT) khi chỉ có duy nhất một khung để xử lý.

---

#### Thế Lưỡng Nan Chưa Có Lời Giải: Khủng Hoảng Thu Nhận Dạng Dòng

Nếu âm thanh truyền đến như một dòng mẫu áp suất không khí liên tục vô tận không thể gom lô mà không phải trả giá bằng độ trễ chí mạng, thì làm thế nào một bộ xử lý biên có thể biến một làn sóng liên tục vô hạn thành các gói toán học hữu hạn mà không làm mất mát thông tin hoặc tạo ra những biến dạng ranh giới nghiêm trọng?

Thế lưỡng nan vật lý này dẫn chúng ta trực tiếp tới cỗ máy toán học của chuỗi tiền xử lý dạng dòng trong Mục 1.2.
