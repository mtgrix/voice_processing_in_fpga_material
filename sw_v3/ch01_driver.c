#include "ch01_wav.h"
#include "ch01_frames.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifndef SIM
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#endif

// Physical Memory Mapping constants for DE10-Standard (Cyclone V SoC)
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

#ifdef SIM
// Software mock state for simulation / verification without physical board
typedef struct {
    uint32_t fifo_in_mem[512];
    uint32_t fifo_in_wr;
    uint32_t fifo_in_rd;
    uint32_t ctrl_regs[8];
    uint16_t fifo_out_mem[1024];
    uint32_t fifo_out_wr;
    uint32_t fifo_out_rd;
} mock_hardware_t;

static mock_hardware_t g_mock;

static void mock_hw_init(void) {
    memset(&g_mock, 0, sizeof(mock_hardware_t));
}

static uint32_t mock_read32(uint32_t offset) {
    if (offset == FIFO_IN_CSR_OFST) {
        // Return samples in input FIFO
        uint32_t words = (g_mock.fifo_in_wr - g_mock.fifo_in_rd) & 0x1FF;
        return words * 2;
    } else if (offset == FIFO_OUT_CSR_OFST) {
        // Return words in output FIFO
        return (g_mock.fifo_out_wr - g_mock.fifo_out_rd) & 0x3FF;
    } else if (offset >= CTRL_OFST && offset < CTRL_OFST + 0x20) {
        uint32_t idx = (offset - CTRL_OFST) / 4;
        return g_mock.ctrl_regs[idx];
    } else if (offset == FIFO_OUT_DATA_OFST) {
        if (g_mock.fifo_out_rd < g_mock.fifo_out_wr) {
            uint16_t v = g_mock.fifo_out_mem[g_mock.fifo_out_rd++];
            return (uint32_t)v;
        }
        return 0;
    }
    return 0;
}

static void mock_write32(uint32_t offset, uint32_t val) {
    if (offset == FIFO_IN_DATA_OFST) {
        g_mock.fifo_in_mem[g_mock.fifo_in_wr++ & 0x1FF] = val;
        // Simulate core consuming samples in streaming fashion so FIFO does not stall
        if (g_mock.fifo_in_wr - g_mock.fifo_in_rd >= 200) {
            g_mock.fifo_in_rd += 100;
        }
    } else if (offset >= CTRL_OFST && offset < CTRL_OFST + 0x20) {
        uint32_t idx = (offset - CTRL_OFST) / 4;
        g_mock.ctrl_regs[idx] = val;
        if (idx == 0 && (val & 1)) {
            // Start triggered: simulate execution
            uint32_t nframes = g_mock.ctrl_regs[1];
            // Produce mock F0 Q12.4 results (e.g. 150 Hz = 2400 in Q12.4)
            for (uint32_t f = 0; f < nframes; f++) {
                g_mock.fifo_out_mem[g_mock.fifo_out_wr++] = 2400;
            }
            g_mock.ctrl_regs[5] = STATUS_DONE; // status done
            g_mock.ctrl_regs[6] = nframes * 98543; // total cycles
            g_mock.ctrl_regs[7] = 98543; // frame cycles
        }
    }
}

#define HW_READ32(base, ofst)         mock_read32(ofst)
#define HW_WRITE32(base, ofst, val)   mock_write32(ofst, val)

#else

// Real hardware access via mmap on /dev/mem
#define HW_READ32(base, ofst)         (*(volatile uint32_t *)((uint8_t *)(base) + (ofst)))
#define HW_WRITE32(base, ofst, val)   (*(volatile uint32_t *)((uint8_t *)(base) + (ofst)) = (val))

#endif

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <wav_file> [out_dir]\n", argv[0]);
        return 1;
    }
    const char *wav_path = argv[1];
    const char *out_dir = (argc >= 3) ? argv[2] : ".";

    printf("=== HPS F0 PROCESSING DRIVER ===\n");
    printf("Loading WAV: %s\n", wav_path);

    // 1. Read and parse WAV
    wav_file_t wav;
    int ret = wav_read_file(wav_path, &wav);
    if (ret != WAV_SUCCESS) {
        printf("Error: Failed to read WAV file (code %d)\n", ret);
        return 1;
    }
    printf("WAV loaded successfully:\n");
    printf("  Samples:    %u (%.3f s)\n", wav.num_samples, (double)wav.num_samples / 16000.0);
    printf("  Rate:       %u Hz, Channels: %u, Bits: %u\n", wav.sample_rate, wav.num_channels, wav.bits_per_sample);
    printf("  globalPeak: %u (amplitude)\n", wav.global_peak);

    // 2. Compute Praat frame grid
    frame_grid_t grid;
    ret = frames_calculate_grid(wav.num_samples, &grid);
    if (ret != 0) {
        printf("Error: Failed to calculate frame grid (code %d)\n", ret);
        wav_free(&wav);
        return 1;
    }
    printf("Frame Grid calculated:\n");
    printf("  n_frames:   %u\n", grid.n_frames);
    printf("  t1:         %.6f s\n", grid.t1);
    printf("  first_win0: %d\n", grid.window_start0[0]);
    printf("  hop_regular:%d\n", grid.hop_regular);

    // 3. Hardware / Bridge mapping
    void *virtual_base = NULL;
#ifndef SIM
    int fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (fd < 0) {
        perror("Error: Cannot open /dev/mem");
        frames_free(&grid);
        wav_free(&wav);
        return 1;
    }
    virtual_base = mmap(NULL, HW_REGS_SPAN, PROT_READ | PROT_WRITE, MAP_SHARED, fd, ALT_LWFPGASLVS_OFST);
    if (virtual_base == MAP_FAILED) {
        perror("Error: mmap failed");
        close(fd);
        frames_free(&grid);
        wav_free(&wav);
        return 1;
    }
#else
    mock_hw_init();
    printf("Simulation mode (-DSIM) active: using software mock memory.\n");
#endif

    // 4. Configure core registers via CTRL_OFST
    HW_WRITE32(virtual_base, CTRL_OFST + REG_CTRL_NFRAMES, grid.n_frames);
    HW_WRITE32(virtual_base, CTRL_OFST + REG_CTRL_FIRST_WIN0, (uint32_t)grid.window_start0[0]);
    HW_WRITE32(virtual_base, CTRL_OFST + REG_CTRL_GLOBAL_PEAK, wav.global_peak);
    HW_WRITE32(virtual_base, CTRL_OFST + REG_CTRL_CONFIG, 0x01); // bit 0: fir_bypass = 1 (match Praat)

    // 5. Stream audio samples to FIFO_IN with fill-level polling
    printf("Streaming %u samples (packing 2 samples per 32-bit word)...\n", wav.num_samples);
    uint32_t words_to_send = (wav.num_samples + 1) / 2;
    uint32_t words_sent = 0;

    while (words_sent < words_to_send) {
        // Poll fill level (in 16-bit samples)
        uint32_t fill_samples = HW_READ32(virtual_base, FIFO_IN_CSR_OFST);
        if (fill_samples <= 480) { // Capacity is 512 samples
            uint32_t s_idx = words_sent * 2;
            int16_t s0 = wav.samples[s_idx];
            int16_t s1 = (s_idx + 1 < wav.num_samples) ? wav.samples[s_idx + 1] : 0;
            uint32_t word = ((uint32_t)(uint16_t)s0) | (((uint32_t)(uint16_t)s1) << 16);

            HW_WRITE32(virtual_base, FIFO_IN_DATA_OFST, word);
            words_sent++;
        }
    }
    printf("Sent %u 32-bit words (%u samples).\n", words_sent, words_sent * 2);

    // 6. Assert START
    printf("Triggering FPGA processing START...\n");
    HW_WRITE32(virtual_base, CTRL_OFST + REG_CTRL_START, 0x01);

    // 7. Poll STATUS for DONE
    printf("Polling STATUS for completion...\n");
    uint32_t status = 0;
    int timeout = 0;
    while (!(status & STATUS_DONE) && timeout < 1000000) {
        status = HW_READ32(virtual_base, CTRL_OFST + REG_CTRL_STATUS);
        timeout++;
    }

    if (!(status & STATUS_DONE)) {
        printf("Error: FPGA processing timed out! Status = 0x%08x\n", status);
    } else {
        uint32_t total_cycles = HW_READ32(virtual_base, CTRL_OFST + REG_CTRL_TOTAL_CYCLES);
        uint32_t frame_cycles = HW_READ32(virtual_base, CTRL_OFST + REG_CTRL_FRAME_CYCLES);
        printf("FPGA Processing COMPLETE!\n");
        printf("  Total FPGA cycles: %u\n", total_cycles);
        printf("  Cycles/frame:      %u\n", frame_cycles);
    }

    // 8. Read F0 results from FIFO_OUT
    char bin_path[512];
    char meta_path[512];
    snprintf(bin_path, sizeof(bin_path), "%s/pitch_f0.bin", out_dir);
    snprintf(meta_path, sizeof(meta_path), "%s/pitch_meta.txt", out_dir);

    FILE *f_bin = fopen(bin_path, "wb");
    if (!f_bin) {
        printf("Error: Cannot open %s for writing\n", bin_path);
    } else {
        for (uint32_t f = 0; f < grid.n_frames; f++) {
            uint32_t val32 = HW_READ32(virtual_base, FIFO_OUT_DATA_OFST);
            uint16_t f0_q12_4 = (uint16_t)(val32 & 0xFFFF);
            fwrite(&f0_q12_4, sizeof(uint16_t), 1, f_bin);
        }
        fclose(f_bin);
        printf("Saved %u F0 words to %s\n", grid.n_frames, bin_path);
    }

    FILE *f_meta = fopen(meta_path, "w");
    if (f_meta) {
        fprintf(f_meta, "t1=%.6f\n", grid.t1);
        fprintf(f_meta, "dt=%.6f\n", grid.dt);
        fprintf(f_meta, "n_frames=%u\n", grid.n_frames);
        fprintf(f_meta, "first_win0=%d\n", grid.window_start0[0]);
        fprintf(f_meta, "global_peak=%u\n", wav.global_peak);
        fclose(f_meta);
        printf("Saved metadata to %s\n", meta_path);
    }

    // Clean up
#ifndef SIM
    munmap(virtual_base, HW_REGS_SPAN);
    close(fd);
#endif
    frames_free(&grid);
    wav_free(&wav);

    printf("=== DRIVER FINISHED SUCCESSFULLY ===\n");
    return 0;
}
