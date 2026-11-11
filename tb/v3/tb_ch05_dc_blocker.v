// ============================================================================
// File: tb/v3/tb_ch05_dc_blocker.v
// Module: tb_ch05_dc_blocker
// Description:
//   Cycle-accurate, bit-exact testbench for rtl/v3/ch05_dc_blocker.v.
//   - Reads cycle-by-cycle stimulus from tb_ch05_dc_blocker_stim.txt.
//   - Reads expected values from tb_ch05_dc_blocker_expected.txt (Python twin).
//   - Sampling convention:
//     * Inputs driven at @(negedge clk)
//     * #1: Sample combinational output (sink_ready)
//     * @(posedge clk); #1: Sample registered outputs (source_valid, source_data)
//   - Fully compatible with `iverilog -g2012 -Wall`.
//   - Counts all errors without early exit; prints 'Total comparison errors: N'.
// ============================================================================

`timescale 1ns / 1ps

module tb_ch05_dc_blocker;

    parameter DATA_WIDTH = 16;
    parameter SHIFT_R    = 8;

    reg clk = 0;
    always #10 clk = ~clk; // 50 MHz clock (20 ns period)

    reg                         rst_n;
    reg                         bypass;
    reg                         sink_valid;
    wire                        sink_ready;
    reg  signed [DATA_WIDTH-1:0] sink_data;

    wire                        source_valid;
    reg                         source_ready;
    wire signed [DATA_WIDTH-1:0] source_data;

    // Instantiate DUT
    ch05_dc_blocker #(
        .DATA_WIDTH(DATA_WIDTH),
        .SHIFT_R(SHIFT_R)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .bypass(bypass),
        .sink_valid(sink_valid),
        .sink_ready(sink_ready),
        .sink_data(sink_data),
        .source_valid(source_valid),
        .source_ready(source_ready),
        .source_data(source_data)
    );

    integer stim_fd;
    integer exp_fd;
    integer cycle_idx;
    integer errors;

    // Stimulus variables from file:
    // format: rst_n bypass sink_valid sink_data source_ready
    integer stim_rst_n;
    integer stim_bypass;
    integer stim_s_vld;
    reg [DATA_WIDTH-1:0] stim_s_dat;
    integer stim_src_rdy;

    // Expected variables from file:
    // format: exp_sink_ready exp_source_valid exp_source_data
    integer exp_sink_rdy;
    integer exp_src_vld;
    reg [DATA_WIDTH-1:0] exp_src_dat;

    initial begin
        rst_n        = 0;
        bypass       = 0;
        sink_valid   = 0;
        sink_data    = {DATA_WIDTH{1'b0}};
        source_ready = 0;
        cycle_idx    = 0;
        errors       = 0;

        // Open stimulus file
        stim_fd = $fopen("verify_v3/tb_ch05_dc_blocker_stim.txt", "r");
        if (stim_fd == 0) stim_fd = $fopen("tb_ch05_dc_blocker_stim.txt", "r");
        if (stim_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch05_dc_blocker_stim.txt");
            $finish;
        end

        // Open expected file
        exp_fd = $fopen("verify_v3/tb_ch05_dc_blocker_expected.txt", "r");
        if (exp_fd == 0) exp_fd = $fopen("tb_ch05_dc_blocker_expected.txt", "r");
        if (exp_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch05_dc_blocker_expected.txt");
            $finish;
        end

        $display("=== STARTING CH05 DC-BLOCKER CYCLE-BY-CYCLE VERIFICATION ===");

        // Align to falling edge
        @(negedge clk);

        while ($fscanf(stim_fd, "%d %d %d %h %d\n",
                       stim_rst_n, stim_bypass, stim_s_vld, stim_s_dat, stim_src_rdy) == 5 &&
               $fscanf(exp_fd, "%d %d %h\n",
                       exp_sink_rdy, exp_src_vld, exp_src_dat) == 3) begin

            // 1. Drive inputs at clock low phase
            rst_n        = (stim_rst_n != 0) ? 1'b1 : 1'b0;
            bypass       = (stim_bypass != 0) ? 1'b1 : 1'b0;
            sink_valid   = (stim_s_vld != 0) ? 1'b1 : 1'b0;
            sink_data    = stim_s_dat;
            source_ready = (stim_src_rdy != 0) ? 1'b1 : 1'b0;

            // 2. Allow combinational logic to settle
            #1;

            // 3. Sample and check combinational output (sink_ready)
            if (sink_ready !== ((exp_sink_rdy != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: sink_ready mismatch: DUT=%b EXP=%b",
                         cycle_idx, sink_ready, exp_sink_rdy != 0);
                errors = errors + 1;
            end

            // 4. Wait for clock rising edge and sample registered outputs
            @(posedge clk);
            #1;

            if (source_valid !== ((exp_src_vld != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: source_valid mismatch: DUT=%b EXP=%b",
                         cycle_idx, source_valid, exp_src_vld != 0);
                errors = errors + 1;
            end

            if (source_valid && (source_data !== exp_src_dat)) begin
                $display("[FAIL] Cycle %0d: source_data mismatch: DUT=%h (%0d) EXP=%h (%0d)",
                         cycle_idx, source_data, $signed(source_data), exp_src_dat, $signed(exp_src_dat));
                errors = errors + 1;
            end

            cycle_idx = cycle_idx + 1;
            @(negedge clk);
        end

        $fclose(stim_fd);
        $fclose(exp_fd);

        $display("-------------------------------------------------------");
        $display("Simulation finished. Total cycles tested: %0d", cycle_idx);
        $display("Total comparison errors: %0d", errors);
        if (errors == 0) begin
            $display("=== ALL %0d VECTORS MATCHED SUCCESSFULLY ===", cycle_idx);
        end else begin
            $display("[FAIL] Verification finished with %0d errors!", errors);
        end
        $display("-------------------------------------------------------");
        $finish;
    end

endmodule
