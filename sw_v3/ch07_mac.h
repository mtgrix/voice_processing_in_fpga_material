// sw_v3/ch07_mac.h
// Software reference implementation of direct MAC autocorrelation for HPS/ARM
#ifndef CH07_MAC_H
#define CH07_MAC_H

#include <stdint.h>

#define CH07_NSAMP_WINDOW 638
#define CH07_TAU_MIN      26
#define CH07_TAU_MAX      214
#define CH07_NLAGS        190

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Computes unnormalized autocorrelation using direct MAC:
 *   R[0]   = sum_{n=0}^{637} xw[n]^2
 *   R[tau] = sum_{n=0}^{637-tau} xw[n] * xw[n+tau], for tau in 26..214
 *
 * @param xw Array of 638 windowed samples (17-bit signed).
 * @param R  Output array of 215 elements (R[0] at index 0, and R[tau] at index tau).
 */
void ch07_autocorr_mac(const int32_t xw[CH07_NSAMP_WINDOW], int64_t R[CH07_TAU_MAX + 1]);

#ifdef __cplusplus
}
#endif

#endif // CH07_MAC_H
