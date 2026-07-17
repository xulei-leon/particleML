"""Thin command-line entry point for particleML."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import NoReturn


def build_parser() -> argparse.ArgumentParser:
    """Build the bootstrap parser without registering scientific commands."""

    return argparse.ArgumentParser(
        prog="particleml",
        description="Bootstrap CLI for cloud-verified jet-physics workflows.",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Parse bootstrap arguments and display help until command groups land."""

    parser = build_parser()
    parser.parse_args(list(argv) if argv is not None else None)
    parser.print_help()
    return 0


def entrypoint() -> NoReturn:
    """Translate the reusable return code into a process exit status."""

    raise SystemExit(main())
