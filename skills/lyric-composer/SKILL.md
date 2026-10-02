---
name: lyric-composer
description: Write and revise original, singable lyrics with human specificity, strong prosody, memorable hooks, fresh imagery, emotional progression, and controlled vocabulary. Use for songs, hooks, verses, choruses, toplines, lyric rewrites, and Suno Custom Mode lyrics.
version: 0.2.0
tags: [lyrics, songwriting, prosody, hooks, suno]
---

# Lyric Composer

## Standard

Write as a serious songwriter, not a rhyming text generator. The lyric must carry a distinct speaker, a scene, pressure, change, and a phrase worth singing twice.

## Drafting sequence

### 1. Find the song's irreversible sentence

For a requested 2–4-line hook, start from a charged spoken/social action instead. Skip full-song section checks, Verse 2 tests and fixed abstraction quotas; preserve the requested form.

Complete: **"By the end, the speaker can finally say ______, but could not say it at the start."**

If that sentence is weak, the song has no turn. Fix the premise before polishing lines.

### 2. Choose one image system

Use 3–5 related concrete images across the song: objects, weather, rooms, roads, body sensations, machines, ritual actions. Let them evolve. Do not switch metaphor universes every line.

Prefer:
- an object with history;
- a verb that changes the object;
- sensory detail the listener can picture;
- one surprising but inevitable comparison.

Reject generic abstractions unless earned by detail: destiny, forever, broken, shadows, light, soul, fire, rise, scars, journey, dream.

### 3. Design the section jobs

- **Verse 1:** place, speaker, friction. Specific nouns; low melodic density.
- **Pre-chorus:** narrow options and increase pressure. Shorter syntax or rising vowels.
- **Chorus:** emotional thesis and title hook. Simpler language, wider vowels, repeatable contour.
- **Verse 2:** consequence or new evidence, not Verse 1 paraphrased.
- **Bridge:** reveal, reversal, cost, or changed point of view.
- **Final chorus:** same hook with changed meaning; add only what the turn earned.

Not every song needs every section. Structure serves the emotional mechanics.

### 4. Engineer prosody

For parallel lines:
- keep stressed beats aligned even if syllable counts differ by one;
- put open/singable vowels on held notes;
- avoid dense consonant clusters at fast tempos;
- make important words land on strong beats;
- read aloud at the intended pulse and mark every stumble.

Use a blend of perfect rhyme, family rhyme, assonance, consonance, and internal echo. Perfect end-rhyme on every line usually sounds juvenile. Never invert normal speech just to rhyme.

### 5. Control diction and coolness

"State of the art" does not mean obscure thesaurus language. Use exact contemporary diction, clean syntax, and one or two high-voltage words whose sound and meaning justify them.

A strong vocabulary choice:
- belongs to the speaker;
- can be sung cleanly;
- sharpens the image or emotional action;
- feels inevitable after hearing it, not decorative.

### 6. Build the hook

A hook should pass all four:
1. understandable on first listen;
2. emotionally charged after the verses;
3. phonetically satisfying to repeat;
4. distinct enough to title the song.

Draft 8–12 hook fragments privately. Keep the best one; do not show the user the entire scratch pile.

## Suno formatting

Use structural tags sparingly:

```text
[Intro - sparse]
[Verse 1 - intimate]
[Pre-Chorus - building]
[Chorus - open, harmonized]
[Verse 2]
[Bridge - stripped]
[Final Chorus - full lift]
[Outro - close and unresolved]
```

Keep 1–3 performance directions per section. Too many bracket tags compete.

Guide pronunciation only where needed:
- spell out numbers and acronyms;
- respell unusual names phonetically;
- use hyphens or vowel extensions only for intentional delivery.

## Revision passes

1. **Truth:** remove any line the speaker would never actually say.
2. **Specificity:** replace weak abstractions with images/actions where the requested form needs them.
3. **Architecture:** confirm every section changes pressure or knowledge.
4. **Prosody:** speak/sing aloud; repair stresses and mouthfeel.
5. **Hook:** test the title phrase in isolation and, when a full song exists, after Verse 2.
6. **Compression:** cut setup words, repeated explanations, and adjective stacks.
7. **Originality:** remove phrases that resemble known lyrics or named-artist signatures.

## Hard vetoes

- imitation of a named artist or cloned voice;
- borrowed lyric fragments or near-paraphrases;
- fake profundity that cannot be pictured;
- unearned key-change language such as "I rise" without an actual scene/turn;
- verse two that only restates verse one;
- bridge used as a random metaphor dump;
- grammatical distortion for rhyme;
- every line at the same emotional intensity.

## Delivery format

Return:
- title;
- one-sentence premise;
- lyrics with section tags;
- short craft note: hook, image system, emotional turn, pronunciation risks.

Do not preface the lyric with a long explanation.

## Shared fundamentals and provider boundary

Read the relevant modules in `docs/MUSIC-FUNDAMENTALS.md`, then `docs/PROVIDER-CAPABILITIES.md` and `docs/MUSIC-FACTORY-CONTRACT.md` when selecting tools or executing production. Canonical public source: https://github.com/frankxai/agentic-music-producer-os. The craft precedes the provider packet.

Suno v6 is the documented baseline checked 2026-10-01; capture the actual account model, settings, limits and credit cost before operating. No official public generation API was verified. Preserve the approved lyrics across adapters. Score/text analysis and a prompt review do not prove audio quality. Record real listening and measurements separately; keep unknown values null. Personal preferences and artist canon remain in their owner project.

Resolve `docs/...` paths from the repository root, not from the skill folder. If using only this skill outside a checkout, read the same named documents from the canonical public source.
