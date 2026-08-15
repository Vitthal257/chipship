#include <iostream>
#include <unistd.h>
#include "Vlong_alu.h"
#include "verilated.h"

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Vlong_alu* top = new Vlong_alu;

    std::cout << "[LONG SIM START] Launching multi-minute regression workload..." << std::endl;

    // Reset
    top->clk = 0; top->rst_n = 0; top->eval();
    top->clk = 1; top->rst_n = 1; top->eval();

    // Run for 380 seconds (~6.3 minutes) in 30-second steps
    int total_duration_s = 380;
    int step_s = 30;

    for (int elapsed = step_s; elapsed <= total_duration_s; elapsed += step_s) {
        sleep(step_s);
        top->op = (elapsed / 30) % 3;
        top->a = elapsed;
        top->b = elapsed * 2;
        top->clk = 0; top->eval();
        top->clk = 1; top->eval();

        std::cout << "[LONG SIM " << elapsed << "s / " << total_duration_s << "s] Step "
                  << (elapsed / step_s) << " completed. Result: " << top->result << std::endl;
        std::cout.flush();
    }

    std::cout << "[LONG SIM COMPLETE] Multi-minute regression finished successfully after "
              << total_duration_s << " seconds." << std::endl;

    top->final();
    delete top;
    return 0;
}
