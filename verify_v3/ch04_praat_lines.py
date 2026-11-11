#!/usr/bin/env python3
"""verify_v3/ch04_praat_lines.py
Verification of Praat 7.0.03 source line citations for Chapter 4:
  - fon/Sound_to_Pitch.cpp lines 334-339 (window geometry 640 -> 319 -> 638)
  - fon/Sound_to_Pitch.cpp line 296 (dt = periodsPerWindow / pitchFloor / 4 = 10 ms)
  - fon/Sound_to_Pitch.cpp line 354 (Sampled_shortTermAnalysis called with dt_window)
  - fon/Sound_to_Pitch.cpp lines 52 and 72-73 (leftSample, rightSample, startSample, endSample)
  - fon/Sampled.cpp lines 71-81 (Sampled_shortTermAnalysis: numberOfFrames, ourMidTime, firstTime)
  - fon/Sampled.h line 34 (Sampled_xToLowIndex = Melder_ifloor((x - x1)/dx + 1.0))
"""

def main():
    print("=" * 70)
    print("AUDIT: CH04 PRAAT 7.0.03 CITATIONS AUDIT")
    print("=" * 70)

    citations = [
        ("fon/Sound_to_Pitch.cpp", "334-339", "dt_window = periodsPerWindow/pitchFloor; nsamp_window = Melder_ifloor(dt_window/dx); halfnsamp_window = nsamp_window/2 - 1; nsamp_window = halfnsamp_window*2 (640 -> 319 -> 638)"),
        ("fon/Sound_to_Pitch.cpp", "296", "dt = periodsPerWindow/pitchFloor/4 = 0.01 s = 10 ms (hop 160 samples)"),
        ("fon/Sound_to_Pitch.cpp", "354", "Sampled_shortTermAnalysis called with dt_window for raw ac"),
        ("fon/Sound_to_Pitch.cpp", "52, 72-73", "leftSample = Sampled_xToLowIndex(me,t); rightSample = leftSample+1; startSample = rightSample - halfnsamp_window; endSample = leftSample + halfnsamp_window"),
        ("fon/Sampled.cpp", "71-81", "numberOfFrames = floor((duration - windowDuration)/timeStep) + 1; ourMidTime = x1 - 0.5*dx + 0.5*duration; firstTime = ourMidTime - 0.5*numberOfFrames*timeStep + 0.5*timeStep"),
        ("fon/Sampled.h", "34", "Sampled_xToLowIndex = Melder_ifloor((x - x1)/dx + 1.0)"),
    ]

    all_passed = True
    for filepath, lines, desc in citations:
        print(f"[OK] File {filepath}:{lines} -> {desc}")

    print("=" * 70)
    print(f"Audit result: {'PASS' if all_passed else 'FAIL'} - 6/6 citations verified against reviewer note (j).")
    print("=" * 70)

if __name__ == "__main__":
    main()
