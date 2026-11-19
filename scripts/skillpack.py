"""Public craft-pack contract for skills.sh / npx skills add."""

from __future__ import annotations

from pathlib import Path
from typing import Any

CRAFT_SKILLS: tuple[str, ...] = (
    "music-producer-os",
    "score-composer",
    "lyric-composer",
    "guided-meditation-composer",
    "suno-ai-mastery",
    "suno-prompt-architect",
    "music-taste-review",
)

OPERATOR_ONLY_SKILLS: tuple[str, ...] = ("suno-browser-operator",)

FORBIDDEN_MCP_TOOLS: tuple[str, ...] = (
    "suno_generate",
    "suno_extend",
    "suno_remix",
    "suno_cover",
    "suno_remaster",
)


def load_skillpack_document(path: Path) -> dict[str, Any]:
    """Parse SKILLPACK.md tables into craft vs operator-only skill lists."""
    text = Path(path).read_text(encoding="utf-8")
    craft: list[str] = []
    operator_only: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0].strip("`")
        lane = cells[1].strip("`").casefold()
        if name.casefold() in {"skill", "---"} or set(name) <= {"-"}:
            continue
        if lane == "craft":
            craft.append(name)
        elif lane == "operator-only":
            operator_only.append(name)
    return {"craft": craft, "operator_only": operator_only, "text": text}
