// ============================================================================
// File: rtl/v3/ch09_lpm_div_wrapper.v
// Module: ch09_lpm_div_wrapper
// Description: Intel LPM_DIVIDE IP Core Wrapper (Route A)
//              Instantiates lpm_divide from 220model / altera_mf library.
//              Reference: Intel "Integer Arithmetic IP Cores User Guide" (UG-01069)
//                         Chapter 5: LPM_DIVIDE IP Core.
//              Parameters:
//                LPM_WIDTHN            = 44 (numerator width)
//                LPM_WIDTHD            = 34 (denominator width)
//                LPM_NREPRESENTATION   = "UNSIGNED"
//                LPM_DREPRESENTATION   = "UNSIGNED"
//                LPM_PIPELINE          = 44 (matching sequential divider latency)
//                LPM_REMAINDERPOSITIVE = "TRUE"
//                MAXIMIZE_SPEED        = 6
// ============================================================================

`timescale 1ns / 1ps

module ch09_lpm_div_wrapper (
    input  wire        clk,
    input  wire        clken,
    input  wire        aclr,
    input  wire [43:0] numer,
    input  wire [33:0] denom,
    output wire [43:0] quotient,
    output wire [33:0] remain
);

    // Instantiation of Intel LPM_DIVIDE megafunction
    lpm_divide #(
        .lpm_widthn(44),
        .lpm_widthd(34),
        .lpm_nrepresentation("UNSIGNED"),
        .lpm_drepresentation("UNSIGNED"),
        .lpm_pipeline(44),
        .lpm_type("LPM_DIVIDE"),
        .lpm_hint("MAXIMIZE_SPEED=6,LPM_REMAINDERPOSITIVE=TRUE")
    ) u_lpm_divide (
        .clock(clk),
        .clken(clken),
        .aclr(aclr),
        .numer(numer),
        .denom(denom),
        .quotient(quotient),
        .remain(remain)
    );

endmodule
