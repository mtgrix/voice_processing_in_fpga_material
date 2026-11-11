// ============================================================================
// File: rtl/v3/ch04_ring_buffer.v
// Module: ch04_ring_buffer
// Description:
//   Circular Ring Buffer (1024x16) for Frame Slicing and Overlap Management
//   in FPGA Praat F0 estimation.
//
// Parameters:
//   DATA_WIDTH = 16      : signed audio sample width
//   ADDR_WIDTH = 10      : 1024 words capacity (fits 2x Intel M10K blocks)
//   FRAME_LEN  = 638     : Praat 7.0.03 analysis window (Sound_to_Pitch.cpp:339)
//   HOP_LEN    = 160     : 10 ms hop at 16 kHz (Sound_to_Pitch.cpp:296)
//   REGISTERED_OUTPUT = 1: 1 = latency 2 (q registered), 0 = latency 1
//
// Theory:
//   - Storage requirement: >= FRAME_LEN + HOP_LEN = 638 + 160 = 798 words.
//   - Natural 10-bit circular wrapping: (rd_base + hop) % 1024.
//   - Sequence of rd_base: 0, 160, 320, 480, 640, 800, 960, 96, 256, ...
//   - Overlap: 638 - 160 = 478 samples reused across consecutive frames.
// ============================================================================

`timescale 1ns / 1ps

module ch04_ring_buffer #(
    parameter DATA_WIDTH        = 16,
    parameter ADDR_WIDTH        = 10,
    parameter FRAME_LEN         = 638,
    parameter HOP_LEN           = 160,
    parameter REGISTERED_OUTPUT = 1
)(
    input  wire                         clk,
    input  wire                         rst_n,
    input  wire                         clr,

    // Avalon-ST Sink Interface (Audio input stream)
    input  wire                         sink_valid,
    output wire                         sink_ready,
    input  wire signed [DATA_WIDTH-1:0] sink_data,

    // Frame Management Handshake
    output wire                         frame_ready,
    input  wire                         frame_step,
    output reg  [15:0]                  frame_idx,
    output wire [ADDR_WIDTH:0]          sample_count_out,
    output reg  [ADDR_WIDTH-1:0]        rd_base,

    // Frame Reader Interface (Direct random-access read port B)
    input  wire                         rd_en,
    input  wire [ADDR_WIDTH-1:0]        rd_sample_idx,
    output wire signed [DATA_WIDTH-1:0] rd_data,
    output wire                         rd_valid
);

    localparam BUFFER_DEPTH = (1 << ADDR_WIDTH); // 1024 words
    localparam SAFE_LIMIT   = BUFFER_DEPTH - 4;  // 1020 words backpressure threshold

    // Write pointer and occupancy tracking
    reg [ADDR_WIDTH-1:0] wr_ptr;
    reg [ADDR_WIDTH:0]   sample_count; // Tracks unconsumed samples (0 to 1024)

    // Backpressure: assert ready when buffer has free space
    assign sink_ready = (sample_count < SAFE_LIMIT);
    wire write_fire   = sink_valid && sink_ready;

    // Frame readiness: at least 638 samples available in buffer
    assign frame_ready = (sample_count >= FRAME_LEN);
    assign sample_count_out = sample_count;

    // Inferred Synchronous Dual-Port RAM (Maps to 2x M10K in Cyclone V)
    reg signed [DATA_WIDTH-1:0] ram [0:BUFFER_DEPTH-1];
    reg signed [DATA_WIDTH-1:0] ram_q;

    // Port A: Synchronous Write
    always @(posedge clk) begin
        if (write_fire) begin
            ram[wr_ptr] <= sink_data;
        end
    end

    // Physical read address: natural 10-bit addition (modulo 1024)
    wire [ADDR_WIDTH-1:0] rd_phys_addr = rd_base + rd_sample_idx;

    // Port B: Synchronous Read (Registered read address)
    always @(posedge clk) begin
        if (rd_en) begin
            ram_q <= ram[rd_phys_addr];
        end
    end

    // Latency pipeline registers for read data and valid flag
    generate
        if (REGISTERED_OUTPUT) begin : gen_reg_output
            // Latency = 2 cycles: address registered + output q registered
            reg signed [DATA_WIDTH-1:0] rd_data_r;
            reg                         rd_en_d1;
            reg                         rd_valid_r;

            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    rd_data_r  <= {DATA_WIDTH{1'b0}};
                    rd_en_d1   <= 1'b0;
                    rd_valid_r <= 1'b0;
                end else if (clr) begin
                    rd_data_r  <= {DATA_WIDTH{1'b0}};
                    rd_en_d1   <= 1'b0;
                    rd_valid_r <= 1'b0;
                end else begin
                    rd_en_d1   <= rd_en;
                    rd_valid_r <= rd_en_d1;
                    if (rd_en_d1) begin
                        rd_data_r <= ram_q;
                    end
                end
            end

            assign rd_data  = rd_data_r;
            assign rd_valid = rd_valid_r;
        end else begin : gen_unreg_output
            // Latency = 1 cycle: address registered, output unlatched
            reg rd_valid_r;

            always @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    rd_valid_r <= 1'b0;
                end else if (clr) begin
                    rd_valid_r <= 1'b0;
                end else begin
                    rd_valid_r <= rd_en;
                end
            end

            assign rd_data  = ram_q;
            assign rd_valid = rd_valid_r;
        end
    endgenerate

    // Write pointer and sample counter update
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr       <= {ADDR_WIDTH{1'b0}};
            rd_base      <= {ADDR_WIDTH{1'b0}};
            sample_count <= {(ADDR_WIDTH+1){1'b0}};
            frame_idx    <= 16'd0;
        end else if (clr) begin
            wr_ptr       <= {ADDR_WIDTH{1'b0}};
            rd_base      <= {ADDR_WIDTH{1'b0}};
            sample_count <= {(ADDR_WIDTH+1){1'b0}};
            frame_idx    <= 16'd0;
        end else begin
            // 1. Advance write pointer upon valid write
            if (write_fire) begin
                wr_ptr <= wr_ptr + 10'd1;
            end

            // 2. Advance read base and frame index upon frame step
            if (frame_step && frame_ready) begin
                rd_base   <= rd_base + HOP_LEN[ADDR_WIDTH-1:0];
                frame_idx <= frame_idx + 16'd1;
            end

            // 3. Update sample counter (atomic tracking of net inflow/outflow)
            case ({write_fire, (frame_step && frame_ready)})
                2'b10: sample_count <= sample_count + 11'd1;
                2'b01: sample_count <= sample_count - HOP_LEN[ADDR_WIDTH:0];
                2'b11: sample_count <= sample_count + 11'd1 - HOP_LEN[ADDR_WIDTH:0];
                default: sample_count <= sample_count;
            endcase
        end
    end

endmodule
