# Bảng Thuật ngữ Kỹ thuật — Voice Edge AI (Glossary)

Bảng tra cứu thuật ngữ chuyên ngành chuẩn hóa phục vụ cuốn chuyên khảo và bài báo khoa học.

| Thuật ngữ Tiếng Anh | Viết tắt | Thuật ngữ Tiếng Việt | Định nghĩa / Bản chất Kỹ thuật |
|---|:---:|---|---|
| **Short-Time Fourier Transform** | STFT | Biến đổi Fourier thời gian ngắn | Phép phân tích phổ tần số của tín hiệu âm thanh theo từng cửa sổ trượt thời gian ngắn. |
| **Mel-Frequency Cepstral Coefficients** | MFCC | Hệ số tần số Mel | Biểu diễn phổ âm thanh dựa trên thang độ cảm nhận phi tuyến tính của thính giác người. |
| **Word Error Rate** | WER | Tỷ lệ từ nhận dạng sai | Chỉ số đánh giá độ chính xác của mô hình ASR: $(S+D+I)/N$. |
| **Perceptual Evaluation of Speech Quality** | PESQ | Đánh giá chất lượng âm thanh theo cảm nhận | Chuẩn ITU-T P.862 đo lường chất lượng âm thoại từ $-0.5$ đến $4.5$. |
| **Deep Processing Unit** | DPU | Khối xử lý học sâu chuyên dụng | Kiến trúc phần cứng cấu hình sẵn trên FPGA của AMD/Xilinx tối ưu cho tensor nơ-ron. |
| **Initiation Interval** | II | Khoảng thời gian khởi tạo xung nhịp | Số chu kỳ xung nhịp giữa hai lần nhận dữ liệu liên tiếp trong luồng phần cứng ($II=1$ là lý tưởng). |
| **Quantization-Aware Training** | QAT | Huấn luyện nhận thức lượng tử hóa | Mô phỏng sai số lượng tử hóa số nguyên trong quá trình lan truyền tiến khi huấn luyện mạng. |
| **Post-Training Quantization** | PTQ | Lượng tử hóa sau huấn luyện | Chuyển đổi trọng số và kích hoạt từ FP32/FP16 sang INT8/INT4 mà không cần huấn luyện lại. |
| **Streaming Multiprocessor** | SM | Khối đa xử lý luồng | Đơn vị tính toán song song cơ bản trong kiến trúc GPU của NVIDIA. |
| **Block RAM** | BRAM | Bộ nhớ RAM khối trên chip | Khối nhớ SRAM lưỡng cổng tốc độ cao tích hợp trực tiếp trên FPGA fabric. |
| **UltraRAM** | URAM | Bộ nhớ UltraRAM dung lượng cao | Khối SRAM mật độ cao trên các dòng FPGA UltraScale+ phục vụ lưu trữ ma trận trọng số. |
| **Digital Signal Processor** | DSP | Bộ xử lý tín hiệu số phần cứng | Khối phần cứng chuyên dụng (ví dụ DSP48E2) thực hiện phép nhân-cộng tích lũy (MAC) cực nhanh. |
| **Real-Time Factor** | RTF | Hệ số thời gian thực | Tỷ số giữa thời gian xử lý và thời lượng đoạn âm thanh; $\text{RTF} < 1$ đảm bảo thời gian thực. |
| **Pareto Frontier** | - | Biên tối ưu Pareto | Tập hợp các điểm thiết kế tối ưu đa mục tiêu (không thể cải thiện chỉ số này mà không làm giảm chỉ số khác). |
