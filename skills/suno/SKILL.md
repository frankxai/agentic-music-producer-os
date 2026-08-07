---
name: suno
description: "The /suno entry point. Classifies intent, picks the execution backend (Chrome MCP, desktop computer use, a self-hosted Suno MCP, or hand-off), plans the run, executes one authorized generation, verifies the result, and hands to post-production for download, measurement, and review. Use for /suno, \"generate it in Suno\", \"run the packet\", \"make the song now\", \"execute this\", or any request that spans prompt to finished audio."
version: 0.1.0
tags: [suno, execution, routing, browser, computer-use, mcp, orchestration]
---

# /suno

One command, five phases: **classify → plan → build → execute → deliver.**

This skill owns *execution and delivery*. It does not own craft — `music-producer-os` owns the
brief, `lyric-composer` owns lyrics, `suno-prompt-architect` owns the packet. When those have
not run and the request needs them, run them first rather than prompting from a mood.

---

## Phase 1 — Classify intent

Read the request and place it in exactly one lane before doing anything else. Stating the lane
back in one line is the cheapest way to catch a misread.

| Signal | Lane | Behavior |
|---|---|---|
| "write / draft / prompt / give me a packet" | **PACKET** | Build to a copy-paste packet. Do not open a browser. Do not spend a Create. |
| "generate / create it / run it / make the song" | **EXECUTE** | Full arc, one Create action, verify, deliver. |
| "another take / try it with X / iterate" | **ITERATE** | Requires a prior run. Change one variable, one Create. |
| "download / get the file / save it" | **DELIVER** | No generation. Fetch, archive, measure. |
| "how did it come out / review the take" | **REVIEW** | No generation. Measure and transcribe; hand judgment back. |
| "extend / cover / remaster / replace section" | **DERIVE** | Separate authorization each time. Never bundled into an earlier request. |

**Ambiguity default: PACKET.** Producing a packet when EXECUTE was wanted costs one message.
Executing when PACKET was wanted costs a Create action and Frank's credits. The asymmetry decides.

## Phase 2 — Pick the backend

Full decision matrix and probe procedure: `reference/backend-matrix.md`.

Short version, in order:

1. **Claude in Chrome MCP** — preferred when available. DOM-aware, reads back field contents
   reliably, survives layout changes better than pixel work.
2. **Desktop computer use** (`suno-browser-operator`) — the Hermes-native path and the fallback
   when the Chrome extension is not connected. Capture → element index → verify, never coordinates.
3. **Self-hosted Suno MCP** — **probe, never assume.** There is no Suno connector in the Anthropic
   registry; any MCP here is third-party or self-hosted, and this repo's operating notes do not
   treat it as a working generation backend. If one is connected, call a read-only tool first and
   confirm the response shape before routing a generation through it. If the probe is anything
   other than clean, fall back to a browser lane and say so.
4. **Hand-off** — print the packet and let Frank paste it. Correct answer when no browser lane is
   healthy, when the account needs sign-in, or when a paywall, 2FA, or credit wall is visible.

Never silently downgrade between backends mid-run. Name the backend before executing and name it
again in the receipt.

## Phase 3 — Build and gate

Before any Create action, all of these must hold:

- session exists and `style-prompt.md` plus `lyrics.md` (or `script.md`) are written;
- `music-taste-review` passed — ≥85/100 for songs and instrumentals, ≥90/100 for meditations,
  no axis under 7.5, no hard veto;
- `session_cli.py validate <session_dir>` returned `ready_for_suno: true`;
- pronunciation risks resolved per `../suno-prompt-architect/reference/phonetic-control.md`.

The taste gate is not skippable because the backend is fast, and not skippable because the lane
is local and free. It exists to stop generation of things nobody will listen to.

## Phase 4 — Execute

**One explicit request authorizes one Create action.** Suno normally returns two takes from it.
Extend, cover, remaster, replace-section, artwork, publish, share, and download each require a
separate instruction. Never bundle.

Execution invariants, whichever backend:

- Read back every populated field against the source files before clicking. Truncation and
  dropped line breaks are the most common silent failure, and they are invisible after generation.
- Select the newest stable model visible to the account unless told otherwise. Record the exact
  visible label — do not infer a version number.
- Click Create once. Wait for real result cards; do not re-click while a generation is pending.
- Capture the actual take titles, URLs, and IDs. Never construct a URL.
- Stop and report on any sign-in, passkey, 2FA, payment, permission, or credit-exhausted dialog.
  Never type credentials, never dismiss a security prompt.

Record both takes under one Create action ID via `session_cli.py record`.

## Phase 5 — Deliver

Hand to `song-postproduction` for download, archival, objective measurement, and transcription.

**On listening: I cannot hear audio.** Any claim about how a take sounds that I did not measure
is fabrication, and `music-taste-review` treats it as a hard veto. What replaces ears:

- **Transcription** of the generated vocal, diffed against `lyrics.md`. This objectively catches
  the one defect class that cannot be repaired after generation — pronunciation and lyric
  intelligibility — and it is the single highest-value post-generation check available.
- **Measurement** — duration, integrated loudness, true peak, dynamic range, leading and trailing
  silence, clipping, and a per-second energy curve that shows whether the intended dynamic arc
  actually happened.
- **Structure inference** from the energy curve against the packet's energy map.

Then Frank listens and supplies the judgment. The division of labor is: I bring evidence, he
brings taste. Ask him for a `KEEP` / `ITERATE` / `CUT` call and, if `ITERATE`, the single
dominant variable to change.

---

## Receipt

Every run reports, in this order:

1. lane and backend used;
2. model label exactly as displayed;
3. one Create action, and the number of take cards actually observed;
4. verified titles and URLs or IDs per take;
5. measurement summary and transcription diff, or a plain statement that they were not run;
6. the single best next move.

Never claim generation succeeded, audio quality, BPM accuracy, or pronunciation correctness
without the observation or measurement that supports it. An unverified claim in a receipt is
worse than a missing one — it survives into the next session as a fact.

## Handoff

- Brief and craft orchestration: `music-producer-os`
- Lyrics: `lyric-composer` · rewrites onto an existing tune: `song-adaptation`
- Musical direction: `suno-ai-mastery`
- Packet assembly: `suno-prompt-architect`
- Quality gate: `music-taste-review`
- Desktop execution: `suno-browser-operator`
- Download, measurement, transcription, archive: `song-postproduction`
- Open-weight lane instead of Suno: `local-music-generation`
