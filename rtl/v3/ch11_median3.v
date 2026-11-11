// ============================================================================
// Module: ch11_median3
// Project: Praat-style F0 Estimation on DE10-Standard FPGA
// Description:
//   3-point Median Filter (Median-3) replacing Praat's Viterbi Path Finder.
//   Removes isolated 1-frame gross pitch errors (spurious octave jumps/halvings).
//   Causal hardware alignment:
//     - Operates with 1-frame causal latency (frame k-1 output at time k).
//     - Edge repetition: replicates sample 0 at start: med(x[0], x[0], x[1]).
//     - Auto flush beat: on in_last, produces one final flush beat replicating
//       sample N-1: med(x[N-2], x[N-1], x[N-1]) with out_last = 1.
//
// Registers (standard names):
//   - f0_z0: newest incoming frame sample (x[k])
//   - f0_z1: center frame sample (x[k-1])
//   - f0_z2: oldest frame sample (x[k-2])
//   - f0_med: registered median output
//
// Target: Cyclone V (5CSXFC6D6F31C6N)
// Standard: Verilog-2001
// ============================================================================

`timescale 1ns / 1ps

module ch11_median3 (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        in_valid,
    input  wire        in_first,
    input  wire        in_last,
    input  wire [15:0] in_f0,
    output reg         out_valid,
    output reg         out_last,
    output wire [15:0] out_f0
);

    // ------------------------------------------------------------------------
    // FSM control states
    // ------------------------------------------------------------------------
    localparam S_IDLE   = 2'd0;
    localparam S_STREAM = 2'd1;
    localparam S_FLUSH  = 2'd2;

    reg [1:0] state;

    // ------------------------------------------------------------------------
    // Pipeline registers for F0 stream
    // ------------------------------------------------------------------------
    reg [15:0] f0_z0;   // Most recent input sample
    reg [15:0] f0_z1;   // Center sample (current frame under analysis)
    reg [15:0] f0_z2;   // Past sample
    reg [15:0] f0_med;  // Registered median output

    assign out_f0 = f0_med;

    // ------------------------------------------------------------------------
    // Combinational 3-element sorting network (16-bit unsigned)
    // Operands: a = f0_z2, b = f0_z1, c = (state == S_FLUSH) ? f0_z1 : in_f0
    // ------------------------------------------------------------------------
    wire [15:0] med_a = f0_z2;
    wire [15:0] med_b = f0_z1;
    wire [15:0] med_c = (state == S_FLUSH) ? f0_z1 : in_f0;

    wire cmp_ab = (med_a <= med_b);
    wire cmp_bc = (med_b <= med_c);
    wire cmp_ac = (med_a <= med_c);

    reg [15:0] med_comb;
    always @(*) begin
        if (cmp_ab) begin
            if (cmp_bc)
                med_comb = med_b;
            else if (cmp_ac)
                med_comb = med_c;
            else
                med_comb = med_a;
        end else begin
            if (cmp_ac)
                med_comb = med_a;
            else if (cmp_bc)
                med_comb = med_c;
            else
                med_comb = med_b;
        end
    end

    // ------------------------------------------------------------------------
    // Synchronous state and register update
    // ------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= S_IDLE;
            f0_z0     <= 16'd0;
            f0_z1     <= 16'd0;
            f0_z2     <= 16'd0;
            f0_med    <= 16'd0;
            out_valid <= 1'b0;
            out_last  <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    out_valid <= 1'b0;
                    out_last  <= 1'b0;
                    if (in_valid && in_first) begin
                        // Load frame 0: duplicate edge sample into z1 and z2
                        f0_z0 <= in_f0;
                        f0_z1 <= in_f0;
                        f0_z2 <= in_f0;
                        if (in_last) begin
                            // Edge case: single-frame stream (N = 1)
                            state <= S_FLUSH;
                        end else begin
                            state <= S_STREAM;
                        end
                    end
                end

                S_STREAM: begin
                    if (in_valid) begin
                        // Output median result for frame k-1
                        f0_med    <= med_comb;
                        out_valid <= 1'b1;
                        out_last  <= 1'b0;

                        // Shift pipeline registers
                        f0_z2 <= f0_z1;
                        f0_z1 <= in_f0;
                        f0_z0 <= in_f0;

                        if (in_last) begin
                            // Last frame x[N-1] received: proceed to flush beat
                            state <= S_FLUSH;
                        end else begin
                            state <= S_STREAM;
                        end
                    end else begin
                        // Backpressure / idle beat: hold registers, deassert out_valid
                        out_valid <= 1'b0;
                        out_last  <= 1'b0;
                    end
                end

                S_FLUSH: begin
                    // Flush beat: duplicate last sample x[N-1] (f0_z1) and emit frame N-1
                    f0_med    <= med_comb;
                    out_valid <= 1'b1;
                    out_last  <= 1'b1;

                    f0_z0     <= f0_z1;
                    state     <= S_IDLE;
                end

                default: begin
                    state     <= S_IDLE;
                    out_valid <= 1'b0;
                    out_last  <= 1'b0;
                end
            endcase
        end
    end

endmodule
