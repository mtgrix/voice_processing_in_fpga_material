// sw_v3/ch07_mac.c
// Implementation of direct MAC autocorrelation for audio frames
#include "ch07_mac.h"

void ch07_autocorr_mac(const int32_t xw[CH07_NSAMP_WINDOW], int64_t R[CH07_TAU_MAX + 1]) {
    // 1. R[0]: sum of 638 squared samples
    int64_t r0 = 0;
    for (int n = 0; n < CH07_NSAMP_WINDOW; ++n) {
        r0 += (int64_t)xw[n] * (int64_t)xw[n];
    }
    R[0] = r0;

    // 2. R[tau] for tau = 26..214
    for (int tau = CH07_TAU_MIN; tau <= CH07_TAU_MAX; ++tau) {
        int64_t acc = 0;
        int max_n = CH07_NSAMP_WINDOW - tau;
        for (int n = 0; n < max_n; ++n) {
            acc += (int64_t)xw[n] * (int64_t)xw[n + tau];
        }
        R[tau] = acc;
    }
}
