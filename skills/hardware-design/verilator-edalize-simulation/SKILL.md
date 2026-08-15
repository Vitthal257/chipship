---
name: verilator-edalize-simulation
description: Run Verilator and Edalize multi-backend simulations.
version: 0.1.0
author: ChipShip Maintainers (chipship), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [verilator, edalize, simulation, hardware, regression]
    related_skills: [eda-verification-loop, cocotb-python-verification, drain3-eda-log-mining]
---

# Verilator & Edalize Simulation Skill

Compiles and executes Verilog/SystemVerilog RTL simulations across open-source EDA backends (Verilator, Icarus, Yosys) using Edalize and Huey background queues. Supports synchronous execution and non-blocking asynchronous jobs.

## When to Use

- Compiling SystemVerilog or Verilog source files into cycle-accurate simulation binaries
- Running regression suites with C++ testbench harnesses
- Dispatching long-running simulations to background queues
- Don't use for: pure Python testbenches (use `cocotb-python-verification` instead)

## Prerequisites

- Verilator binary accessible in PATH
- C++ compiler (`g++` / `clang++`) and `make` installed
- Work directory containing RTL files and optional C++ testbench

## How to Run

Execute synchronous simulation via `terminal`:

```bash
terminal(command="chipship sim test_corpus/alu_module/alu.sv --top alu --cpp test_corpus/alu_module/alu_tb.cpp", timeout=300)
```

For asynchronous background execution:

```bash
terminal(command="chipship sim test_corpus/alu_module/long_alu.sv --top long_alu --mode async --cpp test_corpus/alu_module/long_tb.cpp", timeout=60)
```

## Quick Reference

| Action | Command Pattern |
|---|---|
| Sync Simulation | `chipship sim <files...> --top <module> --cpp <tb_files...>` |
| Async Simulation | `chipship sim <files...> --top <module> --mode async` |
| Check Background Job | `chipship status <job_id>` |
| Extra Flags | `chipship sim <files...> --flags "-Wall -Wno-WIDTH"` |

## Procedure

1. **Identify Source Files & Top Module:**
   Use `search_files` to locate the target RTL files (`.sv`, `.v`) and testbench (`.cpp`).

2. **Run Simulation:**
   Invoke `terminal(command="chipship sim <files> --top <module> --cpp <tb>")`. Check exit code and duration.

3. **Handle Async Background Jobs:**
   If running in async mode, record the returned `job_id` and query status periodically via `terminal(command="chipship status <job_id>")` until status reaches `COMPLETED` or `FAILED`.

4. **Review Results:**
   Check the simulation output summary and error counts. If errors occurred, pass log to `drain3-eda-log-mining`.

## Pitfalls

- **Module Hierarchy:** Top module name specified via `--top` must match the top-level module in the RTL files.
- **Async Polling Interval:** Avoid rapid tight loops when polling background jobs; poll every few seconds.
- **Compiler Warnings as Errors:** Verilator flags like `-Wall` may treat lint warnings as fatal; pass `-Wno-<lint>` when needed.

## Verification

1. Run `terminal(command="chipship sim test_corpus/alu_module/alu.sv --top alu --cpp test_corpus/alu_module/alu_tb.cpp")`.
2. Verify output displays `Simulation Status: COMPLETED`.
