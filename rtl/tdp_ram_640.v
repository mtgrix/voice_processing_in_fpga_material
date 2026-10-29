// True dual-port 640x16 inferred M10K. Port A: addr_a, Port B: addr_b.
module tdp_ram_640 (
  input  wire clk,
  input  wire we_a, input wire [9:0] addr_a, addr_b,
  input  wire signed [15:0] din_a,
  output reg  signed [15:0] dout_a, dout_b
);
  reg signed [15:0] mem [0:639];
  always @(posedge clk) begin
    if (we_a) mem[addr_a] <= din_a;
    dout_a <= mem[addr_a];
    dout_b <= mem[addr_b];
  end
endmodule
