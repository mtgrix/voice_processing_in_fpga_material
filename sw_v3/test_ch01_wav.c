#include "ch01_wav.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <wav_file>\n", argv[0]);
        return 1;
    }
    const char *path = argv[1];
    wav_file_t wav;
    int ret = wav_read_file(path, &wav);
    printf("FILE: %s\n", path);
    printf("RETURN_CODE: %d\n", ret);
    if (ret == WAV_SUCCESS) {
        printf("NUM_SAMPLES: %u\n", wav.num_samples);
        printf("SAMPLE_RATE: %u\n", wav.sample_rate);
        printf("NUM_CHANNELS: %u\n", wav.num_channels);
        printf("BITS_PER_SAMPLE: %u\n", wav.bits_per_sample);
        printf("GLOBAL_PEAK: %u\n", wav.global_peak);
        if (wav.num_samples >= 8) {
            printf("FIRST_8_SAMPLES: %d %d %d %d %d %d %d %d\n",
                   wav.samples[0], wav.samples[1], wav.samples[2], wav.samples[3],
                   wav.samples[4], wav.samples[5], wav.samples[6], wav.samples[7]);
        }
        wav_free(&wav);
    }
    return 0;
}
