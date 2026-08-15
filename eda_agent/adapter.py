"""EDA Tool Adapter Contract powered by Edalize (Open-Hardware Standard).

Wraps Verilator, Icarus, Yosys, GHDL, Vivado, and Questa via Edalize's EDAM metadata abstraction layer.
"""

import os
import sys
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from edalize.edatool import get_edatool

logger = logging.getLogger(__name__)


class EdaToolAdapter(ABC):
    """Abstract contract for Edalize-backed EDA tools."""

    @abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass


class EdalizeToolAdapter(EdaToolAdapter):
    """Edalize-backed EDA tool runner for multi-tool flows."""

    def __init__(self, tool_name: str = "verilator", work_dir: Optional[str] = None):
        self.tool_name = tool_name
        self.work_dir = Path(work_dir or os.getcwd()).resolve()

    def capabilities(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "backend": "edalize",
            "supports_async": True,
            "supported_tools": ["verilator", "icarus", "yosys", "ghdl", "vivado", "questa"],
        }

    def build_edam(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Construct standard EDAM (EDA Metadata) dictionary for Edalize."""
        files = params.get("files", [])
        top_module = params.get("top_module", "top")
        cpp_files = params.get("cpp_files", [])
        extra_flags = params.get("extra_flags", ["-Wall"])

        file_list = []
        for f in files:
            abs_p = str(Path(self.work_dir / f).resolve() if not Path(f).is_absolute() else Path(f))
            file_type = "systemVerilogSource" if abs_p.endswith(".sv") else "verilogSource"
            file_list.append({"name": abs_p, "file_type": file_type})

        for cpp in cpp_files:
            abs_cpp = str(Path(self.work_dir / cpp).resolve() if not Path(cpp).is_absolute() else Path(cpp))
            file_list.append({"name": abs_cpp, "file_type": "cppSource"})

        edam = {
            "name": top_module,
            "toplevel": top_module,
            "files": file_list,
            "tool_options": {
                self.tool_name: {
                    "verilator_options": extra_flags,
                    "make_options": ["-j4"],
                }
            },
        }
        return edam

    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure, build, and run simulation using Edalize."""
        os.environ["PATH"] = f"/home/virtual/miniconda3/bin:{os.environ.get('PATH', '')}"
        os.environ["AR"] = "/usr/bin/ar"
        os.environ["CXX"] = "/usr/bin/g++"
        os.environ["CC"] = "/usr/bin/gcc"

        edam = self.build_edam(params)
        top_module = params.get("top_module", "top")
        build_dir = self.work_dir / ".edalize_build" / top_module
        build_dir.mkdir(parents=True, exist_ok=True)

        tool_class = get_edatool(self.tool_name)
        backend = tool_class(edam=edam, work_root=str(build_dir))

        try:
            backend.configure()
            backend.build()
            backend.run()
            return {
                "status": "COMPLETED",
                "tool": self.tool_name,
                "build_dir": str(build_dir),
                "edam": edam,
            }
        except Exception as exc:
            return {
                "status": "FAILED",
                "tool": self.tool_name,
                "error": str(exc),
                "build_dir": str(build_dir),
            }
