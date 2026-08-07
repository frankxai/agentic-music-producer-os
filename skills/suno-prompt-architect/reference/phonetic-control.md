# Phonetic Control for AI Vocalists

The single most expensive class of failure in AI music generation: pronunciation is decided at
generation time and **cannot be repaired afterwards**. A mispronounced hook word forces a full
regeneration and burns a Create action. Every other flaw — arrangement, energy, mix — can be
addressed by extend, replace-section, or remaster. This one cannot.

Apply this reference to the lyrics field **before** the packet reaches the taste gate.

---

## The model reads graphemes, not meaning

An AI vocalist has no lexicon and no proper-noun knowledge. It infers phonemes from spelling
patterns in its training distribution. When spelling is ambiguous, it picks the statistically
common reading — which is often wrong for names, coinages, loanwords, and technical terms.

Therefore: **spell for the mouth, not for the page.** The lyrics field is a performance score,
not a manuscript.

---

## Risk triage

Scan every lyric for these categories and fix in this order:

| Risk | Failure rate | Fix |
|---|---|---|
| Invented proper nouns and brand names | Highest | Respell phonetically; test in a short clip |
| Loanwords and non-English words | High | Respell in the target language's phonetics or in English approximation |
| Acronyms and initialisms | High | Space or hyphenate the letters |
| Numerals, dates, times, ratios | High | Spell out in words |
| Homographs (read, live, wind, bow, tear) | Medium | Rephrase the line to disambiguate |
| Words with silent or irregular letters | Medium | Respell |
| Symbols (&, %, /, +, ×) | Medium | Spell out |
| Dense consonant clusters at fast tempo | Low but audible | Rewrite the line |

---

## Respelling

Write the sound, keep the meaning:

```text
through        → thru
Arcanea        → Ar-KAY-nee-uh
Nous           → Noose
Lumina         → LOO-min-uh
Gaudí          → Gow-DEE
Fuerteventura  → Fwer-tay-ven-TOO-ra
segue          → seg-way
epitome        → ee-PIT-oh-mee
```

Rules:

- Hyphens mark syllable boundaries and are heard as syllable boundaries — do not hyphenate a
  word you want sung as one gesture.
- Capitalising the stressed syllable is a reliable stress cue.
- Only respell words that actually fail. Wholesale respelling degrades everything else.

## Numbers, acronyms, symbols

```text
24/7      → twenty four seven
2026      → twenty twenty six
3AM       → three A M
AI        → A-I        (or "ay-eye" if the model still fuses it)
OKR       → O K R
100%      → one hundred percent
&         → and
±         → plus or minus
```

Never leave a digit in a lyrics field. There is no upside.

---

## Delivery control

These are the only reliable typographic performance cues. Everything else is noise.

| Notation | Effect | Use when |
|---|---|---|
| `ALL CAPS` | Louder, more forceful attack | One or two words per section, at the emotional peak |
| `lo-o-ove` | Sustained note, melisma across the vowel | The note is genuinely held in the arrangement |
| `ne-e-ed` | Emotional stretch, shorter than a full melisma | A single high-value word |
| `I... need... you` | Deliberate pauses between phrases | Spoken-leaning delivery, dramatic bridge |
| `word—` (em dash) | Clipped cutoff | Abrupt line endings, breath edits |
| `(word)` | Backing-vocal or ad-lib treatment | Call-and-response, doubled hooks |

Budget: **no more than three delivery marks per section.** Past that, the model averages them
into a generically theatrical performance and the intended peak disappears.

## Vowel placement on held notes

Open vowels sustain cleanly. Closed vowels and diphthongs collapse.

```text
Sustains well:  ah (father), oh (go), oo (blue), ay (day), eye (time)
Sustains badly: ih (bit), uh (but), er (bird), ee at high volume, any word ending in a stop
```

If the arrangement holds a note and the lyric lands a closed vowel there, change the word
rather than the melody. This is the difference between a hook that carries and one that chokes.

---

## Consonant load

At tempos above roughly 120 BPM, three or more consonants between vowels will slur:

```text
"strengths that stretched" → slurs
"the strength it took"     → clean
```

Read the line at the intended pulse. If your own mouth stumbles, the model will too.

---

## Multilingual lines

- Mark language changes with a section cue rather than mid-line.
- Respell the foreign phrase in the phonetics of the *singing* language, not the source language.
- Keep the foreign phrase in a low-consonant, open-vowel position — usually a held line ending.
- Never mix two scripts inside one line.

---

## Test-before-spend protocol

When a packet contains more than two high-risk items:

1. Extract the riskiest 4–8 bars into a throwaway packet.
2. Generate that fragment once, at short length, before committing the full Create action.
3. Listen only for pronunciation — ignore arrangement entirely.
4. Correct the lyrics file, then run the real packet.

This costs one cheap action and routinely saves two expensive ones.

---

## Pronunciation notes format

Every packet's `PRONUNCIATION NOTES` block lists only what was changed and why:

```text
Arcanea      → Ar-KAY-nee-uh    (invented proper noun, stress on second syllable)
2026         → twenty twenty six (numeral)
"live" (V2)  → rewrote line to "the life we"  (homograph, wrong reading likely)
"stay" (hook) → sta-a-ay        (held 3 beats, open vowel confirmed)
```

If the block is empty, state that explicitly rather than omitting it — an empty block is a
claim that the lyrics were checked, and that claim should be visible.
