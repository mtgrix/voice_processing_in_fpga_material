```{=latex}
\appendix
```

# Model Fundamentals: The Forward Pass in Hardware Terms

> *Objective: Give a reader who knows logic, clocks and memory the machine-learning ideas the rest of the book uses without teaching them: what a step and a hidden width are, what one encoder block does in what order, how self-attention reads the past and why its scores are scaled, how a convolution does a similar job far more cheaply, what a normalising stage protects, and how any of those becomes a count of bytes. The forward pass only. No training mathematics appears anywhere in this appendix.*

<!-- Authoring note, for whoever edits this file next. The evidence scanner of Issue #59 reads every
     numeric token in prose and requires the same section to cite a claim that carries it, and it
     strips a cross-reference only in the singular form: "section 9.4" and "chapter 8" disappear,
     while "chapters 8 and 9" leaves the digits behind and fails the gate. Write one noun per
     reference. The same rule is why this file's own sections are named by subject rather than by
     number in running text: "A.3" on a line is read as the token 3. Issue #57 is the report this
     appendix answers, and Issue #59 is the gate that keeps its prose honest. -->

This appendix exists because the book assumed knowledge it never taught. Chapter 8 and chapter 9 use
attention, softmax, a key/value cache and a depthwise convolution as though every reader arrived
carrying them, and a reader who can read a Verilog state machine but has never opened a transformer
paper had to take each shape on trust. That is the defect this appendix exists to close, and this file is
its fix: every idea the book needs is stated once here at the level a first meeting requires, in the
book's three orders -- an intuition in plain words, then the mechanism with its symbols, then the
consequence for a piece of silicon.

Nothing here repeats a chapter's argument. The chapters keep their measurements, their disagreements
between sources, and their sizing arithmetic; this appendix keeps the definitions those arguments are
about. The reading order follows the chain of ideas rather than the chapter numbers: what travels
through the model, what a block does, how attention reads the past, how a convolution reads it
cheaper, what keeps the numbers in range, and finally how a dimension becomes a budget.

## A.1 What Travels Through the Model

**Intuition.** A microphone does not hand a model an object; it hands it a process that has not
finished. The process is cut into short frames, each frame is turned into a fixed-length list of
numbers, and the model is a chain of stages that each take such lists in and give such lists back.
Two quantities describe everything that moves. The first is *how many numbers travel together*, which
the literature calls the **hidden width** and a config file calls `d_model`. The second is *how many
such lists a stage sees at once*, which is a length of the encoder's own past and future. A hardware
reader should hold onto the correspondence now, because the whole appendix leans on it: a hidden
width is a bus width, and a count of lists is a memory depth.

**Mechanism.** Write one step as a vector $x_t$ with $d_{\text{model}}$ entries, and the block's input
as the sequence $X = (x_1, \ldots, x_T)$, where $t$ indexes time and $T$ is how many steps one pass
covers. Every stage this appendix describes has the same outer shape:

$$f:\ \mathbb{R}^{T \times d_{\text{model}}} \ \longrightarrow\ \mathbb{R}^{T \times d_{\text{model}}}$$

that is, a stage takes a width by a depth and returns the same width by the same depth. That invariance
is not a detail. It is why the block can be repeated at all: any stage may follow any stage because all
of them cut the tensor to the same size, and the depth of the network is therefore a config key rather
than a design decision. Note also what is absent from the shape: a batch dimension. The pipeline runs at
batch size one, because one microphone cannot gather more speakers to fill a group, and chapter 3 is
about what that costs a graphics processing unit (GPU).

The hidden width is registered for three published recipes and the three do not agree. The small offline
keyword model is 176 wide (`V-05-13`), the offline and streaming large models are 512 wide (`V-05-18`,
`V-05-23`, `V-05-38`), and the other framework's recipe is 256 wide (`V-05-04`). The number of lists a
stage sees is set before the block chain runs, by a `subsampling_factor` that collapses several feature
frames into one encoder step; the two streaming recipes register that factor as 4 (`V-05-32`) and as 8
(`V-05-42`). What one step is in seconds follows from those factors and from a stride no record states in
this appendix's units, so chapter 9 does that conversion and this file does not.

| Symbol | What it is | What it is on a board |
| --- | --- | --- |
| $x_t$ | one step: the list of numbers describing one moment | one row of a buffer |
| $d_{\text{model}}$ | the length of that list | the width of the wire and of every word-aligned store |
| $T$ | how many steps a pass covers | the depth a buffer must reach |
| $t$ | which step, counting in encoder steps | a write address, and nothing more mysterious |
| $h$ | how many attention heads split the width | how many parallel lanes read the same row |
| $d_{\text{head}}$ | one head's share of the width | the width of one lane |
| $k$ | taps in a convolution filter | the length of a delay line |
| $b$ | bits stored per number | the memory primitive a value lands in |

**Hardware application.** A width that is a power of two and a width that is not are different objects
in a datapath. At 512 units (`V-05-18`) the tensor is $2^9$ wide, so a head's offset inside a step is a
shift and a mask, and one row is a whole number of aligned words. At 176 units (`V-05-13`) it is not, so
cutting a step into head slices needs a divide by a non-power-of-two somewhere, and a designer either
pays for that in an address generator or lays the memory out per head so the question never arises. This
is the first instance of a pattern this book keeps meeting: a config value that looks like a size
difference turns out to be a *shape* difference, and shape decides what logic you write.

Nothing above becomes a byte count in this section, deliberately. How many bytes one step occupies is
$d_{\text{model}}$ times $b$, and $b$ is not registered for any candidate model, so the rule is stated
once at the end of this appendix rather than used early and wrongly.

## A.2 One Block, Stage by Stage

**Intuition.** A stage can mix information in exactly two directions: along time, so that a step learns
from other steps, or across the width, so that a step learns from its own numbers. That is the whole
taxonomy, and it explains the block's shape. A Conformer encoder block spends two of its stages mixing
along time -- one with attention, one with a convolution -- and two across the width, with a
feed-forward network. Between the stages the block adds its own input back to each stage's output, which
is the same trick a feedback path is: it keeps a running copy of the signal so a stage can nudge it
instead of replacing it. Repeat the block and each repetition starts from a slightly better
representation than the last.

**Mechanism.** In the order the published recipes use it, one block is five stages:

| Order | Stage | Which direction it mixes | What sizes it, on record |
| --- | --- | --- | --- |
| first | half of a feed-forward network | across the width | an expansion factor of 4 `V-05-36` |
| second | multi-head self-attention | along time, at any allowed distance | `n_heads`, 8 `V-05-19` or 4 `V-05-14` |
| third | a convolution module | along time, at a fixed short reach | `conv_kernel_size`, 31 `V-05-25` or 9 `V-05-40` |
| fourth | the other half of the feed-forward | across the width | the same factor `V-05-36` |
| fifth | one normalisation over the sum | neither; it rescales | `conv_norm_type` names a type, not a size `V-05-26` |

The two feed-forward halves are each narrower than a full one so that the pair costs what one full
network costs: the width of a single half is the hidden width times an expansion factor of 4
(`V-05-36`), and the other framework states its half-width as an absolute instead of as a ratio, 2048
units at a hidden width of 256 (`V-05-04`). Then the block repeats. The registered repetition counts are
16 (`V-05-12`), 17 (`V-05-17`, `V-05-22`, `V-05-37`) and 12 (`V-05-04`), and each repetition has its own
copy of every weight, so the count multiplies both the work and the storage.

> **Whose order this is, and what is not on record.** The five-stage order, the half-and-half split of the
> feed-forward, and the residual additions come from the architecture's published definition and from the
> encoder implementations in the two frameworks this book reads. No record in
> `docs/verification/claims.json` prints a block's sub-layer list or its order, which is why the table
> above cites a key per row rather than citing a source for the shape. Chapter 9 draws the same block from
> the config side and says so in the picture; this appendix draws it from the reading side. The two
> readings are the same assumption, stated twice on purpose.

**Hardware application.** Inside one step, the block is a serial chain, and the stage that finishes last
decides when the step is done. So a step's latency is the sum of five stage latencies multiplied by the
block count, and no overlap is available *within* one step, because every stage needs the previous one's
output. The parallelism a designer can actually use is across the width, and across steps of *different*
utterances, which a streaming pipeline does not have. That is the shape of the problem that chapter 8,
chapter 9 and chapter 10 spend their effort on. Two secondary consequences follow from the same list:

- A residual add is not free in hardware. The stage's input must still exist when its output is ready, so
  every skip connection is a buffer as deep as the span it jumps over. Four such jumps per block, times
  the block count, is a real claim on on-chip storage, and section 8.2 sizes the equivalent for a
  convolution's line buffer.
- A normalisation stage is a reduction: it reads a whole row before it can write any of it. That is the
  end of this appendix's treatment of it; section 8.3 carries the arithmetic of doing one without a
  floating-point unit.

## A.3 Self-Attention: Reading the Past Because You Decide To

**Intuition.** A fixed window of the last few frames cannot express a dependency whose distance varies:
a vowel that matters to a consonant three frames back and the same vowel thirty frames back are the same
linguistic event at two different distances. Attention solves this by letting the model *choose* where to
look, separately for every step. It chooses by comparing what the current step is asking for against what
each other step is offering, and then it averages the offered values with weights taken from that
comparison. Nothing is remembered specially and nothing is skipped: every allowed step is read, and the
answer is a weighted mean.

For a hardware reader the object is less mysterious than it sounds. Attention is a read whose address is
computed from the data, followed by a weighted average of what came back -- a content-selected
multiplexer with a accumulator behind it, where the select code changes every cycle and is derived from
the payload itself. The cost of that convenience is the subject of the rest of this section.

**Mechanism.** Each step produces three vectors from its own values by three matrix-vector products: a
query $q_t$ that says what this step wants, a key $k_i$ that says what step $i$ advertises, and a value
$v_i$ that is what step $i$ would hand over if it were read. The projections cut the width into $h$
heads, and each head keeps its own $d_{\text{head}}$ units of each vector. Then, for the current step:

$$s_{t,i} \;=\; \frac{q_t \cdot k_i}{\sqrt{d_{\text{head}}}} \qquad\text{over the steps } i \text{ the mask allows}$$

$$\alpha_{t,i} \;=\; \frac{\exp(s_{t,i})}{\sum_j \exp(s_{t,j})} \qquad o_t \;=\; \sum_i \alpha_{t,i}\, v_i$$

Read the three parts in order. A **score** $s_{t,i}$ is a dot product, so it is large when the query and
the key point the same way. A **softmax** turns a list of scores into a list of positive weights that sum
to one, which is why the denominator is there: it is what makes the second line an average rather than a
sum. The **output** is then a weighted average of the values, and the head outputs are concatenated and
passed through one more projection before leaving the stage.

**Why the divisor exists, since it looks like a wart.** A dot product of two vectors $d_{\text{head}}$
units wide adds $d_{\text{head}}$ products together. Products of unrelated numbers have variances that
add, so the spread of the sum grows like $\sqrt{d_{\text{head}}}$ while the spread of each input term
stays put. Now remember what a softmax does with spread: it exponentiates. A widened input distribution
makes one weight approach one and every other weight approach zero, and a stage that has degenerated into
a hard selection has stopped averaging -- it can only copy one step, and small changes in a score can no
longer change the output at all. On this book's hardware the same saturation is worse still, because a
fixed-point representation rounds the losing weights to zero and the layer's behaviour becomes
irreproducible at a different word width. Dividing by $\sqrt{d_{\text{head}}}$ puts the spread back near
one whatever the head width is, which is the entire reason the divisor is a function of a model dimension
rather than a constant.

The consequence for two candidate models is concrete: at a hidden width of 512 units with 8 heads
(`V-05-18`, `V-05-19`) one head is $512 \div 8 = 64$ units wide, and at 176 units with 4 heads
(`V-05-13`, `V-05-14`) one head is $176 \div 4 = 44$. Both quotients use the registered width and the
registered head count and nothing else. Two candidates therefore want two different constants, $1/\sqrt{64}$ and
$1/\sqrt{44}$, and a design that hard-codes one cannot host the other without a change to a
multiply-and-round stage.

> **Traceability note.** The divisor is the standard scaled dot-product form and appears in both
> frameworks' attention code. That the *head* width, not the full width, is what enters the divisor is
> the point a config reading can miss: `n_heads` (`V-05-14`, `V-05-19`, `V-05-24`, `V-05-39`) changes the
> constant without changing `d_model` (`V-05-13`, `V-05-18`, `V-05-23`, `V-05-38`), so raising the head
> count at fixed width makes every head narrower and every divisor smaller. Doubling the head count also
> leaves the total cached width exactly where it was, because the heads are slices of one row and not
> additions to it.

::: {#fig-appendix-attention .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  box/.style={draw, rounded corners=1pt, align=center, inner sep=3.5pt,
              text width=24mm, minimum height=7mm},
  store/.style={box, densely dashed, text width=31mm},
  arr/.style={-{Latex[length=1.8mm]}, line width=0.28pt},
  darr/.style={-{Latex[length=1.8mm]}, line width=0.28pt, densely dashed}
]
% Row one, left to right: one step becomes three vectors, then scores, then scale.
\node[box] (xin)  at (0,0)     {one step $x_t$, and every earlier step already read};
\node[box] (qkv)  at (3.4,0)   {three projections give $q_t$ for this step, $k_i$ and $v_i$ for each};
\node[box] (score) at (6.8,0)  {scores: one dot product per allowed step $i$};
\node[box] (scale) at (10.2,0) {mask out the disallowed, then divide by $\sqrt{d_{\text{head}}}$};
% Row two, right to left: the average, then the head merge.
\node[box] (soft) at (6.8,-1.9) {softmax: exponentiate, then divide by the row's sum};
\node[box] (wavg) at (3.4,-1.9) {weighted average of the values $v_i$};
\node[box] (out)  at (0,-1.9)   {$o_t$: heads concatenated, one projection out};
% The storage, which is the reason the figure is drawn at all.
\node[store] (cache) at (4.6,-3.7) {the keys and values of every step still in the allowed set, kept
                                    between steps};
\draw[arr] (xin.east) -- (qkv.west);
\draw[arr] (qkv.east) -- (score.west);
\draw[arr] (score.east) -- (scale.west);
\draw[arr] (scale.south) to[bend right=14] (soft.north);
\draw[arr] (soft.west) -- (wavg.east);
\draw[arr] (wavg.west) -- (out.east);
\draw[darr] (cache.north) -- (wavg.south);
\draw[darr] (cache.east) to[bend left=16] (score.south);
\node[anchor=west, align=left, text width=44mm] at (-1.45,-3.7)
  {\textbf{Dashed} = storage the design must supply. \textbf{Solid} = arithmetic. The mask, not the
   softmax, is what bounds the read set; see chapter 9 for the streaming form of it.};
\end{tikzpicture}
```
One step of one head. Every box on the solid path is arithmetic that must finish before the step is done;
the dashed box is the only memory attention asks for, and it is where the whole question of section 9.4
comes from.
:::

**Hardware application.** Four consequences follow from the mechanism, and each is a design constraint
rather than a taste.

*The work per step is proportional to the read set, not to the width.* A step forms one dot product per
allowed step, so the multiply-accumulates this stage performs grow with how much of the past the mask
admits. In the offline reading of the model that is the whole utterance, and an accelerator sized for it
is sized for a number that changes with the length of the speech. In the streaming readings the read set
is bounded by configuration: a left context of 140 steps (`V-05-29`) for one candidate and 70 for the
other (`V-05-43`), so the stage's work per step becomes a constant a designer can plan around. Buying a
fixed cost is exactly what the bound is for, and the price -- an accuracy penalty for the past the design
refuses to look at -- is what chapter 9 measures.

*Two of the three vectors must be remembered and one need not.* The query of a finished step is
consumed the moment its scores exist; the key and the value are read by every later step that is allowed
to look back, so they persist. That pair is the cache, and [Figure 14](#fig-appendix-attention) draws it
as a box for a reason: it is the only storage attention requires, its depth is the read set, and its
width is the hidden total rather than the head count. Every later step's attention reads it, so it sits
on the critical path of a stage that is already on the critical path of the block. Chapter 9 sizes it;
this appendix leaves the arithmetic alone, because a depth in bytes needs a word width and none is
registered for any candidate (`V-05-57`).

*A softmax is two reductions and a divide.* A maximum or a sum over the whole read set, then one divide
per weight. Both are per-row operations whose length varies with the mask, and neither is a multiply-add
the way a matrix is, so an array of digital signal processing (DSP) slices that is ideal for the dot
products is a poor fit for the tails of the stage. Section 8.3 is where this book deals with that
mismatch, and where the approximation choices get made.

*Position has to reach the score somehow, and the way it does so decides whether a cache survives being
slid.* Both recipes on record use a relative scheme (`V-05-21`, `V-05-27`), in which a step's position
changes its scores only by how far it sits from the step doing the reading. That is the property which
lets a rolling buffer keep meaning as new steps arrive: a distance does not change when older material
leaves. How the distance is folded into a score is not quoted anywhere in this registry, so this
appendix states what the scheme is for and does not present a sum as fact.

## A.4 Convolution Along Time: the Same Read, Done Cheaper

**Intuition.** A convolution over time is the filter an audio engineer has written in hardware
many times: the output at this instant is a weighted sum of this sample and the last few, with fixed
coefficients -- a finite impulse response (FIR) filter, and a shift register is its natural body. The
neural-network version changes that in one respect only: the coefficients are learned rather than
designed. The complication is that a step is a *vector*, so a filter has to say both which taps along
time it reads and which of the width's channels it reads from. That second choice is where all the cost
is, and the two factorisations below are two ways of making it smaller.

**Mechanism.** Let $C$ be the number of channels in, $C'$ the number out, and $k$ the tap count. A
**dense** convolution trains a separate filter for every output channel, and each of those filters reads
every input channel, so one step costs

$$\text{dense:} \quad k \cdot C \cdot C' \ \text{multiply-accumulates}$$

A **depthwise** convolution drops the channel mixing entirely: each output channel gets one filter that
reads exactly one input channel, so the whole layer over time costs

$$\text{depthwise:} \quad k \cdot C$$

A **pointwise** convolution is the opposite extreme: one tap, and it reads every channel to mix them, so
per step it costs $C \cdot C'$. Putting the two together is the **time-channel separable** form: the time
reach of a depthwise filter, and the channel mixing of a pointwise one, in series instead of as a grid.
The pair costs $k \cdot C + C \cdot C'$ per step where the dense form costs $k \cdot C \cdot C'$.

At the width the large recipes publish, 512 units (`V-05-18`), with the tap count of the streaming
Conformer, 31 (`V-05-25`), and a mixing stage that keeps the width the same, the dense form costs
$31 \times 512 \times 512 = 8{,}126{,}464$ multiply-accumulates per step where the separable pair costs
$31 \times 512 + 512 \times 512 = 278{,}016$, every factor of both sums being a registered figure. The
saving is a factor of about twenty-nine. Cut the window to the fast variant's 9 taps (`V-05-40`) and the
depthwise half falls to $9 \times 512 = 4{,}608$ while the mixing half does not move at all,
which is the lesson worth keeping: the factorisation does not make the
stage cheap, it moves the cost. After the trick, the pointwise mix dominates, and it is the part of the
layer that does not care about time at all. Three tap counts are on record for the recipes this book
reads -- 31 (`V-05-25`), 15 (`V-05-04`) and 9 (`V-05-40`) -- and no registered source explains why a
recipe chose one rather than another.

::: {#fig-appendix-dense-separable .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  cell/.style={draw, minimum width=4.4mm, minimum height=4.4mm, inner sep=0pt},
  nodein/.style={circle, draw, inner sep=1.4pt},
  blk/.style={draw, densely dashed, rounded corners=1pt, inner sep=4pt, align=center},
  arr/.style={-{Latex[length=1.6mm]}, line width=0.24pt}
]
% --- left panel: one output channel of a dense filter ---
\node[blk] (dense) at (0,0) {%
  \begin{tikzpicture}[font=\scriptsize]
    \foreach \r in {0,1,2} {
      \foreach \c in {0,1,2} {
        \node[cell] (d\r\c) at (\c*0.52,-\r*0.52) {};
      }
    }
    \node[anchor=north, font=\scriptsize] at (0.52,-1.85) {channel, by tap};
    \node[nodein] (yo) at (3.1,-0.78) {};
    \foreach \r in {0,1,2} { \foreach \c in {0,1,2} { \draw[arr] (d\r\c.east) -- (yo.west); } }
  \end{tikzpicture}%
};
\node[anchor=south, align=center, text width=44mm] at (dense.north)
  {\textbf{Dense.} Every tap of every channel feeds every output channel: $k \cdot C \cdot C'$
   multiply-accumulates per step, and the whole $k \times C$ window must be within reach of one
   multiplier at once};
% --- right panel: depthwise delay lines, then one pointwise mix ---
\node[blk] (sep) at (7.6,0) {%
  \begin{tikzpicture}[font=\scriptsize]
    \foreach \r in {0,1,2} {
      \foreach \c in {0,1,2} {
        \node[cell] (s\r\c) at (\c*0.52,-\r*0.52) {};
      }
      \node[nodein] (zo\r) at (3.1,-\r*0.52) {};
      \draw[arr] (s\r2.east) -- (zo\r.west);
    }
    \node[anchor=north, font=\scriptsize] at (0.52,-1.85) {one delay line per channel};
    \node[blk] (pw) at (5.1,-0.78) {\begin{tabular}{c}$1\times1$\\ mix\end{tabular}};
    \foreach \r in {0,1,2} { \draw[arr] (zo\r.east) -- (pw.west); }
    \foreach \o in {0,1,2} {
      \node[nodein] (wo\o) at (7.1,0.2-\o*0.7) {};
      \draw[arr] (pw.east) -- (wo\o.west);
    }
  \end{tikzpicture}%
};
\node[anchor=south, align=center, text width=58mm] at (sep.north)
  {\textbf{Separable.} A depthwise filter reads only its own channel's delay line, then one pointwise
   step mixes channels: $k \cdot C + C \cdot C'$ multiply-accumulates per step, and a channel's stored
   window is read by that channel alone};
\end{tikzpicture}
```
The two shapes side by side, over three channels and three taps for legibility. What changes is not the
number of outputs but how many values must be within reach of a multiplier at once, and that is a memory
question before it is an arithmetic one.
:::

**Hardware application.** [Figure 15](#fig-appendix-dense-separable) sets the two shapes beside each other.
The arithmetic above is the whole reason a Conformer is buildable, and the two halves of the
factorisation have different physical signatures.

A depthwise filter over time *is* a shift register with taps hanging off it, and it is the one part of
the block a hardware reader will feel at home with: $k$ stored values per channel, one multiply-add per
tap, and a stream that advances one step at a time. For a streaming model the taps must all reach
backwards, and the recipe says so directly -- `conv_context_size: causal` (`V-05-25`), which that file's
own comment reads as every tap behind the current step. A delay line with only backward taps can be
built, filled and retired in place, which is why the convolution module can run ahead of attention
instead of waiting on it.

A dense filter over channels has no such locality. Its input to one output value is a
$k \times C$ block, so either the block sits in on-chip storage or it is re-read once per output channel,
and both answers are paid for in memory rather than in logic. That is the arithmetic this section's
factorisation removes, and it is the reason the separable form is not merely a smaller count of
multiplications: it changes which resource the stage is hungry for.

To put a stage's arithmetic on a clock, divide its per-step multiply-accumulate count by the number of
multipliers a device has. The fabric this book targets is registered with 1,248 multiply-accumulate
slices (`V-01-09`), so the dense layer of the example above would need
$8{,}126{,}464 \div 1{,}248 \approx 6{,}512$
clocks if every slice performed one multiply-accumulate every clock, and it is a bound rather than an
estimate because no design achieves it. The gap between that bound and what a real implementation
reaches is exactly what chapter 3 argues about and chapter 10 measures, and no percentage of peak is
registered for this workload. What the exercise is worth is the ratio, which does not depend on the
gap: the factorisation cuts the stage's floor by about twenty-nine times, and a clock budget cannot
be spent twice.

## A.5 Keeping the Numbers in Range

**Intuition.** A trained network is a chain of gains, and the weights at the far end were fitted to
whatever scale the near end happened to produce. If a later stage sees a signal a hundred times larger
than the one it was fitted on, its answer is nonsense. So the architecture inserts a stage whose job is
nothing but keeping the signal's scale where the weights expect it -- an automatic gain control, with the
twist that it can be set to normalise across the channels of one step or across the steps of one channel,
and those two choices have very different costs on a chip.

**Mechanism.** A layer normalisation over the width takes the $d_{\text{model}}$ values of one step,
subtracts their mean, divides by their standard deviation, and then applies a learned scale and shift per
channel:

$$\hat{x}_{t,c} \;=\; \frac{x_{t,c} - \mu_t}{\sigma_t}\,\gamma_c + \beta_c$$

The mean $\mu_t$ and the standard deviation $\sigma_t$ are computed from that one step, per step, and
$\gamma_c$ and $\beta_c$ are weights -- one pair per channel. A batch normalisation instead collects its
$\mu$ and $\sigma$ once, from the training data, and freezes them; at inference the two statistics are
constants, so the stage reduces to a multiply and an add per channel with no reduction at all.

The two types are not interchangeable across the recipes this book reads. The offline large model's
convolution module is registered as `conv_norm_type: 'batch_norm'` (`V-05-20`); the two streaming recipes
in the same family are registered as `'layer_norm'` (`V-05-26`, `V-05-41`), and the other framework's
config quotes here names neither. Which normalisation a block uses changes what its stages must compute,
so the disagreement is a datapath difference and not a stylistic one.

> **Traceability note.** `V-05-20`, `V-05-26` and `V-05-41` register a config key's value, which is a
> type name. Nothing in this registry records a measured cost for either choice on either device, and this
> appendix therefore describes the two stages' arithmetic rather than pricing them. What can be said
> without a measurement is that one of the two requires a reduction over the whole width at run time and
> the other does not.

**Hardware application.** A batch normalisation at inference is a per-channel affine, and a per-channel
affine can be folded into the weights of the stage that precedes it, in which case it disappears from the
run time entirely. That is why it is the cheap answer, and why it appears in an offline recipe whose whole
utterance is available.

A layer normalisation cannot be folded, because $\mu_t$ and $\sigma_t$ belong to the step being
normalised. Concretely, the stage reads a whole row -- 512 values at the large width (`V-05-18`) -- and
must finish summing it before any output value is valid, so it is a reduction tree on the critical path of
its stage rather than a pass that overlaps. Then it needs a reciprocal square root and a multiply per
element, and on a device with no floating-point unit both the reciprocal and the square root are
approximations with a word width and an error budget. That is the substance of section 8.3, which derives
a power-of-two form for the same shape of problem in the softmax and is the chapter's hardest arithmetic. What
this section was for is the reason that arithmetic matters at all: the model asked for a reduction and a
divide, and the hardware has to answer with additions and shifts.

## A.6 From a Dimension to a Budget

**Intuition.** A width is not a cost. A cost is a count of stored numbers times the width of each, and
the book's arguments only become checkable at that point. Two kinds of numbers are stored, and they behave
oppositely: weights are fixed once training ends and are read over and over, while activations are
produced and consumed every step and are gone a moment later. Almost every architecture decision in this
book is a bet about which of the two is worth keeping close to the arithmetic.

**Mechanism.** The rule is one line:

$$\text{bytes} \;=\; \frac{\text{elements} \times b}{8}$$

where $b$ is the number of bits per stored value. Before using it, a unit convention has to be chosen and
said out loud, because the datasheets in this project are not consistent and the registry has a record
filed about exactly that. Here, $1\ \text{Kb} = 2^{10}\ \text{bits}$, $1\ \text{KiB} = 2^{10}\ \text{bytes}$,
and a decimal $\text{kB}$ or $\text{MB}$ means a thousand or a million of the same; `V-01-23` registers
that the datasheet's Mb columns for this device are 1024-based, which is the reading every figure below
uses. The same record exists to warn that two different totals were each defensible under some reading of
a unit, and a sentence that mixes the conventions is wrong by a factor no rounding can repair.

The device's own on-chip storage, with each type named, is the following. The fabric holds 144 block
random-access memory (BRAM) blocks and 64 UltraRAM (URAM) blocks (`V-01-05`, `V-01-07`), and `V-01-23`
fixes one BRAM tile at 36 Kb and one URAM tile at 288 Kb. Their sum is 23,616 Kb, which `V-01-22` unrolls
in full: 2,952 KiB, 3,022,848 bytes, 2.8828 MiB, or 3.02 MB in decimal units, and 3.13 MiB if the
processing system's own 256 KB on-chip memory is counted as well. That total is **BRAM plus URAM
together**, and the two types are not interchangeable in a design: BRAM on its own is registered as 5.1
Mb (`V-01-06`), which is 0.6375 MiB computed from the registered figure by dividing by eight, and the
datasheet also lists 3.5 Mb of distributed RAM (`V-01-16`) built from the same look-up tables that
implement the logic. Calling 2.8828 MiB a "BRAM budget" would be the same class of unit error this book
already forbids for the four-megabyte figure in chapter 1, so both totals appear above with their types
named.

Now the model side. The three recipes whose sizes are published are the small offline keyword model at
about 14 million parameters (`V-05-16`), the streaming Conformer at about 120 million (`V-05-33`) and the
streaming FastConformer at about 115 million (`V-05-46`). At two bytes per weight -- half-precision, an
assumption of this paragraph and not a record -- the small model's weights are 28 MB, a computed
figure, and the two large models are 240 MB and 230 MB, computed the same way. Set those beside
3.02 MB (`V-01-22`) and the conclusion is not close: the weights are roughly a hundred times the
fabric's entire on-chip storage, so no overlay in this book can hold the model, and the design questions
in chapter 8 and chapter 9 -- what streams, what tiles, what stays, what gets re-read -- exist because of
that ratio.

> **What this appendix will not do, and why.** The counts above are storage for the whole model at a
> precision nobody registered. What is missing is not a rounding but a category: no record in
> `docs/verification/claims.json` gives multiply-accumulates per frame, integer (INT8) weight bytes,
> or activation bytes per step for any candidate model, and `V-05-57` is filed as unresolved
> on precisely those grounds. A budget in this book therefore stops where a record stops, and a table of
> per-layer byte counts is not published until something measures or fetches one.

Two further quantities that a reader might expect to find used here are also unregistered, and they are
named rather than invented because they bound the arithmetic of this appendix from the other side. There
is no fetched value for what one kernel launch costs on this Orin, in microseconds,
which is why the convolution section above gives a stage's floor in clocks
rather than in milliseconds. And there is no registered
percentage of peak multiply-accumulate utilisation for a streaming workload, which is why every figure
divided by 1,248 slices (`V-01-09`) in this appendix is called a bound. Both are fetchable claims, and
`book-en/open-questions.md` is where they wait.

**Hardware application.** The rule and the ratio are the section's whole payload, so it is worth stating
what a reader can now do with them, since that is the point of the appendix. Given a hidden width, a tap
count, a head count and a block count -- all four registered, all four quoted above -- the per-step
multiply-accumulate count of every stage in a block can be written down before any hardware is chosen,
and the sum can be divided by the fabric's 1,248 slices (`V-01-09`) to get a floor in clocks. What cannot
be written down from registered figures alone is any quantity in bytes, for weights beyond the assumption
in this section, or for activations at all. That asymmetry -- arithmetic describable, storage not -- is
the state of the evidence this book was written against, and every chapter's cost table inherits it.
