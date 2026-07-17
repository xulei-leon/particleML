from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from particleml.audit import (
    audit_model_fields,
    build_data_audit,
    missing_track_fraction,
)
from particleml.contracts import IntegrityError
from particleml.metrics import binary_roc_auc, shuffled_label_auc
from tests.test_views import _pipeline


def test_forbidden_model_fields_are_rejected() -> None:
    audit_model_fields(["delta_eta", "delta_phi", "record_id"])

    with pytest.raises(IntegrityError, match="DATA_FORBIDDEN_INPUT"):
        audit_model_fields(["delta_eta", "record_id"], fail_closed=True)


def test_missing_track_fraction_contract() -> None:
    states = np.asarray([[1, 3, 2, 0]], dtype=np.uint8)
    mask = np.asarray([[True, True, True, False]])

    assert missing_track_fraction(states, mask) == pytest.approx(0.5)


def test_auc_and_shuffle_are_deterministic() -> None:
    labels = np.asarray([0, 0, 1, 1], dtype=np.int8)
    scores = np.asarray([0.1, 0.2, 0.8, 0.9])

    assert binary_roc_auc(labels, scores) == 1.0
    assert shuffled_label_auc(labels, scores, seed=7) == shuffled_label_auc(labels, scores, seed=7)


def test_audit_report_retains_thresholds_and_decisions(tmp_path: Path) -> None:
    canonical, _state, _identities = _pipeline(tmp_path)
    policy = tmp_path / "audit-policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "missing_track_fraction_max": 1.0,
                "shuffled_label_seed": 7,
                "shuffled_label_auc_max": 1.0,
                "expected_qcd_mixture_counts": {"18355": 1},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "audit.json"

    report = build_data_audit(canonical, ["delta_eta", "delta_phi"], policy, output)

    assert report["status"] == "passed"
    assert report["checks"]["missing_track"]["threshold"] == 1.0
    assert report["checks"]["shuffled_label"]["seed"] == 7
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


def test_audit_report_retains_failed_decisions(tmp_path: Path) -> None:
    canonical, _state, _identities = _pipeline(tmp_path)
    policy = tmp_path / "audit-policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "missing_track_fraction_max": 0.0,
                "shuffled_label_seed": 7,
                "shuffled_label_auc_max": 1.0,
                "expected_qcd_mixture_counts": {"18355": 2},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_data_audit(
        canonical, ["delta_eta", "delta_phi"], policy, tmp_path / "failed.json"
    )

    assert report["status"] == "failed"
    assert report["checks"]["missing_track"]["passed"] is False
    assert report["checks"]["qcd_mixture_counts"]["passed"] is False
    assert report["checks"]["shuffled_label"]["score_field"] == "audit/jet_pt"


def test_auc_uses_average_ranks_for_ties() -> None:
    labels = np.asarray([0, 1, 0, 1], dtype=np.int8)
    scores = np.asarray([0.5, 0.5, 0.1, 0.9])

    assert binary_roc_auc(labels, scores) == pytest.approx(0.875)
