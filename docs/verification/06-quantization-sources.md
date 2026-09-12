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
| conditions | `M = (S1*S2)/S3 = 2^(-n) * M_0, M_0 in [0.5, 1)` |
| source_tier | `T3` |
| doc_id | `CVPR 2018 / arXiv:1712.05877` |
| title | Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference |
| url | https://arxiv.org/pdf/1712.05877.pdf |
| locator | p.3, Section 2.2 'Integer-arithmetic-only matrix multiplication', Equations (4)-(6) |
| quote | where the multiplier M is defined as M := S1*S2 / S3 ... In other words, the multiplication by M can be implemented as a fixed-point multiplication by M0, followed by a bit-shift to account for 2^(-n). |
| retrieved_utc | `2026-09-12T04:25:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | Allows full integer-only matrix multiplication and requantization without any floating-point hardware. |

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
| status | `unresolved` |
| quantity | `torch_round_tie_breaking_mode` |
| value | `` |
| unit | `n/a` |
| conditions | `Needed to prove bit-exact parity between QAT software output and RTL` |
| source_tier | `T2` |
| doc_id | `PyTorch documentation` |
| title | torch.round / torch.ao.quantization rounding behaviour |
| url |  |
| locator |  |
| quote |  |
| retrieved_utc | `2026-09-12T07:18:00Z` |
| access | `open` |
| corroborating_url |  |
| notes | NOT SOURCED. The previous record asserted 'round-half-to-even' for PyTorch on the strength of a quote whose page could not be re-reached: docs.pytorch.org/docs/stable/generated/torch.ao.quantization.quantize_per_tensor.html returned HTTP 404 in this session, and no live PyTorch text was captured. Do not carry a tie-breaking rule into the book or into RTL until it is read from a live PyTorch page or from aten's own rounding implementation. Brevitas' default operator is evidenced in V-06-04; what is missing is the tie rule inherited from torch.round. |
