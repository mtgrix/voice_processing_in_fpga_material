# ĐỀ CƯƠNG NGHIÊN CỨU & HỌC TẬP: TĂNG TỐC VOICE AI TỪ GPU SANG FPGA

> ⚠ **BẢN CŨ — ĐÃ ĐƯỢC THAY THẾ.** `plan-v2.md` là đề cương thẩm quyền, và 10 chương trong `book/` nay chiếu theo §7 của nó. File này giữ lại vì giá trị lịch sử và vì `plan-v2.md` dẫn lại lỗi của nó để giải thích quy tắc mới. **Đừng lấy số từ đây**: "4 MB" SRAM KV260 (§3) đã bị `V-01-11` phủ định, "10–30 M tham số" cho Conformer chưa từng được verify, và các claim % không có dẫn xuất — xem `plan-v2.md` §3.3 và §9.1.

> **Mục tiêu dự án / Đề cương Sách (Monograph Spec):** Hệ thống hóa kiến thức và phương pháp luận để chuyển đổi các cấu trúc Voice AI (từ Keyword Spotting đến Streaming Conformer ASR) từ **NVIDIA Jetson Orin (GPU)** sang **FPGA (Kria / Zynq)**.
> **Triết lý Sư phạm (Pedagogy):** Đi từ bản chất toán học/kiến trúc (The Why) đến giải pháp phần cứng (The How). Dựa trên nền tảng thiết kế luận lý số cơ bản (Arithmetic, SRAM, Parameterized Convolution) để mở rộng thành hệ thống gia tốc cấp độ nghiên cứu (Research-grade).

---

## 1. BÀI TOÁN GỐC: TẠI SAO CẦN DỊCH CHUYỂN TỪ GPU SANG FPGA?

*   **Vấn đề cốt lõi (Root Cause):** Hệ thống nhận diện giọng nói thời gian thực (Streaming ASR) đòi hỏi phải xử lý từng khung âm thanh ngay khi thu được $\rightarrow$ Kích thước lô xử lý bằng một (atch_size = 1).
*   **Nút thắt trên GPU (Jetson Orin):** Kiến trúc SIMT (Single Instruction, Multiple Threads) của GPU sinh ra để xử lý các lô dữ liệu khổng lồ nhằm che giấu độ trễ truy cập DRAM (latency hiding). Với atch_size = 1, GPU rơi vào trạng thái **Nghẽn cổ chai băng thông bộ nhớ (Memory-Bandwidth Bound)**. Lõi Tensor Cores rơi vào trạng thái "đói" dữ liệu, dẫn đến hiệu suất tính toán cực thấp (Compute Underutilization) và hao phí năng lượng khổng lồ (10W - 25W).
*   **Giải pháp Kiến trúc (SOTA):** Chuyển sang mô hình **Tính toán không gian (Spatial Dataflow)** trên FPGA. Dữ liệu trôi qua một đường ống (Pipeline) gồm các phần tử xử lý (Processing Elements) nối tiếp nhau. Kết quả tầng này đẩy trực tiếp vào tầng kia mà không cần gom lô (Zero-latency RAM).

---

## CƠ SỞ LÝ THUYẾT VÀ NỀN TẢNG KHOA HỌC (THEORETICAL FOUNDATION)

Để đảm bảo tính chặt chẽ trong thiết kế và tối ưu hóa hệ thống phần cứng, đề cương này được xây dựng dựa trên 4 trụ cột lý thuyết toán học và kiến trúc máy tính tiên tiến nhất hiện nay:

### 1. Mô hình Mái nhà (Roofline Model) và Điểm mù của Kiến trúc GPU
Hiệu năng của một bộ gia tốc phần cứng được đo lường qua **Cường độ Số học (Arithmetic Intensity - $I$)**, định nghĩa là số phép toán dấu phẩy động thực hiện trên mỗi byte dữ liệu truy xuất từ bộ nhớ: $I = \frac{FLOPs}{Bytes}$. 
Theo tài liệu kiến trúc Jetson AGX Orin [R01-01], lõi Tensor Cores mang lại sức mạnh tính toán (Peak FLOPs) khổng lồ. Tuy nhiên, đối với ứng dụng thời gian thực như Streaming Voice AI ($batch_size = 1$), dữ liệu âm thanh trôi qua liên tục và không được tái sử dụng nhiều lần. Cường độ số học $I$ trượt xuống mức rất thấp, đưa hệ thống vào vùng giới hạn băng thông bộ nhớ (Memory-Bound Region) của mô hình Roofline. Kết quả là GPU hoạt động thiếu hiệu quả nghiêm trọng.

### 2. Định lý Tính toán Không gian và Giới hạn Khởi tạo (Initiation Interval - II)
Khác với kiến trúc von Neumann trên vi xử lý thông thường, FPGA sử dụng lý thuyết **Tính toán Không gian (Spatial Dataflow)** [R01-02]. Trong lý thuyết này, độ trễ và thông lượng được quyết định bởi **Khoảng Khởi tạo (Initiation Interval - II)** - số chu kỳ xung nhịp (clock cycles) cần thiết để hệ thống chấp nhận một luồng dữ liệu đầu vào mới. 
Mục tiêu tối thượng của đề cương là xây dựng vi kiến trúc đạt được $II = 1$ (chấp nhận một vector dữ liệu vào mỗi chu kỳ xung nhịp). Để làm được điều này, dữ liệu âm thanh phải được bơm thẳng qua các thanh ghi dịch (Shift Registers) và được xử lý bởi một đường ống (pipeline) phần cứng hoàn chỉnh thay vì chờ lệnh điều khiển (Instruction Fetch) từ CPU/GPU.

### 3. Lý thuyết Phân tách Kênh-Thời gian (Time-Channel Separable Convolution)
Một lớp tích chập chuẩn 1D có độ phức tạp tính toán là $O(K \cdot C_{in} \cdot C_{out})$. Lý thuyết của MatchboxNet [R01-05] và Conformer [R01-03] chứng minh rằng bộ trích xuất đặc trưng âm thanh có thể được phân tách (Factorized) thành hai miền độc lập:
*   **Miền thời gian (Time-domain):** Lọc độc lập trên từng kênh (Depthwise Convolution), độ phức tạp $O(K \cdot C_{in})$.
*   **Miền kênh (Channel-domain):** Kết hợp các kênh (Pointwise Convolution), độ phức tạp $O(C_{in} \cdot C_{out})$.
Sự phân tách toán học này cho phép hệ thống phần cứng giảm thiểu 80% - 90% số lượng khối DSP multiplier đắt đỏ trên mạch FPGA mà không làm suy giảm độ chính xác của quá trình nhận diện.

### 4. Lý thuyết Lượng tử hóa Affine (Affine Quantization Theory)
Để thu gọn mô hình khổng lồ (vốn tính toán bằng Float32) vào tài nguyên giới hạn của Kria KV260 [R01-04], hệ thống áp dụng phép ánh xạ tuyến tính Affine: $r = S(q - Z)$, trong đó $r$ là giá trị thực, $q$ là giá trị nguyên lượng tử, $S$ (Scale) và $Z$ (Zero-point) là các tham số lượng tử.
Khi nhân hai tensor lượng tử INT8, kết quả sinh ra trong không gian INT32. Việc ánh xạ ngược kết quả này về lại không gian INT8 (Quá trình Requantization) đòi hỏi một phép chia vô tỷ. Lý thuyết lượng tử hóa thích ứng phần cứng (Hardware-Aware Quantization) yêu cầu biến đổi toán học phép chia này thành một phép nhân với số nguyên $M_0$ và dịch bit phải (Arithmetic Shift Right >>>), đảm bảo 100% thao tác tính toán trên FPGA đều là số nguyên tĩnh.

---

## 2. LẬP LUẬN KIẾN TRÚC 1: XỬ LÝ ÂM THANH STREAMING 

Để xử lý luồng âm thanh liên tục, hệ thống cần đáp ứng các điều kiện về truy xuất và tối ưu hóa số lượng phép tính.

*   **Từ bỏ SRAM tĩnh, chuyển sang Line Buffer:**
    *   *Vì sao?* Âm thanh là dữ liệu chuỗi thời gian (time-series). Mỗi 10ms có một frame đặc trưng mới. Dùng kiến trúc SRAM tĩnh bắt buộc hệ thống phải sao chép/dịch toàn bộ mảng dữ liệu cũ đi 1 ô nhớ mỗi lần có frame mới $\rightarrow$ tiêu tốn hàng trăm chu kỳ xung nhịp (clock cycles) và năng lượng.
    *   *Cơ chế:* Sử dụng **Line Buffer (Shift Register Array)**. Âm thanh trượt tự nhiên vào thanh ghi. Mảng Convolution được đấu nối trực tiếp vào các tap của thanh ghi để tính toán song song tức thời mà không tốn chi phí tạo địa chỉ (Address Generation Overhead).
*   **Dịch chuyển từ Standard Convolution sang Depthwise Separable (DS-Conv):**
    *   *Vì sao?* Tích chập tiêu chuẩn tốn quá nhiều phép nhân.
    *   *Cơ chế:* Cấu hình lại bộ Convolution thành hai bước: **Depthwise Conv** và **Pointwise Conv**. Dựa trên Lý thuyết Phân tách Kênh-Thời gian [R01-05], việc này tối ưu hóa tài nguyên cực độ.

---

## 3. LẬP LUẬN KIẾN TRÚC 2: VƯỢT QUA "BỨC TƯỜNG BỘ NHỚ" CỦA FPGA

Mô hình như Conformer nặng từ 10 - 30 triệu tham số, vượt xa dung lượng BRAM siêu tốc trên chip (chỉ khoảng 4 MB trên Kria KV260). Nếu liên tục gọi trọng số từ DRAM ngoài, FPGA cũng sẽ bị nghẽn y hệt GPU.

*   **Hardware-Aware Quantization (Lượng tử hóa INT8/INT4):**
    *   *Vì sao?* Dựa trên lý thuyết Affine [R01-02], việc giảm biểu diễn trọng số xuống INT8/INT4 giúp tiết kiệm 75-87% băng thông DRAM và tăng mật độ phép tính MAC.
*   **Thiết kế khối Requantizer (Tái lượng tử hóa):**
    *   *Vì sao?* Ngăn ngừa bùng nổ băng thông (Memory Explosion) từ kết quả Accumulator INT32.
    *   *Cơ chế:* Ép INT32 về INT8 qua chuỗi phép toán nguyên tĩnh (Integer Multiplier $M_0$ + Bit-Shift) $\rightarrow$ Bão hòa (Clamping) về khoảng [-128, 127].
*   **Khai thác Tính thưa (Sparsity / Pruning):**
    *   *Vì sao?* Ép xuống INT8 vẫn không đủ giải quyết hoàn toàn nút thắt băng thông cho các model lớn.
    *   *Cơ chế (SOTA):* Huấn luyện mô hình ép các trọng số kém quan trọng về 0. Thiết kế mạch **Hardware Decoder** trên FPGA để chỉ tải và tính toán với các trọng số khác 0 (Zero-skipping), tiết kiệm 50% băng thông DRAM.

---

## 4. LẬP LUẬN KIẾN TRÚC 3: XỬ LÝ CƠ CHẾ ATTENTION THỜI GIAN THỰC

Khối Attention là trung tâm của mô hình Conformer, nhưng kiến trúc nguyên bản không phù hợp với âm thanh Streaming.

*   **Từ bỏ Self-Attention toàn cục, áp dụng Chunk-based Attention:**
    *   *Vì sao?* Self-Attention chuẩn tính tương quan của một từ với *tất cả* các từ trong câu (Độ phức tạp $O(T^2)$). Trong streaming, không thể nhìn thấu tương lai (Vi phạm tính nhân quả - Causal violation) [R01-03].
    *   *Cơ chế:* Phân chia âm thanh thành các "cục" (Chunk) ngắn. Mạch Attention chỉ được cấp quyền tính toán nội bộ trong Chunk đó và nhìn lại một số Chunk quá khứ giới hạn (Left-context).
*   **Thiết kế Hardware KV-Cache:**
    *   *Vì sao?* Để không phải tính lại các Chunk quá khứ mỗi khi có Chunk mới vào.
    *   *Cơ chế:* Cấp phát một vùng BRAM riêng biệt tổ chức dưới dạng **Circular Ring Buffer**. Khi tính Attention cho Chunk mới, Query (Q) của hiện tại sẽ được nhân ma trận trực tiếp với tập Key (K), Value (V) đang lưu tĩnh trong Ring Buffer này.

---

## 5. LẬP LUẬN KIẾN TRÚC 4: CHIẾN LƯỢC QUY MÔ HÓA (SCALABILITY)

*   **Sự dịch chuyển từ Verilog thuần sang HLS (High-Level Synthesis):**
    *   *Vì sao?* Việc sử dụng Verilog thủ công cho lõi Convolution tĩnh là tối ưu để quản lý Bit-exact. Tuy nhiên, khi hệ thống phình to thành hàng chục lớp Residual, Feed-Forward, và Multi-Head Attention, thiết kế Finite State Machine (FSM) bằng tay sẽ bùng nổ độ phức tạp, không có khả năng mở rộng.
    *   *Cơ chế (SOTA):* Chuyển đổi sang sử dụng **C/C++ HLS (Vitis HLS)** hoặc các trình biên dịch AI phần cứng (FINN [R01-02]). Kỹ sư tập trung định nghĩa "Dataflow", trình tự sinh FSM, Pipelining, và cân bằng độ trễ (Latency Balancing) sẽ do trình biên dịch đảm nhiệm.

---

## TỔNG KẾT HƯỚNG TRIỂN KHAI THỰC NGHIỆM

Dựa trên các lập luận kiến trúc trên, quy trình nghiên cứu thực nghiệm được chia thành 5 chặng (Milestones):

1.  **Thiết kế Lõi Kỹ thuật (RTL):** Nâng cấp bộ Parameterized Convolution hiện có bằng khối Requantizer và Streaming Line Buffer. Đảm bảo tính toán bão hòa (Clamping) chính xác.
2.  **Đánh giá Baseline:** Đo đạc các nút thắt bộ nhớ trên NVIDIA Jetson Orin bằng Nsight Systems ở điều kiện streaming.
3.  **Tối ưu Hóa Thuật toán:** Thực hiện QAT và Pruning để trích xuất tập trọng số thưa INT8/INT4.
4.  **Triển khai Hệ thống Cơ sở (KWS SoC):** Đóng gói IP Lõi qua chuẩn AXI4-Stream, chạy luồng dữ liệu liên tục không độ trễ bằng DMA.
5.  **Quy mô hóa lên Streaming Conformer:** Dịch chuyển sang Vitis HLS để hiện thực hóa cơ chế Chunk-based Attention và Hardware KV-Cache.

---

## TÀI LIỆU THAM KHẢO (BIBLIOGRAPHY)

Dự án này được neo trên các tài liệu nền tảng đã được kiểm định (Truy xuất từ hệ thống source_index.json của kho lưu trữ):
*   **[R01-01]** NVIDIA Corporation. (2022). *NVIDIA Jetson AGX Orin Architecture Whitepaper*. 
*   **[R01-02]** Umuroglu, Y., et al. (2017). *FINN: A Framework for Fast, Scalable Binarized Neural Network Inference on FPGAs*. ACM FPGA.
*   **[R01-03]** Gulati, A., et al. (2020). *Conformer: Convolution-augmented Transformer for Speech Recognition*. Interspeech.
*   **[R01-04]** Advanced Micro Devices, Inc. (2023). *AMD Xilinx Kria KV260 Vision AI Starter Kit User Guide*.
*   **[R01-05]** Majumdar, S., et al. (2020). *MatchboxNet: 1D Time-Channel Separable Convolutional Neural Network for Speech Command Recognition*. Interspeech.