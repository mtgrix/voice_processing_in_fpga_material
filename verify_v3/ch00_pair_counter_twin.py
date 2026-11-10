#!/usr/bin/env python3
"""verify_v3/ch00_pair_counter_twin.py
Bit-exact and cycle-exact Python twin for rtl/v3/ch00_pair_counter.v.
Generates the sequence of (addr_a, addr_b, tau, sload, last) pairs and control flags.
"""

class PairCounterTwin:
    def __init__(self, N, tau_min, tau_max):
        self.N = N
        self.tau_min = tau_min
        self.tau_max = tau_max
        
    def expected_total_pairs(self):
        """Analytical sum: N for R[0] + sum_{tau=tau_min}^{tau_max} (N - tau)."""
        num_lags = self.tau_max - self.tau_min + 1
        sum_tau = num_lags * (self.tau_min + self.tau_max) // 2
        sum_N = num_lags * self.N
        mac_lags = sum_N - sum_tau
        return self.N + mac_lags

    def generate_pairs(self):
        """Generate cycle-by-cycle stream of pairs matching RTL behavior while valid=1."""
        pairs = []
        # Lag 0: R[0]
        for n in range(self.N):
            sload = 1 if n == 0 else 0
            last = 1 if n == self.N - 1 else 0
            pairs.append({
                'addr_a': n,
                'addr_b': n,
                'tau': 0,
                'sload': sload,
                'last': last
            })
            
        # Lags tau_min .. tau_max
        for tau in range(self.tau_min, self.tau_max + 1):
            max_n = self.N - 1 - tau
            for n in range(max_n + 1):
                sload = 1 if n == 0 else 0
                last = 1 if n == max_n else 0
                pairs.append({
                    'addr_a': n,
                    'addr_b': n + tau,
                    'tau': tau,
                    'sload': sload,
                    'last': last
                })
        return pairs

    def compute_checksum(self):
        """Compute a 32-bit cumulative checksum over the entire stream of pairs."""
        pairs = self.generate_pairs()
        csum = 0
        mask32 = 0xFFFFFFFF
        for p in pairs:
            # Hash entry: addr_a (10b) | addr_b (10b) | tau (10b) | sload (1b) | last (1b)
            val = (p['addr_a'] & 0x3FF) | \
                  ((p['addr_b'] & 0x3FF) << 10) | \
                  ((p['tau'] & 0x3FF) << 20) | \
                  (p['sload'] << 30) | \
                  (p['last'] << 31)
            csum = (csum * 31 + val) & mask32
        return len(pairs), csum

if __name__ == '__main__':
    twin = PairCounterTwin(638, 26, 214)
    total = twin.expected_total_pairs()
    print(f"Canonical config (N=638, tau_min=26, tau_max=214):")
    print(f"  Expected total pairs: {total}")
    assert total == 98540
    print("  Twin check: OK")
