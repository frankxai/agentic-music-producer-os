# Media Vault OS — Architecture and Data Contract

## Status

This document defines the selected architecture. It does **not** claim that the registry, storage adapters, transcription workers, or graph UI are already deployed.

## Product boundary

Media Vault OS is the private media-data substrate underneath voice, narration, music, and video workflows. It is not a DAW, NLE, streaming service, generation provider, or public publishing system.

### Public Git repository

The Git repository may contain:

- schemas and validators;
- portable CLI/service code;
- generic runbooks and quality profiles;
- fixtures with synthetic/non-private data;
- adapter interfaces and tests.

It must never contain private recordings, transcripts, browser data, credentials, personal memory, provider tokens, unreleased lyrics, rights documents, or absolute private object URLs.

### Private runtime

Use configurable roots rather than hard-coded personal paths:

```text
MEDIA_VAULT_STATE_ROOT   -> small state: registry DB, event log, manifests, queues
MEDIA_VAULT_HOT_ROOT     -> local content-addressed media blobs and active projects
MEDIA_VAULT_INBOX_ROOT   -> capture landing zone; transient, not canonical
MEDIA_VAULT_BACKUP_REPO  -> encrypted backup target
MEDIA_VAULT_OBJECT_URI   -> warm object store
MEDIA_VAULT_ARCHIVE_URI  -> independent cold archive target
```

Recommended Windows defaults are beneath `%USERPROFILE%/.starlight/media-vault` for small private state and `%USERPROFILE%/Music/Starlight-Media` for large hot media. These paths are proposals until the operator approves them; this repository must not create them during documentation or installation dry-runs.

## Invariants

1. **Original bytes are immutable.** Cleaning, mastering, trimming, resampling, transcription, and rendering always create a new blob.
2. **Hash before trust.** A SHA-256 is computed after a file is stable and before it becomes a registered original.
3. **Identity is not a path.** Assets and blobs have durable IDs. Paths and object keys are replicas that may change.
4. **Every derivative names its inputs.** No orphan master, reel, transcript, or stem.
5. **Measurements require tools.** No agent may infer loudness, clipping, sample rate, SNR, or quality from a filename, waveform image, prompt, or generation card.
6. **Listening and measurement are separate evidence.** Objective PASS does not establish artistic quality; a human KEEP verdict does not establish technical conformity.
7. **Transcripts are derivatives.** They keep model, language, timestamps, diarization, and human-review state and never replace the audio.
8. **Replica state is observed.** `uploaded`, `synced`, `backed_up`, `locked`, and `restorable` are separate claims.
9. **Publishing is outside normal processing authority.** Release requires a distinct human authority receipt.
10. **Agents use bounded APIs.** They never recursively search personal drives or phone/MTP mounts.

## Canonical entities

| Entity | Purpose | Key fields |
|---|---|---|
| `Asset` | Human/creative identity across versions | asset ID, kind, title, project/session, status, privacy, tags |
| `Blob` | One immutable byte sequence | blob ID, SHA-256, bytes, MIME/container/codec, role |
| `Replica` | Observed storage location of a blob | tier, provider, URI/key, storage class, observed time, verification, lock |
| `RecordingSession` | Capture context | device/input chain, room, operator, sample format, slate/room tone |
| `ProcessingRun` | One transformation or analysis | operation, tool/model/version, parameter hash, inputs, outputs, receipt hash |
| `QualityMeasurement` | Objective fact from a tool | metric, value/unit, method, profile, pass/warn/fail |
| `ListeningReview` | Human auditory judgment | reviewer, playback method, timecoded notes, KEEP/ITERATE/CUT |
| `Transcript` | Timed text derivative | engine/checkpoint, language, segments/words, diarization, review state |
| `Relationship` | Lineage or semantic edge | subject, predicate, object, creating run |
| `RightsRecord` | Privacy/release constraints | consent, voice/input rights, AI role, terms snapshot, authority, retention |
| `ArchivePackage` | Closed portable package | package hash, BagIt/RO-Crate versions, constituent blobs, validation/restore |
| `Event` | Append-only state transition | event ID, previous hash, actor, action, timestamp, payload hash |

## Relationship vocabulary

Use a constrained predicate set so graphs remain readable:

- `derived_from`
- `transcribes`
- `aligned_to`
- `excerpt_of`
- `denoised_from`
- `edited_from`
- `mixed_from`
- `mastered_from`
- `stem_of`
- `synchronized_with`
- `visualizes`
- `caption_for`
- `published_as`
- `packaged_in`
- `supersedes`

Relationships must point to durable asset/blob IDs, not only paths.

## Content-addressed layout

Canonical object keys should not expose private titles:

```text
blobs/sha256/ab/cd/<64-char-sha256>
assets/<asset-id>/manifest.v1.json
projects/<project-id>/package/<package-id>.json
```

A human-friendly alias can exist in the working project:

```text
20260805_093210-book-ch03-narration-take01.wav
```

The alias is convenience, not identity. Local duplicate references to the same immutable blob may use safe hardlinks on one volume, but the registry must still record one blob and multiple references.

## Capture contracts

### Spoken voice / narration

- 48 kHz, 24-bit mono WAV/BWF source when the device supports it.
- Fixed microphone/interface/room profile ID.
- Conservative gain: normal speech should leave meaningful headroom; clipping is a hard failure.
- No irreversible denoise, gate, limiter, or loudness normalization on the only recording.
- Capture a slate and approximately 10 seconds of room tone for each changed setup.
- Use pop control, stable mic distance, quiet room, and closed-back monitoring.
- For irreplaceable long narration, create a separate safety recording or redundant recorder when practical.

### Video / reel source

- Capture microphone as an isolated track at 48 kHz.
- OBS records crash-safe MKV; remux to MP4 as a derivative after the file closes successfully.
- Use a sync slate/clap when a separate recorder or camera is involved.
- Retain the full source and create lossless/low-loss selects; do not let an auto-editor destroy pauses or source context.

### Music

- Register DAW session/project files, every externally sourced recording, generated take, stem, mix, and master as separate assets/blobs.
- Bind provider/model/checkpoint, prompt/input/reference rights, visible settings, terms snapshot, and human selection/editing decisions.
- A provider URL or project file is not the master. Retain the downloaded bytes and SHA-256.

## Ingest state machine

```text
DISCOVERED
  -> SETTLED          file size/mtime unchanged and writer closed
  -> HASHED           SHA-256 computed
  -> REGISTERED       asset/blob/replica record committed idempotently
  -> PROBED            technical metadata captured
  -> QC_MEASURED       objective measurements and profile verdict
  -> TRANSCRIBED       when speech is present/requested
  -> HUMAN_REVIEW      corrections/listening/rights decisions pending
  -> ACTIVE | HOLD | ARCHIVE_CANDIDATE
```

Failures are explicit states with retry metadata. Retrying ingest with the same SHA-256 must not create another physical blob or duplicate asset unless the operator intentionally creates a second semantic asset reference.

## Quality evidence

### Required technical extraction

- container, codec, duration, sample rate, bit depth where available, channel count;
- file size and SHA-256;
- integrated loudness, loudness range, sample peak and true peak where supported;
- clipping/near-clipping count;
- silence/voice activity spans;
- DC offset, channel imbalance, missing/corrupt frames where measurable;
- waveform and spectrogram derivatives for review, marked rebuildable.

### Versioned quality profiles

Do not impose one loudness target on raw narration, podcast, audiobook, music master, and Instagram reel. Store named profiles such as:

```text
capture-voice-raw-v1
narration-mezzanine-v1
podcast-delivery-v1
music-streaming-master-v1
reel-9x16-aac-v1
archive-preservation-v1
```

Each profile carries thresholds, source standard/vendor, effective date, and tool implementation. Distributor/platform profiles must be refreshed before delivery. Raw capture and archive profiles emphasize integrity and headroom; delivery profiles may normalize or limit a derivative.

### Enhancement policy

1. Listen and diagnose before processing.
2. Preserve the raw original.
3. Apply the smallest reversible chain that fixes an identified defect.
4. Record plugin/tool versions and a parameter hash or project-file reference.
5. Render a new blob.
6. Re-run technical QC and human listening.
7. Never claim that generative enhancement is more human merely because it is smoother. Natural consonants, breaths, room identity, timing, and emotional dynamics are part of the quality gate.

## Transcription pipeline

```text
registered speech blob
  -> VAD regions (optional)
  -> local ASR
  -> word alignment (optional)
  -> speaker diarization (only when needed)
  -> forced alignment against corrected narration script (optional)
  -> canonical transcript JSON
  -> TXT + VTT + SRT exports
  -> human correction
  -> semantic index (rebuildable)
```

The canonical transcript stores:

- source blob SHA-256;
- engine, model/checkpoint and runtime version;
- language and confidence where available;
- segments and words with start/end times;
- speaker labels and diarization model when applicable;
- redaction markers without deleting the private original transcript;
- human-review status, editor and timestamp;
- parent transcript ID when corrected or regenerated.

## Storage and lifecycle

### Hot local

Keep active projects, recent captures, DAW/editor project files, current masters, and useful proxies. Enforce the estate capacity target; do not let media fanout push the system below the required free-space percentage. Automatic local deletion is not allowed by this contract. The system may propose exact deaccession candidates only after it proves durable replicas and rebuildability.

### Warm object

Upload immutable originals as soon as ingest/QC reaches a safe boundary. Use versioning and, for irreplaceable locked material, time-bounded object retention after the operator chooses governance/compliance semantics. Verify remote size/checksum/ETag semantics correctly; multipart ETags are not universal SHA-256 values.

### Independent backup

Back up the registry, event log, manifests, irreplaceable originals, masters, stems, project files, transcripts, and rights evidence with client-side encryption. A successful snapshot is not a recovery proof. Run repository checks and sampled restores on schedule.

### Cold archive

When a project closes, construct a package containing:

- immutable originals and approved masters;
- stems and indispensable project files;
- canonical manifest and lineage export;
- transcripts/captions;
- QC and listening receipts;
- rights/consent/terms records;
- BagIt manifests and optional RO-Crate metadata;
- validation report and package SHA-256.

Archive storage class selection must record retrieval latency, minimum-retention/early-deletion terms, expected retrieval cost, and responsible owner.

### Default retention rhythm

- **Daily:** ingest backlog, QC/transcription failures, replica gaps, free-space guard.
- **Weekly:** backup check, missing metadata queue, transcript review queue, active-project local footprint.
- **Monthly:** sampled restore, archive-package validation, orphan lineage/replica checks, tool/model profile refresh.
- **Project close:** human-approved archive package and deaccession proposal.

## Agent interface

Initial CLI/API verbs:

```text
media ingest <path>
media inspect <asset-id|sha256>
media search <query>
media where <asset-id|blob-id>
media qc <asset-id> --profile <profile>
media transcribe <asset-id> --profile <profile>
media transcript <asset-id> [--format json|txt|vtt|srt]
media lineage <asset-id>
media register-run <receipt.json>
media propose-archive <project-id>
media verify-replica <blob-id> <replica-id>
media restore-test <package-id> --target <disposable-path>
```

Read-only MCP resources/tools may mirror `search`, `inspect`, `where`, `transcript`, and `lineage`. Mutation tools require scoped capabilities, idempotency keys, exact asset IDs, and append-only receipts. No generic `run shell`, arbitrary-path read, arbitrary URL fetch, delete, publish, or upload tool belongs in the public agent surface.

## Graph views

Use relational tables first and render with Cytoscape.js:

1. **Lineage DAG:** original → cleaned → edited → master → reel/published asset.
2. **Storage map:** blob → hot/warm/backup/archive replicas with verification and lock state.
3. **Project graph:** recording sessions, works, takes, stems, edits, masters and release packages.
4. **Quality history:** measurements and human verdicts by version.
5. **Transcript graph:** source audio → ASR → corrected transcript → captions → clip/reel.

Move to PostgreSQL for multi-machine concurrency. Consider Apache AGE or another graph layer only after real traversal/query evidence shows relational edges are insufficient.

## Security, privacy and rights

- Private voice and transcripts default to `protected-local` and local ASR.
- Cloud enhancement/ASR requires a named privacy profile and explicit upload authority.
- Object keys avoid human names and sensitive titles where possible.
- Credentials live in approved secret stores/environment configuration, never manifests.
- Store privacy classification, consent and voice-use scope per recording session/asset.
- A speaker label is not consent. A model output assignment is not voice/style clearance or copyright proof.
- C2PA signing keys must remain server/operator controlled; agents may prepare a signing request but must not possess release keys by default.
- Deletion means a governed tombstone plus provider-specific deaccession; it is never a blind filesystem remove.

## Scale triggers

Stay with a single Python service/CLI and SQLite until one of these becomes true:

- multiple machines write concurrently;
- queue retries and worker ownership become operationally important;
- the registry reaches a measured query or write bottleneck;
- more than one human needs permissions/review queues;
- archive/restore SLAs require durable orchestration observability.

Then move metadata to PostgreSQL, use PostgreSQL full-text search/pgvector before adding a second search system, and introduce Temporal as the preferred durable workflow engine. Every workflow uses an idempotency key derived from source hash plus recipe version so retries cannot duplicate uploads, signing, publication or derivatives. Dagster or Prefect are alternatives only if Temporal is rejected; do not run two orchestration control planes. Keep media bytes in object storage; do not place them in the relational database.

## First implementation slice

Build only this vertical slice:

1. `media ingest` for WAV/MP3/FLAC/M4A/MP4/MOV/MKV.
2. SHA-256 content-addressed blob placement and idempotent SQLite registration as the local reference implementation; PostgreSQL remains the multi-machine target.
3. `ffprobe`/MediaInfo extraction.
4. versioned QC receipt with loudness, peak, duration, channels and clipping checks.
5. faster-whisper transcript with JSON/TXT/VTT output.
6. `media inspect`, `media where`, and `media lineage` JSON output.
7. one synthetic fixture plus one private operator-controlled voice memo acceptance run.

Do not add cloud storage, a web UI, a graph database, background auto-deletion, or publication in the first slice. The slice is done only when rerunning ingest is idempotent and a registered voice memo can be found, transcribed, measured, and traced without opening the media folders manually.
