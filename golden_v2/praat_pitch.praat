# Usage: praat_barren --run praat_pitch.praat in.wav jumpCost vuvCost > out.tsv
# Praat 7.0.03 'To Pitch (raw autocorrelation)': time step 0 (auto = 10 ms), floor 75, ceiling 600,
# 15 candidates, very accurate off, silence 0.03, voicing 0.45, octave 0.01, octave-jump, V/UV.
form Pitch
  sentence inFile
  real jump 0.35
  real vuv 0.14
endform
s = Read from file: inFile$
p = To Pitch (raw autocorrelation): 0, 75, 600, 15, "no", 0.03, 0.45, 0.01, jump, vuv
n = Get number of frames
for i to n
  t = Get time from frame number: i
  f = Get value in frame: i, "Hertz"
  if f = undefined
    f = 0
  endif
  appendInfoLine: fixed$ (t, 9), tab$, fixed$ (f, 9)
endfor
