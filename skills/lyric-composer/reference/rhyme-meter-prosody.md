# Rhyme, Meter, and Prosody

Technical reference behind `lyric-composer` step 4. Load when a lyric scans badly, when rhyme
sounds juvenile or lazy, or when a hook will not sit on the beat.

---

## Rhyme taxonomy

Ordered from tightest to loosest. The craft is in the **blend**, not in any single type.

| Type | Definition | Example | Effect |
|---|---|---|---|
| Perfect | Identical vowel and following consonants | lean / mean | Closure, resolution, finality |
| Family | Same vowel, related consonant family (voiced/unvoiced pairs) | crate / braid | Near-closure with slight lift |
| Assonance | Same vowel, different consonants | had / glass | Openness, forward motion |
| Consonance | Different vowel, same consonants | scene / when | Tension, unease |
| Additive | Rhyme plus an extra syllable | fine / defined | Conversational, slightly off-balance |
| Subtractive | Rhyme minus a syllable | remain / rain | Compression, urgency |
| Para-rhyme | Both framing consonants match, vowel shifts | tell / tall | Cold, unresolved |
| Identity | Same word repeated as rhyme | stay / stay | Insistence — or laziness. Rarely neutral |

**The rule of thumb:** perfect rhyme where the emotion resolves, everything else where it does
not. A song that resolves every line has no unfinished business, and unfinished business is why
listeners stay.

All-perfect reads as nursery rhyme. All-slant reads as a writer avoiding the work. The blend is
the signature.

### Rhyme placement

- **End rhyme** — the default; carries structure.
- **Internal rhyme** — inside a line. Adds density without adding structure.
  `We pruned the lies from bleeding trees / distilled the storm from entropy`
  ("lies" against "bleeding"/"trees"; "trees" against "entropy")
- **Chain rhyme** — line-end rhymes with the *next* line's interior. Pulls the listener forward
  across the line break; the strongest anti-stall device in a slow verse.
- **Cross rhyme** — an interior word rhymes with the previous line's ending. Pulls backward,
  creating a sense of return. Good in a final chorus.

### Scheme selection

```text
AABB   Closed, comic, folk. Resolves too fast for serious material unless deliberately plain.
ABAB   Balanced, open. The workhorse for verses that need to move.
ABCB   Ballad scheme. Only line 4 lands — maximum weight on the payoff line.
AAAA   Obsessive, incantatory. Powerful in short bursts, exhausting past four lines.
XAXA   Only alternating lines rhyme. Nearly conversational; strongest for narrative verses.
Free   No scheme. Requires very strong meter and imagery to hold together.
```

Chorus and verse should not share a scheme. Different schemes are half of what makes a chorus
feel like a chorus.

---

## Meter

Music does not care about syllable counts. It cares about **where stresses land relative to the
pulse.**

### The operative rules

1. Parallel lines should share a **stress count**, even when syllable counts differ by one or two.
2. Important words go on strong beats. If the emotional word of a line lands on a weak beat, the
   line is wrong regardless of how it reads on the page.
3. Unstressed syllables are compressible — the singer absorbs them. Stressed syllables are not.
4. Line endings are where meter breaks are heard. Mid-line irregularity is nearly invisible.

### Scansion procedure

Mark the line, do not count it:

```text
The HOOD-ie's STILL on the HOOK by the DOOR        4 stresses, 10 syllables
And the KETT-le still KNOWS how you TOOK it be-FORE 4 stresses, 13 syllables
```

Both work. They share a stress count; the second simply moves faster through its weak syllables.
Matching the syllable counts here would have made the second line worse.

### Feet, when you need the vocabulary

```text
Iamb     da-DUM    the DOOR         forward motion, most natural in English
Trochee  DUM-da    MORN-ing         declarative, front-loaded, good for hooks
Anapest  da-da-DUM in the DARK      rolling, propulsive, dance-adjacent
Dactyl   DUM-da-da CAR-ry me        falling, elegiac
Spondee  DUM-DUM   COLD LIGHT       weight, arrest, impact — use to stop motion
```

A spondee in a run of iambs is the cheapest way to make one word land.

### Deliberate breaks

Break meter on purpose, once or twice per song, at the moment of highest emotional pressure.
The break is heard as intensity. Break it three or more times and it is heard as incompetence.

---

## Prosody: lyric and music agreeing

Prosody is the alignment of *linguistic* stability with *musical* stability. Get it wrong and a
technically clean lyric feels off, and nobody can say why.

| Emotional state | Melody | Rhyme | Harmony | Phrase ending |
|---|---|---|---|---|
| Resolution, peace, certainty | Settles on chord tones, descends | Perfect | Cadences resolve | On a strong beat, complete |
| Longing, doubt, incompletion | Wanders, ends on a non-chord tone | Slant, para | Unresolved, suspended | Off-beat, phrase runs over the bar |
| Building pressure | Rises stepwise, narrows range | Fewer rhymes, shorter lines | Pedal tone under moving chords | Truncated |
| Release | Widens, jumps up, opens vowels | Return to perfect rhyme | Resolution finally arrives | Long-held |

Standard registers: verse melody sits low and narrow, chorus opens up and sits higher. Invert it
only when the song's meaning requires the chorus to be a collapse rather than a lift — that
inversion is a strong device precisely because it is rare.

### Vowel prosody

- Open vowels (ah, oh, oo, ay) carry held notes and high notes.
- Closed vowels (ih, uh, er) choke at volume and pitch.
- The peak note of the chorus should land on an open vowel. If it does not, change the word.
- Dark vowels (oo, oh) read as interior and heavy; bright vowels (ee, ay) read as exposed and light.
  Match the vowel color to the emotional temperature.

### Consonant prosody

- Plosives (p, t, k, b, d, g) cut and punctuate — good on downbeats.
- Sibilants (s, sh, z) hiss under compression — avoid stacking them in a loud chorus.
- Nasals and liquids (m, n, l, r) sustain — good for lines that need to flow.
- Three or more consonants between vowels will slur above ~120 BPM.

---

## Diagnostic checklist

When a lyric is technically fine but sounds wrong, check in this order:

1. Does the emotional word of each line land on a strong beat?
2. Do parallel lines share a stress count?
3. Does the rhyme density change between verse and chorus?
4. Does the peak note sit on an open vowel?
5. Does anything resolve that should not have resolved yet?
6. Read it aloud at tempo — where does your mouth stumble?

Item six catches more than the other five combined.
