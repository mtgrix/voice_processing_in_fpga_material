// ============================================================================
// File: tb/v3/tb_ch04_ring_buffer.v
// Module: tb_ch04_ring_buffer
// Description:
//   Cycle-accurate, bit-exact testbench for rtl/v3/ch04_ring_buffer.v.
//   - Reads cycle-by-cycle stimulus from tb_ch04_ring_buffer_stim.txt.
//   - Reads expected values from tb_ch04_ring_buffer_expected.txt (Python twin).
//   - Sampling convention:
//     * Inputs driven at @(negedge clk)
//     * #1: Sample combinational outputs (sink_ready, frame_ready)
//     * @(posedge clk); #1: Sample registered outputs (frame_idx, rd_base,
//       sample_count_out, rd_valid, rd_data)
//   - Fully compatible with `iverilog -g2012 -Wall`.
// ============================================================================

`timescale 1ns / 1ps

module tb_ch04_ring_buffer;

    parameter DATA_WIDTH        = 16;
    parameter ADDR_WIDTH        = 10;
    parameter FRAME_LEN         = 638;
    parameter HOP_LEN           = 160;
    parameter REGISTERED_OUTPUT = 1;

    reg clk = 0;
    always #10 clk = ~clk; // 50 MHz clock (20 ns period)

    reg                         rst_n;
    reg                         clr;
    reg                         sink_valid;
    wire                        sink_ready;
    reg  signed [DATA_WIDTH-1:0] sink_data;

    wire                        frame_ready;
    reg                         frame_step;
    wire [15:0]                 frame_idx;
    wire [ADDR_WIDTH:0]         sample_count_out;
    wire [ADDR_WIDTH-1:0]       rd_base;

    reg                         rd_en;
    reg  [ADDR_WIDTH-1:0]       rd_sample_idx;
    wire signed [DATA_WIDTH-1:0] rd_data;
    wire                        rd_valid;

    // Instantiate DUT
    ch04_ring_buffer #(
        .DATA_WIDTH(DATA_WIDTH),
        .ADDR_WIDTH(ADDR_WIDTH),
        .FRAME_LEN(FRAME_LEN),
        .HOP_LEN(HOP_LEN),
        .REGISTERED_OUTPUT(REGISTERED_OUTPUT)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .clr(clr),
        .sink_valid(sink_valid),
        .sink_ready(sink_ready),
        .sink_data(sink_data),
        .frame_ready(frame_ready),
        .frame_step(frame_step),
        .frame_idx(frame_idx),
        .sample_count_out(sample_count_out),
        .rd_base(rd_base),
        .rd_en(rd_en),
        .rd_sample_idx(rd_sample_idx),
        .rd_data(rd_data),
        .rd_valid(rd_valid)
    );

    integer stim_fd;
    integer exp_fd;
    integer cycle_idx;
    integer errors;

    // Stimulus variables from file:
    // format: rst_n clr sink_valid sink_data frame_step rd_en rd_sample_idx
    integer stim_rst_n;
    integer stim_clr;
    integer stim_s_vld;
    reg [DATA_WIDTH-1:0] stim_s_dat;
    integer stim_f_step;
    integer stim_rd_en;
    reg [ADDR_WIDTH-1:0] stim_rd_idx;

    // Expected variables from file:
    // format: c_sink_ready c_frame_ready f_idx r_base s_count r_valid r_data
    integer exp_s_rdy;
    integer exp_f_rdy;
    reg [15:0] exp_f_idx;
    reg [ADDR_WIDTH-1:0] exp_r_base;
    reg [ADDR_WIDTH:0] exp_s_count;
    integer exp_r_vld;
    reg [DATA_WIDTH-1:0] exp_r_dat;

    initial begin
        rst_n         = 0;
        clr           = 0;
        sink_valid    = 0;
        sink_data     = {DATA_WIDTH{1'b0}};
        frame_step    = 0;
        rd_en         = 0;
        rd_sample_idx = {ADDR_WIDTH{1'b0}};
        cycle_idx     = 0;
        errors        = 0;

        // Open stimulus file
        stim_fd = $fopen("verify_v3/tb_ch04_ring_buffer_stim.txt", "r");
        if (stim_fd == 0) stim_fd = $fopen("tb_ch04_ring_buffer_stim.txt", "r");
        if (stim_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch04_ring_buffer_stim.txt");
            $finish;
        end

        // Open expected file
        exp_fd = $fopen("verify_v3/tb_ch04_ring_buffer_expected.txt", "r");
        if (exp_fd == 0) exp_fd = $fopen("tb_ch04_ring_buffer_expected.txt", "r");
        if (exp_fd == 0) begin
            $display("[FAIL] Cannot open tb_ch04_ring_buffer_expected.txt");
            $finish;
        end

        $display("=== STARTING CH04 RING BUFFER CYCLE-BY-CYCLE VERIFICATION ===");

        // Align to falling clock edge before cycle loop
        @(negedge clk);

        while ($fscanf(stim_fd, "%d %d %d %h %d %d %h\n",
                       stim_rst_n, stim_clr, stim_s_vld, stim_s_dat,
                       stim_f_step, stim_rd_en, stim_rd_idx) == 7 &&
               $fscanf(exp_fd, "%d %d %h %h %h %d %h\n",
                       exp_s_rdy, exp_f_rdy, exp_f_idx, exp_r_base,
                       exp_s_count, exp_r_vld, exp_r_dat) == 7) begin

            // 1. Drive inputs at clock low phase
            rst_n         = (stim_rst_n != 0) ? 1'b1 : 1'b0;
            clr           = (stim_clr != 0) ? 1'b1 : 1'b0;
            sink_valid    = (stim_s_vld != 0) ? 1'b1 : 1'b0;
            sink_data     = stim_s_dat;
            frame_step    = (stim_f_step != 0) ? 1'b1 : 1'b0;
            rd_en         = (stim_rd_en != 0) ? 1'b1 : 1'b0;
            rd_sample_idx = stim_rd_idx;

            // 2. Allow combinational outputs to settle
            #1;

            // 3. Sample and check combinational outputs BEFORE clock edge
            if (sink_ready !== ((exp_s_rdy != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: sink_ready mismatch: DUT=%b EXP=%b",
                         cycle_idx, sink_ready, exp_s_rdy != 0);
                errors = errors + 1;
            end
            if (frame_ready !== ((exp_f_rdy != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: frame_ready mismatch: DUT=%b EXP=%b",
                         cycle_idx, frame_ready, exp_f_rdy != 0);
                errors = errors + 1;
            end

            // 4. Clock edge posedge
            @(posedge clk);
            #1; // Let registers settle

            // 5. Sample and check registered outputs
            if (frame_idx !== exp_f_idx) begin
                $display("[FAIL] Cycle %0d: frame_idx mismatch: DUT=%h EXP=%h",
                         cycle_idx, frame_idx, exp_f_idx);
                errors = errors + 1;
            end
            if (rd_base !== exp_r_base) begin
                $display("[FAIL] Cycle %0d: rd_base mismatch: DUT=%h EXP=%h",
                         cycle_idx, rd_base, exp_r_base);
                errors = errors + 1;
            end
            if (sample_count_out !== exp_s_count) begin
                $display("[FAIL] Cycle %0d: sample_count mismatch: DUT=%h EXP=%h",
                         cycle_idx, sample_count_out, exp_s_count);
                errors = errors + 1;
            end
            if (rd_valid !== ((exp_r_vld != 0) ? 1'b1 : 1'b0)) begin
                $display("[FAIL] Cycle %0d: rd_valid mismatch: DUT=%b EXP=%b",
                         cycle_idx, rd_valid, exp_r_vld != 0);
                errors = errors + 1;
            end
            if (rd_valid && (rd_data !== exp_r_dat)) begin
                $display("[FAIL] Cycle %0d: rd_data mismatch: DUT=%h EXP=%h",
                         cycle_idx, rd_data, exp_r_dat);
                errors = errors + 1;
            end

            cycle_idx = cycle_idx + 1;

            // Align to negedge for next cycle
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
            $display("=== TEST FAILED WITH %0d ERRORS ===", errors);
        end
        $display("-------------------------------------------------------");

        $finish;
    end

endmodule
