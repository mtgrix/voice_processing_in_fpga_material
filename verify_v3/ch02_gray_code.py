#!/usr/bin/env python3
"""
verify_v3/ch02_gray_code.py

Demonstrates and verifies the mathematical proof of Gray code single-bit transitions:
G(n) = n ^ (n >> 1)
Proves via the "trailing-ones argument":
For any integer n with k trailing ones:
- Binary addition n + 1 flips bits 0..k (k bits flip from 1 to 0, bit k flips from 0 to 1).
- In Gray code G(n) ^ G(n+1), all bits j < k cancel out (1 ^ 1 = 0).
- Bit k changes (1 ^ 0 = 1).
- All bits j > k are unchanged (0 ^ 0 = 0).
- Therefore, HammingDistance(G(n), G(n+1)) == 1 for every n >= 0.
"""

def count_trailing_ones(n):
    k = 0
    while (n & (1 << k)):
        k += 1
    return k

def gray_code(n):
    return n ^ (n >> 1)

def hamming_weight(v):
    return bin(v).count('1')

def verify_gray_code():
    print("=== GRAY CODE TRAILING-ONES MATHEMATICAL VERIFICATION ===")
    
    # Detailed walkthrough for n = 0..15
    print("  n  |  n (bin)  | Trailing 1s (k) | n+1 (bin) | G(n) (bin) | G(n+1) (bin) | Changed Bit | Hamming Dist")
    print("-" * 105)
    
    for n in range(16):
        k = count_trailing_ones(n)
        g_n = gray_code(n)
        g_next = gray_code(n + 1)
        diff = g_n ^ g_next
        h_dist = hamming_weight(diff)
        changed_bit = diff.bit_length() - 1 if diff > 0 else -1
        
        n_bin = f"{n:05b}"
        next_bin = f"{n+1:05b}"
        gn_bin = f"{g_n:05b}"
        gn_next_bin = f"{g_next:05b}"
        
        print(f" {n:2d}  |   {n_bin}   |        {k}        |   {next_bin}   |   {gn_bin}    |    {gn_next_bin}     |    bit {changed_bit}    |      {h_dist}")
        assert h_dist == 1, f"Hamming distance is not 1 for n={n}"
        assert changed_bit == k, f"Changed bit {changed_bit} != trailing ones {k} for n={n}"
        
    print("-" * 105)
    print("Small integer table verified: Hamming distance is ALWAYS 1, changed bit index is EXACTLY k.\n")
    
    # Extended verification up to 1024
    N_MAX = 1024
    for n in range(N_MAX):
        k = count_trailing_ones(n)
        g_n = gray_code(n)
        g_next = gray_code(n + 1)
        diff = g_n ^ g_next
        assert hamming_weight(diff) == 1, f"Failed Hamming weight 1 at n={n}"
        changed_bit = diff.bit_length() - 1
        assert changed_bit == k, f"Failed changed bit k at n={n}"
        
    print(f"Extended verification: PASSED {N_MAX} transitions (0 to {N_MAX}).")
    print("Mathematical conclusion: G(n) = n ^ (n >> 1) guarantees single-bit transitions unconditionally.")

if __name__ == "__main__":
    verify_gray_code()
