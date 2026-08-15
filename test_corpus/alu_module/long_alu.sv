// Long-running SystemVerilog ALU module for regression simulation
module long_alu (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [3:0]  op,
    input  logic [31:0] a,
    input  logic [31:0] b,
    output logic [31:0] result
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result <= '0;
        end else begin
            case (op)
                4'b0000: result <= a + b;
                4'b0001: result <= a - b;
                default: result <= a ^ b;
            endcase
        end
    end

endmodule
