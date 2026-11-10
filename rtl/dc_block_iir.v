// rtl/dc_block_iir.v
// Complete, synthesizable IIR DC-Blocker matching rtl/v2/dc_block_iir.v.
// y[n] = x[n] - x[n-1] + alpha * y[n-1], alpha = 1 - 2^-8.

`timescale 1ns/1ps

module dc_block_iir (
  input  wire clk, rst_n, in_valid,
  input  wire signed [15:0] x_q15,
  output reg  signed [15:0] y_q15,
  output reg  out_valid
);
  reg signed [15:0] x_z1;
  reg signed [31:0] y_acc;

  wire signed [31:0] x_scaled    = $signed({x_q15, 15'b0});
  wire signed [31:0] x_z1_scaled = $signed({x_z1, 15'b0});
  wire signed [31:0] x_delta     = x_scaled - x_z1_scaled;
  wire signed [31:0] y_next      = y_acc + x_delta - (y_acc >>> 8);
  wire signed [31:0] y_shift     = y_next >>> 15;

  function automatic signed [15:0] sat16(input signed [31:0] val);
    begin
      if (val > 32'sd32767)       sat16 = 16'sd32767;
      else if (val < -32'sd32768) sat16 = -16'sd32768;
      else                        sat16 = val[15:0];
    end
  endfunction

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      x_z1      <= 16'sd0;
      y_acc     <= 32'sd0;
      y_q15     <= 16'sd0;
      out_valid <= 1'b0;
    end else if (in_valid) begin
      y_acc     <= y_next;
      x_z1      <= x_q15;
      y_q15     <= sat16(y_shift);
      out_valid <= 1'b1;
    end else begin
      out_valid <= 1'b0;
    end
  end
endmodule
