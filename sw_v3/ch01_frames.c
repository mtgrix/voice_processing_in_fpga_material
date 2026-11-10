#include "ch01_frames.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define FS_FS 16000.0
#define DX_DX (1.0 / FS_FS)
#define X1_X1 (0.5 * DX_DX)
#define DT_WINDOW 0.04
#define TIME_STEP 0.01
#define HALFNSAMP_WINDOW 319

int frames_calculate_grid(uint32_t nx, frame_grid_t *grid) {
    if (grid == NULL) return -1;
    grid->n_frames = 0;
    grid->t1 = 0.0;
    grid->dt = TIME_STEP;
    grid->window_start0 = NULL;
    grid->left_samples = NULL;
    grid->hop_regular = 1;

    double my_duration = DX_DX * (double)nx;
    if (my_duration < DT_WINDOW) {
        return -2; // Audio shorter than one analysis window (40 ms)
    }

    double nframes_d = floor((my_duration - DT_WINDOW) / TIME_STEP) + 1.0;
    uint32_t nframes = (uint32_t)nframes_d;
    if (nframes == 0) {
        return -2;
    }

    // Centering calculation from Sampled_shortTermAnalysis
    double our_mid = X1_X1 - 0.5 * DX_DX + 0.5 * my_duration;
    double thy_duration = (double)nframes * TIME_STEP;
    double t1 = our_mid - 0.5 * thy_duration + 0.5 * TIME_STEP;

    grid->window_start0 = (int32_t *)malloc(nframes * sizeof(int32_t));
    grid->left_samples  = (int32_t *)malloc(nframes * sizeof(int32_t));
    if (!grid->window_start0 || !grid->left_samples) {
        frames_free(grid);
        return -3;
    }

    grid->n_frames = nframes;
    grid->t1 = t1;

    for (uint32_t i = 1; i <= nframes; i++) {
        double t = t1 + (double)(i - 1) * TIME_STEP;
        // Sampled_xToLowIndex: floor((t - x1) / dx + 1.0)
        double left_d = floor((t - X1_X1) / DX_DX + 1.0);
        int32_t left = (int32_t)left_d;
        int32_t right = left + 1;
        int32_t win0 = right - HALFNSAMP_WINDOW - 1;

        grid->left_samples[i - 1] = left;
        grid->window_start0[i - 1] = win0;

        if (i > 1) {
            int32_t hop = grid->window_start0[i - 1] - grid->window_start0[i - 2];
            if (hop != 160) {
                grid->hop_regular = 0;
            }
        }
    }

    return 0;
}

void frames_free(frame_grid_t *grid) {
    if (grid) {
        if (grid->window_start0) {
            free(grid->window_start0);
            grid->window_start0 = NULL;
        }
        if (grid->left_samples) {
            free(grid->left_samples);
            grid->left_samples = NULL;
        }
        grid->n_frames = 0;
    }
}
