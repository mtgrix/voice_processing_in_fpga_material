# Kế Hoạch Nâng Cấp Toàn Diện Chương 1 (Chapter 01 Improvement Plan)
## Dựa trên Bộ Quy Chuẩn Soạn Thảo Tài Liệu Học Tập Kỹ Thuật (`rules.md`)

> **Mục tiêu:** Nâng cấp `book-en/chapter01.md` đạt chuẩn 10/10 theo bộ quy chuẩn sư phạm và kỹ thuật tại `C:\Users\NGOC\Documents\my_asset\learning\book_writing\rules.md`.  
> **Nguyên lý dẫn đường:** *"Dạy bản chất, không dạy học vẹt; xây dựng trực giác trước khi lượng hóa bằng toán học; mọi công thức đều phải dẫn tới quyết định thiết kế."*

---

## 1. Đánh Giá Hiện Trạng So Với 10 Tiêu Chí Pre-Flight Checklist

| STT | Tiêu chí trong `rules.md` | Hiện trạng ở Chương 1 | Nhiệm vụ nâng cấp cụ thể |
| :---: | :--- | :---: | :--- |
| **1** | Bản chất vật lý vi mô trước công thức (Tầng 1) | **Đạt 70%** | Bổ sung cơ chế sinh học Ốc tai (Cochlea) cho Mel Scale và Định luật Weber-Fechner cho Log Compression. |
| **2** | Giải thích ý nghĩa vật lý từng biến số & đơn vị (Tầng 2) | **Đạt 100%** | Duy trì định dạng Equation Card chuẩn 5 phần đã làm rất tốt. |
| **3** | Quyết định thiết kế & Đánh đổi thực tế (Tầng 3) | **Đạt 95%** | Giữ vững lập luận về trần trễ (10 ms) và độ trôi dạt (jitter) khi so sánh FPGA vs GPU; đóng gói thành Callout rõ ràng. |
| **4** | Mô hình tư duy / Ẩn dụ cơ học chuẩn xác (Mental Model) | **Đạt 85%** | Duy trì ẩn dụ số quay Euler ($e^{-j\theta}$); bổ sung ẩn dụ quán tính thanh quản (vocal tract inertia) cho cửa sổ trượt 25 ms. |
| **5** | Đồ thị sống động, có vector dòng chảy & ranh giới trễ | **Đạt 80%** | Duy trì 3 hình TikZ hiện có; bổ sung vector pha và quỹ đạo biến đổi trong phân tích STFT. |
| **6** | Lời văn dẫn dắt mắt người đọc vào chi tiết hình vẽ | **Đạt 100%** | Duy trì phong cách dẫn dắt tương tác cao giữa văn bản và đồ thị TikZ. |
| **7** | Chiến lược ngôn ngữ & Thuật ngữ chuẩn hóa | **Đạt chuẩn Monograph** | Viết bằng tiếng Anh học thuật B2/C1 sắc bén; giải thích tường minh từ viết tắt ở lần đầu xuất hiện. |
| **8** | Đóng gói module theo thời lượng nhận thức (Time-box) | **Đạt 75%** | Bổ sung các mốc Checkpoint tóm tắt ngắn giữa 4 section lớn để người đọc dễ hấp thụ. |
| **9** | Câu hỏi kiểm tra tình huống thực chiến (Diagnostic) | 🔴 **Chưa đạt (0%)** | **Bổ sung mới hoàn toàn Mục 1.5 gồm 4 bài toán tư duy tình huống thực chiến chuẩn kỹ sư.** |
| **10** | Tái lập số liệu (TikZ/Python) & Chế bản PDF | **Đạt 100%** | Bảo đảm biên dịch LuaLaTeX ra PDF khổ A4 chuẩn mực, test CI `scan_numbers.py` và `pytest` xanh 100%. |

---

## 2. Bốn Trọng Tâm Cải Tiến Cần Hiện Thực

### Trọng tâm 1: Xây dựng Mục 1.5 — Bộ Bài Tập Tình Huống Thực Chiến (Diagnostic Scenario Testing)
Thêm mới mục `## 1.5 Exercises: Diagnostic Engineering Scenarios` vào trước mục `Associated Experiment`, gồm 4 bài toán tư duy thiết kế (không hỏi học vẹt định nghĩa):

1. **Exercise 1.1 (System Framing & Buffer Sizing - Khảo sát Tần số Lấy mẫu):**
   * *Tình huống:* Nếu hệ thống nâng cấp microphone từ $f_s = 16\text{ kHz}$ lên chuẩn phòng thu $f_s = 48\text{ kHz}$ trong khi vẫn giữ nguyên thời gian khung $25\text{ ms}$ và bước nhảy $10\text{ ms}$.
   * *Yêu cầu:* Tính số mẫu mới của khung ($L$) và bước nhảy ($H$). Phân tích sự phình to của Ring Buffer trong Block RAM và lưu lượng băng thông AXI-Stream. Đánh giá sự đánh đổi: Kỹ sư có thu được lợi ích âm học nào cho mô hình nhận dạng giọng nói không khi mà dải tần tiếng người chủ yếu nằm dưới $8\text{ kHz}$?

2. **Exercise 1.2 (Physics of Latency vs. Spectral Uncertainty - Nguyên lý Bất định):**
   * *Tình huống:* Một kỹ sư muốn giảm độ trễ phản hồi của hệ thống xuống cực thấp bằng cách cắt giảm độ dài khung từ $L = 400$ mẫu ($25\text{ ms}$) xuống còn $L = 80$ mẫu ($5\text{ ms}$).
   * *Yêu cầu:* Giải thích tại sao việc này làm suy sụp độ phân giải tần số theo Nguyên lý bất định Gabor-Heisenberg ($\Delta t \cdot \Delta f \ge \frac{1}{4\pi}$). Điều gì sẽ xảy ra với các đỉnh formant của nguyên âm trong tiếng nói khi độ rộng cửa sổ hẹp hơn chu kỳ dao động cơ bản của dây thanh âm?

3. **Exercise 1.3 (FFT Architecture: Zero-Padding vs. Hardware Resource Trade-off):**
   * *Tình huống:* Khung âm thanh có 400 mẫu nhưng giải thuật bắt buộc chèn zero-padding lên $N = 512$ mẫu.
   * *Yêu cầu:* So sánh độ phức tạp phần cứng: Tại sao việc đệm 112 số 0 để dùng thuật toán FFT Radix-2 Cooley-Tukey ($O(N \log_2 N)$) lại tiết kiệm áp đảo số lượng DSP slices và logic LUT trên FPGA so với việc cố gắng tính toán biến đổi Fourier trực tiếp trên 400 mẫu ($O(L^2)$)?

4. **Exercise 1.4 (Memory Hierarchy & Sparse Mel Matrix Storage):**
   * *Tình huống:* Ma trận Mel Filterbank $80 \times 257$ có phần lớn các phần tử bằng 0 (do mỗi bộ lọc tam giác chỉ bao phủ một dải hẹp).
   * *Yêu cầu:* Thiết kế cấu trúc lưu trữ nén (CSR hoặc mảng chỉ số biên $k_{\min}, k_{\max}$ kèm trọng số). Tính toán dung lượng BRAM tiết kiệm được khi chuyển từ ma trận đầy đủ (dense FP32: $82.2\text{ KiB}$) sang định dạng thưa fixed-point INT16. Đánh giá tác động đến băng thông truy xuất trong mỗi chu kỳ xung nhịp 10 ms.

---

### Trọng tâm 2: Bổ Sung Tầng Bản Chất Vật Lý Vi Mô (Tầng 1) vào Mel Scale & Log Compression

* **Sinh học Ốc tai (Cochlea Mechanics) cho Mục Mel Scale:**
  - Giải thích cơ chế màng đáy (Basilar membrane) trong ốc tai người: Có độ cứng và bề rộng thay đổi dần từ đáy đến đỉnh. Đáy ốc tai hẹp và cứng, phản hồi với tần số cao (khoảng lọc rộng, độ phân giải thô); đỉnh ốc tai rộng và mềm, phản hồi với tần số thấp (khoảng lọc hẹp, độ phân giải cực nét).
  - Khẳng định: Thang đo Mel và các tam giác lọc không phải là phát minh toán học ngẫu nhiên, mà là sự mô phỏng trực tiếp các dải lọc tới hạn (Critical Bands) của hệ thống thính giác sinh học.

* **Định luật Tâm vật lý Weber-Fechner cho Mục Log Compression:**
  - Bổ sung trực giác: Bộ não con người cảm nhận độ lớn âm thanh theo thang phi tuyến (logarithmic). Năng lượng âm thanh vật lý tăng gấp 10 lần thì não chỉ cảm nhận độ to tăng khoảng gấp đôi.
  - Phép nén Log $\ln\bigl(\max(E, 10^{-6})\bigr)$ đưa đặc trưng biên độ về không gian tuyến tính với nhận thức sinh học, giúp mô hình học sâu ổn định trước các biến thiên âm lượng nói to/nói nhỏ.

---

### Trọng tâm 3: Thanh Lọc 24 Câu Văn "Kiểm Toán Viên" (Auditor Talk Remediation)

Loại bỏ hoàn toàn các câu văn mang tính đối soát nội bộ hoặc phân bua về database registry:
* ❌ *"What was missing until now was any record of why 16,000 rather than some other number, and two records close that gap."*  
  $\rightarrow$ ✅ *"Why 16 kHz rather than 44.1 kHz or 8 kHz? In human speech acoustics, intelligible linguistic information concentrates below 8 kHz. By the Nyquist-Shannon sampling theorem ($f_s \ge 2B$), sampling at 16 kHz preserves all essential speech cues while preventing unnecessary computational overhead..."*
* ❌ *"section 1.2 keeps the records."*  
  $\rightarrow$ ✅ *"section 1.2 establishes the timing constraints and architectural parameters."*
* ❌ *"the evidence registry holds records about the two platforms... and no record of a frontend's own geometry..."*  
  $\rightarrow$ ✅ Chuyển toàn bộ các ghi chú đối soát về bảng `Traceability` ở cuối mục theo đúng chuẩn `BOOK_PEDAGOGY.md` §8.

---

### Trọng tâm 4: Trực Quan Hóa Hộp Nhận Diện Nhanh (Color-Coded Callouts)

Chuẩn hóa các đoạn giải thích quan trọng thành 4 nhóm hộp nhận diện:
* 🔬 **Physical Mechanism:** Cơ chế vi mô (quán tính thanh quản 25 ms, màng đáy ốc tai, triệt tiêu pha Euler).
* 📐 **Mathematical Derivation:** Bước suy diễn công thức ($k f_s / N$, tính chất đối xứng liên hợp Hermite).
* ⚡ **Engineering Takeaway:** Quyết định đánh đổi phần cứng (lựa chọn $L=400, H=160, N=512$, tối ưu bộ nhớ BRAM).
* ⚠️ **Common Pitfall:** Cảnh báo sai lầm kinh điển (nhầm lẫn giữa độ phân giải nội suy FFT và độ phân giải vật lý của cửa sổ, trượt deadline do jitter trên OS).

---

## 3. Quy Trình Kiểm Thử & Nghiệm Thu (Verification Checklist)

Sau khi chỉnh sửa, bắt buộc phải vượt qua toàn bộ các bước kiểm tra sau:
1. `python -m ruff check book-en/chapter01.md`
2. `python scripts/verification/scan_numbers.py --check book-en/chapter01.md` (Không phát sinh số mồ côi ngoài bảng Traceability).
3. `python -m pytest tests/` (114+ tests passed).
4. `& "C:/Program Files/Git/bin/bash.exe" scripts/build_book.sh --chapter 01` (Biên dịch LuaLaTeX thành công, không lỗi TikZ, không lỗi font).

---

> ### ⚠️ LƯU Ý BẮT BUỘC (CRITICAL NOTE)
> **File kế hoạch này (`improve_ch_01_plan.md`) là tài liệu làm việc và theo dõi tạm thời.**  
> **Sau khi hiện thực xong toàn bộ các hạng mục trên và được con người (human reviewer) audit, approve chính thức, bắt buộc phải XOÁ file này đi khỏi repository để giữ sạch cây mã nguồn.**
