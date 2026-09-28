# Experiment 8: Audio Correlation Algorithms — Software Baseline

## 1. Experiment Metadata & Purpose
- **Experiment code**: `exp_08_audio_correlation_baseline`
- **Linked chapter**: Chapter 08 — Audio Correlation Algorithms for Reading Assessment
- **Status**: 🚧 Design phase / Scaffolded
- **Purpose**: Implement and validate software baselines for three audio correlation
  algorithms (DTW, GOP, Cosine Similarity) on MFCC feature sequences, establishing
  the golden reference for hardware verification in Chapter 9.

## 2. Theoretical Context & Pedagogical Goal
- Validate the DTW dynamic programming recurrence against the `dtw-python` library.
- Demonstrate the $O(N \times M)$ quadratic scaling of DTW with sequence length.
- Compare correlation accuracy (PCC against human scores) across DTW, GOP, and
  cosine similarity on a reading assessment dataset.
- Establish the computational baseline that motivates FPGA acceleration.

## 3. Hardware Target
- **Software baseline**: Host CPU (any x86/ARM64 with Python 3.10+).
- **Profiling target**: NVIDIA Jetson Orin (if available) for GPU baseline timing.
- **Downstream hardware**: AMD Xilinx Kria KV260 (Chapter 9 uses these results as
  the golden reference for bit-exact hardware verification).

## 4. Mathematical Derivation / Algorithm

### DTW Recurrence
$$D(i,j) = d(\mathbf{x}_i, \mathbf{y}_j) + \min\{D(i-1,j),\; D(i-1,j-1),\; D(i,j-1)\}$$

Where $d(\mathbf{x}_i, \mathbf{y}_j) = \sqrt{\sum_{k=1}^{D}(x_{i,k} - y_{j,k})^2}$ is the
Euclidean distance between two MFCC feature vectors of dimension $D = 80$.

### Sakoe-Chiba Band Constraint
Restrict the warping path to $|i - j| \leq W$ where $W$ is the band width,
reducing complexity from $O(N \times M)$ to $O(N \times W)$.

### Normalized DTW Distance
$$\text{DTW}_{\text{norm}} = \frac{D(N, M)}{N + M}$$

## 5. Input Signal & Dataset Specs
- **Feature extraction**: 80-bin log-Mel MFCC from Chapter 1 pipeline.
- **Audio parameters**: 16 kHz sample rate, 25 ms window, 10 ms hop.
- **Test pairs**: Reference and student recordings of the same text passage.
- **Dataset candidates**:
  - SpeechOcean762 (pronunciation assessment with human scores)
  - L2-ARCTIC (accented English with phoneme annotations)
  - Google Speech Commands v2 (for initial validation)

## 6. Execution Command
```bash
# Run DTW baseline with validation
python chapter08/dtw_baseline.py --validate

# Profile DTW scaling with sequence length
python chapter08/dtw_baseline.py --profile-scaling

# Compare all three algorithms
python chapter08/dtw_baseline.py --compare-all
```

## 7. Expected Numerical Output / Tolerances
- DTW distance matches `dtw-python` library within $10^{-6}$ relative tolerance.
- DTW computation time scales as $O(N^2)$ — regression $R^2 > 0.99$ on log-log plot.
- Sakoe-Chiba band ($W = 32$) reduces computation by $> 5\times$ vs. unconstrained DTW
  for sequences of length $N > 200$.

## 8. Profiling & Measurement Methodology
- Wall-clock time via `time.perf_counter_ns()` for each algorithm.
- Memory usage via `tracemalloc` for the DTW cost matrix.
- Sweep sequence lengths $N \in \{50, 100, 200, 500, 1000\}$ frames.
- Report mean ± std over 100 runs per configuration.

## 9. Empirical Results & Artifacts
- [Awaiting execution]

## 10. Hardware-Software Trade-offs
- DTW's $O(N \times M)$ cost matrix is the primary bottleneck — the inner loop
  (distance + min-of-three) maps to a single FPGA Processing Element.
- Cosine similarity is $O(D)$ per pair but requires a pretrained encoder.
- GOP requires a neural acoustic model (DNN inference) but the scoring itself
  is lightweight log-averaging on CPU.

## 11. Limitations & Assumptions
- Software baseline uses FP64 arithmetic; hardware will use INT16/INT8 fixed-point.
- Quantization degradation analysis deferred to Chapter 7 revision.
- No pretrained acoustic model for GOP in this experiment; GOP scoring uses
  synthetic phoneme posteriors for algorithm validation only.

## 12. Pedagogical Takeaways
- DTW is the most computationally intensive algorithm and the natural FPGA target.
- The diagonal wavefront parallelism of the DP grid (anti-diagonal cells independent)
  is invisible in sequential software but defines the hardware architecture.
- Band constraints (Sakoe-Chiba) reduce both software time and hardware PE count.

## 13. Source Citations
- Sakoe, H. & Chiba, S. (1978). "Dynamic programming algorithm optimization for
  spoken word recognition." IEEE TASSP, 26(1), 43-49.
- Witt, S. & Young, S. (2000). "Phone-level pronunciation scoring and assessment
  for interactive language learning." Speech Communication, 30(2-3), 95-108.
- Hu, W. et al. (2015). "Improved mispronunciation detection with deep neural
  network trained acoustic models and transfer learning based logistic regression
  classifiers." Speech Communication, 67, 154-166.
