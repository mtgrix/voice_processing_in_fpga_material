# Rewrite brief (shared by all chapter writers)

Project: Vietnamese study document on estimating F0 (pitch) the Praat way (Boersma 1993) and implementing it on FPGA (DE10-Standard, Cyclone V 5CSXFC6D6F31C6N, Quartus Standard/Lite).
Package: /workspace/writing_material/uoc_luong_f0_praat_fpga_quartus/ ; main tex uoc_luong_f0_praat_fpga_quartus_vi.tex (DO NOT EDIT lines before \input{chuong/chuong_00...}; pp.1-38 = old v10 content that must stay verbatim). New chapters: chuong/chuong_00..14_*.tex.

Reader: Tú, Vietnamese computer-engineering student. He is furious: the current chapters read like an appendix / cheat sheet. His spot checks found: unexplained terms (sidelobe, BRAM, RTF...), formulas that jump steps (R_{x+A}[0] without first writing R[tau]=sum x_n x_{n+tau}), wrong numbers (Hanning example, R[2]), clipped headings, the silly literal phrase "đồ chơi". He says every unread section is likely just as bad.

QUALITY BAR = the old v10 pages. Read sec_1_3_5_vi_v10.tex (in package) or /workspace/ce226/txt/sec_1_3_5_vi_v10.txt first and imitate: full flowing Vietnamese paragraphs that lead from a real phenomenon to the formula; English technical terms kept in parentheses; every symbol defined before use; no forward references.

For EVERY section (each Praat step / each hardware block):
1. Hiện tượng thật (physics / intuition): what physically happens, with a picture (TikZ/pgfplots figure where it helps) and everyday analogy, then say plainly what the term means in reality vs only in calculation.
2. Toán từng bước: start from the base definition, derive each line, no skipped steps; define each symbol.
3. Ví dụ tính tay: small numbers, every intermediate value shown; EVERY number verified by a Python snippet you run (keep scripts in /workspace/writing_material/verify/). Never write a number you did not compute.
4. Ý nghĩa phần cứng: how the Intel IP does it internally (only real IPs/parameters: Altera PLL, FIR Compiler II, On-Chip Memory RAM/ROM 2-PORT, LPM_MULT, LPM_DIVIDE, FFT IP, DSP blocks, DCFIFO, Avalon-ST). ALTDIV_TENT does NOT exist; M10K has no "New Data" mixed-port mode on Cyclone V (Old Data / Don't Care). Then the self-written RTL alternative, with Verilog explained line by line.
5. Twin Python bit-exact, explained.
6. Chi phí: every abbreviation expanded and explained at first use (ALM, LUT, DSP, M10K/BRAM, MLAB, Fmax, latency, RTF = real-time factor = processing time / audio time) and WHY the design choice fits, with computed budget numbers (e.g. 640x16 bit = 10240 bit = 1 M10K; 10 ms hop at 50 MHz = 500000 cycles).
7. Bài tập + lời giải giải thích (not one-word answers).

Rules: replace telegraphic bullets/arrows ("⇒", "—") used as prose with sentences. No "đồ chơi"/"toy" (use "Ví dụ tính tay"). No padding or copy-paste repetition: depth, not length for its own sake. Headings: \section/\subsection titles must render fully (no clipped first letters; check tcolorbox titles fit). Each chapter starts on new page with "Chương N. <title>".

Compile check: do NOT compile in the package dir concurrently with other writers. Copy needed to test: run `xelatex -interaction=nonstopmode -output-directory=/tmp/build_<yourtag> uoc_luong_f0_praat_fpga_quartus_vi.tex` from the package dir (twice), fix any errors YOUR chapters cause, then pdftoppm -r 60 every page of your chapters and LOOK at each image (Read tool) for clipped titles, overflow, broken boxes, leftover shorthand. Edit ONLY your assigned chuong files (and new figure files named with your chapter prefix).

Report: per-section table (section | terms explained | numbers verified by script | figure | prose), word counts before/after, remaining honest issues.
