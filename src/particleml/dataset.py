"""Canonical compact-ROOT conversion and training-fitted preprocessing state."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import awkward as ak  # type: ignore[import-untyped]
import h5py  # type: ignore[import-untyped]
import numpy as np
import uproot  # type: ignore[import-untyped]
from numpy.typing import NDArray

from particleml.artifacts import publish_artifact
from particleml.contracts import Artifact, ContractError, InputError, IntegrityError
from particleml.manifest import (
    hash_canonical_pfn,
    hash_source_manifest,
    load_source_manifest,
    stable_jet_id,
)

MAX_PARTICLES = 150
CONTINUOUS_FIELDS = (
    "delta_eta",
    "delta_phi",
    "log_pt",
    "log_energy",
    "charge",
    "dxy_raw",
    "dxy_error_raw",
    "dz_raw",
    "dz_error_raw",
)
POLICY_KEYS = {
    "schema_version",
    "feature_version",
    "min_particle_pt_gev",
    "min_particle_energy_gev",
    "pid_vocabulary",
    "pt_eta_control",
    "pileup_policy",
    "d_field_unit",
    "d_field_transform",
    "missing_track_policy",
}
SEMANTIC_ATTRIBUTES = (
    "feature_version",
    "schema_version",
    "semantic_hash_algorithm",
    "source_manifest_sha256",
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _load_policy(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("INPUT_NOT_FOUND", f"data policy does not exist: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("DATA_POLICY", f"invalid data policy: {exc}") from exc
    if not isinstance(value, dict) or set(value) != POLICY_KEYS:
        raise ContractError("DATA_POLICY", "data policy has missing or unknown fields")
    if value.get("schema_version") != "1.0.0" or not isinstance(value.get("feature_version"), str):
        raise ContractError("DATA_POLICY", "unsupported schema or feature version")
    for field in ("min_particle_pt_gev", "min_particle_energy_gev"):
        threshold = value.get(field)
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or threshold <= 0:
            raise ContractError("DATA_POLICY", f"{field} must be explicitly positive")
    if (
        value.get("d_field_unit") != "cm"
        or value.get("missing_track_policy") != "zero_with_track_state"
    ):
        raise ContractError("DATA_POLICY", "unsupported track-field policy")
    vocabulary = value.get("pid_vocabulary")
    expected = {
        "unknown": 0,
        "charged_hadron": 1,
        "neutral_hadron": 2,
        "photon": 3,
        "electron": 4,
        "muon": 5,
    }
    if vocabulary != expected:
        raise ContractError("DATA_POLICY", "pid_vocabulary must equal the frozen full-D vocabulary")
    return value


def wrap_delta_phi(value: float) -> float:
    """Wrap an angular difference to the half-open interval [-pi, pi)."""

    return (value + math.pi) % (2.0 * math.pi) - math.pi


def pid_type(pdg_id: int) -> int:
    """Map the absolute PDG identifier to the frozen native-PID vocabulary."""

    absolute = abs(int(pdg_id))
    if absolute in {11}:
        return 4
    if absolute in {13}:
        return 5
    if absolute == 22:
        return 3
    if absolute in {130, 2112, 310}:
        return 2
    if absolute in {211, 321, 2212}:
        return 1
    return 0


def track_state(charge: float, has_track_details: bool) -> int:
    """Return usable, neutral, or charged-missing state for a real constituent."""

    if has_track_details:
        return 1
    return 2 if charge == 0.0 else 3


def _string_bytes(array: NDArray[Any]) -> bytes:
    payload = bytearray()
    for value in array.reshape(-1):
        item = value if isinstance(value, bytes) else str(value).encode("utf-8")
        if not isinstance(item, bytes):
            item = bytes(item)
        payload.extend(len(item).to_bytes(8, "big"))
        payload.extend(item)
    return bytes(payload)


def canonical_semantic_hash(path: Path) -> str:
    """Hash sorted dataset metadata/content and the semantic root-attribute allowlist."""

    digest = hashlib.sha256()
    with h5py.File(path, "r") as handle:
        datasets: list[tuple[str, h5py.Dataset]] = []

        def collect(name: str, value: h5py.Group | h5py.Dataset) -> None:
            if isinstance(value, h5py.Dataset):
                datasets.append((name, value))

        handle.visititems(collect)
        for name, dataset in sorted(datasets):
            array = np.asarray(dataset[...])
            metadata = {"path": name, "dtype": dataset.dtype.str, "shape": list(dataset.shape)}
            digest.update(_canonical_json(metadata))
            digest.update(
                _string_bytes(array)
                if array.dtype.kind in "OUS"
                else np.ascontiguousarray(array).tobytes(order="C")
            )
        attributes = {
            name: str(handle.attrs[name]) for name in SEMANTIC_ATTRIBUTES if name in handle.attrs
        }
        digest.update(_canonical_json(attributes))
    return digest.hexdigest()


def _write_dataset(group: h5py.Group, name: str, data: NDArray[Any]) -> h5py.Dataset:
    chunks = (min(max(1, data.shape[0]), 64), *data.shape[1:])
    return group.create_dataset(
        name, data=data, compression="gzip", compression_opts=4, chunks=chunks
    )


def convert_compact_root(
    roots: Iterable[Path], source_manifest: Path, policy_path: Path, output: Path
) -> Path:
    """Convert deterministic compact ROOT trees into the canonical full-D HDF5 layout."""

    policy = _load_policy(policy_path)
    manifest = load_source_manifest(source_manifest)
    allowed_sources = {(entry.record_id, entry.canonical_pfn) for entry in manifest.entries}
    root_paths = list(roots)
    if not root_paths:
        raise InputError("INPUT_NOT_FOUND", "at least one compact ROOT input is required")

    rows: list[dict[str, Any]] = []
    for root_path in root_paths:
        try:
            with uproot.open(root_path) as root_file:
                arrays = root_file["jets"].arrays(library="ak")
        except (OSError, KeyError, uproot.exceptions.KeyInFileError) as exc:
            raise InputError(
                "INPUT_ROOT", f"cannot read compact ROOT input {root_path}: {exc}"
            ) from exc
        for index in range(len(arrays)):
            rows.append({name: ak.to_list(arrays[name][index]) for name in arrays.fields})
    if not rows:
        raise IntegrityError("DATA_EMPTY", "compact ROOT inputs contain no jets")

    count = len(rows)
    continuous = np.zeros((count, MAX_PARTICLES, len(CONTINUOUS_FIELDS)), dtype=np.float32)
    pids = np.zeros((count, MAX_PARTICLES), dtype=np.uint8)
    masks = np.zeros((count, MAX_PARTICLES), dtype=np.bool_)
    tracks = np.zeros((count, MAX_PARTICLES), dtype=np.uint8)
    identities: list[str] = []
    pfns: list[str] = []
    pfn_hashes: list[str] = []
    split_names: list[str] = []
    labels = np.zeros(count, dtype=np.int8)
    record_ids = np.zeros(count, dtype=np.int64)
    runs = np.zeros(count, dtype=np.int64)
    lumis = np.zeros(count, dtype=np.int64)
    events = np.zeros(count, dtype=np.int64)
    jet_indices = np.zeros(count, dtype=np.int32)
    jet_pt = np.zeros(count, dtype=np.float32)
    jet_eta = np.zeros(count, dtype=np.float32)
    jet_phi = np.zeros(count, dtype=np.float32)
    pv_z = np.zeros(count, dtype=np.float32)
    n_vertices = np.zeros(count, dtype=np.int32)
    seen_ids: set[str] = set()
    observed_sources: set[tuple[int, str]] = set()
    particle_names = (
        "particle_pt",
        "particle_eta",
        "particle_phi",
        "particle_energy",
        "particle_charge",
        "particle_pdg_id",
        "particle_dxy",
        "particle_dxy_error",
        "particle_dz",
        "particle_dz_error",
        "particle_has_track_details",
    )
    for row_index, row in enumerate(rows):
        try:
            record_id = int(row["record_id"])
            pfn = str(row["canonical_pfn"])
            source = (record_id, pfn)
            if source not in allowed_sources:
                raise IntegrityError(
                    "DATA_PROVENANCE", f"source pair is absent from manifest: {source}"
                )
            lengths = {len(row[name]) for name in particle_names}
            if len(lengths) != 1:
                raise IntegrityError(
                    "DATA_PARTICLE_LENGTH", "jagged particle branches have unequal lengths"
                )
            particle_rows = [
                tuple(row[name][i] for name in particle_names) for i in range(next(iter(lengths)))
            ]
            for particle in particle_rows:
                numeric = particle[:10]
                if not all(np.isfinite(float(value)) for value in numeric):
                    raise IntegrityError("DATA_NONFINITE", "particle fields must be finite")
            particle_rows = [
                particle
                for particle in particle_rows
                if float(particle[0]) >= float(policy["min_particle_pt_gev"])
                and float(particle[3]) >= float(policy["min_particle_energy_gev"])
            ]
            particle_rows = sorted(
                enumerate(particle_rows), key=lambda item: (-float(item[1][0]), item[0])
            )[:MAX_PARTICLES]
            jet_id = stable_jet_id(
                record_id,
                pfn,
                int(row["run"]),
                int(row["lumi"]),
                int(row["event"]),
                int(row["jet_index"]),
            )
        except KeyError as exc:
            raise ContractError(
                "DATA_ROOT_SCHEMA", f"missing compact ROOT branch: {exc.args[0]}"
            ) from exc
        if jet_id in seen_ids:
            raise IntegrityError("DATA_DUPLICATE_IDENTITY", f"duplicate jet identity: {jet_id}")
        seen_ids.add(jet_id)
        observed_sources.add(source)
        for output_index, (_, particle) in enumerate(particle_rows):
            pt, eta, phi, energy, charge, pdg, dxy, dxy_error, dz, dz_error, has_track = particle
            state = track_state(float(charge), bool(has_track))
            raw_track = (
                (float(dxy), float(dxy_error), float(dz), float(dz_error))
                if state == 1
                else (0.0, 0.0, 0.0, 0.0)
            )
            continuous[row_index, output_index] = (
                float(eta) - float(row["jet_eta"]),
                wrap_delta_phi(float(phi) - float(row["jet_phi"])),
                math.log(float(pt)),
                math.log(float(energy)),
                float(charge),
                *raw_track,
            )
            pids[row_index, output_index] = pid_type(int(pdg))
            masks[row_index, output_index] = True
            tracks[row_index, output_index] = state
        identities.append(jet_id)
        pfns.append(pfn)
        pfn_hashes.append(hash_canonical_pfn(pfn))
        split_names.append(str(row["split"]))
        if split_names[-1] not in {"train", "validation", "test"}:
            raise ContractError("DATA_SPLIT", f"invalid split name: {split_names[-1]}")
        label = int(row["target"])
        if label not in (0, 1):
            raise ContractError("DATA_LABEL", f"invalid binary target: {label}")
        labels[row_index] = label
        record_ids[row_index] = record_id
        runs[row_index], lumis[row_index], events[row_index] = (
            int(row["run"]),
            int(row["lumi"]),
            int(row["event"]),
        )
        jet_indices[row_index] = int(row["jet_index"])
        jet_pt[row_index], jet_eta[row_index], jet_phi[row_index] = (
            float(row["jet_pt"]),
            float(row["jet_eta"]),
            float(row["jet_phi"]),
        )
        pv_z[row_index], n_vertices[row_index] = float(row["pv_z"]), int(row["n_vertices"])

    if observed_sources != allowed_sources:
        missing = sorted(allowed_sources - observed_sources)
        raise IntegrityError(
            "DATA_PROVENANCE", f"manifest sources have no converted jets: {missing}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    string_dtype = h5py.string_dtype("utf-8")
    with h5py.File(output, "w") as handle:
        handle.attrs["schema_version"] = "1.0.0"
        handle.attrs["feature_version"] = policy["feature_version"]
        handle.attrs["source_manifest_sha256"] = hash_source_manifest(manifest)
        handle.attrs["semantic_hash_algorithm"] = "particleml-hdf5-semantic-v1"
        particles = handle.create_group("particles")
        _write_dataset(particles, "continuous", continuous)
        _write_dataset(particles, "pid_type", pids)
        _write_dataset(particles, "mask", masks)
        _write_dataset(particles, "track_state", tracks)
        labels_group = handle.create_group("labels")
        _write_dataset(labels_group, "pid", labels)
        identity = handle.create_group("identity")
        for name, values in (
            ("jet_id", np.asarray(identities, dtype=string_dtype)),
            ("canonical_pfn", np.asarray(pfns, dtype=string_dtype)),
            ("pfn_sha256", np.asarray(pfn_hashes, dtype=string_dtype)),
            ("record_id", record_ids),
            ("run", runs),
            ("lumi", lumis),
            ("event", events),
            ("jet_index", jet_indices),
        ):
            _write_dataset(identity, name, values)
        split_group = handle.create_group("split")
        _write_dataset(split_group, "name", np.asarray(split_names, dtype=string_dtype))
        audit = handle.create_group("audit")
        for name, values in (
            ("jet_pt", jet_pt),
            ("jet_eta", jet_eta),
            ("jet_phi", jet_phi),
            ("pv_z", pv_z),
            ("n_vertices", n_vertices),
        ):
            _write_dataset(audit, name, values)
    digest = canonical_semantic_hash(output)
    with h5py.File(output, "r+") as handle:
        handle.attrs["semantic_sha256"] = digest
    return output


def fit_preprocessing_state(canonical: Path, policy_path: Path, output: Path) -> dict[str, Any]:
    """Fit deterministic continuous location/scale using only the training partition."""

    policy = _load_policy(policy_path)
    with h5py.File(canonical, "r") as handle:
        split = handle["split/name"].asstr()[:]
        training = split == "train"
        if not np.any(training):
            raise IntegrityError("DATA_NO_TRAIN", "canonical data has no training jets")
        data = np.asarray(handle["particles/continuous"][training], dtype=np.float64)
        mask = np.asarray(handle["particles/mask"][training], dtype=np.bool_)
        values = data[mask]
        if values.size == 0:
            raise IntegrityError(
                "DATA_NO_TRAIN_PARTICLES", "training jets have no selected particles"
            )
        location = np.mean(values, axis=0)
        scale = np.std(values, axis=0)
        scale[scale == 0.0] = 1.0
        training_ids = handle["identity/jet_id"].asstr()[:][training].tolist()
        canonical_hash = str(
            handle.attrs.get("semantic_sha256", canonical_semantic_hash(canonical))
        )
        source_hash = str(handle.attrs["source_manifest_sha256"])
    state: dict[str, Any] = {
        "schema_version": "1.0.0",
        "feature_version": policy["feature_version"],
        "canonical_semantic_sha256": canonical_hash,
        "source_manifest_sha256": source_hash,
        "policy_sha256": hashlib.sha256(_canonical_json(policy)).hexdigest(),
        "training_jet_ids": training_ids,
        "training_jet_ids_sha256": hashlib.sha256(_canonical_json(training_ids)).hexdigest(),
        "continuous_fields": list(CONTINUOUS_FIELDS),
        "continuous_location": location.tolist(),
        "continuous_scale": scale.tolist(),
        "min_particle_pt_gev": policy["min_particle_pt_gev"],
        "min_particle_energy_gev": policy["min_particle_energy_gev"],
        "pid_vocabulary": policy["pid_vocabulary"],
        "pt_eta_control": policy["pt_eta_control"],
        "pileup_policy": policy["pileup_policy"],
        "d_field_unit": policy["d_field_unit"],
        "d_field_transform": policy["d_field_transform"],
        "missing_track_policy": policy["missing_track_policy"],
    }
    state["content_sha256"] = hashlib.sha256(_canonical_json(state)).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_canonical_json(state))
    return state


def publish_canonical_artifact(
    roots: Iterable[Path],
    source_manifest: Path,
    policy_path: Path,
    final: Path,
    *,
    payload_name: str = "canonical.h5",
) -> Artifact:
    """Publish one validated canonical payload through the formal directory lifecycle."""

    if Path(payload_name).name != payload_name or not payload_name:
        raise ContractError("DATA_OUTPUT_NAME", "canonical payload_name must be one filename")
    root_paths = list(roots)
    input_hashes = {
        "source_manifest": hashlib.sha256(source_manifest.read_bytes()).hexdigest(),
        **{
            f"compact_root_{index:03d}": hashlib.sha256(path.read_bytes()).hexdigest()
            for index, path in enumerate(root_paths)
        },
    }
    config_sha256 = hashlib.sha256(policy_path.read_bytes()).hexdigest()

    def writer(directory: Path) -> None:
        convert_compact_root(
            root_paths, source_manifest, policy_path, directory / payload_name
        )

    def validator(directory: Path) -> None:
        payload = directory / payload_name
        with h5py.File(payload, "r") as handle:
            stored = str(handle.attrs.get("semantic_sha256", ""))
        if stored != canonical_semantic_hash(payload):
            raise IntegrityError("DATA_SEMANTIC_HASH", "canonical payload hash is invalid")

    return publish_artifact(
        final,
        writer,
        validator,
        input_hashes,
        config_sha256,
        "particleml.dataset.publish_canonical_artifact-v1",
    )


def publish_preprocessing_artifact(
    canonical: Path,
    policy_path: Path,
    final: Path,
    *,
    payload_name: str = "preprocessing.json",
) -> Artifact:
    """Publish one training-fitted state through the formal directory lifecycle."""

    if Path(payload_name).name != payload_name or not payload_name:
        raise ContractError("DATA_OUTPUT_NAME", "preprocessing payload_name must be one filename")
    with h5py.File(canonical, "r") as handle:
        canonical_hash = str(handle.attrs.get("semantic_sha256", ""))
    config_sha256 = hashlib.sha256(policy_path.read_bytes()).hexdigest()

    def writer(directory: Path) -> None:
        fit_preprocessing_state(canonical, policy_path, directory / payload_name)

    def validator(directory: Path) -> None:
        value = json.loads((directory / payload_name).read_text(encoding="utf-8"))
        stored = value.pop("content_sha256", None)
        if stored != hashlib.sha256(_canonical_json(value)).hexdigest():
            raise IntegrityError("DATA_STATE_HASH", "preprocessing state hash is invalid")

    return publish_artifact(
        final,
        writer,
        validator,
        {"canonical_semantic_sha256": canonical_hash},
        config_sha256,
        "particleml.dataset.publish_preprocessing_artifact-v1",
    )
