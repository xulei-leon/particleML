from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from particleml.contracts import ConfigurationError, ExternalDependencyError, FeatureConfig
from particleml.model_integration import (
    OMNILEARNED_REVISION,
    adapter_flags,
    build_train_argv,
    run_external,
    validate_external_argv,
    validate_index,
)


def _payload_hash(root: Path, names: list[str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(names):
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256((root / name).read_bytes()).digest())
    return digest.hexdigest()


def test_exact_a_d_adapter_and_command_mapping(tmp_path: Path) -> None:
    assert adapter_flags(FeatureConfig.A) == ()
    assert adapter_flags(FeatureConfig.B) == ("--use-add", "--num-add", "1")
    assert adapter_flags(FeatureConfig.C) == (
        "--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "1"
    )
    assert adapter_flags(FeatureConfig.D) == (
        "--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "5"
    )
    command = build_train_argv(
        tmp_path / "omnilearned",
        tmp_path / "index",
        tmp_path / "out",
        tmp_path / "checkpoint.pt",
        FeatureConfig.D,
        model_size="small",
        train_size_per_class=1000,
        model_seed=7,
    )
    assert command.count("--model-size") == 1
    assert command[command.index("--model-size") + 1] == "small"
    assert command[command.index("--train-size-per-class") + 1] == "1000"
    assert command[-6:] == ("--use-pid", "--pid_idx", "4", "--use-add", "--num-add", "5")


def test_allowlist_rejects_shell_strings_conditional_and_unknown_flags(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="RUN_ARGV_TYPE"):
        validate_external_argv("omnilearned train")
    base = ["omnilearned", "train", "--revision", OMNILEARNED_REVISION]
    with pytest.raises(ConfigurationError, match="RUN_FLAG_FORBIDDEN"):
        validate_external_argv([*base, "--use-global"])
    with pytest.raises(ConfigurationError, match="RUN_FLAG_NOT_ALLOWED"):
        validate_external_argv([*base, "--experimental"])
    with pytest.raises(ExternalDependencyError, match="RUN_REVISION_MISMATCH"):
        validate_external_argv(["omnilearned", "train", "--revision", "mutable-main"])


def test_subprocess_boundary_uses_argument_array_shell_false_and_redacts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, object] = {}

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["argv"] = argv
        captured.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, "Bearer abc.secret", "https://x/?token=value")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_external(
        ["omnilearned", "train", "--revision", OMNILEARNED_REVISION],
        cwd=tmp_path,
        timeout_seconds=5,
    )
    assert isinstance(captured["argv"], list)
    assert captured["shell"] is False
    assert captured["capture_output"] is True
    assert captured["timeout"] == 5
    assert "abc.secret" not in result.stdout
    assert "token=value" not in result.stderr


def test_index_required_and_hashed_and_stale_view_rejected(tmp_path: Path) -> None:
    root = tmp_path / "index"
    root.mkdir()
    (root / "part.bin").write_bytes(b"index")
    view_hash = "a" * 64
    record = {
        "schema_version": "1.0.0",
        "dependency_revision": OMNILEARNED_REVISION,
        "source_view_sha256": view_hash,
        "feature_config": "A",
        "row_count": 12,
        "files": ["part.bin"],
        "payload_sha256": _payload_hash(root, ["part.bin"]),
        "official_smoke_loaded": True,
        "evidence_origin": "qualified_runpod",
    }
    (root / "COMPLETED.json").write_text(json.dumps(record), encoding="utf-8")
    assert validate_index(root, expected_view_sha256=view_hash, expected_row_count=12) == record
    with pytest.raises(Exception, match="INDEX_STALE_VIEW"):
        validate_index(root, expected_view_sha256="b" * 64, expected_row_count=12)
