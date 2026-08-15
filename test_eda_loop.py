"""End-to-End Closed-Loop Verification Moderator Test Suite.

Demonstrates closed-loop tool orchestration between:
1. RTL Simulation (Verilator / Edalize / cocotb)
2. Drain3 Log Template Mining & Failure Signature Extraction
3. VCD Waveform Inspection
4. Automated Diagnosis & RTL Patching
5. Re-Verification Loop Convergence
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from eda_agent.moderator import EdaVerificationModerator
from eda_agent.vcd_parser import inspect_vcd_waveform


def test_closed_loop_passing_run():
    print("==================================================================")
    print("LOOP TEST 1: PASSING DESIGN VERIFICATION LOOP CONVERGENCE")
    print("==================================================================")

    corpus_dir = Path(__file__).parent / "test_corpus" / "alu_module"
    moderator = EdaVerificationModerator(work_dir=str(corpus_dir))

    result = moderator.run_moderated_loop(
        files=["alu.sv"],
        top_module="alu",
        tb_type="cpp",
        cpp_files=["alu_tb.cpp"],
        max_iterations=3,
    )

    print(f"Loop Converged: {result['converged']}")
    print(f"Total Iterations: {result['total_iterations']}")
    print(f"Total Duration: {result['total_duration_s']}s")

    assert result["converged"] is True
    assert result["total_iterations"] == 1
    assert result["final_status"] == "PASSED"
    print("[LOOP TEST 1 PASSED]\n")


def test_closed_loop_failing_with_patch_callback():
    print("==================================================================")
    print("LOOP TEST 2: FAILING RTL -> DRAIN3 LOG MINING -> CODE PATCH -> RE-SIM PASS")
    print("==================================================================")

    # Create temporary copy of failing ALU corpus to mutate
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        corpus_dir = Path(__file__).parent / "test_corpus" / "alu_module"
        
        for f in corpus_dir.iterdir():
            if f.is_file():
                shutil.copy(f, tmp_path / f.name)

        moderator = EdaVerificationModerator(work_dir=str(tmp_path))

        def fix_alu_opcode_bug(context):
            """Simulates Hermes agent diagnosing Drain3 templates and patching RTL."""
            print(f"\n  [Hermes Agent Moderator Intervention at Iteration {context['iteration']}]")
            mined = context["mined_diagnostics"]
            print(f"  Mined {mined['total_errors']} error events with {mined['unique_root_causes']} distinct templates.")
            
            for cl in mined["clusters"]:
                print(f"  • Template: {cl['signature']}")

            # Patch failing_alu.sv to support opcode 4'b1111 (NOP / PASS)
            failing_sv = tmp_path / "failing_alu.sv"
            code = failing_sv.read_text()
            
            # Replace fatal assertion on opcode 4'b1111 with safe PASS assignment
            target_str = '$fatal(1, "ALU FATAL: Invalid instruction opcode 4\'b1111 encountered at time %0t", $time);'
            replacement_str = 'result <= a; // Fixed opcode 4\'b1111 support'
            assert target_str in code, f"Could not find target fatal string in {failing_sv}"
            fixed_code = code.replace(target_str, replacement_str)
            failing_sv.write_text(fixed_code)
            print("  ✔ Successfully patched failing_alu.sv to support opcode 4'b1111.")
            return True

        result = moderator.run_moderated_loop(
            files=["failing_alu.sv"],
            top_module="failing_alu",
            tb_type="cpp",
            cpp_files=["failing_tb.cpp"],
            extra_flags=["-Wno-WIDTH"],
            max_iterations=3,
            patch_callback=fix_alu_opcode_bug,
        )

        print(f"\nFinal Moderated Loop Result:")
        print(f"  Converged:        {result['converged']}")
        print(f"  Total Iterations: {result['total_iterations']}")
        print(f"  Final Status:     {result['final_status']}")

        assert result["converged"] is True
        assert result["total_iterations"] == 2
        assert result["final_status"] == "PASSED"
        print("\n[LOOP TEST 2 PASSED — Closed-Loop Auto-Diagnosis & Patching Verified]\n")


def test_closed_loop_cocotb_with_waveform():
    print("==================================================================")
    print("LOOP TEST 3: COCOTB PYTHON TESTBENCH WITH VCD WAVEFORM ATTACHMENT")
    print("==================================================================")

    cocotb_dir = Path(__file__).parent / "test_corpus" / "cocotb_alu"
    moderator = EdaVerificationModerator(work_dir=str(cocotb_dir))

    result = moderator.run_moderated_loop(
        files=["alu.sv"],
        top_module="alu",
        tb_type="cocotb",
        cocotb_dir=str(cocotb_dir),
        max_iterations=1,
    )

    print(f"cocotb Loop Converged: {result['converged']}")
    print(f"VCD Waveform Inspected: {result['vcd_inspected']}")

    assert result["converged"] is True
    assert result["vcd_inspected"] is True
    print("[LOOP TEST 3 PASSED]\n")


if __name__ == "__main__":
    print("Starting Complete Closed-Loop Verification Moderator Suite...\n")
    test_closed_loop_passing_run()
    test_closed_loop_failing_with_patch_callback()
    test_closed_loop_cocotb_with_waveform()
    print("ALL CLOSED-LOOP MODERATOR TESTS COMPLETED SUCCESSFULLY!")
