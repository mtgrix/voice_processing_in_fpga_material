#include "ch01_wav.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

uint32_t wav_compute_global_peak(const int16_t *samples, uint32_t n) {
    if (n == 0 || samples == NULL) {
        return 0;
    }
    int64_t sum = 0;
    int16_t min_v = samples[0];
    int16_t max_v = samples[0];

    for (uint32_t i = 0; i < n; i++) {
        int16_t v = samples[i];
        sum += v;
        if (v < min_v) min_v = v;
        if (v > max_v) max_v = v;
    }

    // Praat: globalPeak = max |x - mean|
    // In integer arithmetic without loss of precision:
    // n * (x - mean) = n * x - sum
    // max |n * x - sum| can only occur at x = min_v or x = max_v!
    int64_t diff1 = (int64_t)n * (int64_t)max_v - sum;
    if (diff1 < 0) diff1 = -diff1;

    int64_t diff2 = (int64_t)n * (int64_t)min_v - sum;
    if (diff2 < 0) diff2 = -diff2;

    int64_t max_diff = (diff1 > diff2) ? diff1 : diff2;

    // Rounding: (max_diff + n / 2) / n
    uint32_t gp = (uint32_t)((max_diff + (int64_t)(n / 2)) / (int64_t)n);
    return gp;
}

int wav_read_file(const char *filename, wav_file_t *wav) {
    if (wav == NULL || filename == NULL) {
        return WAV_ERR_OPEN;
    }
    memset(wav, 0, sizeof(wav_file_t));

    FILE *f = fopen(filename, "rb");
    if (!f) {
        return WAV_ERR_OPEN;
    }

    // Read 12-byte RIFF header
    uint8_t header[12];
    if (fread(header, 1, 12, f) != 12) {
        fclose(f);
        return WAV_ERR_NOT_RIFF;
    }

    if (memcmp(header, "RIFF", 4) != 0) {
        fclose(f);
        return WAV_ERR_NOT_RIFF;
    }

    if (memcmp(header + 8, "WAVE", 4) != 0) {
        fclose(f);
        return WAV_ERR_NOT_WAVE;
    }

    int fmt_found = 0;
    int data_found = 0;

    // Chunk iteration
    while (!data_found) {
        uint8_t chunk_hdr[8];
        size_t nread = fread(chunk_hdr, 1, 8, f);
        if (nread == 0) {
            break; // EOF
        }
        if (nread < 8) {
            fclose(f);
            wav_free(wav);
            return WAV_ERR_TRUNCATED;
        }

        uint32_t chunk_size = (uint32_t)chunk_hdr[4] |
                              ((uint32_t)chunk_hdr[5] << 8) |
                              ((uint32_t)chunk_hdr[6] << 16) |
                              ((uint32_t)chunk_hdr[7] << 24);

        if (memcmp(chunk_hdr, "fmt ", 4) == 0) {
            if (chunk_size < 16) {
                fclose(f);
                return WAV_ERR_NO_FMT;
            }
            uint8_t fmt_buf[16];
            if (fread(fmt_buf, 1, 16, f) != 16) {
                fclose(f);
                return WAV_ERR_TRUNCATED;
            }

            uint16_t audio_format = (uint16_t)(fmt_buf[0] | (fmt_buf[1] << 8));
            uint16_t num_channels = (uint16_t)(fmt_buf[2] | (fmt_buf[3] << 8));
            uint32_t sample_rate  = (uint32_t)(fmt_buf[4] | (fmt_buf[5] << 8) |
                                              (fmt_buf[6] << 16) | (fmt_buf[7] << 24));
            uint16_t bits_per_samp = (uint16_t)(fmt_buf[14] | (fmt_buf[15] << 8));

            if (audio_format != 1) { // 1 = PCM
                fclose(f);
                return WAV_ERR_UNSUPPORTED_FORMAT;
            }
            if (num_channels != 1) { // Mono only
                fclose(f);
                return WAV_ERR_UNSUPPORTED_CHANNELS;
            }
            if (sample_rate != 16000) { // 16 kHz only
                fclose(f);
                return WAV_ERR_UNSUPPORTED_RATE;
            }
            if (bits_per_samp != 16) { // 16-bit only
                fclose(f);
                return WAV_ERR_UNSUPPORTED_BITS;
            }

            wav->sample_rate = sample_rate;
            wav->num_channels = num_channels;
            wav->bits_per_sample = bits_per_samp;
            fmt_found = 1;

            // Skip any remainder of fmt chunk if size > 16
            if (chunk_size > 16) {
                if (fseek(f, chunk_size - 16, SEEK_CUR) != 0) {
                    fclose(f);
                    return WAV_ERR_TRUNCATED;
                }
            }
        } else if (memcmp(chunk_hdr, "data", 4) == 0) {
            if (!fmt_found) {
                fclose(f);
                return WAV_ERR_NO_FMT;
            }
            if (chunk_size % 2 != 0) {
                // Audio data size must be multiple of 2 bytes for 16-bit mono
                chunk_size -= (chunk_size % 2);
            }
            uint32_t n_samples = chunk_size / 2;
            wav->samples = (int16_t *)malloc(chunk_size);
            if (!wav->samples) {
                fclose(f);
                return WAV_ERR_MALLOC;
            }

            size_t bytes_read = fread(wav->samples, 1, chunk_size, f);
            if (bytes_read < chunk_size) {
                fclose(f);
                wav_free(wav);
                return WAV_ERR_TRUNCATED;
            }

            wav->num_samples = n_samples;
            wav->global_peak = wav_compute_global_peak(wav->samples, n_samples);
            data_found = 1;
        } else {
            // Skip auxiliary chunk (LIST, JUNK, bext, etc.)
            if (fseek(f, chunk_size, SEEK_CUR) != 0) {
                fclose(f);
                return WAV_ERR_TRUNCATED;
            }
        }

        // RIFF word alignment: if chunk_size is odd, a pad byte follows
        if (chunk_size & 1) {
            if (fseek(f, 1, SEEK_CUR) != 0) {
                // If EOF at pad byte, break cleanly
                break;
            }
        }
    }

    fclose(f);

    if (!data_found) {
        return WAV_ERR_NO_DATA;
    }

    return WAV_SUCCESS;
}

void wav_free(wav_file_t *wav) {
    if (wav) {
        if (wav->samples) {
            free(wav->samples);
            wav->samples = NULL;
        }
        wav->num_samples = 0;
    }
}
