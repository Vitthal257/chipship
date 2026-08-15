#include <iostream>
#include <cassert>
#include "Valu.h"
#include "verilated.h"

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Valu* top = new Valu;

    // Reset cycle
    top->clk = 0;
    top->rst_n = 0;
    top->eval();

    top->clk = 1;
    top->rst_n = 1;
    top->eval();

    // Test ADD: 15 + 27 = 42
    top->op = 0; // OP_ADD
    top->a = 15;
    top->b = 27;
    top->clk = 0; top->eval();
    top->clk = 1; top->eval();

    std::cout << "[ALU TB] ADD Result: " << top->result << " (expected 42)" << std::endl;
    assert(top->result == 42);

    // Test XOR: 0xFF ^ 0x0F = 0xF0
    top->op = 4; // OP_XOR
    top->a = 0xFF;
    top->b = 0x0F;
    top->clk = 0; top->eval();
    top->clk = 1; top->eval();

    std::cout << "[ALU TB] XOR Result: 0x" << std::hex << top->result << " (expected 0xf0)" << std::endl;
    assert(top->result == 0xF0);

    std::cout << "[ALU TB] ALL TESTS PASSED!" << std::endl;

    top->final();
    delete top;
    return 0;
}
