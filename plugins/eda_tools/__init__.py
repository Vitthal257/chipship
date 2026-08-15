"""Hermes Plugin for EDA Tools, Edalize, Drain3, and VCD Waveform Inspection."""

import json
import logging
from eda_agent.context_engine import EdaLogContextEngine
from eda_agent.verilator_adapter import VerilatorToolAdapter
from eda_agent.vcd_parser import inspect_vcd_waveform

logger = logging.getLogger(__name__)

# Global adapter instance for the plugin
adapter = VerilatorToolAdapter()


def register(ctx):
    """Register EDA tools, hooks, and context engine facade into Hermes host context."""
    logger.info("Registering EDA tools and context engine plugin...")

    # 1. Register Context Engine
    engine = EdaLogContextEngine()
    ctx.register_context_engine(engine)

    # 2. Tool Handlers
    def eda_run_sim_handler(files, top_module="top", mode="async", cpp_files=None, extra_flags=None, timeout_s=300.0, **kwargs):
        res = adapter.invoke({
            "files": files,
            "top_module": top_module,
            "mode": mode,
            "cpp_files": cpp_files or [],
            "extra_flags": extra_flags or ["-Wall"],
            "timeout_s": float(timeout_s),
        })
        return json.dumps(res, indent=2)

    def eda_check_status_handler(job_id, **kwargs):
        res = adapter.check_job_status(job_id)
        return json.dumps(res, indent=2)

    def eda_analyze_failures_handler(raw_log="", **kwargs):
        res = adapter.parse_output(raw_log)
        return json.dumps(res, indent=2)

    def eda_inspect_waveform_handler(vcd_path="", signals=None, start_time=None, end_time=None, **kwargs):
        time_window = (int(start_time), int(end_time)) if (start_time is not None and end_time is not None) else None
        res = inspect_vcd_waveform(vcd_path=vcd_path, signals=signals, time_window=time_window)
        return json.dumps(res, indent=2)

    # 3. Register Tools
    ctx.register_tool(
        name="eda_run_sim",
        toolset="eda",
        schema={
            "name": "eda_run_sim",
            "description": "Run Verilator compilation and simulation regressions (supports async background jobs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of Verilog/SystemVerilog source files.",
                    },
                    "top_module": {
                        "type": "string",
                        "description": "Name of top-level RTL module.",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["async", "sync"],
                        "description": "Execution mode: async (non-blocking, returns job_id) or sync.",
                    },
                    "cpp_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional C++ testbench wrapper files.",
                    },
                    "extra_flags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional Verilator flags (e.g. -Wall).",
                    },
                    "timeout_s": {
                        "type": "number",
                        "description": "Timeout limit in seconds.",
                    },
                },
                "required": ["files"],
            },
        },
        handler=eda_run_sim_handler,
    )

    ctx.register_tool(
        name="eda_check_status",
        toolset="eda",
        schema={
            "name": "eda_check_status",
            "description": "Check status and progress of a background EDA job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID returned by eda_run_sim.",
                    },
                },
                "required": ["job_id"],
            },
        },
        handler=eda_check_status_handler,
    )

    ctx.register_tool(
        name="eda_analyze_failures",
        toolset="eda",
        schema={
            "name": "eda_analyze_failures",
            "description": "Parse raw simulation/compilation log text and cluster failure signatures using Drain3.",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_log": {
                        "type": "string",
                        "description": "Raw log text to analyze.",
                    },
                },
                "required": ["raw_log"],
            },
        },
        handler=eda_analyze_failures_handler,
    )

    ctx.register_tool(
        name="eda_inspect_waveform",
        toolset="eda",
        schema={
            "name": "eda_inspect_waveform",
            "description": "Inspect VCD waveform file and extract signal transitions around timestamps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vcd_path": {
                        "type": "string",
                        "description": "Path to VCD waveform dump file.",
                    },
                    "signals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of signal names to inspect (e.g. clk, rst_n, result).",
                    },
                    "start_time": {
                        "type": "number",
                        "description": "Start timestamp window.",
                    },
                    "end_time": {
                        "type": "number",
                        "description": "End timestamp window.",
                    },
                },
                "required": ["vcd_path"],
            },
        },
        handler=eda_inspect_waveform_handler,
    )

    # 4. Register Pre/Post Tool Call Hooks
    def pre_tool_call_hook(function_name, function_args, **kwargs):
        if function_name.startswith("eda_"):
            logger.info("Hook pre_tool_call for %s: args=%s", function_name, function_args)

    def post_tool_call_hook(function_name, function_args, result, **kwargs):
        if function_name.startswith("eda_"):
            logger.info("Hook post_tool_call for %s: completed.", function_name)

    ctx.register_hook("pre_tool_call", pre_tool_call_hook)
    ctx.register_hook("post_tool_call", post_tool_call_hook)
