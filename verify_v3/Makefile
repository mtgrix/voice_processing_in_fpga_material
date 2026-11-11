# verify_v3/Makefile
# Target ch00: runs all verification scripts for Chapter 0

PYTHON ?= python

.PHONY: all ch00 ch01 ch02 ch03 ch04 ch05 ch06 clean

all: ch00 ch01 ch02 ch03 ch04 ch05 ch06

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

ch01:
	@echo "=== [ch01] Generating test WAV stimuli ==="
	$(PYTHON) make_test_wavs.py
	@echo "=== [ch01] Running WAV parser and globalPeak verification ==="
	$(PYTHON) ch01_wav_verify.py > ch01_wav_verify.log
	@echo "=== [ch01] Running Praat frame grid and floor trap verification ==="
	$(PYTHON) ch01_frames_verify.py > ch01_frames_verify.log
	@echo "=== [ch01] Running Praat 7.0.03 line citations verification ==="
	$(PYTHON) ch01_praat_lines.py > ch01_praat_lines.log
	@echo "=== [ch01] Running Avalon FIFO twin and backpressure test ==="
	$(PYTHON) ch01_fifo_test.py > ch01_fifo_test.log
	@echo "=== [ch01] Running HPS C driver end-to-end simulation test ==="
	$(PYTHON) ch01_driver_test.py > ch01_driver_test.log
	@echo "=== [ch01] All Chapter 1 verifications completed successfully ==="

ch02:
	@echo "=== [ch02] Running Avalon-ST handshake and readyLatency trace ==="
	$(PYTHON) ch02_avalon_st_trace.py > ch02_avalon_st_trace.log
	@echo "=== [ch02] Running file-driven cycle budget derivation and audit ==="
	$(PYTHON) ch02_cycle_budget.py > ch02_cycle_budget.log
	@echo "=== [ch02] Running Gray code trailing-ones mathematical verification ==="
	$(PYTHON) ch02_gray_code.py > ch02_gray_code.log
	@echo "=== [ch02] Running Skid buffer twin and vector generation ==="
	$(PYTHON) ch02_skid_twin.py > ch02_skid_twin.log
	@echo "=== [ch02] Running FSM twin and binary vs onehot vector generation ==="
	$(PYTHON) ch02_fsm_twin.py > ch02_fsm_twin.log
	@echo "=== [ch02] Checking Praat citations ==="
	$(PYTHON) ch02_praat_lines.py > ch02_praat_lines.log
	@echo "=== [ch02] All Chapter 2 verifications completed successfully ==="

ch03:
	@echo "=== [ch03] Running FIR design and frequency response audit ==="
	$(PYTHON) ch03_fir_design.py > ch03_fir_design.log
	@echo "=== [ch03] Running FIR twin and stimulus vector generation ==="
	$(PYTHON) ch03_fir_twin.py > ch03_fir_twin.log
	@echo "=== [ch03] Running Praat citations audit ==="
	$(PYTHON) ch03_praat_lines.py > ch03_praat_lines.log
	@echo "=== [ch03] Running chapter exercises verification ==="
	$(PYTHON) ch03_exercises.py > ch03_exercises.log
	@echo "=== [ch03] All Chapter 3 verifications completed successfully ==="

ch04:
	@echo "=== [ch04] Running Praat frame geometry and floor trap audit ==="
	$(PYTHON) ch04_frame_grid.py > ch04_frame_grid.log
	@echo "=== [ch04] Running Praat 7.0.03 citations audit ==="
	$(PYTHON) ch04_praat_lines.py > ch04_praat_lines.log
	@echo "=== [ch04] Running Ring Buffer twin and vector generation ==="
	$(PYTHON) ch04_ring_buffer_twin.py > ch04_ring_buffer_twin.log
	@echo "=== [ch04] Running chapter exercises verification ==="
	$(PYTHON) ch04_exercises.py > ch04_exercises.log
	@echo "=== [ch04] All Chapter 4 verifications completed successfully ==="

ch05:
	@echo "=== [ch05] Running Praat citations and double vs int mean audit ==="
	$(PYTHON) ch05_praat_lines.py > ch05_praat_lines.log
	@echo "=== [ch05] Running reciprocal division mathematical audit ==="
	$(PYTHON) ch05_mean_math.py > ch05_mean_math.log
	@echo "=== [ch05] Running DC effect and DC-blocker analysis ==="
	$(PYTHON) ch05_dc_effect.py > ch05_dc_effect.log
	@echo "=== [ch05] Running Local Mean and DC-Blocker twin vector generation ==="
	$(PYTHON) ch05_mean_twin.py > ch05_mean_twin.log
	@echo "=== [ch05] Running chapter exercises verification ==="
	$(PYTHON) ch05_exercises.py > ch05_exercises.log
	@echo "=== [ch05] All Chapter 5 verifications completed successfully ==="

ch06:
	@echo "=== [ch06] Running Praat citations audit ==="
	$(PYTHON) ch06_praat_lines.py > ch06_praat_lines.log
	@echo "=== [ch06] Running Hanning N+1 mathematical audit ==="
	$(PYTHON) ch06_hanning_math.py > ch06_hanning_math.log
	@echo "=== [ch06] Running 17-bit dynamic range and stress frame audit ==="
	$(PYTHON) ch06_stress_audit.py > ch06_stress_audit.log
	@echo "=== [ch06] Running chapter exercises verification ==="
	$(PYTHON) ch06_exercises.py > ch06_exercises.log
	@echo "=== [ch06] Running Hanning window twin and vector generation ==="
	$(PYTHON) ch06_window_twin.py > ch06_window_twin.log
	@echo "=== [ch06] All Chapter 6 verifications completed successfully ==="

clean:
	rm -f *.log sim_ch00_* tb_ch00_configs.txt tb_ch00_dump_small.txt test_ch01_* ch01_driver_sim* pitch_f0.bin pitch_meta.txt tb_ch01_fifo_stim.txt tb_ch01_fifo_expected.txt tb_ch01_fifo_out_stim.txt tb_ch01_fifo_out_expected.txt tb_ch02_skid_stim.txt tb_ch02_skid_expected.txt tb_ch02_fsm_stim.txt tb_ch02_fsm_expected.txt sim_ch02_* tb_ch03_fir_stim.txt tb_ch03_fir_expected.txt sim_ch03_* tb_ch04_ring_buffer_stim.txt tb_ch04_ring_buffer_expected.txt sim_ch04_* tb_ch05_mean_stim.txt tb_ch05_mean_expected.txt tb_ch05_dc_blocker_stim.txt tb_ch05_dc_blocker_expected.txt sim_ch05_* tb_ch06_hanning_stim.txt tb_ch06_hanning_expected.txt sim_ch06_*
