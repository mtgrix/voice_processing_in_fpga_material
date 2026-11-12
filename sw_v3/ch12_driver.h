#ifndef SW_V3_CH12_DRIVER_H
#define SW_V3_CH12_DRIVER_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Physical memory mapping constants for DE10-Standard (Cyclone V SoC)
#define ALT_LWFPGASLVS_OFST      0xFF200000
#define HW_REGS_SPAN             0x00200000 // 2 MB window

// IP Slaves Base Offsets within Lightweight Bridge
#define FIFO_IN_DATA_OFST        0x00000000 // Avalon-MM 32-bit write slave
#define FIFO_IN_CSR_OFST         0x00000020 // On-Chip FIFO in_csr
#define CTRL_OFST                0x00000040 // F0 Processing Core CSR
#define FIFO_OUT_DATA_OFST       0x00000080 // Avalon-MM read slave for F0
#define FIFO_OUT_CSR_OFST        0x000000A0 // Output FIFO csr

// Control registers within CTRL_OFST
#define REG_CTRL_START           0x00
#define REG_CTRL_NFRAMES         0x04
#define REG_CTRL_FIRST_WIN0      0x08
#define REG_CTRL_GLOBAL_PEAK     0x0C
#define REG_CTRL_CONFIG          0x10
#define REG_CTRL_STATUS          0x14
#define REG_CTRL_TOTAL_CYCLES    0x18
#define REG_CTRL_FRAME_CYCLES    0x1C

// Status bits
#define STATUS_BUSY              (1 << 0)
#define STATUS_DONE              (1 << 1)
#define STATUS_FIFO_IN_OVF       (1 << 2)
#define STATUS_FIFO_OUT_OVF      (1 << 3)

// Pipeline configuration bits
#define CONFIG_FIR_BYPASS        (1 << 0)
#define CONFIG_DC_BLOCKER_EN     (1 << 1)

typedef struct {
    uint32_t n_frames;
    double   t1;
    double   dt;
    int32_t  first_win0;
    uint16_t global_peak;
    uint32_t total_cycles;
    uint32_t frame_cycles;
} ch12_pipeline_stats_t;

// API functions
int ch12_write_pitch_bin(const char *path, const uint16_t *f0_words, uint32_t n_frames);
int ch12_write_pitch_meta(const char *path, double t1, double dt, uint32_t n_frames, int32_t first_win0, uint16_t global_peak);
int ch12_run_f0_pipeline(const char *wav_path, const char *out_dir, ch12_pipeline_stats_t *stats);

#ifdef __cplusplus
}
#endif

#endif // SW_V3_CH12_DRIVER_H
