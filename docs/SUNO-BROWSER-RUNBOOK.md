# Suno Browser Runbook

## Why browser execution

The operator already has a Suno account and browser session. The public `frankxai/suno-mcp-server` currently has no working server implementation, so the honest production path is Hermes background computer use against the logged-in Chrome UI.

## Machine setup

```bash
hermes computer-use install
hermes computer-use status
hermes computer-use doctor
hermes tools enable skills computer_use --platform telegram
hermes -p music-producer tools enable computer_use
hermes -p music-producer computer-use doctor
```

Windows needs an interactive desktop session. A normal Chrome window must not be elevated above the Hermes process.

Hermes profiles isolate `.env` files. `scripts/install_machine.py` creates a dedicated profile `.env` containing only the local `HERMES_CUA_DRIVER_CMD` path when no profile `.env` already exists. It never edits an existing profile `.env`; in that case, configure the same non-secret driver path manually and rerun `hermes -p music-producer computer-use doctor`.

## Preflight

Before opening Suno:

```bash
python scripts/session_cli.py validate <session-dir>
```

Required state:
- `ready_for_suno: true`;
- taste review ≥85/100 for songs/instrumentals or ≥90/100 for meditations, with no hard veto;
- explicit instruction to generate;
- one-Create budget unused for this instruction.

## Browser sequence

1. Capture Chrome in SOM mode.
2. Reuse an existing Suno tab or navigate to `https://suno.com/create`.
3. Verify the logged-in Create workspace. Stop at any authentication or payment UI.
4. Enable Custom Mode.
5. Select the newest stable model visible in the account.
6. Fill title, lyrics/instrumental mode, style, and Exclude Styles.
7. Capture again and compare UI readback with run files.
8. Click Create once.
9. Wait for completed cards; do not click Create again while processing.
10. Verify actual take count, titles, and completion.
11. Open/copy verified take URLs/IDs and record them with `session_cli.py record`, using one shared `--action-id` plus the exact visible `--model-label` for both cards.
12. Leave publishing/sharing untouched.

## Credit strategy

One Create action normally returns two takes, which is the best default exploration-to-credit ratio. Listen to both before changing the prompt. If neither expresses the thesis, revise one dominant variable and request another pair explicitly.

## Login handoff

The agent never types passwords, passkeys, email codes, authenticator codes, recovery codes, or card data. If Suno is not logged in:

1. agent reports the visible sign-in state;
2. Frank signs in manually;
3. Frank says "continue Suno generation";
4. agent captures again and resumes from preflight.

## Verification receipt

A successful browser run must include observed:
- model label;
- Custom/Instrumental mode;
- Create action count;
- completed take count;
- take title + Suno URL/ID;
- manifest readback.

A screenshot alone proves page state, not a URL. A plausible URL is never acceptable evidence.
