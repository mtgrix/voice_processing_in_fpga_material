# Keyword Spotting on the Board: From Microphone to Decision

> **Scope note (Issue #53, superseding the note left by Issue #29).** These are the re-cut sections,
> not the stubs. `plan-v2.md` section 7 assigns this chapter the keyword-spotting build, so the order
> follows the signal path rather than the topic list: what has to be bolted onto the board before a
> sample exists, then the convolution datapath, then the arithmetic of the non-linear stages, then the
> test that says the build works. The stub that promised streaming chunk-level self-attention moved to
> chapter 9, which is where the model that has that attention now sits; the other three kept their
> subjects and changed their order.

> *Objective: Take a keyword-spotting network from a microphone the board does not have to a decision
> the board can defend: the acquisition path, the convolution datapath, the non-linear arithmetic, and
> the acceptance test that closes the stage.*

---

<!-- source: 8.1 reviewed fragment -->

## 8.1 The Board Has No Microphone: Tracing One Second of Audio

**The board cannot hear you.** The KV260 carrier has no onboard microphone, no audio jack and no audio converter; `V-03-01` records for it only "Audio transmit and receive (I2S) via PMOD audio codec", where I2S (Inter-IC Sound) is the serial link between a converter and the logic, and a PMOD is a module plugging into a two-row header. Nothing is captured until one is bought and fitted. A laptop has a microphone, so a plan written on one reaches the model before it notices this.

**There are two ways in, and they are not the same kind of answer.** The vendor's own part is the Audio Codec I2S PMOD, Digilent SKU 410-379, in connector J2, which `V-03-02` lists as tested with the smart camera application. `V-03-03` opens it up: a Cirrus CS5343 analogue-to-digital converter (ADC) and a CS4344 digital-to-analogue converter (DAC), 24-bit, stereo, on line inputs and outputs, with input rates up to 108 kHz. Read "line" strictly: a capsule still needs amplification upstream of the board. The other way is a USB microphone on one of the four USB 3.0 Type-A ports `V-03-05` records, which Linux sees through ALSA (its audio subsystem) as a USB audio class (UAC1/UAC2) device. That route needs no carrier modification, and it leaves conversion, clocking and gain outside the design. Only the first hands a programmable design a stream it can own, so the choice is scope, not wiring.

**Both corpora are stored at 16 kHz, and that settles the input clock.** `V-05-11` reads the Speech Commands paper, where each utterance is "stored as a one-second (or less) WAVE format file, with the sample data encoded as linear 16-bit single-channel PCM values, at a 16 KHz rate", and `V-05-10` gives the same rate for LibriSpeech. That second record is the corpus's own distribution page, so it corroborates rather than stands alone, as chapter 1 read it. A frontend at any other rate is wrong before a line of hardware exists. What the pair does not settle sits in the same two records: the codec offers 24-bit stereo (`V-03-03`), the files are 16-bit single-channel (`V-05-11`), and no record fixes where the extra bits and the second channel go.

**The encoder consumes frames, not samples, and no record here fixes the frame rate.** Between the stream and the model the frontend groups samples into overlapping frames and reduces each to a few spectral values, so the path runs on two clocks, and only the first is settled above. How many frames arrive in a second, and how long one encoder step lasts, are not among the records this section draws on, so section 8.1 prints no number for either. The two domains are real whatever fills the second one, and a design that sizes a buffer in samples against a budget in steps is wrong in a way no simulation catches.

**The metric is not a word error rate (WER).** MatchboxNet, the keyword spotter registered here, comes in sizes of 77K, 93K and 140K parameters (`V-05-01`). `V-05-02` decides how any later number is read: the task is isolated-word classification over a closed set -- 12 or 35 classes, clips of one second or less -- and the quantity is top-1 accuracy in percent. MatchboxNet is not a continuous sequence model, so it has no WER. Accuracy asks whether the right word was chosen; WER counts edits across a transcript. A table that mixes the two compares nothing.

> **A passing number is speaker-independent, or it is nothing.** `V-05-08` records how the partition is made: `validation_list.txt` and `testing_list.txt` ship with the download, membership follows a hash of the file name, and that name begins with a hashed speaker identifier, so every clip of one speaker lands in one partition. That is what turns the accuracy of `V-05-02` into a claim about unfamiliar voices. `V-05-07` registers the licence as Creative Commons Attribution 4.0 (CC BY 4.0), over 105,829 utterances, 35 words and 2,618 speakers, so attribution is the whole obligation, and a result can travel with its data.

[Figure 3](#fig-kws-signal-path) puts the path on one line, and it is where the two clocks show.

::: {#fig-kws-signal-path .figure}
```tikz
% One second of audio, room to label. The chain is one row of equal-height boxes so
% the two dashed bands, which mark the clock domains, can share a top and a bottom
% edge. Under each box a node states what fixes its rate, and the two boxes whose
% rate no record carries say so in the same ink as the rest.
\begin{tikzpicture}[
  node distance=7mm,
  box/.style={draw, align=center, inner sep=4pt, font=\scriptsize,
              text width=16mm, minimum height=13mm},
  rate/.style={font=\scriptsize, align=center, inner sep=1pt, text width=19mm},
  t/.style={font=\scriptsize, inner sep=2pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
  band/.style={draw, gray!65, densely dashed},
]
\node[box] (dev) {input device:\\ PMOD codec\\ or USB mic};
\node[box, right=of dev] (pcm) {sample stream:\\ 16 kHz, 16-bit,\\ single channel};
\node[box, right=of pcm] (fe)  {frontend:\\ frames of\\ log-Mel values};
\node[box, right=of fe]  (enc) {keyword encoder:\\ one step\\ per frame};
\node[box, right=of enc] (lbl) {one label:\\ 12 or 35\\ classes};
\draw[arr] (dev) -- (pcm);
\draw[arr] (pcm) -- (fe);
\draw[arr] (fe)  -- (enc);
\draw[arr] (enc) -- (lbl);
% What fixes each rate. Every id here is the id prose cites for the same quantity.
\node[rate, below=1pt of dev.south] {up to 108 kHz\\\texttt{V-03-03}};
\node[rate, below=1pt of pcm.south] {16 kHz\\\texttt{V-05-11}};
\node[rate, below=1pt of fe.south]  {frame rate:\\no record};
\node[rate, below=1pt of enc.south] {step rate:\\no record};
\node[rate, below=1pt of lbl.south] {a metric,\\not a rate:\\\texttt{V-05-02}};
% The two clock domains. Equal-height boxes make the two tops and bottoms coincide.
\coordinate (aSW) at ($(dev.south west)+(-5pt,-36pt)$);
\coordinate (aNE) at ($(pcm.north east)+(5pt,14pt)$);
\coordinate (bSW) at ($(fe.south west)+(-5pt,-36pt)$);
\coordinate (bNE) at ($(lbl.north east)+(5pt,14pt)$);
\draw[band] (aSW) rectangle (aNE);
\draw[band] (bSW) rectangle (bNE);
\node[t, anchor=south] at ($(aSW|-aNE)!0.5!(aNE)$) {\textbf{sample clock}};
\node[t, anchor=south] at ($(bSW|-bNE)!0.5!(bNE)$) {\textbf{feature clock}};
\end{tikzpicture}
```
Follow the drawing from the left rather than from the boxes: the first two stages run
on one clock and the next three on another, and the seam between the dashed bands is
where the reduction happens. Two of the nodes under the boxes say that no record fixes
the rate at that stage, and they are why two rows of the table below carry no number.
:::

| Stage | What enters | What leaves | Which record fixes its rate |
| --- | --- | --- | --- |
| Room | a sound | a line-level signal | none: the carrier has no microphone (`V-03-01`) |
| PMOD codec | line-level analogue | an I2S bitstream | up to 108 kHz in (`V-03-03`); part and connector (`V-03-02`) |
| USB route | a microphone capsule | ALSA PCM frames | no rate registered; `V-03-05` gives ports |
| Capture | either stream | a 16-bit, single-channel file of one second or less | 16 kHz (`V-05-11`, corroborated by `V-05-10`) |
| Frontend | the sample stream | frames of spectral values | not registered for this section |
| Encoder | those frames | one output per frame | the same unregistered frame rate |
| Decision | the outputs | one label from a closed set | a metric, not a rate: top-1 accuracy (`V-05-02`) |

<!-- source: 8.2 reviewed fragment -->

## 8.2 A Depthwise Convolution Is a Line Buffer With Taps

**The separable split is a hardware statement written as a network layer.** A depthwise separable convolution replaces one dense filter with two passes. A *depthwise* pass filters each channel on its own, so one filter per channel and no mixing. A *pointwise* pass is a 1 × 1 convolution: one position, all channels in, all channels out, and it does the mixing. The order looks wasteful and the reason for it is arithmetic. In a dense filter every input channel meets every output channel, so a fetched weight is multiplied into many products and a design can hold the weight still while activations stream past. In a depthwise pass a weight belongs to exactly one channel, so far fewer multiply-accumulates (MAC -- one multiplication and one addition fused into one hardware step) arrive per weight fetched, and the fetching becomes the work. The pointwise pass puts the ratio back, because it is dense. So a convolution stack of this kind is two workloads in one layer: the depthwise part is shaped by memory traffic, the pointwise part by arithmetic units, and a machine good at only one of them idles through the other.

**The traffic the depthwise part generates is mostly re-reads, and re-reads are a buffer.** What a sliding window reads more than once is the input, not the weights. A hardware design therefore keeps the recent inputs where they can be read cheaply, in a *line buffer* -- storage for the steps a window still needs, so that each new step is written once and read again by every later output whose window covers it. [Figure 4](#fig-depthwise-line-buffer) draws exactly that, and the whole argument of this section is visible in which arrows repeat.

::: {#fig-depthwise-line-buffer .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize, node distance=1.6mm,
  cell/.style={rectangle, draw, minimum width=6.6mm, minimum height=5.6mm, inner sep=1pt},
  old/.style={cell, fill=black!14},
  cur/.style={cell, fill=black!55},
  tap/.style={cell, minimum height=4.2mm, draw, densely dashed},
  ptr/.style={-{Stealth[length=2mm]}, thick}
]
  \node[old] (c1) {$i{-}3$};
  \node[old, right=of c1] (c2) {$i{-}2$};
  \node[old, right=of c2] (c3) {$i{-}1$};
  \node[cur, right=of c3] (c4) {$i$};
  \node[right=9mm of c4] (rest) {\dots};

  \node[tap, above=8mm of c1] (t1) {$t_0$};
  \node[tap, right=of t1] (t2) {$t_1$};
  \node[tap, right=of t2] (t3) {$t_2$};
  \node[tap, right=of t3] (t4) {$t_3$};

  \draw[ptr] (t1) -- (c1); \draw[ptr] (t2) -- (c2);
  \draw[ptr] (t3) -- (c3); \draw[ptr] (t4) -- (c4);

  \node[left=2mm of t1, anchor=east] {window};
  \node[left=2mm of c1, anchor=east] {stream};

  \node[below=9mm of c2] (buf) [cell, minimum width=30mm, minimum height=8mm]
    {line buffer: $i{-}3$ \dots $i$ held};
  \draw[ptr] (c1.south) -- ++(0,-3mm) -| (buf.north west);
  \draw[ptr] (c3.south) -- (buf.north);
  \draw[ptr] (c4.south) -- ++(0,-3mm) -| (buf.north east);

  \node[below=1.5mm of buf.south, anchor=north, align=center]
    {written once \quad · \quad read $k$ times};
\end{tikzpicture}
```
Read the four downward arrows as four weights, not four fetches: the oldest steps are already in the buffer when a new step arrives, so one store feeds several outputs.
:::

**How long the window is decides how much the buffer holds, and the targets disagree about it.** The registered readings sit side by side below.

| Candidate reading | Taps | What the record reads from it | Record |
| --- | --- | --- | --- |
| Conformer-Transducer, Small | 31 | every variant in that table but XLarge keeps 31, so this is a family property, not a size knob | `V-05-15` |
| Cache-aware streaming Conformer-Transducer, Large, causal | 31 | a tap history of 30 encoder steps | `V-05-25` |
| Cache-aware streaming FastConformer-Transducer, Large, causal | 9 | 8 steps of history, and the saving is in the convolution module's own state rather than the attention cache | `V-05-40` |
| Another implementation's reading of the same field | 15 | registered separately; the pick of a target is open, so the tap count is one of the live differences | `V-05-15` |

Nothing here is priced per frame. Per-frame cost -- MACs, INT8 weight bytes, activation bytes -- is unregistered for every candidate (`V-05-57`), so this section states the shape and stops.

**Reach is a two-term rule, and it is the only arithmetic this section needs.** *Mechanism.* A window reads the current step and reaches backwards for its history; how far it reaches and how often it moves are set by different knobs.

$$R = (k - 1)\,d + 1, \qquad \text{one output every } s \text{ input steps}$$

$k$ is the tap count, $d$ is the dilation -- the spacing between taps, in steps -- and $R$ is the reach, the number of input steps one output covers, including the current one. $s$ is the stride: consecutive outputs start $s$ input steps apart. With $d = 1$ the rule reproduces what the table prints: 31 taps reaching 30 steps back `V-05-25`, and the other candidate's 9 taps reaching 8 `V-05-40`. *Engineering consequence.* $R$ fixes the buffer's depth in steps, and $s$ fixes how fast its contents turn over, so a longer tap costs storage while a larger stride costs the same storage less often. *What it cannot tell the reader.* Not bytes, and not time. $R$ is in steps, and a step becomes a wall-clock interval only once the encoder's step period is registered; and $R$ says nothing about how many channels it must be copied across, which is where the storage actually goes. Dilation is left a symbol on purpose -- neither candidate's records register a value for it.

**The reference keyword network is the small case, and the record prints it as names.** MatchboxNet is a 1D time-channel separable convolutional network at $C = 64$ channels, and `V-05-01` prints three variants with their parameter counts: 77K for `3x1x64`, 93K for `3x2x64`, 140K for `6x2x64`. The name carries the depth and the width, so a reader sees the stack growing in the same record that prices it; `V-05-01` notes that counts of this size fit entirely into on-chip block RAM (BRAM -- on-chip storage) without off-chip access. `V-05-02` is the other half of the record: the model reports isolated word classification accuracy on 1-second clips from a closed set of 12 or 35 classes, not a word error rate (WER -- the fraction of transcribed words that are wrong). A design that quotes that accuracy is not quoting transcription.

**The buffer lives in one of three containers, and the unit must travel with the number.** All figures are the device registered as `xczu5ev` / `XCK26`, from document DS890 page 22, Table 23.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| BRAM blocks, 36 kilobit each | 144 | `V-01-05`, tile size `V-01-23` |
| UltraRAM (URAM) blocks, 288 kilobit each | 64 | `V-01-07`, tile size `V-01-23` |
| BRAM and URAM together | 23,616 Kb | `V-01-22` |
| Distributed RAM (LUTRAM) | 3.5 Mb | `V-01-16` |
| Configurable logic block look-up tables (CLB LUT -- the basic logic element) | 117,120 | `V-01-03` |
| CLB flip-flops | 234,240 | `V-01-04` |
| DSP48E2 slices (the multiply-accumulate block of this family) | 1,248 | `V-01-09` |

Every value is quoted in the unit the record prints it in. `V-01-23` settles the datasheet's megabit columns as 1024-based, so a Mb there is 1,024 Kb; `V-01-22` exists because "4 MB" and "4.5 MB" were each defensible under some other reading and neither survives the arithmetic. The three containers are not interchangeable. BRAM and URAM are fixed tiles and are counted together at 23,616 Kb; LUTRAM is built from the look-up tables in the row above it, so it spends logic and is not initialised by the bitstream the way BRAM is, which is why `V-01-16` is not added to that budget. A short-tap depthwise stage that wants a few hundred words at very low latency may be better served by LUTRAM than by a whole 36 Kb tile, and no record here says which. Flip-flops matter to this section for one reason: at the word level the shifting part of a line buffer is registers. Building any of it needs no licence -- the device is supported in the standard Vivado ML Standard flow without one (`V-04-01`).

<!-- source: 8.3 reviewed fragment -->

## 8.3 Softmax and LayerNorm Without a Floating-Point Unit

Attention and normalisation ask for four things a CPU gives away: an exponential, a
reciprocal, a sum and a square root. A fabric of multipliers, adders and storage can build
all four, and building them is this section. The arithmetic decisions below are design, not
result: no error, rate or resource figure appears here, because none has been measured.

**Subtracting the row maximum is a correctness step.** In real arithmetic, these two
expressions have the same value:

$$\mathrm{softmax}(\mathbf{z})_i = \frac{e^{z_i}}{\sum_j e^{z_j}} = \frac{e^{z_i - m}}{\sum_j e^{z_j - m}}, \qquad m = \max_j z_j$$

$\mathbf{z}$ is one row of attention scores -- one value per position the query may look at --
$m$ is the largest of them, $i$ and $j$ index positions inside the row, and the sum in the
denominator runs across the whole row. The two right-hand forms differ by a factor $e^{m}$
that cancels, so a calculator shows no gain at all. The gain is in the interval, not the
answer. Every term of the right-hand numerator and denominator now lies in $[0,1]$, so the
largest value either one can hold is $1$: a fixed-point encoding whose range tops out at
exactly that holds both without a second thought. The unreduced form, exponentiating $z$
directly, cannot say what its largest value will be before it has been computed.

The price is order. $m$ exists only after the last score of the row exists, so the row must
be held in a buffer and a reduction must finish before the first exponential begins -- an
adder-free tree of pairwise compares, which halves the list at every step. The blocking point
is drawn in Figure 5, and both variants there pay it.

**Base 2 moves the cost from a unit to a multiply, a table and a shift.** The step down from
the unreduced to the reduced softmax is not one an exponentiation unit makes.

$$e^{x} = 2^{\,x\log_2 e} = 2^{k}\,\cdot\,2^{f}, \qquad k = \lfloor\, x\log_2 e \rfloor, \qquad f = x\log_2 e - k$$

$x$ is an already-reduced score, a non-positive fixed-point number. The factor
$\log_2 e$ is one constant multiply, performed in the fixed-point form `V-06-02` describes
below. $k$ is an integer and $f$ is its fraction, in $[0,1)$. Two things follow: $2^{k}$ is a
shift by $k$ places, and $2^{f}$ is not a function evaluation but a read, because $f$ has few
significant bits and every one of them indexes a table written once at compile time.

A reciprocal square root is the same trick with one snag:

$$\frac{1}{\sqrt{y}} = 2^{-k/2}\,\cdot\,\frac{1}{\sqrt{f}}, \qquad y = 2^{k}f$$

$y$ is a LayerNorm variance plus the small constant added to keep its square root away from
zero. A halved integer exponent is a shift, and the fraction again goes to a table. The snag
is that $k$ need not be even: an odd $k$ leaves a factor $\sqrt{2}$ behind, and a plain shift
drops it silently. The cheapest fix is an odd flag taken from the lowest bit of $k$ that
selects a correction entry from the same table; a second table needs no flag at all. The
softmax denominator reaches its reciprocal the same way.

[Figure 5](#fig-nonlinearity-approx) puts the two routes side by side. Look at what each path
spends: the left one keeps a general exponentiation unit and a divider, and the right one
replaces them with a constant multiply, a small read-only memory and three shifts. The dashed
bar in the middle of each path is the reduction that blocks the row.

::: {#fig-nonlinearity-approx .figure}
```tikz
% Two softmax pipelines, drawn as the hardware that realises them. Left: base-e, one
% general exponentiation unit per lane plus a divider. Right: the max-subtracted base-2
% path of this section -- constant multiply, table read, shift -- for both the
% exponential and the reciprocal. The shaded boxes are the stages whose cost is a
% function unit rather than storage; the dashed bar is where the row maximum must
% finish, which both paths pay.
\begin{tikzpicture}[
  box/.style={draw, rounded corners=2pt, inner sep=3.5pt, font=\scriptsize,
              align=center, text width=2.55cm},
  hot/.style={box, fill=red!9, draw=red!70!black},
  cold/.style={box, fill=blue!7},
  blk/.style={draw, dashed, inner sep=4pt, font=\scriptsize, align=center},
  a/.style={-{Stealth[length=2mm]}, thick},
  t/.style={font=\scriptsize, inner sep=2pt},
]
\node[t, font=\small, below] at (-1.55,0.3) {base $e$, general unit};
\node[t, font=\small, below] at (1.85,0.3) {base $2$, table and shift};

\node[box] (zA) at (-1.55,-0.45) {scores $z$, one row};
\node[box] (zB) at (1.85,-0.45) {scores $z$, one row};
\draw[a] (zA) -- (-1.55,-1.05);
\draw[a] (zB) -- (1.85,-1.05);

\node[hot] (eA) at (-1.55,-1.7) {$e^{z_i}$\\ exponentiation unit};
\node[box] (kB) at (1.85,-1.7) {$\times\,\log_2 e$\\ constant multiply};
\draw[a] (kB) -- (1.85,-2.3);
\node[blk] (mA) at (-1.55,-2.35) {$m=\max_j z_j$ must finish};
\node[blk] (mB) at (1.85,-2.65) {$m=\max_j z_j$ must finish};
\draw[a] (mA) -- (-1.55,-3.0);
\draw[a] (mB) -- (1.85,-3.25);

\node[cold] (sB) at (1.85,-3.9) {$z_i-m$, split $k$ \vert $f$};
\draw[a] (sB) -- (1.12,-4.5) -- (1.12,-4.75);
\draw[a] (sB) -- (2.58,-4.5) -- (2.58,-4.75);
\node[box] (tbB) at (1.12,-5.25) {$2^{f}$\\ table read};
\node[box] (shB) at (2.58,-5.25) {$2^{k}$\\ shift};
\draw[box, draw=gray!55] (0.22,-5.72) rectangle (3.48,-4.95);
\node[t, anchor=north west, text width=3.4cm, align=left] at (0.22,-5.78)
  {one ROM, one barrel shifter:\\ no $e^{x}$ unit anywhere};
\node[hot] (sA) at (-1.55,-3.65) {$\sum_j(\cdot)$, then divide\\ reciprocal unit};
\node[box] (sumB) at (1.85,-6.25) {integer sum, then\\ $1/d$ and $2^{-k/2}$: table, shift};
\draw[a] (shB) -- (2.58,-6.0);
\draw[a] (tbB) -- (1.12,-6.0);
\draw[a] (sA) -- (-1.55,-4.9);
\node[box] (oB) at (1.85,-7.05) {$a_i$};
\node[box] (oA) at (-1.55,-5.4) {$a_i$};
\draw[a] (oB) -- (1.85,-6.6);
\draw[a] (oA) -- (-1.55,-4.95);
\end{tikzpicture}
```
The two ways to spend an exponential. Shaded boxes are the stages whose hardware is a
function unit; unshaded ones are a read-only memory, a shifter or an adder tree. The dashed
bar sits in both paths: a row maximum cannot be worked around, so neither variant streams
the row through. What the base-2 column buys is the removal of the red, not of the dash.
:::

**LayerNorm stays in the datapath; a BatchNorm in its place would not.** BatchNorm's mean
and variance are constants derived from the training data, so the whole stage is a per-channel
multiply and add, and those compose into the weights and bias of the convolution before it.
LayerNorm is data-dependent: the mean and variance it uses come from the frame in front of it,
at run time, and it folds into nothing. The three recipe configs on record put that fork in
writing.

| Convolution module normaliser | Value | Where it comes from |
| --- | --- | --- |
| Offline Conformer-Transducer recipe | `batch_norm` | `V-05-20` |
| Streaming Conformer-Transducer recipe | `layer_norm` | `V-05-26` |
| Streaming FastConformer-Transducer recipe | `layer_norm` | `V-05-41` |

Both streaming configs record LayerNorm, so the mean, the variance and the reciprocal square
root above are in this chapter's hardware list. Had the streaming recipes agreed with the
offline one, this section would be about a constant folded into weights.

> **One figure that is a ratio.** `V-05-36` prints 4 for the streaming Conformer's feed-forward
> expansion factor: the hidden width as a multiple of `d_model`, one multiplier inside one
> sub-layer. It is not a count of sub-layers and it says nothing about how many normalisation
> stages this section must build.

**Requantisation gives these stages their number format.** `V-06-01` is the affine form
$r = S(q - Z)$, scale and integer zero-point, which is what lets a datapath carry an
unsigned integer whose real meaning is somewhere near zero. `V-06-02` is the same idea
applied to a product: $M = (S_1 S_2)/S_3 = 2^{-n} M_0$ with $M_0$ in $[0.5,1)$, so a real
multiply becomes a fixed-point multiply by $M_0$ plus a shift. That is the arithmetic the
base-2 path above already spends, borrowed for its shape; chapter 7 owns the choice of
scales, zero-points and widths.

**The tie rule is what a shift gets wrong.** `V-06-04` records that Brevitas' default
`float_to_int_impl` is `RoundSte` -- `torch.round` with a straight-through estimator (STE --
the backward pass treats the rounding as an identity, so gradients ignore it), and the same
record's note is explicit that the tie behaviour is not evidenced there. It is `V-06-05`:
torch.round is "round half to even", so an exact tie goes to whichever neighbour is even. A
fixed-point pipeline that right-shifts truncates, rounding every value down. The usual repair,
adding $1 \ll (\text{shift}-1)$ before the shift, lands on half away from zero, which is a
third behaviour: the tie either way, away, or to even, three answers from one shift. The rule
a design must copy is the one the framework uses, so the shift needs $M_0$ odd at the
truncated bit -- not merely a nonzero remainder -- and ties must break downward or upward
according to the even neighbour. `V-06-04`'s STE is the training half of that agreement.
Whether the fabric and the framework land on the same bits is a measured question; no record
answers it.

<!-- source: 8.4 reviewed fragment -->

## 8.4 An Hour on the Board: What the Acceptance Gate Has to Catch

The project plan sets two conditions for this build, and they are the plan's own words, not a datasheet's or a paper's: the system must run continuously for at least one hour without hanging, and its board-measured 99th-percentile latency must agree with simulation to within plus or minus ten per cent. Two conditions, because a duration test and a percentile test catch different things.

**Neither test can replace the other.** A hang is a stop-responding-without-stopping failure, and the hour is for the ones that grow: a leak, a queue that drifts, a counter that finally overflows, a timing margin that narrows with heat. A rare fault present from the first minute adds nothing up, so the hour is blind to it. The percentile is the reverse instrument: it measures the shape of the rare case immediately, and it passes a design that stops in hour two. The table holds the symmetry.

| Condition | Catches | Blind to |
| --- | --- | --- |
| One hour without hanging | faults that grow with time | a fault already present, but rare |
| 99th percentile within 10% of simulation | a tail present from minute one | a system that fails later |

**The 99th percentile is chosen over the mean because the product is not an average.** Line the frame latencies up from fastest to slowest; the 99th percentile is the value that 99 of every 100 frames were answered at or below. A user saying a wake word once does not experience a mean. They are answered in time, or they are not, and it is the frames at the back of the line that decide whether the product works. A mean folds one very slow frame into all the fast ones and can stay flattering forever; a percentile does not let the slow frame hide.

**The second condition has two sides, and only one of them exists yet.** The board side is a measurement this book does not have and does not claim. The simulation side is produced before implementation, and `V-04-05` is the registered statement of what such a number is: the Xilinx Power Estimator (XPE -- a spreadsheet power model used before the design exists) says its device models "are extracted from measurements, simulation, and/or extrapolation", and that "Advance specifications are based on simulations only and are subject to change". A pre-implementation estimate is an input to an agreement test, not a result. The numbers that describe a built design come from named reports in a named mode: `report_utilization -file <filename>`, run post-synthesis or post-implementation, prints the exact cell breakdown (`V-04-06`), and the same rule carries to whatever report later prints the latency.

**A gate is no better than how you read your own tools.** `V-01-19` is the datasheet form of the lesson: the rounded marketing figure "1.2K" for digital signal processing (DSP) slices reads as 1,200 where the exact count is 1,248, 4% low, while "256K" reads as 256,000 against an exact 256,200, only 0.08% low. Only the first matters, because a roofline built on 1,200 is 4% optimistic against the silicon. A rounded figure is prose; an exact column is a budget. Every number the gate compares needs the same three questions: which mode produced it, what rounding it prints, and which column of it is admissible as a budget.

**One input to the second condition cannot be closed at the desk.** The simulation's percentile depends on which accelerator the board ships with, and that SKU and its core count are registered as a decision not yet taken; chapter 9 carries it. The condition is well specified today, and open.

**What the gate judges is accuracy, not transcripts.** `V-05-02` fixes the task and metric: isolated-word classification accuracy over one-second clips from a closed label set, explicitly not word error rate (WER -- the share of transcript words that were inserted, deleted or substituted). A wake-word answer is a label, and a label is right or wrong. The two conditions decide when the answer arrives; this record decides what right means.

**Done includes someone else redoing it.** The artifact will be badged against the set registered in `V-07-04`: the IEEE FCCM 2025 (Field-Programmable Custom Computing Machines -- an IEEE symposium) evaluates artifacts for Code/Dataset Available, Evaluated (Functional), Reproducible. A gate that only ever passes once is a measurement nobody can check, so the badge list belongs inside the definition of done, not in submission paperwork.
