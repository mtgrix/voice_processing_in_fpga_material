"""Praat's frame grid (Sampled_shortTermAnalysis + Sampled_xToLowIndex), reproduced in IEEE double.

The HPS computes exactly this and tells the FPGA where each frame starts.
"""
import math
from constants import DX, X1, DT_WINDOW, TIME_STEP, HALFNSAMP_WINDOW, NSAMP_PERIOD


def frame_grid(nx: int, dt: float = TIME_STEP):
    """Return (t1, [t_k], [leftSample_k (1-based)]) exactly as Praat computes them."""
    my_duration = DX * nx                                   # Sampled.cpp line 74
    nframes = math.floor((my_duration - DT_WINDOW) / dt) + 1
    our_mid = X1 - 0.5 * DX + 0.5 * my_duration
    thy_duration = nframes * dt
    t1 = our_mid - 0.5 * thy_duration + 0.5 * dt
    times, lefts = [], []
    for i in range(1, nframes + 1):
        t = t1 + (i - 1) * dt                               # Sampled_indexToX
        left = math.floor((t - X1) / DX + 1.0)              # Sampled_xToLowIndex
        times.append(t)
        lefts.append(left)
    return t1, times, lefts


def window_start0(left_1based: int) -> int:
    """0-based index of the first of the 638 window samples (startSample = rightSample - 319)."""
    right = left_1based + 1
    return right - HALFNSAMP_WINDOW - 1


def mean_start0(left_1based: int) -> int:
    """0-based index of the first of the 426 local-mean samples (rightSample - 213)."""
    right = left_1based + 1
    return right - NSAMP_PERIOD - 1
