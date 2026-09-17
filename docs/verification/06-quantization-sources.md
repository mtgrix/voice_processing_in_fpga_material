# Verification Records: 06 Quantization Sources

### V-06-01 · Affine Zero Point Quantization Source

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `affine_zero_point_quantization_source` |
| value | `Jacob et al., CVPR 2018 (Equation 1)` |
| unit | `citation` |
| conditions | `r = S(q - Z), where S is scale and Z is zero-point integer` |
| source_tier | `T3` |
| doc_id | `CVPR 2018 / arXiv:1712.05877` |
| title | Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference |
| url | https://arxiv.org/pdf/1712.05877.pdf |
| locator | p.3, Section 2.1 Quantization scheme, Equation (1) |
| quote | This is equivalent to requiring that the quantization scheme be an affine mapping of integers q to real numbers r, i.e. of the form
r = S(q − Z) (1)
for some constants S and Z. Equation (1) is our quantization scheme and the constants S and Z are our quantization parameters. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Correct foundational citation for affine asymmetric zero-point quantization; replaces incorrect citation of FINN. |

### V-06-02 · Integer Multiply Shift Requantization Source

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `integer_multiply_shift_requantization_source` |
| value | `Jacob et al., CVPR 2018 (Equations 4-6)` |
| unit | `citation` |
| conditions | `M = (S1*S2)/S3 = 2^(-n) * M_0, M_0 in [0.5, 1); the paper's q1 is the weights and q2 the activations` |
| source_tier | `T3` |
| doc_id | `CVPR 2018 / arXiv:1712.05877` |
| title | Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference |
| url | https://arxiv.org/pdf/1712.05877.pdf |
| locator | p.3, Section 2.2 'Integer-arithmetic-only matrix multiplication', Equations (4)-(6); Section 2.4, operand roles |
| quote | where the multiplier M is defined as M := S1*S2 / S3 ... In other words, the multiplication by M can be implemented as a fixed-point multiplication by M0, followed by a bit-shift to account for 2^(-n). ... The normalized multiplier M0 now lends itself well to being expressed as a fixed-point multiplier (e.g. int16 or int32 depending on hardware capability). For example, if int32 is used, the integer representing M0 is the int32 value nearest to 2^31 M0. Since M0 >= 0.5, this value is always at least 2^30 and will therefore always have at least 30 bits of relative accuracy. ... We take the q1 matrix to be the weights, and the q2 matrix to be the activations. |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Allows full integer-only matrix multiplication and requantization without any floating-point hardware. Extended 2026-09-17: quote now also carries the fixed-point word-length guidance (int16/int32, 2^31 nearest, >= 2^30, 30 bits of relative accuracy) and the Section 2.4 operand roles, so chapter 8's requantisation card (S1 weight scale, S2 activation scale, M0 word length) stays traceable to this record. |

### V-06-03 · Finn Framework Scope

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `finn_framework_scope` |
| value | `Framework for Binarized Neural Networks (BNNs) on FPGAs` |
| unit | `n/a` |
| conditions | `1-bit weights and activations (XNOR / popcount) and streaming dataflow` |
| source_tier | `T3` |
| doc_id | `ACM FPGA 2017 / arXiv:1612.07119` |
| title | FINN: A Framework for Fast, Scalable Binarized Neural Network Inference on FPGAs |
| url | https://arxiv.org/pdf/1612.07119.pdf |
| locator | p.1, Abstract and Section 1 Introduction |
| quote | In this paper, we present Finn, a framework for building fast and flexible FPGA accelerators using a flexible heterogeneous streaming architecture. By utilizing a novel set of optimizations that enable efficient mapping of binarized neural networks to hardware ... Binarized Neural Networks (BNNs), proposed by Courbariaux et al. [5], are particularly appealing since they can be implemented almost entirely with binary operations |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | FINN is an FPGA dataflow implementation framework for BNNs/QNNs; it is not the theoretical origin of affine zero-point quantization. |

### V-06-04 · Qat Default Rounding Operator

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `qat_default_rounding_operator` |
| value | `Brevitas default float_to_int_impl = RoundSte (torch.round with a straight-through estimator)` |
| unit | `operator` |
| conditions | `Brevitas master branch read via the GitHub contents API on 2026-09-12; IntQuant and Int8WeightPerTensorFloat defaults` |
| source_tier | `T2` |
| doc_id | `Brevitas master, read 2026-09-12` |
| title | Brevitas source: brevitas.core.quant.int_base and brevitas.function.ops_ste |
| url | https://github.com/Xilinx/brevitas/blob/master/src/brevitas/core/quant/int_base.py |
| locator | src/brevitas/core/quant/int_base.py lines 25, 55, 131; src/brevitas/function/ops_ste.py lines 47-53; src/brevitas/core/quant/int.py line 286 |
| quote | float_to_int_impl: Module = RoundSte() ... def round_ste(x: Tensor) -> Tensor: Function that implements torch.round with a straight-through gradient estimator. ... y = round_ste(y)  # clean up floating point error |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url | https://github.com/Xilinx/brevitas/blob/master/src/brevitas/function/ops_ste.py |
| notes | CORRECTED 2026-09-12. The previous record cited only the torch.round documentation, which says nothing about what a QAT library actually uses, and asserted 'Round-half-to-even (PyTorch/Brevitas)'; the Brevitas half was unsourced. Now evidenced: Brevitas quantizers default to RoundSte, which wraps torch.round, so the software path rounds to nearest. The tie-breaking rule is a property of torch.round and is NOT evidenced here - see V-06-05. This matters because RTL right-shift truncation matches nearest-with-any-tie only if the design implements that rounding explicitly. |

### V-06-05 · Torch Round Tie Breaking Mode

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `torch_round_tie_breaking_mode` |
| value | `round half to even` |
| unit | `string` |
| conditions | `torch.round() in the PyTorch documentation as published 2026-09-12 (version 2.14)` |
| source_tier | `T2` |
| doc_id | `PyTorch 2.14 documentation` |
| title | torch.round - PyTorch documentation |
| url | https://docs.pytorch.org/docs/2.14/generated/torch.round.html |
| locator | torch.round page, description paragraph |
| quote | This function implements the "round half to even" to break ties when a number is equidistant from two integers (e.g. round(2.5) is 2) |
| retrieved_utc | `2026-09-12T12:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | RESOLVED on the second pass. The first pass could not re-reach the page and therefore asserted nothing, which is why this record sat unresolved. Two fetch notes worth keeping: docs.pytorch.org/docs/stable/generated/torch.round.html returns only a 'Redirecting...' shell to a scripted fetcher, and the versioned URL above is what carries the text, so a checker reading the stable URL sees no claim to check. The quoted sentence is the tie rule Brevitas inherits (V-06-04) and that an RTL fixed-point pipeline usually does not implement, since adding (1 << (shift-1)) rounds ties toward positive infinity (at shift = 1 it maps -3 to -1, -1 to 0, 1 to 1 and 3 to 2): three tie behaviours across one toolchain, which is the bit-exactness trap this record was opened for. |

### V-06-06 · Conv Bn Fusion Rewrites Preceding Weights

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `conv_bn_fusion_rewrites_preceding_weights` |
| value | `the batch norm is folded into the preceding convolution's weights and deleted from the graph` |
| unit | `string` |
| conditions | `PyTorch tutorial text as served on 2026-09-14 by the page stamped 2.14.0+cu130. A description of what a framework compiler does, not a measurement of any model.` |
| source_tier | `T2` |
| doc_id | `PyTorch Tutorials 2.14, Convolution/Batch Norm fuser` |
| title | Building a Convolution/Batch Norm fuser with torch.compile — PyTorch Tutorials 2.14.0+cu130 documentation |
| url | https://docs.pytorch.org/tutorials/intermediate/torch_compile_conv_bn_fuser.html |
| locator | Section 'Fusing Convolution with Batch Norm' (the second of the page's two headings with that name) |
| quote | Unlike some other fusions, fusion of convolution with batch norm does not require any new operators. Instead, as batch norm during inference consists of a pointwise add and multiply, these operations can be “baked” into the preceding convolution’s weights. This allows us to remove the batch norm entirely from our model! |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The half of chapter 5.4's argument that a fusion pass changes which layers exist rather than how fast the same layers run: the batch norm is not optimised, it is removed, because at inference it is a pointwise add and multiply that can be folded into the weights beside it. Chapter 9 states the same consequence for this book's model in the register-transfer voice; this record is what lets chapter 5 say it as a documented property of a toolchain. |

### V-06-07 · Compiler Graph Capture Exposes Nested Patterns

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `compiler_graph_capture_exposes_nested_patterns` |
| value | `a compiling pass captures the graph, so patterns inside nested containers and wrapper modules become visible to a matcher that could not otherwise reach them` |
| unit | `string` |
| conditions | `PyTorch tutorial text as served on 2026-09-14 by the page stamped 2.14.0+cu130. A description of what a framework compiler does, not a measurement of any model.` |
| source_tier | `T2` |
| doc_id | `PyTorch Tutorials 2.14, Convolution/Batch Norm fuser` |
| title | Building a Convolution/Batch Norm fuser with torch.compile — PyTorch Tutorials 2.14.0+cu130 documentation |
| url | https://docs.pytorch.org/tutorials/intermediate/torch_compile_conv_bn_fuser.html |
| locator | Section 'Fusing Convolution with Batch Norm' (the first of the page's two headings with that name) |
| quote | One of the primary challenges with trying to automatically fuse convolution and batch norm in PyTorch is that PyTorch does not provide an easy way of accessing the computational graph. torch.compile resolves this problem by capturing the computational graph during compilation, allowing us to apply pattern-based optimizations across the entire model, including operations nested within Sequential modules or wrapped in custom modules. |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Why the rewrite is a compiler pass and not a library call: the pattern has to be found in a captured graph, and modules hidden inside containers are only visible once compilation has inlined them. Chapter 5.4 uses this to say that the graph a reader inspects in the training framework is not the object the accelerator runs, which is the sentence the measurement argument rests on. |

### V-06-08 · Conv Bn Fusion Legality Needs Inference Mode

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `conv_bn_fusion_legality_needs_inference_mode` |
| value | `the fold is valid only in inference mode, while the pattern matcher itself works in both modes` |
| unit | `string` |
| conditions | `PyTorch tutorial text as served on 2026-09-14 by the page stamped 2.14.0+cu130. A description of what a framework compiler does, not a measurement of any model.` |
| source_tier | `T2` |
| doc_id | `PyTorch Tutorials 2.14, Convolution/Batch Norm fuser` |
| title | Building a Convolution/Batch Norm fuser with torch.compile — PyTorch Tutorials 2.14.0+cu130 documentation |
| url | https://docs.pytorch.org/tutorials/intermediate/torch_compile_conv_bn_fuser.html |
| locator | Prerequisites note, before the first code block |
| quote | This optimization only works for models in inference mode (i.e. model.eval()). However, torch.compile’s pattern matching system works for both training and inference. |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The condition, separated from the mechanism. It matters for the book's own argument because the statistics the fold consumes are the stored inference-time ones, so fusion belongs to the same family as calibration: both need the model to have been run and measured before the arithmetic is fixed. The typographic apostrophe in the second sentence is the vendor's, kept as printed. |

### V-06-09 · Conv Bn Fusion Implementation And Arithmetic

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `conv_bn_fusion_implementation_and_arithmetic` |
| value | `an implementation that asserts eval mode, refuses a batch norm without running buffers, and rewrites the weight tensor by a per-channel scale` |
| unit | `string` |
| conditions | `The module torch/nn/utils/fusion.py at the release tag v2.10.0, read from the repository the same day. Source code rather than prose: the behaviour is what the file enforces.` |
| source_tier | `T2` |
| doc_id | `PyTorch v2.10.0 source, torch/nn/utils/fusion.py` |
| title | torch/nn/utils/fusion.py (PyTorch v2.10.0) |
| url | https://raw.githubusercontent.com/pytorch/pytorch/v2.10.0/torch/nn/utils/fusion.py |
| locator | fuse_conv_bn_eval docstring note and guard; fuse_conv_bn_weights body |
| quote | Both ``conv`` and ``bn`` must be in eval mode, and ``bn`` must have its running buffers computed. ... assert not (conv.training or bn.training), "Fusion only for eval!" ... fused_conv_w = (conv_w * (bn_w * bn_var_rsqrt).reshape(shape)) |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered at a release tag rather than a branch, because the same file on the development branch enforces the identical condition with a different statement form: at v2.10.0 the guard reads 'assert not (conv.training or bn.training)' and on the later main branch it is an 'if' that raises AssertionError. The message string is unchanged in both, which is what makes the citation safe either way. The quoted expression is the per-channel multiply that chapter 5.4 gives as the mechanism, and chapter 8's LayerNorm contrast depends on it being a stored per-channel value rather than a runtime reduction. |

### V-06-10 · Ptq Scale And Rounding Option Surface

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ptq_scale_and_rounding_option_surface` |
| value | `the quantizer's documented choices for how a scale is calibrated, how values are rounded, and how disagreement between batches is resolved` |
| unit | `string` |
| conditions | `The vai_q_pytorch configuration document at Vitis-AI commit 77cb9e6ad6749de55cf6de8d4959b1cb4b27020e. A tool's documented option surface, not a measurement; it describes the PyTorch quantizer, which targets the DPU.` |
| source_tier | `T2` |
| doc_id | `Vitis AI Quantizer (vai_q_pytorch) documentation` |
| title | Vitis AI Quantizer (vai_q_pytorch): Quant_Config.md |
| url | https://raw.githubusercontent.com/Xilinx/Vitis-AI/77cb9e6ad6749de55cf6de8d4959b1cb4b27020e/src/vai_quantizer/vai_q_pytorch/doc/Quant_Config.md |
| locator | Parameter list: the method, round_mode and calib_statistic_method entries |
| quote | method: method used to calibrate the quantization “scale”, options: maxmin, percentile, entropy, mse, diffs. round_mode: rounding method in quantization process, options: half_even, half_up, half_down, std_round. ... calib_statistic_method: method to choose one optimal “scale” if got different scales using multiple batch data, option: modal, max, mean, median. |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Chapter 5.4's calibration half. What this record establishes is that the scale in V-06-01's affine mapping is not computed one way: it is the output of a chosen estimator, and the quantizer documents five of them, four rounding behaviours, and four statistics for combining batches. The option names are quoted as printed, including 'if got different scales', which is the tool's own phrasing. |

### V-06-11 · Ptq Option Conflicts Are Refused

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ptq_option_conflicts_are_refused` |
| value | `combinations of calibration method, statistic method and symmetry that the quantizer rejects with an error rather than resolving` |
| unit | `string` |
| conditions | `The vai_q_pytorch configuration document at Vitis-AI commit 77cb9e6ad6749de55cf6de8d4959b1cb4b27020e. A tool's documented option surface, not a measurement; it describes the PyTorch quantizer, which targets the DPU.` |
| source_tier | `T2` |
| doc_id | `Vitis AI Quantizer (vai_q_pytorch) documentation` |
| title | Vitis AI Quantizer (vai_q_pytorch): Quant_Config.md |
| url | https://raw.githubusercontent.com/Xilinx/Vitis-AI/77cb9e6ad6749de55cf6de8d4959b1cb4b27020e/src/vai_quantizer/vai_q_pytorch/doc/Quant_Config.md |
| locator | Closing paragraph on configuration conflicts |
| quote | However, there are some conflicts when using different configurations. For example, if calibration method is ‘maxmin’, ‘percentile’, ‘mse’ or ‘entropy’,  the calibration statistic method ‘modal’ is not supported. If symmetry mode is asymmetry, the calibration method ‘mse’ and ‘entropy’ are not supported. Quantization tool will give error message if there exist configuration conflicts. |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The point worth teaching: the option surface is not free. Percentile and entropy estimators are unavailable for asymmetric ranges, and the modal statistic is incompatible with four of the five scale estimators. So a quantized result is a property of a configuration that had to be admissible, which is why chapter 5.4 insists that a reported accuracy or latency names its calibration configuration as well as its device. The double space inside the second sentence is in the source and is kept. |

### V-06-12 · Ptq Layer Names Exist After Calibration

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `ptq_layer_names_exist_after_calibration` |
| value | `naming a layer to override its configuration requires the calibration run to have completed, because the names come from that run's emitted file` |
| unit | `string` |
| conditions | `The vai_q_pytorch configuration document at Vitis-AI commit 77cb9e6ad6749de55cf6de8d4959b1cb4b27020e. A tool's documented option surface, not a measurement; it describes the PyTorch quantizer, which targets the DPU.` |
| source_tier | `T2` |
| doc_id | `Vitis AI Quantizer (vai_q_pytorch) documentation` |
| title | Vitis AI Quantizer (vai_q_pytorch): Quant_Config.md |
| url | https://raw.githubusercontent.com/Xilinx/Vitis-AI/77cb9e6ad6749de55cf6de8d4959b1cb4b27020e/src/vai_quantizer/vai_q_pytorch/doc/Quant_Config.md |
| locator | Layer configuration notes |
| quote | If setting based on layer name, the model needs to run the calibration process firstly, then pick the required layer name from the generated .py file in quantized_result directory. Besides, the “layer_type” parameter should be null. |
| retrieved_utc | `2026-09-14T06:26:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | The sharpest available evidence that the compiled graph, not the framework graph, is the object of the work: the tool cannot point at a layer by name until it has produced the quantized model, and it tells the user to read the names out of a generated file. Chapter 5.4 uses it for the sentence about why an operator count taken before the tool ran describes a model nobody deploys. |

### V-06-13 · Nemo Streaming Conformer Feature Window Size

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_feature_window_size` |
| value | `0.025` |
| unit | `seconds` |
| conditions | `the mel front end of cache-aware streaming Conformer-Transducer recipe config `conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml`, with window_stride 0.01 at line 70, features 80 at line 72 and n_fft 512 at line 73` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 69, model.preprocessor.window_size |
| quote |     window_size: 0.025 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | Twenty-five milliseconds, the Hamming/Hann window length that maps to 400 samples at 16 kHz. V-05-31 registers the companion stride 0.01 s; together the two values fix the frame/hop pair (400/160 samples) used throughout chapter 6. |

### V-06-14 · Nemo Streaming Conformer Frontend N Fft

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `nemo_streaming_conformer_frontend_n_fft` |
| value | `512` |
| unit | `FFT points` |
| conditions | `the mel front end of cache-aware streaming Conformer-Transducer recipe config, with window_size 0.025 at line 69, window_stride 0.01 at line 70 and features 80 at line 72` |
| source_tier | `T2` |
| doc_id | `NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Line 73, model.preprocessor.n_fft |
| quote |     n_fft: 512 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | 512-point FFT, the transform size that produces 257 frequency bins for 80 Mel bands. The frame is only 400 samples long, so the remaining 112 input slots are zero-padded. |

### V-06-15 · Audio Frame Length Samples

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `audio_frame_length_samples` |
| value | `400` |
| unit | `samples` |
| conditions | `derived from NeMo config: window_size 0.025 s (V-06-13) multiplied by sample rate 16,000 Hz (V-05-10/V-05-11)` |
| source_tier | `T2` |
| doc_id | `Derived from NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config and OpenSLR 12` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Derived from V-06-13 window_size and V-05-10 sample rate; arithmetic derivation: 0.025 * 16000 = 400 |
| quote | window_size: 0.025 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | arithmetic derivation: 0.025 * 16,000 = 400 |

### V-06-16 · Audio Hop Size Samples

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `audio_hop_size_samples` |
| value | `160` |
| unit | `samples` |
| conditions | `derived from NeMo config: window_stride 0.01 s (V-05-31) multiplied by sample rate 16,000 Hz (V-05-10/V-05-11)` |
| source_tier | `T2` |
| doc_id | `Derived from NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config and OpenSLR 12` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Derived from V-05-31 window_stride and V-05-10 sample rate; arithmetic derivation: 0.01 * 16000 = 160 |
| quote | window_stride: 0.01 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | arithmetic derivation: 0.01 * 16,000 = 160 |

### V-06-17 · Fft Size From Frame

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `fft_size_from_frame` |
| value | `512` |
| unit | `FFT points` |
| conditions | `derived: smallest power of two not less than frame length 400 (V-06-15); matches NeMo config n_fft 512 (V-06-14)` |
| source_tier | `T2` |
| doc_id | `Derived from NeMo Cache-Aware Streaming Conformer-Transducer Recipe Config` |
| title | NeMo conformer_transducer_bpe_streaming.yaml |
| url | https://raw.githubusercontent.com/NVIDIA-NeMo/Speech/75e441d6919834c68b206092bf22f4ae102f0264/examples/asr/conf/conformer/cache_aware_streaming/conformer_transducer_bpe_streaming.yaml |
| locator | Derived from V-06-15 frame length; arithmetic derivation: next_pow2(400) = 512, confirmed by V-06-14 n_fft |
| quote | n_fft: 512 |
| retrieved_utc | `2026-09-13T21:32:56Z` |
| access | `open` |
| corroborating_url |  |
| notes | arithmetic derivation: next_pow2(400) = 512 |

### V-06-18 · Cic Hogenauer 1981 Source

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `cic_hogenauer_1981_source` |
| value | `Hogenauer, IEEE TASSP vol 29 no 2 pp 155-162, 1981` |
| unit | `citation` |
| conditions | `primary source for CIC decimation filter theory and the closed-form register-width formula used in section 6.1` |
| source_tier | `T3` |
| doc_id | `IEEE TASSP 1981` |
| title | An Economical Class of Digital Filters for Decimation and Interpolation |
| url | https://doi.org/10.1109/TASSP.1981.1163535 |
| locator | pp 155-162 |
| quote | An Economical Class of Digital Filters for Decimation and Interpolation |
| retrieved_utc | `2026-09-17T00:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered for chapter 6 CIC decimation derivation (section 6.1). Verified via Crossref; no open-access preprint exists. |

### V-06-19 · R2Sdf Fft He Torkelson 1996 Source

| Field | Value |
|---|---|
| status | `verified` |
| quantity | `r2sdf_fft_he_torkelson_1996_source` |
| value | `He & Torkelson, IPPS-96 pp 766-770, 1996` |
| unit | `citation` |
| conditions | `primary source for the R2SDF (radix-2 single-path delay feedback) pipeline FFT microarchitecture used in section 6.3` |
| source_tier | `T3` |
| doc_id | `IPPS 1996 (R2SDF FFT)` |
| title | A New Approach to Pipeline FFT Processor |
| url | https://doi.org/10.1109/IPPS.1996.508145 |
| locator | pp 766-770 |
| quote | A New Approach to Pipeline FFT Processor |
| retrieved_utc | `2026-09-17T00:00:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Registered for chapter 6 fixed-point FFT microarchitecture derivation (section 6.3). Verified via Crossref; DOI 10.1109/IPPS.1996.508119 is an unrelated genetic-algorithms paper. |
