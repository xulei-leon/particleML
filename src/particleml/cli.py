"""Thin command-line entry point for particleML."""

from __future__ import annotations

import argparse
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
from particleml.manifest import build_split_manifest, hash_source_manifest, load_source_manifest
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
