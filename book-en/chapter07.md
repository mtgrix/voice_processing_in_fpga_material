# Quantization That Respects the Hardware

> *Objective: Master Post-Training Quantization (PTQ) and Quantization-Aware Training (QAT) to compress speech models without degrading task-matched quality: accuracy/EER for keyword spotting, WER/CER for ASR, PESQ/STOI for enhancement. plan-v2.md section 5.3 forbids mixing metrics across tasks.*

---

## The cheapest coin in the whole machine, and what it buys wrong

Somewhere between the model that trains and the model that runs, the numbers get smaller. A weight or
an activation that a training framework stores in sixteen bits can be squeezed to eight, or four, or
fewer, and almost everything the FPGA is being brought in for improves when it does: a narrower number
is fewer wires to route, less memory to hold it, and less energy to move it across that memory, which
chapter 3 established is where the real cost lives. This chapter is about that squeeze and about the one
thing it costs in return. A smaller number is a *rounder* number. It cannot represent everything the
bigger one could, so the model makes errors it did not make before -- and unlike a software bug, those
errors are silent, bounded, and sometimes exactly where the task is most fragile.

The chapter's argument is that "how wrong" is not a single question but a task-shaped one, and the book
refuses to mix the answers. A keyword spotter has to keep telling "yes" from "no," and is measured by
accuracy. A recogniser has to transcribe, and is measured by how many words it gets wrong. An
enhancement model has to sound clean to a human ear, and is measured by perceptual scores that no
bit-width predicts on its own. Compressing a model without checking it against the *right* one of those
is how a design ships that is faster, smaller, and quietly worse at the only thing it was built to do.

So the chapter works through the ways to get the small numbers and the ways to check they still work.
It starts with where quantization noise actually hurts a speech signal, because that is not uniform
across the spectrum and not uniform across the layers. It then covers the two routes to a low-bit
model: taking a trained network and rounding it down afterwards, which is cheap but can break on a few
extreme values nobody happened to exercise, and training with the rounding baked in from the start,
which costs time up front but lets the network learn around its own coarseness. It ends on the
realistic compromise, which is that not every layer deserves the same number of bits -- the layers that
can take it get narrowed, the ones that cannot get left alone. This is the trade the preface names as the
narrowest of the three in this book, and it is the bridge between the arithmetic in appendix A and the
networks that chapter 8 and chapter 9 actually build onto the board.

---

## 7.1 Acoustic Sensitivity to Quantization Noise
## 7.2 Post-Training Quantization (PTQ) Calibration Strategies
## 7.3 Quantization-Aware Training (QAT) with Straight-Through Estimators
## 7.4 Layer-Specific Mixed-Precision Schemes

## 7.5 Integer-only softmax: the base-2 path

**Intuition.** Every stage in a quantized pipeline can be made of integer multiplies, integer adds and
shifts, except one. The softmax ends in an exponential, and the exponential is the part that resists
integer hardware: it is transcendental, its input is unbounded, and its intermediate values overflow a
fixed-point word long before its answer does. The usual software answer is a floating-point call to a
library the FPGA does not have. The literature this section reads does not accept that exception. Its
observation is that a softmax input can be made non-positive, and that a non-positive exponent splits
into an integer count and a short remainder, and that the integer half of that split is a bit position
rather than a computation. Only the short remainder needs an approximation, and a second-order
polynomial is enough for it. The record states the difficulty it is working around:

> "Approximating the Softmax layer with integer arithmetic is quite challenging, as the exponential
> function used in Softmax is unbounded and changes rapidly."

**Mechanism.** The path is four steps, and the first three of them are exact -- only the last one
approximates anything.

Make the input non-positive first, by subtracting the row's maximum:

> **The formula.** $\mathrm{Softmax}(x)_i \;=\; \dfrac{\exp(x_i - x_{\max})}{\sum_{j} \exp(x_j - x_{\max})}, \qquad x_{\max} = \max_i x_i$
>
> **The variables.**
>
> - $x_i$ — one score in the row the softmax is normalising. A signed fixed-point number, and before
>   this step its range is unbounded, which is the whole problem.
> - $x_{\max}$ — the largest score in the row. Found by one comparison pass over the row, and the
>   only thing this step needs to know about the input as a whole.
> - $\tilde{x}_i := x_i - x_{\max}$ — the shifted score. Non-positive by construction, and that is
>   the entire point of the step.
>
> **What it means.** Softmax is invariant under a common shift of every input, so subtracting the
> same maximum from the whole row does not change the answer at all; it changes only what the
> exponential has to accept. Every input to the exponential is now less than or equal to zero, so
> every exponential lies in $(0,1]$, and the function has gone from unbounded to bounded without an
> approximation being made. The record states the move and its consequence:
>
> > "First, we subtract the maximum value from the input to the exponential for numerical stability.
> > Note that now all the inputs to the exponential function, i.e., x̃i = xi − xmax, become
> > non-positive."
>
> **What it costs.** One comparison per element to find the maximum and one subtract per element to
> apply it. Comparisons and subtracts are look-up-table work on the fabric, and neither needs a DSP
> slice. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say the shifted values are small. A strongly negative score
> becomes a strongly negative $\tilde{x}$, whose exponential is close to zero, and whether that value
> survives the fixed-point word is a width decision this card does not make. The step bounds the top
> of the range and leaves the bottom exactly where it was, which is why the next card has to cut the
> bottom into pieces.

Split the non-positive input into an integer count and a short remainder:

> **The formula.** $\tilde{x} \;=\; (-\ln 2)\,z \;+\; p, \qquad z \in \mathbb{Z}_{\ge 0}, \qquad p \in (-\ln 2, 0]$
>
> **The variables.**
>
> - $\tilde{x}$ — the shifted score from the card above. Non-positive, which is the precondition the
>   decomposition needs.
> - $z$ — the quotient: how many whole steps of $\ln 2$ fit into $-\tilde{x}$. A non-negative
>   integer, and in fixed point it is the output of a floor, which is a wiring choice.
> - $p$ — the remainder, $\tilde{x} + z \ln 2$, lying in the half-open interval $(-\ln 2, 0]$. The
>   only part of the input that is not an integer, and the only part the next card has to
>   approximate.
> - $\ln 2$ — the natural logarithm of two, irrational. Both this step and the reconstruction below
>   use it, so the design holds it as a compile-time literal.
>
> **What it means.** Any non-positive real number can be written as so many steps of $-\ln 2$ plus a
> remainder that is shorter than one step. The split is exact, and it separates the exponential into
> two pieces with completely different characters: the integer $z$, which the next card turns into a
> bit position, and the remainder $p$, which never leaves an interval less than $\ln 2$ wide. The
> record states the decomposition:
>
> > "We can decompose any non-positive real number x̃ as x̃ = (−ln 2)z + p, where the quotient z is a
> > non-negative integer and the remainder p is a real number in (−ln 2, 0]."
>
> **What it costs.** One multiply by the reciprocal of $\ln 2$, one floor, and one multiply-add to
> recover $p$. With a quantised $\ln 2$ literal the whole step is two DSP48E2 slices and some wiring,
> and the floor costs nothing because it is the binary point itself. The book's own estimate, not a
> registered figure.
>
> **What it does not say.** It does not say the split survives fixed point unscathed. The two
> literals this step uses, $\ln 2$ and its reciprocal, are both irrational, so any fixed-point
> encoding of either is an approximation, and how many bits each one is given is a design decision
> this card inherits rather than settles.

Now take the two halves separately. The integer half is a power of two, and a power of two is exact:

> **The formula.** $\exp(\tilde{x}) \;=\; 2^{-z}\,\exp(p) \;=\; \exp(p) \;\gg\; z$
>
> **The variables.**
>
> - $z$ — the count from the card above. A non-negative integer, and here it is a shift amount: how
>   many bit positions the value moves.
> - $\exp(p)$ — the exponential of the remainder, a value in $(2^{-1}, 1]$. This card receives it as
>   the output of the split; the card below has to build it.
> - $\gg$ — the right-shift operator, written as it appears in the record. On the fabric this is a
>   barrel shifter: a network of multiplexers that moves a bit pattern by a variable amount and
>   performs no arithmetic.
> - $2^{-z}$ — two to a non-negative integer power. A single bit set at a position, which is a bit
>   pattern and not a computed value, and which is why the count never has to be exponentiated.
>
> **What it means.** This is the step that removes a transcendental function by reinterpreting bits.
> Dividing by two $z$ times is not calculated; it is a wiring connection, so the integer half of the
> exponential costs no arithmetic at all. Only the remainder survives as work, and the remainder is
> confined to an interval shorter than $\ln 2$. The record states the identity and then draws the
> conclusion that makes the whole path viable:
>
> > "Then, the exponential of x̃ can be written as: exp(x̃) = 2−z exp(p) = exp(p)>>z, where >> is the
> > bit shifting operation. As a result, we only need to approximate the exponential function in the
> > compact interval of p ∈ (−ln 2, 0]."
>
> The word to notice is "only". The interval that remains is less than $\ln 2$ wide, and that
> narrowness is what a second-order polynomial can hit.
>
> **What it costs.** A barrel shifter on the programmable logic, which is look-up tables and nothing
> else: zero DSP48E2 slices and zero block RAM. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say the shift is free of precision loss. A right shift moves
> bits out of the word, and a large $z$ shifts the small exponential away entirely. That is the
> numerically correct answer -- the value is negligible next to the row's maximum -- but only if the
> word is wide enough at the low end to keep the smallest value the softmax needs to distinguish. A
> barrel shifter that shifts a narrow word by a wide amount returns a wrong answer with no error
> flag.

The remainder is the only place an approximation enters, and a short polynomial is enough for it:

> **The formula.** $L(p) \;=\; 0.3585\,(p + 1.353)^{2} \;+\; 0.344 \;\approx\; \exp(p), \qquad p \in (-\ln 2, 0]$
>
> **The variables.**
>
> - $p$ — the remainder from two cards above, in $(-\ln 2, 0]$. The polynomial's only input, and a
>   fixed-point value whose bit width is the design's one accuracy knob.
> - $0.3585$ — the quadratic coefficient, the curvature that makes the approximation second-order
>   rather than a straight line. A compile-time literal, stored in the design.
> - $1.353$ — the centre shift, which moves the parabola's vertex left of the interval's midpoint so
>   the curve tracks $\exp(p)$ where it is steepest. Also a compile-time literal.
> - $0.344$ — the constant offset, which sets the value at the top of the interval; the polynomial
>   matches $\exp(0) = 1$ closely without being pinned to it.
> - $(p + 1.353)^{2}$ — the squared term, computed by one integer multiply of the shifted input by
>   itself.
>
> **What it means.** On $(-\ln 2, 0]$ the exponential rises smoothly over a range of less than two,
> and a parabola through that curve is close enough that a quantized network does not detect the
> difference. Two integer multiplies and two adds replace a table lookup or a floating-point call,
> and both operations are what the fabric is built for. The record gives the method the fit used,
> which matters more than the coefficients themselves, because the method is what a designer
> re-runs for a different interval or a different width:
>
> > "We use a second-order polynomial to approximate the exponential function in this range. To find
> > the coefficients of the polynomial, we minimize the L2 distance from exponential function in the
> > interval of (−ln 2, 0]."
>
> Substituting that polynomial into the identity above is the whole function, and the record names
> the result:
>
> > "Substituting the exponential term in Eq. 12 with this polynomial results in i-exp: i-exp(x̃) :=
> > L(p)>>z where z = ⌊−x̃/ ln 2⌋ and p = x̃ + z ln 2. This can be calculated with integer
> > arithmetic."
>
> **What it costs.** Two DSP48E2 slices for the two multiplies and no block RAM, because nothing is
> stored. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say the polynomial equals $\exp(p)$, and unlike the previous
> edition of this section it does not have to leave the tolerance to the imagination: the record
> registers it. The largest gap between the polynomial and the true exponential is 0.0019, and the
> quantization that eight bits introduce over a unit interval is 0.0039, one part in 256, so the
> approximation's worst case is smaller than the error of the number format it feeds. That is the
> strongest thing a fitted polynomial in a quantised network can claim, and the record says the error
> "can be subsumed into the quantization error." The three literals 0.3585, 1.353 and 0.344 are also
> only as accurate as the width each one is given, and this card does not set those widths.

The four steps assemble into one datapath, and [Figure 26](#fig-integer-softmax-datapath) draws it as a
chain with one branch in it.

::: {#fig-integer-softmax-datapath .figure}
```tikz
% The integer-only exponential as a chain: subtract the row maximum, decompose what is left in
% units of ln 2, then two branches -- the integer count z becomes a shift amount, the remainder p
% becomes a second-order polynomial -- rejoining at one right shift.
% The box width and the gap before the final shift are tuned to the text block. header.tex sets
% hfuzz=2pt, so an over-wide float prints no error: the build stays quiet and the picture runs into
% the margin. A wider version of this chain measured 465pt against a 444pt text block, which
% figprobe reports and the full build does not.
\begin{tikzpicture}[
  node distance=5mm,
  box/.style={draw, align=center, inner sep=3pt, font=\scriptsize, text width=16mm, minimum height=10mm},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[box] (x) {$x$};
\node[box, right=of x] (sub) {subtract $x_{\max}$};
\node[box, right=of sub] (dec) {decompose in $\ln 2$};
\node[box, above right=2mm and 5mm of dec] (zbox) {count $z$};
\node[box, below right=2mm and 5mm of dec] (poly) {polynomial $L(p)$};
\node[box, right=14mm of poly] (shift) {shift right by $z$};
\node[box, right=of shift] (out) {i-exp$(\tilde{x})$};
\draw[arr] (x) -- (sub);
\draw[arr] (sub) -- (dec);
\draw[arr] (dec) -- (zbox) node[midway, above, font=\scriptsize, inner sep=1pt] {$z$};
\draw[arr] (dec) -- (poly) node[midway, below, font=\scriptsize, inner sep=1pt] {$p$};
\draw[arr] (poly) -- (shift);
\draw[arr] (zbox) -| (shift.north);
\draw[arr] (shift) -- (out);
\end{tikzpicture}
```
The integer-only exponential of section 7.5: one subtract that bounds the input, a decomposition that is mostly wiring, a two-multiply polynomial on the short remainder, and one right shift that costs no arithmetic. Only the polynomial box approximates anything; the shift is exact.
:::

**Application.** This shape suits the KV260 for a reason the record states directly: the path avoids
look up tables and "strive[s] for a pure arithmetic based approximation." Every operation the datapath
names is native to the fabric. Shifts and integer multiplies are what the programmable logic is built
out of, a constant multiply by $\ln 2$ or its reciprocal is one slice or wiring, and the absence of a
lookup table is the property that matters on a device whose block RAM is the scarcest resource in the
design -- the memory a table would occupy is memory the buffers of chapter 9 can use instead. The
polynomial's two multiplies are ordinary DSP48E2 work, and they are the same kind of work the
convolution datapath of section 8.2 already schedules.

The record is also careful about what is new here. A variant of this decomposition was used in the
Itanium 2, and the paper's one-line description of it ends "but with a look up table for evaluating
exp(p)." So the shift idea is not novel; what this path contributes is the removal of the table, which
is the part that makes it fit a small FPGA rather than a server processor.

What this does not buy is a normalising divide. The softmax still ends in a division by a row sum, and
that sum is not a power of two just because the exponential now is. Section 8.3 is where this book
derives a power-of-two form for that normalising shape, and the two arguments are separate: the
exponential card above replaces a transcendental, the normalisation card replaces a divide, and a
design that adopts one has not thereby got the other. What the path also does not do is certify itself
for a given model. The error budget is registered and favourable, but whether it is *enough* is a task
question, and that measurement belongs to the acceptance gate of section 8.4, not to this card.

**Traceability.** The records this section leans on. The resource counts in the equation cards above
are the book's own estimates, not registered figures, and are printed as words for that reason;
everything else is a registered claim.

| Record | What it establishes here |
| --- | --- |
| `V-07-11` | the challenge statement, the maximum subtraction, and the ln-2 decomposition x̃ = (−ln 2)z + p |
| `V-07-12` | the shift identity exp(x̃) = 2^(−z) exp(p) = exp(p) >> z, and the interval (−ln 2, 0] it leaves |
| `V-07-13` | the polynomial L(p) = 0.3585(p + 1.353)² + 0.344 and the L2 fit that produced it |
| `V-07-14` | the assembled i-exp(x̃) := L(p) >> z, with z = ⌊−x̃/ln 2⌋ and p = x̃ + z ln 2 |
| `V-07-15` | that the path avoids look up tables and is pure arithmetic |
| `V-07-27` | the error budget: largest gap 0.0019 against the 0.0039 eight-bit quantisation introduces |
