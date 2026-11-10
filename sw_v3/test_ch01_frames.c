#include "ch01_frames.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <num_samples>\n", argv[0]);
        return 1;
    }
    uint32_t nx = (uint32_t)atoi(argv[1]);
    frame_grid_t grid;
    int ret = frames_calculate_grid(nx, &grid);
    printf("NX: %u\n", nx);
    printf("RETURN_CODE: %d\n", ret);
    if (ret == 0) {
        printf("NFRAMES: %u\n", grid.n_frames);
        printf("T1: %.6f\n", grid.t1);
        printf("DT: %.6f\n", grid.dt);
        printf("HOP_REGULAR: %d\n", grid.hop_regular);
        printf("FIRST_WIN0: %d\n", grid.window_start0[0]);
        printf("LAST_WIN0: %d\n", grid.window_start0[grid.n_frames - 1]);
        if (grid.n_frames >= 4) {
            printf("FIRST_4_WIN0: %d %d %d %d\n",
                   grid.window_start0[0], grid.window_start0[1],
                   grid.window_start0[2], grid.window_start0[3]);
        }
        frames_free(&grid);
    }
    return 0;
}
