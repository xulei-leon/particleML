"""Small deterministic numerical probes used by data audits."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from particleml.contracts import IntegrityError


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
