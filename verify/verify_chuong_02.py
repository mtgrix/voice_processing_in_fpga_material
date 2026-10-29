"""Verify Chương 2 numbers: PLL ratio, SCLK/MCLK, ppm drift, Gray, I2S nibble, integer PLL ppm."""
import numpy as np

assert abs(12.288 / 50 - 0.24576) < 1e-12
assert 256 * 48000 == 12_288_000
assert 48000 * 64 == 3_072_000
assert 48000 * 32 == 1_536_000
assert abs(50e-6 * 60 * 16000 - 48.0) < 1e-9
assert abs(5e-6 * 60 * 16000 - 4.8) < 1e-9

# Integer-N near solution cited in text
fout = 50.0 * 1507 / (73 * 84)
assert abs(fout - 12.287997390737116) < 1e-12
ppm = abs(fout - 12.288) / 12.288 * 1e6
assert abs(ppm - 0.21234235709465438) < 1e-6
drift = ppm * 1e-6 * 60 * 16000
assert abs(drift - 0.2038486628108682) < 1e-9

# Fractional illustration
assert abs(50.0 * 61.44 / (5 * 50) - 12.288) < 1e-12
assert abs(50.0 * 61.44 / 5 - 614.4) < 1e-12


def bin_to_gray(n: int) -> int:
    return n ^ (n >> 1)


grays = [bin_to_gray(i) for i in range(8)]
assert [format(g, "03b") for g in grays] == [
    "000", "001", "011", "010", "110", "111", "101", "100"
]
for a, b in zip(grays, grays[1:]):
    assert bin(a ^ b).count("1") == 1
# binary 3 -> 4 flips 3 bits; gray flips 1
assert bin(0b011 ^ 0b100).count("1") == 3
assert bin(bin_to_gray(3) ^ bin_to_gray(4)).count("1") == 1

bits = [1, 0, 1, 1]
val = 0
for b in bits:
    val = (val << 1) | b
assert val == 11

print("verify_chuong_02 OK", {"fout": fout, "ppm": ppm, "drift_samples": drift})
