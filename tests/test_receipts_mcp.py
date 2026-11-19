from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.receipts_mcp import call_tool, handle_rpc, list_tools
from scripts.skillpack import FORBIDDEN_MCP_TOOLS


class ReceiptsMcpTests(unittest.TestCase):
    def test_tool_list_covers_receipts_and_omits_unofficial_generate(self) -> None:
        names = {tool["name"] for tool in list_tools()}
        self.assertIn("session_init", names)
        self.assertIn("session_validate", names)
        self.assertIn("album_init", names)
        self.assertIn("catalog_list", names)
        for forbidden in FORBIDDEN_MCP_TOOLS:
            self.assertNotIn(forbidden, names)

    def test_call_refuses_unofficial_suno_generate(self) -> None:
        with self.assertRaises(PermissionError):
            call_tool("suno_generate", {"prompt": "x"})

    def test_session_init_and_validate_are_incomplete_without_craft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            created = call_tool(
                "session_init",
                {
                    "workspace": str(workspace),
                    "title": "Dry Run",
                    "kind": "song",
                    "brief": "A private craft-only dry run.",
                },
            )
            session_dir = Path(created["session_dir"])
            self.assertTrue((session_dir / "manifest.json").is_file())
            self.assertEqual(created["manifest"]["schema_version"], 5)
            validated = call_tool("session_validate", {"session_dir": str(session_dir)})
            self.assertFalse(validated["ready_for_suno"])

    def test_jsonrpc_tools_list_has_no_generate(self) -> None:
        response = handle_rpc(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        )
        names = [tool["name"] for tool in response["result"]["tools"]]
        self.assertNotIn("suno_generate", names)
        payload = json.dumps(response)
        self.assertNotIn("suno_generate", payload)

    def test_catalog_list_returns_tracked_scores_without_audio(self) -> None:
        listed = call_tool("catalog_list", {})
        self.assertIn("works", listed)
        self.assertIsInstance(listed["count"], int)


if __name__ == "__main__":
    unittest.main()
