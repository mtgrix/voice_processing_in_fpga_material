"""Verify Chương 4: FIR folding, convolution, polyphase, Q1.15, stopband, DSP cycle budget."""
import numpy as np

a, b, c, d = 3, 4, 5, 6
h = [1, 2, 2, 1]
# full sum then fold — §4.2 step-by-step
full = h[0] * a + h[1] * b + h[2] * c + h[3] * d
assert full == 3 + 8 + 10 + 6 == 27
folded = h[0] * (a + d) + h[1] * (b + c)
assert folded == 1 * 9 + 2 * 9 == 27
assert folded == full

h3 = [1, 2, 1]
x3 = [3, 4, 5, 0, 0]
# explicit terms
assert h3[0] * 3 + h3[1] * 0 + h3[2] * 0 == 3
assert h3[0] * 4 + h3[1] * 3 + h3[2] * 0 == 10
assert h3[0] * 5 + h3[1] * 4 + h3[2] * 3 == 16
y3 = [sum(h3[k] * (x3[n - k] if n - k >= 0 else 0) for k in range(3)) for n in range(5)]
assert y3[:3] == [3, 10, 16]

h = np.array([1.0, 2, 1]) / 4
x = np.array([4.0, 0, 4, 0, 4])
y = np.array([sum(h[k] * (x[n - k] if n - k >= 0 else 0) for k in range(3)) for n in range(5)])
assert np.allclose(y, [1, 2, 2, 2, 2])

hq = np.round(np.array([0.25, 0.5, 0.25]) * (1 << 15)).astype(int)
assert hq.tolist() == [8192, 16384, 8192]

# §4.2 Q1.15 longer vector step-by-step
assert abs(0.1 * 32768 - 3276.8) < 1e-12
assert abs(0.2 * 32768 - 6553.6) < 1e-12
assert abs(0.4 * 32768 - 13107.2) < 1e-12
hq5 = np.round(np.array([0.1, 0.2, 0.4, 0.2, 0.1]) * (1 << 15)).astype(int)
assert hq5.tolist() == [3277, 6554, 13107, 6554, 3277]
assert int(hq5.sum()) == 32769

hh = list(range(6))
E0, E1, E2 = hh[0::3], hh[1::3], hh[2::3]
assert E0 == [0, 3] and E1 == [1, 4] and E2 == [2, 5]
assert 4 / 6 == 2 / 3
assert abs(16000 / 24000 - 2 / 3) < 1e-15
assert 48000 // 2 == 24000

h6 = np.array([1.0, 2, 3, 4, 5, 6])
x6 = np.array([1.0, 2, 3, 4, 5, 6])
yfull = np.convolve(x6, h6, mode="full")
assert yfull.tolist() == [1, 4, 10, 20, 35, 56, 70, 76, 73, 60, 36]

assert abs(50e6 / 24000 - 2083.3333333333335) < 1e-9
assert abs(50e6 / 16000 - 3125.0) < 1e-12
assert 48 // 2 == 24  # folded mult for N=48

def decimate_2_over_3(y_full):
    return [yi for i, yi in enumerate(y_full) if i % 3 != 2]

assert len(decimate_2_over_3(range(6))) == 4

# §4.1b Ví dụ tính tay — stopband amplitudes and alias
assert abs(10e3 - 16e3) == 6e3
assert abs(10 ** (-60 / 20) - 0.001) < 1e-15
assert abs(10 ** (-20 / 20) - 0.1) < 1e-15
assert abs((10 ** (-60 / 20)) ** 2 - 1e-6) < 1e-18
assert abs((10 ** (-20 / 20)) ** 2 - 0.01) < 1e-15

print("verify_chuong_04 OK")
