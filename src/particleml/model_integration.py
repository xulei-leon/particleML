"""Audited boundary for the pinned external OmniLearned dependency.

This module validates and records local software behavior.  It deliberately
does not treat workstation execution or synthetic fixtures as formal E0.5
evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from particleml.contracts import (
    ConfigurationError,
    ContractError,
    ExternalDependencyError,
    FeatureConfig,
    GateError,
    InputError,
    IntegrityError,
    ModelCondition,
)

OMNILEARNED_REVISION = "5091595d226b6021e967ab2ecfff832f40c026f6"
E05_STATUSES = {"passed", "failed", "blocked_external_evidence", "fallback_approved"}
FORMAL_EVIDENCE_ORIGIN = "qualified_runpod"

_SECRET_KEY = re.compile(r"(?i)(token|secret|password|credential|api[_-]?key|signature)")
_URL_SECRET = re.compile(r"(?i)([?&](?:token|sig|signature|key|credential)=)[^&\s]+")
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_SHELL_META = re.compile(r"[\r\n\x00]")

_COMMON_FLAGS = {
    "--revision",
    "--data-path",
    "--output-dir",
    "--feature-config",
    "--model-size",
    "--train-size-per-class",
    "--model-seed",
    "--checkpoint",
    "--use-add",
    "--num-add",
    "--use-pid",
    "--pid_idx",
}
_VALUE_FLAGS = _COMMON_FLAGS - {"--use-add", "--use-pid"}
_FORBIDDEN_FLAG_PARTS = ("conditional", "global", "cond_", "use-cond", "use-global")


@dataclass(frozen=True)
class ExternalResult:
    """Redacted outcome of one argument-array subprocess invocation."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class TensorMismatch:
    """One tensor whose source and target shapes are incompatible."""

    name: str
    source_shape: tuple[int, ...]
    target_shape: tuple[int, ...]


@dataclass(frozen=True)
class TensorLoadReport:
    """Deterministic checkpoint-to-model tensor compatibility report."""

    loaded: tuple[str, ...]
    skipped: tuple[str, ...]
    mismatched: tuple[TensorMismatch, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "loaded": list(self.loaded),
            "skipped": list(self.skipped),
            "mismatched": [asdict(item) for item in self.mismatched],
        }


def _canonical_json(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except FileNotFoundError as exc:
        raise InputError("CHECKPOINT_MISSING", f"missing file: {path}") from exc
    except OSError as exc:
        raise InputError("CHECKPOINT_READ", f"cannot read file: {path}") from exc
    return digest.hexdigest()


def _load_json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(code, f"missing JSON document: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(code, f"invalid JSON document: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(code, "document root must be an object")
    return value


def redact_secret(value: str) -> str:
    """Redact common credential forms before logs become artifacts."""

    redacted = _URL_SECRET.sub(r"\1[REDACTED]", value)
    redacted = _BEARER.sub("Bearer [REDACTED]", redacted)
    for key, env_value in os.environ.items():
        if _SECRET_KEY.search(key) and env_value:
            redacted = redacted.replace(env_value, "[REDACTED]")
    return redacted


def validate_external_argv(argv: Sequence[str]) -> tuple[str, ...]:
    """Validate the strict documented OmniLearned command allowlist."""

    if isinstance(argv, (str, bytes)):
        raise ConfigurationError("RUN_ARGV_TYPE", "argv must be an argument array")
    resolved = tuple(argv)
    if len(resolved) < 2 or not all(isinstance(item, str) and item for item in resolved):
        raise ConfigurationError("RUN_ARGV_TYPE", "argv contains an empty or non-string item")
    if resolved[1] not in {"dataloader", "train", "evaluate"}:
        raise ConfigurationError("RUN_COMMAND_NOT_ALLOWED", "unsupported OmniLearned command")
    expecting_value = False
    for item in resolved[2:]:
        if _SHELL_META.search(item):
            raise ConfigurationError("RUN_ARGUMENT_INVALID", "argument contains a control byte")
        if expecting_value:
            expecting_value = False
            continue
        if not item.startswith("--"):
            raise ConfigurationError(
                "RUN_ARGUMENT_INVALID", f"unexpected positional argument {item!r}"
            )
        lowered = item.lower()
        if any(part in lowered for part in _FORBIDDEN_FLAG_PARTS):
            raise ConfigurationError("RUN_FLAG_FORBIDDEN", f"forbidden flag {item}")
        if item not in _COMMON_FLAGS:
            raise ConfigurationError("RUN_FLAG_NOT_ALLOWED", f"undocumented flag {item}")
        expecting_value = item in _VALUE_FLAGS
    if expecting_value:
        raise ConfigurationError("RUN_ARGUMENT_INVALID", "flag is missing its value")
    revision_positions = [i for i, item in enumerate(resolved) if item == "--revision"]
    if len(revision_positions) != 1:
        raise ConfigurationError("RUN_REVISION_REQUIRED", "exactly one revision flag is required")
    revision_index = revision_positions[0] + 1
    if revision_index >= len(resolved) or resolved[revision_index] != OMNILEARNED_REVISION:
        raise ExternalDependencyError("RUN_REVISION_MISMATCH", "OmniLearned revision is not pinned")
    return resolved


def run_external(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout_seconds: float,
    environment: Mapping[str, str] | None = None,
) -> ExternalResult:
    """Run an allowlisted argument array with captured, redacted output."""

    resolved = validate_external_argv(argv)
    if timeout_seconds <= 0:
        raise ConfigurationError("RUN_TIMEOUT_INVALID", "timeout must be positive")
    if not cwd.is_dir():
        raise InputError("RUN_CWD_MISSING", f"working directory does not exist: {cwd}")
    merged_environment = None
    if environment is not None:
        merged_environment = dict(os.environ)
        merged_environment.update(environment)
    try:
        completed = subprocess.run(
            list(resolved),
            cwd=cwd,
            env=merged_environment,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = redact_secret(exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = redact_secret(exc.stderr or "") if isinstance(exc.stderr, str) else ""
        raise ExternalDependencyError(
            "RUN_TIMEOUT", f"external command timed out; stdout={stdout!r}; stderr={stderr!r}"
        ) from exc
    except OSError as exc:
        raise ExternalDependencyError(
            "RUN_EXECUTABLE", "external executable could not start"
        ) from exc
    result = ExternalResult(
        argv=tuple(redact_secret(item) for item in resolved),
        returncode=completed.returncode,
        stdout=redact_secret(completed.stdout),
        stderr=redact_secret(completed.stderr),
    )
    if completed.returncode != 0:
        raise ExternalDependencyError(
            "RUN_NONZERO_EXIT",
            f"external command returned {completed.returncode}; stderr={result.stderr!r}",
        )
    return result


def adapter_flags(feature_config: FeatureConfig) -> tuple[str, ...]:
    """Return the exact native A-D PID/additional-field flags."""

    return {
        FeatureConfig.A: (),
        FeatureConfig.B: ("--use-add", "--num-add", "1"),
        FeatureConfig.C: ("--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "1"),
        FeatureConfig.D: ("--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "5"),
    }[feature_config]


def build_index_argv(
    executable: Path, view: Path, output: Path, feature_config: FeatureConfig
) -> tuple[str, ...]:
    """Build the exact official custom-data index command."""

    argv = (
        str(executable),
        "dataloader",
        "--revision",
        OMNILEARNED_REVISION,
        "--data-path",
        str(view),
        "--output-dir",
        str(output),
        "--feature-config",
        feature_config.value,
        *adapter_flags(feature_config),
    )
    return validate_external_argv(argv)


def build_train_argv(
    executable: Path,
    index: Path,
    output: Path,
    checkpoint: Path,
    feature_config: FeatureConfig,
    *,
    model_size: str,
    train_size_per_class: int,
    model_seed: int,
) -> tuple[str, ...]:
    """Build an allowlisted train command without conflating model and data size."""

    if not model_size or train_size_per_class <= 0 or model_seed < 0:
        raise ConfigurationError("RUN_CONFIG_INVALID", "model/data sizes and seed are invalid")
    argv = (
        str(executable),
        "train",
        "--revision",
        OMNILEARNED_REVISION,
        "--data-path",
        str(index),
        "--output-dir",
        str(output),
        "--checkpoint",
        str(checkpoint),
        "--feature-config",
        feature_config.value,
        "--model-size",
        model_size,
        "--train-size-per-class",
        str(train_size_per_class),
        "--model-seed",
        str(model_seed),
        *adapter_flags(feature_config),
    )
    return validate_external_argv(argv)


def _payload_hash(root: Path, relative_files: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_files):
        path = root / relative
        if not path.is_file():
            raise IntegrityError("INDEX_FILE_MISSING", f"missing index payload {relative}")
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(bytes.fromhex(_sha256_file(path)))
    return digest.hexdigest()


def validate_index(
    index_directory: Path, *, expected_view_sha256: str, expected_row_count: int
) -> dict[str, Any]:
    """Validate a published official-index completion record and payload."""

    record = _load_json(index_directory / "COMPLETED.json", "INDEX_COMPLETION_MISSING")
    required = {
        "schema_version",
        "dependency_revision",
        "source_view_sha256",
        "feature_config",
        "row_count",
        "files",
        "payload_sha256",
        "official_smoke_loaded",
        "evidence_origin",
    }
    if set(record) != required:
        raise ContractError("INDEX_COMPLETION_FIELDS", "index completion fields are not exact")
    if record["dependency_revision"] != OMNILEARNED_REVISION:
        raise IntegrityError("INDEX_REVISION_MISMATCH", "index revision is stale")
    if record["source_view_sha256"] != expected_view_sha256:
        raise IntegrityError("INDEX_STALE_VIEW", "index source view hash is stale")
    if record["row_count"] != expected_row_count:
        raise IntegrityError("INDEX_ROW_COUNT", "index row count does not match the view")
    files = record["files"]
    if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
        raise ContractError("INDEX_FILE_LIST", "index file list must be non-empty strings")
    if len(set(files)) != len(files):
        raise ContractError("INDEX_FILE_LIST", "index file list contains duplicates")
    actual_hash = _payload_hash(index_directory, files)
    if actual_hash != record["payload_sha256"]:
        raise IntegrityError("INDEX_PAYLOAD_HASH", "index payload hash mismatch")
    if record["official_smoke_loaded"] is not True:
        raise GateError("INDEX_SMOKE_REQUIRED", "official index smoke load is not retained")
    return record


def validate_checkpoint(checkpoint: Path, metadata_path: Path) -> dict[str, Any]:
    """Validate immutable checkpoint identity, rights, corpus, normalization, and bytes."""

    metadata = _load_json(metadata_path, "CHECKPOINT_METADATA")
    required = {
        "schema_version",
        "source",
        "immutable_revision",
        "filename",
        "sha256",
        "license",
        "pretraining_corpus",
        "input_schema",
        "normalization",
    }
    if set(metadata) != required:
        raise ContractError(
            "CHECKPOINT_METADATA_FIELDS", "checkpoint metadata fields are not exact"
        )
    for field in required - {"schema_version"}:
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise ContractError("CHECKPOINT_METADATA_MISSING", f"missing checkpoint {field}")
    if metadata["immutable_revision"] in {"latest", "main", "master", "pretrain_s"}:
        raise ContractError("CHECKPOINT_MUTABLE_ID", "checkpoint revision must be immutable")
    if metadata["filename"] != checkpoint.name:
        raise IntegrityError("CHECKPOINT_FILENAME", "checkpoint filename does not match metadata")
    if _sha256_file(checkpoint) != metadata["sha256"]:
        raise IntegrityError("CHECKPOINT_HASH", "checkpoint SHA-256 mismatch")
    return metadata


def tensor_load_report(
    source_shapes: Mapping[str, Sequence[int]], target_shapes: Mapping[str, Sequence[int]]
) -> TensorLoadReport:
    """Classify every checkpoint tensor deterministically by shape compatibility."""

    loaded: list[str] = []
    skipped: list[str] = []
    mismatched: list[TensorMismatch] = []
    for name in sorted(source_shapes):
        source = tuple(int(value) for value in source_shapes[name])
        target_value = target_shapes.get(name)
        if target_value is None:
            skipped.append(name)
            continue
        target = tuple(int(value) for value in target_value)
        if source == target:
            loaded.append(name)
        else:
            mismatched.append(TensorMismatch(name, source, target))
    return TensorLoadReport(tuple(loaded), tuple(skipped), tuple(mismatched))


def fallback_model_condition(policy_path: Path) -> ModelCondition:
    """Resolve only an explicitly approved E0.5 fallback decision."""

    policy = _load_json(policy_path, "FALLBACK_POLICY")
    required = {"schema_version", "approved", "decision", "reason", "evidence_sha256"}
    if set(policy) != required or policy["approved"] is not True:
        raise GateError("FALLBACK_NOT_APPROVED", "fallback requires an explicit approved policy")
    if policy["decision"] != ModelCondition.RANDOM_OMNILEARNED.value:
        raise ConfigurationError("FALLBACK_DECISION", "unsupported fallback decision")
    if not isinstance(policy["reason"], str) or not policy["reason"]:
        raise ContractError("FALLBACK_REASON", "fallback reason is required")
    if not re.fullmatch(r"[0-9a-f]{64}", str(policy["evidence_sha256"])):
        raise ContractError("FALLBACK_EVIDENCE", "fallback evidence hash is invalid")
    return ModelCondition.RANDOM_OMNILEARNED


def aggregate_e05(evidence_path: Path, policy_path: Path, output: Path) -> dict[str, Any]:
    """Aggregate E0.5 without promoting local or synthetic evidence."""

    evidence = _load_json(evidence_path, "E05_EVIDENCE")
    policy = _load_json(policy_path, "E05_POLICY")
    checks = policy.get("required_checks")
    observed = evidence.get("checks")
    if not isinstance(checks, list) or not all(isinstance(item, str) for item in checks):
        raise ContractError("E05_POLICY", "required_checks must be a string array")
    if not isinstance(observed, dict):
        raise ContractError("E05_EVIDENCE", "checks must be an object")
    missing = sorted(item for item in checks if item not in observed)
    failed = sorted(item for item in checks if observed.get(item) is False)
    origin = evidence.get("evidence_origin")
    fallback = evidence.get("fallback_approved") is True
    if failed:
        status = "fallback_approved" if fallback else "failed"
    elif missing or origin != FORMAL_EVIDENCE_ORIGIN:
        status = "blocked_external_evidence"
    else:
        status = "passed"
    if status not in E05_STATUSES:  # pragma: no cover - defensive invariant
        raise AssertionError(status)
    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "e05_audit_id": str(evidence.get("evidence_id", "e05-unidentified")),
        "status": status,
        "formal_gate_eligible": status in {"passed", "fallback_approved"},
        "evidence_origin": origin if isinstance(origin, str) else "unknown",
        "dependency_revision": OMNILEARNED_REVISION,
        "missing_evidence": missing,
        "failed_checks": failed,
        "model_condition": (
            ModelCondition.RANDOM_OMNILEARNED.value
            if status == "fallback_approved"
            else ModelCondition.PRETRAINED_OMNILEARNED.value
        ),
        "policy_sha256": hashlib.sha256(_canonical_json(policy)).hexdigest(),
    }
    report["content_sha256"] = hashlib.sha256(_canonical_json(report)).hexdigest()
    from particleml.contracts import validate_contract_document

    validate_contract_document(report, "e05_audit")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise IntegrityError("ARTIFACT_EXISTS", f"formal output already exists: {output}")
    output.write_bytes(_canonical_json(report))
    return report
