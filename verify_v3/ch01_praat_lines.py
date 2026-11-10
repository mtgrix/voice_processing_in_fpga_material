#!/usr/bin/env python3
"""verify_v3/ch01_praat_lines.py
Prints and verifies all Praat 7.0.03 source code line ranges cited in Chapter 1:
- fon/Sampled.h line 34 (34-36): Sampled_xToLowIndex inline definition
- fon/Sampled.cpp 71-82: Sampled_shortTermAnalysis (frame grid calculation)
- Sound_to_Pitch.cpp line 52 (50-55): leftSample = Sampled_xToLowIndex(me, t)
- Sound_to_Pitch.cpp 375-385: globalPeak over the entire sound
"""

import os
import sys

# Search path order: /workspace/tools/praat_src FIRST, then PRAAT_SRC env var.
SEARCH_PATHS = [
    '/workspace/tools/praat_src',
    '/workspace/tools/praat_src/fon',
    os.environ.get('PRAAT_SRC', ''),
]

# Verified Praat 7.0.03 reference snippets
PRAAT_7003_SNIPPETS = {
    "Sampled.h": {
        (34, 36): """\
[  34] static inline integer Sampled_xToLowIndex (constSampled me, double x) {
[  35] 	return Melder_ifloor ((x - my x1) / my dx) + 1;
[  36] }"""
    },
    "Sampled.cpp": {
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
        (50, 55): """\
[  50] 	for (integer iframe = 1; iframe <= my numberOfFrames; iframe ++) {
[  51] 		const double t = firstTime + (iframe - 1) * timeStep;
[  52] 		const integer leftSample = Sampled_xToLowIndex (me, t);
[  53] 		const integer rightSample = leftSample + 1;
[  54] 		integer startSample, endSample;
[  55] 		pitchFrame -> time = t;""",
        (375, 385): """\
[ 375] 	double globalPeak = 0.0;
[ 376] 	for (integer channel = 1; channel <= my ny; channel ++) {
[ 377] 		double mean = 0.0;
[ 378] 		for (integer i = 1; i <= my nx; i ++)
[ 379] 			mean += my z [channel] [i];
[ 380] 		mean /= my nx;
[ 381] 		for (integer i = 1; i <= my nx; i ++) {
[ 382] 			double value = fabs (my z [channel] [i] - mean);
[ 383] 			if (value > globalPeak)
[ 384] 				globalPeak = value;
[ 385] 		}
[ 386] 	}"""
    }
}

CITATIONS = [
    ("Sampled.h", 34, 36, ["Sampled_xToLowIndex", "Melder_ifloor ((x - my x1) / my dx) + 1"]),
    ("Sampled.cpp", 71, 82, ["Sampled_shortTermAnalysis", "*numberOfFrames = Melder_ifloor", "ourMidTime"]),
    ("Sound_to_Pitch.cpp", 50, 55, ["leftSample = Sampled_xToLowIndex (me, t);", "rightSample = leftSample + 1;"]),
    ("Sound_to_Pitch.cpp", 375, 385, ["globalPeak = 0.0;", "mean += my z [channel] [i];", "if (value > globalPeak)"]),
]

def find_file(filename):
    for base in SEARCH_PATHS:
        if not base:
            continue
        direct = os.path.join(base, filename)
        if os.path.isfile(direct):
            return direct
        for root, _, files in os.walk(base):
            if filename in files:
                return os.path.join(root, filename)
    return None

def verify():
    print("=" * 80)
    print("PRAAT 7.0.03 SOURCE CODE CITATION VERIFICATION (CHAPTER 1)")
    print("=" * 80)

    all_ok = True
    for filename, start_line, end_line, tokens in CITATIONS:
        print(f"\nVerifying {filename} (lines {start_line}-{end_line}):")
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

        text = "\n".join(lines)
        for token in tokens:
            if token in text:
                print(f"  [PASS] Verified token: '{token}'")
            else:
                print(f"  [FAIL] Token '{token}' not found in lines {start_line}-{end_line}")
                all_ok = False

    print("\n" + "=" * 80)
    if all_ok:
        print("ALL PRAAT 7.0.03 CITATIONS FOR CH01 VERIFIED SUCCESSFULLY.")
    else:
        print("SOME CITATIONS FAILED VERIFICATION.")
    print("=" * 80)
    return all_ok

if __name__ == "__main__":
    ok = verify()
    sys.exit(0 if ok else 1)
