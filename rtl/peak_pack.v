// Argmax + silence/voicing gates + median-3 + Q12.4 pack (uint16 LE contract).
module peak_pack (
  input  wire clk, rst_n,
  input  wire signed [42:0] score,
  input  wire score_valid,
  output reg [15:0] f0_q12_4,
  output reg out_valid
);
endmodule
