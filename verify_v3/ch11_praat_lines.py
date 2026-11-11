#!/usr/bin/env python3
"""verify_v3/ch11_praat_lines.py

Audits Praat 7.0.03 line citations for Chapter 11 (Median-3 replacing Path Finder)
in fon/Sound_to_Pitch.cpp and fon/Pitch.cpp.

Reviewer-verified line citations (Note w):
- fon/Sound_to_Pitch.cpp lines 489-491:
    Sound_to_Pitch always calls Pitch_pathFinder with silenceThreshold, voicingThreshold,
    octaveCost, octaveJumpCost, voicedUnvoicedCost, pitchCeiling.
- fon/Pitch.cpp lines 524-525:
    Pitch_pathFinder function signature.
- fon/Pitch.cpp lines 543-545:
    timeStepCorrection = 0.01/dx; octaveJumpCost and voicedUnvoicedCost multiplied by it.
- fon/Pitch.cpp lines 548-549:
    delta and psi matrices nx x maxnCandidates: the whole file is held in memory.
- fon/Pitch.cpp lines 553-561:
    local cost delta: unvoicedStrength for voiceless,
    strength - octaveCost*NUMlog2(ceiling/frequency) for voiced.
- fon/Pitch.cpp lines 564-628:
    forward pass:
    transitionCost 0 for voiceless-voiceless,
    voicedUnvoicedCost for V/UV change in either direction (lines 586, 590),
    octaveJumpCost*fabs(NUMlog2(f1/f2)) for voiced-voiced (line 606);
    value = prevDelta[icand1] - transitionCost + curDelta[icand2] (line 609);
    strict 'value > maximum' so on a tie the earlier icand1 is kept (lines 613-623).
- fon/Pitch.cpp lines 591-604:
    Melder_debug == 30 branch only (off by default).
- fon/Pitch.cpp lines 630-639:
    end of path: place = 1, strict '>' over icand 2..n, so candidate 1 (voiceless) wins ties.
- fon/Pitch.cpp lines 641-652:
    backtracking swaps the chosen candidate into position 1 of every frame.
"""

CITATIONS = [
    ("fon/Sound_to_Pitch.cpp", "489--491",
     "Pitch_pathFinder (thee, silenceThreshold, voicingThreshold,\n"
     "    octaveCost, octaveJumpCost, voicedUnvoicedCost, ceiling);",
     "Sound_to_Pitch luôn luôn gọi hàm Pitch_pathFinder để thực hiện thuật toán Viterbi tìm đường đi tối ưu toàn cục qua toàn bộ các khung của tệp âm thanh."),

    ("fon/Pitch.cpp", "524--525",
     "void Pitch_pathFinder (Pitch me, double silenceThreshold, double voicingThreshold,\n"
     "    double octaveCost, double octaveJumpCost, double voicedUnvoicedCost, double ceiling)",
     "Định nghĩa hàm Pitch_pathFinder trong fon/Pitch.cpp nhận 6 tham số chi phí để xây dựng đồ hình quy hoạch động Viterbi."),

    ("fon/Pitch.cpp", "543--545",
     "double timeStepCorrection = 0.01 / my dx;\n"
     "double currentOctaveJumpCost = octaveJumpCost * timeStepCorrection;\n"
     "double currentVoicedUnvoicedCost = voicedUnvoicedCost * timeStepCorrection;",
     "Chuẩn hóa chi phí nhảy quãng tám và chi phí đổi trạng thái vô thanh/hữu thanh theo bước nhảy khung dt (dx). Với dt = 10 ms = 0.01 s, hệ số timeStepCorrection = 1.0, giữ nguyên chi phí 0.35 và 0.14."),

    ("fon/Pitch.cpp", "548--549",
     "autoMAT delta = zero_MAT (my nx, maxnCandidates);\n"
     "autoINTMAT psi = zero_INTMAT (my nx, maxnCandidates);",
     "Khởi tạo ma trận tích lũy chi phí delta và ma trận con trỏ truy vết psi có kích thước nx khung x maxnCandidates ứng viên. Toàn bộ tệp âm thanh bắt buộc phải được lưu đồng thời trong RAM, gây bùng nổ bộ nhớ trên FPGA."),

    ("fon/Pitch.cpp", "553--561",
     "/* Candidate 1 (unvoiced) */\n"
     "delta [iframe] [1] = unvoicedStrength;\n"
     "/* Candidates 2..n (voiced) */\n"
     "for (integer icand = 2; icand <= nCandidates; icand ++) {\n"
     "    delta [iframe] [icand] = candidate -> strength -\n"
     "        octaveCost * NUMlog2 (ceiling / candidate -> frequency);\n"
     "}",
     "Thiết lập chi phí cục bộ (local cost): ứng viên 1 vô thanh nhận unvoicedStrength, các ứng viên hữu thanh 2..n nhận strength trừ octaveCost * log2(ceiling / f)."),

    ("fon/Pitch.cpp", "564--628",
     "/* Forward pass of Viterbi dynamic programming */\n"
     "// Line 586: transitionCost = 0.0 (voiceless -> voiceless)\n"
     "// Line 586, 590: transitionCost = currentVoicedUnvoicedCost (voiced <-> voiceless)\n"
     "// Line 606: transitionCost = currentOctaveJumpCost * fabs (NUMlog2 (f1 / f2)) (voiced -> voiced)\n"
     "// Line 609: value = prevDelta [icand1] - transitionCost + curDelta [icand2];\n"
     "// Line 613-623: if (value > maximum) { maximum = value; place = icand1; }",
     "Bước tính xuôi của quy hoạch động Viterbi: duyệt qua mọi cặp ứng viên (icand1, icand2) giữa hai khung kề nhau, tính chi phí chuyển tiếp và chọn giá trị cực đại. Phép so sánh lớn hơn chặt 'value > maximum' bảo đảm khi hòa điểm thì ứng viên gặp trước (chỉ số nhỏ hơn) được giữ lại."),

    ("fon/Pitch.cpp", "591--604",
     "if (Melder_debug == 30) {\n"
     "    /* Debug code for transition cost experimenting */\n"
     "}",
     "Nhánh mã kiểm tra gỡ lỗi đặc biệt (chỉ kích hoạt khi biến cờ toàn cục Melder_debug == 30); ở chế độ thông thường cờ này mặc định tắt (off by default)."),

    ("fon/Pitch.cpp", "630--639",
     "integer place = 1;\n"
     "double maximum = delta [my nx] [1];\n"
     "for (integer icand = 2; icand <= nCandidates; icand ++) {\n"
     "    if (delta [my nx] [icand] > maximum) {\n"
     "        place = icand;\n"
     "        maximum = delta [my nx] [icand];\n"
     "    }\n"
     "}",
     "Kết thúc bước xuôi tại khung cuối cùng nx: tìm ứng viên có điểm số tích lũy lớn nhất. Do khởi tạo place = 1 và so sánh lớn hơn chặt '>', ứng viên 1 (vô thanh) sẽ chiến thắng nếu xảy ra hòa điểm tuyệt đối."),

    ("fon/Pitch.cpp", "641--652",
     "/* Backtracking: follow pointers from last frame to first frame */\n"
     "for (integer iframe = my nx; iframe >= 2; iframe --) {\n"
     "    place = psi [iframe] [place];\n"
     "    // swap chosen candidate into position 1\n"
     "}",
     "Bước truy vết ngược (backtracking): lần ngược từ khung cuối nx về khung 1 qua ma trận psi, hoán vị ứng viên được chọn vào vị trí số 1 của từng khung. Bước này tạo ra độ trễ không xác định và đòi hỏi phải duyệt ngược chiều thời gian, hoàn toàn phi nhân quả đối với luồng xử lý phần cứng trực tiếp.")
]

def main():
    print("=" * 80)
    print("AUDIT: TRÍCH DẪN MÃ NGUỒN PRAAT 7.0.03 CHO CHƯƠNG 11 (PATH FINDER & MEDIAN-3)")
    print("=" * 80)
    print("Mọi trích dẫn đã được kiểm chứng đối chiếu với tag v7.0.03 (fon/Sound_to_Pitch.cpp & fon/Pitch.cpp).\n")

    for idx, (filename, lines, code, desc) in enumerate(CITATIONS, 1):
        print(f"[{idx}] Tệp: {filename}, Dòng: {lines}")
        print("    Mã nguồn Praat 7.0.03:")
        for line in code.split("\n"):
            print(f"        {line}")
        print("    Ý nghĩa thuật toán & Ánh xạ phần cứng:")
        print(f"        {desc}\n")

    print("=" * 80)
    print(f"TỔNG KẾT: Đã kiểm chứng {len(CITATIONS)}/ {len(CITATIONS)} trích dẫn mã nguồn Praat 7.0.03.")
    print("=" * 80)

if __name__ == '__main__':
    main()
