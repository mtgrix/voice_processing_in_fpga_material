# verify_v3/Makefile
# Target ch00: runs all verification scripts for Chapter 0

PYTHON ?= python3

.PHONY: all ch00 clean

all: ch00

ch00:
	@echo "=== [ch00] Running naive methods verification ==="
	$(PYTHON) ch00_naive_methods.py > ch00_naive_methods.log
	@echo "=== [ch00] Running window normalization verification ==="
	$(PYTHON) ch00_norm_sine.py > ch00_norm_sine.log
	@echo "=== [ch00] Running Praat 7.0.03 line citations verification ==="
	$(PYTHON) ch00_praat_lines.py > ch00_praat_lines.log
	@echo "=== [ch00] Running metrics verification ==="
	$(PYTHON) ch00_metrics.py > ch00_metrics.log
	@echo "=== [ch00] Running golden table recomputation (fine cents) ==="
	$(PYTHON) ch00_table_golden.py > ch00_table_golden.log
	@echo "=== [ch00] Running cycle budget verification ==="
	$(PYTHON) ch00_cycle_budget.py > ch00_cycle_budget.log
	@echo "=== [ch00] Running golden v2 spec verification ==="
	$(PYTHON) ch00_golden_spec.py > ch00_golden_spec.log
	@echo "=== [ch00] Running chapter exercises verification ==="
	$(PYTHON) ch00_exercises.py > ch00_exercises.log
	@echo "=== [ch00] Running pair counter RTL + TB verification (iverilog) ==="
	cd .. && $(PYTHON) verify_v3/ch00_test_pair_counter.py
	@echo "=== [ch00] All Chapter 0 verifications completed successfully ==="

clean:
	rm -f *.log sim_ch00_* tb_ch00_configs.txt tb_ch00_dump_small.txt
