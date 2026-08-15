"""Verilator Tool Adapter implementation.

Wraps Verilator compilation & simulation regressions with non-blocking async
execution handles, failure log parsing, and failure clustering.
"""

import os
import re
import sys
import time
import uuid
import json
import subprocess
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from eda_agent.adapter import EdaToolAdapter
from eda_agent.context_engine import cluster_eda_log_lines

logger = logging.getLogger(__name__)

# Active background jobs registry
_JOBS_STORE: Dict[str, Dict[str, Any]] = {}


class VerilatorToolAdapter(EdaToolAdapter):
    """Adapter wrapping Verilator simulator & regression runner."""

    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = Path(work_dir or os.getcwd()).resolve()
        self.jobs_dir = self.work_dir / ".eda_jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def capabilities(self) -> Dict[str, Any]:
        return {
            "name": "verilator",
            "tool_type": "simulator",
            "supports_async": True,
            "default_timeout_s": 300.0,
            "verilator_binary": os.environ.get("VERILATOR_BIN", "verilator"),
        }

    def _save_job_metadata(self, job_meta: Dict[str, Any]) -> None:
        job_id = job_meta["job_id"]
        meta_file = self.jobs_dir / f"{job_id}.json"
        serializable = {
            "job_id": job_meta["job_id"],
            "pid": job_meta.get("pid"),
            "log_file": str(job_meta["log_file"]),
            "exe_dir": str(job_meta["exe_dir"]),
            "top_module": job_meta["top_module"],
            "start_time": job_meta["start_time"],
            "status": job_meta.get("status", "RUNNING"),
            "cmd": job_meta.get("cmd", ""),
            "timeout_s": job_meta.get("timeout_s", 300.0),
        }
        meta_file.write_text(json.dumps(serializable, indent=2))

    def _load_job_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        meta_file = self.jobs_dir / f"{job_id}.json"
        if not meta_file.exists():
            return None
        try:
            return json.loads(meta_file.read_text())
        except Exception:
            return None

    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Verilator compile & sim."""
        files = params.get("files", [])
        top_module = params.get("top_module", "top")
        mode = params.get("mode", "async")
        cpp_files = params.get("cpp_files", [])
        extra_flags = params.get("extra_flags", ["-Wall"])
        timeout_s = float(params.get("timeout_s", 300.0))

        if not files:
            return {
                "status": "FAILED",
                "error": "No RTL source files provided to Verilator adapter.",
            }

        job_id = f"verilator-{uuid.uuid4().hex[:8]}"
        log_file = self.jobs_dir / f"{job_id}.log"
        exe_dir = self.jobs_dir / f"{job_id}_obj_dir"

        # Resolve verilator path
        verilator_bin = os.environ.get("VERILATOR_BIN")
        if not verilator_bin:
            conda_verilator = Path("/home/virtual/miniconda3/bin/verilator")
            if conda_verilator.exists():
                verilator_bin = str(conda_verilator)
            else:
                verilator_bin = "verilator"

        cmd = [
            verilator_bin,
            "--cc",
            "--exe",
            "--build",
            "-j", "4",
            "--Mdir", str(exe_dir),
            "--top-module", top_module,
        ] + extra_flags + files + cpp_files

        env = dict(os.environ)
        env["PATH"] = f"/home/virtual/miniconda3/bin:{env.get('PATH', '')}"
        env["AR"] = "/usr/bin/ar"
        env["CXX"] = "/usr/bin/g++"
        env["CC"] = "/usr/bin/gcc"

        start_time = time.time()

        if mode == "sync":
            try:
                res = subprocess.run(
                    cmd,
                    cwd=str(self.work_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=timeout_s,
                    env=env,
                )
                output = res.stdout
                log_file.write_text(output)
                
                exe_path = exe_dir / f"V{top_module}"
                if res.returncode == 0 and exe_path.exists():
                    sim_res = subprocess.run(
                        [str(exe_path)],
                        cwd=str(self.work_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        timeout=timeout_s,
                    )
                    output += f"\n--- SIMULATION OUTPUT ---\n{sim_res.stdout}"
                    log_file.write_text(output)

                parsed = self.parse_output(output)
                status = "COMPLETED" if (res.returncode == 0 and parsed["success"]) else "FAILED"

                return {
                    "status": status,
                    "job_id": job_id,
                    "returncode": res.returncode,
                    "log_file": str(log_file),
                    "duration_s": round(time.time() - start_time, 2),
                    "parsed_results": parsed,
                }
            except subprocess.TimeoutExpired:
                return {
                    "status": "TIMEOUT",
                    "job_id": job_id,
                    "log_file": str(log_file),
                    "error": f"Verilator execution timed out after {timeout_s}s",
                }

        # Non-blocking async execution pattern
        exe_path = exe_dir / f"V{top_module}"
        compile_cmd_str = " ".join([f"'{arg}'" if " " in arg else arg for arg in cmd])
        full_cmd_str = f"{compile_cmd_str} && '{exe_path}'"

        log_f = open(log_file, "w")
        proc = subprocess.Popen(
            full_cmd_str,
            shell=True,
            cwd=str(self.work_dir),
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )

        job_info = {
            "job_id": job_id,
            "pid": proc.pid,
            "proc": proc,
            "log_f": log_f,
            "log_file": str(log_file),
            "exe_dir": str(exe_dir),
            "top_module": top_module,
            "start_time": start_time,
            "status": "RUNNING",
            "cmd": full_cmd_str,
            "timeout_s": timeout_s,
        }
        _JOBS_STORE[job_id] = job_info
        self._save_job_metadata(job_info)

        return {
            "status": "RUNNING",
            "job_id": job_id,
            "pid": proc.pid,
            "log_file": str(log_file),
            "message": f"Verilator job {job_id} launched asynchronously in background.",
        }

    def check_job_status(self, job_id: str) -> Dict[str, Any]:
        """Check status of a running background Verilator job (process & disk-persisted)."""
        job = _JOBS_STORE.get(job_id)
        if not job:
            job = self._load_job_metadata(job_id)

        if not job:
            return {"status": "UNKNOWN", "error": f"Job ID {job_id} not found."}

        pid = job.get("pid")
        log_file = Path(job["log_file"])
        start_time = job.get("start_time", time.time())
        timeout_s = job.get("timeout_s", 300.0)

        # Check process status
        is_running = False
        proc = job.get("proc")
        if proc is not None:
            poll_ret = proc.poll()
            is_running = (poll_ret is None)
        elif pid:
            try:
                # Check if process is still alive and not a zombie
                try:
                    wpid, _ = os.waitpid(pid, os.WNOHANG)
                    if wpid != 0:
                        is_running = False
                    else:
                        is_running = True
                except ChildProcessError:
                    # Not a child of current process, check via kill(pid, 0) and /proc
                    os.kill(pid, 0)
                    proc_stat = Path(f"/proc/{pid}/status")
                    if proc_stat.exists() and "State:\tZ" in proc_stat.read_text():
                        is_running = False
                    else:
                        is_running = True
            except OSError:
                is_running = False

        elapsed = round(time.time() - start_time, 2)

        if is_running:
            if elapsed > timeout_s:
                try:
                    os.kill(pid, 9)
                except OSError:
                    pass
                job["status"] = "TIMEOUT"
                self._save_job_metadata(job)
                return {
                    "status": "TIMEOUT",
                    "job_id": job_id,
                    "elapsed_s": elapsed,
                    "log_file": str(log_file),
                }

            log_bytes = log_file.stat().st_size if log_file.exists() else 0
            return {
                "status": "RUNNING",
                "job_id": job_id,
                "pid": pid,
                "elapsed_s": elapsed,
                "log_bytes": log_bytes,
                "log_file": str(log_file),
            }

        # Finished
        output = log_file.read_text() if log_file.exists() else ""
        parsed = self.parse_output(output)
        final_status = "COMPLETED" if parsed["success"] else "FAILED"
        job["status"] = final_status
        self._save_job_metadata(job)

        return {
            "status": final_status,
            "job_id": job_id,
            "duration_s": elapsed,
            "log_file": str(log_file),
            "parsed_results": parsed,
        }

    def parse_output(self, raw_output: str) -> Dict[str, Any]:
        """Parse Verilator compile & simulation output."""
        clustered = cluster_eda_log_lines(raw_output)
        
        has_verilator_error = "%Error" in raw_output
        has_sim_fatal = "$fatal" in raw_output or "Assertion failed" in raw_output
        has_fail_marker = "TEST FAILED" in raw_output or "FAILURE" in raw_output
        
        success = not (has_verilator_error or has_sim_fatal or has_fail_marker)

        return {
            "success": success,
            "total_lines": clustered.get("total_lines", 0),
            "error_count": clustered.get("total_errors", 0),
            "warning_count": clustered.get("total_warnings", 0),
            "failure_clusters": clustered.get("clusters", []),
            "key_snippets": [cl["example"] for cl in clustered.get("clusters", [])],
        }
