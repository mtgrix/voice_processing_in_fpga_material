# BRIEF v3 — rewrite of the FPGA F0 study document (Chương 0–14 + Phụ lục A), one chapter per run

You are the **implementer**. You write the chapter `.tex`, the verify scripts, the RTL and the testbenches. A reviewer reads your chapter afterwards and rejects it if it breaks this brief. Read this whole file before writing anything.

## 0. Where you work and what you may touch
- Repo: `/workspace/writing_material/uoc_luong_f0_praat_fpga_quartus/`, branch **`v3`** (already checked out). Do not switch branches, do not push, do not rebase.
- Main file: `phan_moi_v3.tex` (preamble + `\IfFileExists{chuong_v3/...}` lines). **Do not edit it.** It already inputs every chapter file name listed in §9; create exactly the file name given for your chapter.
- You may create or edit ONLY: your chapter file under `chuong_v3/`, figure files `chuong_v3/fig_chXX_*.tex`, scripts `verify_v3/chXX_*.py`, RTL `rtl/v3/chXX_*.v`, testbenches `tb/v3/tb_chXX_*.v`, C code `sw_v3/chXX_*.c`, and `verify_v3/Makefile` (add a target `chXX`). Never touch `golden_v2/`, `golden/`, `chuong/`, other chapters' files, or the old main tex.
- Environment that already works: `xelatex` (TeX Live), `iverilog`/`vvp` 12, `pdftoppm`, `gcc` (x86, use it to test the HPS C code), `python3` + numpy + scipy, Praat 7.0.03 at `/workspace/tools/praat7003/praat_barren`. **Quartus, ModelSim and Platform Designer are NOT installed.** Do not run apt, pip install, or change system config.
- Commit after each finished section: `git add -A && git commit -m "v3: chXX <section>"`. Final commit: `git commit -m "v3: chXX done"`.

## 1. Sources of truth, in order of precedence
1. **`/workspace/writing_material/agenda_chot_v2_2026-11-10.md`** — the approved outline. §1 (what Praat really does, with source line numbers), §2 (chapter list), §3 (per-chapter content: your chapter's subsection list is mandatory), §4 (style rules + the sample passage), §5 (errors already corrected — never reintroduce them), §6 (decisions), §7 (golden v2 results).
2. **`golden_v2/`** (read-only): `constants.py`, `frames.py`, `fixed_twin.py` (its docstring is the integer spec of the core), `praat_float_ref.py`, `gen_roms.py`, `rom/`, `out/compare_report.md`, `hdl_check/`. Every number you print must come from these or from a script of yours that imports them. If you find a contradiction between agenda and golden_v2, golden_v2 code wins; write it in your report.
3. This brief.
4. `STYLE_BRIEF_v2.md` in the repo: use ONLY §2 (Feynman + first principles), §3 (twin + HDL per part) and the section "Bổ sung 2026-11-10 tối" (N1–N5). **Its §4, §6 and §7 are OBSOLETE** where they give numbers or decisions: 640-sample window, 98 280 MAC, RTF 0,197, energy silence gate `R0*10000 < 9*E_ref`, multiplicative octave ROM 17070, microphone/WM8731/I²S/PLL, 2/3 resampling in the main flow. Those are all replaced by the agenda v2.
5. Read for style and for the old failings: `/workspace/writing_material/bai-hoc-viet-tai-lieu.md` (principles 1–41, cases #15–#22), `/workspace/writing_material/audit_phan_moi_2026-11-10.md` (§2 and §6 model rewrites). The old chapter `chuong/chuong_00_mo_dau.tex` is the **minimum** narrative level, not the target; the target is the sample passage in §5 below.

## 2. Reader, target, voice
- Reader: anh Tú, a Vietnamese computer-engineering student who will build this on a DE10-Standard (Cyclone V 5CSXFC6D6F31C6N). He knows C and basic Verilog; he does not yet know Praat's internals or Intel IP details.
- The document must let him answer three questions (agenda §1.1): how far the FPGA F0 track is from Praat's on the same WAV (GPE/VDE/FFE/cents) and which block causes each part of the gap; which side is faster and by how much (FPGA cycles, HPS end-to-end, Praat on the laptop, RTF); and for every Praat component, its essence, why Boersma does it, and how to build it on the FPGA in two ways, (A) Intel IP with every parameter explained and what it generates tied to theory, and (B) self-written HDL that matches (A) bit- and cycle-exactly, with the reason it matches.
- Write in Vietnamese. Keep English technical terms (pipeline, latency, throughput, valid/ready, backpressure, readyLatency, chunk, bridge, …), and give the Vietnamese meaning in parentheses at first use in each chapter. Expand every abbreviation at first use in each chapter (HPS, FPGA, ALM, DSP, M10K, MLAB, Fmax, RTF, MAC, FSM, ROM, PIO, DMA, mSGDMA, CSR, GPE, VDE, FFE, Q-format, Avalon-MM, Avalon-ST, …).
- Voice: calm and precise, like a good teacher talking to one student. No hype words ("đập tan huyền thoại", "tuyệt đối 100%", "món hời", "chết người", "vọt lên", "sinh tử", "sống còn", "cực kỳ thanh lịch", "khuôn vàng thước ngọc", "toy", "đồ chơi"). Bold only conclusions, sparingly. Never address the writer or mention this brief, the reviewer, agy, Argon, Gemini, "golden v1/v2 decisions", "anh chốt", or commits in the reader-facing text. The reader sees a textbook, not a project log. (You may say "tài liệu này chọn …", and cite file names of scripts that the reader can run.)

## 3. The writing rules (agenda §4.1 restated; every one is checked)
1. **Open with a real problem.** Each section and subsection starts with a concrete question or a situation that breaks ("sự thật phũ"), never with a definition or an IP name. Say what goes wrong without this block.
2. **The sentence that motivates a formula or number comes before it.** Every formula, bit width and cycle count follows a sentence saying which counting or reasoning produces it. Derive with no skipped steps: write the small concrete case first, then generalise.
3. **Causal sentences, not arrows.** Forbidden as prose: "nhãn: giá trị" lines, `\paragraph{X.}` used as a label followed by a fragment, chains of →/⇒/`\to`/`\Rightarrow` in place of verbs, bullet stubs, bare "Lý do:", cost boxes made of fragments. Bullets are allowed only for genuine enumerations (pins, files, parameters), and each bullet is a full sentence with its "vì sao". A parameter list for an IP is written as one short paragraph per parameter: what it means, the value, why that value, what goes wrong with the other value.
4. **Look through the black box.** Say where the signal goes and in which register it is latched; whether that register exists in the silicon (DSP input register bank, M10K output register) or must be built from ALM flip-flops. Every such statement must be true for Cyclone V (Cyclone V Device Handbook), not borrowed from Arria 10/Stratix.
5. **Anticipate the snag.** Ask the question the reader will ask ("Chỗ dễ vướng: …?") and answer it on the spot with a hand calculation.
6. **Miniature hand calculation.** 3–6 integer samples, walked through cycle by cycle or step by step, every number matching a script. No "…" in place of numbers.
7. **A one-sentence summary at the end of each subsection**, in italics: `\textit{Tóm lại: …}`.
8. **Every number has a source label.** Each number is one of: derived (the computation is shown), checked by script (name the script, e.g. `verify_v3/ch01_frames.py`, or a `golden_v2/` file), or **phải đo** (comes from a Quartus Fitter/Timing Analyzer report or a board measurement; write "(phải đo)" and say which report). Never invent Fmax, ALM counts, DSP counts, nanosecond delays, transfer times or statistics. Every claim "Praat làm X" cites the file and line range (agenda §1.2 lists them).

Narrative floor (from Tú): a result may appear only after the reader has been led to it, in this order: the problem → why the naive approach fails → the derivation step by step with bridge sentences → a hand example → the number. The reviewer samples paragraphs at random and rejects the chapter if they are a term plus a number, a list of facts, or results without a derivation.

## 4. The fixed skeleton of every hardware block (chapters 1–12 and Phụ lục A)
Each block (each subsection that builds hardware) goes through these steps, as flowing prose with headings where useful:
1. **Bản chất** — what the block computes, from first principles, with a hand example.
2. **Vì sao Boersma/Praat làm vậy, bỏ đi thì hỏng gì** — cite `Sound_to_Pitch.cpp` lines; show the failure with numbers.
3. **Các phương án, đánh đổi, ta chọn gì, vì sao (có số)** — at least two real options (e.g. combinational vs registered multiplier; unregistered vs registered M10K output; Old Data vs Don't Care; PIO vs mSGDMA; FIFO depth 512 vs 1024; one-hot vs binary). For each option give latency (cycles), resources (M10K/DSP from geometry; ALM/Fmax as "phải đo"), and the consequence; then the choice with the numbered reasons.
4. **Đường (A): Intel IP** — the exact IP name for Cyclone V; every parameter in the Parameter Editor as a short paragraph (meaning, value, why, link back to theory); what the IP generates (ports with widths, latency it reports, output width/scaling, resources it uses); the instantiation snippet (Verilog) of the generated wrapper or megafunction. Since Quartus is not installed, say which facts come from the IP user guide (name the guide) and which must be checked in the generated simulation model (mark "phải kiểm trong mô phỏng IP").
5. **Đường (B): HDL tự viết** — complete synthesizable Verilog-2001 (no stubs, no commented-out bodies), explained line by line in prose after the listing; then a paragraph "Vì sao khớp IP" mapping each register stage / rounding / flag to the IP parameter that produces the same behaviour; then "Đổi lựa chọn thì sao": which RTL change moves Fmax, latency and resources, and in which direction.
6. **Twin Python + testbench iverilog** — the twin listing (bit-exact, clocked in the same order as the RTL when timing matters), explained line by line; the testbench compares RTL and twin bit for bit and cycle for cycle on **≥ 200 vectors** (more is better; include edge cases and random backpressure where there is a handshake). State the result in the text exactly as measured: "đã chạy iverilog: N vector, khớp N/N" plus the script/testbench names.
7. **Bảng IP so với HDL** — resources (M10K/DSP derived, ALM/Fmax "phải đo"), latency, throughput, flexibility, what is easier to debug.

When no sensible IP exists (median-3, voicing compare, FSM, WAV parser on HPS) say so and explain why only HDL/software is used.

## 5. Quality bar: the sample passage (agenda §4.3). Your prose must be at least this explanatory.
> Đoạn này là chuẩn văn phong cho cả tài liệu. RTL và twin bên dưới em đã chạy bằng iverilog: 3.040 kết quả R[τ], 0 lỗi, 98.543 chu kỳ/khung với cửa sổ 638 mẫu và toán hạng 17 bit (thư mục `golden_v2/hdl_check/`; bản 640 mẫu, 16 bit của v1 nằm ở `agenda_verify/`).

**Một dòng code, bao nhiêu việc?** Trong C, `acc += x[n]*x[n+tau]` trông như một việc. Trên FPGA, đó là một quãng đường điện. Địa chỉ đi vào bộ nhớ M10K. Hai mẫu đi ra, chạy qua dây nối tới bộ nhân 17×17. Tích 34 bit đi tiếp qua bộ cộng rồi dừng ở thanh ghi tổng. Đồng hồ 50 MHz cho mỗi nhịp 20 ns. Nếu cả quãng đường đó phải xong trong một nhịp, thì tốc độ của cả mạch bị quyết định bởi quãng dài nhất ấy. Người ta gọi nó là đường tới hạn.

**Thứ không thể bỏ.** Trước khi so phương án, cần thấy một điều: phép cộng dồn bắt buộc phải có thanh ghi. Tổng của nhịp này là đầu vào của nhịp sau, nên phải có chỗ giữ nó qua cạnh đồng hồ. Vì vậy không có "MAC tổ hợp thuần". Câu hỏi thật là: có chặt quãng đường phía trước bộ cộng thành nhiều chặng hay không.

**Ba phương án.**

- *Phương án 1: không chốt toán hạng.* Dữ liệu từ M10K đi thẳng vào bộ nhân, rồi tới bộ cộng, rồi tới thanh ghi tổng. Từ lúc phát địa chỉ tới lúc tổng cập nhật mất 2 nhịp: 1 nhịp đọc RAM, 1 nhịp nhân-cộng. Đường tới hạn gồm thời gian ra của M10K, dây nối từ khối RAM tới khối DSP (dài ngắn tùy cách Fitter đặt), phép nhân và phép cộng.
- *Phương án 2: chốt toán hạng ở cửa khối DSP.* Thêm một tầng thanh ghi ở cửa khối DSP. Cyclone V có sẵn input register bank ở đó, nên tầng này không tốn ALM. Quãng đường tách làm hai: RAM → thanh ghi vào, và thanh ghi vào → nhân → cộng → thanh ghi tổng. Đổi lại, latency tăng thêm 1 nhịp, thành 3.
- *Phương án 3: chốt thêm cả tích.* Thêm một thanh ghi giữa bộ nhân và bộ cộng. Khối DSP Cyclone V không có thanh ghi ở vị trí này (Arria 10 mới có), nên Quartus phải lấy khoảng 32 FF từ ALM, hoặc tách phép tính ra khỏi khối. Ở 50 MHz ta không cần chặng này.

**Chỗ dễ vướng: latency có làm chậm 98.540 phép tính không?** Không, vì latency và throughput là hai chuyện khác nhau. Hãy nghĩ tới một băng chuyền: món đầu tiên mất 3 nhịp mới tới cuối. Nhưng từ đó trở đi, mỗi nhịp có một món ra. Ta phát 98.540 cặp địa chỉ liền nhau, gồm 638 cặp cho R[0] và 97.902 cặp cho τ = 26..214. Kết quả cuối ra sau cặp cuối 3 nhịp, nên tổng là 98.543 chu kỳ. Ở phương án 1 tổng là 98.542. Một nhịp chênh trên 98.543 là 0,001%.

Còn chỗ chuyển giữa hai lag thì sao? Cờ `sload` đi kèm cặp đầu tiên của lag mới và bảo bộ tích lũy *nạp* tích thay vì *cộng* tích. Nhờ vậy không cần nhịp nào để xóa thanh ghi về 0. Cái giá là phải đọc kết quả đúng nhịp: tổng của lag cũ chỉ đứng trên thanh ghi đúng một nhịp trước khi bị nạp đè. Vì thế cờ `last` cũng phải đi qua cùng số tầng với dữ liệu, rồi bật `out_valid` đúng nhịp đó.

**Tính tay.** Lấy xw = [2, −3, 4, 1]. Ta tính R[1] = 2·(−3) + (−3)·4 + 4·1 = −14 và R[2] = 2·4 + (−3)·1 = 5. Hai lag phát liền nhau, không nhịp nghỉ:

| Nhịp | Địa chỉ phát (sload, last) | RAM trả ra | Thanh ghi vào a_r, b_r (sload_r) | Tích p | acc | out_valid |
|---|---|---|---|---|---|---|
| 0 | (0,1) (1,0) | – | – | – | – | 0 |
| 1 | (1,2) (0,0) | 2, −3 | – | – | – | 0 |
| 2 | (2,3) (0,1) | −3, 4 | 2, −3 (1) | −6 | – | 0 |
| 3 | (0,2) (1,0) | 4, 1 | −3, 4 (0) | −12 | −6 | 0 |
| 4 | (1,3) (0,1) | 2, 4 | 4, 1 (0) | 4 | −18 | 0 |
| 5 | – | −3, 1 | 2, 4 (1) | 8 | **−14** | **1** |
| 6 | – | – | −3, 1 (0) | −3 | 8 | 0 |
| 7 | – | – | – | – | **5** | **1** |

Ở nhịp 5, acc = −14 và out_valid = 1: đó là R[1]. Ngay nhịp sau, acc bị nạp đè thành 8, là tích đầu của lag 2. Ở nhịp 7 ta có R[2] = 5.

**Ta chọn gì, và vì sao.** Ta chọn phương án 2. Có bốn lý do:

1. Thanh ghi vào có sẵn trong khối DSP, nên không tốn ALM.
2. Một nhịp latency thêm chỉ tốn 0,001% thời gian.
3. Đường tới hạn không còn phụ thuộc chuyện Fitter đặt M10K xa hay gần khối DSP.
4. Cấu hình này khớp đúng một cấu hình IP sinh ra được.

Ta bỏ phương án 3 vì ở 50 MHz nó không đem lại gì mà lại tốn FF ở ALM. Fmax thực của phương án 1 và 2 là **(phải đo)**: chương này đặt bảng Timing Analyzer của cả hai cạnh nhau.

**Đường (A): ALTERA_MULT_ADD.** Mỗi tham số trả lời một câu hỏi ở trên:

- NUMBER_OF_MULTIPLIERS = 1: ta chỉ có một cặp mỗi nhịp.
- WIDTH_A = WIDTH_B = 17 và REPRESENTATION signed: xw có dấu, và sau khi trừ trung bình có thể vượt 16 bit. Nếu chọn unsigned, −3 thành 131.069.
- WIDTH_RESULT = 48: cần 43 bit, và bộ cộng cứng rộng 64 bit nên lấy rộng hơn không tốn gì.
- INPUT_REGISTER_A0/B0 = CLOCK0: đây là phương án 2.
- MULTIPLIER_REGISTER0 = UNREGISTERED: ta bỏ phương án 3.
- ACCUMULATOR = YES, ACCUM_SLOAD_REGISTER = CLOCK0: sinh cổng `accum_sload`, được chốt cùng toán hạng.
- OUTPUT_REGISTER = CLOCK0: đây là thanh ghi tổng.

Latency IP báo phải là 2 nhịp tính từ cổng vào. Cộng 1 nhịp đọc RAM là 3, khớp bảng trên. Số DSP và ALM lấy từ Fitter.

**Đường (B): HDL khớp IP.**

```verilog
module mac_dsp_unit (
    input  wire clk, in_valid, in_sload, in_last,
    input  wire signed [16:0] a, b,          // xw[n], xw[n+tau], 17 bit
    output reg  signed [47:0] acc,           // R[tau] đang cộng dồn
    output reg  out_valid                    // 1 đúng nhịp acc là R[tau] hoàn chỉnh
);
    reg signed [16:0] a_r, b_r;              // tầng 1 = input register bank
    reg v_r, sload_r, last_r;                // cờ đi cùng dữ liệu, cùng số tầng
    always @(posedge clk) begin
        a_r <= a;  b_r <= b;
        v_r <= in_valid;  sload_r <= in_sload;  last_r <= in_last;
    end
    wire signed [33:0] p = a_r * b_r;         // nhân tổ hợp trong khối DSP
    always @(posedge clk) begin               // tầng 2 = thanh ghi tổng (output register)
        if (v_r) acc <= sload_r ? {{14{p[33]}}, p} : acc + {{14{p[33]}}, p};
        out_valid <= v_r & last_r;
    end
endmodule
```

Vì sao khớp IP:

- Hai khối `always` ứng với đúng hai tầng thanh ghi mà IP bật: input register và output register.
- `sload_r` và `last_r` đi cùng tầng với `a_r` và `b_r`, giống ACCUM_SLOAD_REGISTER = CLOCK0.
- Mở rộng dấu tường minh giữ đúng giá trị âm khi cộng vào 48 bit.

Nếu xóa tầng `a_r`/`b_r` (phương án 1), latency giảm 1 nhịp, nhưng Quartus không còn thanh ghi để đặt vào input register bank.

**Twin Python** chạy theo đúng thứ tự cạnh đồng hồ:

```python
class MacTwin:
    def __init__(self):
        self.a_r = self.b_r = self.v_r = self.sload_r = self.last_r = 0
        self.acc, self.out_valid = 0, 0
    def clock(self, in_valid, in_sload, in_last, a, b):
        if self.v_r:                                   # tầng 2 đọc giá trị CŨ của tầng 1
            p = self.a_r * self.b_r
            self.acc = p if self.sload_r else self.acc + p
            self.acc = ((self.acc + (1 << 47)) % (1 << 48)) - (1 << 47)
        self.out_valid = self.v_r & self.last_r
        self.a_r, self.b_r = a, b                      # rồi tầng 1 mới chốt đầu vào mới
        self.v_r, self.sload_r, self.last_r = in_valid, in_sload, in_last
        return self.acc, self.out_valid
```

**Kiểm chứng.** Testbench gồm M10K mô hình đọc 1 nhịp và bộ phát địa chỉ liền mạch, chạy 16 khung 638 mẫu: 14 khung lấy từ file thử có ồn, và 2 khung stress full-scale với |xw| tới 59.379, vượt 16 bit. Kết quả: 3.040 giá trị R[τ] khớp twin 100%, mỗi khung 98.543 chu kỳ. Bảng tính tay ở trên chính là log của testbench `agenda_verify/tb_trace.v`.

*Tóm lại: tích lũy thì luôn cần một thanh ghi. Ta thêm đúng một tầng nữa ở cửa khối DSP vì nó có sẵn trong silicon, chỉ tốn 1 nhịp trên 98.543, và khớp đúng cấu hình ALTERA_MULT_ADD.*

## 6. One before/after example (what "cộc lốc" means and what we want instead)

**Before** (old Ch.11, a real quote; this style is rejected):

> \paragraph{\texttt{readyLatency}.} Tài liệu Avalon Interface Specifications (doc ID 683091) cho phép sink báo \texttt{ready} trước 0 hoặc 1 chu kỳ. Lab này dùng \texttt{readyLatency}=0: quyết định nhận nằm cùng chu kỳ với \texttt{valid}. Nếu nối IP FIR/FFT cấu hình latency 1 mà FSM của bạn giả định 0, beat đầu/cuối burst sẽ lệch --- đọc UG trước khi nối.
>
> Thiếu \texttt{EOP} $\Rightarrow$ FSM treo ở \texttt{FILL}; thừa \texttt{EOP} $\Rightarrow$ cắt khung sớm.

Why it fails: it opens with a label; "báo ready trước 0 hoặc 1 chu kỳ" is never explained (before what?); "beat đầu/cuối burst sẽ lệch" gives no mechanism and no example; the arrows replace the causal verbs; there is no hand trace, no number, no summary.

**After** (the level we want):

> Giả sử khối nhận hạ \texttt{ready} xuống 0 ở chu kỳ 5 vì bộ đệm của nó vừa đầy. Câu hỏi là: mẫu mà khối gửi đặt lên bus \emph{ở chính chu kỳ 5} có được nhận hay không? Câu trả lời phụ thuộc vào một con số mà hai bên phải thống nhất trước, gọi là \texttt{readyLatency} (độ trễ của tín hiệu sẵn sàng).
>
> Với \texttt{readyLatency} = 0, luật rất đơn giản: một mẫu được nhận ở chu kỳ $n$ khi và chỉ khi \texttt{valid} và \texttt{ready} cùng bằng 1 ở chính chu kỳ $n$. Ở chu kỳ 5, \texttt{ready} = 0, nên mẫu đang nằm trên bus không được nhận, và khối gửi phải giữ nguyên nó sang chu kỳ 6. Với \texttt{readyLatency} = 1, \texttt{ready} ở chu kỳ $n$ là lời hứa cho chu kỳ $n+1$: khối nhận nói "nhịp sau tôi còn chỗ". Khi đó \texttt{ready} = 0 ở chu kỳ 5 nghĩa là chu kỳ 6 không được gửi, còn mẫu ở chu kỳ 5 thì vẫn được nhận, vì lời hứa cho chu kỳ 5 đã được đưa ra ở chu kỳ 4.
>
> Hãy đi qua sáu nhịp với dãy mẫu 10, 11, 12, 13 và \texttt{ready} = 1, 1, 0, 1, 1, 1 ở các chu kỳ 3 đến 8. Nếu cả hai bên hiểu \texttt{readyLatency} = 0, khối nhận nhận 10 ở chu kỳ 3, 11 ở chu kỳ 4, bỏ qua chu kỳ 5, rồi nhận 12 ở chu kỳ 6 và 13 ở chu kỳ 7: đủ bốn mẫu, đúng thứ tự. Nếu khối gửi hiểu \texttt{readyLatency} = 1 trong khi khối nhận hiểu 0, khối gửi thấy \texttt{ready} = 0 ở chu kỳ 5 và chỉ dừng ở chu kỳ 6. Nó đã đặt 12 lên bus ở chu kỳ 5 và coi như đã gửi xong, nhưng khối nhận không lấy. Mẫu 12 mất, và khung 638 mẫu từ đó lệch đi một mẫu. Mọi giá trị $R[\tau]$ sau đó vẫn được tính đúng công thức, nhưng trên một khung sai, nên F0 sai mà không có cảnh báo nào.
>
> Vì thế, trước khi nối với một IP, phải đọc giá trị \texttt{readyLatency} trong báo cáo của IP đó và viết khối gửi theo đúng giá trị ấy. Testbench cũng phải đếm số mẫu nhận được, không chỉ xem dạng sóng.
>
> \textit{Tóm lại: \texttt{readyLatency} cho biết \texttt{ready} nói về nhịp này hay nhịp sau; hiểu lệch một nhịp là mất hoặc lặp đúng một mẫu, và lỗi đó im lặng.}

(The numbers in that trace are illustrative; in your chapter every trace must be produced by your twin/testbench and must match the log.)

## 7. Canonical numbers (all from golden_v2; do not use any other value)
fs = 16 kHz. Pitch floor 75 Hz, ceiling 600 Hz, time step 0 (auto) = 0,75/75 = 10 ms = **hop 160**. Window 3/75 = 40 ms, rounded by Praat to **638 samples** (floor(640) → half = 319 → 638; `Sound_to_Pitch.cpp` lines 335–339). Hanning Praat form `w[i] = 0.5 − 0.5·cos(2πi/(N+1))`, i = 1..N, N = 638; ROM Q1.15, saturated 32767 at the top; w[0] = w[637] = 1, w[318] = w[319] = 32767, sum 10 469 378. Local mean over **426 samples** (positions 106..531 of the 638-sample window, 0-based); mean = floor((S + 213)/426), implemented as `(((S + 213 + 426·2^15)·10 082 083) >> 32) − 2^15`. d = x − mean is **17-bit signed**; xw = (d·w + 2^14) >> 15, 17-bit signed; stress frame |xw| = 59 379. LP = max|xw[j]|, j = 212..425. globalPeak GP = round(max|n·x − Σx|/n) on the HPS. Lags: scan **τ = 26..214** (189 lags), search **27..213**; maximumLag = floor(638/3)+2 = 214; minimumLag = floor(16000/600) = 26; brent_ixmax = 319. MAC count **Σ(638 − τ) = 97 902** for τ = 26..214, **98 540** with R[0]; iverilog measured **98 543 cycles/frame** (98 540 issue + 3 latency, `golden_v2/hdl_check/`). At 50 MHz: 3125 cycles per 16 kHz sample, **500 000 cycles per hop**; core RTF ≈ 98 543/500 000 ≈ 0,197 for the MAC alone and ≈ 0,199 for the whole core (≈ 99 700 cycles, estimate; Ch.12). MAC operands 17×17 signed, accumulator 43 bits needed, 48 bits used (Cyclone V DSP accumulator is 64 bits). Normalisation sh = max(0, bitlen(R0) − 26). C[τ] Q2.14 = round(2^14·R_w(0)/R_w(τ)) from the quantised window: C[26] = 16 563, C[27] = 16 578, C[100] = 19 260, C[213] = 34 773, C[214] = 35 030. K[τ] = round(2^20·0,01·log2(600τ/16000)): K[26] = −383, K[27] = 188, K[100] = 19 995, K[213] = 31 434, K[214] = 31 504. **Octave cost is subtractive, no divider**: U = (Rn·C + 2^13) >> 14, Sc = U − ((R0n·K + 2^19) >> 20). Voicing: voiced iff (100·Sc − 45·R0n)·3·GP > 100·R0n·max(0, 6·GP − 145·LP). F0 one division: F0_Q12.4 = round(512 000·den/(2·den·τ_p + num)); example y = (8000, 10000, 9000) at τ_p = 100 gives δ = +1/6, F0 = 159,73 Hz, Q12.4 = 2556. Median-3 replaces the path finder; **no Viterbi on the FPGA**. FIR Nyquist-edge 31 taps, **bypass by default** when comparing with Praat (Praat 6.4.12/7.0.03 code does NOT do the 1993 soft-upsampling step); when on, shift the frame grid by 15 samples. DC-blocker optional, α = 1 − 2^−8 = 0,99609375, off when comparing. Transfer: **PIO over the lightweight HPS-to-FPGA bridge into an On-Chip FIFO** is the main path; mSGDMA is the compared alternative. Data rate 16 000 × 2 B = 32 KB/s; packed 2 samples per 32-bit word = 8 000 writes per second of audio. FIFO depth 512×16 = 1 M10K (M10K = 10 240 bits, widest ×16 shape 512×20); 1024×16 = 2 M10K. Chip: 41 910 ALM, 166 036 registers, 553–557 M10K (take the Fitter value), 112 DSP. Praat reference **7.0.03**, `To Pitch (raw autocorrelation)...`, **10 parameters**; **R1** = defaults (octave-jump 0,35, V/UV 0,14), **R2** = same but octave-jump = V/UV = 0 (path finder reduces to per-frame argmax = apples-to-apples with the FPGA before median). Golden results on the synthetic files: see `golden_v2/out/compare_report.md` and agenda §7 (twin vs R2 clean: VDE 0, GPE 0/208, mean 0,21 cent, p95 0,48, max 1,08; noisy 5 dB: GPE 3/207, R1−R2 differ on 19/207 frames, median-3 GPE vs truth 22 → 15). Synthetic files: 2,8 s, 277 frames, t1 = 0,020 s, first window starts at sample 1 (0-based), hop exactly 160, GP = 22 946 (clean) / 22 937 (noisy). Tú's real WAV set is not available yet: say the chapter's numbers are on the synthetic files and that `golden_v2/compare.py` reruns them on real files.

If you need a number not in this list, compute it with a script under `verify_v3/` that imports `golden_v2` modules, and cite the script.

## 8. LaTeX conventions
- Chapter head exactly like this (keeps the TOC and bookmarks working):
  `\clearpage\phantomsection\section*{Chương N. Title}\addcontentsline{toc}{section}{Chương N. Title}`
  Subsections: `\subsection*{N.k. Title}\addcontentsline{toc}{subsection}{N.k. Title}`. Sub-subsections without TOC entries are fine.
- Start the chapter with the `learningobj` box (full sentences). Use the existing boxes from the preamble when they help (`firstprin`, `feynmanbox`, `thoughtqa`, `equationcard`, `verifygate`, `costbox`, `physicalinsight`), but a box never replaces the prose; a `costbox` is a paragraph.
- Listings: `\begin{lstlisting}[language=Verilog, caption={...}]`, `[language=Python, ...]`, `[language=C, ...]`. Keep listings ≤ ~60 lines each; split long code and explain each piece after it. Explain line by line in prose (refer to line numbers or identifiers).
- Figures: TikZ (inline or `\input{chuong_v3/fig_chXX_name.tex}`), always followed by a paragraph starting "\textbf{Đọc hình.}" that walks through each visible element. Tables: booktabs, with a caption; a table never stands without a paragraph that reads it.
- Vietnamese number style in prose: decimal comma (0,197), thin-space or dot thousands as in the agenda ("97.902" or "97\,902", be consistent within the chapter). In code and file names use normal ASCII.
- Underscores in text must be escaped (`\texttt{golden\_v2/fixed\_twin.py}`); check every `\texttt` with `_`. Tables must have the right column count.

## 9. File names per chapter
Ch.0 `chuong_v3/chuong_00_bai_toan.tex`; Ch.1 `chuong_v3/chuong_01_wav_hps_cau.tex`; Ch.2 `chuong_v3/chuong_02_avalon_st_fsm.tex`; Ch.3 `chuong_03_fir_nyquist.tex`; Ch.4 `chuong_04_khung_ram_vong.tex`; Ch.5 `chuong_05_tru_trung_binh.tex`; Ch.6 `chuong_06_hanning.tex`; Ch.7 `chuong_07_mac.tex`; Ch.8 `chuong_08_chuan_hoa_octave.tex`; Ch.9 `chuong_09_dinh_parabol_chia.tex`; Ch.10 `chuong_10_voicing.tex`; Ch.11 `chuong_11_median3.tex`; Ch.12 `chuong_12_tich_hop.tex`; Ch.13 `chuong_13_kiem_chung.tex`; Ch.14 `chuong_14_checklist.tex`; Phụ lục A `phu_luc_a_resample.tex`.

## 10. Verification you must run and save
- Every number in your chapter that is not in §7 is computed by `verify_v3/chXX_*.py` (import `sys.path.insert(0, '../golden_v2')` or the absolute path). The script prints each number with a label; keep the printed log in `verify_v3/chXX_*.log`.
- Every HDL block: `rtl/v3/chXX_*.v` + `tb/v3/tb_chXX_*.v` + a Python script that generates the vectors with the twin, runs `iverilog -g2005-sv`/`-g2005` + `vvp`, and compares outputs bit for bit (and cycle for cycle where timing matters). ≥ 200 vectors per block. Save the log. Add a `verify_v3/Makefile` target `chXX` that reruns everything for your chapter.
- Every HPS C program: compile with `gcc -Wall -Wextra -O2` on the box and compare its output with the Python twin on the golden WAV files plus crafted edge-case WAVs (save them under `verify_v3/data/`, small).
- Hand-calculation tables in the text must be copied from the logs, not retyped from memory.

## 11. Compile and look
- `cd` to the repo, then run twice: `xelatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp/build_v3_chXX phan_moi_v3.tex`. Zero errors. Fix every Overfull \hbox > 10 pt in your chapter.
- Render your pages: `pdftoppm -r 70 -f A -l B -png /tmp/build_v3_chXX/phan_moi_v3.pdf /tmp/build_v3_chXX/p`, then LOOK at every page image: overlapping labels in figures, clipped tables, listing overflow, missing Vietnamese glyphs (tofu boxes), "??" references, leftover shorthand.

## 12. Final report (print it at the end of your run, also save as `verify_v3/chXX_REPORT.md`)
1. A per-subsection table: subsection | opens with a real problem (y/n) | hand example (y/n, script) | options+trade-off+choice with numbers (y/n) | IP path (y/n) | HDL path (y/n) | twin + iverilog (N/N) | summary sentence (y/n).
2. Pages, words (`texcount` or `wc -w` on the .tex), figures, tables, listings.
3. Every number you could not verify and why; every "phải đo" item.
4. Honest remaining weaknesses.
5. Commit hashes.

## 13. Chapter-specific instructions (in addition to agenda §3 for that chapter)

### Ch.0 — Bài toán, mục tiêu so sánh, và Praat thật sự làm gì (`chuong_00_bai_toan.tex`)
Follow agenda §3 Ch.0 (0.1–0.7) and use agenda §1.2–§1.4 as the content of 0.3. This chapter sets the tone for everything; it must read like the first lecture of a good course.
- 0.1 opens with the situation "một file WAV, hai câu trả lời". Show the two naive methods failing with numbers you compute: (a) zero-crossing counting on a signal with a strong 2nd harmonic (build a 3–4 period example and count crossings); (b) FFT peak picking: bin spacing 16000/640 = 25 Hz (or 16000/638 ≈ 25,08 Hz; say which N and why), half a bin at 100 Hz = 12,5 Hz ≈ 204 cent (verify). Then motivate autocorrelation from "a periodic signal looks like itself shifted by one period", with a tiny integer example.
- 0.2: R_xw(τ) ≈ R_x(τ)·R_w(τ), so divide by R_w. Hand example: a pure sine through an 8-sample Hanning (Praat N+1 form), r before and after dividing; numbers from a script. Explain why the approximation holds (fast oscillation inside a slowly varying arch; principle 20/21 in the lessons file).
- 0.3: the eight steps of Praat exactly as the source code runs (agenda §1.2), each step a short paragraph with what it does, why Boersma does it, and the line range. The 10 parameters as prose (one sentence per parameter, with what it does at fs = 16 kHz) — a table is allowed only in addition to the prose. Then the table "Praat làm / ta làm / vì sao / ảnh hưởng tới phép so" (agenda §1.3) followed by a paragraph that reads it. Mention the 1993 soft-upsampling step and that the code does not do it.
- 0.4: system figure (TikZ): WAV on SD → HPS (parse, GP, frame grid) → lightweight bridge + On-Chip FIFO → FPGA core blocks (Ch.3–Ch.11 order) → FIFO ra → HPS writes `pitch_f0.bin`; laptop runs Praat with the same parameters. "Đọc hình" paragraph. Chapter map: which chapter builds which box.
- 0.5: GPE, VDE, FFE, cent: definitions derived from "what can go wrong in one frame" (four cases: both voiced and close, both voiced and far, voicing differs, both unvoiced). Hand example on 10 invented frames, computed by `verify_v3/ch00_metrics.py`, whose functions must give the same results as `golden_v2/compare.py` metrics on the golden files (check that and say so). Explain why 20 % ≈ 3,16 semitones ≈ 316 cent, and why fine-cent statistics exclude gross errors.
- 0.6: the cycle budget from first principles (50 MHz, 3125 cycles/sample, 500 000/hop), the MAC count Σ(638−τ) derived step by step (show the arithmetic-series sum), 98 540 with R[0], 98 543 measured, RTF. Explain latency vs throughput here briefly (the full treatment is Ch.7). Explain the three timing measurements and RTF definitions, and why Praat's time must be measured inside the script (startup excluded, thread count recorded).
  **HDL for Ch.0:** one small, real block that ties the budget to hardware: an address/pair generator `rtl/v3/ch00_pair_counter.v` that, for parameters (N, τmin, τmax) and including R[0], issues the (n, n+τ) pairs with `sload`/`last` flags exactly as the MAC of Ch.7 will consume them, and counts cycles until done. Twin in Python; testbench over ≥ 200 random (N, τmin, τmax) configurations plus (638, 26, 214) must give count = N + Σ(N−τ) and the same flag sequence as the twin (compare the full sequence for small N, the count and a checksum for large N). Explain the RTL line by line. There is no IP for this (say why).
- 0.7: the twin/verification map: `golden_v2/praat_float_ref.py`, `golden_v2/fixed_twin.py` (walk through its 10-step docstring in prose: this is the spec of the whole core), per-chapter twin + testbench, three-tier verification (twin = RTL bit-exact; RTL = board bit-exact; board vs Praat statistically). Present the golden results table (agenda §7) and read it in prose, honestly including where the twin is weak (noisy file: parabolic vs sinc70+Brent up to ~33 cent; grid ranking 3/207; median-3 cannot replace the path finder).
- Exercises at the end (3–5), each with a full explained answer.

### Ch.1 — WAV trên HPS và cầu HPS–FPGA, chiều đi và chiều về (`chuong_01_wav_hps_cau.tex`)
Follow agenda §3 Ch.1 (1.1–1.7). Blocks: (i) WAV reading on the HPS, (ii) globalPeak + Praat frame grid on the HPS, (iii) the transfer path choice, (iv) the input FIFO (IP vs HDL) with the Avalon-MM slave side, (v) the return path FIFO, (vi) the register map and the C driver.
- 1.2 WAV: explain RIFF chunk structure from the bytes up with a hex dump of a real small file (produce it); why offset 44 is wrong (LIST chunk example you craft); checks (fmt tag 1, channels 1, 16 kHz, 16 bit, block align 2, data size even); odd-sized chunk padding. C parser `sw_v3/ch01_wav.c` + Python twin; test on the two golden WAVs and ≥ 4 crafted edge cases (LIST chunk, odd chunk size with pad byte, wrong rate, stereo, truncated data). There is no FPGA IP for this: say so.
- globalPeak: derive why Praat uses max|x − mean of whole file| (amplitude, for the silence gate in Ch.10), and why the integer form GP = round(max|n·x − Σx| / n) avoids floating point and equals Praat's value after scaling (show the scaling between int16 and Praat's [−1, 1) floats and verify on the golden files: 22 946 / 22 937).
- Frame grid: derive `Sampled_shortTermAnalysis` step by step (nframes, t1 centred), then `Sampled_xToLowIndex`, leftSample, window start = rightSample − 319 − 1 (0-based); hand example for a 1,234 s file and the 2,8 s golden file (t1 = 0,020 s, first window start 1, hop 160). Explain the odd-sample-count floor trap and how the HPS code guards it (compute in double exactly like `golden_v2/frames.py`, check every hop). C implementation + comparison with `frames.py` on ≥ 200 random file lengths (both parities).
- 1.3 options with numbers: PIO over lightweight bridge vs mSGDMA vs HPS-to-FPGA (full) bridge; 32 KB/s; 8 000 writes per audio second when packing 2 samples per word; pessimistic 1 µs/write bound gives transfer RTF ≈ 0,008 (derived); the real write time is "phải đo" (say how: `clock_gettime` around N writes). mSGDMA needs physically contiguous buffers, cache coherency handling, descriptors — explain each in plain words. Choice: PIO main, mSGDMA as compared alternative.
- 1.4 IP path: `altera_avalon_fifo` (On-Chip FIFO Memory) — every parameter as a paragraph (depth 512 and why it is 1 M10K and holds > 3 hops; single clock; input type Avalon-MM write, output Avalon-ST source; bits per symbol 16 / symbols per beat 2 or the 32-bit MM side and how a 32-bit word splits into two samples — be careful and explicit about byte/sample order (little-endian; which sample is first); backpressure; status interface for input (fill level)); what it generates (slaves `in`, `in_csr`, source `out`, the CSR registers fill_level / i_status / event / interrupt enable / almostfull / almostempty — check against the Embedded Peripherals IP User Guide and say which you rely on); latency from write to `valid` is "phải kiểm trong mô phỏng IP". mSGDMA parameters as listed in agenda §1.4 (paragraph each). Return path: FIFO ST-sink → MM-read for F0 words.
- 1.5 HDL path: your own Avalon-MM write slave + synchronous FIFO (power-of-two depth, pointers with one extra wrap bit to distinguish full/empty, inferred M10K with registered read), Avalon-ST source side with valid/ready, a fill-level CSR, `waitrequest` behaviour when full (explain why we choose to assert waitrequest vs drop data vs flag overflow, with trade-offs), 32-bit word unpacking into two 16-bit samples. Say precisely which behaviours you model from the IP guide and which are your own choices.
- 1.6 register map: separate slaves fifo_in (data), fifo_in_csr, ctrl, fifo_out; ctrl fields: start, n_frames, first window start, GP (16 bit), FIR bypass flag, DC-blocker enable, frame_cycles, total_cycles, status (busy/done/overflow). Give a table AND a paragraph per register explaining why it exists and who writes/reads it. Base addresses are your proposal; say they are set in Platform Designer.
- 1.7 C driver for the HPS (`mmap` on /dev/mem of the lightweight bridge window 0xFF200000, span 2 MB): open, map, write loop with fill-level polling, start, poll done, read F0 FIFO, write `pitch_f0.bin` (uint16 LE Q12.4) + meta file (t1, dt, n_frames). It cannot run on the box against hardware: make it compile with gcc (`-DSIM` mode where the register accesses go to a Python-generated trace or a mock), and keep the real path behind `#ifndef SIM`. Python twin of the bus (a cycle model of your FIFO) and the iverilog testbench with ≥ 200 write transactions and random backpressure on the ST side; check no sample lost, none duplicated, order preserved, fill level correct each cycle.

### Ch.2 — Avalon-ST, ngân sách chu kỳ khi đầu vào là file, mã hóa FSM (`chuong_02_avalon_st_fsm.tex`)
Follow agenda §3 Ch.2 (2.1–2.5). valid/ready and readyLatency 0 vs 1 with a measured trace (see §6 above for the level). File-driven budget: no 16 kHz clock imposes the pace; MAC is the bottleneck (~98,5 k cycles per 160 new samples ≈ 616 cycles/sample); 3125 cycles/sample is only the real-time yardstick. FSM encoding: Quartus "State Machine Processing" options (Auto, One-Hot, Minimal Bits, Gray, Johnson, User-Encoded) — explain each with a 4–5 state example, FF count vs decode logic; 166 036 registers so one-hot is cheap; choose Auto with a template Quartus recognises and read the State Machine report (phải đo). Gray code: why n ^ (n >> 1) changes one bit per increment (proof by the trailing-ones argument). Skid buffer: when needed, 2-cycle hand trace, full RTL + twin + ≥ 200 vectors with random stalls (no loss, no duplication). Also a small FSM in two encodings (binary and one-hot, same behaviour) verified equal by iverilog.
