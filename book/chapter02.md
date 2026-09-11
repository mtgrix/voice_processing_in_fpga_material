# Chương 2: Jetson Orin: Điểm chuẩn & Giới hạn Vật lý (Jetson Orin: Edge Baseline & Limits)

> *"Một con chip có khả năng đạt hàng trăm nghìn tỷ phép tính mỗi giây (TOPS) không có nghĩa là nó sẽ phản hồi tức thì với một khung âm thanh 10 mili giây."*

---

## 2.1 Trực giác: Sức mạnh và Nghịch lý của NVIDIA Jetson Orin

Dòng máy tính nhúng NVIDIA Jetson Orin (Orin Nano, Orin NX, AGX Orin) hiện là tiêu chuẩn vàng không thể bàn cãi trong lĩnh vực trí tuệ nhân tạo biên (Edge AI). Được xây dựng dựa trên vi kiến trúc đồ họa Ampere của NVIDIA, Jetson Orin tích hợp các nhân tăng tốc ma trận Tensor Core thế hệ thứ ba và bộ tăng tốc học sâu chuyên dụng (DLA — Deep Learning Accelerator).

Trên các tác vụ thị giác máy tính như phân đoạn hình ảnh hay phát hiện vật thể, Jetson Orin thể hiện hiệu năng xuất sắc: nó có thể xử lý hàng chục khung hình camera độ phân giải cao mỗi giây với mức công suất điều chỉnh linh hoạt từ $7\text{W}$ đến $25\text{W}$.

Tuy nhiên, khi đưa một mô hình giọng nói trực tuyến (streaming voice model) vào Jetson Orin, các kỹ sư hệ thống thường gặp phải một **nghịch lý hiệu năng**:
- Tỷ lệ chiếm dụng nhân tính toán (GPU compute utilization) giảm xuống chỉ còn dưới $15\%$.
- Mức tiêu thụ điện công suất tĩnh của toàn hệ thống (SoC baseline idle power) vẫn duy trì ở mức $3\text{W} - 6\text{W}$ ngay cả khi mô hình chỉ đang "lắng nghe" khoảng lặng.
- Độ trễ phản hồi (latency) bị dao động lớn (jitter) do phụ thuộc vào trình lập lịch của hệ điều hành Linux và chi phí khởi tạo lệnh gọi nhân GPU (kernel launch overhead).

Chương này giải phẫu vi kiến trúc của Jetson Orin, thiết lập phương pháp đo đạc chính xác bằng công cụ TensorRT và hệ thống giám sát cảm biến dòng điện phần cứng tích hợp (`tegrastats`).

---

> ### 📘 Toán học Tối thiểu cho Chương này
> 
> Các công thức vật lý và chỉ số hiệu năng phần cứng cần thiết:
> 1. **Năng lượng Tiêu thụ trên Khung (Energy per Frame)**:
>    $$E_{\text{frame}} = P_{\text{avg}} \times \Delta t_{\text{latency}} \quad (\text{Joules})$$
> 2. **Hệ số Thời gian Thực (RTF — Real-Time Factor)**:
>    $$\text{RTF} = \frac{T_{\text{processing}}}{T_{\text{audio}}}$$
>    Nếu $\text{RTF} < 1$, hệ thống xử lý nhanh hơn thời gian âm thanh phát ra; nếu $\text{RTF} \ge 1$, hệ thống bị trễ tích lũy và tràn hàng đợi.
> 3. **Băng thông Bộ nhớ Lý thuyết (Memory Bandwidth)**:
>    $$BW = \text{Bus Width (bytes)} \times \text{Clock Frequency} \times \text{Data Rate Multiplier}$$

---

## 2.2 Vi Kiến trúc Jetson Orin: Từ Nhân CUDA đến Tensor Cores

Bên trong Jetson Orin, khả năng tính toán được phân bổ qua các khối đa xử lý luồng (SM — Streaming Multiprocessor):

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   NVIDIA Jetson Orin System-on-Chip                    │
│                                                                        │
│   ┌─────────────────────┐       ┌──────────────────────────────────┐   │
│   │  ARM Cortex-A78AE   │       │       Ampere GPU Subsystem       │   │
│   │  (CPU Lõi Nhúng)    │       │  ┌────────────────────────────┐  │   │
│   │  8x Cores @ 2.0 GHz │       │  │ SM 0: CUDA + Tensor Cores  │  │   │
│   └──────────┬──────────┘       │  ├────────────────────────────┤  │   │
│              │                  │  │ SM 1: CUDA + Tensor Cores  │  │   │
│              │                  │  └─────────────┬──────────────┘  │   │
│              ▼                  └────────────────┼─────────────────┘   │
│   ┌──────────────────────────────────────────────▼─────────────────┐   │
│   │        Unified LPDDR5 Memory Subsystem (128-bit, 102 GB/s)      │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

### Cơ chế Hoạt động: Đơn vị Thực thi SIMT

NVIDIA GPU vận hành theo mô hình Thực thi Đơn Lệnh Đa Luồng (SIMT — Single Instruction, Multiple Threads). Các luồng được nhóm thành các phân luồng gọi là **Warp** (mỗi warp gồm 32 luồng).
- Khi nhân Tensor Core thực hiện phép nhân-cộng ma trận tích lũy (FMA — Fused Multiply-Add) ở định dạng nửa chính xác (FP16) hoặc số nguyên 8-bit (INT8), nó đòi hỏi kích thước khối dữ liệu (tile size) tối thiểu (ví dụ: $16 \times 16 \times 16$).
- Khi xử lý âm thanh với $batch=1$, ma trận đầu vào của một khung thời gian chỉ có kích thước $1 \times M$ (với $M=80$ đặc trưng Mel). Việc nhân ma trận vector này với ma trận trọng số biến phép toán thành **phép nhân ma trận-vector (GEMV)** thay vì nhân ma trận-ma trận (GEMM).
- GEMV là bài toán bị giới hạn nghiêm trọng bởi băng thông bộ nhớ (memory-bandwidth bound) chứ không bị giới hạn bởi năng lực tính toán (compute bound). GPU dành phần lớn thời gian chờ nạp dữ liệu trọng số từ bộ nhớ LPDDR5 thay vì thực hiện tính toán.

---

## 2.3 Phương pháp Luận Đo kiểm: TensorRT và Tegrastats

Để thiết lập đường cơ sở (baseline) khoa học vững chắc cho bài báo nghiên cứu, chúng ta không đo đạc thời gian chạy trên Python thô, mà biên dịch mô hình sang công cụ suy diễn tối ưu hóa cao nhất của NVIDIA: **TensorRT**.

### Đo Lường Độ Trễ Cực Đoan (Tail Latency P99)
Không chỉ lấy thời gian trung bình (mean latency), bài báo khoa học cần phân tích phân phối độ trễ qua hàm phân vị 99% (P99 Latency). Một mô hình có độ trễ trung bình $2\text{ ms}$ nhưng có $1\%$ khung bị trễ vọt lên $25\text{ ms}$ (do tranh chấp bộ nhớ hoặc ngắt hệ điều hành) sẽ gây ra hiện tượng mất âm thanh (audio dropouts).

### Đo Lường Công Suất Bằng `tegrastats`
Jetson Orin tích hợp các chip giám sát điện áp và dòng điện chuyên dụng (IC cảm biến INA3221). Lệnh `tegrastats` cho phép đọc trực tiếp:
- `VDD_GPU_SOC`: Công suất tiêu thụ của lõi GPU và các bộ điều khiển logic.
- `VDD_CPU_CV`: Công suất tiêu thụ của các nhân ARM CPU.
- `VIN_SYS_5V0`: Tổng công suất thực tế cấp vào toàn bộ bo mạch.

---

## 2.4 Thí nghiệm Thực thi: Bộ Đo Lường Hiệu Năng Jetson Orin

Trong thư mục [`chapter02/`](../chapter02/), mã nguồn `exp_02_jetson_orin_profiler.py` triển khai công cụ giả lập và phân tích hồ sơ hiệu năng của mô hình thoại trên Jetson Orin dựa trên dữ liệu nhật ký thực tế của TensorRT và `tegrastats`.

Thực thi thí nghiệm:

```bash
python chapter02/exp_02_jetson_orin_profiler.py
```

Thí nghiệm tính toán chính xác bảng chỉ số:
- Độ trễ trung bình (Mean Latency) và P99 Latency.
- Hệ số thời gian thực (RTF).
- Năng lượng tiêu thụ trên từng khung âm thanh ($\text{mJ/frame}$).
- Tỷ lệ hiệu quả năng lượng ($\text{frames/s/Watt}$).

Đây chính là các cột số liệu chuẩn sẽ xuất hiện trong phần thực nghiệm của bài báo khoa học khi so sánh trực diện với phần cứng FPGA.
