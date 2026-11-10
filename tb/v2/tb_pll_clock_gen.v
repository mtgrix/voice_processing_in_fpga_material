// tb/v2/tb_pll_clock_gen.v
`timescale 1ns/1ps

module tb_pll_clock_gen;
    reg clk_ref;
    reg rst_n;
    reg mclk_in;
    wire locked;
    wire sclk;
    wire lrck;
    wire sclk_pulse;

    pll_clock_gen #(.LOCK_CYCLES(16)) dut (
        .clk_ref(clk_ref),
        .rst_n(rst_n),
        .mclk_in(mclk_in),
        .locked(locked),
        .sclk(sclk),
        .lrck(lrck),
        .sclk_pulse(sclk_pulse)
    );

    // 50 MHz reference clock: period = 20 ns
    always #10 clk_ref = ~clk_ref;

    // 12.288 MHz MCLK: period ~ 81.38 ns -> #40.69
    always #40.69 mclk_in = ~mclk_in;

    initial begin
        clk_ref = 0;
        mclk_in = 0;
        rst_n = 0;
        #60;
        rst_n = 1;

        // Wait for lock
        wait(locked == 1'b1);
        $display("LOCK_ASSERTED at %t", $time);

        // Run for several LRCK frames
        #200000;
        $display("PLL_SIM_DONE");
        $finish;
    end
endmodule
