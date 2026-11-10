#ifndef CH01_WAV_H
#define CH01_WAV_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Error codes for WAV parsing
#define WAV_SUCCESS                  0
#define WAV_ERR_OPEN                -1
#define WAV_ERR_NOT_RIFF            -2
#define WAV_ERR_NOT_WAVE            -3
#define WAV_ERR_NO_FMT              -4
#define WAV_ERR_UNSUPPORTED_FORMAT  -5  // Must be PCM (format tag 1)
#define WAV_ERR_UNSUPPORTED_CHANNELS -6 // Must be 1 channel (mono)
#define WAV_ERR_UNSUPPORTED_RATE    -7  // Must be 16000 Hz
#define WAV_ERR_UNSUPPORTED_BITS    -8  // Must be 16-bit
#define WAV_ERR_NO_DATA             -9
#define WAV_ERR_TRUNCATED           -10
#define WAV_ERR_MALLOC              -11

typedef struct {
    int16_t *samples;
    uint32_t num_samples;
    uint32_t sample_rate;
    uint16_t num_channels;
    uint16_t bits_per_sample;
    uint32_t global_peak;   // GP = round(max |n*x - sum(x)| / n)
} wav_file_t;

// Parses a WAV file from disk, performs RIFF/WAVE chunk parsing,
// validates 16 kHz mono 16-bit PCM, and computes integer globalPeak.
int wav_read_file(const char *filename, wav_file_t *wav);

// Computes Praat-compatible integer globalPeak:
// GP = round(max |n * x[i] - sum(x)| / n)
uint32_t wav_compute_global_peak(const int16_t *samples, uint32_t n);

// Frees dynamically allocated memory in wav_file_t
void wav_free(wav_file_t *wav);

#ifdef __cplusplus
}
#endif

#endif // CH01_WAV_H
