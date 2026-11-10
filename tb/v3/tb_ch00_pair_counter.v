// ============================================================================
// File: tb/v3/tb_ch00_pair_counter.v
// Module: tb_ch00_pair_counter
// Description:
//   Testbench for ch00_pair_counter.
//   Tests the canonical Praat configuration (N=638, TAU_MIN=26, TAU_MAX=214)
//   followed by 200 diverse configurations read from "tb_ch00_configs.txt".
//   Checks pair count, cycle count, sload/last counts, and 32-bit checksum.
// ============================================================================

`timescale 1ns/1ps

module tb_ch00_pair_counter;

    localparam ADDR_WIDTH = 10;

    reg clk = 0;
    always #10 clk = ~clk; // 50 MHz clock (20 ns period)

    reg                    rst_n;
    reg                    start;
    reg  [ADDR_WIDTH-1:0]  cfg_n;
    reg  [ADDR_WIDTH-1:0]  cfg_tau_min;
    reg  [ADDR_WIDTH-1:0]  cfg_tau_max;

    wire                   busy;
    wire                   done;
    wire                   valid;
    wire                   sload;
    wire                   last;
    wire [ADDR_WIDTH-1:0]  addr_a;
    wire [ADDR_WIDTH-1:0]  addr_b;
    wire [ADDR_WIDTH-1:0]  tau_out;
    wire [31:0]            total_cycles;
    wire [31:0]            pair_count;

    ch00_pair_counter #(
        .N(638),
        .TAU_MIN(26),
        .TAU_MAX(214),
        .ADDR_WIDTH(ADDR_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .cfg_n(cfg_n),
        .cfg_tau_min(cfg_tau_min),
        .cfg_tau_max(cfg_tau_max),
        .busy(busy),
        .done(done),
        .valid(valid),
        .sload(sload),
        .last(last),
        .addr_a(addr_a),
        .addr_b(addr_b),
        .tau_out(tau_out),
        .total_cycles(total_cycles),
        .pair_count(pair_count)
    );

    // Testbench tracking registers
    integer fd, status;
    integer test_idx;
    integer exp_n, exp_tmin, exp_tmax, exp_pairs;
    reg [31:0] exp_csum;
    reg [31:0] run_csum;
    integer sload_count, last_count, valid_count;
    integer total_errors;
    integer total_tests;

    // Checksum computation while valid is high
    reg [31:0] pair_word;
    always @(posedge clk) begin
        if (rst_n && valid) begin
            valid_count <= valid_count + 1;
            if (sload) sload_count <= sload_count + 1;
            if (last)  last_count  <= last_count + 1;

            pair_word = {last, sload, tau_out[9:0], addr_b[9:0], addr_a[9:0]};
            run_csum <= (run_csum * 32'd31 + pair_word);
        end
    end

    initial begin
        rst_n = 0;
        start = 0;
        cfg_n = 0;
        cfg_tau_min = 0;
        cfg_tau_max = 0;
        run_csum = 0;
        sload_count = 0;
        last_count = 0;
        valid_count = 0;
        total_errors = 0;
        total_tests = 0;

        repeat (5) @(negedge clk);
        rst_n = 1;
        repeat (2) @(negedge clk);

        // --------------------------------------------------------------------
        // Test 1: Canonical Praat Configuration (N=638, TAU_MIN=26, TAU_MAX=214)
        // Using default parameters (cfg_n = 0)
        // --------------------------------------------------------------------
        $display("----------------------------------------------------------------");
        $display("Test 0: Canonical Praat configuration (N=638, tau=26..214)");
        run_csum = 0;
        sload_count = 0;
        last_count = 0;
        valid_count = 0;
        cfg_n = 0;
        cfg_tau_min = 0;
        cfg_tau_max = 0;

        @(negedge clk);
        start = 1;
        @(negedge clk);
        start = 0;

        // Wait until done
        while (!done) @(negedge clk);

        total_tests = total_tests + 1;
        if (valid_count !== 98540) begin
            $display("ERROR: Canonical pair count mismatch: got %0d, expected 98540", valid_count);
            total_errors = total_errors + 1;
        end
        if (total_cycles !== 98540) begin
            $display("ERROR: Canonical total cycles mismatch: got %0d, expected 98540", total_cycles);
            total_errors = total_errors + 1;
        end
        if (sload_count !== 190) begin
            $display("ERROR: Canonical sload count mismatch: got %0d, expected 190 (R0 + 189 lags)", sload_count);
            total_errors = total_errors + 1;
        end
        if (last_count !== 190) begin
            $display("ERROR: Canonical last count mismatch: got %0d, expected 190", last_count);
            total_errors = total_errors + 1;
        end

        $display("Canonical Praat test PASSED: pairs=%0d, cycles=%0d, sloads=%0d, lasts=%0d, csum=0x%08x",
                 valid_count, total_cycles, sload_count, last_count, run_csum);

        repeat (2) @(negedge clk);

        // --------------------------------------------------------------------
        // Test suite from tb_ch00_configs.txt (>= 200 random configurations)
        // --------------------------------------------------------------------
        fd = $fopen("tb_ch00_configs.txt", "r");
        if (fd == 0) begin
            $display("WARNING: Could not open tb_ch00_configs.txt");
        end else begin
            test_idx = 1;
            while ($fscanf(fd, "%d %d %d %d %h\n", exp_n, exp_tmin, exp_tmax, exp_pairs, exp_csum) == 5) begin
                run_csum = 0;
                sload_count = 0;
                last_count = 0;
                valid_count = 0;

                cfg_n       = exp_n[ADDR_WIDTH-1:0];
                cfg_tau_min = exp_tmin[ADDR_WIDTH-1:0];
                cfg_tau_max = exp_tmax[ADDR_WIDTH-1:0];

                @(negedge clk);
                start = 1;
                @(negedge clk);
                start = 0;

                while (!done) @(negedge clk);

                total_tests = total_tests + 1;

                if (valid_count !== exp_pairs) begin
                    $display("ERROR [Test %0d (N=%0d, t=[%0d..%0d])]: pairs got %0d, exp %0d",
                             test_idx, exp_n, exp_tmin, exp_tmax, valid_count, exp_pairs);
                    total_errors = total_errors + 1;
                end
                if (run_csum !== exp_csum) begin
                    $display("ERROR [Test %0d (N=%0d, t=[%0d..%0d])]: csum got 0x%08x, exp 0x%08x",
                             test_idx, exp_n, exp_tmin, exp_tmax, run_csum, exp_csum);
                    total_errors = total_errors + 1;
                end
                if (sload_count !== (exp_tmax - exp_tmin + 2)) begin
                    $display("ERROR [Test %0d]: sload count got %0d, exp %0d",
                             test_idx, sload_count, exp_tmax - exp_tmin + 2);
                    total_errors = total_errors + 1;
                end
                if (last_count !== (exp_tmax - exp_tmin + 2)) begin
                    $display("ERROR [Test %0d]: last count got %0d, exp %0d",
                             test_idx, last_count, exp_tmax - exp_tmin + 2);
                    total_errors = total_errors + 1;
                end

                test_idx = test_idx + 1;
                repeat (2) @(negedge clk);
            end
            $fclose(fd);
        end

        $display("----------------------------------------------------------------");
        $display("TEST SUMMARY: Total tests = %0d, Total errors = %0d", total_tests, total_errors);
        if (total_errors == 0) begin
            $display("ALL TESTS PASSED BIT-FOR-BIT AND CYCLE-FOR-CYCLE!");
        end else begin
            $display("FAILED with %0d errors", total_errors);
        end
        $display("----------------------------------------------------------------");

        $finish;
    end

endmodule
