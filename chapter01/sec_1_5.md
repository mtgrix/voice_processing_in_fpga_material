# 1.5 Diagnostic Failure Modes: Stress-Testing Silicon and Acoustic Boundaries

> **LEARNING OBJECTIVE**  
> Rather than treating the 16 kHz / 25 ms / N=512 / dense Mel stack as sacred, this section breaks each knob and shows where silicon and speech physics refuse to follow.

---

### Organic Bridge from Section 1.4: Testing Physical Limits at the Hardware Boundary

In Section 1.4, we grounded the front-end DSP pipeline in physical silicon, proving that on an AMD Kria KV260 FPGA, the streaming time-domain buffer and Mel filterbank consume minimal Block RAM ($12.6\%$) and negligible DSP48E2 compute ($< 0.001\%$). In contrast to an edge GPU (NVIDIA Jetson Orin Nano Super) where software scheduling, driver queues, and Linux OS interrupts introduce unpredictable latency jitter ($\Delta t_{\text{jitter}} > 0$), the FPGA architecture guarantees deterministic, cycle-accurate execution within the $10\text{ ms}$ real-time hop deadline.

However, an algorithm that runs smoothly under nominal parameters often conceals sharp mathematical and physical failure boundaries. When a systems engineer attempts to optimize performance by turning architectural knobs—such as tripling the sampling rate for higher fidelity, slashing the window duration to cut latency, omitting zero-padding to reduce FFT points, or storing filter matrices in dense floating-point format—the underlying physics of acoustic wave propagation and spatial silicon microarchitectures violently push back.

The four diagnostic scenarios below examine these boundary conditions. Each scenario demonstrates how an apparently intuitive software modification collapses against physical acoustic laws or saturates on-chip FPGA resources.

---

### Diagnostic Scenario 1: The Sampling Rate Illusion

#### The Naive Hypothesis
A systems engineer proposes upgrading the front-end audio acquisition pipeline from the standard $f_s = 16\text{ kHz}$ to the professional studio sampling standard $f_s = 48\text{ kHz}$. The stated engineering rationale is that tripling the temporal sampling rate will preserve subtle high-frequency acoustic nuances, suppress quantization noise, and boost keyword-spotting accuracy, while keeping the acoustic window length at $25\text{ ms}$ and the hop cadence at $10\text{ ms}$.

#### Worked Mathematical Breakdown
1. **Sample Counts ($L_{48}$ and $H_{48}$):**  
   At $f_s = 48\text{ kHz}$, the sampling period shrinks to $T_s = 1 / 48{,}000\text{ s} \approx 20.833\ \mu\text{s}$. To preserve the physical frame duration of $25\text{ ms}$ and hop cadence of $10\text{ ms}$, the required sample counts scale linearly:
   $$\begin{aligned}
   L_{48} &= 48{,}000\text{ samples/s} \times 0.025\text{ s} = 1{,}200\text{ samples} \\
   H_{48} &= 48{,}000\text{ samples/s} \times 0.010\text{ s} = 480\text{ samples}
   \end{aligned}$$
   Both quantities exactly triple compared to the nominal $16\text{ kHz}$ baseline ($L = 400$, $H = 160$).

2. **On-Chip Memory Allocation:**  
   Assuming standard 32-bit single-precision floating-point samples (FP32, 4 bytes per sample), storing the running $1{,}200$-sample audio frame requires:
   $$\text{Buffer Size}_{48} = 1{,}200 \times 4\text{ B} = 4{,}800\text{ bytes}$$
   A single physical 36-kbit Block RAM (RAMB36E2) on the AMD XCK26 MPSoC provides exactly $36{,}864\text{ bits} = 4{,}608\text{ bytes}$ of storage. Because $4{,}800\text{ bytes} > 4{,}608\text{ bytes}$, the circular buffer overflows a single physical BRAM primitive. The FPGA synthesis engine is forced to allocate **two dedicated 36-kbit Block RAM blocks** to host the time-domain history, doubling the required silicon memory footprint.

3. **Acoustic Reality and Nyquist Bounds:**  
   According to the Nyquist-Shannon sampling theorem, a sampling rate of $f_s = 48\text{ kHz}$ yields an acoustic Nyquist bandwidth of $f_{\text{max}} = f_s / 2 = 24\text{ kHz}$. However, the vocal tract resonances that define human speech—the fundamental pitch ($F_0 \approx 85\text{--}255\text{ Hz}$) and vowel formants ($F_1$ to $F_4$ spanning $250\text{--}4{,}500\text{ Hz}$), as well as sibilant fricatives ($/s/, /\int/$ peaking between $4{,}000\text{--}7{,}500\text{ Hz}$)—are entirely contained below $8\text{ kHz}$.  
   The expanded $8\text{--}24\text{ kHz}$ spectral octaves contain zero phonological information; they capture only ambient thermal hiss, circuit switching noise, and ultrasonic environmental artifacts. Furthermore, processing $1{,}200$ samples requires expanding the downstream FFT length to at least $N = 2{,}048$ points, more than quadrupling the butterfly compute workload. The engineering team pays a $3\times$ penalty in on-chip memory, a $3\times$ penalty in streaming I/O throughput, and a $>4\times$ surge in DSP arithmetic for **identically zero acoustic or keyword recognition gain**.

> **PHYSICAL INSIGHT**  
> Tripling the sampling rate from $16\text{ kHz}$ to $48\text{ kHz}$ overflows the $4{,}608\text{-byte}$ boundary of a physical 36-kbit Block RAM block and quadruples downstream arithmetic, squandering silicon area and dynamic power to capture ultrasonic frequencies outside the biomechanical limits of human vocal cords.

---

### Diagnostic Scenario 2: The Gabor–Heisenberg Penalty

#### The Naive Hypothesis
To eliminate speech processing lag in an ultra-responsive edge voice assistant, an embedded designer seeks to aggressively reduce the physical frame accumulation floor. Rather than waiting $25\text{ ms}$ for $400$ audio samples to accumulate, the designer cuts the analysis window length by $80\%$, setting $L = 80$ samples ($\Delta t = 5\text{ ms}$) at $f_s = 16\text{ kHz}$, arguing that modern deep neural networks can extract acoustic features just as easily from shorter time slices.

#### Worked Mathematical Breakdown
1. **Spectral Main-Lobe Resolution:**  
   The Gabor–Heisenberg uncertainty principle governs time-frequency localization in all linear transforms: temporal localization ($\Delta t$) and frequency resolution ($\Delta f$) are mutually constrained by $\Delta t \cdot \Delta f \ge 1 / (4\pi)$. For a finite window of duration $\Delta t$, the effective frequency bandwidth of the main spectral lobe scales inversely with window duration:
   $$\begin{aligned}
   \text{At } \Delta t &= 25\text{ ms (}L = 400\text{):} \quad \Delta f \approx \frac{1}{0.025\text{ s}} = 40\text{ Hz} \quad (\text{Hamming null-to-null: } \approx 80\text{ Hz}) \\
   \text{At } \Delta t &= 5\text{ ms (}L = 80\text{):} \quad \Delta f \approx \frac{1}{0.005\text{ s}} = 200\text{ Hz} \quad (\text{Hamming null-to-null: } \approx 400\text{ Hz})
   \end{aligned}$$

2. **Formant Smearing and Phonetic Collapse:**  
   In human vowel production, formant frequencies correspond to the acoustic resonant poles of the vocal tract. Adjacent formants—specifically the first two formants ($F_1$ and $F_2$), which distinguish vowel identities—frequently lie within $150\text{--}250\text{ Hz}$ of each other.  
   When the filter main lobe broadens to $\Delta f \approx 200\text{ Hz}$ (with side-lobe nulls spanning $400\text{ Hz}$), the spectral analyzer can no longer resolve two distinct spectral peaks spaced $180\text{ Hz}$ apart. The two distinct formants blur together into a single broad, merged spectral mass. Acoustic distinctions between cardinal vowels collapse—for example, the close front vowel $/i/$ (high $F_2$, low $F_1$) merges indistinguishably with the close back vowel $/u/$ (compact low $F_1, F_2$), destroying the phonetic representations required by downstream acoustic models.

3. **Biomechanical Incompatibility:**  
   The human vocal apparatus is constrained by physical inertia: the tongue, velum, jaw, and pharyngeal muscles cannot physically change state in under $20\text{--}30\text{ ms}$. More critically, $5\text{ ms}$ is significantly shorter than the fundamental pitch period of a typical low adult male voice ($1 / 85\text{ Hz} \approx 11.8\text{ ms}$).  
   A $5\text{ ms}$ window captures only an incomplete fraction of a single glottal cycle. Depending on whether the $5\text{ ms}$ window coincides with the open or closed glottal phase, the extracted spectral energy swings erratically by tens of decibels from frame to frame. This produces severe frame-to-frame variance that renders downstream classification impossible.

> **PHYSICAL INSIGHT**  
> Cutting the window length below $20\text{ ms}$ does not create an ultra-low-latency voice engine; it constructs a low-resolution spectral blur. Temporal latency cannot be reduced past the biomechanical inertia of the human vocal tract without violating the Gabor–Heisenberg bound and fusing critical formant frequencies.

---

### Diagnostic Scenario 3: The Discrete Transform Trap

#### The Naive Hypothesis
A hardware architect inspecting the STFT pipeline notices that after windowing, the audio frame contains exactly $L = 400$ samples. Rather than appending $112$ artificial zeros to reach a power-of-two size ($N = 512$), the architect argues that the FPGA should compute a direct 400-point Discrete Fourier Transform (DFT), avoiding the memory overhead of storing zeros and eliminating what appears to be superfluous computation.

#### Worked Mathematical Breakdown
1. **Direct DFT Arithmetic Complexity:**  
   To produce the single-sided power spectrum for frequencies up to the Nyquist limit, the direct DFT must compute $K = L/2 + 1 = 400/2 + 1 = 201$ independent frequency bins according to the direct transform equation:
   $$X[k] = \sum_{n=0}^{L-1} x[n] e^{-j 2\pi k n / L}, \quad k = 0, 1, \dots, 200$$
   Evaluating each bin requires exactly $L = 400$ complex multiply-accumulate operations. Across all 201 bins, the direct DFT requires:
   $$\text{Workload}_{\text{DFT}} = 201 \times 400 = 80{,}400\text{ complex MACs / frame}$$

2. **Radix-2 Cooley-Tukey FFT Arithmetic Complexity:**  
   By appending $112$ zeros to form a length-$512$ vector ($N = 2^9$), the front-end unlocks the recursive divide-and-conquer radix-2 Cooley-Tukey FFT. The computational workload of a radix-2 Decimation-in-Time FFT is bounded by $(N/2) \log_2 N$ complex butterfly stages:
   $$\text{Workload}_{\text{FFT}} = \frac{512}{2} \log_2(512) = 256 \times 9 = 2{,}304\text{ butterfly operations / frame}$$

3. **Silicon Hardware Cost Comparison:**  
   Comparing the two arithmetic workloads reveals a dramatic computational divergence:
   $$\text{Speedup Ratio} = \frac{80{,}400\text{ complex MACs}}{2{,}304\text{ butterflies}} \approx 34.9\times$$
   On an FPGA, an $\mathcal{O}(L^2)$ direct DFT architecture executing within the $10\text{ ms}$ hop deadline requires either dedicating hundreds of DSP48E2 slices to run in parallel or running a serialized multiplier at high clock rates, exhausting silicon routing channels and dynamic power. Conversely, the radix-2 FFT maps into an elegant, pipelined cascade consuming fewer than a dozen DSP slices and a fraction of on-chip BRAM. The $112$ padded zeros cost exactly **zero arithmetic operations**, inject zero synthetic distortion, and reduce silicon execution cost by $34.9\times$.

> **PHYSICAL INSIGHT**  
> Zero-padding is not arithmetic waste; it is an architectural enabler. Padded zeros cost zero multiply-accumulate operations while unlocking power-of-two recursive symmetry that slashes silicon compute by $34.9\times$.

---

### Diagnostic Scenario 4: The Dense Matrix Bottleneck

#### The Naive Hypothesis
A software-trained engineer maps the Mel filterbank stage onto the FPGA by treating the filterbank weights as a standard dense matrix. The stage multiplies $K = 257$ spectral energy bins by $M = 80$ triangular filter vectors:
$$E_\ell[m] = \sum_{k=0}^{256} g_m[k] P_\ell[k], \quad m = 0, 1, \dots, 79$$
Storing this transformation as a dense FP32 matrix requires $80 \times 257 \times 4\text{ B} = 82{,}240\text{ bytes} = 80.3\text{ KiB}$. On the Kria KV260, this dense structure consumes $82{,}240 / 4{,}608 \approx 18$ physical 36-kbit Block RAM blocks ($12.5\%$ of total on-chip BRAM).

#### Worked Mathematical Breakdown
1. **Filterbank Sparsity Exploitation:**  
   Because each Mel filter $g_m[k]$ is a compact triangle that is non-zero only between bounding frequencies $[k_{m-1}, k_{m+1}]$, adjacent filters overlap by exactly $50\%$. Each spectral frequency bin $k$ is covered by at most two overlapping triangular filters.  
   Consequently, out of the $80 \times 257 = 20{,}560$ matrix elements, only a tiny fraction are non-zero:
   $$\text{Non-Zero Weights} \approx 2 \times 257 \approx 514 \quad (\text{or } 80 \times 6.4 \approx 512\text{ active coefficients})$$
   Over $97.5\%$ of the dense matrix consists of structural zeros.

2. **Compressed Sparse Storage Formulation:**  
   Instead of storing thousands of structural zeros in uncompressed FP32 format, the hardware architect compresses each filter into:
   - Quantized 16-bit integer coefficients (INT16, 2 bytes per non-zero weight).
   - A compact metadata header per filter band storing the start bin index $k_{\text{min}}$ (1 byte) and the active band length $K_m$ (1 byte): $80 \times 2\text{ B} = 160\text{ bytes}$.
   
   The total memory required to store the entire 80-channel filterbank becomes:
   $$\text{Compressed Memory} = (514 \times 2\text{ B}) + (80 \times 2\text{ B}) = 1{,}028\text{ B} + 160\text{ B} = 1{,}188\text{ bytes}$$

3. **Silicon Resource and Bandwidth Impact:**  
   Comparing the dense FP32 matrix against the sparse INT16 representation on the AMD XCK26 MPSoC reveals:
   $$\begin{aligned}
   \text{BRAM Consumption} &= \frac{1{,}188\text{ bytes}}{4{,}608\text{ bytes/BRAM}} \approx 25.8\% \text{ of ONE single Block RAM block} \\
   \text{Memory Reduction Ratio} &= \frac{82{,}240\text{ bytes}}{1{,}188\text{ bytes}} \approx 69.2\times
   \end{aligned}$$
   Sparse compression collapses the Mel filterbank memory footprint from $18$ BRAM blocks down to a tiny quadrant ($25.8\%$) of a single BRAM, immediately liberating $17$ physical BRAM primitives ($68\text{ KiB}$) for neural network acoustic weights. Furthermore, the memory read bandwidth collapses from $20{,}560$ reads down to just $514$ reads per frame—a **$40\times$ reduction in memory access operations**.

> **PHYSICAL INSIGHT**  
> Storing structural zeros in physical memory is architectural suicide. Sparse triangular compression collapses the Mel filterbank footprint by $69.2\times$, compressing 18 Block RAMs into a quarter of a single primitive and slashing memory read bandwidth by $40\times$.

---

### Summary: The Four-Knob Silicon and Acoustic Damage Board

The four diagnostic failure modes demonstrate that the standard parameters of the streaming voice pipeline ($f_s = 16\text{ kHz}, L = 400, N = 512, \text{sparse Mel}$) are not arbitrary conventions; they are the exact Pareto-optimal intersection between the physics of human speech and the microarchitectural constraints of edge silicon.

| Parameter Knob | Naive Modification | Physical Failure Mode | Silicon Hardware Consequence |
| :--- | :--- | :--- | :--- |
| **Sampling Rate ($f_s$)** | $16\text{ kHz} \to 48\text{ kHz}$ | Nyquist bandwidth expands to $24\text{ kHz}$; captures ultrasonic hiss with zero speech benefit | Buffer expands to $4{,}800\text{ B} > 4{,}608\text{ B}$; overflows into **2 BRAMs**; quadruples FFT compute |
| **Window Duration ($L$)** | $25\text{ ms} \to 5\text{ ms}$ | Gabor uncertainty broadens main lobe to $\Delta f \approx 200\text{ Hz}$; formants $F_1/F_2$ blur | Destroys phonetic separability (/i/ vs /u/); glottal phase instability |
| **Transform Size ($N$)** | $N = 400\text{ direct DFT}$ | Omits zero-padding; forces direct $\mathcal{O}(L^2)$ matrix evaluation | Direct DFT requires **$80{,}400$ complex MACs** ($34.9\times$ worse than $2{,}304$ FFT butterflies) |
| **Mel Filter Storage** | Dense FP32 matrix | Stores $97.5\%$ structural zeros; squanders on-chip SRAM | Consumes **18 Block RAMs** ($12.5\%$ total chip SRAM) and requires $20{,}560$ memory reads/frame |

---

### Organic Bridge to Section 1.6: From Recognition to Evaluation

With the front-end parameters rigorously stress-tested and defended, our DSP pipeline reliably transforms continuous air pressure into an 80-channel Log-Mel spectrogram vector emitted every $10\text{ ms}$. In a conventional edge voice system, these vectors stream directly into an Automatic Speech Recognition (ASR) acoustic model trained to decode text.

However, when moving from speech *recognition* to pronunciation *evaluation*—such as assessing language learners or children reading aloud—standard ASR architectures collapse. Driven by language model priors, an ASR engine actively hallucinates: it autocorrects mispronunciations into the words it expects to hear, masking student errors.

To evaluate pronunciation fidelity without hallucination, the system must abandon probabilistic language decoding and directly evaluate physical acoustic trajectories. In Section 1.6, we explore pitch tracking ($F_0$), Pearson correlation, and Dynamic Time Warping (DTW) to measure pronunciation distance on physical FPGA hardware.
