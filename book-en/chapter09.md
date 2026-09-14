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

---

<!-- source: 9.1 reviewed fragment -->

## 9.1 The Target, and What Is Still Undecided About It

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

**The convolution tap count is a fork, not a family property.** A depthwise convolution is a sliding window over the recent frames of one hidden stream, so the tap count sets how far back that window reaches and how much history has to be held beside it. The readings disagree in a way that a hardware designer cannot route around: the offline Conformer-Transducer Small keeps **31** taps (`V-05-15`), so does the cache-aware streaming Conformer-Transducer Large (`V-05-25`), the streaming FastConformer cuts the same window to **9** (`V-05-40`), and the other framework in this table publishes **15** (`V-05-04`). An overlay sized for one of those windows is not an overlay sized for the other, and the shorter window is the reason the FastConformer variant is called fast rather than a detail of its recipe. The second structural field is registered for three of the six readings and not for the rest: the offline Conformer-Transducer Large feeds its convolution module through batch normalisation (`V-05-20`), while both streaming NeMo readings use layer normalisation (`V-05-26`, `V-05-41`), and no record here prints a value for either Small row or for the WeNet row. A reader who needs the difference between those two normalisations explained should read section 8.3, where the arithmetic of each one on a device with no floating-point unit is the subject rather than a config field.

**Hidden width decides what a head slice costs.** 512 units across 8 heads (`V-05-18`, `V-05-19`) divides by a power of two, so at that width a head index is a shift and a head slice is a byte range. 176 units across 4 heads (`V-05-13`, `V-05-14`) does not, and neither shortcut is available for that reading.

**The two streaming candidates reach the evidence only as weight counts** — about 120 million (`V-05-33`) and about 115 million (`V-05-46`), both rounded by their publisher rather than counted, against the small offline model's about 14 million (`V-05-16`). Put those beside the fabric this book targets: 117,120 look-up tables, 144 block RAM (BRAM -- on-chip storage) blocks, 64 UltraRAM (URAM) blocks and 1,248 multiply-accumulate slices on the device column registered for this board (`V-01-15`), with 23,616 Kb of BRAM and URAM together, a figure that record itself unrolls to 2,952 KiB (`V-01-22`). The difference in scale needs no arithmetic to see. What cannot be seen is what each weight costs to hold, and that is a registered gap rather than an omission: no multiply-accumulate (MAC) count per frame, no 8-bit integer (INT8) weight bytes and no activation bytes per frame exist for any candidate (`V-05-57`). So this chapter describes a datapath and sizes nothing in bytes, and no parameter count in this section is ever converted into one.

**Two frameworks disagreeing about a model's size is a fact about frameworks.** The WeNet reading carries published accuracy where the NeMo readings here do not: at chunk size 16, which that record turns into 640 ms on its own stated basis of 40 ms per feature frame (`V-05-05`), it reports 3.80% word error rate (WER) with attention rescoring and 4.54% with connectionist temporal classification (CTC) beam search (`V-05-06`). The same record states that right-away and future-context latency in milliseconds remain unverified for that checkpoint, and that the 640 ms is arithmetic on a published chunk size. A reader should conclude that no single registered reading supplies both a shape and an accuracy, so a sentence of the form "the Conformer needs this much and scores that" is not available yet. The fourth model the spine names is worse off still: the search for a checkpoint that is at once Conformer-Transducer, streaming and Small is registered and its answer is not (`V-05-56`), and the English score table for the family was read in full without producing such a row. That phrase therefore carries no published accuracy, which is the split this chapter inherits rather than resolves. Per-step timing for the two streaming candidates is likewise not printed in this section, so no context depth in milliseconds is derived from it here either.

<!-- source: 9.2 reviewed fragment -->

## 9.2 One Conformer Block, Drawn as a Datapath

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

Those columns are candidates, not a settled number. `V-05-12` is the Small row of a table in a config header, read against the body below it, and `V-05-04` describes another toolkit's model; the target is undecided, so the block count stays a set.

Two keys are read before any block runs. The stride 0.01 s `V-05-31` at the factor 4 `V-05-32` gives 40 ms for one encoder step, and the same product with `V-05-45` and `V-05-42` gives 80 ms; both are derived here by multiplying the two records named. That step period is the clock the block chain runs on. Beside `V-05-25` the same file sets `conv_context_size` causal, and its own comment says causal means the pair [kernel_size-1, 0]: every tap looks backwards, which is what lets this convolution be built as a shift register with the taps hanging off it.

**The normalisation key is a datapath decision, not a style preference.** The comment printed beside `V-05-20` lists three answers: `batch_norm`, `layer_norm`, or a grouped variant. BatchNorm's number for a channel comes from statistics stored while training, so at inference it is a scale and a shift per channel, and a scale and a shift can be pushed backwards into the depthwise weights around it: the stage is deleted, and the design inherits a table of stored per-channel values it must keep and apply. LayerNorm's number comes from the frame arriving right now -- a mean, a variance, a reciprocal square root per step, computed at runtime -- so it folds into nothing and has to be built as a unit of its own, with a reduction across `d_model`. The offline Large config prints `batch_norm` `V-05-20`; the two streaming configs both print `layer_norm` `V-05-26`, `V-05-41`. A target that normalises this way inside the block keeps a data-dependent stage; one that does not can remove it and must carry the statistics instead. The position scheme is the other arithmetic choice: `rel_pos` `V-05-21`, `V-05-27` scores a pair of steps by the gap between them, which a table of gaps can hold, while the comment names `abs_pos` as the alternative that indexes position in the window. The decomposition behind relative position is quoted by no record here, so the book notes the choice and stops.

**An expansion factor is a ratio, and reading it as a stage count is a factor-of-four error.** `V-05-36` prints 4, where `V-05-04` prints the same stage's width outright as 2048 units, its own comment calling it the number of units of position-wise feed forward. Two files, two shapes of the same idea, so a reader has to know which one they are holding. Worse, `ff_expansion_factor` 4 `V-05-36` and `subsampling_factor` 4 `V-05-32` are the same digit doing unrelated jobs: one widens a stage, the other collapses time. Take the first as four stages and every per-block total downstream grows by four, and a rounding chain carries that multiplier into the bit widths chosen after it.

**What the registry does not tell you is the block's shape.** No record quoted here prints how many sub-layers sit inside one block, or in what order. Those come from the architecture's definition and from the code implementing it, which a config file has no reason to repeat. So [Figure 8](#fig-conformer-block) draws the sub-layers as the book's working assumption and says so in the picture: the keys inside the boxes are what a record prints, the wires joining them are not. Nothing in this section is a per-frame cost either, because none is registered.

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

<!-- source: 9.3 hand -->

## 9.3 Attention Inside a Chunk, With Position Measured Rather Than Absolute

**Intuition.** Attention lets one frame of audio ask the other frames a question, and the only
engineering problem it creates is that the asking has to be bounded. In words a hardware reader
already has: a frame forms a query, compares it against the key of every frame it is allowed to
see, and takes a weighted average of their values, where the weights come from how well the query
matched each key. Nothing about that is special to speech. What is special here is that the
microphone is still running: most of the frames a finished utterance would offer do not exist
yet, and the frames that do exist cannot be kept indefinitely. So the design must decide, once and
in hardware, which frames exist for the network to read at all. Appendix A explains the query, key
and value machinery from the beginning; this section is about the boundary around it.

**Mechanism.** Streaming attention is not one of the two shapes a reader already knows. Full attention lets every frame see every other frame of an utterance, which is what an offline encoder does and what a chip receiving audio as it arrives cannot do, because the later frames do not exist yet. A plain sliding window lets a frame see a fixed number of earlier steps and nothing else, which is the recurrent shape: it streams, and it also deletes the future that the model was trained to use. Cache-aware streaming attention is a third thing. The registered name for it is `chunked_limited` `V-05-28`, and in that mode a frame attends in both directions inside its own chunk and to a bounded number of earlier chunks -- so the mask is not a stripe of recent steps but a band: the current chunk complete, plus a left context counted in frames the design has already finished.

**Both sides of that band are registered, for both streaming candidates.** The cache-aware streaming Conformer-Transducer publishes `att_context_size: [140, 27]` `V-05-29`, `V-05-30`: one hundred forty steps behind and twenty-seven ahead, where a step is one encoder frame after subsampling, so 40 ms apart for this variant. The FastConformer publishes `[70, 13]` `V-05-43`, `V-05-44` at a step 80 ms wide, the same depth of block `V-05-37` and the same width `V-05-38`. The two pairs are the same shape, and the reason they differ is worth stating precisely because it is easy to read as a smaller model: seventy steps at 80 ms reaches back as far in seconds as one hundred forty at 40 ms, and it does so with half as many cached frames. That trade is what the FastConformer is built to make.

**A strict causal mask is the wrong tool here, not a stricter version of the right one.** A causal mask is a triangle: it keeps the diagonal and everything to its left, and it deletes every future position, which is exactly the twenty-seven and thirteen steps above. A chunk mask keeps the future inside the current chunk, because that future is already in hand -- the design waits for a chunk of audio before it computes anything -- and across chunks it keeps only as much past as the cached context can supply. Set the right context to zero and a chunk mask becomes a causal one, so the two differ by one parameter rather than by a family of ideas. The cost of doing so is not a small loss of accuracy. It removes the look-ahead the recipe configures on purpose, and a checkpoint trained with a nonzero right context has been trained to read those positions.

**Position enters as a distance rather than as an index.** Both the offline large reading and the streaming one register `rel_pos` `V-05-21`, `V-05-27`, which the registry identifies as the Transformer-XL scheme, and what it is for is this: a token's position changes a score only through how far it sits from the token being scored. That property is what lets a cached chunk keep meaning after newer chunks arrive. A score built from absolute indices is only correct while the indices in the cache are the ones the model saw during training, so a rolling buffer would have to be recomputed each time the buffer slides. A score built from distances stays correct at any wall-clock moment, because the distance between two frames is the same whether they are the first frames of an utterance or the last. How a relative score is composed from its terms is not quoted anywhere in this registry, so this section says what the scheme is for and does not present a sum as fact.

**Hardware application.** The cached quantity scales with the hidden width, not with the head count. What the overlay keeps per cached step is a key vector and a value vector for each head, and each has the length of one head: the hidden width divided by the number of heads, which is 64 for the large readings at 512 units and 8 heads `V-05-18`, `V-05-19`, `V-05-23`, `V-05-24`, `V-05-38`, `V-05-39`, and 44 for the small reading at 176 units and 4 heads `V-05-13`, `V-05-14`. Multiply by the head count to get a total per step and the answer is the hidden width again, so doubling the heads at fixed width leaves the cache exactly as large and makes every head narrower. The two keys move together in a config file and not at all in a budget.

**One contrast from the other framework, so the shape above is not mistaken for a convention.** WeNet's recipe sets its chunk at 16 frames, which is 640 ms of audio at the same 40 ms per frame `V-05-05`, and its encoder is 12 blocks of 256 units with 4 heads `V-05-04`. A longer chunk is not a different attention regime. It is the same band with a wider current block, and it buys that width in exactly the currency chapter 8 counts. [Figure 9](#fig-attention-regimes) sets the three masks beside one another, on the same five frames, so the difference between them is a shape rather than a description.

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
geometry, not the registered pairs: the numbers a reader would design with are 140 and 27
`V-05-29`, `V-05-30` for one streaming candidate and 70 and 13 `V-05-43`, `V-05-44` for
the other, both far wider than a grid can show.
:::

<!-- source: 9.4 reviewed fragment -->

## 9.4 The Left-Context K/V Ring Buffer

**Intuition.** A reader who has written a first-in first-out queue has already built the object
this section is named for. Attention needs the frames before the current one, the number of frames
it is allowed to need is fixed by the recipe, and a fixed number of frames is a fixed amount of
storage. So the past is not a list that grows: it is a circle of slots, and a new chunk is written
into the slot that holds the oldest one. Nothing is shifted and nothing is freed, because the write
position returns to the start of the circle by construction. The engineering questions are the two
a designer always asks about a queue: how deep it has to be, and what that depth costs. Appendix A
explains why it is the key and value tensors that have to persist and why the query does not; this
section sizes the storage and names what is still unregistered about it.

**The borrowed name promises the wrong object.** Self-attention -- the part of the encoder where a frame looks at other frames, not only at its neighbours -- reads two tensors per frame, a key and a value, written K and V. The phrase "KV-cache" arrived from large language models (LLMs -- text generators that emit one token at a time), and the inheritance is a trap. An LLM cache grows with everything the model has produced, because its own output is what it must keep attending to, and no bound is set from outside. What this encoder needs is the opposite shape: a bounded window of earlier chunks that a fixed number of entries hold, each overwritten in turn. The name invites a reader to expect growth that never happens. So the project plan renames it the **Left-Context K/V Ring Buffer**, and the four words are the four properties that matter: only the past, both tensors, a write position that wraps, a fixed circle of slots. That rename is the plan's decision on the record, not a measurement.

**Mechanism.** The capacity is a product, and half of it is registered. The plan writes the entry count as chunks kept $\times$ chunk length $\times$ head width $\times$ heads $\times$ two, for keys and values $\times$ bytes per element. Two pairs of those terms collapse. Heads times head width is the hidden width $d_\text{model}$, the length of the feature vector one frame carries, and chunks kept times chunk length is the retained span in steps $T_\text{left}$. What is left is

$$N_\text{ring} = T_\text{left} \times d_\text{model} \times 2 \times b$$

with $b$ the number of bytes each stored value occupies. There the chapter stops: the bytes a frame occupies are unregistered (`V-05-57`), and this book prints no value for them. What sources do fix is $T_\text{left}$ and $d_\text{model}$, and they are worth holding side by side because the choice of target model is still open.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Audio feature stride | 0.01 s, both recipes | `V-05-31`, `V-05-45` |
| Encoder subsampling factor | 4 (Conformer), 8 (FastConformer) | `V-05-32`, `V-05-42` |
| Left context, as configured | 140 steps (Conformer), 70 steps (FastConformer) | `V-05-29`, `V-05-43` |
| Right context, as configured | 27 steps (Conformer), 13 steps (FastConformer) | `V-05-30`, `V-05-44` |
| Hidden width $d_\text{model}$ | 512 units, both streaming large configs | `V-05-23`, `V-05-38` |
| Attention context style | `chunked_limited` | `V-05-28` |

The same recipe family prints 176 for the Small Conformer row `V-05-13` and 512 for the offline Large `V-05-18`, so the ring is sized against the published shapes and not against a chosen model.

**Size the ring in seconds, not in steps.** The two recipes disagree about steps and agree about time. Multiplying each stride by its factor -- derived, from `V-05-31` with `V-05-32`, and from `V-05-45` with `V-05-42` -- one encoder step is 40 ms for the streaming Conformer and 80 ms for the streaming FastConformer. Multiplying each left context by its own step time -- derived, from `V-05-29` with the 40 ms just named, and from `V-05-43` with the 80 ms -- gives 5600 ms both ways. So `chunked_limited` `V-05-28` describes the same span of wall-clock past under two different step counts, and an entry count written in steps silently rescales when the recipe changes. A ring sized in seconds carries one requirement across both candidates; the frame period is also the unit every deadline in this book is written in. The step count is not free, either: it is what the block and tile arithmetic of chapter 8 consumes.

**Hardware application.** The container is registered; the contents are not. The device the plan targets holds 144 block RAM (BRAM -- on-chip storage) blocks `V-01-05` and 64 UltraRAM (URAM) blocks `V-01-07`, with `V-01-23` fixing the tiles at 36 Kb and 288 Kb and stating that the datasheet's Mb columns are 1024-based, which is the reading behind its printed `UltraRAM (Mb): 18.0` `V-01-08`. Together `V-01-22` prints 23,616 Kb and unrolls its own unit chain, because that record exists precisely to show that two different totals were each defensible under some reading of a unit. No figure here is converted.

[Figure 10](#fig-kv-ring-buffer) is the object the section is named for.

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

<!-- source: 9.5 reviewed fragment -->

## 9.5 The Fabric Boundary: What the ARM Side Keeps

**The overlay does not own its memory.** The DDR4 memory controller (DDRC -- the logic that drives the external chips) sits on the processor system (PS -- the fixed ARM cores), and the programmable logic (PL -- the fabric an overlay configures) reaches DRAM only through the AXI ports between the two sides (AXI -- the on-chip interconnect protocol of this family); there are no memory pins from fabric to chips (`V-01-14`). The memory behind those ports is what the datasheet quotes verbatim, "4 GB 64-bit wide, 2400 Mb/s" (`V-01-12`), and the registry derives its theoretical peak, 19.2 GB/s, from that bus width and rate -- an arithmetic figure the source never prints (`V-01-13`). Achievable bandwidth sits below the peak, because the fabric shares the controller, and its quality-of-service priorities, with the processors. An accelerator's view of DRAM is therefore a second-order question on this board: the first-order fact is the sharing. The record the FPGA is being compared against prints 102 GB/s for the Jetson Orin Nano Super (`V-02-10`), and no sentence here should be allowed to hide that gap.

**The PS keeps one on-chip memory, and it is not fabric SRAM.** The datasheet prints 256 KB of on-chip memory (OCM -- storage fixed inside the device) with error-correcting codes, reachable from the PL over AXI; the row spans three device classes, so it is a family-level statement rather than a fact about this part alone (`V-01-17`). It is not fabric BRAM and it is not in the DPU's address space, so the registry keeps it out of any weight budget: latency-critical scratch, not model storage.

**Weights cross in bulk; activations cross in a stream.** A weight set is the same bytes every frame, so a design that streamed them would pay the shared, contended path again for nothing; one bulk load, then residence in the tiles the ladder below counts, spends that path once. Activations are the opposite case: a new item every frame period, forever, which is why they want a streaming interface. The protocol is AXI4-Stream and chapter 4 owns it; this section only marks which traffic gets which shape. The bytes one frame puts on the wire are not registered, so no size is claimed here.

**Four lanes at 12.5 Gb/s is the whole way out.** The silicon contains 16 GTH transceivers (serial lanes that move raw bits off the chip) rated 16.3 Gb/s at device level, but the SFVC784 and SFVE784 packages support up to 12.5 Gb/s (`V-01-20`), and this package bonds out 4 GTH and 0 GTY (`V-01-21`). The KV260's device is marked SFVC784, so a link budget built on 16.3 Gb/s describes a package the board does not have. That is the trap for a reader planning to hang an external accelerator off transceiver lanes; the outward I/O this kit actually carries is four USB 3.0 ports (`V-03-05`).

**The vendor ladder is the honest picture of what a tool costs.** The overlay IP is the DPUCZDX8G DPU (deep learning processing unit) (`V-04-03`). Its guide has already lost one table: the v3.0 edition printed B4096 at 37,266 LUTs, 249.5 Block RAM and 642 DSPs, none of which appears in v4.1, so the record is withdrawn as evidence and kept (`V-04-04`, conflict). The replacement is explicit about its board: B4096 on a ZCU102 costs 52,161 look-up tables (LUT -- the basic logic element), 98,249 registers, 255 Block RAM (BRAM -- 36-kilobit storage tiles) and 710 DSP slices (the multiply-accumulate blocks) (`V-04-07`); the same core buffering in UltraRAM (URAM) instead uses 0 BRAM and 68 URAM tiles (`V-04-08`). Against the 144 BRAM and 64 URAM tiles of ZU5EV, B4096 as tabulated fits neither variant, and DSP is the one resource with headroom, 710 of 1,248 (`V-04-09`).

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

The BRAM column climbs with the name; the URAM column does not -- B1024 uses 26 tiles where B800 uses 40 -- so no rung may be interpolated (`V-04-11`). Fitting the ladder to this device is derived arithmetic, stated as such: B1600 is the largest BRAM core that fits, 126 tiles of 144, and the largest URAM core, B3136, fills 64 of 64 exactly and leaves nothing for the rest of the design, which makes B2304 the practical ceiling; even B1600 takes 38,418 of 117,120 LUTs, about a third of the device for one core (`V-04-12`). Which rung the factory image actually loads is a registered non-answer: no primary source, community files disagree, and the record says documents cannot settle it (`V-04-13`).

**A does-not-fit report is a valid outcome.** The plan's second acceptance condition allows a measured word error rate (WER -- the fraction of reference words a recognizer gets wrong) *or* a report that the design does not fit, with the arithmetic shown, and counts the report as a result. The ladder above is what such a report is written against: "B4096 does not fit ZU5EV" is not a failed project, it is `V-04-09`. One operating assumption stays open: the board power configuration the plan compares against (`V-02-28` is the Jetson model; the project choice there is unresolved).

<!-- source: 9.6 reviewed fragment -->

## 9.6 Look-Ahead Is the Cheapest Accuracy on the Table

**One vendor drew the curve this chapter asks for.** A streaming model can wait for more audio before it commits a word, and that wait is **look-ahead**: the model hears the end of a sound as part of what comes after it. NVIDIA's English score table publishes four checkpoints of one streaming FastConformer family at four amounts of that future, all read on the test-other split of the English LibriSpeech corpus. Word error rate (WER -- the share of reference words the system gets wrong) falls as the wait grows: 7.0 per cent with none of it `V-05-52`, 6.4 at 80 ms `V-05-53`, 5.7 at 480 ms `V-05-54`, and 5.4 at 1040 ms `V-05-55`. [Figure 11](#fig-lookahead-accuracy) puts the four on axes.

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

**The knob is an integer, not a feeling.** Each streaming recipe publishes a pair, `att_context_size: [left, right]`, and the right element is how many attention steps of future audio the model is allowed to see: 27 for the cache-aware streaming Conformer `V-05-30`, 13 for the cache-aware streaming FastConformer `V-05-44`. A step is a fixed slice of time, because the encoder subsamples the feature stream: 0.01 s of features `V-05-31`, `V-05-45` times a factor of 4 `V-05-32` is 40 ms per step, and the same stride times a factor of 8 `V-05-42` is 80 ms. Multiplying gives the wait, and both products land on numbers the records print themselves: 27 steps of 40 ms is the 1080 ms of `V-05-34`, and 13 steps of 80 ms is the 1040 ms of `V-05-47`. That second product is the right end of [Figure 11](#fig-lookahead-accuracy), and 13 is the first entry of a list on the same config line, `[[70,13],[70,6],[70,1],[70,0]]`, whose remaining entries are the other three points `V-05-44`. The curve is one list read four times, not four architectures.

| Quantity | Value | Where it comes from |
| --- | --- | --- |
| Encoder step, streaming Conformer | 40 ms | derived: stride 0.01 s `V-05-31`, `V-05-45` × factor 4 `V-05-32` |
| Encoder step, streaming FastConformer | 80 ms | derived: `V-05-45` × factor 8 `V-05-42` |
| Look-ahead, streaming Conformer | 1080 ms | derived: 27 steps `V-05-30` × 40 ms; printed by `V-05-34` |
| Look-ahead, streaming FastConformer | 1040 ms | derived: 13 steps `V-05-44` × 80 ms; printed by `V-05-47` |
| Left context, both recipes | 5600 ms | derived: 140 steps `V-05-29` × 40 ms, and 70 steps `V-05-43` × 80 ms |

**Left context is a second knob, and these records do not trade it.** The two recipes spend different numbers of steps and land on the same span of the past: derived from `V-05-29` and `V-05-43`, both are 5600 ms of audio. One is a slower encoder holding fewer steps, the other a faster encoder holding more. Note too that the pair is not free of each other: `V-05-30` records that in the mode its config uses, the left element must divide by the right element plus one, and 140 / (27 + 1) is 5 exactly. Buying future audio can therefore cost past audio, and no record on the allowlist prices that second trade.

**The shape is the argument.** The publisher's own note on `V-05-55` prices the whole run of the curve at 1.6 points of error, and [Figure 11](#fig-lookahead-accuracy) shows where those points are earned: nearly all of the slope sits inside the first step, and the two published settings beyond 480 ms differ by less than the first two do while being many times further apart on the axis. So the design question is placement, not completion. The far end of the curve is not a goal; it is a second of waiting, which is a large thing to ask of a system whose frontend was given a frame deadline in single-digit milliseconds.

**Mark what the curve cannot carry.** It is one family, in English, on one corpus, at one size: about 115 million parameters for the streaming FastConformer `V-05-46`, against about 120 million for the other streaming large recipe `V-05-33`. The clean-split counterpart of the same family at its longest setting prints 2.3 `V-05-48` while its test-other cell prints 5.5 `V-05-49`, and the offline row the streaming model is asked to approach prints 2.5 `V-05-50` and 6.6 `V-05-51` -- but that offline pair belongs to the Small variant at about 14 million `V-05-16`, so it is not size-matched, and the streaming row is the lower of the two on both columns. There is no offline large row registered here, so the ceiling this comparison wants is missing rather than won. Two smaller limits: only the test-other column is filled for the four curve rows `V-05-52`, so the curve cannot be drawn on the clean split at all, and the same operating point carries both 5.4 `V-05-55` and 5.5 `V-05-49`, which sets the reading precision of this table. The WeNet streaming row `V-05-06` prints 3.80 and 4.54 per cent under its two decoding modes, on test-clean at a chunk of 16 frames, which is 640 ms: a different column, a different framework, and a comparison between documents, not a controlled experiment.

**This section decides nothing about hardware.** Cost per byte belongs to chapter 3 and the Pareto frontier belongs to chapter 10. The two ridge-point records, 490.2 OP/byte for an Orin NX `V-07-02` and 39.0 to 78.0 for a KV260 `V-07-03`, are cited here for orientation only, and the FPGA pair rests on a fabric clock its own note marks as an assumption. Look-ahead changes how long a frame waits; no record in this section says what it changes about the bytes a frame moves, and this book will not guess.
