// rtl/v2/ch01_step09_octave_score.v
// Octave cost weighting module for Step 9:
// Multiplies candidate score by octave factor (Q1.15) to favor fundamental pitch over sub-harmonics (F0/2).
`timescale 1ns/1ps

module ch01_step09_octave_score (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [31:0] score_in,       // Raw candidate score
    input  wire signed [15:0] octave_factor,  // Q1.15 weighting factor from ROM <= 32767
    output reg                valid_out,
    output reg  signed [31:0] score_penalized
);

    reg signed [47:0] prod;
    reg valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prod            <= 48'sd0;
            valid_d1        <= 1'b0;
            valid_out       <= 1'b0;
            score_penalized <= 32'sd0;
        end else begin
            valid_d1  <= valid_in;
            valid_out <= valid_d1;

            if (valid_in) begin
                prod <= score_in * octave_factor;
            end

            if (valid_d1) begin
                score_penalized <= (prod + 48'sd16384) >>> 15;
            end
        end
    end

endmodule
