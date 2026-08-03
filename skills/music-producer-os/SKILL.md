---
name: music-producer-os
description: Orchestrate an original song, instrumental, or guided meditation from brief through craft, Suno packet, taste review, logged-in browser generation, and durable receipt. Use for "make a song", "produce this", "create in Suno", "guided meditation", and compound music requests.
version: 0.1.0
tags: [music, production, suno, songwriting, meditation, orchestration]
---

# Music Producer OS

Use this as the entry point for compound music work. It coordinates specialist skills and keeps one compact production record; it does not spawn a large swarm by default.

## Trigger contract

Activate when the user asks to:
- make, write, compose, produce, arrange, or generate a song;
- turn an idea, poem, voice note, passage, or emotional state into music;
- create a guided meditation or spoken-word music piece;
- build Suno prompts or generate the result in the logged-in Suno account;
- review or improve a draft before spending more Suno credits.

## Autonomy and credit policy

- "Write/draft/prompt" means create the complete creative packet but do not click Suno Create.
- "Generate/create it in Suno" authorizes browser execution and **one Create action**. Suno normally returns two takes from that action.
- Additional Create actions, public sharing, publishing, downloads, uploads, covers, extensions, or remasters require a follow-up instruction.
- Never interact with payment, subscription, password, passkey, 2FA, or permission dialogs.

## Token-efficient pipeline

### 1. Recover intent before asking

Use the user's message, current session, `session_search`, and accessible local knowledge. Ask only for a missing fact that materially changes the work. Otherwise make an explicit artistic assumption and move.

Classify:
- `song`: sung lyrics and full production;
- `instrumental`: no vocal text required;
- `meditation`: preferred lane is spoken script + separate instrumental bed;
- `spoken-suno`: experimental spoken-word performance inside Suno.

### 2. Open a durable run

From the canonical checkout:

```bash
python ~/agentic-music-producer-os/scripts/session_cli.py init \
  --title "<working title>" --kind <song|instrumental|meditation> \
  --brief "<one-paragraph emotional and functional brief>"
```

Capture the returned `session_dir`. All later artifacts go there:
- `brief.md`
- `lyrics.md` for songs, or `script.md` for meditations
- `style-prompt.md`
- `review.md`
- `manifest.json`

If the canonical checkout is elsewhere, locate it first; do not invent a path.

### 3. Build the one-page creative brief

Write these decisions into `brief.md`:
- **Listener moment:** where, when, and why this is heard.
- **Emotional contract:** starting state → pressure/turn → ending state.
- **Point of view:** who speaks to whom; what is withheld until later.
- **Core image:** one concrete image system, not a bag of metaphors.
- **Hook premise:** the phrase or melodic idea the listener carries out.
- **Sonic thesis:** genre family, pulse/BPM range, harmonic color, focal instruments, vocal persona.
- **Energy map:** section-by-section intensity from 1–10.
- **Negative space:** what the production deliberately excludes.

### 4. Compose with the relevant specialist

- Song lyrics: load `lyric-composer`.
- Guided meditation: load `guided-meditation-composer`.
- Instrumental/song production direction: load `suno-ai-mastery`.
- Suno fields: load `suno-prompt-architect`.

Do one strong full draft. Use a second alternate only for the hook, title, or sonic thesis when a real decision remains.

### 5. Build the Suno packet

Write `style-prompt.md` with:
- title;
- newest stable model visible in UI (selected later, not guessed);
- Custom Mode on;
- style prompt;
- Exclude Styles;
- vocal persona or `instrumental, no vocals`;
- production/dynamic arc;
- lyrics with structural and performance tags.

Do not use named artists, copyrighted lyric fragments, trademarked style shortcuts, or voice-cloning language.

### 6. Taste gate

Load `music-taste-review`. Score the packet. Revise until:
- weighted total ≥ 8.5/10 for songs/instrumentals or ≥ 9.0/10 for meditations;
- no axis < 7.5;
- no hard veto.

Write the scored review and exact revisions to `review.md`. Validate:

```bash
python ~/agentic-music-producer-os/scripts/session_cli.py validate <session_dir>
```

Do not open Suno until `ready_for_suno` is true.

### 7. Generate only when requested

Load `suno-browser-operator`. Use the user's logged-in Chrome in the background. One Create action is the default. Verify the resulting two take cards, capture their actual Suno IDs/URLs, and record each:

```bash
python ~/agentic-music-producer-os/scripts/session_cli.py record <session_dir> \
  --url "<verified-suno-url>" --id "<verified-id>" --take 1 \
  --action-id "<one-local-create-receipt-id>" --model-label "<visible-model-label>" \
  --take-title "<visible-take-title>" \
  --note "<first-listen observation>"
```

Use the same action ID and model label for the second take from that Create click. Never pass `--additional-action-authorized` unless the operator issued a separate instruction authorizing another Create action.

If login is absent, stop with the exact page state and ask the user to sign in. Never type credentials.

### 8. Report like a producer

Return:
1. the central creative decision in one sentence;
2. title + style packet location;
3. verified Suno take links if created;
4. concise A&R notes: what works, what to listen for, and the single best next move.

Do not claim audio quality, BPM accuracy, pronunciation, or successful generation without observing it.

## Escalation

Use delegation only when independent expertise materially improves the output (for example, lyric craft and meditation-safety review in parallel). Do not run a standing seven-agent swarm for a normal track.

Starlight Swarm is a thin bus. If this machine genuinely lacks a YogaBook-only input, send one line naming the artifact and acceptance criterion to the YogaBook bot; continue deep work in the home DM/session. Never post progress chatter or invite dual-gateway dialogue.
