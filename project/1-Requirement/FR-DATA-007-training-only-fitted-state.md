# FR-DATA-007 Training-Only Fitted State

- `FR-ID`: `FR-DATA-007`
- `Title`: Training-only fitted state
- `Phase`: Phase 2 - Synthetic Cloud Data Pipeline
- `Development Order`: 6
- `Priority`: P0
- `Prerequisites`: `FR-DATA-004`, `FR-DATA-006`, `FR-REP-001`
- `Affected Packages`: `src/particleml/dataset.py`, `configs/`, `tests/test_dataset.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-DATA-007

## Goal

Prevent validation/test leakage and undocumented preprocessing by freezing all learned or selected transform state from training data only.

## Requirement Description

Normalization, pT/eta control, optional pileup reweighting, PID vocabulary, and any approved D-field transform shall be fitted or frozen using only the complete training partition, hashed, and reused unchanged by every scale, feature configuration, model, validation set, and test set.

## High-Level Requirements

- Serialize immutable `preprocessing.json` with policy, training identities, parameters, sources, and canonical JSON hash.
- Require explicit positive particle cuts, PID vocabulary, control policies, D-field unit/transform, and missing-track policy.
- Allow a documented checkpoint-native transform only for fields it explicitly names.
- Reject unknown keys and unresolved scientific policy values.

## Inputs

- Canonical dataset and frozen training split.
- Versioned preprocessing policy and any E0/E0.5-approved decisions.

## Outputs

- Content-hashed preprocessing state referenced by views and run records.
- Audit evidence identifying the exact training identities used to fit state.

## Implementation Constraints

- Scientific settings cannot come from ambient environment variables or implicit library defaults.
- Fit once on the full frozen training partition, not separately per training scale.

## Failure and Degradation

- Block view or run creation for unresolved transforms, non-training fit identities, stale hashes, or unsupported policy fields.
- Do not fall back to ad hoc clipping or `tanh` transforms.

## Acceptance Criteria

- Fit-identity audit contains only training jets.
- Validation/test values do not influence fitted parameters.
- All A-D views and model conditions reference one identical preprocessing hash.
- Hash changes invalidate dependent views, indices, and resume attempts.

## Minimum Verification

- `pytest -q tests/test_dataset.py::test_fit_uses_train_only`
- Leakage, canonical-JSON hashing, missing-policy, stale-state, and multi-scale reuse tests.

## Out of Scope

- Per-model or per-scale normalization fitting.
- Automatic scientific-policy selection outside E0/E0.5 gates.

## Notes

- Evidence target: E0/E0.5 preprocessing policy artifact.
