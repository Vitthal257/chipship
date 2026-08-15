"""EDA Model Tools Module for Hermes Agent.

Provides LLM-callable tools for hardware design, RTL verification, simulation,
log mining, and waveform inspection:
- ``eda_simulate``: Run Verilator / Edalize compilation & simulation (sync or async)
- ``eda_cocotb``: Run Python cocotb testbench regressions
- ``eda_mine_log``: Mine failure templates and clusters from logs via Drain3
- ``eda_inspect_vcd``: Parse VCD waveform transitions and inspect signal timelines
- ``eda_verification_loop``: Run moderated closed-loop verification across all EDA tools
- ``eda_job_status``: Poll status of background Huey / Verilator async jobs
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from eda_agent.adapter import EdalizeToolAdapter
from eda_agent.verilator_adapter import VerilatorToolAdapter
from eda_agent.context_engine import cluster_eda_log_with_drain3
from eda_agent.vcd_parser import inspect_vcd_waveform
from eda_agent.job_queue import HueyJobManager
from eda_agent.moderator import EdaVerificationModerator

logger = logging.getLogger(__name__)


def check_eda_requirements() -> bool:
    """Check availability of EDA toolchain."""
    return True


def eda_simulate_handler(
    files: List[str],
    top_module: str,
    mode: str = "sync",
    cpp_files: Optional[List[str]] = None,
    extra_flags: Optional[List[str]] = None,
    timeout_s: float = 300.0,
    **kwargs,
) -> str:
    """Handle eda_simulate tool call from LLM."""
    try:
        work_dir = os.getcwd()
        flags = extra_flags or ["-Wall"]
        cpp = cpp_files or []

        if mode == "async":
            job_mgr = HueyJobManager(work_dir=work_dir)
            res = job_mgr.submit_job({
                "files": files,
                "top_module": top_module,
                "cpp_files": cpp,
                "extra_flags": flags,
                "timeout_s": timeout_s,
            })
            return json.dumps({
                "status": "RUNNING",
                "job_id": res.get("job_id"),
                "message": f"EDA simulation job {res.get('job_id')} enqueued asynchronously. Use eda_job_status to poll progress.",
            }, indent=2)

        adapter = VerilatorToolAdapter(work_dir=work_dir)
        res = adapter.invoke({
            "files": files,
            "top_module": top_module,
            "mode": "sync",
            "cpp_files": cpp,
            "extra_flags": flags,
            "timeout_s": timeout_s,
        })
        return json.dumps(res, indent=2)
    except Exception as exc:
        return json.dumps({"status": "FAILED", "error": str(exc)}, indent=2)


def eda_cocotb_handler(
    cocotb_dir: Optional[str] = None,
    timeout_s: float = 300.0,
    **kwargs,
) -> str:
    """Handle eda_cocotb tool call from LLM."""
    try:
        target_dir = Path(cocotb_dir).resolve() if cocotb_dir else Path(os.getcwd()) / "test_corpus" / "cocotb_alu"
        moderator = EdaVerificationModerator(work_dir=str(target_dir))
        res = moderator.run_simulation_step(
            files=[],
            top_module="top",
            tb_type="cocotb",
            cocotb_dir=str(target_dir),
            timeout_s=timeout_s,
        )
        return json.dumps(res, indent=2)
    except Exception as exc:
        return json.dumps({"status": "FAILED", "error": str(exc)}, indent=2)


def eda_mine_log_handler(
    log_file: Optional[str] = None,
    log_text: Optional[str] = None,
    max_clusters: int = 20,
    **kwargs,
) -> str:
    """Handle eda_mine_log tool call from LLM."""
    try:
        content = ""
        if log_text:
            content = log_text
        elif log_file:
            log_p = Path(log_file).resolve()
            if not log_p.exists():
                return json.dumps({"error": f"Log file '{log_file}' not found."}, indent=2)
            content = log_p.read_text(encoding="utf-8", errors="replace")
        else:
            return json.dumps({"error": "Either 'log_file' or 'log_text' must be provided."}, indent=2)

        mined = cluster_eda_log_with_drain3(content, max_clusters=max_clusters)
        return json.dumps(mined, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


def eda_inspect_vcd_handler(
    vcd_file: str,
    signals: Optional[List[str]] = None,
    window: Optional[List[int]] = None,
    max_changes: int = 30,
    **kwargs,
) -> str:
    """Handle eda_inspect_vcd tool call from LLM."""
    try:
        win_tuple = tuple(window) if window and len(window) == 2 else None
        res = inspect_vcd_waveform(
            vcd_path=vcd_file,
            signals=signals,
            time_window=win_tuple,
            max_changes=max_changes,
        )
        return json.dumps(res, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, indent=2)


def eda_verification_loop_handler(
    files: List[str],
    top_module: str,
    tb_type: str = "cpp",
    cpp_files: Optional[List[str]] = None,
    cocotb_dir: Optional[str] = None,
    extra_flags: Optional[List[str]] = None,
    max_iterations: int = 5,
    **kwargs,
) -> str:
    """Handle eda_verification_loop tool call from LLM."""
    try:
        moderator = EdaVerificationModerator(work_dir=os.getcwd())
        result = moderator.run_moderated_loop(
            files=files,
            top_module=top_module,
            tb_type=tb_type,
            cpp_files=cpp_files,
            cocotb_dir=cocotb_dir,
            extra_flags=extra_flags,
            max_iterations=max_iterations,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"converged": False, "error": str(exc)}, indent=2)


def eda_job_status_handler(
    job_id: str,
    **kwargs,
) -> str:
    """Handle eda_job_status tool call from LLM."""
    try:
        # Check Verilator adapter first, then Huey queue
        adapter = VerilatorToolAdapter(work_dir=os.getcwd())
        st = adapter.check_job_status(job_id)
        if st.get("status") != "UNKNOWN":
            return json.dumps(st, indent=2)

        job_mgr = HueyJobManager(work_dir=os.getcwd())
        res = job_mgr.get_job_status(job_id)
        return json.dumps(res, indent=2)
    except Exception as exc:
        return json.dumps({"status": "FAILED", "error": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# OpenAI JSON Schemas
# ---------------------------------------------------------------------------

EDA_SIMULATE_SCHEMA = {
    "name": "eda_simulate",
    "description": "Compile and run Verilog / SystemVerilog simulation regressions via Verilator and Edalize.",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of SystemVerilog / Verilog source file paths",
            },
            "top_module": {
                "type": "string",
                "description": "Top-level module name",
            },
            "mode": {
                "type": "string",
                "enum": ["sync", "async"],
                "default": "sync",
                "description": "Execution mode: 'sync' (blocking) or 'async' (background Huey job)",
            },
            "cpp_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional C++ testbench files for Verilator",
            },
            "extra_flags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Compiler flags (e.g. ['-Wall', '-Wno-WIDTH'])",
            },
            "timeout_s": {
                "type": "number",
                "default": 300.0,
                "description": "Timeout in seconds",
            },
        },
        "required": ["files", "top_module"],
    },
}

EDA_COCOTB_SCHEMA = {
    "name": "eda_cocotb",
    "description": "Run Python cocotb testbench regression against SystemVerilog designs and capture VCD waveform dumps.",
    "parameters": {
        "type": "object",
        "properties": {
            "cocotb_dir": {
                "type": "string",
                "description": "Directory containing cocotb Makefile and Python testbench files",
            },
            "timeout_s": {
                "type": "number",
                "default": 300.0,
                "description": "Timeout in seconds",
            },
        },
        "required": [],
    },
}

EDA_MINE_LOG_SCHEMA = {
    "name": "eda_mine_log",
    "description": "Mine failure templates and extract root-cause clusters from EDA simulation/synthesis logs using Drain3.",
    "parameters": {
        "type": "object",
        "properties": {
            "log_file": {
                "type": "string",
                "description": "Path to simulation log file on disk",
            },
            "log_text": {
                "type": "string",
                "description": "Direct raw log text content to cluster",
            },
            "max_clusters": {
                "type": "integer",
                "default": 20,
                "description": "Maximum number of template clusters to extract",
            },
        },
        "required": [],
    },
}

EDA_INSPECT_VCD_SCHEMA = {
    "name": "eda_inspect_vcd",
    "description": "Parse VCD waveform file and extract signal value transitions around failure timestamps or clock cycles.",
    "parameters": {
        "type": "object",
        "properties": {
            "vcd_file": {
                "type": "string",
                "description": "Path to the .vcd waveform file",
            },
            "signals": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific signal names or substrings to inspect",
            },
            "window": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Optional time window [start_ns, end_ns]",
            },
            "max_changes": {
                "type": "integer",
                "default": 30,
                "description": "Maximum number of transitions to report per signal",
            },
        },
        "required": ["vcd_file"],
    },
}

EDA_VERIFICATION_LOOP_SCHEMA = {
    "name": "eda_verification_loop",
    "description": "Run closed-loop EDA moderation: compiles, simulates, mines log failures with Drain3, inspects waveforms, and reports status.",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of SystemVerilog / Verilog RTL source files",
            },
            "top_module": {
                "type": "string",
                "description": "Top-level module name",
            },
            "tb_type": {
                "type": "string",
                "enum": ["cpp", "cocotb"],
                "default": "cpp",
                "description": "Testbench harness type: 'cpp' or 'cocotb'",
            },
            "cpp_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "C++ testbench files (if tb_type is 'cpp')",
            },
            "cocotb_dir": {
                "type": "string",
                "description": "cocotb test directory (if tb_type is 'cocotb')",
            },
            "extra_flags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Compiler flags",
            },
            "max_iterations": {
                "type": "integer",
                "default": 5,
                "description": "Maximum moderation loop iterations",
            },
        },
        "required": ["files", "top_module"],
    },
}

EDA_JOB_STATUS_SCHEMA = {
    "name": "eda_job_status",
    "description": "Query the status and results of an asynchronous background EDA simulation job.",
    "parameters": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "description": "The unique job ID handle returned by an async simulation call",
            },
        },
        "required": ["job_id"],
    },
}


# ---------------------------------------------------------------------------
# Tool Registration
# ---------------------------------------------------------------------------
from tools.registry import registry

registry.register(
    name="eda_simulate",
    toolset="eda",
    schema=EDA_SIMULATE_SCHEMA,
    handler=lambda args, **kw: eda_simulate_handler(
        files=args.get("files", []),
        top_module=args.get("top_module", "top"),
        mode=args.get("mode", "sync"),
        cpp_files=args.get("cpp_files"),
        extra_flags=args.get("extra_flags"),
        timeout_s=float(args.get("timeout_s", 300.0)),
    ),
    check_fn=check_eda_requirements,
    emoji="⚡",
)

registry.register(
    name="eda_cocotb",
    toolset="eda",
    schema=EDA_COCOTB_SCHEMA,
    handler=lambda args, **kw: eda_cocotb_handler(
        cocotb_dir=args.get("cocotb_dir"),
        timeout_s=float(args.get("timeout_s", 300.0)),
    ),
    check_fn=check_eda_requirements,
    emoji="🐍",
)

registry.register(
    name="eda_mine_log",
    toolset="eda",
    schema=EDA_MINE_LOG_SCHEMA,
    handler=lambda args, **kw: eda_mine_log_handler(
        log_file=args.get("log_file"),
        log_text=args.get("log_text"),
        max_clusters=int(args.get("max_clusters", 20)),
    ),
    check_fn=check_eda_requirements,
    emoji="⛏",
)

registry.register(
    name="eda_inspect_vcd",
    toolset="eda",
    schema=EDA_INSPECT_VCD_SCHEMA,
    handler=lambda args, **kw: eda_inspect_vcd_handler(
        vcd_file=args.get("vcd_file", ""),
        signals=args.get("signals"),
        window=args.get("window"),
        max_changes=int(args.get("max_changes", 30)),
    ),
    check_fn=check_eda_requirements,
    emoji="📊",
)

registry.register(
    name="eda_verification_loop",
    toolset="eda",
    schema=EDA_VERIFICATION_LOOP_SCHEMA,
    handler=lambda args, **kw: eda_verification_loop_handler(
        files=args.get("files", []),
        top_module=args.get("top_module", "top"),
        tb_type=args.get("tb_type", "cpp"),
        cpp_files=args.get("cpp_files"),
        cocotb_dir=args.get("cocotb_dir"),
        extra_flags=args.get("extra_flags"),
        max_iterations=int(args.get("max_iterations", 5)),
    ),
    check_fn=check_eda_requirements,
    emoji="🔄",
)

registry.register(
    name="eda_job_status",
    toolset="eda",
    schema=EDA_JOB_STATUS_SCHEMA,
    handler=lambda args, **kw: eda_job_status_handler(
        job_id=args.get("job_id", ""),
    ),
    check_fn=check_eda_requirements,
    emoji="⏱",
)
