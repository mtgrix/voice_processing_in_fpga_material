// IIR DC-block: y[n]=x[n]-x[n-1]+alpha*y[n-1], alpha=1-1/256 (Q1.15).
module dc_block_iir (
  input  wire clk, rst_n, in_valid,
  input  wire signed [15:0] x_q15,
  output reg  signed [15:0] y_q15,
  output reg  out_valid
);
endmodule
