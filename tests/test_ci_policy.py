from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deterministic-verification.yml"


class CiPolicyTests(unittest.TestCase):
    def test_workflow_is_deterministic_and_has_no_live_generation_path(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertNotIn("pull_request_target", lowered)
        self.assertNotIn("suno", lowered)
        self.assertNotIn("computer-use", lowered)
        self.assertNotIn("install_machine.py", lowered)
        self.assertNotIn("secrets.", lowered)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("python -m unittest discover -s tests -v", text)
        self.assertIn('python-version: "3.11.9"', text)
        self.assertNotIn("cache:", lowered)

        uses = re.findall(r"^\s*uses:\s+([^\s#]+)", text, flags=re.MULTILINE)
        self.assertTrue(uses)
        for action in uses:
            with self.subTest(action=action):
                self.assertRegex(action, r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
