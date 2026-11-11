// ============================================================================
// File: rtl/v3/ch09_peak_finder.v
// Module: ch09_peak_finder
// Description: Streaming Candidate Peak Finder and Argmax Sc Selector
//              Scans lags tau = 26..214 from Ch.8, searches for local peaks
//              over tau in [27, 213] matching Praat 7.0.03 Sound_to_Pitch.cpp:
//                1. Local peak condition: U[tau] > U[tau-1] && U[tau] >= U[tau+1]
//                2. Voicing threshold gate: 1000 * U[tau] > 225 * R0n
//                   (equivalent to 40 * U[tau] > 9 * R0n, 0 DSP multipliers)
//                3. Argmax Sc selection: picks candidate with highest Sc[tau]
//                   (strictly Sc > best_sc, earlier tau wins ties).
// Latency: 1 clock cycle after in_last at lag 214.
// ============================================================================

`timescale 1ns / 1ps

module ch09_peak_finder (
    input  wire               clk,
    input  wire               rst_n,

    // Streaming input interface from Ch.8 (ch08_norm_score)
    input  wire               in_valid,
    input  wire [7:0]         in_tau,     // 26..214
    input  wire signed [27:0] in_U,       // Normalised ac U[tau]
    input  wire signed [27:0] in_Sc,      // Cost-adjusted score Sc[tau]
    input  wire [26:0]        in_R0n,     // Normalised energy R0n
    input  wire               in_last,    // 1 on lag 214

    // Result output interface
    output reg                peak_valid, // 1-cycle pulse when search complete
    output reg                peak_found, // 1 if at least one candidate found
    output reg  [7:0]         peak_tau,   // tau_p of winning candidate
    output reg  signed [27:0] peak_um,    // U[tau_p - 1]
    output reg  signed [27:0] peak_u0,    // U[tau_p]
    output reg  signed [27:0] peak_up,    // U[tau_p + 1]
    output reg  signed [27:0] peak_sc,    // Sc[tau_p]
    output reg  [26:0]        peak_r0n    // R0n latched for voicing check
);

    // ------------------------------------------------------------------------
    // Internal registers: 3-tap delay buffer for streaming candidate detection
    // ------------------------------------------------------------------------
    reg signed [27:0] u_prev2;
    reg signed [27:0] u_prev1;
    reg signed [27:0] sc_prev1;
    reg [7:0]         tau_prev1;
    reg [26:0]        r0n_latched;

    // Running best candidate registers
    reg               best_found;
    reg [7:0]         best_tau;
    reg signed [27:0] best_um;
    reg signed [27:0] best_u0;
    reg signed [27:0] best_up;
    reg signed [27:0] best_sc;

    // ------------------------------------------------------------------------
    // Combinational evaluation for candidate center at tau_prev1
    // Center candidate is tau_c = tau_prev1, left neighbor is u_prev2,
    // right neighbor is in_U (current incoming sample).
    // ------------------------------------------------------------------------
    wire signed [34:0] term_40u  = ({{7{u_prev1[27]}}, u_prev1} <<< 5) +
                                   ({{7{u_prev1[27]}}, u_prev1} <<< 3);
    wire signed [34:0] term_9r0n = {4'b0000, (r0n_latched << 3) + r0n_latched};

    wire is_cand = (tau_prev1 >= 8'd27) && (tau_prev1 <= 8'd213) &&
                   (u_prev1 > u_prev2) &&
                   (u_prev1 >= in_U) &&
                   (term_40u > term_9r0n);

    // ------------------------------------------------------------------------
    // Sequential tracking
    // ------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            u_prev2     <= 28'sd0;
            u_prev1     <= 28'sd0;
            sc_prev1    <= 28'sd0;
            tau_prev1   <= 8'd0;
            r0n_latched <= 27'd0;

            best_found  <= 1'b0;
            best_tau    <= 8'd0;
            best_um     <= 28'sd0;
            best_u0     <= 28'sd0;
            best_up     <= 28'sd0;
            best_sc     <= 28'sd0;

            peak_valid  <= 1'b0;
            peak_found  <= 1'b0;
            peak_tau    <= 8'd0;
            peak_um     <= 28'sd0;
            peak_u0     <= 28'sd0;
            peak_up     <= 28'sd0;
            peak_sc     <= 28'sd0;
            peak_r0n    <= 27'd0;
        end else begin
            peak_valid <= 1'b0;

            if (in_valid) begin
                // Latch R0n on the first incoming lag (tau == 26) and reset running best
                if (in_tau == 8'd26) begin
                    r0n_latched <= in_R0n;
                    best_found  <= 1'b0;
                    best_tau    <= 8'd0;
                    best_um     <= 28'sd0;
                    best_u0     <= 28'sd0;
                    best_up     <= 28'sd0;
                    best_sc     <= -28'sd134217728; // -2^27
                end

                // Evaluate candidate at tau_prev1 against incoming in_U
                if (is_cand) begin
                    if (!best_found || (sc_prev1 > best_sc)) begin
                        best_found <= 1'b1;
                        best_tau   <= tau_prev1;
                        best_um    <= u_prev2;
                        best_u0    <= u_prev1;
                        best_up    <= in_U;
                        best_sc    <= sc_prev1;
                    end
                end

                // Shift pipeline
                u_prev2   <= u_prev1;
                u_prev1   <= in_U;
                sc_prev1  <= in_Sc;
                tau_prev1 <= in_tau;

                // When in_last arrives (at lag 214), candidate 213 was just evaluated
                if (in_last) begin
                    peak_valid <= 1'b1;
                    // Note: if lag 213 was a candidate that beats prior best, update outputs
                    if (is_cand && (!best_found || (sc_prev1 > best_sc))) begin
                        peak_found <= 1'b1;
                        peak_tau   <= tau_prev1;
                        peak_um    <= u_prev2;
                        peak_u0    <= u_prev1;
                        peak_up    <= in_U;
                        peak_sc    <= sc_prev1;
                    end else begin
                        peak_found <= best_found;
                        peak_tau   <= best_tau;
                        peak_um    <= best_um;
                        peak_u0    <= best_u0;
                        peak_up    <= best_up;
                        peak_sc    <= best_sc;
                    end
                    peak_r0n <= in_R0n;
                end
            end
        end
    end

endmodule
