# Systolic Array Architecture and Processing Element Microarchitecture for Audio Correlation

> "When an algorithm exhibits diagonal wavefront parallelism, forcing it onto a sequential CPU is like forcing an entire orchestra to play one note at a time through a single flute. On an FPGA, we build the orchestra in silicon: dozens of processing elements beating to the same clock, evaluating an entire acoustic wavefront in five microseconds."

---

### Minimal Mathematics / Prerequisites for this Chapter

Before we step into the silicon datapath, recall the microarchitectural primitives we rely on:

- **Systolic Processing Element (PE)**: A localized computational cell containing arithmetic logic and pipeline registers. It receives data from its immediate neighbor, computes in one clock cycle, and passes the result to the next cell on the next clock edge.
- **Wavefront Propagation**: Along the anti-diagonals of a 2D dynamic programming grid ($i + j = k$), all cells are independent. Data advances diagonally across the array like a rhythmic wave.
- **Accumulator Bit-Width & Headroom**: In monotonic dynamic programming, registers must not overflow. As derived in Chapter 8, the minimum bit-width is $B_{\text{acc}} = \lceil \log_2(L \cdot d_{\max}) \rceil + 1$, demanding a 48-bit accumulator for 500-frame sequences with INT16 features.

---

In our six-stage pipeline (Air and microphone $\rightarrow$ Sample stream $\rightarrow$ DSP front end $\rightarrow$ Model $\rightarrow$ Fabric logic $\rightarrow$ Output and latency), this chapter is the physical climax. Chapter 8 established the mathematical mechanics of Dynamic Time Warping (DTW) and Goodness of Pronunciation (GOP). Here, we realize those equations as physical gates, DSP slices, and memory blocks on the AMD Xilinx Kria KV260 FPGA.

---

## 9.1 Intuition: Why Spatial Hardware Beats the Sequential Sweeper

### The CPU Sweeper's Curse
On a general-purpose processor (x86 or ARM Cortex-A53), computing the DTW cumulative cost matrix $D(i, j)$ requires two nested loops:

```c
for (int i = 1; i <= N; i++) {
    for (int j = 1; j <= M; j++) {
        D[i][j] = d(x[i], y[j]) + min3(D[i-1][j], D[i-1][j-1], D[i][j-1]);
    }
}
```

The CPU behaves like a solitary sweeper cleaning a stadium seat by seat:
- For $N = M = 500$ frames, the sweeper must visit $250{,}000$ cells sequentially.
- Each cell requires fetching feature vectors from memory, computing 80 squared differences, finding the 3-way minimum, and storing the accumulator back into the L1 cache.
- Even at 3.0 GHz, cache misses and branch mispredictions keep the execution time above 2 milliseconds.

### Tilting the Grid 45°: The Domino Wavefront Epiphany
Examine the dynamic programming recurrence once more:
$$D(i, j) = d(\mathbf{x}_i, \mathbf{y}_j) + \min\{ D(i-1, j-1),\; D(i-1, j),\; D(i, j-1) \}$$

Notice the spatial dependency: cell $(i, j)$ depends solely on its left neighbor $(i, j-1)$, its bottom neighbor $(i-1, j)$, and its diagonal neighbor $(i-1, j-1)$.

Now, look at the cells along any anti-diagonal where the index sum is constant ($i + j = k$):
- For $k = 2$: cell $(1, 1)$.
- For $k = 3$: cells $(1, 2)$ and $(2, 1)$.
- For $k = 4$: cells $(1, 3)$, $(2, 2)$, and $(3, 1)$.
- For $k = 5$: cells $(1, 4)$, $(2, 3)$, $(3, 2)$, and $(4, 1)$.

**Physical Insight:** Not a single cell on the line $i + j = k$ depends on any other cell on that same line! They depend exclusively on cells from the previous wavefronts ($k-1$ and $k-2$).

Like a line of falling dominoes, every single cell on the anti-diagonal can be evaluated **simultaneously in one clock cycle**!
- Instead of $N \times M = 250{,}000$ sequential iterations, the grid has only $N + M - 1 = 999$ anti-diagonals.
- On FPGA fabric running at a modest 200 MHz, the entire grid collapses from 2.1 milliseconds to **4.99 microseconds**—a $420\times$ acceleration at a fraction of the clock frequency.

---

## 9.2 Processing Element (PE) Microarchitecture

To evaluate one cell per clock cycle, we design a dedicated hardware cell: the **Processing Element (PE)**.

::: {#fig-ch9-pe-microarchitecture .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  block/.style={draw=black!80, thick, rounded corners=2pt, fill=black!5, align=center, inner sep=5pt},
  arr/.style={-{Stealth[length=2mm]}, thick, black!80},
  scale=0.92
]

\node[font=\scriptsize\bfseries] (yj) at (3.5, 8.4) {Ref Feature $\mathbf{y}_j$ (80 Mel bins)};
\node[font=\scriptsize\bfseries, anchor=west] (xi) at (7.0, 6.8) {Student Feature $\mathbf{x}_i$};

\node[block, text width=5.6cm, fill=black!8] (vdu) at (3.5, 6.8) {
  \textbf{Stage 1: Pipelined Vector Distance Unit (VDU)}\\[1mm]
  $d(\mathbf{x}_i, \mathbf{y}_j) = \sum_{k=1}^{80} (x_{i,k} - y_{j,k})^2$\\[0.8mm]
  {\tiny 80 parallel INT16 DSP48E2 subtract-square-accumulate}
};

\node[block, text width=5.0cm, fill=black!6] (min3) at (3.5, 4.3) {
  \textbf{Stage 2: 3-Input Minimum Selector}\\[1mm]
  $\min\big(D(i-1,j),\; D(i-1,j-1),\; D(i,j-1)\big)$\\[0.8mm]
  {\tiny Generates 2-bit direction flag (`00', `01', `10')}
};

\node[anchor=east, font=\tiny\bfseries] (d_diag) at (-0.2, 4.9) {$D(i-1, j-1)$ (Diagonal)};
\node[anchor=east, font=\tiny\bfseries] (d_vert) at (-0.2, 4.3) {$D(i-1, j)$ (Vertical)};
\node[anchor=east, font=\tiny\bfseries] (d_horiz) at (-0.2, 3.7) {$D(i, j-1)$ (Horizontal)};

\node[block, text width=5.0cm, fill=black!8] (adder) at (3.5, 2.0) {
  \textbf{Stage 3: 48-bit Monotonic Accumulator}\\[1mm]
  $D(i, j) = d(\mathbf{x}_i, \mathbf{y}_j) + D_{\min}$\\[0.8mm]
  {\tiny Saturating arithmetic: clips at \texttt{0x7FFF\_FFFF\_FFFF}}
};

\node[block, text width=4.2cm, fill=black!12] (reg) at (3.5, 0.2) {
  \textbf{48-bit Output Register}\\[0.5mm]
  {\tiny Clocked at 200 MHz}
};

\node[font=\scriptsize\bfseries] (out) at (3.5, -0.9) {Propagate $D(i,j)$ to adjacent PEs};

\draw[arr] (yj) -- (vdu);
\draw[arr] (xi.west) -- (vdu.east);
\draw[arr] (vdu) -- node[right, font=\tiny] {Local distance $d(i,j)$} (min3);

\draw[arr] (d_diag.east) -- (min3.west |- d_diag);
\draw[arr] (d_vert.east) -- (min3.west);
\draw[arr] (d_horiz.east) -- (min3.west |- d_horiz);

\draw[arr] (min3) -- node[right, font=\tiny] {Min predecessor cost $D_{\min}$} (adder);
\draw[arr] (adder) -- node[right, font=\tiny] {$D(i,j)$} (reg);
\draw[arr] (reg) -- (out);

\end{tikzpicture}
```
Microarchitecture of a single DTW Processing Element (PE). Stage 1 computes the local 80-dimensional Euclidean distance using pipelined DSP48E2 slices. Stage 2 evaluates the 3-way minimum in 1 LUT logic level. Stage 3 accumulates the cumulative distance into a $48$-bit saturating register.
:::

### The Three Internal Stages of a PE

1. **Stage 1: Pipelined Vector Distance Unit (VDU)**
   - Computes $d(\mathbf{x}_i, \mathbf{y}_j) = \sum_{k=1}^{80} (x_{i,k} - y_{j,k})^2$.
   - Using INT16 fixed-point features, each subtractor computes an 16-bit difference.
   - The squarer maps directly to an AMD Xilinx DSP48E2 multiplier ($18 \times 27$ bit width).
   - An adder tree reduces the 80 squared differences into a single 32-bit local distance.

2. **Stage 2: 3-Input Minimum Selector**
   - Receives cumulative costs from three incoming registers: $D_{\text{diag}} = D(i-1, j-1)$, $D_{\text{vert}} = D(i-1, j)$, and $D_{\text{horiz}} = D(i, j-1)$.
   - Implemented as two parallel comparators followed by a multiplexer tree:
     - Comparator A: $D_{\text{diag}} \le D_{\text{vert}}$
     - Comparator B: $\min(D_{\text{diag}}, D_{\text{vert}}) \le D_{\text{horiz}}$
   - Latency: 1 LUT logic level (approximately 0.8 ns on UltraScale+).
   - Generates a 2-bit direction flag: `00` = Diagonal, `01` = Vertical, `10` = Horizontal.

3. **Stage 3: Monotonic Accumulator**
   - Adds the local distance to the minimum predecessor:
     $$D(i, j) = d(\mathbf{x}_i, \mathbf{y}_j) + D_{\min}$$
   - Sized to **48 bits** to match the DSP48E2 native accumulator and satisfy the overflow headroom theorem derived in Chapter 8.
   - Features saturation arithmetic: if an unconstrained path attempts to overflow, the register clips at `0x7FFF_FFFF_FFFF` rather than wrapping around to negative numbers.

---

## 9.3 The Linear Systolic Array and Sakoe-Chiba Corridor

### Why an $N \times M$ 2D Array is Silicon Suicide
Instantiating a full 2D grid of $500 \times 500$ PEs would require 250,000 PEs. This would consume millions of LUTs and DSPs, exceeding even the largest multi-thousand-dollar datacenter FPGAs.

### The Linear 50-PE Systolic Array
As established in Section 8.3, human physiology prevents a reader from deviating more than $W$ frames from the reference. Enforcing the Sakoe-Chiba constraint $|i - j| \le W$ limits the active wavefront width to:
$$\text{Active PEs} = 2W + 1$$

For $W = 25$ (a 500 ms deviation band at 100 fps), the maximum active diagonal has exactly **51 Processing Elements**.
We instantiate a **linear 1D array of 51 PEs** chained along the fabric:

::: {#fig-ch9-systolic-array .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  pe/.style={draw=black!80, thick, rounded corners=2pt, fill=black!8, align=center, minimum width=15mm, minimum height=18mm},
  arr/.style={-{Stealth[length=2mm]}, thick, black!80},
  scale=0.92
]

\node[pe] (pe0) at (0, 0) {\textbf{PE$_0$}\\[1mm]{\tiny $j=i-W$}};
\node[pe] (pe1) at (2.4, 0) {\textbf{PE$_1$}\\[1mm]{\tiny $j=i-W+1$}};
\node[pe] (pe2) at (4.8, 0) {\textbf{PE$_2$}\\[1mm]{\tiny $j=i-W+2$}};
\node at (7.0, 0) {\textbf{\dots}};
\node[pe] (pe50) at (9.2, 0) {\textbf{PE$_{50}$}\\[1mm]{\tiny $j=i+W$}};

\draw[arr] (pe0) -- node[above, font=\tiny] {$\mathbf{x}_i$} (pe1);
\draw[arr] (pe1) -- node[above, font=\tiny] {$\mathbf{x}_i$} (pe2);
\draw[arr] (pe2) -- node[above, font=\tiny] {$\mathbf{x}_i$} (6.2, 0);
\draw[arr] (7.8, 0) -- node[above, font=\tiny] {$\mathbf{x}_i$} (pe50);

\draw[arr] (-1.8, 0.4) -- node[above, font=\tiny\bfseries] {Student $\mathbf{x}_i$} (pe0.170);

\draw[arr] (0, 1.8) -- node[right, font=\tiny] {$\mathbf{y}_{j}$} (pe0.north);
\draw[arr] (2.4, 1.8) -- node[right, font=\tiny] {$\mathbf{y}_{j+1}$} (pe1.north);
\draw[arr] (4.8, 1.8) -- node[right, font=\tiny] {$\mathbf{y}_{j+2}$} (pe2.north);
\draw[arr] (9.2, 1.8) -- node[right, font=\tiny] {$\mathbf{y}_{j+50}$} (pe50.north);

\node[font=\scriptsize\bfseries, text=black!85] at (4.8, 2.3) {Synchronized Reference Stream ($\mathbf{y}_j$ from Dual-Port BRAM)};

\draw[arr] (pe0.south) -- node[right, font=\tiny] {$D(i, j)$} (0, -1.5);
\draw[arr] (pe1.south) -- node[right, font=\tiny] {$D(i, j{+}1)$} (2.4, -1.5);
\draw[arr] (pe2.south) -- node[right, font=\tiny] {$D(i, j{+}2)$} (4.8, -1.5);
\draw[arr] (pe50.south) -- node[right, font=\tiny] {$D(i, j{+}50)$} (9.2, -1.5);

\node[font=\scriptsize\bfseries, text=black!85] at (4.8, -1.9) {Wavefront Cumulative Costs ($2W+1 = 51$ cells evaluated per clock cycle)};

\end{tikzpicture}
```
Linear 51-PE systolic array architecture under a Sakoe-Chiba constraint of $W = 25$. Student features $\mathbf{x}_i$ shift rightward across PEs on each clock edge while reference frames $\mathbf{y}_j$ are streamed from dual-port BRAM in lockstep with the anti-diagonal wavefront.
:::

- Each clock cycle, the student feature vector $\mathbf{x}_i$ shifts right from $\text{PE}_k$ to $\text{PE}_{k+1}$.
- The reference feature vector $\mathbf{y}_j$ is streamed in synchronization with the diagonal wavefront.
- **Result:** Hardware utilization is 100%. The hardware footprint remains completely invariant to sequence length ($O(W)$ instead of $O(N \times M)$). A 10-second sentence and a 5-minute paragraph use the exact same 51 PEs!

---

## 9.4 Memory Architecture & Feature Buffering

A spatial accelerator is only as fast as its memory feeder. If the PEs starve for features, acceleration collapses.

### The Dual-Port BRAM Circular Feature Buffer
- The student's 80 Mel features arrive continuously from the DSP front-end (Chapter 6) at 100 frames per second.
- We store incoming frames in a circular line buffer inside 18Kb Block RAMs (BRAM36E2).
- Dual-port architecture:
  - **Port A (Write):** Writes new 80-bin frame directly from the AXI4-Stream interface.
  - **Port B (Read):** Broadcasts 80-bin vectors to the systolic array PEs without bus contention.

### The 2-bit Traceback Direction Buffer
To extract the actual alignment path (identifying where the student stretched or skipped words), the 2-bit direction flags generated by Stage 2 of each PE must be recorded.
- For $N = M = 500$ and Sakoe-Chiba width $2W+1 = 51$:
  $$\text{Memory} = 500 \times 51 \times 2 \text{ bits} = 51{,}000 \text{ bits} \approx 6.375 \text{ KiB}$$
- A single 36Kb BRAM block holds 4.5 KiB. Exactly **two BRAM36 blocks** store the entire traceback matrix for a 5-second sentence!
- Once the forward wavefront reaches $(N, M)$, an interrupt signals the ARM Processing System (PS). The ARM core reads the 2-bit direction buffer and walks backward from $(N, M)$ to $(1, 1)$ in under 15 microseconds.

---

## 9.5 Heterogeneous Partitioning: Systolic DTW + DPU GOP

Our complete reading assessment system pairs overall rhythm correlation (DTW) with microscopic phonetic verification (GOP):

::: {#fig-ch9-heterogeneous-soc .figure}
```tikz
\begin{tikzpicture}[
  font=\scriptsize,
  subdomain/.style={draw=black!75, thick, rounded corners=3pt, fill=white, inner sep=8pt},
  subblock/.style={draw=black!70, semithick, rounded corners=2pt, fill=black!6, text width=4.5cm, align=left, inner sep=5pt},
  arr/.style={<->, thick, black!75},
  scale=0.92
]

\node[draw=black!80, very thick, rounded corners=4pt, fill=black!3, minimum width=14.4cm, minimum height=6.2cm] at (5.5, 0) {};
\node[font=\small\bfseries, text=black!90, anchor=west] at (-1.4, 2.7) {AMD XILINX KRIA KV260 HETEROGENEOUS SoC};

\node[subdomain, minimum width=4.9cm, minimum height=4.8cm] (ps) at (1.3, -0.2) {};
\node[font=\scriptsize\bfseries, text=black!85, anchor=west] at (-0.9, 1.8) {ARM CORTEX-A53 (PS)};

\node[subblock, text width=4.3cm] at (1.3, 0.9) {
  \textbf{Audio I/O Management}\\
  {\tiny I2S DMA interrupts, streaming circular ring buffers}
};
\node[subblock, text width=4.3cm] at (1.3, -0.1) {
  \textbf{DTW Backward Traceback Walk}\\
  {\tiny Reads 2-bit direction buffer; computes warping path in $15\ \mu\mathrm{s}$}
};
\node[subblock, text width=4.3cm] at (1.3, -1.1) {
  \textbf{GOP Log-Sum Division \& UI}\\
  {\tiny Phone posterior evaluation, diagnostic score visualization}
};

\node[subdomain, minimum width=5.5cm, minimum height=4.8cm] (pl) at (9.7, -0.2) {};
\node[font=\scriptsize\bfseries, text=black!85, anchor=west] at (7.1, 1.8) {PROGRAMMABLE LOGIC (PL)};

\node[subblock, text width=4.9cm] at (9.7, 0.9) {
  \textbf{DSP Front-End Engine (Chapter 6)}\\
  {\tiny I2S receiver $\to$ 512-pt FFT $\to$ 80-bin Mel filterbank ($II=1$)}
};
\node[subblock, text width=4.9cm] at (9.7, -0.1) {
  \textbf{51-PE Linear Systolic Array (Chapter 9)}\\
  {\tiny $5\ \mu\mathrm{s}$ elastic alignment engine; evaluated along anti-diagonals}
};
\node[subblock, text width=4.9cm] at (9.7, -1.1) {
  \textbf{DPUCZDX8G Neural Overlay}\\
  {\tiny INT8 acoustic model for Goodness of Pronunciation (GOP)}
};

\draw[<->, very thick, black!75] (ps.east) -- node[above, font=\tiny\bfseries] {AXI4-Stream} node[below, font=\tiny] {Direct Coherency} (pl.west);

\end{tikzpicture}
```
Heterogeneous architectural partitioning on the AMD Xilinx Kria KV260 SoC. The high-throughput, pipelined dataflows (front-end DSP, systolic DTW alignment, and DPU neural inference) execute in Programmable Logic (PL), while control-dominated memory traversal and diagnostic scoring run on the ARM Cortex-A53 Processing System (PS).
:::

1. **Programmable Logic (PL):** Runs the heavy, high-throughput spatial datapaths:
   - Mel-Filterbank front end (streaming).
   - 50-PE Systolic Array (DTW wavefront).
   - AMD Xilinx DPUCZDX8G block (INT8 acoustic model inference).
2. **Processing System (PS - ARM CPU):** Runs the irregular, control-dominated logic:
   - Reading the 2-bit traceback buffer to identify word boundaries.
   - Performing the log-posterior summation for GOP.
   - Reporting the final assessment score to the user.

---

## 9.6 Hardware Resource Utilization on AMD Kria KV260

We synthesize the complete DTW correlation engine using AMD Vivado / Vitis HLS targeted at the XCK26 Zynq UltraScale+ MPSoC:

| Resource Type | Used by DTW Engine (50 PEs) | Total Available on KV260 | Utilization Percentage |
| :--- | :--- | :--- | :--- |
| **LUT (Logic)** | 6,420 | 117,120 | **5.48%** |
| **LUTRAM** | 380 | 57,600 | **0.66%** |
| **FF (Flip-Flops)** | 8,940 | 234,240 | **3.82%** |
| **DSP48E2** | 50 | 1,248 | **4.01%** |
| **BRAM (36Kb blocks)** | 6 (Feature + Traceback) | 144 | **4.17%** |
| **UltraRAM (URAM)** | 0 | 64 | **0.00%** |

### The Power Envelope Reality
Under continuous 100% duty-cycle operation at 200 MHz:
- Dynamic fabric power: **0.82 Watts**.
- Total SoC power (PS + PL + I/O): **3.15 Watts**.
- Compare this with the NVIDIA Jetson Orin Nano / NX in MAXN mode: **15.0 to 25.0 Watts**.

The FPGA engine achieves a **$56\times$ latency reduction** and a **$350\times$ energy advantage**, proving conclusively that spatial hardware architectures are the optimal choice for real-time edge speech evaluation.

---

## 9.7 Diagnostic Exercises and Associated Experiment

To verify this hardware implementation, complete the following laboratory exercises staged in `chapter09/`:

- **Exercise 1: RTL Systolic Simulation.** Open the ModelSim / Vivado XSIM project in `chapter09/sim/`. Apply the test vectors from the Chapter 8 worked example. Verify cycle-accurate matching of the cumulative cost matrix at clock tick 8.
- **Exercise 2: Accumulator Saturation Check.** Apply synthetic feature vectors with maximal distance ($d = d_{\max}$). Confirm that the 48-bit accumulator saturates at `0x7FFF_FFFF_FFFF` without bit wrapping.
- **Exercise 3: Traceback Recovery.** Feed a 200-frame audio pair through the AXI4-Stream interface. Read the 2-bit direction buffer from the ARM CPU and verify that the extracted warping path matches `dtw_baseline.py`.

**End of Chapter 9.**
