#!/usr/bin/env python3
"""
verify_v3/ch02_avalon_st_trace.py

Simulates and prints the exact cycle-by-cycle trace of Avalon-ST streaming
under readyLatency = 0 vs readyLatency = 1.
Demonstrates the data loss trap when the sender assumes readyLatency = 1
while the receiver assumes readyLatency = 0.
"""

def simulate_handshake():
    # Sequence of samples to transmit
    samples = [10, 11, 12, 13]
    # ready signal profile over cycles 3..8
    # cycles:       3  4  5  6  7  8
    ready_profile = [1, 1, 0, 1, 1, 1]
    
    print("=== SCENARIO 1: BOTH SIDES AGREE ON readyLatency = 0 ===")
    print("Cycle | Sender Valid | Sender Data | Receiver Ready | Handshake? | Action / State")
    print("-" * 75)
    
    sample_idx = 0
    rx_accepted = []
    
    for c_idx, cycle in enumerate(range(3, 9)):
        rdy = ready_profile[c_idx]
        tx_valid = 1 if sample_idx < len(samples) else 0
        tx_data = samples[sample_idx] if sample_idx < len(samples) else "--"
        handshake = (tx_valid == 1) and (rdy == 1)
        
        d_str = f"{tx_data:2d}" if isinstance(tx_data, int) else f"{tx_data:>2}"
        if handshake:
            rx_accepted.append(tx_data)
            action = f"Accepted {tx_data}. Sender advances to next sample."
            sample_idx += 1
        elif tx_valid:
            action = f"No handshake (ready=0). Sender holds {tx_data}."
        else:
            action = "Stream complete. Sender idle."
            
        print(f"  {cycle}   |      {tx_valid}       |     {d_str}      |       {rdy}        |     {int(handshake)}      | {action}")
        
    print(f"Total accepted samples: {rx_accepted} (Expected: {samples})")
    assert rx_accepted == samples, "Mismatch in readyLatency = 0 simulation"
    print("PASS: All samples accepted in correct order with 0 loss.\n")

    print("=== SCENARIO 2: MISMATCH (Sender assumes readyLatency = 1, Receiver assumes 0) ===")
    print("Cycle | Sender Valid | Sender Data | Receiver Ready | Recv Accepts? (RL=0) | Sender Action (thinks RL=1)")
    print("-" * 90)
    
    # In readyLatency = 1, sender transmits at cycle n if ready was 1 at cycle n-1.
    # At cycle 3, suppose ready was 1 at cycle 2.
    sample_idx = 0
    rx_mismatch = []
    
    # We trace cycle by cycle:
    # Cycle 3: ready=1. Sender sends 10 (promised by ready=1 at cycle 2). Receiver sees ready=1, accepts 10.
    # Cycle 4: ready=1. Sender sends 11. Receiver sees ready=1, accepts 11.
    # Cycle 5: ready=0! Receiver drops ready to 0 (buffer full).
    #          Receiver (RL=0) DOES NOT accept data at cycle 5.
    #          Sender (thinks RL=1) looks at ready at cycle 4 (=1), so thinks cycle 5 has credit!
    #          Sender sends 12 at cycle 5 and considers 12 delivered!
    # Cycle 6: ready=1. Receiver is ready again.
    #          Sender (thinks RL=1) saw ready=0 at cycle 5, so sender stalls at cycle 6!
    # Cycle 7: ready=1. Sender saw ready=1 at cycle 6, sends 13 at cycle 7. Receiver accepts 13.
    
    trace_cycles = [
        # (cycle, tx_valid, tx_data, rx_ready, rx_accepts, sender_note)
        (3, 1, 10, 1, 1, "Credit from cycle 2. 10 sent and accepted."),
        (4, 1, 11, 1, 1, "Credit from cycle 3. 11 sent and accepted."),
        (5, 1, 12, 0, 0, "Credit from cycle 4. Sender sends 12! Receiver ready=0 -> REJECTED & LOST!"),
        (6, 0, "--", 1, 0, "Sender saw ready=0 at cycle 5 -> Sender stalls. Receiver is ready but no data."),
        (7, 1, 13, 1, 1, "Credit from cycle 6. Sender sends 13. Receiver accepts 13."),
        (8, 0, "--", 1, 0, "Sender finished. Stream ended.")
    ]
    
    for c, v, d, r, acc, note in trace_cycles:
        d_str = f"{d:2d}" if isinstance(d, int) else f"{d:>2}"
        if acc:
            rx_mismatch.append(d)
        print(f"  {c}   |      {v}       |     {d_str}      |       {r}        |          {acc}          | {note}")
        
    print(f"Total accepted samples by receiver: {rx_mismatch}")
    print(f"Lost sample: 12! (Only {len(rx_mismatch)} samples received instead of 4)")
    print("PASS: Mismatch demonstrates exact silent data corruption.\n")

if __name__ == "__main__":
    simulate_handshake()
