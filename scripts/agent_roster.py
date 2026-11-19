"""Music constellation role contracts. Roles are files, not live processes."""

from __future__ import annotations

# Root AGENTS.md is a protected filename on this machine; role contracts use ROLE.md.
CONTRACT_FILENAME = "ROLE.md"

ROLES: tuple[tuple[str, str], ...] = (
    ("producer-orchestrator", "skills/music-producer-os/SKILL.md"),
    ("score-captain", "skills/score-composer/SKILL.md"),
    ("lyric-captain", "skills/lyric-composer/SKILL.md"),
    ("meditation-captain", "skills/guided-meditation-composer/SKILL.md"),
    ("suno-craft", "skills/suno-ai-mastery/SKILL.md"),
    ("taste-ar", "skills/music-taste-review/SKILL.md"),
    ("browser-operator", "skills/suno-browser-operator/SKILL.md"),
    ("qa-listener", "docs/AUDIO-QA-RUNBOOK.md"),
    ("dam-release", "templates/release-gate.md"),
    ("visual-director", "templates/audiovisual-hook-board.md"),
    ("packaging-engineer", "SKILLPACK.md"),
    ("independent-reviewer", "docs/OPERATING-PLAN.md"),
)

CLI_CAPTAINS: tuple[str, ...] = (
    "producer-orchestrator",
    "score-captain",
    "taste-ar",
)
