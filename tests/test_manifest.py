from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from particleml.contracts import IntegrityError, Split
from particleml.manifest import (
    EventAssignment,
    assign_split,
    hash_canonical_pfn,
    hash_source_manifest,
    load_source_manifest,
    split_bucket,
    stable_jet_id,
    validate_event_disjointness,
    validate_pfn_assignments,
)

CANONICAL_BYTES = (
    b"18355\troot://example.invalid//qcd.root\t00abcdef\t10\n"
    b"19980\troot://example.invalid//top.root\t1234abcd\t20\n"
)


def _write(path: Path, payload: bytes) -> Path:
    path.write_bytes(payload)
    return path


def test_canonical_manifest_bytes_and_hash(tmp_path: Path) -> None:
    path = _write(tmp_path / "source.tsv", CANONICAL_BYTES)

    manifest = load_source_manifest(path)

    assert [entry.record_id for entry in manifest.entries] == [18355, 19980]
    assert manifest.raw_bytes == CANONICAL_BYTES
    assert hash_source_manifest(manifest) == hashlib.sha256(CANONICAL_BYTES).hexdigest()
    assert path.read_bytes() == CANONICAL_BYTES


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"\xef\xbb\xbf" + CANONICAL_BYTES, "MANIFEST_BOM"),
        (CANONICAL_BYTES.replace(b"\n", b"\r\n"), "MANIFEST_LINE_ENDING"),
        (CANONICAL_BYTES.rstrip(b"\n"), "MANIFEST_LINE_ENDING"),
        (
            b"19980\troot://example.invalid//top.root\t1234abcd\t20\n"
            b"18355\troot://example.invalid//qcd.root\t00abcdef\t10\n",
            "MANIFEST_ORDER",
        ),
        (
            b"18355\troot://example.invalid//qcd.root\t00abcdef\t10\n"
            b"19980\troot://example.invalid//qcd.root\t1234abcd\t20\n",
            "MANIFEST_DUPLICATE_PFN",
        ),
        (b"18355\t\t00abcdef\t10\n", "MANIFEST_EMPTY_FIELD"),
        (b"18355\troot://example.invalid//qcd.root\tbad\t10\n", "MANIFEST_CHECKSUM"),
        (b"18355\troot://example.invalid//qcd.root\t00abcdef\t0\n", "MANIFEST_SIZE"),
    ],
)
def test_invalid_manifest_bytes_fail_closed(tmp_path: Path, payload: bytes, code: str) -> None:
    with pytest.raises(IntegrityError, match=code):
        load_source_manifest(_write(tmp_path / "source.tsv", payload))


def test_exact_pfn_split_golden_vectors() -> None:
    vectors = [
        (
            "root://example.invalid//store/test/file-7.root",
            "86a2d2ef501197c748e1c536b523b3b0e491d74dd9e24bddf79577888bbd529a",
            0,
            Split.TEST,
        ),
        (
            "root://example.invalid//store/test/file-0.root",
            "037bba1c0c146b75f5dea5c3abf38bb287aa9b8ea0d9c96b9885b88adcdbc3b3",
            1,
            Split.VALIDATION,
        ),
        (
            "root://例子.invalid//cms/μ-jet.root",
            "71ac8c0965d5841033850debf7bc8bd8c06b825bdfe4928f74d4c12379ff7d61",
            7,
            Split.TRAIN,
        ),
    ]

    for pfn, expected_hash, expected_bucket, expected_split in vectors:
        assert hash_canonical_pfn(pfn) == expected_hash
        assert split_bucket(pfn) == expected_bucket
        assert assign_split(pfn) is expected_split


def test_pfn_text_is_not_normalized() -> None:
    original = "root://example.invalid//Store/File.root"
    variants = [original.lower(), original + " ", original.replace("root://", "ROOT://")]

    assert all(hash_canonical_pfn(value) != hash_canonical_pfn(original) for value in variants)


def test_stable_jet_identity_uses_full_exact_pfn_digest() -> None:
    pfn = "root://example.invalid//store/test/file-7.root"

    assert stable_jet_id(19980, pfn, 1, 2, 3, 0) == (
        "cms:19980:86a2d2ef501197c748e1c536b523b3b0e491d74dd9e24bddf79577888bbd529a:"
        "1:2:3:0"
    )


@pytest.mark.parametrize("field", ["record_id", "run", "lumi", "event"])
def test_stable_jet_identity_requires_positive_cms_coordinates(field: str) -> None:
    values = {"record_id": 1, "run": 1, "lumi": 1, "event": 1, "jet_index": 0}
    values[field] = 0

    with pytest.raises(IntegrityError, match="SPLIT_IDENTITY_VALUE"):
        stable_jet_id(
            values["record_id"],
            "root://example.invalid//a.root",
            values["run"],
            values["lumi"],
            values["event"],
            values["jet_index"],
        )


def test_event_overlap_is_rejected() -> None:
    assignments = [
        EventAssignment(19980, 1, 2, 3, Split.TRAIN),
        EventAssignment(19980, 1, 2, 3, Split.TEST),
    ]

    with pytest.raises(IntegrityError, match="SPLIT_EVENT_OVERLAP"):
        validate_event_disjointness(assignments)


def test_duplicate_pfn_assignment_is_rejected() -> None:
    with pytest.raises(IntegrityError, match="SPLIT_PFN_OVERLAP"):
        validate_pfn_assignments(
            [("root://example/a", Split.TRAIN), ("root://example/a", Split.TRAIN)]
        )
