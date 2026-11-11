/* sw_v3/ch06_hanning.h
 * C reference implementation of Praat N+1 Hanning window for HPS/ARM
 * Supports double precision, Q1.15 fixed-point generation, and 17-bit window application
 */

#ifndef CH06_HANNING_H
#define CH06_HANNING_H

#include <stdint.h>
#include <stddef.h>

#define CH06_NSAMP_WINDOW 638
#define CH06_LP_FIRST     212
#define CH06_LP_LAST      425

#ifdef __cplusplus
extern "C" {
#endif

/* Generates Praat N+1 Hanning window in double precision:
 * w[i] = 0.5 - 0.5 * cos(2 * pi * (i + 1) / (N + 1)), i = 0..N-1
 */
void ch06_generate_hanning_double(double *w, size_t n);

/* Generates Q1.15 integer window with saturation at 32767:
 * w_q15[i] = min(32767, floor(w_double[i] * 32768.0 + 0.5))
 */
void ch06_generate_hanning_q15(uint16_t *w_q15, size_t n);

/* Applies Q1.15 Hanning window to 17-bit signed difference samples d[i]:
 * xw[i] = (d[i] * w_q15[i] + 16384) >> 15
 * Returns the LocalPeak (max |xw[j]| for j in [LP_FIRST, LP_LAST]).
 */
uint16_t ch06_apply_window_fixed(
    const int32_t *d,
    const uint16_t *w_q15,
    int32_t *xw,
    size_t n
);

#ifdef __cplusplus
}
#endif

#endif /* CH06_HANNING_H */
