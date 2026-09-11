# Experiment Status Tracker — Voice Edge AI

> Standard status indicators:
> - ✅ = Executed successfully with verified output and captured evidence.
> - 📖 = Hardware-in-the-loop or external board required for execution.
> - 🚧 = Design phase, implementation pending.

---

## Experiment Registry

| Exp ID | Chapter | Name | Hardware Target | Status | Evidence / Oracle |
|:---:|:---:|---|:---:|:---:|---|
| **exp_01** | 01 | `streaming_audio_pipeline` | Host / CPU Simulation | ✅ | Bit-exact STFT buffer slide, Mel filterbank matrix, SNR $> 60\text{ dB}$ |
| **exp_02** | 02 | `jetson_orin_profiler` | NVIDIA Orin Model / Mock | ✅ | P99 latency $< 2.5\text{ ms}$, power model calibration against `tegrastats` |
| **exp_03** | 03 | `batch_one_gpu_bottleneck` | Jetson Orin | 🚧 | SM occupancy & kernel launch profiling |
| **exp_04** | 04 | `fpga_dsp_bram_mapping` | AMD Xilinx UltraScale+ | 🚧 | Resource estimation model |
| **exp_05** | 05 | `finn_vs_dpu_benchmark` | Kria KV260 | 🚧 | Dataflow latency vs DPU overlay comparison |
| **exp_06** | 06 | `hardware_fixed_point_fft` | FPGA Vivado HLS | 🚧 | SQNR vs bitwidth analysis |
| **exp_07** | 07 | `voice_qat_calibration` | PyTorch / Brevitas | 🚧 | INT8 QAT calibration on SpeechCommands/LibriSpeech |
| **exp_08** | 08 | `streaming_conformer_fpga` | Kria KV260 | 🚧 | Attention buffer unrolling |
| **exp_09** | 09 | `pynq_dma_audio_overlay` | Kria KV260 PYNQ | 🚧 | End-to-end DMA streaming |
| **exp_10** | 10 | `pareto_frontier_eval` | Orin vs. Kria KV260 | 🚧 | Multi-dimensional Pareto curves |
