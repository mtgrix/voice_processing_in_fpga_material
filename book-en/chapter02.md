# The Jetson Orin Baseline: Microarchitecture and Profiling

> *Objective: Dissect the NVIDIA Jetson Orin SoC architecture (Ampere GPU, Tensor Cores, LPDDR5, DLA) and establish rigorous baseline measurement protocols (TensorRT, tegrastats).*

---

> ### Minimal Mathematics / Prerequisites for this Chapter
> 
> - **Energy per Frame**: $E_{\text{frame}} = P_{\text{avg}} \times \Delta t_{\text{latency}}$ ($\text{Joules}$ or $\text{mJ}$).
> - **Real-Time Factor (RTF)**: $\text{RTF} = T_{\text{compute}} / T_{\text{audio}}$.
> - **Tail Latency (P99)**: 99th percentile processing latency across thousands of consecutive streaming frames.

---

## The number this whole book is trying to beat

A migration has to start somewhere, and the starting point here is a small computer that is already on
the desk: the NVIDIA Jetson Orin. It is not a stand-in for the FPGA or a foil to knock down. It is the
honest baseline, the thing that already works, ships with a compiler, and runs the model today. The
question this chapter answers is narrow and uncomfortable by turns: what does that board *actually* do
to one frame of audio, as opposed to what its marketing page says it can do? Those two numbers are not
the same number, and the gap between them is the whole reason a measurement has to be taken rather than
looked up.

The chapter does three things in order. It opens the box -- an ARM CPU, an Ampere GPU built around
wide groups of lanes that march together, a single LPDDR5 memory bus shared by all of them, and fixed
engines that do one job well -- so that later claims about *why* the board behaves as it does have
somewhere to point. It then says how to measure it so the measurement would survive a skeptic: which
power mode the board is in, because that changes everything, and which sensor the power figure is read
from, because "watts" is not one quantity on this device. And it ends by writing the scorecard the
board is asked to fill in, which is the same shape every other machine is scored on later.

Three quantities run through the whole book and are defined here once, because this is where they get
their first real numbers. **Energy per frame** is power multiplied by the time one frame takes: a board
drawing a certain number of joules a second for a certain number of seconds of work costs the product,
so a faster board is not automatically a cheaper one if it burns more to go faster. **Real-time factor**
is compute time divided by the length of the audio it processed -- under one means the machine keeps up
with the microphone, over one means it falls behind and the buffer grows without bound. **Tail latency**
is not the average frame but the unlucky one, the ninetieth-percentile-and-worse case that a listener
actually hears as a dropout. All three reappear in chapter 10, where they stop being definitions and
become the axes a result is judged on. What this chapter cannot yet supply is the numbers themselves:
no board is on a bench, so the scorecard is drawn with its cells named and left empty, and filling them
is the work chapter 10 describes.

---

## 2.1 Intuition: The Power and Paradox of NVIDIA Jetson Orin
<!-- High peak TOPS vs low compute efficiency under fine-grained streaming audio -->

## 2.2 SoC Architecture: ARM Cores, Ampere SM, and LPDDR5 Memory Subsystem
<!-- Hardware block diagram and SIMT warp scheduling limits -->

## 2.3 Benchmarking Methodology: TensorRT and Hardware Power Sensors
<!-- Compilation with TensorRT, INA3221 shunt reading via tegrastats -->

## 2.4 The Baseline Scorecard
<!-- Latency distribution, RTF, power, and energy consumption metrics -->

---

## Associated Experiment
- Refer to [`chapter02/`](../chapter02/).
