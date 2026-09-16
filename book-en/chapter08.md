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

> ### Minimal Mathematics / Prerequisites for this Chapter
>
> - **A count as a product**: taps, dilation and how far back one output reaches are multiplied, not
>   added, and the difference is what sizes a buffer.
> - **Powers of two**: why shifting replaces multiplying only when a factor lands exactly on one.
> - **Logarithm base two as a depth**: the number of halvings a compare tree takes, which is a count
>   of stages, not of items.
> - **Floor and remainder**: how a fixed-point split into an exponent part and a fraction part is
>   read back, and what rounding off that split costs.

---

<!-- source: 8.1 reviewed fragment -->

## 8.1 The Board Has No Microphone: Tracing One Second of Audio

*Where this sits in the chain: the* **Air and microphone** *stage, at its weakest point -- the board
this book targets cannot supply the stage's one input.*

**The board cannot hear you.** The KV260 carrier has no onboard microphone, no audio jack and no audio converter; its own data sheet lists the audio path only as "Audio transmit and receive (I2S) via PMOD audio codec", where I2S (Inter-IC Sound) is the serial link between a converter and the logic, and a PMOD is a module plugging into a two-row header. Nothing is captured until one is bought and fitted. A laptop has a microphone, so a plan written on one reaches the model before it notices this.

**There are two ways in, and they are not the same kind of answer.** The vendor's own part is the Audio Codec I2S PMOD, Digilent SKU 410-379, in connector J2, which the carrier's accessory list records as tested with the smart camera application. That module opens up to a Cirrus CS5343 analogue-to-digital converter (ADC) and a CS4344 digital-to-analogue converter (DAC), 24-bit, stereo, on line inputs and outputs, with input rates up to 108 kHz. Read "line" strictly: a capsule still needs amplification upstream of the board. The other way is a USB microphone on one of the four USB 3.0 Type-A ports the board manual counts, which Linux sees through ALSA (its audio subsystem) as a USB audio class (UAC1/UAC2) device. That route needs no carrier modification, and it leaves conversion, clocking and gain outside the design. Only the first hands a programmable design a stream it can own, so the choice is scope, not wiring.

**Both corpora are stored at 16 kHz, and that settles the input clock.** The Speech Commands paper says each utterance is "stored as a one-second (or less) WAVE format file, with the sample data encoded as linear 16-bit single-channel PCM values, at a 16 KHz rate", and the LibriSpeech corpus page gives the same rate. That second source is the corpus's own distribution page, so it corroborates rather than stands alone, as chapter 1 read it. A frontend at any other rate is wrong before a line of hardware exists. What the pair does not settle sits in the same two records: the codec offers 24-bit stereo (`V-03-03`), the files are 16-bit single-channel (`V-05-11`), and no record fixes where the extra bits and the second channel go.

**The encoder consumes frames, not samples, and no record here fixes the frame rate.** Between the stream and the model the frontend groups samples into overlapping frames and reduces each to a few spectral values, so the path runs on two clocks, and only the first is settled above. How many frames arrive in a second, and how long one encoder step lasts, are not among the records this section draws on, so section 8.1 prints no number for either. The two domains are real whatever fills the second one, and a design that sizes a buffer in samples against a budget in steps is wrong in a way no simulation catches.

**The metric is not a word error rate (WER).** MatchboxNet, the keyword spotter registered here, comes in sizes of 77K, 93K and 140K parameters. Its paper decides how any later number is read: the task is isolated-word classification over a closed set -- 12 or 35 classes, clips of one second or less -- and the quantity is top-1 accuracy in percent. MatchboxNet is not a continuous sequence model, so it has no WER. Accuracy asks whether the right word was chosen; WER counts edits across a transcript. A table that mixes the two compares nothing.

Keyword spotting is the second tier of this book's three-tier cascade: the wake-word listener stays on first, the transcriber joins only when the spotter speaks, and the spotter's whole model fits the fabric's on-chip memory. That fit is why the tier is the always-listening one -- and the tier's cost is the book's own estimate, not a registered record.

> **A passing number is speaker-independent, or it is nothing.** The Speech Commands paper records how the partition is made: `validation_list.txt` and `testing_list.txt` ship with the download, membership follows a hash of the file name, and that name begins with a hashed speaker identifier, so every clip of one speaker lands in one partition. That is what turns the accuracy figure above into a claim about unfamiliar voices. The corpus licence is Creative Commons Attribution 4.0 (CC BY 4.0), over 105,829 utterances, 35 words and 2,618 speakers, so attribution is the whole obligation, and a result can travel with its data.

[Figure 22](#fig-kws-signal-path) puts the path on one line, and it is where the two clocks show.

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

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-03-01` | the carrier lists no onboard microphone, jack or converter; the audio path is I2S via a PMOD codec |
| `V-03-02` | the Audio Codec I2S PMOD (Digilent SKU 410-379) sits in connector J2 and is tested with the smart camera |
| `V-03-03` | that PMOD is a CS5343 ADC and CS4344 DAC, 24-bit stereo, line-level, to 108 kHz |
| `V-03-05` | the carrier exposes four USB 3.0 Type-A ports |
| `V-05-11` | Speech Commands stores one-second clips as 16-bit single-channel PCM at 16 kHz |
| `V-05-10` | LibriSpeech is 16 kHz read English speech, on the corpus's own distribution page |
| `V-05-01` | MatchboxNet's three sizes are 77K, 93K and 140K parameters |
| `V-05-02` | the task is isolated-word classification, 12 or 35 classes, scored as top-1 accuracy, not WER |
| `V-05-08` | the train/test split follows a hashed speaker id, so it is speaker-independent |
| `V-05-07` | the corpus is CC BY 4.0, 105,829 utterances, 35 words, 2,618 speakers |

<!-- source: 8.2 reviewed fragment -->

## 8.2 A Depthwise Convolution Is a Line Buffer With Taps

**Intuition.** A filter that runs along a stream of frames is the same object as a shift
register with taps, and every hardware reader has built one. Hold the recent values of a single
channel in a row of registers, multiply each register by a weight, add the products, and the
result is that channel's filtered value for the newest frame. A trained network changes nothing
about that shape. It picks the weights by training rather than by hand, and it runs a row like
this for every channel at once. The question worth arguing about is what to do when the channels
are also allowed to talk to one another, because that conversation is where the cost sits, and
the answer the field settled on is to split it into two cheaper passes. The convolution section
of Appendix A derives that split from the arithmetic of a filter; this section keeps the storage,
the traffic and the containers, and it assumes the derivation has been read.

**Mechanism.** The separable split is a hardware statement written as a network layer. A depthwise separable convolution replaces one dense filter with two passes. A *depthwise* pass filters each channel on its own, so one filter per channel and no mixing. A *pointwise* pass is a 1 × 1 convolution: one position, all channels in, all channels out, and it does the mixing. The order looks wasteful and the reason for it is arithmetic. In a dense filter every input channel meets every output channel, so a fetched weight is multiplied into many products and a design can hold the weight still while activations stream past. In a depthwise pass a weight belongs to exactly one channel, so far fewer multiply-accumulates (MAC -- one multiplication and one addition fused into one hardware step) arrive per weight fetched, and the fetching becomes the work. The pointwise pass puts the ratio back, because it is dense. So a convolution stack of this kind is two workloads in one layer: the depthwise part is shaped by memory traffic, the pointwise part by arithmetic units, and a machine good at only one of them idles through the other. [Figure 23](#fig-dense-vs-depthwise) draws the two wirings side by side, so the ratio is a count of lines rather than a claim to take on trust.

::: {#fig-dense-vs-depthwise .figure}
```tikz
% The comparison section 8.2's cost argument turns on, drawn rather than described: a dense filter
% connects every input channel to every output channel, a depthwise pass connects each channel to
% itself and to nothing else. Four channels are drawn on each side as a stand-in for any width -- the
% figure is about which wires exist, not how many, and no channel count is claimed here.
\begin{tikzpicture}[
  font=\tiny,
  dot/.style={circle, draw=black!70, fill=black!12, inner sep=1.6pt},
  odot/.style={circle, draw=black!70, fill=black!45, inner sep=1.6pt},
  wire/.style={black!45, line width=0.28pt},
  lone/.style={black!70, line width=0.5pt},
  tick/.style={text=black!70},
  pcap/.style={text=black!62, align=center}]
  % ---- panel A: the dense cross, every pair wired ----
  \foreach \y in {0,1,2,3}{
    \node[dot] (ai\y) at (0,\y*0.5){};
    \node[odot] (ao\y) at (2.1,\y*0.5){};}
  \foreach \i in {0,1,2,3}{\foreach \o in {0,1,2,3}{
    \draw[wire] (ai\i) -- (ao\o);}}
  \node[pcap, anchor=north] at (1.05,-0.42) {dense: every input channel\\meets every output channel};
  \node[tick, anchor=south east] at (-0.12,1.5) {in};
  \node[tick, anchor=south west] at (2.22,1.5) {out};
  % ---- panel B: the depthwise diagonal, each channel to itself ----
  \foreach \y in {0,1,2,3}{
    \node[dot] (bi\y) at (4.2,\y*0.5){};
    \node[odot] (bo\y) at (6.3,\y*0.5){};}
  \foreach \i in {0,1,2,3}{\draw[lone] (bi\i) -- (bo\i);}
  \node[pcap, anchor=north] at (5.25,-0.42) {depthwise: a weight belongs\\to exactly one channel};
  \node[tick, anchor=south east] at (4.08,1.5) {in};
  \node[tick, anchor=south west] at (6.42,1.5) {out};
\end{tikzpicture}
```
The two passes beside each other, so the ratio the section argues about is a count of wires rather than
a sentence: the dense panel is full because every pair is wired, and the depthwise panel is a matching
because a weight there has one channel to serve. A machine built to keep weights still while activations
stream past is efficient on the left panel and idle on the right one.
:::

**The traffic the depthwise part generates is mostly re-reads, and re-reads are a buffer.** What a sliding window reads more than once is the input, not the weights. A hardware design therefore keeps the recent inputs where they can be read cheaply, in a *line buffer* -- storage for the steps a window still needs, so that each new step is written once and read again by every later output whose window covers it. [Figure 24](#fig-depthwise-line-buffer) draws exactly that, and the whole argument of this section is visible in which arrows repeat.

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

Nothing here is priced per frame. Per-frame cost -- MACs, INT8 weight bytes, activation bytes -- is unregistered for every candidate, so this section states the shape and stops.

**Reach is a two-term rule, and it is the only arithmetic this section needs.** *Mechanism.* A window reads the current step and reaches backwards for its history; how far it reaches and how often it moves are set by different knobs.

> **The formula.** $R = (k - 1)\,d + 1$
>
> **The variables.**
>
> - $R$ — the reach: how many input steps one output depends on, counting the current step. A
>   number of steps, so dimensionless until a step is given a duration.
> - $k$ — the tap count: how many samples of the input the window reads. A count of taps.
> - $d$ — the dilation: the spacing between consecutive taps, in input steps. A count of steps.
>   Left a symbol here on purpose, because neither candidate's records register a value for it.
> - $s$ — the stride: how many input steps apart two consecutive outputs start. A count of steps,
>   and deliberately not a term of $R$: it sets how often the buffer is read, never how deep it is.
>   No record fixes its value for either candidate.
> - $1$ — the current step itself, which every window reads. A count, not a measured quantity.
>
> **What it means.** A window takes $k$ taps, and between the first tap and the last there are
> $k - 1$ gaps, each $d$ steps wide, so the distance from the newest tap to the oldest is
> $(k-1)d$ steps. Adding the current step back gives the total number of input steps the output
> rests on. The subtraction and the addition are the same act seen twice: $k - 1$ counts gaps,
> and $+1$ counts the step those gaps hang off. A separate sentence carries the stride, because
> it is a different knob: consecutive outputs start $s$ input steps apart, and $s$ does not
> appear in $R$ at all. With $d = 1$ the rule reproduces what the table prints -- 31 taps
> reaching 30 steps back `V-05-25`, and the other candidate's 9 taps reaching 8 `V-05-40` --
> which is the check that the formula is describing these recipes and not an invented one.
>
> **What it costs.** $R$ is the depth of the line buffer in steps, and $s$ is how fast its
> contents turn over, so a longer tap costs storage while a larger stride costs the same storage
> less often. In silicon the shifting part of that buffer is registers at the word level, and
> the holding part is a BRAM or URAM tile or a few hundred words of LUTRAM, whichever of the three
> containers the capacity table later in this section prices -- though it lists what each holds, and
> no record says which one a short-tap stage should be given. The formula itself is a multiply by a constant and an add; when $d$ is
> a power of two the multiply is a shift, and when $k$ is fixed at compile time the whole
> expression is one number resolved before the design is placed rather than arithmetic done per
> step.
>
> **What it does not say.** Not bytes, and not time. $R$ is counted in steps, and a step becomes
> a wall-clock interval only once the encoder's step period is registered, which chapter 9 does
> and this chapter does not. And $R$ says nothing about how many channels the window must be
> copied across, which is where the storage actually goes: reach is one dimension of a buffer
> whose size needs three.

**The reference keyword network is the small case, and its paper prints it as names.** MatchboxNet is a 1D time-channel separable convolutional network at $C = 64$ channels, and its paper lists three variants with their parameter counts: 77K for `3x1x64`, 93K for `3x2x64`, 140K for `6x2x64`. The name carries the depth and the width, so a reader sees the stack growing in the same place that prices it, and the paper notes that counts of this size fit entirely into on-chip block RAM (BRAM -- on-chip storage) without off-chip access. The other half of the source is the task definition: isolated word classification accuracy on 1-second clips from a closed set of 12 or 35 classes, not a word error rate (WER -- the fraction of transcribed words that are wrong). A design that quotes that accuracy is not quoting transcription.

**Hardware application.** The buffer lives in one of three containers, and the unit must travel with the number. All figures are the device registered as `xczu5ev` / `XCK26`, from document DS890 page 22, Table 23.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| BRAM blocks, 36 kilobit each | 144 | `V-01-05`, tile size `V-01-23` |
| UltraRAM (URAM) blocks, 288 kilobit each | 64 | `V-01-07`, tile size `V-01-23` |
| BRAM and URAM together | 23,616 Kb | `V-01-22` |
| Distributed RAM (LUTRAM) | 3.5 Mb | `V-01-16` |
| Configurable logic block look-up tables (CLB LUT -- the basic logic element) | 117,120 | `V-01-03` |
| CLB flip-flops | 234,240 | `V-01-04` |
| DSP48E2 slices (the multiply-accumulate block of this family) | 1,248 | `V-01-09` |

Every value is quoted in the unit the record prints it in. The datasheet's megabit columns are 1024-based, so a Mb there is 1,024 Kb; the total was fixed precisely because "4 MB" and "4.5 MB" were each defensible under some other reading and neither survives the arithmetic. The three containers are not interchangeable. BRAM and URAM are fixed tiles and are counted together at 23,616 Kb; LUTRAM is built from the look-up tables in the row above it, so it spends logic and is not initialised by the bitstream the way BRAM is, which is why its capacity is not added to that budget. A short-tap depthwise stage that wants a few hundred words at very low latency may be better served by LUTRAM than by a whole 36 Kb tile, and no record here says which. Flip-flops matter to this section for one reason: at the word level the shifting part of a line buffer is registers. Building any of it needs no licence -- the device is supported in the standard Vivado ML Standard flow without one.

<!-- source: 8.3 reviewed fragment -->

**Traceability.** The records this section's prose leans on. The two tables above carry their own
per-row provenance; this note holds the citations that sit in sentences rather than in a row.

| Record | What it establishes here |
| --- | --- |
| `V-05-57` | nothing is registered for any candidate about MACs per frame, weight bytes or activation bytes |
| `V-05-01` | MatchboxNet's three sizes (77K, 93K, 140K parameters) and that a count this size fits in on-chip BRAM |
| `V-05-02` | the task is isolated-word classification on short clips from a closed label set, scored as accuracy rather than a word error rate |
| `V-01-23` | the datasheet's megabit columns are 1024-based, and one BRAM tile is 36 Kb, one URAM tile 288 Kb |
| `V-01-22` | the 23,616 Kb fabric total, unrolled across the unit conventions that left two megabyte readings defensible |
| `V-01-16` | 3.5 Mb of distributed (LUTRAM) capacity, which spends logic and is excluded from the tile budget |
| `V-04-01` | the device is supported in the standard Vivado ML flow with no licence |

## 8.3 Softmax and LayerNorm Without a Floating-Point Unit

**Intuition.** Two stages in every encoder block do work that a multiplier cannot do directly,
and both of them are about proportions rather than about values. Attention ends with a row of raw
scores, one per frame it was allowed to read, and that row has to become shares of a whole before
it can weight anything: this is what a softmax is for, and it is why the operation contains a sum
and a division. A normalising stage keeps each frame's channel values on a scale the next stage
can use, which is why it contains a mean, a spread, and a reciprocal of a square root. The four
operations this section has to build therefore follow from what the two stages are for: an
exponential, a reciprocal, a sum and a square root. Appendix A defines both stages from the
beginning; this section assumes the definitions and supplies the units. A fabric of multipliers,
adders and storage can build all four, and building them is this section. The arithmetic decisions below are design, not
result: no error, rate or resource figure appears here, because none has been measured.

**Mechanism.** Subtracting the row maximum is a correctness step. In real arithmetic, these two
expressions have the same value:

> **The formula.** $\mathrm{softmax}(\mathbf{z})_i = \dfrac{e^{z_i}}{\sum_j e^{z_j}} = \dfrac{e^{z_i - m}}{\sum_j e^{z_j - m}}$, with $m = \max_j z_j$
>
> **The variables.**
>
> - $\mathbf{z}$ — one row of attention scores: one value per position the query may look at.
>   Raw score units, unbounded in both directions before anything is done to them.
> - $z_i$ — the score of one position $i$ in that row. Same units as $\mathbf{z}$.
> - $m$ — the largest value in the row, $\max_j z_j$. Same units as $\mathbf{z}$, and it is a
>   value from the row, not a constant anybody chose.
> - $i$, $j$ — indices of positions inside the row. Counts of positions.
> - $n$ — how many positions the row holds, counting only the ones the mask keeps. A count of
>   positions, and the unit the holding buffer is sized in.
> - $\log_2 n$ — how many times $n$ has to be halved to reach one: the number of levels a pairwise
>   compare tree needs. A count of levels, not of positions.
> - $\sum_j$ — the sum across the whole row: every position the mask allows, not just the one
>   being weighted.
> - $e^{x}$ — the exponential of $x$, the function this section exists to build without a unit.
>
> **What it means.** The two right-hand forms differ by a factor $e^{m}$ that cancels, so on a
> calculator the subtraction shows no gain at all. The gain is in the interval, not the answer.
> Every term of the reduced numerator and denominator now lies in $[0,1]$, so the largest value
> either one can hold is exactly $1$: a fixed-point encoding whose range tops out there holds
> both without a second thought. The unreduced form, exponentiating $z$ directly, cannot say
> what its largest value will be before it has been computed -- and a hardware designer has to
> size a register before runtime, not after.
>
> **What it costs.** The price is order. $m$ exists only after the last score of the row exists,
> so the row must be held in a buffer and a reduction must finish before the first exponential
> begins -- an adder-free tree of pairwise compares, which halves the list at every step. That
> is a stall paid in storage and in serial depth: a row of $n$ scores needs $n$ registers or a
> tile, and $\log_2 n$ levels of compare before any output can start. The blocking point is
> drawn in [Figure 25](#fig-nonlinearity-approx), and both variants there pay it.
>
> **What it does not say.** It does not say the row fits. The buffer this identity requires is
> as wide as the mask allows the row to grow, and chapter 9 is where that width is counted.
> And the $[0,1]$ bound is a statement about the interval, not about precision: how many bits
> below the binary point survive the shift into that interval is a word-width decision this
> formula does not make for anyone.

> **The formula.** $e^{x} = 2^{\,x\log_2 e} = 2^{k}\cdot 2^{f}$, with $k = \lfloor x\log_2 e \rfloor$ and $f = x\log_2 e - k$
>
> **The variables.**
>
> - $x$ — one already-reduced score, the $z_i - m$ of the card above. A non-positive
>   fixed-point number, so $x \le 0$ always, and $e^x$ lands in $(0,1]$.
> - $\log_2 e$ — the change of base from $e$ to $2$, about $1.4427$. A pure number, and in a design
>   it is a literal: a fixed-point approximation of it, one multiply by a value chosen at compile
>   time. No record here fixes how many bits that literal keeps, so the constant is written to the
>   four decimals the argument needs and not further.
> - $x \log_2 e$ — the same exponent rewritten in base 2. Fixed-point, non-positive.
> - $k$ — the integer part of that quantity, $\lfloor x\log_2 e \rfloor$: the floor, so the
>   greatest integer not exceeding it. A signed integer count of doublings.
> - $f$ — what the floor threw away, $x\log_2 e - k$. A fraction in $[0,1)$, and by
>   construction it has fewer significant bits than $x$ did.
> - $2^k$ — the integer-power term. $2^f$ — the fractional-power term, in $[1,2)$.
> - $b$ — how many of $f$'s fraction bits a design keeps. A count of bits, and the lookup table
>   sized in **What it costs** holds $2^b$ entries: the one knob that trades the exponential's
>   accuracy for its storage.
>
> **What it means.** Writing an exponent in base 2 is not a stylistic choice; it is the choice
> that makes the integer part *be a bit position*. A fixed-point number is a bit pattern read as
> $\text{integer}.\text{fraction}$, so taking its floor separates the two halves by cutting the
> pattern at the binary point, and $2^k$ then means "place the value $k$ positions to the left or
> right of where it is". That is what a barrel shifter is: a network of multiplexers that moves
> bits by a variable amount and performs no arithmetic at all. The fraction cannot be handled
> that way, because $2^{0.5}$ is not a bit position -- it is $\sqrt{2}$ -- so it goes to a table
> instead, and the table is affordable only because $f$ has few significant bits left after the
> floor took the rest. Each of those bits indexes one stored entry, written once at compile time
> and never computed. The exponential therefore survives as one constant multiply, one read and
> one shift, and the transcendental part of it lives in a memory somebody filled in at build time
> rather than in a circuit that evaluates anything at run time.
>
> **What it costs.** A constant multiply for $\log_2 e$ -- one DSP slice, or wiring and no slice
> at all if the literal is chosen as a sum of powers of two. A read-only memory of $2^b$ entries
> where $b$ is the number of fraction bits kept, so the table's size is exponential in the very
> precision it buys, and that trade is the whole design decision. One variable shift, which is a
> shifter and not a multiplier. Whether a given $b$ fits a tile is arithmetic on the tile the
> device register names and on the entry width this book does not choose, so no fit is claimed
> here.
>
> **What it does not say.** It does not say the result is $e^x$. It says the result is what a
> fixed-point $\log_2 e$ and a $b$-bit table return, and the error against the true exponential
> is the sum of three approximations this formula deliberately hides: the literal, the truncation
> of $f$, and the table's own entries. No record in this repository registers that error for any
> candidate, so this book prints none -- and a designer who reads this card as exact arithmetic
> has just made the mistake the card exists to prevent.

A reciprocal square root is the same trick with one snag:

> **The formula.** $\dfrac{1}{\sqrt{y}} = 2^{-k/2}\cdot\dfrac{1}{\sqrt{f}}$, where $y = 2^{k}f$
>
> **The variables.**
>
> - $y$ — a LayerNorm variance plus the small constant added to keep its square root away from
>   zero. A squared quantity in the units of the normalised channel values, and strictly positive
>   because of that added constant.
> - $k$ — the exponent of $y$ when $y$ is written in base 2: the position of its leading bit
>   relative to the binary point. A signed integer count of doublings.
> - $f$ — the significand, the part of $y$ left after the exponent is taken out, so $f$ is in
>   $[1,2)$. A fixed-point fraction, not the same $f$ as the exponential card above: there the
>   remainder sat below the point, here it sits above it.
> - $2^{-k/2}$ — the exponent half, which is the $\sqrt{\;}$ and the reciprocal both, applied to
>   the power-of-two part. A shift.
> - $1/\sqrt{f}$ — the significand half, which cannot be a shift because $f$ is not an integer.
>   A table read.
>
> **What it means.** A square root divides exponents by two and a reciprocal negates them, so
> taking $1/\sqrt{\;}$ of a base-2 number multiplies its exponent by $-1/2$ and leaves the
> significand to be handled separately. The exponent half is wiring. The significand half is a
> function of a value confined to $[1,2)$, which is exactly the interval a table covers cheaply:
> few input bits, one stored output per combination of them.
>
> **What it costs.** One leading-one detector to find $k$, a shift by $-k/2$, and a read-only
> memory indexed by the bits of $f$. No divider and no square-root unit, which is the point of
> the identity: a divider would be iterative, would take a variable number of cycles, and would
> have to be pipelined or hand-held. The softmax denominator reaches its reciprocal the same way.
>
> **What it does not say.** It does not say the shift is clean, and this is the snag the identity
> hides. A halved integer exponent is a shift only when $k$ is even. An odd $k$ leaves a factor
> $\sqrt{2}$ behind, and a plain shift drops it silently: the output comes back wrong by that
> factor and nothing in the datapath reports it, because nothing downstream knows which parity
> the shift assumed. The cheapest fix is an odd flag taken from
> the lowest bit of $k$ that selects a correction entry from the same table; a second table needs
> no flag at all. And the formula does not say what happens at $y = 0$, which is why the constant
> added to the variance is load-bearing rather than tidy: without it, $k$ is undefined for the
> degenerate case and the shift has no value to move.

[Figure 25](#fig-nonlinearity-approx) puts the two routes side by side. Look at what each path
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

**Hardware application.** LayerNorm stays in the datapath; a BatchNorm in its place would not. BatchNorm's mean
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

> **One figure that is a ratio.** The streaming Conformer's config prints 4 for its feed-forward
> expansion factor: the hidden width as a multiple of `d_model`, one multiplier inside one
> sub-layer. It is not a count of sub-layers and it says nothing about how many normalisation
> stages this section must build.

**Requantisation gives these stages their number format.** An integer stands for a real
number by an affine map, and a product of two such integers is put back into an integer
format by one multiplier. Both are one idea applied twice, so one card carries both forms.

> **The formula.** An integer stands for a real number by an affine map, $r = S(q - Z)$
> (V-06-01), and a product of two integers is requantised by the multiplier
> $M = \dfrac{S_1 S_2}{S_3} = 2^{-p} M_0$ (V-06-02), with $M_0$ in $[0.5, 1)$: the real
> multiply becomes a fixed-point multiply by $M_0$ followed by a shift of $p$ places.
>
> **The variables.**
>
> - $r$ — the real number a stored integer stands for. Units of the quantity being carried.
> - $S$ — the scale: how much one integer step counts in real units. A positive real.
> - $q$ — the stored integer, the quantity the datapath actually carries. Integer units.
> - $Z$ — the zero-point: the integer whose real value is zero, which is what lets a narrow
>   unsigned integer mean a real number near zero. Integer units.
> - $S_1$, $S_2$, $S_3$ — the scales of the first operand, the second operand and the
>   output. The paper fixes the first operand as the weights and the second as the
>   activations (V-06-02), so $S_1$ is the weight scale and $S_2$ the activation scale.
> - $M$ — the requantisation multiplier, a ratio of three scales. It is a constant: the
>   number the datapath multiplies by, not the multiplier unit that performs the multiply.
> - $p$ — the shift count, the non-negative integer in the $2^{-p}$ factor. The paper writes
>   $n$; renamed here because $n$ already means a softmax row length earlier in this section.
> - $M_0$ — the mantissa, the part of $M$ in $[0.5, 1)$ a fixed-point multiplier can carry.
>   The paper's example word lengths are int16 and int32 (V-06-02).
>
> **What it means.** The affine form is what lets a datapath carry an unsigned integer whose
> real meaning is somewhere near zero: the zero-point says which integer means zero, and the
> scale says what each step is worth. The multiplier form is the same idea applied to a
> product: because $M = S_1 S_2 / S_3$ and $M = 2^{-p} M_0$, forming the product, scaling it
> and requantising it collapse into one fixed-point multiply by $M_0$ and one shift of
> $p$ places. That is the arithmetic the base-2 path above already spends, borrowed for its
> shape.
>
> **What it costs.** The multiplier is only as accurate as the word length that carries it:
> at int32 the integer nearest to $2^{31} M_0$ is always at least $2^{30}$ -- at least
> $30$ bits of relative accuracy (V-06-02). The fabric cost of that multiply and shift is
> not registered.
>
> **What it does not say.** It does not say what the three scales are worth: the formula
> relates them but nothing here chooses them, and the choice is what determines the word
> widths. It does not say which operand is which, either: the paper fixes the first operand
> as the weights and the second as the activations, so swapping that reading swaps $S_1$ and
> $S_2$ and changes every $M$ this section will spend.

**The tie rule is what a shift gets wrong.** Brevitas' default `float_to_int_impl` is
`RoundSte` -- `torch.round` with a straight-through estimator (STE -- the backward pass treats
the rounding as an identity, so gradients ignore it). Naming the operator does not settle a
tie, because the tie rule is a property of `torch.round` and not of the wrapper around it, and
the framework's source says nothing about which way it goes. So the tie rule has to be read off
the rounding function itself: torch.round is "round half to even", which sends an exact tie to
whichever neighbour is even. A
fixed-point pipeline that right-shifts truncates, rounding every value down, so the tie of a
right shift becomes the lower neighbour. The usual repair adds half a least-significant bit
before the shift: a $1$ at the top of the tail the shift drops, written $1 \ll (\text{shift}-1)$
where $\text{shift}$ is the number of places dropped. That repair has a definite direction,
and it is not away from zero: at $\text{shift} = 1$ the idiom maps $-3 \to -1$, $-1 \to 0$,
$1 \to 1$ and $3 \to 2$, so a half-way value rises toward positive infinity on both sides of
zero -- the label "half away from zero" fits the positive ties, the negative ones rise to the
larger (less negative) neighbour instead. Three tie behaviours from one shift, then:
truncation rounds down, the add-one repair rounds toward $+\infty$, and round-to-even sends
a tie to whichever neighbour is even. The rule
a design must copy is the one the framework uses, so the shift needs $M_0$ odd at the
truncated bit -- not merely a nonzero remainder -- and ties must break downward or upward
according to the even neighbour. The estimator is the training half of that agreement.
Whether the fabric and the framework land on the same bits is a measured question; no record
answers it.

**Traceability.** The records this section's prose leans on.

| Record | What it establishes here |
| --- | --- |
| `V-05-36` | the streaming Conformer's feed-forward expansion factor is 4, a ratio against `d_model` rather than a count of sub-layers |
| `V-06-01` | the affine mapping of integers to reals, $r = S(q - Z)$, which is what lets an unsigned integer mean a real number near zero |
| `V-06-02` | the same paper's equations 4 to 6, which turn a real multiply into a fixed-point multiply and a shift |
| `V-06-04` | Brevitas' default rounding operator is `torch.round` under a straight-through estimator, with no tie rule evidenced in it |
| `V-06-05` | `torch.round` breaks an exact tie half to even |

<!-- source: 8.4 reviewed fragment -->

## 8.4 An Hour on the Board: What the Acceptance Gate Has to Catch

The project plan sets two conditions for this build, and they are the plan's own words, not a datasheet's or a paper's: the system must run continuously for at least one hour without hanging, and its board-measured 99th-percentile latency must agree with simulation to within plus or minus ten per cent. Two conditions, because a duration test and a percentile test catch different things.

**Neither test can replace the other.** A hang is a stop-responding-without-stopping failure, and the hour is for the ones that grow: a leak, a queue that drifts, a counter that finally overflows, a timing margin that narrows with heat. A rare fault present from the first minute adds nothing up, so the hour is blind to it. The percentile is the reverse instrument: it measures the shape of the rare case immediately, and it passes a design that stops in hour two. The table holds the symmetry.

| Condition | Catches | Blind to |
| --- | --- | --- |
| One hour without hanging | faults that grow with time | a fault already present, but rare |
| 99th percentile within 10% of simulation | a tail present from minute one | a system that fails later |

**The 99th percentile is chosen over the mean because the product is not an average.** Line the frame latencies up from fastest to slowest; the 99th percentile is the value that 99 of every 100 frames were answered at or below. A user saying a wake word once does not experience a mean. They are answered in time, or they are not, and it is the frames at the back of the line that decide whether the product works. A mean folds one very slow frame into all the fast ones and can stay flattering forever; a percentile does not let the slow frame hide.

**The second condition has two sides, and only one of them exists yet.** The board side is a measurement this book does not have and does not claim. The simulation side is produced before implementation, and the power-estimator guide is what states the standing of such a number: the Xilinx Power Estimator (XPE -- a spreadsheet power model used before the design exists) says its device models "are extracted from measurements, simulation, and/or extrapolation", and that "Advance specifications are based on simulations only and are subject to change". A pre-implementation estimate is an input to an agreement test, not a result. The numbers that describe a built design come from named reports in a named mode: `report_utilization -file <filename>`, run post-synthesis or post-implementation, prints the exact cell breakdown, and the same rule carries to whatever report later prints the latency.

**A gate is no better than how you read your own tools.** The device's own data sheet is where the lesson starts: the rounded marketing figure "1.2K" for digital signal processing (DSP) slices reads as 1,200 where the exact count is 1,248, 4% low, while "256K" reads as 256,000 against an exact 256,200, only 0.08% low. Only the first matters, because a roofline built on 1,200 is 4% optimistic against the silicon. A rounded figure is prose; an exact column is a budget. Every number the gate compares needs the same three questions: which mode produced it, what rounding it prints, and which column of it is admissible as a budget.

**One input to the second condition cannot be closed at the desk.** The simulation's percentile depends on which accelerator the board ships with, and that SKU and its core count are registered as a decision not yet taken; chapter 9 carries it. The condition is well specified today, and open.

**What the gate judges is accuracy, not transcripts.** The spotter's own paper fixes the task and the metric: isolated-word classification accuracy over one-second clips from a closed label set, explicitly not word error rate (WER -- the share of transcript words that were inserted, deleted or substituted). A wake-word answer is a label, and a label is right or wrong. The two conditions decide when the answer arrives; that paper decides what right means.

**Done includes someone else redoing it.** The artifact will be badged against the set the IEEE FCCM 2025 (Field-Programmable Custom Computing Machines -- an IEEE symposium) awards for artifact evaluation: Code/Dataset Available, Evaluated (Functional), Reproducible. A gate that only ever passes once is a measurement nobody can check, so the badge list belongs inside the definition of done, not in submission paperwork.

**Traceability.** The records this section's prose leans on.

| Record | What it establishes here |
| --- | --- |
| `V-04-05` | the power estimator is a pre-design and pre-implementation tool, and its models come from measurements, simulation or extrapolation |
| `V-04-06` | the named report command, and the modes it must be run in, that produce an exact cell breakdown |
| `V-01-19` | the datasheet prints 1.2K DSP slices against an exact 1,248, and 256K logic cells against 256,200 |
| `V-05-02` | the task is isolated-word classification on short clips from a closed label set, scored as accuracy rather than a word error rate |
| `V-07-04` | the reproducibility badges the symposium's artifact evaluation awards |
