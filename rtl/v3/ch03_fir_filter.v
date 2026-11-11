// ============================================================================
// File: rtl/v3/ch03_fir_filter.v
// Module: ch03_fir_filter
// Description:
//   31-tap folded symmetric FIR Nyquist-edge smoothing filter with Avalon-ST
//   streaming interface and dynamic bypass control.
//
// Theoretical specifications:
//   - Filter order: N = 31 taps, Type I linear phase (symmetrical).
//   - Coefficients: Q1.15 signed fixed-point (16-bit).
//   - Group delay: (N - 1) / 2 = 15 samples.
//   - Architecture: Folded symmetric structure using 1 DSP multiplier and a 17-bit
//     pre-adder running across 16 clock cycles per input sample.
//   - Accumulator: 40-bit signed to prevent any intermediate overflow.
//   - Output rounding: Symmetric round-to-nearest half-up (+16384) with saturation.
//   - Avalon-ST interface: readyLatency = 0, full backpressure support.
//   - Dynamic bypass: when bypass = 1, streams data with 1-cycle latency.
// ============================================================================

`timescale 1ns/1ps

module ch03_fir_filter #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16,
    parameter ACC_WIDTH   = 40
) (
    input  wire                         clk,
    input  wire                         rst_n,
    input  wire                         bypass,

    // Avalon-ST Sink (Input)
    input  wire                         sink_valid,
    output wire                         sink_ready,
    input  wire signed [DATA_WIDTH-1:0] sink_data,

    // Avalon-ST Source (Output)
    output wire                         source_valid,
    input  wire                         source_ready,
    output wire signed [DATA_WIDTH-1:0] source_data
);

    // State definitions
    localparam [1:0]
        S_IDLE     = 2'd0,
        S_CALC     = 2'd1,
        S_WAIT_OUT = 2'd2;

    reg [1:0] state;
    reg [3:0] step;

    // Shift register: 31 taps of 16-bit audio samples
    reg signed [DATA_WIDTH-1:0] shift_reg [0:30];

    // Accumulator register
    reg signed [ACC_WIDTH-1:0] acc;

    // Output registers
    reg signed [DATA_WIDTH-1:0] out_data_reg;
    reg                         out_valid_reg;

    // Handshake conditions
    wire s_handshake = sink_valid && sink_ready;
    wire m_handshake = out_valid_reg && source_ready;

    // Ready signal generation (readyLatency = 0)
    assign sink_ready = bypass ? (!out_valid_reg || source_ready) :
                                 ((state == S_IDLE) && (!out_valid_reg || source_ready));

    assign source_valid = out_valid_reg;
    assign source_data  = out_data_reg;

    // Coefficient ROM: 16 unique symmetrical coefficients (Q1.15)
    // h[0..14] are pairs with h[30..16], h[15] is the center tap.
    reg signed [COEFF_WIDTH-1:0] coeff_rom [0:15];
    initial begin
        coeff_rom[ 0] = 16'sh01f8; //   504
        coeff_rom[ 1] = 16'shfde6; //  -538
        coeff_rom[ 2] = 16'sh023b; //   571
        coeff_rom[ 3] = 16'shfda4; //  -604
        coeff_rom[ 4] = 16'sh027b; //   635
        coeff_rom[ 5] = 16'shfd68; //  -664
        coeff_rom[ 6] = 16'sh02b4; //   692
        coeff_rom[ 7] = 16'shfd33; //  -717
        coeff_rom[ 8] = 16'sh02e4; //   740
        coeff_rom[ 9] = 16'shfd08; //  -760
        coeff_rom[10] = 16'sh030a; //   778
        coeff_rom[11] = 16'shfce7; //  -793
        coeff_rom[12] = 16'sh0324; //   804
        coeff_rom[13] = 16'shfcd4; //  -812
        coeff_rom[14] = 16'sh0332; //   818
        coeff_rom[15] = 16'sh7ccd; // 31949 (center tap)
    end

    wire signed [COEFF_WIDTH-1:0] current_coeff = coeff_rom[step];

    // Pre-adder: sum x[k] + x[30-k] (17-bit signed)
    wire signed [DATA_WIDTH-1:0] tap_a = shift_reg[step];
    wire signed [DATA_WIDTH-1:0] tap_b = (step == 4'd15) ? 16'sh0000 : shift_reg[5'd30 - {1'b0, step}];
    wire signed [DATA_WIDTH:0]   pre_add = $signed(tap_a) + $signed(tap_b); // 17 bits

    // Multiplier: 17-bit pre-adder * 16-bit coefficient = 33-bit signed product
    wire signed [32:0] prod = pre_add * current_coeff;
    wire signed [ACC_WIDTH-1:0] prod_ext = {{7{prod[32]}}, prod};

    // Combinational accumulator for step 15
    wire signed [ACC_WIDTH-1:0] acc_final = (step == 4'd0) ? prod_ext : (acc + prod_ext);

    // Rounding and Saturation logic (+16384 for round-to-nearest, then >>> 15)
    wire signed [ACC_WIDTH-1:0] rounded = (acc_final + 40'sd16384) >>> 15;
    wire signed [DATA_WIDTH-1:0] sat_out = (rounded > 40'sd32767)  ? 16'sh7fff :
                                           (rounded < -40'sd32768) ? 16'sh8000 :
                                           rounded[DATA_WIDTH-1:0];

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state         <= S_IDLE;
            step          <= 4'd0;
            acc           <= {ACC_WIDTH{1'b0}};
            out_data_reg  <= {DATA_WIDTH{1'b0}};
            out_valid_reg <= 1'b0;
            for (i = 0; i < 31; i = i + 1) begin
                shift_reg[i] <= {DATA_WIDTH{1'b0}};
            end
        end else begin
            if (bypass) begin
                // Bypass mode: 1-cycle registered pipeline stage
                state <= S_IDLE;
                step  <= 4'd0;
                if (m_handshake) begin
                    if (s_handshake) begin
                        out_data_reg  <= sink_data;
                        out_valid_reg <= 1'b1;
                    end else begin
                        out_valid_reg <= 1'b0;
                    end
                end else begin
                    if (s_handshake) begin
                        out_data_reg  <= sink_data;
                        out_valid_reg <= 1'b1;
                    end
                end
            end else begin
                // Filtering mode: 31-tap folded execution
                case (state)
                    S_IDLE: begin
                        if (m_handshake) begin
                            out_valid_reg <= 1'b0;
                        end
                        if (s_handshake) begin
                            // Shift in new sample
                            shift_reg[0] <= sink_data;
                            for (i = 1; i < 31; i = i + 1) begin
                                shift_reg[i] <= shift_reg[i-1];
                            end
                            state <= S_CALC;
                            step  <= 4'd0;
                            acc   <= {ACC_WIDTH{1'b0}};
                        end
                    end

                    S_CALC: begin
                        if (m_handshake) begin
                            out_valid_reg <= 1'b0;
                        end

                        acc <= acc_final;

                        if (step == 4'd15) begin
                            out_data_reg  <= sat_out;
                            out_valid_reg <= 1'b1;
                            if (source_ready) begin
                                state <= S_IDLE;
                            end else begin
                                state <= S_WAIT_OUT;
                            end
                        end else begin
                            step <= step + 4'd1;
                        end
                    end

                    S_WAIT_OUT: begin
                        if (source_ready) begin
                            out_valid_reg <= 1'b0;
                            state         <= S_IDLE;
                        end
                    end

                    default: state <= S_IDLE;
                endcase
            end
        end
    end

endmodule
