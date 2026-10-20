## 1.1.5 Mẫu Âm Thanh Chưa Phải Là Áp Suất Không Khí

> 💡 **MỤC TIÊU HỌC TẬP**
> Mục 1.2 sẽ nhận một gói mẫu hữu hạn và biến nó thành phổ. Mục này nói về từ dữ liệu đến trước khi gói đó tồn tại. Micro số xuất ra đúng số 0 trong một số xung nhịp bit cố định, và bộ lọc thông cao sẵn có bên trong micro nằm rất thấp so với cao độ của tiếng nói. Chúng ta tính độ dài khoảng câm ở $16\text{ kHz}$, thêm một biquad thông cao tại $60\text{ Hz}$, và giữ bộ đệm vòng đóng cho đến khi cả khoảng câm lẫn pha khởi động của chính bộ lọc đã đi qua.

Mục 1.1 khép lại bằng một thế lưỡng nan: bộ xử lý biên phải cắt một làn sóng áp suất không có điểm dừng thành những gói hữu hạn, và không được phép chờ để gom lô. Mục 1.2 trả lời bằng bộ đệm vòng, cửa sổ, và phép biến đổi. Cả hai mục đều đúng về cái gói. Cả hai đều bắt đầu chậm một bước. Con số rời khỏi micro I²S (Inter-IC Sound — đường dữ liệu số nối tiếp giữa micro và bộ xử lý) là một từ 24 bit. Nó chỉ trở thành một mẫu của áp suất không khí sau khi hai cổng đã mở.

Tầng tiền xử lý của sách này nghe ở $f_s = 16\text{ kHz}$. Một chu kỳ lấy mẫu dài $62{,}5\,\mu\text{s}$. Bộ đệm mà Mục 1.2 sẽ đóng giữ 400 mẫu, và bước tới 160 mẫu, tức $10\text{ ms}$. Cao độ thấp nhất mà bộ đệm đó phải giữ là $85\text{ Hz}$. Cộng hưởng nguyên âm đầu tiên nằm quanh $300\text{ Hz}$. Thứ gì mục này loại bỏ thì phải biến mất trước khi 400 mẫu ấy được niêm phong, vì phép biến đổi không nhìn thấy từ thô. Nó nhìn thấy khung đã đóng.

---

### Một phần tư giây toàn số 0

Micro đứng trước chuỗi này là INMP441, micro MEMS (hệ vi cơ điện tử) cổng đáy, từ đầu ra 24 bit theo I²S. Datasheet của nó nêu một luật khởi động: micro xuất số 0 trong $2^{18}$ chu kỳ SCK (serial clock — xung nhịp bit) đầu tiên sau khi được cấp nguồn. Ở SCK bằng $3{,}072\text{ MHz}$, khoảng câm dài $85\text{ ms}$.

$2^{18}$ là $262.144$. Chia cho $3{,}072\text{ MHz}$ được $85{,}333\text{ ms}$. Con số $85\text{ ms}$ trong datasheet là thương ấy, đã làm tròn. Datasheet cũng chốt $f_{\mathrm{SCK}} = 64 \times f_{\mathrm{WS}}$: 64 chu kỳ SCK cho mỗi khung stereo, dù từ dữ liệu chỉ dài 24 bit. Ở $16\text{ kHz}$, xung nhịp bit là $1.024.000\text{ Hz}$.

> **Công thức.** $T_{\mathrm{mute}} = 2^{18} / (64\, f_s)$
>
> **Các biến.** $T_{\mathrm{mute}}$ là thời gian từ xung bit đầu đến từ khác 0 đầu tiên, tính bằng giây. $2^{18}$ là số đếm khởi động, tính bằng chu kỳ SCK. $64$ là số chu kỳ SCK mỗi khung stereo. $f_s$ là tần số lấy mẫu; ở đây $16.000\text{ Hz}$, và nó cũng là $f_{\mathrm{WS}}$.
>
> **Ý nghĩa.** Khoảng câm là một số đếm xung bit. $85\text{ ms}$ thuộc về xung $3{,}072\text{ MHz}$. Xung của sách này là $1{,}024\text{ MHz}$, nên cùng số đếm kéo dài hơn theo tỷ lệ ấy.
>
> **Giá trên silicon.** Một bộ đếm và một tín hiệu cho phép ghi. Con trỏ ghi của bộ đệm vòng đứng yên trong lúc đếm. Không có phép nhân. Cái giá trả một lần, lúc bật nguồn.
>
> **Điều công thức không nói.** Đây là khoảng câm của INMP441 với khung 64 xung. Micro khác có số đếm khác. Sau từ khác 0 đầu tiên, bộ đếm đã xong; công thức không mô tả khoảng lặng giữa hai câu nói.

Lab tính ở $16\text{ kHz}$: $T_{\mathrm{mute}} = 262.144 / 1.024.000 = 0{,}256\text{ s}$. Đó là $4.096$ mẫu, tức $25{,}6$ bước nhảy của 160 mẫu. Khoảng câm phủ 25 bước nhảy trọn và 96 mẫu của bước kế. Bộ đệm nếu bắt đầu từ xung đầu sẽ niêm một khung ngang ranh giới ấy, và phép biến đổi đọc khung đó như một bước nhảy. Bỏ $4.096$ từ bằng 0 thì khung ấy không được dựng. Con trỏ ghi bắt đầu tại từ khác 0 đầu tiên.

> 💡 **NHÌN THẤY VẬT LÝ**
> $256\text{ ms}$ là khoảng giữ lúc khởi động, trả một lần mỗi lần bật nguồn. Hạn $10\text{ ms}$ của Mục 1.1 bắt đầu khi con trỏ ghi được thả.

---

### Bộ lọc thông cao bên trong micro là một bộ lọc khác

Datasheet có một bộ lọc thông cao. Đọc ở $16\text{ kHz}$, nó nằm rất thấp so với tiếng nói.

Bảng 7 cho bộ lọc số ở $48\text{ kHz}$ danh định: $-3\text{ dB}$ tại $3{,}7\text{ Hz}$, $-0{,}5\text{ dB}$ tại $10{,}4\text{ Hz}$, $-0{,}1\text{ dB}$ tại $21{,}6\text{ Hz}$. Tần số cắt tỷ lệ với tần số lấy mẫu. Nhân với $16/48$ đưa ba điểm tới $1{,}2333\text{ Hz}$, $3{,}4667\text{ Hz}$ và $7{,}2000\text{ Hz}$. Đến khoảng $7\text{ Hz}$, bộ lọc số của micro đã trở lại còn một phần mười decibel.

Phần tử MEMS tự nó ở $-3\text{ dB}$ tại $60\text{ Hz}$, và bộ lọc số nằm chồng lên góc âm học ấy. Giữa khoảng $7\text{ Hz}$ và cao độ $85\text{ Hz}$, từ dữ liệu vẫn mang tiếng ù, tiếng chạm, và phần lệch một chiều mà bộ lọc $1{,}2333\text{ Hz}$ chưa quên.

---

### Một biquad, đặt dưới cao độ

Tầng mục này thêm vào là một biquad thông cao (bộ lọc bậc hai, hai cực hai không), đúng dạng trong sổ tay hệ số của Robert Bristow-Johnson. Tần số cắt $60\text{ Hz}$. Hệ số phẩm chất là Butterworth $Q = 1/\sqrt{2}$, lab in $0{,}707107$, để dải thông không nhô đỉnh. Bản ghi ngày 20 tháng 10 năm 2026 chạy một bộ lọc kiểu sổ tay, cắt gần $60\text{ Hz}$, bằng số thực trên ESP32, trước mọi phép phân tích phổ. Bản ghi ấy không chốt $Q$. Giá trị ở đây là lựa chọn của mục này.

> **Công thức.** $\omega_0 = 2\pi f_c/f_s$, $\alpha = \sin\omega_0/(2Q)$, rồi
> $b_0 = (1+\cos\omega_0)/2$, $b_1 = -(1+\cos\omega_0)$, $b_2 = b_0$, $a_0 = 1+\alpha$, $a_1 = -2\cos\omega_0$, $a_2 = 1-\alpha$.
> Sau khi chia cho $a_0$: $y[n] = b_0 x[n] + z_1$, rồi cập nhật hai ô nhớ $z_1$, $z_2$.
>
> **Các biến.** $x[n]$ là từ vào, $y[n]$ là mẫu ra. $f_c = 60\text{ Hz}$, $f_s = 16.000\text{ Hz}$. $z_1$ và $z_2$ bắt đầu bằng 0.
>
> **Ý nghĩa.** Hệ số trạng thái dừng tại $0\text{ Hz}$ bằng 0 vì ba hệ số $b$ cộng lại bằng 0. Ở mẫu đầu, $y[0] = b_0 x[0]$ với $b_0 = 0{,}983477$. Bước đơn vị ló ra gần nguyên vẹn, rồi mới tắt khi hai ô nhớ đầy.
>
> **Giá trên silicon.** Năm phép nhân, bốn phép cộng, hai từ nhớ, mỗi mẫu. Ở $16\text{ kHz}$ đó là $80.000$ phép nhân mỗi giây. Chu kỳ mẫu $62{,}5\,\mu\text{s}$ là thời gian vòng lặp có để xong, vì $y[n]$ phụ thuộc mẫu trước. Vòng lặp chạy trên từ thô, trước khung 400 mẫu.
>
> **Điều công thức không nói.** Nó không loại tiếng ồn sống cùng dải nguyên âm, và không thay cửa sổ của Mục 1.2. $Q$ lớn hơn sẽ nhô đỉnh và rung lâu hơn.

| Hệ số | Giá trị |
| --- | --- |
| $b_0$ | $0{,}983477$ |
| $b_1$ | $-1{,}966954$ |
| $b_2$ | $0{,}983477$ |
| $a_1$ | $-1{,}966681$ |
| $a_2$ | $0{,}967227$ |

| Tần số | Vai trò | Hệ số |
| --- | --- | --- |
| $20\text{ Hz}$ | tiếng ù, dưới cao độ | $-19{,}14\text{ dB}$ |
| $40\text{ Hz}$ | vẫn dưới cao độ | $-7{,}83\text{ dB}$ |
| $60\text{ Hz}$ | tần số cắt | $-3{,}01\text{ dB}$ |
| $80\text{ Hz}$ | sát dưới cao độ thấp nhất | $-1{,}19\text{ dB}$ |
| $85\text{ Hz}$ | cao độ thấp nhất Mục 1.2 giữ | $-0{,}96\text{ dB}$ |
| $300\text{ Hz}$ | cộng hưởng nguyên âm đầu | $-0{,}01\text{ dB}$ |

Nhát cắt sâu nằm ở $20\text{ Hz}$ và $40\text{ Hz}$. Tại $80\text{ Hz}$ đáp ứng chỉ hạ $1{,}19\text{ dB}$. Cao độ $85\text{ Hz}$ mất $0{,}96\text{ dB}$. Cộng hưởng $300\text{ Hz}$ còn $-0{,}01\text{ dB}$.

![Hình 1.1.5b. Biên độ tính được và sóng dựng sẵn. Lab vẽ hình này.](fig_1_1_5_response.pdf)

**Hình 1.1.5a** đặt hai cổng trước bộ đệm vòng của Mục 1.2: bỏ khoảng câm, rồi biquad, rồi mới ghi. **Hình 1.1.5b**, bên trái, là biên độ từ $5\text{ Hz}$ đến $400\text{ Hz}$, nét đứt tại $60$, $85$ và $300\text{ Hz}$. Bên phải là sóng dựng sẵn $x = 0{,}2 + 0{,}3\sin(2\pi\cdot 200\, t)$ và đầu ra $y$. Nét đứt trên panel thời gian là chỉ số lắng. Đây là phép tính trên sóng dựng sẵn.

Trên bước đơn vị, lab giữ đầu ra dưới $1\%$ suốt một bước nhảy 160 mẫu. Mẫu đầu của quãng yên là mẫu $219$, tức $13{,}688\text{ ms}$. 219 mẫu ấy ở ngoài bộ đệm vòng. $219$ là con số của bước đơn vị, không phải thời gian lắng đo trên một lời nói.

Sóng dựng sẵn dài $80\text{ ms}$ có trung bình đầu vào $0{,}2000$ và trung bình đuôi đầu ra $-0{,}0020$. Thành phần $200\text{ Hz}$ trên đuôi đi từ $0{,}2087$ sang $0{,}2096$. Độ lệch sụp. Tông trong dải thông còn lại.

Trong khoảng câm, đầu vào bằng 0 nên hai ô nhớ đứng yên. $13{,}688\text{ ms}$ bắt đầu sau $256\text{ ms}$. Từ xung bit đầu đến lúc thả con trỏ ghi là $4.096 + 219 = 4.315$ mẫu.

---

### Ba ngộ nhận

#### Ngộ nhận A: Bộ lọc của datasheet đã làm việc này

Ở $16\text{ kHz}$, điểm $-3\text{ dB}$ của bộ lọc số trong micro nằm tại $1{,}2333\text{ Hz}$. Biquad của mục này nằm tại $60\text{ Hz}$. Chúng xếp chồng.

#### Ngộ nhận B: Khoảng giữ lúc bật nguồn nằm trong ngân sách mỗi khung

Hạn $10\text{ ms}$ là khoảng cách giữa hai khung sau khi con trỏ đã chạy. Bộ đếm khoảng câm chạy trước con trỏ.

#### Ngộ nhận C: Đưa tần số cắt lên gần $300\text{ Hz}$ sẽ làm đặc trưng sạch hơn

Tần số cắt sát cộng hưởng nguyên âm sẽ nuốt cộng hưởng mà Mục 1.2 cần đo. Lựa chọn $60\text{ Hz}$ để $300\text{ Hz}$ ở $-0{,}01\text{ dB}$.

---

#### Thế lưỡng nan còn mở: tiếng ồn sống cùng nguyên âm

Khoảng câm đã đi và độ lệch đang tắt. Tiếng ồn sống giữa $300\text{ Hz}$ và đỉnh dải tiếng nói vẫn nằm trong mọi mẫu mà bộ đệm vòng sẽ niêm. Mục 1.2 có thể bắt đầu. Tiếng ồn ấy vẫn nằm trong lát sóng.

---

### Các con số lấy từ đâu

| Nguồn | Điều nguồn ấy nói |
| --- | --- |
| Datasheet INMP441, DS-INMP441-00, bản sửa 1.1 | Đầu ra bằng 0 trong $2^{18}$ chu kỳ SCK; $85\text{ ms}$ tại $3{,}072\text{ MHz}$; $f_{\mathrm{SCK}} = 64 \times f_{\mathrm{WS}}$. |
| Cùng datasheet, Bảng 7 và Bảng 1 | Bộ lọc số ở $48\text{ kHz}$: $-3\text{ dB}$ tại $3{,}7\text{ Hz}$, $-0{,}5\text{ dB}$ tại $10{,}4\text{ Hz}$, $-0{,}1\text{ dB}$ tại $21{,}6\text{ Hz}$, tỷ lệ theo tần số lấy mẫu. MEMS ở $-3\text{ dB}$ tại $60\text{ Hz}$. |
| Robert Bristow-Johnson, Audio EQ Cookbook | Công thức hệ số thông cao, trước khi chia cho $a_0$. |
| `results/lab115/20261020T175727Z/stdout.log` và `result.json` | Mọi con số dẫn xuất của mục này, kể cả mẫu $219$ và các mức dB. Cả hai tệp có trong `results/SHA256SUMS`. Hình do `chapter01/lab_1_1_5.py` vẽ. |
