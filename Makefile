PDF=uoc_luong_f0_praat_fpga_quartus_vi.pdf
TEX=uoc_luong_f0_praat_fpga_quartus_vi.tex
.PHONY: pdf test hex
pdf:
	xelatex -interaction=nonstopmode $(TEX)
	xelatex -interaction=nonstopmode $(TEX)
	cp -f $(PDF) /workspace/uploads/$(PDF)
test:
	python3 -m pytest test_lab_1_3_5.py -q
hex:
	python3 lab_1_3_5.py --export-hex hex
