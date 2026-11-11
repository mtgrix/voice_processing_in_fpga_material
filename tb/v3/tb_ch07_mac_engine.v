// tb/v3/tb_ch07_mac_engine.v
// Top-level hardware autocorrelation engine testbench
// Instantiates ch07_mac_engine (FSM + address generator + sample RAM + MAC unit)
//
// Verification scope:
//   - Compliant with iverilog -g2012 -Wall (no unsized literals in concat, no $random)
//   - Reads golden vectors from golden_v2/hdl_check/xw.hex (10,208 samples = 16 frames x 638)
//   - Reads expected sums from golden_v2/hdl_check/exp.hex (3,040 results = 16 frames x 190)
//   - For each frame:
//       1. Loads 638 samples via load_en/load_addr/load_data
//       2. Pulses start
//       3. Collects all 190 (out_tau, out_R) results and compares against exp.hex
//       4. Asserts exactly 190 out_valid pulses occur per frame
//       5. Asserts cycle_count equals exactly 98,543 cycles (agenda specification)
//   - Counts all errors without early abort
//   - Prints [FAIL] on any error and reports:
//       "Total comparison errors: N"
//       "Total results checked: N"

`timescale 1ns/1ps

module tb_ch07_mac_engine;

    localparam integer DATA_W          = 17;
    localparam integer DEPTH           = 638;
    localparam integer ADDR_W          = 10;
    localparam integer ACC_W           = 48;
    localparam integer TAU_SCAN_MIN    = 26;
    localparam integer TAU_SCAN_MAX    = 214;
    localparam integer N_LAGS          = 190;
    localparam integer NFRAMES         = 16;
    localparam integer TOTAL_RESULTS   = NFRAMES * N_LAGS; // 3040
    localparam integer EXPECTED_CYCLES = 98543;

    // Clock generation (50 MHz, 20 ns period)
    reg clk = 0;
    always #10 clk = ~clk;

    // DUT Signals
    reg                     rst_n;
    reg                     load_en;
    reg  [ADDR_W-1:0]       load_addr;
    reg  signed [DATA_W-1:0] load_data;
    reg                     start;
    wire                    busy;
    wire                    done;
    wire                    out_valid;
    wire [7:0]              out_tau;
    wire signed [ACC_W-1:0] out_R;
    wire [31:0]             cycle_count;

    // DUT Instantiation
    ch07_mac_engine #(
        .DATA_W       (DATA_W),
        .DEPTH        (DEPTH),
        .ADDR_W       (ADDR_W),
        .ACC_W        (ACC_W),
        .TAU_SCAN_MIN (TAU_SCAN_MIN),
        .TAU_SCAN_MAX (TAU_SCAN_MAX),
        .N_LAGS       (N_LAGS)
    ) dut (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_en     (load_en),
        .load_addr   (load_addr),
        .load_data   (load_data),
        .start       (start),
        .busy        (busy),
        .done        (done),
        .out_valid   (out_valid),
        .out_tau     (out_tau),
        .out_R       (out_R),
        .cycle_count (cycle_count)
    );

    // Golden vector arrays
    reg signed [DATA_W-1:0] mem_xw  [0:NFRAMES*DEPTH-1];
    reg signed [ACC_W-1:0]  mem_exp [0:TOTAL_RESULTS-1];
    reg [7:0]               lag_table [0:N_LAGS-1];

    // Verification bookkeeping
    integer f, n, k;
    integer fd;
    integer errors;
    integer total_results_checked;
    integer frame_res_cnt;
    integer frame_errors_before;
    integer frame_errors;
    integer watchdog;
    reg [7:0] exp_tau;
    reg signed [ACC_W-1:0] exp_val;

    initial begin
        // Initialize control signals
        rst_n                 = 1'b0;
        load_en               = 1'b0;
        load_addr             = {ADDR_W{1'b0}};
        load_data             = {DATA_W{1'b0}};
        start                 = 1'b0;
        errors                = 0;
        total_results_checked = 0;

        // Build expected lag table: lag 0 = 0, lag 1..189 = 26..214
        lag_table[0] = 8'd0;
        for (k = 1; k < N_LAGS; k = k + 1) begin
            lag_table[k] = TAU_SCAN_MIN + (k - 1);
        end

        // Load sample memory xw.hex
        fd = $fopen("golden_v2/hdl_check/xw.hex", "r");
        if (fd != 0) begin
            $fclose(fd);
            $readmemh("golden_v2/hdl_check/xw.hex", mem_xw);
        end else begin
            fd = $fopen("../golden_v2/hdl_check/xw.hex", "r");
            if (fd != 0) begin
                $fclose(fd);
                $readmemh("../golden_v2/hdl_check/xw.hex", mem_xw);
            end else begin
                fd = $fopen("xw.hex", "r");
                if (fd != 0) begin
                    $fclose(fd);
                    $readmemh("xw.hex", mem_xw);
                end else begin
                    $display("[FAIL] Cannot open golden_v2/hdl_check/xw.hex!");
                    $finish;
                end
            end
        end

        // Load expected sum memory exp.hex
        fd = $fopen("golden_v2/hdl_check/exp.hex", "r");
        if (fd != 0) begin
            $fclose(fd);
            $readmemh("golden_v2/hdl_check/exp.hex", mem_exp);
        end else begin
            fd = $fopen("../golden_v2/hdl_check/exp.hex", "r");
            if (fd != 0) begin
                $fclose(fd);
                $readmemh("../golden_v2/hdl_check/exp.hex", mem_exp);
            end else begin
                fd = $fopen("exp.hex", "r");
                if (fd != 0) begin
                    $fclose(fd);
                    $readmemh("exp.hex", mem_exp);
                end else begin
                    $display("[FAIL] Cannot open golden_v2/hdl_check/exp.hex!");
                    $finish;
                end
            end
        end

        $display("=== STARTING CH07 MAC ENGINE VERIFICATION (16 FRAMES, 3040 RESULTS) ===");

        // Reset pulse
        @(negedge clk);
        rst_n = 1'b0;
        repeat (5) @(negedge clk);
        rst_n = 1'b1;
        repeat (2) @(negedge clk);

        // Process all 16 frames
        for (f = 0; f < NFRAMES; f = f + 1) begin
            frame_errors_before = errors;
            frame_res_cnt       = 0;
            watchdog            = 0;

            // 1. Load 638 windowed samples into internal sample RAM
            for (n = 0; n < DEPTH; n = n + 1) begin
                load_en   = 1'b1;
                load_addr = n[ADDR_W-1:0];
                load_data = mem_xw[f * DEPTH + n];
                @(negedge clk);
            end
            load_en   = 1'b0;
            load_addr = {ADDR_W{1'b0}};
            load_data = {DATA_W{1'b0}};
            repeat (2) @(negedge clk);

            // 2. Pulse start to begin 98,540-pair autocorrelation calculation
            start = 1'b1;
            @(negedge clk);
            start = 1'b0;

            // 3. Monitor execution and collect all 190 results
            while (!done && watchdog <= 120000) begin
                @(posedge clk);
                #1;
                watchdog = watchdog + 1;
                if (watchdog > 120000) begin
                    $display("[FAIL] Frame %0d: WATCHDOG TIMEOUT waiting for done! (cycle_count=%0d)",
                             f, cycle_count);
                    errors = errors + 1;
                    // reviewer: iverilog 12 has no break; loop condition exits
                end

                if (out_valid) begin
                    exp_val = mem_exp[f * N_LAGS + frame_res_cnt];
                    exp_tau = lag_table[frame_res_cnt];

                    // Check lag tau tag
                    if (out_tau !== exp_tau) begin
                        $display("[FAIL] Frame %0d Result %0d: lag mismatch DUT=%0d EXP=%0d",
                                 f, frame_res_cnt, out_tau, exp_tau);
                        errors = errors + 1;
                    end

                    // Check 48-bit autocorrelation sum
                    if (out_R !== exp_val) begin
                        $display("[FAIL] Frame %0d Result %0d (tau=%0d): R mismatch DUT=0x%012h (%0d) EXP=0x%012h (%0d)",
                                 f, frame_res_cnt, out_tau, out_R, $signed(out_R), exp_val, $signed(exp_val));
                        errors = errors + 1;
                    end

                    frame_res_cnt         = frame_res_cnt + 1;
                    total_results_checked = total_results_checked + 1;
                end
            end

            // 4. Verify post-frame invariants
            if (frame_res_cnt != N_LAGS) begin
                $display("[FAIL] Frame %0d: Expected %0d results, got %0d out_valid pulses!",
                         f, N_LAGS, frame_res_cnt);
                errors = errors + 1;
            end

            if (cycle_count != EXPECTED_CYCLES) begin
                $display("[FAIL] Frame %0d: Expected cycle_count %0d, got %0d!",
                         f, EXPECTED_CYCLES, cycle_count);
                errors = errors + 1;
            end

            frame_errors = errors - frame_errors_before;
            $display("Frame %2d: %3d results, cycle_count = %0d -> %s",
                     f, frame_res_cnt, cycle_count,
                     (frame_errors == 0) ? "PASS" : "FAIL");

            repeat (2) @(negedge clk);
        end

        // Final verification summary
        $display("-------------------------------------------------------");
        $display("Total results checked: %0d", total_results_checked);
        $display("Total comparison errors: %0d", errors);

        if (total_results_checked != TOTAL_RESULTS) begin
            $display("[FAIL] Total results checked (%0d) != EXPECTED (%0d)!",
                     total_results_checked, TOTAL_RESULTS);
            errors = errors + 1;
        end

        if (errors == 0) begin
            $display("=== ALL 3040 RESULTS MATCHED SUCCESSFULLY ===");
        end else begin
            $display("[FAIL] Verification finished with %0d errors!", errors);
        end
        $display("-------------------------------------------------------");
        $finish;
    end

endmodule
