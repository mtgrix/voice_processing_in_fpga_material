// sw_v3/test_ch07_mac.c
// Test program for ch07_mac.c against golden_v2/hdl_check/xw.hex and exp.hex
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <inttypes.h>
#include "ch07_mac.h"

#define NFRAMES 16

static int32_t sign_extend_17(uint32_t v) {
    if (v & 0x10000) {
        return (int32_t)(v | 0xFFFE0000);
    }
    return (int32_t)v;
}

static int64_t sign_extend_48(uint64_t v) {
    if (v & 0x800000000000ULL) {
        return (int64_t)(v | 0xFFFF000000000000ULL);
    }
    return (int64_t)v;
}

int main(void) {
    printf("=== CH07 HPS C REFERENCE AUTOCORRELATION TEST ===\n");

    const char *xw_path = "golden_v2/hdl_check/xw.hex";
    const char *exp_path = "golden_v2/hdl_check/exp.hex";

    FILE *fx = fopen(xw_path, "r");
    if (!fx) fx = fopen("../golden_v2/hdl_check/xw.hex", "r");
    if (!fx) {
        fprintf(stderr, "[FAIL] Cannot open xw.hex\n");
        return 1;
    }

    FILE *fe = fopen(exp_path, "r");
    if (!fe) fe = fopen("../golden_v2/hdl_check/exp.hex", "r");
    if (!fe) {
        fprintf(stderr, "[FAIL] Cannot open exp.hex\n");
        fclose(fx);
        return 1;
    }

    int total_errors = 0;
    int total_checked = 0;

    for (int f = 0; f < NFRAMES; ++f) {
        int32_t xw[CH07_NSAMP_WINDOW];
        for (int n = 0; n < CH07_NSAMP_WINDOW; ++n) {
            uint32_t val;
            if (fscanf(fx, "%x", &val) != 1) {
                fprintf(stderr, "[FAIL] Premature EOF reading xw.hex at frame %d, sample %d\n", f, n);
                fclose(fx); fclose(fe);
                return 1;
            }
            xw[n] = sign_extend_17(val);
        }

        int64_t exp_res[CH07_NLAGS];
        for (int i = 0; i < CH07_NLAGS; ++i) {
            uint64_t val;
            if (fscanf(fe, "%" SCNx64, &val) != 1) {
                fprintf(stderr, "[FAIL] Premature EOF reading exp.hex at frame %d, lag %d\n", f, i);
                fclose(fx); fclose(fe);
                return 1;
            }
            exp_res[i] = sign_extend_48(val);
        }

        int64_t R[CH07_TAU_MAX + 1];
        ch07_autocorr_mac(xw, R);

        // Verify R[0]
        if (R[0] != exp_res[0]) {
            total_errors++;
            printf("[MISMATCH] Frame %d, R[0]: got %" PRId64 " exp %" PRId64 "\n", f, R[0], exp_res[0]);
        }
        total_checked++;

        // Verify R[26..214]
        for (int tau = CH07_TAU_MIN; tau <= CH07_TAU_MAX; ++tau) {
            int exp_idx = 1 + (tau - CH07_TAU_MIN);
            if (R[tau] != exp_res[exp_idx]) {
                total_errors++;
                if (total_errors <= 5) {
                    printf("[MISMATCH] Frame %d, R[%d]: got %" PRId64 " exp %" PRId64 "\n",
                           f, tau, R[tau], exp_res[exp_idx]);
                }
            }
            total_checked++;
        }
    }

    fclose(fx);
    fclose(fe);

    printf("Checked %d results across %d frames. Total errors: %d\n", total_checked, NFRAMES, total_errors);
    if (total_errors == 0 && total_checked == 3040) {
        printf("=== ALL %d RESULTS MATCHED 100%% BIT-EXACT ===\n", total_checked);
        return 0;
    } else {
        printf("[FAIL] Verification failed with %d errors!\n", total_errors);
        return 1;
    }
}
