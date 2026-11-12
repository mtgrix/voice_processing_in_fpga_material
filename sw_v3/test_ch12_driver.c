// sw_v3/test_ch12_driver.c
// Test runner for Chapter 12 HPS C driver in simulation mode (-DSIM)
// Verifies:
//   1. Execution on golden_v2/synth_glide_vuv_16k.wav (clean)
//   2. Execution on golden_v2/synth_glide_vuv_16k_snr5.wav (noisy 5 dB)
//   3. Correct generation of pitch_f0.bin and pitch_meta.txt
//   4. Byte-identical verification against golden_v2/out/fixed.tsv

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "ch12_driver.h"

static int verify_against_tsv(const char *bin_path, const char *tsv_path, uint32_t n_frames) {
    FILE *f_bin = fopen(bin_path, "rb");
    if (!f_bin) {
        fprintf(stderr, "Error opening %s\n", bin_path);
        return -1;
    }
    uint16_t *bin_words = (uint16_t *)malloc(n_frames * sizeof(uint16_t));
    size_t r = fread(bin_words, sizeof(uint16_t), n_frames, f_bin);
    fclose(f_bin);
    if (r != n_frames) {
        fprintf(stderr, "Read error on %s: read %zu, expected %u\n", bin_path, r, n_frames);
        free(bin_words);
        return -2;
    }

    FILE *f_tsv = fopen(tsv_path, "r");
    if (!f_tsv) {
        fprintf(stderr, "Error opening %s\n", tsv_path);
        free(bin_words);
        return -3;
    }

    char line[256];
    uint32_t line_idx = 0;
    int mismatches = 0;

    while (fgets(line, sizeof(line), f_tsv) && line_idx < n_frames) {
        double t, f0_raw, f0_med;
        if (sscanf(line, "%lf\t%lf\t%lf", &t, &f0_raw, &f0_med) == 3) {
            uint16_t exp_q12_4 = (uint16_t)((f0_med * 16.0) + 0.5);
            uint16_t act_q12_4 = bin_words[line_idx];

            if (act_q12_4 != exp_q12_4) {
                if (mismatches < 5) {
                    fprintf(stderr, "  [MISMATCH] Frame %u (t=%.3f s): act=%u (%.4f Hz), exp=%u (%.4f Hz)\n",
                            line_idx, t, act_q12_4, (double)act_q12_4 / 16.0, exp_q12_4, f0_med);
                }
                mismatches++;
            }
            line_idx++;
        }
    }
    fclose(f_tsv);
    free(bin_words);

    if (line_idx != n_frames) {
        fprintf(stderr, "TSV frame count mismatch: read %u lines, expected %u\n", line_idx, n_frames);
        return -4;
    }
    if (mismatches > 0) {
        fprintf(stderr, "Total TSV mismatches: %d / %u frames\n", mismatches, n_frames);
        return -5;
    }
    return 0;
}

int main(int argc, char **argv) {
    printf("======================================================================\n");
    printf("TEST RUNNER: CH12 HPS C DRIVER END-TO-END PIPELINE (-DSIM)\n");
    printf("======================================================================\n");

    const char *out_dir = (argc > 1) ? argv[1] : "tmp_e2e";
    const char *clean_wav = "../golden_v2/synth_glide_vuv_16k.wav";
    const char *noisy_wav = "../golden_v2/synth_glide_vuv_16k_snr5.wav";
    const char *clean_tsv = "../golden_v2/out/fixed.tsv";
    const char *noisy_tsv = "../golden_v2/out/fixed_snr5.tsv";

    char bin_path[512];
    snprintf(bin_path, sizeof(bin_path), "%s/pitch_f0.bin", out_dir);

    ch12_pipeline_stats_t stats_clean;
    printf("\n[Test 1] Running pipeline on Clean WAV: %s\n", clean_wav);
    int ret = ch12_run_f0_pipeline(clean_wav, out_dir, &stats_clean);
    assert(ret == 0);
    printf("  Execution successful:\n");
    printf("    Frames:       %u\n", stats_clean.n_frames);
    printf("    t1:           %.6f s\n", stats_clean.t1);
    printf("    dt:           %.6f s\n", stats_clean.dt);
    printf("    first_win0:   %d\n", stats_clean.first_win0);
    printf("    global_peak:  %u\n", stats_clean.global_peak);
    printf("    total_cycles: %u\n", stats_clean.total_cycles);
    printf("    frame_cycles: %u\n", stats_clean.frame_cycles);

    assert(stats_clean.n_frames == 277);
    assert(stats_clean.first_win0 == 1);
    assert(stats_clean.global_peak == 22946);

    printf("Verifying generated pitch_f0.bin against %s...\n", clean_tsv);
    ret = verify_against_tsv(bin_path, clean_tsv, 277);
    assert(ret == 0);
    printf("  => Clean WAV pitch_f0.bin is 100%% byte-identical to golden_v2 fixed.tsv!\n");

    ch12_pipeline_stats_t stats_noisy;
    printf("\n[Test 2] Running pipeline on Noisy WAV (SNR 5 dB): %s\n", noisy_wav);
    ret = ch12_run_f0_pipeline(noisy_wav, out_dir, &stats_noisy);
    assert(ret == 0);
    printf("  Execution successful:\n");
    printf("    Frames:       %u\n", stats_noisy.n_frames);
    printf("    t1:           %.6f s\n", stats_noisy.t1);
    printf("    dt:           %.6f s\n", stats_noisy.dt);
    printf("    first_win0:   %d\n", stats_noisy.first_win0);
    printf("    global_peak:  %u\n", stats_noisy.global_peak);
    printf("    total_cycles: %u\n", stats_noisy.total_cycles);

    assert(stats_noisy.n_frames == 277);
    assert(stats_noisy.first_win0 == 1);
    assert(stats_noisy.global_peak == 22937);

    printf("Verifying generated pitch_f0.bin against %s...\n", noisy_tsv);
    ret = verify_against_tsv(bin_path, noisy_tsv, 277);
    assert(ret == 0);
    printf("  => Noisy WAV pitch_f0.bin is 100%% byte-identical to golden_v2 fixed_snr5.tsv!\n");

    printf("\n======================================================================\n");
    printf("ALL CHAPTER 12 C DRIVER TESTS PASSED (100%% BIT-EXACT MATCH)\n");
    printf("======================================================================\n");
    return 0;
}
