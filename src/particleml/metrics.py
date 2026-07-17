"""Small deterministic numerical probes used by data audits."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from particleml.artifacts import publish_artifact
from particleml.contracts import ContractError, IntegrityError, compute_document_hash


@dataclass(frozen=True)
class PredictionArrays:
    """Aligned per-jet identities, binary targets, and finite signal scores."""

    jet_ids: tuple[str, ...]
    targets: NDArray[np.int8]
    scores: NDArray[np.float64]


@dataclass(frozen=True)
class PairedBootstrapResult:
    """Event-bootstrap uncertainty kept separate from model-seed variation."""

    metric: str
    observed_delta: float
    interval_2p5_97p5: tuple[float, float]
    replicate_count: int
    discarded_count: int
    bootstrap_seed: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "observed_delta": self.observed_delta,
            "interval_2p5_97p5": list(self.interval_2p5_97p5),
            "replicate_count": self.replicate_count,
            "discarded_count": self.discarded_count,
            "bootstrap_seed": self.bootstrap_seed,
        }


REQUIRED_CONTRASTS = ("A-B", "B-C", "C-D", "C-A", "D-A")


def validate_prediction_arrays(
    jet_ids: Sequence[str],
    targets: NDArray[np.integer[Any]],
    scores: NDArray[np.floating[Any]],
) -> PredictionArrays:
    """Validate the exact one-row-per-fixed-test-jet numerical contract."""

    identities = tuple(jet_ids)
    target_array = np.asarray(targets, dtype=np.int8).reshape(-1)
    score_array = np.asarray(scores, dtype=np.float64).reshape(-1)
    if (
        len(identities) == 0
        or len(identities) != target_array.size
        or target_array.shape != score_array.shape
    ):
        raise IntegrityError("PREDICTION_ROW_COUNT", "prediction arrays have unequal row counts")
    if len(set(identities)) != len(identities) or any(not item for item in identities):
        raise IntegrityError("PREDICTION_IDENTITY", "jet identities must be non-empty and unique")
    if not np.isin(target_array, (0, 1)).all():
        raise IntegrityError("PREDICTION_TARGET", "targets must be binary")
    if not np.isfinite(score_array).all():
        raise IntegrityError("PREDICTION_SCORE", "scores must be finite")
    return PredictionArrays(identities, target_array, score_array)


def assert_aligned(left: PredictionArrays, right: PredictionArrays) -> None:
    """Require exact ordered identities and targets before paired evaluation."""

    if left.jet_ids != right.jet_ids:
        raise IntegrityError("PREDICTION_IDENTITY_MISMATCH", "ordered jet identities differ")
    if not np.array_equal(left.targets, right.targets):
        raise IntegrityError("PREDICTION_TARGET_MISMATCH", "aligned targets differ")


def background_rejection_at_signal_efficiency(
    labels: NDArray[np.integer[Any]],
    scores: NDArray[np.floating[Any]],
    target_signal_efficiency: float,
) -> dict[str, float | int | None]:
    """Interpolate background efficiency on the full tied-score ROC points."""

    if not 0.0 < target_signal_efficiency < 1.0:
        raise IntegrityError("METRIC_TARGET_EFFICIENCY", "target signal efficiency is invalid")
    label_array = np.asarray(labels).reshape(-1)
    score_array = np.asarray(scores, dtype=np.float64).reshape(-1)
    binary_roc_auc(label_array, score_array)
    positives = int(np.count_nonzero(label_array == 1))
    negatives = int(np.count_nonzero(label_array == 0))
    order = np.argsort(-score_array, kind="stable")
    ordered_labels = label_array[order]
    ordered_scores = score_array[order]
    true_positives = 0
    false_positives = 0
    tpr = [0.0]
    fpr = [0.0]
    start = 0
    while start < ordered_scores.size:
        stop = start + 1
        while stop < ordered_scores.size and ordered_scores[stop] == ordered_scores[start]:
            stop += 1
        group = ordered_labels[start:stop]
        true_positives += int(np.count_nonzero(group == 1))
        false_positives += int(np.count_nonzero(group == 0))
        tpr.append(true_positives / positives)
        fpr.append(false_positives / negatives)
        start = stop
    upper = next(index for index, value in enumerate(tpr) if value >= target_signal_efficiency)
    if tpr[upper] == target_signal_efficiency or upper == 0:
        epsilon_b = fpr[upper]
    else:
        lower = upper - 1
        fraction = (target_signal_efficiency - tpr[lower]) / (tpr[upper] - tpr[lower])
        epsilon_b = fpr[lower] + fraction * (fpr[upper] - fpr[lower])
    rejection = None if epsilon_b == 0.0 else 1.0 / epsilon_b
    return {
        "target_signal_efficiency": target_signal_efficiency,
        "background_efficiency": epsilon_b,
        "background_rejection": rejection,
        "background_count": negatives,
        "signal_count": positives,
    }


def binary_accuracy(
    labels: NDArray[np.integer[Any]],
    scores: NDArray[np.floating[Any]],
    *,
    validation_threshold: float,
) -> float:
    """Compute accuracy using only a caller-supplied validation threshold."""

    if not np.isfinite(validation_threshold):
        raise IntegrityError("METRIC_THRESHOLD", "validation threshold must be finite")
    label_array = np.asarray(labels).reshape(-1)
    score_array = np.asarray(scores, dtype=np.float64).reshape(-1)
    binary_roc_auc(label_array, score_array)
    return float(np.mean((score_array >= validation_threshold).astype(np.int8) == label_array))


def evaluate_binary_predictions(
    predictions: PredictionArrays, *, validation_threshold: float
) -> dict[str, Any]:
    """Compute the preregistered deterministic per-run metrics."""

    at_30 = background_rejection_at_signal_efficiency(
        predictions.targets, predictions.scores, 0.30
    )
    at_50 = background_rejection_at_signal_efficiency(
        predictions.targets, predictions.scores, 0.50
    )
    return {
        "roc_auc": binary_roc_auc(predictions.targets, predictions.scores),
        "accuracy": binary_accuracy(
            predictions.targets,
            predictions.scores,
            validation_threshold=validation_threshold,
        ),
        "validation_threshold": validation_threshold,
        "background_at_signal_efficiency_0_30": at_30,
        "background_at_signal_efficiency_0_50": at_50,
    }


def data_efficiency_summary(
    *, small_scale_auc_gap: float, large_scale_auc_gap: float, minimum_denominator: float
) -> dict[str, Any]:
    """Guard a gap ratio and retain raw differences when the denominator is unstable."""

    values = (small_scale_auc_gap, large_scale_auc_gap, minimum_denominator)
    if not all(np.isfinite(value) for value in values) or minimum_denominator <= 0:
        raise IntegrityError("METRIC_DATA_EFFICIENCY", "data-efficiency inputs are invalid")
    result: dict[str, Any] = {
        "small_scale_auc_gap": small_scale_auc_gap,
        "large_scale_auc_gap": large_scale_auc_gap,
    }
    if abs(large_scale_auc_gap) < minimum_denominator:
        result["auc_gap_fraction"] = None
        result["reason"] = "unstable_large_scale_denominator"
    else:
        result["auc_gap_fraction"] = small_scale_auc_gap / large_scale_auc_gap
        result["reason"] = None
    return result


def validate_prediction_payload(
    metadata_path: Path, payload_path: Path, *, expected_jet_ids: Sequence[str] | None = None
) -> PredictionArrays:
    """Validate NPZ bytes, metadata, identities, and row counts before consumption."""

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        payload_bytes = payload_path.read_bytes()
    except OSError as exc:
        raise ContractError(
            "PREDICTION_INPUT", "prediction metadata or payload is unreadable"
        ) from exc
    if not isinstance(metadata, dict):
        raise ContractError("PREDICTION_METADATA", "prediction metadata must be an object")
    from particleml.contracts import validate_contract_document

    validate_contract_document(metadata, "prediction")
    if hashlib.sha256(payload_bytes).hexdigest() != metadata["payload"]["sha256"]:
        raise IntegrityError("PREDICTION_PAYLOAD_HASH", "prediction payload hash mismatch")
    try:
        with np.load(payload_path, allow_pickle=False) as payload:
            required = {"jet_id", "target", "signal_score"}
            if not required.issubset(payload.files):
                raise ContractError("PREDICTION_COLUMNS", "prediction payload columns are missing")
            ids = tuple(str(item) for item in payload["jet_id"].tolist())
            predictions = validate_prediction_arrays(
                ids, payload["target"], payload["signal_score"]
            )
    except (OSError, ValueError) as exc:
        raise ContractError("PREDICTION_PAYLOAD", "prediction NPZ payload is invalid") from exc
    if len(predictions.jet_ids) != metadata["row_count"]:
        raise IntegrityError("PREDICTION_ROW_COUNT", "payload row count differs from metadata")
    if expected_jet_ids is not None and predictions.jet_ids != tuple(expected_jet_ids):
        raise IntegrityError("PREDICTION_IDENTITY_MISMATCH", "payload identity order is not fixed")
    return predictions


def _deterministic_npz(arrays: Mapping[str, NDArray[Any]]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w") as archive:
        for name in sorted(arrays):
            array_output = io.BytesIO()
            np.lib.format.write_array(  # type: ignore[no-untyped-call]
                array_output, np.asarray(arrays[name]), allow_pickle=False
            )
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, array_output.getvalue())
    return output.getvalue()


def publish_prediction_artifact(
    output: Path,
    metadata_template: Mapping[str, Any],
    predictions: PredictionArrays,
) -> Path:
    """Publish deterministic NPZ predictions and schema-valid metadata immutably."""

    metadata = deepcopy(dict(metadata_template))
    payload_bytes = _deterministic_npz(
        {
            "jet_id": np.asarray(predictions.jet_ids, dtype=np.str_),
            "target": predictions.targets.astype(np.int8, copy=False),
            "signal_score": predictions.scores.astype(np.float32),
        }
    )
    metadata["row_count"] = len(predictions.jet_ids)
    metadata["class_counts"] = {
        "qcd": int(np.count_nonzero(predictions.targets == 0)),
        "top": int(np.count_nonzero(predictions.targets == 1)),
    }
    row_order = ("\n".join(predictions.jet_ids) + "\n").encode()
    metadata["row_order_sha256"] = hashlib.sha256(row_order).hexdigest()
    metadata["payload"] = {
        "format": "npz",
        "path": "payload.npz",
        "sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "byte_size": len(payload_bytes),
        "compression": "zip",
    }
    if not isinstance(metadata.get("content_hash"), dict):
        raise ContractError("PREDICTION_METADATA", "content_hash template is required")
    metadata["content_hash"]["metadata_sha256"] = compute_document_hash(
        metadata, ("content_hash", "metadata_sha256")
    )
    from particleml.contracts import validate_contract_document

    validate_contract_document(metadata, "prediction")
    config_hash = hashlib.sha256(
        (json.dumps(metadata_template, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ).hexdigest()
    input_hashes = {
        "split_manifest": str(metadata["split_manifest_sha256"]),
        "view": str(metadata["view_sha256"]),
    }

    def writer(partial: Path) -> None:
        (partial / "payload.npz").write_bytes(payload_bytes)
        (partial / "prediction.json").write_text(
            json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    def validator(partial: Path) -> None:
        validate_prediction_payload(partial / "prediction.json", partial / "payload.npz")

    artifact = publish_artifact(
        output,
        writer,
        validator,
        input_hashes,
        config_hash,
        "particleml-prediction-v1",
    )
    return artifact.path


def _bootstrap_metric(
    metric: str,
    labels: NDArray[np.int8],
    scores: NDArray[np.float64],
    threshold: float | None,
) -> float:
    if metric == "roc_auc":
        return binary_roc_auc(labels, scores)
    if metric == "accuracy":
        if threshold is None:
            raise IntegrityError("METRIC_THRESHOLD", "paired accuracy requires a threshold")
        return binary_accuracy(labels, scores, validation_threshold=threshold)
    efficiencies = {
        "background_rejection_0_30": 0.30,
        "background_rejection_0_50": 0.50,
    }
    if metric in efficiencies:
        value = background_rejection_at_signal_efficiency(
            labels, scores, efficiencies[metric]
        )["background_rejection"]
        return float("nan") if value is None else float(value)
    raise IntegrityError("METRIC_NAME", f"unsupported paired metric {metric}")


def paired_stratified_bootstrap(
    left: PredictionArrays,
    right: PredictionArrays,
    *,
    metric: str,
    replicate_count: int,
    bootstrap_seed: int,
    left_validation_threshold: float | None = None,
    right_validation_threshold: float | None = None,
) -> PairedBootstrapResult:
    """Compute fixed-seed, class-stratified paired differences with common indices."""

    assert_aligned(left, right)
    if replicate_count < 1000 or bootstrap_seed < 0:
        raise IntegrityError(
            "METRIC_BOOTSTRAP_POLICY",
            "at least 1,000 replicates and a non-negative seed are required",
        )
    negative = np.flatnonzero(left.targets == 0)
    positive = np.flatnonzero(left.targets == 1)
    if negative.size == 0 or positive.size == 0:
        raise IntegrityError("METRIC_BOOTSTRAP_CLASSES", "both classes are required")
    observed_left = _bootstrap_metric(
        metric, left.targets, left.scores, left_validation_threshold
    )
    observed_right = _bootstrap_metric(
        metric, right.targets, right.scores, right_validation_threshold
    )
    observed_delta = observed_left - observed_right
    if not np.isfinite(observed_delta):
        raise IntegrityError("METRIC_BOOTSTRAP_OBSERVED", "observed paired delta is non-finite")
    generator = np.random.Generator(np.random.PCG64(bootstrap_seed))
    finite_deltas: list[float] = []
    discarded = 0
    for _ in range(replicate_count):
        sampled_negative = generator.choice(negative, size=negative.size, replace=True)
        sampled_positive = generator.choice(positive, size=positive.size, replace=True)
        indices = np.concatenate((sampled_negative, sampled_positive))
        labels = left.targets[indices]
        left_value = _bootstrap_metric(
            metric, labels, left.scores[indices], left_validation_threshold
        )
        right_value = _bootstrap_metric(
            metric, labels, right.scores[indices], right_validation_threshold
        )
        delta = left_value - right_value
        if np.isfinite(delta):
            finite_deltas.append(delta)
        else:
            discarded += 1
    if discarded / replicate_count > 0.01:
        raise IntegrityError(
            "METRIC_BOOTSTRAP_DISCARDS", "more than one percent of replicates are non-finite"
        )
    if not finite_deltas:
        raise IntegrityError("METRIC_BOOTSTRAP_EMPTY", "no finite bootstrap replicates remain")
    interval = np.percentile(np.asarray(finite_deltas), [2.5, 97.5])
    return PairedBootstrapResult(
        metric=metric,
        observed_delta=float(observed_delta),
        interval_2p5_97p5=(float(interval[0]), float(interval[1])),
        replicate_count=replicate_count,
        discarded_count=discarded,
        bootstrap_seed=bootstrap_seed,
    )


def validate_required_contrasts(comparisons: Mapping[str, Any]) -> None:
    """Require exactly the five preregistered E2 feature contrasts."""

    if set(comparisons) != set(REQUIRED_CONTRASTS):
        missing = sorted(set(REQUIRED_CONTRASTS) - set(comparisons))
        extra = sorted(set(comparisons) - set(REQUIRED_CONTRASTS))
        raise IntegrityError(
            "METRIC_CONTRAST_SET", f"contrast set differs; missing={missing}, extra={extra}"
        )


def summarize_model_seeds(values: Mapping[int, float]) -> dict[str, Any]:
    """Report every model seed, mean, and sample standard deviation separately."""

    if len(values) < 2 or any(seed < 0 for seed in values):
        raise IntegrityError("METRIC_SEED_SUMMARY", "at least two valid model seeds are required")
    ordered = sorted((int(seed), float(value)) for seed, value in values.items())
    array = np.asarray([value for _, value in ordered], dtype=np.float64)
    if not np.isfinite(array).all():
        raise IntegrityError("METRIC_SEED_SUMMARY", "seed metrics must be finite")
    return {
        "per_seed": [{"model_seed": seed, "value": value} for seed, value in ordered],
        "mean": float(np.mean(array)),
        "sample_standard_deviation": float(np.std(array, ddof=1)),
        "uncertainty_kind": "model_seed_variation",
    }


def binary_roc_auc(labels: NDArray[np.integer[Any]], scores: NDArray[np.floating[Any]]) -> float:
    """Compute binary ROC AUC with pairwise tie handling and no optional dependency."""

    label_array = np.asarray(labels).reshape(-1)
    score_array = np.asarray(scores, dtype=np.float64).reshape(-1)
    if label_array.shape != score_array.shape or not np.isfinite(score_array).all():
        raise IntegrityError("DATA_AUC_INPUT", "labels and finite scores must have equal shape")
    if not np.isin(label_array, (0, 1)).all():
        raise IntegrityError("DATA_AUC_INPUT", "labels must be binary")
    positive_count = int(np.count_nonzero(label_array == 1))
    negative_count = int(np.count_nonzero(label_array == 0))
    if positive_count == 0 or negative_count == 0:
        raise IntegrityError("DATA_AUC_INPUT", "both classes are required")
    order = np.argsort(score_array, kind="stable")
    sorted_scores = score_array[order]
    ranks = np.empty(score_array.size, dtype=np.float64)
    start = 0
    while start < sorted_scores.size:
        stop = start + 1
        while stop < sorted_scores.size and sorted_scores[stop] == sorted_scores[start]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * ((start + 1) + stop)
        start = stop
    positive_rank_sum = float(np.sum(ranks[label_array == 1]))
    baseline = positive_count * (positive_count + 1) / 2.0
    return (positive_rank_sum - baseline) / (positive_count * negative_count)


def shuffled_label_auc(
    labels: NDArray[np.integer[Any]], scores: NDArray[np.floating[Any]], *, seed: int
) -> float:
    """Return AUC after a deterministic permutation of the supplied labels.

    Raises:
        IntegrityError: If the seed or arrays violate the binary-AUC contract.
    """

    if seed < 0:
        raise IntegrityError("DATA_AUDIT_POLICY", "shuffle seed must be non-negative")
    shuffled = np.random.default_rng(seed).permutation(np.asarray(labels).reshape(-1))
    return binary_roc_auc(shuffled, np.asarray(scores).reshape(-1))
