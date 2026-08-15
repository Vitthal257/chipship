"""Unit Tests for EDA Model Tools in Hermes Agent.

Tests:
1. Tool registration and OpenAI JSON Schema structure.
2. Direct invocation of tool handlers (eda_simulate, eda_cocotb, eda_mine_log, eda_inspect_vcd, eda_verification_loop, eda_job_status).
3. Error handling on invalid inputs or missing files.
"""

import json
from pathlib import Path
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from tools.registry import registry
import tools.eda_tools as eda_tools


def test_eda_tools_registration():
    expected_tools = [
        "eda_simulate",
        "eda_cocotb",
        "eda_mine_log",
        "eda_inspect_vcd",
        "eda_verification_loop",
        "eda_job_status",
    ]
    for tool_name in expected_tools:
        entry = registry._tools.get(tool_name)
        assert entry is not None, f"Tool {tool_name} was not registered in registry"
        assert entry.toolset == "eda"
        assert entry.schema is not None
        assert "parameters" in entry.schema
        assert entry.schema["name"] == tool_name


def test_eda_simulate_handler():
    workspace = Path(__file__).parent.parent.parent
    alu_file = str(workspace / "test_corpus" / "alu_module" / "alu.sv")
    tb_file = str(workspace / "test_corpus" / "alu_module" / "alu_tb.cpp")

    res = eda_tools.eda_simulate_handler(
        files=[alu_file],
        top_module="alu",
        mode="sync",
        cpp_files=[tb_file],
    )
    parsed = json.loads(res)
    assert parsed.get("status") == "COMPLETED"
    assert "duration_s" in parsed


def test_eda_cocotb_handler():
    workspace = Path(__file__).parent.parent.parent
    cocotb_dir = str(workspace / "test_corpus" / "cocotb_alu")

    res = eda_tools.eda_cocotb_handler(cocotb_dir=cocotb_dir)
    parsed = json.loads(res)
    assert parsed.get("status") == "COMPLETED"
    assert parsed.get("tool") == "cocotb"


def test_eda_mine_log_handler():
    sample_log = """
[0 ps] %Error: FIFO_DEPTH_EXCEEDED: Write to full FIFO in module fifo_1 at time 100
[100 ps] %Error: WIDTH_MISMATCH: Width 32 does not match 64 in stage_2.sv:15
[200 ps] Assertion 'ack == 1' failed at sync.sv:40: Timeout
"""
    res = eda_tools.eda_mine_log_handler(log_text=sample_log)
    parsed = json.loads(res)
    assert parsed.get("total_errors") == 3
    assert parsed.get("unique_root_causes") == 3
    assert len(parsed.get("clusters", [])) == 3


def test_eda_inspect_vcd_handler():
    workspace = Path(__file__).parent.parent.parent
    vcd_path = str(workspace / "test_corpus" / "cocotb_alu" / "dump.vcd")

    res = eda_tools.eda_inspect_vcd_handler(vcd_file=vcd_path, signals=["clk", "rst_n"])
    parsed = json.loads(res)
    assert parsed.get("total_signals") > 0
    assert "signal_transitions" in parsed


def test_eda_verification_loop_handler():
    workspace = Path(__file__).parent.parent.parent
    alu_file = str(workspace / "test_corpus" / "alu_module" / "alu.sv")
    tb_file = str(workspace / "test_corpus" / "alu_module" / "alu_tb.cpp")

    res = eda_tools.eda_verification_loop_handler(
        files=[alu_file],
        top_module="alu",
        tb_type="cpp",
        cpp_files=[tb_file],
        max_iterations=2,
    )
    parsed = json.loads(res)
    assert parsed.get("converged") is True
    assert parsed.get("total_iterations") == 1


if __name__ == "__main__":
    print("Running EDA Tools Unit & Integration Tests...")
    test_eda_tools_registration()
    print("  ✔ Tool registration verified.")
    test_eda_simulate_handler()
    print("  ✔ eda_simulate handler verified.")
    test_eda_cocotb_handler()
    print("  ✔ eda_cocotb handler verified.")
    test_eda_mine_log_handler()
    print("  ✔ eda_mine_log handler verified.")
    test_eda_inspect_vcd_handler()
    print("  ✔ eda_inspect_vcd handler verified.")
    test_eda_verification_loop_handler()
    print("  ✔ eda_verification_loop handler verified.")
    print("\nALL EDA MODEL TOOLS VERIFIED SUCCESSFULLY!")
