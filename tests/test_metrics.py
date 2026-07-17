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
    validate_prediction_arrays,
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

