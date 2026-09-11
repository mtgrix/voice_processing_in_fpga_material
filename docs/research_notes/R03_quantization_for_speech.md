# Research Note R03: Hardware-Aware Quantization for Audio Models

- **Source ID**: `R01-03`, `R01-05`
- **Topic**: Fixed-Point Representation, INT8/INT4 QAT, and Word Error Rate Protection
- **Date**: 2026-09-11

---

## 1. Acoustic Sensitivity to Quantization Noise

Speech signals possess high dynamic range and time-varying harmonic structures:
- **Audio Preprocessing**:
  Log-Mel filterbanks amplify low-energy speech components. Rounding errors in fixed-point FFT or log-compression introduce spurious spectral artifacts that corrupt subsequent acoustic modeling.
- **Acoustic Model Layers**:
  Depthwise separable convolutions and self-attention heads exhibit disparate dynamic ranges. Uniform 8-bit quantization often suffices for standard convolutional layers, but attention Softmax and LayerNorm require careful calibration (or power-of-two piecewise linear approximation) to prevent catastrophic WER degradation.

---

## 2. Mathematical Uniform Symmetric Quantization Contract

Let real-valued tensor $X \in \mathbb{R}$ with dynamic range $[-x_{\max}, x_{\max}]$.
For bit-width $b$ (e.g. $b=8$ for INT8, range $[-2^{b-1}, 2^{b-1}-1] = [-128, 127]$):

1. **Scale Factor ($S$)**:
   $$S = \frac{x_{\max}}{2^{b-1} - 1}$$
2. **Quantization Function ($Q$)**:
   $$q = \text{clamp}\left(\left\lfloor \frac{x}{S} \right\rceil, -2^{b-1}, 2^{b-1}-1\right)$$
3. **Dequantization Function ($\hat{X}$)**:
   $$\hat{x} = q \times S$$
4. **Quantization Error ($e$)**:
   $$e = x - \hat{x}, \quad |e| \le \frac{S}{2}$$
