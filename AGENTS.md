# Agent Instructions

Read `CLAUDE.md`, then `SOUL.md`, `docs/ARCHITECTURE.md`, and the relevant skill before changing this repository.

## Role

This repository is both:
1. a shareable Hermes profile distribution; and
2. the machine-local source of truth for the default Telegram gateway's music skills.

## Rules

- Keep `distribution.yaml` at the repository root.
- Never add `.env`, auth, browser cookies, memories, sessions, logs, generated runs, or other user state.
- Every `skills/<name>/SKILL.md` frontmatter `name` must exactly match its directory.
- Suno prompts must describe musical attributes rather than named artists or cloned voices.
- Browser generation must use capture → element index → verify; never store coordinates or credentials.
- One explicit generation request authorizes one Suno Create action by default; publishing and additional credit spend are separate decisions.
- Keep the default Telegram gateway as the only running gateway for the shared bot.
- Do not commit or push unless the operator explicitly asks.

## Verification

```bash
python -m unittest discover -s tests -v
python scripts/install_machine.py --dry-run --install-profile
hermes computer-use doctor
```

After machine install:

```bash
hermes profile show music-producer
hermes -p music-producer skills list
```
