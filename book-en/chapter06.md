# Audio Preprocessing in Hardware: I2S, Frame Buffering and the STFT

> *Objective: Design and synthesize dedicated hardware IP cores for fixed-point FFT/STFT and Mel Filterbank extraction directly connected to digital microphone interfaces.*

---

## The same reduction, rebuilt as something you would have to wire

Chapter 1 took a stream of numbers down to eighty of them -- frame, fade, transform, squash onto the
Mel scale, take the logarithm -- and did it as software calling functions, where the only cost worth
naming was arithmetic. This chapter does that identical reduction again, but as hardware somebody has
to place on a chip and route with real wires, and the moment the steps become circuits the questions
change completely. Not "how many multiply-accumulates does a frame need," which chapter 1 already
answered, but "how wide is the bus into the multiplier, how deep is the buffer that holds a frame
between two stages, and what happens on the cycle the data does not arrive." A step that was one line of
Python is now a block with an input, an output, a clock, and a place to store what it is mid-way through.

The chapter follows the signal from the microphone inward. It starts at the boundary, because the FPGA
board has no microphone of its own and the first real decision is how audio gets into the fabric at all
-- a serial link a codec drives, or a stream of single-bit pulses that has to be counted down to a
usable rate -- and it argues for pulling that ingestion *inside* the design rather than handing it off
to a processor, which is the move that keeps the whole front end flowing instead of stopping to be
serviced. From there it builds the fixed-point transform engine, the part that decides how many bits
each intermediate is allowed and where the rounding error is permitted to land, then the Mel
multiplication and the logarithm, which a chip cannot compute exactly and has to approximate out of
tables and shifts.

Read it as chapter 1's mirror. Every quantity chapter 1 derived -- the frame length, the hop, the
transform size, the band count -- is a *parameter* here, and this chapter is where those parameters turn
into wires, memory, and latency. It is also the first place the book confronts a trade that recurs for
the rest of it: fixed-point arithmetic is cheaper in every currency a board cares about, and it is
wrong in a bounded way that has to be measured, not assumed. That wrongness is the subject of chapter 7,
which this chapter sets up without answering.

---

## 6.1 Bypassing the CPU-to-FPGA Host Bottleneck
## 6.2 Fixed-Point Radix-2 / Radix-4 FFT Hardware Engines
## 6.3 Mel Filterbank Matrix Multiplication & Log Approximation on Fabric
## 6.4 Direct Audio Ingestion: I2S Interfaces and PDM Decimation Filtering
