# Cognitive & Reasoning Harness (Pro-Emulation Protocol)

This harness enforces a high-rigor, disciplined reasoning process equivalent to frontier reasoning models (such as Gemini 3.1 Pro) when operating under fast, high-efficiency models (such as Gemini 3.8 Flash High).

## Core Cognitive Mandate

Before executing tools, generating code, or answering complex technical prompts, the agent MUST internally structure its reasoning through the following 5 cognitive phases:

### Phase 1: Intent Decoding & Problem Deconstruction
- **Explicit Goal vs. Implicit Need**: Distinguish what the user asked literally versus what the architecture/system requires to succeed.
- **Context & Constraints Inventory**: Actively enumerate constraints (Edge GPU vs. FPGA resources: BRAM/URAM, DSP slices, power budgets, fixed-point vs floating-point precision, latency budgets).
- **Anti-Rushing Rule**: Do NOT propose code or run modifying tools before understanding the current state of the codebase and inspecting existing patterns.

### Phase 2: First-Principles & Architectural Grounding
- **Mental Model Alignment**: Anchor the problem into the project's core mental models:
  1. Voice Edge System = DSP Preprocessing + Acoustic Model + Microarchitecture.
  2. Migration Flow = GPU Bottleneck Profiling → Quantization → Spatial Architecture Mapping → Pareto Verification.
- **Dependency & Side-Effect Trace**: Map which files, tests, documentation, or chapter skeletons will be impacted.

### Phase 3: Multi-Hypothesis & Counterfactual Evaluation (Stress-Testing)
- **Generate Alternatives**: Brainstorm at least TWO viable technical approaches (e.g., streaming chunk-based vs. frame-by-frame; HLS C++ stream vs. systolic array; fixed-point Q-format vs. INT8 asymmetric).
- **Failure Mode Analysis**: Ask: "Why would this approach fail on hardware or in edge deployment?"
- **Trade-off Matrix**: Formulate explicit trade-offs (Latency vs. Accuracy vs. Resource Utilization vs. Implementation Complexity).

### Phase 4: Pre-Execution Verification Protocol
- Define concrete criteria for success before taking action:
  - Which automated tests must pass (`python -m pytest`)?
  - What linting checks are required (`python -m ruff check .`, `python -m ruff format --check .`)?
  - What numerical tolerances must be met (e.g., SNR > 15 dB, CER degradation < 0.5%)?

### Phase 5: Structured Execution & Self-Correction
- **Execution Plan**: Formulate atomic, verifiable steps.
- **Active Reflection**: After receiving tool output or test results, critique the outcome. If an error or unexpected output occurs, do not guess blindly; inspect root cause from first principles.
