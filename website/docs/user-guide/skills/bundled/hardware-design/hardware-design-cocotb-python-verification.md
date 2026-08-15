---
title: "Cocotb Python Verification — Execute Python cocotb testbenches and verify RTL"
sidebar_label: "Cocotb Python Verification"
description: "Execute Python cocotb testbenches and verify RTL"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Cocotb Python Verification

Execute Python cocotb testbenches and verify RTL.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/hardware-design/cocotb-python-verification` |
| Version | `0.1.0` |
| Author | ChipShip Maintainers (chipship), Hermes Agent |
| License | MIT |
| Platforms | linux, macos |
| Tags | `cocotb`, `python`, `testbench`, `verification`, `vpi`, `hardware` |
| Related skills | [`eda-verification-loop`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-eda-verification-loop), [`verilator-edalize-simulation`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-verilator-edalize-simulation), [`vcd-waveform-analysis`](/docs/user-guide/skills/bundled/hardware-design/hardware-design-vcd-waveform-analysis) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Hermes loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# cocotb Python Testbench Verification Skill

Runs Python-native testbenches against Verilog and SystemVerilog designs using cocotb, coroutine clocks, async triggers, and assertion monitors. Produces VCD waveform traces and structured test reports.

## When to Use

- Executing Python-driven testbenches using `@cocotb.test()` decorators
- Verifying complex protocol interfaces, packet generators, or randomized test vectors
- Generating VCD waveform dumps from Python simulation environments
- Don't use for: C++ or SystemC testbenches (use `verilator-edalize-simulation`)

## Prerequisites

- `cocotb` v2.x and `cocotb-config` installed in the Python environment
- Make-based testbench runner with `Makefile` defining `SIM=verilator` and `TOPLEVEL`

## How to Run

Execute cocotb testbench suites via `terminal`:

```bash
terminal(command="chipship cocotb", timeout=300)
```

Or run directly inside the test directory:

```bash
terminal(command="make -C test_corpus/cocotb_alu", timeout=300)
```

## Quick Reference

| Action | Command Pattern |
|---|---|
| Run Default cocotb TB | `chipship cocotb` |
| Run Directory cocotb | `make -C <cocotb_test_dir>` |
| Clean Build Artifacts | `make -C <cocotb_test_dir> clean` |
| Inspect VCD Output | `chipship analyze-vcd <cocotb_test_dir>/dump.vcd` |

## Procedure

1. **Locate Testbench & Makefile:**
   Use `search_files` to verify the presence of `test_*.py` and `Makefile` configuring cocotb variables (`VERILOG_SOURCES`, `TOPLEVEL`, `MODULE`).

2. **Execute Testbench:**
   Run `terminal(command="chipship cocotb")` or `terminal(command="make -C <dir>")`.

3. **Evaluate Test Results:**
   Check stdout for cocotb results table. Ensure test counts match expected scenarios and status indicates `PASS`.

4. **Investigate Failures:**
   If a test failed, inspect assertion failure line numbers in `test_*.py` and examine the generated `dump.vcd` using `vcd-waveform-analysis`.

## Pitfalls

- **Async/Await Syntax:** cocotb test functions must be async coroutines (`async def`) using `await Timer(...)` or `await RisingEdge(dut.clk)`.
- **Signal Access:** Signals on the DUT must match the exact port names defined in the top-level SystemVerilog module.

## Verification

1. Run `terminal(command="chipship cocotb")`.
2. Confirm output contains `PASS` and `All Python cocotb Testbench Assertions Passed!`.
