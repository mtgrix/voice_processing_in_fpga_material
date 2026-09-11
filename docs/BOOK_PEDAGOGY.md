# Book Pedagogy Policy — Voice Edge AI: Jetson Orin to FPGA

> **Canonical authoring policy.** Every chapter draft, revision, experiment, and research note MUST comply with this document.
> Last updated: 2026-09-11

---

## 1. Local Sufficiency Principle (Nguyên tắc Tự đủ Cục bộ)

Người đọc không bao giờ phải đối mặt với một thuật ngữ phần cứng, tên viết tắt, ký hiệu toán học hoặc chỉ số đo lường mà không có đủ kiến thức **cục bộ** ngay tại vị trí đó để hiểu được lập luận kỹ thuật hiện tại.

"Cục bộ" nghĩa là: nằm trong cùng một mục, hoặc tối đa là mục ngay trước đó. Mọi tham chiếu vượt chương chỉ được phép khi khái niệm đó là **phụ trợ** (incidental) và được kèm theo một định nghĩa tóm lược ngắn gọn ngay tại chỗ.

**Bài kiểm tra (Test):** Một người đọc chỉ đọc tuần tự đến điểm này có thể giải thích được khái niệm đó để theo dõi tiếp đoạn văn sau không? Nếu không, đoạn văn vi phạm nguyên tắc Tự đủ Cục bộ.

---

## 2. Defer Depth, Never Required Understanding (Hoãn Độ sâu, Không hoãn Hiểu biết Cốt lõi)

Độ sâu chuyên sâu (ví dụ: chứng minh hội tụ lượng tử hóa hoặc sơ đồ định thời chu kỳ xung nhịp chi tiết) có thể hoãn lại đến chương sau. Nhưng hiểu biết tối thiểu để nắm bắt bản chất của lập luận hiện tại thì **tuyệt đối không được hoãn**.

| Được phép | Bị cấm |
|-----------|--------|
| "Chúng ta sẽ phân tích vi kiến trúc chi tiết của Tensor Core trong Chương 2" sau khi đã giải thích trực giác về phép nhân ma trận song song | Sử dụng ký hiệu $\text{TOPS}/\text{W}$ hoặc ma trận trọng số lượng tử mà không giải thích ý nghĩa |
| Nhắc đến FPGA DSP slice khi so sánh với ALU của GPU, kèm mô tả chức năng | Dùng thuật ngữ "Initiation Interval ($II=1$)" mà không định nghĩa trực quan |

---

## 3. Required vs Incidental Concepts (Khái niệm Bắt buộc vs Phụ trợ)

### Khái niệm Bắt buộc (Required concept)
Người đọc **bắt buộc** phải hiểu rõ để theo dõi mạch lập luận. Phải được giảng dạy đầy đủ theo 3 cấp độ: Trực giác → Cơ chế → Ứng dụng.

### Khái niệm Phụ trợ (Incidental concept)
Được nêu ra để mở rộng bối cảnh hoặc làm cầu nối đến các chương tiếp theo. Người đọc không cần phải hiểu chi tiết bên trong. Chỉ cần 1 câu giải thích ngắn gọn + con trỏ tham chiếu.

---

## 4. Three-Level Concept Introduction (Quy tắc Giới thiệu Khái niệm 3 Cấp độ)

Mọi khái niệm kỹ thuật bắt buộc phải tuân theo đúng thứ tự 3 bước sau:

1. **Trực giác (Intuition)** — Đây là cái gì? Tại sao nó phải tồn tại? Giải thích bản chất vật lý/kỹ thuật bằng ngôn từ trực quan, không dùng công thức phức tạp.
2. **Cơ chế (Mechanism)** — Nó hoạt động ra sao bên trong? Sơ đồ luồng dữ liệu, công thức toán học, thuật toán, hoặc vi kiến trúc phần cứng kèm ví dụ từng bước.
3. **Ứng dụng (Application)** — Hệ quả thực tế của nó là gì? Ảnh hưởng thế nào đến độ trễ (latency), năng lượng (Joules), hoặc tỷ lệ lỗi âm thanh (WER/PESQ) trên Jetson Orin hoặc FPGA.

---

## 5. Acronym First-Use Rule (Quy tắc Viết tắt Lần đầu)

Trong lần đầu tiên xuất hiện trong toàn bộ tài liệu:

```text
Tên Đầy Đủ (VIẾT TẮT — nghĩa ngắn gọn tiếng Việt)
```

Ví dụ:
- `Fast Fourier Transform (FFT — biến đổi Fourier nhanh)`
- `Deep Processing Unit (DPU — khối xử lý học sâu chuyên dụng trên FPGA)`
- `Word Error Rate (WER — tỷ lệ từ nhận dạng sai)`
- `Real-Time Factor (RTF — hệ số thời gian thực)`

Trong các lần xuất hiện tiếp theo trong cùng chương: chỉ cần dùng từ viết tắt.

---

## 6. Mathematics Must Explain Mechanisms (Toán học Phải Giải thích Cơ chế)

Ký hiệu toán học là công cụ để mô tả cơ chế phần cứng và giải thuật chính xác, không phải màn chắn để làm phức tạp vấn đề.

Đối với mọi biểu thức toán học:
1. Nêu trực giác vật lý/thuật toán bằng văn xuôi trước.
2. Trình bày biểu thức toán học rõ ràng.
3. Ánh xạ từng biến số/ký hiệu vào ngữ cảnh cụ thể của tín hiệu âm thanh hoặc phần cứng.
4. Nêu rõ hệ quả kỹ thuật rút ra từ công thức.
5. Nêu rõ điều gì **KHÔNG** suy ra được (những hiểu lầm phổ biến).

**Yêu cầu Sidebar:** Mỗi chương có sử dụng toán học phi tầm thường phải có khung thông tin "Toán học tối thiểu cho chương này" (Prerequisite Mathematics).
