from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from particleml.contracts import GateError, IntegrityError, Stage
from particleml.experiment import (
    dry_run_ledger,
    failure_record,
    matrix_status,
    publish_run_record,
    resolve_matrix,
    run_subprocess_once,
    validate_stage_gates,
)
from tests.test_contracts import valid_run

HASH = "a" * 64


def _gates() -> dict[str, dict[str, object]]:
    return {
        "E0": {"status": "passed", "formal_gate_eligible": True, "content_sha256": HASH},
        "E0.5": {
            "status": "passed",
            "formal_gate_eligible": True,
            "content_sha256": "b" * 64,
        },
    }


def _config(path: Path) -> Path:
    document = {
        "schema_version": "1.0.0",
        "study_id": "cms2015-feature-availability-v04",
        "stage": "E1",
        "feature_configs": ["A", "D"],
        "train_sizes_per_class": [1000, 10000],
        "model_seeds": [7],
        "model_condition": "pretrained_omnilearned",
        "mandatory": True,
        "dependency_hashes": {"view": "c" * 64, "checkpoint": "d" * 64},
    }
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_gate_order_and_matrix(tmp_path: Path) -> None:
    with pytest.raises(GateError, match="RUN_GATE_BLOCKED"):
        validate_stage_gates(Stage.E1, {"E0": _gates()["E0"]})
    config = _config(tmp_path / "e1.json")
    first = resolve_matrix(config, _gates())
    second = resolve_matrix(config, _gates())
    assert len(first) == 4
    assert first == second
    assert len({item.condition_id for item in first}) == 4
    assert {(item.feature_config.value, item.train_size_per_class) for item in first} == {
        ("A", 1000), ("A", 10000), ("D", 1000), ("D", 10000)
    }


def test_dry_run_is_nonpublishing_and_reports_gate_block(tmp_path: Path) -> None:
    config = _config(tmp_path / "e1.json")
    blocked = dry_run_ledger(config, {})
    assert blocked["status"] == "blocked"
    assert blocked["conditions"] == []
    assert list(tmp_path.iterdir()) == [config]


def test_failure_lifecycle_is_visible_and_immutable(tmp_path: Path) -> None:
    record = failure_record(
        valid_run("failed"),
        status="timed_out",
        code="RUN_TIMEOUT",
        phase="train",
        message="timeout token=redacted",
    )
    output = tmp_path / "run-record.json"
    publish_run_record(record, output)
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "timed_out"
    with pytest.raises(IntegrityError, match="ARTIFACT_EXISTS"):
        publish_run_record(record, output)


def test_run_subprocess_attempts_once_and_retains_nonzero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = 0

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(argv, 9, "partial", "failure")

    monkeypatch.setattr(subprocess, "run", fake_run)
    outcome = run_subprocess_once(["trainer", "--config", "x"], cwd=tmp_path, timeout_seconds=3)
    assert calls == 1
    assert outcome.status == "failed"
    assert outcome.failure_code == "RUN_NONZERO_EXIT"


def test_matrix_status_retains_missing_and_failed(tmp_path: Path) -> None:
    specs = resolve_matrix(_config(tmp_path / "e1.json"), _gates())
    records = {specs[0].condition_id: {"status": "failed"}}
    statuses = matrix_status(specs, records)
    assert statuses[0]["status"] == "failed"
    assert sum(item["status"] == "missing" for item in statuses) == 3


def test_e2_matrix_has_all_36_frozen_conditions(tmp_path: Path) -> None:
    config = json.loads(_config(tmp_path / "e2.json").read_text(encoding="utf-8"))
    config.update(
        stage="E2",
        feature_configs=["A", "B", "C", "D"],
        train_sizes_per_class=[1000, 10000, 100000],
        model_seeds=[1, 2, 3],
    )
    path = tmp_path / "e2.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    gates = _gates()
    gates["E1"] = {"status": "passed", "content_sha256": "e" * 64}
    gates["E2_budget"] = {"status": "passed", "content_sha256": "f" * 64}
    specs = resolve_matrix(path, gates)
    assert len(specs) == 36
    assert len({item.condition_id for item in specs}) == 36


def test_e3_fixture_matrix_has_a_d_and_three_seeds(tmp_path: Path) -> None:
    config = json.loads(_config(tmp_path / "e3.json").read_text(encoding="utf-8"))
    config.update(
        stage="E3",
        feature_configs=["A", "D"],
        train_sizes_per_class=[123],
        model_seeds=[1, 2, 3],
        model_condition="deep_sets_pfn",
    )
    path = tmp_path / "e3.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    gates = _gates()
    gates["E1"] = {"status": "passed", "content_sha256": "e" * 64}
    gates["E2"] = {"status": "passed", "content_sha256": "f" * 64}
    specs = resolve_matrix(path, gates)
    assert len(specs) == 6
    assert {item.feature_config.value for item in specs} == {"A", "D"}
