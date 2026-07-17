from __future__ import annotations

import numpy as np
import pytest

from particleml.contracts import IntegrityError
from particleml.metrics import (
    assert_aligned,
    background_rejection_at_signal_efficiency,
    binary_accuracy,
    binary_roc_auc,
    data_efficiency_summary,
    evaluate_binary_predictions,
    paired_stratified_bootstrap,
    summarize_model_seeds,
    validate_prediction_arrays,
    validate_required_contrasts,
)


def test_golden_auc_rejection_and_accuracy() -> None:
    labels = np.asarray([0, 0, 1, 1], dtype=np.int8)
    scores = np.asarray([0.1, 0.4, 0.35, 0.8], dtype=np.float64)
    predictions = validate_prediction_arrays(["a", "b", "c", "d"], labels, scores)
    assert binary_roc_auc(labels, scores) == pytest.approx(0.75)
    assert binary_accuracy(labels, scores, validation_threshold=0.5) == pytest.approx(0.75)
    rejection = background_rejection_at_signal_efficiency(labels, scores, 0.5)
    assert rejection["background_efficiency"] == 0.0
    assert rejection["background_rejection"] is None
    metrics = evaluate_binary_predictions(predictions, validation_threshold=0.5)
    assert metrics["roc_auc"] == pytest.approx(0.75)


def test_prediction_alignment_rejects_reordered_duplicate_and_target_mismatch() -> None:
    left = validate_prediction_arrays(
        ["a", "b"], np.asarray([0, 1]), np.asarray([0.2, 0.8])
    )
    reordered = validate_prediction_arrays(
        ["b", "a"], np.asarray([1, 0]), np.asarray([0.8, 0.2])
    )
    with pytest.raises(IntegrityError, match="PREDICTION_IDENTITY_MISMATCH"):
        assert_aligned(left, reordered)
    changed_target = validate_prediction_arrays(
        ["a", "b"], np.asarray([1, 0]), np.asarray([0.2, 0.8])
    )
    with pytest.raises(IntegrityError, match="PREDICTION_TARGET_MISMATCH"):
        assert_aligned(left, changed_target)
    with pytest.raises(IntegrityError, match="PREDICTION_IDENTITY"):
        validate_prediction_arrays(["a", "a"], np.asarray([0, 1]), np.asarray([0.2, 0.8]))


def test_nonfinite_single_class_and_unstable_ratio_fail_closed() -> None:
    with pytest.raises(IntegrityError):
        validate_prediction_arrays(["a"], np.asarray([1]), np.asarray([np.nan]))
    with pytest.raises(IntegrityError):
        binary_roc_auc(np.asarray([1, 1]), np.asarray([0.1, 0.2]))
    summary = data_efficiency_summary(
        small_scale_auc_gap=0.03,
        large_scale_auc_gap=0.001,
        minimum_denominator=0.01,
    )
    assert summary["auc_gap_fraction"] is None
    assert summary["reason"] == "unstable_large_scale_denominator"


def test_paired_bootstrap_is_deterministic_stratified_and_uses_common_indices() -> None:
    labels = np.asarray([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int8)
    left = validate_prediction_arrays(
        [f"jet-{index}" for index in range(8)],
        labels,
        np.asarray([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]),
    )
    right = validate_prediction_arrays(left.jet_ids, labels, left.scores.copy())
    first = paired_stratified_bootstrap(
        left, right, metric="roc_auc", replicate_count=1000, bootstrap_seed=17
    )
    second = paired_stratified_bootstrap(
        left, right, metric="roc_auc", replicate_count=1000, bootstrap_seed=17
    )
    assert first == second
    assert first.observed_delta == 0.0
    assert first.interval_2p5_97p5 == (0.0, 0.0)
    assert first.discarded_count == 0


def test_paired_bootstrap_rejects_identity_mismatch_and_small_policy() -> None:
    left = validate_prediction_arrays(
        ["a", "b", "c", "d"], np.asarray([0, 0, 1, 1]), np.asarray([0.1, 0.2, 0.8, 0.9])
    )
    reordered = validate_prediction_arrays(
        ["b", "a", "c", "d"], np.asarray([0, 0, 1, 1]), np.asarray([0.2, 0.1, 0.8, 0.9])
    )
    with pytest.raises(IntegrityError, match="PREDICTION_IDENTITY_MISMATCH"):
        paired_stratified_bootstrap(
            left, reordered, metric="roc_auc", replicate_count=1000, bootstrap_seed=1
        )
    with pytest.raises(IntegrityError, match="METRIC_BOOTSTRAP_POLICY"):
        paired_stratified_bootstrap(
            left, left, metric="roc_auc", replicate_count=999, bootstrap_seed=1
        )


def test_required_contrasts_and_seed_variation_remain_separate() -> None:
    validate_required_contrasts({name: {} for name in ("A-B", "B-C", "C-D", "C-A", "D-A")})
    with pytest.raises(IntegrityError, match="METRIC_CONTRAST_SET"):
        validate_required_contrasts({"A-B": {}})
    summary = summarize_model_seeds({3: 0.7, 1: 0.5, 2: 0.6})
    assert [item["model_seed"] for item in summary["per_seed"]] == [1, 2, 3]
    assert summary["mean"] == pytest.approx(0.6)
    assert summary["sample_standard_deviation"] == pytest.approx(0.1)
    assert summary["uncertainty_kind"] == "model_seed_variation"
