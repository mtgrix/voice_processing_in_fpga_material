// rtl/v2/pll_clock_gen.v
// Model behavioral PLL + clock dividers and lock sequencer for Chapter 2.
// In silicon, Altera PLL / PLL Intel FPGA IP synthesizes the analog VCO.
// This module models the digital dividers (MCLK -> SCLK -> LRCK) and lock/reset sequencing.

`timescale 1ns/1ps

module pll_clock_gen #(
    parameter LOCK_CYCLES = 32  // Number of reference clock cycles before asserting locked
)(
    input  wire clk_ref,    // 50 MHz reference clock from crystal oscillator
    input  wire rst_n,      // Active-low asynchronous reset
    input  wire mclk_in,    // 12.288 MHz master clock (from PLL VCO in silicon / behavioral in sim)
    output reg  locked,     // PLL lock status
    output reg  sclk,       // 3.072 MHz I2S serial bit clock (MCLK / 4)
    output reg  lrck,       // 48 kHz word select / frame clock (SCLK / 64)
    output wire sclk_pulse  // 1-cycle enable pulse on SCLK rising edge
);

    // 1. Lock Sequencer: counts reference clock cycles after reset release
    reg [7:0] lock_cnt;
    always @(posedge clk_ref or negedge rst_n) begin
        if (!rst_n) begin
            lock_cnt <= 8'd0;
            locked   <= 1'b0;
        end else begin
            if (lock_cnt < LOCK_CYCLES) begin
                lock_cnt <= lock_cnt + 8'd1;
                locked   <= 1'b0;
            end else begin
                locked   <= 1'b1;
            end
        end
    end

    // 2. MCLK to SCLK divider: divide by 4 (toggle every 2 MCLK edges)
    // SCLK = 12.288 MHz / 4 = 3.072 MHz
    reg [1:0] sclk_cnt;
    always @(posedge mclk_in or negedge rst_n) begin
        if (!rst_n) begin
            sclk_cnt <= 2'd0;
            sclk     <= 1'b0;
        end else if (locked) begin
            if (sclk_cnt == 2'd1) begin
                sclk_cnt <= 2'd0;
                sclk     <= ~sclk;
            end else begin
                sclk_cnt <= sclk_cnt + 2'd1;
            end
        end else begin
            sclk_cnt <= 2'd0;
            sclk     <= 1'b0;
        end
    end

    // 3. SCLK to LRCK divider: divide by 64 (32 SCLK cycles Left, 32 SCLK cycles Right)
    // LRCK = 3.072 MHz / 64 = 48 kHz
    reg [5:0] lrck_cnt;
    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            lrck_cnt <= 6'd0;
            lrck     <= 1'b0; // 0 = Left channel in Philips I2S
        end else if (locked) begin
            if (lrck_cnt == 6'd31) begin
                lrck_cnt <= 6'd0;
                lrck     <= ~lrck;
            end else begin
                lrck_cnt <= lrck_cnt + 6'd1;
            end
        end else begin
            lrck_cnt <= 6'd0;
            lrck     <= 1'b0;
        end
    end

    assign sclk_pulse = (sclk_cnt == 2'd1) && (~sclk);

endmodule
