# The Streaming Bottleneck: Why Batch=1 Stalls a GPU

> *Objective: Analyze the root architectural causes behind GPU power inefficiency, memory bandwidth saturation, and latency jitter under continuous streaming audio.*

---

## 3.1 The Mismatch Between Streaming Audio and SIMT Architecture

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
than gesturing at. One frame's activation vector is 256 channels wide (`V-05-04`), which is
8 warps' worth of lanes, calculated from those two records. Split the same vector over the encoder's 4 heads
(`V-05-04`) and a head is 64 channels wide, calculated, which is 2 warps, calculated. A frame is
therefore not a trickle. It is a handful of full groups for a general stage and a couple for one head
of attention.

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
4,096 values per channel stack to work through, calculated, which is a batch in all but name. So a chunked design buys back the
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

Now the tail. A chunk's latency is a sum: for each stage, a setup, a wait for its inputs, and its own
execution. Section 3.1 showed that the waits are covered only when some other resident warp is ready,
and that a stream of single frames is the case with the fewest of them, so the cover is thin and what
is left is exposed latency, per stage, twelve blocks deep (`V-05-04` for the depth). Exposed waits are
where a tail is made. Two more sources follow, and both are arithmetic rather than luck. A frame that
slips past a chunk boundary is not answered a moment later; it is answered when the next chunk
completes, because a chunked encoder cannot emit a decision before it has the chunk, so the penalty
for a late sample is up to a whole chunk, 640 ms of audio at 40 ms per feature frame (`V-05-05`). And
a kernel that arrives while the driver is still finishing the setup of the previous one queues, so a
jitter in the host's own timing arrives at the output summed over the stages rather than
averaged away.

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

[Figure 9](#fig-ridge-point-comparison) puts the Kria KV260 and two Jetson Orin models on
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
measure against. [Figure 9](#fig-ridge-point-comparison) prints its two dense corners as two separate numbers for that
reason, and the band between them is drawn as a question, not as a range.

[Figure 10](#fig-clock-sensitivity) belongs to the FPGA corner alone. It varies the one
input behind that corner which is not a datasheet figure, which is why the FPGA corner of
[Figure 9](#fig-ridge-point-comparison) is the softest number in it.

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
single corner in [Figure 9](#fig-ridge-point-comparison), so [Figure 10](#fig-clock-sensitivity) answers one question only: does the gap survive the
assumption. It does. The FPGA ridge stays an order of magnitude below the
Orin dense ridge across every clock this book has reason to name, and the gap closes only
at the clock tagged at the right of the plot, which comes from arithmetic rather than
from a record, and which no record says the part runs at.
:::

## 3.4 Motivation for Spatial Hardware Computing on FPGAs
