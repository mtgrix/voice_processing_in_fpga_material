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
integer hardware: it is transcendental, its intermediate values overflow a fixed-point word long
before its answer does, and the usual software answer is a floating-point call to a library the FPGA
does not have. The literature this section reads does not accept that exception. It rewrites the same
function so that the transcendental part disappears into a bit position and a short polynomial, and a
quantized pipeline then stays integer end to end with no lookup table of any size. The record states
the move plainly:

> "Calculating the exponential function $e^x$ directly with integer arithmetic is notoriously
> difficult due to overflow and precision loss. We reformulate $e^x$ by converting the natural base
> $e$ into base 2: exp(x) = 2^(x * log2(e))"

**Mechanism.** The path is four steps, and the first three of them are exact -- only the last one
approximates anything.

Change the base of the exponential first:

> **The formula.** $\exp(x) \;=\; 2^{\,x \log_2 e}$
>
> **The variables.**
>
> - $x$ — one input value to the exponential: a single score after the row's maximum has been
>   subtracted, so $x \le 0$ and the answer lies in $(0,1]$. A fixed-point number, in this book's
>   design.
> - $\log_2 e$ — the change of base from $e$ to $2$: the single constant that converts a
>   natural-base exponent into a base-two one, about $1.4427$. A pure number, and a compile-time
>   literal in hardware rather than something a design computes.
> - $x \log_2 e$ — the same exponent, now expressed in base two. Call it $z$.
>
> **What it means.** The exponential is unchanged in value; only the base it is written in changes.
> Writing it in base two is what makes the rest of the path possible, because a power of two is a
> bit position, and a bit position is something a shift can reach. Nothing has been made integer
> yet -- $x \log_2 e$ is still a fraction -- but the function is now in the shape integer hardware
> can act on.
>
> **What it costs.** One constant multiply by $\log_2 e$, which is one DSP48E2 slice or, if the
> literal is chosen as a sum of powers of two, wiring alone. The book's own estimate, not a
> registered figure.
>
> **What it does not say.** It does not say the multiply is free of error. $\log_2 e$ is irrational,
> so any fixed-point literal of it is an approximation, and the width that literal is given is a
> design decision this card does not make. It also says nothing about $x$'s own range: the
> subtraction of the row maximum in section 8.3 is what keeps that range safe, and without it this
> step overflows for exactly the reason the record above names.

Split the base-two exponent into its integer and its fraction:

> **The formula.** $z \;=\; x \log_2 e, \qquad z = q + p, \qquad q = \lfloor z \rfloor, \qquad p = z - q$
>
> **The variables.**
>
> - $z$ — the base-two exponent from the card above. A signed fixed-point number, non-positive when
>   $x$ is.
> - $q$ — the integer part of $z$, taken by the floor: the greatest integer not exceeding $z$. A
>   signed count of doublings or halvings, and in a fixed-point word it is simply the bits above the
>   binary point, read as an integer.
> - $p$ — the fractional part, $z - q$. A value in $[0,1)$ by construction, and the only part of the
>   exponent that is not a bit position.
> - $\lfloor \cdot \rfloor$ — the floor function, which rounds towards minus infinity. On the chip
>   this is not a rounding operation at all: it is selecting which wires to read, because the split
>   already exists in the bit pattern.
>
> **What it means.** A fixed-point number is an integer part and a fraction part sitting side by side
> in one word, separated by the binary point. Splitting $z$ at that point separates the two halves of
> the problem, and the two halves are solved by two completely different kinds of circuit: the
> integer part by wiring, the fraction part by arithmetic. The record states the split exactly:
>
> > "Let z = x * log2(e). We decompose z into its integer component q and fractional component p in
> > in $[0, 1)$: z = q + p, where q = floor(z), p = z - q"
>
> **What it costs.** The floor costs zero DSP48E2 slices and zero block RAM, because it is a wiring
> choice and not a computation: route the bits above the binary point to one output and the bits
> below it to another. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say the split is lossless in the sense that matters. The
> floor throws away no information -- $q$ and $p$ together are exactly $z$ -- but $p$ carries fewer
> significant bits than $z$ did below the binary point only if the word was wide enough to hold them.
> How many bits $p$ keeps is the word-width decision the next card inherits, and this card does not
> settle it.

Now take the two halves separately. The integer part is a power of two, and a power of two is exact:

> **The formula.** $2^{z} \;=\; 2^{q}\cdot 2^{p}, \qquad 2^{q} \;=\; \texttt{1 << q}$
>
> **The variables.**
>
> - $q$ — the integer part from the card above. A signed integer, and here it is a shift amount: how
>   many places a bit is moved.
> - $p$ — the fractional part, in $[0,1)$. Handed to the next card, not used here.
> - $2^{q}$ — two raised to an integer power. A single bit set at position $q$, which is a bit
>   pattern and not a computed value.
> - $\texttt{1 << q}$ — the left-shift operator of a hardware description language: place the value
>   one at bit position $q$. Negative $q$ means shift right, which is the same network run the other
>   way.
> - $2^{p}$ — the fractional-power term, in $[1,2)$. This card produces it as an output of the split;
>   the card below has to build it.
>
> **What it means.** This is the step that removes a transcendental function by reinterpreting bits.
> Two to an integer power is not calculated; it is a wiring connection, so the entire integer half of
> the exponent costs no arithmetic at all. The record states it as a hardware fact:
>
> > "Here, 2^q can be computed exactly using a simple hardware bit-shift operation: 1 << q. The term
> > 2^p for p in $[0, 1)$ is approximated with a second-order polynomial using integer multiplication
> > and addition"
>
> The word "exactly" is doing real work in that sentence, and it is the only place in the path where
> the claim is exactness rather than approximation.
>
> **What it costs.** A barrel shifter, which is a network of multiplexers that moves a bit pattern by
> a variable amount and performs no arithmetic. On the KV260's programmable logic that is look-up
> tables and nothing else: zero DSP48E2 slices, zero block RAM. The book's own estimate, not a
> registered figure.
>
> **What it does not say.** It does not say the shift is free of precision loss. A left shift into
> bits the word does not have throws information away, and a right shift out of the word drops bits
> below the resolution the design keeps. Sizing the result word is the designer's job, and a barrel
> shifter that shifts a narrow word by a wide amount returns a wrong answer with no error flag.

The fraction is the only place an approximation enters, and a short polynomial is enough for it:

> **The formula.** $2^{p} \;\approx\; 1 \;+\; 0.6958\,p \;+\; 0.2250\,p^{2}, \qquad p \in [0,1)$
>
> **The variables.**
>
> - $p$ — the fractional part from two cards above, in $[0,1)$. The polynomial's only input, and a
>   fixed-point value whose bit width is the design's one accuracy knob.
> - $0.6958$ — the linear coefficient, a constant fitted so the parabola tracks $2^{p}$ across the
>   unit interval. A compile-time literal, stored in the design.
> - $0.2250$ — the quadratic coefficient, the curvature that makes the approximation second-order
>   rather than a straight line. Also a compile-time literal.
> - $1$ — the value at $p = 0$, which the polynomial matches exactly because $2^{0} = 1$.
> - $p^{2}$ — the squared input, computed by one integer multiply of $p$ by itself.
>
> **What it means.** On $[0,1)$ the function $2^{p}$ rises smoothly from one to two, and a parabola
> through that curve is close enough that a quantized network does not detect the difference. Two
> integer multiplies and two adds replace a table lookup or a floating-point call, and both
> operations are what the fabric is built for. The record gives the coefficients and the form:
>
> > "The term 2^p for p in $[0, 1)$ is approximated with a second-order polynomial using integer
> > multiplication and addition: 2^p approx 1 + 0.6958 p + 0.2250 p^2"
>
> **What it costs.** Two DSP48E2 slices for the two multiplies and no block RAM, because nothing is
> stored. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say the polynomial equals $2^{p}$. It says a fitted parabola
> is within some tolerance of it across the unit interval, and that tolerance, as a number, is not
> registered anywhere in this repository -- so this book prints no error figure and a designer who
> treats the approximation as exact has made the mistake the card exists to prevent. The
> approximation is also only as good as the fixed-point literals $0.6958$ and $0.2250$ are wide, and
> the card says nothing about how many bits each one is given.

The four steps assemble into one datapath, and [Figure 21](#fig-base2-softmax-datapath) draws it as a
chain with one branch in it.

::: {#fig-base2-softmax-datapath .figure}
```tikz
% The integer-only exponential as a chain: scale by log2 e, split at the binary point, then two
% branches -- a shift on the integer part, a second-order polynomial on the fraction -- rejoining
% at one multiplier.
\begin{tikzpicture}[
  node distance=6mm,
  box/.style={draw, align=center, inner sep=3pt, font=\scriptsize, text width=16mm, minimum height=10mm},
  arr/.style={-{Stealth[length=1.8mm]}, thick},
]
\node[box] (x) {$x$};
\node[box, right=of x] (mul) {$\times\;\log_2 e$};
\node[box, right=of mul] (split) {split at binary point};
\node[box, above right=3mm and 5mm of split] (shift) {shift $1 \ll q$};
\node[box, below right=3mm and 5mm of split] (poly) {$1 + 0.6958\,p + 0.2250\,p^2$};
\node[box, right=of shift, text width=12mm] (prod) {multiply};
\node[box, right=of prod] (out) {$2^{\,x\log_2 e}$};
\draw[arr] (x) -- (mul);
\draw[arr] (mul) -- (split);
\draw[arr] (split) -- (shift) node[midway, above, font=\scriptsize, inner sep=1pt] {$q$};
\draw[arr] (split) -- (poly) node[midway, below, font=\scriptsize, inner sep=1pt] {$p$};
\draw[arr] (poly) -| (prod);
\draw[arr] (shift) -- (prod);
\draw[arr] (prod) -- (out);
\end{tikzpicture}
```
The integer-only exponential of section 7.5: one constant multiply, a split that is wiring, a shift that costs no arithmetic, and a two-multiply polynomial on the fraction.
:::

**Application.** This shape suits the KV260 for a reason the record states directly: the whole path
"replaces transcendental floating-point computation with integer arithmetic and bit-shifts, without
requiring large lookup tables." Every operation the datapath names is native to the fabric. Shifts and
integer multiplies are what the programmable logic is built out of, a constant multiply by $\log_2 e$
is one slice or wiring, and the absence of a lookup table is the property that matters on a device
whose block RAM is the scarcest resource in the design -- the memory a table would occupy is memory
the buffers of chapter 9 can use instead. The polynomial's two multiplies are ordinary DSP48E2 work,
and they are the same kind of work the convolution datapath of section 8.2 already schedules.

What this does not buy is an error budget. Whether the approximation is accurate enough for a given
model is a numerical question, and it is a question this book does not settle: no record here
registers the polynomial's error against the true $2^{p}$, so this section prints no tolerance and
claims none. A design that adopts the path must measure the effect on its own task metric -- accuracy,
EER or WER, whichever the model in question is judged by -- and that measurement belongs to the
acceptance gate of section 8.4, not to this card. The path also does not make the softmax's
*normalising* divide integer; section 8.3 is where this book derives a power-of-two form for that
shape, and the two arguments are separate.

**Traceability.** The records this section leans on. The resource counts in the equation cards above
are the book's own estimates, not registered figures, and are printed as words for that reason;
everything else is a registered claim or a registered absence.

| Record | What it establishes here |
| --- | --- |
| `V-07-11` | the base-2 reformulation of the exponential, exp(x) = 2^(x * log2(e)) |
| `V-07-12` | the split of the exponent into an integer part and a fraction, z = q + p |
| `V-07-13` | that the integer power is exact as a hardware bit-shift, 2^q = 1 << q |
| `V-07-14` | the two coefficients of the second-order polynomial, 0.6958 and 0.2250 |
| `V-07-15` | that the path needs no large lookup tables, only integer arithmetic and shifts |
