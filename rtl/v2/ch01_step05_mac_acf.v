// rtl/v2/ch01_step05_mac_acf.v
// Sequential autocorrelation MAC engine for Step 5.
// Accumulates sum_{n=0}^{L-1-tau} x[n] * x[n+tau] with a 48-bit signed accumulator.
// Fully synthesizable FSM with IDLE, RUN, and DONE states.
`timescale 1ns/1ps

module ch01_step05_mac_acf (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               start_tau,   // Pulses high to begin accumulating lag tau
    input  wire [9:0]         n_pairs,     // Number of pairs to accumulate: L - tau
    input  wire signed [15:0] sample_a,    // x[n]
    input  wire signed [15:0] sample_b,    // x[n + tau]
    output reg  [9:0]         rd_addr_a,   // Memory read address for sample_a
    output reg  [9:0]         rd_addr_b,   // Memory read address for sample_b
    output reg                done_tau,    // Pulses high when accumulation is finished
    output reg  signed [47:0] r_tau_out    // Final accumulated autocorrelation energy
);

    localparam S_IDLE = 2'd0;
    localparam S_RUN  = 2'd1;
    localparam S_DONE = 2'd2;

    reg [1:0] state;
    reg [9:0] cnt;
    reg [9:0] num_pairs_reg;
    reg signed [47:0] acc;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= S_IDLE;
            cnt           <= 10'd0;
            num_pairs_reg <= 10'd0;
            acc           <= 48'sd0;
            done_tau      <= 1'b0;
            r_tau_out     <= 48'sd0;
            rd_addr_a     <= 10'd0;
            rd_addr_b     <= 10'd0;
        end else begin
            case (state)
                S_IDLE: begin
                    done_tau <= 1'b0;
                    if (start_tau) begin
                        state         <= S_RUN;
                        cnt           <= 10'd0;
                        num_pairs_reg <= n_pairs;
                        acc           <= 48'sd0;
                        rd_addr_a     <= 10'd0;
                        rd_addr_b     <= 10'd0;
                    end
                end

                S_RUN: begin
                    // Multiply and accumulate
                    acc <= acc + (sample_a * sample_b);
                    cnt <= cnt + 10'd1;
                    rd_addr_a <= cnt + 10'd1;
                    rd_addr_b <= cnt + 10'd1;

                    if (cnt + 10'd1 >= num_pairs_reg) begin
                        state <= S_DONE;
                    end
                end

                S_DONE: begin
                    done_tau  <= 1'b1;
                    r_tau_out <= acc;
                    state     <= S_IDLE;
                end

                default: state <= S_IDLE;
            endcase
        end
    end

endmodule
