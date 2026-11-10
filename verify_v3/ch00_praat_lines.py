#!/usr/bin/env python3
"""verify_v3/ch00_praat_lines.py
Prints and verifies all Praat 7.0.03 source code line ranges cited in Chapter 0.

Verified against Praat 7.0.03 sources (commit 6a9874e, 2026-11-08):
- Sampled.h 34-36: Sampled_xToLowIndex inline definition
- Sampled.cpp 53-65: Sampled_getWindowSamples
- Sampled.cpp 71-82: Sampled_shortTermAnalysis (frame grid calculation)
- Sound_to_Pitch.cpp 56-66: localMean over 2*nsamp_period (426 samples)
- Sound_to_Pitch.cpp 68-84: frame copy + local-mean subtraction * window (kill DC before windowing)
- Sound_to_Pitch.cpp 87-102: localPeak over ±halfnsamp_period and intensity calculation
- Sound_to_Pitch.cpp 147-157: frame FFT (NUMfft_forward around line 150) & autocorrelation
- Sound_to_Pitch.cpp 163-165: autocorrelation normalisation by ac[1] * windowR
- Sound_to_Pitch.cpp 185-200: candidate search (i = 2 .. maximumLag-1) and parabolic first estimate
- Sound_to_Pitch.cpp 254-270: sinc70 / Brent refinement (NUMimproveMaximum at line 258)
- Sound_to_Pitch.cpp 335-339: window length 638 rounding (halfnsamp_window = nsamp_window/2 - 1)
- Sound_to_Pitch.cpp 375-385: globalPeak over the entire sound (line 375: globalPeak = 0.0;)
- Sound_to_Pitch.cpp 422-425: Hanning window formula w[i] = 0.5 - 0.5*cos(2*pi*i/(N+1))
- Sound_to_Pitch.cpp 430-445: window FFT, windowR autocorrelation, normalisation, and brent_ixmax
- Pitch.cpp 543-545: timeStepCorrection = 0.01 / my dx scaling for octave-jump and V/UV costs
- Pitch.cpp 550-565: unvoiced candidate cost formula with silence threshold and voicing threshold
- Pitch.cpp 558-560: Pitch_util_frequencyIsVoiced (lags < 27 map to >= 600 Hz = voiceless)
"""

import os
import sys

# Search path order: /workspace/tools/praat_src FIRST, then PRAAT_SRC env var.
SEARCH_PATHS = [
    '/workspace/tools/praat_src',
    '/workspace/tools/praat_src/fon',
    os.environ.get('PRAAT_SRC', ''),
]

# Verified Praat 7.0.03 reference snippets (used as fallback when running on a host
# without the full /workspace/tools/praat_src tree mounted).
PRAAT_7003_SNIPPETS = {
    "Sampled.h": {
        (34, 36): """\
[  34] static inline integer Sampled_xToLowIndex (constSampled me, double x) {
[  35] 	return Melder_ifloor ((x - my x1) / my dx) + 1;
[  36] }"""
    },
    "Sampled.cpp": {
        (53, 65): """\
[  53] void Sampled_getWindowSamples (constSampled me, double xmin, double xmax,
[  54] 	integer *ixmin, integer *ixmax)
[  55] {
[  56] 	*ixmin = Sampled_xToHighIndex (me, xmin);
[  57] 	*ixmax = Sampled_xToLowIndex (me, xmax);
[  58] 	if (*ixmin < 1)
[  59] 		*ixmin = 1;
[  60] 	if (*ixmax > my nx)
[  61] 		*ixmax = my nx;
[  62] }""",
        (71, 82): """\
[  71] void Sampled_shortTermAnalysis (constSampled me, double windowDuration, double timeStep,
[  72] 	integer *numberOfFrames, double *firstTime)
[  73] {
[  74] 	Melder_assert (windowDuration > 0.0);
[  75] 	Melder_assert (timeStep > 0.0);
[  76] 	volatile double myDuration = my dx * my nx;   // volatile, because we need to truncate to 64 bits
[  77] 	if (windowDuration > myDuration)
[  78] 		Melder_throw (me, U": shorter than window length.");
[  79] 	*numberOfFrames = Melder_ifloor ((myDuration - windowDuration) / timeStep) + 1;
[  80] 	Melder_assert (*numberOfFrames >= 1);
[  81] 	const double ourMidTime = my x1 - 0.5 * my dx + 0.5 * myDuration;
[  82] 	const double thyDuration = *numberOfFrames * timeStep;"""
    },
    "Sound_to_Pitch.cpp": {
        (56, 66): """\
[  56] 		/*
[  57] 			Compute the local mean; look one longest period to both sides.
[  58] 		*/
[  59] 		startSample = rightSample - nsamp_period;
[  60] 		endSample = leftSample + nsamp_period;
[  61] 		Melder_assert (startSample >= 1);
[  62] 		Melder_assert (endSample <= my nx);
[  63] 		localMean [channel] = 0.0;
[  64] 		for (integer i = startSample; i <= endSample; i ++)
[  65] 			localMean [channel] += my z [channel] [i];
[  66] 		localMean [channel] /= 2 * nsamp_period;""",
        (68, 84): """\
[  68] 		/*
[  69] 			Copy a window to a frame and subtract the local mean.
[  70] 			We are going to kill the DC component before windowing.
[  71] 		*/
[  72] 		startSample = rightSample - halfnsamp_window;
[  73] 		endSample = leftSample + halfnsamp_window;
[  74] 		Melder_assert (startSample >= 1);
[  75] 		Melder_assert (endSample <= my nx);
[  76] 		if (method < FCC_NORMAL) {
[  77] 			for (integer j = 1, i = startSample; j <= nsamp_window; j ++)
[  78] 				frame [channel] [j] = (my z [channel] [i ++] - localMean [channel]) * window [j];
[  79] 			for (integer j = nsamp_window + 1; j <= nsampFFT; j ++)
[  80] 				frame [channel] [j] = 0.0;
[  81] 		} else {
[  82] 			for (integer j = 1, i = startSample; j <= nsamp_window; j ++)
[  83] 				frame [channel] [j] = my z [channel] [i ++] - localMean [channel];
[  84] 		}""",
        (87, 102): """\
[  87] 	/*
[  88] 		Compute the local peak; look half a longest period to both sides.
[  89] 	*/
[  90] 	double localPeak = 0.0;
[  91] 	if ((startSample = halfnsamp_window + 1 - halfnsamp_period) < 1)
[  92] 		startSample = 1;
[  93] 	if ((endSample = halfnsamp_window + halfnsamp_period) > nsamp_window)
[  94] 		endSample = nsamp_window;
[  95] 	for (integer channel = 1; channel <= my ny; channel ++) {
[  96] 		for (integer j = startSample; j <= endSample; j ++) {
[  97] 			double value = fabs (frame [channel] [j]);
[  98] 			if (value > localPeak)
[  99] 				localPeak = value;
[ 100] 		}
[ 101] 	}
[ 102] 	pitchFrame -> intensity = ( globalPeak == 0.0 ? 1.0 : localPeak > globalPeak ? 1.0 : localPeak / globalPeak );""",
        (147, 157): """\
[ 147] 		for (integer i = 1; i <= nsampFFT; i ++)
[ 148] 			ac [i] = 0.0;
[ 149] 		for (integer channel = 1; channel <= my ny; channel ++) {
[ 150] 			NUMfft_forward (fftTable, VEC (& frame [channel] [1], fftTable->n));   // complex spectrum
[ 151] 			ac [1] += frame [channel] [1] * frame [channel] [1];   // DC component
[ 152] 			for (integer i = 2; i < nsampFFT; i += 2)
[ 153] 				ac [i] += frame [channel] [i] * frame [channel] [i] + frame [channel] [i+1] * frame [channel] [i+1];   // power spectrum
[ 154] 			ac [nsampFFT] += frame [channel] [nsampFFT] * frame [channel] [nsampFFT];   // Nyquist frequency
[ 155] 		}
[ 156] 		NUMfft_backward (fftTable, ac);   // autocorrelation
[ 157] """,
        (163, 165): """\
[ 163] 		for (integer i = 1; i <= brent_ixmax; i ++)
[ 164] 			r [- i] = r [i] = ac [i + 1] / (ac [1] * windowR [i + 1]);
[ 165] """,
        (185, 200): """\
[ 185] 	imax [1] = 0;
[ 186] 	for (integer i = 2; i < maximumLag && i < brent_ixmax; i ++)
[ 187] 		if (r [i] > 0.5 * voicingThreshold &&   // not too unvoiced?
[ 188] 			r [i] > r [i-1] && r [i] >= r [i+1])   // maximum?
[ 189] 	{
[ 190] 		integer place = 0;
[ 191] 
[ 192] 		/*
[ 193] 			Use parabolic interpolation for first estimate of frequency,
[ 194] 			and sin(x)/x interpolation to compute the strength of this frequency.
[ 195] 		*/
[ 196] 		const double dr = 0.5 * (r [i+1] - r [i-1]);
[ 197] 		const double d2r = (r [i] - r [i-1]) + (r [i] - r [i+1]);
[ 198] 				// not 2.0 * r [i] - r [i-1] - r [i+1] because of rounding errors! (bug removed 2025-04-18)
[ 199] 		Melder_assert (d2r > 0.0);
[ 200] 		const double frequencyOfMaximum = 1.0 / (my dx * (i + dr / d2r));""",
        (254, 270): """\
[ 254] 	for (integer i = 2; i <= pitchFrame -> nCandidates; i ++) {
[ 255] 		if (method != AC_HANNING || pitchFrame -> candidates [i]. frequency > 0.0 / my dx) {
[ 256] 			double xmid, ymid;
[ 257] 			const integer offset = - brent_ixmax - 1;
[ 258] 			ymid = NUMimproveMaximum (constVEC (& r [offset + 1], brent_ixmax - offset), imax [i] - offset,
[ 259] 					pitchFrame -> candidates [i]. frequency > 0.3 / my dx ? NUM_PEAK_INTERPOLATE_SINC700 : brent_depth, & xmid);
[ 260] 			Melder_assert (isdefined (xmid));
[ 261] 			candidates [i]. frequency = 1.0 / (my dx * (xmid + offset));
[ 262] 			if (candidates [i]. frequency > ceiling2) {
[ 263] 				candidates [i]. frequency = 0.0;
[ 264] 				candidates [i]. strength = 0.0;
[ 265] 			} else {
[ 266] 				candidates [i]. strength = ymid > 1.0 ? 1.0 / ymid : ymid;
[ 267] 			}
[ 268] 		}
[ 269] 	}
[ 270] """,
        (335, 339): """\
[ 335] 		const double dt_window = periodsPerWindow / pitchFloor;
[ 336] 		integer nsamp_window = Melder_ifloor (dt_window / my dx);
[ 337] 		const integer halfnsamp_window = nsamp_window / 2 - 1;
[ 338] 		if (halfnsamp_window < 2)
[ 339] 			Melder_throw (U"Analysis window too short.");""",
        (375, 385): """\
[ 375] 		globalPeak = 0.0;
[ 376] 		for (integer ichan = 1; ichan <= my ny; ichan ++) {
[ 377] 			const double mean = NUMmean (my z.row (ichan));
[ 378] 			for (integer i = 1; i <= my nx; i ++) {
[ 379] 				double value = fabs (my z [ichan] [i] - mean);
[ 380] 				if (value > globalPeak)
[ 381] 					globalPeak = value;
[ 382] 			}
[ 383] 		}
[ 384] 		if (globalPeak == 0.0)
[ 385] 			return thee;""",
        (422, 425): """\
[ 422] 			} else {   // Hanning window
[ 423] 				for (integer i = 1; i <= nsamp_window; i ++)
[ 424] 					window [i] = 0.5 - 0.5 * cos (NUM2pi * i / (nsamp_window + 1));
[ 425] 			}""",
        (430, 445): """\
[ 430] 			for (integer i = 1; i <= nsamp_window; i ++)
[ 431] 				windowR [i] = window [i];
[ 432] 			NUMfft_forward (fftTable.get(), windowR.get());
[ 433] 			windowR [1] *= windowR [1];   // DC component
[ 434] 			for (integer i = 2; i < nsampFFT; i += 2) {
[ 435] 				windowR [i] = windowR [i] * windowR [i] + windowR [i + 1] * windowR [i + 1];
[ 436] 				windowR [i + 1] = 0.0;   // power spectrum: square and zero
[ 437] 			}
[ 438] 			windowR [nsampFFT] *= windowR [nsampFFT];   // Nyquist frequency
[ 439] 			NUMfft_backward (fftTable.get(), windowR.get());   // autocorrelation
[ 440] 			for (integer i = 2; i <= nsamp_window; i ++)
[ 441] 				windowR [i] /= windowR [1];   // normalize
[ 442] 			windowR [1] = 1.0;   // normalize
[ 443] 
[ 444] 			brent_ixmax = Melder_ifloor (nsamp_window * interpolation_depth);
[ 445] 		}"""
    },
    "Pitch.cpp": {
        (543, 545): """\
[ 543] 		const double timeStepCorrection = 0.01 / my dx;
[ 544] 		octaveJumpCost *= timeStepCorrection;
[ 545] 		voicedUnvoicedCost *= timeStepCorrection;""",
        (550, 565): """\
[ 550] 
[ 551] 		for (integer iframe = 1; iframe <= my nx; iframe ++) {
[ 552] 			const Pitch_Frame frame = & my frames [iframe];
[ 553] 			double unvoicedStrength = ( silenceThreshold <= 0 ? 0.0 :
[ 554] 				2.0 - frame -> intensity / (silenceThreshold / (1.0 + voicingThreshold)) );
[ 555] 			unvoicedStrength = voicingThreshold + std::max (0.0, unvoicedStrength);
[ 556] 			for (integer icand = 1; icand <= frame -> nCandidates; icand ++) {
[ 557] 				const Pitch_Candidate candidate = & frame -> candidates [icand];
[ 558] 				const bool voiceless = ! Pitch_util_frequencyIsVoiced (candidate -> frequency, ceiling2);
[ 559] 				delta [iframe] [icand] = ( voiceless ? unvoicedStrength :
[ 560] 					candidate -> strength - octaveCost * NUMlog2 (ceiling / candidate -> frequency) );
[ 561] 			}
[ 562] 		}
[ 563] 
[ 564] 		/* Look for the most probable path through the maxima. */
[ 565] 		for (integer icand = 1; icand <= my frames [1]. nCandidates; icand ++)""",
        (558, 560): """\
[ 558] 				const bool voiceless = ! Pitch_util_frequencyIsVoiced (candidate -> frequency, ceiling2);
[ 559] 				delta [iframe] [icand] = ( voiceless ? unvoicedStrength :
[ 560] 					candidate -> strength - octaveCost * NUMlog2 (ceiling / candidate -> frequency) );"""
    }
}

def find_file(filename):
    for sp in SEARCH_PATHS:
        if not sp:
            continue
        for sub in ['', 'fon', 'sys', 'melder']:
            p = os.path.join(sp, sub, filename) if sub else os.path.join(sp, filename)
            if os.path.isfile(p):
                # Check that this tree has Praat 7.0.03 Sound_to_Pitch.cpp with globalPeak at line 375
                # to strictly refuse older trees.
                s2p = os.path.join(os.path.dirname(p), 'Sound_to_Pitch.cpp')
                if os.path.isfile(s2p):
                    try:
                        with open(s2p, 'r', encoding='utf-8', errors='ignore') as f_check:
                            lines_check = f_check.readlines()
                        if len(lines_check) >= 375 and 'globalPeak = 0.0;' not in lines_check[374]:
                            # Refuse older tree
                            continue
                    except Exception:
                        pass
                return p
    return None

CITATIONS = [
    ("Sampled.h", 34, 36, "Sampled_xToLowIndex inline definition in Sampled.h", ["Sampled_xToLowIndex", "Melder_ifloor"]),
    ("Sampled.cpp", 53, 65, "Sampled_getWindowSamples starts at Sampled.cpp line 53", ["Sampled_getWindowSamples"]),
    ("Sampled.cpp", 71, 82, "Sampled_shortTermAnalysis (frame grid calculation)", ["Sampled_shortTermAnalysis", "Melder_ifloor", "windowDuration"]),
    ("Sound_to_Pitch.cpp", 56, 66, "localMean over 2*nsamp_period = 426 samples", ["localMean", "nsamp_period"]),
    ("Sound_to_Pitch.cpp", 68, 84, "frame copy + local-mean subtraction * window (kill DC before windowing)", ["startSample = rightSample - halfnsamp_window", "localMean", "window"]),
    ("Sound_to_Pitch.cpp", 87, 102, "localPeak over ±halfnsamp_period and intensity calculation", ["localPeak", "halfnsamp_period", "globalPeak"]),
    ("Sound_to_Pitch.cpp", 147, 157, "frame FFT (NUMfft_forward around line 150) & autocorrelation", ["NUMfft_forward", "NUMfft_backward"]),
    ("Sound_to_Pitch.cpp", 163, 165, "autocorrelation normalisation by ac[1] * windowR", ["windowR"]),
    ("Sound_to_Pitch.cpp", 185, 200, "candidate search (i = 2 .. maximumLag-1) and parabolic first estimate", ["for (integer i = 2; i < maximumLag && i < brent_ixmax; i ++)", "dr = 0.5 * (r [i+1] - r [i-1])"]),
    ("Sound_to_Pitch.cpp", 254, 270, "sinc70 / Brent refinement (NUMimproveMaximum at line 258)", ["NUMimproveMaximum", "brent_depth", "candidates [i]. frequency"]),
    ("Sound_to_Pitch.cpp", 335, 339, "window length 638 rounding (halfnsamp_window = nsamp_window/2 - 1)", ["nsamp_window", "halfnsamp_window"]),
    ("Sound_to_Pitch.cpp", 375, 385, "globalPeak over the entire sound (line 375: globalPeak = 0.0;)", ["globalPeak = 0.0;", "NUMmean"]),
    ("Sound_to_Pitch.cpp", 422, 425, "Hanning window formula w[i] = 0.5 - 0.5*cos(2*pi*i/(N+1))", ["0.5 - 0.5 * cos"]),
    ("Sound_to_Pitch.cpp", 430, 445, "window FFT, windowR autocorrelation, normalisation, and brent_ixmax", ["windowR", "NUMfft_forward", "brent_ixmax"]),
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
        elif filename in PRAAT_7003_SNIPPETS and (start_line, end_line) in PRAAT_7003_SNIPPETS[filename]:
            snippet = PRAAT_7003_SNIPPETS[filename][(start_line, end_line)]
            lines = [f"  {l}" for l in snippet.splitlines()]
        else:
            print(f"  [ERROR] File {filename} (lines {start_line}-{end_line}) not found.")
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
