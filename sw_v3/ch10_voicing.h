// sw_v3/ch10_voicing.h
// Software reference implementation of Praat-consistent Voicing Decision
// (Silence / Voiceless / Voiced) via 54-bit cross-multiplication for HPS / ARM
#ifndef CH10_VOICING_H
#define CH10_VOICING_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    bool     voiced;       // true if voiced, false if voiceless/silent
    uint16_t f0;           // Gated F0 in Q12.4 (f0_raw if voiced, 0 if unvoiced)
    int64_t  lhs;          // (100*Sc - 45*R0n) * 3 * GP
    int64_t  rhs;          // 100 * R0n * max(0, 6*GP - 145*LP)
    int64_t  term1;        // 100*Sc - 45*R0n
    int32_t  ramp;         // 6*GP - 145*LP
    int32_t  ramp_pos;     // max(0, ramp)
    bool     silence_trap; // true if R0n==0 || LP==0 || GP==0 || !cand_found
} ch10_voicing_result_t;

/**
 * Computes the voicing decision using Praat's exact threshold curve
 * transformed into integer cross-multiplication:
 *   LHS = (100 * Sc - 45 * R0n) * 3 * GP
 *   RHS = 100 * R0n * max(0, 6 * GP - 145 * LP)
 *   Voiced iff !silence_trap && (LHS > RHS)
 *
 * @param f0_raw     Raw F0 candidate in Q12.4 format from Ch.9.
 * @param sc         Cost-adjusted score Sc of best candidate from Ch.9 (28-bit signed).
 * @param r0n        Normalized frame energy R0n from Ch.8 (27-bit unsigned).
 * @param cand_found Boolean flag from Ch.9 indicating a valid peak was detected.
 * @param lp         Local peak amplitude LP = max|xw[j]| for j=212..425 from Ch.6.
 * @param gp         Global peak amplitude GP from HPS WAV analysis.
 * @param res        Pointer to result structure.
 */
void ch10_decide_voicing(uint16_t f0_raw,
                         int32_t sc,
                         uint32_t r0n,
                         bool cand_found,
                         uint16_t lp,
                         uint16_t gp,
                         ch10_voicing_result_t *res);

#ifdef __cplusplus
}
#endif

#endif // CH10_VOICING_H
