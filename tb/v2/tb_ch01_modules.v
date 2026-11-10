// tb/v2/tb_ch01_modules.v
// Comprehensive testbench for Chapter 1 RTL modules:
// Tests Step 1 (Nyquist filter), Step 3 (mean subtraction), Step 4 (window multiply),
// Step 5 (sequential MAC), Step 6 (norm multiply), Step 7 (parabolic curve),
// Step 10 (integer silence/voicing gate), and Step 11 (canonical median3).
`timescale 1ns/1ps

module tb_ch01_modules;

    reg clk;
    reg rst_n;

    // --- Signals for Step 1 ---
    reg        s1_valid_in;
    reg signed [15:0] s1_data_in;
    wire       s1_valid_out;
    wire signed [15:0] s1_data_out;
    ch01_step01_filter u_step01 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s1_valid_in), .data_in(s1_data_in),
        .valid_out(s1_valid_out), .data_out(s1_data_out)
    );

    // --- Signals for Step 3 ---
    reg        s3_valid_in;
    reg signed [15:0] s3_sample_in;
    reg signed [15:0] s3_mean_val;
    wire       s3_valid_out;
    wire signed [15:0] s3_sample_zm;
    ch01_step03_mean_sub u_step03 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s3_valid_in), .sample_in(s3_sample_in), .mean_val(s3_mean_val),
        .valid_out(s3_valid_out), .sample_zm(s3_sample_zm)
    );

    // --- Signals for Step 4 ---
    reg        s4_valid_in;
    reg signed [15:0] s4_x_in, s4_w_in;
    wire       s4_valid_out;
    wire signed [15:0] s4_x_win;
    ch01_step04_window_mul u_step04 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s4_valid_in), .x_in(s4_x_in), .w_in(s4_w_in),
        .valid_out(s4_valid_out), .x_win(s4_x_win)
    );

    // --- Signals for Step 5 ---
    reg        s5_start_tau;
    reg [9:0]  s5_n_pairs;
    reg signed [15:0] s5_sample_a, s5_sample_b;
    wire [9:0] s5_rd_addr_a, s5_rd_addr_b;
    wire       s5_done_tau;
    wire signed [47:0] s5_r_tau_out;
    ch01_step05_mac_acf u_step05 (
        .clk(clk), .rst_n(rst_n),
        .start_tau(s5_start_tau), .n_pairs(s5_n_pairs),
        .sample_a(s5_sample_a), .sample_b(s5_sample_b),
        .rd_addr_a(s5_rd_addr_a), .rd_addr_b(s5_rd_addr_b),
        .done_tau(s5_done_tau), .r_tau_out(s5_r_tau_out)
    );

    // --- Signals for Step 6 ---
    reg        s6_valid_in;
    reg signed [31:0] s6_r_tau_in;
    reg signed [15:0] s6_c_tau_q13;
    wire       s6_valid_out;
    wire signed [47:0] s6_score_out;
    ch01_step06_norm_mul u_step06 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s6_valid_in), .r_tau_in(s6_r_tau_in), .c_tau_q13(s6_c_tau_q13),
        .valid_out(s6_valid_out), .score_out(s6_score_out)
    );

    // --- Signals for Step 7 ---
    reg        s7_valid_in;
    reg signed [15:0] s7_r_minus, s7_r_peak, s7_r_plus;
    wire       s7_valid_out;
    wire signed [16:0] s7_num_diff;
    wire [16:0] s7_den_curv;
    ch01_step07_parabolic u_step07 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s7_valid_in), .r_minus(s7_r_minus), .r_peak(s7_r_peak), .r_plus(s7_r_plus),
        .valid_out(s7_valid_out), .num_diff(s7_num_diff), .den_curv(s7_den_curv)
    );

    // --- Signals for Step 10 ---
    reg        s10_eval_valid;
    reg [31:0] s10_r0_energy, s10_ref_energy;
    reg [47:0] s10_best_score;
    reg [15:0] s10_f0_candidate;
    wire       s10_done_valid;
    wire       s10_is_voiced;
    wire [15:0] s10_f0_gated;
    ch01_step10_voicing_gate u_step10 (
        .clk(clk), .rst_n(rst_n),
        .eval_valid(s10_eval_valid), .r0_energy(s10_r0_energy), .ref_energy(s10_ref_energy),
        .best_score(s10_best_score), .f0_candidate(s10_f0_candidate),
        .done_valid(s10_done_valid), .is_voiced(s10_is_voiced), .f0_gated(s10_f0_gated)
    );

    // --- Signals for Step 11 ---
    reg        s11_valid_in;
    reg [15:0] s11_f_in;
    wire       s11_valid_out;
    wire [15:0] s11_f_out;
    ch01_step11_median3 u_step11 (
        .clk(clk), .rst_n(rst_n),
        .valid_in(s11_valid_in), .f_in(s11_f_in),
        .valid_out(s11_valid_out), .f_out(s11_f_out)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 0;
        rst_n = 0;
        s1_valid_in = 0; s1_data_in = 0;
        s3_valid_in = 0; s3_sample_in = 0; s3_mean_val = 0;
        s4_valid_in = 0; s4_x_in = 0; s4_w_in = 0;
        s5_start_tau = 0; s5_n_pairs = 0; s5_sample_a = 0; s5_sample_b = 0;
        s6_valid_in = 0; s6_r_tau_in = 0; s6_c_tau_q13 = 0;
        s7_valid_in = 0; s7_r_minus = 0; s7_r_peak = 0; s7_r_plus = 0;
        s10_eval_valid = 0; s10_r0_energy = 0; s10_ref_energy = 0; s10_best_score = 0; s10_f0_candidate = 0;
        s11_valid_in = 0; s11_f_in = 0;

        #20;
        rst_n = 1;
        #20;

        // --- Test Step 1: Nyquist tone [1000, -1000, 1000, -1000] -> filtered to 0 ---
        @(posedge clk); #1; s1_valid_in = 1; s1_data_in = 16'sd1000;
        @(posedge clk); #1; s1_valid_in = 1; s1_data_in = -16'sd1000;
        @(posedge clk); #1; s1_valid_in = 1; s1_data_in = 16'sd1000;
        @(posedge clk); #1; s1_valid_in = 1; s1_data_in = -16'sd1000;
        @(posedge clk); #1; s1_valid_in = 0;

        // --- Test Step 3: Local mean sub: x=[3, 5, 3, 5], mean=4 -> [-1, 1, -1, 1] ---
        #20;
        @(posedge clk); #1; s3_valid_in = 1; s3_mean_val = 16'sd4; s3_sample_in = 16'sd3;
        @(posedge clk); #1; s3_valid_in = 1; s3_mean_val = 16'sd4; s3_sample_in = 16'sd5;
        @(posedge clk); #1; s3_valid_in = 1; s3_mean_val = 16'sd4; s3_sample_in = 16'sd3;
        @(posedge clk); #1; s3_valid_in = 1; s3_mean_val = 16'sd4; s3_sample_in = 16'sd5;
        @(posedge clk); #1; s3_valid_in = 0;

        // --- Test Step 4: Window mul: x=16384 (0.5), w=16384 (0.5) -> prod 0.25 -> 8192 ---
        #20;
        @(posedge clk); #1; s4_valid_in = 1; s4_x_in = 16'sd16384; s4_w_in = 16'sd16384;
        @(posedge clk); #1; s4_valid_in = 0;

        // --- Test Step 5: MAC ACF on 4 pairs: [1*1 + (-1)*(-1) + 1*1 + (-1)*(-1)] = 4 ---
        #30;
        @(posedge clk); #1; s5_start_tau = 1; s5_n_pairs = 10'd4;
        s5_sample_a = 16'sd1; s5_sample_b = 16'sd1;
        @(posedge clk); #1; s5_start_tau = 0;
        s5_sample_a = -16'sd1; s5_sample_b = -16'sd1;
        @(posedge clk); #1;
        s5_sample_a = 16'sd1; s5_sample_b = 16'sd1;
        @(posedge clk); #1;
        s5_sample_a = -16'sd1; s5_sample_b = -16'sd1;
        @(posedge clk); #1;

        // --- Test Step 6: Norm mul: R_tau = 1000, C_tau = 8192 (1.0) -> score = 1000 ---
        #50;
        @(posedge clk); #1; s6_valid_in = 1; s6_r_tau_in = 32'sd1000; s6_c_tau_q13 = 16'sd8192;
        @(posedge clk); #1; s6_valid_in = 0;

        // --- Test Step 7: Parabolic: r_-=4000, r*=5000, r_+=4600 ---
        // num = 4000 - 4600 = -600.
        // curv = 4000 - 2*5000 + 4600 = -1400. den = -2 * curv = 2800.
        #30;
        @(posedge clk); #1; s7_valid_in = 1; s7_r_minus = 16'sd4000; s7_r_peak = 16'sd5000; s7_r_plus = 16'sd4600;
        @(posedge clk); #1; s7_valid_in = 0;

        // --- Test Step 10: Silence & Voicing gate ---
        // Case 1: Silence: R0=500_000, Eref=600_000_000 -> is_voiced = 0
        #30;
        @(posedge clk); #1;
        s10_eval_valid = 1;
        s10_r0_energy = 32'd500_000;
        s10_ref_energy = 32'd600_000_000;
        s10_best_score = 48'd410_000; // 0.82 * R0
        s10_f0_candidate = 16'd3200;  // 200 Hz in Q12.4
        @(posedge clk); #1;
        // Case 2: Voiced: R0=1_000_000, Eref=1_200_000, score=780_000 (0.78*R0 >= 0.45*R0) -> is_voiced = 1, f0=3200
        s10_eval_valid = 1;
        s10_r0_energy = 32'd1_000_000;
        s10_ref_energy = 32'd1_200_000;
        s10_best_score = 48'd780_000;
        s10_f0_candidate = 16'd3200;
        @(posedge clk); #1;
        // Case 3: Unvoiced: R0=1_000_000, Eref=1_200_000, score=300_000 (0.30*R0 < 0.45*R0) -> is_voiced = 0, f0=0
        s10_eval_valid = 1;
        s10_r0_energy = 32'd1_000_000;
        s10_ref_energy = 32'd1_200_000;
        s10_best_score = 48'd300_000;
        s10_f0_candidate = 16'd3200;
        @(posedge clk); #1; s10_eval_valid = 0;

        // --- Test Step 11: Median-3 filter on sequence [148, 150, 300, 152, 151] ---
        #30;
        @(posedge clk); #1; s11_valid_in = 1; s11_f_in = 16'd148;
        @(posedge clk); #1; s11_valid_in = 1; s11_f_in = 16'd150;
        @(posedge clk); #1; s11_valid_in = 1; s11_f_in = 16'd300;
        @(posedge clk); #1; s11_valid_in = 1; s11_f_in = 16'd152;
        @(posedge clk); #1; s11_valid_in = 1; s11_f_in = 16'd151;
        @(posedge clk); #1; s11_valid_in = 0;

        #200;
        $finish;
    end

    // Displays
    always @(posedge clk) begin
        if (s1_valid_out)  $display("STEP01: %d", s1_data_out);
        if (s3_valid_out)  $display("STEP03: %d", s3_sample_zm);
        if (s4_valid_out)  $display("STEP04: %d", s4_x_win);
        if (s5_done_tau)   $display("STEP05: %d", s5_r_tau_out);
        if (s6_valid_out)  $display("STEP06: %d", s6_score_out);
        if (s7_valid_out)  $display("STEP07: num=%d den=%d", s7_num_diff, s7_den_curv);
        if (s10_done_valid) $display("STEP10: voiced=%b f0=%d", s10_is_voiced, s10_f0_gated);
        if (s11_valid_out) $display("STEP11: %d", s11_f_out);
    end

endmodule
