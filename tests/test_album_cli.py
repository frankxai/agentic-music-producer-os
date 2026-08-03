import json
import tempfile
import unittest
from pathlib import Path

from scripts.album_cli import initialize_album, migrate_album, record_album_telemetry, reserve_create


class AlbumCliTests(unittest.TestCase):
    def test_album_enforces_ten_create_reservations_and_records_telemetry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            album = initialize_album(root, "Glass Meridian", 10)
            manifest_path = Path(album["manifest_path"])
            for number in range(1, 11):
                receipt = reserve_create(manifest_path, f"track-{number:02d}", f"run-{number:02d}")
                self.assertEqual(receipt["reserved_count"], number)
            with self.assertRaisesRegex(RuntimeError, "maximum Create budget"):
                reserve_create(manifest_path, "track-11", "run-11")
            telemetry = record_album_telemetry(
                manifest_path,
                "track-01",
                {
                    "role": "controller",
                    "provider_model": "configured profile",
                    "actual_usage": None,
                    "unavailable_reason": "subscription meter not exposed",
                    "create_actions": 1,
                    "takes_observed": 2,
                    "stage": "generation_observed",
                    "create_action_id": "create-track-01",
                    "source_receipt_ref": "runs/track-01/manifest.json#create-track-01",
                },
            )
            self.assertEqual(telemetry["track_id"], "track-01")
            with self.assertRaisesRegex(RuntimeError, "already has an observed Create"):
                record_album_telemetry(
                    manifest_path,
                    "track-01",
                    {
                        "role": "controller",
                        "provider_model": "configured profile",
                        "actual_usage": None,
                        "unavailable_reason": "subscription meter not exposed",
                        "create_actions": 1,
                        "takes_observed": 2,
                        "stage": "duplicate",
                        "create_action_id": "create-track-01-duplicate",
                        "source_receipt_ref": "runs/track-01/manifest.json#create-track-01-duplicate",
                    },
                )
            persisted = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["create_budget"]["reserved"], 10)
            self.assertEqual(persisted["create_budget"]["observed"], 1)
            self.assertEqual(len(persisted["telemetry"]), 1)

    def test_migrate_safe_v1_ledger_preserves_zero_create_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "album-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "title": "Legacy Glass",
                        "create_budget": {"maximum": 10, "reserved": 1, "observed": 0},
                        "reservations": [{"track_id": "t01", "run_id": "run-01", "reserved_at": "2026-01-01T00:00:00+00:00", "status": "reserved"}],
                        "telemetry": [{"track_id": "t01", "role": "controller", "provider_model": "legacy", "actual_usage": None, "unavailable_reason": "not exposed", "create_actions": 0, "takes_observed": 0, "stage": "browser_blocked", "recorded_at": "2026-01-01T00:00:00+00:00"}],
                        "publication_authorized": False,
                    }
                ),
                encoding="utf-8",
            )
            migrated = migrate_album(manifest_path)
            self.assertEqual(migrated["status"], "migrated")
            current = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["schema_version"], 2)
            self.assertIsNone(current["reservations"][0]["observed_create_action_id"])
            self.assertIsNone(current["telemetry"][0]["create_action_id"])
            self.assertTrue(current["telemetry"][0]["source_receipt_ref"].startswith("legacy-schema-v1:"))
            self.assertEqual(migrate_album(manifest_path)["status"], "already_current")

    def test_migrate_rejects_unbound_legacy_observed_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "album-manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "title": "Unsafe Legacy",
                        "create_budget": {"maximum": 10, "reserved": 1, "observed": 1},
                        "reservations": [{"track_id": "t01", "run_id": "run-01", "reserved_at": "2026-01-01T00:00:00+00:00", "status": "reserved"}],
                        "telemetry": [{"track_id": "t01", "role": "controller", "provider_model": "legacy", "actual_usage": None, "unavailable_reason": "not exposed", "create_actions": 1, "takes_observed": 2, "stage": "legacy", "recorded_at": "2026-01-01T00:00:00+00:00"}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "cannot be migrated"):
                migrate_album(manifest_path)
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8"))["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
