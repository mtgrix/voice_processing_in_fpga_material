// ============================================================================
// File: rtl/v3/ch02_skid_buffer.v
// Module: ch02_skid_buffer
// Description:
//   Two-stage registered Avalon-ST Skid Buffer (elastic pipeline buffer):
//   - Fully isolates BOTH forward (data/valid) and backward (ready) paths
//     with registers to eliminate combinational timing loops.
//   - Sustains 100% throughput (1 word per cycle) when downstream is ready.
//   - When downstream stalls (m_ready = 0), in-flight upstream data is absorbed
//     into the secondary 'skid' register without data loss or duplication.
//   - Upstream ready (s_ready) depends ONLY on local register state (skid_valid),
//     breaking long combinational backpressure paths across modules.
//   - Synthesizable Verilog-2001, fully compatible with iverilog -g2012 -Wall.
// ============================================================================

`timescale 1ns/1ps

module ch02_skid_buffer #(
    parameter DATA_WIDTH = 16
) (
    input  wire                  clk,
    input  wire                  rst_n,

    // Avalon-ST Sink Interface (Upstream input)
    input  wire                  s_valid,
    input  wire [DATA_WIDTH-1:0] s_data,
    output wire                  s_ready,

    // Avalon-ST Source Interface (Downstream output)
    output wire                  m_valid,
    output wire [DATA_WIDTH-1:0] m_data,
    input  wire                  m_ready
);

    // Main register: holds data currently presented to downstream
    reg [DATA_WIDTH-1:0] main_data;
    reg                  main_valid;

    // Skid register: holds in-flight data captured when downstream stalls
    reg [DATA_WIDTH-1:0] skid_data;
    reg                  skid_valid;

    // Upstream ready is asserted whenever the skid register is empty.
    // It is driven by a local flip-flop (skid_valid), with zero combinational
    // dependence on m_ready.
    assign s_ready = ~skid_valid;

    // Downstream outputs driven directly from main register
    assign m_valid = main_valid;
    assign m_data  = main_data;

    // Internal handshake conditions
    wire s_handshake = s_valid & s_ready;
    wire m_handshake = main_valid & m_ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            main_data  <= {DATA_WIDTH{1'b0}};
            main_valid <= 1'b0;
            skid_data  <= {DATA_WIDTH{1'b0}};
            skid_valid <= 1'b0;
        end else begin
            if (m_handshake) begin
                // Downstream consumed current main_data
                if (skid_valid) begin
                    // Reload main from skid register; skid becomes empty
                    main_data  <= skid_data;
                    main_valid <= 1'b1;
                    skid_valid <= 1'b0;
                end else if (s_handshake) begin
                    // Direct feed from upstream to main register (full throughput streaming)
                    main_data  <= s_data;
                    main_valid <= 1'b1;
                end else begin
                    // Upstream had no new data; main register empties
                    main_valid <= 1'b0;
                end
            end else begin
                // Downstream stalled (m_ready == 0 or main_valid == 0)
                if (s_handshake) begin
                    if (main_valid) begin
                        // Main register is holding stalled data, so incoming beat skids into skid register
                        skid_data  <= s_data;
                        skid_valid <= 1'b1;
                    end else begin
                        // Main was empty; incoming beat fills main register
                        main_data  <= s_data;
                        main_valid <= 1'b1;
                    end
                end
            end
        end
    end

endmodule
