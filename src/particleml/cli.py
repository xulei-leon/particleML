"""Thin command-line entry point for particleML."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from particleml.contracts import ConfigurationError, ParticleMLError, validate_contract
from particleml.manifest import build_split_manifest, hash_source_manifest, load_source_manifest


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
        raise ConfigurationError("CLI_USAGE", "unsupported command")
    except ParticleMLError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code


def entrypoint() -> NoReturn:
    """Translate the reusable return code into a process exit status."""

    raise SystemExit(main())
