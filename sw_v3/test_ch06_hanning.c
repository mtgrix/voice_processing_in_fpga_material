/* sw_v3/test_ch06_hanning.c
 * Unit test for ch06_hanning.c:
 * Verifies w[0], w[318], w[319], sum, symmetry, and stress frame results against golden_v2.
 */

#include "ch06_hanning.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int main(void) {
    printf("=== RUNNING HPS C UNIT TEST: CH06 HANNING WINDOW ===\n");

    uint16_t w[CH06_NSAMP_WINDOW];
    ch06_generate_hanning_q15(w, CH06_NSAMP_WINDOW);

    /* 1. Verify canonical values */
    printf("w[0]   = %u (expected 1)\n", w[0]);
    printf("w[318] = %u (expected 32767)\n", w[318]);
    printf("w[319] = %u (expected 32767)\n", w[319]);
    printf("w[637] = %u (expected 1)\n", w[637]);

    assert(w[0] == 1);
    assert(w[318] == 32767);
    assert(w[319] == 32767);
    assert(w[637] == 1);

    /* 2. Verify sum */
    uint64_t sum = 0;
    for (size_t i = 0; i < CH06_NSAMP_WINDOW; i++) {
        sum += w[i];
    }
    printf("Sum    = %llu (expected 10469378)\n", (unsigned long long)sum);
    assert(sum == 10469378ULL);

    /* 3. Verify symmetry */
    for (size_t i = 0; i < CH06_NSAMP_WINDOW; i++) {
        assert(w[i] == w[CH06_NSAMP_WINDOW - 1 - i]);
    }
    printf("Symmetry check: PASS (all 638 samples symmetric)\n");

    /* 4. Test Stress Frame A (pulse +32767 on background -32768, mean = -26614) */
    int32_t d_stress[CH06_NSAMP_WINDOW];
    int32_t xw_stress[CH06_NSAMP_WINDOW];
    int32_t mean = -26614;

    for (size_t i = 0; i < CH06_NSAMP_WINDOW; i++) {
        int32_t raw_x = (i >= 300 && i < 340) ? 32767 : -32768;
        d_stress[i] = raw_x - mean;
    }

    uint16_t lp = ch06_apply_window_fixed(d_stress, w, xw_stress, CH06_NSAMP_WINDOW);
    printf("Stress Frame A LocalPeak LP = %u (expected 59379)\n", lp);
    assert(lp == 59379);
    assert(xw_stress[318] == 59379);

    printf("=== ALL HPS C UNIT TESTS PASSED SUCCESSFULLY! ===\n");
    return 0;
}
