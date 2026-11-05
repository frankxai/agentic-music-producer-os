---
name: music-producer-os
description: "Compose, plan, revise and coordinate original songs, scores, instrumentals or spoken guidance; route simple prompts, explicit full lyrics, notation and authorized generation through relevant craft and evidence gates."
---

# Music Producer Os

Read `docs/MUSIC-FUNDAMENTALS.md`, `docs/MUSIC-REGULATORS.md` and the matching entry in `docs/WORKFLOW-CONTRACTS.json` from the repository root. If installed without the checkout, resolve those same paths at https://github.com/frankxai/agentic-music-producer-os; do not invent execution.

For a prompt-only request, deliver the paste block directly; keep internal review and orchestration out of the answer unless requested or a material blocker needs explanation.

1. Recover the current request and available project context. Do not claim access to unavailable chats. Keep global craft, user preferences, project canon and this song's contract separate.
2. Choose the output lane. For a normal song prompt, return one natural-language code block per song with 2–3 exact loop lines and let the provider write the remainder. Use no full lyrics unless requested. Instrumentals have no lyric cells. Explicit full lyrics use Custom Mode. Sheets/tabs/piano/orchestra route to `score-composer`; notation is canon. Guidance routes to `guided-meditation-composer`, normally with a separate instrumental bed.
3. Establish listener moment, emotional intention, focal idea and one useful constraint. Apply only relevant fundamentals. Route prompt packaging to `suno-prompt-architect`; full lyric work to `lyric-composer`; production decisions to `suno-ai-mastery`.
4. Open a session when durable production tracking is needed: `python scripts/session_cli.py init --workspace <actual-workspace> --title <title> --kind song --brief <brief> --output-mode simple`. Save exact approved prompt bytes in `prompt.md`, hook lines as a JSON array in `hook-cells.json`, and the evidence review in `review.md`. For Custom Mode, pass `--output-mode custom`; its schema-5 adapter still requires its full packet and legacy review fields. Read `docs/SESSION-MODES.md` before operating.
5. Use `music-taste-review` for scoped critique and run `session_cli.py validate`. Prompt PASS means executable prompt, never listened quality or release clearance.
6. Drafting authorizes creative work. An explicit generation request authorizes one bounded Create action. Load `suno-browser-operator`, observe current model/mode/cost, bind the approved artifacts to a single-use authorization and reconcile uncertain submissions. Record actual results only; no promised take count, blind retry or invented links.
7. After authorized approved-channel export, hash the asset and obtain actual listening. Choose KEEP/ITERATE/CUT with evidence; choose one revision variable. Release needs technical, rights, destination and publication decisions independently.
8. Save a concise recap: exact decisions and versions, available assets, unresolved holds and one next action. Learn from actual reported use and verdicts with context. Do not promote a local preference into a universal rule.

Use a compact team. Delegate only a bounded independent question when useful, with appropriate evidence and a clear owner. Do not activate a standing swarm for a simple prompt. Keep existing one-gateway machine discipline. Do not infer deployment, scheduling or account connection from files in this repository.
