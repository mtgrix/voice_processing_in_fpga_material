"""Verify Chương 4: FIR folding, convolution, polyphase split, rate 2/3, Q1.15 quant."""
import numpy as np

a, b, c, d = 3, 4, 5, 6
h = [1, 2, 2, 1]
assert h[0] * (a + d) + h[1] * (b + c) == sum(hi * xi for hi, xi in zip(h, [a, b, c, d]))
assert h[0] * (a + d) + h[1] * (b + c) == 27

h3 = [1, 2, 1]
x3 = [3, 4, 5, 0, 0]
y3 = [sum(h3[k] * (x3[n - k] if n - k >= 0 else 0) for k in range(3)) for n in range(5)]
assert y3[:3] == [3, 10, 16]

h = np.array([1.0, 2, 1]) / 4
x = np.array([4.0, 0, 4, 0, 4])
y = np.array([sum(h[k] * (x[n - k] if n - k >= 0 else 0) for k in range(3)) for n in range(5)])
assert np.allclose(y, [1, 2, 2, 2, 2])

hq = np.round(np.array([0.25, 0.5, 0.25]) * (1 << 15)).astype(int)
assert hq.tolist() == [8192, 16384, 8192]

hh = list(range(6))
E0, E1, E2 = hh[0::3], hh[1::3], hh[2::3]
assert E0 == [0, 3] and E1 == [1, 4] and E2 == [2, 5]
assert 4 / 6 == 2 / 3
assert abs(16000 / 24000 - 2 / 3) < 1e-15
assert 48000 // 2 == 24000
print("verify_chuong_04 OK")
