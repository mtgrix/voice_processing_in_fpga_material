// sw_v3/ch13_hps_timer.c
// Implementation of high-resolution 3-stage POSIX timer for HPS-to-FPGA execution.
// Measures elapsed time via clock_gettime(CLOCK_MONOTONIC) across:
//   1. File read & preprocessing (WAV reading, chunk parsing, globalPeak)
//   2. Sample streaming over Lightweight Bridge, FPGA computation, F0 read
//   3. Binary file writing (pitch_f0.bin and pitch_meta.txt)

#include "ch13_hps_timer.h"
#include "ch12_driver.h"
#include "ch01_wav.h"
#include "ch01_frames.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int64_t timespec_diff_ns(struct timespec start, struct timespec end) {
    int64_t sec = (int64_t)(end.tv_sec - start.tv_sec);
    int64_t nsec = (int64_t)(end.tv_nsec - start.tv_nsec);
    return sec * 1000000000LL + nsec;
}

int hps_timed_analysis(const char *wav_path, const char *bin_out_path,
                       const char *meta_out_path, hps_timing_report_t *report) {
    if (!wav_path || !bin_out_path || !meta_out_path || !report) {
        return -1;
    }
    memset(report, 0, sizeof(hps_timing_report_t));

    struct timespec t0, t1, t2, t3;

    // =========================================================================
    // GIAI ĐOẠN 1: Đọc tệp WAV từ ổ đĩa/thẻ nhớ, giải mã header, tính globalPeak
    // =========================================================================
    clock_gettime(CLOCK_MONOTONIC, &t0);

    wav_file_t wav;
    if (wav_read_file(wav_path, &wav) != 0) {
        fprintf(stderr, "[CH13 HPS TIMER] Lỗi: Không thể đọc tệp WAV %s\n", wav_path);
        return -2;
    }

    uint16_t gp = (uint16_t)wav.global_peak;
    report->audio_dur_s = (double)wav.num_samples / (double)wav.sample_rate;

    clock_gettime(CLOCK_MONOTONIC, &t1);
    report->t_read_ms = (double)timespec_diff_ns(t0, t1) / 1e6;

    // =========================================================================
    // GIAI ĐOẠN 2: Truyền dữ liệu mẫu qua cầu Lightweight HPS-to-FPGA Bridge,
    //               xử lý trên lõi phần cứng FPGA và đọc kết quả F0
    // =========================================================================
    ch12_pipeline_stats_t stats;
    if (ch12_run_f0_pipeline(wav_path, ".", &stats) != 0) {
        fprintf(stderr, "[CH13 HPS TIMER] Lỗi trong quá trình chạy lõi FPGA\n");
        wav_free(&wav);
        return -3;
    }

    clock_gettime(CLOCK_MONOTONIC, &t2);
    report->t_stream_ms = (double)timespec_diff_ns(t1, t2) / 1e6;
    report->n_frames = stats.n_frames;
    report->fpga_cycles = stats.total_cycles;

    // =========================================================================
    // GIAI ĐOẠN 3: Ghi kết quả định dạng Q12.4 xuống pitch_f0.bin và pitch_meta.txt
    // =========================================================================
    struct timespec tw0, tw1;
    clock_gettime(CLOCK_MONOTONIC, &tw0);

    FILE *f_in = fopen("pitch_f0.bin", "rb");
    if (f_in) {
        uint16_t *buf = (uint16_t *)malloc(stats.n_frames * sizeof(uint16_t));
        if (buf) {
            size_t n_read = fread(buf, sizeof(uint16_t), stats.n_frames, f_in);
            fclose(f_in);
            if (n_read == stats.n_frames) {
                ch12_write_pitch_bin(bin_out_path, buf, stats.n_frames);
            }
            free(buf);
        } else {
            fclose(f_in);
        }
    }
    ch12_write_pitch_meta(meta_out_path, stats.t1, stats.dt, stats.n_frames,
                          stats.first_win0, gp);

    clock_gettime(CLOCK_MONOTONIC, &tw1);
    report->t_write_ms = (double)timespec_diff_ns(tw0, tw1) / 1e6;

    clock_gettime(CLOCK_MONOTONIC, &t3);
    report->t_total_ms = (double)timespec_diff_ns(t0, t3) / 1e6;

    if (report->audio_dur_s > 0.0) {
        report->rtf_stream = (report->t_stream_ms / 1000.0) / report->audio_dur_s;
        report->rtf_total  = (report->t_total_ms / 1000.0) / report->audio_dur_s;
    }

    wav_free(&wav);
    return 0;
}

void hps_print_timing_report(const hps_timing_report_t *report) {
    if (!report) return;
    printf("====================================================================\n");
    printf("BÁO CÁO ĐO THỜI GIAN VÀ HIỆU NĂNG HPS (CLOCK_MONOTONIC)\n");
    printf("====================================================================\n");
    printf("  1. Thời lượng âm thanh gốc     : %8.4f s (%u khung)\n", report->audio_dur_s, report->n_frames);
    printf("  2. Giai đoạn 1 (Đọc WAV & GP)  : %8.3f ms\n", report->t_read_ms);
    printf("  3. Giai đoạn 2 (Truyền & FPGA) : %8.3f ms (Chu kỳ FPGA: %u)\n", report->t_stream_ms, report->fpga_cycles);
    printf("  4. Giai đoạn 3 (Ghi tệp ra)    : %8.3f ms\n", report->t_write_ms);
    printf("  5. Tổng thời gian toàn tuyến   : %8.3f ms\n", report->t_total_ms);
    printf("  --------------------------------------------------------------------\n");
    printf("  6. RTF Giai đoạn 2 (Truyền+FPGA): %8.4f (nhanh gấp %5.2fx realtime)\n",
           report->rtf_stream, report->rtf_stream > 0 ? (1.0 / report->rtf_stream) : 0.0);
    printf("  7. RTF Toàn tuyến HPS          : %8.4f (nhanh gấp %5.2fx realtime)\n",
           report->rtf_total, report->rtf_total > 0 ? (1.0 / report->rtf_total) : 0.0);
    printf("====================================================================\n");
}
