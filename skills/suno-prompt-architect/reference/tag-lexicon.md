# Structural and Performance Tag Lexicon

The full vocabulary, plus the budget that keeps it useful.

**Doctrine first:** tags are a scarce control signal, not decoration. Every additional tag in a
section dilutes the ones already there. The model does not obey ten tags harder than three — it
averages them into a bland middle. Cap at **one structural tag plus one to three cues per
section**, and prefer cues that no other part of the packet already states.

If a cue is already carried by the STYLE field, do not repeat it as a tag. Redundancy costs
control.

---

## Structural tags

Reliable, and the backbone of every packet:

```text
[Intro]  [Verse]  [Verse 1]  [Verse 2]  [Pre-Chorus]  [Chorus]  [Post-Chorus]
[Hook]  [Refrain]  [Bridge]  [Interlude]  [Breakdown]  [Build-up]  [Drop]
[Instrumental]  [Instrumental Break]  [Solo]  [Guitar Solo]  [Outro]  [End]
```

Notes:

- `[End]` after the final section reduces trailing improvisation and unwanted fades.
- `[Silence]` is inconsistently honoured; get silence through arrangement language in STYLE
  ("full stop before the final chorus") instead.
- Numbering verses (`[Verse 1]`, `[Verse 2]`) improves section differentiation more than any
  performance cue does.

## Section length cues

Combine with a structural tag when proportion matters:

```text
[Intro - 4 bars]   [Bridge - short]   [Outro - 8 bars, fading]
```

Bar counts are advisory. Treat them as a bias, not a contract.

---

## Vocal performance cues

```text
Delivery:   [Whispered] [Spoken Word] [Sung] [Belted] [Shouted] [Falsetto] [Head Voice]
Texture:    [Breathy] [Raspy] [Smooth] [Gritty] [Warm] [Strained] [Clear]
Articulation:[Staccato] [Legato] [Melismatic] [Clipped] [Conversational] [Declamatory]
Ensemble:   [Harmonies] [Two-Part Harmony] [Octave Double] [Choir] [Call and Response]
            [Backing Vocals] [Unison] [Gang Vocals] [Ad-libs]
Presence:   [Close Mic] [Distant] [Doubled] [Layered] [Single Take]
```

Use **one** delivery cue and at most one ensemble cue per section. Delivery cues in adjacent
sections should differ — that difference is where perceived dynamics come from.

## Energy and dynamics cues

```text
[High Energy] [Low Energy] [Building Energy] [Falling Tension] [Explosive]
[Emotional Climax] [Gradual Swell] [Orchestral Swell] [Quiet Arrangement]
[Stripped] [Full Lift] [Half-Time] [Double-Time] [Slow Down] [Accelerando]
```

## Atmosphere cues

```text
[Melancholic] [Euphoric] [Nostalgic] [Aggressive] [Dreamy] [Intimate]
[Dark Atmosphere] [Hopeful] [Tense] [Serene] [Triumphant]
```

Atmosphere belongs in STYLE far more than in tags. Use these only when one section departs from
the song's overall emotional register — that is the entire point of the tag.

## Instrumentation cues

```text
[Piano Only] [Acoustic Guitar] [Strings Enter] [Drums Enter] [Drums Out]
[Bass Drop] [Horn Section] [No Percussion] [A Cappella] [Full Band]
```

The subtractive ones (`[Drums Out]`, `[No Percussion]`, `[A Cappella]`) are the highest-value
tags in this entire lexicon. Removal creates contrast more reliably than addition does.

## Vocal identity

```text
[Female Vocals] [Male Vocals] [Androgynous Vocals] [Duet] [Child Vocals]
```

One identity per song. Switching mid-song usually degrades both. Detailed persona work belongs
in the STYLE field, not here.

## Sound effects

```text
[Vinyl Crackle] [Rain] [Thunder] [Static] [Applause] [Crowd] [Tape Hiss]
[Room Tone] [Footsteps] [Wind]
```

Honoured inconsistently and prone to eating headroom. Prefer texture language in STYLE
("dusty noise floor", "room tone under the verse") unless the effect is a structural event.

---

## Composition rules

1. **One structural tag per section, always.**
2. **One to three cues, never more.** Three is already a lot.
3. **Never contradict.** `[Calm]` with `[Aggressive]`, `[Whispered]` with `[Belted]`,
   `[Quiet Arrangement]` with `[Full Band]` — each pair cancels to mush.
4. **Do not restate the STYLE field.** If STYLE says the whole track is intimate, do not tag
   `[Intimate]` on every section; tag the one section that is *not*.
5. **Change cues between adjacent sections.** Identical cues across verse and chorus produce a
   flat song, whatever the STYLE field claims.
6. **Reinforce only the top-priority cue** in both STYLE and tags. Reinforcing everything
   reinforces nothing.
7. **Put no production prose between lyric lines.** Cues live in the section heading.

---

## Worked example

```text
[Intro - piano only, 4 bars]

[Verse 1 - close, conversational]
...

[Pre-Chorus - building energy]
...

[Chorus - belted, harmonies]
...

[Verse 2 - drums enter, restrained]
...

[Bridge - a cappella, whispered]
...

[Final Chorus - full lift, gang vocals]
...

[Outro - piano only, hard stop]
[End]
```

Eleven cues across eight sections. Every section differs from its neighbour. Nothing repeats
what STYLE already says. That is the target density.
