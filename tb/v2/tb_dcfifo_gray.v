// tb/v2/tb_dcfifo_gray.v
`timescale 1ns/1ps

module tb_dcfifo_gray;
    reg aclr;
    reg wrclk;
    reg wrreq;
    reg [15:0] wrdata;
    wire wrfull;

    reg rdclk;
    reg rdreq;
    wire [15:0] rddata;
    wire rdempty;

    dcfifo_gray #(
        .DATA_WIDTH(16),
        .ADDR_WIDTH(4),
        .SHOWAHEAD(1)
    ) dut (
        .aclr(aclr),
        .wrclk(wrclk),
        .wrreq(wrreq),
        .data(wrdata),
        .wrfull(wrfull),
        .rdclk(rdclk),
        .rdreq(rdreq),
        .q(rddata),
        .rdempty(rdempty)
    );

    // wrclk: ~3.072 MHz -> period 325 ns -> #162.5
    always #162.5 wrclk = ~wrclk;

    // rdclk: 50 MHz -> period 20 ns -> #10
    always #10 rdclk = ~rdclk;

    reg [15:0] test_data [0:9];
    integer i;

    initial begin
        test_data[0] = 16'd100;
        test_data[1] = 16'd200;
        test_data[2] = 16'd300;
        test_data[3] = 16'd400;
        test_data[4] = 16'd500;
        test_data[5] = 16'd16384;
        test_data[6] = 16'd32767;
        test_data[7] = 16'd11;
        test_data[8] = 16'd42;
        test_data[9] = 16'd9999;

        wrclk  = 0;
        rdclk  = 0;
        aclr   = 1;
        wrreq  = 0;
        wrdata = 0;
        rdreq  = 0;

        #200;
        aclr = 0;
        #500;

        // Write 10 samples into FIFO on wrclk
        for (i = 0; i < 10; i = i + 1) begin
            @(posedge wrclk);
            wrreq  <= 1'b1;
            wrdata <= test_data[i];
            @(posedge wrclk);
            wrreq  <= 1'b0;
            #300;
        end

        // Wait for 2FF synchronization
        #2000;

        // Read all 10 samples on rdclk (showahead mode: rddata is valid whenever rdempty is low)
        while (!rdempty) begin
            @(posedge rdclk);
            $display("OUT_FIFO:%0d", rddata);
            rdreq <= 1'b1;
            @(posedge rdclk);
            rdreq <= 1'b0;
            #40;
        end

        #500;
        $display("DCFIFO_SIM_DONE");
        $finish;
    end
endmodule
