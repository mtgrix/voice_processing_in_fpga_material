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

## Chương 5: So sánh Các Phương pháp luận Tăng tốc trên FPGA: DPU, HLS, FINN & RTL

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
- **"4 MB" / "4.5 MB"** cho SRAM KV260: cả hai không có cơ sở silicon (`V-01-22`, C-01). Số đúng là
  **23 616 Kb = 2 952 KiB**, và nó được phép viết **2.88 MiB** hoặc **3.02 MB** — cùng một số byte,
  hai quy ước. Bắt buộc ghi rõ quy ước ngay cạnh số; viết `2.88 MiB = 2.95 MB` là trộn hai quy ước
  trong một câu, lỗi đã từng xảy ra ở `V-01-11` và `book/chapter04.md`.
- **"10–30 M tham số"** cho Conformer: `plan.md` tự nêu, chưa verify. Thông số kiến trúc của model
  đích phải **tính ra** từ checkpoint theo §4.2 — hiện vẫn là placeholder trỏ tới mục P1 của fetch brief.
- **Bảng điểm kiểu "97.4 %"**: `plan-v2.md` §9.2 chỉ ra bốn dòng số viết tay trong
  `capstone/voice_edge_benchmark/benchmark_runner.py` và các lệnh assert của test trên chính chúng.

---

## Resolution of the mapping question, recorded 2026-09-13 (English, appended, not replacing)

The two-reading table above stays exactly as it was written. This section is the
second record, not an edit of the first, because the earlier note is itself
evidence that the ambiguity existed and was deliberately left open.

What changed: the repo owner delegated the choice. Instructing the agent to pick
the chapter titles and the most common hardware, in these words --
*"dùng ngôn ngữ ENG level B2; Title anh cho mày tự đặt, phần cứng chọn common nhất. Làm đi"* --
settled the question by moving it out of the agent's hands and into his.

Consequence applied to `book-en/`:

* Chapters 8 and 9 take the titles of the `plan-v2.md` section 7 artefacts --
  the keyword-spotting build and the streaming Conformer overlay. The §7 reading
  is the canonical one for the spine.
* The section stubs under those two chapters still follow the earlier mapping,
  where chapter 8 held shared model primitives and chapter 9 held SoC
  partitioning. They were left in place on purpose. Re-cutting an outline is
  prose work, and a pipeline branch that quietly reorganises two chapters would
  make it impossible to see what the move cost.
* A scope note sits under each of the two H1 lines in `book-en/chapter08.md` and
  `book-en/chapter09.md`, naming the mismatch. Readers meet the gap in the text,
  not in a commit message.

Still open, and unchanged by this decision: `plan-v2.md` section 3.1 carries the
line *"chọn 1"* for the same mapping. That is the owner's to close. Section 7
remains the authority on artefacts; nothing here overrides it.


---

## The re-cut executed, recorded 2026-09-14 (English, appended, not replacing)

The resolution above ended with a task left in the manuscript: _"Re-cutting an outline is prose
work,"_ and it named `plan-v2.md` section 7 as the authority on artefacts. Issue #53 did that work on
the branch `docs/chapter89-prose`. The section lists in `book-en/chapter08.md` and
`book-en/chapter09.md` are now neither of the two readings tabulated above: they follow the stage
artefacts, so chapter 8 is the keyword-spotting build and chapter 9 is the streaming Conformer
overlay and its ring buffer. This section exists so the earlier reading can still be reconstructed.

The scope note under each chapter's H1 says the same thing to the reader, in the book's voice. That
is deliberate: `book/TOC.md` is maintainer documentation, and a change a reader can only see in the
commit history is a change the reader does not see.

| Subject, under the earlier reading | Where it is now |
|---|---|
| 8.1 Hardware challenges in modern acoustic architectures | 8.1, as the concrete question the heading was standing in for: this board ships with no audio input, so what does the path cost and which rate governs |
| 8.2 Pipelined 1D depthwise separable convolutions on FPGA | 8.2, same subject, now argued from the line buffer rather than from the operator name |
| 8.3 Streaming chunk-level self-attention engines | chapter 9, section 9.3. Attention is a property of the model chapter 9 builds, and chapter 8 builds a keyword spotter that has none |
| 8.4 Hardware approximations for non-linearities: base-2 softmax and LayerNorm | 8.3 |
| 9.1 Partitioning computational graphs across CPU and FPGA fabric | 9.5 |
| 9.2 SoC architecture: interfacing PS and PL over AXI | 9.5, which is the same boundary seen from the fabric side |
| 9.3 Software stack: PYNQ overlays, VART, low-latency Linux drivers | nowhere, and that is the finding. No record in `docs/verification/claims.json` covers a toolchain choice for this overlay, so 9.5 states the question and leaves it open to a board run rather than naming products |
| 9.4 System-level power dissipation and thermal optimisation | chapter 10, whose metric matrix in 10.2 already carries energy per frame. A thermal section ahead of any measured joule would have been the gap report's error, not this book's |
| (no earlier stub) | 8.4, the stage-8 acceptance gate, which the spine states and no stub held |
| (no earlier stub) | 9.1 the target and what about it is undecided, 9.2 one block as a datapath, 9.4 the left-context ring buffer, 9.6 look-ahead against accuracy |

Figures: the manuscript carried two, both roofline plots in chapter 3. The re-cut adds seven, so
`scripts/verify_book_pdf.sh` check 6 counts the nine figure sources in the manuscript, finds the numbered captions in the PDF,
requires those numbers to be exactly 1 through 9, and requires a prose reference to every id. That is
a real gate and it passes on this build. What it cannot do is tell whether a picture depicts what its
caption claims, and in `--chapter` mode its source count stays manuscript-wide while its captions come
from one chapter's PDF -- both limits are recorded in Issue #54. Nothing has been asserted here about
fit that was not measured: each picture's natural box was boxed and printed against the 156 mm text
block, which is the only way to know a figure is inside the margins when the filter hands TikZ to the
main pass and no image file exists to inspect.

Still open after this, and not closed by it: `plan-v2.md` section 3.1's _"chọn 1"_ line, and conflict
C-08 in `docs/verification/README.md`, which asks which streaming model the benchmark ports. Chapters
8 and 9 were written to describe a datapath without settling either, and both say so where they say
it. `V-05-57` remains the reason no byte figure appears in either chapter.
