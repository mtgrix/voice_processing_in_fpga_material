// rtl/v2/ch01_step10_voicing_gate.v
// Silence & Voicing gate for Step 10: pure integer cross-multiplication without division or DSP.
// Silence gate: r0 * 10000 < 9 * ref_energy (equivalent to r0/ref_energy < 0.03^2 = 0.0009)
// Voicing gate: best_score * 100 >= 45 * r0  (equivalent to best_score/r0 >= 0.45)
// best_score = S[tau*] = R[tau*] * C[tau*] (has same energy units as r0, NOT dimensionless).
`timescale 1ns/1ps

module ch01_step10_voicing_gate (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        eval_valid,
    input  wire [31:0] r0_energy,       // Energy at tau=0 (frame energy)
    input  wire [31:0] ref_energy,      // Reference peak energy across utterance
    input  wire [47:0] best_score,      // C-compensated peak lag energy S[tau*]
    input  wire [15:0] f0_candidate,    // Interpolated F0 in Q12.4
    output reg         done_valid,
    output reg         is_voiced,
    output reg  [15:0] f0_gated         // Output F0: equals f0_candidate if voiced, 0 if unvoiced/silence
);

    // Cross-multiplications
    wire [63:0] r0_x_10000     = r0_energy * 64'd10000;
    wire [63:0] ref_x_9        = ref_energy * 64'd9;
    wire [63:0] score_x_100    = best_score[47:0] * 64'd100;
    wire [63:0] r0_x_45        = r0_energy * 64'd45;

    wire silence_cond = (r0_x_10000 < ref_x_9);
    wire voicing_cond = (score_x_100 >= r0_x_45);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            done_valid <= 1'b0;
            is_voiced  <= 1'b0;
            f0_gated   <= 16'd0;
        end else if (eval_valid) begin
            done_valid <= 1'b1;
            if (silence_cond) begin
                is_voiced <= 1'b0;
                f0_gated  <= 16'd0;
            end else if (voicing_cond) begin
                is_voiced <= 1'b1;
                f0_gated  <= f0_candidate;
            end else begin
                is_voiced <= 1'b0;
                f0_gated  <= 16'd0;
            end
        end else begin
            done_valid <= 1'b0;
        end
    end

endmodule
