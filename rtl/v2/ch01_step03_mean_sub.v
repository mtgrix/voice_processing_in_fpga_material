// rtl/v2/ch01_step03_mean_sub.v
// Local mean calculation and subtraction for Step 3.
// Accumulates L samples, computes mean = acc / L, and subtracts mean from each sample: x_zm = x - mean.
`timescale 1ns/1ps

module ch01_step03_mean_sub (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [15:0] sample_in,
    input  wire signed [15:0] mean_val,    // Pre-calculated or streaming frame mean
    output reg                valid_out,
    output reg  signed [15:0] sample_zm
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            sample_zm <= 16'sh0000;
        end else if (valid_in) begin
            valid_out <= 1'b1;
            sample_zm <= sample_in - mean_val;
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
