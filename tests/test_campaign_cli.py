from __future__ import annotations
import copy
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
import zipfile
from scripts.campaign_cli import ROOT, PACK_FILES, build_pack, report


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "docs/business-os/campaign.example.json").read_text(encoding="utf-8"))

    def test_allowances_reconcile_without_inventing_actuals(self):
        result = report(self.plan)
        self.assertEqual(result["planned_cash_eur"], 500)
        self.assertIsNone(result["actual_total_eur"])
        self.assertEqual(result["known_actual_cash_eur"], 0)
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["publication_authorized"])

    def test_overspend_and_download_limit_independent_of_credits(self):
        self.plan["budget_cap_eur"] = 499
        self.plan["provider_limits"].update(remaining_credits=999, remaining_downloads=1)
        result = report(self.plan)
        self.assertIn("planned allowances exceed campaign cap", result["planning_blockers"])
        self.assertIn("planned downloads exceed observed remaining balance", result["planning_blockers"])
        self.assertNotIn("planned credits exceed observed remaining balance", result["planning_blockers"])

    def test_actual_spend_requires_every_line_to_reconcile(self):
        for item in self.plan["costs"]:
            item["actual_eur"] = 0
        self.plan["costs"][0]["actual_eur"] = 501
        result = report(self.plan)
        self.assertEqual(result["actual_total_eur"], 501)
        self.assertIn("known actual spend exceeds campaign cap", result["planning_blockers"])

    def test_invalid_cash_values(self):
        for value in (-1, float("nan"), float("inf"), True, "20"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                bad = copy.deepcopy(self.plan)
                bad["costs"][0]["planned_eur"] = value
                report(bad)

    def test_duplicate_cost_and_experiment_ids(self):
        for key in ("costs", "experiments"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                bad = copy.deepcopy(self.plan)
                bad[key].append(copy.deepcopy(bad[key][0]))
                report(bad)

    def test_experiments_cannot_double_allocate_marketing(self):
        self.plan["experiments"][0]["spend_cap_eur"] = 161
        with self.assertRaisesRegex(ValueError, "exceed the marketing"):
            report(self.plan)

    def test_unobserved_and_empty_rates_are_unknown(self):
        self.assertIsNone(report(self.plan)["experiments"][0]["rate"])
        self.plan["experiments"][0]["observations"] = {"source": "synthetic fixture", "window": "test", "numerator": 0, "denominator": 0}
        self.assertIsNone(report(self.plan)["experiments"][0]["rate"])

    def test_rate_has_explicit_denominator_and_no_causality(self):
        self.plan["experiments"][0]["observations"] = {"source": "synthetic fixture", "window": "test", "numerator": 3, "denominator": 20}
        result = report(self.plan)["experiments"][0]
        self.assertEqual(result["rate"], 0.15)
        self.assertEqual(result["denominator"], 20)
        self.assertFalse(result["causal_claim"])

    def test_invalid_observation_and_foreign_cash_rejected(self):
        self.plan["experiments"][0]["observations"] = {"source": "fixture", "window": "test", "numerator": 21, "denominator": 20}
        with self.assertRaises(ValueError):
            report(self.plan)
        self.plan["experiments"][0]["observations"] = None
        self.plan["currency"] = "USD"
        with self.assertRaises(ValueError):
            report(self.plan)

    def test_dates_are_proposals_and_revision_hash_changes(self):
        original = report(self.plan)["plan_sha256"]
        self.plan["target_release_date"] = "2026-12-01"
        result = report(self.plan)
        self.assertEqual(result["proposed_calendar"][0]["proposed_date"], "2026-11-03")
        self.assertFalse(result["calendar_scheduled"])
        self.assertNotEqual(result["plan_sha256"], original)

    def test_pack_allowlist_excludes_private_files_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            for rel in PACK_FILES:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("generic fixture", encoding="utf-8")
            (root / ".env").write_text("private", encoding="utf-8")
            (root / "artist-canon.md").write_text("private", encoding="utf-8")
            first = build_pack(Path(tmp) / "one.zip", root)
            second = build_pack(Path(tmp) / "two.zip", root)
            self.assertEqual(first["sha256"], second["sha256"])
            with zipfile.ZipFile(first["path"]) as archive:
                self.assertEqual(set(archive.namelist()), set(PACK_FILES) | {"PACK-RECEIPT.json"})
            self.assertEqual(first["license_state"], "decision_required")

    def test_pack_refuses_overwrite_and_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "existing.zip"
            existing.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                build_pack(existing)
            self.assertEqual(existing.read_text(encoding="utf-8"), "keep")
            missing = Path(tmp) / "missing"
            missing.mkdir()
            with self.assertRaises(ValueError):
                build_pack(Path(tmp) / "new.zip", missing)
            self.assertFalse((Path(tmp) / "new.zip").exists())

    def test_actual_pack_report_runs_away_from_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = build_pack(Path(tmp) / "pack.zip")
            extracted = Path(tmp) / "extracted"
            with zipfile.ZipFile(bundle["path"]) as archive:
                archive.extractall(extracted)
            completed = subprocess.run([sys.executable, str(extracted / "scripts/campaign_cli.py"), "report", str(extracted / "docs/business-os/campaign.example.json")], cwd=tmp, capture_output=True, text=True, check=True)
            result = json.loads(completed.stdout)
            self.assertEqual(result["planned_cash_eur"], 500)
            self.assertIsNone(result["actual_total_eur"])

    def test_pack_rejects_symlinked_source_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            try:
                (root / "scripts").symlink_to(ROOT / "scripts", target_is_directory=True)
            except OSError:
                self.skipTest("symlink creation requires platform permission")
            with self.assertRaises(ValueError):
                build_pack(Path(tmp) / "unsafe.zip", root)


if __name__ == "__main__":
    unittest.main()
