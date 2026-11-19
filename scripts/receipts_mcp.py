"""Local receipts MCP: session/score/album/catalog access. No unofficial Suno generate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts.album_cli import initialize_album
from scripts.session_cli import initialize_session, validate_session
from scripts.skillpack import FORBIDDEN_MCP_TOOLS

REPO_ROOT = Path(__file__).resolve().parents[1]

_TOOLS: tuple[dict[str, Any], ...] = (
    {
        "name": "session_init",
        "description": "Create a local production session receipt. Does not generate audio.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "title": {"type": "string"},
                "kind": {"type": "string"},
                "brief": {"type": "string"},
            },
            "required": ["workspace", "title", "kind", "brief"],
        },
    },
    {
        "name": "session_validate",
        "description": "Validate a session for Suno readiness. Never claims a Create occurred.",
        "inputSchema": {
            "type": "object",
            "properties": {"session_dir": {"type": "string"}},
            "required": ["session_dir"],
        },
    },
    {
        "name": "album_init",
        "description": "Create a private album ledger with a hard Create reservation cap.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "title": {"type": "string"},
                "maximum_create_actions": {"type": "integer"},
            },
            "required": ["workspace", "title"],
        },
    },
    {
        "name": "catalog_list",
        "description": "List tracked score.txt works in the local catalog. No audio generation.",
        "inputSchema": {
            "type": "object",
            "properties": {"repo_root": {"type": "string"}},
        },
    },
)


def list_tools() -> list[dict[str, Any]]:
    return [dict(tool) for tool in _TOOLS]


def _catalog_list(repo_root: Path) -> dict[str, Any]:
    works: list[dict[str, str]] = []
    catalog = repo_root / "catalog"
    if catalog.is_dir():
        for score_path in sorted(catalog.glob("*/score.txt")):
            works.append({"slug": score_path.parent.name, "path": str(score_path)})
    return {"count": len(works), "works": works}


def call_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = arguments or {}
    if name in FORBIDDEN_MCP_TOOLS or name.startswith("suno_"):
        raise PermissionError(
            f"{name} is not a receipts MCP tool; unofficial Suno generate/extend is forbidden"
        )
    if name == "session_init":
        return initialize_session(
            Path(payload["workspace"]),
            str(payload["title"]),
            str(payload["kind"]),
            str(payload["brief"]),
        )
    if name == "session_validate":
        return validate_session(Path(payload["session_dir"]))
    if name == "album_init":
        maximum = int(payload.get("maximum_create_actions") or 10)
        return initialize_album(Path(payload["workspace"]), str(payload["title"]), maximum)
    if name == "catalog_list":
        root = Path(payload["repo_root"]) if payload.get("repo_root") else REPO_ROOT
        return _catalog_list(root)
    raise KeyError(f"unknown receipts tool: {name}")


def handle_rpc(message: dict[str, Any]) -> dict[str, Any]:
    msg_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "music-producer-receipts", "version": "0.1.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": list_tools()}}
    if method == "tools/call":
        try:
            result = call_tool(str(params.get("name") or ""), params.get("arguments") or {})
        except PermissionError as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": str(exc)},
            }
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]},
        }
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"unknown method: {method}"},
    }


def main() -> int:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        message = json.loads(line)
        sys.stdout.write(json.dumps(handle_rpc(message), ensure_ascii=False) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
