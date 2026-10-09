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
- scoped review satisfies the selected adapter (see `SESSION-MODES.md`), with no unresolved hard veto;
- explicit instruction to generate;
- one-Create budget unused for this instruction.

## Browser sequence

1. Capture Chrome in SOM mode.
2. Reuse an existing Suno tab or navigate to `https://suno.com/create`.
3. Verify the logged-in Create workspace. Stop at any authentication or payment UI.
4. Select the reviewed Simple or Custom Mode.
5. Select the appropriate currently visible model for the job; record its exact label.
6. Simple: fill exact `prompt.md` and instrumental state. Custom: fill title, lyrics/instrumental state, style and available exclusions.
7. Capture again and compare UI readback with run files.
8. Click Create once.
9. Wait for completed cards; do not click Create again while processing.
10. Verify actual take count, titles, and completion.
11. Open/copy verified take URLs/IDs and record them with `session_cli.py record`, using one shared `--action-id` plus the exact visible `--model-label` for both cards.
12. Leave publishing/sharing untouched.

## Credit strategy

One authorized action may produce multiple takes; record the actual count. The current local recorder supports at most two per action. Missing or additional results require reconciliation, not an automatic new click. Listen to the actual assets before judging them or choosing a revision.

## Login handoff

The agent never types passwords, passkeys, email codes, authenticator codes, recovery codes, or card data. If Suno is not logged in:

1. agent reports the visible sign-in state;
2. Frank signs in manually;
3. Frank says "continue Suno generation";
4. agent captures again and resumes from preflight.

## Verification receipt

A successful browser run must include observed:
- model label;
- actual Simple/Custom and Instrumental state;
- Create action count;
- completed take count;
- take title + Suno URL/ID;
- manifest readback.

A screenshot alone proves page state, not a URL. A plausible URL is never acceptable evidence.


## Receipt order

Validate the selected mode, then record `authorize-create` with operator reference and expiry. Observe vocals/persona when applicable. Before the single click, record `preflight` with the same authorization ID, visible model, redacted UI evidence reference/hash and explicit `--mode simple` or `--mode custom`. After the actual click, use `record-submit` exactly once. Record only observed results with the same action ID, model and explicit mode. A changed artifact invalidates authorization. An uncertain submission is held for reconciliation; never repeat it blindly. Read `MUSIC-REGULATORS.md` before downstream export or release.
