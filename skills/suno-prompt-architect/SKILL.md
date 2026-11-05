---
name: suno-prompt-architect
description: "Translate original musical intent into a concise Simple Mode prompt or an explicitly requested Custom Mode packet, preserve exact approved hook/lyric text, and prepare the chosen mode for observed execution."
---

# Suno Prompt Architect

Read the relevant `docs/MUSIC-FUNDAMENTALS.md` module and `docs/MUSIC-REGULATORS.md` from repository root.

Default song output: one clean natural-language code block per song, with a useful title, emotional/sonic direction, vocal character, rhythmic feel, contrast and ending only as needed. Include 2–3 exact single-line hook cells and a clear instruction to preserve and loop them while writing the remaining song. Preserve accepted wording verbatim. Do not add full lyrics, separate operational fields or explanatory labels inside the paste block. Instrumentals contain no hook lyrics.

When the user explicitly requests full lyrics or deliberate Custom Mode control, separate title, style, lyrics and optional exclusions into the actual provider fields. Use structural/performance tags sparingly. Keep pronunciation changes explicit; do not silently rewrite accepted lyrics. Use `lyric-composer` for full lyric craft.

Check coherence, singable stress, focal intent and specific drift risks. Use attribute descriptions rather than imitation or unauthorized voice cloning. Avoid impossible precision: a BPM, section or key instruction is requested direction until measured/observed. Choose a model for the job from current account evidence; never hardcode a version as current.

Save simple sessions as `prompt.md`, exact `hook-cells.json`, brief and scoped review; see `docs/SESSION-MODES.md`. Save Custom packets in the legacy adapter fields only when that lane is selected. An alternate should test one useful variable and preserve the accepted hook. No draft or PASS review authorizes extra generation, export or publication.
