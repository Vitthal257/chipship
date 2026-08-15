"""Empirical VCD Waveform Parser Evaluation Script.

Tests inspect_vcd_waveform against real SystemVerilog cocotb VCD dump (dump.vcd).
"""

import sys
import json
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from eda_agent.vcd_parser import inspect_vcd_waveform


def test_vcd_parser_empirical():
    vcd_path = Path(__file__).parent / "test_corpus" / "cocotb_alu" / "dump.vcd"
    print(f"Testing inspect_vcd_waveform on real VCD dump: {vcd_path} ({vcd_path.stat().st_size:,} bytes)...")

    # Inspect all signals
    res = inspect_vcd_waveform(str(vcd_path), max_changes=20)
    print("\nParsed VCD Structure Summary:")
    print(f"  VCD File:          {res['vcd_file']}")
    print(f"  Total Signals:     {res['total_signals']}")
    print(f"  Time Range:        {res['time_range']}")
    print(f"  Inspected Signals: {res['inspected_signals']}")

    print("\nSignal Transition Timeline:")
    for sig, transitions in res["signal_transitions"].items():
        print(f"  • Signal: {sig}")
        for tv in transitions[:5]:
            print(f"      t={tv['time']} ns: value = {tv['value']}")

    assert res["total_signals"] > 0, "Expected signals in VCD file"
    assert "signal_transitions" in res
    print("\n[EMPIRICAL VCD BENCHMARK PASSED SUCCESSFULLY]")


if __name__ == "__main__":
    test_vcd_parser_empirical()
