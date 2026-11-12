// sw_v3/ch12_driver.c
// HPS C driver for FPGA Praat-style F0 estimation core
// Manages memory-mapped I/O, register transactions, sample streaming,
// cycle counting, and generation of pitch_f0.bin and pitch_meta.txt

#include "ch12_driver.h"
#include "ch01_wav.h"
#include "ch01_frames.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef SIM
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#endif

// ROM C[tau] in unsigned Q2.14 (address = tau - 26, tau = 26..214)
static const uint16_t ROM_C[189] = {
    16563, 16578, 16592, 16608, 16623, 16640, 16657, 16674, 16692, 16711,
    16730, 16750, 16770, 16791, 16812, 16834, 16857, 16880, 16903, 16928,
    16953, 16978, 17004, 17031, 17058, 17086, 17114, 17143, 17173, 17203,
    17234, 17265, 17297, 17330, 17363, 17397, 17432, 17467, 17503, 17540,
    17577, 17615, 17653, 17692, 17732, 17773, 17814, 17856, 17898, 17941,
    17985, 18030, 18075, 18121, 18168, 18215, 18263, 18312, 18362, 18412,
    18463, 18515, 18568, 18621, 18675, 18730, 18786, 18842, 18900, 18958,
    19017, 19076, 19137, 19198, 19260, 19324, 19387, 19452, 19518, 19584,
    19652, 19720, 19789, 19859, 19930, 20002, 20075, 20149, 20224, 20299,
    20376, 20454, 20533, 20612, 20693, 20775, 20857, 20941, 21026, 21112,
    21199, 21287, 21376, 21466, 21558, 21650, 21744, 21839, 21935, 22032,
    22131, 22230, 22331, 22433, 22536, 22641, 22747, 22854, 22962, 23072,
    23183, 23296, 23410, 23525, 23642, 23760, 23879, 24000, 24123, 24247,
    24372, 24499, 24627, 24757, 24889, 25022, 25157, 25294, 25432, 25572,
    25713, 25857, 26002, 26148, 26297, 26447, 26600, 26754, 26910, 27068,
    27227, 27389, 27553, 27719, 27887, 28056, 28228, 28403, 28579, 28757,
    28938, 29121, 29306, 29493, 29683, 29875, 30070, 30267, 30466, 30668,
    30873, 31080, 31289, 31502, 31717, 31934, 32155, 32378, 32604, 32833,
    33065, 33300, 33538, 33778, 34022, 34270, 34520, 34773, 35030
};

// ROM K[tau] in signed 16-bit, scaled by 2^20 (address = tau - 26, tau = 26..214)
static const int16_t ROM_K[189] = {
     -383,   188,   738,  1269,  1782,  2278,  2758,  3224,  3675,  4114,
     4540,  4954,  5358,  5751,  6134,  6507,  6872,  7228,  7576,  7916,
     8248,  8573,  8892,  9204,  9509,  9809, 10103, 10391, 10674, 10951,
    11224, 11492, 11755, 12013, 12268, 12518, 12764, 13006, 13244, 13478,
    13709, 13937, 14161, 14382, 14600, 14814, 15026, 15234, 15440, 15643,
    15844, 16041, 16237, 16429, 16620, 16807, 16993, 17176, 17358, 17537,
    17714, 17888, 18061, 18232, 18401, 18568, 18734, 18897, 19059, 19219,
    19378, 19534, 19690, 19843, 19995, 20146, 20295, 20442, 20589, 20733,
    20877, 21019, 21159, 21299, 21437, 21574, 21710, 21844, 21977, 22109,
    22240, 22370, 22499, 22627, 22753, 22879, 23003, 23127, 23249, 23371,
    23491, 23611, 23730, 23847, 23964, 24080, 24195, 24309, 24423, 24535,
    24647, 24758, 24868, 24977, 25085, 25193, 25300, 25406, 25511, 25616,
    25720, 25823, 25926, 26028, 26129, 26229, 26329, 26429, 26527, 26625,
    26722, 26819, 26915, 27010, 27105, 27200, 27293, 27386, 27479, 27571,
    27662, 27753, 27843, 27933, 28022, 28111, 28199, 28287, 28374, 28461,
    28547, 28633, 28718, 28803, 28887, 28971, 29054, 29137, 29220, 29302,
    29383, 29464, 29545, 29625, 29705, 29784, 29863, 29942, 30020, 30098,
    30175, 30252, 30329, 30405, 30481, 30556, 30631, 30706, 30781, 30855,
    30928, 31001, 31074, 31147, 31219, 31291, 31362, 31434, 31504
};

// Write pitch_f0.bin: array of uint16_t little-endian words (Q12.4 format, 0 = voiceless)
int ch12_write_pitch_bin(const char *path, const uint16_t *f0_words, uint32_t n_frames) {
    if (!path || !f0_words) return -1;
    FILE *f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "Error: Unable to open file for writing: %s\n", path);
        return -2;
    }
    size_t written = fwrite(f0_words, sizeof(uint16_t), n_frames, f);
    fclose(f);
    if (written != n_frames) {
        fprintf(stderr, "Error: Failed to write all %u frames (wrote %zu)\n", n_frames, written);
        return -3;
    }
    return 0;
}

// Write pitch_meta.txt: metadata file containing t1, dt, n_frames, first_win0, global_peak
int ch12_write_pitch_meta(const char *path, double t1, double dt, uint32_t n_frames, int32_t first_win0, uint16_t global_peak) {
    if (!path) return -1;
    FILE *f = fopen(path, "w");
    if (!f) {
        fprintf(stderr, "Error: Unable to open file for writing: %s\n", path);
        return -2;
    }
    fprintf(f, "t1=%.6f\n", t1);
    fprintf(f, "dt=%.6f\n", dt);
    fprintf(f, "n_frames=%u\n", n_frames);
    fprintf(f, "first_win0=%d\n", first_win0);
    fprintf(f, "global_peak=%u\n", global_peak);
    fclose(f);
    return 0;
}

#ifdef SIM
static uint16_t g_hanning_rom[638];
static bool     g_hanning_init = false;

static void init_hanning_table(void) {
    if (g_hanning_init) return;
    double denom = 639.0; // N + 1 = 638 + 1
    for (size_t i = 0; i < 638; i++) {
        double v = 0.5 - 0.5 * cos(2.0 * M_PI * ((double)(i + 1)) / denom);
        int32_t rounded = (int32_t)floor(v * 32768.0 + 0.5);
        if (rounded > 32767) rounded = 32767;
        g_hanning_rom[i] = (uint16_t)rounded;
    }
    g_hanning_init = true;
}

static int16_t sim_local_mean(const int16_t *x) {
    int32_t s = 0;
    for (int j = 106; j <= 531; ++j) {
        s += x[j];
    }
    int64_t biased = (int64_t)s + 213 + (426LL << 15);
    int64_t prod = biased * 10082083LL;
    int32_t mean = (int32_t)((prod >> 32) - (1 << 15));
    return (int16_t)mean;
}

static void sim_hanning_lp(const int16_t *x, int16_t mean, int32_t xw[638], uint16_t *lp) {
    init_hanning_table();
    uint16_t max_lp = 0;
    for (int j = 0; j < 638; ++j) {
        int32_t d = (int32_t)x[j] - (int32_t)mean;
        int64_t p = (int64_t)d * (int64_t)g_hanning_rom[j];
        int32_t val = (int32_t)((p + (1 << 14)) >> 15);
        xw[j] = val;
        if (j >= 212 && j <= 425) {
            uint16_t abs_v = (val < 0) ? (uint16_t)(-val) : (uint16_t)val;
            if (abs_v > max_lp) max_lp = abs_v;
        }
    }
    *lp = max_lp;
}

static void sim_mac(const int32_t xw[638], int64_t *r0, int64_t R[215]) {
    int64_t sum0 = 0;
    for (int j = 0; j < 638; ++j) {
        sum0 += (int64_t)xw[j] * (int64_t)xw[j];
    }
    *r0 = sum0;
    for (int t = 26; t <= 214; ++t) {
        int64_t sum_t = 0;
        for (int j = 0; j < 638 - t; ++j) {
            sum_t += (int64_t)xw[j] * (int64_t)xw[j + t];
        }
        R[t] = sum_t;
    }
}

static int calc_bitlen(int64_t val) {
    if (val <= 0) return 0;
    int len = 0;
    while (val > 0) {
        len++;
        val >>= 1;
    }
    return len;
}

static uint16_t sim_frame(const int16_t *x, uint16_t gp) {
    int16_t mean = sim_local_mean(x);
    int32_t xw[638];
    uint16_t lp = 0;
    sim_hanning_lp(x, mean, xw, &lp);

    int64_t r0 = 0;
    int64_t R[215] = {0};
    sim_mac(xw, &r0, R);

    if (r0 == 0 || lp == 0 || gp == 0) return 0;

    int bl = calc_bitlen(r0);
    int sh = (bl > 26) ? (bl - 26) : 0;
    int32_t r0n = (int32_t)(r0 >> sh);

    int32_t U[215] = {0};
    int32_t Sc[215] = {0};

    for (int t = 26; t <= 214; ++t) {
        int32_t rn = (int32_t)(R[t] >> sh);
        int64_t u_prod = (int64_t)rn * (int64_t)ROM_C[t - 26];
        int32_t u_val = (int32_t)((u_prod + (1 << 13)) >> 14);
        U[t] = u_val;

        int64_t k_prod = (int64_t)r0n * (int64_t)ROM_K[t - 26];
        int32_t k_term = (int32_t)((k_prod + (1 << 19)) >> 20);
        Sc[t] = u_val - k_term;
    }

    int best = 0;
    int32_t bsc = 0;
    bool found = false;

    for (int t = 27; t <= 213; ++t) {
        if (U[t] > U[t - 1] && U[t] >= U[t + 1] && (1000LL * U[t] > 225LL * r0n)) {
            if (!found || Sc[t] > bsc) {
                best = t;
                bsc = Sc[t];
                found = true;
            }
        }
    }

    if (!found || best == 0) return 0;

    int32_t um = U[best - 1];
    int32_t u0 = U[best];
    int32_t up = U[best + 1];

    int32_t num = up - um;
    int32_t den = 2 * u0 - um - up;
    if (den <= 0) return 0;

    int den_bl = calc_bitlen((int64_t)den);
    int s2 = (den_bl > 24) ? (den_bl - 24) : 0;
    int32_t numn = num >> s2;
    int32_t denn = den >> s2;

    int64_t D = 2LL * denn * best + numn;
    if (D <= 0) return 0;

    int64_t f0q = (512000LL * denn + D / 2) / D;

    int64_t term_sc = (100LL * bsc - 45LL * r0n) * 3LL * (int64_t)gp;
    int64_t lp_diff = 6LL * (int64_t)gp - 145LL * (int64_t)lp;
    if (lp_diff < 0) lp_diff = 0;
    int64_t term_rhs = 100LL * (int64_t)r0n * lp_diff;

    bool voiced = (term_sc > term_rhs);
    if (!voiced) return 0;

    if (f0q > 65535) f0q = 65535;
    return (uint16_t)f0q;
}

static void sim_median3(const uint16_t *in, uint16_t *out, uint32_t n) {
    if (n == 0) return;
    if (n == 1) {
        out[0] = in[0];
        return;
    }
    for (uint32_t i = 0; i < n; ++i) {
        uint16_t a = (i == 0) ? in[0] : in[i - 1];
        uint16_t b = in[i];
        uint16_t c = (i == n - 1) ? in[n - 1] : in[i + 1];

        if (a > b) { uint16_t t = a; a = b; b = t; }
        if (b > c) { uint16_t t = b; b = c; c = t; }
        if (a > b) { uint16_t t = a; a = b; b = t; }
        out[i] = b;
    }
}
#endif // SIM

int ch12_run_f0_pipeline(const char *wav_path, const char *out_dir, ch12_pipeline_stats_t *stats) {
    if (!wav_path || !out_dir) return -1;

    wav_file_t wav;
    int ret = wav_read_file(wav_path, &wav);
    if (ret != WAV_SUCCESS) {
        fprintf(stderr, "Error: Failed to read WAV file %s (code %d)\n", wav_path, ret);
        return -2;
    }

    frame_grid_t grid;
    ret = frames_calculate_grid(wav.num_samples, &grid);
    if (ret != 0) {
        fprintf(stderr, "Error: Failed to calculate frame grid (code %d)\n", ret);
        wav_free(&wav);
        return -3;
    }

    uint32_t n_frames = grid.n_frames;
    uint16_t *f0_med = (uint16_t *)malloc(n_frames * sizeof(uint16_t));
    if (!f0_med) {
        frames_free(&grid);
        wav_free(&wav);
        return -4;
    }

    uint32_t total_cycles = 0;
    uint32_t frame_cycles = 0;

#ifdef SIM
    uint16_t *raw_f0 = (uint16_t *)malloc(n_frames * sizeof(uint16_t));
    for (uint32_t f = 0; f < n_frames; ++f) {
        int32_t s0 = grid.window_start0[f];
        raw_f0[f] = sim_frame(&wav.samples[s0], (uint16_t)wav.global_peak);
    }
    sim_median3(raw_f0, f0_med, n_frames);
    free(raw_f0);

    frame_cycles = 99663;
    total_cycles = n_frames * 99663;
#else
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("Error opening /dev/mem");
        free(f0_med);
        frames_free(&grid);
        wav_free(&wav);
        return -5;
    }

    void *virtual_base = mmap(NULL, HW_REGS_SPAN, PROT_READ | PROT_WRITE, MAP_SHARED, fd, ALT_LWFPGASLVS_OFST);
    if (virtual_base == MAP_FAILED) {
        perror("Error mapping memory");
        close(fd);
        free(f0_med);
        frames_free(&grid);
        wav_free(&wav);
        return -6;
    }

    #define HW_READ32(ofst)         (*(volatile uint32_t *)((uint8_t *)(virtual_base) + (ofst)))
    #define HW_WRITE32(ofst, val)   (*(volatile uint32_t *)((uint8_t *)(virtual_base) + (ofst)) = (val))

    HW_WRITE32(CTRL_OFST + REG_CTRL_NFRAMES, n_frames);
    HW_WRITE32(CTRL_OFST + REG_CTRL_FIRST_WIN0, (uint32_t)grid.window_start0[0]);
    HW_WRITE32(CTRL_OFST + REG_CTRL_GLOBAL_PEAK, wav.global_peak);
    HW_WRITE32(CTRL_OFST + REG_CTRL_CONFIG, CONFIG_FIR_BYPASS);

    uint32_t words_to_send = (wav.num_samples + 1) / 2;
    uint32_t words_sent = 0;
    while (words_sent < words_to_send) {
        uint32_t fill_samples = HW_READ32(FIFO_IN_CSR_OFST);
        if (fill_samples <= 480) {
            uint32_t s_idx = words_sent * 2;
            int16_t s0 = wav.samples[s_idx];
            int16_t s1 = (s_idx + 1 < wav.num_samples) ? wav.samples[s_idx + 1] : 0;
            uint32_t word = ((uint32_t)(uint16_t)s0) | (((uint32_t)(uint16_t)s1) << 16);
            HW_WRITE32(FIFO_IN_DATA_OFST, word);
            words_sent++;
        }
    }

    HW_WRITE32(CTRL_OFST + REG_CTRL_START, 0x01);

    uint32_t status = 0;
    uint32_t timeout = 0;
    while (!(status & STATUS_DONE) && timeout < 10000000) {
        status = HW_READ32(CTRL_OFST + REG_CTRL_STATUS);
        timeout++;
    }

    if (!(status & STATUS_DONE)) {
        fprintf(stderr, "Error: Hardware F0 core processing timed out! status = 0x%08x\n", status);
    } else {
        total_cycles = HW_READ32(CTRL_OFST + REG_CTRL_TOTAL_CYCLES);
        frame_cycles = HW_READ32(CTRL_OFST + REG_CTRL_FRAME_CYCLES);
    }

    for (uint32_t f = 0; f < n_frames; ++f) {
        uint32_t val32 = HW_READ32(FIFO_OUT_DATA_OFST);
        f0_med[f] = (uint16_t)(val32 & 0xFFFF);
    }

    munmap(virtual_base, HW_REGS_SPAN);
    close(fd);
#endif

    char bin_path[1024];
    char meta_path[1024];
    snprintf(bin_path, sizeof(bin_path), "%s/pitch_f0.bin", out_dir);
    snprintf(meta_path, sizeof(meta_path), "%s/pitch_meta.txt", out_dir);

    ch12_write_pitch_bin(bin_path, f0_med, n_frames);
    ch12_write_pitch_meta(meta_path, grid.t1, grid.dt, n_frames, grid.window_start0[0], (uint16_t)wav.global_peak);

    if (stats) {
        stats->n_frames = n_frames;
        stats->t1 = grid.t1;
        stats->dt = grid.dt;
        stats->first_win0 = grid.window_start0[0];
        stats->global_peak = (uint16_t)wav.global_peak;
        stats->total_cycles = total_cycles;
        stats->frame_cycles = frame_cycles;
    }

    free(f0_med);
    frames_free(&grid);
    wav_free(&wav);
    return 0;
}
