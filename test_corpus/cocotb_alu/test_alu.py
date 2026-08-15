"""Python-native cocotb Testbench for SystemVerilog ALU.

Enables LLM agents to generate, inspect, and modify simulation testbenches natively in Python.
"""

import cocotb
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock


@cocotb.test()
async def alu_add_test(dut):
    """Test ALU Addition operation (15 + 27 = 42)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # ADD: 15 + 27 = 42
    dut.op.value = 0  # OP_ADD
    dut.a.value = 15
    dut.b.value = 27
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.result.value == 42, f"Expected 42, got {dut.result.value}"
    dut._log.info("[COCOTB] ADD Test Passed: 15 + 27 = 42")


@cocotb.test()
async def alu_xor_test(dut):
    """Test ALU XOR operation (0xFF ^ 0x0F = 0xF0)."""
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # XOR: 0xFF ^ 0x0F = 0xF0
    dut.op.value = 4  # OP_XOR
    dut.a.value = 0xFF
    dut.b.value = 0x0F
    await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert dut.result.value == 0xF0, f"Expected 0xF0, got {hex(dut.result.value)}"
    dut._log.info("[COCOTB] XOR Test Passed: 0xFF ^ 0x0F = 0xF0")
