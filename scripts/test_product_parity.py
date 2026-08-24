#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"cowork-commit", "cowork-doc-init", "cowork-doc-sync", "cowork-insights", "cowork-sprint", "pdca-wf"}

skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
assert skills == EXPECTED, f"skill parity drift: {skills ^ EXPECTED}"

claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
legacy = json.loads((ROOT / "manifest.json").read_text())
assert {claude["name"], codex["name"], legacy["name"]} == {"ai-native-cowork"}
assert len({claude["version"], codex["version"], legacy["version"]}) == 1
assert codex["skills"] == "./skills/"

for name in EXPECTED:
    text = (ROOT / "skills" / name / "SKILL.md").read_text()
    assert text.startswith("---\n"), f"missing frontmatter: {name}"

print("six-skill and manifest parity passed")
