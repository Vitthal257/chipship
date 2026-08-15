module sub_alu (
    input  logic [31:0] a,
    input  logic [15:0] b,
    output logic [31:0] out
);
    // Width mismatch: 32-bit assigned to 16-bit operation without truncation
    always_comb begin
        out = a + b;
    end
endmodule
