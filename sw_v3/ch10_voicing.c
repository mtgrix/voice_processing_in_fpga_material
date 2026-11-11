// sw_v3/ch10_voicing.c
// Implementation of integer cross-multiplication voicing decision
#include "ch10_voicing.h"

void ch10_decide_voicing(uint16_t f0_raw,
                         int32_t sc,
                         uint32_t r0n,
                         bool cand_found,
                         uint16_t lp,
                         uint16_t gp,
                         ch10_voicing_result_t *res)
{
    // Silence shortcuts: R0 == 0, LP == 0, GP == 0, or no candidate found
    bool silence_trap = (r0n == 0) || (lp == 0) || (gp == 0) || (!cand_found);

    // LHS terms: (100*Sc - 45*R0n) * 3 * GP
    int64_t term1 = (int64_t)100 * sc - (int64_t)45 * r0n;
    int64_t mult3_gp = (int64_t)3 * gp;
    int64_t lhs = term1 * mult3_gp;

    // RHS terms: 100 * R0n * max(0, 6*GP - 145*LP)
    int32_t ramp = (int32_t)6 * gp - (int32_t)145 * lp;
    int32_t ramp_pos = (ramp > 0) ? ramp : 0;
    int64_t term_100_r0n = (int64_t)100 * r0n;
    int64_t rhs = term_100_r0n * (int64_t)ramp_pos;

    // Strict inequality: voiced iff LHS > RHS and not in silence trap
    bool is_voiced = (!silence_trap) && (lhs > rhs);

    res->voiced       = is_voiced;
    res->f0           = is_voiced ? f0_raw : 0;
    res->lhs          = lhs;
    res->rhs          = rhs;
    res->term1        = term1;
    res->ramp         = ramp;
    res->ramp_pos     = ramp_pos;
    res->silence_trap = silence_trap;
}
