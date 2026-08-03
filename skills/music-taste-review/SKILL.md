---
name: music-taste-review
description: Score and revise a song, lyric, meditation, or Suno packet against a strict human-quality bar before spending generation credits. Use for A&R review, draft critique, prompt QC, keep/cut decisions, and pre-Suno validation.
version: 0.1.0
tags: [music, taste, review, quality, ar]
---

# Music Taste Review

Review the artifact against its own brief, not against generic commercial taste. Be exacting without replacing the creator's intent.

## Hard vetoes

Any veto blocks generation until fixed:
- named-artist imitation, voice cloning, or borrowed lyrics;
- no coherent listener/use case or emotional contract;
- contradictory style/lyrics/dynamic directions;
- meditation medical claims, coercive language, unsafe breathing, or trauma excavation;
- placeholder/empty required fields;
- fabricated generation data or unverifiable claims;
- unreadable meter or pronunciation failure in the central hook.

## Weighted score (100 points)

| Axis | Weight | Question |
|---|---:|---|
| Emotional truth | 18 | Does it reveal a specific human pressure and change rather than announce a mood? |
| Originality/specificity | 16 | Are images, diction, and sonic decisions distinct without imitation? |
| Hook/memory | 14 | Is there one phrase or motif the listener carries out? |
| Structure/arc | 14 | Does each section change pressure, knowledge, energy, or perspective? |
| Prosody/performance | 12 | Do stress, vowels, syntax, breath, and tags support singing/speaking? |
| Sonic coherence | 12 | Do rhythm, harmony, timbre, vocal persona, production, and exclusions serve one thesis? |
| Restraint/negative space | 7 | Was unnecessary language, instrumentation, and instruction removed? |
| Platform readiness | 7 | Is the Suno packet complete, clear, non-contradictory, and executable? |

For meditation, replace Hook/memory with **Guidance/pacing**: agency, one instruction at a time, silence, speakability, and safe return.

## Scoring anchors

- **9–10:** specific, inevitable, surprising; craft disappears into the experience.
- **8–8.9:** strong and executable with small, named improvements.
- **7–7.9:** competent but generic, flat, crowded, or emotionally under-earned.
- **5–6.9:** major structural or language problem; revise before generation.
- **<5:** wrong premise or unresolved safety/originality issue; rebuild.

## Pass rule

Pass only when:
- weighted score is at least 85/100 for songs/instrumentals or 90/100 for meditations;
- every axis is at least 7.5/10;
- no hard veto remains.

Do not inflate numbers to move the workflow along. Credits are cheaper than bad taste only once; repeated weak generation wastes both.

## Review procedure

1. Restate the creative thesis in one sentence.
2. Name the strongest moment and why it works.
3. Name the single largest failure relative to the brief.
4. Score each axis with one evidence sentence.
5. Give at most five revisions, ordered by expected impact.
6. Apply the revisions when authorized by the orchestration workflow.
7. Re-score the changed artifact; do not reuse the old score.

## First-listen review after generation

Review both generated takes against the same packet:
- opening 15 seconds: immediate identity or generic preamble;
- hook arrival and recall;
- lyric intelligibility/pronunciation;
- section contrast and energy curve;
- vocal persona consistency;
- arrangement masking/crowding;
- ending quality;
- one standout accident worth preserving.

Choose: `KEEP`, `ITERATE`, or `CUT`.
- `KEEP`: thesis landed; only downstream polish remains.
- `ITERATE`: a specific section or one dominant variable can be repaired.
- `CUT`: premise/identity missed; regenerate from revised brief, not cosmetic edits.

Never claim LUFS, dynamic range, pitch accuracy, or spectral balance without actual audio-analysis output.

## Output template

Write `review.md` with the following machine-checked lines. Each required axis must have an evidence sentence and a score of at least `7.5/10` for PASS.

```text
VERDICT: PASS | REVISE | BLOCK
THESIS: ...
STRONGEST MOMENT: ...
PRIMARY FAILURE: ...
SCORE: 87/100
HARD VETOES: none | ...
AXIS: emotional_thesis 8.8/10 | EVIDENCE: specific pressure and turn are visible in the chorus.
AXIS: originality 8.2/10 | EVIDENCE: image system and sonic object are specific and non-imitative.
AXIS: imagery_specificity 8.0/10 | EVIDENCE: concrete sensory detail carries the emotional change.
AXIS: prosody_singability 8.1/10 | EVIDENCE: stressed syllables, vowels, and breaths scan in the hook.
AXIS: section_contrast 8.3/10 | EVIDENCE: every section changes pressure, knowledge, or energy.
AXIS: hook_strength 8.4/10 | EVIDENCE: one recallable phrase/motif arrives cleanly.
AXIS: arrangement_fidelity 8.0/10 | EVIDENCE: sonic plan, dynamics, and exclusions serve the thesis.
AXIS: release_readiness 8.0/10 | EVIDENCE: Custom packet is complete, coherent, and executable.
REVISIONS:
1. ...
```
