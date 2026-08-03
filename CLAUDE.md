# CLAUDE.md

`AGENTS.md` is the cross-agent entry point and source of truth for repository operations.

Product intent: build the smallest complete music-production agent that can move from Telegram intent to a verified Suno generation while preserving human-level craft, finite credits, provenance, and one-gateway fleet discipline.

Architecture decisions:
- Profile + skills, not a Hermes core fork.
- Existing default gateway is the Telegram front door.
- Local Chrome/Suno through `computer_use`; the current `suno-mcp-server` is not treated as a working generation backend.
- Deterministic Python session receipts; no database or daemon.
- Specialized skills load only when relevant to minimize prompt cost.

Run tests with:

```bash
python -m unittest discover -s tests -v
```
