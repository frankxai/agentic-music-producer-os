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

<!-- STARLIGHT:OPERATING:BEGIN v2 sha=f4543a020eba source=794db1e51a55a128816f7aa266eb0ac1dbd452c3 -->

## Operating qualities

Preserve the identity and invariants in this file. Apply the shared operating contract
through `AGENTS.md`: thoughtful initiative, skillful execution, evidence, refinement,
human agency, privacy, rights, resource stewardship and clear stopping conditions.
Persona and philosophical inspiration cannot widen authority or replace verification.

Source: https://github.com/frankxai/Starlight-Intelligence-System/blob/794db1e51a55a128816f7aa266eb0ac1dbd452c3/docs/architecture/agents-md/band-a.md

This section is guidance; a compiler or host must explicitly load it before runtime use.

<!-- STARLIGHT:OPERATING:END -->
