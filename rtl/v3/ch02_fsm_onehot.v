// ============================================================================
// File: rtl/v3/ch02_fsm_onehot.v
// Module: ch02_fsm_onehot
// Description:
//   5-state control FSM using explicit One-Hot state encoding:
//   - Number of states S = 5.
//   - State register width: 5 bits.
//   - State assignments:
//       S_IDLE  = 5'b00001 (bit 0)
//       S_LOAD  = 5'b00010 (bit 1)
//       S_CALC  = 5'b00100 (bit 2)
//       S_DRAIN = 5'b01000 (bit 3)
//       S_DONE  = 5'b10000 (bit 4)
//   - Next-state logic directly computes each bit from simple 2-input terms.
//   - Output strobes (load_en, calc_en, drain_en, done_pulse) are DIRECT WIRES
//     from state flip-flops with ZERO decoding gate delay.
//   - Synthesizable Verilog-2001, fully compatible with iverilog -g2012 -Wall.
// ============================================================================

`timescale 1ns/1ps

module ch02_fsm_onehot (
    input  wire       clk,
    input  wire       rst_n,

    // Control inputs
    input  wire       start,
    input  wire       load_done,
    input  wire       calc_done,
    input  wire       drain_done,

    // Status and strobe outputs
    output wire       busy,
    output wire       load_en,
    output wire       calc_en,
    output wire       drain_en,
    output wire       done_pulse,
    output reg  [2:0] state_num
);

    localparam [4:0] S_IDLE  = 5'b00001;
    localparam [4:0] S_LOAD  = 5'b00010;
    localparam [4:0] S_CALC  = 5'b00100;
    localparam [4:0] S_DRAIN = 5'b01000;
    localparam [4:0] S_DONE  = 5'b10000;

    reg [4:0] state_reg, state_next;

    // 1. State register (5 flip-flops)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_reg <= S_IDLE;
        end else begin
            state_reg <= state_next;
        end
    end

    // 2. One-hot next-state logic
    always @(*) begin
        state_next = 5'b00000;
        state_next[0] = (state_reg[0] & ~start) | state_reg[4];
        state_next[1] = (state_reg[0] & start)  | (state_reg[1] & ~load_done);
        state_next[2] = (state_reg[1] & load_done) | (state_reg[2] & ~calc_done);
        state_next[3] = (state_reg[2] & calc_done) | (state_reg[3] & ~drain_done);
        state_next[4] = (state_reg[3] & drain_done);
    end

    // 3. Moore outputs: single-bit wires directly from state flip-flops
    assign busy       = ~state_reg[0];
    assign load_en    = state_reg[1];
    assign calc_en    = state_reg[2];
    assign drain_en   = state_reg[3];
    assign done_pulse = state_reg[4];

    // Priority decode to numeric state number (0..4) for comparison
    always @(*) begin
        case (1'b1)
            state_reg[0]: state_num = 3'd0;
            state_reg[1]: state_num = 3'd1;
            state_reg[2]: state_num = 3'd2;
            state_reg[3]: state_num = 3'd3;
            state_reg[4]: state_num = 3'd4;
            default:      state_num = 3'd0;
        endcase
    end

endmodule
