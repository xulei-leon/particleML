# FR-REP-003 Evidence Status Propagation

- `FR-ID`: `FR-REP-003`
- `Title`: Evidence status propagation
- `Phase`: Phase 7 - E3 and Reporting
- `Development Order`: 26
- `Priority`: P1
- `Prerequisites`: `FR-REP-001`, `FR-REP-002`, `FR-TRAIN-004`
- `Affected Packages`: `src/particleml/reporting.py`, `docs/software/traceability-matrix.md`, `tests/test_reporting.py`
- `Prototype Phase`: No
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-REP-003

## Goal

Keep requirement, implementation, experiment, artifact, figure, and manuscript-claim status honest and monotonically constrained by evidence.

## Requirement Description

All traceable items shall use `specified`, `implemented`, `verified`, or `deferred`. A downstream item shall never have a stronger status than an unmet upstream requirement, test, gate, or artifact.

## High-Level Requirements

- Preserve stable requirement IDs and one traceability row per active requirement.
- Distinguish planned mappings from repository implementation and retained verification.
- Propagate failures, deferrals, and fallback claim narrowing to dependent figures/tables/claims.
- Require identified code/document evidence for `implemented` and passing cloud/gate evidence for `verified`.
- Update documentation and traceability with any interface, schema, dataset, endpoint, or claim-boundary change.

## Inputs

- Requirement mappings, implementation evidence, CI results, gate records, artifact completion/hashes, and claim dependencies.

## Outputs

- Updated traceability matrix, experiment status, and claim-eligibility ledger.

## Implementation Constraints

- Local execution never upgrades a formal status.
- A planned configuration or artifact path is not evidence of completion.

## Failure and Degradation

- Inconsistent or stronger-than-upstream status blocks release/report claim readiness.
- Deferred required controls narrow claims and remain visible.

## Acceptance Criteria

- Status monotonicity tests reject invalid upstream/downstream combinations.
- Every active FR appears exactly once in the software traceability matrix.
- Implemented and verified states cite concrete evidence identities.
- Fallback and failed-run states propagate to report eligibility.

## Minimum Verification

- `pytest -q tests/test_reporting.py` status and claim-ledger tests.
- `python scripts/validate_software_docs.py` for unique IDs and traceability coverage.

## Out of Scope

- Manual promotion of status without retained evidence.
- Reusing deleted requirement identifiers.

## Notes

- This FR operationalizes publication-integrity NFR-PUB-001.
