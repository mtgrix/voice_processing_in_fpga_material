#!/usr/bin/env python3
"""verify_v3/ch12_cycle_table.py
Exact cycle budget derivation and comparison for Chapter 12:
- Hop 160 budget at 50 MHz = 500,000 cycles (10 ms)
- Breakdown of every per-frame phase:
    1. Local mean calculation (426 samples: 106..531)
    2. Local mean subtraction, Hanning window, and LocalPeak LP (638 samples)
    3. Autocorrelation MAC (R[0] + 189 lags)
    4. C, K ROM, peak search, parabolic interpolation, division
    5. Voicing gate and median-3
- Non-overlap total vs double-buffered overlap total
- Print agenda value, measured value, and exact difference
"""

def derive_cycle_table():
    f_clk = 50_000_000
    fs = 16_000
    hop = 160
    hop_cycles = (f_clk // fs) * hop # 500,000
    
    print("=== CH12 PER-FRAME CYCLE TABLE DERIVATION (HOP 160) ===")
    print(f"System clock: 50 MHz (T_clk = 20 ns)")
    print(f"Sampling rate: 16 kHz (T_s = 62.5 us)")
    print(f"Hop size: {hop} samples ({hop / fs * 1000:.1f} ms)")
    print(f"Cycles available per hop (real-time deadline): {hop_cycles} cycles\n")
    
    # Phase 1: Local Mean (426 samples)
    # 426 read issue beats + 2 memory read latency + 1 mult1 + 1 mult2 + 1 done = 426 + 3 (wait_rd overlap) = 429
    p1_samples = 426
    p1_latency = 3
    p1_cycles = p1_samples + p1_latency # 429
    
    # Phase 2: Mean subtraction + Hanning window + LocalPeak LP (638 samples)
    # 638 sample read issue beats + 2 memory latency + 1 subtraction + 2 window pipeline = 638 + 3 = 641
    p2_samples = 638
    p2_latency = 3
    p2_cycles = p2_samples + p2_latency # 641
    
    # Phase 3: MAC Engine (R[0] + 189 lags)
    # R[0]: 638 pairs
    # Lags 26..214: sum_{tau=26}^{214} (638 - tau) = 97,902 pairs
    # Total issue beats = 638 + 97,902 = 98,540 beats
    # Pipeline drain latency = 3 cycles (1 M10K + 1 in_reg + 1 dsp_acc)
    # Total MAC cycles = 98,540 + 3 = 98,543 cycles
    mac_r0 = 638
    mac_lags = sum(638 - tau for tau in range(26, 215)) # 97902
    mac_issue = mac_r0 + mac_lags # 98540
    mac_latency = 3
    p3_cycles = mac_issue + mac_latency # 98543
    
    # Phase 4 & 5: Norm, Score, Peak Finder, Radix-2 Divider, Voicing Gate
    # Lags 26..214 are evaluated in pipeline streaming concurrent with MAC.
    # After lag 214 completes at cycle 98,543:
    # 3 cycles norm_score pipeline tail -> out_last asserted
    # 2 cycles peak_finder / divider controller setup (calc den, s2, D)
    # 34 cycles radix-2 divider execution (34 quotient bits)
    # 1 cycle divider result latching and rounding
    # 3 cycles voicing gate pipeline
    # Total post-MAC tail = 3 + 2 + 34 + 1 + 3 = 43 cycles
    p4_5_tail = 3 + 2 + 34 + 1 + 3 # 43 cycles
    
    # Phase 6 & 7: Median-3 filter and FSM phase handshakes
    # 1 cycle median-3 registered update
    # FSM state transition handshakes: 1 cycle per phase transition * 6 transitions = 6 cycles
    p6_7_cycles = 1 + 6 # 7 cycles
    
    # Non-overlap baseline total
    measured_total = p1_cycles + p2_cycles + p3_cycles + p4_5_tail + p6_7_cycles # 99,663 cycles
    measured_rtf = measured_total / hop_cycles
    
    # Agenda estimates
    agenda_mac = 98543
    agenda_total = 99700
    agenda_rtf = 0.1994
    
    print("--- Detailed Phase Breakdown (Baseline Non-Overlap) ---")
    print(f"Phase 1 (Local Mean, 426 samples):              {p1_cycles:6d} cycles  (426 issue + 3 latency)")
    print(f"Phase 2 (Sub Mean, Hanning, LP, 638 samples):   {p2_cycles:6d} cycles  (638 issue + 3 pipeline)")
    print(f"Phase 3 (Autocorrelation MAC Engine):          {p3_cycles:6d} cycles  (98,540 issue + 3 drain)")
    print(f"Phase 4-5 (Divider tail + Voicing gate):         {p4_5_tail:6d} cycles  (3 tail + 2 prep + 34 div + 1 rnd + 3 voice)")
    print(f"Phase 6-7 (Median-3 + FSM handshakes):           {p6_7_cycles:6d} cycles")
    print(f"Total per-frame cycles (Model):                {measured_total:6d} cycles")
    print(f"Model core RTF:                                {measured_rtf:.6f} (approx {measured_rtf:.3f})")
    print(f"Agenda estimated total:                        {agenda_total:6d} cycles")
    print(f"Agenda estimated RTF:                          {agenda_rtf:.4f} (approx 0.199)")
    print(f"Difference (Agenda - Model):                   {agenda_total - measured_total:+6d} cycles ({((agenda_total - measured_total)/agenda_total)*100:+.2f}%)\n")
    
    # Double-buffering overlap architecture
    # Phase 1 + Phase 2 of frame k+1 (429 + 641 = 1,070 cycles) run concurrently with Phase 3 (98,543 cycles) of frame k.
    # Overhead remaining = Phase 3 + post-MAC tail + FSM handshakes (2 cycles)
    overlap_hidden = p1_cycles + p2_cycles # 1070 cycles
    overlap_total = p3_cycles + p4_5_tail + 3 # 98589 cycles
    overlap_rtf = overlap_total / hop_cycles
    agenda_overlap = 98600
    agenda_overlap_rtf = 0.1972
    
    print("--- Double-Buffered Overlap Architecture ---")
    print(f"Hidden pre-processing cycles (P1 + P2):        {overlap_hidden:6d} cycles  (< 98,543 cycles)")
    print(f"Overlap execution cycles (Model):              {overlap_total:6d} cycles")
    print(f"Overlap model core RTF:                        {overlap_rtf:.6f} (approx {overlap_rtf:.3f})")
    print(f"Agenda estimated overlap total:                {agenda_overlap:6d} cycles")
    print(f"Agenda estimated overlap RTF:                  {agenda_overlap_rtf:.4f} (approx 0.197)")
    print(f"Difference (Agenda - Overlap model):           {agenda_overlap - overlap_total:+6d} cycles\n")
    
    # Trade-off analysis
    speedup_cycles = measured_total - overlap_total
    speedup_pct = (speedup_cycles / measured_total) * 100
    print("--- Options, Trade-offs, and Architectural Choice ---")
    print(f"Speedup from double-buffering:                 {speedup_cycles} cycles ({speedup_pct:.2f}%)")
    print(f"RTF improvement:                               {measured_rtf:.4f} -> {overlap_rtf:.4f} (delta = {measured_rtf - overlap_rtf:.4f})")
    print(f"Hardware memory cost:                          +2 M10K blocks (4 M10K instead of 2 for xw_ram)")
    print(f"Baseline real-time margin:                     {hop_cycles / measured_total:.2f}x faster than real-time (1.99 ms vs 10 ms deadline)")
    print("Conclusion: Baseline non-overlap provides 5.02x real-time performance while saving 2 M10K blocks and minimizing FSM complexity.")

if __name__ == '__main__':
    derive_cycle_table()
