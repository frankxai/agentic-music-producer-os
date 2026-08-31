---
name: score-composer
description: Compose original piano, chamber, and orchestral works as a score canon (compact DSL, MusicXML, MIDI, ABC, piano sheets, guitar tabs), then route to preview audio, Lyria 3, Suno, or live playing. Use for compose, sheet music, tabs, orchestra, piano works, notation, MusicXML.
version: 0.1.0
tags: [music, composition, piano, orchestra, musicxml, midi, tabs, lyria]
---

# Score Composer

Use this when the work must exist as **music**, not only as a generative MP3.

The score is the canon. Lyria and Suno are performance/promo lanes. Sheets and tabs compile from the score. Never transcribe a generative MP3 and call that the work.

## Trigger

Activate when the user asks to:
- compose piano, chamber, orchestra, or guitar works;
- produce high volume of actual pieces;
- write sheets, tabs, melody/rhythm in correct formats;
- generate with Google Lyria next to Suno or live playing;
- get a high-quality MP3 from simulation or human emotion.

## Pipeline

```text
brief → motif/form → compact score.txt → validate → compile
     → MusicXML / MIDI / ABC / piano sheet / guitar tab
     → choose ONE audio lane
```

### 1. Write the composition, not the prompt

Before any generation:

- **Listener moment** and emotional contract.
- **Motif:** 3–6 notes the piece cannot lose.
- **Form:** bar counts, not vibes.
- **Key, meter, tempo, negative space.**
- One image system. One turn.

Then encode the piece in the compact DSL at:

`~/agentic-music-producer-os/catalog/<slug>/score.txt`

```text
@title Window Latch
@kind piano
@key D minor
@time 4/4
@tempo 68
@thesis ...
@motif descending A-F-D
@form 16-bar miniature

[Piano]
1 RH: A4q F4q D4h
1 LH: D3h A2h
```

Durations: `w h q e s` plus optional `.`  
Rests: `rq` `rh`  
Chords: `[D5A4]q`  
Voices: `RH` `LH` `P` for monophonic parts.

### 2. Validate and compile

```bash
python ~/agentic-music-producer-os/scripts/score_cli.py validate catalog/<slug>/score.txt
python ~/agentic-music-producer-os/scripts/score_cli.py compile catalog/<slug>/score.txt --preview --mp3
```

Required artifacts:

| File | Job |
|---|---|
| `.musicxml` | Canon for MuseScore / Dorico / Sibelius |
| `.mid` | Live play, DAW, sample library |
| `.abc` | Compact interchange |
| `.piano.txt` | Immediate readable piano sheet |
| `.tab.txt` | Guitar melody tab |
| `lyria-prompt.md` | Timed Lyria packet |
| `suno-bridge.md` | Existing Suno lane, one Create only |

Publication-quality PDF: open the MusicXML in MuseScore 4 and export. Do not claim a PDF exists unless MuseScore or LilyPond actually wrote it.

### 3. Audio lanes (pick one; do not blur them)

1. **Live human** — highest emotion. Print the sheet or send MIDI to a keyboard.
2. **High simulation** — MIDI into Pianoteq / NotePerformer / Spitfire / MuseScore + good soundfont. This is the honest "highest quality simulation."
3. **Local preview MP3** — `--preview --mp3` additive piano. Proof of hearing only.
4. **Lyria 3** — Google generative performance. Audio is 44.1 kHz stereo. It will **not** match the score note-for-note.
5. **Suno** — promotional/vocal/commercial. Existing one-Create policy. Load `suno-prompt-architect` + `music-taste-review` first.

Lyria models:

- `lyria-3-clip-preview` — 30s MP3, iterate here first
- `lyria-3-pro-preview` — full piece, MP3 or WAV

```bash
python ~/agentic-music-producer-os/scripts/lyria_cli.py status
python ~/agentic-music-producer-os/scripts/lyria_cli.py packet catalog/<slug>/build/lyria-prompt.md --wav
# only after explicit "generate with Lyria" AND a Gemini key in the process
python ~/agentic-music-producer-os/scripts/lyria_cli.py generate catalog/<slug>/build/lyria-prompt.md --out catalog/<slug>/build --authorize
```

Never paste API keys. Load `GEMINI_API_KEY` from Infisical/registry. Never invent a take.

### 4. Volume factory

Greatest volume of *works* means many validated scores, not many unreviewed MP3s.

Cadence for a session:

1. Choose a series thesis (example: 12 piano nocturnes, one motif family).
2. Write 1 complete miniature (8–32 bars) per cycle.
3. Validate + compile before the next piece.
4. Keep only pieces whose motif, turn, and ending are distinct.
5. Batch-render MIDI later through the high-simulation lane.

```bash
python ~/agentic-music-producer-os/scripts/score_cli.py catalog
```

### 5. Taste for scores

Hard vetoes:

- no motif;
- bar lengths wrong;
- unplayable piano stretches or guitar melody off the instrument;
- named-artist imitation;
- claiming Lyria/Suno audio *is* the score;
- claiming concert-hall MP3 quality from the local preview synth.

A piece is done when:

- `validate` is clean;
- MusicXML + MIDI + sheet + tab exist;
- the ending is authored;
- the next move is one audio lane, named.

## Software map

| Need | Software | Format |
|---|---|---|
| Write / edit | this DSL + MuseScore 4 | `score.txt`, MusicXML |
| Piano sheets | MuseScore export PDF from MusicXML | MusicXML → PDF |
| Guitar tabs | compiler `.tab.txt` or Guitar Pro via MusicXML | ASCII tab, MusicXML |
| Live play | MIDI to keyboard / DAW | `.mid` |
| High simulation | Pianoteq, NotePerformer, Spitfire, FluidSynth+Salamander | MIDI → WAV/MP3 320k or WAV 24-bit |
| Promo vocal | Suno Custom Mode | existing OS |
| Promo/cinematic audio | Lyria 3 Pro WAV | 44.1 kHz stereo + SynthID watermark |

## Report

Return:

1. title + one-sentence thesis;
2. catalog path;
3. verified artifact paths only;
4. which audio lane is next;
5. no quality claim without a real file and, for "high quality," the actual renderer used.
