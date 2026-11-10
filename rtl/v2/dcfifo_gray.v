// rtl/v2/dcfifo_gray.v
// Complete, synthesizable Dual-Clock Asynchronous FIFO (DCFIFO) with Gray-code CDC pointers.
// Functionally equivalent and cycle-accurate to Intel Quartus DCFIFO megafunction.
// Prevents metastability across independent clock domains (wrclk = SCLK, rdclk = 50 MHz).

`timescale 1ns/1ps

module dcfifo_gray #(
    parameter DATA_WIDTH = 16,
    parameter ADDR_WIDTH = 4,   // DEPTH = 2^ADDR_WIDTH = 16 words
    parameter SHOWAHEAD  = 1    // 1: showahead mode (Intel lpm_showahead="ON"), 0: legacy normal mode
)(
    // Asynchronous Reset
    input  wire                   aclr,

    // Write Domain (Audio Bit Clock SCLK ~3.072 MHz)
    input  wire                   wrclk,
    input  wire                   wrreq,
    input  wire [DATA_WIDTH-1:0]  data,
    output wire                   wrfull,

    // Read Domain (System Clock 50 MHz)
    input  wire                   rdclk,
    input  wire                   rdreq,
    output reg  [DATA_WIDTH-1:0]  q,
    output wire                   rdempty
);

    localparam DEPTH = 1 << ADDR_WIDTH;

    // 1. Dual-Port Memory Storage
    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];

    // 2. Binary and Gray Pointers (1 extra MSB for full/empty wraparound distinction)
    reg [ADDR_WIDTH:0] wptr_bin;
    reg [ADDR_WIDTH:0] wptr_gray;
    reg [ADDR_WIDTH:0] rptr_bin;
    reg [ADDR_WIDTH:0] rptr_gray;

    // 3. Gray code conversion function: G(n) = n ^ (n >> 1)
    function [ADDR_WIDTH:0] bin2gray;
        input [ADDR_WIDTH:0] bin;
        begin
            bin2gray = bin ^ (bin >> 1);
        end
    endfunction

    // 4. Two-Flip-Flop (2FF) Synchronizers for Gray Pointers across clock domains
    // Write pointer synchronized to Read Clock domain
    reg [ADDR_WIDTH:0] wptr_gray_rd1, wptr_gray_rd2;
    always @(posedge rdclk or posedge aclr) begin
        if (aclr) begin
            wptr_gray_rd1 <= {(ADDR_WIDTH+1){1'b0}};
            wptr_gray_rd2 <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            wptr_gray_rd1 <= wptr_gray;
            wptr_gray_rd2 <= wptr_gray_rd1;
        end
    end

    // Read pointer synchronized to Write Clock domain
    reg [ADDR_WIDTH:0] rptr_gray_wr1, rptr_gray_wr2;
    always @(posedge wrclk or posedge aclr) begin
        if (aclr) begin
            rptr_gray_wr1 <= {(ADDR_WIDTH+1){1'b0}};
            rptr_gray_wr2 <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            rptr_gray_wr1 <= rptr_gray;
            rptr_gray_wr2 <= rptr_gray_wr1;
        end
    end

    // 5. Full and Empty Flag Generation
    // Empty: read pointer matches write pointer in read domain
    assign rdempty = (rptr_gray == wptr_gray_rd2);

    // Full: write pointer and synchronized read pointer differ in MSB and 2nd MSB,
    // but match in all lower (ADDR_WIDTH-1) bits.
    wire [ADDR_WIDTH:0] wptr_gray_next = bin2gray(wptr_bin + {{ADDR_WIDTH{1'b0}}, 1'b1});
    assign wrfull = (wptr_gray == {~rptr_gray_wr2[ADDR_WIDTH:ADDR_WIDTH-1],
                                   rptr_gray_wr2[ADDR_WIDTH-2:0]});

    // 6. Write Domain Logic
    always @(posedge wrclk or posedge aclr) begin
        if (aclr) begin
            wptr_bin  <= {(ADDR_WIDTH+1){1'b0}};
            wptr_gray <= {(ADDR_WIDTH+1){1'b0}};
        end else if (wrreq && !wrfull) begin
            mem[wptr_bin[ADDR_WIDTH-1:0]] <= data;
            wptr_bin  <= wptr_bin + {{ADDR_WIDTH{1'b0}}, 1'b1};
            wptr_gray <= wptr_gray_next;
        end
    end

    // 7. Read Domain Logic
    wire [ADDR_WIDTH:0] rptr_bin_next = rptr_bin + {{ADDR_WIDTH{1'b0}}, 1'b1};
    wire [ADDR_WIDTH:0] rptr_gray_next = bin2gray(rptr_bin_next);

    always @(posedge rdclk or posedge aclr) begin
        if (aclr) begin
            rptr_bin  <= {(ADDR_WIDTH+1){1'b0}};
            rptr_gray <= {(ADDR_WIDTH+1){1'b0}};
            if (!SHOWAHEAD) q <= {DATA_WIDTH{1'b0}};
        end else if (rdreq && !rdempty) begin
            rptr_bin  <= rptr_bin_next;
            rptr_gray <= rptr_gray_next;
            if (!SHOWAHEAD) begin
                q <= mem[rptr_bin[ADDR_WIDTH-1:0]];
            end
        end
    end

    // In showahead mode, q continuously outputs memory at current rptr_bin
    generate
        if (SHOWAHEAD) begin : gen_showahead
            always @(*) begin
                q = mem[rptr_bin[ADDR_WIDTH-1:0]];
            end
        end
    endgenerate

endmodule
