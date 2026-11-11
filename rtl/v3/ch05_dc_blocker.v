// ============================================================================
// File: rtl/v3/ch05_dc_blocker.v
// Module: ch05_dc_blocker
// Description:
//   Optional 1st-order IIR DC-blocker filter for Praat-style F0 estimation.
//   - Transfer function: H(z) = (1 - z^-1) / (1 - alpha * z^-1)
//   - Parameter: alpha = 1 - 2^-8 = 255/256 = 0.99609375 (SHIFT_R = 8)
//   - -3 dB cutoff frequency: ~9.93 Hz at fs = 16 kHz.
//   - Low-frequency voice loss: -0.059 dB at 75 Hz (pitch floor).
//   - Internal state: 36-bit signed (Q20.16) to eliminate overflow and limit cycles.
//   - Multiplier-free: uses right-shift by 8 bits and additions.
//   - Bypass switch: when bypass=1, passes data unmodified.
//   - Standard Verilog-2001 / IEEE 1800-2012, compiles clean under -Wall.
// ============================================================================

`timescale 1ns / 1ps

module ch05_dc_blocker #(
    parameter DATA_WIDTH = 16,
    parameter SHIFT_R    = 8
)(
    input  wire                         clk,
    input  wire                         rst_n,

    // Control
    input  wire                         bypass,

    // Stream Sink
    input  wire                         sink_valid,
    output wire                         sink_ready,
    input  wire signed [DATA_WIDTH-1:0] sink_data,

    // Stream Source
    output reg                          source_valid,
    input  wire                         source_ready,
    output reg  signed [DATA_WIDTH-1:0] source_data
);

    // Filter internal states
    reg  signed [DATA_WIDTH-1:0] x_prev;
    reg  signed [35:0]           w_acc; // Q20.16 format

    // Handshake: single-cycle pipeline, accepts when source is ready or idle
    assign sink_ready = source_ready || !source_valid;

    // Intermediate calculations
    wire signed [DATA_WIDTH:0]  dx = {sink_data[DATA_WIDTH-1], sink_data} -
                                     {x_prev[DATA_WIDTH-1], x_prev}; // 17-bit signed
    wire signed [35:0]          dx_scaled = {{3{dx[DATA_WIDTH]}}, dx, 16'd0}; // Scaled by 2^16
    wire signed [35:0]          w_feedback = w_acc - (w_acc >>> SHIFT_R);
    wire signed [35:0]          w_next = w_feedback + dx_scaled;

    // Rounding and saturation to int16
    wire signed [35:0]          w_rounded = w_next + 36'sh0000_8000;
    wire signed [19:0]          y_cand = w_rounded >>> 16;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_prev       <= {DATA_WIDTH{1'b0}};
            w_acc        <= 36'sd0;
            source_valid <= 1'b0;
            source_data  <= {DATA_WIDTH{1'b0}};
        end else if (sink_ready) begin
            if (sink_valid) begin
                source_valid <= 1'b1;
                if (bypass) begin
                    source_data <= sink_data;
                end else begin
                    x_prev <= sink_data;
                    w_acc  <= w_next;
                    // Symmetrical saturation to 16-bit signed range [-32768, 32767]
                    if (y_cand > 20'sd32767) begin
                        source_data <= 16'sh7FFF;
                    end else if (y_cand < -20'sd32768) begin
                        source_data <= -16'sh8000;
                    end else begin
                        source_data <= y_cand[DATA_WIDTH-1:0];
                    end
                end
            end else begin
                source_valid <= 1'b0;
            end
        end
    end

endmodule
