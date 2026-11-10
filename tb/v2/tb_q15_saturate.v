// tb/v2/tb_q15_saturate.v: Testbench for q15_saturate module.
// Tests 256 vectors including corner cases and seeded pseudorandom vectors.
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

    reg signed [31:0] mem_in  [0:255];
    reg signed [15:0] mem_exp [0:255];
    integer i, errors;

    initial begin
        clk = 0;
        rst_n = 0;
        valid_in = 0;
        data_in = 0;
        errors = 0;

        $readmemh("tb/v2/q15_vec_in.hex", mem_in);
        $readmemh("tb/v2/q15_vec_exp.hex", mem_exp);

        #22;
        rst_n = 1;
        #10;

        for (i = 0; i < 256; i = i + 1) begin
            @(posedge clk);
            #1;
            valid_in = 1'b1;
            data_in  = mem_in[i];
        end

        @(posedge clk);
        #1;
        valid_in = 1'b0;
        data_in  = 0;

        #100;
        if (errors == 0) begin
            $display("PASS_ALL_256_VECTORS");
        end else begin
            $display("FAILED_WITH_%0d_ERRORS", errors);
        end
        $finish;
    end

    integer out_idx = 0;
    always @(posedge clk) begin
        if (valid_out) begin
            if (data_out !== mem_exp[out_idx]) begin
                $display("MISMATCH at index %0d: in=%0d, got=%0d, exp=%0d",
                         out_idx, mem_in[out_idx], data_out, mem_exp[out_idx]);
                errors = errors + 1;
            end
            out_idx = out_idx + 1;
        end
    end

endmodule
