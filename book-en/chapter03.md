# The Streaming Bottleneck: Why Batch=1 Stalls a GPU

> *Objective: Analyze the root architectural causes behind the two ways a graphics processor misbehaves on continuous streaming audio -- memory bandwidth saturation when the work is too thin to fill it, and latency jitter when the waits are exposed. Power is not analyzed here; chapter seven measures it.*

---

## 3.1 The Mismatch Between Streaming Audio and SIMT Architecture

*Where this sits in the chain: the* **Output and latency** *stage -- this chapter asks why the answer arrives late, or in bursts, when the arithmetic itself is small enough to fit anywhere.*

**Intuition.** A GPU does not run many programs at once. It runs one instruction at a time across a wide group of lanes, and it keeps many such groups waiting in the wings, so that when one group stalls on memory another can be handed the next instruction. The group has a fixed width, and the machine consumes work a whole group at a time. Single instruction, multiple threads (SIMT) is the name of that shape: a thread is what the program sees as one lane, and the group of threads moving together is what the hardware schedules.

Think of a wide multi-lane highway toll booth where all cars in a row must pay exactly the same amount at exactly the same time, moving forward in complete lockstep. A training batch fits that shape by construction. The same arithmetic applies to many independent inputs at once, every lane takes the same path, and the row of cars is full. A streaming microphone fits it in one way only: it never stops. Each frame arrives on its own, and the batch dimension, the multiplier that made the machine's width easy to fill, is gone. The work has not gone with it. One frame of the Voice Edge Benchmark is a vector of channels wide, and a wide vector fills lanes. What the frame loses is the cheapest source of extra groups, which is the same thing the machine uses to cover a memory wait. So the mismatch is not that a frame is small arithmetic. It is that a frame leaves the machine with too little in flight to hide how long its memory takes. 

This starvation of the SIMT model at batch size one is the single most important physical difference between processing a photograph and processing a spoken word. The machine is built to hide its own slowness by changing the subject. When the batch size is one, there are no other subjects to change to.

**Mechanism.** The group is a warp, and the vendor architecture fixes its width: a warp is thirty-two threads. Each streaming multiprocessor (SM, the part of the GPU that owns both the arithmetic and the scheduling) creates, manages, schedules and executes threads in groups of that size, and a thread block is partitioned into warps of thirty-two. A warp issues one common instruction at a time, so full efficiency needs all lanes of it on the same path. When a data-dependent branch splits a warp, the warp executes each taken path in turn with the lanes off that path disabled; one warp's disagreement does not spread, because different warps execute independently. Two costs follow. Work that does not divide into whole warps leaves the last group partly unused. Work whose lanes disagree pays for both paths.

To understand the constraints placed on this execution model, it is necessary to perform a warp occupancy arithmetic worked example. Suppose we have an SM that can hold a maximum of 32 resident blocks and one thousand and twenty-four resident threads. Since a warp is 32 threads, one thousand and twenty-four threads means 32 resident warps. A resident warp is a warp whose execution context is currently held in the on-chip registers of the SM, making it eligible to be selected by the warp scheduler with zero context-switching overhead. However, the maximum number of resident warps is almost never the number actually achieved in practice. The achieved occupancy is bounded by three hardware limits: registers per thread, shared memory per block, and threads per block. 

Consider a hypothetical kernel processing our audio stream. Assume the SM has sixty-five thousand five hundred and thirty-six registers available. If our kernel requires one hundred and twenty-eight registers per thread, each warp of 32 threads demands four thousand and ninety-six registers. Dividing the total SM registers by the per-warp requirement gives $65536 / 4096 = 16$ warps. The hardware maximum was 32 warps, but register pressure has strictly bounded the occupancy to sixteen warps. Now consider shared memory. Assume the SM has sixty-four kilobytes of shared memory. If the programmer designates sixteen kilobytes of shared memory per thread block, the SM can hold at most four blocks. If each block is configured to contain just two warps (sixty-four threads), the SM will hold $four \times two = eight$ resident warps. The register pressure allowed sixteen, the hard limit allowed 32, but the shared memory footprint has squeezed the pipeline down to a mere eight resident warps. This worked example is why maximizing occupancy is a delicate balancing act of kernel design parameters, and why simply "running on a GPU" does not guarantee massive parallelism. 

What the target offers against those rules is a real size, and it is worth writing down rather than gesturing at. One frame's activation vector is 256 channels wide. Divide that width by the 32 lanes a warp issues together leaves eight whole warps. Split the same vector over the encoder's four heads and the same division leaves a head sixty-four channels wide and two warps. A frame is therefore not a trickle: it is eight full groups for a general stage and two for one head of attention. Eight and two are both whole numbers, so nothing here is wasted on a partial last warp -- what is thin is not the fill of one instruction but the number of independent groups the machine can hold ready to cover a memory wait.

Whether a handful is enough is the machine's question, not the model's, and the guide answers it with a list rather than a number: how many blocks and warps an SM holds at once depends on the registers and shared memory the kernel uses and the SM has, on a maximum number of resident blocks and warps per SM, and on the compute capability of the device. This book has registered no value for that maximum on the Orin, so the argument here stops at "bounded" and prints no bound.

It matters because of what the machine does with the groups it holds. Memory latency is hidden by parallelism: the SM switches to execute another warp while memory operations complete. That switch is not itself a cost. The execution context of every warp stays on-chip for the warp's whole lifetime, so switching between warps incurs no cost, and at each instruction issue cycle a scheduler selects a warp with threads ready and issues to it. Read those rules together and they say what an empty cycle is. No switching penalty is being paid, so an idle issue cycle is a missing ready warp. "The GPU was busy" and "the GPU had nothing eligible to issue" are different observations, and a stream of single frames is the case that tells them apart. When the batch size is one, the pool of independent warps is shallow. A memory fetch stalls the active warp, the scheduler looks for another resident warp to take its place, finds none, and the SM issue slot goes empty. The wait is exposed.

The situation worsens when considering memory coalescing failure, which is a structural penalty unique to how warps access memory. Coalesced access means that when the 32 threads in a warp request memory addresses, those addresses fall into a single contiguous block (typically one hundred and twenty-eight bytes), allowing the memory controller to serve all 32 requests in one physical transaction. When a workload has a batch size greater than one, threads within a warp can easily be mapped to the identical feature dimension across consecutive batch items, cleanly hitting contiguous addresses. At batch size one, the mapping often forces threads in a warp to access non-contiguous addresses, for instance striding across channels or jumping between heads. The memory controller cannot serve these scattered requests in one go. Instead, it must issue multiple overlapping memory transactions for a single instruction. This multiplies the bandwidth consumed and extends the wait time, worsening the very stall that the shallow warp pool is already failing to hide.

One qualification keeps this section honest about the model this book actually ports. A cache-aware streaming encoder is not fed one frame at a time. It consumes a chunk of sixteen frames, which is 640 ms of audio at 40 ms per feature frame. Inside a chunk the machine has four thousand and ninety-six values per channel to work through, derived as the 256 channels of one frame times the sixteen frames of one chunk -- a batch in all but name. So a chunked design buys back the parallelism that streaming removed, and the price is not arithmetic but delay: 640 ms of audio must arrive before the encoder can answer any of it. That trade, and not a missing kernel flag, is what "batch one" means on this workload. Chapter eight and chapter 9 take the chunk size as a design input for exactly that reason.

**Hardware application.** The counts above are the whole of what a GPU is handed per step, and they are worth one table because everything in section 3.2 and chapter 9 is built from them.

| What the machine is handed | Value | Source |
| --- | --- | --- |
| Channels in one frame's activation vector | 256 | V-05-04 |
| Whole warps that vector fills | eight | V-05-04 |
| Frames in one chunk of the streaming encoder | sixteen | V-05-05 |
| Channel values in one chunk, before the block loop | four thousand and ninety-six | V-05-04, V-05-05 |
| Encoder blocks that repeat the same stages | twelve | V-05-04 |
| Memory bandwidth those reads compete for | 102 GB/s | V-02-18 |

Read the last row against the first five. The bandwidth is the shared resource, and the model's shape decides how many readers it has at once: a chunk of frames, twelve blocks deep, all reading weights that a previous chunk already touched. The records say this book cannot yet turn that shape into bytes per frame, because no publisher prints a counted parameter breakdown for this encoder. So the table stops at counts of values, and the traffic is left to the board run.

To make the scheduling constraints visible, [Figure 10](#fig-warp-scheduler) draws the warp scheduler in two conditions: a full pipeline typical of training, and the starved pipeline characteristic of streaming inference.

::: {#fig-warp-scheduler .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  arr/.style={-{Stealth[length=1.5mm]}, thick, black!70},
  box/.style={draw, fill=black!five, inner sep=4pt, text width=2.5cm, align=center},
  warp/.style={draw, fill=blue!10, inner sep=2pt, minimum width=2.5cm, minimum height=0.4cm},
  stall/.style={draw, fill=red!10, inner sep=2pt, minimum width=2.5cm, minimum height=0.4cm},
  lbl/.style={text=black!80, font=\tiny}
]
  % Full Pipeline
  \node[font=\small\bfseries] at (1.25, 4.5) {Training: Full Pipeline};
  \node[lbl] at (1.25, 4.2) {Many resident warps hide memory latency};
  
  \node[warp] (w1) at (1.25, 3.5) {Warp one (Executing)};
  \node[warp, fill=gray!20] (w2) at (1.25, 3.0) {Warp two (Waiting Mem)};
  \node[warp, fill=gray!20] (w3) at (1.25, 2.5) {Warp 3 (Waiting Mem)};
  \node[warp, fill=green!10] (w4) at (1.25, 2.0) {Warp four (Ready)};
  \node[warp, fill=green!10] (w5) at (1.25, 1.5) {Warp five (Ready)};
  
  \draw[arr] (w1.east) -- ++(0.5,0) |- (w2.east);
  \node[lbl, anchor=west] at (1.8, 3.25) {Context switch (0 cycles)};

  % Starved Pipeline
  \node[font=\small\bfseries] at (6.25, 4.5) {Streaming: Starved Pipeline};
  \node[lbl] at (6.25, 4.2) {Batch=1 leaves scheduler idle during waits};
  
  \node[warp] (s1) at (6.25, 3.5) {Warp one (Executing)};
  \node[warp, fill=gray!20] (s2) at (6.25, 3.0) {Warp two (Waiting Mem)};
  \node[stall] (s3) at (6.25, 2.5) {Issue Slot Empty};
  \node[stall] (s4) at (6.25, 2.0) {Issue Slot Empty};
  \node[stall] (s5) at (6.25, 1.5) {Issue Slot Empty};
  
  \draw[arr, dashed] (s1.east) -- ++(0.5,0) |- (s2.east);
  \node[lbl, anchor=west] at (6.8, 3.25) {No ready warps};
\end{tikzpicture}
```
The warp scheduler covering a memory wait. On the left, a large batch size provides many resident warps; when the executing warp stalls on a memory fetch, the scheduler instantly swaps in a ready warp from the pool. The SM continues performing arithmetic. On the right, a batch size of one provides too few warps. When the active warps stall on scattered, uncoalesced memory reads, the pool of ready warps is exhausted. The issue slots sit empty, and the SM pays the latency of the memory fetch directly.
:::

The fabric comparison is the reason this section is in a book about FPGAs, and it is narrower than it usually looks. A register-transfer level (RTL) datapath has no warps, so it has none of the two costs above: a stage is wired to the width its tensors have, no lane is left over because of a rounding rule, and a branch that only some channels take is a multiplexer rather than a wasted pass. What the fabric does not gain is the trick with the waiting. There is no pool of resident groups to switch to while a read is in flight, so a stall is a stall, and the only cures are a deeper buffer, an earlier prefetch, or a stage that is genuinely independent. Chapter 9 sizes that buffer. What the fabric pays instead of a scheduler is idleness by construction: a datapath built one frame wide is empty between chunks, and no arriving batch can fill it, because there is no batch left to arrive.

> **Whose execution model this is, and what it does not size.** The behaviour statements above are the CUDA programming model as the vendor documents it in the guide version pinned in the source index, and that guide says the sections they come from describe the features of the SM that are common to all devices, so none of them is a claim about the Orin specifically. Three quantities this section would need to go further are not in the claims repository: the maximum number of warps resident on this device's SM, the fraction of that capacity a streaming chunk reaches, and the bytes per frame in the last paragraph. Each is a measurement, not a reading of a datasheet, so it belongs to the board run in chapter eight rather than to this argument.

**Traceability.** The records behind this section's counts and rules.

| Record | What it establishes here |
| --- | --- | --- |
| `V-02-42` | warp width: the SM creates, schedules, and executes threads in groups of 32 |
| `V-02-43` | warp independence: a data-dependent branch splits a warp, and different warps execute independently |
| `V-05-04` | activation geometry: 256 channels wide, four attention heads, twelve encoder blocks |
| `V-02-45` | SM occupancy limits: resident blocks and warps depend on registers, shared memory, and device compute capability |
| `V-02-46` | latency hiding: the SM switches to execute another warp while memory operations complete |
| `V-02-44` | zero-cost switching: warp context stays on-chip, and a scheduler selects a ready warp at each issue cycle |
| `V-05-05` | chunk size: sixteen frames per chunk, or 640 ms at 40 ms per frame |
| `V-02-18` | Orin NX memory bandwidth: 102 GB/s |
| `V-05-57` | gap: no counted parameter breakdown available for this encoder, leaving bytes per frame unmeasured |


## 3.2 Kernel Launch Overheads, Preemption, and Tail Jitter

**Intuition.** Nothing on a GPU starts itself. Every kernel, which is one pass of one stage of the network over the data the program pointed it at, begins as a request the host processor makes on the device's behalf, and making the request is work in itself. A program that runs one long kernel pays that cost once and forgets it. A streaming program runs the whole stage list again for every chunk of audio it answers, forever, so a cost that never mattered in training becomes a fixed floor under each answer. That is launch overhead.

Tail jitter is a different complaint about the same pipeline, and it needs the distinction stated before the mechanism, because the two words get used as one. Throughput says how many chunks an hour gets answered. Latency says how long one chunk waits. A system can hold its throughput and still miss a deadline, because a deadline belongs to one unlucky chunk and an average belongs to none. The project's own metric is the far end of the latency distribution rather than its middle, which chapter eight defines and states a condition for; this section is about where the far end comes from.

**Mechanism.** The vendor states the first half plainly. When a kernel is placed in a stream, the host driver performs a sequence of operations in preparation for its execution, and those operations are an overhead cost that must be paid for each kernel issued; for a kernel with a short execution time, that cost can be a significant fraction of the overall end-to-end time. Three things in that sentence are worth separating, because each one points at a different fix. The work is on the host, so a faster GPU does not remove it. It is per kernel, so it scales with how many stages the model compiles into, which is why the number of kernels per frame for this encoder is a quantity this book has to bound. And it is charged to short kernels, which is the streaming case by construction.

To formalize this cost, we introduce a timing model for the worst-case frame latency. It is an accumulation of setup delays, wait periods, and actual execution times.

> **The formula.**
> $$L_{\text{frame}} = \sum_{k=1}^{K} \bigl(t_{\text{setup},k} + t_{\text{wait},k} + t_{\text{exec},k}\bigr)$$
>
> **The variables.**
> - $L_{\text{frame}}$ — the total latency to process one frame, in microseconds.
> - $K$ — the total number of kernels launched to process the frame, a dimensionless count.
> - $t_{\text{setup},k}$ — the host driver setup time to launch kernel $k$, in microseconds.
> - $t_{\text{wait},k}$ — the time kernel $k$ sits in the queue or waits for memory, unhidden by other warps, in microseconds.
> - $t_{\text{exec},k}$ — the active execution time the multiprocessor spends on kernel $k$, in microseconds.
>
> **What it means.** The latency of a frame is not simply the sum of its mathematical operations. It is the sum over every compiled stage of the time it took the host to ask for the math, the time the device spent waiting to start the math, and the time the device actually did the math. For small kernels, the setup and wait terms dominate the execution term.
>
> **What it costs.** There is no silicon cost here; this is a timing model rather than a hardware block.
>
> **What it does not say.** It prints no value for any of these terms. A timing model describes a structure, not a measurement. How many microseconds the Orin NX driver takes to launch a kernel, or how many kernels TensorRT compiles the Conformer into, are quantities that belong exclusively to the board run in chapter 8.

The same driver guide names the primary software answer to overhead, and it is worth a paragraph because a streaming encoder is the ideal customer for it. Overhead costs like these are what CUDA Graphs exists to avoid. A workflow that will be launched many times is captured once as a graph, and the costs are paid once for the whole graph during instantiation, after which the graph is launched repeatedly with very little overhead. 

CUDA Graphs operates in three distinct phases, each moving a piece of overhead out of the critical path. The first phase is *capture*: the host driver runs through the kernel launch sequence, but instead of sending work to the GPU, it records the operations, dependencies, and memory allocations into a directed acyclic graph. The second phase is *instantiate*: the runtime analyzes the captured graph, validates its topology, and translates it into an executable format tailored to the specific GPU, performing heavy allocation work once. The third phase is *launch*: the host submits the instantiated executable graph to the GPU with a single command. By shifting the capture and instantiate phases to initialization time, the launch phase avoids host-side driver overhead entirely.

A graph is a description of a fixed sequence of work, so it fits this design for one reason and strains on it for one. The reason it fits: the encoder's stage list is the same every chunk. The reason it strains: a chunked encoder does not always do the same *amount* of work, since a partial chunk at the end of an utterance and a full chunk in the middle are different shapes, and a graph is only worth instantiating if the shape recurs. The recurrence is a chunk of sixteen frames, and nothing here registers how often the tail of an utterance breaks it.

Beyond CUDA Graphs, the deep learning compiler itself provides a second defense: kernel fusion. A framework like TensorRT does not strictly launch one kernel per mathematical layer. It analyzes the network graph and aggressively fuses consecutive operations—such as a matrix multiplication followed by an activation function and a residual addition—into a single monolithic kernel. Fusion directly reduces $K$ in our equation. Fewer kernels mean fewer round-trips to the host, fewer setups, and less data written to and re-read from global memory. When kernel fusion and CUDA Graphs are applied together, the overhead floor drops significantly, though it never reaches zero.

Now the tail. A chunk's latency is a sum over the stages it passes through, and the three terms are different physical things, mapped exactly to the equation card above. Section 3.1 showed that the waits are covered only when some other resident warp is ready, and that a stream of single frames is the case with the fewest of them, so the cover is thin and what is left is exposed latency, per stage, twelve blocks deep. Exposed waits are where a tail is made. Two more sources follow, and both are arithmetic rather than luck; [Figure 11](#fig-chunk-boundary) draws the first of them as a distance. A frame that slips past a chunk boundary is not answered a moment later; it is answered when the next chunk completes, because a chunked encoder cannot emit a decision before it has the chunk, so the penalty for a late sample is up to a whole chunk, 640 ms of audio at 40 ms per feature frame. And a kernel that arrives while the driver is still finishing the setup of the previous one queues, so a jitter in the host's own timing arrives at the output summed over the stages rather than averaged away.

::: {#fig-chunk-boundary .figure}
```tikz
% The shape behind the sentence "the penalty for a late sample is up to a whole chunk". One frame
% period is drawn 0.62cm wide, so the sixteen-frame chunk is exactly sixteen of those widths and the two waits
% are horizontal distances a reader can compare with a ruler. No value is added that section 3.2 does
% not already print from the records; every span below is a dimension line with drop guides.
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
  \node[lab] at (4.96,1.38) {one chunk: sixteen frames, 640 ms of audio};
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
The chunk as a shape rather than a number: the arrival rate and the answer rate on one ruler, so the wait a frame inherits is a horizontal distance and one period sits sixteen times inside the window it has to fill. Both spans are the same record's two figures, and the drawing adds no measurement to them.
:::

> **What "preemption" is doing in this heading, and what it is not.** The word came from the original outline for this chapter, and no record supports a description of how this device arbitrates between competing work on one SM, or how long an interrupted kernel can be held. Two sentences about hardware arbitration would be the most quotable lines in this section, and they are exactly the two this book cannot source, so they are not written. What the section can say stands on its own: a streaming encoder's per-frame cost is dominated by host-side setup and by exposed waits, both of which are documented above, and any device-sharing effect is an addition to that, whose size is unmeasured.

**Hardware application.** On the Orin, the argument is about what to time. A stage's execution time is not a property of the model; it is a property of a compiled graph, a driver, and a machine that may have other things to do, so a benchmark that launches kernels one at a time from the host measures a question this project does not ask. Two consequences are testable on the board in chapter eight without any new source: measure a frame, not a kernel, so the setup is inside the number; and measure the far end of the distribution over a long run, because a short run reports a tail that the hour-long run required by the project plan has not yet had the chance to produce.

On the FPGA, the same three costs land elsewhere, and the mapping is the entire point of the spatial accelerator thesis. There is no $K$ variable, no host round-trip, and no launch overhead per frame. An FPGA replaces $K$ temporal kernel launches with $K$ spatial, hardwired stages laid out physically on the fabric. The host setup cost, the CUDA Graph instantiation, the kernel fusion analysis—all of this is paid precisely once, by the synthesis toolchain on the developer's workstation, not by the processor during inference. A stage boundary on an FPGA is simply physical wiring connecting one block's output register to the next block's input register. The per-frame cost becomes the sum of the pipeline stage latencies plus whatever depth the synchronization buffers must absorb. This is why chapter 9 spends its time on a ring buffer rather than on a driver call. What the fabric keeps is the part no architecture removes: the encoder is chunked, so a frame that arrives late is still answered late by up to a chunk, and that is a property of the model's contract with the audio clock, not of the silicon under it.

> **Open questions this section leaves on purpose.** Four numbers would sharpen the argument above and none of them exists in this repository's evidence set: the microseconds a kernel launch costs on the Orin, the count of kernels one frame of the compiled encoder issues, the occupancy a streaming chunk reaches against the SM's resident-warp maximum, and any measured far-percentile frame latency on either board. The first three are a benchmark run away, and the last is chapter eight's deliverable. Until then this section says what the driver does and what the machine does with waiting warps, because those are on record, and it prints no cost, which is the difference between an architectural argument and a number someone else repeated.

**Traceability.** The records behind the kernel overheads and chunk boundaries.

| Record | What it establishes here |
| --- | --- |
| `V-02-47` | host overhead and graphs: host driver setup operations are paid per kernel and are significant for short executions; CUDA Graphs instantiate the workflow once to minimize this |
| `V-05-05` | chunk size: sixteen frames, 640 ms of audio at 40 ms per frame |
| `V-05-04` | encoder depth: twelve blocks |


## 3.3 Roofline Analysis: Why Voice at Batch=1 is Memory-Bound

**Intuition.** A machine can either be waiting for data (memory-bound) or waiting for compute units to finish (compute-bound). The roofline is the simplest way to see which. It plots the absolute limits of a hardware architecture on a two-dimensional grid, making it instantly visually apparent whether a given algorithm will run out of arithmetic units first or run out of memory bandwidth first. 

A roofline answers one question with two lines. The horizontal axis is arithmetic intensity: how many operations a program performs for each byte it reads. The vertical axis is the rate the machine can sustain. A machine follows the rising line while the work is light on arithmetic, which means it is waiting for memory, and it follows the flat line once the work is dense enough to keep the compute units fed. The corner between them is the ridge point, and for this book it is always the same division: peak operations divided by peak bandwidth.

**Mechanism.** The ridge point separates the two regimes.

> **The formula.**
> $$R = \dfrac{P_{\text{ops}}}{P_{\text{bw}}}$$
>
> **The variables.**
> - $R$ — the ridge point: the arithmetic intensity, in operations per byte, where the machine stops waiting for memory and starts waiting for the compute units. A rate ratio, not a time and not a count of anything.
> - $P_{\text{ops}}$ — the peak operation rate the machine can sustain, in operations per second. For the two boards this is the dense compute ceiling the figure's flat line is drawn at.
> - $P_{\text{bw}}$ — the peak memory bandwidth, in bytes per second: the height of the rising line.
>
> **What it means.** Dividing a rate of operations by a rate of bytes leaves operations per byte, which is the one axis a workload can be placed on and a machine's two lines can be read against. The corner is where the two ceilings agree on a single number, so it is a ratio of the datasheet's two headline figures and nothing else -- which is why both boards' corners can be drawn without a measurement of this project's own.
>
> **What it costs.** Nothing to compute: $R$ is arithmetic on two numbers a datasheet already prints, done once when the figure is drawn. The cost it *names* is the machine's -- to sit right of the corner a design must be fed $P_{\text{ops}}$ worth of work for every byte of state, and a bandwidth-light accelerator reaches its own corner at a far lower intensity, which is the whole argument for the smaller part.
>
> **What it does not say.** It does not say where the Voice Edge Benchmark sits relative to $R$: that depends on a compiled network and a chosen kernel, and no record here has it. It also does not say the corner is the same point on both boards -- the two dense corners are drawn apart for exactly that reason -- nor does a lower $R$ mean a faster machine, only one that saturates sooner.

**Hardware application.** [Figure 12](#fig-ridge-point-comparison) puts the Kria KV260 and two Jetson Orin models on one pair of axes. For a reader who has never seen a roofline, here is how to walk through the lines. First, look at the rising diagonals on the left. These are the memory bandwidth ceilings. Any algorithm that sits far to the left (low arithmetic intensity) will hit this slanted roof and be unable to go higher, meaning its throughput is entirely dictated by how fast it can load bytes, regardless of how many trillion operations the ALU is capable of. Next, follow the lines to the right until they hit the horizontal plateaus. These plateaus are the absolute compute ceilings. If an algorithm is far to the right (high arithmetic intensity), it performs so many operations per loaded byte that it easily outpaces the memory wall and is limited solely by the number of multipliers on the chip.

Read the rising lines before the corners. Each is labelled with the bandwidth that fixes its height, the Orin's is the higher of the two, and so at any intensity left of both corners the GPU is faster in absolute terms, and nothing here says the FPGA saves this project anything. 

The numerical gap analysis reveals the exact size of the architectural difference. The Orin NX dense ridge sits at approximately $ OP/byte. The KV260 dense ridge sits at approximately $ OP/byte. That is a $12.6$-fold difference. The physical meaning of this gap is profound: for any streaming workload whose intensity falls below $ OP/byte, the FPGA has already reached its maximum possible compute utilization and is compute-bound, working as hard as its silicon permits. At that exact same intensity, the Orin is still deep in the memory-bound slope, starved for data, wasting the vast majority of its massive ALU array while waiting for memory. The smaller, bandwidth-light accelerator can be *used* where a large one sits idle. That is the whole argument of this chapter, and the arithmetic label in the figure is all of it.

Where does the Voice Edge Benchmark sit? We cannot place an exact point because we do not have a registered parameter breakdown (a known gap). However, we can bound it qualitatively. A streaming Conformer at batch size one, reading a 256-dimensional vector to compute four heads of attention at INT8 precision, does very little work per fetched weight. It loads a matrix from memory, multiplies it by a single vector, and throws the matrix away. This is essentially a matrix-vector multiplication, which inherently possesses an arithmetic intensity close to one OP/byte. Even with aggressive layer fusion, the intensity remains far below 39 OP/byte. Thus, the workload sits far to the left of the plot, firmly in the memory-bound regime for both architectures.

Two things the figure does not say are worth naming. It does not say where the Voice Edge Benchmark sits on the horizontal axis: that number belongs to a compiled network and a chosen kernel, and no record in this book has it, so the workload is left off the plot rather than guessed at. It also does not resolve which Orin the project will measure against. [Figure 12](#fig-ridge-point-comparison) prints its two dense corners as two separate numbers for that reason, and the band between them is drawn as a question, not as a range.

[Figure 13](#fig-clock-sensitivity) belongs to the FPGA corner alone. It varies the one input behind that corner which is not a datasheet figure, which is why the FPGA corner of [Figure 12](#fig-ridge-point-comparison) is the softest number in it.

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
The ridge points of the two sides. A rising line is one machine's memory bandwidth and a flat line is its compute peak, so the corner where they meet is the arithmetic intensity at which that machine stops waiting for memory. Each corner is printed as the division that produced it and computed at compile time from the inputs its record names; the red dashed corner is the one quantity here that no record carries, because it is this book's own division of a sparse TOPS figure by the 2x sparsity factor. Dotted lines are the sparse or packed second reading of a machine, solid lines the dense reading, and the shaded band is the gap between the two dense SKUs while the exact hardware remains unresolved.
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
How much of the ridge-point gap is the clock. Both lines here are the division plotted as a single corner in [Figure 11](#fig-chunk-boundary), so Figure twelve answers one question only: does the gap survive the assumption. It does. The FPGA ridge stays an order of magnitude below the Orin dense ridge across every clock this book has reason to name, and the gap closes only at the clock tagged at the right of the plot, which comes from arithmetic rather than from a record, and which no record says the part runs at.
:::

**Traceability.** The records behind the roofline arithmetic and architectural comparisons.

| Record | What it establishes here |
| --- | --- |
| `V-07-01` | the roofline model introduction, plotting operations per second against arithmetic intensity |
| `V-07-02` | Orin NX MAXN peak rates and memory bandwidth |
| `V-07-03` | KV260 peak rates, assuming 300 MHz clock |
| `V-02-31` | the 2x sparsity factor, used to compute dense equivalents |
| `V-02-28` | unresolved SKU gap |
| `V-01-09` | KV260 DSP slice count, 1248 |
| `V-01-13` | KV260 memory bandwidth, 19.2 GB/s |
| `V-05-57` | missing parameter breakdown, keeping the workload off the exact plot |

## 3.4 Motivation for Spatial Hardware Computing on FPGAs

**Intuition.** Section 3.3 ended at a corner: the KV260 reaches its own compute ceiling at a low arithmetic intensity, and an Orin reaches its at a higher one. That is a statement about *waiting*, and waiting is a symptom. The roofline proves the FPGA is compute-bound, but being compute-bound is only beneficial if computing costs less than waiting. This section looks at the cause, which is a quantity the roofline does not plot at all, namely energy.

The short version is that arithmetic on a number is cheap and moving the same number is not. A neural network accelerator is therefore budgeted by its traffic before it is budgeted by its arithmetic. How many times each weight, each activation and each partial sum has to be fetched, carried across the chip, and written back is what decides the energy of one inference, and the multiply-accumulate that all of that traffic exists to serve is a small item in that account. A spatial architecture is the name for a class of machines that admits this and then does something about it: rather than hiding the wait behind a scheduler, it changes where each operand lives so that the traffic does not have to happen. The roofline said the FPGA saturates early; this section says what a designer arranges so that saturating early costs less than it sounds.

The register for the energy argument is a survey of efficient neural-network processing, and its treatment of the subject is a figure rather than a table of measurements. Reading that figure right matters for everything after it, because it is *normalised*: the arithmetic is the reference and every level of the memory hierarchy is quoted against it.

> "Normalized Energy Cost 200× six× 2× 1× 1× (Reference)"

Read the bracket as a ladder with four rungs, where the bottom rung is the arithmetic itself and every other rung is a fetch. Reading one word from off-chip DRAM costs 200 times what operating on it costs. Fetching it from the global buffer, the large on-chip memory that sits between the array and DRAM, costs six times. Fetching it from the register file inside a processing element costs twice. The survey is blunt about the size of that gap, and about what kind of statement it is:

> "fetching the data from the RF or neighbor PEs is going to cost one or two orders of magnitude lower energy than from DRAM"

> "DRAM can store gigabytes of data, but consumes two orders of magnitude higher energy per access than a small on-chip memory of a few kilobytes"

The ladder comes with the sizes of the levels it compares: a register file of 0.5 to 1.0 kB inside each processing element, a global buffer of 100 to 500 kB shared by the array, and a network on chip of 200 to 1000 processing elements. Those three ranges are what make the ratios concrete rather than aspirational, and they are the sizes the survey's own dataflow evaluation uses.

Two qualifications keep the ladder usable. It is normalised, not absolute: the survey prints no access energy in picojoules anywhere in this argument, so neither does this book, and a designer who quotes the 200 as though it were a measurement of some particular board has misread the figure. It is also a property of a class of memory hierarchies rather than of the KV260 or the Orin, and this book has not measured either board's access energy, so the ladder is used here as an ordering of costs, which is robust, and not as a budget, which would be a fabrication. The ordering is all the argument needs: off-chip fetch is the expensive rung, on-chip storage is cheap, and arithmetic is cheap.

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

The four definitions agree about the arithmetic and disagree about which operand, if any, is allowed to be cheap to reach. [Figure 14](#fig-sze-dataflows) draws three of them on the same grid so that the disagreement is the only thing visible.

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
    \draw[arr] (0.75,-0.42) -- (0.75,-0.68);
    \node[t, anchor=west] at (0.82,-0.55) {\down};
  \end{scope}
}
\begin{scope}[xshift=9.2cm]
  \node[ttl] at (0.75,2.5) {No Local Reuse};
  \node[bigbuf] (b) at (0.75,-1.05) {larger global buffer};
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

A streaming inference at batch one is a severely constrained environment for data reuse. In a traditional vision network with large batches, a weight fetched from DRAM is multiplied by every image in the batch before being evicted. The cost of fetching the weight is amortized. In a voice network operating at batch size one, each weight in a dense layer is fetched, multiplied exactly once into the single arriving activation vector, and discarded. If the design uses a weight-stationary dataflow, it parks a weight in the register file only to immediately replace it. The stationary operand is not actually stationary. Weight-stationary buys almost nothing here because the fundamental mechanism of its energy savings—temporal reuse—has been eliminated by the streaming constraint.

Because weights stream endlessly through the array without reuse, the operand whose traffic dominates is the partial sum. A single output activation in a matrix-vector product is the accumulation of hundreds or thousands of individual multiplications. If partial sums are forced to travel back to the global buffer after every addition, the local network-on-chip is flooded with read-modify-write traffic. The output-stationary dataflow solves this by keeping the accumulation local to the processing element's register file. The partial sum stays parked, accumulating every term of its dot product, and leaves the chip only when it is a finished output activation. This is why the designs this book develops sit firmly at the output-stationary end of the family: parking the partial sum attacks the only operand that retains any temporal reuse when batch size is one.

One thing about that lean is worth stating plainly: it is not the choice the survey's own evaluation makes. Held at equal area and equal processing-element count, row-stationary is the family that survey measures as lowest energy, and a design that parks the partial sum gives up part of what row-stationary gains in exchange for a datapath a single-board toolchain can actually schedule. The book takes that exchange deliberately and names it as a trade; it does not claim the parked partial sum is optimal.

That is an inclination, not a measurement, and its edges are worth naming. The survey's taxonomy describes spatial accelerators as a class; no record in this repository says which dataflow the KV260's toolchain actually emits for a given layer, and a real compiled design usually mixes families across its stages, so a single label for the whole network would be an overclaim even after a board run. What parking the partial sum does *not* buy is the one thing section 3.3 already showed the FPGA cannot avoid: the design still has to be fed from DRAM at the rate its bandwidth allows, and the corner on that roofline moves down, not away. Chapter four turns to the primitives that make the choice concrete, because a parked operand is only useful once there is a multiply-accumulate structure to park it in.

> **What this section is not claiming.** The energy ladder is quoted from a survey of accelerator design, and its ratios describe the memory hierarchy that survey analyses; they are not measurements of the KV260, of the Orin, or of any board this project has run, and this book prints no access energy of its own, in picojoules or in any other absolute unit. The four dataflow definitions are quoted verbatim and describe families of architecture, not the AMD toolchain's output for a specific layer; which family any compiled stage of the Voice Edge Benchmark realises is an open question that chapter eight's board work would have to answer, and the choice argued for above is a design lean reasoned from the workload's shape, not a result.

**Traceability.** The records behind the ladder and the four definitions quoted above.

| Record | What it establishes here |
| --- | --- |
| `V-07-06` | the normalised energy ladder as its source prints it: 200 times the arithmetic cost to read from off-chip DRAM, six times from the global buffer, two times from the register file |
| `V-07-07` | the survey's own wording for that gap: a DRAM access costs two orders of magnitude more energy than an on-chip memory of a few kilobytes |
| `V-07-26` | the sizes the ladder compares: a 0.5 to 1.0 kB register file per processing element, a 100 to 500 kB global buffer, and a network on chip of 200 to 1000 processing elements |
| `V-07-08` | the weight-stationary definition, quoted verbatim above |
| `V-07-09` | the no-local-reuse definition, quoted verbatim above |
| `V-07-10` | the output-stationary definition, quoted verbatim above |
| `V-07-28` | the row-stationary result quoted above: 1.4 to 2.5 times lower energy than the other dataflows at equal area and equal processing-element count |
| `V-07-29` | the row-stationary definition, quoted verbatim above, and the survey's attribution of that design to an earlier work |

## 3.5 Chapter Summary

This chapter examined the structural collision between continuous streaming audio and the architectures designed to process it. The core problem is that a streaming edge system must process audio continuously with an effective batch size of one, stripping away the massive parallelism that both graphics processors and vendor benchmarks rely upon to hide latency. We have arrived at four key architectural findings.

First, the SIMT execution model starves when fed a single frame at a time. A GPU covers its own memory latency by instantly context-switching to another resident warp. Without the multiplier of a large batch size, the pool of independent warps is shallow, memory accesses become uncoalesced, and the SM issue slot simply sits empty. The wait becomes exposed. 

Second, temporal kernel launch overhead creates a fixed floor under every frame. On a GPU, every functional layer of the network requires a host round-trip to set up and launch the kernel. For a streaming network that repeats its stages indefinitely, this overhead accumulates rapidly. While CUDA Graphs and layer fusion can push this floor down, they cannot eliminate it. An FPGA removes this cost entirely by replacing temporal launches with physical, hardwired spatial stages.

Third, the roofline analysis confirms that edge voice inference operates deep in the memory-bound regime. The ridge point of the KV260 sits at 39 OP/byte, and the Orin NX dense ridge sits at 490.2 OP/byte. At batch size one, the arithmetic intensity of a matrix-vector product is near one OP/byte. Both machines are therefore waiting for memory, but the FPGA reaches its compute ceiling at an order of magnitude lower intensity, making its smaller pool of multipliers vastly more efficient for this specific shape of work.

Fourth, a spatial architecture leverages output-stationary dataflows to mitigate this exact traffic. In a regime where weights are fetched once per frame and discarded without reuse, weight-stationary designs buy nothing. Parking the partial sum in the local register file is the only way to intercept the operand that is actually reused temporally, keeping the heaviest traffic entirely off the network-on-chip.

What this chapter has *not* proven is any measured latency. The timing models and architectural claims presented here are structural; they describe how the machines behave, but they print no values for the Orin's actual frame latency or the KV260's true power draw. Those physical measurements are the exclusive domain of chapter eight, which executes the board run. Before those numbers can be measured, the spatial logic must be built, which is the exact subject of chapter 4.

## 3.6 Exercises: four problems that tie the concepts to the metal

> **Exercise 3.1 (Pencil) -- Ridge point calculation and ratio.**
> The ridge point is the arithmetic intensity where a machine stops waiting for memory and starts waiting for compute units. Compute the dense INT8 ridge point for the Orin NX and the KV260 using the following inputs: the Orin NX has a peak memory bandwidth of $102$ GB/s and a peak compute of $50$ TOPS. The KV260 has a peak memory bandwidth of $19.2$ GB/s. For the KV260's compute, assume $1{,}248$ DSP slices operating at $300$ MHz, where each slice can perform $2$ operations per cycle in packed INT8 mode. (a) Compute the KV260's peak compute in GOP/s. (b) Compute the ridge point for both boards in operations per byte. (c) Compute the ratio of the Orin NX ridge point to the KV260 ridge point and interpret what that ratio means for a bandwidth-starved workload.
>
> **Solution.**
> (a) The KV260 peak compute is $1248 \text{ slices} \times 2 \text{ ops/cycle} \times 300 \text{ MHz} = 748{,}800 \text{ MOP/s}$, which is $748.8$ GOP/s, computed as the product of slices, operations per cycle, and clock frequency.
> (b) The Orin NX ridge point is $50 \text{ TOPS} / 102 \text{ GB/s} = 50{,}000 \text{ GOP/s} / 102 \text{ GB/s} \approx 490.2$ operations per byte, computed as peak compute divided by peak bandwidth. The KV260 ridge point is $748.8 \text{ GOP/s} / 19.2 \text{ GB/s} = 39$ operations per byte, computed identically.
> (c) The ratio is $490.2 / 39 \approx 12.6$, computed as the quotient of the two ridge points. This means the Orin NX requires $12.6$ times more arithmetic intensity than the FPGA to reach its maximum compute efficiency. For a workload like streaming inference that sits at very low intensity, the GPU will waste the vast majority of its massive ALU array waiting for memory, while the FPGA will saturate its smaller array much sooner.

> **Exercise 3.2 (Analysis) -- The fraction of a frame spent launching.**
> Consider a hypothetical streaming Conformer with 12 blocks, consuming audio in chunks of 16 frames per chunk, with 256 channels. Suppose each encoder block compiles to 4 sub-layers, and each sub-layer requires 3 un-fused kernel launches. (a) How many total kernel launches does the host driver execute to process one chunk? (b) Assume a hypothetical host driver overhead of 5 microseconds per kernel launch (note: this is a hypothetical value for the exercise, not a registered measurement). What is the total launch overhead per chunk in microseconds? (c) One frame period is $40$ milliseconds. What fraction of a single $40$ ms frame period is consumed *solely* by the host setup overhead for the entire chunk?
>
> **Solution.**
> (a) The total launches per chunk is $12 \text{ blocks} \times four \text{ sub-layers/block} \times 3 \text{ kernels/sub-layer} = 144$ launches per chunk, computed as the product of the depth and the kernels per block.
> (b) The total launch overhead is $144 \text{ launches} \times 5 \ \mu\text{s/launch} = 720 \ \mu\text{s}$, computed as the product of the launch count and the hypothetical per-launch overhead.
> (c) The frame period is $40 \text{ ms}$, which is $40{,}000 \ \mu\text{s}$. The fraction consumed by launch overhead is $720 / 40{,}000 = 0.018$, or $1.8\%$, computed as the total overhead divided by the frame period. While $1.8\%$ seems small, this is pure overhead spent on the CPU before a single flop of arithmetic is executed on the GPU, and it is a fixed floor that cannot be optimized away by a faster GPU architecture.

> **Exercise 3.3 (Design) -- Capture and replay in CUDA Graphs.**
> CUDA Graphs reduces the launch overhead floor by capturing a sequence of kernel launches once and replaying the instantiated graph many times. (a) Describe the capture, instantiate, and launch phases for 3 full, identical chunks of audio. (b) Name one structural reason why CUDA Graphs strains on a continuous voice stream, specifically concerning the final, partial chunk of an utterance.
>
> **Solution.**
> (a) For 3 full chunks:
> - Chunk one (Capture & Instantiate): The host driver records the 144 kernel launches into a directed acyclic graph without executing them. The runtime then instantiates this graph into an executable format, allocating memory and validating dependencies. This phase pays the heavy setup overhead.
> - Chunk one (Launch): The instantiated graph is submitted to the GPU in a single command and executed.
> - Chunk two (Launch): The identical, already-instantiated graph is submitted again in a single command. The setup overhead is bypassed.
> - Chunk 3 (Launch): The graph is submitted a third time in a single command.
> (b) CUDA Graphs strains on a continuous stream because a captured graph requires a perfectly fixed execution topology. If an utterance ends and leaves a partial chunk of, say, 7 frames instead of sixteen, the data shape changes. The instantiated graph for 16 frames cannot accept 7 frames. The system must either pad the partial chunk with silence (wasting compute), fall back to slow individual kernel launches, or pay the heavy instantiation cost again to capture a new seven-frame graph.

> **Exercise 3.4 (Compare) -- Weight reuse at batch size one.**
> The Sze survey normalizes energy costs as: arithmetic = $1\times$, register file (RF) = $2\times$, off-chip DRAM = $200\times$. Consider a weight-stationary dataflow where a weight is read from DRAM into the RF, and then multiplied by input activations. (a) At batch size one, with $256$ input channels, how many times is a single fetched weight reused in the RF to compute a dot product before it is discarded? (b) At batch size $32$, how many times is that same weight reused? (c) Explain why batch size one heavily erodes the energy advantage of a weight-stationary dataflow.
>
> **Solution.**
> (a) At batch size one, a dense layer weight is multiplied exactly once by the single arriving activation vector. Therefore, the weight has $0$ reuses in the RF; it is fetched from DRAM, multiplied once, and immediately overwritten by the next weight.
> (b) At batch size $32$, the identical weight is multiplied by $32$ independent activation vectors. It is fetched from DRAM once, parked in the RF, and reused $31$ times for the subsequent batch elements.
> (c) A weight-stationary dataflow saves energy by amortizing the massive $200\times$ DRAM fetch cost across many $2\times$ RF reads. At batch size one, there is no amortization. Every weight fetched incurs the full $200\times$ penalty for a single $1\times$ arithmetic operation. The dataflow parks a weight that is never actually stationary, completely eroding the intended energy advantage and shifting the dominant traffic cost to the un-parked partial sums.

