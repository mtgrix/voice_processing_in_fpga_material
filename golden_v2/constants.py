"""Shared constants for golden_v2: everything derived from Praat 7.0.03 Sound_to_Pitch.cpp
with the standard settings (floor 75 Hz, ceiling 600 Hz, 3 periods, Hanning, fs = 16 kHz).

Line numbers refer to fon/Sound_to_Pitch.cpp at tag v7.0.03 (praat/praat master, Nov 2026).
"""
import math

FS = 16000
DX = 1.0 / FS                       # Praat: my dx
X1 = 0.5 / FS                       # Praat: Sound x1 = 0.5 * dx (Sound.cpp, Sound_createSimple)

PITCH_FLOOR = 75.0
PITCH_CEILING = 600.0
PERIODS_PER_WINDOW = 3.0
TIME_STEP = 0.75 / PITCH_FLOOR      # line 296: periodsPerWindow / floor / 4 = 0.01 s
HOP_NOMINAL = 160

# lines 326-339
NSAMP_PERIOD = math.floor(1.0 / DX / PITCH_FLOOR)            # 213
HALFNSAMP_PERIOD = NSAMP_PERIOD // 2 + 1                      # 107
DT_WINDOW = PERIODS_PER_WINDOW / PITCH_FLOOR                  # 0.04 s
_n = math.floor(DT_WINDOW / DX)                               # 640
HALFNSAMP_WINDOW = _n // 2 - 1                                # 319
NSAMP_WINDOW = HALFNSAMP_WINDOW * 2                           # 638
# lines 344-345
MINIMUM_LAG = max(2, math.floor(1.0 / DX / PITCH_CEILING))    # 26
MAXIMUM_LAG = min(math.floor(NSAMP_WINDOW / PERIODS_PER_WINDOW) + 2, NSAMP_WINDOW)  # 214
BRENT_IXMAX = math.floor(NSAMP_WINDOW * 0.5)                  # 319 (interpolation_depth 0.5)

# Mean span: rightSample - nsamp_period .. leftSample + nsamp_period  -> 2*213 = 426 samples
MEAN_SPAN = 2 * NSAMP_PERIOD                                  # 426
# Positions inside the 638-sample window (0-based), derived in frame_geometry()
MEAN_OFFSET = HALFNSAMP_WINDOW - NSAMP_PERIOD                 # 106 -> positions 106..531
LP_FIRST = HALFNSAMP_WINDOW + 1 - HALFNSAMP_PERIOD - 1        # 212 (0-based) lines 91-94
LP_LAST = HALFNSAMP_WINDOW + HALFNSAMP_PERIOD - 1             # 425 (0-based, inclusive)

# Praat defaults (praat_Sound.cpp, To Pitch (raw autocorrelation))
MAX_CANDIDATES = 15
SILENCE_THRESHOLD = 0.03
VOICING_THRESHOLD = 0.45
OCTAVE_COST = 0.01
OCTAVE_JUMP_COST = 0.35
VOICED_UNVOICED_COST = 0.14

# Hardware lag ranges
TAU_SCAN_MIN, TAU_SCAN_MAX = MINIMUM_LAG, MAXIMUM_LAG        # 26..214, 189 lags
TAU_SEARCH_MIN, TAU_SEARCH_MAX = MINIMUM_LAG + 1, MAXIMUM_LAG - 1   # 27..213
N_SCAN = TAU_SCAN_MAX - TAU_SCAN_MIN + 1                      # 189

# Fixed-point formats
W_FRAC = 15            # Hanning ROM Q1.15 (unsigned, max 32767)
C_FRAC = 14            # C[tau] ROM unsigned Q2.14
K_FRAC = 20            # octave-cost K[tau] ROM signed, scale 2^20
# Mean = floor((S + 213) / 426) computed as ((S + 213 + 426*2^15) * M_MEAN) >> K_MEAN, minus 2^15
M_MEAN, K_MEAN = 10_082_083, 32
MEAN_BIAS = MEAN_SPAN * (1 << 15)

assert (NSAMP_WINDOW, HALFNSAMP_WINDOW, NSAMP_PERIOD, HALFNSAMP_PERIOD) == (638, 319, 213, 107)
assert (MINIMUM_LAG, MAXIMUM_LAG, BRENT_IXMAX, MEAN_SPAN) == (26, 214, 319, 426)
assert (MEAN_OFFSET, LP_FIRST, LP_LAST) == (106, 212, 425)
