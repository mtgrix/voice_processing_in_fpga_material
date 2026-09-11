# Chapter 1: From Acoustic Waves to Edge Inference

> *"Audio is continuous time; processing speech at the edge is a physical battle between latency constraints and silicon power limits."*

---

## 1.1 Intuition: The Fundamental Divergence Between Vision and Voice

In edge compute systems, computer vision and voice AI pose diametrically opposed execution characteristics:

A camera frame arrives in discrete static snapshots (e.g. $30\text{ fps} \approx 33.3\text{ ms}$ per frame). Once delivered, the entire 2D pixel tensor ($1920 \times 1080 \times 3$) is available in memory. The processor can aggregate multiple frames into a batch to saturate thousands of parallel arithmetic units on a Graphics Processing Unit (GPU).

In contrast, acoustic speech is a **continuous, 1D time-varying waveform** $x(t)$. Humans speak continuously at a standard sampling rate of $16\text{ kHz}$ ($16,000$ amplitude samples per second). A user cannot wait for the system to buffer a full second of speech before processing; interactive speech recognition and noise cancellation require near-instantaneous feedback with end-to-end latency below $100\text{ ms}$, or even $<10\text{ ms}$ for keyword spotting (KWS).

Consequently: **Edge voice AI fundamentally operates at batch size one ($batch=1$) over continuous sliding windows.** This reality exposes deep inefficiencies in GPU execution architectures and presents an immense opportunity for spatial computing on Field-Programmable Gate Arrays (FPGAs).

---

> ### 📘 Minimal Mathematics for this Chapter
> 
> Three foundational concepts:
> 1. **Discrete Fourier Transform (DFT)**: Decomposes a time sequence into constituent sinusoidal basis functions across discrete frequency bins.
> 2. **1D Convolution**: Slides an impulse response kernel across a temporal sequence to extract localized features.
> 3. **Logarithmic Scaling**: Compresses the extreme dynamic range of acoustic pressure to match human auditory psychoacoustics.

---

## 1.2 The Streaming Audio Preprocessing Pipeline

Before a deep neural network processes speech, mechanical pressure waves captured by a microphone undergo mathematical transformations to convert raw temporal amplitude into a 2D time-frequency spectral representation.

```text
Audio Waveform x[n] (16 kHz)
   │
   ▼
[ Sliding Window Buffer ] ──── Frame length: N=400 (25 ms), Hop length: H=160 (10 ms)
   │
   ▼
[ Hamming Windowing ] ──── Suppresses boundary spectral leakage
   │
   ▼
[ Short-Time Fourier Transform (STFT) ] ──── O(N log N) FFT
   │
   ▼
[ Power Spectrogram ] ──── |X(k)|^2 = Re^2 + Im^2
   │
   ▼
[ Mel Filterbank Matrix ] ──── Matrix multiplication M x (N/2 + 1) with M=80 triangular filters
   │
   ▼
[ Logarithmic Compression ] ──── S[m] = ln(max(E[m], ε)) ── Fed to Neural Network
```

### Mathematical Formulation: Short-Time Fourier Transform (STFT)

For a discrete signal $x[n]$ extracted through an analysis window $w[n]$ of length $N$ at time frame $m$ with hop size $H$:

$$X[m, k] = \sum_{n=0}^{N-1} x[m \cdot H + n] \cdot w[n] \cdot e^{-j \frac{2\pi}{N} k n}$$

Where:
- $m \in \mathbb{Z}$ is the time-frame index.
- $k \in \{0, 1, \dots, N/2\}$ is the discrete frequency bin.
- $N$ is the frame length ($N=400$ samples for $25\text{ ms}$ at $16\text{ kHz}$).
- $H$ is the hop size ($H=160$ samples for $10\text{ ms}$).
- $w[n] = 0.54 - 0.46 \cos\left(\frac{2\pi n}{N-1}\right)$ is the Hamming window.

---

## 1.3 Mel Filterbanks & Log-Mel Spectrogram Extraction

Human pitch perception is non-linear, exhibiting high sensitivity at lower frequencies and diminishing sensitivity at higher frequencies. The Mel scale models this biological property:

$$m = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$$

We project the $N/2 + 1$ power spectral bins onto $M$ triangular bandpass filters ($M=80$):

$$E[m, b] = \sum_{k=0}^{N/2} P[m, k] \cdot H_b[k]$$

Followed by dynamic range log compression:

$$S[m, b] = \ln\left(\max(E[m, b], \epsilon)\right)$$

The resulting tensor $S \in \mathbb{R}^{T \times M}$ forms the standard input to modern acoustic architectures such as Conformer, Whisper, or MatchboxNet.

---

## 1.4 Executable Experiment: Online Streaming Preprocessing

Under [`chapter01/`](../chapter01/), experiment `exp_01_streaming_audio_pipeline.py` provides a bit-exact sliding ring-buffer implementation simulating real-time audio ingress and verifies numerical agreement between batched and streaming execution.
