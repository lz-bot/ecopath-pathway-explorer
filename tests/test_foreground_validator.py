import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_foreground", ROOT / "scripts" / "validate_foreground.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ForegroundDraftValidationTest(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(
            (ROOT / "examples" / "foreground" / "foreground-draft.example.json").read_text()
        )

    def make_review_ready(self):
        document = copy.deepcopy(self.document)
        process = document["processes"][0]
        contrast = process["exchanges"][1]
        contrast.update(
            {
                "amount": 0.1,
                "unit": "kg",
                "provider_database": "example-background-database",
                "provider_code": "example-contrast-provider",
                "data_source": "Illustrative test fixture",
            }
        )
        review = VALIDATOR.process_review(process)
        process["draft_status"] = "review-ready"
        process["review"] = {
            key: review[key]
            for key in (
                "ready",
                "exchange_count",
                "quantified_exchange_count",
                "mapped_exchange_count",
            )
        }
        return document

    def test_example_is_valid_but_incomplete(self):
        VALIDATOR.validate_document(self.document)
        summary = VALIDATOR.review_summary(self.document)
        self.assertEqual(summary["process_count"], 1)
        self.assertEqual(summary["review_ready_count"], 0)
        self.assertEqual(summary["incomplete_count"], 1)
        self.assertFalse(summary["brightway_database_modified"])

    def test_complete_process_is_review_ready(self):
        document = self.make_review_ready()
        VALIDATOR.validate_document(document)
        summary = VALIDATOR.review_summary(document)
        self.assertEqual(summary["review_ready_count"], 1)
        self.assertEqual(summary["incomplete"], [])

    def test_duplicate_mapping_key_is_rejected(self):
        duplicate = copy.deepcopy(self.document["processes"][0])
        duplicate["process_id"] = "different-process-id"
        self.document["processes"].append(duplicate)
        with self.assertRaisesRegex(VALIDATOR.ConfigurationError, "duplicate mapping_key"):
            VALIDATOR.validate_document(self.document)

    def test_stale_review_counts_are_rejected(self):
        self.document["processes"][0]["review"]["exchange_count"] = 99
        with self.assertRaisesRegex(VALIDATOR.ConfigurationError, "does not match"):
            VALIDATOR.validate_document(self.document)

    def test_require_ready_cli_rejects_incomplete_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "foreground.json"
            path.write_text(json.dumps(self.document))
            result = VALIDATOR.main(["--input", str(path), "--require-ready"])
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
