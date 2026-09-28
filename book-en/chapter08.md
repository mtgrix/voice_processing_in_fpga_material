# Audio Correlation Algorithms for Reading Assessment

> "To evaluate how well a student reads, we do not need to transcribe every phoneme into text—a task prone to hallucination in noisy classrooms. We need only to measure the distance between the student's acoustic trajectory and the expected phonetic path. The challenge is not transcription; the challenge is elastic alignment."

---

### Minimal Mathematics / Prerequisites for this Chapter

Before we dive into the algorithms, recall the mathematical foundations we rely on for comparing sequences. If these concepts are fresh, you can safely skip this sidebar.

- **Dynamic Programming (DP) Recurrence**: A method for solving complex problems by breaking them down into simpler subproblems. For sequence alignment, it takes the form $D(i,j) = c(i,j) + \min(D(i-1,j), D(i,j-1), D(i-1,j-1))$, where $c$ is the local cost and $D$ is the cumulative cost.
- **Cross-Correlation**: A measure of similarity between two waveforms as a function of a time-lag applied to one of them. For discrete signals, it is a sliding dot product.
- **Log-Probability**: Instead of multiplying small probability values (which underflow hardware floating-point representations), we sum their logarithms: $\log(A \times B) = \log(A) + \log(B)$. This transforms multiplicative probability chains into additive scores.

---

In our six-stage pipeline (Air and microphone $\rightarrow$ Sample stream $\rightarrow$ DSP front end $\rightarrow$ Model $\rightarrow$ Fabric logic $\rightarrow$ Output and latency), this chapter sits exactly at the transition from the DSP front end to the Model, and ultimately dictates the Output and latency. The Mel-Frequency Cepstral Coefficients (MFCC — acoustic feature vectors representing the power spectrum) have been extracted. Now, we must evaluate them. 

This chapter is the theoretical core of the thesis: we define the mathematical algorithms used to correlate a student's spoken audio with a reference. By understanding the physical intuition, the mathematical mechanisms, and the computational costs, we lay the groundwork for why specific algorithms demand spatial hardware acceleration on a Field-Programmable Gate Array (FPGA — reconfigurable silicon integrated circuit).

### Contribution Statement

To our knowledge, no prior work has combined a banded DTW systolic-array accelerator with a real-time pronunciation assessment pipeline on an edge FPGA SoC, under a controlled power-matched comparison against an edge GPU (NVIDIA Jetson Orin). This thesis makes three contributions:

1. **A DTW systolic-array engine** mapped to the Kria KV260 FPGA fabric, achieving $O(N + M)$ cycle latency with $W$ processing elements under Sakoe-Chiba banding — a direct hardware realization of the diagonal wavefront parallelism inherent in the DP recurrence.
2. **A formal fixed-point error analysis** proving that INT16 features with a 32-bit accumulator preserve pronunciation correlation scores (PCC degradation $< 0.02$) for utterances up to 2,000 frames, and identifying the bit-width at which degradation becomes unacceptable.
3. **A controlled GPU-versus-FPGA evaluation** measuring frame latency, energy per evaluation, and correlation accuracy under matched power envelopes — demonstrating that the FPGA's deterministic, scheduling-free pipeline achieves lower energy per evaluation despite the GPU's higher peak throughput.

### Algorithm Landscape at a Glance

The table below summarizes the five algorithms surveyed in this chapter. The rest of the chapter develops each row in depth.

| Algorithm | Time Complexity | Space | Parallelism | Model Needed? | Assessment Level | FPGA Fit |
|-----------|----------------|-------|-------------|---------------|-----------------|----------|
| Euclidean / Cosine Distance | $O(D)$ per pair | $O(D)$ | Trivial (single vector op) | No | Frame | Low (too simple to justify custom HW) |
| **DTW** (Sakoe-Chiba) | $O(N \times W)$ | $O(N \times W)$ | **Diagonal wavefront** — $W$ cells per cycle | No | Segment / Utterance | **High** — systolic array |
| Subsequence DTW | $O(N \times M)$ | $O(N \times M)$ | Same as DTW | No | Sub-utterance | High |
| **GOP** | $O(T \times C)$ per phoneme | $O(C)$ | DNN inference (matrix multiply) | Yes (acoustic DNN) | Phoneme | Medium — DPU overlay |
| Cosine on Embeddings | $O(D_{\text{emb}})$ per pair | $O(D_{\text{emb}})$ | Single dot product | Yes (large encoder) | Utterance | Low (encoder dominates) |

Where $N, M$ = sequence lengths in frames, $W$ = Sakoe-Chiba band width, $D$ = MFCC dimension (80), $T$ = total frames, $C$ = phoneme count, $D_{\text{emb}}$ = embedding dimension.

## 8.1 Intuition: What Does "Audio Correlation" Mean?

When assessing reading or pronunciation, the fundamental task is comparison. We have a reference recording (or a synthetic baseline) of a sentence, and we have the student's attempt. 

### The Rubber Band Dilemma: Why Naive Comparison Fails

Consider an expert teacher reciting the phrase:
$$\text{Teacher Reference: } \text{"Good morning"} \quad (1.0 \text{ s}, N = 100 \text{ frames})$$
Now, consider a young student attempting to read the exact same phrase:
$$\text{Student Attempt: } \text{"Gooood... mor...ning"} \quad (1.8 \text{ s}, M = 180 \text{ frames})$$

Phonetically and semantically, the student has articulated the sentence correctly. However, if we pass these two audio waveforms to standard signal processing or machine learning distance metrics, the result is complete failure:

1. **Waveform Subtraction ($x(t) - y(t)$):** Because human speech fluctuates at millisecond resolution, subtracting two raw waveforms of different lengths produces pure, uncorrelated acoustic noise.
2. **Linear Cross-Correlation / Dot Product ($x * y$):** Cross-correlation can only slide one audio stream rigidly across another (a uniform time-lag $\tau$). It cannot stretch one word while compressing another. When the student prolongs "Good" while rushing through "morning", linear correlation collapses.

Reading assessment is **not** the rigid overlay of two iron rulers. It is the elastic alignment of two **rubber bands**. We must compress segments where the student hesitates and stretch segments where the student rushes—aligning identical phonetic moments before computing spectral discrepancies.

This differs fundamentally from Automatic Speech Recognition (ASR — converting speech into text). In ASR, the model must guess the spoken words from an infinite vocabulary. In reading assessment, the text is known. We are not transcribing; we are verifying. We are measuring elastic correlation.

We measure this correlation at three distinct levels:
1. **Frame-level**: Comparing the instantaneous spectral distance between two 20-millisecond windows of audio.
2. **Segment-level**: Aligning sequences of frames elastically to handle differences in speaking rate.
3. **Utterance-level**: Comparing compressed mathematical representations of the entire spoken phrase.

The microarchitectural mechanism required to support these comparisons dictates our hardware design. A frame-level distance is a simple vector operation. A segment-level alignment is a complex grid traversal. An utterance-level comparison is a matrix multiplication. We must choose our algorithms based not only on pedagogical accuracy but on computational viability.

## 8.2 Cross-Correlation and Spectral Distance Metrics

Before we can align two sequences, we need a metric to compare individual frames. Each audio frame has been processed by our DSP front end into a feature vector, typically an 80-dimensional MFCC vector. 

### Euclidean Distance

The most intuitive metric for comparing two vectors is the Euclidean distance. It measures the straight-line distance between two points in the feature space.

**Equation Card 1: Euclidean Distance**
- **The formula**: 
  $$d(\mathbf{x}_i, \mathbf{y}_j) = \sqrt{\sum_{k=1}^{D} (x_{i,k} - y_{j,k})^2}$$
- **The variables**: $\mathbf{x}_i$ is the $i$-th frame of the student's audio. $\mathbf{y}_j$ is the $j$-th frame of the reference audio. $D$ is the dimensionality of the feature vector (e.g., 80). $x_{i,k}$ is the $k$-th feature coefficient.
- **What it means**: It calculates the physical magnitude of the difference between the spectral envelopes of the two frames. A smaller distance implies higher acoustic similarity.
- **What it costs**: $O(D)$ operations per frame pair. It requires $D$ subtractions, $D$ multiplications (squaring), $D-1$ additions, and one square root. The square root is notoriously expensive in hardware, often requiring iterative algorithms or lookup tables.
- **What it does not say**: It does not account for overall volume differences. If the student speaks louder than the reference, the Euclidean distance will be large even if the phonetic content is identical.

### Cosine Distance

To decouple phonetic similarity from absolute volume, we often turn to cosine distance. 

**Equation Card 2: Cosine Distance**
- **The formula**:
  $$d_{\cos}(\mathbf{x}_i, \mathbf{y}_j) = 1 - \frac{\mathbf{x}_i \cdot \mathbf{y}_j}{\|\mathbf{x}_i\| \|\mathbf{y}_j\|}$$
- **The variables**: $\mathbf{x}_i$ and $\mathbf{y}_j$ are the feature vectors. $\cdot$ denotes the dot product. $\|\mathbf{x}_i\|$ is the L2 norm (magnitude) of the vector.
- **What it means**: It measures the angle between the two vectors in the $D$-dimensional space. It is completely invariant to the magnitude of the vectors, meaning it is robust to volume differences.
- **What it costs**: $O(D)$ operations. It requires a dot product ($D$ multiply-accumulates), two vector norms (each requiring $D$ multiply-accumulates and a square root), and a division. Division and square roots are both high-latency operations in silicon.
- **What it does not say**: It ignores magnitude completely, which can be problematic if silence (low magnitude noise) is compared to speech; the angle might arbitrarily align, yielding a false high similarity.

### Hardware Trade-off & Reality

These distance metrics are the microscopic building blocks of our evaluation system. We do not compute them just once; we compute them millions of times as part of the inner loop of our alignment algorithms. The computational profile is $O(N \cdot D)$ per frame pair, where $N$ is the sequence length.

In hardware, we actively avoid the square root in the Euclidean distance by simply using the Squared Euclidean distance ($d^2$). Since distance is used strictly for relative comparison during alignment, the monotonic nature of the square function means the optimal alignment path is identical whether we use $d$ or $d^2$. This microarchitectural optimization saves tremendous silicon area and reduces pipeline latency.

## 8.3 Dynamic Time Warping (DTW) — The Core Algorithm

We arrive at the centerpiece of our correlation algorithms. Measuring the distance between individual frames is insufficient; we must measure the distance between entire spoken sequences that are almost certainly different lengths. 

The physical friction is the elasticity of human speech. A student reading "The quick brown fox" might elongate the word "brown." If we rigidly compare frame 50 of the student with frame 50 of the reference, we might be comparing the student's "br-" with the reference's "-ox." 

Dynamic Time Warping (DTW — an elastic sequence alignment algorithm) solves this. The microarchitectural mechanism is dynamic programming: we construct a grid where the x-axis represents the reference sequence frames and the y-axis represents the student sequence frames. We then find the optimal contiguous path through this grid that minimizes the cumulative distance.

### The DTW Recurrence

**Equation Card 3: Dynamic Time Warping DP Recurrence**
- **The formula**:
  $$D(i,j) = d(\mathbf{x}_i, \mathbf{y}_j) + \min\{D(i-1,j),\; D(i-1,j-1),\; D(i,j-1)\}$$
- **The variables**: $D(i,j)$ is the cumulative minimum cost to align the student sequence up to frame $i$ with the reference sequence up to frame $j$. $d(\mathbf{x}_i, \mathbf{y}_j)$ is the local spectral distance between the student's frame $i$ and the reference's frame $j$ (typically the squared Euclidean distance on 80-dimensional MFCC vectors). $N$ is the length of the student sequence. $M$ is the length of the reference sequence.
- **What it means**: To find the cheapest path to coordinate $(i,j)$, we take the local cost at $(i,j)$ and add the minimum cumulative cost from the three valid preceding steps: an insertion (moving vertically from $(i-1, j)$ — the student repeats a phoneme), a deletion (moving horizontally from $(i, j-1)$ — the student skips a reference phoneme), or a match (moving diagonally from $(i-1, j-1)$ — both sequences advance together).
- **What it costs**: The complexity is $O(N \times M)$ in both time and space, where $N$ and $M$ are the lengths of the two sequences. For a 5-second student utterance ($N = 500$ frames at 100 frames/s) against a 4-second reference ($M = 400$ frames), the grid contains 200,000 cells. Each cell requires one distance computation ($D$ multiply-accumulates) and one three-way minimum. On a single CPU core at 1 GHz, this takes roughly 2 ms; on a systolic array with $W = 64$ processing elements at 200 MHz, the same grid finishes in under 10 microseconds.
- **What it does not say**: The basic formula does not restrict pathological alignments. Without constraints, a single reference frame can map to 100 student frames, producing a physically implausible warping. The constraint bands described below fix this. The formula also says nothing about the *quality* of the alignment in phonetic terms — it minimizes acoustic distance, which is not the same as phonetic correctness.

### Boundary Conditions

The grid requires careful initialization. We set the starting cell to the local distance at the origin:

$$D(1,1) = d(\mathbf{x}_1, \mathbf{y}_1)$$

All cells outside the valid region are initialized to positive infinity, forcing the warping path to begin at $(1,1)$ and end at $(N,M)$:

$$D(i,0) = \infty \quad \text{for all } i > 0$$
$$D(0,j) = \infty \quad \text{for all } j > 0$$

This endpoint constraint is essential: the alignment must account for the entirety of both sequences. A partial alignment (stopping early in either sequence) would misrepresent the student's reading of the full passage.

### Worked Example: Walking Through the Grid

To make the mechanism concrete, consider two short sequences: a student utterance of $N = 4$ frames and a reference of $M = 5$ frames. We precompute the local distance matrix $d(i,j)$ between every student-reference frame pair (using squared Euclidean distance on their MFCC vectors):

|  | $j=1$ | $j=2$ | $j=3$ | $j=4$ | $j=5$ |
|--|-------|-------|-------|-------|-------|
| $i=1$ | 2 | 4 | 7 | 6 | 3 |
| $i=2$ | 5 | 3 | 2 | 5 | 4 |
| $i=3$ | 8 | 6 | 1 | 3 | 6 |
| $i=4$ | 9 | 7 | 4 | 2 | 1 |

We now fill the cumulative cost matrix $D(i,j)$ row by row. The first cell is simply $D(1,1) = 2$. Moving along the first row, each cell can only come from its left neighbor (since there is no row above): $D(1,2) = 4 + D(1,1) = 6$, $D(1,3) = 7 + 6 = 13$, and so on. Moving along the first column, each cell comes from above: $D(2,1) = 5 + 2 = 7$, $D(3,1) = 8 + 7 = 15$, $D(4,1) = 9 + 15 = 24$.

The interior cells apply the full recurrence. For example, $D(2,2) = 3 + \min(D(1,2), D(1,1), D(2,1)) = 3 + \min(6, 2, 7) = 3 + 2 = 5$. The minimum came from the diagonal neighbor, meaning both sequences advanced together — a natural alignment.

Completing the entire grid:

|  | $j=1$ | $j=2$ | $j=3$ | $j=4$ | $j=5$ |
|--|-------|-------|-------|-------|-------|
| $i=1$ | **2** | 6 | 13 | 19 | 22 |
| $i=2$ | 7 | **5** | **7** | 12 | 16 |
| $i=3$ | 15 | 11 | 6 | **9** | 15 |
| $i=4$ | 24 | 18 | 10 | 8 | **9** |

The final DTW distance is $D(4,5) = 9$. The optimal warping path, traced back from $(4,5)$ by always stepping to the neighbor with the smallest cumulative cost, is: $(1,1) \to (2,2) \to (2,3) \to (3,4) \to (4,5)$. Notice that frame $i=2$ aligned to both $j=2$ and $j=3$ — the student held that phoneme longer than the reference, and DTW correctly accommodated the stretch.

### The Traceback Procedure

The warping path is recovered by a reverse pass through the grid. At each cell $(i,j)$, we stored a direction flag indicating which of the three predecessors contributed the minimum: diagonal (match), left (deletion), or below (insertion). This direction matrix costs 2 bits per cell ($\lceil \log_2 3 \rceil = 2$).

Starting at $(N,M)$, we follow the direction flags back to $(1,1)$. The path has at most $N + M - 1$ steps, so traceback is $O(N + M)$ — negligible compared to the $O(N \times M)$ grid fill. On hardware, the direction matrix is stored in Block RAM during the forward pass. The traceback itself runs on the ARM CPU because it is a lightweight sequential walk with irregular memory access patterns — exactly the kind of workload a CPU handles well and an FPGA pipeline would waste on.

### Normalized DTW Distance

Raw DTW distance $D(N,M)$ grows with sequence length: longer utterances accumulate more distance simply because they traverse more cells. To compare scores across utterance pairs of different durations, we normalize:

**Equation Card 4: Normalized DTW Distance**
- **The formula**:
  $$\text{DTW}_{\text{norm}} = \frac{D(N, M)}{N + M}$$
- **The variables**: $D(N,M)$ is the raw cumulative cost at the grid endpoint. $N$ is the student sequence length in frames. $M$ is the reference sequence length in frames.
- **What it means**: It divides the total alignment cost by the length of the warping path (which is bounded between $\max(N,M)$ and $N + M - 1$). Using $N + M$ as the denominator is a common convention that makes scores comparable: a $\text{DTW}_{\text{norm}}$ of 0.5 means the average per-step cost was 0.5 distance units, regardless of whether the utterance was two seconds or 20.
- **What it costs**: One integer addition and one division. On FPGA fabric, division is expensive (iterative or LUT-based), but it is computed only once per utterance pair — at the very end of the pipeline — so its latency is amortized.
- **What it does not say**: Normalization by $N + M$ slightly penalizes paths that deviate far from the diagonal (because they traverse more steps). Alternative normalizations exist ($\sqrt{N \cdot M}$, path length), each with different biases. The choice does not affect the alignment itself, only the final score.

### Constraint Bands: Taming the Quadratic

An unconstrained $O(N \times M)$ search space is computationally wasteful for real speech. Physically, a student's speaking rate will not deviate infinitely from the reference. We exploit this regularity by restricting the warping path to a band around the diagonal.

**Sakoe-Chiba Band.** We enforce $|i \cdot M/N - j| \leq W$, where $W$ is the maximum allowed deviation in frames. In practice, for sequences where $N \approx M$, this simplifies to $|i - j| \leq W$. The parameter $W$ is set based on the expected speaking rate variation — for reading assessment, $W = 50$ frames (500 ms at 100 frames/s) is typical.

The effect on complexity is dramatic:

$$\text{Cells evaluated} = N \times (2W + 1) \quad \text{instead of} \quad N \times M$$

For $N = M = 500$ and $W = 50$: unconstrained DTW evaluates 250,000 cells; Sakoe-Chiba evaluates $500 \times 101 = 50,500$ cells — a $4.95\times$ reduction. For the FPGA systolic array, this is even more consequential: we need only $W$ processing elements instead of $M$, dramatically reducing silicon area.

**Itakura Parallelogram.** A more aggressive constraint that bounds the instantaneous slope of the warping path between $1/s$ and $s$ (typically $s = 2$). This creates a parallelogram-shaped valid region and prevents the path from advancing too quickly or too slowly in either sequence. While theoretically tighter, it is harder to implement in hardware due to the slope-dependent boundary, and Sakoe-Chiba is the standard choice for FPGA implementations.

### Diagonal Wavefront Parallelism: Why DTW Belongs on an FPGA

This subsection is the bridge between algorithm and architecture — the reason this chapter exists in a hardware book.

Examine the data dependencies in the recurrence relation: cell $(i,j)$ depends on exactly three cells — $(i-1,j)$, $(i-1,j-1)$, and $(i,j-1)$. Now consider the anti-diagonal of the grid: all cells $(i,j)$ where $i + j = k$ for a fixed $k$. None of these cells depend on each other. They are completely independent.

This is diagonal wavefront parallelism. On a CPU, we process the grid row by row, cell by cell — $N \times M$ sequential steps. On an FPGA with $P$ processing elements arranged as a linear systolic array, we process one anti-diagonal per clock cycle. The number of anti-diagonals is $N + M - 1$, so the total latency is:

$$T_{\text{systolic}} = N + M - 1 \quad \text{clock cycles}$$

Compare this to the sequential CPU:

$$T_{\text{CPU}} = N \times M \quad \text{iterations}$$

For $N = M = 500$: the CPU takes 250,000 iterations; the systolic array takes 999 cycles. At 200 MHz, the systolic array completes in $999 / 200 \times 10^6 = 5.0\;\mu\text{s}$. A CPU core at 3 GHz running the same algorithm takes roughly $250{,}000 / 3 \times 10^9 \approx 83\;\mu\text{s}$ (assuming one iteration per cycle, which is optimistic). The FPGA is $16.7\times$ faster at $1/15$ the clock frequency.

With Sakoe-Chiba banding ($W = 50$), the systolic array needs only $W = 50$ processing elements. Each PE contains one subtractor, one multiplier (for squared distance), one three-input minimum comparator, and three registers for the neighbor values. On the Kria KV260:

| Resource | Per PE | $\times 50$ PEs | Available on KV260 | Utilization |
|----------|--------|------------------|--------------------|-------------|
| LUTs | ~120 | ~6,000 | 117,120 | 5.1% |
| DSP48E2 | 1 | 50 | 1,248 | 4.0% |
| BRAM (for feature row) | 0.5 | 25 | 144 | 17.4% |

The DTW engine consumes a small fraction of the FPGA fabric, leaving ample room for the MFCC preprocessing pipeline (Chapter 6), the GOP acoustic model (DPU), and the control logic. This is why DTW is our primary hardware target: it is computationally demanding enough to justify custom hardware, yet architecturally simple enough to fit comfortably beside the rest of the system.

We maintain a software baseline using the `dtw-python` library. All custom hardware implementations in Chapter 9 will be mathematically verified against this baseline to ensure bit-accurate execution within the tolerance defined by the chosen fixed-point representation.

## 8.4 Goodness of Pronunciation (GOP) Scoring

While DTW provides a robust overall similarity score and aligns the audio, it does not easily pinpoint specific phonetic errors. A student might score well overall but consistently mispronounce the "th" sound. For granular assessment, we turn to Goodness of Pronunciation (GOP).

The physical intuition here relies on forced alignment. We know what the student is supposed to say. We use a hidden Markov model or Viterbi decoding to forcefully align the known text to the student's audio, determining exactly where each phoneme starts and ends. 

Once the boundaries are known, we calculate how confident our acoustic model is that the audio within those boundaries actually represents the expected phoneme.

### The GOP Mathematical Mechanism

**Equation Card 4: Goodness of Pronunciation (GOP)**
- **The formula**:
  $$\text{GOP}(p) = \frac{1}{d_p} \sum_{t=t_s}^{t_e} \log P(p \mid \mathbf{o}_t)$$
- **The variables**: $p$ is the expected phoneme. $t_s$ and $t_e$ are the start and end frames of that phoneme (found via forced alignment). $d_p = t_e - t_s + 1$ is the duration in frames. $\mathbf{o}_t$ is the acoustic observation (MFCC vector) at frame $t$. $P(p \mid \mathbf{o}_t)$ is the posterior probability of phoneme $p$ given the observation.
- **What it means**: It calculates the average log-probability that the spoken acoustic frames match the expected phoneme. A higher GOP score (closer to 0, since log-probabilities are negative) indicates better pronunciation.
- **What it costs**: It requires a forward pass of a Deep Neural Network (DNN) or Time Delay Neural Network (TDNN) for every acoustic frame to generate the probabilities, followed by the arithmetic mean.
- **What it does not say**: It does not penalize speaking rate directly; it only evaluates the acoustic quality of the frames assigned to the phoneme.

The log-posterior is derived from the acoustic model using Bayes' theorem: $\log P(p \mid \mathbf{o}_t) = \log P(\mathbf{o}_t \mid p) + \log P(p) - \log P(\mathbf{o}_t)$. 

### Hardware Partitioning

GOP introduces a distinctly different computational load than DTW. It relies heavily on a pre-trained acoustic model (the DNN). In our system, the hardware partitioning is clear: the DNN inference (matrix multiplications to generate posteriors) runs on the FPGA fabric utilizing the Deep Learning Processor Unit (DPU) blocks discussed in earlier chapters. The Viterbi forced alignment and the final log-scoring math run on the ARM CPU cores. 

GOP is complementary to DTW. DTW assesses fluency, rhythm, and overall trajectory without needing a trained phoneme model. GOP requires a trained model but provides the pinpoint diagnostic feedback necessary for reading assessment.

## 8.5 Cosine Similarity on Neural Embeddings

For completeness, we must mention the modern deep learning alternative to frame-by-frame alignment. The intuition is to bypass sequence alignment entirely. Instead of comparing sequences frame-by-frame, we use a large neural encoder to compress the entire variable-length utterance into a single fixed-length summary vector (an embedding).

Once both the reference and the student audio are converted into embeddings, we compare them using a single mathematical operation.

**Equation Card 5: Embedding Cosine Similarity**
- **The formula**:
  $$S(\mathbf{E}_{ref}, \mathbf{E}_{stu}) = \frac{\mathbf{E}_{ref} \cdot \mathbf{E}_{stu}}{\|\mathbf{E}_{ref}\| \|\mathbf{E}_{stu}\|}$$
- **The variables**: $\mathbf{E}_{ref}$ and $\mathbf{E}_{stu}$ are the fixed-length neural embeddings for the reference and student utterances.
- **What it means**: It measures the angle between the two summary representations in a high-dimensional latent space.
- **What it costs**: An initial heavy cost of running a massive transformer or RNN encoder model. However, the similarity comparison itself is merely $O(D_{embed})$, a single fast dot product.
- **What it does not say**: It obscures temporal details. If a student mispronounces a single word in a long sentence, the embedding might smear that error across the entire vector, making it hard to localize.

This approach excels at capturing high-level features like prosody and intonation. However, the trade-off is steep: it requires a massively parameterized, highly trained neural network. While inference is relatively cheap once the embedding is generated, the generation itself dominates the pipeline.

## 8.6 Selecting the Algorithm for Hardware Implementation

We have surveyed the mathematical landscape. To design our custom silicon architecture, we must select our primary algorithmic target. We evaluate DTW, GOP, and Neural Embeddings across four axes:

1. **Computational Intensity**: DTW exhibits strict $O(N \times M)$ quadratic growth. For a 5-second sentence, evaluating the unconstrained grid requires over 62,000 distance calculations. It is a severe CPU bottleneck. 
2. **FPGA Suitability**: DTW's diagonal wavefront data dependency makes it a perfect candidate for spatial hardware. We can map the algorithm directly to a custom systolic array. GOP's DNN components are suited for generalized neural accelerators (DPUs), not bespoke RTL. 
3. **Assessment Granularity**: GOP provides phoneme-level resolution. DTW provides utterance and word-level temporal resolution. 
4. **Model Dependency**: DTW requires zero trained parameters. It is a pure algorithmic calculation on the raw signal geometry. GOP and Embeddings rely on models that must be trained, updated, and quantized.

### Recommendation: DTW as the Primary Target

We select **Dynamic Time Warping** as the primary target for custom hardware acceleration. 

The rationale is clear: the $O(N \times M)$ complexity makes it the primary latency bottleneck in the evaluation pipeline. The DP grid maps naturally and beautifully to spatial hardware, promising order-of-magnitude speedups over CPU execution. Furthermore, it operates independently of complex acoustic models, making the hardware block highly reusable. 

GOP will be retained in the software stack, utilizing the existing DPU infrastructure for its neural network passes. Neural embeddings are discarded for this system due to their inability to provide precise temporal localization of errors.

In Chapter 9, we will translate the DTW recurrence equation into hardware, designing the processing elements and the systolic array architecture required to execute this algorithm at the speed of silicon.

## 8.7 DTW Variants for Robust Reading Assessment

Our pipeline depends on a robust transition from the DSP front end to the model. Standard DTW is brittle in the wild. A student pausing to sound out a word, coughing, or speaking at varying volumes breaks the global alignment constraint. To address this, we implement three variants of DTW in our fabric logic, each resolving a specific physical friction in real-world audio.

### Subsequence DTW (Open-Begin / Open-End)

In a classroom, students rarely read a passage perfectly from start to finish. They may pause, stutter, or read only part of a sentence. Global DTW forces a complete alignment of the entire student sequence to the reference. When the student stops mid-sentence, the algorithm forcibly stretches the remaining reference audio over silence or background noise, destroying the score.

To allow an alignment to begin anywhere in the reference sequence, we modify the initialization of our dynamic programming grid. Instead of initializing the first column to infinity, we initialize it to zero. This open-begin condition allows a match to start at any reference frame without penalty. Symmetrically, for an open-end condition, we search the last row for the minimum distance rather than rigidly taking the endpoint cell.

**Equation Card 7: Subsequence DTW Boundary Conditions**
- **The formula:**
  $$D(i, 0) = 0 \quad \text{for all } i \in [1, N]$$
  $$S_{\text{match}} = \min_{i} D(i, M)$$
- **The variables:** $D(i, j)$ is the accumulated distance at reference frame $i$ and student frame $j$. $N$ is the length of the reference sequence. $M$ is the length of the student sequence. $S_{\text{match}}$ is the final subsequence match score.
- **What it means:** The first equation removes the penalty for skipping the beginning of the reference. The second equation finds the best exit point, allowing the student to stop early without penalty.
- **What it costs:** Almost nothing. It replaces an infinity initialization with a zero initialization and requires a running minimum comparator across the final row — one comparator and one register at the array output.
- **What it does not say:** It does not prevent spurious short matches. A very short, poor utterance might match a tiny segment of the reference well. Length normalization is still required.

In our systolic array, the boundary Processing Elements simply change their reset state from a saturated maximum to zero. The area overhead is negligible.

### Derivative DTW (DDTW)

Standard DTW computed directly on MFCC values is highly sensitive to baseline amplitude shifts. If a student speaks louder or quieter than the reference, the Euclidean distance between their frames inflates, even if the phonetic content matches perfectly. We need to match the *shape* of the spectral trajectory, not its absolute offset.

Rather than aligning the raw features, we align their first-order derivatives. This eliminates static offsets. We replace the input feature sequence with a smoothed local derivative calculated over a moving window of three frames.

**Equation Card 8: Derivative Feature Estimation**
- **The formula:**
  $$\hat{x}_i = \frac{(x_i - x_{i-1}) + (x_{i+1} - x_{i-1})/2}{2}$$
- **The variables:** $\hat{x}_i$ is the derivative feature vector at frame $i$. $x_i$ is the original MFCC feature vector at frame $i$.
- **What it means:** This is a smoothed approximation of the local slope, combining the immediate backward difference and the wider backward difference. It captures the trajectory of the speech features, inherently rejecting constant offsets.
- **What it costs:** Two subtractions and a bit-shift (division by two) per feature dimension, per frame. Approximately 20 LUTs per PE.
- **What it does not say:** Derivative features amplify high-frequency noise. If the signal-to-noise ratio (SNR) is poor, DDTW can perform worse than standard DTW. A low-pass pre-filter may be needed.

We insert an additional pipeline stage between the feature buffer and the distance computation unit. This stage holds a sliding window of three frames and computes the derivative on the fly. It is a classic compute-for-robustness trade-off, easily absorbed by the fabric logic.

### Weighted DTW

In human speech, not all frames are equally informative. A long, drawn-out vowel contains redundant information, while a brief, sharp consonant onset is critical for intelligibility. Furthermore, silence frames should not dominate the alignment score. Standard DTW treats every frame pair as an equal contributor.

We introduce a local weighting factor to the distance computation. Before adding the local distance to the accumulated path cost, we scale it by a weight $w(i,j)$ derived from the local energy or a phoneme-importance map:

$$D(i,j) = w(i,j) \cdot d(x_i, y_j) + \min(D(i-1,j),\; D(i,j-1),\; D(i-1,j-1))$$

This requires one additional multiplier per PE in the systolic array. While this increases the DSP48E2 utilization, it provides the algorithmic flexibility to penalize silence and reward phonetically rich segments, yielding a dramatic improvement in correlation with human expert raters.

---

## 8.8 Quantization Error Analysis for Fixed-Point DTW

When we map the correlation engine into fabric logic, floating-point arithmetic becomes a luxury we cannot afford. We must quantize the DTW computation from 64-bit floating-point (FP64) down to 16-bit or 8-bit integers. Quantization introduces two distinct failure modes: catastrophic overflow in the accumulator and creeping noise in the distance metric. Both must be formally bounded before we commit a design to silicon.

### Accumulator Overflow Analysis

Unlike matrix multiplication where values fluctuate, the DTW accumulator grows monotonically. Every step along the warping path adds a positive distance. If the accumulator overflows, the alignment score wraps around, rendering the result meaningless.

For a sequence pair of lengths $N$ and $M$, the maximum warping path length is $L \leq N + M - 1$. If the maximum possible local distance between any two frames is $d_{\max}$, the maximum accumulated value is $L \cdot d_{\max}$. The minimum required bit-width for the accumulator is:

**Equation Card 9: DTW Accumulator Bit-Width**
- **The formula:**
  $$B_{\text{acc}} = \lceil \log_2(L \cdot d_{\max}) \rceil + 1$$
- **The variables:** $B_{\text{acc}}$ is the minimum accumulator bit-width. $L = N + M - 1$ is the maximum warping path length. $d_{\max}$ is the maximum local distance between any two quantized feature vectors. The $+1$ accounts for the sign bit.
- **What it means:** The accumulator must be wide enough to hold the worst-case sum of $L$ maximum-distance steps without overflow.
- **What it costs:** Each additional bit in the accumulator costs routing and flip-flop resources across every PE. A 48-bit accumulator on a Kria KV260 uses roughly twice the registers of a 24-bit one.
- **What it does not say:** This is a worst-case bound. Real utterances never traverse all-maximum-distance cells. But hardware must guarantee correctness, not hope for it.

**Worked example.** Suppose $N = M = 500$, feature dimension $D = 80$, and MFCC features quantized to INT16. The maximum single-feature difference is $2^{15}$. The squared Euclidean distance can reach $d_{\max} = 80 \times (2^{15})^2 \approx 8.59 \times 10^{10}$. The maximum path length is $999$. The maximum accumulation is $999 \times 8.59 \times 10^{10} \approx 8.58 \times 10^{13}$. We find $B_{\text{acc}} = \lceil \log_2(8.58 \times 10^{13}) \rceil + 1 = 47 + 1 = 48$ bits. A standard 32-bit accumulator would catastrophically fail. We must either scale the features down or use a 48-bit accumulator.

In practice, we scale INT16 features by a factor of $2^{-4}$ (shift right by four bits, yielding effective INT12 range), which reduces $d_{\max}$ by $2^8$ and brings the accumulator requirement down to 40 bits — comfortably handled by the DSP48E2 slice's 48-bit internal accumulator.

### Quantization Noise in the Distance Metric

When we quantize FP32 features to INT$Q$ integers with a scaling factor $s$, each quantized feature has an error bounded by $|\epsilon| \leq s/2$. The squaring operation in the Euclidean distance magnifies these errors, and the monotonic accumulation ensures they compound along the path.

**Equation Card 10: DTW Quantization Error Bound**
- **The formula:**
  $$|\Delta D(N,M)| \leq L \cdot \left( 2D \cdot s \cdot \|\mathbf{x} - \mathbf{y}\|_\infty + D \cdot s^2 \right)$$
- **The variables:** $|\Delta D(N,M)|$ is the total accumulated error in the final DTW score. $L$ is the warping path length. $D$ is the feature dimension (80). $s$ is the quantization step size. $\|\mathbf{x} - \mathbf{y}\|_\infty$ is the maximum absolute difference between unquantized feature dimensions.
- **What it means:** The total error grows linearly with the path length $L$ and the feature dimension $D$. The error per frame has a linear term (dependent on the true distance) and a quadratic term (dependent only on the quantization step).
- **What it costs:** This formula guides our choice of $Q$ (and therefore $s$). Tighter bounds require smaller $s$, meaning wider feature buses and larger multipliers.
- **What it does not say:** This is a worst-case bound. In practice, quantization errors are often uncorrelated and grow closer to $\sqrt{L}$ than $L$. However, for hardware correctness, we design for the worst case.

**Design guideline.** For reading assessment where Pearson Correlation Coefficient (PCC — the correlation between hardware DTW scores and human expert ratings) degradation must stay below 0.02, INT16 features with a 48-bit accumulator provide sufficient headroom for sequences up to $N = 2,000$ frames (20 seconds of audio at 100 frames/s). INT8 features degrade PCC by approximately 0.05–0.08 for typical reading passages, which may be acceptable for coarse screening but not for diagnostic assessment.

---

## 8.9 GPU vs. FPGA Microarchitectural Comparison for DTW

The thesis is about migration from the Jetson Orin. We must therefore rigorously compare what happens when DTW runs on the GPU versus the FPGA. A reader who skips this analysis would rightfully ask: why not just run DTW on the Orin's 2,048 CUDA cores?

### GPU Wavefront Execution in CUDA

DTW *can* be parallelized on a GPU using anti-diagonal wavefront execution with shared memory tiling. Each CUDA thread block processes a tile of the DP grid (typically $32 \times 32$ cells), with threads computing cells along the same anti-diagonal simultaneously. However, progressing from one tile anti-diagonal to the next requires inter-block synchronization — either via cooperative groups (which occupy the entire GPU) or via sequential kernel launches from the host.

If we partition the $N \times M$ grid into tiles of size $T_b \times T_b$, the number of tile-level anti-diagonals is $O(N/T_b + M/T_b)$. Each requires either a global memory fence or a new kernel launch. Each CUDA kernel launch incurs approximately 5 $\mu$s of overhead on the Orin. For $N = M = 500$ and $T_b = 32$, the anti-diagonal tile count is roughly 31, costing $31 \times 5\;\mu\text{s} = 155\;\mu\text{s}$ in launch overhead alone — before any computation. For always-on reading assessment at 100 frames/s (a 10 ms deadline), this overhead alone consumes 1.55% of the frame budget, and it compounds with the actual compute time.

### Why Tensor Cores Cannot Help

The Orin's most potent compute units are its Tensor Cores, capable of hundreds of tera-operations per second. But this power is inaccessible for DTW. Tensor Cores perform exactly one operation: Matrix Multiply-Accumulate ($D = A \times B + C$). The inner loop of DTW is the Bellman equation: $d + \min(a, b, c)$ — an addition and a three-way minimum. This is an operation in the tropical semiring (where "multiply" is addition and "add" is minimum), not standard arithmetic. Tensor Cores are structurally incapable of computing a three-way minimum.

This is a crucial architectural insight: the Orin's most expensive and powerful silicon sits completely idle during DTW computation. The GPU is forced to execute DTW on its standard CUDA cores, memory-bound by the shared memory tile loads and latency-bound by wavefront synchronization.

### FPGA Advantage: Deterministic Latency and Energy Efficiency

For always-on reading assessment devices in classrooms, we require strict deterministic latency. When the student stops speaking, the system must respond within a fixed deadline. The GPU approach suffers from kernel launch overhead, unpredictable memory coalescing penalties, and OS scheduling jitter (the P99 tail latency on Orin can exceed the P50 by $3\times$–$5\times$).

Our FPGA systolic array maps the spatial structure of the DTW grid directly into silicon routing. Data flows continuously through the array. Once the pipeline fills, the array produces one DTW result per utterance with deterministic latency of $N + M - 1$ clock cycles, zero scheduling overhead, and mathematical bit-exactness.

| Metric | GPU CUDA (Jetson Orin) | FPGA Systolic (Kria KV260) |
|--------|----------------------|--------------------------|
| **DTW Latency** ($N = M = 500$) | ~200–500 $\mu$s (kernel launches + compute) | ~5 $\mu$s at 200 MHz |
| **Throughput** | Moderate (memory-bound, warp starvation) | High (1 result per $N + M$ cycles) |
| **Power** | 15–30 W (MAXN mode) | 3–5 W (full fabric active) |
| **Energy per Evaluation** | ~3–15 mJ | ~0.015–0.025 mJ |
| **Tail Latency (P99/P50)** | $3\times$–$5\times$ (OS jitter) | $1.0\times$ (deterministic) |
| **Tensor Core Utilization** | 0% (structurally incompatible) | N/A |
| **Programming Effort** | Moderate (CUDA, shared memory tuning) | High (RTL/HLS, timing closure) |

The energy-per-evaluation ratio is the defining metric. Even if the GPU achieves comparable raw latency through careful CUDA optimization, it burns $100\times$–$600\times$ more energy per evaluation. For a battery-powered classroom device processing thousands of evaluations per day, this difference determines whether the device lasts a school day or an hour.

---

## 8.10 Related Work

### DTW Hardware Acceleration

The foundation of our acceleration strategy rests on decades of dynamic programming optimization, beginning with Sakoe and Chiba's (1978) seminal work, "Dynamic programming algorithm optimization for spoken word recognition" in IEEE TASSP. They established the global constraints — such as the Sakoe-Chiba band — that limit the warping path search space, a mathematical boundary we directly map to FPGA processing element count. As dataset sizes grew, software limits drove the community toward hardware. Sart, Mueen, et al. (2010) presented a breakthrough in "Accelerating Dynamic Time Warping Subsequence Search with GPUs and FPGAs" at IEEE ICDM, demonstrating that while GPUs yield two orders of magnitude speedup over CPUs, FPGAs achieve up to four orders of magnitude by natively pipelining the recurrence relations. Subsequent FCCM and FPT literature, such as Xia et al. (2013), exposed how deeply pipelined datapaths circumvent CPU cache bottlenecks. Neil et al. (2014) pioneered hardware-efficient architectures for autonomous phoneme recognition, proving that low-latency speech pipelines belong on dedicated logic rather than host software.

### Systolic Arrays and Spatial DP: The Smith-Waterman Connection

The DTW DP grid shares its data dependency structure with the Smith-Waterman algorithm for biological sequence alignment, and we draw heavily from 40 years of bioinformatics accelerator design. H.T. Kung's (1982) "Why systolic architectures?" laid the theoretical groundwork, demonstrating how rhythmic, localized data flow across processing elements maximizes compute-to-I/O ratios — a strict necessity for memory-bound dynamic programming. Lipton and Lopresti (1985) materialized this concept in "A Systolic Array for Rapid String Comparison," fabricating a custom nMOS chip that executed edit distance operations orders of magnitude faster than minicomputers. Modern efforts culminate in Turakhia et al.'s (2018) ASPLOS paper on "Darwin: A Genomics Co-processor," which mapped Smith-Waterman recurrence equations to a highly parallel systolic array handling massive sequence lengths through precise data movement orchestration. We port these exact systolic routing primitives to the audio domain, re-tuning the sequence comparators to process continuous acoustic features rather than discrete nucleotide characters.

### Pronunciation Assessment and CAPT Systems

Our hardware must serve the application layer of Computer-Assisted Pronunciation Training (CAPT — systems for language learners). Witt and Young (2000) defined the standard with "Phone-level pronunciation scoring and assessment for interactive language learning" in Speech Communication, introducing the Goodness of Pronunciation (GOP) metric that remains the statistical anchor for evaluating learner speech. Hu et al. (2015) pushed accuracy by substituting traditional HMMs with DNNs and employing transfer learning, drastically reducing false rejection rates. Modern embedded CAPT systems focus on hardware-software co-design to push DNN-based GOP algorithms to edge SoCs. Our work directly accelerates the temporal alignment bottleneck inherent in these edge-based phoneme evaluators.

### GPU DTW and Tensor Core Limitations

While GPUs dominate dense acoustic modeling, they structurally falter on DTW's sequential dependencies. CUDA-based DTW implementations hit a hard limit defined by the wavefront: threads must synchronize iteratively across anti-diagonals, starving the GPU of its massive thread-level parallelism. Tensor Cores — rigidly fused multiply-accumulate engines designed for matrix multiplication — fundamentally cannot compute the minimum reduction required by the DTW recurrence. Cuturi and Blondel (2017) introduced "Soft-DTW" at ICML, replacing the hard minimum with a differentiable softmin operator for neural network training; however, this actually increases the computational load for inference. We bypass these GPU architectural mismatches by implementing the hard DTW constraint in custom FPGA logic.

### DTW Variants for Robust Assessment

Standard DTW suffers from pathological alignments under amplitude shifts and partial utterances. Keogh and Pazzani (2001) addressed this with Derivative Dynamic Time Warping (DDTW) at SDM, aligning structural shape rather than raw values — advantageous for comparing pitch and formants in non-native speakers. Müller (2007) formalized subsequence DTW in "Information Retrieval for Music and Motion," allowing short templates to slide along continuous signals without strict endpoint constraints. Salvador and Chan (2007) developed FastDTW for linear-time approximation, though our FPGA implementation achieves low latency through exact hardware parallelism rather than heuristic multi-scale projection.

### Our Position

To our knowledge, no prior work has combined a banded DTW systolic accelerator with real-time pronunciation assessment on an edge FPGA SoC under a controlled power-matched comparison against an edge GPU. By bridging the bioinformatics systolic arrays of the 1980s with modern DNN-based phonetic scoring, we expose a critical hardware-software trade-off: moving the sequential wavefront out of CUDA and into spatial logic.

---

## 8.11 Diagnostic Exercises and Associated Experiment

To solidify these concepts, the following exercises outline the software baseline validation. 🚧 These experiments are staged in the `../chapter08/` repository directory and represent our software ground truth before hardware migration.

- **Exercise 1**: Implement the unconstrained DTW recurrence in Python using NumPy. Extract MFCC features from two sample wav files and compute the optimal warping path. Validate your resulting path against the `dtw-python` library output.
- **Exercise 2**: Profile the computation time of your DTW implementation. Generate synthetic sequences of lengths $N \in \{100, 200, 400, 800, 1600\}$. Plot execution time versus $N$ to observe the $O(N^2)$ quadratic growth curve. This curve defines the necessity of our hardware acceleration.
- **Exercise 3**: Compute the Euclidean distance, Cosine distance, and DTW distance on 15 pairs of utterances. Observe how Euclidean distance fluctuates with varying microphone gains, while Cosine and DTW distances remain relatively stable.
- **Exercise 4**: Implement Subsequence DTW by modifying the boundary conditions from Exercise 1. Test with a student recording that is shorter than the reference.
- **Exercise 5**: Quantize the MFCC features to INT16 and INT8. Compare the resulting DTW distances against the FP64 reference. Plot the relative error as a function of bit-width.

**End of Chapter 8.**
