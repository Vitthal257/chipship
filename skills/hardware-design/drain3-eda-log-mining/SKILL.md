---
name: drain3-eda-log-mining
description: Mine failure templates from large EDA simulation logs.
version: 0.1.0
author: ChipShip Maintainers (chipship), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [drain3, log-mining, clustering, eda, diagnostics]
    related_skills: [eda-verification-loop, verilator-edalize-simulation, vcd-waveform-analysis]
---

# Drain3 EDA Log Template Mining Skill

Extracts failure signatures and groups repetitive error logs using Drain3 log template mining. Compresses multi-megabyte simulation and regression traces into concise root-cause clusters to preserve Hermes context window tokens.

## When to Use

- Analyzing long simulation logs containing hundreds or thousands of error messages
- Isolating distinct root causes from repetitive failure cascades
- Compressing raw log output before feeding diagnostics to Hermes reasoning loops
- Don't use for: simple one-line compiler errors with no log file

## Prerequisites

- `drain3` Python package installed
- Simulation log file (`.log`, `.txt`) produced by Verilator, Edalize, or VCS

## How to Run

Analyze and cluster any EDA log file via `terminal`:

```bash
terminal(command="chipship analyze test_corpus/alu_module/.eda_jobs/failing_run.log", timeout=60)
```

Programmatic extraction in Python:

```python
from eda_agent.context_engine import cluster_eda_log_with_drain3
clusters = cluster_eda_log_with_drain3(raw_log_text)
```

## Quick Reference

| Action | Command Pattern |
|---|---|
| Analyze Log File | `chipship analyze <path_to_log>` |
| Compress Large Log | Handled automatically by `EdaLogContextEngine` |
| View Extracted Clusters | Displayed in Drain3 template summary table |

## Procedure

1. **Locate Target Log File:**
   Identify the log file path returned by a previous simulation or regression step.

2. **Run Drain3 Mining:**
   Execute `terminal(command="chipship analyze <log_file>")`.

3. **Examine Root Cause Clusters:**
   Inspect the mined template signatures table. Check occurrence counts and representative examples for each unique failure category.

4. **Map to Source Files:**
   Identify referenced file names and line numbers in the mined templates (e.g. `alu.sv:26`) to locate the bug in source code.

## Pitfalls

- **Context Window Overload:** Never read an uncompressed multi-megabyte log file with `read_file`. Always run `chipship analyze` first.
- **Log Noise:** Drain3 filters out routine informational trace lines and focuses specifically on error, warning, fatal, and assertion events.

## Verification

1. Run `terminal(command="chipship analyze test_corpus/alu_module/.eda_jobs/verilator-39621e62.log")` (or any available failing log).
2. Confirm output displays `Drain3 Mining Report` and `Extracted Failure Log Templates`.
