// rtl/v2/ch01_step02_framing_cnt.v
// Framing controller for Step 2: manages sample counting, hop triggering,
// and window indexing for L=640 samples and H=160 hop.
`timescale 1ns/1ps

module ch01_step02_framing_cnt (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        sample_valid,
    output reg         frame_ready,    // Triggers processing every H=160 samples after initial L=640
    output reg  [9:0]  wr_ptr,         // Circular write pointer modulo 640 (0..639)
    output reg  [31:0] total_samples
);

    reg [9:0] hop_cnt;
    reg       initial_fill_done;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr            <= 10'd0;
            hop_cnt           <= 10'd0;
            total_samples     <= 32'd0;
            initial_fill_done <= 1'b0;
            frame_ready       <= 1'b0;
        end else if (sample_valid) begin
            total_samples <= total_samples + 32'd1;

            // Circular write pointer modulo 640
            if (wr_ptr == 10'd639)
                wr_ptr <= 10'd0;
            else
                wr_ptr <= wr_ptr + 10'd1;

            // Hop counting: trigger every 160 samples
            if (!initial_fill_done) begin
                if (total_samples + 32'd1 >= 32'd640) begin
                    initial_fill_done <= 1'b1;
                    hop_cnt           <= 10'd0;
                    frame_ready       <= 1'b1;
                end else begin
                    frame_ready       <= 1'b0;
                end
            end else begin
                if (hop_cnt == 10'd159) begin
                    hop_cnt     <= 10'd0;
                    frame_ready <= 1'b1;
                end else begin
                    hop_cnt     <= hop_cnt + 10'd1;
                    frame_ready <= 1'b0;
                end
            end
        end else begin
            frame_ready <= 1'b0;
        end
    end

endmodule
