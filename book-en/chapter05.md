# Four Ways to Accelerate on an FPGA: DPU, HLS, FINN and RTL

> *Objective: Comprehensively evaluate and compare four hardware implementation methodologies for neural acceleration on FPGAs.*

---

## 5.1 The Four Hardware Implementation Paths

A model that trains on a workstation is a graph of multiply-accumulate operations, and the board this book builds around must execute that graph many times per second. The question this section answers is the one every FPGA project starts with: by what means does the software model become a running datapath? "Datapath" is the word for the chain of operations the data physically travels through, and an FPGA gives the designer an unusually wide choice of how that chain is built. The fabric of a field-programmable gate array is a sea of configurable logic, small memories and hardened arithmetic units that can be wired into almost any shape, and the vendor of this book's board, together with the open-source community, sells four distinct ways of turning a graph into that wiring. Section 5.4 will follow what happens to a model before any of them runs, and this section presents the four datapaths themselves, each with an intuition, a mechanism, and an application to this book's streaming voice task.

The four paths are the vendor's deep learning processor, high-level synthesis, the FINN toolchain, and register transfer level design, usually called the DPU, HLS, FINN, and RTL. They form a natural ordering from the most prebuilt to the least: the DPU is an engine the vendor has already drawn, HLS is a compiler that draws the hardware from your description of its behaviour, FINN is a toolchain that specialises a model into a small custom datapath, and RTL is the hardware drawn by hand. The ordering is one of control: how much of the eventual circuit the designer holds in their own hands. It is also one of productivity, the axis section 5.2 will price, and the four paths are best read as a spectrum rather than a menu, because a real design can sit on more than one of them at once. Whatever the path, the object every path must serve is the same: a single utterance arriving as a stream of short hops, each hop one one-hundredth of a second long (`V-05-31`), so the datapath must be ready to accept a new slice of audio at that rhythm without ever being caught unprepared. The comparison is deliberately static: this section fixes the board, the model and the workload, and varies only the path, because a comparison that changed two things at once would teach nothing. The question asked of each path is the same one — what does the datapath look like, and what did it cost to obtain?

[Figure 21](#fig-ch5-four-paths) draws that spectrum: from the most prebuilt on the left, where the vendor has made the decisions, to the most hand-drawn on the right, where the designer makes every one. The arrow under the row is the ordering axis, and each path's subtitle names what it actually is: an engine, a compiler, a toolchain, or the designer's own modules.

::: {#fig-ch5-four-paths .figure}
```tikz
% The four implementation paths as a spectrum: most prebuilt (left) to most
% hand-drawn (right), with the ordering axis drawn beneath the row. Purely
% geometric: no registered figure is printed, so the picture cannot age.
\begin{tikzpicture}[
  node distance=4mm,
  path/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
               text width=17mm, minimum height=13mm},
  axis/.style={-{Stealth[length=2mm]}, thick},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
]
\node[path] (dpu) {DPU\\vendor overlay};
\node[path, right=of dpu] (hls) {HLS\\C to schedule};
\node[path, right=of hls] (finn) {FINN\\XNOR arithmetic};
\node[path, right=of finn] (rtl) {RTL\\hand-written silicon};
\coordinate[left=6mm of dpu.west] (lo);
\coordinate[right=6mm of rtl.east] (hi);
\draw[axis] (lo) -- (hi);
\node[lbl, below=1mm of dpu.south] {the vendor's decisions};
\node[lbl, below=1mm of hls.south] {a compiler's schedule};
\node[lbl, below=1mm of finn.south] {a toolchain's arithmetic};
\node[lbl, below=1mm of rtl.south] {every decision yours};
\node[lbl, below=2mm of lo, yshift=-3mm] {most prebuilt};
\node[lbl, below=2mm of hi, yshift=-3mm] {most hand-drawn};
\end{tikzpicture}
```
The path's subtitle is the shape of its ownership: the DPU is an engine the vendor has already drawn, HLS is a compiler that draws the structure from C or C++, FINN is a toolchain that specialises the arithmetic to one bit, and RTL is the hardware drawn by hand. The axis says nothing about quality — it is an axis of control, and the sections that follow price each path's position on it.
:::

**The DPU path (the vendor overlay).**

**Intuition.** The deepest shortcut available is to buy the datapath ready-made. The board's vendor sells a soft core, a processor design that is synthesised into the fabric rather than etched into silicon, called the Zynq deep learning processing unit, or DPU (`V-04-03`). The DPU executes neural networks; the designer supplies the model, and the vendor supplies nearly everything else: the instruction set, the scheduler, the way convolution is unrolled, the way weights are buffered. The mental model is a specialised co-processor sitting beside the general-purpose processor of the chip. On the host side the designer writes an application in the ordinary way; on the accelerator side, a compiled model runs on the engine. Someone else has already made the thousands of design decisions that a custom datapath would have demanded, and the price of that is what the section will return to: the sketch is not free to redraw.

**Mechanism.** The DPU is a fixed-function but configurable engine. It is "soft" because it occupies programmable logic resources on the board, and it is configurable because the vendor ships it in a ladder of sizes, each a different footprint of the same core. The engine executes an instruction stream compiled from the graph of the model, and it does so with its own internal array of multipliers and its own hierarchy of on-chip memories feeding them. The fabric the DPU consumes is the same fabric a hand-written datapath would have used, and this board has a specific inventory of it: one hundred and forty-four Block RAM tiles (`V-01-05`), sixty-four UltraRAM tiles (`V-01-07`), one thousand two hundred and forty-eight hardened multiply-accumulate slices (`V-01-09`), and on-chip static memory measured in the tens of thousands of kilobits (`V-01-11`). The ladder's sizes are the interesting part, because each rung is registered with the exact number of tiles it consumes in each of the two memory families (`V-04-10`, `V-04-11`). The largest rung asks for two hundred and fifty-five Block RAM tiles and sixty-eight UltraRAM tiles, and the board holds neither enough of one nor enough of the other, so the flagship size does not fit this board at all (`V-04-09`). The largest rung that fits the Block RAM variant uses one hundred and twenty-six of the one hundred and forty-four tiles, and the largest that fits the UltraRAM variant uses sixty-four of sixty-four, exactly full, leaving nothing for the rest of the design (`V-04-12`). A vendor overlay is therefore not "any size you like": it is a ladder with a ceiling, and on this board the ceiling is reached in the middle of the range.

**Application.** For a streaming voice model the DPU offers a working neural core in days rather than months, and that is the argument that wins most practical projects. The model arrives as hops of one hundredth of a second (`V-05-31`), one utterance at a time, and the DPU processes a compiled graph that section 5.4's toolchain steps have already shrunk: the graph the DPU receives is not the model that trained, but the folded, quantised graph the deployment pipeline produces. On this board the utility of the DPU is bounded by exactly the two numbers above: the core must fit, and the fit comes in whole rungs. The design point is B1600 for the Block RAM variant, where the board still has eighteen tiles of slack, or B3136 for the UltraRAM variant, where the fit is exact. A team that needs the flagship rung is asking for a different board, and a team that needs the fabric for a custom front end may find the exactly-full UltraRAM fit leaves them nothing to work with; these are the DPU path's two cautionary notes, and section 5.2 counts them.

**The HLS path (C to schedule).**

**Intuition.** The second path takes the programmer's own language, C or C++, and compiles it into hardware. The word for this is high-level synthesis: the source code describes what the design does, and the tool decides how the hardware is arranged to do it. A designer who despairs of hand-drawing every wire still wants more than the vendor's fixed engine, and HLS sits between the two: the source is fully the designer's, the structure is generated. The mental model is the compiler's loop, not the engineer's schematic. Where RTL would ask "what does this stage look like", HLS asks "what does this stage do", and then produces the look. The trade is visible from the start: HLS is a compiler, and like every compiler it can only emit what its front end can express, so the cleverness of the datapath is capped by the cleverness of the tool that generates it.

**Mechanism.** The unit of design in HLS is the loop. The designer writes the signal-processing stages of the datapath as C functions with loops over samples, and the tool transforms those loops into hardware with three families of decisions. The first is pipelining: the tool overlaps the stages of a loop so that a new sample enters before the previous one has finished, governed by an initiation interval, the number of clock cycles between the starts of two consecutive iterations; an initiation interval of one means a new iteration begins every single cycle, which is the rhythm a streaming datapath wants. The second is array partitioning: a memory in the source becomes one or more memories in the hardware, and splitting it across banks is what allows several reads in the same cycle. The third is dataflow: the tool decides how the stages of the whole function communicate and whether they run concurrently. These are scheduling decisions, and they are the entire power of the path, because they are also its entire fragility: one loop-carried dependency, work that must wait for the previous iteration to finish, stalls the whole pipeline regardless of how the tool scheduled everything else. The generated hardware still uses the same fabric as the other paths — the tool maps multiplications onto the board's one thousand two hundred and forty-eight hardened slices (`V-01-09`) — but the resource plan is produced by the tool from the source, not fixed by a vendor or drawn by hand. It is, in essence, the RTL path with the drawing automated, and the automation is the whole difference.

**Application.** HLS wins where the datapath is a well-understood algorithm with regular loops: this book's front end, the filter chains and transforms that turn raw audio into features, is the canonical case. The mechanism above is exactly the vocabulary of chapter 6, where every stage is a loop over samples and the rhythm the loops must keep is the hop of one hundredth of a second (`V-05-31`). The tool's schedule is a re-runnable artefact: change a directive, re-run the synthesis, and a different datapath comes out, which is what makes HLS the cheapest of the four paths to iterate while the design is still being shaped. Where HLS is fragile is equally specific. A designer who wants a datapath whose structure is unusual, or whose latency must be guaranteed cycle by cycle, spends their time fighting the tool's schedule rather than writing the design, and bit-exactness, the property that the datapath reproduces a reference arithmetic exactly, is not the tool's default. The productivity price of the path is counted in section 5.2; the intuition to carry forward is that HLS is the path that capitalises on regular loops and pays for irregular ones.

**The FINN path (XNOR arithmetic).**

**Intuition.** The third path changes the arithmetic instead of the datapath. FINN is the open-source toolchain, developed for the board's vendor and now maintained as a community project, that takes a model trained for extreme low precision and generates a custom datapath for it (`V-06-03`). The essence is one bit: weights and activations are constrained to single-bit values, so a multiply becomes an equality check — an XNOR, the logical operation that is true when its two inputs agree — and a sum of products becomes a count of agreeing bits, a popcount. The intuition is that the hardware for a multiply is replaced by logic that can be implemented in a small sliver of the fabric, and the memory for a weight is replaced by a single flip-flop. FINN does not merely quantise a network; it rebuilds the model's arithmetic around the one-bit multiply, and the datapath it generates is specialised to the exact layer sizes of the network it was told about. The path is the extreme of the spectrum: the model becomes the datapath, and nothing generic remains.

**Mechanism.** The compiled design is a chain of matrix-vector-threshold units, one per layer. Each unit holds its layer's weights in on-chip memory, multiplies the incoming vector by them using one-bit arithmetic, and applies a threshold where an activation function would have been. Because the weights are one bit, their storage cost is the smallest possible: a weight is exactly one bit, and the book's target keyword model, the ninety-three thousand parameter variant (`V-05-01`), occupies, at one bit per weight, a set of ninety-three thousand bits. What that means on this board is worth computing. Ninety-three thousand bits divided by eight gives eleven thousand six hundred and twenty-five bytes, computed as the parameter count divided by the bits in a byte; divided again by one thousand and twenty-four per kibibyte the same set is about eleven point three five, a little over eleven kibibytes, and read in decimal kilobytes it is eleven point six, a shade under twelve. Both readings are tiny beside the board's on-chip static memory, which stands at twenty-three thousand six hundred and sixteen kilobits (`V-01-11`), so the entire weight set of the model sits on the chip with the overwhelming majority of that memory untouched. The weight stream never leaves the fabric, and an access that never leaves the fabric is the cheapest kind of access there is; the energy ladder of chapter 7 prices that difference, and the FINN path simply never pays the expensive step. The generated design is small in memory and regular in shape: every layer is the same kind of unit carrying different weights, and the compiler arranges those units into the streaming datapath that the model's own layer sizes dictate, so the hardware is a direct photograph of the network rather than a generic engine running it.

**Application.** The FA — the accuracy of the model — is the tolerance of the FINN path, not an afterthought. One bit per value is an approximation, and the path is right for tasks whose accuracy survives it, of which keyword spotting, the recognition of a small set of spoken words, is the textbook example (`V-06-03`). The same mechanism explains what the path cannot do. The fold that section 5.4 describes, the deletion of a trained normalisation stage by folding its per-channel scale into the weights, has nowhere to land on this path: a per-channel product needs room inside the weight, and a one-bit weight has no room. The softmax argument of chapter 7 also runs in reverse. Chapter 7 needs an integer exponential because its quantised path must reproduce a softmax; on the FINN path there is no low-bit exponential to begin with, because the arithmetic is a threshold, and a threshold needs no transcendental. The FINN path is therefore not a general tool but a specialisation: it is the strongest on storage and traffic, and the narrowest in what a network may do, and both halves of that sentence follow from the same one bit.

**The RTL path (fully owned silicon).**

**Intuition.** The fourth path is the one the other three automate: register transfer level design, the hardware drawn by hand. At RTL the designer describes the datapath one register at a time, in a hardware description language, and every decision is theirs: the width of every bus, the depth of every pipeline, the protocol by which stages hand data to one another, the state machine that sequences the whole. Where the DPU path is someone else's engine and the HLS path is a compiler's schedule, the RTL path is the designer's own silicon, laid out at the level of hardware. The intuition is complete ownership, and the price of complete ownership is that nothing runs for you. A working audio front end plus a small neural core is dozens of modules, and each module is a decision made and a design written; section 5.2 counts that price.

**Mechanism.** The mechanism is the discipline of the register transfer level itself. The datapath is described as combinational logic between registers: each clock edge captures new values into registers, and in the time between edges the combinational logic computes what those values will be. Multiplications become banks of the board's hardened slices (`V-01-09`), memories become the board's Block RAM and UltraRAM tiles, and the scope of the design is bounded by exactly the inventory section 5.1's DPU discussion already listed: one hundred and forty-four Block RAM tiles, sixty-four UltraRAM tiles, one thousand two hundred and forty-eight multiply-accumulate slices (`V-01-05`, `V-01-07`, `V-01-09`). What the designer writes is bit-exactness itself: the rounding rule for every fixed-point stage, the rule for values that fall exactly halfway between two representable values, are written into the design as ordinary logic, so a reference arithmetic is reproduced in silicon as a consequence of the module, not as a contract fought for against a compiler. The RTL path is the only one of the four where the sizing of every stage is a single author's decision: the datapath consumes exactly the resources its arithmetic needs, no more, and the board's ceiling of one hundred and forty-four Block RAM tiles or sixty-four UltraRAM tiles is met by the design the author actually wrote rather than by a vendor's ladder.

**Application.** The RTL path is where this book's two most exacting requirements meet. The first is bit-exactness: a fixed-point datapath that reproduces a reference exactly, which section 5.4 and chapter 7 treat as the goal a deployment must hit, and which at RTL is the default rather than a property to negotiate. The second is the sharing of one datapath between the front end and the model, which the FINN and DPU paths cannot easily offer: a hand-written datapath can compute the mel features in one stage and feed them directly into the arithmetic of the network in the next, with no interface between them. The cost is the productivity price already counted and counted again: the RTL path takes the longest to first working hardware of the four, and it applies the caution of section 5.4's note — this book describes the datapath and sizes nothing of the encoder's arithmetic, because no registered figure exists for it. For the streaming shape of this book the payoff is the most direct of the four: a datapath whose pipeline depth is written by hand can guarantee the rhythm of the hop by construction, where the other paths must hope their compiled schedules hold it. The RTL path is the reference the other three are measured against: it is what a datapath looks like when nobody automated it, and every other path is an attempt to buy back its price.

Four paths, then, and a spectrum to place them on. The DPU is the most prebuilt: the engine is the vendor's, the fit is a ladder of rungs, and the largest rung this board can hold is B1600 for the Block RAM variant, one hundred and twenty-six of one hundred and forty-four tiles, or B3136 for the UltraRAM variant, sixty-four of sixty-four, exactly full (`V-04-12`, `V-04-10`, `V-04-11`). HLS is the compiler's path, as productive as the DPU for a fresh design whose loops are regular and fragile where the schedule closes. FINN specialises the arithmetic to one bit and, with it, the ninety-three thousand parameter model down to about eleven kibibytes of storage on a board whose on-chip memory is measured in thousands of times that (`V-05-01`, `V-01-11`). RTL owns the silicon outright and charges the full price in design work. Section 5.2 takes the four paths and prices them on the axes the DPU and RTL entries have already hinted at — productivity, flexibility, latency, and the efficient use of the board's scarce resources. The spectrum also explains the hybrid designs the rest of the book assembles: a project can run the neural core on the DPU while a hand-written stage feeds it features, or let FINN own the keyword spotter while HLS builds the front end, and section 5.3 and section 5.5 turn that possibility into a rule and an exercise.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-31` | the hop period of one one-hundredth of a second every path must serve |
| `V-04-03` | the DPU, the vendor's soft processing unit this part of the book deploys |
| `V-04-09` | the verdict that the flagship rung fits neither memory variant |
| `V-04-10` | the DPU Block RAM ladder, each rung's tile count |
| `V-04-11` | the DPU UltraRAM ladder, each rung's tile count |
| `V-04-12` | the largest rungs that fit: B1600 at 126 of 144 Block RAM tiles; B3136 at 64 of 64 UltraRAM tiles, exactly full |
| `V-01-05` | the board's one hundred and forty-four Block RAM tiles |
| `V-01-07` | the board's sixty-four UltraRAM tiles |
| `V-01-09` | the board's one thousand two hundred and forty-eight hardened multiply-accumulate slices |
| `V-01-11` | the board's on-chip static memory of 23,616 kilobits |
| `V-05-01` | the ninety-three thousand parameter variant of the keyword model |
| `V-06-03` | the FINN toolchain's scope: one-bit arithmetic, keyword spotting among its targets |

---

## 5.2 Trade-off Analysis: Productivity, Flexibility, Latency, and Resource Efficiency

Section 5.1 named four hardware implementation paths — the DPU, high-level synthesis, the FINN toolchain and register transfer level design — and section 5.4 will examine what the compiler does to a model before any of them runs it. This section sits between them and answers the question a design team actually faces: which path should carry this book's workload, a streaming single-speaker recognition model that must answer one short hop of audio at a time. The honest answer is that there is no outright winner. Each path trades four things against the others: how much engineering work stands between the model and a running design (productivity), how much of the design stays free to change after the path is chosen (flexibility), how quickly a result arrives (latency), and how well the board's scarce resources are spent (resource efficiency). A trade-off means exactly that: taking more of one good thing is what makes you give up another. This section prices the four paths on those four axes, draws a comparison table, and then turns to the roofline, the tool that shows which axis really governs this workload. The count of the RTL path's productivity price that section 5.4 promises is kept here, axis by axis.

**Productivity.** Productivity is the number of engineering decisions that stand between the model and a running design. The unit of account is the decision, not the line of code: a decision is a choice that fixes part of the design, and a path is productive to the degree that something else — a compiler, a generator, a vendor — makes those decisions for you.

The DPU path is the most productive of the four, together with high-level synthesis. A compiled graph runs on the vendor's engine, an already-built datapath; the datapath is the chain of operations the data travels through. Your work is to make the toolchain decisions of section 5.4, choose the engine size that fits the board, and run the compiler, which turns the graph into the integer instruction stream the engine executes. Nobody draws the hardware, because the hardware already exists as silicon on the board; one configuration and one compiler run deliver a design that would take months by hand. The price of that productivity — an engine whose size is fixed whether the graph is large or small — is what the resource efficiency axis charges.

High-level synthesis, usually called HLS, is equally productive on a fresh design, but it borrows the productivity from a different place. HLS is a compiler that turns C or C++ source into the hardware description of a datapath. You write the behaviour — the loops and the arithmetic — and add directives, which are instructions to the tool about how to arrange the work, and the tool generates the structure. The word "generate" is the point: the tool absorbs the structural decisions the way the DPU compiler does, and it can re-run as often as you like. The difference from the DPU is that the decisions are yours to write rather than yours to pick from a vendor's menu, so the path is as fast as the DPU only when the source is worth writing.

The FINN path sits in the middle. FINN is a working toolchain: it takes a model, rebuilds it around one-bit arithmetic, and produces a design for the fabric. But it asks for a different model, not just a different compiler pass. The network must survive at one bit per weight and one bit per activation, and the accuracy must tolerate that; a team that arrives with a full-precision network is not running a tool, it is re-deciding the model. That extra decision is what separates the middle of this axis from the top.

The register transfer level path, RTL for short, is the least productive of the four, and by a wide margin. This is the count section 5.4 promises. At register transfer level you describe the hardware itself: every register, every gate. Every decision is a module. Each stage of the datapath is a module you write; the width of every bus is a choice you make; the handshake that passes data between stages is a protocol you design; the rounding tie rule of a fixed-point stage is a behaviour you implement; the state machine that sequences the work is a design you own. Where the DPU path delivers with a configuration choice and a compiler run, the RTL path charges one decision per module, and a working audio front end plus a small neural core is dozens of modules. Nothing runs for you. That is the productivity price section 5.4 points to, and this axis is where it is paid.

**Flexibility.** Flexibility is how much of the design space stays open after a path is chosen. A path that can express any datapath is flexible; a path that can only express what its vendor or its data types allow is narrow, and the narrowness decides, in advance, which future changes are cheap and which are impossible.

RTL is the most flexible of the four, because it is total. The fabric of the board is unopinionated: it is a sea of logic, memory and arithmetic units that can be wired into any shape the designer can describe. On RTL there is no operator the path does not know, because the designer simply writes it, so every future change is a question of effort rather than of permission.

HLS is partially flexible. The designer controls the schedule, which is the order and timing of the operations: how deeply the pipeline overlaps one step with the next, how the memories are split so that several reads happen in the same cycle, whether a loop stays serial or unrolls. What the designer does not control is the structure — the tool decides which multiplier units exist, which buffers are built, how the datapath is shaped. Schedule, not structure: that is the whole flexibility of the HLS path, and it is why a change that only re-times the work is easy while a change in the shape of the datapath means rewriting the source.

FINN is narrow, because the whole arithmetic lives in a one-bit world. Weights and activations are single bits, and a multiply becomes an equality check followed by a count of true results. Any operation that cannot be expressed at one bit has no home on this path. Section 5.4 showed the fold — the deletion of a trained normalisation stage — has nowhere to land here, because a fold bakes a per-channel product into the weights, and a one-bit weight has no room for a product. The narrowness is the price of the path's efficiency, and the next axis prices the efficiency.

The DPU is the narrowest of the four, because the vendor's instruction set architecture decides what a graph may contain. An instruction set architecture, or ISA, is the fixed menu of operations an engine can perform; every compiled graph is a program written in that menu. An ingredient the menu does not know — a new operator, an exotic shape of tensor, a fusion the compiler does not implement — cannot be deployed on the core. It must be rewritten into operations the ISA knows, approximated, or handed to the host processor beside the fabric. What the path cannot do is extend: the ISA is decided by the vendor, and the design bends to it, never the other way.

**Latency.** Latency is the delay between the moment a slice of audio enters a design and the moment its answer leaves it. The streaming shape sets the budget, so this axis is simple to price. The book's target model steps forward one hop at a time, a hop being one slice of audio one hundredth of a second long (`V-05-31`), and it must always be ready for the next hop because the microphone never waits. Any path whose per-hop delay is a large share of that budget fails the workload; any path well inside it has latency to spare, and the argument moves elsewhere.

All four paths, on this workload, sit in the sub-millisecond regime, meaning below one thousandth of a second — the book estimates this, because the per-hop work is small and none of the four paths must reach off the board to do it. Each path reaches the regime through a different mechanism, and the mechanism decides how predictable the latency is. On the DPU the compiled graph executes on the engine's fixed schedule, and the book estimates the delay is a small fraction of the hop budget, the same from hop to hop because the schedule is the same. On HLS the delay belongs to the generated schedule: one loop-carried dependency, which is work that must wait for the previous iteration to finish, can stretch the whole pipeline, so the book estimates a sub-millisecond result only when the pipeline opens; the risk is structural, not arithmetic. On the FINN path the model is small enough to live on the chip, so nothing waits on an off-chip fetch, and the book estimates sub-millisecond latency; the axis that actually limits FINN is accuracy tolerance, not delay. On RTL latency is a design variable: the pipeline depth the designer writes fixes the delay, the book estimates the designer can reach well below one thousandth of a second, and the estimate is exact because the designer wrote every stage of it. The comparison table below records the profiles in words. The shape of the axis is the interesting part: the workload is easy on latency — every path beats the one hundredth of a second it is given — and hard on everything else, which is why the rest of this section is not about speed.

**Resource efficiency.** Resource efficiency is how well the board's scarce resources are spent: the on-chip memory where weights live, the arithmetic units where operations happen, and above all the traffic between the two. The energy ladder explains why traffic is the resource that matters. An access to an off-chip memory costs about two hundred times the energy of an arithmetic operation, an access to a buffer on the chip about six times, and an access to a register about twice (`V-07-06`). Energy is not the only bill — delay is a second bill — but the ladder is the reason an efficient design is measured in bytes moved, not in gates used: the cheapest arithmetic in the world is wasted if every operand drags two hundred times its cost in from outside.

The DPU path spends resources in ladder steps, because the engine comes in fixed sizes. The vendor publishes a resource ladder of eight depths, each depth a different footprint of the same core, and it offers the ladder in two memory families: one that fills block RAM, one that fills ultra-wide memory, UltraRAM (`V-04-10`, `V-04-11`). The board holds one hundred and forty-four block RAM tiles (`V-01-05`) and sixty-four UltraRAM tiles (`V-01-07`). The largest depth in the block RAM family wants two hundred and fifty-five tiles, and the largest in the UltraRAM family wants sixty-eight, so the top of the ladder does not fit this board at all. What fits is the block RAM depth that uses one hundred and twenty-six of the one hundred and forty-four tiles, or the UltraRAM depth that uses sixty-four of sixty-four — exactly full, leaving no tile spare (`V-04-12`). That sparelessness is the efficiency story: the DPU prices its memory in whole rungs, so even a graph that needs a fraction of a rung rents the whole rung, and the chip has no slack left for anything else.

The FINN path spends the least possible on weights. Its weights are one bit wide, and the book's target keyword model carries ninety-three thousand parameters (`V-05-01`), which at one bit per weight is small enough to live entirely on the chip: the weight set never leaves the fabric, so the path never pays the off-chip step of the energy ladder. One bit is the smallest footprint a weight can have, which makes this path the ceiling of efficiency on storage and traffic.

The RTL path spends resources exactly where the arithmetic demands them, because the designer sets every width. Chapter 7 argues that a stage should be exactly as wide as its arithmetic needs, no more, because every extra bit is hardware that must be switched and stored with every sample, and because the rounding tie rule — how a value exactly halfway between two representable values is decided — fixes where the safe minimum lies. On the RTL path that width is written into the module, so bit-exact reproduction of a reference is the default rather than a contract to fight for.

Put the three together and the axis has a hierarchy: FINN spends almost nothing, the DPU spends a whole fixed rung, RTL spends the measured minimum and pays for it in the productivity counted above, and every path's score improves the less it reaches off the chip. That last sentence is the whole argument the roofline makes rigorous.

**The comparison table.** The four axes, priced side by side. The rows are the four paths; the columns are the axes. Cells carry words, and registered numbers sit beside the records that carry them; no cell prints a figure this section has not registered.

| Path | Productivity | Flexibility | Latency profile | Resource fit | Bit-exactness |
| --- | --- | --- | --- | --- | --- |
| DPU | highest — a configuration and a compiler run deliver the deployed object | narrowest — the vendor's instruction set decides what a graph may contain | the book estimates sub-millisecond, well inside the 0.01 s hop (`V-05-31`) | B1600 fits (126 of 144 block RAM) or B3136 exactly full (64 of 64 UltraRAM) (`V-04-12`, `V-04-10`, `V-04-11`, `V-01-05`, `V-01-07`) | integer arithmetic fixed by the instruction set; the requantization constants of the toolchain are the accuracy contract |
| HLS | highest — C/C++ source and directives generate the datapath | partial — the schedule is yours, the structure is the tool's | schedule-dependent; the book estimates sub-millisecond, well inside the 0.01 s hop (`V-05-31`), when the pipeline opens | the tool maps memories and multipliers; the fit follows the schedule directives, not a fixed footprint | ties and rounding follow the tool's built-in rules unless the design re-specifies them |
| FINN | middle — a working toolchain that demands a model rebuilt for one-bit arithmetic | narrow — every operation must live at one bit | the book estimates sub-millisecond, well inside the 0.01 s hop (`V-05-31`); nothing waits off chip | 93K parameters at one bit per weight stay entirely on the chip (`V-05-01`) | the arithmetic is exact; the one-bit approximation is the model's own choice |
| RTL | lowest — every decision is a module | total — any datapath the fabric can hold | a design variable; the book estimates sub-millisecond, well inside the 0.01 s hop (`V-05-31`), fixed by the pipeline the designer writes | exactly the width each stage needs, so a bit wider is a bit wasted | the default — the tie rule of chapter 7 is written into the module |

**The roofline.** The resource efficiency axis ends in a tool that explains why this workload is decided by bytes. A roofline is a picture of a machine drawn as a roof: the ridge point is the arithmetic intensity, measured in operations per byte — how many arithmetic operations each byte of memory traffic pays for — at which the machine's ability to compute and its ability to fetch data run with exactly equal effort. A design below the ridge is memory-bound: it waits for bytes, and its arithmetic units stand idle while the memory catches up. A design above the ridge is compute-bound: it has memory to spare and waits on its own operations. Where the ridge sits is a property of the machine, and the two machines this book compares sit far apart. The Kria KV260 sits between thirty-nine and seventy-eight operations per byte (`V-07-03`), and the Jetson Orin NX sits at about four hundred and ninety (`V-07-02`). The ridge points, as digits beside the records:

| Platform | Ridge point | Record |
| --- | --- | --- |
| Kria KV260 | 39.0–78.0 operations per byte | `V-07-03` |
| Jetson Orin NX | about 490.2 operations per byte | `V-07-02` |

[Figure 22](#fig-ch5-roofline) puts those two ridge points on the roof they belong to: the rising line is the memory ceiling, where the sustainable rate grows with arithmetic intensity until the machine's ability to fetch bytes is spent, and the flat line is the compute ceiling, where adding intensity cannot add rate. The ridge point is where the two meet, and the two positions marked on the intensity axis are the digits the table above carries.

::: {#fig-ch5-roofline .figure}
```tikz
% The roofline concept: a memory ceiling rising with intensity, a compute ceiling
% flat in intensity, and the ridge where they cross. Two registered ridge points
% mark where the book's machines sit on the intensity axis. The axes are linear
% and schematic, not measured: this picture teaches the shape, and chapter 3's
% ridge-point comparison draws the machines' roofs to scale.
\begin{tikzpicture}[
  scale=1,
  line/.style={thick},
  ceil/.style={thick},
  mem/.style={thick},
  ridge/.style={-{Stealth[length=2mm]}, thick},
  lbl/.style={font=\scriptsize, inner sep=2pt},
  dot/.style={circle, inner sep=1.2pt, fill},
  axis/.style={-{Stealth[length=2mm]}},
]
% Axes.
\draw[axis] (0,0) -- (10.6,0) node[lbl, below right] {arithmetic intensity, ops/byte};
\draw[axis] (0,0) -- (0,5.6) node[lbl, above, rotate=90] {sustainable rate};
% The roof: memory ceiling rising, compute ceiling flat.
\draw[mem] (0,0) -- (6.2,4.6) node[lbl, above, pos=0.62] {memory-bound: waits for bytes};
\draw[ceil] (6.2,4.6) -- (10.6,4.6) node[lbl, above, pos=0.5] {compute-bound: waits on operations};
% The ridge: what the rising and flat lines have in common.
\fill[black] (6.2,4.6) circle (1.4pt);
\draw[ridge] (6.2,4.6) -- (6.2,0) node[lbl, below, align=center] {ridge point\\the machine's crossover};
% The two registered ridge points of the book, on the intensity axis.
\draw[dotted, thick] (3.4,4.6) -- (3.4,0);
\fill[black] (3.4,0) circle (1.2pt);
\node[lbl, below=1mm] at (3.4,0) {KV260: 39 to 78};
\draw[dotted, thick] (8.6,4.6) -- (8.6,0);
\fill[black] (8.6,0) circle (1.2pt);
\node[lbl, below=1mm] at (8.6,0) {Orin NX: about 490};
\end{tikzpicture}
```
The two marked points are placed on the intensity axis only; their height on the rate axis is deliberately left unplotted, because this book registers the ridge positions, not the machines' peak rates on one shared scale — that comparison belongs to chapter 3. What the picture fixes is the geometry of the roof: the crossover below the ridge is a memory problem, the crossover above it is an arithmetic problem, and a machine with a low ridge spends most of the axis in the memory-bound regime.
:::

The FPGA side of this book lives or dies on bytes moved. Its ridge is low because the board's main memory, a fast kind of dynamic random-access memory called DDR4, delivers nineteen point two gigabytes per second (`V-01-13`) — respectable for a board like this, but modest next to what the arithmetic units could consume if they were kept full. Below the ridge, a design that reaches into that memory for every weight is the design that idles. The three paths of the comparison table are, in effect, three answers to that one threat: the DPU keeps its weights in the fixed rung, FINN keeps its one-bit weights on the chip entirely, and RTL lets the designer decide which bytes are worth moving. The encoder's own weight stream, delivered in hops of one hundredth of a second (`V-05-31`), is far under what the board's nineteen point two gigabytes per second can carry in one hop (`V-01-13`): the bytes the model needs are not the problem, and never were. The problem is only whether the design makes the memory work for bytes it could have kept on the chip.

The GPU side of the comparison suffers the opposite shape. Chapter 3 argues that the Orin NX reaches its advertised intensity only when a machine processes many independent items at once, filling its parallel lanes; a single utterance streams nowhere near enough work to do that. In the batch-one streaming shape this book studies, the Orin sits far below its ridge, paying for an enormous memory and huge arithmetic units that stand mostly idle. So the two machines are mirrors: the GPU is over-provisioned for this workload and cannot fill itself, while the FPGA is under-provisioned and that is exactly right, because a streaming datapath wants a machine that matches the stream instead of one that needs a fleet of streams to justify itself. That asymmetry is what section 5.3 turns into a choice rule.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-31` | the hop period, 0.01 s, the latency budget every path must beat |
| `V-04-10` | the DPU block RAM ladder, eight depths, the largest needing 255 tiles |
| `V-04-11` | the DPU UltraRAM ladder, eight depths, the largest needing 68 tiles |
| `V-04-12` | the largest rungs that fit the board: B1600 at 126 of 144 block RAM; B3136 at 64 of 64 UltraRAM, exactly full |
| `V-01-05` | the board's 144 block RAM tiles, the ceiling of the block RAM ladder |
| `V-01-07` | the board's 64 UltraRAM tiles, the ceiling of the UltraRAM ladder |
| `V-05-01` | the 93K-parameter keyword model, which at one bit per weight stays entirely on the chip |
| `V-07-06` | the energy ladder: an off-chip access about 200 times an arithmetic operation, a chip buffer about 6 times, a register about 2 times |
| `V-07-03` | the KV260 ridge point, 39.0–78.0 operations per byte |
| `V-07-02` | the Orin NX ridge point, about 490.2 operations per byte |
| `V-01-13` | the board's DDR4 bandwidth, 19.2 GB/s, the ceiling the encoder's weight stream stays far under |

---

## 5.3 Selecting the Optimal Architecture for Edge Voice Workloads

Section 5.1 presented four ways to accelerate a neural model on the programmable logic, and section 5.2 priced them against one another on productivity, flexibility, latency and resource efficiency. This section turns that comparison into a choice. The choice cannot be made in the abstract: a design team chooses an architecture for a workload, and the workload of this book is a very specific one. So the first task is to state that workload precisely from the book's own geometry — the numbers the book registers for the audio, the frames, the transform and the filter bank. With the workload fixed by registered figures, each path of section 5.1 wins under a different condition, and the rules at the end of this section name those conditions one at a time.

The audio arrives as a single utterance at a time — one spoken command, or one unbroken stretch of speech — and it is sampled at sixteen kilohertz (`V-05-10`), the rate at which the other corpus in the book's benchmark set also stores its recordings (`V-05-11`). Sixteen kilohertz means the microphone produces sixteen thousand samples every second. The front end never waits for a whole utterance to finish before it starts: streaming means the hardware consumes the audio as a continuous flow and emits results as it goes, hop by hop, exactly as the book's target model behaves in section 5.1. The front end of chapter 6 cuts that flow into short blocks called frames, the windows of audio it transforms at one step. One frame is four hundred samples (`V-06-15`), and four hundred samples at sixteen kilohertz lasts twenty-five milliseconds, computed as 400 over 16000 seconds. The analysis window does not start each frame from scratch. Between one frame and the next it slides forward by a shorter distance, called a hop — the step the window takes along the stream — so consecutive frames overlap and no sample is lost between them. One hop is one hundred and sixty samples (`V-06-16`), which lasts ten milliseconds, computed as 160 over 16000 seconds: the same ten milliseconds the model's own configuration registers as its window stride, point zero one seconds (`V-05-31`). That ten-millisecond hop is the heartbeat of the entire design. New audio arrives every hop, whether the hardware is ready or not, so every stage must be able to absorb one hundred and sixty new samples within the ten milliseconds before the next hop begins. The frame, being twenty-five milliseconds long while the hop is ten, is the same shape the stream always presents: a moving window that overlaps itself, one hundred and sixty samples gained at each step.

Inside each frame the front end does two fixed pieces of work. It first runs a fast Fourier transform, the standard algorithm that turns a block of samples into its spectrum of frequencies, and for this workload the transform is five hundred and twelve points (`V-06-14`). The size is not an accident: five hundred and twelve is the smallest power of two that a four hundred sample frame reaches, the remaining one hundred and twelve slots of the transform being padded with zeros (`V-06-17`). The spectrum is then folded into eighty mel bands (`V-05-35`), the ranges of frequency that the filter bank groups together to imitate how human hearing judges pitch, and a logarithm compresses the band energies so that quiet sounds and loud ones are compared on the same scale. The result every hop is the same shaped object: eighty numbers that describe the last twenty-five milliseconds of audio, ready for the model. Nothing in that description varies from hop to hop or from utterance to utterance — the transform size is fixed, the band count is fixed, the arithmetic is the same every ten milliseconds. That regularity is the first fact the choice rules build on.

**The hybrid thesis.** The design this book describes is a hybrid: three different owners, each taking the part of the workload that suits it. The signal front end of chapter 6 — the windowing, the transform, the mel filter bank and the logarithm — lives on the programmable logic, where a fixed, regular pipeline of registers and arithmetic units is exactly the kind of computation the fabric is built for. The neural core — the part that turns the eighty mel values into a label or a stream of text — is one of the four paths of section 5.1, and the rules below pick which one. The host SoC, the general-purpose processor that sits beside the fabric on the same chip, keeps the streaming context — the state the model must remember across hops. The hybrid thesis is that this division of labour costs less than any single-owner design: the regular part goes to the machine that excels at regular work, the model part goes to the path whose owner the designer actually chooses, and the bookkeeping goes to a processor whose job is bookkeeping.

[Figure 23](#fig-ch5-hybrid) draws that division of labour as the three owners and the object that crosses between them: the fabric front end feeds the chosen neural core eighty mel values every hop, and the host SoC keeps the streaming context off that line, because the context is state, not datapath.

::: {#fig-ch5-hybrid .figure}
```tikz
% The three-owner hybrid: fabric front end feeds one chosen core over the mel
% object, and the host SoC keeps the streaming context. The hop rhythm belongs
% only to the fabric-to-core boundary; the context loop is drawn off the line.
\begin{tikzpicture}[
  node distance=7mm,
  owner/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
                text width=20mm, minimum height=12mm},
  part/.style={draw, align=center, inner sep=3pt, font=\scriptsize,
               text width=16mm, minimum height=10mm},
  lbl/.style={font=\scriptsize, align=center, inner sep=1pt},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
  ctx/.style={-{Stealth[length=1.8mm]}, thick, dashed},
]
\node[owner] (host) {host SoC\\streaming context\\state, not datapath};
\node[owner, below=14mm of host] (fe) {fabric front end\\windowing, transform,\\mel filter bank};
\node[owner, right=14mm of fe] (core) {neural core\\one of the four paths\\of section 5.1};
\node[part, below right=4mm and 6mm of fe] (mic) {microphone};
\draw[arr] (mic) -- (fe.south west);
\node[lbl, below=0mm of core.south] {the chosen owner};
\draw[arr] (fe.east) -- (core.west) node[lbl, midway, above] {eighty mel values, each hop};
\draw[ctx] (core.north) -- (host.south) node[lbl, midway, right] {context in, context out};
\draw[ctx] (host.west) -- (fe.north);
\node[lbl, right=1mm of mic.east, yshift=-7mm] {audio, hop by hop};
\end{tikzpicture}
```
The boundary between the fabric front end and the core is where the ten-millisecond rhythm lives: eighty values must cross it every hop. The host SoC's loop is drawn dashed because it is not part of that rhythm — the context changes once per hop, but the state is a set of pointers and a cache, and the hardware that carries it does not sit on the microphone's critical path.
:::

Why the front end belongs on the fabric: it is the most regular arithmetic in the whole chain. Every hop runs the same operations on the same shapes — a window of four hundred samples, a transform of five hundred and twelve points, eighty bands — and none of that depends on which model family is listening at the other end. A programmable logic fabric is a machine of exactly this kind: a pipeline that consumes one continuous sample stream and emits a fixed-width vector, in time with a clock the designer fixes. Placing the front end there also removes it from the model decision entirely. Section 5.2 priced the four paths for a neural core; none of that pricing applies to the front end, because the front end is not what any of the four paths would be chosen for. One datapath, fixed once, never revisited.

Why the neural core is a path of section 5.1: the model is the opposite of regular. Its layers differ from one another, its arithmetic is the subject of the whole accuracy argument of this book, and how it is built decides how much engineering stands between the checkpoint and a running design. The four paths of section 5.1 are four different owners for that core — the vendor's overlay, a synthesis compiler, a one-bit toolchain, or the designer's own hand-written modules — and the rules below choose between them on the conditions each path demands.

Why the host SoC keeps the context: streaming recognition needs state that is not a datapath. A model that has already heard four hundred milliseconds of an utterance must know what it said so far when the next hop arrives; that memory is the streaming context, and it must survive from hop to hop for as long as the utterance lasts. The registered reading of a streaming context in this book's evidence set comes from WeNet, a streaming speech toolkit whose own configuration processes speech in chunks: WeNet builds its context from a chunk of sixteen feature frames, and at forty milliseconds per feature frame that chunk spans six hundred and forty milliseconds of audio (`V-05-05`). It is worth being exact about which model that number describes: it is WeNet's configuration, not this book's model. The book's own streaming Conformer is a different model whose context this book does not register, so the six hundred and forty milliseconds stands here as an example of what a streaming context is and roughly how large such a span can be, not as a figure about the book's neural core. The important property for the hybrid thesis is structural: however long the context is, it changes rarely and cheaply — a counter, a cache, a set of pointers that grow as the utterance does. That is state, not datapath. The host SoC is the natural home for state, and the fabric the natural home for the pipeline; the two exchange a small fixed object each hop, the eighty mel values going one way and the updated context coming back.

**Decision rules.** Four rules, one per path of section 5.1. Each rule names the condition under which its path is the right owner of the neural core; when more than one condition holds at once, the tighter one wins — a date schedules out RTL, an accuracy budget schedules out one-bit arithmetic, and a bit-exactness contract schedules out everything except RTL.

**Choose the DPU when time-to-market rules.** The DPU is the vendor overlay: an engine the vendor has already designed and placed on the fabric, into which a design loads a program rather than building hardware. On this path the model arrives as a compiled graph — the artefact of section 5.4 — the integer instruction stream that the toolchain produces after its folding and calibration passes. A compiled graph runs on the core the design chooses, and the choice is constrained by the board. This board's fabric holds a fixed number of memory tiles in two families: block RAM, the standard on-chip memory blocks of the fabric, and UltraRAM, a deeper and wider family that holds more bits per tile. The core depths that fit are exactly two: B1600 on block RAM, and B3136 on UltraRAM — the latter consuming every one of the board's UltraRAM tiles, exactly full, as the record registers it (`V-04-12`). The depth is the price. The overlay comes in whole rungs, so the chosen rung is reserved whether the graph needs it all or not, and an exactly full core leaves the design no spare memory for anything else on that family. What the designer buys with that price is time: the hardware already exists, the accuracy contract is the toolchain's to keep, and the engineering that remains is a configuration and a compile. When the date on the wall is the binding constraint, that is the path.

**Choose FINN when the task tolerates one bit.** The FINN toolchain rebuilds a network around one-bit arithmetic: weights and activations are single bits, so a multiply becomes an equality test followed by a count of the bits that match, and the arithmetic that remains is exact within that one-bit world. The approximation is the model's own decision to live at one bit, taken before deployment, and the price of the path is whatever accuracy that decision costs. The rule therefore has two conditions. The first is tolerance: the task must keep working when every number in the model is a single bit. Keyword spotting — deciding which of a small set of spoken commands was said, or whether one was said at all — is such a task, and it is the task this book's small model is trained for. The second condition is fit: the whole model must live on the chip, because a one-bit network that reached off the fabric for its weights every hop would hand back exactly the efficiency the path exists to buy. The book's keyword model carries ninety-three thousand parameters (`V-05-01`), and a parameter set that small fits on the fabric at one bit per weight, so the weight stream never leaves the chip between hops. When both conditions hold — the accuracy survives at one bit and the model fits in the fabric — FINN is the most efficient owner the core can have.

**Choose RTL when bit-exactness or the chapter 7 softmax path owns the design.** Bit-exactness is the property that the hardware reproduces a reference computation exactly, bit for bit, on every input; on the register transfer level it is the default, because the designer writes every stage, every width and every rounding decision. Chapter 7 works through the accuracy argument in detail, and section 7.5 examines the softmax — the stage that turns the model's raw scores into probabilities that sum to one — as a fixed-point path of its own. A very narrow exponential on that path is a component no compiled overlay offers ready-made, and when the model's accuracy rests on reproducing its behaviour exactly, the design must be able to write it into existence; only the register transfer level can hold a module the vendor's instruction set never anticipated. The second trigger is the shared datapath. A datapath is the chain of operations the data travels through, and when the front end of chapter 6 and the neural core must run through one and the same chain — the mel values flowing straight into the model's first arithmetic stage, with no memory interface and no boss between the two owners — the register transfer level is the only path on which one datapath is actually one. The cost of both is the productivity price section 5.2 counted: every decision is a module, and every module is written by hand.

**Choose HLS for the middle.** High-level synthesis, HLS for short, is a compiler that turns behaviour written in C or C++ into a hardware description of the datapath, and the schedule is its design lever. The schedule is the order and timing of the operations: how deeply the pipeline overlaps one step with the next, how the memories are split so that several reads happen in the same cycle, how a loop stays serial or unrolls. Choose HLS when neither extreme binds. The datapath needs to be programmable — the front end and the core still share the fabric, and the designer still wants the compiler's productivity — but bit-exactness is not the contract, and the schedule risk is manageable: the loops are simple enough that the generated pipeline stays open, and no single loop-carried dependency, work that must wait for the previous iteration to finish, stretches the whole chain. That is the middle position the first four sections describe: more control than the overlay, less than hand-written registers; productivity counted next to the DPU's in section 5.2, flexibility that is schedule rather than structure. When the model is too small or too recent to justify hand-written modules, and too demanding for the vendor's menu, HLS is the owner.

**What this chapter does not decide.** This chapter decides which of the four paths owns the neural core. It does not decide the board itself. The board that runs this workload is built in the chapters that follow: chapter 8 works the quantization arithmetic that the choice of core must honour and the acceptance metric the design must meet, and chapter 9 assembles the streaming datapath around the front end and the chosen core. Section 8.4 gates acceptance on the task's own metric — a design passes when it meets the measure its task is judged by, not when it satisfies a resource ledger or a schedule diary. The rule of this section is therefore a pointer rather than a verdict: it says which path the model's datapath belongs to, and it deliberately leaves the board, the clock and the pass-or-fail line to the chapters whose subject they are.

**Traceability.** The records this section's argument rests on.

| Record | What it establishes here |
| --- | --- |
| `V-05-10` | the audio sample rate, 16 kHz, the first element of the workload's geometry |
| `V-05-11` | the same 16 kHz rate from the book's other corpus, corroborating the clock the front end runs on |
| `V-06-15` | the 400-sample frame, twenty-five milliseconds of audio at sixteen kilohertz |
| `V-06-16` | the 160-sample hop, ten milliseconds of audio at sixteen kilohertz |
| `V-05-31` | the registered hop period, 0.01 s, which the computed 160-over-16000 hop matches |
| `V-06-14` | the 512-point FFT of the front end, the transform size the config registers |
| `V-06-17` | the 512-point FFT as the smallest power of two that contains the four-hundred-sample frame |
| `V-05-35` | the 80 mel bands the filter bank produces every hop |
| `V-05-05` | WeNet's streaming context, 640 ms from a chunk of 16 feature frames at 40 ms per frame, attributed to WeNet and not to the book's own model |
| `V-04-12` | the core depths that fit the board: B1600 on block RAM, B3136 on UltraRAM at 64 of 64 tiles, exactly full |
| `V-05-01` | the 93K-parameter keyword model, small enough to fit on the fabric at one bit per weight |

---

## 5.4 What the Toolchain Decides Before the Hardware Sees the Model

**Intuition.** A signal chain is not the diagram it was drawn on. A preamplifier has a gain dial and
the mixer channel behind it has a gain dial too, and an engineer who needs more level usually turns
whichever dial is closer and then stops thinking about there having been two. Nothing in the sound tells
those two cases apart, because two constant gains in a row are one gain. What does change is how many
stages the signal actually passes through. A stage absorbed into its neighbour is not gone: the setting
still exists, now stored inside the other box, and somebody has to remember what it was folded with.

A network compiled for one of the four paths in section 5.1 behaves the same way, and one of its stages
folds more completely than a gain dial does. Batch normalisation (a scale and a shift applied per
channel, using numbers collected while the model was trained) sits after a convolution in most
recognition networks. At inference those two numbers per channel never change, so the stage is a
multiply and an add with nothing computed at run time. A convolution ends in a sum of products, and a
constant multiply and add applied to every output of it can be pushed backwards into the sums that
produce them. The compiler does the multiplication once, when it builds the model, and takes the stage
out of the graph. It does not make the stage faster. It deletes it (`V-06-06`).

Two consequences are what this section exists to teach. The first is that the model a piece of hardware
runs is not the model a framework prints, and the difference is not cosmetic: different stages exist.
The second is that the folded numbers, and the integer formats around them, come from measurements the
tools took earlier. So a stage count, a bandwidth budget or a latency written against the wrong graph is
not a small error of bookkeeping. It describes a model nobody deploys.

**Mechanism.** Three properties of the folding pass decide when a reader may rely on it.

The pass has to see the pair. A convolution and a normalisation written one inside the other are not
visible as a pattern to anything that walks a model one module at a time, and the framework gives no easy
way to reach its computational graph at all. Compilation answers that by capturing the graph, which is
what makes pattern-based rewrites possible across the whole model, including operations nested inside
container modules or wrapped in custom ones (`V-06-07`). A rewrite is therefore a property of a compiled
object. Printing a module list from the training framework cannot show you whether the pattern was ever
there for a matcher to find.

The pass has to be allowed to run. Folding is valid only in inference mode, the setting in which a model
answers rather than learns, while the pattern matcher behind it works in training and inference alike
(`V-06-08`). The shipped implementation says so twice over: it asserts that both modules are in that mode,
and it refuses a normalisation whose stored running statistics have not been computed yet (`V-06-09`).
Read the two together and folding belongs to the same family as calibration. Both consume a measurement
that had to be taken first, and neither can be applied to a model that is still deciding its own numbers.

The pass rewrites a weight, not an operator. What `V-06-09` shows is a multiply of the convolution's
whole weight tensor by a per-channel factor built from the normalisation's stored scale and inverse
standard deviation, with the bias taking the remainder. No new operator is required and none is removed
(`V-06-06`), so no accelerator has to be built for the folded form and no run-time stage is left to
schedule. Why the other kind of normalisation cannot be folded this way is section 9.2's subject. What
matters in this chapter is narrower: whether the pattern exists at all is decided by a line in a config
file, before any compiler is involved.

**Which graphs offer the fold is a field, not a family property.** Three published readings of this
book's target model disagree about it.

| Reading of the target model | What its convolution module normalises with | A compiler can delete that stage | Records |
| --- | --- | --- | --- |
| Conformer-Transducer Large, offline | `batch_norm` | the pattern is present | `V-05-20` |
| Streaming Conformer Large, cache-aware | `layer_norm` | there is nothing to fold | `V-05-26` |
| Streaming FastConformer Large, cache-aware | `layer_norm` | there is nothing to fold | `V-05-41` |

Two configurations that a paper would describe with the same three words hand the compiler different
graphs, and only one of them can lose a stage. That is why "the model" is a weaker description of a
design input than "the config", and why this book names a config file whenever it names a shape.

**Calibration is a choice among estimators, and the tool refuses some choices.** Quantization maps real
values onto integers, and chapter 8 works through the arithmetic of that mapping. The part that matters
here is where the map's scale comes from. It is not printed anywhere in a checkpoint. The vendor's
quantizer documents five different methods for calibrating a scale, four rounding behaviours and four
statistics for settling on one scale when separate batches of sample data disagree (`V-06-10`). Those
lists are not independent of one another. Four of the five scale estimators cannot be combined with the
modal statistic, and two of them cannot be used at all with an asymmetric range; the tool stops with an
error rather than picking something for you (`V-06-11`). And the layer names a reader would use to give
one layer a different configuration do not exist until calibration has finished, because the instruction
is to read them out of the file that run emits (`V-06-12`).

> **Traceability note.** What the records in this section establish is behaviour, not size. `V-06-06` to
> `V-06-09` come from one framework's tutorial and the module it documents, pinned to a release tag, and
> they say that a rewrite happens, when it is permitted, and what it multiplies. `V-06-10` to `V-06-12`
> are the documented option surface of the vendor quantizer that produces the DPU's integer graphs: what
> can be asked, what is refused, what does not exist yet. `V-05-20`, `V-05-26` and `V-05-41` register a
> type name read out of a config file. No record in this set measures anything, so this section names a
> stage that may or may not survive compilation and prints no figure for what its removal saves.

**Hardware application.** Take the four paths of section 5.1 one at a time, because folding is not the
same kind of event on each of them.

On the DPU path the deployed object is a compiled integer graph, instantiated by a named core
configuration (`V-04-03`) rather than by a framework module list. Folding changes the stage inventory
that graph is compiled from, and the requantization constant chapter 8 attaches to each stage boundary is
computed from the scales of the stages that surround it (`V-06-02`), so a boundary that no longer exists
has no constant, no rounding and no slot in the schedule. There is a second effect, and it is the larger
one on this hardware. A per-channel affine still reads every value it scales and writes every value it
produces, so deleting the stage removes one full pass over an activation tensor. That is traffic rather
than arithmetic, which is why a folded model can speed up on a machine whose multiply units were never
the limit.

On the FINN path the fold is not offered. Its weights are one bit wide and its activations one bit wide,
with the arithmetic performed as comparisons and popcounts instead of multiplies (`V-06-03`), so there is
nowhere for the per-channel product of `V-06-09` to be baked into. What that flow does with a
normalisation instead is not in this book's evidence set, and this chapter records the difference rather
than filling it in.

On the register transfer level (RTL) path the fold is the designer's decision, not a pass. Nothing runs
for you: whether a normalisation survives as its own stage, disappears into the neighbour's shift and
rounding, or is computed at all, is a choice written into a module, and it is visible in the source
instead of in a compiler log. That is the productivity price of the path, and section 5.2 counts it.

Three habits follow, and they are the reason this section sits in a chapter about choosing an
architecture rather than in a chapter about tools.

- Count stages in the artefact the compiler emitted, whose own file lists the names the tool will accept
  (`V-06-12`), and not in the module list the training framework prints.
- Report an accuracy or a latency together with the calibration configuration that produced it, since the
  option surface refuses some configurations outright (`V-06-11`) and separates others by an estimator
  choice alone (`V-06-10`).
- Read a published multiply-accumulate or byte figure as a claim about whichever graph its authors
  compiled. No such figure is registered for the encoder this book targets, in either direction
  (`V-05-57`), which is why the sections before this one describe a datapath and size nothing.

The measurement claim in one sentence: a stage count taken before these passes ran is not a slightly
wrong count of the deployed model, because the deployed model does not contain the stages it counts.

---

## 5.5 Exercises: four problems that tie the paths to the board

Section 5.1 named the four hardware paths, and section 5.2 counted what each of them costs. This
section sets the comparisons on the board's own numbers. Four problems follow, each worked from
first step to last so a reader can follow every division. They ladder upward. The first
sizes the very first buffer in the signal chain, the one that catches the microphone. The second
reads the vendor processor's ladder of core sizes against the board's memory. The third folds a
binarised array down to a count of cycles. The fourth assembles the whole chain, microphone to
streaming context, into one latency budget. Every arithmetic step sits either inside the mathematics
or on a line marked "computed as", so nothing is asserted that the reader cannot check.

A few terms are worth fixing once. A hop is the interval between the starts of two consecutive
frames, so a hop shorter than a frame means the frames overlap. A bank is one independently addressed
block of storage inside a memory, with its own access path. A processing element is one small
arithmetic unit inside an array of them, and the array's depth is how many a single pass can feed. A
ring buffer is storage whose address wraps from its end to its start, so new data overwrites the
oldest and nothing is copied. A popcount is the count of bits set to one in a word, and a kibibyte is
one thousand and twenty-four bytes, the unit that appears beside a decimal kilobyte of one thousand.
The constants are this book's registered target geometry: sixteen kilohertz audio (`V-05-10`), a
four-hundred-sample frame (`V-06-15`), a one-hundred-and-sixty-sample hop (`V-06-16`), a
five-hundred-and-twelve-point transform (`V-06-14`), a hop period of one one-hundredth of a second
(`V-05-31`), and the board's own fabric counts (`V-01-05`, `V-01-07`, `V-01-09`, `V-01-11`).

> **Exercise (laddered) -- initiating a frame: memory banking for the front end.**
> A microphone delivers audio at sixteen kilohertz (`V-05-10`). The front end cuts that stream into
> frames of four hundred samples (`V-06-15`), transforms each frame with a five-hundred-and-twelve-point
> fast Fourier transform (`V-06-14`), and then advances by a hop of one hundred and sixty samples
> (`V-06-16`), so that consecutive frames share part of their length. (a) How many milliseconds long
> is one frame, and how many is one hop, computed as the sample count divided by the sample rate?
> (b) The processing loop wants to read two samples every clock cycle out of one memory. With a
> single bank, why can it miss that rhythm when the two accesses land in the same bank, and how many
> banks let two reads happen every cycle, computed as the quotient of the samples in flight by the
> ports per bank? (c) What does the overlap between consecutive frames demand of the buffer, in words?
>
> **Answers.**
> (a) The frame is $400 / 16000 = 0.025$ seconds, that is twenty-five milliseconds, computed as the
> sample count divided by the sample rate. The hop is $160 / 16000 = 0.01$ seconds, that is ten
> milliseconds, computed the same way from the same rate. The transform is longer than the hop, which
> is the point of the overlap: a new frame begins while the previous one is still being finished.
> (b) A memory of one bank holds a single array of cells behind a single read port, and one port can
> decode one address in a cycle. When the loop's two wanted samples live in that one bank, both
> requests reach the same port at once and only one is served; the other waits a cycle, and the
> rhythm that should deliver two samples delivers one. Splitting the storage across banks gives each
> its own port, so two requests in different banks proceed together. The number of banks is the samples
> in flight divided by the ports per bank, computed as $2 / 1 = 2$ banks. Two banks are enough because
> two reads are wanted per cycle and each bank serves one; a wider loop needs a wider split.
> (c) The frame is four hundred samples long and the next frame starts only one hundred and sixty
> samples later, so consecutive frames share their middle: the overlap is $400 - 160 = 240$ samples,
> computed as the frame length minus the hop. The buffer therefore has to hold a whole frame at once
> rather than a hop's worth, and it may not throw a sample away the moment its first frame has read
> it, because the next frame still needs that sample. A ring buffer of at least a frame's length
> provides exactly this: the shared tail of one frame is simply the head of the next.
> The consequence is that the front end's memory is a datapath decision, not a framework setting. The
> HLS and RTL paths of section 5.1 let a designer choose the bank count and port width that carry the
> rhythm; a compiled processor overlay fixes its own memories and leaves the front end to meet
> whatever rhythm the board provides.

> **Exercise (laddered) -- the DPU depth that fits.**
> The keyword model the board runs carries ninety-three thousand parameters (`V-05-01`). The board
> itself carries one hundred and forty-four Block RAM tiles (`V-01-05`), sixty-four UltraRAM tiles
> (`V-01-07`), and one thousand two hundred and forty-eight digital signal processing slices
> (`V-01-09`). A tile here is one indivisible memory block in the fabric, and a digital signal
> processing slice is one hardened multiply-and-accumulate unit. The vendor's deep learning processor
> is sold in eight core sizes, named B512 up to B4096, and each size is registered with the number of
> memory tiles it consumes in each of the two memory variants (`V-04-10`, `V-04-11`). (a) Which sizes
> fit the Block RAM variant, and which fit the UltraRAM variant, comparing each size's tile count
> against the board's, one row per size? (b) Why does the largest size, B4096, fit neither variant?
> (c) How many B1600 cores fit the Block RAM variant, computed as the board's tiles divided by the
> core's tiles, rounded down?
>
> **Answers.**
> (a) Both ladders are registered rung by rung (`V-04-10`, `V-04-11`). Reading each rung against the
> board's two totals gives the table below; each row is a computed line.
>
> | Core size | Block RAM tiles (`V-04-10`) | Fits the $144$ tiles (`V-01-05`)? | UltraRAM tiles (`V-04-11`) | Fits the $64$ tiles (`V-01-07`)? |
> | --- | --- | --- | --- | --- |
> | B512 | $72$ | yes, $72 \le 144$ | $18$ | yes, $18 \le 64$ |
> | B800 | $90$ | yes, $90 \le 144$ | $40$ | yes, $40 \le 64$ |
> | B1024 | $104$ | yes, $104 \le 144$ | $26$ | yes, $26 \le 64$ |
> | B1152 | $121$ | yes, $121 \le 144$ | $44$ | yes, $44 \le 64$ |
> | B1600 | $126$ | yes, $126 \le 144$ | $56$ | yes, $56 \le 64$ |
> | B2304 | $165$ | no, $165 > 144$ | $60$ | yes, $60 \le 64$ |
> | B3136 | $208$ | no, $208 > 144$ | $64$ | yes, $64 \le 64$ |
> | B4096 | $255$ | no, $255 > 144$ | $68$ | no, $68 > 64$ |
>
> So five of the eight sizes fit the Block RAM variant, and seven fit the UltraRAM variant. The
> ladders do not agree on which size is largest, and the UltraRAM footprints are not monotonic in the
> size name, so a rung can fail in one variant while sitting comfortably in the other. Each rung must
> be read from its own row.
> (b) The largest size fails both variants for the same reason, at two different scales. In the Block
> RAM variant it asks for $255$ tiles against the board's $144$, and in the UltraRAM variant it asks
> for $68$ against $64$, computed as each core's tile count compared with the available count. Both
> comparisons exceed, so neither variant holds it, and the registry's own verdict for the size is No
> (`V-04-09`). What is *not* the obstacle is the arithmetic: the same size needs $710$ of the board's
> $1{,}248$ slices, computed as the quotient $710 / 1248 \approx 0.57$, a little over half, so the
> multiply-and-accumulate units have room to spare (`V-04-09`, `V-01-09`). The flagship rung of the
> vendor's ladder is therefore not a design this board can hold, and what it runs out of is memory,
> not multipliers. That is a memory-bound failure in the vendor's most capable rung.
> (c) The largest size that fits the Block RAM variant is B1600, at $126$ of the board's $144$ tiles
> (`V-04-12`). How many such cores fit? Computed as the board's tiles divided by the core's tiles,
> rounded down: $144 / 126 = 1.14$, so one core. Two cores would need $126 \times 2 = 252$ tiles
> against the board's $144$, which does not fit, and that matches the registered reading: B1600 is the
> largest Block RAM configuration that fits, one core (`V-04-12`). The UltraRAM variant reads the same
> way: its largest fitting rung, B3136, consumes all sixty-four UltraRAM tiles, leaving nothing for
> the rest of the design (`V-04-12`).
> The consequence is the chapter's caution about a vendor path's flexibility. The processor path is
> sold as a choice of depths, but the choice is a ladder with a ceiling, and on this board the ceiling
> is reached in the middle: every rung above B1600 in the Block RAM variant spends more tiles than the
> device owns, so it is resource efficiency, counted among the axes of section 5.2, that ends the
> ladder rather than productivity. A team that wants the flagship rung is asking for a different board.

> **Exercise (laddered) -- folding the FINN array.**
> Recall from section 5.1 that the FINN path works in one bit: its weights are single-bit values, so
> a multiply becomes a comparison and a sum of products becomes a count of agreeing bits. The engine
> that consumes those weights is a matrix-vector-threshold unit, a rectangular array of processing
> elements that each accumulate a popcount. Write the array as P elements deep and Q elements wide.
> It computes a K-by-N matrix product in $\lceil K/P \rceil$ passes down the rows times
> $\lceil N/Q \rceil$ passes across the columns, so the whole product takes
> $\lceil K/P \rceil \times \lceil N/Q \rceil$ passes. With numbers: the weight set is ninety-three
> thousand parameters (`V-05-01`). (a) How many bytes does the single-bit weight set occupy, computed
> as the parameter count divided by eight, then by 1024 per kibibyte? (b) What share of the board's
> 23,616 kilobits of on-chip memory is that, computed as the quotient (`V-01-11`)? (c) If the array
> is eight by eight, how many cycles does one pass over the full weight matrix take, computed as the
> quotient of the parameters by the array depth, rounded up?
>
> **Answers.**
> (a) Counting one bit per weight, the set is $93000 / 8 = 11625$ bytes, computed as the parameter
> count divided by eight, since eight bits make one byte. In binary kilobytes the same set is
> $11625 / 1024 \approx 11.35$, about eleven kibibytes, computed as the byte count divided by $1024$
> per kibibyte; read in decimal kilobytes it is $11625 / 1000 \approx 11.6$, about twelve kilobytes.
> The two readings differ only in which thousand is meant, the same unit collision this book's memory
> figures carry, so it is worth naming rather than hiding. Either way the set is tiny, and that is
> what makes the on-chip argument work at all.
> (b) The board's on-chip memory is 23,616 kilobits (`V-01-11`), the sum of its Block RAM and its
> UltraRAM. The share the weight set takes is $93000 / 23616000 \approx 0.0039$, computed as the
> quotient of the model's bits by the board's bits, so about four tenths of one percent. The weight
> set does not merely fit; it leaves essentially the whole fabric for activations, intermediates and
> the front end's buffers. That, in one number, is the FINN path's central claim: at one bit per
> weight, storage stops being this board's constraint.
> (c) An array eight by eight holds $8 \times 8 = 64$ processing elements, one per weight in flight,
> computed as the product of the two sides of the array. One pass over the full weight matrix
> therefore consumes sixty-four weights each cycle, so the pass takes
> $\lceil 93000 / 64 \rceil = \lceil 1453.125 \rceil = 1454$ cycles, computed as the quotient of the
> parameters by the array depth, rounded up. The count follows the formula directly: a deeper array
> scans the same weights in fewer cycles, because each cycle retires more of them, and its price is
> the silicon those extra processing elements occupy.
> The consequence is the trade the chapter counts in section 5.2. The FINN path buys a weight set that
> occupies a small fraction of one percent of the on-chip memory and a full scan in about fifteen
> hundred cycles, and it pays for both with a one-bit world, in which every value is a single bit and
> the model's accuracy has to survive a comparison count rather than a multiply. It is the clearest
> case in the chapter of a path whose resource profile is excellent and whose flexibility is exactly
> as narrow as its word width.

> **Exercise (laddered) -- the hybrid latency budget.**
> Assemble the whole chain from the microphone outward. Audio arrives at sixteen kilohertz (`V-05-10`).
> The front end forms frames of four hundred samples, a frame length of twenty-five milliseconds
> (`V-06-15`), and advances by a hop of one hundred and sixty samples, ten milliseconds (`V-06-16`),
> which is the registered hop period of one one-hundredth of a second (`V-05-31`). The streaming
> context is the WeNet configuration of sixteen feature frames at forty milliseconds each, which is
> six hundred and forty milliseconds (`V-05-05`); the context is the history an encoder attends
> across, the stretch of past audio it keeps in view while it decides the current output. (a) On the
> timeline, when does the next hop's processing begin relative to the frame, in words and on computed
> lines? (b) The front end spends the five-hundred-and-twelve-point transform and the mel windowing,
> where mel windowing is the step that folds the spectrum onto a perceptual frequency scale before
> the model sees it, and the inference on the accelerator is sub-millisecond, which the book
> estimates rather than registers; what slack remains in the ten-millisecond hop budget? (c) Where
> does the streaming context sit in this timeline, and why is its clock different from the hop clock?
>
> **Answers.**
> (a) Frame zero is the first four hundred samples, and the next frame begins at sample $160$,
> computed as the hop, so it covers samples $160$ to $559$. The next hop's processing therefore begins
> one hop after the current one, computed as the hop divided by the sample rate: $160 / 16000 = 0.01$
> seconds, that is ten milliseconds. The startup delay is a frame long, not a hop long: the first
> frame cannot be transformed until its last sample has arrived, computed as $400 / 16000 = 0.025$
> seconds, that is twenty-five milliseconds. After that first frame the chain settles into a steady
> state and emits one finished frame every ten milliseconds, so the rhythm the rest of the chain must
> meet is the hop, while the one-time wait at the start is the frame. The two answer different
> questions: the frame says how much the front end must hold, and the hop says how often it must
> deliver.
> (b) The hop budget is ten milliseconds. What the chain spends in a hop is the front end's work, the
> transform and the mel windowing, plus the accelerator's inference, which the book estimates at under
> one millisecond. The slack is the budget minus that work, computed as
> $10 - (t_{\text{fe}} + t_{\text{dpu}})$ milliseconds, where $t_{\text{fe}}$ is the front end's time
> and $t_{\text{dpu}}$ is the inference. The book registers no figure for the front end, so the
> subtraction stops at that formula: it says the front end must fit inside the hop with at least the
> inference's fraction of a millisecond left over, and it says nothing about how much of the hop the
> transform actually claims. What matters is the sign, not the size: the budget is met only if the
> front end is faster than the hop, and the sub-millisecond inference is far too small to decide that.
> (c) The streaming context is not a stage in this per-hop pipeline at all; it is the history the
> encoder reads across many hops. It spans $640 / 10 = 64$ hops, computed as the context divided by
> the hop period, so its clock is the hop clock counted sixty-four times over rather than a second,
> independent rate. That is why the context and the hop are not rivals: every hop adds one feature
> frame to the window, and the window's length is measured in hops, not in milliseconds of its own.
> The context therefore sits on the host side, off the ten-millisecond critical path, where it can
> grow to hundreds of milliseconds without slowing the front end or the accelerator.
> The consequence is the arrangement this chapter argues for, compressed into one timeline. The
> microphone sets a hard ten-millisecond rhythm that only the front end must meet, the model's own
> inference is a small fraction of a hop, and the long context lives off the critical path on the
> host. That split is what makes the four paths of section 5.1 a choice about the front end and the
> model rather than the whole system, and why a design can pick one path for the core and leave the
> streaming context to the processor beside it.

**Traceability.** The four exercises above are arithmetic on this book's registered target geometry. The
table lists each record this section cites and what it establishes here.

| Record | What it establishes here |
| --- | --- |
| `V-05-10` | the sixteen-kilohertz sample rate both frame times are computed from |
| `V-06-14` | the five-hundred-and-twelve-point transform the front end runs |
| `V-06-15` | the four-hundred-sample frame, the frame length of the first and fourth exercises |
| `V-06-16` | the one-hundred-and-sixty-sample hop, the advance of the first and fourth exercises |
| `V-05-31` | the registered hop period of one one-hundredth of a second the hop length is checked against |
| `V-05-01` | the ninety-three-thousand-parameter model the processor and FINN exercises size |
| `V-01-05` | the one hundred and forty-four Block RAM tiles the core ladder is read against |
| `V-01-07` | the sixty-four UltraRAM tiles the core ladder is read against |
| `V-01-09` | the one thousand two hundred and forty-eight digital signal processing slices |
| `V-01-11` | the 23,616 kilobits of on-chip memory the one-bit weight set is weighed against |
| `V-04-09` | the verdict that the largest core fits neither memory variant |
| `V-04-10` | the Block RAM footprint of each core rung |
| `V-04-11` | the UltraRAM footprint of each core rung |
| `V-04-12` | the largest fitting core of each variant, B1600 and B3136 |
| `V-05-05` | the WeNet streaming context of six hundred and forty milliseconds |
