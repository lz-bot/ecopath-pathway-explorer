#!/usr/bin/env python3
"""Validate and review an ECO-PATH foreground inventory draft export.

This script is intentionally read-only. It does not import data into Brightway
or modify any Brightway project or database.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FLOW_TYPES = {"technosphere", "biosphere", "waste"}
DIRECTIONS = {"input", "output"}
UNCERTAINTY_TYPES = {"none", "lognormal", "normal", "triangular", "uniform", "pedigree"}
MODULE_PATTERN = re.compile(r"^EM\d{2}$")


class ConfigurationError(ValueError):
    """Raised when a foreground draft does not satisfy the data contract."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigurationError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConfigurationError(f"{label} must be an array")
    return value


def _require_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    if missing:
        raise ConfigurationError(f"{label} is missing: {', '.join(missing)}")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive_or_null(value: Any, label: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ConfigurationError(f"{label} must be null or a positive number")


def process_review(process: dict[str, Any]) -> dict[str, Any]:
    """Return technical-review readiness for one foreground process draft."""
    reference = process["reference_output"]
    metadata = process["metadata"]
    exchanges = process["exchanges"]

    reference_ready = (
        _nonempty(reference.get("name"))
        and isinstance(reference.get("amount"), (int, float))
        and not isinstance(reference.get("amount"), bool)
        and reference["amount"] > 0
        and _nonempty(reference.get("unit"))
    )
    metadata_ready = (
        _nonempty(metadata.get("location"))
        and isinstance(metadata.get("reference_year"), int)
        and 1900 <= metadata["reference_year"] <= 2200
        and _nonempty(metadata.get("data_source"))
    )

    quantified = 0
    mapped = 0
    complete = 0
    for exchange in exchanges:
        is_quantified = (
            _nonempty(exchange.get("name"))
            and isinstance(exchange.get("amount"), (int, float))
            and not isinstance(exchange.get("amount"), bool)
            and exchange["amount"] > 0
            and _nonempty(exchange.get("unit"))
        )
        is_mapped = _nonempty(exchange.get("provider_database")) and _nonempty(
            exchange.get("provider_code")
        )
        has_uncertainty = (
            exchange["uncertainty"]["type"] == "none"
            or _nonempty(exchange["uncertainty"].get("parameter"))
        )
        if is_quantified:
            quantified += 1
        if is_mapped:
            mapped += 1
        if (
            is_quantified
            and is_mapped
            and _nonempty(exchange.get("data_source"))
            and exchange.get("flow_type") in FLOW_TYPES
            and exchange.get("direction") in DIRECTIONS
            and has_uncertainty
        ):
            complete += 1

    missing: list[str] = []
    if not reference_ready:
        missing.append("reference_output")
    if not metadata_ready:
        missing.append("process_metadata")
    if not exchanges or complete != len(exchanges):
        missing.append("complete_physical_exchanges")

    return {
        "ready": reference_ready and metadata_ready and bool(exchanges) and complete == len(exchanges),
        "exchange_count": len(exchanges),
        "quantified_exchange_count": quantified,
        "mapped_exchange_count": mapped,
        "missing": missing,
    }


def _validate_exchange(exchange: Any, label: str) -> dict[str, Any]:
    item = _require_mapping(exchange, label)
    required = {
        "exchange_id",
        "name",
        "flow_type",
        "direction",
        "amount",
        "unit",
        "provider_database",
        "provider_code",
        "data_source",
        "uncertainty",
    }
    _require_keys(item, required, label)
    if item["flow_type"] not in FLOW_TYPES:
        raise ConfigurationError(f"{label}.flow_type is invalid")
    if item["direction"] not in DIRECTIONS:
        raise ConfigurationError(f"{label}.direction is invalid")
    _positive_or_null(item["amount"], f"{label}.amount")
    uncertainty = _require_mapping(item["uncertainty"], f"{label}.uncertainty")
    _require_keys(uncertainty, {"type", "parameter"}, f"{label}.uncertainty")
    if uncertainty["type"] not in UNCERTAINTY_TYPES:
        raise ConfigurationError(f"{label}.uncertainty.type is invalid")
    return item


def _validate_process(process: Any, index: int) -> dict[str, Any]:
    label = f"processes[{index}]"
    item = _require_mapping(process, label)
    required = {
        "process_id",
        "mapping_key",
        "module_id",
        "building_block",
        "draft_status",
        "reference_output",
        "metadata",
        "exchanges",
        "review",
    }
    _require_keys(item, required, label)
    if not _nonempty(item["process_id"]) or not _nonempty(item["mapping_key"]):
        raise ConfigurationError(f"{label} needs non-empty process_id and mapping_key")
    if not isinstance(item["module_id"], str) or not MODULE_PATTERN.match(item["module_id"]):
        raise ConfigurationError(f"{label}.module_id must match EMxx")
    if item["draft_status"] not in {"draft", "review-ready"}:
        raise ConfigurationError(f"{label}.draft_status is invalid")

    reference = _require_mapping(item["reference_output"], f"{label}.reference_output")
    _require_keys(reference, {"name", "amount", "unit"}, f"{label}.reference_output")
    _positive_or_null(reference["amount"], f"{label}.reference_output.amount")

    metadata = _require_mapping(item["metadata"], f"{label}.metadata")
    _require_keys(
        metadata,
        {
            "location",
            "reference_year",
            "technology_description",
            "data_source",
            "allocation_method",
            "cut_off_note",
        },
        f"{label}.metadata",
    )
    year = metadata["reference_year"]
    if year is not None and (isinstance(year, bool) or not isinstance(year, int) or not 1900 <= year <= 2200):
        raise ConfigurationError(f"{label}.metadata.reference_year must be null or 1900-2200")

    exchanges = _require_list(item["exchanges"], f"{label}.exchanges")
    exchange_ids: set[str] = set()
    for exchange_index, exchange in enumerate(exchanges):
        validated = _validate_exchange(exchange, f"{label}.exchanges[{exchange_index}]")
        exchange_id = validated["exchange_id"]
        if not _nonempty(exchange_id):
            raise ConfigurationError(f"{label}.exchanges[{exchange_index}].exchange_id is empty")
        if exchange_id in exchange_ids:
            raise ConfigurationError(f"{label} contains duplicate exchange_id {exchange_id!r}")
        exchange_ids.add(exchange_id)

    review = _require_mapping(item["review"], f"{label}.review")
    _require_keys(
        review,
        {"ready", "exchange_count", "quantified_exchange_count", "mapped_exchange_count"},
        f"{label}.review",
    )
    calculated = process_review(item)
    for key in ("ready", "exchange_count", "quantified_exchange_count", "mapped_exchange_count"):
        if review[key] != calculated[key]:
            raise ConfigurationError(f"{label}.review.{key} does not match the process content")
    expected_status = "review-ready" if calculated["ready"] else "draft"
    if item["draft_status"] != expected_status:
        raise ConfigurationError(f"{label}.draft_status must be {expected_status!r}")
    return item


def validate_document(document: Any) -> dict[str, Any]:
    """Validate the export structure and return the original document."""
    root = _require_mapping(document, "document")
    _require_keys(
        root,
        {
            "schema_version",
            "export_type",
            "exported_at",
            "app",
            "language",
            "pathway",
            "functional_unit",
            "processes",
            "disclaimer",
        },
        "document",
    )
    if root["schema_version"] != "1.0":
        raise ConfigurationError("schema_version must be '1.0'")
    if root["export_type"] != "ecopath_foreground_draft":
        raise ConfigurationError("export_type must be 'ecopath_foreground_draft'")

    functional_unit = _require_mapping(root["functional_unit"], "functional_unit")
    _require_keys(functional_unit, {"referenceAmount", "referenceUnit"}, "functional_unit")
    _positive_or_null(functional_unit["referenceAmount"], "functional_unit.referenceAmount")
    if functional_unit["referenceAmount"] is None or not _nonempty(functional_unit["referenceUnit"]):
        raise ConfigurationError("functional_unit needs a positive referenceAmount and referenceUnit")

    processes = _require_list(root["processes"], "processes")
    if not processes:
        raise ConfigurationError("processes must contain at least one draft")
    mapping_keys: set[str] = set()
    process_ids: set[str] = set()
    for index, process in enumerate(processes):
        validated = _validate_process(process, index)
        if validated["mapping_key"] in mapping_keys:
            raise ConfigurationError(f"duplicate mapping_key {validated['mapping_key']!r}")
        if validated["process_id"] in process_ids:
            raise ConfigurationError(f"duplicate process_id {validated['process_id']!r}")
        mapping_keys.add(validated["mapping_key"])
        process_ids.add(validated["process_id"])
    return root


def review_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Summarize which drafts are ready for technical LCA review."""
    processes = document["processes"]
    reviews = [process_review(process) for process in processes]
    incomplete = [
        {
            "mapping_key": process["mapping_key"],
            "missing": review["missing"],
        }
        for process, review in zip(processes, reviews)
        if not review["ready"]
    ]
    return {
        "process_count": len(processes),
        "review_ready_count": sum(review["ready"] for review in reviews),
        "incomplete_count": len(incomplete),
        "incomplete": incomplete,
        "brightway_database_modified": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Foreground draft JSON export")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Fail unless every process draft is complete for technical LCA review",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        validate_document(document)
        summary = review_summary(document)
        if args.require_ready and summary["incomplete_count"]:
            missing = ", ".join(item["mapping_key"] for item in summary["incomplete"])
            raise ConfigurationError(f"foreground drafts are incomplete: {missing}")
    except (OSError, json.JSONDecodeError, ConfigurationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
