# Composer Factory

Score-first extension of Agentic Music Producer OS.

```text
brief → motif/form → catalog/<slug>/score.txt
                  → MusicXML MIDI ABC piano-sheet guitar-tab
                  → live | sample-library | Lyria 3 | Suno | preview
```

The score is the work. Generative audio is a performance of the brief.

## Commands

```bash
python scripts/score_cli.py init --title "Window Latch" --kind piano --key "D minor" --tempo 68
python scripts/score_cli.py validate catalog/window-latch/score.txt
python scripts/score_cli.py compile catalog/window-latch/score.txt --preview --mp3
python scripts/score_cli.py catalog
python scripts/lyria_cli.py status
```

## First works

- `catalog/window-latch/` — 16-bar piano miniature
- `catalog/window-latch-chamber/` — 8-bar string quartet study

## Audio honesty

Local `--preview --mp3` is a hearing sketch. Highest-emotion audio is a human playing the sheet. Highest simulation is MIDI through Pianoteq/NotePerformer/a real library. Lyria 3 and Suno are separate lanes and will drift from the notation.

Lyria 3: `lyria-3-clip-preview` (30s) and `lyria-3-pro-preview` (full, MP3 or WAV, 44.1 kHz stereo). All Lyria audio is SynthID-watermarked. Custom lyrics/timestamps are supported; MusicXML is not.
