# Session modes

CLI `init` defaults to Simple Mode for song/instrumental and Custom for meditation. The Python API retains its previous default (schema-5 Custom) for backward compatibility; pass `output_mode="simple"` explicitly for schema 6.

| Contract | Simple (schema 6) | Retained Custom (schema 5) |
|---|---|---|
| Files | brief.md, prompt.md, hook-cells.json, review.md | Existing style/lyrics or script and composition/casting/hook-board files |
| Song text | 2–3 exact single-line cells, each present verbatim in prompt | Full authored lyrics |
| Instrumental | Empty JSON cell array | Existing instrumental contract |
| Review | Prompt scope, named reviewer, evidence, PASS, no hard veto | Existing score/axis fields and thresholds; legacy adapter policy only |
| Voice observation | Selected or observed not_applicable for generic Simple vocals | Selected persona required for vocal songs |
| Execution | Observed mode must equal approved mode | Same |

Both hash the reviewed files into expiring single-use authorizations. Changed files invalidate authorization; no credits are spent by validation. Preflight and submission are separate receipts, and uncertain submissions must be reconciled. The retained recorder has a two-take-per-action capacity; this is a local limit, not a provider guarantee. Do not invent extra or missing results. These changes do not establish a running browser, installed Hermes profile, audio critique, legal clearance or public deployment.

Use `--mode simple` explicitly for preflight and record commands for Simple sessions (those command flags retain `custom` defaults for compatibility). A generic vocal still needs an observed Voice/Persona `not_applicable` receipt, not a silent bypass. To revise an already submitted session, initialize a new version and preserve its receipts.
