// SystemVerilog ALU Module
module alu #(
    parameter int WIDTH = 32
) (
    input  logic             clk,
    input  logic             rst_n,
    input  logic [3:0]       op,
    input  logic [WIDTH-1:0] a,
    input  logic [WIDTH-1:0] b,
    output logic [WIDTH-1:0] result,
    output logic             zero,
    output logic             overflow
);

    typedef enum logic [3:0] {
        OP_ADD = 4'b0000,
        OP_SUB = 4'b0001,
        OP_AND = 4'b0010,
        OP_OR  = 4'b0011,
        OP_XOR = 4'b0100,
        OP_SHL = 4'b0101,
        OP_SHR = 4'b0110
    } op_e;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result   <= '0;
            zero     <= 1'b1;
            overflow <= 1'b0;
        end else begin
            case (op)
                OP_ADD: begin
                    {overflow, result} <= {1'b0, a} + {1'b0, b};
                end
                OP_SUB: begin
                    result   <= a - b;
                    overflow <= (a < b);
                end
                OP_AND:  result <= a & b;
                OP_OR:   result <= a | b;
                OP_XOR:  result <= a ^ b;
                OP_SHL:  result <= a << b[4:0];
                OP_SHR:  result <= a >> b[4:0];
                default: begin
                    // Intentional illegal opcode check
                    $error("ALU: Illegal opcode 4'b%b executed at time %0t", op, $time);
                    result <= '0;
                end
            endcase
            zero <= (result == '0);
        end
    end

endmodule
