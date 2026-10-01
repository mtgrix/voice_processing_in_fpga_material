# 1.4 Hardware Consequences and Processing Latency Limits

#### Organic Bridge from Section 1.3: Mapping Equations onto Physical Transistors

In Section 1.3, we completed the mathematical microscope of the front-end DSP pipeline, transforming 400 streaming pressure samples into 80 Log-Mel spectral values. But an algorithm on paper assumes infinite memory and zero execution time. In this section, we force these abstract equations to collide with physical silicon: evaluating how the mathematical parameters translate into memory footprint and processing deadlines across an Edge GPU (NVIDIA Jetson Orin Nano) and a spatial FPGA fabric (AMD Xilinx Kria KV260).

> 💡 **LEARNING OBJECTIVE**  
> Rather than treating hardware latency as an arbitrary processing delay, this section grounds timing in physical acoustic accumulation, contrasts on-chip Block RAM allocations against external memory bandwidth, and exposes why the migration of audio front-ends to FPGA logic is driven by deterministic execution and zero-jitter hardware isolation rather than raw arithmetic throughput.

---

### State 1: The Physical Latency Floor

Latency in a streaming audio system has an absolute physical lower bound that is dictated by acoustics before any semiconductor chip is ever powered on. Three temporal quantities are permanently locked by the front-end acoustic specification:

| Parameter | Numerical Value | Mathematical Origin & Physical Definition |
| :--- | :--- | :--- |
| First-frame accumulation floor | $25\text{ ms}$ | $L / f_s = 400 / 16{,}000$ (Microphone diaphragm collection time) |
| Hop cadence between frames | $10\text{ ms}$ | $H / f_s = 160 / 16{,}000$ (Periodic emission interval to downstream model) |
| Overlap ratio across adjacent frames | $60\%$ | $(L - H) / L = 240 / 400$ (Shared historical context preserving boundary energy) |

This acoustic reality establishes a strict latency floor that no processor can circumvent: **Frame 0 physically cannot exist** before $25\text{ ms}$ of continuous air pressure vibrations have physically struck the microphone diaphragm. Even a theoretical $5\text{ GHz}$ CPU executing the spectral transformation in zero nanoseconds cannot emit the first feature vector at $t = 24.9\text{ ms}$ because the four-hundredth audio sample has not yet occurred in physical reality.

```
+-----------------------------------------------------------------------------+
| Figure 1.4a: Acoustic Latency Floor vs. Processing Speed                    |
| [Timeline showing Frame 0 physical accumulation (0-25 ms) setting the floor |
|  followed by Frame 1 (10-35 ms, 60% overlap) and 10 ms periodic cadence.    |
|  Processor speed arrow highlights that near-zero compute time cannot erase  |
|  the 25 ms physical accumulation requirement.]                              |
+-----------------------------------------------------------------------------+
```

Once the initial $25\text{ ms}$ accumulation floor is satisfied, the system enters steady-state operation. From this point forward, the microphone emits a new block of $H = 160$ samples every $10\text{ ms}$. This $10\text{ ms}$ interval is the **hard real-time deadline**: all downstream computations—windowing, 512-point FFT, power spectrum, 80-channel Mel filtering, logarithmic compression, and neural network inference—must complete within $10\text{ ms}$. A faster processor does not shrink the $25\text{ ms}$ physical floor; it merely prevents additional computational delay from accumulating on top of it.

---

### State 2: Memory Footprint on Physical Silicon

To evaluate physical feasibility, we ground our memory requirements against official hardware specifications from the AMD DS890 datasheet for the Zynq UltraScale+ `XCK26` Multiprocessor SoC (MPSoC) deployed on the Kria KV260:

- **117,120** logic cell Lookup Tables (LUTs).
- **144** Block RAM blocks of $36\text{ kbit}$ each ($5.1\text{ Mb} \approx 648\text{ KiB}$ total on-chip SRAM).
- **64** UltraRAM blocks ($18.0\text{ Mb} \approx 2.25\text{ MiB}$ total on-chip bulk SRAM).
- **1,248** DSP48E2 compute slices optimized for single-cycle multiply-accumulate operations.

Now contrast these available resources against the two core state structures that the streaming DSP front-end must maintain in 32-bit single-precision floating point (FP32):

1. **Audio Ring Buffer ($400$ samples)**: At $4\text{ bytes}$ per sample, storing the running acoustic history requires $400 \times 4\text{ B} = 1{,}600\text{ bytes}$. A single $36\text{-kbit}$ Block RAM block provides $4{,}608\text{ bytes}$ of dual-port storage. The entire time-domain state occupies only **$34.7\%$ of a single BRAM block** ($0.2\%$ of total on-chip BRAM).
2. **Mel Filterbank Weight Matrix ($80 \times 257$)**: Dense storage of the triangular filter weights requires $80 \times 257 \times 4\text{ B} = 82{,}240\text{ bytes} = 80.3\text{ KiB}$. This entire coefficient matrix requires 18 Block RAM blocks, consuming exactly **$12.4\%$ of total on-chip BRAM**.

> 💡 **PHYSICAL INSIGHT**  
> Because the combined memory footprint of the front-end state and filterbank matrix ($81.9\text{ KiB}$) consumes less than $13\%$ of on-chip Block RAM, the entire DSP pipeline fits within local FPGA SRAM. The hardware requires zero round-trips to external DDR DRAM, eliminating dynamic memory arbitration, DRAM refresh stalls, and memory bus energy consumption.

---

### State 3: The Arithmetic Fallacy — Throughput vs. Deterministic Isolation

Evaluating the 80-channel Mel filterbank requires multiplying 257 power spectral bins by 80 triangular weight vectors:
$$\text{Workload per frame} = 80 \times 257 = 20{,}560\ \text{MAC operations}$$

At a hop cadence of $10\text{ ms}$, the front-end produces $100\text{ frames per second}$, resulting in an aggregate computational throughput of:
$$\text{Throughput} = 20{,}560\ \text{MAC/frame} \times 100\ \text{frames/s} = 2.056 \times 10^6\ \text{MAC/s} \approx 2.06\ \text{MMAC/s}$$

Spread evenly across the $1{,}248$ DSP48E2 slices of the Kria KV260, each individual DSP slice would need to execute only **$1{,}647\text{ operations per second}$**. When clocked at $200\text{ MHz}$, a single DSP48E2 slice provides $200 \times 10^6\text{ MAC/s}$; thus, the entire front-end arithmetic workload represents less than $0.001\%$ of the chip's computational capacity.

Now compare this to the competing edge accelerator: the **NVIDIA Jetson Orin Nano Super**. The Orin Nano delivers up to **67 sparse INT8 TOPS** (or approximately **33 dense TOPS** at a $25\text{ W}$ power ceiling). Against this massive computing budget, the $2.06\text{ MMAC/s}$ required by the voice front-end is literally **one millionth** of the GPU's available processing bandwidth.

```
+-----------------------------------------------------------------------------+
| Figure 1.4b: KV260 BRAM Breakdown and Datapath Determinism Comparison       |
| [Panel (a): KV260 BRAM breakdown showing Ring Buffer (0.2%), Mel Filterbank |
|  Matrix (12.4%), and Free BRAM (87.4%) for downstream neural networks.      |
|  Panel (b): Edge GPU shared software stack (DMA -> OS preemption -> CUDA    |
|  launch -> Jitter) versus Spatial FPGA dedicated wires (I2S -> Pipelined   |
|  DSP -> Zero-jitter deterministic completion).]                             |
+-----------------------------------------------------------------------------+
```

This disparity exposes a central architectural truth: **migrating an audio front-end to FPGA logic is never about raw arithmetic throughput**. An edge GPU possesses orders of magnitude more raw floating-point performance. The migration is driven entirely by **temporal determinism and hardware isolation**:

- **The Shared Software Trap (Edge GPU)**: On a GPU/CPU system, the audio front-end shares the $10\text{ ms}$ processing window with the Linux operating system kernel, microphone DMA driver interrupts, background network stacks, and concurrent neural network inference. Each CUDA kernel invocation incurs $5\text{--}15\ \mu\text{s}$ of launch overhead, and operating system thread scheduling introduces random preemption. A deadline shared among multiple asynchronous software layers is inherently subject to latency jitter ($\Delta t_{\text{jitter}}$).
- **The Dedicated Spatial Fabric (FPGA)**: On an FPGA, the DSP pipeline is constructed from dedicated, physically isolated silicon wires and registers. It does not share a clock, an execution pipeline, or a memory bus with an operating system. The front-end completes each frame in a mathematically fixed number of clock cycles ($N_{\text{clk}}$), guaranteeing an execution jitter of identically zero nanoseconds ($\Delta t = 0\text{ ns}$).

> 💡 **GROUNDBREAKING FINDING**  
> The FPGA does not outperform the edge GPU on raw arithmetic throughput; it outperforms the GPU on deterministic isolation. Dedicated silicon wires guarantee zero-jitter execution within the non-negotiable 10 ms hop deadline, completely decoupled from operating system preemption and memory contention.

---

### Organic Bridge to Section 1.5: Stress-Testing Hardware Boundaries

We have established that the streaming front-end pipeline maps with exceptional efficiency onto physical FPGA resources—consuming minimal Block RAM and a negligible fraction of DSP slices while securing absolute latency determinism. 

However, mathematical formulations reveal catastrophic points of failure when pushed beyond their operating boundaries. What happens if a designer attempts to lower latency by cutting window length in half? What happens if audio is sampled at studio rates ($48\text{ kHz}$)? What happens if dense matrix evaluation is chosen over sparse compression? In Section 1.5, we subject our theoretical models to four rigorous diagnostic stress-tests, examining where edge silicon breaks when pushed to its limits.
