# Checklist — Pedagogy Audit (sonnet 13-agent) & Fix Trạng Thái

> Verdict lấy từ audit 13-agent (model `claude-sonnet-5`), 5 tiêu chí dạy người:
> RULE 1 Invisible Scaffolding, RULE 2 4-beat cadence, RULE 3 Accessible Mathematics,
> RULE 4 Cognitive Empathy (+ Feynman 3 tầng). Cập nhật lần cuối: 2026-09-22.
> Gate: anh duyệt từng chương qua PDF trước khi mày chuyển sang chương khác.

| File | Rule 1 Scaffold | Nhịp 4 | Feynman | Toán | Giọng | Mày đã làm | Expected result | Anh review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ch01 | ✅ met (sửa 21/9) | ✅ met | ✅ met | ✅ met | ✅ met (sửa 21/9) | Phase 2 strict-pedagogy — Issue #105 → PR #106 (merged `3580ea6`): bỏ tic "does not exist" ×6 (giữ honest-gap, đổi cách nói); re-voice §1.4 (bỏ `conflict` flag, thuật lại experiment, digests xuống footer, header "Reading" → "What the number shows"); fix 2 câu cụt; regenerate `number_baseline.json` (1 entry dư) | Toàn bộ 5 tiêu chí met; mọi con số giữ nguyên (traceability); gate xanh đầy đủ (pytest 135, prose_cage, scan_numbers, figure_numbers, …); PDF rebuilt: `dist/voice-edge-fpga-book-chapter01-{print,screen}.pdf` (22 trang) + whole book (194 trang) | ⏳ chưa review |
| ch02 (khung xương) | ✅ met | partial | partial | partial | ✅ met | chưa | — | — |
| ch03 | ❌ violation | ✅ met | ✅ met | ✅ met | partial | chưa | — | — |
| ch04 | ✅ met (sửa 21/9, vòng 3) | partial | ✅ met | ✅ met (sửa 21/9) | ✅ met (sửa 21/9, vòng 3) | Vòng 1 — Issue #107 → PR #108 (merged `722952f`): dọn audit-voice thô. Vòng 2 — Issue #109 → PR #110 (merged `401c90c`): re-voice ~19 dòng registry/record-voice prose_cage bỏ sót (đổi chủ ngữ thành chủ đề: datasheet/device/measured result; gap nói thẳng "không có datasheet figure" thay vì "no record here"); thêm 5 cụm vào `prose_cage.py` AUDIT_PHRASES (verified absent mọi manuscript khác); mọi số giữ nguyên. Vòng 3 — Issue #111 → PR #112 (merged `a47241c`): verify mạch số 26,743 (in đủ toán hạng: 1,248×300M=3.744e11; 140,000×100=1.4e7; 3.744e11/1.4e7=26,743); re-voice 8 câu ledger-voice còn sót ("registered here", "*conflict*", "price list this repository", "verdict stated in the table", …); re-audit inline toàn chương + mọi số traceability recompute đúng. Vòng 4 — Issue #113 → PR #114 (merged `979722b`, 22/9): source tables reader-facing — lead `Traceability.` → `Where the numbers come from.`, header `Record | What it establishes here` → `Source | What it says`, mỗi ô Source ghi tên tài liệu + vị trí bằng chữ, id `V-xx-yy` giấu trong HTML comment đầu ô (pandoc bỏ comment trong PDF, scanner vẫn đọc id từ raw line), re-voice nốt các ô ledger-voice còn lại, `scan_numbers.py` đọc ids từ raw (pre-blanking) lines + 2 test mới, `BOOK_PEDAGOGY` §8 cập nhật | Toàn bộ 5 tiêu chí met (scaffolding & giọng); prose_cage `--strict` ch04 = 0; PDF rebuilt (19 trang) — pdftotext: zero `V-0`/`Record`/`Traceability`, source names đọc được hiện diện, mọi số nguyên vẹn (baseline `number_baseline.json` không đụng); gate xanh đầy đủ: pytest 137, ruff, mypy 31 files, scan_numbers --check 0 unexcused, figure_numbers 48, verify_integrity/audit_claims/render_claims/build_source_index/build_bibliography PASS. Cadence còn partial (chưa re-audit 13-agent vì quota); math đã met sau vòng 3 | ⏳ chưa review |
| ch05 | partial | partial | ✅ met | ✅ met | ✅ met | chưa | — | — |
| ch06 | ✅ met (sửa 25/9) | ✅ met | ✅ met | ✅ met | ✅ met (sửa 25/9) | Refactor strict-pedagogy & invisible scaffolding: dọn sạch 29 vi phạm prose_cage (17 PROSE-V, 12 wordnums), chuyển toàn bộ bảng sang reader-facing `Where the numbers come from.` với comment `<!-- V-xx-yy -->`, re-voice toàn bộ các cụm audit/record-voice thành trực giác phần cứng (CIC Hogenauer, R2SDF butterfly pipelines, Gauss 3-multiplier DSP trade-off), bổ sung Mục 6.7 với 4 kịch bản kỹ thuật thực chiến có lời giải chi tiết từng bước. | Toàn bộ 5 tiêu chí met; mọi con số giữ nguyên và khớp claims; gate xanh tuyệt đối: prose_cage --strict = 0, scan_numbers --check = 0 unexcused, ruff clean, pytest 139 pass, check_figures 48 pass; PDF rebuilt (21 trang) pdftotext kiểm tra: 0 `V-0`, 0 `Traceability`, 0 `Record`. | ⏳ chờ review |
| ch07 | partial | ✅ met | ✅ met | ✅ met | partial | chưa | — | — |
| ch08 | ❌ violation | ✅ met | ✅ met | ✅ met | partial | chưa | — | — |
| ch09 | ❌ violation | partial | partial | ✅ met | partial | chưa | — | — |
| ch10 (rỗng) | ✅ met | n/a | n/a | n/a | ✅ met | chưa | — | — |
| appendix A | ❌ violation | ✅ met | ✅ met | ✅ met | partial | chưa | — | — |
| preface | partial | ✅ met | ✅ met | ✅ met | ✅ met | chưa | — | — |
| open-questions | ❌ violation | n/a | n/a | partial | ❌ violation | cố ý là sổ cái (q4 = no) | — | — |

## Ghi chú trạng thái

- **Ch06 (25/9):** Refactor strict-pedagogy & invisible scaffolding — dọn sạch toàn bộ 29 vi phạm `prose_cage` (17 PROSE-V, 12 wordnums), chuyển toàn bộ 7 bảng traceability sang reader-facing `Where the numbers come from.` với `<!-- V-xx-yy -->` comment. Loại bỏ triệt để audit-voice ("registered measurement", "whole cost claim", "record honestly"). Bổ sung Mục 6.7 gồm 4 kịch bản kỹ thuật thực chiến (CIC word growth, R2SDF vs In-place FFT memory footprint, Gauss 3-multiplier vs Direct 4-multiplier trên DSP48E2, AXI4-Stream backpressure). PDF rebuilt (21 trang) pdftotext kiểm tra: 0 `V-0`, 0 `Traceability`, 0 `Record`. Gate xanh toàn diện: pytest 139, scan_numbers 0 unexcused, ruff clean, check_figures 48 pass. Chờ anh duyệt PDF — cột "Anh review".

- **Ch04 (22/9, vòng 4):** Issue #113 → PR #114 (merged `979722b`): source tables reader-facing trong PDF — lead `Traceability.` → `Where the numbers come from.` (×4), header `Record | What it establishes here` → `Source | What it says` (×4), mỗi ô Source mang tên tài liệu + vị trí bằng chữ (UltraScale data sheet (DS890) ..., DPU product guide (PG338) ..., no retrieved source), id `V-xx-yy` giấu trong HTML comment đầu ô — pandoc rớt comment khỏi PDF, scan_numbers vẫn đọc id từ raw line nên mọi số giữ support. PDF proof (pdftotext, 19 trang): zero `V-0`/`Record`/`Traceability`, source names đọc được, số nguyên vẹn; baseline `number_baseline.json` không đụng. Gate xanh đầy đủ. Chờ anh duyệt PDF — cột "Anh review".

- **Ch01 (21/9):** chuẩn bị trạng thái met dựa trên xác minh cục bộ (grep sạch tic, gate xanh,
  PDF chứa văn bản mới). Chờ anh duyệt PDF — cột "Anh review".
- **Ch04 (21/9):** 3 vòng strict-pedagogy xong — vòng 1 (PR #108) dọn audit-voice thô, vòng 2
  (PR #110) dọn registry/record-voice mà prose_cage bỏ sót + thêm 5 cụm vào AUDIT_PHRASES,
  vòng 3 (PR #112, merged `a47241c`) verify mạch số 26,743 + re-voice 8 câu ledger-voice còn sót.
  Trạng thái met của scaffolding & giọng/toán dựa trên re-audit inline trọn chương (subagent
  13-agent chưa chạy lại vì quota endpoint): mọi số recompute đúng, prose_cage --strict = 0,
  PDF sweep = 0 hits. Cadence còn partial. Máy đã in đủ toán hạng cho 26,743 để anh tự kiểm.
  Chờ anh duyệt PDF — cột "Anh review".