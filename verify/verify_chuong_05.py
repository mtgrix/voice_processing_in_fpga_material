"""Verify Chương 5: M10K budget, circular L=8, hop, latency, L@100Hz, warm-up, RTF."""
L, W = 640, 16
bits = L * W
assert bits == 10240
assert bits <= 10240

mem = [0] * 8
wr = 0
for x in range(1, 10):
    mem[wr] = x
    wr = (wr + 1) % 8
assert mem == [9, 2, 3, 4, 5, 6, 7, 8]
assert wr == 1
frame = [mem[(wr + k) % 8] for k in range(8)]
assert frame == [2, 3, 4, 5, 6, 7, 8, 9]

# hop H=2 on L=8 after full 1..8 then write 9,10
mem = list(range(1, 9))
wr = 0
for x in (9, 10):
    mem[wr] = x
    wr = (wr + 1) % 8
assert mem == [9, 10, 3, 4, 5, 6, 7, 8]
assert wr == 2
assert [mem[(wr + k) % 8] for k in range(8)] == [3, 4, 5, 6, 7, 8, 9, 10]

assert int(0.01 * 50e6) == 500_000
assert 640 + 2 == 642
assert abs(3 * 16000 / 75 - 640) < 1e-12
assert abs(3 * 16000 / 100 - 480) < 1e-12
assert 480 * 16 == 7680
assert 16000 / 160 == 100  # frames/s
assert 100 * 640 == 64000  # reads/s
assert abs(642 / 50e6 - 12.84e-6) < 1e-9
assert abs(642 / 500_000 - 0.001284) < 1e-9

# Old Data semantic — Ví dụ tính tay
cell = 7
new = 42
old = cell
cell = new
assert old == 7 and cell == 42

# RTF memory portion (asserted in §5.1 / costbox)
rtf_mem = 642 / 500_000
assert abs(rtf_mem - 0.001284) < 1e-12

print("verify_chuong_05 OK", {"bits": bits, "frame": frame, "rtf_mem": rtf_mem})
