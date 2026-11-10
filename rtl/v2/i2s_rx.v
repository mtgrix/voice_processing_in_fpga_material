// rtl/v2/i2s_rx.v
// Complete, synthesizable I2S Receiver for Wolfson WM8731 codec (Philips format).
// Receives serial PCM audio data, extracts 16-bit Q1.15 Left-channel samples.
// Operates synchronously in the SCLK domain (~3.072 MHz).
// Follows Philips I2S standard: exactly 1 SCLK delay after WS edge before MSB.

`timescale 1ns/1ps

module i2s_rx #(
    parameter W = 16  // Bit width of PCM audio sample (Q1.15)
)(
    input  wire                 sclk,         // I2S bit clock (3.072 MHz)
    input  wire                 rst_n,        // Active-low asynchronous reset
    input  wire                 ws,           // Word select / LRCK (48 kHz: 0=Left, 1=Right)
    input  wire                 sdat,         // Serial data input from codec ADC
    output reg  signed [W-1:0]  sample_left,  // Extracted 16-bit signed sample
    output reg                  sample_valid  // 1-cycle active-high strobe when sample is ready
);

    // 1. Edge detection for Word Select (WS)
    // Transmitter drives WS and SDAT on falling edge of SCLK; receiver samples on rising edge.
    reg ws_d;
    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            ws_d <= 1'b1;
        end else begin
            ws_d <= ws;
        end
    end

    // Falling edge of WS signals the start of the Left audio frame in Philips I2S
    wire ws_fall = (ws_d == 1'b1) && (ws == 1'b0);

    // 2. FSM States
    localparam STATE_WAIT_WS  = 2'd0;
    localparam STATE_SHIFT    = 2'd1;
    localparam STATE_IGNORE   = 2'd2;

    reg [1:0] state;
    reg [4:0] bit_cnt;
    reg [W-1:0] shreg;

    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= STATE_WAIT_WS;
            bit_cnt      <= 5'd0;
            shreg        <= {W{1'b0}};
            sample_left  <= {W{1'b0}};
            sample_valid <= 1'b0;
        end else begin
            sample_valid <= 1'b0; // Default: 1-cycle strobe

            case (state)
                STATE_WAIT_WS: begin
                    if (ws_fall) begin
                        // In Philips I2S, the rising edge right after WS transition is the 1-bit delay.
                        // MSB will be present on SDAT at the next rising edge.
                        state   <= STATE_SHIFT;
                        bit_cnt <= 5'd0;
                    end
                end

                STATE_SHIFT: begin
                    shreg <= {shreg[W-2:0], sdat};
                    if (bit_cnt == (W - 1)) begin
                        // All 16 bits captured (MSB at bit_cnt 0, LSB at bit_cnt 15)
                        sample_left  <= {shreg[W-2:0], sdat};
                        sample_valid <= 1'b1;
                        state        <= STATE_IGNORE;
                    end else begin
                        bit_cnt <= bit_cnt + 5'd1;
                    end
                end

                STATE_IGNORE: begin
                    // Ignore remaining bits of Left slot (e.g. 16 padding bits in 32-bit slot)
                    // and entire Right channel until next Left frame start.
                    if (ws_fall) begin
                        state   <= STATE_SHIFT;
                        bit_cnt <= 5'd0;
                    end
                end

                default: state <= STATE_WAIT_WS;
            endcase
        end
    end

endmodule
