# 1.3 Mathematical Modeling: STFT and Mel Filterbank

Section 1.2 constructed the physical datapath that packages streaming air pressure into discrete frames. Section 1.3 is the mathematical microscope placed over a single packet, deducing each spectral operator from wave interference and auditory perception.

Six expressions transform a streaming sample flow into the 80 numbers of a frame:
1. The Windowed Frame
2. The Short-Time Fourier Transform (STFT)
3. The Power Spectrum
4. The Mel-Frequency Mapping
5. The Mel Filterbank as a Weighted Sum
6. Logarithmic Compression

Every operator is autopsied through five fixed beats: formula, symbols, physical meaning, hardware price, and what the formula hides.

Standard design parameters:
Sampling frequency $f_s = 16{,}000\text{ Hz}$, frame length $L = 400$ samples ($25\text{ ms}$), hop size $H = 160$ samples ($10\text{ ms}$), transform length $N = 512$ points, filterbank count $M = 80$ channels, frequency span $f_{\min} = 0\text{ Hz}$ to $f_{\max} = 8{,}000\text{ Hz}$.

---

## The Probe Wave, Before the Formula

Before writing down the Fourier summation, consider the physical interrogation problem. An unknown acoustic packet arrives at the sensor as a discrete sequence of air-pressure displacements $x_\ell[n]$. How does a computational circuit determine whether this packet vibrates at a specific frequency $f_k$?

In classical physics, resonance is detected by probing: we bring an external oscillator of known frequency $\omega_k$ into contact with the system and observe steady-state energy transfer. In digital computation, we generate an internal reference probe tone and evaluate its constructive or destructive interference against the incoming signal through an inner product:

$$\int_0^T x(t) \cos(\omega_k t) \, dt$$

If $x(t)$ contains an oscillation at $\omega_k$ in identical phase ($\cos(\omega_k t)$), the product becomes $\cos^2(\omega_k t) = \frac{1 + \cos(2\omega_k t)}{2}$. Integrated across an integer number of cycles $T$, the high-frequency $2\omega_k$ component averages to zero, leaving a positive DC accumulation of $\frac{T}{2}$. If $x(t)$ oscillates at any different harmonic $\omega_m$ ($m \ne k$), the cross-product integrates to identically zero. The probe resonates exclusively with its own frequency.

Now expose the fatal flaw of a single probe wave: **phase blindness**.

Suppose the incoming acoustic packet contains a pure tone at $\omega_k$, but arrives delayed by a quarter-cycle (a phase shift of $\pi/2$, turning the input into a pure sine wave $\sin(\omega_k t)$). The product evaluated by our cosine probe is now $\sin(\omega_k t)\cos(\omega_k t) = \frac{1}{2}\sin(2\omega_k t)$. Over the integration interval $T$, this wave integrates to exactly zero:

$$\int_0^T \sin(\omega_k t) \cos(\omega_k t) \, dt = 0$$

The single probe reports zero energy. A pure acoustic tone is roaring through the physical transducer, but because it arrived with a $90^\circ$ phase offset, our mathematical detector is completely deaf to it.

To eliminate phase blindness, we must interrogate the incoming wave with **two orthogonal probes in quadrature**: an in-phase probe oscillating as $\cos(\omega_k t)$ and a quadrature probe oscillating as $-\sin(\omega_k t)$ (delayed by $90^\circ$). When an arbitrary signal $x(t) = A \cos(\omega_k t + \theta)$ strikes this dual-branch detector, the cosine branch measures $A \cos\theta$ and the sine branch measures $A \sin\theta$. By the Pythagorean theorem, total signal magnitude is recovered with complete phase immunity:

$$A = \sqrt{(A\cos\theta)^2 + (A\sin\theta)^2}$$

Euler's identity, $e^{-j\theta} = \cos\theta - j\sin\theta$, is the algebraic packaging of this two-channel physical quadrature receiver.

```
                  +---> [ * cos(2 pi k n / N) ] ---> [ Accumulator ] ---> Re(X[k]) ---+
                  |                                                                   |---> X[k] = Re + j Im
x[n] (Frame) -----+                                                                   |
                  |                                                                   |
                  +---> [ * -sin(2 pi k n / N) ] --> [ Accumulator ] ---> Im(X[k]) ---+
```

> [!TIP]
> **$\bigstar$ GROUNDBREAKING FINDING**
>
> A complex spectral bin is a dual-channel hardware quadrature receiver: two orthogonal reference oscillators ($\cos$ and $-\sin$) beating against the incoming pressure wave, returning two agreement scores that recover signal magnitude invariant to arrival phase.

---

## 1. The Windowed Frame

To prevent artificial step discontinuities at frame boundaries, the finite audio segment must be smoothly tapered toward zero before spectral analysis.

### The 5-Beat Autopsy: The Windowed Frame

**Beat 1: The Formula**
$$x_\ell[n] = x[n_0 + \ell H + n] \, w[n], \qquad n = 0, 1, \dots, L-1$$
followed by zero-padding to transform length $N = 512$:
$$x_\ell[n] = 0, \qquad L \le n < N$$

**Beat 2: The Symbols**
- $x_\ell[n]$: windowed frame $\ell$, an array of $L = 400$ samples ($25\text{ ms}$ at $f_s = 16{,}000\text{ Hz}$).
- $x$: incoming continuous streaming audio sequence.
- $H$: hop size, $160$ samples ($10\text{ ms}$).
- $L$: physical frame length, $400$ samples ($25\text{ ms}$).
- $w[n]$: fixed Hamming window, tapering boundary samples to $w[0] = w[L-1] = 0.08$ with a center peak of $1.00$.

**Beat 3: The Physical Meaning**
Slicing a continuous signal with an abrupt cut is equivalent to multiplying by a rectangular window, which convolves the true underlying spectrum with a sinc function in the frequency domain. The high side-lobes of a rectangular window decay slowly, with the first side-lobe peaking at $-13\text{ dB}$ relative to the main lobe. The smooth raised-cosine profile of the Hamming window brings boundary values down to $0.08$, suppressing the first side-lobe peak to $-44\text{ dB}$—a $31\text{ dB}$ reduction in spurious spectral leakage.

```
Figure 6: Rectangular vs. Hamming Window Spectral Response
-----------------------------------------------------------------------------------------
Rectangular Window:  Main-lobe width = 2 f_s / L = 80 Hz    First side-lobe = -13 dB
Hamming Window:      Main-lobe width = 4 f_s / L = 160 Hz   First side-lobe = -44 dB
Attenuation Gain:    31 dB side-lobe suppression bought by doubling main-lobe width.
```

> [!NOTE]
> **$\blacktriangleright$ PHYSICAL INSIGHT**
>
> Windowing is an unavoidable bargain with the uncertainty principle: we accept a doubling of main-lobe width (from $80\text{ Hz}$ to $160\text{ Hz}$) to buy $31\text{ dB}$ of side-lobe suppression. Without this suppression, loud fundamental harmonics would wash out quiet high-frequency formants across the entire spectrum.

**Beat 4: The Hardware Price**
The hardware price is $L = 400$ real multiplications per $10\text{ ms}$ frame. Symmetric window coefficients can be stored in an on-chip lookup table. Pipelined multipliers execute this stage easily within the frame cadence. The precise slice count is Section 1.4 / Chapter 6.

**Beat 5: What the Formula Does Not Say**
Windowing destroys acoustic energy near the frame boundaries, attenuating edge samples toward zero. To prevent blind spots where transient acoustic events could vanish undetected, consecutive frames must overlap heavily: a hop size of $H = 160$ samples advances the window by only $40\%$ of its length, leaving a $60\%$ overlap ($L - H = 240$ shared samples) that guarantees continuous, uniform energy coverage across the streaming timeline.

---

## 2. The Short-Time Fourier Transform (STFT)

Having windowed and zero-padded the frame, we assemble the time-dependent spectral matrix that maps phonetic transitions as they evolve through time.

### The 5-Beat Autopsy: The Short-Time Fourier Transform

**Beat 1: The Formula**
$$X_\ell[k] = \sum_{n=0}^{N-1} x_\ell[n] \, e^{-j \frac{2\pi k n}{N}}, \qquad k = 0, 1, \dots, N-1$$

**Beat 2: The Symbols**
- $k \in \{0, 1, \dots, N-1\}$: discrete frequency bin index, mapping to physical frequency $f_k = k \frac{f_s}{N} = k \times \frac{16{,}000}{512} = k \times 31.25\text{ Hz}$.
- $n \in \{0, 1, \dots, N-1\}$: discrete time sample index within the $N$-point padded analysis frame.
- $x_\ell[n]$: framed audio signal, padded with $N - L = 112$ zeros to transform length $N = 512$.
- $X_\ell[k]$: complex spectral coefficient. Because the input audio is real-valued, the upper half of the spectrum is redundant by conjugate symmetry ($X_\ell[N-k] = X_\ell^*[k]$), allowing the system to retain only the first $N/2 + 1 = 257$ independent frequency bins ($0\text{ Hz}$ to $8{,}000\text{ Hz}$).

**Beat 3: The Physical Meaning**
The STFT projects the 1D temporal signal into a 2D complex time-frequency coordinate space, balancing the fundamental trade-off between temporal localization and frequency resolution. A $25\text{ ms}$ window isolates stationary acoustic slices of speech, while providing sufficient frequency granularity ($\Delta f = 31.25\text{ Hz}$) to separate fundamental formants.

**Beat 4: The Hardware Price**
The hardware price is $N$ bins $\times N$ complex multiply-accumulates per $10\text{ ms}$ frame under direct evaluation. A radix-2 FFT exists so the designer is not stuck with $N^2$, reducing the computational workload to $\frac{N}{2} \log_2 N$ butterflies per frame. The precise slice count is Section 1.4 / Chapter 6.

**Beat 5: What the Formula Does Not Say**
The summation over $n \in [0, N-1]$ mathematically presumes that the signal repeats periodically with period $N$. Furthermore, zero-padding from $L = 400$ to $N = 512$ merely interpolates the evaluation grid more densely; it does not improve the physical frequency resolution of the acoustic sensor, which remains strictly bounded by the physical window length $L$.

---

## 3. The Power Spectrum

Downstream acoustic models do not ingest raw complex coordinates. We must convert the complex spectral bins into real-valued acoustic energy.

### The 5-Beat Autopsy: The Power Spectrum

**Beat 1: The Formula**
$$P_\ell[k] = |X_\ell[k]|^2 = \text{Re}(X_\ell[k])^2 + \text{Im}(X_\ell[k])^2, \qquad k = 0, 1, \dots, \frac{N}{2}$$

**Beat 2: The Symbols**
- $P_\ell[k] \in \mathbb{R}_{\ge 0}$: power spectral density at frame $\ell$ and frequency bin $k$, representing real-valued energy across $257$ frequency bins.
- $\text{Re}(X_\ell[k]), \text{Im}(X_\ell[k])$: in-phase and quadrature projection scores from the STFT.

**Beat 3: The Physical Meaning**
Speech recognition models require the distribution of signal energy across frequency, not the acoustic arrival phase. Squaring the complex magnitude strips phase angle while converting $257$ complex coordinates into $257$ non-negative real energy values representing acoustic formant structure.

**Beat 4: The Hardware Price**
The hardware price is 2 squarings and 1 addition per bin across 257 bins per $10\text{ ms}$ frame. Computing power ($|X|^2$) rather than magnitude ($|X|$) avoids square-root hardware logic entirely. The precise slice count is Section 1.4 / Chapter 6.

**Beat 5: What the Formula Does Not Say**
Discarding phase is an irreversible, one-way operation. While beneficial for extracting clean formant envelopes for recognition, time-domain waveform reconstruction is no longer possible without phase estimation.

---

## 4. Mel-Frequency Mapping

Linear frequency bins treat all frequencies with uniform numerical importance. Human hearing, however, perceives pitch non-linearly.

### The 5-Beat Autopsy: Mel-Frequency Mapping

**Beat 1: The Formula**
$$\mathrm{mel}(f) = 2595 \log_{10}\!\left(1 + \frac{f}{700}\right)$$

**Beat 2: The Symbols**
- $f$: continuous physical frequency in Hertz ($0 \le f \le 8{,}000\text{ Hz}$).
- $\mathrm{mel}(f)$: subjective perceived pitch in Mels.

**Beat 3: The Physical Meaning**
Human cochlear frequency resolution is non-linear: highly sensitive to minute pitch variations at low frequencies (vowel formants), but coarse at higher frequencies (fricative noise). The Mel scale models this biological warping: equal perceptual intervals of $355\text{ mel}$ span only $259\text{ Hz}$ at the lowest band, but expand to $2{,}351\text{ Hz}$ at the highest band—a nine-fold dilation in physical bandwidth for the same perceptual step.

**Beat 4: The Hardware Price**
The hardware price is zero runtime logic. The Mel warp is evaluated offline at system design time to establish the filterbank center frequencies and weighting coefficients stored in on-chip memory.

**Beat 5: What the Formula Does Not Say**
The continuous mathematical curve must be mapped onto a discrete FFT bin grid. At low frequencies, the bandwidth of perceptual filters can become narrower than the digital bin spacing $\Delta f = 31.25\text{ Hz}$, creating a risk of bin discretization mismatch.

---

## 5. Mel Filterbank as a Weighted Sum

To compress linear bins into perceptual channels, triangular filters integrate energy across non-uniform bands.

### The 5-Beat Autopsy: The Mel Filterbank

**Beat 1: The Formula**
$$E_\ell[m] = \sum_{k=0}^{256} g_m[k] \, P_\ell[k], \qquad m = 0, 1, \dots, M-1$$
where $g_m[k]$ represents overlapping triangular weighting functions:
$$g_m[k] = \begin{cases}
\dfrac{k - k_{m-1}}{k_m - k_{m-1}}, & k_{m-1} \le k \le k_m \\[6pt]
\dfrac{k_{m+1} - k}{k_{m+1} - k_m}, & k_m < k \le k_{m+1} \\[6pt]
0, & \text{otherwise}
\end{cases}$$

**Beat 2: The Symbols**
- $m \in \{0, 1, \dots, M-1\}$: Mel band index, with $M = 80$ filters.
- $k_m$: discrete FFT bin index of the center frequency of filter $m$.
- $g_m[k]$: triangular filter weight for bin $k$ in filter $m$.
- $E_\ell[m]$: integrated Mel spectral energy vector (shape $[1, 80]$).

**Beat 3: The Physical Meaning**
Eighty overlapping triangular filters compress 257 linear power bins into 80 perceptual energy channels. Each filter integrates energy across its band, preserving fine spectral detail in low-frequency vowel regions while pooling broad energy swaths in high-frequency noise regions.

> [!NOTE]
> **$\blacktriangleright$ PHYSICAL INSIGHT**
>
> The Mel filterbank is an unequal information concentrator. In low frequencies ($0\text{--}1\text{ kHz}$), where pitch and fundamental vowel formants reside, each band integrates only a few FFT bins, preserving fine harmonic detail. In high frequencies ($6\text{--}8\text{ kHz}$), where fricative consonants produce diffuse noise, each band pools dozens of bins, preserving overall energy envelope while shedding irrelevant fine structure.

**Beat 4: The Hardware Price**
The hardware price is a sparse matrix-vector multiplication per frame. Because each linear FFT bin $k$ falls within at most two adjacent triangular filters, the matrix is predominantly zero. The hardware price is non-zero multiply-accumulates across active bin spans; the precise slice count is Section 1.4 / Chapter 6.

**Beat 5: What the Formula Does Not Say**
The discretization trap. When continuous filter center frequencies are mapped to discrete bin indices, adjacent low-frequency filters can round to the identical bin if spacing is narrower than $\Delta f = 31.25\text{ Hz}$. A filter whose center and edges collapse to the same bin produces zero width and returns dead energy. Hardware filterbanks must ensure every band spans at least one unique bin.

---

## 6. Logarithmic Compression

The final transformation compresses wide physical energy variations into a normalized feature space suitable for neural network layers.

### The 5-Beat Autopsy: Logarithmic Compression

**Beat 1: The Formula**
$$S_\ell[m] = \ln\bigl(\max(E_\ell[m], 10^{-6})\bigr), \qquad m = 0, 1, \dots, M-1$$

**Beat 2: The Symbols**
- $S_\ell[m]$: log-Mel energy feature vector (shape $[1, 80]$) emitted to downstream acoustic models.
- $E_\ell[m]$: raw Mel band energy from Operator 5.
- $10^{-6}$: clamping floor preventing catastrophic $\ln(0) \to -\infty$ evaluation during silence.

**Beat 3: The Physical Meaning**
Human loudness perception scales logarithmically with acoustic power. In the physical environment, acoustic pressure spans from a quiet whisper ($10^{-5}\text{ Pa}$) to a loud shout ($10\text{ Pa}$)—an energy ratio of $10^{10}$, or $100\text{ dB}$. Logarithmic compression normalizes this vast dynamic range into a compact numerical distribution. Furthermore, taking the logarithm converts multiplicative channel effects (such as microphone distance and room acoustics) into simple additive offsets.

**Beat 4: The Hardware Price**
The hardware price is 80 logarithm evaluations per $10\text{ ms}$ frame. In hardware, logarithms can be evaluated using lookup tables or piece-wise polynomial approximations. The precise slice count is Section 1.4 / Chapter 6.

**Beat 5: What the Formula Does Not Say**
The derivative of the natural logarithm, $\frac{d}{dx}\ln(x) = \frac{1}{x}$, diverges toward infinity as $x \to 0$. While clamping at $10^{-6}$ prevents negative infinity, tiny noise fluctuations near the clamping floor still produce large excursions in feature space, demanding careful numerical management during fixed-point quantization.

---

## The Silicon Reality Check: Bridge to Section 1.4

The mathematical derivations of STFT and Mel filterbanks in this section assume infinite-precision arithmetic, zero-latency memory access, and instantaneous execution. On a workstation development machine, these equations run effortlessly within Python scientific environments, where abundant memory and floating-point hardware hide the $10\text{ ms}$ processing deadline and thermal budgets.

When this mathematical chain is pushed onto physical edge silicon operating under strict thermal limits ($< 15\text{ W}$) with a hard $10\text{ ms}$ frame deadline, abstract formulas collide with physical hardware constraints. Whether an edge GPU or a spatial FPGA fabric can satisfy these streaming acoustic deadlines is the architectural question explored next.
