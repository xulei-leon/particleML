"""Immutable artifact publication and completion-marker validation."""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from particleml.contracts import SHA256_PATTERN, Artifact, IntegrityError

COMPLETION_FILENAME = "COMPLETED.json"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _validate_hashes(input_hashes: Mapping[str, str], config_sha256: str) -> None:
    if not SHA256_PATTERN.fullmatch(config_sha256):
        raise IntegrityError("ARTIFACT_HASH_FORMAT", "config_sha256 is invalid")
    for name, digest in input_hashes.items():
        if not name or not SHA256_PATTERN.fullmatch(digest):
            raise IntegrityError("ARTIFACT_HASH_FORMAT", f"invalid input hash: {name}")


def _payload_records(directory: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    paths = sorted(
        directory.rglob("*"), key=lambda item: item.relative_to(directory).as_posix()
    )
    for path in paths:
        if path.is_symlink():
            raise IntegrityError("ARTIFACT_SYMLINK", f"symlink payload is forbidden: {path}")
        if not path.is_file() or path.name == COMPLETION_FILENAME:
            continue
        payload = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(directory).as_posix(),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "byte_size": len(payload),
            }
        )
    if not records:
        raise IntegrityError("ARTIFACT_EMPTY", "artifact has no payload files")
    return records


def _artifact_hash(records: list[dict[str, object]]) -> str:
    return hashlib.sha256(_canonical_json(records)).hexdigest()


def publish_artifact(
    final: Path,
    writer: Callable[[Path], None],
    validator: Callable[[Path], None],
    input_hashes: Mapping[str, str],
    config_sha256: str,
    writer_version: str,
) -> Artifact:
    """Write, validate, hash, publish, and mark one immutable directory artifact."""

    _validate_hashes(input_hashes, config_sha256)
    if not writer_version:
        raise IntegrityError("ARTIFACT_WRITER_VERSION", "writer_version must not be empty")
    final.parent.mkdir(parents=True, exist_ok=True)
    if final.exists():
        raise IntegrityError("ARTIFACT_EXISTS", f"formal output already exists: {final}")
    partial = final.with_name(f"{final.name}.partial.{uuid.uuid4()}")
    partial.mkdir()
    published = False
    try:
        writer(partial)
        validator(partial)
        records = _payload_records(partial)
        digest = _artifact_hash(records)
        partial.rename(final)
        published = True
        marker = {
            "schema_version": "1.0.0",
            "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "writer_version": writer_version,
            "input_hashes": dict(sorted(input_hashes.items())),
            "config_sha256": config_sha256,
            "payloads": records,
            "artifact_sha256": digest,
        }
        (final / COMPLETION_FILENAME).write_bytes(_canonical_json(marker))
        return Artifact(final, digest, "1.0.0")
    finally:
        if not published and partial.exists():
            try:
                shutil.rmtree(partial)
            except OSError:
                pass


def _load_marker(final: Path) -> dict[str, Any]:
    marker_path = final / COMPLETION_FILENAME
    if not final.is_dir() or not marker_path.is_file():
        raise IntegrityError("ARTIFACT_INCOMPLETE", f"missing authoritative marker: {marker_path}")
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntegrityError("ARTIFACT_INCOMPLETE", f"invalid completion marker: {exc}") from exc
    if not isinstance(marker, dict):
        raise IntegrityError("ARTIFACT_INCOMPLETE", "completion marker must be an object")
    return marker


def resume_artifact(
    final: Path,
    input_hashes: Mapping[str, str],
    config_sha256: str,
) -> Artifact:
    """Reuse a completed artifact only when request and payload hashes still match."""

    _validate_hashes(input_hashes, config_sha256)
    marker = _load_marker(final)
    if marker.get("input_hashes") != dict(sorted(input_hashes.items())) or marker.get(
        "config_sha256"
    ) != config_sha256:
        raise IntegrityError("ARTIFACT_RESUME_MISMATCH", "input or configuration hashes differ")
    records = _payload_records(final)
    digest = _artifact_hash(records)
    if marker.get("payloads") != records or marker.get("artifact_sha256") != digest:
        raise IntegrityError(
            "ARTIFACT_HASH_MISMATCH",
            "published payload does not match completion marker",
        )
    return Artifact(final, digest, str(marker.get("schema_version", "1.0.0")))
