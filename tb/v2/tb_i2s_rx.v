// tb/v2/tb_i2s_rx.v
`timescale 1ns/1ps

module tb_i2s_rx;
    reg sclk;
    reg rst_n;
    reg ws;
    reg sdat;
    wire signed [15:0] sample_left;
    wire sample_valid;

    i2s_rx #(.W(16)) dut (
        .sclk(sclk),
        .rst_n(rst_n),
        .ws(ws),
        .sdat(sdat),
        .sample_left(sample_left),
        .sample_valid(sample_valid)
    );

    // SCLK 3.072 MHz -> period ~ 325.52 ns
    always #162.76 sclk = ~sclk;

    // Task to send one 32-bit slot for Left channel and one 32-bit slot for Right channel
    task send_i2s_frame(input [15:0] left_data, input [15:0] right_data);
        integer i;
        begin
            // 1. Left Channel: ws falls to 0
            @(negedge sclk);
            ws = 1'b0;
            sdat = 1'b0; // Philips delay cycle: 1 SCLK bit before MSB

            // Send 16-bit MSB first
            for (i = 15; i >= 0; i = i - 1) begin
                @(negedge sclk);
                sdat = left_data[i];
            end

            // Remaining 16 bits of 32-bit slot (padding zeros)
            for (i = 0; i < 16; i = i + 1) begin
                @(negedge sclk);
                sdat = 1'b0;
            end

            // 2. Right Channel: ws rises to 1
            @(negedge sclk);
            ws = 1'b1;
            sdat = 1'b0; // Philips delay cycle

            for (i = 15; i >= 0; i = i - 1) begin
                @(negedge sclk);
                sdat = right_data[i];
            end

            for (i = 0; i < 16; i = i + 1) begin
                @(negedge sclk);
                sdat = 1'b0;
            end
        end
    endtask

    // Monitor outputs
    always @(posedge sclk) begin
        if (sample_valid) begin
            $display("OUT_SAMPLE:%0d", sample_left);
        end
    end

    reg [15:0] test_samples [0:7];

    integer k;
    initial begin
        test_samples[0] = 16'sd16384;
        test_samples[1] = -16'sd16384;
        test_samples[2] = 16'sd1234;
        test_samples[3] = -16'sd32768;
        test_samples[4] = 16'sd32767;
        test_samples[5] = 16'sd0;
        test_samples[6] = 16'sd11;
        test_samples[7] = -16'sd1;

        sclk  = 0;
        rst_n = 0;
        ws    = 1;
        sdat  = 0;

        #500;
        rst_n = 1;
        #500;

        for (k = 0; k < 8; k = k + 1) begin
            send_i2s_frame(test_samples[k], 16'h0000);
        end

        #2000;
        $display("I2S_SIM_DONE");
        $finish;
    end
endmodule
