// ============================================================================
// File: rtl/v3/ch01_fifo_out.v
// Module: ch01_fifo_out
// Description:
//   Output F0 FIFO buffer returning estimated pitch values from FPGA core to HPS.
//   - Input side: Avalon-ST sink 16-bit (accepts Q12.4 F0 words, 0 for unvoiced).
//   - Memory: 512 x 16-bit synchronous dual-port RAM inferred in 1 M10K block
//     (Cyclone V M10K = 10,240 bits; 512x16 = 8,192 bits).
//     Can hold up to 512 frame results (> 5 seconds of audio analysis).
//   - Output side: Avalon-MM read slave for HPS (read F0 data words).
//   - CSR side: provides fill_level (number of frame words ready to read).
// ============================================================================

`timescale 1ns/1ps

module ch01_fifo_out #(
    parameter integer ADDR_WIDTH = 9  // 2^9 = 512 words of 16-bit
)(
    input  wire        clk,
    input  wire        rst_n,

    // ------------------------------------------------------------------------
    // Avalon-ST Sink (from FPGA core)
    // ------------------------------------------------------------------------
    input  wire [15:0] st_data,
    input  wire        st_valid,
    output wire        st_ready,

    // ------------------------------------------------------------------------
    // Avalon-MM Data Read Slave (fifo_out)
    // ------------------------------------------------------------------------
    input  wire        mm_read,
    output wire [31:0] mm_readdata,
    output wire        mm_waitrequest,

    // ------------------------------------------------------------------------
    // Avalon-MM CSR Read Slave (fifo_out_csr)
    // ------------------------------------------------------------------------
    input  wire        csr_read,
    input  wire [2:0]  csr_address,
    output reg  [31:0] csr_readdata
);

    localparam integer DEPTH = 1 << ADDR_WIDTH; // 512 words

    // Inferred dual-port RAM
    reg [15:0] mem [0:DEPTH-1];
    reg [15:0] rdata_reg;

    reg [ADDR_WIDTH:0] wr_ptr;
    reg [ADDR_WIDTH:0] rd_ptr;

    wire [ADDR_WIDTH-1:0] wr_addr = wr_ptr[ADDR_WIDTH-1:0];
    wire [ADDR_WIDTH-1:0] rd_addr = rd_ptr[ADDR_WIDTH-1:0];

    wire fifo_empty = (wr_ptr == rd_ptr);
    wire fifo_full  = (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
                      (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]);

    wire [ADDR_WIDTH:0] words_used = wr_ptr - rd_ptr;

    // st_ready high when FIFO has space
    assign st_ready = !fifo_full;

    // mm_waitrequest high when reading from empty FIFO
    assign mm_waitrequest = mm_read && fifo_empty;

    // Push into FIFO
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            if (st_valid && st_ready) begin
                mem[wr_addr] <= st_data;
                wr_ptr       <= wr_ptr + 1'b1;
            end
        end
    end

    // Pop from FIFO on mm_read
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr    <= {(ADDR_WIDTH+1){1'b0}};
            rdata_reg <= 16'd0;
        end else begin
            if (mm_read && !fifo_empty) begin
                rdata_reg <= mem[rd_addr];
                rd_ptr    <= rd_ptr + 1'b1;
            end
        end
    end

    assign mm_readdata = {16'd0, rdata_reg};

    // CSR interface
    always @(*) begin
        case (csr_address)
            3'd0: csr_readdata = {22'd0, words_used};
            3'd1: csr_readdata = {30'd0, fifo_full, fifo_empty};
            default: csr_readdata = 32'd0;
        endcase
    end

endmodule
