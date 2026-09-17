# Media Vault OS — Daily Operator Runbook

## Purpose

Make high-quality voice, narration, music, and short-form video production repeatable without losing originals, context, transcripts, rights, quality evidence, or storage truth.

This is the target operating loop. Until the Media Vault CLI exists, follow it manually and do not represent unexecuted steps as automated.

## Before the first recording day

### Create one equipment profile per real setup

Record non-secret facts:

- microphone and serial/asset label;
- USB or audio interface and input channel;
- sample rate/bit depth;
- polar pattern;
- mic distance/angle, pop filter and stand;
- room/location and treatment notes;
- monitoring route;
- DAW/capture app and template version;
- baseline room-tone measurement and a short reference phrase.

A setup change creates a new profile version. Do not silently compare quality across different rooms/mics as though only the processing changed.

### Default source format

- Spoken voice/narration: mono WAV/BWF, 48 kHz, 24-bit.
- Video production audio: 48 kHz; isolated microphone track when possible.
- Music: DAW native session plus rendered lossless WAV masters/stems.
- Do not record the only source through irreversible denoise, aggressive gate, limiter, or loudness normalization.

### Capture template

1. Confirm the correct input and equipment profile.
2. Speak at the loudest expected performance level.
3. Leave headroom; any clipping means reduce gain and retake the test.
4. Record a slate: project, chapter/scene, take, date.
5. Record approximately 10 seconds of room tone.
6. Record a 20–30 second reference passage and listen back through headphones.
7. Start the real take only after the reference is clean.

## Daily voice memo loop — under two minutes of ceremony

1. Open the fixed voice-memo recording template.
2. Say the slate: topic + date + intended use.
3. Record; keep the full original.
4. Stop and wait for the recorder to close the file.
5. Drop/export the file into `MEDIA_VAULT_INBOX_ROOT`.
6. Ingest assigns an asset ID, SHA-256 and original replica.
7. Run the voice-memo profile: technical probe, light QC and local transcript.
8. Review the transcript title/summary/tags; correct only material ASR errors.
9. Mark one disposition:
   - `reference` — searchable personal knowledge;
   - `content_candidate` — may become article/video/reel;
   - `narration_seed` — may become a scripted recording;
   - `music_seed` — may become lyrics/composition;
   - `private_hold` — no agent reuse or cloud processing.
10. Confirm a durable replica within 24 hours for any irreplaceable recording.

## Book / long-form narration loop

### Record

- Use one chapter/section per recording session where practical.
- Keep take markers and pickup notes.
- Preserve room tone and mistakes until editorial creates a new derivative.
- For irreplaceable long sessions, use a safety recorder or redundant track.

### Ingest and diagnose

1. Ingest immutable original.
2. Verify duration, sample format, channels and file integrity.
3. Measure peaks/clipping, loudness, silence, noise/room consistency and dropouts.
4. Generate transcript with word timestamps.
5. Compare transcript with the approved manuscript/script version.
6. Create a pickup list; do not hide missing lines with generative replacement by default.

### Edit and refine

1. Create a non-destructive DAW project bound to the source asset IDs.
2. Apply edits and pickups.
3. Diagnose breaths, clicks, plosives, sibilance, noise and room changes individually.
4. Use the smallest repair needed; use iZotope RX or equivalent only for identified defects.
5. Render a narration mezzanine WAV without platform-specific lossy encoding.
6. Re-run objective QC and a real human listen.
7. Produce distributor-specific derivatives from the mezzanine using a versioned delivery profile.

## Camera / Instagram reel loop

### Capture

- Record camera/screen and isolated microphone in OBS or the selected camera workflow.
- Prefer MKV during OBS capture; remux after successful close.
- Use a visual/audio sync marker when sources are separate.
- Retain the full source, even when only a short clip will ship.

### Build

1. Ingest video and separate audio assets.
2. Generate transcript and word timestamps.
3. Mark the strongest 6–15 second hook and 20–60 second story/payoff ranges.
4. Create a proposed edit decision list; auto-editor output is a proposal, not authority.
5. Edit in DaVinci Resolve or render in Remotion.
6. Register captions, music bed, images, motion assets and timeline references.
7. Render a 9:16 review derivative.
8. Check speech intelligibility, captions, visual safe areas, true peak/loudness profile, mobile crop, and reduced-motion/accessibility expectations.
9. Human approves the exact render hash before publishing. Publishing is a separate action.

## Music loop

1. Register brief, lyrics, composition map and provider/generation receipt.
2. Download each authorized take and compute SHA-256.
3. Actually listen; decide `KEEP`, `ITERATE`, or `CUT` with timecoded notes.
4. Run technical probe/QC only on retained takes.
5. Register every stem, edit, mix and master as a derivative with explicit inputs.
6. Preserve provider/model/version, prompt/input rights, applicable terms snapshot, human edits and final approval.
7. Build reel/visualizer derivatives only from retained, rights-reviewed assets.
8. Release packaging and publishing remain separate human gates.

## Automated ingest checklist

For each stable inbox file:

- [ ] File is closed and size/mtime have settled.
- [ ] SHA-256 computed.
- [ ] Duplicate blob check completed.
- [ ] Asset and original replica registered atomically.
- [ ] `ffprobe`/MediaInfo receipt stored.
- [ ] Correct quality profile selected.
- [ ] QC receipt stored with tool/version/command hash.
- [ ] Speech detection/transcription policy applied.
- [ ] Transcript derivatives linked to source SHA-256.
- [ ] Rights/privacy profile applied.
- [ ] Warm/backup gap entered into the replica queue.
- [ ] Inbox file is not deleted automatically.

## Human review queues

### Listen queue

- new narration mezzanines;
- retained music takes and masters;
- repaired/denoised voice where naturalness may have changed;
- final reel/video renders.

### Transcript queue

- names, terminology, numbers and quotations;
- chapter/script completeness;
- multi-speaker labels;
- redaction/public excerpt decisions.

### Rights queue

- other people's voices;
- cloned/synthetic voice requests;
- reference audio;
- generated provider outputs;
- licensed music/SFX/images;
- public release authority.

### Archive/deaccession queue

- project close packages;
- assets with verified warm + independent backup/archive replicas;
- exact local bytes proposed for removal;
- rollback/restore method and expected retrieval delay/cost.

No agent clears these queues by inventing a human identity string.

## Quality incident responses

| Signal | Action |
|---|---|
| Clipping or corrupted frames | Keep original, fail QC, retake when possible; do not normalize the evidence away |
| Unexpected noise/reverb | Compare equipment profile and room tone; repair a derivative only after diagnosis |
| Robotic/over-smoothed voice | Reduce denoise/gating/time correction; compare blind against raw; preserve breaths and dynamics |
| ASR errors | Correct transcript derivative; never edit audio metadata to pretend the words changed |
| Audio/video drift | Inspect sample-rate/timestamp assumptions and timeline; create a corrected synchronized derivative |
| Missing original | Hold downstream release; locate provider/device/source or mark provenance gap explicitly |
| Replica mismatch | Quarantine replica, verify source hash, restore from a known-good independent copy |
| Low local free space | Stop media fanout; generate an exact human-approved deaccession proposal; never broad-delete caches or packages |

## Daily close — five minutes

- [ ] Inbox has no unexplained files.
- [ ] Every irreplaceable capture has an asset ID and SHA-256.
- [ ] QC/transcription failures are visible, not silently skipped.
- [ ] Private assets have the correct privacy profile.
- [ ] Durable-replica gaps are queued.
- [ ] No generated render is mislabeled as a master or approved release.
- [ ] Local capacity remains above the estate target.

## Weekly operations

- Review missing metadata, failed jobs and orphan derivatives.
- Verify backup repository health.
- Sample-restore at least one recent small asset or rotate through project packages.
- Review hot-local footprint and active-project status.
- Review ASR/model/tool updates before changing production profiles.
- Reconcile final human decisions with registry state.

## Monthly archive review

- Validate a closed-project BagIt/package manifest.
- Restore one asset/package from an independent target and recompute SHA-256.
- Inspect expiring Object Lock/retention and lifecycle rules.
- Refresh distributor/social delivery profiles from authoritative current sources.
- Review transcript privacy, retention and public-excerpt boundaries.
- Confirm that semantic/vector indexes can be rebuilt and are not treated as canonical.

## Definition of a complete asset

An asset is operationally complete only when:

- its original byte sequence is hash-identified;
- its technical metadata is probed;
- required QC/transcription has a receipt;
- derivatives and relationships are explicit;
- rights/privacy state is known;
- a real human has completed any required listen/approval;
- the registry knows every durable replica;
- required backup/archive recovery has been tested on schedule.
