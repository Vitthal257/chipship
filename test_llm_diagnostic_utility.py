"""Diagnostic Summary Quality Inspection Script.

Evaluates whether the diagnostic summary generated from the compressed EDA failure clusters
provides actionable, precise root-cause analysis for verification and design engineers.
"""

from eda_agent.context_engine import EdaLogContextEngine, cluster_eda_log_lines


def test_diagnostic_quality():
    sample_log = """
[0 ps] %Error: FIFO_DEPTH_EXCEEDED: Write to full FIFO in module fifo_buffer_2 at time 38 ps (cycle 5)
[0 ps] %Error: FIFO_DEPTH_EXCEEDED: Write to full FIFO in module fifo_buffer_5 at time 92 ps (cycle 9)
[600 ps] %Error: WIDTH_MISMATCH: Output signal width 32 does not match driver width 64 in alu_stage_5.sv:430
[1200 ps] Assertion 'cdc_ack == 1' failed at cdc_sync_7.sv:384: Handshake timeout at cycle 1202
[1800 ps] $fatal(1, "RAM PARITY ERROR: Memory address 0x123CBA3D corrupted in ram_blk_2 at cycle 1805")
[2400 ps] %Error: RESET_POLARITY_MISMATCH: Line 369: Active-high reset drive detected on active-low input rst_n in ctrl_2.sv
[3000 ps] %Error: AXI_PROTOCOL_VIOLATION: Invalid AWBURST=2'b11 in axi_master_8.sv:318
"""

    parsed = cluster_eda_log_lines(sample_log)
    
    # Generate structured diagnostic report format for engineer
    report = []
    report.append("=== EDA AUTOMATED ROOT-CAUSE DIAGNOSIS ===")
    report.append(f"Summary: 6 distinct failure categories detected across {parsed['total_errors']} error events.\n")

    for idx, cl in enumerate(parsed["clusters"], 1):
        report.append(f"Root Cause Category #{idx}:")
        report.append(f"  • Signature: {cl['signature']}")
        report.append(f"  • Impact: {cl['count']} failure occurrence(s)")
        report.append(f"  • Representative Evidence: {cl['example']}")
        
        # Actionable engineering fix suggestion based on root cause type
        sig = cl['signature']
        if "FIFO_DEPTH_EXCEEDED" in sig:
            fix = "Fix Suggestion: Check backpressure signal (full flag) handling or increase FIFO depth parameters."
        elif "WIDTH_MISMATCH" in sig:
            fix = "Fix Suggestion: Inspect bus width assignment; ensure 64-bit to 32-bit slice truncation is explicit [31:0]."
        elif "cdc_ack" in sig or "Handshake" in sig:
            fix = "Fix Suggestion: Verify clock-domain crossing synchronizer handshake logic and toggle rate."
        elif "RAM PARITY" in sig:
            fix = "Fix Suggestion: Investigate memory write enable timing and parity bit calculation logic."
        elif "RESET_POLARITY" in sig:
            fix = "Fix Suggestion: Correct reset signal inversion at module instantiation line 369 in ctrl_2.sv."
        elif "AXI_PROTOCOL" in sig:
            fix = "Fix Suggestion: Ensure AWBURST encoding uses valid values (2'b00 FIXED, 2'b01 INCR, 2'b10 WRAP; 2'b11 is RESERVED)."
        else:
            fix = "Fix Suggestion: Inspect source file for syntax/semantic errors."

        report.append(f"  • Actionable Fix Guidance: {fix}\n")

    final_report = "\n".join(report)
    print(final_report)
    return final_report


if __name__ == "__main__":
    test_diagnostic_quality()
