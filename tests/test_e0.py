from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from particleml.contracts import validate_contract
from particleml.e0 import E0Status, build_e0_audit, project_resources

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "configs" / "e0" / "e0-audit-policy.json"
SCHEMA = ROOT / "schemas" / "e0-audit.schema.json"


def _complete_evidence(tier: str = "qualified_host") -> dict[str, object]:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    artifacts = {
        name: {
            "path": f"/artifacts/{name}",
            "sha256": format(index + 1, "x")[-1] * 64,
            "completed": True,
        }
        for index, name in enumerate(policy["required_artifacts"])
    }
    checks = {name: True for name in policy["required_checks"]}
    measurements = {
        "source_bytes": 1_000_000,
        "events_processed": 1_000,
        "cpu_seconds": 500.0,
        "wall_seconds": 250.0,
        "failed_files": 0,
        "total_files": 12,
        "compact_bytes": 200_000,
        "canonical_bytes": 300_000,
        "view_bytes": 400_000,
        "selected_qcd_jets": 120_000,
        "selected_top_jets": 110_000,
        "charged_no_track_fraction": 0.005,
        "e0_base_cost_usd": 40.0,
        "e1_base_cost_usd": 60.0,
        "e2_base_cost_usd": 120.0,
    }
    decisions = {name: "frozen-test-value" for name in policy["required_freeze_decisions"]}
    return {
        "schema_version": "1.0.0",
        "evidence_id": "e0-fixture",
        "evidence_tier": tier,
        "host_qualification": {
            "host_id": "qualified-host",
            "tested_commit": "a" * 40,
            "container_digest": "sha256:" + "b" * 64,
            "source_manifest_sha256": "c" * 64,
            "tt_qualification_files": 1,
            "qcd_qualification_files": 1,
            "tt_pilot_files": 5,
            "qcd_pilot_files_by_record": {
                "18355": 2,
                "18358": 2,
                "18373": 2,
                "18376": 2,
                "18377": 2,
            },
        },
        "artifacts": artifacts,
        "measurements": measurements,
        "checks": checks,
        "freeze_decisions": decisions,
    }


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")
    return path


def test_resource_projection_includes_reserve() -> None:
    projection = project_resources(
        {
            "source_bytes": 1_000,
            "events_processed": 100,
            "cpu_seconds": 50.0,
            "wall_seconds": 20.0,
            "failed_files": 1,
            "total_files": 10,
            "compact_bytes": 200,
            "canonical_bytes": 300,
            "view_bytes": 400,
            "selected_qcd_jets": 100_000,
            "selected_top_jets": 100_000,
            "charged_no_track_fraction": 0.0,
            "e0_base_cost_usd": 20.0,
            "e1_base_cost_usd": 40.0,
            "e2_base_cost_usd": 80.0,
        },
        reserve_fraction=0.25,
    )

    assert projection["source_bytes_per_wall_second"] == 50.0
    assert projection["cpu_seconds_per_event"] == 0.5
    assert projection["file_failure_fraction"] == 0.1
    assert projection["projected_cost_usd_with_reserve"] == {
        "E0": 25.0,
        "E1": 50.0,
        "E2": 100.0,
    }


def test_missing_external_evidence_is_retained_as_blocked(tmp_path: Path) -> None:
    evidence = {
        "schema_version": "1.0.0",
        "evidence_id": "unresolved-e0",
        "evidence_tier": "fixture",
        "host_qualification": None,
        "artifacts": {},
        "measurements": {},
        "checks": {},
        "freeze_decisions": {},
    }
    output = tmp_path / "audit.json"

    audit = build_e0_audit(_write(tmp_path / "evidence.json", evidence), POLICY, output)

    assert audit["status"] == E0Status.BLOCKED_EXTERNAL_EVIDENCE.value
    assert "qualified_host_evidence_tier" in audit["missing_evidence"]
    assert audit["formal_gate_eligible"] is False


def test_fixture_cannot_promote_a_complete_formal_gate(tmp_path: Path) -> None:
    output = tmp_path / "audit.json"

    audit = build_e0_audit(
        _write(tmp_path / "evidence.json", _complete_evidence("fixture")), POLICY, output
    )

    assert audit["status"] == E0Status.BLOCKED_EXTERNAL_EVIDENCE.value
    assert audit["formal_gate_eligible"] is False


def test_qualified_host_evidence_can_pass_or_fail_deterministically(tmp_path: Path) -> None:
    passing = _complete_evidence()
    passed = build_e0_audit(
        _write(tmp_path / "passing.json", passing), POLICY, tmp_path / "passed.json"
    )
    assert passed["status"] == E0Status.PASSED.value
    assert passed["formal_gate_eligible"] is True

    failing = _complete_evidence()
    failing["measurements"]["charged_no_track_fraction"] = 0.02  # type: ignore[index]
    failed = build_e0_audit(
        _write(tmp_path / "failing.json", failing), POLICY, tmp_path / "failed.json"
    )
    assert failed["status"] == E0Status.FAILED.value
    assert "charged_no_track_fraction" in failed["failed_gates"]


def test_e0_output_satisfies_schema(tmp_path: Path) -> None:
    output = tmp_path / "audit.json"
    audit = build_e0_audit(
        _write(tmp_path / "evidence.json", _complete_evidence()),
        POLICY,
        output,
    )
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    Draft202012Validator(schema).validate(audit)
    assert validate_contract(output) == "e0_audit"


@pytest.mark.parametrize("field", ["wall_seconds", "events_processed", "total_files"])
def test_invalid_measurement_denominators_fail_closed(field: str) -> None:
    measurements = _complete_evidence()["measurements"]
    measurements[field] = 0  # type: ignore[index]

    with pytest.raises(Exception, match="E0_MEASUREMENT"):
        project_resources(measurements, reserve_fraction=0.25)  # type: ignore[arg-type]
