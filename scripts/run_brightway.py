#!/usr/bin/env python3
"""Calculate an exported ECO-PATH scenario with an existing Brightway project.

This script is intentionally read-only with respect to Brightway databases. It
does not import, write, delete, relink, or migrate projects or databases.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"


class ConfigurationError(ValueError):
    """Raised when an ECO-PATH scenario or Brightway mapping is invalid."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"JSON root must be an object: {path}")
    return data


def validate_scenario(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    if scenario.get("schema_version") != SCHEMA_VERSION:
        raise ConfigurationError(f"scenario schema_version must be {SCHEMA_VERSION}")
    if not isinstance(scenario.get("scenario_id"), str) or not scenario["scenario_id"]:
        raise ConfigurationError("scenario_id is required")
    functional_unit = scenario.get("functional_unit")
    if not isinstance(functional_unit, dict) or not functional_unit.get("statement"):
        raise ConfigurationError("functional_unit.statement is required")
    blocks = scenario.get("building_blocks")
    if not isinstance(blocks, list):
        raise ConfigurationError("building_blocks must be a list")

    active_blocks: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            raise ConfigurationError(f"building_blocks[{index}] must be an object")
        key = block.get("mapping_key")
        if not isinstance(key, str) or not key:
            raise ConfigurationError(f"building_blocks[{index}].mapping_key is required")
        if key in seen_keys:
            raise ConfigurationError(f"Duplicate building-block mapping_key: {key}")
        seen_keys.add(key)
        quantity = block.get("quantity_per_functional_unit")
        if not isinstance(quantity, (int, float)) or quantity < 0:
            raise ConfigurationError(f"Invalid quantity for building block {key}")
        if block.get("enabled") is True and quantity > 0:
            active_blocks.append(block)
    if not active_blocks:
        raise ConfigurationError("No enabled building block has a positive quantity")
    return active_blocks


def validate_mapping(mapping: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    if mapping.get("schema_version") != SCHEMA_VERSION:
        raise ConfigurationError(f"mapping schema_version must be {SCHEMA_VERSION}")
    project = mapping.get("project")
    if not isinstance(project, str) or not project:
        raise ConfigurationError("mapping.project is required")
    blocks = mapping.get("building_blocks")
    methods = mapping.get("methods")
    if not isinstance(blocks, dict):
        raise ConfigurationError("mapping.building_blocks must be an object")
    if not isinstance(methods, dict) or not methods:
        raise ConfigurationError("mapping.methods must contain at least one method")
    for key, reference in blocks.items():
        if not isinstance(reference, dict) or not reference.get("database") or not reference.get("code"):
            raise ConfigurationError(f"Mapping for {key} must contain database and code")
    for category_id, method in methods.items():
        if not isinstance(method, list) or not method or not all(isinstance(item, str) and item for item in method):
            raise ConfigurationError(f"Method mapping for {category_id} must be a non-empty string list")
    return project, blocks, methods


def mapping_coverage(
    active_blocks: list[dict[str, Any]], block_mapping: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    mapped: list[dict[str, Any]] = []
    missing: list[str] = []
    for block in active_blocks:
        key = block["mapping_key"]
        if key in block_mapping:
            mapped.append(block)
        else:
            missing.append(key)
    return mapped, missing


def installed_project_names(bd: Any) -> set[str]:
    return {getattr(item, "name", str(item)) for item in bd.projects}


def calculate_score(bd: Any, bc: Any, demand: dict[Any, float], method: tuple[str, ...]) -> float:
    if hasattr(bd, "prepare_lca_inputs"):
        prepared_demand, data_objects, remapping = bd.prepare_lca_inputs(demand, method=method)
        lca = bc.LCA(
            demand=prepared_demand,
            method=method,
            data_objs=data_objects,
            remapping_dicts=remapping,
        )
    else:
        lca = bc.LCA(demand, method=method)
    lca.lci()
    lca.lcia()
    return float(lca.score)


def build_demand(
    bd: Any,
    mapped_blocks: list[dict[str, Any]],
    block_mapping: dict[str, Any],
) -> tuple[dict[Any, float], dict[str, Any]]:
    demand: dict[Any, float] = defaultdict(float)
    nodes: dict[str, Any] = {}
    for block in mapped_blocks:
        key = block["mapping_key"]
        reference = block_mapping[key]
        try:
            node = bd.get_node(database=reference["database"], code=reference["code"])
        except Exception as exc:
            raise ConfigurationError(
                f"Brightway node not found for {key}: "
                f"{reference['database']}/{reference['code']}"
            ) from exc
        demand[node] += float(block["quantity_per_functional_unit"])
        nodes[key] = node
    return dict(demand), nodes


def calculate(
    scenario: dict[str, Any],
    mapping: dict[str, Any],
    allow_missing: bool,
    with_contributions: bool,
) -> dict[str, Any]:
    active_blocks = validate_scenario(scenario)
    project, block_mapping, methods = validate_mapping(mapping)
    mapped_blocks, missing = mapping_coverage(active_blocks, block_mapping)
    if missing and not allow_missing:
        raise ConfigurationError(
            "Missing Brightway mappings for active building blocks: " + ", ".join(missing)
        )
    if not mapped_blocks:
        raise ConfigurationError("No active building block has a Brightway mapping")

    try:
        import bw2calc as bc
        import bw2data as bd
    except ImportError as exc:
        raise ConfigurationError(
            "Brightway is not installed in this Python environment. "
            "Install bw2data and bw2calc, or run this script in the Activity Browser environment."
        ) from exc

    if project not in installed_project_names(bd):
        raise ConfigurationError(
            f"Brightway project '{project}' does not exist. Available projects: "
            + ", ".join(sorted(installed_project_names(bd)))
        )
    bd.projects.set_current(project)
    demand, nodes = build_demand(bd, mapped_blocks, block_mapping)
    cohort_size = max(1.0, float(scenario.get("cohort_size", 1)))

    method_results: list[dict[str, Any]] = []
    contributions: list[dict[str, Any]] = []
    requested = {
        item.get("category_id"): item
        for item in scenario.get("impact_method_request", {}).get("categories", [])
        if isinstance(item, dict)
    }
    for category_id, configured_method in methods.items():
        method = tuple(configured_method)
        if method not in bd.methods:
            raise ConfigurationError(
                f"Brightway method is not installed for {category_id}: {method!r}"
            )
        score = calculate_score(bd, bc, demand, method)
        metadata = requested.get(category_id, {})
        method_metadata = bd.methods.get(method, {}) or {}
        unit = metadata.get("unit") or method_metadata.get("unit") or "unknown unit"
        method_results.append(
            {
                "category_id": category_id,
                "name": metadata.get("name", category_id),
                "unit": unit,
                "method": list(method),
                "score_per_functional_unit": score,
                "score_for_cohort": score * cohort_size,
            }
        )
        if with_contributions:
            for block in mapped_blocks:
                key = block["mapping_key"]
                block_demand = {nodes[key]: float(block["quantity_per_functional_unit"])}
                contributions.append(
                    {
                        "category_id": category_id,
                        "mapping_key": key,
                        "module_id": block.get("module_id"),
                        "name": block.get("name"),
                        "score_per_functional_unit": calculate_score(bd, bc, block_demand, method),
                        "unit": unit,
                    }
                )

    databases = sorted({block_mapping[block["mapping_key"]]["database"] for block in mapped_blocks})
    warnings = []
    if missing:
        warnings.append("Active building blocks omitted because mappings were missing: " + ", ".join(missing))
    return {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": scenario["scenario_id"],
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "name": "Brightway",
            "bw2data_version": getattr(bd, "__version__", "unknown"),
            "bw2calc_version": getattr(bc, "__version__", "unknown"),
            "python_version": platform.python_version(),
        },
        "functional_unit": scenario["functional_unit"],
        "cohort_size": cohort_size,
        "methods": method_results,
        "contributions": contributions,
        "mapping_coverage": {
            "active_building_blocks": len(active_blocks),
            "mapped_building_blocks": len(mapped_blocks),
            "missing_mapping_keys": missing,
        },
        "provenance": {"project": project, "databases": databases},
        "warnings": warnings,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, required=True, help="Scenario JSON exported by the web app")
    parser.add_argument("--mapping", type=Path, required=True, help="Local Brightway mapping JSON")
    parser.add_argument("--output", type=Path, default=Path("brightway-results.json"))
    parser.add_argument("--allow-missing", action="store_true", help="Omit active blocks without mappings")
    parser.add_argument("--with-contributions", action="store_true", help="Calculate block-level contributions")
    parser.add_argument("--validate-only", action="store_true", help="Validate JSON and mapping coverage without Brightway")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        scenario = load_json(args.scenario)
        mapping = load_json(args.mapping)
        active_blocks = validate_scenario(scenario)
        _, block_mapping, _ = validate_mapping(mapping)
        mapped, missing = mapping_coverage(active_blocks, block_mapping)
        if args.validate_only:
            summary = {
                "valid": not missing or args.allow_missing,
                "scenario_id": scenario["scenario_id"],
                "active_building_blocks": len(active_blocks),
                "mapped_building_blocks": len(mapped),
                "missing_mapping_keys": missing,
            }
            print(json.dumps(summary, indent=2))
            return 0 if summary["valid"] else 2

        result = calculate(scenario, mapping, args.allow_missing, args.with_contributions)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote Brightway results to {args.output}")
        return 0
    except ConfigurationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
