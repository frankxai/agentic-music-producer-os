# Music Estate Operating Plan

**Date:** 2026-08-30  
**Status:** operating source of truth for the music cluster  
**Decision posture:** evolve every music repo; none are archived or abandoned; one runtime; BYOK packs + local MCP; never a generation-credit broker.

> Agents: read this after `AGENTS.md`, `CLAUDE.md`, `SOUL.md`, and `docs/ARCHITECTURE.md`. Do not start a ninth music runtime. Do not treat GitHub “archived” as a kill order — un-archive and give the repo a job.

---

## 1. Executive recommendation

Ship **this repository** as:

1. the only music **runtime** (Hermes profile + skills + deterministic receipts);
2. the public **skills.sh craft pack**;
3. the operator **Producer** profile (computer use + Telegram on the existing default gateway);
4. the seed of a **Label OS** (DAM, rights, release gate, album ledger).

Wrap existing CLIs as a **local stdio MCP**. Use Cloudflare later for **catalog search and team label graph**, never for Suno login or unofficial generate APIs.

`creator-skills` already lists two Suno prompt skills on skills.sh. That pack stays the ACOS creative-production SKU. This OS is the **producer/label SKU**. Pointers, not copies.

Commercial default remains: **BYOK + skill/agent packs + subscription**, not resale of Suno credits.

---

## 2. Non-negotiables

| Rule | Why |
|---|---|
| One canonical runtime: `frankxai/agentic-music-producer-os` | Estate map 2026-08-07; still true |
| No new music repo | Prefer PR into the owner |
| No unofficial Suno generate API as product | ToS, breakage, credit brokerage |
| One Telegram gateway (default profile) | Dual-gateway echo / token waste |
| One Create action per explicit ask | Finite credits |
| Named-artist / voice-clone language forbidden | Originality |
| Publishing never implied by generation | Authority |
| Skills teach *how*; MCP exposes *access* | Anthropic / skills.sh model |
| Computer use: capture → element index → verify | No stored coordinates/credentials |
| Score is canon; generative audio is a performance lane | Composer factory |
| Event log is hash-linked and locally integrity-checked | Schema v5 |
| Independent reviewer ≠ implementer | Cannot self-approve |

---

## 3. Product layers (what we sell and what we run)

```text
Discovery     awesome-music-agent-skills / awesome-suno-agent-skills
Teaching      ai-music-academy + frankx.ai/music-lab (copy only)
Craft pack    skills.sh  ← skills in THIS repo (no browser operator)
Producer      Hermes profile music-producer + session/score/album CLIs
Label MCP     local stdio around CLIs + suno-library-archiver
Catalog MCP   Cloudflare Worker (read-only, later)
Creator pair  starlight-creator-mcp (image/video/taste/ledger, BYOK)
ACOS overlay  agentic-creator-os music pillar POINTS HERE
```

| SKU | Audience | Install | Includes | Excludes |
|---|---|---|---|---|
| **Craft pack** | Any agent (Claude Code, Cursor, Codex, OpenCode, Hermes) | `npx skills add frankxai/agentic-music-producer-os` | lyric, score, mastery, prompt-architect, taste, meditation | browser operator, receipts CLI requiring this machine |
| **Producer profile** | Operators running Hermes | `scripts/install_machine.py` | all eight skills + CLIs + computer_use | second gateway |
| **Label add-on** | Producer + catalog/rights | local MCP + archiver | DAM, album ledger, release gate | public Suno generate |
| **Academy** | Learners | `ai-music-academy` | curriculum, six-agent teaching orchestra | production receipts |

---

## 4. Repo responsibilities — evolve all, archive none

Every music-adjacent repo keeps a **job**, an **owner concern**, and a **done line**. GitHub archive flags are reversed; READMEs become honest about role.

### 4.1 Canonical cluster

| Repo | Evolves into | Owns | Does not own | Done when |
|---|---|---|---|---|
| **agentic-music-producer-os** | Producer + Label runtime | Skills, SOUL, session/score/album CLIs, Hermes profile, event graph, taste/credit policy | Unofficial Suno HTTP generate; public teaching site; awesome catalogs | Craft pack installable; one proven KEEP; score factory on main |
| **agentic-music-os** | SIP public charter / pointer OS | `MUSIC-OS.md` protocol: phases, receipts vocabulary, originality/credit doctrine | Runtime code, skills copies | README states “runtime lives in producer-os”; charter tests as markdown contract |
| **music-intelligence-systems** | Theory + schema substrate | `MUSIC.md` spec, motif/form/harmony schemas, portable exports, research library | Session receipts, browser Create | Schemas versioned; producer-os validates optional MIS fields without requiring MIS at runtime |
| **vibe-os** | State-change companion | Research-backed state presets, frequency-as-aesthetic-only policy, prompt generator | Production receipts; medical claims | Honest manifest; FSL license; producer-os may *reference* a vibe preset as brief color, never as a health claim |
| **vibe-os-substrate** | SIP vertical charter for Vibe | Substrate README + VERTICALS entry; no duplicate runtime | Prompts, audio files | Un-archived; points at vibe-os + producer-os |
| **suno-library-archiver** | DAM backend | Resumable library archive, hashes, Kura projections | Create clicks; A&R taste | Producer-os `retain` can cite an archiver record ID + SHA-256 |
| **suno-mcp-server** | **Local receipts MCP** (rename purpose, keep repo) | stdio/HTTP MCP wrapping `session_cli` / `score_cli` / `album_cli` / catalog search | `suno_generate` against unofficial APIs | Tools map 1:1 to CLI verbs; generate tool **absent** or returns policy error |
| **starlight-creator-mcp** | BYOK creator substrate pair | image/video/audio-adjacent/taste/ledger/publishing tools | Music event graph | Producer visual loop calls creator MCP after KEEP; no second ledger |
| **awesome-music-agent-skills** | Web-first music skill catalog | Curated third-party + first-party *links* | Runtime, install payload | Public README useful if all frankxai links are removed; monthly pulse |
| **awesome-suno-agent-skills** | Web-first generative-audio catalog | Suno-adjacent tools, analysis, structure | Official Suno affiliation | Same catalog bar; disclaimer: not official Suno |

### 4.2 Product / teaching / distribution cluster

| Repo | Evolves into | Owns | Does not own | Done when |
|---|---|---|---|---|
| **ai-music-academy** | Teaching SKU | Curriculum, six-agent *pedagogy* orchestra, learner UX | Credit-bearing Create; DAM | Lessons cite producer-os craft skills; never claim academy *is* the OS |
| **creator-skills** | ACOS public pack | Video/image/brand + **thin music routers** | Producer receipts, browser operator | Music skills say “for full producer OS: `npx skills add frankxai/agentic-music-producer-os`” |
| **skills** (architect lane) | Architect pack | MCP, orchestration, routing | Music craft | No music SKILL.md duplication |
| **agentic-creator-os** | Creator OS overlay | Commands `/create-music`, pillar waitlist, plugin marketplace | Session schema | `/create-music` loads this pack; no third lyric skill |
| **claude-skills-library** | Long-tail library | Ports/mirrors with provenance | SoT skills | Suno copies marked derived-from producer-os version |
| **arcanea-marketplace** | Creative plugin listing | Marketplace cards for music plugins | Execution | Card links producer-os + craft pack; no fake generate |
| **claude-code-music-production** | Claude Code plugin adapter | `.claude-plugin` marketplace manifest installing this pack | Skill bodies | `/plugin marketplace add frankxai/agentic-music-producer-os` works |
| **lyric-genius-mcp-server** | Lyric-contract MCP adapter | Structured hook/prosody/section JSON checks | Taste scoring; Suno fields | Consumes lyric-composer contracts; MIS may share schema |
| **suno-api** | Private compatibility lab | Upstream provenance notes, breakage log, archiver research | Product generate path | README: lab only; no npm generate advertise; license/provenance documented |
| **StarlightAudio** | QA experiment bench | DSP/spectrum experiments that may feed `record-technical-qa` | Session graph | One tool path producer-os can call without importing the repo |
| **vibeclubs.ai** | Community/brand satellite | Community product | Catalog of Frank’s masters | Naming stays distinct from Vibe OS and producer-os |

### 4.3 Handoff law

```text
MIS schemas  --optional fields-->  producer-os receipts
vibe-os presets  --brief color-->  producer-os brief.md
archiver records  --retain cite-->  producer-os DAM
suno-mcp-server  --wraps-->        producer-os CLIs
starlight-creator-mcp  --visual--> after KEEP
awesome lists  --link only-->      never copy SKILL.md bodies
ACOS / creator-skills  --point-->  this pack
academy  --teaches-->              this pack
suno-api lab  --informs-->         archiver only
```

One-way sanitized projections. No shared database. No duplicated state machines.

---

## 5. Event graph and loops

Canonical reducer: `scripts/session_cli.py` schema **v5**. Album cap: `scripts/album_cli.py` schema **v2**, max **10** Create *reservations* (plan ≠ spend).

```text
INTAKE brief
  → COMPOSE     score | lyrics | meditation | instrumental
  → PACKET      Custom Mode fields (attributes, not artists)
  → TASTE       ≥85/100 songs-instrumentals; ≥90 meditation; no axis <7.5; no veto
  → AUTH CREATE single-use, expiry, operator-ref, artifact hashes
  → VOICE OBS   songs only (`voice_observed`)
  → PREFLIGHT   logged-in Chrome (`browser_preflighted`)
  → CREATE ×1   (`create_submitted`)
  → OBSERVE     real `/song/<id>` or `/s/<id>` (`generation_observed`)
  → AUTH DL     take-bound
  → HASH FILE   SHA-256 in C940 private release root
  → LISTEN      KEEP | ITERATE | CUT
  → QA          tool evidence; KEEP only
  → DAM/RIGHTS  RETAIN
  → HOOK+COVER  lead KEEP only; native image gen
  → RELEASE     HOLD | PRIVATE_PACKAGE_READY | RELEASE_CLEARED
  → DISTRIBUTE  separate instruction
  → LEARN       token/time/pair telemetry
```

| Loop | Credit | Rule |
|---|---|---|
| Craft | none | One strong draft; ≤5 named revisions; no Create |
| Credit | one Create | ITERATE changes one dominant variable |
| Listen | none | No KEEP without playback receipt; no QA without KEEP |
| Album | reserved ≠ spent | 10-track ceiling on Glass Meridian class |
| Visual | image-model BYOK | After KEEP lead only |
| Label | none until release | Human hash-bound; system cannot self-approve |

Score-first parallel graph: `catalog/<slug>/score.txt` → MusicXML/MIDI/ABC/sheet/tab → **one** audio lane (live | sample-library | preview | Lyria authorized | Suno authorized).

---

## 6. Multi-agent team

Roles are **contracts**, not live processes. Do not clone a 99-agent roster into every CLI picker. One generic worker loads the contract for the task.

### 6.1 Constellation (music)

| ID | Role | Loads | May spend credits? | May publish? |
|---|---|---|---|---|
| `producer-orchestrator` | Queen / home DM | `music-producer-os` | No (delegates) | No |
| `score-captain` | Notation canon | `score-composer` | Lyria only if operator `--authorize` | No |
| `lyric-captain` | Lyrics / hooks | `lyric-composer` | No | No |
| `meditation-captain` | Spoken wellness | `guided-meditation-composer` | No | No |
| `suno-craft` | Arrangement / packet | `suno-ai-mastery` + `suno-prompt-architect` | No | No |
| `taste-ar` | Pre-credit + first listen | `music-taste-review` | No | No |
| `browser-operator` | Logged-in Create | `suno-browser-operator` | **One Create** when preconditions hold | No |
| `qa-listener` | Playback + ffmpeg/songsee | `docs/AUDIO-QA-RUNBOOK.md` | No | No |
| `dam-release` | Hash, rights, gate | session_cli retain + archiver | No | No (RELEASE_CLEARED still needs human) |
| `visual-director` | Hook board + covers | native image gen; creator MCP | Image BYOK after KEEP | No |
| `packaging-engineer` | skills.sh, profile, MCP | `agent-profile-distributions`, `hermes-agent-skill-authoring` | No | Docs only |
| `independent-reviewer` | Spec + safety | `requesting-code-review` | No | No |

**Hard rule:** implementer ≠ independent-reviewer ≠ release approver.

### 6.2 Where contracts live (this repo)

| Layer | Path | What |
|---|---|---|
| Human/agent entry | `AGENTS.md` | Points at this plan + architecture |
| Soul | `SOUL.md` | Producer stance |
| Skills | `skills/<name>/SKILL.md` | How |
| Role cards | `agents/<id>/ROLE.md` | One file per constellation ID |
| Harness map | `.agent-harness.json` | Pointers, not copies |
| Claude Code | `.claude/agents/` | **1 orchestrator + captains + gates only** |
| Codex | `.codex/agents/` | Implement / review subset |
| OpenCode | `.opencode/agents/` | plan / build / review |
| Cursor | `.cursor/rules/` | Domain rules, not N agents |
| Hermes | profile `music-producer` **gateway stopped** | Skills mirrored to default for Telegram |
| Gemini | `GEMINI.md` | Pointer to root AGENTS.md |

Do **not** install this roster into user-global `~/.claude/agents`, the default Hermes gateway profile as a second bot, ACOS, Arcanea, or SIS.

### 6.3 Model routing (estate doctrine)

| Work | Model |
|---|---|
| Orchestrate + implement + critical craft | Grok 4.6 primary |
| Fallback implement | OpenAI Codex `gpt-5.6-sol` only when Grok unavailable |
| Independent review | Different seat than implementer (Codex or Claude) |
| Free / overflow | hy3 / best-free; never `opencode run` in no-agent cron |

### 6.4 Connectors and tools

| Connector | Kind | Allowed use | Forbidden use |
|---|---|---|---|
| Hermes `computer_use` | local desktop | Suno Create, library archive, DistroKid **after** separate ask | Passwords, pay, 2FA, extra Create |
| Hermes `web_search` / `web_extract` | web | Attribute research, rights, catalog intel | Artist-clone prompt stuffing |
| Hermes `browser_*` | automated browser | Public research | Login walls; stop and ask |
| Hermes `image_generate` | native stills | Cover / hook after KEEP | FAL filler; humans-as-band photography as default |
| `session_cli.py` / `score_cli.py` / `album_cli.py` / `lyria_cli.py` | local CLI | Authoritative mutations | Invented receipts |
| **suno-mcp-server** (evolved) | local MCP | Same verbs as CLIs | Unofficial generate |
| **starlight-creator-mcp** | BYOK MCP | Visual / publishing adapters | Music event authority |
| **lyric-genius-mcp-server** (evolved) | lyric MCP | Prosody/structure JSON | Taste scores |
| Cloudflare Worker MCP | remote, later | Awesome catalog search; team label graph | Suno cookies, Generate |
| `suno-api` lab | private | Archiver research | Product path |
| Telegram | default gateway only | Natural-language producer | Second bot, swarm as home |
| Infisical | secrets | Gemini/Lyria in process env | Secrets in git |

### 6.5 Collaboration bus

- **Home / deep work:** default Hermes Desktop or Telegram DM.
- **Git bus:** PRs into the owning repo. Book/frontend copy via git-bus, not a peer Hermes in Swarm.
- **Starlight Swarm:** thin assignment line only when a machine-local input is missing. No dual-gateway dialogue.
- **Worktrees:** one concern per worktree. Do not stack Label MCP work onto an unmerged score-composer branch without a fresh tree.

### 6.6 Skill ownership (SoT vs mirrors)

| Skill | SoT | Mirrors |
|---|---|---|
| `music-producer-os` | this repo | default Hermes skills (installer ledger) |
| `score-composer` | this repo (PR #2) | same |
| `lyric-composer` | this repo | lyric-genius MCP consumes, does not fork prose |
| `suno-ai-mastery` / `suno-prompt-architect` | this repo | `creator-skills` thin routers + version pin |
| `music-taste-review` | this repo | none |
| `suno-browser-operator` | this repo | Hermes operator machines only |
| `guided-meditation-composer` | this repo | academy may teach, not fork |
| `songwriting-and-ai-music` | Hermes official | complementary; not SoT |

Every `SKILL.md` `name` must equal its directory. Public pack skills must not contain machine-local paths (`C:/Users/frank/...`). Operator runbooks may.

---

## 7. Production targets

Calendar is **evidence-gated**, not date-gated. A later target does not start until the previous target’s success criteria are green.

### T0 — Honest v0.1 (current)

Machine-ready profile distribution, schema v5 receipts, one-Create doctrine, Glass Meridian bible present, score factory on branch `agent/c940/score-composer-factory` (PR #2).

### T1 — Public craft pack

This repo is installable via `npx skills add frankxai/agentic-music-producer-os`. `SKILLPACK.md` exists. skills.sh badge on README. Browser operator **not** in the public pack list.

### T2 — Score factory on main

PR #2 merged. `python -m unittest discover -s tests -v` includes score tests. Two catalog miniatures compile.

### T3 — Local receipts MCP

`suno-mcp-server` tools wrap CLIs; no generate-against-unofficial-API. Producer-os docs point at it as optional connector. `hermes mcp list` / client `tools/list` shows session/score/album/catalog verbs.

### T4 — Proven private KEEP

One track with: authorization → observed takes → download hash → listening KEEP → technical QA PASS → DAM retain. Glass Meridian T01 or Window Latch. No publication.

### T5 — Label receipts

Rights/splits/ISRC fields on retain; release-gate document for that KEEP; archiver record ID linked; album_cli reservation consumed only after observed Create.

### T6 — Visual loop

KEEP lead has hook board + one native still; no publish. Optional starlight-creator-mcp if publish-ready.

### T7 — Marketplace SKU

Craft pack listed from install telemetry; Hermes profile install path documented; ACOS `/create-music` and `creator-skills` music rows point here; Claude Code plugin adapter repo un-archived and wired.

### T8 — Glass Meridian private album

10 reservations, observed Creates only where authorized, KEEP set defined, no track released. Calibration dataset for token/outcome telemetry.

### T9 — Cloudflare catalog MCP

Read-only search over awesome-music (+ optional awesome-suno). OAuth for team later. Zero generation tools.

### T10 — Teaching alignment

Academy lessons and frankx.ai/music-lab cite pack install + producer doctrine. No claim that the website generates music.

---

## 8. Success criteria (falsifiable)

Legend: **command or artifact must exist**. Claims without the evidence are failures.

### 8.1 Safety (must stay green every target)

| ID | Criterion | Proof |
|---|---|---|
| S1 | No secrets in git | `git grep` / installer tests; no `.env` in distribution |
| S2 | One running Telegram gateway | `hermes gateway status` — default up, `music-producer` stopped |
| S3 | One Create default | session_cli rejects second action without new single-use auth |
| S4 | No named-artist / clone in packets | validate_session imitation tests |
| S5 | Meditation non-clinical | taste veto tests |
| S6 | No unofficial generate in product MCP | MCP `tools/list` has no working `suno_generate` against third-party Suno HTTP |
| S7 | Publishing not implied | release gate default HOLD |

### 8.2 Runtime quality

| ID | Criterion | Proof |
|---|---|---|
| R1 | Unit suite green | `python -m unittest discover -s tests -v` |
| R2 | Installer dry-run | `python scripts/install_machine.py --dry-run --install-profile` |
| R3 | Schema v5 init | `session_cli.py init` writes `schema_version: 5` |
| R4 | Taste gate enforced | incomplete/imitation/below-threshold sessions `ready_for_suno: false` |
| R5 | Score compile | `score_cli.py compile catalog/window-latch/score.txt` writes MusicXML+MIDI (after T2) |
| R6 | Lyria refuses without authorize | existing test in `tests/test_score_cli.py` |
| R7 | Computer-use health | `hermes computer-use doctor` + capture smoke; doctor alone is not enough for T4 |

### 8.3 Pack / marketplace

| ID | Criterion | Proof |
|---|---|---|
| P1 | `SKILLPACK.md` lists included/excluded skills | file exists; browser operator excluded |
| P2 | `npx skills add frankxai/agentic-music-producer-os --list` shows craft skills | real CLI output |
| P3 | Frontmatter names match directories | existing distribution tests |
| P4 | creator-skills music rows point here | remote file contains install line |
| P5 | ACOS `/create-music` points here | ACOS docs or command text |

### 8.4 KEEP / label

| ID | Criterion | Proof |
|---|---|---|
| K1 | Observed Suno URL/ID match | manifest `generations[]` |
| K2 | Download SHA-256 | `downloads[]` |
| K3 | Listening KEEP | `listening_receipts[]` decision KEEP |
| K4 | QA PASS bound to same SHA | `technical_qa[]` |
| K5 | DAM retain | archiver id or local catalog record |
| K6 | Release still HOLD unless human hash | `release_gates[]` |

**World-class bar** (from `docs/PRODUCTION-SYSTEM-EVALUATION.md`, still the north star): ≥90/100 on every safety-critical dimension; one retained listened track; release gate prevents accidental publication; measured token/time/pair outcomes. T4+T5+K1–K6 are the first honest step. Do not claim world-class before that.

### 8.5 Estate hygiene

| ID | Criterion | Proof |
|---|---|---|
| E1 | Every repo in §4 has a README job sentence | remote README first paragraph |
| E2 | No GitHub archive on music cluster | `isArchived=false` after un-archive pass |
| E3 | No second music runtime README claiming Create | grep / review |
| E4 | Awesome catalogs remain web-first | no hub-and-spoke funnel |

---

## 9. Implementation packets (this repo first)

Work in **isolated worktrees** from `main` unless the packet *is* PR #2. Do not commit unless the operator asks.

### Packet A — Operating contracts (this change)

- Add `docs/OPERATING-PLAN.md` (this file).
- Point `AGENTS.md`, `docs/ARCHITECTURE.md`, `README.md` at it.
- Later: `agents/<id>/ROLE.md` thin role cards (Packet A2). Root `AGENTS.md` stays the repo entry; that filename is protected on the operator machine.

### Packet B — Craft pack surface

- Create `SKILLPACK.md` (include/exclude table).
- README install: `npx skills add frankxai/agentic-music-producer-os`.
- skills.sh badge.
- Tests: pack manifest lists expected skill dirs; excludes `suno-browser-operator` from public pack metadata if split, **or** documents it as operator-only in SKILLPACK.

### Packet C — Score factory

- Finish/merge [PR #2](https://github.com/frankxai/agentic-music-producer-os/pull/2).
- CI green on Windows verification workflow.

### Packet D — Event-graph dry run

- Fixture session that fails each gate in order.
- Fixture session that reaches `ready_for_suno` without network.
- Document operator commands for T4; do not spend credits in CI.

### Packet E — suno-mcp-server evolution (other repo)

- Replace advertised generate tools with CLI wrappers.
- README status: receipts MCP, not generation backend.
- Smoke: `tools/list` matches session_cli verbs.

### Packet F — Pointers in sibling repos

- `creator-skills` music READMEs.
- `agentic-music-os` charter pointer.
- `claude-code-music-production` un-archive + plugin manifest.
- `vibe-os-substrate` / `lyric-genius-mcp-server` un-archive + job README.
- Academy + ACOS command text.

### Packet G — T4 KEEP (operator session)

- Glass Meridian T01 or Window Latch.
- Real Chrome, one Create, two takes, one KEEP path.
- Evidence files stay gitignored under `runs/` and C940 private release root.

---

## 10. Files likely to change

**This repo**

- `docs/OPERATING-PLAN.md` (SoT)
- `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`
- `SKILLPACK.md` (Packet B)
- `agents/*/AGENTS.md`, `.agent-harness.json` (Packet A2)
- `distribution.yaml` only if pack metadata belongs in-profile
- `scripts/session_cli.py` / tests if rights fields land in T5
- `skills/*/SKILL.md` only for SoT fixes, not copies

**Other repos (PRs there, not here)**

- `frankxai/suno-mcp-server`
- `frankxai/creator-skills`
- `frankxai/agentic-music-os`
- `frankxai/music-intelligence-systems`
- `frankxai/claude-code-music-production`
- `frankxai/lyric-genius-mcp-server`
- `frankxai/vibe-os-substrate`
- `frankxai/agentic-creator-os` (`/create-music`)
- `frankxai/ai-music-academy` (citation only)

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Mixing this plan into PR #2 | Land Packet A on main; keep score factory as its own PR |
| Unofficial API temptation | S6; suno-mcp-server generate tool removed |
| Dual gateway | S2; dual-gateway-hard-stop skill |
| Skill duplication across ACOS/creator-skills | SoT table §6.6; pointers |
| Claiming KEEP without listening | K3 required before QA |
| Cloudflare MCP holding secrets | Catalog-only; no cookies |
| 99-agent swarm | §6 role contracts; no standing swarm per track |
| Machine-local paths in public pack | Skill-authoring rule; pack test |
| Glass Meridian treated as released | Bible status: private; T8 forbids publish |

---

## 12. Open questions (do not block T1–T4)

1. Public pack license vs operator profile (MIT vs FSL for academy/vibe). Default: this repo stays shareable profile; academy/vibe keep their current licenses.
2. Whether `suno-browser-operator` is documented in the public repo but omitted from skills.sh pack metadata, or moved under `optional-skills/`.
3. Cloudflare account + Worker name for T9 (catalog MCP).
4. Paid SKU price — pack free, Producer/Label subscription later; not a credit broker.

---

## 13. Strategic decision

**Evolve the cluster. Run production in this repo. Teach and list elsewhere. Access via local MCP. Discover via awesome lists and skills.sh. Never archive a music repo — retitle it and give it a job.**
