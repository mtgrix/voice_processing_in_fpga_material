# Book Pedagogy Policy — Voice Edge AI: Jetson Orin to FPGA

> **Canonical authoring policy.** Every chapter draft, revision, experiment, and research note MUST comply with this document.
> Last updated: 2026-09-14 (sections 7 to 10: the equation card, traceability out of prose, the six-stage pipeline, figure duty)

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
3. **Ứng dụng (Application)** — Hệ quả thực tế của nó là gì? Ảnh hưởng thế nào đến độ trễ (latency), năng lượng (Joules), hoặc chất lượng âm thanh **theo đúng metric của tác vụ đang xét** (KWS: accuracy/EER, ASR: WER/CER, tăng cường tiếng nói: PESQ/STOI — xem `plan-v2.md` §5.3) trên Jetson Orin hoặc FPGA.

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

---

## 7. The Equation Card (Thẻ Công thức) — every printed formula, no exceptions

Quy tắc 6 là nguyên tắc. Thẻ công thức là dạng trình bày bắt buộc để nguyên tắc đó không thể bị bỏ sót
khi đọc lại. Mọi biểu thức display math trong bản thảo tiếng Anh phải đi kèm đủ năm phần, theo đúng thứ
tự, với năm lead-in in đậm. Một chương có quyền gộp nhiều biểu thức vào một thẻ, và phải nói rõ vì sao.

```text
**The formula.**        <biểu thức, display math>
**The variables.**      <một dòng cho mỗi ký hiệu: nó là gì, đơn vị là gì>
**What it means.**      <vì sao viết như vậy chứ không phải cách khác; văn xuôi, không ký hiệu mới>
**What it costs.**      <giá trong silicon: LUT, DSP slice, BRAM/URAM tile, chu kỳ, stall>
**What it does not say.** <hiểu lầm phổ biến mà công thức này mời gọi>
```

Ranh giới áp dụng, ghi rõ để không tranh luận về sau:

* `$x$` inline trong câu văn không phải một biểu thức in ra; nó là một từ. Không thẻ.
* Một biểu thức trong `$$ ... $$`, hoặc một phương trình được đánh số để trích dẫn, luôn cần thẻ.
* Phần **What it costs** được phép nói "không đăng ký" khi registry không có số liệu; nó không được
  phép bỏ trống, và không được phép bịa một con số. Đây là chỗ duy nhất sự thiếu bằng chứng bắt buộc
  phải hiển thị ra ngoài.
* **The variables** định nghĩa *mọi* ký hiệu, kể cả ký hiệu đã xuất hiện ở thẻ trước đó trong cùng
  chương. Nguyên tắc Tự đủ Cục bộ (§1) thắng tiết kiệm chữ.

Ví dụ tối thiểu, để dạng thức không bị hiểu sai:

> **The formula.** $v = a \times t$
>
> **The variables.**
> - $v$ — vận tốc, tính bằng m/s.
> - $a$ — gia tốc, tính bằng m/s².
> - $t$ — thời gian trôi qua kể từ khi vận tốc bằng 0, tính bằng s.
>
> **What it means.** Gia tốc là "mỗi giây thì vận tốc tăng thêm bao nhiêu". Nhân nó với số giây đã trôi
> qua cộng dồn những lần tăng đó lại, nên ta có vận tốc hiện tại.
>
> **What it costs.** Một bộ nhân. Nhân với hằng số là dây nối và dịch bit; nhân với biến là một DSP
> slice bị chiếm suốt phép tính.
>
> **What it does not say.** Công thức đúng chỉ khi $a$ không đổi và $v$ bắt đầu từ 0. Với hai điều kiện
> bị bỏ, nó là một phỏng đoán.

---

## 8. Traceability lives in a table, never in a sentence

`V-xx-yy` là con trỏ tới hồ sơ bằng chứng. Nó không phải một từ loại trong câu, và khi nằm trong câu nó
cắt đôi mệnh đề mà người đọc đang theo.

* Trong văn xuôi: **không** có `V-xx-yy`. Không paren, không inline.
* Mỗi mục (section) kết thúc bằng một bảng **Traceability**: một hàng cho mỗi hồ sơ mục đó dựa vào, kèm
  điều hồ sơ đó thực sự nói.
* Bảng số liệu giữa mục giữ cột nguồn của riêng nó (`Where it comes from`). Đây là ngoại lệ bắt buộc,
  không phải sơ suất: `scripts/verification/scan_numbers.py` coi một hàng bảng không có trích dẫn là một
  claim không nguồn, và nó tính phạm vi trích dẫn **theo mục**, không theo file. Vì vậy bảng traceability
  đặt ở cuối *mục* thì hợp lệ, còn đặt ở cuối *file* (kiểu footnote `[^1]`) thì làm hỏng cage: các số in
  trong mục không còn hồ sơ nào cùng phạm vi.
* Một claim dẫn xuất vẫn phải ghi rõ là dẫn xuất, và nêu tên các hồ sơ là số hạng.
* Một chữ số trần trong văn bản luôn bị đọc là một đại lượng. `scan_numbers.py` bắt cả `1.` của danh sách đánh số lẫn `| **1 Air and microphone** |` của một bảng, và nó chỉ miễn cho "chapter 4" ở dạng số ít -- "chapters 4, 5 and 8" không khớp mẫu, nên hai số sau vẫn bị tính. Vì vậy: danh sách tầng viết bằng gạch đầu dòng, tên tầng đứng một mình không số, nhiều chương thì nhắc lại mỗi lần một chương, và số tầng chỉ xuất hiện trong fence `tikz` -- vùng đã được miễn. Thứ tự của sáu tầng do chính thứ tự dòng trong danh sách giữ.

---

## 9. One pipeline, named once, mapped everywhere

Sách phải có một bức tranh tổng trước khi có một chi tiết nào. Chương 1 mở đầu bằng **The Journey of an
Audio Frame**: một sơ đồ khối, sáu tầng được đặt tên, từ không khí tới quyết định. Sáu tên đó là
`Air and microphone`, `Sample stream`, `DSP front end`, `Model`, `Fabric logic`, `Output and latency`
và được dùng nguyên văn để người đọc luôn biết mình đang đứng ở tầng nào.

* Mọi chương khác mở đầu bằng một câu chỉ vào một trong sáu tầng đó.
* Một khái niệm không thuộc tầng nào thì không thuộc sách.
* Sơ đồ là thẩm quyền thứ tự cho các tầng; `plan-v2.md` vẫn là thẩm quyền cho nội dung kỹ thuật.

---

## 10. Visual density: a concept with a shape gets a figure

Mỗi khái niệm có hình dạng phải có hình vẽ, vì mô tả bằng lời một hình dạng là bắt người đọc tự dựng lại
hình đó trong đầu — đúng cái việc sơ đồ sinh ra để khỏi phải làm.

* Đối tượng bắt buộc có hình: đường ống dữ liệu, bộ đệm vòng, đệm trượt theo thời gian, ma trận điểm và
  mask của nó, biểu đồ tài nguyên, đường roofline, và mọi so sánh "A chặt hơn B" mà chỉ khác nhau về hình.
* Hình vẽ bằng `tikz` trong `::: {#fig-slug .figure}`, caption là đoạn văn sau fence, và **prose phải
  trỏ tới nó** bằng `[Figure N](#fig-slug)` — `verify_book_pdf.sh` check 6 từ chối một div không ai trỏ
  tới, và từ chối số caption khác số fence.
* Con số trong hình là hình học, không phải claim: `scan_numbers.py` miễn vùng fenced. Một nhãn in *số
  liệu của thế giới* trong hình vẫn phải có hồ sơ, và hồ sơ đó nằm trong bảng traceability của mục.
* Thư viện TikZ khả dụng chỉ là `arrows.meta`, `positioning`, `calc` (`book/header.tex`). Không `matrix`,
  không `patterns`, không `decorations`.
* Đo một hình mới là một nửa việc kiểm. `make book-figsize` so *cả hình* với khối văn bản của trang; nó
  không bao giờ so bộ phận này với bộ phận khác bên trong hình, nên một nhãn mọc xuyên qua hộp nét đứt vẽ
  quanh nó vẫn qua mọi con số. Hình mới vì vậy phải được *nhìn*: chạy probe, rồi `pdftoppm -png -r 200
  -singlefile` trên đúng PDF nó để lại, rồi mở ảnh lên. Và mở file ảnh của lần probe **cuối**, không phải
  của lần trước — một artifact cũ trả lời y hệt một artifact mới.
