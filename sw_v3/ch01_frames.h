#ifndef CH01_FRAMES_H
#define CH01_FRAMES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t n_frames;
    double t1;
    double dt;
    int32_t *window_start0; // 0-based index of first sample of each 638-sample window
    int32_t *left_samples;   // 1-based leftSample index from Praat
    int hop_regular;         // 1 if all hops are exactly 160 samples, 0 otherwise
} frame_grid_t;

// Computes Praat's frame grid in IEEE double precision, identical to
// Sampled_shortTermAnalysis and Sampled_xToLowIndex in Praat 7.0.03.
int frames_calculate_grid(uint32_t nx, frame_grid_t *grid);

// Frees dynamically allocated memory in frame_grid_t
void frames_free(frame_grid_t *grid);

#ifdef __cplusplus
}
#endif

#endif // CH01_FRAMES_H
