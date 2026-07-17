"""Evidence-only deterministic reporting and claim eligibility."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

from particleml.artifacts import publish_artifact, verify_artifact_payload
from particleml.contracts import ConfigurationError, IntegrityError, validate_contract_document

EVIDENCE_STATUSES = ("specified", "implemented", "verified", "deferred")
_STATUS_RANK = {"specified": 0, "implemented": 1, "verified": 2}


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError("REPORT_INPUT", f"cannot load JSON input {path}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError("REPORT_INPUT", f"JSON input is not an object: {path}")
    return value


def validate_status_monotonicity(
    statuses: Mapping[str, str], dependencies: Mapping[str, Sequence[str]]
) -> None:
    """Reject downstream evidence status stronger than its weakest upstream item."""

    if any(status not in EVIDENCE_STATUSES for status in statuses.values()):
        raise IntegrityError("REPORT_STATUS", "unknown evidence status")
    for child, upstream_ids in dependencies.items():
        if child not in statuses or any(item not in statuses for item in upstream_ids):
            raise IntegrityError(
                "REPORT_STATUS_REFERENCE", f"unknown status dependency for {child}"
            )
        child_status = statuses[child]
        upstream = [statuses[item] for item in upstream_ids]
        if any(item == "deferred" for item in upstream):
            if child_status != "deferred":
                raise IntegrityError(
                    "REPORT_STATUS_MONOTONICITY", f"{child} exceeds deferred input"
                )
            continue
        if child_status == "deferred":
            continue
        weakest = min(_STATUS_RANK[item] for item in upstream)
        if _STATUS_RANK[child_status] > weakest:
            raise IntegrityError("REPORT_STATUS_MONOTONICITY", f"{child} exceeds upstream status")


def build_claim_ledger(
    claims: Sequence[Mapping[str, Any]],
    statuses: Mapping[str, str],
    *,
    supervised_fallback: bool,
    e3_deferred: bool,
) -> list[dict[str, Any]]:
    """Resolve claims from verified dependencies and automatic narrowing policies."""

    ledger: list[dict[str, Any]] = []
    for claim in claims:
        required = {"claim_id", "text", "category", "dependencies"}
        if set(claim) != required or not isinstance(claim["dependencies"], list):
            raise ConfigurationError("REPORT_CLAIM_CONFIG", "claim definition fields are invalid")
        dependencies = [str(item) for item in claim["dependencies"]]
        missing = sorted(item for item in dependencies if statuses.get(item) != "verified")
        reasons = [f"unverified:{item}" for item in missing]
        if supervised_fallback and claim["category"] == "pretrained_transfer":
            reasons.append("supervised_fallback_removes_pretrained_transfer")
        if e3_deferred and claim["category"] == "cross_architecture_robustness":
            reasons.append("e3_control_deferred")
        ledger.append(
            {
                "claim_id": claim["claim_id"],
                "text": claim["text"],
                "category": claim["category"],
                "eligible": not reasons,
                "reasons": reasons,
                "dependencies": dependencies,
            }
        )
    return ledger


def collect_run_records(paths: Sequence[Path]) -> dict[str, dict[str, Any]]:
    """Load only schema-valid final run records and reject duplicate identities."""

    records: dict[str, dict[str, Any]] = {}
    for path in paths:
        verify_artifact_payload(path)
        document = _load_json(path)
        validate_contract_document(document, "run")
        run_id = document["run_id"]
        if run_id in records:
            raise IntegrityError("REPORT_DUPLICATE_RUN", f"duplicate run record {run_id}")
        records[run_id] = document
    return records


def _report_payload(
    config: Mapping[str, Any], records: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    expected = config.get("expected_condition_ids")
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        raise ConfigurationError("REPORT_CONFIG", "expected_condition_ids must be strings")
    matrix: list[dict[str, Any]] = []
    successful_metrics: list[dict[str, Any]] = []
    for condition_id in expected:
        record = records.get(condition_id)
        status = "missing" if record is None else str(record["status"])
        matrix.append({"condition_id": condition_id, "status": status})
        if record is not None and status == "succeeded":
            successful_metrics.append(
                {"condition_id": condition_id, "metrics": deepcopy(record["metrics"])}
            )
    statuses = config.get("evidence_statuses")
    dependencies = config.get("status_dependencies")
    claims = config.get("claims")
    if (
        not isinstance(statuses, dict)
        or not isinstance(dependencies, dict)
        or not isinstance(claims, list)
    ):
        raise ConfigurationError("REPORT_CONFIG", "status or claim configuration is invalid")
    normalized_statuses = {str(key): str(value) for key, value in statuses.items()}
    normalized_dependencies = {
        str(key): [str(item) for item in value]
        for key, value in dependencies.items()
        if isinstance(value, list)
    }
    if len(normalized_dependencies) != len(dependencies):
        raise ConfigurationError("REPORT_CONFIG", "status dependencies must be arrays")
    validate_status_monotonicity(normalized_statuses, normalized_dependencies)
    claim_ledger = build_claim_ledger(
        claims,
        normalized_statuses,
        supervised_fallback=config.get("supervised_fallback") is True,
        e3_deferred=config.get("e3_deferred") is True,
    )
    return {
        "schema_version": "1.0.0",
        "report_id": config.get("report_id"),
        "matrix_status": matrix,
        "successful_metrics": successful_metrics,
        "claim_eligibility": claim_ledger,
        "outputs": {
            "T1": {"status": "ineligible_without_validated_audit_evidence"},
            "T2": {"status": "generated", "rows": matrix},
            "T3": {"status": "ineligible_without_complete_e2_evidence"},
            "T4": {"status": "ineligible_without_complete_e3_evidence"},
            "F1": {"status": "ineligible_without_complete_e2_evidence"},
            "F2": {"status": "ineligible_without_paired_comparisons"},
            "F3": {"status": "ineligible_without_complete_e3_evidence"},
        },
    }


def build_report(config_path: Path, run_record_paths: Sequence[Path], output: Path) -> Path:
    """Build a deterministic, immutable report solely from validated retained evidence."""

    config = _load_json(config_path)
    records = collect_run_records(run_record_paths)
    payload = _report_payload(config, records)
    config_hash = hashlib.sha256(_canonical_json(config)).hexdigest()
    input_hashes = {
        f"run_record_{index}": hashlib.sha256(path.read_bytes()).hexdigest()
        for index, path in enumerate(run_record_paths)
    }
    if not input_hashes:
        input_hashes = {"empty_evidence_set": hashlib.sha256(b"").hexdigest()}

    def writer(partial: Path) -> None:
        (partial / "report.json").write_bytes(_canonical_json(payload))

    def validator(partial: Path) -> None:
        rebuilt = _load_json(partial / "report.json")
        if rebuilt != payload:
            raise IntegrityError("REPORT_NONDETERMINISTIC", "report payload changed during write")

    artifact = publish_artifact(
        output,
        writer,
        validator,
        input_hashes,
        config_hash,
        "particleml-report-v1",
    )
    return artifact.path
