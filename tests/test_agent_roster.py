from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.agent_roster import CLI_CAPTAINS, CONTRACT_FILENAME, ROLES


ROOT = Path(__file__).resolve().parents[1]


class AgentRosterTests(unittest.TestCase):
    def test_every_role_has_a_contract_that_names_its_load_path(self) -> None:
        for role_id, load_path in ROLES:
            contract = ROOT / "agents" / role_id / CONTRACT_FILENAME
            self.assertTrue(contract.is_file(), f"missing {contract}")
            text = contract.read_text(encoding="utf-8")
            self.assertIn(role_id, text)
            self.assertIn(load_path, text)
            self.assertTrue((ROOT / load_path).is_file(), f"{role_id} load path missing: {load_path}")

    def test_harness_map_points_at_contracts_not_copies(self) -> None:
        harness = json.loads((ROOT / ".agent-harness.json").read_text(encoding="utf-8"))
        self.assertEqual(harness["name"], "music-producer-os")
        self.assertEqual(harness["roles"], [role_id for role_id, _path in ROLES])
        self.assertIn(f"agents/<id>/{CONTRACT_FILENAME}", harness["source_of_truth"])
        self.assertTrue(harness["gateway"]["music_producer_stopped"])

    def test_claude_adapter_is_captains_only(self) -> None:
        captains = {path.stem for path in (ROOT / ".claude" / "agents").glob("*.md")}
        self.assertEqual(captains, set(CLI_CAPTAINS))
        self.assertIn("producer-orchestrator", captains)
        self.assertLessEqual(len(captains), 4)


if __name__ == "__main__":
    unittest.main()
