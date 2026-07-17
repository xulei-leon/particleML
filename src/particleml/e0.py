"""Cross-artifact E0 evidence aggregation without synthetic gate promotion."""

from __future__ import annotations

import hashlib
import json
import math
from enum import Enum
from pathlib import Path
from typing import Any

from particleml.contracts import ContractError, InputError, IntegrityError, validate_schema_document

POLICY_KEYS = {
    "schema_version",
    "required_artifacts",
    "required_measurements",
    "required_checks",
    "required_freeze_decisions",
    "required_qcd_record_ids",
    "minimum_tt_pilot_files",
    "minimum_qcd_pilot_files_per_record",
    "charged_no_track_fraction_max",
    "cost_reserve_fraction",
    "working_budget_usd_max",
    "provisional_n_max_per_class",
}
EVIDENCE_KEYS = {
    "schema_version",
    "evidence_id",
    "evidence_tier",
    "host_qualification",
    "artifacts",
    "measurements",
    "checks",
    "freeze_decisions",
}
MEASUREMENT_FIELDS = {
    "source_bytes",
    "events_processed",
    "cpu_seconds",
    "wall_seconds",
    "failed_files",
    "total_files",
    "compact_bytes",
    "canonical_bytes",
    "view_bytes",
    "selected_qcd_jets",
    "selected_top_jets",
    "charged_no_track_fraction",
    "e0_base_cost_usd",
    "e1_base_cost_usd",
    "e2_base_cost_usd",
}


class E0Status(str, Enum):
    """Formal cross-artifact E0 gate outcomes."""

    PASSED = "passed"
    FAILED = "failed"
    BLOCKED_EXTERNAL_EVIDENCE = "blocked_external_evidence"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _load_object(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise InputError("INPUT_NOT_FOUND", f"input does not exist: {path}") from exc
    except OSError as exc:
        raise InputError("INPUT_UNREADABLE", f"cannot read {path}: {exc}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(code, f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(code, f"JSON root must be an object: {path}")
    return value, raw


def _require_string_list(value: object, field: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item for item in value)
        or len(set(value)) != len(value)
    ):
        raise ContractError("E0_POLICY", f"{field} must be a unique non-empty string list")
    return value


def _load_policy(path: Path) -> tuple[dict[str, Any], bytes]:
    policy, raw = _load_object(path, "E0_POLICY")
    if set(policy) != POLICY_KEYS or policy.get("schema_version") != "1.0.0":
        raise ContractError("E0_POLICY", "policy has missing, unknown, or unsupported fields")
    for field in (
        "required_artifacts",
        "required_measurements",
        "required_checks",
        "required_freeze_decisions",
    ):
        _require_string_list(policy[field], field)
    if set(policy["required_measurements"]) != MEASUREMENT_FIELDS:
        raise ContractError("E0_POLICY", "required_measurements does not match the E0 contract")
    records = policy.get("required_qcd_record_ids")
    if not isinstance(records, list) or not records or not all(
        isinstance(record, int) and not isinstance(record, bool) and record > 0
        for record in records
    ):
        raise ContractError("E0_POLICY", "required_qcd_record_ids is invalid")
    for field in (
        "minimum_tt_pilot_files",
        "minimum_qcd_pilot_files_per_record",
        "provisional_n_max_per_class",
    ):
        value = policy.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ContractError("E0_POLICY", f"{field} must be a positive integer")
    for field in (
        "charged_no_track_fraction_max",
        "cost_reserve_fraction",
        "working_budget_usd_max",
    ):
        value = policy.get(field)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            or float(value) < 0
        ):
            raise ContractError("E0_POLICY", f"{field} must be finite and non-negative")
    return policy, raw


def _number(measurements: dict[str, object], field: str) -> float:
    value = measurements.get(field)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
        or float(value) < 0
    ):
        raise IntegrityError("E0_MEASUREMENT", f"{field} must be finite and non-negative")
    return float(value)


def project_resources(
    measurements: dict[str, object], *, reserve_fraction: float
) -> dict[str, object]:
    """Calculate deterministic throughput, storage, failure, and reserved-cost values."""

    if set(measurements) != MEASUREMENT_FIELDS:
        raise IntegrityError("E0_MEASUREMENT", "measurement fields are missing or unknown")
    values = {field: _number(measurements, field) for field in MEASUREMENT_FIELDS}
    if not math.isfinite(reserve_fraction) or reserve_fraction < 0:
        raise IntegrityError("E0_MEASUREMENT", "reserve_fraction must be finite and non-negative")
    for denominator in ("wall_seconds", "events_processed", "total_files"):
        if values[denominator] <= 0:
            raise IntegrityError("E0_MEASUREMENT", f"{denominator} must be positive")
    if values["failed_files"] > values["total_files"]:
        raise IntegrityError("E0_MEASUREMENT", "failed_files exceeds total_files")
    reserved_costs = {
        stage: values[field] * (1.0 + reserve_fraction)
        for stage, field in (
            ("E0", "e0_base_cost_usd"),
            ("E1", "e1_base_cost_usd"),
            ("E2", "e2_base_cost_usd"),
        )
    }
    return {
        "source_bytes_per_wall_second": values["source_bytes"] / values["wall_seconds"],
        "events_per_wall_second": values["events_processed"] / values["wall_seconds"],
        "cpu_seconds_per_event": values["cpu_seconds"] / values["events_processed"],
        "file_failure_fraction": values["failed_files"] / values["total_files"],
        "retained_storage_bytes": int(
            values["compact_bytes"] + values["canonical_bytes"] + values["view_bytes"]
        ),
        "projected_cost_usd_with_reserve": reserved_costs,
        "projected_total_cost_usd_with_reserve": sum(reserved_costs.values()),
    }


def _artifact_is_valid(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"path", "sha256", "completed"}
        and isinstance(value.get("path"), str)
        and bool(value["path"])
        and isinstance(value.get("sha256"), str)
        and len(value["sha256"]) == 64
        and all(character in "0123456789abcdef" for character in value["sha256"])
        and value.get("completed") is True
    )


def build_e0_audit(evidence_path: Path, policy_path: Path, output: Path) -> dict[str, Any]:
    """Aggregate one E0 evidence bundle and retain blocked, failed, or passed status."""

    policy, policy_raw = _load_policy(policy_path)
    evidence, evidence_raw = _load_object(evidence_path, "E0_EVIDENCE")
    if set(evidence) != EVIDENCE_KEYS or evidence.get("schema_version") != "1.0.0":
        raise ContractError("E0_EVIDENCE", "evidence has missing, unknown, or unsupported fields")
    if not isinstance(evidence.get("evidence_id"), str) or not evidence["evidence_id"]:
        raise ContractError("E0_EVIDENCE", "evidence_id must be non-empty")
    missing: list[str] = []
    failed: list[str] = []
    if evidence.get("evidence_tier") != "qualified_host":
        missing.append("qualified_host_evidence_tier")

    host = evidence.get("host_qualification")
    host_fields = {
        "host_id",
        "tested_commit",
        "container_digest",
        "source_manifest_sha256",
        "tt_qualification_files",
        "qcd_qualification_files",
        "tt_pilot_files",
        "qcd_pilot_files_by_record",
    }
    if not isinstance(host, dict):
        missing.append("host_qualification")
    else:
        for field in sorted(host_fields - set(host)):
            missing.append(f"host_qualification:{field}")
        if set(host) == host_fields:
            for field in ("host_id", "tested_commit", "container_digest", "source_manifest_sha256"):
                if not isinstance(host[field], str) or not host[field]:
                    failed.append(f"host_qualification:{field}")
            for field in ("tt_qualification_files", "qcd_qualification_files"):
                if host[field] != 1:
                    failed.append(f"host_qualification:{field}")
            if (
                not isinstance(host["tt_pilot_files"], int)
                or host["tt_pilot_files"] < policy["minimum_tt_pilot_files"]
            ):
                failed.append("tt_pilot_file_coverage")
            qcd_files = host["qcd_pilot_files_by_record"]
            for record in policy["required_qcd_record_ids"]:
                if (
                    not isinstance(qcd_files, dict)
                    or not isinstance(qcd_files.get(str(record)), int)
                    or qcd_files[str(record)] < policy["minimum_qcd_pilot_files_per_record"]
                ):
                    failed.append(f"qcd_pilot_file_coverage:{record}")

    artifacts = evidence.get("artifacts")
    if not isinstance(artifacts, dict):
        missing.append("artifacts")
        artifacts = {}
    for name in policy["required_artifacts"]:
        if name not in artifacts:
            missing.append(f"artifact:{name}")
        elif not _artifact_is_valid(artifacts[name]):
            failed.append(f"artifact:{name}")

    checks = evidence.get("checks")
    if not isinstance(checks, dict):
        missing.append("checks")
        checks = {}
    for name in policy["required_checks"]:
        if name not in checks:
            missing.append(f"check:{name}")
        elif checks[name] is not True:
            failed.append(f"check:{name}")

    decisions = evidence.get("freeze_decisions")
    if not isinstance(decisions, dict):
        missing.append("freeze_decisions")
        decisions = {}
    for name in policy["required_freeze_decisions"]:
        value = decisions.get(name)
        if not isinstance(value, str) or not value or value.lower() == "unresolved":
            missing.append(f"freeze_decision:{name}")

    measurements_value = evidence.get("measurements")
    projection: dict[str, object] | None = None
    measurements: dict[str, object] = (
        measurements_value if isinstance(measurements_value, dict) else {}
    )
    for name in policy["required_measurements"]:
        if name not in measurements:
            missing.append(f"measurement:{name}")
    if not any(item.startswith("measurement:") for item in missing):
        try:
            projection = project_resources(
                measurements, reserve_fraction=float(policy["cost_reserve_fraction"])
            )
        except IntegrityError:
            failed.append("resource_measurements")
        else:
            charged_fraction = _number(measurements, "charged_no_track_fraction")
            if charged_fraction > float(policy["charged_no_track_fraction_max"]):
                failed.append("charged_no_track_fraction")
            for field, gate in (
                ("selected_qcd_jets", "qcd_yield"),
                ("selected_top_jets", "top_yield"),
            ):
                if _number(measurements, field) < int(policy["provisional_n_max_per_class"]):
                    failed.append(gate)
            projected_total = projection["projected_total_cost_usd_with_reserve"]
            if not isinstance(projected_total, (int, float)) or isinstance(
                projected_total, bool
            ):
                raise IntegrityError("E0_MEASUREMENT", "projected total cost is invalid")
            if projected_total > float(policy["working_budget_usd_max"]):
                failed.append("working_budget")

    missing = sorted(set(missing))
    failed = sorted(set(failed))
    if missing:
        status = E0Status.BLOCKED_EXTERNAL_EVIDENCE
    elif failed:
        status = E0Status.FAILED
    else:
        status = E0Status.PASSED
    identity_hash = hashlib.sha256(evidence_raw + policy_raw).hexdigest()
    audit: dict[str, Any] = {
        "schema_version": "1.0.0",
        "e0_audit_id": f"e0-{identity_hash[:16]}",
        "evidence_id": evidence["evidence_id"],
        "status": status.value,
        "formal_gate_eligible": status is E0Status.PASSED,
        "missing_evidence": missing,
        "failed_gates": failed,
        "policy_sha256": hashlib.sha256(policy_raw).hexdigest(),
        "resource_projection": projection,
        "observed": {
            "evidence_tier": evidence.get("evidence_tier"),
            "artifact_count": len(artifacts),
            "check_count": len(checks),
            "freeze_decision_count": len(decisions),
        },
    }
    audit["content_sha256"] = hashlib.sha256(_canonical_json(audit)).hexdigest()
    validate_schema_document(audit, "e0_audit")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_json(audit))
    return audit
