# Production-System Evaluation — 2026-07-19

## Verdict

**Status: strong v0.1 production-safe profile distribution; not yet world-class as a complete release-production operating system.**

The current build is unusually strong where most AI-music workflows fail: it has bounded Suno credit behavior, one-gateway discipline, original-work safeguards, meditation safety, a deterministic pre-Suno contract, and verified local Chrome automation health. It is intentionally not yet a full digital-asset, playback-QA, or release system.

## Evidence actually run

| Check | Result |
|---|---|
| Unit suite | `20 passed` via `python -m unittest discover -s tests -v` |
| Profile-install dry run | passed; all seven skill directories unchanged and profile source stayed at the persistent sanitized path |
| Desktop automation health | `cua-driver 0.8.3`; UI Automation and Windows Graphics Capture reachable |
| Installed profile | `music-producer`: Grok 4.3 primary, GPT-5.6-sol fallback, 7 local enabled skills, gateway stopped |
| Default Telegram capability | `skills` and `computer_use` enabled |
| Live model smoke | `hermes -p music-producer chat ...` returned `MUSIC_PROFILE_SKILL_OK` |
| No-credit lifecycle smoke | incomplete session rejected; compliant synthetic song session passed `ready_for_suno` |
| Audio tooling | `ffmpeg` and `ffprobe` available; `songsee` not installed |
| Suno generation/download/listening | not run; no credit spend and no audio playback claim |

## Weighted maturity score

**52.19 / 100**

This score measures the complete product lifecycle, not merely the correctness of the current code. A strong one-Create browser workflow cannot be called world-class while it lacks durable download, listening, technical-QA, DAM, and release-gate evidence.

| Dimension | Score | Weight | Rationale |
|---|---:|---:|---|
| Originality, lyric, and meditation safety | 86 | 15 | Strong craft skills and clear hard vetoes; no deterministic full-review-axis parser yet |
| Browser and credit safety | 91 | 15 | One Create boundary, capture/read-back doctrine, healthy desktop driver |
| Deterministic pre-Suno receipts | 82 | 12 | Session schema v3 and strict URL/duplicate checks; review parser remains too shallow |
| Voice/persona observability | 30 | 8 | No mandatory observed voice-inspection receipt yet |
| Audio-visual hook system | 20 | 10 | No durable hook board or lead-track social asset contract |
| Authorized download and actual listening | 15 | 12 | Explicitly separated in policy, but no receipt/state-machine implementation |
| Technical audio QA | 25 | 10 | ffmpeg is available; no QA runbook or stored tool evidence exists |
| DAM, rights, and release gate | 20 | 10 | Runs/receipts exist but there is no master catalog, rights record, or release-clear gate |
| Token-to-outcome measurement | 45 | 3 | Good specialist-loading doctrine; no run-level actual-usage receipt |
| Independent verification | 75 | 5 | Taste gate and browser read-back are strong; post-generation independence is absent |

## Current strengths to preserve

1. **One explicit Suno Create action is the default credit boundary.**
2. **The default Telegram gateway is the only running shared bot.**
3. **Suno prompts prohibit named-artist imitation and voice cloning.**
4. **Meditation uses a safer separate-script-plus-bed model.**
5. **The installer protects profile distribution from runtime state, secrets, and Windows junction/reparse-point abuse.**
6. **Generation receipts require real Suno URLs/IDs and reject duplicate IDs, URLs, takes, and unapproved second Create actions.**

## Highest-value build sequence

1. Tighten the review parser and introduce `CRAFT_READY` / `SUNO_READY` state transitions.
2. Add a required composition map and audio-visual hook board for lead tracks.
3. Add observed voice/persona selection evidence before Create.
4. Implement separate authorized-download, actual-listening, technical-QA, and `KEEP|ITERATE|CUT` receipts.
5. Implement catalog, rights, asset-hash, and `RELEASE_CLEARED` gates.
6. Add token/outcome receipts and run the first three private demo tracks as calibration data.

The detailed implementation plan is at:

```text
.hermes/plans/2026-07-19_world-class-music-production-system.md
```

## Definition of world-class

The system becomes world-class only when it has:

- at least 90/100 in every safety-critical dimension above;
- an end-to-end dry run that proves every stage and refusal condition;
- at least one retained, actually listened-to private track with real source IDs, audio file hash, QA evidence, and DAM registration;
- a release gate that prevents accidental publication;
- measured token, time, and generation-pair outcomes to inform future routing.

Until then, describe it accurately as a **safe, high-quality v0.1 production profile**—not a finished release machine.

## Independent-audit addendum

Three independent, read-only specialist audits confirmed the overall conclusion and refined the priorities:

| Audit | Score | Material conclusion |
|---|---:|---|
| Architecture, authorization, and execution safety | 58/100 | Current Suno receipts are syntactically validated but self-attested; a user/agent-supplied URL is not proof of an observed browser transaction. |
| Craft and production quality | 69/100 | Lyric and prompt craft are strong; enforceable listening, composition-map, social-hook, vocal-casting, and meditation-safety receipts are absent. |
| Lifecycle, DAM, and QA | 38/100 | The system stops at generated take references; download, playback, technical QA, master storage, catalog, rights, release, social, and analytics controls are unimplemented. |

### Corrected P0

The first implementation task is now **trusted Create authorization and observed-result event receipts**, before tightening the score parser. A Boolean `--additional-action-authorized` flag cannot be treated as operator authorization. The redesign must consume a single-use, expiry-bound authorization that references the originating operator instruction and reviewed artifact hashes, then append browser-preflight and result-observation events. Only that evidence may use the word **verified**.

### Specialist deployment decision

Do **not** add another generic lyricist or arranger. The smallest additions that materially improve the system are:

1. **Audio QA / A&R Listener** — mandatory after generation; actual playback plus evidence-backed KEEP/ITERATE/CUT review.
2. **Short-form Audio-Visual Director** — only for retained lead tracks; creates a draft hook board, storyboard, captions, accessibility notes, and clip timecodes; never publishes.
3. **Trauma-informed meditation safety editor** — conditional for meditation, sleep, breathwork-adjacent, grief, panic, or emotionally vulnerable briefs.
4. **DAM/release verifier** — only when a retained asset advances toward release; validates file identity, rights metadata, and the explicit release gate.
