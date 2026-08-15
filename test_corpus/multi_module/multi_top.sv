module multi_top (
    input  logic        clk,
    input  logic [31:0] in_a,
    input  logic [15:0] in_b,
    input  logic [3:0]  addr,
    output logic [31:0] alu_out,
    output logic [31:0] reg_out
);

    sub_alu u_alu (
        .a(in_a),
        .b(in_b),
        .out(alu_out)
    );

    sub_regfile u_regfile (
        .clk(clk),
        .addr(addr),
        .wdata(in_a),
        .rdata(reg_out)
    );

endmodule
