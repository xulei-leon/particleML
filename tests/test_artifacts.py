from __future__ import annotations

import json
from pathlib import Path

import pytest

import particleml.artifacts as artifacts_module
from particleml.artifacts import publish_artifact, resume_artifact
from particleml.contracts import IntegrityError

INPUTS = {"source_manifest": "1" * 64}
CONFIG_HASH = "2" * 64


def _writer(directory: Path) -> None:
    (directory / "payload.txt").write_text("payload\n", encoding="utf-8", newline="\n")


def _validator(directory: Path) -> None:
    assert (directory / "payload.txt").read_text(encoding="utf-8") == "payload\n"


def test_completed_marker_controls_resume(tmp_path: Path) -> None:
    final = tmp_path / "artifact"

    published = publish_artifact(final, _writer, _validator, INPUTS, CONFIG_HASH, "test-writer")
    resumed = resume_artifact(final, INPUTS, CONFIG_HASH)

    marker = json.loads((final / "COMPLETED.json").read_text(encoding="utf-8"))
    assert published == resumed
    assert marker["artifact_sha256"] == published.sha256
    assert marker["input_hashes"] == INPUTS


def test_partial_output_is_not_complete(tmp_path: Path) -> None:
    final = tmp_path / "artifact"
    final.mkdir()
    (final / "payload.txt").write_text("payload\n", encoding="utf-8")

    with pytest.raises(IntegrityError, match="ARTIFACT_INCOMPLETE"):
        resume_artifact(final, INPUTS, CONFIG_HASH)


def test_resume_rejects_stale_inputs_and_payload_mutation(tmp_path: Path) -> None:
    final = tmp_path / "artifact"
    publish_artifact(final, _writer, _validator, INPUTS, CONFIG_HASH, "test-writer")

    with pytest.raises(IntegrityError, match="ARTIFACT_RESUME_MISMATCH"):
        resume_artifact(final, {"source_manifest": "3" * 64}, CONFIG_HASH)

    (final / "payload.txt").write_text("mutated\n", encoding="utf-8")
    with pytest.raises(IntegrityError, match="ARTIFACT_HASH_MISMATCH"):
        resume_artifact(final, INPUTS, CONFIG_HASH)


def test_formal_output_is_never_overwritten(tmp_path: Path) -> None:
    final = tmp_path / "artifact"
    publish_artifact(final, _writer, _validator, INPUTS, CONFIG_HASH, "test-writer")

    with pytest.raises(IntegrityError, match="ARTIFACT_EXISTS"):
        publish_artifact(final, _writer, _validator, INPUTS, CONFIG_HASH, "test-writer")


def test_failed_validation_leaves_no_published_output(tmp_path: Path) -> None:
    final = tmp_path / "artifact"

    def reject(_directory: Path) -> None:
        raise ValueError("invalid")

    with pytest.raises(ValueError, match="invalid"):
        publish_artifact(final, _writer, reject, INPUTS, CONFIG_HASH, "test-writer")

    assert not final.exists()
    assert not list(tmp_path.glob("artifact.partial.*"))


def test_cleanup_error_does_not_mask_validation_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    final = tmp_path / "artifact"

    def reject(_directory: Path) -> None:
        raise ValueError("original validation error")

    def fail_cleanup(*_args: object, **_kwargs: object) -> None:
        raise OSError("cleanup failed")

    monkeypatch.setattr(artifacts_module.shutil, "rmtree", fail_cleanup)

    with pytest.raises(ValueError, match="original validation error"):
        publish_artifact(final, _writer, reject, INPUTS, CONFIG_HASH, "test-writer")
