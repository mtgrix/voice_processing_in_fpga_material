// ============================================================================
// File: rtl/v3/ch01_avalon_fifo.v
// Module: ch01_avalon_fifo
// Description:
//   Input audio FIFO buffer connecting HPS to FPGA DSP pipeline.
//   - Input side: Avalon-MM 32-bit write slave (from Lightweight HPS-to-FPGA bridge).
//     Each 32-bit write packs two 16-bit PCM audio samples (little-endian:
//     lower 16 bits [15:0] = sample n, upper 16 bits [31:16] = sample n+1).
//   - Memory: 256 x 32-bit dual-port synchronous RAM inferred into 1 M10K block
//     (Cyclone V M10K = 10,240 bits; 256x32 = 8,192 bits).
//     Total capacity: 512 16-bit audio samples (> 3 hops of 160 samples).
//   - Output side: Avalon-ST 16-bit source with valid/ready handshake.
//     An internal unpacker streams sample n followed by sample n+1.
//   - Status/CSR side (in_csr): Avalon-MM read slave exposing fill_level (in
//     16-bit sample units: 0..512), empty, full, almost_full, almost_empty,
//     and overflow sticky flag.
//   - Backpressure & flow control:
//     - Downstream Avalon-ST: halts reading when st_ready is low.
//     - Upstream Avalon-MM: asserts waitrequest when FIFO is full (words_used == 256).
// ============================================================================

`timescale 1ns/1ps

module ch01_avalon_fifo #(
    parameter integer ADDR_WIDTH = 8  // 2^8 = 256 words (32-bit) = 512 samples (16-bit)
)(
    input  wire        clk,
    input  wire        rst_n,

    // ------------------------------------------------------------------------
    // Avalon-MM Data Write Slave (fifo_in)
    // ------------------------------------------------------------------------
    input  wire        mm_write,
    input  wire [31:0] mm_writedata,
    output wire        mm_waitrequest,

    // ------------------------------------------------------------------------
    // Avalon-MM CSR Read Slave (fifo_in_csr)
    // ------------------------------------------------------------------------
    input  wire        csr_read,
    input  wire [2:0]  csr_address,
    output reg  [31:0] csr_readdata,

    // ------------------------------------------------------------------------
    // Avalon-ST Data Source (to FPGA core)
    // ------------------------------------------------------------------------
    output wire [15:0] st_data,
    output wire        st_valid,
    input  wire        st_ready
);

    localparam integer DEPTH_WORDS   = 1 << ADDR_WIDTH; // 256 words
    localparam integer DEPTH_SAMPLES = DEPTH_WORDS * 2;  // 512 samples

    // ------------------------------------------------------------------------
    // Inferred Dual-Port Synchronous RAM (1 M10K block)
    // ------------------------------------------------------------------------
    reg [31:0] mem [0:DEPTH_WORDS-1];
    reg [31:0] mem_rdata;

    // ------------------------------------------------------------------------
    // Word-level FIFO pointers with wrap bit
    // ------------------------------------------------------------------------
    reg [ADDR_WIDTH:0] wr_ptr; // 9 bits (bit 8 is wrap bit)
    reg [ADDR_WIDTH:0] rd_ptr;

    wire [ADDR_WIDTH-1:0] wr_addr = wr_ptr[ADDR_WIDTH-1:0];
    wire [ADDR_WIDTH-1:0] rd_addr = rd_ptr[ADDR_WIDTH-1:0];

    wire fifo_empty = (wr_ptr == rd_ptr);
    wire fifo_full  = (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
                      (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]);

    wire [ADDR_WIDTH:0] words_used = wr_ptr - rd_ptr;

    // mm_waitrequest asserted when full and master attempts to write
    assign mm_waitrequest = fifo_full;

    // Sticky overflow flag
    reg ovf_sticky;

    // ------------------------------------------------------------------------
    // RAM Write Port (Avalon-MM)
    // ------------------------------------------------------------------------
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr     <= {(ADDR_WIDTH+1){1'b0}};
            ovf_sticky <= 1'b0;
        end else begin
            if (mm_write) begin
                if (!fifo_full) begin
                    mem[wr_addr] <= mm_writedata;
                    wr_ptr       <= wr_ptr + 1'b1;
                end else begin
                    ovf_sticky <= 1'b1;
                end
            end
        end
    end

    // ------------------------------------------------------------------------
    // Unpacker FSM / Output Streaming (Avalon-ST)
    // State machine reads 32-bit word, unpacks low 16-bit, then high 16-bit
    // ------------------------------------------------------------------------
    localparam [1:0] ST_IDLE    = 2'b00;
    localparam [1:0] ST_FETCH   = 2'b01;
    localparam [1:0] ST_UNPACK0 = 2'b10;
    localparam [1:0] ST_UNPACK1 = 2'b11;

    reg [1:0]  st_state;
    reg [31:0] holding_word;

    // RAM Read port
    always @(posedge clk) begin
        mem_rdata <= mem[rd_addr];
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr       <= {(ADDR_WIDTH+1){1'b0}};
            st_state     <= ST_IDLE;
            holding_word <= 32'd0;
        end else begin
            case (st_state)
                ST_IDLE: begin
                    if (!fifo_empty) begin
                        // RAM registered read takes 1 cycle
                        st_state <= ST_FETCH;
                        rd_ptr   <= rd_ptr + 1'b1;
                    end
                end

                ST_FETCH: begin
                    // mem_rdata is now valid from RAM
                    holding_word <= mem_rdata;
                    st_state     <= ST_UNPACK0;
                end

                ST_UNPACK0: begin
                    // Emitting lower 16 bits [15:0]
                    if (st_ready) begin
                        st_state <= ST_UNPACK1;
                    end
                end

                ST_UNPACK1: begin
                    // Emitting upper 16 bits [31:16]
                    if (st_ready) begin
                        if (!fifo_empty) begin
                            st_state <= ST_FETCH;
                            rd_ptr   <= rd_ptr + 1'b1;
                        end else begin
                            st_state <= ST_IDLE;
                        end
                    end
                end
            endcase
        end
    end

    assign st_valid = (st_state == ST_UNPACK0) || (st_state == ST_UNPACK1);
    assign st_data  = (st_state == ST_UNPACK0) ? holding_word[15:0] : holding_word[31:16];

    // ------------------------------------------------------------------------
    // Fill Level in Sample Units (0..512)
    // ------------------------------------------------------------------------
    // Samples inside RAM: words_used * 2
    // Samples inside holding_word unpacker:
    //   ST_UNPACK0: 2 samples remain
    //   ST_UNPACK1: 1 sample remains
    //   ST_FETCH:   2 samples in flight
    wire [1:0] unpacker_samples = (st_state == ST_UNPACK0) ? 2'd2 :
                                  (st_state == ST_UNPACK1) ? 2'd1 :
                                  (st_state == ST_FETCH)   ? 2'd2 : 2'd0;

    wire [9:0] total_samples_used = {words_used, 1'b0} + {8'd0, unpacker_samples};

    // ------------------------------------------------------------------------
    // CSR Read Port (fifo_in_csr)
    // Address map:
    //   0x0 (offset 0): fill_level (sample units: 0..512)
    //   0x1 (offset 1): status: [0] empty, [1] full, [2] almost_empty, [3] almost_full
    //   0x2 (offset 2): event / overflow sticky
    //   0x3 (offset 3): words_used (0..256)
    // ------------------------------------------------------------------------
    wire almost_empty = (total_samples_used <= 10'd32);
    wire almost_full  = (total_samples_used >= 10'd480);

    always @(*) begin
        case (csr_address)
            3'd0: csr_readdata = {22'd0, total_samples_used};
            3'd1: csr_readdata = {28'd0, almost_full, almost_empty, fifo_full, (total_samples_used == 10'd0)};
            3'd2: csr_readdata = {31'd0, ovf_sticky};
            3'd3: csr_readdata = {23'd0, words_used};
            default: csr_readdata = 32'd0;
        endcase
    end

endmodule
