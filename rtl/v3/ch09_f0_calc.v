// ============================================================================
// File: rtl/v3/ch09_f0_calc.v
// Module: ch09_f0_calc
// Description: Top-Level F0 Parabolic Interpolation and Divider Unit (Chapter 9)
//              Integrates:
//                1. ch09_peak_finder: candidate detection on tau in [27, 213]
//                   and argmax Sc selection.
//                2. Parabola parameter preparation with dynamic s2 normalization:
//                     num = up - um, den = 2*u0 - um - up
//                     s2 = max(0, bitlen(den) - 24)
//                     numn = num >>> s2, denn = den >> s2
//                     D = 2*denn*tau_p + numn (34-bit unsigned)
//                     N = 512000*denn + D/2 (44-bit unsigned)
//                3. ch09_radix2_div: 44/34 bit sequential restoring divider
//                   (can also instantiate ch09_lpm_div_wrapper for Route A).
//              Outputs:
//                out_valid: 1-cycle completion pulse
//                out_f0_raw: Q12.4 uint16 raw F0 estimate (Hz * 16)
//                out_best_tau, out_sc, out_r0n: forwarded to Ch.10 for voicing gate.
// ============================================================================

`timescale 1ns / 1ps

module ch09_f0_calc (
    input  wire               clk,
    input  wire               rst_n,

    // Streaming input interface from Ch.8 (ch08_norm_score)
    input  wire               in_valid,
    input  wire [7:0]         in_tau,     // 26..214
    input  wire signed [27:0] in_U,       // Normalised ac U[tau]
    input  wire signed [27:0] in_Sc,      // Cost-adjusted score Sc[tau]
    input  wire [26:0]        in_R0n,     // Normalised energy R0n
    input  wire               in_last,    // 1 on lag 214

    // Result output interface (to Ch.10 Voicing Gate)
    output reg                out_valid,
    output reg  [15:0]        out_f0_raw,  // Q12.4 unsigned
    output reg  [7:0]         out_best_tau,
    output reg  signed [27:0] out_sc,
    output reg  [26:0]        out_r0n,
    output reg                out_found
);

    // ------------------------------------------------------------------------
    // Peak Finder Submodule
    // ------------------------------------------------------------------------
    wire               peak_valid;
    wire               peak_found;
    wire [7:0]         peak_tau;
    wire signed [27:0] peak_um;
    wire signed [27:0] peak_u0;
    wire signed [27:0] peak_up;
    wire signed [27:0] peak_sc;
    wire [26:0]        peak_r0n;

    ch09_peak_finder u_peak_finder (
        .clk        (clk),
        .rst_n      (rst_n),
        .in_valid   (in_valid),
        .in_tau     (in_tau),
        .in_U       (in_U),
        .in_Sc      (in_Sc),
        .in_R0n     (in_R0n),
        .in_last    (in_last),
        .peak_valid (peak_valid),
        .peak_found (peak_found),
        .peak_tau   (peak_tau),
        .peak_um    (peak_um),
        .peak_u0    (peak_u0),
        .peak_up    (peak_up),
        .peak_sc    (peak_sc),
        .peak_r0n   (peak_r0n)
    );

    // ------------------------------------------------------------------------
    // FSM States
    // ------------------------------------------------------------------------
    localparam S_IDLE = 2'd0;
    localparam S_PREP = 2'd1;
    localparam S_DIV  = 2'd2;

    reg [1:0]          state;

    // Latched candidate parameters
    reg [7:0]          best_tau_reg;
    reg signed [27:0]  best_sc_reg;
    reg [26:0]         best_r0n_reg;
    reg signed [28:0]  num_reg;
    reg [28:0]         den_reg;

    // Divider interface
    reg                div_start;
    wire               div_busy;
    wire               div_done;
    reg  [43:0]        div_numer;
    reg  [33:0]        div_denom;
    wire [43:0]        div_quotient;
    wire [33:0]        div_remain;

    ch09_radix2_div #(
        .WIDTHN(44),
        .WIDTHD(34)
    ) u_divider (
        .clk      (clk),
        .rst_n    (rst_n),
        .start    (div_start),
        .busy     (div_busy),
        .done     (div_done),
        .numer    (div_numer),
        .denom    (div_denom),
        .quotient (div_quotient),
        .remain   (div_remain)
    );

    // ------------------------------------------------------------------------
    // Combinational Parabola & s2 Math in S_PREP
    // ------------------------------------------------------------------------
    reg [2:0] s2_comb;
    always @(*) begin
        if (den_reg[28])      s2_comb = 3'd5;
        else if (den_reg[27]) s2_comb = 3'd4;
        else if (den_reg[26]) s2_comb = 3'd3;
        else if (den_reg[25]) s2_comb = 3'd2;
        else if (den_reg[24]) s2_comb = 3'd1;
        else                  s2_comb = 3'd0;
    end

    wire signed [28:0] numn_comb  = num_reg >>> s2_comb;
    wire [28:0]        denn_shift = den_reg >> s2_comb;
    wire [23:0]        denn_comb  = denn_shift[23:0]; // guaranteed <= 2^24 - 1

    // denn * best_tau_reg (24 bit x 8 bit -> 32 bit unsigned)
    wire [31:0] mult_tau = denn_comb * best_tau_reg;

    // D = 2 * denn * best_tau + numn
    // Signed addition because numn can be negative
    wire signed [34:0] D_signed = {2'b00, mult_tau, 1'b0} + {{6{numn_comb[28]}}, numn_comb};
    wire [33:0] D_comb = D_signed[33:0];

    // 512000 * denn = (denn << 19) - (denn << 13) - (denn << 12)
    wire [43:0] prod_512k = ({20'd0, denn_comb} << 19) -
                            ({20'd0, denn_comb} << 13) -
                            ({20'd0, denn_comb} << 12);

    // N = 512000 * denn + D // 2
    wire [43:0] N_comb = prod_512k + {11'd0, D_comb[33:1]};

    // ------------------------------------------------------------------------
    // FSM Control Logic
    // ------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= S_IDLE;
            out_valid    <= 1'b0;
            out_f0_raw   <= 16'd0;
            out_best_tau <= 8'd0;
            out_sc       <= 28'sd0;
            out_r0n      <= 27'd0;
            out_found    <= 1'b0;

            best_tau_reg <= 8'd0;
            best_sc_reg  <= 28'sd0;
            best_r0n_reg <= 27'd0;
            num_reg      <= 29'sd0;
            den_reg      <= 29'd0;

            div_start    <= 1'b0;
            div_numer    <= 44'd0;
            div_denom    <= 34'd0;
        end else begin
            out_valid <= 1'b0;
            div_start <= 1'b0;

            case (state)
                S_IDLE: begin
                    if (peak_valid) begin
                        if (!peak_found) begin
                            // No candidate peak found in this frame
                            out_valid    <= 1'b1;
                            out_f0_raw   <= 16'd0;
                            out_best_tau <= 8'd0;
                            out_sc       <= 28'sd0;
                            out_r0n      <= peak_r0n;
                            out_found    <= 1'b0;
                            state        <= S_IDLE;
                        end else begin
                            // Latch candidate parameters
                            best_tau_reg <= peak_tau;
                            best_sc_reg  <= peak_sc;
                            best_r0n_reg <= peak_r0n;

                            // num = peak_up - peak_um
                            num_reg <= $signed(peak_up) - $signed(peak_um);

                            // den = 2*peak_u0 - peak_um - peak_up
                            // For a local peak: peak_u0 > peak_um and peak_u0 >= peak_up -> den >= 1
                            den_reg <= ($signed(peak_u0) <<< 1) - $signed(peak_um) - $signed(peak_up);

                            state <= S_PREP;
                        end
                    end
                end

                S_PREP: begin
                    // Trigger divider with prepared N and D
                    div_start <= 1'b1;
                    div_numer <= N_comb;
                    div_denom <= D_comb;
                    state     <= S_DIV;
                end

                S_DIV: begin
                    if (div_done) begin
                        out_valid    <= 1'b1;
                        out_f0_raw   <= (div_quotient > 44'd65535) ? 16'hFFFF : div_quotient[15:0];
                        out_best_tau <= best_tau_reg;
                        out_sc       <= best_sc_reg;
                        out_r0n      <= best_r0n_reg;
                        out_found    <= 1'b1;
                        state        <= S_IDLE;
                    end
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
