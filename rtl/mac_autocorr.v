// Sequential MAC over tau in [26,214]; accum 41-bit signed. Bit-exact with lab_1_3_5.py.
module mac_autocorr (
  input  wire clk, rst_n, start,
  input  wire signed [15:0] xa, xb,
  output reg signed [40:0] acc,
  output reg done_tau
);
endmodule
