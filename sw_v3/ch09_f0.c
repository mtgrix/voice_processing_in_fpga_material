// sw_v3/ch09_f0.c
// Implementation of Chapter 9 F0 parabolic interpolation and single division

#include "ch09_f0.h"

static inline uint8_t calc_s2(uint32_t den) {
    if (den & (1u << 28)) return 5;
    if (den & (1u << 27)) return 4;
    if (den & (1u << 26)) return 3;
    if (den & (1u << 25)) return 2;
    if (den & (1u << 24)) return 1;
    return 0;
}

void ch09_calc_f0(const int32_t U[CH09_TAU_SCAN_MAX + 1],
                  const int32_t Sc[CH09_TAU_SCAN_MAX + 1],
                  uint32_t r0n,
                  ch09_f0_result_t *res)
{
    if (!res) return;

    res->found    = false;
    res->best_tau = 0;
    res->best_um  = 0;
    res->best_u0  = 0;
    res->best_up  = 0;
    res->best_sc  = -2147483647; // -2^31 + 1
    res->num      = 0;
    res->den      = 0;
    res->s2       = 0;
    res->N        = 0;
    res->D        = 0;
    res->f0_raw   = 0;

    // 1. Scan for candidates over tau in [27, 213]
    for (int t = CH09_TAU_SEARCH_MIN; t <= CH09_TAU_SEARCH_MAX; ++t) {
        int32_t um = U[t - 1];
        int32_t u0 = U[t];
        int32_t up = U[t + 1];

        // Peak condition: u0 > um && u0 >= up && 40*u0 > 9*r0n
        int64_t term_40u = ((int64_t)u0 << 5) + ((int64_t)u0 << 3);
        int64_t term_9r0n = ((int64_t)r0n << 3) + (int64_t)r0n;

        if (u0 > um && u0 >= up && term_40u > term_9r0n) {
            // Check argmax Sc (strictly greater; earlier candidate wins ties)
            if (!res->found || Sc[t] > res->best_sc) {
                res->found    = true;
                res->best_tau = (uint8_t)t;
                res->best_um  = um;
                res->best_u0  = u0;
                res->best_up  = up;
                res->best_sc  = Sc[t];
            }
        }
    }

    if (!res->found) {
        return;
    }

    // 2. Parabolic interpolation parameters
    int32_t num = res->best_up - res->best_um;
    int32_t den = 2 * res->best_u0 - res->best_um - res->best_up;
    res->num = num;
    res->den = den;

    if (den <= 0) {
        // Degenerate peak
        res->found = false;
        return;
    }

    // 3. Dynamic s2 normalization
    uint8_t s2 = calc_s2((uint32_t)den);
    res->s2 = s2;

    int32_t numn = num >> s2;
    uint32_t denn = (uint32_t)den >> s2;

    // D = 2 * denn * best_tau + numn (guaranteed > 0 for valid candidates)
    int64_t D_val = 2 * (int64_t)denn * (int64_t)res->best_tau + (int64_t)numn;
    res->D = (uint64_t)D_val;

    // 512000 * denn
    uint64_t prod_512k = 512000ULL * (uint64_t)denn;
    uint64_t N_val = prod_512k + ((uint64_t)D_val >> 1);
    res->N = N_val;

    // 4. Single division with rounding
    uint64_t quotient = N_val / (uint64_t)D_val;
    res->f0_raw = (quotient > 65535ULL) ? 65535 : (uint16_t)quotient;
}
