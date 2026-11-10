// rtl/v2/ch01_step07_parabolic.v
// Parabolic interpolation module for Step 7.
// Fits parabola through three points (r_minus, r_peak, r_plus):
// y = a*x^2 + b*x + c with peak offset delta = -b / (2a) = (r_minus - r_plus) / (2*(r_minus - 2*r_peak + r_plus)).
// Prepares signed numerator and positive denominator for subsequent division stage.
`timescale 1ns/1ps

module ch01_step07_parabolic (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [15:0] r_minus,   // r[tau* - 1]
    input  wire signed [15:0] r_peak,    // r[tau*]
    input  wire signed [15:0] r_plus,    // r[tau* + 1]
    output reg                valid_out,
    output reg  signed [16:0] num_diff,  // r_minus - r_plus
    output reg         [16:0] den_curv   // -2 * (r_minus - 2*r_peak + r_plus) (strictly positive for concave peak)
);

    wire signed [16:0] diff = {r_minus[15], r_minus} - {r_plus[15], r_plus};
    wire signed [17:0] two_r_peak = {r_peak[15], r_peak, 1'b0};
    wire signed [18:0] sum_ends   = {r_minus[15], r_minus[15], r_minus} + {r_plus[15], r_plus[15], r_plus};
    wire signed [18:0] curv       = sum_ends - {two_r_peak[17], two_r_peak}; // r_minus - 2*r_peak + r_plus (< 0)

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            num_diff  <= 17'sd0;
            den_curv  <= 17'd0;
        end else if (valid_in) begin
            valid_out <= 1'b1;
            num_diff  <= diff;
            // Negate and double to form strictly positive denominator: -2 * curv
            if (curv < 0) begin
                den_curv <= (-curv) << 1;
            end else begin
                den_curv <= 17'd1; // Safety fallback against division by zero
            end
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
