// rtl/v2/ch01_step04_window_mul.v
// Window multiplier for Step 4: multiplies zero-mean sample x_zm (Q1.15)
// by Hanning window coefficient w_q15 (Q1.15) to produce windowed sample x_tilde (Q1.15).
// Features registered multiplier input and output matching DSP block / LPM_MULT pipeline.
`timescale 1ns/1ps

module ch01_step04_window_mul (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [15:0] x_in,     // Zero-mean sample (Q1.15)
    input  wire signed [15:0] w_in,     // Window coefficient from ROM (Q1.15, [0..32767])
    output reg                valid_out,
    output reg  signed [15:0] x_win     // Windowed sample (Q1.15)
);

    reg signed [31:0] prod;
    reg valid_d1;

    // Cycle 1: Registered product
    // (x * w + 16384) >> 15 gives round-to-nearest Q1.15
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prod     <= 32'sd0;
            valid_d1 <= 1'b0;
        end else begin
            valid_d1 <= valid_in;
            if (valid_in) begin
                prod <= x_in * w_in;
            end
        end
    end

    // Cycle 2: Rounding and output registered
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            x_win     <= 16'sh0000;
        end else begin
            valid_out <= valid_d1;
            if (valid_d1) begin
                // Round half LSB (+16384) and shift 15 bits
                x_win <= (prod + 32'sd16384) >>> 15;
            end
        end
    end

endmodule
