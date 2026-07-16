# FR-DATA-001 Frozen Source Manifest

- `FR-ID`: `FR-DATA-001`
- `Title`: Frozen source manifest
- `Phase`: Phase 1 - Deterministic Core and Contracts
- `Development Order`: 1
- `Priority`: P0
- `Prerequisites`: None
- `Affected Packages`: `src/particleml/manifest.py`, `src/particleml/cli.py`, `tests/test_manifest.py`, `configs/`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-001

## Goal

Establish an immutable, byte-reproducible identity for the CMS source corpus before extraction or downstream processing begins.

## Requirement Description

The system shall validate and consume a persistent source manifest containing the CMS record ID, exact canonical PFN, Adler-32 checksum, and byte size for every source file. The exact manifest bytes and their SHA-256 digest are the authoritative corpus identity.

## High-Level Requirements

- Accept UTF-8 without BOM, LF endings, no header, and exactly four tab-separated fields per row.
- Sort rows by numeric record ID and then by the exact UTF-8 PFN byte sequence.
- Reject duplicate PFNs, empty fields, invalid checksums, non-positive sizes, CRLF, and non-canonical order.
- Never trim, lowercase, URL-decode, or protocol-normalize a PFN.
- Expose `load_source_manifest`, `hash_source_manifest`, and `manifest validate --source PATH` through a thin CLI.

## Inputs

- A source-manifest TSV assembled from the approved CMS records.
- The expected manifest SHA-256 when a formal stage references a frozen corpus.

## Outputs

- A validated in-memory source manifest.
- The SHA-256 of the exact manifest bytes.
- Concise diagnostics and a non-zero stable exit code on failure.

## Implementation Constraints

- Use typed Python interfaces and `pathlib.Path`.
- Hash exact file bytes; do not reserialize before hashing.
- Credentials and temporary signed URLs must not enter the manifest.
- Formal validation evidence must come from GitHub Actions, not local execution.

## Failure and Degradation

- Fail closed with a `MANIFEST_*` error for malformed bytes, duplicate PFNs, ordering errors, or a hash mismatch.
- Do not continue with a warning or synthesize a replacement manifest.

## Acceptance Criteria

- Canonical fixture bytes yield the expected SHA-256 on Python 3.10 and 3.12 CI jobs.
- Every invalid condition above has a negative fixture and stable error family.
- Revalidation does not modify the manifest.
- The manifest hash is available to split, extraction, and provenance records.

## Minimum Verification

- `pytest -q tests/test_manifest.py::test_canonical_manifest_bytes_and_hash`
- Negative tests for BOM, CRLF, duplicates, ordering, checksum, size, and whitespace mutation.
- `ruff check`, `mypy src/particleml`, and `python scripts/validate_software_docs.py` in GitHub Actions.

## Out of Scope

- Discovering CMS files from an online catalog.
- Downloading or mirroring the CMS corpus to the local workstation.

## Notes

- Source contracts: `docs/software/requirements.md` FR-DATA-001 and `docs/software/specification.md` §2.1.
- Evidence target: E0 `manifests/source-manifest.tsv`.
