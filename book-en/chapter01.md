# Voice Processing Pipelines and Real-Time Constraints

> *Objective: Understand continuous streaming audio processing fundamentals, real-time physical latency constraints, and why edge voice applications inherently execute at batch size one ($batch=1$).*

---

> ### Minimal Mathematics / Prerequisites for this Chapter
> 
> - **Discrete Fourier Transform (DFT)**: Spectral decomposition from time to frequency domain.
> - **Time-Frequency Uncertainty Principle (Heisenberg-Gabor)**: Temporal vs. spectral resolution trade-off.
> - **Non-linear Mel Scale**: Auditory psychoacoustic pitch perception modeling.

---

## The whole machine, before any of its parts

Every section that follows makes one argument: a streaming voice system is not a slow vision
system, it is a different measurement problem. That argument is easier to follow with the machine
already in view, so the view comes first. [Figure 4](#fig-ch1-pipeline-contract) is the version this
book keeps returning to. Its stages carry the same names, in the same order, as the preface's map,
and each box is labelled with the chapters that work inside it.

Those labels are printed rather than described on purpose. The book's chapter order is a building
order, not a viewing order: chapter 4 is about the fabric but chapter 4 comes after the front-end
chapters because a reader needs a frame before a place to put it. A reader who loses the thread
anywhere in the volume can therefore ask one question to get back, and the answer is under a box:
**which stage is this?**

::: {#fig-ch1-pipeline-contract .figure}
```tikz
% One frame's whole route, drawn as a set of contracts: what crosses each boundary, what state has
% to survive between frames, and where the deadline bites. Stage names match the preface verbatim,
% and so do the chapter labels under the boxes, so the two figures cannot drift apart.
\begin{tikzpicture}[
  font=\scriptsize,
  stg/.style={draw, align=center, inner sep=3pt, minimum width=1.75cm, minimum height=9mm},
  mob/.style={stg, fill=black!7},
  art/.style={text=black!62, align=center, inner sep=0pt, text width=1.85cm, font=\tiny},
  own/.style={text=black!55, align=center, inner sep=0pt, text width=1.9cm, font=\tiny},
  mem/.style={draw, densely dashed, rounded corners=1.5pt, align=center, inner sep=3pt,
              text width=4.2cm, minimum height=6.5mm, text=black!75},
  arr/.style={-{Stealth[length=1.8mm]}, semithick},
  par/.style={-{Stealth[length=1.4mm]}, black!55, thin, densely dashed}]
\node[stg] (s1) at (0,0) {Air and\\ microphone};
\node[stg] (s2) at (2.15,0) {Sample\\ stream};
\node[stg] (s3) at (4.3,0) {DSP\\ front end};
\node[mob] (s4) at (6.45,0) {Model};
\node[mob] (s5) at (8.6,0) {Fabric\\ logic};
\node[mob] (s6) at (10.75,0) {Output\\ and latency};
\draw[arr] (s1) -- node[art, midway, above=1.2mm] {samples} (s2);
\draw[arr] (s2) -- node[art, midway, above=1.2mm] {a frame, then a hop} (s3);
\draw[arr] (s3) -- node[art, midway, above=1.2mm] {a fixed feature vector} (s4);
\draw[arr] (s4) -- node[art, midway, above=1.2mm] {activations} (s5);
\draw[arr] (s5) -- node[art, midway, above=1.2mm] {a decision} (s6);
\node[own, anchor=north] at ($(s1.south)+(0,-1.3mm)$) {ch. 6\\ ch. 8};
\node[own, anchor=north] at ($(s2.south)+(0,-1.3mm)$) {ch. 4\\ ch. 8};
\node[own, anchor=north] at ($(s3.south)+(0,-1.3mm)$) {ch. 1\\ ch. 6};
\node[own, anchor=north] at ($(s4.south)+(0,-1.3mm)$) {App. A\\ ch. 7\\ ch. 9};
\node[own, anchor=north] at ($(s5.south)+(0,-1.3mm)$) {ch. 4, 5\\ ch. 8};
\node[own, anchor=north] at ($(s6.south)+(0,-1.3mm)$) {ch. 2, 3\\ ch. 10};
\node[mem] (m1) at ($(s2.south)!0.5!(s3.south)+(0,-1.5cm)$)
  {the sliding sample window\\ held between frames, moved by a hop};
\node[mem] (m2) at ($(s4.south)!0.5!(s5.south)+(0,-1.5cm)$)
  {the left context the model still needs\\ keys and values, block by block};
\draw[par] (m1.north) -- ($(s2.south)!0.5!(s3.south)$);
\draw[par] (m2.north) -- ($(s4.south)!0.5!(s5.south)$);
\coordinate (dl) at ($(s3.north west)+(0,-3.2cm)$);
\coordinate (dr) at ($(s6.north east)+(0,-3.2cm)$);
\draw[black!55, thin] (dl) -- ++(0,-2.5mm) (dr) -- ++(0,-2.5mm)
  ($(dl)+(0,-2.5mm)$) -- ($(dr)+(0,-2.5mm)$);
\node[art, text width=6.6cm] at ($(dl)!0.5!(dr)+(0,-5.2mm)$)
  {one frame period: the same deadline, at every stage, on both boards};
\end{tikzpicture}
```
The two dashed boxes are the difference between this machine and the one a photograph comes from.
A picture arrives complete and needs no memory of the last one; a frame arrives into a window that
has to be kept, and a model that reads history has to keep that too, block after block, for as long
as the board is powered. Carrying state between frames, and not the size of the arithmetic, is what
separates the two designs -- which is why the sliding window of section 1.2 and the ring buffer of
chapter 9 are one idea seen at two depths in the same chain.
:::

**What crosses each boundary.** Each stage hands the next one an object of a fixed shape, and a
fixed shape is what makes a stage replaceable. That is the whole reason a move like the one in this
book can be made one stage at a time instead of all at once.

- **Air to samples.** A microphone and its encoder turn pressure into numbers at a steady rate. The
  frontend used throughout this book works at the rate the corpora it trains against are stored at,
  which is a documented match rather than a tuned optimum, and section 1.2 keeps the records.
- **Samples to a frame.** Numbers arrive one at a time and analysis needs them in groups, so the
  stream is cut into overlapping frames. The frame and the step between frames are the first two
  deadlines any design inherits.
- **A frame to features.** Frequencies, then a perceptual scale, then a logarithm. The front end's
  job is to reduce a frame to a fixed-length list, and every choice in section 1.3 is about how much
  of that reduction to do, and when.
- **Features to scores.** A trained network reads the list and returns one number per thing it
  recognises. This stage is arithmetic to this book and nothing more, which is what Appendix A is
  for, and what chapter 7 is about when it decides how narrow that arithmetic may be.
- **Scores to a decision.** A winner is chosen and reported. The question stops being what the
  network computed and becomes how long after the sound the answer arrived.

**What each stage owes the clock.** The chapters are in the diagram; what belongs in prose is what
each stage has to promise about time, because that promise, and not accuracy, is what this book
sizes a design against.

- **Air and microphone** owes bits at the rate its encoder claims, forever, with no gap that has to
  be explained later. chapter 8 starts on a board that cannot promise this.
- **Sample stream** owes a frame that is complete by its own deadline, with no copy along the way
  that can block. chapter 4 is where a blocking copy stops being invisible.
- **DSP front end** owes a finished feature vector inside one frame period, because a front end that
  runs long does not delay one frame, it delays every frame after it. chapter 1 does this arithmetic
  and chapter 6 wires it.
- **Model** owes a fixed count of reads and multiplies per frame, so that the stages after it can be
  sized rather than guessed at. Appendix A counts them and chapter 7 decides their width.
- **Fabric logic** owes a clock period that closes, and a design that finishes one frame per frame
  at that period. chapter 4, chapter 5 and chapter 8 are about what that costs in cells.
- **Output and latency** owes a measurement taken from the microphone rather than from the last
  function call, because the two differ by everything upstream. chapter 2, chapter 3 and chapter 10
  are about not reporting the shorter one.

> **One inherited quantity.** This section prints a single rate, and it is inherited rather than
> chosen: the frontend works at 16 kHz because that is the storage rate both training corpora
> register -- the Speech Commands paper for one, the LibriSpeech distribution page for the other. Both
> describe how training audio is stored. Neither measures a frontend, and neither says 16 kHz is the
> right bandwidth for keyword spotting, so this book cites the match as a constraint the data imposes
> and not as a result anybody reached.


**Traceability.** The records behind this section's one rate.

| Record | What it establishes here |
| --- | --- |
| `V-05-11` | the Speech Commands storage rate, 16 kHz |
| `V-05-10` | the LibriSpeech storage rate, 16 kHz |


## 1.1 Intuition: Fundamental Divergence Between Computer Vision and Voice AI

A photograph is a finished object. A sound is a process that has not finished yet.

That difference explains most of this book. Everything in it -- the frame period, the
buffer, the choice of hardware -- grows out of the fact that an image arrives whole and
audio arrives in pieces.

Consider what a model does with a picture. One picture contains everything the model needs.
Nothing that happens to a second picture changes the first one, so the two can be put
together and computed at the same time. Grouping inputs like this is called **batching**,
and the number of inputs in the group is the **batch size**. A graphics processing unit
(GPU -- many simple arithmetic lanes driven in lockstep) does one large calculation much
better than eight small ones, so batching is close to free performance. The only thing the
group costs is patience, and nobody is waiting for a photograph.

Audio is the opposite case. The input does not arrive complete; it arrives as a continuous
stream of samples and it keeps arriving. To batch eight frames, the system must hold the
first frame back until the eighth has been recorded. **Latency** is the time between a
sound happening and the system knowing about it, so in a streaming task batching is not
free. It is bought directly with latency.

The exchange is short enough to write down. If a new frame is produced every $T_h$ seconds,
a batch of $B$ frames makes the first one wait $(B-1)\,T_h$. With the frame period used
throughout this book, 10 ms, a batch of eight adds 70 ms. That number is arithmetic on a
design choice, not a measurement, and section 1.2 explains where the 10 ms comes from. For a
keyword spotter, 70 ms is the difference between feeling immediate and feeling slow. This is
why the objective of this chapter names $batch=1$: an edge voice system that answers a
person cannot group its inputs, so the hardware question is not "how do we compute a large
batch faster" but "how do we compute one small frame fast, every ten milliseconds,
forever".

Three smaller differences follow from the same fact, and each one becomes a hardware
requirement later in the book.

**There is no natural end.** An image has a height and a width. A stream has neither, so a
streaming program can never see its whole input. It must carry the past forward in **state**:
a fixed amount of memory holding what the next frame will need. In chapter 4 this becomes a
question about how much on-chip memory a design spends, which is a sharper question than
"how many arithmetic units are there".

**Consecutive frames mostly repeat.** Speech changes slowly next to the rate at which a
useful frame can be taken, so the frames used in this book overlap: of the 400 samples in a
frame, 240 were already present in the frame before it. Recomputing those 240 every time is
wasted work, which is why a streaming program keeps a moving window instead of restarting
from the recording. In hardware the overlap is an opportunity: a design that never needs the
discarded part again can be built around a buffer whose read and write positions simply
travel around a fixed circle.

**The arrival rate is not negotiable.** A microphone does not slow down when the processor is
busy. In vision a full queue means the job finishes late. In audio a full queue means
samples are dropped, and a dropped sample cannot be recovered later. Chapter 4 names the
mechanism that pushes this problem back toward the source **back-pressure**, meaning simply
refusing the next item because the current one is not finished. The intuition is enough for
now: the frame period is a deadline, not a suggestion.

The consequence is a shift in what "fast" means, and it is worth stating before any
mathematics. A vision accelerator is judged by throughput, which is images per second. A
streaming voice accelerator is judged first by whether it produces one frame of output
inside one frame period, again and again, and only then by how much energy each frame costs.
The first reason a GPU is not obviously the right machine for this job is not that it is
slow. It is that its speed is quoted in a quantity this task does not use. Chapter 3 develops
that argument with measurements of what happens to a single-instruction-multiple-thread
(SIMT -- one instruction issued to many data lanes at once) processor when there is only one
frame to work on.

## 1.2 The Streaming Audio Preprocessing Pipeline

This section follows the data through the reference implementation in
`chapter01/exp_01_streaming_audio_pipeline.py`, stage by stage. The stages are waveform, sliding ring
buffer, windowing, STFT, Mel filterbank, log compression. Six names in a row read like a syllabus, and
they are not one: each stage exists because the stage before it left a problem that the next piece of
arithmetic cannot proceed without, and the problems are not a matter of taste.

- Pressure is a continuing thing and a computer holds only numbers, so the air is **sampled** at a
  steady rate.
- The stream has no end and a frequency analysis needs a finite group of numbers to hold still and
  work on, so the pipeline takes a fixed-size **buffer** and slides it forward a little at a time.
- Sliding gives each frame hard ends, and a sudden edge looks, to any frequency analysis, like very
  high frequency content that was never in the room, so each frame is **faded** before it is read.
- A fade spends the frame's edges, which is where some of its information was, so consecutive frames
  are made to **overlap** and the analysis is taken **once per frame** rather than once per hop.
- One faded frame still has to be turned into pitch content, which is the question the **STFT**
  answers, $N$ times over for $N$ candidate rates.
- Two hundred and fifty-seven separate answers is more than a keyword spotter can use, and they are
  spaced evenly in hertz where hearing is not, so they are collapsed into eighty **Mel bands**.
- Band energies span decades and a later stage that adds them would be dominated by whichever band
  happened to be loudest, so each energy is replaced by its **logarithm**.

All six live inside the box labelled "DSP front end" in
[Figure 4](#fig-ch1-pipeline-contract), which draws the whole machine at one frame's worth of time and
marks the two places a design has to remember something between frames -- the first of them being the
buffer that the second stage of this list is about.

**Waveform.** Sound is captured as a sequence of numbers measuring air pressure at even time
intervals. The intervals follow from the **sampling rate**, which is how many numbers are
taken per second. The reference frontend uses 16,000 samples per second, so one sample
arrives every 62.5 microseconds and a 25 ms frame holds 400 of them. That rate is a **design
parameter, not a fact about the world**: it is written in the `AudioConfig` defaults of the
experiment, and no measurement chose it. What was missing until now was any record of why
16,000 rather than some other number, and two records close that gap. The Speech Commands dataset
paper says each utterance is "stored as a one-second (or less) WAVE format file, with the sample
data encoded as linear 16-bit single-channel PCM values, at a 16 KHz rate". The LibriSpeech corpus
page describes 1000 hours of 16 kHz read English speech. Those two sources are not equally strong:
the first is a paper, the second is the distribution page of the corpus it describes, and this
project's own source hierarchy (`docs/WEB_SEARCH_PROTOCOL.md` section 2) ranks a page of that kind
as corroborating rather than admissible on its own. So the justification here is the pair, and it is worth naming
exactly what the pair supports. Both corpora that the chapter 5 models train on are stored at
16,000 Hz, which is why a frontend that handed a model a different rate would be wrong before
any hardware is chosen. That is a documented match, not a derived optimum, and the two are
different claims. Nobody has swept the rate against recognition accuracy here, and the number
in the config would not move if the sweep said it should.

**Sliding ring buffer.** The pipeline inspects 400 samples at a time and moves forward by 160
samples per step. A program that recomputes each frame from the original recording re-reads
the 240 samples it has already seen. Instead the implementation keeps a single buffer of 400
numbers: it shifts the contents up by 160 places, writes the 160 new samples at the end, and
computes on the buffer. The important part is what a shift costs. In software it is a loop
over memory, and in hardware it can be free, because a real ring is a memory with two
counters that move around a fixed circle. Nothing moves; only the reading order changes. That
difference between a loop and a counter is one of the clearest examples of what porting to an
FPGA actually buys.

[Figure 5](#fig-ch1-ring-buffer) draws that difference, because it is the one claim in this section
that a reader cannot check from the prose -- "a loop" and "two counters" look like two ways of saying
the same thing until the two pictures are side by side.

::: {#fig-ch1-ring-buffer .figure}
```tikz
% Why a ring buffer is free in hardware and a loop in software -- the same 400-sample window, the
% same hop of 160, drawn two ways. Panel (a) is what the reference code does: the 240 surviving
% samples are physically copied to new addresses every frame, which is a loop over memory. Panel (b)
% is what a real ring does: the samples never move; two counters travel around a fixed circle, and
% the only thing that changes is the reading order. The arcs are drawn in true proportion -- the
% written block is 160/400 of the circle (144 degrees) and the kept block is 240/400 (216 degrees).
% One unit (cm). Style names are drawn from the set the rest of the book already compiles with.
\begin{tikzpicture}[
  font=\tiny,
  blk/.style={draw=black!70, thin, align=center, inner sep=1pt, minimum height=6.2mm},
  gone/.style={blk, fill=black!4, text=black!55},
  kept/.style={blk, fill=black!20},
  live/.style={blk, fill=black!48, text=black!85},
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ann/.style={font=\tiny, text=black!66, align=center, inner sep=0pt},
  annt/.style={font=\tiny, text=black!66, align=left, inner sep=0pt},
  ar/.style={-{Stealth[length=1.4mm]}, black!62, thin},
  cp/.style={-{Stealth[length=1.4mm]}, black!72, semithick},
  hd/.style={-{Stealth[length=1.6mm]}, black!78, thick},
  fl/.style={font=\tiny, text=black!60}]

% ================= (a) software: the data moves =================
\node[ttl, anchor=west] at (0,3.62) {(a) what the code does:\\the samples are copied};
\node[fl, anchor=east] at (-0.08,2.86) {frame $\ell$};
% frame l: oldest 160 (about to be dropped) + newest 240 (about to be kept)
\node[gone, minimum width=1.6cm] at (0.80,2.86) {oldest $160$};
\node[kept, minimum width=2.4cm] at (2.80,2.86) {newest $240$};
\node[fl, anchor=east] at (-0.08,1.56) {frame $\ell\!+\!1$};
% frame l+1: the 240 have moved down to earlier addresses; 160 new land at the end
\node[kept, minimum width=2.4cm] at (1.50,1.56) {the same $240$, moved down};
\node[live, minimum width=1.6cm] at (3.50,1.56) {new $160$};
% the copy: the kept block physically changes address (drawn in the gap between the rows)
\draw[cp] (2.55,2.55) .. controls (1.95,2.22) and (1.68,2.06) .. (1.50,1.90);
\node[annt, text=black!72] at (2.78,2.12) {copied};
% the drop: the oldest block leaves the buffer entirely, exiting down-left into the margin
\draw[ar] (0.45,2.55) -- (0.05,1.16);
\node[fl, anchor=north east] at (0.30,1.12) {dropped};
% the write: new samples enter the right edge of the new block from the margin
\draw[ar] (4.92,2.86) .. controls (4.92,2.10) and (4.70,1.72) .. (4.34,1.60);
\node[fl, anchor=west] at (4.98,2.86) {written};
\node[annt, anchor=west] at (0.05,0.72)
  {a loop over memory: $240$ reads and $240$ writes, every frame};

% ================= (b) hardware: only the counters move =================
\begin{scope}[shift={(9.85,2.02)}]
  \node[ttl, anchor=west] at (-3.60,1.62) {(b) what the hardware does:\\the samples stay put};
  % donut: written 160/400 = 144 deg, kept 240/400 = 216 deg, one unit (cm), start at top, clockwise
  \def\R{1.45}\def\ri{0.62}
  \fill[black!48] (0,0) -- (90:\R) arc (90:-54:\R) -- cycle;
  \fill[black!20] (0,0) -- (-54:\R) arc (-54:-270:\R) -- cycle;
  \fill[white] (0,0) circle (\ri);
  \draw[black!70, thin] (90:\R) arc (90:-270:\R);
  \draw[black!70, thin] (90:\ri) arc (90:-270:\ri);
  \draw[black!55, thin] (90:\ri) -- (90:\R);
  \draw[black!55, thin] (-54:\ri) -- (-54:\R);
  \draw[black!55, thin] (-270:\ri) -- (-270:\R);
  % arc labels at their true mid-angles
  \node[font=\tiny, text=black!85] at (18:1.04) {$160$};
  \node[font=\tiny, text=black!70] at (-162:1.04) {$240$};
  % the write head sits on the top boundary; it advances by one hop and nothing else moves
  \fill[black!80] (90:\R) circle (0.05);
  \node[fl, anchor=south east] at (96:1.50) {write head};
  \draw[hd] (78:1.74) arc (78:-54:1.74);
  \node[fl, anchor=west] at (0:1.80) {advance by $160$};
  % the two counters, drawn as the only state the buffer carries
  \node[font=\tiny, text=black!72, align=center] at (0,0) {two\\counters};
  \node[ann] at (0,-1.86) {a write counter and a read counter,\\
    each moved forward by $160$ and wrapped at $400$};
  \node[ann, text=black!72] at (0,-2.44) {no sample is read or written\\because it moved location};
\end{scope}
\end{tikzpicture}
```
The two panels are the same window and the same hop. In panel (a) the surviving $240$ samples change
address every frame -- that is a loop, and it is what the reference implementation literally does -- so
the cost of a shift is $240$ reads and $240$ writes. In panel (b) the samples are bolted to fixed
addresses and never move; a write counter and a read counter step forward by $160$ and wrap around at
$400$, and the frame boundary is wherever those two counters happen to point. The proportions are the
real ones: the written block is $160/400$ of the circle and the kept block is $240/400$. This is the
clearest single example in the chapter of what porting to an FPGA buys -- not less arithmetic, but a
bookkeeping operation that costs a loop in software and two counters in hardware.
:::

**Windowing.** A frame is a slice cut from a continuing sound, and the cut is abrupt: the
signal simply stops at one end and begins at the other. A sudden edge looks, to any frequency
analysis, like very high frequency content that was never in the room. The remedy is to
multiply the frame by a **window function** that fades both ends toward zero before the
analysis is taken. The reference implementation uses the Hamming window across the 400
samples of the buffer. The cost is that the ends of the frame contribute little, which makes the
frequency response wider -- and "wider" is a claim with a number attached to it, not a mood. Section
1.3 prices it: [Figure 9](#fig-ch1-window-cost) draws the frame before and after the fade and shows
what each one does to a single tone.

**Short-Time Fourier Transform (STFT).** One DFT (Discrete Fourier Transform -- the sum that
turns a finite list of samples into a list of frequency strengths) per frame, repeated over
time, is the STFT. The reference implementation computes each frame's transform with a
512-point Fast Fourier Transform (FFT -- the standard family of algorithms for evaluating a
DFT quickly) and keeps only the non-redundant half, since the input values are real. That
leaves 257 frequency bins per frame.

**Mel filterbank.** The 257 bins are then collapsed into 80 bands, and the bands are not the
same width. They are spaced like human pitch perception, which resolves low frequencies well
and high frequencies poorly, so the filters are narrow at the bottom of the range and wide at
the top. Each filter is a triangle over a stretch of bins, and each output band is the
weighted sum of the bins under its triangle.

**Log compression.** Last, each band energy $E$ is replaced by $\ln(\max(E, 10^{-6}))$. The
logarithm is used because ears and models respond to ratios of loudness rather than to
differences in it. The floor at $10^{-6}$ exists so that a silent band returns a finite
number instead of minus infinity. The floor has a side effect on how this chapter's
experiment reports its error, and section 1.4 reads it.

The shapes belong in one table, because in hardware a shape is a wire width and a memory
size.

| Stage | Data produced per frame | Size at 32-bit float |
| --- | --- | --- |
| Waveform input | 160 new samples | 640 bytes arriving every 10 ms |
| Ring buffer | 400 samples held | 1,600 bytes, resident |
| Windowed frame | 400 samples | product of buffer and window |
| FFT input | 512 samples | 400 real plus 112 zeros |
| Spectrum | 257 bins | one power value each |
| Mel bands | 80 values | weighted by a fixed 80 x 257 matrix |
| Log-Mel frame | 80 values | the model input |

Two points to carry forward. The 80 log-Mel numbers are what the model sees, so the
pipeline's whole job is to reduce 400 pressure samples to 80 summary values, and every
decision in sections 1.3 and 1.4 is a choice about how much of that reduction to perform and
when. And the 80 x 257 matrix of filter weights never changes: it is computed once from the
sampling rate and the band limits, so in hardware it is a constant. That is why its
*size* -- not its arithmetic -- is the interesting number, and why section 1.4 measures it
against the memory a real chip has.

**Traceability.** The records this section's rate argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-11` | Speech Commands stores each utterance as linear 16-bit single-channel PCM at a 16 KHz rate |
| `V-05-10` | LibriSpeech is 1000 hours of 16 kHz read English speech, on a corpus distribution page |


## 1.3 Mathematical Formulation: STFT and Mel Filterbank

Six expressions turn a stream of samples into the 80 numbers of one frame. Each of them is read
in five fixed steps: the formula, the variables, what it means, what it costs in silicon, and what
it does *not* say. The last step matters most in this book. An equation is easy to mistake for a
permission slip, and each of these six invites a conclusion people draw from it that the equation
does not support.

That five-step shape is required of every printed formula in this book, so section 1.3 is where it
is set up. Later chapters repeat it rather than restate it. No card here depends on another card:
each one defines every symbol it prints, even a symbol an earlier card has already defined, because
a reader who jumps to one expression should not have to hunt backwards through the chapter to
understand it.

The design parameters come from `AudioConfig` in
`chapter01/exp_01_streaming_audio_pipeline.py`. They are gathered here as one block so the
arithmetic below can be checked by hand. Each is written as a statement about a symbol rather than
as a quantity in the world, because their source is a source file and not an instrument:

$f_s = 16{,}000\ \text{Hz}$, frame length $L = 400$ samples, hop $H = 160$ samples, transform
length $N = 512$ slots, band count $M = 80$, band range $f_{\min} = 0$ to
$f_{\max} = 8{,}000\ \text{Hz}$.

> **Where these parameters come from, and where their consequences come from.** All six are declared
> in the experiment file, so all six are design choices and none is a measurement. Nothing in this
> repository has varied them, so this book cannot say any of them is optimal. The rate is the one
> exception worth repeating: 16 kHz is inherited from the rate at which both training corpora store
> audio, which makes it a constraint the data imposes rather than a choice this project made, and
> section 1.2 keeps those records. Every quantity printed below is derived from this block by
> arithmetic the text shows in full. That is deliberate: the evidence registry holds records about
> the two platforms and about the training data, and no record of a frontend's own geometry, so a
> number here that is not traceable to a record is traceable to this block instead, and says so.

### A probe wave, before any formula

One of the six expressions contains the symbol $e^{-j2\pi kn/N}$. A reader who has not met that
symbol should not have to accept it on trust, so this subsection earns it first. Nothing in it is a
new idea. It is the ordinary fact that finding a wave inside a signal means multiplying by that wave
and adding.

**What a frequency has to match on.** A pure tone has three properties you can ask about. How far it
swings is its *amplitude*. How fast it repeats is its *frequency*. And *phase* is where in its cycle
it starts: two tones of the same pitch and the same loudness can begin on the way up or in the
middle of the swing, and they are then different signals. A method that finds a frequency in a
recording therefore has to answer all three questions or it has answered none of them.

**The test is a multiplication, not a division.** The frame is an array of samples. Hold a candidate
tone of the same length: a list of numbers, one per sample, saying where that tone is at each moment.
Multiply the two lists sample by sample and add up all the products. The sum answers one question --
how much do these two lists agree?

- If the frame *is* that tone, each product is the tone multiplied by itself, which is never
  negative. Every sample adds more, so the sum comes out large. A louder frame makes a larger sum,
  which is why the size of the sum carries the amplitude.
- If the frame is a tone of a different rate, the two rise and fall out of step. The products are
  sometimes positive and sometimes negative, the signs cancel, and the sum comes out near zero.
- If the frame is that same tone but *shifted* in phase, the cancelling stops and the sum grows
  again. So the sum depends on phase as much as on presence. That is the problem to solve next, not
  a detail to ignore.

**Two probes, because one cannot carry all three answers.** A single probe tone cannot tell a quiet
perfect match from a loud match with the wrong phase: both can give the same sum. The repair is to
run two probes that are a quarter of a cycle apart. Call them the cosine probe and the sine probe.
The cosine asks how much of the frame lines up with the candidate starting at the top of its swing.
The sine asks the same about a candidate starting a quarter of a cycle later, in the middle of its
swing. Two numbers, one from each probe, describe the frame's contents completely: the amplitude is
the length of the pair and the phase is the pair's angle. That is why a frequency analysis returns
*complex* values instead of plain magnitudes. A complex number is not exotic. It is two ordinary
numbers kept together so that one calculation can carry both accounts at once.

**Euler's formula writes the pair as one object.** Now the step that turns a recipe into a formula.
Take a number that spins rather than a number that swings.

$$e^{-j\theta} = \cos\theta - j\sin\theta$$

> **The formula.**
> $$e^{-j\theta} = \cos\theta - j\sin\theta$$
>
> **The variables.**
> - $e$ — the base of the natural logarithm: the constant whose growth per unit time equals itself.
>   No units. It appears here as the usual name for the operation that turns a rate of turning into a
>   position on a circle.
> - $j$ — the unit imaginary number, whose meaning is "turn through a right angle". Multiplying by
>   $j$ rotates a number by a quarter turn; multiplying by $-j$ rotates it the other way. $j$ is not
>   a variable, not a quantity and not a measurement. Mathematicians write $i$; engineers write $j$
>   because $i$ is already carrying electric current, which is this book's subject.
> - $\theta$ — the angle already turned, in radians. A full turn is $2\pi$ radians, so $\theta$ is not
>   a frequency and not a time; it is a position in a cycle.
> - $\cos\theta$ and $\sin\theta$ — the two projections of that position: the horizontal coordinate
>   and the vertical one. Each is a plain number between minus one and one, with no units.
>
> **What it means.** Follow the right-hand side as $\theta$ grows from zero. $\cos\theta$ starts at
> one and swings between one and minus one. $\sin\theta$ starts at zero and swings the same way a
> quarter of a turn later. The two of them together are a position on a circle of radius one, and
> the left-hand side is the compact name for that same position. The minus sign in front of the
> $j$ says which way the point travels as $\theta$ grows: clockwise. Read the whole thing as one
> sentence and it is this -- *multiplying by* $e^{-j\theta}$ *rotates a number through* $\theta$
> *clockwise*, *and taking the real and imaginary parts of the result is reading off the two probe
> values at that point of the cycle.* The identity is also why the probe wave below has length one
> at every sample: $\cos$ and $\sin$ of the same angle square and add to one.
>
> **What it costs.** Nothing. It is a change of notation, and notation is free. What costs silicon
> is the multiplication it licenses, and that price depends entirely on how the rotations are
> ordered -- one complex product per sample per bin if they are done as the sum below reads, or a
> few thousand if the same rotations are walked through in the order a Fast Fourier Transform uses.
> The card after this one prices that difference, and chapter 6 is where a hardware engine for it
> would be specified.
>
> **What it does not say.** It says nothing about audio. The identity holds for every angle and
> mentions no sample, no rate and no microphone. Reading it as a statement about sound is exactly the
> mistake the next card exists to prevent, and it is the reason this subsection comes before the
> formula rather than after it.

The use this book has for the identity is narrow. A list of the values that $e^{-j\theta}$ takes as
$\theta$ advances by a fixed step *is* the pair of probe waves above, written as one object: its real
part is the cosine probe at every sample, its imaginary part the sine probe, and advancing
$\theta$ by one step advances both probes by one sample. So one multiplication against the spinning
number performs the two probe multiplications together, and adding the products accumulates both
accounts of the agreement in a single sum.

### The windowed frame

*Mechanism.* A frame is a slice of the recording, and a slice has two hard ends. The analysis that
follows behaves as if what it is given repeats, so a slice that is loud at one end and silent at the
other presents a step, and a step contains every frequency a little. Fading the ends is the repair,
and fading is multiplication.

> **The formula.**
> $$x_\ell[n] = x[n_0 + \ell H + n]\; w[n], \qquad n = 0, 1, \dots, L-1$$
>
> **The variables.**
> - $x_\ell$ — the windowed frame that everything after this card works on: frame number $\ell$, an
>   array of $L$ numbers. Its unit is a sample's amplitude -- a normalised number in this
>   implementation, not a pressure.
> - $x$ — the whole sample stream, one number per sample, in the same amplitude units. It carries no
>   time unit of its own: time enters through the index and through $f_s$.
> - $\ell$ — which frame this is, counted from zero. Dimensionless.
> - $n$ — which sample inside one frame, from zero to $L-1$. Dimensionless.
> - $n_0$ — the sample index at which frame zero starts, anchoring the whole slide to one place in the
>   recording. A sample index, dimensionless. The reference implementation uses $n_0 = 0$.
> - $H$ — the hop: how many new samples each frame adds, $160$ here. Samples, dimensionless as a
>   count.
> - $L$ — the frame length, $400$ samples. Samples, dimensionless as a count.
> - $w$ — the window: a fixed list of $L$ numbers, one per position within a frame, whose job is to
>   fade the frame's ends. Dimensionless, and identical for every frame. This implementation uses the
>   Hamming window, whose ends sit at $0.08$ and whose middle at $1.00$.
> - $x[n_0 + \ell H + n]$ — the raw sample that lands at position $n$ of frame $\ell$, before the fade.
>
> **What it means.** Both counts are also lengths of time, and the conversion is one division:
> $f_s$ says how many numbers one second of audio is worth, so a count of samples becomes seconds by
> dividing it by $f_s$ -- $400$ samples are $400 / 16{,}000 = 25$ ms of audio and $160$ are
> $160 / 16{,}000 = 10$ ms. The second of those is the one everything downstream is measured against,
> because a new frame appears once per hop: $10$ ms is the deadline, and $25$ ms is how much audio has
> to have arrived before there is a frame to answer with. Two independent things happen in one line.
> The index $n_0 + \ell H$ is a sliding
> window: frame $\ell+1$ starts $H$ samples after frame $\ell$, so the analysis walks through the
> recording in steps rather than end to end. Because $H$ is smaller than $L$, consecutive frames cover
> $L - H$ samples in common, and that overlap is the whole reason a stream can be analysed in pieces
> without losing the samples that sit at a piece's edges -- every sample is heard by several frames, at
> several different points of the fade. The second thing is the fade itself: raw sample values are
> multiplied position by position by $w$, so the middle of the frame passes through nearly unchanged
> while its ends are cut down to $8\%$. Nothing is added, averaged or shifted. This is the least
> controversial stage in the pipeline, and the one place where a fixed list of constants is doing
> something irreversible to the data.
>
> **What it costs.** $w$ never changes, so in hardware it is a read-only table of $L$ constants and a
> multiplier per lane -- or one multiplier reused $L$ times per frame, which is the usual choice
> because it trades area for latency and this stage has $10$ ms to answer. It has no state to carry
> between frames and it makes no decisions. A registered figure for this stage's share of either
> platform is not available: the resource records in this book's evidence set describe whole
> accelerators and named processor blocks, not a multiplier bank of this size, so what the honest cost
> here is, is the shape.
>
> **What it does not say.** It does not say the fade is harmless. Multiplying by $w$ lowers the
> amplitude near both ends, which changes the answer every later stage gives, and changes it
> differently for a low tone than for a high one. Whether that change is acceptable to a recognition
> model is a question about the model: no formula can settle it, and no measurement against a model
> is registered in this repository. This book states the mechanism and reports nothing about its
> price in accuracy.

The two durations inside those variables are named once here because they recur everywhere else in
the book. A frame is $L$ samples, which at $16{,}000$ samples per second is $25$ ms of audio; a hop
is $H$ samples, which is $10$ ms. So the pipeline delivers one feature vector every $10$ ms, each
computed from $25$ ms of audio, and consecutive deliveries share $15$ ms of that audio. That shared
part is $240$ samples of a $400$-sample frame, which is $60\%$ of a frame, and
[Figure 6](#fig-ch1-frames-window-overlap) draws the whole arrangement to scale.

::: {#fig-ch1-frames-window-overlap .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  env/.style={draw=black!72, semithick, smooth},
  fb/.style={draw=black!45, thin, fill=black!4},
  lab/.style={font=\tiny, text=black!70},
  dim/.style={<->, black!70, thin},
  guide/.style={black!28, thin, densely dotted},
  st/.style={-{Stealth[length=1.4mm]}, black!55, thin}]
\begin{scope}[x=0.0122cm, y=1cm]
  \draw[guide] (0,0.12) -- (0,3.5300000000000002);
  \draw[guide] (160,0.12) -- (160,3.5300000000000002);
  \draw[guide] (320,0.12) -- (320,3.5300000000000002);
  \draw[guide] (480,0.12) -- (480,3.5300000000000002);
  \draw[guide] (640,0.12) -- (640,3.5300000000000002);
  \draw[guide] (1040,0.12) -- (1040,3.5300000000000002);
  \draw[fb] (0,2.97) rectangle (399,3.49);
  \draw[env] plot coordinates {(0,3.062) (25,3.076) (50,3.116) (75,3.176) (100,3.247) (125,3.317) (150,3.377) (175,3.416) (200,3.430) (225,3.415) (250,3.375) (275,3.315) (300,3.244) (325,3.173) (350,3.114) (375,3.075) (399,3.062)};
  \node[lab, anchor=east] at (-5,3.230) {$\ell=0$};
  \draw[fb] (160,2.35) rectangle (559,2.87);
  \draw[env] plot coordinates {(160,2.442) (185,2.456) (210,2.496) (235,2.556) (260,2.627) (285,2.697) (310,2.757) (335,2.796) (360,2.810) (385,2.795) (410,2.755) (435,2.695) (460,2.624) (485,2.553) (510,2.494) (535,2.455) (559,2.442)};
  \node[lab, anchor=east] at (155,2.610) {$\ell=1$};
  \draw[fb] (320,1.73) rectangle (719,2.25);
  \draw[env] plot coordinates {(320,1.822) (345,1.836) (370,1.876) (395,1.936) (420,2.007) (445,2.077) (470,2.137) (495,2.176) (520,2.190) (545,2.175) (570,2.135) (595,2.075) (620,2.004) (645,1.933) (670,1.874) (695,1.835) (719,1.822)};
  \node[lab, anchor=east] at (315,1.990) {$\ell=2$};
  \draw[fb] (480,1.1099999999999999) rectangle (879,1.63);
  \draw[env] plot coordinates {(480,1.202) (505,1.216) (530,1.256) (555,1.316) (580,1.387) (605,1.457) (630,1.517) (655,1.556) (680,1.570) (705,1.555) (730,1.515) (755,1.455) (780,1.384) (805,1.313) (830,1.254) (855,1.215) (879,1.202)};
  \node[lab, anchor=east] at (475,1.370) {$\ell=3$};
  \draw[fb] (640,0.49000000000000005) rectangle (1039,1.01);
  \draw[env] plot coordinates {(640,0.582) (665,0.596) (690,0.636) (715,0.696) (740,0.767) (765,0.837) (790,0.897) (815,0.936) (840,0.950) (865,0.935) (890,0.895) (915,0.835) (940,0.764) (965,0.693) (990,0.634) (1015,0.595) (1039,0.582)};
  \node[lab, anchor=east] at (635,0.750) {$\ell=4$};
  \draw[->, black!75] (-25,0.0) -- (1075,0.0) node[right, font=\tiny, xshift=1.5pt] {$n$};
  \draw[black!55] (0,-0.03) -- (0,0.03);
  \draw[black!55] (400,-0.03) -- (400,0.03);
  \draw[black!55] (800,-0.03) -- (800,0.03);
  \draw[black!55] (1040,-0.03) -- (1040,0.03);
  \node[lab, anchor=north] at (0,0.0) {0};
  \node[lab, anchor=north] at (400,0.0) {400};
  \node[lab, anchor=north] at (800,0.0) {800};
  \node[lab, anchor=north west, xshift=1pt] at (1040,0.0) {1040};
  \draw[dim] (0,-0.34) -- (160,-0.34) node[midway, below, font=\tiny] {$H$};
  \draw[dim] (0,3.6500000000000004) -- (400,3.6500000000000004) node[midway, above, font=\tiny] {$L$};
  \draw[dim] (160,-0.60) -- (400,-0.60) node[midway, below, font=\tiny] {{$L-H$ shared}};
  \draw[st] (280,-0.44) -- (280,-0.05);
\end{scope}
\end{tikzpicture}
```
Five frames of $L$ samples, each beginning $H$ samples after the one before, drawn to scale against
the sample axis. The curve over each lane is $w$, whose ends sit at $0.08$ of a sample's value and
whose middle passes it through unchanged. Reading across rather than down is the point: one region of
the recording appears in several frames at different points of the fade.
:::

### The Short-Time Fourier Transform

*Mechanism.* The transform asks one question of a frame, $N$ times: how much of this frame agrees
with a probe wave turning at this rate? The subsection before the first card above built the right
to ask it that way, and this is where that construction is written down.

> **The formula.**
> $$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n]\; e^{-j 2\pi k n / N}, \qquad k = 0, 1, \dots, N-1$$
>
> **The variables.**
> - $X_\ell[k]$ — the transform of frame $\ell$ at bin $k$: one complex number, which is two real
>   accounts kept together. No physical unit; it is a sum of sample amplitudes.
> - $x_\ell[n]$ — sample $n$ of the windowed frame from the card above, already faded, which is why
>   this expression never touches the raw stream. Amplitude units.
> - $k$ — the bin index, from zero to $N-1$: which probe wave this sum is being asked about.
>   Dimensionless. Bin $0$ is the probe that never turns, so it measures the frame's mean value.
> - $n$ — the sample index inside the transform, from zero to $N-1$. Dimensionless.
> - $N$ — the transform length in slots, $512$. Not the frame length: the $400$ windowed samples are
>   written into a $512$-slot array and the remaining $112$ slots are filled with zeros.
> - $j$ — the unit imaginary number, the symbol for a quarter turn, as the Euler card above defines it.
> - $\pi$ — the circle constant, so $2\pi$ radians is one full turn.
> - $e^{-j2\pi kn/N}$ — the probe wave of bin $k$: at sample $n$ it has turned $kn/N$ of a full
>   revolution, clockwise. Its length is one at every step, so multiplying by it changes a number's
>   direction and not its size.
>
> **What it means.** Take one term first. $x_\ell[n]$ is a sample, and multiplying it by a unit-length
> spinning number turns that sample's value by an angle rather than scaling it: a positive sample stays
> where it pointed, a negative one points the opposite way, and how far round it has been turned
> depends on where in the frame it sits. Adding the terms then lays those turned contributions head to
> tail. If the frame really contains bin $k$'s rate, the turns line up: every term arrives pointing in
> roughly the same direction, so they reinforce and the result is long. If it does not, the terms point
> all the way round the circle and cancel, and the result is short. Because the probe is the spinning
> number rather than a swinging one, the surviving length *and* the surviving direction both come out
> of one sum: the real part is the cosine probe's account, the imaginary part the sine probe's. That
> is the whole content of the phrase *how much of this frame is at this pitch* -- a correlation against
> a candidate wave, read on two axes so that loudness and timing cannot be confused with each other.
> The zeros added between sample $400$ and slot $512$ contribute nothing to any sum; their effect is
> to place the bins on a finer grid, not to sharpen anything.
>
> **What it costs.** Written as a sum, one bin costs $N$ complex multiplications and $N$ bins cost
> $N$ times that, so the *expression* costs $512^2$ products per frame. Nobody pays it, including
> this implementation, which calls a Fast Fourier Transform and reaches the same numbers in a few
> thousand operations instead -- the card above is where that difference is introduced, and chapter 6
> is where a fixed-point engine for it is specified. Two other costs hide in the notation. Padding
> from $400$ to $512$ means any hardware holding a frame holds the padded length, not the physical
> one. And the output is complex, so a design that keeps every bin in full stores two numbers per bin
> even though the next stage throws one of them away. No measured cost for this stage on either
> platform is registered in this book's evidence set.
>
> **What it does not say.** It does not say a large result proves a tone is present. A frame of padded
> silence, a click, a breath, and a tone sitting just off bin $k$'s rate all produce sums, and the
> expression cannot tell which produced it. It does not say the bins are independent measurements of
> the world either: they are $N$ readings of one frame, at a spacing fixed by $N$ and $f_s$ alone.
> Most importantly for anyone sizing a design, it does not say anything about how fast it is to
> evaluate -- the sum's shape prices the arithmetic of the written form, and reading a resource
> estimate off that is the single most common error in this section, worth an order of magnitude.

Where does the $k f_s / N$ come from? The card above says that by sample $n$, bin $k$'s probe has
turned $kn/N$ of a revolution, so across the $N$ samples one frame spans it has turned exactly $k$
whole revolutions. $k$ revolutions divided by the $N$ samples it took to perform them is $k / N$ of a
revolution *per sample*, which is what the formula's $N$ underneath is for: on its own it says how
fast the probe turns per sample, not per second. A stream hands over $f_s$ samples per second, so
multiplying the per-sample rate by $f_s$ converts it to revolutions per second, and a revolution per
second is a hertz. That is the whole of $k f_s / N$, and it is why $f_s$ sits on top. Adjacent bins
differ by one such step, which is $f_s / N = 16{,}000 / 512 = 31.25$ Hz apart, and the top of the
range is half the sampling rate, $8{,}000$ Hz. Because the input
samples are real, bin $k$ and bin $N-k$ carry the same information, so the implementation keeps bins
$0$ through $N/2$: $257$ bins of one frame's spectrum. That spacing is fixed by $N$ and $f_s$ alone.
It is not adjustable per frame, and no cleverness in the hardware changes it.

### The power spectrum

*Mechanism.* Recognition models use energy and discard phase, so each complex bin is reduced to one
real number. Discarding phase is a decision with consequences -- a model that cannot see timing at
the scale of a cycle is a model that has been handed exactly this reduction, and chapter 9 has to
live with it.

> **The formula.**
> $$P_\ell[k] = |X_\ell[k]|^2$$
>
> **The variables.**
> - $P_\ell[k]$ — the power of frame $\ell$ at bin $k$, one of $257$ non-negative real numbers in this
>   implementation. Its unit is amplitude squared.
> - $X_\ell[k]$ — bin $k$ of the transform from the card above: a complex number with a real part and
>   an imaginary part, in amplitude units.
> - $|\cdot|$ — the magnitude of a complex number: its distance from zero, found by squaring both parts
>   and taking the square root.
>
> **What it means.** The magnitude asks how long the sum ended up and ignores which way it pointed.
> Squaring then removes the root, which is the point: a later stage can add these numbers meaningfully
> only if they are plain reals, and a square root in the way of an addition is both a cost and a
> nuisance. Two accounts are discarded on the way. The direction the sum pointed -- the phase -- is
> gone, and the sign of the amplitude is gone too, since a square cannot be negative. What remains is a
> non-negative profile over the bins: a description of how one frame's energy lies across rates, and
> nothing else. Every stage after this one consumes that profile.
>
> **What it costs.** Two multiplications and one addition per kept bin when the real and imaginary
> parts are already in hand, and no extra storage: the output is half the size of the input because a
> real number replaces a pair. The square root that the magnitude notation implies is deliberately
> never computed, because this stage squares instead -- so a design needs no root here, which matters
> because a square root is the kind of non-linear step that has no fixed cost per cycle. A registered
> measurement of this stage on either platform does not exist in this book's evidence set.
>
> **What it does not say.** It does not say the result is a power in any physical sense. $P_\ell[k]$
> is in sample units squared: the microphone's sensitivity, the recording gain, and any normalisation
> applied before the samples were read are all inside that value and none of them is separated out by
> it. It does not say the numbers are comparable across frames either, because the window faded each
> frame differently -- two identical tones at two positions in the recording do not produce identical
> powers. That is a consequence of the first card, not of this one, and it is the reason a frontend
> that is judged on a single frame's absolute value is being judged on the wrong thing.

### Mapping hertz to the Mel scale

*Mechanism.* $257$ bins have to become $80$ bands, and hearing does not divide the range the way the
arithmetic does: two low frequencies are easier to tell apart than two high ones. So the band edges
are placed at equal steps on a *perceptual* scale and converted back to hertz. This formula defines
that scale.

> **The formula.**
> $$\mathrm{mel}(f) = 2595 \log_{10}\!\left(1 + \frac{f}{700}\right)$$
>
> **The variables.**
> - $\mathrm{mel}$ — the function returning a position on the Mel scale for a frequency in hertz. Its
>   output is in mels, a unit of perceived pitch rather than of cycles per second.
> - $f$ — a frequency in hertz, which is cycles per second. The range used here is $0$ to $8{,}000$.
> - $2595$ — the scale constant, fixing how many mels correspond to one decade of frequency. Part of
>   this definition of the Mel scale, not a property of any hardware or of any listener here.
> - $700$ — the corner frequency of the same definition, in hertz. Well below it the scale is close to
>   linear in hertz; well above it, close to logarithmic.
> - $\log_{10}$ — the base-ten logarithm, whose argument is the plain ratio $1 + f/700$ and which
>   returns a pure number.
>
> **What it means.** A logarithm rises quickly and then hardly at all, so equal steps of this function
> correspond to ever larger steps of frequency: the bottom of the range is stretched and the top is
> squeezed. That is the whole trick, and it is why placing band edges evenly *in mels* produces bands
> that are narrow at low frequency and wide at high frequency, which is what the figure below draws.
> The $1 + {}$ term makes the function pass through zero at zero hertz; without it the scale would be
> undefined at exactly the frequency the band range starts at, since a logarithm of zero is minus
> infinity. The inverse is used as well, and the code writes it as $700$ multiplied by ten raised to
> the mels divided by $2595$, minus $700$.
>
> **What it costs.** This function is evaluated during setup, once, at $M+2$ frequencies, and its
> result is folded into a table of constants. At run time the stage costs no logarithm at all, which
> is the entire reason for doing it this way: a non-linear function has no fixed cost per cycle and so
> has no place in a data path that must answer every $10$ ms. A registered figure for the setup cost is
> not available, and it would not matter if it were, since setup runs once per experiment rather than
> once per frame.
>
> **What it does not say.** It does not say the Mel scale is correct for keyword spotting. It describes
> how human listeners judge the closeness of two pure tones, measured in a laboratory, and it enters a
> machine frontend by convention rather than by argument. Nothing in this repository compares a model
> fed these features against the same model fed bands placed any other way, so this book cannot claim
> the perceptual step buys anything. It also does not say $80$ bands, or $0$ to $8{,}000$ hertz, or
> that the two constants are right for $16$ kHz audio: those are `AudioConfig` and its `f_min` and
> `f_max`, and the next card shows one place where treating the constants as though they were
> measurements produces a silent band.

The compression the card describes is easiest to see as a curve rather than as a sentence about
logarithms. [Figure 7](#fig-ch1-mel-curve) plots the function itself, with equal steps marked on the
mel axis and dropped through to the hertz axis they select.

::: {#fig-ch1-mel-curve .figure}
```tikz
% The Mel function itself, which the triangles figure beside it does not draw: it shows what the
% triangles LOOK like after the warp, this shows the warp. Hertz on the base axis, mels on the upright
% one, and the curve is mel(f) = 2595 log10(1 + f/700) evaluated by pgfmath at every point, so it is
% the function and not a sketch of it. The horizontal rules are equal steps of mels -- what the
% filterbank actually spaces evenly -- and where each one meets the curve and drops to the hertz axis
% is the frequency it selects. The gaps between those drops grow from left to right: that is the whole
% idea in one picture.
% One unit (cm). The nine mel/hertz band-edge pairs are computed once from the inverse map and written
% as literals, so no number is printed by the compiler and none is eyeballed. x = 0.001125 cm/Hz,
% y = 0.001479 cm/mel.
\begin{tikzpicture}[
  font=\tiny,
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ann/.style={font=\tiny, text=black!66, align=center, inner sep=0pt},
  annt/.style={font=\tiny, text=black!66, align=left, inner sep=0pt},
  ax/.style={->, black!72, semithick},
  tk/.style={font=\tiny, text=black!60},
  gr/.style={black!30, thin, densely dashed},
  drop/.style={black!40, thin, densely dotted},
  curve/.style={black!82, line width=0.9pt},
  gap/.style={black!70, thin},
  tick/.style={black!70, thin}]
\def\sx{0.001125}   % cm per hertz   (8000 Hz -> 9.00 cm)
\def\sy{0.001479}   % cm per mel     (2840 mel -> 4.20 cm)
\def\X{1.30}        % cm, plot origin
\def\Y{0.70}

\node[ttl, anchor=west] at (0,\Y + 5.14)
  {equal steps up the mel axis, unequal steps along the hertz axis};

% ---------- the curve, drawn first so the rules and ticks sit on top ----------
\draw[curve, domain=0:8000, smooth, variable=\f, samples=140]
  plot ({\X + \f*\sx}, {\Y + 1126.98*ln(1+\f/700)*\sy});

% ---------- axes ----------
\draw[ax] (\X,\Y) -- (\X + 9.00 + 0.55,\Y);
\draw[ax] (\X,\Y) -- (\X,\Y + 4.20 + 0.35);

% hertz ticks: only the two axis ends are labelled, because the eight band-edge drops crowd together
% at the low end (the first three fall inside 0.9cm) -- that crowding IS the story, and the dotted
% drops mark the positions without naming each one.
\draw[black!55] (\X,\Y-0.035) -- (\X,\Y+0.035);
\draw[black!55] (\X + 8000.0*\sx,\Y-0.035) -- (\X + 8000.0*\sx,\Y+0.035);
\node[tk, anchor=north] at (\X,\Y-0.06) {$0$};
\node[tk, anchor=north] at (\X + 8000.0*\sx,\Y-0.06) {$8000$};
\node[tk, anchor=west] at (\X + 9.00 + 0.60,\Y) {Hz};

% mel ticks every 355 (literal)
\foreach \m/\lab in {0/$0$,355/$355$,710/$710$,1065/$1065$,1420/$1420$,1775/$1775$,
                     2130/$2130$,2485/$2485$,2840/$2840$} {
  \draw[black!55] (\X-0.035,\Y + \m*\sy) -- (\X+0.035,\Y + \m*\sy);
  \node[tk, anchor=east] at (\X-0.07,\Y + \m*\sy) {\lab};
}
\node[tk, anchor=south] at (\X,\Y + 4.20 + 0.38) {mels};

% ---------- equal-mel rules, dropped to the hertz axis ----------
\foreach \m/\h in {355/259.2,710/614.3,1065/1101.0,1420/1767.8,1775/2681.5,
                   2130/3933.6,2485/5649.2,2840/8000.0} {
  \draw[gr] (\X,\Y + \m*\sy) -- (\X + \h*\sx,\Y + \m*\sy);
  \draw[drop] (\X + \h*\sx,\Y + \m*\sy) -- (\X + \h*\sx,\Y);
}

% ---------- the two gaps that carry the argument, as dimension lines with end ticks ----------
\draw[gap] (\X + 0.000*\sx,\Y-0.36) -- (\X + 259.2*\sx,\Y-0.36);
\draw[tick] (\X + 0.000*\sx,\Y-0.44) -- (\X + 0.000*\sx,\Y-0.28);
\draw[tick] (\X + 259.2*\sx,\Y-0.44) -- (\X + 259.2*\sx,\Y-0.28);
\draw[gap] (\X + 5649.2*\sx,\Y-0.36) -- (\X + 8000.0*\sx,\Y-0.36);
\draw[tick] (\X + 5649.2*\sx,\Y-0.44) -- (\X + 5649.2*\sx,\Y-0.28);
\draw[tick] (\X + 8000.0*\sx,\Y-0.44) -- (\X + 8000.0*\sx,\Y-0.28);
\node[ann, text=black!80] at (\X + 129.6*\sx,\Y-0.54) {$259$};
\node[ann, text=black!80] at (\X + 6824.6*\sx,\Y-0.54) {$2{,}351$};
\node[annt, text=black!80, align=left] at (\X + 9.00 + 0.62,\Y + 1.10)
  {one step of\\mels is $259$\\Hz here,\\$2{,}351$ Hz\\at the top};
\end{tikzpicture}
```
The upright axis is mels, the base axis is hertz, and the curve is the function the filterbank card
above prints. Reading it the way the code does: pick a frequency on the base axis, go up to the curve,
come across to the upright axis, and you have its mel position. The horizontal rules are the mel values
the $80$ bands are spaced between -- equal steps of $355$ mels -- and each one drops to the hertz it
selects. Those drops are the point. The first step spans $259$ Hz and the last spans $2{,}351$ Hz, nine
times as much, for the same perceptual distance, because a logarithm rises quickly and then hardly at
all. That is why the triangles in the next figure are narrow on the left and wide on the right without
anyone choosing widths: the widths are read off this curve.
:::

### The filterbank as a weighted sum

*Mechanism.* The $82$ scale points turn back into hertz and then into whole bin indices, and each
neighbouring triple of points becomes a triangle over the bins it spans. Band $m$ is the weighted sum
of the power spectrum under its own triangle.

> **The formula.**
> $$E_\ell[m] = \sum_{k=0}^{256} g_m[k]\, P_\ell[k], \qquad g_m[k] =
> \begin{cases}
> \dfrac{k - k_{m-1}}{k_m - k_{m-1}} & k_{m-1} \le k \le k_m \\[4pt]
> \dfrac{k_{m+1} - k}{k_{m+1} - k_m} & k_m < k \le k_{m+1} \\[4pt]
> 0 & \text{otherwise}
> \end{cases}$$
>
> **The variables.**
> - $E_\ell[m]$ — the energy of band $m$ in frame $\ell$. One of $M$ non-negative reals in
>   amplitude-squared units; all $M$ of them together are the whole output of this stage.
> - $m$ — the band index, from $0$ to $M-1$, with $M = 80$. Dimensionless.
> - $k$ — the bin index inside the sum, from $0$ to $256$. Dimensionless.
> - $P_\ell[k]$ — bin $k$ of the power spectrum from its card above, a non-negative real in
>   amplitude-squared units.
> - $g_m[k]$ — the height of band $m$'s triangle at bin $k$: a unitless weight between zero and one,
>   zero outside the triangle and one at its peak.
> - $k_j$ — the bin index of the $j$-th of the $M+2 = 82$ scale points, a whole number from zero
>   upward. It is the *rounded-down* result of turning a hertz value into a bin, which is why every
>   width below is a whole number of bins rather than a slice of one.
> - $k_{m-1}$, $k_m$, $k_{m+1}$ — the left edge, the centre and the right edge of band $m$'s triangle.
>   Each band borrows its edges from the points next to its own centre, which is why $80$ bands need
>   $82$ points and why neighbouring triangles touch rather than overlap.
> - $256$ — the index of the top kept bin, because $257$ bins are numbered from zero.
>
> **What it means.** A triangle is an average that prefers the bins near its centre. The two middle
> lines are its two slopes: the first climbs from zero at the left edge to one at the centre, the
> second falls back to zero at the right edge, which is what the two ratios say in words -- a fraction
> of the way along a span. The third line matters as much: a band ignores every bin outside its own
> triangle entirely rather than giving them a small weight, so the row of $g$ is mostly zero.
> Multiplying a fixed $g$ by $P_\ell$ and adding is a matrix times a vector, so the entire stage is
> $M$ dot products of length $257$, and once the triangles are set up nothing about it depends on the
> audio at all. That is what makes this the most replaceable stage in the frontend.
>
> **What it costs.** The full matrix has $M$ by $257$ entries: eighty rows of two hundred and
> fifty-seven weights each, so $80 \times 257 = 20{,}560$ multiply-accumulate operations per frame --
> one multiplication and one addition fused into a single step -- if every entry is performed. The
> per-second figure is that count times how often a frame appears. One frame is produced per hop, a hop
> is $H / f_s = 160 / 16{,}000 = 10$ ms of audio, so the stage runs $100$ times a second and the
> upper-bound count is $20{,}560 \times 100 = 2.056$ million operations a second. Three facts make
> that an upper bound rather than a bill. A triangle covers only the bins between its own edges, so
> most of the matrix is zero, and a design that skips zeros spends nothing on them: the matrix
> computed at these parameters has 20,560 entries and only 425 of them are non-zero, which is 98%
> of the stage skippable, and derived from the code rather than measured on any hardware. The same
> arithmetic spread over the fabric's registered multiply-accumulator count gives each slice about
> 1,647 operations per second, computed by dividing the per-second figure above by 1,248, which is a
> way of noticing that $100$ frames per second is a very light load for that many of them -- not a
> claim that anyone has built that design. And on the Jetson side the count is a bandwidth problem
> rather than an arithmetic one: the weights are read-only, so the question chapter 3 asks is how
> much of this matrix can sit where it reads fast, not whether the multiplies fit. None of these
> figures is a measured cost of an implementation.
>
> **What it does not say.** Nothing here says $80$ is the right number of bands. Eighty is what
> `AudioConfig` declares; fewer bands lose spectral detail and cost less storage, more do the reverse,
> and where the balance lies is a question about the model that consumes the features, which is
> chapter 5's subject. No run in this repository has varied $M$. The formula also hides something the
> figure below is drawn to show: because every point's bin index is rounded *down* to a whole bin, and
> adjacent bins are only $31.25$ Hz apart, the bands at the bottom of the range cannot be
> distinguished from each other at that resolution. Run over this book's own parameters, the stage
> produces one band that covers no bin at all, eighteen bands that cover exactly one, and a widest band
> covering sixteen. So "80 bands" counts the rows of a matrix; it does not claim $80$ independent
> measurements. In particular, the band that covers nothing returns zero energy for every input, which
> is a permanent fact about the feature vector rather than a fact about the audio.

::: {#fig-ch1-mel-triangles .figure}
```tikz
% The 80 Mel triangles at their computed positions. The geometry is not eyeballed: the 82 points come
% from mel(f) = 2595 log10(1 + f/700) run backwards over 0..8000 Hz, converted to bins by
% floor((N+1) f / fs) exactly as the reference code does, and every hertz value below is that bin
% times 31.25 Hz. Six triangles are drawn in panel (a) rather than eighty because at this width eighty
% outlines merge into one band; panel (b) then shows the low end, where the rounding bites.
% Width: 8000 Hz at 0.00145cm/Hz is 11.6cm, inside the 15.6cm text block.
\begin{tikzpicture}[
  font=\scriptsize,
  tri/.style={draw=black!78, semithick},
  bin/.style={draw=black!25, thin},
  ax/.style={->, black!75},
  tk/.style={font=\tiny, text=black!75},
  nb/.style={font=\tiny, black!60},
  band/.style={draw, black!60, thin, fill=black!6, inner sep=2.5pt, font=\tiny}]

% ---------- panel (a): the whole range, drawn against hertz ----------
\begin{scope}[x=0.00145cm, y=1.05cm]
  \node[anchor=west, font=\tiny\itshape, text=black!70] at (-140,1.72)
    {(a) six of the eighty triangles, against hertz: equal steps in mels, growing steps in hertz};
  \draw[ax] (-120,0) -- (8320,0);
  \foreach \h/\lbl in {0/$0$,1000/$1$,2000/$2$,3000/$3$,4000/$4$,5000/$5$,6000/$6$,7000/$7$,8000/$8$} {
    \draw[black!55] (\h,-0.04) -- (\h,0.04) node[tk, below, yshift=-0.5pt] {\lbl};
  }
  \node[tk, anchor=west, xshift=2pt] at (8330,0) {kHz};
  % the energy floor, so the reader sees the bank as a floor and not six islands
  \fill[black!8] (0,0) rectangle (8000,0.045);
  % band 25, 40, 55, 65, 72, 79: edges from the computed bin indices
  \draw[tri] (812.50,0) -- (843.75,1) -- (906.25,0) -- cycle;
  \draw[tri] (1718.75,0) -- (1781.25,1) -- (1875.00,0) -- cycle;
  \draw[tri] (3156.25,0) -- (3281.25,1) -- (3406.25,0) -- cycle;
  \draw[tri] (4593.75,0) -- (4750.00,1) -- (4937.50,0) -- cycle;
  \draw[tri] (5875.00,0) -- (6093.75,1) -- (6281.25,0) -- cycle;
  \draw[tri] (7468.75,0) -- (7718.75,1) -- (8000.00,0) -- cycle;
  % whole-bin grid, to make the resolution the triangles actually have visible
  \foreach \b in {64,128,192,256} {
    \pgfmathsetmacro{\hb}{\b*31.25}
    \draw[bin] (\hb,0) -- (\hb,1.18);
    \node[nb, anchor=south west, xshift=1.2pt] at (\hb,1.19) {bin \b};
  }
  \node[nb, align=left, anchor=west] at (6350,0.62)
    {band 79: $16$ bins\\ of real support};
\end{scope}

% ---------- panel (b): the bottom 300 Hz, where one bin is coarser than one band ----------
% Two aligned rows. The upper row is the ten lowest whole bins, 31.25 Hz wide each. The lower row is
% bands 0..9, and each band box sits directly under the single bin it actually reads, so the mapping
% is shown by vertical alignment rather than by crossing arrows. Band 2 reads no bin: its ideal
% triangle has centre and right edge on the same rounded bin, so it collapses onto the boundary
% between bins 1 and 2 and is drawn there, in red.
\begin{scope}[yshift=-4.15cm, x=0.040cm, y=0.9cm]
  \node[anchor=west, font=\tiny\itshape, text=black!70] at (0,2.95)
    {(b) the ten lowest bins, and which one each band reads};
  % --- Hz ruler along the top of the bin row ---
  \draw[ax] (0,2.15) -- (330,2.15);
  \foreach \h/\lbl in {0/$0$,62.5/$62.5$,125/$125$,187.5/$187.5$,250/$250$,312.5/$312.5$} {
    \draw[black!55] (\h,2.09) -- (\h,2.21) node[tk, above, yshift=0.5pt] {\lbl};
  }
  \node[tk, anchor=west, xshift=2pt] at (332,2.15) {Hz};
  % --- the ten bin cells, index centred inside each ---
  \foreach \b in {0,...,9} {
    \pgfmathsetmacro{\lo}{\b*31.25}
    \draw[bin, fill=black!4] (\lo,1.25) rectangle ++(31.25,0.72);
    \node[font=\tiny, text=black!72] at (\lo+15.6,1.61) {bin $\b$};
  }
  % --- band boxes, each under the bin it reads (band m reads bin m-1, except band 2) ---
  \node[band] (b0) at (15.6,0.30) {band $0$};
  \node[band] (b1) at (46.9,0.30) {band $1$};
  \node[band, fill=red!8, draw=black!55] (b2) at (62.5,-0.55) {band $2$};
  \node[band] (b3) at (78.1,0.30) {band $3$};
  \node[band] (b4) at (109.4,0.30) {band $4$};
  \node[band] (b5) at (140.6,0.30) {band $5$};
  \node[band] (b6) at (171.9,0.30) {band $6$};
  \node[band] (b7) at (203.1,0.30) {band $7$};
  \node[band] (b8) at (234.4,0.30) {band $8$};
  \node[band] (b9) at (265.6,0.30) {band $9$};
  % short vertical links from each band up to the bin it reads
  \foreach \x in {15.6,46.9,78.1,109.4,140.6,171.9,203.1,234.4,265.6} {
    \draw[->, black!50, thin] (\x,0.55) -- (\x,1.23);
  }
  % band 2's dashed link to the empty boundary between bin 1 and bin 2
  \draw[->, black!50, thin, densely dashed] (62.5,-0.07) -- (62.5,1.23);
  \node[font=\tiny, text=black!60, anchor=north] at (62.5,-0.78) {reads nothing};
\end{scope}

\end{tikzpicture}
```
The eighty triangles at their computed positions, against hertz rather than against mels, because
that is the axis on which the spacing visibly grows. Panel (a) draws six of the eighty, with faint
lines marking whole bins; panel (b) draws the ten lowest bins and the one bin each of the ten lowest
bands reads. Band $2$ is red because its triangle straddles a bin boundary and reads nothing at all.
:::

### Log compression

*Mechanism.* Energy spans many orders of magnitude and a network prefers numbers of comparable size,
so each band is replaced by the logarithm of its energy, and a floor keeps that logarithm finite.

> **The formula.**
> $$c_\ell[m] = \ln\bigl(\max(E_\ell[m],\, 10^{-6})\bigr)$$
>
> **The variables.**
> - $c_\ell[m]$ — element $m$ of frame $\ell$'s log-Mel feature vector: one of $M$ real numbers,
>   negative or positive, in units of log-energy. This whole vector is what the model in chapter 5
>   receives, so its length is that model's input width.
> - $E_\ell[m]$ — band $m$'s energy from the filterbank card above, a non-negative real in
>   amplitude-squared units.
> - $\ln$ — the natural logarithm, base $e$: the power to which $e$ must be raised to give its
>   argument. It returns a pure number and carries no unit.
> - $\max(\cdot,\cdot)$ — the larger of its two arguments, which is what makes the second one a floor.
> - $10^{-6}$ — the floor, in the same amplitude-squared units as $E_\ell[m]$. A declared constant of
>   the code, not a measured property of anything.
>
> **What it means.** A logarithm turns ratios into differences, so a band a hundred times louder than
> another becomes a fixed distance away rather than a hundred times further out, and a whisper and a
> shout end up in comparable ranges. The floor exists because the logarithm of zero is minus infinity
> and infinity cannot be stored in a fixed-width number: with no floor, a single silent band would put
> minus infinity into the vector and poison every operation that touches it. The comparison happens in
> energy units *before* the logarithm, which is why the floor is quoted as an energy rather than as a
> feature value. Once taken, a band sitting exactly at the floor returns $\ln(10^{-6})$, about
> $-13.8$, so the floor does not disappear: it arrives at the model's input as a specific number.
>
> **What it costs.** A design must either evaluate a logarithm -- a non-linear function, so a lookup
> table or a polynomial rather than a multiply -- or hold energies in a number format whose exponent
> field already *is* a logarithm. That fork is chapter 6's subject, and which side is cheaper depends
> on the number format chosen there, which is why this card cannot price it. On the GPU side the stage
> is memory-bound and small next to the model; no measured cost is registered. The comparison itself
> is a comparator and a multiplexer, about as close to free as anything in this pipeline gets.
>
> **What it does not say.** This floor needs caution twice, and this book needs both. First,
> $10^{-6}$ sets the smallest energy the output can report, so an error claimed below it is
> meaningless: a band at the floor and a band at true silence return the same feature and nothing
> downstream can separate them. Second, a quantity built on this output can be dominated by the floor
> rather than by the signal, because the logarithm flattens the top of the range while the floor keeps
> its bottom differences large -- and the filterbank card above names a band that sits at the floor for
> every frame of every recording, which means at least one element of this vector carries a constant
> rather than a measurement. Section 1.4 reads a measured number of exactly this kind and treats it as
> a property of the floor. Nothing in the formula says which logarithm base is right, or that a
> logarithm is the best compression for a keyword spotter at all. Those are `AudioConfig`, and they are
> untested.

### The trade-off the sidebar names

The sidebar at the head of this chapter lists a time-frequency uncertainty principle, and the
arithmetic behind it is already on the page. The frame is 400 samples long, which at
16,000 samples per second is 25 ms: that is how finely the pipeline can say *when*. The bins
are 31.25 Hz apart: that is how finely it can say *at what pitch*. Both come from $L$ and $N$
in the same config block, and both are fixed for the whole run.

The engineering consequence is that a preprocessing design cannot be good at both, so the
frame length is a real decision rather than a formality. What cannot be inferred is which
side of the trade-off matters more for a voice model. A longer frame gives finer pitch and
coarser timing, and whether a given keyword spotter gains or loses by that is a question about
the model. It is answerable by measuring recognition accuracy and the equal error rate (EER --
the threshold where false accepts and false rejects are equally common) at several values of
$L$. Nobody has run that sweep here. [Figure 6](#fig-ch1-frames-window-overlap) and
[Figure 8](#fig-ch1-mel-triangles) are the same decision drawn twice: a wider frame buys a finer
bin grid and gives up the ability to say when something happened, and at the values this book uses
the grid is still coarse enough that the lowest bands of the bank land on whole bins one at a time.

The other half of the trade-off is not about $L$ at all, and it is the half the windowing paragraph
owes a number. Holding the frame length fixed, the shape of the frame's ends decides how wide every
tone comes out and how much of the neighbouring bins' energy lands on it.

[Figure 9](#fig-ch1-window-cost) prices it, because the sentence above says the fade makes
the response "wider" and nobody can tell from that word how much wider, or what the widening is
buying. It draws one frame of a $250$ Hz tone twice -- once as a bare cut leaves it, once as the
Hamming window leaves it -- and beside each, what a single tone becomes under that choice.

::: {#fig-ch1-window-cost .figure}
```tikz
% One frame in time, and what each way of ending it costs in frequency. Each row is one choice
% and its price: left, the 400-sample frame of a 250 Hz tone against the continuing tone it was
% cut out of; right, the shape a single tone gets smeared into -- the transform of the window,
% parked at the tone. The dashed rule is the first ridge: -13 dB down for the cut,
% -44 dB for the fade. The widths are exact divisions, not measurements:
% 2 f_s/L = 80 Hz for the cut against 4 f_s/L = 160 Hz for the fade, on a bin
% grid 31.25 Hz apart, so the fade pays 2.6 extra bins of width to
% buy back its edges. One unit (cm); numpy evaluated these curves, pgfmath evaluates nothing.
\begin{tikzpicture}[
  font=\tiny,
  ttl/.style={font=\tiny\itshape, text=black!78, align=left, inner sep=0pt},
  ax/.style={->, black!72, semithick},
  tk/.style={font=\tiny, text=black!60},
  curve/.style={black!82, line width=0.8pt},
  env/.style={black!52, thin, densely dashed},
  gone/.style={black!28, thin},
  dim/.style={black!70, thin},
  ridge/.style={black!55, thin, dash dot},
  tick/.style={black!70, thin},
  lab/.style={font=\tiny, text=black!72, align=center, inner sep=0pt}]
\draw[gone] plot [smooth] coordinates {(0.12,4.21) (0.14,4.10) (0.16,3.98) (0.18,3.84) (0.20,3.70) (0.23,3.56) (0.25,3.42) (0.27,3.30) (0.29,3.19) (0.31,3.10) (0.33,3.03) (0.35,2.99) (0.37,2.98) (0.39,2.99) (0.41,3.03) (0.43,3.10) (0.46,3.19) (0.48,3.30) (0.50,3.42) (0.52,3.56) (4.74,4.42) (4.76,4.41) (4.78,4.37) (4.80,4.30) (4.82,4.21) (4.85,4.10) (4.87,3.98) (4.89,3.84) (4.91,3.70) (4.93,3.56) (4.95,3.42) (4.97,3.30) (4.99,3.19) (5.01,3.10) (5.03,3.03) (5.06,2.99) (5.08,2.98) (5.10,2.99) (5.12,3.03) (5.14,3.10)};
\draw[ax] (0.06,3.70) -- (5.41,3.70);
\draw[black!58, thin] (0.12,2.90) -- (0.12,4.50);
\draw[black!58, thin] (4.31,2.90) -- (4.31,4.50);
\draw[curve] plot [smooth] coordinates {(0.54,3.70) (0.56,3.84) (0.58,3.98) (0.60,4.10) (0.62,4.21) (0.65,4.30) (0.67,4.37) (0.69,4.41) (0.71,4.42) (0.73,4.41) (0.75,4.37) (0.77,4.30) (0.79,4.21) (0.81,4.10) (0.83,3.98) (0.86,3.84) (0.88,3.70) (0.90,3.56) (0.92,3.42) (0.94,3.30) (0.96,3.19) (0.98,3.10) (1.00,3.03) (1.02,2.99) (1.04,2.98) (1.06,2.99) (1.09,3.03) (1.11,3.10) (1.13,3.19) (1.15,3.30) (1.17,3.42) (1.19,3.56) (1.21,3.70) (1.23,3.84) (1.25,3.98) (1.27,4.10) (1.30,4.21) (1.32,4.30) (1.34,4.37) (1.36,4.41) (1.38,4.42) (1.40,4.41) (1.42,4.37) (1.44,4.30) (1.46,4.21) (1.48,4.10) (1.51,3.98) (1.53,3.84) (1.55,3.70) (1.57,3.56) (1.59,3.42) (1.61,3.30) (1.63,3.19) (1.65,3.10) (1.67,3.03) (1.70,2.99) (1.72,2.98) (1.74,2.99) (1.76,3.03) (1.78,3.10) (1.80,3.19) (1.82,3.30) (1.84,3.42) (1.86,3.56) (1.88,3.70) (1.91,3.84) (1.93,3.98) (1.95,4.10) (1.97,4.21) (1.99,4.30) (2.01,4.37) (2.03,4.41) (2.05,4.42) (2.07,4.41) (2.09,4.37) (2.12,4.30) (2.14,4.21) (2.16,4.10) (2.18,3.98) (2.20,3.84) (2.22,3.70) (2.24,3.56) (2.26,3.42) (2.28,3.30) (2.30,3.19) (2.33,3.10) (2.35,3.03) (2.37,2.99) (2.39,2.98) (2.41,2.99) (2.43,3.03) (2.45,3.10) (2.47,3.19) (2.49,3.30) (2.51,3.42) (2.54,3.56) (2.56,3.70) (2.58,3.84) (2.60,3.98) (2.62,4.10) (2.64,4.21) (2.66,4.30) (2.68,4.37) (2.70,4.41) (2.72,4.42) (2.75,4.41) (2.77,4.37) (2.79,4.30) (2.81,4.21) (2.83,4.10) (2.85,3.98) (2.87,3.84) (2.89,3.70) (2.91,3.56) (2.93,3.42) (2.96,3.30) (2.98,3.19) (3.00,3.10) (3.02,3.03) (3.04,2.99) (3.06,2.98) (3.08,2.99) (3.10,3.03) (3.12,3.10) (3.14,3.19) (3.17,3.30) (3.19,3.42) (3.21,3.56) (3.23,3.70) (3.25,3.84) (3.27,3.98) (3.29,4.10) (3.31,4.21) (3.33,4.30) (3.35,4.37) (3.38,4.41) (3.40,4.42) (3.42,4.41) (3.44,4.37) (3.46,4.30) (3.48,4.21) (3.50,4.10) (3.52,3.98) (3.54,3.84) (3.56,3.70) (3.59,3.56) (3.61,3.42) (3.63,3.30) (3.65,3.19) (3.67,3.10) (3.69,3.03) (3.71,2.99) (3.73,2.98) (3.75,2.99) (3.77,3.03) (3.80,3.10) (3.82,3.19) (3.84,3.30) (3.86,3.42) (3.88,3.56) (3.90,3.70) (3.92,3.84) (3.94,3.98) (3.96,4.10) (3.98,4.21) (4.00,4.30) (4.03,4.37) (4.05,4.41) (4.07,4.42) (4.09,4.41) (4.11,4.37) (4.13,4.30) (4.15,4.21) (4.17,4.10) (4.19,3.98) (4.22,3.84) (4.24,3.70) (4.26,3.56) (4.28,3.42) (4.30,3.30) (4.32,3.19) (4.34,3.10) (4.36,3.03) (4.38,2.99) (4.40,2.98) (4.43,2.99) (4.45,3.03) (4.47,3.10) (4.49,3.19) (4.51,3.30) (4.53,3.42) (4.55,3.56) (4.57,3.70) (4.59,3.84) (4.61,3.98) (4.64,4.10) (4.66,4.21) (4.68,4.30) (4.70,4.37) (4.72,4.41)};
\node[lab, text=black!74, anchor=west] at (0.06,4.58) {the frame, as the cut leaves it -- a cliff at each end};
\node[tk, anchor=north east] at (0.18,2.88) {$0$};
\node[tk, anchor=north] at (4.31,2.88) {$400$};
\node[tk, anchor=west] at (5.45,3.70) {n};
\draw[ax] (6.45,4.38) -- (6.45,2.60);
\draw[ax] (6.45,2.60) -- (13.69,2.60);
\draw[black!55] (6.45,2.56) -- (6.45,2.64);
\node[tk, anchor=north] at (6.45,2.55) {$0$};
\draw[black!55] (13.45,2.56) -- (13.45,2.64);
\node[tk, anchor=north] at (13.45,2.55) {$500$};
\node[tk, anchor=west] at (13.73,2.60) {Hz};
\node[tk, anchor=south east] at (6.38,4.33) {dB};
\draw[black!40, thin, densely dotted] (9.95,2.60) -- (9.95,4.08);
\draw[black!55] (9.95,2.56) -- (9.95,2.64);
\node[tk, anchor=north] at (9.95,2.55) {$250$};
\draw[curve] plot [smooth] coordinates {(6.45,3.22) (6.45,3.22) (6.49,3.16) (6.49,3.15) (6.50,3.14) (6.53,3.04) (6.53,3.02) (6.54,3.00) (6.57,2.74) (6.58,2.67) (6.58,2.60) (6.61,2.80) (6.62,2.85) (6.62,2.89) (6.65,3.06) (6.66,3.08) (6.66,3.10) (6.70,3.19) (6.70,3.20) (6.71,3.20) (6.74,3.26) (6.74,3.26) (6.75,3.27) (6.78,3.30) (6.79,3.31) (6.79,3.31) (6.82,3.33) (6.83,3.33) (6.83,3.34) (6.86,3.34) (6.87,3.34) (6.87,3.35) (6.91,3.34) (6.91,3.34) (6.92,3.34) (6.95,3.33) (6.95,3.32) (6.96,3.32) (6.99,3.29) (7.00,3.29) (7.00,3.28) (7.03,3.23) (7.04,3.22) (7.04,3.21) (7.07,3.13) (7.08,3.12) (7.08,3.10) (7.12,2.93) (7.12,2.89) (7.13,2.85) (7.16,2.61) (7.16,2.72) (7.17,2.79) (7.20,3.05) (7.21,3.07) (7.21,3.09) (7.24,3.20) (7.25,3.21) (7.25,3.22) (7.28,3.29) (7.29,3.29) (7.29,3.30) (7.33,3.34) (7.33,3.35) (7.34,3.35) (7.37,3.38) (7.37,3.38) (7.38,3.38) (7.41,3.39) (7.42,3.39) (7.42,3.40) (7.45,3.40) (7.46,3.40) (7.46,3.40) (7.49,3.39) (7.50,3.38) (7.50,3.38) (7.54,3.36) (7.54,3.35) (7.55,3.35) (7.58,3.31) (7.58,3.30) (7.59,3.29) (7.62,3.23) (7.63,3.21) (7.63,3.20) (7.66,3.07) (7.67,3.05) (7.67,3.02) (7.70,2.60) (7.71,2.60) (7.71,2.60) (7.75,3.03) (7.75,3.06) (7.76,3.09) (7.79,3.22) (7.79,3.23) (7.80,3.25) (7.83,3.32) (7.84,3.33) (7.84,3.34) (7.87,3.39) (7.88,3.39) (7.88,3.40) (7.91,3.43) (7.92,3.43) (7.92,3.43) (7.96,3.45) (7.96,3.45) (7.97,3.46) (8.00,3.46) (8.00,3.46) (8.01,3.46) (8.04,3.46) (8.05,3.46) (8.05,3.45) (8.08,3.44) (8.09,3.43) (8.09,3.43) (8.12,3.40) (8.13,3.39) (8.13,3.38) (8.17,3.33) (8.17,3.32) (8.18,3.31) (8.21,3.21) (8.21,3.19) (8.22,3.17) (8.25,2.92) (8.26,2.85) (8.26,2.74) (8.29,2.98) (8.30,3.03) (8.30,3.07) (8.33,3.25) (8.34,3.26) (8.34,3.28) (8.38,3.37) (8.38,3.38) (8.39,3.39) (8.41,3.43) (8.41,3.44) (8.42,3.45) (8.42,3.45) (8.43,3.46) (8.43,3.47) (8.44,3.47) (8.44,3.48) (8.45,3.48) (8.45,3.49) (8.46,3.49) (8.46,3.50) (8.47,3.50) (8.47,3.51) (8.47,3.51) (8.48,3.51) (8.48,3.52) (8.49,3.52) (8.49,3.52) (8.50,3.53) (8.50,3.53) (8.51,3.53) (8.51,3.53) (8.52,3.54) (8.52,3.54) (8.53,3.54) (8.53,3.54) (8.54,3.54) (8.54,3.54) (8.54,3.55) (8.55,3.55) (8.55,3.55) (8.56,3.55) (8.56,3.55) (8.57,3.55) (8.57,3.55) (8.58,3.55) (8.58,3.55) (8.59,3.55) (8.59,3.55) (8.60,3.55) (8.60,3.55) (8.61,3.54) (8.61,3.54) (8.61,3.54) (8.62,3.54) (8.62,3.54) (8.63,3.54) (8.63,3.53) (8.64,3.53) (8.64,3.53) (8.65,3.52) (8.65,3.52) (8.66,3.52) (8.66,3.51) (8.67,3.51) (8.67,3.51) (8.68,3.50) (8.68,3.50) (8.68,3.49) (8.69,3.49) (8.69,3.48) (8.70,3.47) (8.70,3.47) (8.71,3.46) (8.71,3.45) (8.72,3.44) (8.72,3.43) (8.73,3.43) (8.73,3.42) (8.74,3.41) (8.74,3.39) (8.75,3.38) (8.75,3.37) (8.75,3.36) (8.76,3.34) (8.76,3.33) (8.77,3.31) (8.77,3.29) (8.78,3.27) (8.78,3.25) (8.79,3.22) (8.79,3.19) (8.80,3.16) (8.80,3.12) (8.81,3.08) (8.81,3.02) (8.82,2.95) (8.82,2.85) (8.82,2.67) (8.83,2.60) (8.83,2.67) (8.84,2.85) (8.84,2.96) (8.85,3.03) (8.85,3.09) (8.86,3.14) (8.86,3.18) (8.87,3.21) (8.87,3.24) (8.88,3.27) (8.88,3.29) (8.89,3.32) (8.89,3.34) (8.89,3.36) (8.90,3.37) (8.90,3.39) (8.91,3.41) (8.91,3.42) (8.92,3.44) (8.92,3.45) (8.93,3.46) (8.93,3.47) (8.94,3.48) (8.94,3.49) (8.95,3.51) (8.95,3.51) (8.96,3.52) (8.96,3.53) (8.96,3.54) (8.97,3.55) (8.97,3.56) (8.98,3.56) (8.98,3.57) (8.99,3.58) (8.99,3.59) (9.00,3.59) (9.00,3.60) (9.01,3.60) (9.01,3.61) (9.02,3.61) (9.02,3.62) (9.03,3.62) (9.03,3.63) (9.03,3.63) (9.04,3.64) (9.04,3.64) (9.05,3.64) (9.05,3.65) (9.06,3.65) (9.06,3.66) (9.07,3.66) (9.07,3.66) (9.08,3.66) (9.08,3.67) (9.09,3.67) (9.09,3.67) (9.10,3.67) (9.10,3.67) (9.10,3.68) (9.11,3.68) (9.11,3.68) (9.12,3.68) (9.12,3.68) (9.13,3.68) (9.13,3.68) (9.14,3.68) (9.14,3.68) (9.15,3.68) (9.15,3.68) (9.16,3.68) (9.16,3.68) (9.17,3.68) (9.17,3.68) (9.17,3.68) (9.18,3.68) (9.18,3.68) (9.19,3.68) (9.19,3.68) (9.20,3.67) (9.20,3.67) (9.21,3.67) (9.21,3.67) (9.22,3.66) (9.22,3.66) (9.23,3.66) (9.23,3.65) (9.24,3.65) (9.24,3.65) (9.24,3.64) (9.25,3.64) (9.25,3.63) (9.26,3.62) (9.26,3.62) (9.27,3.61) (9.27,3.61) (9.28,3.60) (9.28,3.59) (9.29,3.58) (9.29,3.57) (9.30,3.56) (9.30,3.55) (9.31,3.54) (9.31,3.53) (9.31,3.52) (9.32,3.51) (9.32,3.49) (9.33,3.47) (9.33,3.46) (9.34,3.44) (9.34,3.41) (9.35,3.39) (9.35,3.36) (9.36,3.33) (9.36,3.29) (9.37,3.25) (9.37,3.19) (9.38,3.12) (9.38,3.02) (9.38,2.85) (9.39,2.60) (9.39,2.85) (9.40,3.03) (9.40,3.14) (9.41,3.21) (9.41,3.27) (9.42,3.32) (9.42,3.36) (9.43,3.40) (9.43,3.43) (9.44,3.46) (9.44,3.48) (9.45,3.51) (9.45,3.53) (9.45,3.55) (9.46,3.57) (9.46,3.59) (9.47,3.60) (9.47,3.62) (9.48,3.64) (9.48,3.65) (9.49,3.66) (9.49,3.68) (9.50,3.69) (9.50,3.70) (9.51,3.71) (9.51,3.73) (9.52,3.74) (9.52,3.75) (9.52,3.76) (9.53,3.77) (9.53,3.78) (9.54,3.79) (9.54,3.79) (9.55,3.80) (9.55,3.81) (9.56,3.82) (9.56,3.83) (9.57,3.83) (9.57,3.84) (9.58,3.85) (9.58,3.86) (9.59,3.86) (9.59,3.87) (9.59,3.88) (9.60,3.88) (9.60,3.89) (9.61,3.89) (9.61,3.90) (9.62,3.91) (9.62,3.91) (9.63,3.92) (9.63,3.92) (9.64,3.93) (9.64,3.93) (9.65,3.94) (9.65,3.94) (9.66,3.95) (9.66,3.95) (9.66,3.95) (9.67,3.96) (9.67,3.96) (9.68,3.97) (9.68,3.97) (9.69,3.98) (9.69,3.98) (9.70,3.98) (9.70,3.99) (9.71,3.99) (9.71,3.99) (9.72,4.00) (9.72,4.00) (9.73,4.00) (9.73,4.01) (9.73,4.01) (9.74,4.01) (9.74,4.02) (9.75,4.02) (9.75,4.02) (9.76,4.02) (9.76,4.03) (9.77,4.03) (9.77,4.03) (9.78,4.03) (9.78,4.04) (9.79,4.04) (9.79,4.04) (9.80,4.04) (9.80,4.04) (9.80,4.05) (9.81,4.05) (9.81,4.05) (9.82,4.05) (9.82,4.05) (9.83,4.05) (9.83,4.06) (9.84,4.06) (9.84,4.06) (9.85,4.06) (9.85,4.06) (9.86,4.06) (9.86,4.06) (9.87,4.07) (9.87,4.07) (9.87,4.07) (9.88,4.07) (9.88,4.07) (9.89,4.07) (9.89,4.07) (9.90,4.07) (9.90,4.07) (9.91,4.07) (9.91,4.07) (9.92,4.07) (9.92,4.07) (9.93,4.07) (9.93,4.07) (9.94,4.07) (9.94,4.07) (9.94,4.07) (9.95,4.08) (9.95,4.07) (9.96,4.07) (9.96,4.07) (9.97,4.07) (9.97,4.07) (9.98,4.07) (9.98,4.07) (9.99,4.07) (9.99,4.07) (10.00,4.07) (10.00,4.07) (10.01,4.07) (10.01,4.07) (10.01,4.07) (10.02,4.07) (10.02,4.07) (10.03,4.07) (10.03,4.07) (10.04,4.06) (10.04,4.06) (10.05,4.06) (10.05,4.06) (10.06,4.06) (10.06,4.06) (10.07,4.06) (10.07,4.05) (10.08,4.05) (10.08,4.05) (10.08,4.05) (10.09,4.05) (10.09,4.05) (10.10,4.04) (10.10,4.04) (10.11,4.04) (10.11,4.04) (10.12,4.04) (10.12,4.03) (10.13,4.03) (10.13,4.03) (10.14,4.03) (10.14,4.02) (10.15,4.02) (10.15,4.02) (10.15,4.02) (10.16,4.01) (10.16,4.01) (10.17,4.01) (10.17,4.00) (10.18,4.00) (10.18,4.00) (10.19,3.99) (10.19,3.99) (10.20,3.99) (10.20,3.98) (10.21,3.98) (10.21,3.98) (10.22,3.97) (10.22,3.97) (10.22,3.96) (10.23,3.96) (10.23,3.95) (10.24,3.95) (10.24,3.95) (10.25,3.94) (10.25,3.94) (10.26,3.93) (10.26,3.93) (10.27,3.92) (10.27,3.92) (10.28,3.91) (10.28,3.91) (10.29,3.90) (10.29,3.89) (10.29,3.89) (10.30,3.88) (10.30,3.88) (10.31,3.87) (10.31,3.86) (10.32,3.86) (10.32,3.85) (10.33,3.84) (10.33,3.83) (10.34,3.83) (10.34,3.82) (10.35,3.81) (10.35,3.80) (10.36,3.79) (10.36,3.79) (10.36,3.78) (10.37,3.77) (10.37,3.76) (10.38,3.75) (10.38,3.74) (10.39,3.73) (10.39,3.71) (10.40,3.70) (10.40,3.69) (10.41,3.68) (10.41,3.66) (10.42,3.65) (10.42,3.64) (10.43,3.62) (10.43,3.60) (10.43,3.59) (10.44,3.57) (10.44,3.55) (10.45,3.53) (10.45,3.51) (10.46,3.48) (10.46,3.46) (10.47,3.43) (10.47,3.40) (10.48,3.36) (10.48,3.32) (10.49,3.27) (10.49,3.21) (10.50,3.14) (10.50,3.03) (10.50,2.85) (10.51,2.60) (10.51,2.85) (10.52,3.02) (10.52,3.12) (10.53,3.19) (10.53,3.25) (10.54,3.29) (10.54,3.33) (10.55,3.36) (10.55,3.39) (10.56,3.41) (10.56,3.44) (10.57,3.46) (10.57,3.47) (10.57,3.49) (10.58,3.51) (10.58,3.52) (10.59,3.53) (10.59,3.54) (10.60,3.55) (10.60,3.56) (10.61,3.57) (10.61,3.58) (10.62,3.59) (10.62,3.60) (10.63,3.61) (10.63,3.61) (10.64,3.62) (10.64,3.62) (10.64,3.63) (10.65,3.64) (10.65,3.64) (10.66,3.65) (10.66,3.65) (10.67,3.65) (10.67,3.66) (10.68,3.66) (10.68,3.66) (10.69,3.67) (10.69,3.67) (10.70,3.67) (10.70,3.67) (10.71,3.68) (10.71,3.68) (10.71,3.68) (10.72,3.68) (10.72,3.68) (10.73,3.68) (10.73,3.68) (10.74,3.68) (10.74,3.68) (10.75,3.68) (10.75,3.68) (10.76,3.68) (10.76,3.68) (10.77,3.68) (10.77,3.68) (10.78,3.68) (10.78,3.68) (10.78,3.68) (10.79,3.68) (10.79,3.68) (10.80,3.67) (10.80,3.67) (10.81,3.67) (10.81,3.67) (10.82,3.67) (10.82,3.66) (10.83,3.66) (10.83,3.66) (10.84,3.66) (10.84,3.65) (10.85,3.65) (10.85,3.64) (10.85,3.64) (10.86,3.64) (10.86,3.63) (10.87,3.63) (10.87,3.62) (10.88,3.62) (10.88,3.61) (10.89,3.61) (10.89,3.60) (10.90,3.60) (10.90,3.59) (10.91,3.59) (10.91,3.58) (10.92,3.57) (10.92,3.56) (10.92,3.56) (10.93,3.55) (10.93,3.54) (10.94,3.53) (10.94,3.52) (10.95,3.51) (10.95,3.51) (10.96,3.49) (10.96,3.48) (10.97,3.47) (10.97,3.46) (10.98,3.45) (10.98,3.44) (10.99,3.42) (10.99,3.41) (10.99,3.39) (11.00,3.37) (11.00,3.36) (11.01,3.34) (11.01,3.32) (11.02,3.29) (11.02,3.27) (11.03,3.24) (11.03,3.21) (11.04,3.18) (11.04,3.14) (11.05,3.09) (11.05,3.03) (11.06,2.96) (11.06,2.85) (11.06,2.67) (11.07,2.60) (11.07,2.67) (11.08,2.85) (11.08,2.95) (11.09,3.02) (11.09,3.08) (11.10,3.12) (11.10,3.16) (11.11,3.19) (11.11,3.22) (11.12,3.25) (11.12,3.27) (11.13,3.29) (11.13,3.31) (11.13,3.33) (11.14,3.34) (11.14,3.36) (11.15,3.37) (11.15,3.38) (11.16,3.39) (11.16,3.41) (11.17,3.42) (11.17,3.43) (11.18,3.43) (11.18,3.44) (11.19,3.45) (11.19,3.46) (11.20,3.47) (11.20,3.47) (11.20,3.48) (11.21,3.49) (11.21,3.49) (11.22,3.50) (11.22,3.50) (11.23,3.51) (11.23,3.51) (11.24,3.51) (11.24,3.52) (11.25,3.52) (11.25,3.52) (11.26,3.53) (11.26,3.53) (11.27,3.53) (11.27,3.54) (11.27,3.54) (11.28,3.54) (11.28,3.54) (11.29,3.54) (11.29,3.54) (11.30,3.55) (11.30,3.55) (11.31,3.55) (11.31,3.55) (11.32,3.55) (11.32,3.55) (11.33,3.55) (11.33,3.55) (11.34,3.55) (11.34,3.55) (11.34,3.55) (11.35,3.55) (11.35,3.55) (11.36,3.54) (11.36,3.54) (11.37,3.54) (11.37,3.54) (11.38,3.54) (11.38,3.54) (11.39,3.53) (11.39,3.53) (11.40,3.53) (11.40,3.53) (11.41,3.52) (11.41,3.52) (11.41,3.52) (11.42,3.51) (11.42,3.51) (11.43,3.51) (11.43,3.50) (11.44,3.50) (11.44,3.49) (11.45,3.49) (11.45,3.48) (11.46,3.48) (11.46,3.47) (11.47,3.47) (11.47,3.46) (11.48,3.45) (11.48,3.45) (11.48,3.44) (11.49,3.43) (11.49,3.43) (11.53,3.36) (11.53,3.35) (11.54,3.34) (11.57,3.23) (11.57,3.21) (11.58,3.19) (11.61,2.92) (11.62,2.85) (11.62,2.75) (11.65,2.97) (11.66,3.02) (11.66,3.06) (11.69,3.23) (11.70,3.24) (11.70,3.26) (11.74,3.34) (11.74,3.35) (11.75,3.36) (11.78,3.40) (11.78,3.41) (11.79,3.41) (11.82,3.44) (11.83,3.44) (11.83,3.45) (11.86,3.46) (11.87,3.46) (11.87,3.46) (11.90,3.46) (11.91,3.46) (11.91,3.46) (11.95,3.45) (11.95,3.45) (11.96,3.45) (11.99,3.42) (11.99,3.42) (12.00,3.42) (12.03,3.38) (12.04,3.37) (12.04,3.37) (12.07,3.31) (12.08,3.30) (12.08,3.29) (12.11,3.20) (12.12,3.19) (12.12,3.17) (12.16,2.99) (12.16,2.95) (12.17,2.91) (12.20,2.67) (12.20,2.77) (12.21,2.85) (12.24,3.10) (12.25,3.12) (12.25,3.14) (12.28,3.24) (12.29,3.25) (12.29,3.26) (12.32,3.32) (12.33,3.32) (12.33,3.33) (12.37,3.36) (12.37,3.37) (12.38,3.37) (12.41,3.39) (12.41,3.39) (12.42,3.39) (12.45,3.40) (12.46,3.40) (12.46,3.40) (12.49,3.39) (12.50,3.39) (12.50,3.39) (12.53,3.37) (12.54,3.37) (12.54,3.37) (12.58,3.34) (12.58,3.33) (12.59,3.33) (12.62,3.28) (12.62,3.27) (12.63,3.26) (12.66,3.19) (12.67,3.17) (12.67,3.16) (12.70,3.03) (12.71,3.00) (12.71,2.97) (12.74,2.60) (12.75,2.60) (12.75,2.60) (12.79,2.96) (12.79,2.99) (12.80,3.02) (12.83,3.15) (12.83,3.16) (12.84,3.17) (12.87,3.24) (12.88,3.25) (12.88,3.25) (12.91,3.30) (12.92,3.30) (12.92,3.30) (12.95,3.33) (12.96,3.33) (12.96,3.33) (13.00,3.34) (13.00,3.34) (13.01,3.34) (13.04,3.34) (13.04,3.34) (13.05,3.34) (13.08,3.33) (13.09,3.33) (13.09,3.32) (13.12,3.30) (13.13,3.30) (13.13,3.29) (13.16,3.25) (13.17,3.24) (13.17,3.24) (13.21,3.17) (13.21,3.16) (13.22,3.15) (13.25,3.05) (13.25,3.03) (13.26,3.00) (13.29,2.75) (13.30,2.67) (13.30,2.60) (13.33,2.80) (13.34,2.85) (13.34,2.88) (13.37,3.05) (13.38,3.07) (13.38,3.09) (13.42,3.17) (13.42,3.18) (13.43,3.19)};
\draw[dim] (9.39,4.21) -- (10.51,4.21);
\draw[tick] (9.39,4.17) -- (9.39,4.26);
\draw[tick] (10.51,4.17) -- (10.51,4.26);
\node[lab, anchor=south] at (9.95,4.23) {$80$ Hz wide};
\draw[ridge] (6.45,3.68) -- (13.45,3.68);
\fill[black!72] (10.75,3.68) circle (0.04);
\draw[tick] (6.40,3.68) -- (6.50,3.68);
\node[tk, anchor=east] at (6.36,3.68) {$-13$};
\draw[gone] plot [smooth] coordinates {(0.12,1.71) (0.14,1.60) (0.16,1.48) (0.18,1.34) (0.20,1.20) (0.23,1.06) (0.25,0.92) (0.27,0.80) (0.29,0.69) (0.31,0.60) (0.33,0.53) (0.35,0.49) (0.37,0.48) (0.39,0.49) (0.41,0.53) (0.43,0.60) (0.46,0.69) (0.48,0.80) (0.50,0.92) (0.52,1.06) (4.74,1.92) (4.76,1.91) (4.78,1.87) (4.80,1.80) (4.82,1.71) (4.85,1.60) (4.87,1.48) (4.89,1.34) (4.91,1.20) (4.93,1.06) (4.95,0.92) (4.97,0.80) (4.99,0.69) (5.01,0.60) (5.03,0.53) (5.06,0.49) (5.08,0.48) (5.10,0.49) (5.12,0.53) (5.14,0.60)};
\draw[ax] (0.06,1.20) -- (5.41,1.20);
\draw[black!58, thin] (0.12,0.40) -- (0.12,2.00);
\draw[black!58, thin] (4.31,0.40) -- (4.31,2.00);
\draw[env] plot [smooth] coordinates {(0.54,1.26) (0.56,1.26) (0.58,1.26) (0.60,1.26) (0.62,1.26) (0.65,1.26) (0.67,1.26) (0.69,1.27) (0.71,1.27) (0.73,1.27) (0.75,1.27) (0.77,1.28) (0.79,1.28) (0.81,1.28) (0.83,1.29) (0.86,1.29) (0.88,1.30) (0.90,1.30) (0.92,1.31) (0.94,1.32) (0.96,1.32) (0.98,1.33) (1.00,1.33) (1.02,1.34) (1.04,1.35) (1.06,1.36) (1.09,1.36) (1.11,1.37) (1.13,1.38) (1.15,1.39) (1.17,1.39) (1.19,1.40) (1.21,1.41) (1.23,1.42) (1.25,1.43) (1.27,1.44) (1.30,1.45) (1.32,1.46) (1.34,1.47) (1.36,1.48) (1.38,1.49) (1.40,1.50) (1.42,1.51) (1.44,1.52) (1.46,1.53) (1.48,1.54) (1.51,1.55) (1.53,1.56) (1.55,1.57) (1.57,1.58) (1.59,1.59) (1.61,1.60) (1.63,1.61) (1.65,1.62) (1.67,1.63) (1.70,1.64) (1.72,1.65) (1.74,1.66) (1.76,1.67) (1.78,1.68) (1.80,1.69) (1.82,1.70) (1.84,1.71) (1.86,1.72) (1.88,1.73) (1.91,1.74) (1.93,1.75) (1.95,1.76) (1.97,1.77) (1.99,1.78) (2.01,1.78) (2.03,1.79) (2.05,1.80) (2.07,1.81) (2.09,1.82) (2.12,1.82) (2.14,1.83) (2.16,1.84) (2.18,1.85) (2.20,1.85) (2.22,1.86) (2.24,1.86) (2.26,1.87) (2.28,1.87) (2.30,1.88) (2.33,1.88) (2.35,1.89) (2.37,1.89) (2.39,1.90) (2.41,1.90) (2.43,1.90) (2.45,1.91) (2.47,1.91) (2.49,1.91) (2.51,1.91) (2.54,1.92) (2.56,1.92) (2.58,1.92) (2.60,1.92) (2.62,1.92) (2.64,1.92) (2.66,1.92) (2.68,1.92) (2.70,1.92) (2.72,1.92) (2.75,1.92) (2.77,1.91) (2.79,1.91) (2.81,1.91) (2.83,1.91) (2.85,1.90) (2.87,1.90) (2.89,1.90) (2.91,1.89) (2.93,1.89) (2.96,1.88) (2.98,1.88) (3.00,1.87) (3.02,1.87) (3.04,1.86) (3.06,1.85) (3.08,1.85) (3.10,1.84) (3.12,1.84) (3.14,1.83) (3.17,1.82) (3.19,1.81) (3.21,1.81) (3.23,1.80) (3.25,1.79) (3.27,1.78) (3.29,1.77) (3.31,1.76) (3.33,1.75) (3.35,1.75) (3.38,1.74) (3.40,1.73) (3.42,1.72) (3.44,1.71) (3.46,1.70) (3.48,1.69) (3.50,1.68) (3.52,1.67) (3.54,1.66) (3.56,1.65) (3.59,1.64) (3.61,1.63) (3.63,1.62) (3.65,1.61) (3.67,1.60) (3.69,1.58) (3.71,1.57) (3.73,1.56) (3.75,1.55) (3.77,1.54) (3.80,1.53) (3.82,1.52) (3.84,1.51) (3.86,1.50) (3.88,1.49) (3.90,1.48) (3.92,1.47) (3.94,1.46) (3.96,1.45) (3.98,1.44) (4.00,1.43) (4.03,1.43) (4.05,1.42) (4.07,1.41) (4.09,1.40) (4.11,1.39) (4.13,1.38) (4.15,1.37) (4.17,1.37) (4.19,1.36) (4.22,1.35) (4.24,1.34) (4.26,1.34) (4.28,1.33) (4.30,1.32) (4.32,1.32) (4.34,1.31) (4.36,1.31) (4.38,1.30) (4.40,1.30) (4.43,1.29) (4.45,1.29) (4.47,1.28) (4.49,1.28) (4.51,1.28) (4.53,1.27) (4.55,1.27) (4.57,1.27) (4.59,1.26) (4.61,1.26) (4.64,1.26) (4.66,1.26) (4.68,1.26) (4.70,1.26) (4.72,1.26)};
\draw[env] plot [smooth] coordinates {(0.54,1.14) (0.56,1.14) (0.58,1.14) (0.60,1.14) (0.62,1.14) (0.65,1.14) (0.67,1.14) (0.69,1.13) (0.71,1.13) (0.73,1.13) (0.75,1.13) (0.77,1.12) (0.79,1.12) (0.81,1.12) (0.83,1.11) (0.86,1.11) (0.88,1.10) (0.90,1.10) (0.92,1.09) (0.94,1.08) (0.96,1.08) (0.98,1.07) (1.00,1.07) (1.02,1.06) (1.04,1.05) (1.06,1.04) (1.09,1.04) (1.11,1.03) (1.13,1.02) (1.15,1.01) (1.17,1.01) (1.19,1.00) (1.21,0.99) (1.23,0.98) (1.25,0.97) (1.27,0.96) (1.30,0.95) (1.32,0.94) (1.34,0.93) (1.36,0.92) (1.38,0.91) (1.40,0.90) (1.42,0.89) (1.44,0.88) (1.46,0.87) (1.48,0.86) (1.51,0.85) (1.53,0.84) (1.55,0.83) (1.57,0.82) (1.59,0.81) (1.61,0.80) (1.63,0.79) (1.65,0.78) (1.67,0.77) (1.70,0.76) (1.72,0.75) (1.74,0.74) (1.76,0.73) (1.78,0.72) (1.80,0.71) (1.82,0.70) (1.84,0.69) (1.86,0.68) (1.88,0.67) (1.91,0.66) (1.93,0.65) (1.95,0.64) (1.97,0.63) (1.99,0.62) (2.01,0.62) (2.03,0.61) (2.05,0.60) (2.07,0.59) (2.09,0.58) (2.12,0.58) (2.14,0.57) (2.16,0.56) (2.18,0.55) (2.20,0.55) (2.22,0.54) (2.24,0.54) (2.26,0.53) (2.28,0.53) (2.30,0.52) (2.33,0.52) (2.35,0.51) (2.37,0.51) (2.39,0.50) (2.41,0.50) (2.43,0.50) (2.45,0.49) (2.47,0.49) (2.49,0.49) (2.51,0.49) (2.54,0.48) (2.56,0.48) (2.58,0.48) (2.60,0.48) (2.62,0.48) (2.64,0.48) (2.66,0.48) (2.68,0.48) (2.70,0.48) (2.72,0.48) (2.75,0.48) (2.77,0.49) (2.79,0.49) (2.81,0.49) (2.83,0.49) (2.85,0.50) (2.87,0.50) (2.89,0.50) (2.91,0.51) (2.93,0.51) (2.96,0.52) (2.98,0.52) (3.00,0.53) (3.02,0.53) (3.04,0.54) (3.06,0.55) (3.08,0.55) (3.10,0.56) (3.12,0.56) (3.14,0.57) (3.17,0.58) (3.19,0.59) (3.21,0.59) (3.23,0.60) (3.25,0.61) (3.27,0.62) (3.29,0.63) (3.31,0.64) (3.33,0.65) (3.35,0.65) (3.38,0.66) (3.40,0.67) (3.42,0.68) (3.44,0.69) (3.46,0.70) (3.48,0.71) (3.50,0.72) (3.52,0.73) (3.54,0.74) (3.56,0.75) (3.59,0.76) (3.61,0.77) (3.63,0.78) (3.65,0.79) (3.67,0.80) (3.69,0.82) (3.71,0.83) (3.73,0.84) (3.75,0.85) (3.77,0.86) (3.80,0.87) (3.82,0.88) (3.84,0.89) (3.86,0.90) (3.88,0.91) (3.90,0.92) (3.92,0.93) (3.94,0.94) (3.96,0.95) (3.98,0.96) (4.00,0.97) (4.03,0.97) (4.05,0.98) (4.07,0.99) (4.09,1.00) (4.11,1.01) (4.13,1.02) (4.15,1.03) (4.17,1.03) (4.19,1.04) (4.22,1.05) (4.24,1.06) (4.26,1.06) (4.28,1.07) (4.30,1.08) (4.32,1.08) (4.34,1.09) (4.36,1.09) (4.38,1.10) (4.40,1.10) (4.43,1.11) (4.45,1.11) (4.47,1.12) (4.49,1.12) (4.51,1.12) (4.53,1.13) (4.55,1.13) (4.57,1.13) (4.59,1.14) (4.61,1.14) (4.64,1.14) (4.66,1.14) (4.68,1.14) (4.70,1.14) (4.72,1.14)};
\draw[curve] plot [smooth] coordinates {(0.54,1.20) (0.56,1.21) (0.58,1.22) (0.60,1.23) (0.62,1.24) (0.65,1.25) (0.67,1.26) (0.69,1.26) (0.71,1.27) (0.73,1.27) (0.75,1.27) (0.77,1.26) (0.79,1.26) (0.81,1.25) (0.83,1.23) (0.86,1.22) (0.88,1.20) (0.90,1.18) (0.92,1.16) (0.94,1.14) (0.96,1.11) (0.98,1.09) (1.00,1.08) (1.02,1.06) (1.04,1.05) (1.06,1.05) (1.09,1.05) (1.11,1.06) (1.13,1.07) (1.15,1.10) (1.17,1.13) (1.19,1.16) (1.21,1.20) (1.23,1.24) (1.25,1.29) (1.27,1.33) (1.30,1.38) (1.32,1.41) (1.34,1.45) (1.36,1.47) (1.38,1.49) (1.40,1.49) (1.42,1.48) (1.44,1.46) (1.46,1.43) (1.48,1.39) (1.51,1.33) (1.53,1.27) (1.55,1.20) (1.57,1.13) (1.59,1.05) (1.61,0.98) (1.63,0.91) (1.65,0.85) (1.67,0.80) (1.70,0.77) (1.72,0.75) (1.74,0.75) (1.76,0.76) (1.78,0.80) (1.80,0.85) (1.82,0.92) (1.84,1.00) (1.86,1.10) (1.88,1.20) (1.91,1.31) (1.93,1.41) (1.95,1.51) (1.97,1.60) (1.99,1.68) (2.01,1.74) (2.03,1.78) (2.05,1.80) (2.07,1.80) (2.09,1.77) (2.12,1.72) (2.14,1.65) (2.16,1.55) (2.18,1.45) (2.20,1.33) (2.22,1.20) (2.24,1.07) (2.26,0.94) (2.28,0.83) (2.30,0.72) (2.33,0.63) (2.35,0.56) (2.37,0.52) (2.39,0.50) (2.41,0.51) (2.43,0.55) (2.45,0.61) (2.47,0.70) (2.49,0.80) (2.51,0.93) (2.54,1.06) (2.56,1.20) (2.58,1.34) (2.60,1.48) (2.62,1.60) (2.64,1.71) (2.66,1.80) (2.68,1.86) (2.70,1.90) (2.72,1.92) (2.75,1.90) (2.77,1.86) (2.79,1.79) (2.81,1.70) (2.83,1.59) (2.85,1.47) (2.87,1.34) (2.89,1.20) (2.91,1.07) (2.93,0.94) (2.96,0.82) (2.98,0.72) (3.00,0.64) (3.02,0.58) (3.04,0.55) (3.06,0.55) (3.08,0.56) (3.10,0.61) (3.12,0.67) (3.14,0.76) (3.17,0.86) (3.19,0.97) (3.21,1.08) (3.23,1.20) (3.25,1.31) (3.27,1.42) (3.29,1.52) (3.31,1.60) (3.33,1.66) (3.35,1.70) (3.38,1.73) (3.40,1.73) (3.42,1.71) (3.44,1.67) (3.46,1.61) (3.48,1.54) (3.50,1.47) (3.52,1.38) (3.54,1.29) (3.56,1.20) (3.59,1.11) (3.61,1.04) (3.63,0.97) (3.65,0.91) (3.67,0.87) (3.69,0.84) (3.71,0.83) (3.73,0.84) (3.75,0.85) (3.77,0.88) (3.80,0.92) (3.82,0.97) (3.84,1.03) (3.86,1.08) (3.88,1.14) (3.90,1.20) (3.92,1.25) (3.94,1.30) (3.96,1.34) (3.98,1.37) (4.00,1.40) (4.03,1.41) (4.05,1.41) (4.07,1.41) (4.09,1.40) (4.11,1.38) (4.13,1.35) (4.15,1.32) (4.17,1.29) (4.19,1.26) (4.22,1.23) (4.24,1.20) (4.26,1.17) (4.28,1.15) (4.30,1.13) (4.32,1.12) (4.34,1.11) (4.36,1.10) (4.38,1.10) (4.40,1.10) (4.43,1.11) (4.45,1.12) (4.47,1.13) (4.49,1.14) (4.51,1.16) (4.53,1.17) (4.55,1.19) (4.57,1.20) (4.59,1.21) (4.61,1.22) (4.64,1.23) (4.66,1.24) (4.68,1.25) (4.70,1.25) (4.72,1.26)};
\node[lab, text=black!74, anchor=west] at (0.06,2.08) {the same frame, faded to $0.08$};
\node[tk, anchor=north east] at (0.18,0.38) {$0$};
\node[tk, anchor=north] at (4.31,0.38) {$400$};
\node[tk, anchor=west] at (5.45,1.20) {n};
\draw[ax] (6.45,1.87) -- (6.45,0.10);
\draw[ax] (6.45,0.10) -- (13.69,0.10);
\draw[black!55] (6.45,0.06) -- (6.45,0.13);
\node[tk, anchor=north] at (6.45,0.05) {$0$};
\draw[black!55] (13.45,0.06) -- (13.45,0.13);
\node[tk, anchor=north] at (13.45,0.05) {$500$};
\node[tk, anchor=west] at (13.73,0.10) {Hz};
\node[tk, anchor=south east] at (6.38,1.83) {dB};
\draw[black!40, thin, densely dotted] (9.95,0.10) -- (9.95,1.57);
\draw[black!55] (9.95,0.06) -- (9.95,0.13);
\node[tk, anchor=north] at (9.95,0.05) {$250$};
\draw[curve] plot [smooth] coordinates {(6.45,0.19) (6.45,0.19) (6.49,0.13) (6.49,0.12) (6.50,0.11) (6.53,0.10) (6.53,0.10) (6.54,0.10) (6.57,0.10) (6.58,0.10) (6.58,0.10) (6.61,0.10) (6.62,0.10) (6.62,0.10) (6.65,0.10) (6.66,0.10) (6.66,0.10) (6.70,0.14) (6.70,0.15) (6.71,0.16) (6.74,0.22) (6.74,0.22) (6.75,0.23) (6.78,0.26) (6.79,0.27) (6.79,0.27) (6.82,0.29) (6.83,0.29) (6.83,0.29) (6.86,0.30) (6.87,0.30) (6.87,0.30) (6.91,0.30) (6.91,0.30) (6.92,0.29) (6.95,0.28) (6.95,0.28) (6.96,0.27) (6.99,0.24) (7.00,0.24) (7.00,0.23) (7.03,0.18) (7.04,0.17) (7.04,0.17) (7.07,0.10) (7.08,0.10) (7.08,0.10) (7.12,0.10) (7.12,0.10) (7.13,0.10) (7.16,0.10) (7.16,0.10) (7.17,0.10) (7.20,0.10) (7.21,0.10) (7.21,0.10) (7.24,0.13) (7.25,0.14) (7.25,0.15) (7.28,0.21) (7.29,0.22) (7.29,0.23) (7.33,0.27) (7.33,0.27) (7.34,0.28) (7.37,0.30) (7.37,0.30) (7.38,0.30) (7.41,0.31) (7.42,0.31) (7.42,0.32) (7.45,0.31) (7.46,0.31) (7.46,0.31) (7.49,0.30) (7.50,0.30) (7.50,0.30) (7.54,0.27) (7.54,0.27) (7.55,0.26) (7.58,0.22) (7.58,0.21) (7.59,0.20) (7.62,0.13) (7.63,0.12) (7.63,0.11) (7.66,0.10) (7.67,0.10) (7.67,0.10) (7.70,0.10) (7.71,0.10) (7.71,0.10) (7.75,0.10) (7.75,0.10) (7.76,0.10) (7.79,0.10) (7.79,0.10) (7.80,0.11) (7.83,0.18) (7.84,0.19) (7.84,0.20) (7.87,0.24) (7.88,0.24) (7.88,0.25) (7.91,0.27) (7.92,0.27) (7.92,0.28) (7.96,0.29) (7.96,0.29) (7.97,0.29) (8.00,0.29) (8.00,0.28) (8.01,0.28) (8.04,0.27) (8.05,0.27) (8.05,0.26) (8.08,0.24) (8.09,0.23) (8.09,0.23) (8.12,0.18) (8.13,0.17) (8.13,0.17) (8.17,0.10) (8.17,0.10) (8.18,0.10) (8.21,0.10) (8.21,0.10) (8.22,0.10) (8.25,0.10) (8.26,0.10) (8.26,0.10) (8.29,0.10) (8.30,0.10) (8.30,0.10) (8.33,0.10) (8.34,0.10) (8.34,0.10) (8.38,0.10) (8.38,0.10) (8.39,0.10) (8.41,0.10) (8.41,0.10) (8.42,0.10) (8.42,0.10) (8.43,0.10) (8.43,0.10) (8.44,0.10) (8.44,0.10) (8.45,0.10) (8.45,0.10) (8.46,0.10) (8.46,0.10) (8.47,0.10) (8.47,0.10) (8.47,0.10) (8.48,0.10) (8.48,0.10) (8.49,0.10) (8.49,0.10) (8.50,0.10) (8.50,0.10) (8.51,0.10) (8.51,0.10) (8.52,0.10) (8.52,0.10) (8.53,0.10) (8.53,0.10) (8.54,0.10) (8.54,0.10) (8.54,0.10) (8.55,0.10) (8.55,0.10) (8.56,0.10) (8.56,0.10) (8.57,0.10) (8.57,0.10) (8.58,0.10) (8.58,0.10) (8.59,0.11) (8.59,0.12) (8.60,0.13) (8.60,0.14) (8.61,0.15) (8.61,0.16) (8.61,0.17) (8.62,0.18) (8.62,0.19) (8.63,0.20) (8.63,0.21) (8.64,0.21) (8.64,0.22) (8.65,0.23) (8.65,0.23) (8.66,0.24) (8.66,0.24) (8.67,0.25) (8.67,0.25) (8.68,0.25) (8.68,0.26) (8.68,0.26) (8.69,0.26) (8.69,0.26) (8.70,0.26) (8.70,0.26) (8.71,0.26) (8.71,0.26) (8.72,0.26) (8.72,0.26) (8.73,0.26) (8.73,0.25) (8.74,0.25) (8.74,0.24) (8.75,0.24) (8.75,0.23) (8.75,0.22) (8.76,0.21) (8.76,0.20) (8.77,0.19) (8.77,0.18) (8.78,0.16) (8.78,0.14) (8.79,0.12) (8.79,0.10) (8.80,0.10) (8.80,0.10) (8.81,0.10) (8.81,0.10) (8.82,0.10) (8.82,0.10) (8.82,0.10) (8.83,0.10) (8.83,0.10) (8.84,0.10) (8.84,0.10) (8.85,0.11) (8.85,0.16) (8.86,0.21) (8.86,0.25) (8.87,0.28) (8.87,0.31) (8.88,0.34) (8.88,0.37) (8.89,0.40) (8.89,0.42) (8.89,0.45) (8.90,0.47) (8.90,0.49) (8.91,0.51) (8.91,0.53) (8.92,0.55) (8.92,0.57) (8.93,0.58) (8.93,0.60) (8.94,0.62) (8.94,0.63) (8.95,0.65) (8.95,0.66) (8.96,0.68) (8.96,0.69) (8.96,0.70) (8.97,0.72) (8.97,0.73) (8.98,0.74) (8.98,0.76) (8.99,0.77) (8.99,0.78) (9.00,0.79) (9.00,0.80) (9.01,0.81) (9.01,0.83) (9.02,0.84) (9.02,0.85) (9.03,0.86) (9.03,0.87) (9.03,0.88) (9.04,0.89) (9.04,0.90) (9.05,0.91) (9.05,0.92) (9.06,0.93) (9.06,0.94) (9.07,0.94) (9.07,0.95) (9.08,0.96) (9.08,0.97) (9.09,0.98) (9.09,0.99) (9.10,1.00) (9.10,1.00) (9.10,1.01) (9.11,1.02) (9.11,1.03) (9.12,1.04) (9.12,1.04) (9.13,1.05) (9.13,1.06) (9.14,1.07) (9.14,1.07) (9.15,1.08) (9.15,1.09) (9.16,1.09) (9.16,1.10) (9.17,1.11) (9.17,1.11) (9.17,1.12) (9.18,1.13) (9.18,1.13) (9.19,1.14) (9.19,1.15) (9.20,1.15) (9.20,1.16) (9.21,1.17) (9.21,1.17) (9.22,1.18) (9.22,1.18) (9.23,1.19) (9.23,1.19) (9.24,1.20) (9.24,1.21) (9.24,1.21) (9.25,1.22) (9.25,1.22) (9.26,1.23) (9.26,1.23) (9.27,1.24) (9.27,1.24) (9.28,1.25) (9.28,1.25) (9.29,1.26) (9.29,1.26) (9.30,1.27) (9.30,1.27) (9.31,1.28) (9.31,1.28) (9.31,1.29) (9.32,1.29) (9.32,1.30) (9.33,1.30) (9.33,1.31) (9.34,1.31) (9.34,1.32) (9.35,1.32) (9.35,1.32) (9.36,1.33) (9.36,1.33) (9.37,1.34) (9.37,1.34) (9.38,1.35) (9.38,1.35) (9.38,1.35) (9.39,1.36) (9.39,1.36) (9.40,1.36) (9.40,1.37) (9.41,1.37) (9.41,1.38) (9.42,1.38) (9.42,1.38) (9.43,1.39) (9.43,1.39) (9.44,1.39) (9.44,1.40) (9.45,1.40) (9.45,1.40) (9.45,1.41) (9.46,1.41) (9.46,1.41) (9.47,1.42) (9.47,1.42) (9.48,1.42) (9.48,1.43) (9.49,1.43) (9.49,1.43) (9.50,1.44) (9.50,1.44) (9.51,1.44) (9.51,1.45) (9.52,1.45) (9.52,1.45) (9.52,1.45) (9.53,1.46) (9.53,1.46) (9.54,1.46) (9.54,1.46) (9.55,1.47) (9.55,1.47) (9.56,1.47) (9.56,1.47) (9.57,1.48) (9.57,1.48) (9.58,1.48) (9.58,1.48) (9.59,1.49) (9.59,1.49) (9.59,1.49) (9.60,1.49) (9.60,1.50) (9.61,1.50) (9.61,1.50) (9.62,1.50) (9.62,1.50) (9.63,1.51) (9.63,1.51) (9.64,1.51) (9.64,1.51) (9.65,1.51) (9.65,1.52) (9.66,1.52) (9.66,1.52) (9.66,1.52) (9.67,1.52) (9.67,1.53) (9.68,1.53) (9.68,1.53) (9.69,1.53) (9.69,1.53) (9.70,1.53) (9.70,1.53) (9.71,1.54) (9.71,1.54) (9.72,1.54) (9.72,1.54) (9.73,1.54) (9.73,1.54) (9.73,1.54) (9.74,1.55) (9.74,1.55) (9.75,1.55) (9.75,1.55) (9.76,1.55) (9.76,1.55) (9.77,1.55) (9.77,1.55) (9.78,1.56) (9.78,1.56) (9.79,1.56) (9.79,1.56) (9.80,1.56) (9.80,1.56) (9.80,1.56) (9.81,1.56) (9.81,1.56) (9.82,1.56) (9.82,1.56) (9.83,1.57) (9.83,1.57) (9.84,1.57) (9.84,1.57) (9.85,1.57) (9.85,1.57) (9.86,1.57) (9.86,1.57) (9.87,1.57) (9.87,1.57) (9.87,1.57) (9.88,1.57) (9.88,1.57) (9.89,1.57) (9.89,1.57) (9.90,1.57) (9.90,1.57) (9.91,1.57) (9.91,1.57) (9.92,1.57) (9.92,1.57) (9.93,1.57) (9.93,1.57) (9.94,1.57) (9.94,1.57) (9.94,1.57) (9.95,1.57) (9.95,1.57) (9.96,1.57) (9.96,1.57) (9.97,1.57) (9.97,1.57) (9.98,1.57) (9.98,1.57) (9.99,1.57) (9.99,1.57) (10.00,1.57) (10.00,1.57) (10.01,1.57) (10.01,1.57) (10.01,1.57) (10.02,1.57) (10.02,1.57) (10.03,1.57) (10.03,1.57) (10.04,1.57) (10.04,1.57) (10.05,1.57) (10.05,1.57) (10.06,1.57) (10.06,1.57) (10.07,1.57) (10.07,1.57) (10.08,1.56) (10.08,1.56) (10.08,1.56) (10.09,1.56) (10.09,1.56) (10.10,1.56) (10.10,1.56) (10.11,1.56) (10.11,1.56) (10.12,1.56) (10.12,1.56) (10.13,1.55) (10.13,1.55) (10.14,1.55) (10.14,1.55) (10.15,1.55) (10.15,1.55) (10.15,1.55) (10.16,1.55) (10.16,1.54) (10.17,1.54) (10.17,1.54) (10.18,1.54) (10.18,1.54) (10.19,1.54) (10.19,1.54) (10.20,1.53) (10.20,1.53) (10.21,1.53) (10.21,1.53) (10.22,1.53) (10.22,1.53) (10.22,1.53) (10.23,1.52) (10.23,1.52) (10.24,1.52) (10.24,1.52) (10.25,1.52) (10.25,1.51) (10.26,1.51) (10.26,1.51) (10.27,1.51) (10.27,1.51) (10.28,1.50) (10.28,1.50) (10.29,1.50) (10.29,1.50) (10.29,1.50) (10.30,1.49) (10.30,1.49) (10.31,1.49) (10.31,1.49) (10.32,1.48) (10.32,1.48) (10.33,1.48) (10.33,1.48) (10.34,1.47) (10.34,1.47) (10.35,1.47) (10.35,1.47) (10.36,1.46) (10.36,1.46) (10.36,1.46) (10.37,1.46) (10.37,1.45) (10.38,1.45) (10.38,1.45) (10.39,1.45) (10.39,1.44) (10.40,1.44) (10.40,1.44) (10.41,1.43) (10.41,1.43) (10.42,1.43) (10.42,1.42) (10.43,1.42) (10.43,1.42) (10.43,1.41) (10.44,1.41) (10.44,1.41) (10.45,1.40) (10.45,1.40) (10.46,1.40) (10.46,1.39) (10.47,1.39) (10.47,1.39) (10.48,1.38) (10.48,1.38) (10.49,1.38) (10.49,1.37) (10.50,1.37) (10.50,1.36) (10.50,1.36) (10.51,1.36) (10.51,1.35) (10.52,1.35) (10.52,1.35) (10.53,1.34) (10.53,1.34) (10.54,1.33) (10.54,1.33) (10.55,1.32) (10.55,1.32) (10.56,1.32) (10.56,1.31) (10.57,1.31) (10.57,1.30) (10.57,1.30) (10.58,1.29) (10.58,1.29) (10.59,1.28) (10.59,1.28) (10.60,1.27) (10.60,1.27) (10.61,1.26) (10.61,1.26) (10.62,1.25) (10.62,1.25) (10.63,1.24) (10.63,1.24) (10.64,1.23) (10.64,1.23) (10.64,1.22) (10.65,1.22) (10.65,1.21) (10.66,1.21) (10.66,1.20) (10.67,1.19) (10.67,1.19) (10.68,1.18) (10.68,1.18) (10.69,1.17) (10.69,1.17) (10.70,1.16) (10.70,1.15) (10.71,1.15) (10.71,1.14) (10.71,1.13) (10.72,1.13) (10.72,1.12) (10.73,1.11) (10.73,1.11) (10.74,1.10) (10.74,1.09) (10.75,1.09) (10.75,1.08) (10.76,1.07) (10.76,1.07) (10.77,1.06) (10.77,1.05) (10.78,1.04) (10.78,1.04) (10.78,1.03) (10.79,1.02) (10.79,1.01) (10.80,1.00) (10.80,1.00) (10.81,0.99) (10.81,0.98) (10.82,0.97) (10.82,0.96) (10.83,0.95) (10.83,0.94) (10.84,0.94) (10.84,0.93) (10.85,0.92) (10.85,0.91) (10.85,0.90) (10.86,0.89) (10.86,0.88) (10.87,0.87) (10.87,0.86) (10.88,0.85) (10.88,0.84) (10.89,0.83) (10.89,0.81) (10.90,0.80) (10.90,0.79) (10.91,0.78) (10.91,0.77) (10.92,0.76) (10.92,0.74) (10.92,0.73) (10.93,0.72) (10.93,0.70) (10.94,0.69) (10.94,0.68) (10.95,0.66) (10.95,0.65) (10.96,0.63) (10.96,0.62) (10.97,0.60) (10.97,0.58) (10.98,0.57) (10.98,0.55) (10.99,0.53) (10.99,0.51) (10.99,0.49) (11.00,0.47) (11.00,0.45) (11.01,0.42) (11.01,0.40) (11.02,0.37) (11.02,0.34) (11.03,0.31) (11.03,0.28) (11.04,0.25) (11.04,0.21) (11.05,0.16) (11.05,0.11) (11.06,0.10) (11.06,0.10) (11.06,0.10) (11.07,0.10) (11.07,0.10) (11.08,0.10) (11.08,0.10) (11.09,0.10) (11.09,0.10) (11.10,0.10) (11.10,0.10) (11.11,0.10) (11.11,0.12) (11.12,0.14) (11.12,0.16) (11.13,0.18) (11.13,0.19) (11.13,0.20) (11.14,0.21) (11.14,0.22) (11.15,0.23) (11.15,0.24) (11.16,0.24) (11.16,0.25) (11.17,0.25) (11.17,0.26) (11.18,0.26) (11.18,0.26) (11.19,0.26) (11.19,0.26) (11.20,0.26) (11.20,0.26) (11.20,0.26) (11.21,0.26) (11.21,0.26) (11.22,0.26) (11.22,0.25) (11.23,0.25) (11.23,0.25) (11.24,0.24) (11.24,0.24) (11.25,0.23) (11.25,0.23) (11.26,0.22) (11.26,0.21) (11.27,0.21) (11.27,0.20) (11.27,0.19) (11.28,0.18) (11.28,0.17) (11.29,0.16) (11.29,0.15) (11.30,0.14) (11.30,0.13) (11.31,0.12) (11.31,0.11) (11.32,0.10) (11.32,0.10) (11.33,0.10) (11.33,0.10) (11.34,0.10) (11.34,0.10) (11.34,0.10) (11.35,0.10) (11.35,0.10) (11.36,0.10) (11.36,0.10) (11.37,0.10) (11.37,0.10) (11.38,0.10) (11.38,0.10) (11.39,0.10) (11.39,0.10) (11.40,0.10) (11.40,0.10) (11.41,0.10) (11.41,0.10) (11.41,0.10) (11.42,0.10) (11.42,0.10) (11.43,0.10) (11.43,0.10) (11.44,0.10) (11.44,0.10) (11.45,0.10) (11.45,0.10) (11.46,0.10) (11.46,0.10) (11.47,0.10) (11.47,0.10) (11.48,0.10) (11.48,0.10) (11.48,0.10) (11.49,0.10) (11.49,0.10) (11.53,0.10) (11.53,0.10) (11.54,0.10) (11.57,0.10) (11.57,0.10) (11.58,0.10) (11.61,0.10) (11.62,0.10) (11.62,0.10) (11.65,0.10) (11.66,0.10) (11.66,0.10) (11.69,0.10) (11.70,0.10) (11.70,0.10) (11.74,0.11) (11.74,0.12) (11.75,0.13) (11.78,0.19) (11.78,0.20) (11.79,0.20) (11.82,0.24) (11.83,0.24) (11.83,0.25) (11.86,0.27) (11.87,0.27) (11.87,0.28) (11.90,0.29) (11.91,0.29) (11.91,0.29) (11.95,0.29) (11.95,0.28) (11.96,0.28) (11.99,0.27) (11.99,0.27) (12.00,0.26) (12.03,0.23) (12.04,0.23) (12.04,0.22) (12.07,0.17) (12.08,0.16) (12.08,0.15) (12.11,0.10) (12.12,0.10) (12.12,0.10) (12.16,0.10) (12.16,0.10) (12.17,0.10) (12.20,0.10) (12.20,0.10) (12.21,0.10) (12.24,0.10) (12.25,0.10) (12.25,0.10) (12.28,0.15) (12.29,0.16) (12.29,0.17) (12.32,0.23) (12.33,0.23) (12.33,0.24) (12.37,0.27) (12.37,0.28) (12.38,0.28) (12.41,0.30) (12.41,0.31) (12.42,0.31) (12.45,0.32) (12.46,0.32) (12.46,0.32) (12.49,0.31) (12.50,0.31) (12.50,0.31) (12.53,0.30) (12.54,0.29) (12.54,0.29) (12.58,0.26) (12.58,0.26) (12.59,0.25) (12.62,0.21) (12.62,0.20) (12.63,0.19) (12.66,0.12) (12.67,0.10) (12.67,0.10) (12.70,0.10) (12.71,0.10) (12.71,0.10) (12.74,0.10) (12.75,0.10) (12.75,0.10) (12.79,0.10) (12.79,0.10) (12.80,0.10) (12.83,0.10) (12.83,0.11) (12.84,0.12) (12.87,0.19) (12.88,0.20) (12.88,0.21) (12.91,0.25) (12.92,0.25) (12.92,0.26) (12.95,0.28) (12.96,0.28) (12.96,0.29) (13.00,0.30) (13.00,0.30) (13.01,0.30) (13.04,0.30) (13.04,0.30) (13.05,0.30) (13.08,0.29) (13.09,0.28) (13.09,0.28) (13.12,0.26) (13.13,0.25) (13.13,0.25) (13.16,0.21) (13.17,0.20) (13.17,0.20) (13.21,0.13) (13.21,0.12) (13.22,0.11) (13.25,0.10) (13.25,0.10) (13.26,0.10) (13.29,0.10) (13.30,0.10) (13.30,0.10) (13.33,0.10) (13.34,0.10) (13.34,0.10) (13.37,0.10) (13.38,0.10) (13.38,0.10) (13.42,0.14) (13.42,0.15) (13.43,0.16)};
\draw[dim] (8.83,1.71) -- (11.07,1.71);
\draw[tick] (8.83,1.66) -- (8.83,1.76);
\draw[tick] (11.07,1.66) -- (11.07,1.76);
\node[lab, anchor=south] at (9.95,1.73) {$160$ Hz wide};
\draw[ridge] (6.45,0.26) -- (13.45,0.26);
\fill[black!72] (11.20,0.26) circle (0.04);
\draw[tick] (6.40,0.26) -- (6.50,0.26);
\node[tk, anchor=east] at (6.36,0.26) {$-44$};
\node[ttl, anchor=west] at (0.02,4.92) {what the frame is};
\node[ttl, anchor=west] at (5.99,4.92) {what one tone becomes};
\end{tikzpicture}
```
Two rows, each one a choice and its price. The left column is a frame of a $250$ Hz tone, and
the faint line running past both edges is the tone the frame was cut out of, so that the cliff is
visible rather than asserted: row 1 is the bare cut, holding a value of $1$ at its last sample and
nothing one sample later, and row 2 is the same frame multiplied by the Hamming window, whose dashed
envelope brings both ends to $0.08$. The right column is what that buys. A single tone is never
reported as one bin; it is reported as the window's own transform, parked at the tone, so each bump
here is the width that every tone in the recording gets smeared to. The widths are measured between
the two nulls either side of the bump, and they are exact divisions rather than measurements:
$2 f_s / L = 80$ Hz for the cut against $4 f_s / L = 160$ Hz for the fade, on the $31.25$ Hz grid the
STFT card derives. The dash-dot rule marks the first ridge of each skirt, about $13$ dB below the
peak for the cut and about $44$ dB below for the fade. So the fade costs one doubling of width and
buys back roughly $30$ dB of the energy that the cut would have scattered, which is the trade the
sidebar names, priced on the two axes it is actually paid on.
:::

**Traceability.** The records behind this section. The frame, hop, transform length and band count
are parameters declared in the experiment file rather than measurements, so they are not in this
table, and every quantity this section prints that is not one of those parameters is arithmetic on
them, shown in full where it is used. What the records below supply are the two rates that turn a
sample count into milliseconds, and the two hardware quantities that the cost paragraphs divide by.

| Record | What it establishes here |
| --- | --- |
| `V-05-10` | LibriSpeech is 16 kHz read English speech, so the frontend's rate is a constraint from the data |
| `V-05-11` | Speech Commands is stored as 16-bit single-channel PCM at 16 kHz |
| `V-01-09` | the fabric holds 1,248 multiply-accumulate slices, which every per-slice figure in this book divides by |
| `V-02-09` | the Jetson baseline's rated sparse INT8 throughput, whose dense half is the other side of the comparison in section 1.4 |

## 1.4 Hardware Implications & Processing Latency Bounds

Sections 1.1 and 1.3 gave a deadline and a set of operations. This section puts them next to
the memory and arithmetic that a real device has, and states which of the resulting numbers
are printed in a datasheet, which are arithmetic on those prints, and which nobody has
measured.

### Latency has a floor, and it is not the processor

Three quantities are fixed by the config before any hardware exists. They are derived from the
design values, so they are arithmetic, not measurement.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Fill time of the first frame | 25 ms | $L/f_s = 400/16{,}000$ |
| Interval between frames | 10 ms | $H/f_s = 160/16{,}000$ |
| Overlap of neighbouring frames | 60% | $(L-H)/L = 240/400$ |

The consequence is a shape of delay that no amount of computing power removes. The very first
frame cannot exist before 25 ms of sound has arrived. After that, a new frame appears every
10 ms. A faster device does not lower the 25 ms; it only fails to add anything to it.

The same arithmetic explains $batch=1$ again, from the other side. Waiting to collect $B$
frames adds $(B-1)\times10$ ms before any of them is processed, so a batch of 8 costs 70 ms.
A design whose queue holds two frames has already spent 10 ms of margin it was never given.

There is a second, smaller bound that shows up in every streaming implementation. A recording
of one second yields 98 frames, and the count is worth doing once because what is left over is the
point. A frame needs all $400$ of its samples, so its start cannot pass $16{,}000 - 400 = 15{,}600$.
Starts land on hops, so the last legal start is the largest multiple of $160$ at or below $15{,}600$,
which is $97 \times 160 = 15{,}520$ -- frames numbered $0$ through $97$, so $98$ of them -- and that
last window ends at $15{,}520 + 400 = 15{,}920$. The trailing $16{,}000 - 15{,}920 = 80$ samples never
form a frame, because a frame is a fixed-size group and $80$ of them is not one.
Any design that must report the end of an utterance has to decide what to do with a tail
shorter than $L$, and the two answers, dropping it or padding it, are not equivalent.

### Memory, against containers that are documented

The FPGA figures below are device capacities, each from a record in the evidence set, taken
from Advanced Micro Devices document DS890 (v4.10), page 22, Table 23, for the device
registered as `xczu5ev` / `XCK26`:

| Record | Capacity |
| --- | --- |
| `V-01-03` | 117,120 configurable logic block look-up tables (CLB LUT -- the basic logic element) |
| `V-01-05`, `V-01-06` | 144 Block RAM (BRAM -- on-chip storage) blocks of 36 kilobit, 5.1 Mb total |
| `V-01-07`, `V-01-08` | 64 UltraRAM (URAM) blocks, 18.0 Mb total |
| `V-01-09` | 1,248 DSP48E2 slices (the multiply-accumulate block of this chip family) |
| `V-01-11`, `V-01-22` | 23,616 Kb of combined BRAM and URAM |

Two of those rows are worth a note on how to read a datasheet. The BRAM total is printed as
"5.1 Mb", which is the datasheet's rounding of $144 \times 36 = 5{,}184$ kilobit. The combined
capacity carries a `conflict` flag: 23,616 Kb is what multiplying the two block counts by their sizes
gives, while the project's own plan document says "4 MB" and a research note says about 4.5 MB. The
record that unrolls the whole chain -- 23,616 Kb = 2,952 KiB = 3,022,848 bytes = 2.8828 MiB = 3.02 MB in
decimal units -- so the disagreement is partly a units disagreement, which is exactly the kind
of thing a table of capacities hides. All readings stay in the record; none was averaged.

Now the two things the frontend actually needs to store, both in 32-bit floating point (FP32):

| Item | Size | Fraction of the container |
| --- | --- | --- |
| Ring buffer, 400 samples | 1,600 B | 34.7% of one 36-kilobit BRAM block (4,608 B) |
| Mel matrix, $80 \times 257$ weights | 82,240 B = 80.3 KiB | 12.4% of BRAM; 2.7% of BRAM plus URAM |

Both right-hand columns are derived arithmetic: each percentage is the item's byte size divided by
the container's byte size, so the first row is $1{,}600 / 4{,}608 = 34.7\%$ and the second is
$82{,}240 / 663{,}552 = 12.4\%$. One derived number over one recorded number, in that order. Read them for what they are. They say that the frontend's data is small against the
storage a device of this class contains. They do **not** say the design would occupy that much
of a device, because nothing here has been described in a hardware language, let alone
synthesised. A percentage of a container is not a percentage of a design, and the difference
is the first thing a synthesis report will correct.

### The arithmetic is not where the argument is

The Mel stage costs 20,560 MAC per frame, hence 2.056 million per second (the fabric's 1,248
multiply-accumulate slices, so spread across all of them the stage would ask each slice for 1,647 MAC
per second). On the Jetson side, the registered rating is 67 sparse INT8 (8-bit integer) TOPS for an
Orin Nano Super at up to the 25 W ceiling its power-mode record lists, and the sparsity record states
that structured sparsity doubles throughput. Dividing the first by the second gives roughly 33
dense INT8 TOPS, which is arithmetic in this book and is carried by no record. Against that, the
frontend asks for $2.056$ million operations a second, so the ratio is
$3.3 \times 10^{13} / 2.056 \times 10^{6} \approx 1.6 \times 10^{7}$: about sixteen million, with one
multiply-accumulate counted as one operation. Count it as the two operations it literally is -- a
multiply and an add -- and the stage asks for $4.112$ million a second and the factor halves to about
eight million. The two readings disagree by a factor of two and the gap they are measuring is in the
millions, so nothing in the argument below turns on which one is taken.

So the case for moving a voice frontend into programmable logic is not a peak-throughput case,
and a chapter that pretended otherwise would be selling the wrong argument. It is a deadline
and interference case. A CPU runs the frontend inside the same 10 ms budget that it also
spends on the microphone driver, the network stack and the model, and a deadline shared four
ways is a deadline that gets missed. Dedicated logic removes the sharing: the frontend arrives
on time because it has its own wiring. Whether that argument survives contact with a real
design is exactly the kind of question this book cannot answer without a board, so it is left
open rather than closed with an estimate.


**Traceability.** The Jetson records the division above spends. The 33 dense TOPS is arithmetic in
this book, not a rating any record carries; the rows below are only its operands.

| Record | What it establishes here |
| --- | --- |
| `V-02-09` | an Orin Nano Super rated 67 sparse INT8 (8-bit integer) TOPS |
| `V-02-11` | its power modes, up to the 25 W ceiling the rating assumes |
| `V-02-31` | structured sparsity doubles throughput -- the factor the division uses |


### What the experiment measured, and what its number really says

The reference run is recorded at `results/exp01/20260913T020406Z/`, with its digests in
`results/SHA256SUMS`. It compared the streaming implementation against an offline one over one
second of a three-tone test signal, on a host running Python 3.12.10 with NumPy 2.5.2. It
produced 98 frames of 80 values and reported:

| Reported | Value | Reading |
| --- | --- | --- |
| Mean absolute error (MAE) | $0.0$ | Satisfies the section 7 bound of README `chapter01/`, which is written as an expectation, not a result |
| Frames | 98 | As derived above from $L$, $H$ and one second |
| Element comparison | 0 of 7,840 differ | The two arrays are bitwise identical, not merely close |
| SQNR | 134.48 dB | **Not a measurement of noise.** See below. |

The signal-to-quantization-noise ratio (SQNR -- decibels of signal power over error power) is
computed in the script as $10\log_{10}\bigl(P_\text{signal}/(P_\text{error}+10^{-12})\bigr)$.
Here $P_\text{error}$ is exactly zero, because the arrays are identical, so the guard term
$10^{-12}$ is the entire denominator. The reported figure is therefore
$10\log_{10}(28.04136848449707/10^{-12})$, and it reproduces to the last printed digit. That
number is a property of the epsilon in the formula and of the signal's amplitude. It says
nothing about numerical noise, and it must not be quoted as a margin. This is the floor
effect that section 1.3 warned about, arriving in a table rather than in prose.

What the run does establish is narrower and more useful. Feeding a ring buffer 160 samples at
a time reaches the same numbers as reading the whole recording at once, on this input, in this
precision, to the last bit. That is a correctness result about the streaming rewrite. It is
not evidence about fixed-point arithmetic, about hardware, or about accuracy of any model, and
the last two of those are where this chapter's real difficulty is.

Two things follow. The comparison proves the buffer logic, not the number format, because both
sides use FP32; fixed point is chapter 6's subject and this run has no bearing on it. And a
frontend that reproduces its offline reference bit-for-bit still tells you nothing about the
only metric the task uses. Recognition accuracy and EER live downstream of these 80 numbers.
The procedure that would close that gap is written out in `chapter01/README.md`, and its result
cells are empty.

---

## Associated Experiment
- Refer to [`chapter01/`](../chapter01/).
- Executed on a host on 2026-09-13; raw output at
  [`results/exp01/20260913T020406Z/`](../results/exp01/20260913T020406Z/). Section 1.4 reads it.
