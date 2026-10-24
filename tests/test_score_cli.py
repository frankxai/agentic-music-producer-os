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
            for key in (
                "musicxml",
                "midi",
                "abc",
                "piano_sheet",
                "guitar_tab",
                "lyria_prompt",
                "suno_bridge",
            ):
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
            manifest = json.loads(
                Path(artifacts["manifest"]).read_text(encoding="utf-8")
            )
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
        self.assertEqual(
            [part.name for part in score.parts],
            ["Violin I", "Violin II", "Viola", "Cello"],
        )


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


class TestScorelibComprehensive(unittest.TestCase):
    def test_midi_number_invalid(self):
        with self.assertRaises(ValueError):
            midi_number("H4")

    def test_midi_number_accidental_b(self):
        self.assertEqual(midi_number("Eb4"), 63)

    def test_midi_number_accidental_sharp(self):
        self.assertEqual(midi_number("F#4"), 66)

    def test_midi_number_accidental_B(self):
        self.assertEqual(midi_number("BB4"), 70)

    def test_normalize_pitch_invalid(self):
        from scorelib import normalize_pitch

        with self.assertRaises(ValueError):
            normalize_pitch("H4")

    def test_normalize_pitch_accidental_b(self):
        from scorelib import normalize_pitch

        self.assertEqual(normalize_pitch("eb4"), "Eb4")

    def test_dotted_note(self):
        from scorelib import parse_note_token

        event = parse_note_token("C4q.")
        self.assertTrue(event.dotted)
        self.assertEqual(event.ticks, 480 + 240)
        self.assertEqual(event.xml_duration, 4 + 2)

    def test_velocity(self):
        from scorelib import parse_note_token

        event = parse_note_token("C4qv100")
        self.assertEqual(event.velocity, 100)
        event2 = parse_note_token("C4qv200")
        self.assertEqual(event2.velocity, 127)

    def test_invalid_note_token(self):
        from scorelib import parse_note_token

        with self.assertRaises(ValueError):
            parse_note_token("C4z")

    def test_empty_chord(self):
        from scorelib import parse_note_token

        with self.assertRaises(ValueError):
            parse_note_token("[]q")

    def test_invalid_note_token_content(self):
        from scorelib import parse_note_token

        with self.assertRaises(ValueError):
            parse_note_token("[invalid]q")

    def test_parse_score_text_invalid_line(self):
        with self.assertRaises(ValueError):
            parse_score_text("invalid line")

    def test_parse_score_text_no_parts(self):
        with self.assertRaises(ValueError):
            parse_score_text("@title T")

    def test_implicit_part(self):
        score = parse_score_text("@title T\n1 RH: C4w")
        self.assertEqual(score.parts[0].name, "Piano")

    def test_instrument_guitar(self):
        score = parse_score_text("@title T\n[Electric Guitar]\n1 RH: C4w")
        self.assertEqual(score.parts[0].instrument, "guitar")

    def test_instrument_viola(self):
        score = parse_score_text("@title T\n[Viola Section]\n1 RH: C4w")
        self.assertEqual(score.parts[0].instrument, "viola")

    def test_instrument_cello(self):
        score = parse_score_text("@title T\n[Cello Solo]\n1 RH: C4w")
        self.assertEqual(score.parts[0].instrument, "cello")

    def test_validate_tempo_low(self):
        from scorelib import Score

        score = Score("T", "C", "K", "C", "4/4", 30, "Th", "M", "F", [])
        issues = validate_score(score)
        self.assertTrue(any("tempo" in i for i in issues))

    def test_validate_tempo_high(self):
        from scorelib import Score

        score = Score("T", "C", "K", "C", "4/4", 250, "Th", "M", "F", [])
        issues = validate_score(score)
        self.assertTrue(any("tempo" in i for i in issues))

    def test_validate_no_measures(self):
        from scorelib import Score, Part

        score = Score(
            "T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [Part("Piano", "piano")]
        )
        issues = validate_score(score)
        self.assertTrue(any("no measures" in i for i in issues))

    def test_validate_non_contiguous_measures(self):
        from scorelib import Score, Part, NoteEvent

        part = Part("Piano", "piano")
        part.measure(2).voices["RH"] = [NoteEvent(["C4"], 16, False, 72, False)]
        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [part])
        issues = validate_score(score)
        self.assertTrue(any("contiguous" in i for i in issues))

    def test_validate_empty_measure(self):
        from scorelib import Score, Part

        part = Part("Piano", "piano")
        part.measure(1)
        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [part])
        issues = validate_score(score)
        self.assertTrue(any("empty" in i for i in issues))

    def test_validate_score_errors(self):
        from scorelib import Score

        score = Score("T", "C", "K", "C", "4/4", 80, "", "", "", [])
        issues = validate_score(score)
        self.assertIn("missing motif", issues)
        self.assertIn("missing thesis", issues)

    def test_key_fifths(self):
        from scorelib import key_fifths

        self.assertEqual(key_fifths("C minor"), (-3, "minor"))
        self.assertEqual(key_fifths("F major"), (-1, "major"))

    def test_program_for_strings(self):
        from scorelib import _program_for

        self.assertEqual(_program_for("strings"), 48)

    def test_step_alter_b(self):
        from scorelib import _step_alter

        self.assertEqual(_step_alter("Bb4"), ("B", -1))

    def test_step_alter_invalid(self):
        from scorelib import _step_alter

        with self.assertRaises(ValueError):
            _step_alter("H4")

    def test_lead_events_P(self):
        from scorelib import Score, NoteEvent, _lead_events

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["P"] = [NoteEvent(["C4"], 16, False, 72, False)]
        events = _lead_events(score)
        self.assertEqual(len(events), 1)

    def test_lead_events_first(self):
        from scorelib import Score, NoteEvent, _lead_events

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["V1"] = [NoteEvent(["C4"], 16, False, 72, False)]
        events = _lead_events(score)
        self.assertEqual(len(events), 1)

    def test_guitar_position_out_of_range(self):
        string_idx, fret = guitar_position(100)  # C7 is way too high
        self.assertEqual(string_idx, 0)
        self.assertGreater(fret, 19)

    def test_voice_text_rest(self):
        from scorelib import _voice_text, NoteEvent

        txt = _voice_text([NoteEvent([], 16, False, 72, True)])
        self.assertEqual(txt, "r:w")

    def test_voice_text_dotted(self):
        from scorelib import _voice_text, NoteEvent

        txt = _voice_text([NoteEvent(["C4"], 4, True, 72, False)])
        self.assertEqual(txt, "C4:q.")

    def test_part_reuse(self):
        from scorelib import Score

        score = Score("", "", "", "", "", 80, "", "", "")
        p1 = score.part("Piano")
        p2 = score.part("Piano")
        self.assertIs(p1, p2)

    def test_score_to_json(self):
        from scorelib import Score, NoteEvent, score_to_json

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        score.part("Piano").measure(1).voices["RH"] = [
            NoteEvent(["C4"], 4, False, 72, False)
        ]
        data = score_to_json(score)
        self.assertEqual(data["title"], "T")

    def test_compile_score_preview(self):
        from scorelib import Score, NoteEvent, compile_score
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["RH"] = [NoteEvent(["C4"], 16, False, 72, False)]
        part.measure(1).voices["LH"] = [NoteEvent(["C3"], 16, False, 72, False)]
        with tempfile.TemporaryDirectory() as d:
            artifacts = compile_score(score, Path(d), preview=True)
            self.assertIn("preview_wav", artifacts)
            self.assertTrue(Path(artifacts["preview_wav"]).exists())

    def test_compile_score_validation_fails(self):
        from scorelib import Score, compile_score
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "", "", "", [])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                compile_score(score, Path(d), preview=False)

    def test_musicxml_rest(self):
        from scorelib import Score, NoteEvent, write_musicxml
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["RH"] = [NoteEvent([], 16, False, 72, True)]  # rest
        with tempfile.TemporaryDirectory() as d:
            path = write_musicxml(score, Path(d) / "test.xml")
            xml = path.read_text(encoding="utf-8")
            self.assertIn("<rest/>", xml)

    def test_musicxml_staves_edge(self):
        from scorelib import Score, NoteEvent, write_musicxml
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(2).voices["LH"] = [NoteEvent(["C3"], 16, False, 72, False)]
        with tempfile.TemporaryDirectory() as d:
            path = write_musicxml(score, Path(d) / "test.xml")
            xml = path.read_text(encoding="utf-8")
            self.assertIn("<voice>2</voice>", xml)
            self.assertIn("<staff>2</staff>", xml)
            self.assertIn("</score-partwise>", xml)

    def test_staves_edge_no_clef(self):
        from scorelib import Score, NoteEvent, write_musicxml
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["LH"] = [NoteEvent(["C3"], 16, False, 72, False)]
        with tempfile.TemporaryDirectory() as d:
            path = write_musicxml(score, Path(d) / "test.xml")
            xml = path.read_text(encoding="utf-8")
            self.assertIn("<staves>2</staves>", xml)

    def test_abc_pitch_octave(self):
        from scorelib import Score, NoteEvent, write_abc
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["RH"] = [NoteEvent(["C6"], 16, False, 72, False)]
        with tempfile.TemporaryDirectory() as d:
            path = write_abc(score, Path(d) / "test.abc")
            abc = path.read_text(encoding="utf-8")
            self.assertIn("c'", abc)

    def test_abc_pitch_alter(self):
        from scorelib import Score, NoteEvent, write_abc
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["RH"] = [NoteEvent(["C#4", "Bb3"], 16, False, 72, False)]
        with tempfile.TemporaryDirectory() as d:
            path = write_abc(score, Path(d) / "test.abc")
            abc = path.read_text(encoding="utf-8")
            self.assertIn("^C", abc)
            self.assertIn("_B,", abc)

    def test_abc_rest(self):
        from scorelib import Score, NoteEvent, write_abc
        import tempfile

        score = Score("T", "C", "K", "C", "4/4", 80, "Th", "M", "F", [])
        part = score.part("Piano")
        part.measure(1).voices["RH"] = [NoteEvent([], 16, False, 72, True)]
        with tempfile.TemporaryDirectory() as d:
            path = write_abc(score, Path(d) / "test.abc")
            abc = path.read_text(encoding="utf-8")
            self.assertIn("z1", abc)


if __name__ == "__main__":
    unittest.main()
