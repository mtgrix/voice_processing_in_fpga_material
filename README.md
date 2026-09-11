# Voice Edge AI: From Jetson Orin to FPGA

<h4 align="center">Từ Jetson Orin đến FPGA: Tăng tốc Phần cứng Mô hình Xử lý Giọng nói — Khung Nghiên cứu & Bản thảo Chuyên khảo Thực thi</h4>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0--or--later-blue" alt="license: GPL-3.0-or-later"></a>
  <a href="#editions"><img src="https://img.shields.io/badge/Tiếng_Việt-Bản_thảo_chuẩn-green" alt="Tiếng Việt"></a>
  <a href="#editions"><img src="https://img.shields.io/badge/English-Paper_Drafts-blue" alt="English"></a>
  <a href="#testing"><img src="https://img.shields.io/badge/python-%3E%3D3.12-informational" alt="python: >=3.12"></a>
  <a href="#testing"><img src="https://img.shields.io/badge/hardware-Jetson%20Orin%20%7C%20FPGA-orange" alt="hardware"></a>
</p>

> Khung sườn nghiên cứu khoa học và chuyên khảo thực thi (executable monograph scaffolding) phục vụ mục tiêu học tập, thực nghiệm và viết bài báo khoa học về đề tài chuyển đổi mô hình xử lý giọng nói (Voice AI / Speech Processing) từ nền tảng nhúng GPU NVIDIA Jetson Orin sang kit phần cứng FPGA (AMD Xilinx Kria / Zynq UltraScale+).

---

## Hai Mô hình Tư duy Cốt lõi (The Two Mental Models)

```text
Mô hình 1 — Hệ thống Xử lý Thoại Biên (Edge Voice System):
  Voice Edge System  =  Audio Preprocessing / DSP  +  Neural Acoustic Model  +  Hardware Microarchitecture
  (Hệ thống Thoại Biên  =  Tầng Tiền xử lý / DSP  +  Mô hình Nơ-ron Âm học  +  Vi kiến trúc Phần cứng)

Mô hình 2 — Vòng đời Nghiên cứu & Di chuyển Phần cứng (Hardware Migration Lifecycle):
  Hardware Migration  =  Profiling & Bottlenecks (GPU)  →  Hardware-Aware Quantization  →  Spatial Architecture Mapping (FPGA)  →  Pareto Verification
  (Vòng đời Di chuyển  =  Định lượng Điểm nghẽn  →  Lượng tử hóa Thích ứng  →  Ánh xạ Kiến trúc Không gian  →  Đánh giá Biên tối ưu Pareto)
```

Hai mô hình trên đóng vai trò kim chỉ nam phân tách rành mạch giữa: xử lý tín hiệu âm thanh (miền thời gian - tần số), mô hình nơ-ron học sâu (mạng nơ-ron âm học) và vi kiến trúc phần cứng bán dẫn (GPU SIMT vs. FPGA Spatial Dataflow).

---

## Khung Mục lục 10 Chương (Curriculum & Paper Roadmap)

| Phần | Chương | Tên Chương | Trọng tâm Nghiên cứu & Học tập |
|:---:|:---:|---|---|
| **I. Nền tảng & Điểm chuẩn GPU** | 1 | **Kiến trúc Pipeline Xử lý Tiếng nói & Ràng buộc Thời gian thực** | Đặc thù của luồng âm thanh liên tục (streaming), độ trễ khung (<10–25ms), kích thước lô bằng một ($batch=1$). |
| | 2 | **Phân tích Vi kiến trúc & Đo kiểm Điểm chuẩn trên Jetson Orin** | Vi kiến trúc Ampere GPU, Tensor Cores, bộ nhớ LPDDR5, công cụ đo kiểm TensorRT và `tegrastats`. |
| | 3 | **Điểm nghẽn Xử lý Luồng (Streaming) trên Kiến trúc GPU** | Phân tích tại sao GPU bị lãng phí năng lượng, giảm hiệu suất tính toán và gặp hiện tượng jitter khi $batch=1$. |
| **II. Vi kiến trúc FPGA & Tăng tốc** | 4 | **Vi kiến trúc FPGA: Logic Slices, DSP, BRAM/URAM & Luồng Dữ liệu** | Nguyên lý tính toán không gian (spatial computing), đường ống luồng (pipelining), chu kỳ khởi tạo ($II=1$). |
| | 5 | **So sánh Các Phương pháp luận Tăng tốc trên FPGA** | So sánh 4 hướng triển khai: AMD Vitis AI DPU, FINN Streaming Dataflow, Vivado HLS và Custom RTL. |
| | 6 | **Tăng tốc Phần cứng cho Tầng Tiền xử lý Tín hiệu Âm thanh** | Thiết kế phần cứng tính toán STFT/FFT fixed-point bit-exact, Mel filterbank và giao tiếp micrô I2S/PDM trực tiếp. |
| **III. Nén & Lượng tử hóa Thích ứng** | 7 | **Khoa học Lượng tử hóa Thích ứng Phần cứng cho Mô hình Thoại** | Lý thuyết PTQ và QAT (INT8, INT4, non-uniform); kiểm soát suy giảm tỷ lệ lỗi từ (WER) và chất lượng âm (PESQ). |
| | 8 | **Tăng tốc Các Khối Tính toán Cốt lõi của Mô hình Thoại** | Tối ưu hóa Attention (Softmax phi tuyến), Depthwise Separable Convolutions và các khối nơ-ron trên FPGA fabric. |
| **IV. Tích hợp & Viết Paper** | 9 | **Tích hợp Hệ thống SoC & Đồng thiết kế Phần cứng/Phần mềm** | Giao tiếp ARM Host + FPGA Logic qua DMA, AXI-Stream, PYNQ driver và tối ưu hóa băng thông bộ nhớ DDR. |
| | 10 | **Thiết lập Thực nghiệm Đo kiểm, Đánh giá Pareto & Viết Bài báo** | Phương pháp luận thực nghiệm đo đạc (WER, RTF, mJ/frame, TOPS/W, Tài nguyên FPGA), dựng Pareto Frontier và cấu trúc bài báo. |

---

## Cấu trúc Không gian Làm việc (Workspace Structure)

```text
voice_jetson_to_fpga_learning-journey/
├── book/                   # Khung bản thảo tiếng Việt chuẩn (Chương 01 -> 10)
├── book-en/                # Khung bản thảo tiếng Anh / Bản nháp Paper
├── chapter01–10/           # Thư mục chứa các thí nghiệm thực thi theo từng chương
├── capstone/               # Khung kịch bản đo kiểm so sánh Jetson Orin vs FPGA (Voice Edge Benchmark)
├── docs/                   # Quy chuẩn sư phạm, phương pháp nghiên cứu, tra cứu nguồn khoa học
│   ├── BOOK_PEDAGOGY.md    # Quy chuẩn sư phạm (Local Sufficiency, 3-Level Concept Intro)
│   ├── RESEARCH_METHODOLOGY.md # Hướng dẫn viết bài báo khoa học chuẩn IEEE/ACM
│   ├── SOURCES.md          # Danh mục tài liệu tham khảo có thẩm quyền
│   ├── source_index.json   # Chỉ mục nguồn chuẩn JSON
│   ├── BOOK_STATUS.md      # Bảng theo dõi tiến độ biên soạn các chương
│   ├── EXPERIMENT_STATUS.md# Bảng theo dõi trạng thái các bài thí nghiệm
│   └── GLOSSARY.md         # Bảng tra cứu thuật ngữ chuyên ngành Thoại & Phần cứng
├── scripts/                # Script kiểm tra tính toàn vẹn và hỗ trợ tự động hóa
└── tests/                  # Bộ kiểm thử cấu trúc khung sườn và tính toàn vẹn của dự án
```

---

## Hướng dẫn Khởi đầu

### Yêu cầu Tiên quyết
- **Python 3.12+**
- Trình quản lý gói `uv` hoặc `pip`

### Kiểm tra Tính toàn vẹn của Khung Dự án
```bash
python scripts/verify_integrity.py
python -m pytest
python -m ruff check .
```

---

## Trích dẫn Định dạng BibTeX
```bibtex
@book{voice_jetson_to_fpga_journey,
  title     = {Voice Edge AI: From Jetson Orin to FPGA},
  author    = {Nguyen, Minh Tuan},
  year      = {2026},
  publisher = {Open Source Monograph \& Research Journey},
  url       = {https://github.com/MinhTuan76800310/voice_jetson_to_fpga_learning-journey}
}
```

**Giấy phép (License):** [GPL-3.0-or-later](LICENSE)
