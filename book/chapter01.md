# Chương 1: Chuỗi Tiền Xử Lý Tín Hiệu Âm Thanh & Trích Xuất Đặc Trưng: Từ Sóng Liên Tục Đến Log-Mel Spectrogram

> *Mục tiêu: Nắm vững bản chất chuỗi xử lý tín hiệu âm thanh liên tục (streaming audio), các ràng buộc độ trễ vật lý thời gian thực, và lý do vì sao các ứng dụng nhận thức giọng nói tại biên (edge voice) bắt buộc phải hoạt động ở chế độ kích thước lô bằng một ($batch=1$).*

---

> ### 📘 Toán học / Khái niệm Tối thiểu cho Chương này
> 
> - **Biến đổi Fourier Rời rạc (DFT)**: Phân rã phổ tín hiệu từ miền thời gian sang miền tần số.
> - **Nguyên lý Bất định Thời gian - Tần số (Heisenberg-Gabor)**: Sự đánh đổi giữa độ phân giải thời gian và độ phân giải tần số của cửa sổ phân tích.
> - **Thang đo Mel phi tuyến (Non-linear Mel Scale)**: Mô hình hóa cảm thụ cao độ của hệ thính giác người.

---

## Toàn bộ cỗ máy, trước khi mổ xẻ từng bộ phận

Mỗi phần tiếp theo trong chương này đều bảo vệ một luận điểm cốt lõi: một hệ thống xử lý giọng nói dạng dòng (streaming voice) không phải là một hệ thống thị giác máy tính chạy chậm; đó là một bài toán đo đạc hoàn toàn khác biệt về mặt bản chất. Luận điểm này sẽ sáng tỏ hơn rất nhiều khi ta quan sát toàn bộ cỗ máy trong tầm mắt trước tiên. [Hình 1](#fig-ch1-pipeline-contract) phác họa sơ đồ kiến trúc mà cuốn sách này sẽ liên tục quy chiếu. Các tầng xử lý mang tên gọi và thứ tự đồng nhất với bản đồ lộ trình của cuốn sách, và mỗi khối được gắn nhãn các chương nghiên cứu sâu về nó.

Những nhãn chương này được in trực tiếp nhằm phục vụ một mục đích sư phạm: thứ tự các chương trong sách là thứ tự kiến tạo thực tế, không phải thứ tự trình chiếu thụ động. Chương 4 bàn về cấu trúc logic phần cứng (fabric), nhưng Chương 4 phải đứng sau các chương tiền xử lý đầu vào vì người kỹ sư cần một khung tín hiệu hoàn chỉnh trước khi tìm nơi bố trí nó trên silicon. Một người đọc nếu cảm thấy lạc hướng ở bất kỳ đâu trong tập sách này chỉ cần tự đặt một câu hỏi duy nhất để quay lại mạch tư duy: **đây là tầng xử lý nào trong chuỗi tín hiệu?**

::: {#fig-ch1-pipeline-contract .figure}
```tikz
% Toàn bộ lộ trình của một khung tín hiệu, vẽ dưới dạng các giao ước dữ liệu:
% cái gì vượt qua từng ranh giới, trạng thái nào phải tồn tại giữa các khung, và hạn chót xung nhịp nằm ở đâu.
\begin{tikzpicture}[
  font=\scriptsize,
  stg/.style={draw, align=center, inner sep=3pt, minimum width=1.75cm, minimum height=9mm},
  mob/.style={stg, fill=black!7},
  art/.style={text=black!62, align=center, inner sep=0pt, text width=1.85cm, font=\tiny},
  own/.style={text=black!55, align=center, inner sep=0pt, text width=1.9cm, font=\tiny},
  mem/.style={draw, densely dashed, rounded corners=1.5pt, align=center, inner sep=3pt,
              text width=4.2cm, minimum height=6.5mm, text=black!75},
  arr/.style={-{Stealth[length=1.8mm]}, semithick},
  par/.style={-{Stealth[length=1.4mm]}, black!55, thin, densely dashed}]
\node[stg] (s1) at (0,0) {Không khí \&\\ micrô};
\node[stg] (s2) at (2.15,0) {Dòng mẫu\\ âm thanh};
\node[stg] (s3) at (4.3,0) {Khối DSP\\ front end};
\node[mob] (s4) at (6.45,0) {Mô hình\\ nơ-ron};
\node[mob] (s5) at (8.6,0) {Logic phần cứng\\ Fabric};
\node[mob] (s6) at (10.75,0) {Đầu ra \&\\ độ trễ};
\draw[arr] (s1) -- node[art, midway, above=1.2mm] {các mẫu số} (s2);
\draw[arr] (s2) -- node[art, midway, above=1.2mm] {khung tín hiệu\\ \& bước nhảy} (s3);
\draw[arr] (s3) -- node[art, midway, above=1.2mm] {vector đặc trưng\\ cố định} (s4);
\draw[arr] (s4) -- node[art, midway, above=1.2mm] {kích hoạt\\ nơ-ron} (s5);
\draw[arr] (s5) -- node[art, midway, above=1.2mm] {quyết định\\ nhận dạng} (s6);
\node[own, anchor=north] at ($(s1.south)+(0,-1.3mm)$) {ch. 6\\ ch. 8};
\node[own, anchor=north] at ($(s2.south)+(0,-1.3mm)$) {ch. 4\\ ch. 8};
\node[own, anchor=north] at ($(s3.south)+(0,-1.3mm)$) {ch. 1\\ ch. 6};
\node[own, anchor=north] at ($(s4.south)+(0,-1.3mm)$) {Phụ lục A\\ ch. 7\\ ch. 9};
\node[own, anchor=north] at ($(s5.south)+(0,-1.3mm)$) {ch. 4, 5\\ ch. 8};
\node[own, anchor=north] at ($(s6.south)+(0,-1.3mm)$) {ch. 2, 3\\ ch. 10};
\node[mem] (m1) at ($(s2.south)!0.5!(s3.south)+(0,-1.5cm)$)
  {cửa sổ mẫu trượt\\ lưu giữ giữa các khung, dịch theo bước nhảy};
\node[mem] (m2) at ($(s4.south)!0.5!(s5.south)+(0,-1.5cm)$)
  {ngữ cảnh quá khứ (left context) mô hình cần\\ khóa (keys) và giá trị (values), từng khối};
\draw[par] (m1.north) -- ($(s2.south)!0.5!(s3.south)$);
\draw[par] (m2.north) -- ($(s4.south)!0.5!(s5.south)$);
\coordinate (dl) at ($(s3.north west)+(0,-3.2cm)$);
\coordinate (dr) at ($(s6.north east)+(0,-3.2cm)$);
\draw[black!55, thin] (dl) -- ++(0,-2.5mm) (dr) -- ++(0,-2.5mm)
  ($(dl)+(0,-2.5mm)$) -- ($(dr)+(0,-2.5mm)$);
\node[art, text width=6.6cm] at ($(dl)!0.5!(dr)+(0,-5.2mm)$)
  {chu kỳ một khung hình: cùng một hạn chót, ở mọi tầng, trên cả hai bo mạch};
\end{tikzpicture}
```
Hai hộp nét đứt chính là sự khác biệt bản chất giữa cỗ máy xử lý tiếng nói và cỗ máy chụp ảnh tĩnh. Một bức ảnh khi xuất hiện là đã trọn vẹn và không cần ghi nhớ bức ảnh trước đó; trong khi một khung âm thanh bước vào một cửa sổ mẫu trượt bắt buộc phải được lưu giữ trong bộ nhớ, và một mô hình nơ-ron đọc lịch sử chuỗi phải lưu giữ trạng thái đó khối này qua khối khác chừng nào bo mạch còn được cấp điện. Việc mang theo trạng thái liên tục giữa các khung hình, chứ không phải độ lớn của các phép tính số học, là điểm phân kỳ giữa hai trường phái thiết kế — đó là lý do vì sao cửa sổ trượt ở Phần 1.2 và bộ đệm xoay vòng ở Chương 9 thực chất là một ý tưởng duy nhất được soi chiếu ở hai tầng sâu của chuỗi thực thi.
:::

**Những gì vượt qua từng ranh giới.** Mỗi tầng xử lý chuyển giao cho tầng tiếp theo một đối tượng có kích thước và khuôn dạng hình học cố định, và chính hình dạng cố định này cho phép từng tầng có thể thay thế độc lập. Đó là lý do toàn bộ việc chuyển đổi kiến trúc trong cuốn sách này có thể được tiến hành từng tầng một thay vì phải đập đi xây lại toàn bộ cùng lúc.

- **Từ không khí sang các mẫu số.** Micrô và bộ mã hóa ADC chuyển đổi áp suất âm thanh thành các con số rời rạc với tốc độ đều đặn. Khối tiền xử lý trong sách này vận hành ở tần số lấy mẫu chuẩn của các tập ngữ xơ huấn luyện, một sự tương thích bắt buộc do dữ liệu áp đặt chứ không phải do tùy hứng cá nhân, và Phần 1.2 sẽ giải thích lý do vật lý của nó.
- **Từ các mẫu số sang một khung hình.** Các con số âm thanh đổ về từng mẫu đơn lẻ nhưng quá trình giải tích quang phổ đòi hỏi một cụm dữ liệu cố định, do đó dòng tín hiệu được cắt thành các khung trượt gối đầu lên nhau (overlapping frames). Kích thước khung và bước nhảy giữa các khung chính là hai hạn chót thời gian đầu tiên mà mọi kiến trúc phần cứng thừa hưởng.
- **Từ khung hình sang vector đặc trưng.** Tần số cơ bản, ánh xạ thang đo cảm thụ thính giác, rồi nén logarit. Nhiệm vụ của khối DSP front-end là rút gọn một khung 400 mẫu thành một danh sách 80 con số cô đọng, và mọi lựa chọn ở Phần 1.3 đều xoay quanh việc giảm chiều dữ liệu bao nhiêu và vào thời điểm nào.
- **Từ đặc trưng sang điểm số xác suất.** Mạng nơ-ron đọc vector đặc trưng và trả về điểm số xác suất cho từng âm vị hoặc từ khóa cần nhận diện. Tầng này đối với sách chỉ đơn thuần là phép tính nhân-cộng ma trận số học, điều mà Phụ lục A chứng minh và Chương 7 quyết định độ rộng bit lượng tử hóa.
- **Từ điểm số sang quyết định.** Lớp ra chọn từ khóa chiến thắng và phát lệnh. Khi đó câu hỏi không còn là mạng nơ-ron đã tính toán điều gì, mà là sau bao nhiêu mili-giây kể từ khi âm thanh phát ra thì phản hồi được kích hoạt.

**Những gì mỗi tầng nợ xung nhịp đồng hồ.** Các chương sách được ghi chú trong sơ đồ; điều cần được khắc họa bằng lời là lời hứa về mặt thời gian của mỗi tầng, bởi chính lời hứa thời gian này, chứ không phải độ chính xác lý thuyết suông, là thước đo định cỡ toàn bộ kiến trúc phần cứng.

- **Không khí và micrô** cam kết cung cấp các bit dữ liệu theo đúng tốc độ lấy mẫu của bộ giải mã, liên tục, không có khoảng trễ bất thường nào phải giải trình sau đó.
- **Dòng mẫu âm thanh** cam kết cung cấp một khung trượt hoàn chỉnh trước hạn chót của nó, không có bất kỳ thao tác copy bộ nhớ nghẽn tắc nào cản trở dòng dữ liệu.
- **Khối DSP front-end** cam kết hoàn tất một vector đặc trưng Log-Mel trong vòng một chu kỳ khung hình (10 ms), bởi vì một khối tiền xử lý bị trễ hạn chót không chỉ làm chậm khung hiện tại, mà sẽ làm sụp đổ toàn bộ chuỗi khung phía sau. Phần 1.3 thực hiện các phép toán này và Chương 6 hiện thực hóa nó trên mạch logic.
- **Mô hình nơ-ron** cam kết số lượng phép đọc bộ nhớ và phép nhân-cộng (MAC) cố định cho mỗi khung, để các tầng phần cứng phía sau có thể định cỡ tài nguyên chính xác thay vì phỏng đoán.
- **Logic phần cứng (Fabric logic)** cam kết đóng chu kỳ xung nhịp (timing closure) và xử lý dứt điểm một khung hình trong mỗi chu kỳ khung tại tần số làm việc đó.
- **Đầu ra và độ trễ** cam kết đo lường thời gian trễ thực tế tính từ lúc sóng âm chạm màng micrô cho đến khi có phản hồi, thay vì chỉ đo thời gian thực thi của một hàm gọi phần mềm, bởi vì hai con số này chênh lệch nhau bởi toàn bộ độ trễ tích lũy của chuỗi tiền xử lý đầu vào.

> **Một thông số kế thừa định hình toàn bộ thiết kế.** Phần này nhắc đến một tần số lấy mẫu duy nhất: $f_s = 16\text{ kHz}$. Con số này được kế thừa từ các tập dữ liệu huấn luyện chuẩn mực quốc tế — cả bài báo Google Speech Commands lẫn trang phát hành tập dữ liệu LibriSpeech đều lưu trữ âm thanh ở 16 kHz. Cả hai nguồn đều phản ánh tiêu chuẩn lưu trữ của cộng đồng học thuật thế giới. Cuốn sách này xem sự tương thích 16 kHz là một ràng buộc thực tế mà dữ liệu áp đặt, không phải là một con số tùy tiện.

---

## 1.1 Trực giác: Sự Phân Kỳ Cốt Lõi Giữa Thị Giác Máy Tính và Voice AI

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì xem xử lý âm thanh như một chuỗi các ma trận số học trừu tượng, phần này thiết lập bản chất cơ học và vật lý của sóng âm. Chúng ta sẽ giải mã vì sao xử lý giọng nói phân kỳ sâu sắc với thị giác máy tính, tại sao áp lực độ trễ tại biên buộc hệ thống phải thực thi ở chế độ kích thước lô bằng một ($batch=1$), và quán tính sinh học của bộ máy phát âm con người đã ấn định các biên độ thời gian thực cho mọi kiến trúc bán dẫn trong cuốn sách này như thế nào.

Một bức ảnh là một đối tượng tĩnh đã hoàn tất. Một âm thanh là một quá trình vật lý chưa kết thúc.

Sự khác biệt căn bản đó giải thích hầu hết mọi lựa chọn kỹ thuật trong cuốn sách này. Mọi yếu tố — chu kỳ khung, bộ đệm xoay vòng, lựa chọn phần cứng FPGA thay vì GPU — đều bắt nguồn từ một thực tế vật lý: hình ảnh xuất hiện trọn vẹn trong một lần nạp, còn âm thanh xuất hiện nhỏ giọt từng mảnh theo thời gian.

Hãy quan sát cách một mô hình học sâu xử lý một bức ảnh. Một bức ảnh chứa đựng toàn bộ thông tin cần thiết. Việc xử lý bức ảnh thứ hai không hề làm thay đổi thông tin của bức ảnh thứ nhất, do đó ta có thể gom nhiều bức ảnh lại với nhau và xử lý đồng thời trong một bước tính toán. Việc nhóm các đầu vào như vậy gọi là **tạo lô (batching)**, và số lượng đầu vào trong nhóm là **kích thước lô (batch size)**. Một bộ xử lý đồ họa (GPU — gồm hàng ngàn làn tính toán số học đơn giản chạy đồng nhịp) thực hiện một phép tính ma trận lớn hiệu quả hơn rất nhiều so với việc thực hiện tám phép tính nhỏ lẻ tẻ, do đó gom lô trên GPU mang lại hiệu năng tính toán khổng lồ gần như miễn phí. Cái giá duy nhất phải trả là thời gian chờ đợi gom đủ dữ liệu, và không có người dùng nào đang phải chờ một bức ảnh tĩnh theo thời gian thực tương tác từng mili-giây.

Tín hiệu âm thanh thì hoàn toàn ngược lại. Dữ liệu đầu vào không xuất hiện nguyên khối; nó đến dưới dạng một dòng mẫu liên tục và không bao giờ ngừng lại. Để gom một lô gồm tám khung hình, hệ thống buộc phải giữ khung hình đầu tiên lại trong hàng đợi cho đến khi khung hình thứ tám được ghi âm xong từ màng micrô. **Độ trễ (Latency)** là khoảng thời gian tính từ khi một âm thanh cơ học vang lên trong không khí cho đến khi hệ thống hiểu được nó; do đó, trong một tác vụ xử lý dòng thời gian thực, việc gom lô không hề miễn phí. Nó được mua trực tiếp bằng việc đánh đổi độ trễ của người dùng.

Mối quan hệ đánh đổi này rất ngắn gọn để viết thành công thức. Nếu một khung hình mới được sinh ra sau mỗi $T_h$ giây (bước nhảy chu kỳ), việc gom một lô gồm $B$ khung sẽ buộc khung hình đầu tiên phải chờ đợi một khoảng thời gian:
$$\Delta t_{\text{wait}} = (B - 1) \, T_h$$

Với chu kỳ bước nhảy chuẩn được sử dụng xuyên suốt cuốn sách này là $10\text{ ms}$, việc gom một lô $B = 8$ khung hình sẽ cộng thêm ngay lập tức $70\text{ ms}$ độ trễ thuần túy trước khi khung hình đầu tiên được đưa vào tính toán. Con số $70\text{ ms}$ này là hệ quả số học trực tiếp từ lựa chọn thiết kế, không phải lỗi đo đạc ngẫu nhiên. Đối với một hệ thống nhận diện từ khóa (Keyword Spotting - KWS), $70\text{ ms}$ chính là ranh giới phân định giữa cảm giác tương tác tức thì và cảm giác giật cục, trễ nải. Đó là lý do vì sao mục tiêu cốt lõi của chương này khẳng định **$batch=1$**: một hệ thống Voice AI tại biên tương tác với con người không thể gom lô dữ liệu đầu vào. Câu hỏi đặt ra cho kiến trúc sư phần cứng không phải là *"Làm thế nào để tính toán một lô ma trận khổng lồ nhanh hơn?"*, mà là:

> *"Làm thế nào để tính toán dứt điểm MỘT khung hình nhỏ thật nhanh, đều đặn mỗi mười mili-giây, liên tục không ngừng nghỉ?"*

Ba điểm phân kỳ cơ học tiếp theo xuất phát từ chính hiện thực vật lý này, và mỗi điểm sẽ trở thành một yêu cầu thiết kế phần cứng ở các chương sau:

1. **Âm thanh không có điểm kết thúc tự nhiên.** Một bức ảnh có chiều cao và chiều rộng pixel hữu hạn. Một dòng âm thanh liên tục thì không có cả hai, do đó một chương trình xử lý streaming không bao giờ nhìn thấy toàn bộ dữ liệu đầu vào. Nó bắt buộc phải chuyển giao thông tin quá khứ vào **trạng thái (state)**: một dung lượng bộ nhớ cố định lưu giữ những gì khung tiếp theo cần dùng. Ở Chương 4, điều này trở thành câu hỏi then chốt: một thiết kế tiêu tốn bao nhiêu Block RAM trên chip, một câu hỏi sắc bén hơn nhiều so với việc hỏi *"có bao nhiêu bộ nhân số học"*.
2. **Các khung kế tiếp nhau hầu như lặp lại dữ liệu.** Các cơ quan phát âm vật lý trong khoang miệng con người — lưỡi, môi, hàm dưới, màn hầu — đều có khối lượng cơ học và quán tính sinh học. Chúng không thể thay đổi cấu hình vị trí tức thời trong nháy mắt; âm thanh tiếng nói duy trì tính chất gần như dừng (quasi-stationary) trong các khoảng thời gian ngắn từ $20\text{ đến }30\text{ ms}$. Để bắt được một lát cắt âm học ổn định thống kê, khối front-end phải quan sát một cửa sổ dài $25\text{ ms}$ ($400$ mẫu ở $16\text{ kHz}$), nhưng để theo dõi các chuyển tiếp âm vị nhanh giữa phụ âm và nguyên âm, nó phải dịch chuyển mỗi $10\text{ ms}$ ($160$ mẫu). Hệ quả là hai khung kế tiếp chồng lấn lên nhau dữ dội: trong số 400 mẫu của khung hiện tại, có tới 240 mẫu đã từng xuất hiện ở khung trước đó. Việc tính toán lại 240 mẫu này mỗi lần là hoàn toàn lãng phí tài nguyên. Trong phần cứng, sự chồng lấn này là một cơ hội vàng: một kiến trúc không bao giờ cần đọc lại dữ liệu bị loại bỏ có thể được xây dựng xung quanh một bộ đệm xoay vòng mà con trỏ đọc và ghi chỉ việc di chuyển tuần hoàn trên một vòng tròn cố định.
3. **Tốc độ đổ về của âm thanh là không thể thương lượng.** Một micrô cơ học không bao giờ chạy chậm lại chỉ vì bộ vi xử lý đang bận rộn. Trong thị giác, một hàng đợi đầy đồng nghĩa với việc tác vụ kết thúc muộn hơn vài mili-giây. Trong âm thanh, một hàng đợi đầy đồng nghĩa với việc các mẫu sóng âm bị rơi rụng (dropped samples), và một mẫu âm thanh bị rơi rụng vĩnh viễn không bao giờ có thể khôi phục lại được. Chu kỳ khung là một hạn chót cơ học tối thượng, không phải là một gợi ý tùy chọn.

Hệ quả tất yếu là một sự chuyển dịch căn bản trong định nghĩa về khái niệm "nhanh". Một bộ tăng tốc thị giác máy tính được định giá bằng thông lượng (throughput) — tức số khung hình xử lý được trong một giây. Một bộ tăng tốc tiếng nói thời gian thực tại biên trước hết được định giá bằng việc liệu nó có hoàn thành xử lý một khung tín hiệu bên trong chu kỳ thời gian thực của khung đó hay không, lặp đi lặp lại một cách tất định, và chỉ sau đó mới đánh giá đến năng lượng tiêu thụ trên mỗi khung. Lý do đầu tiên khiến GPU không phải là cỗ máy chân ái cho bài toán này không phải vì GPU yếu, mà vì sức mạnh của GPU được đo bằng một đại lượng mà bài toán $batch=1$ không thể sử dụng.

#### Tình thế lưỡng nan chưa giải quyết: Cuộc khủng hoảng nạp dòng (The Streaming Ingestion Crisis)

Nếu âm thanh đổ về như một dòng mẫu áp suất không khí liên tục vô tận và không thể gom lô mà không bị phạt nặng về độ trễ, làm thế nào một bộ xử lý tại biên có thể biến đổi một làn sóng liên tục vô hạn thành các gói toán học hữu hạn mà không làm thất thoát thông tin tại các biên ranh giới cắt? Tình thế lưỡng nan này dẫn dắt chúng ta trực tiếp vào các giai đoạn vật lý của chuỗi tiền xử lý âm thanh dạng dòng.

---

## 1.2 Chuỗi Tiền Xử Lý Tín Hiệu Âm Thanh Dạng Dòng

#### Cầu nối hữu cơ từ Phần 1.1: Chuyển hóa áp suất thành quy trình xử lý

Ở Phần 1.1, chúng ta đã chứng minh âm thanh là một quá trình vật lý liên tục không thể gom lô ($B > 1 \implies \text{trễ}$). Nhưng các mô hình học máy và bộ xử lý tín hiệu số không thể trực tiếp tiêu hóa một làn sóng tương tự vô tận. Để chuyển hóa áp suất không khí thô thành các đặc trưng ngôn ngữ, chúng ta phải xây dựng một đường truyền dữ liệu (datapath) phần cứng - phần mềm có khả năng cắt nhỏ, điều hòa và biến đổi dòng âm thanh với một tốc độ tất định tuyệt đối.

Phần này theo chân dòng dữ liệu qua sáu bước biến đổi chuẩn mực trong file thực nghiệm `chapter01/exp_01_streaming_audio_pipeline.py`: dạng sóng (waveform), bộ đệm xoay vòng trượt (sliding ring buffer), hàm cửa sổ (windowing), biến đổi Fourier thời gian ngắn (STFT), ngân hàng lọc Mel (Mel filterbank), và nén logarit (log compression). Sáu tên gọi này không phải là một danh mục bài học tùy tiện: mỗi tầng xử lý sinh ra bởi vì tầng xử lý trước nó để lại một vấn đề vật lý hóc búa mà nếu không giải quyết thì phép toán tiếp theo không thể thực hiện được.

- Áp suất không khí là một đại lượng liên tục trong khi máy tính chỉ lưu trữ các con số rời rạc, do đó không khí được **lấy mẫu** với tần số đều đặn.
- Dòng âm thanh không có điểm kết thúc trong khi các phép phân tích tần số cần một cụm số hữu hạn đứng yên để tính toán, do đó hệ thống duy trì một **bộ đệm** kích thước cố định và trượt nhẹ về phía trước từng bước nhỏ.
- Thao tác cắt trượt tạo ra hai đầu mép khung bị đứt đoạn đột ngột, và đối với giải tích Fourier, một mép cắt sắc nhọn trông giống hệt như các xung nhiễu tần số cực cao vốn không hề tồn tại trong phòng thu, do đó mỗi khung hình phải được **làm mờ hai đầu mép (faded)** trước khi đọc.
- Việc làm mờ hai đầu mép làm triệt tiêu năng lượng tại biên khung, nơi chứa đựng một phần thông tin âm học, do đó các khung kế tiếp nhau bắt buộc phải **chồng lấn lên nhau (overlap)** và quá trình phân tích được thực hiện **mỗi khung một lần** thay vì mỗi bước nhảy một lần.
- Một khung hình đã làm mờ vẫn chỉ là các mẫu thời gian và cần được chuyển hóa thành phổ tần số, đó là câu hỏi mà phép biến đổi **STFT** trả lời, tính toán $N$ lần cho $N$ tần số dò ứng viên.
- $257$ giá trị tần số rời rạc là quá nhiều so với khả năng tiêu hóa của một mô hình nhận diện từ khóa, và chúng lại phân bổ đều tuyến tính theo thang Hertz trong khi tai người cảm nhận phi tuyến, do đó chúng được gom lại thành $80$ **dải lọc Mel**.
- Năng lượng giữa các dải phổ chênh lệch nhau tới hàng tỉ lần và tầng nơ-ron phía sau nếu cộng trực tiếp sẽ bị chi phối hoàn toàn bởi dải âm to nhất, do đó mỗi giá trị năng lượng được thay thế bằng giá trị **logarit** của chính nó.

Toàn bộ sáu bước biến đổi này nằm gọn trong khối mang tên "Khối DSP front end" trong [Hình 1](#fig-ch1-pipeline-contract), minh họa toàn bộ cỗ máy ở quy mô thời gian của một khung hình và đánh dấu hai vị trí mà kiến trúc phải ghi nhớ trạng thái giữa các khung — vị trí đầu tiên chính là bộ đệm trượt.

**Dạng sóng tín hiệu (Waveform).** Âm thanh được ghi lại dưới dạng một chuỗi số đo độ biến thiên áp suất không khí tại các khoảng thời gian đều nhau. Khoảng thời gian này được quy định bởi **tần số lấy mẫu ($f_s$)**, tức số lượng mẫu đo được ghi lại trong một giây. Khối tiền xử lý chuẩn mực sử dụng $16{,}000$ mẫu mỗi giây, đồng nghĩa cứ mỗi $62.5\ \mu\text{s}$ sẽ có một mẫu số mới xuất hiện từ micrô và một khung phân tích $25\text{ ms}$ sẽ tích lũy $400$ mẫu. Con số này bắt rễ sâu sắc từ cơ học âm học của bộ máy phát âm con người:
- Dây thanh âm dao động ở tần số cơ bản ($F_0$) từ $85\text{ Hz}$ (giọng nam trầm) đến $255\text{ Hz}$ (giọng nữ cao).
- Khoang cộng hưởng thanh quản, vòm họng và khoang miệng tạo ra các đỉnh cộng hưởng formant ($F_1, F_2, F_3$) định hình nguyên âm, trải rộng từ $300\text{ Hz}$ đến $3{,}500\text{ Hz}$.
- Các thành phần âm học có tần số cao nhất là các phụ âm ma sát và phụ âm bật vô thanh (như tiếng xì /s/, /sh/), suy hao nhanh chóng ở dải trên $8\text{ kHz}$.

Theo định lý lấy mẫu Nyquist-Shannon, để khôi phục hoàn hảo một tín hiệu mà không bị hiện tượng chồng phổ, tần số lấy mẫu phải lớn hơn ít nhất hai lần dải thông cao nhất ($f_s \ge 2B$). Tần số lấy mẫu $16\text{ kHz}$ thiết lập tần số Nyquist tại $8\text{ kHz}$, bao bọc trọn vẹn toàn bộ phổ ngữ âm của con người trong khi triệt tiêu các nhiễu siêu âm từ môi trường. Việc nâng lên chuẩn đĩa CD $44.1\text{ kHz}$ hay chuẩn phòng thu $48\text{ kHz}$ chỉ làm tăng gấp ba kích thước bộ nhớ đệm, lưu lượng truyền dẫn bus và các phép tính DSP mà không mang lại thêm bất kỳ thông tin ngữ âm hữu ích nào cho mô hình nhận dạng.

**Bộ đệm xoay vòng trượt (Sliding ring buffer).** Chuỗi xử lý quan sát $400$ mẫu mỗi lần và tiến về phía trước $160$ mẫu mỗi bước. Một chương trình phần mềm ngây thơ tính toán lại mỗi khung từ mảng dữ liệu gốc sẽ phải đọc lại $240$ mẫu mà nó vừa xử lý ở khung trước. Thay vào đó, thiết kế duy trì một bộ đệm duy nhất chứa $400$ con số: nó dịch chuyển dữ liệu bên trong lên $160$ vị trí, ghi đè $160$ mẫu mới vào cuối mảng, rồi thực hiện tính toán. Điều tối quan trọng là chi phí của phép dịch chuyển này: trong phần mềm, đó là một vòng lặp di chuyển bộ nhớ (`memmove`), nhưng trong phần cứng chuyên dụng, chi phí này hoàn toàn **bằng 0 chu kỳ xung nhịp**, bởi vì một bộ đệm vòng thực thụ trên silicon chỉ là một khối RAM với hai bộ đếm di chuyển tuần hoàn quanh một vòng tròn cố định. Dữ liệu đứng yên; chỉ có thứ tự đọc thay đổi. Sự khác biệt giữa một vòng lặp phần mềm và hai con trỏ phần cứng là một trong những minh chứng rực rỡ nhất về giá trị thực sự của việc đưa thuật toán lên FPGA.

::: {#fig-ch1-ring-buffer .figure}
```tikz
% Vì sao bộ đệm vòng là miễn phí trên phần cứng và là vòng lặp trong phần mềm --
% cùng một cửa sổ 400 mẫu, cùng bước nhảy 160, vẽ theo hai cách.
\begin{tikzpicture}[
  font=\tiny,
  blk/.style={draw=black!70, thin, align=center, inner sep=1pt, minimum height=6.2mm},
  gone/.style={blk, fill=black!4, text=black!55},
  kept/.style={blk, fill=black!20},
  live/.style={blk, fill=black!48, text=black!85},
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ann/.style={font=\tiny, text=black!66, align=center, inner sep=0pt},
  annt/.style={font=\tiny, text=black!66, align=left, inner sep=0pt},
  ar/.style={-{Stealth[length=1.4mm]}, black!62, thin},
  cp/.style={-{Stealth[length=1.4mm]}, black!72, semithick},
  hd/.style={-{Stealth[length=1.6mm]}, black!78, thick},
  fl/.style={font=\tiny, text=black!60}]

% ================= (a) Phần mềm: Dữ liệu bị sao chép =================
\node[ttl, anchor=west] at (0,3.62) {(a) Trong phần mềm:\\các mẫu số bị sao chép};
\node[fl, anchor=east] at (-0.08,2.86) {khung $\ell$};
\node[gone, minimum width=1.6cm] at (0.80,2.86) {cũ nhất $160$};
\node[kept, minimum width=2.4cm] at (2.80,2.86) {mới nhất $240$};
\node[fl, anchor=east] at (-0.08,1.56) {khung $\ell\!+\!1$};
\node[kept, minimum width=2.4cm] at (1.50,1.56) {chính $240$ mẫu đó, bị dời xuống};
\node[live, minimum width=1.6cm] at (3.50,1.56) {$160$ mẫu mới};
\draw[cp] (2.55,2.55) .. controls (1.95,2.22) and (1.68,2.06) .. (1.50,1.90);
\node[annt, text=black!72] at (2.78,2.12) {sao chép};
\draw[ar] (0.45,2.55) -- (0.05,1.16);
\node[fl, anchor=north east] at (0.30,1.12) {hủy bỏ};
\draw[ar] (4.92,2.86) .. controls (4.92,2.10) and (4.70,1.72) .. (4.34,1.60);
\node[fl, anchor=west] at (4.98,2.86) {ghi mới};
\node[annt, anchor=west] at (0.05,0.72)
  {vòng lặp bộ nhớ: $240$ lần đọc và $240$ lần ghi, mỗi khung hình};

% ================= (b) Phần cứng: Chỉ có con trỏ di chuyển =================
\begin{scope}[shift={(9.85,2.02)}]
  \node[ttl, anchor=west] at (-3.60,1.62) {(b) Trong phần cứng:\\các mẫu số đứng yên};
  \def\R{1.45}\def\ri{0.62}
  \fill[black!48] (0,0) -- (90:\R) arc (90:-54:\R) -- cycle;
  \fill[black!20] (0,0) -- (-54:\R) arc (-54:-270:\R) -- cycle;
  \fill[white] (0,0) circle (\ri);
  \draw[black!70, thin] (90:\R) arc (90:-270:\R);
  \draw[black!70, thin] (90:\ri) arc (90:-270:\ri);
  \draw[black!55, thin] (90:\ri) -- (90:\R);
  \draw[black!55, thin] (-54:\ri) -- (-54:\R);
  \draw[black!55, thin] (-270:\ri) -- (-270:\R);
  \node[font=\tiny, text=black!85] at (18:1.04) {$160$};
  \node[font=\tiny, text=black!70] at (-162:1.04) {$240$};
  \fill[black!80] (90:\R) circle (0.05);
  \node[fl, anchor=south east] at (96:1.50) {con trỏ ghi};
  \draw[hd] (78:1.74) arc (78:-54:1.74);
  \node[fl, anchor=west] at (0:1.80) {tiến $160$ bước};
  \node[font=\tiny, text=black!72, align=center] at (0,0) {hai\\con trỏ};
  \node[ann] at (0,-1.86) {một con trỏ ghi và một con trỏ đọc,\\
    mỗi con trỏ tiến $160$ bước và cuộn tròn tại $400$};
  \node[ann, text=black!72] at (0,-2.44) {không có mẫu số nào bị di dời vị trí\\trong bộ nhớ vật lý};
\end{scope}
\end{tikzpicture}
```
Hai bảng vẽ cùng một kích thước cửa sổ và cùng một bước nhảy. Ở bảng (a), $240$ mẫu số còn giữ lại phải thay đổi địa chỉ ô nhớ sau mỗi khung — đó là một vòng lặp phần mềm tốn kém $240$ lệnh đọc và $240$ lệnh ghi. Ở bảng (b), các mẫu số nằm bất động tại địa chỉ cố định; con trỏ ghi và con trỏ đọc chỉ việc bước tới $160$ bước và cuộn vòng tại $400$. Chi phí dịch chuyển dữ liệu trong phần cứng bằng $0$.
:::

**Áp hàm cửa sổ (Windowing).** Một khung hình là một lát cắt rời rạc từ một làn sóng liên tục, và mép cắt này diễn ra đột ngột: tín hiệu dừng hẳn ở một đầu và bắt đầu tức thì ở đầu kia. Sự đứt gãy đột ngột này đối với phân tích Fourier trông giống hệt như các sóng hài có tần số vô cùng cao. Giải pháp là nhân khung hình với một **hàm cửa sổ** làm suy giảm mượt mà hai đầu mép về gần mức 0. Thiết kế chuẩn sử dụng hàm cửa sổ Hamming trên 400 mẫu của bộ đệm. Cái giá phải trả là hai đầu mép khung đóng góp rất ít năng lượng, làm cho đáp ứng phổ của từng âm thanh bị "rộng ra" (broadening).

**Biến đổi Fourier thời gian ngắn (STFT).** Một phép biến đổi DFT trên mỗi khung hình, lặp đi lặp lại theo dòng thời gian, tạo nên biến đổi STFT. Thiết kế tính toán biến đổi này thông qua thuật toán FFT 512 điểm và chỉ giữ lại một nửa dải phổ không dư thừa (do tín hiệu âm thanh đầu vào là số thực), mang lại $257$ dải tần số cho mỗi khung hình.

**Ngân hàng lọc Mel (Mel filterbank).** $257$ dải tần số tuyến tính sau đó được thu gọn thành $80$ dải lọc Mel với độ rộng không bằng nhau. Chúng được phân bổ mô phỏng theo cơ chế cảm thụ của ốc tai người: phân giải rất mịn ở tần số thấp và phân giải thô ở tần số cao. Mỗi bộ lọc là một hình tam giác trùm lên một cụm dải tần số, và năng lượng đầu ra của mỗi dải là tổng có trọng số của các dải phổ nằm dưới tam giác đó.

**Nén logarit (Log compression).** Cuối cùng, năng lượng của mỗi dải $E$ được thay thế bằng $\ln(\max(E, 10^{-6}))$. Phép nén logarit được áp dụng vì màng nhĩ và mạng nơ-ron phản hồi theo tỉ lệ cường độ âm thanh thay vì chênh lệch tuyến tính tuyệt đối. Ngưỡng sàn $10^{-6}$ được đặt ra để một dải tần số im lặng tuyệt đối trả về một con số hữu hạn thay vì âm vô cực ($-\infty$).

Các hình dạng dữ liệu được tổng hợp trong bảng kích thước dưới đây, bởi vì trong phần cứng, hình dạng dữ liệu chính là độ rộng dây dẫn và dung lượng ô nhớ:

| Tầng xử lý | Dữ liệu sinh ra mỗi khung | Kích thước ở định dạng FP32 (Float 32-bit) |
| :--- | :--- | :--- |
| Dữ liệu sóng âm vào | 160 mẫu mới | 640 byte nạp mỗi 10 ms |
| Bộ đệm xoay vòng | 400 mẫu lưu giữ | 1,600 byte, thường trú |
| Khung sau áp cửa sổ | 400 mẫu | tích của bộ đệm và cửa sổ Hamming |
| Đầu vào FFT | 512 mẫu | 400 mẫu thực cộng 112 số 0 đệm (zero-padding) |
| Phổ năng lượng | 257 dải phổ | 257 giá trị năng lượng thực |
| Các dải lọc Mel | 80 giá trị | nhân với ma trận trọng số $80 \times 257$ |
| Khung Log-Mel | 80 giá trị | đầu vào trực tiếp cho mô hình nhận dạng |

### Hộp Bẻ Gãy Ngộ Nhận (Misconception Buster): Ba Tử Huyệt Của Tiền Xử Lý Âm Thanh

| Ngộ nhận (Tử huyệt nhận thức) | Căn nguyên gây ngộ nhận | Bản chất khoa học bẻ gãy bẫy ngộ nhận |
| :--- | :--- | :--- |
| **Bẫy A: Tần số lấy mẫu càng cao ($48\text{ kHz}$) thì độ chính xác của AI càng lớn.** | Trực giác người nghe nhạc thường đồng nhất $48\text{ kHz}$ hay $96\text{ kHz}$ với âm thanh hi-fi trung thực, sắc nét hơn. | **Âm học tiếng nói suy hao triệt để trên $8\text{ kHz}$.** Các formant của thanh quản ($F_1, F_2, F_3$) trải từ $300\text{ Hz}$ đến $3{,}500\text{ Hz}$; phụ âm xì tắt dần trước $8\text{ kHz}$. Tăng $f_s$ lên $48\text{ kHz}$ chỉ thu thêm tiếng xì siêu âm của môi trường trong khi thổi phồng dung lượng BRAM, băng thông bus và phép tính FFT lên gấp ba lần mà không đem lại thông tin ngữ âm nào. |
| **Bẫy B: Cửa sổ trượt chỉ là một vòng lặp sao chép bộ nhớ trong phần mềm.** | Trong mã nguồn Python hay C, dịch mảng $160$ mẫu được thực thi bằng lệnh `memmove` ($240$ lần đọc, $240$ lần ghi). | **Trên phần cứng không gian FPGA, bộ đệm vòng tốn 0 chu kỳ sao chép.** Bằng cách hiện thực hai bộ đếm phần cứng (con trỏ đọc và ghi) xoay vòng quanh Block RAM, dữ liệu đứng yên hoàn toàn trong khi địa chỉ tự cuộn tròn theo modulo $L$. Chi phí dời bộ nhớ từ $\mathcal{O}(L-H)$ biến mất hoàn toàn. |
| **Bẫy C: Cắt âm thanh bằng khung chữ nhật sắc cạnh giữ trọn dữ liệu gốc.** | Cắt phẳng giữ nguyên vẹn giá trị từng mẫu âm thanh mà không làm biến dạng biên độ. | **Sự gián đoạn bước nhảy đột ngột tạo ra sóng hài giả tần số cao.** Với phép phân tích Fourier, mép cắt vuông vức trông giống như nhiễu tần số vô hạn không hề có trong phòng thu. Việc nhân với hàm cửa sổ suy giảm mượt (Hamming) là bắt buộc về mặt vật lý để triệt tiêu hiện tượng rò rỉ phổ. |

#### Tình thế lưỡng nan chưa giải quyết: Hiện tượng nhòe mờ tần số (The Frequency Blur)

Chúng ta đã thu được các khung tín hiệu dừng ổn định $400$ mẫu mỗi $10\text{ ms}$. Nhưng đồ thị dạng sóng trong miền thời gian vẫn che giấu các formant thanh quản phân biệt nguyên âm /a/ với nguyên âm /i/. Làm thế nào để cô lập các tần số cộng hưởng rời rạc về mặt toán học mà không phải hàn hàng ngàn bộ lọc dải tương tự bằng linh kiện rời? Câu hỏi này dẫn dắt chúng ta trực tiếp vào cơ sở toán học của phép biến đổi phổ.

---

## 1.3 Mô Hình Hóa Toán Học: STFT và Ngân Hàng Lọc Mel

#### Cầu nối hữu cơ từ Phần 1.2: Giải phẫu toán học của phổ tín hiệu

Phần 1.2 đã phác thảo hành trình vật lý từ áp suất không khí liên tục đến các khung tín hiệu được áp cửa sổ. Bây giờ, chúng ta phải xây dựng chiếc kính hiển vi toán học để nhìn sâu vào bên trong từng khung hình: Biến đổi Fourier Thời gian ngắn (STFT) và ngân hàng lọc Mel. Thay vì học vẹt các công thức phức tạp, chúng ta sẽ suy luận từng phép toán từ các nguyên lý đầu tiên của giao thoa sóng và cảm thụ thính giác.

Sáu biểu thức biến đổi một dòng mẫu thành $80$ con số của một khung hình. Mỗi biểu thức được mổ xẻ qua năm bước cố định: công thức, các biến số, ý nghĩa vật lý, cái giá phần cứng, và những gì công thức *không* nói.

Các tham số thiết kế chuẩn được định nghĩa thống nhất:
Tần số lấy mẫu $f_s = 16{,}000\ \text{Hz}$, độ dài khung $L = 400$ mẫu ($25\text{ ms}$), bước nhảy $H = 160$ mẫu ($10\text{ ms}$), độ dài biến đổi $N = 512$ điểm, số lượng dải Mel $M = 80$, dải tần số $f_{\min} = 0$ đến $f_{\max} = 8{,}000\ \text{Hz}$.

### Sóng dò (Probe Wave), trước khi xuất hiện công thức

Một trong sáu biểu thức chứa biểu tượng $e^{-j2\pi kn/N}$. Một người học chưa từng gặp biểu tượng này không nên bị bắt buộc phải chấp nhận nó bằng niềm tin mù quáng. Bản chất của biểu thức này không có gì xa lạ: nó xuất phát từ một thực tế trực quan rằng việc tìm kiếm một tần số bên trong một tín hiệu thực chất là nhân tín hiệu đó với một sóng dò chuẩn rồi cộng dồn lại.

**Một tần số cần khớp những gì.** Một âm thanh thuần khiết có ba đặc tính: biên độ, tần số và pha. Hai âm thanh cùng tần số và cùng độ lớn nhưng bắt đầu lệch nhau là hai tín hiệu khác nhau. Một phương pháp dò tìm tần số do đó phải trả lời được cả ba câu hỏi cùng lúc.

**Phép kiểm tra là một phép nhân, không phải phép chia.** Khung tín hiệu là một mảng các mẫu số. Nhân hai mảng theo từng vị trí mẫu rồi cộng tất cả các tích số lại. Tổng số thu được trả lời câu hỏi: hai chuỗi này đồng điệu với nhau đến mức nào? Nếu cùng tần số và cùng pha, tổng số rất lớn. Nếu lệch tần số, các tích số triệt tiêu nhau về 0.

**Cần hai sóng dò.** Một sóng dò đơn lẻ không thể phân biệt được tín hiệu nhỏ nhưng cùng pha với tín hiệu lớn nhưng lệch pha. Sử dụng cặp sóng dò Cosine và Sine lệch nhau $90^\circ$ cho phép giải quyết trọn vẹn cả biên độ và pha. Đó là lý do giải tích Fourier trả về **số phức**.

**Công thức Euler gom cặp số thành một đối tượng duy nhất.**

> **Công thức.**
> $$e^{-j\theta} = \cos\theta - j\sin\theta$$
>
> **Ý nghĩa vật lý.** Theo dõi vế phải khi $\theta$ tăng từ 0. Nhân với $e^{-j\theta}$ bản chất là xoay một số đi một góc $\theta$ theo chiều kim đồng hồ, và việc tách phần thực và phần ảo chính là đọc giá trị của hai sóng dò Cosine và Sine tại thời điểm đó.

---

### Khung hình sau khi áp cửa sổ (Windowed Frame)

> **Công thức.**
> $$x_\ell[n] = x[n_0 + \ell H + n]\; w[n], \qquad n = 0, 1, \dots, L-1$$
>
> **Các biến số.**
> - $x_\ell$: khung hình thứ $\ell$ đã được áp cửa sổ, mảng gồm $L=400$ mẫu số.
> - $x$: dòng mẫu âm thanh liên tục đầu vào.
> - $H$: bước nhảy khung, $160$ mẫu ($10\text{ ms}$).
> - $L$: độ dài khung hình, $400$ mẫu ($25\text{ ms}$).
> - $w$: hàm cửa sổ Hamming cố định $L$ điểm, làm suy giảm hai đầu mép về $0.08$ và giữ đỉnh giữa tại $1.00$.

::: {#fig-ch1-frames-window-overlap .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  env/.style={draw=black!72, semithick, smooth},
  fb/.style={draw=black!45, thin, fill=black!4},
  lab/.style={font=\tiny, text=black!70},
  dim/.style={<->, black!70, thin},
  guide/.style={black!28, thin, densely dotted},
  st/.style={-{Stealth[length=1.4mm]}, black!55, thin}]
\begin{scope}[x=0.0122cm, y=1cm]
  \draw[guide] (0,0.12) -- (0,3.53);
  \draw[guide] (160,0.12) -- (160,3.53);
  \draw[guide] (320,0.12) -- (320,3.53);
  \draw[guide] (480,0.12) -- (480,3.53);
  \draw[guide] (640,0.12) -- (640,3.53);
  \draw[guide] (1040,0.12) -- (1040,3.53);
  \draw[fb] (0,2.97) rectangle (399,3.49);
  \draw[env] plot coordinates {(0,3.062) (25,3.076) (50,3.116) (75,3.176) (100,3.247) (125,3.317) (150,3.377) (175,3.416) (200,3.430) (225,3.415) (250,3.375) (275,3.315) (300,3.244) (325,3.173) (350,3.114) (375,3.075) (399,3.062)};
  \node[lab, anchor=east] at (-5,3.230) {$\ell=0$};
  \draw[fb] (160,2.35) rectangle (559,2.87);
  \draw[env] plot coordinates {(160,2.442) (185,2.456) (210,2.496) (235,2.556) (260,2.627) (285,2.697) (310,2.757) (335,2.796) (360,2.810) (385,2.795) (410,2.755) (435,2.695) (460,2.624) (485,2.553) (510,2.494) (535,2.455) (559,2.442)};
  \node[lab, anchor=east] at (155,2.610) {$\ell=1$};
  \draw[fb] (320,1.73) rectangle (719,2.25);
  \draw[env] plot coordinates {(320,1.822) (345,1.836) (370,1.876) (395,1.936) (420,2.007) (445,2.077) (470,2.137) (495,2.176) (520,2.190) (545,2.175) (570,2.135) (595,2.075) (620,2.004) (645,1.933) (670,1.874) (695,1.835) (719,1.822)};
  \node[lab, anchor=east] at (315,1.990) {$\ell=2$};
  \draw[fb] (480,1.11) rectangle (879,1.63);
  \draw[env] plot coordinates {(480,1.202) (505,1.216) (530,1.256) (555,1.316) (580,1.387) (605,1.457) (630,1.517) (655,1.556) (680,1.570) (705,1.555) (730,1.515) (755,1.455) (780,1.384) (805,1.313) (830,1.254) (855,1.215) (879,1.202)};
  \node[lab, anchor=east] at (475,1.370) {$\ell=3$};
  \draw[fb] (640,0.49) rectangle (1039,1.01);
  \draw[env] plot coordinates {(640,0.582) (665,0.596) (690,0.636) (715,0.696) (740,0.767) (765,0.837) (790,0.897) (815,0.936) (840,0.950) (865,0.935) (890,0.895) (915,0.835) (940,0.764) (965,0.693) (990,0.634) (1015,0.595) (1039,0.582)};
  \node[lab, anchor=east] at (635,0.750) {$\ell=4$};
  \draw[->, black!75] (-25,0.0) -- (1075,0.0) node[right, font=\tiny, xshift=1.5pt] {$n$};
  \draw[black!55] (0,-0.03) -- (0,0.03);
  \draw[black!55] (400,-0.03) -- (400,0.03);
  \draw[black!55] (800,-0.03) -- (800,0.03);
  \draw[black!55] (1040,-0.03) -- (1040,0.03);
  \node[lab, anchor=north] at (0,0.0) {0};
  \node[lab, anchor=north] at (400,0.0) {400};
  \node[lab, anchor=north] at (800,0.0) {800};
  \node[lab, anchor=north west, xshift=1pt] at (1040,0.0) {1040};
  \draw[dim] (0,-0.34) -- (160,-0.34) node[midway, below, font=\tiny] {$H$};
  \draw[dim] (0,3.65) -- (400,3.65) node[midway, above, font=\tiny] {$L$};
  \draw[dim] (160,-0.60) -- (400,-0.60) node[midway, below, font=\tiny] {{$L-H$ mẫu chung}};
  \draw[st] (280,-0.44) -- (280,-0.05);
\end{scope}
\end{tikzpicture}
```
Năm khung hình gồm $L$ mẫu, mỗi khung bắt đầu sau khung trước $H$ mẫu, vẽ đúng tỉ lệ dọc theo trục mẫu số $n$. Đường cong trên mỗi làn là hàm cửa sổ $w$. Phần chồng lấn $L-H = 240$ mẫu chiếm $60\%$ khung hình giúp bảo toàn năng lượng tín hiệu liên tục.
:::

---

### Biến đổi Fourier Thời gian ngắn (STFT)

> **Công thức.**
> $$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n]\; e^{-j 2\pi k n / N}, \qquad k = 0, 1, \dots, N-1$$
>
> **Ý nghĩa.** Khung hình $400$ mẫu được đệm thêm $112$ số không thành $N=512$ điểm. Biểu thức thực hiện tương quan tín hiệu với sóng dò quay ở tần số bin thứ $k$. Khoảng cách giữa hai bin kế tiếp là $\Delta f = f_s / N = 16{,}000 / 512 = 31.25\text{ Hz}$. Do tín hiệu đầu vào là số thực, phổ đối xứng qua trục giữa, ta chỉ cần giữ lại $N/2 + 1 = 257$ dải tần số độc lập (từ $0\text{ Hz}$ đến $8{,}000\text{ Hz}$).

---

### Phổ năng lượng (Power Spectrum)

> **Công thức.**
> $$P_\ell[k] = |X_\ell[k]|^2 = \text{Re}(X_\ell[k])^2 + \text{Im}(X_\ell[k])^2$$
>
> **Ý nghĩa.** Mô hình âm học nhận diện từ khóa chỉ quan tâm đến mật độ năng lượng và loại bỏ thông tin pha. Phép bình phương độ lớn triệt tiêu căn bậc hai phức tạp, biến đổi $257$ số phức thành $257$ số thực không âm đại diện cho phân bố năng lượng theo tần số của khung hình.

---

### Ánh xạ thang đo tần số Mel

Ốc tai con người có cấu trúc cơ học phân giải âm thanh phi tuyến: cực kỳ nhạy cảm với các biến đổi cao độ nhỏ ở dải trầm (nguyên âm), nhưng lại kém phân biệt ở dải cao (nhiễu ma sát). Thang đo Mel được sinh ra để mô hình hóa hiện tượng sinh học này:

> **Công thức.**
> $$\mathrm{mel}(f) = 2595 \log_{10}\!\left(1 + \frac{f}{700}\right)$$

::: {#fig-ch1-mel-curve .figure}
```tikz
% Đồ thị hàm Mel: Hertz ở trục hoành, Mels ở trục tung.
\begin{tikzpicture}[
  font=\tiny,
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ann/.style={font=\tiny, text=black!66, align=center, inner sep=0pt},
  annt/.style={font=\tiny, text=black!66, align=left, inner sep=0pt},
  ax/.style={->, black!72, semithick},
  tk/.style={font=\tiny, text=black!60},
  gr/.style={black!30, thin, densely dashed},
  drop/.style={black!40, thin, densely dotted},
  curve/.style={black!82, line width=0.9pt},
  gap/.style={black!70, thin},
  tick/.style={black!70, thin}]
\def\sx{0.001125}
\def\sy{0.001479}
\def\X{1.30}
\def\Y{0.70}

\node[ttl, anchor=west] at (0,\Y + 5.14)
  {các bước đều nhau trên trục mel tạo thành các bước giãn nở trên trục hertz};

\draw[curve, domain=0:8000, smooth, variable=\f, samples=140]
  plot ({\X + \f*\sx}, {\Y + 1126.98*ln(1+\f/700)*\sy});

\draw[ax] (\X,\Y) -- (\X + 9.00 + 0.55,\Y);
\draw[ax] (\X,\Y) -- (\X,\Y + 4.20 + 0.35);

\draw[black!55] (\X,\Y-0.035) -- (\X,\Y+0.035);
\draw[black!55] (\X + 8000.0*\sx,\Y-0.035) -- (\X + 8000.0*\sx,\Y+0.035);
\node[tk, anchor=north] at (\X,\Y-0.06) {$0$};
\node[tk, anchor=north] at (\X + 8000.0*\sx,\Y-0.06) {$8000$};
\node[tk, anchor=west] at (\X + 9.00 + 0.60,\Y) {Hz};

\foreach \m/\lab in {0/$0$,355/$355$,710/$710$,1065/$1065$,1420/$1420$,1775/$1775$,
                     2130/$2130$,2485/$2485$,2840/$2840$} {
  \draw[black!55] (\X-0.035,\Y + \m*\sy) -- (\X+0.035,\Y + \m*\sy);
  \node[tk, anchor=east] at (\X-0.07,\Y + \m*\sy) {\lab};
}
\node[tk, anchor=south] at (\X,\Y + 4.20 + 0.38) {mels};

\foreach \m/\h in {355/259.2,710/614.3,1065/1101.0,1420/1767.8,1775/2681.5,
                   2130/3933.6,2485/5649.2,2840/8000.0} {
  \draw[gr] (\X,\Y + \m*\sy) -- (\X + \h*\sx,\Y + \m*\sy);
  \draw[drop] (\X + \h*\sx,\Y + \m*\sy) -- (\X + \h*\sx,\Y);
}

\draw[gap] (\X + 0.000*\sx,\Y-0.36) -- (\X + 259.2*\sx,\Y-0.36);
\draw[tick] (\X + 0.000*\sx,\Y-0.44) -- (\X + 0.000*\sx,\Y-0.28);
\draw[tick] (\X + 259.2*\sx,\Y-0.44) -- (\X + 259.2*\sx,\Y-0.28);
\draw[gap] (\X + 5649.2*\sx,\Y-0.36) -- (\X + 8000.0*\sx,\Y-0.36);
\draw[tick] (\X + 5649.2*\sx,\Y-0.44) -- (\X + 5649.2*\sx,\Y-0.28);
\draw[tick] (\X + 8000.0*\sx,\Y-0.44) -- (\X + 8000.0*\sx,\Y-0.28);
\node[ann, text=black!80] at (\X + 129.6*\sx,\Y-0.54) {$259$};
\node[ann, text=black!80] at (\X + 6824.6*\sx,\Y-0.54) {$2{,}351$};
\node[annt, text=black!80, align=left] at (\X + 9.00 + 0.62,\Y + 1.10)
  {một bước trên\\thang mel là $259$\\Hz ở dải thấp,\\$2{,}351$ Hz\\ở dải cao};
\end{tikzpicture}
```
Trục tung là thang đo Mel, trục hoành là tần số Hertz. Các vạch ngang biểu thị các bước đều nhau $355\text{ mel}$. Khi chiếu xuống trục Hertz, dải đầu tiên chỉ rộng $259\text{ Hz}$ trong khi dải cuối cùng giãn nở rộng tới $2{,}351\text{ Hz}$ (gấp 9 lần) cho cùng một khoảng cách cảm thụ âm nhạc.
:::

---

### Ngân hàng lọc Mel dưới dạng tổng có trọng số

> **Công thức.**
> $$E_\ell[m] = \sum_{k=0}^{256} g_m[k]\, P_\ell[k], \qquad g_m[k] =
> \begin{cases}
> \dfrac{k - k_{m-1}}{k_m - k_{m-1}} & k_{m-1} \le k \le k_m \\[4pt]
> \dfrac{k_{m+1} - k}{k_{m+1} - k_m} & k_m < k \le k_{m+1} \\[4pt]
> 0 & \text{khác}
> \end{cases}$$
>
> **Ý nghĩa.** $80$ dải lọc tam giác gối đầu lên nhau biến đổi ma trận $257$ điểm phổ thành $80$ giá trị năng lượng $E_\ell[m]$. Về mặt toán học, đây là phép nhân ma trận trọng số thưa kích thước $80 \times 257$ với vector phổ $257 \times 1$.

::: {#fig-ch1-mel-triangles .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  tri/.style={draw=black!78, semithick},
  bin/.style={draw=black!25, thin},
  ax/.style={->, black!75},
  tk/.style={font=\tiny, text=black!75},
  nb/.style={font=\tiny, black!60},
  band/.style={draw, black!60, thin, fill=black!6, inner sep=2.5pt, font=\tiny}]

\begin{scope}[x=0.00145cm, y=1.05cm]
  \node[anchor=west, font=\tiny\itshape, text=black!70] at (-140,1.72)
    {(a) sáu trong số tám mươi bộ lọc tam giác vẽ theo tần số hertz: bước đều trên thang mel, bước rộng dần trên hertz};
  \draw[ax] (-120,0) -- (8320,0);
  \foreach \h/\lbl in {0/$0$,1000/$1$,2000/$2$,3000/$3$,4000/$4$,5000/$5$,6000/$6$,7000/$7$,8000/$8$} {
    \draw[black!55] (\h,-0.04) -- (\h,0.04) node[tk, below, yshift=-0.5pt] {\lbl};
  }
  \node[tk, anchor=west, xshift=2pt] at (8330,0) {kHz};
  \fill[black!8] (0,0) rectangle (8000,0.045);
  \draw[tri] (812.50,0) -- (843.75,1) -- (906.25,0) -- cycle;
  \draw[tri] (1718.75,0) -- (1781.25,1) -- (1875.00,0) -- cycle;
  \draw[tri] (3156.25,0) -- (3281.25,1) -- (3406.25,0) -- cycle;
  \draw[tri] (4593.75,0) -- (4750.00,1) -- (4937.50,0) -- cycle;
  \draw[tri] (5875.00,0) -- (6093.75,1) -- (6281.25,0) -- cycle;
  \draw[tri] (7468.75,0) -- (7718.75,1) -- (8000.00,0) -- cycle;
  \foreach \b in {64,128,192,256} {
    \pgfmathsetmacro{\hb}{\b*31.25}
    \draw[bin] (\hb,0) -- (\hb,1.18);
    \node[nb, anchor=south west, xshift=1.2pt] at (\hb,1.19) {bin \b};
  }
  \node[nb, align=left, anchor=west] at (6350,0.62)
    {dải 79: trùm lên $16$ bin\\phổ thực tế};
\end{scope}

\begin{scope}[yshift=-4.15cm, x=0.040cm, y=0.9cm]
  \node[anchor=west, font=\tiny\itshape, text=black!70] at (0,2.95)
    {(b) mười bin phổ thấp nhất và dải lọc mel tương ứng};
  \draw[ax] (0,2.15) -- (330,2.15);
  \foreach \h/\lbl in {0/$0$,62.5/$62.5$,125/$125$,187.5/$187.5$,250/$250$,312.5/$312.5$} {
    \draw[black!55] (\h,2.09) -- (\h,2.21) node[tk, above, yshift=0.5pt] {\lbl};
  }
  \node[tk, anchor=west, xshift=2pt] at (332,2.15) {Hz};
  \foreach \b in {0,...,9} {
    \pgfmathsetmacro{\lo}{\b*31.25}
    \draw[bin, fill=black!4] (\lo,1.25) rectangle ++(31.25,0.72);
    \node[font=\tiny, text=black!72] at (\lo+15.6,1.61) {bin $\b$};
  }
  \node[band] (b0) at (15.6,0.30) {dải $0$};
  \node[band] (b1) at (46.9,0.30) {dải $1$};
  \node[band, fill=red!8, draw=black!55] (b2) at (62.5,-0.55) {dải $2$};
  \node[band] (b3) at (78.1,0.30) {dải $3$};
  \node[band] (b4) at (109.4,0.30) {dải $4$};
  \node[band] (b5) at (140.6,0.30) {dải $5$};
  \node[band] (b6) at (171.9,0.30) {dải $6$};
  \node[band] (b7) at (203.1,0.30) {dải $7$};
  \node[band] (b8) at (234.4,0.30) {dải $8$};
  \node[band] (b9) at (265.6,0.30) {dải $9$};
  \foreach \x in {15.6,46.9,78.1,109.4,140.6,171.9,203.1,234.4,265.6} {
    \draw[->, black!50, thin] (\x,0.55) -- (\x,1.23);
  }
  \draw[->, black!50, thin, densely dashed] (62.5,-0.07) -- (62.5,1.23);
  \node[font=\tiny, text=black!60, anchor=north] at (62.5,-0.78) {không đọc bin nào};
\end{scope}

\end{tikzpicture}
```
80 bộ lọc tam giác Mel vẽ theo thang Hertz. Bảng (a) phác họa sự giãn nở độ rộng bộ lọc khi tần số tăng dần. Bảng (b) phóng to 10 dải tần số thấp nhất: dải 2 có màu đỏ vì đỉnh và cạnh của nó rơi vào cùng một bin phổ bị làm tròn, dẫn tới việc dải 2 luôn trả về giá trị 0.
:::

---

### Nén Logarit (Log Compression)

> **Công thức.**
> $$c_\ell[m] = \ln\bigl(\max(E_\ell[m],\, 10^{-6})\bigr)$$
>
> **Ý nghĩa.** Định luật tâm sinh lý học Weber-Fechner chỉ ra rằng con người cảm nhận độ to của âm thanh theo thang logarit. Trong tự nhiên, tỉ lệ năng lượng giữa tiếng thì thầm ($10^{-5}\text{ Pa}$) và tiếng hét lớn ($10\text{ Pa}$) chênh lệch tới $10^{10}$ lần ($100\text{ dB}$). Phép nén logarit biến phép nhân tỉ lệ biên độ thành phép cộng khoảng cách tuyến tính, giúp mạng nơ-ron học tập đồng đều mà không bị áp đảo bởi các nguyên âm quá to.

::: {#fig-ch1-window-cost .figure}
```tikz
% Cái giá của việc áp hàm cửa sổ đối với độ rộng phổ
\begin{tikzpicture}[
  font=\tiny,
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ax/.style={->, black!72, semithick},
  tk/.style={font=\tiny, text=black!60},
  curve/.style={black!82, line width=0.8pt},
  env/.style={black!52, thin, densely dashed},
  gone/.style={black!28, thin},
  dim/.style={black!70, thin},
  ridge/.style={black!55, thin, dash dot},
  tick/.style={black!70, thin},
  lab/.style={font=\tiny, text=black!72, align=center, inner sep=0pt}]
\draw[gone] plot [smooth] coordinates {(0.12,4.21) (0.50,3.42) (1.00,3.03) (2.00,4.37) (3.00,3.10) (4.00,4.30) (5.14,3.10)};
\draw[ax] (0.06,3.70) -- (5.41,3.70);
\draw[black!58, thin] (0.12,2.90) -- (0.12,4.50);
\draw[black!58, thin] (4.31,2.90) -- (4.31,4.50);
\draw[curve] plot [smooth] coordinates {(0.54,3.70) (1.00,3.03) (1.50,3.84) (2.00,4.37) (2.50,3.30) (3.00,3.10) (3.50,3.98) (4.00,4.30) (4.72,4.41)};
\node[lab, text=black!74, anchor=west] at (0.06,4.58) {khung hình khi cắt thẳng -- vách đứng ở hai đầu};
\node[tk, anchor=north east] at (0.18,2.88) {$0$};
\node[tk, anchor=north] at (4.31,2.88) {$400$};
\node[tk, anchor=west] at (5.45,3.70) {n};
\draw[ax] (6.45,4.38) -- (6.45,2.60);
\draw[ax] (6.45,2.60) -- (13.69,2.60);
\node[tk, anchor=north] at (6.45,2.55) {$0$};
\node[tk, anchor=north] at (13.45,2.55) {$500$};
\node[tk, anchor=west] at (13.73,2.60) {Hz};
\node[tk, anchor=south east] at (6.38,4.33) {dB};
\draw[black!40, thin, densely dotted] (9.95,2.60) -- (9.95,4.27);
\node[tk, anchor=north] at (9.95,2.55) {$250$};
\draw[curve] plot [smooth] coordinates {(6.45,2.60) (8.0,2.7) (9.4,3.1) (9.95,4.27) (10.5,3.1) (12.0,2.7) (13.45,2.60)};
\draw[dim] (9.40,4.35) -- (10.50,4.35);
\node[lab, anchor=south] at (9.95,4.37) {$80$ Hz};
\draw[ridge] (6.45,2.90) -- (13.45,2.90);
\node[tk, anchor=east] at (6.36,2.90) {$-13$};

% Row 2: Hamming fade
\draw[curve] plot [smooth] coordinates {(0.54,0.70) (1.00,0.5) (2.00,1.3) (2.50,0.6) (3.00,0.8) (4.31,0.7)};
\draw[ax] (0.06,0.70) -- (5.41,0.70);
\node[lab, text=black!74, anchor=west] at (0.06,1.58) {khung hình sau khi nhân cửa sổ Hamming};
\draw[ax] (6.45,1.88) -- (6.45,0.10);
\draw[ax] (6.45,0.10) -- (13.69,0.10);
\node[tk, anchor=north] at (6.45,0.05) {$0$};
\node[tk, anchor=north] at (13.45,0.05) {$500$};
\node[tk, anchor=west] at (13.73,0.10) {Hz};
\draw[black!40, thin, densely dotted] (9.95,0.10) -- (9.95,1.57);
\node[tk, anchor=north] at (9.95,0.05) {$250$};
\draw[curve] plot [smooth] coordinates {(6.45,0.1) (8.5,0.15) (9.3,0.8) (9.95,1.57) (10.6,0.8) (11.5,0.15) (13.45,0.1)};
\draw[dim] (8.83,1.71) -- (11.07,1.71);
\node[lab, anchor=south] at (9.95,1.73) {$160$ Hz};
\draw[ridge] (6.45,0.26) -- (13.45,0.26);
\node[tk, anchor=east] at (6.36,0.26) {$-44$};
\end{tikzpicture}
```
So sánh giữa cắt thẳng chữ nhật (hàng trên) và nhân cửa sổ Hamming (hàng dưới). Cắt thẳng tạo búp sóng chính hẹp ($80\text{ Hz}$) nhưng búp sóng phụ cực kỳ cao (chỉ cách đỉnh $-13\text{ dB}$), gây rò rỉ phổ nặng nề. Cửa sổ Hamming chấp nhận nới rộng búp sóng chính lên $160\text{ Hz}$ để dìm búp sóng phụ xuống $-44\text{ dB}$, triệt tiêu hoàn toàn sóng hài giả.
:::

#### Tình thế lưỡng nan chưa giải quyết: Hiện thực kiểm chứng trên silicon (The Silicon Reality Check)

Chúng ta đã hoàn thiện toàn bộ công thức toán học biến $400$ mẫu áp suất không khí thành $80$ giá trị Log-Mel. Trên máy tính phát triển mạnh mẽ, các công thức này chạy trơn tru trong môi trường Python khoa học. Nhưng điều gì sẽ xảy ra khi chuỗi toán học này bị đẩy xuống một vi mạch nhúng hoạt động dưới giới hạn nhiệt ngặt nghèo ($< 15\text{ W}$) với hạn chót cứng $10\text{ ms}$? GPU biên hay FPGA không gian sẽ đảm bảo được các ràng buộc kiến trúc này? Điều đó đưa ta rời trang giấy toán học để bước vào thế giới vật lý của chất bán dẫn.


## 1.4 Hệ Quả Phần Cứng & Giới Hạn Độ Trễ Xử Lý

#### Cầu nối hữu cơ từ Phần 1.3: Ánh xạ phương trình lên bóng bán dẫn vật lý

Ở Phần 1.3, chúng ta đã hoàn thiện mô hình toán học của khối DSP front-end. Nhưng một thuật toán trên giấy có bộ nhớ vô hạn và thời gian thực thi bằng 0. Trong phần này, chúng ta buộc các phương trình toán học phải va chạm với các bóng bán dẫn thực tế: so sánh đặc tính kiến trúc của Edge GPU (NVIDIA Jetson Orin Nano) với Fabric không gian của FPGA (AMD Xilinx Kria KV260).

### Độ trễ luôn có một mức sàn vật lý, và đó không phải do bộ xử lý

Ba đại lượng thời gian được ấn định trực tiếp từ cấu hình âm học trước khi có bất kỳ phần cứng nào tồn tại:

| Đại lượng | Giá trị | Nguồn gốc xác lập |
| :--- | :--- | :--- |
| Thời gian tích lũy khung hình đầu tiên | 25 ms | $L/f_s = 400/16{,}000$ |
| Chu kỳ bước nhảy giữa các khung | 10 ms | $H/f_s = 160/16{,}000$ |
| Tỉ lệ chồng lấn giữa các khung kề nhau | 60% | $(L-H)/L = 240/400$ |

Hệ quả là một mức sàn độ trễ mà không một bộ xử lý siêu máy tính nào có thể xóa bỏ: khung hình đầu tiên **về mặt vật lý không thể tồn tại** trước khi 25 ms âm thanh thực tế đi vào micrô. Sau đó, cứ mỗi 10 ms sẽ có một khung hình mới xuất hiện. Một con chip nhanh hơn không làm giảm con số 25 ms đó; nó chỉ không làm cộng thêm độ trễ vào đó mà thôi.

### Bộ nhớ, đối chiếu với dung lượng phần cứng thực tế

Các thông số phần cứng dưới đây được trích xuất từ tài liệu kỹ thuật chính thức AMD DS890 cho dòng chip Zynq UltraScale+ `XCK26` trên kit Kria KV260:

- **117,120** logic cell LUT (Lookup Table - phần tử logic cơ bản).
- **144** khối Block RAM 36-kilobit (tổng dung lượng $5.1\text{ Mb} \approx 648\text{ KiB}$).
- **64** khối UltraRAM (tổng dung lượng $18.0\text{ Mb} \approx 2.25\text{ MiB}$).
- **1,248** lát cắt tính toán DSP48E2 chuyên dụng cho phép nhân-cộng.

Bây giờ hãy đối chiếu với hai đối tượng mà khối DSP front-end thực sự cần lưu trữ ở định dạng FP32:
- **Bộ đệm xoay vòng 400 mẫu**: Tốn $1{,}600\text{ byte}$ $\implies$ Chiếm $34.7\%$ dung lượng của DUY NHẤT MỘT khối Block RAM 36Kb ($4{,}608\text{ byte}$).
- **Ma trận trọng số Mel $80 \times 257$**: Tốn $82{,}240\text{ byte} = 80.3\text{ KiB}$ $\implies$ Chiếm $12.4\%$ tổng dung lượng Block RAM toàn chip.

### Bản chất bài toán không nằm ở số lượng phép tính thô

Tầng lọc Mel tiêu tốn $20{,}560$ phép nhân-cộng (MAC) mỗi khung hình, tương đương $2.056\text{ triệu}$ phép tính mỗi giây. Trải đều trên $1{,}248$ lát cắt DSP của FPGA, mỗi lát cắt chỉ cần gánh vỏn vẹn $1{,}647$ phép tính mỗi giây. 

Ở phía đối thủ NVIDIA Jetson Orin Nano Super, năng lực xử lý danh định lên tới 67 sparse INT8 TOPS (hoặc khoảng 33 dense TOPS ở mức tiêu thụ 25W). So với con số đó, nhu cầu $2.056\text{ triệu}$ phép tính/giây của front-end chỉ chiếm một phần triệu tỉ lệ băng thông tính toán của GPU!

Do đó, lý do để chuyển dịch khối front-end âm thanh sang logic khả trình FPGA **hoàn toàn không phải vì bài toán thiếu thông lượng tính toán (throughput)**. Đó là bài toán về **hạn chót tất định và sự cô lập can nhiễu (deadline & deterministic execution)**:
- Trên GPU/CPU, khối tiền xử lý âm thanh phải chen chúc chạy chung trong quỹ thời gian 10 ms với driver micrô, ngăn xếp mạng, hệ điều hành Linux và mô hình nơ-ron. Một hạn chót bị chia sẻ cho bốn tác vụ phần mềm là một hạn chót chắc chắn sẽ bị trễ ngẫu nhiên (jitter).
- Trên phần cứng FPGA chuyên dụng, khối DSP có dây dẫn và xung nhịp riêng biệt: nó luôn luôn cán đích đúng 10 ms vì nó sở hữu đường dây bán dẫn độc quyền.

#### Tình thế lưỡng nan chưa giải quyết: Kiểm chứng biên phần cứng dưới áp lực

Chúng ta đã thiết lập và chứng minh sự tương đương toán học của khối tiền xử lý âm thanh dạng dòng. Nhưng người kỹ sư phần cứng biên hiểu rằng các công thức toán học sẽ bộc lộ điểm gãy khi bị ép vào các giới hạn tài nguyên silicon hữu hạn. Điều gì xảy ra nếu tăng tần số lấy mẫu lên chuẩn phòng thu? Điều gì xảy ra nếu cố tình thu hẹp khung cửa sổ để giảm độ trễ? Bốn kịch bản chẩn đoán sau đây sẽ thử tải các giả định lý thuyết của chúng ta.

---

## 1.5 Bài Tập: Bốn Kịch Bản Chẩn Đoán Kiểm Tra Giới Hạn

#### Cầu nối hữu cơ từ Phần 1.4: Thử tải các giới hạn phần cứng tại biên

Lý thuyết chỉ ra cách một chuỗi xử lý vận hành trong điều kiện lý tưởng; kỹ nghệ phần cứng bộc lộ nơi nó sụp đổ khi bị đẩy tới các biên vận hành. Bốn kịch bản chẩn đoán dưới đây không phải là bài tập sách giáo khoa trừu tượng, mà là bốn hình thái thất bại kinh điển mà các đội ngũ kỹ sư nhúng thường gặp phải khi di trú thuật toán lên chip:

- **Ảo tưởng tần số lấy mẫu (The Sampling Rate Illusion)**: Vạch trần việc nâng tần số lấy mẫu lên chuẩn phòng thu làm phình to bộ nhớ và logic mà không tăng thêm độ chính xác nhận dạng từ khóa.
- **Hình phạt bất định Gabor-Heisenberg (The Gabor-Heisenberg Penalty)**: Minh chứng hiện tượng nhòe mờ phổ khi cố tình thu ngắn khung phân tích để ép độ trễ.
- **Cái bẫy biến đổi rời rạc trực tiếp (The Discrete Transform Trap)**: Định lượng lý do vì sao tính toán DFT trực tiếp làm phá sản tài nguyên DSP so với cấu trúc FFT lũy thừa 2 có đệm số không.
- **Điểm nghẽn ma trận dày đặc (The Dense Matrix Bottleneck)**: Chứng minh cách nén ma trận Mel thưa giải phóng tài nguyên Block RAM quý giá trên chip.

> **Bài tập 1 (Kịch bản) -- Tần số lấy mẫu, bộ nhớ đệm và giới hạn Nyquist.**  
> Một kỹ sư đề xuất nâng tần số lấy mẫu front-end từ $f_s = 16\text{ kHz}$ lên chuẩn phòng thu $f_s = 48\text{ kHz}$ với lập luận giữ lại chi tiết âm thanh tinh tế hơn. Hệ thống duy trì độ dài khung $25\text{ ms}$ và bước nhảy $10\text{ ms}$.  
> (a) Tính độ dài khung mới $L_{48}$ và bước nhảy mới $H_{48}$ theo số lượng mẫu.  
> (b) Nếu bộ đệm xoay vòng lưu trữ mẫu FP32 (4 byte), tính kích thước bộ đệm mới và xác định cần bao nhiêu khối Block RAM 36Kb ($4{,}608\text{ byte}$) trên KV260.  
> (c) Dựa vào định lý Nyquist và âm học tiếng nói, hãy giải thích vì sao việc tăng tần số lấy mẫu gấp ba làm tăng gấp ba lưu lượng bộ nhớ và phép tính DSP nhưng không đem lại lợi ích nhận dạng ngữ âm.
>
> **Lời giải.**  
> (a) Tại $f_s = 48\text{ kHz}$, chu kỳ mẫu là $1/48{,}000\text{ s} \approx 20.833\ \mu\text{s}$. Độ dài khung mới $L_{48} = 48{,}000 \times 0.025 = 1{,}200\text{ mẫu}$. Bước nhảy mới $H_{48} = 48{,}000 \times 0.010 = 480\text{ mẫu}$. Cả hai đại lượng đều tăng gấp ba lần so với gốc 16 kHz ($L=400, H=160$).  
> (b) Tại 4 byte/mẫu, bộ đệm cần $1{,}200 \times 4 = 4{,}800\text{ byte}$. Một khối BRAM 36Kb chứa $4{,}608\text{ byte}$. Vì $4{,}800 > 4{,}608$, bộ đệm bị tràn và bắt buộc phải tốn tới **2 khối Block RAM** riêng biệt.  
> (c) Theo định lý Nyquist-Shannon, $f_s = 48\text{ kHz}$ thu được tần số lên tới $24\text{ kHz}$. Tuy nhiên, toàn bộ formant và phụ âm tiếng nói con người tập trung dưới $8\text{ kHz}$. Dải từ $8\text{ kHz}$ đến $24\text{ kHz}$ chỉ chứa tiếng rít siêu âm của môi trường. Tăng $f_s$ buộc phép biến đổi FFT phải tăng lên ít nhất $N = 2{,}048$ điểm, làm tăng số phép tính bướm FFT lên hơn 4 lần mà hoàn toàn không tăng thêm độ chính xác nhận dạng từ khóa.

> **Bài tập 2 (Kịch bản) -- Độ phân giải thời gian - tần số và bất định Gabor-Heisenberg.**  
> Để ép sàn độ trễ xuống dưới $25\text{ ms}$, một nhà thiết kế giảm độ dài cửa sổ phân tích từ $L = 400$ mẫu ($25\text{ ms}$) xuống $L = 80$ mẫu ($5\text{ ms}$) ở $f_s = 16\text{ kHz}$.  
> (a) Tính độ rộng dải thông búp sóng chính $\Delta f \approx 1/\Delta t$ của cửa sổ phân tích ở cả hai trường hợp $25\text{ ms}$ và $5\text{ ms}$.  
> (b) Trong nguyên âm con người, hai formant kề nhau ($F_1$ và $F_2$) có thể chỉ cách nhau $150\text{ Hz}$ đến $250\text{ Hz}$. Điều gì xảy ra với các đỉnh formant trên phổ năng lượng khi $\Delta t = 5\text{ ms}$?  
> (c) Vì sao quán tính sinh học của bộ máy phát âm khiến cửa sổ $5\text{ ms}$ trở nên phản tác dụng?
>
> **Lời giải.**  
> (a) Độ rộng búp sóng chính tỉ lệ nghịch với thời gian: Ở $\Delta t = 25\text{ ms}$, $\Delta f \approx 1/0.025 = 40\text{ Hz}$ (hoặc $\approx 80\text{ Hz}$ giữa hai điểm triệt tiêu của cửa sổ Hamming). Ở $\Delta t = 5\text{ ms}$, độ rộng búp sóng bị nhòe rộng ra tới $\Delta f \approx 1/0.005 = 200\text{ Hz}$ (hoặc $\approx 400\text{ Hz}$ giữa hai điểm triệt tiêu).  
> (b) Khi $\Delta f \approx 200\text{ Hz}$, bộ lọc hoàn toàn mất khả năng phân giải hai đỉnh phổ cách nhau $150 - 200\text{ Hz}$. Hai đỉnh formant $F_1$ và $F_2$ sẽ hòa lẫn vào nhau thành một khối mờ nhạt duy nhất, phá hủy hoàn toàn các đặc trưng âm học mà mạng nơ-ron dựa vào để phân biệt nguyên âm (như phân biệt /i/ với /u/).  
> (c) Các cơ quan phát âm (lưỡi, môi, hàm) không thể chuyển động nhanh hơn $20 - 30\text{ ms}$ do giới hạn cơ bắp sinh học. Cửa sổ $5\text{ ms}$ thậm chí còn ngắn hơn chu kỳ dao động thanh quản của giọng nam trầm ($1/85\text{ Hz} \approx 11.8\text{ ms}$), nghĩa là cửa sổ chỉ chộp được một phần của một nhịp đóng mở dây thanh âm, khiến năng lượng phổ đo được trồi sụt dữ dội tùy thuộc vào việc nó bắt trúng lúc thanh quản đóng hay mở, gây mất ổn định trầm trọng cho vector đặc trưng.

> **Bài tập 3 (Kịch bản) -- Đệm số không FFT so với tính toán DFT trực tiếp trên FPGA.**  
> Cửa sổ phân tích cung cấp $L = 400$ mẫu, nhưng kiến trúc chuẩn đệm thêm số 0 thành $N = 512$ điểm trước khi biến đổi phổ.  
> (a) Tính số phép nhân-cộng phức cần thiết để tính toán DFT trực tiếp trên 400 mẫu cho 201 dải tần số độc lập theo công thức $X[k] = \sum_{n=0}^{L-1} x[n] e^{-j 2\pi k n / L}$.  
> (b) Tính số phép tính phức cho thuật toán FFT radix-2 Cooley-Tukey trên mảng 512 điểm theo công thức $\frac{N}{2}\log_2 N$.  
> (c) So sánh chi phí phần cứng: vì sao đệm thêm 112 số không để nâng lên 512 lại tiết kiệm tài nguyên silicon vượt trội so với giữ nguyên 400 điểm?
>
> **Lời giải.**  
> (a) Đánh giá DFT trực tiếp 201 bin từ 400 mẫu đòi hỏi $201 \times 400 = 80{,}400$ phép nhân-cộng phức mỗi khung hình.  
> (b) Thuật toán FFT radix-2 trên $N = 512$ điểm đòi hỏi $\frac{512}{2} \log_2(512) = 256 \times 9 = 2{,}304$ phép tính bướm (butterfly operations).  
> (c) Tính toán 512 điểm qua FFT chỉ tốn $2{,}304$ phép tính so với $80{,}400$ của DFT trực tiếp — giảm tới **34.9 lần khối lượng tính toán**. Trên FPGA, thuật toán DFT bậc $\mathcal{O}(L^2)$ sẽ ngốn sạch hàng trăm lát cắt DSP48E2 chạy song song hoặc làm nghẽn hàng ngàn chu kỳ xung nhịp. Trong khi đó, FFT radix-2 có cấu trúc đệ quy đồng nhất, ánh xạ hoàn hảo lên chuỗi pipeline nhỏ gọn gồm vài DSP và thanh ghi dịch Block RAM. Đệm 112 số không tốn 0 phép tính, không sinh thêm thông tin giả, nhưng mở khóa một bước nhảy vọt về tiết kiệm diện tích silicon và năng lượng.

> **Bài tập 4 (Kịch bản) -- Nén ma trận ngân hàng lọc Mel thưa và định cỡ bộ nhớ trên chip.**  
> Phép lọc Mel tính $E_\ell[m] = \sum_{k=0}^{256} g_m[k] P_\ell[k]$ cho $M = 80$ dải từ $K = 257$ bin phổ. Nếu lưu dưới dạng ma trận dày đặc FP32 (4 byte), trọng số chiếm $80 \times 257 \times 4 = 82{,}240\text{ byte}$ ($80.3\text{ KiB}$).  
> (a) Vì mỗi bộ lọc tam giác $g_m[k]$ chỉ khác 0 trong khoảng từ bin $k_{m-1}$ đến $k_{m+1}$, mỗi dải chỉ trùm lên trung bình $6.4$ bin hoạt động. Tính số lượng hệ số thực sự khác 0 trên toàn bộ 80 dải.  
> (b) Nếu mỗi hệ số khác 0 được lượng tử hóa sang số nguyên 16-bit (INT16, 2 byte) và lưu kèm chỉ số bin bắt đầu $k_{\min}$ cùng độ dài dải $K_m$ (1 byte mỗi trường), tính tổng dung lượng bộ nhớ nén theo byte.  
> (c) So sánh biểu diễn nén này với dung lượng một khối Block RAM 36Kb ($4{,}608\text{ byte}$) trên KV260 và đánh giá mức độ giảm băng thông truy cập.
>
> **Lời giải.**  
> (a) Với các tam giác chồng lấn $50\%$, tổng số hệ số khác 0 trên toàn bộ 80 dải là khoảng $2 \times 257 \approx 514$ hệ số (hoặc $80 \times 6.4 \approx 512$ trọng số).  
> (b) Lưu trữ 514 hệ số INT16 tốn $514 \times 2 = 1{,}028\text{ byte}$. Lưu 80 cặp siêu dữ liệu ($k_{\min}, K_m$) tốn $80 \times 2 = 160\text{ byte}$. Tổng bộ nhớ nén là $1{,}028 + 160 = 1{,}188\text{ byte}$.  
> (c) Ma trận dày đặc chưa nén ($82{,}240\text{ byte}$) đòi hỏi $82{,}240 / 4{,}608 \approx 18$ khối Block RAM (chiếm tới $12.5\%$ toàn bộ BRAM của chip KV260). Biểu diễn nén thưa ($1{,}188\text{ byte}$) chỉ chiếm $1{,}188 / 4{,}608 \approx 25.8\%$ dung lượng của **DUY NHẤT MỘT khối Block RAM**, giảm dung lượng bộ nhớ tới **69.2 lần**, giải phóng 17 khối BRAM cho bộ nhớ đệm trọng số mô hình nơ-ron và cắt giảm số lần đọc bộ nhớ từ $20{,}560$ lần xuống chỉ còn $514$ lần đọc mỗi khung hình.


---

## 1.6 Từ Nhận Dạng Đến Đánh Giá: Cơ Sở Thuật Toán Của Tương Quan Âm Thanh (Audio Correlation)

Mọi nội dung trong chương này cho đến thời điểm hiện tại đều tập trung xây dựng một cỗ máy biến đổi sóng áp suất không khí liên tục thành một dòng các vector đặc trưng có kích thước cố định: 80 giá trị năng lượng Log-Mel mỗi khung, được sản xuất đều đặn mỗi 10 ms. Trong các hệ thống giọng nói tiêu chuẩn, những vector đặc trưng đó đi theo một lộ trình quen thuộc: chúng nạp vào mô hình âm học nhận dạng giọng nói tự động (ASR - Automatic Speech Recognition) để giải mã ra chuỗi văn bản tương ứng.

Tuy nhiên, trong bài toán đánh giá năng lực đọc và luyện phát âm ngoại ngữ, lộ trình nhận dạng truyền thống này vấp phải một rào cản mang tính bản chất. Khi một học sinh nhỏ tuổi hoặc người học ngôn ngữ đọc to một đoạn văn bản, việc đưa âm thanh của họ vào một mô hình ASR thông thường thường dẫn đến hiện tượng "ảo giác" (hallucination) thảm họa. Do các mô hình âm học bị chi phối bởi xác suất tiên nghiệm của mô hình ngôn ngữ (Language Model priors), bộ máy ASR có xu hướng tự động "sửa sai" phát âm lệch lạc của học sinh thành từ ngữ chuẩn xác mà nó kỳ vọng, hoặc ngược lại, xuất ra một từ hoàn toàn xa lạ khi đối mặt với ngữ điệu lạ lẫm của trẻ em hoặc tiếng ồn lớp học.

Trong đánh giá đọc thành tiếng, hệ thống hoàn toàn không cần phải đoán xem học sinh đang cố gắng nói từ gì: **văn bản tham chiếu đã được biết trước 100%**. Nhiệm vụ sư phạm ở đây không phải là phiên âm (transcription); đó là **đánh giá quỹ đạo âm học (trajectory evaluation)**. Hệ thống phải đo đạc chính xác khoảng cách vật lý, âm học và ngữ điệu giữa quỹ đạo phát âm của học sinh so với bản ghi âm giọng đọc chuẩn mực của giáo viên.

> 💡 **MỤC TIÊU HỌC TẬP**  
> Thay vì xem đánh giá tiếng nói như một mô hình học máy hộp đen bí ẩn, phần này dẫn dắt người học qua hành trình khám phá có tính quy nạp về việc so sánh giọng nói: từ sự rung động cơ học của dây thanh âm ($F_0$) đến thảm họa sụp đổ pha của phép nội suy co giãn tuyến tính, và cuối cùng là sự tao nhã toán học của thuật toán Dynamic Time Warping (DTW) được tăng tốc song song trên silicon FPGA.

---

### 1.6.1 Đường Cơ Sở Ngữ Điệu Âm Học: Dò Cao Độ (Pitch Tracking) và Tương Quan Pearson

#### Cầu nối hữu cơ từ Phần 1.5: Tình thế lưỡng nan của bài toán đánh giá

Ở các phần trước, chúng ta đã xây dựng chuỗi DSP để biến đổi âm thanh thành các vector phổ 80 chiều Log-Mel nhằm trả lời câu hỏi: *Những từ ngữ nào đã được nói ra?* 

Nhưng trong luyện nói và trị liệu ngôn ngữ, bài toán đánh giá quỹ đạo đòi hỏi trả lời câu hỏi: *Học sinh đã phát âm chuẩn xác, trôi chảy và biểu cảm như thế nào so với giáo viên bản xứ?*

Đôi tai con người khi lắng nghe lời nói luôn phân biệt hai chiều kích âm học độc lập:
1. **Khẩu hình ngữ âm (Phonetic articulation)**: Từng phụ âm và nguyên âm có được phát âm chuẩn xác hay không?
2. **Ngữ điệu và trường độ (Prosody and intonation)**: Cao độ của giọng nói có trầm bổng đúng lúc để biểu đạt ngữ pháp, trọng âm và cảm xúc hay không?

Để đánh giá một bài đọc, trực giác đầu tiên của chúng ta là đo đạc giai điệu âm nhạc của giọng nói — tức **ngữ điệu (intonation)**. Điều này dẫn ta tới câu hỏi quy nạp đầu tiên: *Làm thế nào một cảm biến kỹ thuật số có thể đo được giai điệu của giọng nói con người?*

#### Khám phá quy nạp: Đồng hồ đo tốc độ của bộ máy phát âm

Hãy tưởng tượng bạn đang nói vào micrô trong khi đặt nhẹ hai đầu ngón tay lên thanh quản (yết hầu) của mình. Khi bạn phát ra một âm hữu thanh (như nguyên âm "a"), ngón tay bạn thực sự cảm nhận được điều gì? Bạn cảm nhận được một sự rung động dồn dập, liên tục. Bên trong thanh quản, hai nếp gấp cơ bắp — dây thanh âm — liên tục khép chặt lại rồi bị áp suất luồng khí từ phổi thổi bùng ra hàng chục đến hàng trăm lần mỗi giây, băm dòng khí liên tục thành các xung áp suất khí động học rời rạc. Tốc độ rung cơ học này được gọi là **Tần số Cơ bản ($F_0$ - Fundamental Frequency)**, được thính giác con người cảm nhận dưới dạng **cao độ (pitch)**.

Giống như chiếc kim đồng hồ trên xe máy đo tốc độ di chuyển tức thời, thuật toán dò pitch đo đạc tần số dao động tức thời của dây thanh âm. Bằng cách trượt một bản sao của tín hiệu âm thanh trên chính nó thông qua **hàm tự tương quan (autocorrelation)**:
$$R_x(\tau) = \sum_{n=0}^{W-1} x[n] \, x[n + \tau]$$
Thuật toán tìm ra độ trễ thời gian $\tau$ tại điểm cực đại của hàm tương quan, từ đó suy ra chu kỳ dao động $T_0$ và tần số cơ bản:
$$F_0 = \frac{f_s}{\tau_{\text{peak}}}$$

#### Đo lường sự tương đồng ngữ điệu: Hệ số tương quan Pearson

Sau khi trích xuất được chuỗi cao độ của học sinh $X = \{x_1, x_2, \dots, x_N\}$ và chuỗi cao độ của giáo viên $Y = \{y_1, y_2, \dots, y_N\}$, làm thế nào để chấm điểm độ tương đồng về mặt giai điệu?

Công cụ toán học cổ điển và trực quan nhất là **Hệ số Tương quan Pearson ($r$)**:

> **Công thức.**
> $$r = \frac{\sum_{i=1}^N (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^N (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^N (y_i - \bar{y})^2}}$$
>
> **Ý nghĩa.** Hệ số $r \in [-1, 1]$ đo lường mức độ đồng điệu về mặt xu hướng dao động giữa hai đường cong. Nếu khi giáo viên lên giọng ($y_i > \bar{y}$) mà học sinh cũng lên giọng ($x_i > \bar{x}$), tích số dương $\implies r \to +1$. Điểm ưu việt tuyệt đối của Pearson là nó trừ đi giá trị trung bình ($\bar{x}, \bar{y}$), giúp thuật toán **hoàn toàn miễn nhiễm với sự chênh lệch cao độ sinh học giữa người lớn và trẻ em** (người lớn giọng trầm quanh $120\text{ Hz}$, trẻ em giọng the thé quanh $250\text{ Hz}$ vẫn đạt $r = 1.0$ nếu biểu cảm ngữ điệu giống nhau).

---

### 1.6.2 Cú Va Chạm: Vì Sao Co Giãn Tuyến Tính Thất Bại Thảm Hại?

#### Thảm họa co giãn thước đo sắt (The Iron Ruler Fallacy)

Nhưng ở đây xuất hiện một rào cản toán học không thể vượt qua nếu dùng tư duy tuyến tính ngây thơ:
- Câu đọc của cô giáo kéo dài $1.0\text{ s}$ ($100$ khung hình).
- Câu đọc của học sinh nhỏ tuổi kéo dài $1.8\text{ s}$ ($180$ khung hình).

Công thức Pearson bắt buộc hai mảng số phải có cùng độ dài $N$. Trực giác sơ khai của các kỹ sư là: *Tại sao không dùng phép nội suy tuyến tính (Linear Resampling) để kéo giãn hoặc ép mảng của học sinh cho khớp với độ dài của cô giáo như một chiếc thước đo bằng sắt?*

Hãy làm một **thí nghiệm phản chứng thực tế** trong lớp học:
- **Cô giáo đọc chuẩn**: *"Good morning"* trong $1.0\text{ s}$. Cô đọc từ *"Good"* trong $0.35\text{ s}$ với ngữ điệu đi lên ($160 \to 190\text{ Hz}$), rồi đọc *"morning"* trong $0.65\text{ s}$ với ngữ điệu đi xuống ($175 \to 120\text{ Hz}$).
- **Học sinh đọc ngập ngừng**: *"Gooood... morning"* trong $1.8\text{ s}$. Em bé hơi rụt rè nên ngân dài nguyên âm /u/ trong từ *"Good"* mất tới $1.1\text{ s}$ ($61\%$ tổng thời gian câu), sau đó em đọc từ *"morning"* rất chuẩn trong $0.7\text{ s}$ ($39\%$). Em lên giọng ở *"Good"* và xuống giọng ở *"morning"* hoàn toàn đúng lời cô dạy.

Bây giờ hãy xem thuật toán co giãn tuyến tính xử lý âm thanh của em:
1. **Tiếng nói là dải cao su đàn hồi, không phải chiếc thước sắt!** Khi con người nói chậm lại, họ chỉ kéo dài các **nguyên âm** (như /u/, /a/ vốn có luồng khí thở duy trì liên tục). Con người **không thể kéo dài các phụ âm tắc** (như âm bật /d/, /t/ vốn bị khống chế bởi động học cơ miệng chỉ diễn ra trong $20 - 30\text{ ms}$). Thước đo tuyến tính ép mọi âm vị phải giãn đều một tỉ lệ như nhau, vi phạm thô bạo cơ chế sinh học phát âm.
2. **Thảm họa nghịch đảo pha (Phase Inversion Disaster):** 
   - Trong âm thanh cô giáo, từ *"Good"* kết thúc ở khung $35\%$. Tại khung $45\%$, cô giáo đã sang từ *"morning"* và cao độ đang lao dốc: $(y_{45} - \bar{y}) < 0$.
   - Trong âm thanh học sinh bị ép thẳng tuyến tính, vì từ *"Good"* chiếm tới $61\%$ thời gian thực, nên tại khung $45\%$, em bé **vẫn đang ngân nga từ "Good"** và cao độ đang đi lên: $(x_{45} - \bar{x}) > 0$!
   - Tích số Pearson tại khung 45 trở thành: $(\text{Dương}) \times (\text{Âm}) = \mathbf{\text{ÂM}}$!
   - Thay vì so sánh *"Good"* với *"Good"*, chiếc thước sắt đã ép cao độ đi lên của từ *"Good"* phải nhân với cao độ đi xuống của từ *"morning"*.
   - **Hệ quả số học**: Hệ số Pearson sụp đổ thảm hại xuống **$r \approx -0.42$** (Tương quan nghịch sâu sắc)!

Hệ thống chấm điểm tự động lập tức báo đèn đỏ và thông báo: *"Ngữ điệu sai hoàn toàn. Bạn bị 0 điểm!"* Trong khi đứa trẻ phát âm từng từ chuẩn xác và biểu cảm rất đúng. **Thuật toán đã trừng phạt đứa trẻ chỉ vì một chiếc thước đo tuyến tính cứng nhắc không thể hiểu được tính đàn hồi của giọng nói!**

::: {#fig-ch1-elastic-alignment .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  box/.style={draw=black!80, font=\scriptsize, align=center},
  badbox/.style={draw=black!80, fill=black!15, font=\scriptsize, align=center, inner sep=5pt},
  goodbox/.style={draw=black!80, fill=black!5, font=\scriptsize, align=center, inner sep=5pt},
  warpar/.style={-{Stealth[length=1.5mm]}, black!75, semithick},
  link/.style={densely dashed, black!40, thin},
  badlink/.style={densely dashed, black!80, semithick},
  ttl/.style={font=\small\bfseries, text=black!90, align=left},
  subttl/.style={font=\footnotesize\itshape, text=black!70, align=left},
  ann/.style={font=\scriptsize, text=black!80, align=right},
  scale=0.92
]

% ================= Panel (a): Thước đo sắt (Nội suy tuyến tính) =================
\node[ttl, anchor=west] at (0, 7.7) {(a) Thước Đo Sắt: Co Giãn Tuyến Tính Gây Sụp Đổ Pha};
\node[subttl, anchor=west] at (0, 7.25) {Câu nói bị kéo giãn đồng đều, ép các âm vị lệch qua ranh giới từ vựng.};

\node[ann, anchor=east] at (-0.15, 6.0) {Học sinh ($1.8\,\mathrm{s} \to 100\%$):};
\draw[box, fill=black!15] (0, 5.55) rectangle (3.78, 6.45) 
  node[midway] {\textbf{``Gooood\dots''}\\[-0.5mm]{\tiny nguyên âm /u/, 61\%}};
\draw[box, fill=black!8] (3.78, 5.55) rectangle (6.20, 6.45) 
  node[midway] {\textbf{``morning''}\\[-0.5mm]{\tiny 39\%}};

\node[ann, anchor=east] at (-0.15, 4.2) {Cô giáo ($1.0\,\mathrm{s} \to 100\%$):};
\draw[box, fill=black!12] (0, 3.75) rectangle (2.17, 4.65) 
  node[midway] {\textbf{``Good''}\\[-0.5mm]{\tiny 35\%}};
\draw[box, fill=black!5] (2.17, 3.75) rectangle (6.20, 4.65) 
  node[midway] {\textbf{``morning''}\\[-0.5mm]{\tiny 65\%}};

\draw[link] (0, 5.55) -- (0, 4.65);
\draw[link] (6.20, 5.55) -- (6.20, 4.65);

\fill[black!20, opacity=0.7] (2.17, 4.65) -- (3.78, 5.55) -- (2.17, 5.55) -- cycle;
\fill[black!20, opacity=0.7] (2.17, 4.65) -- (3.78, 5.55) -- (3.78, 4.65) -- cycle;
\draw[badlink] (2.17, 4.65) -- (2.17, 5.55);
\draw[badlink] (3.78, 4.65) -- (3.78, 5.55);
\draw[badlink] (2.17, 4.65) -- (3.78, 5.55);

\node[fill=white, draw=black!70, inner sep=2pt, font=\tiny\bfseries] at (2.975, 5.1) {VA CHẠM ÂM VỊ};

\node[badbox, text width=4.8cm, anchor=west] at (6.8, 5.1) {
  \textbf{Thảm họa nghịch đảo pha}\\[1mm]
  Ngữ điệu đi lên của ``Good'' va chạm\\
  với ngữ điệu đi xuống của ``morning''.\\
  $\Delta x \cdot \Delta y < 0 \implies \mathbf{r \approx -0.42}$ (Hỏng!)
};

% ================= Panel (b): Dải cao su (Căn chỉnh đàn hồi DTW) =================
\node[ttl, anchor=west] at (0, 3.1) {(b) Dải Cao Su Đàn Hồi: Dynamic Time Warping Khôi Phục Âm Học Thực};
\node[subttl, anchor=west] at (0, 2.65) {Đường uốn nắn phi tuyến hấp thụ nguyên âm ngân dài trong khi khóa chặt ranh giới từ.};

\node[ann, anchor=east] at (-0.15, 1.6) {Học sinh ($1.8\,\mathrm{s}$):};
\draw[box, fill=black!12] (0, 1.15) rectangle (3.78, 2.05) 
  node[midway] {\textbf{``Gooood\dots''}\\[-0.5mm]{\tiny /u/ ngân dài ($1.1\,\mathrm{s}$)}};
\draw[box, fill=black!6] (3.78, 1.15) rectangle (6.20, 2.05) 
  node[midway] {\textbf{``morning''}\\[-0.5mm]{\tiny bình thường ($0.7\,\mathrm{s}$)}};

\node[ann, anchor=east] at (-0.15, -0.1) {Cô giáo ($1.0\,\mathrm{s}$):};
\draw[box, fill=black!10] (0, -0.55) rectangle (1.30, 0.35) 
  node[midway] {\textbf{``Good''}\\[-0.5mm]{\tiny $0.35\,\mathrm{s}$}};
\draw[box, fill=black!5] (1.30, -0.55) rectangle (3.70, 0.35) 
  node[midway] {\textbf{``morning''}\\[-0.5mm]{\tiny $0.65\,\mathrm{s}$}};

\draw[warpar] (0.8, 1.15) -- (0.65, 0.35);
\draw[warpar] (1.8, 1.15) -- (0.65, 0.35);
\draw[warpar] (2.8, 1.15) -- (0.85, 0.35);
\draw[warpar] (3.78, 1.15) -- (1.30, 0.35);

\draw[warpar] (4.5, 1.15) -- (2.1, 0.35);
\draw[warpar] (5.3, 1.15) -- (2.9, 0.35);
\draw[warpar] (6.2, 1.15) -- (3.70, 0.35);

\node[goodbox, text width=4.8cm, anchor=west] at (6.8, 0.8) {
  \textbf{Hòa hợp pha được bảo toàn}\\[1mm]
  Đường gióng $\mathcal{P}$ khớp đúng từng trạng thái âm vị.\\
  Các vector pitch được so sánh cùng pha:\\
  $\Delta \tilde{x} \cdot \Delta \tilde{y} > 0 \implies \mathbf{r_{\mathrm{warped}} \approx +0.94}$ (Đạt!)
};

\end{tikzpicture}
```
Đối chiếu hai trường phái gióng trục thời gian trong đánh giá giọng đọc. Bảng (a) minh chứng sự sụp đổ của phép co giãn tuyến tính: ép thẳng một câu nói làm các âm vị bị đẩy lệch qua ranh giới từ vựng, gây nghịch đảo pha và điểm tương quan âm ($r < 0$). Bảng (b) minh họa việc căn chỉnh đàn hồi bằng DTW: đường uốn nắn phi tuyến hấp thụ trọn vẹn việc ngân dài nguyên âm mà vẫn khóa chặt ranh giới âm học, bảo tồn tương quan đồng pha ($r_{\text{warped}} > 0$).
:::

#### Hai tử huyệt tiếp theo của việc chỉ dùng Pitch $F_0$:
1. **Cái bẫy ngâm nga (The Humming Fallacy - Mù tịt Formant):** Cao độ $F_0$ chỉ đo tốc độ rung của dây thanh quản, hoàn toàn không biết hình dạng khoang miệng hay vị trí của lưỡi (các formant $F_1, F_2, F_3$). Nếu một học sinh ngậm chặt miệng và chỉ ... **ngâm nga (humming) "Ư... ư-ư"** theo đúng giai điệu của cô giáo $\implies$ Thuật toán Pearson trên Pitch vẫn cho điểm tuyệt đối **$r = 0.98$** dù đứa trẻ không phát âm một từ nào!
2. **Vực thẳm vô thanh (The Unvoiced Abyss):** Các phụ âm vô thanh (/s/, /t/, /p/, /k/) không có dao động thanh quản ($F_0 = 0$). Nội suy tuyến tính qua các điểm 0 tạo ra các vách dốc nhân tạo làm méo mó nghiêm trọng công thức thống kê Pearson.

---

### 1.6.3 Bước Đột Phá: Dynamic Time Warping (DTW) và Đánh Giá Đa Tầng

Để thay thế chiếc thước sắt cứng nhắc, chúng ta đưa vào thuật toán **Uốn Nắn Thời Gian Động (Dynamic Time Warping - DTW)** kết hợp với kiến trúc **Đánh giá Đa tầng (Dual-Tier Assessment)**:

1. **Tầng 1 (Căn chỉnh quang phổ âm học):** Dùng ma trận đặc trưng 80 dải Log-Mel để tìm ra đường uốn nắn thời gian phi tuyến tối ưu $\mathcal{P}$. Vì Log-Mel ghi nhận trọn vẹn các formant, nó đập tan hoàn toàn chiêu trò ngậm miệng ngâm nga (Humming) và xử lý mượt mà cả âm vô thanh lẫn hữu thanh.
2. **Tầng 2 (Tương quan ngữ điệu có dẫn đường - DTW-Guided Pearson):** Dùng đường uốn nắn $\mathcal{P}$ đã tìm được ở Tầng 1 để gióng các điểm cao độ $F_0$ của học sinh khớp hoàn hảo với giáo viên, rồi **mới tính toán hệ số tương quan Pearson** trên các cặp đã đồng pha.

#### Hệ thức truy hồi Bellman của DTW:

Tại mỗi tọa độ $(i, j)$ so sánh khung thứ $i$ của học sinh với khung thứ $j$ của giáo viên, khoảng cách âm học cục bộ là khoảng cách Euclidean bình phương trên 80 dải Mel:
$$d(\mathbf{x}_i, \mathbf{y}_j) = \sum_{k=1}^{80} (x_{i,k} - y_{j,k})^2$$

Khoảng cách tích lũy tối ưu $D(i, j)$ được xác định qua nguyên lý quy hoạch động Bellman:
$$D(i, j) = d(\mathbf{x}_i, \mathbf{y}_j) + \min \big\{ D(i-1, j-1), \; D(i-1, j), \; D(i, j-1) \big\}$$

Trong đó ba bước chuyển đại diện cho ba hiện thực vật lý trong giọng nói:
- **Bước chéo $(i-1, j-1)$**: Học sinh và giáo viên phát âm cùng tốc độ.
- **Bước đứng $(i-1, j)$**: Học sinh ngân dài nguyên âm hoặc ngập ngừng trong khi giáo viên đã dừng.
- **Bước ngang $(i, j-1)$**: Học sinh nói lướt hoặc bỏ sót một âm vị có trong câu của giáo viên.

Sau khi quy hoạch động tìm ra đường đi tối ưu $\mathcal{P} = \{(i_k, j_k)\}_{k=1}^P$, ta tính toán hệ số Pearson trên các vector pitch đã được gióng trục:
$$r_{\text{warped}} = \frac{\sum_{k=1}^P (\tilde{x}_k - \bar{\tilde{x}})(\tilde{y}_k - \bar{\tilde{y}})}{\sqrt{\sum_{k=1}^P (\tilde{x}_k - \bar{\tilde{x}})^2} \sqrt{\sum_{k=1}^P (\tilde{y}_k - \bar{\tilde{y}})^2}}$$

Kết quả là hiện tượng nghịch đảo pha bị xóa bỏ hoàn toàn: điểm số của em bé trong ví dụ trên vọt từ thất bại vô lý ($r \approx -0.42$) lên mức công nhận xuất sắc ($r_{\text{warped}} \approx \mathbf{+0.94}$)!

---

### 1.6.4 Cái Giá Phần Cứng: Vì Sao Căn Chỉnh Đàn Hồi Cần Kiến Trúc Không Gian FPGA?

Thuật toán DTW mang lại chiến thắng tuyệt đối về mặt âm học, nhưng nó đặt ra một thách thức tính toán khổng lồ: đối với câu nói 5 giây ($N = M = 500$ khung), ma trận DTW cần đánh giá tới $250{,}000$ ô nhớ lặp tuần tự. Trên vi xử lý ARM nhúng, các vòng lặp lồng nhau với các lệnh rẽ nhánh điều kiện tiêu tốn từ $12\text{ ms}$ đến $18\text{ ms}$ — **làm sụp đổ hoàn toàn hạn chót thời gian thực 10 ms của dòng âm thanh**.

Trên GPU Edge (NVIDIA Jetson Orin), các nhân Tensor Core chỉ thực hiện được phép nhân-cộng ma trận ($A \times B + C$) và bất lực trước phép tìm giá trị nhỏ nhất $\min(a, b, c)$ của Bellman. GPU buộc phải chạy trên các nhân CUDA vạn năng với độ trễ kích hoạt kernel (kernel launch latency $5\ \mu\text{s}$) và hiện tượng phân kỳ luồng (thread divergence).

#### Khai sáng mặt sóng song song (Anti-Diagonal Wavefront Parallelism)

Giải pháp nằm ở hình học phụ thuộc dữ liệu của lưới DTW. Hãy quan sát kỹ: ô $(i, j)$ chỉ phụ thuộc vào ba ô $(i-1, j)$, $(i, j-1)$ và $(i-1, j-1)$.
Nếu ta quan sát các đường phản đường chéo định nghĩa bởi $i + j = k$:
**Tất cả các ô nằm trên cùng một đường phản đường chéo hoàn toàn độc lập với nhau và có thể được tính toán đồng thời trong DUY NHẤT MỘT chu kỳ xung nhịp ([Hình 2](#fig-ch1-wavefront-scheduling))!**

::: {#fig-ch1-wavefront-scheduling .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  cell/.style={draw=black!75, circle, inner sep=1pt, minimum size=10mm, align=center, fill=white, font=\scriptsize},
  wavecell/.style={draw=black!90, circle, inner sep=1pt, minimum size=10mm, align=center, fill=black!15, font=\scriptsize},
  diag/.style={draw=black!35, densely dashed, thin},
  dep/.style={-{Stealth[length=1.4mm]}, black!35, thin},
  scale=0.92
]

\foreach \i in {1,2,3,4} {
  \foreach \j in {1,2,3,4} {
    \ifnum\i>1
      \draw[dep] (\i-1, \j) -- (\i-0.5, \j);
    \fi
    \ifnum\j>1
      \draw[dep] (\i, \j-1) -- (\i, \j-0.5);
    \fi
    \ifnum\i>1
      \ifnum\j>1
        \draw[dep] (\i-1, \j-1) -- (\i-0.35, \j-0.35);
      \fi
    \fi
  }
}

\draw[diag] (0.5, 1.5) -- (1.5, 0.5) node[below right, font=\tiny, text=black!60] {$t{=}1$};
\draw[diag] (0.5, 2.5) -- (2.5, 0.5) node[below right, font=\tiny, text=black!60] {$t{=}2$};
\draw[diag] (0.5, 3.5) -- (3.5, 0.5) node[below right, font=\tiny, text=black!60] {$t{=}3$};
\draw[draw=black!85, semithick, dashed] (0.45, 4.55) -- (4.55, 0.45) node[below right, font=\tiny\bfseries, text=black!90] {$t{=}4$};
\draw[diag] (1.5, 4.5) -- (4.5, 1.5) node[above right, font=\tiny, text=black!60] {$t{=}5$};
\draw[diag] (2.5, 4.5) -- (4.5, 2.5) node[above right, font=\tiny, text=black!60] {$t{=}6$};
\draw[diag] (3.5, 4.5) -- (4.5, 3.5) node[above right, font=\tiny, text=black!60] {$t{=}7$};

\node[above=2mm, font=\scriptsize\bfseries, fill=black!12, draw=black!70, rounded corners=2pt, inner sep=2.5pt] at (1.1, 4.6) {Mặt sóng kích hoạt ($t = 4$)};

\foreach \i in {1,2,3,4} {
  \foreach \j in {1,2,3,4} {
    \pgfmathtruncatemacro{\k}{\i + \j - 1}
    \ifnum\k=4
      \node[wavecell] (c\i\j) at (\i, \j) {
        \textbf{$(\i,\j)$}\\[-1mm]
        {\tiny\bfseries t = 4}
      };
    \else
      \node[cell] (c\i\j) at (\i, \j) {
        \textbf{$(\i,\j)$}\\[-1mm]
        {\tiny t = \k}
      };
    \fi
  }
}

\draw[-{Stealth[length=2mm]}, thick, black!75] (0.3, -0.1) -- (4.7, -0.1);
\node[font=\scriptsize\bfseries, text=black!85] at (2.5, -0.7) {Chỉ số khung học sinh $i \longrightarrow$};

\draw[-{Stealth[length=2mm]}, thick, black!75] (-0.1, 0.3) -- (-0.1, 4.7);
\node[font=\scriptsize\bfseries, text=black!85, rotate=90] at (-0.7, 2.5) {Chỉ số khung giáo viên $j \longrightarrow$};

\foreach \i in {1,2,3,4} {
  \node[font=\scriptsize\bfseries, text=black!85] at (\i, -0.35) {$\i$};
}
\foreach \j in {1,2,3,4} {
  \node[font=\scriptsize\bfseries, text=black!85] at (-0.35, \j) {$\j$};
}

\node[draw=black!75, fill=black!4, rounded corners=3pt, inner sep=6pt, text width=5.0cm, align=left, anchor=west] at (5.7, 2.5) {
  \textbf{\large Tính Song Song Mặt Sóng}\\[2mm]
  \textbf{Truy hồi Bellman:}\\
  $D(i,j) = d(i,j) + \min\big(D_{i-1,j},\; D_{i,j-1},\; D_{i-1,j-1}\big)$\\[2mm]
  \textbf{Độc lập dữ liệu:}\\
  Mọi ô được kích hoạt tại nhịp đồng hồ $t$ chỉ phụ thuộc vào các ô từ nhịp $t-1$ và $t-2$.\\[2mm]
  $\implies$ \textbf{Không có phụ thuộc lẫn nhau dọc theo nhịp $t$!}\\[2mm]
  Mảng Systolic trên FPGA tính toán toàn bộ các ô trên đường chéo $k = i+j$ (vùng xám, $t = 4$) \textbf{đồng thời trong 1 chu kỳ xung nhịp}.\\[2mm]
  \textbf{Tổng thời gian thực thi:}\\
  $T_{\mathrm{FPGA}} = N + M - 1 = \mathbf{7\text{ chu kỳ xung nhịp}}$\\
  (so với $4 \times 4 = 16$ bước tuần tự của CPU).
};

\end{tikzpicture}
```
Lập lịch mặt sóng phản đường chéo song song cho quy hoạch động. Mọi ô trên đường $i+j=k$ có thể thực thi đồng thời vì dữ liệu đầu vào của chúng chỉ xuất phát từ các đường chéo đã hoàn tất trước đó. Mảng Systolic trên FPGA tính toán mỗi mặt sóng chỉ trong 1 chu kỳ xung nhịp duy nhất.
:::

Bằng cách hiện thực hóa mặt sóng này lên **Mảng Systolic (Systolic Array)** trên FPGA:
- **Trên CPU tuần tự**: $T_{\text{CPU}} = N \times M = 500 \times 500 = 250{,}000$ bước lặp.
- **Trên FPGA Systolic Array**: $T_{\text{FPGA}} = N + M - 1 = 500 + 500 - 1 = \mathbf{999}$ chu kỳ xung nhịp!

Tại tần số xung nhịp $200\text{ MHz}$ trên AMD Xilinx Kria KV260, 999 chu kỳ xung nhịp được hoàn tất trong:
$$t_{\text{latency}} = \frac{999}{200 \times 10^6\text{ Hz}} \approx \mathbf{4.995}\ \mu\text{s} \quad (\approx 5\text{ micro-giây}!)$$

Tốc độ tính toán nhanh hơn CPU **$2{,}400$ lần**, tiêu thụ chỉ $3.2\text{ W}$, với độ trễ tất định theo từng chu kỳ xung nhịp bán dẫn.

| Tiêu chí so sánh | Co giãn Tuyến tính Pitch (Đề xuất cũ của nhóm) | DTW Chuẩn trên MFCC (Cơ sở âm học) | DTW Dẫn Đường Pitch Pearson (Đề xuất tối ưu của bạn) |
| :--- | :--- | :--- | :--- |
| **Đặc trưng âm thanh** | Đại lượng vô hướng Pitch ($F_0$) | 80 chiều Log-Mel / MFCC | MFCC/Log-Mel (Gióng trục) + $F_0$ (Ngữ điệu) |
| **Mô hình thời gian** | Co giãn tuyến tính bằng thước sắt | Quy hoạch động đàn hồi phi tuyến | Đường uốn nắn đàn hồi phi tuyến |
| **Độ nhạy ngữ âm** | Mù tịt (Không bắt được Formant) | Rất cao (Bắt trọn khẩu hình âm vị) | Tối ưu kép (Cả ngữ âm lẫn ngữ điệu) |
| **Chống gian lận ngâm nga** | Thất bại (Ngâm nga đạt $r=0.98$) | Miễn nhiễm (Phổ âm thanh lệch) | Miễn nhiễm (Khoảng cách âm học bóc trần) |
| **Đứt quãng vô thanh** | Tạo vách dốc giả khi $F_0=0$ | Xử lý tự nhiên trên toàn dải phổ | Lọc bỏ điểm vô thanh khi tính Pearson |
| **Độ trễ thực thi** | $\approx 2\text{ ms}$ (Python CPU) | $\approx 15\text{ ms}$ (CPU) / $\mathbf{5.0}\ \mu\text{s}$ (FPGA) | $\mathbf{5.0}\ \mu\text{s}$ (FPGA DTW) $+ 1\text{ ms}$ (ARM) |
| **Phù hợp phần cứng** | Vi điều khiển / CPU | Mảng Systolic tuyến tính FPGA | Hệ thống Heterogeneous SoC (FPGA + ARM) |

Sự đối chiếu toàn diện này khép lại Phần I của cuốn sách: thấu hiểu tường tận bản chất toán học của tín hiệu là điều kiện tiên quyết bắt buộc để lý giải vì sao ta không thể thỏa hiệp với các phương pháp tuyến tính thô sơ, và vì sao các vi kiến trúc phần cứng chuyên dụng được xây dựng trong Phần II (Chương 4, 6 và 8) lại đóng vai trò sống còn đối với trí tuệ nhân tạo giọng nói thời gian thực tại biên.

---

## Thực Nghiệm Liên Kết
- Tham chiếu mã nguồn tại [`chapter01/`](../chapter01/).
- Nhật ký thực thi và mã băm kiểm tra tính toàn vẹn được lưu giữ tại [`results/exp01/`](../results/exp01/).
