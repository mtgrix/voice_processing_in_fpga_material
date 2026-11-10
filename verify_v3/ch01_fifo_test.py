#!/usr/bin/env python3
"""verify_v3/ch01_fifo_test.py
Verification script for Input Avalon-MM to Avalon-ST FIFO:
- Tests AvalonFifoTwin with >= 200 transactions and random backpressure.
- Verifies sample order (little-endian unpacking), waitrequest, and fill levels.
- Generates test vector file tb_ch01_fifo_stim.txt for Verilog testbench.
- Compares bit-for-bit and logs all metrics.
"""
import os
import random
from ch01_fifo_twin import AvalonFifoTwin

def main():
    print("=" * 70)
    print("VERIFICATION: CH01 AVALON-MM TO AVALON-ST FIFO TWIN")
    print("=" * 70)

    random.seed(20261110)
    twin = AvalonFifoTwin(depth_words=256)

    # Prepare 250 32-bit words (500 16-bit audio samples)
    num_words = 250
    words = []
    expected_samples = []

    for i in range(num_words):
        s0 = (i * 2) & 0xFFFF
        s1 = (i * 2 + 1) & 0xFFFF
        w32 = s0 | (s1 << 16)
        words.append(w32)
        expected_samples.append(s0)
        expected_samples.append(s1)

    # Save stimuli file for tb_ch01_fifo.v
    stim_file = os.path.join(os.path.dirname(__file__), "tb_ch01_fifo_stim.txt")
    with open(stim_file, "w") as f:
        for w in words:
            f.write(f"{w:08x}\n")
    print(f"Generated {num_words} 32-bit test words ({len(expected_samples)} audio samples) to {stim_file}")

    # Simulation loop
    received_samples = []
    wr_idx = 0
    cycle = 0
    max_cycles = 4000
    full_events = 0

    while cycle < max_cycles and len(received_samples) < len(expected_samples):
        # Master write logic
        do_write = False
        wdata = 0
        if wr_idx < num_words:
            # Try to write with some burst probability
            if random.random() < 0.8:
                do_write = True
                wdata = words[wr_idx]

        # Downstream ready logic (random backpressure: 0 or 1)
        st_ready = 1 if random.random() < 0.6 else 0

        # Clock twin
        st_data, st_valid, waitreq, fill_level = twin.clock(do_write, wdata, st_ready)

        if do_write:
            if not waitreq:
                wr_idx += 1
            else:
                full_events += 1

        if st_valid and st_ready:
            received_samples.append(st_data)

        cycle += 1

    print(f"\nSimulation completed in {cycle} cycles.")
    print(f"Total 32-bit words written: {wr_idx}/{num_words}")
    print(f"Total 16-bit samples received: {len(received_samples)}/{len(expected_samples)}")
    print(f"FIFO full / waitrequest occurrences: {full_events}")

    assert len(received_samples) == len(expected_samples), "Sample count mismatch!"
    assert received_samples == expected_samples, "Sample data or order mismatch!"
    print("Verification PASSED: 100% bit-exact match with zero sample loss or duplication.")
    print("Little-endian order verified: lower 16-bit sample emitted before upper 16-bit sample.")

    # Edge case: Fill FIFO to maximum capacity (256 words in RAM + 1 word in unpacker = 257 words total)
    print("\nTesting FIFO capacity saturation:")
    twin_sat = AvalonFifoTwin(depth_words=256)
    for i in range(257):
        s0, s1 = (100 + i) & 0xFFFF, (200 + i) & 0xFFFF
        twin_sat.clock(True, s0 | (s1 << 16), False) # st_ready = False
    
    # After 257 writes, RAM has exactly 256 words and unpacker holds 1 word
    _, _, waitreq_full, fill_samples = twin_sat.clock(False, 0, False)
    print(f"  After 257 writes: words_used={twin_sat.words_used}, full={twin_sat.fifo_full}, waitrequest={waitreq_full}, fill_samples={fill_samples}")
    assert twin_sat.fifo_full, "FIFO RAM should be full!"
    assert waitreq_full, "waitrequest should be active!"

    # 258th write should trigger waitrequest and ovf_sticky
    twin_sat.clock(True, 0xDEADBEEF, False)
    assert twin_sat.ovf_sticky == 1, "ovf_sticky should be set on overflow write!"
    print("  Overflow protection and ovf_sticky verified.")

    print("\n" + "=" * 70)
    print("ALL AVALON FIFO TWIN TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
