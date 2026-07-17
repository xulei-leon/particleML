"""Validate the particleML software documentation suite.

This check verifies repository-local links, version and terminology consistency,
requirements traceability, JSON Schema correctness, and representative schema
instances. It does not verify E0-E3 implementation or scientific results.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import unquote

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "jsonschema is required; install requirements-ci.lock or the docs-only "
        "requirements-docs.txt before running this check"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_SUITE_VERSION = "1.1.0"
SCHEMA_VERSION = "1.0.0"
RESEARCH_VERSION = "Research Plan v0.4.0"

DOCS = (
    ROOT / "docs/software/requirements.md",
    ROOT / "docs/software/architecture.md",
    ROOT / "docs/software/specification.md",
    ROOT / "docs/software/traceability-matrix.md",
)
LINK_DOCUMENTS = DOCS + (
    ROOT / "docs/index.md",
    ROOT / "docs/engineering/particleml-architecture.md",
    ROOT / "README.md",
    ROOT / "project/superpowers/specs/2026-07-16-particleml-software-documentation-suite-design.md",
)
SCHEMAS = {
    "run": ROOT / "schemas/run-record.schema.json",
    "split": ROOT / "schemas/split-manifest.schema.json",
    "prediction": ROOT / "schemas/prediction.schema.json",
    "e0_audit": ROOT / "schemas/e0-audit.schema.json",
    "e05_audit": ROOT / "schemas/e05-audit.schema.json",
}

OBSOLETE_VIEW_PATTERNS = (
    r"view dimensions after one-hot PID expansion",
    r"six PID one-hot channels",
    r"converted to the frozen one-hot representation",
    r"unknown PID bit",
)

REQUIRED_VIEW_MARKERS = {
    "docs/software/architecture.md": (
        (
            "C native integer-PID dimension and order",
            "| C | 6 | A + `pid_type` at index 4 + `charge` |",
        ),
        (
            "D OmniLearned flags",
            "`--use-pid --pid_idx 4 --use-add --num-add 5`",
        ),
    ),
    "docs/software/specification.md": (
        (
            "C native integer-PID dimension and order",
            "| C | 6 | A + `pid_type` at index 4 + `charge` |",
        ),
        (
            "D native integer-PID dimension",
            "| D | 10 | C + `dxy_raw`, `dxy_error_raw`, `dz_raw`, `dz_error_raw` |",
        ),
        (
            "C OmniLearned flags",
            "`--use-pid --pid_idx 4 --use-add --num-add 1`",
        ),
        (
            "D OmniLearned flags",
            "`--use-pid --pid_idx 4 --use-add --num-add 5`",
        ),
    ),
    "docs/software/traceability-matrix.md": (
        (
            "FR-DATA-005 native integer-PID regression mapping",
            "native integer-PID/obsolete-contract regression",
        ),
        (
            "FR-MODEL-003 exact argv mapping",
            "exact A-D native PID/additional-feature argv snapshots",
        ),
    ),
}


def view_contract_errors(documents: Mapping[str, str]) -> list[str]:
    """Return native integer-PID contract errors for software documents."""

    errors: list[str] = []
    normalized = {path.replace("\\", "/"): text for path, text in documents.items()}

    for path, text in normalized.items():
        for pattern in OBSOLETE_VIEW_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                errors.append(
                    f"{path}: obsolete one-hot PID view contract: {match.group(0)!r}"
                )

    for path, markers in REQUIRED_VIEW_MARKERS.items():
        text = normalized.get(path)
        if text is None:
            errors.append(f"{path}: missing from native integer-PID contract validation")
            continue
        for label, marker in markers:
            if marker not in text:
                errors.append(f"{path}: missing {label}: {marker!r}")

    return errors

HASH = "a" * 64
OTHER_HASH = "b" * 64
COMMIT = "c" * 40
TIMESTAMP = "2026-07-16T00:00:00Z"


def artifact(path: str, digest: str = HASH, byte_size: int = 1) -> dict[str, object]:
    return {"path": path, "sha256": digest, "byte_size": byte_size}


def sample_run() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": "e1-deepsets-a-n1000-s1",
        "study_id": "cms2015-feature-availability-v04",
        "stage": "E1",
        "status": "succeeded",
        "created_at": TIMESTAMP,
        "started_at": TIMESTAMP,
        "ended_at": "2026-07-16T00:01:00Z",
        "git": {
            "repository": "https://github.com/xulei-leon/particleML",
            "commit": COMMIT,
            "dirty": False,
        },
        "data": {
            "dataset_name": "CMS 2015 RunIIFall15MiniAODv2",
            "source_manifest_sha256": HASH,
            "canonical_dataset": artifact("canonical/canonical-full-d.h5"),
            "split_manifest": artifact("manifests/split-manifest.json"),
            "preprocessing": artifact("manifests/preprocessing.json"),
            "view": artifact("views/n1000/A/view.h5"),
            "qcd_mixture_sha256": OTHER_HASH,
        },
        "condition": {
            "feature_config": "A",
            "train_size_per_class": 1000,
            "subset_id": "n1000",
            "subset_seed": 20260714,
            "model_seed": 1,
        },
        "model": {
            "family": "deep_sets_pfn",
            "repository": "particleML",
            "revision": COMMIT,
            "adapter_policy": "native_baseline",
            "output_head": "binary_top_qcd",
            "checkpoint": None,
            "omnilearned_index": None,
            "loaded_tensors": [],
            "skipped_tensors": [],
            "mismatched_tensors": [],
        },
        "hyperparameters": {
            "optimizer": "adamw",
            "learning_rate": 0.001,
            "batch_size": 128,
            "max_epochs": 2,
            "weight_decay": 0.0001,
            "early_stopping": {
                "monitor": "validation_auc",
                "mode": "max",
                "patience": 1,
                "min_delta": 0.0,
            },
            "extra": {},
        },
        "environment": {
            "python_version": "3.10.0",
            "dependency_lock_sha256": HASH,
            "operating_system": "Linux",
            "device": {"type": "cpu", "name": "fixture"},
            "deterministic_algorithms": True,
            "known_nondeterminism": [],
        },
        "timing": {"wall_seconds": 60.0, "peak_gpu_memory_mib": None},
        "metrics": {
            "best_epoch": 1,
            "validation_auc": 0.7,
            "test_auc": 0.7,
            "test_accuracy": 0.65,
            "epsilon_b_at_epsilon_s_0_30": 0.1,
            "epsilon_b_at_epsilon_s_0_50": 0.2,
            "background_rejection_at_epsilon_s_0_30": 10.0,
            "background_rejection_at_epsilon_s_0_50": 5.0,
            "validation_threshold": 0.5,
            "test_background_count": 100,
        },
        "artifacts": {
            "run_directory": "runs/e1-deepsets-a-n1000-s1",
            "resolved_config": artifact("runs/e1-deepsets-a-n1000-s1/resolved-config.yaml"),
            "stdout_log": artifact("runs/e1-deepsets-a-n1000-s1/stdout.log"),
            "stderr_log": artifact("runs/e1-deepsets-a-n1000-s1/stderr.log"),
            "model_checkpoint": artifact("runs/e1-deepsets-a-n1000-s1/model.pt"),
            "prediction_metadata": artifact("predictions/e1-deepsets-a-n1000-s1/prediction.json"),
        },
        "failure": None,
    }


def sample_split() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": "cms2015-split-v1",
        "study_id": "cms2015-feature-availability-v04",
        "created_at": TIMESTAMP,
        "dataset": {
            "name": "CMS 2015 RunIIFall15MiniAODv2",
            "campaign": "RunIIFall15MiniAODv2",
            "source_manifest": artifact("manifests/source-manifest.tsv"),
            "canonical_dataset": artifact("canonical/canonical-full-d.h5"),
            "source_records": [
                {"record_id": 19980, "role": "signal"},
                {"record_id": 18373, "role": "qcd_active"},
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
            "buckets": {
                "test": [0],
                "validation": [1],
                "train": [2, 3, 4, 5, 6, 7, 8, 9],
            },
        },
        "source_files": [
            {
                "record_id": 19980,
                "role": "signal",
                "canonical_pfn": "root://example/signal.root",
                "pfn_sha256": HASH,
                "adler32": "1234abcd",
                "size_bytes": 100,
                "bucket": 2,
                "split": "train",
            },
            {
                "record_id": 18373,
                "role": "qcd_active",
                "canonical_pfn": "root://example/qcd.root",
                "pfn_sha256": OTHER_HASH,
                "adler32": "5678abcd",
                "size_bytes": 100,
                "bucket": 0,
                "split": "test",
            },
        ],
        "partitions": {
            "train": {
                "file_count": 1,
                "event_count": 2,
                "jet_counts_by_class": {"qcd": 1, "top": 1},
                "record_jet_counts": {"19980": 1, "18373": 1},
            },
            "validation": {
                "file_count": 0,
                "event_count": 0,
                "jet_counts_by_class": {"qcd": 0, "top": 0},
                "record_jet_counts": {},
            },
            "test": {
                "file_count": 1,
                "event_count": 2,
                "jet_counts_by_class": {"qcd": 1, "top": 1},
                "record_jet_counts": {"19980": 1, "18373": 1},
            },
        },
        "training_subsets": [
            {
                "subset_id": "n1000",
                "train_size_per_class": 1000,
                "subset_seed": 20260714,
                "selection_rule": "sha256-ranked-signal-and-record-round-robin-qcd-v1",
                "identity_payload": artifact("manifests/subsets/n1000.txt"),
                "counts_by_class": {"qcd": 1000, "top": 1000},
            }
        ],
        "preprocessing": {
            "feature_version": "cms-ad-v1",
            "policy": artifact("manifests/preprocessing.json"),
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
            "pt_eta_control_sha256": HASH,
            "pileup_reweighting_sha256": None,
        },
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
                "utf8-sorted-keys-compact-json-lf-excluding-"
                "hash_metadata.content_sha256"
            ),
            "content_sha256": HASH,
        },
    }


def column(name: str, dtype: str, **extra: object) -> dict[str, object]:
    return {"name": name, "dtype": dtype, "nullable": False, **extra}


def sample_prediction() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "prediction_id": "pred-e1-deepsets-a-n1000-s1",
        "run_id": "e1-deepsets-a-n1000-s1",
        "created_at": TIMESTAMP,
        "partition": "test",
        "feature_config": "A",
        "model_condition": "deep_sets_pfn",
        "split_manifest_sha256": HASH,
        "view_sha256": OTHER_HASH,
        "ordered": True,
        "row_count": 2,
        "class_counts": {"qcd": 1, "top": 1},
        "row_order_sha256": HASH,
        "logical_columns": {
            "jet_id": column("jet_id", "utf8"),
            "record_id": column("record_id", "uint32"),
            "run": column("run", "uint32"),
            "lumi": column("lumi", "uint32"),
            "event": column("event", "uint64"),
            "jet_index": column("jet_index", "uint16"),
            "target": column("target", "int8", allowed_values=[0, 1]),
            "signal_score": column("signal_score", "float32", range=[0, 1]),
        },
        "payload": {
            "format": "npz",
            "path": "predictions/e1-deepsets-a-n1000-s1/payload.npz",
            "sha256": HASH,
            "byte_size": 100,
            "compression": "zip",
        },
        "content_hash": {
            "algorithm": "sha256",
            "canonicalization": (
                "utf8-sorted-keys-compact-json-lf-excluding-"
                "content_hash.metadata_sha256"
            ),
            "metadata_sha256": HASH,
        },
    }


def sample_e05_audit() -> dict[str, object]:
    document: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "e05_audit_id": "e05-local-software-fixture",
        "status": "blocked_external_evidence",
        "formal_gate_eligible": False,
        "evidence_origin": "local_fixture",
        "dependency_revision": "5091595d226b6021e967ab2ecfff832f40c026f6",
        "missing_evidence": [],
        "failed_checks": [],
        "model_condition": "pretrained_omnilearned",
        "policy_sha256": HASH,
    }
    payload = json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    document["content_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    return document


def markdown_link_errors(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        raw_target = match.group(1).strip()
        target = raw_target.split(maxsplit=1)[0].strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target.split("#", 1)[0])
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: missing link target {raw_target}")
    return errors


def expect_valid(
    validator: Draft202012Validator,
    instance: dict[str, object],
    name: str,
    errors: list[str],
) -> None:
    found = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    for error in found:
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{name} sample at {location}: {error.message}")


def expect_invalid(
    validator: Draft202012Validator,
    instance: dict[str, object],
    name: str,
    errors: list[str],
) -> None:
    if validator.is_valid(instance):
        errors.append(f"negative schema fixture unexpectedly passed: {name}")


def main() -> int:
    errors: list[str] = []

    for path in DOCS + tuple(SCHEMAS.values()):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"required deliverable missing or empty: {path.relative_to(ROOT)}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    document_text = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8") for path in DOCS
    }
    canonical_text = "\n".join(document_text.values())
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        if f"Software documentation suite | {DOCUMENT_SUITE_VERSION}" not in text:
            errors.append(
                f"{path.relative_to(ROOT)}: missing suite version {DOCUMENT_SUITE_VERSION}"
            )
        if RESEARCH_VERSION not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing research baseline {RESEARCH_VERSION}")
        if "CMS 2015" not in text:
            errors.append(f"{path.relative_to(ROOT)}: missing canonical dataset term CMS 2015")

    forbidden = {
        r"Research Plan v0\.3": "stale research-plan version",
        r"docs/plan/": "stale research-plan path",
        r"(?i)\b(?:TBD|TODO|FIXME|REPLACE_ME)\b|<fill-me>": "unresolved placeholder marker",
        r"(?i)primary dataset[^\n]*JetClass": "stale primary-dataset statement",
    }
    for pattern, reason in forbidden.items():
        match = re.search(pattern, canonical_text)
        if match:
            errors.append(f"canonical documentation contains {reason}: {match.group(0)!r}")

    errors.extend(view_contract_errors(document_text))

    for path in LINK_DOCUMENTS:
        if not path.exists():
            errors.append(f"link-bearing document missing: {path.relative_to(ROOT)}")
            continue
        errors.extend(markdown_link_errors(path))

    loaded_schemas: dict[str, dict[str, object]] = {}
    validators: dict[str, Draft202012Validator] = {}
    expected_ids = {
        "run": "https://xulei-leon.github.io/particleML/schemas/run-record.schema.json",
        "split": "https://xulei-leon.github.io/particleML/schemas/split-manifest.schema.json",
        "prediction": "https://xulei-leon.github.io/particleML/schemas/prediction.schema.json",
        "e0_audit": "https://xulei-leon.github.io/particleML/schemas/e0-audit.schema.json",
        "e05_audit": "https://xulei-leon.github.io/particleML/schemas/e05-audit.schema.json",
    }
    for name, path in SCHEMAS.items():
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
            continue
        loaded_schemas[name] = schema
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path.relative_to(ROOT)}: wrong JSON Schema dialect")
        if schema.get("$id") != expected_ids[name]:
            errors.append(f"{path.relative_to(ROOT)}: unexpected $id")
        if schema.get("additionalProperties") is not False:
            errors.append(
                f"{path.relative_to(ROOT)}: top-level unknown properties are not rejected"
            )
        version = schema.get("properties", {}).get("schema_version", {}).get("const")
        if version != SCHEMA_VERSION:
            errors.append(f"{path.relative_to(ROOT)}: schema_version is not {SCHEMA_VERSION}")
        remote_refs = [
            value
            for value in re.findall(r'"\$ref"\s*:\s*"([^"]+)"', path.read_text(encoding="utf-8"))
            if not value.startswith("#/")
        ]
        if remote_refs:
            errors.append(
                f"{path.relative_to(ROOT)}: unresolved/non-local $ref values {remote_refs}"
            )
        try:
            Draft202012Validator.check_schema(schema)
            validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        except SchemaError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid Draft 2020-12 schema: {exc.message}")

    if set(validators) == set(SCHEMAS):
        run = sample_run()
        expect_valid(validators["run"], run, "successful run", errors)
        failed_run = copy.deepcopy(run)
        failed_run["status"] = "failed"
        failed_run.pop("metrics")
        failed_run["artifacts"]["model_checkpoint"] = None
        failed_run["artifacts"]["prediction_metadata"] = None
        failed_run["failure"] = {
            "code": "RUN_TRAINING_FAILED",
            "phase": "train",
            "message": "fixture failure",
        }
        expect_valid(validators["run"], failed_run, "failed run", errors)
        missing_metrics = copy.deepcopy(run)
        missing_metrics.pop("metrics")
        expect_invalid(validators["run"], missing_metrics, "successful run without metrics", errors)
        extra_run_field = copy.deepcopy(run)
        extra_run_field["unexpected"] = True
        expect_invalid(validators["run"], extra_run_field, "run with unknown field", errors)

        split = sample_split()
        expect_valid(validators["split"], split, "split manifest", errors)
        invalid_split = copy.deepcopy(split)
        invalid_split["semantic_checks"]["event_disjoint"] = False
        expect_invalid(validators["split"], invalid_split, "overlapping split declaration", errors)

        prediction = sample_prediction()
        expect_valid(validators["prediction"], prediction, "prediction metadata", errors)
        unordered = copy.deepcopy(prediction)
        unordered["ordered"] = False
        expect_invalid(validators["prediction"], unordered, "unordered prediction", errors)

        expect_valid(validators["e05_audit"], sample_e05_audit(), "E0.5 audit", errors)

    requirements_text = DOCS[0].read_text(encoding="utf-8")
    matrix_text = DOCS[3].read_text(encoding="utf-8")
    requirement_ids = set(
        re.findall(r"^### ((?:FR|NFR|AC)-[A-Z0-9]+-\d{3})\b", requirements_text, re.MULTILINE)
    )
    matrix_ids = re.findall(
        r"^\| ((?:FR|NFR|AC)-[A-Z0-9]+-\d{3}) \|", matrix_text, re.MULTILINE
    )
    if requirement_ids != set(matrix_ids):
        errors.append(
            "traceability mismatch: "
            f"missing={sorted(requirement_ids - set(matrix_ids))}, "
            f"extra={sorted(set(matrix_ids) - requirement_ids)}"
        )
    duplicates = sorted({item for item in matrix_ids if matrix_ids.count(item) > 1})
    if duplicates:
        errors.append(f"traceability matrix repeats requirement rows: {duplicates}")

    specification = DOCS[2].read_text(encoding="utf-8")
    for schema_path in SCHEMAS.values():
        repository_path = schema_path.relative_to(ROOT).as_posix()
        if repository_path not in specification:
            errors.append(f"specification does not name {repository_path}")

    if errors:
        print("Software documentation validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Software documentation validation passed: "
        f"{len(DOCS)} documents, {len(SCHEMAS)} schemas, "
        f"{len(requirement_ids)} traced requirements, {len(LINK_DOCUMENTS)} link-bearing files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
