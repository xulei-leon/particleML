"""Deterministic nested subsets and native-PID A-D model views."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py  # type: ignore[import-untyped]
import numpy as np

from particleml.artifacts import verify_artifact_payload
from particleml.contracts import ContractError, FeatureConfig, IntegrityError
from particleml.dataset import canonical_semantic_hash
from particleml.manifest import rank_jet_id


@dataclass(frozen=True)
class SubsetJet:
    """Minimal identity used by the deterministic subset selector."""

    record_id: int
    jet_id: str
    label: int


def select_nested_subsets(
    jets: Iterable[SubsetJet],
    sizes: Iterable[int],
    subset_seed: int,
    active_qcd_record_ids: set[int],
) -> dict[int, dict[str, list[str]]]:
    """Select class-balanced nested prefixes with QCD record round-robin."""

    requested = tuple(sizes)
    if not requested or tuple(sorted(set(requested))) != requested or requested[0] <= 0:
        raise ContractError("SPLIT_SUBSET_GRID", "subset sizes must be positive and increasing")
    if subset_seed < 0 or not active_qcd_record_ids:
        raise ContractError("SPLIT_SUBSET_CONFIG", "seed and active QCD records are invalid")
    rows = list(jets)
    top = sorted(
        (row for row in rows if row.label == 1),
        key=lambda row: rank_jet_id(subset_seed, row.jet_id),
    )
    qcd_by_record: dict[int, list[SubsetJet]] = defaultdict(list)
    for row in rows:
        if row.label == 0 and row.record_id in active_qcd_record_ids:
            qcd_by_record[row.record_id].append(row)
        elif row.label not in (0, 1):
            raise ContractError("SPLIT_LABEL", f"unsupported class label: {row.label}")
    for record_id in qcd_by_record:
        qcd_by_record[record_id].sort(key=lambda row: rank_jet_id(subset_seed, row.jet_id))
    ordered_records = sorted(active_qcd_record_ids)
    qcd: list[SubsetJet] = []
    offsets = {record_id: 0 for record_id in ordered_records}
    while len(qcd) < requested[-1]:
        progressed = False
        for record_id in ordered_records:
            queue = qcd_by_record.get(record_id, [])
            offset = offsets[record_id]
            if offset < len(queue):
                qcd.append(queue[offset])
                offsets[record_id] += 1
                progressed = True
        if not progressed:
            break
    if len(top) < requested[-1] or len(qcd) < requested[-1]:
        raise IntegrityError(
            "SPLIT_INSUFFICIENT_CLASS_YIELD",
            f"requested {requested[-1]} per class, found top={len(top)} qcd={len(qcd)}",
        )
    return {
        size: {
            "qcd": [row.jet_id for row in qcd[:size]],
            "top": [row.jet_id for row in top[:size]],
        }
        for size in requested
    }


def view_argv(feature_config: FeatureConfig) -> list[str]:
    """Return the exact deferred OmniLearned argv fragment for one feature view."""

    return {
        FeatureConfig.A: [],
        FeatureConfig.B: ["--use-add", "--num-add", "1"],
        FeatureConfig.C: ["--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "1"],
        FeatureConfig.D: ["--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "5"],
    }[feature_config]


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("VIEW_CONTRACT", f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("VIEW_CONTRACT", f"JSON root must be an object: {path}")
    return value


def _state_hash_is_valid(state: Mapping[str, Any]) -> bool:
    stored = state.get("content_sha256")
    unsigned = dict(state)
    unsigned.pop("content_sha256", None)
    payload = (
        json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    return isinstance(stored, str) and stored == hashlib.sha256(payload).hexdigest()


def materialize_view(
    canonical: Path,
    preprocessing_state: Path,
    identities_path: Path,
    split_manifest_sha256: str,
    feature_config: FeatureConfig,
    output: Path,
    *,
    expected_subset_sha256: str | None = None,
    split_manifest_path: Path | None = None,
    require_completed_dependencies: bool = False,
) -> Path:
    """Materialize one immutable-order native-PID view for deferred model execution."""

    if require_completed_dependencies:
        try:
            if split_manifest_path is None:
                raise IntegrityError(
                    "ARTIFACT_INCOMPLETE", "formal view requires a split-manifest payload"
                )
            for dependency in (
                canonical,
                preprocessing_state,
                identities_path,
                split_manifest_path,
            ):
                verify_artifact_payload(dependency)
        except IntegrityError as exc:
            raise IntegrityError("VIEW_STALE_HASH", str(exc)) from exc
    state = _load_json_object(preprocessing_state)
    try:
        identity_bytes = identities_path.read_bytes()
    except OSError as exc:
        raise ContractError("VIEW_CONTRACT", f"cannot load {identities_path}: {exc}") from exc
    identity_sha256 = hashlib.sha256(identity_bytes).hexdigest()
    if expected_subset_sha256 is not None and identity_sha256 != expected_subset_sha256:
        raise IntegrityError("VIEW_STALE_HASH", "subset identity payload hash differs")
    if require_completed_dependencies and expected_subset_sha256 is None:
        raise ContractError("VIEW_CONTRACT", "formal view requires the expected subset SHA-256")
    identities = _load_json_object(identities_path)
    if not _state_hash_is_valid(state):
        raise IntegrityError("VIEW_STALE_HASH", "preprocessing state content hash is invalid")
    if len(split_manifest_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in split_manifest_sha256
    ):
        raise ContractError("VIEW_HASH_FORMAT", "split manifest SHA-256 is invalid")
    if split_manifest_path is not None:
        try:
            observed_split_hash = hashlib.sha256(split_manifest_path.read_bytes()).hexdigest()
        except OSError as exc:
            raise ContractError(
                "VIEW_CONTRACT", f"cannot load {split_manifest_path}: {exc}"
            ) from exc
        if observed_split_hash != split_manifest_sha256:
            raise IntegrityError("VIEW_STALE_HASH", "split-manifest payload hash differs")
    selected = [*identities.get("qcd", []), *identities.get("top", [])]
    if not selected or not all(isinstance(value, str) for value in selected):
        raise ContractError("VIEW_CONTRACT", "subset must contain ordered qcd and top identities")
    with h5py.File(canonical, "r") as source:
        canonical_hash = str(source.attrs.get("semantic_sha256", ""))
        if canonical_hash != canonical_semantic_hash(canonical):
            raise IntegrityError("VIEW_STALE_HASH", "canonical semantic hash is stale")
        if state.get("canonical_semantic_sha256") != canonical_hash:
            raise IntegrityError(
                "VIEW_STALE_HASH", "preprocessing state references another canonical dataset"
            )
        all_ids = source["identity/jet_id"].asstr()[:].tolist()
        index = {jet_id: position for position, jet_id in enumerate(all_ids)}
        if len(index) != len(all_ids) or any(jet_id not in index for jet_id in selected):
            raise IntegrityError(
                "VIEW_IDENTITY", "subset contains missing or duplicate canonical identities"
            )
        positions = np.asarray([index[jet_id] for jet_id in selected], dtype=np.int64)
        continuous = np.asarray(source["particles/continuous"][:], dtype=np.float32)[positions]
        pid = np.asarray(source["particles/pid_type"][:], dtype=np.float32)[positions]
        mask = np.asarray(source["particles/mask"][:], dtype=np.bool_)[positions]
        labels = np.asarray(source["labels/pid"][:], dtype=np.int8)[positions]
    location = np.asarray(state.get("continuous_location"), dtype=np.float32)
    scale = np.asarray(state.get("continuous_scale"), dtype=np.float32)
    if location.shape != (9,) or scale.shape != (9,) or np.any(scale <= 0):
        raise ContractError("VIEW_PREPROCESSING", "continuous location/scale is invalid")
    normalized = (continuous - location) / scale
    normalized[~mask] = 0.0
    base = normalized[:, :, :4]
    charge = normalized[:, :, 4:5]
    track = normalized[:, :, 5:9]
    field_names: list[str]
    if feature_config is FeatureConfig.A:
        data, field_names = base, ["delta_eta", "delta_phi", "log_pt", "log_energy"]
    elif feature_config is FeatureConfig.B:
        data = np.concatenate((base, charge), axis=2)
        field_names = ["delta_eta", "delta_phi", "log_pt", "log_energy", "charge"]
    elif feature_config is FeatureConfig.C:
        data = np.concatenate((base, pid[:, :, None], charge), axis=2)
        field_names = ["delta_eta", "delta_phi", "log_pt", "log_energy", "pid_type", "charge"]
    else:
        data = np.concatenate((base, pid[:, :, None], charge, track), axis=2)
        field_names = [
            "delta_eta",
            "delta_phi",
            "log_pt",
            "log_energy",
            "pid_type",
            "charge",
            "dxy_raw",
            "dxy_error_raw",
            "dz_raw",
            "dz_error_raw",
        ]
    # This final pass also covers the native PID column added after continuous normalization.
    data[~mask] = 0.0
    output.parent.mkdir(parents=True, exist_ok=True)
    string_dtype = h5py.string_dtype("utf-8")
    with h5py.File(output, "w") as target:
        target.create_dataset(
            "data", data=data.astype(np.float32), compression="gzip", compression_opts=4
        )
        target.create_dataset("mask", data=mask, compression="gzip", compression_opts=4)
        target.create_dataset("label", data=labels, compression="gzip", compression_opts=4)
        target.create_dataset(
            "jet_id",
            data=np.asarray(selected, dtype=string_dtype),
            compression="gzip",
            compression_opts=4,
        )
        target.attrs["schema_version"] = "1.0.0"
        target.attrs["feature_config"] = feature_config.value
        target.attrs["field_names_json"] = json.dumps(field_names, separators=(",", ":"))
        target.attrs["omnilearned_argv_json"] = json.dumps(
            view_argv(feature_config), separators=(",", ":")
        )
        target.attrs["canonical_semantic_sha256"] = canonical_hash
        target.attrs["split_manifest_sha256"] = split_manifest_sha256
        target.attrs["preprocessing_sha256"] = str(state["content_sha256"])
        target.attrs["subset_sha256"] = identity_sha256
    return output
