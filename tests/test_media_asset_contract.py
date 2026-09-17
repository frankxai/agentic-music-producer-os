import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "media-asset-manifest.schema.json"
EXAMPLE_PATH = ROOT / "templates" / "media-asset-manifest.example.json"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
ID = re.compile(r"^[a-z][a-z0-9_]{1,31}_[0-9a-fA-F-]{8,64}$")


class MediaAssetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.example = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_schema_declares_draft_2020_12_and_closed_top_level(self):
        self.assertEqual(
            self.schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(self.schema["properties"]["schemaVersion"]["const"], "0.1.0")

    def test_example_has_every_required_top_level_field(self):
        missing = set(self.schema["required"]) - set(self.example)
        self.assertEqual(missing, set())
        self.assertEqual(self.example["schemaVersion"], "0.1.0")

    def test_blob_and_replica_identity_is_unique_and_hash_bound(self):
        blob_ids = [blob["blobId"] for blob in self.example["blobs"]]
        self.assertEqual(len(blob_ids), len(set(blob_ids)))
        replica_ids = []
        for blob in self.example["blobs"]:
            self.assertRegex(blob["blobId"], ID)
            self.assertRegex(blob["sha256"], SHA256)
            self.assertGreaterEqual(blob["bytes"], 0)
            self.assertTrue(blob["replicas"])
            for replica in blob["replicas"]:
                replica_ids.append(replica["replicaId"])
                self.assertRegex(replica["replicaId"], ID)
                self.assertTrue(replica["uri"])
        self.assertEqual(len(replica_ids), len(set(replica_ids)))

    def test_one_immutable_original_is_present(self):
        originals = [blob for blob in self.example["blobs"] if blob["role"] == "original"]
        self.assertEqual(len(originals), 1)
        self.assertFalse(originals[0]["rebuildable"])

    def test_relationships_and_processing_runs_reference_known_blobs(self):
        blob_ids = {blob["blobId"] for blob in self.example["blobs"]}
        run_ids = {run["runId"] for run in self.example["processingRuns"]}
        for relationship in self.example["relationships"]:
            self.assertIn(relationship["subjectId"], blob_ids)
            self.assertIn(relationship["objectId"], blob_ids)
            if "processingRunId" in relationship:
                self.assertIn(relationship["processingRunId"], run_ids)
        for run in self.example["processingRuns"]:
            self.assertRegex(run["runId"], ID)
            self.assertRegex(run["parameterSha256"], SHA256)
            self.assertRegex(run["receiptSha256"], SHA256)
            self.assertTrue(set(run["inputBlobIds"]).issubset(blob_ids))
            self.assertTrue(set(run["outputBlobIds"]).issubset(blob_ids))

    def test_transcripts_and_measurements_reference_known_blobs(self):
        blob_ids = {blob["blobId"] for blob in self.example["blobs"]}
        for transcript in self.example.get("transcripts", []):
            self.assertRegex(transcript["transcriptAssetId"], ID)
            self.assertIn(transcript["sourceBlobId"], blob_ids)
        for measurement in self.example["qualityMeasurements"]:
            self.assertRegex(measurement["measurementId"], ID)
            self.assertIn(measurement["blobId"], blob_ids)

    def test_integrity_hashes_are_well_formed(self):
        self.assertRegex(self.example["provenance"]["eventLogHeadSha256"], SHA256)
        for measurement in self.example["qualityMeasurements"]:
            if "evidenceSha256" in measurement:
                self.assertRegex(measurement["evidenceSha256"], SHA256)


if __name__ == "__main__":
    unittest.main()
