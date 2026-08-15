"""VCD Waveform Parser and Signal Inspection Subsystem.

Enables ChipShip to inspect VCD waveform transitions, signal values, and clock edge
alignments around simulation failure timestamps or assertion triggers.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from vcdvcd import VCDVCD

logger = logging.getLogger(__name__)


def inspect_vcd_waveform(
    vcd_path: str,
    signals: Optional[List[str]] = None,
    time_window: Optional[Tuple[int, int]] = None,
    max_changes: int = 50,
) -> Dict[str, Any]:
    """Parse VCD file and extract signal value transitions."""
    path = Path(vcd_path).resolve()
    if not path.exists():
        return {"error": f"VCD waveform file '{vcd_path}' not found."}

    try:
        vcd = VCDVCD(str(path))
        all_signals = list(vcd.references_to_ids.keys())

        if signals:
            # Match requested signals by exact name or substring match
            selected_signals = []
            for s in signals:
                matches = [sig for sig in all_signals if s.lower() in sig.lower()]
                selected_signals.extend(matches if matches else [s])
        else:
            selected_signals = all_signals[:10]

        signal_data: Dict[str, List[Dict[str, Any]]] = {}

        for sig_name in selected_signals:
            if sig_name in vcd.references_to_ids:
                sig_obj = vcd[sig_name]
                tv_list = []
                for tv in sig_obj.tv:
                    t_val = int(tv[0])
                    s_val = str(tv[1])
                    if time_window:
                        if time_window[0] <= t_val <= time_window[1]:
                            tv_list.append({"time": t_val, "value": s_val})
                    else:
                        tv_list.append({"time": t_val, "value": s_val})
                signal_data[sig_name] = tv_list[:max_changes]

        begintime = getattr(vcd, "begintime", 0)
        endtime = getattr(vcd, "endtime", 0)

        return {
            "vcd_file": str(path),
            "total_signals": len(all_signals),
            "inspected_signals": list(signal_data.keys()),
            "time_range": [begintime, endtime],
            "signal_transitions": signal_data,
        }
    except Exception as exc:
        logger.exception("VCD parsing exception")
        return {"error": f"Failed to parse VCD waveform '{vcd_path}': {str(exc)}"}
