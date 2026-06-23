# Agentic Music Producer OS

> The producer-focused profile of [Agentic Music OS](https://github.com/frankxai/agentic-music-os) — autonomous, end-to-end production workflows for AI-native producers. Part of the [FrankX Intelligence Systems](https://github.com/frankxai/frankxai/blob/main/ECOSYSTEM.md) family.

## What this is

Where [agentic-music-os](https://github.com/frankxai/agentic-music-os) is the general operating system, **Producer OS** is the opinionated workflow layer for shipping releases at volume: batch generation, A&R-style curation, catalog management, and distribution prep — run by agents, supervised by the producer.

## Where it sits in the stack

```
agentic-music-producer-os  →  extends  →  agentic-music-os
                              →  composes →  music-intelligence-systems · SIS · ACOS
```

## Planned modules

- `pipeline/` — folder-drop → generate → curate → master → catalog
- `curate/` — taste-model scoring, keep/cut decisions, playlist assembly
- `catalog/` — metadata, splits, rights, release calendar
- `distribute/` — release prep for streaming platforms

## Relationship to siblings

- **[agentic-music-os](https://github.com/frankxai/agentic-music-os)** — the OS this builds on.
- **[music-intelligence-systems](https://github.com/frankxai/music-intelligence-systems)** — the knowledge substrate.
- **[suno-mcp-server](https://github.com/frankxai/suno-mcp-server)** — generation backend.

> If consolidation is preferred, this repo folds cleanly into `agentic-music-os` as its `producer/` profile.

## Status

🌱 Scaffolding.

---

<sub>Part of the <a href="https://github.com/frankxai/frankxai/blob/main/ECOSYSTEM.md">FrankX ecosystem</a>.</sub>
