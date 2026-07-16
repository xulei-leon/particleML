# FR-MODEL-002 Custom-Data Index

- `FR-ID`: `FR-MODEL-002`
- `Title`: Custom-data index
- `Phase`: Phase 4 - OmniLearned E0.5
- `Development Order`: 14
- `Priority`: P0
- `Prerequisites`: `FR-MODEL-001`, `FR-DATA-005`, `FR-REP-001`
- `Affected Packages`: `src/particleml/model_integration.py`, `src/particleml/cli.py`, `tests/test_model_integration.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-002

## Goal

Make OmniLearned's required custom-data indexing a validated, content-bound prerequisite rather than an implicit training side effect.

## Requirement Description

For every materialized A-D view, particleML shall run the pinned official `omnilearned dataloader` step, validate its outputs and row count, hash the complete index payload, and bind that hash to dependent runs.

## High-Level Requirements

- Record exact argv, dependency revision, source view hash, produced file list, row count, and index hash.
- Smoke-load the index through the official data path before publishing it.
- Invalidate an index whenever the source view hash changes.
- Require `COMPLETED.json` and matching hashes before training.

## Inputs

- Completed A-D view artifact and pinned OmniLearned executable.

## Outputs

- Validated index directory and completion record for each view.
- Stable index hash referenced by every dependent run record.

## Implementation Constraints

- Index construction runs in the isolated RunPod environment.
- The index is derived and disposable, while its identity and completion record remain auditable.

## Failure and Degradation

- Missing files, non-zero exit, row-count mismatch, stale view hash, or absent completion marker fails with `INDEX_*`.
- Training must not rebuild or accept an index implicitly.

## Acceptance Criteria

- All A-D indices pass the official smoke loader and expected row-count check.
- Changing a view hash makes the old index unusable.
- Every E0.5/E1+ run record contains the validated index hash.

## Minimum Verification

- `pytest -q tests/test_model_integration.py::test_index_required_and_hashed`
- Stale-view, missing-file, count-mismatch, failed-command, and completion-marker tests.
- RunPod E0.5 smoke evidence for all A-D views.

## Out of Scope

- Replacing the official index format with a project-specific loader.
- Treating index creation as optional.

## Notes

- Evidence target: E0.5 index completion records and validated index hashes.
