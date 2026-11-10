// rtl/v2/q15_saturate.v
// Module lam tron va bao hoa tu so 32-bit (Q17.14 hoac tich) ve Q1.15 co dau (16-bit).
// Khop bit-exact va cycle-exact voi mo hinh Python twin bang phep cong lam tron nua LSB (+16384)
// va kep gia tri (clamp) vao khoang [-32768, +32767].
`timescale 1ns/1ps

module q15_saturate (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        valid_in,
    input  wire signed [31:0] data_in,   // Dinh dang Q17.14 hoac Q2.30 sau dich
    output reg         valid_out,
    output reg  signed [15:0] data_out    // Dinh dang Q1.15 [-32768, +32767]
);

    // Buoc 1: Lam tron nua LSB (round-half-up / nearest): cong them 2^14 = 16384 truoc khi dich phai 15 bit
    // Neu la Q2.30 can dich 15 bit truoc, o day coi data_in can lam tron tai bit 14 ve bit 15:
    wire signed [32:0] rounded = {data_in[31], data_in} + 33'sh0000_4000;
    wire signed [17:0] shifted = rounded[32:15]; // Trich 18 bit cao

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            data_out  <= 16'sh0000;
        end else if (valid_in) begin
            valid_out <= 1'b1;
            // Buoc 2: Bao hoa (saturation / clamping)
            if (shifted > 18'sh07FFF) begin
                data_out <= 16'sh7FFF; // +32767
            end else if (shifted < -18'sh08000) begin
                data_out <= -16'sh8000; // -32768
            end else begin
                data_out <= shifted[15:0];
            end
        end else begin
            valid_out <= 1'b0;
        end
    end

endmodule
