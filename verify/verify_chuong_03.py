"""Verify Chương 3: DC-blocker float tables + bit-exact Q1.15 twin."""
import numpy as np

def dc_float(x, alpha):
    y = np.zeros(len(x), dtype=float)
    yp = 0.0
    xp = 0.0
    for i, xi in enumerate(x):
        y[i] = (xi - xp) + alpha * yp
        yp = y[i]
        xp = xi
    return y

ydc = dc_float(np.ones(5), 0.5)
assert np.allclose(ydc, [1, 0.5, 0.25, 0.125, 0.0625])

x0 = np.array([1.0, -1, 1, -1])
A = 2.0
assert np.sum((x0 + A) ** 2) == 20.0
assert np.sum(x0 ** 2) == 4.0

alpha = 1 - 2 ** (-8)
assert abs(alpha - 0.99609375) < 1e-15
assert abs(1 / (1 - alpha) - 256.0) < 1e-12
fc16 = (1 - alpha) / (2 * np.pi) * 16000
fc48 = (1 - alpha) / (2 * np.pi) * 48000
assert abs(fc16 - 9.94718394324346) < 1e-9
assert abs(fc48 - 29.841551829730378) < 1e-9


def sat16(v):
    return int(np.clip(v, -32768, 32767))


def dc_q15(x, alpha_shift=8):
    y_acc = np.int32(0)
    x_z1 = np.int32(0)
    out = np.empty(len(x), dtype=np.int16)
    for i, xi in enumerate(np.asarray(x, dtype=np.int32)):
        dx = np.int32((xi << 15) - (x_z1 << 15))
        y_acc = np.int32(y_acc + dx - (y_acc >> alpha_shift))
        x_z1 = xi
        out[i] = sat16(int(y_acc >> 15))
    return out

x = np.array([0, 0, 0] + [16384] * 29, dtype=np.int16)
y = dc_q15(x)
assert int(y[3]) == 16384
assert int(y[4]) == 16320
assert int(y[5]) == 16256
assert int(y_acc_check := int(np.int32(536870912 + 0 - (536870912 >> 8)))) == 534773760
assert 534773760 >> 15 == 16320

x_long = np.array([0, 0, 0] + [16384] * 1600, dtype=np.int16)
y_long = dc_q15(x_long)
assert abs(int(y_long[-1])) < 50
assert abs(int(y_long[3 + 256]) - int(round(16384 / np.e))) < 80
print("verify_chuong_03 OK", "y[3:6]=", y[3:6].tolist(), "fc16=", fc16)
