// sw_v3/ch08_norm.h
// Software reference implementation of window normalization C[tau]
// and subtractive octave cost scoring Sc[tau] for HPS/ARM
#ifndef CH08_NORM_H
#define CH08_NORM_H

#include <stdint.h>

#define CH08_TAU_MIN 26
#define CH08_TAU_MAX 214
#define CH08_NLAGS   189

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint8_t  sh;
    uint32_t r0n;
    int32_t  U[CH08_TAU_MAX + 1];
    int32_t  Sc[CH08_TAU_MAX + 1];
} ch08_norm_result_t;

/**
 * Computes window normalization and subtractive octave cost:
 *   sh = max(0, bitlen(R0) - 26)
 *   R0n = R0 >> sh
 *   For tau in 26..214:
 *     Rn = R[tau] >> sh
 *     U[tau] = (Rn * C[tau] + 2^13) >> 14
 *     term_k = (R0n * K[tau] + 2^19) >> 20
 *     Sc[tau] = U[tau] - term_k
 *
 * @param r0 Unnormalized frame energy R[0] (non-negative).
 * @param R  Array of unnormalized autocorrelation values (index 26..214).
 * @param res Output structure holding sh, R0n, U[tau], Sc[tau].
 */
void ch08_norm_score(int64_t r0, const int64_t R[CH08_TAU_MAX + 1], ch08_norm_result_t *res);

#ifdef __cplusplus
}
#endif

#endif // CH08_NORM_H
