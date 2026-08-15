"""SQLite-backed Background Job Queue powered by Huey.

Provides lightweight, zero-external-dependency task execution, background worker handling,
and status polling out of the box for EDA tool regressions.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from huey import SqliteHuey

logger = logging.getLogger(__name__)

# Initialize SQLite-backed Huey queue
DB_PATH = Path(os.getcwd()) / ".chipship_jobs.db"
huey = SqliteHuey(filename=str(DB_PATH))


@huey.task()
def run_eda_simulation_task(params: Dict[str, Any], work_dir: str) -> Dict[str, Any]:
    """Huey background task wrapper executing Verilator/Edalize regressions."""
    from eda_agent.verilator_adapter import VerilatorToolAdapter

    adapter = VerilatorToolAdapter(work_dir=work_dir)
    params["mode"] = "sync"  # Huey task worker runs sync execution internally
    start_time = time.time()
    
    res = adapter.invoke(params)
    res["duration_s"] = round(time.time() - start_time, 2)
    return res


class HueyJobManager:
    """Manager for submitting and querying Huey EDA background tasks."""

    def __init__(self, work_dir: Optional[str] = None):
        self.work_dir = str(Path(work_dir or os.getcwd()).resolve())

    def submit_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit background EDA job to Huey queue."""
        task_handle = run_eda_simulation_task(params, self.work_dir)
        return {
            "status": "RUNNING",
            "job_id": task_handle.id,
            "queue_backend": "huey_sqlite",
            "message": f"EDA job {task_handle.id} queued successfully in Huey.",
        }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Query status and result of a Huey background EDA job."""
        task_result = huey.result(job_id, preserve=True)

        if task_result is None:
            # Check if task is pending execution
            if huey.is_revoked(job_id):
                return {"status": "CANCELLED", "job_id": job_id}
            return {
                "status": "RUNNING",
                "job_id": job_id,
                "message": "Job is running in background Huey queue...",
            }

        # Task finished
        if isinstance(task_result, Exception):
            return {
                "status": "FAILED",
                "job_id": job_id,
                "error": str(task_result),
            }

        if isinstance(task_result, dict):
            task_result["job_id"] = job_id
            return task_result

        return {
            "status": "COMPLETED",
            "job_id": job_id,
            "result": task_result,
        }
