// mac_dsp_unit17: 17x17 signed MAC (xw is 17-bit after mean removal), 2 register stages.
// Maps to ONE Cyclone V variable-precision DSP in 18x18 mode (64-bit accumulator; we keep 48).
module mac_dsp_unit17 (
    input  wire               clk,
    input  wire               in_valid,
    input  wire               in_sload,   // first pair of a lag: load instead of add
    input  wire               in_last,    // last pair of a lag
    input  wire signed [16:0] a,          // xw[n]
    input  wire signed [16:0] b,          // xw[n+tau]
    output reg  signed [47:0] acc,
    output reg                out_valid
);
    reg signed [16:0] a_r, b_r;
    reg               v_r, sload_r, last_r;
    initial begin v_r = 1'b0; out_valid = 1'b0; acc = 48'sd0; end
    always @(posedge clk) begin
        a_r <= a;  b_r <= b;
        v_r <= in_valid;  sload_r <= in_sload;  last_r <= in_last;
    end
    wire signed [33:0] p = a_r * b_r;
    always @(posedge clk) begin
        if (v_r) acc <= sload_r ? {{14{p[33]}}, p} : acc + {{14{p[33]}}, p};
        out_valid <= v_r & last_r;
    end
endmodule
