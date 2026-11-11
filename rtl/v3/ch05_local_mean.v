// ============================================================================
// File: rtl/v3/ch05_local_mean.v
// Module: ch05_local_mean
// Description:
//   Bit-exact local mean calculation and subtraction module for Praat-style F0.
//   - Frame length: 638 samples.
//   - Local mean span: 426 samples (positions 106..531 inclusive, 0-based).
//   - Formula: mean = floor((S + 213) / 426)
//   - Reciprocal integer multiplication:
//       S_biased = S + 213 + 426 * 32768 (25-bit unsigned)
//       mean = (((S_biased * 10_082_083) >> 32) - 32768)
//   - Subtraction phase: d = x - mean (17-bit signed output [-65535, +65535]).
//   - Matches Intel LPM_MULT (25x24 unsigned, LPM_PIPELINE=1/2, 1 DSP in 27x27 mode).
//   - Standard Verilog-2001 / IEEE 1800-2012, compiles clean under -Wall.
// ============================================================================

`timescale 1ns / 1ps

module ch05_local_mean #(
    parameter DATA_WIDTH  = 16,
    parameter ADDR_WIDTH  = 10,
    parameter SPAN_LEN    = 426,
    parameter SPAN_OFFSET = 106,
    parameter MULT_M      = 24'd10082083, // ceil(2^32 / 426)
    parameter SHIFT_K     = 32
)(
    input  wire                         clk,
    input  wire                         rst_n,

    // Control interface
    input  wire                         start,          // Pulse to start mean calculation for frame
    output reg                          busy,           // High while reading and calculating mean
    output reg                          mean_valid,     // Asserted when mean_out is valid
    output reg  signed [DATA_WIDTH-1:0] mean_out,       // Computed 16-bit signed local mean

    // Ring buffer read master interface (requests 426 samples: 106..531)
    output reg                          rd_en,
    output reg  [ADDR_WIDTH-1:0]        rd_sample_idx,
    input  wire                         rd_valid,
    input  wire signed [DATA_WIDTH-1:0] rd_data,

    // Subtraction datapath (subtracts mean from frame samples 0..637)
    input  wire                         sub_valid_in,
    input  wire signed [DATA_WIDTH-1:0] sub_data_in,
    output reg                          diff_valid_out,
    output reg  signed [DATA_WIDTH:0]   diff_data_out   // 17-bit signed (x - mean)
);

    // State machine definition
    localparam STATE_IDLE    = 3'd0;
    localparam STATE_ISSUE   = 3'd1;
    localparam STATE_WAIT_RD = 3'd2;
    localparam STATE_MULT1   = 3'd3;
    localparam STATE_MULT2   = 3'd4;
    localparam STATE_DONE    = 3'd5;

    reg [2:0] state;

    // Address and sample counters
    reg [ADDR_WIDTH-1:0] issue_cnt;
    reg [ADDR_WIDTH-1:0] collect_cnt;

    // 25-bit accumulator initialized to rounding offset 213
    reg [24:0] acc;

    // Multiplier pipeline registers (modeling LPM_MULT 25x24 unsigned, pipeline=2)
    reg [24:0] mult_a_r;
    reg [23:0] mult_b_r;
    reg [48:0] mult_prod_r;

    // Registered subtraction output
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            diff_valid_out <= 1'b0;
            diff_data_out  <= {(DATA_WIDTH + 1){1'b0}};
        end else begin
            diff_valid_out <= sub_valid_in;
            if (sub_valid_in) begin
                // Sign-extend both operands to 17 bits before subtraction
                diff_data_out <= {sub_data_in[DATA_WIDTH-1], sub_data_in} -
                                 {mean_out[DATA_WIDTH-1], mean_out};
            end
        end
    end

    // FSM and Datapath
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= STATE_IDLE;
            busy          <= 1'b0;
            mean_valid    <= 1'b0;
            mean_out      <= {DATA_WIDTH{1'b0}};
            rd_en         <= 1'b0;
            rd_sample_idx <= {ADDR_WIDTH{1'b0}};
            issue_cnt     <= {ADDR_WIDTH{1'b0}};
            collect_cnt   <= {ADDR_WIDTH{1'b0}};
            acc           <= 25'd213; // Pre-loaded rounding offset
            mult_a_r      <= 25'd0;
            mult_b_r      <= 24'd0;
            mult_prod_r   <= 49'd0;
        end else begin
            case (state)
                STATE_IDLE: begin
                    busy       <= 1'b0;
                    rd_en      <= 1'b0;
                    mean_valid <= 1'b0;
                    if (start) begin
                        busy          <= 1'b1;
                        mean_valid    <= 1'b0;
                        issue_cnt     <= 10'd0;
                        collect_cnt   <= 10'd0;
                        acc           <= 25'd213; // Reset accumulator with +213
                        rd_en         <= 1'b1;
                        rd_sample_idx <= SPAN_OFFSET[ADDR_WIDTH-1:0]; // Start at 106
                        state         <= STATE_ISSUE;
                    end
                end

                STATE_ISSUE: begin
                    // Issue read requests for all 426 samples
                    if (issue_cnt < SPAN_LEN - 1) begin
                        issue_cnt     <= issue_cnt + 1'b1;
                        rd_sample_idx <= SPAN_OFFSET[ADDR_WIDTH-1:0] + (issue_cnt + 1'b1);
                        rd_en         <= 1'b1;
                    end else begin
                        rd_en         <= 1'b0;
                    end

                    // Concurrently accumulate returning samples from ring buffer
                    if (rd_valid) begin
                        // Map int16 [-32768, 32767] to uint16 [0, 65535] via inversion of MSB (XOR 0x8000)
                        acc         <= acc + {9'd0, (rd_data ^ 16'h8000)};
                        collect_cnt <= collect_cnt + 1'b1;
                        if (collect_cnt == SPAN_LEN - 1) begin
                            state <= STATE_MULT1;
                        end
                    end else if (issue_cnt == SPAN_LEN - 1) begin
                        state <= STATE_WAIT_RD;
                    end
                end

                STATE_WAIT_RD: begin
                    rd_en <= 1'b0;
                    if (rd_valid) begin
                        acc         <= acc + {9'd0, (rd_data ^ 16'h8000)};
                        collect_cnt <= collect_cnt + 1'b1;
                        if (collect_cnt == SPAN_LEN - 1) begin
                            state <= STATE_MULT1;
                        end
                    end
                end

                STATE_MULT1: begin
                    // Pipeline stage 1: latch multiplier operands (25x24 unsigned)
                    mult_a_r <= acc;
                    mult_b_r <= MULT_M;
                    state    <= STATE_MULT2;
                end

                STATE_MULT2: begin
                    // Pipeline stage 2: compute 49-bit unsigned product
                    mult_prod_r <= mult_a_r * mult_b_r;
                    state       <= STATE_DONE;
                end

                STATE_DONE: begin
                    // Quotient Q_biased is bits [47:32] (product shifted right by 32)
                    // Restore signed value: mean = Q_biased - 32768 (invert MSB of 16-bit word)
                    mean_out   <= {~mult_prod_r[47], mult_prod_r[46:32]};
                    mean_valid <= 1'b1;
                    busy       <= 1'b0;
                    state      <= STATE_IDLE;
                end

                default: state <= STATE_IDLE;
            endcase
        end
    end

endmodule
