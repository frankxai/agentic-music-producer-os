#!/usr/bin/env python3
"""Tests for the composer-first score compiler."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from scorelib import (  # noqa: E402
    compile_score,
    guitar_position,
    midi_number,
    parse_score_text,
    validate_score,
)


MINI = """
@title Test Latch
@composer Test
@kind piano
@key D minor
@time 4/4
@tempo 68
@thesis A door almost closes.
@motif A-F-D
@form 2-bar cell

[Piano]
1 RH: A4q F4q D4h
1 LH: D3h A2h
2 RH: A4w
2 LH: A2h E3h
"""


class ScoreCompilerTests(unittest.TestCase):
    def test_parse_and_validate_fixture(self) -> None:
        score = parse_score_text(MINI)
        self.assertEqual(score.title, "Test Latch")
        self.assertEqual(score.parts[0].measures[0].voices["RH"][0].pitches, ["A4"])
        self.assertEqual(validate_score(score), [])

    def test_rejects_incomplete_bar(self) -> None:
        bad = MINI.replace("A4q F4q D4h", "A4q F4q")
        score = parse_score_text(bad)
        issues = validate_score(score)
        self.assertTrue(any("duration" in item for item in issues))

    def test_midi_number(self) -> None:
        self.assertEqual(midi_number("A4"), 69)
        self.assertEqual(midi_number("C4"), 60)
        self.assertEqual(midi_number("Bb2"), 46)

    def test_guitar_position_open_e(self) -> None:
        string_index, fret = guitar_position(64)
        open_midis = [64, 59, 55, 50, 45, 40]
        self.assertEqual(open_midis[string_index] + fret, 64)
        self.assertGreaterEqual(fret, 0)
        self.assertLessEqual(fret, 19)

    def test_compile_writes_canon_formats(self) -> None:
        score = parse_score_text(MINI)
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = compile_score(score, Path(tmp), preview=False)
            for key in ("musicxml", "midi", "abc", "piano_sheet", "guitar_tab", "lyria_prompt", "suno_bridge"):
                path = Path(artifacts[key])
                self.assertTrue(path.exists(), key)
                self.assertGreater(path.stat().st_size, 20, key)
            midi = Path(artifacts["midi"]).read_bytes()
            self.assertTrue(midi.startswith(b"MThd"))
            xml = Path(artifacts["musicxml"]).read_text(encoding="utf-8")
            self.assertIn("<score-partwise", xml)
            self.assertIn("Test Latch", xml)
            tab = Path(artifacts["guitar_tab"]).read_text(encoding="utf-8")
            self.assertIn("e|", tab)
            manifest = json.loads(Path(artifacts["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(manifest["measures"], 2)

    def test_window_latch_catalog_validates(self) -> None:
        path = ROOT / "catalog" / "window-latch" / "score.txt"
        if not path.exists():
            self.skipTest("catalog work not present")
        score = parse_score_text(path.read_text(encoding="utf-8"))
        self.assertEqual(validate_score(score), [])
        self.assertEqual(max(len(part.measures) for part in score.parts), 16)

    def test_chamber_catalog_validates(self) -> None:
        path = ROOT / "catalog" / "window-latch-chamber" / "score.txt"
        if not path.exists():
            self.skipTest("catalog work not present")
        score = parse_score_text(path.read_text(encoding="utf-8"))
        self.assertEqual(validate_score(score), [])
        self.assertEqual([part.name for part in score.parts], ["Violin I", "Violin II", "Viola", "Cello"])


class LyriaCliTests(unittest.TestCase):
    def test_status_does_not_print_secrets(self) -> None:
        from lyria_cli import cmd_status

        class _Args:
            pass

        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_status(_Args())
        payload = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(payload["provider"], "google-lyria-3")
        self.assertIn("lyria-3-clip-preview", payload["models"])
        self.assertNotIn("GEMINI_API_KEY", buf.getvalue())
        self.assertNotIn("GOOGLE_API_KEY", buf.getvalue())

    def test_generate_refuses_without_authorize(self) -> None:
        from lyria_cli import cmd_generate

        class _Args:
            authorize = False
            prompt = "unused"
            model = "lyria-3-clip-preview"
            out = "."
            wav = False

        with self.assertRaises(SystemExit) as raised:
            cmd_generate(_Args())
        self.assertIn("authorize", str(raised.exception).casefold())

    def test_packet_writes_prompt_without_calling_network(self) -> None:
        from lyria_cli import cmd_packet

        with tempfile.TemporaryDirectory() as tmp:
            prompt_path = Path(tmp) / "lyria-prompt.md"
            prompt_path.write_text("Instrumental only.\n", encoding="utf-8")
            out_path = Path(tmp) / "lyria-packet.json"

            class _Args:
                prompt = str(prompt_path)
                model = "lyria-3-pro-preview"
                wav = True
                out = str(out_path)

            rc = cmd_packet(_Args())
            self.assertEqual(rc, 0)
            packet = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["model"], "lyria-3-pro-preview")
            self.assertIn("Instrumental only", packet["input"])
            self.assertEqual(packet["response_format"], {"type": "audio"})


if __name__ == "__main__":
    unittest.main()
