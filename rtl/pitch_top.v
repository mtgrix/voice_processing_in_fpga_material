// Top-level FSM: IDLE -> PHA1 -> PHA2 -> POST (+ EDGE for zero/DC/clip).
module pitch_top (
  input  wire clk, rst_n,
  input  wire signed [15:0] sample_q15,
  input  wire sample_valid,
  output reg [15:0] f0_q12_4,
  output reg f0_valid
);
endmodule
