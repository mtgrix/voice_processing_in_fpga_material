// sw_v3/test_ch10_voicing.c
// Unit test runner for Chapter 10 voicing decision logic
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "ch10_voicing.h"

int main(void)
{
    printf("======================================================================\n");
    printf("UNIT TESTS: CH10 VOICING DECISION (HPS C REFERENCE)\n");
    printf("======================================================================\n");

    ch10_voicing_result_t res;
    int test_count = 0;
    int pass_count = 0;

    // Test 1: Voiced Speech (I=0.10, Sc/R0n=0.80)
    test_count++;
    ch10_decide_voicing(2560, 800000, 1000000, true, 2000, 20000, &res);
    printf("[Test 1] Voiced Speech: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == true && res.f0 == 2560);
    pass_count++;

    // Test 2: Flat Voiceless (I=0.10, Sc/R0n=0.35)
    test_count++;
    ch10_decide_voicing(2560, 350000, 1000000, true, 2000, 20000, &res);
    printf("[Test 2] Flat Voiceless: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == false && res.f0 == 0);
    pass_count++;

    // Test 3: Strict Silence (I=0.02 < 0.03)
    test_count++;
    ch10_decide_voicing(2560, 700000, 1000000, true, 400, 20000, &res);
    printf("[Test 3] Strict Silence: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == false && res.f0 == 0);
    pass_count++;

    // Test 4: Ramp Zone Voiced (I=0.038, Sc/R0n=0.70)
    test_count++;
    ch10_decide_voicing(2560, 700000, 1000000, true, 760, 20000, &res);
    printf("[Test 4] Ramp Zone Voiced: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == true && res.f0 == 2560);
    pass_count++;

    // Test 5: Ramp Zone Voiceless (I=0.035, Sc/R0n=0.60)
    test_count++;
    ch10_decide_voicing(2560, 600000, 1000000, true, 700, 20000, &res);
    printf("[Test 5] Ramp Zone Voiceless: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == false && res.f0 == 0);
    pass_count++;

    // Test 6: Near-threshold 0.4499
    test_count++;
    ch10_decide_voicing(2560, 449900, 1000000, true, 2000, 20000, &res);
    printf("[Test 6] Near-threshold 0.4499: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == false && res.f0 == 0);
    pass_count++;

    // Test 7: Near-threshold 0.4501
    test_count++;
    ch10_decide_voicing(2560, 450100, 1000000, true, 2000, 20000, &res);
    printf("[Test 7] Near-threshold 0.4501: voiced=%d, f0=%u, LHS=%lld, RHS=%lld\n",
           res.voiced, res.f0, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == true && res.f0 == 2560);
    pass_count++;

    // Test 8: Silence shortcut LP=0
    test_count++;
    ch10_decide_voicing(2560, 800000, 1000000, true, 0, 20000, &res);
    printf("[Test 8] Silence shortcut LP=0: voiced=%d, silence_trap=%d\n",
           res.voiced, res.silence_trap);
    assert(res.voiced == false && res.silence_trap == true);
    pass_count++;

    // Test 9: Silence shortcut GP=0
    test_count++;
    ch10_decide_voicing(2560, 800000, 1000000, true, 2000, 0, &res);
    printf("[Test 9] Silence shortcut GP=0: voiced=%d, silence_trap=%d\n",
           res.voiced, res.silence_trap);
    assert(res.voiced == false && res.silence_trap == true);
    pass_count++;

    // Test 10: Silence shortcut R0=0
    test_count++;
    ch10_decide_voicing(2560, 800000, 0, true, 2000, 20000, &res);
    printf("[Test 10] Silence shortcut R0=0: voiced=%d, silence_trap=%d\n",
           res.voiced, res.silence_trap);
    assert(res.voiced == false && res.silence_trap == true);
    pass_count++;

    // Test 11: No candidate found (!cand_found)
    test_count++;
    ch10_decide_voicing(0, 0, 1000000, false, 2000, 20000, &res);
    printf("[Test 11] No candidate found: voiced=%d, silence_trap=%d\n",
           res.voiced, res.silence_trap);
    assert(res.voiced == false && res.silence_trap == true);
    pass_count++;

    // Test 12: Stress frame max dynamic range
    test_count++;
    int32_t sc_stress = (1 << 27) - 1;
    uint32_t r0n_stress = (1 << 27) - 1;
    uint16_t gp_stress = 32768;
    uint16_t lp_stress = 59379;
    ch10_decide_voicing(4000, sc_stress, r0n_stress, true, lp_stress, gp_stress, &res);
    printf("[Test 12] Max dynamic range stress: voiced=%d, LHS=%lld, RHS=%lld\n",
           res.voiced, (long long)res.lhs, (long long)res.rhs);
    assert(res.voiced == true);
    pass_count++;

    printf("======================================================================\n");
    printf("SUMMARY: %d / %d tests PASSED successfully.\n", pass_count, test_count);
    printf("======================================================================\n");
    return 0;
}
