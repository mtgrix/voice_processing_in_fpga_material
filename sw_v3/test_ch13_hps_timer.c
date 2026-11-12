// sw_v3/test_ch13_hps_timer.c
// Test harness for Chapter 13 HPS timing code in simulation mode (-DSIM)

#include "ch13_hps_timer.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

int main(void) {
    printf("====================================================================\n");
    printf("KIỂM THỬ ĐO THỜI GIAN HPS C DRIVER (sw_v3/ch13_hps_timer.c)\n");
    printf("====================================================================\n");

    const char *wav_path = "golden_v2/synth_glide_vuv_16k.wav";
    FILE *f_test = fopen(wav_path, "rb");
    if (!f_test) {
        wav_path = "../golden_v2/synth_glide_vuv_16k.wav";
        f_test = fopen(wav_path, "rb");
    }
    if (f_test) {
        fclose(f_test);
    } else {
        fprintf(stderr, "[FAIL] Không tìm thấy tệp synth_glide_vuv_16k.wav\n");
        return 1;
    }

    const char *bin_out = "ch13_test_pitch_f0.bin";
    const char *meta_out = "ch13_test_pitch_meta.txt";

    hps_timing_report_t report;
    int rc = hps_timed_analysis(wav_path, bin_out, meta_out, &report);
    if (rc != 0) {
        fprintf(stderr, "[FAIL] Không thể chạy phép đo thời gian HPS (mã lỗi %d)\n", rc);
        return 1;
    }

    hps_print_timing_report(&report);

    assert(report.audio_dur_s > 2.7 && report.audio_dur_s < 2.9);
    assert(report.n_frames == 277);
    assert(report.t_read_ms >= 0.0);
    assert(report.t_stream_ms >= 0.0);
    assert(report.t_write_ms >= 0.0);
    assert(report.t_total_ms >= 0.0);

    // Clean up temporary files
    remove(bin_out);
    remove(meta_out);
    remove("pitch_f0.bin");
    remove("pitch_meta.txt");

    printf("[PASS] KIỂM THỬ ĐO THỜI GIAN HPS THÀNH CÔNG (0 LỖI)!\n");
    return 0;
}
