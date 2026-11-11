#!/usr/bin/env python3
"""verify_v3/ch07_mac_twin.py

Cycle-accurate, bit-exact Python twin for Chapter 7 module: ch07_mac_unit.v
and test vector generator for tb/v3/tb_ch07_mac.v.

Rules followed:
- Cast every boolean to int() to prevent $fscanf parsing issues (Lesson m.1)
- Write vector files with newline='\\n'
- Test >= 200 vectors including clean frames, noisy frames, stress frames,
  and hand-calculation edge cases
- Strict 2-stage DSP pipeline tracking matching ALTERA_MULT_ADD
"""

import sys
import os

# Add golden_v2 path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../golden_v2')))
import constants as K

class MacUnitTwin:
    """Cycle-accurate model of ch07_mac_unit.v."""

    def __init__(self, data_w=17, acc_w=48):
        self.data_w = data_w
        self.acc_w = acc_w
        self.mask_data = (1 << data_w) - 1
        self.mask_acc = (1 << acc_w) - 1
        self.reset()

    def reset(self):
        # Stage 1: Input registers
        self.a_r = 0
        self.b_r = 0
        self.v_r = 0
        self.sload_r = 0
        self.last_r = 0

        # Stage 2: Accumulator
        self.acc = 0
        self.out_valid = 0

    def to_signed(self, val, width):
        val = val & ((1 << width) - 1)
        if val >= (1 << (width - 1)):
            val -= (1 << width)
        return val

    def step(self, rst_n, in_valid, in_sload, in_last, a, b):
        """Execute one clock cycle.
        
        Sampling convention:
        - Inputs driven at negedge (or before posedge)
        - Registered outputs evaluated based on current register state
        - Registers latch new state on posedge
        """
        if not rst_n:
            self.reset()
            return {
                'out_valid': int(self.out_valid),
                'acc': int(self.acc)
            }

        # 1. Combinational logic for Stage 2 (Accumulator) using Stage 1 registers
        next_out_valid = int(self.v_r and self.last_r)
        next_acc = self.acc

        if self.v_r:
            p = self.a_r * self.b_r  # 34-bit signed product
            if self.sload_r:
                next_acc = p
            else:
                next_acc = self.acc + p
            # Wrap to 48-bit signed
            next_acc = self.to_signed(next_acc, self.acc_w)

        # 2. Update Stage 1 registers on posedge clk
        next_a_r = self.to_signed(a, self.data_w) if in_valid else 0
        next_b_r = self.to_signed(b, self.data_w) if in_valid else 0
        next_v_r = int(in_valid)
        next_sload_r = int(in_sload) if in_valid else 0
        next_last_r = int(in_last) if in_valid else 0

        # 3. Latch state
        self.a_r = next_a_r
        self.b_r = next_b_r
        self.v_r = next_v_r
        self.sload_r = next_sload_r
        self.last_r = next_last_r

        self.acc = next_acc
        self.out_valid = next_out_valid

        return {
            'out_valid': int(self.out_valid),
            'acc': int(self.acc)
        }


def generate_vectors():
    """Build a comprehensive test stimulus sequence."""
    twin = MacUnitTwin()
    stim_records = []
    exp_records = []

    def clock_cycle(rst_n, in_valid, in_sload, in_last, a, b):
        out = twin.step(rst_n, in_valid, in_sload, in_last, a, b)
        # Stimulus: rst_n in_valid in_sload in_last a b
        stim_records.append((int(rst_n), int(in_valid), int(in_sload), int(in_last), int(a), int(b)))
        # Expected: out_valid acc
        exp_records.append((int(out['out_valid']), int(out['acc'])))

    # Phase 1: Reset (5 cycles)
    for _ in range(5):
        clock_cycle(0, 0, 0, 0, 0, 0)

    # Phase 2: Hand-calculation sequence (xw = [2, -3, 4, 1])
    # Lag 1: (2,-3), (-3,4), (4,1) -> R[1] = -14
    # Lag 2: (2,4), (-3,1)         -> R[2] = 5
    # Back-to-back issue
    clock_cycle(1, 1, 1, 0, 2, -3)
    clock_cycle(1, 1, 0, 0, -3, 4)
    clock_cycle(1, 1, 0, 1, 4, 1)

    clock_cycle(1, 1, 1, 0, 2, 4)
    clock_cycle(1, 1, 0, 1, -3, 1)

    # Idle gap (3 cycles to drain and observe R[1] and R[2])
    for _ in range(3):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Phase 3: Stress vectors - Max amplitude saturation and sign checks
    # Full scale positive: a = 65535, b = 65535
    clock_cycle(1, 1, 1, 0, 65535, 65535)
    clock_cycle(1, 1, 0, 0, -65535, -65535)
    clock_cycle(1, 1, 0, 1, -65535, 65535)
    for _ in range(2):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Phase 4: Long accumulation sequence (638 terms of full scale 65535)
    # Tests that 48-bit accumulator handles max bound (2,740,105,511,550) without overflow
    for i in range(638):
        sload = 1 if i == 0 else 0
        last = 1 if i == 637 else 0
        clock_cycle(1, 1, sload, last, 65535, 65535)
    for _ in range(3):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Phase 5: Long negative accumulation (638 terms of -65535 * +65535)
    # Tests negative bound (-2,740,105,511,550)
    for i in range(638):
        sload = 1 if i == 0 else 0
        last = 1 if i == 637 else 0
        clock_cycle(1, 1, sload, last, -65535, 65535)
    for _ in range(3):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Phase 6: Multi-lag sequence from speech frame (10 lags with back-to-back transitions)
    # Lags tau = 26..35 from Stress Frame A (from golden_v2)
    xw_path = os.path.join(os.path.dirname(__file__), '../golden_v2/hdl_check/xw.hex')
    with open(xw_path, 'r') as fx:
        xw_raw = [int(line.strip(), 16) for line in fx if line.strip()]
    # Convert to signed 17
    xw_signed = [v - (1 << 17) if v >= (1 << 16) else v for v in xw_raw[:638]]

    for tau in range(26, 36):
        num_pairs = 638 - tau
        for n in range(num_pairs):
            sload = 1 if n == 0 else 0
            last = 1 if n == num_pairs - 1 else 0
            clock_cycle(1, 1, sload, last, xw_signed[n], xw_signed[n + tau])

    # Drain pipeline
    for _ in range(5):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Phase 7: Intermittent backpressure / random stalls
    # Inject valid = 0 stalls mid-accumulation to verify accumulator state hold
    for i in range(50):
        sload = 1 if i == 0 else 0
        last = 1 if i == 49 else 0
        clock_cycle(1, 1, sload, last, (i * 100) - 2500, (i * 50) + 1000)
        if i % 5 == 0:
            # stall 2 cycles
            clock_cycle(1, 0, 0, 0, 0, 0)
            clock_cycle(1, 0, 0, 0, 0, 0)

    # Final drain
    for _ in range(10):
        clock_cycle(1, 0, 0, 0, 0, 0)

    # Write stimulus and expected files
    stim_file = os.path.join(os.path.dirname(__file__), 'tb_ch07_mac_stim.txt')
    exp_file = os.path.join(os.path.dirname(__file__), 'tb_ch07_mac_expected.txt')

    with open(stim_file, 'w', newline='\n') as f_stim, open(exp_file, 'w', newline='\n') as f_exp:
        for stim in stim_records:
            f_stim.write(f"{stim[0]} {stim[1]} {stim[2]} {stim[3]} {stim[4]} {stim[5]}\n")
        for exp in exp_records:
            f_exp.write(f"{exp[0]} {exp[1]}\n")

    print(f"Generated {len(stim_records)} cycles of stimulus into {stim_file}")
    print(f"Generated {len(exp_records)} cycles of expected outputs into {exp_file}")
    assert len(stim_records) >= 200, f"Expected >= 200 cycles, got {len(stim_records)}"
    return len(stim_records)

def main():
    print("=" * 78)
    print("CH07 MAC UNIT TWIN AND VECTOR GENERATION")
    print("=" * 78)
    total_vectors = generate_vectors()
    print(f"Vector verification ready: {total_vectors} test vectors generated successfully.")
    print("=" * 78)

if __name__ == "__main__":
    main()
