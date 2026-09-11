---
name: local-music-generation
description: Decide between hosted Suno and local open-weight music generation, and run the local lane when it is the right call. Covers full-song models with vocals (YuE, DiffRhythm, ACE-Step), instrumental and SFX models (MusicGen, AudioGen, Stable Audio Open), hardware feasibility, and disk cost. Use for "generate this locally", "without Suno", "open source music model", "self-hosted music generation", or when credits are exhausted.
version: 0.1.0
tags: [local, open-weights, musicgen, yue, diffrhythm, offline, gpu]
---

# Local Music Generation

The craft in `lyric-composer`, `suno-ai-mastery`, and `suno-prompt-architect` is model-agnostic.
Lyrics, structural tags, dynamic arc, and phonetic control transfer to every open-weight song
model, because they all take the same two inputs: lyrics with section markers, and a style tag
string. What changes is throughput, control, and cost shape.

**Do not open this lane by default.** Hosted generation is faster and better for almost every
brief. Local wins on exactly four axes.

---

## When local is the right call

Choose local only when at least one is true:

- **Volume**: dozens of variants, or a systematic sweep of one variable. Per-generation cost
  goes to zero; the constraint becomes wall-clock, not credits.
- **Privacy**: the lyric or the voice must not leave the machine.
- **Determinism**: you need a fixed seed to reproduce a take exactly. Hosted generation does not
  give you this.
- **Pipeline integration**: generation must run headless inside a script, without browser control.

Choose hosted when: the brief is a single finished song, vocal quality is the deliverable,
turnaround matters, or the operator has credits and a working session. That is most of the time.

---

## Model landscape

Verify current model state before committing — this field moves monthly and the entries below
are a starting map, not a current fact.

### Full song, with vocals

| Model | Shape | Notes |
|---|---|---|
| **YuE** | Autoregressive, lyrics → full song with vocals and accompaniment | Closest open analogue to hosted song generation. Heaviest compute of the three. |
| **DiffRhythm** | Non-autoregressive diffusion, full-length | Fast — published figures cite well above realtime on a high-end discrete GPU. Best throughput option. |
| **ACE-Step** | Foundation-model approach to music generation | Broad capability surface; check current release state and licence before use. |

### Instrumental and sound design

| Model | Shape | Notes |
|---|---|---|
| **MusicGen** (audiocraft) | Text → instrumental, melody-conditioning variant available | Mature, well-documented, small variants run without a large GPU. No vocals. |
| **AudioGen** (audiocraft) | Text → sound effects and environmental audio | The right tool for foley and texture beds, not music. |
| **Stable Audio Open** | Text → audio, permissive weights | Good for stems, loops, and short beds. |

**Licence check is not optional.** Open weights are not automatically commercial-use weights.
Before any generated audio enters an Arcanea, FrankX, or client deliverable, confirm the model's
licence permits commercial output and record the model name, version, and licence in the run's
`manifest.json`. This is a release-readiness item, not a legal footnote.

---

## Hardware feasibility — check before installing anything

Full-song vocal models are built around discrete NVIDIA GPUs with substantial VRAM. Published
performance figures are almost always on a 4090-class card.

Run the check honestly rather than optimistically:

1. **Is there a discrete NVIDIA GPU with ≥12 GB VRAM available on the target machine?**
   - Yes → full-song models are viable.
   - No → full-song vocal generation is not practical locally. Two real options remain:
     instrumental generation with a small MusicGen variant on CPU (slow, minutes per clip, but it
     works), or moving the job to a machine that has the GPU.

2. **Intel Arc / integrated graphics**: these do not run CUDA. Some models have alternative
   backends, but treat any such path as an experiment with a time budget, not a plan. Do not
   promise a local song lane on an iGPU laptop.

3. **Disk**: model weights run to many gigabytes per model, plus caches. Check free space against
   the storage contract before downloading. Under TIGHT or CRITICAL, do not pull weights —
   the download is not recoverable from a wedged disk.

4. **Thermals and duration**: a batch sweep will hold the machine at load for a long time. Run a
   performance preflight and treat it as unattended work, not something to run under a session
   that also needs the machine responsive.

If the check fails, say so plainly and route back to hosted generation. A local lane that takes
forty minutes per take and thermally throttles is worse than one Create action.

---

## Craft transfer

Everything from the Suno skills applies, with these deltas:

| Element | Hosted | Local |
|---|---|---|
| Style field | Natural-language paragraph, semicolon-separated layers | Usually a comma-separated tag string. Compress the same layers; drop connective prose. |
| Structural tags | `[Verse 1]`, `[Chorus]` etc. | Same convention, generally honoured. Verify against the specific model's documented format. |
| Performance cues | Reliable | Weaker. Push more of the intent into the style string and the arrangement. |
| Exclusions | Dedicated field | Usually absent — negative prompting may or may not exist. Achieve exclusion through positive specificity. |
| Pronunciation | Fix in lyrics before generation | Same, and more important — respelling is the only lever available. |
| Seed | Not exposed | Exposed. **Record it.** A seed plus a prompt is a reproducible take; this is the main advantage of the lane. |

`suno-prompt-architect/reference/phonetic-control.md` transfers unchanged and matters more here.

---

## Run discipline

The credit boundary that governs hosted generation does not apply — but the taste gate does.
Zero marginal cost is not a licence to skip `music-taste-review`. Generating fifty unreviewed
takes produces fifty things nobody will listen to, and the review burden lands on the operator.

Procedure:

1. Pass the packet through `music-taste-review` exactly as for a hosted run.
2. Fix the seed. Generate a small batch — three to five — varying **one** variable.
3. Review the batch against the same brief. Score, do not vibe.
4. Record in the session `manifest.json`: model name and version, licence, seed, prompt string,
   lyrics file hash, and wall-clock. A local take without a recorded seed is not reproducible and
   is therefore not an asset.
5. Keep survivors in the session directory. Delete the rest — local audio accumulates fast and
   the disk is the constraint that bites first.

---

## Hybrid pattern

The strongest use of this lane is not replacing hosted generation but feeding it:

- Sweep locally to find the arrangement or hook that works, then produce the final vocal take hosted.
- Generate instrumental beds locally for meditation and video work, where no vocal is needed and
  volume is high — this is where the lane pays for itself.
- Use AudioGen for texture and foley under narration rather than paying music credits for a bed.

---

## Handoff

- Brief, orchestration, and session receipts: `music-producer-os`.
- Lyrics: `lyric-composer`.
- Musical direction: `suno-ai-mastery`.
- Prompt compression and pronunciation: `suno-prompt-architect` and its references.
- Quality gate: `music-taste-review` — unchanged thresholds.
