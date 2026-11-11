// rtl/v3/ch08_ck_rom.v
// 256x32-bit Synchronous Single-Port ROM for C[tau] (bits [31:16]) and K[tau] (bits [15:0])
// Fits in exactly 1 M10K Embedded Memory block on Intel Cyclone V (256x40 configuration)
// Initialized from golden_v2/rom/ck_rom.hex (189 words used, address = tau - 26)
//
// Document citations:
//   - Embedded Memory (RAM: 1-PORT, RAM: 2-PORT, ROM: 1-PORT, and ROM: 2-PORT) User Guide (UG-01068)
//   - Cyclone V Device Handbook, Volume 1 (CV-52003), Chapter 3: Embedded Memory Blocks (Table 3-1)

`timescale 1ns/1ps

module ch08_ck_rom #(
    parameter integer ADDR_W    = 8,
    parameter integer DATA_W    = 32,
    parameter integer DEPTH     = 256,
    parameter         INIT_FILE = "golden_v2/rom/ck_rom.hex"
) (
    input  wire              clk,
    input  wire [ADDR_W-1:0] addr,
    output reg  [DATA_W-1:0] q
);

    // Inferred synchronous single-port ROM
    reg [DATA_W-1:0] rom [0:DEPTH-1];

    initial begin
        $readmemh(INIT_FILE, rom);
    end

    // Registered read (1 cycle read latency)
    always @(posedge clk) begin
        q <= rom[addr];
    end

endmodule
