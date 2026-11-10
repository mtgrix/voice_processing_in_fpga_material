// rtl/i2s_rx.v
// Complete, synthesizable I2S Receiver matching rtl/v2/i2s_rx.v.
// Maps WM8731 BCLK/LRCK/DOUT -> Q1.15 sample + sample_valid.

`timescale 1ns/1ps

module i2s_rx #(parameter W=16) (
  input  wire clk, rst_n, bclk, lrck, din,
  output wire signed [W-1:0] sample_q15,
  output wire sample_valid
);
  i2s_rx_core #(.W(W)) u_core (
    .sclk(bclk),
    .rst_n(rst_n),
    .ws(lrck),
    .sdat(din),
    .sample_left(sample_q15),
    .sample_valid(sample_valid)
  );
endmodule

module i2s_rx_core #(
    parameter W = 16
)(
    input  wire                 sclk,
    input  wire                 rst_n,
    input  wire                 ws,
    input  wire                 sdat,
    output reg  signed [W-1:0]  sample_left,
    output reg                  sample_valid
);
    reg ws_d;
    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            ws_d <= 1'b1;
        end else begin
            ws_d <= ws;
        end
    end

    wire ws_fall = (ws_d == 1'b1) && (ws == 1'b0);

    localparam S_WAIT = 2'd0, S_SHIFT = 2'd1, S_IGN = 2'd2;
    reg [1:0] state;
    reg [4:0] bit_cnt;
    reg [W-1:0] shreg;

    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= S_WAIT;
            bit_cnt      <= 5'd0;
            shreg        <= {W{1'b0}};
            sample_left  <= {W{1'b0}};
            sample_valid <= 1'b0;
        end else begin
            sample_valid <= 1'b0;
            case (state)
                S_WAIT: if (ws_fall) begin
                    state   <= S_SHIFT;
                    bit_cnt <= 5'd0;
                end
                S_SHIFT: begin
                    shreg <= {shreg[W-2:0], sdat};
                    if (bit_cnt == (W - 1)) begin
                        sample_left  <= {shreg[W-2:0], sdat};
                        sample_valid <= 1'b1;
                        state        <= S_IGN;
                    end else begin
                        bit_cnt <= bit_cnt + 5'd1;
                    end
                end
                S_IGN: if (ws_fall) begin
                    state   <= S_SHIFT;
                    bit_cnt <= 5'd0;
                end
                default: state <= S_WAIT;
            endcase
        end
    end
endmodule
