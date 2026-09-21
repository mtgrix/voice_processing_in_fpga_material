# FPGA Microarchitecture for Edge AI: Logic, DSP, BRAM and Dataflow

> **Scope note (Issue #66, superseding the stub).** This chapter was a list of four headings. It is
> now the microarchitecture behind every capacity number used later in the book, written from the
> primitive up: what a piece of fabric physically is, what one unit of it costs, and what the device
> in this project actually contains. Two rules shape it. First, every hardware claim about *this*
> part traces to a named source; where a low-level figure is named only in a device guide this
> project could not retrieve, the book names the gap and prints no number,
> because a figure that reads like a datasheet value, with no source behind it, is the failure mode
> this book exists
> to avoid. Second, nothing here is a synthesis result. No design has been placed, routed or timed,
> so every throughput figure in this chapter is arithmetic on a device count, never a measurement.
> The chapters that would pay for a measurement -- chapter 5 on toolchains, chapter 6 on the audio
> front end in logic, chapter 10 on power -- are pointed to rather than pre-empted.

> *Objective: Know what the fabric of the target device is made of at the level where a count
> becomes a design decision: the look-up table, the multiply-accumulate slice, the two memory
> tiles, the streaming handshake between blocks, and the residency test that decides whether a
> model can live on-chip at all.*

---

> ### Minimal Mathematics / Prerequisites for this Chapter
>
> - **Counting in powers of two**: how the number of input wires on a logic element sets the size of
>   the table stored inside it.
> - **Units of storage**: kilobits, kibibytes and kilobytes, and why one datasheet row can be read
>   two defensible ways.
> - **Throughput as a product**: items per cycle, cycles per second, and the difference between them.
> - **Fixed-point numbers**: the register width a multiply-accumulate has to hold, from chapter 1's
>   audio frames and chapter 5's quantisation.

---

## 4.1 Spatial vs. Temporal Computing Paradigms

*Where this sits in the chain: the* **Fabric logic** *stage -- what the fabric a design is wired into
is built from, and what one unit of it costs. The Model stage above hands its arithmetic down here.*

**Intuition.** A processor and a fabric do the same arithmetic in two physically different ways, and
the difference is not speed. It is *where* the work lives. A central processing unit is one small
machine that does many things one after another: it keeps a list of instructions in memory, reads the
next one, acts, moves on. Every part of it is reused for every step. Its silicon population -- how
many adders, how wide a memory port, how many things can happen at once -- is fixed when the chip is
made, and only the list changes. A field-programmable gate array (FPGA -- silicon whose wiring is set
after manufacture) inverts that. There is no list. The design *is* the wiring: for each computation a
different piece of silicon is built, and all the pieces a computation needs sit side by side and act
in the same moment.

That is the whole word "spatial". A processor computes in **time**: one place, many steps. A fabric
computes in **space**: many places, each stepping through its own small job while the others do
theirs. The words are not metaphors. On the device this book targets, "one place" is one population
of 117,120 look-up tables (LUT -- the basic logic element of this family) that every design must share,
and "many places" means that a design spending a thousand of them on one stage physically cannot
spend them on another. The budget is a geography.

**Mechanism.** Three hardware styles, laid end to end, show what each one gives up.

A **general microprocessor** buys flexibility with a fetch stage. It runs any program, and pays for
that in two directions: the instruction list must be read from memory before anything is computed, and
one step's result must be written before the next can depend on it. A single instruction occupies most
of the machine, and the machine's width is decided by the vendor.

A **graphics processing unit** (GPU -- the processor this book's Jetson baseline runs on) buys
throughput by applying the *same* instruction to many data items at once, and hides its memory reads
behind thousands of independent threads. It is still a temporal machine: instructions are still
fetched and executed in program order, and its arithmetic units are still general-purpose
implementations of whatever the instruction names. What its parallelism cannot buy it is the ability
to have no memory traffic at all. Chapter 2 argues that, and chapter 3 turns it into a roofline.

An **FPGA** buys a custom datapath and pays in configuration time. A design is described in a hardware
description language, compiled into gates, placed onto the fabric, routed, and written into a
**bitstream** -- the configuration image that sets the look-up tables, the wiring and the initial
contents of the block memories. That compile is a build measured in minutes to hours, not a launch
measured in milliseconds, and until it finishes the chip is not yet the machine that will do the work.
In exchange, a stage that needs no memory read contains no memory read, a datapath of a given width
costs that width, and every stage can accept its own item on the same clock edge.

[Figure 15](#fig-spatial-vs-temporal) draws the exchange: the same four-layer sequence, on the same
amount of silicon, both ways. On the left one block of hardware is reused four times, so four time
slots are occupied and no slot holds two layers. On the right four different blocks hold four
different layers at once and a single item leaves the column after one pass -- but each block is
committed to its own job, so a fifth layer has nowhere to go.

::: {#fig-spatial-vs-temporal .figure}
```tikz
% One four-stage sequence, run two ways over the same height of hardware. Left: one block, four uses
% of it, drawn as four slots in time. Right: four blocks, one use each, drawn as four rows in space.
% Both columns sit on the same 4-unit grid, so the reader can see that the same silicon height is
% spent either way and that the whole difference is on the other axis.
\begin{tikzpicture}[
  font=\scriptsize,
  blk/.style={draw, minimum width=2.05cm, minimum height=7.6mm, inner sep=1pt, align=center},
  reuse/.style={blk, fill=black!9},
  ded/.style={blk, fill=black!55, text=white},
  tick/.style={font=\tiny, text=black!62, align=center},
  arr/.style={->, black!72, semithick},
  lab/.style={font=\tiny\itshape, text=black!72},
  dim/.style={<->, black!45, thin}]
% ---------- panel (a): a temporal machine ----------
  \node[lab, anchor=west] at (-0.05,4.52) {(a) one machine, four moments};
  \node[reuse] at (1.3,3.8) {shared block\\ layer 1};
  \node[reuse] at (1.3,2.7) {shared block\\ layer 2};
  \node[reuse] at (1.3,1.6) {shared block\\ layer 3};
  \node[reuse] at (1.3,0.5) {shared block\\ layer 4};
  \draw[arr] (1.3,3.42) -- (1.3,3.08);
  \draw[arr] (1.3,2.32) -- (1.3,2.00);
  \draw[arr] (1.3,1.22) -- (1.3,0.90);
  \node[tick, anchor=east] at (0.20,3.8) {$t_0$};
  \node[tick, anchor=east] at (0.20,2.7) {$t_1$};
  \node[tick, anchor=east] at (0.20,1.6) {$t_2$};
  \node[tick, anchor=east] at (0.20,0.5) {$t_3$};
  \draw[dim] (2.62,0.5) -- (2.62,4.10);
  \node[tick, anchor=west] at (2.72,2.55) {one block,\\ four passes:\\ the same\\ hardware is\\ asked again\\ and again};
% ---------- panel (b): a spatial machine ----------
  \begin{scope}[shift={(7.05cm,0)}]
    \node[lab, anchor=west] at (-0.05,4.52) {(b) four machines, one moment};
    \node[ded] at (1.3,3.8) {block 1\\ layer 1};
    \node[ded] at (1.3,2.7) {block 2\\ layer 2};
    \node[ded] at (1.3,1.6) {block 3\\ layer 3};
    \node[ded] at (1.3,0.5) {block 4\\ layer 4};
    \draw[arr] (1.3,3.42) -- (1.3,3.08);
    \draw[arr] (1.3,2.32) -- (1.3,2.00);
    \draw[arr] (1.3,1.22) -- (1.3,0.90);
    \node[tick, anchor=west] at (2.42,3.8) {stage};
    \node[tick, anchor=west] at (2.42,2.7) {stage};
    \node[tick, anchor=west] at (2.42,1.6) {stage};
    \node[tick, anchor=west] at (2.42,0.5) {stage};
    \draw[dim] (-0.30,4.16) -- (2.20,4.16);
    \node[tick] at (0.95,4.32) {all four live at once};
    \node[tick, anchor=west] at (3.00,2.55) {four blocks,\\ one pass each:\\ four items\\ in flight, and\\ a fifth layer\\ needs a fifth\\ block};
  \end{scope}
\end{tikzpicture}
```
The same four layers, on the same height of hardware. Panel (a) reuses one block across four slots; panel (b) gives each layer its own block, so four items are in flight where (a) has one. Adding a layer to (a) lengthens a program; adding one to (b) means finding a fifth block, which is a fitting problem rather than a programming one.
:::

**Hardware application.** Read the two columns as two answers to "what happens to the fifth layer". In
the temporal column, nothing happens: the program gets one line longer and the same silicon does one
more pass, so a deeper model costs time, and time is a per-frame bill. In the spatial column, a fifth
layer has to be *built*, and its gates have to come from somewhere, so a deeper model costs fabric,
and fabric is a one-off bill paid at compile time and never again. That is the sentence behind every
capacity figure in the book: on a GPU a bigger model is slower; on a fabric a bigger model may simply
not exist. Chapter 9 needs it for the streaming Conformer overlay, and chapter 8 needs it to explain
why a keyword-spotting network small enough to wire out is small enough to be worth wiring.

A second consequence follows from the first, and it is the one a voice engineer meets sooner. A spatial
design's latency is not an average over many runs. Each stage in panel (b) commits its answer on a
clock edge, so the delay from an item entering the datapath to its result leaving is the number of
stages times the clock period -- no dependence on how much work the machine has already done, no queue
forming in front of it. Whether that stays true once a stage cannot keep up is section 4.3's subject. A
temporal machine's per-item delay contains a scheduler, a memory round trip, and whatever else was
already in flight. For a system whose front end has a frame deadline in single-digit milliseconds,
"no queue" is not a small convenience; it is the difference between a bounded and an unbounded worst
case. What this section cannot give is the clock period itself, because a synthesised design's achieved
frequency is a placement result and no measurement of one exists for this device -- chapter 3's ridge
point has to assume a clock for exactly this reason.

**Where the numbers come from.** Every quantity below is tied to the row that names it; the two figures that would
need a measurement -- a build's wall-clock and a synthesised clock period -- are named as absent
rather than estimated.

| Source | What it says |
| --- | --- |
| <!-- V-01-03 --> UltraScale data sheet (DS890), device-feature table, CLB-LUTs row | the fabric holds 117,120 LUTs, so splitting the pool between stages is a division of a fixed number |
| <!-- V-01-15 --> UltraScale data sheet (DS890), the device column that carries all four populations | the device column those counts belong to, printed in full: LUTs, flip-flops, memory blocks and DSP slices together |
| <!-- V-01-01 --> Kria K26 SOM data sheet (DS987), the overview that names the part | the part the budget belongs to, marked on the module rather than inferred from a board name |
| <!-- V-04-01 --> Vivado user guide (UG973), the architecture-support table, no-licence row | building any of it needs no licence: the device is supported in the standard Vivado ML Standard flow |

**From dataflow to fabric.** Chapter 3 met the three dataflow families and the one thing each of them
parks in its processing elements: weights, input activations, or running sums. What this book has not
yet answered is what those processing elements are made of, because the answer decides which family a
given model can actually afford. A stationarity strategy is a claim about where data lives, and the
next section walks the three kinds of place a KV260 fabric can hold data in: the look-up tables that
build logic and small memories, the DSP slices that do the arithmetic, and the block RAM that holds
everything else. Each one is a stationarity decision waiting to be made, and each one reappears when
the book ports the streaming recogniser in chapter 9.

## 4.2 FPGA Hardware Primitives: CLBs, DSP48E2, and SRAM Blocks

**Intuition.** A fabric is not a list of components. It is a large population of identical, generic
pieces, and a design is what happens when you tell those pieces what to become. Three kinds of piece
matter here, and they answer three different questions a designer asks:

- a **look-up table** answers "what should come out given what just came in?" -- combinational logic,
  no memory of the past, a stored answer rather than a computed one;
- a **flip-flop** answers "what was the answer last time?" -- one bit held across a clock edge, which
  is the only thing that turns logic into a machine with state;
- a **memory block** answers "what did I store at some address I choose later?" -- bulk storage that
  costs no logic at all.

A fourth piece, the **DSP48E2 slice** (the multiply-accumulate block of this family), answers the
question a neural network actually asks thousands of times per frame: "what is this number times that
number, plus what I already had?" Everything in this section is one of those four.

Mechanically, the first two are packed together into a **configurable logic block** (CLB -- the cell
that the datasheet counts when it prints an LUT total), and the memory and arithmetic pieces sit in
columns beside the logic. What a design does is allocate against those populations, and the datasheet
is the allocation sheet.

### The look-up table: logic as a stored answer

**Mechanism.** Start from the smallest case, because it needs no new mathematics. A logic gate with
two inputs has four possible input combinations. Saying what the gate does is exactly saying what it
outputs for each of those four: that is a table with four rows. An **and** gate is the table
$0,0,0,1$; an **or** gate is $0,1,1,1$; an exclusive-or is $0,1,1,0$. Two different gates are two
different tables. Nothing about this depends on silicon -- a truth table with $k$ inputs has one row
per input combination, and the number of combinations of $k$ yes-or-no choices is the point of the
card below.

Now invert the engineering. Instead of building a gate out of transistors, build a tiny memory whose
address is the input combination and whose stored bit is the answer. Then *any* function of those
inputs is implementable -- not by wiring, but by writing different contents in. That is a look-up
table: a small random-access memory with its address wires exposed as the logic inputs and its data
output exposed as the logic output. A design's logic is data. This is what makes the device
programmable, and it is also why the datasheet counts LUTs rather than gates: gates are what a
designer writes, LUTs are what the silicon actually contains.

>
> **The formula.**
>
> $$c(k) = 2^{k}$$
>
> **The variables.**
>
> - $c$ — the number of memory cells one table must hold. A count of bits.
> - $k$ — the number of input wires on the table. A count of wires.
> - $2$ — the number of values each input wire can take, low or high. A count, written as the base of
>   the power because a table's rows are chosen one wire at a time.
>
> **What it means.** Each input wire doubles the number of distinct situations the table can be
> confronted with, so wires compound multiplicatively rather than adding up. Four inputs give $2^4 = 16$
> rows; five give $2^5 = 32$; six give $2^6 = 64$. The doubling is why the size of a logic cell is
> quoted as an input count: going from five inputs to six does not add one row, it adds as many rows as
> the whole previous table had. It is also why the relationship is a ceiling on what one cell can
> express -- a function of seven variables needs two of these tables and something to combine their
> outputs, not a slightly bigger one.
>
> **What it costs.** One table of $k$ inputs costs $2^{k}$ SRAM cells and one address decoder, and it
> is *the same piece of silicon* whatever the function is -- chapter 1's Mel triangle weights, a
> comparator, and the enable line of a register all become cell contents rather than wiring. The
> population for this device is 117,120 tables, counted as `CLB LUTs` by the datasheet row
> named in the table at this section's end. What no fetched source names is $k$ for this family's
> table: the device architecture guide that would name it could not be retrieved by this project, so
> this book leaves it unstated, and no figure in this book is computed from it. The consequence for a reader is narrow but
> real: an LUT count is a count of *cells*, and converting it into "how much logic" needs $k$, so the
> only honest per-cell statement available is a proportion -- see the next card.
>
> **What it does not say.** Not a speed, and not a cost per function. A table with six wires can hold a
> function that is trivial to compute in hardware (an and of five inputs) or one that is expensive, and
> the table is priced the same either way -- which is the quiet gift of this style of logic: a
> complicated boolean function is free at run time once it fits in one cell. It also says nothing about
> whether a design *can* be expressed: it says only that a design needing $n$ tables has to find $n$
> of the 117,120.

**Mechanism, second half.** The flip-flop is the piece that makes a datapath rather than a combinator
pile: one bit, held until the clock edge, then replaced by whatever its input said at that edge. It
costs no LUT cells, which is why the two populations are counted as two datasheet rows and budgeted
separately -- and why their ratio is a design constraint worth computing before writing any code.

>
> **The formula.**
>
> $$r = N_\text{FF} / N_\text{LUT}$$
>
> **The variables.**
>
> - $r$ — how many flip-flops the device provides per LUT. A ratio, so dimensionless.
> - $N_\text{FF}$ — the device's registered flip-flop count: 234,240, the `CLB Flip-Flops` row of the
>   datasheet column this section's table names. A count of one-bit registers.
> - $N_\text{LUT}$ — the device's LUT count: 117,120, the `CLB LUTs` row of the same column. A count of
>   logic tables.
>
> **What it means.** The division comes out at exactly two, computed from the two registered counts
> rather than asserted: 234,240 / 117,120 = 2.0. Whatever the repeating unit of this fabric is, it
> hands out flip-flops at twice the rate it hands out tables, so a design that needs more than two
> held bits per logic table will run out of flip-flops first and a design that needs fewer will run out
> of tables first. That is a usable pre-flight check on a datapath, because a pipeline register is
> usually the cheap part: a 16-bit sample travelling down a datapath costs 16 flip-flops and no
> table at all, while the logic that decides what to do with it costs tables and few registers.
>
> **What it costs.** Nothing by itself; it prices a *shape*. Concretely, in this device's terms: a
> weight-stationary multiply-accumulate column that holds one 16-bit weight and one 32-bit
> accumulator per lane spends 48 flip-flops per lane and can spend very few LUTs, so with 234,240
> registers on hand the register-bound ceiling for that column shape is 4,880 lanes -- computed by
> dividing the registered flip-flop count by 48, and well above the 1,248 arithmetic slices that
> the same datasheet column registers as the real ceiling. The registers are not the constraint. The multipliers are.
>
> **What it does not say.** Not the packing, and not how the cells are grouped. The datasheet counts
> cells; the device guide that would name how many sit in one group this project could not retrieve,
> so this book never prints a logic-slice count. Any such figure would be the LUT total divided by an
> input count that no retrievable source states, and a derived number inherits a missing premise.
> Nor does the ratio say a design *can* use all of both:
> placement is a packing problem, a table and a register in the same group share wiring, and a
> utilisation report is where the truth about any one design lives: the tool command that prints one,
> named in this section's table, is the only legitimate source of a real per-design number.

[Figure 16](#fig-ch4-lut-truth-table) is the two halves of that argument drawn together: the left panel
shows a function becoming contents, the right shows what a design then has to fit into.

::: {#fig-ch4-lut-truth-table .figure}
```tikz
% Panel (a): an exclusive-or as an address and a stored bit -- logic as data. The four rows are the
% four combinations of two wires, which is 2^2 by the first card and is a worked instance, not a
% device claim. Panel (b): what a design is measured against -- the three registered populations,
% drawn as their own bars because the point of (b) is that a design picks a scarce resource, and the
% ratios between these counts span two orders of magnitude.
\begin{tikzpicture}[
  font=\scriptsize,
  cell/.style={draw, minimum size=6.2mm, inner sep=0pt},
  bit/.style={cell, fill=black!58, text=white, font=\scriptsize},
  head/.style={font=\tiny\itshape, text=black!72},
  row/.style={font=\tiny, text=black!72, align=center},
  arr/.style={->, black!72, semithick},
  pop/.style={draw=black!72, fill=black!12, minimum height=4.6mm, inner sep=1pt, align=right},
  val/.style={font=\tiny, text=black!72, anchor=west}]
% ---------- panel (a): the table ----------
  \node[head, anchor=west] at (0,3.05) {(a) a function, written in as data};
  \node[head] at (0.30,2.62) {$a$};
  \node[head] at (0.85,2.62) {$b$};
  \node[head, anchor=west] at (1.15,2.62) {address $\to$ stored bit};
  \foreach \i/\aa/\bb/\v in {0/0/0/0, 1/0/1/1, 2/1/0/1, 3/1/1/0} {
    \node[row] at (0.30,2.20-\i*0.56) {\aa};
    \node[row] at (0.85,2.20-\i*0.56) {\bb};
    \node[bit] at (1.62,2.20-\i*0.56) {\v};
    \node[row] at (2.55,2.20-\i*0.56) {row \i};
  }
  \node[row, anchor=north west, align=left] at (0.00,-0.10) {four rows, because $2^2 = 4$:\\
    the stored column \emph{is} the gate};
% ---------- panel (b): the populations ----------
  \begin{scope}[shift={(5.15cm,0)}]
    \node[head, anchor=west] at (0,3.05) {(b) what a design is measured against};
    \node[row, anchor=east] at (1.62,2.52) {logic tables\\ {\scriptsize LUTs}};
    \node[row, anchor=east] at (1.62,1.60) {registers\\ {\scriptsize flip-flops}};
    \node[row, anchor=east] at (1.62,0.68) {memory tiles\\ {\scriptsize BRAM + URAM}};
    \node[row, anchor=east] at (1.62,-0.24) {multipliers\\ {\scriptsize DSP slices}};
    \draw[pop] (1.72,2.30) rectangle (4.62,2.74);
    \draw[pop] (1.72,1.38) rectangle (4.62,1.82);
    \draw[pop, fill=black!30] (1.72,0.46) rectangle (1.86,0.90);
    \draw[pop, fill=black!30] (1.72,-0.46) rectangle (1.80,-0.02);
    \node[val] at (4.72,2.52) {117,120};
    \node[val] at (4.72,1.60) {234,240};
    \node[val] at (1.98,0.68) {208 tiles: 144 + 64, full bars off this scale};
    \node[val] at (1.92,-0.24) {1,248 -- the same width of fabric, 94 times fewer};
    \node[row, anchor=west] at (1.72,-0.72) {bar lengths are proportional to count, so the two bottom rows are deliberately tiny};
  \end{scope}
\end{tikzpicture}
```
Panel (a): a two-wire function is four stored bits, and changing the gate means rewriting the bits, not the wiring. Panel (b): the four registered populations at the same scale. A design that needs multipliers is short of something a design that needs logic has in abundance, and a figure drawn on one axis is the only way to show that without a table.
:::

### The DSP48E2 slice: one multiply and one add, kept together

**Intuition.** Chapter 1 ended with the same three words over and over -- multiply, add, accumulate --
and chapter 8 calls them a fused multiply-accumulate (MAC -- one multiplication and one addition done
as one step). A general ALU can do a multiply or an add. Doing both as one step, on wide operands,
every clock, is not a general-purpose thing to be good at: it needs the multiplier's result wired
straight into an adder whose other input is its own previous output, registered so the next
multiplication can begin before this addition finishes. A fabric that is a population of logic tables
would build that out of hundreds of LUTs and run it slowly, so fabrics do not build it. They ship it.

**Mechanism.** One **DSP48E2 slice** is a small, fixed datapath whose job is precisely that fused step:
take two operands, multiply, add something to the product, keep the result. It is not a processor and
it has no instruction; what a design chooses is what the two operands are and what gets added. That is
the whole of it, and the simplicity is the point: a design's arithmetic throughput is therefore not a
property of the design so much as a property of how many slices it was allowed to instantiate.

>
> **The formula.**
>
> $$A \mathrel{+}= x \cdot w$$
>
> **The variables.**
>
> - $A$ — the accumulator: the running total, held in a register that survives the clock edge. Its
>   width is what a dot product's partial sums need room to grow into, and no datasheet figure fixes it for
>   this device.
> - $x$ — one input value: a sample, or an activation from the previous layer. A number in whatever
>   format the design chose, fixed-point at every point in this book's route.
> - $w$ — one weight: the same number every frame, which is why section 4.4 asks where it lives rather
>   than how fast it arrives.
> - $\mathrel{+}=$ — read "becomes itself plus": the old $A$ is an operand of the operation that
>   replaces it, so one step of the loop consumes the previous step's result.
>
> **What it means.** A dot product is this line repeated and summed, so a MAC is the unit that a neural
> network's arithmetic is actually made of -- which is why a fabric counts them. The line says nothing
> about how fast: the answer to that is how many slices the design holds and how many products each
> one commits per clock, and both of those are the same two numbers for every design on this device.
> The accumulation also carries a warning the next card picks up: the register has a width, the true
> sum of a long dot product needs a wider one, and fixed-point arithmetic gets to choose what happens
> when it does not fit.
>
> **What it costs.** One slice per lane, and 1,248 slices exist -- the `DSP Slices` row of the device
> datasheet, printed as "1.2K" in the board's own rounded summary, a rounded reading
> that sits 4% below the 1,248 the row actually counts and must not be used as a budget. So
> a lane-per-slice design has 1,248 lanes of ceiling before any other resource is touched, and that
> count divides every throughput number in this book: chapter 3's ridge point is built on it, and
> chapter 1's Mel-stage arithmetic spread itself over it. What a slice costs in the *other* currencies
> has only one measured answer: the vendor's own convolution engine puts 710 slices into a
> network accelerator alongside 52,161 LUTs and 255 memory tiles -- a real footprint, and one
> measured on a different board.
>
> **What it does not say.** Not the width of the multiplier, and not how many stages of registers are
> inside the slice. Both are named only in the device guide this project could not fetch, and the
> practical consequence is plain: this book cannot compute a
> maximum achievable clock from a DSP48E2's internal structure, which is why chapter 3's ridge point
> assumes a fabric clock instead of deriving one. Nor does the count say 1,248 lanes are *usable*
> together: they must be placed, fed with operands, and kept supplied by the memory tiles that the
> next subsection counts, and a design whose arithmetic units outnumber its ability to feed them is
> waiting on data rather than computing. That is the roofline of chapter 3 seen from the inside.

[Figure 17](#fig-ch4-mac-pipeline) draws the one distinction in that card that changes a throughput
number: whether the slice waits for its own answer before taking new work.

::: {#fig-ch4-mac-pipeline .figure}
```tikz
% Two shapes for the same MAC. (a): the combinational chain, where the accumulate loop closes through
% one long path, so a new pair cannot start until this one's total is in. (b): the same arithmetic with
% the loop cut by registers, so several partial sums are in flight and one new pair is accepted every
% cycle -- with a longer trip from input to output. This is the generic shape, drawn because the
% device-specific stage assignment inside a real DSP48E2 is unregistered here.
\begin{tikzpicture}[
  font=\scriptsize,
  op/.style={draw, minimum width=1.55cm, minimum height=6.6mm, inner sep=1pt, align=center},
  reg/.style={draw, fill=black!58, minimum width=3.0mm, minimum height=6.6mm, inner sep=0pt},
  arr/.style={->, black!75, semithick},
  back/.style={->, black!70, semithick, densely dashed},
  lab/.style={font=\tiny\itshape, text=black!72},
  note/.style={font=\tiny, text=black!65, align=center}]
% ---------- panel (a): no cut ----------
  \node[lab, anchor=west] at (0,2.35) {(a) the loop closes through logic: one answer at a time};
  \node[op] (m1) at (0.95,1.20) {multiply\\ $x\cdot w$};
  \node[op] (a1) at (3.05,1.20) {add\\ $+\,A$};
  \node[reg] (r1) at (4.35,1.20) {};
  \node[note, anchor=west] at (4.55,1.20) {$A$};
  \draw[arr] (m1) -- (a1);
  \draw[arr] (a1) -- (r1);
  \draw[back] (r1) |- (2.45,0.35) -| (a1);
  \node[note] at (3.20,0.20) {previous total, from this same cycle's end};
  \node[note, align=left] at (2.30,2.00) {one pair in flight\quad\textbullet\quad the clock period must cover multiply {\em and} add\quad\textbullet\quad a new pair waits};
% ---------- panel (b): cut ----------
  \begin{scope}[shift={(0,-3.15cm)}]
    \node[lab, anchor=west] at (0,2.35) {(b) the loop is cut by registers: a new pair every cycle};
    \node[op] (m2) at (0.95,1.20) {multiply};
    \node[reg] (r2) at (2.00,1.20) {};
    \node[op] (a2) at (3.05,1.20) {add};
    \node[reg] (r3) at (4.10,1.20) {};
    \node[reg] (r4) at (4.85,1.20) {};
    \node[note, anchor=west] at (5.05,1.20) {$A$};
    \draw[arr] (m2) -- (r2);
    \draw[arr] (r2) -- (a2);
    \draw[arr] (a2) -- (r3);
    \draw[arr] (r3) -- (r4);
    \draw[back] (r4) -- ++(0.55,0) |- (3.60,0.35) -| (a2);
    \node[note] at (3.60,0.18) {one cycle later, and the adder is free again};
    \node[note, align=left] at (2.55,2.00) {several items in flight\quad\textbullet\quad each stage's delay is one register's delay\quad\textbullet\quad the result arrives later};
  \end{scope}
\end{tikzpicture}
```
The same arithmetic, two schedules. Panel (a) closes its accumulation loop through combinational logic, so the next pair waits for this one's total; panel (b) cuts the loop with registers, so a pair starts every cycle while the first one is still travelling. The filled bars are registers: panel (b) buys throughput by holding more state, which is why the flip-flop count of the last card is a real budget.
:::

### The memory blocks: two tiles, one geometry

**Mechanism.** Two kinds of bulk storage are wired into this fabric, and they differ in size, not in
kind. A **block RAM** (BRAM -- on-chip storage) tile is a 36-kilobit block that can also be used as
two independent 18-kilobit halves. An **UltraRAM** (URAM -- the deeper block of
this family) tile is 288 kilobits, a pair of sizes derived -- as this section's table shows
-- from the datasheet's own printed totals. The tile sizes are why the datasheet counts *blocks* rather than bytes: capacity is
not allocated continuously, it is allocated in whole tiles, and the unit of allocation is the fact that
decides what a design fits into.

>
> **The formula.**
>
> $$C_\text{SRAM} = \bigl(N_\text{BRAM}\,c_\text{BRAM} + N_\text{URAM}\,c_\text{URAM}\bigr) / 8$$
>
> **The variables.**
>
> - $C_\text{SRAM}$ — the fabric's total on-chip storage, in bytes once the divide by eight happens.
>   A count of bytes.
> - $N_\text{BRAM}$ — the number of block RAM tiles, 144, from the datasheet's `Block RAM Blocks` row.
> - $c_\text{BRAM}$ — the size of one block RAM tile, 36 kilobits, from the derived pair of tile sizes.
> - $N_\text{URAM}$ — the number of UltraRAM tiles, 64, from the `UltraRAM Blocks` row.
> - $c_\text{URAM}$ — the size of one UltraRAM tile, 288 kilobits, from the same derivation.
> - $8$ — the number of bits in a byte. A count, not a measured quantity.
>
> **What it means.** Storage is bought in tiles, so the total is a sum of two products, and each product
> is a count of containers times the size of one container. The divide by eight exists because the
> silicon is measured in bits and everything a designer carries is measured in bytes: the weights of a
> model, the width of a bus, the size of a frame. The two terms are not equal, and the inequality is
> the design fact -- 64 tiles of the deep kind carry 18,432 kilobits, where 144 of the shallow kind
> carry 5,184, so computed from those two products the deep blocks are 78.0% of the fabric's storage
> while being 30.8% of its tiles. A designer counting tiles is not counting bytes.
>
> **What it costs.** Every number in this card traces to the datasheet: 144 and 64 tiles from the two
> rows this section's table names, 36 and 288 kilobits from the tile-size derivation, and the
> 23,616-kilobit sum from the datasheet's own printed totals. Carried to bytes it is 2,952 KiB, which
> is 3,022,848 bytes, which the same totals unroll to 2.8828 MiB and to 3.02 MB read as a million
> bytes -- the identical quantity wearing four units. Two further on-chip storage populations are
> deliberately left out of this sum: 3.5 Mb of distributed RAM, which is built from the
> LUTs of the first card and therefore spends logic rather than arriving free, and 256 KB of
> processor-side memory, which is not fabric storage at all.
>
> **What it does not say.** Not what a design can use. The 144 and 64 tiles are gross populations: the
> design that this book is building toward also needs storage for its input buffer, its line buffers,
> its activations, its key-value cache, and the vendor accelerator's own weight staging, and a
> measured example of the collision exists: a convolution core that asks for 255 block RAM
> tiles against a device holding 144 does not fit, and no arithmetic in this card changes that. Nor
> does it say how fast: a tile's port count and its clock behaviour are per-configuration choices this book leaves unnamed. And it does not say the total is convenient, which is the subject of section 4.4.

**Hardware application.** The unit arithmetic in that card is not pedantry: the same storage answered to two names --
"about 4 MB" and "about 4.5 MB" -- until the division in the card showed which one the silicon
actually holds. The figure that survives carries its unit with it, and the two readings are both
named in the table below. [Figure 18](#fig-ch4-tile-geometry)
draws the same fact as geometry, because "3.02 MB, mostly in the deep tiles" is a shape: two grids of
containers, one cell eight times the other by area, and the design has to pick.

::: {#fig-ch4-tile-geometry .figure}
```tikz
% The two tile populations at ONE scale, so a reader can see the fact the prose states in bytes:
% one deep tile holds 8 shallow tiles' worth of storage. The side ratio is therefore sqrt(8), NOT
% 8 -- eight is the AREA (and capacity) ratio, which is what holds bits. 144 = 12x12 and 64 = 8x8
% are both perfect squares, so each population is a grid rather than an arbitrary strip. Counts and
% per-tile sizes (36 Kb, 288 Kb) are registered; the grid arrangement is a drawing, not a
% placement result. Ink area is exactly proportional to bits: 64*(sqrt(8)*a)^2 : 144*a^2 = 8.
\begin{tikzpicture}[
  font=\tiny,
  sh/.style={draw=black!58, fill=black!9, minimum size=0.20cm, inner sep=0pt, outer sep=0pt},
  dp/.style={draw=black!70, fill=black!46, minimum size=0.566cm, inner sep=0pt, outer sep=0pt},
  cap2/.style={font=\tiny\itshape, text=black!72, align=center},
  note/.style={font=\tiny, text=black!62, align=left}]
  % ---- 144 block RAM tiles: 12 x 12 grid of 0.20cm squares, 0.26cm pitch, on baseline y=0 ----
  \foreach \c in {0,...,11}{\foreach \r in {0,...,11}{%
    \node[sh] at (0.260*\c+0.100, 0.260*\r+0.100) {};}}
  \node[cap2] at (1.53,3.34) {144 block RAM tiles\\ 36 Kb each\quad 5,184 Kb total};
  % ---- 64 UltraRAM tiles: 8 x 8 grid, square side sqrt(8)*0.20 = 0.566cm, 0.626cm pitch ----
  \foreach \c in {0,...,7}{\foreach \r in {0,...,7}{%
    \node[dp] at (4.260+0.626*\c+0.283, 0.626*\r+0.283) {};}}
  \node[cap2] at (6.734,5.23) {64 UltraRAM tiles\\ 288 Kb each\quad 18,432 Kb total};
  % ---- the scale statement, and the count-vs-bytes fact the geometry encodes ----
  \node[note, anchor=north west] at (0,-0.34) {one scale: each deep square is $\sqrt{8}\approx 2.8$ times as wide as a shallow one,\\
    so eight times its \emph{area} -- and area, not side, is the storage that a weight fits into};
  \node[note, anchor=north west] at (0,-1.16) {30.8\% of the containers (64 of 208) carry 78.0\% of the bits (18,432 of\\
    23,616 kilobits): the deep grid is the fewest boxes and most of the storage};
\end{tikzpicture}
```
The fabric's storage at one scale: 144 shallow 36-kilobit tiles as a square grid, 64 deep 288-kilobit tiles as a smaller square grid beside it, drawn so each deep square is the square root of eight wide and so eight shallow tiles fit inside one deep one by area. Two thirds of the containers hold a fifth of the bits, which is why a capacity question has to be asked in bytes and an allocation question in tiles.
:::

**Where the numbers come from.** What stands behind this section's printed numbers, and what this book leaves
unnamed. Nothing here is
a measured per-design result: the only measured footprint belongs to a vendor
accelerator on another board, and it is cited as that.

| Source | What it says |
| --- | --- |
| <!-- V-01-03 --> UltraScale data sheet (DS890), device-feature table, CLB-LUTs row | 117,120 `CLB LUTs`, the logic population a design allocates against |
| <!-- V-01-04 --> UltraScale data sheet (DS890), device-feature table, flip-flop row | 234,240 `CLB Flip-Flops`, the second term of the 2.0 ratio |
| <!-- V-01-05 --> UltraScale data sheet (DS890), device-feature table, block-RAM row | 144 block RAM tiles, and each is 36 Kb usable as two 18 Kb halves |
| <!-- V-01-07 --> UltraScale data sheet (DS890), device-feature table, UltraRAM row | 64 UltraRAM tiles |
| <!-- V-01-23 --> derived: the tile-size table (DS891) divided against the block counts (DS890) | the tile sizes, 36 Kb and 288 Kb, derived from the datasheet's own printed totals |
| <!-- V-01-22 --> the summed tile capacities (DS890, DS891) carried along the unit chain | the 23,616 Kb sum and its unit chain to 2,952 KiB, 3,022,848 bytes, 2.8828 MiB and 3.02 MB |
| <!-- V-01-16 --> UltraScale data sheet (DS890), device-feature table, distributed-RAM row | 3.5 Mb of distributed RAM, which spends LUTs and is excluded from that sum |
| <!-- V-01-17 --> UltraScale data sheet (DS890), device-feature table, embedded-memory row | 256 KB of processor-side on-chip memory, not fabric storage |
| <!-- V-01-09 --> UltraScale data sheet (DS890), device-feature table, DSP row | 1,248 `DSP Slices`, the multiplier ceiling every throughput figure divides by |
| <!-- V-01-19 --> derived: the rounded column (DS986) compared with the exact counts (DS890) | that the rounded "1.2K" is 4% low against 1,248, so it must not be used as a budget |
| <!-- V-01-15 --> UltraScale data sheet (DS890), the device column that carries all four populations | the datasheet column all four populations are read from, which is what makes them one device |
| <!-- V-01-11 --> summed from the block counts (DS890) and the tile-size table (DS891) | two megabyte readings, each once defensible, of which the unit chain keeps one |
| <!-- V-04-07 --> DPU product guide (PG338), the measured-footprint table, B4096 row | one measured accelerator footprint, 52,161 LUTs with 710 slices and 255 tiles, on a different board |
| <!-- V-04-09 --> derived: the guide's footprint (PG338) held against this device's counts (DS890) | the comparison, derived from the rows above, that it does not fit this device |
| <!-- V-04-06 --> Vivado user guide (UG906), the Report Utilization section | the report command that is the only legitimate source of a per-design number |
## 4.3 Streaming Interfaces: AXI4-Stream Protocol and Backpressure

**Intuition.** Section 4.1 established that a fabric design is several machines working at once, and
once they are separate machines they can disagree about timing. One stage produces a Mel frame every
hop, the frame stride of chapter 1's front end; the next consumes one per encoder step; the one after
that may stall for a hundred cycles while a division resolves. A datapath that assumes all its stages
are always ready is a
datapath that silently loses data the first time they are not. So between every pair of blocks the
design needs an agreement, and the agreement has to answer one question in one clock: *may this item
be handed over now?*

The answer this book's designs use is the streaming interface of the family named in chapter 9,
AXI4-Stream (the on-chip point-to-point streaming protocol of this vendor's interconnect), whose rule
fits on two lines and costs two wires per channel. It is described here as the book's own working
definition, because the specification that formally defines it is an Arm document this project could
not retrieve: **the timing rules of this subsection come from no retrieved source**, and nothing in
them should be read as a quotation.

**Mechanism.** A streaming channel carries a payload on one set of wires and two control signals
beside it, and all three are sampled on the same clock edge.

- the source raises **TVALID** to say "what is on the payload wires right now is a real item, and I
  will hold it until you take it";
- the destination raises **TREADY** to say "I can accept an item on this edge";
- a transfer happens on a clock edge **if and only if both are high**. One high wire is a wish; two
  is a handshake.

That is the whole rule. Its teeth are in what the rule forbids. A source may not drop TVALID while
TREADY is low, because that would delete an item nobody received; a destination may not treat a payload
as valid unless TVALID is high, because the source is allowed to change the wires whenever it is not.
Neither side has to stay ready, and neither has to stay valid, so a channel is legal even when each end
stalls for hundreds of cycles -- which is the property that makes a design composable. The consequence
for a designer is the one that costs real silicon: **stalls propagate backwards**. When a stage is not
ready, the channel feeding it holds its item, so that stage cannot accept a new one, so *its* upstream
holds, and so on to the source. The condition is called back-pressure, and a pipeline under
back-pressure is doing nothing while continuing to burn its clock.

[Figure 19](#fig-ch4-stream-handshake) draws the rule and its two failure modes on one time axis. Read
the item labelled $D$ first: it is offered at cycle 3, held for two cycles because the destination
dropped TREADY, and transferred at cycle 5 -- and it occupies three cycles of the payload band because
holding an item and losing an item are different things, which is the entire value of the protocol.
Then read cycles 6 and 7, where the picture's other half lives: TREADY is high and nothing transfers,
because the source had nothing to send. Those two stretches look alike in a table of utilisation and
have opposite causes.

::: {#fig-ch4-stream-handshake .figure}
```tikz
% A streaming channel over ten cycles, on a 0.62cm-per-cycle grid so the geometry *is* the argument.
% A transfer dot sits under exactly the cycles where both control wires are high -- 0, 1, 2, 5, 8, 9 --
% item D spans three cycles because it was offered at 3, refused, held, and accepted at 5, and cycles
% 6-7 are a bubble where the destination waits on a source that has nothing. The levels are this
% book's own drawing of the two-line rule above, not a captured trace: no record backs any timing
% here, which is stated in the prose and in the section's traceability table.
\begin{tikzpicture}[
  font=\tiny,
  hi/.style={draw=black!82, line width=0.6pt},
  ed/.style={draw=black!82, line width=0.6pt},
  sig/.style={anchor=east, text=black!80, align=right},
  xferdot/.style={fill=black!78, circle, inner sep=1.05pt},
  note/.style={font=\tiny, text=black!64, align=left},
  itm/.style={inner sep=1.3pt, font=\tiny}]
% ---- the two shaded regions, first, so everything sits on top ----
  \fill[black!7]   (1.86,-1.60) rectangle (3.10,3.92);
  \fill[black!3.5] (3.72,-1.60) rectangle (4.96,3.92);
  \node[anchor=south, text=black!72, align=center, font=\tiny\itshape] at (2.48,3.98)
    {back-pressure:\\ held two cycles};
  \node[anchor=south, text=black!62, align=center, font=\tiny\itshape] at (4.34,3.98)
    {a bubble:\\ nothing to send};
% ---- cycle ruler ----
  \foreach \c in {0,...,9} {
    \pgfmathsetmacro{\xa}{0.62*\c}
    \pgfmathsetmacro{\xm}{\xa+0.31}
    \draw[black!40] (\xa,3.28) -- (\xa,3.40);
    \node[text=black!58] at (\xm,3.58) {\c};
  }
  \draw[black!40] (6.20,3.28) -- (6.20,3.40);
  \node[text=black!58, anchor=south west] at (0.05,3.80) {clock cycle};
% ---- clock ----
  \foreach \c in {0,...,9} {
    \pgfmathsetmacro{\xa}{0.62*\c}
    \pgfmathsetmacro{\xb}{\xa+0.31}
    \pgfmathsetmacro\xc{\xa+0.62}
    \draw[hi] (\xa,2.98) -- (\xb,2.98);
    \draw[ed] (\xb,2.98) -- (\xb,2.68);
    \draw[ed] (\xb,2.68) -- (\xc,2.68);
    \ifnum\c<9 \draw[ed] (\xc,2.68) -- (\xc,2.98); \fi
  }
  \node[sig] at (-0.10,2.83) {clk};
% ---- TVALID: high over cycles 0-5 and 8-9 ----
  \draw[ed] (0,2.02) -- (0,2.32);
  \draw[hi] (0,2.32) -- (3.72,2.32);
  \draw[ed] (3.72,2.32) -- (3.72,2.02);
  \draw[ed] (3.72,2.02) -- (4.96,2.02);
  \draw[ed] (4.96,2.02) -- (4.96,2.32);
  \draw[hi] (4.96,2.32) -- (6.20,2.32);
  \node[sig] at (-0.10,2.17) {TVALID\\ source offers};
% ---- TREADY: low over cycles 3 and 4 only ----
  \draw[ed] (0,1.36) -- (1.86,1.36);
  \draw[ed] (1.86,1.36) -- (1.86,1.06);
  \draw[hi] (1.86,1.06) -- (2.48,1.06);
  \draw[ed] (2.48,1.06) -- (2.48,1.36);
  \draw[ed] (2.48,1.36) -- (6.20,1.36);
  \node[sig] at (-0.10,1.21) {TREADY\\ destination takes};
% ---- the payload bus: a wide channel, so one box is many items ----
  \draw[black!45, thin] (0,0.26) -- (6.20,0.26);
  \draw[black!45, thin] (0,0.90) -- (6.20,0.90);
  \node[fill=black!11, itm] at (0.31,0.58) {$A$};
  \node[fill=black!11, itm] at (0.93,0.58) {$B$};
  \node[fill=black!11, itm] at (1.55,0.58) {$C$};
  \node[fill=black!42, text=white, itm] at (2.48,0.58) {$D$\ held};
  \node[fill=black!42, text=white, itm] at (4.34,0.58) {idle};
  \node[fill=black!11, itm] at (5.27,0.58) {$E$};
  \node[fill=black!11, itm] at (5.89,0.58) {$F$};
  \node[sig] at (-0.10,0.58) {payload\\ $W$ bits};
% ---- the transfer row ----
  \node[sig] at (-0.10,-0.22) {transfer};
  \foreach \x in {0.31,0.93,1.55,3.41,5.27,5.89} \node[xferdot] at (\x,-0.22) {};
  \foreach \x in {2.17,2.79} \node[text=black!58] at (\x,-0.22) {no};
  \foreach \x in {4.03,4.65} \node[text=black!40] at (\x,-0.22) {no};
% ---- the two readings, side by side under their own regions ----
  \node[note, anchor=north west] at (0.00,-0.60)
    {back-pressure, cycles 3-4:\\ a real item sits on the wires\\ while both ends say ``later'';\\ the source may not let go of it.};
  \node[note, anchor=north west] at (3.72,-0.60)
    {a bubble, cycles 6-7:\\ the destination is ready\\ but the source has nothing,\\ so the channel idles at this end.};
\end{tikzpicture}
```
Ten cycles of one channel. A transfer is drawn where and only where TVALID and TREADY are both high, so the six dots are the rule itself rather than an illustration of it; item $D$ is three cycles wide because it was offered, refused, held, and finally accepted, which is what the protocol guarantees and what a design without it would silently lose.
:::

The honest reading of that picture is the important one: the rule is four words, and everything hard
about a streaming design follows from the fact that no one may assume anything beyond them.

**Mechanism, priced.** Two costs attach to obeying the rule, and both are per channel.

>
> **The formula.**
>
> $$n_\text{wire} = W + 2$$
>
> **The variables.**
>
> - $n_\text{wire}$ — the number of signal wires one streaming channel needs, apart from the clock. A
>   count of wires.
> - $W$ — the payload width: how many bits the channel carries per transfer. A count of bits.
> - $2$ — the two control signals of the rule above, TVALID and TREADY. A count, not a measurement.
>
> **What it means.** The handshake is a fixed overhead per transfer rather than per bit, so a wide
> payload amortises it and a narrow one pays for it every cycle. That is the reason a design carrying
> one 16-bit audio sample per transfer is a design with a bad idea: the same two control wires would
> serve 32 samples if the payload were widened to 512 bits, and the item rate the rest of the pipeline
> must handle would fall by that same factor. Widening is not free either -- a 512-bit payload means
> the source must accumulate 32 samples before its first valid edge, which is a buffer and a delay --
> so the payload width is a latency decision disguised as a bus decision.
>
> **What it costs.** No datasheet fixes a channel width, a per-channel overhead, or a clock for a design of this kind -- and that absence is the point of the card. What the card can be read
> against is the fabric's own totals: $W$ payload bits need $W$ registers to be held across an edge at
> each end of the link, so a 512-bit channel registered at both ends is 1,024 flip-flops of the 234,240
> the device datasheet registers -- computed from those two numbers as 0.44% of the device's registers. A
> buffer deep enough to absorb a stall costs storage again, and section 4.2 is where that currency is
> counted.
>
> **What it does not say.** It does not say a channel is unlimited in rate. Throughput on a streaming
> channel is $W$ bits per *transferring* cycle, and the number of transferring cycles per second is a
> clock times a duty fraction, neither of which this book can measure -- so this book never prints a
> streaming bandwidth for a link of this kind. Any such figure a reader meets elsewhere is a synthesis
> result from a design they are not looking at, which is the distinction the whole chapter is built to
> keep visible.

**Hardware application.** Back-pressure is where chapter 3's roofline becomes physical. A stage held
off by its destination is a stage whose multipliers are idle, and idle multipliers are the exact
mechanism by which a device with 1,248 arithmetic slices delivers the throughput of a smaller one. The
designer's response is not to make stalls illegal -- the rule is what makes composition possible -- but
to absorb them: a buffer between two stages whose rates disagree lets one keep working while the other
waits, and its price is storage plus the latency of filling it. Every buffer in this book is that
sentence in a different guise: chapter 8's audio frame buffer, chapter 9's left-context ring, and the
overlapping hop that chapter 1 pays for in re-reads are all answers to "two stages, different rates,
nothing may be lost".

There is a boundary where this stops being a design choice, and it is the one the next section crosses:
back-pressure coordinates stages *inside* the fabric. It cannot make an external memory fast.

**Where the numbers come from.** This section prints one device quantity and one percentage, and the absence behind the
rest of it is the finding.

| Source | What it says |
| --- | --- |
| <!-- V-01-04 --> UltraScale data sheet (DS890), device-feature table, flip-flop row | 234,240 flip-flops, the denominator of the register cost, and the only fabric population the wire card's arithmetic touches |
| no retrieved source | the protocol specification itself, the definitions of TVALID and TREADY, every level and interval in [Figure 19](#fig-ch4-stream-handshake), any channel width, and any streaming bandwidth -- the interface is this book's working definition, and no retrieved source fixes its details

---

## 4.4 On-Chip Weight Residency: Eliminating External DRAM Traffic

**Intuition.** A trained network is two kinds of number. Weights are read the same way every frame, in
an order the design decides once. Activations are new every frame. On a fabric those two facts want
opposite treatments, and the treatment for weights has a name: keep them on-chip, permanently, in
storage that belongs to the design. That is *weight residency*, and on this particular board it is not
an optimisation. It is forced by the topology. The memory controller -- the logic that drives the
external chips -- sits on the fixed processor side of the device, and the fabric reaches it only
through the ports between the two sides; no memory pins run from the fabric straight to the chips.
Every weight read by a fabric design is therefore a request into a controller it shares with the
processors it is co-located with.

**Mechanism.** The residency question is one product and one comparison, and the product is where the
unit traps live.

>
> **The formula.**
>
> $$B_w = P \times b / 8 \qquad \text{versus} \qquad C_\text{SRAM}$$
>
> **The variables.**
>
> - $B_w$ — the bytes a weight set occupies in the format the design will actually store it in. A count
>   of bytes.
> - $P$ — the parameter count of the model: 77,000, 93,000 or 140,000 for the three keyword-spotting
>   variants chapter 8 targets, and about 14 million for the small Conformer of chapter 9. A count of
>   weights.
> - $b$ — the bits holding one weight after quantisation: 8 for INT8, 4 for INT4. The choice is
>   chapter 5's subject, and every figure below is stated at a named $b$, because the same model is a different
>   size at each.
> - $8$ — bits per byte. A count.
> - $C_\text{SRAM}$ — the fabric's whole on-chip storage: 2,952 KiB, the byte reading of the
>   23,616-kilobit total of section 4.2's last card. A count of bytes, so the two sides are
>   comparable.
>
> **What it means.** Weights are numbers, and numbers cost bytes at a width the designer picks, so a
> weight set's size is a count times a width -- which is why quantisation is a *storage* technique
> before it is an accuracy technique, and why halving $b$ halves $B_w$ exactly. Comparing the product
> against $C_\text{SRAM}$ asks the residency question in its whole: could every weight sit on-chip at
> once, if the fabric spent nothing else on storage? Clearing the comparison makes a resident design
> possible; failing it at every available $b$ means no resident design exists and the alternatives are
> a smaller width, a smaller model, or an architecture that streams weights across the boundary this
> section is about.
>
> **What it costs.** Run the product at both widths. The largest keyword spotter, 140,000 parameters,
> is 136.72 KiB at INT8 and 68.36 KiB at INT4; the smallest, 77,000, is 75.20 and 37.60 KiB -- all
> computed from those parameter counts and the named bit widths. Divided by the 2,952 KiB of $C_\text{SRAM}$
> those are 4.63% and 2.32% for the largest variant, 2.55% and 1.27% for the smallest, derived from the
> same two numbers each time. The whole keyword-spotting family therefore lives at a few per cent of the
> fabric either way, and the keyword spotter's own source makes that claim about this architecture
> family -- it is the first source this section's table names. The 14-million Conformer is 13,672 KiB at INT8 and 6,836 KiB at INT4, computed
> the same way: 4.63 and 2.32 times the fabric's entire storage.
>
> **What it does not say.** Three things, in order of how much they will cost a reader. It does not say
> *fits*, because $C_\text{SRAM}$ is a gross population: the same design also needs its input buffer,
> its line buffers, its activations and a key-value cache that chapter 9 shows growing per block, so a
> model at 95% of the total does not fit. It does not say anything about speed, which is the argument
> below and the actual reason residency matters. And it does not say a vendor tool sizes its own memory
> the same way: the accelerator ladder at the end of this section is a measured footprint on a different
> board, and the fit of each rung against this device is arithmetic on those rows -- the
> table below lists where each one was measured.

[Figure 20](#fig-ch4-residency) puts all eight quantities on one axis, because the interesting thing is
not the per-centages -- it is that one bar crosses the fabric's line and the other six do not come
close to it.

::: {#fig-ch4-residency .figure}
```tikz
% Weight bytes against the fabric's whole on-chip storage, on two DIFFERENT value axes on
% purpose. Panel (a) is zoomed to 0..5 per cent so the three keyword-spotting variants can be
% read against each other; at that zoom the fabric (100 per cent) is off the top and is NOT
% drawn. Panel (b) is a 0..5-multiples-of-the-fabric axis where the container is the dashed
% line at 1x, so the Conformer bars are shown crossing it. Each bar height = value x that
% panel's own scale; the two scales are deliberately unequal so no drawn height means two
% things. Bar values are registered parameter counts x a stated bit width, over the 2,952 KiB
% the SRAM card registers. All reading of the picture lives in the caption, not on the plot.
\begin{tikzpicture}[
  font=\tiny,
  i4/.style={draw=black!78, fill=black!17},
  i8/.style={draw=black!78, fill=black!62},
  ttl/.style={font=\tiny\itshape, text=black!74, anchor=west},
  axl/.style={font=\tiny, text=black!62},
  tk/.style={font=\tiny, text=black!58, anchor=east},
  xl/.style={font=\tiny, text=black!66, anchor=north},
  val/.style={font=\tiny, text=black!72, anchor=south},
  leg/.style={font=\tiny, text=black!62, anchor=north west}]
% ---- panel (a): the keyword spotter, zoomed to 0..5 per cent of the whole fabric ----
\node[ttl] at (0,2.760) {(a) keyword spotter \textbullet{} per cent of the fabric};
\draw[black!9, thin] (0,0.420) -- (5.420,0.420);
\draw[black!9, thin] (0,0.840) -- (5.420,0.840);
\draw[black!9, thin] (0,1.260) -- (5.420,1.260);
\draw[black!9, thin] (0,1.680) -- (5.420,1.680);
\draw[black!9, thin] (0,2.100) -- (5.420,2.100);
\draw[black!45] (-0.035,0.000) -- (0.035,0.000);
\node[tk] at (-0.10,-0.045) {0};
\draw[black!45] (-0.035,0.420) -- (0.035,0.420);
\node[tk] at (-0.10,0.375) {1};
\draw[black!45] (-0.035,0.840) -- (0.035,0.840);
\node[tk] at (-0.10,0.795) {2};
\draw[black!45] (-0.035,1.260) -- (0.035,1.260);
\node[tk] at (-0.10,1.215) {3};
\draw[black!45] (-0.035,1.680) -- (0.035,1.680);
\node[tk] at (-0.10,1.635) {4};
\draw[black!45] (-0.035,2.100) -- (0.035,2.100);
\node[tk] at (-0.10,2.055) {5};
\draw[->, black!72] (0,0) -- (5.620,0);
\draw[->, black!72] (0,0) -- (0,2.220);
\node[rotate=90, axl] at (-0.62,1.050) {per cent of $C_\text{SRAM}$};
\draw[i4] (0.300,0) rectangle (0.850,0.533);
\draw[i8] (0.950,0) rectangle (1.500,1.071);
\node[val] at (0.575,0.533) {1.27};
\node[val] at (1.225,1.071) {2.55};
\node[xl] at (0.900,-0.030) {77K};
\draw[i4] (2.150,0) rectangle (2.700,0.647);
\draw[i8] (2.800,0) rectangle (3.350,1.294);
\node[val] at (2.425,0.647) {1.54};
\node[val] at (3.075,1.294) {3.08};
\node[xl] at (2.750,-0.030) {93K};
\draw[i4] (4.000,0) rectangle (4.550,0.974);
\draw[i8] (4.650,0) rectangle (5.200,1.945);
\node[val] at (4.275,0.974) {2.32};
\node[val] at (4.925,1.945) {4.63};
\node[xl] at (4.600,-0.030) {140K};
\node[leg] at (0,-0.420) {light = INT4\quad dark = INT8};
% ================= panel (b): multiples of the fabric, origin 7.3cm =================
\begin{scope}[shift={(7.300,0)}]
\node[ttl] at (0,2.760) {(b) the same six, plus a model \textbullet{} multiples of the fabric};
\draw[black!9, thin] (0,0.500) -- (3.520,0.500);
\draw[black!9, thin] (0,1.000) -- (3.520,1.000);
\draw[black!9, thin] (0,1.500) -- (3.520,1.500);
\draw[black!9, thin] (0,2.000) -- (3.520,2.000);
\draw[black!9, thin] (0,2.500) -- (3.520,2.500);
\draw[black!45] (-0.035,0.000) -- (0.035,0.000);
\node[tk] at (-0.10,-0.045) {0};
\draw[black!45] (-0.035,0.500) -- (0.035,0.500);
\node[tk] at (-0.10,0.455) {1};
\draw[black!45] (-0.035,1.000) -- (0.035,1.000);
\node[tk] at (-0.10,0.955) {2};
\draw[black!45] (-0.035,1.500) -- (0.035,1.500);
\node[tk] at (-0.10,1.455) {3};
\draw[black!45] (-0.035,2.000) -- (0.035,2.000);
\node[tk] at (-0.10,1.955) {4};
\draw[black!45] (-0.035,2.500) -- (0.035,2.500);
\node[tk] at (-0.10,2.455) {5};
\draw[->, black!72] (0,0) -- (3.720,0);
\draw[->, black!72] (0,0) -- (0,2.220);
\node[rotate=90, axl] at (-0.62,1.050) {$\times$ the whole fabric};
\draw[black!80, line width=0.9pt, densely dashed] (0,0.500) -- (3.550,0.500);
\node[anchor=south west, font=\tiny\itshape, text=black!72] at (0.05,0.520) {the fabric, $2{,}952$ KiB};
\draw[i4] (0.240,0) rectangle (0.500,0.010);
\draw[i4] (0.560,0) rectangle (0.820,0.013);
\draw[i4] (0.960,0) rectangle (1.220,0.010);
\draw[i4] (1.280,0) rectangle (1.540,0.015);
\draw[i4] (1.680,0) rectangle (1.940,0.012);
\draw[i4] (2.000,0) rectangle (2.260,0.023);
\draw[<->, black!55, thin] (0.240,-0.140) -- (2.260,-0.140);
\node[xl] at (1.250,-0.160) {six spotter bars};
\draw[i4] (2.700,0) rectangle (2.960,1.160);
\draw[i8] (3.020,0) rectangle (3.280,2.315);
\node[val] at (2.830,1.160) {$2.32\times$};
\node[val] at (3.150,2.315) {$4.63\times$};
\node[xl] at (2.990,-0.030) {about 14M parameters};
\end{scope}
\end{tikzpicture}
```
The same eight weight sets, read two ways. Panel (a) zooms to per cent so the three keyword-spotting variants can be compared: the widest, 140K at INT8, is 4.63 per cent of the fabric, and the axis stops at five per cent because nothing here needs to reach 100. Panel (b) switches the axis to multiples of the whole fabric, where the container itself is the dashed line at 1x: the six spotter bars collapse to hairlines at the base, while the Conformer's two bars stand 2.32 and 4.63 times above the line. The two panels share no scale -- that is the point -- so the spotter's fit and the Conformer's overflow are the same fact seen from the two ends of a range no single axis can hold.
:::

**Mechanism, second half: why capacity is not the argument.** A reader could conclude from the card
above that residency is a matter of space -- 3% used, room to spare. That conclusion is wrong, and the
arithmetic of the feed rate shows it. Take a design that instantiates all 1,248 slices at one product
each per cycle, run at the same assumed 300 MHz that chapter 3's ridge point uses -- a stated
assumption, not a measurement, and the table at this section's end says so. That datapath consumes
1,248 multiplicands and 1,248 multipliers per cycle. If the weights were not resident they would have
to arrive from off-chip, so the design would need 1,248 weight reads per cycle. At 300 million cycles
per second that is $1{,}248 \times 300$ million reads a second -- $3.744 \times 10^{11}$, the product of
one read per slice per cycle and cycles per second, which is the units the number is made of. A DRAM
controller does not serve single bytes on request. It serves a burst of tens of bytes
after a round trip, and the burst is useful only if consecutive words of the design's stream are
consecutive in memory. That is the real constraint on this board, and it is not a capacity constraint:

- **bytes per second are cheap.** Re-reading the largest keyword spotter's whole weight set once per
  frame at 100 frames per second is 14.00 MB/s at INT8, computed from 140,000 weights at one byte each
  and that frame rate. That is 0.073% of the 19.2 GB/s theoretical peak, derived from the bus width and the data rate named in this
  section's table. Even the 14-million Conformer's weight set, streamed once a frame, is 1,400 MB/s at INT8 --
  7.29% of the same peak. Both look survivable, and that is the trap.
- **requests per second are not.** A controller serves a burst, not a byte, so what matters is how many
  separate asks a design makes. The keyword spotter re-read at 100 frames a second needs $1.4 \times 10^{7}$
  single-byte reads a second -- computed as 140,000 weights times that frame rate -- which a wide enough
  burst could absorb. The full-array datapath above needs $3.744 \times 10^{11}$, because it wants 1,248 of
  them *in one cycle*. That is 26,743 times the first figure, derived by dividing the two, and the gap is
  the whole argument: the bytes are affordable at either rate and the request granularity is impossible at
  the high one.
- **and the peak is shared, not owned.** The datasheet places the controller on the processor side with
  no direct fabric pins, and the processors on the same module are running Linux. The datasheet's note on the
  19.2 GB/s row says that achievable bandwidth depends on port width, burst length and
  scheduling, so that peak is a ceiling a fabric design competes for rather than a pipe it holds.

Residency is the answer to a *request-rate* problem, and the tiles of section 4.2 are what solve it: 208
containers, each with its own ports, so a design can read many weights in the same cycle without asking
anybody. That is the sentence chapter 9's overlay rests on, and it is why this book's default is weights
resident and activations streamed -- the traffic split chapter 9's boundary section names.

**The residency budget is not the end of the fitting problem, and the vendor numbers prove it.** The
device supports the free standard edition of the build flow -- a fact named in the table
below -- so a reader can compile a resident design without a licence; what nobody can compile their way out of is a tile that does not
exist. The measured ladder in the accelerator's own product guide is the most useful evidence for exactly
that reason -- a real tool's real footprint, on a real board, at eight settings.
The whole memory ladder is short enough to print at once, and reading it is the fitting test:

| Rung | block RAM tiles | UltraRAM tiles | Where it comes from |
| --- | --- | --- | --- |
| B512 | 72 | 18 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B800 | 90 | 40 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B1024 | 104 | 26 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B1152 | 121 | 44 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B1600 | 126 | 56 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B2304 | 165 | 60 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B3136 | 208 | 64 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |
| B4096 | 255 | 68 | <!-- V-04-10, V-04-11 --> DPU product guide (PG338), the two ladder tables |

::: {#fig-ch4-dpu-ladder .figure}
```tikz
% The same eight rows as geometry, so the two facts the prose reads off the table become lines a
% reader checks with a ruler instead of re-deriving: the block RAM column crosses the device's 144
% between B1600 and B2304, and the UltraRAM column does not climb with the rung name at all (B800
% asks for 40 where the larger B1024 asks for 26). Tiles come from the guide's ladder tables (V-04-10, V-04-11);
% the ceilings are the device's own populations (V-01-05, V-01-07). Heights are value x 0.026 cm,
% computed by hand: this figure has no axis arithmetic to get wrong.
\begin{tikzpicture}[
  font=\tiny,
  bar/.style={inner sep=0pt, outer sep=0pt, anchor=south},
  bcol/.style={bar, draw=black!70, fill=black!30},
  ucol/.style={bar, draw=black!70, fill=white},
  ceil/.style={draw=black!60, densely dashed},
  tick/.style={text=black!70},
  lab/.style={text=black!62, align=center, anchor=north}]
  % ---- axes: baseline y=0; value axis in tiles, 0.026 cm per tile ----
  \draw[->,black!70] (-0.15,0) -- (11.15,0);
  \draw[->,black!70] (-0.15,0) -- (-0.15,6.95);
  \node[tick, above left] at (-0.15,6.95) {tiles};
  \foreach \v/\h in {0/0, 50/1.30, 100/2.60, 150/3.90, 200/5.20, 250/6.50}{
    \draw[black!40] (-0.15,\h) -- (0.02,\h);
    \node[tick, anchor=east] at (-0.22,\h) {\v};}
  % ---- the two device ceilings, drawn as the fit test itself ----
  \draw[ceil] (0,3.744) -- (10.9,3.744);
  \node[tick, anchor=south west] at (10.95,3.744) {144 block RAM};
  \draw[ceil] (0,1.664) -- (10.9,1.664);
  \node[tick, anchor=south west] at (10.95,1.664) {64 UltraRAM};
  % ---- eight rung groups; solid bar = block RAM, hollow bar = UltraRAM, both to one scale ----
  \foreach \cx/\b/\bpx/\u/\upx/\nm in {
      0.70/72/1.872/18/0.468/B512,  2.05/90/2.340/40/1.040/B800,
      3.40/104/2.704/26/0.676/B1024, 4.75/121/3.146/44/1.144/B1152,
      6.10/126/3.276/56/1.456/B1600, 7.45/165/4.290/60/1.560/B2304,
      8.80/208/5.408/64/1.664/B3136, 10.15/255/6.630/68/1.768/B4096}{
    \node[bcol, minimum width=0.50cm, minimum height=\bpx cm] at (\cx-0.29,0) {};
    \node[ucol, minimum width=0.50cm, minimum height=\upx cm] at (\cx+0.29,0) {};
    \node[tick, anchor=south] at (\cx-0.29,\bpx+0.03) {\b};
    \node[tick, anchor=south, fill=white, inner sep=1.2pt] at (\cx+0.29,\upx+0.03) {\u};
    \node[lab] at (\cx,-0.05) {\nm};}
  % ---- the three readings, marked where they happen, in the open space above the bars ----
  \draw[<->,black!72] (6.10,4.86) -- (7.45,4.86);
  \node[tick, align=center, anchor=south] at (6.78,4.92) {the crossing:\\last fit, first stall};
  % the connector passes over the tall B1024 bar, so it is drawn with a white halo to stay legible
  \draw[white, line width=1.7pt] (2.34,1.040) -- (3.69,0.676);
  \draw[<->,black!62] (2.34,1.040) -- (3.69,0.676);
  \node[tick, align=center, anchor=north] at (3.02,-0.55) {a dip: the taller rung\\asks for less storage};
  % ---- legend, top-left, inside the frame ----
  \node[bcol, minimum width=0.42cm, minimum height=0.14cm, anchor=west] at (0.25,6.75) {};
  \node[tick, anchor=west] at (0.78,6.75) {block RAM tiles};
  \node[ucol, minimum width=0.42cm, minimum height=0.14cm, anchor=west] at (3.05,6.75) {};
  \node[tick, anchor=west] at (3.58,6.75) {UltraRAM tiles};
  \draw[ceil] (5.9,6.75) -- (6.32,6.75);
  \node[tick, anchor=west] at (6.42,6.75) {this device's ceiling};
\end{tikzpicture}
```
The vendor ladder drawn as fit rather than as rows: every rung's two tile counts against this device's two storage ceilings, so the crossing, the non-monotonic dip that forbids interpolation, and the one rung that fills its ceiling exactly are shapes on the page instead of arithmetic to redo. The counts are the table's, unchanged; nothing in the drawing adds a measurement.
:::

Three readings of that table, all of them arithmetic against the device's own populations; [Figure 21](#fig-ch4-dpu-ladder)
draws the same rows as geometry, so the first and second of them can be checked with a ruler. The block RAM
column climbs with the rung name and crosses this device's 144 tiles between B1600 and B2304, so 126
tiles of 144 is the largest block RAM core that fits, derived as 87.5% of the fabric's shallow storage
for one accelerator and leaving 18 tiles for everything else a voice design needs. The UltraRAM column
does *not* climb with the name -- B800 asks for 40 tiles where the larger B1024 asks for 26 -- which is
why no rung may be interpolated and each must be read from the table. Against this device's 64 UltraRAM
tiles, B3136 fills 64 of 64 exactly and leaves nothing, which makes B2304 the practical ceiling; B4096 fits neither variant, 255 tiles against 144 or 68
against 64 -- and DSP is the one resource that does have headroom, 710 slices of the fabric's 1,248 (56.9%,
derived from those two). The rows were measured on another board with a stated option set, and the product guide leaves
which rung a shipped image loads onto unresolved. So the ladder demonstrates a shape rather
than supplying a budget: **the resource that runs out on a fabric is usually not the one a parameter count
predicts.** The keyword spotter's 140,000 weights are 4.63% of the storage and a rounding error in the
logic; an accelerator's choice of how to stage its own buffers is what consumes the device.

**Where the numbers come from.** The sources behind the residency arithmetic and the ladder, with the assumption named
separately.

| Source | What it says |
| --- | --- |
| <!-- V-05-01; Interspeech 2020 / arXiv:2004.08531 --> the keyword-spotting conference paper (Interspeech) | the three keyword-spotting parameter counts -- 77,000, 93,000, 140,000 -- and the source's own claim that a model this size fits in on-chip block RAM |
| <!-- V-05-16 --> the NeMo recipe config, the recommended-variants table's Small-model row | about 14 million parameters for the small Conformer, and that the count is rounded by its source |
| <!-- V-01-22 --> the summed tile capacities (DS890, DS891) carried along the unit chain | the 2,952 KiB that every share above is divided by, with the unit chain that makes the division meaningful |
| <!-- V-01-11 --> summed from the block counts (DS890) and the tile-size table (DS891) | the same quantity, twice read and each reading once defensible, of which the unit chain keeps one |
| <!-- V-01-14 --> Kria K26 SOM data sheet (DS987), the processing-system overview | the memory controller sits on the processor side and the fabric has no pins straight to the chips |
| <!-- V-01-13 --> derived from the memory line (DS987) with the Kria card's own note (DS986) | the 19.2 GB/s theoretical peak, derived from the bus width and rate, and the note that achievable bandwidth depends on port width, burst length and scheduling |
| <!-- V-01-12 --> Kria K26 SOM data sheet (DS987), the memory line in the overview | the datasheet's verbatim memory line behind that derivation |
| <!-- V-01-09 --> UltraScale data sheet (DS890), device-feature table, DSP row | 1,248 slices, the multiplier in the request-rate arithmetic |
| <!-- V-07-03 --> derived in chapter 7 from the DSP row (DS890) and the peak bandwidth (DS987) | the 300 MHz used above as a stated assumption, and the ridge point it feeds |
| <!-- V-04-10 --> DPU product guide (PG338), the first resource table | the block RAM ladder: 72, 104, 126, 165 and 255 tiles at the rungs printed above |
| <!-- V-04-11 --> DPU product guide (PG338), the second resource table | the UltraRAM ladder, and that its rungs cannot be interpolated |
| <!-- V-04-12 --> derived: the two ladder tables (PG338) held against this device's tile counts (DS890) | the derived fit: B1600 the largest block RAM core that fits, B2304 the practical UltraRAM ceiling |
| <!-- V-04-09 --> derived: the guide's footprint (PG338) held against this device's counts (DS890) | that B4096 fits neither variant on this device, read off the two rows above |
| <!-- V-04-13 --> no retrieved source | which rung a shipped image actually loads -- no datasheet in this chapter states it |
| <!-- V-04-01 --> Vivado user guide (UG973), the architecture-support table, no-licence row | the device is supported in the standard flow with no licence required |

> **Scope note, closing this chapter.** Everything a design pays with is now on the table: logic tables
> and registers for state, slices for arithmetic, tiles for storage, and a handshake that lets all four
> disagree about timing without losing data. What this chapter deliberately did not decide is *who does
> the placing* -- whether a hand-written register-transfer description, a high-level synthesis flow, or a
> vendor accelerator builds the datapath that spends these resources, which is chapter 5's question --
> and what the audio in front of the arithmetic costs in the same currency, which is chapter 6's.
