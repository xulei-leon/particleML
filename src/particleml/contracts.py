"""Public value types and serialized-contract validation."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SUPPORTED_SCHEMA_MAJOR = 1
SCHEMA_PATHS = {
    "run": "run-record.schema.json",
    "split": "split-manifest.schema.json",
    "prediction": "prediction.schema.json",
    "e0_audit": "e0-audit.schema.json",
}


class ParticleMLError(Exception):
    """Base exception with a stable machine-readable code and CLI exit code."""

    exit_code = 2

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class ConfigurationError(ParticleMLError):
    """CLI syntax or configuration error."""

    exit_code = 2


class InputError(ParticleMLError):
    """Missing or unreadable input."""

    exit_code = 3


class ContractError(ParticleMLError):
    """Serialized schema or contract error."""

    exit_code = 4


class IntegrityError(ParticleMLError):
    """Scientific identity, overlap, or content-integrity error."""

    exit_code = 5


class ExternalDependencyError(ParticleMLError):
    """External dependency or subprocess error."""

    exit_code = 6


class ExecutionError(ParticleMLError):
    """Training or evaluation failure after execution began."""

    exit_code = 7


class GateError(ParticleMLError):
    """Required scientific gate is not passed."""

    exit_code = 8


class Split(str, Enum):
    """Frozen dataset partition vocabulary."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class FeatureConfig(str, Enum):
    """Nested A-D feature configurations."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Stage(str, Enum):
    """Experiment-stage vocabulary."""

    E0 = "E0"
    E05 = "E0.5"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"


class ModelCondition(str, Enum):
    """Model-condition vocabulary shared by run and prediction contracts."""

    PRETRAINED_OMNILEARNED = "pretrained_omnilearned"
    RANDOM_OMNILEARNED = "random_initialized_omnilearned"
    DEEP_SETS_PFN = "deep_sets_pfn"


def _require_sha256(value: str, field: str) -> None:
    if not SHA256_PATTERN.fullmatch(value):
        raise ContractError("CONTRACT_HASH_FORMAT", f"{field} must be lowercase SHA-256")


@dataclass(frozen=True)
class Artifact:
    """Content-addressed artifact identity."""

    path: Path
    sha256: str
    schema_version: str | None = None

    def __post_init__(self) -> None:
        _require_sha256(self.sha256, "Artifact.sha256")


@dataclass(frozen=True)
class ViewSpec:
    """Immutable view-selection values."""

    feature_config: FeatureConfig
    subset_id: str
    train_size_per_class: int
    subset_seed: int

    def __post_init__(self) -> None:
        if not self.subset_id:
            raise ContractError("CONTRACT_VALUE", "ViewSpec.subset_id must not be empty")
        if self.train_size_per_class <= 0 or self.subset_seed < 0:
            raise ContractError("CONTRACT_VALUE", "ViewSpec size and seed are invalid")


@dataclass(frozen=True)
class RunSpec:
    """Immutable inputs for a future execution stage."""

    stage: Stage
    model_condition: ModelCondition
    feature_config: FeatureConfig
    train_size_per_class: int
    model_seed: int
    view: Artifact
    split_manifest: Artifact
    preprocessing: Artifact
    checkpoint: Artifact | None = None

    def __post_init__(self) -> None:
        if self.train_size_per_class <= 0 or self.model_seed < 0:
            raise ContractError("CONTRACT_VALUE", "RunSpec size and seed are invalid")


@dataclass(frozen=True)
class SplitConfig:
    """Deterministic split/subset configuration loaded from versioned JSON."""

    study_id: str
    manifest_id: str
    source_manifest_sha256: str
    subset_sizes: tuple[int, ...]
    subset_seed: int

    def __post_init__(self) -> None:
        _require_sha256(self.source_manifest_sha256, "SplitConfig.source_manifest_sha256")
        if not self.study_id or not self.manifest_id:
            raise ContractError("CONTRACT_VALUE", "SplitConfig identifiers must not be empty")
        if not self.subset_sizes or any(size <= 0 for size in self.subset_sizes):
            raise ContractError("CONTRACT_VALUE", "SplitConfig subset sizes must be positive")
        if tuple(sorted(set(self.subset_sizes))) != self.subset_sizes or self.subset_seed < 0:
            raise ContractError("CONTRACT_VALUE", "SplitConfig sizes must be unique and increasing")


def _schema_root() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas"


def _load_schema(kind: str) -> dict[str, Any]:
    try:
        filename = SCHEMA_PATHS[kind]
    except KeyError as exc:
        raise ContractError("CONTRACT_KIND", f"unsupported contract kind: {kind}") from exc
    path = _schema_root() / filename
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("CONTRACT_SCHEMA_SOURCE", f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("CONTRACT_SCHEMA_SOURCE", f"schema is not an object: {path}")
    return value


def _validate_major_version(document: dict[str, Any]) -> None:
    value = document.get("schema_version")
    if not isinstance(value, str):
        raise ContractError("CONTRACT_VERSION_TYPE", "schema_version must be a string")
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", value)
    if match and int(match.group(1)) != SUPPORTED_SCHEMA_MAJOR:
        raise ContractError(
            "CONTRACT_UNSUPPORTED_MAJOR",
            f"schema major {match.group(1)} is unsupported",
        )


def validate_schema_document(document: dict[str, Any], kind: str) -> dict[str, Any]:
    """Validate a document against one Draft 2020-12 schema."""

    _validate_major_version(document)
    validator = Draft202012Validator(_load_schema(kind), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ContractError("CONTRACT_SCHEMA", f"{kind} {location}: {error.message}")
    return document


def compute_document_hash(document: dict[str, Any], excluded_path: tuple[str, ...]) -> str:
    """Hash canonical JSON after removing one self-referential digest field."""

    if not excluded_path:
        raise ValueError("excluded_path must not be empty")
    canonical = deepcopy(document)
    parent: dict[str, Any] = canonical
    for key in excluded_path[:-1]:
        child = parent.get(key)
        if not isinstance(child, dict):
            raise ContractError(
                "CONTRACT_HASH_FIELD", f"missing object at {'.'.join(excluded_path)}"
            )
        parent = child
    if excluded_path[-1] not in parent:
        raise ContractError("CONTRACT_HASH_FIELD", f"missing field {'.'.join(excluded_path)}")
    del parent[excluded_path[-1]]
    payload = (
        json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _validate_embedded_hash(document: dict[str, Any], excluded_path: tuple[str, ...]) -> None:
    current: Any = document
    for key in excluded_path:
        if not isinstance(current, dict) or key not in current:
            raise ContractError("CONTRACT_HASH_FIELD", f"missing field {'.'.join(excluded_path)}")
        current = current[key]
    if not isinstance(current, str) or current != compute_document_hash(document, excluded_path):
        raise ContractError("CONTRACT_HASH_MISMATCH", f"invalid {'.'.join(excluded_path)}")


def _validate_prediction_semantics(document: dict[str, Any]) -> None:
    class_counts = document["class_counts"]
    if class_counts["qcd"] + class_counts["top"] != document["row_count"]:
        raise ContractError("CONTRACT_ROW_COUNT", "prediction class counts do not equal row_count")
    _validate_embedded_hash(document, ("content_hash", "metadata_sha256"))


def _validate_split_semantics(document: dict[str, Any]) -> None:
    from particleml.manifest import assign_split, hash_canonical_pfn, split_bucket

    seen: set[str] = set()
    for source in document["source_files"]:
        pfn = source["canonical_pfn"]
        if pfn in seen:
            raise ContractError("CONTRACT_PFN_DUPLICATE", f"duplicate PFN: {pfn}")
        seen.add(pfn)
        if source["pfn_sha256"] != hash_canonical_pfn(pfn):
            raise ContractError("CONTRACT_HASH_MISMATCH", f"invalid PFN hash: {pfn}")
        if source["bucket"] != split_bucket(pfn) or source["split"] != assign_split(pfn).value:
            raise ContractError("CONTRACT_SPLIT_MISMATCH", f"invalid split assignment: {pfn}")
    _validate_embedded_hash(document, ("hash_metadata", "content_sha256"))


def _validate_e0_audit_semantics(document: dict[str, Any]) -> None:
    status = document["status"]
    eligible = document["formal_gate_eligible"]
    if eligible != (status == "passed"):
        raise ContractError("CONTRACT_GATE_STATUS", "E0 eligibility does not match status")
    if status == "passed" and (document["missing_evidence"] or document["failed_gates"]):
        raise ContractError("CONTRACT_GATE_STATUS", "passed E0 audit retains blocking items")
    if status == "blocked_external_evidence" and not document["missing_evidence"]:
        raise ContractError("CONTRACT_GATE_STATUS", "blocked E0 audit needs missing evidence")
    _validate_embedded_hash(document, ("content_sha256",))


def validate_contract_document(document: dict[str, Any], kind: str) -> dict[str, Any]:
    """Run JSON Schema and cross-field semantic validation."""

    validate_schema_document(document, kind)
    if kind == "prediction":
        _validate_prediction_semantics(document)
    elif kind == "split":
        _validate_split_semantics(document)
    elif kind == "e0_audit":
        _validate_e0_audit_semantics(document)
    return document


def detect_contract_kind(document: dict[str, Any]) -> str:
    """Detect the contract family from its stable identifier field."""

    matches = [
        kind
        for kind, identifier in (
            ("run", "run_id"),
            ("split", "manifest_id"),
            ("prediction", "prediction_id"),
            ("e0_audit", "e0_audit_id"),
        )
        if identifier in document
    ]
    if len(matches) != 1:
        raise ContractError("CONTRACT_KIND", "cannot uniquely detect contract kind")
    return matches[0]


def validate_contract(path: Path) -> str:
    """Load and validate one run, split, or prediction JSON document."""

    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputError("INPUT_NOT_FOUND", f"input does not exist: {path}") from exc
    except OSError as exc:
        raise InputError("INPUT_UNREADABLE", f"cannot read {path}: {exc}") from exc
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError("CONTRACT_JSON", f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ContractError("CONTRACT_JSON", "contract root must be an object")
    kind = detect_contract_kind(document)
    validate_contract_document(document, kind)
    return kind
