# Agentic Music Producer OS

A shareable Hermes profile and machine workflow for **original songs, guided meditations, Suno production packets, taste review, and verified browser generation**.

This repository upgrades the original scaffold into a working profile-first system. It uses Frank's existing creator/music intelligence, but keeps runtime state local and the operating surface small:

```text
Telegram brief → compose → taste gate → Suno Custom Mode → two verified takes → durable receipt
```

## What ships

| Surface | Purpose |
|---|---|
| `music-producer` Hermes profile | Grok-first creative persona with authenticated OpenAI Codex fallback |
| Seven portable skills | Orchestration, lyrics, meditation, Suno craft/prompting, taste, browser execution |
| Default-gateway mirroring | Natural Telegram prompts can execute on this machine without a second bot |
| Background Chrome control | Uses the operator's logged-in Suno session; never stores credentials |
| Session CLI | Reviewable brief, lyrics, style, score, and verified generation URLs |
| One-Create policy | One explicit generation command spends one Create action, usually returning two takes |

## Architecture

The existing default Hermes gateway remains the **single Telegram front door**. The dedicated music profile is installed for focused local sessions, but its gateway stays stopped. This avoids duplicate polling, shared-channel echo loops, and token waste.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Install on this machine

Prerequisites: Hermes ≥0.18, Python 3.11+, Git, Chrome, a configured model provider, and a Suno account that Frank signs into manually.

```bash
git clone https://github.com/frankxai/agentic-music-producer-os.git
cd agentic-music-producer-os

# Background desktop control
hermes computer-use install
hermes computer-use doctor

# Preview the exact local changes
python scripts/install_machine.py --dry-run --install-profile

# Install focused profile + mirror the seven skills into the default Telegram profile
python scripts/install_machine.py --install-profile --profile-name music-producer

# Make the Telegram dependencies explicit instead of relying on platform defaults
hermes tools enable skills computer_use --platform telegram
hermes -p music-producer tools enable computer_use

# From a separate shell outside the running gateway, reload it after skill changes
hermes gateway restart
```

The installer mirrors only `skills/<name>/...` into the default profile and stages only manifest-owned files for the dedicated profile, so repository `.git` metadata and runtime caches never enter Hermes. It never copies credentials, auth, sessions, memory, logs, or browser data. If the new profile has no `.env`, it may create one containing only the detected non-secret `HERMES_CUA_DRIVER_CMD` path; an existing `.env` is never modified.

The wrapper is the only supported install/update path for a local checkout. It keeps a persistent sanitized source under `HERMES_HOME/local/profile-sources/music-producer`; direct `hermes profile install` from the repository root is intentionally unsupported because Hermes v0.18.2 copies unowned top-level files. For an existing profile, preview and explicitly authorize only the profile refresh:

```bash
python scripts/install_machine.py --dry-run --install-profile --force-profile
python scripts/install_machine.py --install-profile --force-profile
```

Mirrored skills use a local hash ledger. An unowned or user-modified collision stops without changing anything. Use `--force-skills` only after reviewing and intentionally accepting replacement of those named skill directories. `hermes profile update` reads the sanitized source but does not refresh it from Git; rerun this wrapper for repository upgrades.

If the new profile needs the same provider login as the default profile, configure it through Hermes auth/model setup; do not put credentials in this repo:

```bash
hermes -p music-producer model
```

## Verify

```bash
python -m unittest discover -s tests -v
hermes profile show music-producer
hermes -p music-producer skills list
hermes -p music-producer fallback list
hermes -p music-producer computer-use doctor
hermes tools list --platform telegram
hermes gateway status
hermes -p music-producer chat -Q -q \
  'Load the music-producer-os skill, then reply exactly MUSIC_PROFILE_SKILL_OK'
```

The dedicated profile should be present with its gateway **stopped**. The default gateway should remain the only running Telegram gateway. The profile prefers Grok and automatically falls back to `openai-codex/gpt-5.6-sol` when Grok OAuth is unavailable, rate-limited, or out of credits.

## Use from Telegram

Draft without credits:

> Write the strongest original song from this idea. Give me the complete Suno packet and taste review, but don't generate yet: ...

Full execution:

> Compose this like the best human team would, review it hard, then generate it in my logged-in Suno here: ...

Guided meditation:

> Write a twelve-minute grounded guided meditation for winding down after a high-pressure day. Use a separate spoken script and instrumental Suno bed, then generate the bed.

See [`docs/TELEGRAM-RUNBOOK.md`](docs/TELEGRAM-RUNBOOK.md).

## Production record

Initialize:

```bash
python scripts/session_cli.py init \
  --title "Light Between the Waves" \
  --kind song \
  --brief "Intimate art-pop that moves from vigilance to grounded hope."
```

After writing `style-prompt.md`, `review.md`, and either `lyrics.md` for a song or `script.md` for a meditation:

```bash
python scripts/session_cli.py validate <session-dir>
```

After a real Suno take exists:

```bash
python scripts/session_cli.py record <session-dir> \
  --url "https://suno.com/song/<verified-id>" \
  --id "<verified-id>" --take 1 \
  --action-id "create-001" --model-label "<visible-model-label>" \
  --take-title "<visible-take-title>" \
  --note "Verified first take; chorus landed, Verse 2 needs less density."
```

The CLI enforces readiness and review thresholds, accepts only Suno `/song/<id>` or `/s/<id>` evidence, requires each ID to match its URL, and rejects duplicate IDs, URLs, or take numbers. It groups up to two observed takes under an auditable one-click Create action. A second action requires a distinct single-use authorization bound to a new explicit operator instruction; no Boolean or CLI switch can substitute. Download, declared actual-playback, tool-derived QA, and private DAM/rights retention receipts are separate gates. It never invents a generation receipt.

## Skills

| Skill | Loads when |
|---|---|
| `music-producer-os` | Compound song/meditation/production request |
| `lyric-composer` | Lyrics, hooks, prosody, rewrites |
| `guided-meditation-composer` | Guided practice or spoken wellness audio |
| `suno-ai-mastery` | Arrangement, vocal persona, production, iteration |
| `suno-prompt-architect` | Exact Custom Mode fields |
| `music-taste-review` | Pre-credit gate and first-listen A&R |
| `suno-browser-operator` | Explicit logged-in Suno generation |

The built-in Hermes `songwriting-and-ai-music` skill remains useful; this pack adds Frank's full orchestration, safety, taste, session receipts, and browser execution.

## Principles

- Original musical attributes, never named-artist imitation or cloned voices.
- One strong direction over twenty generic options.
- One Create action by default; additional credits require another instruction.
- Guided meditation is creative wellness content, not treatment.
- No publishing, sharing, or release inferred from generation.
- No fabricated UI actions, links, audio measurements, or success claims.
- Local-first, BYOK, git-backed, profile-first.

## Ecosystem

- [`agentic-music-os`](https://github.com/frankxai/agentic-music-os) — general music operation layer.
- [`music-intelligence-systems`](https://github.com/frankxai/music-intelligence-systems) — composition/production/catalog substrate.
- [`agentic-creator-os`](https://github.com/frankxai/agentic-creator-os) — reusable creator skills and agents.
- [`suno-mcp-server`](https://github.com/frankxai/suno-mcp-server) — future MCP generation backend; currently a scaffold, not claimed as production runtime.

## Status

**v0.1 machine-ready distribution.** Unit-tested local installer and session receipt tooling; browser readiness is verified separately against each machine's interactive Chrome/Suno session.
