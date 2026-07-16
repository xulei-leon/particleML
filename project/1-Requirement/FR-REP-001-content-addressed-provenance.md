# FR-REP-001 Content-Addressed Provenance

- `FR-ID`: `FR-REP-001`
- `Title`: Content-addressed provenance
- `Phase`: Phase 1 - Deterministic Core and Contracts
- `Development Order`: 3
- `Priority`: P0
- `Prerequisites`: `FR-REP-002`
- `Affected Packages`: `src/particleml/contracts.py`, artifact writers, `tests/test_artifacts.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-REP-001

## Goal

Make every formal dataset, model, prediction, and report traceable to immutable inputs and reject stale or partial output.

## Requirement Description

All formal artifacts shall carry versioned SHA-256 metadata and use the lifecycle `prepare -> temporary write -> validate -> hash -> publish -> COMPLETED.json`. Consumers shall verify completion and hashes before reuse.

## High-Level Requirements

- Cover manifests, canonical data, views, preprocessing, indices, checkpoints, predictions, run records, tables, and figures.
- Version hash algorithms and canonicalization rules.
- Publish within one filesystem; POSIX may use atomic rename while `COMPLETED.json` remains the authoritative explicit record.
- Resume only when all requested input/configuration hashes match.
- Keep formal artifacts on persistent cloud storage outside Git and temporary GPU disks.

## Inputs

- Temporary artifact payload, resolved input/config hashes, schema/semantic validator, and artifact root.

## Outputs

- Published immutable artifact, lowercase SHA-256, metadata, and completion record.

## Implementation Constraints

- `PARTICLEML_ARTIFACT_ROOT` is the only supported environment-supplied path setting.
- Artifact paths are data, not shell fragments.

## Failure and Degradation

- Missing marker, stale hash, validation error, partial publication, or unsupported hash/schema version rejects the artifact and dependents.
- Formal output is never overwritten.

## Acceptance Criteria

- Partial outputs are never accepted as complete.
- Byte/content changes are detected and invalidate resume.
- Completion records bind inputs, configuration, payloads, and writer version.
- Cloud storage remains authoritative; local copies cannot become formal sources.

## Minimum Verification

- Content-hash, temporary-write, completion-sentinel, stale-resume, mismatch, and no-overwrite tests.
- `pytest -q tests/test_artifacts.py` in GitHub Actions.

## Out of Scope

- Treating temporary GPU disks or local workstation files as authoritative storage.
- Mutable in-place formal artifacts.

## Notes

- Supports NFR-ROB-001 and every downstream evidence contract.
