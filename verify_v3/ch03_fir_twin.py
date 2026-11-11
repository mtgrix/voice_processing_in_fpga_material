"""verify_v3/ch03_fir_twin.py
Bit-exact and cycle-accurate Python twin for rtl/v3/ch03_fir_filter.v.
Simulates:
- 31-tap folded symmetric FIR filter (16 cycles per sample) with pre-adder
- Dynamic bypass mode (1-cycle registered pipeline)
- Avalon-ST ready/valid handshaking with backpressure (readyLatency = 0)
- Generates tb_ch03_fir_stim.txt and tb_ch03_fir_expected.txt for iverilog TB.
"""
import os
import wave
import numpy as np

# 16 unique symmetrical coefficients (Q1.15)
COEFF_16 = [
    504, -538, 571, -604, 635, -664, 692, -717,
    740, -760, 778, -793, 804, -812, 818, 31949
]

class FirFilterTwin:
    def __init__(self):
        self.shift_reg = [0] * 31
        self.state = 0      # 0: S_IDLE, 1: S_CALC, 2: S_WAIT_OUT
        self.step = 0
        self.acc = 0
        self.out_data = 0
        self.out_valid = 0

    def step_cycle(self, rst_n, bypass, sink_valid, sink_data, source_ready):
        """Simulates one clock cycle matching posedge clk of ch03_fir_filter.v."""
        if not rst_n:
            self.shift_reg = [0] * 31
            self.state = 0
            self.step = 0
            self.acc = 0
            self.out_data = 0
            self.out_valid = 0
            sink_ready = 1
            return sink_ready, self.out_valid, self.out_data, self.state, self.step

        # Combinational ready generation
        if bypass:
            sink_ready = 1 if (not self.out_valid or source_ready) else 0
        else:
            if self.state == 0:
                sink_ready = 1 if (not self.out_valid or source_ready) else 0
            else:
                sink_ready = 0

        # Handshakes
        s_handshake = sink_valid and sink_ready
        m_handshake = self.out_valid and source_ready

        # State updates on clock edge
        if bypass:
            self.state = 0
            self.step = 0
            if m_handshake:
                if s_handshake:
                    self.out_data = sink_data
                    self.out_valid = 1
                else:
                    self.out_valid = 0
            else:
                if s_handshake:
                    self.out_data = sink_data
                    self.out_valid = 1
        else:
            if self.state == 0:  # S_IDLE
                if m_handshake:
                    self.out_valid = 0
                if s_handshake:
                    self.shift_reg = [sink_data] + self.shift_reg[:-1]
                    self.state = 1
                    self.step = 0
                    self.acc = 0
            elif self.state == 1:  # S_CALC
                if m_handshake:
                    self.out_valid = 0

                xa = self.shift_reg[self.step]
                xb = 0 if self.step == 15 else self.shift_reg[30 - self.step]
                pre_add = xa + xb
                prod = pre_add * COEFF_16[self.step]
                acc_final = prod if self.step == 0 else (self.acc + prod)
                self.acc = acc_final

                if self.step == 15:
                    rounded = (acc_final + 16384) >> 15
                    sat = max(-32768, min(32767, rounded))
                    self.out_data = sat
                    self.out_valid = 1
                    if source_ready:
                        self.state = 0
                    else:
                        self.state = 2
                else:
                    self.step += 1
            elif self.state == 2:  # S_WAIT_OUT
                if source_ready:
                    self.out_valid = 0
                    self.state = 0

        return sink_ready, self.out_valid, self.out_data, self.state, self.step


def generate_verification_vectors():
    np.random.seed(20261111)

    print("=== GENERATING CH03 FIR VERIFICATION VECTORS ===")

    # 1. Create sample sequences:
    # A: Impulse response (1 sample of 32767, then 40 zeros)
    seq_impulse = [32767] + [0] * 40

    # B: 7.8 kHz sine wave (50 samples)
    fs = 16000.0
    t_sine78 = np.arange(50) / fs
    seq_sine78 = (28000.0 * np.sin(2.0 * np.pi * 7800.0 * t_sine78)).astype(int).tolist()

    # C: 1.0 kHz sine wave (50 samples)
    t_sine10 = np.arange(50) / fs
    seq_sine10 = (28000.0 * np.sin(2.0 * np.pi * 1000.0 * t_sine10)).astype(int).tolist()

    # D: Real WAV audio snippet (100 samples from synthetic WAV)
    wav_path = os.path.join(os.path.dirname(__file__), "..", "golden_v2", "synth_glide_vuv_16k.wav")
    if os.path.exists(wav_path):
        with wave.open(wav_path, 'rb') as wf:
            frames = wf.readframes(100)
            seq_wav = np.frombuffer(frames, dtype=np.int16).tolist()
    else:
        # Fallback if run standalone
        seq_wav = (15000.0 * np.sin(2.0 * np.pi * 200.0 * np.arange(100) / fs)).astype(int).tolist()

    # E: Stress edge cases: saturation overshoot (+32767 alternating with -32768)
    seq_stress = [32767, -32768, 32767, -32768] * 10

    # Combine all sample blocks:
    all_samples = seq_impulse + seq_sine78 + seq_sine10 + seq_wav + seq_stress
    print(f"Total audio test samples assembled: {len(all_samples)}")

    # We want to test both bypass = 0 (FIR active) and bypass = 1 (pass-through)
    # with random backpressure and bubbles
    stim_lines = []
    exp_lines = []

    twin = FirFilterTwin()

    # Initial reset cycles
    for c in range(5):
        s_rdy, m_vld, m_dat, st, sp = twin.step_cycle(0, 0, 0, 0, 1)
        stim_lines.append(f"0 0 0 0000 1\n")
        exp_lines.append(f"{c:5d} 0 0 0 0000 1 {s_rdy} {m_vld} {m_dat & 0xFFFF:04x} {st} {sp}\n")

    cycle_count = 5
    sample_ptr = 0
    bypass_mode = 0

    # Run through the samples with varying backpressure
    # First half: bypass = 0 (31-tap FIR active)
    # Second half: bypass = 1 (pass-through)
    total_samples = len(all_samples)
    
    while sample_ptr < total_samples or cycle_count < 1500:
        # Switch to bypass mode after 160 samples processed
        if sample_ptr >= 160:
            bypass_mode = 1

        # Current sample to offer
        has_sample = (sample_ptr < total_samples)
        sample_val = all_samples[sample_ptr] if has_sample else 0

        # Randomize input valid (bubbles) and output ready (backpressure)
        # Give periodic bursty patterns
        rand_v = np.random.rand()
        rand_r = np.random.rand()

        # In impulse/early section, keep handshake clean for traceable cycles
        if cycle_count < 80:
            s_valid = 1 if has_sample else 0
            m_ready = 1
        elif cycle_count < 500:
            # Moderate stall: m_ready 80% high, s_valid 85% high
            s_valid = 1 if (has_sample and rand_v > 0.15) else 0
            m_ready = 1 if (rand_r > 0.20) else 0
        else:
            # Heavy stress: m_ready 50% high, s_valid 50% high
            s_valid = 1 if (has_sample and rand_v > 0.50) else 0
            m_ready = 1 if (rand_r > 0.50) else 0

        rst_n = 1
        # Capture pre-edge state and run cycle
        s_rdy, m_vld, m_dat, st, sp = twin.step_cycle(rst_n, bypass_mode, s_valid, sample_val, m_ready)

        s_dat_hex = f"{sample_val & 0xFFFF:04x}"
        m_dat_hex = f"{m_dat & 0xFFFF:04x}"

        stim_lines.append(f"{rst_n} {bypass_mode} {s_valid} {s_dat_hex} {m_ready}\n")
        exp_lines.append(f"{cycle_count:5d} {rst_n} {bypass_mode} {s_valid} {s_dat_hex} {m_ready} {s_rdy} {m_vld} {m_dat_hex} {st} {sp}\n")

        # If sample accepted, advance pointer
        if s_valid and s_rdy:
            sample_ptr += 1

        cycle_count += 1
        if sample_ptr >= total_samples and twin.state == 0 and not twin.out_valid:
            # Done flushing
            break

    # Add trailing flush cycles
    for _ in range(10):
        s_rdy, m_vld, m_dat, st, sp = twin.step_cycle(1, bypass_mode, 0, 0, 1)
        stim_lines.append(f"1 {bypass_mode} 0 0000 1\n")
        exp_lines.append(f"{cycle_count:5d} 1 {bypass_mode} 0 0000 1 {s_rdy} {m_vld} {m_dat & 0xFFFF:04x} {st} {sp}\n")
        cycle_count += 1

    # Write files
    stim_path = os.path.join(os.path.dirname(__file__), "tb_ch03_fir_stim.txt")
    exp_path = os.path.join(os.path.dirname(__file__), "tb_ch03_fir_expected.txt")

    with open(stim_path, "w", encoding="utf-8") as f:
        f.writelines(stim_lines)

    with open(exp_path, "w", encoding="utf-8") as f:
        f.writelines(exp_lines)

    print(f"Generated {cycle_count} cycles of verification stimulus.")
    print(f"Successfully processed {sample_ptr} samples across both FIR and bypass modes.")
    print(f"Stimulus written to: {stim_path}")
    print(f"Expected trace written to: {exp_path}")


if __name__ == '__main__':
    generate_verification_vectors()
