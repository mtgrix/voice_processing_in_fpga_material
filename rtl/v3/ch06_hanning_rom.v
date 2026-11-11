// rtl/v3/ch06_hanning_rom.v
// Synchronous 638-word x 16-bit ROM for Praat N+1 Hanning window (Q1.15 format)
// Compatible with Intel FPGA ROM: 1-PORT megafunction (UG-01068)
// Latency: 1 clock cycle (registered output q)

`timescale 1ns/1ps

module ch06_hanning_rom #(
    parameter integer WIDTH     = 16,
    parameter integer DEPTH     = 638,
    parameter integer ADDR_W    = 10,
    parameter         INIT_FILE = "rom/hanning638_q15.hex"
)(
    input  wire                 clk,
    input  wire [ADDR_W-1:0]    addr,
    output reg  [WIDTH-1:0]     q
);

    // ROM storage array
    reg [WIDTH-1:0] rom [0:DEPTH-1];

    // Initialize ROM contents from hex file
    initial begin
        if (INIT_FILE != "") begin
            $readmemh(INIT_FILE, rom);
        end
    end

    // Synchronous read (1-cycle latency, matching Intel ROM: 1-PORT outdata_reg_a = "CLOCK0")
    always @(posedge clk) begin
        q <= rom[addr];
    end

endmodule
