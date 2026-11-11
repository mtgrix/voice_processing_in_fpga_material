// sw_v3/test_ch09_f0.c
// Unit test for Chapter 9 C reference implementation

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "ch09_f0.h"

int main(void) {
    printf("=== [test_ch09_f0] Running Chapter 9 C Reference Tests ===\n");

    // ------------------------------------------------------------------------
    // Test 1: Hand calculation example: y = (8000, 10000, 9000) at tau_p = 100
    // ------------------------------------------------------------------------
    {
        int32_t U[CH09_TAU_SCAN_MAX + 1] = {0};
        int32_t Sc[CH09_TAU_SCAN_MAX + 1] = {0};
        uint32_t r0n = 10000;

        U[99]  = 8000;
        U[100] = 10000;
        U[101] = 9000;
        Sc[100] = 5000;

        ch09_f0_result_t res;
        ch09_calc_f0(U, Sc, r0n, &res);

        printf("Test 1 (Hand Example): found=%d, tau=%d, num=%d, den=%d, f0q=%d\n",
               res.found, res.best_tau, res.num, res.den, res.f0_raw);
        assert(res.found == true);
        assert(res.best_tau == 100);
        assert(res.num == 1000);
        assert(res.den == 3000);
        assert(res.s2 == 0);
        assert(res.f0_raw == 2556);
        printf("Test 1 PASSED: f0q = 2556 (expected 2556)\n");
    }

    // ------------------------------------------------------------------------
    // Test 2: Exercise 2: y = (9500, 10000, 8500) at tau_p = 80 (delta = -0.25)
    // ------------------------------------------------------------------------
    {
        int32_t U[CH09_TAU_SCAN_MAX + 1] = {0};
        int32_t Sc[CH09_TAU_SCAN_MAX + 1] = {0};
        uint32_t r0n = 10000;

        U[79] = 9500;
        U[80] = 10000;
        U[81] = 8500;
        Sc[80] = 6000;

        ch09_f0_result_t res;
        ch09_calc_f0(U, Sc, r0n, &res);

        printf("Test 2 (Exercise 2): found=%d, tau=%d, num=%d, den=%d, f0q=%d\n",
               res.found, res.best_tau, res.num, res.den, res.f0_raw);
        assert(res.found == true);
        assert(res.best_tau == 80);
        assert(res.num == -1000);
        assert(res.den == 2000);
        assert(res.s2 == 0);
        assert(res.f0_raw == 3210);
        printf("Test 2 PASSED: f0q = 3210 (expected 3210)\n");
    }

    // ------------------------------------------------------------------------
    // Test 3: Unvoiced frame: peaks fail 40*U > 9*R0n threshold
    // ------------------------------------------------------------------------
    {
        int32_t U[CH09_TAU_SCAN_MAX + 1] = {0};
        int32_t Sc[CH09_TAU_SCAN_MAX + 1] = {0};
        uint32_t r0n = 100000; // 9 * r0n = 900,000

        // Peak at tau = 50: U[50] = 2000 -> 40 * U[50] = 80,000 < 900,000
        U[49] = 1000;
        U[50] = 2000;
        U[51] = 1000;
        Sc[50] = 1500;

        ch09_f0_result_t res;
        ch09_calc_f0(U, Sc, r0n, &res);

        printf("Test 3 (Unvoiced Frame): found=%d, f0q=%d\n", res.found, res.f0_raw);
        assert(res.found == false);
        assert(res.f0_raw == 0);
        printf("Test 3 PASSED: unvoiced rejected correctly\n");
    }

    // ------------------------------------------------------------------------
    // Test 4: Multiple candidates with Argmax Sc selection and tie-breaking
    // ------------------------------------------------------------------------
    {
        int32_t U[CH09_TAU_SCAN_MAX + 1] = {0};
        int32_t Sc[CH09_TAU_SCAN_MAX + 1] = {0};
        uint32_t r0n = 10000;

        // Peak 1 at tau = 40, U=5000, Sc=3000
        U[39] = 4000; U[40] = 5000; U[41] = 4000; Sc[40] = 3000;
        // Peak 2 at tau = 80, U=6000, Sc=7000 (Higher Sc -> should win!)
        U[79] = 5000; U[80] = 6000; U[81] = 5000; Sc[80] = 7000;
        // Peak 3 at tau = 160, U=7000, Sc=7000 (Equal Sc to peak 2 -> peak 2 should win tie!)
        U[159] = 6000; U[160] = 7000; U[161] = 6000; Sc[160] = 7000;

        ch09_f0_result_t res;
        ch09_calc_f0(U, Sc, r0n, &res);

        printf("Test 4 (Argmax Sc & Tie-Break): found=%d, best_tau=%d, sc=%d\n",
               res.found, res.best_tau, res.best_sc);
        assert(res.found == true);
        assert(res.best_tau == 80); // Peak 2 wins over peak 1 (higher Sc) and peak 3 (earlier)
        assert(res.best_sc == 7000);
        printf("Test 4 PASSED: argmax Sc and earlier tie-break verified\n");
    }

    // ------------------------------------------------------------------------
    // Test 5: Dynamic s2 Normalization (large den > 2^24)
    // ------------------------------------------------------------------------
    {
        int32_t U[CH09_TAU_SCAN_MAX + 1] = {0};
        int32_t Sc[CH09_TAU_SCAN_MAX + 1] = {0};
        uint32_t r0n = 50000000;

        // Peak at tau = 120 with large den
        // u0 = 20,000,000, um = 11,000,000, up = 12,000,000
        // den = 40,000,000 - 11,000,000 - 12,000,000 = 17,000,000 > 2^24 (16,777,216) -> s2 = 1
        U[119] = 11000000;
        U[120] = 20000000;
        U[121] = 12000000;
        Sc[120] = 15000000;

        ch09_f0_result_t res;
        ch09_calc_f0(U, Sc, r0n, &res);

        printf("Test 5 (s2 Normalization): den=%d, s2=%d, f0q=%d\n",
               res.den, res.s2, res.f0_raw);
        assert(res.found == true);
        assert(res.den == 17000000);
        assert(res.s2 == 1);
        assert(res.f0_raw > 0);
        printf("Test 5 PASSED: s2 shift correctly applied\n");
    }

    printf("=== [test_ch09_f0] ALL CHAPTER 9 C TESTS PASSED (0 ERRORS) ===\n");
    return 0;
}
