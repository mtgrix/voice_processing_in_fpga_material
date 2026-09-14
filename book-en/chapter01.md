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
already in view, so the view comes first. [Figure 2](#fig-ch1-pipeline-contract) is the version this
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
`chapter01/exp_01_streaming_audio_pipeline.py`, stage by stage. The stages are waveform,
sliding ring buffer, windowing, STFT, Mel filterbank, log compression.

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

**Windowing.** A frame is a slice cut from a continuing sound, and the cut is abrupt: the
signal simply stops at one end and begins at the other. A sudden edge looks, to any frequency
analysis, like very high frequency content that was never in the room. The remedy is to
multiply the frame by a **window function** that fades both ends toward zero before the
analysis is taken. The reference implementation uses the Hamming window across the 400
samples of the buffer. The cost is that the ends of the frame contribute little, which makes
the frequency response slightly wider and softer. Section 1.3 is where that trade-off is
priced.

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

Four expressions produce the 80 numbers of one frame. Each is read in five steps: the
intuition, the expression, what each symbol is, what it costs in hardware, and what it does
*not* tell you. The last step matters most in this book. An equation is easy to mistake for a
permission slip, and each of these four has a conclusion people draw from it that the equation
does not support.

The design parameters come from `AudioConfig` in the experiment file, and they are
repeated here as one block so the arithmetic below can be checked: sampling rate
$f_s = 16{,}000$ Hz, frame length $L = 400$ samples, hop $H = 160$ samples, transform
length $N = 512$, band count $M = 80$, band range 0 to 8,000 Hz. They are design
parameters, so their provenance is the code and not a measurement.

### The windowed frame

*Mechanism.* A frame is a slice of the recording, and a slice needs to be faded at its ends
before it is analysed, for the reason given in section 1.2. Fading is multiplication.

$$x_\ell[n] = x[n_0 + \ell H + n]\; w[n], \qquad n = 0, 1, \dots, L-1$$

$x$ is the sample stream, $\ell$ counts frames, $n$ counts samples inside one frame, $w$ is
the window of $L$ fixed numbers, and $n_0$ is where the first frame starts. The index
$n_0 + \ell H$ moves forward by $H$ samples per frame, which is the whole of what "streaming"
means in symbols.

*Engineering consequence.* $w$ never changes, so a hardware window is a table of 400
constants and 400 multipliers, or fewer multipliers reused 400 times. It has no state and
makes no decisions. This is the least controversial stage in the pipeline.

*What cannot be inferred.* That the window is harmless. Multiplying by $w$ lowers the
amplitude near the edges of the frame, which changes the answer every later stage gives. The
expression says nothing about whether that change is acceptable for a recognition model, and
a formula cannot settle it. Only a measurement against a model can, and none has been made
here.

### The Short-Time Fourier Transform

*Mechanism.* The transform asks one question of a frame, $N$ times: how much of this frame
rotates at this rate?

$$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n]\; e^{-j 2\pi k n / N}, \qquad k = 0, 1, \dots, N-1$$

The factor $e^{-j2\pi kn/N}$ is a complex number of length one that turns at $k/N$ of a
revolution per sample, and $j$ is the unit imaginary number, the $90^\circ$ turn. Multiplying
the frame by it and adding up measures how strongly the frame agrees with that rotation, in
both amplitude and timing. Each $k$ is one **frequency bin**, and a bin's answer is complex,
carrying magnitude and phase.

The reference implementation writes the 400 windowed samples into a 512-slot array, padding
the last 112 slots with zeros, and evaluates the sum by a Fast Fourier Transform rather than
term by term. Because the input samples are real, bin $k$ and bin $N-k$ carry the same
information, so only bins $0$ to $N/2$ are kept: 257 bins.

*Engineering consequence.* Bin $k$ sits at $k f_s / N$ hertz, so adjacent bins are
$16{,}000/512 = 31.25$ Hz apart and the last bin is at 8,000 Hz. That spacing is fixed by
$N$ and $f_s$ alone. It is not adjustable per frame, and no cleverness in the hardware changes
it.

*What cannot be inferred.* The cost. Written as a sum, one bin needs $N$ complex
multiplications and there are $N$ bins, which would be $512^2$ products per frame. Nobody
computes it that way, including this implementation, because the FFT reaches the same answer
with far fewer steps. The number $512^2$ is what the *expression* costs, not what the *code*
costs, and confusing the two is how a resource estimate goes wrong by an order of magnitude.

### The power spectrum and the Mel filterbank

*Mechanism.* Recognition models use energy, not phase, so each bin is reduced to a real
number:

$$P_\ell[k] = |X_\ell[k]|^2$$

Then 257 bins are folded into 80 bands. Human hearing separates two low frequencies more
easily than two high ones, so the bands are narrow at the bottom and wide at the top. The
implementation converts hertz to the perceptual **Mel scale** by

$$\mathrm{mel}(f) = 2595 \log_{10}\!\left(1 + \frac{f}{700}\right)$$

places $M+2 = 82$ points at equal spacing in Mel between 0 and 8,000 Hz, and turns them back
into hertz. Each band $m$ is a triangle over the bins between its left point, its centre and
its right point, and its output is the weighted sum under that triangle:

$$E_\ell[m] = \sum_{k=0}^{256} g_m[k]\, P_\ell[k], \qquad g_m[k] =
\begin{cases}
\dfrac{k - k_{m-1}}{k_m - k_{m-1}} & k_{m-1} \le k \le k_m \\[6pt]
\dfrac{k_{m+1} - k}{k_{m+1} - k_m} & k_m < k \le k_{m+1} \\[4pt]
0 & \text{otherwise}
\end{cases}$$

$g_m[k]$ is the height of band $m$'s triangle at bin $k$, and $k_j$ is the bin index of the
$j$-th Mel point. The two middle lines are the ramp up and the ramp down.

*Engineering consequence.* The 82 constants, the 80 triangles and the whole of $g$ are
computed once from $f_s$, $N$ and the band limits. After that the stage is a fixed matrix
times a vector: $M \times 257 = 20{,}560$ multiply-accumulate operations (MAC -- one
multiplication and one addition fused into a single hardware step) per frame, and nothing
else. At 100 frames per second that is 2.056 million MAC per second for the whole stage.
A fixed matrix is a read-only memory, which is why section 1.4 discusses its size and not its
arithmetic.

*What cannot be inferred.* Nothing in these formulas says that 80 bands is the right number.
Eighty is what `AudioConfig` declares. Fewer bands would lose spectral detail and cost less
memory; more would be the reverse. Where the balance lies depends on the model that consumes
the features, which is chapter 5's subject, and no run in this repository has varied $M$.

### Log compression

*Mechanism.*

$$c_\ell[m] = \ln\bigl(\max(E_\ell[m],\, 10^{-6})\bigr)$$

$10^{-6}$ is a floor. Without it a band with no energy would return $\ln(0)$, which is minus
infinity, and infinity cannot be stored in a fixed-width number.

*Engineering consequence.* The floor is also a constraint on the hardware. A design must
either compute a logarithm, which is a non-linear function needing a lookup table or a
polynomial, or store the values some other way. Chapter 6 deals with that choice, because the
choice depends on the number format.

*What cannot be inferred.* The floor's value, and this book needs that caution twice. First,
$10^{-6}$ sets the smallest number the output can report, so a claimed error below it is
meaningless. Second, and less obviously, a ratio built on this output can be dominated by the
floor rather than by the signal. Section 1.4 reads a measured number of exactly that kind.

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
$L$. Nobody has run that sweep here.

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
of one second yields 98 frames, because a frame needs all 400 samples and the last complete
window starts at sample 15,520 and ends at 15,920. The trailing 80 samples never form a frame.
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

Both right-hand columns are derived arithmetic, dividing one derived number by one recorded
number. Read them for what they are. They say that the frontend's data is small against the
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
dense INT8 TOPS, which is arithmetic in this book and is carried by no record. Against that,
the frontend's rate is about sixteen million times smaller.

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
