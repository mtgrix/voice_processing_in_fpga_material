# Audio Preprocessing in Hardware: I2S, Frame Buffering and the STFT

> *Objective: Design and synthesize dedicated hardware IP cores for fixed-point FFT/STFT and Mel Filterbank extraction directly connected to digital microphone interfaces.*

---

## The same reduction, rebuilt as something you would have to wire

Chapter 1 took a stream of numbers down to eighty of them -- frame, fade, transform, squash onto the
Mel scale, take the logarithm -- and did it as software calling functions, where the only cost worth
naming was arithmetic. This chapter does that identical reduction again, but as hardware somebody has
to place on a chip and route with real wires, and the moment the steps become circuits the questions
change completely. Not "how many multiply-accumulates does a frame need," which chapter 1 already
answered, but "how wide is the bus into the multiplier, how deep is the buffer that holds a frame
between two stages, and what happens on the cycle the data does not arrive." A step that was one line of
Python is now a block with an input, an output, a clock, and a place to store what it is mid-way through.

The chapter follows the signal from the microphone inward. It starts at the boundary, because the FPGA
board has no microphone of its own and the first real decision is how audio gets into the fabric at all
-- a serial link a codec drives, or a stream of single-bit pulses that has to be counted down to a
usable rate -- and it argues for pulling that ingestion *inside* the design rather than handing it off
to a processor, which is the move that keeps the whole front end flowing instead of stopping to be
serviced. From there it builds the fixed-point transform engine, the part that decides how many bits
each intermediate is allowed and where the rounding error is permitted to land, then the Mel
multiplication and the logarithm, which a chip cannot compute exactly and has to approximate out of
tables and shifts.

Read it as chapter 1's mirror. Every quantity chapter 1 derived -- the frame length, the hop, the
transform size, the band count -- is a *parameter* here, and this chapter is where those parameters turn
into wires, memory, and latency. It is also the first place the book confronts a trade that recurs for
the rest of it: fixed-point arithmetic is cheaper in every currency a board cares about, and it is
wrong in a bounded way that has to be measured, not assumed. That wrongness is the subject of chapter 7,
which this chapter sets up without answering.

---

> ### Minimal Mathematics / Prerequisites for this Chapter
>
> - **A serial stream and its rate**: a hardware front end is fed by wires that carry one sample or one
>   bit per clock; how many of them arrive per second is what the rest of the design is scaled against.
> - **Decimation and the two clock domains**: dividing a stream's rate means keeping a filter on the
>   fast side and its partner on the slow side, and the reason a CIC can be cheap is that the two sides
>   do not need to run at the same rate.
> - **Powers of two**: a radix-two transform wants a length that is a power of two, because each stage
>   halves the work and the stages are a logarithm, not a count.
> - **A dot product as a row of multiply-accumulates**: a matrix column is a sum of products, and on
>   fabric that sum is a row of cells each fusing a multiply with an add.
> - **Fixed point as width and place**: a fixed-point number is an integer with a stated position of
>   the point, and every width choice moves where rounding error lands.
> - **A logarithm as an address into a table**: the one function a chip cannot compute cheaply exactly
>   is turned into a lookup plus a short interpolation.

---

<!-- source: 6.1 draft fragment -->

## 6.1 Direct Audio Ingestion: I2S Interfaces and PDM Decimation Filtering

*Where this sits in the chain: the* **Air and microphone** *stage, at its weakest point -- the board
this book targets has no microphone until one is fitted, and the first hardware decision is which of
two serial links carries sound into the fabric.*

**Intuition.** The KV260 has no audio input of its own; chapter 8 prices the codec route and the
connector it plugs into, and this section keeps that choice rather than relitigating it. What chapter 6
owns is the front end behind it: the design has to turn whatever the boundary delivers, a codec's framed
samples or a microphone's single-bit stream, into 16 kHz PCM samples that the frame buffer of section 6.2
can accept. The two links look different to a hardware designer. A codec samples the analogue
signal itself and shifts out complete samples over a companion serial link, so the fabric's job is
framing and aligning, not filtering. A pulse-density-modulation (PDM) microphone is a one-bit
sigma-delta modulator inside the capsule: it emits a single bit per clock, and the density of ones
carries the signal, so the fabric's job is to *filter and count that stream down* to a usable rate, and
that counting is real arithmetic, done at the fastest clock in the design.

**Mechanism.** The codec path first. The board's own audio module is a line-level stereo converter
(`V-03-03`) on a PMOD header (`V-03-02`); it samples the line-level signal and serialises each sample
over the companion link (I2S -- Inter-IC Sound), which carries a bit clock, a word clock and a data
wire. The fabric receives serialised samples at the sample rate the corpus fixes: both corpora chapter 1
reads store speech at 16 kHz (`V-05-10`, corroborated by `V-05-11`), so the ingest expects one 16 kHz
sample per frame period and nothing faster. The blocker is clocking, not arithmetic: the codec's bit
clock comes from the PMOD's own oscillator domain, and a design that crosses a clock boundary without a
synchroniser reads metastable values, so the I2S receiver's job is to sample the data wire into the
fabric's clock domain safely and then hand complete words to the frame buffer. By the numbering of
chapter 4, this is a stream handshake at its simplest: a valid pulse per sample.

**The PDM path is the one that needs a filter.** A PDM microphone does not hand out samples at all; it
handles a constant stream of single bits, oversampled by a large factor. Inside the packet is a
one-bit sigma-delta modulated representation of the audio: the density of ones tracks the signal level,
and the noise shaped by the modulator sits at high frequencies, above the band the front end keeps.
Turning that stream into 16 kHz PCM means *decimating* it: low-pass filtering the stream so the
out-of-band noise is gone, then keeping one output sample per decimation factor. Do that naively -- a
long finite-impulse-response (FIR) filter at the fast clock, multiplying every tap on every bit -- and
the front end's fastest clock is also its most expensive arithmetic, which is backwards. The classic
answer is a cascade-integrator-comb (CIC) filter, Eugene Hogenauer's 1981 contribution (`V-06-18`),
which does the low-passing with adders and registers alone: no multipliers at all. [Figure 25](#fig-ch6-pdm-cic)
draws the structure, and it is small enough to read as a recipe.

::: {#fig-ch6-pdm-cic .figure}
```tikz
% The PDM path beside the I2S path, ending at the frame buffer. The PDM side is the
% interesting one: integrators running at the fast clock, then the rate change, then
% combs at the slow clock, which is the whole trick of the CIC.
\begin{tikzpicture}[
  node distance=6mm,
  blk/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
              text width=15mm, minimum height=12mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[blk] (mic) {PDM mic\\ one bit};
\node[blk, right=of mic] (int) {integrator\\ x3};
\node[blk, right=of int] (dec) {divide\\ by 64};
\node[blk, right=of dec] (cmb) {comb\\ x3};
\node[blk, right=of cmb] (pcm) {16 kHz\\ PCM};
\draw[arr] (mic) -- (int);
\draw[arr] (int) -- (dec);
\draw[arr] (dec) -- (cmb);
\draw[arr] (cmb) -- (pcm);
\node[lbl, below=1pt of mic.south] {fast clock};
\node[lbl, below=1pt of int.south] {fast clock};
\node[lbl, below=1pt of dec.south] {rate change};
\node[lbl, below=1pt of cmb.south] {slow clock};
\node[lbl, below=1pt of pcm.south] {slow clock};
\end{tikzpicture}
```
The PDM side of the boundary. The three integrators run at the fast clock and the three
combs at the slow one; the rate change between the two clocks is where the stream slows, and the filter has
no multipliers anywhere, which is the point of putting it on the fast clock.
:::

**The CIC filter is two halves that run at two different rates.** *Mechanism.* Hogenauer's structure is
a cascade of $N$ integrators followed by a rate change followed by $N$ combs, where an integrator is
$y[n] = y[n-1] + x[n]$, an accumulator -- one adder and one register -- and a comb is $y[n] = x[n] - x[n-D]$,
a difference across a delay of $D$ samples. Because the combs sit after the rate change, their
$D$ samples of delay live *between consecutive output samples*, not consecutive input bits, so the
comb's registers tick at the slow clock while the integrators tick at the fast one. That split is what
makes the filter cheap: both halves are adders, and the cost of the filter is a handful of
accumulators and registers.

> **The formula.**
> $$H(z) = \left(\frac{1 - z^{-DM}}{1 - z^{-1}}\right)^{N}$$
>
> **The variables.**
> - $H(z)$ -- the transfer function of the whole decimating filter, from fast-clock input to slow-clock
>   output, in the z-transform.
> - $M$ -- the decimation ratio: how many input bits one output sample averages. An integer ratio of
>   rates, chosen by the design.
> - $D$ -- the differential delay of each comb, almost always $1$: how many samples apart the comb
>   subtracts. A count of samples, a design parameter.
> - $N$ -- the number of integrator-comb stages. A count of stages, chosen by the design.
> - $z^{-1}$ -- the unit delay operator; the numerator is the combs and the denominator is the
>   integrators, and each letter of the formula is one of the boxes already drawn.
>
> **What it means.** The numerator is a set of $N$ combs and the denominator is a set of $N$
> integrators, so the expression is literally the cascade drawn above, written as algebra. The
> denominator's $(1 - z^{-1})$ is an accumulator, making the filter's fast half; the numerator's
> $(1 - z^{-DM})$ is the difference, making the slow half; and the ratio of the two is a
> low-pass filter whose passband widens as $N$ grows. Because $M$ and $D$ only ever enter multiplied as
> a pair, doubling the decimation ratio doubles the comb's delay and changes the shape not at all.
>
> **What it costs.** No multipliers. Each integrator is one adder and one register, each comb one
> subtractor and one delay, so the whole filter is a few accumulate cells running at the fast clock and
> a few difference cells at the slow one. The price is internal word growth: every stage adds bits to
> the accumulator, and the next card bounds that growth.
>
> **What it does not say.** It does not say the passband is flat or sharp -- a CIC is a very long,
> gentle filter, and the passband droops toward the band edge, which is why designs flatten it with a
> short compensation filter at the end. It does not fix $M$, $D$ or $N$: those are decisions, the
> trinity that sets where the noise band lands. And it says nothing about the one-bit input; the same
> filter can decimate any word width, and the interface above is drawn with one-bit values for the PDM
> case rather than by necessity.

**Register growth is the CIC's only arithmetic, and it is bounded.** *Mechanism.* Every integrator
accumulates, and an unpadded accumulator would wrap. Hogenauer's growth rule puts an exact bound on how
wide the internal words must be for the output to be exactly the decimated signal, and it is the
single most useful quantity in this section.

> **The formula.**
> $$B_{\text{out}} = B_{\text{in}} + N \lceil \log_{2}(DM) \rceil$$
>
> **The variables.**
> - $B_{\text{out}}$ -- the width of the widest accumulator inside the filter, in bits. A number of
>   bits, a design quantity.
> - $B_{\text{in}}$ -- the width of the input stream, in bits: $1$ for a PDM microphone's single-bit
>   line, whatever the codec path's converter yields otherwise.
> - $N$, $D$, $M$ -- the same three parameters as the previous card, unchanged.
> - $\log_{2}(DM)$ -- the base-two logarithm of the product $DM$; the amount each stage can grow a
>   peak signal.
> - $\lceil\ \rceil$ -- the ceiling, rounding up to an integer number of bits.
>
> **What it means.** The worst-case gain a signal can accumulate while crossing $N$ stages of a filter
> whose decimating product is $DM$ is $(DM)^{N}$, and $(DM)^{N}$ demands $\log_{2}((DM)^{N}) = N \log_{2}(DM)$
> bits beyond the input. The ceiling makes that a whole number of bits. With the design's choices this
> section uses -- a single-bit input, $N = 3$ stages and $M = 64$ -- the width comes out to
> $1 + 3 \cdot 6 = 19$ bits, computed as the formula states, and that is the width the accumulator and
> the internal buses are drawn at, with the output optionally rounded back down.
>
> **What it costs.** One bit of width per stage per halving of the decimating product, which is cheap on
> fabric: nineteen bits is a handful of registers per cell, and the whole PDM filter's register bill is
> a fraction of one block of the on-chip memory this book counts in chapter 1 (`V-01-22` gives the
> board's total). What it *buys* is the guarantee that the pipelined filter's output is exact in
> fixed-point terms until the final rounding, which is the strongest honest statement a fixed-point
> front end can make about its own arithmetic.
>
> **What it does not say.** It does not say the nineteen bits are all significant -- the growth bounds
> the accumulator against overflow, it does not measure the noise in the signal itself, which the
> one-bit modulator puts there deliberately. It does not say where the final rounding happens, or that
> the codec path needs the same rule: a codec already emits finished samples, so a CIC is not used on
> that side at all. And it does not say the growth number is a registered measurement of this design; it
> is a derived arithmetic quantity, stated for the reader to check against the formula above.

**The width is visible in the code, and it is the whole interface.** The growth bound is not a
number to believe: it is a line of RTL, and the line is where a learner sees that the register
width is *computed*, not chosen. One integrator stage, in the width the card above derives:

```systemverilog
module cic_integrator
#(parameter int N_STAGES = 3,   // integrator-comb pairs
  parameter int DECIM    = 64,  // decimation ratio M
  parameter int DIN_W    = 1)   // one-bit PDM input
 (input  logic                  clk,
  input  logic                  rst_n,
  input  logic signed [DIN_W-1:0] din,
  output logic signed [B_MAX-1:0]  dout);

  // Hogenauer growth bound, as a localparam: the synthesiser sizes the register.
  localparam int B_MAX = DIN_W + N_STAGES*$ceil($log2(DECIM));

  logic signed [B_MAX-1:0] acc;   // y[n-1]

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)  acc <= '0;
    else         acc <= acc + din;   // y[n] = y[n-1] + x[n]
  end
  assign dout = acc;
endmodule
```

Two things to read out of it. The `localparam` is the formula from the card, so the register width
and the bound cannot drift apart in an edit: change `DECIM` and the accumulator widens by itself, which
is the difference between a derived width and a magic number. And the add is an ordinary `+` on signed
operands of that width, which is the whole cost claim of the section in one line -- an integrator is
one adder and one register, and the comb that follows it is a subtractor and a delay, so there is no
multiplier anywhere in this filter. The width `B_MAX` evaluates to the nineteen bits the card derived
for the section's choices, and the one-bit input is widened to it by the signed extension the port
already declares, not by padding logic the designer must remember to add.

**Application.** The section's whole case is the two paths beside each other. The I2S path hands the
frame buffer complete 16 kHz samples as they arrive, with no arithmetic of its own, only clock-domain
care. The PDM path must decimate, and the CIC does it with adders, with a width that is derived,
bounded, and cheap. Both paths end in the same place: a stream of 16 kHz PCM samples that section 6.2
assembles into windows, and the section that follows treats the ingest as settled.

**What this section does not yet know.** It has fixed the sample rate at 16 kHz and the filtering
structure, but it has not decided the *frame* -- how many of those 16 kHz samples one transform reads,
how often a new one starts, and how a fixed-point input width behaves through an FFT. Those are the
questions the next section turns into buffers, and the wrongness fixed point introduces is left for
chapter 7 to measure, exactly as the chapter opening promised.

> **Stop and check.** A CIC integrator runs at the fast clock, on every single input bit, forever; the
> comb runs at the slow clock. Why is that arrangement correct, and what would be wrong about running a
> plain FIR decimating filter at the fast clock instead?
>
> **Answer.** The integrators must see every input bit, because each output sample is a function of a
> whole block of them, so they belong before the rate change and run at the fast clock. The combs
> subtract values $D$ sample-periods apart *at the output rate*, so they belong after the rate change
> and run at the slow clock; that is exactly the split the formula's two factors draw. A plain FIR at
> the fast clock would be mathematically the same kind of filter but would multiply a tap weight on
> every one of the fast clock's bits, which is where the multiplier bill comes from. The CIC's trick is
> that both halves are adders, and the rate split is why it stays cheap.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-03-02` | the board's audio path is a PMOD module in an accessory header, so the design's boundary is a plug, not a chip |
| `V-03-03` | that module is a line-level stereo converter, whose samples arrive framed on the serial link |
| `V-05-10` | the LibriSpeech corpus stores 16 kHz speech, fixing the rate the ingest must deliver |
| `V-05-11` | Speech Commands stores 16 kHz single-channel PCM, corroborating the same rate |
| `V-06-18` | a CIC decimator (Hogenauer, 1981) is the registered low-pass structure for the PDM path |
| `V-01-22` | the board's on-chip memory total, against which this section's register bill is a fraction |

## 6.2 Line_Buffer_1D: Framing 400 Samples with a 160-Sample Hop

*Where this sits in the chain: the first buffer inside the fabric -- the samples are arriving as a
stream, and the transform of section 6.3 wants a whole window at once.*

**Intuition.** A streaming front end is two things disagreeing about time. The ingest delivers one
sample after another, forever; the transform reads a *frame*, a fixed block of consecutive samples, and
it wants a new frame more often than one frame-length apart, so consecutive frames overlap. The buffer
between them is a line buffer: a shift register (or a small circular memory) that holds the overlap and
emits one finished window per hop. Nothing in it is arithmetic. It is addressing -- which samples are
kept, which are dropped, and where the zeros go -- and the discipline is that every parameter the
buffer uses is the *same* parameter the model was trained with, because a front end whose window
differs from training by one sample is a different front end.

**Mechanism.** The frame spine chapter 1 fixed is the contract. Each frame reads 400 consecutive
samples, a window of 0.025 s at the ingest rate (`V-06-13`, `V-06-15`); a new frame starts every 160
samples, a stride of 0.01 s (`V-05-31`, `V-06-16`); the transform reads 512 points (`V-06-14`,
`V-06-17`). The buffer's behaviour follows from those three numbers with no further choices. It
retains the newest 400 samples, emits them as a window, advances 160, and repeats -- so each window
shares 240 of its samples with its predecessor, computed as the difference the frame and hop imply.
The transform size exceeds the window, so the last $112$ positions of every 512-point input are filled
with zeros, computed as the padding the two sizes imply; zero-padding interpolates the spectrum, it
does not add information, and the buffer writes the zeros itself so no upstream stage has to know
about them. [Figure 26](#fig-ch6-line-buffer) draws the three quantities as one window sliding over
the stream.

::: {#fig-ch6-line-buffer .figure}
```tikz
% One window, one hop, one zero tail: 400 kept, 160 advanced, 112 padded to 512.
% All arithmetic lives in computed sentences or math; the fence is scan-exempt.
\begin{tikzpicture}[
  node distance=4mm,
  seg/.style={draw, align=center, inner sep=2pt, font=\scriptsize,
              minimum height=9mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[seg, minimum width=44mm] (win) {kept window};
\node[seg, minimum width=14mm, right=of win] (pad) {zero tail};
\node[lbl, below=of win] (wl) {one frame of samples};
\node[lbl, below=of pad] (pl) {padding to transform size};
\draw[arr] ([yshift=6mm]win.north west) -- node[lbl, above] {next frame starts one hop later} ([yshift=6mm]win.north east);
\end{tikzpicture}
```
The buffer's three quantities in one picture. The kept window is one frame of samples, the
advance between consecutive windows is one hop, and the zero tail pads the window out to the
transform size; the prose states each quantity as a computed value.
:::

**The window the transform reads is not the raw samples.** Before the FFT, each frame is multiplied by
a window function -- a Hann window in this design's corpus path -- which fades both ends of the frame
toward zero so the transform does not read the frame's edges as a discontinuity. In hardware that fade
is a table of coefficients and one multiply per sample per frame: the coefficient table is loaded once,
and each emitted sample is scaled as it leaves the buffer. The cost is one multiplier running at the
sample rate, which is negligible beside the transform, and the alternative -- a rectangular window,
which is no multiply at all -- smears every tone across neighbouring bins, which chapter 7 would then
have to explain as error. The buffer emits windowed samples; the transform never sees the raw ones.

**Application.** The section's deliverable is a contract the rest of the chapter can rely on. The buffer
holds one frame, advances one hop, pads to the transform size, applies the fade, and hands section 6.3
a finished 512-point window ten milliseconds after the previous one. Every number in that sentence is
either a registered claim or a computed quantity stated as such, and the buffer itself is the only
place in the front end that knows the frame exists -- downstream stages see windows, never streams.

**What this section does not yet know.** It has not said how the 512 windowed samples become a
spectrum, nor how many bits each of them carries. The transform engine is next, and with it the first
fixed-point decisions of the chapter.

> **Exercise (laddered).** A new frame starts every 160 samples and each frame keeps 400. (a) How many
> samples does one frame share with its predecessor, computed as the difference the two imply? (b) The
> transform reads 512 points. How many trailing zeros does the buffer write per frame, computed as the
> padding the sizes imply? (c) The ingest runs at 16 kHz. How many finished windows does the buffer
> emit per second of audio, and why does that rate, not the sample rate, set the throughput the
> transform of section 6.3 must sustain?
>
> **Answers.** (a) $400 - 160 = 240$ samples shared. (b) $512 - 400 = 112$ zeros. (c) One window per
> hop, so $16000 / 160 = 100$ windows per second of audio, computed as the rate the hop implies; the
> transform must finish one window per hop period, because the buffer emits finished windows at that
> rate and has nowhere to put a backlog.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-10` | the ingest delivers 16 kHz speech, the rate the exercise's window count divides by |
| `V-06-13` | each frame spans a window of 0.025 s, the duration the buffer holds |
| `V-06-15` | that window is 400 samples at the ingest rate |
| `V-05-31` | a new frame starts every 0.01 s, the stride the buffer advances |
| `V-06-16` | that stride is 160 samples |
| `V-06-14` | the transform reads 512 points, the size the buffer pads to |
| `V-06-17` | that size is 512 FFT points as a derived quantity |

<!-- source: 6.3 draft fragment -->

## 6.3 Fixed-Point Radix-2 FFT Hardware Engines: the R2SDF Microarchitecture

*Where this sits in the chain: the transform -- 512 windowed samples in, a spectrum out, one finished
window per hop period.*

**Intuition.** The fast Fourier transform is an algorithm for computing a discrete Fourier transform in
$N \log N$ operations instead of $N^{2}$, and on fabric the question is not the operation count but the
*shape*: how the butterflies are laid out in space and time, where the twiddle factors (the complex
roots of unity each butterfly multiplies by) are stored, and how many bits wide every intermediate is.
This section's engine is a radix-$2$ single-path delay-feedback (R2SDF) pipeline after He and Torkelson
(`V-06-19`): one butterfly per stage, stages chained in series, samples streaming through without ever
stopping. The alternative the section title names -- radix-$4$, which does four samples per butterfly --
is kept as a comparison, because its trade against radix-$2$ is the chapter's clearest example of area
against throughput.

**Mechanism.** A radix-$2$ FFT of $N$ points factors into $\log_{2}(N)$ stages of butterflies, where one
butterfly takes two complex inputs $a$ and $b$ and a twiddle factor $W$ and emits $a + Wb$ and
$a - Wb$: one complex multiply and two complex adds. With the design's transform size the stage count
is $\log_{2}(512) = 9$, computed as the logarithm the size implies, so the pipeline is nine butterfly
stages in series. The R2SDF discipline is how data moves between them: each stage $k$ holds a delay
line of $N/2^{k}$ samples -- half the remaining size -- so that the two inputs each butterfly needs
arrive together, one fresh from the previous stage and one emerging from the delay. The first stage
delays 256 samples, the next 128, computed as the halving each stage implies; the total storage
across all nine delay lines is $N - 1 = 511$ complex samples, computed as the sum the stage sizes
imply. The twiddle factors are read from a table per stage, or generated by a smaller table plus
symmetry logic; either way they are constants, loaded once, never computed at run time.
[Figure 27](#fig-ch6-r2sdf-stage) draws one stage, and [Figure 28](#fig-ch6-r2sdf-pipeline) chains
nine of them.

::: {#fig-ch6-r2sdf-stage .figure}
```tikz
% One R2SDF stage, after He & Torkelson: a 2:1 switch, a butterfly whose sum output
% recirculates through the delay line in the feedback path, and a twiddle multiply on
% the difference output. The delay line is *in the loop*, not beside it: that feedback
% is what the "single-path delay feedback" name describes.
\begin{tikzpicture}[
  node distance=9mm,
  blk/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
              text width=19mm, minimum height=12mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
  fb/.style={-{Stealth[length=1.8mm]}, thick, dashed},
]
\node[blk] (sw) {switch\\(2:1 MUX)};
\node[blk, right=of sw] (bf) {butterfly};
\node[blk, right=of bf] (tw) {twiddle $\times$};
\node[blk, below=16mm of bf] (dly) {delay line\\$N/2^{k}$};
\coordinate[left=10mm of sw] (in);
\coordinate[right=10mm of tw] (outd);
\draw[arr] (in) -- (sw) node[lbl, midway, above] {input};
\draw[arr] (sw) -- (bf) node[lbl, midway, above] {selected};
\draw[arr] (bf) -- (tw) node[lbl, midway, above] {difference};
\draw[arr] (tw) -- (outd) node[lbl, midway, above] {to next stage};
\draw[arr] (bf.south) -- node[lbl, right=1pt] {sum} (dly.north);
\draw[fb] (dly.west) -| node[lbl, below, pos=0.25] {recirculated sample} (sw.south);
\node[lbl, below=1pt of sw.south, yshift=-1mm] {toggles every $N/2^{k}$};
\node[lbl, below=1pt of tw.south] {table constant};
\end{tikzpicture}
```
One R2SDF stage. The switch toggles every $N/2^{k}$ samples, so the delay line first loads and then
empties: while it loads, the input is stored; while it empties, each stored sample is the butterfly's
second operand and the current input is the first. The butterfly's sum output recirculates through
the delay line in the feedback path, which is the loop the architecture is named for, and only the
difference output leaves the stage through the twiddle multiply. The feedback wire is dashed because
it carries a different sample than the forward path, not a different clock.
:::

::: {#fig-ch6-r2sdf-pipeline .figure}
```tikz
% Nine stages in series, delay lines halving: 256 down to 1.
\begin{tikzpicture}[
  node distance=5mm,
  stg/.style={draw, align=center, inner sep=2pt, font=\scriptsize,
              text width=13mm, minimum height=10mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[stg] (s1) {stage 1};
\node[stg, right=of s1] (s2) {stage 2};
\node[stg, right=of s2] (s3) {stage 3};
\node[lbl, right=of s3] (dots) {$\cdots$};
\node[stg, right=of dots] (s9) {stage 9};
\draw[arr] (s1) -- (s2);
\draw[arr] (s2) -- (s3);
\draw[arr] (s3) -- (dots);
\draw[arr] (dots) -- (s9);
\node[lbl, below=1pt of s1.south] {longest delay};
\node[lbl, below=1pt of s9.south] {one sample};
\end{tikzpicture}
```
The nine stages in series. Each stage is one copy of the previous figure; the delay lines halve
from the longest at stage $1$ down to a single sample at the last stage, and the stage count is
the logarithm the transform size implies, computed as the previous section's padding states.
:::

**The butterfly is where fixed point enters.** *Mechanism.* Each butterfly multiplies by a twiddle
factor and adds, and in fixed point every multiply can grow the word: a $b$-bit input times a
twiddle factor needs guarding, or the stage overflows. The standard discipline is scaling by one half
at selected stages -- a right shift by one bit, free in hardware -- which bounds every intermediate at
the price of dropping each stage's least significant bit. Nine halvings is a factor of $2^{9} = 512$,
computed as the product the stage count implies, so a pipeline that scales at every stage divides the
signal's amplitude by the transform size itself; the spectrum's *shape* is exact up to that known
scale, and the design recovers it downstream by treating the FFT's gain as part of the Mel stage's
scaling. Whether to scale at every stage or only where overflow threatens is the section's fixed-point
decision, and it is the first quantity chapter 7 will measure rather than assume: the signal-to-noise
ratio of the fixed-point spectrum against the floating-point golden the experiment protocol of section 6.6
defines.

**The twiddle multiply is where the DSP bill is decided, and it has two shapes.** *Mechanism.* A
twiddle factor is a complex number on the unit circle, and multiplying one complex number by another
costs real multiplies. The direct form follows the algebra: $(a + jb)(c + jd) = (ac - bd) +
j(ad + bc)$, which is four real multiplies and two real adds. Every butterfly in this chapter's
nine-stage pipeline does one of these, so a radix-$2$ stage that computes the whole spectrum spends
its multiplies here and nowhere else. That is the honest count and the reason a 512-point transform is
not a small design: nine stages of butterflies, each carrying a complex multiply.

The Gauss rearrangement, which the field calls the three-multiplier form, trades one multiply for two
extra adds by observing that $ac$ and $bd$ are already computed and $ad + bc$ can be reached from
$(a + b)(c + d) = ac + ad + bc + bd$: form that third product, subtract the two you have, and the
imaginary part appears. The bookkeeping is

$$\text{Re} = p_1 - p_2,\qquad \text{Im} = p_3 - p_1 - p_2,\qquad p_1 = ac,\ p_2 = bd,\ p_3 = (a+b)(c+d),$$

which is three multiplies and three adds against the direct form's four multiplies and two adds.
On a DSP48E2 slice the trade reads one way and on LUT fabric another: a slice is a multiply-accumulate
whose adder is already there and already paid for, so the two extra adds are nearly free and a
three-multiplier complex multiply costs three slices where the direct form costs four -- a
$25\%$ slice saving on the pipeline's dominant arithmetic, computed as the difference the counts
imply. On LUT fabric the same saving is weaker, because an adder built from lookup tables is not free,
and the three-multiplier form's longer combinational depth costs the clock period that chapter 4's
slice is there to protect. The choice is therefore not "Gauss is better"; it is "Gauss is better where
the adder is already in the slice," and on this device's DSP48E2 that condition holds.

What the saving does *not* change is the table: the twiddle factors are constants either way, so the
storage bill is the same, and the chapter's scaling discipline is the same, because the width growth
through a complex multiply does not depend on how many real multiplies implement it.

> **The formula.**
> $$X[k] = \sum_{n=0}^{N-1} x[n]\, W_{N}^{kn}, \qquad W_{N} = e^{-j 2\pi / N}$$
>
> **The variables.**
> - $X[k]$ -- the $k$-th complex output bin of the transform. A complex number per bin.
> - $x[n]$ -- the $n$-th windowed input sample from the buffer of section 6.2. A fixed-point real
>   number per position.
> - $N$ -- the transform size, the 512 points the buffer pads to.
> - $W_{N}$ -- the primitive $N$-th root of unity, the twiddle factor; each butterfly multiplies by a
>   power of it read from the stage's table.
> - $k, n$ -- the output-bin and input-sample indices, each running over the transform size.
>
> **What it means.** The spectrum is a sum over all input samples of each sample times a complex
> exponential, and the FFT is a factorisation of that sum into $\log_{2}(N)$ stages of butterflies, so
> the formula is what the nine-stage pipeline of the previous figure computes. Each butterfly handles
> one factor of two in the sum's length; chaining nine of them handles $2^{9}$, which is the transform
> size the buffer delivers.
>
> **What it costs.** One complex multiply and two complex adds per butterfly per sample, times nine
> stages: the arithmetic is small, and the storage dominates -- the delay lines hold $N - 1$ complex
> samples, computed as the sum the stage sizes imply, plus the twiddle tables. The fixed-point price is
> the scaling: halving at a stage is a free shift, but each halving discards a bit of precision, and
> the accumulated rounding is what section 6.6 measures.
>
> **What it does not say.** It does not say the arithmetic is exact -- in fixed point it is not, and
> the formula is the ideal the pipeline approximates. It does not fix the input width, the twiddle
> width, or which stages scale; those are the design's decisions, and chapter 7 is where their error is
> bounded. And it does not say radix-$2$ is the only factorisation -- the next paragraph compares it
> with radix-$4$ on equal terms.

**Radix-$4$ against radix-$2$, on equal terms.** A radix-$4$ butterfly handles four samples at once with
three nontrivial twiddle multiplies, and a 512-point transform factors into $\log_{4}(512) = 4.5$
stages -- not an integer, so a pure radix-$4$ pipeline cannot cover this size and a real design mixes
radix-$4$ stages with one radix-$2$ stage. The trade is concrete: fewer stages and fewer delay lines
against a wider, hungrier butterfly with more multipliers and a longer critical path. For a front end
whose throughput is one window per hop period -- a gentle rate, set by the buffer -- the radix-$2$
pipeline's single sample per clock is already fast enough, and its small identical stages are simpler
to close timing on. The chapter therefore builds radix-$2$ and records radix-$4$ as the considered
alternative, with the reason stated: throughput the design does not need is area the design should not
spend.

> **Stop and check.** The pipeline scales by one half at a stage -- a right shift, free in hardware.
> What does that shift cost in signal terms, and why is it still the standard choice?
>
> **Answer.** It discards the stage's least significant bit, injecting rounding noise that accumulates
> across the nine stages. It is standard because the alternative -- widening every intermediate by a
> bit per stage -- grows every downstream bus, multiplier and delay line, and the rounding it avoids is
> small beside the quantisation the microphone and the Mel stage already impose. The honest statement is
> that the shift trades a bounded, measurable noise against unbounded width growth -- and section 6.6
> defines exactly how that noise gets measured.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-06-14` | the transform reads 512 points, the size this pipeline factors |
| `V-06-17` | that size is 512 FFT points as a derived quantity |
| `V-06-19` | the R2SDF pipeline (He and Torkelson, 1996) is the registered microarchitecture |
| `V-06-16` | a new window arrives every 160 samples, setting the throughput the pipeline must sustain |

<!-- source: 6.4 draft fragment -->

## 6.4 Mel Filterbank, Logarithm and Requantization on Fabric

*Where this sits in the chain: the three remaining transforms between the spectrum and the
quantized features -- a matrix that maps $257$ FFT bins onto 80 Mel bands, a logarithm that compresses
each band, and a requantizer that packs each compressed value into the integer word the downstream
hardware reads.*

**Intuition.** A spectrum is a wall of numbers, and too many of them matter for the downstream task to
be practical: a streaming voice recognizer reads one hundred features per second and must not make one
thousand decisions about what the spectrum contains. The Mel filterbank turns a spectrum into a much
shorter vector of band energies, the logarithm compresses the dynamic range so quiet and loud frames
fit in the same word, and the requantizer packs each result into the smallest integer the next stage
can accept. On a processor the three steps are a matrix multiply, a function call and a cast. On
fabric they are three blocks, each with a word width, a table and a throughput, and each one that
scales in width scales everything behind it: one extra bit in the matrix product is one extra bit in
the log, in the requantizer, and in the buffer that holds the features for the next stage.

**Mechanism.** The Mel filterbank is a fixed matrix. Chapter 1 owns the formula that maps hertz to
mel, and this section does not re-derive it; the 80 bands and their center frequencies are parameters
of the trained model, already fixed (`V-05-35`), and the design's job is to multiply the spectrum by a
matrix whose $M$ rows each carry a triangular weighting over the FFT bins it spans. The matrix is
$80 \times 257$, computed as the product of the band count and the bin count the transform produces,
and every nonzero element is a fixed coefficient, loaded once. A single multiply-accumulate (MAC)
engine running at the feature rate can compute one Mel band's energy per hop period, producing
80 values in 80 consecutive output cycles; a bank of MAC engines can compute all 80 simultaneously.
The throughput choice is again a free parameter: the pipeline must finish one feature vector per hop
period, and a single MAC engine can sustain that if its clock runs $80$ times the feature rate,
computed as the ratio the band count implies. The section keeps both alternatives in view, because
area against throughput is a trade the rest of the book inherits.

> **The formula.**
> $$\mathbf{E} = \mathbf{M} \cdot \mathbf{P}$$
>
> **The variables.**
> - $\mathbf{E}$ -- the 80-element Mel-energy vector: one value per band, the output of the filterbank.
> - $\mathbf{M}$ -- the $80 \times 257$ Mel weighting matrix: one row per band, one column per FFT bin,
>   every element a fixed-point constant. The weights are non-negative and sum to one across each row,
>   so the matrix scales but does not amplify.
> - $\mathbf{P}$ -- the $257$-element power spectrum: one squared magnitude per FFT bin, already in fixed
>   point from the transform engine.
>
> **What it means.** Each band's energy is a weighted sum of the FFT bins it covers, and the matrix is
> exactly the same triangular weighting the Mel formula of chapter 1 defines, discretized onto $257$ bin
> positions and rounded to the fixed-point width the design requires. The multiply-accumulate is a
> linear transform, and on fabric each MAC fuses the fixed-point multiply with an add: one DSP slice,
> one cycle, one row element.
>
> **What it costs.** One multiply per nonzero element per band; the Mel matrix is sparse, so a naive
> $80 \times 257$ count overestimates the real bill. The nonzero elements per row are the bins each
> triangle spans, which depends on the triangle width, and the total nonzero count is the number of
> multiplies the design must sustain. The MAC count is a fixed quantity, and it is derived from the
> matrix the corpus's Mel formula produces -- not something the hardware designer chooses.
>
> **What it does not say.** It does not say the matrix is dense -- it is not, and a sparse layout
> exploits the structure. It does not say the MAC count is a registered measurement of this design;
> it is a derived arithmetic quantity, stated for the reader to check against the formula and the
> matrix's structure. And it does not say the Mel formula belongs to this chapter: the formula is
> owned by chapter 1, and the matrix is its fixed-point discretization on the hardware.

**The logarithm is a table lookup plus an interpolation.** A chip cannot compute a logarithm in a
single cycle, and the signal needs its dynamic range compressed before the next stage. The standard
solution is a lookup table (LUT) indexed by the upper bits of the Mel-energy value, with a short
linear interpolation between table entries filling in the remaining bits. The table size sets the
accuracy: a 256-entry table addressing the upper eight bits of a $16$-bit Mel energy gives each entry
four bits of range, and one linear segment per range gives the log to within one quantization step.
The LUT is stored in block RAM, which chapter 1 counts (`V-01-22` gives the total), and the
interpolation is one multiply and one add, both of the same width as the Mel energy. The log does not
change the sample rate -- one output per input -- but it sets the word width of every downstream value:
the log of a $16$-bit unsigned integer fits in a signed $16$-bit word, and that signed word is the width
the requantizer reads. The cost is one table and one multiply per Mel band per feature vector, and the
price is the table's approximation error, which chapter 7 measures against the exact log as a second
round of fixed-point noise.

**The requantizer packs the log value into a smaller word.** The downstream features -- the input to
the first convolutions -- read a fixed-point integer, and the requantizer scales and rounds the
signed-$16$-bit log value into that smaller width. The standard integer quantization maps a range
$[a, b]$ into $[0, 2^{B} - 1]$ by a linear transformation: subtract the lower bound, multiply by
the range of the target word, divide by the range of the source, and round. In hardware this is one
subtract, one multiply, one shift and one rounding, all free at the feature rate; the only table is
the pair of bounds $[a, b]$, which are constants loaded once from the trained model's configuration.
Jacob et al. (`V-06-01`, `V-06-02`) provide the formulation this design follows for the integer requantization
weights, which fix both the bounds and the scaling. The cost is one arithmetic cycle per band per
feature vector, and the price is the quantization error at the rounding step, a third bounded noise
term that chapter 7 will measure.

[Figure 29](#fig-ch6-mel-pipeline) draws the three stages as one datapath.

::: {#fig-ch6-mel-pipeline .figure}
```tikz
% Three stages: matrix multiply, log lookup, requantize.
\begin{tikzpicture}[
  node distance=6mm,
  blk/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
              text width=15mm, minimum height=12mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[blk] (mat) {Mel matrix\\ 80 x 257};
\node[blk, right=of mat] (log) {log LUT\\ + interp};
\node[blk, right=of log] (req) {requantize};
\draw[arr] (mat) -- (log);
\draw[arr] (log) -- (req);
\node[lbl, below=1pt of mat.south] {257 bins in};
\node[lbl, below=1pt of log.south] {80 bands};
\node[lbl, below=1pt of req.south] {80 integers out};
\end{tikzpicture}
```
The three remaining stages of the front end as one datapath. The matrix maps $257$ FFT bins to 80
Mel bands, the log compresses the dynamic range, and the requantizer packs each value into the
word width the downstream features read; each stage is one cycle per band per feature vector.
:::

> **Exercise (laddered).** The Mel matrix is $80 \times 257$. (a) If each row is sparse and spans
> exactly 10 nonzero elements, how many MAC operations does one feature vector require, computed as the
> product the nonzero count implies? (b) At one hundred feature vectors per second, how many MACs per second
> does one MAC engine sustain, computed as the product the rates imply? (c) The log table has 256
> entries and one interpolation multiply per lookup. If one table entry covers the range of eight bits
> in the Mel energy, how many bits does the table index have, computed as the base-two logarithm the
> entry count implies, and what does that say about the minimum word width the Mel energy must carry
> for the table to be fully addressed?
>
> **(d) The same engine on a clock.** Suppose the MAC engine of part (b) runs at a fabric clock of
> $100$ MHz and commits one MAC per cycle per DSP slice. How many clock cycles does one feature vector
> consume, what is the execution period of one feature vector, and what fraction of one slice's time is
> occupied, computed as the ratio of the execution period to the frame period the hop rate implies?
> Then state how many feature vectors a single slice could sustain in principle, and why the answer is
> not the design's real limit.
>
> **Answers.** (a) $80 \times 10 = 800$ MACs per feature vector. (b) $800 \times 100 = 80{,}000$ MACs
> per second -- a very modest number for modern fabric. (c) $\log_{2}(256) = 8$, so the index needs $8$
> bits, meaning the Mel energy must be at least $8$ bits wide for every table entry to be addressable; a
> wider energy value gives the interpolator more bits to work with.
>
> (d) $800$ cycles per feature vector at $100$ MHz is a period of $800 \times 10\ \text{ns} = 8\ \mu\text{s}$, computed as the product the cycle count and the clock period imply. The frame period
> is $160$ samples at $16$ kHz, which is $10$ ms, so one slice is occupied $8\ \mu\text{s}$ out of every
> $10$ ms: a duty cycle of $0.08\%$, computed as the ratio of the two periods. One slice could in
> principle sustain $10\ \text{ms} / 8\ \mu\text{s} = 1250$ feature vectors per period, against the
> $100$ the front end actually produces. That margin is not the design's real limit, for two reasons:
> the Mel engine must also wait on the $257$-bin spectrum the FFT stage delivers before any of its MACs
> can start, so the latency budget is set upstream of the arithmetic count, and a slice that is
> $99.92\%$ idle on this task is only idle if nothing else is scheduled onto it -- the same silicon
> runs the log table lookup, the requantizer, or the next chapter's convolutions in the cycles this
> stage leaves free. The honest reading of the number is that the Mel filterbank is arithmetically tiny
> and the design's constraints are elsewhere: in memory bandwidth for the table, in the FFT's
> throughput, and in the fixed-point widths part (c) sized.

**Application.** The section's deliverable is a three-stage datapath that reduces $257$ fixed-point
spectrum bins to 80 fixed-point features per hop, and the cost is three small arithmetic blocks plus
the LUT. Each stage is a word-width decision, and the widths propagate: if the Mel energy is
$B_{\text{mel}}$ bits and the log value is $B_{\text{log}}$ bits, the downstream features are at most
$\min(B_{\text{log}}, B_{\text{req}})$ bits, and the buffer that holds features for the next chapter's
convolutions is sized by that width times the number of features. The Mel matrix is constant, loaded
once; the log table is constant; the requantizer is two constants and a shift. The three stages add
zero ongoing state to the front end, and section 6.5 closes the chapter by describing where the finished
features go.

**What this section does not yet know.** The features are finished at this point, but the
experiment protocol that proves them correct against a floating-point baseline has not been defined.
Section 6.6 provides that protocol and states what the numbers will be before they are measured.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-35` | the Mel filterbank has 80 bands, fixing the matrix height |
| `V-06-14` | the transform produces $257$ bins, fixing the matrix width |
| `V-06-01` | integer requantization weights (Jacob et al., 2018) follow the standard linear scaling |
| `V-06-02` | the same formulation, corroborating the requantization weights |
| `V-05-10` | the corpus stores speech at 16 kHz, the rate the exercise's frame period divides by |
| `V-06-16` | the hop is 160 samples, which fixes the $10$ ms frame period the duty cycle divides |
| `V-01-22` | the board's on-chip memory total, against which the log LUT is a small allocation |

<!-- source: 6.5 draft fragment -->

## 6.5 The Handoff to Feature Processing

*Where this sits in the chain: the boundary between the audio front end and the network that runs on
the features it produces.*

**Intuition.** The front end's output is a stream of 80-element vectors, one per hop period, and the
stream's properties are fixed by the parameters chapter 1 derived: one vector per 0.01 s
(`V-05-31`), one vector per 160 audio samples (`V-06-16`), each vector carrying 80 mel bands
(`V-05-35`). The handoff is not a new stage but a contract: whatever follows must read 80 values per
period at one hundred periods per second, and the front end must produce them at that rate. On the KV260 the
receiver is a block that reshapes the vector into the activation format the first convolutional layer
reads -- a small adapter, not a processing step -- and the chapter treats it as settled: the features
arrive, the network accepts them.

**Mechanism.** The feature stream is synchronous to the hop clock, which the buffer of section 6.2
generates. Every 0.01 s the requantizer produces its last band's value, the vector is complete, and
the downstream block reads it. The handoff block must not stall: if it reads one value per cycle and
there are 80 values, the handoff takes at most 80 cycles per hop period, computed as the vector length
times the per-cycle rate, and any cycle stolen by a downstream stall must be absorbed by the vector's
internal registers. The front end does not store a backlog of vectors -- the buffer holds one window,
the transform holds one spectrum, and the Mel chain holds one vector -- so the front end is *pipeline
synchronous* to the downstream consumer: a stall in the features stops the front end, which stops the
transform, which stops the buffer, which stops accepting audio. This is the design's single
throughput bottleneck, and section 6.6 defines how its margin is measured.

**What this section does not yet know.** The handoff's timing margin has not been measured on real
hardware; it has been sized by the parameters the front end implies. Section 6.6 defines the
experiment that measures the margin and the noise, and the wrongness the chapter opened with is left
for chapter 7 to bound.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-31` | the feature rate is one vector per 0.01 s, the hop period the handoff must sustain |
| `V-06-16` | the hop is 160 audio samples, derived from the same rate |
| `V-05-35` | each feature vector carries 80 mel bands, the vector length the handoff must deliver |

<!-- source: 6.6 draft fragment -->

## 6.6 The experiment protocol: what the numbers will be before they are measured

*Where this sits in the chain: a protocol definition for experiment exp_06, which measures the
fixed-point front end's correctness against a floating-point baseline.*

**Intuition.** Chapter 4 and chapter 8 proved that a design's numerical honesty lives in its experiment log,
not in its paper, and this section follows the same discipline. The fixed-point front end has been
built without measured data: the transform's rounding error, the Mel stage's quantization noise and
the requantizer's truncation are all *bounded by design* but not yet measured on the hardware. The
experiment protocol below defines what the measurements will be, what the baseline is, and how the
results will be compared, so that the reader knows in advance what a passing log looks like and what
a failure looks like. No fabricated values appear in this section.

**Mechanism.** The experiment, designated exp_06, compares the fixed-point front end against the
exp_01 floating-point golden, which chapter 5 captured as a fully deterministic FP32 pipeline on
the same corpus. The comparison is a signal-to-quantization-noise ratio (SQNR): for each of the feature vectors the
exp_01 golden under `results/exp01/` produced, the experiment computes the mean
squared error between the fixed-point feature vector and the FP32 feature vector, then converts
that error to a decibel ratio against the signal power. The design is hardware (Vivado HLS or RTL),
and the comparison is bit-exact between the fixed-point and the floating-point on the same input
frames.

> **The formula.**
> $$\text{SQNR}_{\text{dB}} = 10 \log_{10}\!\left(\frac{\sum_{f=1}^{F} \|\mathbf{y}_f\|^{2}}{\sum_{f=1}^{F} \|\mathbf{e}_f\|^{2}}\right)$$
>
> **The variables.**
> - $\text{SQNR}_{\text{dB}}$ -- the signal-to-quantization-noise ratio in decibels. A negative number
>   means the error is larger than the signal; a positive number means the signal dominates.
> - $\mathbf{y}_f$ -- the $f$-th feature vector from the FP32 golden (exp_01). A vector of eighty
>   floating-point values.
> - $\mathbf{e}_f = \mathbf{y}_f - \hat{\mathbf{y}}_f$ -- the error vector: the difference between the
>   FP32 golden and the fixed-point output for the same frame. The experiment's core quantity.
> - $F$ -- the total number of frames compared, one per hop period in the corpus.
>
> **What it means.** The numerator is the total signal power across all frames; the denominator is the
> total error power. The ratio measures how many bits of the fixed-point output are meaningful: every
> $6$ dB of SQNR is approximately one bit of precision above the noise floor. A high SQNR means the
> fixed-point output is very close to the FP32 golden; a low SQNR means the fixed-point arithmetic is
> losing information that the downstream network would otherwise see.
>
> **What it costs.** The cost is not in the front end but in the measurement: the experiment must
> replay the same corpus through both pipelines and compare, which is the same offline validation
> discipline chapter 5 established. The golden log under `results/exp01/` provides the FP32 reference.
> What it does not say. It does not say the SQNR will be a particular number -- that is what the
> experiment will measure, and this section does not fabricate it.

**The comparison also records the mean absolute error (MAE) per band.** The SQNR captures total
noise power but not where it lives; a band-by-band MAE shows whether the error is concentrated in the
low-frequency bands, where speech energy sits, or in the high-frequency bands, where the Mel weighting
is sparse. The experiment computes the MAE of each of the $80$ bands across all frames, producing a
vector of $80$ error values, one per band. The FP32 golden for exp_01 reported a zero mean absolute
error for the feature vectors; the fixed-point front end will have nonzero error, and the experiment
protocol records that error honestly.

**The experiment compares against the FP32 golden, not against the zero-decibel hypothesis.** The fixed-point
front end is not expected to produce a zero-decibel error, and the comparison against zero decibels would be
meaningless. What the experiment proves is that the fixed-point error is bounded and measurable, and
that the downstream network can accept the features without a detectable degradation. Chapter 7 will
measure the degradation through the full model, but this experiment's SQNR is the front end's own
score: it answers "how much precision did the fixed-point pipeline lose?" independent of whether the
network tolerates that loss.

**What this section does not yet know.** The SQNR value, the MAE values and the frame count of exp_06
are all to be measured. The experiment has been defined, the baseline captured, and the comparison
metric chosen; the results will appear in the experiment log under `results/exp06/` when the design is
synthesized and tested on the FPGA.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-35` | each feature vector carries 80 mel bands, the comparison dimension |
| `V-05-31` | one feature vector arrives per hop period, the fixed input cadence for the comparison |
| `V-05-10` | the ingest delivers 16 kHz speech, the rate the feature stream comes from |
| `V-06-15` | the frame size of 400 samples, fixed by the design parameters |
| `V-06-16` | the hop is 160 samples, which sets the feature rate the comparison counts |

---

## Summary

This chapter followed the signal from the microphone inward, and at every stage the question was the
same: what does a quantity that chapter 1 derived as an arithmetic step become when it is a block with
a clock and a word width. The ingest turned out to be two paths: a codec link that needs framing only,
and a PDM stream that needs a multiplierless CIC filter at the fastest clock in the design. The frame
buffer turned out to be a shift register that retains, advances and pads, with every parameter
inherited directly from the trained model. The transform turned out to be a nine-stage R2SDF pipeline
whose storage cost dominates its arithmetic cost and whose rounding error is bounded but not yet
measured. The Mel stage turned out to be a sparse matrix multiply, a lookup table and a short linear
scale, all of them small, all of them setting the word width of every downstream value. And the
handoff turned out to be a contract: a synchronous stream of eighty-element vectors, one per hop period,
whose timing margin is the front end's single bottleneck.

The chapter did not fix the wrongness. It built the pipeline, bounded the error at each stage, and
defined the experiment that will measure it. The wrongness is chapter 7's business.