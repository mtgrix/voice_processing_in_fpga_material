# STYLE BRIEF v2: rewriting Chương 0–14 (supersedes STYLE_BRIEF.md where they differ; keep STYLE_BRIEF.md)

Project: a Vietnamese study document on estimating F0 the Praat way (Boersma 1993 AC method) and implementing it on an FPGA (DE10-Standard, Cyclone V 5CSXFC6D6F31C6N, Quartus).
- Main tex: `uoc_luong_f0_praat_fpga_quartus_vi.tex`. Chapters: `chuong/chuong_00..14_*.tex`.
- **DO NOT EDIT** anything in the main tex before `\input{chuong/chuong_00_mo_dau.tex}` (printed pp.1–38 are the old v10 pages and must stay verbatim). Do not touch other groups' chapter files.

Reader: Tú, a Vietnamese computer-engineering student. Write in Vietnamese and keep English technical terms in parentheses at first use.

Required reading before writing:
1. `/workspace/writing_material/audit_phan_moi_2026-11-10.md`, the audit of the current chapters. Section 6 has four model rewrites; imitate them.
2. `/workspace/writing_material/bai-hoc-viet-tai-lieu.md`, the lessons log: principles 1–41 and cases #1–#22. Cases #15–#22 are new and mandatory.
3. `sec_1_3_5_vi_v10.tex`, the quality bar for prose.

## 1. Diagnosis: why the current text fails ("cộc lốc")
The text reads like a telegram or cheat sheet rather than a lesson. Real quotes from the audit:
- tr.81 §3.2: "Đáp ứng tần số gần DC: |H(e^{jω})| tăng gần tuyến tính với ω khi ω nhỏ; hằng thời gian xấp xỉ 1/(1−α) mẫu." This sentence drops the zero, the pole, the unit circle and the time constant with no derivation.
- tr.90 §4.3 opens directly with "Viết k = mM + r … H(z)=Σ z^-r E_r(z^M) … Noble identity". The formula falls from the sky, and it is also WRONG for 2/3.
- tr.92: "RTL thay thế. Khi không gọi IP: systolic MAC + coeff ROM, folding tay nếu N ≤ 32."
- tr.120: "Lệch một chu kỳ gắn F0 khung trước vào khung sau — lỗi thời gian, không phải lỗi toán." The 13÷3 hand table is full of "…".
- tr.114/116/121/153: "Không tồn tại IP ALTDIV_TENT." This is a bare assertion with no context.
- Cost boxes everywhere look like "• MAC mặc định: 1 DSP, accumulator 48-bit, 120960 chu kỳ/khung @ 50 MHz ⇒ 2,42 ms".
- Chains of arrows used as sentences, e.g. "FILL → WINDOW → MAC → PEAK/DIV → VOICE → PACK", "Bước 8: … xóa → parabolic: lệch vài cent".
- Ch.14 is about 20 `\item`s per 1000 words: a pure checklist with "Lý do: …" stubs.

## 2. Core rule: Feynman + first principles, for EVERY section and subsection
1. **Open with the real problem**: a provocative question or a blunt truth ("sự thật phũ"). Say what goes wrong without this block.
2. **Reduce to fundamental facts and build up with no skipped steps.** Never put a formula before the sentence that motivates it. Write a small concrete case explicitly first, then generalise.
3. **Give an everyday analogy AND a tiny "Ví dụ tính tay"** before generalising. Every number must be computed by a Python script that you run and save under `verify/` (for example `verify/v2_chXX_*.py`). Never write a number you did not compute.
4. **Anticipate confusions and answer them explicitly.** Use Tú's real questions (section 4 below).
5. **Only then map to hardware**: the internals of the Intel IP, the RTL, and the cost, each with the reason the choice follows from the earlier reasoning.
6. **Close with a one-sentence summary** ("*Tóm lại:* …").

Prose rules:
- Full flowing Vietnamese sentences. Each idea goes **what → why → hand example → consequence if wrong**.
- Put a bridge sentence before every formula and between topics.
- **Forbidden as prose**: "label: value" lines, arrow chains (→, ⇒, \to, \Rightarrow), bullet stubs, cost boxes made of fragments, a bare "Lý do:".
- Bullets are allowed ONLY for genuine enumerations (a list of pins or files), and every bullet must be a full sentence.
- A cost box must be a paragraph that explains each number and why it fits the budget.
- Expand every abbreviation at first use in each chapter: ALM, LUT, DSP, M10K, MLAB, Fmax, RTF, MAC, CDC, FSM, ROM, BFP, Q-format, Avalon-ST, …
- No "toy" / "đồ chơi". No empty exclamations ("cực kỳ thanh lịch", "sinh tử", "sống còn", "khuôn vàng thước ngọc").
- Every figure needs an "Đọc hình" sentence. Hand examples must be complete, with no "…" in place of numbers.
- One section, one topic. Split stacked topics and add transitions.
- Any section that is still a list of facts is a reject.

## 3. Mandatory per-part rule: Python twin + Verilog HDL at the end of EACH part
Each subsection or step that describes a computation or a hardware block (not once per chapter) must end with:
- **(A) A Python twin block** (lstlisting), explained line by line in prose.
- **(B) A Verilog HDL block**, explained line by line.

If the part uses an Intel IP (Altera PLL, FIR Compiler II, LPM_DIVIDE, LPM_MULT, On-Chip Memory RAM/ROM 2-PORT, FFT IP, DCFIFO, DSP block modes):
- The HDL must be a **self-written equivalent that matches the IP bit-exactly and cycle-accurately**: latency, rounding, saturation, data ordering and valid timing.
- The prose must explain **why it matches**, for example:
  - LPM_PIPELINE = L means L register stages, so valid is delayed by L;
  - LPM_DIVIDE truncates toward zero, and the remainder carries the sign of the numerator;
  - the FIR Compiler II output rounding mode (truncation or round-half-up) determines the shift and the +half;
  - M10K "Old Data" in read-during-write gives a registered read, which shows up as the extra cycle;
  - DCFIFO showahead versus normal mode;
  - the 18×19 DSP pre-adder needs one extra bit.
- **Show the IP instantiation** (megafunction or IP Catalog wrapper) next to it for comparison.
- Exception: the analog part of the PLL (VCO) has no HDL equivalent. Say so and explain why, then give HDL for what can be modelled: the clock dividers, a behavioural PLL model for simulation, and the lock/reset sequencing.

The twin must be bit-exact with the HDL:
- **iverilog 12 is installed** (`iverilog`, `vvp`).
- For every HDL block, write a small testbench under `tb/v2/` and a Python script under `verify/` that runs the twin on the same vectors and compares the outputs bit for bit, cycle by cycle.
- Run it, and state in the text what was verified ("đã chạy iverilog: N vector khớp 100%").
- Keep any existing `rtl/*.v` working. New RTL files go in `rtl/v2/`.

A part missing either block, or missing the "why it matches the IP" explanation, is a reject.

## 4. Tú's real questions: each must be answered where it belongs
- **Zero padding** (Ch.0 Feynman 4; Ch.1 §1.1/Bước 1; Ch.7):
  - It adds no information and does not reduce leakage; it only samples the same DTFT more densely (Δf = fs/M).
  - What attenuates energy near Nyquist is the mask G[k] or a low-pass filter. Never say zero padding "dọn mép Nyquist"; rename §1.1.
  - For a linear autocorrelation, N_FFT ≥ L + τmax = 854, so 1024 is enough. It is NOT "pad at least L zeros / 2048".
- **24k→16k** (Ch.0 Feynman 9; Ch.4): use the approved explanation (case #16) in this order:
  1. Blunt truth: you cannot "pick 2 of 3".
  2. Timeline: 41.67 µs vs 62.5 µs, the grids coinciding every 125 µs.
  3. Dropping samples gives jitter.
  4. ↑2 to the 48 kHz grid → LPF at 8 kHz (sinc interpolation, which also removes 8–12 kHz) → ↓3, keeping M0, M3, …
  5. The polyphase shortcut.
  6. A one-line summary.
- **Bài tập 0.1b** (tr.47): say plainly that it is a hypothetical "what-if" (16 kHz is the last rate). Then cover both fronts:
  - frequency: a Hanning window only pushes sidelobes to about −32 dB, it does not remove them;
  - autocorrelation: 7 kHz has a period of about 2.29 samples and ripples across τ = 26–214.
  - Conclusion: the FIR filter before framing is mandatory.
- **Folding** (Ch.4 §4.2):
  - x[n] is NOT symmetric; h[k] is (a windowed sinc is an even function, and symmetry gives linear phase).
  - Hand example: h = [1,2,2,1], x = [3,4,5,6] gives 27 both ways with half the multiplies.
  - The DSP pre-adder computes (a + d), which needs one extra bit.
- **Polyphase 2/3** (Ch.4 §4.3, Hình 25, §4.3b, §4.4, Bài 4.2):
  - Start from the waste in the naive method. y16[m] = Σ h[k] x_up[3m−k] uses only taps k ≡ m (mod 2).
  - So E0 = even taps and E1 = odd taps (L = 2 phases), used alternately: about N/2 multiplies per output, i.e. 3 vs 18 for N = 6, a 6× / ~83% saving (NOT 66%).
  - The mod-3 "E0/E1/E2, E2 không xuất" story is WRONG. Remove it and redraw Hình 25.
  - The twin `decimate_2_over_3` that keeps i mod 3 ∈ {0,1} is WRONG; replace it with ↑2 → filter → ↓3, or with the even/odd polyphase form.
- **Half-band** (§4.3b): split into three bridged pieces:
  1. h[n] = sin(πn/2)/(πn), so every even tap except the centre is 0;
  2. the budget: 50 MHz / 16 kHz = 3125 cycles per output;
  3. the MAC count on the even/odd branches.
- **DC-blocker §3.2** (tr.81): answer these six questions IN ORDER, in prose, with figures (unit-circle figure; |H| plot) and hand examples. All the numbers below are already script-verified; re-verify them yourself.
  1. Why does a one-sample delay equal multiplication by z⁻¹? Use the phasor clock hand: x[n] = e^{jωn}, x[n−1] = e^{jωn}·e^{−jω}, z = e^{jω}. Write Euler with correct + signs, e^{jθ} = cosθ + j sinθ. Explain that the magnitude stays 1 and the angles add (ωn − ω).
  2. What H means physically: a gain and a phase for each frequency. Why DC gives H = 0 (x[n] = x[n−1]). Why x[n] − x[n−1] alone also kills 80–200 Hz (at 100 Hz, |H| ≈ 0.039), so a pole is needed.
  3. |H| = (distance to the zero) / (distance to the pole):
     - At z = 1 it is 0/(1−a) = 0.
     - Just off DC it is ≈ 1.
     - At z = −1 it is 2/(1+a) ≈ 1.00196: explain the tiny gain above 1 and the optional normalisation (1+a)/2.
  4. Time constant: aⁿ ≈ e^{−(1−a)n}. After 256 samples, 0.36716 vs 1/e = 0.36788.
  5. fc ≈ (1−a)fs/(2π) ≈ 9.95 Hz at 16 kHz is the −3 dB point. Include a table of |H| at 1, 5, 10, 20, 75, 200 Hz: 0.10003 / 0.44929 / 0.70967 / 0.89678 / 0.99323 / 1.00072, i.e. −20.0 / −6.95 / −2.98 / −0.95 / −0.059 / +0.006 dB.
  6. Unit-circle map: z = 1 is DC, z = −1 is Nyquist (the sequence +1, −1, +1, …). Answer "why not the same at Nyquist?": a zero at −1 and a pole at −a gives H = (1+z⁻¹)/(1+a z⁻¹), a notch at fs/2. The book uses the DC version because its goal is DC removal.
  - Also fix: "Sau khoảng 5·256 mẫu đầu ra tụt dưới 50 LSB" is false (109 LSB at 1280 samples; it first drops below 50 at sample 1480 after the step).
  - Use one α everywhere: α = 1 − 2⁻⁸ = 0.99609375. Fix "z = 0,995" on tr.46.

## 5. Keep ALL existing technical content: expand, do not drop
- Every fact, number, figure, table, listing, exercise and RTL module in the current chapter must survive, re-explained in prose. The only exceptions are items the audit marks as WRONG: fix those, and say in your report what was replaced.
- The reviewer will compare word, figure, table and listing counts before and after. Counts must not decrease, and the word count is expected to grow.
- Do not pad with repetition: the growth must come from derivations, examples, explanations and twin+HDL blocks.

## 6. Correctness fixes (from the audit; apply in your chapters)
- **A6, MAC count.** The real count is Σ(640−τ) for τ = 26..214, which is 98 280. 189 × 640 = 120 960 is only an upper bound.
  - Define this once (Ch.7) and use it consistently. Ch.0, 1, 11, 13 and 14 currently say 120 960 as if it were exact, and Bài 0.2 says "mỗi giá trị trễ tích lũy L = 640".
  - RTF = 98 280 / 500 000 ≈ 0.197.
- **A7, M10K geometry.** 640×16 does NOT fit one M10K: the widest ×16 configuration is 512×16 (512×20), so it takes 2 blocks.
  - Fix every "vừa khít 1 M10K" and the "4 M10K" budget in Ch.0.
  - Or present the alternatives (half-table window ROM of 320 words, which fits in 1 block).
  - Say "kiểm tra bằng báo cáo Fitter".
- **A8, silence threshold.** Ch.1 §1.10 uses a hard energy gate (Rx[0]/Eref, θ² = 0.0009), but Praat uses the amplitude ratio localPeak/globalPeak as a soft cost in the unvoiced candidate. Align Ch.1 with Ch.10. If an FPGA hard gate is kept, call it a deliberate approximation and give the reason.
- **A9, missing C[τ].** Forgetting C[τ] biases the result toward SMALL τ (high pitch), not toward large τ / octave down. Fix Ch.14 (p.152 item 6, p.154–155).
- **A10, Hanning form.** Praat uses N+1 with a full 640-word table. Remove "dạng cổ điển N−1, nửa bảng" from Ch.14.
- **A11.** Octave cost in Praat is SUBTRACTIVE (−octaveCost·log2(ceiling/F0)). If Ch.8 folds it into a multiplicative ROM factor, call that an approximation and say where it holds.
- **A12.** 189 × 16 = 3024 cycles does NOT "phá RTF" (it is 0.6% of 500 000). Give the real reason for not dividing per τ.
- **A13, Ch.10 median-3.**
  - The current twin `median3_stream` gives [0,200,210,200,205] while the RTL gives [0,0,0,200,200] for {200,210,80,205,208}. Make the twin and the RTL bit-exact and cycle-exact, and verify with iverilog.
  - Fix the latency statement: the current RTL output is 2 hops after the centre frame. Either say so, or change the RTL.
  - Use one consistent ALM figure (currently 22–28 / 25 / <200 / 60–100).
- **A5, Ch.1 Nyquist example.** x = [1,0,−1,0,…] is fs/4 (bin 2), not Nyquist, and G[2] = 1. Use [1,−1,1,−1,…] or a near-Nyquist bin and compute G.
- **A16, DSP budget.** "FIR Compiler II — vài chục khối DSP" (tr.52) conflicts with the 3-DSP total (tr.41). Give one consistent, reasoned number.
- **BFP.** Arithmetic −5 >> 1 = −3, not −2. State the rounding convention.
- **Floor vs round** differ by up to 1 LSB, not 0.5.
- **Wording to delete:**
  - "ALTDIV_TENT": at most one sentence in Ch.9 explaining that this name appears online but no such IP exists, and the divider is LPM_DIVIDE or self-written.
  - Remove "Soft Upsampling / dọn mép Nyquist" wording (A3), and "Tiết kiệm 66%".
- **Figures and listings.** The Hình 9 caption says step 2 is deleted although the text keeps it. The Listing 2 caption is broken.

## 7. Per-chapter findings
Fix all of these. Page numbers are printed pages of the current PDF.
- **Ch.0** (p.40–49):
  - Feynman 4 (tr.43): rewrite per case #15, with no reference to a figure that is not included.
  - Feynman 9 (tr.45): rewrite per case #16, and remove "66%" and "loại bỏ bớt các mẫu thừa".
  - Feynman 10–12 are dense jargon: unpack them and use α = 0.99609375.
  - Bài 0.1b per case #17; Bài 0.2 per A6; the ALM, DSP and M10K budget table per A7/A16.
  - Remove the exclamations "yêu cầu sinh tử", "sống còn", "khuôn vàng thước ngọc".
  - Every Feynman box must end with a one-sentence summary.
- **Ch.1** (p.50–71):
  - §1.1: retitle and fix per A3/A5, and fix the Hình 9 caption.
  - §1.5: split DFT / butterfly / Parseval / BFP into separate parts. Define "depth" in nsampFFT and connect it to N ≥ L + τmax.
  - §1.8: explain Brent. §1.10: per A8.
  - Rewrite the 10-parameter table (tr.69) and the T3 solutions (tr.70–71) as prose.
  - A6 everywhere. Fix the Listing 2 caption.
  - Steps 1–9 need a twin + HDL per step. For Bước 1 (offline FFT), give the Python twin and an HDL that explains what the FPGA does instead (FIR), or why there is no HDL.
- **Ch.2** (p.72–79):
  - Convert the cost boxes and FSM arrow chains to prose.
  - PLL: explain why there is no HDL for the VCO; give HDL for the MCLK/SCLK/LRCK dividers and the reset/lock logic, verified with iverilog against a twin.
  - I²S RX: the full RTL (not commented stubs), plus a DCFIFO-equivalent model (or a 2-FF synchroniser + Gray pointers) with cycle-matched behaviour, compared to the DCFIFO instantiation.
- **Ch.3** (p.80–87):
  - §3.2 per section 4 (six questions); A14; §3.4 split into bridged parts; remove "mô hình toy" (tr.83); "Magnitut" typo.
  - Twin + HDL per part (the existing dc_block_iir.v must be verified with iverilog against the twin).
- **Ch.4** (p.88–94):
  - The 24→16 explanation per case #16. §4.2 folding per case #18. §4.3 polyphase per case #19 (even/odd), and redraw Hình 25. §4.3b per case #20. Fix §4.4 and Bài 4.2.
  - Write a self-written polyphase FIR (even/odd branches, pre-adder folding) matching FIR Compiler II's output (state the coefficient quantisation, the output rounding/truncation, and the latency you model), with the FIR II instantiation shown. Verify it with iverilog against the twin.
  - Convert "Lộ trình thực tế" and the arrow lists to prose.
- **Ch.5** (p.95–100):
  - A7 (M10K geometry). Write the "Latency đọc — điểm dễ lệch khung" bullets as prose.
  - HDL for the circular buffer, with On-Chip RAM 2-PORT Old Data / registered-output equivalence explained; twin + iverilog.
- **Ch.6** (p.101–106): A7 for the 640-word ROM. Exercises 6.1–6.5: give each its own explained answer. Twin + HDL for the window multiply (LPM_MULT/DSP pipeline equivalence: q15_mul rounding).
- **Ch.7** (p.107–111):
  - A4: N ≥ L + τmax = 854 so 1024 is enough; remove "ít nhất thêm L / 640 số 0, 2048". A6. The BFP convention.
  - "Bit-reverse, zero-pad — hai bẫy" as prose.
  - The full MAC RTL (not a stub) with a 48-bit accumulator; twin + iverilog.
  - FFT IP: state what a self-written equivalent would need, or give a small radix-2 HDL for N = 8/16 that matches the twin.
- **Ch.8** (p.112–117):
  - A11, A12. Remove the "ALTDIV_TENT" lines (C2). Bài 8.3 (floor vs round, 1 LSB).
  - Rewrite the LPM table as prose. ROM HDL plus twin. LPM_DIVIDE-equivalent HDL if division is used here.
- **Ch.9** (p.118–123):
  - Rewrite the tr.120 line on latency using audit model rewrite 6.3, and complete the 13÷3 example (no "…").
  - Explain Golden Mode B (why 65536, why +half), and say what "Mode A" is.
  - A self-written non-restoring/restoring divider matching LPM_DIVIDE bit-exactly (truncation, remainder sign) and cycle-exactly (LPM_PIPELINE = L); show the LPM_DIVIDE instantiation; twin + iverilog.
  - Parabolic peak HDL + twin.
- **Ch.10** (p.124–130): A13. Explain "timeStepCorrection" (tr.127). Write the Viterbi "Vì sao fabric tắt" stubs as prose. Twin + HDL per part (voicing compare, median-3).
- **Ch.11** (p.131–137): write the FSM role bullets (tr.133) as prose; A6 (tr.133). Twin + HDL per part (Avalon-ST handshake, readyLatency).
- **Ch.12** (p.138–144): write steps 1–5 (tr.138) as prose; explain Avalon-MM at first use; twin + HDL per part (Q12.4 rounding, byte packing).
- **Ch.13** (p.145–151):
  - Convert the bullet lists to prose. Rewrite B12 (GPE 20% ≈ 3.2 semitones, and why).
  - Explain X-propagation at first use; A6.
  - Give a real testbench, explained line by line, that actually runs under iverilog.
- **Ch.14** (p.152–156):
  - Turn every checklist item into a cause-and-effect paragraph (what goes wrong, why, how to see it, how to fix it), with one hand example where it helps.
  - Fix A9, A10, A6. Rewrite the symptom table rows as sentences.
  - Do NOT touch Phụ lục A or anything after chuong_14.

## 8. Process
- Work in small steps. After each finished section: `git add -A && git commit -m "v2: <chapter> <section>"`. **Do not push.**
- **Compile:** from the package dir, run `xelatex -interaction=nonstopmode -output-directory=/tmp/build_<tag> uoc_luong_f0_praat_fpga_quartus_vi.tex` twice. Fix any errors your chapters cause.
- **Render:** `pdftoppm -r 60` your chapters' pages, then LOOK at each image and check for clipped titles, overflow, broken boxes and leftover shorthand.
- **Final report:**
  - a per-section table: section | Feynman 6 points (y/n each) | twin+HDL (iverilog result) | numbers verified (script) | audit items fixed;
  - word, figure, table and listing counts before and after;
  - remaining honest issues.
