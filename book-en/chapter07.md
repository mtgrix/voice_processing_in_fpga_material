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

> ### Minimal Mathematics / Prerequisites for this Chapter
>
> - **Dynamic range in decibels**: the span between a signal's loudest and quietest meaningful
>   parts, and how wide a number has to be to hold both at once.
> - **Rounding error as a bounded step**: a fixed-point number is a rounded real number, wrong by at
>   most half a step, and the noise-floor arguments in this chapter start from that bound.
> - **A quotient and a remainder**: splitting one number into a whole part and a leftover shorter
>   than one step, which is school arithmetic with a hardware meaning and the foundation of
>   section 7.5.
> - **A matrix product as rows of dot products**: a quantized network is a stack of such rows, and
>   every cost count in the chapter is a count of multiply-accumulates.
> - **A power of two as a shift**: dividing by a power of two is wiring, not arithmetic, which is
>   why the base-two path of section 7.5 can be integer-only.

---

## 7.1 Acoustic Sensitivity to Quantization Noise

*Where this sits in the chain: the* **Model** *stage -- the width decisions this chapter makes are
decisions about the numbers the acoustic model multiplies, and the fixed-point front end of chapter 6
has already decided the noise floor on the features that arrive here.*

**Intuition.** A photograph has one brightness range for the whole frame, and an eight-bit image
carries its quantization noise fairly evenly across it. Speech is not like that. A voice swings
between a loud vowel and a quiet consonant, and the quiet parts -- the fricatives, the breaths, the
word endings -- carry meaning at a level far below the average. Quantization drops a fixed-size noise
floor on top of every sample, and when that floor sits above the quiet parts, a recogniser cannot tell
a soft consonant from the noise that replaced it. The average is no comfort: a model can lose every
low-energy phoneme and still pass a mean-squared-error check, because the loud frames dominate the
sum.

**Mechanism.** Treat the quantizer as an additive noise source and measure it. A uniform quantizer
with step size $\Delta$ turns the rounding of each value into an error bounded by half a step, and the
variance of that error is one twelfth of the step squared:

> **The formula.** $\sigma_{q}^{2} \;=\; \dfrac{\Delta^{2}}{12}, \qquad \Delta \;=\; \dfrac{r_{\max} - r_{\min}}{2^{b} - 1}$
>
> **The variables.**
>
> - $\Delta$ — the step size: the quantized range split into $2^{b} - 1$ pieces of equal width.
> - $b$ — the word width in bits.
> - $r_{\max}, r_{\min}$ — the edges of the range the quantizer can represent.
> - $\sigma_{q}^{2}$ — the variance of the rounding error: the noise floor this section keeps
>   coming back to.
>
> **What it means.** Rounding error under a fine uniform quantizer spreads evenly across one step,
> and the variance of that spread is a twelfth of the step squared. Doubling the width halves the
> step, and halving the step cuts the noise power by a quarter -- about six decibels, in the view the
> next card takes. The formula is the book's own derivation from the uniform-quantizer model, not a
> registered figure.
>
> **What it costs.** Nothing to compute, because this is a variance, not a circuit. What it does is
> fix the currency of the chapter: the noise floor is set by the step, the step is set by the range
> and the width, and the width is wires, memory and lanes of arithmetic, so the floor carries a
> hardware price exactly where the next sections spend it.
>
> **What it does not say.** It does not say the error is white in a speech signal, or that the range
> is known before the model runs. Both are assumptions, and the formula holds only while they hold.
> The next card keeps the ideal model and adds the one speech fact that changes the answer.

The useful measure is how far a real speech sample sits above that floor. The familiar law for a
full-scale sinusoid gives about six decibels per bit plus a small constant, but speech is not a
sinusoid: it swings from peak to average, and the ratio between the two -- the crest factor, which the
book estimates at twelve to eighteen decibels for conversational speech -- spends part of every width
before the quantizer has done anything:

> **The formula.** $\mathrm{SQNR}_{\text{speech}} \;\approx\; 6.02\, b \;+\; 1.76 \;-\; 10 \log_{10}(\mathrm{PAR})$
>
> **The variables.**
>
> - $b$ — the width in bits.
> - $6.02$ — the decibels gained per bit, the slope of the ideal uniform quantizer.
> - $1.76$ — the constant the ideal sinusoid model adds on top.
> - $\mathrm{PAR}$ — the peak-to-average ratio of the utterance, the crest factor. Twelve to
>   eighteen decibels for conversational speech: the book's own estimate, not a registered figure.
>
> **What it means.** Each extra bit buys about six decibels of floor, and speech's own swing from
> peak to average spends part of that before the quantizer does anything. A component that sits forty
> decibels below full scale -- the energy a fricative carries, again the book's own estimate -- then
> sees a floor that much closer. The quiet content is protected not by the average signal level but
> by the width left after the crest factor is paid, which is why the first question of any
> quantization budget is this one: how many decibels does the quietest meaningful part need?
>
> **What it costs.** Choosing $b$ pays in every currency the fabric charges: one bit is one wire per
> value, one cell per stored value, one lane per arithmetic unit. The speech statistics in this card
> are estimates, not registered figures, and the traceability table at the end of the section marks
> the records the rest of the argument leans on.
>
> **What it does not say.** It does not say the signal-to-quantization-noise ratio is the task
> metric. A recogniser is judged on word error rate, a spotter on accuracy or equal-error rate, an
> enhancer on perceptual scores, and the numbers in this card only say which widths make those gates
> reachable. It also does not say every layer hears the same crest factor: the log-Mel front end
> compresses the dynamic range before the model sees the features, so a layer fed compressed inputs
> meets a different noise trade than one fed raw spectral energy.

**Application.** The consequence is memory traffic, and the records give the ladder. An arithmetic
operation on the kinds of accelerators this book studies costs one unit of energy, moving a value into
on-chip memory costs more than that, and moving it off-chip costs two hundred times the arithmetic
figure -- a gap the record registers as two orders of magnitude. A narrower word is worth
proportionally more the farther the number travels, which is why quantization earns its keep on an
FPGA: the fabric's ridge point, the compute density below which a design is memory-bound, sits
between thirty-nine and seventy-eight operations per byte on the KV260 and at roughly four hundred
and ninety on the Orin NX. The KV260 side of the book's comparison therefore lives or dies on how many
bytes a model moves, and every bit a quantization scheme removes from the weight stream is a byte that
never crosses that ridge.

The second consequence is the gate. However the width is chosen, acceptance has to be measured on the
task's own metric, and nothing in this section changes that: accuracy for a spotter, word or character
error rate for a recogniser, perceptual scores for an enhancer. A design that trades a generic
signal-to-noise figure against those gates is measuring the wrong thing, and this chapter does not.

**How the front end spreads the noise: SQNR across log-Mel bands.**

The crest factor spent the width on the waveform, but the model does not multiply the waveform. The front end of chapter 6 compresses the spectrum before the model sees it: the energy the mel filterbank sums is converted to ten times its common logarithm, so each feature is a reading in decibels. A logarithm turns a multiplicative range into an additive one. In the linear domain a loud band can sit one thousand times above a quiet one, a span of thirty decibels, computed as ten times the common logarithm of one thousand, and a step that reaches the loudest value is far too coarse to resolve the quietest. After the log the same span is thirty decibels, and a fixed step represents the same number of decibels everywhere along it. That is the good news of the front end, and also the trap: the floor becomes uniform in decibels, but the signal that stands above the floor is not.

The mechanism is a derivative. Let the linear energy of mel band $b$, as the front end measures it after the filterbank sum, be $P_{b}$, and let the fixed-point path carry a step $\delta$ in that linear domain. The reading the model multiplies is $y_{b} = 10 \log_{10} P_{b}$, and a linear error of one step perturbs the reading by the derivative of the mapping at the band's own level:

> **The formula.** $y_{b} \;=\; 10\,\log_{10} P_{b}, \qquad \Delta y_{b} \;\approx\; \dfrac{10}{\ln 10}\, \dfrac{\delta}{P_{b}}$
>
> **The variables.**
>
> - $P_{b}$ — the linear energy of mel band $b$ as the front end measures it, after the filterbank sum.
> - $y_{b}$ — the reading in decibels that the model actually multiplies.
> - $\delta$ — the quantization step of the linear path: the smallest change in $P_{b}$ the fixed-point front end can represent.
> - $\Delta y_{b}$ — the resulting error in the reading, in decibels.
>
> **What it means.** A logarithm is a per-band derivative machine. The change in the reading equals the derivative of the mapping at the band's own level multiplied by the change in the level, and the derivative falls as the level rises: it is ten over the natural logarithm of ten, divided by the band's linear energy. The same absolute step therefore becomes a large decibel error on a quiet band and a small one on a loud band; the band error is inversely proportional to the band's linear level, derived from the derivative of the logarithmic mapping.
>
> **What it costs.** The quiet bands pay in the currency section 7.1 set. Their margin below the loudest band is exactly the factor by which the step's decibel error is amplified: a band ten decibels below the loudest hears the step enlarged ten times, computed as ten raised to the quotient of ten by ten, and a band forty decibels below hears it enlarged ten thousand times, computed by the same rule. The floor does not move; the signal it lands on is what shrinks.
>
> **What it does not say.** It does not say the model's own quantizer lives in the linear domain. If the quantizer works after the log, which is where the front end delivers the reading, the step is already a step in decibels and the same absolute error lands on every band; the quiet band's difficulty is then the small signal above the floor rather than an amplified step. Both readings follow from the same derivative, seen from the two sides of the logarithm, and the close of this block takes the log-domain view because that is the arithmetic the model performs.

The unit deserves one plain sentence, because the whole argument lives in it. A decibel is a ratio stated on a logarithmic scale, and a log-Mel reading is a number of decibels, so a step in the reading is a step in decibels wherever it lands. The model's INT8 grid is therefore uniform in decibels too: each cell of the grid covers the same number of decibels on every band, and the resolution a band gets is equal to every other band's rather than proportional to its loudness. That equality is the front end's purpose, the compression the intuition of the section promised: the logarithmic map is what lets one grid serve a dynamic range no fixed-point linear scale could hold in eight bits. What the map cannot do is enlarge the quiet band's content; it can only make the floor uniform. The uniform floor is the price, and the derivation above is the receipt: every band's margin is measured from the same floor, so the band that sits far down the ladder starts that much closer to the noise, whatever the grid's step is.

The eighty mel bands the front end runs across, registered as `V-05-35`, each bring their own linear level to the log, and speech does not fill them evenly. The voiced parts spend their energy at the low mel indices, where the vowels live; the high-mel bands carry the fricatives, the breaths and the word endings, the content section 7.1's crest-factor estimate already flagged as the quietest meaningful parts of the utterance. For those bands the reading is small while the floor is the same absolute number of decibels below every reading the range touches, so the band's own margin above the floor is smaller by exactly how far the band sits below the top of the range. That is the crest factor replayed at one band: the loudest band pays the wave-form's peak-to-average swing, and every quieter band pays its own swing on top, band by band, down the eighty-band ladder the front end delivers. Averaging the noise over the frame helps as little here as it did in the intuition of the section: the loud low-mel bands dominate the mean, and a model can lose the quiet high-mel content and still pass a mean-squared-error check on the features at large.

The ladder's bottom is where the book's own figures make the problem concrete. The energy ladder of the section's Application prices an off-chip access at two hundred times an arithmetic operation, and the ridge point that separates memory-bound from compute-bound designs is where the extra width shows up first: a feature that must survive the memory budget pays for every bit it carries across that ridge. Quantizing the quiet band is therefore not cosmetic, because on the batch-one streaming shape every hop is a fresh trip across the ridge, and the quietest band's margin is the one that decides whether the quantization error is a lost phoneme or merely a presence in the noise floor. A design that treats the loud and quiet bands as one population inherits the loudest band's step for the whole eighty-band ladder, including the bands that needed the finest steps most. That is the sentence section 7.2 exists to answer, and the close of this block states it plainly.

The practical reading is the one that surprises. INT8 at the quietest band is not INT8 at the utterance as a whole, because one eight-bit grid covers all eighty mel bands `V-05-35` and the grid is a single range. Calibration chooses where that range sits, and the estimator is where the choice becomes concrete. A maximum-minimum range that must also hold the loudest transient the stream has made stretches the decibel step, and the stretch is paid first by the bands with the least margin: the quiet high-mel bands whose content sits a short distance above the floor have the most to lose from a step that grows to protect a peak the task never reads. The estimator that protects them is the one that refuses to let the loud tail own the step, clipping it so the range is set by the level the task actually uses, or choosing the clipping point that keeps the most signal. That is section 7.2's estimator menu in one sentence: the choice between stretching the step to include the tail and clipping the tail to protect the band is the choice this chapter hands to calibration. This section fixed the floor; the next one chooses where the clipper sits.


**Traceability.** The records this section leans on. The speech statistics -- the crest factor, the
dynamic range, the fricative level -- are the book's own estimates, not registered figures, and are
printed as words for that reason; the energy ladder and the ridge points are registered claims.

| Record | What it establishes here |
| --- | --- |
| `V-07-06` | the energy ladder: an off-chip access costs two hundred times an arithmetic operation |
| `V-07-07` | the same gap as two orders of magnitude between off-chip and on-chip memory |
| `V-07-26` | the sizes of the register file, global buffer and network a dataflow engine works in |
| `V-07-02` | the Orin NX ridge point, the reference the GPU side is measured against |
| `V-07-03` | the KV260 ridge point, the memory-bound regime this chapter's savings target |
| `V-05-35` | the eighty mel bands the log-Mel analysis runs across |

---

## 7.2 Post-Training Quantization (PTQ) Calibration Strategies

*Where this sits in the chain: the* **Model** *stage -- the first of the chapter's two routes to a
small number, applied to a network that already trained in floating point.*

**Intuition.** A trained network is a finished object, and post-training quantization (PTQ) rounds it
in place. The only free decision is where the clipper sits. Quantize a range that is too tight and the
loudest values saturate; widen the range to save them and every value gets a fatter step, so the
rounding grows everywhere. Somewhere between the two is a clipping point the task tolerates, and
calibration is the art of finding it from data. The subtlety this section cares about is that the two
halves of a quantized number carry very different hardware prices: the scale is a multiply, while the
zero point is a correction that can demand a second pass over streaming data.

**Mechanism.** The arithmetic is affine: every real number the layer sees is an integer times a step,
shifted by a zero point. The record formulates it as one equation:

> **The formula.** $r \;=\; S\,(q - Z)$
>
> **The variables.**
>
> - $r$ — the real value the quantized number represents.
> - $q$ — the stored integer.
> - $S$ — the scale: the real step each integer counts for.
> - $Z$ — the zero point: the integer that represents zero, the affine shift.
>
> **What it means.** A quantizer is one real multiply of an integer with a shift folded in. When
> $Z = 0$ the form is symmetric, a scale around zero; when $Z \neq 0$ it is asymmetric, or affine,
> shifted. The affine form is the one Jacob and colleagues defined in their 2018 CVPR paper, and it is
> the shape every tool in this section builds on.
>
> **What it costs.** The scale is a multiply, already the fabric's ordinary work. The zero point is
> an add, trivial by itself and the source of an entire correction pass inside a matrix product;
> the next card works out where that expense lands.
>
> **What it does not say.** It does not say $S$ and $Z$ are known. Nothing in this equation tells a
> designer how to choose them, and choosing them is the calibration problem the rest of the section
> is about.

The zero point is the expensive idea, and the reason is the cross term. Multiply two quantized
numbers and the affine shifts interact:

> **The formula.** $\displaystyle \sum_{k} r^{(w)}_{k} r^{(a)}_{k} \;=\; S_{w} S_{a} \Bigg[ \sum_{k} q^{(w)}_{k} q^{(a)}_{k} \;-\; Z_{w} \sum_{k} q^{(a)}_{k} \;-\; Z_{a} \sum_{k} q^{(w)}_{k} \;+\; K\, Z_{w} Z_{a} \Bigg]$
>
> **The variables.**
>
> - $q^{(w)}_{k}, q^{(a)}_{k}$ — the integer weights and activations along the shared reduction
>   index $k$.
> - $Z_{w}, Z_{a}$ — the zero point of each side.
> - $S_{w}, S_{a}$ — the scale of each side.
> - $K$ — the length of the reduction.
>
> **What it means.** The core term in the brackets is the integer multiply-accumulate the fabric does
> natively. Each nonzero zero point adds a correction on top of it. With both zero points zero -- the
> symmetric case -- the two correction sums vanish and the whole product is one pass of
> multiply-accumulates. With an asymmetric activation alone, $Z_{a} \neq 0$, the term
> $Z_{a} \sum_{k} q^{(w)}_{k}$ sums weights, which are constants, so it folds into a per-output bias
> before the design starts. The expensive case is an asymmetric weight, $Z_{w} \neq 0$: the term
> $Z_{w} \sum_{k} q^{(a)}_{k}$ needs a live sum of each activation row, a second reduction inside the
> datapath. That asymmetry -- weights are static, activations stream -- is why this section pushes
> weights toward symmetric. The expansion is the section's own derivation from the registered affine
> form, not a separate registered figure.
>
> **What it costs.** An asymmetric weight zero point buys a second adder tree and a correction
> multiply per output; the symmetric path buys none of it. On the KV260 the price lands in look-up
> tables and routing rather than in the DSP slices themselves, because the board's 1,248 slices do
> the same multiply either way; the extra tree lives beside them in logic. The book's own estimate,
> not a registered figure.
>
> **What it does not say.** It does not say asymmetric activations are unaffordable -- they are the
> common case, and a single $Z_{a}$ folds into bias. It says the *weight* zero point is the expensive
> one, and it does not say a cleverer dataflow could not amortize the row sums across many outputs;
> it says the plain design pays twice.

Before calibration can even start, the graph has to be clean. A convolution followed by batch norm is
two affine transforms in a row, and the toolchain folds the norm into the weights first -- the record
documents the eval-mode guard that keeps the fold off the training path and the per-channel rescale
that applies it -- so the quantizer sees one layer instead of two. Calibrate after the fold, not
before it.

That leaves the estimator, and the tools register the menu. Min-max calibration takes the observed
extrema; the trouble is that streaming speech has outliers the task never needs, and a range stretched
by an extreme value fattens every step. Percentile calibration clips a small upper tail, at
$99.99\%$ of the distribution in the usual setting. Entropy, or KL, calibration chooses the clipping
point that moves the least information, and mean-squared-error calibration chooses the one that
minimises the expected rounding loss. The registered tool exposes all four -- maximum-minimum,
percentile, entropy and MSE -- together with the rounding modes half-even, half-up, half-down and
stochastic, and it documents the combinations it refuses: the entropy and MSE estimators are
unsupported for asymmetric quantization, and the modal statistic conflicts with the four estimators.
Refusals are data, not noise. In its own configuration language the tool is confirming that an
asymmetric budget which wants MSE calibration does not exist in the ecosystem this book works in, and
that a designer who needs both has to move to symmetric or change the estimator.

The output of one quantized layer feeds the next, and the scales do not agree, so each transition
requantizes. The registered trick collapses the three scales involved into one integer multiply by a
constant and one shift:

> **The formula.** $M \;=\; \dfrac{S_{\text{in}}\, S_{w}}{S_{\text{out}}} \;=\; 2^{-n} M_{0}, \qquad M_{0} \in \big[\tfrac{1}{2},\, 1\big)$
>
> **The variables.**
>
> - $S_{\text{in}}, S_{\text{out}}$ — the scales of adjacent layers.
> - $S_{w}$ — the scale of the weights in between.
> - $M$ — the combined multiplier that converts one layer's integer output into the next layer's
>   fixed-point input.
> - $M_{0}, n$ — the normalized mantissa and the shift: halve $M$ until it lands in $[1/2, 1)$ and
>   remember how many halvings.
>
> **What it means.** Three scale changes collapse into one multiplier. Storing $M_{0}$ as a signed
> thirty-two-bit integer, with a scale that puts $2^{31} M_{0}$ at least $2^{30}$, keeps at least thirty bits
> of relative accuracy -- which is what the record registers. The shift $n$ is wiring; the constant
> multiply is one lane of DSP work.
>
> **What it costs.** One integer multiply and one shift per value at each layer boundary, two pieces
> of the fabric's native vocabulary. The book's own estimate, not a registered figure.
>
> **What it does not say.** It does not say $M_{0}$ always falls out normalized. The formula is the
> recipe the record gives, and a design that skips the normalization pays with a wider multiply. It
> also does not say requantization re-calibrates: it converts scales, it does not re-derive them.

**Application.** The step before any of this is useful is the statement "weights symmetric,
activations affine", and the DSP48E2 makes the choice stick. The slice's multiplier is asymmetric in
its own way -- one wide operand and one narrow one, twenty-seven bits across by eighteen -- and a
symmetric INT8 weight fits the narrow side exactly, leaving the wide side for the activation's
intermediate growth. On the Orin NX the same choice is made by the toolchain, and the tensor core
executes one INT8 layout for everything. The FPGA's version of the choice is geometric: each slice
already pairs wide with narrow for free, and the 1,248 slices give the design room to spend
correction logic where calibration says it is needed rather than where the data type forces it.

**The four estimators, derived.**

The menu the section above named is a set of answers to one question: where does the range end? Every estimator is a rule for picking a clipping point, and the step, the noise floor and the section 7.1 currency all follow from that one choice. The registered tool exposes the four rules together with the rounding modes and the batch-combination statistics (`V-06-10`); what the menu does not say is which rule protects what, so each estimator below is derived before it is priced.

> **The formula.** $\Delta \;=\; \dfrac{r_{\max} - r_{\min}}{2^{b} - 1}$
>
> **The variables.**
>
> - $r_{\max}, r_{\min}$ — the largest and smallest values the calibration set produces.
> - $b$ — the word width in bits.
> - $\Delta$ — the resulting step, the width of one quantization cell.
>
> **What it means.** Minimum-maximum calibration fits the data exactly: nothing observed is clipped, and the step is simply the observed range split into $2^{b} - 1$ pieces. It is the honest baseline the other estimators measure themselves against, and it is deliberately free of assumptions about what the next sample will do.
>
> **What it costs.** The defect is the range itself. Calibration data is a sample, and a stream of speech carries outliers the task never needs, so the observed extrema can stretch the range; a stretched range fattens every step, and the fattening is paid, in section 7.1's currency, by every value the range was stretched to hold. One distant sample can buy a coarser grid for the entire tensor.
>
> **What it does not say.** It does not say the extrema of a calibration set are informative; it says they are exhaustive of that set. The derivative of the decibel mapping of section 7.1 applies the same verdict to the loudest band: a range held open to protect a peak the task never reads is a step paid for across the quiet bands.

> **The formula.** $\Delta_{p} \;=\; \dfrac{r_{p} - r_{\min}}{2^{b} - 1} \;=\; \Delta\, \dfrac{r_{p} - r_{\min}}{r_{\max} - r_{\min}}$
>
> **The variables.**
>
> - $p$ — the percentile that owns the clip, the fraction of the calibration distribution kept below the clipping point.
> - $r_{p}$ — the value of the calibration distribution at that percentile.
> - $\Delta_{p}$ — the step when the range is cut at $r_{p}$.
>
> **What it means.** Percentile calibration clips a tail and re-derives the step from the range that remains. The reduction factor is the derived quotient: the new step is the old step times the share of the range the kept portion occupies. In the usual setting the tool clips above the ninety-nine point nine nine percentile, so the step is set by the range nearly all speech actually uses, and the extreme values that pass the clip saturate, which is the point.
>
> **What it costs.** The clipped tail is surrendered deliberately, and the surrender is the price that buys the finer step. The estimator is a trade, not a free lunch: saturation at the top of the range is exactly the overload error the next card names, and the quiet-band protection of section 7.1 is bought by spending it.
>
> **What it does not say.** It does not say the percentile is derived from the task. A percentile protects most of the data; it is a statistical statement, and whether the part of the distribution that carries the task's errors sits inside the kept range is a question the estimator does not ask.

> **The formula.** $\mathcal{E}(c) \;=\; \dfrac{\Delta(c)^{2}}{12} \, \Pr(|x| \le c) \;+\; \operatorname{\mathbb{E}}\big[\, (|x| - c)^{2} \;\mathbf{1}_{|x| > c} \,\big]$
>
> **The variables.**
>
> - $c$ — the clipping point, the edge of the representable range.
> - $\Delta(c)$ — the step when the range ends at $c$.
> - $x$ — the value being quantized.
> - $\mathcal{E}(c)$ — the expected squared error the estimator minimises.
>
> **What it means.** Mean-squared-error calibration writes down both costs of a clip and finds the point that balances them. The first term is the granular error: the step-squared-over-twelve variance of section 7.1, paid only by the values that survive the clip. The second term is the overload error: the values that fall outside pay the square of how far the clip pushed them, and the expectation counts how often that happens. Tighten the clip and the granular term shrinks while the overload grows; loosen it and the trade runs the other way. The minimum sits where the two slopes cross, a derived trade rather than a heuristic. The entropy, or KL, estimator is the information-theoretic version of the same balance: it chooses the clipping point that moves the least information, measured as the divergence between the empirical distribution and the quantized one.
>
> **What it costs.** The two information-faithful estimators carry the sharpest restriction in the registered menu: the tool refuses them for asymmetric quantization (`V-06-11`). Choosing entropy or MSE decides the symmetry too, and with it the zero-point arithmetic of the cross-term card: a designer who wants the information-optimal step must take the symmetric range that keeps the correction tree out of the datapath.
>
> **What it does not say.** It does not say the balancing point is the task's point. The expected squared error is a proxy for the recogniser's own gate, and section 7.1's closing verdict applies: an estimator that minimises a generic error against a task metric is measuring the wrong thing unless the two coincide.

**The convolution-batch-norm fold, proved.**

The section above described the fold; the algebra is one line of collecting terms. In evaluation mode the normalization is an affine map of the convolution's output: each channel $k$ is scaled by its own $\gamma_{k}$ over the square root of its registered variance plus the stabilization term, and shifted by $\beta_{k}$. Substituting the convolution's output, the two affine maps compose into one:

> **The formula.** $\hat{y}_{k} \;=\; \sum_{j} W'_{k,j}\, a_{j} + b'_{k}, \qquad W'_{k,j} \;=\; \dfrac{\gamma_{k}}{\sqrt{\sigma_{k}^{2} + \varepsilon}}\, W_{k,j}, \qquad b'_{k} \;=\; \dfrac{\gamma_{k}}{\sqrt{\sigma_{k}^{2} + \varepsilon}}\big(b_{k} - \mu_{k}\big) + \beta_{k}$
>
> **The variables.**
>
> - $W_{k,j}$ — the convolution kernel entry for output channel $k$ and input channel $j$.
> - $a_{j}$ — the input activation on channel $j$.
> - $b_{k}$ — the convolution bias on channel $k$.
> - $\gamma_{k}, \beta_{k}$ — the normalization's per-channel scale and shift.
> - $\mu_{k}, \sigma_{k}^{2}$ — the running mean and variance the normalization uses in evaluation mode.
> - $\varepsilon$ — the stabilisation constant added to the variance before the square root.
> - $W'_{k,j}, b'_{k}$ — the folded kernel and bias, the only quantities the deployed graph stores.
>
> **What it means.** A convolution followed by an affine map is still a convolution. The folded kernel is the old kernel rescaled per channel by the normalization's own scale, and the folded bias is the old bias rescaled, pulled toward the running mean and pushed by the shift. Every symbol is defined because the fold is a substitution, not a new operation: the derived line is the convolution's output written into the normalization's formula and collected by channel. Computed on a per-channel scale, this is exactly what the record guards (`V-06-09`): an implementation that asserts evaluation mode, refuses a batch norm without running buffers, and rewrites the weight tensor by a per-channel scale.
>
> **What it costs.** One rewrite of the kernel and bias, performed once before calibration. Inference pays nothing: the normalization pass is deleted from the graph, the state the record registers (`V-06-06`), so the streaming hop of section 7.1 never rides a separate normalization layer. The price is paid in the rewrite itself, and that is why calibration must run after the fold: a quantizer measures a range, a range is a property of a layer, and the layers that exist after the fold are the ones the deployed graph multiplies.
>
> **What it does not say.** It does not say the fold preserves training behavior. The running statistics make it an evaluation-mode rewrite only, which is the point of the registered guard, and a fold applied with batch statistics would not be the same map. It also does not say the fold and the quantizer commute: quantize the folded kernel, because it is what the design stores.

**Why the thirty-bit bound holds.**

The existing requantization card registered the answer; the derivation is three lines. Let $m$ be the integer nearest to $2^{31} M_{0}$, the fixed-point representation the card chooses, with the normalized mantissa $M_{0}$ in the half-open interval $\big[\tfrac{1}{2}, 1\big)$. Because the mantissa never drops below one half, $2^{31} M_{0}$ is never below $2^{30}$: the stored integer always carries a magnitude of at least two to the thirtieth, and its most significant bit is always set. Rounding to the nearest integer leaves the stored constant $m / 2^{31}$ within one half of a unit in the last place of the true mantissa, which is a relative error of at most one over two to the thirty-first when measured against the smallest admissible mantissa, computed as the half-unit error divided by the mantissa's lower bound, about one part in two billion. "At least thirty bits of relative accuracy" is exactly this: the leading bit is always set, so the remaining thirty bits of the thirty-one-bit word are all significant, whatever the mantissa does inside its interval. The record registers the bound (`V-06-02`); the derivation is the section's own.

**The slice's half of the argument.**

The multiplier is asymmetric, twenty-seven bits across by eighteen, and the choice the Application above stated makes the asymmetry useful: a symmetric INT8 weight sits inside the narrow operand with room to spare, while the wide operand absorbs the activation's growth across the reduction without ever spilling. Symmetry does the deeper work. With the weight zero point forced to zero, the expensive case of the cross-term card never enters the datapath: the live row-sum of activations is not computed, because there is no weight zero point to multiply it by, and the correction logic the one thousand two hundred and forty-eight slices (`V-01-09`) can afford is not consumed by arithmetic the data type forced. The slice prices the two halves of the cross-term card in silicon: the multiply is native, the zero-point correction is an extra adder tree, and symmetric weights simply refuse to build the tree. An asymmetric activation range remains perfectly comfortable, because its single zero point folds into the bias before the design starts; the pairing the section recommends, symmetric weights with affine activations, is precisely the pairing the slice's asymmetry wants, which is why the sentence this block sits under is a hardware sentence and not a style preference. The estimator that calibrates the pair matters for the same reason the fold does: the range the estimator picks becomes the step, and the step is what the slice multiplies.


**Traceability.** The records this section leans on. The arithmetic derivations -- the cross-term
expansion and the requantization normalization -- are the section's own work from registered forms,
and the resource counts in the cards are the book's own estimates; every other figure is a registered
claim.

| Record | What it establishes here |
| --- | --- |
| `V-06-01` | the affine quantized form $r = S(q - Z)$ from Jacob and colleagues, 2018 |
| `V-06-02` | the requantization multiplier $M = 2^{-n} M_{0}$ and the thirty-bit accuracy bound |
| `V-06-09` | the convolution-batch-norm fold that must run before calibration |
| `V-06-10` | the calibration estimator menu and the rounding-mode list |
| `V-06-11` | the tool's refusals: entropy and MSE unsupported for asymmetric quantization |
| `V-01-09` | the KV260's 1,248 DSP slices that the correction-logic argument prices |

## 7.3 Quantization-Aware Training (QAT) with Straight-Through Estimators

*Where this sits in the chain: the* **Model** *stage -- the second route to a small number, the one
that makes rounding part of training instead of a tax on it.*

**Intuition.** PTQ makes a finished network put up with rounding. Quantization-aware training (QAT)
makes the rounding part of training, so the weights learn values that survive it. The obstacle is
calculus: rounding has zero derivative almost everywhere, so the gradient the optimizer needs dies at
the quantizer. The straight-through estimator (STE) is the standard repair -- a forward pass that is
exactly the hardware, and a backward pass that pretends the quantizer was the identity map.

**Mechanism.** The forward pass must match the fabric bit for bit; the backward pass is where the
trick lives:

> **The formula.** $q \;=\; \mathrm{clamp}\!\left( S\, \mathrm{round}\!\left( \dfrac{x}{S} \right),\, q_{\min},\, q_{\max} \right), \qquad \dfrac{\partial q}{\partial x} \;=\; 1 \ \ \text{inside the clamped range}$
>
> **The variables.**
>
> - $S$ — the step size.
> - $\mathrm{round}$ — whichever tie rule this section pins down below; the forward pass inherits it
>   exactly.
> - $q_{\min}, q_{\max}$ — the edges of the integer range.
>
> **What it means.** Training and hardware see the same function in the forward direction, which is
> the whole contract of QAT: what runs on the fabric is what the loss was computed with. The backward
> direction replaces the zero derivative of round with the constant one inside the range, so the
> gradient flows through the quantizer as if it were a wire, and the optimizer moves the weights as
> though the rounding did not exist. Both halves matter: a forward-only round would train a network
> that its own hardware then surprises.
>
> **What it costs.** The estimator is biased: the gradient it passes is the gradient of the identity,
> not of round, so weight updates drift from the true loss surface. The bias is the price of a
> training-time model that executes in integer hardware, and it is why a learned scale, below, exists.
>
> **What it does not say.** It does not say STE is the only estimator, or the best; it is the one
> that makes the forward pass exact, and for hardware work that exactness is the property that
> matters. It also does not say the clamp is free: values pushed past the edges contribute nothing to
> the gradient, which is how training learns to stay inside the range.

For eight-bit post-training work the scale comes from a calibration pass; for QAT it can be learned as
a parameter like any other. Esser and colleagues' learned-step-size scheme, LSQ, treats the step size
as trainable and derives its gradient through the same rounding:

> **The formula.** $\dfrac{\partial \mathcal{L}}{\partial S} \;=\; \sum_{i} \dfrac{\partial \mathcal{L}}{\partial q_{i}} \, \dfrac{\partial q_{i}}{\partial S}, \qquad \dfrac{\partial q_{i}}{\partial S} \;=\; \mathrm{round}\!\left( \dfrac{x_{i}}{S} \right) - \dfrac{x_{i}}{S}$
>
> **The variables.**
>
> - $\mathcal{L}$ — the task loss.
> - $q_{i}$ — the quantized value of element $i$.
> - $S$ — the step size being learned.
>
> **What it means.** The chain rule through the quantizer gives each element a contribution equal to
> its own quantization error, so the scale moves toward the value that makes the current rounding
> errors smallest in the direction the loss wants. The step size a histogram would guess at is instead
> negotiated with the task itself.
>
> **What it costs.** One extra learned parameter per tensor, its own learning-rate treatment and its
> interaction with weight decay: the price of a scale that fits the task rather than a calibration
> set.
>
> **What it does not say.** It does not say a learned scale survives every hardware path. The learned
> $S$ still has to become the requantization constant $M_{0}$ of section 7.2, and landing in
> $[1/2, 1)$ is not automatic. It also does not say LSQ is the only route; it is the named one this
> book builds its argument on.

**The bit-exactness trap.** QAT's contract is that the training-time quantizer equals the fabric's
quantizer, and the tools make that harder than it looks. The record documents the default: the widely
used Brevitas flow's default integer conversion wraps PyTorch's round, and PyTorch's round uses
round-half-to-even. The counterpart a designer naturally writes in RTL -- add half a step, then
truncate -- is round-half-up, and a bare arithmetic shift truncates toward minus infinity. That is
three tie behaviours across one toolchain. Every exact tie, every value whose dropped bits are exactly
half a step, then rounds differently in the golden model and on the fabric, and the difference is
silent, bounded, and exactly the kind this book says to catch early.

Round-half-to-even is not four gates: the tie test is one compare against the half-step boundary, and
the module below hardens it:

```systemverilog
// Round-half-to-even on a signed accumulator, matching PyTorch's round() exactly.
// Keep W_IN-SHIFT bits and drop SHIFT; when the dropped part is exactly half a
// step, round toward the even kept value. Pure combinational logic: two gates
// and one adder -- the book's own estimate of the fabric cost.
module round_half_even #(
  parameter int W_IN  = 16,          // accumulator width
  parameter int SHIFT = 3            // how many bits are dropped
)(
  input  logic signed [W_IN-1:0] x,
  output logic signed [W_IN-SHIFT-1:0] y
);
  // The dropped part is x[SHIFT-1:0]; its top bit is the guard bit.
  wire guard  = x[SHIFT-1];                   // dropped part reaches half a step
  wire sticky = (x[SHIFT-2:0] != '0);         // dropped part goes beyond half a step
  // Round up when the dropped part is more than half, or exactly half and the
  // kept part is odd, so the kept part lands on an even value.
  wire up     = guard & (sticky | x[SHIFT]);
  assign y    = (x >>> SHIFT) + up;           // arithmetic shift keeps two's complement
endmodule
```

An accumulator of $125$ with a shift of $3$ holds the value $125 / 8 = 15.625$: truncation gives
$15$, round-half-up gives $16$, and round-half-to-even gives $16$ as well, because the dropped part is
strictly past half a step. The cases that separate the rules are the ties: $124 / 8 = 15.5$ rounds to
$16$ under both rules, but $116 / 8 = 14.5$ rounds to $15$ under round-half-up and to $14$ under
round-half-to-even, because $14$ is even.

**Application.** The trap closes when the tie rule is a named contract on both sides of the toolchain
and when the test bench includes the tie vectors -- a value whose dropped bits are exactly half a
step. A golden model and a fabric that disagree only on ties pass any corpus that misses the boundary
and still diverge in production. On the KV260 each rounding site costs two logic gates and one adder,
which is the book's own estimate, not a registered figure. The registered cost is documentation: the
default conversion is round-half-to-even wrapped from PyTorch, so the default golden model and the
default RTL disagree on ties unless someone re-pins the rule.

**Why the identity proxy is the wrong derivative between the steps.**

The card above passes the gradient of a straight line through a function that is not one. The quantizer the forward pass computes is a staircase. Along each tread, the width of one step, the true derivative is exactly zero, because the output does not move when the input does. At each riser it is neither zero nor finite: the output jumps one whole step in no distance. Written as a derivative, the staircase's slope is a train of infinitely thin spikes at the step boundaries, halfway between the step centres, and zero everywhere else. The straight-through estimator replaces that train with the constant one across the clamped range: true where the loss is smooth, false exactly where the quantizer is doing its work.

**The bias is a function of position inside the step.** Averaged over one step the proxy is right: across a run of width $S$ the staircase climbs by exactly $S$, so its mean slope is one, and the estimator is unbiased in that mean. What it cannot see is the local slope. Let $f$ be where a value sits inside its own step, $f = x/S - \lfloor x/S \rfloor$, running from zero at a left edge to one at the right. Only an update that carries $f$ past a boundary moves the quantized value at all. A weight resting at mid-step, $f = \tfrac12$, can be nudged half a step either way with the fabric's output unchanged; a weight resting against a boundary flips a whole step on the smallest push. The update the optimizer believes it made and the update the fabric delivers therefore disagree by an amount proportional to the weight's distance from the nearest boundary, and the disagreement is largest where the optimizer is most confident: at mid-step, the position the proxy treats as the most ordinary place to be. Training on that mismatch writes a systematic pressure that drifts weights through boundaries as though the loss crossed them smoothly.

**The clamp is the one place the proxy tells the truth.** Outside $q_{\min}$ and $q_{\max}$ the two agree exactly, and for the same reason: beyond the range the quantizer is constant in its input, so its true derivative is zero, and the clamp hands back zero too. There the identity is not an approximation. That agreement is the mechanism the card above credits for keeping the model inside the range. An element driven past an edge receives no gradient at all, so no update pulls it back, and the saturation zone becomes a region the training signal cannot reach. The optimizer's only way to stop losing elements to it is to keep the mass of the distribution inside the representable interval, which is how a range chosen once, before training, ends up respected by the model rather than merely imposed on it.

**Why a learned scale repairs the frozen boundary.** The defect the critique isolates is that the boundaries do not move. With $S$ fixed, every weight's $f$ is fixed by the data, and no gradient reaches the boundary positions to move them where the loss wants them; the optimizer can only push weights across boundaries it did not choose. That is the repair a learned step size makes. Making $S$ trainable turns the boundary positions into parameters, and the LSQ card above shows the derivative of the loss with respect to $S$ is available through the very rounding that blocks every other gradient, so the placement of the steps becomes something the task negotiates instead of a constant handed down by a histogram. A learned scale is not a different estimator; it is this one with the quantity the critique identifies as frozen made free.

**The requantizer as a pipeline, with saturation at the end.** The boundary between two quantized layers is where the multiplier of section 7.2 applies: one constant multiply and one shift convert one layer's output scale into the next layer's input scale. The module below is that boundary as hardware. It multiplies a signed accumulator by the normalized mantissa $M = 2^{-n} M_0$, drops $n$ bits with the round-half-to-even rule, then clamps. Three register stages sit between those steps, the multiply owning one, the shift and round the next, the saturation the last, so the element takes a new sample every cycle instead of stretching one long combinational path across the fabric's clock. It speaks AXI4-Stream: the `tvalid`/`tready` handshake that pairs a producer with a consumer, and `tlast` marking a frame's final sample, which is what lets it drop into the FIFO-based streaming datapath of chapter 9 with no wrapper.

```systemverilog
// ---------------------------------------------------------------------------
// requant_axis -- a pipelined fixed-point requantizer on an AXI4-Stream port.
// Per sample: multiply by the normalized mantissa M0 of the requantization
// multiplier M = 2^-SHIFT * M0 (section 7.2); drop SHIFT bits with the
// round-half-to-even rule, the same rule the round_half_even module above
// implements; then saturate into the output word instead of wrapping.
// One register stage owns each step, so the element is pipelined.
// ---------------------------------------------------------------------------
module requant_axis #(
  parameter int W_IN  = 32,          // accumulator width, signed
  parameter int W_M0  = 32,          // width of the M0 literal
  parameter int SHIFT = 12,          // n: how many bits are dropped (wiring)
  parameter int W_OUT = 8,           // output word, signed
  // M0 lies in [1/2, 1); scaled by 2^31 as a signed literal its range is
  // [2^30, 2^31), and this default is the lower edge of that interval.
  parameter logic signed [W_M0-1:0] M0 = 32'sh4000_0000
)(
  input  logic                    clk,
  input  logic                    rst_n,
  input  logic                    s_axis_tvalid,   // slave: values arrive here
  output logic                    s_axis_tready,
  input  logic signed [W_IN-1:0]  s_axis_tdata,
  input  logic                    s_axis_tlast,    // the frame's final sample
  output logic                    m_axis_tvalid,   // master: results leave here
  input  logic                    m_axis_tready,
  output logic signed [W_OUT-1:0] m_axis_tdata,
  output logic                    m_axis_tlast
);
  localparam int WP = W_IN + W_M0;   // width of the full product
  localparam int WK = WP - SHIFT;    // width kept once the shift is applied
  localparam logic signed [WK:0] OUT_MAX = (1 <<< (W_OUT-1)) - 1;  // range for
  localparam logic signed [WK:0] OUT_MIN = -(1 <<< (W_OUT-1));     // the clamp

  // The three stages advance together: a sample enters only when the output
  // register can take one, the backpressure a chapter 9 FIFO applies.
  logic out_ready;
  assign out_ready     = m_axis_tready | ~m_axis_tvalid;
  assign s_axis_tready = out_ready;

  // ---- stage 1: multiply, then register -----------------------------------
  logic signed [WP-1:0] product, prod_q;
  logic                 v1_q, l1_q;
  assign product = s_axis_tdata * M0;   // one native DSP48E2 multiply

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      prod_q <= '0;
      v1_q   <= 1'b0;
      l1_q   <= 1'b0;
    end else if (out_ready) begin
      prod_q <= product;
      v1_q   <= s_axis_tvalid;
      l1_q   <= s_axis_tlast;
    end
  end

  // ---- stage 2: shift and round, then register ----------------------------
  // The dropped part of prod_q is its SHIFT low bits: guard says it reaches
  // half a step, sticky says it goes past. Round up when it is past half a
  // step, or exactly half and the kept value is odd -- round half to even.
  logic guard, sticky, up;
  logic signed [WK:0] shifted, rounded, rnd_q;
  logic               v2_q, l2_q;
  assign guard   = prod_q[SHIFT-1];
  assign sticky  = (prod_q[SHIFT-2:0] != '0);
  assign up      = guard & (sticky | prod_q[SHIFT]);
  assign shifted = prod_q >>> SHIFT;    // arithmetic shift preserves the sign
  assign rounded = shifted + up;        // the tie rule, as in round_half_even

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      rnd_q <= '0;
      v2_q  <= 1'b0;
      l2_q  <= 1'b0;
    end else if (out_ready) begin
      rnd_q <= rounded;
      v2_q  <= v1_q;
      l2_q  <= l1_q;
    end
  end

  // ---- stage 3: saturate, then register -----------------------------------
  logic signed [WK:0] saturated;
  assign saturated = (rnd_q > OUT_MAX) ? OUT_MAX :
                     (rnd_q < OUT_MIN) ? OUT_MIN : rnd_q;

  always_ff @(posedge clk) begin
    if (!rst_n) begin
      m_axis_tdata  <= '0;
      m_axis_tvalid <= 1'b0;
      m_axis_tlast  <= 1'b0;
    end else if (out_ready) begin
      m_axis_tdata  <= saturated[W_OUT-1:0];   // clamped into the output word
      m_axis_tvalid <= v2_q;
      m_axis_tlast  <= l2_q;
    end
  end
endmodule
```

**Why saturation and not wrap.** Two's complement arithmetic carries no overflow flag. When a result leaves the representable range it wraps, the largest positive value becoming the most negative, and nothing reports it. For a weight that is merely wrong; for a score about to enter a softmax it is worse. The softmax of section 7.5 subtracts the row maximum, so a wrapped score that was the largest in its row becomes the smallest, the subtraction inverts, and the whole row's attention mass moves to a different position. The error is large, silent, and structured: not like noise a calibration might average away, but like a decision. Saturation replaces the wrap with the nearest representable value, which is bounded, preserves the row's ordering, and fails in a direction a downstream stage can still reason about.

**The tie rule, and why the test vectors are the payload.** The rounding stage is the same rule the `round_half_even` module above implements, bit for bit: a guard bit that says the dropped part reaches half a step, a sticky bit that says it goes past, and a round up when the dropped part is past half, or exactly half and the kept value is odd. Holding the two modules on one rule is not tidiness. The training flow's registered default wraps PyTorch's round (`V-06-04`), and PyTorch's round breaks ties toward the even value (`V-06-05`); a fabric module that breaks them any other way agrees with its golden model on every sample except the ties, and passes any corpus that never lands on one. So the section closes where it began: the tie vectors, a value whose dropped bits are exactly half a step, and their negatives, are what a test bench exists to carry, because every other sample passes for free.


**Traceability.** The records this section leans on; the fabric costs in the cards are the book's own
estimates, not registered figures.

| Record | What it establishes here |
| --- | --- |
| `V-06-04` | the Brevitas default: integer conversion is RoundSte wrapping PyTorch's round |
| `V-06-05` | torch.round implements round-half-to-even, and the RTL add-then-shift maps ties differently |

---

## 7.4 Layer-Specific Mixed-Precision Schemes

*Where this sits in the chain: the* **Model** *stage -- the chapter's compromise: the width becomes a
per-layer decision made against the whole network.*

**Intuition.** Layers tolerate noise differently. A layer whose products feed a softmax or a
normalization is more fragile than one feeding another convolution, because a small perturbation in
its output changes a probability or a mean. Uniform width wastes fabric at both ends: eight bits for
a layer that could hold four, and eight bits for a layer that needs twelve. Mixed precision spends
each bit where the network is most curved.

**Mechanism.** The measure of "most curved" is the Hessian of the loss with respect to a layer's
weights. To second order, the loss change from corrupting layer $i$'s weights by a perturbation is
half the trace of that Hessian times the perturbation's energy:

> **The formula.** $\Delta \mathcal{L}_{i} \;\approx\; \tfrac{1}{2}\, \mathrm{Tr}\big( \mathbf{H}_{i} \big)\, \| \mathbf{e}_{i} \|^{2}$
>
> **The variables.**
>
> - $\mathbf{H}_{i}$ — the Hessian of the task loss with respect to layer $i$'s weights.
> - $\mathrm{Tr}(\mathbf{H}_{i})$ — the trace of that Hessian, the layer's average curvature.
> - $\mathbf{e}_{i}$ — the perturbation the weights suffer, here the quantization error.
>
> **What it means.** The trace is a per-layer sensitivity number: a layer with a large trace doubles
> the loss more for the same rounding error, so it deserves more width; a layer with a small trace can
> be narrowed almost for free. Hessian-aware width selection, the HAWQ line of work, is exactly this:
> rank the layers by trace, spend the bits there. The card is the book's own formulation of the
> standard second-order result; no registered figure sits behind the trace itself.
>
> **What it costs.** A full Hessian per layer is far too expensive to compute for a real model, so
> practical schemes estimate the trace, and the proxies are where the method's own error enters. On
> the fabric the cost runs the other way: per-layer widths are routing decisions, nearly free to
> spend and costly to undo.
>
> **What it does not say.** It does not say trace ranking is the only rule; it is the one with a
> convex justification. It also does not say the sensitivity is static: quantization-aware retraining
> reshapes it, which is why section 7.3 and this section belong together.

The book's own model, the streaming Conformer that chapter 9 builds, fixes the layer census this
section can price. The registered geometry: sixteen encoder layers, a model width
$d_{\text{model}} = 176$, four attention heads, a depthwise kernel of thirty-one taps, and a
feed-forward expansion of four, so the feed-forward width is $d_{\text{ff}} = 4 \times 176 = 704$.
The block's multiply work divides unevenly. Each block runs two feed-forward networks of two matrix
products each, at the expanded width, and one attention stage of four projections at the unexpanded
width. The feed-forward products are four times the attention products, computed as the quotient of
the two feed-forward networks' combined matrix sizes by the four attention projections' combined
sizes, which is exactly four to one for any model that follows the expansion.

The width budget then follows the sensitivity, not the arithmetic order, and [Figure 26](#fig-ch7-mixed-precision-map) collects the census:

::: {#fig-ch7-mixed-precision-map .figure}
```tikz
% One streaming-Conformer block with the per-part widths this section argues for:
% the GEMM-heavy feed-forward nets are narrowed hardest, the attention keeps INT8
% with the integer softmax of section 7.5, the normalization stays widest. The
% stack is drawn in the order the block executes the parts.
\begin{tikzpicture}[
  node distance=4mm,
  blk/.style={draw, align=center, inner sep=2pt, font=\scriptsize, text width=38mm, minimum height=9mm},
  arr/.style={-{Stealth[length=1.6mm]}, thick},
]
\node[blk] (fe)   {subsampling front end\\ \texttt{INT16} or \texttt{INT8}};
\node[blk, below=of fe] (ff)    {macaron feed-forward\\ \texttt{INT4} weights};
\node[blk, below=of ff] (mhsa)  {multi-head attention\\ \texttt{INT8} with integer softmax};
\node[blk, below=of mhsa] (dw)  {depthwise convolution\\ per-channel \texttt{INT8}};
\node[blk, below=of dw] (ln)    {layer normalisation\\ \texttt{INT16}};
\draw[arr] (fe) -- (ff);
\draw[arr] (ff) -- (mhsa);
\draw[arr] (mhsa) -- (dw);
\draw[arr] (dw) -- (ln);
\end{tikzpicture}
```
The mixed-precision map of one streaming-Conformer block: the feed-forward nets, which dominate the
multiply work, carry the narrowest weights; the attention and its softmax keep eight bits; the
front end and the normalisation keep the widest words. Per-block scaling is the pattern the silicon
study below reports.
:::

- **The macaron feed-forward nets take INT4 weights.** They hold the dominant share of the block's
  multiply work, by the ratio above, and their products feed a residual addition rather than a
  probability or a scale, so they tolerate the coarsest step.
- **The multi-head attention keeps INT8 for its projections**, and its softmax runs integer-only by
  the path of section 7.5, because a probability is the most fragile output in the block.
- **The subsampling front end keeps INT16**, or INT8 where calibration shows the range is quiet: it
  meets the widest dynamic range in the model, the raw spectral path.
- **The depthwise convolution runs per-channel INT8 or INT16.** Its channels are isolated filters,
  and a per-channel scale fits that isolation at zero extra DSP cost, because each channel is a
  separate product anyway.
- **The layer normalization keeps INT16.** Its mean-and-variance reduction divides, and a tired
  denominator corrupts every element that follows.

**Application.** On the Orin NX the census fights the datapath. The tensor core executes one INT8
layout per operation, and mixing INT4 with INT8 means unpacking bytes, alignment and register
pressure; the SIMD machine charges for heterogeneity. On the FPGA the same census is geometry: each
block is its own datapath and gets its own width, the DSP48E2's asymmetric multiplier pairs a wide
operand with a narrow one at no extra cost, and a per-channel scale is the same multiplier with a
different constant. The memory consequence closes the loop this chapter opened. The two feed-forward
networks of one block hold $2 \cdot 2 \cdot 176 \cdot 704 = 495{,}616$ weights, computed as the
product of the two networks, their two matrices each, and the two widths; streamed once per hop
period at INT8 that is about 49.6 MB/s, computed as the weight count times one byte per weight over
the $0.01$ s hop period, and half of that at INT4. Both sit far under the registered 19.2 GB/s of the
board's DDR4, so the feed-forward width is not a bus problem; it is a capacity problem. The same
495,616 weights at INT8 are about 484 KiB, computed as the byte count divided by 1024 per kibibyte,
which is a large slice of the KV260's registered 23,616 kilobits of on-chip SRAM, and at INT4 it
halves. Fewer bytes across the ladder of section 7.1 is exactly where the energy is.

The direction has silicon behind it. A registered study of a streaming Conformer ASIC at 22 nm runs
the encoder at 250 MHz on 359 mW, reports a nine-hundred-fold streaming-throughput advantage, a
four-fold latency cut and a sixteen-fold power cut against its GPU reference, and credits two
choices: a shared MAC array that keeps all activations on chip, and hardware-friendly normalization
in which the non-linear functions share block-wide scaling factors. The second choice is this
section's argument in silicon: precision is organized per block, with scales shared across the block's
non-linear stages, rather than per tensor as a GPU data path would impose.

**The trace without the matrix: the Hutchinson estimator, derived.**

The card above measures sensitivity by the trace of the layer Hessian, and the trace looks like it should cost the whole matrix. It does not, and the trick is a one-line identity: a random probe vector whose distribution has identity covariance contracts the Hessian to its trace in expectation. Draw each probe entry independently from a distribution with zero mean and unit variance, the registered options being the Rademacher choice, plus or minus one with equal probability, or the standard Gaussian, and the expected quadratic form is the trace itself. The Monte Carlo estimator then averages a small number of probes:

> **The formula.** $\mathrm{Tr}\big(\mathbf{H}_{i}\big) \;=\; \mathbb{E}_{z}\!\big[\, z^{\top} \mathbf{H}_{i}\, z \,\big] \;=\; \lim_{m \to \infty} \frac{1}{m} \sum_{h=1}^{m} z_{h}^{\top} \mathbf{H}_{i}\, z_{h}$
>
> **The variables.**
>
> - $\mathbf{H}_{i}$ — the Hessian of the task loss with respect to layer $i$'s weights, the matrix the section's card above introduces.
> - $z$ — a random probe vector whose entries are independent with mean zero and unit variance, so the probe's covariance is the identity matrix.
> - $z_{h}$ — the $h$-th draw of the probe; $m$ — the number of draws.
> - $\mathbb{E}_{z}$ — the expectation over the probe distribution; $\mathrm{Tr}$ — the trace.
>
> **What it means.** The identity is the exchange of expectation and trace: the quadratic form is the trace of the Hessian times the probe's outer product, the expectation of the outer product is the identity because the probe's covariance is, and the trace of the Hessian against the identity is the trace of the Hessian. Derived in that one line, the trace becomes the expectation of a scalar each probe computes. The finite sum is the estimator: the average over $m$ draws converges to the trace as the probe count grows, and a small count gives a noisy but usable reading.
>
> **What it costs.** Each probe is one Hessian-vector product, not one Hessian. The product $\mathbf{H}_{i} z$ is the derivative of the gradient along the direction $z$, computed by a second backward pass, the double backprop the section's card above mentions: differentiate the already-computed gradient once more, along the probe direction, and the vector comes out without ever materializing the matrix. The full Hessian, whose size is the square of the layer's weight count, is the thing that is not computed, because nothing in the estimator needs it. No registered figure sits behind the trace; the estimator is the section's own arithmetic, and the cost is in passes, not in the matrix.
>
> **What it does not say.** It does not say a small probe count gives the exact trace. The Monte Carlo average carries variance that falls like one over the probe count, and the error like one over its square root, so the estimator is a budget choice, not a closed form. It also does not say the sensitivity is static: the quantization-aware retraining of section 7.3 reshapes the Hessian, which is why the estimator and the retraining belong together.

Why only the trace is needed, and why the vector product is the right unit of work, is the same fact twice. The second-order term of the section's card, half the trace times the perturbation energy, treats the perturbation per layer: the energy $\|\mathbf{e}_{i}\|^{2}$ is a scalar, and no direction inside the layer's weight space ever enters the term. Contracting the Hessian against an isotropic energy throws away all off-diagonal curvature, because nothing in the term is aligned with any eigenvector; the trace is the only contract the term can sign. The Hessian-vector product is the natural unit of work for the same reason: it is the list of second derivatives along one direction, one vector the size of the layer's weights, and the trace of the whole matrix is the average of such products over random directions. The estimator prices the sensitivity the budget needs — one scalar per layer, ranked against the other layers — and the full matrix, which the budget never asked for, is never built.

The estimator's own arithmetic deserves one plain sentence, because the probe choice is the part a budget can actually see. The variance of the estimate falls like one over the probe count, as the card's closing disclaimer stated, and the constant in front of that fall depends on the distribution the probes are drawn from. The Rademacher probe, plus or minus one, keeps every draw bounded, so no single probe can dominate the average and one unlucky direction cannot fabricate a fragile layer out of the noise; the Gaussian probe concentrates the estimate a shade tighter on a smooth loss surface but lets a rare large draw spend the whole average. For a ranking that only has to separate three tolerance classes, the two choices agree, and the bounded probe is the safer one, because its worst draw is known before the first pass. The probe count, in turn, is a budget line like any other in this chapter: a few more passes shrink the error of the ranking, and the census below is robust to exactly that difference, because it places entire word-width classes apart rather than layers within a few percent of one another. The estimator is a spending decision dressed as a formula, which is why it belongs in a chapter about what quantization buys.

**The census, read as per-block sensitivity.**

Read the census through the estimator, and the assignment stops looking like a set of taste calls. The feed-forward networks hold the four-to-one share of the block's multiply work, the quotient the section above computed, and their products feed a residual addition rather than a probability or a scale; a perturbation in a feed-forward weight changes a partial sum that later stages dilute, so the trace spends there: the coarsest step lands on the weights whose error the residual path absorbs, and the width that is cheapest in fabric buys the widest step on the weights the loss bends least. The attention stage and its softmax keep INT8 because a probability is the most fragile output in the block; a perturbation there is the one the second-order term does not dilute, and the integer softmax of section 7.5, a registered sequence of arithmetic steps (`V-07-11` through `V-07-15`), is what lets that stage stay at eight bits without a floating-point exponent. The normalization keeps INT16 because its output is a scale: a tired denominator multiplies every element that follows, its error propagates with the block's full swing, and that is the trace's worst case by the section's own reasoning, not by habit.

The block, not the tensor, is the unit the estimator and the silicon agree on. The registered finding the section above cites already organized precision this way: hardware-friendly normalization in which the non-linear functions share block-wide scaling factors (`V-07-24`), the block as the budgeting unit rather than the per-tensor granularity a GPU data path imposes. The shared MAC dataflow (`V-07-23`) is the fabric side of the same decision: one array serves the block's widths, because the multiplier the section 7.2 mapping priced, twenty-seven bits across by eighteen, fits a narrow INT4 or INT8 weight against a wide operand that grows with the activation, at no extra cost. The ranking from the estimator and the structure from the silicon study land on the same statement: sensitivity is priced per block, the narrowest words on the GEMM-heavy feed-forward that owns the multiply work, the eight-bit paths on the probability, the widest words where a denominator divides. The chapter's argument is one sentence when the estimator and the census are read together: the network bends where the products are diluted, the block works where the geometry is per-block, and both said the same thing before the silicon confirmed it.

The per-block reading and the per-block silicon are the same claim at two scales. The estimator hands back one scalar per block, a single number the budget can rank against its neighbours, and the registered normalization the study credits shares block-wide scaling factors across the block's non-linear stages; one side of that pairing says sensitivity is a property of the block, the other says the arithmetic is organized that way too. The shared MAC dataflow closes the loop, because a precision plan per block is only meaningful if the hardware multiplies the block's words without repacking them, and the shared array is precisely the repacking-free datapath. That is the sentence this chapter opened with, back at the section 7.1 ladder: quantization is a budget, the budget in a block-structured model is per block, and the estimator and the fabricated study agree on where the block boundaries sit. Neither alone would be enough, which is why the section keeps both: the estimator says where the error lives, and the silicon study says the fabric can be built to match.


**Traceability.** The records this section leans on. The census arithmetic -- the four-to-one ratio,
the weight counts and the bandwidths -- is computed from the registered model geometry in this table;
the trace-based sensitivity card is the book's own formulation; everything else is a registered
claim.

| Record | What it establishes here |
| --- | --- |
| `V-05-12` | the sixteen encoder layers that fix the block count the census prices |
| `V-05-13` | the model width $d_{\text{model}} = 176$ |
| `V-05-14` | the four attention heads of the attention stage |
| `V-05-15` | the depthwise kernel of thirty-one taps |
| `V-05-36` | the feed-forward expansion of four, the source of the four-to-one ratio |
| `V-05-31` | the $0.01$ s hop period that turns weight counts into bandwidth |
| `V-01-09` | the 1,248 DSP slices the per-layer widths are spent on |
| `V-01-11` | the 23,616 kilobits of on-chip SRAM the width budget lands in |
| `V-01-13` | the 19.2 GB/s DDR4 bandwidth the weight stream stays under |
| `V-07-06` | the energy ladder the byte savings climb down |
| `V-07-26` | the dataflow memory sizes the per-block widths live in |
| `V-07-16` | the 22 nm process of the streaming-Conformer study |
| `V-07-17` | its 250 MHz clock |
| `V-07-18` | its 359 mW operating power |
| `V-07-23` | the shared MAC dataflow that keeps activations on chip |
| `V-07-24` | hardware-friendly normalization with shared per-block scaling factors |
| `V-07-20` | the nine-hundred-fold streaming-throughput figure |
| `V-07-21` | the four-fold latency reduction |
| `V-07-22` | the sixteen-fold power reduction |

---

## 7.5 Integer-only softmax: the base-2 path

*Where this sits in the chain: the* **Model** *stage -- this section protects one activation function
inside the quantized networks the rest of the chapter has been sizing for the fabric.*

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

The four steps assemble into one datapath, and [Figure 27](#fig-integer-softmax-datapath) draws it as a
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

---

## 7.6 Exercises: four problems that tie the chapter to the fabric

> **Exercise (laddered) -- the crest-factor budget.**
> This exercise works the numbers of section 7.1 on one acoustic path. Take a speech front end whose
> conversational crest factor is $18$ dB and whose quietest meaningful content, fricative energy,
> sits $40$ dB below full scale. Use the ideal six-decibels-per-bit law with the $1.76$ dB constant.
> (a) How many decibels of signal-to-quantization-noise ratio does the fricative actually see at
> INT8 and at INT16, computed as $6.02 b + 1.76 - 18 - 40$ for $b = 8$ and $b = 16$? (b) What is the
> narrowest width whose fricative margin stays positive, computed as the width at which
> $6.02 b + 1.76 - 18$ just reaches $40$ dB?
>
> **Answers.**
> (a) At INT8 the fricative sees $6.02 \times 8 + 1.76 - 18 - 40 = -9.9$ dB, buried below the floor;
> at INT16 it sees $6.02 \times 16 + 1.76 - 18 - 40 = 40.1$ dB, a healthy margin. (b) The crossover
> comes when $6.02 b = 40 + 18 - 1.76 = 56.24$, so $b = 56.24 / 6.02 \approx 9.34$, which implies a
> ten-bit path is the narrowest with a positive margin, computed as that quotient rounded up. The
> consequence is the section's point: INT8 on raw spectral energy cannot carry both the crest factor
> and the fricative floor, which is why the calibration sections spend so much attention on which
> range a layer actually sees.
>
> **Exercise (laddered) -- the price of a weight zero point.**
> A matrix engine multiplies $M \times K$ activation rows by $K \times N$ weight columns, one
> multiply-accumulate per DSP slice per cycle. With symmetric weights the core schedule is $M K N$
> cycles, and the asymmetric activation's correction folds into $N$ precomputed bias constants. Now
> extend the engine to a nonzero weight zero point. (a) Write the added work as a formula in $M$, $K$
> and $N$: the row-sum reduction plus the per-output fix-ups. (b) At $M = K = N = 256$, how many
> extra operations does the correction add, and what share of the $16{,}777{,}216$ core
> multiply-accumulates is that, computed as the ratio of the two contributions' sum to the core
> count? (c) How many extra adder stages does the correction tree need, computed as the base-two
> logarithm of its reduction length?
>
> **Answers.**
> (a) The added work is $M K$ adds for the row sums, one $K$-term reduction per row, plus $M N$
> fix-up subtractions, one per output element. (b) At $M = K = N = 256$: $256^2 + 256^2 = 131{,}072$
> extra operations, which is $0.78\%$ of the $16{,}777{,}216$ core multiply-accumulates, computed as
> the ratio of the correction work to the core work. (c) A binary tree over $256$ inputs needs
> $\lceil \log_2 256 \rceil = 8$ stages, computed as the logarithm of the reduction length. The engine
> keeps the same DSP count; the extra tree stands beside it in look-up tables, which is exactly the
> argument of section 7.2 for keeping weights symmetric.
>
> **Exercise (laddered) -- rounding ties in RTL.**
> A quantizer drops $n = 3$ bits from a signed accumulator holding $125$. (a) Give the rounded output
> under truncation, under round-half-up and under round-half-to-even, computed as $125 / 8 = 15.625$
> rounded by each rule. (b) Repeat for the tie values $124$ and $116$, and name the case that
> separates round-half-up from round-half-to-even. (c) Write a concise SystemVerilog module that
> implements round-half-to-even for a parameterized accumulator width and shift, and state the test
> vectors it must pass that a non-tie corpus misses.
>
> **Answers.**
> (a) Truncation gives $15$; round-half-up gives $16$; round-half-to-even gives $16$ as well, since
> the dropped part, $0.625$, is strictly past the half-step tie. (b) For $124 / 8 = 15.5$: truncation
> $15$, half-up $16$, half-to-even $16$; for $116 / 8 = 14.5$: truncation $14$, half-up $15$,
> half-to-even $14$, because $14$ is even. The tie cases, dropped bits exactly half a step, are where
> the rules separate. (c) The reference is the module of section 7.3; any candidate must pass the tie
> vectors $116$ and $124$ at a shift of $3$, and their negatives, because a bit-exact golden model
> and the fabric agree on everything else.
>
> **Exercise (laddered) -- where the FFN bytes go.**
> A streaming-Conformer block has $d_{\text{model}} = 256$ and a feed-forward expansion of four, so
> $d_{\text{ff}} = 1024$, running at $100$ hops per second. (a) How many weights do the two
> feed-forward networks of one block hold, computed as the product of the two networks, their two
> matrices each, and the two widths? (b) How many bytes per second reach the memory system at INT8
> and at INT4, computed as the weight count times one byte, or half a byte, per weight, times $100$
> hops? (c) What share of the board's $19.2$ GB/s DDR4 is the INT8 stream, computed as the quotient?
> (d) How many $36$-kilobit BRAM tiles hold the INT8 set, and the INT4 set, computed as the quotient
> of the byte count by the tile capacity, rounded up?
>
> **Answers.**
> (a) The two networks hold $2 \cdot 2 \cdot 256 \cdot 1024 = 1{,}048{,}576$ weights. (b) At $100$
> hops per second the INT8 stream is $104{,}857{,}600$ bytes per second, about $104.9$ MB/s, and the
> INT4 stream is half of that, about $52.4$ MB/s, computed as the byte counts times the hop rate. (c)
> The INT8 stream is $0.55\%$ of the registered $19.2$ GB/s, computed as the quotient of $104.9$ MB/s
> by $19.2$ GB/s, and the INT4 stream is $0.27\%$ of it. (d) A $36$-kilobit tile is $4{,}608$ bytes,
> so the INT8 set takes $1{,}048{,}576 / 4{,}608 \approx 227.6$ tiles, rounded up to $228$, and the
> INT4 set takes $113.9$, rounded up to $114$, computed as the quotient of each byte count by the
> tile capacity. The consequence is the section's: the BRAM array alone, one hundred and forty-four
> tiles on the KV260, cannot hold the INT8 set, which therefore lives in URAM or streams from DDR4,
> where the bandwidth math above says it is cheap; INT4 fits the array with room to spare.

**Traceability.** The exercise arithmetic is the reader's own check against the chapter's derivations.
The $18$ dB crest factor and the $40$ dB fricative level are section 7.1's book estimates; the rows
below are the registered records the remaining numbers trace to.

| Record | What it establishes here |
| --- | --- |
| `V-05-36` | the feed-forward expansion of four the fourth exercise's width uses |
| `V-05-31` | the $0.01$ s hop period behind the $100$ hops per second |
| `V-01-13` | the $19.2$ GB/s DDR4 bandwidth the streams are weighed against |
| `V-01-11` | the registered 23,616 kilobits of on-chip SRAM the tile math lands in |

---

## Summary

This chapter took the wrongness chapter 6 handed over and priced it. Section 7.1 established what
quantization noise does to speech: a uniform floor under a signal whose meaning sits far below its
peak, measured with a crest-factor-corrected signal-to-quantization-noise ratio and validated only on
the task's own metric. Section 7.2 worked the first route to small numbers, post-training
calibration, and arrived at a hardware-shaped conclusion: the scale is cheap, the zero point is the
expensive idea, weights should stay symmetric, and the whole budget hinges on where calibration
places the clip. Section 7.3 worked the second route, quantization-aware training, and arrived at a
contract: the training-time quantizer must equal the fabric's tie for tie, and a bit-exact golden
model is a named rounding rule, not a hope. Section 7.4 combined the two routes into the realistic
answer -- mixed precision, with the feed-forward nets narrowed hardest, the attention and the
normalisation kept wider, and per-block scaling that recent silicon confirms. Section 7.5 closed the
one arithmetic gap the rest of the chapter cannot dodge, the softmax itself, made integer-only by a
base-two path. The exercises of section 7.6 then turned each argument into a number the reader can
check on the back of an envelope: a crest-factor budget, a zero-point price, a tie rule, and a
bandwidth count. What the chapter has not done is prove any of this on a board; the acceptance gate
of section 8.4 will decide, on a task's own metric, whether the widths chosen here are enough. That
is where the compromise stops being arithmetic and becomes an experiment.
