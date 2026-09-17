# The Streaming Bottleneck: Why Batch=1 Stalls a GPU

> *Objective: Analyze the root architectural causes behind the two ways a graphics processor misbehaves on continuous streaming audio -- memory bandwidth saturation when the work is too thin to fill it, and latency jitter when the waits are exposed. Power is not analyzed here; chapter 7 measures it.*

---

## 3.1 The Mismatch Between Streaming Audio and SIMT Architecture

*Where this sits in the chain: the* **Output and latency** *stage -- this chapter asks why the answer arrives*
*late, or in bursts, when the arithmetic itself is small enough to fit anywhere.*

**Intuition.** A GPU does not run many programs at once. It runs one instruction at a time across a
wide group of lanes, and it keeps many such groups waiting in the wings, so that when one group stalls
on memory another can be handed the next instruction. The group has a fixed width, and the machine
consumes work a whole group at a time. Single instruction, multiple threads (SIMT) is the name of that
shape: a *thread* is what the program sees as one lane, and the group of threads moving together is
what the hardware schedules.

A training batch fits that shape by construction. The same arithmetic applies to many independent
inputs at once, every lane takes the same path, and the group is full. A streaming microphone fits it
in one way only: it never stops. Each frame arrives on its own, and the batch dimension, the
multiplier that made the machine's width easy to fill, is gone. The work has not gone with it. One
frame of the Voice Edge Benchmark is a vector of channels wide, and a wide vector fills lanes. What
the frame loses is the cheapest source of extra groups, which is the same thing the machine uses to
cover a memory wait. So the mismatch is not that a frame is small arithmetic. It is that a frame
leaves the machine with too little in flight to hide how long its memory takes.

**Mechanism.** The group is a warp, and `V-02-42` fixes its width: a warp is 32 threads, each
streaming multiprocessor (SM, the part of the GPU that owns both the arithmetic and the scheduling)
creates, manages, schedules and executes threads in groups of that size, and a thread block is
partitioned into warps of 32. A warp issues one common instruction at a time, so full efficiency needs
all lanes of it on the same path. When a data-dependent branch splits a warp, the warp executes each
taken path in turn with the lanes off that path disabled; one warp's disagreement does not spread,
because different warps execute independently (`V-02-43`). Two costs follow. Work that does not
divide into whole warps leaves the last group partly unused. Work whose lanes disagree pays for both
paths.

What the target offers against those two rules is a real size, and it is worth writing down rather
than gesturing at. One frame's activation vector is 256 channels wide (`V-05-04`). Divide that width
by the 32 lanes a warp issues together (`V-02-42`) leaves 8 whole warps, derived from those two
records. Split the same vector over the encoder's 4 heads (`V-05-04`) and the same division leaves a
head 64 channels wide and 2 warps, derived the same way.
A frame is therefore not a trickle: it is eight full groups for a general stage and two for one head of
attention. Eight and two are both whole numbers, so nothing here is wasted on a partial last warp --
what is thin is not the fill of one instruction but the number of independent groups the machine can
hold ready to cover a memory wait.

Whether a handful is enough is the machine's question, not the model's, and the guide answers it with
a list rather than a number: how many blocks and warps an SM holds at once depends on the registers
and shared memory the kernel uses and the SM has, on a maximum number of resident blocks and warps per
SM, and on the compute capability of the device (`V-02-45`). This book has registered no value for
that maximum on the Orin, so the argument here stops at "bounded" and prints no bound.

It matters because of what the machine does with the groups it holds. Memory latency is hidden by
parallelism: the SM switches to execute another warp while memory operations complete (`V-02-46`).
That switch is not itself a cost. The execution context of every warp stays on-chip for the warp's
whole lifetime, so switching between warps incurs no cost, and at each instruction issue cycle a
scheduler selects a warp with threads ready and issues to it (`V-02-44`). Read the two records
together and they say what an empty cycle is. No switching penalty is being paid, so an idle issue
cycle is a missing ready warp. "The GPU was busy" and "the GPU had nothing eligible to issue" are
different observations, and a stream of single frames is the case that tells them apart.

One qualification keeps this section honest about the model this book actually ports. A cache-aware
streaming encoder is not fed one frame at a time. It consumes a chunk of 16 frames, which is 640 ms of
audio at 40 ms per feature frame (`V-05-05`). Inside a chunk the machine has
4,096 values per channel to work through, derived as the 256 channels of one frame (`V-05-04`) times
the 16 frames of one chunk (`V-05-05`) -- a batch in all but name. So a chunked design buys back the
parallelism that streaming removed, and the price is not arithmetic but delay: 640 ms of audio must
arrive before the encoder can answer any of it. That trade, and not a missing kernel flag, is what
"batch one" means on this workload. Chapter 8 and chapter 9 take the chunk size as a design input for exactly
that reason.

**Hardware application.** The counts above are the whole of what a GPU is handed per step, and they
are worth one table because everything in section 3.2 and chapter 9 is built from them.

| What the machine is handed | Value | Where it comes from |
| --- | --- | --- |
| Channels in one frame's activation vector | 256 | `V-05-04` |
| Whole warps that vector fills | 8 | calculated from `V-05-04` with `V-02-42` |
| Frames in one chunk of the streaming encoder | 16 | `V-05-05` |
| Channel values in one chunk, before the block loop | 4,096 | calculated from `V-05-04` with `V-05-05` |
| Encoder blocks that repeat the same stages | 12 | `V-05-04` |
| Memory bandwidth those reads compete for | 102 GB/s | `V-02-18` |

Read the last row against the first five. The bandwidth is the shared resource, and the model's shape
decides how many readers it has at once: a chunk of frames, twelve blocks deep, all reading weights
that a previous chunk already touched. `V-05-57` is the record that says this book cannot yet turn
that shape into bytes per frame, because no publisher prints a counted parameter breakdown for this
encoder. So the table stops at counts of values, and the traffic is left to the board run.

The fabric comparison is the reason this section is in a book about FPGAs, and it is narrower than it
usually looks. A register-transfer level (RTL) datapath has no warps, so it has none of the two costs
above: a stage is wired to the width its tensors have, no lane is left over because of a rounding
rule, and a branch that only some channels take is a multiplexer rather than a wasted pass. What the
fabric does not gain is the trick with the waiting. There is no pool of resident groups to switch to
while a read is in flight, so a stall is a stall, and the only cures are a deeper buffer, an earlier
prefetch, or a stage that is genuinely independent. Chapter 9 sizes that buffer. What the fabric pays
instead of a scheduler is idleness by construction: a datapath built one frame wide is empty between
chunks, and no arriving batch can fill it, because there is no batch left to arrive.

> **Whose execution model this is, and what it does not size.** The five behaviour statements above
> are the CUDA programming model as the vendor documents it in the guide version pinned in
> `docs/source_index.json`, and that guide says the
> sections they come from describe the features of the SM that are common to all devices, so none of
> them is a claim about the Orin specifically. Three quantities this section would need to go further
> are not in `docs/verification/claims.json`: the maximum number of warps resident on this device's
> SM, the fraction of that capacity a streaming chunk reaches, and the bytes per frame in the last
> paragraph, which `V-05-57` registers as an open gap. Each is a measurement, not a reading of a
> datasheet, so it belongs to the board run in chapter 8 rather than to this argument.

## 3.2 Kernel Launch Overheads, Preemption, and Tail Jitter

**Intuition.** Nothing on a GPU starts itself. Every kernel, which is one pass of one stage of the
network over the data the program pointed it at, begins as a request the host processor makes on the
device's behalf, and making the request is work in itself. A program that runs one long kernel pays
that cost once and forgets it. A streaming program runs the whole stage list again for every chunk of
audio it answers, forever, so a cost that never mattered in training becomes a fixed floor under each
answer. That is launch overhead.

Tail jitter is a different complaint about the same pipeline, and it needs the distinction stated
before the mechanism, because the two words get used as one. Throughput says how many chunks an hour
gets answered. Latency says how long one chunk waits. A system can hold its throughput and still miss
a deadline, because a deadline belongs to one unlucky chunk and an average belongs to none. The
project's own metric is the far end of the latency distribution rather than its middle, which
chapter 8 defines and states a condition for; this section is about where the far end comes from.

**Mechanism.** The vendor states the first half plainly. When a kernel is placed in a stream, the host
driver performs a sequence of operations in preparation for its execution, and those operations are an
overhead cost that must be paid for each kernel issued; for a kernel with a short execution time, that
cost can be a significant fraction of the overall end-to-end time (`V-02-47`). Three things in that
sentence are worth separating, because each one points at a different fix. The work is on the host, so
a faster GPU does not remove it. It is per kernel, so it scales with how many stages the model
compiles into, which is why `V-05-57` matters here: the number of kernels per frame for this encoder is
a quantity this book has not measured. And it is charged to short kernels, which is the streaming case
by construction.

The same page names the answer, and it is worth a paragraph because a streaming encoder is the ideal
customer for it. Overhead costs like these are what CUDA Graphs exists to avoid: a workflow that will
be launched many times is captured once as a graph, and the costs are paid once for the whole graph
during instantiation, after which the graph is launched repeatedly with very little overhead
(`V-02-47`). A graph is a description of a fixed sequence of work, so it fits this design for one
reason and strains on it for one. The reason it fits: the encoder's stage list is the same every
chunk. The reason it strains: a chunked encoder does not always do the same *amount* of work, since a
partial chunk at the end of an utterance and a full chunk in the middle are different shapes, and a
graph is only worth instantiating if the shape recurs. `V-05-05` registers the recurrence, a chunk of
16 frames, and nothing here registers how often the tail of an utterance breaks it.

Now the tail. A chunk's latency is a sum over the stages it passes through, and the three terms are
different physical things. The first is the driver's setup: the host work that happens before the
kernel runs at all. The second is a wait -- the time the stage's inputs are not yet readable, which is
covered only if another resident warp is ready to issue. The third is execution: the cycles the
multiprocessor actually spends on that stage's instructions. A chunk's total is the three added stage by
stage, over twelve blocks of them (`V-05-04` for the depth). Section 3.1 showed that the waits are covered only when some other resident warp is ready,
and that a stream of single frames is the case with the fewest of them, so the cover is thin and what
is left is exposed latency, per stage, twelve blocks deep (`V-05-04` for the depth). Exposed waits are
where a tail is made. Two more sources follow, and both are arithmetic rather than luck; [Figure 10](#fig-chunk-boundary)
draws the first of them as a distance. A frame that
slips past a chunk boundary is not answered a moment later; it is answered when the next chunk
completes, because a chunked encoder cannot emit a decision before it has the chunk, so the penalty
for a late sample is up to a whole chunk, 640 ms of audio at 40 ms per feature frame (`V-05-05`). And
a kernel that arrives while the driver is still finishing the setup of the previous one queues, so a
jitter in the host's own timing arrives at the output summed over the stages rather than
averaged away.

::: {#fig-chunk-boundary .figure}
```tikz
% The shape behind the sentence "the penalty for a late sample is up to a whole chunk". One frame
% period is drawn 0.62cm wide, so the 16-frame chunk is exactly 16 of those widths and the two waits
% are horizontal distances a reader can compare with a ruler. No value is added that section 3.2 does
% not already print from `V-05-05`; every span below is a dimension line with drop guides.
\begin{tikzpicture}[
  font=\tiny,
  tick/.style={text=black!70},
  lab/.style={text=black!62, align=center},
  arr/.style={-{Stealth[length=1.8mm]}, black!70},
  dim/.style={<->, black!68},
  guide/.style={black!40},
  band/.style={draw=black!55, fill=black!6, inner sep=0pt}]
  % ---- the arrival rail: sixteen frames on the input's own clock ----
  \draw[arr] (-0.25,2.05) -- (11.05,2.05);
  \foreach \i in {0,...,15}{
    \draw[black!62] ({\i*0.62+0.31},1.87) -- ({\i*0.62+0.31},2.23);}
  \node[tick, anchor=south west] at (-0.02,2.30) {a frame arrives every 40 ms};
  % ---- the window that has to fill before anything can be answered ----
  \node[band, minimum width=9.92cm, minimum height=0.72cm, anchor=south west] at (0,1.02) {};
  \node[lab] at (4.96,1.38) {one chunk: 16 frames, 640 ms of audio};
  % ---- the boundary: the instant the whole window is answered at once ----
  \draw[densely dotted, black!65] (9.92,0.30) -- (9.92,2.42);
  \node[tick, anchor=west, align=left, text width=1.55cm] at (10.02,1.16) {all sixteen answered at
    once, on one boundary};
  % ---- the two waits, as dimension lines under the band ----
  \draw[guide] (0.31,0.96) -- (0.31,0.60);
  \draw[guide] (9.61,0.96) -- (9.61,0.60);
  \draw[dim] (0.31,0.66) -- (9.55,0.66);
  \node[tick, anchor=north] at (4.93,0.60) {the first frame in the window waits the whole 640 ms};
  \draw[dim] (9.61,0.30) -- (9.86,0.30);
  \node[tick, anchor=west] at (10.02,0.24) {the last waits a moment};
  % ---- the comparison the section turns on: two rates on one ruler ----
  \draw[guide] (0.93,-0.06) -- (0.93,-0.44);
  \draw[dim] (0.31,-0.38) -- (0.87,-0.38);
  \node[tick, anchor=north] at (0.62,-0.44) {40 ms};
  \draw[dim] (0.31,-0.94) -- (9.86,-0.94);
  \node[tick, anchor=north] at (5.08,-1.00) {sixteen of them, and none answered before the last one lands};
\end{tikzpicture}
```
The chunk as a shape rather than a number: the arrival rate and the answer rate on one ruler, so the
wait a frame inherits is a horizontal distance and one period sits sixteen times inside the window it
has to fill. Both spans are the same record's two figures, and the drawing adds no measurement to
them.
:::


> **What "preemption" is doing in this heading, and what it is not.** The word came from the original
> outline for this chapter, and no record in `docs/verification/claims.json` supports a description of
> how this device arbitrates between competing work on one SM, or how long an interrupted kernel can
> be held. Two sentences about hardware arbitration would be the most quotable lines in this section,
> and they are exactly the two this book cannot source, so they are not written. What the section can
> say stands on its own: a streaming encoder's per-frame cost is dominated by host-side setup and by
> exposed waits, both of which are documented above, and any device-sharing effect is an addition to
> that, whose size is unmeasured.

**Hardware application.** On the Orin, the argument is about what to time. A stage's execution time is
not a property of the model; it is a property of a compiled graph, a driver, and a machine that may
have other things to do, so a benchmark that launches kernels one at a time from the host measures a
question this project does not ask. Two consequences are testable on the board in chapter 8 without
any new source: measure a frame, not a kernel, so the setup is inside the number; and measure the far
end of the distribution over a long run, because a short run reports a tail that the hour-long run
required by the project plan has not yet had the chance to produce.

On the FPGA, the same three costs land elsewhere, and the mapping is the point. There is no launch: a
compiled datapath is not issued per frame, so there is no host round trip on the critical path and no
setup cost that recurs. The work that CUDA Graphs does at instantiation, the toolchain does at
synthesis, once, and it is charged to the build machine rather than to the frame. A stage boundary is
wiring, so the per-frame cost becomes the sum of stage latencies plus whatever a buffer has to absorb,
which is why chapter 9 spends its time on a ring buffer rather than on a launch. What the fabric keeps
is the part no architecture removes: the encoder is chunked, so a frame that arrives late is still
answered late by up to a chunk, and that is a property of the model's contract with the audio clock,
not of the silicon under it.

> **Open questions this section leaves on purpose.** Four numbers would sharpen the argument above and
> none of them exists in this repository's evidence set: the microseconds a kernel launch costs on the
> Orin, the count of kernels one frame of the compiled encoder issues, the occupancy a streaming chunk
> reaches against the SM's resident-warp maximum, and any measured far-percentile frame latency on
> either board. The first three are a benchmark run away, and the last is chapter 8's deliverable.
> Until then this section says what the driver does and what the machine does with waiting warps,
> because those are on record, and it prints no cost, which is the difference between an architectural
> argument and a number someone else repeated.

## 3.3 Roofline Analysis: Why Voice at Batch=1 is Memory-Bound

A roofline answers one question with two lines. The horizontal axis is arithmetic
intensity: how many operations a program performs for each byte it reads. The vertical
axis is the rate the machine can sustain. A machine follows the rising line while the
work is light on arithmetic, which means it is waiting for memory, and it follows the
flat line once the work is dense enough to keep the compute units fed. The corner
between them is the ridge point, and for this book it is always the same division: peak
operations divided by peak bandwidth. `V-07-01` is the paper that introduced the plot.

> **The formula.** $R = \dfrac{P_{\text{ops}}}{P_{\text{bw}}}$
>
> **The variables.**
> - $R$ — the ridge point: the arithmetic intensity, in operations per byte, where the machine stops
>   waiting for memory and starts waiting for the compute units. A rate ratio, not a time and not a
>   count of anything.
> - $P_{\text{ops}}$ — the peak operation rate the machine can sustain, in operations per second. For
>   the two boards this is the dense compute ceiling the figure's flat line is drawn at.
> - $P_{\text{bw}}$ — the peak memory bandwidth, in bytes per second: the height of the rising line.
>
> **What it means.** Dividing a rate of operations by a rate of bytes leaves operations per byte,
> which is the one axis a workload can be placed on and a machine's two lines can be read against.
> The corner is where the two ceilings agree on a single number, so it is a ratio of the datasheet's
> two headline figures and nothing else -- which is why both boards' corners can be drawn from the
> records `V-07-02` and `V-07-03` without a measurement of this project's own.
>
> **What it costs.** Nothing to compute: $R$ is arithmetic on two numbers a datasheet already prints,
> done once when the figure is drawn. The cost it *names* is the machine's -- to sit right of the
> corner a design must be fed $P_{\text{ops}}$ worth of work for every byte of state, and a
> bandwidth-light accelerator reaches its own corner at a far lower intensity, which is the whole
> argument for the smaller part.
>
> **What it does not say.** It does not say where the Voice Edge Benchmark sits relative to $R$: that
> depends on a compiled network and a chosen kernel, and no record here has it. It also does not say
> the corner is the same point on both boards -- the two dense corners are drawn apart for exactly
> that reason -- nor does a lower $R$ mean a faster machine, only one that saturates sooner.

[Figure 11](#fig-ridge-point-comparison) puts the Kria KV260 and two Jetson Orin models on
one pair of axes. Read the rising lines before the corners. Each is labelled with the
bandwidth that fixes its height, the Orin's is the higher of the two, and so at any
intensity left of both corners the GPU is faster in absolute terms, and nothing here says
the FPGA saves this project anything.
The claim the figure supports is narrower and it is about corners: the FPGA reaches its
own ceiling at an intensity an order of magnitude lower, so a small, bandwidth-light
accelerator can be *used* where a large one sits idle. That is the whole argument of
this chapter, and `V-07-02`, `V-07-03` and the arithmetic label in the figure are all of
it.

Two things the figure does not say are worth naming. It does not say where the Voice
Edge Benchmark sits on the horizontal axis: that number belongs to a compiled network
and a chosen kernel, and no record in this book has it, so the workload is left off the
plot rather than guessed at. It also does not resolve which Orin the project will
measure against. [Figure 11](#fig-ridge-point-comparison) prints its two dense corners as two separate numbers for that
reason, and the band between them is drawn as a question, not as a range.

[Figure 12](#fig-clock-sensitivity) belongs to the FPGA corner alone. It varies the one
input behind that corner which is not a datasheet figure, which is why the FPGA corner of
[Figure 11](#fig-ridge-point-comparison) is the softest number in it.

::: {#fig-ridge-point-comparison .figure}
```tikz
% One roofline per machine, on logarithmic axes. The corners are computed here rather
% than typed, so a label cannot drift away from the division it claims to be: every
% ridge below is peak operations divided by peak bandwidth, evaluated by pgfmath from
% the same two inputs the record names.
%
% pgfmath routes the operands of a division through a TeX dimension, whose ceiling is
% about 16384, so 67000/2 fails the build with "Dimension too large" while 67/2 is
% fine. Hence every peak below is held in TOPS and every height is log10(TOPS)+3,
% which is the same point on an axis labelled in GOP/s.
\begin{tikzpicture}[
  x=2.7cm, y=1.15cm,
  declare function={X(\v)=log10(\v); Y(\t)=log10(\t)+3;},
  orin/.style={blue!55!black, thick},
  nano/.style={red!65!black, thick, densely dashed},
  fpga/.style={black, thick},
  sp/.style={loosely dotted, thick},
  dot/.style={circle, inner sep=1.1pt, fill},
  t/.style={font=\scriptsize, inner sep=2pt},
]
% Inputs. Each is the number a record carries, in the unit that record states it in.
\pgfmathsetmacro{\bwOrin}{102}                % V-02-10, GB/s; V-07-02 states it too
\pgfmathsetmacro{\bwKv}{19.2}                 % V-01-13, GB/s
\pgfmathsetmacro{\pkNxdense}{50}              % V-07-02, TOPS INT8 dense
\pgfmathsetmacro{\pkNxsparse}{100}            % V-07-02, TOPS sparse
\pgfmathsetmacro{\pkNssparse}{67}             % V-02-09, Sparse INT8 TOPS
\pgfmathsetmacro{\pkNsdense}{\pkNssparse/2}   % arithmetic on V-02-31's 2x, TOPS
\pgfmathsetmacro{\pkKvone}{1248*2*0.3/1000}   % V-01-09 slices, V-07-03 clock, TOPS
\pgfmathsetmacro{\pkKvpacked}{1248*4*0.3/1000}% the packed INT8 reading of V-07-03
\pgfmathsetmacro{\gopKvone}{\pkKvone*1000}     % V-07-03 states its peaks in GOP/s, so
\pgfmathsetmacro{\gopKvpacked}{\pkKvpacked*1000}% both labels are printed from the TOPS
% The four Orin corners and the two FPGA corners: peak divided by bandwidth.
\pgfmathsetmacro{\rdNxdense}{\pkNxdense/\bwOrin*1000}
\pgfmathsetmacro{\rdNxsparse}{\pkNxsparse/\bwOrin*1000}
\pgfmathsetmacro{\rdNsdense}{\pkNsdense/\bwOrin*1000}
\pgfmathsetmacro{\rdNssparse}{\pkNssparse/\bwOrin*1000}
\pgfmathsetmacro{\rdKvone}{\pkKvone/\bwKv*1000}
\pgfmathsetmacro{\rdKvpacked}{\pkKvpacked/\bwKv*1000}
\def\xr{3.18}   % right edge, arithmetic intensity just past 1500 OP/byte
\def\yb{1}      % bottom edge, 10 GOP/s
\def\yt{5.2}    % top edge, a little above 100000 GOP/s

% Decade grid, then the two axes.
\foreach \d in {0,1,2,3} {\draw[gray!22] (\d,\yb) -- (\d,\yt);}
\foreach \d in {2,3,4,5} {\draw[gray!22] (0,\d) -- (\xr,\d);}
\draw[<->] (0,\yb) -- (\xr,\yb);
\draw[<->] (0,\yb) -- (0,\yt);
\node[t, below] at (0,\yb) {1};
\node[t, below] at (1,\yb) {10};
\node[t, below] at (2,\yb) {100};
\node[t, below] at (3,\yb) {1000};
\node[t, left] at (0,\yb) {10};
\node[t, left] at (0,2) {100};
\node[t, left] at (0,3) {1000};
\node[t, left] at (0,4) {10000};
\node[t, left] at (0,5) {100000};
\node[below=34pt, font=\small] at (\xr/2,\yb) {arithmetic intensity, OP/byte};
\node[rotate=90, above=30pt, font=\small] at (0,3.1) {sustainable rate, GOP/s};

% The two memory roofs, each named in the ink of its own line. They go in the empty
% upper-left triangle: every compute roof starts further right than this block ends,
% and the two rising lines come within 0.3 decades of each other, so neither can be
% labelled along itself.
\node[t, anchor=north west, align=left] at (0.06,\yt-0.06) {
  \textcolor{blue!55!black}{102 GB/s: V-02-10 and V-07-02}\penalty0\\
  19.2 GB/s: V-01-13};

% The gap the undecided SKU opens, drawn under the lines so it hides none of them.
\fill[red!9] ({X(\rdNsdense)},\yb) rectangle ({X(\rdNxdense)},\yt);
\node[t, red!65!black, anchor=south] at ({(X(\rdNsdense)+X(\rdNxdense))/2},\yt+0.04)
  {which SKU? V-02-28: unresolved};

% KV260: one shallow memory roof, two compute roofs. V-07-03 carries both corners.
\draw[fpga] ({X(1)},{Y(\bwKv/1000)}) -- ({X(\rdKvone)},{Y(\pkKvone)});
\draw[sp, fpga] ({X(\rdKvone)},{Y(\pkKvone)}) -- ({X(\rdKvpacked)},{Y(\pkKvpacked)});
\draw[fpga] ({X(\rdKvone)},{Y(\pkKvone)}) -- (\xr,{Y(\pkKvone)});
\draw[sp, fpga] ({X(\rdKvpacked)},{Y(\pkKvpacked)}) -- (\xr,{Y(\pkKvpacked)});
\node[dot, label={[t]below:\pgfmathprintnumber[fixed,precision=1]{\rdKvone}}]
  at ({X(\rdKvone)},{Y(\pkKvone)}) {};
\node[dot, label={[t]above:\pgfmathprintnumber[fixed,precision=1]{\rdKvpacked}}]
  at ({X(\rdKvpacked)},{Y(\pkKvpacked)}) {};
\node[t, anchor=north east] at (\xr-0.03,{Y(\pkKvone)-0.03}) {\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvone} GOP/s};
\node[t, anchor=south east] at (\xr-0.03,{Y(\pkKvpacked)+0.03}) {\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvpacked} GOP/s};

% Orin: one shared memory roof, four compute roofs. Only the Nano Super dense line is
% arithmetic this book performs rather than a figure a record carries, so it alone is
% drawn dashed in a second ink.
\draw[orin] ({X(1)},{Y(\bwOrin/1000)}) -- ({X(\rdNxsparse)},{Y(\pkNxsparse)});
\draw[orin] ({X(\rdNxdense)},{Y(\pkNxdense)}) -- (\xr,{Y(\pkNxdense)});
\draw[sp, orin] ({X(\rdNxsparse)},{Y(\pkNxsparse)}) -- (\xr,{Y(\pkNxsparse)});
\draw[nano] ({X(\rdNsdense)},{Y(\pkNsdense)}) -- (\xr,{Y(\pkNsdense)});
\draw[sp, nano] ({X(\rdNssparse)},{Y(\pkNssparse)}) -- (\xr,{Y(\pkNssparse)});
\node[dot, orin] at ({X(\rdNxdense)},{Y(\pkNxdense)}) {};
\node[dot, orin, loosely dotted] at ({X(\rdNxsparse)},{Y(\pkNxsparse)}) {};
\node[dot, nano] at ({X(\rdNsdense)},{Y(\pkNsdense)}) {};
\node[dot, nano, loosely dotted] at ({X(\rdNssparse)},{Y(\pkNssparse)}) {};

% The four Orin ridge values are deliberately absent from the axis. They sit 0.17
% decades apart, which no rotated label clears either, and the key below already names
% each one beside the roof it belongs to.

% The key, outside the frame. Every plotted quantity is named here or on its own line.
\node[t, anchor=north west, align=left] at (\xr+0.14,\yt-0.06) {
  \textcolor{blue!55!black}{\textbf{Orin NX 16GB, MAXN}} V-07-02\penalty0\\
  \hspace*{1.5em}50 TOPS dense, corner \pgfmathprintnumber[fixed,precision=1]{\rdNxdense}\penalty0\\
  \hspace*{1.5em}100 TOPS sparse, \pgfmathprintnumber[fixed,precision=1]{\rdNxsparse}\penalty0\\
  \textcolor{red!65!black}{\textbf{Orin Nano Super}} V-02-09, V-02-10\penalty0\\
  \hspace*{1.5em}67 TOPS sparse, \pgfmathprintnumber[fixed,precision=1]{\rdNssparse}\penalty0\\
  \hspace*{1.5em}\textcolor{red!65!black}{33.5 dense, \pgfmathprintnumber[fixed,precision=1]{\rdNsdense}: no record}\penalty0\\
  \textbf{Kria KV260} V-07-03\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvone} GOP/s, corner \pgfmathprintnumber[fixed,precision=1]{\rdKvone}\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1,1000 sep={}]{\gopKvpacked} packed, \pgfmathprintnumber[fixed,precision=1]{\rdKvpacked}\penalty0\\
  dotted: sparse or packed reading\penalty0\\
  band: the dense corners of both SKUs
};
\end{tikzpicture}
```
The ridge points of the two sides, on the axes `V-07-01` defines. A rising line is one
machine's memory bandwidth and a flat line is its compute peak, so the corner where they
meet is the arithmetic intensity at which that machine stops waiting for memory. Each
corner is printed as the division that produced it and computed at compile time from the
inputs its record names; the red dashed corner is the one quantity here that no record
carries, because it is this book's own division of a sparse TOPS figure by the 2x
sparsity factor of `V-02-31`. Dotted lines are the sparse or packed second reading of a
machine, solid lines the dense reading, and the shaded band is the gap between the two
dense SKUs while `V-02-28` stays unresolved.
:::

::: {#fig-clock-sensitivity .figure}
```tikz
% The FPGA ridge point against the clock of its DSP array, with the Orin NX dense ridge
% as a horizontal reference. Both slopes are the same division as in the figure above,
% drawn here as a line instead of a point: peak operations per MHz divided by bandwidth.
\begin{tikzpicture}[
  x=0.0055cm, y=0.017cm,
  fpga/.style={black, thick},
  packed/.style={black, thick, densely dotted},
  dot/.style={circle, inner sep=1.1pt, fill},
  orin/.style={blue!55!black, thick},
  t/.style={font=\scriptsize, inner sep=2pt},
]
% Inputs, as above: 1248 slices from V-01-09, 19.2 GB/s from V-01-13, and two or four
% operations per slice per cycle from the two readings of V-07-03. Division first, and
% only ever between small numbers, because pgfmath sends operands to a TeX dimension.
\pgfmathsetmacro{\slopenone}{1248*2/19.2/1000}   % OP/byte per MHz, one MAC per slice
\pgfmathsetmacro{\slopedense}{2*\slopenone}      % the packed INT8 reading
\pgfmathsetmacro{\pkNxdense}{50}                 % V-07-02, TOPS
\pgfmathsetmacro{\bwOrin}{102}                   % V-02-10, GB/s
\pgfmathsetmacro{\rdNxdense}{\pkNxdense/\bwOrin*1000}
\pgfmathsetmacro{\fAssume}{300}                  % the clock V-07-03's figures assume
\pgfmathsetmacro{\fAlt}{500}                     % the clock its note offers
\pgfmathsetmacro{\ridgeAssume}{\slopenone*\fAssume}
\pgfmathsetmacro{\ridgeAlt}{\slopenone*\fAlt}
\pgfmathsetmacro{\gapAssume}{\rdNxdense/\ridgeAssume}
\pgfmathsetmacro{\gapAlt}{\rdNxdense/\ridgeAlt}
\pgfmathsetmacro{\fCross}{\rdNxdense/\slopedense} % where packed meets the Orin ridge
\pgfmathsetmacro{\crossRatio}{\fCross/\fAssume}   % that clock as a multiple of the assumed one
\def\xmax{2000}
\def\ymax{540}

\draw[gray!22] (0,\rdNxdense) -- (\xmax,\rdNxdense);
\foreach \f in {500,1000,1500,2000} {\draw[gray!22] (\f,0) -- (\f,\ymax);}
\draw[<->] (0,0) -- (\xmax,0);
\draw[<->] (0,0) -- (0,\ymax);
\node[t, below] at (0,0) {0};
\node[t, below] at (500,0) {500};
\node[t, below] at (1000,0) {1000};
\node[t, below] at (1500,0) {1500};
\node[t, below] at (2000,0) {2000};
\node[t, left] at (0,100) {100};
\node[t, left] at (0,200) {200};
\node[t, left] at (0,300) {300};
\node[t, left] at (0,400) {400};
\node[t, left] at (0,500) {500};
\node[below=16pt, font=\small] at (\xmax/2,0) {DSP clock, MHz};
\node[rotate=90, above=26pt, font=\small] at (0,270) {ridge point, OP/byte};

\draw[fpga] (0,0) -- (\xmax,\slopenone*\xmax);
\draw[packed] (0,0) -- (\xmax,\slopedense*\xmax);
\draw[orin] (0,\rdNxdense) -- (\xmax,\rdNxdense);
\node[t, orin, anchor=south west] at (120,\rdNxdense+8)
  {Orin NX dense ridge, \pgfmathprintnumber[fixed,precision=1]{\rdNxdense}: V-07-02};
\node[t, anchor=north west, text width=3.9cm, align=left] at (1080,150)
  {KV260 dense ridge: V-01-09 and V-01-13, and the packed reading of V-07-03 above it};

% The two clocks, and the ratio to the Orin corner that each implies.
\foreach \c/\lab in {300/assumed, 500/alternative} {
  % One ridge per clock, computed once: printnumber takes a number, not an
  % expression, and the two coordinates want the same value.
  \pgfmathsetmacro{\ridgeAtC}{\slopenone*\c}
  \draw[gray!60] (\c,0) -- (\c,\ridgeAtC);
  \node[dot] at (\c,\ridgeAtC) {};
  \node[t, below right] at (\c,\ridgeAtC)
    {\lab: {\c} MHz gives \pgfmathprintnumber[fixed,precision=1]{\ridgeAtC}};
}
\draw[gray!60] (\fCross,0) -- (\fCross,\rdNxdense);
\node[circle, inner sep=1.3pt, draw, black] at (\fCross,\rdNxdense) {};
\node[t, anchor=south west, text width=4.6cm, align=left] at (120,350)
  {Ratio to the Orin dense ridge:\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1]{\gapAssume}x at 300 MHz,\penalty0\\
  \hspace*{1.5em}\pgfmathprintnumber[fixed,precision=1]{\gapAlt}x at 500 MHz.};
\node[t, anchor=north west, text width=3.0cm, align=left] at (\fCross+16,\rdNxdense-10)
  {packed meets the ridge at
  \pgfmathprintnumber[fixed,precision=0,1000 sep={}]{\fCross} MHz,
  \pgfmathprintnumber[fixed,precision=1]{\crossRatio}x the assumed clock};
\end{tikzpicture}
```
How much of the ridge-point gap is the clock. `V-07-03` states its KV260 figures at 300
MHz, which is an assumption about a board this project has not measured, and its own note
says what the same inputs give at 500 MHz. Both lines here are the division plotted as a
single corner in [Figure 11](#fig-ridge-point-comparison), so [Figure 12](#fig-clock-sensitivity) answers one question only: does the gap survive the
assumption. It does. The FPGA ridge stays an order of magnitude below the
Orin dense ridge across every clock this book has reason to name, and the gap closes only
at the clock tagged at the right of the plot, which comes from arithmetic rather than
from a record, and which no record says the part runs at.
:::

## 3.4 Motivation for Spatial Hardware Computing on FPGAs


**Intuition.** Section 3.3 ended at a corner: the KV260 reaches its own compute ceiling at a low arithmetic intensity, and an Orin reaches its at a higher one. That is a statement about *waiting*, and waiting is a symptom. This section looks at the cause, which is a quantity the roofline does not plot at all, namely energy.

The short version is that arithmetic on a number is cheap and moving the same number is not. A neural network accelerator is therefore budgeted by its traffic before it is budgeted by its arithmetic. How many times each weight, each activation and each partial sum has to be fetched, carried across the chip, and written back is what decides the energy of one inference, and the multiply-accumulate that all of that traffic exists to serve is a small item in that account. A spatial architecture is the name for a class of machines that admits this and then does something about it: rather than hiding the wait behind a scheduler, it changes where each operand lives so that the traffic does not have to happen. The roofline said the FPGA saturates early; this section says what a designer arranges so that saturating early costs less than it sounds.

The register for the energy argument is a survey of efficient neural-network processing, and its
treatment of the subject is a figure rather than a table of measurements. Reading that figure right
matters for everything after it, because it is *normalised*: the arithmetic is the reference and every
level of the memory hierarchy is quoted against it.

> "Normalized Energy Cost 200× 6× 2× 1× 1× (Reference)"

Read the bracket as a ladder with four rungs, where the bottom rung is the arithmetic itself and every
other rung is a fetch. Reading one word from off-chip DRAM costs 200 times what operating on it costs.
Fetching it from the global buffer, the large on-chip memory that sits between the array and DRAM, costs
six times. Fetching it from the register file inside a processing element costs twice. The survey is
blunt about the size of that gap, and about what kind of statement it is:

> "fetching the data from the RF or neighbor PEs is going to cost 1 or 2 orders of magnitude lower
> energy than from DRAM"

> "DRAM can store gigabytes of data, but consumes two orders of magnitude higher energy per access
> than a small on-chip memory of a few kilobytes"

The ladder comes with the sizes of the levels it compares: a register file of 0.5 to 1.0 kB inside each
processing element, a global buffer of 100 to 500 kB shared by the array, and a network on chip of 200
to 1000 processing elements. Those three ranges are what make the ratios concrete rather than
aspirational, and they are the sizes the survey's own dataflow evaluation uses.

Two qualifications keep the ladder usable. It is normalised, not absolute: the survey prints no access
energy in picojoules anywhere in this argument, so neither does this book, and a designer who quotes the
200 as though it were a measurement of some particular board has misread the figure. It is also a
property of a class of memory hierarchies rather than of the KV260 or the Orin, and this book has not
measured either board's access energy, so the ladder is used here as an ordering of costs, which is
robust, and not as a budget, which would be a fabrication. The ordering is all the argument needs:
off-chip fetch is the expensive rung, on-chip storage is cheap, and arithmetic is cheap.

**Mechanism.** If the expensive act is carrying an operand, then the design lever is deciding which operand stays put. A processing element (PE) is one multiply-accumulate site in a spatial array, and it has a small register file (RF) of its own, local storage that costs the cheap rung to read. A dataflow is the naming convention for which operand a machine parks in that local storage and which ones it makes travel. The survey names four families, and their definitions are quoted here in full because the distinction between them is a distinction about traffic, and paraphrase tends to blur it.

> "The weight stationary dataflow is designed to minimize the energy consumption of reading weights by maximizing the accesses of weights from the register file (RF) at the PE. Each weight is read from DRAM into the RF of each PE and stays stationary for further accesses."

In a weight-stationary design, the parked operand is the weight. Each PE loads its weight once, holds it in its own register file, and multiplies it by a stream of arriving activations. What travels is therefore the input activation, which is broadcast across the array, and the partial sum, which accumulates as it goes and must be handed back through the global buffer. This pays off when a weight is reused many times, because the one expensive fetch is amortised across many multiply-accumulates.

> "The output stationary dataflow is designed to minimize the energy consumption of reading and writing the partial sums. It keeps the accumulation of partial sums for the same output activation value local in the RF."

In an output-stationary design, the parked operand is the partial sum, the running total of a dot product. The PE that owns an output accumulates into its own register file and writes nothing back until the sum is finished, so the operand that never has to leave the chip is the one that would otherwise have been read and written once per accumulated term. Weights and activations travel instead, which is a real cost and not a free one; the family bets that the partial sum is the operand with the most traffic, because it is touched repeatedly within a single dot product, and that parking it saves more than parking a weight or an activation would.

The third family is not a choice of *which* operand to park, and reading it as though it were is the mistake that makes the taxonomy look smaller than it is. It is the refusal to park anything:

> "While small register files are efficient in terms of energy (pJ/bit), they are inefficient in terms of area. In order to maximize the storage capacity, and minimize the off-chip memory bandwidth, no local storage is allocated to the PE and instead all that area is allocated to the global buffer to increase its capacity. The no local reuse dataflow differs from the previous dataflows in that nothing stays stationary inside the PE array."

No-local-reuse turns the register file's area into buffer capacity instead. Every weight, activation and partial sum travels, and the design buys bandwidth with silicon: the global buffer is larger than in either stationary family, so more data stays on chip even though none of it sits still. The survey is candid about what that costs, reporting that most of this family's accesses come from that larger buffer, whose own access energy is well above the register file's, so the overall energy stays fairly high.

The fourth family is the one the survey's own evaluation crowns, and it is worth quoting because it changes how the first three should be read:

> "A row stationary dataflow is proposed in [...], which aims to maximize the reuse and accumulation at the RF level for all types of data (weights, pixels, partial sums) for the overall energy efficiency. This differs from WS or OS dataflows, which optimize for only weights and partial sums, respectively."

The numeral in that sentence is the survey's own reference marker, elided here rather than printed. It points to Eyeriss, the spatial architecture the survey credits with the row-stationary design, and that work is not registered in this repository's source index, so the book names it in words instead of leaving a bracketed numeral that no source in this book can resolve.

Row-stationary parks nothing in particular; it optimises all the operand types at once rather than betting on one. In the survey's own comparison, held at equal area and equal processing-element count, this family uses 1.4 to 2.5 times lower energy than the others, which is the clearest available statement that betting on a single operand is a trade and not a free lunch.

The four definitions agree about the arithmetic and disagree about which operand, if any, is allowed to be cheap to reach. [Figure 13](#fig-sze-dataflows) draws three of them on the same grid so that the disagreement is the only thing visible.

::: {#fig-sze-dataflows .figure}
```tikz
% Three two-by-two PE arrays, one per dataflow family. In each array the operand the
% family parks in the PE register file is drawn with a double border, and the operands
% that must travel are drawn as light arrows through the array and down to the global
% buffer. The three grids are identical on purpose: only the parked operand differs.
\begin{tikzpicture}[
  pe/.style={draw, minimum width=13mm, minimum height=11mm, font=\scriptsize},
  stay/.style={draw, double, double distance=1pt, fill=black!10, font=\scriptsize,
    inner sep=1.5pt},
  buf/.style={draw=black!50, fill=black!4, font=\scriptsize, inner sep=3pt,
    rounded corners=1.5pt},
  bigbuf/.style={draw=black!50, fill=black!12, font=\scriptsize, inner sep=3pt,
    rounded corners=1.5pt, minimum width=30mm, minimum height=8mm},
  arr/.style={-{Stealth[length=1.8mm]}, black!55, thick},
  t/.style={font=\scriptsize, inner sep=1pt},
  ttl/.style={font=\small, align=center},
]
% Weight-stationary and output-stationary park one operand each, drawn with a double border.
% No local reuse parks nothing, so its PEs are empty and its buffer is drawn larger and
% darker, because that family gives the register file's area to the global buffer instead.
\foreach \g/\name/\anch/\row/\col/\down in {%
  0/{Weight-Stationary}/W/{Act}/{Psum}/{Psum},
  1/{Output-Stationary}/{Psum}/{Weight}/{Act}/{output}} {
  \begin{scope}[xshift=\g*4.6cm]
    \node[ttl] at (0.75,2.5) {\name};
    \node[buf] (b) at (0.75,-1.05) {global buffer};
    \foreach \x in {0,1} \foreach \y in {0,1} {
      \node[pe] (p\x\y) at (\x*1.5,\y*1.4) {};
      \node[stay] at (\x*1.5,\y*1.4) {\anch};
    }
    \draw[arr] (p00.east) -- (p10.west);
    \draw[arr] (p01.east) -- (p11.west);
    \node[t, anchor=south] at (0.75,0.08) {\row};
    \node[t, anchor=south] at (0.75,1.48) {\row};
    \draw[arr] (p00.north) -- (p01.south);
    \draw[arr] (p10.north) -- (p11.south);
    \node[t, anchor=east] at (-0.08,0.7) {\col};
    \node[t, anchor=west] at (1.58,0.7) {\col};
    \draw[arr] (0.75,-0.5) -- (b.north);
    \node[t, anchor=west] at (0.85,-0.78) {\down};
  \end{scope}
}
\begin{scope}[xshift=2*4.6cm]
  \node[ttl] at (0.75,2.5) {No Local Reuse};
  \node[bigbuf] (b) at (0.75,-1.05) {global buffer (enlarged)};
  \foreach \x in {0,1} \foreach \y in {0,1} {
    \node[pe] (q\x\y) at (\x*1.5,\y*1.4) {};
  }
  \draw[arr] (q00.east) -- (q10.west);
  \draw[arr] (q01.east) -- (q11.west);
  \node[t, anchor=south] at (0.75,0.08) {Act};
  \node[t, anchor=south] at (0.75,1.48) {Act};
  \draw[arr] (q00.north) -- (q01.south);
  \draw[arr] (q10.north) -- (q11.south);
  \node[t, anchor=east] at (-0.08,0.7) {Weight};
  \node[t, anchor=west] at (1.58,0.7) {Weight};
  \draw[arr] (0.45,-0.42) -- (0.45,-0.68);
  \node[t, anchor=east] at (0.38,-0.55) {Psum};
  \draw[arr] (1.05,-0.68) -- (1.05,-0.42);
  \node[t, anchor=west] at (1.12,-0.55) {Act, Weight};
\end{scope}
\end{tikzpicture}
```
Three families on one identical grid of processing elements, so that what differs is only what each does with its local storage. Each large square is one processing element, and the small box with the double border inside it is the operand held in that element's register file: the weight in weight-stationary, the partial sum in output-stationary. The light arrows are the operands that must travel, labelled as they move; Act is an input activation, Weight a filter weight, Psum a partial sum. The box under each array is the global buffer, and the arrow down to it is the operand that has to cross it. The two stationary families disagree over which operand stays put, and both still send something home through the buffer. The third grid, no local reuse, is the family that parks nothing: its processing elements are empty, and its buffer is drawn larger and darker because the register file's area has been spent on buffer capacity instead. Its two arrows at the bottom are the exchange that results, a partial sum written back and activations and weights refetched, on every step.
:::

**Hardware application.** Which family serves this book's workload is a design question, and the honest answer is that it leans one way for a reason the records support and is unresolved for everything beyond that reason.

A streaming inference at batch one is a poor fit for weight-stationary, and the reason is the reuse the family needs. Each weight in a streaming layer is multiplied into a small number of activations per frame, because there is no batch to multiply it into, so the expensive fetch of that weight is amortised across few uses. The operand whose traffic dominates in this regime is the partial sum, which is touched once per accumulated term inside every dot product and would have to cross the array and the buffer on every one of those touches if it were not parked. So the designs this book develops sit at the output-stationary end of the family, and the survey's definition of that family is what makes the choice legible rather than habitual.

One thing about that lean is worth stating plainly: it is not the choice the survey's own evaluation makes. Held at equal area and equal processing-element count, row-stationary is the family that survey measures as lowest energy, and a design that parks the partial sum gives up part of what row-stationary gains in exchange for a datapath a single-board toolchain can actually schedule. The book takes that exchange deliberately and names it as a trade; it does not claim the parked partial sum is optimal.

That is an inclination, not a measurement, and its edges are worth naming. The survey's taxonomy describes spatial accelerators as a class; no record in this repository says which dataflow the KV260's toolchain actually emits for a given layer, and a real compiled design usually mixes families across its stages, so a single label for the whole network would be an overclaim even after a board run. What parking the partial sum does *not* buy is the one thing section 3.3 already showed the FPGA cannot avoid: the design still has to be fed from DRAM at the rate its bandwidth allows, and the corner on that roofline moves down, not away. Chapter 4 turns to the primitives that make the choice concrete, because a parked operand is only useful once there is a multiply-accumulate structure to park it in.

> **What this section is not claiming.** The energy ladder is quoted from a survey of accelerator design, and its ratios describe the memory hierarchy that survey analyses; they are not measurements of the KV260, of the Orin, or of any board this project has run, and this book prints no access energy of its own, in picojoules or in any other absolute unit. The four dataflow definitions are quoted verbatim and describe families of architecture, not the AMD toolchain's output for a specific layer; which family any compiled stage of the Voice Edge Benchmark realises is an open question that chapter 8's board work would have to answer, and the choice argued for above is a design lean reasoned from the workload's shape, not a result.

**Traceability.** The records behind the ladder and the four definitions quoted above.

| Record | What it establishes here |
| --- | --- |
| `V-07-06` | the normalised energy ladder as its source prints it: 200 times the arithmetic cost to read from off-chip DRAM, 6 times from the global buffer, 2 times from the register file |
| `V-07-07` | the survey's own wording for that gap: a DRAM access costs two orders of magnitude more energy than an on-chip memory of a few kilobytes |
| `V-07-26` | the sizes the ladder compares: a 0.5 to 1.0 kB register file per processing element, a 100 to 500 kB global buffer, and a network on chip of 200 to 1000 processing elements |
| `V-07-08` | the weight-stationary definition, quoted verbatim above |
| `V-07-09` | the no-local-reuse definition, quoted verbatim above |
| `V-07-10` | the output-stationary definition, quoted verbatim above |
| `V-07-28` | the row-stationary result quoted above: 1.4 to 2.5 times lower energy than the other dataflows at equal area and equal processing-element count |
| `V-07-29` | the row-stationary definition, quoted verbatim above, and the survey's attribution of that design to an earlier work |
