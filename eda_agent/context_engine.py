"""EDA-specific Context Engine Plugin powered by Drain3 (LogPAI Template Mining).

Replaces hand-rolled regexes with Drain3 log-template mining to extract log templates,
group failure signatures, and compress multi-megabyte simulation logs into high-density summaries.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

from agent.context_engine import ContextEngine

logger = logging.getLogger(__name__)


def cluster_eda_log_with_drain3(raw_text: str, max_clusters: int = 20) -> Dict[str, Any]:
    """Mine log templates and cluster failure signatures using Drain3."""
    config = TemplateMinerConfig()
    config.profiling_enabled = False
    template_miner = TemplateMiner(config=config)

    lines = raw_text.splitlines()
    total_lines = len(lines)
    error_lines = []
    hard_errors_count = 0
    warnings_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Filter log lines containing true EDA errors, warnings, fatals, or assertions
        # Avoid false positives on compiler invocations containing filenames like 'failing_tb.cpp'
        if ("/bin/" in stripped or stripped.startswith(("python", "rm ", "make:", "make["))) and not ("%Error" in stripped or "%Fatal" in stripped or ": error:" in stripped):
            continue

        lower = stripped.lower()
        
        # Exclude purely informational or passing summary lines
        if re.search(r'\b(info|fail=0|0 failures?)\b', lower) and not ("%error" in lower or "%fatal" in lower):
            continue

        is_hard_error = bool(
            re.search(r'(%(?:error|fatal)|\b(?:error|fatal|\$fatal|\$stop|\$error)\b|assert(?:ion)?.*failed|test\s+failed|fail=[1-9])', lower)
        )
        is_warning = bool(
            re.search(r'(%(?:warning)|\b(?:warning|deprecationwarning)\b)', lower)
        )

        if is_hard_error or is_warning:
            if is_hard_error:
                hard_errors_count += 1
            elif is_warning:
                warnings_count += 1
            error_lines.append(stripped)
            template_miner.add_log_message(stripped)

    drain_clusters = template_miner.drain.clusters
    sorted_clusters = sorted(drain_clusters, key=lambda c: c.size, reverse=True)

    result_clusters = []
    for c in sorted_clusters[:max_clusters]:
        result_clusters.append({
            "cluster_id": c.cluster_id,
            "signature": c.get_template(),
            "count": c.size,
            "example": c.get_template(),
            "full_snippet": c.get_template(),
        })

    return {
        "total_lines": total_lines,
        "total_errors": len(error_lines),
        "hard_errors_count": hard_errors_count,
        "warnings_count": warnings_count,
        "unique_root_causes": len(sorted_clusters),
        "clusters": result_clusters,
    }


# Backward compatibility aliases
cluster_eda_log_lines = cluster_eda_log_with_drain3
parse_eda_error_blocks = cluster_eda_log_with_drain3


class EdaLogContextEngine(ContextEngine):
    """Context Engine powered by Drain3 log template mining."""

    def __init__(self, log_threshold_chars: int = 2500):
        self._name = "eda_compressor"
        self.log_threshold_chars = log_threshold_chars
        self.last_prompt_tokens = 0
        self.last_completion_tokens = 0
        self.last_total_tokens = 0
        self.threshold_tokens = 100000
        self.context_length = 128000
        self.compression_count = 0

    @property
    def name(self) -> str:
        return self._name

    def update_from_response(self, usage: Dict[str, Any]) -> None:
        self.last_prompt_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
        self.last_completion_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
        self.last_total_tokens = usage.get("total_tokens", self.last_prompt_tokens + self.last_completion_tokens)

    def should_compress(self, prompt_tokens: int = None) -> bool:
        tokens = prompt_tokens or self.last_prompt_tokens
        return tokens > self.threshold_tokens

    def compress(
        self,
        messages: List[Dict[str, Any]],
        current_tokens: Optional[int] = None,
        focus_topic: Optional[str] = None,
        force: bool = False,
        memory_context: str = "",
    ) -> List[Dict[str, Any]]:
        self.compression_count += 1
        pruned_messages, _ = self.prune_tool_results_only(messages)
        return pruned_messages

    def prune_tool_results_only(
        self,
        messages: List[Dict[str, Any]],
        current_tokens: int | None = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Intercept and compress large EDA tool output messages using Drain3."""
        pruned = 0
        new_messages = []

        for msg in messages:
            if msg.get("role") == "tool" and isinstance(msg.get("content"), str):
                content = msg["content"]
                if len(content) > self.log_threshold_chars:
                    parsed = cluster_eda_log_with_drain3(content)
                    
                    cluster_lines = []
                    for cl in parsed["clusters"]:
                        cluster_lines.append(
                            f"  - [{cl['count']}x] Template: {cl['signature']}"
                        )

                    summary_parts = [
                        "[EDA LOG SUMMARY — Compressed by EdaLogContextEngine (Drain3 Mined)]",
                        f"Raw Size: {len(content):,} chars | Total Lines: {parsed['total_lines']:,}",
                        f"Total Log Events: {parsed['total_errors']:,} | Drain3 Mined Templates: {parsed['unique_root_causes']}",
                    ]
                    if cluster_lines:
                        summary_parts.append("Mined Failure Templates:")
                        summary_parts.extend(cluster_lines)
                    else:
                        head = content[:800]
                        tail = content[-800:]
                        summary_parts.append(f"Log Head:\n{head}\n...\nLog Tail:\n{tail}")

                    compressed_content = "\n".join(summary_parts)
                    new_msg = dict(msg)
                    new_msg["content"] = compressed_content
                    new_messages.append(new_msg)
                    pruned += 1
                    continue

            new_messages.append(msg)

        return new_messages, pruned
