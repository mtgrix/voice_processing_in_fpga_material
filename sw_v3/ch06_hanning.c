/* sw_v3/ch06_hanning.c
 * Implementation of Praat N+1 Hanning window for HPS
 */

#include "ch06_hanning.h"
#include <math.h>
#include <stdlib.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

void ch06_generate_hanning_double(double *w, size_t n) {
    if (!w || n == 0) return;
    double denom = (double)(n + 1);
    for (size_t i = 0; i < n; i++) {
        /* Praat Sound_to_Pitch.cpp lines 422-424:
         * window[i] = 0.5 - 0.5 * cos(2 * pi * i / (nsamp_window + 1))
         * where i is 1-based (i = 1..n). Here i+1 is 1-based.
         */
        w[i] = 0.5 - 0.5 * cos(2.0 * M_PI * ((double)(i + 1)) / denom);
    }
}

void ch06_generate_hanning_q15(uint16_t *w_q15, size_t n) {
    if (!w_q15 || n == 0) return;
    double denom = (double)(n + 1);
    for (size_t i = 0; i < n; i++) {
        double v = 0.5 - 0.5 * cos(2.0 * M_PI * ((double)(i + 1)) / denom);
        int32_t rounded = (int32_t)floor(v * 32768.0 + 0.5);
        if (rounded > 32767) {
            rounded = 32767; /* Clamping at apex */
        }
        w_q15[i] = (uint16_t)rounded;
    }
}

uint16_t ch06_apply_window_fixed(
    const int32_t *d,
    const uint16_t *w_q15,
    int32_t *xw,
    size_t n
) {
    if (!d || !w_q15 || !xw || n == 0) return 0;

    int32_t max_abs_lp = 0;

    for (size_t i = 0; i < n; i++) {
        /* d[i] is 17-bit signed, w_q15[i] is 16-bit unsigned (0..32767) */
        int64_t prod = (int64_t)d[i] * (int64_t)w_q15[i];
        int32_t rounded = (int32_t)((prod + 16384) >> 15);
        xw[i] = rounded;

        if (i >= CH06_LP_FIRST && i <= CH06_LP_LAST) {
            int32_t a = abs(rounded);
            if (a > max_abs_lp) {
                max_abs_lp = a;
            }
        }
    }

    return (uint16_t)max_abs_lp;
}
