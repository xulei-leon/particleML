from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import pytest

from particleml.artifacts import publish_artifact
from particleml.contracts import ContractError, FeatureConfig, IntegrityError
from particleml.dataset import (
    convert_compact_root,
    fit_preprocessing_state,
    publish_canonical_artifact,
    publish_preprocessing_artifact,
)
from particleml.views import (
    SubsetJet,
    materialize_view,
    select_nested_subsets,
    view_argv,
)
from tests.fixtures.generate_compact_root import default_jets, write_compact_root
from tests.test_dataset import _manifest, _policy


def _pipeline(tmp_path: Path) -> tuple[Path, Path, Path]:
    jets = default_jets()
    canonical = tmp_path / "canonical.h5"
    convert_compact_root(
        [write_compact_root(tmp_path / "compact.root", jets)],
        _manifest(tmp_path / "source.tsv", jets),
        _policy(tmp_path / "policy.json"),
        canonical,
    )
    state_path = tmp_path / "preprocessing.json"
    fit_preprocessing_state(canonical, _policy(tmp_path / "fit-policy.json"), state_path)
    with h5py.File(canonical, "r") as handle:
        ids = handle["identity/jet_id"].asstr()[:]
        splits = handle["split/name"].asstr()[:]
        labels = handle["labels/pid"][:]
        records = handle["identity/record_id"][:]
    selected = [
        jet_id
        for jet_id, split, label in zip(ids, splits, labels, strict=True)
        if split == "train" and label in (0, 1)
    ]
    payload = {
        "schema_version": "1.0.0",
        "subset_id": "train-1",
        "subset_seed": 7,
        "qcd": [selected[0]],
        "top": [selected[1]],
        "record_ids": records[:2].tolist(),
    }
    payload_path = tmp_path / "identities.json"
    payload_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return canonical, state_path, payload_path


def test_balanced_nested_subsets() -> None:
    jets = [SubsetJet(19980, f"top-{index}", 1) for index in range(4)] + [
        SubsetJet(record, f"qcd-{record}-{index}", 0) for index in range(2) for record in (10, 20)
    ]

    subsets = select_nested_subsets(jets, (1, 2, 4), 7, {10, 20})

    assert subsets[1]["top"] == subsets[2]["top"][:1]
    assert subsets[2]["qcd"] == subsets[4]["qcd"][:2]
    assert [value.split("-")[1] for value in subsets[4]["qcd"][:2]] == ["10", "20"]


def test_insufficient_subset_yield_fails() -> None:
    with pytest.raises(IntegrityError, match="SPLIT_INSUFFICIENT_CLASS_YIELD"):
        select_nested_subsets([SubsetJet(1, "top-1", 1)], (1,), 7, {10})


def test_ad_identity_equivalence(tmp_path: Path) -> None:
    canonical, state, identities = _pipeline(tmp_path)
    outputs: dict[FeatureConfig, Path] = {}
    for config in FeatureConfig:
        output = tmp_path / f"view-{config.value}.h5"
        materialize_view(canonical, state, identities, "f" * 64, config, output)
        outputs[config] = output

    expected_fields = {
        FeatureConfig.A: 4,
        FeatureConfig.B: 5,
        FeatureConfig.C: 6,
        FeatureConfig.D: 10,
    }
    reference_ids: list[str] | None = None
    for config, output in outputs.items():
        with h5py.File(output, "r") as handle:
            ids = handle["jet_id"].asstr()[:].tolist()
            reference_ids = ids if reference_ids is None else reference_ids
            assert ids == reference_ids
            assert handle["data"].shape == (2, 150, expected_fields[config])
            assert json.loads(handle.attrs["omnilearned_argv_json"]) == view_argv(config)
    with h5py.File(outputs[FeatureConfig.C], "r") as handle:
        assert json.loads(handle.attrs["field_names_json"])[4] == "pid_type"
    with h5py.File(outputs[FeatureConfig.D], "r") as handle:
        assert "pid_one_hot" not in json.loads(handle.attrs["field_names_json"])


def test_view_rejects_stale_canonical_content(tmp_path: Path) -> None:
    canonical, state, identities = _pipeline(tmp_path)
    with h5py.File(canonical, "r+") as handle:
        handle["particles/continuous"][0, 0, 0] += 1.0

    with pytest.raises(IntegrityError, match="VIEW_STALE_HASH"):
        materialize_view(
            canonical,
            state,
            identities,
            "f" * 64,
            FeatureConfig.A,
            tmp_path / "stale.h5",
        )


def test_view_rejects_stale_subset_hash_and_missing_identity(tmp_path: Path) -> None:
    canonical, state, identities = _pipeline(tmp_path)

    with pytest.raises(IntegrityError, match="VIEW_STALE_HASH"):
        materialize_view(
            canonical,
            state,
            identities,
            "f" * 64,
            FeatureConfig.A,
            tmp_path / "stale-subset.h5",
            expected_subset_sha256="0" * 64,
        )

    payload = json.loads(identities.read_text(encoding="utf-8"))
    payload["top"] = ["missing-jet-id"]
    identities.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    current_hash = hashlib.sha256(identities.read_bytes()).hexdigest()
    with pytest.raises(IntegrityError, match="VIEW_IDENTITY"):
        materialize_view(
            canonical,
            state,
            identities,
            "f" * 64,
            FeatureConfig.A,
            tmp_path / "missing.h5",
            expected_subset_sha256=current_hash,
        )


def test_view_rejects_invalid_split_hash(tmp_path: Path) -> None:
    canonical, state, identities = _pipeline(tmp_path)

    with pytest.raises(ContractError, match="VIEW_HASH_FORMAT"):
        materialize_view(
            canonical,
            state,
            identities,
            "not-a-hash",
            FeatureConfig.A,
            tmp_path / "invalid.h5",
        )


def test_formal_view_rejects_unpublished_dependencies(tmp_path: Path) -> None:
    canonical, state, identities = _pipeline(tmp_path)

    with pytest.raises(IntegrityError, match="VIEW_STALE_HASH"):
        materialize_view(
            canonical,
            state,
            identities,
            "f" * 64,
            FeatureConfig.A,
            tmp_path / "formal.h5",
            expected_subset_sha256=hashlib.sha256(identities.read_bytes()).hexdigest(),
            require_completed_dependencies=True,
        )


def test_formal_view_accepts_completed_dependency_payloads(tmp_path: Path) -> None:
    jets = default_jets()
    source = _manifest(tmp_path / "source.tsv", jets)
    policy = _policy(tmp_path / "policy.json")
    canonical_artifact = tmp_path / "canonical-artifact"
    publish_canonical_artifact(
        [write_compact_root(tmp_path / "compact.root", jets)],
        source,
        policy,
        canonical_artifact,
    )
    canonical = canonical_artifact / "canonical.h5"
    state_artifact = tmp_path / "state-artifact"
    publish_preprocessing_artifact(canonical, policy, state_artifact)
    state = state_artifact / "preprocessing.json"
    with h5py.File(canonical, "r") as handle:
        ids = handle["identity/jet_id"].asstr()[:2].tolist()

    identity_artifact = tmp_path / "identity-artifact"
    identity_bytes = (json.dumps({"qcd": [ids[0]], "top": [ids[1]]}) + "\n").encode()
    publish_artifact(
        identity_artifact,
        lambda directory: (directory / "identities.json").write_bytes(identity_bytes),
        lambda directory: (directory / "identities.json").read_bytes(),
        {"split": "1" * 64},
        "2" * 64,
        "test-identity-writer",
    )
    split_artifact = tmp_path / "split-artifact"
    split_bytes = b'{"schema_version":"1.0.0"}\n'
    publish_artifact(
        split_artifact,
        lambda directory: (directory / "split.json").write_bytes(split_bytes),
        lambda directory: (directory / "split.json").read_bytes(),
        {"source": "3" * 64},
        "4" * 64,
        "test-split-writer",
    )

    output = tmp_path / "formal-view.h5"
    materialize_view(
        canonical,
        state,
        identity_artifact / "identities.json",
        hashlib.sha256(split_bytes).hexdigest(),
        FeatureConfig.D,
        output,
        expected_subset_sha256=hashlib.sha256(identity_bytes).hexdigest(),
        split_manifest_path=split_artifact / "split.json",
        require_completed_dependencies=True,
    )

    assert output.is_file()
