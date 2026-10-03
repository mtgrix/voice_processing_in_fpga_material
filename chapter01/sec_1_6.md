# 1.6 From Recognition to Evaluation: where the group report sits, what it already does, and what is still open

> [!NOTE]
> **LEARNING OBJECTIVE**
> Rather than evaluating speech recognition purely as text transcription, this section examines how an edge voice processing system scores a learner's read-aloud utterance. We place the research group's internal technical report (`BAO_CAO_492026.pdf`, 32 slides across four September 2026 meetings: 04/09, 11/09, 18/09, 23/09) inside the end-to-end evaluation flow, reconstruct the mathematical and geometric contract established across the slides, articulate what that contract already accomplishes, systematically analyze four independent open cases, formulate architectural candidates across uniform evaluation axes, and prepare an actionable decision table for the team without pre-judging the group's choice.

---

## 1.6.0 Where the Report Sits in Read-Aloud Speech Evaluation

Automated speech scoring in educational technology is fundamentally distinct from automatic speech recognition (ASR). An ASR engine maps continuous acoustic waveforms into discrete orthographic text tokens, maximizing statistical transcription accuracy. In contrast, an automated pronunciation assessment system must evaluate a student who is reading a known prompt aloud. In this setting, the orthographic text is already given; the engineering objective is to determine how well, how accurately, and how naturally the learner articulated the target text.

Scoring a spoken read-aloud task requires five distinct processing stages:
1. **Stage 1: Audio Capture and Acoustic Conditioning.** Digitizing the raw microphone signal, removing direct-current (DC) offset, normalizing energy across varying mouth-to-microphone distances, and executing Voice Activity Detection (VAD) to trim leading and trailing non-speech silences.
2. **Stage 2: Word Edge Localization (Forced Alignment).** Segmenting the continuous audio stream into discrete word intervals by computing acoustic boundaries $[t_{\text{start}}, t_{\text{end}}]$ for each orthographic token in the prompt.
3. **Stage 3: Phonetic Correctness Verification (Acoustic Quality Scoring).** Evaluating whether the spectral realization of each segment matches the target phonemes (e.g., verifying formant trajectories $F_1, F_2, F_3$, computing Goodness of Pronunciation [GOP] log-likelihood ratios, or detecting phoneme substitutions, deletions, and insertions).
4. **Stage 4: Melodic and Prosodic Comparison Against Reference Audio.** Extracting prosodic contours---primarily fundamental frequency ($F_0$), syllabic duration, and energy dynamics---and comparing their trajectory against an exemplar spoken reference.
5. **Stage 5: Labeling and Score Calibration.** Aggregating acoustic and prosodic measurements into pedagogical feedback, mapping continuous numerical scores to discrete word-level pass/fail color codes, diagnostic feedback, or calibrated performance rubrics.

```
+----------------------------------------------------------------------------------------------------------------+
|                                         FIVE-STAGE EVALUATION PIPELINE                                         |
+--------------------+ +--------------------+ +--------------------+ +--------------------+ +--------------------+
| Stage 1: Capture   | | Stage 2: Word      | | Stage 3: Phone     | | Stage 4: Melody    | | Stage 5: Label     |
| & Conditioning     | | Edges (Forced      | | Correctness        | | Comparison vs Ref  | | & Calibration      |
|                    | | Alignment)         | | (Formants / GOP)   | | (Pearson Pitch r)  | | (r < 0.3 Rule)     |
| [Pre-trimmed wav]  | | [Bypassed by Win]  | | [Assumed by Pitch] | | [SLIDES 1-32]      | | [SLIDE 23]         |
+--------------------+ +--------------------+ +--------------------+ +--------------------+ +--------------------+
```

### Placement of the Group Report
The 32 slides of `BAO_CAO_492026.pdf` occupy **Stage 4** (Melodic and prosodic comparison via Pearson pitch correlation) and provide an initial heuristic toward **Stage 5** (word-level pass/fail labeling via sliding window thresholding). The report does not implement Stages 1, 2, or 3, but rather makes specific operational assumptions about them:
- **Stage 1 is assumed already resolved:** On Slide 25, the pipeline executes upon a pre-processed reference recording with pre-trimmed silences. The silence detection, DC removal, and boundary cropping are assumed to be performed offline before the pipeline begins.
- **Stage 2 is assumed unneeded:** Rather than deploying a forced alignment acoustic model to identify exact temporal word boundaries $[t_{\text{start}}, t_{\text{end}}]$, the report constructs an analytical sliding window model (Slides 19--23) that slices the sentence into $K+1$ overlapping geometric segments based solely on word count $K$ and total sentence length $N$.
- **Stage 3 is assumed to follow from pitch correlation:** The report treats the correlation of fundamental frequency ($F_0$) as an indicator of whether the user read correctly (``checking whether the user reads like the model'', Slide 2), assuming that a learner matching the intonation contour also pronounced the underlying phonemes accurately.

### Sarah is an Exemplar Ruler, Not Linguistic Ground Truth
Throughout the four meeting reports, the target reference is denoted as ``Sarah'' (Slide 5, 12, 25, 32). In the group's engineering baseline, Sarah is a specific native recording used as a comparative ruler. It is essential to recognize that Sarah represents an exemplar reference, not absolute linguistic ground truth. In human speech, two native speakers pronouncing the exact same sentence correctly will exhibit different baseline pitch registers (between low-pitched and high-pitched voices), distinct dynamic pitch excursions, and natural tempo fluctuations across syllables.

By selecting Sarah's audio as the sole comparative target, the pipeline adopts an engineering simplification: evaluating a student's prosodic contour against one fixed performance. Understanding where the report sits in this broader five-stage hierarchy allows a new member of the research group to appreciate what the slides deliberately chose to isolate, what they built, and what remains open for team decision.

---

## 1.6.1 The Evaluation Contract as the Slides Wrote It

Across four formal group presentations in September 2026, the research team established an explicit algorithmic and geometric contract to score spoken utterances. Every equation, worked numeric trace, and threshold in this section is extracted directly from the slide deck `BAO_CAO_492026.pdf`.

### Meeting 04/09/2026: Intonation Correlation via Pearson $r$ (Slides 1--9)

The initial presentation defines the core problem statement: *``Checking whether the graphs of two pitch contours have the same trend?''* (Checking whether two pitch contours follow the same trend, Slide 1), proposing Pearson correlation as the comparative engine: *``Pearson Correlation Coefficient: checking whether the user reads like the model''* (Slide 2).

On Slide 5, the report formulates the mathematical definition:
$$r = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y} = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2}\sqrt{\sum_{i=1}^n (y_i - \bar{y})^2}}$$

The slide explicitly assigns variable definitions:
- $n$: *``total duration of a word''* (the total duration or discrete sample point count representing the word).
- $X = \{x_1, x_2, \dots, x_n\}$: *``pitch array of a word from User''* (discrete pitch array of the learner).
- $Y = \{y_1, y_2, \dots, y_n\}$: *``pitch array of a word from Sarah''* (discrete pitch array of the reference recording).
- $\bar{x}, \bar{y}$: *``arithmetic mean pitch''* (the arithmetic mean pitch of User and Sarah).

**Mathematical Rationale from the Slides.** The deductive properties of Pearson correlation are articulated across Slides 6--8:
1. **Directional Trend Matching (Numerator):** The product $(x_i - \bar{x})(y_i - \bar{y})$ tests co-directional inflection. If the learner's pitch rises when Sarah's pitch rises (both above their respective means), or falls when Sarah's falls, the product is positive (*``Same trend''*, Slide 7). Conversely, if the learner's pitch rises while Sarah's falls, the product is negative (*``Opposite trend''*, Slide 7).
2. **Pitch Register Invariance (Denominator):** The normalization by $\sigma_X \sigma_Y$ rescales the covariance strictly into the interval $[-1, +1]$ (Slide 8). This eliminates the effect of absolute pitch magnitude (*``removes differences in pitch magnitude''*, Slide 6), enabling comparison between a low-pitched male voice and a high-pitched female voice, and normalizes dynamic intonation excursion range (*``cancels out differences in pitch excursion''*, Slide 8).

Slide 9 provides an external bibliographic reference for the statistical derivation: [Statistics Solutions Directory](https://www.statisticssolutions.com/free-resources/directory-of-statistical-analyses/pearsons-correlation-coefficient/).

### Meeting 11/09/2026: Resampling Preprocessing and the Sliding Window Model (Slides 10--23)

The presentation of 11/09/2026 addresses two central requirements: enforcing identical array lengths and localizing evaluation across multi-word sentences under the title *``SLIDING WINDOW PEARSON''* (Sliding Window Pearson, Slide 10).

**Part 1: Linear Resampling Preprocessing (Slides 11--18).** The Pearson correlation formula strictly requires arrays $X$ and $Y$ to contain an identical number of points $n$. Because human speakers read at different speaking rates, the raw pitch arrays inevitably diverge in length. Slide 11 defines the preprocessing contract: *``Resize length so user equals Sarah (Pearson requires equal array lengths: using linear interpolation)''*.

To demonstrate this preprocessing step, Slides 12--18 present a concrete worked example (``VD1''):
- Input User array: $\text{User} = [40, 90, 100, 60, 120, 145]$ ($6$ points).
- Target Sarah array: $\text{Sarah} = [30, 100, 60, 80]$ ($4$ points).

The engineering goal is to resample the 6-point User array down to 4 points to match Sarah. Mapping both sequences onto a normalized continuous coordinate $x \in [0, 1]$:
- The 6 User points are located at uniform coordinates $x \in \{0.0, 0.2, 0.4, 0.6, 0.8, 1.0\}$.
- The 4 Sarah target points are located at $x \in \{0.0, 0.33, 0.67, 1.0\}$.

Slides 14--17 print the exact arithmetic executed for each target index:
1. **At $x = 0.0$ (Slide 14):** $\text{User}[0] = 40$.
2. **At $x = 0.33$ (Slide 15):** The target coordinate $0.33$ lies in the interval $[0.2, 0.4]$ between $\text{User}(0.2) = 90$ and $\text{User}(0.4) = 100$. The fractional distance across the sub-interval is $\alpha = \frac{0.33 - 0.20}{0.40 - 0.20} = \frac{0.13}{0.20} = 0.65$. The interpolated value is:
   $$\text{User}[1] = 90 + 0.65 \times (100 - 90) = 90 + 6.5 = 96.5$$
3. **At $x = 0.67$ (Slide 16):** The target coordinate $0.67$ lies in the interval $[0.6, 0.8]$ between $\text{User}(0.6) = 60$ and $\text{User}(0.8) = 120$. The fractional distance across the sub-interval is $\alpha = \frac{0.67 - 0.60}{0.80 - 0.60} = \frac{0.07}{0.20} = 0.35$. The interpolated value is:
   $$\text{User}[2] = 60 + 0.35 \times (120 - 60) = 60 + 21.0 = 81.0$$
4. **At $x = 1.0$ (Slide 17):** The terminal sample is assigned directly: $\text{User}[4] = 145$ (labeled as $\text{User}[4]$ on Slide 17, corresponding to the final target sample).

On Slide 18, the resulting resampled array is printed in full:
$$\text{User_{resized}} = [40, 96.5, 81, 145]$$

**Convention Note on VD1:** The slide states the interpolation factors $0.65$ and $0.35$ directly. While the exact node-endpoint convention in Python code (e.g., `np.interp` endpoints versus discrete coordinate rounding) is underspecified in the slide text, the printed arithmetic corresponds precisely to linear interpolation at normalized coordinates $x = 0.33$ and $x = 0.67$. Slide 18 concludes with the candid operational note: *``Asking the chatbot to explain makes it easier to understand''*.

**Part 2: The Sliding Window Model (Slides 19--23).** Rather than computing a single global Pearson correlation across the entire sentence, the group introduced an analytical sliding window model (Slides 19--22) to localize prosodic evaluation. The formulation establishes four parameters:
- $N$: total length of the sentence (in samples or frames).
- $K$: number of orthographic words in the sentence prompt.
- $W$: analysis window size (in samples or frames).
- $S$: window shift step (stride).

On Slides 20--22, the group adopts the specific parameterization: *``Assuming $S = W / 2$, we slide $K + 1$ times (instructor proposal)''*. Setting the stride to a $50\%$ overlap ($S = W/2$), covering the full sentence length $N$ in exactly $K+1$ overlapping windows yields the geometric sizing identity:
$$N = W + K \times S \iff N = W + K \times \left(\frac{W}{2}\right) = W \left(1 + \frac{K}{2}\right) = W \left(\frac{K+2}{2}\right)$$

Solving algebraically for window width $W$ yields:
$$W = \frac{2N}{K+2}, \qquad S = \frac{W}{2} = \frac{N}{K+2}$$

**The Group Condemnation Rule.** On Slide 23, the group couples this window geometry with an explicit scoring decision rule:
> *``If any window has $r < 0.3$, then all words falling on that window are marked incorrect, even if they also fall on another window with $r \ge 0.3$.''*

Under this rule, a threshold of $r = 0.3$ serves as the boundary between acceptable intonation and error. Crucially, the rule is asymmetrical and condemnatory: if a word spans across multiple overlapping windows, any single window dropping below $0.3$ permanently stains and fails all overlapping words, regardless of high correlation in neighboring windows.

```
====================================================================================================
Figure 1.6a: The Sliding Window Contract and Group Condemnation Rule
Sentence Timeline: N frames across K = 3 Words ("READ THE BOOK")
Window Size: W = 2N / (K+2) = 0.40N | Stride: S = W / 2 = 0.20N | Total Windows: K + 1 = 4
----------------------------------------------------------------------------------------------------
Spoken Words:   [--- Word 1: "READ" ---] [--- Word 2: "THE" ---] [--- Word 3: "BOOK" ---]
Timeline:       0.00N                  0.33N                   0.67N                    1.00N

Window 1:       [====== Window 1: [0.00N, 0.40N] ======]   (r1 >= 0.3 -> Pass)
Window 2:                  [====== Window 2: [0.20N, 0.60N] ======]   (r2 < 0.3 -> FAIL!)
Window 3:                             [====== Window 3: [0.40N, 0.80N] ======]   (r3 >= 0.3 -> Pass)
Window 4:                                        [====== Window 4: [0.60N, 1.00N] ======]   (r4 >= 0.3)

Group Condemnation Rule:
Because Window 2 drops below r = 0.3, BOTH Word 1 and Word 2 are stained and marked incorrect,
even though Word 1 also overlaps Window 1 where r1 >= 0.3!
====================================================================================================
```

### Meeting 18/09/2026: Pitch Grid Regularity and Praat Centering Verification (Slides 24--30)

The third meeting investigates the temporal regularity of the extracted pitch grid under the title *``PITCH ARRAY EVENLY DISTRIBUTED AT 0.01s: To ensure that linear interpolation can be applied soundly''* (Slide 24).

Slide 25 formulates an empirical question based on a real test file:
> *``Proving pitch values recorded by Praat are spaced at 0.01s (One might wonder why, with 0.01s spacing and a 1.450667s audio duration, one would expect 145 pitch points starting from 0.01, 0.02, 0.03, ...)...''*

When parsing a reference audio recording of duration $T_{\text{audio}} = 1.450667\text{ s}$ (Slide 25), Praat extracts exactly $142$ pitch points, spaced at regular $0.01\text{ s}$ increments.

**Checking the Praat Manual.** Slide 26 cites the Praat documentation ([Intro 4.2 Configuring the pitch contour](https://www.fon.hum.uva.nl/praat/manual/Intro_4_2__Configuring_the_pitch_contour.html)) and Parselmouth. Opening the Praat manual reveals the exact sizing formulas:
> *``If the pitch floor is 50 Hz, the pitch analysis method requires a 60-millisecond analysis window, i.e., in order to measure the F0 at a time of, say, 0.850 seconds, Praat needs to consider a part of the sound that runs from 0.820 to 0.880 seconds. These 60 milliseconds correspond to 3 maximum pitch periods (3/50 = 0.060).''*

The manual specifies:
$$\text{Analysis Window Length} = \frac{3}{\text{pitch\_floor}}$$

For the group's default pitch floor of $75\text{ Hz}$, the analysis window is:
$$T_{\text{window}} = \frac{3}{75} = 0.040\text{ s} = 40\text{ ms}$$

**Discrepancy Note on Slide 27:** Slide 27 states: *``Pitch floor = 75Hz => T = 1 / 75 = 0.04s (analysis window length)''*. Notice that $1 / 75 \approx 0.013333\dots\text{ s} \ne 0.04\text{ s}$. The formula printed on Slide 27 contains a typographical error in the numerator ($1/75$ instead of $3/75$), but the calculated duration $0.04\text{ s}$ is mathematically identical to the Praat manual's 3-period identity $3/75 = 0.04\text{ s}$.

Furthermore, the Praat manual for `Sound: To Pitch...` defines the default time step (hop):
$$\Delta t = \frac{0.75}{\text{pitch\_floor}} = \frac{0.75}{75} = 0.010\text{ s} = 10\text{ ms}$$

**Reconstructing the 142-Point Count and Centering Offset.** Slides 28--30 trace the arithmetic:
1. **Interior Span for Complete Windows (Slide 28):** For an analysis window of length $0.04\text{ s}$ to lie entirely within the audio bounds $[0, 1.450667\text{ s}]$, the span available for window centers is:
   $$T_{\text{interior}} = 1.450667\text{ s} - 0.040000\text{ s} = 1.410667\text{ s}$$
2. **Number of Steps and Point Count (Slide 29):** With a time step of $\Delta t = 0.01\text{ s}$, the number of full steps is:
   $$\text{Hops} = \left\lfloor \frac{1.410667}{0.01} \right\rfloor = 141 \implies \text{Total Points} = 141 + 1 = 142\text{ points}$$
3. **Centering Offset (Slide 30):** The 141 hops span $141 \times 0.01 = 1.410000\text{ s}$, leaving a residual:
   $$T_{\text{residual}} = 1.410667\text{ s} - 1.410000\text{ s} = 0.000667\text{ s}$$
   Praat's centering mechanism splits this residual equally between the beginning and the end of the file (Slide 30):
   $$\text{Centering Offset} = \frac{0.000667\text{ s}}{2} = 0.00033\text{ s}$$
   The center of the first window is located at half the window length plus this centering offset:
   $$t_1 = \frac{T_{\text{window}}}{2} + \text{Centering Offset} = \frac{0.04}{2} + 0.00033 = 0.02033\text{ s}$$
   This accounts for why the pitch grid starts at $t_1 \approx 0.02033\text{ s}$ rather than $0.01\text{ s}$, directly explaining the framing mechanism analyzed on Slides 25--30.

### Meeting 23/09/2026: Rounding Discrepancy Budget and Edge Behavior (Slides 31--32)

The final presentation examines numerical edge effects under the title: *``ARISING ISSUES (THIS PART IS NOTED FOR PAPER WRITING; IN IMPLEMENTATION, PYTHON AUTOMATICALLY HANDLES TRUNCATION)''* (Slide 31).

Slide 32 considers a concrete scenario:
- Reference audio (Sarah): $T_1 = 1.42\text{ s}$, $n_1 = 139$ pitch points.
- Learner audio (User): $T_2 = 2.00\text{ s}$, with point count labeled as `n1 = 196` on the slide.

**Typographical Note on Slide 32:** The slide prints *``T2 = 2s, n1 = 196''*, duplicating the variable name $n_1$ instead of labeling the User point count as $n_2 = 196$.

The slide then computes an effective rescaled temporal step:
$$\theta = \frac{T_1}{n_2} = \frac{1.42\text{ s}}{196} = 0.0072448979\dots\text{ s} \approx 0.007\text{ s}$$
(Note: the slide prints the formula symbol as $\theta = \frac{T_2}{n_1} = 0.00724489\text{s}$, swapping variable indices in the formula while correctly evaluating $1.42 / 196$).

**The Truncation Budget.** Slide 32 examines what occurs if $\theta$ is rounded or truncated to three decimal places ($0.007\text{ s}$):
1. Reconstructed duration across 196 samples:
   $$T_{\text{reconstructed}} = 196 \times 0.007\text{ s} = 1.372\text{ s}$$
2. Temporal discrepancy between Sarah's original audio and the rescaled representation:
   $$\Delta T = 1.420\text{ s} - 1.372\text{ s} = 0.048\text{ s}$$
3. Discrepancy expressed in standard $0.01\text{ s}$ pitch frames:
   $$\text{Missed Frames} = \frac{1.420\text{ s} - 1.372\text{ s}}{0.01\text{ s}} = \frac{0.048\text{ s}}{0.01\text{ s}} = 4.8\text{ points}$$

Slide 32 concludes: *``Misses approximately $(1.42 - 1.372) / 0.01 = 4$ to $5$ pitch points $\implies$ Thus approximating will miss or leave surplus points. We treat this as an allowable error tolerance.''*

**Laboratory Recomputation for Duration $2.00\text{ s}$.** To cross-check framing behavior on a $2.00\text{ s}$ audio under the verified 18/09 framing setup (pitch floor $75\text{ Hz}$, window $0.04\text{ s}$, hop $0.01\text{ s}$):
$$T_{\text{interior}} = 2.000000\text{ s} - 0.040000\text{ s} = 1.960000\text{ s}$$
The number of hops is:
$$\text{Hops} = \frac{1.960000}{0.01} = 196 \implies \text{Total Points} = 196 + 1 = 197\text{ points}$$
Crucially, Slide 32's $n_2 = 196$ and this laboratory count of $197$ represent two distinct constructions. The count of $196$ on Slide 32 is an assumed scenario parameter chosen to demonstrate the arithmetic effect of three-decimal step truncation ($\theta \approx 0.007\text{ s}$). In contrast, $197$ is the sample count obtained when strictly applying the verified 18/09 window length ($0.04\text{ s}$) and hop cadence ($\lfloor 1.96 / 0.01 \rfloor + 1$) to a $2.00\text{ s}$ audio.

---

## 1.6.2 What That Contract Already Buys

A critical responsibility of any incoming researcher joining an active project is to understand what the existing design already achieves before analyzing unhandled edge cases. A reader who only encounters open cases risks forming the mistaken impression that the pipeline was arbitrary or deficient. In reality, the contract constructed across the September 2026 slides establishes several profound engineering advantages:

1. **Minimal Computational Complexity (Slides 5, 11):** Evaluating linear interpolation (`np.interp`) and Pearson correlation requires only 1D scalar accumulation, closed-form multiply-accumulate (MAC) operations, and a single square root. This closed-form arithmetic avoids iterative optimization, dynamic programming grids, and large memory buffers, operating with minimal compute demands on an edge device.
2. **Invariance to Vocal Register and Dynamic Range (Slides 6, 8):** By subtracting means ($\bar{x}, \bar{y}$) and dividing by standard deviations ($\sigma_X, \sigma_Y$), the metric decouples evaluation from absolute pitch magnitude and dynamic excursion range (Slides 6, 8). As the slides emphasize, subtracting the mean eliminates differences in absolute pitch between high-pitched and low-pitched voices (Slide 6), while dividing by standard deviations normalizes dynamic pitch excursion (Slide 8), allowing direct comparison across different vocal registers.
3. **Zero Training Pipeline and Zero Weight Footprint (Slides 2, 10):** Unlike neural acoustic models that demand gigabytes of training data, CTC loss alignments, and megabytes of on-chip weight storage, the Pearson sliding window operates entirely as a closed-form deterministic algorithm. It requires zero training epochs, zero parameter storage, and zero memory thrashing.
4. **Self-Contained Word Localization Without Forced Alignment (Slides 19--23):** Deploying an external forced aligner (such as a Kaldi or Montreal Forced Aligner pipeline) introduces heavy phonetic dictionaries, G2P converters, and acoustic hidden Markov models. The group's analytical formula ($W = 2N/(K+2)$ with $S = W/2$) provides an elegant geometric proxy that localizes scores along the utterance timeline using only the word count $K$.
5. **Empirically Verified Framing Infrastructure (Slides 24--30):** The team conducted rigorous signal-level validation of Praat's framing mechanics, verifying the analysis window ($40\text{ ms}$), the hop cadence ($10\text{ ms}$), and the sub-millisecond boundary centering ($0.00033\text{ s}$). This empirical discipline provides a solid foundation for any subsequent signal-processing expansion.

---

## 1.6.3 Open Cases in the Evaluation Pipeline

Having identified the core strengths of the contract, we turn to the open cases where physical speech dynamics diverge from the operational assumptions of the slides.

**Independence of the Open Cases.** It is vital to recognize that the four open cases detailed below are **mutually independent**. They do not stem from a single shared bug; rather, each case addresses an independent dimension of the speech signal. Resolving unvoiced frames (Case 3) does not resolve non-linear tempo variations (Case 2); localizing acoustic word edges (Case 4) does not verify whether the learner pronounced the correct vowel formants (Case 1). Each case must be evaluated on its own mathematical merits.

In this section, we do not propose a dynamic time warping (DTW) solution or pre-empt the team's architectural choices; we strictly document the assumption, the uncovered physical reality, the consequence of the current rule, the meeting question, and assign one of two engineering labels: **patch this line** or **replace this line**.

### Open Case 1: The Measure is Pitch Trend, Not Phonetic Identity

1. **Assumption Used on the Slides (Slides 2, 5):** The pipeline assumes that evaluating Pearson correlation on fundamental frequency ($F_0$) over time is sufficient to verify whether a learner read the prompt correctly (*``checking whether the user reads like the model''*, Slide 2).
2. **Physical Case Not Covered by This Assumption:** Human speech acoustics decouple the vocal source (fundamental frequency $F_0$, determined by vocal fold vibration) from the vocal tract filter (formant resonances $F_1, F_2, F_3, \dots$, determined by the tongue, jaw, and lip geometry). Pearson correlation on pitch evaluates only whether the speaker's vocal folds tensed and relaxed in directional harmony with the reference. It is completely blind to spectral formant envelopes.
   Consequently, this assumption fails to cover two common student behaviors:
   - *Humming Exploits:* A student can keep their mouth entirely closed and hum the rising and falling melody of the sentence without articulating a single consonant or vowel.
   - *Phonetic Substitutions with Matching Intonation:* A student reciting an entirely incorrect sentence (for example, saying *``I hate that dog''* instead of *``I love this cat''*) with the same declarative pitch trajectory will produce a nearly identical pitch sequence $X$.
3. **What the Current Rule Would Do:** Because the pitch trajectory matches Sarah's intonation trend, the numerator $\sum (x_i - \bar{x})(y_i - \bar{y})$ remains strongly positive, yielding $r \ge 0.3$. The current rule assigns a passing score to hummed audio or completely incorrect words.
4. **Meeting Question for the Group:** Does the research group intend for pitch Pearson correlation to serve as a complete standalone pronunciation scoring engine, or is it envisioned strictly as an auxiliary prosody score layered on top of an independent acoustic phonetic recognizer?
5. **Engineering Label:** **replace this line**. Pitch correlation cannot verify phonetic identity; evaluating whether the learner articulated the prompt requires an acoustic spectral metric (such as spectral distance or phonetic log-likelihoods).

### Open Case 2: Equal Index After Linear Resize Is Not the Same Place in the Sentence

1. **Assumption Used on the Slides (Slide 11):** The pipeline assumes that global linear interpolation (`np.interp`) mapping the learner's pitch array to match the length of Sarah's pitch array aligns corresponding phonetic moments across the sentence.
2. **Physical Case Not Covered by This Assumption:** Human speech rate is fundamentally non-uniform. When a non-native learner hesitates, prolongs a challenging vowel, or pauses before an unfamiliar word, the temporal expansion is concentrated entirely on that specific phoneme, while the remainder of the sentence may be spoken at normal speed.
   For example, consider a learner saying *``Gooood... morning''* ($1.8\text{ s}$) where the vowel $/u/$ in ``Good'' is prolonged across $60\%$ of the utterance, compared to an instructor saying *``Good morning''* ($1.0\text{ s}$) where ``Good'' occupies only $35\%$ of the utterance.
3. **What the Current Rule Would Do:** Global linear interpolation stretches or compresses all intervals uniformly. Because the learner's first word was elongated, uniform downsampling forces the tail of the learner's first word into the temporal slot occupied by Sarah's second word.
   At normalized frame $k = 45$, the learner is still concluding the rising intonation of ``Good'' ($\Delta x > 0$), while Sarah is already descending on the unaccented syllable of ``morning'' ($\Delta y < 0$). Multiplying these opposing slopes yields:
   $$(x_{45} - \bar{x})(y_{45} - \bar{y}) < 0$$
   This phase inversion forces the covariance negative ($r < 0$). Even though the student pronounced both words with excellent native-like intonation, the rigid uniform ruler produces a catastrophic false negative failure.
4. **Meeting Question for the Group:** How should the pipeline decouple local speaking rate variations from prosodic evaluation? Should the alignment mechanism allow non-linear temporal elasticity to absorb vowel stretching before computing intonation correlation?
5. **Engineering Label:** **replace this line**. Uniform linear interpolation is structurally incapable of mapping non-linearly distorted acoustic timelines onto one another.

### Open Case 3: The Numeric State of Unvoiced Frames

1. **Assumption Used on the Slides (Slide 5):** The Pearson formula assumes that $X = \{x_1, \dots, x_n\}$ and $Y = \{y_1, \dots, y_n\}$ are dense, continuous, well-defined real-valued vectors across all frames $i \in \{1, \dots, n\}$.
2. **Physical Case Not Covered by This Assumption:** Speech is not continuously periodic. Consonants such as unvoiced fricatives (/s/, /sh/, /f/), unvoiced plosive closures and bursts (/p/, /t/, /k/), and inter-word pauses involve no vocal fold vibration. During these intervals, fundamental frequency $F_0$ is physically non-existent.
3. **What the Current Rule Would Do:** The slide deck does not state how the group's Python baseline treats unvoiced frames. Opening the Praat manual indicates that Praat flags unvoiced frames as undefined. In numerical implementations, this leads to three unhandled failure modes:
   - *If unvoiced frames are stored as `NaN`:* Any sum $\sum (x_i - \bar{x})$ containing a `NaN` propagates across all accumulators, resulting in $r = \text{NaN}$ and crashing downstream comparators.
   - *If unvoiced frames are filled with $0.0\text{ Hz}$:* A jump from $0.0\text{ Hz}$ to a voiced pitch of $150\text{ Hz}$ represents an artificial delta of $150\text{ Hz}$. These massive artificial discontinuities completely dominate the variance sums $\sum (x_i - \bar{x})^2$, distorting the Pearson correlation into a measure of silence overlap rather than intonation trend.
   - *If unvoiced frames are deleted:* Deleting unvoiced frames destroys the uniform $0.01\text{ s}$ temporal grid, making linear interpolation geometrically invalid.
4. **Meeting Question for the Group:** What is the formal specification for unvoiced frames in the group's Python code? When Praat marks a frame as undefined or voiceless, should the implementation drop missing frames, keep a sentinel value, or skip the window entirely?
5. **Engineering Label:** **patch this line**. This is a patch because the slides currently leave unvoiced frame behavior underspecified; the patch consists of formally writing the missing unvoiced handling rule into the Python implementation without altering the overall pipeline architecture.

### Open Case 4: Window Staining Cascades and the Rounding Residual

1. **Assumption Used on the Slides (Slides 20--23, 32):** The sliding window formula $W = 2N/(K+2)$ with $50\%$ stride ($S = W/2$) accurately isolates word-level mistakes, and the 4-to-5 frame discrepancy identified on Slide 32 is an allowable engineering tolerance (*``allowable error tolerance''*).
2. **Physical Cases Not Covered by This Assumption:**
   - *Acoustic Window Staining:* Geometric windows sized purely by total sentence length $N$ and word count $K$ assume that all words have identical durations. In real language, English words vary wildly in duration: short monosyllabic function words (``a'', ``in'', ``the'') contrast sharply with extended polysyllabic content words (``pronunciation'', ``extraordinary''). Fixed geometric windows inevitably cut across acoustic word boundaries. An intonation error occurring strictly within Word~2 will spill across both Window~2 and Window~3.
   - *The Rounding Residual:* Truncating the effective rescaled step $\theta$ to three decimal places ($0.007\text{ s}$) produces a $4\text{ to }5\text{ frame}$ ($40\text{ to }50\text{ ms}$) drift over the sentence (Slide 32), shifting window boundaries unpredictably relative to phonemes.
3. **What the Current Rule Would Do:** Under the Group Condemnation Rule (Slide 23):
   > *``If any window has $r < 0.3$, then all words falling on that window are marked incorrect, even if they also fall on another window with $r \ge 0.3$.''*
   Because Window~2 drops below $0.3$, Word~1 and Word~2 are marked incorrect. Because Window~3 also drops below $0.3$, Word~2 and Word~3 are marked incorrect. A single localized prosodic error on Word~2 thus stains and fails all three words in the sentence. Compounding this, the $4\text{ to }5\text{ frame}$ rounding residual documented on Slide 32 shifts the artificial geometric cut points by up to half the duration of a short function word.
4. **Meeting Questions for the Group:**
   - *On Window Staining:* Should the synthetic geometric window formula be replaced by acoustic word boundaries obtained from an upstream forced aligner, and should the binary condemnation rule be relaxed to proportional overlap credit?
   - *On the Rounding Residual:* Should the Python framing arithmetic retain full floating-point time step precision rather than truncating $\theta$ to three decimal places?
5. **Engineering Labels:**
   - **Window Staining:** **replace this line**. Sizing windows by a synthetic geometric formula cannot track variable acoustic word durations. Replacing this line with acoustic forced alignment introduces real word boundaries; an aligner is an architectural replacement of the windowing line, not a patch.
   - **Rounding Residual:** **patch this line**. Retaining floating-point precision for the time step $\theta$ rather than truncating to three decimals ($0.007\text{ s}$) is a local arithmetic patch that preserves the existing framing structure without altering the pipeline architecture.

---

## 1.6.4 Stages the Report Does Not Contain, and Four Unchosen Candidates

### Flow Stages Not Contained in the Report
Reviewing the five-stage architecture established in Section~1.6.0 confirms that the group report focuses specifically on Stage~4 and an initial rule in Stage~5. The pipeline does not contain the following operational stages:
1. **Stage 1: Upstream Audio Conditioning and Dynamic VAD.** The slides operate on a pre-trimmed static reference recording (Slide 25). The report does not contain real-time Voice Activity Detection to crop user pauses, DC bias filters, or automated energy normalization to handle low-cost USB edge microphones.
2. **Stage 2: Acoustic Forced Alignment.** The report does not include a phone- or word-level aligner (such as an HMM-GMM Viterbi decoder or CTC forced aligner). Word segmentation is performed entirely geometrically via the $K+1$ window formula ($W = 2N/(K+2)$).
3. **Stage 3: Spectral Phoneme Quality Verification.** The report does not evaluate vocal tract filter properties (formants $F_1, F_2, F_3$) or acoustic model posteriors. Spectral phone correctness is assumed to correlate with fundamental frequency trajectory.
4. **Stage 5: Composite Pedagogical Rubric Calibration.** While the report establishes the $r < 0.3$ threshold on Slide 23, it does not define how prosodic correlation combines with phonetic accuracy, lexical stress, or speaking rate to produce a calibrated pedagogical rubric.

### Four Architecture Candidates Under Uniform Evaluation Axes

To provide the research group with actionable engineering pathways without pre-judging the outcome, we evaluate four distinct architectural candidates. Each candidate is examined across the exact same four analytical axes:
- **Axis 1 (Preserved Group Idea):** The core principles and components of the September 2026 contract retained.
- **Axis 2 (Open Cases Covered):** Which of the four independent open cases (Section~1.6.3) the candidate resolves.
- **Axis 3 (Output Granularity):** The resolution of feedback delivered to the student (sentence-level, window-level, word-level, or phoneme-level).
- **Axis 4 (Compute Profile and Hardware Profile):** The algorithmic complexity and compute requirements, accompanied by a concise one-phrase characterization of FPGA mapping.

#### Candidate A: Keep the Contract
- **Axis 1 (Preserved Group Idea):** Full slide contract. Retains global linear interpolation (`np.interp`), the $K+1$ sliding window geometry ($W = 2N/(K+2)$), Praat $0.01\text{ s}$ framing, and the Group Condemnation Rule ($r < 0.3$).
- **Axis 2 (Open Cases Covered):** Covers none of the four open cases. The pipeline treats the $4\text{ to }5$ frame rounding discrepancy documented on Slide 32 as an allowable engineering tolerance (*``allowable error tolerance''*).
- **Axis 3 (Output Granularity):** Coarse window-level pass/fail status mapped to overlapping word groups.
- **Axis 4 (Compute Profile):** Minimal compute. Composed entirely of $\mathcal{O}(N)$ 1D scalar interpolations, closed-form multiply-accumulate (MAC) operations, and a single square root. On FPGA, it maps to lightweight arithmetic logic without large memory buffers.

#### Candidate B: Add Word Edges, Then Pearson Per Word
- **Axis 1 (Preserved Group Idea):** Pitch Pearson and Sarah reference ruler preserved. Retains Praat pitch extraction, Pearson intonation correlation, and comparative scoring against Sarah. Replaces the synthetic geometric windows ($W = 2N/(K+2)$) with acoustic word boundaries obtained from an upstream aligner.
- **Axis 2 (Open Cases Covered):** Resolves Open Case 4 window staining completely: each word is evaluated strictly within its true acoustic boundaries $[t_{\text{start}}, t_{\text{end}}]$, eliminating cross-word staining. Partially mitigates Open Case 2 at word boundaries, but does not resolve sub-word non-uniform vowel stretching. Leaves Open Case 1 (phone identity), Case 3 (unvoiced handling), and the Case 4 rounding residual open.
- **Axis 3 (Output Granularity):** True word-level score ($K$ independent numerical correlation scores).
- **Axis 4 (Compute Profile):** Moderate compute. Executes one upstream forced alignment pass to obtain word boundaries, then performs $K$ short Pearson calls on word intervals. On FPGA, word boundary timestamps must be streamed from an upstream model or host processor.

#### Candidate C: Replace Only the Resize Line (Elastic Align, Then Pearson on Path)
- **Axis 1 (Preserved Group Idea):** Comparative prosodic scoring against Sarah and the Pearson intonation metric preserved. Replaces only the global linear interpolation line (`np.interp`) with non-linear dynamic time warping along an elastic path $\mathcal{P}$.
- **Algorithmic Formulation:** For learner sequence $X$ of length $N$ and reference sequence $Y$ of length $M$, local cost is computed as Euclidean distance $d(i, j) = \|x_i - y_j\|$. The accumulated cost grid satisfies the standard dynamic programming recurrence:
  $$D(i, j) = d(i, j) + \min\big(D(i-1, j),\, D(i, j-1),\, D(i-1, j-1)\big)$$
  Tracing the optimal warping path $\mathcal{P} = ((i_1, j_1), \dots, (i_L, j_L))$ from $(1, 1)$ to $(N, M)$ elastically aligns corresponding acoustic events. Pearson intonation correlation is subsequently evaluated strictly along the reindexed warping path $\mathcal{P}$.
- **Axis 2 (Open Cases Covered):** Resolves Open Case 2 (Equal Index After Resize) by elastically absorbing local vowel stretching and pauses, completely preventing false negative phase inversions ($r < 0$). When paired with a mutually voiced frame mask, it isolates Open Case 3. However, it does not resolve Open Case 1 unless multi-dimensional spectral features are incorporated into local distance $d(i, j)$.
- **Axis 3 (Output Granularity):** Frame-level alignment path mapped into localized window or word scores.
- **Axis 4 (Compute Profile):** Moderate compute. Evaluates an $N \times M$ dynamic programming recurrence grid ($250,000\text{ cells}$ for a 5-second sentence). On FPGA, it maps to a streaming hardware pipeline without requiring external memory.

#### Candidate D: Replace the Measure (Goodness of Pronunciation or Acoustic Embeddings)
- **Axis 1 (Preserved Group Idea):** High-level goal of automated English pronunciation assessment preserved. Replaces pitch Pearson correlation with acoustic model posterior probabilities (Goodness of Pronunciation, GOP) or self-supervised speech representation embeddings (e.g., wav2vec 2.0 or Conformer representations).
- **Axis 2 (Open Cases Covered):** Resolves Open Case 1 (Phone Correctness) directly by evaluating spectral acoustic log-likelihoods, resolves Open Case 3 natively (neural acoustic models handle voiced and unvoiced frames inherently), and provides intrinsic phonetic forced alignment.
- **Axis 3 (Output Granularity):** Fine-grained phoneme-level, syllable-level, and word-level posterior scores.
- **Axis 4 (Compute Profile):** High compute. Demands full neural network forward inference, multi-megabyte parameter storage, and intensive matrix-vector multiplications. On FPGA, it requires a dedicated deep learning neural network accelerator core and an extensive ongoing engineering burden to train, prune, and maintain the acoustic model.

**Explicit Neutrality Note:** We emphasize that Candidate~C is not declared the winner, nor is Candidate~A rejected as incorrect. If the project's computational budget is severely restricted and learners are instructed to match a fixed metronome cadence, Candidate~A provides an exceptionally lightweight baseline. If phoneme verification is paramount, Candidate~D is mandatory despite its substantial model footprint. The choice between these four candidates belongs entirely to the research group.

---

## 1.6.5 The Group Meeting Decision Page

To facilitate a productive discussion in the upcoming research group meeting, the table below synthesizes the four architecture candidates. In accordance with the objective tone of this review, the final column is intentionally left blank for the team's collective decision.

| Candidate | Preserved Group Idea | Open Cases Covered | Output Grain | Compute Profile | FPGA Profile | Engineering Burden | Group Chooses |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **A: Keep Contract** | Full slide contract (linear resize, sliding windows, $r<0.3$ rule) | None (treats 4--5 frame residual as allowable error) | Coarse window pass/fail | Closed-form MACs, 1 sq-root | Lightweight arithmetic logic | Zero new software; code is complete | |
| **B: Add Word Edges** | Pitch Pearson and Sarah ruler preserved; replaces geometric windows | Case 4 staining (eliminates cross-word staining) | Word-level ($K$ scalar scores) | 1 aligner pass, $K$ short Pearson calls | Word timestamps streamed from host | Integrate forced aligner (MFA/Kaldi) or VAD segmentation | |
| **C: Elastic Alignment** | Pitch Pearson on warping path $\mathcal{P}$ preserved; replaces linear resize | Case 2 (absorbs vowel tempo), isolates Case 3 | Warped path $\to$ word/window | $N \times M$ DP grid ($2.5\times 10^5$ cells) | Streaming DP pipeline | Implement 2D DP matrix recurrence; define local metric | |
| **D: Replace Measure** | High-level goal preserved; replaces pitch correlation | Case 1 (phones), Case 3 (unvoiced), intrinsic alignment | Fine-grained phoneme posteriors | Neural forward inference (GEMMs) | Dedicated deep learning NPU accelerator | Train, prune, and quantize neural acoustic model (GOP/Conformer) | |

### Actionable Meeting Questions for the Group

The decision matrix reflects four concrete architectural crossroads. We submit the following questions, drawn directly from the open cases analyzed in Section~1.6.3, to guide the team's agenda:

1. **On Phonetic Scope (Open Case 1):** Is the current pipeline expected to detect unpronounced or substituted words independently, or is the edge voice system designed as a two-tier device where an upstream phoneme recognizer verifies phonetic correctness before passing pitch vectors to this stage?
2. **On Temporal Alignment (Open Case 2):** Does the group wish to preserve global linear interpolation by instructing students to adhere to a rigid metronome pace (Candidate~A), segment utterances by word boundaries (Candidate~B), or adopt elastic non-linear dynamic time warping (Candidate~C) to accommodate natural vowel prolongation?
3. **On Unvoiced Frame Specification (Open Case 3):** What precise mathematical rule will be committed to the Python codebase for unvoiced frames ($F_0 = 0$ or undefined)? Should the calculation drop missing frames, keep a sentinel value, or skip the window entirely?
4. **On Rubric Calibration (Open Case 4):** How should the team refine the Group Condemnation Rule? Should the binary fail condition ($r < 0.3$ condemns all overlapping words) be replaced by a proportional credit rule based on the percentage of overlap between word acoustic boundaries and sliding windows?
