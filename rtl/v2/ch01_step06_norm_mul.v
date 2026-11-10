// rtl/v2/ch01_step06_norm_mul.v
// Normalization multiplier for Step 6: multiplies R_x[tau] by C[tau] (Q3.13 format)
// to produce compensated score S[tau] = (R_x[tau] * C[tau] + 4096) >> 13.
`timescale 1ns/1ps

module ch01_step06_norm_mul (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               valid_in,
    input  wire signed [31:0] r_tau_in,    // Truncated / saturated 32-bit ACF
    input  wire signed [15:0] c_tau_q13,   // Q3.13 normalization factor (e.g., 8192 for 1.0)
    output reg                valid_out,
    output reg  signed [47:0] score_out    // S[tau] = R_x[tau] * C[tau]
);

    reg signed [47:0] prod;
    reg valid_d1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prod      <= 48'sd0;
            valid_d1  <= 1'b0;
            valid_out <= 1'b0;
            score_out <= 48'sd0;
        end else begin
            valid_d1  <= valid_in;
            valid_out <= valid_d1;

            if (valid_in) begin
                // Product in Q.13
                prod <= r_tau_in * c_tau_q13;
            end

            if (valid_d1) begin
                // Round half LSB (+4096) and shift 13 bits
                score_out <= (prod + 48'sd4096) >>> 13;
            end
        end
    end

endmodule
