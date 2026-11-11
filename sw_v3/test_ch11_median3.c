#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include "ch11_median3.h"

static int test_scalar(void) {
    printf("[TEST 1] Testing ch11_median3_scalar permutations and ties...\n");
    struct { uint16_t a, b, c, expected; } cases[] = {
        {10, 20, 30, 20}, {10, 30, 20, 20}, {20, 10, 30, 20},
        {20, 30, 10, 20}, {30, 10, 20, 20}, {30, 20, 10, 20},
        {20, 20, 10, 20}, {20, 20, 30, 20}, {10, 20, 20, 20},
        {30, 20, 20, 20}, {20, 10, 20, 20}, {20, 30, 20, 20},
        {25, 25, 25, 25}
    };
    size_t n = sizeof(cases) / sizeof(cases[0]);
    for (size_t i = 0; i < n; ++i) {
        uint16_t med = ch11_median3_scalar(cases[i].a, cases[i].b, cases[i].c);
        if (med != cases[i].expected) {
            fprintf(stderr, "[FAIL] scalar(%u, %u, %u) = %u, expected %u\n",
                    cases[i].a, cases[i].b, cases[i].c, med, cases[i].expected);
            return -1;
        }
    }
    printf("  => 13/13 permutation and tie cases PASSED.\n");
    return 0;
}

static int test_hand_example(void) {
    printf("[TEST 2] Testing agenda hand calculation example...\n");
    const uint16_t in[6]  = {120, 122, 244, 121, 0, 0};
    const uint16_t exp[6] = {120, 122, 122, 121, 0, 0};
    uint16_t out_arr[6];

    ch11_median3_array(in, out_arr, 6);
    for (size_t i = 0; i < 6; ++i) {
        if (out_arr[i] != exp[i]) {
            fprintf(stderr, "[FAIL] hand_example array[%zu] = %u, expected %u\n",
                    i, out_arr[i], exp[i]);
            return -1;
        }
    }

    // Now test stream implementation
    ch11_median3_stream_t st;
    ch11_median3_stream_init(&st);
    uint16_t out_str[6];
    size_t out_cnt = 0;

    for (size_t i = 0; i < 6; ++i) {
        int vld = 0, last = 0;
        uint16_t val = 0;
        ch11_median3_stream_step(&st, 1, (i == 0), (i == 5), in[i], &vld, &last, &val);
        if (vld) {
            out_str[out_cnt++] = val;
        }
    }
    // Flush beat
    int vld = 0, last = 0;
    uint16_t val = 0;
    ch11_median3_stream_step(&st, 0, 0, 0, 0, &vld, &last, &val);
    if (vld) {
        out_str[out_cnt++] = val;
    }

    assert(out_cnt == 6);
    for (size_t i = 0; i < 6; ++i) {
        if (out_str[i] != exp[i]) {
            fprintf(stderr, "[FAIL] hand_example stream[%zu] = %u, expected %u\n",
                    i, out_str[i], exp[i]);
            return -1;
        }
    }

    printf("  => Hand calculation [120, 122, 244, 121, 0, 0] -> [120, 122, 122, 121, 0, 0] PASSED.\n");
    return 0;
}

static int test_edge_cases(void) {
    printf("[TEST 3] Testing edge cases N=1 and N=2...\n");
    // N = 1
    const uint16_t in1[1] = {3200};
    uint16_t out1[1];
    ch11_median3_array(in1, out1, 1);
    assert(out1[0] == 3200);

    ch11_median3_stream_t st1;
    ch11_median3_stream_init(&st1);
    int vld = 0, last = 0;
    uint16_t val = 0;
    ch11_median3_stream_step(&st1, 1, 1, 1, in1[0], &vld, &last, &val);
    assert(vld == 0); // No output on cycle 1
    ch11_median3_stream_step(&st1, 0, 0, 0, 0, &vld, &last, &val);
    assert(vld == 1 && last == 1 && val == 3200);

    // N = 2
    const uint16_t in2[2] = {1000, 2000};
    uint16_t out2[2];
    ch11_median3_array(in2, out2, 2);
    assert(out2[0] == 1000 && out2[1] == 2000);

    ch11_median3_stream_t st2;
    ch11_median3_stream_init(&st2);
    ch11_median3_stream_step(&st2, 1, 1, 0, in2[0], &vld, &last, &val);
    assert(vld == 0);
    ch11_median3_stream_step(&st2, 1, 0, 1, in2[1], &vld, &last, &val);
    assert(vld == 1 && last == 0 && val == 1000);
    ch11_median3_stream_step(&st2, 0, 0, 0, 0, &vld, &last, &val);
    assert(vld == 1 && last == 1 && val == 2000);

    printf("  => Edge cases N=1 and N=2 PASSED.\n");
    return 0;
}

static int test_spikes_and_dropouts(void) {
    printf("[TEST 4] Testing single spikes, double spikes, and dropouts...\n");
    // Single spike
    const uint16_t sp1[5] = {150, 150, 300, 150, 150};
    uint16_t out_sp1[5];
    ch11_median3_array(sp1, out_sp1, 5);
    for (size_t i = 0; i < 5; ++i) {
        assert(out_sp1[i] == 150);
    }

    // Double spike
    const uint16_t sp2[6] = {150, 150, 300, 300, 150, 150};
    uint16_t out_sp2[6];
    ch11_median3_array(sp2, out_sp2, 6);
    assert(out_sp2[2] == 300 && out_sp2[3] == 300);

    // Dropout
    const uint16_t drop[5] = {150, 150, 0, 150, 150};
    uint16_t out_drop[5];
    ch11_median3_array(drop, out_drop, 5);
    for (size_t i = 0; i < 5; ++i) {
        assert(out_drop[i] == 150);
    }

    // Glitch in silence
    const uint16_t glitch[5] = {0, 0, 150, 0, 0};
    uint16_t out_glitch[5];
    ch11_median3_array(glitch, out_glitch, 5);
    for (size_t i = 0; i < 5; ++i) {
        assert(out_glitch[i] == 0);
    }

    printf("  => Spikes and dropouts PASSED.\n");
    return 0;
}

int main(void) {
    printf("=================================================================\n");
    printf("UNIT TEST: CH11 MEDIAN-3 (C REFERENCE IMPLEMENTATION)\n");
    printf("=================================================================\n");

    if (test_scalar() != 0) return 1;
    if (test_hand_example() != 0) return 1;
    if (test_edge_cases() != 0) return 1;
    if (test_spikes_and_dropouts() != 0) return 1;

    printf("=================================================================\n");
    printf("ALL CH11 C UNIT TESTS PASSED SUCCESSFULLY (0 ERRORS)!\n");
    printf("=================================================================\n");
    return 0;
}
