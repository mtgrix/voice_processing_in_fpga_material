# A Streaming Conformer Overlay and the Left-Context Ring Buffer

> **Scope note (Issue #53, superseding the note left by Issue #29).** The spine of this chapter is the
> streaming Conformer overlay and its left-context K/V ring buffer, so the sections run: what the
> target is and what about it is still open, one block as a datapath, attention inside a chunk, the
> ring buffer itself, the fabric boundary it sits behind, and what look-ahead buys. Two stubs are not
> kept, and neither is quietly dropped. The software-stack question, which overlay toolchain and which
> runtime drive the fabric, has no registered source in this repository, so it waits for a board run
> instead of being answered with a product name. System power and thermal behaviour belongs to
> chapter 10, where energy per frame is one of the metrics the benchmark reports. `book/TOC.md` holds
> both readings, and this note is the record that the move was made on purpose.

> *Objective: Put a streaming Conformer encoder into an overlay and keep its past: the block as a
> datapath, chunked attention with a relative position scheme, the ring buffer that holds left context
> without growing, the boundary between the processor and the fabric, and the accuracy that look-ahead
> buys.*

> ### Minimal Mathematics / Prerequisites for this Chapter
>
> - **A count as a product**: steps per frame, frames per second, and why multiplying the two gives a
>   rate whose units have to be checked before the number is trusted.
> - **Capacity as a product**: entries per block, blocks held, elements per entry -- the same shape of
>   argument, sized in a different unit.
> - **Powers of two**: why a depth or a width that lands on one costs differently from one that does
>   not, and where that difference stops being free.
> - **Headroom**: the gap between a value and the largest its container can hold, and why a ring buffer
>   is full at capacity minus one rather than at capacity.

---

<!-- source: 9.1 reviewed fragment -->

## 9.1 The Target, and What Is Still Undecided About It

*Where this sits in the chain: the* **Model** *stage, drawn as wiring -- and the* **Fabric logic**
*storage it shares a design with, because none of this encoder's memory lives anywhere else.*

Everything in this chapter rests on one model, and that model is not chosen. The decision is the owner's, it is open, and it is load-bearing: a streaming Conformer Large and a streaming FastConformer Large want different cache shapes, different step periods and different widths of wire, so they produce different overlays. What follows says which parts of each are registered and which are not, and it keeps naming both options instead of averaging them into one.

**The registered readings do not agree on the target's shape.** *Conformer* here names the encoder block that puts self-attention beside a depthwise convolution, and *FastConformer* is the cheaper variant of that block. Each row below is one published config for one model. A dash means this section prints no value for that field, not that the field does not exist.

| Reading of the target | Hidden width | Encoder blocks | Attention heads | Convolution taps | Whole model | Records |
| --- | --- | --- | --- | --- | --- | --- |
| Conformer-Transducer Small, offline | 176 | 16 | 4 | **31** | about 14 million | `V-05-12`, `V-05-13`, `V-05-14`, `V-05-15`, `V-05-16` |
| Conformer-Transducer Large, offline | 512 | 17 | 8 | — | — | `V-05-17`, `V-05-18`, `V-05-19` |
| WeNet U2++ Conformer, streaming | 256 | 12 | 4 | **15** | — | `V-05-03`, `V-05-04`, `V-05-05`, `V-05-06` |
| Streaming Conformer Large, cache-aware | 512 | 17 | 8 | **31** | about 120 million | `V-05-23`, `V-05-22`, `V-05-24`, `V-05-25`, `V-05-33` |
| Streaming FastConformer Large, cache-aware | 512 | 17 | 8 | **9** | about 115 million | `V-05-38`, `V-05-37`, `V-05-39`, `V-05-40`, `V-05-46` |
| Streaming Conformer-Transducer Small, named by the project spine | — | — | — | — | — | `V-05-56` |

Two of these fields change the datapath rather than merely its size.

**The convolution tap count is a fork, not a family property.** A depthwise convolution is a sliding window over the recent frames of one hidden stream, so the tap count sets how far back that window reaches and how much history has to be held beside it. The readings disagree in a way that a hardware designer cannot route around: the offline Conformer-Transducer Small keeps **31** taps, and so does the cache-aware streaming Conformer-Transducer Large, while the streaming FastConformer cuts the same window to **9** and the other framework in this table publishes **15**. The Records column of the table above says which reading prints which of those three, and the sentence beside it is not a claim about a single model. An overlay sized for one of those windows is not an overlay sized for the other, and the shorter window is the reason the FastConformer variant is called fast rather than a detail of its recipe. The second structural field is registered for three of the six readings and not for the rest: the offline Conformer-Transducer Large feeds its convolution module through batch normalisation, while both streaming NeMo readings use layer normalisation, and no record in this section prints a value for either Small row or for the WeNet row. A reader who needs the difference between those two normalisations explained should read section 8.3, where the arithmetic of each one on a device with no floating-point unit is the subject rather than a config field.

**Hidden width decides what a head slice costs.** A width of 512 units split across 8 heads divides by a power of two, so at that width a head index is a shift and a head slice is a byte range. A width of 176 units across 4 heads does not, and neither shortcut is available for that reading. The Records column names which record prints which pair.

**The two streaming candidates reach the evidence only as weight counts** — about 120 million and about 115 million, both rounded by their publisher rather than counted, against the small offline model's about 14 million. Put those beside the fabric this book targets: 117,120 look-up tables, 144 block RAM (BRAM -- on-chip storage) blocks, 64 UltraRAM (URAM) blocks and 1,248 multiply-accumulate slices on the device column registered for this board, with 23,616 Kb of BRAM and URAM together, a figure that same record unrolls to 2,952 KiB. The difference in scale needs no arithmetic to see; the two records behind those device numbers are named in the table at the end of this section. What cannot be seen is what each weight costs to hold, and that is a registered gap rather than an omission: no multiply-accumulate (MAC) count per frame, no 8-bit integer (INT8) weight bytes and no activation bytes per frame exist for any candidate. So this chapter describes a datapath and sizes nothing in bytes, and no parameter count in this section is ever converted into one.

**Two frameworks disagreeing about a model's size is a fact about frameworks.** The WeNet reading carries published accuracy where the NeMo readings here do not: at chunk size 16, which that record turns into 640 ms on its own stated basis of 40 ms per feature frame, it reports 3.80% word error rate (WER) with attention rescoring and 4.54% with connectionist temporal classification (CTC) beam search. The same record states that right-away and future-context latency in milliseconds remain unverified for that checkpoint, and that the 640 ms is arithmetic on a published chunk size. A reader should conclude that no single registered reading supplies both a shape and an accuracy, so a sentence of the form "the Conformer needs this much and scores that" is not available yet. The fourth model the spine names is worse off still: the search for a checkpoint that is at once Conformer-Transducer, streaming and Small is registered and its answer is not, and the English score table for the family was read in full without producing such a row. That phrase therefore carries no published accuracy, which is the split this chapter inherits rather than resolves. Per-step timing for the two streaming candidates is likewise not printed in this section, so no context depth in milliseconds is derived from it here either.

> **Traceability note.** The records this section stands on, and what each one is claimed to
> establish. The table at the head of the section keeps the shape readings row by row; the rows below
> carry the fields the prose argues over, the device capacities, and the two gaps.

| Record | What it establishes here |
| --- | --- |
| `V-05-15`, `V-05-25` | the offline Small and the streaming Large Conformer-Transducer each set `conv_kernel_size: 31`, so the tap window is **31** wide in both |
| `V-05-40` | the streaming FastConformer sets the same key to **9**, a shorter window rather than a smaller model |
| `V-05-04` | the WeNet config prints `cnn_kernel: 15`, the third tap count on the table, together with `output_size: 256`, `attention_heads: 4` and `num_blocks: 12` |
| `V-05-18`, `V-05-19` | hidden width **512** and attention heads **8** for the offline Large, so a head slice is 512 / 8 units wide |
| `V-05-13`, `V-05-14` | hidden width **176** and heads **4** for the offline Small, a division by no power of two |
| `V-05-23`, `V-05-38` | hidden width **512** for each of the two streaming large configs |
| `V-05-20` | the offline Large convolution module is normalised with `batch_norm`; the config comment beside it lists the alternatives |
| `V-05-26`, `V-05-41` | the two streaming NeMo configs normalise the same module with `layer_norm` |
| `V-05-33` | about **120 million** parameters for the streaming Conformer Large, rounded by its publisher |
| `V-05-46` | about **115 million** parameters for the streaming FastConformer Large, rounded the same way |
| `V-05-16` | about **14 million** parameters for the offline Small Conformer-Transducer |
| `V-01-15` | the target device column: **117,120** LUTs, **144** BRAM blocks, **64** URAM blocks, **1,248** multiply-accumulate slices |
| `V-01-22` | **23,616** Kb of BRAM and URAM together, unrolled by the record itself to **2,952** KiB and to the rest of its unit chain |
| `V-05-57` | no per-frame MAC count, no INT8 weight bytes and no activation bytes per frame are printed by any publisher, for any candidate |
| `V-05-05` | the WeNet chunk size **16** equals **640** ms at that record's own basis of **40** ms per feature frame |
| `V-05-06` | **3.80** per cent WER with attention rescoring and **4.54** per cent with CTC beam search for that checkpoint, with right-away and future-context latency unverified |
| `V-05-56` | the search for a checkpoint that is at once Conformer-Transducer, streaming and Small, registered as unresolved: no such row in the family's English score table |

<!-- source: 9.2 reviewed fragment -->

## 9.2 One Conformer Block, Drawn as a Datapath

*Where this sits in the chain: the* **Model** *stage -- one block of it, drawn as wiring. The same*
*block is drawn again from the* **Fabric logic** *side in chapter 8, where its cells get placed.*

**A block is a line of stages, and each stage carries one number.** Read one encoder block as a datapath and the questions turn hardware-shaped: how wide is the tensor between stage two and stage three, what arithmetic does each stage perform, and what must it remember. Each answer is a key in a recipe config published by somebody else. Eight keys size or shape the whole chain, and two of those eight choose arithmetic rather than size.

| Config key | What it controls | Values on record |
| --- | --- | --- |
| `model.encoder.n_layers` | how many times the block repeats | 16 blocks `V-05-12`; 17 `V-05-17`, `V-05-22`, `V-05-37`; 12 `V-05-04` |
| `model.encoder.d_model` | hidden width, the wire every stage is cut to | 176 `V-05-13`; 512 `V-05-18`, `V-05-23`, `V-05-38`; 256 `V-05-04` |
| `model.encoder.n_heads` | how that width is split for attention (attention -- the stage that scores every step against the steps it may look at) | 4 `V-05-14`, `V-05-04`; 8 `V-05-19`, `V-05-24`, `V-05-39` |
| `model.encoder.conv_kernel_size` | taps in the depthwise convolution (one filter per channel, not across channels) | 31 `V-05-15`, `V-05-25`; 9 `V-05-40`; 15 `V-05-04` |
| `model.encoder.ff_expansion_factor` | inner width of the feed-forward, as a multiple of `d_model` | 4 `V-05-36`; the WeNet config prints an absolute instead: 2048 `V-05-04` |
| `model.encoder.subsampling_factor` | how many feature frames collapse into the one step a block sees | 4 `V-05-32`; 8 `V-05-42` |
| `model.encoder.conv_norm_type` | which normalisation sits inside the convolution module | `batch_norm` `V-05-20`; `layer_norm` `V-05-26`, `V-05-41` |
| `model.encoder.self_attention_model` | how attention learns distance between steps | `rel_pos` `V-05-21`, `V-05-27` |

Those columns are candidates, not a settled number. One of them is the Small row of a table in a config header, read against the body below it, and another describes a different toolkit's whole model; the target is undecided, so the block count stays a set rather than collapsing to its largest member. The traceability note at the end of this section names which record prints which value.

**Two keys are read before any block runs, and together they set the clock.** The front end hands
over a feature frame every 0.01 s, and the encoder collapses a fixed number of those frames into the
one step a block sees. Both periods are products of that kind of pair, and the note at the end of
this section names which record prints which factor. Multiplying the streaming Conformer's stride by
its factor of 4 is derived arithmetic, and the same stride against a factor of 8 is derived
arithmetic too: derived values of 40 ms and 80 ms, for the two recipes respectively. That product is
worth writing out once, because almost every other number in this chapter is measured in steps of it,
and because it is where an expensive misreading lives.

> **The formula.** $T_\text{step} = S_\text{feat} \times F_\text{sub}$
>
> **The variables.**
>
> - $T_\text{step}$ — the period of one encoder step: how often the block chain is handed a new
>   frame to work on. Seconds, printed here in milliseconds.
> - $S_\text{feat}$ — the stride between successive audio feature frames leaving the front end.
>   Seconds. Both recipes here print 0.01 s.
> - $F_\text{sub}$ — the encoder's subsampling factor: how many feature frames are thrown away to
>   keep one. A pure count, with no unit. The two recipes print 4 and 8.
>
> **What it means.** The encoder's first move is to decimate: it reads $F_\text{sub}$ feature frames
> and hands the blocks one step. So the object a block works on is $F_\text{sub}$ strides old, and
> the interval between the things a block does is the stride multiplied by that count. Nothing else
> in the block sets the rate -- no weight, no head count, no clock frequency enters this product --
> which is why the two config keys are read before any block is argued about.
>
> **What it costs.** In fabric terms, $T_\text{step}$ is the deadline, not a resource: one step must
> finish inside it, at whatever clock the overlay closes at. Nothing is registered for any candidate
> about what a step costs in look-up tables, DSP slices, storage tiles or cycles, so this card claims
> no silicon figure, and the record that registers the absence is named in the note below.
>
> **What it does not say.** It does not say that the frames counted in $F_\text{sub}$ are frames of
> raw audio. They are the output of the **DSP front end**, one per stride, so every span written in
> steps -- a chunk, a left context, a look-ahead -- is already in decimated units. Reading those
> units as raw audio frames is wrong by the very factor the product just used: out by four for the
> one recipe, out by eight for the other, and section 9.4 works one example through. The step time is
> not a computation time either: nothing says how long a step takes, and that number belongs to a
> board nobody has run. Nor is the stride a measured arrival rate -- it is a number a config file
> declares, in both recipes.

Beside the record that sets the streaming Conformer's tap count to 31, the same file sets
`conv_context_size` to `causal`, and the comment on that line spells *causal* as the pair "kernel
size minus one behind, zero ahead": every tap looks backwards, which is what lets this convolution
be built as a shift register with the taps hanging off it.

**The normalisation key is a datapath decision, not a style preference.** The comment printed in the offline Large's config lists three answers for the convolution's normalisation: `batch_norm`, `layer_norm`, or a grouped variant. BatchNorm's number for a channel comes from statistics stored while training, so at inference it is a scale and a shift per channel, and a scale and a shift can be pushed backwards into the depthwise weights around it: the stage is deleted, and the design inherits a table of stored per-channel values it must keep and apply. LayerNorm's number comes from the frame arriving right now -- a mean, a variance, a reciprocal square root per step, computed at runtime -- so it folds into nothing and has to be built as a unit of its own, with a reduction across `d_model`. The offline Large config prints `batch_norm`; the two streaming configs both print `layer_norm`, and the records that print each are in the note below. A target that normalises this way inside the block keeps a data-dependent stage; one that does not can remove it and must carry the statistics instead. The position scheme is the other arithmetic choice: `rel_pos` scores a pair of steps by the gap between them, which a table of gaps can hold, while the same config comment names `abs_pos` as the alternative that indexes position in the window. The decomposition behind relative position is quoted by no record here, so the book notes the choice and stops.

**An expansion factor is a ratio, and reading it as a stage count is a factor-of-four error.** One record prints the feed-forward expansion factor as 4, where the other framework's config prints the same stage's width outright as 2048 units, its own comment calling it the number of units of position-wise feed forward. Two files, two shapes of the same idea, so a reader has to know which one they are holding. Worse, the expansion factor 4 and the subsampling factor 4 are the same digit doing unrelated jobs: one widens a stage, the other collapses time. Take the first as four stages and every per-block total downstream grows by four, and a rounding chain carries that multiplier into the bit widths chosen after it.

**What the registry does not tell you is the block's shape.** No record quoted here prints how many sub-layers sit inside one block, or in what order. Those come from the architecture's definition and from the code implementing it, which a config file has no reason to repeat. So [Figure 32](#fig-conformer-block) draws the sub-layers as the book's working assumption and says so in the picture: the keys inside the boxes are what a record prints, the wires joining them are not. Nothing in this section is a per-frame cost either, because none is registered.

::: {#fig-conformer-block .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  stage/.style={draw, densely dashed, rounded corners=1pt, align=center,
                inner sep=4pt, minimum width=7.2cm},
  add/.style={draw, circle, inner sep=2.4pt},
  flow/.style={-{Stealth[length=2.2mm]}, semithick},
  res/.style={-{Stealth[length=2.2mm]}, semithick, densely dashed},
  t/.style={text width=2.8cm, align=center}
]
\node[t] (stepin) {one encoder step in\\[2pt] \texttt{subsampling\_factor}};
\node[stage] (ff) [below=9mm of stepin] {feed-forward part\\[2pt] \texttt{ff\_expansion\_factor}};
\node[add] (a1) [below=7mm of ff] {$+$};
\node[stage] (att) [below=7mm of a1] {multi-head attention\\[2pt] \texttt{d\_model}\qquad \texttt{n\_heads}\\[2pt] \texttt{self\_attention\_model}};
\node[add] (a2) [below=7mm of att] {$+$};
\node[stage] (conv) [below=7mm of a2] {depthwise convolution and its norm\\[2pt] \texttt{conv\_kernel\_size}\quad \texttt{conv\_norm\_type}\\[2pt] \textit{does this norm fold?}};
\node[add] (a3) [below=7mm of conv] {$+$};
\node[t] (stepout) [below=9mm of a3] {to block $i{+}1$\\[2pt] \texttt{n\_layers} blocks deep};
\draw[flow] (stepin) -- (ff);
\draw[flow] (ff) -- (a1);
\draw[flow] (a1) -- (att);
\draw[flow] (att) -- (a2);
\draw[flow] (a2) -- (conv);
\draw[flow] (conv) -- (a3);
\draw[flow] (a3) -- (stepout);
\draw[res] (stepin.east) to[bend left=16] (a1.east);
\draw[res] (a1.east) to[bend left=16] (a2.east);
\draw[res] (a2.east) to[bend left=16] (a3.east);
\node[anchor=west, font=\scriptsize] at ($(a1.east)+(1.6cm,0.5cm)$) {residual};
\node[below=10mm of stepout, align=left, font=\scriptsize, text width=11.2cm]
  {\textbf{Dashed} = the count and order of the sub-layers inside the block, which no
   record quotes; each \texttt{key} is a config line a record does print.};
\end{tikzpicture}
```
One block, stage by stage, with the addition points where a block's input is returned to its output and the key that sizes each stage written under the stage it sizes.
:::

> **Traceability note.** The config-key table above carries its own per-row citations. This note
> holds the records the prose leans on, the pair that sets the step period, and the gap that keeps the
> card above from naming a cost.

| Record | What it establishes here |
| --- | --- |
| `V-05-12` | `n_layers: 16` for the offline Small, read from a table in a config header against the body below it |
| `V-05-31`, `V-05-45` | `window_stride: 0.01` -- one feature frame every 0.01 s, in the streaming Conformer's config and in the FastConformer's |
| `V-05-32` | `subsampling_factor: 4` for the streaming Conformer, with the config comment requiring a power of two |
| `V-05-42` | `subsampling_factor: 8` for the streaming FastConformer, on the same comment |
| `V-05-25` | the streaming Conformer's `conv_kernel_size: 31`, on the same file and in the same comment block as its `conv_context_size: causal` |
| `V-05-20` | `conv_norm_type: batch_norm` for the offline Large, with the comment listing `layer_norm` and a grouped variant as the alternatives |
| `V-05-26`, `V-05-41` | `conv_norm_type: layer_norm` for the two streaming configs |
| `V-05-21`, `V-05-27` | `self_attention_model: rel_pos` for the offline Large and the streaming Large, the two readings that register the position scheme |
| `V-05-36` | `ff_expansion_factor: 4`, a ratio against `d_model` rather than an absolute width |
| `V-05-57` | nothing is registered for any candidate about MACs per frame, weight bytes or activation bytes, so no step in this section can be priced |

<!-- source: 9.2 ConfASR hand -->

### 9.2.1 The Silicon Record: ConfASR

Everything this chapter has drawn as wires has been built, taped out and measured by somebody else: ConfASR, a Conformer-block accelerator from RWTH Aachen University, presented at a design-automation conference. It is not a study of a related network, and not a survey of accelerators in general. It takes the block family this book ports, and it puts that family into silicon. For a chapter that has so far reasoned from config files and from arithmetic, that changes the standing of every shape on the page. The datapath sketched in this section, and the buffer drawn in section 9.4, exist as measured hardware in the record, and the book's own unmeasured design can now be read against them rather than against nothing.

One thing about this section's evidence has to be said before it is used, and the rest of the section depends on saying it. No full text of this paper is available to this project. What is available is the record's abstract, retrieved from the publisher's metadata, and it is short enough to quote in full against the mechanisms it names:

> "We propose a hardware-friendly normalization, shared scaling factors for non-linear functions, and an efficient dataflow with a shared MAC array that keeps all activations on chip."

That one sentence names two mechanisms, and each one lands on a decision this book has already made or still owes. It does not name a third, and the third thing this section would like to claim is handled at the end of this subsection as the unresolved question it is rather than pressed into service as a third quote.

**Mechanism one: keep the activations on-chip.**

The clause that carries this one is the last: one MAC array, shared across the block's stages, sized so that all the activations stay on chip. This is the chapter 3 dataflow taxonomy made into silicon, with the decision taken one level above the processing element. Rather than parking one operand at each element, the array itself is shared between a block's operations, and the intermediate activations that would otherwise travel to DRAM never leave the die. The reason is memory traffic and not arithmetic -- which is the same argument this chapter makes for keeping a block's stages on chip instead of running them as separate passes over memory.

**Mechanism two: buy the non-linear stages with shared scaling.**

The first two clauses of the same sentence are this one: a normalisation the hardware can afford, and scaling factors shared across the non-linear functions rather than one per function. That is the integer-only path section 7.5 reads out of I-BERT and that section 8.3 derives for this book's own design, and it is why the plan uses fixed-point scaling at those stages. "Shared" is the load-bearing word. A scaling factor per function costs a multiplier and a width decision each, and sharing them is what makes a block's worth of non-linear stages affordable at all.

**The third thing this section would like to claim, and cannot.**

A streaming Conformer has to carry the keys and values of its left context forward from chunk to chunk, so a dedicated buffer for that past is exactly the object this chapter would like to find in silicon. The record does not name one. The available abstract mentions on-chip activation residency and shared scaling factors, and stops there; a claim that this accelerator builds a left-context cache could not be traced to any text this project can reach, so the record for it is registered as unresolved and this section does not attribute it. [Figure 36](#fig-kv-ring-buffer) is therefore this book's own design for that requirement and not a reproduction of the record's: the ring buffer holds the left-context keys and values for the attention of the current chunk, writes the new entries in as each chunk arrives, and overwrites the oldest rather than shifting anything. The requirement is real, and section 9.3 derives it from the model. Who else has spent fabric on it is a question this repository cannot answer yet.

The record's silicon figures and this book's registered fabric figures sit side by side below. Every row that prints a ConfASR number carries its record id in that row, and the book's column prints only the values the registry holds for its own target.

| Quantity | ConfASR record | This book's KV260 design | Where it comes from |
| --- | --- | --- | --- |
| Process | 22 nm FDSOI | no registered value | `V-07-16` |
| Clock | 250 MHz | no registered value | `V-07-17` |
| Operating power | 359 mW | no registered value | `V-07-18` |
| Core die area | 1.19 mm2 | no registered value | `V-07-19` |
| Fabric look-up tables | not reported | 117,120 | `V-01-15` |
| DSP slices | not reported | 1,248 | `V-01-15` |
| On-chip memory | not reported | 23,616 Kb | `V-01-22` |
| Streaming headroom | greater than 900x real-time | no registered value | `V-07-20` |
| Latency vs prior ASR hardware | greater than 4x | no registered value | `V-07-21` |
| Power vs existing edge platforms | 16x | no registered value | `V-07-22` |

What the record changes is the standing of the plan, not its numbers. Both of the mechanisms this section can attribute are proven in silicon, running at the record's clock in the record's process and burning its operating power over its core die area -- all four figures carried by the traceability rows below. That is the difference between a datapath this book has argued for and one that has been measured. And both are decisions this book has already reached for its own reasons: on-chip activation residency follows from chapter 3's dataflow argument, and hardware-friendly normalisation with shared scaling factors is the method that section 7.5 and section 8.3 teach. The left-context buffer is not part of that count. It is this book's own answer to a requirement the model imposes, drawn in section 9.4, and the record's silence on it leaves it exactly as unmeasured as it was before this section began.

What the record does not buy is a prediction for this build. ConfASR is a dedicated die in a fully-depleted silicon-on-insulator process, while the KV260 is programmable fabric whose resources are quoted above; those are different ways to make a circuit, and a dedicated die spends no silicon on rerouting. The book's own column holds no registered clock, power, area or process figure, so no frequency and no watt for this build is printed here. The record's headroom and reduction figures are claims about that accelerator's measurements against the baselines it compared itself to, and each is supported in its row above; they are not forecasts of what a KV260 overlay would reach, and this book has measured none of them. The record also reports no fabric figure -- no look-up tables and no DSP slices -- so the two columns cannot be joined into one comparison of efficiency.

> **Traceability note.** The comparison table above carries its own per-row citations. This note
> holds the ConfASR records behind the table's left column and the one mechanism quote the prose
> attributes to the record. No full text of this paper is available to this project: that quote is a
> sentence of the abstract, retrieved from the publisher's metadata, and it is transcribed in full in
> research note R04, section 3.2. Two of the three mechanism quotes an earlier revision of this
> section attributed to the paper were paraphrases, and the third was not in any source this
> repository holds; R04, section 3.2, records that correction, and the third mechanism's record is
> registered as unresolved rather than re-quoted.

| Record | What it establishes here |
| --- | --- |
| `V-07-16` | the accelerator's process technology, printed by the record as fully-depleted silicon-on-insulator |
| `V-07-17` | the accelerator's clock frequency |
| `V-07-18` | the accelerator's operating power |
| `V-07-19` | the accelerator's core die area |
| `V-07-20` | the streaming headroom multiplier, given by the record as a lower bound against real-time streaming |
| `V-07-21` | the latency reduction multiplier, given by the record as a lower bound against previous streaming ASR hardware solutions |
| `V-07-22` | the power reduction multiplier, claimed by the record in real-time streaming mode against existing edge platforms |
| `V-07-23` | the abstract's efficient dataflow with a shared MAC array keeping all activations on chip, the clause mechanism one rests on |
| `V-07-24` | the abstract's hardware-friendly normalisation and its shared scaling factors for non-linear functions, the clauses mechanism two rests on |
| `V-07-25` | registered unresolved: no text available to this project supports a claim that the accelerator buffers chunk-based causal attention left context, which is why this section attributes no such mechanism to it |

<!-- source: 9.3 hand -->

## 9.3 Attention Inside a Chunk, With Position Measured Rather Than Absolute

*Where this sits in the chain: still the* **Model** *stage, inside one block, at the stage that reads
the past. What it decides here -- how much past exists for the network to read -- is what the*
**Fabric logic** *stage has to store.*

**Intuition.** Attention lets one frame of audio ask the other frames a question, and the only
engineering problem it creates is that the asking has to be bounded. In words a hardware reader
already has: a frame forms a query, compares it against the key of every frame it is allowed to
see, and takes a weighted average of their values, where the weights come from how well the query
matched each key. Nothing about that is special to speech. What is special here is that the
microphone is still running: most of the frames a finished utterance would offer do not exist
yet, and the frames that do exist cannot be kept indefinitely. So the design must decide, once and
in hardware, which frames exist for the network to read at all. Appendix A explains the query, key
and value machinery from the beginning; this section is about the boundary around it.

**Mechanism.** Streaming attention is not one of the two shapes a reader already knows. Full attention lets every frame see every other frame of an utterance, which is what an offline encoder does and what a chip receiving audio as it arrives cannot do, because the later frames do not exist yet. A plain sliding window lets a frame see a fixed number of earlier steps and nothing else, which is the recurrent shape: it streams, and it also deletes the future that the model was trained to use. Cache-aware streaming attention is a third thing. The registered name for it is `chunked_limited`, and in that mode a frame attends in both directions inside its own chunk and to a bounded number of earlier chunks -- so the mask is not a stripe of recent steps but a band: the current chunk complete, plus a left context counted in frames the design has already finished.

**Both sides of that band are registered, for both streaming candidates.** The cache-aware streaming Conformer-Transducer publishes an attention context pair of one hundred forty steps behind and twenty-seven ahead; the FastConformer publishes seventy behind and thirteen ahead, at a step 80 ms wide rather than 40 ms, on the same block depth and the same hidden width. The records behind those five numbers are named in the note at the end of this section, and section 9.4 is where the step periods come from. The two pairs are the same shape, and the reason they differ is worth stating precisely because it is easy to read as a smaller model: seventy steps at 80 ms reaches back as far in seconds as one hundred forty at 40 ms, and it does so with half as many cached frames. That trade is what the FastConformer is built to make.

**A strict causal mask is the wrong tool here, not a stricter version of the right one.** A causal mask is a triangle: it keeps the diagonal and everything to its left, and it deletes every future position, which is exactly the twenty-seven and thirteen steps above. A chunk mask keeps the future inside the current chunk, because that future is already in hand -- the design waits for a chunk of audio before it computes anything -- and across chunks it keeps only as much past as the cached context can supply. Set the right context to zero and a chunk mask becomes a causal one, so the two differ by one parameter rather than by a family of ideas. The cost of doing so is not a small loss of accuracy. It removes the look-ahead the recipe configures on purpose, and a checkpoint trained with a nonzero right context has been trained to read those positions.

**Position enters as a distance rather than as an index.** Both the offline large reading and the streaming one register `rel_pos`, which the registry identifies as the Transformer-XL scheme, and what it is for is this: a token's position changes a score only through how far it sits from the token being scored. That property is what lets a cached chunk keep meaning after newer chunks arrive. A score built from absolute indices is only correct while the indices in the cache are the ones the model saw during training, so a rolling buffer would have to be recomputed each time the buffer slides. A score built from distances stays correct at any wall-clock moment, because the distance between two frames is the same whether they are the first frames of an utterance or the last. How a relative score is composed from its terms is not quoted anywhere in this registry, so this section says what the scheme is for and does not present a sum as fact.

**Hardware application.** The cached quantity scales with the hidden width, not with the head count. What the overlay keeps per cached step is a key vector and a value vector for each head, and each has the length of one head: the hidden width divided by the number of heads. At a hidden width of 512 units that is 64 per head with 8 heads, and 44 per head with 4 heads at a width of 176; the records that print those widths and counts are in the note below. Multiply a head slice by the head count to get a total per step and the answer is the hidden width again, so doubling the heads at fixed width leaves the cache exactly as large and makes every head narrower. The two keys move together in a config file and not at all in a budget, which is the point [Figure 34](#fig-head-slicing) draws.

**One contrast from the other framework, so the shape above is not mistaken for a convention.** The other recipe sets its chunk at 16 frames, which is 640 ms of audio at the same 40 ms per feature frame, and its encoder is 12 blocks of 256 units with 4 heads -- both printed by the single record the note below names for that row. A longer chunk is not a different attention regime. It is the same band with a wider current block, and it buys that width in exactly the currency chapter 8 counts. [Figure 33](#fig-attention-regimes) sets the three masks beside one another, on the same five frames, so the difference between them is a shape rather than a description.

::: {#fig-attention-regimes .figure}
```tikz
% Three attention masks over one five-frame stream. A filled cell at row r, column c
% means frame r is allowed to read frame c. Cell (r,c) with r below c is future context.
\begin{tikzpicture}[
  % One unit is one cell, and +y points down so that row r sits below row r-1. With the
  % default upward y the causal triangle mirrors into "only the future", which is the exact
  % opposite of the sentence beside it.
  x=3.4mm, y=-3.4mm,
  lbl/.style={font=\scriptsize, anchor=east, inner sep=2pt},
  ex/.style={font=\scriptsize, align=left, anchor=west, inner sep=2pt, text width=62mm},
  ax/.style={font=\tiny, inner sep=1pt},
  grid/.style={draw=black, line width=0.3pt},
  chunk/.style={draw=black!70, densely dashed, line width=0.4pt},
]
% The frame index, printed once above the first grid; the three grids share one stream.
\foreach \i/\x in {1/0.5,2/1.5,3/2.5,4/3.5,5/4.5}
  \node[ax] at (\x,-0.6) {\i};
% --- full: the offline case, every cell open.
\fill[black!70] (0,0) rectangle (5,5);
\draw[grid] (0,0) rectangle (5,5);
\node[lbl] at (-0.35,2.5) {full};
\node[ex] at (6.2,2.5) {every frame reads every other one, which needs the whole
  utterance before any of it can start};
% --- causal: the diagonal and the past, nothing to the right of it.
\fill[black!70] (0,6.5) rectangle (1,7.5);
\fill[black!70] (0,7.5) rectangle (2,8.5);
\fill[black!70] (0,8.5) rectangle (3,9.5);
\fill[black!70] (0,9.5) rectangle (4,10.5);
\fill[black!70] (0,10.5) rectangle (5,11.5);
\draw[grid] (0,6.5) rectangle (5,11.5);
\node[lbl] at (-0.35,9) {causal};
\node[ex] at (6.2,9) {the diagonal survives and everything below it, and every cell to
  the right of it is a frame that has not arrived yet};
% --- chunked: complete across the current chunk, bounded behind it.
\fill[black!35] (0,13) rectangle (2,14);
\fill[black!35] (0,14) rectangle (3,15);
\fill[black!35] (0,15) rectangle (4,16);
\fill[black!35] (1,16) rectangle (5,17);
\fill[black!35] (2,17) rectangle (5,18);
\fill[black!80] (3,16) rectangle (5,18);
\draw[chunk] (3,16) rectangle (5,18);
\draw[grid] (0,13) rectangle (5,18);
\node[lbl] at (-0.35,15.5) {chunked};
\node[ex] at (6.2,15.5) {the dashed block is the current chunk, complete in both
  directions; the grey to its left is cached context, and the grey to the right of each
  diagonal is the look-ahead a causal mask deletes};
\end{tikzpicture}
```
The same five frames under three masks, drawn at two steps of left context and one of
look-ahead so that the shape is legible at this size. Those three spans are illustrative
geometry, not the registered pairs: the context widths a reader would design with are in the
prose above and in the note below this section, and they are far wider than a grid can show.
:::

**A head is a slice of the wire, not a second wire.** The figure above says how far back a step may
look. What it cannot say is how much a step costs to remember, and that is where the head count
looks like it should matter and does not. One row of the figure is the length of one stored vector,
and the cache is that row repeated by the number of heads and doubled for the two tensors.

::: {#fig-head-slicing .figure}
```tikz
% Two readings of one hidden vector, both spanning the same 6.4cm so that the equality is
% geometry rather than a sentence: heads x head-slice is the width, and the width is fixed.
\begin{tikzpicture}[
  font=\scriptsize,
  span/.style={Stealth-Stealth, black!65, thin},
  t/.style={font=\scriptsize, inner sep=2pt, align=left},
  sm/.style={font=\tiny, inner sep=1pt, text=black!62, align=left},
  cell/.style={draw, black!80, line width=0.3pt, fill=black!8},
  num/.style={font=\tiny, inner sep=0pt}
]
% Row 1: eight slices, one per head, at pitch 0.8cm.
\node[t, anchor=south west] at (0,1.5) {one cached step, width 512 split 8 ways};
\foreach \i in {0,...,7} {
  \draw[cell] (0.05+0.8*\i,0.15) rectangle (0.75+0.8*\i,0.95);
  \node[num] at (0.4+0.8*\i,0.55) {\i};
}
\draw[span] (0.05,1.1) -- (6.35,1.1);
\node[sm, above] at (3.2,1.1) {$d_\text{model}$: 8 slices of 64 units, one key row and one value row each};
% Row 2: four slices at twice the width, same total.
\node[t, anchor=south west] at (0,-0.78) {the same step, split 4 ways: wider slices, half as many};
\foreach \i in {0,...,3} {
  \draw[cell] (0.1+1.6*\i,-2.25) rectangle (1.5+1.6*\i,-1.45);
  \node[num] at (0.8+1.6*\i,-1.85) {\i};
}
\draw[span] (0.1,-1.3) -- (6.3,-1.3);
\node[sm, above] at (3.2,-1.3) {$d_\text{model}$ again: 4 slices of 128 units -- the same total, twice drawn};
\node[sm, text width=8.2cm, align=left, anchor=north west] at (0,-2.75)
  {what a step costs to keep is therefore the full width, counted twice for the two tensors and
   once per block -- the head count cancels, because it only moves the boundary between slices in
   the address map. The 64 and the 128 are arithmetic on the widths this book registers, not
   numbers a publisher prints; the widths and counts they divide are.};
\end{tikzpicture}
```
One cached step drawn twice, at the same total width and two different head counts, with the
two head-slice sizes the chapter's registered widths divide to. The point of drawing it this
way is that the second row is not smaller than the first: attention splits a vector, it does
not narrow it, so the cache a step leaves behind is the hidden width multiplied by the two
tensors and by the block count, and the head count cancels out of that product before any
byte is counted.
:::

> **Traceability note.** The records behind the mask widths, the position scheme and the head
> arithmetic above; the config-key table in section 9.2 already carries the same keys row by row.

| Record | What it establishes here |
| --- | --- |
| `V-05-28` | `att_context_style: chunked_limited` for the streaming Conformer, the registered name for the third mask shape |
| `V-05-29`, `V-05-30` | `att_context_size: [140, 27]` -- 140 attention steps of left context and 27 of right, for the streaming Conformer |
| `V-05-43`, `V-05-44` | `att_context_size: [70, 13]` -- 70 steps behind and 13 ahead, for the streaming FastConformer |
| `V-05-37`, `V-05-38` | the FastConformer's block depth and hidden width, the two fields that make its pair comparable with the Conformer's |
| `V-05-21`, `V-05-27` | `self_attention_model: rel_pos` for the offline Large and for the streaming Large, the two readings of the distance scheme |
| `V-05-18`, `V-05-19` | hidden width 512 and 8 heads for the offline Large, which divide to a head slice of 64 units |
| `V-05-23`, `V-05-24` | hidden width 512 and 8 heads for the streaming Conformer Large, the same division |
| `V-05-38`, `V-05-39` | hidden width 512 and 8 heads for the streaming FastConformer Large, the same division again |
| `V-05-13`, `V-05-14` | hidden width 176 and 4 heads for the offline Small, a head slice that no shift can reach |
| `V-05-05` | the other recipe's chunk size of 16 frames equals 640 ms at that record's own 40 ms per feature frame |
| `V-05-04` | that recipe's encoder: 12 blocks, `output_size: 256`, `attention_heads: 4`, in one published config |

<!-- source: 9.4 reviewed fragment -->

## 9.4 The Left-Context K/V Ring Buffer

*Where this sits in the chain: it is the* **Model** *stage's memory, held in* **Fabric logic**
*storage, and it is the reason the two stages cannot be designed one after the other.*

**Intuition.** A reader who has written a first-in first-out queue has already built the object
this section is named for. Attention needs the frames before the current one, the number of frames
it is allowed to need is fixed by the recipe, and a fixed number of frames is a fixed amount of
storage. So the past is not a list that grows: it is a circle of slots, and a new chunk is written
into the slot that holds the oldest one. Nothing is shifted and nothing is freed, because the write
position returns to the start of the circle by construction. The engineering questions are the two
a designer always asks about a queue: how deep it has to be, and what that depth costs. Appendix A
explains why it is the key and value tensors that have to persist and why the query does not -- a
finished step's query is consumed the moment its scores exist, while its key and value are read
again by every later step allowed to look back -- and that asymmetry is why this object has two
tensors per step and not three. This section sizes the storage and names what is still unregistered
about it.

**The borrowed name promises the wrong object.** Self-attention -- the part of the encoder where a frame looks at other frames, not only at its neighbours -- reads two tensors per frame, a key and a value, written K and V. The phrase "KV-cache" arrived from large language models (LLMs -- text generators that emit one token at a time), and the inheritance is a trap. An LLM cache grows with everything the model has produced, because its own output is what it must keep attending to, and no bound is set from outside. What this encoder needs is the opposite shape: a bounded window of earlier chunks that a fixed number of entries hold, each overwritten in turn. The name invites a reader to expect growth that never happens. So the project plan renames it the **Left-Context K/V Ring Buffer**, and the four words are the four properties that matter: only the past, both tensors, a write position that wraps, a fixed circle of slots. That rename is the plan's decision on the record, not a measurement. The plan's own capacity product, in section 6.7, is one factor short, and the correction is printed here rather than assumed silently.
<!-- Issue #48 is the open record for the omission in plan-v2.md section 6.7, measured against the
     WeNet recipe at 12 blocks. This chapter carries the corrected product; the plan file still
     prints the old one, and fixing it is that issue's job and not this file's. -->

**Mechanism.** The capacity is a product, and most of its factors are registered. The plan writes
the entry count as chunks kept $\times$ chunk length $\times$ head width $\times$ heads $\times$
two, for keys and values $\times$ bytes per element. Two pairs of those terms collapse. Heads times
head width is the hidden width, the length of the feature vector one frame carries, and chunks kept
times chunk length is the retained span in steps. What is left after that collapsing is the cache
of *one* block -- and that is where the plan's product stops, which is the error this chapter does
not repeat. Every encoder block keeps its own keys and its own values, because a block's attention
reads its own head of the stream and no other block's; the ring therefore holds one context per
block, each needing its own address space, and the whole product carries a factor of the block
count.

> **The formula.**
>
> $$N_\text{ring} = n_\text{blocks} \times T_\text{left} \times d_\text{model} \times 2 \times b$$
>
> **The variables.**
>
> - $N_\text{ring}$ — the capacity of the ring: how many stored numbers it must hold while the
>   design runs. A count, with no unit. Times $b$, it is a byte count.
> - $n_\text{blocks}$ — how many times the encoder block of section 9.2 repeats. A pure count,
>   registered per candidate in the table below, and the factor the plan's product leaves out.
> - $T_\text{left}$ — the left context: how many encoder steps of past the mask of section 9.3 lets a
>   step read. A count of steps, not of seconds -- the conversion is two paragraphs on.
> - $d_\text{model}$ — the hidden width: how many numbers describe one step. Hidden units.
> - $2$ — the two tensors a step caches: its key vector and its value vector. A count, and not three,
>   because the query is never cached; Appendix A is where that reason lives.
> - $b$ — the number of bytes one stored number occupies. Bytes. Unregistered for every candidate.
>
> **What it means.** Each factor is a direction of growth, and the product says the cache grows in
> all of them at once. Deeper past, more steps. Wider model, more numbers per step. More blocks,
> more copies of the whole thing, because a block's memory is not shared with its neighbour. Keys and
> values, never queries, because a step's question is answered the moment it is asked and thrown
> away while its answer is read by everything after it. The order of the factors does not matter and
> their independence does: the product is written this way because halving any one of them halves the
> ring, which is exactly what makes this arithmetic useful to a designer and useless as a cost.
>
> **What it costs.** Nothing is registered for this product in silicon, and this card invents no
> figure. What is on record is the container the cost would be paid in -- the block RAM and UltraRAM
> tile counts of the target device, named in the Hardware application below and in the note at the end
> of this section -- and what is not is the one factor, $b$, that turns a count of numbers into a
> count of bytes. Until a publisher or a board run prints a number format for a streaming Conformer,
> the capacity is a shape rather than a budget: the address map it implies, the number of tiles that
> would be claimed, and the cycles a read costs are all unmeasured.
>
> **What it does not say.** It says nothing about whether the result fits, and that is the misreading
> this formula invites hardest: a product of registered shapes is still not a resource report. Fitting
> is a placement question -- how many tiles the fabric holds, how they are banked, whether one
> block's read port collides with another's, and what is left over for the weights -- none of which
> a multiplication of counts can reach. It also does not say the block factor is a single number,
> because which candidate is the target is undecided, so the multiplier is registered per candidate
> and not for the book. And it does not say a step costs what a step costs: $b$ is a number no source
> prints, so the left-hand side is a count of stored numbers and not, yet, a count of bytes.

**The multiplier is registered, the target is not.** The block count is a published config value for
every reading this book holds, so the factor is not a hedge -- but section 9.1 is the reason it is
written as a set rather than as one number. The book's spine names a model whose checkpoint search
is registered and unresolved, so which of these counts is the design's is still the owner's decision.
Dropping the factor is therefore not a rounding choice either: the true capacity is twelve to
seventeen times the product the plan prints, and the reading a reader picks sets which.
[Figure 35](#fig-ring-per-block) draws what that factor is, because the single ring of the picture
below cannot show it -- one ring turning, twelve to seventeen times over, each copy needing its own
address space.

::: {#fig-ring-per-block .figure}
```tikz
% The factor the plan's product leaves out. Left: the one ring a reader has already seen.
% Right: the same ring, one copy per block, each with its own address space. The two are
% drawn at the same slot size so the difference is count and geometry, not scale.
\begin{tikzpicture}[font=\scriptsize,
  slot/.style={draw, minimum size=4.4mm, inner sep=0pt, fill=black!12},
  blk/.style={draw, densely dashed, rounded corners=1.5pt, inner sep=0pt},
  lab/.style={font=\scriptsize, inner sep=1pt},
  sm/.style={font=\tiny, text=black!65, inner sep=1pt},
  arr/.style={-{Stealth[length=2mm]}, semithick}]
% ---- left: the single ring every earlier picture drew ------------------------
\begin{scope}[shift={(1.15cm,0)}]
  \foreach \a in {90,45,0,-45,-90,-135,180,135}
    \node[slot] at (\a:0.72cm) {};
  \node[slot, fill=black!62] at (90:0.72cm) {};
\end{scope}
\node[sm, align=center, text width=3.4cm] at (1.15cm,1.62cm) {one ring, turning};
\node[sm, align=center, text width=4.2cm] at (1.15cm,-1.62cm)
  {$T_\text{left} \times d_\text{model} \times 2 \times b$\\
   the plan's product: one block's cache};
% ---- the multiplier, aimed at the gap in the stack -------------------------
\draw[arr] (2.35cm,0) -- (4.05cm,0);
\node[sm, text=black!80, align=left, anchor=south west] at (2.5cm,0.08cm)
  {$\times\; n_\text{blocks}$};
% ---- right: the same ring once per block -----------------------------------
\foreach \y/\lbl in {1.85/0, 0.95/1, -0.95/n{-}1} {
  \begin{scope}[shift={(6.4cm,\y)}]
    \node[blk, minimum width=5.6cm, minimum height=0.78cm] {};
    \node[anchor=west, lab] at (-2.5cm,0) {block $\lbl$};
    \begin{scope}[shift={(-0.55cm,0)}]
      \foreach \a in {90,45,0,-45,-90,-135,180,135}
        \node[slot, minimum size=2.2mm] at (\a:0.3cm) {};
      \node[slot, minimum size=2.2mm, fill=black!62] at (90:0.3cm) {};
    \end{scope}
    \node[anchor=west, sm, align=left, text width=2.5cm] at (0.3cm,0)
      {its own $T_\text{left}$ of past, its own address space};
  \end{scope}
}
\node[sm, align=left, text width=4.6cm, anchor=west] at (4.35cm,0)
  {\vdots\quad every block between them, too};
\node[sm, align=left, text width=5.6cm, anchor=north west] at (3.75cm,-1.62cm)
  {a block reads its own past and never its neighbour's, so the copies are twelve to
   seventeen address spaces live during every step, not one number folded into a total};
\end{tikzpicture}
```
The single ring of the figure below is one block's memory, and this is the whole encoder: the same
turning circle, once per block, with each copy deep enough to hold its own left context. The block
count is registered for every candidate the book holds, so the factor is a published number, while
which candidate is the target is not -- section 9.1 keeps that open. The bytes each slot occupies are
the one factor no source prints.
:::

Every factor the product needs, with the reading that registers it. The first five rows are the
plan's own fields; the block row is the one the plan's product leaves out.

| Factor | Value on record | Where it comes from |
| --- | --- | --- |
| $n_\text{blocks}$, streaming Conformer Large | 17 blocks | `V-05-22` |
| $n_\text{blocks}$, streaming FastConformer Large | 17 blocks | `V-05-37` |
| $n_\text{blocks}$, offline Conformer Large | 17 blocks | `V-05-17` |
| $n_\text{blocks}$, offline Conformer Small | 16 blocks | `V-05-12` |
| $n_\text{blocks}$, the other framework's streaming recipe | 12 blocks | `V-05-04` |
| $T_\text{left}$, as configured | 140 steps (Conformer), 70 steps (FastConformer) | `V-05-29`, `V-05-43` |
| $d_\text{model}$ | 512 units, both streaming large configs | `V-05-23`, `V-05-38` |
| Chunk length, the plan's own term, in feature frames | 16 frames | `V-05-05` |
| $b$, bytes per stored number | not printed by any source | `V-05-57` |
| Audio feature stride | 0.01 s, both recipes | `V-05-31`, `V-05-45` |
| Encoder subsampling factor | 4 (Conformer), 8 (FastConformer) | `V-05-32`, `V-05-42` |
| Step period, derived by multiplying the two rows above | 40 ms (Conformer), 80 ms (FastConformer) | `V-05-31`, `V-05-32`, `V-05-42`, `V-05-45` |
| Left span in time, derived: each context above at its own step period | 5600 ms, both recipes | `V-05-29`, `V-05-31`, `V-05-32`, `V-05-42`, `V-05-43`, `V-05-45` |
| Right context, as configured | 27 steps (Conformer), 13 steps (FastConformer) | `V-05-30`, `V-05-44` |
| Attention context style | `chunked_limited` | `V-05-28` |

Two more rows belong in that table for one reason: a reader who sizes the ring for a smaller model
needs to know how far below the large widths the published shapes reach, and which records say so.

| Factor | Value on record | Where it comes from |
| --- | --- | --- |
| $d_\text{model}$, the Small row of the recipe's own table | 176 units | `V-05-13` |
| $d_\text{model}$, the offline Large config body | 512 units | `V-05-18` |
| $d_\text{model}$, the other framework's streaming recipe | 256 units, with 4 heads | `V-05-04` |

So the ring is sized against the published shapes and not against a chosen model: the small reading
is not a guess at the large one, and every width in these two tables is a printed config line.

**Size the ring in seconds, not in steps.** The two recipes disagree about steps and agree about
time. Taking each recipe's left context at its own step period is derived arithmetic on the pairs of
records the last two rows of the table above cite, and both products are derived as 5600 ms --
section 9.2 is where the step period itself is built, factor by factor. So `chunked_limited` describes the same span of
wall-clock past under two different step counts, and an entry count written in steps silently
rescales when the recipe changes. A ring sized in seconds carries one requirement across both
candidates; the frame period is also the unit every deadline in this book is written in. The step
count is not free, either: it is what the block and tile arithmetic of chapter 8 consumes, and it is
the unit $T_\text{left}$ takes.

The trap the card warns about runs through this arithmetic in one step. A chunk of 16 frames is 16
*feature* frames, 40 ms each, so 640 ms of audio -- not 16 raw audio frames. Anyone who reads
$T_\text{left}$ as raw frames counts the same window four times too short in time, which is four
times too few entries in the ring, and then wonders why the overlay that size produced loses the
left context the recipe asked for. The subsampling factor of section 9.2 is the divisor that makes
the two units agree, and it belongs between them.

**Hardware application.** The container is registered; the contents are not. The device the plan
targets holds 144 BRAM blocks and 64 URAM blocks, with the
tile sizes fixed at 36 Kb and 288 Kb and the datasheet's Mb columns stated to be 1024-based, which is
the reading behind its printed `UltraRAM (Mb): 18.0`. The four records that print those figures are
named at the end of this section, because none of them converts into a claim about this ring. What
the same device's totals add up to is 23,616 Kb of BRAM and URAM together, a figure unrolled through
its own unit chain by the record that exists precisely to show that two different totals were each
defensible under some reading of a unit. No figure here is converted. What the block factor changes
about the placement, and what it does not, is what the picture above this one is for.

[Figure 36](#fig-kv-ring-buffer) is the object the section is named for.

::: {#fig-kv-ring-buffer .figure}
```tikz
\begin{tikzpicture}[font=\scriptsize,
  slot/.style={draw, minimum width=10mm, minimum height=7mm, inner sep=1pt},
  live/.style={slot, fill=black!62, text=white},
  kept/.style={slot, fill=black!12},
  old/.style={slot, fill=black!25},
  gone/.style={slot, dashed, text=black!55}]
\def\r{2.0cm}
\node[align=center] at (0,0) {one full turn\\ of the ring\\ $=$ the kept\\ window};
\node[live] (a) at (90:\r)  {live};
\node[kept] (b) at (45:\r)  {kept};
\node[kept] (c) at (0:\r)   {kept};
\node[kept] (d) at (-45:\r) {kept};
\node[kept] (e) at (-90:\r) {kept};
\node[kept] (f) at (-135:\r){kept};
\node[old]  (g) at (180:\r) {oldest};
\node[gone] (h) at (135:\r) {erased};
\draw[Stealth-, line width=1pt] ([shift={(0.55cm,0.5cm)}]a.north)
  node[left, align=right] {write\\ pointer} -- (a.north);
\draw[Stealth-Stealth, dashed, black!60] (g) -- (h)
  node[midway, above, align=center] {one slot per\\ chunk, no shift};
\node[anchor=west, text=black!60] at (118:2.75cm) {older than the window: never stored};
\end{tikzpicture}
```
Read the erased slot and the outer label together: nothing in this shape grows, so the price of keeping context is paid in a fixed circle of slots rather than in a list that lengthens.
:::

**What the product does not tell you.** Each step, a frame writes its K and its V into the live slot, and the pointer moves on: the slot it lands on holds the oldest retained chunk, and overwriting it is the entire cost, with no loop over memory and no shift, for the reason section 1.2 gave about the audio buffer. The product $N_\text{ring}$ is the useful half of that arithmetic, because it names the knobs and their factors -- halving chunks kept halves the entries, a narrower $d_\text{model}$ cuts them in proportion, and the number format moves $b$ as a step, not a slope. It cannot say whether the result fits. Fitting is a placement question about how many tiles the fabric holds and how they are banked, and a $b$ no source prints, so the fifth step of the rule matters more here than anywhere earlier in this book: a product of registered shapes is still not a resource report.

> **Traceability note.** Both factor tables above carry their own per-row citations, so this note
> holds only the prose: the device whose tiles the Hardware application names, and the shape of the
> one gap that keeps the card from pricing anything.

| Record | What it establishes here |
| --- | --- |
| `V-01-05` | the target device holds 144 block RAM tiles, each counted as a BRAM36 block |
| `V-01-07` | it holds 64 UltraRAM tiles, each counted as a URAM288 block |
| `V-01-23` | a block RAM tile is 36 Kb and an UltraRAM tile 288 Kb, and the datasheet's Mb columns are 1024-based |
| `V-01-08` | the datasheet line `UltraRAM (Mb): 18.0`, which is that reading of the UltraRAM population |
| `V-01-22` | the two populations together, 23,616 Kb, with the record's own unit chain unrolled because two different totals were each defensible under some reading of a unit |
| `V-05-57` | registered, and unresolved: no source prints the bytes one stored number occupies, so no candidate's ring has a byte size and no tile count follows from the product |

<!-- source: 9.5 reviewed fragment -->

## 9.5 The Fabric Boundary: What the ARM Side Keeps

**The overlay does not own its memory.** The DDR4 memory controller (DDRC -- the logic that drives the external chips) sits on the processor system (PS -- the fixed ARM cores), and the programmable logic (PL -- the fabric an overlay configures) reaches DRAM only through the AXI ports between the two sides (AXI -- the on-chip interconnect protocol of this family). The data sheet places the controller on the PS; the record's own note on that description adds that no memory pins run from the fabric straight to the chips. The memory behind those ports is what the data sheet quotes verbatim, "4 GB 64-bit wide, 2400 Mb/s", and its theoretical peak of 19.2 GB/s is derived in this book's registry from that bus width and rate -- an arithmetic figure the source itself never prints. Achievable bandwidth sits below the peak, because the fabric shares the controller, and its quality-of-service priorities, with the processors. An accelerator's view of DRAM is therefore a second-order question on this board: the first-order fact is the sharing. The Jetson this fabric is being compared against is registered at 102 GB/s of memory bandwidth, and no sentence here should be allowed to hide that gap.

::: {#fig-fabric-boundary .figure}
```tikz
% The topology section 9.5 argues from: the fabric and the memory it wants are on opposite sides of
% one narrow bridge. Positions only -- no measurement is drawn that the prose does not already cite.
% The DDRC and the DRAM sit on the PS; the PL reaches them only through the AXI ports, which is why
% the overlay "does not own its memory". Both crossings go left to right: weights arrive, activations
% arrive, and the fabric owns only what it is placed with.
\begin{tikzpicture}[
  font=\tiny,
  side/.style={draw=black!55, rounded corners=2pt, inner sep=0pt},
  blk/.style={draw=black!70, fill=black!6, rounded corners=1.5pt, align=center, inner sep=3pt,
    text width=3.1cm},
  hub/.style={draw=black!70, fill=black!16, rounded corners=1.5pt, align=center, inner sep=3pt},
  tick/.style={text=black!70},
  lab/.style={text=black!62, align=center, text width=3.5cm},
  bulk/.style={-{Stealth[length=2.2mm]}, line width=0.9pt, black!75},
  strm/.style={-{Stealth[length=1.9mm]}, densely dashed, black!68},
  own/.style={-{Stealth[length=1.6mm]}, black!55}]
  % ---- the two halves of the device, PS left, PL right, one gap between them ----
  \node[side, minimum width=4.4cm, minimum height=4.6cm] (ps) at (0,0) {};
  \node[side, minimum width=4.0cm, minimum height=4.6cm] (pl) at (8.6,0) {};
  \node[tick, anchor=north] at ($(ps.north)+(0,-0.06)$) {processor system (PS)};
  \node[tick, align=center, anchor=north] at ($(pl.north)+(0,-0.06)$) {programmable logic\\(PL -- the fabric)};
  % ---- off-chip memory and its controller, both on the PS side ----
  \node[blk] (dram) at ($(ps.north)+(0,-0.95)$) {external DDR4\\the model's weights};
  \node[hub] (ddrc) at ($(ps.north)+(0,-2.15)$) {memory controller (DDRC)};
  \node[blk] (arm) at ($(ps.north)+(0,-3.55)$) {ARM cores\\same model, in software};
  \draw[own] (dram.south) -- (ddrc.north);
  \draw[own] (ddrc) -- (arm);
  % ---- the fabric's own storage, which it does own ----
  \node[blk] (tiles) at ($(pl.north)+(0,-1.35)$) {BRAM / URAM tiles\\residence for one core};
  \node[hub] (ovl) at ($(pl.north)+(0,-2.85)$) {the overlay (DPU)};
  \draw[own] (tiles) -- (ovl);
  % ---- the bridge: the AXI ports, drawn once and labelled once ----
  \draw[black!45, densely dotted] (4.3,-2.3) -- (4.3,2.3);
  \node[tick, anchor=south] at (4.3,2.32) {the AXI ports};
  % ---- both crossings use the same bridge; they differ in frequency, not in direction, and the
  % ---- prose registers no direction, so the arrows only show traffic that pays the shared path ----
  \draw[bulk] (ddrc.east) -- node[lab, anchor=south] {weights: one bulk load, then residence} (ovl.west);
  \draw[strm] ($(ddrc.east)+(0,-0.42)$) -- node[lab, anchor=north]
    {activations: a new item every frame} ($(ovl.west)+(0,-0.42)$);
  % ---- the comparison the section turns on ----
  \node[lab, anchor=north] at ($(ps.south)+(0,-0.16)$) {everything the fabric reads\\lives behind the bridge};
  \node[lab, anchor=north] at ($(pl.south)+(0,-0.16)$) {only the tiles it is\\placed with are its own};
\end{tikzpicture}
```
The boundary as a picture rather than a paragraph: the memory controller and the DRAM that holds the
weights both sit on the processor side, and the fabric reaches them only through the AXI ports, so the
one heavy crossing is a bulk load made once and the light traffic is a stream that never stops. The
drawing adds no measurement -- the two populations and the sharing it shows are the records section 9.5
cites.
:::


[Figure 37](#fig-fabric-boundary) draws that sharing: the controller and the chips are on the far
side of one bridge, and the fabric reaches them only across it.

**The PS keeps one on-chip memory, and it is not fabric SRAM.** The data sheet prints 256 KB of on-chip memory (OCM -- storage fixed inside the device) with error-correcting codes, reachable from the PL over AXI; that row spans three device classes, so it is a family-level statement rather than a fact about this part alone. It is not fabric BRAM and it is not in the DPU's address space, so the registry keeps it out of any weight budget: latency-critical scratch, not model storage.

**Weights cross in bulk; activations cross in a stream.** A weight set is the same bytes every frame, so a design that streamed them would pay the shared, contended path again for nothing; one bulk load, then residence in the tiles the ladder below counts, spends that path once. Activations are the opposite case: a new item every frame period, forever, which is why they want a streaming interface. The protocol is AXI4-Stream and chapter 4 owns it; this section only marks which traffic gets which shape. The bytes one frame puts on the wire are not registered, so no size is claimed here.

**Four lanes at 12.5 Gb/s is the whole way out.** The silicon contains 16 GTH transceivers (serial lanes that move raw bits off the chip) rated 16.3 Gb/s at device level, but the SFVC784 and SFVE784 packages support up to 12.5 Gb/s, and the KV260's device -- an SFVC784 -- bonds out only 4 GTH lanes and no GTY. A link budget built on 16.3 Gb/s therefore describes a package the board does not have. That is the trap for a reader planning to hang an external accelerator off transceiver lanes; the outward input/output this kit actually carries is four USB 3.0 ports.

**The vendor ladder is the honest picture of what a tool costs.** The overlay's intellectual property is the DPUCZDX8G deep learning processing unit (DPU). Its guide has already lost one table: an earlier edition printed B4096 at 37,266 LUTs, 249.5 Block RAM and 642 DSPs, none of which appears in the edition this book reads, so that record is withdrawn as evidence and kept for the conflict. The replacement is explicit about its board: B4096 on a ZCU102 costs 52,161 look-up tables (LUT -- the basic logic element), 98,249 registers, 255 BRAM tiles and 710 DSP slices (the multiply-accumulate blocks); the same core buffering its weight stream in URAM instead uses no BRAM and 68 URAM tiles. Against the 144 BRAM and 64 URAM tiles of the ZU5EV, B4096 as tabulated fits neither variant, and DSP is the one resource with headroom, 710 of the fabric's 1,248.

| Rung | `V-04-10` BRAM tiles | `V-04-11` URAM tiles |
| --- | --- | --- |
| B512 | 72 | 18 |
| B800 | 90 | 40 |
| B1024 | 104 | 26 |
| B1152 | 121 | 44 |
| B1600 | 126 | 56 |
| B2304 | 165 | 60 |
| B3136 | 208 | 64 |
| B4096 | 255 | 68 |

The BRAM column climbs with the name; the URAM column does not -- B1024 uses 26 tiles where B800 uses 40
-- so no rung may be interpolated. [Figure 20](#fig-ch4-dpu-ladder) draws those two columns against this
device's two storage ceilings, so the crossing and the dip are geometry rather than arithmetic to redo; the
drawing is chapter 4's, because that is where the tiles themselves are defined, and the counts are the table
above unchanged. Fitting the ladder to this device is derived arithmetic, stated as such: B1600 is the largest BRAM core that fits, 126 tiles of 144, and the largest URAM core, B3136, fills 64 of 64 exactly and leaves nothing for the rest of the design, which makes B2304 the practical ceiling; even B1600 takes 38,418 of 117,120 LUTs, about a third of the device for one core. Which rung the factory image actually loads is a registered non-answer: no primary source, community files disagree, and the source note says documents cannot settle it.

**A does-not-fit report is a valid outcome.** The plan's second acceptance condition allows a measured word error rate (WER -- the fraction of reference words a recognizer gets wrong) *or* a report that the design does not fit, with the arithmetic shown, and counts the report as a result. The ladder above is what such a report is written against: "B4096 does not fit ZU5EV" is not a failed project, it is the registered fit verdict for that pairing. One operating assumption stays open: the Jetson model the plan compares against is recorded as a project choice still unresolved.

<!-- source: 9.6 reviewed fragment -->


**Traceability.** The records this section leans on. The 19.2 GB/s peak and the ladder-fit LUT counts are
derived; the sentence that uses each names it as derived, and the registered operands are in the rows below.

| Record | What it establishes here |
| --- | --- |
| `V-01-12` | the data sheet's verbatim memory line, 4 GB, 64-bit wide, 2400 Mb/s |
| `V-01-13` | the theoretical DRAM peak of 19.2 GB/s, derived from the bus width and rate |
| `V-01-14` | the DDRC sits on the PS and the PL reaches DRAM only through AXI -- no fabric-to-chip memory pins |
| `V-02-10` | the Jetson Orin Nano Super's registered memory bandwidth |
| `V-01-17` | 256 KB of error-corrected on-chip memory on the PS, reachable over AXI, a family-level row |
| `V-01-20` | GTH transceivers at 16.3 Gb/s device level, but 12.5 Gb/s on the 784 packages |
| `V-01-21` | this package bonds out 4 GTH and 0 GTY |
| `V-03-05` | the outward I/O this kit carries is four USB 3.0 ports |
| `V-04-03` | the overlay's DPU architecture is the DPUCZDX8G |
| `V-04-04` | an earlier guide table, withdrawn as evidence for the conflict it created |
| `V-04-07` | B4096 on a ZCU102: 52,161 LUT, 98,249 registers, 255 BRAM, 710 DSP |
| `V-04-08` | the same core buffering weights in URAM: 0 BRAM, 68 URAM |
| `V-04-09` | the verdict that B4096 as tabulated does not fit ZU5EV |
| `V-04-10`, `V-04-11` | the BRAM and URAM variant ladders the table above prints |
| `V-04-12` | the derived fit: B1600 largest for BRAM, B2304 the practical URAM ceiling |
| `V-04-13` | the shipped DPU core is unresolved: documents cannot settle which rung the image loads |
| `V-02-28` | the Jetson model the plan compares against, chosen but flagged unresolved |


## 9.6 Look-Ahead Is the Cheapest Accuracy on the Table

**One vendor drew the curve this chapter asks for.** A streaming model can wait for more audio before it commits a word, and that wait is **look-ahead**: the model hears the end of a sound as part of what comes after it. NVIDIA's English score table publishes four checkpoints of one streaming FastConformer family at four amounts of that future, all read on the test-other split of the English LibriSpeech corpus. Word error rate (WER -- the share of reference words the system gets wrong) falls as the wait grows: 7.0 per cent with none of it, 6.4 at a short 80 ms wait, 5.7 at 480 ms, and 5.4 at the full 1040 ms. [Figure 38](#fig-lookahead-accuracy) puts the four on axes, and the traceability table at this section's end names the record behind each point.

::: {#fig-lookahead-accuracy .figure}
```tikz
% Coordinates: x is look-ahead in hundreds of milliseconds, y is test-other WER in per
% cent. Each plotted pair is the number a record prints, V-05-52 to V-05-55, plus the
% second value the same table carries for the far setting, V-05-49.
\begin{tikzpicture}[
  x=0.9cm, y=2.4cm,
  curve/.style={blue!55!black, thick},
  ceil/.style={red!65!black, thick, densely dashed},
  dot/.style={circle, inner sep=1.3pt, fill=blue!55!black},
  oth/.style={circle, inner sep=1.3pt, draw=blue!55!black, thick, fill=white},
  t/.style={font=\scriptsize, inner sep=2pt},
]
\def\yb{5.0}
\def\yt{7.45}
\def\xr{11.6}

% Grid at the published positions, so the uneven spacing is visible without reading numbers.
\foreach \y in {5.5,6.0,6.5,7.0} {\draw[gray!22] (0,\y) -- (\xr,\y);}
\foreach \x in {0.8,4.8,10.4} {\draw[gray!22] (\x,\yb) -- (\x,\yt);}
\draw[-Stealth] (0,\yb) -- (\xr,\yb);
\draw[-Stealth] (0,\yb) -- (0,\yt);
\foreach \y in {5.0,5.5,6.0,6.5,7.0} {\node[t, left] at (0,\y) {\y};}
% The same four points, counted the other way: attention steps of right context.
\foreach \x/\ms/\st in {0/0/0, 0.8/80/1, 4.8/480/6, 10.4/1040/13} {
  \node[t, below] at (\x,\yb) {\ms};
  \node[t, below=10pt] at (\x,\yb) {\st};
}
\node[below=26pt, font=\small] at (\xr/2,\yb) {look-ahead, ms \penalty0 (right context, attention steps)};
\node[rotate=90, above=26pt, font=\small] at (0,{(\yb+\yt)/2}) {test-other WER, \%};

% The offline Small row, on the same column of the same corpus, at a different size.
\draw[ceil] (0,6.6) -- (11.0,6.6);
\node[t, ceil, anchor=south west] at (5.9,6.62) {offline Small, V-05-51, 14M params V-05-16};

\draw[curve] (0,7.0) -- (0.8,6.4) -- (4.8,5.7) -- (10.4,5.4);
\node[dot, label={[t]above right:V-05-52}] at (0,7.0) {};
\node[dot, label={[t]right:V-05-53}] at (0.8,6.4) {};
\node[dot, label={[t]above right:V-05-54}] at (4.8,5.7) {};
\node[dot, label={[t]below right:V-05-55}] at (10.4,5.4) {};
\node[oth, label={[t]above right:V-05-49}] at (10.4,5.5) {};

\draw[gray!60,-Stealth] (2.55,7.05) -- (0.5,6.82);
\node[t, anchor=south west, text width=3.5cm, align=left] at (2.6,7.0)
  {one encoder step of future audio: the steepest segment on the plot};
\end{tikzpicture}
```
The only accuracy-against-latency curve a publisher draws for this family, which is why the design question is where to sit on it. Read from the left: the first published step is the steepest thing there is, the open circle is the table's second value for the far setting, and the dashed line belongs to a smaller model, so it marks a size mismatch rather than a ceiling.
:::

**The knob is an integer, not a feeling.** Each streaming recipe publishes a pair, `att_context_size: [left, right]`, and the right element is how many attention steps of future audio the model is allowed to see: 27 for the cache-aware streaming Conformer, 13 for the cache-aware streaming FastConformer. A step is a fixed slice of time, because the encoder subsamples the feature stream: a 0.01 s feature stride times a factor of four is 40 ms per step, and the same stride times a factor of eight is 80 ms. Multiplying gives the wait, and both products land on numbers the records print themselves: 27 steps of 40 ms is the 1080 ms published for the Conformer, and 13 steps of 80 ms is the 1040 ms published for the FastConformer. That second product is the right end of [Figure 38](#fig-lookahead-accuracy), and 13 is the first entry of a list on the same config line, `[[70,13],[70,6],[70,1],[70,0]]`, whose remaining entries are the other three points. The curve is one list read four times, not four architectures. Each figure above is a registered operand or a product of them; the table at this section's end names the record for each.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Encoder step, streaming Conformer | 40 ms | derived: stride 0.01 s `V-05-31`, `V-05-45` × factor 4 `V-05-32` |
| Encoder step, streaming FastConformer | 80 ms | derived: `V-05-45` × factor 8 `V-05-42` |
| Look-ahead, streaming Conformer | 1080 ms | derived: 27 steps `V-05-30` × 40 ms; printed by `V-05-34` |
| Look-ahead, streaming FastConformer | 1040 ms | derived: 13 steps `V-05-44` × 80 ms; printed by `V-05-47` |
| Left context, both recipes | 5600 ms | derived: 140 steps `V-05-29` × 40 ms, and 70 steps `V-05-43` × 80 ms |

**Left context is a second knob, and the two recipes do not trade it.** The two recipes spend different numbers of steps and land on the same span of the past: derived from the two recipes' registered left contexts, both are 5600 ms of audio. One is a slower encoder holding fewer steps, the other a faster encoder holding more. Note too that the pair is not free of each other: the streaming Conformer's own record notes that in the mode its config uses, the left element must divide by the right element plus one, and 140 / (27 + 1) is 5 exactly. Buying future audio can therefore cost past audio, and no registered source prices that second trade.

**The shape is the argument.** The publisher's note on the far point of the curve prices the whole run at 1.6 points of error, and [Figure 38](#fig-lookahead-accuracy) shows where those points are earned: nearly all of the slope sits inside the first step, and the two published settings beyond 480 ms differ by less than the first two do while being many times further apart on the axis. So the design question is placement, not completion. The far end of the curve is not a goal; it is a second of waiting, which is a large thing to ask of a system whose frontend was given a frame deadline in single-digit milliseconds.

**Mark what the curve cannot carry.** It is one family, in English, on one corpus, at one size: about 115 million parameters for the streaming FastConformer, against about 120 million for the other streaming large recipe. The clean-split counterpart of the same family at its longest setting prints 2.3 per cent while its test-other cell prints 5.5, and the offline row the streaming model is asked to approach prints 2.5 and 6.6 -- but that offline pair belongs to the Small variant at about 14 million, so it is not size-matched, and the streaming row is the lower of the two on both columns. There is no offline large row registered here, so the ceiling this comparison wants is missing rather than won. Two smaller limits: only the test-other column is filled for the four curve points, so the curve cannot be drawn on the clean split at all, and the same operating point carries both 5.4 and 5.5 per cent, which sets the reading precision of this table. A WeNet streaming row prints 3.80 and 4.54 per cent under its two decoding modes, on test-clean at a chunk of 16 frames, which is 640 ms: a different column, a different framework, and a comparison between documents, not a controlled experiment.

**This section decides nothing about hardware.** Cost per byte belongs to chapter 3 and the Pareto frontier belongs to chapter 10. The two ridge-point records -- 490.2 operations per byte for an Orin NX, and 39.0 to 78.0 for a KV260 -- are cited here for orientation only, and the FPGA pair rests on a fabric clock its own source note marks as an assumption. Look-ahead changes how long a frame waits; no record in this section says what it changes about the bytes a frame moves, and this book will not guess.

**Traceability.** The records behind this section's figures. The four curve points, the step durations and
the look-ahead products are named by the paragraph that uses them; each row below is the record for the
figures in this section.

| Record | What it establishes here |
| --- | --- |
| `V-05-30`, `V-05-44` | the streaming Conformer and FastConformer right contexts, 27 and 13 attention steps |
| `V-05-31`, `V-05-45` | the 0.01 s feature stride shared by both recipes |
| `V-05-32`, `V-05-42` | the subsampling factors, four and eight, that turn a stride into a step |
| `V-05-34`, `V-05-47` | the two published look-aheads, 1080 ms and 1040 ms, that the step products land on |
| `V-05-29`, `V-05-43` | the left contexts, 140 and 70 steps, that derive to the same five-and-a-half-second span |
| `V-05-52`, `V-05-53`, `V-05-54`, `V-05-55` | the four test-other curve points, 7.0, 6.4, 5.7 and 5.4 per cent |
| `V-05-48`, `V-05-49` | the same family at its longest setting, on the clean split and the test-other split |
| `V-05-50`, `V-05-51` | the offline Small row, 2.5 and 6.6 per cent, that the streaming row is compared to |
| `V-05-16`, `V-05-33`, `V-05-46` | the parameter counts, 14 million Small, 120 million Conformer, 115 million FastConformer |
| `V-05-06` | a WeNet streaming row on a different split, decoding modes and chunk size |
| `V-07-02`, `V-07-03` | the two roofline ridge points, cited for orientation only, the FPGA one on an assumed clock |
