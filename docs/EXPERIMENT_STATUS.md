# Bảng Theo dõi Trạng thái Thí nghiệm (Experiment Status)

> Quy ước ký hiệu:
> - 🚧 = Đang trong giai đoạn thiết kế khung / Chưa triển khai (Scaffolded / In Planning)
> - 📖 = Yêu cầu phần cứng thực tế hoặc đo kiểm thủ công (Hardware-in-the-loop / Manual)
> - ✅ = Đã thực thi thành công, có đầy đủ bằng chứng và vượt qua kiểm thử tự động

---

## Danh mục Thí nghiệm

| Mã Thí nghiệm | Chương | Tên Thí nghiệm | Nền tảng Phần cứng | Trạng thái | Mục tiêu Khảo sát |
|:---:|:---:|---|:---:|:---:|---|
| **exp_01** | 01 | `streaming_audio_pipeline` | Host / Python Simulation | 🚧 | Đệm trượt vòng, tính toán STFT và Mel filterbank trực tuyến |
| **exp_02** | 02 | `jetson_orin_profiler` | NVIDIA Jetson Orin | 🚧 | Đo độ trễ TensorRT và công suất cảm biến INA3221 (`tegrastats`) |
| **exp_03** | 03 | `batch_one_gpu_bottleneck` | Jetson Orin | 🚧 | Đo độ chiếm dụng SM, thời gian kernel launch và jitter |
| **exp_04** | 04 | `fpga_dsp_bram_mapping` | AMD Xilinx UltraScale+ | 🚧 | Ước tính tài nguyên LUT, FF, DSP và dung lượng BRAM/URAM |
| **exp_05** | 05 | `dpu_vs_finn_benchmark` | Kria KV260 | 🚧 | So sánh thời gian đáp ứng giữa Vitis AI DPU và FINN Dataflow |
| **exp_06** | 06 | `hardware_fixed_point_fft` | Vivado HLS / RTL | 🚧 | Đánh giá sai số SQNR của bộ FFT dấu phẩy tĩnh so với FP32 |
| **exp_07** | 07 | `voice_qat_calibration` | PyTorch / Brevitas | 🚧 | Lượng tử hóa QAT INT8/INT4 và đánh giá suy giảm WER/PESQ |
| **exp_08** | 08 | `voice_attention_accelerator` | Kria KV260 | 🚧 | Tăng tốc hàm Softmax cơ số 2 và LayerNorm trên FPGA fabric |
| **exp_09** | 09 | `pynq_dma_audio_streaming` | Kria KV260 PYNQ | 🚧 | Đo độ trễ DMA round-trip giữa ARM Host và FPGA Logic |
| **exp_10** | 10 | `pareto_frontier_eval` | Orin vs. Kria KV260 | 🚧 | Dựng đường cong Pareto: Độ trễ vs Năng lượng vs Độ chính xác |
