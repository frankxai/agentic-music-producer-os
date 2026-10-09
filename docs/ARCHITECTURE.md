# Architecture

## Decision

Agentic Music Producer OS is a **Hermes profile distribution plus portable skill pack**, not a new daemon and not a Hermes fork.

The router chooses prompt, full lyric, score or guidance work; craft specialists produce only the selected deliverable. Authorized execution yields observed receipts. Listening, technical QA and release decisions require their own evidence. See `WORKFLOW-CONTRACTS.json` for exact handoffs.

The intended installation uses a dedicated `music-producer` profile for focused Desktop/CLI sessions with its gateway stopped; source updates do not prove a host install. The same eight skills are mirrored into the default Hermes skill root so a natural-language Telegram DM can activate them without a second bot.

## Why one gateway

Running the same Telegram bot token from two profile gateways creates competing long-poll consumers. Running two machine bots freely in one shared channel creates self-echo and status thrash. The topology therefore keeps:

- default profile DM as the home and deep-work surface;
- Starlight Swarm as a thin assignment/status bus;
- dedicated music profile as a local reasoning persona, not another shared-channel responder.

## Runtime layers

### 1. Intent/router

`skills/music-producer-os/SKILL.md` classifies score, song, instrumental, meditation, or experimental spoken-Suno work. It recovers context, opens one run, and loads only the needed specialist skills.

### 2. Craft specialists

- `score-composer`: compact DSL, MusicXML/MIDI/ABC/sheets/tabs, Lyria/Suno bridges.
- `lyric-composer`: premise, image system, hook, prosody, section mechanics.
- `guided-meditation-composer`: trauma-sensitive spoken pacing and speech-safe music beds.
- `suno-ai-mastery`: rhythm, harmony, timbre, vocal persona, dynamics, production.
- `suno-prompt-architect`: default Simple prompt or explicitly selected Custom fields.
- `music-taste-review`: scoped evidence and reasoned craft review; schema-5 scores retained only for compatibility.

### 3. Browser operator

`suno-browser-operator` uses the actual logged-in local Chrome through `computer_use`. It captures the UI, acts by current accessibility-tree element index, verifies every state change, clicks Create once, and records only real take URLs/IDs.

The public `suno-mcp-server` repository is currently a scaffold, so this build does not pretend an API backend exists.

### 4. Durable session contract

`scripts/session_cli.py` stores each run beneath:

```text
~/agentic-music-producer-os/runs/YYYY-MM-DD/HHMMSS-title/
├── manifest.json
├── brief.md
├── lyrics.md / script.md  # when applicable
├── style-prompt.md
├── review.md
├── composition-map.md
├── vocal-casting.md
└── audiovisual-hook-board.md
```

`manifest.json` uses schema v6 for Simple sessions; schema v5 Custom sessions retain compatibility. Its locally **verified but unanchored** hash-linked event log records `create_authorized → voice_observed (when vocals apply) → browser_preflighted → create_submitted → generation_observed`, then separately records per-take `download_authorized → download_recorded → listening_recorded → technical_qa_recorded`. Every CLI mutation validates the stored hash chain first. The log detects ordinary local alteration but is not an external trust anchor or a substitute for gateway-signed confirmation. A valid Suno URL, UI reference, UI hash, or a listening command remains an operator-supplied local assertion; no playback or technical-quality claim is made without its corresponding receipt and tool evidence.

A run is executable only when its selected mode contract passes deterministic checks; see `SESSION-MODES.md`. Simple requires exact prompt, 2–3 song hook cells (none for instrumentals), brief and prompt-scoped evidence review. Custom retains its full packet and legacy gates. Vocal songs require observed Voice/Persona state: selected for Custom, selected or observed not_applicable for Simple. A downloaded asset must be inside an explicit C940 release root and is bound to a separate take-specific download authorization with a file SHA-256. `KEEP` is unavailable until a declared real playback receipt exists; technical QA requires that `KEEP` decision. Generated runs and assets are gitignored and never included in the profile distribution.

Album-level `scripts/album_cli.py` creates a private ledger with a hard maximum of 10 Create reservations and separate observed outcome telemetry. It never treats a plan allocation as an observed Create or provider cost.

## Token model

- One orchestrator handles a normal track.
- Specialist skills load on demand rather than all at startup.
- One strong direction + one controlled alternate maximum.
- One Suno Create action per explicit request; record actual observed results, subject to the current recorder capacity.
- Delegation is reserved for independent, high-value review—not routine ceremony.
- Old screenshot context is handled by Hermes's computer-use pruning.

## Trust boundaries

| Boundary | Rule |
|---|---|
| Credentials | Never shipped, read, printed, or typed by the agent |
| Browser login | User signs in; agent stops at password/passkey/2FA |
| Credits | One Create action per explicit generation instruction |
| Publishing | Never implied by generation; requires separate instruction |
| Originality | No named-artist imitation, cloned voice, or borrowed lyrics |
| Meditation | Creative wellness, permissive language, no medical claims |
| Evidence | No fabricated URLs, audio metrics, UI state, or completed actions |


Current operational routing: `WORKFLOW-CONTRACTS.json`; mode-specific validation: `SESSION-MODES.md`; evidence gates: `MUSIC-REGULATORS.md`.
