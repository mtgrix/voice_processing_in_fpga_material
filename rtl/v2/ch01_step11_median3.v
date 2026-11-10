// rtl/v2/ch01_step11_median3.v
// Canonical 3-point Median Filter for Step 11.
// Computes median(f_in, d0, d1) with NO extra m_reg.
// The output corresponds to the center frame of the 3-frame window,
// introducing an inherent group delay of 1 frame (10 ms).
`timescale 1ns/1ps

module ch01_step11_median3 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        valid_in,
    input  wire [15:0] f_in,        // Raw input F0 in Q12.4
    output reg         valid_out,
    output reg  [15:0] f_out        // Filtered F0 in Q12.4
);

    reg [15:0] d0, d1;

    // 3-input median function:
    // median(a,b,c) = a > b ? (b > c ? b : (a > c ? c : a))
    //                       : (a > c ? a : (b > c ? c : b))
    function [15:0] get_median;
        input [15:0] a, b, c;
        begin
            if (a > b) begin
                if (b > c)      get_median = b;
                else if (a > c) get_median = c;
                else            get_median = a;
            end else begin
                if (a > c)      get_median = a;
                else if (b > c) get_median = c;
                else            get_median = b;
            end
        end
    endfunction

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            d0        <= 16'd0;
            d1        <= 16'd0;
            valid_out <= 1'b0;
            f_out     <= 16'd0;
        end else if (valid_in) begin
            d0        <= f_in;
            d1        <= d0;
            valid_out <= 1'b1;
            f_out     <= get_median(f_in, d0, d1);
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
