from __future__ import annotations

import json
from pathlib import Path

import pytest

from particleml.artifacts import publish_artifact
from particleml.contracts import GateError, IntegrityError, ModelCondition
from particleml.model_integration import aggregate_e05, fallback_model_condition
from particleml.reporting import (
    build_claim_ledger,
    build_report,
    validate_status_monotonicity,
)
from tests.test_contracts import valid_run


def test_local_fixture_cannot_promote_e05(tmp_path: Path) -> None:
    policy = {"schema_version": "1.0.0", "required_checks": ["index_A", "finite_A"]}
    evidence = {
        "evidence_id": "local-fixture",
        "evidence_origin": "local_fixture",
        "checks": {"index_A": True, "finite_A": True},
    }
    policy_path = tmp_path / "policy.json"
    evidence_path = tmp_path / "evidence.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    report = aggregate_e05(evidence_path, policy_path, tmp_path / "audit.json")
    assert report["status"] == "blocked_external_evidence"
    assert report["formal_gate_eligible"] is False


def test_fallback_requires_explicit_approval_and_narrows_model_condition(tmp_path: Path) -> None:
    path = tmp_path / "fallback.json"
    policy = {
        "schema_version": "1.0.0",
        "approved": False,
        "decision": None,
        "reason": "not approved",
        "evidence_sha256": None,
    }
    path.write_text(json.dumps(policy), encoding="utf-8")
    with pytest.raises(GateError, match="FALLBACK_NOT_APPROVED"):
        fallback_model_condition(path)
    policy.update(
        approved=True,
        decision=ModelCondition.RANDOM_OMNILEARNED.value,
        reason="native checkpoint compatibility failed",
        evidence_sha256="a" * 64,
    )
    path.write_text(json.dumps(policy), encoding="utf-8")
    assert fallback_model_condition(path) is ModelCondition.RANDOM_OMNILEARNED


def test_status_monotonicity_and_fallback_narrow_claims() -> None:
    with pytest.raises(IntegrityError, match="REPORT_STATUS_MONOTONICITY"):
        validate_status_monotonicity(
            {"upstream": "implemented", "claim": "verified"},
            {"claim": ["upstream"]},
        )
    ledger = build_claim_ledger(
        [
            {
                "claim_id": "transfer",
                "text": "pretrained transfer claim",
                "category": "pretrained_transfer",
                "dependencies": ["AC-E2-001"],
            }
        ],
        {"AC-E2-001": "verified"},
        supervised_fallback=True,
        e3_deferred=False,
    )
    assert ledger[0]["eligible"] is False
    assert "supervised_fallback_removes_pretrained_transfer" in ledger[0]["reasons"]


def _report_config(path: Path, expected: list[str]) -> Path:
    document = {
        "schema_version": "1.0.0",
        "report_id": "fixture-report",
        "expected_condition_ids": expected,
        "evidence_statuses": {"AC-E2-001": "deferred"},
        "status_dependencies": {},
        "supervised_fallback": False,
        "e3_deferred": True,
        "uncertainty_conventions": {
            "event_level": "paired bootstrap percentile interval",
            "model_seed_level": "per-seed mean and sample standard deviation",
        },
        "claims": [],
    }
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _publish_record(root: Path, name: str, record: dict[str, object]) -> Path:
    def writer(directory: Path) -> None:
        (directory / "run-record.json").write_text(json.dumps(record), encoding="utf-8")

    artifact = publish_artifact(
        root / name,
        writer,
        lambda _directory: None,
        {"fixture": "a" * 64},
        "b" * 64,
        "test-run-record",
    )
    return artifact.path / "run-record.json"


def test_reports_are_deterministic_and_keep_failed_missing_visible(tmp_path: Path) -> None:
    succeeded = valid_run("succeeded")
    failed = valid_run("failed")
    success_path = _publish_record(tmp_path, "success", succeeded)
    failure_path = _publish_record(tmp_path, "failure", failed)
    config = _report_config(
        tmp_path / "report-config.json",
        ["run-succeeded", "run-failed", "run-missing"],
    )
    first = build_report(config, [success_path, failure_path], tmp_path / "report-a")
    second = build_report(config, [success_path, failure_path], tmp_path / "report-b")
    first_bytes = (first / "report.json").read_bytes()
    assert first_bytes == (second / "report.json").read_bytes()
    report = json.loads(first_bytes)
    assert [row["status"] for row in report["matrix_status"]] == [
        "succeeded", "failed", "missing"
    ]
    assert len(report["successful_metrics"]) == 1
    first_marker = json.loads((first / "COMPLETED.json").read_text(encoding="utf-8"))
    second_marker = json.loads((second / "COMPLETED.json").read_text(encoding="utf-8"))
    assert first_marker["artifact_sha256"] == second_marker["artifact_sha256"]


def test_incomplete_report_never_invents_scientific_outputs(tmp_path: Path) -> None:
    config = _report_config(tmp_path / "report-config.json", [])
    output = build_report(config, [], tmp_path / "report")
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["successful_metrics"] == []
    assert report["outputs"]["F1"]["status"].startswith("ineligible")
    assert report["outputs"]["T2"] == {"status": "generated", "rows": []}


def test_report_rejects_mutated_completed_input(tmp_path: Path) -> None:
    record_path = _publish_record(tmp_path, "run", valid_run("succeeded"))
    record_path.write_text("{}", encoding="utf-8")
    config = _report_config(tmp_path / "report-config.json", ["run-succeeded"])
    with pytest.raises(IntegrityError, match="ARTIFACT_HASH_MISMATCH"):
        build_report(config, [record_path], tmp_path / "report")
