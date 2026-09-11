# ĐỀ CƯƠNG v2 — TĂNG TỐC VOICE AI TỪ JETSON ORIN SANG FPGA

> **Tài liệu này thay thế cách dùng `plan.md`, không xoá `plan.md`.** `plan.md` giữ nguyên làm "kiến trúc luận" (architecture essay) — nó vẫn có giá trị như bản lập luận vì sao spatial dataflow đáng nghiên cứu. `plan-v2.md` là **đường học (learning path) + giao thức thực nghiệm (experimental protocol)**, tức hai thứ mà `plan.md` không hề chứa.
>
> **Quy chiếu chuẩn (normative refs):** `README.md` (10 chương), `docs/BOOK_STATUS.md`, `docs/RESEARCH_METHODOLOGY.md`, `docs/BOOK_PEDAGOGY.md`, `AGENTS.md` (13-section experiment template). Khi `plan-v2.md` và các file trên mâu thuẫn, **10 chương là canonical** — xem §9.3.

---

## 0. BA THỨ plan.md KHÔNG PHẢI

| `plan.md` là | Đề cương này là |
|---|---|
| Lập luận kiến trúc: "vì sao FPGA hợp lý" | Hợp đồng thực thi: "làm gì, theo thứ tự nào, nghiệm thu bằng gì" |
| Tuyên bố kết quả ("tiết kiệm 75–87%") | Giả thuyết + phép đo để kiểm chứng hoặc bác bỏ |
| 5 milestone, song song với 10 chương của phần còn lại repo | 10 chặng khớp 1:1 `docs/BOOK_STATUS.md`, mỗi chặng có gate |
| Không có người học | Có điều kiện tiên quyết, thời lượng, artefact, đường hầm thất bại |

★ Insight ─────────────────────────────────────
Một tài liệu chỉ nêu *cơ chế* mà không nêu *phép đo* thì không thể sai — và cái gì không thể sai thì không thể bảo vệ. Toàn bộ phần "sửa" dưới đây quy về một việc: biến mỗi assertion trong `plan.md` thành một claim có gate kiểm chứng đi kèm, hoặc gắn nhãn "chưa chứng minh".
─────────────────────────────────────────────────

---

## 1. PHẠM VI VÀ CÂU HỎI NGHIÊN CỨU

### 1.1 Câu hỏi nghiên cứu (Research Questions)

- **RQ1** — Với một mô hình voice streaming xác định (§4.2) chạy ở `batch=1` trên một SKU Jetson Orin xác định (§3.1), giới hạn thật sự là băng thông DRAM, hay là kernel-launch overhead, occupancy thấp, hay đơn giản là chưa bật đúng TensorRT INT8 / CUDA Graphs / DLA?
- **RQ2** — Trong cùng ràng buộc năng lượng (matched power envelope, theo `docs/RESEARCH_METHODOLOGY.md` §2.A), một vi kiến trúc spatial dataflow trên FPGA có vượt Orin về *độ trễ khung* và *mJ/frame* không, và vượt ở vùng tham số nào?
- **RQ3** — Đường Pareto (độ chính xác × độ trễ × năng lượng × tài nguyên) trông ra sao khi quét qua bit-width, số PE, chunk size? FPGA thắng ở đâu và **thua** ở đâu?

### 1.2 Giả thuyết không (Null hypotheses) — bắt buộc phải bác bỏ được

| ID | Giả thuyết không | Bác bỏ bằng |
|---|---|---|
| H0-A | Sau khi đã tối ưu đúng cách trên Orin (TensorRT INT8 + CUDA Graphs + `nvpmodel`/`jetson_clocks` khoá clock), không còn hiện tượng memory-bound đáng kể ở `batch=1`. | Nsight Compute: đạt `dram__throughput.avg.pct_of_peak_sustained_elapsed` cao ⇒ thực sự memory-bound; đạt thấp ⇒ H0-A đúng, luận điểm của `plan.md` §1 sụp. |
| H0-B | Ở cùng mức công suất bị giới hạn, FPGA overlay không cho P99 frame latency tốt hơn Orin. | So sánh P50/P90/P99 với ≥5 seed × ≥300 giây/run, khoảng tin cậy 95 %. |
| H0-C | Lượng tử hoá INT8 trên mô hình đã chọn làm suy giảm độ chính xác vượt ngưỡng chấp nhận được. | Đo metric của tác vụ (§4.4) trước/sau QAT, với khoảng tin cậy. |

> **Nếu H0-A không bị bác bỏ, dự án phải đổi câu hỏi, không phải đổi số.** Đây là gate ở cuối Chặng 3.

### 1.3 Phạm vi loại trừ (Out of scope, nói rõ để khỏi tranh luận)

Huấn luyện mô hình mới từ đầu; ASR đa ngôn ngữ; beam search trên phần cứng; nhiều mic / beamforming; an toàn chức năng (functional safety).

---

## 2. ĐIỀU KIỆN TIÊN QUYẾT VÀ TỰ CHẨN ĐOÁN

`plan.md` giả định ngầm người học đã có **4 kỹ năng độc lập**, mỗi cái mất hàng tháng. Đề cương này nêu tường minh và cho đường bổ túc.

| # | Kỹ năng | Dấu hiệu "đã đủ" (tự kiểm tra, làm được trong ≤2 giờ) | Nếu chưa đạt → học ở |
|---|---|---|---|
| P1 | RTL số (Verilog/SystemVerilog) | Viết `parameterized` FIFO đồng bộ có `full`/`empty`, tự viết testbench, chạy được trên Verilator | Phụ lục C-1 (≈3 tuần) |
| P2 | Fixed-point / số học máy | Tính tay overflow và sai số làm tròn của Q1.15 × Q1.15, giải thích vì sao accumulator cần 31 bit | Phụ lục C-2 (≈1 tuần) |
| P3 | PyTorch training + inference | Train lại một KWS model nhỏ trên dataset công khai, reproduce được accuracy công bố ±1% | Phụ lục C-3 (≈3 tuần) |
| P4 | Linux embedded + đo lường | Đọc `tegrastats`/sysfs, đổi `nvpmodel`, khoá clock, giải thích được rail nào là cái gì | Phụ lục C-4 (≈1 tuần) |

**Gate vào đề cương:** P1 **và** P2 **và** P3 phải đạt. P4 có thể học song song với Chặng 1–2.

### 2.1 Chiến thắng sớm (Early win) — chống bỏ cuộc

Trước khi chạm vào bất kỳ file RTL nào, người học phải **nghe và thấy máy chạy** trong buổi đầu tiên:

> **E0 (≤1 ngày):** Chạy `chapter01/exp_01_streaming_audio_pipeline.py` trên một file WAV có sẵn, in ra phổ log-mel streaming, và xác nhận kết quả **khớp với librosa** trong dung sai cho trước. Không FPGA, không Jetson, không tổng hợp.

Đây là artefact đầu tiên và là neo động lực. `plan.md` không có bước nào cho ra kết quả cảm nhận được trước milestone 4.

---

## 3. NỀN TẢNG PHẦN CỨNG ĐÃ CHỐT

### 3.1 Jetson Orin — phải chốt SKU, không được nói "Orin"

"Jetson Orin" là một **dòng sản phẩm**, không phải một chip. Khác nhau về SM count, băng thông LPDDR5, có/không DLA, và mức công suất — tức là mọi con số sau này đều vô nghĩa nếu không chốt.

| Hạng mục | Giá trị chốt | Nguồn bắt buộc phải verify |
|---|---|---|
| Board baseline | ⚠ chọn 1: Orin Nano 8GB / Orin Nano Super / Orin NX 16GB / AGX Orin 64GB | `jetson-datasheet-<sku>.pdf` — **đọc trực tiếp, không lấy từ memory** |
| Số SM, Tensor Cores/SM | ⚠ | Whitepaper kiến trúc + `deviceQuery` trên máy thật |
| Băng thông DRAM danh định | ⚠ GB/s | Datasheet + **đo thực** bằng STREAM-like benchmark |
| DLA có hay không, mấy nhân | ⚠ | `nvpmodel -q`, `/proc/device-tree` |
| JetPack / L4T / CUDA / TensorRT | ⠓ pin chính xác | `cat /etc/nv_tegra_release`, `nvcc --version`, `dpkg -l \| grep -i tensorrt` |
| Chế độ nguồn khi đo | ⚠ chốt 1 `nvpmodel` + `jetson_clocks` | Ghi vào metadata mọi log |

> **Quy tắc:** mọi con số hiệu năng trong sách/paper phải kèm `(SKU, nvpmodel, JetPack version, ambient)`. Không có 4 thành phần đó thì số không được phép xuất hiện.

### 3.2 FPGA — chốt part, không chốt "Kria"

| Hạng mục | Giá trị chốt | Nguồn bắt buộc phải verify |
|---|---|---|
| Board | ⚠ Kria KV260 (ZU5EV) hay một board khác | `ug1089` user guide + `xsct`/`bootgen` đọc ID thật |
| Part + speed grade | ⚠ `xczu5ev-ffvg1537-<i>-e` | Marking trên chip, **không** lấy từ ảnh marketing |
| LUT / FF / DSP48E2 / BRAM36 / URAM288 | ⚠ từng ô | **DS891 datasheet + `report_utilization` sau tổng hợp** |
| On-chip SRAM tổng | ⚠ **xem 3.3 — repo đang sai** | DS891, tính từ block count × dung lượng/block |
| DDR loại/băng thông | ⚠ | DS891 + `ddr_test`/example design |
| vào âm thanh bằng đường nào | ⚠ USB audio / UBB expansion / I2S-PDM qua PL | `ug1089` mục carrier card + `arecord -l` |
| Vivado / Vitis / Vitis AI / PetaLinux | ⠓ pin chính xác | `vivado -version`, `petalinux-version` |

### 3.3 Lỗi dung lượng nhớ on-chip — phải sửa trước khi dùng lại

Ba chỗ trong repo đưa ba giá trị khác nhau cho cùng một đại lượng:

| Nơi viết | Tuyên bố |
|---|---|
| `plan.md` dòng 55 | "chỉ khoảng **4 MB** trên Kria KV260" |
| `docs/research_notes/R02_fpga_audio_streaming.md` | "144 BRAMs and 64 URAMs, providing **~4.5 MB**" |
| Chính phép tính từ số liệu của R02 | 144×36 Kb + 64×288 Kb = 23 616 Kb ≈ **3.02 MB** |

Con số 3.02 MB **không cần datasheet** để phủ định 4.5 MB — nó là phép cộng trên chính số block mà R02 nêu. `docs/SOURCES.md` thì nêu "256K LUTs, 1.2K DSP slices" và **không** nêu dung lượng nhớ, nên không chỗ nào dẫn nguồn gốc.

Hệ quả trực tiếp lên `plan.md` §3, vốn lấy "4 MB" làm mẫu số để biện minh cho việc nhét KV-Cache vào BRAM:

| Mô hình | INT16 | INT8 | INT4 |
|---|---|---|---|
| 10 M tham số | 20 MB — **6.6×** | 10 MB — **3.3×** | 5 MB — **1.7×** |
| 30 M tham số | 60 MB — **19.8×** | 30 MB — **9.9×** | 15 MB — **5.0×** |

(mẫu số = 3.02 MB; "10–30 M tham số" là con số `plan.md` tự nêu, chưa verify)

**Kết luận bắt buộc phải viết lại:** ngay cả ở INT4, một Conformer 10–30 M tham số **không** nằm trọn trong BRAM/URAM. Toàn bộ lập luận "zero off-chip traffic" của `R02` chỉ đứng được với KWS cỡ nhỏ (MatchboxNet ~0.5 M). Đề cương phải tách làm **hai chương trình riêng**, xem §7 Chặng 4 và Chặng 8.

> **Hành động:** mở `docs/DATASHEET_VERIFICATION.md`, điền từng ô từ file PDF thật, ghi rõ trang. Mọi claim trong sách chỉ được dùng số sau khi bảng này đầy.

---

## 4. CHUỖI BÀI TOÁN: ÂM THANH → MÔ HÌNH → KIẾN TRÚC

`plan.md` nhảy từ "waveform" sang "spatial dataflow" và bỏ mất ba tầng. Đây là chuỗi đầy đủ; các ô ★ là những tầng `plan.md` không hề có.

```
[Microphone / ★input nguồn] → [★ADC & clock domain] → [Pre-emphasis]
   → [Framing 25ms / hop 10ms] → [Window] → [FFT] → [Mel filterbank] → [log]
   → [★CMVN / feature frontend trên PL hay PS?]
   → [Encoder: Conv/DS-Conv + Attention]   ← phần FPGA thật sự làm
   → [★Decoder: CTC greedy / transducer]   ← plan.md im lặng hoàn toàn
   → [★Output: beep / command dispatch / transcript]
```

### 4.1 ★ Tầng thu âm — `plan.md` có 0 ký tự về micro

Phải chốt, và phải tái lập được khi **không cắm micro**:

| Quyết định | Lựa chọn | Hệ quả phải ghi |
|---|---|---|
| Nguồn tín hiệu | File WAV nhúng trong repo (canonical) **và** micro thật (validation) | Mọi số so sánh được lấy từ WAV; micro chỉ dùng cho demo |
| Micro | ⚠ loại, sample rate danh định, gain | Sai sample rate ⇒ lệch phổ ⇒ accuracy sai mà không ai biết |
| Giao diện | USB audio (PS) / I2S-PDM qua UBB (PL) | Chọn PDM-qua-PL thì phải có CIC decimation trong RTL |
| Clock | ⚠ master clock ở đâu, có CDC không | Đây là nguồn bug "chạy được trên sim, hỏng trên board" số 1 |
| Determinism | Phát file WAV qua `sox`/loopback, **không** thu trực tiếp | Không có bước này thì không có run nào tái lập được |

> Artefact bắt buộc: `data/captured/` chứa WAV đầu vào đã pin **SHA-256**, và `data/README.md` ghi licence của từng file.

### 4.2 ★ Chốt mô hình và tác vụ — `plan.md` không bao giờ chọn

| Chặng | Tác vụ | Mô hình ứng viên | Vì sao chọn |
|---|---|---|---|
| 4–6 | **KWS** (12–35 nhãn) | MatchboxNet / SpeechCommands1 v2 | Đủ nhỏ để vào hết BRAM ⇒ chứng minh được đường RTL + bit-exact trước khi mơ lớn |
| 8–10 | **Streaming ASR** | Streaming Conformer đã công bố, có checkpoint mở | Có WER để so; có rightaway/future-context để vẽ đường accuracy-vs-latency |

**Sửa lỗi phân loại nghiêm trọng trong `plan.md`:** MatchboxNet `[R01-05]` được `plan.md` dùng làm chỗ dựa cho "Streaming ASR" ở §1, nhưng nó là **classifier 12–35 nhãn**, không phải ASR ⇒ **không có WER**. Mọi bảng metric phải nói rõ metric nào thuộc tác vụ nào (§5.3).

Phải ghi tường minh: số lớp, `d_model`, số head, kernel size, số tham số, số MACs/frame, byte trọng số, byte activation — **tính ra**, không ước lượng. Đây là đầu vào của roofline ở §6.1.

### 4.3 ★ Tầng giải mã — tầng bị bỏ quên

`plan.md` thiết kế encoder rồi coi như xong. Trên biên, chi phí của tầng giải mã thường **lớn hơn** encoder.

| Câu hỏi | Đề cương phải trả lời |
|---|---|
| KWS | Có decode không, hay argmax? Chạy ở đâu? |
| ASR | CTC greedy hay transducer? Beam? |
| Placement | PS (ARM) hay PL? Nếu PS thì đã tính CPU của nó vào ngân sách năng lượng chưa? |
| Trạng thái | Buffer giải mã bao nhiêu byte, có bị tràn khi nói liên tục không? |

### 4.4 ★ Độ trễ thuật toán — trục mà reviewer speech sẽ đòi

`plan.md` nêu "chunk-based attention" như một lựa chọn kiến trúc, không định nghĩa ràng buộc thời gian.

- Định nghĩa **rightaway** (số frame hiện tại model được nhìn) và **future context** (số frame tương lai), bằng **mili giây**, cho từng chặng.
- Ngân sách end-to-end: `T_total = T_capture + T_frontend + T_encoder + T_decode + T_output`. Đo từng thành phần, không đo gộp.
- Vẽ **đường cong accuracy vs latency** bằng cách quét chunk size. Đây là kết quả, không phải giả định.
- `plan.md` nói "streaming không nhìn thấu tương lai (causal violation)" nhưng không bao giờ nêu con số future-context của Conformer gốc — vốn **có** future context. Phải sửa câu này cho đúng.

---

## 5. GIAO THỨC THỰC NGHIỆM

`plan.md` có 0 occurrence của: dataset, seed, phép lặp, độ lệch chuẩn, related work, null hypothesis. `docs/RESEARCH_METHODOLOGY.md` đã có một phần — **đề cương phải tham chiếu nó**, hiện không file nào liên kết hai bên.

### 5.1 Tái lập được (Reproducibility)

| Bắt buộc | Cách làm |
|---|---|
| Pin mọi version | `env/VERSIONS.lock.md`: JetPack, CUDA, TensorRT, Vivado, Vitis, Vitis AI, PetaLinux, Python, commit hash của repo |
| Pin dữ liệu | SHA-256 mỗi file; ghi licence; ghi cả cách sinh WAV tổng hợp nếu có |
| Pin seed | `SEED` cho training, cho calibration, và cho mọi phép đo có ngẫu nhiên |
| Số phép lặp | **≥5 seed × ≥3 lần đo**; báo trung bình ± độ lệch mẫu và khoảng tin cậy 95 % |
| Lệnh tái lập | Mỗi experiment có đúng 1 lệnh `make exp-NN` in ra log + JSON |
| Không có "chạy lại sẽ ra số khác" | Log thô commit vào `results/expNN/<timestamp>/` |

### 5.2 Đối công bằng (Fairness)

- **Matched power envelope** (theo `RESEARCH_METHODOLOGY.md` §2.A): so Orin ở `nvpmodel` bị giới hạn xuống **cùng công suất** với FPGA, chứ không so Orin ở max power. Đây là chỗ mà bảng số bịa sẵn trong `capstone/` (xem §9.2) đã vi phạm.
- **Cùng độ chính xác hoặc thấp hơn có khai báo**: so sánh phải kèm Δaccuracy. "Nhanh hơn 4.5× nhưng tụt 0.5 WER" là một kết luận khác hẳn.
- **Cùng điều kiện nhiệt & idle**: đo idle trước, trừ baseline, ghi ambient.
- **Báo P50/P90/P99 và jitter**, không chỉ mean. Một con số mean không chứng minh được điều gì cho hệ thống thời gian thực.

### 5.3 Metric theo đúng tác vụ

| Tác vụ | Metric chất lượng | Metric hệ thống |
|---|---|---|
| KWS | Accuracy / EER, FAR-FRR trên **speaker-independent** split | P50/P99 frame latency, RTF, mJ/frame, FPS/W |
| Streaming ASR | **WER/CER**, độ trễ word-first (LRS/first-story latency) | như trên + CPU% của tầng decode |
| Speech enhancement | PESQ / STOI / SI-SDR | như trên |

> Cấm dùng lẫn: một bảng có "97.4 %" mà không nói là accuracy KWS hay 1−WER thì không được phép tồn tại.

### 5.4 Ablations bắt buộc

Ít nhất: bit-width {FP32, FP16, INT8, INT4} × {có/không pruning} × {PE count} × {chunk size} × {frontend ở PL hay PS}. Mỗi hàng một cấu hình thật, có log.

### 5.5 Related work — `plan.md` hoàn toàn thiếu

Phải có bảng định vị: FINN, Vitis AI DPU, AIE-based, Eyeriss, Timeloop/Accelergy, và các công trình FPGA-ASR đã công bố (kèm số của **chính** họ). Paper không có mục này bị reject ở vòng 1 tại FCCM/FPGA.

### 5.6 Threats to validity — mục bắt buộc của paper

Nêu ít nhất: (a) một board ≠ cả dòng sản phẩm; (b) overlay chưa tối ưu ⇒ so với Orin đã tối ưu là thiên vị ngược; (c) Xilinx Power Estimator là **ước lượng**, không phải đo; (d) Linux không hard-RT ⇒ P99 có thể do OS, không phải do kiến trúc; (e) một dataset ≠ phân phối thực.

---

## 6. ĐẶC TẢ VI KIẾN TRÚC VÀ VERIFICATION

Đây là lỗ hổng lớn nhất về mặt nghề nghiệp: `plan.md` mô tả **chức năng** của khối phần cứng mà không bao giờ cho **đặc tả** của nó. Không có đặc tả thì không có RTL nào đúng, chỉ có RTL chạy được trên testbench người ta tự viết để nó chạy được.

### 6.1 Roofline phải có số, không có số thì bỏ

Với mô hình đã chốt ở §4.2, tính và ghi vào `docs/roofline/<model>.md`:

```
I = MACs_per_frame × 2 / Bytes_moved_per_frame
Bytes_moved = weights + activations + (I/O)
ridge_point = Peak_MACs / Peak_BW        ← cả hai lấy từ §3, đã verify
```
Rồi mới được phép kết luận memory-bound hay không. `plan.md` §1.1 kết luận mà không tính.

### 6.2 ★ Đặc tả fixed-point theo từng tầng — `plan.md` có 0 chữ

| Tầng | Q-format | Accumulator | Rounding | Bão hòa (Clamp) | Ghi chú phải khớp PyTorch |
|---|---|---|---|---|---|
| Mel/log frontend | ⚠ | ⚠ | ⚠ | ⚠ | log xấp xỉ bằng gì? |
| Conv/DS-Conv depthwise | ⚠ | ⚠ | ⚠ | ⚠ | |
| Pointwise | ⚠ | ⚠ | ⚠ | ⚠ | |
| LayerNorm | ⚠ | ⚠ | ⚠ | — | rsqrt bằng LUT hay Newton? |
| Softmax | ⚠ | ⚠ | ⚠ | — | power-of-two piecewise? |
| Requantize | ⚠ | ⚠ | **phải chốt: round-half-up / nearest-even / trunc** | ⚠ | **đây là chỗ bit-exact chết** |

> **Rounding mode là bug số một của mọi dự án quantized-RTL.** PyTorch/Brevitas dùng một quy ước, RTL dùng quy ước khác ⇒ sai số tích luỹ qua hàng chục lớp, và người học sẽ debug vài tuần mà không hiểu vì sao. Phải chốt một quy ước, ghi vào file, và test bit-exact **trên từng tầng**, không chỉ trên toàn mạng.

### 6.3 ★ Verification methodology — `plan.md` có 0 chữ

| Lớp | Phương tiện | Gate |
|---|---|---|
| Golden model | Python/NumPy fixed-point **mô phỏng đúng Q-format và rounding đã chốt** | Khớp FP32 trong dung sai công bố |
| Vector | Sinh `.hex` từ golden model, có manifest + checksum | Đủ phủ: min/max/zero/boundary/overflow |
| Sim | Verilator (nhanh, CI được) + cocotb (test bằng Python) | Mọi block có testbench riêng, pass |
| Assertions | SVA/`assert` cho handshake, overflow, FSM illegal state | Không vi phạm trong mọi run |
| Coverage | Toggle + line + functional | Ngưỡng công bố, không phải "đã có" |
| Bit-exact | RTL vs golden, **từng tầng một** | 0 mismatch trên toàn bộ vector |
| Trên board | ILA/VIO bắt tín hiệu thật | Dạng sóng khớp sim tại cùng vector |

> `pyproject.toml` hiện **không có** `cocotb` và không khai báo công cụ RTL nào. Phải thêm, nếu không thì cả mục này là văn.

### 6.4 ★ Clocking, CDC, constraints, timing closure — `plan.md` có 0 chữ

| Mục | Phải có |
|---|---|
| Clock plan | Liệt kê mọi domain: PL clock, audio MCLK/BCLK/LRCLK, DDR, PS. Vẽ sơ đồ. |
| CDC | Mọi chỗ vượt domain phải có synchronizer/async FIFO được gọi tên |
| XDC | File constraint thật, commit, có `create_clock` cho mọi domain |
| Reset | Sync hay async, domain nào, ai phát |
| Timing closure | Gate: **WNS ≥ 0** sau implementation, kèm báo cáo |
| Iteration time | Ghi lại thời gian tổng hợp/implementation thực đo — nó là chi phí thật của đề cương |

### 6.5 ★ Resource budget — phải là bảng có dẫn xuất, không phải "tiết kiệm 80–90%"

Mỗi khối: `LUT, FF, DSP48E2, BRAM36, URAM288` — **ước từ cấu trúc**, rồi **đối chiếu với `report_utilization` sau tổng hợp**, và báo chênh lệch. Con số của `plan.md` ("giảm thiểu 80%–90% DSP", "tiết kiệm 75–87% DRAM bandwidth", "tiết kiệm 50% bandwidth") **không có dẫn xuất và không có nguồn** → hoặc chứng minh bằng phép tính, hoặc xoá. Xem §9.1.

### 6.6 ★ Dataflow: FIFO, back-pressure, II

| Phải chốt | Vì sao |
|---|---|
| Kích thước mọi FIFO, tính từ burst + jitter | FIFO tràn/đói là lỗi "chạy 10 phút rồi treo" kinh điển |
| Back-pressure: TREADY ai giữ, deadlock ở đâu | AXI4-Stream không tự giải quyết được |
| II thực đo sau tổng hợp, không phải II mong muốn | `plan.md` nêu II=1 như mục tiêu; phải đo |
| Overflow ở mỗi tap | Có clamp hay wrap — phải khớp §6.2 |

### 6.7 ★ "KV-Cache" — thuật ngữ đang gây hiểu lầm

`plan.md` §4 mượn chữ "KV-Cache" từ LLM autoregressive decoding. Trong streaming Conformer, trạng thái cần giữ là **left-context của K/V theo chunk**, có vòng đời và kích thước hữu hạn, không phải cache tăng trưởng theo token. Gọi bằng tên LLM khiến reviewer hiểu sai thiết kế và khiến người học thiết kế sai bộ nhớ.

**Sửa:** đổi thành **"Left-Context K/V Ring Buffer"**, và nêu: dung lượng = `n_chunks_kept × chunk_len × d_head × n_head × 2 × bytes`, tính ra con số, đối chiếu §3.3.

---

## 7. LỘ TRÌNH 10 CHẶNG

Khớp 1:1 `docs/BOOK_STATUS.md`. Mỗi chặng có **điều kiện vào / artefact / gate nghiệm thu quan sát được / thời lượng ước**. Thời lượng là **ước lượng để hiệu chỉnh sau chặng 1**, không phải số đã kiểm chứng.

| Chặng | Chương | Điều kiện vào | Artefact (nộp được) | Gate nghiệm thu | Ước |
|---|---|---|---|---|---|
| 0 | — | P1+P2+P3 đạt (§2) | `data/captured/*.wav` + SHA-256; E0 log | `make exp-01` khớp librosa trong dung sai | 2–4 ngày |
| 1 | 01 | E0 xong | Sơ đồ khối + ngân sách latency từng tầng | Ngân sách cộng lại ≤ mục tiêu, có chữ ký của số đo | 1–2 tuần |
| 2 | 02 | Chốt SKU + JetPack (§3.1) | `results/exp02/` log thô + bảng P50/P90/P99, jitter, mJ/frame | Đo ≥3 run, idle đã trừ, metadata đủ 4 thành phần | 2–3 tuần |
| 3 | 03 | Chặng 2 xong | Roofline có số (§6.1) + Nsight Compute + **đã tối ưu Orin đúng cách** | **H0-A bị bác bỏ hoặc dự án đổi câu hỏi** ← gate thật | 3–4 tuần |
| 4 | 04 | Chặng 3 xong | Bảng tài nguyên ZU5EV đã verify + `DATASHEET_VERIFICATION.md` | Mọi ô có trang datasheet; không còn "4 MB/4.5 MB/3.02 MB" mâu thuẫn | 1–2 tuần |
| 5 | 05 | Chặng 4 | So sánh DPU/HLS/FINN/RTL **trên cùng một model**, có số | 4 hàng, mỗi hàng có log tổng hợp thật | 2–3 tuần |
| 6 | 06 | Chặng 5 | RTL `Line_Buffer_1D` + Requantizer + **golden model** | Bit-exact 0 mismatch, coverage ≥ ngưỡng, WNS ≥ 0 | 6–8 tuần |
| 7 | 07 | Chặng 6 | QAT/pruning bằng **Brevitas** + Δaccuracy có CI | H0-C đo được; số lượng hoá khớp §6.2 | 3–5 tuần |
| 8 | 08 | Chặng 7 | KWS SoC trên board: audio vào → kết quả ra | Chạy liên tục ≥1 giờ không treo; P99 đo trên board khớp sim ±10 % | 4–6 tuần |
| 9 | 09 | Chặng 8 | Streaming Conformer overlay + Left-Context Ring Buffer | WER đo được; **hoặc** báo cáo "không fit" kèm phép tính §3.3 ← kết quả hợp lệ | 8–12 tuần |
| 10 | 10 | Chặng 9 | Paper draft + artifact package + Pareto frontier | Vượt checklist §8.4; người khác tái lập được từ README | 4–6 tuần |

**Tổng ước: ~36–58 tuần** part-time. `plan.md` không có lịch nào.

### 7.1 ★ Ngân sách thất bại (Failure budget)

FPGA thật thì hỏng nhiều ngày liên tục. Đề cương phải tiên liệu, nếu không người học bỏ ở chặng 6–8.

| Rủi ro | Tần suất thực tế | Đệm đã tính |
|---|---|---|
| Timing không closure | Rất thường xuyên | +20 % thời gian chặng 6, 9 |
| Tool crash / project corruption | Thường xuyên | Commit mọi `.xpr`, giữ 1 bản build xanh |
| Tổng hợp/implementation qua đêm | Mỗi lần sửa RTL | Chiến lược: incremental compile + Verilator cho vòng lặp nhanh |
| Board brick / boot loop | Có, ít nhất một lần | Ghi quy trình recovery vào `docs/BOARD_RECOVERY.md` |
| License hết hạn | Nếu dùng bản không Community | Kiểm tra ở chặng 4 |
| Rounding mismatch gặm accuracy | Gần như chắc chắn | Test bit-exact **từng tầng** (§6.3) |

### 7.2 ★ Chi phí cập nhật mô hình — phản đối số một của giới thực hành

Phải có một mục trả lời: **nạp một model mới mà không viết lại RTL thì làm thế nào?** Nếu không trả lời được, thiết kế chỉ là một demo một lần, không phải một hệ thống. Hai hướng phải so: (a) weight-stationary với trọng số nạp từ DDR qua DMA; (b) overlay cố định + cấu hình qua tham số. Nêu chi phí mỗi hướng.

---

## 8. MÔI TRƯỜNG, HOÁ ĐƠN, VÀ CÔNG CỤ

### 8.1 ★ Bảng môi trường phát triển — nơi dự án tự học chết trong tuần đầu

| Thành phần | Yêu cầu | Ghi chú |
|---|---|---|
| Host chạy Vivado/Vitis | ⚠ disk (hàng chục GB), RAM, OS | Vivado trên Windows và Linux khác nhau ở chỗ sinh lỗi |
| Serial console cho Kria | Cable + driver | Không có thì không debug được boot |
| Host để flash Jetson | USB + `jetson-flash`/SDK Manager | |
| Network | Tải package rất lớn, một lần | |
| License | Community đủ hay cần bản quyền | Chốt ở chặng 4 |

### 8.2 ★ BOM — `plan.md` có 0 mục

| Item | Số lượng | Giá | Nguồn cung | Lead time | Phải kiểm chứng |
|---|---|---|---|---|---|
| Jetson Orin `<SKU>` | 1 | ⚠ | ⚠ | ⚠ | ⚠ SKU đuôi chữ cái |
| Kria KV260 | 1 | ⚠ | ⚠ | ⚠ | ⚠ còn được bán? |
| UBB carrier card (nếu cần I2S/PDM) | 1 | ⚠ | ⚠ | ⚠ | ⚠ **KV260 là kit Vision AI, audio không phải đường sẵn có** |
| Micro / mic array | 1 | ⚠ | ⚠ | ⚠ | |
| USB audio (phường dự phòng) | 1 | ⚠ | ⚠ | ⚠ | |
| Nguồn đúng công suất | 1 | ⚠ | ⚠ | ⚠ | ⚠ quá dòng là hỏng board |
| **Inline power meter / shunt + scope** | 1 | ⚠ | ⚠ | ⚠ | **bắt buộc — xem 8.3** |
| ESD mat, dây, heatsink/fan | — | ⚠ | ⚠ | ⚠ | |

### 8.3 ★ Đo năng lượng: XPE là ước lượng, không phải số đo

Xilinx Power Estimator cho **dự báo**. Nếu paper lấy số XPE ghi là "measured power" thì bị reject. Bắt buộc:
- Đo **tại wall/12V rail** bằng thiết bị độc lập, ghi cả idle.
- Hiệu chuẩn thiết bị, nêu độ phân giải và băng thông mẫu.
- Báo `mJ/frame = P_measured × T_frame`, với T_frame đo độc lập.
- So sánh XPE vs đo thực và **báo chênh lệch** — đó là một kết quả hay.

### 8.4 ★ Phụ thuộc phần mềm — repo đang thiếu thật

`pyproject.toml` hiện chỉ có numpy/scipy/matplotlib/rich/pydantic (+ audio, ml). Đề cương yêu cầu thêm và **pin version**:

| Package | Dùng ở | Trạng thái hiện tại |
|---|---|---|
| `brevitas` | Chặng 7 (QAT) — `book/TOC.md` chương 3 **đã yêu cầu** | ❌ chưa có |
| `cocotb` | Chặng 6 (verification) | ❌ chưa có |
| Verilator | Chặng 6 (sim trong CI) | ❌ chưa có, là binary ngoài → cần `docs/INSTALL.md` |
| `onnx` / `onnxruntime` | Chặng 3, 5 | ⚠ có ở optional `ml`, chưa pin |
| `pytest-cov` | Gate coverage | ❌ |

### 8.5 Phần còn lại của hệ thống — những thứ `plan.md` không nhắc mà không có thì không chạy

ALSA/PulseAudio latency và buffer trên Linux; câu hỏi real-time (Linux thường có đủ tốt để tuyên bố P99 không, hay cần PREEMPT_RT / bare-metal trên R5); đường ra (beep / command dispatch / transcript); logging; watchdog; hành vi khi khởi động lại giữa chừng.

---

## 9. KỶ LUẬT TRÍCH DẪN VÀ QUẢN TRỊ TÀI LIỆU

### 9.1 Mỗi claim phải có đúng một nguồn, hoặc bị gắn nhãn

`plan.md` có **4 claim định lượng dạng %** (dòng 32, 36, 58, 64) và **0 claim** nào có dẫn xuất. Quy tắc mới:

```
[claim] → [source id + trang/section] → [derivation hoặc measurement id]
```
Không đủ 3 vòng thì claim phải viết dưới dạng `⚠ CHƯA CHỨNG MINH — derivation TBD (exp_NN)`.

**Lỗi gán nguồn cụ thể trong `plan.md`:** `[R01-02]` (FINN — framework cho **binarized** NN inference) đang được dùng làm chỗ dựa cho **3** thứ khác nhau: tính toán không gian (dòng 25, hợp lý), **lý thuyết lượng tử hoá affine** (dòng 58, **sai** — FINN không phải nguồn của affine quantization), và HLS/FINN (dòng 85, trùng lặp). Dòng 58 phải đổi sang nguồn lượng tử hoá thật (Jacob et al. 2018, hoặc GEMMQL/quantization handbook), hoặc dẫn xuất thẳng từ §6.2.

**Lỗi lý thuyết lớn hơn:** `plan.md` §1.4 nêu "Lý thuyết Lượng tử hóa Affine $r=S(q-Z)$" và tuyên bố neo vào `source_index.json`, nhưng note đăng ký cho nó — `docs/research_notes/R03_quantization_for_speech.md` §2 — lại có tiêu đề **"Mathematical Uniform *Symmetric* Quantization Contract"** và đặt $S=x_{\max}/(2^{b-1}-1)$, tức trường hợp **không có zero-point**. Lý thuyết mà `plan.md` viện dẫn **không nằm trong nguồn mà `plan.md` đăng ký**. Phải hoặc thêm derivation asymmetric vào note, hoặc hạ cấp claim.

### 9.2 ★ Cách ly dữ liệu bịa — blocker nghiêm trọng nhất

`capstone/voice_edge_benchmark/benchmark_runner.py::build_default_benchmark_suite()` trả về **4 kết quả viết tay** (Orin Nano FP16 2.15 ms/8.8 W/97.4 %/52.8 FPS/W; Orin INT8 1.45 ms/8.2 W/97.2 %/84.1; KV260 DPU 1.10 ms/4.8 W/97.1 %/189.4; KV260 FINN 0.48 ms/3.9 W/96.9 %/534.2) với docstring *"reference comparative data reflecting empirical publications"*, và `__main__` in ra dưới nhãn **"Academic Benchmark Matrix"**. `tests/test_audio_pipeline.py` **assert trên chính các số đó**.

Đây là con đường ngắn nhất phá huỷ cả mục tiêu xuất bản lẫn uy tín cá nhân, và nó đang **xanh đèn trong CI**. Sửa bắt buộc:

1. Đổi tên → `synthetic_demo_fixture()`, docstring nêu **rõ** "SYNTHETIC PLACEHOLDER — not measured, never cite".
2. Thêm trường `provenance: Literal["synthetic","measured"]` vào `HardwareBenchmarkResult`; mọi hàm xuất (JSON, Pareto table) **phải in nhãn** theo trường này.
3. `__main__` không được in chữ "Academic Benchmark Matrix" khi còn hàng synthetic.
4. Test chỉ assert **cấu trúc** (đủ số hàng, đúng kiểu, đơn vị), **không** assert giá trị; và có `pytest.mark.skipif` khi chưa có log đo thật.
5. `scripts/verify_integrity.py` thêm gate: **không file nào được đánh dấu ✅ nếu `results/` không có log thô tương ứng có checksum.**

### 9.3 Số chương: 10 là canonical, và drift phải bất khả thi

`plan.md` + `book/TOC.md` nói 5; `README.md` + `docs/BOOK_STATUS.md` + `docs/EXPERIMENT_STATUS.md` + `tests/test_pedagogy.py` nói 10; commit gần nhất ghi "10-chapter roadmap". **10 thắng.** `plan-v2.md` đã theo §7.

Nhưng sửa một lần không đủ — phải làm cho drift quay lại được. Hiện `plan.md` và `book/TOC.md` là **untracked** và `grep` toàn repo cho thấy **không một file nào tham chiếu tới chúng**, nên không test nào có thể bắt được lệch. Hành động:

- `git add plan.md book/TOC.md` (hoặc xoá `book/TOC.md` và sinh nó từ `plan-v2.md`).
- Thêm `tests/test_plan_consistency.py`: số chặng trong `plan-v2.md` == số chương trong `docs/BOOK_STATUS.md` == số hàng trong `docs/EXPERIMENT_STATUS.md` == `10`.
- Thêm `make gate` chạy `pytest && ruff check && verify_integrity.py && test_plan_consistency`.

### 9.4 ★ Source ID scheme — hiện không thể mở rộng

Mọi id trong `docs/source_index.json` đều mang prefix `R01-` (`R01-01`…`R01-05`) dù chúng thuộc các chủ đề khác nhau ⇒ **không thể thêm nguồn cho chương 2** mà không phá hệ thống. Đồng thời mapping source→note đang **rối**:

| Source | Loại thật | Note được gán | Vấn đề |
|---|---|---|---|
| `R01-04` AMD Kria KV260 User Guide | FPGA hardware | `R01_jetson_orin_arch.md` | Claim phần cứng FPGA đang neo vào note về **NVIDIA** |
| `R01-03` Conformer | Kiến trúc attention | `R03_quantization_for_speech.md` | Claim attention đang neo vào note về **lượng tử hoá** |
| `R01-02` FINN | Framework | `R02_fpga_audio_streaming.md` | Đúng, nhưng note này lại chứa con số nhớ sai (§3.3) |

**Scheme mới:** `S<NNN>` toàn cục, duy nhất, **không** mang số chương (chương là thuộc tính, không phải danh tính). Thêm field `claims_supported: [claim_id...]` để `verify_integrity.py` kiểm được chiều ngược lại: *mọi claim trong sách phải trỏ tới một source có thật, và mọi source phải đỡ ít nhất một claim*.

### 9.5 Đánh số và thuật ngữ

- **Đánh số:** `plan.md` có `## 1. BÀI TOÁN GỐC`, rồi `## CƠ SỞ LÝ THUYẾT` **không số** mà bên trong tự đánh `### 1..4`, rồi `## 2..## 5`, rồi `## TỔNG KẾT`/`## TÀI LIỆU` không số ⇒ **có hai mục số "1" ở hai cấp**. Đề cương này đánh số phẳng, liên tục, mọi `##` có số.
- **Danh xưng quá cỡ:** "Định lý Tính toán Không gian", "Lý thuyết Phân tách Kênh-Thời gian ... chứng minh rằng giảm 80–90%" — đây **không phải định lý** và **không có chứng minh**. Vi phạm chính `docs/BOOK_PEDAGOGY.md` (mục 6: toán phải giải thích cơ chế, và phải nêu rõ điều *không* suy ra được). Hạ cấp thành "nguyên lý/mô hình" hoặc đưa ra chứng minh thật.
- **Thuật ngữ:** `plan.md` dùng II, HLS, QAT, MAC, FSM, DSP, DPU, STFT, ASR, KWS, WER mà không mở rộng ở nhiều chỗ ⇒ vi phạm mục 5 `BOOK_PEDAGOGY.md`. Giữ quy tắc: viết đầy đủ + tiếng Việt ở lần xuất hiện đầu tiên.

### 9.6 CI không tồn tại

Không có `.github/workflows/`. CLAUDE.md yêu cầu bước "Validate" nhưng **không có chỗ nào để validate tự chạy**. Thêm `ci.yml`: `make gate` + `verify_integrity` + (về sau) Verilator sim.

---

## 10. KHI NÀO LUẬN ĐIỂM SAI

Một đề cương không nói được điều gì sẽ làm nó sụp thì không bảo vệ được ở peer review.

| Điều kiện | Hệ quả |
|---|---|
| H0-A không bác bỏ (Orin đã tối ưu vẫn không memory-bound) | Đổi câu hỏi: từ "GPU nghẽn" sang "GPU tốn điện ở always-on" — vẫn là một paper, nhưng khác |
| Orin thắng ở cùng công suất | Kết quả trung thực vẫn đáng công bố; nêu rõ FPGA thắng ở đâu (có thể chỉ ở <1 W always-on) |
| Một MCU/NPU/ASIC rẻ hơn thắng **cả hai** | Phải nêu. Reviewer sẽ hỏi tại sao không dùng ASIC/NPU rời |
| Conformer không fit (§3.3) | Chặng 9 báo cáo "không fit" kèm phép tính — **đây là kết quả hợp lệ**, không phải thất bại |
| Chỉ một SKU + một board | Giới hạn phạm vi, nêu ở threats to validity, không được tổng quát hoá |

---

## 11. ARTEFACT VÀ PORTFOLIO

Reviewer chỉ có 5 phút. Sản phẩm phải là **thứ chạy được**, không phải một cuốn sách.

| Chặng | Artefact công khai được |
|---|---|
| 2 | Bảng + log profiling Orin thật, có metadata |
| 3 | Roofline có số + kết luận H0-A |
| 6 | Waveform bit-exact + coverage report |
| 8 | **Video 30 s: nói vào micro, thiết bị phản hồi**, kèm số đo trên board |
| 9 | Overlay + WER + đường cong accuracy-vs-latency |
| 10 | Artifact package tái lập được (theo chuẩn artifact evaluation của FCCM/FPGA) |

Mỗi artefact: repo công khai, tag, một bài viết ngắn mô tả *điều đã học được khi nó hỏng*.

---

## PHỤ LỤC A — DIFF v1 → v2 (tóm tắt)

| `plan.md` | `plan-v2.md` |
|---|---|
| Không có RQ, không có H0 | §1.1, §1.2 — 3 RQ, 3 H0, mỗi H0 có phép bác bỏ |
| "Jetson Orin" chung chung | §3.1 — chốt SKU + bảng verify |
| "4 MB" / "4.5 MB" / 3.02 MB mâu thuẫn | §3.3 — chỉ ra bằng số học của chính repo, bắt mở `DATASHEET_VERIFICATION.md` |
| Không có micro | §4.1 — nguồn âm, clock domain, WAV pin SHA-256 |
| Không chọn model/tác vụ; nhầm MatchboxNet là ASR | §4.2 — hai chương trình tách bạch, metric tách bạch |
| Không có decoder | §4.3 |
| Không có ngân sách latency | §4.4 — rightaway/future context bằng ms |
| Không dataset/seed/repetition/CI | §5.1 |
| Không related work, không threats | §5.5, §5.6 |
| Roofline không số | §6.1 |
| Không Q-format, không accumulator, không rounding | §6.2 |
| Không verification methodology | §6.3 — 7 lớp, gate bit-exact từng tầng |
| Không clock/CDC/XDC/timing | §6.4 |
| "80–90%", "75–87%", "50%" không dẫn xuất | §6.5 + §9.1 — hoặc chứng minh hoặc xoá |
| Không FIFO sizing/back-pressure/II đo được | §6.6 |
| "KV-Cache" mượn từ LLM | §6.7 — Left-Context K/V Ring Buffer, có công thức dung lượng |
| Milestone 1 = RTL, milestone 2 = đo baseline (đảo logic) | §7 — đo trước, thiết kế sau; gate H0-A ở chặng 3 |
| Không lịch, không failure budget | §7 — 36–58 tuần; §7.1 đệm rủi ro |
| Không chi phí cập nhật model | §7.2 |
| Không BOM, không dev host, không an toàn phần cứng | §8.1, §8.2 |
| XPE có thể bị dùng làm số đo | §8.3 — đo tại wall, báo chênh với ước lượng |
| Thiếu `brevitas` dù TOC yêu cầu | §8.4 |
| Benchmark bịa, test assert lên số bịa, CI xanh | §9.2 — cách ly + provenance field + gate |
| 5 vs 10 chương, file untracked, không test nào bắt được | §9.3 — 10 canonical + `test_plan_consistency.py` + `make gate` |
| Prefix `R01-` không mở rộng được; source→note rối | §9.4 — `S<NNN>` + `claims_supported` |
| Đánh số đụng nhau; "định lý" không chứng minh; thuật ngữ không mở rộng | §9.5 |
| Không CI | §9.6 |
| Không nói khi nào mình sai | §10 |
| Không có artefact/portfolio | §11 |

## PHỤ LỤC B — Số phải kiểm chứng trước khi bất kỳ file nào khác dùng lại

| Đại lượng | Hiện trạng | Nguồn hợp lệ duy nhất |
|---|---|---|
| On-chip SRAM của board | 3 giá trị mâu thuẫn | DS891 + `report_utilization` |
| LUT / DSP của board | `SOURCES.md` nêu, không dẫn trang | DS891 |
| Băng thông LPDDR5 từng Orin SKU | note nêu ~102/~68 GB/s, không dẫn | Datasheet + **đo thực** |
| "10–30 M tham số" cho Conformer | `plan.md` tự nêu | Paper đã công bố, chỉ rõ variant |
| "10W–25W" của Orin | `plan.md` nêu; note R01 lại nói idle 3–7 W | Đo tại wall, có metadata |
| 80–90 % DSP, 75–87 % BW, 50 % BW | Không dẫn xuất | Phép tính trong `docs/roofline/` hoặc xoá |
| 4 hàng benchmark trong `capstone/` | **Số bịa** | Không có nguồn — phải cách ly (§9.2) |

## PHỤ LỤC C — Đường bổ túc tiên quyết

C-1 RTL · C-2 Fixed-point · C-3 PyTorch · C-4 Jetson/Linux measurement. Mỗi mục: ≤3 tuần, kết thúc bằng một artefact nhỏ, không phải bằng "đã đọc".
