// rtl/v3/ch08_norm_score.v
// Pipelined Window Normalization C[tau] and Subtractive Octave Cost Unit
// Matches Praat 7.0.03 normalized autocorrelation and candidate ranking local cost
//
// Theoretical formulation:
//   1. Dynamic shift on R0:
//        sh = max(0, bitlen(R0) - 26)
//        R0n = R0 >> sh               (26-bit non-negative mantissa)
//   2. Stream scaling on R[tau]:
//        Rn[tau] = R[tau] >>> sh      (27-bit signed operand)
//   3. Window normalization:
//        U[tau] = (Rn[tau] * C[tau] + 2^13) >>> 14        (~ r(tau) * R0n)
//   4. Octave cost subtraction:
//        term_k = (R0n * K[tau] + 2^19) >>> 20
//        Sc[tau] = U[tau] - term_k                        (~ (r(tau) - 0.01*log2(600/f)) * R0n)
//
// Pipeline latency: 2 clock cycles from sampling in_tau at Edge 1 to valid U[tau]/Sc[tau] at Edge 3
//   (3 pipeline register stages: Stage 1 input latch/ROM, Stage 2 DSP mult, Stage 3 output)
//   Stage 1: Combinational ROM address (in_tau - 26) + synchronous ROM read (1 cycle)
//            in lockstep with dynamic arithmetic shift (Rn = in_R >>> sh)
//   Stage 2: Dual DSP multipliers (Rn*C and R0n*K)
//   Stage 3: Rounding (+2^13, +2^19), shift (>>> 14, >>> 20), subtraction (Sc = U - term_k)
//
// Document citations:
//   - Embedded Memory (RAM: 1-PORT, RAM: 2-PORT, ROM: 1-PORT, and ROM: 2-PORT) User Guide (UG-01068)
//   - Integer Arithmetic IP Cores User Guide (UG-01069)
//   - Cyclone V Device Handbook, Volume 1 (CV-52003), Chapter 5: Variable Precision DSP Blocks

`timescale 1ns/1ps

module ch08_norm_score #(
    parameter integer IN_W         = 48,  // Autocorrelation bit-width from MAC
    parameter integer RN_W         = 27,  // Normalized R bit-width (signed)
    parameter integer R0N_W        = 26,  // Normalized R0 bit-width (unsigned)
    parameter integer OUT_W        = 28,  // U and Sc bit-width (signed)
    parameter integer TAU_SCAN_MIN = 26,
    parameter integer TAU_SCAN_MAX = 214,
    parameter         INIT_FILE    = "golden_v2/rom/ck_rom.hex"
) (
    input  wire                   clk,
    input  wire                   rst_n,

    // Streaming input from MAC engine
    input  wire                   in_valid,
    input  wire [7:0]             in_tau,    // 0 for R0, or 26..214 for R[tau]
    input  wire signed [IN_W-1:0] in_R,

    // Streaming output to Peak Detector and Voicing stages
    output reg                    out_valid,
    output reg  [7:0]             out_tau,
    output reg  signed [OUT_W-1:0] out_U,
    output reg  signed [OUT_W-1:0] out_Sc,
    output reg  [R0N_W-1:0]       out_R0n,
    output reg  [4:0]             out_sh,
    output reg                    out_last
);

    // -------------------------------------------------------------------------
    // Priority encoder to compute bitlen(R0) and sh = max(0, bitlen(R0) - 26)
    // -------------------------------------------------------------------------
    function [5:0] calc_bitlen;
        input [IN_W-1:0] val;
        integer i;
        begin
            calc_bitlen = 6'd0;
            for (i = IN_W-1; i >= 0; i = i - 1) begin
                if (val[i] && (calc_bitlen == 6'd0)) begin
                    calc_bitlen = i[5:0] + 6'd1;
                end
            end
        end
    endfunction

    reg [4:0]        sh_reg;
    reg [R0N_W-1:0]  r0n_reg;

    wire [5:0] r0_len  = calc_bitlen(in_R);
    wire [4:0] sh_comb = (r0_len > 6'd26) ? (r0_len[4:0] - 5'd26) : 5'd0;
    wire [IN_W-1:0] r0_shifted = in_R >> sh_comb;

    // Latch R0 and compute normalization factor sh
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sh_reg  <= 5'd0;
            r0n_reg <= {R0N_W{1'b0}};
        end else begin
            if (in_valid && (in_tau == 8'd0)) begin
                sh_reg  <= sh_comb;
                r0n_reg <= r0_shifted[R0N_W-1:0];
            end
        end
    end

    // -------------------------------------------------------------------------
    // ROM instantiation: 256x32 (bits[31:16]=C[tau], bits[15:0]=K[tau])
    // Combinational address driven directly from in_tau
    // Read latency = 1 cycle (registered q inside ch08_ck_rom)
    // -------------------------------------------------------------------------
    wire [7:0]  rom_addr;
    wire [31:0] rom_data;

    assign rom_addr = (in_valid && (in_tau >= TAU_SCAN_MIN[7:0]) && (in_tau <= TAU_SCAN_MAX[7:0]))
                    ? (in_tau - TAU_SCAN_MIN[7:0])
                    : 8'd0;

    ch08_ck_rom #(
        .ADDR_W    (8),
        .DATA_W    (32),
        .DEPTH     (256),
        .INIT_FILE (INIT_FILE)
    ) u_ck_rom (
        .clk  (clk),
        .addr (rom_addr),
        .q    (rom_data)
    );

    // -------------------------------------------------------------------------
    // Pipeline Stage 1: Dynamic arithmetic shift of R[tau] and pipeline registers
    // In lockstep with ROM read (rom_data and Stage 1 registers update on same clk edge)
    // -------------------------------------------------------------------------
    reg                     v_pipe1;
    reg [7:0]               tau_pipe1;
    reg signed [RN_W-1:0]   rn_pipe1;
    reg [R0N_W-1:0]         r0n_pipe1;

    wire signed [IN_W-1:0] r_shifted = in_R >>> sh_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_pipe1   <= 1'b0;
            tau_pipe1 <= 8'd0;
            rn_pipe1  <= {RN_W{1'b0}};
            r0n_pipe1 <= {R0N_W{1'b0}};
        end else begin
            if (in_valid && (in_tau >= TAU_SCAN_MIN[7:0]) && (in_tau <= TAU_SCAN_MAX[7:0])) begin
                v_pipe1   <= 1'b1;
                tau_pipe1 <= in_tau;
                rn_pipe1  <= r_shifted[RN_W-1:0];
                r0n_pipe1 <= r0n_reg;
            end else begin
                v_pipe1   <= 1'b0;
                tau_pipe1 <= 8'd0;
                rn_pipe1  <= {RN_W{1'b0}};
                r0n_pipe1 <= {R0N_W{1'b0}};
            end
        end
    end

    // -------------------------------------------------------------------------
    // Pipeline Stage 2: Dual Multipliers (Rn * C and R0n * K)
    // -------------------------------------------------------------------------
    reg                     v_pipe2;
    reg [7:0]               tau_pipe2;
    reg signed [43:0]       prod_c_pipe2; // 27-bit signed * 17-bit signed -> 44-bit signed
    reg signed [42:0]       prod_k_pipe2; // 27-bit signed * 16-bit signed -> 43-bit signed
    reg [R0N_W-1:0]         r0n_pipe2;

    wire [15:0]        c_coeff = rom_data[31:16]; // Q2.14 unsigned
    wire signed [15:0] k_coeff = $signed(rom_data[15:0]); // signed 16-bit

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_pipe2      <= 1'b0;
            tau_pipe2    <= 8'd0;
            prod_c_pipe2 <= 44'sd0;
            prod_k_pipe2 <= 43'sd0;
            r0n_pipe2    <= {R0N_W{1'b0}};
        end else begin
            v_pipe2      <= v_pipe1;
            tau_pipe2    <= tau_pipe1;
            r0n_pipe2    <= r0n_pipe1;
            prod_c_pipe2 <= rn_pipe1 * $signed({1'b0, c_coeff});
            prod_k_pipe2 <= $signed({1'b0, r0n_pipe1}) * k_coeff;
        end
    end

    // -------------------------------------------------------------------------
    // Pipeline Stage 3: Rounding (+2^13, +2^19), Shift (>>> 14, >>> 20), Subtraction
    // -------------------------------------------------------------------------
    wire signed [43:0] c_rounded = prod_c_pipe2 + 44'sd8192;
    wire signed [29:0] u_div     = c_rounded >>> 14;

    wire signed [42:0] k_rounded = prod_k_pipe2 + 43'sd524288;
    wire signed [22:0] k_div     = k_rounded >>> 20;

    wire signed [29:0] sc_diff   = u_div - {{7{k_div[22]}}, k_div};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_valid <= 1'b0;
            out_tau   <= 8'd0;
            out_U     <= {OUT_W{1'b0}};
            out_Sc    <= {OUT_W{1'b0}};
            out_R0n   <= {R0N_W{1'b0}};
            out_sh    <= 5'd0;
            out_last  <= 1'b0;
        end else begin
            out_valid <= v_pipe2;
            out_tau   <= tau_pipe2;
            out_U     <= u_div[OUT_W-1:0];
            out_Sc    <= sc_diff[OUT_W-1:0];
            out_R0n   <= r0n_pipe2;
            out_sh    <= sh_reg;
            out_last  <= v_pipe2 && (tau_pipe2 == TAU_SCAN_MAX[7:0]);
        end
    end

endmodule
