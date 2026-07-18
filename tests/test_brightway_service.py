import importlib.util
import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "serve_brightway", ROOT / "scripts" / "serve_brightway.py"
)
assert SPEC and SPEC.loader
SERVICE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SERVICE
SPEC.loader.exec_module(SERVICE)


class BrightwayServiceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario = json.loads(
            (ROOT / "examples" / "brightway" / "scenario.example.json").read_text()
        )
        cls.mapping = json.loads((ROOT / "brightway" / "mapping.example.json").read_text())

        def fake_inspector(mapping):
            return {
                "ready": True,
                "project": mapping["project"],
                "databases": ["test-db"],
                "mapped_building_blocks": len(mapping["building_blocks"]),
                "mapped_methods": len(mapping["methods"]),
                "engine": {"name": "Brightway test double"},
            }

        def fake_calculator(scenario, mapping, allow_missing, with_contributions):
            return {
                "schema_version": "1.0",
                "scenario_id": scenario["scenario_id"],
                "functional_unit": scenario["functional_unit"],
                "cohort_size": scenario["cohort_size"],
                "engine": {"name": "Brightway test double"},
                "methods": [
                    {
                        "category_id": "climate",
                        "name": "Climate change",
                        "unit": "kg CO2-eq",
                        "score_per_functional_unit": 1.25,
                        "score_for_cohort": 1.25,
                    }
                ],
                "provenance": {"project": mapping["project"], "databases": ["test-db"]},
                "warnings": [],
            }

        cls.server = SERVICE.create_server(
            "127.0.0.1",
            0,
            cls.mapping,
            ROOT / "brightway" / "mapping.example.json",
            calculator=fake_calculator,
            inspector=fake_inspector,
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def read_json(self, response):
        return json.loads(response.read().decode("utf-8"))

    def test_health_exposes_ready_local_service(self):
        with urlopen(f"{self.base_url}/api/health") as response:
            payload = self.read_json(response)
        self.assertTrue(payload["ready"])
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["session_token"])

    def test_calculation_requires_session_token(self):
        request = Request(
            f"{self.base_url}/api/calculate",
            data=json.dumps(self.scenario).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 403)

    def test_calculation_returns_result_without_file_round_trip(self):
        token = self.server.context.token
        request = Request(
            f"{self.base_url}/api/calculate",
            data=json.dumps(self.scenario).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Ecopath-Token": token,
            },
            method="POST",
        )
        with urlopen(request) as response:
            payload = self.read_json(response)
        self.assertEqual(payload["scenario_id"], self.scenario["scenario_id"])
        self.assertEqual(payload["methods"][0]["score_per_functional_unit"], 1.25)


if __name__ == "__main__":
    unittest.main()
