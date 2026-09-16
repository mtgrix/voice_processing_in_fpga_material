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

> **The formula.** $f:\ \mathbb{R}^{T \times d_{\text{model}}} \longrightarrow \mathbb{R}^{T \times d_{\text{model}}}$
>
> **The variables.**
>
> - $f$ — one stage of the network, read as "a function that maps an input to an output". It is a
>   placeholder for every stage this appendix describes, not one particular stage.
> - $\mathbb{R}$ — the real numbers. The set every entry of the tensor is drawn from, which is a
>   statement about the mathematics and not about the hardware: a real number is exactly what a
>   fixed-point register is not.
> - $T$ — how many steps one pass covers. A count of steps.
> - $d_{\text{model}}$ — the hidden width: how many numbers describe one step. A count of numbers,
>   called units in the records.
> - $T \times d_{\text{model}}$ — the shape of the whole input: a rectangle of $T$ rows of
>   $d_{\text{model}}$ entries. Two counts multiplied, not a measured quantity.
> - $\longrightarrow$ — "maps to". The left shape goes in and the right shape comes out.
>
> **What it means.** A stage takes a width by a depth and returns the same width by the same depth.
> That invariance is not a detail. It is why the block can be repeated at all: any stage may follow
> any stage because all of them cut the tensor to the same size, and the depth of the network is
> therefore a config key rather than a design decision. Note also what is absent from the shape: a
> batch dimension. The pipeline runs at batch size one, because one microphone cannot gather more
> speakers to fill a group, and chapter 3 is about what that costs a graphics processing unit (GPU).
>
> **What it costs.** Nothing by itself, and that is the useful reading: a shape equation prices
> nothing until it is multiplied by a word width and a count of operations. What it does fix is the
> geometry every cost is later counted over. A tensor $T$ by $d_{\text{model}}$ held in a fabric
> costs $T \times d_{\text{model}}$ stored values times the bits each occupies, which is the
> bytes rule at the end of this appendix, and a stage that preserves the shape can be chained without a
> reshuffle between links -- no crossbar, no repacking, no buffer whose depth changes at the
> boundary. The absence of a batch dimension is a cost too, in the other direction: the parallelism
> a GPU would fill by processing many utterances at once is simply not available, so the only
> parallelism left is inside one step.
>
> **What it does not say.** It does not say the stage is linear, or cheap, or the same stage twice --
> two identical shapes can hide completely different arithmetic. And $\mathbb{R}$ does not say the
> hardware computes in the reals: it does not, and chapter 7 is about what is lost when a real number
> is replaced by a fixed-point one. Read as a promise about precision, this line is false; read as a
> statement about shape, which is all it is offered for, it is exact.

The hidden width is registered for three published recipes and the three do not agree. The small offline
keyword model is 176 wide, the offline and streaming large models are 512 wide, and the other framework's
recipe is 256 wide -- each one a config value read out of that recipe's own published definition. The
number of lists a stage sees is set before the block chain runs, by a `subsampling_factor` that collapses
several feature frames into one encoder step, and the two streaming recipes register that factor as four
and as eight. Which record says what is the traceability table at the end of this section. What one step
is in seconds follows from those factors and from a stride no record states in this appendix's units, so
chapter 9 does that conversion and this file does not.

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
in a datapath. At the large recipe's width of 512 units the tensor is $2^9$ wide, so a head's offset
inside a step is a shift and a mask, and one row is a whole number of aligned words. At the small offline
model's width of 176 units it is not, so
cutting a step into head slices needs a divide by a non-power-of-two somewhere, and a designer either
pays for that in an address generator or lays the memory out per head so the question never arises. This
is the first instance of a pattern this book keeps meeting: a config value that looks like a size
difference turns out to be a *shape* difference, and shape decides what logic you write.

Nothing above becomes a byte count in this section, deliberately. How many bytes one step occupies is
$d_{\text{model}}$ times $b$, and $b$ is not registered for any candidate model, so the rule is stated
once at the end of this appendix rather than used early and wrongly.


**Traceability.** The records this section's figures come from.

| Record | What it establishes here |
| --- | --- |
| `V-05-13` | the small offline keyword model's hidden width is 176 |
| `V-05-18`, `V-05-23`, `V-05-38` | the large recipes' hidden width is 512, read from three configs that agree |
| `V-05-04` | the other framework's recipe in one line: hidden width 256, 12 blocks, 4 heads, feed-forward width 2048, kernel 15 |
| `V-05-32` | a streaming recipe's `subsampling_factor` of 4 -- four feature frames per encoder step |
| `V-05-42` | the other streaming recipe's `subsampling_factor` of 8, twice the collapse |


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

[Figure 33](#fig-appendix-block-reading) is that same block drawn for the direction each stage mixes,
and for the storage a residual quietly asks for.

::: {#fig-appendix-block-reading .figure}
```tikz
% The same block chapter 9 draws from the config side, read instead for what each stage
% MIXES. Box shape is the encoding: a NARROW box works within one step, across its width;
% a WIDE box reaches along time. Residuals are drawn as stored copies, because an add has
% to hold the pre-stage value until the stage's output is ready.
\begin{tikzpicture}[
  font=\scriptsize,
  flow/.style={-{Stealth[length=2mm]}, semithick},
  res/.style={-{Stealth[length=2mm]}, semithick, densely dashed},
  addn/.style={draw, circle, inner sep=2.6pt},
  keep/.style={draw, dashed, rounded corners=1pt, inner sep=2pt, font=\scriptsize},
  narrow/.style={draw, rounded corners=1pt, align=center, inner sep=4pt,
                 text width=3.0cm, minimum height=1.15cm},
  wide/.style={draw, rounded corners=1pt, align=center, inner sep=4pt,
               text width=8.2cm, minimum height=0.85cm},
  mid/.style={draw, rounded corners=1pt, align=center, inner sep=4pt,
              text width=5.6cm, minimum height=0.8cm},
  t/.style={align=center}
]
\node[t] (in) at (0,0) {one encoder step in\\[1pt] {\itshape a row of $d_\text{model}$ numbers}};
\node[narrow] (ff1) at (0,-1.35) {feed-forward, half one\\[1pt] {\itshape mixes across the width}};
\node[addn] (a1) at (0,-2.5) {$+$};
\node[wide] (att) at (0,-3.8) {multi-head attention\\[1pt] {\itshape mixes along time, at any allowed distance}};
\node[addn] (a2) at (0,-4.9) {$+$};
\node[wide] (conv) at (0,-6.2) {depthwise convolution\\[1pt] {\itshape mixes along time, at a fixed short reach}};
\node[addn] (a3) at (0,-7.3) {$+$};
\node[narrow] (ff2) at (0,-8.55) {feed-forward, half two\\[1pt] {\itshape mixes across the width}};
\node[addn] (a4) at (0,-9.7) {$+$};
\node[mid] (norm) at (0,-10.9) {one normalisation over the sum\\[1pt] {\itshape rescales; mixes neither}};
\node[t] (out) at (0,-12.1) {to the next block};

\draw[flow] (in) -- (ff1);
\draw[flow] (ff1) -- (a1);
\draw[flow] (a1) -- (att);
\draw[flow] (att) -- (a2);
\draw[flow] (a2) -- (conv);
\draw[flow] (conv) -- (a3);
\draw[flow] (a3) -- (ff2);
\draw[flow] (ff2) -- (a4);
\draw[flow] (a4) -- (norm);
\draw[flow] (norm) -- (out);

% Residuals on the right, each one a stored copy held across a single stage.
\node[keep, anchor=west] (k1) at (4.9,-1.35) {keep};
\node[keep, anchor=west] (k2) at (4.9,-3.8) {keep};
\node[keep, anchor=west] (k3) at (4.9,-6.2) {keep};
\node[keep, anchor=west] (k4) at (4.9,-8.55) {keep};
\draw[res] (in.east)  -- (k1.west);  \draw[res] (k1.east) to[bend left=8] (a1.east);
\draw[res] (a1.east)  -- (k2.west);  \draw[res] (k2.east) to[bend left=8] (a2.east);
\draw[res] (a2.east)  -- (k3.west);  \draw[res] (k3.east) to[bend left=8] (a3.east);
\draw[res] (a3.east)  -- (k4.west);  \draw[res] (k4.east) to[bend left=8] (a4.east);
\node[anchor=west, align=left, text width=20mm] at (6.0,-5.0) {a dashed \textbf{keep} is a value the block must still hold when the stage's output is ready};

% Direction legend, bottom left.
\node[anchor=north west, align=left, text width=76mm] at (-6.3,-12.7)
  {\textbf{Narrow box} $=$ one step, mixed across its own width. \textbf{Wide box} $=$
   one step, reaching along the row of steps. The two feed-forward halves are narrow
   because a step learns from its own numbers; attention and convolution are wide because
   a step learns from other steps. This is the block read for what it mixes; chapter 9
   draws the same block for what sizes it.};
\end{tikzpicture}
```
A stage can mix in two directions only: along time, or across the width. The block spends two stages on
each and one on neither, and the shape of every box here says which. The dashed keep-boxes are the point
a config reading misses: a residual is not free, because the value it adds back has to survive the stage
it jumped over, so four jumps per block are four claims on on-chip storage before a single weight is
counted.
:::


The two feed-forward halves are each narrower than a full one so that the pair costs what one full
network costs. One streaming recipe states the half-width as a ratio -- four times the hidden width --
and the other framework states its as an absolute instead, 2048 units at a hidden width of 256. Then the
block repeats. Three repetition counts are on record for the recipes this book reads: 16, 17 and 12, and
each repetition has its own copy of every weight, so the count multiplies both the work and the
storage.

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


**Traceability.** The records this section's figures come from.

| Record | What it establishes here |
| --- | --- |
| `V-05-36` | the streaming Conformer's feed-forward expansion factor is 4, a ratio against the hidden width rather than an absolute |
| `V-05-04` | the other framework's absolute half-width of 2048 at a hidden width of 256, and its block count of 12 |
| `V-05-12` | the small variant's block count of 16 |
| `V-05-17`, `V-05-22`, `V-05-37` | the larger variant's block count of 17, confirmed across three configs |


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

> **The formula.** $s_{t,i} \;=\; \dfrac{q_t \cdot k_i}{\sqrt{d_{\text{head}}}}$, taken over the steps $i$ the mask allows
>
> **The variables.**
>
> - $s_{t,i}$ — one score: how much step $t$ wants to read step $i$. A raw number with no unit and
>   no fixed range, which is precisely the problem the divisor addresses.
> - $q_t$ — the query of the current step: a vector $d_{\text{head}}$ entries long saying what this
>   step is looking for. Entries are dimensionless activations.
> - $k_i$ — the key of step $i$: a vector the same length, saying what step $i$ advertises that it
>   holds. Same units as $q_t$.
> - $\cdot$ — the dot product: multiply the two vectors entry by entry and add the $d_{\text{head}}$
>   products up. It is large when the two point the same way and near zero when they do not.
> - $d_{\text{head}}$ — the head width: how many entries each of $q$ and $k$ carries inside one
>   head. A count of numbers.
> - $\sqrt{d_{\text{head}}}$ — the square root of that count, used as a fixed divisor. A pure number.
> - $i$ — the step being read; $t$ — the step doing the reading. Counts of steps.
> - "the mask allows" — the subset of steps $i$ this step is permitted to look at, decided by
>   position rather than by content, and drawn in [Figure 36](#fig-appendix-attention).
>
> **What it means.** A score is a similarity test with no threshold attached: multiply matching
> entries and add, and a large sum means the query and the key point the same way. The divisor is
> not decoration and it is not a convention. Two passages below this card carry the argument in
> full -- why the divisor exists even though it looks like a wart, and what two candidate models
> therefore want as constants -- and the short form of the first is that a wider head adds up more
> products, which makes the score's spread grow, and the stage that consumes this number
> exponentiates it.
>
> **What it costs.** The dot product is $d_{\text{head}}$ multiply-accumulates, one per entry, and
> that is the whole price of the numerator. The divisor is the interesting part on a chip: it is a
> multiply by a constant, because $d_{\text{head}}$ is known at compile time, and a constant
> multiply whose value is a power of two is a bit shift that occupies no DSP slice at all. That is
> why a head width that is a power of two is worth having, and why the choice of head count is a
> hardware decision and not only a modelling one -- the consequence is worked out below.
>
> **What it does not say.** It does not say $s$ is a probability, a similarity between zero and one,
> or comparable across heads, layers or models -- it is an unbounded dot product with a scale
> correction. And the divisor does not make the score small; it makes its *spread* predictable,
> which is a different claim and the only one the next stage actually needs.
>
> **The formula.** $\alpha_{t,i} \;=\; \dfrac{\exp(s_{t,i})}{\sum_j \exp(s_{t,j})}$, and then $o_t \;=\; \sum_i \alpha_{t,i}\, v_i$
>
> **The variables.**
>
> - $\exp(s_{t,i})$ — the exponential of one score: $e$ raised to it. Always positive, whatever the
>   sign of the score, and it turns a difference of scores into a ratio.
> - $\sum_j$ — the sum of those exponentials over every step $j$ the mask allows, including $i$
>   itself. This is the denominator, and it is what makes the line an average rather than a sum.
> - $\alpha_{t,i}$ — the softmax weight: step $t$'s share of attention going to step $i$. A
>   dimensionless fraction in $[0,1]$, and the whole list of them over $i$ adds to exactly one.
> - $v_i$ — the value of step $i$: the vector step $i$ hands over if it is read, $d_{\text{head}}$
>   entries long.
> - $o_t$ — the output for step $t$: a weighted average of the values, $d_{\text{head}}$ entries
>   long.
>
> **What it means.** The softmax converts a list of unbounded scores into a list of positive shares
> that sum to one, which is what attention needs: it cannot average values with weights that add up
> to an arbitrary total, because then the output's scale would depend on how many steps were
> readable. Exponentiating first does two jobs at once -- it forces every weight positive, and it
> stretches differences so that a score slightly above the rest claims a disproportionate share.
> Dividing by the sum of all the exponentials then normalises the shares to one. The output is the
> weighted average those shares define, and the head outputs are concatenated and passed through one
> more projection before leaving the stage.
>
> **What it costs.** One exponential per readable step, one sum, one division per step -- and
> chapter 8 is where each of those three is built without a floating-point unit. The sum is a
> reduction, so it cannot begin until every score in the row exists, which is the same ordering
> constraint the max-subtraction there pays. The division is a reciprocal, and a reciprocal is
> iterative unless it is tabulated. The storage is not free either: $\alpha_{t,i}$ must exist for
> every allowed $i$ before the average can be taken, so the row of weights is as wide as the mask
> is permissive.
>
> **What it does not say.** It does not say attention selected one step. Unless a score dominates by
> a wide margin, the output is a genuine blend, and a reader who pictures a hard lookup has replaced
> an average with a multiplexer. And the weights summing to one is a property of the arithmetic, not
> a guarantee of interpretability: $\alpha_{t,i}$ being large says the dot product was large, which
> is a statement about vectors this stage computed, not about which words "matter" to a human.

[Figure 34](#fig-appendix-softmax-shares) draws that same row three times, so the two jobs the exponential does and the normalising divide are visible as a change of shape rather than as a sentence.

::: {#fig-appendix-softmax-shares .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  ax/.style={-{Stealth[length=1.6mm]}, line width=0.28pt},
  dn/.style={fill=black!12, draw=black!45, line width=0.3pt},
  up/.style={fill=black!32, draw=black!55, line width=0.3pt},
  sh/.style={draw=black!55, line width=0.3pt},
  ttl/.style={font=\scriptsize, anchor=north},
  note/.style={font=\scriptsize, align=center, text width=34mm, anchor=north}
]
% One row of four scores, drawn three times. The four illustrative values are
% (-2, -0.5, 0.5, 2): symmetric about zero, so the reader sees the sign die under
% exp and one value run away. Heights are scaled by hand, not computed.
% --- Panel 1: raw scores, a zero line, two bars below it ---
\begin{scope}[xshift=0cm]
  \draw[ax] (0,0) -- (3.4,0);
  \draw[ax] (1.7,-1.5) -- (1.7,1.9);
  \node[ttl] at (1.7,2.15) {raw scores};
  \node[note] at (1.7,-1.75) {$z$ can be negative, and any size. Nothing here\\ sums to anything useful.};
  \draw[black!40, densely dotted] (0,0) -- (3.4,0);
  \draw[dn] (0.3,0) rectangle (0.8,-1.0);
  \draw[dn] (1.15,0) rectangle (1.65,-0.25);
  \draw[up] (1.75,0) rectangle (2.25,0.25);
  \draw[up] (2.35,0) rectangle (2.85,1.0);
\end{scope}
% --- Panel 2: exponentiate, all positive, one dominates ---
\begin{scope}[xshift=4.6cm]
  \draw[ax] (0,0) -- (3.4,0);
  \draw[ax] (1.7,-0.3) -- (1.7,1.9);
  \node[ttl] at (1.7,2.15) {exponentiate $e^{z}$};
  \node[note] at (1.7,-1.75) {every bar is now above zero, but the largest\\ has run away from the rest.};
  \draw[black!40, densely dotted] (0,0) -- (3.4,0);
  \draw[up] (0.3,0) rectangle (0.8,0.14);
  \draw[up] (1.15,0) rectangle (1.65,0.38);
  \draw[up] (1.75,0) rectangle (2.25,0.65);
  \draw[up] (2.35,0) rectangle (2.85,1.7);
\end{scope}
% --- Panel 3: divide by the sum -> ONE stacked column of total height 1 ---
\begin{scope}[xshift=9.2cm]
  \draw[ax] (0,0) -- (3.4,0);
  \node[ttl] at (1.7,2.15) {divide by the row sum};
  \node[note] at (1.7,-1.75) {the four are stacked into one column exactly\\ one unit tall: shares, and they add to one.};
  \draw[black!40, densely dotted] (0,0) -- (3.4,0);
  % unit tick, so "one" is a height the reader can check
  \draw[line width=0.3pt] (1.05,1.0) -- (1.2,1.0);
  \node[anchor=east] at (1.02,1.0) {\scriptsize $1$};
  % one column, split into four shares summing to 1: 0.05, 0.13, 0.22, 0.60
  \draw[sh] (1.2,0.00) rectangle (2.2,0.05);
  \draw[sh] (1.2,0.05) rectangle (2.2,0.18);
  \draw[sh] (1.2,0.18) rectangle (2.2,0.40);
  \draw[sh, fill=black!45] (1.2,0.40) rectangle (2.2,1.00);
  \draw[<->, line width=0.28pt] (2.45,0) -- (2.45,1.0);
  \node[anchor=west] at (2.52,0.5) {\scriptsize sum $=1$};
\end{scope}
\end{tikzpicture}
```
One row of four scores, drawn three times. Exponentiating does two jobs at once -- it forces every
weight positive, and it stretches the gaps -- and dividing by the row's sum is what turns the result
from a set of runaway numbers into shares that add to one. The four values are chosen to show the
sign dying under $e^{z}$, not to be measured.
:::

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

[Figure 35](#fig-appendix-score-matrix) lays the mask over the scores it deletes, so the two
grids are visibly the same shape.

::: {#fig-appendix-score-matrix .figure}
```tikz
% Two readings of the SAME 6x6 grid: rows are queries, columns are keys, every cell is
% one dot product. Shaded = the mask keeps that cell. The mask has the same shape as the
% scores and is chosen by position, never by value.
\begin{tikzpicture}[
  font=\scriptsize,
  x=3.9mm, y=-3.9mm,
  grid/.style={draw=black!70, line width=0.3pt},
  ax/.style={font=\scriptsize, inner sep=1pt},
  rowhl/.style={draw=black, line width=0.7pt},
  arr/.style={-{Stealth[length=1.6mm]}, line width=0.3pt}
]
% ---------- panel A: causal ----------
\begin{scope}
  \foreach \r in {0,...,5} { \foreach \c in {0,...,5} {
      \draw[grid] (\c,\r) rectangle (\c+1,\r+1); } }
  \foreach \r in {0,...,5} { \foreach \c in {0,...,\r} {
      \fill[black!45] (\c,\r) rectangle (\c+1,\r+1); } }
  \draw[grid] (0,0) rectangle (6,6);
  \foreach \i in {1,...,6} {
    \node[ax, anchor=east] at (-0.15,\i-0.5) {$q_{\i}$};
    \node[ax, anchor=south] at (\i-0.5,-0.1) {$k_{\i}$};
  }
  \node[ax, anchor=south west] at (0,-1.1) {causal mask};
  \draw[rowhl] (0,5) rectangle (6,6);
  \draw[arr] (6.25,5.5) -- (7.15,5.5);
  \node[ax, anchor=west, text width=22mm] at (7.3,5.5) {one row at a time: its kept cells are exponentiated and divided by their own sum};
\end{scope}
% ---------- panel B: chunked ----------
\begin{scope}[xshift=11.7cm]
  \foreach \r in {0,...,5} { \foreach \c in {0,...,5} {
      \draw[grid] (\c,\r) rectangle (\c+1,\r+1); } }
  \foreach \r in {0,1} { \foreach \c in {0,1} {
      \fill[black!45] (\c,\r) rectangle (\c+1,\r+1); } }
  \foreach \r in {2,3} { \foreach \c in {0,...,3} {
      \fill[black!45] (\c,\r) rectangle (\c+1,\r+1); } }
  \foreach \r in {4,5} { \foreach \c in {2,...,5} {
      \fill[black!45] (\c,\r) rectangle (\c+1,\r+1); } }
  \draw[grid] (0,0) rectangle (6,6);
  \foreach \i in {1,...,6} {
    \node[ax, anchor=east] at (-0.15,\i-0.5) {$q_{\i}$};
    \node[ax, anchor=south] at (\i-0.5,-0.1) {$k_{\i}$};
  }
  \node[ax, anchor=south west] at (0,-1.1) {chunked mask};
  \draw[densely dashed, line width=0.5pt] (4,4) rectangle (6,6);
  \node[ax, anchor=north, text width=30mm] at (3,6.15) {the dashed block is the current chunk, read in both directions};
\end{scope}
\end{tikzpicture}
```
The same six steps, scored the same way, under two masks. Nothing about the arithmetic changes between
the panels; only which cells survive, and that is decided by position before a single score is computed.
The causal mask deletes every future cell. The chunked mask keeps the future inside the block the design
is already waiting for, and reaches back a fixed number of finished blocks. Chapter 9 sets these regimes
against one another and measures what the deletion costs; this figure's point is prior and smaller: a
mask is a second grid, the same shape as the scores, and the softmax runs across one row of it at a time.
:::


> **Which width the divisor uses.** The divisor is the standard scaled dot-product form and appears in
> both frameworks' attention code. That the *head* width, not the full width, is what enters it is the
> point a config reading can miss: the head count changes the constant without changing the hidden width,
> so raising the head count at fixed width makes every head narrower and every divisor smaller. Doubling
> the head count also leaves the total cached width exactly where it was, because the heads are slices of
> one row and not additions to it.

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
\node[anchor=west, align=left, text width=37mm] at (-1.7,-3.7)
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
is bounded by configuration: each streaming recipe registers its own left context, and the two values on
record are 140 steps and 70, so the stage's work per step becomes a constant a designer can plan around.
Buying a
fixed cost is exactly what the bound is for, and the price -- an accuracy penalty for the past the design
refuses to look at -- is what chapter 9 measures.

*Two of the three vectors must be remembered and one need not.* The query of a finished step is
consumed the moment its scores exist; the key and the value are read by every later step that is allowed
to look back, so they persist. That pair is the cache, and [Figure 36](#fig-appendix-attention) draws it
as a box for a reason: it is the only storage attention requires, its depth is the read set, and its
width is the hidden total rather than the head count. Every later step's attention reads it, so it sits
on the critical path of a stage that is already on the critical path of the block. Chapter 9 sizes it;
this appendix leaves the arithmetic alone, because a depth in bytes needs a word width and none is
registered for any candidate -- the registry carries that absence as an unresolved record.

*A softmax is two reductions and a divide.* A maximum or a sum over the whole read set, then one divide
per weight. Both are per-row operations whose length varies with the mask, and neither is a multiply-add
the way a matrix is, so an array of digital signal processing (DSP) slices that is ideal for the dot
products is a poor fit for the tails of the stage. Section 8.3 is where this book deals with that
mismatch, and where the approximation choices get made.

*Position has to reach the score somehow, and the way it does so decides whether a cache survives being
slid.* Both recipes on record configure a relative-position scheme rather than an absolute one, in
which a step's position
changes its scores only by how far it sits from the step doing the reading. That is the property which
lets a rolling buffer keep meaning as new steps arrive: a distance does not change when older material
leaves. How the distance is folded into a score is not quoted anywhere in this registry, so this
appendix states what the scheme is for and does not present a sum as fact.


**Traceability.** The records this section leans on. The two head-width quotients above are derived, and
their operands are named in the sentence that computes them; everything else is a registered figure or a
registered absence.

| Record | What it establishes here |
| --- | --- |
| `V-05-13` | the small offline model's hidden width, 176 |
| `V-05-14` | that model's head count, 4 -- a head width that is not a power of two |
| `V-05-18` | the large recipes' hidden width, 512 |
| `V-05-19`, `V-05-24`, `V-05-39` | head count 8 on three large configs -- a head width that is a power of two |
| `V-05-23`, `V-05-38` | two further configs registering the same width of 512 |
| `V-05-29` | one streaming candidate's left context, 140 encoder steps |
| `V-05-43` | the other streaming candidate's left context, 70 encoder steps |
| `V-05-21`, `V-05-27` | both recipes set relative-position attention, the second confirming it for the streaming model |
| `V-05-57` | unresolved on purpose: no publisher prints a per-step word width, so no cache depth in bytes is derivable |


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

> **The formula.** dense: $k \cdot C \cdot C'$ multiply-accumulates per step
>
> **The variables.**
>
> - $k$ — the tap count: how many time steps one filter reads. A count of steps.
> - $C$ — the channels in: how many separate value streams one step carries. A count of channels.
> - $C'$ — the channels out. A count of channels, equal to $C$ in the stages this book meets.
> - "multiply-accumulates" — one multiply and one add fused into a single operation, which is what
>   a DSP slice performs and what a MAC count is therefore counting. Operations, not bytes.
>
> **What it means.** A dense filter is a grid, and the product is that grid read off: each of the
> $C'$ outputs needs its own filter, each of those filters reads all $C$ input channels, and each
> reading spans $k$ taps. Three independent directions of work, multiplied. Nothing in the
> expression says which of the three is expensive -- it says all three are, at once.
>
> **What it costs.** $k \cdot C \cdot C'$ multiply-accumulates per step, and every one of them
> needs the input value at its own position, so the same input is re-read by every output that
> touches it. The re-reads are the traffic, and traffic is what a line buffer exists to remove --
> which is why this number is a floor on arithmetic and not a ceiling on what the stage actually
> moves across the chip.
>
> **What it does not say.** It does not say the stage is slow, and it does not say the count is
> reachable at the word width the design uses. It counts operations at one multiply each; a
> fixed-point multiply that occupies a DSP slice for several pipeline stages, or a weight stream
> that has to come off-chip, costs time this expression cannot see.

A **depthwise** convolution drops the channel mixing entirely: each output channel gets one filter that
reads exactly one input channel, so the whole layer over time costs

> **The formula.** depthwise: $k \cdot C$ multiply-accumulates per step
>
> **The variables.**
>
> - $k$ — the tap count, the same quantity as in the dense formula above: how many time steps the
>   filter reads. A count of steps.
> - $C$ — the channels, which is both the count in and the count out, because a depthwise stage
>   cannot change the width: channel $c$'s output is built only from channel $c$'s inputs. A count
>   of channels.
> - $k \cdot C$ — the product: one $k$-tap filter per channel, and no cross-channel terms.
>   Operations per step.
>
> **What it means.** Removing $C'$ from the product is not a saving of one factor out of three; it
> is a change of what the stage can express. A depthwise filter can look backwards in time and it
> can treat each channel differently, but it cannot combine two channels into one output. That is
> why it never appears alone: the mixing it dropped has to come back as a separate stage, and the
> pair is what the next paragraph costs out.
>
> **What it costs.** $k \cdot C$ operations, and one filter per channel rather than one per output
> channel, so the weight storage falls by the same factor the arithmetic does. What does not fall
> is the reading: a $k$-tap window still needs $k$ steps of history within reach per channel, which
> is the line buffer of chapter 8 and is a storage cost the operation count hides.
>
> **What it does not say.** It does not say the stage is cheaper than a dense one *and* does the
> same job. It does a strictly narrower job, and comparing $k \cdot C$ against $k \cdot C \cdot C'$
> without naming the mixing stage that has to be added back is the single most common misreading of
> this line.

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
reads: 31, 15 and 9, one per recipe, and no registered source explains why a recipe chose one rather than
another.

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

**Hardware application.** [Figure 37](#fig-appendix-dense-separable) sets the two shapes beside each other.
The arithmetic above is the whole reason a Conformer is buildable, and the two halves of the
factorisation have different physical signatures.

A depthwise filter over time *is* a shift register with taps hanging off it, and it is the one part of
the block a hardware reader will feel at home with: $k$ stored values per channel, one multiply-add per
tap, and a stream that advances one step at a time. For a streaming model the taps must all reach
backwards, and the streaming Conformer's config says so directly with its own key,
`conv_context_size: causal`, whose file comment reads it as every tap behind the current step. A delay
line with only backward taps can be
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


**Traceability.** The records this section leans on. The cost figures in the arithmetic above are derived,
and the sentence that derives them names the records supplying its operands; the rows below are the same
records read as attributions.

| Record | What it establishes here |
| --- | --- |
| `V-05-18` | the hidden width the worked cost example uses, 512 |
| `V-05-25` | the streaming Conformer's depthwise kernel: 31 taps, declared causal in the same config |
| `V-05-04` | the other framework's kernel of 15 taps at a hidden width of 256 |
| `V-05-40` | the fast variant's kernel of 9 taps |
| `V-01-09` | the fabric's 1,248 multiply-accumulate slices, the divisor every bound in this appendix uses |


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

> **The formula.** $\hat{x}_{t,c} \;=\; \frac{x_{t,c} - \mu_t}{\sigma_t}\,\gamma_c + \beta_c$
>
> **The variables.**
>
> - $\hat{x}_{t,c}$ — the normalised value of channel $c$ at step $t$: what leaves the stage. A
>   dimensionless activation, by construction, because the subtraction and the division remove
>   whatever units the input carried.
> - $x_{t,c}$ — the same value before normalisation, straight out of the previous stage.
> - $\mu_t$ — the mean of the $d_{\text{model}}$ values of step $t$ alone. Computed per step, at
>   run time.
> - $\sigma_t$ — the standard deviation of those same values: their spread about that mean. Also
>   per step, also at run time, and the reason this stage contains a square root and a reciprocal.
> - $\gamma_c$, $\beta_c$ — a learned scale and shift, one pair per channel, fixed once training
>   ends. Weights, not statistics.
> - $t$, $c$ — the step and the channel. Counts of each.
>
> **What it means.** Subtracting the mean and dividing by the spread moves every step's values onto
> a common scale, so the next stage receives numbers whose size does not depend on how loud the
> input was. The learned pair comes after, and it matters: normalising alone would force every
> channel to the same scale, which throws away real information, so $\gamma_c$ and $\beta_c$ let
> training put back whatever scale a channel actually wants. The order in the expression is the
> order in the hardware -- reduce, divide, then multiply and add -- and only the last two of those
> four operations are per-channel constants.
>
> **What it costs.** Two reductions over the full width per step, one for the mean and one for the
> variance, and neither can finish until every channel of that step exists. Then one reciprocal
> square root per step, which chapter 8 builds from a shift and a table, and then a pair of
> constant multiplies per channel, which could have been folded into the preceding stage had they
> been constants rather than per-channel weights. The reduction is the expensive part and it
> is a *latency* cost, not an arithmetic one: a wide step is a deep adder tree.
>
> **What it does not say.** It does not say the stage is cheap because each line of it is
> elementary. And it does not say which axis is normalised -- this one reduces across the channels
> of one step, which is what makes it usable on a stream. The alternative in the next paragraph
> reduces across steps and is computed offline, and the two are not interchangeable on a chip.

A batch normalisation instead collects its
$\mu$ and $\sigma$ once, from the training data, and freezes them; at inference the two statistics are
constants, so the stage reduces to a multiply and an add per channel with no reduction at all.

The two types are not interchangeable across the recipes this book reads. The `conv_norm_type` key of the
offline large model's convolution module reads `batch_norm`; the same key in the two streaming recipes of
that family reads `layer_norm`; and the other framework's config, quoted elsewhere in this appendix,
names neither. Which normalisation a block uses changes what its stages must compute, so the disagreement
is a datapath difference and not a stylistic one.

> **What is not on record.** The three configs above register a key's value, which is a type name.
> Nothing in this registry records a measured cost for either choice on either device, and this appendix
> therefore describes the two stages' arithmetic rather than pricing them. What can be said without a
> measurement is that one of the two requires a reduction over the whole width at run time and the other
> does not.

**Hardware application.** A batch normalisation at inference is a per-channel affine, and a per-channel
affine can be folded into the weights of the stage that precedes it, in which case it disappears from the
run time entirely. That is why it is the cheap answer, and why it appears in an offline recipe whose whole
utterance is available.

A layer normalisation cannot be folded, because $\mu_t$ and $\sigma_t$ belong to the step being
normalised. Concretely, the stage reads a whole row -- 512 values at the width the large recipes register
-- and must finish summing it before any output value is valid, so it is a reduction tree on the critical
path of
its stage rather than a pass that overlaps. Then it needs a reciprocal square root and a multiply per
element, and on a device with no floating-point unit both the reciprocal and the square root are
approximations with a word width and an error budget. That is the substance of section 8.3, which derives
a power-of-two form for the same shape of problem in the softmax and is the chapter's hardest arithmetic. What
this section was for is the reason that arithmetic matters at all: the model asked for a reduction and a
divide, and the hardware has to answer with additions and shifts.

The base-two polynomial above is not a chapter 7 curiosity, because both normalising shapes in this
appendix ask for the same exponential. The softmax of section 3 of appendix A exponentiates a row of
scores before it divides by their sum, and the layer normalisation derived just above needs a
reciprocal square root that is another transcendental in fixed-point clothing. The integer-only path
is the same one in all three places: split the exponent at the binary point so the integer half
becomes a shift, and hand the fraction to the second-order polynomial with coefficients $0.6958$ and
$0.2250$. Section 8.3 is where that arithmetic is derived for the softmax's normalising shape, and
the coefficients above are what it inherits.


**Traceability.** The records this section leans on.

| Record | What it establishes here |
| --- | --- |
| `V-05-20` | the offline large model's convolution module normalises with BatchNorm |
| `V-05-26`, `V-05-41` | both streaming configs of the same family normalise with LayerNorm |
| `V-05-18` | the row a layer normalisation must reduce: the large recipes' width of 512 |
| `V-07-14` | the two coefficients of the base-two polynomial the same integer-only path uses on the softmax |


## A.6 From a Dimension to a Budget

**Intuition.** A width is not a cost. A cost is a count of stored numbers times the width of each, and
the book's arguments only become checkable at that point. Two kinds of numbers are stored, and they behave
oppositely: weights are fixed once training ends and are read over and over, while activations are
produced and consumed every step and are gone a moment later. Almost every architecture decision in this
book is a bet about which of the two is worth keeping close to the arithmetic.

**Mechanism.** The rule is one line:

> **The formula.** $\text{bytes} \;=\; \dfrac{\text{elements} \times b}{8}$
>
> **The variables.**
>
> - elements — how many values are being stored. A count, and the only term that comes from the
>   architecture: a tensor's shape, a weight file, a row of activations.
> - $b$ — the number of bits each stored value occupies. Bits per value. This is the word width,
>   and it is a design decision, not a property of the model.
> - $8$ — the number of bits in a byte. An exact constant, and the reason the division is a shift
>   by three rather than a divide.
> - bytes — the storage the pair implies. Bytes, and only comparable to a datasheet figure once the
>   unit convention below is settled.
>
> **What it means.** A width is not a cost; a cost is a count of stored numbers times the width of
> each. This is that sentence written once, and it is the point where the book's shape arguments
> become checkable: every earlier section in this appendix produced a count of elements, and this
> converts one into something a memory budget can absorb. The division by eight carries no
> information -- it is a change of unit, from the bits the arithmetic works in to the bytes the
> datasheets quote.
>
> **What it costs.** Nothing to compute, and everything to decide. The two terms are independent,
> so the storage falls linearly in $b$: halving the word width halves the bytes at any element
> count, which is the whole economic argument of chapter 7 stated as one line. On the device this
> book targets the result is compared against tiles, not against a smooth budget, so a total that
> lands one value over a tile boundary costs a whole tile more.
>
> **What it does not say.** It does not say the answer is the memory the design uses. It counts
> payload only: no addressing, no banking, no padding to a port width, no double buffering, and no
> copy that a runtime makes before the fabric sees the data. It also does not say which bytes are
> resident at once -- weights and activations both use this formula and behave oppositely, which is
> the distinction the intuition above is about. And a byte is not a bit: the unit convention below
> exists because this project's sources have disagreed about exactly that.

Before using it, a unit convention has to be chosen and
said out loud, because the datasheets in this project are not consistent and the registry has a record
filed about exactly that. Here, $1\ \text{Kb} = 2^{10}\ \text{bits}$, $1\ \text{KiB} = 2^{10}\ \text{bytes}$,
and a decimal $\text{kB}$ or $\text{MB}$ means a thousand or a million of the same. The datasheet's Mb
columns for this device are 1024-based, and that is the reading every figure below uses. The same record exists to warn that two different totals were each defensible under some reading of
a unit, and a sentence that mixes the conventions is wrong by a factor no rounding can repair.

The device's own on-chip storage, with each type named, is the following. The fabric holds 144 block
random-access memory (BRAM) blocks and 64 UltraRAM (URAM) blocks, one BRAM tile 36 Kb and one URAM tile
288 Kb. Their sum is 23,616 Kb, unrolled in full by the datasheet's memory table: 2,952 KiB, 3,022,848
bytes, 2.8828 MiB, or 3.02 MB in decimal units, and 3.13 MiB if the processing system's own 256 KB
on-chip memory is counted as well. That total is **BRAM plus URAM together**, and the two types are not
interchangeable in a design: BRAM on its own is 5.1 Mb, which is 0.6375 MiB computed from that figure by
dividing by eight, and the datasheet also lists 3.5 Mb of distributed RAM built from the same look-up
tables that
implement the logic. Calling 2.8828 MiB a "BRAM budget" would be the same class of unit error this book
already forbids for the four-megabyte figure in chapter 1, so both totals appear above with their types
named.

Now the model side. The three recipes whose sizes are published are the small offline keyword model at
about 14 million parameters, the streaming Conformer at about 120 million and the streaming FastConformer
at about 115 million -- one publisher's parameter count each. At two bytes per weight -- half-precision,
an assumption of this paragraph and not a record -- the small model's weights are 28 MB, a computed
figure, and the two large models are 240 MB and 230 MB, computed the same way. Set those beside the
device's 3.02 MB of on-chip storage and the conclusion is not close: the weights are roughly a hundred
times the
fabric's entire on-chip storage, so no overlay in this book can hold the model, and the design questions
in chapter 8 and chapter 9 -- what streams, what tiles, what stays, what gets re-read -- exist because of
that ratio.

> **What this appendix will not do, and why.** The counts above are storage for the whole model at a
> precision nobody registered. What is missing is not a rounding but a category: no record in
> `docs/verification/claims.json` gives multiply-accumulates per frame, integer (INT8) weight bytes,
> or activation bytes per step for any candidate model, and the registry carries that gap as an
> unresolved record on precisely those grounds. A budget in this book therefore stops where a record
> stops, and a table of
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

**Traceability.** The records this section leans on. Every byte product in the arithmetic above is
derived, and each derivation names the registered figures it spends; the rows below are those records read
as sources.

| Record | What it establishes here |
| --- | --- |
| `V-01-23` | the datasheet's Mb columns for this device are 1024-based; one BRAM tile 36 Kb, one URAM tile 288 Kb |
| `V-01-05` | the fabric holds 144 BRAM blocks |
| `V-01-07` | the fabric holds 64 URAM blocks |
| `V-01-22` | the storage total unrolled: 23,616 Kb, 2,952 KiB, 3,022,848 bytes, 2.8828 MiB, or 3.02 MB decimal, and 3.13 MiB with the 256 KB processing-system memory |
| `V-01-06` | BRAM alone totals 5.1 Mb |
| `V-01-16` | 3.5 Mb of distributed RAM, built from the same look-up tables as the logic |
| `V-05-16` | the small offline keyword model at about 14 million parameters |
| `V-05-33` | the streaming Conformer at about 120 million |
| `V-05-46` | the streaming FastConformer at about 115 million |
| `V-05-57` | unresolved on purpose: no publisher prints a word width, so no per-step byte count is derivable |
| `V-01-09` | the fabric's 1,248 multiply-accumulate slices, the divisor that turns an arithmetic floor into clocks |
