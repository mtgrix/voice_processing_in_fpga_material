// sw_v3/ch09_f0.h
// Software reference implementation of local peak finding, parabolic interpolation,
// and single-division F0 estimation (Q12.4) for HPS / ARM
#ifndef CH09_F0_H
#define CH09_F0_H

#include <stdint.h>
#include <stdbool.h>

#define CH09_TAU_SCAN_MIN   26
#define CH09_TAU_SCAN_MAX   214
#define CH09_TAU_SEARCH_MIN 27
#define CH09_TAU_SEARCH_MAX 213

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    bool     found;        // true if at least one candidate peak met criteria
    uint8_t  best_tau;     // tau_p of argmax Sc candidate in 27..213
    int32_t  best_um;      // U[tau_p - 1]
    int32_t  best_u0;      // U[tau_p]
    int32_t  best_up;      // U[tau_p + 1]
    int32_t  best_sc;      // Sc[tau_p]
    int32_t  num;          // up - um
    int32_t  den;          // 2*u0 - um - up
    uint8_t  s2;           // max(0, bitlen(den) - 24)
    uint64_t N;            // 512000*denn + D/2 (44-bit unsigned)
    uint64_t D;            // 2*denn*tau_p + numn (34-bit unsigned)
    uint16_t f0_raw;       // Raw F0 in Q12.4 format (0 if !found)
} ch09_f0_result_t;

/**
 * Searches for local peaks over tau in 27..213, selects argmax Sc,
 * computes parabolic interpolation with s2 normalization, and calculates F0_Q12.4
 * via a single division:
 *   num = U[tau+1] - U[tau-1]
 *   den = 2*U[tau] - U[tau-1] - U[tau+1]
 *   s2 = max(0, bitlen(den) - 24)
 *   D = 2 * (den >> s2) * tau + (num >> s2)
 *   F0_Q12.4 = (512000 * (den >> s2) + D/2) / D
 *
 * @param U    Array of normalized autocorrelation values U[26..214].
 * @param Sc   Array of cost-adjusted scores Sc[26..214].
 * @param r0n  Normalized frame energy R0n (for voicing threshold check 40*U > 9*R0n).
 * @param res  Pointer to output result structure.
 */
void ch09_calc_f0(const int32_t U[CH09_TAU_SCAN_MAX + 1],
                  const int32_t Sc[CH09_TAU_SCAN_MAX + 1],
                  uint32_t r0n,
                  ch09_f0_result_t *res);

#ifdef __cplusplus
}
#endif

#endif // CH09_F0_H
