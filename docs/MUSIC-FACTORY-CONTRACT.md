# Music factory contract

Use one human front door and one durable job owner. An orchestrator may load craft
skills and delegate an independent listener review; it does not need a network of
agents for every song. n8n handles bounded requests, waits, retries and records.

## Stages

1. Recover the brief and owner/project canon. Keep artist identity out of shared defaults.
2. Write the premise, hook/form, sonic direction and original lyrics/score.
3. Review text against the exact contract hash. Record rationale, not an invented audio score.
4. Compile a provider packet. Check capabilities, lyrics, candidate count and dated estimate.
5. Host approves a finite owner budget/credit envelope. Caller input cannot grant authority.
6. Persist a reservation and submission intent before the paid request.
7. Store provider job ID, then poll status. A lost POST response becomes `submission_unknown`.
8. Reconcile uncertain jobs in the provider account; do not rerender to find out.
9. Download through an authorized export/client into owner storage; preserve originals and checksums.
10. Listen to the actual take; record reviewer, timestamp/asset and keep/revise/reject rationale.
11. Measure delivery and remeasure every written normalization. Choose destination targets.
12. Check provenance/rights and stage metadata. Publish only through the separate release route.

## Production properties

| Property | Required mechanism |
|---|---|
| Idempotency | Owner + work revision + candidate; same ID/different contract is a conflict |
| Scope | Authenticated host maps identity to owner; body owner must match |
| Budget | Atomic reserve across concurrent jobs; retain unknown charges conservatively |
| Retries | Bounded status GET retries; never retry a paid POST without provider reconciliation |
| Credentials | Host secrets store; no keys/cookies in prompts, repository exports or receipts |
| Storage | External media archive; repository contains code, schemas and sanitized metadata |
| Audio evidence | Actual asset hash, tool output and declared/observed listening provenance |
| Learning | Exact change, result, failure and evidence class; no private taste in public cards |
| Release | Staging is distinct from distribution/publication; unknown rights hold release |

## n8n integration

Prefer an authenticated HTTP tool to a loop inside a Code node. Prepare/status
routes can be exposed to ChatGPT; paid submit and budget grants need a host-owned
execution surface. Do not accept `approved:true` as authority. On queue completion,
persist the result first, archive it, then request the listening decision.

Use Wait/status nodes or separate bounded polling executions. Store provider IDs
outside execution history. Review imported workflows while inactive. Verify node
versions, credential bindings, owner resolution, paths, rollback and error branches
before enabling. Search/details/execute MCP access alone cannot import/update a
workflow. A JSON export is not a deployed automation.

## Integration boundary

Public consumers use these portable skills and their own executor. Existing
machine-local Hermes/Suno session receipts remain authoritative for that host.
An optional operated Songcraft/factory core can be installed by its owner; it
does not become a dependency or permission requirement for public skill users.
Do not copy private canon or fork another craft engine into each project.

## Review packet

Return title, selected direction, lyrics/score, provider-ready fields, production
plan and real status. State exactly which of prepared, submitted, generated,
archived, listened, technically checked, rights-attested and release-staged have
evidence. Suggest one next action tied to the largest remaining musical failure.
