---
name: song-postproduction
description: "Everything after the take exists: authorized download, archival naming, objective measurement (loudness, dynamics, silence, energy arc), vocal transcription diffed against the written lyric, and an evidence-based first-listen review. Use for \"download it\", \"how did it come out\", \"review the take\", \"did it sing the words right\", or any post-generation step. Backend-agnostic — works for hosted and local takes alike."
version: 0.1.0
tags: [postproduction, download, review, measurement, transcription, archive]
---

# Song Post-Production

## The honest constraint

**I cannot hear audio.** Any statement about how a take sounds that is not backed by a
measurement or a transcript is fabrication, and `music-taste-review` treats fabricated
generation data as a hard veto.

The division of labor that actually works:

- **I bring evidence** — measured loudness and dynamics, the energy curve against the intended
  arc, silence and clipping, and a transcript of what the vocalist actually sang.
- **Frank brings judgment** — whether it moves him, whether the voice is right, whether the hook
  lands.

This is not a limitation to apologize around. Transcription catches the one defect class that no
amount of listening will let you *fix* — pronunciation is decided at generation time and survives
every extend, replace-section, and remaster. Measurement catches a flat arc that a first listen
will forgive and a tenth listen will not.

---

## 1. Download, with authorization

Download is a **separate authorization** from generation. One Create request does not imply a
download, and downloading both takes is two decisions, not one. Ask, then act.

Never fabricate a download. If the file did not land on disk, say so and name what blocked it.

## 2. Archive before touching

Into the run's session directory, never a scratch path:

```text
<session_dir>/audio/take-1--<slugified-title>.mp3
<session_dir>/audio/take-2--<slugified-title>.mp3
```

Record in `manifest.json` alongside the existing take record: local path, byte size, SHA-256, the
verified Suno URL/ID, and the exact visible model label. A local file with no provenance row is
not an asset — six weeks later nobody can say which prompt produced it.

## 3. Measure

```bash
python scripts/audio_probe.py <session_dir>/audio/take-1--<title>.mp3 \
  --session <session_dir> --take 1
```

Requires ffmpeg and ffprobe. No Python dependencies. Writes `probe-take-N.json` and
`probe-take-N.md` into the session and prints the summary.

What it returns and what each number is for:

| Measure | Reads on | Interpretation |
|---|---|---|
| Duration | Truncation | Well under the intended length means a failed or cut generation, not a short song. |
| Integrated LUFS | Level | Streaming platforms normalize around −14 LUFS. Far quieter is fine as a master; far louder will be turned down and lose punch. |
| True peak dBTP | Clipping | Above −1.0 risks inter-sample clipping on lossy playback. Above −0.1 is flagged. |
| Loudness range (LU) | Contrast | Under 3 LU means the sections do not differ in level — the dynamic arc did not happen, whatever the prompt asked for. |
| Leading / trailing silence | Trim | Dead air at the head is the most common release defect and the easiest fix. |
| Energy curve (0–10 per 0.5 s) | Arc | Compare directly against the packet's energy map. |
| Largest energy changes | Structure | Section-boundary candidates. Their timestamps should roughly match the intended form. |

**The arc check is the point.** Put the packet's energy map next to the measured curve. If the
brief said `Intro 2 → Verse 4 → Chorus 8 → Bridge 3 → Final 9` and the curve is flat at 7
throughout, the arrangement instruction did not land. That is an `ITERATE` with a known variable,
not a matter of taste.

## 4. Transcribe and diff

```bash
python scripts/audio_probe.py <take.mp3> --session <session_dir> --take 1 \
  --transcribe --lyrics <session_dir>/lyrics.md
```

Opt-in; needs a local ASR (`uv tool install faster-whisper`). Then diff the transcript against
`lyrics.md` and classify every mismatch:

| Mismatch | Meaning | Action |
|---|---|---|
| Hook word wrong | Unrecoverable in this take | Regenerate with a phonetic respelling. Do not attempt repair. |
| Proper noun mangled | Expected — highest failure category | Respell per `../suno-prompt-architect/reference/phonetic-control.md`, regenerate. |
| Number or acronym read wrong | Preventable defect that reached generation | Fix the lyrics file, and note that the pre-generation phonetic pass missed it. |
| Verse word wrong, meaning intact | Usually acceptable | Judgment call — flag, do not block. |
| Whole line missing | Lyrics field truncated at entry | This is an execution defect, not a model defect. Check the read-back step. |
| Transcript garbled throughout | ASR struggling with music, not necessarily bad diction | Low confidence; do not report as a pronunciation failure. |

The last row matters: ASR on dense mixes produces noise. Report transcription confidence honestly
rather than converting ASR weakness into a verdict about the take.

## 5. First-listen review

Run `music-taste-review`'s post-generation section against **both** takes and the original packet.
Every acoustic claim must cite a measurement or the transcript. Everything else is explicitly
handed to Frank as a question, not asserted as a finding.

Report shape:

```text
TAKE 1 — <verified url>
  measured:  4:02 · -13.8 LUFS · -1.2 dBTP · LRA 7.1 LU · peak energy 2:48
  arc:       matches the packet through the bridge; final chorus lands 1.5 lower than mapped
  transcript: clean except "Arcanea" read as "ar-CAN-ee-uh" in the hook
  flag:      hook pronunciation is unrecoverable in this take
  for you:   does the voice carry the second verse?

TAKE 2 — <verified url>
  ...

RECOMMENDATION: regenerate with "Ar-KAY-nee-uh" respelled; everything else held constant.
Your call on KEEP / ITERATE / CUT.
```

## 6. Close the run

Write the review to `review.md`, update `manifest.json`, and state the single best next move.
If `ITERATE`, name **one** dominant variable — changing two means the next take teaches nothing.

---

## Handoff

- Execution and backends: `suno`
- Scoring rubric and vetoes: `music-taste-review`
- Pronunciation fixes before the next take: `../suno-prompt-architect/reference/phonetic-control.md`
- Arrangement changes: `suno-ai-mastery`
- Local-lane takes: `local-music-generation` — this skill applies unchanged
