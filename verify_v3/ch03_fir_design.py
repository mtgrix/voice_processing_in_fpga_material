"""verify_v3/ch03_fir_design.py
FIR Nyquist-edge filter design and frequency-response evaluation using scipy.signal.firls and kaiserord.
Verifies all numbers quoted in agenda_chot_v2 §Ch.3 and Table 3.2.
"""
import numpy as np
import scipy.signal as signal

def run_design():
    fs = 16000.0
    nyq = fs / 2.0  # 8000.0 Hz
    
    print("=== CH03 FIR DESIGN & FREQUENCY RESPONSE AUDIT ===")
    print(f"Sampling frequency: fs = {fs:.1f} Hz, Nyquist = {nyq:.1f} Hz")
    
    # 1. Kaiser formula check: 60 dB attenuation in 400 Hz transition (7600 to 8000 Hz)
    delta_f = 8000.0 - 7600.0  # 400 Hz
    attenuation_db = 60.0
    # Normalized transition width (relative to Nyquist)
    width_norm = delta_f / nyq  # 400 / 8000 = 0.05
    kaiser_taps, kaiser_beta = signal.kaiserord(attenuation_db, width_norm)
    # Bellanger / Kaiser textbook approximation: (A - 7.95) / (14.36 * delta_f / fs)
    kaiser_approx = (attenuation_db - 7.95) / (14.36 * (delta_f / fs))
    
    print("\n--- Kaiser Filter Length Estimation ---")
    print(f"Target attenuation: {attenuation_db:.1f} dB, Transition bandwidth: {delta_f:.1f} Hz")
    print(f"scipy.signal.kaiserord taps: {kaiser_taps} (beta = {kaiser_beta:.5f})")
    print(f"Kaiser formula approximation: {kaiser_approx:.2f} -> ~{int(np.ceil(kaiser_approx))} taps")
    
    # 2. Design filters with firls: target 1 from 0 to 7600 Hz, ramp down to 0 at 8000 Hz
    # bands: [0, 7600, 7600, 8000], desired: [1, 1, 1, 0]
    bands = [0.0, 7600.0, 7600.0, 8000.0]
    desired = [1.0, 1.0, 1.0, 0.0]
    
    configs = [
        (31, "31 tap"),
        (63, "63 tap"),
        (127, "127 tap")
    ]
    
    test_freqs = [0.0, 1000.0, 7400.0, 7600.0, 8000.0]
    
    print("\n--- FIR Filter Options Frequency Response Table ---")
    print(f"{'Option':<10} | {'Taps':<6} | {'Group Delay':<12} | {'0 kHz (dB)':<10} | {'7.4 kHz (dB)':<12} | {'7.6 kHz (dB)':<12} | {'8.0 kHz (dB)':<12}")
    print("-" * 88)
    
    results = {}
    for n_taps, label in configs:
        h = signal.firls(n_taps, bands, desired, fs=fs)
        group_delay = (n_taps - 1) // 2
        
        # Frequency response
        w, H = signal.freqz(h, 1, worN=test_freqs, fs=fs)
        db = 20.0 * np.log10(np.maximum(np.abs(H), 1e-12))
        
        results[n_taps] = {
            'h': h,
            'group_delay': group_delay,
            'db': {f: db[i] for i, f in enumerate(test_freqs)}
        }
        
        print(f"{label:<10} | {n_taps:<6} | {group_delay:<12} | {db[0]:+9.3f} | {db[2]:+11.2f} | {db[3]:+11.2f} | {db[4]:+11.2f}")

    # Check 31-tap Q1.15 quantized coefficients
    h31 = results[31]['h']
    h31_q15 = np.round(h31 * 32768.0).astype(int)
    w_q, H_q = signal.freqz(h31_q15 / 32768.0, 1, worN=test_freqs, fs=fs)
    db_q = 20.0 * np.log10(np.maximum(np.abs(H_q), 1e-12))
    
    print("\n--- 31-Tap Quantization Comparison (Float vs Q1.15) ---")
    print(f"Float  : 7.4k={results[31]['db'][7400.0]:+.2f} dB, 7.6k={results[31]['db'][7600.0]:+.2f} dB, 8.0k={results[31]['db'][8000.0]:+.2f} dB")
    print(f"Q1.15  : 7.4k={db_q[2]:+.2f} dB, 7.6k={db_q[3]:+.2f} dB, 8.0k={db_q[4]:+.2f} dB")
    print(f"Sum of Q1.15 coefficients: {np.sum(h31_q15)} (DC gain = {np.sum(h31_q15)/32768.0:.6f})")
    print(f"Symmetric check (h == h[::-1]): {np.array_equal(h31_q15, h31_q15[::-1])}")
    print(f"Center tap h[15] = {h31_q15[15]} ({h31_q15[15]/32768.0:.6f})")
    print("Unique 16 coefficients h[0..15]:")
    for k in range(16):
        print(f"  h[{k:2d}] = {h31_q15[k]:6d} (0x{h31_q15[k] & 0xFFFF:04x}, float: {h31[k]:+.6f})")
        
    return results

if __name__ == '__main__':
    run_design()
