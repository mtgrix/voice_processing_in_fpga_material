// ============================================================================
// File: rtl/v3/ch10_voicing.v
// Module: ch10_voicing
// Description: Praat-Consistent Voicing Decision Unit (Chapter 10)
//              Evaluates the cross-multiplied voicing inequality:
//                (100*Sc - 45*R0n) * 3 * GP > 100 * R0n * max(0, 6*GP - 145*LP)
//              Using a 3-stage pipeline with shift-add constants:
//                - Stage 1: Linear combinations via shift-add (100*Sc, 45*R0n, 3*GP, 145*LP, 6*GP, 100*R0n)
//                           and silence condition evaluation.
//                - Stage 2: 54-bit multiplications (LHS = term1 * 3*GP, RHS = 100*R0n * ramp_pos).
//                - Stage 3: Strict comparison (LHS > RHS), silence gating, and Q12.4 F0 output multiplexing.
//              Latency: Exactly 3 clock cycles from in_valid to out_valid.
//              Throughput: 1 frame decision per cycle.
//              Silicon footprint: 0 M10K RAM.
// ============================================================================

`timescale 1ns / 1ps

module ch10_voicing (
    input  wire               clk,
    input  wire               rst_n,

    // Control and Data input from Chapter 9 (ch09_f0_calc)
    input  wire               in_valid,
    input  wire [15:0]        in_f0_raw,      // Raw F0 in Q12.4 format
    input  wire signed [27:0] in_sc,          // Cost-adjusted score Sc of best candidate (28-bit signed)
    input  wire [26:0]        in_r0n,         // Normalized frame energy R0n (27-bit unsigned)
    input  wire               in_cand_found,  // At least one valid candidate met peak criteria

    // Measurement inputs from Chapter 6 and HPS
    input  wire [15:0]        in_lp,          // Local peak amplitude LP = max|xw[j]| for j in [212, 425]
    input  wire [15:0]        in_gp,          // Global peak amplitude GP from HPS WAV analysis

    // Output decision interface
    output reg                out_valid,      // Asserted for 1 cycle when decision is ready
    output reg  [15:0]        out_f0,         // Gated F0 in Q12.4 (in_f0_raw if voiced, 0 if unvoiced)
    output reg                out_voiced,     // 1 if frame is voiced, 0 if unvoiced/silent
    output reg  signed [53:0] out_lhs,        // LHS value (for verification/debugging)
    output reg  signed [53:0] out_rhs         // RHS value (for verification/debugging)
);

    // ------------------------------------------------------------------------
    // Stage 1: Linear Combinations via Shift-and-Add & Silence Detection
    // ------------------------------------------------------------------------
    // Constant multiplier implementations using shift-add:
    // 100 = 64 + 32 + 4 = (x << 6) + (x << 5) + (x << 2)
    // 45  = 32 + 8 + 4 + 1 = (x << 5) + (x << 3) + (x << 2) + x
    // 3   = 2 + 1 = (x << 1) + x
    // 6   = 4 + 2 = (x << 2) + (x << 1)
    // 145 = 128 + 16 + 1 = (x << 7) + (x << 4) + x

    wire signed [34:0] sc_ext = {{7{in_sc[27]}}, in_sc};
    wire signed [34:0] term_100_sc = (sc_ext <<< 6) + (sc_ext <<< 5) + (sc_ext <<< 2);

    wire signed [34:0] r0n_ext = {8'd0, in_r0n};
    wire signed [34:0] term_45_r0n = (r0n_ext <<< 5) + (r0n_ext <<< 3) + (r0n_ext <<< 2) + r0n_ext;

    wire signed [34:0] comb_term1 = term_100_sc - term_45_r0n;

    wire [17:0] comb_mult3_gp = {in_gp, 1'b0} + {2'b00, in_gp};
    wire [33:0] comb_100_r0n  = ({in_r0n, 6'd0}) + ({in_r0n, 5'd0}) + ({in_r0n, 2'd0});

    wire [18:0] comb_mult6_gp   = ({1'b0, in_gp, 2'b00}) + ({2'b00, in_gp, 1'b0});
    wire [23:0] comb_mult145_lp = ({in_lp, 7'd0}) + ({3'd0, in_lp, 4'd0}) + ({8'd0, in_lp});

    wire signed [24:0] comb_ramp_diff = $signed({6'd0, comb_mult6_gp}) - $signed({1'b0, comb_mult145_lp});
    wire [17:0] comb_ramp_pos = (comb_ramp_diff > 25'sd0) ? comb_ramp_diff[17:0] : 18'd0;

    wire comb_silence_trap = (in_r0n == 27'd0) || (in_lp == 16'd0) || (in_gp == 16'd0) || (!in_cand_found);

    reg signed [34:0] s1_term1;
    reg        [17:0] s1_mult3_gp;
    reg        [33:0] s1_100_r0n;
    reg        [17:0] s1_ramp_pos;
    reg        [15:0] s1_f0_raw;
    reg               s1_silence_trap;
    reg               s1_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s1_term1        <= 35'sd0;
            s1_mult3_gp     <= 18'd0;
            s1_100_r0n      <= 34'd0;
            s1_ramp_pos     <= 18'd0;
            s1_f0_raw       <= 16'd0;
            s1_silence_trap <= 1'b1;
            s1_valid        <= 1'b0;
        end else begin
            s1_term1        <= comb_term1;
            s1_mult3_gp     <= comb_mult3_gp;
            s1_100_r0n      <= comb_100_r0n;
            s1_ramp_pos     <= comb_ramp_pos;
            s1_f0_raw       <= in_f0_raw;
            s1_silence_trap <= comb_silence_trap;
            s1_valid        <= in_valid;
        end
    end

    // ------------------------------------------------------------------------
    // Stage 2: 54-bit Products Generation (LHS and RHS)
    // ------------------------------------------------------------------------
    wire signed [53:0] comb_lhs = s1_term1 * $signed({1'b0, s1_mult3_gp});
    wire signed [53:0] comb_rhs = $signed({1'b0, s1_100_r0n}) * $signed({1'b0, s1_ramp_pos});

    reg signed [53:0] s2_lhs;
    reg signed [53:0] s2_rhs;
    reg        [15:0] s2_f0_raw;
    reg               s2_silence_trap;
    reg               s2_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s2_lhs          <= 54'sd0;
            s2_rhs          <= 54'sd0;
            s2_f0_raw       <= 16'd0;
            s2_silence_trap <= 1'b1;
            s2_valid        <= 1'b0;
        end else begin
            s2_lhs          <= comb_lhs;
            s2_rhs          <= comb_rhs;
            s2_f0_raw       <= s1_f0_raw;
            s2_silence_trap <= s1_silence_trap;
            s2_valid        <= s1_valid;
        end
    end

    // ------------------------------------------------------------------------
    // Stage 3: Strict Comparator, Silence Gating and Q12.4 F0 Multiplexer
    // ------------------------------------------------------------------------
    wire comb_is_voiced = (!s2_silence_trap) && (s2_lhs > s2_rhs);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_valid   <= 1'b0;
            out_f0      <= 16'd0;
            out_voiced  <= 1'b0;
            out_lhs     <= 54'sd0;
            out_rhs     <= 54'sd0;
        end else begin
            out_valid   <= s2_valid;
            out_voiced  <= comb_is_voiced;
            out_f0      <= comb_is_voiced ? s2_f0_raw : 16'd0;
            out_lhs     <= s2_lhs;
            out_rhs     <= s2_rhs;
        end
    end

endmodule
