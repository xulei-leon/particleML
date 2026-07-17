from __future__ import annotations

from pathlib import Path

import pytest

# M1-01 deliberately treats the repository documentation validator as the
# executable boundary for authoritative software-contract regression tests.
from scripts.validate_software_docs import REQUIRED_VIEW_MARKERS, ROOT, view_contract_errors

SOFTWARE_DOCS = (
    Path("docs/software/architecture.md"),
    Path("docs/software/specification.md"),
    Path("docs/software/traceability-matrix.md"),
)


def _document_text() -> dict[str, str]:
    return {
        path.as_posix(): (ROOT / path).read_text(encoding="utf-8")
        for path in SOFTWARE_DOCS
    }


def test_native_integer_pid_contract_is_consistent() -> None:
    assert view_contract_errors(_document_text()) == []


def test_obsolete_one_hot_contract_is_rejected() -> None:
    documents = _document_text()
    specification = SOFTWARE_DOCS[1].as_posix()
    documents[specification] += "\nView dimensions after one-hot PID expansion are:\n"

    errors = view_contract_errors(documents)

    assert any("obsolete one-hot PID view contract" in error for error in errors)


@pytest.mark.parametrize(
    ("document_path", "label", "marker"),
    [
        (document_path, label, marker)
        for document_path, markers in REQUIRED_VIEW_MARKERS.items()
        for label, marker in markers
    ],
)
def test_missing_required_native_pid_marker_is_rejected(
    document_path: str,
    label: str,
    marker: str,
) -> None:
    documents = _document_text()
    documents[document_path] = documents[document_path].replace(marker, "")

    errors = view_contract_errors(documents)

    assert any(label in error for error in errors)
