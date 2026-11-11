// rtl/v3/ch06_hanning_window.v
// Module applying Praat N+1 Hanning window (Q1.15) to 17-bit signed audio difference samples d = x - mean
// Features:
// 1. Synchronous ROM lookup (1-cycle read latency) matching Intel ROM: 1-PORT
// 2. Sample delay matching (d_r1 matches w_q)
// 3. 17x17-bit signed multiplier with pipeline register (1-cycle latency) matching Intel LPM_MULT
// 4. Convergent rounding adder: (p + 2^14) >> 15 producing 17-bit signed xw
// 5. Real-time LocalPeak (LP = max|xw[j]| for j in [212, 425]) detection for Praat voicing threshold
// Total latency: 3 clock cycles from in_valid to out_valid

`timescale 1ns/1ps

module ch06_hanning_window #(
    parameter integer DATA_W    = 17,                        // 17-bit signed (d = x - mean)
    parameter integer ROM_W     = 16,                        // 16-bit Q1.15 window coefficient
    parameter integer PROD_W    = 34,                        // 34-bit signed product (17x17)
    parameter integer N_SAMPLES = 638,                       // Window length N = 638
    parameter integer LP_FIRST  = 212,                       // First sample of LocalPeak window (0-based)
    parameter integer LP_LAST   = 425,                       // Last sample of LocalPeak window (0-based)
    parameter         INIT_FILE = "rom/hanning638_q15.hex"
)(
    input  wire                     clk,
    input  wire                     rst_n,

    // Control interface
    input  wire                     start,                   // 1-cycle pulse to start a new 638-sample frame
    output reg                      busy,                    // High during frame processing

    // Streaming sample input (d = x - mean)
    input  wire                     in_valid,
    input  wire signed [DATA_W-1:0] in_d,

    // Streaming windowed output (xw)
    output reg                      out_valid,
    output reg  signed [DATA_W-1:0] out_xw,

    // Frame completion and LocalPeak measurement
    output reg                      out_done,                // 1-cycle pulse when sample 637 completes
    output reg         [15:0]       out_lp                   // max |xw[j]| for j in [212, 425]
);

    // -------------------------------------------------------------------------
    // Internal counters and registers
    // -------------------------------------------------------------------------
    reg  [9:0]              sample_cnt;
    wire [9:0]              rom_addr = sample_cnt;
    wire [ROM_W-1:0]        w_q;

    // Pipeline Stage 1 registers (Sample delay to match ROM read latency)
    reg signed [DATA_W-1:0] d_r1;
    reg                     v_r1;
    reg  [9:0]              idx_r1;

    // Pipeline Stage 2 registers (Multiplier output pipeline register)
    reg signed [PROD_W-1:0] prod_r2;
    reg                     v_r2;
    reg  [9:0]              idx_r2;

    // Local peak tracking accumulator
    reg  [15:0]             lp_reg;

    // -------------------------------------------------------------------------
    // Synchronous ROM instance (1-cycle read latency)
    // -------------------------------------------------------------------------
    ch06_hanning_rom #(
        .WIDTH     (ROM_W),
        .DEPTH     (N_SAMPLES),
        .ADDR_W    (10),
        .INIT_FILE (INIT_FILE)
    ) u_rom (
        .clk  (clk),
        .addr (rom_addr),
        .q    (w_q)
    );

    // -------------------------------------------------------------------------
    // Stage 0 -> Stage 1: Sample issue, address generation and delay matching
    // -------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_cnt <= 10'd0;
            d_r1       <= {DATA_W{1'b0}};
            v_r1       <= 1'b0;
            idx_r1     <= 10'd0;
            busy       <= 1'b0;
        end else begin
            if (start) begin
                sample_cnt <= 10'd0;
                busy       <= 1'b1;
            end

            if (in_valid && (busy || start)) begin
                d_r1   <= in_d;
                v_r1   <= 1'b1;
                idx_r1 <= start ? 10'd0 : sample_cnt;

                if ((start ? 10'd0 : sample_cnt) == N_SAMPLES - 1) begin
                    sample_cnt <= 10'd0;
                end else begin
                    sample_cnt <= (start ? 10'd0 : sample_cnt) + 10'd1;
                end
            end else begin
                v_r1 <= 1'b0;
            end
        end
    end

    // -------------------------------------------------------------------------
    // Stage 1 -> Stage 2: 17x17 signed multiplication with pipeline register
    // -------------------------------------------------------------------------
    // w_q is unsigned Q1.15 in [0, 32767]. MSB is 0, so prepending 1'b0 extends
    // to 17-bit positive signed, matching LPM_REPRESENTATION = "SIGNED".
    wire signed [16:0] w_signed = {1'b0, w_q};
    wire signed [PROD_W-1:0] prod_comb = d_r1 * w_signed;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prod_r2 <= {PROD_W{1'b0}};
            v_r2    <= 1'b0;
            idx_r2  <= 10'd0;
        end else begin
            prod_r2 <= prod_comb;
            v_r2    <= v_r1;
            idx_r2  <= idx_r1;
        end
    end

    // -------------------------------------------------------------------------
    // Stage 2 -> Stage 3: Rounding adder, output registers, LocalPeak detection
    // -------------------------------------------------------------------------
    // Rounding formula: (p + 2^14) >> 15
    wire signed [34:0] p_round = {prod_r2[33], prod_r2} + 35'sd16384;
    wire signed [16:0] xw_comb = p_round[31:15];
    wire [15:0] abs_xw = (xw_comb < 0) ? -xw_comb[15:0] : xw_comb[15:0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_valid <= 1'b0;
            out_xw    <= {DATA_W{1'b0}};
            out_done  <= 1'b0;
            out_lp    <= 16'd0;
            lp_reg    <= 16'd0;
        end else begin
            if (start) begin
                lp_reg   <= 16'd0;
                out_done <= 1'b0;
            end

            out_valid <= v_r2;

            if (v_r2) begin
                out_xw <= xw_comb;

                // Track peak in range [LP_FIRST, LP_LAST]
                if (idx_r2 >= LP_FIRST && idx_r2 <= LP_LAST) begin
                    if (abs_xw > lp_reg) begin
                        lp_reg <= abs_xw;
                    end
                end

                // Frame complete when last sample (637) exits pipeline
                if (idx_r2 == N_SAMPLES - 1) begin
                    out_done <= 1'b1;
                    out_lp   <= lp_reg;
                    busy     <= 1'b0;
                end else begin
                    out_done <= 1'b0;
                end
            end else begin
                out_done <= 1'b0;
            end
        end
    end

endmodule
