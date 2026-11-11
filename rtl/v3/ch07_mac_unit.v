// rtl/v3/ch07_mac_unit.v
// Core 17x17-bit Signed Multiplier-Accumulator Unit (Option 2: Registered Inputs)
// Matches Intel ALTERA_MULT_ADD IP Core in Cyclone V Variable Precision DSP
//
// Pipeline stages:
//   Stage 1: Input register bank (a_r, b_r, v_r, sload_r, last_r) - utilizes DSP input registers (0 ALMs)
//   Combinational: 17x17-bit signed multiplier -> 34-bit signed product p
//   Stage 2: 48-bit accumulator register (acc) with synchronous load (sload_r) and sign-extension
//   Latency: 2 cycles from DSP input ports (a, b) to accumulator output (acc, out_valid)
//
// Document citations:
//   - Cyclone V Device Handbook, Vol 1 (CV-52003), Chapter 5: Variable Precision DSP Blocks
//   - Integer Arithmetic IP Cores User Guide (UG-01069): ALTERA_MULT_ADD

`timescale 1ns/1ps

module ch07_mac_unit #(
    parameter integer DATA_W   = 17,  // xw bit-width (signed)
    parameter integer PROD_W   = 34,  // Product bit-width (signed)
    parameter integer ACC_W    = 48   // Accumulator bit-width (signed, holds >= 43 bits)
) (
    input  wire                   clk,
    input  wire                   rst_n,      // Active-low synchronous/asynchronous reset
    input  wire                   in_valid,   // 1 when input pair (a, b) is valid
    input  wire                   in_sload,   // Synchronous load: 1 for first pair of each lag
    input  wire                   in_last,    // 1 for final pair of each lag
    input  wire signed [DATA_W-1:0] a,        // Sample xw[n]
    input  wire signed [DATA_W-1:0] b,        // Sample xw[n+tau]
    output reg  signed [ACC_W-1:0]  acc,      // Running / completed accumulation sum
    output reg                    out_valid   // 1 on the exact cycle when acc holds final R[tau]
);

    // Stage 1: Input Register Bank (Cyclone V DSP input registers)
    reg signed [DATA_W-1:0] a_r, b_r;
    reg                     v_r, sload_r, last_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_r     <= {DATA_W{1'b0}};
            b_r     <= {DATA_W{1'b0}};
            v_r     <= 1'b0;
            sload_r <= 1'b0;
            last_r  <= 1'b0;
        end else begin
            a_r     <= a;
            b_r     <= b;
            v_r     <= in_valid;
            sload_r <= in_sload;
            last_r  <= in_last;
        end
    end

    // Combinational 17x17 multiplier in DSP silicon (p is 34-bit signed)
    wire signed [PROD_W-1:0] p = a_r * b_r;

    // Explicit sign-extension of 34-bit product to 48-bit accumulator
    localparam integer EXT_W = ACC_W - PROD_W; // 48 - 34 = 14 bits
    wire signed [ACC_W-1:0] p_ext = {{EXT_W{p[PROD_W-1]}}, p};

    // Stage 2: 48-bit Accumulator Register (Cyclone V 64-bit DSP accumulator)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acc       <= {ACC_W{1'b0}};
            out_valid <= 1'b0;
        end else begin
            if (v_r) begin
                acc <= sload_r ? p_ext : acc + p_ext;
            end
            out_valid <= v_r & last_r;
        end
    end

endmodule
