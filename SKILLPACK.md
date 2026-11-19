# Music Producer OS skill pack

**Repo:** `frankxai/agentic-music-producer-os`  
**Not an awesome-* catalog.** Public craft pack for original songs, scores, meditations, and Suno packets.

```sh
npx skills add frankxai/agentic-music-producer-os
```

Hermes operators on this machine still use `python scripts/install_machine.py --install-profile`. That path mirrors **all** skills, including the browser operator.

## Include

| Skill | Lane |
| --- | --- |
| `music-producer-os` | craft |
| `score-composer` | craft |
| `lyric-composer` | craft |
| `guided-meditation-composer` | craft |
| `suno-ai-mastery` | craft |
| `suno-prompt-architect` | craft |
| `music-taste-review` | craft |

## Exclude from the public craft install story

| Skill | Lane |
| --- | --- |
| `suno-browser-operator` | operator-only |

The browser operator stays in this repository for logged-in Chrome on an operator machine. It is **not** the skills.sh craft SKU. One explicit generation request still authorizes one Create action. Publishing is a separate decision.

## MCP pair

Local receipts MCP: `python -m scripts.receipts_mcp` (session/score/album/catalog). **No** `suno_generate` / unofficial Suno HTTP. Pair with `starlight-creator-mcp` for visuals after KEEP.

## Forbidden

- Unofficial Suno generate/extend/remix APIs as product tools
- Named-artist imitation or cloned voices
- A second Telegram gateway
- Shipping `.env`, cookies, runs, or catalog audio

## Maintain

`python -m unittest discover -s tests -v` before claiming the pack is green. Skill `name` frontmatter must match its directory.
