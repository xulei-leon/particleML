from __future__ import annotations

import json
from pathlib import Path

import pytest

from particleml.contracts import GateError, ModelCondition
from particleml.model_integration import aggregate_e05, fallback_model_condition


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

