// sw_v3/ch13_hps_timer.h
// High-resolution three-stage POSIX timer for HPS-to-FPGA execution
// Uses clock_gettime(CLOCK_MONOTONIC) to isolate:
//   Stage 1: Reading WAV from storage, parsing RIFF, calculating globalPeak.
//   Stage 2: Streaming audio samples over Lightweight Bridge, FPGA computation, reading F0.
//   Stage 3: Formatting and writing pitch_f0.bin and pitch_meta.txt to storage.

#ifndef CH13_HPS_TIMER_H
#define CH13_HPS_TIMER_H

#include <stdint.h>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double t_read_ms;       // Stage 1: File reading & preprocessing (ms)
    double t_stream_ms;     // Stage 2: Bridge transfer & FPGA computation (ms)
    double t_write_ms;      // Stage 3: File output writing (ms)
    double t_total_ms;      // Total wall-clock time across all 3 stages (ms)
    double audio_dur_s;     // Audio signal duration (s)
    double rtf_stream;      // RTF for Stage 2 alone (t_stream / t_audio)
    double rtf_total;       // RTF for end-to-end HPS pipeline (t_total / t_audio)
    uint32_t n_frames;      // Total number of analysis frames
    uint32_t fpga_cycles;   // FPGA core cycles read from CSR REG_CTRL_TOTAL_CYCLES
} hps_timing_report_t;

// Calculate difference between two timespec timestamps in nanoseconds
int64_t timespec_diff_ns(struct timespec start, struct timespec end);

// Execute the full three-stage timed pipeline on a WAV file
int hps_timed_analysis(const char *wav_path, const char *bin_out_path,
                       const char *meta_out_path, hps_timing_report_t *report);

// Print timing report to console
void hps_print_timing_report(const hps_timing_report_t *report);

#ifdef __cplusplus
}
#endif

#endif // CH13_HPS_TIMER_H
