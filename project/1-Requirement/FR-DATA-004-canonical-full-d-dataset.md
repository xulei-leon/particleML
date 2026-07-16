# FR-DATA-004 Canonical Full-D Dataset

- `FR-ID`: `FR-DATA-004`
- `Title`: Canonical full-D dataset
- `Phase`: Phase 2 - Synthetic Cloud Data Pipeline
- `Development Order`: 5
- `Priority`: P0
- `Prerequisites`: `FR-DATA-001`, `FR-DATA-006`, `FR-REP-001`, `FR-REP-002`
- `Affected Packages`: `src/particleml/dataset.py`, `src/particleml/cli.py`, `tests/test_dataset.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-004

## Goal

Create one immutable, auditable full-D dataset from which every feature condition is derived without changing jet membership or order.

## Requirement Description

Compact ROOT inputs shall be converted into a content-addressed HDF5 dataset with at most 150 pT-ordered constituents, explicit masks, binary labels, stable identities, audit fields, and complete provenance.

## High-Level Requirements

- Apply approved positive pT/energy cuts, wrapped delta-phi, logarithmic kinematics, absolute-PDG-ID PID coding, track-state coding, stable pT sorting, and truncation.
- Store zero padding with `mask=false`; never infer validity from zero values.
- Validate finiteness, units, mask-prefix shape, unique identities, split consistency, allowed labels/PID codes, and absence of truth fields in model arrays.
- Use gzip level 4 and jet-major chunks for the canonical HDF5 layout.
- Publish only after semantic validation and hashing.

## Inputs

- Compact ROOT files and their extraction metadata.
- Frozen source/split identity and a versioned preprocessing policy.
- Required positive particle pT and energy thresholds.

## Outputs

- `<artifact-root>/<study-id>/canonical/canonical-full-d.h5`.
- Dataset hash, completion record, conversion provenance, and structured audit data.

## Implementation Constraints

- Canonical logic belongs in package modules; notebooks are read-only API consumers.
- The dataset remains full-D even when downstream views expose fewer fields.
- Scientific policy values have no implicit environment or library defaults.

## Failure and Degradation

- Reject missing policy fields, non-finite valid entries, invalid units/codes, identity collisions, mask errors, or source/split mismatches with `DATA_*` or `SPLIT_*` errors.
- Never publish a partial HDF5 file as complete.

## Acceptance Criteria

- A deterministic cloud-generated compact ROOT fixture produces the specified HDF5 paths, shapes, dtypes, attributes, masks, and identities.
- Positive and negative PDG IDs map to the same species code.
- Sorting uses original daughter index as the pT tie-breaker and truncates at 150.
- Repeated CI conversion of identical inputs yields identical semantic content and recorded hashes.

## Minimum Verification

- `pytest -q tests/test_dataset.py::test_canonical_layout`
- Unit tests for phi wrapping, PID sign removal, track states, padding, sorting, truncation, and invalid inputs.
- Fixture integration in GitHub Actions; local output is not formal evidence.

## Out of Scope

- A separate canonical dataset per feature configuration.
- JetClass as a production dataset.

## Notes

- Source contracts: architecture §5.2 and specification §3.2-3.3.
