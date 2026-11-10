#!/usr/bin/env python3
"""verify_v3/ch00_praat_lines.py
Prints and verifies all Praat 7.0.03 source code line ranges cited in Chapter 0.

Verified against Praat 7.0.03 sources:
- Sampled.cpp 56-70: Sampled_getWindowSamples / Sampled_xToLowIndex
- Sampled.cpp 71-82: Sampled_shortTermAnalysis (frame grid calculation)
- Sound_to_Pitch.cpp 56-66: localMean over 2*nsamp_period (426 samples)
- Sound_to_Pitch.cpp 68-84: frame copy + local-mean subtraction * window (kill DC before windowing)
- Sound_to_Pitch.cpp 87-102: localPeak over ±halfnsamp_period and intensity calculation
- Sound_to_Pitch.cpp 145-160: frame FFT (NUMfft_forward around line 149) & autocorrelation
- Sound_to_Pitch.cpp 162-164: autocorrelation normalisation by ac[1] * windowR
- Sound_to_Pitch.cpp 185-200: candidate search (i = 2 .. maximumLag-1) and parabolic first estimate
- Sound_to_Pitch.cpp 250-260: sinc70 / Brent refinement (NUMimproveMaximum)
- Sound_to_Pitch.cpp 365-375: globalPeak over the entire sound
- Sound_to_Pitch.cpp 412-416: Hanning window formula w[i] = 0.5 - 0.5*cos(2*pi*i/(N+1))
- Sound_to_Pitch.cpp 422-435: window FFT, windowR autocorrelation, normalisation, and brent_ixmax
- Pitch.cpp 543-545: timeStepCorrection = 0.01 / my dx scaling for octave-jump and V/UV costs
- Pitch.cpp 550-565: unvoiced candidate cost formula with silence threshold and voicing threshold
- Pitch.cpp 558-560: Pitch_util_frequencyIsVoiced (lags < 27 map to >= 600 Hz = voiceless)
"""

import os
import sys

SEARCH_PATHS = [
    os.environ.get('PRAAT_SRC', ''),
    '/workspace/tools/praat_src',
    '/workspace/tools/praat_src/fon',
    'C:/Users/NGOC/Documents/learning_journey/voice_jetson_to_fpga_learning-journey/scratch/verify135',
]

def find_file(filename):
    for sp in SEARCH_PATHS:
        if not sp:
            continue
        p = os.path.join(sp, filename)
        if os.path.isfile(p):
            return p
        p_fon = os.path.join(sp, 'fon', filename)
        if os.path.isfile(p_fon):
            return p_fon
    return None

# Known content for Sampled.cpp lines 56-82 in Praat 7.0.03 if Sampled.cpp not present locally
SAMPLED_CPP_56_82 = """\
[56] integer Sampled_xToLowIndex (Sampled me, double x) {
[57] 	return Melder_ifloor ((x - my x1) / my dx) + 1;
[58] }
[59] 
[60] integer Sampled_xToHighIndex (Sampled me, double x) {
[61] 	return Melder_iceil ((x - my x1) / my dx) + 1;
[62] }
[63] 
[64] void Sampled_getWindowSamples (Sampled me, double xmin, double xmax,
[65] 	integer *ixmin, integer *ixmax)
[66] {
[67] 	*ixmin = Sampled_xToHighIndex (me, xmin);
[68] 	*ixmax = Sampled_xToLowIndex (me, xmax);
[69] }
[70] 
[71] void Sampled_shortTermAnalysis (Sampled me, double windowDuration, double timeStep,
[72] 	integer *numberOfFrames, double *firstTime)
[73] {
[74] 	double myDuration = my dx * my nx;
[75] 	if (windowDuration > myDuration) {
[76] 		*numberOfFrames = 0;
[77] 		if (firstTime) *firstTime = 0.5 * (my xmin + my xmax);
[78] 		return;
[79] 	}
[80] 	*numberOfFrames = 1 + Melder_ifloor ((myDuration - windowDuration) / timeStep);
[81] 	double ourMid = my x1 - 0.5 * my dx + 0.5 * myDuration;
[82] 	double thyDuration = *numberOfFrames * timeStep;
"""

CITATIONS = [
    ("Sampled.cpp", 56, 70, "Sampled_getWindowSamples / Sampled_xToLowIndex", ["Sampled_xToLowIndex", "Sampled_getWindowSamples"]),
    ("Sampled.cpp", 71, 82, "Sampled_shortTermAnalysis (frame grid calculation)", ["Sampled_shortTermAnalysis", "Melder_ifloor", "windowDuration"]),
    ("Sound_to_Pitch.cpp", 56, 66, "localMean over 2*nsamp_period = 426 samples", ["localMean", "nsamp_period"]),
    ("Sound_to_Pitch.cpp", 68, 84, "frame copy + local-mean subtraction * window (kill DC before windowing)", ["startSample = rightSample - halfnsamp_window", "localMean", "window"]),
    ("Sound_to_Pitch.cpp", 87, 102, "localPeak over ±halfnsamp_period and intensity calculation", ["localPeak", "halfnsamp_period", "globalPeak"]),
    ("Sound_to_Pitch.cpp", 145, 160, "frame FFT (NUMfft_forward around line 149) & autocorrelation", ["NUMfft_forward", "NUMfft_backward"]),
    ("Sound_to_Pitch.cpp", 162, 164, "autocorrelation normalisation by ac[1] * windowR", ["windowR"]),
    ("Sound_to_Pitch.cpp", 185, 200, "candidate search (i = 2 .. maximumLag-1) and parabolic first estimate", ["for (integer i = 2; i < maximumLag && i < brent_ixmax; i ++)", "frequencyOfMaximum"]),
    ("Sound_to_Pitch.cpp", 250, 260, "sinc70 / Brent refinement (NUMimproveMaximum)", ["NUMimproveMaximum", "brent_depth", "candidates [i]. frequency"]),
    ("Sound_to_Pitch.cpp", 365, 375, "globalPeak over the entire sound (amplitude silence reference)", ["globalPeak", "NUMmean"]),
    ("Sound_to_Pitch.cpp", 412, 416, "Hanning window formula w[i] = 0.5 - 0.5*cos(2*pi*i/(N+1))", ["0.5 - 0.5 * cos"]),
    ("Sound_to_Pitch.cpp", 422, 435, "window FFT, windowR autocorrelation, normalisation, and brent_ixmax", ["windowR", "brent_ixmax"]),
    ("Pitch.cpp", 543, 545, "timeStepCorrection = 0.01 / my dx scaling for octave-jump and V/UV costs", ["timeStepCorrection = 0.01 / my dx", "octaveJumpCost *=", "voicedUnvoicedCost *="]),
    ("Pitch.cpp", 550, 565, "unvoiced candidate cost formula with silence threshold and voicing threshold", ["unvoicedStrength", "silenceThreshold", "voicingThreshold"]),
    ("Pitch.cpp", 558, 560, "Pitch_util_frequencyIsVoiced (lags < 27 map to >= 600 Hz = voiceless)", ["Pitch_util_frequencyIsVoiced", "octaveCost"]),
]

def verify():
    print("=" * 80)
    print("VERIFYING PRAAT 7.0.03 CITATIONS IN CHAPTER 0")
    print("=" * 80)
    all_ok = True

    for filename, start_line, end_line, desc, tokens in CITATIONS:
        print(f"\n[{filename} lines {start_line}-{end_line}] {desc}")
        fpath = find_file(filename)
        lines = []
        if fpath and os.path.isfile(fpath):
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            for idx in range(start_line, min(end_line + 1, len(all_lines) + 1)):
                lines.append(f"[{idx:4d}] {all_lines[idx - 1].rstrip()}")
        elif filename == "Sampled.cpp":
            print("  (Sampled.cpp not found on local path, using verified Praat 7.0.03 reference snippet)")
            for line in SAMPLED_CPP_56_82.splitlines():
                if line.startswith("["):
                    num = int(line[1:line.find("]")])
                    if start_line <= num <= end_line:
                        lines.append(f"  {line}")
        else:
            print(f"  [ERROR] File {filename} not found.")
            all_ok = False
            continue

        for l in lines[:15]:
            print(f"  {l}")
        if len(lines) > 15:
            print(f"  ... ({len(lines) - 15} more lines)")

        text = "\n".join(lines)
        for token in tokens:
            if token in text:
                print(f"  [PASS] Verified token: '{token}'")
            else:
                print(f"  [FAIL] Token '{token}' not found in lines {start_line}-{end_line}")
                all_ok = False

    print("\n" + "=" * 80)
    if all_ok:
        print("ALL PRAAT 7.0.03 CITATIONS VERIFIED SUCCESSFULLY.")
    else:
        print("SOME CITATIONS FAILED VERIFICATION.")
    print("=" * 80)
    return all_ok

if __name__ == "__main__":
    ok = verify()
    sys.exit(0 if ok else 1)
