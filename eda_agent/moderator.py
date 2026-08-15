"""EDA Tool Moderator and Closed-Loop Verification Orchestrator.

Hermes moderates all EDA tools (Edalize, Verilator, cocotb, Drain3, VCD parser, Huey queue),
forming automated closed feedback loops:
  [RTL / TB] -> [Simulate (Verilator/cocotb)] -> [Drain3 Log Mining] -> [VCD Signal Trace]
      ^                                                                      |
      |---------------- [Hermes Diagnostic & Patch] <-----------------------|
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from eda_agent.adapter import EdalizeToolAdapter
from eda_agent.verilator_adapter import VerilatorToolAdapter
from eda_agent.context_engine import cluster_eda_log_with_drain3
from eda_agent.vcd_parser import inspect_vcd_waveform
from eda_agent.job_queue import HueyJobManager

logger = logging.getLogger(__name__)


class EdaVerificationModerator:
    """Moderates execution, diagnosis, waveform tracing, and iterative refinement across all EDA tools."""

    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = Path(work_dir or os.getcwd()).resolve()
        self.jobs_dir = self.work_dir / ".eda_jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.history: List[Dict[str, Any]] = []

    def run_simulation_step(
        self,
        files: List[str],
        top_module: str,
        tb_type: str = "cpp",
        cpp_files: Optional[List[str]] = None,
        cocotb_dir: Optional[str] = None,
        extra_flags: Optional[List[str]] = None,
        timeout_s: float = 300.0,
    ) -> Dict[str, Any]:
        """Execute a single simulation step via Verilator, Edalize, or cocotb."""
        flags = extra_flags or ["-Wall"]
        cpp = cpp_files or []

        if tb_type == "cocotb":
            target_dir = Path(cocotb_dir).resolve() if cocotb_dir else self.work_dir
            import subprocess
            env = dict(os.environ)
            env["PATH"] = f"/home/virtual/miniconda3/bin:{env.get('PATH', '')}"
            start_t = time.time()
            res = subprocess.run(
                ["make"],
                cwd=str(target_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                timeout=timeout_s,
            )
            duration = round(time.time() - start_t, 2)
            raw_output = res.stdout
            status = "COMPLETED" if (res.returncode == 0 and ("PASS" in raw_output or "passed" in raw_output)) else "FAILED"
            log_file = self.jobs_dir / f"cocotb_{int(time.time())}.log"
            log_file.write_text(raw_output)

            vcd_path = target_dir / "dump.vcd"
            return {
                "status": status,
                "tool": "cocotb",
                "duration_s": duration,
                "returncode": res.returncode,
                "raw_output": raw_output,
                "log_file": str(log_file),
                "vcd_file": str(vcd_path) if vcd_path.exists() else None,
            }
        else:
            adapter = VerilatorToolAdapter(work_dir=str(self.work_dir))
            res = adapter.invoke({
                "files": files,
                "top_module": top_module,
                "mode": "sync",
                "cpp_files": cpp,
                "extra_flags": flags,
                "timeout_s": timeout_s,
            })
            log_p = Path(res.get("log_file", ""))
            raw_output = log_p.read_text() if log_p.exists() else ""
            
            # Check for possible VCD dump files
            vcd_candidate = self.work_dir / f"{top_module}.vcd"
            if not vcd_candidate.exists():
                vcd_candidate = self.work_dir / "dump.vcd"

            return {
                "status": res.get("status", "FAILED"),
                "tool": "verilator",
                "job_id": res.get("job_id"),
                "duration_s": res.get("duration_s", 0),
                "returncode": res.get("returncode", 0),
                "raw_output": raw_output,
                "log_file": res.get("log_file"),
                "parsed_results": res.get("parsed_results", {}),
                "vcd_file": str(vcd_candidate) if vcd_candidate.exists() else None,
            }

    def mine_log_diagnostics(self, raw_output: str) -> Dict[str, Any]:
        """Mine log templates using Drain3 to extract error clusters and signatures."""
        return cluster_eda_log_with_drain3(raw_output)

    def trace_waveform_signals(
        self,
        vcd_path: str,
        signals: Optional[List[str]] = None,
        max_changes: int = 30,
    ) -> Dict[str, Any]:
        """Parse VCD waveform and retrieve signal transition timelines."""
        return inspect_vcd_waveform(vcd_path, signals=signals, max_changes=max_changes)

    def run_moderated_loop(
        self,
        files: List[str],
        top_module: str,
        tb_type: str = "cpp",
        cpp_files: Optional[List[str]] = None,
        cocotb_dir: Optional[str] = None,
        extra_flags: Optional[List[str]] = None,
        max_iterations: int = 5,
        patch_callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> Dict[str, Any]:
        """Run complete closed verification loop across all tools until PASS or max iterations."""
        loop_start = time.time()
        iteration = 0
        all_passed = False
        iteration_records = []

        while iteration < max_iterations:
            iteration += 1
            logger.info("=== EDA MODERATION LOOP ITERATION %d / %d ===", iteration, max_iterations)

            # Step 1: Run simulation tool
            sim_result = self.run_simulation_step(
                files=files,
                top_module=top_module,
                tb_type=tb_type,
                cpp_files=cpp_files,
                cocotb_dir=cocotb_dir,
                extra_flags=extra_flags,
            )

            # Step 2: Mine failure log with Drain3
            mined_diagnostics = self.mine_log_diagnostics(sim_result["raw_output"])

            # Step 3: Inspect VCD waveform if available
            vcd_info = None
            if sim_result.get("vcd_file") and Path(sim_result["vcd_file"]).exists():
                vcd_info = self.trace_waveform_signals(sim_result["vcd_file"])

            iter_data = {
                "iteration": iteration,
                "sim_status": sim_result["status"],
                "duration_s": sim_result["duration_s"],
                "tool": sim_result["tool"],
                "total_lines": mined_diagnostics["total_lines"],
                "total_errors": mined_diagnostics["total_errors"],
                "mined_templates": mined_diagnostics["unique_root_causes"],
                "clusters": mined_diagnostics["clusters"],
                "vcd_attached": bool(vcd_info and "signal_transitions" in vcd_info),
            }
            iteration_records.append(iter_data)

            # Check termination: If status is COMPLETED / PASS with 0 hard errors
            if sim_result["status"] == "COMPLETED" and mined_diagnostics.get("hard_errors_count", 0) == 0:
                all_passed = True
                break

            # If simulation failed and a patch callback was provided, invoke it
            if patch_callback:
                context = {
                    "iteration": iteration,
                    "files": files,
                    "top_module": top_module,
                    "sim_result": sim_result,
                    "mined_diagnostics": mined_diagnostics,
                    "vcd_info": vcd_info,
                }
                patched = patch_callback(context)
                if not patched:
                    logger.warning("Patch callback returned False; stopping loop.")
                    break
            else:
                # No automated patch callback; break loop and return diagnostics for Hermes
                break

        total_loop_time = round(time.time() - loop_start, 2)
        summary = {
            "converged": all_passed,
            "total_iterations": iteration,
            "max_iterations": max_iterations,
            "total_duration_s": total_loop_time,
            "final_status": "PASSED" if all_passed else "FAILED",
            "iterations": iteration_records,
            "last_diagnostics": mined_diagnostics if iteration_records else {},
            "vcd_inspected": bool(vcd_info),
        }
        self.history.append(summary)
        return summary

    def build_llm_diagnosis_prompt(self, context: Dict[str, Any]) -> str:
        """Construct an empirical reasoning prompt for the LLM agent to diagnose failures."""
        top_module = context.get("top_module", "unknown")
        files = context.get("files", [])
        sim_result = context.get("sim_result", {})
        mined = context.get("mined_diagnostics", {})
        vcd_info = context.get("vcd_info", {})
        iteration = context.get("iteration", 1)

        lines = [
            f"# EDA Verification Failure Report (Iteration {iteration})",
            f"**Target Top Module:** `{top_module}`",
            f"**Simulation Tool:** `{sim_result.get('tool')}`",
            f"**Status:** `{sim_result.get('status')}` (Exit Code: {sim_result.get('returncode')})",
            "",
            "## 1. Mined Failure Root Causes (Drain3 Template Mining)",
            f"Total Error Events: {mined.get('total_errors', 0)} | Unique Root-Cause Clusters: {mined.get('unique_root_causes', 0)}",
        ]

        for cl in mined.get("clusters", [])[:10]:
            lines.append(f"- **Template [x{cl.get('count', 1)}]:** `{cl.get('signature', '')}`")
            if cl.get("example") and cl.get("example") != cl.get("signature"):
                lines.append(f"  *Example:* `{cl.get('example')}`")

        if vcd_info and "signal_transitions" in vcd_info:
            lines.extend([
                "",
                "## 2. VCD Waveform Transitions Around Failure",
                f"Total Signals Captured: {vcd_info.get('total_signals', 0)} | Timescale: {vcd_info.get('timescale', '1ps')}",
            ])
            for sig, trans in list(vcd_info.get("signal_transitions", {}).items())[:8]:
                recent = trans[-5:] if len(trans) > 5 else trans
                trans_str = ", ".join([f"t={t}ns: {v}" for t, v in recent])
                lines.append(f"- Signal `{sig}`: [{trans_str}]")

        lines.extend([
            "",
            "## 3. RTL Source Files",
        ])
        for f in files:
            p = Path(f)
            if not p.is_absolute():
                p = self.work_dir / f
            if p.exists():
                code = p.read_text(encoding="utf-8", errors="replace")
                lines.append(f"### File `{f}`:\n```systemverilog\n{code}\n```\n")

        lines.extend([
            "## 4. Your Autonomous Objective",
            "1. **Reason step-by-step:** Analyze the root cause using the mined failure signature and waveform transitions.",
            "2. **Patch the RTL / Testbench:** Use `patch` or `write_file` to apply the corrected Verilog/SystemVerilog code.",
            "3. **Verify:** Use `eda_simulate` or re-run the verification step to ensure 0 errors.",
            "4. **Learn:** If you discover a reusable hardware pattern or verification quirk, save it using `memory`.",
        ])
        return "\n".join(lines)

    def run_ai_moderated_loop(
        self,
        agent: Any,
        files: List[str],
        top_module: str,
        tb_type: str = "cpp",
        cpp_files: Optional[List[str]] = None,
        cocotb_dir: Optional[str] = None,
        extra_flags: Optional[List[str]] = None,
        max_iterations: int = 5,
        memory_persist: bool = True,
    ) -> Dict[str, Any]:
        """Run an autonomous AI-driven verification loop powered by Hermes LLM reasoning."""
        def ai_patch_callback(context: Dict[str, Any]) -> bool:
            prompt = self.build_llm_diagnosis_prompt(context)
            logger.info("Sending empirical EDA diagnostic prompt to Hermes Agent...")
            try:
                response = agent.chat(prompt)
                logger.info("Hermes Agent responded to diagnostic prompt: %s", str(response)[:200])
                return True
            except Exception as e:
                logger.error("Error during AI agent reasoning turn: %s", e)
                return False

        result = self.run_moderated_loop(
            files=files,
            top_module=top_module,
            tb_type=tb_type,
            cpp_files=cpp_files,
            cocotb_dir=cocotb_dir,
            extra_flags=extra_flags,
            max_iterations=max_iterations,
            patch_callback=ai_patch_callback,
        )

        if result.get("converged") and memory_persist:
            try:
                learn_prompt = (
                    f"The EDA verification loop for `{top_module}` converged successfully in {result.get('total_iterations')} iterations. "
                    "If you learned any durable hardware design rule, bug pattern, or tool convention during this session, "
                    "save it to persistent memory using `memory(action='set', ...)`."
                )
                agent.chat(learn_prompt)
            except Exception as e:
                logger.debug("Failed to prompt memory learning: %s", e)

        return result

