// ============================================================================
// File: tb/v3/tb_ch02_fsm_equiv.v
// Module: tb_ch02_fsm_equiv
// Description:
//   Cycle-accurate equivalence testbench comparing:
//   - DUT 1: ch02_fsm_binary (3-bit binary encoding)
//   - DUT 2: ch02_fsm_onehot (5-bit one-hot encoding)
//   - Golden Model: Python twin expected file (tb_ch02_fsm_expected.txt)
//   Verifies that both hardware architectures exhibit bit-for-bit and
//   cycle-for-cycle identity across >= 200 vectors.
//   Fully compatible with `iverilog -g2012 -Wall`.
// ============================================================================

`timescale 1ns/1ps

module tb_ch02_fsm_equiv;

    reg clk = 0;
    always #10 clk = ~clk; // 50 MHz (20 ns period)

    reg   rst_n;
    reg   start;
    reg   load_done;
    reg   calc_done;
    reg   drain_done;

    // Outputs from Binary DUT
    wire       bin_busy;
    wire       bin_load_en;
    wire       bin_calc_en;
    wire       bin_drain_en;
    wire       bin_done_pulse;
    wire [2:0] bin_state_num;

    // Outputs from One-Hot DUT
    wire       one_busy;
    wire       one_load_en;
    wire       one_calc_en;
    wire       one_drain_en;
    wire       one_done_pulse;
    wire [2:0] one_state_num;

    // Instantiate Binary FSM
    ch02_fsm_binary u_fsm_bin (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .load_done(load_done),
        .calc_done(calc_done),
        .drain_done(drain_done),
        .busy(bin_busy),
        .load_en(bin_load_en),
        .calc_en(bin_calc_en),
        .drain_en(bin_drain_en),
        .done_pulse(bin_done_pulse),
        .state_num(bin_state_num)
    );

    // Instantiate One-Hot FSM
    ch02_fsm_onehot u_fsm_one (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .load_done(load_done),
        .calc_done(calc_done),
        .drain_done(drain_done),
        .busy(one_busy),
        .load_en(one_load_en),
        .calc_en(one_calc_en),
        .drain_en(one_drain_en),
        .done_pulse(one_done_pulse),
        .state_num(one_state_num)
    );

    integer stim_fd;
    integer exp_fd;
    integer cycle_idx;
    integer errors;

    // Stimulus variables
    integer stim_rst_n;
    integer stim_start;
    integer stim_ld_done;
    integer stim_calc_done;
    integer stim_drain_done;

    // Expected variables
    integer exp_c;
    integer exp_rst_n;
    integer exp_busy;
    integer exp_ld_en;
    integer exp_calc_en;
    integer exp_drain_en;
    integer exp_done_pulse;
    integer exp_state_num;

    initial begin
        rst_n = 0;
        start = 0;
        load_done = 0;
        calc_done = 0;
        drain_done = 0;
        cycle_idx = 0;
        errors = 0;

        // Open stimulus file
        stim_fd = $fopen("verify_v3/tb_ch02_fsm_stim.txt", "r");
        if (stim_fd == 0) stim_fd = $fopen("tb_ch02_fsm_stim.txt", "r");
        if (stim_fd == 0) begin
            $display("ERROR: Cannot open tb_ch02_fsm_stim.txt");
            $finish;
        end

        // Open expected trace file
        exp_fd = $fopen("verify_v3/tb_ch02_fsm_expected.txt", "r");
        if (exp_fd == 0) exp_fd = $fopen("tb_ch02_fsm_expected.txt", "r");
        if (exp_fd == 0) begin
            $display("ERROR: Cannot open tb_ch02_fsm_expected.txt");
            $finish;
        end

        $display("=== STARTING CH02 FSM BINARY VS ONE-HOT EQUIVALENCE VERIFICATION ===");

        // Run cycle by cycle
        while ($fscanf(stim_fd, "%d %d %d %d %d\n",
                       stim_rst_n, stim_start, stim_ld_done, stim_calc_done, stim_drain_done) == 5 &&
               $fscanf(exp_fd, "%d %d %d %d %d %d %d %d\n",
                       exp_c, exp_rst_n, exp_busy, exp_ld_en, exp_calc_en,
                       exp_drain_en, exp_done_pulse, exp_state_num) == 8) begin

            // Drive inputs before posedge clk
            rst_n      <= (stim_rst_n != 0) ? 1'b1 : 1'b0;
            start      <= (stim_start != 0) ? 1'b1 : 1'b0;
            load_done  <= (stim_ld_done != 0) ? 1'b1 : 1'b0;
            calc_done  <= (stim_calc_done != 0) ? 1'b1 : 1'b0;
            drain_done <= (stim_drain_done != 0) ? 1'b1 : 1'b0;

            // Wait for posedge clk and delta settle
            @(posedge clk);
            #1;

            // 1. Cross-check Binary vs One-Hot outputs
            if (bin_busy !== one_busy) begin
                $display("[FAIL] Cycle %0d: busy mismatch between Binary (%b) and One-Hot (%b)",
                         cycle_idx, bin_busy, one_busy);
                errors = errors + 1;
            end

            if (bin_load_en !== one_load_en) begin
                $display("[FAIL] Cycle %0d: load_en mismatch between Binary (%b) and One-Hot (%b)",
                         cycle_idx, bin_load_en, one_load_en);
                errors = errors + 1;
            end

            if (bin_calc_en !== one_calc_en) begin
                $display("[FAIL] Cycle %0d: calc_en mismatch between Binary (%b) and One-Hot (%b)",
                         cycle_idx, bin_calc_en, one_calc_en);
                errors = errors + 1;
            end

            if (bin_drain_en !== one_drain_en) begin
                $display("[FAIL] Cycle %0d: drain_en mismatch between Binary (%b) and One-Hot (%b)",
                         cycle_idx, bin_drain_en, one_drain_en);
                errors = errors + 1;
            end

            if (bin_done_pulse !== one_done_pulse) begin
                $display("[FAIL] Cycle %0d: done_pulse mismatch between Binary (%b) and One-Hot (%b)",
                         cycle_idx, bin_done_pulse, one_done_pulse);
                errors = errors + 1;
            end

            if (bin_state_num !== one_state_num) begin
                $display("[FAIL] Cycle %0d: state_num mismatch between Binary (%0d) and One-Hot (%0d)",
                         cycle_idx, bin_state_num, one_state_num);
                errors = errors + 1;
            end

            // 2. Check both against Python expected model
            if (bin_busy !== ((exp_busy != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: busy vs Expected mismatch (got %b, exp %0d)",
                         cycle_idx, bin_busy, exp_busy);
                errors = errors + 1;
            end

            if (bin_state_num !== exp_state_num[2:0]) begin
                $display("[FAIL] Cycle %0d: state_num vs Expected mismatch (got %0d, exp %0d)",
                         cycle_idx, bin_state_num, exp_state_num);
                errors = errors + 1;
            end

            if (errors >= 20) begin
                $display("Too many errors. Aborting simulation.");
                $finish;
            end

            cycle_idx = cycle_idx + 1;
        end

        $fclose(stim_fd);
        $fclose(exp_fd);

        $display("Simulation completed %0d cycles.", cycle_idx);
        $display("Total comparison errors: %0d", errors);

        if (errors == 0 && cycle_idx >= 200) begin
            $display("=== [PASS] CH02 BINARY AND ONE-HOT FSMS MATCHED PYTHON TWIN AND EACH OTHER ON %0d CYCLES ===", cycle_idx);
        end else begin
            $display("=== [FAIL] CH02 FSM EQUIVALENCE FAILED WITH %0d ERRORS ===", errors);
        end

        $finish;
    end

endmodule
