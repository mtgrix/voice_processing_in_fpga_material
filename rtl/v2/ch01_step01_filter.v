// rtl/v2/ch01_step01_filter.v
// Streaming anti-aliasing pre-filter alternative for Step 1 on FPGA.
// Implements a 3-tap symmetric FIR filter with coefficients [1, 2, 1] / 4
// to attenuate high frequencies near Nyquist in real-time streaming mode.
`timescale 1ns/1ps

module ch01_step01_filter (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [15:0] data_in,
    output reg                valid_out,
    output reg  signed [15:0] data_out
);

    reg signed [15:0] d1, d2;

    // Filter equation: y[n] = (x[n] + 2*x[n-1] + x[n-2]) / 4
    // Fully attenuates Nyquist frequency (at f_s/2, x = [1, -1, 1, -1] -> 1 - 2 + 1 = 0)
    wire signed [17:0] sum = {data_in[15], data_in[15], data_in} +
                             {d1[15], d1, 1'b0} +
                             {d2[15], d2[15], d2};

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            d1        <= 16'sh0000;
            d2        <= 16'sh0000;
            valid_out <= 1'b0;
            data_out  <= 16'sh0000;
        end else if (valid_in) begin
            d1        <= data_in;
            d2        <= d1;
            valid_out <= 1'b1;
            data_out  <= sum[17:2]; // Divide by 4
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
