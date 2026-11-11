#ifndef CH11_MEDIAN3_H
#define CH11_MEDIAN3_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Tính trung vị của 3 số nguyên không dấu 16-bit (Q12.4).
 *        Mô phỏng chính xác mạng 3 bộ so sánh trong RTL Verilog (rtl/v3/ch11_median3.v).
 */
uint16_t ch11_median3_scalar(uint16_t a, uint16_t b, uint16_t c);

/**
 * @brief Trạng thái của bộ lọc Median-3 dạng luồng phần cứng (Streaming state machine).
 *        Ánh xạ 1-1 với các thanh ghi f0_z0, f0_z1, f0_z2 và trạng thái FSM.
 */
typedef enum {
    CH11_STATE_IDLE = 0,
    CH11_STATE_STREAM = 1,
    CH11_STATE_FLUSH = 2
} ch11_state_t;

typedef struct {
    ch11_state_t state;
    uint16_t     f0_z0;
    uint16_t     f0_z1;
    uint16_t     f0_z2;
    uint16_t     f0_med;
} ch11_median3_stream_t;

/**
 * @brief Khởi tạo lại trạng thái bộ lọc Median-3 dạng luồng.
 */
void ch11_median3_stream_init(ch11_median3_stream_t *s);

/**
 * @brief Xử lý một mẫu F0 mới đến trong luồng.
 * @param s Con trỏ đến cấu trúc trạng thái.
 * @param in_valid 1 nếu có mẫu mới.
 * @param in_first 1 nếu là mẫu đầu tiên (khung 0).
 * @param in_last 1 nếu là mẫu cuối cùng (khung N-1).
 * @param in_f0 Giá trị F0 ngõ vào (Q12.4).
 * @param out_valid Con trỏ nhận cờ ngõ ra hợp lệ (1 chu kỳ).
 * @param out_last Con trỏ nhận cờ mẫu cuối cùng.
 * @param out_f0 Con trỏ nhận giá trị F0 sau lọc trung vị.
 * @return 0 nếu thành công, mã lỗi âm nếu thất bại.
 */
int ch11_median3_stream_step(ch11_median3_stream_t *s,
                             int in_valid, int in_first, int in_last, uint16_t in_f0,
                             int *out_valid, int *out_last, uint16_t *out_f0);

/**
 * @brief Bộ lọc Median-3 xử lý mảng tĩnh toàn bộ tệp (Batch array processing),
 *        sử dụng quy tắc lặp mẫu biên đối xứng chuẩn Praat / golden_v2.
 * @param src Mảng F0 thô ngõ vào (độ dài n).
 * @param dst Mảng F0 sau lọc ngõ ra (độ dài n).
 * @param n Số lượng khung (n >= 1).
 */
void ch11_median3_array(const uint16_t *src, uint16_t *dst, size_t n);

#ifdef __cplusplus
}
#endif

#endif // CH11_MEDIAN3_H
