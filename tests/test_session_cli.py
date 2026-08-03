import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.session_cli import (
    authorize_create,
    authorize_download,
    initialize_session,
    record_browser_preflight,
    record_create_submission,
    record_download,
    record_generation,
    record_listening,
    record_release_gate,
    record_technical_qa,
    record_voice_observation,
    validate_session,
)


class SessionCliTests(unittest.TestCase):
    def _write_passing_review(
        self, session_dir: Path, score: int = 88, meditation: bool = False
    ) -> None:
        axes = (
            "emotional_thesis",
            "originality",
            "imagery_specificity",
            "prosody_singability",
            "section_contrast",
            "hook_strength",
            "arrangement_fidelity",
            "release_readiness",
        )
        if meditation:
            axes = tuple("guidance_pacing" if axis == "hook_strength" else axis for axis in axes)
        axis_lines = "\n".join(
            f"AXIS: {axis} 8.0/10 | EVIDENCE: concrete reviewed evidence for {axis}."
            for axis in axes
        )
        (session_dir / "review.md").write_text(
            f"VERDICT: PASS\nSCORE: {score}/100\nHARD VETOES: none\n{axis_lines}\n",
            encoding="utf-8",
        )
        self._write_production_contract(session_dir, song=not meditation)

    def _write_production_contract(self, session_dir: Path, song: bool = True) -> None:
        (session_dir / "composition-map.md").write_text(
            """# Composition Map
- Tempo/Meter: 124 BPM, 4/4
- Tonal Center/Harmony: D minor; suspended, widening cadence
- Form/Timing: 8-bar intro; verse; pre; chorus; bridge; final chorus; 4-bar outro
- Energy Map: 2 → 4 → 6 → 8 → 3 → 9 → 2
- Focal Arrangement/Negative Space: felt piano and solo violin; leave the verse midrange open
- Ending: final piano octave and sub-bass release
""",
            encoding="utf-8",
        )
        (session_dir / "vocal-casting.md").write_text(
            """# Vocal Casting
- Range/Grain: alto, clear with a dry edge
- Placement/Articulation: close-mic, conversational, open only in the chorus
- Harmony/Intelligibility: unison verse; restrained thirds in the final chorus; no dense strings under consonants
- No-clone declaration: original vocal direction only; no named person, artist likeness, or cloned voice.
""" if song else """# Vocal Casting
- Mode: instrumental, no vocals
- No-clone declaration: no vocal/persona selection applies.
""",
            encoding="utf-8",
        )
        (session_dir / "audiovisual-hook-board.md").write_text(
            """# Audio-Visual Hook Board
- Lyric nucleus: a concrete repeatable title line
- Drop/reveal nucleus: piano-to-sub-bass handoff at the chorus
- Atmosphere nucleus: bow-on-string detail in a dark blue room
""",
            encoding="utf-8",
        )

    def test_initialize_creates_collision_safe_session_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            now = datetime(2026, 7, 19, 2, 45, 0, tzinfo=timezone.utc)

            first = initialize_session(
                workspace=workspace,
                title="Light Between the Waves",
                kind="song",
                brief="An intimate song that grows into grounded hope.",
                now=now,
            )
            second = initialize_session(
                workspace=workspace,
                title="Light Between the Waves",
                kind="song",
                brief="A second take.",
                now=now,
            )

            self.assertNotEqual(first["session_dir"], second["session_dir"])
            session_dir = Path(first["session_dir"])
            self.assertTrue((session_dir / "manifest.json").is_file())
            self.assertEqual(
                json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))["status"],
                "draft",
            )
            self.assertEqual(
                json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))[
                    "create_actions"
                ],
                [],
            )
            self.assertEqual(
                (session_dir / "brief.md").read_text(encoding="utf-8"),
                "An intimate song that grows into grounded hope.\n",
            )
            self.assertTrue((session_dir / "lyrics.md").is_file())
            self.assertFalse((session_dir / "script.md").exists())
            self.assertTrue((session_dir / "style-prompt.md").is_file())
            self.assertTrue((session_dir / "review.md").is_file())

    def test_validate_requires_real_style_and_lyrics_for_song(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Northern Signal",
                kind="song",
                brief="A restrained electronic anthem.",
            )
            session_dir = Path(result["session_dir"])

            initial = validate_session(session_dir)
            self.assertFalse(initial["ready_for_suno"])
            self.assertEqual(
                set(initial["missing"]),
                {
                    "lyrics.md",
                    "style-prompt.md",
                    "review.md",
                    "composition-map.md",
                    "vocal-casting.md",
                    "audiovisual-hook-board.md",
                },
            )

            (session_dir / "lyrics.md").write_text("[Verse 1]\nThe window keeps the weather.\n", encoding="utf-8")
            (session_dir / "style-prompt.md").write_text(
                "Art-pop, 94 BPM, intimate alto, glassy synths, restrained verse to radiant final chorus.\n",
                encoding="utf-8",
            )
            self._write_passing_review(session_dir)

            final = validate_session(session_dir)
            self.assertTrue(final["ready_for_suno"])
            self.assertEqual(final["missing"], [])

            (session_dir / "review.md").write_text(
                "VERDICT: PASS\nSCORE: 88/100\nHARD VETOES: none\n"
                "AXIS: originality 8.0/10 | EVIDENCE: distinct image system.\n",
                encoding="utf-8",
            )
            incomplete_review = validate_session(session_dir)
            self.assertFalse(incomplete_review["ready_for_suno"])
            self.assertIn("review must score every required axis", incomplete_review["errors"])
            self._write_passing_review(session_dir)

            (session_dir / "style-prompt.md").write_text(
                "In the style of a famous singer, clone their voice.\n",
                encoding="utf-8",
            )
            imitation = validate_session(session_dir)
            self.assertFalse(imitation["ready_for_suno"])
            self.assertIn("style prompt contains imitation language", imitation["errors"])

    def test_instrumental_does_not_require_lyrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Still Current",
                kind="instrumental",
                brief="A seven-minute breath-paced ambient composition.",
            )
            session_dir = Path(result["session_dir"])
            (session_dir / "style-prompt.md").write_text(
                "Organic ambient, free pulse, felt piano, bowed glass, low warm drones, no vocals.\n",
                encoding="utf-8",
            )
            self._write_passing_review(session_dir, score=87)

            validation = validate_session(session_dir)
            self.assertTrue(validation["ready_for_suno"])

    def test_incomplete_validation_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Incomplete Song",
                kind="song",
                brief="Intentionally incomplete for CLI verification.",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).parents[1] / "scripts" / "session_cli.py"),
                    "validate",
                    result["session_dir"],
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn('"ready_for_suno": false', completed.stdout)

    def test_meditation_uses_script_and_requires_higher_review_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Return to the Room",
                kind="meditation",
                brief="A ten-minute optional external-orientation practice.",
            )
            session_dir = Path(result["session_dir"])

            self.assertTrue((session_dir / "script.md").is_file())
            self.assertFalse((session_dir / "lyrics.md").exists())
            self.assertIn("script.md", validate_session(session_dir)["missing"])

            (session_dir / "script.md").write_text(
                "You can keep your eyes open and notice what is easiest to notice. [pause 10s]\n",
                encoding="utf-8",
            )
            (session_dir / "style-prompt.md").write_text(
                "Instrumental organic ambient, speech-safe restrained midrange, no vocals, gentle fade.\n",
                encoding="utf-8",
            )
            self._write_passing_review(session_dir, score=89, meditation=True)
            below_threshold = validate_session(session_dir)
            self.assertFalse(below_threshold["ready_for_suno"])
            self.assertIn("review score must be at least 90/100", below_threshold["errors"])

            self._write_passing_review(session_dir, score=92, meditation=True)
            self.assertTrue(validate_session(session_dir)["ready_for_suno"])

            (session_dir / "script.md").write_text(
                "Hold your breath. This frequency heals trauma.\n",
                encoding="utf-8",
            )
            unsafe = validate_session(session_dir)
            self.assertFalse(unsafe["ready_for_suno"])
            self.assertIn("meditation script contains a safety or medical-claim veto", unsafe["errors"])

    def test_record_generation_requires_a_consumed_create_authorization(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Authorization Smoke",
                kind="song",
                brief="A bounded authorization regression fixture.",
            )
            session_dir = Path(result["session_dir"])
            (session_dir / "lyrics.md").write_text("[Chorus]\nHold the line.\n", encoding="utf-8")
            (session_dir / "style-prompt.md").write_text(
                "Original electronic pop, restrained verse to open final chorus.\n",
                encoding="utf-8",
            )
            self._write_passing_review(session_dir)

            with self.assertRaisesRegex(RuntimeError, "Create authorization"):
                record_generation(
                    session_dir,
                    "https://suno.com/song/auth-123",
                    "auth-123",
                    1,
                    "A syntactically valid URL is not authorization evidence.",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Authorization Smoke",
                )

    def test_record_generation_requires_suno_url_and_reads_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(
                workspace=Path(tmp),
                title="Quiet Fire",
                kind="song",
                brief="A song brief.",
            )
            session_dir = Path(result["session_dir"])

            with self.assertRaisesRegex(RuntimeError, "not ready for Suno"):
                record_generation(
                    session_dir,
                    "https://suno.com/song/abc-123",
                    "abc-123",
                    1,
                    "",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )

            (session_dir / "lyrics.md").write_text(
                "[Chorus]\nKeep the quiet fire.\n", encoding="utf-8"
            )
            (session_dir / "style-prompt.md").write_text(
                "Original art-pop, restrained verse, radiant final chorus.\n",
                encoding="utf-8",
            )
            self._write_passing_review(session_dir)
            authorize_create(
                session_dir,
                "create-001",
                "telegram:8582160385:instruction-001",
                "2099-01-01T00:00:00+00:00",
            )
            record_voice_observation(
                session_dir,
                "selected",
                "Observed Test Voice",
                "Visible selector option observed with clear alto descriptor; original direction only.",
                "Observed Test Voice — clear alto descriptor — visible selector options inspected.",
            )
            record_browser_preflight(
                session_dir,
                "create-001",
                "Suno v4.5",
                "custom",
                "redacted-ui-evidence/create-001.json",
                "a" * 64,
            )
            record_create_submission(session_dir, "create-001")

            with self.assertRaises(ValueError):
                record_generation(
                    session_dir,
                    "https://example.com/fake",
                    "fake",
                    1,
                    "",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )
            with self.assertRaises(ValueError):
                record_generation(
                    session_dir,
                    "https://suno.com/not-a-song/arbitrary-path",
                    "arbitrary-path",
                    1,
                    "",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )
            with self.assertRaises(ValueError):
                record_generation(
                    session_dir,
                    "https://suno.com/song/abc-123",
                    "different-id",
                    1,
                    "",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )

            receipt = record_generation(
                session_dir,
                "https://suno.com/song/abc-123",
                "abc-123",
                1,
                "Strong chorus; verse two needs less density.",
                create_action_id="create-001",
                model_label="Suno v4.5",
                take_title="Quiet Fire",
            )

            self.assertEqual(receipt["generation_count"], 1)
            manifest = json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["status"], "generated_partial")
            self.assertEqual(manifest["generations"][0]["id"], "abc-123")
            self.assertEqual(manifest["generations"][0]["take"], 1)
            self.assertEqual(manifest["generations"][0]["title"], "Quiet Fire")
            self.assertEqual(manifest["generations"][0]["create_action_id"], "create-001")
            self.assertEqual(manifest["create_actions"][0]["create_click_count"], 1)
            self.assertEqual(manifest["create_actions"][0]["completed_take_count"], 1)
            self.assertEqual(manifest["events"][-1]["type"], "generation_observed")

            with self.assertRaises(ValueError):
                record_generation(
                    session_dir,
                    "https://suno.com/song/abc-123",
                    " abc-123 ",
                    2,
                    "Whitespace must not bypass duplicate detection.",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )

            with self.assertRaises(ValueError):
                record_generation(
                    session_dir,
                    "https://suno.com/song/def-456",
                    "def-456",
                    1,
                    "Duplicate take number.",
                    create_action_id="create-001",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )

            second_take = record_generation(
                session_dir,
                "https://suno.com/song/def-456",
                "def-456",
                2,
                "Second take from the same Create action.",
                create_action_id="create-001",
                model_label="Suno v4.5",
                take_title="Quiet Fire — Alternate",
            )
            self.assertEqual(second_take["create_action"]["completed_take_count"], 2)
            self.assertEqual(second_take["create_action"]["status"], "completed")

            with self.assertRaisesRegex(RuntimeError, "Create authorization"):
                record_generation(
                    session_dir,
                    "https://suno.com/song/ghi-789",
                    "ghi-789",
                    3,
                    "Unauthorized reroll.",
                    create_action_id="create-002",
                    model_label="Suno v4.5",
                    take_title="Quiet Fire",
                )

            authorize_create(
                session_dir,
                "create-002",
                "telegram:8582160385:instruction-002",
                "2099-01-01T00:00:00+00:00",
            )
            record_voice_observation(
                session_dir,
                "selected",
                "Observed Test Voice",
                "Visible selector option observed with clear alto descriptor; original direction only.",
                "Observed Test Voice — clear alto descriptor — visible selector options inspected.",
            )
            record_browser_preflight(
                session_dir,
                "create-002",
                "Suno v4.5",
                "custom",
                "redacted-ui-evidence/create-002.json",
                "b" * 64,
            )
            record_create_submission(session_dir, "create-002")
            authorized = record_generation(
                session_dir,
                "https://suno.com/song/ghi-789",
                "ghi-789",
                3,
                "Distinct operator authorization created a distinct Create action.",
                create_action_id="create-002",
                model_label="Suno v4.5",
                take_title="Quiet Fire — Reroll",
            )
            self.assertEqual(authorized["create_action_count"], 2)

    def test_song_preflight_requires_observed_voice_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = initialize_session(Path(tmp), "Voice Gate", "song", "A vocal-contract fixture.")
            session_dir = Path(result["session_dir"])
            (session_dir / "lyrics.md").write_text("[Chorus]\nKeep the signal clear.\n", encoding="utf-8")
            (session_dir / "style-prompt.md").write_text("Original chamber electronic song, close alto, piano and violin.\n", encoding="utf-8")
            self._write_passing_review(session_dir)
            authorize_create(session_dir, "create-voice", "cron:voice-test", "2099-01-01T00:00:00+00:00")
            with self.assertRaisesRegex(RuntimeError, "Voice/Persona"):
                record_browser_preflight(session_dir, "create-voice", "Observed Model", "custom", "evidence/preflight.txt", "c" * 64)
            record_voice_observation(
                session_dir,
                "selected",
                "Observed Test Voice",
                "Visible selector option described as a clear alto; no identity inference.",
                "Observed Test Voice — clear alto — visible selector options inspected.",
            )
            preflight = record_browser_preflight(session_dir, "create-voice", "Observed Model", "custom", "evidence/preflight.txt", "c" * 64)
            self.assertEqual(preflight["status"], "preflighted")

    def test_download_requires_per_take_authorization_and_qa_requires_actual_listening(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = initialize_session(
                workspace=workspace,
                title="Receipt Chain",
                kind="song",
                brief="A bounded lifecycle fixture.",
            )
            session_dir = Path(result["session_dir"])
            (session_dir / "lyrics.md").write_text("[Chorus]\nKeep the receipt chain.\n", encoding="utf-8")
            (session_dir / "style-prompt.md").write_text("Original chamber-electronic song, 124 BPM, clear alto, piano violin and controlled sub-bass.\n", encoding="utf-8")
            self._write_passing_review(session_dir)
            self._write_production_contract(session_dir)
            self.assertTrue(validate_session(session_dir)["ready_for_suno"])
            authorize_create(session_dir, "create-001", "cron:album-program", "2099-01-01T00:00:00+00:00")
            record_voice_observation(
                session_dir,
                "selected",
                "Observed Test Voice",
                "Visible selector option observed with clear alto descriptor; original direction only.",
                "Observed Test Voice — clear alto descriptor — visible selector options inspected.",
            )
            record_browser_preflight(session_dir, "create-001", "Observed Model", "custom", "evidence/preflight.txt", "a" * 64)
            record_create_submission(session_dir, "create-001")
            record_generation(session_dir, "https://suno.com/song/take-001", "take-001", 1, "Observed card only.", "create-001", "Observed Model", "Receipt Chain")

            audio_path = workspace / "release" / "take-001.wav"
            audio_path.parent.mkdir(parents=True)
            audio_path.write_bytes(b"RIFFtest-audio")
            with self.assertRaisesRegex(RuntimeError, "download authorization"):
                record_download(session_dir, "take-001", audio_path, workspace / "release")
            authorize_download(session_dir, "download-001", "take-001", "cron:album-program", "2099-01-01T00:00:00+00:00")
            download = record_download(session_dir, "take-001", audio_path, workspace / "release")
            self.assertEqual(download["take_id"], "take-001")
            with self.assertRaisesRegex(RuntimeError, "listening receipt"):
                record_technical_qa(session_dir, "take-001", {"codec": "pcm_s16le"}, "PASS")
            listening = record_listening(session_dir, "take-001", "Hermes agent audio playback", "cron-album-listener", "KEEP", "Opening and hook were played back; no technical claim implied.")
            self.assertEqual(listening["decision"], "KEEP")
            with self.assertRaisesRegex(ValueError, "asset_sha256"):
                record_technical_qa(
                    session_dir,
                    "take-001",
                    {"tool": "ffprobe", "command": "ffprobe -show_format", "asset_sha256": "0" * 64},
                    "PASS",
                )
            qa = record_technical_qa(
                session_dir,
                "take-001",
                {
                    "tool": "ffprobe",
                    "command": "ffprobe -show_format -show_streams take-001.wav",
                    "asset_sha256": download["sha256"],
                    "codec": "pcm_s16le",
                    "sample_rate": "44100",
                },
                "PASS",
            )
            self.assertEqual(qa["status"], "PASS")
            retained = record_release_gate(
                session_dir,
                "take-001",
                workspace / "release",
                "RETAIN",
                "private_unpublished",
                "Private C940 DAM receipt; no publication or sharing authorized.",
            )
            self.assertFalse(retained["publication_authorized"])
            self.assertEqual(retained["sha256"], download["sha256"])


if __name__ == "__main__":
    unittest.main()
