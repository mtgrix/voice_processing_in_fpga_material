// tb/v2/tb_dc_block_iir.v
`timescale 1ns/1ps

module tb_dc_block_iir;
    reg                 clk;
    reg                 rst_n;
    reg                 in_valid;
    wire                in_ready;
    reg  signed [15:0]  x_in;
    wire                out_valid;
    reg                 out_ready;
    wire signed [15:0]  y_out;

    dc_block_iir dut (
        .clk(clk),
        .rst_n(rst_n),
        .in_valid(in_valid),
        .in_ready(in_ready),
        .x_in(x_in),
        .out_valid(out_valid),
        .out_ready(out_ready),
        .y_out(y_out)
    );

    // 50 MHz clock -> period 20 ns
    always #10 clk = ~clk;

    // Monitor outputs
    integer out_count;
    always @(posedge clk) begin
        if (out_valid && out_ready) begin
            $display("OUT_SAMPLE:%0d:%0d", out_count, y_out);
            out_count = out_count + 1;
        end
    end

    integer i;

    initial begin
        clk       = 0;
        rst_n     = 0;
        in_valid  = 0;
        x_in      = 0;
        out_ready = 1;
        out_count = 0;

        #100;
        rst_n = 1;
        #40;

        // Feed 3 zeros, then 1600 samples of 16384 (step of +0.5 in Q1.15)
        for (i = 0; i < 1603; i = i + 1) begin
            @(posedge clk);
            while (!in_ready) @(posedge clk); // wait if backpressure
            in_valid <= 1'b1;
            if (i < 3)
                x_in <= 16'sd0;
            else
                x_in <= 16'sd16384;
        end

        @(posedge clk);
        in_valid <= 1'b0;

        // Wait for pipeline to drain
        #500;
        $display("DC_BLOCK_SIM_DONE");
        $finish;
    end
endmodule
