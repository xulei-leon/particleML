"""Thin command-line entry point for particleML."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from particleml.audit import build_data_audit
from particleml.contracts import (
    ConfigurationError,
    FeatureConfig,
    ParticleMLError,
    validate_contract,
)
from particleml.dataset import convert_compact_root
from particleml.e0 import build_e0_audit
from particleml.experiment import dry_run_ledger, resolve_matrix
from particleml.manifest import build_split_manifest, hash_source_manifest, load_source_manifest
from particleml.metrics import evaluate_binary_predictions, validate_prediction_payload
from particleml.model_integration import aggregate_e05, build_index_argv, validate_checkpoint
from particleml.reporting import build_report
from particleml.views import materialize_view


class _Parser(argparse.ArgumentParser):
    """Argument parser that keeps syntax errors inside the reusable CLI boundary."""

    def error(self, message: str) -> NoReturn:
        raise ConfigurationError("CLI_USAGE", message)


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic-core command tree."""

    parser = _Parser(
        prog="particleml",
        description="Bootstrap CLI for cloud-verified jet-physics workflows.",
    )
    groups = parser.add_subparsers(dest="group")

    manifest = groups.add_parser("manifest", help="source-manifest operations")
    manifest_commands = manifest.add_subparsers(dest="command", required=True)
    manifest_validate = manifest_commands.add_parser("validate", help="validate exact bytes")
    manifest_validate.add_argument("--source", required=True, type=Path)

    contracts = groups.add_parser("contracts", help="serialized-contract operations")
    contract_commands = contracts.add_subparsers(dest="command", required=True)
    contracts_validate = contract_commands.add_parser("validate", help="validate a JSON contract")
    contracts_validate.add_argument("--path", required=True, type=Path)

    split = groups.add_parser("split", help="deterministic split operations")
    split_commands = split.add_subparsers(dest="command", required=True)
    split_build = split_commands.add_parser("build", help="build a split manifest")
    split_build.add_argument("--canonical", required=True, type=Path)
    split_build.add_argument("--config", required=True, type=Path)
    split_build.add_argument("--output", required=True, type=Path)

    convert = groups.add_parser("convert", help="convert compact ROOT to canonical HDF5")
    convert.add_argument("--input", required=True, action="append", type=Path)
    convert.add_argument("--source-manifest", required=True, type=Path)
    convert.add_argument("--policy", required=True, type=Path)
    convert.add_argument("--output", required=True, type=Path)

    audit = groups.add_parser("audit", help="data-audit operations")
    audit_commands = audit.add_subparsers(dest="command", required=True)
    audit_data = audit_commands.add_parser("data", help="run the retained data audit")
    audit_data.add_argument("--canonical", required=True, type=Path)
    audit_data.add_argument("--field", action="append", default=[])
    audit_data.add_argument("--policy", required=True, type=Path)
    audit_data.add_argument("--output", required=True, type=Path)
    audit_e0 = audit_commands.add_parser("e0", help="aggregate the cross-artifact E0 gate")
    audit_e0.add_argument("--evidence", required=True, type=Path)
    audit_e0.add_argument("--policy", required=True, type=Path)
    audit_e0.add_argument("--output", required=True, type=Path)
    audit_e05 = audit_commands.add_parser("e05", help="aggregate the E0.5 model gate")
    audit_e05.add_argument("--evidence", required=True, type=Path)
    audit_e05.add_argument("--policy", required=True, type=Path)
    audit_e05.add_argument("--output", required=True, type=Path)

    index = groups.add_parser("index", help="OmniLearned custom-index operations")
    index_commands = index.add_subparsers(dest="command", required=True)
    index_build = index_commands.add_parser("build", help="resolve an official index command")
    index_build.add_argument("--executable", required=True, type=Path)
    index_build.add_argument("--view", required=True, type=Path)
    index_build.add_argument("--output", required=True, type=Path)
    index_build.add_argument(
        "--feature-config", required=True, choices=[item.value for item in FeatureConfig]
    )

    checkpoint = groups.add_parser("checkpoint", help="checkpoint integrity operations")
    checkpoint_commands = checkpoint.add_subparsers(dest="command", required=True)
    checkpoint_audit = checkpoint_commands.add_parser("audit", help="audit checkpoint provenance")
    checkpoint_audit.add_argument("--checkpoint", required=True, type=Path)
    checkpoint_audit.add_argument("--metadata", required=True, type=Path)

    run = groups.add_parser("run", help="stage-gated experiment operations")
    run_commands = run.add_subparsers(dest="command", required=True)
    run_train = run_commands.add_parser("train", help="resolve a frozen training matrix")
    run_train.add_argument("--config", required=True, type=Path)
    run_train.add_argument("--gates", required=True, type=Path)
    run_train.add_argument("--dry-run", action="store_true")

    evaluate = groups.add_parser("evaluate", help="evaluate aligned predictions")
    evaluate.add_argument("--metadata", required=True, type=Path)
    evaluate.add_argument("--payload", required=True, type=Path)
    evaluate.add_argument("--validation-threshold", required=True, type=float)

    report = groups.add_parser("report", help="evidence-derived report operations")
    report_commands = report.add_subparsers(dest="command", required=True)
    report_build = report_commands.add_parser("build", help="build a deterministic report")
    report_build.add_argument("--config", required=True, type=Path)
    report_build.add_argument("--run-record", action="append", default=[], type=Path)
    report_build.add_argument("--output", required=True, type=Path)

    view = groups.add_parser("view", help="model-view operations")
    view_commands = view.add_subparsers(dest="command", required=True)
    view_build = view_commands.add_parser("build", help="materialize one A-D view")
    view_build.add_argument("--canonical", required=True, type=Path)
    view_build.add_argument("--preprocessing", required=True, type=Path)
    view_build.add_argument("--identities", required=True, type=Path)
    view_build.add_argument("--split-manifest-sha256", required=True)
    view_build.add_argument("--split-manifest", type=Path)
    view_build.add_argument("--subset-sha256")
    view_build.add_argument("--allow-unpublished-diagnostics", action="store_true")
    view_build.add_argument(
        "--feature-config", required=True, choices=[item.value for item in FeatureConfig]
    )
    view_build.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command and map typed project exceptions to stable exit codes."""

    parser = build_parser()
    try:
        arguments = parser.parse_args(list(argv) if argv is not None else None)
        if arguments.group is None:
            parser.print_help()
            return 0
        if arguments.group == "manifest" and arguments.command == "validate":
            print(hash_source_manifest(load_source_manifest(arguments.source)))
            return 0
        if arguments.group == "contracts" and arguments.command == "validate":
            kind = validate_contract(arguments.path)
            print(f"valid {kind} contract")
            return 0
        if arguments.group == "split" and arguments.command == "build":
            output = build_split_manifest(arguments.canonical, arguments.config, arguments.output)
            print(f"valid split manifest: {output}")
            return 0
        if arguments.group == "convert":
            output = convert_compact_root(
                arguments.input,
                arguments.source_manifest,
                arguments.policy,
                arguments.output,
            )
            print(f"valid canonical dataset: {output}")
            return 0
        if arguments.group == "audit" and arguments.command == "data":
            report = build_data_audit(
                arguments.canonical,
                arguments.field,
                arguments.policy,
                arguments.output,
            )
            print(f"data audit {report['status']}: {arguments.output}")
            return 0
        if arguments.group == "audit" and arguments.command == "e0":
            report = build_e0_audit(arguments.evidence, arguments.policy, arguments.output)
            print(f"E0 audit {report['status']}: {arguments.output}")
            return 0
        if arguments.group == "audit" and arguments.command == "e05":
            report = aggregate_e05(arguments.evidence, arguments.policy, arguments.output)
            print(f"E0.5 audit {report['status']}: {arguments.output}")
            return 0
        if arguments.group == "index" and arguments.command == "build":
            resolved = build_index_argv(
                arguments.executable,
                arguments.view,
                arguments.output,
                FeatureConfig(arguments.feature_config),
            )
            print(json.dumps(list(resolved), separators=(",", ":")))
            return 0
        if arguments.group == "checkpoint" and arguments.command == "audit":
            metadata = validate_checkpoint(arguments.checkpoint, arguments.metadata)
            print(f"valid checkpoint: {metadata['sha256']}")
            return 0
        if arguments.group == "run" and arguments.command == "train":
            try:
                gates = json.loads(arguments.gates.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ConfigurationError("RUN_GATES_INVALID", "cannot load gate records") from exc
            if not isinstance(gates, dict):
                raise ConfigurationError("RUN_GATES_INVALID", "gate records must be an object")
            if arguments.dry_run:
                print(json.dumps(dry_run_ledger(arguments.config, gates), sort_keys=True))
                return 0
            specs = resolve_matrix(arguments.config, gates)
            raise ConfigurationError(
                "RUN_EXECUTION_EXPLICIT_COMMAND_REQUIRED",
                f"resolved {len(specs)} conditions; execution must use retained commands",
            )
        if arguments.group == "evaluate":
            predictions = validate_prediction_payload(arguments.metadata, arguments.payload)
            metrics = evaluate_binary_predictions(
                predictions, validation_threshold=arguments.validation_threshold
            )
            print(json.dumps(metrics, sort_keys=True, separators=(",", ":")))
            return 0
        if arguments.group == "report" and arguments.command == "build":
            output = build_report(arguments.config, arguments.run_record, arguments.output)
            print(f"valid evidence-derived report: {output}")
            return 0
        if arguments.group == "view" and arguments.command == "build":
            output = materialize_view(
                arguments.canonical,
                arguments.preprocessing,
                arguments.identities,
                arguments.split_manifest_sha256,
                FeatureConfig(arguments.feature_config),
                arguments.output,
                expected_subset_sha256=arguments.subset_sha256,
                split_manifest_path=arguments.split_manifest,
                require_completed_dependencies=not arguments.allow_unpublished_diagnostics,
            )
            print(f"valid {arguments.feature_config} view: {output}")
            return 0
        raise ConfigurationError("CLI_USAGE", "unsupported command")
    except ParticleMLError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code


def entrypoint() -> NoReturn:
    """Translate the reusable return code into a process exit status."""

    raise SystemExit(main())
