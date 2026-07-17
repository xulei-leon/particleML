"""Deterministic, gate-aware experiment planning and immutable run lifecycle."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from particleml.contracts import (
    ConfigurationError,
    ExecutionError,
    FeatureConfig,
    GateError,
    IntegrityError,
    ModelCondition,
    Stage,
    validate_contract_document,
)
from particleml.model_integration import redact_secret

OutcomeStatus = Literal["succeeded", "failed", "timed_out", "interrupted"]

_STAGE_PREREQUISITES: dict[Stage, tuple[str, ...]] = {
    Stage.E0: (),
    Stage.E05: ("E0",),
    Stage.E1: ("E0", "E0.5"),
    Stage.E2: ("E0", "E0.5", "E1", "E2_budget"),
    Stage.E3: ("E0", "E0.5", "E1", "E2"),
}


@dataclass(frozen=True)
class RunSpec:
    """One stable condition resolved from a frozen stage matrix."""

    condition_id: str
    stage: Stage
    feature_config: FeatureConfig
    train_size_per_class: int
    model_condition: ModelCondition
    model_seed: int
    mandatory: bool
    configuration_sha256: str
    dependency_hashes: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["stage"] = self.stage.value
        document["feature_config"] = self.feature_config.value
        document["model_condition"] = self.model_condition.value
        document["dependency_hashes"] = dict(self.dependency_hashes)
        return document


@dataclass(frozen=True)
class AttemptOutcome:
    """One and only one process attempt; retry policy intentionally does not exist."""

    status: OutcomeStatus
    returncode: int | None
    stdout: str
    stderr: str
    failure_code: str | None


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError("RUN_CONFIG_INVALID", f"cannot load configuration {path}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError("RUN_CONFIG_INVALID", "configuration root must be an object")
    return value


def _require_hash(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise IntegrityError("RUN_HASH_INVALID", f"{field} is not a SHA-256")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise IntegrityError("RUN_HASH_INVALID", f"{field} is not a SHA-256") from exc
    return value


def validate_stage_gates(stage: Stage, gates: Mapping[str, Mapping[str, Any]]) -> None:
    """Reject a stage when a mandatory upstream gate is absent, stale, or ineligible."""

    failures: list[str] = []
    for gate_name in _STAGE_PREREQUISITES[stage]:
        gate = gates.get(gate_name)
        if gate is None:
            failures.append(f"{gate_name}:missing")
            continue
        if gate.get("formal_gate_eligible") is not True and gate.get("status") != "passed":
            failures.append(f"{gate_name}:{gate.get('status', 'invalid')}")
        digest = gate.get("content_sha256")
        try:
            _require_hash(digest, f"gate {gate_name}")
        except IntegrityError:
            failures.append(f"{gate_name}:invalid_hash")
    if failures:
        raise GateError("RUN_GATE_BLOCKED", ", ".join(failures))


def _matrix_axes(config: Mapping[str, Any]) -> tuple[list[str], list[int], list[int]]:
    allowed = {
        "schema_version",
        "study_id",
        "stage",
        "feature_configs",
        "train_sizes_per_class",
        "model_seeds",
        "model_condition",
        "mandatory",
        "dependency_hashes",
    }
    if set(config) != allowed:
        unknown = sorted(set(config) - allowed)
        missing = sorted(allowed - set(config))
        raise ConfigurationError(
            "RUN_CONFIG_KEYS", f"configuration keys differ; unknown={unknown}, missing={missing}"
        )
    features = config["feature_configs"]
    sizes = config["train_sizes_per_class"]
    seeds = config["model_seeds"]
    if not isinstance(features, list) or not isinstance(sizes, list) or not isinstance(seeds, list):
        raise ConfigurationError("RUN_CONFIG_INVALID", "matrix axes must be arrays")
    if not features or not sizes or not seeds or len(set(features)) != len(features):
        raise ConfigurationError("RUN_CONFIG_INVALID", "matrix axes are empty or duplicated")
    if not all(isinstance(item, str) for item in features):
        raise ConfigurationError("RUN_CONFIG_INVALID", "feature configs must be strings")
    if not all(isinstance(item, int) and item > 0 for item in sizes):
        raise ConfigurationError("RUN_CONFIG_INVALID", "train sizes must be positive integers")
    if not all(isinstance(item, int) and item >= 0 for item in seeds):
        raise ConfigurationError("RUN_CONFIG_INVALID", "model seeds must be non-negative integers")
    return features, sizes, seeds


def resolve_matrix(config_path: Path, gates: Mapping[str, Mapping[str, Any]]) -> list[RunSpec]:
    """Resolve and gate one complete frozen experiment matrix deterministically."""

    config = _load_json(config_path)
    features, sizes, seeds = _matrix_axes(config)
    try:
        stage = Stage(config["stage"])
        model_condition = ModelCondition(config["model_condition"])
        feature_values = [FeatureConfig(value) for value in features]
    except (ValueError, KeyError) as exc:
        raise ConfigurationError(
            "RUN_CONFIG_INVALID", "stage, model, or feature value is invalid"
        ) from exc
    validate_stage_gates(stage, gates)
    dependencies = config["dependency_hashes"]
    if not isinstance(dependencies, dict) or not dependencies:
        raise ConfigurationError("RUN_CONFIG_INVALID", "dependency_hashes must be non-empty")
    normalized_dependencies = tuple(
        sorted((str(name), _require_hash(value, str(name))) for name, value in dependencies.items())
    )
    config_sha256 = hashlib.sha256(_canonical_json(config)).hexdigest()
    specs: list[RunSpec] = []
    for feature in feature_values:
        for size in sizes:
            for seed in seeds:
                identity = {
                    "study_id": config["study_id"],
                    "stage": stage.value,
                    "feature_config": feature.value,
                    "train_size_per_class": size,
                    "model_condition": model_condition.value,
                    "model_seed": seed,
                    "configuration_sha256": config_sha256,
                }
                suffix = hashlib.sha256(_canonical_json(identity)).hexdigest()[:12]
                condition_id = (
                    f"{stage.value.lower().replace('.', '')}-{model_condition.value}-"
                    f"{feature.value.lower()}-n{size}-s{seed}-{suffix}"
                )
                specs.append(
                    RunSpec(
                        condition_id=condition_id,
                        stage=stage,
                        feature_config=feature,
                        train_size_per_class=size,
                        model_condition=model_condition,
                        model_seed=seed,
                        mandatory=config["mandatory"] is True,
                        configuration_sha256=config_sha256,
                        dependency_hashes=normalized_dependencies,
                    )
                )
    return specs


def dry_run_ledger(
    config_path: Path, gates: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    """Return a deterministic non-publishing plan, including gate diagnostics."""

    try:
        specs = resolve_matrix(config_path, gates)
    except GateError as exc:
        return {"status": "blocked", "code": exc.code, "message": exc.message, "conditions": []}
    return {
        "status": "runnable",
        "code": None,
        "message": None,
        "conditions": [spec.to_dict() for spec in specs],
    }


def run_subprocess_once(
    argv: Sequence[str], *, cwd: Path, timeout_seconds: float
) -> AttemptOutcome:
    """Execute one process attempt with no retry and retain all available logs."""

    if (
        isinstance(argv, (str, bytes))
        or not argv
        or not all(isinstance(item, str) for item in argv)
    ):
        raise ConfigurationError("RUN_ARGV_TYPE", "argv must be a non-empty argument array")
    if timeout_seconds <= 0 or not cwd.is_dir():
        raise ConfigurationError("RUN_EXECUTION_CONFIG", "cwd and timeout are invalid")
    try:
        result = subprocess.run(
            list(argv),
            cwd=cwd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return AttemptOutcome(
            "timed_out",
            None,
            redact_secret(exc.stdout) if isinstance(exc.stdout, str) else "",
            redact_secret(exc.stderr) if isinstance(exc.stderr, str) else "",
            "RUN_TIMEOUT",
        )
    except KeyboardInterrupt:
        return AttemptOutcome("interrupted", None, "", "", "RUN_INTERRUPTED")
    except OSError as exc:
        raise ExecutionError("RUN_PROCESS_START", "training process could not start") from exc
    status: OutcomeStatus = "succeeded" if result.returncode == 0 else "failed"
    return AttemptOutcome(
        status,
        result.returncode,
        redact_secret(result.stdout),
        redact_secret(result.stderr),
        None if status == "succeeded" else "RUN_NONZERO_EXIT",
    )


def failure_record(
    base_record: Mapping[str, Any], *, status: OutcomeStatus, code: str, phase: str, message: str
) -> dict[str, Any]:
    """Create a schema-oriented failure variant without success-only metrics."""

    if status == "succeeded":
        raise ConfigurationError("RUN_FAILURE_STATUS", "failure record cannot be succeeded")
    record = deepcopy(dict(base_record))
    record["status"] = status
    record["ended_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record.pop("metrics", None)
    artifacts = record.get("artifacts")
    if isinstance(artifacts, dict):
        artifacts["model_checkpoint"] = None
        artifacts["prediction_metadata"] = None
    record["failure"] = {"code": code, "phase": phase, "message": redact_secret(message)}
    return record


def publish_run_record(record: Mapping[str, Any], output: Path) -> Path:
    """Validate and immutably publish one final run outcome record."""

    document = deepcopy(dict(record))
    validate_contract_document(document, "run")
    if output.exists():
        raise IntegrityError("ARTIFACT_EXISTS", f"run record already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_json(document))
    return output


def matrix_status(
    planned: Sequence[RunSpec], records: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """Keep every planned condition visible, including missing and failed outcomes."""

    result: list[dict[str, Any]] = []
    for spec in planned:
        record = records.get(spec.condition_id)
        status = "missing" if record is None else str(record.get("status", "invalid"))
        result.append(
            {
                "condition_id": spec.condition_id,
                "mandatory": spec.mandatory,
                "status": status,
            }
        )
    return result
