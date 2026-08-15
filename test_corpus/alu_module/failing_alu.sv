// Failing SystemVerilog ALU Module with Intentional Verilator & Runtime Errors
module failing_alu (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [3:0]  op,
    input  logic [31:0] a,
    input  logic [31:0] b,
    output logic [31:0] result,
    output logic        overflow
);

    logic [63:0] wide_acc;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result   <= '0;
            overflow <= '0;
            wide_acc <= '0;
        end else begin
            case (op)
                4'b0000: begin // ADD
                    wide_acc <= a + b;
                    result   <= wide_acc; // Width mismatch / delay hazard
                end
                4'b1111: begin // Illegal Opcode
                    $fatal(1, "ALU FATAL: Invalid instruction opcode 4'b1111 encountered at time %0t", $time);
                end
                default: begin
                    $display("ALU WARNING: Unknown opcode %b", op);
                    result <= 32'hDEADBEEF;
                end
            endcase
        end
    end

endmodule
