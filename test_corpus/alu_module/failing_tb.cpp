#include <iostream>
#include "Vfailing_alu.h"
#include "verilated.h"

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Vfailing_alu* top = new Vfailing_alu;

    // Reset
    top->clk = 0; top->rst_n = 0; top->eval();
    top->clk = 1; top->rst_n = 1; top->eval();

    // Valid ADD
    top->op = 0; top->a = 100; top->b = 200;
    top->clk = 0; top->eval();
    top->clk = 1; top->eval();

    std::cout << "[SIM] ADD output: " << top->result << std::endl;

    // Trigger Fatal Opcode (4'b1111)
    std::cout << "[SIM] Injecting illegal opcode 4'b1111..." << std::endl;
    top->op = 15;
    top->clk = 0; top->eval();
    top->clk = 1; top->eval(); // Will trigger $fatal in verilator simulation!

    top->final();
    delete top;
    return 0;
}
