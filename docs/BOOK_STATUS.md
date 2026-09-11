# Book & Research Status — Voice Edge AI

> **Tracking progress across all 10 chapters and paper sections.**
> Last updated: 2026-09-11

---

## 1. Chapter Progress Overview

| Chapter | Title | VI Draft | EN Draft | Experiments | Status |
|:---:|---|:---:|:---:|:---:|:---:|
| **01** | Từ Sóng Âm đến Suy diễn Biên | Complete | In Progress | ✅ exp_01 | In Active Development |
| **02** | Jetson Orin: Điểm chuẩn & Giới hạn | Complete | In Progress | ✅ exp_02 | In Active Development |
| **03** | Điểm nghẽn Streaming trên Edge GPU | Planned | Planned | 🚧 exp_03 | Outlined |
| **04** | Vi kiến trúc FPGA cho Edge AI | Planned | Planned | 🚧 exp_04 | Outlined |
| **05** | Phương pháp luận Tăng tốc: HLS, DPU, FINN | Planned | Planned | 🚧 exp_05 | Outlined |
| **06** | Tăng tốc Tầng Tiền xử lý Âm thanh | Planned | Planned | 🚧 exp_06 | Outlined |
| **07** | Khoa học Lượng tử hóa Thích ứng Phần cứng | Planned | Planned | 🚧 exp_07 | Outlined |
| **08** | Tăng tốc Attention & Conformer | Planned | Planned | 🚧 exp_08 | Outlined |
| **09** | Tích hợp SoC & Đồng thiết kế HW/SW | Planned | Planned | 🚧 exp_09 | Outlined |
| **10** | Phương pháp Luận Nghiên cứu & Viết Paper | Planned | Planned | 🚧 exp_10 | Outlined |

---

## 2. Paper Drafting Milestone

- **Target Venue**: IEEE/ACM FCCM / ICASSP / ESL
- **Core Title**: *Spatial Dataflow vs. SIMT for Continuous Edge Voice AI: A Comprehensive Pareto Analysis from Jetson Orin to FPGA*
- **Target Metrics**:
  - Word Error Rate (WER) degradation $< 0.3\%$ under INT8/INT4 quantization
  - Real-Time Factor (RTF) $< 0.05$ on FPGA fabric
  - Active Power $< 4.5\text{W}$ on FPGA vs. $10.2\text{W}$ on Jetson Orin
  - Energy per Audio Frame: $\ge 2.5\times$ improvement on FPGA
