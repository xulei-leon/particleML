from __future__ import annotations

from importlib.metadata import entry_points

import pytest

import particleml
from particleml.cli import main


def test_package_exposes_version() -> None:
    assert particleml.__version__ == "0.1.0"


def test_cli_help_is_available(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert "particleml" in output
    assert "cloud-verified jet-physics workflows" in output


def test_cli_without_arguments_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage: particleml" in capsys.readouterr().out


def test_console_script_targets_thin_entrypoint() -> None:
    matches = [
        entry_point
        for entry_point in entry_points(group="console_scripts")
        if entry_point.name == "particleml"
    ]
    assert len(matches) == 1
    assert matches[0].value == "particleml.cli:entrypoint"
