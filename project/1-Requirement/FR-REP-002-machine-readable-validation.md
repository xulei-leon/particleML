# FR-REP-002 Machine-Readable Validation

- `FR-ID`: `FR-REP-002`
- `Title`: Machine-readable validation
- `Phase`: Phase 1 - Deterministic Core and Contracts
- `Development Order`: 4
- `Priority`: P0
- `Prerequisites`: None
- `Affected Packages`: `src/particleml/contracts.py`, `schemas/`, `scripts/validate_software_docs.py`, contract tests
- `Prototype Phase`: Yes
- `Source Type`: SRS baseline
- `Original SRS Section`: Software Requirements Specification §4, FR-REP-002

## Goal

Provide strict, versioned machine validation for artifacts that cross component and environment boundaries.

## Requirement Description

Run records, split manifests, and prediction metadata shall validate against JSON Schema Draft 2020-12 version 1.0.0 before downstream consumption. Semantic validators shall enforce cross-artifact constraints not expressible in JSON Schema.

## High-Level Requirements

- Maintain the three schemas under `schemas/` with exact major-version handling.
- Reject unknown properties at all defined object boundaries.
- Support valid successful and failed run-record variants.
- Validate content hashes, split disjointness, identity order, and external payload relationships semantically.
- Expose `contracts validate --path PATH` and keep documentation/schema/traceability synchronized.

## Inputs

- Serialized run record, split manifest, or prediction metadata and referenced artifacts when available.

## Outputs

- Typed validated representation or stable `CONTRACT_*`/integrity error diagnostics.

## Implementation Constraints

- A prose/schema conflict is a release blocker and must be corrected in one change.
- Readers reject unsupported major versions rather than coercing them.

## Failure and Degradation

- Schema violation, unknown property, unsupported version, missing reference, or semantic mismatch fails closed.
- Invalid artifacts are not consumed with warnings.

## Acceptance Criteria

- Representative valid/invalid fixtures cover every schema branch.
- Unknown properties and unsupported versions are rejected.
- Semantic overlap/order/hash failures are detected.
- `python scripts/validate_software_docs.py` confirms SRS/spec/schema/traceability consistency.

## Minimum Verification

- Contract fixture suite plus `python scripts/validate_software_docs.py`.
- GitHub Actions: Python 3.10/3.12 `pytest`, `ruff check`, `mypy src/particleml`, `pnpm test`, and `pnpm docs:build` as applicable.

## Out of Scope

- Silently migrating incompatible artifact versions.
- Treating schema validation alone as proof of scientific correctness.

## Notes

- Schema major version remains 1.0.0 until an approved incompatible migration.
