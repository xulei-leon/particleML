from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]
RUNPOD_DIR = ROOT / "containers" / "runpod"
RECORD_PATH = RUNPOD_DIR / "environment-record.template.json"
SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_?key|credential|password|private_?key|secret|token)(?:$|_)",
    re.IGNORECASE,
)
RUNTIME_IDENTITY_FIELDS = {
    "captured_at_utc",
    "image_digest",
    "dependency_lock_sha256",
    "cuda_version",
    "driver_version",
    "pytorch_version",
    "gpu_model",
    "gpu_vram_mib",
}


def _credential_shaped_paths(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if SECRET_KEY.search(str(key)):
                findings.append(path)
            findings.extend(_credential_shaped_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_credential_shaped_paths(child, f"{prefix}[{index}]"))
    return findings


def _assert_secret_free(record: Mapping[str, Any]) -> None:
    findings = _credential_shaped_paths(record)
    assert findings == [], f"credential-shaped fields are forbidden: {findings}"


def test_runpod_image_and_dependencies_are_pinned() -> None:
    dockerfile = (RUNPOD_DIR / "Dockerfile").read_text(encoding="utf-8")
    first_instruction = next(
        line.strip()
        for line in dockerfile.splitlines()
        if line.strip() and not line.startswith("#")
    )
    assert re.fullmatch(r"FROM [^\s]+@sha256:[0-9a-f]{64}", first_instruction)

    requirements = (RUNPOD_DIR / "requirements.lock").read_text(encoding="utf-8")
    pinned = [
        line
        for line in requirements.splitlines()
        if line and not line[0].isspace() and not line.startswith("#")
    ]
    assert pinned
    for line in pinned:
        requirement = Requirement(line)
        specifiers = list(requirement.specifier)
        assert len(specifiers) == 1
        assert specifiers[0].operator == "=="


def test_docker_build_context_excludes_local_and_secret_state() -> None:
    dockerfile = (RUNPOD_DIR / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY . " not in dockerfile

    ignored = {
        line.strip()
        for line in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert {
        ".git/",
        ".venv/",
        "*.env",
        "*.key",
        "*.pem",
        "data/",
        "node_modules/",
        "project/4-Reviews/",
    } <= ignored


def test_environment_record_template_is_complete_and_unpopulated() -> None:
    record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    assert record["schema_version"] == "1.0.0"
    assert record["image_reference"].count("@sha256:") == 1
    assert record["dependency_lock_path"] == "containers/runpod/requirements.lock"
    assert RUNTIME_IDENTITY_FIELDS <= record.keys()
    assert all(record[field] is None for field in RUNTIME_IDENTITY_FIELDS)
    _assert_secret_free(record)


def test_environment_record_rejects_credential_shaped_fields() -> None:
    record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    record["api_token"] = "must-not-be-recorded"

    with pytest.raises(AssertionError, match="credential-shaped fields"):
        _assert_secret_free(record)
