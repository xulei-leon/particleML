from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from particleml.contracts import (
    Artifact,
    ContractError,
    FeatureConfig,
    ModelCondition,
    RunSpec,
    Split,
    SplitConfig,
    Stage,
    ViewSpec,
    compute_document_hash,
    detect_contract_kind,
    validate_contract_document,
    validate_schema_document,
)

ZERO_HASH = "0" * 64


def _artifact(digit: str) -> dict[str, object]:
    return {"path": f"artifact-{digit}", "sha256": digit * 64, "byte_size": 1}


def valid_run(status: str) -> dict[str, object]:
    succeeded = status == "succeeded"
    document: dict[str, object] = {
        "schema_version": "1.0.0",
        "run_id": f"run-{status}",
        "study_id": "particleml-cms-2015",
        "stage": "E1",
        "status": status,
        "created_at": "2026-07-17T00:00:00Z",
        "started_at": "2026-07-17T00:00:01Z",
        "ended_at": "2026-07-17T00:00:02Z",
        "git": {"repository": "particleML", "commit": "a" * 40, "dirty": False},
        "data": {
            "dataset_name": "CMS 2015 RunIIFall15MiniAODv2",
            "source_manifest_sha256": "1" * 64,
            "canonical_dataset": _artifact("2"),
            "split_manifest": _artifact("3"),
            "preprocessing": _artifact("4"),
            "view": _artifact("5"),
            "qcd_mixture_sha256": None,
        },
        "condition": {
            "feature_config": "A",
            "train_size_per_class": 1000,
            "subset_id": "train-1000",
            "subset_seed": 7,
            "model_seed": 3,
        },
        "model": {
            "family": "deep_sets_pfn",
            "repository": "particleML",
            "revision": "a" * 40,
            "adapter_policy": "native_baseline",
            "output_head": "binary_top_qcd",
            "checkpoint": None,
            "omnilearned_index": None,
            "loaded_tensors": [],
            "skipped_tensors": [],
            "mismatched_tensors": [],
        },
        "hyperparameters": {
            "optimizer": "adam",
            "learning_rate": 0.001,
            "batch_size": 32,
            "max_epochs": 2,
            "weight_decay": 0.0,
            "early_stopping": {
                "monitor": "validation_auc",
                "mode": "max",
                "patience": 1,
                "min_delta": 0.0,
            },
            "extra": {},
        },
        "environment": {
            "python_version": "3.12.8",
            "dependency_lock_sha256": "6" * 64,
            "operating_system": "test",
            "device": {"type": "cpu", "name": "test-cpu"},
            "deterministic_algorithms": True,
            "known_nondeterminism": [],
        },
        "timing": {"wall_seconds": 1.0, "peak_gpu_memory_mib": None},
        "artifacts": {
            "run_directory": "runs/run-001",
            "resolved_config": _artifact("7"),
            "stdout_log": _artifact("8"),
            "stderr_log": _artifact("9"),
            "model_checkpoint": _artifact("a") if succeeded else None,
            "prediction_metadata": _artifact("b") if succeeded else None,
        },
        "failure": None
        if succeeded
        else {"code": "RUN_FAILED", "phase": "train", "message": "expected failure"},
    }
    if succeeded:
        document["metrics"] = {
            "best_epoch": 1,
            "validation_auc": 0.7,
            "test_auc": 0.7,
            "test_accuracy": 0.65,
            "epsilon_b_at_epsilon_s_0_30": 0.2,
            "epsilon_b_at_epsilon_s_0_50": 0.3,
            "background_rejection_at_epsilon_s_0_30": 5.0,
            "background_rejection_at_epsilon_s_0_50": 3.333,
        }
    return document


def valid_prediction() -> dict[str, object]:
    column = {"nullable": False}
    document: dict[str, object] = {
        "schema_version": "1.0.0",
        "prediction_id": "prediction-001",
        "run_id": "run-001",
        "created_at": "2026-07-17T00:00:00Z",
        "partition": "test",
        "feature_config": "A",
        "model_condition": "pretrained_omnilearned",
        "split_manifest_sha256": ZERO_HASH,
        "view_sha256": "1" * 64,
        "ordered": True,
        "row_count": 2,
        "class_counts": {"qcd": 1, "top": 1},
        "row_order_sha256": "2" * 64,
        "logical_columns": {
            "jet_id": {**column, "name": "jet_id", "dtype": "utf8"},
            "record_id": {**column, "name": "record_id", "dtype": "uint32"},
            "run": {**column, "name": "run", "dtype": "uint32"},
            "lumi": {**column, "name": "lumi", "dtype": "uint32"},
            "event": {**column, "name": "event", "dtype": "uint64"},
            "jet_index": {**column, "name": "jet_index", "dtype": "uint16"},
            "target": {
                **column,
                "name": "target",
                "dtype": "int8",
                "allowed_values": [0, 1],
            },
            "signal_score": {
                **column,
                "name": "signal_score",
                "dtype": "float32",
                "range": [0, 1],
            },
        },
        "payload": {
            "format": "npz",
            "path": "payload.npz",
            "sha256": "3" * 64,
            "byte_size": 10,
            "compression": None,
        },
        "content_hash": {
            "algorithm": "sha256",
            "canonicalization": (
                "utf8-sorted-keys-compact-json-lf-excluding-content_hash.metadata_sha256"
            ),
            "metadata_sha256": ZERO_HASH,
        },
    }
    document["content_hash"]["metadata_sha256"] = compute_document_hash(  # type: ignore[index]
        document, ("content_hash", "metadata_sha256")
    )
    return document


def test_public_contract_value_types() -> None:
    artifact = Artifact(Path("view.h5"), "a" * 64, "1.0.0")
    view = ViewSpec(FeatureConfig.A, "subset-001", 1000, 7)
    run = RunSpec(
        Stage.E1,
        ModelCondition.PRETRAINED_OMNILEARNED,
        FeatureConfig.A,
        1000,
        3,
        artifact,
        artifact,
        artifact,
    )

    assert Split.TRAIN.value == "train"
    assert view.subset_seed == 7
    assert run.checkpoint is None


def test_split_config_accepts_unique_increasing_sizes() -> None:
    config = SplitConfig("study", "manifest", "a" * 64, (10, 100, 1000), 7)

    assert config.subset_sizes == (10, 100, 1000)


@pytest.mark.parametrize(
    ("study_id", "manifest_id", "sizes", "seed"),
    [
        ("", "manifest", (10,), 7),
        ("study", "", (10,), 7),
        ("study", "manifest", (), 7),
        ("study", "manifest", (0,), 7),
        ("study", "manifest", (10, 10), 7),
        ("study", "manifest", (100, 10), 7),
        ("study", "manifest", (10,), -1),
    ],
)
def test_split_config_rejects_invalid_values(
    study_id: str, manifest_id: str, sizes: tuple[int, ...], seed: int
) -> None:
    with pytest.raises(ContractError, match="CONTRACT_VALUE"):
        SplitConfig(study_id, manifest_id, "a" * 64, sizes, seed)


def test_prediction_schema_and_semantics_accept_valid_document() -> None:
    document = valid_prediction()

    assert validate_schema_document(document, "prediction") == document
    assert validate_contract_document(document, "prediction") == document


@pytest.mark.parametrize("status", ["succeeded", "failed"])
def test_run_schema_accepts_success_and_failure_branches(status: str) -> None:
    document = valid_run(status)

    assert validate_schema_document(document, "run") == document
    assert validate_contract_document(document, "run") == document


def test_run_schema_rejects_inconsistent_outcome_branches() -> None:
    succeeded = valid_run("succeeded")
    succeeded["failure"] = {"code": "RUN_FAILED", "phase": "train", "message": "bad"}
    with pytest.raises(ContractError, match="CONTRACT_SCHEMA"):
        validate_schema_document(succeeded, "run")

    failed = valid_run("failed")
    failed["failure"] = None
    with pytest.raises(ContractError, match="CONTRACT_SCHEMA"):
        validate_schema_document(failed, "run")


def test_unknown_property_and_major_version_are_rejected() -> None:
    unknown = valid_prediction()
    unknown["unexpected"] = True
    with pytest.raises(ContractError, match="CONTRACT_SCHEMA"):
        validate_schema_document(unknown, "prediction")

    unsupported = valid_prediction()
    unsupported["schema_version"] = "2.0.0"
    with pytest.raises(ContractError, match="CONTRACT_UNSUPPORTED_MAJOR"):
        validate_schema_document(unsupported, "prediction")

    invalid_type = valid_prediction()
    invalid_type["schema_version"] = None
    with pytest.raises(ContractError, match="CONTRACT_VERSION_TYPE"):
        validate_schema_document(invalid_type, "prediction")


def test_contract_kind_detection_fails_closed() -> None:
    assert detect_contract_kind({"run_id": "run-001"}) == "run"
    with pytest.raises(ContractError, match="CONTRACT_KIND"):
        detect_contract_kind({})
    with pytest.raises(ContractError, match="CONTRACT_KIND"):
        detect_contract_kind({"run_id": "run-001", "manifest_id": "split-001"})


def test_metadata_hash_mutation_is_rejected() -> None:
    document = valid_prediction()
    mutated = deepcopy(document)
    mutated["run_id"] = "run-mutated"

    with pytest.raises(ContractError, match="CONTRACT_HASH_MISMATCH"):
        validate_contract_document(mutated, "prediction")


def test_prediction_class_counts_must_match_row_count() -> None:
    document = valid_prediction()
    document["class_counts"] = {"qcd": 1, "top": 2}
    document["content_hash"]["metadata_sha256"] = compute_document_hash(  # type: ignore[index]
        document, ("content_hash", "metadata_sha256")
    )

    with pytest.raises(ContractError, match="CONTRACT_ROW_COUNT"):
        validate_contract_document(document, "prediction")
