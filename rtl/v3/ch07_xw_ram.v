// rtl/v3/ch07_xw_ram.v
// True Dual-Port Sample RAM for windowed frame samples xw[0..637]
// Inferred dual-port synchronous RAM mapping to 2x Intel M10K blocks in Cyclone V
//
// Configuration details:
//   - Depth: 638 words, Data width: 17 bits
//   - Port A: Writes incoming samples during frame loading, reads xw[n] during MAC
//   - Port B: Reads xw[n+tau] during MAC calculation
//   - Read latency: 1 clock cycle (registered address, unregistered data output)
//   - Read-during-write: DONT_CARE (read and write phases are strictly disjoint)
//
// Document citations:
//   - Cyclone V Device Handbook, Vol 1 (CV-52003), Chapter 3: Embedded Memory Blocks (Table 3-1)
//   - Embedded Memory (RAM: 1-PORT, RAM: 2-PORT, ...) User Guide (UG-01068)

`timescale 1ns/1ps

module ch07_xw_ram #(
    parameter integer DATA_W = 17,
    parameter integer DEPTH  = 638,
    parameter integer ADDR_W = 10
) (
    input  wire                   clk,
    
    // Port A: Read/Write
    input  wire                   we_a,
    input  wire [ADDR_W-1:0]      addr_a,
    input  wire signed [DATA_W-1:0] din_a,
    output reg  signed [DATA_W-1:0] dout_a,

    // Port B: Read-only (we_b tied low in standard MAC operation)
    input  wire                   we_b,
    input  wire [ADDR_W-1:0]      addr_b,
    input  wire signed [DATA_W-1:0] din_b,
    output reg  signed [DATA_W-1:0] dout_b
);

    // RAM array: 638 words of 17-bit signed samples
    // Quartus infers 2x M10K blocks (1024x10 configuration) because depth 638 > 512
    reg signed [DATA_W-1:0] mem [0:DEPTH-1];

    // Port A synchronous read/write
    always @(posedge clk) begin
        if (we_a) begin
            mem[addr_a] <= din_a;
        end
        dout_a <= mem[addr_a];
    end

    // Port B synchronous read/write
    always @(posedge clk) begin
        if (we_b) begin
            mem[addr_b] <= din_b;
        end
        dout_b <= mem[addr_b];
    end

endmodule
