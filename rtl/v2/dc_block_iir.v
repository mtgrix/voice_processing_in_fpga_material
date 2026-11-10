// rtl/v2/dc_block_iir.v
// Complete, synthesizable first-order IIR DC-Blocker filter with 32-bit accumulator.
// Transfer function: H(z) = (1 - z^-1) / (1 - alpha * z^-1) with alpha = 1 - 2^-8 = 0.99609375.
// Bit-exact and cycle-accurate with Python twin dc_blocker_q15.
// Avalon-ST streaming interface with valid/ready backpressure handshake.

`timescale 1ns/1ps

module dc_block_iir (
    input  wire                 clk,        // System clock (e.g. 50 MHz)
    input  wire                 rst_n,      // Active-low asynchronous reset
    input  wire                 in_valid,   // Avalon-ST input data valid
    output wire                 in_ready,   // Avalon-ST ready to accept input
    input  wire signed [15:0]   x_in,       // 16-bit signed audio sample (Q1.15)
    output reg                  out_valid,  // Avalon-ST output data valid
    input  wire                 out_ready,  // Avalon-ST downstream ready
    output reg  signed [15:0]   y_out       // 16-bit signed filtered output (Q1.15)
);

    // 1. Avalon-ST ready generation: ready if downstream accepts or output buffer is empty
    assign in_ready = out_ready | ~out_valid;

    // 2. State registers
    reg signed [15:0] x_z1;     // Previous input sample x[n-1]
    reg signed [31:0] y_acc;    // 32-bit accumulator reservoir (Q2.30 format)

    // 3. Difference computation with 15-bit left shift into Q2.30
    // x_in and x_z1 are Q1.15 (1 sign bit + 15 fractional bits).
    // Appending 15 zeros aligns them to Q2.30 with 15 LSBs of fractional precision.
    wire signed [31:0] x_scaled    = $signed({x_in, 15'b0});
    wire signed [31:0] x_z1_scaled = $signed({x_z1, 15'b0});
    wire signed [31:0] x_delta     = x_scaled - x_z1_scaled;

    // 4. IIR feedback update: y_acc[n] = y_acc[n-1] + x_delta - (y_acc[n-1] >>> 8)
    // Arithmetic right shift >>> 8 implements alpha = 1 - 2^-8 = 255/256
    wire signed [31:0] y_next  = y_acc + x_delta - (y_acc >>> 8);
    wire signed [31:0] y_shift = y_next >>> 15;

    // 5. Symmetric 16-bit saturation to prevent overflow clicks: clamp to [-32768, +32767]
    function automatic signed [15:0] sat16(input signed [31:0] val);
        begin
            if (val > 32'sd32767)
                sat16 = 16'sd32767;
            else if (val < -32'sd32768)
                sat16 = -16'sd32768;
            else
                sat16 = val[15:0];
        end
    endfunction

    // 6. Sequential datapath update
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_z1      <= 16'sd0;
            y_acc     <= 32'sd0;
            y_out     <= 16'sd0;
            out_valid <= 1'b0;
        end else begin
            // Handshake occurs when both valid and ready are high
            if (in_valid && in_ready) begin
                y_acc     <= y_next;
                x_z1      <= x_in;
                y_out     <= sat16(y_shift);
                out_valid <= 1'b1;
            end else if (out_valid && out_ready) begin
                // Downstream consumed the output and no new input arrived
                out_valid <= 1'b0;
            end
        end
    end

endmodule
