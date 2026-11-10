// tb/v2/tb_q15_saturate.v
`timescale 1ns/1ps

module tb_q15_saturate;

    reg clk;
    reg rst_n;
    reg valid_in;
    reg signed [31:0] data_in;
    wire valid_out;
    wire signed [15:0] data_out;

    q15_saturate dut (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .data_in(data_in),
        .valid_out(valid_out),
        .data_out(data_out)
    );

    always #5 clk = ~clk;

    reg signed [31:0] vec [0:9];
    integer i;

    initial begin
        vec[0] = 32'sd0;
        vec[1] = 32'sd1073709056;
        vec[2] = 32'sd2000000000;
        vec[3] = -32'sd2000000000;
        vec[4] = 32'sd16384;
        vec[5] = 32'sd16383;
        vec[6] = -32'sd16384;
        vec[7] = -32'sd16385;
        vec[8] = -32'sd536870912;
        vec[9] = 32'sd1073730000;

        clk = 0;
        rst_n = 0;
        valid_in = 0;
        data_in = 0;
        #22;
        rst_n = 1;
        #10;

        for (i = 0; i < 10; i = i + 1) begin
            @(posedge clk);
            #1;
            valid_in = 1'b1;
            data_in  = vec[i];
        end

        @(posedge clk);
        #1;
        valid_in = 1'b0;
        data_in  = 0;

        #100;
        $finish;
    end

    always @(posedge clk) begin
        if (valid_out) begin
            $display("OUT: %d", data_out);
        end
    end

endmodule
