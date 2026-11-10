// ============================================================================
// File: rtl/v3/ch00_pair_counter.v
// Module: ch00_pair_counter
// Description:
//   Address and pair generator for Praat-style autocorrelation on FPGA.
//   For a frame of length N and lag range [TAU_MIN, TAU_MAX], this block
//   issues sample pairs (addr_a = n, addr_b = n + tau) for the energy R[0]
//   followed seamlessly by lags tau in [TAU_MIN, TAU_MAX].
//
//   Control flags:
//     - valid: asserted when a valid address pair is presented.
//     - sload: asserted for the first pair (n = 0) of each lag, instructing
//              the MAC accumulator to synchronously load the first product
//              rather than accumulate, eliminating idle flush cycles.
//     - last:  asserted for the final pair (n = N - 1 - tau) of each lag,
//              signaling that the accumulated R[tau] is complete.
//
//   Configuration:
//     - Parameter defaults: N = 638, TAU_MIN = 26, TAU_MAX = 214.
//     - Runtime inputs cfg_n, cfg_tau_min, cfg_tau_max: if cfg_n == 0,
//       parameters N, TAU_MIN, TAU_MAX are used. This allows static
//       synthesis optimization while enabling dynamic multi-configuration
//       verification in testbenches.
//
//   Total pairs issued: N + sum_{tau=TAU_MIN}^{TAU_MAX} (N - tau).
//   For N = 638, TAU_MIN = 26, TAU_MAX = 214: exactly 98,540 pairs.
// ============================================================================

`timescale 1ns/1ps

module ch00_pair_counter #(
    parameter integer N          = 638,
    parameter integer TAU_MIN    = 26,
    parameter integer TAU_MAX    = 214,
    parameter integer ADDR_WIDTH = 10
)(
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   start,
    input  wire [ADDR_WIDTH-1:0]  cfg_n,
    input  wire [ADDR_WIDTH-1:0]  cfg_tau_min,
    input  wire [ADDR_WIDTH-1:0]  cfg_tau_max,
    output reg                    busy,
    output reg                    done,
    output reg                    valid,
    output reg                    sload,
    output reg                    last,
    output reg  [ADDR_WIDTH-1:0]  addr_a,
    output reg  [ADDR_WIDTH-1:0]  addr_b,
    output reg  [ADDR_WIDTH-1:0]  tau_out,
    output reg  [31:0]            total_cycles,
    output reg  [31:0]            pair_count
);

    // Internal state encoding
    localparam [1:0] STATE_IDLE = 2'b00;
    localparam [1:0] STATE_RUN  = 2'b01;
    localparam [1:0] STATE_DONE = 2'b10;

    reg [1:0]            state;
    reg [ADDR_WIDTH-1:0] n_cnt;
    reg [ADDR_WIDTH-1:0] tau_cnt;
    reg [ADDR_WIDTH-1:0] act_n;
    reg [ADDR_WIDTH-1:0] act_tau_min;
    reg [ADDR_WIDTH-1:0] act_tau_max;

    // Maximum sample index for current lag
    // When tau_cnt == 0: max_n = act_n - 1
    // When tau_cnt >= act_tau_min: max_n = act_n - 1 - tau_cnt
    wire [ADDR_WIDTH-1:0] max_n = (tau_cnt == {ADDR_WIDTH{1'b0}}) ?
                                  (act_n - 1'b1) : (act_n - 1'b1 - tau_cnt);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= STATE_IDLE;
            busy         <= 1'b0;
            done         <= 1'b0;
            valid        <= 1'b0;
            sload        <= 1'b0;
            last         <= 1'b0;
            addr_a       <= {ADDR_WIDTH{1'b0}};
            addr_b       <= {ADDR_WIDTH{1'b0}};
            tau_out      <= {ADDR_WIDTH{1'b0}};
            total_cycles <= 32'd0;
            pair_count   <= 32'd0;
            n_cnt        <= {ADDR_WIDTH{1'b0}};
            tau_cnt      <= {ADDR_WIDTH{1'b0}};
            act_n        <= N[ADDR_WIDTH-1:0];
            act_tau_min  <= TAU_MIN[ADDR_WIDTH-1:0];
            act_tau_max  <= TAU_MAX[ADDR_WIDTH-1:0];
        end else begin
            case (state)
                STATE_IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        state <= STATE_RUN;
                        busy  <= 1'b1;
                        valid <= 1'b1;
                        sload <= 1'b1;

                        // Latch active parameters
                        if (cfg_n != {ADDR_WIDTH{1'b0}}) begin
                            act_n       <= cfg_n;
                            act_tau_min <= cfg_tau_min;
                            act_tau_max <= cfg_tau_max;
                            last        <= (cfg_n == 1'b1);
                        end else begin
                            act_n       <= N[ADDR_WIDTH-1:0];
                            act_tau_min <= TAU_MIN[ADDR_WIDTH-1:0];
                            act_tau_max <= TAU_MAX[ADDR_WIDTH-1:0];
                            last        <= (N == 1);
                        end

                        addr_a       <= {ADDR_WIDTH{1'b0}};
                        addr_b       <= {ADDR_WIDTH{1'b0}};
                        tau_out      <= {ADDR_WIDTH{1'b0}};
                        tau_cnt      <= {ADDR_WIDTH{1'b0}};
                        n_cnt        <= {ADDR_WIDTH{1'b0}};
                        total_cycles <= 32'd1;
                        pair_count   <= 32'd1;
                    end else begin
                        busy  <= 1'b0;
                        valid <= 1'b0;
                        sload <= 1'b0;
                        last  <= 1'b0;
                    end
                end

                STATE_RUN: begin
                    if (n_cnt < max_n) begin
                        // Advance to next sample in current lag
                        total_cycles <= total_cycles + 1'b1;
                        n_cnt      <= n_cnt + 1'b1;
                        addr_a     <= n_cnt + 1'b1;
                        addr_b     <= (tau_cnt == {ADDR_WIDTH{1'b0}}) ?
                                      (n_cnt + 1'b1) : (n_cnt + 1'b1 + tau_cnt);
                        sload      <= 1'b0;
                        last       <= (n_cnt + 1'b1 == max_n);
                        pair_count <= pair_count + 1'b1;
                    end else begin
                        // Reached end of current lag: transition to next lag seamlessly
                        if (tau_cnt == {ADDR_WIDTH{1'b0}}) begin
                            // Completed R[0], transition to act_tau_min
                            total_cycles <= total_cycles + 1'b1;
                            tau_cnt    <= act_tau_min;
                            tau_out    <= act_tau_min;
                            n_cnt      <= {ADDR_WIDTH{1'b0}};
                            addr_a     <= {ADDR_WIDTH{1'b0}};
                            addr_b     <= act_tau_min;
                            sload      <= 1'b1;
                            last       <= (act_n - 1'b1 - act_tau_min == 0);
                            pair_count <= pair_count + 1'b1;
                        end else if (tau_cnt < act_tau_max) begin
                            // Advance to next lag in [act_tau_min, act_tau_max]
                            total_cycles <= total_cycles + 1'b1;
                            tau_cnt    <= tau_cnt + 1'b1;
                            tau_out    <= tau_cnt + 1'b1;
                            n_cnt      <= {ADDR_WIDTH{1'b0}};
                            addr_a     <= {ADDR_WIDTH{1'b0}};
                            addr_b     <= tau_cnt + 1'b1;
                            sload      <= 1'b1;
                            last       <= (act_n - 1'b1 - (tau_cnt + 1'b1) == 0);
                            pair_count <= pair_count + 1'b1;
                        end else begin
                            // Completed final lag act_tau_max: all pairs issued
                            valid <= 1'b0;
                            sload <= 1'b0;
                            last  <= 1'b0;
                            busy  <= 1'b0;
                            done  <= 1'b1;
                            state <= STATE_DONE;
                        end
                    end
                end

                STATE_DONE: begin
                    busy  <= 1'b0;
                    valid <= 1'b0;
                    sload <= 1'b0;
                    last  <= 1'b0;
                    done  <= 1'b1;
                    if (!start) begin
                        state <= STATE_IDLE;
                    end
                end

                default: state <= STATE_IDLE;
            endcase
        end
    end

endmodule
