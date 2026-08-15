module sub_regfile (
    input  logic        clk,
    input  logic [3:0]  addr,
    input  logic [31:0] wdata,
    output logic [31:0] rdata
);
    logic [31:0] mem [7:0]; // Size 8 (valid indices 0-7)
    logic [31:0] undriven_sig; // Intentional undriven warning

    always_ff @(posedge clk) begin
        // Out-of-bounds SELRANGE index (addr is 4-bit, max 15, but mem is size 8)
        mem[addr] <= wdata;
    end

    assign rdata = mem[addr[2:0]];
endmodule
