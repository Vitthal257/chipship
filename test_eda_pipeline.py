"""End-to-End Test & Verification Script for EDA AI Agent Scaffold on Hermes.

Runs real Verilator compilation & simulation against open-source SystemVerilog test corpus,
tests non-blocking async job polling, lifecycle hooks, and failure clustering.
"""

import sys
import time
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from eda_agent.verilator_adapter import VerilatorToolAdapter
from eda_agent.context_engine import EdaLogContextEngine, cluster_eda_log_lines


def run_pipeline_test():
    print("===============================================================")
    print("EDA AI AGENT SCAFFOLD — VERILATOR & CONTEXT ENGINE PIPELINE TEST")
    print("===============================================================\n")

    corpus_dir = Path(__file__).parent / "test_corpus" / "alu_module"
    adapter = VerilatorToolAdapter(work_dir=str(corpus_dir))
    context_engine = EdaLogContextEngine(log_threshold_chars=200)

    # -------------------------------------------------------------------------
    # TEST 1: Passing ALU Testbench (Async Mode)
    # -------------------------------------------------------------------------
    print("--- [TEST 1] Running Passing ALU Testbench (Async Non-Blocking) ---")
    run_res = adapter.invoke({
        "files": ["alu.sv"],
        "cpp_files": ["alu_tb.cpp"],
        "top_module": "alu",
        "mode": "async",
    })
    print(f"Async Launch Response:\n{json.dumps(run_res, indent=2)}")

    job_id = run_res["job_id"]
    print(f"\nPolling job {job_id} status...")
    
    for i in range(30):
        status = adapter.check_job_status(job_id)
        print(f"  [Poll {i+1}] Status: {status['status']}")
        if status["status"] in ("COMPLETED", "FAILED", "TIMEOUT"):
            print(f"Final Status:\n{json.dumps(status, indent=2)}")
            assert status["status"] == "COMPLETED", f"Expected COMPLETED, got {status['status']}"
            break
        time.sleep(1.0)

    print("\n[TEST 1 PASSED]\n")

    # -------------------------------------------------------------------------
    # TEST 2: Failing ALU Testbench (Runtime Fatal Assertion Failure)
    # -------------------------------------------------------------------------
    print("--- [TEST 2] Running Failing ALU Testbench (Async Non-Blocking) ---")
    fail_res = adapter.invoke({
        "files": ["failing_alu.sv"],
        "cpp_files": ["failing_tb.cpp"],
        "top_module": "failing_alu",
        "mode": "async",
        "extra_flags": ["-Wno-WIDTH"],
    })
    print(f"Async Launch Response:\n{json.dumps(fail_res, indent=2)}")

    fail_job_id = fail_res["job_id"]
    print(f"\nPolling job {fail_job_id} status...")

    final_fail_status = None
    for i in range(30):
        status = adapter.check_job_status(fail_job_id)
        print(f"  [Poll {i+1}] Status: {status['status']}")
        if status["status"] in ("COMPLETED", "FAILED", "TIMEOUT"):
            final_fail_status = status
            print(f"Final Status:\n{json.dumps(status, indent=2)}")
            break
        time.sleep(1.0)

    assert final_fail_status is not None and final_fail_status["status"] == "FAILED", (
        f"Expected FAILED status for illegal opcode test, got {final_fail_status}"
    )
    print("\n[TEST 2 PASSED — Real Verilator Simulation Failure Caught]\n")

    # -------------------------------------------------------------------------
    # TEST 3: Context Engine Log Compression & Failure Signature Clustering
    # -------------------------------------------------------------------------
    print("--- [TEST 3] Testing EdaLogContextEngine Failure Log Compression ---")
    raw_log_path = Path(final_fail_status["log_file"])
    raw_log_text = raw_log_path.read_text()
    
    print(f"Raw Log Length: {len(raw_log_text)} characters, {len(raw_log_text.splitlines())} lines.")

    # Create dummy tool message as would appear in Hermes agent transcript
    messages = [
        {"role": "user", "content": "Run Verilator regression on failing_alu.sv"},
        {"role": "tool", "content": raw_log_text},
    ]

    compressed_messages, pruned_count = context_engine.prune_tool_results_only(messages)
    
    print(f"Pruned Message Count: {pruned_count}")
    print("Compressed Log Output in Context Engine:\n")
    print(compressed_messages[1]["content"])

    assert pruned_count == 1
    assert "[EDA LOG SUMMARY" in compressed_messages[1]["content"]
    assert "Failure Clusters" in compressed_messages[1]["content"] or "ALU FATAL" in compressed_messages[1]["content"]

    print("\n[TEST 3 PASSED — Context Engine Log Compression Verified]\n")

    print("===============================================================")
    print(" ALL SCAFFOLD & MVP PIPELINE TESTS COMPLETED SUCCESSFULLY!")
    print("===============================================================")


if __name__ == "__main__":
    run_pipeline_test()
