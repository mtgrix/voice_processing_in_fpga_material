// rtl/v3/ch07_mac_engine.v
// Complete Hardware Autocorrelation Engine for 638-sample Audio Frames
//
// Features:
//   - Instantiates 638x17-bit True Dual-Port Sample RAM (ch07_xw_ram, 2x M10K)
//   - Instantiates 17x17-bit Signed MAC Unit (ch07_mac_unit, 1x DSP Variable Precision)
//   - Zero-bubble address generator: issues 98,540 pairs back-to-back
//       * Lag tau = 0       : 638 pairs  (n = 0..637)
//       * Lag tau = 26..214 : 97,902 pairs (n = 0..637-tau across 189 lags)
//       * Total pairs       : 98,540 issue cycles
//   - 3-cycle pipeline latency (1 cycle RAM read + 2 cycles DSP MAC)
//   - Total processing latency: exactly 98,543 cycles per frame
//   - At 50 MHz (hop 160 = 500,000 cycles), Core MAC RTF = 98,543 / 500,000 = 0.197

`timescale 1ns/1ps

module ch07_mac_engine #(
    parameter integer DATA_W       = 17,
    parameter integer DEPTH        = 638,
    parameter integer ADDR_W       = 10,
    parameter integer ACC_W        = 48,
    parameter integer TAU_SCAN_MIN = 26,
    parameter integer TAU_SCAN_MAX = 214,
    parameter integer N_LAGS       = 190   // R[0] + 189 lags (26..214)
) (
    input  wire                     clk,
    input  wire                     rst_n,

    // Frame sample loading interface (writes 638 samples into internal RAM)
    input  wire                     load_en,
    input  wire [ADDR_W-1:0]        load_addr,
    input  wire signed [DATA_W-1:0] load_data,

    // Execution control
    input  wire                     start,
    output reg                      busy,
    output reg                      done,

    // Streaming output interface for R[tau]
    output wire                     out_valid,
    output wire [7:0]               out_tau,      // Current lag index: 0, then 26..214
    output wire signed [ACC_W-1:0]  out_R,        // 48-bit signed unnormalized autocorrelation
    output reg  [31:0]              cycle_count   // Measured execution cycles from start to done
);

    // FSM States
    localparam [1:0]
        S_IDLE  = 2'd0,
        S_CALC  = 2'd1,
        S_DRAIN = 2'd2,
        S_DONE  = 2'd3;

    reg [1:0] state;

    // Address and Lag Counters
    reg [ADDR_W-1:0] n_cnt;
    reg [7:0]        lag_idx; // 0..189 (0: tau=0; 1..189: tau=26..214)
    reg [ADDR_W-1:0] current_tau;
    reg [ADDR_W-1:0] current_max_n;

    // Zero-bubble next-state logic
    wire is_last_n = (n_cnt == current_max_n);
    wire is_last_lag = (lag_idx == N_LAGS - 1);

    // Compute tau from lag_idx
    always @(*) begin
        if (lag_idx == 8'd0) begin
            current_tau = 10'd0;
        end else begin
            current_tau = TAU_SCAN_MIN + (lag_idx - 8'd1);
        end
        current_max_n = DEPTH - 1 - current_tau;
    end

    // Address Generator Outputs
    reg              gen_valid;
    reg              gen_sload;
    reg              gen_last;
    reg [7:0]        gen_tau;
    reg [ADDR_W-1:0] gen_addr_a;
    reg [ADDR_W-1:0] gen_addr_b;

    // Drain counter (to wait 3 cycles of pipeline latency at end of frame)
    reg [1:0] drain_cnt;

    // FSM and Address Generation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state       <= S_IDLE;
            busy        <= 1'b0;
            done        <= 1'b0;
            n_cnt       <= {ADDR_W{1'b0}};
            lag_idx     <= 8'd0;
            gen_valid   <= 1'b0;
            gen_sload   <= 1'b0;
            gen_last    <= 1'b0;
            gen_tau     <= 8'd0;
            gen_addr_a  <= {ADDR_W{1'b0}};
            gen_addr_b  <= {ADDR_W{1'b0}};
            drain_cnt   <= 2'd0;
            cycle_count <= 32'd0;
        end else begin
            case (state)
                S_IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        busy        <= 1'b1;
                        state       <= S_CALC;
                        n_cnt       <= {ADDR_W{1'b0}};
                        lag_idx     <= 8'd0;
                        cycle_count <= 32'd1;

                        // Issue first pair: n=0, tau=0
                        gen_valid   <= 1'b1;
                        gen_sload   <= 1'b1;
                        gen_last    <= 1'b0;
                        gen_tau     <= 8'd0;
                        gen_addr_a  <= 10'd0;
                        gen_addr_b  <= 10'd0;
                    end else begin
                        busy      <= 1'b0;
                        gen_valid <= 1'b0;
                        gen_sload <= 1'b0;
                        gen_last  <= 1'b0;
                    end
                end

                S_CALC: begin
                    cycle_count <= cycle_count + 32'd1;

                    if (is_last_n) begin
                        if (is_last_lag) begin
                            // Last pair of last lag (tau=214, n=423) was issued
                            // Stop generating, transition to drain
                            gen_valid <= 1'b0;
                            gen_sload <= 1'b0;
                            gen_last  <= 1'b0;
                            drain_cnt <= 2'd0;
                            state     <= S_DRAIN;
                        end else begin
                            // Advance to next lag with ZERO bubble
                            lag_idx   <= lag_idx + 8'd1;
                            n_cnt     <= {ADDR_W{1'b0}};

                            // Next lag tau
                            begin: advance_lag
                                reg [ADDR_W-1:0] next_t;
                                next_t = TAU_SCAN_MIN + lag_idx; // next lag_idx is lag_idx + 1
                                gen_valid  <= 1'b1;
                                gen_sload  <= 1'b1;
                                gen_last   <= (next_t == DEPTH - 1); // Only 1 pair if max
                                gen_tau    <= next_t[7:0];
                                gen_addr_a <= 10'd0;
                                gen_addr_b <= next_t;
                            end
                        end
                    end else begin
                        // Advance n within current lag
                        n_cnt      <= n_cnt + 10'd1;
                        gen_valid  <= 1'b1;
                        gen_sload  <= 1'b0;
                        gen_last   <= (n_cnt + 10'd1 == current_max_n);
                        gen_tau    <= (lag_idx == 8'd0) ? 8'd0 : (TAU_SCAN_MIN + lag_idx - 8'd1);
                        gen_addr_a <= n_cnt + 10'd1;
                        gen_addr_b <= n_cnt + 10'd1 + current_tau;
                    end
                end

                S_DRAIN: begin
                    cycle_count <= cycle_count + 32'd1;
                    gen_valid   <= 1'b0;
                    gen_sload   <= 1'b0;
                    gen_last    <= 1'b0;

                    if (drain_cnt == 2'd2) begin
                        state <= S_DONE;
                    end else begin
                        drain_cnt <= drain_cnt + 2'd1;
                    end
                end

                S_DONE: begin
                    done  <= 1'b1;
                    busy  <= 1'b0;
                    state <= S_IDLE;
                end
            endcase
        end
    end

    // RAM Instance
    wire signed [DATA_W-1:0] ram_qa;
    wire signed [DATA_W-1:0] ram_qb;

    wire [ADDR_W-1:0] ram_addr_a = busy ? gen_addr_a : load_addr;
    wire signed [DATA_W-1:0] ram_din_a = busy ? {DATA_W{1'b0}} : load_data;
    wire ram_we_a = busy ? 1'b0 : load_en;

    ch07_xw_ram #(
        .DATA_W(DATA_W),
        .DEPTH(DEPTH),
        .ADDR_W(ADDR_W)
    ) u_ram (
        .clk    (clk),
        .we_a   (ram_we_a),
        .addr_a (ram_addr_a),
        .din_a  (ram_din_a),
        .dout_a (ram_qa),
        .we_b   (1'b0),
        .addr_b (gen_addr_b),
        .din_b  ({DATA_W{1'b0}}),
        .dout_b (ram_qb)
    );

    // RAM Pipeline Delay: 1 cycle delay for control flags
    reg       ram_vld_r;
    reg       ram_sload_r;
    reg       ram_last_r;
    reg [7:0] ram_tau_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ram_vld_r   <= 1'b0;
            ram_sload_r <= 1'b0;
            ram_last_r  <= 1'b0;
            ram_tau_r   <= 8'd0;
        end else begin
            ram_vld_r   <= gen_valid;
            ram_sload_r <= gen_sload;
            ram_last_r  <= gen_last;
            ram_tau_r   <= gen_tau;
        end
    end

    // DSP Pipeline Delay: 2 cycles delay for tau tag to match MAC unit latency
    reg [7:0] mac_tau_d1;
    reg [7:0] mac_tau_d2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            mac_tau_d1 <= 8'd0;
            mac_tau_d2 <= 8'd0;
        end else begin
            mac_tau_d1 <= ram_tau_r;
            mac_tau_d2 <= mac_tau_d1;
        end
    end

    assign out_tau = mac_tau_d2;

    // MAC Unit Instance
    ch07_mac_unit #(
        .DATA_W(DATA_W),
        .PROD_W(2 * DATA_W),
        .ACC_W (ACC_W)
    ) u_mac (
        .clk       (clk),
        .rst_n     (rst_n),
        .in_valid  (ram_vld_r),
        .in_sload  (ram_sload_r),
        .in_last   (ram_last_r),
        .a         (ram_qa),
        .b         (ram_qb),
        .acc       (out_R),
        .out_valid (out_valid)
    );

endmodule
