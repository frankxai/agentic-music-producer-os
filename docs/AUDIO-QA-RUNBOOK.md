# Audio QA and Private Packaging Runbook

## Scope

This runbook is for an already observed Suno take. It does not authorize a Create, retry, extension, cover, remaster, publication, sharing, or distribution.

## Required sequence

1. Record a distinct per-take download authorization in `session_cli.py`, bound to the observed take ID and source URL.
2. Download only to the explicit C940 release root:
   `C:/Users/frank/Music/C940-Private-Releases/<album>/<track>/`
3. Record the resulting file path, SHA-256, byte count, format, and source linkage with `record-download`.
4. Play the downloaded file. Record the method, reviewer, timestamped observations, and `KEEP|ITERATE|CUT` in `listening-review.md` and `record-listening`.
5. For `KEEP` only, run `ffprobe` and preserve its output reference. Run a spectrum visualization only if the relevant tool is available. Record tool-derived facts with `record-technical-qa`.
6. Create a DAM/release-gate document with source URL, action ID, hashes, rights/plan state, and the explicit absence of publication authorization.
7. Package only retained, authorized assets and documents. Do not include rejected takes, credentials, cookies, or browser evidence containing secrets.

## Frequency-motif policy

Terms such as `528 Hz`, `936 Hz`, `1100 Hz`, and fast amplitude/gamma-rate modulation are creative reference labels only. They are never proof that the generated file contains an exact component and never support health, therapeutic, sleep, manifestation, neuroscience, or consciousness-control claims. If a component matters musically, verify it after download with spectrum evidence and describe only the measured result.

## Google Drive

Before creating a folder or upload, check Google authorization. Upload only retained, authorized assets and the associated album documents. Do not share a folder publicly unless separately authorized. The observed Drive folder URL is the only valid success evidence.
