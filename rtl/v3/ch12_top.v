// ============================================================================
// File: rtl/v3/ch12_top.v
// Module: ch12_top
// Description:
//   Top-level integration module for Praat-style F0 Estimation on Cyclone V SoC.
//   Instantiates and coordinates all accepted hardware modules:
//     - ch01_avalon_fifo: Input FIFO (Avalon-MM write slave, Avalon-ST source)
//     - ch03_fir_filter:  Nyquist-edge anti-aliasing FIR (bypass default)
//     - ch04_ring_buffer: 1024x16 Circular sample buffer (hop 160, frame 638)
//     - ch05_local_mean:  Local mean calculation (426 samples) & subtraction
//     - ch06_hanning_window: Hanning N+1 window (638 samples) & LocalPeak detector
//     - ch07_mac_engine:  Autocorrelation MAC engine (R0 + 189 lags, 98,543 cycles)
//     - ch08_norm_score:  Normalization & subtractive octave cost scoring
//     - ch09_f0_calc:     Parabolic peak finder & radix-2 divider
//     - ch10_voicing:     Integer cross-multiplication voicing decision gate
//     - ch11_median3:     3-frame causal median filter with symmetric edge replication
//     - ch01_fifo_out:    Output FIFO (Avalon-ST sink, Avalon-MM read slave)
//
//   Control & Status Register (CSR) Map (32-bit words):
//     Offset 0x00: REG_CTRL_START        (Write 1 to start processing)
//     Offset 0x04: REG_CTRL_NFRAMES      (Total number of analysis frames)
//     Offset 0x08: REG_CTRL_FIRST_WIN0   (Initial window sample discard offset)
//     Offset 0x0C: REG_CTRL_GLOBAL_PEAK  (WAV-level globalPeak amplitude GP)
//     Offset 0x10: REG_CTRL_CONFIG       (Bit 0: fir_bypass, Bit 1: dc_blocker_en)
//     Offset 0x14: REG_CTRL_STATUS       (Bit 0: busy, Bit 1: done, Bit 2/3: ovf)
//     Offset 0x18: REG_CTRL_TOTAL_CYCLES (Total processing clock cycles)
//     Offset 0x1C: REG_CTRL_FRAME_CYCLES (Processing cycles of latest frame)
//
// Target: Cyclone V SoC (5CSXFC6D6F31C6N)
// Standard: Verilog-2001 (iverilog -g2012 -Wall compatible)
// ============================================================================

`timescale 1ns / 1ps

module ch12_top #(
    parameter integer FIFO_IN_ADDR_W  = 8,   // 256 words = 512 samples
    parameter integer FIFO_OUT_ADDR_W = 9,   // 512 words
    parameter integer RING_ADDR_W     = 10,  // 1024 words
    parameter integer FRAME_LEN       = 638,
    parameter integer HOP_LEN         = 160
)(
    input  wire        clk,
    input  wire        rst_n,

    // ------------------------------------------------------------------------
    // Avalon-MM Data Write Slave (FIFO_IN)
    // ------------------------------------------------------------------------
    input  wire        mm_in_write,
    input  wire [31:0] mm_in_writedata,
    output wire        mm_in_waitrequest,

    // ------------------------------------------------------------------------
    // Avalon-MM CSR Read Slave (FIFO_IN_CSR)
    // ------------------------------------------------------------------------
    input  wire        csr_in_read,
    input  wire [2:0]  csr_in_address,
    output wire [31:0] csr_in_readdata,

    // ------------------------------------------------------------------------
    // Avalon-MM Control & Status Register Slave (CTRL)
    // ------------------------------------------------------------------------
    input  wire        ctrl_write,
    input  wire        ctrl_read,
    input  wire [2:0]  ctrl_address,
    input  wire [31:0] ctrl_writedata,
    output reg  [31:0] ctrl_readdata,

    // ------------------------------------------------------------------------
    // Avalon-MM Data Read Slave (FIFO_OUT)
    // ------------------------------------------------------------------------
    input  wire        mm_out_read,
    output wire [31:0] mm_out_readdata,
    output wire        mm_out_waitrequest,

    // ------------------------------------------------------------------------
    // Avalon-MM CSR Read Slave (FIFO_OUT_CSR)
    // ------------------------------------------------------------------------
    input  wire        csr_out_read,
    input  wire [2:0]  csr_out_address,
    output wire [31:0] csr_out_readdata
);

    // ========================================================================
    // CSR Register Definitions and Storage
    // ========================================================================
    reg        reg_start_pulse;
    reg [15:0] reg_nframes;
    reg [15:0] reg_first_win0;
    reg [15:0] reg_global_peak;
    reg [31:0] reg_config;
    reg [31:0] reg_total_cycles;
    reg [31:0] reg_frame_cycles;
    reg        busy_reg;
    reg        done_reg;

    wire [31:0] status_word = {28'd0, 2'b00, done_reg, busy_reg};

    // CSR Write Handler
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg_start_pulse  <= 1'b0;
            reg_nframes      <= 16'd0;
            reg_first_win0   <= 16'd0;
            reg_global_peak  <= 16'd0;
            reg_config       <= 32'h00000001; // Default: fir_bypass = 1
        end else begin
            reg_start_pulse <= 1'b0; // Self-clearing start pulse
            if (ctrl_write) begin
                case (ctrl_address)
                    3'd0: if (ctrl_writedata[0]) reg_start_pulse <= 1'b1;
                    3'd1: reg_nframes     <= ctrl_writedata[15:0];
                    3'd2: reg_first_win0  <= ctrl_writedata[15:0];
                    3'd3: reg_global_peak <= ctrl_writedata[15:0];
                    3'd4: reg_config      <= ctrl_writedata;
                    default: ;
                endcase
            end
        end
    end

    // CSR Read Handler
    always @(*) begin
        case (ctrl_address)
            3'd0: ctrl_readdata = {31'd0, reg_start_pulse};
            3'd1: ctrl_readdata = {16'd0, reg_nframes};
            3'd2: ctrl_readdata = {16'd0, reg_first_win0};
            3'd3: ctrl_readdata = {16'd0, reg_global_peak};
            3'd4: ctrl_readdata = reg_config;
            3'd5: ctrl_readdata = status_word;
            3'd6: ctrl_readdata = reg_total_cycles;
            3'd7: ctrl_readdata = reg_frame_cycles;
            default: ctrl_readdata = 32'd0;
        endcase
    end

    // ========================================================================
    // Module Interconnect Wires
    // ========================================================================

    // FIFO IN to Audio Input Flow
    wire [15:0] fifo_in_st_data;
    wire        fifo_in_st_valid;
    wire        fifo_in_st_ready;

    // Discard & Stream Mux
    reg  [15:0] discard_cnt;
    wire        discarding = (discard_cnt < reg_first_win0);

    wire        stream_in_valid = fifo_in_st_valid && !discarding;
    wire [15:0] stream_in_data  = fifo_in_st_data;
    wire        stream_in_ready;

    assign fifo_in_st_ready = discarding ? 1'b1 : stream_in_ready;

    // FIR Filter
    wire        fir_source_valid;
    wire        fir_source_ready;
    wire [15:0] fir_source_data;

    // Ring Buffer
    reg         core_clr;
    wire        ring_frame_ready;
    reg         ring_frame_step;
    wire [15:0] ring_frame_idx;
    wire [10:0] ring_sample_count;
    wire [9:0]  ring_rd_base;
    reg         ring_rd_en;
    reg  [9:0]  ring_rd_sample_idx;
    wire signed [15:0] ring_rd_data;
    wire        ring_rd_valid;

    // Local Mean
    reg         mean_start;
    wire        mean_busy;
    wire        mean_valid;
    wire signed [15:0] mean_out;
    wire        mean_rd_en;
    wire [9:0]  mean_rd_sample_idx;
    reg         mean_rd_valid;
    reg         mean_sub_valid_in;
    wire        mean_diff_valid_out;
    wire signed [16:0] mean_diff_data_out;

    // Hanning Window & LocalPeak
    reg         win_start;
    wire        win_busy;
    wire        win_out_valid;
    wire signed [16:0] win_out_xw;
    wire        win_out_done;
    wire [15:0] win_out_lp;
    reg  [15:0] latched_lp;

    // MAC Engine
    reg  [9:0]  mac_load_addr;
    reg         mac_start;
    wire        mac_busy;
    wire        mac_done;
    wire        mac_out_valid;
    wire [7:0]  mac_out_tau;
    wire signed [47:0] mac_out_R;
    wire [31:0] mac_cycle_count;

    // Normalization & Scoring
    wire        norm_out_valid;
    wire [7:0]  norm_out_tau;
    wire signed [27:0] norm_out_U;
    wire signed [27:0] norm_out_Sc;
    wire [25:0] norm_out_R0n;
    wire [4:0]  norm_out_sh;
    wire        norm_out_last;

    // F0 Calculation (Peak Finder + Radix-2 Divider)
    wire        calc_out_valid;
    wire [15:0] calc_out_f0_raw;
    wire [7:0]  calc_out_best_tau;
    wire signed [27:0] calc_out_sc;
    wire [26:0] calc_out_r0n;
    wire        calc_out_found;

    // Voicing Decision Gate
    wire        voice_out_valid;
    wire [15:0] voice_out_f0;
    wire        voice_out_voiced;

    // Median-3 Filter
    reg         med_in_valid;
    reg         med_in_first;
    reg         med_in_last;
    reg  [15:0] med_in_f0;
    wire        med_out_valid;
    wire        med_out_last;
    wire [15:0] med_out_f0;

    // FIFO OUT
    wire        fifo_out_st_ready;

    // ========================================================================
    // Top-Level Coordination FSM States
    // ========================================================================
    localparam [3:0]
        FSM_IDLE         = 4'd0,
        FSM_DISCARD      = 4'd1,
        FSM_WAIT_FRAME   = 4'd2,
        FSM_MEAN         = 4'd3,
        FSM_WINDOW       = 4'd4,
        FSM_MAC          = 4'd5,
        FSM_DIV_VOICE    = 4'd6,
        FSM_FLUSH_MEDIAN = 4'd7,
        FSM_DONE         = 4'd8;

    reg [3:0]  state;
    reg [15:0] frame_idx_cnt;
    reg [9:0]  p2_issue_cnt;
    reg [31:0] total_cycles_cnt;
    reg [31:0] frame_cycles_cnt;
    reg        counting_frame;

    // Cycle Counters Tracking
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            total_cycles_cnt <= 32'd0;
            frame_cycles_cnt <= 32'd0;
            reg_total_cycles <= 32'd0;
            reg_frame_cycles <= 32'd0;
        end else begin
            if (busy_reg) begin
                total_cycles_cnt <= total_cycles_cnt + 32'd1;
            end
            if (counting_frame) begin
                frame_cycles_cnt <= frame_cycles_cnt + 32'd1;
            end
        end
    end

    // ========================================================================
    // FSM Control Transitions and Datapath Multiplexing
    // ========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state            <= FSM_IDLE;
            busy_reg         <= 1'b0;
            done_reg         <= 1'b0;
            core_clr         <= 1'b0;
            discard_cnt      <= 16'd0;
            frame_idx_cnt    <= 16'd0;
            counting_frame   <= 1'b0;
            mean_start       <= 1'b0;
            win_start        <= 1'b0;
            mac_start        <= 1'b0;
            ring_frame_step  <= 1'b0;
            latched_lp       <= 16'd0;
            mac_load_addr    <= 10'd0;
            p2_issue_cnt     <= 10'd0;
            med_in_valid     <= 1'b0;
            med_in_first     <= 1'b0;
            med_in_last      <= 1'b0;
            med_in_f0        <= 16'd0;
        end else begin
            // Default pulse de-assertions
            core_clr        <= 1'b0;
            mean_start      <= 1'b0;
            win_start       <= 1'b0;
            mac_start       <= 1'b0;
            ring_frame_step <= 1'b0;
            med_in_valid    <= 1'b0;

            case (state)
                FSM_IDLE: begin
                    busy_reg       <= 1'b0;
                    counting_frame <= 1'b0;
                    if (reg_start_pulse) begin
                        busy_reg      <= 1'b1;
                        done_reg      <= 1'b0;
                        core_clr      <= 1'b1;
                        frame_idx_cnt <= 16'd0;
                        discard_cnt   <= 16'd0;
                        if (reg_first_win0 > 0) begin
                            state <= FSM_DISCARD;
                        end else begin
                            state <= FSM_WAIT_FRAME;
                        end
                    end
                end

                FSM_DISCARD: begin
                    if (fifo_in_st_valid) begin
                        discard_cnt <= discard_cnt + 16'd1;
                        if (discard_cnt + 16'd1 == reg_first_win0) begin
                            state <= FSM_WAIT_FRAME;
                        end
                    end
                end

                FSM_WAIT_FRAME: begin
                    if (ring_frame_ready) begin
                        // Start frame processing
                        counting_frame <= 1'b1;
                        mean_start     <= 1'b1;
                        state          <= FSM_MEAN;
                    end
                end

                FSM_MEAN: begin
                    if (mean_valid) begin
                        // Phase 1 complete: launch Phase 2
                        win_start     <= 1'b1;
                        p2_issue_cnt  <= 10'd0;
                        mac_load_addr <= 10'd0;
                        state         <= FSM_WINDOW;
                    end
                end

                FSM_WINDOW: begin
                    // Issue read requests for 638 samples (0..637)
                    if (p2_issue_cnt < FRAME_LEN) begin
                        p2_issue_cnt <= p2_issue_cnt + 10'd1;
                    end

                    // As windowed samples emerge, write into MAC engine sample RAM
                    if (win_out_valid) begin
                        mac_load_addr <= mac_load_addr + 10'd1;
                    end

                    // When sample 637 completes, latch LP and launch MAC engine
                    if (win_out_done) begin
                        latched_lp <= win_out_lp;
                        mac_start  <= 1'b1;
                        state      <= FSM_MAC;
                    end
                end

                FSM_MAC: begin
                    if (mac_done) begin
                        // MAC autocorrelation complete; await divider and voicing
                        state <= FSM_DIV_VOICE;
                    end
                end

                FSM_DIV_VOICE: begin
                    if (voice_out_valid) begin
                        // Deliver frame F0 result to median-3 filter
                        med_in_valid <= 1'b1;
                        med_in_first <= (frame_idx_cnt == 16'd0);
                        med_in_last  <= (frame_idx_cnt == reg_nframes - 16'd1);
                        med_in_f0    <= voice_out_f0;

                        // Step ring buffer hop by 160 samples
                        ring_frame_step <= 1'b1;
                        counting_frame  <= 1'b0;
                        reg_frame_cycles <= frame_cycles_cnt + 32'd1;

                        frame_idx_cnt <= frame_idx_cnt + 16'd1;

                        if (frame_idx_cnt + 16'd1 < reg_nframes) begin
                            state <= FSM_WAIT_FRAME;
                        end else begin
                            state <= FSM_FLUSH_MEDIAN;
                        end
                    end
                end

                FSM_FLUSH_MEDIAN: begin
                    // Await median-3 flush beat emitting frame N-1
                    if (med_out_last) begin
                        done_reg         <= 1'b1;
                        busy_reg         <= 1'b0;
                        reg_total_cycles <= total_cycles_cnt + 32'd1;
                        state            <= FSM_DONE;
                    end
                end

                FSM_DONE: begin
                    busy_reg <= 1'b0;
                    done_reg <= 1'b1;
                    if (reg_start_pulse) begin
                        state <= FSM_IDLE;
                    end
                end

                default: state <= FSM_IDLE;
            endcase
        end
    end

    // ========================================================================
    // Ring Buffer Read Port Multiplexer
    // ========================================================================
    always @(*) begin
        case (state)
            FSM_MEAN: begin
                ring_rd_en         = mean_rd_en;
                ring_rd_sample_idx = mean_rd_sample_idx;
                mean_rd_valid      = ring_rd_valid;
                mean_sub_valid_in  = 1'b0;
            end

            FSM_WINDOW: begin
                ring_rd_en         = (p2_issue_cnt < FRAME_LEN);
                ring_rd_sample_idx = p2_issue_cnt;
                mean_rd_valid      = 1'b0;
                mean_sub_valid_in  = ring_rd_valid;
            end

            default: begin
                ring_rd_en         = 1'b0;
                ring_rd_sample_idx = 10'd0;
                mean_rd_valid      = 1'b0;
                mean_sub_valid_in  = 1'b0;
            end
        endcase
    end

    // ========================================================================
    // Module Instantiations
    // ========================================================================

    // 1. Input FIFO (Avalon-MM write slave -> Avalon-ST source)
    ch01_avalon_fifo #(
        .ADDR_WIDTH(FIFO_IN_ADDR_W)
    ) u_fifo_in (
        .clk            (clk),
        .rst_n          (rst_n),
        .mm_write       (mm_in_write),
        .mm_writedata   (mm_in_writedata),
        .mm_waitrequest (mm_in_waitrequest),
        .csr_read       (csr_in_read),
        .csr_address    (csr_in_address),
        .csr_readdata   (csr_in_readdata),
        .st_data        (fifo_in_st_data),
        .st_valid       (fifo_in_st_valid),
        .st_ready       (fifo_in_st_ready)
    );

    // 2. Anti-aliasing FIR Filter (Folded 31-tap, bypass default)
    ch03_fir_filter #(
        .DATA_WIDTH(16),
        .COEFF_WIDTH(16),
        .ACC_WIDTH(40)
    ) u_fir (
        .clk          (clk),
        .rst_n        (rst_n),
        .bypass       (reg_config[0]),
        .sink_valid   (stream_in_valid),
        .sink_ready   (stream_in_ready),
        .sink_data    (stream_in_data),
        .source_valid (fir_source_valid),
        .source_ready (fir_source_ready),
        .source_data  (fir_source_data)
    );

    // 3. Circular Ring Buffer (1024 words dual-port RAM)
    ch04_ring_buffer #(
        .DATA_WIDTH(16),
        .ADDR_WIDTH(RING_ADDR_W),
        .FRAME_LEN(FRAME_LEN),
        .HOP_LEN(HOP_LEN),
        .REGISTERED_OUTPUT(1)
    ) u_ring_buffer (
        .clk              (clk),
        .rst_n            (rst_n),
        .clr              (core_clr),
        .sink_valid       (fir_source_valid),
        .sink_ready       (fir_source_ready),
        .sink_data        (fir_source_data),
        .frame_ready      (ring_frame_ready),
        .frame_step       (ring_frame_step),
        .frame_idx        (ring_frame_idx),
        .sample_count_out (ring_sample_count),
        .rd_base          (ring_rd_base),
        .rd_en            (ring_rd_en),
        .rd_sample_idx    (ring_rd_sample_idx),
        .rd_data          (ring_rd_data),
        .rd_valid         (ring_rd_valid)
    );

    // 4. Local Mean Calculation & Subtraction
    ch05_local_mean #(
        .DATA_WIDTH(16),
        .ADDR_WIDTH(RING_ADDR_W),
        .SPAN_LEN(426),
        .SPAN_OFFSET(106),
        .MULT_M(24'd10082083),
        .SHIFT_K(32)
    ) u_local_mean (
        .clk            (clk),
        .rst_n          (rst_n),
        .start          (mean_start),
        .busy           (mean_busy),
        .mean_valid     (mean_valid),
        .mean_out       (mean_out),
        .rd_en          (mean_rd_en),
        .rd_sample_idx  (mean_rd_sample_idx),
        .rd_valid       (mean_rd_valid),
        .rd_data        (ring_rd_data),
        .sub_valid_in   (mean_sub_valid_in),
        .sub_data_in    (ring_rd_data),
        .diff_valid_out (mean_diff_valid_out),
        .diff_data_out  (mean_diff_data_out)
    );

    // 5. Hanning Windowing & LocalPeak Detector
    ch06_hanning_window #(
        .DATA_W(17),
        .ROM_W(16),
        .PROD_W(34),
        .N_SAMPLES(FRAME_LEN),
        .LP_FIRST(212),
        .LP_LAST(425),
        .INIT_FILE("golden_v2/rom/hanning638_q15.hex")
    ) u_hanning_window (
        .clk       (clk),
        .rst_n     (rst_n),
        .start     (win_start),
        .busy      (win_busy),
        .in_valid  (mean_diff_valid_out),
        .in_d      (mean_diff_data_out),
        .out_valid (win_out_valid),
        .out_xw    (win_out_xw),
        .out_done  (win_out_done),
        .out_lp    (win_out_lp)
    );

    // 6. Autocorrelation MAC Engine
    ch07_mac_engine #(
        .DATA_W(17),
        .DEPTH(FRAME_LEN),
        .ADDR_W(RING_ADDR_W),
        .ACC_W(48),
        .TAU_SCAN_MIN(26),
        .TAU_SCAN_MAX(214),
        .N_LAGS(190)
    ) u_mac_engine (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_en     (win_out_valid),
        .load_addr   (mac_load_addr),
        .load_data   (win_out_xw),
        .start       (mac_start),
        .busy        (mac_busy),
        .done        (mac_done),
        .out_valid   (mac_out_valid),
        .out_tau     (mac_out_tau),
        .out_R       (mac_out_R),
        .cycle_count (mac_cycle_count)
    );

    // 7. Normalization & Subtractive Octave Cost Scoring
    ch08_norm_score #(
        .IN_W(48),
        .RN_W(27),
        .R0N_W(26),
        .OUT_W(28),
        .TAU_SCAN_MIN(26),
        .TAU_SCAN_MAX(214),
        .INIT_FILE("golden_v2/rom/ck_rom.hex")
    ) u_norm_score (
        .clk       (clk),
        .rst_n     (rst_n),
        .in_valid  (mac_out_valid),
        .in_tau    (mac_out_tau),
        .in_R      (mac_out_R),
        .out_valid (norm_out_valid),
        .out_tau   (norm_out_tau),
        .out_U     (norm_out_U),
        .out_Sc    (norm_out_Sc),
        .out_R0n   (norm_out_R0n),
        .out_sh    (norm_out_sh),
        .out_last  (norm_out_last)
    );

    // 8. Peak Finder & Parabolic F0 Single-Division Calculator
    ch09_f0_calc u_f0_calc (
        .clk          (clk),
        .rst_n        (rst_n),
        .in_valid     (norm_out_valid),
        .in_tau       (norm_out_tau),
        .in_U         (norm_out_U),
        .in_Sc        (norm_out_Sc),
        .in_R0n       ({1'b0, norm_out_R0n}),
        .in_last      (norm_out_last),
        .out_valid    (calc_out_valid),
        .out_f0_raw   (calc_out_f0_raw),
        .out_best_tau (calc_out_best_tau),
        .out_sc       (calc_out_sc),
        .out_r0n      (calc_out_r0n),
        .out_found    (calc_out_found)
    );

    // 9. Voicing Decision Gate
    ch10_voicing u_voicing (
        .clk           (clk),
        .rst_n         (rst_n),
        .in_valid      (calc_out_valid),
        .in_f0_raw     (calc_out_f0_raw),
        .in_sc         (calc_out_sc),
        .in_r0n        (calc_out_r0n),
        .in_cand_found (calc_out_found),
        .in_lp         (latched_lp),
        .in_gp         (reg_global_peak),
        .out_valid     (voice_out_valid),
        .out_f0        (voice_out_f0),
        .out_voiced    (voice_out_voiced),
        .out_lhs       (),
        .out_rhs       ()
    );

    // 10. 3-Point Causal Median Filter with Flush Beat
    ch11_median3 u_median3 (
        .clk       (clk),
        .rst_n     (rst_n),
        .in_valid  (med_in_valid),
        .in_first  (med_in_first),
        .in_last   (med_in_last),
        .in_f0     (med_in_f0),
        .out_valid (med_out_valid),
        .out_last  (med_out_last),
        .out_f0    (med_out_f0)
    );

    // 11. Output FIFO (Avalon-ST sink -> Avalon-MM read slave)
    ch01_fifo_out #(
        .ADDR_WIDTH(FIFO_OUT_ADDR_W)
    ) u_fifo_out (
        .clk            (clk),
        .rst_n          (rst_n),
        .st_data        (med_out_f0),
        .st_valid       (med_out_valid),
        .st_ready       (fifo_out_st_ready),
        .mm_read        (mm_out_read),
        .mm_readdata    (mm_out_readdata),
        .mm_waitrequest (mm_out_waitrequest),
        .csr_read       (csr_out_read),
        .csr_address    (csr_out_address),
        .csr_readdata   (csr_out_readdata)
    );

endmodule
