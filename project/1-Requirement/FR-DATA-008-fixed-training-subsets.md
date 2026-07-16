# FR-DATA-008 Fixed Training Subsets

- `FR-ID`: `FR-DATA-008`
- `Title`: Fixed training subsets
- `Phase`: Phase 2 - Synthetic Cloud Data Pipeline
- `Development Order`: 7
- `Priority`: P0
- `Prerequisites`: `FR-DATA-006`, `FR-DATA-009`, `FR-REP-001`
- `Affected Packages`: `src/particleml/manifest.py`, `src/particleml/views.py`, `tests/test_views.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-008

## Goal

Make labeled-data-efficiency comparisons use identical, nested, class-balanced training identities across A-D and all model conditions.

## Requirement Description

The system shall materialize deterministic subsets for `10^3`, `10^4`, and provisional `10^5` jets per class, or an amended E0 grid, using a dedicated subset seed independent of model seeds.

## High-Level Requirements

- Rank signal identities by `SHA256(str(seed) + "\0" + jet_id)` and then `jet_id`.
- Rank QCD per active record and select round-robin across sorted record IDs.
- Make every smaller subset a prefix of the next larger subset.
- Store realized identity lists and hashes in the split manifest.
- Reuse each subset unchanged across A-D, pretrained/fallback conditions, and model seeds.

## Inputs

- Frozen training identities, active QCD record mixture, requested scale grid, and explicit subset seed.

## Outputs

- Named nested subset identities and SHA-256 values in the split manifest.
- Deterministic selectors for view materialization.

## Implementation Constraints

- Never sample with replacement.
- The subset seed cannot default from a library and cannot equal model-seed semantics.

## Failure and Degradation

- Raise `INSUFFICIENT_CLASS_YIELD` when either class cannot satisfy a requested scale.
- Do not silently shrink, duplicate, or rebalance the requested subset.

## Acceptance Criteria

- Each subset is class-balanced and a strict prefix-compatible selection of the largest set.
- QCD selection follows deterministic record round-robin.
- Repeated builds produce identical identity lists and hashes.
- A-D and all model seeds consume the same subset identity hash.

## Minimum Verification

- `pytest -q tests/test_views.py::test_balanced_nested_subsets`
- Signal ranking, QCD round-robin, seed separation, insufficient-yield, and repeatability tests.

## Out of Scope

- Dynamic sampling during training.
- Changing the scale grid without an E0-backed research-plan amendment.

## Notes

- Supports RQ2 and the E2 data-efficiency analysis.
