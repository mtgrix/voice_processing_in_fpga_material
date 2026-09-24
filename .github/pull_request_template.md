## Description

Briefly describe the change, motivation, and context.

Fixes #(issue number)

## Type of Change

- [ ] `feat`: New experiment, hardware kernel, or monograph section
- [ ] `fix`: Bug fix in code, formula, or script
- [ ] `docs`: Documentation, citation, or monograph refinement
- [ ] `test`: New or updated tests
- [ ] `perf`: Hardware/software performance optimization
- [ ] `refactor`: Structural improvement without functional change

## Hardware Tested (if applicable)

- [ ] None / Host CPU simulation only
- [ ] NVIDIA Jetson Orin (Nano / NX)
- [ ] AMD Xilinx FPGA (Kria KV260 / Zynq UltraScale+)

## Verification & Quality Checklist

- [ ] Code formatted with `ruff format --check .`
- [ ] Linting passed with `ruff check .`
- [ ] Static types verified with `mypy .`
- [ ] Unit tests passed with `pytest`
- [ ] Integrity check passed with `python scripts/verify_integrity.py`
- [ ] Any numeric hardware/algorithmic claims are registered in `docs/verification/claims.json` or `docs/source_index.json`
- [ ] Experiment READMEs follow the 13-section template (if touching experiments)
