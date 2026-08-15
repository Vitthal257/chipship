---
title: "Eda Verification Loop — Run closed-loop EDA regression, diagnosis, and patching"
sidebar_label: "Eda Verification Loop"
description: "Run closed-loop EDA regression, diagnosis, and patching"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Eda Verification Loop

Run closed-loop EDA regression, diagnosis, and patching.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/hardware-design/eda-verification-loop` |
| Version | `0.1.0` |
| Author | ChipShip Maintainers (chipship), Hermes Agent |
| License | MIT |
| Platforms | linux, macos |
| Tags | `eda`, `verification`, `verilator`, `cocotb`, `loops`, `hardware` |
| Related skills | [`verilator-edalize-simulation`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-verilator-edalize-simulation), [`cocotb-python-verification`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-cocotb-python-verification), [`drain3-eda-log-mining`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-drain3-eda-log-mining), [`vcd-waveform-analysis`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-vcd-waveform-analysis) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Hermes loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# EDA Verification Loop Skill

Coordinates closed-loop hardware verification between RTL compilation, simulation, log template mining, waveform analysis, and automated code repair. Uses Hermes to moderate tool feedback cycles until regression tests pass cleanly.

## When to Use

- Running automated regression loops that diagnose and patch failing RTL modules
- Iterating between simulation runs, failure triage, and bug fixing
- Orchestrating multi-tool verification workflows across Verilator, cocotb, Drain3, and VCD inspection
- Don't use for: simple one-off file reads without simulation runs

## Prerequisites

- ChipShip EDA stack installed with Conda toolchain in PATH (`/home/virtual/miniconda3/bin`)
- Verilator 5.x, cocotb 2.x, Drain3, and Python dependencies installed

## How to Run

Execute the verification loop via the `terminal` tool:

```bash
terminal(command="chipship loop test_corpus/alu_module/alu.sv --top alu --tb test_corpus/alu_module/alu_tb.cpp", timeout=300)
```

For cocotb Python testbenches:

```bash
terminal(command="chipship loop test_corpus/cocotb_alu/alu.sv --top alu --tb-type cocotb --cocotb-dir test_corpus/cocotb_alu", timeout=300)
```

## Quick Reference

| Action | Command Pattern |
|---|---|
| Run C++ TB Loop | `chipship loop <rtl_files> --top <top_module> --tb <cpp_tb>` |
| Run cocotb Loop | `chipship loop <rtl_files> --top <top_module> --tb-type cocotb --cocotb-dir <dir>` |
| Query Job Status | `chipship status <job_id>` |
| Mine Log Errors | `chipship analyze <log_file>` |

## Procedure

1. **Invoke Simulation Run:**
   Execute `terminal(command="chipship loop ...")` to launch the initial compilation and testbench cycle. Check that process returns execution status and log path.

2. **Evaluate Output & Mine Signatures:**
   If simulation fails, read the Drain3 failure summary from tool output or call `terminal(command="chipship analyze <log_file>")`. Confirm unique root-cause templates and line numbers.

3. **Inspect Waveform Transitions:**
   If a VCD file was generated, use `vcd-waveform-analysis` to inspect signal transitions around the failure timestamp or assertion failure cycle.

4. **Apply RTL or Testbench Patch:**
   Read the offending RTL or testbench lines using `read_file`. Use `patch` to modify the source code to resolve the diagnosed bug.

5. **Re-run Regression Loop:**
   Trigger the verification loop again via `terminal` and verify that all assertions pass with zero errors.

## Pitfalls

- **Missing Conda PATH:** Ensure `/home/virtual/miniconda3/bin` is in PATH or invoke commands through `chipship`.
- **Large Simulation Logs:** Do not load raw multi-megabyte log files directly into context; always use `chipship analyze` or Drain3 compression summaries.
- **VCD File Missing:** Waveform dumps require `$dumpvars` in Verilog or `--trace` in Verilator build options.

## Verification

1. Run `terminal(command="chipship loop test_corpus/alu_module/alu.sv --top alu --tb test_corpus/alu_module/alu_tb.cpp")`.
2. Confirm the loop status reports `COMPLETED` or `PASSED`.
3. Confirm zero error templates remain in the output summary.
