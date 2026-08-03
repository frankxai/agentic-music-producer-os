# Telegram Runbook

## Operating topology

Use the existing **default Hermes Telegram gateway** as the only home gateway on this machine. The dedicated `music-producer` profile gateway stays stopped.

- Deep work: Frank's bot DM/topic.
- Shared Starlight Swarm: one-line assignments or final status only.
- Never let two bots discuss the song with each other in the shared channel.

## After installation

Start a new session so the mirrored skills are discovered. If an external shell owns the gateway, restart it there:

```bash
hermes gateway restart
```

If Hermes reports that the command is running inside the gateway process, do not force it: use the in-chat `/restart` command or run `hermes gateway restart` from a separate shell outside the gateway. A normal `/reset` is sufficient when only the skill catalog needs a fresh session.

Start a fresh topic/session after tool or skill changes (`/reset`).

## Natural-language control phrases

### Draft only

> Write an intimate electronic song about recognizing your old self in a train window. Build the complete Suno packet but don't generate yet.

Result: run record, lyrics, style, exclusions, taste review. No credit spend.

### Full execution

> Make this into the strongest original song you can, review it hard, then generate it in my logged-in Suno here.

Result: complete packet + one Suno Create action (normally two takes) + verified links.

### Guided meditation

> Create a twelve-minute grounded meditation for coming down after a high-pressure workday. Use separate narration and an instrumental Suno bed. Generate the bed in Suno.

Result: safe spoken script, pause map, instrumental prompt, one Suno Create action for the bed.

### Controlled iteration

> Take the stronger Suno version. Keep the chorus and vocal persona, but make Verse 2 less dense and the ending a hard unresolved stop. Generate one new pair.

Result: one-variable revision + one additional authorized Create action.

## What an explicit command authorizes

| Wording | Action |
|---|---|
| "write", "draft", "make a prompt" | Text packet only |
| "generate/create in Suno" | One Create action; typically two takes |
| "generate another pair" | One additional Create action |
| "publish/share/release" | Separate workflow and confirmation; never inferred |

## Starlight Swarm escalation

If a YogaBook-only input genuinely blocks the work, send exactly one targeted assignment to the YogaBook bot:

```text
@Hermesyogabookbot MUSIC INPUT — Need <artifact/fact>. Acceptance: <one verifiable criterion>. Reply with path/link only.
```

Do not send progress banners, acknowledgements, periods, or open-ended "thoughts?" prompts. Continue composition in the home DM/session. When the result arrives, verify it at the provided source before using it.

## Failure handling

- **Suno asks for login/2FA:** agent stops; Frank completes login, then says "continue".
- **Credits exhausted/paywall:** agent reports visible state and stops.
- **Computer use unavailable:** run `hermes computer-use doctor` from Desktop/terminal.
- **Wrong tab/UI changed:** agent re-captures; never reuses stale element indices.
- **Skill not activating:** run `/skill music-producer-os`, then `/reset`; verify with `hermes skills list`.
- **Shared-channel chatter:** stop responding; move deep work to DM and require explicit bot mention in the shared bus.
