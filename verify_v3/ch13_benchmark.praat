# verify_v3/ch13_benchmark.praat
# Praat 7.0.03 Benchmark and Extraction Script for Chapter 13
# Runs R1 (defaults) or R2 (zero octave-jump and V/UV cost) with internal stopwatch timing.
# Separates process startup time from pure algorithmic analysis time.
# Runs N iterations and calculates median execution time and Real-Time Factor (RTF).
#
# Usage:
#   praat_barren --run verify_v3/ch13_benchmark.praat sound.wav R1 20 > out_r1.tsv
#   praat_barren --run verify_v3/ch13_benchmark.praat sound.wav R2 20 > out_r2.tsv

form BenchmarkPitch
  sentence inFile synth_glide_vuv_16k.wav
  word mode R1
  integer nRuns 20
endform

# Configure cost parameters according to mode
if mode$ = "R1"
  jumpCost = 0.35
  vuvCost = 0.14
elsif mode$ = "R2"
  jumpCost = 0.0
  vuvCost = 0.0
else
  exitScript: "Unknown mode: " + mode$ + " (must be R1 or R2)"
endif

# Load sound file once into Praat memory
sound = Read from file: inFile$
duration = Get total duration

# Run N benchmark iterations using Praat internal stopwatch
# Excludes process invocation, dynamic library loading, and file I/O overhead
times# = zero# (nRuns)
for run from 1 to nRuns
  selectObject: sound
  stopwatch
  pitchTemp = To Pitch (raw autocorrelation): 0, 75, 600, 15, "no", 0.03, 0.45, 0.01, jumpCost, vuvCost
  elapsed = stopwatch
  times#[run] = elapsed
  removeObject: pitchTemp
endfor

# Sort run times to find median
sortedTimes# = sort# (times#)
if nRuns mod 2 = 1
  medianIdx = (nRuns + 1) / 2
  medianTime = sortedTimes#[medianIdx]
else
  idx1 = nRuns / 2
  idx2 = idx1 + 1
  medianTime = (sortedTimes#[idx1] + sortedTimes#[idx2]) / 2.0
endif

rtf = medianTime / duration

# Extract final Pitch track for frame-level evaluation
selectObject: sound
finalPitch = To Pitch (raw autocorrelation): 0, 75, 600, 15, "no", 0.03, 0.45, 0.01, jumpCost, vuvCost
nFrames = Get number of frames

# Print Benchmark Header to stdout (lines starting with # are comments)
appendInfoLine: "# PRAAT 7.0.03 BENCHMARK REPORT"
appendInfoLine: "# File: ", inFile$
appendInfoLine: "# Mode: ", mode$, " (octave_jump=", fixed$(jumpCost, 2), ", vuv=", fixed$(vuvCost, 2), ")"
appendInfoLine: "# Audio duration: ", fixed$(duration, 6), " s"
appendInfoLine: "# Iterations (N): ", nRuns
appendInfoLine: "# Min time: ", fixed$(sortedTimes#[1] * 1000.0, 3), " ms"
appendInfoLine: "# Median time: ", fixed$(medianTime * 1000.0, 3), " ms"
appendInfoLine: "# Max time: ", fixed$(sortedTimes#[nRuns] * 1000.0, 3), " ms"
appendInfoLine: "# Algorithmic RTF: ", fixed$(rtf, 6)
appendInfoLine: "# Total frames: ", nFrames
appendInfoLine: "# --- FRAME DATA (t [s], f0 [Hz]) ---"

for i from 1 to nFrames
  t = Get time from frame number: i
  f = Get value in frame: i, "Hertz"
  if f = undefined
    f = 0.0
  endif
  appendInfoLine: fixed$(t, 9), tab$, fixed$(f, 9)
endfor

removeObject: finalPitch
removeObject: sound
