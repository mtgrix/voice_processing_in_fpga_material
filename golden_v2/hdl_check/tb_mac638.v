`timescale 1ns/1ps
module tb_mac638;
    localparam L = 638, NF = 16, NLAG = 190;
    reg clk = 0; always #10 clk = ~clk;          // 50 MHz
    reg signed [16:0] mem [0:NF*L-1];
    reg [47:0] expv [0:NF*NLAG-1];
    integer lagtab [0:NLAG-1];
    // address generator (FSM stand-in): back-to-back pairs, no gaps between lags
    integer f, li, n, tau, k, errors, nres, t_first, t_last, cyc;
    reg [15:0] addr_a, addr_b; reg g_valid, g_sload, g_last;
    reg signed [16:0] q_a, q_b; reg d_valid, d_sload, d_last;     // M10K: data 1 cycle after address
    wire signed [47:0] acc; wire out_valid;
    mac_dsp_unit17 dut(.clk(clk), .in_valid(d_valid), .in_sload(d_sload), .in_last(d_last),
                     .a(q_a), .b(q_b), .acc(acc), .out_valid(out_valid));
    always @(posedge clk) begin
        q_a <= mem[addr_a]; q_b <= mem[addr_b];
        d_valid <= g_valid; d_sload <= g_sload; d_last <= g_last;
    end
    always @(posedge clk) cyc <= cyc + 1;
    always @(posedge clk) if (out_valid) begin
        if (acc !== expv[nres]) begin errors = errors + 1;
            if (errors < 5) $display("MISMATCH %0d got %0d exp %0d", nres, acc, $signed(expv[nres])); end
        nres = nres + 1; t_last = cyc;
    end
    initial begin
        $readmemh("xw.hex", mem); $readmemh("exp.hex", expv);
        lagtab[0] = 0; for (k = 1; k < NLAG; k = k + 1) lagtab[k] = 25 + k;   // 0, 26..214
        errors = 0; nres = 0; cyc = 0; g_valid = 0; g_sload = 0; g_last = 0; addr_a = 0; addr_b = 0;
        d_valid = 0;
        @(negedge clk);
        for (f = 0; f < NF; f = f + 1) begin
            t_first = cyc;
            for (li = 0; li < NLAG; li = li + 1) begin
                tau = lagtab[li];
                for (n = 0; n < L - tau; n = n + 1) begin
                    addr_a = f*L + n; addr_b = f*L + n + tau;
                    g_valid = 1; g_sload = (n == 0); g_last = (n == L - tau - 1);
                    @(negedge clk);
                end
            end
            g_valid = 0; g_sload = 0; g_last = 0;
            repeat (4) @(negedge clk);
            $display("frame %0d: issue cycles = %0d, first-address -> last result = %0d cycles", f,
                     98540, t_last - t_first + 1);
            repeat (2) @(negedge clk);
        end
        $display("results checked = %0d, errors = %0d", nres, errors);
        $finish;
    end
endmodule
