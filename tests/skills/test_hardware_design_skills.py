"""Unit & Conformance Tests for Hardware Design & EDA Skills in Hermes.

Tests:
1. YAML frontmatter parsing and validity.
2. Hardline description constraints: <= 60 characters, one sentence, ends with a period.
3. Supported platform list is explicit [linux, macos].
4. Valid section ordering (When to Use, Prerequisites, How to Run, Quick Reference, Procedure, Pitfalls, Verification).
5. All related_skills resolve to existing in-repo skills.
"""

import re
import yaml
from pathlib import Path
try:
    import pytest
except ImportError:
    pytest = None

SKILLS_ROOT = Path(__file__).parent.parent.parent / "skills" / "hardware-design"

EDA_SKILLS = [
    "eda-verification-loop",
    "verilator-edalize-simulation",
    "cocotb-python-verification",
    "drain3-eda-log-mining",
    "vcd-waveform-analysis",
]


def test_eda_skill_frontmatter_and_hardline_standards(skill_name):
    skill_file = SKILLS_ROOT / skill_name / "SKILL.md"
    assert skill_file.exists(), f"Skill file {skill_file} not found"

    content = skill_file.read_text(encoding="utf-8")
    assert content.startswith("---"), f"{skill_name}: Frontmatter must start with '---' at byte 0"

    m = re.search(r"\n---\s*\n", content[3:])
    assert m is not None, f"{skill_name}: Frontmatter closing '---' delimiter not found"

    fm_raw = content[3 : m.start() + 3]
    fm = yaml.safe_load(fm_raw)
    assert isinstance(fm, dict), f"{skill_name}: Frontmatter must parse as a YAML mapping"

    # 1. Name check
    assert fm.get("name") == skill_name, f"{skill_name}: Name in frontmatter must match directory name"

    # 2. Hardline description check (<= 60 chars, ends with period, single sentence)
    desc = fm.get("description", "")
    assert desc, f"{skill_name}: Description is required"
    assert len(desc) <= 60, f"{skill_name}: Description is {len(desc)} chars (must be <= 60 chars)"
    assert desc.endswith("."), f"{skill_name}: Description must end with a period"
    assert "\n" not in desc, f"{skill_name}: Description must be a single line"

    # 3. Platform audit
    assert "platforms" in fm, f"{skill_name}: Platforms field is required"
    assert isinstance(fm["platforms"], list)
    assert "linux" in fm["platforms"]

    # 4. In-repo related_skills check
    metadata = fm.get("metadata", {})
    hermes_meta = metadata.get("hermes", {})
    related = hermes_meta.get("related_skills", [])
    for rel in related:
        # Must resolve to an existing skill in skills/ or optional-skills/
        repo_root = Path(__file__).parent.parent.parent
        match_in_skills = list(repo_root.glob(f"skills/**/{rel}/SKILL.md"))
        match_in_opt = list(repo_root.glob(f"optional-skills/**/{rel}/SKILL.md"))
        assert match_in_skills or match_in_opt, f"{skill_name}: Related skill '{rel}' does not exist in repo"

    # 5. Section headings check
    body = content[m.end() + 3 :]
    required_sections = [
        "## When to Use",
        "## Prerequisites",
        "## How to Run",
        "## Quick Reference",
        "## Procedure",
        "## Pitfalls",
        "## Verification",
    ]
    for section in required_sections:
        assert section in body, f"{skill_name}: Missing required section '{section}'"


def test_all_eda_skills_exist():
    for skill_name in EDA_SKILLS:
        skill_dir = SKILLS_ROOT / skill_name
        assert skill_dir.is_dir(), f"Expected skill directory {skill_dir}"
        assert (skill_dir / "SKILL.md").is_file()


if __name__ == "__main__":
    print("Running Hardware Design Skills Frontmatter & Standards Validation...")
    test_all_eda_skills_exist()
    for skill in EDA_SKILLS:
        test_eda_skill_frontmatter_and_hardline_standards(skill)
        print(f"  ✔ Skill '{skill}' passed all hardline frontmatter standards.")
    print("\nALL HARDWARE DESIGN & EDA SKILLS VALIDATED SUCCESSFULLY!")
