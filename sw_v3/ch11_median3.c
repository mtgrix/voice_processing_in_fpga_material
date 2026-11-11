#include "ch11_median3.h"

uint16_t ch11_median3_scalar(uint16_t a, uint16_t b, uint16_t c) {
    int cmp_ab = (a <= b);
    int cmp_bc = (b <= c);
    int cmp_ac = (a <= c);

    if (cmp_ab) {
        if (cmp_bc)
            return b;
        else if (cmp_ac)
            return c;
        else
            return a;
    } else {
        if (cmp_ac)
            return a;
        else if (cmp_bc)
            return c;
        else
            return b;
    }
}

void ch11_median3_stream_init(ch11_median3_stream_t *s) {
    if (!s) return;
    s->state  = CH11_STATE_IDLE;
    s->f0_z0  = 0;
    s->f0_z1  = 0;
    s->f0_z2  = 0;
    s->f0_med = 0;
}

int ch11_median3_stream_step(ch11_median3_stream_t *s,
                             int in_valid, int in_first, int in_last, uint16_t in_f0,
                             int *out_valid, int *out_last, uint16_t *out_f0) {
    if (!s || !out_valid || !out_last || !out_f0) return -1;

    *out_valid = 0;
    *out_last  = 0;
    *out_f0    = 0;

    switch (s->state) {
        case CH11_STATE_IDLE:
            if (in_valid && in_first) {
                s->f0_z0 = in_f0;
                s->f0_z1 = in_f0;
                s->f0_z2 = in_f0;
                if (in_last) {
                    s->state = CH11_STATE_FLUSH;
                } else {
                    s->state = CH11_STATE_STREAM;
                }
            }
            break;

        case CH11_STATE_STREAM:
            if (in_valid) {
                uint16_t med = ch11_median3_scalar(s->f0_z2, s->f0_z1, in_f0);
                s->f0_med = med;
                *out_valid = 1;
                *out_last  = 0;
                *out_f0    = med;

                s->f0_z2 = s->f0_z1;
                s->f0_z1 = in_f0;
                s->f0_z0 = in_f0;

                if (in_last) {
                    s->state = CH11_STATE_FLUSH;
                }
            }
            break;

        case CH11_STATE_FLUSH: {
            uint16_t med = ch11_median3_scalar(s->f0_z2, s->f0_z1, s->f0_z1);
            s->f0_med = med;
            *out_valid = 1;
            *out_last  = 1;
            *out_f0    = med;

            s->f0_z0 = s->f0_z1;
            s->state = CH11_STATE_IDLE;
            break;
        }

        default:
            s->state = CH11_STATE_IDLE;
            break;
    }

    return 0;
}

void ch11_median3_array(const uint16_t *src, uint16_t *dst, size_t n) {
    if (!src || !dst || n == 0) return;

    if (n == 1) {
        dst[0] = src[0];
        return;
    }

    // Khung đầu tiên k = 0: lặp mẫu biên bên trái src[0]
    dst[0] = ch11_median3_scalar(src[0], src[0], src[1]);

    // Các khung nội tại k = 1 .. n-2
    for (size_t k = 1; k + 1 < n; ++k) {
        dst[k] = ch11_median3_scalar(src[k - 1], src[k], src[k + 1]);
    }

    // Khung cuối cùng k = n-1: lặp mẫu biên bên phải src[n-1]
    dst[n - 1] = ch11_median3_scalar(src[n - 2], src[n - 1], src[n - 1]);
}
