from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py

from particleml.cli import main
from particleml.contracts import validate_contract_document
from particleml.dataset import fit_preprocessing_state
from tests.fixtures.generate_compact_root import default_jets, write_compact_root
from tests.test_dataset import _manifest, _policy


def test_manifest_validate_prints_exact_hash(tmp_path: Path, capsys: object) -> None:
    source = tmp_path / "source.tsv"
    source.write_bytes(b"1\troot://example.invalid//a.root\t1234abcd\t1\n")

    assert main(["manifest", "validate", "--source", str(source)]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert len(output.strip()) == 64


def test_missing_input_maps_to_stable_exit_code(tmp_path: Path, capsys: object) -> None:
    missing = tmp_path / "missing.tsv"

    assert main(["manifest", "validate", "--source", str(missing)]) == 3
    assert "INPUT_NOT_FOUND" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_invalid_manifest_maps_to_integrity_exit_code(tmp_path: Path, capsys: object) -> None:
    source = tmp_path / "source.tsv"
    source.write_bytes(b"invalid\r\n")

    assert main(["manifest", "validate", "--source", str(source)]) == 5
    assert "MANIFEST_LINE_ENDING" in capsys.readouterr().err  # type: ignore[attr-defined]


def _write_split_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    source = tmp_path / "source.tsv"
    source.write_bytes(
        b"18355\troot://example.invalid//store/test/file-8.root\t1234abcd\t10\n"
        b"19980\troot://example.invalid//store/test/file-2.root\t00abcdef\t20\n"
    )
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    canonical = tmp_path / "canonical-identities.json"
    canonical.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "canonical_dataset": {
                    "path": "canonical-full-d.h5",
                    "sha256": "4" * 64,
                    "byte_size": 123,
                },
                "jets": [
                    {
                        "record_id": 18355,
                        "canonical_pfn": "root://example.invalid//store/test/file-8.root",
                        "run": 1,
                        "lumi": 2,
                        "event": 3,
                        "jet_index": 0,
                        "target": 0,
                    },
                    {
                        "record_id": 19980,
                        "canonical_pfn": "root://example.invalid//store/test/file-2.root",
                        "run": 4,
                        "lumi": 5,
                        "event": 6,
                        "jet_index": 0,
                        "target": 1,
                    },
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    config = tmp_path / "split-config.json"
    config.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "manifest_id": "split-001",
                "study_id": "particleml-cms-2015",
                "created_at": "2026-07-17T00:00:00Z",
                "source_manifest": {"path": str(source), "sha256": source_hash},
                "source_roles": {"18355": "qcd_active", "19980": "signal"},
                "training_subsets": [
                    {"subset_id": "train-1", "train_size_per_class": 1, "subset_seed": 7}
                ],
                "preprocessing": {
                    "feature_version": "full-d-v1",
                    "policy": {"path": "preprocessing.json", "sha256": "5" * 64},
                    "fitted_partition": "train",
                    "pid_vocabulary": {
                        "unknown": 0,
                        "charged_hadron": 1,
                        "neutral_hadron": 2,
                        "photon": 3,
                        "electron": 4,
                        "muon": 5,
                    },
                    "impact_parameter_policy": "training_fitted",
                    "pt_eta_control_sha256": None,
                    "pileup_reweighting_sha256": None,
                },
            }
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    output = tmp_path / "split-manifest.json"
    return canonical, config, output


def _split_argv(canonical: Path, config: Path, output: Path) -> list[str]:
    return [
        "split",
        "build",
        "--canonical",
        str(canonical),
        "--config",
        str(config),
        "--output",
        str(output),
    ]


def test_split_build_writes_schema_valid_manifest_and_identity_payload(
    tmp_path: Path, capsys: object
) -> None:
    canonical, config, output = _write_split_fixture(tmp_path)

    assert main(_split_argv(canonical, config, output)) == 0

    document = json.loads(output.read_text(encoding="utf-8"))
    validate_contract_document(document, "split")
    identity_path = Path(document["training_subsets"][0]["identity_payload"]["path"])
    assert identity_path.is_file()
    assert document["partitions"]["train"]["jet_counts_by_class"] == {"qcd": 1, "top": 1}
    assert capsys.readouterr().out == f"valid split manifest: {output}\n"  # type: ignore[attr-defined]


def test_split_build_rejects_missing_inventory(tmp_path: Path, capsys: object) -> None:
    _canonical, config, output = _write_split_fixture(tmp_path)
    missing = tmp_path / "missing.json"

    assert main(_split_argv(missing, config, output)) == 3
    assert "INPUT_NOT_FOUND" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_split_build_rejects_source_hash_mismatch(tmp_path: Path, capsys: object) -> None:
    canonical, config, output = _write_split_fixture(tmp_path)
    document = json.loads(config.read_text(encoding="utf-8"))
    document["source_manifest"]["sha256"] = "f" * 64
    config.write_text(json.dumps(document) + "\n", encoding="utf-8", newline="\n")

    assert main(_split_argv(canonical, config, output)) == 5
    assert "MANIFEST_HASH_MISMATCH" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_split_build_rejects_invalid_identity_target(tmp_path: Path, capsys: object) -> None:
    canonical, config, output = _write_split_fixture(tmp_path)
    document = json.loads(canonical.read_text(encoding="utf-8"))
    document["jets"][0]["target"] = 2
    canonical.write_text(json.dumps(document) + "\n", encoding="utf-8", newline="\n")

    assert main(_split_argv(canonical, config, output)) == 4
    assert "CONTRACT_VALUE" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_split_build_rejects_output_collision(tmp_path: Path, capsys: object) -> None:
    canonical, config, output = _write_split_fixture(tmp_path)
    output.write_text("existing\n", encoding="utf-8")

    assert main(_split_argv(canonical, config, output)) == 5
    assert "ARTIFACT_EXISTS" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_split_build_rejects_insufficient_active_qcd(tmp_path: Path, capsys: object) -> None:
    canonical, config, output = _write_split_fixture(tmp_path)
    document = json.loads(config.read_text(encoding="utf-8"))
    document["source_roles"]["18355"] = "qcd_candidate"
    config.write_text(json.dumps(document) + "\n", encoding="utf-8", newline="\n")

    assert main(_split_argv(canonical, config, output)) == 5
    assert "SPLIT_INSUFFICIENT_CLASS_YIELD" in capsys.readouterr().err  # type: ignore[attr-defined]


def test_data_pipeline_cli_commands(tmp_path: Path, capsys: object) -> None:
    jets = default_jets()
    root = write_compact_root(tmp_path / "compact.root", jets)
    source = _manifest(tmp_path / "source.tsv", jets)
    policy = _policy(tmp_path / "policy.json")
    canonical = tmp_path / "canonical.h5"

    assert (
        main(
            [
                "convert",
                "--input",
                str(root),
                "--source-manifest",
                str(source),
                "--policy",
                str(policy),
                "--output",
                str(canonical),
            ]
        )
        == 0
    )
    preprocessing = tmp_path / "preprocessing.json"
    fit_preprocessing_state(canonical, policy, preprocessing)
    with h5py.File(canonical, "r") as handle:
        ids = handle["identity/jet_id"].asstr()[:2].tolist()
    identities = tmp_path / "identities.json"
    identities.write_text(
        json.dumps({"qcd": [ids[0]], "top": [ids[1]]}) + "\n", encoding="utf-8"
    )
    subset_sha256 = hashlib.sha256(identities.read_bytes()).hexdigest()
    views: list[Path] = []
    for feature_config in ("A", "B", "C", "D"):
        view = tmp_path / f"view-{feature_config}.h5"
        views.append(view)
        assert (
            main(
                [
                    "view",
                    "build",
                    "--canonical",
                    str(canonical),
                    "--preprocessing",
                    str(preprocessing),
                    "--identities",
                    str(identities),
                    "--split-manifest-sha256",
                    "f" * 64,
                    "--subset-sha256",
                    subset_sha256,
                    "--feature-config",
                    feature_config,
                    "--allow-unpublished-diagnostics",
                    "--output",
                    str(view),
                ]
            )
            == 0
        )
    audit_policy = tmp_path / "audit-policy.json"
    audit_policy.write_text(
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
    audit_output = tmp_path / "audit.json"
    assert (
        main(
            [
                "audit",
                "data",
                "--canonical",
                str(canonical),
                "--field",
                "delta_eta",
                "--policy",
                str(audit_policy),
                "--output",
                str(audit_output),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert f"valid canonical dataset: {canonical}" in output
    assert f"valid D view: {views[-1]}" in output
    assert f"data audit passed: {audit_output}" in output
