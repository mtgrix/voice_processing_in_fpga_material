// ============================================================================
// File: rtl/v3/ch02_fsm_binary.v
// Module: ch02_fsm_binary
// Description:
//   5-state control FSM using Minimal Bits (Binary) state encoding:
//   - Number of states S = 5.
//   - State register width: ceil(log2(5)) = 3 bits.
//   - State assignments:
//       S_IDLE  = 3'b000 (0)
//       S_LOAD  = 3'b001 (1)
//       S_CALC  = 3'b010 (2)
//       S_DRAIN = 3'b011 (3)
//       S_DONE  = 3'b100 (4)
//   - Standard 2-process FSM coding template (registered state + comb next-state).
//   - Moore outputs decoded from state_reg.
//   - Synthesizable Verilog-2001, fully compatible with iverilog -g2012 -Wall.
// ============================================================================

`timescale 1ns/1ps

module ch02_fsm_binary (
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
    output wire [2:0] state_num
);

    localparam [2:0] S_IDLE  = 3'b000;
    localparam [2:0] S_LOAD  = 3'b001;
    localparam [2:0] S_CALC  = 3'b010;
    localparam [2:0] S_DRAIN = 3'b011;
    localparam [2:0] S_DONE  = 3'b100;

    reg [2:0] state_reg, state_next;

    // 1. State register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_reg <= S_IDLE;
        end else begin
            state_reg <= state_next;
        end
    end

    // 2. Next-state combinational logic
    always @(*) begin
        state_next = state_reg;
        case (state_reg)
            S_IDLE: begin
                if (start) state_next = S_LOAD;
            end
            S_LOAD: begin
                if (load_done) state_next = S_CALC;
            end
            S_CALC: begin
                if (calc_done) state_next = S_DRAIN;
            end
            S_DRAIN: begin
                if (drain_done) state_next = S_DONE;
            end
            S_DONE: begin
                state_next = S_IDLE;
            end
            default: begin
                state_next = S_IDLE;
            end
        endcase
    end

    // 3. Moore outputs decoded directly from state_reg
    assign busy       = (state_reg != S_IDLE);
    assign load_en    = (state_reg == S_LOAD);
    assign calc_en    = (state_reg == S_CALC);
    assign drain_en   = (state_reg == S_DRAIN);
    assign done_pulse = (state_reg == S_DONE);
    assign state_num  = state_reg;

endmodule
