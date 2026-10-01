# Music providers and connectors

Checked 2026-10-01; recheck official docs and account access before paid execution.
This is a capability register, not proof that a key, app or entitlement is installed.
ChatGPT/Codex subscriptions do not include third-party API usage charges.

| Lane | Current documented route | Strong use | Boundary |
|---|---|---|---|
| Suno | v6; supervised Create in an authorized account | Full songs and iterative human selection | No official public generation API verified; observe current model/settings/credit cost |
| Lyria full | Gemini Interactions, `lyria-3.5` | Programmatic full-song rendering | Approximate duration, single turn; SynthID |
| Lyria clip | `lyria-3-clip-preview` | Fixed 30-second render | Separate generation, not a continuation/edit |
| Eleven Music | `/v1/music`, `music_v2_5` | Prompt or chunk composition plan | Check account duration/rights/output entitlements |
| MiniMax through fal | Queue `minimax/music-3` | Original vocal songs with lyrics | Duration is an upper bound; own-line section tags |
| MiniMax direct | Official music API | Eligible existing accounts | Official August notice restricts new paid music/lyrics access; verify eligibility |
| ACE-Step | Official local API/weights | Sovereign generation and local editing | Hardware, model license and quality need a local benchmark |

## Translate a song once

Keep the approved lyric and musical contract provider neutral. Each adapter owns
the provider model ID, request shape, lengths, instrumental semantics and edit
support. Do not send Suno bracket/performance habits unchanged to every model.

Suno: keep title, Style, Exclude Styles and Lyrics as separate fields. Verify the
visible model and UI limits. Tags, BPM, harmony and spatial instructions remain
directions, not enforceable controls. Current v6 documentation describes up to
eight minutes; do not promise eight minutes for every account or output.

Lyria: one prompt can describe structure and original lyrics. Full-song duration
is a hint. The current Interactions response must contain actual audio; retain
watermark/provenance metadata. Exact notation belongs to the score lane.

Eleven: use one prompt or a composition plan, not both. Chunk plans can preserve
approved lyric text and sectional direction. Current API docs describe up to 30
chunks, each 3–120 seconds and total 3–600 seconds; verify the account's limit.
Stored song references can support inpainting; stem separation is a separate
endpoint and charge/entitlement. Preserve source/song references before editing.

MiniMax/fal: put `[Verse]`/`[Chorus]` tags on their own lines. Current Music 3
requires prompt and lyrics in the validated lane here; do not advertise tested
instrumental support. Persist request ID before polling and archive returned
audio before links expire. Never blindly repeat a timed-out paid POST.

## Native skills, apps and MCP

Skills teach decisions. Plugins distribute skills and tools. MCP exposes callable
tools. Connectors give an authenticated surface access. None of these words proves
that music generation is connected. Inventory actual tools first.

The public `suno-mcp-server` is a text workbench and packet preparer. A prompt/tool
success is not a Suno take or download. Personal installed skills do not deploy
their own remote MCP servers. Local stdio tooling needs a compatible host; a
mobile ChatGPT session needs a separately hosted authenticated app/tool surface.

Use the native GitHub connector for source/review, Drive or an object store for
owned exports, Notion for project records when configured, and n8n for deterministic
jobs. Check permissions and callable operations. Do not invent a Suno connector,
an n8n mutation tool or Eleven Creative Flows API. Flows has a UI; public API support
was still described as planned in the checked docs.

## Prices are estimates

Planning examples: Lyria full $0.08/song; clip $0.04; Eleven Music $0.15/min;
fal MiniMax Music 3 $0.002/second. Store rate date, currency, billable duration and
scope. These exclude reasoning calls, edits, stems, storage, taxes and compute.
Suno credits need their own observed per-action envelope. A USD field never
authorizes a Suno Create or a paid generation by itself.

## Official references

- https://help.suno.com/en/articles/13924801 — current v6 family
- https://help.suno.com/en/articles/13924481 — Variety/Max directions
- https://help.suno.com/en/categories/550145-rights-ownership — account/rights guidance
- https://ai.google.dev/gemini-api/docs/music-generation
- https://ai.google.dev/gemini-api/docs/pricing
- https://elevenlabs.io/docs/api-reference/music/compose
- https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans
- https://elevenlabs.io/docs/eleven-api/guides/how-to/music/inpainting
- https://elevenlabs.io/pricing/api
- https://platform.minimax.io/docs/api-reference/music-generation
- https://fal.ai/models/minimax/music-3/api
- https://github.com/ace-step/ACE-Step-1.5

Provider claims are documented facts dated above. Craft choices are hypotheses.
Account availability, rendered quality and rights for a particular take remain
unverified until a scoped receipt exists.

## MiniMax Music 3 packet template

Keep provider instructions outside the sung lyric. Prepare this input for the official fal queue client; submission remains a separate authorized operation.

```json
{
  "prompt": "Genre, pocket, vocal register/delivery, bass/instrument roles, section contrast and ending. Sing only the supplied original lyric.",
  "lyrics": "[chorus]\nLeave your coat here\nWe have time",
  "duration": 45
}
```

`duration` is an upper bound (up to 300 seconds), not a guaranteed exact length. Every bracket tag has its own line. Preserve approved lyric words; test an edit as a new revision.
