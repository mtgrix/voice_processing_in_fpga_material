// I2S RX stub — expand per Phần C.2 (default teaching path).
// Maps WM8731 BCLK/LRCK/DOUT -> Q1.15 sample + FIFO write.
module i2s_rx #(parameter W=16) (
  input  wire clk, rst_n, bclk, lrck, din,
  output reg signed [W-1:0] sample_q15,
  output reg sample_valid
);
  // Collect W bits on BCLK edges; assert sample_valid one cycle per word.
endmodule
