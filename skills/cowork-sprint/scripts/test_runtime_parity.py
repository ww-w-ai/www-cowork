#!/usr/bin/env python3
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RuntimeParityTests(unittest.TestCase):
    def test_entrypoint_routes_both_hosts(self):
        text = (ROOT / "SKILL.md").read_text()
        for token in ("runtime-claude-code.md", "runtime-codex.md", "ambiguous", "unsupported"):
            self.assertIn(token, text)

    def test_host_cluster_contract_matches(self):
        contracts = []
        for name in ("runtime-claude-code.md", "runtime-codex.md"):
            text = (ROOT / "references" / name).read_text()
            for token in ("cowork-method.md", "schedule.py", "first unfinished cluster", "integrationOrder", "state helper", "commit", "blocked or failed"):
                self.assertIn(token, text)
            self.assertIn("never edit state", text)
            match = re.search(r"cluster-contract (\{.*?\}) -->", text)
            self.assertIsNotNone(match)
            contracts.append(json.loads(match.group(1)))
        self.assertEqual(contracts[0], contracts[1])
        self.assertEqual({"admission", "barrier", "failure", "integration", "stateOwner"}, set(contracts[0]))

if __name__ == "__main__":
    unittest.main()
