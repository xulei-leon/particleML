# FR-MODEL-005 Pretraining Fallback

- `FR-ID`: `FR-MODEL-005`
- `Title`: Pretraining fallback
- `Phase`: Phase 4 - OmniLearned E0.5
- `Development Order`: 17
- `Priority`: P0
- `Prerequisites`: `FR-MODEL-003`, `FR-MODEL-004`, `FR-REP-003`
- `Affected Packages`: `src/particleml/model_integration.py`, `src/particleml/reporting.py`, `configs/`, `tests/test_reporting.py`
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-MODEL-005

## Goal

Preserve a scientifically honest execution path when pretrained input compatibility cannot be established.

## Requirement Description

If E0.5 cannot validate native adapter compatibility, the system shall use only an explicitly approved full-dimensional neutralization policy or switch to a supervised OmniLearned-architecture ablation. The supervised fallback automatically removes pretrained-transfer claims.

## High-Level Requirements

- Record the failed compatibility evidence and chosen allowed policy.
- Apply one fixed neutralization policy consistently across relevant conditions when approved.
- Represent supervised initialization as a distinct model condition.
- Propagate the fallback decision to run-matrix and claim-eligibility artifacts.
- Never present fallback results as pretrained transfer.

## Inputs

- Failed E0.5 checkpoint/adapter audit and an explicit approved fallback decision.

## Outputs

- Versioned fallback configuration, revised condition matrix, and narrowed claim ledger.

## Implementation Constraints

- There is no silent default and no post-hoc policy selection using test performance.
- The fallback must retain the same data, splits, subsets, evaluation, and artifact contracts.

## Failure and Degradation

- Without an approved policy, stop at E0.5.
- If reporting still marks pretrained-transfer claims eligible, fail the report build.

## Acceptance Criteria

- Fallback activation is explicit, hashed, and visible in every dependent run.
- Supervised fallback outputs are never labeled pretrained.
- Claim eligibility removes or narrows all affected manuscript statements.
- The unchanged data/evaluation protocol remains traceable.

## Minimum Verification

- `pytest -q tests/test_reporting.py::test_fallback_narrows_claims`
- Policy-required, matrix-rewrite, run-condition, and ineligible-claim tests.

## Out of Scope

- Arbitrary adapter redesign after examining E2 results.
- Concealing an incompatible checkpoint behind neutral zero-filled fields.

## Notes

- This is a controlled degradation of claim scope, not an automatic recovery.
