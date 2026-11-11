// ============================================================================
// File: tb/v3/tb_ch05_local_mean.v
// Module: tb_ch05_local_mean
// Description:
//   Cycle-accurate, bit-exact testbench for rtl/v3/ch05_local_mean.v.
//   - Reads cycle-by-cycle stimulus from tb_ch05_mean_stim.txt.
//   - Reads expected values from tb_ch05_mean_expected.txt (Python twin).
//   - Sampling convention:
//     * Inputs driven at @(negedge clk)
//     * @(posedge clk); #1: Sample registered outputs (busy, mean_valid,
//       mean_out, rd_en, rd_sample_idx, diff_valid_out, diff_data_out).
//   - Fully compatible with `iverilog -g2012 -Wall`.
//   - Counts all errors without early exit; prints 'Total comparison errors: N'.
// ============================================================================

`timescale 1ns / 1ps

module tb_ch05_local_mean;

    parameter DATA_WIDTH  = 16;
    parameter ADDR_WIDTH  = 10;
    parameter SPAN_LEN    = 426;
    parameter SPAN_OFFSET = 106;

    reg clk = 0;
    always #10 clk = ~clk; // 50 MHz clock (20 ns period)

    reg                         rst_n;
    reg                         start;
    wire                        busy;
    wire                        mean_valid;
    wire signed [DATA_WIDTH-1:0] mean_out;

    wire                        rd_en;
    wire [ADDR_WIDTH-1:0]       rd_sample_idx;
    reg                         rd_valid;
    reg  signed [DATA_WIDTH-1:0] rd_data;

    reg                         sub_valid_in;
    reg  signed [DATA_WIDTH-1:0] sub_data_in;
    wire                        diff_valid_out;
    wire signed [DATA_WIDTH:0]  diff_data_out;

    // Instantiate DUT
    ch05_local_mean #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH),
        .SPAN_LEN(SPAN_LEN),
        .SPAN_OFFSET(SPAN_OFFSET)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .start(start),
        .busy(busy),
        .mean_valid(mean_valid),
        .mean_out(mean_out),
        .rd_en(rd_en),
        .rd_sample_idx(rd_sample_idx),
        .rd_valid(rd_valid),
        .rd_data(rd_data),
        .sub_valid_in(sub_valid_in),
        .sub_data_in(sub_data_in),
        .diff_valid_out(diff_valid_out),
        .diff_data_out(diff_data_out)
    );

    integer stim_fd;
    integer exp_fd;
    integer cycle_idx;
    integer errors;

    // Stimulus variables from file
    integer stim_rst_n;
    integer stim_start;
    integer stim_rd_vld;
    reg [DATA_WIDTH-1:0] stim_rd_dat;
    integer stim_sub_vld;
    reg [DATA_WIDTH-1:0] stim_sub_dat;

    // Expected variables from file
    integer exp_busy;
    integer exp_mean_vld;
    reg [DATA_WIDTH-1:0] exp_mean_out;
    integer exp_rd_en;
    reg [ADDR_WIDTH-1:0] exp_rd_idx;
    integer exp_diff_vld;
    reg [DATA_WIDTH:0]   exp_diff_dat;

    initial begin
        rst_n        = 0;
        start        = 0;
        rd_valid     = 0;
        rd_data      = {DATA_WIDTH{1'b0}};
        sub_valid_in = 0;
        sub_data_in  = {DATA_WIDTH{1'b0}};
        cycle_idx    = 0;
        errors       = 0;

        // Open stimulus file
        stim_fd = $fopen("verify_v3/tb_ch05_mean_stim.txt", "r");
        if (stim_fd == 0) stim_fd = $fopen("tb_ch05_mean_stim.txt", "r");
        if (stim_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch05_mean_stim.txt");
            $finish;
        end

        // Open expected file
        exp_fd = $fopen("verify_v3/tb_ch05_mean_expected.txt", "r");
        if (exp_fd == 0) exp_fd = $fopen("tb_ch05_mean_expected.txt", "r");
        if (exp_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch05_mean_expected.txt");
            $finish;
        end

        $display("=== STARTING CH05 LOCAL MEAN CYCLE-BY-CYCLE VERIFICATION ===");

        // Align to falling edge
        @(negedge clk);

        while ($fscanf(stim_fd, "%d %d %d %h %d %h\n",
                       stim_rst_n, stim_start, stim_rd_vld, stim_rd_dat,
                       stim_sub_vld, stim_sub_dat) == 6 &&
               $fscanf(exp_fd, "%d %d %h %d %h %d %h\n",
                       exp_busy, exp_mean_vld, exp_mean_out,
                       exp_rd_en, exp_rd_idx, exp_diff_vld, exp_diff_dat) == 7) begin

            // 1. Drive inputs at clock low phase
            rst_n        = (stim_rst_n != 0) ? 1'b1 : 1'b0;
            start        = (stim_start != 0) ? 1'b1 : 1'b0;
            rd_valid     = (stim_rd_vld != 0) ? 1'b1 : 1'b0;
            rd_data      = stim_rd_dat;
            sub_valid_in = (stim_sub_vld != 0) ? 1'b1 : 1'b0;
            sub_data_in  = stim_sub_dat;

            // 2. Wait for clock rising edge and sample registered outputs
            @(posedge clk);
            #1;

            // Check registered outputs
            if (busy !== ((exp_busy != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: busy mismatch: DUT=%b EXP=%b",
                         cycle_idx, busy, exp_busy != 0);
                errors = errors + 1;
            end

            if (mean_valid !== ((exp_mean_vld != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: mean_valid mismatch: DUT=%b EXP=%b",
                         cycle_idx, mean_valid, exp_mean_vld != 0);
                errors = errors + 1;
            end

            if (mean_valid && (mean_out !== exp_mean_out)) begin
                $display("[FAIL] Cycle %0d: mean_out mismatch: DUT=%h (%0d) EXP=%h (%0d)",
                         cycle_idx, mean_out, $signed(mean_out), exp_mean_out, $signed(exp_mean_out));
                errors = errors + 1;
            end

            if (rd_en !== ((exp_rd_en != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: rd_en mismatch: DUT=%b EXP=%b",
                         cycle_idx, rd_en, exp_rd_en != 0);
                errors = errors + 1;
            end

            if (rd_en && (rd_sample_idx !== exp_rd_idx)) begin
                $display("[FAIL] Cycle %0d: rd_sample_idx mismatch: DUT=%h EXP=%h",
                         cycle_idx, rd_sample_idx, exp_rd_idx);
                errors = errors + 1;
            end

            if (diff_valid_out !== ((exp_diff_vld != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: diff_valid_out mismatch: DUT=%b EXP=%b",
                         cycle_idx, diff_valid_out, exp_diff_vld != 0);
                errors = errors + 1;
            end

            if (diff_valid_out && (diff_data_out !== exp_diff_dat)) begin
                $display("[FAIL] Cycle %0d: diff_data_out mismatch: DUT=%h (%0d) EXP=%h (%0d)",
                         cycle_idx, diff_data_out, $signed(diff_data_out), exp_diff_dat, $signed(exp_diff_dat));
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
