"""Verify Chương 5: M10K bit budget, circular L=8, hop cycles, latency."""
L, W = 640, 16
bits = L * W
assert bits == 10240
assert bits <= 10240  # fits 1 M10K exactly

mem = [0] * 8
wr = 0
for x in range(1, 10):
    mem[wr] = x
    wr = (wr + 1) % 8
assert mem == [9, 2, 3, 4, 5, 6, 7, 8]
assert wr == 1
frame = [mem[(wr + k) % 8] for k in range(8)]
assert frame == [2, 3, 4, 5, 6, 7, 8, 9]

assert int(0.01 * 50e6) == 500_000
assert 640 + 2 == 642
assert abs(3 * 16000 / 75 - 640) < 1e-12
print("verify_chuong_05 OK", {"bits": bits, "frame": frame})
