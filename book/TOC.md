# DÀN Ý CUỐN SÁCH (TABLE OF CONTENTS)

**Tên sách dự kiến:** Gia Tốc Hardware Voice AI: Từ Jetson GPU Đến FPGA Spatial Dataflow

> **File này là gì:** xương sống 10 chương của chuyên khảo, chiếu từ `plan-v2.md` §7.
> Nó **không** định nghĩa đề cương — nó trích đề cương. Thẩm quyền theo thứ tự:
> `plan-v2.md` → `docs/verification/` (số đã verify) → file này.
>
> **Lịch sử:** `plan.md` tự nhận là "Đề cương Sách (Monograph Spec)" ở dòng 3 và là bản mà 10
> chương `book/chapterNN.md` đã soạn theo. `plan-v2.md` thay thế nó; §9.1 và §3.3 chỉ ra các claim
> định lượng của `plan.md` không có dẫn xuất. Khi hai bản khác nhau, `plan-v2.md` thắng. Bản 5
> chương trước đây của file này là tàn dư của `plan.md`; nó đã bị thay bằng đúng 10 chương dưới
> đây, khớp `plan-v2.md` §9.3 và `docs/BOOK_STATUS.md`.
>
> **Giữ file này khỏi lệch trở lại:** `tests/test_plan_consistency.py` assert số chương ở đây == 10
> và == số hàng bảng §7. Thời lượng **không** chép vào đây, vì đó là metadata thuần sao chép — xem
> §7. Tiêu đề chương lấy nguyên văn từ `docs/BOOK_STATUS.md` để không tạo nguồn thứ năm.

---

## Ba quyết định đã chốt mà sách phải dạy, không được footnote

| Quyết định | Nội dung | Chỗ ghi |
|---|---|---|
| **Model ASR** | **NVIDIA NeMo streaming Conformer-Transducer `small`**, checkpoint mở. Whisper đã xét và **bị loại**: cửa sổ 30 giây không nhân quả là một *lớp model* khác, phá đường cong accuracy-vs-latency mà §4.2 sinh ra để dạy | `plan-v2.md` §4.2, 2026-09-12 |
| **Điểm vận hành** | **`MAXN`.** Ridge point sách dạy là **490.2 OP/byte** (Orin, `V-07-02`) so với **39–78 OP/byte** (KV260, `V-07-03`), không phải 764.7 của `MAXN_SUPER`. Hồ sơ `MAXN_SUPER` vẫn đúng cho carrier cấp 40 W và rail 8 V | `plan-v2.md` §3.1; `docs/verification/README.md` C-07, đóng 2026-09-12 |
| **Đường âm thanh** | **I2S/PDM qua carrier vào PL.** KV260 **không có mic**; CIC decimation thành bắt buộc; USB rớt xuống hàng dự phòng vì nó đi vòng qua PL và biến chương FPGA thành bài toán số học không có micro trong fabric | `plan-v2.md` §3.2, §4.1, §8.2, 2026-09-12 |

**Một giả định chưa verify:** liệu carrier KV260 có đưa được bitstream mic vào PL hay không. Nếu UBB
không có I2S/PDM, hệ quả là phải đổi tên carrier hoặc mở lại quyết định âm thanh. Theo dõi tại
`docs/AGENT_FETCH_BRIEF_2026-09-12.md` mục P3.

---

## Xương sống 10 chương

Mỗi mục: **Trọng tâm** (chương trả lời câu hỏi gì) và **Nghiệm thu** (artefact + gate của chặng tương
ứng, chiếu `plan-v2.md` §7 — §7 là chỗ duy nhất ghi thời lượng).

## Chương 1: Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực

**Trọng tâm:** Vì sao âm thanh là dòng dữ liệu $batch=1$ và vì sao GPU không sinh ra cho dạng đó.
**Nghiệm thu (chặng 1):** Sơ đồ khối + ngân sách latency từng tầng; các tầng cộng lại ≤ mục tiêu và
mỗi con số có chữ ký của một phép đo.

## Chương 2: Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin

**Trọng tâm:** Phẫu thuật SoC Orin và dựng đường cơ sở đo được bằng phương pháp luận công khai.
**Nghiệm thu (chặng 2):** `results/exp02/` log thô + bảng P50/P90/P99, jitter, mJ/frame; ≥3 run, đã
trừ idle, mỗi số mang đủ 4 thành phần metadata (SKU, nvpmodel, JetPack, ambient).

## Chương 3: Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU

**Trọng tâm:** Chứng minh bằng Roofline, không bằng cảm tính, rằng Orin bị chặn băng thông đúng ở
khối lượng công việc của cuốn sách này.
**Nghiệm thu (chặng 3):** Roofline có số theo §6.1 tại **`MAXN`** + Nsight Compute + Orin đã được tối
ưu *đúng cách*. Gate thật: **giả thuyết H0-A bị bác bỏ, hoặc dự án đổi câu hỏi.**

## Chương 4: Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu

**Trọng tâm:** Tài nguyên thật của ZU5EV và hệ quả của nó lên bài toán chứa trọng số.
**Nghiệm thu (chặng 4):** `docs/DATASHEET_VERIFICATION.md` — file này **chưa tồn tại**, §7 lập ra để
  chứa bảng tài nguyên ZU5EV mà mỗi ô phải ghi rõ trang datasheet. Gate của chặng này chưa vượt qua.
  Số đã verify của chương này hiện nằm trong `docs/verification/` (hồ sơ `V-01-*`), không phải trong
  file đó. Số phải dạy: SRAM fabric **23 616 Kb = 2.88 MiB**, **3.13 MiB** nếu tính cả 256 KB PS OCM
  (`V-01-11`). Hệ quả bắt buộc của §3.3: một Conformer 10–30 M tham số **không** nằm trọn trong chip
  kể cả ở INT4, nên sách phải tách **hai chương trình** — KWS vừa chip, ASR không vừa.

## Chương 5: So sánh Các Phương pháp luận Tăng tốc trên FPGA

**Trọng tâm:** DPU, HLS, FINN, RTL tự viết — cái nào thắng, và thắng trên **cùng một model**.
**Nghiệm thu (chặng 5):** Bốn hàng, mỗi hàng có log tổng hợp thật. Chương này dạy **thủ tục so sánh**;
nó không được kết luận hộ số liệu. Lưu ý nguồn: `R01-02` là framework cho binarized NN inference,
không phải nguồn của lý thuyết lượng tử hoá affine (§9.1).

## Chương 6: Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh

**Trọng tâm:** Đưa FFT/STFT, Mel filterbank, CIC decimation và log compression vào fabric, tính từ
bit micro do **carrier** mang tới — không phải từ một file WAV đã giải mã sẵn.
**Nghiệm thu (chặng 6):** RTL `Line_Buffer_1D` + Requantizer + golden model; bit-exact 0 mismatch,
coverage ≥ ngưỡng, WNS ≥ 0.

## Chương 7: Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại

**Trọng tâm:** PTQ/QAT/mixed-precision, với chi tiết chất lượng **đo theo đúng tác vụ**: accuracy/EER
và FAR-FRR cho KWS, WER/CER cho ASR, PESQ/STOI/SI-SDR cho tăng cường tiếng nói (§5.3 cấm dùng lẫn).
**Nghiệm thu (chặng 7):** QAT/pruning bằng Brevitas + Δaccuracy có khoảng tin cậy; giả thuyết H0-C đo
được; quy ước làm tròn chốt một lần và test bit-exact **từng tầng** (§6.2).

## Chương 8: Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại

**Trọng tâm:** Depthwise separable conv, attention streaming, softmax/LayerNorm xấp xỉ cơ số 2. Model
đích là **NeMo Conformer-Transducer `small`**, không phải Whisper (§4.2).
**Nghiệm thu (chặng 8):** xem mục "Lệch ánh xạ chưa chốt" bên dưới.

## Chương 9: Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng / Phần mềm

**Trọng tâm:** PS/PL partition, AXI DMA, PYNQ/VART, nhiệt và power domain trên KV260.
**Nghiệm thu (chặng 9):** xem mục "Lệch ánh xạ chưa chốt" bên dưới.

## Chương 10: Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo Khoa học

**Trọng tâm:** So sánh công bằng, không gian đánh đổi Pareto, và đóng gói thành công trình tái lập
được.
**Nghiệm thu (chặng 10):** Paper draft + artifact package + Pareto frontier, vượt checklist §8.4;
người khác tái lập từ README. Bảng định vị liên quan công trình (§8.1) là mục bắt buộc.

---

## Lệch ánh xạ chưa chốt — ghi lại, không dàn phẳng

`plan-v2.md` §7 gán artefact theo **chặng**; `docs/BOOK_STATUS.md` đặt **tiêu đề** theo chương. Số
lượng 10 khớp nhau, nhưng nội dung hai cặp sau thì không:

| Chương | Tiêu đề đã tracked | Artefact §7 ở chặng đó |
|---|---|---|
| 08 | Tăng tốc các khối tính toán cốt lõi | KWS SoC chạy trên board: audio vào → kết quả ra, ≥1 giờ không treo |
| 09 | Tích hợp hệ thống SoC PS/PL | Streaming Conformer overlay + Left-Context Ring Buffer |

Cả hai cách đọc đều hợp lệ, và đây là quyết định của chủ repo chứ không của agent. Tạm thời: **gate
của chặng 8–9 phủ cả hai chương 08 và 09**, và §7 vẫn là thẩm quyền. Hoặc đổi tiêu đề chương, hoặc
viết lại §7, rồi xoá mục này. Ghi cả hai bản ghi theo đúng tinh thần rule 6: không đè.

## Những số không được phép xuất hiện trong sách

- **Không một con số đo nào** (ms, W, %, TOPS/W) được viết nếu chưa có log thô trong `results/` —
  `scripts/verify_integrity.py` từ chối dấu ✅ không kèm log, và rule 8 cấm tự nhận đã xong.
- **"4 MB" / "4.5 MB" / "3.02 MB"** cho SRAM KV260: chỉ một giá trị được phép sống, và đó là giá trị
  có trang datasheet (`V-01-11`, `plan-v2.md` §3.3).
- **"10–30 M tham số"** cho Conformer: `plan.md` tự nêu, chưa verify. Thông số kiến trúc của model
  đích phải **tính ra** từ checkpoint theo §4.2 — hiện vẫn là placeholder trỏ tới mục P1 của fetch brief.
- **Bảng điểm kiểu "97.4 %"**: `plan-v2.md` §9.2 chỉ ra bốn dòng số viết tay trong
  `capstone/voice_edge_benchmark/benchmark_runner.py` và các lệnh assert của test trên chính chúng.
