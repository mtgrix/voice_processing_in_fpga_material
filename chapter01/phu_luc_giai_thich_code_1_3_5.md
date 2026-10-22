# Phụ lục 1.3.5-A. Giải thích nguyên lý hoạt động của `audio_processing.py` và `evaluator.py` dưới góc nhìn Mục 1.3.5

> **Phạm vi.** Phụ lục này đối chiếu hai tệp trong thư mục `Pronunciation_Final_Master` của kho `DucDocDao/Pitch-Project` (nhánh `main`) với lý thuyết đo cao độ $F_0$ bằng tự tương quan ở Mục 1.3.5 (Praat, Boersma 1993). Để hiểu luồng gọi hàm, phụ lục có tham khảo thêm `main.py`, `visualizer.py`, `generate_audio.py` và `sentence_data.py`, nhưng chỉ ở những dòng liên quan. Mọi hành vi mô tả dưới đây đều lấy từ mã nguồn thực tế. Chỗ nào mã nguồn không đủ để khẳng định thì phụ lục ghi rõ là **chưa kiểm chứng**.

---

## 1. Bức tranh tổng thể: hai tệp làm gì trong hệ thống

### 1.1. Bài toán của dự án

Dự án so sánh **đường cao độ** (pitch contour, tức chuỗi giá trị $F_0$ theo thời gian) của một câu tiếng Anh do giọng tham chiếu đọc (giọng tổng hợp `sarah`) với cùng câu đó do một giọng khác đọc (các giọng nam Mỹ, ví dụ `michael`). Âm thanh được sinh bằng mô hình tổng hợp tiếng nói Kokoro (`generate_audio.py`). Kết quả cuối là hệ số tương quan Pearson $r$ giữa hai đường cao độ, đúng loại phép đối sánh mà Mục 1.3.5 (phần 0) nêu: *"đối sánh tương quan Pearson ($r$) với các công cụ âm học chuẩn mực phòng thí nghiệm như Praat"*.

### 1.2. Luồng xử lý một câu (theo `main.py`)

1. `trim_silence_and_save` (`audio_processing.py`): cắt khoảng lặng hai đầu, ghi ra tệp WAV đã cắt.
2. `extract_features_praat` (`audio_processing.py`): đo đường $F_0$ trên **chính tệp đã cắt** bằng Praat (thông qua thư viện `parselmouth`).
3. `get_user_timestamps` (`evaluator.py`): dùng mô hình nhận dạng tiếng nói Whisper để lấy mốc thời gian bắt đầu/kết thúc của từng từ, cũng trên **chính tệp đã cắt**.
4. `plot_analysis` (`visualizer.py`) gọi tiếp bốn hàm của `audio_processing.py`: `get_local_chunk` → `equalize_local_chunk` → `dynamic_sliding_window_pearson` → `summarize_pearson`, để căn chỉnh hai đường cao độ theo từng từ và tính $r$.
5. `summarize_sentence_reports` (`audio_processing.py`): gom kết quả nhiều câu thành bảng thống kê.

Ghi chú trong `main.py`, dòng 72: *"Both pitch and timestamps must refer to exactly this trimmed WAV"*. Nghĩa là cả $F_0$ lẫn mốc thời gian từ đều phải đo trên cùng một tệp, nếu không trục thời gian của hai đại lượng sẽ lệch nhau đúng bằng đoạn lặng đã cắt.

### 1.3. Hiểu lầm cần tránh ngay từ đầu

- **`evaluator.py` không chấm điểm.** Dù tên tệp là "evaluator", nó chỉ nạp Whisper và trả về danh sách mốc thời gian của từng từ. Phép so sánh và chấm điểm ($r$) nằm trong `audio_processing.py` và được gọi từ `visualizer.py`.
- **Không có dòng nào tự tính tổng tự tương quan.** Công thức (1) $R_x[\tau]$, cửa sổ Hanning, phép chuẩn hóa (6) và bảng tra (7) đều không xuất hiện trong mã Python. Chúng nằm bên trong Praat. Mã Python chỉ gọi một dòng `snd.to_pitch()`. Phần 3 dưới đây giải thích dòng đó thực chất là toàn bộ Mục 1.3.5.

---

## 2. Bảng thuật ngữ dùng trong phụ lục

| Thuật ngữ | Định nghĩa dùng ở đây |
|---|---|
| Khung phân tích (frame) | Đoạn $L$ mẫu liên tiếp để tính một giá trị $F_0$ (Mục 1.3.5, phần 2). |
| Bước nhảy $\Delta t_{hop}$ (time step) | Khoảng thời gian giữa tâm hai khung liên tiếp. |
| Điểm cao độ (pitch point) | Một phần tử trong mảng `pitch` trả về: $F_0$ của một khung, đơn vị Hz; bằng $0$ nếu khung bị phán là vô thanh. |
| Hữu thanh / vô thanh (voiced / unvoiced) | Khung có / không có dao động tuần hoàn của dây thanh. |
| Tổng tự tương quan $R_x[\tau]$ | Công thức (1) của Mục 1.3.5. Đây là tổng tích các cặp mẫu, **không phải tích chập**. |
| Hệ số tương quan Pearson $r$ | Thước đo mức độ hai chuỗi số cùng tăng cùng giảm theo quan hệ tuyến tính, nằm trong $[-1,1]$. **Khác hoàn toàn** với $r_x[\tau]$ của Công thức (6). |
| Căn chỉnh (alignment) | Đưa hai đường cao độ có độ dài khác nhau về cùng một trục chỉ số để so sánh từng điểm. |

> **Cảnh báo trùng ký hiệu.** Tài liệu dùng $r_x[\tau]$ cho tự tương quan chuẩn hóa (Công thức 6), còn mã nguồn dùng `r`, `mean_r` cho hệ số Pearson. Hai đại lượng này không liên quan. $r_x[\tau]$ đo mức một khung tín hiệu giống chính nó khi trượt đi $\tau$ mẫu. Pearson $r$ đo mức hai *đường cao độ* giống nhau về hình dạng. Phụ lục luôn viết "Pearson $r$" để phân biệt.

---

## 3. `extract_features_praat`: một dòng code chứa toàn bộ Mục 1.3.5

### 3.1. Mã nguồn

```python
def extract_features_praat(audio_path, verbose=False):
    snd = parselmouth.Sound(audio_path)
    pitch_object = snd.to_pitch()
    pitch = np.nan_to_num(pitch_object.selected_array["frequency"])
    time_stamps = pitch_object.xs()
    ...
    return pitch, time_stamps
```

### 3.2. Từng dòng làm gì

1. `parselmouth.Sound(audio_path)`: nạp tệp WAV thành đối tượng `Sound` của Praat. `parselmouth` là thư viện Python gọi thẳng vào mã C++ của Praat, nên kết quả trùng với kết quả của Praat chạy trên máy tính.
2. `snd.to_pitch()`: tương đương lệnh `Sound: To Pitch...` của Praat với **toàn bộ tham số mặc định**. Theo mã nguồn Praat, lệnh này gọi `Sound_to_Pitch_ac` (phương pháp tự tương quan) với: `time_step` tự động, `pitch_floor = 75 Hz`, `pitch_ceiling = 600 Hz`, 3 chu kỳ mỗi cửa sổ, `max_number_of_candidates = 15`, `very_accurate = off`, `silence_threshold = 0,03`, `voicing_threshold = 0,45`, `octave_cost = 0,01`, `octave_jump_cost = 0,35`, `voiced_unvoiced_cost = 0,14`. Đây **chính là 10 tham số của Bảng 1.3.5a**, giữ nguyên giá trị chuẩn.
3. `selected_array['frequency']`: lấy ứng viên mà thuật toán Viterbi đã chọn cho mỗi khung, tức đường $F_0$ cuối cùng. Khung vô thanh có giá trị $0$ (đúng nhánh "$F_0 = 0$ (Unvoiced)" trong Thẻ công thức của Mục 1.3.5). `np.nan_to_num` đổi mọi giá trị NaN thành $0$ nếu có, nên quy ước "0 Hz = vô thanh" được giữ thống nhất cho các hàm phía sau.
4. `pitch_object.xs()`: mảng thời điểm tâm của từng khung (giây). Hàm có trả về mảng này, nhưng `main.py` gọi `pitch, _ = extract_features_praat(...)` và **bỏ đi** (xem mục 3.5).

### 3.3. Ánh xạ sang lý thuyết

| Bước bên trong `to_pitch()` (Praat) | Mục/Công thức trong tài liệu |
|---|---|
| Cắt khung 3 chu kỳ của 75 Hz = 40 ms, bước nhảy $0{,}75/75 = 0{,}01$ s | Phần 3.A, tham số 1–2 |
| Nhân cửa sổ Hanning (vì `very_accurate = off`) | Phần 3, mục 2; tham số 4 |
| Tính $R_x[\tau]$ của khung đã nhân cửa sổ | Công thức (1) |
| Chia cho $R_w[\tau]$ | Công thức (5), (6) |
| Chỉ tìm đỉnh trong $[\tau_{min}, \tau_{max}]$ | Công thức (3), (4) |
| Ứng viên vô thanh, ngưỡng 0,45 và 0,03 | Tham số 6–7 |
| Phạt `octave_cost` theo $\log_2$ độ trễ | Tham số 8 |
| Viterbi với `octave_jump_cost`, `voiced_unvoiced_cost` | Tham số 9–10, Hình 1.3.5c (nhánh "Praat Viterbi") |
| $F_0 = f_s/\tau^*$ | Phần 2 |

Kết luận: dòng `pitch_object = snd.to_pitch()` **chính là toàn bộ Thẻ công thức của Mục 1.3.5**, nhưng là phiên bản phần mềm đầy đủ (nhánh bên phải Hình 1.3.5c), không phải phiên bản FPGA đã tối giản ở phần 4 của tài liệu.

### 3.4. Chỗ mã nguồn khác lý thuyết và hệ quả

**(a) Tần số lấy mẫu là 24 kHz, không phải 16 kHz.** `generate_audio.py` ghi tệp bằng `sf.write(path, ..., 24000)`. `trim_silence_and_save` nạp với `sr=None` (giữ nguyên tần số gốc) rồi ghi lại cùng `sr`. Vậy Praat đo $F_0$ trên tín hiệu $f_s = 24.000$ Hz. Toàn bộ con số đổi theo:

$$
\tau_{min} = \left\lceil \frac{24.000}{600} \right\rceil = 40 \text{ mẫu}, \qquad
\tau_{max} = \left\lfloor \frac{24.000}{75} \right\rfloor = 320 \text{ mẫu}
$$

$$
L = 0{,}040 \times 24.000 = 960 \text{ mẫu}, \qquad \Delta t_{hop} = 0{,}01 \text{ s} = 240 \text{ mẫu}
$$

So với tài liệu: dải lag tăng từ $[27, 213]$ (187 lag) lên $[40, 320]$ (281 lag); khung tăng từ 640 lên 960 mẫu. **Thời lượng** khung (40 ms) và dải **tần số** (75–600 Hz) không đổi, vì chúng được định nghĩa theo giây và Hz, còn số mẫu thì tỉ lệ với $f_s$.

Ví dụ số: một đỉnh tại $\tau^* = 200$ mẫu cho $F_0 = 24.000/200 = 120$ Hz ở dự án này. Cùng lag đó ở $f_s = 16$ kHz sẽ cho $16.000/200 = 80$ Hz. Vì vậy **không được** đem bảng tra lag của tài liệu áp vào dữ liệu của dự án.

Hệ quả với lượng tử hóa (phần 5 của tài liệu, mục "Phi tuyến lượng tử hóa"): ở $f_s = 24$ kHz, bước nhảy 1 lag gần trần cao độ là $24.000/40 - 24.000/41 \approx 14{,}6$ Hz, mịn hơn mức 22 Hz ở 16 kHz. Tuy nhiên Praat còn nội suy đỉnh dưới mẫu (sub-sample), nên trong dự án này $F_0$ **không** bị bậc thang hóa như phiên bản FPGA chỉ dùng lag nguyên. (Các bước bỏ đi ở phần 4 của tài liệu, như "Bỏ nội suy Sinc" và "Bỏ Viterbi", **không** áp dụng ở đây.)

**(b) Có Viterbi và 15 ứng viên.** Khác thiết kế FPGA (1 ứng viên, quyết định cục bộ từng khung), Praat ở đây duyệt toàn câu. Hệ quả: đường cao độ mượt hơn và ít lỗi nhảy quãng tám hơn, đổi lại phải có trọn câu mới ra kết quả. Với bài toán chấm điểm câu đã ghi âm sẵn, điều này không gây hại.

**(c) Không có lọc thông cao (HPF) 60 Hz.** Tài liệu (phần 4, khung "Cổng kiểm chứng phần mềm") yêu cầu dữ liệu "đã lọc tiền xử lý (HPF 60 Hz ở Mục 1.1.5)". Mã Python không có bước lọc nào trước `to_pitch()`. Với âm thanh tổng hợp từ Kokoro, nhiễu tần thấp có lẽ không đáng kể, nhưng đây vẫn là điểm lệch khỏi quy trình trong tài liệu.

**(d) Chưa kiểm chứng.** Chi tiết bên trong Praat, chẳng hạn $R_x[\tau]$ được tính trực tiếp theo Công thức (1) hay qua FFT, hoặc Praat có lấy mẫu lại nội bộ hay không, đều không nhìn thấy được từ mã Python. Phụ lục không khẳng định những điểm này.

### 3.5. Trục thời gian của mảng `pitch`

Với bước nhảy 10 ms, một câu dài $D$ giây cho khoảng $100D$ điểm cao độ. Vì khung dài 40 ms nên tâm khung đầu tiên **không** nằm ở $t = 0$ mà lùi vào khoảng nửa khung (cỡ 20 ms; đây là cách đặt khung thông thường của Praat, chưa chạy thử để kiểm chứng). Đây chính là hiện tượng "độ lệch tâm pha" của Hình 1.3.5d. Mảng `xs()` cho biết chính xác các thời điểm này, nhưng bị bỏ đi. Mục 5.1 phân tích hệ quả.

---

## 4. `trim_silence_and_save`: cắt khoảng lặng hai đầu

### 4.1. Mã nguồn

```python
y, sr = librosa.load(audio_path, sr=None)
y_trimmed, _ = librosa.effects.trim(y, top_db=top_db)  # top_db = 30
if not len(y_trimmed) or not np.any(y_trimmed):
    raise ValueError(...)
sf.write(trimmed_path, y_trimmed, sr)
```

### 4.2. Cơ chế

`librosa.effects.trim` chia tín hiệu thành các khung ngắn (mặc định của librosa: 2048 mẫu, bước 512 mẫu), tính năng lượng RMS từng khung đổi ra dB so với khung to nhất. Khung nào thấp hơn mức to nhất quá `top_db = 30` dB thì bị coi là lặng. Hàm chỉ cắt **phần lặng ở đầu và cuối**, không động vào khoảng lặng giữa câu.

Con số 30 dB nghĩa là gì: $10^{-30/20} \approx 0{,}0316$, tức biên độ còn khoảng **3,2 %** biên độ của khung to nhất.

### 4.3. So sánh với `silence_threshold = 0,03` của Praat

Hai ngưỡng có giá trị gần nhau (3,2 % và 3 %) nhưng **khác vai trò**:

| | `top_db = 30` (librosa) | `silence_threshold = 0,03` (Praat, tham số 6) |
|---|---|---|
| Tác động | Xóa hẳn mẫu ở hai đầu tệp | Chỉ làm khung yếu được gán $F_0 = 0$ qua $R_{unvoiced}$ |
| Phạm vi | Chỉ đầu và cuối | Mọi khung, kể cả giữa câu |
| Đại lượng so sánh | RMS khung (dB) | Biên độ đỉnh cục bộ / đỉnh toàn tệp |

Hiểu lầm cần tránh: cắt lặng **không** thay thế việc Praat phán vô thanh. Khoảng ngừng giữa câu và các phụ âm vô thanh vẫn cho $F_0 = 0$ trong mảng `pitch`.

Mục đích thật của bước cắt là **căn trục thời gian**: hai giọng đọc có đoạn lặng đầu dài ngắn khác nhau. Sau khi cắt, mốc $t = 0$ của cả hai gần với lúc bắt đầu phát âm hơn. Lưu ý: sau khi cắt, Praat đo lại trên tệp mới, nên khung đầu tiên lại lùi vào khoảng nửa khung so với $t=0$ mới (mục 3.5).

---

## 5. Căn chỉnh hai đường cao độ theo từng từ

### 5.1. `get_local_chunk`: cắt đoạn cao độ của một từ

```python
i1 = int((w_start / total_dur) * N)
i2 = int((w_end / total_dur) * N)
return raw_array[i1:i2]
```

Hàm đổi mốc thời gian của từ (giây, lấy từ Whisper) thành chỉ số trong mảng `pitch` theo **tỉ lệ**: $i = \lfloor (t / D) \cdot N \rfloor$, với $D$ = thời lượng tệp đã cắt (`len(y)/sr`) và $N$ = số điểm cao độ.

Ví dụ số: $D = 2{,}0$ s, $N = 197$ điểm, từ "hello" kéo dài từ 0,50 s đến 0,90 s, suy ra $i_1 = \lfloor 0{,}25 \times 197 \rfloor = 49$, $i_2 = \lfloor 0{,}45 \times 197 \rfloor = 88$, đoạn gồm 39 điểm.

**Chỗ khác lý thuyết.** Phép tỉ lệ ngầm giả định điểm cao độ thứ $i$ nằm ở thời điểm $i \cdot D/N$, tức các khung phủ đều từ $0$ đến $D$. Thực tế khung $i$ có tâm tại $t_1 + i \cdot 0{,}01$ s, với $t_1$ cỡ 20 ms (mục 3.5, Hình 1.3.5d). Cách đúng là dùng `xs()`, nhưng mảng này đã bị bỏ. Với ví dụ trên (nếu $t_1 = 0{,}02$ s), điểm 49 thực ra nằm ở $0{,}02 + 0{,}49 = 0{,}51$ s chứ không phải 0,50 s. Sai lệch luôn nhỏ hơn khoảng nửa khung (≈ 20 ms, tương đương ≤ 2 điểm cao độ), và giống nhau về bản chất ở cả hai giọng nên phần lớn tự bù trừ. Hệ quả nhỏ, nhưng là một điểm thiếu chính xác có thật.

### 5.2. `equalize_local_chunk`: kéo giãn đoạn cao độ cho bằng độ dài tham chiếu

```python
x_ref = np.linspace(0, 1, len(ref_chunk))
x_user = np.linspace(0, 1, len(user_chunk))
return np.interp(x_ref, x_user, user_chunk)
```

Cả hai đoạn được đặt lên cùng trục chuẩn hóa $[0,1]$ (đầu từ ↔ 0, cuối từ ↔ 1), sau đó đoạn của người đọc được **nội suy tuyến tính** tại đúng các vị trí của đoạn tham chiếu. Kết quả: hai đoạn có cùng số điểm. Đây là phép co giãn thời gian tuyến tính *trong phạm vi một từ*, đơn giản hơn so khớp động DTW.

Ví dụ số: từ "hello" của `sarah` có 39 điểm, của `michael` có 30 điểm. Đoạn của `michael` được lấy mẫu lại thành 39 điểm.

Trường hợp biên: nếu một trong hai đoạn rỗng, hàm trả về mảng toàn $0$ dài bằng `ref_chunk`. Vì quy ước 0 = vô thanh, các điểm này về sau bị loại khỏi phép tính Pearson.

**Lỗi tiềm ẩn: nội suy qua giá trị 0.** `np.interp` không biết $0$ nghĩa là "vô thanh". Tại ranh giới hữu thanh/vô thanh, ví dụ hai điểm liền nhau $[0, 200]$ Hz, một vị trí nội suy ở giữa sẽ nhận giá trị như $100$ Hz. Đây là một **$F_0$ giả**: không khung nào thật sự rung ở 100 Hz. Giá trị này $> 0$ nên lọt qua bộ lọc `valid` ở mục 6, và có thể làm giảm Pearson $r$ (một điểm tụt sâu bất thường). Muốn tránh, cần nội suy riêng các điểm hữu thanh hoặc đánh dấu vô thanh bằng NaN trước khi nội suy.

### 5.3. Ghép lại thành đường cao độ dài bằng tham chiếu (trong `visualizer.py`)

`plot_analysis` tạo `stitched_user_pitch = np.zeros(N_ref)`, rồi với mỗi từ khớp giữa văn bản chuẩn và kết quả Whisper (khớp bằng `difflib.SequenceMatcher`, chỉ lấy khối `equal`), dán đoạn đã kéo giãn vào đúng vị trí chỉ số của từ đó bên tham chiếu. Hệ quả:

- Các vị trí ngoài mọi từ (khoảng ngừng giữa từ) hoặc thuộc từ Whisper nhận sai đều giữ giá trị $0$, nên bị loại khỏi Pearson.
- Đường tham chiếu `raw_ref_pitch` giữ **nguyên vẹn**. Chỉ đường của người đọc bị co giãn.

---

## 6. `dynamic_sliding_window_pearson`: tính Pearson $r$ trên các cửa sổ trượt

### 6.1. Mã nguồn chính

```python
W = max(6, int((2 * N) / (num_words + 2)))
if W % 2 != 0:
    W -= 1
S = max(1, W // 2)
num_slides = num_words + 1
...
valid = (u_win > 0) & (r_win > 0)
if np.sum(valid) >= 3 and np.std(u_win[valid]) > 0 and np.std(r_win[valid]) > 0:
    r = np.corrcoef(u_win[valid], r_win[valid])[0, 1]
else:
    r = np.nan
```

### 6.2. Nguồn gốc công thức kích thước cửa sổ

Gọi $K$ = `num_words` (số từ của câu chuẩn), $N$ = số điểm cao độ tham chiếu. Mã tạo $K+1$ cửa sổ dài $W$, mỗi cửa sổ gối lên cửa sổ trước một nửa (bước $S = W/2$). Tổng độ dài phủ được là:

$$
\underbrace{K \cdot S}_{\text{vị trí bắt đầu cửa sổ cuối}} + W = K\frac{W}{2} + W = \frac{(K+2)W}{2}.
$$

Đặt tổng này bằng $N$ ta được $W = \dfrac{2N}{K+2}$, đúng biểu thức trong mã. Ý nghĩa: số cửa sổ bám theo số từ, mỗi cửa sổ dài khoảng **hai lần thời lượng trung bình của một từ**, nên mỗi cửa sổ thường chứa trọn một đến hai từ. Mã còn ép $W$ chẵn để $S = W/2$ là số nguyên, đặt tối thiểu $W = 6$, và cửa sổ cuối được kéo dài tới $N$ để bù phần dư do làm tròn.

Ví dụ số: câu 8 từ, $N = 197$ điểm (≈ 2 s): $W = \lfloor 394/10 \rfloor = 39$, ép chẵn thành $38$; $S = 19$; có 9 cửa sổ bắt đầu tại $0, 19, 38, \dots, 152$. Cửa sổ cuối chạy từ 152 đến 197 (45 điểm).

### 6.3. Hệ số Pearson trên từng cửa sổ

Trong mỗi cửa sổ, chỉ giữ các chỉ số mà **cả hai** đường đều hữu thanh ($F_0 > 0$). Với $M$ điểm hợp lệ $(u_i, v_i)$:

$$
r = \frac{\sum_{i=1}^{M}(u_i - \bar u)(v_i - \bar v)}{\sqrt{\sum_{i=1}^{M}(u_i-\bar u)^2}\,\sqrt{\sum_{i=1}^{M}(v_i-\bar v)^2}}
$$

Đây là việc `np.corrcoef(...)[0, 1]` thực hiện. Cửa sổ bị gán NaN (không tính) khi có ít hơn 3 điểm hợp lệ, hoặc khi một đường phẳng tuyệt đối ($\sigma = 0$, mẫu số bằng 0).

**Vì sao Pearson phù hợp khi so giọng nam với giọng tham chiếu `sarah`:** Pearson không đổi khi một chuỗi bị cộng thêm hằng số hoặc nhân với hằng số dương. Nếu `michael` nói trầm hơn `sarah` một quãng tám ($F_0$ bằng một nửa) nhưng lên xuống giống hệt, ta có $u_i = 0{,}5\,v_i$ và $r = 1$. Vậy chỉ số này đo **hình dạng ngữ điệu**, không đo độ cao tuyệt đối.

Ví dụ số: $v = [200, 220, 240, 220]$ Hz, $u = [100, 110, 120, 110]$ Hz: $r = 1{,}0$. Nếu $u = [120, 110, 100, 110]$ (ngữ điệu ngược) thì $r = -1{,}0$.

Hiểu lầm cần tránh:

- Pearson tính trên **Hz tuyến tính**, không đổi sang semitone hay thang log. Nếu hai giọng khác nhau đúng theo một tỉ lệ thì vẫn ra $r=1$ như trên. Tuy nhiên, khi chuyển động cao độ được đo bằng semitone (tỉ lệ), thang Hz đặt trọng số lớn hơn cho các vùng cao. Mã không xử lý điểm này.
- Pearson **không phải** là tự tương quan $r_x[\tau]$ trong Công thức (6). Nó so hai đường $F_0$ (mỗi đường đã là đầu ra của Công thức (6) qua Praat), không so tín hiệu với chính nó.
- Quy ước loại điểm "$F_0 = 0$" chính là cách mã tận dụng nhánh "Unvoiced" của Praat: chỉ so những khung mà **cả hai** giọng đều được Praat công nhận có tuần hoàn ($r_x \ge 0{,}45$ sau Viterbi).

### 6.4. Đặc điểm cần biết

- `num_words` lấy theo số từ của câu chuẩn (`len(ref_words_json)`), kể cả những từ Whisper không nhận được.
- Do tồn tại "$F_0$ giả" ở mục 5.2, một số điểm hợp lệ trong cửa sổ có thể là điểm nội suy giữa 0 và giá trị thật.

---

## 7. `summarize_pearson` và `summarize_sentence_reports`: từ cửa sổ đến điểm số

### 7.1. Điểm của một câu

```python
valid = values[np.isfinite(values)]
'mean_r': float(np.maximum(valid, 0).mean())
```

1. Bỏ các cửa sổ NaN (chính sách `missing_r_policy = 'exclude'`).
2. Đổi mọi $r \le 0$ thành $0$ (chính sách `nonpositive_r_policy = 'zero'`). Lý do theo docstring: tương quan âm hay bằng 0 đều được coi là "không giống", không bị phạt thêm.
3. Lấy trung bình, ra `mean_r` của câu, nằm trong $[0, 1]$.

Ví dụ số: 9 cửa sổ cho $[0{,}9;\ 0{,}8;\ \text{NaN};\ -0{,}4;\ 0{,}7;\ 0{,}6;\ \text{NaN};\ 0{,}85;\ 0{,}75]$. Bỏ 2 NaN, còn 7 giá trị; $-0{,}4 \to 0$; tổng $= 0{,}9+0{,}8+0+0{,}7+0{,}6+0{,}85+0{,}75 = 4{,}6$; `mean_r` $= 4{,}6/7 \approx 0{,}657$; `valid_r_count = 7`, `missing_r_count = 2`.

Hệ quả cần biết: phép kẹp về 0 làm `mean_r` **cao hơn** trung bình thô ($(4{,}6-0{,}4)/7 = 0{,}6$ trong ví dụ). Ngoài ra, một câu có ít cửa sổ hợp lệ vẫn được tính như câu đủ cửa sổ.

### 7.2. Thống kê nhiều câu

`summarize_sentence_reports` đếm số câu (trạng thái `ok`, có `mean_r`) đạt `mean_r` $\ge$ mỗi ngưỡng $0{,}9;\ 0{,}8;\ \dots;\ 0{,}3$ (`range(9, 2, -1)` chia 10). Các ngưỡng mang tính **cộng dồn**: câu đạt $0{,}9$ cũng được đếm ở mọi ngưỡng thấp hơn. Hàm cũng báo số câu đã xử lý, số câu có điểm và số câu không có điểm. Mã không quy định ngưỡng nào là "đạt". Phần diễn giải thuộc về người dùng kết quả.

Lưu ý nhỏ: `threshold / 10` dùng số thực, ví dụ $0{,}3$ thực ra là $0{,}30000000000000004$. Một câu có `mean_r` đúng bằng 0,3 về lý thuyết có thể không được đếm ở mốc "0.3". Trong thực tế rất khó xảy ra.

---

## 8. `evaluator.py`: lấy mốc thời gian của từng từ

### 8.1. Mã nguồn chính

```python
torch.set_num_threads(min(4, torch.get_num_threads()))
whisper.load_model('base', ...)
...
audio, sr = sf.read(audio_path, dtype='float32')
if audio.ndim > 1: audio = audio.mean(axis=1)
if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
result = model.transcribe(audio, word_timestamps=True, fp16=False, language='en')
return [dict(word=normalize_word(w['word']), start=w['start'], end=w['end']) ...]
```

### 8.2. Từng bước

1. `load_stt_model`: giới hạn số luồng CPU tối đa là 4 (chú thích trong mã: tránh tranh chấp luồng khi phiên âm câu ngắn) và nạp mô hình Whisper cỡ `base`.
2. `get_user_timestamps`: đọc **tệp đã cắt lặng**, trộn stereo về mono bằng trung bình kênh, lấy mẫu lại từ 24 kHz về **16 kHz** (Whisper yêu cầu đầu vào 16 kHz), rồi phiên âm tiếng Anh, chạy số thực 32 bit (`fp16=False`) và bật mốc thời gian theo từ.
3. Mỗi từ được chuẩn hóa bằng `normalize_word`: bỏ mọi ký tự không phải chữ/số, rồi viết thường (ví dụ `" Hello,"` thành `"hello"`), để khớp với văn bản chuẩn bằng `difflib`.

### 8.3. Đặc trưng cao độ mà phép chấm điểm dựa vào

`evaluator.py` **không đọc** đặc trưng cao độ nào. Nó chỉ cung cấp **ranh giới thời gian của từ**. Phép chấm điểm dựa trên:

- đường $F_0$ theo khung 10 ms của Praat (chỉ các khung hữu thanh $F_0>0$);
- mốc `start`/`end` của từ do Whisper đưa ra, dùng để cắt và co giãn đường $F_0$ (mục 5);
- Pearson $r$ trên các cửa sổ cỡ khoảng hai từ (mục 6).

Mã không dùng cường độ, trường độ hay giá trị $F_0$ tuyệt đối để chấm điểm.

### 8.4. Liên hệ với tài liệu và hiểu lầm cần tránh

- Con số 16 kHz ở đây **trùng** với $f_s$ của tài liệu, nhưng chỉ áp dụng cho Whisper. Praat vẫn đo $F_0$ trên tín hiệu 24 kHz (mục 3.4a). Hai mô-đun dùng hai tần số lấy mẫu khác nhau trên cùng một tệp. Điều này không gây lệch thời gian, vì lấy mẫu lại giữ nguyên thời lượng tính bằng giây.
- Bên trong, Whisper dùng đặc trưng Log-Mel (Mục 1.3), tức chính loại đặc trưng mà Mục 1.3.5 phần 0 nói là "xóa bỏ cao độ". Điều này hợp lý: Whisper chỉ cần biết **từ nào** được nói và **khi nào**, còn **cao độ** do luồng Praat riêng đảm nhận. Đây đúng là kiến trúc **hai luồng song song** (Log-Mel và F0) mà tài liệu đề xuất.
- Độ chính xác của mốc thời gian theo từ từ Whisper không được mã kiểm tra. Mọi sai lệch ranh giới từ sẽ truyền thẳng vào phép căn chỉnh ở mục 5.

---

## 9. Bảng tổng hợp: tài liệu và mã nguồn

| Đại lượng | Tài liệu Mục 1.3.5 | Mã nguồn dự án | Hệ quả |
|---|---|---|---|
| Tính $F_0$ | Tự cài Công thức (1), (5)–(7) | `parselmouth` `to_pitch()` | Dùng đúng Praat chuẩn |
| $f_s$ khi đo $F_0$ | 16.000 Hz | 24.000 Hz (Kokoro) | $\tau\in[40,320]$, $L=960$ |
| Dải $F_0$ | 75–600 Hz | 75–600 Hz (mặc định) | Trùng |
| Khung / bước | 40 ms / 10 ms | 40 ms / 10 ms (mặc định) | Trùng |
| Cửa sổ | Hanning | Hanning (`very_accurate=off`) | Trùng |
| Ngưỡng | 0,45 / 0,03 / 0,01 | Mặc định Praat, giống tài liệu | Trùng |
| Chọn đỉnh | FPGA: 1 ứng viên, lag nguyên | 15 ứng viên + Viterbi + nội suy | Mượt hơn, không bậc thang |
| HPF 60 Hz | Có (Mục 1.1.5) | Không có | Lệch quy trình |
| Khử lặng | `silence_threshold` theo khung | Thêm `librosa.trim` 30 dB ở hai đầu | Chỉ để căn trục thời gian |
| Đối sánh | Pearson $r$ với Praat | Pearson theo cửa sổ ~2 từ, chỉ dùng khung hữu thanh | Đo hình dạng ngữ điệu |
| $f_s$ cho nhận dạng | 16 kHz (Log-Mel) | 16 kHz (Whisper) | Trùng |

---

## 10. Danh sách điểm lệch và lỗi tiềm ẩn

1. **Bỏ mảng thời gian `xs()`**, suy chỉ số theo tỉ lệ $t/D$. Sai lệch tối đa cỡ nửa khung (~20 ms, khoảng 2 điểm cao độ) (mục 5.1).
2. **Nội suy tuyến tính qua điểm vô thanh** ($0$ Hz) sinh $F_0$ giả ở ranh giới hữu thanh/vô thanh, các giá trị này lọt qua bộ lọc `> 0` (mục 5.2).
3. **$f_s = 24$ kHz** thay vì 16 kHz. Mọi con số lag/mẫu của tài liệu không dùng trực tiếp được (mục 3.4a).
4. **Không có HPF 60 Hz** như tài liệu yêu cầu cho phần kiểm chứng phần mềm (mục 3.4c).
5. **Kẹp $r\le 0$ về 0** khiến `mean_r` cao hơn trung bình thô. Câu có ít cửa sổ hợp lệ được tính ngang câu đủ cửa sổ (mục 7.1).
6. **Tên `evaluator.py` dễ gây hiểu lầm**: tệp này không chấm điểm (mục 1.3, 8.3).
7. Pearson tính trên Hz tuyến tính, không trên semitone (mục 6.3). Đây là lựa chọn thiết kế, không phải lỗi.
8. Ngưỡng số thực `threshold/10` có sai số làm tròn rất nhỏ (mục 7.2).
