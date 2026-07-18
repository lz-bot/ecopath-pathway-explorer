import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_brightway", ROOT / "scripts" / "run_brightway.py"
)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class BrightwayRunnerValidationTest(unittest.TestCase):
    def setUp(self):
        self.scenario = json.loads(
            (ROOT / "examples" / "brightway" / "scenario.example.json").read_text()
        )
        self.mapping = json.loads((ROOT / "brightway" / "mapping.example.json").read_text())

    def test_example_has_complete_structural_mapping(self):
        blocks = RUNNER.validate_scenario(self.scenario)
        _, mappings, _ = RUNNER.validate_mapping(self.mapping)
        mapped, missing = RUNNER.mapping_coverage(blocks, mappings)
        self.assertEqual(len(mapped), 1)
        self.assertEqual(missing, [])

    def test_duplicate_mapping_key_is_rejected(self):
        self.scenario["building_blocks"].append(dict(self.scenario["building_blocks"][0]))
        with self.assertRaises(RUNNER.ConfigurationError):
            RUNNER.validate_scenario(self.scenario)

    def test_validate_only_cli_does_not_import_brightway(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            scenario_path = directory_path / "scenario.json"
            mapping_path = directory_path / "mapping.json"
            scenario_path.write_text(json.dumps(self.scenario))
            mapping_path.write_text(json.dumps(self.mapping))
            result = RUNNER.main(
                [
                    "--scenario",
                    str(scenario_path),
                    "--mapping",
                    str(mapping_path),
                    "--validate-only",
                ]
            )
            self.assertEqual(result, 0)

    def test_missing_requested_method_is_rejected(self):
        self.mapping["methods"].pop("climate")
        summary = RUNNER.validation_summary(self.scenario, self.mapping)
        self.assertFalse(summary["valid"])
        self.assertEqual(summary["missing_method_mappings"], ["climate"])

    def test_scenario_without_confirmed_building_blocks_is_rejected(self):
        for block in self.scenario["building_blocks"]:
            block["enabled"] = False
        with self.assertRaisesRegex(RUNNER.ConfigurationError, "No enabled building block"):
            RUNNER.validation_summary(self.scenario, self.mapping)


if __name__ == "__main__":
    unittest.main()
