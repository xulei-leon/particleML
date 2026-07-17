"""Structured data-audit policy evaluation and retained results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import h5py  # type: ignore[import-untyped]
import numpy as np
from numpy.typing import NDArray

from particleml.contracts import ContractError, IntegrityError
from particleml.metrics import shuffled_label_auc

FORBIDDEN_MODEL_FIELDS = frozenset(
    {
        "record_id",
        "canonical_pfn",
        "pfn_sha256",
        "run",
        "lumi",
        "event",
        "jet_index",
        "jet_pt",
        "jet_eta",
        "jet_phi",
        "pv_z",
        "n_vertices",
        "generator_bin",
        "process",
        "truth",
        "truth_label",
        "audit_weight",
    }
)
AUDIT_POLICY_KEYS = {
    "schema_version",
    "missing_track_fraction_max",
    "shuffled_label_seed",
    "shuffled_label_auc_max",
    "expected_qcd_mixture_counts",
}


def audit_model_fields(fields: list[str], *, fail_closed: bool = False) -> list[str]:
    """Enumerate forbidden identity/audit/truth fields and optionally reject them."""

    forbidden = sorted(set(fields) & FORBIDDEN_MODEL_FIELDS)
    if forbidden and fail_closed:
        raise IntegrityError(
            "DATA_FORBIDDEN_INPUT", f"forbidden model fields: {', '.join(forbidden)}"
        )
    return forbidden


def missing_track_fraction(states: NDArray[np.uint8], mask: NDArray[np.bool_]) -> float:
    """Measure charged missing-track rows among all charged track-eligible rows."""

    state_array = np.asarray(states, dtype=np.uint8)
    mask_array = np.asarray(mask, dtype=np.bool_)
    if state_array.shape != mask_array.shape:
        raise IntegrityError("DATA_AUDIT_INPUT", "track state and mask shape differ")
    eligible = mask_array & np.isin(state_array, (1, 3))
    return (
        float(np.count_nonzero(mask_array & (state_array == 3)) / np.count_nonzero(eligible))
        if np.any(eligible)
        else 0.0
    )


def _load_audit_policy(path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("DATA_AUDIT_POLICY", f"invalid audit policy: {exc}") from exc
    if (
        not isinstance(policy, dict)
        or set(policy) != AUDIT_POLICY_KEYS
        or policy.get("schema_version") != "1.0.0"
    ):
        raise ContractError(
            "DATA_AUDIT_POLICY", "audit policy has missing, unknown, or unsupported fields"
        )
    for field in ("missing_track_fraction_max", "shuffled_label_auc_max"):
        value = policy.get(field)
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0.0 <= float(value) <= 1.0
        ):
            raise ContractError("DATA_AUDIT_POLICY", f"{field} must be in [0, 1]")
    if not isinstance(policy.get("shuffled_label_seed"), int) or policy["shuffled_label_seed"] < 0:
        raise ContractError("DATA_AUDIT_POLICY", "shuffled_label_seed must be non-negative")
    expected_counts = policy.get("expected_qcd_mixture_counts")
    if (
        not isinstance(expected_counts, dict)
        or not expected_counts
        or any(
            not isinstance(record_id, str)
            or not record_id.isdigit()
            or not isinstance(count, int)
            or isinstance(count, bool)
            or count <= 0
            for record_id, count in expected_counts.items()
        )
    ):
        raise ContractError(
            "DATA_AUDIT_POLICY", "expected_qcd_mixture_counts must map record IDs to counts"
        )
    return policy


def build_data_audit(
    canonical: Path, model_fields: list[str], policy_path: Path, output: Path
) -> dict[str, Any]:
    """Evaluate versioned data gates and serialize observed values and decisions."""

    policy = _load_audit_policy(policy_path)
    forbidden = audit_model_fields(model_fields)
    with h5py.File(canonical, "r") as handle:
        states = np.asarray(handle["particles/track_state"][:], dtype=np.uint8)
        mask = np.asarray(handle["particles/mask"][:], dtype=np.bool_)
        labels = np.asarray(handle["labels/pid"][:], dtype=np.int8)
        scores = np.asarray(handle["audit/jet_pt"][:], dtype=np.float64)
        n_vertices = np.asarray(handle["audit/n_vertices"][:], dtype=np.int64)
        splits = handle["split/name"].asstr()[:]
        record_ids = np.asarray(handle["identity/record_id"][:], dtype=np.int64)
        jet_ids = handle["identity/jet_id"].asstr()[:]
        canonical_hash = str(handle.attrs.get("semantic_sha256", ""))
    training = splits == "train"
    if (
        np.count_nonzero(training & (labels == 0)) == 0
        or np.count_nonzero(training & (labels == 1)) == 0
    ):
        raise IntegrityError("DATA_AUDIT_CLASS_YIELD", "training split must contain both classes")
    missing = missing_track_fraction(states[training], mask[training])
    shuffled = shuffled_label_auc(
        labels[training], scores[training], seed=policy["shuffled_label_seed"]
    )
    missing_passed = missing <= float(policy["missing_track_fraction_max"])
    shuffled_passed = shuffled <= float(policy["shuffled_label_auc_max"])
    forbidden_passed = not forbidden
    qcd_records = record_ids[training & (labels == 0)]
    unique_records, counts = np.unique(qcd_records, return_counts=True)
    observed_counts = {
        str(record): int(count) for record, count in zip(unique_records, counts, strict=True)
    }
    mixture_passed = observed_counts == policy["expected_qcd_mixture_counts"]
    report: dict[str, Any] = {
        "schema_version": "1.0.0",
        "canonical_semantic_sha256": canonical_hash,
        "status": (
            "passed"
            if missing_passed and shuffled_passed and forbidden_passed and mixture_passed
            else "failed"
        ),
        "training_jet_ids": jet_ids[training].tolist(),
        "checks": {
            "forbidden_fields": {"observed": forbidden, "passed": forbidden_passed},
            "missing_track": {
                "observed": missing,
                "threshold": float(policy["missing_track_fraction_max"]),
                "passed": missing_passed,
            },
            "shuffled_label": {
                "observed_auc": shuffled,
                "threshold": float(policy["shuffled_label_auc_max"]),
                "seed": policy["shuffled_label_seed"],
                "score_field": "audit/jet_pt",
                "passed": shuffled_passed,
            },
            "qcd_mixture_counts": {
                "observed": observed_counts,
                "expected": policy["expected_qcd_mixture_counts"],
                "passed": mixture_passed,
            },
            "pileup_n_vertices": {
                "observed": {
                    "minimum": int(np.min(n_vertices[training])),
                    "mean": float(np.mean(n_vertices[training])),
                    "maximum": int(np.max(n_vertices[training])),
                },
                "policy": "diagnostic_only",
                "passed": True,
            },
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report
