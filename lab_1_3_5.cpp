#define _USE_MATH_DEFINES
#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <fstream>
#include <string>
#include <algorithm>
#include <array>
#include <numbers>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ============================================================================
// Hằng số phần cứng FPGA DE10-Standard (fs = 16 kHz)
// ============================================================================
constexpr int FS_HZ = 16000;
constexpr int FRAME_LEN = 640;      // 40 ms
constexpr int HOP_LEN = 160;        // 10 ms
constexpr int TAU_SCAN_MIN = 26;    // Dải quét mở rộng [26, 214] (189 lag)
constexpr int TAU_SCAN_MAX = 214;
constexpr int TAU_MIN = 27;         // Dải tìm kiếm đỉnh [27, 213] (187 lag)
constexpr int TAU_MAX = 213;
constexpr int N_SCAN_LAGS = TAU_SCAN_MAX - TAU_SCAN_MIN + 1; // 189
constexpr int64_t Q15 = 1LL << 15;  // 32768
constexpr int64_t Q13 = 1LL << 13;  // 8192

// ============================================================================
// Bẫy 1: Hàm chia sàn số nguyên có dấu (Floor Division s64)
// C++ / cắt về 0 (truncation towards zero), Python // làm tròn về -infinity.
// ============================================================================
inline int64_t div_floor_s64(int64_t a, int64_t b) {
    int64_t q = a / b;
    int64_t r = a % b;
    if (r != 0 && ((r < 0) ^ (b < 0))) {
        q -= 1;
    }
    return q;
}

// ============================================================================
// Cấu trúc kết quả khung cao độ
// ============================================================================
struct FrameResultCpp {
    double f0_hz;
    int tau_star;
    bool voiced;
    int f0_q12_4;
};

// ============================================================================
// Bảng tra ROM phần cứng (Hanning Q1.15 và Scoring C[tau] Q3.13)
// ============================================================================
class FpgaPitchRoms {
public:
    std::array<int64_t, FRAME_LEN> hanning_q15;
    std::array<int64_t, N_SCAN_LAGS> scoring_q13;
    std::array<int64_t, TAU_MAX - TAU_MIN + 1> f0_lut_q12_4;

    FpgaPitchRoms(double octave_cost = 0.01) {
        // Khởi tạo ROM Hanning 640 mẫu
        std::vector<double> w_flt(FRAME_LEN);
        for (int i = 1; i <= FRAME_LEN; ++i) {
            double val = 0.5 - 0.5 * std::cos(2.0 * M_PI * static_cast<double>(i) / 641.0);
            w_flt[i - 1] = val;
            int64_t q = static_cast<int64_t>(std::round(val * 32768.0));
            hanning_q15[i - 1] = std::clamp<int64_t>(q, 0, 32767);
        }

        // Tự tương quan Hanning rw0
        double rw0 = 0.0;
        for (double val : w_flt) rw0 += val * val;

        // Bẫy 4: Lũy thừa 2^(-cost * log2(...)) dùng std::pow, không dùng toán tử ^
        for (int tau = TAU_SCAN_MIN; tau <= TAU_SCAN_MAX; ++tau) {
            double rw_tau = 0.0;
            for (int n = 0; n < FRAME_LEN - tau; ++n) {
                rw_tau += w_flt[n] * w_flt[n + tau];
            }
            double f_cand = 16000.0 / static_cast<double>(tau);
            double bias = std::pow(2.0, -octave_cost * std::log2(600.0 / f_cand));
            double c_val = (rw0 / rw_tau) * bias;
            scoring_q13[tau - TAU_SCAN_MIN] = static_cast<int64_t>(std::round(c_val * 8192.0));
        }

        // Bảng tra F0 Chế độ A (187 mục cho tau = 27..213)
        for (int tau = TAU_MIN; tau <= TAU_MAX; ++tau) {
            double f0 = 16000.0 / static_cast<double>(tau);
            f0_lut_q12_4[tau - TAU_MIN] = static_cast<int64_t>(std::round(f0 * 16.0));
        }
    }
};

// ============================================================================
// Hàm nhân cửa sổ Hanning Q1.15 (+16384 >> 15)
// ============================================================================
inline void window_frame_q15_cpp(const int64_t* x_zm, const int64_t* hanning_rom, int64_t* xw) {
    for (int n = 0; n < FRAME_LEN; ++n) {
        xw[n] = ((x_zm[n] * hanning_rom[n]) + 16384LL) >> 15;
    }
}

// ============================================================================
// Hàm lọc trung vị 3 điểm (Median-3 Filter)
// ============================================================================
inline std::vector<int> median3_cpp(const std::vector<int>& seq) {
    int n = static_cast<int>(seq.size());
    std::vector<int> out(n);
    for (int i = 0; i < n; ++i) {
        int a = seq[std::max(0, i - 1)];
        int b = seq[i];
        int c = seq[std::min(n - 1, i + 1)];
        // Tìm trung vị của 3 số
        if ((a <= b && b <= c) || (c <= b && b <= a)) out[i] = b;
        else if ((b <= a && a <= c) || (c <= a && a <= b)) out[i] = a;
        else out[i] = c;
    }
    return out;
}

// ============================================================================
// Nội suy Parabol 3 điểm số nguyên (Mode B)
// ============================================================================
inline std::pair<int64_t, int> parabolic_interpolation_fixed_cpp(
    const int64_t* scores, int best_idx, int tau_star)
{
    int64_t sm1 = scores[best_idx - 1];
    int64_t s0  = scores[best_idx];
    int64_t sp1 = scores[best_idx + 1];

    int64_t N = sm1 - sp1;
    int64_t D = 2LL * (sm1 - 2LL * s0 + sp1);

    int64_t tau_fine_q16;
    if (D == 0) {
        tau_fine_q16 = static_cast<int64_t>(tau_star) << 16;
    } else {
        // Bẫy 1 & Bẫy 3: Dùng div_floor_s64 và nhân hằng số LL thay vì dịch trái số âm
        tau_fine_q16 = (static_cast<int64_t>(tau_star) << 16) + div_floor_s64(N * 65536LL, D);
    }

    if (tau_fine_q16 <= 0) return {tau_fine_q16, 0};

    // Bẫy 2: 16000LL * 16LL * 65536LL = 16.777.216.000 (vượt giới hạn int32 2^31-1)
    int64_t num = 16000LL * 16LL * 65536LL + (tau_fine_q16 >> 1);
    int f0_q12_4 = static_cast<int>(div_floor_s64(num, tau_fine_q16));
    return {tau_fine_q16, f0_q12_4};
}

// ============================================================================
// Xử lý cao độ 1 khung 640 mẫu bằng số nguyên thuần túy (Fixed-Point Frame)
// ============================================================================
FrameResultCpp fixed_pitch_frame_cpp(
    const int64_t* x_q15,
    int64_t ref_energy,
    bool use_interpolation,
    const FpgaPitchRoms& roms)
{
    // Bước 1: Khử DC trên 640 mẫu
    int64_t sum_x = 0;
    for (int n = 0; n < FRAME_LEN; ++n) sum_x += x_q15[n];
    int64_t mean_x = div_floor_s64(sum_x + 320LL, 640LL);

    int64_t x_zm[FRAME_LEN];
    for (int n = 0; n < FRAME_LEN; ++n) x_zm[n] = x_q15[n] - mean_x;

    // Pha 1a: Nhân cửa sổ Hanning Q1.15
    int64_t xw[FRAME_LEN];
    window_frame_q15_cpp(x_zm, roms.hanning_q15.data(), xw);

    // Pha 1b: Năng lượng khung R_x[0] (tích lũy 41-bit có dấu)
    int64_t r0 = 0;
    for (int n = 0; n < FRAME_LEN; ++n) r0 += xw[n] * xw[n];

    // Cổng khoảng lặng (Silence Gate): r0 * 10000 < 9 * ref_energy
    // Bẫy 2: Dùng __int128_t để triệt tiêu nguy cơ tràn số
    if (ref_energy > 0) {
        if (static_cast<__int128>(r0) * 10000 < static_cast<__int128>(9) * ref_energy) {
            return {0.0, 0, false, 0};
        }
    }
    if (r0 == 0) return {0.0, 0, false, 0};

    // Pha 2: Quét tự tương quan 189 lag & nhân bảng tra ROM C[tau]
    int64_t scores[N_SCAN_LAGS];
    for (int idx = 0; idx < N_SCAN_LAGS; ++idx) {
        int tau = TAU_SCAN_MIN + idx;
        int n_len = FRAME_LEN - tau;
        int64_t r_tau = 0;
        for (int n = 0; n < n_len; ++n) {
            r_tau += xw[n] * xw[n + tau];
        }
        // Tích R_x * C <= 56-bit, S[tau] <= 43-bit có dấu
        scores[idx] = (r_tau * roms.scoring_q13[idx] + 4096LL) >> 13;
    }

    // Tìm cực đại trong dải [TAU_MIN, TAU_MAX] (idx 1..187)
    int64_t best_score = -0x7FFFFFFFFFFFFFFFLL;
    int tau_star = 0;
    int best_idx = 0;
    for (int idx = 1; idx < N_SCAN_LAGS - 1; ++idx) {
        if (scores[idx] > best_score) {
            best_score = scores[idx];
            tau_star = TAU_SCAN_MIN + idx;
            best_idx = idx;
        }
    }

    // Cổng hữu thanh (Voicing Gate): best_score * 100 >= 45 * r0
    // Bẫy 2: Nhân chéo với __int128_t bảo đảm an toàn tuyệt đối
    if (static_cast<__int128>(best_score) * 100 < static_cast<__int128>(45) * r0) {
        return {0.0, 0, false, 0};
    }

    if (use_interpolation) {
        auto [tau_fine_q16, f0_q12_4] = parabolic_interpolation_fixed_cpp(scores, best_idx, tau_star);
        double f0_hz = static_cast<double>(f0_q12_4) / 16.0;
        return {f0_hz, tau_star, true, f0_q12_4};
    }

    double f0_hz = std::round(16000.0 / static_cast<double>(tau_star));
    int f0_q12_4 = static_cast<int>(std::round(f0_hz * 16.0));
    return {f0_hz, tau_star, true, f0_q12_4};
}

// ============================================================================
// Tự kiểm tra (Self-Test) in kết quả đối chiếu trực tiếp với Python
// ============================================================================
void run_selftest_cpp() {
    FpgaPitchRoms roms(0.01);
    std::cout << "=== SELFTEST lab_1_3_5.cpp (C++20) ===" << std::endl;
    std::cout << "H[0..4]: [";
    for (int i = 0; i < 5; ++i) std::cout << roms.hanning_q15[i] << (i < 4 ? ", " : "]\n");

    std::cout << "C[26..30]: [";
    for (int i = 0; i < 5; ++i) std::cout << roms.scoring_q13[i] << (i < 4 ? ", " : "]\n");
    std::cout << "C[214]: " << roms.scoring_q13.back() << std::endl;

    // Sinh sóng sin 440 Hz
    int64_t x_440[FRAME_LEN];
    for (int n = 0; n < FRAME_LEN; ++n) {
        double t = static_cast<double>(n) / 16000.0;
        x_440[n] = static_cast<int64_t>(std::round(0.5 * 32767.0 * std::sin(2.0 * M_PI * 440.0 * t)));
    }

    // Tính điểm 440 Hz
    int64_t sum_440 = 0;
    for (int n = 0; n < FRAME_LEN; ++n) sum_440 += x_440[n];
    int64_t mean_440 = div_floor_s64(sum_440 + 320LL, 640LL);
    int64_t xw_440[FRAME_LEN];
    for (int n = 0; n < FRAME_LEN; ++n) {
        int64_t zm = x_440[n] - mean_440;
        xw_440[n] = ((zm * roms.hanning_q15[n]) + 16384LL) >> 15;
    }

    int64_t sc_440[N_SCAN_LAGS];
    for (int idx = 0; idx < N_SCAN_LAGS; ++idx) {
        int tau = TAU_SCAN_MIN + idx;
        int64_t r_tau = 0;
        for (int n = 0; n < FRAME_LEN - tau; ++n) r_tau += xw_440[n] * xw_440[n + tau];
        sc_440[idx] = (r_tau * roms.scoring_q13[idx] + 4096LL) >> 13;
    }

    std::cout << "440 Hz S[35..37]: S[35]=" << sc_440[35 - 26]
              << ", S[36]=" << sc_440[36 - 26]
              << ", S[37]=" << sc_440[37 - 26] << std::endl;

    auto res = fixed_pitch_frame_cpp(x_440, 1000000000LL, true, roms);
    std::cout << "Parabolic mode B: tau_star=" << res.tau_star
              << ", f0_q12_4=" << res.f0_q12_4
              << " (" << std::fixed << std::setprecision(3) << res.f0_hz << " Hz)" << std::endl;

    // Quét chi phí quãng tám
    std::cout << "Octave Cost Sweep:" << std::endl;
    std::vector<double> costs = {0.0, 0.005, 0.009, 0.01, 0.02};
    for (double cost : costs) {
        FpgaPitchRoms r_cost(cost);
        int fails = 0;
        for (int f0 = 75; f0 <= 600; ++f0) {
            int64_t xt[FRAME_LEN];
            int64_t ref_e = 0;
            for (int n = 0; n < FRAME_LEN; ++n) {
                double t = static_cast<double>(n) / 16000.0;
                double val = 0.5 * std::sin(2.0 * M_PI * static_cast<double>(f0) * t) * 32768.0;
                xt[n] = static_cast<int64_t>(std::round(val));
                ref_e += xt[n] * xt[n];
            }
            auto rf = fixed_pitch_frame_cpp(xt, ref_e, true, r_cost);
            if (rf.f0_hz <= 0.0 || std::abs(1200.0 * std::log2(rf.f0_hz / f0)) > 600.0) {
                fails++;
            }
        }
        std::cout << "  cost=" << std::fixed << std::setprecision(3) << cost
                  << ": " << fails << " / 526 failures" << std::endl;
    }

    // Kiểm tra sai số sóng sin chuẩn
    std::cout << "Sine Freq Accuracy (Mode B vs true freq):" << std::endl;
    std::vector<double> test_freqs = {75.0, 100.0, 200.0, 440.0, 590.0};
    for (double f : test_freqs) {
        int64_t xt[FRAME_LEN];
        int64_t ref_e = 0;
        for (int n = 0; n < FRAME_LEN; ++n) {
            double t = static_cast<double>(n) / 16000.0;
            xt[n] = static_cast<int64_t>(std::round(0.5 * 32767.0 * std::sin(2.0 * M_PI * f * t)));
            ref_e += xt[n] * xt[n];
        }
        auto rf = fixed_pitch_frame_cpp(xt, ref_e, true, roms);
        double c_err = 1200.0 * std::log2(rf.f0_hz / f);
        std::cout << "  " << std::setw(3) << static_cast<int>(f) << " Hz: "
                  << (c_err >= 0 ? "+" : "") << std::fixed << std::setprecision(2) << c_err
                  << " c (F0 = " << std::fixed << std::setprecision(3) << rf.f0_hz << " Hz)" << std::endl;
    }
}

void export_hex_cpp(const std::string& out_dir = "chapter01/hex") {
    FpgaPitchRoms roms;
    std::ofstream fh(out_dir + "/hanning_rom.hex");
    if (fh.is_open()) {
        for (int v : roms.hanning_q15) {
            fh << std::hex << std::setw(4) << std::setfill('0') << (v & 0xFFFF) << "\n";
        }
        fh.close();
    }
    std::ofstream fc(out_dir + "/c_tau_rom.hex");
    if (fc.is_open()) {
        for (int v : roms.scoring_q13) {
            fc << std::hex << std::setw(4) << std::setfill('0') << (v & 0xFFFF) << "\n";
        }
        fc.close();
    }
    std::ofstream ff(out_dir + "/f0_lut.hex");
    if (ff.is_open()) {
        for (int v : roms.f0_lut_q12_4) {
            ff << std::hex << std::setw(4) << std::setfill('0') << (v & 0xFFFF) << "\n";
        }
        ff.close();
    }
    std::cout << "Exported ROM hex files to " << out_dir << std::endl;
}

// ============================================================================
// Điểm nhập chính (main)
// ============================================================================
int main(int argc, char* argv[]) {
    bool do_selftest = true;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--export-hex") {
            std::string dir = (i + 1 < argc && argv[i + 1][0] != '-') ? argv[++i] : "chapter01/hex";
            export_hex_cpp(dir);
            do_selftest = false;
        } else if (arg == "--selftest") {
            do_selftest = true;
        }
    }
    if (do_selftest) {
        run_selftest_cpp();
    }
    return 0;
}
