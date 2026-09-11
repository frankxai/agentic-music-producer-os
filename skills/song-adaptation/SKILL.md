---
name: song-adaptation
description: Rewrite a song onto an existing metrical skeleton — contrafacts, parodies, translations, theme rewrites, and revisions of the operator's own catalog. Maps syllables, stress, and held-vowel positions from a source, then writes entirely new lyrics that sing cleanly over that shape. Use for "rewrite this song about X", "make a parody of", "new lyrics to the same tune", "translate this song", or reworking an existing track.
version: 0.1.0
tags: [lyrics, adaptation, parody, contrafact, prosody, suno]
---

# Song Adaptation

Writing to an existing metrical skeleton is a distinct discipline from writing a song from
scratch. The melody is fixed, so the lyric has almost no freedom: stress positions, held notes,
and breath points are all pre-decided. Every craft decision moves into word choice.

This skill covers four cases with different rights postures. Establish which one applies before
writing a line.

---

## Case classification — do this first

| Case | Source | Rights posture |
|---|---|---|
| **A. Own catalog** | The operator's own song | Unrestricted. Retaining original lines is a craft choice. |
| **B. Public domain** | Verified PD melody and text | Unrestricted, but verify PD status by jurisdiction and publication date — do not assume. |
| **C. Contrafact** | New melody written to the *shape* of a third-party song | Permitted. Nothing of the source ships. |
| **D. Third-party parody** | A recognisable third-party song | Constrained. See below. Never generated as an imitation of the original recording. |

### Case D constraints

For third-party material, the following are hard vetoes and override any user request to the
contrary. State them once, plainly, and proceed with the compliant version rather than stalling:

- **No original lyric lines survive.** Not a couplet, not a hook fragment, not a "recognisable
  tag". Structural similarity is the point of a parody; reproduced text is the liability.
  Recognition comes from meter, rhyme scheme, and vowel shape — which is enough.
- **No named-artist, named-song, or "sounds like" language reaches the Suno style field.** The
  musical direction is written from attributes, exactly as `suno-ai-mastery` requires.
- **No voice cloning, persona imitation, or reference-audio upload of the source recording.**
- **The output is a new work that shares a metrical skeleton**, not a derivative of a recording.

The pop-culture instinct to "keep a few original lines for recognisability" is precisely the
part that does not survive contact with a rights review. Drop it for Case D; it is free in Case A.

---

## Map the skeleton before writing anything

Do not draft lyrics until the skeleton exists as a written artefact. Adaptation written by ear
fails at exactly the moments that matter — the held notes.

For each section of the source, record:

1. **Line count** per section, and the section order.
2. **Stress count** per line — mark stressed syllables, do not just count syllables.
3. **Syllable count** per line, as a secondary constraint.
4. **Rhyme scheme**, with the rhyme *sounds* noted, not just the letters.
5. **Held or sustained notes** — which syllable, how long, and **which vowel**.
6. **Breath points** — where the singer must stop.
7. **Pickup notes** — lines that start before the downbeat.

Write it as a table:

```text
SECTION   LINE  STRESS  SYLL  RHYME  HELD                    BREATH
Verse 1   1     4       9     A      —                       end
Verse 1   2     4       8     B      syll 8, "ay", 2 beats   end
Verse 1   3     4       9     A      —                       end
Verse 1   4     3       7     B      syll 7, "ay", 4 beats   end + 2 beats
Chorus    1     3       6     C      syll 6, "oh", 4 beats   end
```

The `HELD` column governs everything. Those are the only syllables the listener will fully
register, and the only ones where a wrong vowel is unrecoverable.

---

## Fitting rules

**Stress alignment is the contract.** Stressed syllables must land on the same beats as the
source's stressed syllables. Everything else is negotiable.

- Syllable count may flex by one or two, provided the extra syllables are unstressed and sit
  between stresses, not on them.
- On a held note, **match the vowel sound of the source**, not the word class. A source holding
  "LOOOVE" (an "uh" going to "v") takes "BLOOOD" or "ENOOOUGH" far better than "LIFE".
- Monosyllabic substitution in hooks and tags preserves rhythm perfectly and is the highest-yield
  move available: `Crime → Code`, `Snake → Noose`, `Heart → Chart`.
- Pickup lines must keep their pickup. Adding a syllable before the first stress collapses the
  phrase into the previous bar.
- Never invert word order to reach a rhyme. If the rhyme will not come naturally, change the
  rhyme sound — you are choosing it, the source only chose the scheme.

**Reverse-engineer to a fixed line.** When a specific line must appear at a specific place
(usually the title or a punchline), place it first and work the rhyme scheme *backwards* from it
to set it up. Writing forward and hoping to arrive at the line is how adaptations die in the
last verse.

---

## Concept before craft

An adaptation needs a concept strong enough to sustain a full song, not a single joke that
exhausts itself by the second verse. Test the concept against the source's structure:

- Does it have a **turn** available at the bridge? The bridge is where the source shifts
  perspective; the adaptation must have something to shift *to*.
- Does it have **two distinct verses' worth** of material, or does verse two just restate verse one?
- Does the **title/hook** work as the emotional centre, not just the setup?

Generate raw material first — puns, technical vocabulary, images, phrases from the target domain
— in bulk, before fitting anything. Then select into the skeleton. Fitting while inventing
produces lines that scan but say nothing.

---

## Translation adaptations

When adapting across languages:

- Match stress positions in the target language's own prosody; do not carry the source's stress
  pattern into a language that stresses differently.
- Held notes need open vowels in the *target* language.
- Preserve the emotional function of each section, not the literal content.
- Apply `suno-prompt-architect/reference/phonetic-control.md` to every foreign-language line
  before it enters a packet.

---

## Verification pass

Before the packet goes to the taste gate:

1. **Sing the new lyric against the source's pulse**, line by line. Every stumble is a defect.
2. **Check every held note** against the `HELD` column — vowel and duration.
3. **Confirm no source text survives** (Case D): search the draft for any three-word sequence
   from the original. Three words is the working threshold.
4. **Confirm the style field is attribute-only** — no artist, song, album, or label names.
5. **Confirm the adaptation reads as a work**, not as a list of substitutions. Read it with no
   knowledge of the source: does it hold?

Item five is the one adaptations fail. If the new lyric only makes sense as a commentary on the
original, it is not finished.

---

## Handoff

- Lyric craft, imagery, and hook quality: `lyric-composer`.
- Rhyme, meter, and prosody detail: `lyric-composer/reference/rhyme-meter-prosody.md`.
- Musical direction for the new recording: `suno-ai-mastery` — write it from scratch, from
  attributes. Do not describe the source recording.
- Packet assembly: `suno-prompt-architect`.
- Quality gate: `music-taste-review`. The named-artist-imitation and borrowed-lyric vetoes apply
  in full.

## Delivery format

Return:

1. case classification (A/B/C/D) and any constraint applied;
2. the skeleton table;
3. title and one-sentence concept;
4. full adapted lyrics with section tags;
5. a craft note covering held-note vowel choices, the hook substitution, and any line where
   stress alignment was traded for meaning.
