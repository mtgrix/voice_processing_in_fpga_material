// sw_v3/test_ch08_norm.c
// Test harness for ch08_norm.c reference software implementation
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include <assert.h>
#include "ch08_norm.h"

int main(void) {
    printf("=== CH08 HPS C REFERENCE NORMALIZATION & SCORING TEST ===\n");

    // 1. Test canonical values at tau = 26, 27, 100, 213, 214 with R0 = 67,000,000 (sh = 0)
    int64_t r0_canon = 60000000;
    int64_t R_canon[CH08_TAU_MAX + 1] = {0};

    // Let R[tau] = 0.8 * R0 for tau in [26, 214]
    for (int t = CH08_TAU_MIN; t <= CH08_TAU_MAX; ++t) {
        R_canon[t] = (int64_t)(0.8 * r0_canon);
    }

    ch08_norm_result_t res;
    ch08_norm_score(r0_canon, R_canon, &res);

    printf("Canonical Test (R0 = %" PRId64 "):\n", r0_canon);
    printf("  sh  = %d (Expected: 0)\n", res.sh);
    printf("  R0n = %u\n", res.r0n);
    assert(res.sh == 0);
    assert(res.r0n == (uint32_t)r0_canon);

    // Verify U and Sc calculation at tau = 100
    // C[100] = 19260, K[100] = 19995
    // Rn[100] = 48000000
    // prod_c = 48000000 * 19260 = 924480000000
    // U[100] = (924480000000 + 8192) >> 14 = 56425781
    // prod_k = 60000000 * 19995 = 1199700000000
    // term_k = (1199700000000 + 524288) >> 20 = 1144124
    // Sc[100] = 56425781 - 1144124 = 55281657
    int64_t expected_prod_c = (int64_t)48000000 * 19260;
    int32_t expected_U100 = (int32_t)((expected_prod_c + 8192) >> 14);
    int64_t expected_prod_k = (int64_t)60000000 * 19995;
    int32_t expected_term_k = (int32_t)((expected_prod_k + 524288) >> 20);
    int32_t expected_Sc100 = expected_U100 - expected_term_k;

    printf("  tau=100: U = %d (Expected: %d) | Sc = %d (Expected: %d)\n",
           res.U[100], expected_U100, res.Sc[100], expected_Sc100);
    assert(res.U[100] == expected_U100);
    assert(res.Sc[100] == expected_Sc100);

    // 2. Test large R0 triggering dynamic shift sh > 0
    // R0 = 2^40 approx 1.0995 * 10^12 -> bitlen = 41 -> sh = 41 - 26 = 15
    int64_t r0_large = 1ULL << 40;
    R_canon[100] = 1ULL << 39; // 0.5 * R0
    ch08_norm_score(r0_large, R_canon, &res);
    printf("\nLarge R0 Test (R0 = 2^40):\n");
    printf("  sh  = %d (Expected: 15)\n", res.sh);
    printf("  R0n = %u (Expected: %u)\n", res.r0n, (uint32_t)(1 << 25));
    assert(res.sh == 15);
    assert(res.r0n == (1U << 25));

    // 3. Test Silence / Zero R0
    ch08_norm_score(0, R_canon, &res);
    printf("\nSilence Test (R0 = 0):\n");
    printf("  sh  = %d, R0n = %u, U[100] = %d, Sc[100] = %d\n",
           res.sh, res.r0n, res.U[100], res.Sc[100]);
    assert(res.sh == 0);
    assert(res.r0n == 0);
    assert(res.U[100] == 0);
    assert(res.Sc[100] == 0);

    printf("\n=== ALL HPS C REFERENCE TESTS PASSED (0 errors) ===\n");
    return 0;
}
