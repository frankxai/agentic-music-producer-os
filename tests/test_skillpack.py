from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.skillpack import (
    CRAFT_SKILLS,
    FORBIDDEN_MCP_TOOLS,
    OPERATOR_ONLY_SKILLS,
    load_skillpack_document,
)


ROOT = Path(__file__).resolve().parents[1]


class SkillpackContractTests(unittest.TestCase):
    def test_craft_skills_exist_and_match_frontmatter(self) -> None:
        for name in CRAFT_SKILLS:
            skill_md = ROOT / "skills" / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"missing craft skill {name}")
            text = skill_md.read_text(encoding="utf-8")
            match = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)", text)
            self.assertIsNotNone(match, f"no frontmatter name in {name}")
            self.assertEqual(match.group(1).strip(), name)

    def test_operator_only_skills_are_not_in_the_public_craft_pack(self) -> None:
        overlap = set(CRAFT_SKILLS) & set(OPERATOR_ONLY_SKILLS)
        self.assertEqual(overlap, set())
        self.assertIn("suno-browser-operator", OPERATOR_ONLY_SKILLS)

    def test_skillpack_markdown_documents_both_lanes(self) -> None:
        doc = load_skillpack_document(ROOT / "SKILLPACK.md")
        self.assertEqual(doc["craft"], list(CRAFT_SKILLS))
        self.assertEqual(doc["operator_only"], list(OPERATOR_ONLY_SKILLS))
        self.assertIn("npx skills add frankxai/agentic-music-producer-os", doc["text"])

    def test_readme_advertises_the_skills_sh_install(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills add frankxai/agentic-music-producer-os", readme)
        self.assertIn("SKILLPACK.md", readme)

    def test_forbidden_generation_tools_are_explicit(self) -> None:
        self.assertIn("suno_generate", FORBIDDEN_MCP_TOOLS)
        self.assertIn("suno_extend", FORBIDDEN_MCP_TOOLS)
        self.assertIn("suno_remix", FORBIDDEN_MCP_TOOLS)


if __name__ == "__main__":
    unittest.main()
