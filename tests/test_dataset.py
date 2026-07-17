from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
import pytest

from particleml.contracts import ContractError, IntegrityError
from particleml.dataset import (
    canonical_semantic_hash,
    convert_compact_root,
    fit_preprocessing_state,
    pid_type,
    track_state,
    wrap_delta_phi,
)
from tests.fixtures.generate_compact_root import default_jets, write_compact_root


def _policy(path: Path) -> Path:
    document = {
        "schema_version": "1.0.0",
        "feature_version": "full-d-v1",
        "min_particle_pt_gev": 0.1,
        "min_particle_energy_gev": 0.1,
        "pid_vocabulary": {
            "unknown": 0,
            "charged_hadron": 1,
            "neutral_hadron": 2,
            "photon": 3,
            "electron": 4,
            "muon": 5,
        },
        "pt_eta_control": {"mode": "none"},
        "pileup_policy": {"mode": "diagnostic_only"},
        "d_field_unit": "cm",
        "d_field_transform": {"mode": "training_fitted"},
        "missing_track_policy": "zero_with_track_state",
    }
    path.write_text(json.dumps(document) + "\n", encoding="utf-8", newline="\n")
    return path


def _manifest(path: Path, jets: list[dict[str, object]]) -> Path:
    rows = sorted({(int(jet["record_id"]), str(jet["canonical_pfn"])) for jet in jets})
    payload = "".join(f"{record_id}\t{pfn}\t1234abcd\t1\n" for record_id, pfn in rows).encode()
    path.write_bytes(payload)
    return path


def _converted(tmp_path: Path) -> Path:
    jets = default_jets()
    root = write_compact_root(tmp_path / "compact.root", jets)
    manifest = _manifest(tmp_path / "source.tsv", jets)
    output = tmp_path / "canonical.h5"
    convert_compact_root([root], manifest, _policy(tmp_path / "policy.json"), output)
    return output


def test_transform_pid_and_track_state_contracts() -> None:
    assert wrap_delta_phi(3.5) == pytest.approx(3.5 - 2 * np.pi)
    assert pid_type(211) == pid_type(-211) == 1
    assert pid_type(999999) == 0
    assert track_state(1.0, True) == 1
    assert track_state(0.0, False) == 2
    assert track_state(-1.0, False) == 3


def test_canonical_layout(tmp_path: Path) -> None:
    output = _converted(tmp_path)

    with h5py.File(output, "r") as handle:
        assert handle["particles/continuous"].shape == (4, 150, 9)
        assert handle["particles/continuous"].dtype == np.dtype("float32")
        assert handle["particles/pid_type"].dtype == np.dtype("uint8")
        assert handle["particles/mask"].dtype == np.dtype("bool")
        assert handle["particles/track_state"].dtype == np.dtype("uint8")
        assert handle["labels/pid"][:].tolist() == [0, 1, 0, 1]
        assert handle["particles/mask"][:, :3].all()
        assert not handle["particles/mask"][:, 3:].any()
        assert np.all(handle["particles/continuous"][:, 3:, :] == 0)
        assert handle["particles/pid_type"][0, :3].tolist() == [3, 5, 1]
        assert handle["particles/track_state"][0, :3].tolist() == [2, 3, 1]
        assert handle.attrs["semantic_sha256"] == canonical_semantic_hash(output)
        assert handle["particles/continuous"].compression == "gzip"
        assert handle["particles/continuous"].compression_opts == 4


def test_fit_uses_train_only(tmp_path: Path) -> None:
    canonical = _converted(tmp_path)
    first = fit_preprocessing_state(
        canonical, _policy(tmp_path / "fit-policy.json"), tmp_path / "state-1.json"
    )
    with h5py.File(canonical, "r+") as handle:
        splits = handle["split/name"].asstr()[:]
        handle["particles/continuous"][splits != "train", :, :] = 999.0
    second = fit_preprocessing_state(
        canonical, _policy(tmp_path / "fit-policy-2.json"), tmp_path / "state-2.json"
    )

    assert first["training_jet_ids"] == second["training_jet_ids"]
    assert first["continuous_location"] == second["continuous_location"]
    assert first["continuous_scale"] == second["continuous_scale"]


def test_semantic_hash_is_repeatable(tmp_path: Path) -> None:
    first = _converted(tmp_path / "first")
    second = _converted(tmp_path / "second")

    assert canonical_semantic_hash(first) == canonical_semantic_hash(second)


def test_policy_requires_positive_particle_thresholds(tmp_path: Path) -> None:
    jets = default_jets()
    root = write_compact_root(tmp_path / "compact.root", jets)
    manifest = _manifest(tmp_path / "source.tsv", jets)
    policy = json.loads(_policy(tmp_path / "policy.json").read_text(encoding="utf-8"))
    del policy["min_particle_pt_gev"]
    (tmp_path / "policy.json").write_text(json.dumps(policy), encoding="utf-8")

    with pytest.raises(ContractError, match="DATA_POLICY"):
        convert_compact_root([root], manifest, tmp_path / "policy.json", tmp_path / "out.h5")


def test_non_finite_particle_fails_closed(tmp_path: Path) -> None:
    jets = default_jets()
    jets[0]["particle_pt"] = [float("nan")]
    for name in (
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
    ):
        jets[0][name] = [jets[0][name][0]]
    root = write_compact_root(tmp_path / "bad.root", jets)

    with pytest.raises(IntegrityError, match="DATA_NONFINITE"):
        convert_compact_root(
            [root],
            _manifest(tmp_path / "source.tsv", jets),
            _policy(tmp_path / "policy.json"),
            tmp_path / "out.h5",
        )


def test_particle_order_is_stable_and_truncated(tmp_path: Path) -> None:
    jets = default_jets()
    count = 151
    jets[0]["particle_pt"] = [float(index + 1) for index in range(count)]
    jets[0]["particle_energy"] = [float(index + 2) for index in range(count)]
    for name, value in (
        ("particle_pdg_id", 211),
        ("particle_eta", 0.0),
        ("particle_phi", 0.0),
        ("particle_charge", 1.0),
        ("particle_dxy", 0.0),
        ("particle_dxy_error", 0.0),
        ("particle_dz", 0.0),
        ("particle_dz_error", 0.0),
        ("particle_has_track_details", True),
    ):
        jets[0][name] = [value] * count
    output = tmp_path / "canonical.h5"
    convert_compact_root(
        [write_compact_root(tmp_path / "long.root", jets)],
        _manifest(tmp_path / "source.tsv", jets),
        _policy(tmp_path / "policy.json"),
        output,
    )

    with h5py.File(output, "r") as handle:
        log_pt = handle["particles/continuous"][0, :, 2]
        assert np.all(np.diff(log_pt) <= 0)
        assert log_pt[0] == pytest.approx(np.log(151.0))
        assert log_pt[-1] == pytest.approx(np.log(2.0))


def test_duplicate_jet_identity_fails_closed(tmp_path: Path) -> None:
    jets = default_jets()
    jets.append(dict(jets[0]))

    with pytest.raises(IntegrityError, match="DATA_DUPLICATE_IDENTITY"):
        convert_compact_root(
            [write_compact_root(tmp_path / "duplicate.root", jets)],
            _manifest(tmp_path / "source.tsv", jets),
            _policy(tmp_path / "policy.json"),
            tmp_path / "out.h5",
        )


def test_empty_constituent_jet_is_masked_without_invented_particles(tmp_path: Path) -> None:
    jets = default_jets()
    for name in (
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
    ):
        jets[0][name] = []
    output = tmp_path / "canonical.h5"
    convert_compact_root(
        [write_compact_root(tmp_path / "empty-jet.root", jets)],
        _manifest(tmp_path / "source.tsv", jets),
        _policy(tmp_path / "policy.json"),
        output,
    )

    with h5py.File(output, "r") as handle:
        assert not handle["particles/mask"][0].any()
        assert np.all(handle["particles/continuous"][0] == 0)


def test_preprocessing_state_content_hash_is_canonical_json(tmp_path: Path) -> None:
    canonical = _converted(tmp_path)
    state = fit_preprocessing_state(
        canonical, _policy(tmp_path / "fit-policy.json"), tmp_path / "state.json"
    )
    stored = state.pop("content_sha256")
    canonical_bytes = (
        json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()

    assert stored == hashlib.sha256(canonical_bytes).hexdigest()
