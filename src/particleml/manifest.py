"""Exact-byte source-manifest, split, and stable-identity helpers."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from particleml.contracts import (
    SHA256_PATTERN,
    ConfigurationError,
    ContractError,
    InputError,
    IntegrityError,
    Split,
)

CHECKSUM_PATTERN = re.compile(r"^[0-9a-fA-F]{8}$")


@dataclass(frozen=True)
class SourceFile:
    """One validated source-manifest row."""

    record_id: int
    canonical_pfn: str
    adler32: str
    size_bytes: int


@dataclass(frozen=True)
class SourceManifest:
    """Validated rows bound to their exact serialized bytes."""

    path: Path
    entries: tuple[SourceFile, ...]
    raw_bytes: bytes


@dataclass(frozen=True)
class EventAssignment:
    """Minimal event identity used for split-disjointness validation."""

    record_id: int
    run: int
    lumi: int
    event: int
    split: Split


@dataclass(frozen=True)
class JetIdentity:
    """Minimal canonical identity-inventory row used by split construction."""

    record_id: int
    canonical_pfn: str
    run: int
    lumi: int
    event: int
    jet_index: int
    target: int

    @property
    def split(self) -> Split:
        return assign_split(self.canonical_pfn)

    @property
    def jet_id(self) -> str:
        return stable_jet_id(
            self.record_id,
            self.canonical_pfn,
            self.run,
            self.lumi,
            self.event,
            self.jet_index,
        )


def _manifest_error(code: str, message: str) -> IntegrityError:
    return IntegrityError(code, message)


def load_source_manifest(path: Path) -> SourceManifest:
    """Read and validate a canonical TSV without changing its bytes."""

    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise InputError("INPUT_NOT_FOUND", f"input does not exist: {path}") from exc
    except OSError as exc:
        raise InputError("INPUT_UNREADABLE", f"cannot read {path}: {exc}") from exc
    if raw.startswith(b"\xef\xbb\xbf"):
        raise _manifest_error("MANIFEST_BOM", "UTF-8 BOM is forbidden")
    if not raw or b"\r" in raw or not raw.endswith(b"\n"):
        raise _manifest_error("MANIFEST_LINE_ENDING", "manifest must use LF and end with LF")
    try:
        raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _manifest_error("MANIFEST_UTF8", f"invalid UTF-8 at byte {exc.start}") from exc

    entries: list[SourceFile] = []
    seen_pfns: set[str] = set()
    for line_number, raw_line in enumerate(raw[:-1].split(b"\n"), start=1):
        fields = raw_line.split(b"\t")
        if len(fields) != 4:
            raise _manifest_error("MANIFEST_FIELD_COUNT", f"line {line_number} needs four fields")
        if any(field == b"" for field in fields):
            raise _manifest_error("MANIFEST_EMPTY_FIELD", f"line {line_number} has an empty field")
        try:
            record_text, pfn_bytes, checksum_bytes, size_text = fields
            record_id = int(record_text.decode("ascii"))
            canonical_pfn = pfn_bytes.decode("utf-8")
            checksum = checksum_bytes.decode("ascii")
            size_bytes = int(size_text.decode("ascii"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise _manifest_error("MANIFEST_FIELD_VALUE", f"line {line_number} is invalid") from exc
        if record_id <= 0:
            raise _manifest_error("MANIFEST_RECORD_ID", f"line {line_number} record ID is invalid")
        if not CHECKSUM_PATTERN.fullmatch(checksum):
            raise _manifest_error("MANIFEST_CHECKSUM", f"line {line_number} checksum is invalid")
        if size_bytes <= 0:
            raise _manifest_error("MANIFEST_SIZE", f"line {line_number} size is not positive")
        if canonical_pfn in seen_pfns:
            raise _manifest_error("MANIFEST_DUPLICATE_PFN", f"duplicate PFN on line {line_number}")
        seen_pfns.add(canonical_pfn)
        entries.append(SourceFile(record_id, canonical_pfn, checksum, size_bytes))

    ordering = [(entry.record_id, entry.canonical_pfn.encode("utf-8")) for entry in entries]
    if ordering != sorted(ordering):
        raise _manifest_error("MANIFEST_ORDER", "rows are not in canonical order")
    return SourceManifest(path=path, entries=tuple(entries), raw_bytes=raw)


def hash_source_manifest(manifest: SourceManifest) -> str:
    """Return SHA-256 over the exact validated file bytes."""

    return hashlib.sha256(manifest.raw_bytes).hexdigest()


def hash_canonical_pfn(canonical_pfn: str) -> str:
    """Hash the exact UTF-8 PFN without normalization."""

    return hashlib.sha256(canonical_pfn.encode("utf-8")).hexdigest()


def split_bucket(canonical_pfn: str) -> int:
    """Return the exact unsigned-big-endian modulo-10 bucket."""

    digest = hashlib.sha256(canonical_pfn.encode("utf-8")).digest()
    return int.from_bytes(digest, byteorder="big", signed=False) % 10


def assign_split(canonical_pfn: str) -> Split:
    """Assign test bucket 0, validation bucket 1, and train otherwise."""

    return {0: Split.TEST, 1: Split.VALIDATION}.get(split_bucket(canonical_pfn), Split.TRAIN)


def _require_identifier_integer(name: str, value: int, *, positive: bool = False) -> None:
    minimum = 1 if positive else 0
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise IntegrityError("SPLIT_IDENTITY_VALUE", f"{name} must be an integer >= {minimum}")


def stable_jet_id(
    record_id: int,
    canonical_pfn: str,
    run: int,
    lumi: int,
    event: int,
    jet_index: int,
) -> str:
    """Build the exact stable textual jet identity from supplied coordinates."""

    _require_identifier_integer("record_id", record_id, positive=True)
    for name, value in (("run", run), ("lumi", lumi), ("event", event)):
        _require_identifier_integer(name, value, positive=True)
    _require_identifier_integer("jet_index", jet_index)
    return (
        f"cms:{record_id}:{hash_canonical_pfn(canonical_pfn)}:"
        f"{run}:{lumi}:{event}:{jet_index}"
    )


def validate_pfn_assignments(assignments: Iterable[tuple[str, Split]]) -> None:
    """Reject a PFN assigned more than once, including to the same partition."""

    seen: dict[str, Split] = {}
    for pfn, split in assignments:
        if pfn in seen:
            raise IntegrityError(
                "SPLIT_PFN_OVERLAP",
                f"PFN assigned more than once: {pfn} ({seen[pfn].value}, {split.value})",
            )
        seen[pfn] = split


def validate_event_disjointness(assignments: Iterable[EventAssignment]) -> None:
    """Reject one event identity appearing in multiple partitions."""

    seen: dict[tuple[int, int, int, int], Split] = {}
    for assignment in assignments:
        identity = (
            assignment.record_id,
            assignment.run,
            assignment.lumi,
            assignment.event,
        )
        prior = seen.get(identity)
        if prior is not None and prior is not assignment.split:
            raise IntegrityError(
                "SPLIT_EVENT_OVERLAP",
                f"event {identity} appears in {prior.value} and {assignment.split.value}",
            )
        seen[identity] = assignment.split


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise InputError("INPUT_NOT_FOUND", f"{label} does not exist: {path}") from exc
    except OSError as exc:
        raise InputError("INPUT_UNREADABLE", f"cannot read {label} {path}: {exc}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError("CONTRACT_JSON", f"invalid {label} JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError("CONTRACT_JSON", f"{label} root must be an object")
    return value


def _require_exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        missing = sorted(keys - set(value))
        unknown = sorted(set(value) - keys)
        raise ContractError(
            "CONTRACT_UNKNOWN_PROPERTY",
            f"{label} keys differ; missing={missing}, unknown={unknown}",
        )


def _parse_identity_inventory(path: Path) -> tuple[dict[str, Any], tuple[JetIdentity, ...]]:
    document = _load_json_object(path, "canonical identity inventory")
    _require_exact_keys(document, {"schema_version", "canonical_dataset", "jets"}, "inventory")
    if document["schema_version"] != "1.0.0":
        raise ContractError("CONTRACT_UNSUPPORTED_MAJOR", "identity inventory requires 1.0.0")
    artifact = document["canonical_dataset"]
    if not isinstance(artifact, dict):
        raise ContractError("CONTRACT_VALUE", "canonical_dataset must be an object")
    _require_exact_keys(artifact, {"path", "sha256", "byte_size"}, "canonical_dataset")
    if (
        not isinstance(artifact["path"], str)
        or not artifact["path"]
        or not isinstance(artifact["sha256"], str)
        or not SHA256_PATTERN.fullmatch(artifact["sha256"])
        or isinstance(artifact["byte_size"], bool)
        or not isinstance(artifact["byte_size"], int)
        or artifact["byte_size"] < 0
    ):
        raise ContractError("CONTRACT_VALUE", "canonical_dataset artifact is invalid")
    raw_jets = document["jets"]
    if not isinstance(raw_jets, list) or not raw_jets:
        raise ContractError("CONTRACT_VALUE", "inventory jets must be a non-empty array")
    jets: list[JetIdentity] = []
    keys = {"record_id", "canonical_pfn", "run", "lumi", "event", "jet_index", "target"}
    for index, raw_jet in enumerate(raw_jets):
        if not isinstance(raw_jet, dict):
            raise ContractError("CONTRACT_VALUE", f"inventory jet {index} must be an object")
        _require_exact_keys(raw_jet, keys, f"inventory jet {index}")
        numeric = ("record_id", "run", "lumi", "event", "jet_index", "target")
        if any(
            isinstance(raw_jet[key], bool) or not isinstance(raw_jet[key], int)
            for key in numeric
        ):
            raise ContractError("CONTRACT_VALUE", f"inventory jet {index} has non-integer values")
        if not isinstance(raw_jet["canonical_pfn"], str) or not raw_jet["canonical_pfn"]:
            raise ContractError("CONTRACT_VALUE", f"inventory jet {index} has invalid PFN")
        if raw_jet["target"] not in (0, 1):
            raise ContractError("CONTRACT_VALUE", f"inventory jet {index} has invalid target")
        jet = JetIdentity(
            record_id=raw_jet["record_id"],
            canonical_pfn=raw_jet["canonical_pfn"],
            run=raw_jet["run"],
            lumi=raw_jet["lumi"],
            event=raw_jet["event"],
            jet_index=raw_jet["jet_index"],
            target=raw_jet["target"],
        )
        _ = jet.jet_id
        jets.append(jet)
    return artifact, tuple(jets)


def _parse_split_config(path: Path) -> dict[str, Any]:
    config = _load_json_object(path, "split configuration")
    _require_exact_keys(
        config,
        {
            "schema_version",
            "manifest_id",
            "study_id",
            "created_at",
            "source_manifest",
            "source_roles",
            "training_subsets",
            "preprocessing",
        },
        "split configuration",
    )
    if config["schema_version"] != "1.0.0":
        raise ConfigurationError("CONFIG_VERSION", "split configuration requires 1.0.0")
    for name in ("manifest_id", "study_id", "created_at"):
        if not isinstance(config[name], str) or not config[name]:
            raise ConfigurationError("CONFIG_VALUE", f"{name} must be a non-empty string")
    source = config["source_manifest"]
    if not isinstance(source, dict):
        raise ConfigurationError("CONFIG_VALUE", "source_manifest must be an object")
    _require_exact_keys(source, {"path", "sha256"}, "source_manifest")
    if (
        not isinstance(source["path"], str)
        or not source["path"]
        or not isinstance(source["sha256"], str)
        or not SHA256_PATTERN.fullmatch(source["sha256"])
    ):
        raise ConfigurationError("CONFIG_VALUE", "source_manifest identity is invalid")
    roles = config["source_roles"]
    allowed_roles = {"signal", "qcd_candidate", "qcd_active", "qcd_excluded_after_e0"}
    if not isinstance(roles, dict) or not roles:
        raise ConfigurationError("CONFIG_VALUE", "source_roles must be a non-empty object")
    if any(not isinstance(key, str) or value not in allowed_roles for key, value in roles.items()):
        raise ConfigurationError("CONFIG_VALUE", "source_roles contains an invalid entry")
    subsets = config["training_subsets"]
    if not isinstance(subsets, list) or not subsets:
        raise ConfigurationError("CONFIG_VALUE", "training_subsets must be non-empty")
    prior_size = 0
    common_seed: int | None = None
    for index, subset in enumerate(subsets):
        if not isinstance(subset, dict):
            raise ConfigurationError("CONFIG_VALUE", f"training subset {index} must be an object")
        _require_exact_keys(
            subset,
            {"subset_id", "train_size_per_class", "subset_seed"},
            f"training subset {index}",
        )
        if (
            not isinstance(subset["subset_id"], str)
            or not subset["subset_id"]
            or isinstance(subset["train_size_per_class"], bool)
            or not isinstance(subset["train_size_per_class"], int)
            or subset["train_size_per_class"] <= prior_size
            or isinstance(subset["subset_seed"], bool)
            or not isinstance(subset["subset_seed"], int)
            or subset["subset_seed"] < 0
        ):
            raise ConfigurationError("CONFIG_VALUE", f"training subset {index} is invalid")
        if common_seed is not None and subset["subset_seed"] != common_seed:
            raise ConfigurationError("CONFIG_VALUE", "all nested subsets must use one seed")
        common_seed = subset["subset_seed"]
        prior_size = subset["train_size_per_class"]
    if not isinstance(config["preprocessing"], dict):
        raise ConfigurationError("CONFIG_VALUE", "preprocessing must be an object")
    return config


def _rank_identity(seed: int, jet_id: str) -> tuple[int, str]:
    digest = hashlib.sha256(f"{seed}\0{jet_id}".encode()).digest()
    return int.from_bytes(digest, "big", signed=False), jet_id


def _select_qcd(jets: list[JetIdentity], size: int, seed: int) -> list[JetIdentity]:
    queues: dict[int, list[JetIdentity]] = {}
    for jet in jets:
        queues.setdefault(jet.record_id, []).append(jet)
    for queue in queues.values():
        queue.sort(key=lambda jet: _rank_identity(seed, jet.jet_id))
    selected: list[JetIdentity] = []
    positions = {record_id: 0 for record_id in queues}
    while len(selected) < size:
        progressed = False
        for record_id in sorted(queues):
            position = positions[record_id]
            if position < len(queues[record_id]):
                selected.append(queues[record_id][position])
                positions[record_id] += 1
                progressed = True
                if len(selected) == size:
                    break
        if not progressed:
            break
    if len(selected) != size:
        raise IntegrityError(
            "SPLIT_INSUFFICIENT_CLASS_YIELD",
            f"QCD selection requires {size} jets but only {len(selected)} are available",
        )
    return selected


def _partition_counts(
    entries: tuple[SourceFile, ...], jets: tuple[JetIdentity, ...]
) -> dict[str, dict[str, object]]:
    output: dict[str, dict[str, object]] = {}
    for split in Split:
        split_jets = [jet for jet in jets if jet.split is split]
        events = {(jet.record_id, jet.run, jet.lumi, jet.event) for jet in split_jets}
        record_counts: dict[str, int] = {}
        for jet in split_jets:
            key = str(jet.record_id)
            record_counts[key] = record_counts.get(key, 0) + 1
        output[split.value] = {
            "file_count": sum(assign_split(entry.canonical_pfn) is split for entry in entries),
            "event_count": len(events),
            "jet_counts_by_class": {
                "qcd": sum(jet.target == 0 for jet in split_jets),
                "top": sum(jet.target == 1 for jet in split_jets),
            },
            "record_jet_counts": record_counts,
        }
    return output


def build_split_manifest(canonical_path: Path, config_path: Path, output_path: Path) -> Path:
    """Build a schema-valid split manifest from a synthetic identity inventory."""

    from particleml.contracts import compute_document_hash, validate_contract_document

    if output_path.exists():
        raise IntegrityError("ARTIFACT_EXISTS", f"formal output already exists: {output_path}")
    artifact, jets = _parse_identity_inventory(canonical_path)
    config = _parse_split_config(config_path)
    source_value = config["source_manifest"]
    source_path = Path(source_value["path"])
    if not source_path.is_absolute():
        source_path = config_path.parent / source_path
    source_manifest = load_source_manifest(source_path)
    source_hash = hash_source_manifest(source_manifest)
    if source_hash != source_value["sha256"]:
        raise IntegrityError("MANIFEST_HASH_MISMATCH", "source manifest hash differs from config")
    roles = config["source_roles"]
    record_ids = {entry.record_id for entry in source_manifest.entries}
    if set(roles) != {str(record_id) for record_id in record_ids}:
        raise ConfigurationError("CONFIG_RECORDS", "source_roles must cover every manifest record")
    entries_by_pfn = {entry.canonical_pfn: entry for entry in source_manifest.entries}
    jet_ids: set[str] = set()
    for jet in jets:
        entry = entries_by_pfn.get(jet.canonical_pfn)
        if entry is None or entry.record_id != jet.record_id:
            raise IntegrityError("SPLIT_SOURCE_IDENTITY", "jet does not match the source manifest")
        expected_target = 1 if roles[str(jet.record_id)] == "signal" else 0
        if jet.target != expected_target:
            raise IntegrityError("SPLIT_TARGET_MISMATCH", f"invalid target for {jet.jet_id}")
        if jet.jet_id in jet_ids:
            raise IntegrityError("SPLIT_IDENTITY_DUPLICATE", f"duplicate jet ID: {jet.jet_id}")
        jet_ids.add(jet.jet_id)
    validate_event_disjointness(
        EventAssignment(jet.record_id, jet.run, jet.lumi, jet.event, jet.split) for jet in jets
    )
    validate_pfn_assignments(
        (entry.canonical_pfn, assign_split(entry.canonical_pfn))
        for entry in source_manifest.entries
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    identity_documents: list[tuple[Path, bytes, dict[str, object]]] = []
    training_subsets: list[dict[str, object]] = []
    train_top = [jet for jet in jets if jet.split is Split.TRAIN and jet.target == 1]
    train_qcd = [
        jet
        for jet in jets
        if jet.split is Split.TRAIN
        and jet.target == 0
        and roles[str(jet.record_id)] == "qcd_active"
    ]
    for subset in config["training_subsets"]:
        size = subset["train_size_per_class"]
        seed = subset["subset_seed"]
        selected_top = sorted(train_top, key=lambda jet: _rank_identity(seed, jet.jet_id))[:size]
        selected_qcd = _select_qcd(train_qcd, size, seed)
        if len(selected_top) != size:
            raise IntegrityError(
                "SPLIT_INSUFFICIENT_CLASS_YIELD",
                f"subset {subset['subset_id']} requires {size} jets per class",
            )
        identity_document = {
            "schema_version": "1.0.0",
            "subset_id": subset["subset_id"],
            "subset_seed": seed,
            "qcd": [jet.jet_id for jet in selected_qcd],
            "top": [jet.jet_id for jet in selected_top],
        }
        identity_bytes = (
            json.dumps(identity_document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        identity_path = output_path.with_name(
            f"{output_path.stem}-{subset['subset_id']}-identities.json"
        )
        if identity_path.exists():
            raise IntegrityError("ARTIFACT_EXISTS", f"identity output exists: {identity_path}")
        identity_record = {
            "path": str(identity_path),
            "sha256": hashlib.sha256(identity_bytes).hexdigest(),
            "byte_size": len(identity_bytes),
        }
        identity_documents.append((identity_path, identity_bytes, identity_record))
        training_subsets.append(
            {
                "subset_id": subset["subset_id"],
                "train_size_per_class": size,
                "subset_seed": seed,
                "selection_rule": "sha256-ranked-signal-and-record-round-robin-qcd-v1",
                "identity_payload": identity_record,
                "counts_by_class": {"qcd": size, "top": size},
            }
        )

    source_files = [
        {
            "record_id": entry.record_id,
            "role": roles[str(entry.record_id)],
            "canonical_pfn": entry.canonical_pfn,
            "pfn_sha256": hash_canonical_pfn(entry.canonical_pfn),
            "adler32": entry.adler32,
            "size_bytes": entry.size_bytes,
            "bucket": split_bucket(entry.canonical_pfn),
            "split": assign_split(entry.canonical_pfn).value,
        }
        for entry in source_manifest.entries
    ]
    document: dict[str, Any] = {
        "schema_version": "1.0.0",
        "manifest_id": config["manifest_id"],
        "study_id": config["study_id"],
        "created_at": config["created_at"],
        "dataset": {
            "name": "CMS 2015 RunIIFall15MiniAODv2",
            "campaign": "RunIIFall15MiniAODv2",
            "source_manifest": {
                "path": str(source_path),
                "sha256": source_hash,
                "byte_size": len(source_manifest.raw_bytes),
            },
            "canonical_dataset": artifact,
            "source_records": [
                {"record_id": record_id, "role": roles[str(record_id)]}
                for record_id in sorted(record_ids)
            ],
        },
        "split_rule": {
            "version": "exact-pfn-sha256-mod10-v1",
            "identifier": "exact_pfn_sha256_mod10",
            "input": "exact canonical_pfn field from the sorted source manifest",
            "encoding": "UTF-8",
            "digest": "SHA-256",
            "integer_byte_order": "big",
            "modulus": 10,
            "buckets": {"test": [0], "validation": [1], "train": list(range(2, 10))},
        },
        "source_files": source_files,
        "partitions": _partition_counts(source_manifest.entries, jets),
        "training_subsets": training_subsets,
        "preprocessing": config["preprocessing"],
        "semantic_checks": {
            "unique_pfns": True,
            "pfn_disjoint": True,
            "event_disjoint": True,
            "subset_identities_unique": True,
            "subsets_nested": True,
            "class_counts_sufficient": True,
        },
        "hash_metadata": {
            "algorithm": "sha256",
            "canonicalization": (
                "utf8-sorted-keys-compact-json-lf-excluding-hash_metadata.content_sha256"
            ),
            "content_sha256": "0" * 64,
        },
    }
    document["hash_metadata"]["content_sha256"] = compute_document_hash(
        document, ("hash_metadata", "content_sha256")
    )
    validate_contract_document(document, "split")
    output_bytes = (
        json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    pending: list[tuple[Path, Path]] = []
    try:
        for final, payload, _record in identity_documents + [(output_path, output_bytes, {})]:
            partial = final.with_name(f"{final.name}.partial.{uuid.uuid4()}")
            partial.write_bytes(payload)
            pending.append((partial, final))
        # Every partial is created beside its final path, enforcing the confirmed
        # same-filesystem publication boundary. Concurrent publishers are out of scope.
        for partial, final in pending:
            partial.rename(final)
    finally:
        for partial, _final in pending:
            if partial.exists():
                partial.unlink()
    return output_path
