// ============================================================================
// File: rtl/v3/ch09_radix2_div.v
// Module: ch09_radix2_div
// Description: Parameterized Sequential Radix-2 Restoring Divider
//              Computes unsigned integer quotient and remainder:
//                numer = quotient * denom + remain, with 0 <= remain < denom.
//              Latency: exactly WIDTHN clock cycles from start.
//              Throughput: 1 division per (WIDTHN + 1) cycles.
//              Area: compact (1 subtractor, shift registers, no DSP, 0 M10K).
// ============================================================================

`timescale 1ns / 1ps

module ch09_radix2_div #(
    parameter WIDTHN = 44,
    parameter WIDTHD = 34
) (
    input  wire              clk,
    input  wire              rst_n,

    // Control interface
    input  wire              start,
    output reg               busy,
    output reg               done,

    // Data interface
    input  wire [WIDTHN-1:0] numer,
    input  wire [WIDTHD-1:0] denom,
    output reg  [WIDTHN-1:0] quotient,
    output reg  [WIDTHD-1:0] remain
);

    localparam S_IDLE = 2'd0;
    localparam S_CALC = 2'd1;
    localparam S_DONE = 2'd2;

    reg [1:0]          state;
    reg [5:0]          count;
    reg [WIDTHN-1:0]   quo_reg;
    reg [WIDTHN-1:0]   rem_reg;
    reg [WIDTHD-1:0]   div_reg;

    // Combinational shift and subtract for restoring division step
    wire [WIDTHN:0]    next_rem = {rem_reg[WIDTHN-2:0], quo_reg[WIDTHN-1]};
    wire [WIDTHN:0]    ext_div  = {{(WIDTHN - WIDTHD + 1){1'b0}}, div_reg};
    wire [WIDTHN:0]    sub_diff = next_rem - ext_div;
    wire               sub_ok   = (next_rem >= ext_div);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= S_IDLE;
            busy     <= 1'b0;
            done     <= 1'b0;
            count    <= 6'd0;
            quo_reg  <= {WIDTHN{1'b0}};
            rem_reg  <= {WIDTHN{1'b0}};
            div_reg  <= {WIDTHD{1'b0}};
            quotient <= {WIDTHN{1'b0}};
            remain   <= {WIDTHD{1'b0}};
        end else begin
            done <= 1'b0;

            case (state)
                S_IDLE: begin
                    busy <= 1'b0;
                    if (start) begin
                        busy    <= 1'b1;
                        count   <= WIDTHN[5:0];
                        quo_reg <= numer;
                        rem_reg <= {WIDTHN{1'b0}};
                        div_reg <= denom;
                        state   <= S_CALC;
                    end
                end

                S_CALC: begin
                    // Perform 1 restoring division step
                    if (sub_ok) begin
                        rem_reg <= sub_diff[WIDTHN-1:0];
                        quo_reg <= {quo_reg[WIDTHN-2:0], 1'b1};
                    end else begin
                        rem_reg <= next_rem[WIDTHN-1:0];
                        quo_reg <= {quo_reg[WIDTHN-2:0], 1'b0};
                    end

                    count <= count - 6'd1;
                    if (count == 6'd1) begin
                        state <= S_DONE;
                    end
                end

                S_DONE: begin
                    busy     <= 1'b0;
                    done     <= 1'b1;
                    quotient <= quo_reg;
                    remain   <= rem_reg[WIDTHD-1:0];
                    state    <= S_IDLE;
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
