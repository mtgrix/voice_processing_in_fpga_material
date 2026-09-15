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
