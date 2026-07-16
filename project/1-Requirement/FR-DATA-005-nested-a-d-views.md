# FR-DATA-005 Nested A-D Views

- `FR-ID`: `FR-DATA-005`
- `Title`: Nested A-D views
- `Phase`: Phase 2 - Synthetic Cloud Data Pipeline
- `Development Order`: 9
- `Priority`: P0
- `Prerequisites`: `FR-DATA-004`, `FR-DATA-006`, `FR-DATA-007`, `FR-DATA-008`, `FR-REP-001`
- `Affected Packages`: `src/particleml/views.py`, `src/particleml/model_integration.py`, `tests/test_views.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline with Phase 0 contract correction
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-005

## Goal

Materialize identity-equivalent A-D feature views that differ only in approved particle-feature availability and conform to OmniLearned's native integer-PID interface.

## Requirement Description

All A-D views shall project the same canonical jets, order, masks, labels, splits, and subset identities. PID is an integer absolute-PDG-ID species category, not a materialized one-hot block, so charge information is not duplicated.

## High-Level Requirements

- Configuration A contains four kinematic fields.
- Configuration B contains A plus charge and uses `--use-add --num-add 1`.
- Configuration C contains A plus integer PID at index 4 and charge, using `--use-pid --pid_idx 4 --use-add --num-add 1`.
- Configuration D contains A plus integer PID, charge, and four D fields, using `--use-pid --pid_idx 4 --use-add --num-add 5`.
- Do not materialize one-hot PID columns in OmniLearned HDF5 views.
- Validate byte-for-byte equality of ordered jet IDs, labels, masks, split hashes, and subset hashes across A-D.

## Inputs

- Canonical full-D dataset, split manifest, fitted preprocessing state, feature configuration, and subset ID.
- E0.5-approved D-field transform and missing-track policy.

## Outputs

- Immutable HDF5 views for A-D with ordered field metadata and hashes.
- View completion records consumable by OmniLearned index building and the in-repository baseline.

## Implementation Constraints

- The development plan's native integer-PID correction supersedes the one-hot view tables currently present in architecture/specification version 1.0.0; Phase 0 must synchronize those documents before implementation.
- PID sign removal occurs before view construction; mask remains the sole validity indicator.
- Fixed full-dimensional neutralization is allowed only when E0.5 explicitly approves and records that fallback.

## Failure and Degradation

- Any identity, order, label, mask, split, subset, field-order, or hash mismatch fails with `VIEW_*`.
- Missing approved preprocessing or D-field policy blocks the affected view; do not invent defaults.

## Acceptance Criteria

- A-D ordered jet IDs, labels, masks, split hashes, and subset hashes are identical in cloud fixture tests.
- C and D contain one integer PID field and no one-hot PID columns.
- The generated OmniLearned argv uses the exact PID/additional-feature flags for each configuration.
- Positive and negative species share the same PID category while charge remains a distinct feature.

## Minimum Verification

- `pytest -q tests/test_views.py::test_ad_identity_equivalence`
- PID sign, ordered-field, dimensions, command-flag, stale-hash, and neutralization-policy tests.
- Documentation consistency check after correcting architecture, specification, and traceability.

## Out of Scope

- Per-configuration jet resampling or normalization fitting.
- One-hot PID materialization in OmniLearned HDF5 views.

## Notes

- This FR records the explicit Phase 0 correction in `particleml-development-plan.md`.
