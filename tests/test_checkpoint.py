from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from particleml.contracts import IntegrityError
from particleml.model_integration import tensor_load_report, validate_checkpoint


def test_checkpoint_identity_license_and_hash(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"immutable checkpoint fixture")
    metadata = {
        "schema_version": "1.0.0",
        "source": "https://example.invalid/releases/model.pt",
        "immutable_revision": "release-2026-01",
        "filename": "model.pt",
        "sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        "license": "Apache-2.0",
        "pretraining_corpus": "documented fixture corpus",
        "input_schema": "pT,eta,phi,mass plus native optional fields",
        "normalization": "documented training normalization",
    }
    metadata_path = tmp_path / "checkpoint.json"
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    assert validate_checkpoint(checkpoint, metadata_path) == metadata
    checkpoint.write_bytes(b"mutated")
    with pytest.raises(IntegrityError, match="CHECKPOINT_HASH"):
        validate_checkpoint(checkpoint, metadata_path)


def test_tensor_load_report_is_sorted_and_keeps_shapes() -> None:
    report = tensor_load_report(
        {"z": [2], "a": [2, 3], "missing": [1]},
        {"a": [2, 4], "z": [2]},
    )
    assert report.loaded == ("z",)
    assert report.skipped == ("missing",)
    assert [item.name for item in report.mismatched] == ["a"]
    assert report.mismatched[0].source_shape == (2, 3)
    assert report.mismatched[0].target_shape == (2, 4)


def test_checkpoint_rejects_mutable_nickname(tmp_path: Path) -> None:
    checkpoint = tmp_path / "model.pt"
    checkpoint.write_bytes(b"x")
    metadata = {
        "schema_version": "1.0.0",
        "source": "https://example.invalid/model.pt",
        "immutable_revision": "pretrain_s",
        "filename": "model.pt",
        "sha256": hashlib.sha256(b"x").hexdigest(),
        "license": "Apache-2.0",
        "pretraining_corpus": "known",
        "input_schema": "known",
        "normalization": "known",
    }
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps(metadata), encoding="utf-8")
    with pytest.raises(Exception, match="CHECKPOINT_MUTABLE_ID"):
        validate_checkpoint(checkpoint, path)

