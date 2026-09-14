# Four Ways to Accelerate on an FPGA: DPU, HLS, FINN and RTL

> *Objective: Comprehensively evaluate and compare four hardware implementation methodologies for neural acceleration on FPGAs.*

---

## 5.1 The Four Hardware Implementation Paths
## 5.2 Trade-off Analysis: Productivity, Flexibility, Latency, and Resource Efficiency
## 5.3 Selecting the Optimal Architecture for Edge Voice Workloads

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
